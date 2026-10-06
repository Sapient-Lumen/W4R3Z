#!/usr/bin/env python3
"""Validate r528 post-detach export-bundle access receipts.

r508 made export bundles redacted and approval-bound. r528 gives the actual
bundle release/access its own receipt: approval, query-access, tombstone,
recipient, transport/retention, support-safe decision, denial/rate-limit joins,
and CAS-rooted export ledger are checked as a typed artifact.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from cube_digest_lib import file_json_digest, load_json

ROOT = Path(__file__).resolve().parents[1]
VERSION = "2026-05-30r528"
SCHEMA = "spec/removable.media.local.post_detach.export.bundle.access.receipt.schema.json"
EXAMPLE = "spec/examples/removable.media.local.post_detach.export.bundle.access.receipt.json"
INVALID_DIR = "spec/examples/invalid/removable-media/post-detach-export-bundle-access-receipt"

SOURCE_BINDINGS = {
    "export_bundle_computed_digest": "spec/examples/removable.media.local.post_detach.export.bundle.json",
    "query_projection_access_receipt_computed_digest": "spec/examples/removable.media.local.post_detach.query.projection.access.receipt.json",
    "query_projection_computed_digest": "spec/examples/removable.media.local.post_detach.query.projection.json",
    "support_projection_computed_digest": "spec/examples/removable.media.local.post_detach.support.projection.json",
    "denial_selection_receipt_computed_digest": "spec/examples/removable.media.local.post_detach.denial.selection.receipt.json",
    "rate_limit_debit_ledger_receipt_computed_digest": "spec/examples/removable.media.local.post_detach.rate_limit.debit.ledger.receipt.json",
    "revocation_tombstone_computed_digest": "spec/examples/removable.media.local.post_detach.revocation.tombstone.json",
}

EXPECTED_INVALIDS = [
    "export-ledger-not-advanced.json",
    "export-without-approval.json",
    "live-locator-present.json",
    "missing-deletion-receipt.json",
    "raw-authoritative-receipts-included.json",
    "raw-path-visible.json",
    "recipient-unbound.json",
    "stale-query-access-binding.json",
    "tombstone-not-checked.json",
    "unbounded-retention.json",
]

REQUIRED_DOC_TOKENS = {
    "CHANGELOG.md": [VERSION, "export.bundle.access.receipt", "check_removable_media_local_post_detach_export_bundle_access_receipt.py"],
    "README.md": [VERSION, "export-bundle-access", "export-bundle-schema-split"],
    "docs/00-index.md": [VERSION, "docs/current/removable-media-post-detach-export-bundle-access.md"],
    "docs/98-archive-hygiene.md": ["check_removable_media_local_post_detach_export_bundle_access_receipt.py"],
    "docs/99-llm-runbook.md": ["check_removable_media_local_post_detach_export_bundle_access_receipt.py"],
    "docs/110-juicy-os-lessons.md": ["r528 removable-media post-detach export bundle access"],
    "docs/783-removable-media-local-fallback-post-detach-export-bundle-access-and-schema-split.md": [
        "removable.media.local.post_detach.export.bundle.access.receipt",
        "post-detach-export-bundle-access-positive-and-negative-fixture-guarded",
        "post-detach-export-bundle-generic-runtime-schema-plus-exact-fixture-split",
    ],
    "docs/current/removable-media-post-detach-export-bundle-access.md": [
        "approval-bound",
        "query-access-bound",
        "recipient-bound",
        "export ledger",
    ],
}


def fail(msg: str) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(1)


def validation_errors(schema_rel: str, obj: Any) -> list[str]:
    schema = load_json(ROOT, schema_rel)
    validator = Draft202012Validator(schema)
    return [e.message for e in sorted(validator.iter_errors(obj), key=lambda e: list(e.absolute_path))]


def semantic_errors(obj: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if obj.get("generated_for_version") != VERSION:
        errors.append("export-bundle access receipt version mismatch")
    lane = obj.get("lane", {})
    if lane.get("family") != "removable-media-local-fallback" or lane.get("phase") != "post-detach":
        errors.append("lane must remain removable-media-local-fallback/post-detach")

    bindings = obj.get("source_bindings", {})
    if bindings.get("canonical_digest_rule") != "json-sort-keys-compact-utf8-sha256":
        errors.append("canonical digest rule mismatch")
    for key, rel in SOURCE_BINDINGS.items():
        if bindings.get(key) != file_json_digest(ROOT, rel):
            errors.append(f"{key} does not match {rel}")

    export = load_json(ROOT, "spec/examples/removable.media.local.post_detach.export.bundle.json")
    qaccess = load_json(ROOT, "spec/examples/removable.media.local.post_detach.query.projection.access.receipt.json")
    support = load_json(ROOT, "spec/examples/removable.media.local.post_detach.support.projection.json")

    req = obj.get("export_request", {})
    if req.get("approval_receipt_digest") != export.get("export_authority", {}).get("approval_receipt_digest"):
        errors.append("approval receipt digest must match export bundle")
    if req.get("recipient_digest") != export.get("transport_storage", {}).get("recipient_digest"):
        errors.append("recipient digest must match export bundle")
    if req.get("source_projection_snapshot_digest") != export.get("source_projection", {}).get("projection_snapshot_digest"):
        errors.append("source projection snapshot digest must match export bundle")
    if set(req.get("approved_entries", [])) - set(export.get("bundle_contents", {}).get("allowed_entries", [])):
        errors.append("approved export entries must be a subset of bundle allowed entries")

    auth = obj.get("authorization", {})
    if auth.get("query_projection_access_receipt_digest") != file_json_digest(ROOT, "spec/examples/removable.media.local.post_detach.query.projection.access.receipt.json"):
        errors.append("query-projection access digest binding is stale")
    if not auth.get("export_requires_approval") or not auth.get("approval_digest_matches_bundle"):
        errors.append("export access must be approval-bound")
    if not auth.get("query_projection_access_required") or not auth.get("query_projection_access_ledger_committed"):
        errors.append("export access must be query-access-bound and committed first")
    if not auth.get("revocation_checked_before_export") or not auth.get("tombstone_checked_before_export"):
        errors.append("revocation/tombstone must be checked before export")
    if not auth.get("recipient_bound"):
        errors.append("export access must be recipient-bound")
    if auth.get("ambient_debug_dump_allowed") is not False:
        errors.append("ambient debug dump must remain forbidden")

    policy = obj.get("bundle_policy", {})
    for field in [
        "raw_authoritative_receipts_included",
        "raw_query_index_included",
        "raw_media_bytes_included",
        "derived_output_bytes_included",
        "secret_material_included",
    ]:
        if policy.get(field) is not False:
            errors.append(f"{field} must be false")
    if not policy.get("bundle_derived_from_redacted_projection"):
        errors.append("bundle must be derived from the redacted projection")

    transport = obj.get("transport_storage", {})
    if transport.get("recipient_digest") != req.get("recipient_digest"):
        errors.append("transport recipient digest must match request recipient")
    if transport.get("live_locator") != "forbidden-in-first-lane" or transport.get("raw_locator_visible") is not False:
        errors.append("live/raw locators must remain absent from export access")
    if transport.get("retention") != "bounded-explicit-expiry" or transport.get("unbounded_retention_allowed") is not False:
        errors.append("export access must be retention-bounded")
    if transport.get("deletion_receipt_required") is not True:
        errors.append("export access must require deletion receipt")

    decision = obj.get("decision", {})
    if decision.get("support_projection_visibility") != support.get("visibility"):
        errors.append("support projection visibility must match support projection")
    for field in ["raw_payload_visible", "raw_path_visible", "filename_visible", "device_identifier_visible", "host_identity_visible", "body_or_full_text_visible"]:
        if decision.get(field) is not False:
            errors.append(f"{field} must be false")
    if decision.get("failure_denial_selection_required") is not True or decision.get("rate_limit_debit_receipt_required_on_denial") is not True:
        errors.append("failed exports must join denial selection and rate-limit debit")

    ledger = obj.get("export_ledger", {})
    if ledger.get("expected_root_digest") != ledger.get("prior_root_digest"):
        errors.append("export ledger CAS expected root must equal prior root")
    if ledger.get("new_root_digest") == ledger.get("prior_root_digest"):
        errors.append("export ledger root must advance")
    if ledger.get("compare_and_swap_result") != "committed":
        errors.append("export ledger CAS must commit")
    if any(ledger.get(flag) is not False for flag in ["rollback_accepted", "forked_root_accepted", "stale_root_accepted"]):
        errors.append("rollback/fork/stale roots must not be accepted")
    if ledger.get("export_sequence", 0) <= qaccess.get("access_ledger", {}).get("access_sequence", 0):
        errors.append("export sequence should follow query-projection access sequence")

    joins = obj.get("joins", {})
    if joins.get("export_bundle_schema") != "spec/removable.media.local.post_detach.export.bundle.schema.json":
        errors.append("runtime export-bundle schema path mismatch")
    if joins.get("export_bundle_fixture_schema") != "spec/removable.media.local.post_detach.export.bundle.fixture.schema.json":
        errors.append("fixture export-bundle schema path mismatch")
    for flag in [
        "export_bundle_accesses_redacted_projection_only",
        "query_access_receipt_committed_before_export",
        "recipient_digest_matches_bundle",
        "approval_digest_matches_bundle",
        "retention_matches_bundle",
        "support_projection_is_allowlisted",
    ]:
        if joins.get(flag) is not True:
            errors.append(f"join flag {flag} must be true")

    for key, value in obj.get("invariants", {}).items():
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
    hygiene = (ROOT / "tools" / "hygiene.py").read_text(encoding="utf-8", errors="replace")
    if "check_removable_media_local_post_detach_export_bundle_access_receipt.py" not in hygiene:
        fail("tools/hygiene.py missing export-bundle access checker")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="reserved; example is static for this cut")
    args = ap.parse_args()
    if args.write:
        print("example is maintained directly for r528")
        return 0

    obj = load_json(ROOT, EXAMPLE)
    errs = validation_errors(SCHEMA, obj)
    if errs:
        fail(f"{EXAMPLE} failed {SCHEMA}: {errs[:10]}")
    sem = semantic_errors(obj)
    if sem:
        fail("semantic export-bundle access errors:\n- " + "\n- ".join(sem[:30]))

    invalid_dir = ROOT / INVALID_DIR
    observed = sorted(p.name for p in invalid_dir.glob("*.json"))
    if observed != EXPECTED_INVALIDS:
        fail(f"invalid fixture set drifted: {observed} != {EXPECTED_INVALIDS}")
    for name in EXPECTED_INVALIDS:
        rel = f"{INVALID_DIR}/{name}"
        bad = load_json(ROOT, rel)
        schema_errs = validation_errors(SCHEMA, bad)
        sem_errs = semantic_errors(bad)
        if not schema_errs and not sem_errs:
            fail(f"invalid fixture unexpectedly passes schema + semantic checks: {rel}")

    require_docs()
    print("removable-media post-detach export-bundle access receipt check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
