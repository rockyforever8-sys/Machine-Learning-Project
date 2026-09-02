from __future__ import annotations

import unittest
from unittest import mock

from ppap_inbox_triage.models import InboxFile
from ppap_inbox_triage.quality_analysis import (
    QUALITY_PARSER_VERSION,
    _extract_capability_values,
    _extract_grr_values,
    _is_spurious_capability_reading,
    _parse_pfmea_rows,
    analyze_inbox_quality,
)


class QualityMetricExtractionTests(unittest.TestCase):
    def test_extract_grr_flags_above_ten(self) -> None:
        text = "Measurement System Analysis Gage R&R study percent GRR 12.5%"
        values = _extract_grr_values(text)
        self.assertTrue(any(value > 10 for value, _ in values))

    def test_extract_grr_passes_at_ten(self) -> None:
        text = "%GRR = 8.2%"
        values = _extract_grr_values(text)
        self.assertEqual(values[0][0], 8.2)

    def test_extract_cpk_below_benchmark(self) -> None:
        text = "Initial process capability study Cpk 1.12 Ppk 1.05 USL LSL"
        values = _extract_capability_values(text)
        labels = {label: value for label, value, _ in values}
        self.assertLess(labels["Cpk"], 1.33)
        self.assertLess(labels["Ppk"], 1.33)

    def test_cpk_list_index_is_not_capability_value(self) -> None:
        """PDFs often show 'Cpk 1' as a row/characteristic label, not Cpk = 1.0."""
        text = (
            "Cpk 1 Cpk 2.23 Cpk 3.80 2.23 Cpk 3.80 Cpk "
            "Cpk 2.13 Cpk 3.29 2.13 Cpk 3.29 Cpk"
        )
        values = _extract_capability_values(text)
        cpk_values = [value for label, value, _ in values if label == "Cpk"]
        self.assertNotIn(1.0, cpk_values)
        self.assertIn(2.23, cpk_values)
        self.assertIn(3.8, cpk_values)
        self.assertIn(2.13, cpk_values)
        self.assertIn(3.29, cpk_values)

    def test_explicit_cpk_assignment_allows_integer(self) -> None:
        text = "Process capability index Cpk = 1.05 Ppk: 1.08"
        values = _extract_capability_values(text)
        labels = {label: value for label, value, _ in values}
        self.assertEqual(labels["Cpk"], 1.05)
        self.assertEqual(labels["Ppk"], 1.08)

    def test_spurious_capability_guard_rejects_cpk_one_label(self) -> None:
        self.assertTrue(_is_spurious_capability_reading("Cpk", 1.0, "Cpk 1"))
        self.assertFalse(_is_spurious_capability_reading("Cpk", 2.23, "Cpk 2.23"))

    def test_analyze_skips_cpk_one_row_label(self) -> None:
        inbox_file = InboxFile(
            path=__import__("pathlib").Path("SAMSUNG CL21Y475KBBVPJE.pdf"),
            relative_path="SAMSUNG CL21Y475KBBVPJE.pdf",
            name="SAMSUNG CL21Y475KBBVPJE.pdf",
            suffix=".pdf",
            size_bytes=1,
        )

        class FakePages:
            @staticmethod
            def extract_pdf_pages(path, max_pages=0):
                return [
                    (
                        124,
                        "Cpk 1 Cpk 2.23 Cpk 3.80 2.23 Cpk 3.80 Cpk Cpk 2.13 Cpk 3.29",
                    ),
                ]

        with mock.patch(
            "ppap_inbox_triage.quality_analysis.extract_pdf_pages",
            FakePages.extract_pdf_pages,
        ):
            analysis = analyze_inbox_quality(
                [inbox_file],
                use_pdf_text=True,
                binder_files={"SAMSUNG CL21Y475KBBVPJE.pdf"},
            )

        cpk_values = [item.value for item in analysis.capability_findings if item.metric == "Cpk"]
        self.assertNotIn(1.0, cpk_values)
        self.assertTrue(any(item.value == 2.23 for item in analysis.capability_findings))
        self.assertFalse(any("Cpk 1.00" in flag or "Cpk 1.0" in flag for flag in analysis.flags))
        self.assertEqual(analysis.to_summary()["parser_version"], QUALITY_PARSER_VERSION)

    def test_parse_pfmea_rows_and_countermeasures(self) -> None:
        text = (
            "Process FMEA PFMEA process step weld joint failure mode porosity "
            "8 4 6 192 current process control visual inspection"
        )
        rows = _parse_pfmea_rows(text, source_file="pfmea.pdf", page_number=6)
        self.assertTrue(rows)
        self.assertEqual(rows[0].rpn, 192)
        self.assertTrue(any("vent" in item.lower() or "melt" in item.lower() for item in rows[0].countermeasures))

    def test_parse_pfmea_table_lines_without_keyword(self) -> None:
        text = (
            "Failure mode / effect                    S  O  D  RPN\n"
            "Porosity in weld cavity visual escape      8  4  6  192\n"
            "Dimensional out of tolerance on bore        7  3  5  105\n"
            "Surface scratch from handling               6  4  4   96\n"
        )
        rows = _parse_pfmea_rows(text, source_file="binder.pdf", page_number=42)
        rpns = sorted((row.rpn for row in rows), reverse=True)
        self.assertEqual(rpns[:3], [192, 105, 96])
        self.assertTrue(rows[0].countermeasures)

    def test_analyze_pfmea_from_element_six_pages_without_keyword(self) -> None:
        inbox_file = InboxFile(
            path=__import__("pathlib").Path("PPAP_package.pdf"),
            relative_path="PPAP_package.pdf",
            name="PPAP_package.pdf",
            suffix=".pdf",
            size_bytes=1,
        )

        class FakePages:
            @staticmethod
            def extract_pdf_pages(path, max_pages=0):
                return [
                    (41, "Cover sheet"),
                    (
                        42,
                        "Control plan excerpt\n"
                        "Weld porosity at joint line              8 4 6 192\n"
                        "Leak at seal groove                      7 3 6 126\n",
                    ),
                ]

        with mock.patch(
            "ppap_inbox_triage.quality_analysis.extract_pdf_pages",
            FakePages.extract_pdf_pages,
        ):
            analysis = analyze_inbox_quality(
                [inbox_file],
                use_pdf_text=True,
                binder_files={"PPAP_package.pdf"},
                pfmea_pages_by_file={"PPAP_package.pdf": {42}},
            )

        self.assertEqual(len(analysis.pfmea_top_rpn), 2)
        self.assertEqual(analysis.pfmea_top_rpn[0].rpn, 192)
        self.assertEqual(analysis.pfmea_top_rpn[0].rank, 1)
        self.assertGreaterEqual(len(analysis.pfmea_top_rpn[0].countermeasures), 1)
        self.assertTrue(analysis.pfmea_benchmark_notes)
        self.assertTrue(analysis.pfmea_default_practices)


