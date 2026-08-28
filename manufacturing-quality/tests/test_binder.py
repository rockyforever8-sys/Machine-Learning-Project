from __future__ import annotations

import tempfile
import unittest
from types import SimpleNamespace
from pathlib import Path

from ppap_inbox_triage.binder import (
    classify_binder_pages,
    find_index_pages,
    is_index_page,
    is_psw_form,
    compact_text,
    normalize_text,
    score_page,
)
from ppap_inbox_triage.models import InboxFile, match_evidence
from ppap_inbox_triage.pdf_text import pdf_text_available
from ppap_inbox_triage.sqe_checklist import compact_page_range
from ppap_inbox_triage.triage import triage_inbox

from pdf_fixture import write_multipage_text_pdf


TOC_PAGE = """
TABLE OF CONTENTS
1. Design Records ................................ 3
2. Engineering Change Documents .................. 8
3. Customer Engineering Approval ................. 10
4. Design FMEA ................................... 12
5. Process Flow Diagram .......................... 20
6. Process FMEA .................................. 24
7. Control Plan .................................. 40
8. MSA Studies ................................... 52
9. Dimensional Results ........................... 60
10. Material / Performance Test Results .......... 75
11. Initial Process Studies ...................... 82
12. Qualified Laboratory Documentation ........... 90
13. Appearance Approval Report ................... 94
14. Sample Production Parts ...................... 96
15. Master Sample ................................ 98
16. Checking Aids ................................ 100
17. Customer-Specific Requirements ............... 105
18. Part Submission Warrant ...................... 110
"""

PSW_WITH_CHECKLIST = """
Part Submission Warrant
Part Name: Bracket  Part Number: 1616-5YY3235
Engineering drawing change level: A
Shown on drawing number: 1616-5YY3235
Purchase order no: PO-9921
Submission level: Level 3
Declaration: I hereby warrant the samples represented by this warrant
Supplier authorized signature: J. Supplier
The following documents are attached:
1. Design Records
2. Engineering Change Documents
3. Customer Engineering Approval
4. Design FMEA
5. Process Flow Diagram
6. Process FMEA
7. Control Plan
8. MSA Studies
9. Dimensional Results
10. Material / Performance Test Results
11. Initial Process Studies
12. Qualified Laboratory Documentation
13. Appearance Approval Report
14. Sample Production Parts
15. Master Sample
16. Checking Aids
17. Customer-Specific Requirements
18. Part Submission Warrant
"""

BINDER_PAGES = [
    "PPAP Level 3 Submission Cover Part 1616-5YY3235 Supplier RKG",
    TOC_PAGE,
    "1. Design Records  Drawing number 1616-5YY3235 title block revision B engineering drawing scale 1:1",
    "2. Engineering Change Documents  ECO no 4412 engineering change order effectivity date 2021-02-01 reason for change",
    "3. Customer Engineering Approval  customer engineering approval signed deviation permit approved by customer",
    "4. Design FMEA  DFMEA design function potential failure mode severity occurrence detection RPN recommended action",
    "5. Process Flow Diagram  process flow diagram incoming material operation description process step shipping rework",
    "6. Process FMEA  PFMEA process function current process control potential failure mode severity occurrence detection RPN",
    "SEV OCC DET RPN 8 4 6 192 process step weld failure mode porosity process control visual inspection",
    "7. Control Plan  production control plan reaction plan sample size sample frequency control method special characteristic",
    "8. MSA Studies  measurement system analysis gage r&r repeatability reproducibility percent GRR ANOVA NDC",
    "9. Dimensional Results  layout inspection first article FAI balloon no 12 CMM report measured value nominal in spec",
    "10. Material / Performance Test Results  mill certificate certificate of analysis tensile strength chemical composition heat number",
    "11. Initial Process Studies  process capability study Cpk 1.67 Ppk 1.52 USL LSL subgroup special characteristic",
    "12. Qualified Laboratory Documentation  ISO 17025 laboratory accreditation certificate of accreditation laboratory scope A2LA",
    "13. Appearance Approval Report  appearance approval color gloss texture master plaque AAR",
    "14. Sample Production Parts  sample production parts sample tag quantity 6 packing list shipped samples",
    "15. Master Sample  master sample retained master sample agreement storage location",
    "16. Checking Aids  checking fixture go/no-go checking aid number CF-16 calibration",
    "17. Customer-Specific Requirements  customer specific requirement CSR checklist OEM requirement IATF addendum",
    PSW_WITH_CHECKLIST,
]


def _inbox_file(name: str) -> InboxFile:
    return InboxFile(
        path=Path(name),
        relative_path=name,
        name=name,
        suffix=".pdf",
        size_bytes=1,
    )


