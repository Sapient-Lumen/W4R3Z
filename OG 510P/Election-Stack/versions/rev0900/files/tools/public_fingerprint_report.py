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
Symlinked packet roots, included files, included directories, unyielded/dangling public-surface symlinks, non-file public routes, oversized public files, public-name ambiguity surfaces, and cross-platform reserved public path components emit stable warnings; strict policy verification treats any public-fingerprint warning as fail-closed.

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
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

try:
    from tools.jcs import dump_bytes as jcs_dump_bytes
except Exception:
    from jcs import dump_bytes as jcs_dump_bytes


REPORT_FORMAT_VERSION = "1.4"  # report JSON format / inclusion-safety profile (not the archive VERSION)

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


def _canonical_file_hash(p: Path, rel_posix: str, max_bytes: int) -> Tuple[Optional[str], Optional[str]]:
    """Return (sha256_hex_or_none, warning).

    JSON files are JCS-canonicalized before hashing.
    Text/other files are hashed as raw bytes.

    Profile 1.4 intentionally rejects oversized public files instead of hashing
    only a prefix. A prefix hash plus a warning is easy for downstream tools or
    humans to misread as a content commitment; a rejected file with a stable
    warning makes strict policy verification and compare tooling fail closed.
    """

    b, truncated = _read_bytes_bounded(p, max_bytes)

    # Warnings are intended to be machine-parsable and stable. If multiple warnings
    # apply, join them with ';' rather than dropping one.
    warns: List[str] = []
    if truncated:
        return None, f"file_exceeds_max_include_bytes_rejected_for_hash:{rel_posix}:max_bytes={max_bytes}"

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
    """Yield (path, rel_posix) for files included in the public fingerprint.

    This iterator deliberately avoids following symlinked included directories.
    Per-file symlinks are filtered by ``compute_public_fingerprint`` so the
    report can emit a stable warning for strict verifier fail-closed behavior.
    """

    # Preserve caller-supplied packet_dir so a packet-root symlink remains visible.

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
    if notes_dir.exists() and notes_dir.is_dir() and not notes_dir.is_symlink():
        for p in sorted(notes_dir.rglob("*")):
            if not p.is_file():
                continue
            if p.suffix.lower() not in {".md", ".txt"}:
                continue
            rel = str(p.relative_to(packet_dir)).replace(os.sep, "/")
            yield p, rel

    # envelopes/*.envelope.json
    env_dir = packet_dir / "envelopes"
    if env_dir.exists() and env_dir.is_dir() and not env_dir.is_symlink():
        for p in sorted(env_dir.glob("*.envelope.json")):
            if p.is_file():
                rel = str(p.relative_to(packet_dir)).replace(os.sep, "/")
                yield p, rel

    # objects/*.json (JSON only; excludes pinned binaries)
    obj_dir = packet_dir / "objects"
    if obj_dir.exists() and obj_dir.is_dir() and not obj_dir.is_symlink():
        for p in sorted(obj_dir.glob("*.json")):
            if p.is_file():
                rel = str(p.relative_to(packet_dir)).replace(os.sep, "/")
                yield p, rel



WINDOWS_RESERVED_BASENAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}
WINDOWS_RESERVED_CHARS = set('<>:"|?*')


def _public_portable_component_problem(rel: str) -> str | None:
    """Return a portable-name problem for a bounded public relpath.

    The public fingerprint is intended for offline comparison by operators on
    different filesystems. POSIX allows names such as ``bad:name.txt`` and
    ``CON.txt`` that are ambiguous or unrepresentable on common Windows/macOS
    review machines. Strict policy verification treats these warnings as
    fail-closed, so reject them before they can become cross-platform replay or
    omission ambiguity.
    """

    for part in rel.split("/"):
        if any(ch in WINDOWS_RESERVED_CHARS for ch in part):
            return "windows_reserved_character"
        if part.endswith(" ") or part.endswith("."):
            return "windows_trailing_space_or_dot"
        stem = part.split(".", 1)[0].upper()
        if stem in WINDOWS_RESERVED_BASENAMES:
            return "windows_reserved_device_name"
    return None

