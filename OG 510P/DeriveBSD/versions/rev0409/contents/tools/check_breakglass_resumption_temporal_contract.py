#!/usr/bin/env python3
"""Guardrail for time-ordered post-breakglass ordinary resumption."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def jcs_bytes(obj: dict) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(rel: str) -> str:
    return "sha256:" + hashlib.sha256(jcs_bytes(load_json(rel))).hexdigest()


def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def main() -> int:
    errors: list[str] = []

    bg = load_json("spec/examples/breakglass.receipt.json")
    att = load_json("spec/examples/attestation.receipt.json")
    sec = load_json("spec/examples/secret.receipt.json")
    wia = load_json("spec/examples/workload.identity.issue.receipt.json")
    incident = load_json("spec/examples/incident.bundle.json")

    bg_created = parse_ts(bg["created_at"])
    att_created = parse_ts(att["created_at"])
    sec_emitted = parse_ts(sec["emitted_at"])
    wia_issued = parse_ts(wia["issued_at"])
    wia_captured = parse_ts(wia["captured_at"])
    incident_created = parse_ts(incident["created_at"])

    if not att_created > bg_created:
        errors.append("spec/examples/attestation.receipt.json created_at must be strictly later than spec/examples/breakglass.receipt.json created_at")
    if sec_emitted < att_created:
        errors.append("spec/examples/secret.receipt.json emitted_at must not predate spec/examples/attestation.receipt.json created_at")
    if wia_issued < att_created:
        errors.append("spec/examples/workload.identity.issue.receipt.json issued_at must not predate spec/examples/attestation.receipt.json created_at")
    if wia_captured < att_created:
        errors.append("spec/examples/workload.identity.issue.receipt.json captured_at must not predate spec/examples/attestation.receipt.json created_at")
    if incident_created < sec_emitted:
        errors.append("spec/examples/incident.bundle.json created_at must not predate the canonical secret receipt it includes")
    if incident_created < att_created:
        errors.append("spec/examples/incident.bundle.json created_at must not predate the canonical attestation receipt it includes")
    if incident_created < bg_created:
        errors.append("spec/examples/incident.bundle.json created_at must not predate the canonical breakglass receipt it includes")

    att_d = digest("spec/examples/attestation.receipt.json")
    bg_d = digest("spec/examples/breakglass.receipt.json")
    if (sec.get("attestation_verification") or {}).get("attestation_receipt_digest") != att_d:
        errors.append("spec/examples/secret.receipt.json must point to the canonical attestation receipt digest")
    if (sec.get("attestation_verification") or {}).get("relevant_breakglass_receipt_digest") != bg_d:
        errors.append("spec/examples/secret.receipt.json must point to the canonical breakglass receipt digest")
    if (wia.get("attestation_verification") or {}).get("attestation_receipt_digest") != att_d:
        errors.append("spec/examples/workload.identity.issue.receipt.json must point to the canonical attestation receipt digest")
    if (wia.get("attestation_verification") or {}).get("relevant_breakglass_receipt_digest") != bg_d:
        errors.append("spec/examples/workload.identity.issue.receipt.json must point to the canonical breakglass receipt digest")

    schema_checks = {
        "spec/secret.receipt.schema.json": [
            "attestation.receipt.created_at` must be strictly later than the relevant breakglass receipt `created_at`",
            "secret-receipt.emitted_at",
            "must not predate the pinned `attestation.receipt.created_at`",
        ],
        "spec/workload.identity.issue.receipt.schema.json": [
            "attestation.receipt.created_at` must be strictly later than the relevant breakglass receipt `created_at`",
            "workload-identity-issue-receipt.issued_at and `captured_at`",
            "must not predate the pinned `attestation.receipt.created_at`",
        ],
        "spec/breakglass.receipt.schema.json": [
            "later ordinary receipt must not predate the fresh attestation receipt it claims to consume",
            "fresh-attestation-after-breakglass-created-at-required",
        ],
    }
    for rel, needles in schema_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        lower = text.lower()
        for needle in needles:
            if needle.lower() not in lower:
                errors.append(f"{rel} missing token: {needle}")

    doc_checks = {
        "docs/181-workload-identity-and-secretless-deploys.md": ["strictly later than the relevant breakglass receipt `created_at`", "issued_at` / `captured_at` must not predate the pinned `attestation.receipt.created_at`"],
        "docs/223-secrets-and-key-management-as-evidence.md": ["strictly later than the relevant breakglass receipt `created_at`", "`secret-receipt.emitted_at` must not predate the pinned `attestation.receipt.created_at`"],
        "docs/226-platform-posture-and-attestation-results-as-evidence.md": ["causally ordered", "must not predate the pinned `attestation.receipt.created_at`"],
        "docs/236-breakglass-and-recovery-mode.md": ["time-ordered too", "later ordinary receipt must not predate the fresh attestation receipt it claims to consume"],
        "docs/250-breakglass-and-recovery-workflows.md": ["strictly later than the exact breakglass receipt `created_at`", "must not predate the pinned `attestation.receipt.created_at`"],
        "docs/388-remote-attestation-admission-and-enrollment.md": ["strictly later than the relevant breakglass receipt `created_at`", "must not predate the pinned `attestation.receipt.created_at`"],
        "docs/469-platform-provenance-and-attestation-admission-posture-by-profile.md": ["time-ordered post-breakglass", "must not predate the pinned `attestation.receipt.created_at`"],
        "docs/492-attestation-results-evidence-and-admission-issue-boundary.md": ["strictly later than the relevant breakglass receipt `created_at`", "portable causal story"],
        "docs/650-post-breakglass-ordinary-resumption-stays-exact-breakglass-digest-joined.md": ["docs/652-post-breakglass-ordinary-resumption-stays-time-ordered.md", "time-ordered"],
        "docs/651-post-breakglass-ordinary-resumption-stays-same-host-bound.md": ["docs/652-post-breakglass-ordinary-resumption-stays-time-ordered.md", "time chain"],
        "docs/652-post-breakglass-ordinary-resumption-stays-time-ordered.md": ["strictly later", "must not predate", "causally ordered"],
        "docs/98-archive-hygiene.md": ["check_breakglass_resumption_temporal_contract.py", "breakglass resumption temporal guardrail"],
        "docs/99-llm-runbook.md": ["docs/652-post-breakglass-ordinary-resumption-stays-time-ordered.md", "check_breakglass_resumption_temporal_contract.py"],
        "README.md": ["time-ordered as well", "must not predate the pinned attestation receipt"],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        lower = text.lower()
        for needle in needles:
            if needle.lower() not in lower:
                errors.append(f"{rel} missing token: {needle}")

    if errors:
        print("Breakglass resumption temporal contract FAILED:\n")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Breakglass resumption temporal contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
