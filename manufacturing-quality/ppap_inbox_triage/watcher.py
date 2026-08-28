from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

from .report import format_console_summary, write_all_reports
from .scanner import scan_inbox
from .triage import triage_inbox


@dataclass
class InboxSnapshot:
    file_count: int
    total_size_bytes: int
    latest_mtime_ns: int


def snapshot_inbox(inbox_path: Path, *, recursive: bool = True) -> InboxSnapshot:
    files = scan_inbox(inbox_path, recursive=recursive)
    if not files:
        return InboxSnapshot(file_count=0, total_size_bytes=0, latest_mtime_ns=0)

    total_size = sum(file.size_bytes for file in files)
    latest_mtime = max(file.path.stat().st_mtime_ns for file in files)
    return InboxSnapshot(
        file_count=len(files),
        total_size_bytes=total_size,
        latest_mtime_ns=latest_mtime,
    )


def wait_for_stable_inbox(
    inbox_path: Path,
    *,
    recursive: bool = True,
    stable_seconds: float = 1.0,
    poll_seconds: float = 0.25,
    timeout_seconds: float = 30.0,
) -> InboxSnapshot:
    deadline = time.monotonic() + timeout_seconds
    previous = snapshot_inbox(inbox_path, recursive=recursive)
    stable_since = time.monotonic()

    while time.monotonic() < deadline:
        time.sleep(poll_seconds)
        current = snapshot_inbox(inbox_path, recursive=recursive)
        if (
            current.file_count == previous.file_count
            and current.total_size_bytes == previous.total_size_bytes
            and current.latest_mtime_ns == previous.latest_mtime_ns
        ):
            if time.monotonic() - stable_since >= stable_seconds:
                return current
        else:
            previous = current
            stable_since = time.monotonic()

    return previous


def watch_inbox(
    inbox_path: Path,
    output_dir: Path,
    *,
    interval_seconds: float = 2.0,
    stable_seconds: float = 1.0,
    recursive: bool = True,
    use_pdf_text: bool = False,
    pdf_max_pages: int = 5,
    run_once: bool = False,
) -> None:
    last_signature: tuple[int, int, int] | None = None

    while True:
        snapshot = wait_for_stable_inbox(
            inbox_path,
            recursive=recursive,
            stable_seconds=stable_seconds,
            timeout_seconds=max(stable_seconds, interval_seconds),
        )
        signature = (
            snapshot.file_count,
            snapshot.total_size_bytes,
            snapshot.latest_mtime_ns,
        )

        if signature != last_signature:
            report = triage_inbox(
                inbox_path,
                recursive=recursive,
                use_pdf_text=use_pdf_text,
                pdf_max_pages=pdf_max_pages,
            )
            outputs = write_all_reports(report, output_dir)
            timestamp = report.scanned_at.replace("T", " ").split("+")[0]
            print(f"\n[{timestamp} UTC] Inbox change detected")
            print(format_console_summary(report))
            print("Reports written:")
            for name, path in outputs.items():
                print(f"  {name}: {path}")
            last_signature = signature

        if run_once:
            return

        time.sleep(interval_seconds)
