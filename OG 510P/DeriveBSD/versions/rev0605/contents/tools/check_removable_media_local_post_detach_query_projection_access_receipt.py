#!/usr/bin/env python3
"""Validate r527 post-detach query-projection access receipts.

r507 made the post-detach query projection lease-bound and redacted. r527 gives
actual projection access its own receipt: the access request, lease, allowlisted
fields, tombstone check, support-safe decision, CAS-rooted access ledger, and
failure-denial/rate-limit joins are checked as a typed artifact.
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
VERSION = "2026-05-30r527"
SCHEMA = "spec/removable.media.local.post_detach.query.projection.access.receipt.schema.json"
EXAMPLE = "spec/examples/removable.media.local.post_detach.query.projection.access.receipt.json"
INVALID_DIR = "spec/examples/invalid/removable-media/post-detach-query-projection-access-receipt"

SOURCE_BINDINGS = {
    "query_projection_computed_digest": "spec/examples/removable.media.local.post_detach.query.projection.json",
    "support_projection_computed_digest": "spec/examples/removable.media.local.post_detach.support.projection.json",
    "denial_selection_receipt_computed_digest": "spec/examples/removable.media.local.post_detach.denial.selection.receipt.json",
    "rate_limit_debit_ledger_receipt_computed_digest": "spec/examples/removable.media.local.post_detach.rate_limit.debit.ledger.receipt.json",
    "revocation_tombstone_computed_digest": "spec/examples/removable.media.local.post_detach.revocation.tombstone.json",
}

EXPECTED_INVALIDS = [
    "aggregate-counts-enabled.json",
    "audit-ledger-not-advanced.json",
    "body-text-visible.json",
    "disallowed-field-returned.json",
    "live-subscription-enabled.json",
    "query-without-lease.json",
    "raw-path-visible.json",
    "stale-projection-binding.json",
    "tombstone-not-checked.json",
]

REQUIRED_DOC_TOKENS = {
    "CHANGELOG.md": [VERSION, "query.projection.access.receipt", "check_removable_media_local_post_detach_query_projection_access_receipt.py"],
    "README.md": [VERSION, "query-projection-access", "query-projection-schema-split"],
    "docs/00-index.md": [VERSION, "docs/current/removable-media-post-detach-query-projection-access.md"],
    "docs/98-archive-hygiene.md": ["check_removable_media_local_post_detach_query_projection_access_receipt.py"],
    "docs/99-llm-runbook.md": ["check_removable_media_local_post_detach_query_projection_access_receipt.py"],
    "docs/110-juicy-os-lessons.md": ["r527 removable-media post-detach query projection access"],
    "docs/782-removable-media-local-fallback-post-detach-query-projection-access-and-schema-split.md": [
        "removable.media.local.post_detach.query.projection.access.receipt",
        "post-detach-query-projection-access-positive-and-negative-fixture-guarded",
        "post-detach-query-projection-generic-runtime-schema-plus-exact-fixture-split",
    ],
    "docs/current/removable-media-post-detach-query-projection-access.md": [
        "lease-bound",
        "tombstone-checked",
        "access ledger",
        "allowlisted fields",
    ],
}


def fail(msg: str) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(1)


def validation_errors(schema_rel: str, obj: Any) -> list[str]:
    schema = load_json(ROOT, schema_rel)
    validator = Draft202012Validator(schema)
    return [e.message for e in sorted(validator.iter_errors(obj), key=lambda e: list(e.absolute_path))]


def build_receipt() -> dict[str, Any]:
    query_projection = load_json(ROOT, "spec/examples/removable.media.local.post_detach.query.projection.json")
    support = load_json(ROOT, "spec/examples/removable.media.local.post_detach.support.projection.json")
    selection = load_json(ROOT, "spec/examples/removable.media.local.post_detach.denial.selection.receipt.json")
    rate = load_json(ROOT, "spec/examples/removable.media.local.post_detach.rate_limit.debit.ledger.receipt.json")

    returned_fields = [
        "receipt_digest",
        "contract_digest",
        "recovery_evidence_digest",
        "derivative_output_digest",
        "status",
        "redaction_profile",
        "lease_digest",
    ]

    return {
        "kind": "removable.media.local.post_detach.query.projection.access.receipt",
        "schema_version": "1.0",
        "access_receipt_id": "rm-postdetach-query-access-20260530-r527",
        "generated_for_version": VERSION,
        "lane": {
            "family": "removable-media-local-fallback",
            "phase": "post-detach",
            "identity_policy": "family-normalized-phase-by-kind",
        },
        "source_bindings": {
            "canonical_digest_rule": "json-sort-keys-compact-utf8-sha256",
            **{key: file_json_digest(ROOT, rel) for key, rel in SOURCE_BINDINGS.items()},
        },
        "query_request": {
            "request_id": "rm-postdetach-query-request-20260530-r527",
            "actor_scope": query_projection["lease_binding"]["actor_scope"],
            "query_scope": query_projection["lease_binding"]["query_scope"],
            "query_language": query_projection["query_index"]["query_language"],
            "requested_fields": [
                "receipt_digest",
                "contract_digest",
                "recovery_evidence_digest",
                "derivative_output_digest",
                "status",
                "lease_digest",
            ],
            "returned_fields": returned_fields,
            "lease_digest": query_projection["lease_binding"]["lease_digest"],
            "subject_digest": "sha256:d1d1d1d1d1d1d1d1d1d1d1d1d1d1d1d1d1d1d1d1d1d1d1d1d1d1d1d1d1d1d1d1",
            "live_subscription_requested": False,
            "aggregate_counts_requested": False,
        },
        "authorization": {
            "query_access_model": query_projection["lease_binding"]["query_access_model"],
            "lease_required": True,
            "lease_digest_matches_projection": True,
            "revocation_checked_before_projection": True,
            "tombstone_checked_before_projection": True,
            "tombstone_digest": query_projection["revocation_tombstone"]["digest"],
            "ambient_index_read_allowed": False,
            "cross_lane_join_policy": query_projection["query_index"]["cross_lane_join"],
            "fresh_authority_required_after_tombstone": True,
        },
        "projection_policy": {
            "field_policy_digest": query_projection["projection_policy"]["field_policy_digest"],
            "allowed_fields": query_projection["projection_policy"]["allowed_fields"],
            "returned_fields_are_subset_of_allowed_fields": True,
            "no_body_text": query_projection["query_index"]["no_body_text"],
            "no_raw_paths": query_projection["query_index"]["no_raw_paths"],
            "no_device_identifiers": query_projection["query_index"]["no_device_identifiers"],
            "no_host_identity": query_projection["query_index"]["no_host_identity"],
            "filename_indexing_allowed": False,
            "observed_hints_indexed": query_projection["source_receipts"]["raw_media_hints_indexed"],
            "raw_media_hints_indexed": query_projection["source_receipts"]["raw_media_hints_indexed"],
        },
        "decision": {
            "outcome": "projection-access-granted-redacted-digest-only",
            "projection_visible": True,
            "raw_payload_visible": False,
            "body_or_full_text_visible": False,
            "raw_path_visible": False,
            "filename_visible": False,
            "device_identifier_visible": False,
            "host_identity_visible": False,
            "support_projection_visibility": support["visibility"],
            "failure_denial_receipt_required": True,
            "query_after_tombstone_action": "deny-with-denial-selection-and-rate-limit-debit",
            "rate_limit_debit_receipt_required_on_denial": True,
        },
        "access_ledger": {
            "prior_root_digest": "sha256:9a9a000000000000000000000000000000000000000000000000000000000001",
            "expected_root_digest": "sha256:9a9a000000000000000000000000000000000000000000000000000000000001",
            "new_root_digest": "sha256:9a9a000000000000000000000000000000000000000000000000000000000002",
            "ledger_anchor_digest": "sha256:9a9a000000000000000000000000000000000000000000000000000000000003",
            "access_sequence": 51,
            "broker_epoch_id": "rm-postdetach-broker-epoch-20260530-r527",
            "idempotency_key_digest": rate["debit_accounting"]["idempotency_key_digest"],
            "compare_and_swap_result": "committed",
            "replay_outcome": "first-query-projection-access",
            "rollback_accepted": False,
            "forked_root_accepted": False,
            "stale_root_accepted": False,
        },
        "joins": {
            "query_projection_schema": "spec/removable.media.local.post_detach.query.projection.schema.json",
            "query_projection_fixture_schema": "spec/removable.media.local.post_detach.query.projection.fixture.schema.json",
            "lease_digest_matches_query_projection": True,
            "allowed_fields_match_query_projection": True,
            "tombstone_digest_matches_query_projection": True,
            "support_projection_is_allowlisted": True,
            "denial_selection_available_for_failures": selection["selection_receipt_id"],
            "rate_limit_debit_available_for_denials": rate["debit_receipt_id"],
        },
        "invariants": {
            "access_receipt_precedes_projection_visibility": True,
            "ambient_index_read_forbidden": True,
            "returned_fields_are_allowlisted": True,
            "raw_values_absent_from_projection": True,
            "tombstone_checked_before_projection": True,
            "denied_queries_emit_typed_denial_selection": True,
            "denied_queries_have_rate_limit_debit_receipt": True,
            "access_ledger_root_advances": True,
            "cas_expected_equals_prior": True,
        },
        "negative_fixture_policy": "known-bad-post-detach-query-projection-access-shapes-must-fail-validation",
    }


def semantic_errors(obj: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if obj.get("generated_for_version") != VERSION:
        errors.append("query projection access receipt version mismatch")
    for key, rel in SOURCE_BINDINGS.items():
        expected = file_json_digest(ROOT, rel)
        if obj.get("source_bindings", {}).get(key) != expected:
            errors.append(f"source binding {key} is stale")

    query_projection = load_json(ROOT, "spec/examples/removable.media.local.post_detach.query.projection.json")
    allowed = set(query_projection["projection_policy"]["allowed_fields"])
    returned = set(obj.get("query_request", {}).get("returned_fields", []))
    if not returned or not returned <= allowed:
        errors.append("returned fields must be a non-empty subset of query_projection.projection_policy.allowed_fields")
    requested = set(obj.get("query_request", {}).get("requested_fields", []))
    if not requested <= allowed:
        errors.append("requested fields must be subset of allowed fields")

    if obj.get("query_request", {}).get("lease_digest") != query_projection["lease_binding"]["lease_digest"]:
        errors.append("lease digest must match query projection lease")
    if obj.get("authorization", {}).get("tombstone_digest") != query_projection["revocation_tombstone"]["digest"]:
        errors.append("tombstone digest must match query projection tombstone binding")
    if obj.get("authorization", {}).get("lease_required") is not True:
        errors.append("query projection access must require a lease")
    if obj.get("authorization", {}).get("tombstone_checked_before_projection") is not True:
        errors.append("query projection access must check tombstone before projection")
    if obj.get("authorization", {}).get("ambient_index_read_allowed") is not False:
        errors.append("ambient index reads must remain forbidden")
    if obj.get("query_request", {}).get("live_subscription_requested") is not False:
        errors.append("live subscriptions are forbidden in this lane")
    if obj.get("query_request", {}).get("aggregate_counts_requested") is not False:
        errors.append("aggregate counts are forbidden in this lane")

    decision = obj.get("decision", {})
    for key in [
        "raw_payload_visible",
        "body_or_full_text_visible",
        "raw_path_visible",
        "filename_visible",
        "device_identifier_visible",
        "host_identity_visible",
    ]:
        if decision.get(key) is not False:
            errors.append(f"decision.{key} must be false")

    ledger = obj.get("access_ledger", {})
    if ledger.get("expected_root_digest") != ledger.get("prior_root_digest"):
        errors.append("access ledger CAS expected root must equal prior root")
    if ledger.get("new_root_digest") == ledger.get("prior_root_digest"):
        errors.append("access ledger root must advance")
    if ledger.get("compare_and_swap_result") != "committed":
        errors.append("access ledger CAS must commit")

    joins = obj.get("joins", {})
    if joins.get("query_projection_fixture_schema") != "spec/removable.media.local.post_detach.query.projection.fixture.schema.json":
        errors.append("query projection fixture schema join missing")
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
    if "check_removable_media_local_post_detach_query_projection_access_receipt.py" not in hygiene:
        fail("tools/hygiene.py missing query projection access checker")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="write the canonical r527 example")
    args = ap.parse_args()

    expected = build_receipt()
    if args.write:
        (ROOT / EXAMPLE).write_text(json.dumps(expected, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {EXAMPLE}")
        return 0

    observed = load_json(ROOT, EXAMPLE)
    errs = validation_errors(SCHEMA, observed)
    if errs:
        fail(f"{EXAMPLE} failed {SCHEMA}: {errs[:10]}")
    sem = semantic_errors(observed)
    if sem:
        fail("semantic query projection access errors:\n- " + "\n- ".join(sem[:30]))
    if observed != expected:
        fail("query projection access example is stale; regenerate with python3 tools/check_removable_media_local_post_detach_query_projection_access_receipt.py --write")

    invalid_root = ROOT / INVALID_DIR
    observed_invalids = sorted(p.name for p in invalid_root.glob("*.json"))
    if observed_invalids != EXPECTED_INVALIDS:
        fail(f"invalid fixture set mismatch: {observed_invalids} != {EXPECTED_INVALIDS}")
    for path in sorted(invalid_root.glob("*.json")):
        bad = load_json(ROOT, path.relative_to(ROOT).as_posix())
        if not validation_errors(SCHEMA, bad) and not semantic_errors(bad):
            fail(f"invalid fixture unexpectedly validates semantically: {path.relative_to(ROOT)}")

    require_docs()
    print("removable-media post-detach query-projection access receipt check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
