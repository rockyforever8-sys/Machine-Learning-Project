from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ppap_inbox_triage.classifier import classify_file
from ppap_inbox_triage.models import InboxFile, MatchConfidence
from ppap_inbox_triage.pdf_text import extract_pdf_text, pdf_text_available
from ppap_inbox_triage.report import report_to_dict, write_all_reports
from ppap_inbox_triage.scanner import scan_inbox
from ppap_inbox_triage.triage import triage_inbox
from ppap_inbox_triage.watcher import snapshot_inbox, watch_inbox

from pdf_fixture import write_multipage_text_pdf, write_text_pdf


FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "sample_inbox"


class ClassifierTests(unittest.TestCase):
    def test_classifies_psw(self) -> None:
        file = InboxFile(
            path=Path("18_PSW_Signed.pdf"),
            relative_path="18_PSW_Signed.pdf",
            name="18_PSW_Signed.pdf",
            suffix=".pdf",
            size_bytes=1,
        )
        matches = classify_file(file)
        self.assertTrue(matches)
        self.assertEqual(matches[0].element.number, 18)
        self.assertEqual(matches[0].confidence, MatchConfidence.HIGH)

    def test_prefix_disambiguates_fixture_drawing(self) -> None:
        file = InboxFile(
            path=Path("16_Checking_Fixture_Drawing.pdf"),
            relative_path="16_Checking_Fixture_Drawing.pdf",
            name="16_Checking_Fixture_Drawing.pdf",
            suffix=".pdf",
            size_bytes=1,
        )
        matches = classify_file(file)
        self.assertEqual(matches[0].element.number, 16)

        file = InboxFile(
            path=Path("06_PFMEA_Line-2.xlsx"),
            relative_path="06_PFMEA_Line-2.xlsx",
            name="06_PFMEA_Line-2.xlsx",
            suffix=".xlsx",
            size_bytes=1,
        )
        matches = classify_file(file)
        self.assertEqual(matches[0].element.number, 6)

    def test_content_classification_from_pdf_text(self) -> None:
        file = InboxFile(
            path=Path("supplier_doc.pdf"),
            relative_path="supplier_doc.pdf",
            name="supplier_doc.pdf",
            suffix=".pdf",
            size_bytes=1,
        )
        matches = classify_file(
            file,
            text_content="Customer Engineering Approval signed by OEM quality.",
        )
        self.assertEqual(matches[0].element.number, 3)
        self.assertTrue(matches[0].matched_pattern.startswith("content:"))