def _safe_public_rel(rel: str) -> bool:
    if not rel or rel.startswith("/") or "\\" in rel:
        return False
    parts = rel.split("/")
    if any(part in ("", ".", "..") for part in parts):
        return False
    if any((ord(c) < 32) or (ord(c) == 127) for c in rel):
        return False
    return True


def _public_root_candidate(p: Path) -> bool:
    """Return whether a packet-root entry is part of the bounded public surface family."""

    if p.name in EXCLUDE_ROOT_NAMES:
        return False
    if p.name in ROOT_TEXT_NAMES or p.name in ROOT_JSON_NAMES:
        return True
    return p.suffix.lower() in {".md", ".txt", ".json"}


def _warn_unyielded_public_symlinks(packet_dir: Path) -> List[str]:
    """Warn for public-surface symlinks the normal include iterator would skip.

    ``Path.is_file()`` follows symlinks, so live symlinks to regular files are
    yielded and rejected by the main hashing loop. Dangling symlinks, directory
    symlinks nested below a public directory, and other unyielded routes can
    otherwise collapse into ordinary missing-file semantics. Strict policy
    verification treats these warnings as fail-closed.
    """

    warnings: List[str] = []

    for p in sorted(packet_dir.glob("*")):
        if p.is_symlink() and _public_root_candidate(p) and not p.is_file():
            warnings.append(f"file_symlink_rejected_for_hash:{p.name}")

    notes_dir = packet_dir / "notes"
    if notes_dir.exists() and notes_dir.is_dir() and not notes_dir.is_symlink():
        for p in sorted(notes_dir.rglob("*")):
            if not p.is_symlink():
                continue
            rel = str(p.relative_to(packet_dir)).replace(os.sep, "/")
            if p.suffix.lower() in {".md", ".txt"}:
                if not p.is_file():
                    warnings.append(f"file_symlink_rejected_for_hash:{rel}")
            elif not p.is_file():
                warnings.append(f"directory_symlink_rejected_for_hash:{rel}")

    env_dir = packet_dir / "envelopes"
    if env_dir.exists() and env_dir.is_dir() and not env_dir.is_symlink():
        for p in sorted(env_dir.glob("*.envelope.json")):
            if p.is_symlink() and not p.is_file():
                rel = str(p.relative_to(packet_dir)).replace(os.sep, "/")
                warnings.append(f"file_symlink_rejected_for_hash:{rel}")

    obj_dir = packet_dir / "objects"
    if obj_dir.exists() and obj_dir.is_dir() and not obj_dir.is_symlink():
        for p in sorted(obj_dir.glob("*.json")):
            if p.is_symlink() and not p.is_file():
                rel = str(p.relative_to(packet_dir)).replace(os.sep, "/")
                warnings.append(f"file_symlink_rejected_for_hash:{rel}")

    return warnings



def _warn_unyielded_public_nonfiles(packet_dir: Path) -> List[str]:
    """Warn for public-surface routes that exist but are not regular files.

    Without this pass, a same-selector packet could replace a public README or
    note with a directory/FIFO/device and look like the file was simply absent
    to the normal include iterator.  Strict policy verification treats warnings
    as fail-closed, so these routes must remain explicit.
    """

    warnings: List[str] = []
    for p in sorted(packet_dir.glob("*")):
        if _public_root_candidate(p) and not p.is_symlink() and not p.is_file():
            warnings.append(f"non_file_public_surface_rejected_for_hash:{p.name}")

    notes_dir = packet_dir / "notes"
    if notes_dir.exists() and notes_dir.is_dir() and not notes_dir.is_symlink():
        for p in sorted(notes_dir.rglob("*")):
            if p.is_symlink() or p.is_file():
                continue
            if p.suffix.lower() in {".md", ".txt"}:
                rel = str(p.relative_to(packet_dir)).replace(os.sep, "/")
                warnings.append(f"non_file_public_surface_rejected_for_hash:{rel}")

    env_dir = packet_dir / "envelopes"
    if env_dir.exists() and env_dir.is_dir() and not env_dir.is_symlink():
        for p in sorted(env_dir.glob("*.envelope.json")):
            if not p.is_symlink() and not p.is_file():
                rel = str(p.relative_to(packet_dir)).replace(os.sep, "/")
                warnings.append(f"non_file_public_surface_rejected_for_hash:{rel}")

    obj_dir = packet_dir / "objects"
    if obj_dir.exists() and obj_dir.is_dir() and not obj_dir.is_symlink():
        for p in sorted(obj_dir.glob("*.json")):
            if not p.is_symlink() and not p.is_file():
                rel = str(p.relative_to(packet_dir)).replace(os.sep, "/")
                warnings.append(f"non_file_public_surface_rejected_for_hash:{rel}")

    return warnings

