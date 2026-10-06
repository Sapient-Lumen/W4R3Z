#!/usr/bin/env python3
"""Guardrail for the attestation evidence vs issued-authority boundary.

This checker keeps DeriveBSD's attestation-admission contract wired:
- `attestation.receipt` stays verifier evidence only
- `attestation.admission.policy` maps actions to `attestation.requirement`
- consuming authority receipts summarize attestation decisions in `attestation_verification`
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def jcs_bytes(obj: dict) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(obj: dict) -> str:
    return f"sha256:{hashlib.sha256(jcs_bytes(obj)).hexdigest()}"


def main() -> int:
    errors: list[str] = []

    att_schema = load_json("spec/attestation.receipt.schema.json")
    a_props = att_schema.get("properties") or {}
    if a_props.get("authority_semantics", {}).get("const") != "attestation-evidence-only":
        errors.append("spec/attestation.receipt.schema.json authority_semantics const must be attestation-evidence-only")
    if "authority_semantics" not in (att_schema.get("required") or []):
        errors.append("spec/attestation.receipt.schema.json missing required authority_semantics")

    for rel in (
        "spec/secret.receipt.schema.json",
        "spec/breakglass.receipt.schema.json",
        "spec/workload.identity.issue.receipt.schema.json",
    ):
        schema = load_json(rel)
        av = (schema.get("properties") or {}).get("attestation_verification") or {}
        av_props = av.get("properties") or {}
        for key in ("decision", "attestation_requirement_digest", "attestation_receipt_digest"):
            if key not in av_props:
                errors.append(f"{rel} attestation_verification missing {key}")

    req = load_json("spec/examples/attestation.requirement.json")
    policy = load_json("spec/examples/attestation.admission.policy.json")
    ordinary_receipt = load_json("spec/examples/attestation.receipt.json")
    breakglass_attestation_receipt = load_json("spec/examples/attestation.receipt.breakglass.json")
    secret_receipt = load_json("spec/examples/secret.receipt.json")
    breakglass_grant = load_json("spec/examples/breakglass.grant.json")
    breakglass_receipt = load_json("spec/examples/breakglass.receipt.json")
    secret_grant = load_json("spec/examples/secret.grant.json")
    wia_receipt = load_json("spec/examples/workload.identity.issue.receipt.json")

    req_d = digest(req)
    policy_d = digest(policy)
    ordinary_receipt_d = digest(ordinary_receipt)
    breakglass_attestation_receipt_d = digest(breakglass_attestation_receipt)
    breakglass_grant_d = digest(breakglass_grant)

    if ordinary_receipt.get("authority_semantics") != "attestation-evidence-only":
        errors.append("spec/examples/attestation.receipt.json authority_semantics must be attestation-evidence-only")

    for i, rule in enumerate(policy.get("rules") or [], start=1):
        if rule.get("requirement_ref") != req_d:
            errors.append(f"spec/examples/attestation.admission.policy.json rules[{i}] requirement_ref != computed digest of spec/examples/attestation.requirement.json")

    if (breakglass_grant.get("constraints") or {}).get("attestation_requirement_digest") != req_d:
        errors.append("spec/examples/breakglass.grant.json constraints.attestation_requirement_digest != computed digest of spec/examples/attestation.requirement.json")
    if (secret_grant.get("constraints") or {}).get("attestation_requirement_digest") != req_d:
        errors.append("spec/examples/secret.grant.json constraints.attestation_requirement_digest != computed digest of spec/examples/attestation.requirement.json")
    if breakglass_receipt.get("grant_digest") != breakglass_grant_d:
        errors.append("spec/examples/breakglass.receipt.json grant_digest != computed digest of spec/examples/breakglass.grant.json")

    expected_receipt_digests = {
        "spec/examples/secret.receipt.json": ordinary_receipt_d,
        "spec/examples/breakglass.receipt.json": breakglass_attestation_receipt_d,
        "spec/examples/workload.identity.issue.receipt.json": ordinary_receipt_d,
    }
    for rel, obj in (
        ("spec/examples/secret.receipt.json", secret_receipt),
        ("spec/examples/breakglass.receipt.json", breakglass_receipt),
        ("spec/examples/workload.identity.issue.receipt.json", wia_receipt),
    ):
        av = obj.get("attestation_verification") or {}
        if av.get("decision") != "accepted":
            errors.append(f"{rel} attestation_verification.decision must be accepted in the canonical example")
        if av.get("attestation_requirement_digest") != req_d:
            errors.append(f"{rel} attestation_verification.attestation_requirement_digest != computed digest of spec/examples/attestation.requirement.json")
        if av.get("attestation_receipt_digest") != expected_receipt_digests[rel]:
            errors.append(f"{rel} attestation_verification.attestation_receipt_digest != expected attestation receipt digest for this canonical example")
        if av.get("attestation_admission_policy_digest") != policy_d:
            errors.append(f"{rel} attestation_verification.attestation_admission_policy_digest != computed digest of spec/examples/attestation.admission.policy.json")

    wia_ref = (wia_receipt.get("attestation_ref") or {})
    if wia_ref.get("kind") != "attestation.receipt":
        errors.append("spec/examples/workload.identity.issue.receipt.json attestation_ref.kind must remain attestation.receipt")
    if wia_ref.get("digest") != ordinary_receipt_d:
        errors.append("spec/examples/workload.identity.issue.receipt.json attestation_ref.digest != computed digest of spec/examples/attestation.receipt.json")

    doc_checks = {
        "docs/226-platform-posture-and-attestation-results-as-evidence.md": [
            "`attestation.receipt`",
            "`attestation.admission.policy`",
            "`attestation.requirement`",
            "`attestation_verification`",
        ],
        "docs/388-remote-attestation-admission-and-enrollment.md": [
            "`attestation.receipt`",
            "`attestation.admission.policy`",
            "`attestation.requirement`",
            "`attestation_verification`",
        ],
        "docs/492-attestation-results-evidence-and-admission-issue-boundary.md": [
            "`attestation.receipt`",
            "`attestation.admission.policy`",
            "`attestation.requirement`",
            "`secret-receipt`",
            "`breakglass-receipt`",
            "`workload-identity-issue-receipt`",
            "`attestation_verification`",
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

    print("Attestation admission contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
