#!/usr/bin/env python3
"""Check the pinned-source byte-acquisition queue and cache-name refactor.

The source-byte receipt pack proves a selected subset.  This gate covers the
next risk: the remaining pinned rows must have stable cache basenames and a
fresh machine-readable operator queue so byte acquisition can proceed in finite
batches instead of by ad hoc lockfile spelunking.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REV = VERSION.removeprefix("v").zfill(4)
TOOL = ROOT / "tools" / "source_byte_acquisition_queue.py"
REPORT = ROOT / "artifacts" / "reports" / "source-byte-acquisition-queue.json"
FETCH = ROOT / "scripts" / "fetch_source_sha256.py"
CACHE_RECEIPT = ROOT / "scripts" / "source_byte_receipt_from_cache.py"
RECEIPT_REPORT = ROOT / "artifacts" / "reports" / "source-byte-receipt-validation-report.json"

REQUIRED_BOUNDARY_PHRASES = (
    "not current voter instruction",
    "not legal advice",
    "not source-byte cache completeness",
)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def run_json(cmd: list[str]) -> dict:
    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.returncode != 0:
        print("ERROR: command failed:", " ".join(cmd), file=sys.stderr)
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        raise SystemExit(2)
    return json.loads(proc.stdout)


def main() -> int:
    errors: list[str] = []
    for path, label in ((TOOL, "tool"), (REPORT, "report"), (FETCH, "fetch helper"), (CACHE_RECEIPT, "cache receipt helper"), (RECEIPT_REPORT, "receipt report")):
        if not path.exists():
            errors.append(f"missing {label}: {path.relative_to(ROOT)}")
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2

    generated = run_json([sys.executable, str(TOOL), "--json"])
    shipped = load_json(REPORT)
    receipt_report = load_json(RECEIPT_REPORT)
    if generated != shipped:
        errors.append("source-byte-acquisition-queue.json is stale; run tools/source_byte_acquisition_queue.py --write")

    if shipped.get("archive_version") != VERSION:
        errors.append("source-byte acquisition queue archive_version does not match VERSION")
    if shipped.get("synthetic_only") is not True:
        errors.append("source-byte acquisition queue must carry synthetic_only=true")
    if shipped.get("third_party_bytes_bundled") is not False:
        errors.append("source-byte acquisition queue must not claim bundled third-party bytes")

    boundary = str(shipped.get("boundary") or "").lower()
    for phrase in REQUIRED_BOUNDARY_PHRASES:
        if phrase not in boundary:
            errors.append(f"source-byte acquisition queue boundary missing phrase: {phrase}")

    pinned = int(shipped.get("pinned_source_count") or 0)
    present = int(shipped.get("receipt_present_count") or 0)
    missing = int(shipped.get("receipt_missing_count") or 0)
    if pinned <= 0:
        errors.append("pinned_source_count must be positive")
    if present != int(receipt_report.get("valid_receipt_count") or -1):
        errors.append("receipt_present_count must equal valid_receipt_count from receipt report")
    if present + missing != pinned:
        errors.append("receipt_present_count + receipt_missing_count must equal pinned_source_count")
    if int(shipped.get("pinned_sources_with_local_filename_count") or 0) != pinned:
        errors.append("every pinned source must have a local_filename")
    if shipped.get("missing_local_filename_source_ids"):
        errors.append("missing_local_filename_source_ids must be empty")
    if shipped.get("duplicate_local_filenames"):
        errors.append("duplicate_local_filenames must be empty")

    status_counts = shipped.get("receipt_status_counts") or {}
    if int(status_counts.get("receipt_present") or 0) != present:
        errors.append("receipt_status_counts.receipt_present disagrees with summary")
    if int(status_counts.get("receipt_missing") or 0) != missing:
        errors.append("receipt_status_counts.receipt_missing disagrees with summary")

    rows = shipped.get("rows") or []
    if len(rows) != pinned:
        errors.append("rows length must equal pinned_source_count")
    seen_ids: set[str] = set()
    seen_names: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            errors.append("queue row is not an object")
            continue
        sid = str(row.get("source_id") or "")
        if not sid:
            errors.append("queue row missing source_id")
        elif sid in seen_ids:
            errors.append(f"duplicate queue source_id: {sid}")
        seen_ids.add(sid)
        lfn = str(row.get("local_filename") or "")
        if not lfn:
            errors.append(f"queue row missing local_filename: {sid}")
        elif lfn in seen_names:
            errors.append(f"duplicate queue local_filename: {lfn}")
        seen_names.add(lfn)

    template = str(shipped.get("fetch_command_template") or "")
    if "{source_id}" not in template or "--write-receipt" not in template or "--cache-dir" not in template:
        errors.append("fetch_command_template must include {source_id}, --cache-dir, and --write-receipt")

    current_batch = str(shipped.get("current_batch_file") or "")
    expected_batch = f"artifacts/source_byte_cache_intake/batches/source-byte-cache-missing-receipts-rev{REV}-batch01.sha256"
    if current_batch != expected_batch:
        errors.append("current_batch_file must point at the current rev batch01 handoff")
    batch_template = str(shipped.get("batch_fetch_command_template") or "")
    if expected_batch not in batch_template or "fetch_source_byte_batch.py" not in batch_template or "--write-receipts" not in batch_template:
        errors.append("batch_fetch_command_template must run the current batch fetcher with --write-receipts")
    followup_template = str(shipped.get("batch_followup_command_template") or "")
    if f"source-byte-batch-fetch-plan-rev{REV}.json" not in followup_template or "build_source_byte_batch_followup.py" not in followup_template:
        errors.append("batch_followup_command_template must reference the current rev fetch plan and follow-up builder")
    workplan_template = str(shipped.get("operator_workplan_command_template") or "")
    if "build_source_byte_operator_workplan.py" not in workplan_template or "check_source_byte_operator_workplan.py" not in workplan_template:
        errors.append("operator_workplan_command_template must build and check the source-byte operator workplan")

    batch = shipped.get("next_operator_batch_source_ids") or []
    if missing > 0 and not batch:
        errors.append("next_operator_batch_source_ids must not be empty while receipts are missing")
    if len(batch) > int(shipped.get("recommended_batch_size") or 0):
        errors.append("next_operator_batch_source_ids exceeds recommended_batch_size")

    # Smoke the source-id fetch planner without network I/O. This catches drift
    # between the queue command shape, lockfile local_filename requirements, and
    # the operator helper before a maintainer starts a long fetch batch.
    probe_id = str(batch[0]) if batch else "rfc8785_txt"
    plan = run_json([sys.executable, str(FETCH), "--source-id", probe_id, "--print-plan"])
    if plan.get("source_id") != probe_id:
        errors.append("fetch helper --print-plan did not echo requested source_id")
    if plan.get("network_io") is not False:
        errors.append("fetch helper --print-plan must not perform network I/O")
    if not str(plan.get("local_filename") or ""):
        errors.append("fetch helper --print-plan did not resolve local_filename")
    plan_boundary = str(plan.get("boundary") or "").lower()
    for phrase in REQUIRED_BOUNDARY_PHRASES:
        if phrase not in plan_boundary:
            errors.append(f"fetch helper plan boundary missing phrase: {phrase}")

    cache_plan = run_json([
        sys.executable,
        str(CACHE_RECEIPT),
        "--source-id",
        probe_id,
        "--cache-dir",
        "/path/to/source-cache",
        "--print-plan",
    ])
    if cache_plan.get("source_id") != probe_id:
        errors.append("cache receipt helper --print-plan did not echo requested source_id")
    if cache_plan.get("network_io") is not False:
        errors.append("cache receipt helper --print-plan must not perform network I/O")
    if cache_plan.get("observation_type") != "operator_cache_file":
        errors.append("cache receipt helper plan must use operator_cache_file observation_type")
    if not str(cache_plan.get("local_filename") or ""):
        errors.append("cache receipt helper --print-plan did not resolve local_filename")
    cache_boundary = str(cache_plan.get("boundary") or "").lower()
    for phrase in REQUIRED_BOUNDARY_PHRASES:
        if phrase not in cache_boundary:
            errors.append(f"cache receipt helper plan boundary missing phrase: {phrase}")

    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2
    print(
        "PASS: source-byte acquisition queue "
        f"({VERSION}, pinned={pinned}, receipts={present}, queued={missing})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
