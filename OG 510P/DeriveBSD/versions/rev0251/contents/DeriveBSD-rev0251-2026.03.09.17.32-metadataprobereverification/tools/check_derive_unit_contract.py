#!/usr/bin/env python3
"""Guardrail for the derive.unit source / compile-receipt / runtime boundary.

This checker keeps DeriveBSD's component-runtime authoring story narrow and wired:
- `derive.unit` stays the reviewed human-authored source
- `derive.unit` must choose exactly one authored runtime-byte source (`rootfs` xor `strata`)
- `runtime.manifest` stays compiled launch authority and binds back to `derive.unit`
- `derive.unit.compile.receipt` stays evidence-only and joins the canonical example to compiled outputs
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

    unit_schema = load_json("spec/derive.unit.schema.json")
    one_of = unit_schema.get("oneOf") or []
    expected_one_of = [
        {"required": ["rootfs"], "not": {"required": ["strata"]}},
        {"required": ["strata"], "not": {"required": ["rootfs"]}},
    ]
    if one_of != expected_one_of:
        errors.append("spec/derive.unit.schema.json must keep the exact rootfs xor strata oneOf boundary")

    runtime_schema = load_json("spec/runtime.manifest.schema.json")
    if "runtime_contract" not in (runtime_schema.get("required") or []):
        errors.append("spec/runtime.manifest.schema.json must require runtime_contract")
    runtime_contract_props = (((runtime_schema.get("properties") or {}).get("runtime_contract") or {}).get("properties") or {})
    runtime_contract_required = (((runtime_schema.get("properties") or {}).get("runtime_contract") or {}).get("required") or [])
    for key in ("derive_unit_digest", "stratum_stack_digest", "mount_view_digest"):
        if key not in runtime_contract_props:
            errors.append(f"spec/runtime.manifest.schema.json missing runtime_contract.{key}")
        if key not in runtime_contract_required:
            errors.append(f"spec/runtime.manifest.schema.json runtime_contract must require {key}")

    receipt_schema = load_json("spec/derive.unit.compile.receipt.schema.json")
    props = receipt_schema.get("properties") or {}
    if props.get("authority_semantics", {}).get("const") != "derive-unit-compilation-evidence-only":
        errors.append("spec/derive.unit.compile.receipt.schema.json authority_semantics const must be derive-unit-compilation-evidence-only")
    if "authority_semantics" not in (receipt_schema.get("required") or []):
        errors.append("spec/derive.unit.compile.receipt.schema.json missing required authority_semantics")
    if props.get("runtime_source_mode", {}).get("enum") != ["rootfs", "strata"]:
        errors.append("spec/derive.unit.compile.receipt.schema.json runtime_source_mode enum drifted")

    unit = load_json("spec/examples/derive.unit.web.service.json")
    runtime = load_json("spec/examples/runtime.manifest.json")
    stack = load_json("spec/examples/stratum.stack.json")
    view = load_json("spec/examples/mount.view.json")
    preopen = load_json("spec/examples/preopen.map.json")
    devfs = load_json("spec/examples/devfs.view.plan.json")
    budget = load_json("spec/examples/authority.budget.json")
    budget_check = load_json("spec/examples/authority.budget.check.json")
    receipt = load_json("spec/examples/derive.unit.compile.receipt.json")

    unit_d = digest(unit)
    runtime_d = digest(runtime)
    stack_d = digest(stack)
    view_d = digest(view)
    preopen_d = digest(preopen)
    devfs_d = digest(devfs)
    budget_d = digest(budget)

    if ("rootfs" in unit) == ("strata" in unit):
        errors.append("spec/examples/derive.unit.web.service.json must use exactly one of rootfs or strata")
    if unit.get("id") != "web.nginx":
        errors.append("spec/examples/derive.unit.web.service.json canonical id must stay web.nginx")

    runtime_contract = runtime.get("runtime_contract") or {}
    if runtime_contract.get("derive_unit_digest") != unit_d:
        errors.append("spec/examples/runtime.manifest.json runtime_contract.derive_unit_digest != computed digest of spec/examples/derive.unit.web.service.json")
    if runtime_contract.get("stratum_stack_digest") != stack_d:
        errors.append("spec/examples/runtime.manifest.json runtime_contract.stratum_stack_digest != computed digest of spec/examples/stratum.stack.json")
    if runtime_contract.get("mount_view_digest") != view_d:
        errors.append("spec/examples/runtime.manifest.json runtime_contract.mount_view_digest != computed digest of spec/examples/mount.view.json")

    if (preopen.get("derived_from") or {}).get("derive_unit_digest") != unit_d:
        errors.append("spec/examples/preopen.map.json derived_from.derive_unit_digest != computed digest of spec/examples/derive.unit.web.service.json")
    if (devfs.get("inputs") or {}).get("derive_unit_digest") != unit_d:
        errors.append("spec/examples/devfs.view.plan.json inputs.derive_unit_digest != computed digest of spec/examples/derive.unit.web.service.json")
    if (budget.get("derived_from") or {}).get("derive_unit_digest") != unit_d:
        errors.append("spec/examples/authority.budget.json derived_from.derive_unit_digest != computed digest of spec/examples/derive.unit.web.service.json")
    if (budget_check.get("inputs") or {}).get("derive_unit_digest") != unit_d:
        errors.append("spec/examples/authority.budget.check.json inputs.derive_unit_digest != computed digest of spec/examples/derive.unit.web.service.json")

    if receipt.get("authority_semantics") != "derive-unit-compilation-evidence-only":
        errors.append("spec/examples/derive.unit.compile.receipt.json authority_semantics must be derive-unit-compilation-evidence-only")
    if (receipt.get("source_unit") or {}).get("digest") != unit_d:
        errors.append("spec/examples/derive.unit.compile.receipt.json source_unit.digest != computed digest of spec/examples/derive.unit.web.service.json")
    if (receipt.get("source_unit") or {}).get("example_path") != "spec/examples/derive.unit.web.service.json":
        errors.append("spec/examples/derive.unit.compile.receipt.json source_unit.example_path must be spec/examples/derive.unit.web.service.json")
    if receipt.get("runtime_source_mode") != "strata":
        errors.append("spec/examples/derive.unit.compile.receipt.json runtime_source_mode must be strata in the canonical example")

    expected_outputs = {
        "stratum.stack": stack_d,
        "mount.view": view_d,
        "preopen.map": preopen_d,
        "devfs-view-plan": devfs_d,
        "authority.budget": budget_d,
        "runtime.manifest": runtime_d,
    }
    compiled = {entry.get("kind"): entry for entry in (receipt.get("compiled_outputs") or [])}
    if set(compiled) != set(expected_outputs):
        errors.append("spec/examples/derive.unit.compile.receipt.json compiled_outputs kinds drifted")
    else:
        for kind, expected_digest in expected_outputs.items():
            if compiled[kind].get("digest") != expected_digest:
                errors.append(f"spec/examples/derive.unit.compile.receipt.json compiled_outputs[{kind}].digest != computed digest of canonical example")

    doc_checks = {
        "docs/297-component-descriptors-and-compiled-runtime-manifests.md": [
            "`derive.unit`",
            "`runtime.manifest`",
            "`derive.unit.compile.receipt`",
            "`rootfs` or `strata`",
        ],
        "docs/344-derive-unit-manifests-and-capability-routing.md": [
            "`derive.unit`",
            "`runtime.manifest`",
            "`derive.unit.compile.receipt`",
            "`rootfs`",
            "`strata`",
        ],
        "docs/33-runtime-manifest-schema.md": [
            "`derive.unit`",
            "`derive.unit.compile.receipt`",
            "`derive_unit_digest`",
        ],
        "docs/229-evidence-spine-overview.md": [
            "`derive.unit.compile.receipt`",
            "evidence-only",
            "`runtime.manifest`",
        ],
        "docs/500-derive-unit-source-compile-receipt-and-runtime-boundary.md": [
            "`derive.unit`",
            "`runtime.manifest`",
            "`derive.unit.compile.receipt`",
            "`rootfs`",
            "`strata`",
            "evidence-only",
        ],
        "adrs/ADR-0090-derive-unit-source-compile-receipt-and-runtime-boundary.md": [
            "derive.unit",
            "runtime.manifest",
            "derive.unit.compile.receipt",
            "rootfs",
            "strata",
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

    print("Derive-unit/runtime boundary contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
