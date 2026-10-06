#!/usr/bin/env python3
"""Guardrail for decisive attestation-consuming action receipts pinning the exact decision tuple."""
from __future__ import annotations

import json
from pathlib import Path

from cube_digest_lib import canonical_digest, load_json as load_json_strict

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    return load_json_strict(ROOT, rel)


def digest(obj: dict) -> str:
    return canonical_digest(obj)


def main() -> int:
    errors: list[str] = []
    decisive_tokens = ["accepted", "degraded", "rejected", "attestation_requirement_digest", "attestation_receipt_digest", "attestation_admission_policy_digest"]

    for rel in (
        "spec/secret.receipt.schema.json",
        "spec/breakglass.receipt.schema.json",
        "spec/workload.identity.issue.receipt.schema.json",
    ):
        schema = load_json(rel)
        av = (schema.get("properties") or {}).get("attestation_verification") or {}
        desc = av.get("description", "")
        for needle in ["decisive consuming outcomes", "exact requirement/receipt/policy digest tuple", "backend policy-service folklore"]:
            if needle not in desc:
                errors.append(f"{rel} attestation_verification description missing token: {needle}")
        av_props = av.get("properties") or {}
        for key, needle in {
            "attestation_requirement_digest": "actually consumed",
            "attestation_receipt_digest": "actually consumed",
            "attestation_admission_policy_digest": "materially gated",
        }.items():
            if needle not in (av_props.get(key, {}).get("description", "")):
                errors.append(f"{rel} {key} description missing token: {needle}")
        allof_txt = json.dumps(schema.get("allOf", []), sort_keys=True)
        for needle in decisive_tokens:
            if needle not in allof_txt:
                errors.append(f"{rel} allOf missing decisive tuple token: {needle}")

    req = load_json("spec/examples/attestation.requirement.json")
    policy = load_json("spec/examples/attestation.admission.policy.json")
    ordinary_receipt = load_json("spec/examples/attestation.receipt.json")
    breakglass_receipt = load_json("spec/examples/attestation.receipt.breakglass.json")
    req_d = digest(req)
    policy_d = digest(policy)
    ordinary_receipt_d = digest(ordinary_receipt)
    breakglass_receipt_d = digest(breakglass_receipt)

    expected_receipt_digests = {
        "spec/examples/secret.receipt.json": ordinary_receipt_d,
        "spec/examples/breakglass.receipt.json": breakglass_receipt_d,
        "spec/examples/workload.identity.issue.receipt.json": ordinary_receipt_d,
    }
    for rel, expected_receipt_d in expected_receipt_digests.items():
        example = load_json(rel)
        av = example.get("attestation_verification") or {}
        if av.get("decision") != "accepted":
            errors.append(f"{rel} canonical example must demonstrate attestation_verification.decision = accepted")
        if av.get("attestation_requirement_digest") != req_d:
            errors.append(f"{rel} attestation_requirement_digest != digest of spec/examples/attestation.requirement.json")
        if av.get("attestation_receipt_digest") != expected_receipt_d:
            errors.append(f"{rel} attestation_receipt_digest != expected attestation receipt digest for this canonical example")
        if av.get("attestation_admission_policy_digest") != policy_d:
            errors.append(f"{rel} attestation_admission_policy_digest != digest of spec/examples/attestation.admission.policy.json")

    wia = load_json("spec/examples/workload.identity.issue.receipt.json")
    att_ref = wia.get("attestation_ref") or {}
    if att_ref.get("digest") != ((wia.get("attestation_verification") or {}).get("attestation_receipt_digest")):
        errors.append("spec/examples/workload.identity.issue.receipt.json attestation_ref.digest must mirror attestation_verification.attestation_receipt_digest")

    checks = {
        "docs/181-workload-identity-and-secretless-deploys.md": [
            "exact requirement/receipt/policy tuple",
            "attestation_verification",
            "workload-identity-issue-receipt",
        ],
        "docs/223-secrets-and-key-management-as-evidence.md": [
            "exact requirement/receipt/policy tuple",
            "attestation_verification",
            "secret-receipt",
        ],
        "docs/236-breakglass-and-recovery-mode.md": [
            "exact requirement/receipt/policy tuple",
            "attestation_verification",
            "breakglass-receipt",
        ],
        "docs/226-platform-posture-and-attestation-results-as-evidence.md": [
            "exact decision tuple",
            "attestation_requirement_digest",
            "attestation_admission_policy_digest",
        ],
        "docs/388-remote-attestation-admission-and-enrollment.md": [
            "exact decision tuple",
            "attestation_verification",
            "policy-service folklore",
        ],
        "docs/469-platform-provenance-and-attestation-admission-posture-by-profile.md": [
            "exact decision tuple",
            "authoritative action receipts",
            "hidden policy-service state",
        ],
        "docs/492-attestation-results-evidence-and-admission-issue-boundary.md": [
            "full exact decision tuple",
            "attestation_admission_policy_digest",
            "service-side state",
        ],
        "docs/645-attestation-consuming-action-receipts-pin-the-exact-decision-tuple.md": [
            "full exact decision tuple",
            "attestation_requirement_digest",
            "attestation_admission_policy_digest",
        ],
        "docs/98-archive-hygiene.md": [
            "check_attestation_action_verification_contract.py",
            "action-verification guardrail",
        ],
        "docs/99-llm-runbook.md": [
            "docs/645-attestation-consuming-action-receipts-pin-the-exact-decision-tuple.md",
            "check_attestation_action_verification_contract.py",
        ],
    }
    for rel, needles in checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        lower = text.lower()
        for needle in needles:
            if needle.lower() not in lower:
                errors.append(f"{rel} missing token: {needle}")

    if errors:
        print("Attestation action verification contract FAILED:\n")
        for e in errors:
            print(f"- {e}")
        return 1

    print("Attestation action verification contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
