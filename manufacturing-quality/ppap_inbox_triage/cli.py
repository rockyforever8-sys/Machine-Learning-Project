from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .report import format_console_summary, write_all_reports
from .triage import triage_inbox


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ppap_inbox_triage",
        description="Triage a folder of supplier PPAP Level 3 submission files.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    triage_parser = subparsers.add_parser(
        "triage",
        help="Scan an inbox folder and generate PPAP Level 3 triage reports.",
    )
    triage_parser.add_argument(
        "inbox",
        type=Path,
        help="Path to the supplier submission inbox folder.",
    )
    triage_parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("triage-out"),
        help="Directory for JSON, CSV, and Markdown reports.",
    )
    triage_parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Only scan the top level of the inbox folder.",
    )
    triage_parser.add_argument(
        "--fail-on-blocked",
        action="store_true",
        help="Exit with code 2 when critical PPAP elements are missing.",
    )
    triage_parser.add_argument(
        "--fail-on-incomplete",
        action="store_true",
        help="Exit with code 1 when any PPAP elements are missing.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "triage":
        try:
            report = triage_inbox(
                args.inbox,
                submission_level=3,
                recursive=not args.no_recursive,
            )
        except (FileNotFoundError, NotADirectoryError, ValueError) as error:
            print(f"Error: {error}", file=sys.stderr)
            return 1

        outputs = write_all_reports(report, args.output)
        print(format_console_summary(report))
        print("Reports written:")
        for name, path in outputs.items():
            print(f"  {name}: {path}")

        if args.fail_on_blocked and report.status.value == "blocked":
            return 2
        if args.fail_on_incomplete and report.summary["elements_missing"] > 0:
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
