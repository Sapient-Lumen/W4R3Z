#!/usr/bin/env python3
"""Offline smoke gate for the source-byte batch fetcher.

The fetcher is network-capable, so the release gate only exercises no-network
paths: plan-only against the current batch, exact-match cache receipt writing in
a temporary fixture, and refusal to use a release-governed cache directory.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "fetch_source_byte_batch.py"
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REV = VERSION.removeprefix("v").zfill(4)
CURRENT_BATCH01 = ROOT / "artifacts" / "source_byte_cache_intake" / "batches" / f"source-byte-cache-missing-receipts-rev{REV}-batch01.sha256"


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)


def fail(msg: str, proc: subprocess.CompletedProcess[str] | None = None) -> int:
    print("FAIL:", msg, file=sys.stderr)
    if proc is not None:
        if proc.stdout:
            print(proc.stdout, file=sys.stderr)
        if proc.stderr:
            print(proc.stderr, file=sys.stderr)
    return 2


def main() -> int:
    if not CURRENT_BATCH01.exists():
        return fail(f"missing current batch file {CURRENT_BATCH01.relative_to(ROOT)}")

    # Current release plan-only path must be deterministic and offline.
    proc = run([
        sys.executable,
        str(SCRIPT),
        "--batch-file",
        str(CURRENT_BATCH01),
        "--print-plan",
        "--json",
    ])
    if proc.returncode != 0:
        return fail("plan-only current batch fetch report failed", proc)
    try:
        plan = json.loads(proc.stdout)
    except Exception as exc:
        return fail(f"plan-only output was not JSON: {exc}", proc)
    if plan.get("archive_version") != VERSION or plan.get("network_io") is not False:
        return fail("plan-only report did not preserve current version/no-network boundary", proc)
    if int(plan.get("candidate_source_count") or 0) < 2:
        return fail("plan-only report selected fewer than two current batch sources", proc)
    statuses = {r.get("status") for r in plan.get("rows", []) if isinstance(r, dict)}
    if statuses != {"plan_only"}:
        return fail(f"plan-only rows had unexpected statuses: {statuses!r}", proc)

    # Source-id filters let operators route around a failing host or large file
    # without hand-editing governed batch files. They must be strict: unknown ids
    # fail closed and valid include/skip filters only change the selected row set.
    plan_ids = [str(r.get("source_id") or "") for r in plan.get("rows", []) if isinstance(r, dict)]
    first_id, second_id = plan_ids[0], plan_ids[1]
    proc = run([
        sys.executable,
        str(SCRIPT),
        "--batch-file",
        str(CURRENT_BATCH01),
        "--print-plan",
        "--only-source-ids",
        first_id,
        "--json",
    ])
    if proc.returncode != 0:
        return fail("plan-only --only-source-ids failed for a valid current batch id", proc)
    filtered = json.loads(proc.stdout)
    if int(filtered.get("candidate_source_count") or 0) != 1 or filtered.get("source_id_filter_applied") is not True:
        return fail("--only-source-ids did not narrow the batch to exactly one row", proc)
    if [r.get("source_id") for r in filtered.get("rows", [])] != [first_id]:
        return fail("--only-source-ids selected the wrong source", proc)

    proc = run([
        sys.executable,
        str(SCRIPT),
        "--batch-file",
        str(CURRENT_BATCH01),
        "--print-plan",
        "--skip-source-ids",
        first_id,
        "--limit",
        "1",
        "--json",
    ])
    if proc.returncode != 0:
        return fail("plan-only --skip-source-ids failed for a valid current batch id", proc)
    skipped = json.loads(proc.stdout)
    if int(skipped.get("candidate_source_count") or 0) != 1:
        return fail("--skip-source-ids plus --limit did not select one row", proc)
    if skipped.get("rows", [{}])[0].get("source_id") != second_id:
        return fail("--skip-source-ids did not route around the skipped source", proc)

    proc = run([
        sys.executable,
        str(SCRIPT),
        "--batch-file",
        str(CURRENT_BATCH01),
        "--print-plan",
        "--only-source-ids",
        "not_in_this_batch",
        "--json",
    ])
    if proc.returncode == 0:
        return fail("fetcher accepted an unknown --only-source-ids value", proc)

    # Exact-match cache fixture writes one operator_cache_file receipt without network.
    with tempfile.TemporaryDirectory(prefix="tes_source_batch_fetcher_") as td:
        tmp = Path(td)
        cache = tmp / "cache"
        receipts = tmp / "receipts"
        report_path = tmp / "report.json"
        cache.mkdir()
        body = b"fixture source bytes\n"
        digest = hashlib.sha256(body).hexdigest()
        local_filename = "fixture_source.txt"
        (cache / local_filename).write_bytes(body)
        lock = tmp / "external-sources.toml"
        lock.write_text(
            "[[source]]\n"
            "id = \"fixture_source\"\n"
            "url = \"https://example.invalid/fixture_source.txt\"\n"
            "retrieved = \"2026-06-13\"\n"
            f"sha256 = \"{digest}\"\n"
            f"local_filename = \"{local_filename}\"\n"
            "tags = [\"test\"]\n"
            "note = \"test fixture\"\n",
            encoding="utf-8",
        )
        batch = tmp / "batch.sha256"
        batch.write_text(f"{digest}  {local_filename}\n", encoding="utf-8")
        proc = run([
            sys.executable,
            str(SCRIPT),
            "--lockfile",
            str(lock),
            "--batch-file",
            str(batch),
            "--cache-dir",
            str(cache),
            "--receipt-dir",
            str(receipts),
            "--cache-only",
            "--write-receipts",
            "--retrieved-at-utc",
            "2026-06-13T00:00:00Z",
            "--report-path",
            str(report_path),
            "--write-report",
        ])
        if proc.returncode != 0:
            return fail("cache-only exact-match receipt fixture failed", proc)
        receipt_path = receipts / "fixture_source.receipt.json"
        if not receipt_path.exists() or not report_path.exists():
            return fail("cache-only fixture did not write receipt/report", proc)
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        if receipt.get("observation_type") != "operator_cache_file" or receipt.get("cache_file_sha256_matched") is not True:
            return fail("cache-only fixture wrote wrong receipt semantics", proc)
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if report.get("network_io") is not False or report.get("receipt_written_count") != 1:
            return fail("cache-only fixture report did not prove no-network receipt write", proc)

    # Release-governed cache paths outside evidence/cache/ must be refused.
    proc = run([
        sys.executable,
        str(SCRIPT),
        "--batch-file",
        str(CURRENT_BATCH01),
        "--cache-dir",
        str(ROOT / "artifacts" / "source_byte_receipts"),
        "--cache-only",
        "--limit",
        "1",
    ])
    if proc.returncode == 0:
        return fail("fetcher accepted a release-governed cache directory outside evidence/cache/", proc)
    if "cache-dir is inside the release tree" not in proc.stderr:
        return fail("fetcher rejected unsafe cache dir without the expected diagnostic", proc)

    print("PASS: source-byte batch fetcher offline smoke")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
