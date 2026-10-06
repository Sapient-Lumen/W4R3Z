#!/usr/bin/env python3
"""Guardrail for the temporary-authority grant / lease / use boundary.

This checker keeps DeriveBSD's generic lease contract wired:
- lane-specific grant / lease / session objects remain authoritative
- `lease.envelope` and `lease.issue.receipt` point at the authoritative object
- `lease.issue.receipt` and `lease.use.receipt` stay evidence-only
- later operation evidence is linked from `lease.use.receipt.related`
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

    issue_schema = load_json("spec/lease.issue.receipt.schema.json")
    issue_props = issue_schema.get("properties") or {}
    if issue_props.get("authority_semantics", {}).get("const") != "lease-issue-evidence-only":
        errors.append("spec/lease.issue.receipt.schema.json authority_semantics const must be lease-issue-evidence-only")
    if "authority_semantics" not in (issue_schema.get("required") or []):
        errors.append("spec/lease.issue.receipt.schema.json missing required authority_semantics")

    use_schema = load_json("spec/lease.use.receipt.schema.json")
    use_props = use_schema.get("properties") or {}
    if use_props.get("authority_semantics", {}).get("const") != "lease-use-evidence-only":
        errors.append("spec/lease.use.receipt.schema.json authority_semantics const must be lease-use-evidence-only")
    if "authority_semantics" not in (use_schema.get("required") or []):
        errors.append("spec/lease.use.receipt.schema.json missing required authority_semantics")

    env = load_json("spec/examples/lease.envelope.json")
    issue = load_json("spec/examples/lease.issue.receipt.json")
    use = load_json("spec/examples/lease.use.receipt.json")
    portal = load_json("spec/examples/portal.grant.json")
    export = load_json("spec/examples/export.receipt.json")

    portal_d = digest(portal)
    env_d = digest(env)
    export_d = digest(export)

    for rel, obj in (("spec/examples/lease.envelope.json", env), ("spec/examples/lease.issue.receipt.json", issue)):
        target = obj.get("target") or {}
        kind = str(target.get("kind", ""))
        if "receipt" in kind:
            errors.append(f"{rel} target.kind must point at an authoritative grant/lease/session object, not a receipt kind")
        if target.get("kind") != portal.get("kind"):
            errors.append(f"{rel} target.kind must match spec/examples/portal.grant.json kind in the canonical example")
        if target.get("digest") != portal_d:
            errors.append(f"{rel} target.digest != computed digest of spec/examples/portal.grant.json")

    if env.get("lease_id") != portal.get("lease_id"):
        errors.append("spec/examples/lease.envelope.json lease_id must match spec/examples/portal.grant.json lease_id")
    if issue.get("lease_id") != portal.get("lease_id"):
        errors.append("spec/examples/lease.issue.receipt.json lease_id must match spec/examples/portal.grant.json lease_id")
    if use.get("lease_id") != portal.get("lease_id"):
        errors.append("spec/examples/lease.use.receipt.json lease_id must match spec/examples/portal.grant.json lease_id")
    if export.get("lease_id") != portal.get("lease_id"):
        errors.append("spec/examples/export.receipt.json lease_id must match spec/examples/portal.grant.json lease_id")

    if issue.get("authority_semantics") != "lease-issue-evidence-only":
        errors.append("spec/examples/lease.issue.receipt.json authority_semantics must be lease-issue-evidence-only")
    if use.get("authority_semantics") != "lease-use-evidence-only":
        errors.append("spec/examples/lease.use.receipt.json authority_semantics must be lease-use-evidence-only")
    if issue.get("envelope_digest") != env_d:
        errors.append("spec/examples/lease.issue.receipt.json envelope_digest != computed digest of spec/examples/lease.envelope.json")

    related = use.get("related") or {}
    if related.get("kind") != export.get("kind"):
        errors.append("spec/examples/lease.use.receipt.json related.kind must match spec/examples/export.receipt.json kind in the canonical example")
    if related.get("digest") != export_d:
        errors.append("spec/examples/lease.use.receipt.json related.digest != computed digest of spec/examples/export.receipt.json")

    doc_checks = {
        "docs/249-lease-registry-and-cross-lane-revocation.md": ["`lease.envelope`", "`lease.issue.receipt`", "`lease.use.receipt`"],
        "docs/252-lease-envelope-and-cross-lane-joins.md": ["`lease.envelope`", "`lease.use.receipt.related`", "grant / lease / session"],
        "docs/449-lease-issue-and-use-receipts.md": ["`lease.issue.receipt`", "`lease.use.receipt`", "evidence-only"],
        "docs/493-temporary-authority-grant-lease-and-use-boundary.md": ["`lease.envelope`", "`lease.issue.receipt`", "`lease.use.receipt`", "`portal-grant`", "`export.receipt`"],
        "docs/229-evidence-spine-overview.md": ["`lease.issue.receipt`", "`lease.use.receipt`", "evidence-only"],
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

    print("Lease authority contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