class QualityInboxAnalysisTests(unittest.TestCase):
    def test_analyze_flags_grr_cpk_and_pfmea(self) -> None:
        inbox_file = InboxFile(
            path=__import__("pathlib").Path("binder.pdf"),
            relative_path="binder.pdf",
            name="binder.pdf",
            suffix=".pdf",
            size_bytes=1,
        )

        class FakePages:
            @staticmethod
            def extract_pdf_pages(path, max_pages=0):
                return [
                    (
                        8,
                        "MSA Studies measurement system analysis gage r&r repeatability percent GRR 14.2%",
                    ),
                    (
                        11,
                        "Initial Process Studies process capability Cpk 1.05 Ppk 1.08 subgroup",
                    ),
                    (
                        6,
                        "Process FMEA PFMEA porosity in weld 8 4 6 192 process control",
                    ),
                ]

        with mock.patch(
            "ppap_inbox_triage.quality_analysis.extract_pdf_pages",
            FakePages.extract_pdf_pages,
        ):
            analysis = analyze_inbox_quality(
                [inbox_file],
                use_pdf_text=True,
                binder_files={"binder.pdf"},
            )

        self.assertTrue(any("MSA %GRR" in flag for flag in analysis.flags))
        self.assertTrue(any("Cpk" in flag for flag in analysis.flags))
        self.assertEqual(len(analysis.pfmea_top_rpn), 1)
        self.assertGreaterEqual(len(analysis.actions), 2)


if __name__ == "__main__":
    unittest.main()
