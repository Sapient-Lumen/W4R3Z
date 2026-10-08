#!/usr/bin/env python3
"""Check per-batch source-byte cache intake manifests.

This gate makes the source-byte completion lane easier to execute without
weakening the evidence boundary: the shipped batch files must reconstruct the
master sha256sum intake file exactly, must cover each receipt-missing pinned
source once, and must remain current with VERSION.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REV = VERSION.removeprefix("v").zfill(4)
BUILDER = ROOT / "scripts" / "build_source_byte_cache_batch_manifests.py"
REPORT = ROOT / "artifacts" / "reports" / f"source-byte-cache-batch-manifests-rev{REV}.json"
MASTER = ROOT / "artifacts" / "source_byte_cache_intake" / f"source-byte-cache-missing-receipts-rev{REV}.sha256"
BATCH_DIR = ROOT / "artifacts" / "source_byte_cache_intake" / "batches"
INTAKE_REPORT = ROOT / "artifacts" / "reports" / f"source-byte-cache-intake-manifest-rev{REV}.json"
LINE_RE = re.compile(r"^[0-9a-f]{64}  [A-Za-z0-9._-]+$")
REQUIRED_BOUNDARY_PHRASES = (
    "not current voter instruction",
    "not legal advice",
    "bundle no third-party bytes",
    "do not prove source-byte cache completeness",
)


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except Exception:
        return str(path)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run_generated() -> dict:
    proc = subprocess.run(
        [sys.executable, str(BUILDER), "--json"],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.returncode != 0:
        print("ERROR: batch manifest builder failed", file=sys.stderr)
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        raise SystemExit(2)
    return json.loads(proc.stdout)


def main() -> int:
    errors: list[str] = []
    for path in (BUILDER, REPORT, MASTER, INTAKE_REPORT):
        if not path.exists():
            errors.append(f"missing required file: {rel(path)}")
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2

    generated = run_generated()
    shipped = load_json(REPORT)
    intake = load_json(INTAKE_REPORT)
    if generated != shipped:
        errors.append("source-byte cache batch-manifests report is stale; run scripts/build_source_byte_cache_batch_manifests.py --write")

    if shipped.get("archive_version") != VERSION:
        errors.append("batch-manifests report archive_version does not match VERSION")
    if shipped.get("synthetic_only") is not True:
        errors.append("batch-manifests report must carry synthetic_only=true")
    if shipped.get("network_io") is not False:
        errors.append("batch-manifests report must record network_io=false")
    if shipped.get("third_party_bytes_bundled") is not False:
        errors.append("batch-manifests report must record third_party_bytes_bundled=false")
    boundary = str(shipped.get("boundary") or "").lower()
    for phrase in REQUIRED_BOUNDARY_PHRASES:
        if phrase not in boundary:
            errors.append(f"batch-manifests boundary missing phrase: {phrase}")
    if int(shipped.get("error_count", -1)) != 0:
        errors.append(f"batch-manifests report errors must be zero: {shipped.get('errors')}")
    if shipped.get("master_sha256sum_path") != rel(MASTER):
        errors.append("batch-manifests report points at the wrong master sha256sum path")
    if shipped.get("intake_report") != rel(INTAKE_REPORT):
        errors.append("batch-manifests report points at the wrong intake report")
    if int(shipped.get("manifest_entry_count") or -1) != int(intake.get("manifest_entry_count") or -2):
        errors.append("batch manifest entry count does not match intake manifest")
    if int(shipped.get("receipt_missing_count") or -1) != int(intake.get("receipt_missing_count") or -2):
        errors.append("batch receipt-missing count does not match intake manifest")

    master_lines = [ln for ln in MASTER.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if len(master_lines) != int(shipped.get("manifest_entry_count") or -1):
        errors.append("master sha256sum line count does not match batch report")
    if any(not LINE_RE.fullmatch(ln) for ln in master_lines):
        errors.append("master sha256sum contains an invalid line")

    reconstructed_lines: list[str] = []
    seen_paths: set[str] = set()
    seen_source_ids: set[str] = set()
    duplicate_source_ids: set[str] = set()
    batch_files = shipped.get("batch_files") or []
    if int(shipped.get("batch_count") or 0) != len(batch_files):
        errors.append("batch_count does not equal batch_files length")
    for idx, row in enumerate(batch_files, start=1):
        if not isinstance(row, dict):
            errors.append("batch_files entry is not an object")
            continue
        path = ROOT / str(row.get("path") or "")
        seen_paths.add(str(row.get("path") or ""))
        if int(row.get("batch_index") or 0) != idx:
            errors.append(f"batch index drift at row {idx}")
        if not path.exists():
            errors.append(f"missing batch file: {rel(path)}")
            continue
        lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        reconstructed_lines.extend(lines)
        if len(lines) != int(row.get("line_count") or -1):
            errors.append(f"batch line count mismatch: {rel(path)}")
        if int(row.get("line_count") or 0) > int(shipped.get("batch_size") or 0):
            errors.append(f"batch has too many entries: {rel(path)}")
        if any(not LINE_RE.fullmatch(ln) for ln in lines):
            errors.append(f"batch file contains invalid sha256sum line: {rel(path)}")
        for sid in row.get("source_ids") or []:
            sid = str(sid)
            if sid in seen_source_ids:
                duplicate_source_ids.add(sid)
            seen_source_ids.add(sid)
    if reconstructed_lines != master_lines:
        errors.append("concatenated batch files do not reconstruct the master sha256sum file exactly")
    if duplicate_source_ids:
        errors.append("duplicate source ids across batches: " + ",".join(sorted(duplicate_source_ids)))

    expected_paths = {str((BATCH_DIR / f"source-byte-cache-missing-receipts-rev{REV}-batch{i:02d}.sha256").relative_to(ROOT)) for i in range(1, int(shipped.get("batch_count") or 0) + 1)}
    actual_current_paths = {rel(p) for p in BATCH_DIR.glob(f"source-byte-cache-missing-receipts-rev{REV}-batch*.sha256")}
    if seen_paths != expected_paths or actual_current_paths != expected_paths:
        errors.append("current batch file set does not match expected contiguous batch paths")

    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2
    print(f"PASS: source-byte cache batch manifests ({VERSION}, batches={shipped['batch_count']}, entries={shipped['manifest_entry_count']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
