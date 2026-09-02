from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ppap_inbox_triage.classifier import classify_file
from ppap_inbox_triage.layout import is_binder_filename
from ppap_inbox_triage.models import InboxFile, MatchConfidence
from ppap_inbox_triage.pdf_text import extract_pdf_text, pdf_text_available
from ppap_inbox_triage.report import report_to_dict, write_all_reports, write_package_reports
from ppap_inbox_triage.scanner import discover_submission_packages, scan_inbox
from ppap_inbox_triage.triage import triage_inbox, triage_packages
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

    def test_classifies_chinese_filenames(self) -> None:
        pfmea = InboxFile(
            path=Path("06_过程FMEA_焊接.pdf"),
            relative_path="06_过程FMEA_焊接.pdf",
            name="06_过程FMEA_焊接.pdf",
            suffix=".pdf",
            size_bytes=1,
        )
        matches = classify_file(pfmea)
        self.assertTrue(matches)
        self.assertEqual(matches[0].element.number, 6)

        psw = InboxFile(
            path=Path("零件提交保证书.pdf"),
            relative_path="零件提交保证书.pdf",
            name="零件提交保证书.pdf",
            suffix=".pdf",
            size_bytes=1,
        )
        psw_matches = classify_file(psw)
        self.assertEqual(psw_matches[0].element.number, 18)

        plan = InboxFile(
            path=Path("07_控制计划.xlsx"),
            relative_path="07_控制计划.xlsx",
            name="07_控制计划.xlsx",
            suffix=".xlsx",
            size_bytes=1,
        )
        plan_matches = classify_file(plan)
        self.assertEqual(plan_matches[0].element.number, 7)

    def test_chinese_content_not_confused_with_dfmea(self) -> None:
        file = InboxFile(
            path=Path("supplier.pdf"),
            relative_path="supplier.pdf",
            name="supplier.pdf",
            suffix=".pdf",
            size_bytes=1,
        )
        matches = classify_file(
            file,
            text_content="过程FMEA 过程功能 当前过程控制 失效模式 严重度 频度 探测度",
        )
        self.assertEqual(matches[0].element.number, 6)
        self.assertFalse(any(match.element.number == 4 for match in matches if match.score >= 0.8))

    def test_chinese_binder_filenames(self) -> None:
        self.assertTrue(is_binder_filename("PPAP第3级提交.pdf"))
        self.assertTrue(is_binder_filename("供应商PPAP卷宗.pdf"))
        self.assertTrue(is_binder_filename("全套PPAP资料.pdf"))
        self.assertTrue(is_binder_filename("PPAP Level 3_binder.pdf"))
        self.assertTrue(is_binder_filename("PPAP_1431-8YY0024(A) from zhiye.pdf"))
        self.assertTrue(is_binder_filename("PPAP_1431-8YY0024(A)\u00a0from\u00a0zhiye.pdf"))
        self.assertFalse(is_binder_filename("PSW_1431-8YY0024A_Approved.pdf"))

    def test_psw_checklist_does_not_count_as_design_records(self) -> None:
        file = InboxFile(
            path=Path("0044-G22C615XX0025 PSW..pdf"),
            relative_path="0044-G22C615XX0025 D002 606146/0044-G22C615XX0025 PSW..pdf",
            name="0044-G22C615XX0025 PSW..pdf",
            suffix=".pdf",
            size_bytes=1,
        )
        psw_text = """
Part Submission Warrant
Part Name: Bracket  Part Number: 0044-G22C615XX0025
Engineering drawing change level: A
Shown on drawing number: 0044-G22C615XX0025
Purchase order no: PO-9921
Submission level: Level 3
Declaration: I hereby warrant the samples represented by this warrant
Supplier authorized signature: J. Supplier
The following documents are attached:
1. Design Records
2. Engineering Change Documents
4. Design FMEA
6. Process FMEA
7. Control Plan
18. Part Submission Warrant
"""
        matches = classify_file(file, text_content=psw_text)
        self.assertTrue(matches)
        self.assertEqual(matches[0].element.number, 18)
        self.assertFalse(any(match.element.number == 1 for match in matches))


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

    def test_psw_file_is_not_a_design_record_duplicate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            inbox = Path(temp_dir)
            write_text_pdf(
                inbox / "0044-G22C615XX0025 PSW..pdf",
                """
Part Submission Warrant
Engineering drawing change level: A
Shown on drawing number: 0044-G22C615XX0025
Submission level: Level 3
Declaration: I hereby warrant the samples
Supplier authorized signature: J. Supplier
1. Design Records
2. Engineering Change Documents
6. Process FMEA
7. Control Plan
18. Part Submission Warrant
""",
            )
            write_text_pdf(
                inbox / "01_Drawing.pdf",
                "Design Records drawing number 0044-G22C615XX0025 title block revision A engineering drawing scale 1:1",
            )
            report = triage_inbox(inbox, use_pdf_text=True, layout_mode="discrete")
            design = next(item for item in report.elements if item.element.number == 1)
            psw = next(item for item in report.elements if item.element.number == 18)
            self.assertEqual(design.status, "present")
            self.assertEqual(psw.status, "present")
            self.assertTrue(any("PSW" in match.file.name for match in psw.matches))
            self.assertFalse(any("PSW" in match.file.name for match in design.matches))
            self.assertTrue(any("Drawing" in match.file.name for match in design.matches))

    def test_ppap_named_package_pdf_is_scanned_as_binder(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            inbox = Path(temp_dir) / "1431-8YY0024 D008 611818"
            inbox.mkdir()
            write_multipage_text_pdf(
                inbox / "PPAP_1431-8YY0024(A) from zhiye.pdf",
                [
                    "Cover PPAP Level 3 1431-8YY0024",
                    "TABLE OF CONTENTS\n1. Design Records\n6. Process FMEA\n7. Control Plan\n18. Part Submission Warrant",
                    "1. Design Records  Drawing number 1431-8YY0024 title block revision A engineering drawing scale 1:1",
                    "6. Process FMEA  PFMEA process function current process control potential failure mode severity occurrence detection RPN",
                    "7. Control Plan  production control plan reaction plan sample size sample frequency control method special characteristic",
                    "18. Part Submission Warrant PSW submission level supplier authorized signature declaration",
                ],
            )
            write_text_pdf(
                inbox / "PSW_1431-8YY0024A_Approved.pdf",
                "Part Submission Warrant PSW submission level supplier authorized signature declaration",
            )
            (inbox / "1431-8YY0024 A.xlsx").write_text("x", encoding="utf-8")

            report = triage_inbox(inbox, use_pdf_text=True, layout_mode="auto")
            self.assertEqual(report.summary["submission_layout"], "mixed")
            binder_files = report.summary.get("binder_files", [])
            discrete_files = report.summary.get("discrete_files", [])
            self.assertTrue(any("PPAP_1431" in name for name in binder_files))
            self.assertFalse(any("PSW_" in name for name in binder_files))
            self.assertTrue(any("PSW_" in name for name in discrete_files))
            self.assertTrue(any(name.endswith(".xlsx") for name in discrete_files))
            present = {
                item.element.number for item in report.elements if item.status == "present"
            }
            self.assertIn(1, present)
            self.assertIn(6, present)
            self.assertIn(7, present)
            self.assertIn(18, present)
            self.assertGreater(report.summary["completeness_pct"], 0)

    def test_auto_detects_tiny_ppap_named_pdf_next_to_psw(self) -> None:
        """Cover-only PPAP_*.pdf must still be a binder; first pages have no element text."""
        with tempfile.TemporaryDirectory() as temp_dir:
            inbox = Path(temp_dir) / "1431-8YY0024 D008 611818"
            inbox.mkdir()
            write_multipage_text_pdf(
                inbox / "PPAP_1431-8YY0024(A) from zhiye.pdf",
                ["Cover page", "Supplier letter from zhiye", "Revision history"],
            )
            write_text_pdf(
                inbox / "PSW_1431-8YY0024A_Approved.pdf",
                "Part Submission Warrant PSW submission level supplier authorized signature declaration",
            )
            (inbox / "1431-8YY0024 A.xlsx").write_text("x", encoding="utf-8")

            report = triage_inbox(inbox, use_pdf_text=True, layout_mode="auto")
            self.assertEqual(report.summary["submission_layout"], "mixed")
            binder_files = report.summary.get("binder_files", [])
            self.assertEqual(len(binder_files), 1)
            self.assertIn("PPAP_1431", binder_files[0])
            self.assertFalse(any("PSW_" in name for name in binder_files))
            psw = next(item for item in report.elements if item.element.number == 18)
            self.assertEqual(psw.status, "present")
            self.assertTrue(any("PSW_" in match.file.name for match in psw.matches))

    def test_auto_detects_unnamed_companion_pdf_next_to_psw(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            inbox = Path(temp_dir)
            write_multipage_text_pdf(
                inbox / "1431-8YY0024(A) from zhiye.pdf",
                [
                    "Cover",
                    "1. Design Records  Drawing number 1431-8YY0024 title block revision A engineering drawing scale 1:1",
                    "6. Process FMEA  PFMEA process function current process control potential failure mode severity occurrence detection RPN",
                    "7. Control Plan  production control plan reaction plan sample size sample frequency control method special characteristic",
                ],
            )
            write_text_pdf(
                inbox / "PSW_1431-8YY0024A_Approved.pdf",
                "Part Submission Warrant PSW submission level supplier authorized signature declaration",
            )

            report = triage_inbox(inbox, use_pdf_text=True, layout_mode="auto")
            self.assertEqual(report.summary["submission_layout"], "mixed")
            binder_files = report.summary.get("binder_files", [])
            self.assertTrue(any("from zhiye" in name for name in binder_files))
            self.assertFalse(any(name.startswith("PSW_") or "/PSW_" in name for name in binder_files))
            present = {
                item.element.number for item in report.elements if item.status == "present"
            }
            self.assertIn(1, present)
            self.assertIn(6, present)
            self.assertIn(7, present)
            self.assertIn(18, present)


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


class PackageDiscoveryTests(unittest.TestCase):
    def test_flat_inbox_is_one_package(self) -> None:
        packages = discover_submission_packages(FIXTURES)
        self.assertEqual(len(packages), 1)
        self.assertEqual(packages[0].kind, "inbox")

    def test_two_folders_are_independent_reviews(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            inbox = Path(temp_dir)
            folder_a = inbox / "0044-G22C615XX0025 D002 606146"
            folder_b = inbox / "1104-1060261A(QWP086A)PPAP24.03.25-Update"
            folder_a.mkdir()
            folder_b.mkdir()
            (folder_a / "01_Drawing.pdf").write_text("drawing", encoding="utf-8")
            (folder_a / "18_PSW_Signed.pdf").write_text("x", encoding="utf-8")
            (folder_b / "01_Drawing.pdf").write_text("drawing", encoding="utf-8")
            (folder_b / "18_PSW_Signed.pdf").write_text("x", encoding="utf-8")

            mixed = triage_inbox(inbox)
            mixed_design = next(item for item in mixed.elements if item.element.number == 1)
            self.assertEqual(mixed_design.status, "duplicate")

            packages = discover_submission_packages(inbox)
            self.assertEqual([package.name for package in packages], [folder_a.name, folder_b.name])

            results = triage_packages(inbox)
            self.assertEqual(len(results), 2)
            for _package, report in results:
                design = next(item for item in report.elements if item.element.number == 1)
                psw = next(item for item in report.elements if item.element.number == 18)
                self.assertEqual(design.status, "present")
                self.assertEqual(psw.status, "present")

            with tempfile.TemporaryDirectory() as output_dir:
                written = write_package_reports(results, Path(output_dir))
                self.assertEqual(len(written), 2)
                self.assertTrue((Path(output_dir) / "packages-index.json").exists())
                self.assertTrue((Path(output_dir) / folder_a.name / "triage-report.json").exists())
                self.assertTrue((Path(output_dir) / folder_b.name / "sqe-checklist.md").exists())


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
