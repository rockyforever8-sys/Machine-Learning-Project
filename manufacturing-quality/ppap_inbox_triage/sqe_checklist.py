from __future__ import annotations

from pathlib import Path

from .models import ElementMatch, ElementTriage, TriageReport

SQE_VERIFICATION_CHECKS: dict[int, tuple[str, ...]] = {
    1: (
        "Drawing revision matches part number and submission date",
        "Specifications are current, legible, and customer-approved",
    ),
    2: (
        "ECN/ECO included or documented as not applicable",
        "Change level matches production intent",
    ),
    3: (
        "Customer engineering approval or deviation permit is signed",
        "Approval covers this part number and revision",
    ),
    4: (
        "DFMEA is complete with team signature and date",
        "High RPN items have documented actions",
    ),
    5: (
        "Process flow matches actual manufacturing routing",
        "Flow links to PFMEA and Control Plan",
    ),
    6: (
        "PFMEA is current revision with production controls identified",
        "Special characteristics are called out",
    ),
    7: (
        "Control Plan matches PFMEA and current production process",
        "Reaction plans and sampling frequency are defined",
    ),
    8: (
        "MSA/Gage R&R results meet customer acceptance criteria",
        "Studies cover gauges used for SC characteristics",
    ),
    9: (
        "Dimensional results cover all drawing requirements",
        "FAI/layout inspection is complete and signed",
    ),
    10: (
        "Material and performance test results meet spec",
        "Test reports are from acceptable date range",
    ),
    11: (
        "Initial process capability studies meet Cpk/Ppk requirement",
        "SPC method and subgroup size are appropriate",
    ),
    12: (
        "Laboratory accreditation is valid and in scope",
        "Test methods are covered by accreditation",
    ),
    13: (
        "Appearance approval is signed if required for this part",
        "Color/master references are identified",
    ),
    14: (
        "Sample production parts are available for inspection",
        "Sample tags/packing list match submission quantity",
    ),
    15: (
        "Master sample agreement is documented if required",
        "Storage and control method is defined",
    ),
    16: (
        "Checking aids/fixtures are identified and controlled",
        "Calibration or verification records are available",
    ),
    17: (
        "Customer-specific requirements checklist is complete",
        "OEM addenda are addressed with evidence",
    ),
    18: (
        "PSW is signed with correct submission level and part data",
        "PSW matches all supporting documentation",
    ),
}


def collect_page_numbers(matches: list[ElementMatch]) -> list[int]:
    return sorted({match.page_number for match in matches if match.page_number is not None})


def format_page_numbers(matches: list[ElementMatch]) -> str:
    pages = collect_page_numbers(matches)
    if not pages:
        return "—"
    return ", ".join(str(page) for page in pages)


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
