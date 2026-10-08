#!/usr/bin/env python3
"""Batch-create source-byte receipts from an external byte cache.

Operators can fetch third-party source files outside this release tree, place the
bytes at the lockfile's ``local_filename`` inside a cache directory, and run this
script once to identify every matching/missing/mismatched pinned source.  With
``--write-receipts`` it writes receipts only for files whose SHA-256 exactly
matches ``evidence/lock/external-sources.toml``.

The script never fetches the network and never copies third-party bytes into the
release archive.  It is intentionally a byte-identity bridge from an external
cache to small in-repo receipts, not a currentness, legal-authority, or public-
guidance mechanism.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
import tomllib
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from release_context import archive_version as _archive_version, release_date as _release_date
from source_byte_priority import source_byte_priority_tier

LOCK = ROOT / "evidence" / "lock" / "external-sources.toml"
DEFAULT_RECEIPT_DIR = ROOT / "artifacts" / "source_byte_receipts"
def current_revision_token(root: Path = ROOT) -> str:
    return _archive_version(root).removeprefix("v").zfill(4)


def default_report_path(root: Path = ROOT) -> Path:
    return root / "artifacts" / "reports" / f"source-byte-cache-batch-ingest-rev{current_revision_token(root)}.json"


DEFAULT_REPORT = default_report_path()
DEFAULT_CACHE_DIR = ROOT / "evidence" / "cache" / "source-bytes"
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
SAFE_BASENAME_RE = re.compile(r"^[A-Za-z0-9._-]+$")
SHA256SUM_LINE_RE = re.compile(r"^([0-9a-f]{64})  ([A-Za-z0-9._-]+)$")
NON_CLAIMS = (
    "not current voter instruction; not legal advice; not source-byte cache "
    "completeness; not public-release authorization; not live-pilot approval"
)
BOUNDARY = (
    "Batch source-byte cache ingest verifies external cache files against pinned "
    "lockfile SHA-256 values before writing receipts. It performs no network I/O, "
    "bundles no third-party bytes, and is not current voter instruction, not legal "
    "advice, not source-byte cache completeness, not public-release authorization, "
    "and not live-pilot approval."
)



def safe_basename(raw: Any) -> bool:
    s = str(raw or "")
    if not s or s.startswith(".") or "/" in s or "\\" in s or ".." in s:
        return False
    return bool(SAFE_BASENAME_RE.fullmatch(s))


def load_sources(lockfile: Path) -> list[dict[str, Any]]:
    with lockfile.open("rb") as f:
        rows = tomllib.load(f).get("source", [])
    return [r for r in rows if isinstance(r, dict) and str(r.get("id") or "").strip()]


def pinned_sources(lockfile: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in load_sources(lockfile):
        sha = str(row.get("sha256") or "").strip().lower()
        if sha:
            out.append(row)
    return out


def sha256_file(path: Path) -> tuple[str, int]:
    h = hashlib.sha256()
    total = 0
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            total += len(chunk)
            h.update(chunk)
    return h.hexdigest(), total


def infer_content_type(local_filename: str) -> str:
    low = local_filename.lower()
    if low.endswith(".pdf"):
        return "application/pdf"
    if low.endswith(".txt"):
        return "text/plain"
    if low.endswith(".md"):
        return "text/markdown"
    if low.endswith(".html") or low.endswith(".htm"):
        return "text/html"
    if low.endswith(".json"):
        return "application/json"
    return "application/octet-stream"


def stable_path_ref(path: Path, root: Path = ROOT) -> str:
    """Return a deterministic path reference for reports when inside the release tree."""
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def parse_batch_file(batch_file: Path) -> list[dict[str, str]]:
    """Parse a strict sha256sum batch file as an ordered source-intake filter."""

    entries: list[dict[str, str]] = []
    seen_filenames: set[str] = set()
    seen_lines: set[tuple[str, str]] = set()
    for lineno, raw in enumerate(batch_file.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        m = SHA256SUM_LINE_RE.fullmatch(raw)
        if not m:
            raise ValueError(f"invalid batch sha256sum line {batch_file}:{lineno}")
        expected_sha, local_filename = m.group(1), m.group(2)
        if not safe_basename(local_filename):
            raise ValueError(f"unsafe batch local filename {batch_file}:{lineno}")
        key = (expected_sha, local_filename)
        if key in seen_lines:
            raise ValueError(f"duplicate batch sha256sum line {batch_file}:{lineno}")
        if local_filename in seen_filenames:
            raise ValueError(f"duplicate batch local filename {batch_file}:{lineno}")
        seen_lines.add(key)
        seen_filenames.add(local_filename)
        entries.append({"expected_sha256": expected_sha, "local_filename": local_filename, "line_number": str(lineno)})
    if not entries:
        raise ValueError(f"empty batch file: {batch_file}")
    return entries


def select_sources_for_batch(sources: list[dict[str, Any]], batch_file: Path | None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Return lockfile rows selected by an optional batch sha256sum file."""

    if batch_file is None:
        return sources, {
            "batch_file": "",
            "batch_file_entry_count": 0,
            "batch_file_source_count": 0,
            "batch_file_sha256sum_sha256": "",
        }

    entries = parse_batch_file(batch_file)
    index: dict[tuple[str, str], dict[str, Any]] = {}
    for row in sources:
        local_filename = str(row.get("local_filename") or "").strip()
        expected_sha = str(row.get("sha256") or "").strip().lower()
        if not local_filename or not expected_sha:
            continue
        key = (expected_sha, local_filename)
        if key in index:
            raise ValueError(f"batch selection cannot disambiguate duplicate lockfile entry for {local_filename}")
        index[key] = row

    selected: list[dict[str, Any]] = []
    unmatched: list[dict[str, str]] = []
    for entry in entries:
        key = (entry["expected_sha256"], entry["local_filename"])
        row = index.get(key)
        if row is None:
            unmatched.append(entry)
        else:
            selected.append(row)
    if unmatched:
        details = ",".join(f"{e['line_number']}:{e['local_filename']}" for e in unmatched[:10])
        raise ValueError(f"batch file contains entries not pinned in lockfile: {details}")

    digest = hashlib.sha256(batch_file.read_bytes()).hexdigest()
    return selected, {
        "batch_file": stable_path_ref(batch_file),
        "batch_file_entry_count": len(entries),
        "batch_file_source_count": len(selected),
        "batch_file_sha256sum_sha256": "sha256:" + digest,
    }


