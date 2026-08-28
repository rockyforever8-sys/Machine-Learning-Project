from __future__ import annotations

from pathlib import Path

DEFAULT_MAX_PAGES = 5


def pdf_text_available() -> bool:
    try:
        import pypdf  # noqa: F401
    except ImportError:
        return False
    return True


def extract_pdf_text(path: Path, *, max_pages: int = DEFAULT_MAX_PAGES) -> str | None:
    """Extract text from the first pages of a PDF file.

    Returns None when pypdf is not installed or the file cannot be read.
    """
    try:
        from pypdf import PdfReader
    except ImportError:
        return None

    if path.suffix.lower() != ".pdf":
        return None

    try:
        reader = PdfReader(str(path))
    except Exception:
        return None

    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception:
            return None

    chunks: list[str] = []
    for page in reader.pages[:max_pages]:
        try:
            text = page.extract_text() or ""
        except Exception:
            continue
        if text.strip():
            chunks.append(text)

    combined = "\n".join(chunks).strip()
    return combined or None
