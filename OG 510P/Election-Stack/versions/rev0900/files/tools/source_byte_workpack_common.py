"""Strict source-byte workpack parsing helpers.

Source-byte handoffs use ordinary ``sha256sum`` two-space lines.  Multiple
builders and retry classifiers need the same fail-closed parsing rules so a bad
handoff cannot be accepted by one surface and rejected by another.
"""
from __future__ import annotations

import hashlib
import re
import tomllib
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

SHA256SUM_LINE_RE = re.compile(r"^([0-9a-f]{64})  ([A-Za-z0-9._-]+)$")
SAFE_BASENAME_RE = re.compile(r"^[A-Za-z0-9._-]+$")


def safe_basename(raw: Any) -> bool:
    """Return whether ``raw`` is an archive-safe source-byte cache basename."""

    s = str(raw or "")
    if not s or s.startswith(".") or "/" in s or "\\" in s or ".." in s:
        return False
    return bool(SAFE_BASENAME_RE.fullmatch(s))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def host_of(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


def load_sources(lockfile: Path) -> list[dict[str, Any]]:
    with lockfile.open("rb") as f:
        rows = tomllib.load(f).get("source", [])
    return [r for r in rows if isinstance(r, dict) and str(r.get("id") or "").strip()]


def source_index_by_sha_local(lockfile: Path) -> dict[tuple[str, str], dict[str, Any]]:
    """Index pinned source rows by expected SHA-256 and local filename."""

    out: dict[tuple[str, str], dict[str, Any]] = {}
    for row in load_sources(lockfile):
        sha = str(row.get("sha256") or "").strip().lower()
        local = str(row.get("local_filename") or "").strip()
        if not sha or not local:
            continue
        key = (sha, local)
        if key in out:
            raise ValueError(f"duplicate sha/local lockfile entry for {local}")
        out[key] = row
    return out


def parse_strict_sha256sum_batch(batch_file: Path, *, lockfile: Path | None = None) -> list[dict[str, Any]]:
    """Parse a strict source-byte workpack.

    If ``lockfile`` is supplied, each line must match a pinned source row and the
    returned row includes ``source_id`` and ``url_host``.  The function rejects
    empty workpacks, duplicate lines, duplicate local filenames, unsafe names,
    and lockfile-missing entries.
    """

    pinned = source_index_by_sha_local(lockfile) if lockfile is not None else {}
    rows: list[dict[str, Any]] = []
    seen_lines: set[tuple[str, str]] = set()
    seen_names: set[str] = set()
    for lineno, raw in enumerate(batch_file.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        m = SHA256SUM_LINE_RE.fullmatch(raw)
        if not m:
            raise ValueError(f"invalid sha256sum line {batch_file}:{lineno}")
        sha, local = m.group(1), m.group(2)
        if not safe_basename(local):
            raise ValueError(f"unsafe batch local filename {batch_file}:{lineno}")
        key = (sha, local)
        if key in seen_lines:
            raise ValueError(f"duplicate sha256sum line {batch_file}:{lineno}")
        if local in seen_names:
            raise ValueError(f"duplicate batch local filename {batch_file}:{lineno}")
        seen_lines.add(key)
        seen_names.add(local)
        out: dict[str, Any] = {"expected_sha256": sha, "local_filename": local, "line_number": lineno}
        if lockfile is not None:
            src = pinned.get(key)
            if src is None:
                raise ValueError(f"batch line not pinned in lockfile {batch_file}:{lineno}:{local}")
            out["source_id"] = str(src.get("id") or "").strip()
            out["url_host"] = host_of(str(src.get("url") or ""))
            out["lockfile_row"] = src
        rows.append(out)
    if not rows:
        raise ValueError(f"empty batch file: {batch_file}")
    return rows


def sha256sum_line(row: dict[str, Any]) -> str:
    return f"{row['expected_sha256']}  {row['local_filename']}"