def validate_retrieved_at(raw: str) -> str:
    if not raw:
        return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", raw):
        raise ValueError("--retrieved-at-utc must be UTC ISO seconds ending in Z")
    dt.datetime.fromisoformat(raw.replace("Z", "+00:00"))
    return raw


def receipt_id_for(version: str, source_id: str) -> str:
    token = version.upper().replace("V", "REV", 1)
    return f"SBR-{token}-CACHE-{source_id}"


def build_receipt(row: dict[str, Any], *, observed_sha256: str, byte_count: int, retrieved_at_utc: str) -> dict[str, Any]:
    source_id = str(row.get("id") or "").strip()
    local_filename = str(row.get("local_filename") or "").strip()
    expected_sha = str(row.get("sha256") or "").strip().lower()
    return {
        "receipt_id": receipt_id_for(_archive_version(ROOT), source_id),
        "source_id": source_id,
        "source_url": str(row.get("url") or "").strip(),
        "retrieved_at_utc": retrieved_at_utc,
        "observation_type": "operator_cache_file",
        "fetch_status": "not_applicable_cache_file",
        "content_type": infer_content_type(local_filename),
        "byte_count": byte_count,
        "observed_sha256": observed_sha256.lower(),
        "lockfile_sha256": expected_sha,
        "local_cache_filename": local_filename,
        "cache_file_sha256_matched": True,
        "bundled_bytes": False,
        "non_claims": NON_CLAIMS,
    }


def existing_receipt_source_ids(receipt_dir: Path) -> set[str]:
    seen: set[str] = set()
    if not receipt_dir.exists():
        return seen
    for path in sorted(receipt_dir.glob("*.receipt.json")):
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(obj, dict) and str(obj.get("source_id") or "").strip():
            seen.add(str(obj.get("source_id") or "").strip())
    return seen


