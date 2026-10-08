#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter

from archive_meta import GENERATED, METADATA_DIR, ROOT, current_revision, generated_at_utc
from metadata_surface import cell, sorted_counts, write_json_and_markdown


def render_markdown(data: dict) -> str:
    lines = [
        "# Fieldwork execution controls",
        "",
        f"Generated for `{data['revision']}` from `{data['fieldwork_execution_control_source']}`.",
        "",
        data.get("execution_role", ""),
        "",
        "## Closure policy",
        "",
        data.get("closure_policy", ""),
        "",
        "## Summary counts",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Execution controls | {data['control_count']} |",
        f"| Gap blockers | {len(data.get('gap_control_map', {}))} |",
        f"| Authorization gates linked | {len(data.get('authorization_gate_control_map', {}))} |",
        "",
        "## Execution status counts",
        "",
        "| Status | Count |",
        "| --- | ---: |",
    ]
    for status, count in data.get("execution_status_counts", {}).items():
        lines.append(f"| `{status}` | {count} |")
    lines.extend(["", "## Gap blockers", "", "| Gap | Execution controls |", "| --- | --- |"])
    for gap, controls in data.get("gap_control_map", {}).items():
        lines.append(f"| `{gap}` | {', '.join(f'`{cid}`' for cid in controls)} |")
    lines.extend(["", "## Control details", ""])
    for control in data.get("controls", []):
        lines.extend([
            f"### `{control['control_id']}` — {cell(control.get('control_label'))}",
            "",
            f"Status: `{control.get('execution_status')}`",
            "",
            f"Authorization gate: `{control.get('linked_authorization_gate')}`  ",
            f"Field-intake control: `{control.get('linked_field_intake_control')}`  ",
            f"Sampling gate: `{control.get('linked_sampling_gate')}`  ",
            f"Outcome-tail plan: `{control.get('linked_outcome_tail_plan')}`",
            "",
            f"Closure blocker: {control.get('closure_blocker', '')}",
            "",
            "| Execution family | Items |",
            "| --- | --- |",
            f"| Required artifacts | {cell('; '.join(control.get('execution_artifacts_required', [])))} |",
            f"| Operating log floor | {cell('; '.join(control.get('operating_log_floor', [])))} |",
            f"| Participant safety | {cell('; '.join(control.get('participant_safety_controls', [])))} |",
            f"| Incident response | {cell('; '.join(control.get('incident_response_controls', [])))} |",
            f"| Breach response | {cell('; '.join(control.get('breach_response_controls', [])))} |",
            f"| Audit controls | {cell('; '.join(control.get('audit_controls', [])))} |",
            f"| Retention/destruction | {cell('; '.join(control.get('retention_destruction_controls', [])))} |",
            f"| Publication release | {cell('; '.join(control.get('publication_release_controls', [])))} |",
            f"| Prohibited cube artifacts | {cell('; '.join(control.get('prohibited_cube_artifacts', [])))} |",
            f"| Pause/stop conditions | {cell('; '.join(control.get('pause_stop_conditions', [])))} |",
            "",
            f"Next action: {control.get('next_action', '')}",
            "",
        ])
    lines.extend(["", "## Privacy posture", "", data.get("privacy_posture", ""), ""])
    return "\n".join(lines)


def main() -> None:
    source = METADATA_DIR / "fieldwork_execution_controls.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    controls = []
    status_counts: Counter[str] = Counter()
    source_claim_counts: Counter[str] = Counter()
    prohibited_counts: Counter[str] = Counter()
    gap_control_map: dict[str, list[str]] = {}
    authorization_gate_control_map: dict[str, list[str]] = {}
    field_intake_control_map: dict[str, list[str]] = {}
    sampling_gate_control_map: dict[str, list[str]] = {}
    outcome_plan_control_map: dict[str, list[str]] = {}
    pause_condition_counts: Counter[str] = Counter()
    for control_id, control in sorted(payload.get("controls", {}).items()):
        status_counts.update([control.get("execution_status", "unknown")])
        source_claim_counts.update(control.get("linked_source_claim_receipts", []))
        prohibited_counts.update(control.get("prohibited_cube_artifacts", []))
        pause_condition_counts.update(control.get("pause_stop_conditions", []))
        authorization_gate_control_map.setdefault(control.get("linked_authorization_gate", "unknown"), []).append(control_id)
        field_intake_control_map.setdefault(control.get("linked_field_intake_control", "unknown"), []).append(control_id)
        sampling_gate_control_map.setdefault(control.get("linked_sampling_gate", "unknown"), []).append(control_id)
        outcome_plan_control_map.setdefault(control.get("linked_outcome_tail_plan", "unknown"), []).append(control_id)
        for gap_id in control.get("linked_gaps", []):
            gap_control_map.setdefault(gap_id, []).append(control_id)
        controls.append({"control_id": control_id, **control})
    data = {
        "revision": current_revision(),
        "generated_at_utc": generated_at_utc(),
        "fieldwork_execution_control_source": str(source.relative_to(ROOT)),
        "execution_role": payload.get("execution_role", ""),
        "privacy_posture": payload.get("privacy_posture", ""),
        "closure_policy": payload.get("closure_policy", ""),
        "control_count": len(controls),
        "controls": controls,
        "execution_status_counts": sorted_counts(status_counts),
        "source_claim_receipt_counts": sorted_counts(source_claim_counts),
        "prohibited_artifact_counts": sorted_counts(prohibited_counts),
        "pause_condition_counts": sorted_counts(pause_condition_counts),
        "gap_control_map": {k: sorted(v) for k, v in sorted(gap_control_map.items())},
        "authorization_gate_control_map": {k: sorted(v) for k, v in sorted(authorization_gate_control_map.items())},
        "field_intake_control_map": {k: sorted(v) for k, v in sorted(field_intake_control_map.items())},
        "sampling_gate_control_map": {k: sorted(v) for k, v in sorted(sampling_gate_control_map.items())},
        "outcome_plan_control_map": {k: sorted(v) for k, v in sorted(outcome_plan_control_map.items())},
    }
    write_json_and_markdown(GENERATED, "FIELDWORK_EXECUTION_CONTROLS", data, render_markdown(data))
    print("OK: wrote generated/FIELDWORK_EXECUTION_CONTROLS.json and generated/FIELDWORK_EXECUTION_CONTROLS.md")


if __name__ == "__main__":
    main()
