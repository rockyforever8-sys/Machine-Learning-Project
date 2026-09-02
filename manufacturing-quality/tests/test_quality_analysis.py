from __future__ import annotations

import unittest

from ppap_inbox_triage.models import InboxFile
from ppap_inbox_triage.quality_analysis import (
    _extract_capability_values,
    _extract_grr_values,
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

    def test_parse_pfmea_rows_and_countermeasures(self) -> None:
        text = (
            "Process FMEA PFMEA process step weld joint failure mode porosity "
            "8 4 6 192 current process control visual inspection"
        )
        rows = _parse_pfmea_rows(text, source_file="pfmea.pdf", page_number=6)
        self.assertTrue(rows)
        self.assertEqual(rows[0].rpn, 192)
        self.assertTrue(any("vent" in item.lower() or "melt" in item.lower() for item in rows[0].countermeasures))


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

        with unittest.mock.patch(
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
