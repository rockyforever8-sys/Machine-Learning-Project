from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .classifier import classify_file
from .elements import CRITICAL_ELEMENT_NUMBERS, PPAP_LEVEL_3_ELEMENTS
from .models import (
    ElementMatch,
    ElementTriage,
    InboxFile,
    MatchConfidence,
    OrphanFile,
    TriageReport,
    TriageStatus,
)
from .pdf_text import extract_pdf_text
from .scanner import scan_inbox


def _element_status(matches: list[ElementMatch]) -> str:
    if not matches:
        return "missing"
    high_or_medium = [
        match for match in matches if match.confidence != MatchConfidence.LOW
    ]
    if len(high_or_medium) > 1:
        return "duplicate"
    if high_or_medium:
        return "present"
    if len(matches) == 1:
        return "review"
    return "duplicate"


def _build_actions(
    element_triages: list[ElementTriage],
    orphans: list[OrphanFile],
    missing_critical: list[int],
) -> list[str]:
    actions: list[str] = []

    if missing_critical:
        critical_names = [
            next(element.name for element in PPAP_LEVEL_3_ELEMENTS if element.number == number)
            for number in sorted(missing_critical)
        ]
        actions.append(
            "Request missing critical elements from supplier: "
            + ", ".join(critical_names)
        )

    for triage in element_triages:
        if triage.status == "duplicate":
            names = ", ".join(match.file.relative_path for match in triage.matches[:3])
            actions.append(
                f"Resolve duplicate submissions for element {triage.element.number} "
                f"({triage.element.name}): {names}"
            )
        elif triage.status == "review":
            actions.append(
                f"Manually verify element {triage.element.number} "
                f"({triage.element.name}) — low-confidence filename match"
            )
        elif triage.status == "missing" and triage.element.physical_artifact:
            actions.append(
                f"Confirm physical artifact for element {triage.element.number} "
                f"({triage.element.name}) — documentation not detected in inbox"
            )

    for orphan in orphans[:10]:
        actions.append(f"Classify orphan file: {orphan.file.relative_path} ({orphan.reason})")

    if not actions:
        actions.append("All Level 3 elements detected — assign SQE for formal PPAP review")

    return actions


def _classify_inbox_file(
    inbox_file: InboxFile,
    *,
    use_pdf_text: bool,
    pdf_max_pages: int,
) -> list[ElementMatch]:
    text_content = None
    if use_pdf_text and inbox_file.suffix == ".pdf":
        text_content = extract_pdf_text(inbox_file.path, max_pages=pdf_max_pages)
    return classify_file(inbox_file, text_content=text_content)


def triage_inbox(
    inbox_path: Path,
    *,
    submission_level: int = 3,
    recursive: bool = True,
    use_pdf_text: bool = False,
    pdf_max_pages: int = 5,
) -> TriageReport:
    if submission_level != 3:
        raise ValueError("Only PPAP Level 3 triage is supported in this release")

    scanned_at = datetime.now(timezone.utc).isoformat()
    inbox_files = scan_inbox(inbox_path, recursive=recursive)

    file_matches_cache: dict[str, list[ElementMatch]] = {}
    for inbox_file in inbox_files:
        file_matches_cache[inbox_file.relative_path] = _classify_inbox_file(
            inbox_file,
            use_pdf_text=use_pdf_text,
            pdf_max_pages=pdf_max_pages,
        )

    matches_by_element: dict[int, list[ElementMatch]] = defaultdict(list)
    assigned_files: set[str] = set()

    for inbox_file in inbox_files:
        file_matches = file_matches_cache[inbox_file.relative_path]
        if not file_matches:
            continue

        top_match = file_matches[0]
        if top_match.confidence == MatchConfidence.LOW and len(file_matches) > 1:
            for match in file_matches:
                if match.confidence != MatchConfidence.LOW:
                    top_match = match
                    break

        matches_by_element[top_match.element.number].append(top_match)

        if top_match.confidence != MatchConfidence.LOW:
            assigned_files.add(inbox_file.relative_path)
        else:
            for match in file_matches:
                if match.element.number != top_match.element.number:
                    matches_by_element[match.element.number].append(match)

    element_triages: list[ElementTriage] = []
    missing_elements: list[int] = []
    missing_critical: list[int] = []
    duplicate_count = 0
    review_count = 0
    content_classified_count = 0

    for element in PPAP_LEVEL_3_ELEMENTS:
        matches = matches_by_element.get(element.number, [])
        status = _element_status(matches)
        notes: list[str] = []

        if status == "missing":
            missing_elements.append(element.number)
            if element.number in CRITICAL_ELEMENT_NUMBERS:
                missing_critical.append(element.number)
            if element.physical_artifact:
                notes.append("Physical artifact may be required even without a file")
        elif status == "duplicate":
            duplicate_count += 1
            notes.append("Multiple files map to this element")
        elif status == "review":
            review_count += 1
            notes.append("Filename match confidence is low")

        if any(match.matched_pattern.startswith("content:") for match in matches):
            notes.append("Classified using PDF text content")
            content_classified_count += 1

        element_triages.append(
            ElementTriage(
                element=element,
                status=status,
                matches=sorted(
                    matches,
                    key=lambda match: (-match.score, match.file.relative_path),
                ),
                notes=notes,
            )
        )

    orphans: list[OrphanFile] = []
    for inbox_file in inbox_files:
        if inbox_file.relative_path in assigned_files:
            continue
        file_matches = file_matches_cache[inbox_file.relative_path]
        if file_matches:
            orphans.append(
                OrphanFile(
                    file=inbox_file,
                    reason="Low-confidence or secondary match — not assigned to primary element",
                )
            )
        else:
            orphans.append(
                OrphanFile(
                    file=inbox_file,
                    reason="No PPAP element pattern matched in filename or PDF text",
                )
            )

    present_count = sum(1 for triage in element_triages if triage.status == "present")

    if missing_critical:
        status = TriageStatus.BLOCKED
    elif not missing_elements and duplicate_count == 0 and review_count == 0 and not orphans:
        status = TriageStatus.READY_FOR_REVIEW
    elif missing_elements and duplicate_count == 0 and review_count == 0 and not orphans:
        status = TriageStatus.INCOMPLETE
    else:
        status = TriageStatus.NEEDS_CLARIFICATION

    summary: dict[str, Any] = {
        "files_scanned": len(inbox_files),
        "elements_present": present_count,
        "elements_missing": len(missing_elements),
        "elements_duplicate": duplicate_count,
        "elements_review": review_count,
        "orphan_files": len(orphans),
        "missing_element_numbers": missing_elements,
        "missing_critical_numbers": missing_critical,
        "completeness_pct": round((present_count / len(PPAP_LEVEL_3_ELEMENTS)) * 100, 1),
        "pdf_text_enabled": use_pdf_text,
        "content_classified_elements": content_classified_count,
    }

    actions = _build_actions(element_triages, orphans, missing_critical)

    return TriageReport(
        inbox_path=inbox_path.resolve(),
        submission_level=submission_level,
        scanned_at=scanned_at,
        status=status,
        elements=element_triages,
        orphans=orphans,
        summary=summary,
        actions=actions,
    )
