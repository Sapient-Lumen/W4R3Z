#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter

from archive_meta import GENERATED, METADATA_DIR, ROOT, current_revision, generated_at_utc

GAP_INPUT = METADATA_DIR / "gap_ledger.json"

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium_high": 2, "medium": 3, "low": 4}
STATUS_ORDER = {"next_candidate": 0, "open": 1, "queued": 2, "maintenance_queue": 3}


def status_rank(status: str) -> int:
    if status.startswith("repaired_rev"):
        return 4
    return STATUS_ORDER.get(status, 99)


def render_markdown(data: dict) -> str:
    lines = [
        "# Gap ledger",
        "",
        f"Generated for `{data['revision']}` from `metadata/gap_ledger.json`.",
        "",
        "This is intentionally small: it records high-risk missing domains and the next artifact needed, not an invitation to add registries instead of cases.",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Gaps | {data['gap_count']} |",
        "",
        "## Gaps",
        "",
        "| Gap | Status | Severity | Next artifact |",
        "| --- | --- | --- | --- |",
    ]
    for gap in data.get("gaps", []):
        lines.append(f"| `{gap['gap_id']}` {gap['missing_domain']} | `{gap['status']}` | `{gap['severity']}` | {gap['next_artifact']} |")
    lines.extend(["", "## Detail", ""])
    for gap in data.get("gaps", []):
        notes = ", ".join(f"`{n}`" for n in gap.get("nearest_notes", [])) or "—"
        keys = ", ".join(f"`{k}`" for k in gap.get("source_keys", [])) or "—"
        lines.extend([
            f"### `{gap['gap_id']}` — {gap['severity']} / {gap['status']}",
            "",
            gap.get("why_it_matters", ""),
            "",
            f"Nearest notes: {notes}",
            "",
            f"Source keys: {keys}",
            "",
            f"Next artifact: {gap.get('next_artifact', '')}",
            "",
            f"Why not now: {gap.get('why_not_now', '')}",
            "",
        ])
    return "\n".join(lines)


def main() -> None:
    GENERATED.mkdir(exist_ok=True)
    payload = json.loads(GAP_INPUT.read_text(encoding="utf-8"))
    gaps = []
    status_counts: Counter[str] = Counter()
    severity_counts: Counter[str] = Counter()
    for gap_id, gap in payload.get("gaps", {}).items():
        item = {"gap_id": gap_id, **gap}
        status_counts[item.get("status", "unknown")] += 1
        severity_counts[item.get("severity", "unknown")] += 1
        gaps.append(item)
    gaps.sort(key=lambda item: (status_rank(item.get("status", "")), SEVERITY_ORDER.get(item.get("severity"), 99), item.get("gap_id", "")))
    data = {
        "revision": current_revision(),
        "generated_at_utc": generated_at_utc(),
        "gap_ledger_source": str(GAP_INPUT.relative_to(ROOT)),
        "ledger_role": payload.get("ledger_role", ""),
        "review_date": payload.get("review_date"),
        "gap_count": len(gaps),
        "status_counts": dict(sorted(status_counts.items())),
        "severity_counts": dict(sorted(severity_counts.items())),
        "gaps": gaps,
    }
    (GENERATED / "GAP_LEDGER.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (GENERATED / "GAP_LEDGER.md").write_text(render_markdown(data), encoding="utf-8")
    print("OK: wrote generated/GAP_LEDGER.json and generated/GAP_LEDGER.md")


if __name__ == "__main__":
    main()
