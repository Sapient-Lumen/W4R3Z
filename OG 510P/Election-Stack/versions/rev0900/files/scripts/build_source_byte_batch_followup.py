#!/usr/bin/env python3
"""Build a strict follow-up sha256sum file from a source-byte batch attempt report.

A real network/cache attempt can partially succeed: some sources may fetch and
match, some may already have receipts, and some may fail or remain unattempted.
This helper turns the attempt report back into a finite next action without
hand-editing governed batch files. It performs no network I/O and writes no
receipts; it only emits a new strict `.sha256` handoff for rows whose bytes still
need acquisition or verification, plus JSON accounting for receipt-only follow-up.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tomllib
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from release_context import archive_version as _archive_version, release_date as _release_date  # noqa: E402

VERSION = _archive_version(ROOT)
REV = VERSION.removeprefix("v").zfill(4)
LOCK = ROOT / "evidence" / "lock" / "external-sources.toml"
DEFAULT_BATCH = ROOT / "artifacts" / "source_byte_cache_intake" / "batches" / f"source-byte-cache-missing-receipts-rev{REV}-batch01.sha256"
DEFAULT_ATTEMPT_REPORT = ROOT / "artifacts" / "reports" / f"source-byte-batch-fetch-plan-rev{REV}.json"
DEFAULT_FOLLOWUP_DIR = ROOT / "artifacts" / "source_byte_cache_intake" / "followups"
DEFAULT_SHA256SUM = DEFAULT_FOLLOWUP_DIR / f"source-byte-cache-followup-rev{REV}-batch01-unresolved.sha256"
DEFAULT_REPORT = ROOT / "artifacts" / "reports" / f"source-byte-batch-followup-rev{REV}.json"

SAFE_BASENAME_RE = re.compile(r"^[A-Za-z0-9._-]+$")
SHA256SUM_LINE_RE = re.compile(r"^([0-9a-f]{64})  ([A-Za-z0-9._-]+)$")
SOURCE_ID_RE = re.compile(r"^[a-z0-9_]+$")
BYTE_MATCH_STATUSES = {"fetched_match", "cache_hit_match"}
RECEIPT_COMPLETE_STATUSES = {"skipped_existing_receipt"}
BOUNDARY = (
    "Source-byte batch follow-up is a no-network resumability handoff. It turns "
    "a batch attempt report into the next strict sha256sum file for unresolved "
    "byte acquisition only; it writes no receipts, bundles no third-party bytes, "
    "does not prove source-byte cache completeness, is not source-byte cache "
    "completeness, and is not current voter instruction, not legal advice, "
    "not public-release authorization, and not "
    "live-pilot approval."
)


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except Exception:
        return str(path)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def safe_basename(raw: Any) -> bool:
    s = str(raw or "")
    if not s or s.startswith(".") or "/" in s or "\\" in s or ".." in s:
        return False
    return bool(SAFE_BASENAME_RE.fullmatch(s))


def parse_batch_file(batch_file: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    seen_names: set[str] = set()
    for lineno, raw in enumerate(batch_file.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        m = SHA256SUM_LINE_RE.fullmatch(raw)
        if not m:
            raise ValueError(f"invalid sha256sum line {batch_file}:{lineno}")
        expected_sha, local_filename = m.group(1), m.group(2)
        if not safe_basename(local_filename):
            raise ValueError(f"unsafe local filename {batch_file}:{lineno}")
        key = (expected_sha, local_filename)
        if key in seen:
            raise ValueError(f"duplicate sha256sum line {batch_file}:{lineno}")
        if local_filename in seen_names:
            raise ValueError(f"duplicate local filename {batch_file}:{lineno}")
        seen.add(key)
        seen_names.add(local_filename)
        entries.append({"expected_sha256": expected_sha, "local_filename": local_filename, "line_number": lineno})
    if not entries:
        raise ValueError(f"empty batch file: {batch_file}")
    return entries


def load_sources(lockfile: Path) -> list[dict[str, Any]]:
    with lockfile.open("rb") as f:
        rows = tomllib.load(f).get("source", [])
    return [r for r in rows if isinstance(r, dict) and str(r.get("id") or "").strip()]


def host_of(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


def source_index(lockfile: Path) -> dict[tuple[str, str], dict[str, Any]]:
    out: dict[tuple[str, str], dict[str, Any]] = {}
    duplicates: list[str] = []
    for row in load_sources(lockfile):
        sha = str(row.get("sha256") or "").strip().lower()
        local_filename = str(row.get("local_filename") or "").strip()
        if not sha or not local_filename:
            continue
        key = (sha, local_filename)
        if key in out:
            duplicates.append(local_filename)
        out[key] = row
    if duplicates:
        raise ValueError("duplicate pinned sha/local entries in lockfile: " + ",".join(sorted(duplicates)[:10]))
    return out


def load_attempt_report(path: Path, *, allow_version_mismatch: bool) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("attempt report root must be a JSON object")
    report_version = str(obj.get("archive_version") or "")
    if report_version != VERSION and not allow_version_mismatch:
        raise ValueError(f"attempt report archive_version {report_version!r} does not match current {VERSION!r}")
    rows = obj.get("rows")
    if not isinstance(rows, list):
        raise ValueError("attempt report must contain rows[]")
    return obj


def attempt_index(report: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    out: dict[tuple[str, str], dict[str, Any]] = {}
    duplicates: list[str] = []
    for idx, row in enumerate(report.get("rows") or [], start=1):
        if not isinstance(row, dict):
            raise ValueError(f"attempt report row {idx} is not an object")
        sha = str(row.get("expected_sha256") or "").strip().lower()
        local_filename = str(row.get("local_filename") or "").strip()
        if not re.fullmatch(r"[0-9a-f]{64}", sha):
            raise ValueError(f"attempt report row {idx} has invalid expected_sha256")
        if not safe_basename(local_filename):
            raise ValueError(f"attempt report row {idx} has unsafe local_filename")
        key = (sha, local_filename)
        if key in out:
            duplicates.append(local_filename)
        out[key] = row
    if duplicates:
        raise ValueError("duplicate attempt report sha/local rows: " + ",".join(sorted(duplicates)[:10]))
    return out


def csv_source_ids(ids: list[str], *, limit: int = 25) -> str:
    safe = [sid for sid in ids if SOURCE_ID_RE.fullmatch(sid)]
    return ",".join(safe[:limit])


def build_followup(
    *,
    batch_file: Path,
    attempt_report_path: Path,
    lockfile: Path,
    followup_sha256sum_path: Path,
    allow_version_mismatch: bool = False,
) -> tuple[dict[str, Any], str]:
    batch_entries = parse_batch_file(batch_file)
    attempt_report = load_attempt_report(attempt_report_path, allow_version_mismatch=allow_version_mismatch)
    attempts = attempt_index(attempt_report)
    sources = source_index(lockfile)

    rows: list[dict[str, Any]] = []
    followup_entries: list[dict[str, Any]] = []
    receipt_action_source_ids: list[str] = []
    completed_source_ids: list[str] = []
    not_attempted_count = 0

    for entry in batch_entries:
        key = (str(entry["expected_sha256"]), str(entry["local_filename"]))
        src = sources.get(key)
        if src is None:
            raise ValueError(f"batch entry not pinned in lockfile: {entry['local_filename']}")
        sid = str(src.get("id") or "").strip()
        attempt = attempts.get(key)
        status = "not_attempted_in_report"
        if attempt is not None:
            status = str(attempt.get("status") or "").strip() or "missing_status"
        else:
            not_attempted_count += 1

        receipt_written = bool(attempt.get("receipt_written")) if attempt is not None else False
        receipt_preexisting = bool(attempt.get("receipt_preexisting")) if attempt is not None else False
        byte_match = status in BYTE_MATCH_STATUSES
        receipt_complete = status in RECEIPT_COMPLETE_STATUSES or receipt_written or receipt_preexisting
        followup_needed = not byte_match and not receipt_complete
        receipt_action_required = byte_match and not receipt_complete
        if followup_needed:
            followup_entries.append(entry)
            next_action = "fetch_or_cache_required"
        elif receipt_action_required:
            receipt_action_source_ids.append(sid)
            next_action = "write_receipt_from_matched_cache"
        else:
            completed_source_ids.append(sid)
            next_action = "none_receipt_present_or_written"

        rows.append(
            {
                "source_id": sid,
                "url_host": host_of(str(src.get("url") or "")),
                "line_number": int(entry["line_number"]),
                "local_filename": str(entry["local_filename"]),
                "expected_sha256": str(entry["expected_sha256"]),
                "attempt_status": status,
                "byte_match": byte_match,
                "receipt_complete": receipt_complete,
                "followup_needed": followup_needed,
                "receipt_action_required": receipt_action_required,
                "next_action": next_action,
            }
        )

    followup_lines = [f"{e['expected_sha256']}  {e['local_filename']}" for e in followup_entries]
    sha_text = "\n".join(followup_lines) + ("\n" if followup_lines else "")
    attempt_status_counts = Counter(str(r["attempt_status"]) for r in rows)
    next_action_counts = Counter(str(r["next_action"]) for r in rows)
    host_counts = Counter(str(r["url_host"]) for r in rows if r.get("followup_needed"))

    fetch_cmd = (
        "python3 scripts/fetch_source_byte_batch.py "
        f"--batch-file {rel(followup_sha256sum_path)} "
        "--cache-dir /path/to/external-source-cache --write-receipts --write-report"
    )
    receipt_only_cmd = ""
    if receipt_action_source_ids:
        receipt_only_cmd = (
            "python3 scripts/fetch_source_byte_batch.py "
            f"--batch-file {rel(batch_file)} --cache-dir /path/to/external-source-cache "
            "--cache-only --write-receipts --only-source-ids "
            + csv_source_ids(receipt_action_source_ids)
        )

    report = {
        "archive_version": VERSION,
        "release_date": _release_date(ROOT),
        "synthetic_only": True,
        "boundary": BOUNDARY,
        "network_io": False,
        "third_party_bytes_bundled": False,
        "scope": "source-byte-batch-followup",
        "lockfile": rel(lockfile),
        "batch_file": rel(batch_file),
        "batch_file_entry_count": len(batch_entries),
        "batch_file_sha256sum_sha256": "sha256:" + sha256_bytes(batch_file.read_bytes()),
        "attempt_report": rel(attempt_report_path),
        "attempt_report_archive_version": str(attempt_report.get("archive_version") or ""),
        "attempt_report_status_counts": dict(sorted((attempt_report.get("status_counts") or {}).items())),
        "followup_sha256sum_path": rel(followup_sha256sum_path),
        "followup_sha256sum_sha256": "sha256:" + sha256_text(sha_text),
        "original_batch_entry_count": len(batch_entries),
        "followup_entry_count": len(followup_entries),
        "not_attempted_count": not_attempted_count,
        "byte_match_count": sum(1 for r in rows if r.get("byte_match") is True),
        "receipt_complete_count": sum(1 for r in rows if r.get("receipt_complete") is True),
        "receipt_action_required_count": len(receipt_action_source_ids),
        "completed_source_ids": completed_source_ids,
        "receipt_action_required_source_ids": receipt_action_source_ids,
        "attempt_status_counts": dict(sorted(attempt_status_counts.items())),
        "next_action_counts": dict(sorted(next_action_counts.items())),
        "followup_host_counts": dict(sorted(host_counts.items())),
        "operator_next_commands": [cmd for cmd in [fetch_cmd if followup_entries else "", receipt_only_cmd] if cmd],
        "rows": rows,
    }
    return report, sha_text


def main() -> int:
    ap = argparse.ArgumentParser(description="Build a source-byte follow-up batch from a fetch/cache attempt report")
    ap.add_argument("--batch-file", default=str(DEFAULT_BATCH), help="original strict sha256sum batch file")
    ap.add_argument("--attempt-report", default=str(DEFAULT_ATTEMPT_REPORT), help="fetch/cache attempt report JSON")
    ap.add_argument("--lockfile", default=str(LOCK), help="external-sources.toml path")
    ap.add_argument("--followup-sha256sum-path", default=str(DEFAULT_SHA256SUM), help="output sha256sum path for unresolved rows")
    ap.add_argument("--report-path", default=str(DEFAULT_REPORT), help="output JSON report path")
    ap.add_argument("--allow-version-mismatch", action="store_true", help="diagnostic only: permit attempt report archive_version to differ from VERSION")
    ap.add_argument("--write", action="store_true", help="write report and follow-up sha256sum file")
    ap.add_argument("--json", action="store_true", help="print JSON report")
    ap.add_argument("--sha256sum", action="store_true", help="print follow-up sha256sum lines")
    args = ap.parse_args()

    try:
        report, sha_text = build_followup(
            batch_file=Path(args.batch_file),
            attempt_report_path=Path(args.attempt_report),
            lockfile=Path(args.lockfile),
            followup_sha256sum_path=Path(args.followup_sha256sum_path),
            allow_version_mismatch=bool(args.allow_version_mismatch),
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    payload = json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n"
    if args.write:
        rp = Path(args.report_path)
        sp = Path(args.followup_sha256sum_path)
        rp.parent.mkdir(parents=True, exist_ok=True)
        sp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text(payload, encoding="utf-8")
        sp.write_text(sha_text, encoding="utf-8")
    if args.json or not (args.write or args.sha256sum):
        sys.stdout.write(payload)
    if args.sha256sum:
        sys.stdout.write(sha_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
