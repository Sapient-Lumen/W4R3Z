#!/usr/bin/env python3
"""Validate source-byte fetch receipts without bundling third-party bytes.

The lockfile can pin external source hashes, but the release archive intentionally
keeps downloaded third-party artifacts out of the ZIP.  This pack closes the gap
between "hash in lockfile" and "operator observed matching bytes at least once"
by validating small receipts that record observation method, byte count, and
observed sha256 for selected high-leverage pinned sources.

Receipts are not authority promotion: they prove byte-identity observations for
pinned rows only.  They do not make mutable pages current, do not authorize voter
instruction, and do not prove source-cache completeness.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import tomllib
from pathlib import Path
from typing import Any

from release_context import archive_version, release_date

ROOT = Path(__file__).resolve().parents[1]
VERSION = archive_version(ROOT)
RELEASE_DATE = release_date(ROOT)
LOCK = ROOT / "evidence" / "lock" / "external-sources.toml"
DEFAULT_RECEIPT_DIR = ROOT / "artifacts" / "source_byte_receipts"
REPORT = ROOT / "artifacts" / "reports" / "source-byte-receipt-validation-report.json"

HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
SAFE_BASENAME_RE = re.compile(r"^[A-Za-z0-9._-]+$")

REQUIRED_FIELDS = {
    "receipt_id",
    "source_id",
    "source_url",
    "retrieved_at_utc",
    "observation_type",
    "fetch_status",
    "content_type",
    "byte_count",
    "observed_sha256",
    "lockfile_sha256",
    "local_cache_filename",
    "bundled_bytes",
    "non_claims",
}

ERROR_MESSAGES = {
    "JSON_PARSE_ERROR": "receipt JSON could not be parsed",
    "MISSING_REQUIRED_FIELD": "receipt is missing a required field",
    "UNKNOWN_SOURCE_ID": "source_id is not present in external-sources lockfile",
    "UNPINNED_SOURCE_RECEIPT": "source-byte receipts must target pinned lockfile rows only",
    "URL_MISMATCH": "receipt source_url differs from lockfile URL",
    "INVALID_RETRIEVED_AT": "retrieved_at_utc must be UTC ISO seconds ending in Z",
    "INVALID_OBSERVATION_TYPE": "observation_type must be network_fetch or operator_cache_file",
    "FETCH_STATUS_NOT_200": "network_fetch receipts must carry fetch_status=200",
    "CACHE_FETCH_STATUS_INVALID": "operator_cache_file receipts must carry fetch_status=not_applicable_cache_file",
    "CACHE_FILE_MATCH_FLAG_MISSING": "operator_cache_file receipts must carry cache_file_sha256_matched=true",
    "INVALID_BYTE_COUNT": "byte_count must be a positive integer",
    "INVALID_OBSERVED_SHA256": "observed_sha256 must be lowercase 64-hex",
    "SHA256_LOCKFILE_MISMATCH": "observed_sha256 must equal the pinned lockfile sha256",
    "LOCKFILE_SHA256_FIELD_MISMATCH": "lockfile_sha256 field must echo the pinned lockfile sha256",
    "UNSAFE_LOCAL_CACHE_FILENAME": "local_cache_filename must be a safe basename",
    "BUNDLED_BYTES_TRUE": "receipts in this archive must not claim bundled third-party bytes",
    "NON_CLAIMS_BOUNDARY_MISSING": "non_claims must include the no-current-instruction/no-legal-advice/no-completeness boundary",
    "DUPLICATE_RECEIPT_ID": "receipt_id must be unique",
    "DUPLICATE_SOURCE_ID": "each source_id may appear at most once in the receipt pack",
}


def load_sources() -> dict[str, dict[str, Any]]:
    with LOCK.open("rb") as f:
        rows = tomllib.load(f).get("source", [])
    return {str(r.get("id") or ""): r for r in rows if isinstance(r, dict) and str(r.get("id") or "")}


def iter_receipts(receipt_dir: Path) -> list[Path]:
    if not receipt_dir.exists():
        return []
    return sorted(p for p in receipt_dir.glob("*.json") if p.is_file())


def _valid_utc(raw: Any) -> bool:
    s = str(raw or "")
    if not UTC_RE.fullmatch(s):
        return False
    try:
        dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def _safe_basename(raw: Any) -> bool:
    name = str(raw or "").strip()
    if not name:
        return False
    if "/" in name or "\\" in name or name.startswith(".") or ".." in name:
        return False
    return bool(SAFE_BASENAME_RE.fullmatch(name))


def validate_receipt(record: dict[str, Any], sources: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    for field in sorted(REQUIRED_FIELDS):
        val = record.get(field)
        if field not in record or (val is None) or (isinstance(val, str) and not val.strip()):
            errors.append("MISSING_REQUIRED_FIELD")

    sid = str(record.get("source_id") or "").strip()
    src = sources.get(sid)
    pinned_sha = ""
    if not src:
        errors.append("UNKNOWN_SOURCE_ID")
    else:
        pinned_sha = str(src.get("sha256") or "").strip()
        if not pinned_sha:
            errors.append("UNPINNED_SOURCE_RECEIPT")
        if str(record.get("source_url") or "").strip() != str(src.get("url") or "").strip():
            errors.append("URL_MISMATCH")

    if not _valid_utc(record.get("retrieved_at_utc")):
        errors.append("INVALID_RETRIEVED_AT")

    obs_type = str(record.get("observation_type") or "").strip()
    if obs_type not in {"network_fetch", "operator_cache_file"}:
        errors.append("INVALID_OBSERVATION_TYPE")
    if obs_type == "network_fetch":
        try:
            status = int(record.get("fetch_status"))
        except Exception:
            status = -1
        if status != 200:
            errors.append("FETCH_STATUS_NOT_200")
    elif obs_type == "operator_cache_file":
        if str(record.get("fetch_status") or "") != "not_applicable_cache_file":
            errors.append("CACHE_FETCH_STATUS_INVALID")
        if record.get("cache_file_sha256_matched") is not True:
            errors.append("CACHE_FILE_MATCH_FLAG_MISSING")

    try:
        byte_count = int(record.get("byte_count"))
    except Exception:
        byte_count = -1
    if byte_count <= 0:
        errors.append("INVALID_BYTE_COUNT")

    observed = str(record.get("observed_sha256") or "").strip()
    if not HEX64_RE.fullmatch(observed):
        errors.append("INVALID_OBSERVED_SHA256")
    elif pinned_sha and observed != pinned_sha:
        errors.append("SHA256_LOCKFILE_MISMATCH")

    echoed = str(record.get("lockfile_sha256") or "").strip()
    if pinned_sha and echoed != pinned_sha:
        errors.append("LOCKFILE_SHA256_FIELD_MISMATCH")

    if not _safe_basename(record.get("local_cache_filename")):
        errors.append("UNSAFE_LOCAL_CACHE_FILENAME")

    if record.get("bundled_bytes") is not False:
        errors.append("BUNDLED_BYTES_TRUE")

    non_claims = str(record.get("non_claims") or "").lower()
    required_phrases = [
        "not current voter instruction",
        "not legal advice",
        "not source-byte cache completeness",
    ]
    if any(phrase not in non_claims for phrase in required_phrases):
        errors.append("NON_CLAIMS_BOUNDARY_MISSING")

    return sorted(set(errors))


def source_family(src: dict[str, Any]) -> str:
    tags = [str(t) for t in (src.get("tags") or [])]
    for key in ("eac", "nist", "rfc", "nasem", "cisa", "vvsg", "cdf"):
        if key in tags or str(src.get("id") or "").startswith(key + "_"):
            return key
    if tags:
        return tags[0]
    return "untagged"


def build_report(receipt_dir: Path = DEFAULT_RECEIPT_DIR) -> dict[str, Any]:
    sources = load_sources()
    pinned_count = sum(1 for row in sources.values() if str(row.get("sha256") or "").strip())
    rows: list[dict[str, Any]] = []
    seen_receipts: set[str] = set()
    seen_sources: set[str] = set()

    for path in iter_receipts(receipt_dir):
        rel = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            rows.append({
                "path": rel,
                "receipt_id": "",
                "source_id": "",
                "valid": False,
                "error_codes": ["JSON_PARSE_ERROR"],
                "error_messages": {"JSON_PARSE_ERROR": str(exc)},
            })
            continue
        if not isinstance(record, dict):
            record = {"_raw_non_object": record}
        errors = validate_receipt(record, sources)
        rid = str(record.get("receipt_id") or "").strip()
        sid = str(record.get("source_id") or "").strip()
        if rid:
            if rid in seen_receipts:
                errors.append("DUPLICATE_RECEIPT_ID")
            seen_receipts.add(rid)
        if sid:
            if sid in seen_sources:
                errors.append("DUPLICATE_SOURCE_ID")
            seen_sources.add(sid)
        src = sources.get(sid, {})
        rows.append({
            "path": rel,
            "receipt_id": rid,
            "source_id": sid,
            "source_family": source_family(src) if src else "unknown",
            "byte_count": int(record.get("byte_count") or 0) if str(record.get("byte_count") or "").isdigit() else 0,
            "observation_type": str(record.get("observation_type") or ""),
            "content_type": str(record.get("content_type") or ""),
            "local_cache_filename": str(record.get("local_cache_filename") or ""),
            "observed_sha256": str(record.get("observed_sha256") or ""),
            "valid": not errors,
            "error_codes": sorted(set(errors)),
            "error_messages": {code: ERROR_MESSAGES.get(code, code) for code in sorted(set(errors))},
        })

    valid_rows = [r for r in rows if r.get("valid") is True]
    families: dict[str, int] = {}
    observation_types: dict[str, int] = {}
    for r in valid_rows:
        fam = str(r.get("source_family") or "unknown")
        families[fam] = families.get(fam, 0) + 1
        obs = str(r.get("observation_type") or "unknown")
        observation_types[obs] = observation_types.get(obs, 0) + 1

    return {
        "archive_version": VERSION,
        "release_date": RELEASE_DATE,
        "synthetic_only": True,
        "receipt_dir": receipt_dir.relative_to(ROOT).as_posix() if receipt_dir.is_relative_to(ROOT) else str(receipt_dir),
        "receipt_count": len(rows),
        "valid_receipt_count": len(valid_rows),
        "invalid_receipt_count": len(rows) - len(valid_rows),
        "pinned_lockfile_source_count": pinned_count,
        "receipt_covered_pinned_source_count": len({r["source_id"] for r in valid_rows}),
        "receipt_coverage_percent_of_pinned": round((len({r["source_id"] for r in valid_rows}) / pinned_count * 100.0), 2) if pinned_count else 0.0,
        "observed_byte_total": sum(int(r.get("byte_count") or 0) for r in valid_rows),
        "families_covered": dict(sorted(families.items())),
        "observation_type_counts": dict(sorted(observation_types.items())),
        "bundled_third_party_bytes": False,
        "required_fields": sorted(REQUIRED_FIELDS),
        "boundary": "Source-byte receipts prove observed byte identity for selected pinned rows only; they are not current voter instruction, not legal advice, not source-byte cache completeness, not public-release authorization, and not live-pilot approval.",
        "rows": rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--receipt-dir", default=str(DEFAULT_RECEIPT_DIR), help="Directory containing source-byte receipt JSON files")
    ap.add_argument("--write", action="store_true", help="Write deterministic validation report")
    ap.add_argument("--json", action="store_true", help="Print validation report JSON")
    args = ap.parse_args()

    report = build_report(Path(args.receipt_dir))
    if args.write:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 0 if int(report["invalid_receipt_count"]) == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
