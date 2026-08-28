from __future__ import annotations

from pathlib import Path

DEFAULT_MAX_PAGES = 5
ALL_PAGES = 0


def pdf_text_available() -> bool:
    try:
        import pypdf  # noqa: F401
    except ImportError:
        return False
    return True


def _read_pdf_pages(path: Path) -> list[tuple[int, str]]:
    try:
        from pypdf import PdfReader
    except ImportError:
        return []

    try:
        reader = PdfReader(str(path))
    except Exception:
        return []

    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception:
            return []

    pages: list[tuple[int, str]] = []
    for index, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception:
            continue
        if text.strip():
            pages.append((index, text))
    return pages


def extract_pdf_pages(
    path: Path,
    *,
    max_pages: int = DEFAULT_MAX_PAGES,
) -> list[tuple[int, str]]:
    """Extract text per page from a PDF.

    Pass max_pages=0 (ALL_PAGES) to scan every page — used for binder analysis.
    """
    pages = _read_pdf_pages(path)
    if max_pages == ALL_PAGES:
        return pages
    return pages[:max_pages]


def extract_pdf_text(path: Path, *, max_pages: int = DEFAULT_MAX_PAGES) -> str | None:
    page_texts = extract_pdf_pages(path, max_pages=max_pages)
    if not page_texts:
        return None
    return "\n".join(text for _, text in page_texts).strip() or None
