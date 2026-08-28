from __future__ import annotations

import csv
import json
from pathlib import Path

from .models import TriageReport, TriageStatus


def _status_emoji(status: str) -> str:
    mapping = {
        "present": "OK",
        "missing": "MISSING",
        "duplicate": "DUPLICATE",
        "review": "REVIEW",
    }
    return mapping.get(status, status.upper())


def report_to_dict(report: TriageReport) -> dict:
    return {
        "inbox_path": str(report.inbox_path),
        "submission_level": report.submission_level,
        "scanned_at": report.scanned_at,
        "status": report.status.value,
        "summary": report.summary,
        "actions": report.actions,
        "elements": [
            {
                "number": triage.element.number,
                "name": triage.element.name,
                "priority": triage.element.priority.value,
                "status": triage.status,
                "notes": triage.notes,
                "matches": [
                    {
                        "file": match.file.relative_path,
                        "confidence": match.confidence.value,
                        "matched_pattern": match.matched_pattern,
                        "score": match.score,
                    }
                    for match in triage.matches
                ],
            }
            for triage in report.elements
        ],
        "orphans": [
            {
                "file": orphan.file.relative_path,
                "reason": orphan.reason,
            }
            for orphan in report.orphans
        ],
    }


def write_json_report(report: TriageReport, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report_to_dict(report), indent=2), encoding="utf-8")
    return output_path


def write_csv_report(report: TriageReport, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "element_number",
                "element_name",
                "priority",
                "status",
                "primary_file",
                "confidence",
                "notes",
            ]
        )
        for triage in report.elements:
            primary = triage.matches[0] if triage.matches else None
            writer.writerow(
                [
                    triage.element.number,
                    triage.element.name,
                    triage.element.priority.value,
                    triage.status,
                    primary.file.relative_path if primary else "",
                    primary.confidence.value if primary else "",
                    "; ".join(triage.notes),
                ]
            )
    return output_path


def write_markdown_report(report: TriageReport, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = [
        "# PPAP Level 3 Inbox Triage Report",
        "",
        f"- **Inbox:** `{report.inbox_path}`",
        f"- **Scanned:** {report.scanned_at}",
        f"- **Status:** `{report.status.value}`",
        f"- **Completeness:** {report.summary['completeness_pct']}% "
        f"({report.summary['elements_present']}/18 elements)",
        "",
        "## Summary",
        "",
        f"- Files scanned: {report.summary['files_scanned']}",
        f"- Missing elements: {report.summary['elements_missing']}",
        f"- Duplicate mappings: {report.summary['elements_duplicate']}",
        f"- Low-confidence matches: {report.summary['elements_review']}",
        f"- Orphan files: {report.summary['orphan_files']}",
        "",
        "## Recommended Actions",
        "",
    ]

    for index, action in enumerate(report.actions, start=1):
        lines.append(f"{index}. {action}")

    lines.extend(["", "## Element Checklist", "", "| # | Element | Status | File |", "|---:|---|---|---|"])

    for triage in report.elements:
        primary = triage.matches[0].file.relative_path if triage.matches else "—"
        lines.append(
            f"| {triage.element.number} | {triage.element.name} | "
            f"{_status_emoji(triage.status)} | `{primary}` |"
        )

    if report.orphans:
        lines.extend(["", "## Orphan Files", ""])
        for orphan in report.orphans:
            lines.append(f"- `{orphan.file.relative_path}` — {orphan.reason}")

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path


def write_all_reports(report: TriageReport, output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    return {
        "json": write_json_report(report, output_dir / "triage-report.json"),
        "csv": write_csv_report(report, output_dir / "triage-elements.csv"),
        "markdown": write_markdown_report(report, output_dir / "triage-report.md"),
    }


def format_console_summary(report: TriageReport) -> str:
    status_prefix = {
        TriageStatus.READY_FOR_REVIEW: "READY",
        TriageStatus.INCOMPLETE: "INCOMPLETE",
        TriageStatus.NEEDS_CLARIFICATION: "CLARIFY",
        TriageStatus.BLOCKED: "BLOCKED",
    }[report.status]

    lines = [
        f"[{status_prefix}] PPAP Level 3 inbox triage — {report.summary['completeness_pct']}% complete",
        f"Files: {report.summary['files_scanned']} | Missing: {report.summary['elements_missing']} | "
        f"Duplicates: {report.summary['elements_duplicate']} | Orphans: {report.summary['orphan_files']}",
    ]

    if report.summary["missing_element_numbers"]:
        lines.append(
            "Missing elements: "
            + ", ".join(str(number) for number in report.summary["missing_element_numbers"])
        )

    if report.actions:
        lines.append("Next action: " + report.actions[0])

    return "\n".join(lines)
