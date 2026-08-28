from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .pdf_text import pdf_text_available
from .report import format_console_summary, write_all_reports
from .triage import triage_inbox
from .watcher import watch_inbox


def _add_pdf_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--pdf-text",
        action="store_true",
        help="Extract PDF text for content-based PPAP element classification.",
    )
    parser.add_argument(
        "--pdf-max-pages",
        type=int,
        default=5,
        help="Maximum PDF pages to scan for text (default: 5).",
    )


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
    triage_parser.add_argument(
        "--layout",
        choices=("auto", "discrete", "binder"),
        default="auto",
        help="Submission layout strategy: auto-detect binder vs discrete files (default: auto).",
    )
    _add_pdf_flags(triage_parser)

    watch_parser = subparsers.add_parser(
        "watch",
        help="Watch an inbox folder and re-triage when new supplier files arrive.",
    )
    watch_parser.add_argument(
        "inbox",
        type=Path,
        help="Path to the supplier submission inbox folder.",
    )
    watch_parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("triage-out"),
        help="Directory for JSON, CSV, and Markdown reports.",
    )
    watch_parser.add_argument(
        "--interval",
        type=float,
        default=2.0,
        help="Polling interval in seconds between inbox checks (default: 2).",
    )
    watch_parser.add_argument(
        "--stable-seconds",
        type=float,
        default=1.0,
        help="Wait until inbox is stable for this many seconds before triaging.",
    )
    watch_parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Only scan the top level of the inbox folder.",
    )
    watch_parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single triage pass and exit (useful for cron or CI).",
    )
    _add_pdf_flags(watch_parser)
    watch_parser.add_argument(
        "--layout",
        choices=("auto", "discrete", "binder"),
        default="auto",
        help="Submission layout strategy: auto-detect binder vs discrete files (default: auto).",
    )

    return parser


def _validate_pdf_text(use_pdf_text: bool) -> int | None:
    if use_pdf_text and not pdf_text_available():
        print(
            "Error: --pdf-text requires the pypdf package. Install with: pip install pypdf",
            file=sys.stderr,
        )
        return 1
    return None


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "triage":
        pdf_error = _validate_pdf_text(args.pdf_text)
        if pdf_error is not None:
            return pdf_error

        try:
            report = triage_inbox(
                args.inbox,
                submission_level=3,
                recursive=not args.no_recursive,
                use_pdf_text=args.pdf_text,
                pdf_max_pages=args.pdf_max_pages,
                layout_mode=args.layout,
            )
        except (FileNotFoundError, NotADirectoryError, ValueError) as error:
            print(f"Error: {error}", file=sys.stderr)
            return 1

        outputs = write_all_reports(report, args.output)
        print(format_console_summary(report))
        print("Reports written:")
        for name, path in outputs.items():
            print(f"  {name}: {path}")
        if "sqe_checklist" in outputs:
            print("SQE review: open sqe-checklist.md for binder page references")

        if args.fail_on_blocked and report.status.value == "blocked":
            return 2
        if args.fail_on_incomplete and report.summary["elements_missing"] > 0:
            return 1

    if args.command == "watch":
        pdf_error = _validate_pdf_text(args.pdf_text)
        if pdf_error is not None:
            return pdf_error

        if not args.inbox.exists():
            print(f"Error: Inbox path does not exist: {args.inbox}", file=sys.stderr)
            return 1
        if not args.inbox.is_dir():
            print(f"Error: Inbox path is not a directory: {args.inbox}", file=sys.stderr)
            return 1

        print(f"Watching {args.inbox.resolve()} (interval={args.interval}s)")
        if args.pdf_text:
            print("PDF text extraction enabled for content-based classification")
        try:
            watch_inbox(
                args.inbox,
                args.output,
                interval_seconds=args.interval,
                stable_seconds=args.stable_seconds,
                recursive=not args.no_recursive,
                use_pdf_text=args.pdf_text,
                pdf_max_pages=args.pdf_max_pages,
                layout_mode=args.layout,
                run_once=args.once,
            )
        except KeyboardInterrupt:
            print("\nStopped watching inbox.")
            return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
