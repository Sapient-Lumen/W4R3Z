#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter

from archive_meta import GENERATED, METADATA_DIR, ROOT, current_revision, generated_at_utc
from metadata_surface import cell, sorted_counts, write_json_and_markdown


def render_markdown(data: dict) -> str:
    lines = [
        "# Fieldwork post-closure monitoring controls",
        "",
        f"Generated for `{data['revision']}` from `{data['fieldwork_postclosure_monitoring_source']}`.",
        "",
        data.get("monitoring_role", ""),
        "",
        "## Monitoring policy",
        "",
        data.get("monitoring_policy", ""),
        "",
        "## Summary counts",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Post-closure monitoring controls | {data['control_count']} |",
        f"| Gap blockers | {len(data.get('gap_control_map', {}))} |",
        f"| Closure dossiers linked | {len(data.get('closure_dossier_map', {}))} |",
        "",
        "## Monitoring status counts",
        "",
        "| Status | Count |",
        "| --- | ---: |",
    ]
    for status, count in data.get("monitoring_status_counts", {}).items():
        lines.append(f"| `{status}` | {count} |")
    lines.extend(["", "## Gap blockers", "", "| Gap | Monitoring controls |", "| --- | --- |"])
    for gap, controls in data.get("gap_control_map", {}).items():
        lines.append(f"| `{gap}` | {', '.join(f'`{cid}`' for cid in controls)} |")
    lines.extend(["", "## Control details", ""])
    for control in data.get("controls", []):
        lines.extend([
            f"### `{control['control_id']}` — {cell(control.get('control_label'))}",
            "",
            f"Status: `{control.get('monitoring_status')}`",
            "",
            f"Closure dossier: `{control.get('linked_fieldwork_closure_dossier')}`  ",
            f"Redress verification control: `{control.get('linked_fieldwork_redress_verification_control')}`  ",
            f"Correction control: `{control.get('linked_fieldwork_correction_control')}`  ",
            f"Release control: `{control.get('linked_fieldwork_release_control')}`  ",
            f"Execution control: `{control.get('linked_fieldwork_execution_control')}`  ",
            f"Authorization gate: `{control.get('linked_authorization_gate')}`  ",
            f"Field-intake control: `{control.get('linked_field_intake_control')}`  ",
            f"Sampling gate: `{control.get('linked_sampling_gate')}`  ",
            f"Outcome-tail plan: `{control.get('linked_outcome_tail_plan')}`",
            "",
            f"Monitoring blocker: {control.get('monitoring_blocker', '')}",
            "",
            "| Monitoring family | Items |",
            "| --- | --- |",
            f"| Cadence classes | {cell('; '.join(control.get('monitoring_cadence_classes', [])))} |",
            f"| Drift triggers | {cell('; '.join(control.get('drift_triggers', [])))} |",
            f"| Recheck evidence required | {cell('; '.join(control.get('recheck_evidence_required', [])))} |",
            f"| Gap reopen rules | {cell('; '.join(control.get('gap_reopen_rules', [])))} |",
            f"| Allowed cube artifacts | {cell('; '.join(control.get('allowed_cube_artifacts', [])))} |",
            f"| Prohibited cube artifacts | {cell('; '.join(control.get('prohibited_cube_artifacts', [])))} |",
            "",
            f"Next action: {control.get('next_action', '')}",
            "",
        ])
    lines.extend(["", "## Privacy posture", "", data.get("privacy_posture", ""), ""])
    return "\n".join(lines)


def main() -> None:
    source = METADATA_DIR / "fieldwork_postclosure_monitoring_controls.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    controls = []
    status_counts: Counter[str] = Counter()
    source_claim_counts: Counter[str] = Counter()
    prohibited_counts: Counter[str] = Counter()
    drift_counts: Counter[str] = Counter()
    cadence_counts: Counter[str] = Counter()
    reopen_rule_counts: Counter[str] = Counter()
    gap_control_map: dict[str, list[str]] = {}
    closure_dossier_map: dict[str, list[str]] = {}
    redress_control_map: dict[str, list[str]] = {}
    correction_control_map: dict[str, list[str]] = {}
    release_control_map: dict[str, list[str]] = {}
    execution_control_map: dict[str, list[str]] = {}
    authorization_gate_control_map: dict[str, list[str]] = {}
    field_intake_control_map: dict[str, list[str]] = {}
    sampling_gate_control_map: dict[str, list[str]] = {}
    outcome_plan_control_map: dict[str, list[str]] = {}
    for control_id, control in sorted(payload.get("controls", {}).items()):
        status_counts.update([control.get("monitoring_status", "unknown")])
        source_claim_counts.update(control.get("linked_source_claim_receipts", []))
        prohibited_counts.update(control.get("prohibited_cube_artifacts", []))
        drift_counts.update(control.get("drift_triggers", []))
        cadence_counts.update(control.get("monitoring_cadence_classes", []))
        reopen_rule_counts.update(control.get("gap_reopen_rules", []))
        closure_dossier_map.setdefault(control.get("linked_fieldwork_closure_dossier", "unknown"), []).append(control_id)
        redress_control_map.setdefault(control.get("linked_fieldwork_redress_verification_control", "unknown"), []).append(control_id)
        correction_control_map.setdefault(control.get("linked_fieldwork_correction_control", "unknown"), []).append(control_id)
        release_control_map.setdefault(control.get("linked_fieldwork_release_control", "unknown"), []).append(control_id)
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
        "fieldwork_postclosure_monitoring_source": str(source.relative_to(ROOT)),
        "monitoring_role": payload.get("monitoring_role", ""),
        "privacy_posture": payload.get("privacy_posture", ""),
        "monitoring_policy": payload.get("monitoring_policy", ""),
        "control_count": len(controls),
        "controls": controls,
        "monitoring_status_counts": sorted_counts(status_counts),
        "source_claim_receipt_counts": sorted_counts(source_claim_counts),
        "prohibited_artifact_counts": sorted_counts(prohibited_counts),
        "drift_trigger_counts": sorted_counts(drift_counts),
        "cadence_class_counts": sorted_counts(cadence_counts),
        "gap_reopen_rule_counts": sorted_counts(reopen_rule_counts),
        "gap_control_map": {k: sorted(v) for k, v in sorted(gap_control_map.items())},
        "closure_dossier_map": {k: sorted(v) for k, v in sorted(closure_dossier_map.items())},
        "redress_control_map": {k: sorted(v) for k, v in sorted(redress_control_map.items())},
        "correction_control_map": {k: sorted(v) for k, v in sorted(correction_control_map.items())},
        "release_control_map": {k: sorted(v) for k, v in sorted(release_control_map.items())},
        "execution_control_map": {k: sorted(v) for k, v in sorted(execution_control_map.items())},
        "authorization_gate_control_map": {k: sorted(v) for k, v in sorted(authorization_gate_control_map.items())},
        "field_intake_control_map": {k: sorted(v) for k, v in sorted(field_intake_control_map.items())},
        "sampling_gate_control_map": {k: sorted(v) for k, v in sorted(sampling_gate_control_map.items())},
        "outcome_plan_control_map": {k: sorted(v) for k, v in sorted(outcome_plan_control_map.items())},
    }
    write_json_and_markdown(GENERATED, "FIELDWORK_POSTCLOSURE_MONITORING_CONTROLS", data, render_markdown(data))
    print("OK: wrote generated/FIELDWORK_POSTCLOSURE_MONITORING_CONTROLS.json and generated/FIELDWORK_POSTCLOSURE_MONITORING_CONTROLS.md")


if __name__ == "__main__":
    main()
