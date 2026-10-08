from __future__ import annotations

from dataclasses import dataclass
import difflib
from pathlib import Path

from .file_access import read_file_bytes_contained, read_file_bytes_contained_bounded


@dataclass(frozen=True)
class FileReadResult:
    """Decoded file contents in the editor's internal newline shape."""

    path: str
    text: str
    fileformat: str
    encoding: str
    byte_count: int


def detect_fileformat_from_text(text: str) -> str:
    """Return a tiny line-ending guess for raw decoded file text."""

    s = str(text or "")
    i = s.find("\n")
    if i > 0 and s[i - 1] == "\r":
        return "dos"
    return "unix"


def read_file_for_editor(
    path: str | Path,
    *,
    encoding: str,
    containment_root: str | Path | None = None,
    max_bytes: int | None = None,
    timeout_seconds: float | None = None,
) -> FileReadResult:
    """Read a text file using Micromax's internal newline convention.

    ``containment_root`` is the read-side sibling of the save writer's final
    root check.  Script recovery helpers validate before calling into the editor;
    this re-resolves the concrete path near the read so a late symlink swap
    fails closed instead of exposing files outside the configured capability root.
    ``max_bytes`` lets executable source-loading paths reject oversized files
    without changing ordinary editor buffer reads.  ``timeout_seconds`` is used
    by editor command/recovery paths that need the same killable read boundary as
    script-visible ``ed.fs-read``; ``None`` preserves the historical direct read
    for callers that already run under a stronger outer timeout.
    """

    p = Path(path)
    if timeout_seconds is None:
        result = read_file_bytes_contained(p, containment_root=containment_root, max_bytes=max_bytes)
    else:
        result = read_file_bytes_contained_bounded(
            p,
            containment_root=containment_root,
            max_bytes=max_bytes,
            timeout_seconds=timeout_seconds,
        )
    raw = result.data
    decoded = raw.decode(str(encoding or "utf-8"))
    return FileReadResult(
        path=str(result.path),
        text=decoded.replace("\r\n", "\n").replace("\r", "\n"),
        fileformat=detect_fileformat_from_text(decoded),
        encoding=str(encoding or "utf-8"),
        byte_count=len(raw),
    )


def unified_file_diff_lines(
    *,
    disk_text: str,
    buffer_text: str,
    disk_label: str,
    buffer_label: str,
    max_lines: int = 80,
) -> list[str]:
    """Return a bounded unified diff between disk and buffer text."""

    lines = list(
        difflib.unified_diff(
            str(disk_text).splitlines(),
            str(buffer_text).splitlines(),
            fromfile=str(disk_label or "disk"),
            tofile=str(buffer_label or "buffer"),
            lineterm="",
        )
    )
    if not lines:
        return []
    limit = max(0, int(max_lines or 0))
    if limit and len(lines) > limit:
        hidden = len(lines) - limit
        return lines[:limit] + [f"... {hidden} more diff line{'s' if hidden != 1 else ''} omitted"]
    return lines
