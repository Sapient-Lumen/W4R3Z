#!/usr/bin/env python3
"""Build a sha256sum-ready source-byte cache intake manifest.

This is the offline handoff between the release archive and a network-capable or
out-of-band source acquisition environment.  It reads the pinned-source lockfile
and the current receipt report, lists the receipt-missing pinned rows in the same
priority order as the acquisition queue, and emits both:

- a JSON report for release-gate accounting; and
- a POSIX-style ``sha256sum -c`` input file of ``<sha256>  <local_filename>``
  entries for an external cache directory.

It never fetches the network and never copies third-party source bytes into the
release tree.  The sha256sum file is an expectation manifest only.
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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from release_context import archive_version as _archive_version, release_date as _release_date  # noqa: E402
from source_byte_receipt_pack import source_family  # noqa: E402
from source_byte_priority import source_byte_priority_tier  # noqa: E402

VERSION = _archive_version(ROOT)
REV = VERSION.removeprefix("v").zfill(4)
LOCK = ROOT / "evidence" / "lock" / "external-sources.toml"
RECEIPT_REPORT = ROOT / "artifacts" / "reports" / "source-byte-receipt-validation-report.json"
QUEUE_REPORT = ROOT / "artifacts" / "reports" / "source-byte-acquisition-queue.json"
OUT_DIR = ROOT / "artifacts" / "source_byte_cache_intake"
SHA256SUM = OUT_DIR / f"source-byte-cache-missing-receipts-rev{REV}.sha256"
REPORT = ROOT / "artifacts" / "reports" / f"source-byte-cache-intake-manifest-rev{REV}.json"

HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
SAFE_BASENAME_RE = re.compile(r"^[A-Za-z0-9._-]+$")

BOUNDARY = (
    "Source-byte cache intake manifest is an expectation file for externally "
    "acquired bytes. It performs no network I/O, bundles no third-party bytes, "
    "does not prove source-byte cache completeness, and is not current voter "
    "instruction, not legal advice, not public-release authorization, and not "
    "live-pilot approval."
)


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except Exception:
        return str(path)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_sources(lockfile: Path = LOCK) -> list[dict[str, Any]]:
    with lockfile.open("rb") as f:
        rows = tomllib.load(f).get("source", [])
    return [r for r in rows if isinstance(r, dict) and str(r.get("id") or "").strip()]


def receipt_source_ids() -> set[str]:
    report = load_json(RECEIPT_REPORT)
    return {
        str(row.get("source_id") or "").strip()
        for row in report.get("rows") or []
        if isinstance(row, dict) and row.get("valid") is True and str(row.get("source_id") or "").strip()
    }


def host_of(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


def safe_basename(raw: Any) -> bool:
    s = str(raw or "").strip()
    if not s or s.startswith(".") or "/" in s or "\\" in s or ".." in s:
        return False
    return bool(SAFE_BASENAME_RE.fullmatch(s))


def sha256sum_lines(rows: list[dict[str, Any]]) -> list[str]:
    return [f"{r['expected_sha256']}  {r['local_filename']}" for r in rows]


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_manifest(*, batch_size: int = 20) -> tuple[dict[str, Any], str]:
    receipt_ids = receipt_source_ids()
    sources = load_sources()
    pinned = [r for r in sources if str(r.get("sha256") or "").strip()]
    pinned_ids = {str(r.get("id") or "").strip() for r in pinned}
    missing = [r for r in pinned if str(r.get("id") or "").strip() not in receipt_ids]

    rows: list[dict[str, Any]] = []
    errors: list[str] = []
    seen_names: Counter[str] = Counter(str(r.get("local_filename") or "").strip() for r in pinned)
    for src in missing:
        sid = str(src.get("id") or "").strip()
        local_filename = str(src.get("local_filename") or "").strip()
        sha = str(src.get("sha256") or "").strip().lower()
        row_errors: list[str] = []
        if not HEX64_RE.fullmatch(sha):
            row_errors.append("invalid_expected_sha256")
        if not safe_basename(local_filename):
            row_errors.append("unsafe_or_missing_local_filename")
        if seen_names[local_filename] > 1:
            row_errors.append("duplicate_local_filename")
        if row_errors:
            errors.extend(f"{sid}:{e}" for e in row_errors)
        rows.append(
            {
                "source_id": sid,
                "priority_tier": source_byte_priority_tier(src),
                "source_family": source_family(src),
                "url_host": host_of(str(src.get("url") or "")),
                "local_filename": local_filename,
                "expected_sha256": sha,
                "batch_index": 0,  # filled after sorting
            }
        )

    rows.sort(key=lambda r: (str(r["priority_tier"]), str(r["source_family"]), str(r["source_id"])))
    for idx, row in enumerate(rows):
        row["batch_index"] = idx // max(batch_size, 1) + 1

    lines = sha256sum_lines(rows)
    sha_text = "\n".join(lines) + ("\n" if lines else "")
    priority_counts = Counter(str(r["priority_tier"]) for r in rows)
    family_counts = Counter(str(r["source_family"]) for r in rows)
    host_counts = Counter(str(r["url_host"]) for r in rows)
    batch_counts = Counter(str(r["batch_index"]) for r in rows)
    first_batch = [str(r["source_id"]) for r in rows[:batch_size]]

    queue = load_json(QUEUE_REPORT) if QUEUE_REPORT.exists() else {}
    receipt_report = load_json(RECEIPT_REPORT) if RECEIPT_REPORT.exists() else {}

    report = {
        "archive_version": VERSION,
        "release_date": _release_date(ROOT),
        "synthetic_only": True,
        "boundary": BOUNDARY,
        "network_io": False,
        "third_party_bytes_bundled": False,
        "scope": "missing-receipts",
        "lockfile": rel(LOCK),
        "receipt_report": rel(RECEIPT_REPORT),
        "queue_report": rel(QUEUE_REPORT),
        "sha256sum_path": rel(SHA256SUM),
        "sha256sum_sha256": "sha256:" + sha256_text(sha_text),
        "batch_size": batch_size,
        "batch_count": (len(rows) + batch_size - 1) // batch_size if rows else 0,
        "pinned_source_count": len(pinned),
        "receipt_present_count": len(receipt_ids & pinned_ids),
        "receipt_missing_count": len(rows),
        "manifest_entry_count": len(rows),
        "priority_counts": dict(sorted(priority_counts.items())),
        "family_counts": dict(sorted(family_counts.items())),
        "host_counts": dict(sorted(host_counts.items())),
        "batch_counts": dict(sorted(batch_counts.items(), key=lambda kv: int(kv[0]))),
        "next_batch_source_ids": first_batch,
        "queue_next_batch_matches": first_batch == [str(x) for x in (queue.get("next_operator_batch_source_ids") or [])],
        "queue_receipt_missing_count": int(queue.get("receipt_missing_count") or 0),
        "receipt_report_valid_count": int(receipt_report.get("valid_receipt_count") or 0),
        "error_count": len(errors),
        "errors": errors,
        "operator_check_commands": [
            "cd /path/to/external-source-cache && sha256sum -c /path/to/source-byte-cache-missing-receipts.sha256",
            "python3 scripts/source_byte_receipts_from_cache_batch.py --cache-dir /path/to/external-source-cache --write-receipts",
        ],
        "rows": rows,
    }
    return report, sha_text


def main() -> int:
    ap = argparse.ArgumentParser(description="Build source-byte cache intake manifest and sha256sum file")
    ap.add_argument("--batch-size", type=int, default=20, help="operator batch size used for batch indexes")
    ap.add_argument("--report-path", default=str(REPORT), help="JSON report path for --write")
    ap.add_argument("--sha256sum-path", default=str(SHA256SUM), help="sha256sum expectation path for --write")
    ap.add_argument("--write", action="store_true", help="write JSON report and sha256sum expectation file")
    ap.add_argument("--json", action="store_true", help="print JSON report")
    ap.add_argument("--sha256sum", action="store_true", help="print sha256sum expectation lines")
    args = ap.parse_args()

    if args.batch_size <= 0:
        print("ERROR: --batch-size must be positive", file=sys.stderr)
        return 2
    report, sha_text = build_manifest(batch_size=args.batch_size)
    payload = json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n"
    if args.write:
        rp = Path(args.report_path)
        sp = Path(args.sha256sum_path)
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
