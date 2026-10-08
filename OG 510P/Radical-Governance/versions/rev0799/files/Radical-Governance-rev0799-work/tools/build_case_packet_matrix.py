#!/usr/bin/env python3
"""Build the applied case-packet matrix generated surface."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
METADATA_DIR = ROOT / "metadata"
GENERATED_DIR = ROOT / "generated"
DATA_PATH = METADATA_DIR / "case_packets.json"
GAP_LEDGER_PATH = METADATA_DIR / "gap_ledger.json"
OUT_JSON = GENERATED_DIR / "CASE_PACKET_MATRIX.json"
OUT_MD = GENERATED_DIR / "CASE_PACKET_MATRIX.md"


def load_cases() -> list[dict]:
    data = json.loads(DATA_PATH.read_text())
    raw_cases = data.get("cases", {})
    if isinstance(raw_cases, dict):
        cases = [{"case_id": int(case_id), **case} for case_id, case in raw_cases.items()]
    else:
        cases = [{"case_id": int(case.get("case_id", 0)), **case} for case in raw_cases]
    return sorted(cases, key=lambda item: int(item.get("case_id", 0)))


def load_open_gaps() -> list[str]:
    if not GAP_LEDGER_PATH.exists():
        return []
    ledger = json.loads(GAP_LEDGER_PATH.read_text())
    open_items: list[str] = []
    for gap_id, gap in sorted(ledger.get("gaps", {}).items()):
        status = str(gap.get("status", ""))
        if status.startswith("repaired"):
            continue
        missing = gap.get("missing_domain", "unspecified domain")
        next_artifact = gap.get("next_artifact", "name a concrete next artifact")
        open_items.append(f"{gap_id} ({status}): {missing}; next artifact: {next_artifact}")
    return open_items


def compact_family_summary(cases: list[dict], limit: int = 8) -> str:
    counter = Counter(str(case.get("form_family", "unclassified")) for case in cases)
    pieces = [f"{family} ({count})" for family, count in counter.most_common(limit)]
    remainder = len(counter) - len(pieces)
    if remainder > 0:
        pieces.append(f"{remainder} other families")
    return "; ".join(pieces)


def build_counts(cases: list[dict]) -> dict:
    live = Counter()
    reserved = Counter()
    source_keys = Counter()
    families = Counter()
    classes = Counter()
    for case in cases:
        live.update(int(n) for n in case.get("live_chain_notes", []))
        reserved.update(int(n) for n in case.get("reserved_notes", []))
        source_keys.update(str(k) for k in case.get("source_keys", []))
        families.update([str(case.get("form_family", "unclassified"))])
        classes.update([str(case.get("thickness", "unclassified"))])
    return {
        "live_chain_note_counts": {str(k): v for k, v in sorted(live.items())},
        "reserved_chain_note_counts": {str(k): v for k, v in sorted(reserved.items())},
        "source_key_counts": dict(sorted(source_keys.items())),
        "form_family_counts": dict(sorted(families.items())),
        "thickness_counts": dict(sorted(classes.items())),
    }


def build_merge_guidance(cases: list[dict]) -> dict:
    ids = [int(case["case_id"]) for case in cases]
    latest = cases[-1] if cases else {}
    open_gaps = load_open_gaps()
    if open_gaps:
        next_needed = open_gaps[:8]
    else:
        next_needed = [
            "Run a deletion/merge-retirement review only when two packets have the same lower-form result, affected-party tail, source posture, and anti-theater test; otherwise keep them distinct.",
            "Continue source-health triage for high-dependency current-note and case-packet sources before adding decorative registry surfaces.",
            "Shrink generated surfaces when they repeat metadata already available in compact source files.",
        ]
    latest_label = latest.get("case_label", "none")
    reason = (
        f"The matrix now covers {len(cases)} applied packets from note {min(ids) if ids else 'n/a'} "
        f"through note {max(ids) if ids else 'n/a'}; the latest packet is {latest.get('case_id', 'n/a')} "
        f"({latest_label}). The dominant form families are: {compact_family_summary(cases)}. "
        "The chain is manual-ready but not deletion-ready because apparent overlap often hides different affected-party tails, "
        "repair surfaces, source postures, or anti-theater tests. Keep the case packets until a merge review proves that no live dispatch, "
        "source-currentness, appeal, compensation, degraded-mode, or tail-risk function would be lost."
    )
    return {
        "current_holding": "manual-ready with annexes, but not deletion-ready",
        "reason": reason,
        "open_gap_count": len(open_gaps),
        "open_gap_summary": open_gaps,
        "next_needed_tests": next_needed,
    }


def render_markdown(data: dict) -> str:
    lines = [
        "# Applied case-packet matrix",
        "",
        f"Revision: `{data['revision']}`",
        "",
        f"Case count: **{data['case_count']}**",
        "",
        "## Merge guidance",
        "",
        f"- Current holding: {data['merge_guidance']['current_holding']}",
        f"- Reason: {data['merge_guidance']['reason']}",
        f"- Open gap count: {data['merge_guidance']['open_gap_count']}",
        "- Next needed tests:",
    ]
    for item in data["merge_guidance"].get("next_needed_tests", []):
        lines.append(f"  - {item}")
    if data["merge_guidance"].get("open_gap_summary"):
        lines.extend(["", "## Open / maintenance gap scan", ""])
        for item in data["merge_guidance"]["open_gap_summary"]:
            lines.append(f"- {item}")
    lines.extend(["", "## Chain-note recurrence", "", "| Note | Live | Reserved |", "| --- | ---: | ---: |"])
    all_notes = sorted(set(data.get("live_chain_note_counts", {})) | set(data.get("reserved_chain_note_counts", {})), key=lambda item: int(item))
    for note in all_notes:
        lines.append(f"| `{note}` | {data.get('live_chain_note_counts', {}).get(note, 0)} | {data.get('reserved_chain_note_counts', {}).get(note, 0)} |")
    lines.extend(["", "## Cases", ""])
    for case in data["cases"]:
        handback = case.get("downshift_or_handback_triggers", case.get("downshift_or_handback", []))
        lines.extend([
            f"### {case['case_id']} — {case['case_label']}",
            "",
            f"- File: `{case['file']}`",
            f"- Form family: {case.get('form_family', '')}",
            f"- Form verdict: {case.get('form_verdict', '')}",
            f"- Trigger type: {case.get('trigger_type', '')}",
            f"- Thickness: {case.get('thickness', '')}",
            f"- Lower-form result: {case.get('lower_form_result', '')}",
            f"- Live chain notes: {', '.join(str(n) for n in case.get('live_chain_notes', []))}",
            f"- Reserved notes: {', '.join(str(n) for n in case.get('reserved_notes', []))}",
            f"- Repair surfaces: {', '.join(case.get('repair_surfaces', []))}",
            f"- Upgrade triggers: {', '.join(case.get('upgrade_triggers', []))}",
            f"- Downshift / handback triggers: {', '.join(handback)}",
            f"- Anti-theater core: {', '.join(case.get('anti_theater_core', []))}",
            f"- Source keys: {', '.join(case.get('source_keys', []))}",
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    GENERATED_DIR.mkdir(exist_ok=True)
    cases = load_cases()
    raw = json.loads(DATA_PATH.read_text())
    counts = build_counts(cases)
    data = {
        "generated_from": "metadata/case_packets.json",
        "revision": raw.get("revision"),
        "case_count": len(cases),
        "merge_guidance": build_merge_guidance(cases),
        **counts,
        "cases": cases,
    }
    OUT_JSON.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    OUT_MD.write_text(render_markdown(data))


if __name__ == "__main__":
    main()
