#!/usr/bin/env python3
"""Guardrail for attestation receipts carrying attester identity provenance by digest."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    schema = load_json("spec/attestation.receipt.schema.json")
    idprov = (schema.get("properties") or {}).get("identity_provenance") or {}
    desc = idprov.get("description", "")
    for needle in ["attester.provision.receipt", "digest", "registrar/database lookup folklore"]:
        if needle not in desc:
            errors.append(f"spec/attestation.receipt.schema.json identity_provenance description missing token: {needle}")
    ap = (idprov.get("properties") or {}).get("attester_provision_receipt_digest") or {}
    for needle in ["attester.provision.receipt", "enrolled attester identity"]:
        if needle not in ap.get("description", ""):
            errors.append(
                f"spec/attestation.receipt.schema.json identity_provenance.attester_provision_receipt_digest description missing token: {needle}"
            )
    allof_txt = json.dumps(schema.get("allOf", []), sort_keys=True)
    for needle in ["attester_key_id", "identity_provenance", "attester_provision_receipt_digest"]:
        if needle not in allof_txt:
            errors.append(f"spec/attestation.receipt.schema.json allOf missing rule fragment: {needle}")

    example = load_json("spec/examples/attestation.receipt.json")
    subj = example.get("subject") or {}
    if not subj.get("attester_key_id"):
        errors.append("spec/examples/attestation.receipt.json must demonstrate subject.attester_key_id")
    idp = example.get("identity_provenance") or {}
    if not idp.get("attester_provision_receipt_digest"):
        errors.append("spec/examples/attestation.receipt.json must carry identity_provenance.attester_provision_receipt_digest")

    checks = {
        "docs/176-measured-boot-attestation.md": [
            "attester_provision_receipt_digest",
            "attester key id alone is not enough",
            "exact lifecycle digest join",
        ],
        "docs/226-platform-posture-and-attestation-results-as-evidence.md": [
            "identity_provenance.attester_provision_receipt_digest",
            "attester-provision digest",
            "registrar or inventory lookup",
        ],
        "docs/314-attester-provisioning-and-key-lifecycle-receipts.md": [
            "identity_provenance.attester_provision_receipt_digest",
            "direct exact digest join",
            "attester_key_id` alone is never the review surface",
        ],
        "docs/315-durable-attestation-and-posture-timelines.md": [
            "identity provenance",
            "attester.provision.receipt",
            "AK rotation",
        ],
        "docs/332-tpm-attestation-in-practice-pcr-registry-uki-keylime.md": [
            "inventory database",
            "exact attester-provision digest",
            "wrong verification policy",
        ],
        "docs/469-platform-provenance-and-attestation-admission-posture-by-profile.md": [
            "attester-provision receipt digest",
            "AK handle",
            "reviewable artifacts",
        ],
        "docs/644-attestation-receipts-carry-attester-identity-provenance-by-digest.md": [
            "attester.provision.receipt",
            "identity_provenance.attester_provision_receipt_digest",
            "backend-only truth",
        ],
        "docs/98-archive-hygiene.md": [
            "check_attestation_identity_provenance_contract.py",
            "attestation identity-provenance guardrail",
        ],
        "docs/99-llm-runbook.md": [
            "docs/644-attestation-receipts-carry-attester-identity-provenance-by-digest.md",
            "check_attestation_identity_provenance_contract.py",
        ],
    }
    for rel, needles in checks.items():
        txt = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        lower = txt.lower()
        for needle in needles:
            if needle.lower() not in lower:
                errors.append(f"{rel} missing token: {needle}")

    if errors:
        print("Attestation identity provenance contract FAILED:\n")
        for e in errors:
            print(f"- {e}")
        return 1

    print("Attestation identity provenance contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