def scan_cache(
    *,
    cache_dir: Path,
    receipt_dir: Path,
    lockfile: Path,
    scope: str,
    limit: int,
    assume_empty_cache: bool,
    batch_file: Path | None = None,
) -> dict[str, Any]:
    existing = existing_receipt_source_ids(receipt_dir)
    sources = pinned_sources(lockfile)
    selected_sources, batch_meta = select_sources_for_batch(sources, batch_file)
    rows: list[dict[str, Any]] = []
    local_name_counts = Counter(str(r.get("local_filename") or "") for r in sources)

    for row in selected_sources:
        sid = str(row.get("id") or "").strip()
        expected_sha = str(row.get("sha256") or "").strip().lower()
        local_filename = str(row.get("local_filename") or "").strip()
        has_receipt = sid in existing
        if scope == "missing-receipts" and has_receipt:
            continue
        if limit and len(rows) >= limit:
            break

        status = "not_checked"
        observed_sha = ""
        byte_count = 0
        cache_path = cache_dir / local_filename if local_filename else cache_dir / "(missing-local-filename)"
        error = ""
        if not HEX64_RE.fullmatch(expected_sha):
            status = "invalid_lockfile_sha256"
            error = "lockfile sha256 must be lowercase 64 hex"
        elif not safe_basename(local_filename):
            status = "unsafe_or_missing_local_filename"
            error = "local_filename must be a safe basename"
        elif local_name_counts[local_filename] > 1:
            status = "duplicate_local_filename"
            error = "local_filename is not unique across pinned sources"
        elif assume_empty_cache:
            status = "cache_not_inspected_assumed_empty"
        elif not cache_path.exists():
            status = "cache_file_missing"
        elif not cache_path.is_file():
            status = "cache_path_not_file"
            error = "cache path exists but is not a regular file"
        else:
            try:
                observed_sha, byte_count = sha256_file(cache_path)
            except Exception as exc:  # pragma: no cover - filesystem-dependent
                status = "cache_file_read_error"
                error = f"{exc.__class__.__name__}: {exc}"
            else:
                status = "cache_file_matched" if observed_sha.lower() == expected_sha else "cache_file_mismatch"

        rows.append({
            "source_id": sid,
            "priority_tier": source_byte_priority_tier(row, has_receipt=has_receipt),
            "existing_receipt": has_receipt,
            "local_filename": local_filename,
            "expected_sha256": expected_sha,
            "observed_sha256": observed_sha,
            "byte_count": byte_count,
            "cache_status": status,
            "would_write_receipt": status == "cache_file_matched" and not has_receipt,
            "error": error,
        })

    status_counts = Counter(str(r["cache_status"]) for r in rows)
    priority_counts = Counter(str(r["priority_tier"]) for r in rows)
    return {
        "archive_version": _archive_version(ROOT),
        "release_date": _release_date(ROOT),
        "synthetic_only": True,
        "boundary": BOUNDARY,
        "lockfile": str(lockfile.relative_to(ROOT)) if lockfile.is_relative_to(ROOT) else str(lockfile),
        "receipt_dir": str(receipt_dir.relative_to(ROOT)) if receipt_dir.is_relative_to(ROOT) else str(receipt_dir),
        "cache_dir": str(cache_dir.relative_to(ROOT)) if cache_dir.is_relative_to(ROOT) else str(cache_dir),
        "network_io": False,
        "third_party_bytes_bundled": False,
        "assume_empty_cache": assume_empty_cache,
        "scope": scope,
        "limit": limit,
        **batch_meta,
        "pinned_source_count": len(sources),
        "existing_receipt_source_count": len(existing & {str(r.get("id") or "") for r in sources}),
        "candidate_source_count": len(rows),
        "cache_status_counts": dict(sorted(status_counts.items())),
        "priority_counts": dict(sorted(priority_counts.items())),
        "matched_cache_file_count": status_counts.get("cache_file_matched", 0),
        "mismatched_cache_file_count": status_counts.get("cache_file_mismatch", 0),
        "would_write_receipt_count": sum(1 for r in rows if r.get("would_write_receipt") is True),
        "blocked_receipt_count": len(rows) - sum(1 for r in rows if r.get("would_write_receipt") is True),
        "rows": rows,
    }


