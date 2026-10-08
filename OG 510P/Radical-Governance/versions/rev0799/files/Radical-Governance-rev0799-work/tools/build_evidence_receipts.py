#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter

from archive_meta import GENERATED, METADATA_DIR, ROOT, current_revision, generated_at_utc
from metadata_surface import sorted_counts, write_json_and_markdown


def render_markdown(data: dict) -> str:
    lines = [
        "# Evidence receipts pilot",
        "",
        f"Generated for `{data['revision']}` from `{data['evidence_receipt_source']}`.",
        "",
        "This surface records what a source can prove, what proof floor it reaches, and which live gaps it blocks. It deliberately does not store private records or claim field validation.",
        "",
        "## Closure policy",
        "",
        data.get("closure_policy", "No receipt below field-validated person outcome proof can close a live gap."),
        "",
        "## Proof-floor counts",
        "",
        "| Proof floor | Count |",
        "| --- | ---: |",
    ]
    for floor, count in data["proof_floor_counts"].items():
        lines.append(f"| `{floor}` | {count} |")
    lines.extend(["", "## Material-outcome dimension counts", "", "| Dimension | Count |", "| --- | ---: |"])
    for dimension, count in data.get("material_outcome_dimension_counts", {}).items():
        lines.append(f"| `{dimension}` | {count} |")
    lines.extend(["", "## Source-receipt levels", "", "| Level | Count |", "| --- | ---: |"])
    for level, count in data.get("source_receipt_level_counts", {}).items():
        lines.append(f"| `{level}` | {count} |")
    lines.extend(["", "## Closure blockers", "", "| Gap | Blocking receipts |", "| --- | --- |"] )
    for gap, receipts in data["closure_blocker_map"].items():
        receipt_list = ", ".join(f"`{rid}`" for rid in receipts)
        lines.append(f"| `{gap}` | {receipt_list} |")
    lines.extend([
        "",
        "## Receipts",
        "",
        "| Receipt | Case family | Proof floor | Can close gap? | Claim | Remaining affected-person gap |",
        "| --- | --- | --- | --- | --- | --- |",
    ])
    for receipt in data["receipts"]:
        lines.append(
            f"| `{receipt['receipt_id']}` | `{receipt['case_family']}` | `{receipt['proof_floor']}` | `{receipt['can_close_gap']}` | {receipt['claim']} | {receipt['affected_person_gap']} |"
        )
    lines.extend(["", "## Source-key recurrence", "", "| Source key | Count |", "| --- | ---: |"])
    for key, count in data["source_key_counts"].items():
        lines.append(f"| `{key}` | {count} |")
    lines.extend(["", "## Note recurrence", "", "| Note | Count |", "| --- | ---: |"] )
    for note, count in data["note_counts"].items():
        lines.append(f"| `{note}` | {count} |")
    lines.extend(["", "## Privacy posture", "", data.get("privacy_posture", ""), ""])
    return "\n".join(lines)


def main() -> None:
    GENERATED.mkdir(exist_ok=True)
    source = METADATA_DIR / "evidence_receipts.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    receipts = []
    source_counts: Counter[str] = Counter()
    note_counts: Counter[int] = Counter()
    proof_floor_counts: Counter[str] = Counter()
    material_outcome_dimension_counts: Counter[str] = Counter()
    source_receipt_level_counts: Counter[str] = Counter()
    closure_blocker_map: dict[str, list[str]] = {}
    for receipt_id, receipt in sorted(payload.get("receipts", {}).items()):
        source_counts.update(receipt.get("source_keys", []))
        note_counts.update(int(n) for n in receipt.get("archive_notes", []))
        proof_floor_counts.update([receipt.get("proof_floor", "unknown")])
        material_outcome_dimension_counts.update(receipt.get("material_outcome_dimensions", []))
        source_receipt_level_counts.update([receipt.get("source_receipt_level", "unknown")])
        for gap_id in receipt.get("closure_blocker_for", []):
            closure_blocker_map.setdefault(gap_id, []).append(receipt_id)
        receipts.append({"receipt_id": receipt_id, **receipt})
    data = {
        "revision": current_revision(),
        "generated_at_utc": generated_at_utc(),
        "evidence_receipt_source": str(source.relative_to(ROOT)),
        "receipt_count": len(receipts),
        "privacy_posture": payload.get("privacy_posture", ""),
        "closure_policy": payload.get("closure_policy", ""),
        "proof_floor_labels": payload.get("proof_floor_labels", {}),
        "receipts": receipts,
        "source_key_counts": sorted_counts(source_counts),
        "note_counts": {str(k): v for k, v in sorted(note_counts.items())},
        "proof_floor_counts": sorted_counts(proof_floor_counts),
        "material_outcome_dimension_counts": sorted_counts(material_outcome_dimension_counts),
        "source_receipt_level_counts": sorted_counts(source_receipt_level_counts),
        "closure_blocker_map": {k: v for k, v in sorted(closure_blocker_map.items())},
    }
    write_json_and_markdown(GENERATED, "EVIDENCE_RECEIPTS", data, render_markdown(data))
    print("OK: wrote generated/EVIDENCE_RECEIPTS.json and generated/EVIDENCE_RECEIPTS.md")


if __name__ == "__main__":
    main()
