#!/usr/bin/env python3
"""Guardrail for decisive action receipts mirroring the exact pinned attestation verdict."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []

    schema_rels = (
        "spec/secret.receipt.schema.json",
        "spec/breakglass.receipt.schema.json",
        "spec/workload.identity.issue.receipt.schema.json",
    )
    for rel in schema_rels:
        schema = load_json(rel)
        av = ((schema.get("properties") or {}).get("attestation_verification") or {})
        desc = av.get("description", "")
        for needle in [
            "attestation_receipt_verdict",
            "exact verdict already present in the pinned `attestation.receipt`",
            "rather than reinterpreting it in service-side state",
        ]:
            if needle not in desc:
                errors.append(f"{rel} attestation_verification description missing token: {needle}")
        av_props = av.get("properties") or {}
        verdict = av_props.get("attestation_receipt_verdict") or {}
        if verdict.get("enum") != ["pass", "degraded", "fail"]:
            errors.append(f"{rel} attestation_receipt_verdict enum must be ['pass', 'degraded', 'fail']")
        vdesc = verdict.get("description", "")
        for needle in ["accepted`→`pass`", "degraded`→`degraded`", "rejected`→`fail`"]:
            if needle not in vdesc:
                errors.append(f"{rel} attestation_receipt_verdict description missing token: {needle}")
        allof_txt = json.dumps(schema.get("allOf", []), sort_keys=True)
        for needle in [
            "attestation_receipt_verdict",
            "accepted", "pass",
            "degraded",
            "rejected", "fail",
        ]:
            if needle not in allof_txt:
                errors.append(f"{rel} allOf missing verdict-projection token: {needle}")

    example_expectations = {
        "spec/examples/secret.receipt.json": ("accepted", "pass"),
        "spec/examples/secret.receipt.degraded.json": ("degraded", "degraded"),
        "spec/examples/secret.receipt.rejected.json": ("rejected", "fail"),
        "spec/examples/breakglass.receipt.json": ("accepted", "pass"),
        "spec/examples/breakglass.receipt.rejected.json": ("rejected", "fail"),
        "spec/examples/workload.identity.issue.receipt.json": ("accepted", "pass"),
    }
    for rel, (decision, verdict) in example_expectations.items():
        ex = load_json(rel)
        av = ex.get("attestation_verification") or {}
        if av.get("decision") != decision:
            errors.append(f"{rel} attestation_verification.decision must be {decision}")
        if av.get("attestation_receipt_verdict") != verdict:
            errors.append(f"{rel} attestation_verification.attestation_receipt_verdict must be {verdict}")

    checks = {
        "docs/181-workload-identity-and-secretless-deploys.md": [
            "attestation_receipt_verdict",
            "accepted`→`pass`",
            "workload-identity-issue-receipt",
        ],
        "docs/223-secrets-and-key-management-as-evidence.md": [
            "attestation_receipt_verdict",
            "accepted`→`pass`",
            "service-side reinterpretation",
        ],
        "docs/226-platform-posture-and-attestation-results-as-evidence.md": [
            "attestation_receipt_verdict",
            "accepted`→`pass`",
            "may summarize, but they may not rewrite",
        ],
        "docs/236-breakglass-and-recovery-mode.md": [
            "attestation_receipt_verdict",
            "rejected`→`fail`",
            "breakglass-receipt",
        ],
        "docs/388-remote-attestation-admission-and-enrollment.md": [
            "attestation_receipt_verdict",
            "fixed projection",
            "service-side reinterpretation",
        ],
        "docs/469-platform-provenance-and-attestation-admission-posture-by-profile.md": [
            "attestation_receipt_verdict",
            "exact pinned verifier outcome",
            "backend archaeology",
        ],
        "docs/492-attestation-results-evidence-and-admission-issue-boundary.md": [
            "attestation_receipt_verdict",
            "accepted`→`pass`",
            "may not reinterpret",
        ],
        "docs/645-attestation-consuming-action-receipts-pin-the-exact-decision-tuple.md": [
            "attestation_receipt_verdict",
            "exact pinned verdict",
            "reinterpreting the same receipt",
        ],
        "docs/648-attestation-consuming-action-receipts-carry-the-exact-pinned-attestation-verdict.md": [
            "attestation_receipt_verdict",
            "accepted`→`pass`",
            "rejected`→`fail`",
        ],
        "docs/98-archive-hygiene.md": [
            "check_attestation_verdict_projection_contract.py",
            "attestation verdict-projection guardrail",
        ],
        "docs/99-llm-runbook.md": [
            "docs/648-attestation-consuming-action-receipts-carry-the-exact-pinned-attestation-verdict.md",
            "check_attestation_verdict_projection_contract.py",
        ],
    }
    for rel, needles in checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        lower = text.lower()
        for needle in needles:
            if needle.lower() not in lower:
                errors.append(f"{rel} missing token: {needle}")

    if errors:
        print("Attestation verdict projection contract FAILED:\n")
        for e in errors:
            print(f"- {e}")
        return 1

    print("Attestation verdict projection contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
