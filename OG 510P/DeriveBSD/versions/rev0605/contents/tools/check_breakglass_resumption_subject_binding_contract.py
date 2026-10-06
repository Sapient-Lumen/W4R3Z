#!/usr/bin/env python3
"""Guardrail for same-host binding on post-breakglass ordinary resumption."""
from __future__ import annotations

import json
from pathlib import Path

from cube_digest_lib import file_json_digest, load_json as load_json_strict

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    return load_json_strict(ROOT, rel)


def digest(rel: str) -> str:
    return file_json_digest(ROOT, rel)


def main() -> int:
    errors: list[str] = []

    att = load_json("spec/examples/attestation.receipt.json")
    bg = load_json("spec/examples/breakglass.receipt.json")
    att_host = ((att.get("subject") or {}).get("host_id"))
    bg_host = ((bg.get("session") or {}).get("host_id"))
    if not att_host:
        errors.append("spec/examples/attestation.receipt.json must carry subject.host_id")
    if not bg_host:
        errors.append("spec/examples/breakglass.receipt.json must carry session.host_id")
    if att_host != bg_host:
        errors.append("canonical attestation/breakglass examples must name the same host for post-breakglass resumption")

    att_d = digest("spec/examples/attestation.receipt.json")
    bg_d = digest("spec/examples/breakglass.receipt.json")

    for rel in ["spec/examples/secret.receipt.json", "spec/examples/workload.identity.issue.receipt.json"]:
        ex = load_json(rel)
        av = ex.get("attestation_verification") or {}
        if av.get("attestation_receipt_digest") != att_d:
            errors.append(f"{rel} attestation_verification.attestation_receipt_digest must equal digest of spec/examples/attestation.receipt.json")
        if av.get("relevant_breakglass_receipt_digest") != bg_d:
            errors.append(f"{rel} attestation_verification.relevant_breakglass_receipt_digest must equal digest of spec/examples/breakglass.receipt.json")

    schema_checks = {
        "spec/secret.receipt.schema.json": [
            "same host as the pinned `attestation.receipt.subject.host_id`",
            "cross-host emergency context",
            "cross-host inventory joins",
        ],
        "spec/workload.identity.issue.receipt.schema.json": [
            "same host as the pinned `attestation.receipt.subject.host_id`",
            "cross-host emergency context",
            "cross-host inventory joins",
        ],
    }
    for rel, needles in schema_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        lower = text.lower()
        for needle in needles:
            if needle.lower() not in lower:
                errors.append(f"{rel} missing token: {needle}")

    doc_checks = {
        "docs/181-workload-identity-and-secretless-deploys.md": ["same host", "cross-host join folklore"],
        "docs/223-secrets-and-key-management-as-evidence.md": ["same host", "cross-host join folklore"],
        "docs/226-platform-posture-and-attestation-results-as-evidence.md": ["same host", "cross-host join"],
        "docs/236-breakglass-and-recovery-mode.md": ["same host", "cross-host join folklore"],
        "docs/250-breakglass-and-recovery-workflows.md": ["same host", "cross-host join folklore"],
        "docs/388-remote-attestation-admission-and-enrollment.md": ["same host", "cross-host join folklore"],
        "docs/469-platform-provenance-and-attestation-admission-posture-by-profile.md": ["same host", "cross-host join folklore"],
        "docs/492-attestation-results-evidence-and-admission-issue-boundary.md": ["same host", "cross-host join folklore"],
        "docs/650-post-breakglass-ordinary-resumption-stays-exact-breakglass-digest-joined.md": ["docs/651-post-breakglass-ordinary-resumption-stays-same-host-bound.md", "same host"],
        "docs/651-post-breakglass-ordinary-resumption-stays-same-host-bound.md": ["same-host bound", "cross-host join folklore", "attestation.receipt.subject.host_id"],
        "docs/98-archive-hygiene.md": ["check_breakglass_resumption_subject_binding_contract.py", "breakglass resumption same-host guardrail"],
        "docs/99-llm-runbook.md": ["docs/651-post-breakglass-ordinary-resumption-stays-same-host-bound.md", "check_breakglass_resumption_subject_binding_contract.py"],
        "README.md": ["same host", "cross-host join folklore"],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        lower = text.lower()
        for needle in needles:
            if needle.lower() not in lower:
                errors.append(f"{rel} missing token: {needle}")

    if errors:
        print("Breakglass resumption same-host binding contract FAILED:\n")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Breakglass resumption same-host binding contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
