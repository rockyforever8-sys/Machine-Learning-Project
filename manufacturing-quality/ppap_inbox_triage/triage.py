from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .classifier import classify_binder_pdf, classify_file, content_element_hits
from .elements import CRITICAL_ELEMENT_NUMBERS, PPAP_LEVEL_3_ELEMENTS
from .layout import (
    count_discrete_files,
    detect_submission_layout,
    identify_binder_candidates,
)
from .models import (
    ElementMatch,
    ElementTriage,
    InboxFile,
    MatchConfidence,
    OrphanFile,
    SubmissionLayout,
    TriageReport,
    TriageStatus,
)
from .pdf_text import ALL_PAGES, extract_pdf_pages, extract_pdf_text
from .scanner import scan_inbox


def _element_status(
    matches: list[ElementMatch],
    *,
    binder_files: set[str],
) -> str:
    if not matches:
        return "missing"

    strong_matches = [
        match for match in matches if match.confidence != MatchConfidence.LOW
    ]
    if not strong_matches:
        if len(matches) == 1:
            return "review"
        return "duplicate"

    source_files = {match.file.relative_path for match in strong_matches}
    non_binder_files = {path for path in source_files if path not in binder_files}
    if len(non_binder_files) > 1:
        return "duplicate"

    return "present"


def _build_actions(
    element_triages: list[ElementTriage],
    orphans: list[OrphanFile],
    missing_critical: list[int],
    *,
    submission_layout: SubmissionLayout,
    binder_files: set[str],
) -> list[str]:
    actions: list[str] = []

    if submission_layout == SubmissionLayout.BINDER:
        if binder_files:
            binder_name = next(iter(binder_files))
            actions.append(
                "Detected PPAP binder submission — verify section coverage inside "
                f"`{binder_name}` against all 18 elements"
            )
    elif submission_layout == SubmissionLayout.MIXED:
        actions.append(
            "Detected mixed submission (binder plus discrete files) — verify binder "
            "sections and standalone files do not conflict"
        )
    else:
        actions.append(
            "Detected discrete file submission — each PPAP element should map to its own file"
        )

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
                f"({triage.element.name}) — low-confidence match"
            )
        elif triage.status == "missing" and triage.element.physical_artifact:
            actions.append(
                f"Confirm physical artifact for element {triage.element.number} "
                f"({triage.element.name}) — documentation not detected in inbox"
            )

    for orphan in orphans[:10]:
        actions.append(f"Classify orphan file: {orphan.file.relative_path} ({orphan.reason})")

    if not any("Request missing" in action for action in actions) and not orphans:
        if submission_layout == SubmissionLayout.BINDER:
            actions.append(
                "Binder elements detected — assign SQE for formal PPAP section-by-section review"
            )
        elif len([triage for triage in element_triages if triage.status == "present"]) == 18:
            actions.append("All Level 3 elements detected — assign SQE for formal PPAP review")

    return actions


def _classify_inbox_file(
    inbox_file: InboxFile,
    *,
    use_pdf_text: bool,
    pdf_max_pages: int,
    binder_mode: bool,
) -> list[ElementMatch]:
    if binder_mode and inbox_file.suffix.lower() == ".pdf":
        page_texts = extract_pdf_pages(inbox_file.path, max_pages=ALL_PAGES)
        return classify_binder_pdf(inbox_file, page_texts)

    text_content = None
    if use_pdf_text and inbox_file.suffix.lower() == ".pdf":
        text_content = extract_pdf_text(inbox_file.path, max_pages=pdf_max_pages)
    return classify_file(inbox_file, text_content=text_content)


def _assign_discrete_file(
    inbox_file: InboxFile,
    file_matches: list[ElementMatch],
    matches_by_element: dict[int, list[ElementMatch]],
    assigned_files: set[str],
) -> None:
    if not file_matches:
        return

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


def _assign_binder_file(
    file_matches: list[ElementMatch],
    matches_by_element: dict[int, list[ElementMatch]],
    assigned_files: set[str],
    inbox_file: InboxFile,
) -> None:
    assigned = False
    for match in file_matches:
        if match.confidence == MatchConfidence.LOW:
            continue
        matches_by_element[match.element.number].append(match)
        assigned = True

    if assigned:
        assigned_files.add(inbox_file.relative_path)