def compute_public_fingerprint(packet_dir: Path, max_include_bytes: int) -> Tuple[str, List[str], List[str]]:
    """Return (root_digest, entry_lines, warnings).

    The public fingerprint is a publishable comparison digest, not a sandbox.
    Still, strict policy verification uses it as a replay boundary, so included
    surfaces must be boring local files.  Symlinks and escaped resolved paths are
    reported as warnings instead of being followed silently; the strict verifier
    already treats any warning as an authentication failure.
    """

    entry_lines: List[str] = []
    warnings: List[str] = []

    packet_dir_abs = packet_dir.resolve(strict=False)
    if packet_dir.is_symlink():
        warnings.append("packet_root_symlink_rejected_for_hash:.")
        warnings.sort()
        return sha256_bytes(b""), [], warnings

    for rel_dir in ("notes", "envelopes", "objects"):
        d = packet_dir / rel_dir
        if d.is_symlink():
            warnings.append(f"directory_symlink_rejected_for_hash:{rel_dir}")

    warnings.extend(_warn_unyielded_public_symlinks(packet_dir))
    warnings.extend(_warn_unyielded_public_nonfiles(packet_dir))

    seen: set[str] = set()
    seen_portable: dict[str, str] = {}
    for p, rel in _iter_included_files(packet_dir):
        if rel in seen:
            continue
        seen.add(rel)
        if not _safe_public_rel(rel):
            warnings.append(f"unsafe_relpath_rejected_for_hash:{rel}")
            continue
        nfc_rel = unicodedata.normalize("NFC", rel)
        if nfc_rel != rel:
            warnings.append(f"public_relpath_unicode_nfc_required_for_hash:{rel}")
            continue
        portable_problem = _public_portable_component_problem(nfc_rel)
        if portable_problem:
            warnings.append(f"public_relpath_portable_component_rejected_for_hash:{rel}:{portable_problem}")
            continue
        portable_key = nfc_rel.casefold()
        prior_rel = seen_portable.get(portable_key)
        if prior_rel and prior_rel != rel:
            warnings.append(f"public_relpath_casefold_collision_rejected_for_hash:{prior_rel}:{rel}")
            continue
        seen_portable[portable_key] = rel
        if p.is_symlink():
            warnings.append(f"file_symlink_rejected_for_hash:{rel}")
            continue
        try:
            resolved = p.resolve(strict=True)
            resolved.relative_to(packet_dir_abs)
        except Exception:
            warnings.append(f"file_resolved_outside_packet_rejected_for_hash:{rel}")
            continue
        if not p.is_file():
            warnings.append(f"non_file_rejected_for_hash:{rel}")
            continue
        h, warn = _canonical_file_hash(p, rel, max_include_bytes)
        if h is not None:
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

    packet_dir = Path(args.packet_dir)
    if not packet_dir.exists() or not packet_dir.is_dir():
        print("FAIL: packet_dir is not a directory")
        return 2

    if args.write_default and not args.out:
        args.out = str(packet_dir / "public-fingerprint.json")

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
            "path_portability_checks": "public relpaths must be NFC-normalized, distinct under Unicode casefolding, and avoid cross-platform reserved path components",
            "oversized_file_policy": "public files exceeding max_include_bytes are rejected with a warning instead of prefix-hashed",
            "non_file_policy": "public routes that exist but are not regular files are rejected with a warning instead of being treated as absent",
        },
        "warning_policy": "strict policy verification and compare tooling treat any warning as fail-closed/unsafe",
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
