#!/usr/bin/env python3
"""Build host-scoped sha256sum slices for the first source-byte batch.

Batch 01 is operator-sized, but it is still host-mixed. In a network-capable
run, a single slow/blocked host can waste attention or obscure which same-host
objects should be retried together. This helper splits the current batch into
strict host-scoped sha256sum files without fetching the network or writing
receipts. The files remain ordinary batch files accepted by
``scripts/fetch_source_byte_batch.py``.
"""
from __future__ import annotations

import argparse
import hashlib
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

# Import the current intake builder so host slices inherit the same source-byte
# priority/order semantics as the queue, intake manifest, and batch manifests.
sys.path.insert(0, str(ROOT / "scripts"))
from build_source_byte_cache_intake_manifest import build_manifest as build_intake_manifest  # noqa: E402

VERSION = _archive_version(ROOT)
REV = VERSION.removeprefix("v").zfill(4)
DEFAULT_BATCH = ROOT / "artifacts" / "source_byte_cache_intake" / "batches" / f"source-byte-cache-missing-receipts-rev{REV}-batch01.sha256"
OUT_DIR = ROOT / "artifacts" / "source_byte_cache_intake" / "host_slices"
REPORT = ROOT / "artifacts" / "reports" / f"source-byte-batch-host-slices-rev{REV}.json"
SAFE_SLUG_RE = re.compile(r"[^a-z0-9._-]+")
BOUNDARY = (
    "Source-byte batch host slices are no-network operator routing handoffs. "
    "They split an already governed sha256sum batch by URL host; they bundle no "
    "third-party bytes, write no receipts, do not prove source-byte cache "
    "completeness, are not source-byte cache completeness, and are not "
    "current voter instruction, not legal advice, "
    "not public-release authorization, and not live-pilot approval."
)


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except Exception:
        return str(path)


def host_slug(host: str) -> str:
    slug = SAFE_SLUG_RE.sub("-", str(host or "no-host").lower()).strip(".-_") or "no-host"
    if len(slug) <= 70:
        return slug
    return slug[:54].rstrip(".-_") + "-" + hashlib.sha256(slug.encode("utf-8")).hexdigest()[:12]


def slice_path(index: int, host: str, *, out_dir: Path = OUT_DIR) -> Path:
    return out_dir / f"source-byte-cache-host-slice-rev{REV}-batch01-{index:02d}-{host_slug(host)}.sha256"


def fetch_command(path: Path) -> str:
    report_name = path.with_suffix(".fetch-report.json").name
    report_path = ROOT / "artifacts" / "reports" / report_name
    return (
        "python3 scripts/fetch_source_byte_batch.py "
        f"--batch-file {rel(path)} "
        "--cache-dir /path/to/external-source-cache "
        "--write-receipts --write-report "
        f"--report-path {rel(report_path)}"
    )


