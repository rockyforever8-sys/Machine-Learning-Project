from __future__ import annotations

from pathlib import Path

from .models import InboxFile, SubmissionPackage

IGNORED_NAMES = {".ds_store", "thumbs.db", "desktop.ini"}
IGNORED_SUFFIXES = {".tmp", ".partial", ".download"}
IGNORED_DIR_NAMES = {
    ".git",
    ".cursor",
    "__pycache__",
    "node_modules",
    "triage-out",
    "triage_out",
}


def scan_inbox(inbox_path: Path, *, recursive: bool = True) -> list[InboxFile]:
    if not inbox_path.exists():
        raise FileNotFoundError(f"Inbox path does not exist: {inbox_path}")
    if not inbox_path.is_dir():
        raise NotADirectoryError(f"Inbox path is not a directory: {inbox_path}")

    files: list[InboxFile] = []
    iterator = inbox_path.rglob("*") if recursive else inbox_path.glob("*")

    for path in sorted(iterator):
        if not path.is_file():
            continue
        if path.name.startswith("."):
            continue
        if path.name.lower() in IGNORED_NAMES:
            continue
        if path.suffix.lower() in IGNORED_SUFFIXES:
            continue

        stat = path.stat()
        files.append(
            InboxFile(
                path=path,
                relative_path=str(path.relative_to(inbox_path)),
                name=path.name,
                suffix=path.suffix.lower(),
                size_bytes=stat.st_size,
            )
        )

    return files


def discover_submission_packages(inbox_path: Path) -> list[SubmissionPackage]:
    """Treat each immediate inbox subfolder as its own PPAP Level 3 submission.

    A flat inbox with no child folders stays a single package. Loose files sitting
    next to those folders become an extra root-files package so they are not mixed
    into a supplier folder review.
    """
    if not inbox_path.exists():
        raise FileNotFoundError(f"Inbox path does not exist: {inbox_path}")
    if not inbox_path.is_dir():
        raise NotADirectoryError(f"Inbox path is not a directory: {inbox_path}")

    inbox_path = inbox_path.resolve()
    child_packages: list[SubmissionPackage] = []
    try:
        entries = sorted(inbox_path.iterdir(), key=lambda item: item.name.lower())
    except OSError:
        entries = []

    for child in entries:
        if not child.is_dir():
            continue
        if child.name.startswith("."):
            continue
        if child.name.lower() in IGNORED_DIR_NAMES:
            continue
        try:
            child_files = scan_inbox(child, recursive=True)
        except (FileNotFoundError, NotADirectoryError, OSError):
            continue
        if child_files:
            child_packages.append(
                SubmissionPackage(name=child.name, path=child, recursive=True, kind="folder")
            )

    root_files = scan_inbox(inbox_path, recursive=False)
    if not child_packages:
        return [
            SubmissionPackage(name=inbox_path.name, path=inbox_path, recursive=True, kind="inbox")
        ]

    packages = list(child_packages)
    if root_files:
        packages.append(
            SubmissionPackage(
                name=f"{inbox_path.name} (root files)",
                path=inbox_path,
                recursive=False,
                kind="inbox_root",
            )
        )
    return packages
