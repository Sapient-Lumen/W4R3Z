#!/usr/bin/env python3
"""Check that the review inventory closes the unpublished-paper universe.

This is intentionally stricter than the old count-only check.  It verifies every
series paper is represented exactly once, every inventory hash matches shipped
bytes, every queue source binding is reflected, and deliberately unqueued papers
are visible rather than silently outside the review lane.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import pathlib
from typing import Any

QUEUE_STATES = ["candidate", "hold", "published_ready", "published"]


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def queue_bindings(queue_index: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = collections.defaultdict(list)
    for state in QUEUE_STATES:
        for item in queue_index.get("states", {}).get(state, []):
            if not isinstance(item, dict):
                continue
            source = item.get("source_tex")
            if source:
                out[str(source)].append(
                    {
                        "queue_state": state,
                        "item_id": str(item.get("item_id", "")),
                        "path": str(item.get("path", "")),
                        "title": str(item.get("title", "")),
                    }
                )
    return dict(out)


def sorted_bindings(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return sorted(rows, key=lambda row: (row.get("queue_state", ""), row.get("path", ""), row.get("item_id", "")))


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    queue_index = load_json(root / "release_queue" / "QUEUE_INDEX.json")
    inventory = load_json(root / "release_queue" / "REVIEW_INVENTORY.json")
    bindings = queue_bindings(queue_index)
    checks: list[dict[str, Any]] = []

    def record(name: str, ok: bool, details: str, samples: list[Any] | None = None) -> None:
        row = {"name": name, "status": "pass" if ok else "fail", "details": details}
        if samples is not None:
            row["samples"] = samples[:20]
        checks.append(row)

    entries = inventory.get("entries", [])
    sources = [entry.get("source_tex") for entry in entries]
    source_counts = collections.Counter(sources)
    duplicate_inventory_sources = sorted(source for source, count in source_counts.items() if count != 1)
    series_sources = sorted(p.relative_to(root).as_posix() for p in root.glob("series/**/paper.tex"))
    inventory_sources = sorted(str(source) for source in sources if source)
    missing_from_inventory = sorted(set(series_sources) - set(inventory_sources))
    extra_inventory_sources = sorted(set(inventory_sources) - set(series_sources))

    record(
        "revision_binding",
        inventory.get("generated_for_revision") == release["revision"] and inventory.get("generated_from_bundle") == release["bundle"],
        f"inventory_revision={inventory.get('generated_for_revision')} release_revision={release['revision']} inventory_bundle={inventory.get('generated_from_bundle')} release_bundle={release['bundle']}",
    )
    record(
        "series_paper_universe_closed",
        not duplicate_inventory_sources and not missing_from_inventory and not extra_inventory_sources,
        f"series_papers={len(series_sources)} inventory_entries={len(entries)} duplicates={len(duplicate_inventory_sources)} missing={len(missing_from_inventory)} extra={len(extra_inventory_sources)}",
        duplicate_inventory_sources + missing_from_inventory + extra_inventory_sources,
    )

    hash_failures: list[dict[str, str]] = []
    missing_files: list[str] = []
    for entry in entries:
        rel = str(entry.get("source_tex", ""))
        path = root / rel
        if not path.exists():
            missing_files.append(rel)
            continue
        expected = str(entry.get("sha256", ""))
        actual = sha256_file(path)
        if expected != actual:
            hash_failures.append({"source_tex": rel, "expected": expected, "actual": actual})
    record(
        "inventory_hashes_match_shipped_sources",
        not missing_files and not hash_failures,
        f"missing_files={len(missing_files)} hash_failures={len(hash_failures)}",
        missing_files + hash_failures,
    )

    binding_failures: list[dict[str, Any]] = []
    queued_count = 0
    unqueued_count = 0
    unqueued_entries: list[dict[str, str]] = []
    state_source_counts: collections.Counter[str] = collections.Counter()
    bucket_counts: collections.Counter[str] = collections.Counter()
    unqueued_by_bucket: collections.Counter[str] = collections.Counter()
    unqueued_by_series: collections.Counter[str] = collections.Counter()
    for entry in entries:
        rel = str(entry.get("source_tex", ""))
        expected_bindings = sorted_bindings(bindings.get(rel, []))
        actual_bindings = sorted_bindings(entry.get("queue_bindings", []))
        states = sorted({row["queue_state"] for row in expected_bindings})
        bucket = str(entry.get("review_bucket", ""))
        series = str(entry.get("series", ""))
        bucket_counts[bucket] += 1
        for state in states:
            state_source_counts[state] += 1
        if expected_bindings:
            queued_count += 1
        else:
            unqueued_count += 1
            unqueued_by_bucket[bucket] += 1
            unqueued_by_series[series] += 1
            unqueued_entries.append({"source_tex": rel, "series": series, "review_bucket": bucket})
        if actual_bindings != expected_bindings or entry.get("queue_states", []) != states or int(entry.get("queue_binding_count", -1)) != len(expected_bindings):
            binding_failures.append({"source_tex": rel, "expected_bindings": expected_bindings, "actual_bindings": actual_bindings, "expected_states": states, "actual_states": entry.get("queue_states", [])})
    record(
        "queue_bindings_reflected_exactly",
        not binding_failures,
        f"binding_failures={len(binding_failures)}",
        binding_failures,
    )

    queued_sources = set(bindings)
    queue_sources_not_in_inventory = sorted(queued_sources - set(inventory_sources))
    duplicate_queue_bindings = sorted({source: rows for source, rows in bindings.items() if len(rows) > 1}.items(), key=lambda item: item[0])
    record(
        "queue_sources_are_inventory_sources",
        not queue_sources_not_in_inventory and not duplicate_queue_bindings,
        f"queue_sources={len(queued_sources)} missing_from_inventory={len(queue_sources_not_in_inventory)} duplicate_queue_bindings={len(duplicate_queue_bindings)}",
        queue_sources_not_in_inventory + [{"source_tex": source, "bindings": rows} for source, rows in duplicate_queue_bindings],
    )

    queue_coverage = inventory.get("queue_coverage", {})
    coverage_summary_ok = (
        queue_coverage.get("queued_count") == queued_count
        and queue_coverage.get("unqueued_count") == unqueued_count
        and queue_coverage.get("queue_state_source_counts") == dict(sorted(state_source_counts.items()))
        and queue_coverage.get("unqueued_by_bucket") == dict(sorted(unqueued_by_bucket.items()))
        and queue_coverage.get("unqueued_by_series") == dict(sorted(unqueued_by_series.items()))
        and queue_coverage.get("queue_sources_not_in_inventory") == queue_sources_not_in_inventory
        and queue_coverage.get("duplicate_queue_binding_count") == len(duplicate_queue_bindings)
    )
    record(
        "coverage_summary_matches_entries",
        coverage_summary_ok,
        f"queued={queued_count} unqueued={unqueued_count} state_counts={dict(sorted(state_source_counts.items()))} unqueued_by_bucket={dict(sorted(unqueued_by_bucket.items()))}",
    )

    qsum = queue_index.get("summary", {})
    queue_summary_ok = (
        qsum.get("reviewable_unpublished_papers") == len(entries)
        and qsum.get("standalone_series_review_first") == bucket_counts.get("standalone_series_review_first", 0)
        and qsum.get("synthesis_foundation_review_later") == bucket_counts.get("synthesis_foundation_review_later", 0)
        and qsum.get("synthesis_tail_defer_high_churn") == bucket_counts.get("synthesis_tail_defer_high_churn", 0)
    )
    record(
        "queue_summary_matches_review_inventory",
        queue_summary_ok,
        f"queue_summary_reviewable={qsum.get('reviewable_unpublished_papers')} inventory={len(entries)} bucket_counts={dict(sorted(bucket_counts.items()))}",
    )

    # This is an intentional posture check, not a requirement that every paper be queued today.
    # It prevents non-synthesis standalone papers from silently falling outside the queue lane.
    unqueued_posture_ok = all(row["series"] == "synthesis" and row["review_bucket"] == "synthesis_foundation_review_later" for row in unqueued_entries)
    record(
        "unqueued_sources_are_visible_synthesis_foundations",
        unqueued_posture_ok,
        f"unqueued_count={unqueued_count} unqueued_by_series={dict(sorted(unqueued_by_series.items()))} unqueued_by_bucket={dict(sorted(unqueued_by_bucket.items()))}",
        [row for row in unqueued_entries if row["series"] != "synthesis" or row["review_bucket"] != "synthesis_foundation_review_later"],
    )

    failures = [row for row in checks if row["status"] != "pass"]
    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "inventory_version": inventory.get("inventory_version"),
        "checks": checks,
        "summary": {
            "checks_passed": len(checks) - len(failures),
            "checks_failed": len(failures),
            "series_paper_count": len(series_sources),
            "inventory_entry_count": len(entries),
            "queued_inventory_count": queued_count,
            "unqueued_inventory_count": unqueued_count,
            "queue_source_count": len(queued_sources),
            "queue_state_source_counts": dict(sorted(state_source_counts.items())),
            "unqueued_by_bucket": dict(sorted(unqueued_by_bucket.items())),
            "unqueued_by_series": dict(sorted(unqueued_by_series.items())),
        },
        "visible_unqueued_sources": sorted(unqueued_entries, key=lambda row: row["source_tex"]),
        "fail_closed_rule": "If the review inventory no longer closes the unpublished-paper universe or drifts from queue bindings, default to no publication and rebuild the review inventory before choosing release work.",
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
    print(text, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
