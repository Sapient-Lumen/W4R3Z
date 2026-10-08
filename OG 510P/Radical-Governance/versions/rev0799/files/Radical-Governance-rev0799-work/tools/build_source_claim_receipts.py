#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter

from archive_meta import GENERATED, METADATA_DIR, ROOT, current_revision, generated_at_utc
from metadata_surface import cell, sorted_counts, write_json_and_markdown


def render_markdown(data: dict) -> str:
    lines = [
        "# Source-claim receipts",
        "",
        f"Generated for `{data['revision']}` from `{data['source_claim_receipt_source']}`.",
        "",
        data.get("receipt_role", ""),
        "",
        "## Closure policy",
        "",
        data.get("closure_policy", "A source-claim receipt is not a field outcome or preservation-complete receipt."),
        "",
        "## Summary counts",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Receipts | {data['receipt_count']} |",
        f"| Source keys | {len(data.get('source_key_counts', {}))} |",
        f"| Closure-blocked gaps | {len(data.get('closure_blocker_map', {}))} |",
        "",
        "## Source receipt levels",
        "",
        "| Level | Count |",
        "| --- | ---: |",
    ]
    for level, count in data.get("source_receipt_level_counts", {}).items():
        lines.append(f"| `{level}` | {count} |")
    lines.extend(["", "## Preservation statuses", "", "| Status | Count |", "| --- | ---: |"])
    for status, count in data.get("preservation_status_counts", {}).items():
        lines.append(f"| `{status}` | {count} |")
    lines.extend(["", "## Closure blockers", "", "| Gap | Blocking source-claim receipts |", "| --- | --- |"])
    for gap, receipts in data.get("closure_blocker_map", {}).items():
        lines.append(f"| `{gap}` | {', '.join(f'`{rid}`' for rid in receipts)} |")
    lines.extend([
        "",
        "## Receipts",
        "",
        "| Receipt | Source key | Claim family | Locator type | Anchor | Evidence limit |",
        "| --- | --- | --- | --- | --- | --- |",
    ])
    for row in data.get("receipts", []):
        lines.append(
            f"| `{row['receipt_id']}` | `{row['source_key']}` | `{row['claim_family']}` | `{row['locator_type']}` | {cell(row['anchor_quote'])} | {cell(row['evidence_limit'])} |"
        )
    lines.extend(["", "## Copyright and privacy posture", "", data.get("copyright_and_privacy_posture", ""), ""])
    return "\n".join(lines)


def main() -> None:
    GENERATED.mkdir(exist_ok=True)
    source = METADATA_DIR / "source_claim_receipts.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    receipts = []
    source_key_counts: Counter[str] = Counter()
    note_counts: Counter[int] = Counter()
    level_counts: Counter[str] = Counter()
    preservation_counts: Counter[str] = Counter()
    blocker_map: dict[str, list[str]] = {}
    for receipt_id, receipt in sorted(payload.get("receipts", {}).items()):
        source_key_counts.update([receipt.get("source_key", "")])
        note_counts.update(int(n) for n in receipt.get("archive_notes", []))
        level_counts.update([receipt.get("source_receipt_level", "unknown")])
        preservation_counts.update([receipt.get("preservation_status", "unknown")])
        for gap_id in receipt.get("closure_blocker_for", []):
            blocker_map.setdefault(gap_id, []).append(receipt_id)
        receipts.append({"receipt_id": receipt_id, **receipt})
    data = {
        "revision": current_revision(),
        "generated_at_utc": generated_at_utc(),
        "source_claim_receipt_source": str(source.relative_to(ROOT)),
        "receipt_role": payload.get("receipt_role", ""),
        "copyright_and_privacy_posture": payload.get("copyright_and_privacy_posture", ""),
        "closure_policy": payload.get("closure_policy", ""),
        "receipt_count": len(receipts),
        "receipts": receipts,
        "source_key_counts": {k: v for k, v in sorted_counts(source_key_counts).items() if k},
        "note_counts": {str(k): v for k, v in sorted(note_counts.items())},
        "source_receipt_level_counts": sorted_counts(level_counts),
        "preservation_status_counts": sorted_counts(preservation_counts),
        "closure_blocker_map": {k: sorted(v) for k, v in sorted(blocker_map.items())},
    }
    write_json_and_markdown(GENERATED, "SOURCE_CLAIM_RECEIPTS", data, render_markdown(data))
    print("OK: wrote generated/SOURCE_CLAIM_RECEIPTS.json and generated/SOURCE_CLAIM_RECEIPTS.md")


if __name__ == "__main__":
    main()
