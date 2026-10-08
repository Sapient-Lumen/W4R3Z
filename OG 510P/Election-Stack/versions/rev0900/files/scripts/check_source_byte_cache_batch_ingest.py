#!/usr/bin/env python3
"""Check source-byte cache batch-ingest readiness.

The one-by-one cache receipt helper was useful but too slow for the remaining
105 pinned-source queue.  This gate keeps a batch scanner/writer available and
proves two important properties without bundling third-party bytes:
- the shipped readiness report is deterministic for a clean no-cache release;
- a temp matching cache file produces an operator_cache_file receipt, while a
  wrong byte file is reported as a mismatch and does not become a receipt.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
SCRIPT = ROOT / "scripts" / "source_byte_receipts_from_cache_batch.py"
def current_revision_token() -> str:
    return VERSION.removeprefix("v").zfill(4)


REPORT = ROOT / "artifacts" / "reports" / f"source-byte-cache-batch-ingest-rev{current_revision_token()}.json"
QUEUE_REPORT = ROOT / "artifacts" / "reports" / "source-byte-acquisition-queue.json"
RECEIPT_REPORT = ROOT / "artifacts" / "reports" / "source-byte-receipt-validation-report.json"

REQUIRED_BOUNDARY_PHRASES = (
    "not current voter instruction",
    "not legal advice",
    "not source-byte cache completeness",
    "bundles no third-party bytes",
)


def run_json(cmd: list[str], *, cwd: Path = ROOT) -> dict:
    proc = subprocess.run(
        cmd,
        cwd=cwd,
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
    try:
        return json.loads(proc.stdout)
    except Exception as exc:
        print(f"ERROR: could not parse JSON from {' '.join(cmd)}: {exc}", file=sys.stderr)
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        raise SystemExit(2)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def smoke_temp_lockfile() -> list[str]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="source-cache-batch-smoke-") as td:
        tmp = Path(td)
        lock = tmp / "external-sources.toml"
        cache = tmp / "cache"
        receipts = tmp / "receipts"
        cache.mkdir()
        good_payload = "sample source bytes\n"
        bad_payload = "wrong source bytes\n"
        good_sha = sha256_text(good_payload)
        write_text(cache / "sample-good.txt", good_payload)
        write_text(cache / "sample-bad.txt", bad_payload)
        write_text(
            lock,
            """
[[source]]
id = "sample_good"
url = "https://example.invalid/sample-good.txt"
retrieved = "2026-06-13"
sha256 = "{good_sha}"
local_filename = "sample-good.txt"
tags = ["eac"]
note = "temporary smoke fixture only"

