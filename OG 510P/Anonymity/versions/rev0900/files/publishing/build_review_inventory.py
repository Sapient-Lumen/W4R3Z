#!/usr/bin/env python3
"""Rebuild release_queue/REVIEW_INVENTORY.{json,md} from paper sources.

The review inventory is a source-identity surface, not just a paper list.  Its
hash and queue-binding fields must reflect the current shipped bytes and queue
records so review work cannot silently point at older or unqueued paper
identities.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import pathlib
import re
import sys
from typing import Any

PAT_TITLE = re.compile(r"\\title\{(.+?)\}", re.S)
PAT_DATE = re.compile(r"\\date\{(.+?)\}", re.S)
QUEUE_STATES = ["candidate", "hold", "published_ready", "published"]


def clean_title(raw: str) -> str:
    s = raw.replace("\\large", " ")
    s = s.replace("\\textbf{", "")
    s = s.replace("\\texorpdfstring", " ")
    s = s.replace("\\", " ")
    s = s.replace("{", " ").replace("}", " ")
    return " ".join(s.split()).strip()


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def bucket_for(rel: str, paper_dir: str) -> tuple[str, str, list[str], list[str]]:
    parts = rel.split("/")
    top = parts[1] if len(parts) > 1 and parts[0] == "series" else parts[0]
    bucket = "standalone_series_review_first"
    priority = "review sooner"
    churn: list[str] = []
    notes: list[str] = []

    if top == "synthesis":
        m = re.match(r"paper(\d+)", paper_dir)
        num = int(m.group(1)) if m else None
        if num is not None and num >= 31:
            bucket = "synthesis_tail_defer_high_churn"
            priority = "defer by default"
            notes.append("Late synthesis paper; review only after foundation and standalone-series decisions.")
            if num >= 59:
                churn.append("Patch notes v228-v236 repeatedly extended the source-only successor/reissue sub-tail (papers 65-73).")
            else:
                churn.append("Part of the successor-maintenance / challenge-answer decomposition tail.")
        else:
            bucket = "synthesis_foundation_review_later"
            priority = "review after standalone families"
            notes.append("Early synthesis foundation paper; likely important, but not the first public entrypoint to review.")
        if num == 17:
            churn.append("Worked example was repeatedly bumped through archive revisions up to worked-example-draft-133.")
            priority = "defer until surrounding spine is calmer"
        if num == 24:
            notes.append("Crosswalk paper; useful for orientation, but not obviously the first new public entrypoint.")
    else:
        notes.append("Standalone or semi-standalone series paper; safer early review target than the synthesis tail.")
    return bucket, priority, churn, notes


def queue_bindings(queue_index: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = collections.defaultdict(list)
    for state in QUEUE_STATES:
        for item in queue_index.get("states", {}).get(state, []):
            if not isinstance(item, dict):
                continue
            source = item.get("source_tex")
            if not source:
                continue
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


def build(root: pathlib.Path) -> tuple[dict[str, Any], str]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    queue_index = load_json(root / "release_queue" / "QUEUE_INDEX.json")
    revision = str(release.get("revision", "unknown"))
    timestamp = str(release.get("timestamp", ""))
    generated_on = timestamp[:10].replace(".", "-") if timestamp else "unknown"
    bindings = queue_bindings(queue_index)

    entries: list[dict[str, Any]] = []
    series_counts: collections.Counter[str] = collections.Counter()
    bucket_counts: collections.Counter[str] = collections.Counter()
    state_source_counts: collections.Counter[str] = collections.Counter()
    unqueued_by_bucket: collections.Counter[str] = collections.Counter()
    unqueued_by_series: collections.Counter[str] = collections.Counter()

    source_root = root / "series"
    for p in sorted(source_root.rglob("paper.tex")):
        rel = p.relative_to(root).as_posix()
        text = p.read_text(encoding="utf-8", errors="replace")
        title_raw = PAT_TITLE.search(text)
        date_raw = PAT_DATE.search(text)
        paper_dir = p.parent.name
        bucket, priority, churn, notes = bucket_for(rel, paper_dir)
        parts = rel.split("/")
        top = parts[1] if len(parts) > 1 and parts[0] == "series" else parts[0]
        qrows = sorted_bindings(bindings.get(rel, []))
        qstates = sorted({row["queue_state"] for row in qrows})
        digest = sha256_file(p)
        entry = {
            "source_tex": rel,
            "series": top,
            "paper_dir": paper_dir,
            "title_plain": clean_title(title_raw.group(1).strip() if title_raw else ""),
            "date_raw": date_raw.group(1).strip() if date_raw else "",
            "review_bucket": bucket,
            "initial_review_priority": priority,
            "churn_signals": churn,
            "notes": notes,
            "sha256": digest,
            "sha256_prefix": digest[:16],
            "queue_binding_count": len(qrows),
            "queue_states": qstates,
            "queue_bindings": qrows,
            "queue_visibility": "queued" if qrows else "not_queued_explicitly_visible",
        }
        entries.append(entry)
        series_counts[top] += 1
        bucket_counts[bucket] += 1
        if qrows:
            for state in qstates:
                state_source_counts[state] += 1
        else:
            unqueued_by_bucket[bucket] += 1
            unqueued_by_series[top] += 1

    inventory_sources = {entry["source_tex"] for entry in entries}
    queued_sources = set(bindings)
    queue_sources_not_in_inventory = sorted(queued_sources - inventory_sources)
    duplicate_queue_bindings = [
        {"source_tex": source, "bindings": sorted_bindings(rows)}
        for source, rows in sorted(bindings.items())
        if len(rows) > 1
    ]
    queued_count = sum(1 for entry in entries if entry["queue_bindings"])
    unqueued_count = len(entries) - queued_count

    queue_coverage = {
        "queued_count": queued_count,
        "unqueued_count": unqueued_count,
        "queue_state_source_counts": dict(sorted(state_source_counts.items())),
        "unqueued_by_bucket": dict(sorted(unqueued_by_bucket.items())),
        "unqueued_by_series": dict(sorted(unqueued_by_series.items())),
        "queue_sources_not_in_inventory": queue_sources_not_in_inventory,
        "duplicate_queue_binding_count": len(duplicate_queue_bindings),
        "duplicate_queue_bindings": duplicate_queue_bindings,
        "interpretation": "Unqueued papers remain visible in the inventory. Current allowed unqueued posture is synthesis foundation papers only; standalone families must appear in an explicit queue state.",
    }

    data: dict[str, Any] = {
        "inventory_version": 3,
        "generated_for_revision": revision,
        "generated_from_bundle": release.get("bundle", ""),
        "generated_timestamp": timestamp,
        "generated_on": generated_on,
        "owner": "release_queue/",
        "reviewable_unpublished_papers": len(entries),
        "series_counts": dict(sorted(series_counts.items())),
        "review_bucket_counts": dict(sorted(bucket_counts.items())),
        "queue_coverage": queue_coverage,
        "entries": entries,
    }

    lines = [
        "# Review Inventory",
        "",
        f"- Generated for revision: `{revision}`",
        f"- Generated from bundle: `{release.get('bundle', '')}`",
        f"- Generated on: {generated_on}",
        f"- Reviewable unpublished papers: {len(entries)}",
        f"- Explicitly queued sources: {queued_count}",
        f"- Visible but unqueued sources: {unqueued_count}",
        f"- Standalone-series review-first papers: {bucket_counts.get('standalone_series_review_first', 0)}",
        f"- Early synthesis foundations (review later): {bucket_counts.get('synthesis_foundation_review_later', 0)}",
        f"- Late synthesis tail (defer by default): {bucket_counts.get('synthesis_tail_defer_high_churn', 0)}",
        "",
        "Every row in `release_queue/REVIEW_INVENTORY.json` carries the current SHA-256 over the shipped `paper.tex` bytes and an exact copy of any queue binding for that source.",
        "Run `python3 -B publishing/check_review_inventory_coverage.py --root .` and `python3 -B publishing/check_review_inventory_integrity.py --root .` after editing, adding, removing, or renaming any paper source or queue note.",
        "",
        "See `release_queue/REVIEW_INVENTORY.json` for the full machine-readable inventory.",
        "",
    ]
    return data, "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write-json", default="release_queue/REVIEW_INVENTORY.json")
    parser.add_argument("--write-markdown", default="release_queue/REVIEW_INVENTORY.md")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    data, markdown = build(root)
    (root / args.write_json).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    (root / args.write_markdown).write_text(markdown, encoding="utf-8")
    sys.stdout.write(json.dumps({"status": "pass", "entry_count": len(data["entries"]), "queued_count": data["queue_coverage"]["queued_count"], "revision": data.get("generated_for_revision")}, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
