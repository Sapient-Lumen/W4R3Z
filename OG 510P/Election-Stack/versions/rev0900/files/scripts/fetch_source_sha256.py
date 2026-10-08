#!/usr/bin/env python3
"""Fetch an external source, compute sha256, and optionally emit a receipt.

Legacy usage still works:
  python3 scripts/fetch_source_sha256.py '<url>'

Source-id usage reads evidence/lock/external-sources.toml, uses the pinned URL,
expected sha256, and local_filename, then can populate an external cache and a
small in-repo source-byte receipt:
  python3 scripts/fetch_source_sha256.py --source-id rfc8785_txt \
      --cache-dir /path/to/source-cache --write-receipt

Notes:
- This script is dependency-free and performs network I/O only when not using
  --print-plan.
- Release ZIPs must not bundle third-party source bytes. Use an external cache
  or local evidence/cache/ directory, which is excluded from manifest/ZIP scope.
- Receipts do not make sources current voter instruction or legal authority.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import tempfile
import tomllib
import urllib.request
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


def load_source(source_id: str, lockfile: Path = LOCK) -> dict[str, Any]:
    with lockfile.open("rb") as f:
        rows = tomllib.load(f).get("source", [])
    matches = [r for r in rows if isinstance(r, dict) and str(r.get("id") or "") == source_id]
    if not matches:
        raise ValueError(f"unknown source_id in {lockfile}: {source_id}")
    row = matches[0]
    sha = str(row.get("sha256") or "").strip().lower()
    if not sha:
        raise ValueError(f"source_id is unpinned; receipts require a lockfile sha256: {source_id}")
    if not HEX64_RE.fullmatch(sha):
        raise ValueError(f"source_id has invalid lockfile sha256: {source_id}")
    local_filename = str(row.get("local_filename") or "").strip()
    if not safe_basename(local_filename):
        raise ValueError(f"source_id must have a safe local_filename before fetch: {source_id}")
    return row


def safe_basename(raw: str) -> bool:
    if not raw or raw.startswith(".") or "/" in raw or "\\" in raw or ".." in raw:
        return False
    return bool(SAFE_BASENAME_RE.fullmatch(raw))


def infer_content_type(headers: Any, local_filename: str) -> str:
    raw = ""
    try:
        raw = str(headers.get("Content-Type") or "").split(";", 1)[0].strip().lower()
    except Exception:
        raw = ""
    if raw:
        return raw
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


def fetch_bytes(
    url: str,
    *,
    timeout: int,
    max_bytes: int,
    target: Path | None = None,
) -> tuple[str, int, str, Path | None]:
    h = hashlib.sha256()
    total = 0
    content_type = ""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "The-Election-Stack/source-byte-receipt"},
    )

    tmp_name: str | None = None
    out = None
    try:
        if target is not None:
            target.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp_name = tempfile.mkstemp(prefix=target.name + ".", suffix=".part", dir=str(target.parent))
            out = os.fdopen(fd, "wb")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content_type = infer_content_type(resp.headers, target.name if target is not None else url.rsplit("/", 1)[-1])
            while True:
                chunk = resp.read(64 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > max_bytes:
                    raise RuntimeError(f"exceeded --max-bytes ({max_bytes}); aborting at {total}")
                h.update(chunk)
                if out is not None:
                    out.write(chunk)
        if out is not None:
            out.flush()
            os.fsync(out.fileno())
            out.close()
            out = None
    except Exception:
        if out is not None:
            out.close()
        if tmp_name:
            try:
                Path(tmp_name).unlink()
            except OSError:
                pass
        raise
    return h.hexdigest(), total, content_type, Path(tmp_name) if tmp_name else None


def receipt_id_for(version: str, source_id: str) -> str:
    token = version.upper().replace("V", "REV", 1)
    return f"SBR-{token}-{source_id}"


def archive_version() -> str:
    try:
        return (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    except Exception:
        return "v000"


def write_receipt(
    *,
    row: dict[str, Any],
    receipt_dir: Path,
    byte_count: int,
    observed_sha256: str,
    content_type: str,
    retrieved_at_utc: str,
) -> Path:
    source_id = str(row.get("id") or "").strip()
    local_filename = str(row.get("local_filename") or "").strip()
    expected_sha = str(row.get("sha256") or "").strip().lower()
    record = {
        "receipt_id": receipt_id_for(archive_version(), source_id),
        "source_id": source_id,
        "source_url": str(row.get("url") or "").strip(),
        "retrieved_at_utc": retrieved_at_utc,
        "observation_type": "network_fetch",
        "fetch_status": 200,
        "content_type": content_type,
        "byte_count": byte_count,
        "observed_sha256": observed_sha256,
        "lockfile_sha256": expected_sha,
        "local_cache_filename": local_filename,
        "bundled_bytes": False,
        "non_claims": NON_CLAIMS,
    }
    receipt_dir.mkdir(parents=True, exist_ok=True)
    out = receipt_dir / f"{source_id}.receipt.json"
    out.write_text(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Fetch a URL/source-id and compute its sha256")
    ap.add_argument("url", nargs="?", help="URL to fetch (legacy mode; omit when using --source-id)")
    ap.add_argument("--source-id", help="Lockfile source id to fetch and verify")
    ap.add_argument("--lockfile", default=str(LOCK), help="external-sources.toml path for --source-id")
    ap.add_argument("--cache-dir", help="optional external cache directory for fetched bytes")
    ap.add_argument("--write-receipt", action="store_true", help="write artifacts/source_byte_receipts/<source_id>.receipt.json after sha match")
    ap.add_argument("--receipt-dir", default=str(DEFAULT_RECEIPT_DIR), help="receipt output directory")
    ap.add_argument("--force", action="store_true", help="replace existing cache file when --cache-dir is used")
    ap.add_argument("--print-plan", action="store_true", help="print lockfile fetch plan and exit without network I/O")
    ap.add_argument(
        "--max-bytes",
        type=int,
        default=200 * 1024 * 1024,
        help="maximum bytes to download (default: 200 MiB)",
    )
    ap.add_argument("--timeout", type=int, default=30, help="request timeout seconds")
    args = ap.parse_args()

    if args.url and args.source_id:
        print("ERROR: pass either a positional URL or --source-id, not both", file=sys.stderr)
        return 2
    if not args.url and not args.source_id:
        print("ERROR: pass a URL or --source-id", file=sys.stderr)
        return 2
    if args.write_receipt and not args.source_id:
        print("ERROR: --write-receipt requires --source-id", file=sys.stderr)
        return 2

    row: dict[str, Any] | None = None
    expected_sha = ""
    local_filename = ""
    if args.source_id:
        try:
            row = load_source(args.source_id, Path(args.lockfile))
        except Exception as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2
        url = str(row.get("url") or "").strip()
        expected_sha = str(row.get("sha256") or "").strip().lower()
        local_filename = str(row.get("local_filename") or "").strip()
    else:
        url = str(args.url or "").strip()
        local_filename = url.rsplit("/", 1)[-1] or "download.bin"

    target: Path | None = None
    if args.cache_dir:
        if not safe_basename(local_filename):
            print(f"ERROR: unsafe local filename: {local_filename!r}", file=sys.stderr)
            return 2
        target = Path(args.cache_dir) / local_filename
        if target.exists() and not args.force:
            print(f"ERROR: cache target exists; pass --force to replace: {target}", file=sys.stderr)
            return 2

    if args.print_plan:
        plan = {
            "source_id": args.source_id or "",
            "url": url,
            "expected_sha256": expected_sha,
            "local_filename": local_filename,
            "cache_target": str(target) if target is not None else "",
            "write_receipt": bool(args.write_receipt),
            "network_io": False,
            "boundary": NON_CLAIMS,
        }
        print(json.dumps(plan, sort_keys=True, separators=(",", ":")))
        return 0

    try:
        digest, total, content_type, tmp_path = fetch_bytes(url, timeout=args.timeout, max_bytes=args.max_bytes, target=target)
    except Exception as exc:
        print(f"ERROR: fetch failed: {exc}", file=sys.stderr)
        return 1

    if expected_sha and digest.lower() != expected_sha:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except OSError:
                pass
        print(f"ERROR: sha256 mismatch for {args.source_id}: got {digest}, expected {expected_sha}", file=sys.stderr)
        return 2

    if target is not None:
        if tmp_path is None or not tmp_path.exists():
            print(f"ERROR: internal cache temp file missing for {target.name}", file=sys.stderr)
            return 2
        tmp_path.replace(target)

    print(digest)
    print(f"bytes={total}")
    if content_type:
        print(f"content_type={content_type}")

    if args.write_receipt:
        assert row is not None
        retrieved_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        path = write_receipt(
            row=row,
            receipt_dir=Path(args.receipt_dir),
            byte_count=total,
            observed_sha256=digest.lower(),
            content_type=content_type or infer_content_type({}, local_filename),
            retrieved_at_utc=retrieved_at,
        )
        print(f"receipt={path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
