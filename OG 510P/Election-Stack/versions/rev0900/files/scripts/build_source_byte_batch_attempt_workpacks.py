#!/usr/bin/env python3
"""Build classified source-byte retry workpacks from DNS/fetch attempts.

This helper is deliberately no-network. It consumes the current first batch, the
current DNS preflight observation, and any host-slice fetch reports that were
written during an operator attempt. It then emits strict `.sha256` workpacks by
next-action class so a DNS-blocked cloudtainer run does not collapse back into a
single undifferentiated missing-receipts queue.
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from release_context import archive_version as _archive_version, release_date as _release_date  # noqa: E402
from source_byte_workpack_common import parse_strict_sha256sum_batch, sha256_text, sha256sum_line  # noqa: E402

VERSION = _archive_version(ROOT)
REV = VERSION.removeprefix("v").zfill(4)
LOCK = ROOT / "evidence" / "lock" / "external-sources.toml"
DEFAULT_BATCH = ROOT / "artifacts" / "source_byte_cache_intake" / "batches" / f"source-byte-cache-missing-receipts-rev{REV}-batch01.sha256"
DEFAULT_DNS = ROOT / "artifacts" / "reports" / f"source-byte-dns-preflight-rev{REV}.json"
DEFAULT_ATTEMPT_GLOB = str(ROOT / "artifacts" / "reports" / f"source-byte-cache-host-slice-rev{REV}-batch01-*.fetch-report.json")
OUT_DIR = ROOT / "artifacts" / "source_byte_cache_intake" / "attempt_workpacks"
REPORT = ROOT / "artifacts" / "reports" / f"source-byte-batch-attempt-workpacks-rev{REV}.json"
BOUNDARY = (
    "Source-byte batch attempt workpacks are no-network retry/accounting handoffs. "
    "They classify current DNS/fetch attempt reports, write no receipts, bundle no "
    "third-party bytes, do not prove source-byte cache completeness, are not source-byte "
    "cache completeness, and are not current voter instruction, not legal advice, "
    "not public-release authorization, and not live-pilot approval."
)

# Classes that still need a strict sha256sum retry/review workpack.
WORKPACK_CLASSES = {
    "dns_blocked_preflight",
    "dns_blocked_fetch_error",
    "fetch_not_attempted_dns_ok",
    "fetch_not_attempted_no_preflight",
    "transient_network_or_tool_error",
    "source_url_not_found_or_changed",
    "access_denied_or_waf",
    "cache_seed_needed",
    "hash_mismatch_operator_review",
}


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except Exception:
        return str(path)


def parse_batch(batch_file: Path, *, lockfile: Path) -> list[dict[str, Any]]:
    rows = []
    for row in parse_strict_sha256sum_batch(batch_file, lockfile=lockfile):
        rows.append({k: v for k, v in row.items() if k != "lockfile_row"})
    return rows


def line_for(row: dict[str, Any]) -> str:
    return sha256sum_line(row)


def load_dns_statuses(path: Path) -> tuple[dict[str, str], dict[str, str], dict[str, Any]]:
    if not path.exists():
        return {}, {}, {}
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("DNS report root is not an object")
    if str(obj.get("archive_version") or "") != VERSION:
        raise ValueError(f"DNS report archive_version {obj.get('archive_version')!r} does not match {VERSION!r}")
    host_status: dict[str, str] = {}
    host_error: dict[str, str] = {}
    for row in obj.get("rows") or []:
        if not isinstance(row, dict):
            continue
        host = str(row.get("host") or "")
        host_status[host] = str(row.get("status") or "")
        host_error[host] = str(row.get("error") or "")
    return host_status, host_error, obj


def load_attempt_rows(patterns: list[str]) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    attempt_by_source: dict[str, dict[str, Any]] = {}
    reports: list[dict[str, Any]] = []
    paths: list[Path] = []
    for pattern in patterns:
        matches = [Path(p) for p in glob.glob(pattern)] if any(ch in pattern for ch in "*?[") else [Path(pattern)]
        paths.extend(matches)
    for path in sorted(set(paths)):
        if not path.exists():
            continue
        obj = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(obj, dict):
            raise ValueError(f"attempt report root is not an object: {path}")
        if str(obj.get("archive_version") or "") != VERSION:
            raise ValueError(f"attempt report archive_version mismatch in {rel(path)}")
        reports.append(
            {
                "path": rel(path),
                "status_counts": obj.get("status_counts") or {},
                "error_count": obj.get("error_count"),
                "receipt_written_count": obj.get("receipt_written_count"),
                "network_io": obj.get("network_io"),
                "candidate_source_count": obj.get("candidate_source_count"),
            }
        )
        for row in obj.get("rows") or []:
            if not isinstance(row, dict):
                continue
            sid = str(row.get("source_id") or "").strip()
            if not sid:
                continue
            # Sorted path order makes this deterministic. A later path replaces an
            # earlier one for the same source, matching the newest/manual attempt
            # convention if operators name reports with increasing slice numbers.
            attempt_by_source[sid] = {**row, "attempt_report_path": rel(path)}
    return attempt_by_source, reports


def classify_row(attempt: dict[str, Any] | None, *, dns_status: str, dns_error: str) -> tuple[str, str]:
    if attempt is None:
        if dns_status in {"dns_resolution_failed", "dns_resolution_timeout"}:
            return "dns_blocked_preflight", "retry outside this DNS-blocked cloudtainer or after resolver repair"
        if dns_status == "resolved":
            return "fetch_not_attempted_dns_ok", "run host-slice fetcher for this source or host"
        return "fetch_not_attempted_no_preflight", "run DNS preflight or host-slice fetcher"

    status = str(attempt.get("status") or "")
    error = str(attempt.get("error") or "")
    if attempt.get("receipt_written") is True or status == "skipped_existing_receipt":
        return "complete_receipt_present", "none"
    if status in {"fetched_match", "cache_hit_match"}:
        return "write_receipt_from_matched_bytes", "rerun cache-only with --write-receipts for this source"
    if status == "cache_missing":
        return "cache_seed_needed", "place exact bytes in external cache or run network fetch"
    if status in {"cache_hit_mismatch", "fetched_sha256_mismatch"}:
        return "hash_mismatch_operator_review", "review upstream drift, lockfile pin, or cache contamination"
    lowered = (error or dns_error).lower()
    if status in {"dns_preflight_failed"} or "temporary failure in name resolution" in lowered or "name or service not known" in lowered:
        return "dns_blocked_fetch_error", "retry outside this DNS-blocked cloudtainer or after resolver repair"
    if "http error 404" in lowered or "not found" in lowered:
        return "source_url_not_found_or_changed", "review source URL and lockfile pin before retry"
    if "http error 403" in lowered or "http error 401" in lowered or "forbidden" in lowered:
        return "access_denied_or_waf", "fetch from an allowed operator network or review source access policy"
    if "timed out" in lowered or "connection reset" in lowered or "temporarily unavailable" in lowered:
        return "transient_network_or_tool_error", "retry with bounded timeout from a healthy network"
    if status == "plan_only":
        if dns_status in {"dns_resolution_failed", "dns_resolution_timeout"}:
            return "dns_blocked_preflight", "retry outside this DNS-blocked cloudtainer or after resolver repair"
        return "fetch_not_attempted_no_preflight", "run a real fetch/cache attempt"
    if status == "error":
        return "transient_network_or_tool_error", "retry or inspect tool/network error"
    return "fetch_not_attempted_no_preflight", "inspect attempt status and rerun"


def line_for(row: dict[str, Any]) -> str:
    return f"{row['expected_sha256']}  {row['local_filename']}"


def workpack_path(action_class: str) -> Path:
    safe = re.sub(r"[^a-z0-9._-]+", "-", action_class.lower()).strip(".-_") or "unclassified"
    return OUT_DIR / f"source-byte-attempt-workpack-rev{REV}-batch01-{safe}.sha256"


def build_workpacks(*, batch_file: Path, dns_report: Path, attempt_patterns: list[str]) -> tuple[dict[str, Any], dict[Path, str]]:
    batch_rows = parse_batch(batch_file, lockfile=LOCK)
    dns_status, dns_errors, dns_obj = load_dns_statuses(dns_report)
    attempts, attempt_reports = load_attempt_rows(attempt_patterns)

    rows: list[dict[str, Any]] = []
    classes: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in batch_rows:
        sid = str(row["source_id"])
        host = str(row["url_host"])
        attempt = attempts.get(sid)
        action_class, next_action = classify_row(attempt, dns_status=dns_status.get(host, ""), dns_error=dns_errors.get(host, ""))
        out = {
            **row,
            "dns_status": dns_status.get(host, ""),
            "attempt_report_path": str(attempt.get("attempt_report_path") or "") if attempt else "",
            "attempt_status": str(attempt.get("status") or "") if attempt else "not_attempted",
            "attempt_error": str(attempt.get("error") or "") if attempt else "",
            "receipt_written": bool(attempt.get("receipt_written")) if attempt else False,
            "action_class": action_class,
            "next_action": next_action,
            "workpack_required": action_class in WORKPACK_CLASSES,
        }
        rows.append(out)
        if out["workpack_required"]:
            classes[action_class].append(out)

    files: dict[Path, str] = {}
    workpacks: list[dict[str, Any]] = []
    for action_class in sorted(classes):
        class_rows = sorted(classes[action_class], key=lambda r: int(r["line_number"]))
        text = "\n".join(line_for(r) for r in class_rows) + "\n"
        path = workpack_path(action_class)
        files[path] = text
        workpacks.append(
            {
                "action_class": action_class,
                "path": rel(path),
                "line_count": len(class_rows),
                "sha256sum_sha256": "sha256:" + sha256_text(text),
                "source_ids": [str(r["source_id"]) for r in class_rows],
                "operator_fetch_command": (
                    "python3 scripts/fetch_source_byte_batch.py "
                    f"--batch-file {rel(path)} --cache-dir /path/to/external-source-cache "
                    "--write-receipts --write-report"
                ),
            }
        )

    class_counts = Counter(str(r["action_class"]) for r in rows)
    dns_counts = Counter(str(r.get("dns_status") or "missing_dns_status") for r in rows)
    attempted = [r for r in rows if r["attempt_status"] != "not_attempted"]
    unresolved = [r for r in rows if r["workpack_required"]]
    report = {
        "archive_version": VERSION,
        "release_date": _release_date(ROOT),
        "synthetic_only": True,
        "boundary": BOUNDARY,
        "network_io": False,
        "third_party_bytes_bundled": False,
        "scope": "batch01-source-byte-attempt-workpacks",
        "batch_file": rel(batch_file),
        "batch_file_entry_count": len(batch_rows),
        "dns_preflight_report": rel(dns_report) if dns_report.exists() else "",
        "dns_preflight_status_counts": dns_obj.get("status_counts") if isinstance(dns_obj, dict) else {},
        "attempt_report_globs": [p.replace(str(ROOT) + "/", "") for p in attempt_patterns],
        "attempt_reports": attempt_reports,
        "attempt_report_count": len(attempt_reports),
        "attempted_source_count": len(attempted),
        "receipt_written_count": sum(1 for r in rows if r.get("receipt_written") is True),
        "complete_or_receipt_action_count": sum(1 for r in rows if r["action_class"] in {"complete_receipt_present", "write_receipt_from_matched_bytes"}),
        "unresolved_workpack_source_count": len(unresolved),
        "action_class_counts": dict(sorted(class_counts.items())),
        "dns_status_counts_by_source": dict(sorted(dns_counts.items())),
        "workpack_count": len(workpacks),
        "workpacks": workpacks,
        "operator_next_commands": [w["operator_fetch_command"] for w in workpacks[:5]],
        "rows": rows,
    }
    return report, files


def main() -> int:
    ap = argparse.ArgumentParser(description="Build classified source-byte batch01 attempt workpacks")
    ap.add_argument("--batch-file", default=str(DEFAULT_BATCH))
    ap.add_argument("--dns-preflight-report", default=str(DEFAULT_DNS))
    ap.add_argument("--attempt-report", action="append", default=[], help="fetch/cache attempt report path or glob; may be repeated")
    ap.add_argument("--out-dir", default=str(OUT_DIR))
    ap.add_argument("--report-path", default=str(REPORT))
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    patterns = args.attempt_report or [DEFAULT_ATTEMPT_GLOB]
    try:
        report, files = build_workpacks(batch_file=Path(args.batch_file), dns_report=Path(args.dns_preflight_report), attempt_patterns=patterns)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    payload = json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n"
    if args.write:
        out_dir = Path(args.out_dir)
        report_path = Path(args.report_path)
        out_dir.mkdir(parents=True, exist_ok=True)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        for stale in out_dir.glob(f"source-byte-attempt-workpack-rev{REV}-batch01-*.sha256"):
            stale.unlink()
        for path, text in sorted(files.items()):
            target = out_dir / path.name if path.parent != out_dir else path
            target.write_text(text, encoding="utf-8")
        report_path.write_text(payload, encoding="utf-8")
    if args.json or not args.write:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
