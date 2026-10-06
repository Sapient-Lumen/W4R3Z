#!/usr/bin/env python3
"""Guardrail for exact breakglass joins on post-breakglass ordinary authority."""
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

    expected_bg = digest(load_json("spec/examples/breakglass.receipt.json"))

    schema_checks = {
        "spec/secret.receipt.schema.json": [
            "relevant_breakglass_receipt_digest",
            "latest-session folklore",
            "created_at` formed the resumption barrier",
        ],
        "spec/workload.identity.issue.receipt.schema.json": [
            "relevant_breakglass_receipt_digest",
            "latest-wins folklore",
            "created_at` formed the resumption barrier",
        ],
    }
    for rel, needles in schema_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        lower = text.lower()
        for needle in needles:
            if needle.lower() not in lower:
                errors.append(f"{rel} missing token: {needle}")

    for rel in ["spec/examples/secret.receipt.json", "spec/examples/workload.identity.issue.receipt.json"]:
        av = (load_json(rel).get("attestation_verification") or {})
        if av.get("relevant_breakglass_receipt_digest") != expected_bg:
            errors.append(f"{rel} attestation_verification.relevant_breakglass_receipt_digest must equal digest of spec/examples/breakglass.receipt.json")

    doc_checks = {
        "docs/181-workload-identity-and-secretless-deploys.md": [
            "relevant_breakglass_receipt_digest",
            "exact breakglass receipt",
        ],
        "docs/223-secrets-and-key-management-as-evidence.md": [
            "relevant_breakglass_receipt_digest",
            "exact breakglass receipt",
        ],
        "docs/226-platform-posture-and-attestation-results-as-evidence.md": [
            "relevant_breakglass_receipt_digest",
            "latest breakglass wins",
        ],
        "docs/236-breakglass-and-recovery-mode.md": [
            "relevant_breakglass_receipt_digest",
            "latest-session folklore",
        ],
        "docs/250-breakglass-and-recovery-workflows.md": [
            "relevant_breakglass_receipt_digest",
            "exact breakglass receipt digest",
        ],
        "docs/388-remote-attestation-admission-and-enrollment.md": [
            "relevant_breakglass_receipt_digest",
            "governing emergency session",
        ],
        "docs/469-platform-provenance-and-attestation-admission-posture-by-profile.md": [
            "relevant_breakglass_receipt_digest",
            "latest breakglass",
        ],
        "docs/492-attestation-results-evidence-and-admission-issue-boundary.md": [
            "relevant_breakglass_receipt_digest",
            "exact breakglass receipt",
        ],
        "docs/649-breakglass-does-not-silently-reopen-ordinary-attestation-gated-authority.md": [
            "docs/650-post-breakglass-ordinary-resumption-stays-exact-breakglass-digest-joined.md",
            "relevant_breakglass_receipt_digest",
        ],
        "docs/650-post-breakglass-ordinary-resumption-stays-exact-breakglass-digest-joined.md": [
            "relevant_breakglass_receipt_digest",
            "latest-session folklore",
            "exact-breakglass-digest joined",
        ],
        "docs/98-archive-hygiene.md": [
            "check_breakglass_resumption_join_contract.py",
            "breakglass resumption exact-join guardrail",
        ],
        "docs/99-llm-runbook.md": [
            "docs/650-post-breakglass-ordinary-resumption-stays-exact-breakglass-digest-joined.md",
            "check_breakglass_resumption_join_contract.py",
        ],
        "README.md": [
            "relevant_breakglass_receipt_digest",
            "latest breakglass wins",
        ],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        lower = text.lower()
        for needle in needles:
            if needle.lower() not in lower:
                errors.append(f"{rel} missing token: {needle}")

    if errors:
        print("Breakglass resumption exact join contract FAILED:\n")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Breakglass resumption exact join contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
