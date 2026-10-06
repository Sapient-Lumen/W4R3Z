#!/usr/bin/env python3
"""Guardrail for the frontend-source / compile-receipt / canonical-IR boundary.

This checker keeps DeriveBSD's frontend-authoring story narrow and wired:
- canonical compiled JSON remains authoritative
- `frontend.compile.receipt` remains evidence-only
- the canonical example binds source/compiler evidence to a real compiled object digest
- the blessed HuJSON example stays hermetic and ambient-IO-free
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


def digest_json(obj: dict) -> str:
    return f"sha256:{hashlib.sha256(jcs_bytes(obj)).hexdigest()}"


def digest_bytes(rel: str) -> str:
    return f"sha256:{hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()}"


def main() -> int:
    errors: list[str] = []

    schema = load_json("spec/frontend.compile.receipt.schema.json")
    props = schema.get("properties") or {}
    if props.get("authority_semantics", {}).get("const") != "frontend-compilation-evidence-only":
        errors.append("spec/frontend.compile.receipt.schema.json authority_semantics const must be frontend-compilation-evidence-only")
    if "authority_semantics" not in (schema.get("required") or []):
        errors.append("spec/frontend.compile.receipt.schema.json missing required authority_semantics")
    if props.get("source_frontend", {}).get("enum") != ["json", "hujson", "cue", "pkl", "nickel", "starlark", "other"]:
        errors.append("spec/frontend.compile.receipt.schema.json source_frontend enum drifted")

    receipt = load_json("spec/examples/frontend.compile.receipt.json")
    trust = load_json("spec/examples/trust.policy.json")
    trust_digest = digest_json(trust)
    hujson_digest = digest_bytes("spec/examples/trust.policy.hujson")

    if receipt.get("authority_semantics") != "frontend-compilation-evidence-only":
        errors.append("spec/examples/frontend.compile.receipt.json authority_semantics must be frontend-compilation-evidence-only")
    if receipt.get("source_frontend") != "hujson":
        errors.append("spec/examples/frontend.compile.receipt.json canonical example must stay on the blessed hujson lane")

    sources = receipt.get("sources") or []
    if len(sources) != 1:
        errors.append("spec/examples/frontend.compile.receipt.json canonical example must have exactly one source")
    else:
        src = sources[0]
        if src.get("path") != "spec/examples/trust.policy.hujson":
            errors.append("spec/examples/frontend.compile.receipt.json source path must stay bound to spec/examples/trust.policy.hujson")
        if src.get("digest") != hujson_digest:
            errors.append("spec/examples/frontend.compile.receipt.json source digest != computed digest of spec/examples/trust.policy.hujson")

    compiled = receipt.get("compiled_object") or {}
    if compiled.get("kind") != "trust-policy":
        errors.append("spec/examples/frontend.compile.receipt.json compiled_object.kind must be trust-policy")
    if compiled.get("digest") != trust_digest:
        errors.append("spec/examples/frontend.compile.receipt.json compiled_object.digest != computed digest of spec/examples/trust.policy.json")
    if compiled.get("schema_path") != "spec/trust.policy.schema.json":
        errors.append("spec/examples/frontend.compile.receipt.json compiled_object.schema_path must be spec/trust.policy.schema.json")
    if compiled.get("example_path") != "spec/examples/trust.policy.json":
        errors.append("spec/examples/frontend.compile.receipt.json compiled_object.example_path must be spec/examples/trust.policy.json")

    compiler = receipt.get("compiler") or {}
    expected = {
        "sandbox_profile": "builtin-normalizer",
        "network_access": "forbidden",
        "module_imports": "none",
        "resource_reads": "none",
        "file_embedding": "forbidden",
        "external_readers": "forbidden",
    }
    for k, v in expected.items():
        if compiler.get(k) != v:
            errors.append(f"spec/examples/frontend.compile.receipt.json compiler.{k} must be {v!r} in the canonical hujson example")

    doc_checks = {
        "docs/79-derive-spec-frontends.md": ["`frontend.compile.receipt`", "adapter lane", "JSON", "HuJSON"],
        "docs/83-evaluator-minimalism.md": ["`frontend.compile.receipt`", "canonical Spec JSON"],
        "docs/149-human-policy-hujson-and-canonicalization.md": ["`frontend.compile.receipt`", "HuJSON", "canonical"],
        "docs/229-evidence-spine-overview.md": ["`frontend.compile.receipt`", "evidence-only"],
        "docs/495-frontend-source-compile-receipt-and-canonical-ir-boundary.md": ["`frontend.compile.receipt`", "JSON", "HuJSON", "adapter lanes"],
        "adrs/ADR-0085-frontend-source-compile-receipt-and-canonical-ir-boundary.md": ["frontend.compile.receipt", "HuJSON", "adapter lanes", "canonical JSON"],
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

    print("Frontend compile contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
