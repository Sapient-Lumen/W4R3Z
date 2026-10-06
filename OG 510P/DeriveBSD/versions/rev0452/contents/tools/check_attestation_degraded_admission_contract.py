#!/usr/bin/env python3
"""Guardrail for degraded attestation admission staying requirement-shaped."""
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

    req_schema = load_json("spec/attestation.requirement.schema.json")
    min_verdict = ((req_schema.get("properties") or {}).get("min_verdict") or {}).get("description", "")
    for needle in ["sole portable way", "degraded posture", "hidden one-off waivers"]:
        if needle not in min_verdict:
            errors.append(f"spec/attestation.requirement.schema.json min_verdict description missing token: {needle}")

    for rel in (
        "spec/secret.receipt.schema.json",
        "spec/breakglass.receipt.schema.json",
        "spec/workload.identity.issue.receipt.schema.json",
    ):
        schema = load_json(rel)
        av = ((schema.get("properties") or {}).get("attestation_verification") or {})
        desc = av.get("description", "")
        for needle in ["degraded", "consumed attestation.requirement", "no hidden degraded-waiver lane"]:
            if needle not in desc:
                errors.append(f"{rel} attestation_verification description missing token: {needle}")
        dec = ((av.get("properties") or {}).get("decision") or {}).get("description", "")
        for needle in ["degraded", "consumed attestation.requirement", "no hidden degraded-waiver lane"]:
            if needle not in dec:
                errors.append(f"{rel} attestation_verification.decision description missing token: {needle}")

    degraded_req = load_json("spec/examples/attestation.requirement.degraded.json")
    if degraded_req.get("min_verdict") != "degraded":
        errors.append("spec/examples/attestation.requirement.degraded.json must demonstrate min_verdict = degraded")

    att_receipt = load_json("spec/examples/attestation.receipt.json")
    att_policy = load_json("spec/examples/attestation.admission.policy.json")
    degraded_secret = load_json("spec/examples/secret.receipt.degraded.json")
    av = degraded_secret.get("attestation_verification") or {}
    if av.get("decision") != "degraded":
        errors.append("spec/examples/secret.receipt.degraded.json must demonstrate attestation_verification.decision = degraded")
    if av.get("attestation_requirement_digest") != digest(degraded_req):
        errors.append("spec/examples/secret.receipt.degraded.json attestation_requirement_digest != digest of spec/examples/attestation.requirement.degraded.json")
    if av.get("attestation_receipt_digest") != digest(att_receipt):
        errors.append("spec/examples/secret.receipt.degraded.json attestation_receipt_digest != digest of spec/examples/attestation.receipt.json")
    if av.get("attestation_admission_policy_digest") != digest(att_policy):
        errors.append("spec/examples/secret.receipt.degraded.json attestation_admission_policy_digest != digest of spec/examples/attestation.admission.policy.json")
    if "reviewed degraded attestation requirement" not in (degraded_secret.get("notes") or ""):
        errors.append("spec/examples/secret.receipt.degraded.json notes must explain the reviewed degraded attestation requirement path")

    checks = {
        "docs/226-platform-posture-and-attestation-results-as-evidence.md": [
            "min_verdict = degraded",
            "sole portable way",
            "hidden degraded-waiver lane",
        ],
        "docs/388-remote-attestation-admission-and-enrollment.md": [
            "requirement-shaped",
            "no hidden degraded-waiver lane",
            "breakglass",
        ],
        "docs/469-platform-provenance-and-attestation-admission-posture-by-profile.md": [
            "requirement-shaped",
            "no hidden degraded-waiver lane",
            "degraded posture",
        ],
        "docs/492-attestation-results-evidence-and-admission-issue-boundary.md": [
            "degraded admission stays requirement-shaped",
            "no hidden degraded-waiver lane",
            "breakglass",
        ],
        "docs/645-attestation-consuming-action-receipts-pin-the-exact-decision-tuple.md": [
            "no hidden degraded-waiver lane",
            "attestation.requirement.min_verdict = degraded",
        ],
        "docs/646-attestation-degraded-admission-stays-requirement-shaped-and-no-hidden-waivers.md": [
            "sole portable way",
            "no hidden degraded-waiver lane",
            "attestation.requirement.min_verdict = degraded",
        ],
        "docs/98-archive-hygiene.md": [
            "check_attestation_degraded_admission_contract.py",
            "degraded-admission guardrail",
        ],
        "docs/99-llm-runbook.md": [
            "docs/646-attestation-degraded-admission-stays-requirement-shaped-and-no-hidden-waivers.md",
            "check_attestation_degraded_admission_contract.py",
        ],
    }
    for rel, needles in checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        lower = text.lower()
        for needle in needles:
            if needle.lower() not in lower:
                errors.append(f"{rel} missing token: {needle}")

    if errors:
        print("Attestation degraded admission contract FAILED:\n")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Attestation degraded admission contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
