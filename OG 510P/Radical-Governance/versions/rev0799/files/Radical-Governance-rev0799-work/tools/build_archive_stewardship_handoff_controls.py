#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter

from archive_meta import GENERATED, METADATA_DIR, ROOT, current_revision, generated_at_utc
from metadata_surface import cell, sorted_counts, write_json_and_markdown


def render_markdown(data: dict) -> str:
    lines = [
        "# Archive stewardship handoff controls",
        "",
        f"Generated for `{data['revision']}` from `{data['archive_stewardship_handoff_source']}`.",
        "",
        data.get("handoff_role", ""),
        "",
        "## Handoff policy",
        "",
        data.get("handoff_policy", ""),
        "",
        "## Summary counts",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Stewardship handoff controls | {data['control_count']} |",
        f"| Gap blockers | {len(data.get('gap_control_map', {}))} |",
        f"| Required public documents | {len(data.get('public_document_counts', {}))} |",
        f"| Required role classes | {len(data.get('role_class_counts', {}))} |",
        "",
        "## Handoff status counts",
        "",
        "| Status | Count |",
        "| --- | ---: |",
    ]
    for status, count in data.get("handoff_status_counts", {}).items():
        lines.append(f"| `{status}` | {count} |")
    lines.extend(["", "## Gap blockers", "", "| Gap | Handoff controls |", "| --- | --- |"])
    for gap, controls in data.get("gap_control_map", {}).items():
        lines.append(f"| `{gap}` | {', '.join(f'`{cid}`' for cid in controls)} |")
    lines.extend(["", "## Control details", ""])
    for control in data.get("controls", []):
        lines.extend([
            f"### `{control['control_id']}` — {cell(control.get('control_label'))}",
            "",
            f"Status: `{control.get('handoff_status')}`",
            "",
            f"Handoff blocker: {control.get('handoff_blocker', '')}",
            "",
            "| Handoff family | Items |",
            "| --- | --- |",
            f"| Linked gaps | {cell('; '.join(control.get('linked_gaps', [])))} |",
            f"| Source-claim receipts | {cell('; '.join(control.get('linked_source_claim_receipts', [])))} |",
            f"| Required owner decisions | {cell('; '.join(control.get('required_owner_decisions', [])))} |",
            f"| Required public documents | {cell('; '.join(control.get('required_public_documents', [])))} |",
            f"| Role classes required | {cell('; '.join(control.get('role_classes_required', [])))} |",
            f"| Handoff clocks | {cell('; '.join(control.get('handoff_clocks', [])))} |",
            f"| Allowed cube artifacts | {cell('; '.join(control.get('allowed_cube_artifacts', [])))} |",
            f"| Prohibited cube artifacts | {cell('; '.join(control.get('prohibited_cube_artifacts', [])))} |",
            "",
            f"Next action: {control.get('next_action', '')}",
            "",
        ])
    lines.extend(["", "## Privacy posture", "", data.get("privacy_posture", ""), ""])
    return "\n".join(lines)


def main() -> None:
    source = METADATA_DIR / "archive_stewardship_handoff_controls.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    controls = []
    status_counts: Counter[str] = Counter()
    source_claim_counts: Counter[str] = Counter()
    gap_control_map: dict[str, list[str]] = {}
    public_document_counts: Counter[str] = Counter()
    role_class_counts: Counter[str] = Counter()
    owner_decision_counts: Counter[str] = Counter()
    clock_counts: Counter[str] = Counter()
    prohibited_counts: Counter[str] = Counter()
    for control_id, control in sorted(payload.get("controls", {}).items()):
        status_counts.update([control.get("handoff_status", "unknown")])
        source_claim_counts.update(control.get("linked_source_claim_receipts", []))
        public_document_counts.update(control.get("required_public_documents", []))
        role_class_counts.update(control.get("role_classes_required", []))
        owner_decision_counts.update(control.get("required_owner_decisions", []))
        clock_counts.update(control.get("handoff_clocks", []))
        prohibited_counts.update(control.get("prohibited_cube_artifacts", []))
        for gap_id in control.get("linked_gaps", []):
            gap_control_map.setdefault(gap_id, []).append(control_id)
        controls.append({"control_id": control_id, **control})
    data = {
        "revision": current_revision(),
        "generated_at_utc": generated_at_utc(),
        "archive_stewardship_handoff_source": str(source.relative_to(ROOT)),
        "handoff_role": payload.get("handoff_role", ""),
        "privacy_posture": payload.get("privacy_posture", ""),
        "handoff_policy": payload.get("handoff_policy", ""),
        "control_count": len(controls),
        "controls": controls,
        "handoff_status_counts": sorted_counts(status_counts),
        "source_claim_receipt_counts": sorted_counts(source_claim_counts),
        "public_document_counts": sorted_counts(public_document_counts),
        "role_class_counts": sorted_counts(role_class_counts),
        "owner_decision_counts": sorted_counts(owner_decision_counts),
        "handoff_clock_counts": sorted_counts(clock_counts),
        "prohibited_artifact_counts": sorted_counts(prohibited_counts),
        "gap_control_map": {k: sorted(v) for k, v in sorted(gap_control_map.items())},
    }
    write_json_and_markdown(GENERATED, "ARCHIVE_STEWARDSHIP_HANDOFF_CONTROLS", data, render_markdown(data))
    print("OK: wrote generated/ARCHIVE_STEWARDSHIP_HANDOFF_CONTROLS.json and generated/ARCHIVE_STEWARDSHIP_HANDOFF_CONTROLS.md")


if __name__ == "__main__":
    main()
