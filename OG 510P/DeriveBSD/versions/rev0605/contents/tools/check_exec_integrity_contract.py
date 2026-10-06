#!/usr/bin/env python3
"""Guardrail for the exec-integrity authority boundary.

This checker keeps DeriveBSD's execution-integrity contract wired:
- `exec.integrity.plan` / `exec.integrity.receipt` bind runtime-composition digests
- examples line up across policy → plan → receipt and runtime composition
- the drift surface is `exec.verify.policy.diff`, but it compares authoritative policy objects
- change sets use `apply-exec-integrity`
- key docs mention the authority boundary explicitly
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

    plan_schema = load_json("spec/exec.integrity.plan.schema.json")
    for key in ("runtime_contract", "resolution"):
        if key not in plan_schema.get("required", []):
            errors.append(f"spec/exec.integrity.plan.schema.json missing required {key}")
    plan_runtime_props = (((plan_schema.get("properties") or {}).get("runtime_contract") or {}).get("properties") or {})
    for key in ("runtime_manifest_digest", "stratum_stack_digest", "mount_view_digest"):
        if key not in plan_runtime_props:
            errors.append(f"spec/exec.integrity.plan.schema.json missing runtime_contract.{key}")

    receipt_schema = load_json("spec/exec.integrity.receipt.schema.json")
    for key in ("runtime_contract", "resolution", "plan_digest"):
        if key not in receipt_schema.get("required", []):
            errors.append(f"spec/exec.integrity.receipt.schema.json missing required {key}")
    receipt_runtime_props = (((receipt_schema.get("properties") or {}).get("runtime_contract") or {}).get("properties") or {})
    for key in ("runtime_manifest_digest", "stratum_stack_digest", "mount_view_digest"):
        if key not in receipt_runtime_props:
            errors.append(f"spec/exec.integrity.receipt.schema.json missing runtime_contract.{key}")

    diff_schema = load_json("spec/exec.verify.policy.diff.schema.json")
    scope_change_props = (((diff_schema.get("$defs") or {}).get("scope_change") or {}).get("properties") or {})
    for key in ("allowed_sources_added", "allowed_sources_removed", "exceptions_added"):
        if key not in scope_change_props:
            errors.append(f"spec/exec.verify.policy.diff.schema.json missing $defs.scope_change.{key}")

    change_set_schema = load_json("spec/change.set.schema.json")
    ops = ((((change_set_schema.get("properties") or {}).get("steps") or {}).get("items") or {}).get("properties") or {}).get("op", {}).get("enum", [])
    if "apply-exec-integrity" not in ops:
        errors.append("spec/change.set.schema.json missing apply-exec-integrity op")
    if "apply-exec-verify" in ops:
        errors.append("spec/change.set.schema.json should not keep apply-exec-verify in the canonical op enum")

    policy = load_json("spec/examples/exec.integrity.policy.json")
    plan = load_json("spec/examples/exec.integrity.plan.json")
    receipt = load_json("spec/examples/exec.integrity.receipt.json")
    runtime = load_json("spec/examples/runtime.manifest.json")
    stack = load_json("spec/examples/stratum.stack.json")
    view = load_json("spec/examples/mount.view.json")
    change_set = load_json("spec/examples/change.set.json")

    policy_d = digest(policy)
    plan_d = digest(plan)
    runtime_d = digest(runtime)
    stack_d = digest(stack)
    view_d = digest(view)

    if plan.get("policy_digest") != policy_d:
        errors.append("spec/examples/exec.integrity.plan.json policy_digest != computed digest of spec/examples/exec.integrity.policy.json")

    runtime_contract = plan.get("runtime_contract") or {}
    if runtime_contract.get("runtime_manifest_digest") != runtime_d:
        errors.append("spec/examples/exec.integrity.plan.json runtime_contract.runtime_manifest_digest != computed digest of spec/examples/runtime.manifest.json")
    if runtime_contract.get("stratum_stack_digest") != stack_d:
        errors.append("spec/examples/exec.integrity.plan.json runtime_contract.stratum_stack_digest != computed digest of spec/examples/stratum.stack.json")
    if runtime_contract.get("mount_view_digest") != view_d:
        errors.append("spec/examples/exec.integrity.plan.json runtime_contract.mount_view_digest != computed digest of spec/examples/mount.view.json")

    receipt_runtime = receipt.get("runtime_contract") or {}
    if receipt.get("policy_digest") != policy_d:
        errors.append("spec/examples/exec.integrity.receipt.json policy_digest != computed digest of spec/examples/exec.integrity.policy.json")
    if receipt.get("plan_digest") != plan_d:
        errors.append("spec/examples/exec.integrity.receipt.json plan_digest != computed digest of spec/examples/exec.integrity.plan.json")
    if receipt_runtime.get("runtime_manifest_digest") != runtime_d:
        errors.append("spec/examples/exec.integrity.receipt.json runtime_contract.runtime_manifest_digest != computed digest of spec/examples/runtime.manifest.json")
    if receipt_runtime.get("stratum_stack_digest") != stack_d:
        errors.append("spec/examples/exec.integrity.receipt.json runtime_contract.stratum_stack_digest != computed digest of spec/examples/stratum.stack.json")
    if receipt_runtime.get("mount_view_digest") != view_d:
        errors.append("spec/examples/exec.integrity.receipt.json runtime_contract.mount_view_digest != computed digest of spec/examples/mount.view.json")

    resolution = plan.get("resolution") or {}
    if resolution.get("loaders") != "abi-anchor-only":
        errors.append("spec/examples/exec.integrity.plan.json resolution.loaders must be 'abi-anchor-only'")
    if resolution.get("interpreters") != "resolve-within-mount-view":
        errors.append("spec/examples/exec.integrity.plan.json resolution.interpreters must be 'resolve-within-mount-view'")
    if receipt.get("resolution") != resolution:
        errors.append("spec/examples/exec.integrity.receipt.json resolution must match spec/examples/exec.integrity.plan.json resolution")

    found_apply = False
    for step in change_set.get("steps") or []:
        if step.get("op") == "apply-exec-integrity":
            found_apply = True
            refs = step.get("refs") or []
            if not any(ref.get("kind") == "exec.integrity.policy" for ref in refs):
                errors.append("spec/examples/change.set.json apply-exec-integrity step must reference kind exec.integrity.policy")
    if not found_apply:
        errors.append("spec/examples/change.set.json missing apply-exec-integrity step")

    doc_checks = {
        "docs/289-exec-integrity-policy-and-verified-execution.md": [
            "`exec.integrity.policy`",
            "`exec.integrity.plan`",
            "`exec.integrity.receipt`",
            "`mount.view`",
            "ABI-anchor-only",
        ],
        "docs/233-verified-execution-as-evidence.md": [
            "`exec.integrity.policy`",
            "`exec.integrity.receipt`",
            "`exec-verify-snapshot`",
            "`exec-verify-event`",
        ],
        "docs/442-exec-verify-policy-diff-as-review-surface.md": [
            "`exec.verify.policy.diff`",
            "`exec.integrity.policy`",
            "`exec.integrity.receipt`",
        ],
        "docs/486-exec-integrity-authority-and-verified-execution-boundary.md": [
            "`exec.integrity.policy`",
            "`exec.integrity.plan`",
            "`exec.integrity.receipt`",
            "`exec-verify-snapshot`",
            "`exec.verify.policy.diff`",
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

    print("Exec-integrity authority contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