@unittest.skipUnless(pdf_text_available(), "pypdf is required for PDF extraction tests")
class PdfTextTests(unittest.TestCase):
    def test_extract_pdf_text(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            pdf_path = Path(temp_dir) / "approval.pdf"
            write_text_pdf(pdf_path, "Customer Engineering Approval")
            text = extract_pdf_text(pdf_path)
            self.assertIsNotNone(text)
            assert text is not None
            self.assertIn("Customer Engineering Approval", text)

    def test_pdf_text_classifies_ambiguous_filename(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            inbox = Path(temp_dir)
            pdf_path = inbox / "supplier_submission_rev_a.pdf"
            write_text_pdf(pdf_path, "Customer Engineering Approval and sign-off")
            report = triage_inbox(inbox, use_pdf_text=True)
            self.assertEqual(report.summary["submission_layout"], "discrete")
            self.assertNotIn(3, report.summary["missing_element_numbers"])
            element_three = next(item for item in report.elements if item.element.number == 3)
            self.assertEqual(element_three.status, "present")

    def test_binder_detects_multiple_elements_from_one_pdf(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            inbox = Path(temp_dir)
            pdf_path = inbox / "PPAP Level 3_1616-5YY3235_RKG-25V392MK9WZQ-FC6_26-02-2021.pdf"
            write_multipage_text_pdf(
                pdf_path,
                [
                    "Design Records drawing number 1616 title block engineering drawing revision A",
                    "Process FMEA PFMEA process function current process control failure mode RPN severity occurrence detection",
                    "Control Plan production control plan reaction plan sample frequency control method",
                    "Part Submission Warrant PSW submission level supplier authorized signature declaration",
                    "Dimensional Results layout inspection FAI balloon no CMM report measured value",
                ],
            )
            report = triage_inbox(inbox, use_pdf_text=True)
            self.assertEqual(report.summary["submission_layout"], "binder")
            self.assertIn(1, [item.element.number for item in report.elements if item.status == "present"])
            self.assertIn(6, [item.element.number for item in report.elements if item.status == "present"])
            self.assertIn(7, [item.element.number for item in report.elements if item.status == "present"])
            self.assertIn(18, [item.element.number for item in report.elements if item.status == "present"])
            self.assertGreaterEqual(report.summary["elements_present"], 5)
            self.assertNotIn(6, report.summary["missing_critical_numbers"])
            self.assertNotIn(7, report.summary["missing_critical_numbers"])
            self.assertNotIn(18, report.summary["missing_critical_numbers"])

            element_six = next(item for item in report.elements if item.element.number == 6)
            self.assertTrue(any(match.page_number is not None for match in element_six.matches))

            with tempfile.TemporaryDirectory() as output_dir:
                outputs = write_all_reports(report, Path(output_dir))
                self.assertTrue(outputs["sqe_checklist"].exists())
                checklist = outputs["sqe_checklist"].read_text(encoding="utf-8")
                self.assertIn("Binder page index", checklist)
                self.assertIn("Element verification", checklist)
                markdown = outputs["markdown"].read_text(encoding="utf-8")
                self.assertIn("Binder Page Index", markdown)
                self.assertIn("| Pages |", markdown)


class ScannerTests(unittest.TestCase):
    def test_scan_fixture_inbox(self) -> None:
        files = scan_inbox(FIXTURES)
        names = {file.name for file in files}
        self.assertIn("18_PSW_Signed.pdf", names)
        self.assertIn("random_supplier_cover_letter.pdf", names)


class WatcherTests(unittest.TestCase):
    def test_snapshot_tracks_file_count(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            inbox = Path(temp_dir)
            snapshot = snapshot_inbox(inbox)
            self.assertEqual(snapshot.file_count, 0)

            (inbox / "psw.pdf").write_text("x", encoding="utf-8")
            snapshot = snapshot_inbox(inbox)
            self.assertEqual(snapshot.file_count, 1)

    def test_watch_once_writes_reports(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            inbox = Path(temp_dir) / "inbox"
            output = Path(temp_dir) / "out"
            inbox.mkdir()
            (inbox / "18_PSW_Signed.pdf").write_text("x", encoding="utf-8")

            with patch("ppap_inbox_triage.watcher.time.sleep", return_value=None):
                watch_inbox(inbox, output, run_once=True)

            self.assertTrue((output / "triage-report.json").exists())


class TriageTests(unittest.TestCase):
    def test_sample_inbox_triage(self) -> None:
        report = triage_inbox(FIXTURES)
        self.assertEqual(report.submission_level, 3)
        self.assertEqual(report.summary["submission_layout"], "discrete")
        self.assertGreater(report.summary["files_scanned"], 10)
        self.assertGreater(report.summary["elements_present"], 10)
        self.assertIn(3, report.summary["missing_element_numbers"])
        self.assertIn(14, report.summary["missing_element_numbers"])
        self.assertIn(15, report.summary["missing_element_numbers"])
        self.assertTrue(report.orphans)

    def test_blocked_when_critical_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            inbox = Path(temp_dir)
            (inbox / "01_Drawing.pdf").write_text("drawing", encoding="utf-8")
            report = triage_inbox(inbox)
            self.assertEqual(report.status.value, "blocked")
            self.assertIn(6, report.summary["missing_critical_numbers"])
            self.assertIn(7, report.summary["missing_critical_numbers"])
            self.assertIn(18, report.summary["missing_critical_numbers"])

    def test_ready_when_complete(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            inbox = Path(temp_dir)
            filenames = [
                "drawing.pdf",
                "ecn.pdf",
                "customer_approval.pdf",
                "dfmea.xlsx",
                "process_flow.pdf",
                "pfmea.xlsx",
                "control_plan.xlsx",
                "gage_rr.pdf",
                "dimensional_fai.pdf",
                "material_test.pdf",
                "cpk_study.xlsx",
                "lab_accreditation.pdf",
                "aar.pdf",
                "sample_parts_list.pdf",
                "master_sample.pdf",
                "checking_fixture.pdf",
                "csr_checklist.pdf",
                "psw_signed.pdf",
            ]
            for name in filenames:
                (inbox / name).write_text("x", encoding="utf-8")

            report = triage_inbox(inbox)
            self.assertEqual(report.status.value, "ready_for_review")
            self.assertEqual(report.summary["elements_missing"], 0)
            self.assertEqual(report.summary["orphan_files"], 0)

    def test_report_outputs(self) -> None:
        report = triage_inbox(FIXTURES)
        with tempfile.TemporaryDirectory() as temp_dir:
            outputs = write_all_reports(report, Path(temp_dir))
            self.assertTrue(outputs["json"].exists())
            self.assertTrue(outputs["csv"].exists())
            self.assertTrue(outputs["markdown"].exists())
            self.assertTrue(outputs["sqe_checklist"].exists())

        payload = report_to_dict(report)
        self.assertEqual(len(payload["elements"]), 18)
        self.assertIn("actions", payload)


if __name__ == "__main__":
    unittest.main()
