#!/usr/bin/env python3
"""Guardrail for attestation.reference renewals staying digest-linked and successor-shaped."""
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

def main() -> int:
    errors: list[str] = []
    schema = load_json("spec/attestation.reference.schema.json")
    exc = ((schema.get("properties") or {}).get("exception") or {})
    required = exc.get("required") or []
    for field in ["renewal_posture"]:
        if field not in required:
            errors.append(f"spec/attestation.reference.schema.json exception must require {field}")
    renewal_enum = (((exc.get("properties") or {}).get("renewal_posture") or {}).get("enum") or [])
    for value in ["fresh-exception", "supersedes-prior-exception"]:
        if value not in renewal_enum:
            errors.append(f"spec/attestation.reference.schema.json exception.renewal_posture missing enum value: {value}")
    all_of = json.dumps(exc.get("allOf") or [], sort_keys=True)
    for needle in ['"const": "supersedes-prior-exception"', '"required": ["supersedes_reference_digest"]', '"const": "fresh-exception"']:
        if needle not in all_of:
            errors.append(f"spec/attestation.reference.schema.json exception allOf missing rule fragment: {needle}")
    example = load_json("spec/examples/attestation.reference.exception.json")
    exc_ex = example.get("exception") or {}
    if exc_ex.get("renewal_posture") != "supersedes-prior-exception":
        errors.append("spec/examples/attestation.reference.exception.json must demonstrate supersedes-prior-exception renewal posture")
    if not exc_ex.get("supersedes_reference_digest"):
        errors.append("spec/examples/attestation.reference.exception.json must carry supersedes_reference_digest")
    if ((example.get("scope") or {}).get("kind")) != 'deployment':
        errors.append("spec/examples/attestation.reference.exception.json must demonstrate non-baseline deployment scope")
    if (((example.get("boot") or {}).get("variance") or {}).get("mode")) != 'mixed':
        errors.append("spec/examples/attestation.reference.exception.json must demonstrate non-baseline mixed variance mode")
    doc_checks = {
        "docs/176-measured-boot-attestation.md": ["`exception.renewal_posture`", "`exception.supersedes_reference_digest`", "new artifact"],
        "docs/226-platform-posture-and-attestation-results-as-evidence.md": ["`exception.renewal_posture`", "`supersedes-prior-exception`", "row ordering"],
        "docs/313-boot-manifests-and-eventlog-replay.md": ["`supersedes_reference_digest`", "in-place extension", "new artifact"],
        "docs/332-tpm-attestation-in-practice-pcr-registry-uki-keylime.md": ["successor digest", "renewed exception", "verifier-side databases"],
        "docs/469-platform-provenance-and-attestation-admission-posture-by-profile.md": ["digest-linked renewal trail", "successor artifact"],
        "docs/641-attestation-reference-exceptions-stay-timeboxed-and-approval-shaped.md": ["`exception.renewal_posture`", "`exception.supersedes_reference_digest`", "new artifact"],
        "docs/642-attestation-reference-renewals-stay-digest-linked-and-successor-shaped.md": ["`exception.renewal_posture`", "`exception.supersedes_reference_digest`", "successor artifact"],
        "docs/98-archive-hygiene.md": ["check_attestation_reference_renewal_contract.py", "digest-linked and successor-shaped"],
        "docs/99-llm-runbook.md": ["check_attestation_reference_renewal_contract.py", "digest-linked and successor-shaped"],
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
    print("Attestation reference renewal contract: OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
