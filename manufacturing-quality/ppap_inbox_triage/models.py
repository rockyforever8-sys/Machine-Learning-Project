from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class TriageStatus(str, Enum):
    READY_FOR_REVIEW = "ready_for_review"
    INCOMPLETE = "incomplete"
    NEEDS_CLARIFICATION = "needs_clarification"
    BLOCKED = "blocked"


class MatchConfidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ElementPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SubmissionLayout(str, Enum):
    DISCRETE = "discrete"
    BINDER = "binder"
    MIXED = "mixed"


@dataclass(frozen=True)
class PpapElement:
    number: int
    name: str
    aliases: tuple[str, ...]
    filename_patterns: tuple[str, ...]
    priority: ElementPriority
    physical_artifact: bool = False
    content_markers: tuple[str, ...] = ()
    unique_markers: tuple[str, ...] = ()
    exclude_markers: tuple[str, ...] = ()
    continuation_markers: tuple[str, ...] = ()
    aiag_rule: str = ""


@dataclass
class InboxFile:
    path: Path
    relative_path: str
    name: str
    suffix: str
    size_bytes: int


@dataclass
class ElementMatch:
    element: PpapElement
    file: InboxFile
    confidence: MatchConfidence
    matched_pattern: str
    score: float
    page_number: int | None = None
    match_mode: str = "filename"
    evidence: tuple[str, ...] = ()

    def __getattr__(self, name: str) -> object:
        if name == "evidence":
            return ()
        raise AttributeError(f"{type(self).__name__!r} object has no attribute {name!r}")


def match_evidence(match: object) -> tuple[str, ...]:
    """Read AIAG evidence from a match, including older ElementMatch objects."""
    raw = getattr(match, "evidence", ())
    if not raw:
        return ()
    return tuple(raw)


@dataclass
class ElementTriage:
    element: PpapElement
    status: str
    matches: list[ElementMatch] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass
class OrphanFile:
    file: InboxFile
    reason: str


@dataclass
class TriageReport:
    inbox_path: Path
    submission_level: int
    scanned_at: str
    status: TriageStatus
    elements: list[ElementTriage]
    orphans: list[OrphanFile]
    summary: dict[str, Any]
    actions: list[str]
