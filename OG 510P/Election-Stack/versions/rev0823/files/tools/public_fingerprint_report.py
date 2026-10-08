#!/usr/bin/env python3
"""tools/public_fingerprint_report.py

Compute a deterministic *public fingerprint* for an evidence packet directory.

Why this exists:
- Dispute bundles and other publishable packets are meant to be compared and mirrored.
- A normal directory hash (see tools/bundle_hash_report.py) includes *everything*,
  including pinned third-party bytes or private raw captures.
- Operators often want a tight, publishable digest that covers only the small,
  intended-to-share surfaces.

This tool computes a root hash over a bounded set of files:
- packet root small text/json surfaces (e.g., claim.md, README.*, capture-note.md, redaction-log.md)
- manifest.json (if present)
- envelopes/*.envelope.json
- objects/*.json (JSON objects only; excludes non-JSON/binary objects)
- notes/**/*.md|txt

JSON files are canonicalized via RFC 8785 JCS before hashing to reduce formatting drift.

Output:
- JSON report to stdout (or --out)

Exit codes:
- 0: success
- 2: invalid path / IO error

See also:
- docs/173 (publishable packet preflight)
- docs/189 (publication hygiene + redaction)
- docs/222 (divergence dispute bundles)
- source: rfc8785_txt
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

try:
    from tools.jcs import dump_bytes as jcs_dump_bytes
except Exception:
    from jcs import dump_bytes as jcs_dump_bytes


REPORT_FORMAT_VERSION = "1.0"  # report JSON format (not the archive VERSION)

ROOT_TEXT_NAMES = {
    "README.md",
    "README.txt",
    "claim.md",
    "capture-note.md",
    "redaction-log.md",
}

ROOT_JSON_NAMES = {
    "manifest.json",
}

EXCLUDE_ROOT_NAMES = {
    "PUBLIC_FINGERPRINT.json",
    "public-fingerprint.json",
    "public_fingerprint.json",
}

# Bound scanning to avoid accidental inclusion of large bodies.
MAX_INCLUDE_BYTES_DEFAULT = 512 * 1024  # 512 KiB


def iso_utc_now_seconds() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _read_bytes_bounded(p: Path, max_bytes: int) -> Tuple[bytes, bool]:
    """Return (bytes, truncated) for p."""

    with p.open("rb") as f:
        b = f.read(max_bytes + 1)
    if len(b) > max_bytes:
        return b[:max_bytes], True
    return b, False


def _canonical_file_hash(p: Path, rel_posix: str, max_bytes: int) -> Tuple[str, Optional[str]]:
    """Return (sha256_hex, warning).

    JSON files are JCS-canonicalized before hashing.
    Text/other files are hashed as raw bytes.
    """

    b, truncated = _read_bytes_bounded(p, max_bytes)

    # Warnings are intended to be machine-parsable and stable. If multiple warnings
    # apply, join them with ';' rather than dropping one.
    warns: List[str] = []
    if truncated:
        warns.append(f"file_truncated_for_hash:{rel_posix}:max_bytes={max_bytes}")

    if p.suffix.lower() == ".json":
        try:
            obj = json.loads(b.decode("utf-8"))
            canon = jcs_dump_bytes(obj)
            warn = ";".join(warns) if warns else None
            return sha256_bytes(canon), warn
        except Exception:
            # Fall back to raw bytes; caller can decide whether to treat as fatal.
            warns.append(f"json_canonicalize_failed:{rel_posix}")
            return sha256_bytes(b), ";".join(warns)

    warn = ";".join(warns) if warns else None
    return sha256_bytes(b), warn


def _iter_included_files(packet_dir: Path) -> Iterable[Tuple[Path, str]]:
    """Yield (path, rel_posix) for files included in the public fingerprint."""

    packet_dir = packet_dir.resolve()

    # Root surfaces.
    for name in sorted(ROOT_TEXT_NAMES | ROOT_JSON_NAMES):
        if name in EXCLUDE_ROOT_NAMES:
            continue
        p = packet_dir / name
        if p.exists() and p.is_file():
            yield p, name

    # Include other small root .md/.txt files (e.g., packet README variants) except excluded.
    for p in sorted(packet_dir.glob("*")):
        if not p.is_file():
            continue
        if p.name in ROOT_TEXT_NAMES or p.name in ROOT_JSON_NAMES or p.name in EXCLUDE_ROOT_NAMES:
            continue
        if p.suffix.lower() in {".md", ".txt", ".json"}:
            yield p, p.name

    # notes/**/*.md|txt
    notes_dir = packet_dir / "notes"
    if notes_dir.exists() and notes_dir.is_dir():
        for p in sorted(notes_dir.rglob("*")):
            if not p.is_file():
                continue
            if p.suffix.lower() not in {".md", ".txt"}:
                continue
            rel = str(p.relative_to(packet_dir)).replace(os.sep, "/")
            yield p, rel

    # envelopes/*.envelope.json
    env_dir = packet_dir / "envelopes"
    if env_dir.exists() and env_dir.is_dir():
        for p in sorted(env_dir.glob("*.envelope.json")):
            if p.is_file():
                rel = str(p.relative_to(packet_dir)).replace(os.sep, "/")
                yield p, rel

    # objects/*.json (JSON only; excludes pinned binaries)
    obj_dir = packet_dir / "objects"
    if obj_dir.exists() and obj_dir.is_dir():
        for p in sorted(obj_dir.glob("*.json")):
            if p.is_file():
                rel = str(p.relative_to(packet_dir)).replace(os.sep, "/")
                yield p, rel


def compute_public_fingerprint(packet_dir: Path, max_include_bytes: int) -> Tuple[str, List[str], List[str]]:
    """Return (root_digest, entry_lines, warnings)."""

    entry_lines: List[str] = []
    warnings: List[str] = []

    seen: set[str] = set()
    for p, rel in _iter_included_files(packet_dir):
        if rel in seen:
            continue
        seen.add(rel)
        h, warn = _canonical_file_hash(p, rel, max_include_bytes)
        entry_lines.append(f"{h}  {rel}")
        if warn:
            warnings.append(warn)

    entry_lines.sort()
    warnings.sort()

    root = sha256_bytes(("\n".join(entry_lines)).encode("utf-8"))
    return root, entry_lines, warnings


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("packet_dir", help="Path to evidence packet directory")
    ap.add_argument("--out", help="Write JSON report to this file instead of stdout")
    ap.add_argument(
        "--write-default",
        action="store_true",
        help="Convenience: write to <packet_dir>/public-fingerprint.json (suppresses stdout output)",
    )
    ap.add_argument(
        "--max-include-bytes",
        type=int,
        default=MAX_INCLUDE_BYTES_DEFAULT,
        help=f"Max bytes read per included file (default: {MAX_INCLUDE_BYTES_DEFAULT})",
    )
    ap.add_argument(
        "--stable",
        action="store_true",
        help="Omit generated_at (stable file content across regenerations); public_fingerprint_sha256 is always stable",
    )
    ap.add_argument(
        "--include-file-hashes",
        action="store_true",
        help="Include per-file hash lines in the JSON output (can be long for large packets)",
    )
    args = ap.parse_args()

    packet_dir = Path(args.packet_dir).resolve()
    if not packet_dir.exists() or not packet_dir.is_dir():
        print("FAIL: packet_dir is not a directory")
        return 2

    if args.write_default and not args.out:
        args.out = str((packet_dir / "public-fingerprint.json").resolve())

    root, lines, warnings = compute_public_fingerprint(packet_dir, int(args.max_include_bytes))
    report = {
        "report_format_version": REPORT_FORMAT_VERSION,
        "hash_alg": "sha256",
        "root_hash_construction": "sha256(sorted_lines_of('sha256  relpath'))",
        "public_fingerprint_sha256": root,
        "included_file_count": len(lines),
        "include_rules": {
            "root_text_names": sorted(ROOT_TEXT_NAMES),
            "root_json_names": sorted(ROOT_JSON_NAMES),
            "root_excludes": sorted(EXCLUDE_ROOT_NAMES),
            "envelopes": "envelopes/*.envelope.json",
            "objects": "objects/*.json",
            "notes": "notes/**/*.md|txt",
            "json_canonicalization": "RFC8785 JCS",
        },
        "warnings": warnings,
    }

    if not args.stable:
        report["generated_at"] = iso_utc_now_seconds()

    if args.include_file_hashes:
        report["file_hashes"] = lines

    out = json.dumps(report, indent=2)
    if args.out:
        Path(args.out).write_text(out + "\n", encoding="utf-8")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
