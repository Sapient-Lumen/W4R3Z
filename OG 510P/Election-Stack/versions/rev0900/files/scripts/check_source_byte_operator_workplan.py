#!/usr/bin/env python3
"""Gate the source-byte operator workplan.

This check keeps the source-byte completion plan current with the actual queue,
batch, host-slice, DNS, and attempt-workpack reports.  It prevents a common
failure mode in this archive: a polished next-action report drifting away from
the governed `.sha256` files operators are supposed to run.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REV = VERSION.removeprefix("v").zfill(4)
SCRIPT = ROOT / "scripts" / "build_source_byte_operator_workplan.py"
REPORT = ROOT / "artifacts" / "reports" / f"source-byte-operator-workplan-rev{REV}.json"
STATUS_REPORT = ROOT / "artifacts" / "reports" / f"source-byte-cache-batch-status-rev{REV}.json"
BATCH01 = ROOT / "artifacts" / "source_byte_cache_intake" / "batches" / f"source-byte-cache-missing-receipts-rev{REV}-batch01.sha256"
REQUIRED_BOUNDARY_PHRASES = (
    "no-network acquisition accounting",
    "writes no receipts",
    "bundles no third-party bytes",
    "not source-byte cache completeness",
    "not current voter instruction",
    "not legal advice",
)


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except Exception:
        return str(path)


def fail(msg: str, proc: subprocess.CompletedProcess[str] | None = None) -> int:
    print("FAIL:", msg, file=sys.stderr)
    if proc is not None:
        if proc.stdout:
            print(proc.stdout, file=sys.stderr)
        if proc.stderr:
            print(proc.stderr, file=sys.stderr)
    return 2


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def nonempty_lines(path: Path) -> list[str]:
    return [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def main() -> int:
    if not REPORT.exists():
        return fail(f"missing current operator workplan: {rel(REPORT)}")
    proc = run([sys.executable, str(SCRIPT), "--json"])
    if proc.returncode != 0:
        return fail("operator workplan builder failed", proc)
    try:
        generated = json.loads(proc.stdout)
    except Exception as exc:
        return fail(f"operator workplan builder emitted non-json: {exc}", proc)
    shipped = load_json(REPORT)
    status = load_json(STATUS_REPORT)
    if generated != shipped:
        return fail("source-byte operator workplan is stale; run scripts/build_source_byte_operator_workplan.py --write")

    errors: list[str] = []
    if shipped.get("archive_version") != VERSION:
        errors.append("archive_version does not match VERSION")
    if shipped.get("network_io") is not False:
        errors.append("operator workplan must be no-network")
    if shipped.get("third_party_bytes_bundled") is not False:
        errors.append("operator workplan must not bundle third-party bytes")
    boundary = str(shipped.get("boundary") or "").lower()
    for phrase in REQUIRED_BOUNDARY_PHRASES:
        if phrase not in boundary:
            errors.append(f"boundary missing phrase: {phrase}")
    summary = shipped.get("receipt_summary") or {}
    for key in ("pinned_source_count", "receipt_present_count", "receipt_missing_count"):
        if int(summary.get(key) or -1) != int(status.get(key) or -2):
            errors.append(f"receipt_summary.{key} does not match batch status")
    if int(shipped.get("first_incomplete_batch_index") or -1) != int(status.get("first_incomplete_batch_index") or -2):
        errors.append("first incomplete batch index does not match batch status")
    if shipped.get("first_incomplete_batch_file") != status.get("first_incomplete_batch_file"):
        errors.append("first incomplete batch file does not match batch status")
    batches = shipped.get("current_batch_summaries") or []
    if int(shipped.get("batch_count") or -1) != len(batches):
        errors.append("batch_count does not match current_batch_summaries length")
    missing = int(summary.get("receipt_missing_count") or 0)
    if sum(int(b.get("line_count") or 0) for b in batches) != missing:
        errors.append("batch summary line counts do not sum to receipt_missing_count")
    if batches and int(shipped.get("batch01_source_count") or -1) != len(nonempty_lines(BATCH01)):
        errors.append("batch01_source_count does not match current batch01 line count")
    if int(shipped.get("post_batch01_remaining_source_count") or -1) != max(0, missing - len(nonempty_lines(BATCH01))):
        errors.append("post_batch01_remaining_source_count is wrong")

    command_plan = shipped.get("operator_command_plan") or []
    if len(command_plan) < 3:
        errors.append("operator_command_plan should contain at least fetch, return, and regenerate steps")
    command_text = "\n".join(str(c.get("command") or "") for c in command_plan if isinstance(c, dict))
    if f"rev{REV}" not in command_text:
        errors.append("operator_command_plan does not reference current revision workpacks")
    if "fetch_source_byte_batch.py" not in command_text:
        errors.append("operator_command_plan lacks fetch_source_byte_batch.py command")
    if "source_byte_receipts_from_cache_batch.py" not in command_text:
        errors.append("operator_command_plan lacks cache-return receipt command")
    if "--write-receipts" not in command_text:
        errors.append("operator_command_plan lacks --write-receipts return path")
    if "evidence/cache" in command_text:
        errors.append("operator_command_plan must not direct operators to release-local evidence/cache")
    if not shipped.get("classified_workpacks"):
        errors.append("classified_workpacks must not be empty while batch01 remains incomplete")
    if not shipped.get("highest_yield_host_slice"):
        errors.append("highest_yield_host_slice must be present while batch01 host slices exist")
    if "source_byte_receipts_from_cache_batch.py" not in str((shipped.get("operator_return_contract") or {}).get("full_missing_cache_scan_command") or ""):
        errors.append("operator_return_contract missing full cache scan command")
    if "source_byte_receipts_missing" not in (shipped.get("blocking_conditions") or []):
        errors.append("blocking_conditions must include source_byte_receipts_missing while receipts are missing")

    # Every path in executable workpack commands must exist in the release tree.
    for collection_name in ("classified_workpacks",):
        for row in shipped.get(collection_name) or []:
            path = ROOT / str(row.get("path") or "")
            if not path.exists():
                errors.append(f"missing workplan {collection_name} path: {rel(path)}")
    hpath = ROOT / str((shipped.get("highest_yield_host_slice") or {}).get("path") or "")
    if str(hpath) and not hpath.exists():
        errors.append(f"missing highest-yield host slice path: {rel(hpath)}")

    if errors:
        for err in errors:
            print("ERROR:", err, file=sys.stderr)
        return 2
    print(f"PASS: source-byte operator workplan ({VERSION}, missing={missing}, commands={len(command_plan)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
