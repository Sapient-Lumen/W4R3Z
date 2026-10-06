#!/usr/bin/env python3
"""Guardrail for interactive breakglass tty-recording joins and start posture."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

def jcs_bytes(obj: dict) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def digest(rel: str) -> str:
    return "sha256:" + hashlib.sha256(jcs_bytes(load_json(rel))).hexdigest()

def main() -> int:
    errors = []
    schema = load_json("spec/breakglass.receipt.schema.json")
    evidence = (schema.get("properties") or {}).get("evidence") or {}
    eprops = evidence.get("properties") or {}
    if "tty_recording_digests" not in eprops:
        errors.append("spec/breakglass.receipt.schema.json missing evidence.tty_recording_digests")
    if "session-open-before-first-prompt" not in ((eprops.get("tty_recording_start_posture") or {}).get("enum") or []):
        errors.append("spec/breakglass.receipt.schema.json must keep tty_recording_start_posture = session-open-before-first-prompt")
    allof_txt = json.dumps(schema.get("allOf", []), sort_keys=True)
    if "tty_recording_digests" not in allof_txt or "tty_recording_start_posture" not in allof_txt:
        errors.append("spec/breakglass.receipt.schema.json must require tty_recording_start_posture whenever tty_recording_digests are present")
    example = load_json("spec/examples/breakglass.receipt.json")
    evidence_ex = example.get("evidence") or {}
    digests = evidence_ex.get("tty_recording_digests") or []
    expected = digest("spec/examples/tty.session.recording.json")
    if not digests:
        errors.append("spec/examples/breakglass.receipt.json missing evidence.tty_recording_digests")
    elif digests[0] != expected:
        errors.append("spec/examples/breakglass.receipt.json evidence.tty_recording_digests[0] must match computed digest of spec/examples/tty.session.recording.json")
    if evidence_ex.get("tty_recording_start_posture") != "session-open-before-first-prompt":
        errors.append("spec/examples/breakglass.receipt.json evidence.tty_recording_start_posture must be session-open-before-first-prompt")
    doc_checks = {
        "docs/236-breakglass-and-recovery-mode.md": ["tty_recording_digests", "session-open-before-first-prompt"],
        "docs/250-breakglass-and-recovery-workflows.md": ["tty_recording_digests", "session-open-before-first-prompt"],
        "docs/292-terminal-session-recording-as-evidence.md": ["tty_recording_start_posture = session-open-before-first-prompt", "breakglass.receipt.evidence.tty_recording_digests"],
        "docs/618-breakglass-recording-detail-and-export-posture-by-profile.md": ["starts at session open before the first prompt", "breakglass.receipt.evidence.tty_recording_digests"],
        "docs/704-breakglass-interactive-sessions-carry-tty-recording-proof-and-start-at-session-open.md": ["tty_recording_start_posture", "session-open-before-first-prompt", "tty.session.recording"],
        "docs/98-archive-hygiene.md": ["check_breakglass_recording_activation_boundary.py", "first prompt"],
        "docs/99-llm-runbook.md": ["check_breakglass_recording_activation_boundary.py", "docs/704-breakglass-interactive-sessions-carry-tty-recording-proof-and-start-at-session-open.md"],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")
    if errors:
        for err in errors: print(f"ERROR: {err}")
        return 1
    print("Breakglass recording activation boundary: OK")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
