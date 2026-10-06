#!/usr/bin/env python3
"""Guardrail for packet-capture normalization redaction evidence.

This checker keeps packet-capture normalization connected to the archive's
existing deterministic redaction lane rather than drifting back into tool or
filename folklore.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

ROOT = Path(__file__).resolve().parents[1]
BASE_URI = "https://derivebsd.local/spec/"


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def digest_obj(obj: dict) -> str:
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def build_registry(schema_paths: list[Path]) -> Registry:
    reg: Registry = Registry()
    for p in schema_paths:
        uri = BASE_URI + p.name
        schema = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(schema, dict) and "$id" not in schema:
            schema = dict(schema)
            schema["$id"] = uri
        reg = reg.with_resource(uri, Resource.from_contents(schema, default_specification=DRAFT202012))
    return reg


def validate(schema_rel: str, example_rel: str, reg: Registry) -> list[str]:
    schema = load_json(schema_rel)
    if "$id" not in schema:
        schema = dict(schema)
        schema["$id"] = BASE_URI + Path(schema_rel).name
    instance = load_json(example_rel)
    errs = sorted(Draft202012Validator(schema, registry=reg).iter_errors(instance), key=lambda e: list(e.absolute_path))
    out: list[str] = []
    for e in errs[:20]:
        path = "/".join(str(x) for x in e.absolute_path) or "<root>"
        out.append(f"{example_rel} invalid at {path}: {e.message}")
    if len(errs) > 20:
        out.append(f"{example_rel} invalid with {len(errs) - 20} additional errors")
    return out


def main() -> int:
    errors: list[str] = []

    transform_schema = load_json("spec/redaction.transform.packet-capture.schema.json")
    receipt_schema = load_json("spec/redaction.receipt.packet-capture.schema.json")
    import_receipt_schema = load_json("spec/content.import.packet-capture.receipt.schema.json")

    def has_ref(schema: dict, ref: str) -> bool:
        return any(isinstance(part, dict) and part.get("$ref") == ref for part in schema.get("allOf") or [])

    if not has_ref(transform_schema, "redaction.transform.schema.json"):
        errors.append("spec/redaction.transform.packet-capture.schema.json must specialize redaction.transform.schema.json")
    if not has_ref(receipt_schema, "redaction.receipt.schema.json"):
        errors.append("spec/redaction.receipt.packet-capture.schema.json must specialize redaction.receipt.schema.json")
    if "redaction_receipt_digest" not in json.dumps(import_receipt_schema):
        errors.append("spec/content.import.packet-capture.receipt.schema.json must expose typed redaction proof on the normalized output")

    schema_paths = sorted((ROOT / "spec").glob("*.schema.json"))
    reg = build_registry(schema_paths)
    errors.extend(validate("spec/redaction.transform.packet-capture.schema.json", "spec/examples/redaction.transform.packet-capture.json", reg))
    errors.extend(validate("spec/redaction.receipt.packet-capture.schema.json", "spec/examples/redaction.receipt.packet-capture.json", reg))
    errors.extend(validate("spec/content.import.packet-capture.receipt.schema.json", "spec/examples/content.import.packet-capture.receipt.json", reg))

    transform = load_json("spec/examples/redaction.transform.packet-capture.json")
    receipt = load_json("spec/examples/redaction.receipt.packet-capture.json")
    import_receipt = load_json("spec/examples/content.import.packet-capture.receipt.json")

    if transform.get("kind") != "redaction-transform":
        errors.append("packet-capture redaction transform must keep kind = redaction-transform")
    if receipt.get("kind") != "redaction-receipt":
        errors.append("packet-capture redaction receipt must keep kind = redaction-receipt")

    applies = set(transform.get("applies_to") or [])
    if "pcap" not in applies:
        errors.append("packet-capture redaction transform must apply to pcap")

    policy = transform.get("policy") or {}
    allow = set(policy.get("allow_attributes") or [])
    deny = set(policy.get("deny_attributes") or [])
    if "packet-records" not in allow:
        errors.append("packet-capture redaction transform must allow packet-records")
    for item in {"capture-comment", "packet-comment", "name-resolution", "decryption-secrets"}:
        if item not in deny:
            errors.append(f"packet-capture redaction transform missing deny attribute: {item}")

    summary = receipt.get("summary") or {}
    if summary.get("output_metadata_posture") != "packet-records-only":
        errors.append("packet-capture redaction receipt must end at output_metadata_posture = packet-records-only")
    if summary.get("promotion_verdict") not in {"ordinary-review-export-eligible", "summary-only"}:
        errors.append("packet-capture redaction receipt must declare promotion_verdict")

    outputs = import_receipt.get("outputs") or []
    norm_outputs = [o for o in outputs if (o.get("labels") or {}).get("class") == "packet-capture-normalized"]
    if not norm_outputs:
        errors.append("packet-capture import receipt must include a normalized output")
    else:
        labels = norm_outputs[0].get("labels") or {}
        if norm_outputs[0].get("digest") != receipt.get("output_digest"):
            errors.append("packet-capture normalized output digest must match packet-capture redaction receipt output_digest")
        if labels.get("redaction_transform_digest") != receipt.get("transform_digest"):
            errors.append("packet-capture normalized output labels.redaction_transform_digest must match packet-capture redaction receipt transform_digest")
        if labels.get("redaction_receipt_digest") != digest_obj(receipt):
            errors.append("packet-capture normalized output labels.redaction_receipt_digest must carry the typed packet-capture redaction receipt digest")
        if labels.get("promotion_verdict") != summary.get("promotion_verdict"):
            errors.append("packet-capture normalized output labels.promotion_verdict must match the packet-capture redaction receipt")
        if labels.get("metadata_posture") != "packet-records-only":
            errors.append("packet-capture normalized output labels.metadata_posture must remain packet-records-only")

    doc_checks = {
        "docs/195-deterministic-redaction-transforms.md": [
            "Packet-capture normalization",
            "`spec/redaction.transform.packet-capture.schema.json`",
            "`spec/redaction.receipt.packet-capture.schema.json`",
        ],
        "docs/511-packet-capture-strong-artifact-safe-open-intake-and-normalize-boundary.md": [
            "redaction evidence",
            "`docs/512-packet-capture-normalization-redaction-receipt-boundary.md`",
        ],
        "docs/512-packet-capture-normalization-redaction-receipt-boundary.md": [
            "redaction-transform",
            "redaction-receipt",
            "typed normalized-output labels",
        ],
        "docs/251-export-policies-and-support-bundle-portal.md": [
            "redaction-receipt",
            "ordinary-review-export-eligible",
        ],
        "docs/99-llm-runbook.md": [
            "tools/check_packet_capture_normalization_contract.py",
            "redaction-receipt",
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

    print("Packet-capture normalization redaction contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
