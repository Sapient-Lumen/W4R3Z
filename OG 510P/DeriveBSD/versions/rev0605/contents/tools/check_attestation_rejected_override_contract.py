#!/usr/bin/env python3
"""Guardrail for rejected attestation not silently minting ordinary authority."""
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

    secret = load_json("spec/secret.receipt.schema.json")
    av = ((secret.get("properties") or {}).get("attestation_verification") or {})
    desc = av.get("description", "")
    for needle in ["rejected", "ordinary secret-delivery actions", "breakglass"]:
        if needle not in desc:
            errors.append(f"spec/secret.receipt.schema.json attestation_verification description missing token: {needle}")
    dec = ((av.get("properties") or {}).get("decision") or {}).get("description", "")
    for needle in ["rejected", "ordinary secret-delivery actions", "breakglass"]:
        if needle not in dec:
            errors.append(f"spec/secret.receipt.schema.json attestation_verification.decision description missing token: {needle}")
    allof_txt = json.dumps(secret.get("allOf", []), sort_keys=True)
    for needle in ["materialize", "fetch", "unseal", "ok", "rejected"]:
        if needle not in allof_txt:
            errors.append(f"spec/secret.receipt.schema.json allOf missing rejected ordinary-delivery token: {needle}")

    wia = load_json("spec/workload.identity.issue.receipt.schema.json")
    wav = ((wia.get("properties") or {}).get("attestation_verification") or {})
    wdesc = wav.get("description", "")
    for needle in ["rejected", "ordinary workload identity", "breakglass"]:
        if needle not in wdesc:
            errors.append(f"spec/workload.identity.issue.receipt.schema.json attestation_verification description missing token: {needle}")
    wdec = ((wav.get("properties") or {}).get("decision") or {}).get("description", "")
    for needle in ["rejected", "ordinary workload identity", "breakglass"]:
        if needle not in wdec:
            errors.append(f"spec/workload.identity.issue.receipt.schema.json attestation_verification.decision description missing token: {needle}")
    w_allof_txt = json.dumps(wia.get("allOf", []), sort_keys=True)
    for needle in ["rejected", "attestation_verification"]:
        if needle not in w_allof_txt:
            errors.append(f"spec/workload.identity.issue.receipt.schema.json allOf missing rejected-issue token: {needle}")

    bg = load_json("spec/breakglass.receipt.schema.json")
    bdesc = (((bg.get("properties") or {}).get("attestation_verification") or {}).get("description", ""))
    for needle in ["Unlike ordinary issue/delivery lanes", "breakglass", "rejected"]:
        if needle not in bdesc:
            errors.append(f"spec/breakglass.receipt.schema.json attestation_verification description missing token: {needle}")

    req = load_json("spec/examples/attestation.requirement.json")
    policy = load_json("spec/examples/attestation.admission.policy.json")
    att_receipt = load_json("spec/examples/attestation.receipt.json")
    req_d = digest(req)
    policy_d = digest(policy)
    att_d = digest(att_receipt)

    secret_rejected = load_json("spec/examples/secret.receipt.rejected.json")
    if secret_rejected.get("action") not in {"materialize", "fetch", "unseal"}:
        errors.append("spec/examples/secret.receipt.rejected.json must demonstrate an ordinary secret-delivery action")
    if secret_rejected.get("result") == "ok":
        errors.append("spec/examples/secret.receipt.rejected.json must not succeed")
    sav = secret_rejected.get("attestation_verification") or {}
    if sav.get("decision") != "rejected":
        errors.append("spec/examples/secret.receipt.rejected.json must demonstrate attestation_verification.decision = rejected")
    if sav.get("attestation_requirement_digest") != req_d:
        errors.append("spec/examples/secret.receipt.rejected.json attestation_requirement_digest != digest of spec/examples/attestation.requirement.json")
    if sav.get("attestation_receipt_digest") != att_d:
        errors.append("spec/examples/secret.receipt.rejected.json attestation_receipt_digest != digest of spec/examples/attestation.receipt.json")
    if sav.get("attestation_admission_policy_digest") != policy_d:
        errors.append("spec/examples/secret.receipt.rejected.json attestation_admission_policy_digest != digest of spec/examples/attestation.admission.policy.json")
    if "fail-closed" not in ((secret_rejected.get("notes") or "") + " " + (secret_rejected.get("error") or "")):
        errors.append("spec/examples/secret.receipt.rejected.json must explain the fail-closed ordinary path")

    bg_grant = load_json("spec/examples/breakglass.grant.json")
    bg_rejected = load_json("spec/examples/breakglass.receipt.rejected.json")
    bav = bg_rejected.get("attestation_verification") or {}
    if bav.get("decision") != "rejected":
        errors.append("spec/examples/breakglass.receipt.rejected.json must demonstrate attestation_verification.decision = rejected")
    if bg_rejected.get("grant_digest") != digest(bg_grant):
        errors.append("spec/examples/breakglass.receipt.rejected.json grant_digest != digest of spec/examples/breakglass.grant.json")
    if bav.get("attestation_requirement_digest") != req_d:
        errors.append("spec/examples/breakglass.receipt.rejected.json attestation_requirement_digest != digest of spec/examples/attestation.requirement.json")
    if bav.get("attestation_receipt_digest") != att_d:
        errors.append("spec/examples/breakglass.receipt.rejected.json attestation_receipt_digest != digest of spec/examples/attestation.receipt.json")
    if bav.get("attestation_admission_policy_digest") != policy_d:
        errors.append("spec/examples/breakglass.receipt.rejected.json attestation_admission_policy_digest != digest of spec/examples/attestation.admission.policy.json")
    if "explicit console recovery proceeded through the breakglass lane" not in (bg_rejected.get("notes") or ""):
        errors.append("spec/examples/breakglass.receipt.rejected.json notes must explain the explicit breakglass recovery path")

    checks = {
        "docs/181-workload-identity-and-secretless-deploys.md": [
            "never silently mints an ordinary workload identity",
            "breakglass",
            "workload-identity-issue-receipt",
        ],
        "docs/223-secrets-and-key-management-as-evidence.md": [
            "ordinary secret-delivery actions fail closed",
            "breakglass",
            "secret-receipt",
        ],
        "docs/236-breakglass-and-recovery-mode.md": [
            "explicit emergency lane",
            "decision = rejected",
            "ordinary issue/delivery lanes",
        ],
        "docs/226-platform-posture-and-attestation-results-as-evidence.md": [
            "ordinary issue/delivery lanes stay fail-closed on rejected posture",
            "breakglass",
            "rejected",
        ],
        "docs/388-remote-attestation-admission-and-enrollment.md": [
            "ordinary issue/delivery lanes stay fail-closed",
            "breakglass",
            "rejected",
        ],
        "docs/469-platform-provenance-and-attestation-admission-posture-by-profile.md": [
            "fail-closed on rejected posture",
            "breakglass",
            "ordinary authority",
        ],
        "docs/492-attestation-results-evidence-and-admission-issue-boundary.md": [
            "fail-closed on rejected posture",
            "breakglass",
            "ordinary authority",
        ],
        "docs/645-attestation-consuming-action-receipts-pin-the-exact-decision-tuple.md": [
            "successful ordinary issue/delivery lanes do not carry `rejected`",
            "breakglass",
            "rejected",
        ],
        "docs/646-attestation-degraded-admission-stays-requirement-shaped-and-no-hidden-waivers.md": [
            "breakglass",
            "rejected posture",
            "ordinary authority",
        ],
        "docs/647-rejected-attestation-does-not-silently-mint-ordinary-authority-breakglass-stays-explicit.md": [
            "ordinary issue/delivery lanes are fail-closed on rejected attestation",
            "breakglass may explicitly record `attestation_verification.decision = rejected`",
            "silent success",
        ],
        "docs/98-archive-hygiene.md": [
            "check_attestation_rejected_override_contract.py",
            "rejected-override guardrail",
        ],
        "docs/99-llm-runbook.md": [
            "docs/647-rejected-attestation-does-not-silently-mint-ordinary-authority-breakglass-stays-explicit.md",
            "check_attestation_rejected_override_contract.py",
        ],
    }
    for rel, needles in checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        lower = text.lower()
        for needle in needles:
            if needle.lower() not in lower:
                errors.append(f"{rel} missing token: {needle}")

    if errors:
        print("Attestation rejected-override contract FAILED:\n")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Attestation rejected-override contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