class BinderSemanticsTests(unittest.TestCase):
    def test_detects_table_of_contents_page(self) -> None:
        self.assertTrue(is_index_page(TOC_PAGE))
        self.assertIn(2, find_index_pages([(1, "Cover page"), (2, TOC_PAGE), (3, "Design Records drawing number")]))

    def test_does_not_treat_pfmea_body_as_index(self) -> None:
        body = "6. Process FMEA PFMEA process function current process control RPN severity occurrence detection"
        self.assertFalse(is_index_page(body))

    def test_psw_form_detected_even_with_document_list(self) -> None:
        normalized = normalize_text(PSW_WITH_CHECKLIST)
        self.assertTrue(is_psw_form(normalized, compact_text(normalized)))

    def test_toc_page_assigns_no_elements(self) -> None:
        matches = classify_binder_pages(
            _inbox_file("PPAP Level 3_binder.pdf"),
            [(1, "Cover"), (2, TOC_PAGE)],
        )
        self.assertEqual(matches, [])

    def test_actual_section_pages_not_toc(self) -> None:
        page_texts = list(enumerate(BINDER_PAGES, start=1))
        matches = classify_binder_pages(_inbox_file("PPAP Level 3_binder.pdf"), page_texts)
        pages_by_element: dict[int, list[int]] = {}
        for match in matches:
            pages_by_element.setdefault(match.element.number, []).append(match.page_number or 0)

        self.assertNotIn(2, [page for pages in pages_by_element.values() for page in pages])
        self.assertIn(8, pages_by_element.get(6, []))
        self.assertIn(9, pages_by_element.get(6, []))
        self.assertEqual(pages_by_element.get(18), [21])
        self.assertNotIn(1, [match.element.number for match in matches if match.page_number == 21])
        self.assertIn(3, pages_by_element.get(1, []))
        self.assertGreaterEqual(len(pages_by_element), 10)

    def test_score_requires_more_than_a_title(self) -> None:
        self.assertEqual(score_page("Dimensional"), [])
        body_scores = score_page(
            "Process FMEA PFMEA current process control potential failure mode RPN severity occurrence detection"
        )
        self.assertTrue(any(item.element.number == 6 and item.score >= 1.0 for item in body_scores))
        self.assertFalse(any(item.element.number == 4 for item in body_scores))

    def test_compact_page_range(self) -> None:
        self.assertEqual(compact_page_range([8, 9, 10, 21]), "8-10, 21")
        self.assertEqual(compact_page_range([]), "—")

    def test_match_evidence_compatible_with_old_objects(self) -> None:
        self.assertEqual(match_evidence(SimpleNamespace()), ())
        self.assertEqual(match_evidence(SimpleNamespace(evidence=("pfmea", "rpn"))), ("pfmea", "rpn"))


@unittest.skipUnless(pdf_text_available(), "pypdf is required for PDF extraction tests")
class BinderInboxTriageTests(unittest.TestCase):
    def test_137_page_style_binder_ignores_toc_and_finds_sections(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            inbox = Path(temp_dir)
            pdf_path = inbox / "PPAP Level 3_1616-5YY3235_RKG-25V392MK9WZQ-FC6_26-02-2021.pdf"
            write_multipage_text_pdf(pdf_path, BINDER_PAGES)

            report = triage_inbox(inbox, use_pdf_text=True)
            self.assertEqual(report.summary["submission_layout"], "binder")
            self.assertIn(2, report.summary["index_pages_skipped"])

            pages_by_element = {
                item.element.number: [
                    match.page_number for match in item.matches if match.page_number is not None
                ]
                for item in report.elements
            }

            for number, pages in pages_by_element.items():
                self.assertNotIn(2, pages, f"Element {number} should not use the TOC page")

            self.assertEqual(report.elements[5].status, "present")  # PFMEA is 0-indexed element 6
            pfmea_pages = pages_by_element[6]
            self.assertIn(8, pfmea_pages)
            self.assertIn(9, pfmea_pages)

            psw_pages = pages_by_element[18]
            self.assertEqual(psw_pages, [21])

            present = [item.element.number for item in report.elements if item.status == "present"]
            self.assertGreaterEqual(len(present), 15)
            self.assertIn(6, present)
            self.assertIn(7, present)
            self.assertIn(18, present)

            pfmea = next(item for item in report.elements if item.element.number == 6)
            self.assertTrue(any("AIAG content evidence" in note for note in pfmea.notes))
            self.assertTrue(any("Detected in PPAP binder pages: 8-9" in note for note in pfmea.notes))


if __name__ == "__main__":
    unittest.main()
