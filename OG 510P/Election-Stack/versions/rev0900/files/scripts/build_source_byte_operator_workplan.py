#!/usr/bin/env python3
"""Build the source-byte operator workplan for the current release.

The archive cannot complete source-byte acquisition inside a DNS-blocked
cloudtainer.  This no-network builder turns the current receipt/batch/DNS state
into a finite execution plan for a network-capable operator and a safe return
path for exact-match receipts.  It intentionally writes no receipts and bundles
no third-party bytes.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from release_context import archive_version as _archive_version, release_date as _release_date  # noqa: E402
from source_byte_workpack_common import parse_strict_sha256sum_batch  # noqa: E402

VERSION = _archive_version(ROOT)
REV = VERSION.removeprefix("v").zfill(4)
LOCK = ROOT / "evidence" / "lock" / "external-sources.toml"
REPORT = ROOT / "artifacts" / "reports" / f"source-byte-operator-workplan-rev{REV}.json"
STATUS_REPORT = ROOT / "artifacts" / "reports" / f"source-byte-cache-batch-status-rev{REV}.json"
BATCH_MANIFEST_REPORT = ROOT / "artifacts" / "reports" / f"source-byte-cache-batch-manifests-rev{REV}.json"
DNS_REPORT = ROOT / "artifacts" / "reports" / f"source-byte-dns-preflight-rev{REV}.json"
ATTEMPT_WORKPACK_REPORT = ROOT / "artifacts" / "reports" / f"source-byte-batch-attempt-workpacks-rev{REV}.json"
HOST_SLICE_REPORT = ROOT / "artifacts" / "reports" / f"source-byte-batch-host-slices-rev{REV}.json"
QUEUE_REPORT = ROOT / "artifacts" / "reports" / "source-byte-acquisition-queue.json"
RECEIPT_REPORT = ROOT / "artifacts" / "reports" / "source-byte-receipt-validation-report.json"
BOUNDARY = (
    "Source-byte operator workplan is no-network acquisition accounting and return-path guidance. "
    "It writes no receipts, bundles no third-party bytes, does not prove source-byte cache "
    "completeness, is not source-byte cache completeness, and is not current voter instruction, "
    "not legal advice, not public-release authorization, and not live-pilot approval."
)


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except Exception:
        return str(path)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def maybe_load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return load_json(path)


def batch_summary(row: dict[str, Any]) -> dict[str, Any]:
    path = ROOT / str(row.get("path") or "")
    parsed = parse_strict_sha256sum_batch(path, lockfile=LOCK)
    hosts = Counter(str(r.get("url_host") or "no-host") for r in parsed)
    source_ids = [str(r.get("source_id") or "") for r in parsed]
    dominant_host = ""
    dominant_count = 0
    if hosts:
        dominant_host, dominant_count = sorted(hosts.items(), key=lambda kv: (-kv[1], kv[0]))[0]
    return {
        "batch_index": int(row.get("batch_index") or 0),
        "path": rel(path),
        "line_count": len(parsed),
        "first_source_id": source_ids[0] if source_ids else "",
        "last_source_id": source_ids[-1] if source_ids else "",
        "host_count": len(hosts),
        "dominant_host": dominant_host,
        "dominant_host_count": dominant_count,
        "host_counts": dict(sorted(hosts.items())),
        "source_ids": source_ids,
        "cache_return_command": (
            "python3 scripts/source_byte_receipts_from_cache_batch.py "
            f"--batch-file {rel(path)} --cache-dir /path/to/external-source-cache "
            "--write-receipts --write-report"
        ),
        "fetch_command": (
            "python3 scripts/fetch_source_byte_batch.py "
            f"--batch-file {rel(path)} --cache-dir /path/to/external-source-cache "
            "--write-receipts --write-report"
        ),
    }


def _current_workpacks(workpack_report: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in workpack_report.get("workpacks") or []:
        if not isinstance(row, dict):
            continue
        out.append(
            {
                "action_class": str(row.get("action_class") or ""),
                "path": str(row.get("path") or ""),
                "line_count": int(row.get("line_count") or 0),
                "source_ids": [str(s) for s in (row.get("source_ids") or [])],
                "operator_fetch_command": str(row.get("operator_fetch_command") or ""),
            }
        )
    return sorted(out, key=lambda r: (-int(r.get("line_count") or 0), str(r.get("action_class") or ""), str(r.get("path") or "")))


def _host_slices(host_report: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in host_report.get("host_slices") or []:
        if not isinstance(row, dict):
            continue
        out.append(
            {
                "host_slice_index": int(row.get("host_slice_index") or 0),
                "url_host": str(row.get("url_host") or ""),
                "path": str(row.get("path") or ""),
                "line_count": int(row.get("line_count") or 0),
                "source_ids": [str(s) for s in (row.get("source_ids") or [])],
                "operator_fetch_command": str(row.get("operator_fetch_command") or ""),
            }
        )
    return sorted(out, key=lambda r: (-int(r.get("line_count") or 0), int(r.get("host_slice_index") or 0)))


def build_workplan() -> dict[str, Any]:
    status = load_json(STATUS_REPORT)
    batches = load_json(BATCH_MANIFEST_REPORT)
    queue = load_json(QUEUE_REPORT)
    receipt = load_json(RECEIPT_REPORT)
    dns = maybe_load_json(DNS_REPORT)
    attempt = maybe_load_json(ATTEMPT_WORKPACK_REPORT)
    host = maybe_load_json(HOST_SLICE_REPORT)

    batch_summaries = [batch_summary(b) for b in (batches.get("batch_files") or []) if isinstance(b, dict)]
    all_hosts = Counter()
    for b in batch_summaries:
        all_hosts.update({str(k): int(v) for k, v in (b.get("host_counts") or {}).items()})

    workpacks = _current_workpacks(attempt)
    host_slices = _host_slices(host)
    dominant_host_slice = host_slices[0] if host_slices else {}
    first_batch = batch_summaries[0] if batch_summaries else {}
    missing = int(status.get("receipt_missing_count") or 0)
    present = int(status.get("receipt_present_count") or 0)
    pinned = int(status.get("pinned_source_count") or 0)
    batch01_count = int(first_batch.get("line_count") or 0)
    post_batch01_remaining = max(0, missing - batch01_count)

    command_plan: list[dict[str, Any]] = []
    if dominant_host_slice:
        command_plan.append(
            {
                "step": 1,
                "name": "highest-yield-host-slice-fetch",
                "why": "Start with the largest same-host slice to avoid one mixed-host batch hiding per-host failures.",
                "path": str(dominant_host_slice.get("path") or ""),
                "expected_source_count": int(dominant_host_slice.get("line_count") or 0),
                "command": str(dominant_host_slice.get("operator_fetch_command") or ""),
            }
        )
    for idx, w in enumerate(workpacks[:3], start=2 if command_plan else 1):
        command_plan.append(
            {
                "step": idx,
                "name": f"classified-workpack-{w.get('action_class')}",
                "why": "Retry only rows in the same action class rather than rerunning an undifferentiated batch.",
                "path": str(w.get("path") or ""),
                "expected_source_count": int(w.get("line_count") or 0),
                "command": str(w.get("operator_fetch_command") or ""),
            }
        )
    next_step = len(command_plan) + 1
    if first_batch:
        command_plan.append(
            {
                "step": next_step,
                "name": "return-batch01-cache-into-receipts",
                "why": "After external bytes are present, write only exact-SHA-256 matching receipts from the external cache.",
                "path": str(first_batch.get("path") or ""),
                "expected_source_count": batch01_count,
                "command": str(first_batch.get("cache_return_command") or ""),
            }
        )
        next_step += 1
    command_plan.append(
        {
            "step": next_step,
            "name": "regenerate-source-byte-status",
            "why": "Refresh queue, intake, batch manifests, batch status, follow-up/workpack reports, then rerun targeted gates before moving to batch02.",
            "path": "",
            "expected_source_count": 0,
            "command": "python3 tools/source_byte_acquisition_queue.py --write && python3 scripts/build_source_byte_cache_intake_manifest.py --write && python3 scripts/build_source_byte_cache_batch_manifests.py --write && python3 scripts/build_source_byte_cache_batch_status.py --write",
        }
    )

    blockers: list[str] = []
    if dns:
        dns_counts = dns.get("status_counts") or {}
        dns_blocked = sum(int(dns_counts.get(k) or 0) for k in ("dns_resolution_failed", "dns_resolution_timeout"))
        if dns_blocked > 0:
            blockers.append("cloudtainer_dns_resolution_blocked_for_batch01_hosts")
    if missing:
        blockers.append("source_byte_receipts_missing")
    if not workpacks:
        blockers.append("no_current_attempt_workpacks")

    report = {
        "archive_version": VERSION,
        "release_date": _release_date(ROOT),
        "synthetic_only": True,
        "boundary": BOUNDARY,
        "network_io": False,
        "third_party_bytes_bundled": False,
        "scope": "source-byte-operator-completion-workplan",
        "source_reports": {
            "queue_report": rel(QUEUE_REPORT),
            "receipt_report": rel(RECEIPT_REPORT),
            "batch_status_report": rel(STATUS_REPORT),
            "batch_manifest_report": rel(BATCH_MANIFEST_REPORT),
            "dns_preflight_report": rel(DNS_REPORT) if DNS_REPORT.exists() else "",
            "attempt_workpack_report": rel(ATTEMPT_WORKPACK_REPORT) if ATTEMPT_WORKPACK_REPORT.exists() else "",
            "host_slice_report": rel(HOST_SLICE_REPORT) if HOST_SLICE_REPORT.exists() else "",
        },
        "receipt_summary": {
            "pinned_source_count": pinned,
            "receipt_present_count": present,
            "valid_receipt_count": int(receipt.get("valid_receipt_count") or 0),
            "receipt_missing_count": missing,
            "completion_percent": round((present / pinned) * 100, 2) if pinned else 0.0,
            "all_batches_complete": bool(status.get("all_batches_complete")),
        },
        "blocking_conditions": blockers,
        "dns_preflight_status_counts": dns.get("status_counts") if isinstance(dns, dict) else {},
        "attempt_action_class_counts": attempt.get("action_class_counts") if isinstance(attempt, dict) else {},
        "first_incomplete_batch_index": int(status.get("first_incomplete_batch_index") or 0),
        "first_incomplete_batch_file": str(status.get("first_incomplete_batch_file") or ""),
        "batch_count": len(batch_summaries),
        "batch01_source_count": batch01_count,
        "post_batch01_remaining_source_count": post_batch01_remaining,
        "all_missing_host_counts": dict(sorted(all_hosts.items(), key=lambda kv: (-kv[1], kv[0]))),
        "current_batch_summaries": batch_summaries,
        "highest_yield_host_slice": dominant_host_slice,
        "classified_workpacks": workpacks,
        "operator_command_plan": command_plan,
        "operator_return_contract": {
            "cache_dir_must_be_outside_release_zip": True,
            "expected_cache_key": "lockfile local_filename basename",
            "receipt_write_condition": "observed SHA-256 exactly equals evidence/lock/external-sources.toml sha256 for the selected source",
            "forbidden_shortcut": "do not write receipts from URLs, snippets, browser-rendered text, or partial downloads",
            "full_missing_cache_scan_command": "python3 scripts/source_byte_receipts_from_cache_batch.py --cache-dir /path/to/external-source-cache --scope missing-receipts --write-receipts --write-report",
        },
        "no_go_reason": "GO_SYNTHETIC_RELEASE_ONLY while any pinned source-byte receipt is missing or externally fetched bytes have not been verified by exact SHA-256.",
    }
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description="Build source-byte operator completion workplan")
    ap.add_argument("--write", action="store_true", help="write deterministic report")
    ap.add_argument("--json", action="store_true", help="print deterministic JSON")
    args = ap.parse_args()
    try:
        report = build_workplan()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    payload = json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n"
    if args.write:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(payload, encoding="utf-8")
    if args.json or not args.write:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
