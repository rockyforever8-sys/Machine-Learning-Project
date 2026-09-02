from __future__ import annotations

from pathlib import Path

from .models import ElementMatch, ElementTriage, TriageReport
from .skill_loader import sqe_checks_by_element

SQE_VERIFICATION_CHECKS: dict[int, tuple[str, ...]] = sqe_checks_by_element()


def collect_page_numbers(matches: list[ElementMatch]) -> list[int]:
    return sorted({match.page_number for match in matches if match.page_number is not None})


def compact_page_range(pages: list[int]) -> str:
    if not pages:
        return "—"
    ordered = sorted(set(pages))
    ranges: list[tuple[int, int]] = []
    start = previous = ordered[0]
    for page in ordered[1:]:
        if page == previous + 1:
            previous = page
            continue
        ranges.append((start, previous))
        start = previous = page
    ranges.append((start, previous))
    parts = [
        str(low) if low == high else f"{low}-{high}"
        for low, high in ranges
    ]
    return ", ".join(parts)


def format_page_numbers(matches: list[ElementMatch]) -> str:
    return compact_page_range(collect_page_numbers(matches))


def build_binder_page_index(report: TriageReport) -> list[tuple[int, list[int]]]:
    page_to_elements: dict[int, list[int]] = {}
    for triage in report.elements:
        if triage.status not in {"present", "review"}:
            continue
        for page in collect_page_numbers(triage.matches):
            page_to_elements.setdefault(page, []).append(triage.element.number)

    return sorted(page_to_elements.items(), key=lambda item: item[0])


def _primary_file(triage: ElementTriage) -> str:
    if not triage.matches:
        return "—"
    return triage.matches[0].file.relative_path


def write_sqe_checklist_report(report: TriageReport, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    binder_files = report.summary.get("binder_files", [])
    binder_label = binder_files[0] if binder_files else "—"

    lines: list[str] = [
        "# SQE PPAP Level 3 Review Checklist",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Inbox | `{report.inbox_path}` |",
        f"| Scanned | {report.scanned_at} |",
        f"| Triage status | `{report.status.value}` |",
        f"| Completeness | {report.summary['completeness_pct']}% "
        f"({report.summary['elements_present']}/18) |",
        f"| Submission layout | `{report.summary.get('submission_layout', 'discrete')}` |",
        f"| Binder file | `{binder_label}` |",
        "| Part / Program | |",
        "| Supplier | |",
        "| Reviewer | |",
        "| Review date | |",
        "",
        "## Review decision",
        "",
        "- [ ] Approve",
        "- [ ] Approve with conditions",
        "- [ ] Reject",
        "",
        "**Conditions / notes:**",
        "",
        "---",
        "",
    ]

    if report.summary.get("submission_layout") == "binder":
        page_index = build_binder_page_index(report)
        if page_index:
            lines.extend(
                [
                    "## Binder page index (auto-detected)",
                    "",
                    "| Page | Element(s) |",
                    "|---:|---|",
                ]
            )
            for page, element_numbers in page_index:
                labels = ", ".join(f"#{number}" for number in element_numbers)
                lines.append(f"| {page} | {labels} |")
            lines.extend(["", "---", ""])

    lines.append("## Element verification")
    lines.append("")

    for triage in report.elements:
        pages = format_page_numbers(triage.matches)
        checks = SQE_VERIFICATION_CHECKS.get(triage.element.number, ("Verify element content",))
        lines.extend(
            [
                f"### {triage.element.number}. {triage.element.name} — {triage.status.upper()}",
                "",
                f"- **Source file:** `{_primary_file(triage)}`",
                f"- **Binder pages:** {pages}",
                f"- **Priority:** {triage.element.priority.value}",
            ]
        )
        if triage.notes:
            lines.append(f"- **Triage notes:** {'; '.join(triage.notes)}")
        lines.append("- **SQE checks:**")
        for check in checks:
            lines.append(f"  - [ ] {check}")
        lines.extend(["- **SQE notes:**", "", "---", ""])

    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return output_path
