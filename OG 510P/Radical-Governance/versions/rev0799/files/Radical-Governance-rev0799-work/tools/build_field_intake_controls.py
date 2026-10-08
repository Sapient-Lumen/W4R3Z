#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter

from archive_meta import GENERATED, METADATA_DIR, ROOT, current_revision, generated_at_utc
from metadata_surface import cell, sorted_counts, write_json_and_markdown


def render_markdown(data: dict) -> str:
    lines = [
        "# Field-intake controls",
        "",
        f"Generated for `{data['revision']}` from `{data['field_intake_control_source']}`.",
        "",
        data.get("control_role", ""),
        "",
        "## Closure policy",
        "",
        data.get("closure_policy", ""),
        "",
        "## Summary counts",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Controls | {data['control_count']} |",
        f"| Gap blockers | {len(data.get('gap_control_map', {}))} |",
        f"| Linked sampling gates | {len(data.get('sampling_gate_control_map', {}))} |",
        "",
        "## Status counts",
        "",
        "| Status | Count |",
        "| --- | ---: |",
    ]
    for status, count in data.get("control_status_counts", {}).items():
        lines.append(f"| `{status}` | {count} |")
    lines.extend(["", "## Gap blockers", "", "| Gap | Field-intake controls |", "| --- | --- |"])
    for gap, controls in data.get("gap_control_map", {}).items():
        lines.append(f"| `{gap}` | {', '.join(f'`{cid}`' for cid in controls)} |")
    lines.extend(["", "## Controls", ""])
    for control in data.get("controls", []):
        lines.extend([
            f"### `{control['control_id']}` — {cell(control.get('control_label'))}",
            "",
            f"Status: `{control.get('control_status')}`",
            "",
            f"Linked sampling gate: `{control.get('linked_sampling_gate')}`",
            "",
            f"Human-subjects boundary: {control.get('human_subjects_boundary', '')}",
            "",
            f"Closure blocker: {control.get('closure_blocker', '')}",
            "",
            "| Control family | Items |",
            "| --- | --- |",
            f"| Lawful basis floor | {cell('; '.join(control.get('lawful_basis_floor', [])))} |",
            f"| Consent/notice floor | {cell('; '.join(control.get('consent_notice_floor', [])))} |",
            f"| Data-linkage controls | {cell('; '.join(control.get('data_linkage_controls', [])))} |",
            f"| Adverse-action firewall | {cell('; '.join(control.get('adverse_action_firewall', [])))} |",
            f"| Prohibited cube artifacts | {cell('; '.join(control.get('prohibited_cube_artifacts', [])))} |",
            "",
            f"Next action: {control.get('next_action', '')}",
            "",
        ])
    lines.extend(["", "## Privacy posture", "", data.get("privacy_posture", ""), ""])
    return "\n".join(lines)


def main() -> None:
    source = METADATA_DIR / "field_intake_controls.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    controls = []
    status_counts: Counter[str] = Counter()
    source_claim_counts: Counter[str] = Counter()
    prohibited_counts: Counter[str] = Counter()
    gap_control_map: dict[str, list[str]] = {}
    sampling_gate_control_map: dict[str, list[str]] = {}
    outcome_plan_control_map: dict[str, list[str]] = {}
    for control_id, control in sorted(payload.get("controls", {}).items()):
        status_counts.update([control.get("control_status", "unknown")])
        sampling_gate_control_map.setdefault(control.get("linked_sampling_gate", "unknown"), []).append(control_id)
        outcome_plan_control_map.setdefault(control.get("linked_outcome_tail_plan", "unknown"), []).append(control_id)
        source_claim_counts.update(control.get("linked_source_claim_receipts", []))
        prohibited_counts.update(control.get("prohibited_cube_artifacts", []))
        for gap_id in control.get("linked_gaps", []):
            gap_control_map.setdefault(gap_id, []).append(control_id)
        controls.append({"control_id": control_id, **control})
    data = {
        "revision": current_revision(),
        "generated_at_utc": generated_at_utc(),
        "field_intake_control_source": str(source.relative_to(ROOT)),
        "control_role": payload.get("control_role", ""),
        "privacy_posture": payload.get("privacy_posture", ""),
        "closure_policy": payload.get("closure_policy", ""),
        "control_count": len(controls),
        "controls": controls,
        "control_status_counts": sorted_counts(status_counts),
        "source_claim_receipt_counts": sorted_counts(source_claim_counts),
        "prohibited_artifact_counts": sorted_counts(prohibited_counts),
        "gap_control_map": {k: sorted(v) for k, v in sorted(gap_control_map.items())},
        "sampling_gate_control_map": {k: sorted(v) for k, v in sorted(sampling_gate_control_map.items())},
        "outcome_plan_control_map": {k: sorted(v) for k, v in sorted(outcome_plan_control_map.items())},
    }
    write_json_and_markdown(GENERATED, "FIELD_INTAKE_CONTROLS", data, render_markdown(data))
    print("OK: wrote generated/FIELD_INTAKE_CONTROLS.json and generated/FIELD_INTAKE_CONTROLS.md")


if __name__ == "__main__":
    main()
