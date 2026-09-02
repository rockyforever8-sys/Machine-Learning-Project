from __future__ import annotations

import re

from .models import InboxFile, SubmissionLayout

BINDER_FILENAME_PATTERNS: tuple[str, ...] = (
    r"^ppap\b",
    r"ppap[\s_-]?level[\s_-]?3",
    r"ppap[\s_-]?level[\s_-]?\d",
    r"ppap[\s_-]?package",
    r"ppap[\s_-]?submission",
    r"ppap[\s_-]?binder",
    r"full[\s_-]?ppap",
    r"complete[\s_-]?ppap",
    r"ppap[\s_-]?提交",
    r"ppap[\s_-]?卷宗",
    r"ppap[\s_-]?资料",
    r"ppap[\s_-]?資料",
    r"全套[\s_-]?ppap",
    r"完整[\s_-]?ppap",
    r"第[3三]级",
    r"第[3三]級",
)

DISCRETE_FILENAME_TOKENS: tuple[str, ...] = (
    "pfmea",
    "dfmea",
    "psw",
    "control plan",
    "fai",
    "控制计划",
    "控制計劃",
    "过程fmea",
    "過程fmea",
    "保证书",
    "保證書",
    "设计记录",
    "設計記錄",
    "尺寸结果",
    "尺寸結果",
)

MIN_BINDER_CONTENT_ELEMENTS = 3
MIN_DISCRETE_FILE_COUNT = 8
MIN_BINDER_PAGE_COUNT = 8
MIN_BINDER_SIZE_BYTES = 400_000


def _normalize_filename(filename: str) -> str:
    from .binder import normalize_text

    return normalize_text(filename)


def is_binder_filename(filename: str) -> bool:
    normalized = _normalize_filename(filename)
    if re.match(r"^ppap\b", normalized):
        return True
    return any(re.search(pattern, normalized) for pattern in BINDER_FILENAME_PATTERNS)


def _looks_like_standalone_psw(filename: str) -> bool:
    normalized = _normalize_filename(filename)
    return bool(
        re.search(r"\bpsw\b", normalized)
        or "零件提交保证" in normalized
        or "零件提交保證" in normalized
    )


def _looks_like_package_pdf(inbox_file: InboxFile) -> bool:
    """Large/multi-page PDFs named as a package, not a standalone PSW."""
    if inbox_file.suffix.lower() != ".pdf":
        return False
    if _looks_like_standalone_psw(inbox_file.name):
        return False
    if inbox_file.size_bytes < 10_000:
        return False
    if inbox_file.size_bytes >= MIN_BINDER_SIZE_BYTES:
        return True
    from .pdf_text import pdf_page_count

    return pdf_page_count(inbox_file.path) >= MIN_BINDER_PAGE_COUNT


def _has_numbered_ppap_prefix(filename: str) -> bool:
    match = re.match(r"^(\d{1,2})[_\-.]", filename)
    if not match:
        return False
    return 1 <= int(match.group(1)) <= 18


def detect_submission_layout(
    inbox_files: list[InboxFile],
    *,
    binder_candidates: set[str],
    discrete_file_count: int,
) -> SubmissionLayout:
    if not inbox_files:
        return SubmissionLayout.DISCRETE

    if binder_candidates and discrete_file_count >= MIN_DISCRETE_FILE_COUNT:
        return SubmissionLayout.MIXED

    if binder_candidates:
        return SubmissionLayout.BINDER

    if len(inbox_files) == 1:
        only_file = inbox_files[0]
        if only_file.suffix.lower() == ".pdf" and (
            is_binder_filename(only_file.name) or only_file.name.lower().startswith("ppap")
        ):
            return SubmissionLayout.BINDER

    if discrete_file_count >= MIN_DISCRETE_FILE_COUNT:
        return SubmissionLayout.DISCRETE

    return SubmissionLayout.DISCRETE


def identify_binder_candidates(
    inbox_files: list[InboxFile],
    element_hits_by_file: dict[str, set[int]],
) -> set[str]:
    binder_files: set[str] = set()

    for inbox_file in inbox_files:
        if inbox_file.suffix.lower() != ".pdf":
            continue

        content_hits = element_hits_by_file.get(inbox_file.relative_path, set())
        if is_binder_filename(inbox_file.name) or _looks_like_package_pdf(inbox_file):
            binder_files.add(inbox_file.relative_path)
            continue

        if len(inbox_files) <= 3 and len(content_hits) >= MIN_BINDER_CONTENT_ELEMENTS:
            binder_files.add(inbox_file.relative_path)

    if len(inbox_files) == 1:
        only_file = inbox_files[0]
        only_hits = element_hits_by_file.get(only_file.relative_path, set())
        if only_file.suffix.lower() == ".pdf" and (
            is_binder_filename(only_file.name)
            or _looks_like_package_pdf(only_file)
            or len(only_hits) >= MIN_BINDER_CONTENT_ELEMENTS
            or only_file.name.lower().startswith("ppap")
        ):
            binder_files.add(only_file.relative_path)

    return binder_files


def count_discrete_files(
    inbox_files: list[InboxFile],
    binder_files: set[str],
) -> int:
    count = 0
    for inbox_file in inbox_files:
        if inbox_file.relative_path in binder_files:
            continue
        if _has_numbered_ppap_prefix(inbox_file.name):
            count += 1
            continue
        normalized = _normalize_filename(inbox_file.name)
        if any(token in normalized for token in DISCRETE_FILENAME_TOKENS):
            count += 1
    return count
