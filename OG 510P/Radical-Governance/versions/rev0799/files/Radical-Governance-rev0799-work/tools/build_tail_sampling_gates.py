#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter

from archive_meta import GENERATED, METADATA_DIR, ROOT, current_revision, generated_at_utc
from metadata_surface import cell, sorted_counts, write_json_and_markdown


def render_markdown(data: dict) -> str:
    lines = [
        "# Tail sampling gates",
        "",
        f"Generated for `{data['revision']}` from `{data['tail_sampling_gate_source']}`.",
        "",
        data.get("gate_role", ""),
        "",
        "## Privacy posture",
        "",
        data.get("privacy_posture", ""),
        "",
        "## Closure policy",
        "",
        data.get("closure_policy", ""),
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Gates | {data['gate_count']} |",
        f"| Cohort gate rows | {data['cohort_gate_count']} |",
        f"| Linked source-claim receipts | {len(data.get('source_claim_receipt_counts', {}))} |",
        "",
        "## Gate statuses",
        "",
        "| Status | Count |",
        "| --- | ---: |",
    ]
    for status, count in data.get("gate_status_counts", {}).items():
        lines.append(f"| `{status}` | {count} |")
    lines.extend(["", "## Gap blockers", "", "| Gap | Gates |", "| --- | --- |"])
    for gap, gates in data.get("gap_gate_map", {}).items():
        lines.append(f"| `{gap}` | {', '.join(f'`{gid}`' for gid in gates)} |")
    lines.extend(["", "## Source-claim receipt dependencies", "", "| Receipt | Count |", "| --- | ---: |"])
    for rid, count in data.get("source_claim_receipt_counts", {}).items():
        lines.append(f"| `{rid}` | {count} |")
    lines.extend(["", "## Gates", ""])
    for gate in data.get("gates", []):
        lines.extend([
            f"### `{gate['gate_id']}` — {cell(gate.get('gate_label'))}",
            "",
            f"Outcome-tail plan: `{gate.get('outcome_tail_plan')}`  ",
            f"Status: `{gate.get('gate_status')}`",
            "",
            f"Target population: {gate.get('target_population', '')}",
            "",
            f"Sampling frame: {gate.get('sampling_frame', '')}",
            "",
            "| Cohort | Minimum observation goal | Denominator audit |",
            "| --- | --- | --- |",
        ])
        for cohort in gate.get("cohort_requirements", []):
            lines.append(
                f"| `{cohort.get('cohort_id')}` | {cell(cohort.get('minimum_observation_goal'))} | {cell(cohort.get('denominator_audit'))} |"
            )
        lines.extend([
            "",
            f"Nonresponse-bias plan: {gate.get('nonresponse_bias_plan', '')}",
            "",
            f"Closure blocker: {gate.get('closure_blocker', '')}",
            "",
            f"Next action: {gate.get('next_action', '')}",
            "",
        ])
    return "\n".join(lines)


def main() -> None:
    source = METADATA_DIR / "tail_sampling_gates.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    gates = []
    status_counts: Counter[str] = Counter()
    source_claim_counts: Counter[str] = Counter()
    gap_gate_map: dict[str, list[str]] = {}
    plan_gate_map: dict[str, list[str]] = {}
    cohort_gate_count = 0
    material_field_counts: Counter[str] = Counter()
    for gate_id, gate in sorted(payload.get("gates", {}).items()):
        status_counts.update([gate.get("gate_status", "unknown")])
        source_claim_counts.update(gate.get("linked_source_claim_receipts", []))
        material_field_counts.update(gate.get("material_fields", []))
        cohort_gate_count += len(gate.get("cohort_requirements", []))
        plan_gate_map.setdefault(gate.get("outcome_tail_plan", "unknown"), []).append(gate_id)
        for gap_id in gate.get("linked_gaps", []):
            gap_gate_map.setdefault(gap_id, []).append(gate_id)
        gates.append({"gate_id": gate_id, **gate})
    data = {
        "revision": current_revision(),
        "generated_at_utc": generated_at_utc(),
        "tail_sampling_gate_source": str(source.relative_to(ROOT)),
        "gate_role": payload.get("gate_role", ""),
        "privacy_posture": payload.get("privacy_posture", ""),
        "closure_policy": payload.get("closure_policy", ""),
        "gate_count": len(gates),
        "cohort_gate_count": cohort_gate_count,
        "gates": gates,
        "gate_status_counts": sorted_counts(status_counts),
        "source_claim_receipt_counts": sorted_counts(source_claim_counts),
        "material_field_counts": sorted_counts(material_field_counts),
        "gap_gate_map": {k: sorted(v) for k, v in sorted(gap_gate_map.items())},
        "plan_gate_map": {k: sorted(v) for k, v in sorted(plan_gate_map.items())},
    }
    write_json_and_markdown(GENERATED, "TAIL_SAMPLING_GATES", data, render_markdown(data))
    print("OK: wrote generated/TAIL_SAMPLING_GATES.json and generated/TAIL_SAMPLING_GATES.md")


if __name__ == "__main__":
    main()
