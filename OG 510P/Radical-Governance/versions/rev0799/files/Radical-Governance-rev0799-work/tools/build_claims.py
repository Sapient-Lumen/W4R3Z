#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from archive_meta import GENERATED, METADATA_DIR, ROOT, current_revision, generated_at_utc

CURRENT_REV = current_revision()
CLAIMS_INPUT = METADATA_DIR / "claims.json"

STATUS_ORDER = ["settled_holding", "strong_default", "threshold_frontier", "case_diagnosis", "hypothesis", "source_repair"]


def note_title(note_file: str) -> str:
    path = ROOT / note_file
    if not path.exists():
        return Path(note_file).name
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return Path(note_file).name


def render_markdown(data: dict) -> str:
    lines: list[str] = [
        "# Claims ledger",
        "",
        f"Generated for `{data.get('revision')}` from `metadata/claims.json`.",
        "",
        "## Claim status counts",
        "",
        "| Status | Count |",
        "| --- | ---: |",
    ]
    for status in STATUS_ORDER:
        if status in data.get("status_counts", {}):
            lines.append(f"| `{status}` | {data['status_counts'][status]} |")
    for status, count in data.get("status_counts", {}).items():
        if status not in STATUS_ORDER:
            lines.append(f"| `{status}` | {count} |")

    lines.extend(["", "## Current revision claims", ""])
    current_note_files = set(data.get("current_note_files", []))
    for claim in data.get("claims", []):
        if claim.get("note_file") not in current_note_files:
            continue
        keys = ", ".join(f"`{k}`" for k in claim.get("source_keys", [])) or "—"
        channels = ", ".join(claim.get("capture_channels", [])) or "—"
        lines.extend([
            f"### `{claim.get('claim_id')}` — {claim.get('claim_status')}",
            "",
            f"Note: `{Path(claim.get('note_file', '')).name}` — {claim.get('note_title', '')}",
            "",
            claim.get("claim_text", ""),
            "",
            f"Evidence lane: `{claim.get('evidence_type')}`. Currentness: `{claim.get('currentness')}`. Review clock: `{claim.get('review_clock')}`.",
            "",
            f"Source keys: {keys}",
            "",
            f"Opposition: {claim.get('opposition_brief', '')}",
            "",
            f"Falsifier: {claim.get('falsifier', '')}",
            "",
            f"Capture channels: {channels}",
            "",
        ])

    lines.extend(["---", "", "## Complete claim table", "", "| Claim | Status | Note | Evidence | Currentness | Sources |", "| --- | --- | --- | --- | --- | --- |"])
    for claim in data.get("claims", []):
        keys = ", ".join(f"`{k}`" for k in claim.get("source_keys", [])) or "—"
        lines.append(f"| `{claim.get('claim_id')}` | `{claim.get('claim_status')}` | `{Path(claim.get('note_file', '')).name}` | `{claim.get('evidence_type')}` | `{claim.get('currentness')}` | {keys} |")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    GENERATED.mkdir(exist_ok=True)
    raw = json.loads(CLAIMS_INPUT.read_text(encoding="utf-8"))
    claims = []
    status_counts: Counter[str] = Counter()
    evidence_counts: Counter[str] = Counter()
    currentness_counts: Counter[str] = Counter()
    for claim_id, claim in sorted(raw.get("claims", {}).items()):
        item = dict(claim)
        item["claim_id"] = claim_id
        item["note_title"] = note_title(item.get("note_file", ""))
        status_counts[item.get("claim_status", "unknown")] += 1
        evidence_counts[item.get("evidence_type", "unknown")] += 1
        currentness_counts[item.get("currentness", "unknown")] += 1
        claims.append(item)
    data = {
        "revision": CURRENT_REV,
        "generated_at_utc": generated_at_utc(),
        "claims_source": str(CLAIMS_INPUT.relative_to(ROOT)),
        "ledger_role": raw.get("ledger_role", ""),
        "status_labels": raw.get("status_labels", {}),
        "currentness_labels": raw.get("currentness_labels", {}),
        "current_note_files": raw.get("current_note_files", []),
        "claim_count": len(claims),
        "status_counts": dict(sorted(status_counts.items())),
        "evidence_counts": dict(sorted(evidence_counts.items())),
        "currentness_counts": dict(sorted(currentness_counts.items())),
        "claims": claims,
    }
    (GENERATED / "CLAIMS.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (GENERATED / "CLAIMS.md").write_text(render_markdown(data), encoding="utf-8")
    print("OK: wrote generated/CLAIMS.json and generated/CLAIMS.md")


if __name__ == "__main__":
    main()
