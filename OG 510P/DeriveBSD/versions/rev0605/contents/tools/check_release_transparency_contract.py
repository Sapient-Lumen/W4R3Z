#!/usr/bin/env python3
"""Guardrail for the release-transparency authority boundary.

This checker keeps DeriveBSD's release transparency contract wired:
- `release.publish.receipt` stays authoritative
- `release.transparency.entry`, `log.checkpoint.receipt`, and `transparency.monitor.snapshot`
  stay evidence-only
- examples line up across authority policy → transparency entry → checkpoint receipt →
  monitor snapshot → publish receipt
- key docs explicitly mention the boundary
"""
from __future__ import annotations

from pathlib import Path

from cube_digest_lib import canonical_digest, load_json as cube_load_json

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    return cube_load_json(ROOT, rel)


def digest(obj: dict) -> str:
    return canonical_digest(obj)


def main() -> int:
    errors: list[str] = []

    entry_schema = load_json("spec/release.transparency.entry.schema.json")
    if "authority_policy_digest" not in entry_schema.get("required", []):
        errors.append("spec/release.transparency.entry.schema.json missing required authority_policy_digest")
    if "policy_digest" in (entry_schema.get("properties") or {}):
        errors.append("spec/release.transparency.entry.schema.json must not expose generic policy_digest")
    entry_props = entry_schema.get("properties") or {}
    if entry_props.get("authority_semantics", {}).get("const") != "publication-evidence-only":
        errors.append("spec/release.transparency.entry.schema.json authority_semantics must const to publication-evidence-only")
    for key in ("authority_semantics", "checkpoint_receipt_digest"):
        if key not in entry_props:
            errors.append(f"spec/release.transparency.entry.schema.json missing property {key}")

    checkpoint_schema = load_json("spec/log.checkpoint.receipt.schema.json")
    checkpoint_props = checkpoint_schema.get("properties") or {}
    if checkpoint_props.get("authority_semantics", {}).get("const") != "checkpoint-evidence-only":
        errors.append("spec/log.checkpoint.receipt.schema.json authority_semantics must const to checkpoint-evidence-only")

    snapshot_schema = load_json("spec/transparency.monitor.snapshot.schema.json")
    for key in ("authority_semantics", "summary_status", "checkpoint_receipt_digest"):
        if key not in (snapshot_schema.get("properties") or {}):
            errors.append(f"spec/transparency.monitor.snapshot.schema.json missing property {key}")
    if snapshot_schema.get("properties", {}).get("authority_semantics", {}).get("const") != "monitor-state-evidence-only":
        errors.append("spec/transparency.monitor.snapshot.schema.json authority_semantics must const to monitor-state-evidence-only")

    authority_schema = load_json("spec/release.authority.policy.schema.json")
    transparency_props = (((authority_schema.get("properties") or {}).get("transparency") or {}).get("properties") or {})
    if "require_checkpoint_receipt" not in transparency_props:
        errors.append("spec/release.authority.policy.schema.json missing transparency.require_checkpoint_receipt")

    publish_schema = load_json("spec/release.publish.receipt.schema.json")
    publish_props = publish_schema.get("properties") or {}
    if "transparency_verification" not in publish_props:
        errors.append("spec/release.publish.receipt.schema.json missing transparency_verification")
    for legacy in ("release_transparency_entry_digest", "monitor_snapshots"):
        if legacy in publish_props:
            errors.append(f"spec/release.publish.receipt.schema.json must not expose legacy top-level {legacy}")
    tv_props = ((publish_props.get("transparency_verification") or {}).get("properties") or {})
    for key in ("decision", "release_transparency_entry_digest", "checkpoint_receipt_digest", "monitor_snapshot_digests", "monitor_summary_status"):
        if key not in tv_props:
            errors.append(f"spec/release.publish.receipt.schema.json missing transparency_verification.{key}")

    authority = load_json("spec/examples/release.authority.policy.json")
    checkpoint = load_json("spec/examples/log.checkpoint.receipt.json")
    entry = load_json("spec/examples/release.transparency.entry.json")
    snapshot = load_json("spec/examples/transparency.monitor.snapshot.json")
    publish = load_json("spec/examples/release.publish.receipt.json")

    authority_d = digest(authority)
    checkpoint_d = digest(checkpoint)
    entry_d = digest(entry)
    snapshot_d = digest(snapshot)

    if entry.get("authority_semantics") != "publication-evidence-only":
        errors.append("spec/examples/release.transparency.entry.json authority_semantics must be publication-evidence-only")
    if entry.get("authority_policy_digest") != authority_d:
        errors.append("spec/examples/release.transparency.entry.json authority_policy_digest != computed digest of spec/examples/release.authority.policy.json")
    if entry.get("checkpoint_receipt_digest") != checkpoint_d:
        errors.append("spec/examples/release.transparency.entry.json checkpoint_receipt_digest != computed digest of spec/examples/log.checkpoint.receipt.json")
    if "policy_digest" in entry:
        errors.append("spec/examples/release.transparency.entry.json must not include generic policy_digest")

    if checkpoint.get("authority_semantics") != "checkpoint-evidence-only":
        errors.append("spec/examples/log.checkpoint.receipt.json authority_semantics must be checkpoint-evidence-only")

    if snapshot.get("authority_semantics") != "monitor-state-evidence-only":
        errors.append("spec/examples/transparency.monitor.snapshot.json authority_semantics must be monitor-state-evidence-only")
    if snapshot.get("checkpoint_receipt_digest") != checkpoint_d:
        errors.append("spec/examples/transparency.monitor.snapshot.json checkpoint_receipt_digest != computed digest of spec/examples/log.checkpoint.receipt.json")
    if snapshot.get("summary_status") != "clean":
        errors.append("spec/examples/transparency.monitor.snapshot.json summary_status must be clean")

    transparency = authority.get("transparency") or {}
    if not transparency.get("require_checkpoint_receipt"):
        errors.append("spec/examples/release.authority.policy.json transparency.require_checkpoint_receipt must be true")
    monitoring = authority.get("monitoring") or {}
    if not monitoring.get("require_monitor_clean"):
        errors.append("spec/examples/release.authority.policy.json monitoring.require_monitor_clean must be true")

    if publish.get("authority_policy_digest") != authority_d:
        errors.append("spec/examples/release.publish.receipt.json authority_policy_digest != computed digest of spec/examples/release.authority.policy.json")
    tv = publish.get("transparency_verification") or {}
    if tv.get("decision") != "accepted":
        errors.append("spec/examples/release.publish.receipt.json transparency_verification.decision must be accepted")
    if tv.get("release_transparency_entry_digest") != entry_d:
        errors.append("spec/examples/release.publish.receipt.json transparency_verification.release_transparency_entry_digest != computed digest of spec/examples/release.transparency.entry.json")
    if tv.get("checkpoint_receipt_digest") != checkpoint_d:
        errors.append("spec/examples/release.publish.receipt.json transparency_verification.checkpoint_receipt_digest != computed digest of spec/examples/log.checkpoint.receipt.json")
    if snapshot_d not in (tv.get("monitor_snapshot_digests") or []):
        errors.append("spec/examples/release.publish.receipt.json transparency_verification.monitor_snapshot_digests must include computed digest of spec/examples/transparency.monitor.snapshot.json")
    if tv.get("monitor_summary_status") != "clean":
        errors.append("spec/examples/release.publish.receipt.json transparency_verification.monitor_summary_status must be clean")

    doc_checks = {
        "docs/257-release-capsules-and-transparency.md": [
            "`release.publish.receipt`",
            "`release.transparency.entry`",
            "`authority_policy_digest`",
            "`transparency_verification`",
        ],
        "docs/259-transparency-monitors-and-witness-gossip.md": [
            "`transparency.monitor.snapshot`",
            "`summary_status`",
            "`release.publish.receipt`",
            "`transparency_verification`",
        ],
        "docs/260-release-authority-policy-and-key-management.md": [
            "`release.authority.policy`",
            "`release.publish.receipt`",
            "`transparency_verification`",
            "supplemental",
        ],
        "docs/488-release-transparency-evidence-and-monitor-gate-boundary.md": [
            "`release.publish.receipt`",
            "`release.transparency.entry`",
            "`log.checkpoint.receipt`",
            "`transparency.monitor.snapshot`",
            "`transparency_verification`",
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

    print("Release transparency authority contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
