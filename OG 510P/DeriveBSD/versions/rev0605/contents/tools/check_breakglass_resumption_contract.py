#!/usr/bin/env python3
"""Guardrail for breakglass not silently reopening ordinary attestation-gated authority."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []

    bg = load_json("spec/breakglass.receipt.schema.json")
    if "ordinary_resumption_posture" not in (bg.get("required") or []):
        errors.append("spec/breakglass.receipt.schema.json must require ordinary_resumption_posture")
    posture = (bg.get("properties") or {}).get("ordinary_resumption_posture") or {}
    if posture.get("const") != "fresh-attestation-after-breakglass-created-at-required":
        errors.append("spec/breakglass.receipt.schema.json ordinary_resumption_posture const mismatch")
    pdesc = posture.get("description", "")
    for needle in [
        "does not silently reopen ordinary attestation-gated authority",
        "fresh attestation.receipt issued after this breakglass receipt `created_at`",
        "pre-breakglass accepted/degraded receipt",
    ]:
        if needle not in pdesc:
            errors.append(f"spec/breakglass.receipt.schema.json ordinary_resumption_posture description missing token: {needle}")
    av_desc = (((bg.get("properties") or {}).get("attestation_verification") or {}).get("description", ""))
    for needle in [
        "ordinary_resumption_posture",
        "fresh-attestation-after-breakglass-created-at-required",
        "issued after this breakglass receipt `created_at`",
    ]:
        if needle not in av_desc:
            errors.append(f"spec/breakglass.receipt.schema.json attestation_verification description missing token: {needle}")
    allof_txt = json.dumps(bg.get("allOf", []), sort_keys=True)
    for needle in ["ordinary_resumption_posture", "fresh-attestation-after-breakglass-created-at-required"]:
        if needle not in allof_txt:
            errors.append(f"spec/breakglass.receipt.schema.json allOf missing resumption token: {needle}")

    for rel in ["spec/examples/breakglass.receipt.json", "spec/examples/breakglass.receipt.rejected.json"]:
        ex = load_json(rel)
        if ex.get("ordinary_resumption_posture") != "fresh-attestation-after-breakglass-created-at-required":
            errors.append(f"{rel} ordinary_resumption_posture must be fresh-attestation-after-breakglass-created-at-required")
        notes = ex.get("notes", "")
        if "fresh attestation receipt issued after this breakglass entry" not in notes:
            errors.append(f"{rel} notes must explain fresh post-breakglass attestation for ordinary resumption")

    schema_checks = {
        "spec/secret.receipt.schema.json": [
            "relevant breakglass receipt `created_at`",
            "fresh attestation receipt issued after",
            "reusing pre-breakglass evidence",
        ],
        "spec/workload.identity.issue.receipt.schema.json": [
            "relevant breakglass receipt `created_at`",
            "fresh attestation receipt issued after",
            "reusing pre-breakglass evidence",
        ],
    }
    for rel, needles in schema_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        lower = text.lower()
        for needle in needles:
            if needle.lower() not in lower:
                errors.append(f"{rel} missing token: {needle}")

    doc_checks = {
        "docs/223-secrets-and-key-management-as-evidence.md": [
            "fresh `attestation.receipt` issued after the relevant breakglass receipt `created_at`",
            "ordinary secret-delivery actions",
        ],
        "docs/181-workload-identity-and-secretless-deploys.md": [
            "fresh `attestation.receipt` issued after the relevant breakglass receipt `created_at`",
            "ordinary workload identity",
        ],
        "docs/226-platform-posture-and-attestation-results-as-evidence.md": [
            "breakglass does not silently reopen ordinary attestation-gated authority",
            "fresh `attestation.receipt` issued after that breakglass `created_at`",
        ],
        "docs/236-breakglass-and-recovery-mode.md": [
            "ordinary_resumption_posture",
            "fresh-attestation-after-breakglass-created-at-required",
            "ordinary attestation-gated lanes resume only on a fresh `attestation.receipt` issued after the breakglass receipt `created_at`",
        ],
        "docs/250-breakglass-and-recovery-workflows.md": [
            "fresh post-breakglass attestation",
            "ordinary attestation-gated lanes",
        ],
        "docs/388-remote-attestation-admission-and-enrollment.md": [
            "fresh `attestation.receipt` issued after the relevant breakglass receipt `created_at`",
            "ordinary lanes",
        ],
        "docs/469-platform-provenance-and-attestation-admission-posture-by-profile.md": [
            "fresh `attestation.receipt` issued after the relevant breakglass receipt `created_at`",
            "breakglass remains explicit rather than sticky ordinary authority",
        ],
        "docs/492-attestation-results-evidence-and-admission-issue-boundary.md": [
            "fresh `attestation.receipt` issued after the relevant breakglass receipt `created_at`",
            "breakglass is not standing ordinary authority",
        ],
        "docs/647-rejected-attestation-does-not-silently-mint-ordinary-authority-breakglass-stays-explicit.md": [
            "fresh post-breakglass attestation",
            "ordinary attestation-gated lanes",
        ],
        "docs/648-attestation-consuming-action-receipts-carry-the-exact-pinned-attestation-verdict.md": [
            "fresh post-breakglass attestation",
            "ordinary authority only resumes",
        ],
        "docs/649-breakglass-does-not-silently-reopen-ordinary-attestation-gated-authority.md": [
            "ordinary_resumption_posture",
            "fresh-attestation-after-breakglass-created-at-required",
            "breakglass stays explicit and bounded",
        ],
        "docs/98-archive-hygiene.md": [
            "check_breakglass_resumption_contract.py",
            "breakglass resumption guardrail",
        ],
        "docs/99-llm-runbook.md": [
            "docs/649-breakglass-does-not-silently-reopen-ordinary-attestation-gated-authority.md",
            "check_breakglass_resumption_contract.py",
        ],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        lower = text.lower()
        for needle in needles:
            if needle.lower() not in lower:
                errors.append(f"{rel} missing token: {needle}")

    if errors:
        print("Breakglass resumption contract FAILED:\n")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Breakglass resumption contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
