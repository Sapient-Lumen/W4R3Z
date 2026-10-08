#!/usr/bin/env python3
"""Validate the current source-byte DNS preflight observation shape.

This gate deliberately does not rerun DNS.  DNS preflight is an environment
observation, so the deterministic release check only proves the shipped report is
current, bounded to the first receipt-missing batch, non-HTTP, non-receipt, and
not a source-byte completion claim.
"""
from __future__ import annotations

import json
import re
import sys
import tomllib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REV = VERSION.removeprefix("v").zfill(4)
REPORT = ROOT / "artifacts" / "reports" / f"source-byte-dns-preflight-rev{REV}.json"
BATCH01 = ROOT / "artifacts" / "source_byte_cache_intake" / "batches" / f"source-byte-cache-missing-receipts-rev{REV}-batch01.sha256"
LOCK = ROOT / "evidence" / "lock" / "external-sources.toml"
ALLOWED_STATUSES = {"resolved", "dns_resolution_failed", "dns_resolution_timeout", "missing_host"}
REQUIRED_BOUNDARY_PHRASES = (
    "environment observation",
    "no HTTP fetch".lower(),
    "writes no receipts",
    "bundles no third-party bytes",
    "not a source-byte receipt",
    "not source-byte cache completeness",
)
SHA256SUM_RE = re.compile(r"^([0-9a-f]{64})  ([A-Za-z0-9._-]+)$")


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except Exception:
        return str(path)


def fail(msg: str) -> int:
    print("FAIL:", msg, file=sys.stderr)
    return 2


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_sources() -> list[dict[str, Any]]:
    with LOCK.open("rb") as f:
        rows = tomllib.load(f).get("source", [])
    return [r for r in rows if isinstance(r, dict)]


def batch_source_ids() -> list[str]:
    sources = load_sources()
    by_sha_file = {
        (str(r.get("sha256") or "").strip().lower(), str(r.get("local_filename") or "").strip()): str(r.get("id") or "").strip()
        for r in sources
        if str(r.get("sha256") or "").strip() and str(r.get("local_filename") or "").strip()
    }
    ids: list[str] = []
    for lineno, raw in enumerate(BATCH01.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        m = SHA256SUM_RE.fullmatch(raw)
        if not m:
            raise ValueError(f"invalid batch line {lineno}")
        sid = by_sha_file.get((m.group(1), m.group(2)))
        if not sid:
            raise ValueError(f"batch line {lineno} not pinned in lockfile")
        ids.append(sid)
    return ids


def main() -> int:
    if not REPORT.exists():
        return fail(f"missing current DNS preflight report: {rel(REPORT)}")
    if not BATCH01.exists():
        return fail(f"missing current batch01 file: {rel(BATCH01)}")
    try:
        obj = load_json(REPORT)
        expected_ids = batch_source_ids()
    except Exception as exc:
        return fail(f"could not load DNS preflight inputs: {exc}")

    errors: list[str] = []
    if obj.get("archive_version") != VERSION:
        errors.append("archive_version does not match VERSION")
    if obj.get("synthetic_only") is not True:
        errors.append("synthetic_only must be true")
    if obj.get("network_io") != "dns_resolution_only":
        errors.append("network_io must be dns_resolution_only")
    if obj.get("http_fetch_io") is not False:
        errors.append("http_fetch_io must be false")
    if obj.get("write_receipts") is not False:
        errors.append("write_receipts must be false")
    if float(obj.get("resolve_timeout_seconds") or 0) <= 0:
        errors.append("resolve_timeout_seconds must be positive")
    if obj.get("third_party_bytes_bundled") is not False:
        errors.append("third_party_bytes_bundled must be false")
    boundary = str(obj.get("boundary") or "").lower()
    for phrase in REQUIRED_BOUNDARY_PHRASES:
        if phrase not in boundary:
            errors.append(f"boundary missing phrase: {phrase}")
    selected = [str(x) for x in (obj.get("selected_source_ids") or [])]
    if selected != expected_ids:
        errors.append("selected_source_ids must match current batch01 source order")
    if int(obj.get("selected_missing_source_count") or -1) != len(expected_ids):
        errors.append("selected_missing_source_count must match current batch01 line count")

    rows = obj.get("rows") or []
    if not isinstance(rows, list) or not rows:
        errors.append("rows must be a non-empty list")
    seen_sources: list[str] = []
    for idx, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            errors.append(f"row {idx} is not an object")
            continue
        status = str(row.get("status") or "")
        if status not in ALLOWED_STATUSES:
            errors.append(f"row {idx} has unknown status {status!r}")
        if status in {"dns_resolution_failed", "dns_resolution_timeout"} and not str(row.get("error") or ""):
            errors.append(f"row {idx} DNS failure lacks error detail")
        ids = [str(x) for x in (row.get("source_ids") or [])]
        if int(row.get("queued_source_count_in_selected_batch") or -1) != len(ids):
            errors.append(f"row {idx} source count mismatch")
        seen_sources.extend(ids)
    if sorted(seen_sources) != sorted(expected_ids):
        errors.append("DNS preflight rows do not cover exactly the current batch01 source ids")

    if errors:
        for err in errors:
            print("ERROR:", err, file=sys.stderr)
        return 2
    print(
        "PASS: source-byte DNS preflight shape "
        f"({VERSION}, hosts={obj.get('selected_unique_host_count')}, statuses={obj.get('status_counts')})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
