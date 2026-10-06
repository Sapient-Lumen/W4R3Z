#!/usr/bin/env python3
"""Guardrail for attestation.reference exceptions staying timeboxed and approval-shaped."""
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

def main() -> int:
    errors: list[str] = []
    schema = load_json("spec/attestation.reference.schema.json")
    props = schema.get("properties") or {}
    exc = props.get("exception") or {}
    for field in ["reason", "justification", "expires_at", "approvals"]:
        if field not in (exc.get("required") or []):
            errors.append(f"spec/attestation.reference.schema.json exception must require {field}")
    reason_enum = ((exc.get("properties") or {}).get("reason") or {}).get("enum") or []
    for value in ["rollout-window", "hardware-containment", "firmware-class-drift", "regulatory-pin", "legacy-bridge", "incident-containment", "lab-calibration", "other"]:
        if value not in reason_enum:
            errors.append(f"spec/attestation.reference.schema.json exception.reason missing enum value: {value}")
    all_of = schema.get("allOf") or []
    serialized = json.dumps(all_of, sort_keys=True)
    for needle in ['"const": "deployment"', '"const": "host"', '"enum": ["mixed", "strict-pcr-only"]', '"const": "manifest-replay-first"', '"not": {"required": ["strict_pcr_values"]}', '"const": "strict-pcr-only"', '"required": ["strict_pcr_values"]']:
        if needle not in serialized:
            errors.append(f"spec/attestation.reference.schema.json allOf missing rule fragment: {needle}")
    example = load_json("spec/examples/attestation.reference.json")
    if "exception" in example:
        errors.append("spec/examples/attestation.reference.json canonical example must stay on the no-exception baseline")
    doc_checks = {
        "docs/176-measured-boot-attestation.md": ["`exception.expires_at`", "`exception.approvals`", "timeboxed"],
        "docs/226-platform-posture-and-attestation-results-as-evidence.md": ["`attestation.reference.exception`", "timeboxed", "approval-shaped"],
        "docs/313-boot-manifests-and-eventlog-replay.md": ["`attestation.reference.exception`", "`manifest-replay-first`", "`strict_pcr_values` may not hide"],
        "docs/332-tpm-attestation-in-practice-pcr-registry-uki-keylime.md": ["named measured boot policies", "timeboxed exception references", "verifier-side databases"],
        "docs/469-platform-provenance-and-attestation-admission-posture-by-profile.md": ["`attestation.reference.exception`", "timeboxed", "approval-shaped"],
        "docs/640-attestation-reference-scope-and-variance-boundary.md": ["`attestation.reference.exception`", "timeboxed", "approval-shaped"],
        "docs/641-attestation-reference-exceptions-stay-timeboxed-and-approval-shaped.md": ["`exception.expires_at`", "`exception.approvals`", "`strict_pcr_values` may not appear"],
        "docs/98-archive-hygiene.md": ["check_attestation_reference_exception_contract.py", "timeboxed and approval-shaped"],
        "docs/99-llm-runbook.md": ["check_attestation_reference_exception_contract.py", "timeboxed and approval-shaped"],
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
    print("Attestation reference exception contract: OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
