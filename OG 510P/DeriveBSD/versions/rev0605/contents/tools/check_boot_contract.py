#!/usr/bin/env python3
"""Guardrail for the boot-code admission contract.

This checker keeps the archive's boot closure, constrained override, and kmod
join surfaces wired together:
- boot.manifest carries required policy digests
- boot.attestation verified digests match the boot manifest example
- boot.override.receipt binds the boot.override.policy digest
- kmod.load.plan / receipt bind the boot.manifest digest
- kmod.load.receipt binds the computed plan digest
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from cube_digest_lib import canonical_digest, load_json as cube_load_json  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
EX = ROOT / "spec" / "examples"


def load_json(rel: str) -> dict:
    return cube_load_json(ROOT, rel)


def digest(obj: dict) -> str:
    return canonical_digest(obj)


def main() -> int:
    errors: list[str] = []

    boot_manifest_schema = load_json("spec/boot.manifest.schema.json")
    if "policy_digests" not in boot_manifest_schema.get("required", []):
        errors.append("spec/boot.manifest.schema.json missing required policy_digests")
    policy_props = (((boot_manifest_schema.get("properties") or {}).get("policy_digests") or {}).get("properties") or {})
    for key in ("kmod_policy_digest", "boot_override_policy_digest"):
        if key not in policy_props:
            errors.append(f"spec/boot.manifest.schema.json missing policy_digests.{key}")

    boot_att_schema = load_json("spec/boot.attestation.schema.json")
    verified = (boot_att_schema.get("properties") or {}).get("verified") or {}
    for key in ("kernel_digest", "kernel_modules_digest", "kmod_policy_digest", "boot_override_policy_digest"):
        if key not in ((verified.get("properties") or {})):
            errors.append(f"spec/boot.attestation.schema.json missing verified.{key}")

    for rel in ("spec/kmod.load.plan.schema.json", "spec/kmod.load.receipt.schema.json"):
        schema = load_json(rel)
        if "boot_manifest_digest" not in schema.get("required", []):
            errors.append(f"{rel} missing required boot_manifest_digest")

    boot_manifest = load_json("spec/examples/boot.manifest.json")
    boot_att = load_json("spec/examples/boot.attestation.json")
    kmod_policy = load_json("spec/examples/kmod.policy.json")
    boot_override_policy = load_json("spec/examples/boot.override.policy.json")
    boot_override_receipt = load_json("spec/examples/boot.override.receipt.json")
    kmod_plan = load_json("spec/examples/kmod.load.plan.json")
    kmod_receipt = load_json("spec/examples/kmod.load.receipt.json")

    boot_manifest_d = digest(boot_manifest)
    kmod_policy_d = digest(kmod_policy)
    boot_override_policy_d = digest(boot_override_policy)
    boot_override_receipt_d = digest(boot_override_receipt)
    kmod_plan_d = digest(kmod_plan)

    manifest_policy = boot_manifest.get("policy_digests") or {}
    if manifest_policy.get("kmod_policy_digest") != kmod_policy_d:
        errors.append("spec/examples/boot.manifest.json policy_digests.kmod_policy_digest != computed digest of spec/examples/kmod.policy.json")
    if manifest_policy.get("boot_override_policy_digest") != boot_override_policy_d:
        errors.append("spec/examples/boot.manifest.json policy_digests.boot_override_policy_digest != computed digest of spec/examples/boot.override.policy.json")

    att_subject = boot_att.get("subject") or {}
    if att_subject.get("boot_manifest_digest") != boot_manifest_d:
        errors.append("spec/examples/boot.attestation.json subject.boot_manifest_digest != computed digest of spec/examples/boot.manifest.json")

    verified_block = boot_att.get("verified") or {}
    components = {c.get("role"): c for c in (boot_manifest.get("components") or [])}
    expected_pairs = {
        "loader_digest": (components.get("loader") or {}).get("digest"),
        "kernel_digest": (components.get("kernel") or {}).get("digest"),
        "kernel_modules_digest": (components.get("kernel-modules") or {}).get("digest"),
        "kmod_policy_digest": kmod_policy_d,
        "boot_override_policy_digest": boot_override_policy_d,
        "override_receipt_digest": boot_override_receipt_d,
    }
    for key, expected in expected_pairs.items():
        if expected is None:
            errors.append(f"spec/examples/boot.manifest.json missing component needed for {key}")
            continue
        if verified_block.get(key) != expected:
            errors.append(f"spec/examples/boot.attestation.json verified.{key} != expected {expected}")

    if boot_override_receipt.get("policy_digest") != boot_override_policy_d:
        errors.append("spec/examples/boot.override.receipt.json policy_digest != computed digest of spec/examples/boot.override.policy.json")

    if kmod_plan.get("boot_manifest_digest") != boot_manifest_d:
        errors.append("spec/examples/kmod.load.plan.json boot_manifest_digest != computed digest of spec/examples/boot.manifest.json")
    if kmod_plan.get("policy_digest") != kmod_policy_d:
        errors.append("spec/examples/kmod.load.plan.json policy_digest != computed digest of spec/examples/kmod.policy.json")

    if kmod_receipt.get("boot_manifest_digest") != boot_manifest_d:
        errors.append("spec/examples/kmod.load.receipt.json boot_manifest_digest != computed digest of spec/examples/boot.manifest.json")
    if kmod_receipt.get("policy_digest") != kmod_policy_d:
        errors.append("spec/examples/kmod.load.receipt.json policy_digest != computed digest of spec/examples/kmod.policy.json")
    if kmod_receipt.get("plan_digest") != kmod_plan_d:
        errors.append("spec/examples/kmod.load.receipt.json plan_digest != computed digest of spec/examples/kmod.load.plan.json")

    doc_checks = {
        "docs/276-kernel-module-policy-and-loading-as-evidence.md": [
            "`boot_manifest_digest`",
            "`kmod.load.plan`",
            "`kmod.load.receipt`",
        ],
        "docs/277-loader-verification-and-boot-config-constraints.md": [
            "`boot.override.policy`",
            "`boot.override.receipt`",
            "`next-entry`",
            "`boot-mode`",
            "`console-profile`",
        ],
        "docs/482-boot-code-admission-and-constrained-overrides.md": [
            "`boot.manifest`",
            "`boot.override.policy`",
            "`boot.override.receipt`",
            "`boot.attestation`",
            "`kmod.load.plan`",
            "`kmod.load.receipt`",
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

    print("Boot-code admission contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
