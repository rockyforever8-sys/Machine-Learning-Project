from __future__ import annotations

import re
from dataclasses import dataclass

from .elements import ELEMENT_BY_NUMBER, PPAP_LEVEL_3_ELEMENTS
from .models import ElementMatch, InboxFile, MatchConfidence, PpapElement

INDEX_PHRASES: tuple[str, ...] = (
    "table of contents",
    "table of content",
    "table content",
    "contents page",
    "list of documents",
    "document index",
    "ppap contents",
    "submission contents",
    "index of ppap",
    "list of ppap elements",
    "ppap element list",
)

PSW_FORM_MARKERS: tuple[str, ...] = (
    "part submission warrant",
    "supplier authorized signature",
    "submission level",
    "engineering drawing change level",
    "shown on drawing",
    "purchase order",
    "declaration",
    "authorized customer representative",
    "molds / dies",
    "checking aid no",
)

INDEX_TITLE_HIT_THRESHOLD = 8
INDEX_NUMBERED_THRESHOLD = 8
MULTI_TITLE_PAGE_THRESHOLD = 4
CONTINUATION_GAP_LIMIT = 2
MIN_ASSIGN_SCORE = 0.6

HEADING_RE = re.compile(
    r"(?:^|\n)\s*(?:element\s+|ppap\s+element\s+)?(1[0-8]|[1-9])[\.\:\)]\s+([^\n]{3,90})",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class PageElementScore:
    element: PpapElement
    score: float
    confidence: MatchConfidence
    evidence: tuple[str, ...]
    unique_hits: int
    content_hits: int
    heading: bool
    title_hit: bool


def normalize_text(text: str) -> str:
    lowered = text.lower().replace("\u00a0", " ")
    lowered = lowered.replace("–", "-").replace("—", "-")
    return re.sub(r"[_\-.]+", " ", lowered)


def compact_text(normalized: str) -> str:
    return re.sub(r"\s+", "", normalized)


def marker_present(normalized: str, compact: str, marker: str) -> bool:
    marker_n = marker.lower().strip()
    if not marker_n:
        return False

    if " " in marker_n or len(marker_n) > 4:
        if marker_n in normalized:
            return True
        compact_marker = re.sub(r"\s+", "", marker_n)
        return len(compact_marker) >= 5 and compact_marker in compact

    pattern = rf"\b{re.escape(marker_n)}\b"
    if re.search(pattern, normalized):
        return True
    compact_marker = re.sub(r"[^a-z0-9&]+", "", marker_n)
    return len(compact_marker) >= 3 and re.search(
        rf"{re.escape(compact_marker)}", compact
    ) is not None


def _title_aliases(element: PpapElement) -> tuple[str, ...]:
    names = (element.name.lower(),) + tuple(alias.lower() for alias in element.aliases)
    return names


def element_title_hit(normalized: str, element: PpapElement) -> bool:
    for alias in _title_aliases(element):
        if " " in alias:
            if alias in normalized:
                return True
            continue
        if re.search(rf"\b{re.escape(alias)}\b", normalized):
            return True
    return False


def count_element_title_hits(normalized: str) -> set[int]:
    hits: set[int] = set()
    for element in PPAP_LEVEL_3_ELEMENTS:
        if element_title_hit(normalized, element):
            hits.add(element.number)
    return hits


def detect_numbered_headings(page_text: str) -> list[int]:
    found: list[int] = []
    for match in HEADING_RE.finditer(page_text):
        number = int(match.group(1))
        if number not in ELEMENT_BY_NUMBER:
            continue
        element = ELEMENT_BY_NUMBER[number]
        title = match.group(2).lower()
        if element.name.lower() in title or any(alias in title for alias in element.aliases):
            if number not in found:
                found.append(number)
    return found


def is_index_page(page_text: str, normalized: str | None = None) -> bool:
    normalized = normalized if normalized is not None else normalize_text(page_text)
    title_hits = count_element_title_hits(normalized)
    numbered_headings = detect_numbered_headings(page_text)

    if any(phrase in normalized for phrase in INDEX_PHRASES):
        return True
    if len(title_hits) >= INDEX_TITLE_HIT_THRESHOLD:
        return True
    if len(numbered_headings) >= INDEX_NUMBERED_THRESHOLD:
        return True
    if len(title_hits) >= 6 and len(numbered_headings) >= 6:
        return True
    return False


def is_psw_form(normalized: str, compact: str) -> bool:
    hits = sum(1 for marker in PSW_FORM_MARKERS if marker_present(normalized, compact, marker))
    return hits >= 3


def _collect_hits(
    normalized: str,
    compact: str,
    markers: tuple[str, ...],
) -> list[str]:
    hits: list[str] = []
    for marker in markers:
        if marker_present(normalized, compact, marker) and marker not in hits:
            hits.append(marker)
    return hits


def _excluded(normalized: str, compact: str, element: PpapElement) -> bool:
    if not element.exclude_markers:
        return False
    unique_hits = _collect_hits(normalized, compact, element.unique_markers)
    if unique_hits:
        return False
    return any(marker_present(normalized, compact, marker) for marker in element.exclude_markers)


def score_element_on_page(
    page_text: str,
    normalized: str,
    compact: str,
    element: PpapElement,
    *,
    numbered_headings: list[int],
) -> PageElementScore | None:
    if _excluded(normalized, compact, element):
        return None

    unique_hits = _collect_hits(normalized, compact, element.unique_markers)
    content_hits = _collect_hits(normalized, compact, element.content_markers)
    title_hit = element_title_hit(normalized, element)
    heading = element.number in numbered_headings
    if not heading and title_hit:
        first_chunk = normalized[:220]
        heading = first_chunk.strip().startswith(element.name.lower()) or (
            element.name.lower() in first_chunk[:80]
        )

    evidence = tuple(dict.fromkeys([*unique_hits, *content_hits[:6]]))
    unique_count = len(unique_hits)
    content_count = len(content_hits)

    score = 0.0
    confidence = MatchConfidence.LOW

    if unique_count >= 2 or (unique_count >= 1 and content_count >= 2):
        score = 1.15
        confidence = MatchConfidence.HIGH
    elif unique_count >= 1 and content_count >= 1:
        score = 1.1
        confidence = MatchConfidence.HIGH
    elif unique_count >= 1:
        score = 1.0
        confidence = MatchConfidence.HIGH
    elif content_count >= 3:
        score = 1.0
        confidence = MatchConfidence.HIGH
    elif heading and content_count >= 1:
        score = 0.9
        confidence = MatchConfidence.HIGH
    elif content_count >= 2:
        score = 0.85
        confidence = MatchConfidence.HIGH
    elif heading and title_hit:
        score = 0.72
        confidence = MatchConfidence.MEDIUM
    elif title_hit and content_count >= 1:
        score = 0.7
        confidence = MatchConfidence.MEDIUM
    elif heading:
        score = 0.65
        confidence = MatchConfidence.MEDIUM
    elif title_hit:
        score = 0.35
        confidence = MatchConfidence.LOW
    else:
        return None

    return PageElementScore(
        element=element,
        score=score,
        confidence=confidence,
        evidence=evidence,
        unique_hits=unique_count,
        content_hits=content_count,
        heading=heading,
        title_hit=title_hit,
    )


def score_page(
    page_text: str,
    *,
    normalized: str | None = None,
) -> list[PageElementScore]:
    normalized = normalized if normalized is not None else normalize_text(page_text)
    compact = compact_text(normalized)
    numbered_headings = detect_numbered_headings(page_text)

    scores: list[PageElementScore] = []
    for element in PPAP_LEVEL_3_ELEMENTS:
        scored = score_element_on_page(
            page_text,
            normalized,
            compact,
            element,
            numbered_headings=numbered_headings,
        )
        if scored is not None:
            scores.append(scored)

    assignable = [item for item in scores if item.score >= MIN_ASSIGN_SCORE]
    if len(assignable) >= MULTI_TITLE_PAGE_THRESHOLD:
        strong = [
            item
            for item in assignable
            if item.unique_hits >= 1 or item.content_hits >= 2 or item.score >= 1.0
        ]
        return sorted(strong, key=lambda item: (-item.score, item.element.number))

    return sorted(assignable, key=lambda item: (-item.score, item.element.number))


def _continuation_score(
    page_text: str,
    normalized: str,
    compact: str,
    element: PpapElement,
) -> PageElementScore | None:
    if _excluded(normalized, compact, element):
        return None

    unique_hits = _collect_hits(normalized, compact, element.unique_markers)
    content_hits = _collect_hits(normalized, compact, element.content_markers)
    continuation_hits = _collect_hits(normalized, compact, element.continuation_markers)
    numbered_headings = detect_numbered_headings(page_text)
    other_heading = any(number != element.number for number in numbered_headings)
    if other_heading:
        return None

    if unique_hits or len(content_hits) >= 1 or len(continuation_hits) >= 2:
        evidence = tuple(dict.fromkeys([*unique_hits, *content_hits, *continuation_hits[:4]]))
        return PageElementScore(
            element=element,
            score=0.75,
            confidence=MatchConfidence.MEDIUM,
            evidence=evidence or ("section continuation",),
            unique_hits=len(unique_hits),
            content_hits=len(content_hits),
            heading=False,
            title_hit=False,
        )

    return None


def find_index_pages(page_texts: list[tuple[int, str]]) -> list[int]:
    index_pages: list[int] = []
    for page_number, page_text in page_texts:
        if is_index_page(page_text):
            index_pages.append(page_number)
    return index_pages


def classify_binder_pages(
    file: InboxFile,
    page_texts: list[tuple[int, str]],
) -> list[ElementMatch]:
    matches: list[ElementMatch] = []
    current_element: PpapElement | None = None
    gap = 0

    for page_number, page_text in page_texts:
        normalized = normalize_text(page_text)
        compact = compact_text(normalized)

        if is_index_page(page_text, normalized):
            if is_psw_form(normalized, compact):
                psw = ELEMENT_BY_NUMBER[18]
                psw_score = score_element_on_page(
                    page_text,
                    normalized,
                    compact,
                    psw,
                    numbered_headings=detect_numbered_headings(page_text),
                )
                if psw_score is not None and psw_score.score >= MIN_ASSIGN_SCORE:
                    matches.append(_match_from_score(file, page_number, psw_score))
                    current_element = psw
                    gap = 0
                    continue
            current_element = None
            gap = 0
            continue

        page_scores = score_page(page_text, normalized=normalized)
        if page_scores:
            for scored in page_scores:
                matches.append(_match_from_score(file, page_number, scored))
            current_element = page_scores[0].element
            gap = 0
            continue

        if current_element is None:
            continue

        continued = _continuation_score(page_text, normalized, compact, current_element)
        if continued is not None:
            matches.append(_match_from_score(file, page_number, continued, continuation=True))
            gap = 0
        else:
            gap += 1
            if gap >= CONTINUATION_GAP_LIMIT:
                current_element = None

    return matches


def _match_from_score(
    file: InboxFile,
    page_number: int,
    scored: PageElementScore,
    *,
    continuation: bool = False,
) -> ElementMatch:
    prefix = "binder:continuation" if continuation else "binder:semantic"
    evidence_label = ",".join(scored.evidence[:4]) if scored.evidence else scored.element.name
    return ElementMatch(
        element=scored.element,
        file=file,
        confidence=scored.confidence,
        matched_pattern=f"{prefix}:{evidence_label}",
        score=scored.score,
        page_number=page_number,
        match_mode="binder",
        evidence=scored.evidence,
    )
