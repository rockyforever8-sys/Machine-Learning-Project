from __future__ import annotations

import re

from .binder import (
    classify_binder_pages,
    compact_text,
    has_cjk,
    is_index_page,
    is_psw_form,
    marker_present,
)
from .elements import PPAP_LEVEL_3_ELEMENTS
from .models import ElementMatch, InboxFile, MatchConfidence, PpapElement

DESIGN_RECORD_EXCLUSIONS = ("fixture", "checking aid", "template", "gage", "gauge")
CONTENT_SCORE_BOOST = 1.1
FILENAME_PREFIX_BOOST = 1.25
BINDER_PAGE_SCORE_BOOST = 1.15
CONTENT_MATCH_THRESHOLD = 0.6


def _normalize(text: str) -> str:
    from .binder import normalize_text

    return normalize_text(text)


def _ppap_prefix_number(filename: str) -> int | None:
    match = re.match(r"^(\d{1,2})[_\-.]", filename)
    if not match:
        return None
    number = int(match.group(1))
    if 1 <= number <= 18:
        return number
    return None


def _pattern_matches(normalized_text: str, compact: str, pattern: str) -> bool:
    if not pattern:
        return False
    if has_cjk(pattern):
        return marker_present(normalized_text, compact, pattern)
    try:
        return re.search(pattern, normalized_text, flags=re.IGNORECASE) is not None
    except re.error:
        return marker_present(normalized_text, compact, pattern)


def _score_match(
    element: PpapElement,
    normalized_text: str,
    compact: str,
    pattern: str,
    *,
    is_filename: bool,
) -> float:
    if is_filename and element.number == 1 and pattern == r"\bdrawing\b":
        if any(term in normalized_text for term in DESIGN_RECORD_EXCLUSIONS):
            return 0.0

    if not _pattern_matches(normalized_text, compact, pattern):
        return 0.0
    if any(marker_present(normalized_text, compact, alias) for alias in element.aliases):
        return 1.0
    return 0.85


def _confidence_for_score(score: float) -> MatchConfidence | None:
    if score >= 0.8:
        return MatchConfidence.HIGH
    if score >= 0.6:
        return MatchConfidence.MEDIUM
    if score > 0:
        return MatchConfidence.LOW
    return None


def _classify_normalized_text(
    file: InboxFile,
    normalized_text: str,
    *,
    source: str,
    prefix_number: int | None = None,
    apply_prefix_rules: bool = False,
    page_number: int | None = None,
) -> list[ElementMatch]:
    matches: list[ElementMatch] = []
    match_mode = "filename"
    if source == "content":
        match_mode = "content"
    if source == "binder":
        match_mode = "binder"

    compact = compact_text(normalized_text)
    for element in PPAP_LEVEL_3_ELEMENTS:
        best_score = 0.0
        best_pattern = ""

        for pattern in element.filename_patterns:
            score = _score_match(
                element,
                normalized_text,
                compact,
                pattern,
                is_filename=source == "filename",
            )
            if score > best_score:
                best_score = score
                best_pattern = pattern

        for alias in element.aliases:
            if (
                source == "filename"
                and element.number == 1
                and alias == "drawing"
                and any(term in normalized_text for term in DESIGN_RECORD_EXCLUSIONS)
            ):
                continue
            if marker_present(normalized_text, compact, alias) and best_score < 0.8:
                best_score = 0.8
                best_pattern = f"{source}:alias:{alias}"

        if apply_prefix_rules and prefix_number == element.number and best_score > 0:
            best_score = max(best_score, FILENAME_PREFIX_BOOST)
            best_pattern = f"prefix:{prefix_number}"
        elif (
            apply_prefix_rules
            and prefix_number is not None
            and prefix_number != element.number
            and best_score < 1.0
        ):
            best_score *= 0.5

        if source in {"content", "binder"} and best_score > 0:
            boost = BINDER_PAGE_SCORE_BOOST if source == "binder" else CONTENT_SCORE_BOOST
            best_score = min(best_score * boost, 1.2)
            if not best_pattern.startswith(f"{source}:"):
                best_pattern = f"{source}:{best_pattern}"

        confidence = _confidence_for_score(best_score)
        if confidence is None:
            continue

        matches.append(
            ElementMatch(
                element=element,
                file=file,
                confidence=confidence,
                matched_pattern=best_pattern,
                score=best_score,
                page_number=page_number,
                match_mode=match_mode,
            )
        )

    return matches


def _merge_matches(*match_groups: list[ElementMatch]) -> list[ElementMatch]:
    best_by_element: dict[int, ElementMatch] = {}
    for group in match_groups:
        for match in group:
            current = best_by_element.get(match.element.number)
            if current is None or match.score > current.score:
                best_by_element[match.element.number] = match

    return sorted(
        best_by_element.values(),
        key=lambda match: (-match.score, match.element.number),
    )


def _looks_like_psw_filename(filename: str) -> bool:
    normalized = _normalize(filename)
    compact = compact_text(normalized)
    return any(
        marker_present(normalized, compact, marker)
        for marker in (
            "psw",
            "part submission warrant",
            "零件提交保证书",
            "零件提交保證書",
            "提交保证书",
            "提交保證書",
        )
    )


def _keep_psw_matches(matches: list[ElementMatch]) -> list[ElementMatch]:
    psw_matches = [match for match in matches if match.element.number == 18]
    return psw_matches or matches


def classify_file(
    file: InboxFile,
    *,
    text_content: str | None = None,
    page_texts: list[tuple[int, str]] | None = None,
) -> list[ElementMatch]:
    normalized_name = _normalize(file.name)
    prefix_number = _ppap_prefix_number(file.name)
    psw_filename = _looks_like_psw_filename(file.name)

    filename_matches = _classify_normalized_text(
        file,
        normalized_name,
        source="filename",
        prefix_number=prefix_number,
        apply_prefix_rules=True,
    )
    if psw_filename:
        filename_matches = _keep_psw_matches(filename_matches)

    content_groups: list[list[ElementMatch]] = []
    psw_form = False
    if text_content:
        normalized_content = _normalize(text_content)
        compact_content = compact_text(normalized_content)
        psw_form = is_psw_form(normalized_content, compact_content)
        # A PSW attached-document list (or other TOC) names every element.
        # That checklist is not evidence that those documents are in this file.
        if psw_form:
            content_groups.append(
                _keep_psw_matches(
                    _classify_normalized_text(
                        file,
                        normalized_content,
                        source="content",
                        apply_prefix_rules=False,
                    )
                )
            )
        elif not is_index_page(text_content, normalized_content):
            content_groups.append(
                _classify_normalized_text(
                    file,
                    normalized_content,
                    source="content",
                    apply_prefix_rules=False,
                )
            )

    if page_texts:
        for page_number, page_text in page_texts:
            content_groups.append(
                _classify_normalized_text(
                    file,
                    _normalize(page_text),
                    source="binder",
                    apply_prefix_rules=False,
                    page_number=page_number,
                )
            )

    if not content_groups:
        return filename_matches

    merged = _merge_matches(filename_matches, *content_groups)
    if psw_filename or psw_form:
        return _keep_psw_matches(merged)
    return merged


def content_element_hits(matches: list[ElementMatch]) -> set[int]:
    hits: set[int] = set()
    for match in matches:
        if match.match_mode in {"content", "binder"} and match.score >= CONTENT_MATCH_THRESHOLD:
            hits.add(match.element.number)
    return hits


def classify_binder_pdf(
    file: InboxFile,
    page_texts: list[tuple[int, str]],
) -> list[ElementMatch]:
    return classify_binder_pages(file, page_texts)
