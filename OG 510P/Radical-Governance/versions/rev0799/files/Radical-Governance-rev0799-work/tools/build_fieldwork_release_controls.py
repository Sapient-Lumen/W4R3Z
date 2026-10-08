#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter

from archive_meta import GENERATED, METADATA_DIR, ROOT, current_revision, generated_at_utc
from metadata_surface import cell, sorted_counts, write_json_and_markdown


def render_markdown(data: dict) -> str:
    lines = [
        "# Fieldwork release controls",
        "",
        f"Generated for `{data['revision']}` from `{data['fieldwork_release_control_source']}`.",
        "",
        data.get("release_role", ""),
        "",
        "## Closure policy",
        "",
        data.get("closure_policy", ""),
        "",
        "## Summary counts",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Release controls | {data['control_count']} |",
        f"| Gap blockers | {len(data.get('gap_control_map', {}))} |",
        f"| Execution controls linked | {len(data.get('execution_control_map', {}))} |",
        "",
        "## Release status counts",
        "",
        "| Status | Count |",
        "| --- | ---: |",
    ]
    for status, count in data.get("release_status_counts", {}).items():
        lines.append(f"| `{status}` | {count} |")
    lines.extend(["", "## Gap blockers", "", "| Gap | Release controls |", "| --- | --- |"])
    for gap, controls in data.get("gap_control_map", {}).items():
        lines.append(f"| `{gap}` | {', '.join(f'`{cid}`' for cid in controls)} |")
    lines.extend(["", "## Control details", ""])
    for control in data.get("controls", []):
        lines.extend([
            f"### `{control['control_id']}` — {cell(control.get('control_label'))}",
            "",
            f"Status: `{control.get('release_status')}`",
            "",
            f"Execution control: `{control.get('linked_fieldwork_execution_control')}`  ",
            f"Authorization gate: `{control.get('linked_authorization_gate')}`  ",
            f"Field-intake control: `{control.get('linked_field_intake_control')}`  ",
            f"Sampling gate: `{control.get('linked_sampling_gate')}`  ",
            f"Outcome-tail plan: `{control.get('linked_outcome_tail_plan')}`",
            "",
            f"Closure blocker: {control.get('closure_blocker', '')}",
            "",
            "| Release family | Items |",
            "| --- | --- |",
            f"| Required release artifacts | {cell('; '.join(control.get('release_artifacts_required', [])))} |",
            f"| Disclosure limitation | {cell('; '.join(control.get('disclosure_limitation_controls', [])))} |",
            f"| De-identification | {cell('; '.join(control.get('deidentification_controls', [])))} |",
            f"| Public narrative | {cell('; '.join(control.get('public_narrative_controls', [])))} |",
            f"| Quality/integrity | {cell('; '.join(control.get('quality_integrity_controls', [])))} |",
            f"| Participant/community harm review | {cell('; '.join(control.get('participant_community_review_controls', [])))} |",
            f"| Errata/retraction | {cell('; '.join(control.get('errata_retraction_controls', [])))} |",
            f"| Allowed cube artifacts | {cell('; '.join(control.get('allowed_cube_artifacts', [])))} |",
            f"| Prohibited public outputs | {cell('; '.join(control.get('prohibited_public_outputs', [])))} |",
            f"| Pause/stop conditions | {cell('; '.join(control.get('pause_stop_conditions', [])))} |",
            "",
            f"Next action: {control.get('next_action', '')}",
            "",
        ])
    lines.extend(["", "## Privacy posture", "", data.get("privacy_posture", ""), ""])
    return "\n".join(lines)


def main() -> None:
    source = METADATA_DIR / "fieldwork_release_controls.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    controls = []
    status_counts: Counter[str] = Counter()
    source_claim_counts: Counter[str] = Counter()
    prohibited_counts: Counter[str] = Counter()
    pause_counts: Counter[str] = Counter()
    gap_control_map: dict[str, list[str]] = {}
    execution_control_map: dict[str, list[str]] = {}
    authorization_gate_control_map: dict[str, list[str]] = {}
    field_intake_control_map: dict[str, list[str]] = {}
    sampling_gate_control_map: dict[str, list[str]] = {}
    outcome_plan_control_map: dict[str, list[str]] = {}
    for control_id, control in sorted(payload.get("controls", {}).items()):
        status_counts.update([control.get("release_status", "unknown")])
        source_claim_counts.update(control.get("linked_source_claim_receipts", []))
        prohibited_counts.update(control.get("prohibited_public_outputs", []))
        pause_counts.update(control.get("pause_stop_conditions", []))
        execution_control_map.setdefault(control.get("linked_fieldwork_execution_control", "unknown"), []).append(control_id)
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
        "fieldwork_release_control_source": str(source.relative_to(ROOT)),
        "release_role": payload.get("release_role", ""),
        "privacy_posture": payload.get("privacy_posture", ""),
        "closure_policy": payload.get("closure_policy", ""),
        "control_count": len(controls),
        "controls": controls,
        "release_status_counts": sorted_counts(status_counts),
        "source_claim_receipt_counts": sorted_counts(source_claim_counts),
        "prohibited_public_output_counts": sorted_counts(prohibited_counts),
        "pause_condition_counts": sorted_counts(pause_counts),
        "gap_control_map": {k: sorted(v) for k, v in sorted(gap_control_map.items())},
        "execution_control_map": {k: sorted(v) for k, v in sorted(execution_control_map.items())},
        "authorization_gate_control_map": {k: sorted(v) for k, v in sorted(authorization_gate_control_map.items())},
        "field_intake_control_map": {k: sorted(v) for k, v in sorted(field_intake_control_map.items())},
        "sampling_gate_control_map": {k: sorted(v) for k, v in sorted(sampling_gate_control_map.items())},
        "outcome_plan_control_map": {k: sorted(v) for k, v in sorted(outcome_plan_control_map.items())},
    }
    write_json_and_markdown(GENERATED, "FIELDWORK_RELEASE_CONTROLS", data, render_markdown(data))
    print("OK: wrote generated/FIELDWORK_RELEASE_CONTROLS.json and generated/FIELDWORK_RELEASE_CONTROLS.md")


if __name__ == "__main__":
    main()
