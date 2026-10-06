#!/usr/bin/env python3
"""Guardrail for attestation.reference selection staying exact-digest-pinned and no-latest-wins."""
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

def main() -> int:
    errors: list[str] = []
    ref_schema = load_json("spec/attestation.reference.schema.json")
    scope_selector_desc = ((((ref_schema.get("properties") or {}).get("scope") or {}).get("properties") or {}).get("selector") or {}).get("description", "")
    for needle in ["Not an implicit precedence", "exact reference digest"]:
        if needle not in scope_selector_desc:
            errors.append(f"spec/attestation.reference.schema.json scope.selector description missing token: {needle}")
    ref_id_desc = ((ref_schema.get("properties") or {}).get("reference_id") or {}).get("description", "")
    for needle in ["not for recency", "overlap precedence"]:
        if needle not in ref_id_desc:
            errors.append(f"spec/attestation.reference.schema.json reference_id description missing token: {needle}")
    receipt_schema = load_json("spec/attestation.receipt.schema.json")
    ref_digest_desc = ((receipt_schema.get("properties") or {}).get("reference_digest") or {}).get("description", "")
    for needle in ["Exact digest/id", "No implicit selector/recency resolution"]:
        if needle not in ref_digest_desc:
            errors.append(f"spec/attestation.receipt.schema.json reference_digest description missing token: {needle}")
    doc_checks = {
        "docs/176-measured-boot-attestation.md": ["exact-digest-pinned", "`scope.selector`", "latest-matching selector"],
        "docs/226-platform-posture-and-attestation-results-as-evidence.md": ["exact digest", "`attestation.receipt.reference_digest`", "selector precedence"],
        "docs/313-boot-manifests-and-eventlog-replay.md": ["exact reviewed reference digest", "latest-wins", "selector overlap"],
        "docs/332-tpm-attestation-in-practice-pcr-registry-uki-keylime.md": ["named measured boot policies", "verifier database", "exact digest"],
        "docs/469-platform-provenance-and-attestation-admission-posture-by-profile.md": ["exact-digest-pinned", "selector overlap", "latest matching row"],
        "docs/643-attestation-reference-selection-stays-exact-digest-pinned-and-no-latest-wins.md": ["exact-digest-pinned", "`scope.selector`", "latest-wins-shaped"],
        "docs/98-archive-hygiene.md": ["check_attestation_reference_selection_contract.py", "exact-digest-pinned and no-latest-wins"],
        "docs/99-llm-runbook.md": ["check_attestation_reference_selection_contract.py", "exact-digest-pinned and no-latest-wins"],
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
    print("Attestation reference selection contract: OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
