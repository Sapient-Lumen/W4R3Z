#!/usr/bin/env python3
"""Guardrail for keeping breakglass adapter/runtime detail out of the baseline receipt."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []

    schema = load_json("spec/breakglass.receipt.schema.json")
    props = schema.get("properties") or {}
    session = props.get("session") or {}
    session_props = session.get("properties") or {}
    evidence = props.get("evidence") or {}
    evidence_props = evidence.get("properties") or {}

    expected_session_keys = {"host_id", "started_at", "expires_at", "ended_at", "method", "operator"}
    expected_evidence_keys = {
        "tty_recording_digests",
        "tty_recording_start_posture",
        "bootstrap_receipt_joins",
        "bootstrap_join_posture",
        "bootstrap_join_sequence_posture",
    }
    if set(session_props) != expected_session_keys:
        errors.append("spec/breakglass.receipt.schema.json session properties drifted; baseline breakglass session must stay adapter-thin and closed-world")
    if set(evidence_props) != expected_evidence_keys:
        errors.append("spec/breakglass.receipt.schema.json evidence properties drifted; baseline breakglass evidence must stay adapter-thin and closed-world")
    if session.get("additionalProperties") is not False:
        errors.append("spec/breakglass.receipt.schema.json session must keep additionalProperties=false")
    if evidence.get("additionalProperties") is not False:
        errors.append("spec/breakglass.receipt.schema.json evidence must keep additionalProperties=false")

    method_desc = ((session_props.get("method") or {}).get("description") or "")
    for needle in [
        "session ids/tokens",
        "plugin/runtime choices",
        "redacted side evidence outside the baseline breakglass receipt",
    ]:
        if needle not in method_desc:
            errors.append(f"spec/breakglass.receipt.schema.json session.method description missing required token: {needle}")

    evidence_desc = evidence.get("description") or ""
    for needle in [
        "Richer BMC / virtual-media / serial / console adapter metadata",
        "redacted side evidence outside the baseline breakglass receipt",
        "future dedicated artifact family/RFC",
    ]:
        if needle not in evidence_desc:
            errors.append(f"spec/breakglass.receipt.schema.json evidence description missing required token: {needle}")

    notes_desc = ((props.get("notes") or {}).get("description") or "")
    for needle in [
        "remote console URLs",
        "session ids/tokens",
        "ConsoleEntryCommand",
        "redacted side evidence outside the baseline breakglass receipt",
    ]:
        if needle not in notes_desc:
            errors.append(f"spec/breakglass.receipt.schema.json notes description missing required token: {needle}")

    doc_checks = {
        "adrs/ADR-0300-breakglass-adapter-details-stay-redacted-side-evidence-and-off-baseline-receipt.md": [
            "adapter-thin",
            "ConsoleEntryCommand",
            "redacted side evidence",
            "notes",
        ],
        "docs/710-breakglass-adapter-details-stay-redacted-side-evidence-and-off-baseline-receipt.md": [
            "adapter-thin",
            "OpenBMC",
            "ConsoleEntryCommand",
            "redacted side evidence",
            "tools/check_breakglass_adapter_detail_boundary.py",
        ],
        "docs/706-breakglass-session-methods-stay-concrete-and-oob-adapters-project-into-them.md": [
            "richer adapter/runtime detail still stays redacted side evidence",
            "docs/710-breakglass-adapter-details-stay-redacted-side-evidence-and-off-baseline-receipt.md",
        ],
        "docs/236-breakglass-and-recovery-mode.md": [
            "session ids/tokens",
            "docs/710-breakglass-adapter-details-stay-redacted-side-evidence-and-off-baseline-receipt.md",
        ],
        "docs/250-breakglass-and-recovery-workflows.md": [
            "adapter launch/runtime detail",
            "redacted side evidence",
            "docs/710-breakglass-adapter-details-stay-redacted-side-evidence-and-off-baseline-receipt.md",
        ],
        "docs/618-breakglass-recording-detail-and-export-posture-by-profile.md": [
            "adapter launch/runtime detail stays redacted side evidence",
            "notes is not a loophole",
        ],
        "docs/266-open-questions-and-risk-register.md": [
            "ADR-0300",
            "baseline breakglass receipt now stays adapter-thin",
        ],
        "docs/98-archive-hygiene.md": [
            "check_breakglass_adapter_detail_boundary.py",
            "adapter/runtime detail out of the baseline receipt",
        ],
        "docs/99-llm-runbook.md": [
            "docs/710-breakglass-adapter-details-stay-redacted-side-evidence-and-off-baseline-receipt.md",
            "tools/check_breakglass_adapter_detail_boundary.py",
        ],
        "docs/00-index.md": [
            "docs/710-breakglass-adapter-details-stay-redacted-side-evidence-and-off-baseline-receipt.md",
            "tools/check_breakglass_adapter_detail_boundary.py",
        ],
        "docs/110-juicy-os-lessons.md": [
            "adapter-thin",
            "docs/710-breakglass-adapter-details-stay-redacted-side-evidence-and-off-baseline-receipt.md",
        ],
        "docs/32-curated-references.md": [
            "DMTF Redfish Property Guide (`ConsoleEntryCommand`, `HotKeySequenceDisplay`, `VirtualMedia`, `VirtualMediaConfig`)",
            "OpenBMC virtual-media design",
        ],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")

    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        return 1
    print("Breakglass adapter detail boundary: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
