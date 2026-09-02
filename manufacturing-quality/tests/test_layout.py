from __future__ import annotations

import unittest
from pathlib import Path

from ppap_inbox_triage.layout import (
    detect_submission_layout,
    identify_binder_candidates,
    is_binder_filename,
)
from ppap_inbox_triage.models import InboxFile, SubmissionLayout


def _file(name: str, *, size: int = 100, relative: str | None = None) -> InboxFile:
    return InboxFile(
        path=Path(name),
        relative_path=relative or name,
        name=name,
        suffix=Path(name).suffix.lower(),
        size_bytes=size,
    )


class BinderFilenameTests(unittest.TestCase):
    def test_ppap_underscore_part_number_is_binder(self) -> None:
        self.assertTrue(is_binder_filename("PPAP_1431-8YY0024(A) from zhiye.pdf"))
        self.assertTrue(is_binder_filename("PPAP_1431-8YY0024(A)\u00a0from zhiye.pdf"))
        self.assertTrue(is_binder_filename("ppap1431-package.pdf"))

    def test_standalone_psw_is_not_binder(self) -> None:
        self.assertFalse(is_binder_filename("PSW_1431-8YY0024A_Approved.pdf"))
        self.assertFalse(is_binder_filename("18_PSW_Signed.pdf"))


class AutoLayoutTests(unittest.TestCase):
    def test_mixed_folder_marks_package_pdf_not_psw(self) -> None:
        files = [
            _file("PPAP_1431-8YY0024(A) from zhiye.pdf", size=200),
            _file("PSW_1431-8YY0024A_Approved.pdf", size=200),
            _file("1431-8YY0024 A.xlsx", size=80),
        ]
        binders = identify_binder_candidates(files, {})
        self.assertEqual(binders, {"PPAP_1431-8YY0024(A) from zhiye.pdf"})
        layout = detect_submission_layout(
            files,
            binder_candidates=binders,
            discrete_file_count=1,
        )
        self.assertEqual(layout, SubmissionLayout.MIXED)

    def test_companion_pdf_next_to_psw_is_binder_without_ppap_prefix(self) -> None:
        files = [
            _file("1431-8YY0024(A) from zhiye.pdf", size=200),
            _file("PSW_1431-8YY0024A_Approved.pdf", size=200),
        ]
        binders = identify_binder_candidates(files, {})
        self.assertEqual(binders, {"1431-8YY0024(A) from zhiye.pdf"})

    def test_lone_drawing_is_not_treated_as_binder(self) -> None:
        files = [_file("01_Drawing.pdf", size=200)]
        binders = identify_binder_candidates(files, {})
        self.assertEqual(binders, set())
        layout = detect_submission_layout(
            files,
            binder_candidates=binders,
            discrete_file_count=1,
        )
        self.assertEqual(layout, SubmissionLayout.DISCRETE)

    def test_drawing_next_to_psw_stays_discrete(self) -> None:
        files = [
            _file("01_Drawing.pdf", size=200),
            _file("18_PSW_Signed.pdf", size=200),
        ]
        binders = identify_binder_candidates(files, {})
        self.assertEqual(binders, set())
        layout = detect_submission_layout(
            files,
            binder_candidates=binders,
            discrete_file_count=2,
        )
        self.assertEqual(layout, SubmissionLayout.DISCRETE)


if __name__ == "__main__":
    unittest.main()