[[source]]
id = "sample_bad"
url = "https://example.invalid/sample-bad.txt"
retrieved = "2026-06-13"
sha256 = "{good_sha}"
local_filename = "sample-bad.txt"
tags = ["eac"]
note = "temporary smoke fixture only"
""".format(good_sha=good_sha).lstrip(),
        )
        report = run_json([
            sys.executable,
            str(SCRIPT),
            "--lockfile",
            str(lock),
            "--cache-dir",
            str(cache),
            "--receipt-dir",
            str(receipts),
            "--scope",
            "all-pinned",
            "--write-receipts",
            "--retrieved-at-utc",
            "2026-06-13T04:30:00Z",
            "--json",
        ])
        if int(report.get("matched_cache_file_count") or 0) != 1:
            errors.append("batch ingest smoke expected exactly one matched cache file")
        if int(report.get("mismatched_cache_file_count") or 0) != 1:
            errors.append("batch ingest smoke expected exactly one mismatched cache file")
        if int(report.get("written_receipt_count") or 0) != 1:
            errors.append("batch ingest smoke expected exactly one written receipt")
        receipt = receipts / "sample_good.receipt.json"
        if not receipt.exists():
            errors.append("batch ingest smoke did not write matching receipt")
        else:
            obj = load_json(receipt)
            if obj.get("observation_type") != "operator_cache_file":
                errors.append("batch ingest smoke receipt has wrong observation_type")
            if obj.get("fetch_status") != "not_applicable_cache_file":
                errors.append("batch ingest smoke receipt has wrong fetch_status")
            if obj.get("observed_sha256") != good_sha or obj.get("lockfile_sha256") != good_sha:
                errors.append("batch ingest smoke receipt does not bind observed and lockfile sha256")
            if obj.get("bundled_bytes") is not False:
                errors.append("batch ingest smoke receipt must state bundled_bytes=false")
        if (receipts / "sample_bad.receipt.json").exists():
            errors.append("batch ingest smoke wrote a receipt for mismatched bytes")

        original_receipt = receipt.read_text(encoding="utf-8") if receipt.exists() else ""
        rerun = run_json([
            sys.executable,
            str(SCRIPT),
            "--lockfile",
            str(lock),
            "--cache-dir",
            str(cache),
            "--receipt-dir",
            str(receipts),
            "--scope",
            "all-pinned",
            "--write-receipts",
            "--retrieved-at-utc",
            "2026-06-13T04:31:00Z",
            "--json",
        ])
        if int(rerun.get("written_receipt_count") or 0) != 0:
            errors.append("batch ingest smoke rewrote an existing receipt without --force")
        if "sample_good" not in set(rerun.get("skipped_existing_receipt_source_ids") or []):
            errors.append("batch ingest smoke did not report skipped existing receipt")
        if receipt.exists() and receipt.read_text(encoding="utf-8") != original_receipt:
            errors.append("batch ingest smoke changed an existing receipt without --force")
    return errors


def main() -> int:
    errors: list[str] = []
    for path, label in (
        (SCRIPT, "batch ingest script"),
        (REPORT, "batch ingest readiness report"),
        (QUEUE_REPORT, "source-byte acquisition queue"),
        (RECEIPT_REPORT, "source-byte receipt report"),
    ):
        if not path.exists():
            errors.append(f"missing {label}: {path.relative_to(ROOT)}")
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2

    generated = run_json([
        sys.executable,
        str(SCRIPT),
        "--assume-empty-cache",
        "--scope",
        "missing-receipts",
        "--json",
    ])
    shipped = load_json(REPORT)
    if generated != shipped:
        errors.append("current source-byte-cache-batch-ingest report is stale; run scripts/source_byte_receipts_from_cache_batch.py --assume-empty-cache --write-report")

    queue = load_json(QUEUE_REPORT)
    receipt = load_json(RECEIPT_REPORT)
    if shipped.get("archive_version") != VERSION:
        errors.append("batch ingest report archive_version does not match VERSION")
    if shipped.get("synthetic_only") is not True:
        errors.append("batch ingest report must carry synthetic_only=true")
    if shipped.get("network_io") is not False:
        errors.append("batch ingest report must state network_io=false")
    if shipped.get("third_party_bytes_bundled") is not False:
        errors.append("batch ingest report must not bundle third-party bytes")
    if shipped.get("assume_empty_cache") is not True:
        errors.append("release readiness report must be generated with assume_empty_cache=true")
    boundary = str(shipped.get("boundary") or "").lower()
    for phrase in REQUIRED_BOUNDARY_PHRASES:
        if phrase not in boundary:
            errors.append(f"batch ingest boundary missing phrase: {phrase}")

    if int(shipped.get("pinned_source_count") or 0) != int(queue.get("pinned_source_count") or -1):
        errors.append("batch ingest pinned_source_count must equal acquisition queue")
    if int(shipped.get("existing_receipt_source_count") or 0) != int(receipt.get("receipt_covered_pinned_source_count") or -1):
        errors.append("batch ingest existing receipt count must equal receipt report coverage")
    if int(shipped.get("candidate_source_count") or 0) != int(queue.get("receipt_missing_count") or -1):
        errors.append("batch ingest candidate count must equal receipt-missing queue count")
    if int(shipped.get("matched_cache_file_count", -1)) != 0:
        errors.append("release readiness report must not claim matched cache files")
    if int(shipped.get("would_write_receipt_count", -1)) != 0:
        errors.append("release readiness report must not claim receipts would be written")
    status_counts = shipped.get("cache_status_counts") or {}
    if int(status_counts.get("cache_not_inspected_assumed_empty") or 0) != int(shipped.get("candidate_source_count") or -1):
        errors.append("all release readiness candidates should be cache_not_inspected_assumed_empty")
    rows = shipped.get("rows") or []
    if len(rows) != int(shipped.get("candidate_source_count") or -1):
        errors.append("batch ingest rows length does not match candidate_source_count")
    for row in rows[:10]:
        if not isinstance(row, dict):
            errors.append("batch ingest row is not an object")
            continue
        if row.get("existing_receipt") is True:
            errors.append("missing-receipts scope row unexpectedly has existing_receipt=true")
        if row.get("cache_status") != "cache_not_inspected_assumed_empty":
            errors.append("release row has unexpected cache_status")

    errors.extend(smoke_temp_lockfile())

    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2
    print(
        "PASS: source-byte cache batch ingest "
        f"({VERSION}, candidates={shipped['candidate_source_count']}, matched={shipped['matched_cache_file_count']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
