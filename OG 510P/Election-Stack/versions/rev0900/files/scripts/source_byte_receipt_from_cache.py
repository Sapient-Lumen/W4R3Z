#!/usr/bin/env python3
"""Create a source-byte receipt from an already-populated external cache file.

This is the no-network complement to scripts/fetch_source_sha256.py.  It lets an
operator download third-party bytes outside the release tree, place the file at
its lockfile local_filename, and emit a receipt only after the local file's
sha256 exactly matches evidence/lock/external-sources.toml.

The helper never fetches the network and never copies third-party bytes into the
release archive.  It records a byte-identity observation, not source currentness,
legal authority, or cache completeness.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
import tomllib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "evidence" / "lock" / "external-sources.toml"
DEFAULT_RECEIPT_DIR = ROOT / "artifacts" / "source_byte_receipts"
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
SAFE_BASENAME_RE = re.compile(r"^[A-Za-z0-9._-]+$")
NON_CLAIMS = (
    "not current voter instruction; not legal advice; not source-byte cache "
    "completeness; not public-release authorization; not live-pilot approval"
)


def safe_basename(raw: str) -> bool:
    if not raw or raw.startswith(".") or "/" in raw or "\\" in raw or ".." in raw:
        return False
    return bool(SAFE_BASENAME_RE.fullmatch(raw))


def archive_version() -> str:
    return (ROOT / "VERSION").read_text(encoding="utf-8").strip()


def receipt_id_for(version: str, source_id: str) -> str:
    token = version.upper().replace("V", "REV", 1)
    return f"SBR-{token}-CACHE-{source_id}"


def load_source(source_id: str, lockfile: Path = LOCK) -> dict[str, Any]:
    with lockfile.open("rb") as f:
        rows = tomllib.load(f).get("source", [])
    matches = [r for r in rows if isinstance(r, dict) and str(r.get("id") or "") == source_id]
    if not matches:
        raise ValueError(f"unknown source_id in {lockfile}: {source_id}")
    row = matches[0]
    sha = str(row.get("sha256") or "").strip().lower()
    if not sha:
        raise ValueError(f"source_id is unpinned; cache receipts require a lockfile sha256: {source_id}")
    if not HEX64_RE.fullmatch(sha):
        raise ValueError(f"source_id has invalid lockfile sha256: {source_id}")
    local_filename = str(row.get("local_filename") or "").strip()
    if not safe_basename(local_filename):
        raise ValueError(f"source_id must have a safe local_filename before receipt: {source_id}")
    return row


def sha256_file(path: Path) -> tuple[str, int]:
    h = hashlib.sha256()
    total = 0
    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
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


def validate_retrieved_at(raw: str) -> str:
    if not raw:
        return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", raw):
        raise ValueError("--retrieved-at-utc must be UTC ISO seconds ending in Z")
    dt.datetime.fromisoformat(raw.replace("Z", "+00:00"))
    return raw


def build_receipt(
    *,
    row: dict[str, Any],
    byte_count: int,
    observed_sha256: str,
    content_type: str,
    retrieved_at_utc: str,
) -> dict[str, Any]:
    source_id = str(row.get("id") or "").strip()
    local_filename = str(row.get("local_filename") or "").strip()
    expected_sha = str(row.get("sha256") or "").strip().lower()
    return {
        "receipt_id": receipt_id_for(archive_version(), source_id),
        "source_id": source_id,
        "source_url": str(row.get("url") or "").strip(),
        "retrieved_at_utc": retrieved_at_utc,
        "observation_type": "operator_cache_file",
        "fetch_status": "not_applicable_cache_file",
        "content_type": content_type,
        "byte_count": byte_count,
        "observed_sha256": observed_sha256,
        "lockfile_sha256": expected_sha,
        "local_cache_filename": local_filename,
        "cache_file_sha256_matched": True,
        "bundled_bytes": False,
        "non_claims": NON_CLAIMS,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Emit a source-byte receipt from a verified local cache file")
    ap.add_argument("--source-id", required=True, help="pinned external source id")
    ap.add_argument("--cache-dir", required=True, help="external cache directory containing local_filename")
    ap.add_argument("--lockfile", default=str(LOCK), help="external-sources.toml path")
    ap.add_argument("--receipt-dir", default=str(DEFAULT_RECEIPT_DIR), help="receipt output directory")
    ap.add_argument("--retrieved-at-utc", default="", help="UTC observation timestamp, e.g. 2026-06-13T04:00:00Z")
    ap.add_argument("--content-type", default="", help="override content type; default inferred from local_filename")
    ap.add_argument("--write-receipt", action="store_true", help="write artifacts/source_byte_receipts/<source_id>.receipt.json")
    ap.add_argument("--force", action="store_true", help="replace an existing receipt file")
    ap.add_argument("--print-plan", action="store_true", help="print cache receipt plan without reading bytes or writing")
    args = ap.parse_args()

    try:
        row = load_source(args.source_id, Path(args.lockfile))
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    local_filename = str(row.get("local_filename") or "").strip()
    cache_path = Path(args.cache_dir) / local_filename
    expected_sha = str(row.get("sha256") or "").strip().lower()

    if args.print_plan:
        print(json.dumps({
            "source_id": args.source_id,
            "expected_sha256": expected_sha,
            "local_filename": local_filename,
            "cache_path": str(cache_path),
            "write_receipt": bool(args.write_receipt),
            "network_io": False,
            "observation_type": "operator_cache_file",
            "boundary": NON_CLAIMS,
        }, sort_keys=True, separators=(",", ":")))
        return 0

    if not cache_path.exists() or not cache_path.is_file():
        print(f"ERROR: cache file not found: {cache_path}", file=sys.stderr)
        return 1

    observed_sha, byte_count = sha256_file(cache_path)
    if observed_sha.lower() != expected_sha:
        print(
            f"ERROR: sha256 mismatch for {args.source_id}: got {observed_sha}, expected {expected_sha}",
            file=sys.stderr,
        )
        return 2

    print(observed_sha)
    print(f"bytes={byte_count}")
    content_type = args.content_type.strip() or infer_content_type(local_filename)
    print(f"content_type={content_type}")

    if args.write_receipt:
        try:
            retrieved_at = validate_retrieved_at(args.retrieved_at_utc)
        except Exception as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2
        receipt = build_receipt(
            row=row,
            byte_count=byte_count,
            observed_sha256=observed_sha.lower(),
            content_type=content_type,
            retrieved_at_utc=retrieved_at,
        )
        receipt_dir = Path(args.receipt_dir)
        receipt_dir.mkdir(parents=True, exist_ok=True)
        out = receipt_dir / f"{args.source_id}.receipt.json"
        if out.exists() and not args.force:
            print(f"ERROR: receipt exists; pass --force to replace: {out}", file=sys.stderr)
            return 2
        out.write_text(json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
        print(f"receipt={out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