def build_host_slices(*, batch_file: Path = DEFAULT_BATCH) -> tuple[dict[str, Any], dict[Path, str]]:
    batch_entries = parse_strict_sha256sum_batch(batch_file)
    intake, _master_text = build_intake_manifest(batch_size=20)
    intake_rows = [r for r in (intake.get("rows") or []) if isinstance(r, dict)]
    by_line = {(str(r.get("expected_sha256") or ""), str(r.get("local_filename") or "")): r for r in intake_rows}

    rows: list[dict[str, Any]] = []
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    errors: list[str] = []
    for entry in batch_entries:
        key = (str(entry["expected_sha256"]), str(entry["local_filename"]))
        src = by_line.get(key)
        if src is None:
            errors.append(f"batch_entry_not_in_current_intake:{entry['local_filename']}")
            continue
        host = str(src.get("url_host") or "no-host") or "no-host"
        row = {
            "source_id": str(src.get("source_id") or ""),
            "line_number": int(entry["line_number"]),
            "priority_tier": str(src.get("priority_tier") or ""),
            "source_family": str(src.get("source_family") or ""),
            "url_host": host,
            "local_filename": str(entry["local_filename"]),
            "expected_sha256": str(entry["expected_sha256"]),
        }
        rows.append(row)
        groups[host].append(row)

    # Largest same-host batches first; stable host name tie-break. This puts the
    # highest-yield host run at the top without changing the underlying batch.
    ordered_hosts = sorted(groups, key=lambda h: (-len(groups[h]), h))
    files: dict[Path, str] = {}
    host_reports: list[dict[str, Any]] = []
    reconstructed_lines: list[str] = []
    seen_sources: set[str] = set()
    duplicate_sources: list[str] = []

    for index, host in enumerate(ordered_hosts, start=1):
        host_rows = sorted(groups[host], key=lambda r: int(r["line_number"]))
        lines = [sha256sum_line(r) for r in host_rows]
        text = "\n".join(lines) + ("\n" if lines else "")
        path = slice_path(index, host)
        files[path] = text
        source_ids = [str(r["source_id"]) for r in host_rows]
        for sid in source_ids:
            if sid in seen_sources:
                duplicate_sources.append(sid)
            seen_sources.add(sid)
        reconstructed_lines.extend(lines)
        host_reports.append(
            {
                "host_slice_index": index,
                "url_host": host,
                "path": rel(path),
                "line_count": len(lines),
                "sha256sum_sha256": "sha256:" + sha256_text(text),
                "source_ids": source_ids,
                "operator_fetch_command": fetch_command(path),
            }
        )

    original_text = "\n".join(sha256sum_line(e) for e in batch_entries) + "\n"
    # Host-slice reconstruction is set-based because slices are sorted by host
    # yield, not by the original line order.
    if sorted(reconstructed_lines) != sorted(original_text.strip().splitlines()):
        errors.append("host_slices_do_not_reconstruct_batch01_line_set")
    if duplicate_sources:
        errors.append("duplicate_source_ids_in_host_slices:" + ",".join(sorted(set(duplicate_sources))))

    host_counts = Counter(str(r["url_host"]) for r in rows)
    report = {
        "archive_version": VERSION,
        "release_date": _release_date(ROOT),
        "synthetic_only": True,
        "boundary": BOUNDARY,
        "network_io": False,
        "third_party_bytes_bundled": False,
        "scope": "batch01-host-slices",
        "batch_file": rel(batch_file),
        "batch_file_entry_count": len(batch_entries),
        "host_slice_count": len(host_reports),
        "dominant_host": ordered_hosts[0] if ordered_hosts else "",
        "dominant_host_entry_count": len(groups[ordered_hosts[0]]) if ordered_hosts else 0,
        "host_counts": dict(sorted(host_counts.items())),
        "slice_dir": rel(OUT_DIR),
        "error_count": len(errors),
        "errors": errors,
        "operator_next_commands": [h["operator_fetch_command"] for h in host_reports[:3]],
        "host_slices": host_reports,
        "rows": rows,
    }
    return report, files


def main() -> int:
    ap = argparse.ArgumentParser(description="Build host-scoped source-byte batch01 sha256sum slices")
    ap.add_argument("--batch-file", default=str(DEFAULT_BATCH))
    ap.add_argument("--out-dir", default=str(OUT_DIR))
    ap.add_argument("--report-path", default=str(REPORT))
    ap.add_argument("--write", action="store_true", help="write report and host-slice sha256sum files")
    ap.add_argument("--json", action="store_true", help="print JSON report")
    args = ap.parse_args()

    try:
        report, files = build_host_slices(batch_file=Path(args.batch_file))
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    payload = json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n"
    if args.write:
        out_dir = Path(args.out_dir)
        report_path = Path(args.report_path)
        out_dir.mkdir(parents=True, exist_ok=True)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        for stale in out_dir.glob(f"source-byte-cache-host-slice-rev{REV}-batch01-*.sha256"):
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
