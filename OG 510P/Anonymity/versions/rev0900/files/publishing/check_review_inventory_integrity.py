#!/usr/bin/env python3
"""Check that REVIEW_INVENTORY.json names the current unpublished paper universe.

The queue uses the inventory as a review universe, so it must not retain stale
source hashes after paper edits.  This checker validates source membership,
count summaries, bucket summaries, duplicate bindings, queue coverage, and
per-row SHA-256 prefixes against the bytes shipped in the archive.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import pathlib
import sys
from typing import Any


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_prefix(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    inventory = load_json(root / "release_queue" / "REVIEW_INVENTORY.json")
    queue = load_json(root / "release_queue" / "QUEUE_INDEX.json")

    entries = inventory.get("entries", [])
    entry_paths = [str(entry.get("source_tex", "")) for entry in entries]
    actual_paths = sorted(p.relative_to(root).as_posix() for p in (root / "series").rglob("paper.tex"))
    duplicate_paths = sorted(path for path, count in collections.Counter(entry_paths).items() if count > 1)
    missing_from_inventory = sorted(set(actual_paths) - set(entry_paths))
    extra_in_inventory = sorted(set(entry_paths) - set(actual_paths))

    sha_mismatches = []
    missing_files = []
    for entry in entries:
        rel = str(entry.get("source_tex", ""))
        path = root / rel
        if not path.exists():
            missing_files.append(rel)
            continue
        expected = entry.get("sha256_prefix")
        actual = sha256_prefix(path)
        if expected != actual:
            sha_mismatches.append({"source_tex": rel, "expected_prefix": expected, "actual_prefix": actual})

    series_counts = collections.Counter()
    bucket_counts = collections.Counter()
    for entry in entries:
        series_counts[str(entry.get("series", ""))] += 1
        bucket_counts[str(entry.get("review_bucket", ""))] += 1

    queue_sources = []
    for state, items in queue.get("states", {}).items():
        if not isinstance(items, list):
            continue
        for item in items:
            if isinstance(item, dict) and item.get("source_tex"):
                queue_sources.append(str(item["source_tex"]))
    queue_sources_missing_from_inventory = sorted(set(queue_sources) - set(entry_paths))
    unqueued_inventory_paths = sorted(set(entry_paths) - set(queue_sources))
    unqueued_by_bucket = collections.Counter()
    path_to_bucket = {str(entry.get("source_tex", "")): str(entry.get("review_bucket", "")) for entry in entries}
    for rel in unqueued_inventory_paths:
        unqueued_by_bucket[path_to_bucket.get(rel, "unknown")] += 1

    checks = []

    def record(name: str, ok: bool, details: str) -> None:
        checks.append({"name": name, "status": "pass" if ok else "fail", "details": details})

    record(
        "revision_binding",
        inventory.get("generated_for_revision") == release.get("revision"),
        f"inventory={inventory.get('generated_for_revision')} release={release.get('revision')}",
    )
    record(
        "entry_count_matches_series_papers",
        inventory.get("reviewable_unpublished_papers") == len(entries) == len(actual_paths),
        f"inventory_count={inventory.get('reviewable_unpublished_papers')} entries={len(entries)} actual_series_papers={len(actual_paths)}",
    )
    record("no_duplicate_source_tex_entries", not duplicate_paths, "duplicates=" + (", ".join(duplicate_paths[:20]) if duplicate_paths else "none"))
    record("inventory_covers_all_series_papers", not missing_from_inventory, "missing=" + (", ".join(missing_from_inventory[:20]) if missing_from_inventory else "none"))
    record("inventory_has_no_extra_sources", not extra_in_inventory, "extra=" + (", ".join(extra_in_inventory[:20]) if extra_in_inventory else "none"))
    record("all_inventory_sources_exist", not missing_files, "missing_files=" + (", ".join(missing_files[:20]) if missing_files else "none"))
    record("sha256_prefixes_match_current_bytes", not sha_mismatches, f"mismatches={len(sha_mismatches)}")
    record(
        "series_counts_match_entries",
        dict(sorted(series_counts.items())) == inventory.get("series_counts", {}),
        f"computed={dict(sorted(series_counts.items()))} declared={inventory.get('series_counts', {})}",
    )
    record(
        "review_bucket_counts_match_entries",
        dict(sorted(bucket_counts.items())) == inventory.get("review_bucket_counts", {}),
        f"computed={dict(sorted(bucket_counts.items()))} declared={inventory.get('review_bucket_counts', {})}",
    )
    record("queue_sources_are_inventory_sources", not queue_sources_missing_from_inventory, "missing=" + (", ".join(queue_sources_missing_from_inventory[:20]) if queue_sources_missing_from_inventory else "none"))

    failures = [check for check in checks if check["status"] != "pass"]
    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release.get("revision"),
        "checked_bundle": release.get("bundle"),
        "publication_authorized": False,
        "checked_inventory": "release_queue/REVIEW_INVENTORY.json",
        "checks": checks,
        "summary": {
            "checks_passed": len(checks) - len(failures),
            "checks_failed": len(failures),
            "inventory_entry_count": len(entries),
            "actual_series_paper_count": len(actual_paths),
            "queue_source_count": len(set(queue_sources)),
            "unqueued_inventory_entry_count": len(unqueued_inventory_paths),
            "unqueued_by_bucket": dict(sorted(unqueued_by_bucket.items())),
            "sha256_prefix_mismatch_count": len(sha_mismatches),
            "duplicate_source_tex_count": len(duplicate_paths),
        },
        "sha256_prefix_mismatches": sha_mismatches[:100],
        "queue_sources_missing_from_inventory": queue_sources_missing_from_inventory,
        "fail_closed_rule": "If review-inventory integrity fails, default to no queue movement and rebuild REVIEW_INVENTORY from current source bytes before trusting review priority or queue coverage claims.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write-report", default="")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    report = check(root)
    text = json.dumps(report, indent=2) + "\n"
    if args.write_report:
        out = root / args.write_report
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
