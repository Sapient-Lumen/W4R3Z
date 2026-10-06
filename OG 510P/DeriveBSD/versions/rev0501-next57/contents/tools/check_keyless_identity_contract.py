#!/usr/bin/env python3
"""Guardrail for the keyless-identity / release-authority boundary.

This checker keeps DeriveBSD's publisher-identity lane wired:
- `publisher.identity.receipt` remains supplemental identity evidence
- `sigstore-keyless` receipts bind both bundle and verification-root digests
- `release.authority.policy` may constrain identity evidence without replacing thresholds
- `release.publish.receipt` can summarize the identity-evidence decision
- key docs explicitly state the boundary
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

    receipt_schema = load_json("spec/publisher.identity.receipt.schema.json")
    if "authority_semantics" not in receipt_schema.get("required", []):
        errors.append("spec/publisher.identity.receipt.schema.json missing required authority_semantics")
    props = receipt_schema.get("properties") or {}
    for key in ("authority_semantics", "sigstore_bundle_digest", "verification_roots_digest"):
        if key not in props:
            errors.append(f"spec/publisher.identity.receipt.schema.json missing property {key}")
    if props.get("authority_semantics", {}).get("const") != "identity-evidence-only":
        errors.append("spec/publisher.identity.receipt.schema.json authority_semantics must const to identity-evidence-only")
    all_of = receipt_schema.get("allOf") or []
    has_sigstore_requirement = False
    for item in all_of:
        if ((item.get("if") or {}).get("properties") or {}).get("method", {}).get("const") == "sigstore-keyless":
            req = set((item.get("then") or {}).get("required") or [])
            if {"sigstore_bundle_digest", "verification_roots_digest"}.issubset(req):
                has_sigstore_requirement = True
    if not has_sigstore_requirement:
        errors.append("spec/publisher.identity.receipt.schema.json must require sigstore_bundle_digest + verification_roots_digest for method=sigstore-keyless")

    authority_schema = load_json("spec/release.authority.policy.schema.json")
    identity_evidence_props = (((authority_schema.get("properties") or {}).get("identity_evidence") or {}).get("properties") or {})
    for key in ("mode", "allowed_methods", "allowed_issuers", "require_offline_verification_material"):
        if key not in identity_evidence_props:
            errors.append(f"spec/release.authority.policy.schema.json missing identity_evidence.{key}")

    publish_schema = load_json("spec/release.publish.receipt.schema.json")
    publish_identity_props = (((publish_schema.get("properties") or {}).get("identity_evidence") or {}).get("properties") or {})
    for key in ("decision", "publisher_identity_receipt_digests"):
        if key not in publish_identity_props:
            errors.append(f"spec/release.publish.receipt.schema.json missing identity_evidence.{key}")

    sigstore_bundle = load_json("spec/examples/sigstore.bundle.json")
    trust_roots = load_json("spec/examples/pki.trust.bundle.json")
    identity_receipt = load_json("spec/examples/publisher.identity.receipt.json")
    authority_policy = load_json("spec/examples/release.authority.policy.json")
    publish_receipt = load_json("spec/examples/release.publish.receipt.json")

    sigstore_bundle_d = digest(sigstore_bundle)
    trust_roots_d = digest(trust_roots)
    identity_receipt_d = digest(identity_receipt)
    authority_policy_d = digest(authority_policy)

    if identity_receipt.get("authority_semantics") != "identity-evidence-only":
        errors.append("spec/examples/publisher.identity.receipt.json authority_semantics must be identity-evidence-only")
    if identity_receipt.get("method") != "sigstore-keyless":
        errors.append("spec/examples/publisher.identity.receipt.json method must be sigstore-keyless")
    if identity_receipt.get("sigstore_bundle_digest") != sigstore_bundle_d:
        errors.append("spec/examples/publisher.identity.receipt.json sigstore_bundle_digest != computed digest of spec/examples/sigstore.bundle.json")
    if identity_receipt.get("verification_roots_digest") != trust_roots_d:
        errors.append("spec/examples/publisher.identity.receipt.json verification_roots_digest != computed digest of spec/examples/pki.trust.bundle.json")

    identity_policy = authority_policy.get("identity_evidence") or {}
    if identity_policy.get("mode") != "required":
        errors.append("spec/examples/release.authority.policy.json identity_evidence.mode must be required")
    if "sigstore-keyless" not in (identity_policy.get("allowed_methods") or []):
        errors.append("spec/examples/release.authority.policy.json identity_evidence.allowed_methods must include sigstore-keyless")
    if not identity_policy.get("require_offline_verification_material"):
        errors.append("spec/examples/release.authority.policy.json identity_evidence.require_offline_verification_material must be true")

    if publish_receipt.get("authority_policy_digest") != authority_policy_d:
        errors.append("spec/examples/release.publish.receipt.json authority_policy_digest != computed digest of spec/examples/release.authority.policy.json")
    publish_identity = publish_receipt.get("identity_evidence") or {}
    if publish_identity.get("decision") != "accepted":
        errors.append("spec/examples/release.publish.receipt.json identity_evidence.decision must be accepted")
    if identity_receipt_d not in (publish_identity.get("publisher_identity_receipt_digests") or []):
        errors.append("spec/examples/release.publish.receipt.json identity_evidence.publisher_identity_receipt_digests must include computed digest of spec/examples/publisher.identity.receipt.json")

    doc_checks = {
        "docs/290-keyless-signing-and-publisher-identity-receipts.md": [
            "`publisher.identity.receipt`",
            "`authority_semantics = identity-evidence-only`",
            "`sigstore_bundle_digest`",
            "`verification_roots_digest`",
            "`release.authority.policy`",
        ],
        "docs/333-sigstore-bundles-and-offline-verification.md": [
            "`sigstore.bundle`",
            "`sigstore_bundle_digest`",
            "`verification_roots_digest`",
            "bundle-first",
        ],
        "docs/260-release-authority-policy-and-key-management.md": [
            "`release.authority.policy`",
            "`release.publish.receipt`",
            "`identity_evidence`",
            "supplemental",
        ],
        "docs/487-keyless-identity-evidence-and-offline-verification-boundary.md": [
            "`publisher.identity.receipt`",
            "`release.authority.policy`",
            "`release.publish.receipt`",
            "`sigstore_bundle_digest`",
            "`verification_roots_digest`",
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

    print("Keyless identity authority contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
