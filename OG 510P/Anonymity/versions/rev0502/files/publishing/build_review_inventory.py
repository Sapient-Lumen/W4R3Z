#!/usr/bin/env python3
"""Rebuild release_queue/REVIEW_INVENTORY.{json,md} from paper sources.

This script is intentionally simple so a future operator can rerun it after adding or renaming papers.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
PAT_TITLE = re.compile(r"\\title\{(.+?)\}", re.S)
PAT_DATE = re.compile(r"\\date\{(.+?)\}", re.S)


def clean_title(raw: str) -> str:
    s = raw.replace("\\large", " ")
    s = s.replace("\\textbf{", "")
    s = s.replace("\\texorpdfstring", " ")
    s = s.replace("\\", " ")
    s = s.replace("{", " ").replace("}", " ")
    return " ".join(s.split()).strip()


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


def main() -> None:
    entries = []
    series_counts: dict[str, int] = {}
    bucket_counts: dict[str, int] = {}

    for p in sorted(ROOT.rglob("paper.tex")):
        if "published" in p.parts:
            continue
        rel = p.relative_to(ROOT).as_posix()
        text = p.read_text(encoding="utf-8", errors="ignore")
        title_raw = PAT_TITLE.search(text)
        date_raw = PAT_DATE.search(text)
        paper_dir = p.parent.name
        bucket, priority, churn, notes = bucket_for(rel, paper_dir)
        parts = rel.split("/")
        top = parts[1] if len(parts) > 1 and parts[0] == "series" else parts[0]
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
            "sha256_prefix": hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()[:16],
        }
        entries.append(entry)
        series_counts[top] = series_counts.get(top, 0) + 1
        bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1

    out_json = ROOT / "release_queue" / "REVIEW_INVENTORY.json"
    out_json.write_text(
        json.dumps(
            {
                "inventory_version": 1,
                "generated_on": "2026-03-16",
                "reviewable_unpublished_papers": len(entries),
                "series_counts": dict(sorted(series_counts.items())),
                "review_bucket_counts": dict(sorted(bucket_counts.items())),
                "entries": entries,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Review Inventory",
        "",
        f"- Reviewable unpublished papers: {len(entries)}",
        f"- Standalone-series review-first papers: {bucket_counts.get('standalone_series_review_first', 0)}",
        f"- Early synthesis foundations (review later): {bucket_counts.get('synthesis_foundation_review_later', 0)}",
        f"- Late synthesis tail (defer by default): {bucket_counts.get('synthesis_tail_defer_high_churn', 0)}",
        "",
        "See `release_queue/REVIEW_INVENTORY.json` for the full machine-readable inventory.",
    ]
    (ROOT / "release_queue" / "REVIEW_INVENTORY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
