from __future__ import annotations

import re

from .elements import PPAP_LEVEL_3_ELEMENTS
from .models import ElementMatch, InboxFile, MatchConfidence, PpapElement

DESIGN_RECORD_EXCLUSIONS = ("fixture", "checking aid", "template", "gage", "gauge")


def _normalize(text: str) -> str:
    lowered = text.lower()
    return re.sub(r"[_\-.]+", " ", lowered)


def _ppap_prefix_number(filename: str) -> int | None:
    match = re.match(r"^(\d{1,2})[_\-.]", filename)
    if not match:
        return None
    number = int(match.group(1))
    if 1 <= number <= 18:
        return number
    return None


def _score_match(element: PpapElement, normalized_name: str, pattern: str) -> float:
    if element.number == 1 and pattern == r"\bdrawing\b":
        if any(term in normalized_name for term in DESIGN_RECORD_EXCLUSIONS):
            return 0.0

    if not re.search(pattern, normalized_name):
        return 0.0
    if any(alias in normalized_name for alias in element.aliases):
        return 1.0
    return 0.85


def classify_file(file: InboxFile) -> list[ElementMatch]:
    normalized_name = _normalize(file.name)
    prefix_number = _ppap_prefix_number(file.name)
    matches: list[ElementMatch] = []

    for element in PPAP_LEVEL_3_ELEMENTS:
        best_score = 0.0
        best_pattern = ""

        for pattern in element.filename_patterns:
            score = _score_match(element, normalized_name, pattern)
            if score > best_score:
                best_score = score
                best_pattern = pattern

        for alias in element.aliases:
            if alias in normalized_name and best_score < 0.8:
                best_score = 0.8
                best_pattern = f"alias:{alias}"

        if prefix_number == element.number and best_score > 0:
            best_score = max(best_score, 1.25)
            best_pattern = f"prefix:{prefix_number}"
        elif prefix_number is not None and prefix_number != element.number and best_score < 1.0:
            best_score *= 0.5

        if best_score >= 0.8:
            confidence = MatchConfidence.HIGH
        elif best_score >= 0.6:
            confidence = MatchConfidence.MEDIUM
        elif best_score > 0:
            confidence = MatchConfidence.LOW
        else:
            continue

        matches.append(
            ElementMatch(
                element=element,
                file=file,
                confidence=confidence,
                matched_pattern=best_pattern,
                score=best_score,
            )
        )

    matches.sort(key=lambda match: (-match.score, match.element.number))
    return matches
