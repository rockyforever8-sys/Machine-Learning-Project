from __future__ import annotations

from typing import Any

from .models import ElementPriority, PpapElement
from .skill_loader import skill_element_records, skill_metadata


def _as_tuple(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, (list, tuple)):
        return tuple(str(item) for item in value)
    return ()


def _element_from_skill(record: dict[str, Any]) -> PpapElement:
    return PpapElement(
        number=int(record["number"]),
        name=str(record["name"]),
        aliases=_as_tuple(record.get("aliases")),
        filename_patterns=_as_tuple(record.get("filename_patterns")),
        priority=ElementPriority(str(record.get("priority", "medium"))),
        physical_artifact=bool(record.get("physical_artifact", False)),
        content_markers=_as_tuple(record.get("content_markers")),
        unique_markers=_as_tuple(record.get("unique_markers")),
        exclude_markers=_as_tuple(record.get("exclude_markers")),
        continuation_markers=_as_tuple(record.get("continuation_markers")),
        aiag_rule=str(record.get("aiag_rule") or ""),
    )


PPAP_LEVEL_3_ELEMENTS: tuple[PpapElement, ...] = tuple(
    _element_from_skill(record) for record in skill_element_records()
)

CRITICAL_ELEMENT_NUMBERS: frozenset[int] = frozenset(
    int(number) for number in skill_metadata()["critical_element_numbers"]
)

ELEMENT_BY_NUMBER: dict[int, PpapElement] = {
    element.number: element for element in PPAP_LEVEL_3_ELEMENTS
}
