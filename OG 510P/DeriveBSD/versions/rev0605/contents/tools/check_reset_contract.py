#!/usr/bin/env python3
"""Guardrail for the destructive-reprovision / reset-authority contract.

This checker keeps the archive's destructive reprovision contract wired:
- reset.authorization carries target + requested digests + authority + retention
- reset.receipt binds the computed reset.authorization digest
- examples join back to disk.layout.plan and disk.layout.receipt digests
- key docs mention the contract pieces so discovery does not drift
- product profiles keep the stable destructive_reprovision defaults
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from cube_digest_lib import canonical_digest, load_json as load_json_strict

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    return load_json_strict(ROOT, rel)


def digest(obj: dict) -> str:
    return canonical_digest(obj)


def main() -> int:
    errors: list[str] = []

    auth_schema = load_json("spec/reset.authorization.schema.json")
    for key in ("target", "requested", "destructive_scope", "retention", "authority"):
        if key not in auth_schema.get("required", []):
            errors.append(f"spec/reset.authorization.schema.json missing required {key}")
    requested_props = (((auth_schema.get("properties") or {}).get("requested") or {}).get("properties") or {})
    for key in ("disk_layout_plan_digest", "install_bundle_digest"):
        if key not in requested_props:
            errors.append(f"spec/reset.authorization.schema.json missing requested.{key}")

    receipt_schema = load_json("spec/reset.receipt.schema.json")
    for key in ("authorization", "target", "requested", "observed_evidence", "outcome"):
        if key not in receipt_schema.get("required", []):
            errors.append(f"spec/reset.receipt.schema.json missing required {key}")

    auth = load_json("spec/examples/reset.authorization.json")
    receipt = load_json("spec/examples/reset.receipt.json")
    disk_plan = load_json("spec/examples/disk.layout.plan.json")
    disk_receipt = load_json("spec/examples/disk.layout.receipt.json")

    auth_d = digest(auth)
    disk_plan_d = digest(disk_plan)
    disk_receipt_d = digest(disk_receipt)

    requested = auth.get("requested") or {}
    if requested.get("disk_layout_plan_digest") != disk_plan_d:
        errors.append("spec/examples/reset.authorization.json requested.disk_layout_plan_digest != computed digest of spec/examples/disk.layout.plan.json")

    auth_target = auth.get("target") or {}
    receipt_target = receipt.get("target") or {}
    if receipt_target.get("serial") != auth_target.get("serial"):
        errors.append("spec/examples/reset.receipt.json target.serial must match reset.authorization target.serial")
    if not receipt_target.get("matched_selector"):
        errors.append("spec/examples/reset.receipt.json target.matched_selector must be true in the success example")

    auth_required = set((auth.get("authority") or {}).get("required_evidence") or [])
    observed = receipt.get("observed_evidence") or []
    observed_kinds = {e.get("kind") for e in observed if e.get("outcome") == "observed"}
    missing = sorted(auth_required - observed_kinds)
    if missing:
        errors.append(f"spec/examples/reset.receipt.json missing observed_evidence for required kinds: {', '.join(missing)}")

    if (receipt.get("authorization") or {}).get("digest") != auth_d:
        errors.append("spec/examples/reset.receipt.json authorization.digest != computed digest of spec/examples/reset.authorization.json")

    requested_r = receipt.get("requested") or {}
    if requested_r.get("disk_layout_plan_digest") != disk_plan_d:
        errors.append("spec/examples/reset.receipt.json requested.disk_layout_plan_digest != computed digest of spec/examples/disk.layout.plan.json")
    if requested_r.get("install_bundle_digest") != requested.get("install_bundle_digest"):
        errors.append("spec/examples/reset.receipt.json requested.install_bundle_digest must match reset.authorization install_bundle_digest")

    resulting = receipt.get("resulting_receipts") or {}
    if resulting.get("disk_layout_receipt_digest") != disk_receipt_d:
        errors.append("spec/examples/reset.receipt.json resulting_receipts.disk_layout_receipt_digest != computed digest of spec/examples/disk.layout.receipt.json")

    profiles = load_json("spec/examples/product.profiles.json")
    expected_defaults = {
        "fleet_host": "target-bound-digest-breakglass-or-maintenance",
        "workstation": "trusted-ui-target-confirm-digest-bound",
        "general_os": "explicit-admin-or-trusted-ui-digest-bound",
        "appliance_factory": "offline-signed-authority-plus-reset-marker",
    }
    for pid, expected in expected_defaults.items():
        got = (((profiles.get("profiles") or {}).get(pid) or {}).get("defaults") or {}).get("destructive_reprovision")
        if got != expected:
            errors.append(f"spec/examples/product.profiles.json {pid}.defaults.destructive_reprovision expected {expected!r}, found {got!r}")

    doc_checks = {
        "docs/309-installation-and-recovery-as-derived-operations.md": [
            "`reset.authorization`",
            "`reset.receipt`",
        ],
        "docs/310-disk-layout-plans-and-receipts.md": [
            "`reset.authorization`",
            "`reset.receipt`",
        ],
        "docs/483-destructive-reprovisioning-and-reset-authority.md": [
            "`reset.authorization`",
            "`reset.receipt`",
            "`disk.layout.plan`",
            "`disk.layout.receipt`",
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

    print("Reset-authority contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
