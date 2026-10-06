#!/usr/bin/env python3
"""Guardrail for attestation.reference scope/variance staying explicit and anti-snowflake."""
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))

def main() -> int:
    errors: list[str] = []
    schema = load_json('spec/attestation.reference.schema.json')
    scope = (schema.get('properties') or {}).get('scope') or {}
    if 'kind' not in (scope.get('required') or []):
        errors.append('spec/attestation.reference.schema.json scope.kind must be required')
    kind_enum = (((scope.get('properties') or {}).get('kind') or {}).get('enum') or [])
    for value in ['cohort', 'deployment', 'host']:
        if value not in kind_enum:
            errors.append(f'spec/attestation.reference.schema.json scope.kind missing enum value: {value}')
    boot = (schema.get('properties') or {}).get('boot') or {}
    if 'variance' not in (boot.get('required') or []):
        errors.append('spec/attestation.reference.schema.json boot.variance must be required')
    variance = ((boot.get('properties') or {}).get('variance') or {})
    mode_enum = (((variance.get('properties') or {}).get('mode') or {}).get('enum') or [])
    for value in ['manifest-replay-first', 'mixed', 'strict-pcr-only']:
        if value not in mode_enum:
            errors.append(f'spec/attestation.reference.schema.json boot.variance.mode missing enum value: {value}')
    example = load_json('spec/examples/attestation.reference.json')
    if ((example.get('scope') or {}).get('kind')) != 'cohort':
        errors.append('spec/examples/attestation.reference.json scope.kind must be cohort in the canonical example')
    variance_obj = ((example.get('boot') or {}).get('variance') or {})
    if variance_obj.get('mode') != 'manifest-replay-first':
        errors.append('spec/examples/attestation.reference.json boot.variance.mode must be manifest-replay-first in the canonical example')
    if example.get('boot', {}).get('strict_pcr_values'):
        errors.append('spec/examples/attestation.reference.json canonical example should not use strict_pcr_values')
    allowed = variance_obj.get('allowed_degraded_reason_codes') or []
    for code in ['FIRMWARE_CLASS_DRIFT', 'OPTIONAL_COMPONENT_MISMATCH']:
        if code not in allowed:
            errors.append(f'spec/examples/attestation.reference.json missing allowed degraded reason code: {code}')
    doc_checks = {
        'docs/176-measured-boot-attestation.md': ['scope.kind = `cohort`', '`boot.variance.mode = manifest-replay-first`', 'per-host allowlist sprawl'],
        'docs/226-platform-posture-and-attestation-results-as-evidence.md': ['`scope.kind`', '`boot.variance.mode`', 'per-host'],
        'docs/313-boot-manifests-and-eventlog-replay.md': ['`manifest-replay-first`', '`strict-pcr-only`', 'per-host'],
        'docs/332-tpm-attestation-in-practice-pcr-registry-uki-keylime.md': ['`scope.kind = cohort`', '`boot.variance.mode = manifest-replay-first`', 'per-host snowflakes'],
        'docs/469-platform-provenance-and-attestation-admission-posture-by-profile.md': ['cohort-scoped reference authoring baseline', 'strict-PCR exception posture'],
        'docs/640-attestation-reference-scope-and-variance-boundary.md': ['`scope.kind`', '`boot.variance.mode`', '`strict-pcr-only`', 'per-host allowlist database'],
        'docs/98-archive-hygiene.md': ['check_attestation_reference_variance_contract.py', 'anti-snowflake'],
        'docs/99-llm-runbook.md': ['check_attestation_reference_variance_contract.py', 'manifest-replay-first'],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding='utf-8')
        for needle in needles:
            if needle not in text:
                errors.append(f'{rel} missing required token: {needle}')
    if errors:
        for err in errors:
            print(f'ERROR: {err}')
        return 1
    print('Attestation reference variance contract: OK')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
