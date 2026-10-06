#!/usr/bin/env python3
"""Validate r529 post-detach export-bundle deletion receipts.

r528 made export access auditable and required a deletion receipt. r529 makes
that terminal deletion/revocation step typed: the broker must bind the export
access receipt, prove bounded retention/expiry or explicit revocation, terminal
managed-copy/remote-object posture, support-safe visibility, and monotonic CAS
ledger advancement without claiming unmanaged offline-copy erasure.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from cube_digest_lib import file_json_digest, load_json

ROOT = Path(__file__).resolve().parents[1]
VERSION = "2026-05-30r529"
SCHEMA = "spec/removable.media.local.post_detach.export.bundle.deletion.receipt.schema.json"
EXAMPLE = "spec/examples/removable.media.local.post_detach.export.bundle.deletion.receipt.json"
INVALID_DIR = "spec/examples/invalid/removable-media/post-detach-export-bundle-deletion-receipt"

SOURCE_BINDINGS = {
    "export_bundle_access_receipt_computed_digest": "spec/examples/removable.media.local.post_detach.export.bundle.access.receipt.json",
    "export_bundle_computed_digest": "spec/examples/removable.media.local.post_detach.export.bundle.json",
    "revocation_tombstone_computed_digest": "spec/examples/removable.media.local.post_detach.revocation.tombstone.json",
    "support_projection_computed_digest": "spec/examples/removable.media.local.post_detach.support.projection.json",
}

EXPECTED_INVALIDS = [
    "deletion-before-expiry-without-revocation.json",
    "deletion-ledger-not-advanced.json",
    "local-managed-copy-left-live.json",
    "missing-export-access-binding.json",
    "not-terminal-after-deletion.json",
    "offline-erasure-claimed.json",
    "raw-locator-visible.json",
    "remote-object-left-live.json",
    "stale-export-access-binding.json",
    "unbounded-retention.json",
]

REQUIRED_DOC_TOKENS = {
    "CHANGELOG.md": [VERSION, "export.bundle.deletion.receipt", "check_removable_media_local_post_detach_export_bundle_deletion_receipt.py"],
    "README.md": [VERSION, "export-bundle-deletion", "revocation-tombstone-schema-split"],
    "docs/00-index.md": [VERSION, "docs/current/removable-media-post-detach-export-bundle-deletion.md"],
    "docs/98-archive-hygiene.md": ["check_removable_media_local_post_detach_export_bundle_deletion_receipt.py"],
    "docs/99-llm-runbook.md": ["check_removable_media_local_post_detach_export_bundle_deletion_receipt.py"],
    "docs/110-juicy-os-lessons.md": ["r529 removable-media post-detach export bundle deletion"],
    "docs/784-removable-media-local-fallback-post-detach-export-bundle-deletion-and-revocation-tombstone-schema-split.md": [
        "removable.media.local.post_detach.export.bundle.deletion.receipt",
        "post-detach-export-bundle-deletion-positive-and-negative-fixture-guarded",
        "post-detach-revocation-tombstone-generic-runtime-schema-plus-exact-fixture-split",
    ],
    "docs/current/removable-media-post-detach-export-bundle-deletion.md": [
        "terminal deletion",
        "bounded retention",
        "export access receipt",
        "offline-copy erasure is not claimed",
    ],
}


def fail(msg: str) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(1)


def validation_errors(schema_rel: str, obj: Any) -> list[str]:
    schema = load_json(ROOT, schema_rel)
    validator = Draft202012Validator(schema)
    return [e.message for e in sorted(validator.iter_errors(obj), key=lambda e: list(e.absolute_path))]


def parse_z(ts: str) -> datetime:
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    return datetime.fromisoformat(ts)


def semantic_errors(obj: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if obj.get("generated_for_version") != VERSION:
        errors.append("export-bundle deletion receipt version mismatch")
    lane = obj.get("lane", {})
    if lane.get("family") != "removable-media-local-fallback" or lane.get("phase") != "post-detach":
        errors.append("lane must remain removable-media-local-fallback/post-detach")

    bindings = obj.get("source_bindings", {})
    if bindings.get("canonical_digest_rule") != "json-sort-keys-compact-utf8-sha256":
        errors.append("canonical digest rule mismatch")
    for key, rel in SOURCE_BINDINGS.items():
        if bindings.get(key) != file_json_digest(ROOT, rel):
            errors.append(f"{key} does not match {rel}")

    export_access = load_json(ROOT, "spec/examples/removable.media.local.post_detach.export.bundle.access.receipt.json")
    support = load_json(ROOT, "spec/examples/removable.media.local.post_detach.support.projection.json")

    access = obj.get("export_access_binding", {})
    if access.get("export_access_receipt_id") != export_access.get("access_receipt_id"):
        errors.append("export access receipt id binding is stale")
    if access.get("export_access_receipt_digest") != file_json_digest(ROOT, "spec/examples/removable.media.local.post_detach.export.bundle.access.receipt.json"):
        errors.append("export access receipt digest binding is stale")
    if access.get("recipient_digest") != export_access.get("export_request", {}).get("recipient_digest"):
        errors.append("recipient digest must match export access request")
    if access.get("export_sequence") != export_access.get("export_ledger", {}).get("export_sequence"):
        errors.append("export sequence must match export access ledger")
    if access.get("new_export_requires_new_approval") is not True:
        errors.append("new export must require new approval after deletion")

    trigger = obj.get("deletion_trigger", {})
    if trigger.get("trigger_kind") == "retention-expired":
        try:
            if parse_z(trigger.get("deletion_observed_at", "")) < parse_z(trigger.get("retention_expires_at", "")):
                errors.append("retention-expired deletion must be observed at or after retention expiry")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"invalid deletion trigger timestamp: {exc}")
    if trigger.get("early_revocation_allowed") is not True:
        errors.append("explicit revocation path must stay available before retention expiry")

    actions = obj.get("deletion_actions", {})
    if actions.get("local_managed_copy") != "deleted-or-quarantined-and-terminal":
        errors.append("local managed copy must be terminal")
    if actions.get("remote_object") != "revoked-or-deleted-if-present-and-receipted":
        errors.append("remote object must be revoked/deleted if present")
    if actions.get("live_locator") != "absent-or-terminal-after-deletion":
        errors.append("live locator must be absent or terminal after deletion")
    if actions.get("raw_locator_visible") is not False:
        errors.append("raw locator must not be visible")
    if actions.get("offline_copy_claim") != "not-claimed-erased-only-future-authority-denied":
        errors.append("deletion receipt must not claim unmanaged offline-copy erasure")

    retention = obj.get("retention_proof", {})
    if retention.get("retention_was_bounded") is not True or retention.get("unbounded_retention_allowed") is not False:
        errors.append("export deletion must prove bounded retention and reject unbounded retention")
    if retention.get("deletion_after_expiry_or_revocation") is not True:
        errors.append("deletion must be after expiry or explicit revocation")
    if retention.get("deletion_receipt_visible") is not True:
        errors.append("deletion receipt must be visible as evidence")

    support_projection = obj.get("support_projection", {})
    if support_projection.get("visibility") != support.get("visibility"):
        errors.append("support visibility must match support projection")
    for field in [
        "raw_payload_visible",
        "raw_path_visible",
        "filename_visible",
        "device_identifier_visible",
        "host_identity_visible",
        "body_or_full_text_visible",
        "secret_material_visible",
    ]:
        if support_projection.get(field) is not False:
            errors.append(f"{field} must be false")

    ledger = obj.get("deletion_ledger", {})
    if ledger.get("expected_root_digest") != ledger.get("prior_root_digest"):
        errors.append("deletion ledger CAS expected root must equal prior root")
    if ledger.get("new_root_digest") == ledger.get("prior_root_digest"):
        errors.append("deletion ledger root must advance")
    if ledger.get("compare_and_swap_result") != "committed":
        errors.append("deletion ledger CAS must commit")
    if ledger.get("delete_sequence", 0) <= access.get("export_sequence", 0):
        errors.append("deletion sequence must follow export access sequence")
    if any(ledger.get(flag) is not False for flag in ["rollback_accepted", "forked_root_accepted", "stale_root_accepted"]):
        errors.append("rollback/fork/stale deletion roots must not be accepted")

    joins = obj.get("joins", {})
    for flag in [
        "export_access_required_deletion_receipt",
        "export_access_digest_matches_source_binding",
        "recipient_digest_matches_export_access",
        "tombstone_digest_checked_before_deletion",
        "support_projection_is_allowlisted",
    ]:
        if joins.get(flag) is not True:
            errors.append(f"join flag {flag} must be true")
    if joins.get("revocation_tombstone_fixture_schema") != "spec/removable.media.local.post_detach.revocation.tombstone.fixture.schema.json":
        errors.append("revocation tombstone fixture schema path mismatch")

    invariants = obj.get("invariants", {})
    for key, value in invariants.items():
        if value is not True:
            errors.append(f"invariant {key} must be true")
    return errors


def require_docs() -> None:
    for rel, tokens in REQUIRED_DOC_TOKENS.items():
        path = ROOT / rel
        if not path.exists():
            fail(f"missing required doc surface: {rel}")
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in tokens:
            if token not in text:
                fail(f"{rel} missing required token {token!r}")
    hygiene = (ROOT / "tools" / "hygiene.py").read_text(encoding="utf-8")
    if "check_removable_media_local_post_detach_export_bundle_deletion_receipt.py" not in hygiene:
        fail("tools/hygiene.py must include check_removable_media_local_post_detach_export_bundle_deletion_receipt.py")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.parse_args()

    example = load_json(ROOT, EXAMPLE)
    errs = validation_errors(SCHEMA, example)
    if errs:
        fail(f"{EXAMPLE} failed {SCHEMA}: {errs[:10]}")
    sem = semantic_errors(example)
    if sem:
        fail("semantic export-bundle deletion receipt errors:\n- " + "\n- ".join(sem[:30]))

    invalid_root = ROOT / INVALID_DIR
    if not invalid_root.is_dir():
        fail(f"missing invalid fixture dir {INVALID_DIR}")
    observed = sorted(p.name for p in invalid_root.glob("*.json"))
    if observed != EXPECTED_INVALIDS:
        fail(f"invalid fixtures mismatch: {observed} != {EXPECTED_INVALIDS}")
    for name in EXPECTED_INVALIDS:
        rel = f"{INVALID_DIR}/{name}"
        bad = load_json(ROOT, rel)
        schema_errs = validation_errors(SCHEMA, bad)
        sem_errs = semantic_errors(bad) if not schema_errs else []
        if not schema_errs and not sem_errs:
            fail(f"invalid fixture unexpectedly passed schema+semantic checks: {rel}")

    require_docs()
    print("removable-media post-detach export-bundle deletion receipt check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