def write_matching_receipts(report: dict[str, Any], *, lockfile: Path, receipt_dir: Path, force: bool, retrieved_at_utc: str) -> dict[str, Any]:
    sources = {str(r.get("id") or "").strip(): r for r in pinned_sources(lockfile)}
    written: list[str] = []
    skipped_existing: list[str] = []
    for row in report.get("rows") or []:
        if not isinstance(row, dict) or row.get("cache_status") != "cache_file_matched":
            continue
        sid = str(row.get("source_id") or "").strip()
        src = sources.get(sid)
        if not src:
            continue
        out = receipt_dir / f"{sid}.receipt.json"
        if out.exists() and not force:
            skipped_existing.append(sid)
            continue
        receipt = build_receipt(
            src,
            observed_sha256=str(row.get("observed_sha256") or ""),
            byte_count=int(row.get("byte_count") or 0),
            retrieved_at_utc=retrieved_at_utc,
        )
        receipt_dir.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
        written.append(sid)
    report = dict(report)
    report["write_receipts_requested"] = True
    report["written_receipt_source_ids"] = written
    report["skipped_existing_receipt_source_ids"] = skipped_existing
    report["written_receipt_count"] = len(written)
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description="Batch scan an external source-byte cache and optionally write receipts")
    ap.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR), help="external cache directory containing lockfile local_filename entries")
    ap.add_argument("--receipt-dir", default=str(DEFAULT_RECEIPT_DIR), help="receipt directory to inspect/write")
    ap.add_argument("--lockfile", default=str(LOCK), help="external-sources.toml path")
    ap.add_argument("--scope", choices=["missing-receipts", "all-pinned"], default="missing-receipts", help="sources to scan")
    ap.add_argument("--batch-file", default="", help="optional sha256sum batch file limiting the scan/write to listed expected sha256 + local filenames")
    ap.add_argument("--limit", type=int, default=0, help="optional max rows to scan after scope filtering; 0 means no limit")
    ap.add_argument("--assume-empty-cache", action="store_true", help="do not inspect the cache directory; report all candidates as cache-not-inspected")
    ap.add_argument("--write-receipts", action="store_true", help="write receipts for matching cache files")
    ap.add_argument("--force", action="store_true", help="replace existing receipts when --write-receipts is used")
    ap.add_argument("--retrieved-at-utc", default="", help="UTC timestamp for written receipts; default is current UTC")
    ap.add_argument("--report-path", default=str(DEFAULT_REPORT), help="report output path for --write-report")
    ap.add_argument("--write-report", action="store_true", help="write deterministic report JSON")
    ap.add_argument("--json", action="store_true", help="print report JSON")
    args = ap.parse_args()

    if args.limit < 0:
        print("ERROR: --limit must be non-negative", file=sys.stderr)
        return 2
    if args.assume_empty_cache and args.write_receipts:
        print("ERROR: --write-receipts cannot be used with --assume-empty-cache", file=sys.stderr)
        return 2
    try:
        retrieved_at = validate_retrieved_at(args.retrieved_at_utc) if args.write_receipts else ""
        report = scan_cache(
            cache_dir=Path(args.cache_dir),
            receipt_dir=Path(args.receipt_dir),
            lockfile=Path(args.lockfile),
            scope=args.scope,
            limit=args.limit,
            assume_empty_cache=args.assume_empty_cache,
            batch_file=Path(args.batch_file) if args.batch_file else None,
        )
        if args.write_receipts:
            report = write_matching_receipts(report, lockfile=Path(args.lockfile), receipt_dir=Path(args.receipt_dir), force=args.force, retrieved_at_utc=retrieved_at)
        else:
            report["write_receipts_requested"] = False
            report["written_receipt_source_ids"] = []
            report["skipped_existing_receipt_source_ids"] = []
            report["written_receipt_count"] = 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    payload = json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n"
    if args.write_report:
        out = Path(args.report_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload, encoding="utf-8")
    if args.json or not args.write_report:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
