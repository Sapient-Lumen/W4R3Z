#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter

from archive_meta import GENERATED, METADATA_DIR, ROOT, current_revision, generated_at_utc
from metadata_surface import cell, sorted_counts, write_json_and_markdown


def render_markdown(data: dict) -> str:
    lines = [
        "# Fieldwork authorization gates",
        "",
        f"Generated for `{data['revision']}` from `{data['fieldwork_authorization_gate_source']}`.",
        "",
        data.get("authorization_role", ""),
        "",
        "## Closure policy",
        "",
        data.get("closure_policy", ""),
        "",
        "## Summary counts",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Authorization gates | {data['gate_count']} |",
        f"| Gap blockers | {len(data.get('gap_gate_map', {}))} |",
        f"| Linked field-intake controls | {len(data.get('field_intake_gate_map', {}))} |",
        "",
        "## Authorization status counts",
        "",
        "| Status | Count |",
        "| --- | ---: |",
    ]
    for status, count in data.get("authorization_status_counts", {}).items():
        lines.append(f"| `{status}` | {count} |")
    lines.extend(["", "## Gap blockers", "", "| Gap | Authorization gates |", "| --- | --- |"])
    for gap, gates in data.get("gap_gate_map", {}).items():
        lines.append(f"| `{gap}` | {', '.join(f'`{gid}`' for gid in gates)} |")
    lines.extend(["", "## Gate details", ""])
    for gate in data.get("gates", []):
        lines.extend([
            f"### `{gate['gate_id']}` — {cell(gate.get('gate_label'))}",
            "",
            f"Status: `{gate.get('authorization_status')}`",
            "",
            f"Field-intake control: `{gate.get('linked_field_intake_control')}`  ",
            f"Sampling gate: `{gate.get('linked_sampling_gate')}`  ",
            f"Outcome-tail plan: `{gate.get('linked_outcome_tail_plan')}`",
            "",
            f"Handoff boundary: {gate.get('handoff_boundary', '')}",
            "",
            f"Closure blocker: {gate.get('closure_blocker', '')}",
            "",
            "| Authorization family | Items |",
            "| --- | --- |",
            f"| Required authorizers | {cell('; '.join(gate.get('required_authorizers', [])))} |",
            f"| Authorization artifacts | {cell('; '.join(gate.get('authorization_artifacts', [])))} |",
            f"| Custody handoff controls | {cell('; '.join(gate.get('custody_handoff_controls', [])))} |",
            f"| Minimum necessary fields | {cell('; '.join(gate.get('minimum_necessary_fields', [])))} |",
            f"| Prohibited cube artifacts | {cell('; '.join(gate.get('prohibited_cube_artifacts', [])))} |",
            f"| Stop conditions | {cell('; '.join(gate.get('stop_conditions', [])))} |",
            "",
            f"Next action: {gate.get('next_action', '')}",
            "",
        ])
    lines.extend(["", "## Privacy posture", "", data.get("privacy_posture", ""), ""])
    return "\n".join(lines)


def main() -> None:
    source = METADATA_DIR / "fieldwork_authorization_gates.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    gates = []
    status_counts: Counter[str] = Counter()
    source_claim_counts: Counter[str] = Counter()
    prohibited_counts: Counter[str] = Counter()
    gap_gate_map: dict[str, list[str]] = {}
    field_intake_gate_map: dict[str, list[str]] = {}
    sampling_gate_map: dict[str, list[str]] = {}
    outcome_plan_map: dict[str, list[str]] = {}
    authorizer_counts: Counter[str] = Counter()
    for gate_id, gate in sorted(payload.get("gates", {}).items()):
        status_counts.update([gate.get("authorization_status", "unknown")])
        source_claim_counts.update(gate.get("linked_source_claim_receipts", []))
        prohibited_counts.update(gate.get("prohibited_cube_artifacts", []))
        authorizer_counts.update(gate.get("required_authorizers", []))
        field_intake_gate_map.setdefault(gate.get("linked_field_intake_control", "unknown"), []).append(gate_id)
        sampling_gate_map.setdefault(gate.get("linked_sampling_gate", "unknown"), []).append(gate_id)
        outcome_plan_map.setdefault(gate.get("linked_outcome_tail_plan", "unknown"), []).append(gate_id)
        for gap_id in gate.get("linked_gaps", []):
            gap_gate_map.setdefault(gap_id, []).append(gate_id)
        gates.append({"gate_id": gate_id, **gate})
    data = {
        "revision": current_revision(),
        "generated_at_utc": generated_at_utc(),
        "fieldwork_authorization_gate_source": str(source.relative_to(ROOT)),
        "authorization_role": payload.get("authorization_role", ""),
        "privacy_posture": payload.get("privacy_posture", ""),
        "closure_policy": payload.get("closure_policy", ""),
        "gate_count": len(gates),
        "gates": gates,
        "authorization_status_counts": sorted_counts(status_counts),
        "source_claim_receipt_counts": sorted_counts(source_claim_counts),
        "prohibited_artifact_counts": sorted_counts(prohibited_counts),
        "required_authorizer_counts": sorted_counts(authorizer_counts),
        "gap_gate_map": {k: sorted(v) for k, v in sorted(gap_gate_map.items())},
        "field_intake_gate_map": {k: sorted(v) for k, v in sorted(field_intake_gate_map.items())},
        "sampling_gate_map": {k: sorted(v) for k, v in sorted(sampling_gate_map.items())},
        "outcome_plan_map": {k: sorted(v) for k, v in sorted(outcome_plan_map.items())},
    }
    write_json_and_markdown(GENERATED, "FIELDWORK_AUTHORIZATION_GATES", data, render_markdown(data))
    print("OK: wrote generated/FIELDWORK_AUTHORIZATION_GATES.json and generated/FIELDWORK_AUTHORIZATION_GATES.md")


if __name__ == "__main__":
    main()
