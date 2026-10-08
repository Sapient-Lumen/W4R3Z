#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter

from archive_meta import GENERATED, METADATA_DIR, ROOT, current_revision, generated_at_utc
from metadata_surface import cell, sorted_counts, write_json_and_markdown


def render_markdown(data: dict) -> str:
    lines = [
        "# Outcome-tail sampling plans",
        "",
        f"Generated for `{data['revision']}` from `{data['outcome_tail_plan_source']}`.",
        "",
        data.get("plan_role", ""),
        "",
        "## Privacy posture",
        "",
        data.get("privacy_posture", ""),
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Plans | {data['plan_count']} |",
        f"| Cohorts | {data['cohort_count']} |",
        f"| Outcome-tail fields | {len(data.get('outcome_tail_field_counts', {}))} |",
        "",
        "## Gap coverage",
        "",
        "| Gap | Plans |",
        "| --- | --- |",
    ]
    for gap, plans in data.get("gap_plan_map", {}).items():
        lines.append(f"| `{gap}` | {', '.join(f'`{pid}`' for pid in plans)} |")
    lines.extend(["", "## Outcome-tail fields", "", "| Field | Count |", "| --- | ---: |"])
    for field, count in data.get("outcome_tail_field_counts", {}).items():
        lines.append(f"| `{field}` | {count} |")
    lines.extend(["", "## Plans", ""])
    for plan in data.get("plans", []):
        lines.extend([
            f"### `{plan['plan_id']}` — `{plan['case_family']}`",
            "",
            f"Closure floor: {plan['closure_floor']}",
            "",
            "| Cohort | Denominator role | Exclusion risk |",
            "| --- | --- | --- |",
        ])
        for cohort in plan.get("cohorts", []):
            lines.append(
                f"| `{cohort.get('cohort_id')}` | {cell(cohort.get('denominator_role'))} | {cell(cohort.get('exclusion_risk'))} |"
            )
        lines.extend(["", f"First next action: {plan.get('first_next_action', '')}", ""])
    return "\n".join(lines)


def main() -> None:
    GENERATED.mkdir(exist_ok=True)
    source = METADATA_DIR / "outcome_tail_plans.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    plans = []
    gap_plan_map: dict[str, list[str]] = {}
    field_counts: Counter[str] = Counter()
    cohort_count = 0
    for plan_id, plan in sorted(payload.get("plans", {}).items()):
        for gap_id in plan.get("linked_gaps", []):
            gap_plan_map.setdefault(gap_id, []).append(plan_id)
        field_counts.update(plan.get("outcome_tail_fields", []))
        cohort_count += len(plan.get("cohorts", []))
        plans.append({"plan_id": plan_id, **plan})
    data = {
        "revision": current_revision(),
        "generated_at_utc": generated_at_utc(),
        "outcome_tail_plan_source": str(source.relative_to(ROOT)),
        "plan_role": payload.get("plan_role", ""),
        "privacy_posture": payload.get("privacy_posture", ""),
        "plan_count": len(plans),
        "cohort_count": cohort_count,
        "plans": plans,
        "gap_plan_map": {k: sorted(v) for k, v in sorted(gap_plan_map.items())},
        "outcome_tail_field_counts": sorted_counts(field_counts),
    }
    write_json_and_markdown(GENERATED, "OUTCOME_TAIL_PLANS", data, render_markdown(data))
    print("OK: wrote generated/OUTCOME_TAIL_PLANS.json and generated/OUTCOME_TAIL_PLANS.md")


if __name__ == "__main__":
    main()
