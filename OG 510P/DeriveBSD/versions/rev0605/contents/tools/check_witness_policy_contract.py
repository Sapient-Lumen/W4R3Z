#!/usr/bin/env python3
"""Guardrail for the witness-policy boundary.

This checker keeps DeriveBSD's witness-trust contract wired:
- witness roster/quorum/shortfall are defined by `witness.policy`
- `log.checkpoint.receipt` binds `witness_policy_digest` + `quorum_verdict`
- `transparency.monitor.policy` and `release.authority.policy` reference the same digest-bound witness policy
- publish receipts summarize witness-policy results instead of inferring trust from backend state
"""
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

    witness_schema = load_json("spec/witness.policy.schema.json")
    props = witness_schema.get("properties") or {}
    for key in ("log_scope", "witnesses", "quorum", "shortfall"):
        if key not in props:
            errors.append(f"spec/witness.policy.schema.json missing property {key}")
    if props.get("kind", {}).get("const") != "witness.policy":
        errors.append("spec/witness.policy.schema.json kind const must be witness.policy")

    checkpoint_schema = load_json("spec/log.checkpoint.receipt.schema.json")
    c_props = checkpoint_schema.get("properties") or {}
    for key in ("witness_policy_digest", "quorum_verdict"):
        if key not in c_props:
            errors.append(f"spec/log.checkpoint.receipt.schema.json missing property {key}")
    if "witness_policy_digest" not in (checkpoint_schema.get("required") or []):
        errors.append("spec/log.checkpoint.receipt.schema.json missing required witness_policy_digest")
    if "quorum_verdict" not in (checkpoint_schema.get("required") or []):
        errors.append("spec/log.checkpoint.receipt.schema.json missing required quorum_verdict")

    monitor_schema = load_json("spec/transparency.monitor.policy.schema.json")
    m_props = (((monitor_schema.get("properties") or {}).get("logs") or {}).get("items") or {}).get("properties") or {}
    if "witness_policy_digest" not in m_props:
        errors.append("spec/transparency.monitor.policy.schema.json logs items missing witness_policy_digest")
    if "witness_quorum" in m_props:
        errors.append("spec/transparency.monitor.policy.schema.json must not expose legacy logs[].witness_quorum")

    authority_schema = load_json("spec/release.authority.policy.schema.json")
    t_props = (((authority_schema.get("properties") or {}).get("transparency") or {}).get("properties") or {})
    if "witness_policy_digest" not in t_props:
        errors.append("spec/release.authority.policy.schema.json transparency missing witness_policy_digest")
    if "require_witness_quorum" in t_props:
        errors.append("spec/release.authority.policy.schema.json must not expose legacy transparency.require_witness_quorum")

    publish_schema = load_json("spec/release.publish.receipt.schema.json")
    tv_props = (((publish_schema.get("properties") or {}).get("transparency_verification") or {}).get("properties") or {})
    for key in ("witness_policy_digest", "checkpoint_quorum_verdict"):
        if key not in tv_props:
            errors.append(f"spec/release.publish.receipt.schema.json transparency_verification missing {key}")

    witness = load_json("spec/examples/witness.policy.json")
    checkpoint = load_json("spec/examples/log.checkpoint.receipt.json")
    monitor = load_json("spec/examples/transparency.monitor.policy.json")
    authority = load_json("spec/examples/release.authority.policy.json")
    publish = load_json("spec/examples/release.publish.receipt.json")

    witness_d = digest(witness)
    if checkpoint.get("witness_policy_digest") != witness_d:
        errors.append("spec/examples/log.checkpoint.receipt.json witness_policy_digest != computed digest of spec/examples/witness.policy.json")
    if checkpoint.get("quorum_verdict") != "satisfied":
        errors.append("spec/examples/log.checkpoint.receipt.json quorum_verdict must be satisfied")
    if monitor.get("logs", [{}])[0].get("witness_policy_digest") != witness_d:
        errors.append("spec/examples/transparency.monitor.policy.json logs[0].witness_policy_digest != computed digest of spec/examples/witness.policy.json")
    if authority.get("transparency", {}).get("witness_policy_digest") != witness_d:
        errors.append("spec/examples/release.authority.policy.json transparency.witness_policy_digest != computed digest of spec/examples/witness.policy.json")
    tv = publish.get("transparency_verification") or {}
    if tv.get("witness_policy_digest") != witness_d:
        errors.append("spec/examples/release.publish.receipt.json transparency_verification.witness_policy_digest != computed digest of spec/examples/witness.policy.json")
    if tv.get("checkpoint_quorum_verdict") != checkpoint.get("quorum_verdict"):
        errors.append("spec/examples/release.publish.receipt.json transparency_verification.checkpoint_quorum_verdict must match spec/examples/log.checkpoint.receipt.json quorum_verdict")

    doc_checks = {
        "docs/282-witness-cosigning-checkpoints-and-witness-networks.md": [
            "`witness.policy`",
            "`log.checkpoint.receipt`",
            "`witness_policy_digest`",
            "`quorum_verdict`",
        ],
        "docs/259-transparency-monitors-and-witness-gossip.md": [
            "`transparency.monitor.policy`",
            "`witness.policy`",
            "`witness_policy_digest`",
            "`release.publish.receipt`",
        ],
        "docs/260-release-authority-policy-and-key-management.md": [
            "`release.authority.policy`",
            "`witness.policy`",
            "`witness_policy_digest`",
            "`transparency_verification`",
        ],
        "docs/490-witness-policy-and-roster-quorum-boundary.md": [
            "`witness.policy`",
            "`log.checkpoint.receipt`",
            "`transparency.monitor.policy`",
            "`release.authority.policy`",
            "`witness_policy_digest`",
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

    print("Witness policy contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
