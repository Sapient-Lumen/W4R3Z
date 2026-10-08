#!/usr/bin/env python3
"""Check source-byte receipt pack and validation report.

This gate makes the source-byte acquisition lane concrete without shipping
third-party PDFs/texts. It verifies that selected high-leverage pinned lockfile
rows have deterministic receipts whose observed sha256 equals the lockfile pin,
while preserving the archive boundary that receipts are not current voter
instruction and not source-cache completeness.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
TOOL = ROOT / "tools" / "source_byte_receipt_pack.py"
REPORT = ROOT / "artifacts" / "reports" / "source-byte-receipt-validation-report.json"
RECEIPTS = ROOT / "artifacts" / "source_byte_receipts"

MIN_RECEIPTS = 13
MIN_OBSERVED_BYTE_TOTAL = 10_421_893
REQUIRED_FAMILIES = {"eac", "nist", "rfc"}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    if not TOOL.exists():
        errors.append("missing tools/source_byte_receipt_pack.py")
    if not RECEIPTS.exists():
        errors.append("missing artifacts/source_byte_receipts/")
    if not REPORT.exists():
        errors.append("missing source-byte-receipt-validation-report.json")
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2

    proc = subprocess.run(
        [sys.executable, str(TOOL), "--json"],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.returncode != 0:
        print("ERROR: source_byte_receipt_pack.py --json failed", file=sys.stderr)
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        return 2
    generated = json.loads(proc.stdout)
    shipped = load_json(REPORT)
    if generated != shipped:
        errors.append("source-byte-receipt-validation-report.json is stale; run tools/source_byte_receipt_pack.py --write")

    if shipped.get("archive_version") != VERSION:
        errors.append("source-byte receipt report archive_version does not match VERSION")
    if shipped.get("synthetic_only") is not True:
        errors.append("source-byte receipt report must carry synthetic_only=true")
    if shipped.get("bundled_third_party_bytes") is not False:
        errors.append("source-byte receipt report must not claim bundled third-party bytes")
    if int(shipped.get("receipt_count") or 0) < MIN_RECEIPTS:
        errors.append(f"expected at least {MIN_RECEIPTS} source-byte receipts")
    if int(shipped.get("invalid_receipt_count", -1)) != 0:
        errors.append("source-byte receipt invalid count must be zero")
    if int(shipped.get("valid_receipt_count", 0)) != int(shipped.get("receipt_count", -1)):
        errors.append("all source-byte receipts must be valid")
    if int(shipped.get("observed_byte_total") or 0) < MIN_OBSERVED_BYTE_TOTAL:
        errors.append(f"observed_byte_total regressed below current floor {MIN_OBSERVED_BYTE_TOTAL}")

    obs_counts = shipped.get("observation_type_counts") or {}
    if not obs_counts:
        errors.append("source-byte receipt report must include observation_type_counts")
    if int(obs_counts.get("network_fetch") or 0) <= 0:
        errors.append("source-byte receipt pack must retain at least one network_fetch observation")

    boundary = str(shipped.get("boundary") or "").lower()
    for phrase in ("not current voter instruction", "not legal advice", "not source-byte cache completeness"):
        if phrase not in boundary:
            errors.append(f"source-byte receipt boundary missing phrase: {phrase}")

    families = set((shipped.get("families_covered") or {}).keys())
    missing_families = sorted(REQUIRED_FAMILIES - families)
    if missing_families:
        errors.append("source-byte receipts must cover families: " + ", ".join(missing_families))

    for row in shipped.get("rows") or []:
        if not isinstance(row, dict):
            errors.append("source-byte receipt row is not an object")
            continue
        path = str(row.get("path") or "")
        if not path.startswith("artifacts/source_byte_receipts/"):
            errors.append(f"unexpected source-byte receipt path: {path}")
        if row.get("valid") is not True:
            errors.append(f"invalid source-byte receipt: {path} {row.get('error_codes')}")
        if str(row.get("observation_type") or "") not in {"network_fetch", "operator_cache_file"}:
            errors.append(f"invalid observation_type in receipt row: {path}")
        if not str(row.get("observed_sha256") or ""):
            errors.append(f"missing observed sha in receipt row: {path}")

    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2

    print(
        "PASS: source-byte receipt pack "
        f"({VERSION}, receipts={shipped['receipt_count']}, observed_bytes={shipped['observed_byte_total']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
