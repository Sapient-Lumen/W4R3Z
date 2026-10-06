#!/usr/bin/env python3
"""Guardrail for the stratum-stack / runtime-composition contract.

This checker keeps DeriveBSD's explicit userland-composition boundary wired:
- `stratum.manifest` exposes source + ABI join keys
- `stratum.stack` carries one ABI anchor and the no-host-fallback rules
- `mount.view` binds the computed `stratum.stack` digest
- `runtime.manifest` example carries both `stratum_stack_digest` and `mount_view_digest`
- key docs explicitly mention the contract objects
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

    manifest_schema = load_json("spec/stratum.manifest.schema.json")
    for key in ("subject", "source", "abi"):
        if key not in manifest_schema.get("required", []):
            errors.append(f"spec/stratum.manifest.schema.json missing required {key}")
    abi_props = (((manifest_schema.get("properties") or {}).get("abi") or {}).get("properties") or {})
    for key in ("family", "loader_path", "default_library_paths", "execution_domains"):
        if key not in abi_props:
            errors.append(f"spec/stratum.manifest.schema.json missing abi.{key}")

    stack_schema = load_json("spec/stratum.stack.schema.json")
    for key in ("layers", "constraints", "evidence"):
        if key not in stack_schema.get("required", []):
            errors.append(f"spec/stratum.stack.schema.json missing required {key}")
    constraint_props = (((stack_schema.get("properties") or {}).get("constraints") or {}).get("properties") or {})
    for key in ("host_fallback", "loader_resolution", "foreign_abi_policy", "write_policy"):
        if key not in constraint_props:
            errors.append(f"spec/stratum.stack.schema.json missing constraints.{key}")

    view_schema = load_json("spec/mount.view.schema.json")
    for key in ("stratum_stack_digest", "layers", "constraints"):
        if key not in view_schema.get("required", []):
            errors.append(f"spec/mount.view.schema.json missing required {key}")

    runtime_schema = load_json("spec/runtime.manifest.schema.json")
    runtime_contract_props = (((runtime_schema.get("properties") or {}).get("runtime_contract") or {}).get("properties") or {})
    for key in ("stratum_stack_digest", "mount_view_digest"):
        if key not in runtime_contract_props:
            errors.append(f"spec/runtime.manifest.schema.json missing runtime_contract.{key}")

    manifest = load_json("spec/examples/stratum.manifest.json")
    stack = load_json("spec/examples/stratum.stack.json")
    view = load_json("spec/examples/mount.view.json")
    runtime = load_json("spec/examples/runtime.manifest.json")

    manifest_d = digest(manifest)
    stack_d = digest(stack)
    view_d = digest(view)

    layers = stack.get("layers") or []
    abi_anchor = [layer for layer in layers if layer.get("role") == "abi-anchor"]
    if len(abi_anchor) != 1:
        errors.append("spec/examples/stratum.stack.json must contain exactly one abi-anchor layer")
    elif abi_anchor[0].get("stratum_manifest_digest") != manifest_d:
        errors.append("spec/examples/stratum.stack.json abi-anchor stratum_manifest_digest != computed digest of spec/examples/stratum.manifest.json")

    constraints = stack.get("constraints") or {}
    if constraints.get("host_fallback") != "forbidden":
        errors.append("spec/examples/stratum.stack.json constraints.host_fallback must be 'forbidden'")
    if constraints.get("loader_resolution") != "abi-anchor-only":
        errors.append("spec/examples/stratum.stack.json constraints.loader_resolution must be 'abi-anchor-only'")

    if view.get("stratum_stack_digest") != stack_d:
        errors.append("spec/examples/mount.view.json stratum_stack_digest != computed digest of spec/examples/stratum.stack.json")

    runtime_contract = runtime.get("runtime_contract") or {}
    if runtime_contract.get("stratum_stack_digest") != stack_d:
        errors.append("spec/examples/runtime.manifest.json runtime_contract.stratum_stack_digest != computed digest of spec/examples/stratum.stack.json")
    if runtime_contract.get("mount_view_digest") != view_d:
        errors.append("spec/examples/runtime.manifest.json runtime_contract.mount_view_digest != computed digest of spec/examples/mount.view.json")

    doc_checks = {
        "docs/264-mount-namespaces-and-union-views.md": [
            "`mount.view`",
            "`stratum.stack`",
            "ABI anchor",
        ],
        "docs/295-strata-and-multi-origin-userlands.md": [
            "`stratum.manifest`",
            "`stratum.stack`",
            "`mount.view`",
        ],
        "docs/297-component-descriptors-and-compiled-runtime-manifests.md": [
            "`stratum.stack`",
            "`mount.view`",
            "`stratum_stack_digest`",
            "`mount_view_digest`",
        ],
        "docs/485-stratum-stack-and-runtime-composition-boundary.md": [
            "`stratum.manifest`",
            "`stratum.stack`",
            "`mount.view`",
            "`runtime.manifest`",
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

    print("Strata/runtime composition contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