def triage_inbox(
    inbox_path: Path,
    *,
    submission_level: int = 3,
    recursive: bool = True,
    use_pdf_text: bool = False,
    pdf_max_pages: int = 5,
    layout_mode: str = "auto",
) -> TriageReport:
    if submission_level != 3:
        raise ValueError("Only PPAP Level 3 triage is supported in this release")

    if layout_mode not in {"auto", "discrete", "binder"}:
        raise ValueError("layout_mode must be one of: auto, discrete, binder")

    scanned_at = datetime.now(timezone.utc).isoformat()
    inbox_files = scan_inbox(inbox_path, recursive=recursive)

    probe_cache: dict[str, list[ElementMatch]] = {}
    element_hits_by_file: dict[str, set[int]] = {}
    for inbox_file in inbox_files:
        probe_matches = _classify_inbox_file(
            inbox_file,
            use_pdf_text=use_pdf_text,
            pdf_max_pages=pdf_max_pages,
            binder_mode=False,
        )
        probe_cache[inbox_file.relative_path] = probe_matches
        element_hits_by_file[inbox_file.relative_path] = content_element_hits(probe_matches)

    if layout_mode == "binder":
        binder_files = {file.relative_path for file in inbox_files if file.suffix.lower() == ".pdf"}
        submission_layout = SubmissionLayout.BINDER if binder_files else SubmissionLayout.DISCRETE
    elif layout_mode == "discrete":
        binder_files = set()
        submission_layout = SubmissionLayout.DISCRETE
    else:
        binder_files = identify_binder_candidates(inbox_files, element_hits_by_file)
        discrete_file_count = count_discrete_files(inbox_files, binder_files)
        submission_layout = detect_submission_layout(
            inbox_files,
            binder_candidates=binder_files,
            discrete_file_count=discrete_file_count,
        )

    file_matches_cache: dict[str, list[ElementMatch]] = {}
    for inbox_file in inbox_files:
        is_binder = inbox_file.relative_path in binder_files
        file_matches_cache[inbox_file.relative_path] = _classify_inbox_file(
            inbox_file,
            use_pdf_text=use_pdf_text,
            pdf_max_pages=pdf_max_pages,
            binder_mode=is_binder,
        )

    matches_by_element: dict[int, list[ElementMatch]] = defaultdict(list)
    assigned_files: set[str] = set()

    for inbox_file in inbox_files:
        file_matches = file_matches_cache[inbox_file.relative_path]
        if inbox_file.relative_path in binder_files:
            _assign_binder_file(
                file_matches,
                matches_by_element,
                assigned_files,
                inbox_file,
            )
        else:
            _assign_discrete_file(
                inbox_file,
                file_matches,
                matches_by_element,
                assigned_files,
            )

    element_triages: list[ElementTriage] = []
    missing_elements: list[int] = []
    missing_critical: list[int] = []
    duplicate_count = 0
    review_count = 0
    content_classified_count = 0
    binder_element_count = 0

    for element in PPAP_LEVEL_3_ELEMENTS:
        matches = matches_by_element.get(element.number, [])
        status = _element_status(matches, binder_files=binder_files)
        notes: list[str] = []

        if status == "missing":
            missing_elements.append(element.number)
            if element.number in CRITICAL_ELEMENT_NUMBERS:
                missing_critical.append(element.number)
            if element.physical_artifact:
                notes.append("Physical artifact may be required even without a file")
        elif status == "duplicate":
            duplicate_count += 1
            notes.append("Multiple discrete files map to this element")
        elif status == "review":
            review_count += 1
            notes.append("Match confidence is low")

        binder_matches = [match for match in matches if match.match_mode == "binder"]
        content_matches = [match for match in matches if match.match_mode == "content"]
        if binder_matches:
            pages = sorted(
                {match.page_number for match in binder_matches if match.page_number is not None}
            )
            if pages:
                notes.append(f"Detected in PPAP binder pages: {', '.join(str(page) for page in pages)}")
            else:
                notes.append("Detected in PPAP binder")
            binder_element_count += 1
        elif content_matches:
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
        "binder_classified_elements": binder_element_count,
        "submission_layout": submission_layout.value,
        "binder_files": sorted(binder_files),
    }

    actions = _build_actions(
        element_triages,
        orphans,
        missing_critical,
        submission_layout=submission_layout,
        binder_files=binder_files,
    )

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
