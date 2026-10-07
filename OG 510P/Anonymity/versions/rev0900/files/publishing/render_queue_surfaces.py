#!/usr/bin/env python3
"""Render human queue-facing markdown surfaces from compact queue/decision state."""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Iterable


def load_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _summary_line(latest: dict) -> str:
    summary = (latest.get("summary") or "").strip()
    if summary:
        return summary
    heading = (latest.get("heading") or "").strip()
    if heading:
        return heading
    return "No summary available."


def render_status_md(root: pathlib.Path) -> str:
    queue_index = load_json(root / "release_queue" / "QUEUE_INDEX.json")
    review_inventory = load_json(root / "release_queue" / "REVIEW_INVENTORY.json")
    latest = load_json(root / "release_queue" / "LATEST_DECISION.json")
    decision_index = load_json(root / "release_queue" / "DECISION_INDEX.json")
    q = queue_index["summary"]
    buckets = review_inventory["review_bucket_counts"]
    lines = [
        "# Release Queue Status",
        "",
        "_Generated from `release_queue/QUEUE_INDEX.json`, `release_queue/REVIEW_INVENTORY.json`, `release_queue/LATEST_DECISION.json`, and `release_queue/DECISION_INDEX.json`. Do not edit by hand; rerun `python3 -B publishing/render_queue_surfaces.py --root .` or `make rebuild-surfaces`._",
        "",
        "## Current queue summary",
        "",
        f"- Candidates: {q['candidate']}",
        f"- Hold notes: {q['hold']} explicit paper-level holds in queue directories",
        f"- Locally reviewed / publication-blocked (`published_ready`): {q['published_ready']}",
        f"- New post-policy published entries: {q.get('published', 0)}",
        f"- Reviewable unpublished papers inventoried: {q['reviewable_unpublished_papers']}",
        f"- Standalone-series review-first papers: {buckets['standalone_series_review_first']}",
        f"- Early synthesis foundations (review later): {buckets['synthesis_foundation_review_later']}",
        f"- Late synthesis tail (defer by default): {buckets['synthesis_tail_defer_high_churn']}",
        "",
        "## Current posture",
        "",
        f"- Latest decision note: `{latest['path']}`",
        f"- Latest decision heading: {latest.get('heading', '').strip()}",
        f"- Latest decision kind: {latest.get('kind', '')}",
        f"- Latest decision publication action: {latest.get('publication_action', '')}",
        f"- Latest decision summary: {_summary_line(latest)}",
        f"- Total recorded decision notes: {decision_index['decision_count']}",
        "- Default safe action when compact surfaces disagree: no publication until the trust surfaces agree again.",
        "",
        "## Legacy/public distinction",
        "",
        "- Legacy already-published work remains public under the Mathematics-era wiki links listed in `published/LEGACY_PUBLISHED_LINKS.md`.",
        "- New releases, when they eventually happen, must use the Anonymity naming rule.",
        "",
        "## Next safe kinds of work",
        "",
        "1. close one theorem/evidence gap in a standalone source,",
        "2. repair one concrete verifier or compile failure,",
        "3. shrink one duplicated hot-path surface without deleting its source of truth,",
        "4. or record one evidence-backed queue move.",
        "",
        "## Additional orientation",
        "",
        "- `release_queue/REVIEW_INVENTORY.md` is the source-of-truth paper list for future review turns.",
        "- `publishing/REVIEW_ORDER.md` combines review order and family triage, including why high-churn families should be reviewed later.",
        "- `publishing/CONTROL_SURFACES.md` answers \"which file should I trust for this question?\" without relying on memory.",
        "- `reports/lifecycle_gate_status.json` answers \"which compact surface matters right now?\" before the operator widens into longer docs.",
        "- `DATACUBE_TRANSFER_LEDGER.md` answers \"did we already steal this idea from another datacube, and why?\".",
        "",
        "## Fast machine surfaces",
        "",
        "- `release_queue/LATEST_DECISION.json` gives the latest decision in a compact machine-readable form.",
        "- `release_queue/DECISION_INDEX.json` gives the cumulative machine-readable decision history.",
        "- `reports/lifecycle_gate_status.json` gives the compact stage-by-stage gate status.",
        "",
    ]
    return "\n".join(lines)


