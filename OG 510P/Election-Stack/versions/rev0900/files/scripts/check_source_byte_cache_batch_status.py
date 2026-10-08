#!/usr/bin/env python3
"""Check the current source-byte batch completion status report.

The report is a small drift firewall between three independently useful lanes:
source-byte receipts, the acquisition queue, and per-batch sha256sum handoffs.
If receipts are added later, this check forces the batch files/status report to
be regenerated instead of leaving completed source ids in receipt-missing batch
handoffs.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REV = VERSION.removeprefix("v").zfill(4)
SCRIPT = ROOT / "scripts" / "build_source_byte_cache_batch_status.py"
REPORT = ROOT / "artifacts" / "reports" / f"source-byte-cache-batch-status-rev{REV}.json"

REQUIRED_BOUNDARY_PHRASES = (
    "not current voter instruction",
    "not legal advice",
    "not source-byte cache completeness",
    "bundles no third-party bytes",
)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    if not SCRIPT.exists():
        errors.append("missing build_source_byte_cache_batch_status.py")
    if not REPORT.exists():
        errors.append(f"missing current batch status report {REPORT.relative_to(ROOT)}")
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2

    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--json"],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.returncode != 0:
        print("ERROR: build_source_byte_cache_batch_status.py --json failed", file=sys.stderr)
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        return 2

    generated = json.loads(proc.stdout)
    shipped = load_json(REPORT)
    if generated != shipped:
        errors.append("source-byte batch status report is stale; run scripts/build_source_byte_cache_batch_status.py --write")

    if shipped.get("archive_version") != VERSION:
        errors.append("batch status archive_version does not match VERSION")
    if shipped.get("synthetic_only") is not True:
        errors.append("batch status must carry synthetic_only=true")
    if shipped.get("network_io") is not False:
        errors.append("batch status must not perform network I/O")
    if shipped.get("third_party_bytes_bundled") is not False:
        errors.append("batch status must not bundle third-party source bytes")
    if int(shipped.get("error_count") or 0) != 0:
        errors.append("batch status error_count must be zero: " + ",".join(shipped.get("errors") or []))
    if int(shipped.get("stale_receipt_present_source_count") or 0) != 0:
        errors.append("batch status includes receipt-present sources in receipt-missing batch files")
    if int(shipped.get("missing_from_batch_count") or 0) != 0:
        errors.append("some receipt-missing queue sources are absent from batch files")
    if int(shipped.get("unexpected_in_batch_count") or 0) != 0:
        errors.append("some batch file sources are not currently receipt-missing")
    if int(shipped.get("duplicate_source_id_count") or 0) != 0:
        errors.append("duplicate source ids appear in batch files")
    if int(shipped.get("batched_source_count") or -1) != int(shipped.get("receipt_missing_count") or -2):
        errors.append("batched_source_count must equal receipt_missing_count")
    if int(shipped.get("receipt_present_count") or 0) <= 0:
        errors.append("batch status must retain existing receipt_present_count")
    if int(shipped.get("observed_byte_total") or 0) <= 0:
        errors.append("batch status must retain observed_byte_total")
    if int(shipped.get("first_incomplete_batch_index") or 0) <= 0 and int(shipped.get("receipt_missing_count") or 0) > 0:
        errors.append("batch status must identify a first incomplete batch while receipts are missing")

    boundary = str(shipped.get("boundary") or "").lower()
    for phrase in REQUIRED_BOUNDARY_PHRASES:
        if phrase not in boundary:
            errors.append(f"batch status boundary missing phrase: {phrase}")

    batch_count = int(shipped.get("batch_count") or 0)
    batches = shipped.get("batches") or []
    if batch_count != len(batches):
        errors.append("batch_count does not match batches length")
    for row in batches:
        if not isinstance(row, dict):
            errors.append("batch status row is not an object")
            continue
        if not str(row.get("path") or "").startswith("artifacts/source_byte_cache_intake/batches/"):
            errors.append("batch status row has unexpected batch path")
        if int(row.get("line_count") or -1) != int(row.get("receipt_missing_count") or -2):
            # Current batch handoffs are generated only for receipt-missing rows;
            # once receipts are added, the manifest/status must be regenerated.
            errors.append(f"batch row {row.get('batch_index')} line_count no longer equals receipt_missing_count")

    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2

    print(
        "PASS: source-byte cache batch status "
        f"({VERSION}, batches={batch_count}, missing={shipped['receipt_missing_count']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
