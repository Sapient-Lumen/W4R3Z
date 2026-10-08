#!/usr/bin/env python3
"""Gate the shared strict source-byte workpack parser.

The source-byte lane now has multiple `.sha256` handoff builders: intake batch
manifests, host slices, attempt workpacks, and follow-ups.  This gate proves the
common parser rejects the failure modes that would otherwise make one handoff
surface disagree with another: unsafe basenames, duplicate lines, duplicate
local filenames, empty workpacks, and entries not pinned in the lockfile.
"""
from __future__ import annotations

import hashlib
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from source_byte_workpack_common import parse_strict_sha256sum_batch, safe_basename, sha256sum_line  # noqa: E402

VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REV = VERSION.removeprefix("v").zfill(4)
CURRENT_BATCH = ROOT / "artifacts" / "source_byte_cache_intake" / "batches" / f"source-byte-cache-missing-receipts-rev{REV}-batch01.sha256"
LOCK = ROOT / "evidence" / "lock" / "external-sources.toml"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def expect_error(label: str, fn) -> list[str]:
    try:
        fn()
    except Exception:
        return []
    return [f"common parser accepted invalid fixture: {label}"]


def main() -> int:
    errors: list[str] = []
    if not CURRENT_BATCH.exists():
        errors.append(f"missing current batch01: {CURRENT_BATCH.relative_to(ROOT)}")
    else:
        try:
            rows = parse_strict_sha256sum_batch(CURRENT_BATCH, lockfile=LOCK)
        except Exception as exc:
            errors.append(f"common parser rejected current batch01: {exc}")
            rows = []
        if rows:
            if len(rows) != 20:
                errors.append(f"current batch01 should have 20 rows, got {len(rows)}")
            if len({str(r.get('source_id') or '') for r in rows}) != len(rows):
                errors.append("common parser produced duplicate source_id values for current batch01")
            if any(not str(r.get("url_host") or "") for r in rows):
                errors.append("common parser did not attach url_host to every lockfile-backed row")
            if sha256sum_line(rows[0]) not in CURRENT_BATCH.read_text(encoding="utf-8"):
                errors.append("common parser sha256sum_line did not reconstruct the first current batch row")

    if not safe_basename("valid-file_1.2.pdf"):
        errors.append("safe_basename rejected a valid cache basename")
    for bad in ("", ".hidden", "../x.pdf", "dir/x.pdf", "dir\\x.pdf", "has space.pdf", "two..dots.pdf"):
        if safe_basename(bad):
            errors.append(f"safe_basename accepted unsafe value: {bad!r}")

    with tempfile.TemporaryDirectory(prefix="tes_source_workpack_common_") as td:
        tmp = Path(td)
        payload = "good bytes\n"
        sha = sha256_text(payload)
        lock = tmp / "external-sources.toml"
        good = tmp / "good.sha256"
        duplicate_line = tmp / "duplicate-line.sha256"
        duplicate_name = tmp / "duplicate-name.sha256"
        unsafe = tmp / "unsafe.sha256"
        unpinned = tmp / "unpinned.sha256"
        empty = tmp / "empty.sha256"
        write(
            lock,
            f'''
[[source]]
id = "fixture_good"
url = "https://example.invalid/good.pdf"
retrieved = "2026-06-13"
sha256 = "{sha}"
local_filename = "good.pdf"
tags = ["eac"]
'''.lstrip(),
        )
        write(good, f"{sha}  good.pdf\n")
        parsed = parse_strict_sha256sum_batch(good, lockfile=lock)
        if len(parsed) != 1 or parsed[0].get("source_id") != "fixture_good" or parsed[0].get("url_host") != "example.invalid":
            errors.append("common parser did not attach expected lockfile metadata for valid fixture")
        write(duplicate_line, f"{sha}  good.pdf\n{sha}  good.pdf\n")
        errors.extend(expect_error("duplicate line", lambda: parse_strict_sha256sum_batch(duplicate_line, lockfile=lock)))
        write(duplicate_name, f"{sha}  good.pdf\n{'0'*64}  good.pdf\n")
        errors.extend(expect_error("duplicate local filename", lambda: parse_strict_sha256sum_batch(duplicate_name, lockfile=lock)))
        write(unsafe, f"{sha}  ../good.pdf\n")
        errors.extend(expect_error("unsafe basename", lambda: parse_strict_sha256sum_batch(unsafe, lockfile=lock)))
        write(unpinned, f"{'0'*64}  other.pdf\n")
        errors.extend(expect_error("unpinned entry", lambda: parse_strict_sha256sum_batch(unpinned, lockfile=lock)))
        write(empty, "\n")
        errors.extend(expect_error("empty workpack", lambda: parse_strict_sha256sum_batch(empty, lockfile=lock)))

    if errors:
        for err in errors:
            print("ERROR:", err, file=sys.stderr)
        return 2
    print(f"PASS: source-byte workpack common parser ({VERSION})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