def _render_state_block(title: str, items: list[dict], empty_line: str) -> list[str]:
    if not items:
        return [f"- {title}: 0", f"  - {empty_line}"]
    lines = [f"- {title}: {len(items)} explicit entries"]
    for item in items:
        lines.append(f"  - `{item['path']}`")
    return lines


def render_queue_md(root: pathlib.Path) -> str:
    queue_index = load_json(root / "release_queue" / "QUEUE_INDEX.json")
    latest = load_json(root / "release_queue" / "LATEST_DECISION.json")
    states = queue_index["states"]
    lines = [
        "# Queue Ledger",
        "",
        "_Generated from `release_queue/QUEUE_INDEX.json` and `release_queue/LATEST_DECISION.json`. Do not edit by hand; rerun `python3 -B publishing/render_queue_surfaces.py --root .` or `make rebuild-surfaces`._",
        "",
        "## Current status",
        "",
        f"- Generated for revision: `{queue_index.get('generated_for_revision', '')}`",
        f"- Latest decision note: `{latest['path']}`",
        f"- Latest decision summary: {_summary_line(latest)}",
        f"- Published queue: {queue_index['summary'].get('published', 0)} post-policy Anonymity publications",
    ]
    lines.extend(_render_state_block("Locally reviewed / publication-blocked (`published_ready`)", states["published_ready"], "none"))
    lines.extend(_render_state_block("Candidate queue", states["candidate"], "none"))
    lines.extend(_render_state_block("Hold queue", states["hold"], "none"))
    lines.extend([
        "",
        "## Safe interpretation",
        "",
        "The queue is intentionally conservative.",
        "Use `release_queue/LATEST_DECISION.md` for the newest rationale, `release_queue/DECISION_INDEX.md` for the compact history, and `reports/lifecycle_gate_status.json` for the current gate statuses.",
        "",
        "## Operating rule",
        "",
        "When a paper is moved:",
        "",
        "- add a written decision note under `release_queue/decisions/`,",
        "- place a short state file in the relevant queue subdirectory,",
        "- rerun the queue-surface renderer and trust checks, and",
        "- do not move more than the evidence justifies.",
        "",
        "## Review universe",
        "",
        "Paper-level review should start from the inventory, not from ad hoc repo browsing.",
        "Use `release_queue/REVIEW_INVENTORY.md` and `publishing/REVIEW_ORDER.md`.",
        "",
        "## Fast machine surfaces",
        "",
        "- `release_queue/LATEST_DECISION.json` gives the latest decision in a compact machine-readable form.",
        "- `release_queue/DECISION_INDEX.json` gives the cumulative machine-readable decision history.",
        "- `reports/lifecycle_gate_status.json` gives the compact stage-by-stage gate status.",
        "",
    ])
    return "\n".join(lines)


def render_latest_decision_md(root: pathlib.Path) -> str:
    latest = load_json(root / "release_queue" / "LATEST_DECISION.json")
    lines = [
        "# Latest decision",
        "",
        "_Generated from `release_queue/LATEST_DECISION.json`. Do not edit by hand; rerun `python3 -B publishing/render_queue_surfaces.py --root .` or `make rebuild-surfaces`._",
        "",
        "Latest decision note:",
        "",
        f"- `{latest['path']}`",
        "",
        "Machine-readable companions:",
        "",
        "- `release_queue/LATEST_DECISION.json`",
        "- `release_queue/DECISION_INDEX.md`",
        "- `release_queue/DECISION_INDEX.json`",
        "",
        "Summary:",
        "",
        f"- Heading: {latest.get('heading', '').strip()}",
        f"- Date: {latest.get('date', '')}",
        f"- Time hint: {latest.get('time_hint', '') or 'none'}",
        f"- Kind: {latest.get('kind', '')}",
        f"- Publication action: {latest.get('publication_action', '')}",
        f"- Action class: {latest.get('action_class', '')}",
        f"- Summary: {_summary_line(latest)}",
        "",
    ]
    return "\n".join(lines)


def render_all(root: pathlib.Path) -> dict[str, str]:
    return {
        "release_queue/STATUS.md": render_status_md(root),
        "release_queue/QUEUE.md": render_queue_md(root),
        "release_queue/LATEST_DECISION.md": render_latest_decision_md(root),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    outputs = render_all(root)
    for rel, text in outputs.items():
        (root / rel).write_text(text, encoding="utf-8")
    print(json.dumps({"rendered": list(outputs.keys())}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
