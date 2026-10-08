#!/usr/bin/env python3
"""Record host-level DNS preflight for queued source-byte acquisition work.

This is an environment report, not a source-byte receipt.  It helps distinguish
"source byte work not attempted" from "source byte work blocked by this
cloudtainer's resolver" before maintainers spend time on individual URLs.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import socket
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from release_context import archive_version, release_date

ROOT = Path(__file__).resolve().parents[1]
VERSION = archive_version(ROOT)
REV = VERSION.removeprefix("v").zfill(4)
QUEUE = ROOT / "artifacts" / "reports" / "source-byte-acquisition-queue.json"
REPORT = ROOT / "artifacts" / "reports" / f"source-byte-dns-preflight-rev{REV}.json"
BOUNDARY = (
    "DNS preflight is a cloudtainer environment observation only. It performs "
    "DNS resolution but no HTTP fetch, writes no receipts, bundles no third-party "
    "bytes, and is not a source-byte receipt, not source-byte cache completeness, "
    "not current voter instruction, not legal advice, and not public-release authorization."
)


def load_queue() -> dict[str, Any]:
    return json.loads(QUEUE.read_text(encoding="utf-8"))


def resolve_host(host: str, timeout_seconds: float) -> tuple[str, str]:
    code = "import socket,sys; socket.getaddrinfo(sys.argv[1],443,type=socket.SOCK_STREAM)"
    try:
        proc = subprocess.run(
            [sys.executable, "-c", code, host],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return "dns_resolution_timeout", f"Timed out after {timeout_seconds:g}s"
    if proc.returncode == 0:
        return "resolved", ""
    detail = (proc.stderr or proc.stdout or "dns resolution failed").strip().splitlines()[-1]
    return "dns_resolution_failed", detail


def preflight_hosts(limit: int, *, timeout_seconds: float = 3.0) -> dict[str, Any]:
    q = load_queue()
    if str(q.get("archive_version") or "") != VERSION:
        raise ValueError(f"queue archive_version {q.get('archive_version')!r} does not match {VERSION!r}")
    missing = [r for r in q.get("rows", []) if isinstance(r, dict) and r.get("receipt_status") == "receipt_missing"]
    selected = missing[:limit]
    by_host: dict[str, list[str]] = {}
    for row in selected:
        host = str(row.get("url_host") or "") or "(missing-host)"
        by_host.setdefault(host, []).append(str(row.get("source_id") or ""))

    rows: list[dict[str, Any]] = []
    for host, source_ids in sorted(by_host.items()):
        if host == "(missing-host)":
            status = "missing_host"
            error = "selected source row has no URL host"
        else:
            status, error = resolve_host(host, timeout_seconds)
        rows.append(
            {
                "host": host,
                "status": status,
                "error": error,
                "queued_source_count_in_selected_batch": len(source_ids),
                "source_ids": source_ids,
            }
        )

    status_counts = Counter(str(r["status"]) for r in rows)
    source_host_counts = Counter(str(r.get("url_host") or "(missing-host)") for r in selected)
    return {
        "archive_version": VERSION,
        "release_date": release_date(ROOT),
        "observed_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "synthetic_only": True,
        "boundary": BOUNDARY,
        "scope": "first-receipt-missing-source-byte-batch-dns-preflight",
        "source_queue_report": "artifacts/reports/source-byte-acquisition-queue.json",
        "network_io": "dns_resolution_only",
        "resolve_timeout_seconds": timeout_seconds,
        "http_fetch_io": False,
        "write_receipts": False,
        "third_party_bytes_bundled": False,
        "selected_missing_source_count": len(selected),
        "selected_unique_host_count": len(rows),
        "selected_source_ids": [str(r.get("source_id") or "") for r in selected],
        "source_host_counts": dict(sorted(source_host_counts.items())),
        "status_counts": dict(sorted(status_counts.items())),
        "rows": rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="DNS preflight for the next source-byte acquisition batch")
    ap.add_argument("--limit", type=int, default=20, help="number of receipt-missing queue rows to inspect")
    ap.add_argument("--report-path", default=str(REPORT), help="output JSON report path")
    ap.add_argument("--resolve-timeout-seconds", type=float, default=3.0, help="per-host resolver timeout")
    ap.add_argument("--write", action="store_true", help="write current DNS preflight report")
    ap.add_argument("--json", action="store_true", help="print JSON report")
    args = ap.parse_args()

    if args.limit <= 0:
        print("ERROR: --limit must be positive", file=sys.stderr)
        return 2
    if args.resolve_timeout_seconds <= 0:
        print("ERROR: --resolve-timeout-seconds must be positive", file=sys.stderr)
        return 2
    try:
        report = preflight_hosts(args.limit, timeout_seconds=args.resolve_timeout_seconds)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    payload = json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n"
    if args.write:
        out = Path(args.report_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload, encoding="utf-8")
    if args.json or not args.write:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
