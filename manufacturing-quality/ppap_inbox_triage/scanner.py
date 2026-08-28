from __future__ import annotations

from pathlib import Path

from .models import InboxFile

IGNORED_NAMES = {".ds_store", "thumbs.db", "desktop.ini"}
IGNORED_SUFFIXES = {".tmp", ".partial", ".download"}


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
