#!/usr/bin/env python3
"""Build per-batch sha256sum manifests for external source-byte intake.

The master intake manifest is useful, but a 105-file handoff is still awkward for
operators.  This builder splits the receipt-missing pinned-source manifest into
small, deterministic ``sha256sum -c`` batch files that can be fetched, checked,
and converted into receipts incrementally.

It performs no network I/O and never copies third-party source bytes into the
release tree.  The batch files are expectation manifests only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from release_context import archive_version as _archive_version, release_date as _release_date  # noqa: E402

# Import the current intake builder so the master and batch manifests cannot drift
# into parallel priority/scope logic.
sys.path.insert(0, str(ROOT / "scripts"))
from build_source_byte_cache_intake_manifest import build_manifest as build_intake_manifest  # noqa: E402

VERSION = _archive_version(ROOT)
REV = VERSION.removeprefix("v").zfill(4)
DEFAULT_BATCH_SIZE = 20
MASTER_SHA256SUM = ROOT / "artifacts" / "source_byte_cache_intake" / f"source-byte-cache-missing-receipts-rev{REV}.sha256"
OUT_DIR = ROOT / "artifacts" / "source_byte_cache_intake" / "batches"
REPORT = ROOT / "artifacts" / "reports" / f"source-byte-cache-batch-manifests-rev{REV}.json"
BOUNDARY = (
    "Source-byte cache batch manifests split the master expectation file into "
    "operator-sized sha256sum checks. They perform no network I/O, bundle no "
    "third-party bytes, do not prove source-byte cache completeness, and are not "
    "current voter instruction, not legal advice, not public-release authorization, "
    "and not live-pilot approval."
)


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except Exception:
        return str(path)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def batch_path(batch_index: int, out_dir: Path = OUT_DIR, rev: str = REV) -> Path:
    return out_dir / f"source-byte-cache-missing-receipts-rev{rev}-batch{batch_index:02d}.sha256"


def line_for(row: dict[str, Any]) -> str:
    return f"{row['expected_sha256']}  {row['local_filename']}"


def build_batch_manifests(*, batch_size: int = DEFAULT_BATCH_SIZE) -> tuple[dict[str, Any], dict[Path, str]]:
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    intake, master_text = build_intake_manifest(batch_size=batch_size)
    rows = list(intake.get("rows") or [])
    files: dict[Path, str] = {}
    batch_reports: list[dict[str, Any]] = []
    seen_source_ids: set[str] = set()
    duplicate_source_ids: list[str] = []
    seen_lines: set[str] = set()
    duplicate_lines: list[str] = []

    for batch_index in range(1, int(intake.get("batch_count") or 0) + 1):
        batch_rows = [r for r in rows if int(r.get("batch_index") or 0) == batch_index]
        lines = [line_for(r) for r in batch_rows]
        text = "\n".join(lines) + ("\n" if lines else "")
        path = batch_path(batch_index)
        files[path] = text
        source_ids = [str(r.get("source_id") or "") for r in batch_rows]
        for sid in source_ids:
            if sid in seen_source_ids:
                duplicate_source_ids.append(sid)
            seen_source_ids.add(sid)
        for line in lines:
            if line in seen_lines:
                duplicate_lines.append(line)
            seen_lines.add(line)
        batch_reports.append(
            {
                "batch_index": batch_index,
                "path": rel(path),
                "line_count": len(lines),
                "sha256sum_sha256": "sha256:" + sha256_text(text),
                "first_source_id": source_ids[0] if source_ids else "",
                "last_source_id": source_ids[-1] if source_ids else "",
                "source_ids": source_ids,
            }
        )

    reconstructed = "".join(files[path] for path in sorted(files))
    priority_counts = Counter(str(r.get("priority_tier") or "") for r in rows)
    family_counts = Counter(str(r.get("source_family") or "") for r in rows)
    errors: list[str] = []
    if reconstructed != master_text:
        errors.append("batch_files_do_not_reconstruct_master_sha256sum_text")
    if duplicate_source_ids:
        errors.append("duplicate_source_ids:" + ",".join(sorted(set(duplicate_source_ids))))
    if duplicate_lines:
        errors.append("duplicate_sha256sum_lines:" + str(len(set(duplicate_lines))))
    overfull = [b for b in batch_reports if int(b["line_count"]) > batch_size]
    if overfull:
        errors.append("batch_line_count_exceeds_batch_size")

    report = {
        "archive_version": VERSION,
        "release_date": _release_date(ROOT),
        "synthetic_only": True,
        "boundary": BOUNDARY,
        "network_io": False,
        "third_party_bytes_bundled": False,
        "scope": "missing-receipts",
        "batch_size": batch_size,
        "batch_count": len(batch_reports),
        "manifest_entry_count": len(rows),
        "master_sha256sum_path": rel(MASTER_SHA256SUM),
        "master_sha256sum_sha256": intake.get("sha256sum_sha256"),
        "reconstructed_master_sha256sum_sha256": "sha256:" + sha256_text(reconstructed),
        "intake_report": rel(ROOT / "artifacts" / "reports" / f"source-byte-cache-intake-manifest-rev{REV}.json"),
        "receipt_missing_count": int(intake.get("receipt_missing_count") or 0),
        "receipt_present_count": int(intake.get("receipt_present_count") or 0),
        "pinned_source_count": int(intake.get("pinned_source_count") or 0),
        "priority_counts": dict(sorted(priority_counts.items())),
        "family_counts": dict(sorted(family_counts.items())),
        "error_count": len(errors),
        "errors": errors,
        "operator_check_template": "cd /path/to/external-source-cache && sha256sum -c {batch_file}",
        "batch_files": batch_reports,
    }
    return report, files


def main() -> int:
    ap = argparse.ArgumentParser(description="Build per-batch source-byte sha256sum manifests")
    ap.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    ap.add_argument("--report-path", default=str(REPORT))
    ap.add_argument("--out-dir", default=str(OUT_DIR))
    ap.add_argument("--write", action="store_true", help="write report and per-batch sha256sum files")
    ap.add_argument("--json", action="store_true", help="print JSON report")
    args = ap.parse_args()

    try:
        report, files = build_batch_manifests(batch_size=args.batch_size)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    payload = json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n"
    if args.write:
        report_path = Path(args.report_path)
        out_dir = Path(args.out_dir)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        out_dir.mkdir(parents=True, exist_ok=True)
        # Remove stale batch files for older/current revisions from the target directory only.
        for stale in out_dir.glob(f"source-byte-cache-missing-receipts-rev{REV}-batch*.sha256"):
            stale.unlink()
        for path, text in sorted(files.items()):
            target = out_dir / path.name if path.parent != out_dir else path
            target.write_text(text, encoding="utf-8")
        report_path.write_text(payload, encoding="utf-8")
    if args.json or not args.write:
        sys.stdout.write(payload)
    return 0 if int(report.get("error_count") or 0) == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
