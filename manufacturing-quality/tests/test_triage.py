from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ppap_inbox_triage.classifier import classify_file
from ppap_inbox_triage.models import InboxFile, MatchConfidence
from ppap_inbox_triage.report import report_to_dict, write_all_reports
from ppap_inbox_triage.scanner import scan_inbox
from ppap_inbox_triage.triage import triage_inbox


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


class ScannerTests(unittest.TestCase):
    def test_scan_fixture_inbox(self) -> None:
        files = scan_inbox(FIXTURES)
        names = {file.name for file in files}
        self.assertIn("18_PSW_Signed.pdf", names)
        self.assertIn("random_supplier_cover_letter.pdf", names)


class TriageTests(unittest.TestCase):
    def test_sample_inbox_triage(self) -> None:
        report = triage_inbox(FIXTURES)
        self.assertEqual(report.submission_level, 3)
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

        payload = report_to_dict(report)
        self.assertEqual(len(payload["elements"]), 18)
        self.assertIn("actions", payload)


if __name__ == "__main__":
    unittest.main()
