#!/usr/bin/env python3
"""Build the source-byte acquisition queue for pinned external sources.

This report is the operational bridge between a lockfile sha256 and a local
source-byte cache.  It does not fetch network resources, does not bundle third-
party bytes, and does not claim authority/currentness.  Instead it makes the
remaining byte-acquisition work finite: every pinned row needs a stable cache
basename, rows with receipts are marked complete, and the rest are ordered for
operator fetch/receipt work.
"""
from __future__ import annotations

import argparse
import json
import sys
import tomllib
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from release_context import archive_version, release_date
from source_byte_receipt_pack import build_report, source_family
from source_byte_priority import source_byte_priority_tier

ROOT = Path(__file__).resolve().parents[1]
VERSION = archive_version(ROOT)
REV = VERSION.removeprefix("v").zfill(4)
RELEASE_DATE = release_date(ROOT)
LOCK = ROOT / "evidence" / "lock" / "external-sources.toml"
REPORT = ROOT / "artifacts" / "reports" / "source-byte-acquisition-queue.json"

BOUNDARY = (
    "Source-byte acquisition queue is an operator work queue for pinned rows. "
    "It is not current voter instruction, not legal advice, not source-byte cache "
    "completeness, not public-release authorization, and not live-pilot approval."
)


def load_sources() -> list[dict[str, Any]]:
    with LOCK.open("rb") as f:
        rows = tomllib.load(f).get("source", [])
    return [r for r in rows if isinstance(r, dict) and str(r.get("id") or "").strip()]


def host_of(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


def short_sha(raw: str) -> str:
    s = str(raw or "").strip().lower()
    return s[:16] if len(s) >= 16 else s


def build_queue() -> dict[str, Any]:
    sources = load_sources()
    receipt_report = build_report()
    receipt_sources = {
        str(row.get("source_id") or "")
        for row in (receipt_report.get("rows") or [])
        if isinstance(row, dict) and row.get("valid") is True
    }

    pinned = [r for r in sources if str(r.get("sha256") or "").strip()]
    rows: list[dict[str, Any]] = []
    duplicate_names: list[str] = []
    name_counts = Counter(str(r.get("local_filename") or "") for r in pinned)
    for name, count in sorted(name_counts.items()):
        if name and count > 1:
            duplicate_names.append(name)

    for src in pinned:
        sid = str(src.get("id") or "").strip()
        tags = [str(t) for t in (src.get("tags") or [])]
        has_receipt = sid in receipt_sources
        priority = source_byte_priority_tier(src, has_receipt=has_receipt)
        rows.append(
            {
                "source_id": sid,
                "receipt_status": "receipt_present" if has_receipt else "receipt_missing",
                "priority_tier": priority,
                "source_family": source_family(src),
                "url_host": host_of(str(src.get("url") or "")),
                "local_filename": str(src.get("local_filename") or ""),
                "sha256_prefix": short_sha(str(src.get("sha256") or "")),
            }
        )

    rows.sort(key=lambda r: (str(r["priority_tier"]), str(r["source_family"]), str(r["source_id"])))

    priority_counts = Counter(str(r["priority_tier"]) for r in rows)
    family_counts = Counter(str(r["source_family"]) for r in rows)
    status_counts = Counter(str(r["receipt_status"]) for r in rows)
    missing_rows = [r for r in rows if r["receipt_status"] == "receipt_missing"]
    missing_local_filename = sorted(str(r.get("id") or "") for r in pinned if not str(r.get("local_filename") or "").strip())

    return {
        "archive_version": VERSION,
        "release_date": RELEASE_DATE,
        "synthetic_only": True,
        "boundary": BOUNDARY,
        "lockfile": "evidence/lock/external-sources.toml",
        "receipt_report": "artifacts/reports/source-byte-receipt-validation-report.json",
        "third_party_bytes_bundled": False,
        "pinned_source_count": len(pinned),
        "receipt_present_count": len(receipt_sources & {str(r.get("id") or "") for r in pinned}),
        "receipt_missing_count": len(missing_rows),
        "pinned_sources_with_local_filename_count": len([r for r in pinned if str(r.get("local_filename") or "").strip()]),
        "missing_local_filename_source_ids": missing_local_filename,
        "duplicate_local_filenames": duplicate_names,
        "priority_counts": dict(sorted(priority_counts.items())),
        "family_counts": dict(sorted(family_counts.items())),
        "receipt_status_counts": dict(sorted(status_counts.items())),
        "next_operator_batch_source_ids": [str(r["source_id"]) for r in missing_rows[:20]],
        "recommended_batch_size": 20,
        "current_batch_file": f"artifacts/source_byte_cache_intake/batches/source-byte-cache-missing-receipts-rev{REV}-batch01.sha256",
        "batch_fetch_command_template": (
            f"python3 scripts/fetch_source_byte_batch.py --batch-file "
            f"artifacts/source_byte_cache_intake/batches/source-byte-cache-missing-receipts-rev{REV}-batch01.sha256 "
            "--cache-dir /path/to/external-source-cache --write-receipts --write-report"
        ),
        "batch_followup_command_template": (
            f"python3 scripts/build_source_byte_batch_followup.py --attempt-report "
            f"artifacts/reports/source-byte-batch-fetch-plan-rev{REV}.json --write"
        ),
        "operator_workplan_command_template": (
            "python3 scripts/build_source_byte_operator_workplan.py --write && "
            f"python3 scripts/check_source_byte_operator_workplan.py"
        ),
        "operator_cache_note": (
            "Keep fetched third-party bytes outside release ZIPs. A local evidence/cache/ "
            "or external source-cache directory can be verified by scripts/verify_external_sources_lock.py."
        ),
        "fetch_command_template": (
            "python3 scripts/fetch_source_sha256.py --source-id {source_id} "
            "--cache-dir /path/to/source-cache --write-receipt"
        ),
        "rows": rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="Write deterministic acquisition queue report")
    ap.add_argument("--json", action="store_true", help="Print deterministic acquisition queue JSON")
    args = ap.parse_args()

    report = build_queue()
    payload = json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n"
    if args.write:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(payload, encoding="utf-8")
    if args.json or not args.write:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
