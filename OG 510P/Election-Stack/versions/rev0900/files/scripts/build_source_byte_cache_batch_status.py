#!/usr/bin/env python3
"""Build the source-byte batch completion status report.

The batch manifest files make the source-byte receipt gap operator-sized, but an
operator still needs a current, deterministic view of which batch is actually
next and whether any batch file has become stale after receipts were added. This
report joins the receipt pack, acquisition queue, and batch manifests into a
small progress ledger without fetching network bytes or bundling third-party
source files.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from release_context import archive_version as _archive_version, release_date as _release_date  # noqa: E402
from source_byte_acquisition_queue import build_queue  # noqa: E402
from source_byte_receipt_pack import build_report as build_receipt_report  # noqa: E402

sys.path.insert(0, str(ROOT / "scripts"))
from build_source_byte_cache_batch_manifests import build_batch_manifests  # noqa: E402

VERSION = _archive_version(ROOT)
REV = VERSION.removeprefix("v").zfill(4)
REPORT = ROOT / "artifacts" / "reports" / f"source-byte-cache-batch-status-rev{REV}.json"
BOUNDARY = (
    "Source-byte cache batch status joins existing source-byte receipts, the "
    "receipt-missing acquisition queue, and current sha256sum batch manifests. "
    "It performs no network I/O, bundles no third-party bytes, is not "
    "source-byte cache completeness, and is not current voter instruction, not "
    "legal advice, not public-release authorization, and not live-pilot approval."
)


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except Exception:
        return str(path)


def source_lookup(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        sid = str(row.get("source_id") or "")
        if sid:
            out[sid] = row
    return out


def build_status() -> dict[str, Any]:
    receipt_report = build_receipt_report()
    queue_report = build_queue()
    batch_report, _files = build_batch_manifests()

    receipt_rows = [r for r in receipt_report.get("rows") or [] if isinstance(r, dict)]
    valid_receipt_sources = {
        str(r.get("source_id") or "")
        for r in receipt_rows
        if r.get("valid") is True and str(r.get("source_id") or "")
    }
    queue_rows = [r for r in queue_report.get("rows") or [] if isinstance(r, dict)]
    queue_by_source = source_lookup(queue_rows)
    queue_missing_sources = {
        str(r.get("source_id") or "")
        for r in queue_rows
        if str(r.get("receipt_status") or "") == "receipt_missing" and str(r.get("source_id") or "")
    }

    batch_source_order: list[str] = []
    duplicate_source_ids: list[str] = []
    seen: set[str] = set()
    batch_rows: list[dict[str, Any]] = []
    stale_receipt_present_sources: list[str] = []

    for batch in batch_report.get("batch_files") or []:
        if not isinstance(batch, dict):
            continue
        source_ids = [str(s) for s in batch.get("source_ids") or [] if str(s)]
        for sid in source_ids:
            if sid in seen:
                duplicate_source_ids.append(sid)
            seen.add(sid)
            batch_source_order.append(sid)
        present = [sid for sid in source_ids if sid in valid_receipt_sources]
        missing = [sid for sid in source_ids if sid not in valid_receipt_sources]
        stale_receipt_present_sources.extend(present)
        priority_counts = Counter(str(queue_by_source.get(sid, {}).get("priority_tier") or "unknown") for sid in source_ids)
        family_counts = Counter(str(queue_by_source.get(sid, {}).get("source_family") or "unknown") for sid in source_ids)
        batch_rows.append(
            {
                "batch_index": int(batch.get("batch_index") or 0),
                "path": str(batch.get("path") or ""),
                "line_count": int(batch.get("line_count") or len(source_ids)),
                "sha256sum_sha256": str(batch.get("sha256sum_sha256") or ""),
                "receipt_present_count": len(present),
                "receipt_missing_count": len(missing),
                "first_missing_source_id": missing[0] if missing else "",
                "last_missing_source_id": missing[-1] if missing else "",
                "priority_counts": dict(sorted(priority_counts.items())),
                "family_counts": dict(sorted(family_counts.items())),
            }
        )

    batched_sources = set(batch_source_order)
    missing_from_batches = sorted(queue_missing_sources - batched_sources)
    unexpected_in_batches = sorted(batched_sources - queue_missing_sources)
    next_batch = next((b for b in batch_rows if int(b.get("receipt_missing_count") or 0) > 0), None)
    first_incomplete_index = int(next_batch.get("batch_index") or 0) if next_batch else 0
    first_incomplete_path = str(next_batch.get("path") or "") if next_batch else ""

    errors: list[str] = []
    if int(receipt_report.get("invalid_receipt_count") or 0) != 0:
        errors.append("receipt_report_has_invalid_receipts")
    if int(batch_report.get("error_count") or 0) != 0:
        errors.append("batch_manifest_report_has_errors")
    if duplicate_source_ids:
        errors.append("duplicate_source_ids_in_batch_files:" + ",".join(sorted(set(duplicate_source_ids))[:10]))
    if missing_from_batches:
        errors.append("queue_missing_sources_not_in_batches:" + ",".join(missing_from_batches[:10]))
    if unexpected_in_batches:
        errors.append("batch_sources_not_currently_receipt_missing:" + ",".join(unexpected_in_batches[:10]))
    if stale_receipt_present_sources:
        errors.append("batch_files_include_receipt_present_sources:" + ",".join(sorted(set(stale_receipt_present_sources))[:10]))
    if len(batch_source_order) != int(batch_report.get("manifest_entry_count") or -1):
        errors.append("batch_status_source_count_mismatch_batch_manifest_entry_count")
    if len(batch_source_order) != int(queue_report.get("receipt_missing_count") or -1):
        errors.append("batch_status_source_count_mismatch_queue_receipt_missing_count")

    status = {
        "archive_version": VERSION,
        "release_date": _release_date(ROOT),
        "synthetic_only": True,
        "boundary": BOUNDARY,
        "network_io": False,
        "third_party_bytes_bundled": False,
        "scope": "receipt-missing-batch-status",
        "receipt_report": rel(ROOT / "artifacts" / "reports" / "source-byte-receipt-validation-report.json"),
        "queue_report": rel(ROOT / "artifacts" / "reports" / "source-byte-acquisition-queue.json"),
        "batch_manifest_report": rel(ROOT / "artifacts" / "reports" / f"source-byte-cache-batch-manifests-rev{REV}.json"),
        "pinned_source_count": int(queue_report.get("pinned_source_count") or 0),
        "receipt_present_count": int(queue_report.get("receipt_present_count") or 0),
        "receipt_missing_count": int(queue_report.get("receipt_missing_count") or 0),
        "valid_receipt_count": int(receipt_report.get("valid_receipt_count") or 0),
        "observed_byte_total": int(receipt_report.get("observed_byte_total") or 0),
        "batch_count": int(batch_report.get("batch_count") or 0),
        "batch_size": int(batch_report.get("batch_size") or 0),
        "batched_source_count": len(batch_source_order),
        "first_incomplete_batch_index": first_incomplete_index,
        "first_incomplete_batch_file": first_incomplete_path,
        "first_incomplete_operator_command": (
            f"python3 scripts/source_byte_receipts_from_cache_batch.py --batch-file {first_incomplete_path} --cache-dir /path/to/external-source-cache --write-receipts"
            if first_incomplete_path
            else ""
        ),
        "all_batches_complete": len(queue_missing_sources) == 0,
        "stale_receipt_present_source_count": len(set(stale_receipt_present_sources)),
        "missing_from_batch_count": len(missing_from_batches),
        "unexpected_in_batch_count": len(unexpected_in_batches),
        "duplicate_source_id_count": len(set(duplicate_source_ids)),
        "error_count": len(errors),
        "errors": errors,
        "batches": batch_rows,
    }
    return status


def main() -> int:
    ap = argparse.ArgumentParser(description="Build source-byte batch completion status report")
    ap.add_argument("--write", action="store_true", help="write deterministic status report")
    ap.add_argument("--json", action="store_true", help="print deterministic status JSON")
    args = ap.parse_args()

    report = build_status()
    payload = json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n"
    if args.write:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(payload, encoding="utf-8")
    if args.json or not args.write:
        sys.stdout.write(payload)
    return 0 if int(report.get("error_count") or 0) == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
