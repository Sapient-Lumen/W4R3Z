#!/usr/bin/env python3
"""Build compact human/machine-readable decision surfaces from markdown decision notes."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from collections import Counter

DECISION_RE = re.compile(r"^- ([A-Za-z][A-Za-z /-]+):\s*(.*)$")
FILENAME_TS_RE = re.compile(r"^(\d{4}\.\d{2}\.\d{2})(?:-(\d{4}))?")


def classify_action(stem: str, content: str) -> str:
    lower = stem.lower()
    content_lower = content.lower()
    if "published-ready" in lower:
        return "promote_to_published_ready"
    if "-hold-" in lower or lower.endswith("-hold"):
        return "hold"
    if "-candidate-" in lower or lower.endswith("-candidate"):
        return "candidate_review"
    if "publish" in content_lower and "no publication" not in content_lower:
        return "publication_or_release"
    return "structure_or_no_publication"


def extract_fields(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in text.splitlines():
        m = DECISION_RE.match(line)
        if m:
            key = (
                m.group(1)
                .strip()
                .lower()
                .replace(" ", "_")
                .replace("-", "_")
                .replace("/", "_")
            )
            fields[key] = m.group(2).strip()
    return fields


def first_non_heading_paragraph(text: str) -> str:
    lines = [line.rstrip() for line in text.splitlines()]
    buf: list[str] = []
    for line in lines[1:]:
        if not line.strip():
            if buf:
                break
            continue
        if line.startswith("#"):
            continue
        buf.append(line.strip())
    return " ".join(buf)


def decision_kind(action_class: str) -> str:
    if action_class in {"hold", "candidate_review", "promote_to_published_ready", "publication_or_release"}:
        return "paper-state decision"
    return "archive/control-surface pass"


def build(root: pathlib.Path, revision: str) -> tuple[dict, dict, str]:
    decisions_dir = root / "release_queue" / "decisions"
    paths = sorted(p for p in decisions_dir.glob("*.md"))
    records = []
    for path in paths:
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        stem = path.stem
        lines = text.splitlines()
        heading = lines[0].lstrip("# ").strip() if lines else stem
        fields = extract_fields(text)
        m = FILENAME_TS_RE.match(stem)
        date = m.group(1) if m else ""
        time_hint = m.group(2) if m and m.group(2) else ""
        publication_action = "none" if "no publication" in text.lower() else "unspecified"
        action_class = classify_action(stem, text)
        record = {
            "decision_id": stem,
            "path": rel,
            "date": date,
            "time_hint": time_hint,
            "heading": heading,
            "subject": fields.get("subject", ""),
            "decision": fields.get("decision", ""),
            "state_before": fields.get("state_before", ""),
            "state_after": fields.get("state_after", ""),
            "reason": fields.get("reason", ""),
            "follow_up_needed": fields.get("follow_up_needed", ""),
            "action_class": action_class,
            "kind": decision_kind(action_class),
            "publication_action": publication_action,
            "summary": first_non_heading_paragraph(text),
        }
        records.append(record)

    latest = records[-1] if records else {}
    action_counts = Counter(item["action_class"] for item in records)
    publication_counts = Counter(item["publication_action"] for item in records)
    kind_counts = Counter(item["kind"] for item in records)
    dates = sorted({item["date"] for item in records if item["date"]})

    index = {
        "version": 2,
        "owner": "release_queue/decisions/",
        "generated_for_revision": revision,
        "latest_decision": latest.get("path", ""),
        "decision_count": len(records),
        "action_class_counts": dict(action_counts),
        "publication_action_counts": dict(publication_counts),
        "kind_counts": dict(kind_counts),
        "summary": {
            "total_notes": len(records),
            "first_note": records[0]["path"] if records else "",
            "latest_note": latest.get("path", ""),
            "distinct_decision_dates": len(dates),
        },
        "decisions": list(reversed(records)),
    }
    latest_json = {
        "version": 1,
        "owner": "release_queue/",
        "generated_for_revision": revision,
        **latest,
    }

    lines = [
        "# Decision Index",
        "",
        "This is the compact index over `release_queue/decisions/`.",
        "Use it when you need the decision history without opening the whole directory or guessing which note came last.",
        "",
        "## Summary",
        "",
        f"- Generated for revision: `{revision}`",
        f"- Total decision notes: {len(records)}",
        f"- First decision note: `{records[0]['path']}`" if records else "- First decision note: ``",
        f"- Latest decision note: `{latest.get('path', '')}`",
        f"- Distinct decision dates: {len(dates)}",
        "- Decision counts:",
    ]
    for key, value in sorted(publication_counts.items()):
        lines.append(f"  - {key}: {value}")
    lines.append("- Kind counts:")
    for key, value in sorted(kind_counts.items()):
        lines.append(f"  - {key}: {value}")
    lines.extend([
        "",
        "## Most recent 20 notes",
        "",
        "| Timestamp | Publication action | Kind | Note |",
        "| --- | --- | --- | --- |",
    ])
    for item in reversed(records[-20:]):
        stamp = item["date"] + (f" {item['time_hint']}" if item["time_hint"] else "")
        lines.append(f"| {stamp} | {item['publication_action']} | {item['kind']} | `{item['path']}` |")
    lines.extend([
        "",
        "For the full machine-readable history, use `release_queue/DECISION_INDEX.json`.",
        "",
    ])
    markdown = "\n".join(lines)
    return index, latest_json, markdown


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write-index", default="release_queue/DECISION_INDEX.json")
    parser.add_argument("--write-latest", default="release_queue/LATEST_DECISION.json")
    parser.add_argument("--write-markdown", default="release_queue/DECISION_INDEX.md")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    revision = json.loads((root / "RELEASE_MANIFEST.json").read_text(encoding="utf-8"))["revision"]
    index, latest, markdown = build(root, revision)

    (root / args.write_index).write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    (root / args.write_latest).write_text(json.dumps(latest, indent=2) + "\n", encoding="utf-8")
    (root / args.write_markdown).write_text(markdown, encoding="utf-8")
    sys.stdout.write(
        json.dumps(
            {"index": args.write_index, "latest": args.write_latest, "markdown": args.write_markdown},
            indent=2,
        )
        + "\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
