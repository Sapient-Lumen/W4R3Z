#!/usr/bin/env python3
"""Validate removable-media post-detach fresh-authority receipts.

This guardrail keeps r511 from drifting toward stale-handle renewal: successor
query/export/rehydration authority after a tombstone-caused denial must be a
fresh lease and new policy decision, not replay of the denied handle.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_REL = "spec/removable.media.local.post_detach.fresh.authority.receipt.schema.json"
FIXTURE_SCHEMA_REL = "spec/removable.media.local.post_detach.fresh.authority.receipt.fixture.schema.json"
EXAMPLE_REL = "spec/examples/removable.media.local.post_detach.fresh.authority.receipt.json"
INVALID_DIR = "spec/examples/invalid/removable-media/post-detach-fresh-authority-receipt"
F_KIND = "removable.media.local.post_detach.fresh.authority.receipt"
F_POSTURE = "typed-post-detach-fresh-authority-receipt-positive-and-negative-fixture-guarded"
F_DIGEST = "sha256:7171717171717171717171717171717171717171717171717171717171717171"
F_POLICY = "known-bad-post-detach-fresh-authority-receipt-shapes-must-fail-validation"
F_LEASE_DIGEST = "sha256:7272727272727272727272727272727272727272727272727272727272727272"
DENIAL_DIGEST = "sha256:6868686868686868686868686868686868686868686868686868686868686868"
TOMBSTONE_DIGEST = "sha256:6666666666666666666666666666666666666666666666666666666666666666"

REQUIRED_INVALID_FIXTURES = ['missing-denial-receipt-causality.json', 'stale-handle-reused.json', 'old-tombstone-mutated.json', 'broad-successor-scope.json', 'pattern-successor-subject.json', 'raw-locator-included.json', 'no-fresh-lease.json', 'no-user-presence.json', 'secret-material-present.json', 'offline-erasure-claimed.json']

JSON_REQUIREMENTS = {
    "spec/examples/removable.media.local.post_detach.denial.receipt.json": (
        (("fresh_authority", "posture"), F_POSTURE),
        (("fresh_authority", "kind"), F_KIND),
        (("fresh_authority", "schema"), SCHEMA_REL),
        (("fresh_authority", "digest"), F_DIGEST),
        (("fresh_authority", "negative_fixture_policy"), F_POLICY),
        (("fresh_authority", "fresh_authority_required_for_successor"), True),
        (("fresh_authority", "stale_handle_is_not_renewal_handle"), True),
        (("fresh_authority", "new_lease_digest"), F_LEASE_DIGEST),
    ),
    "spec/examples/removable.media.local.post_detach.revocation.tombstone.json": (
        (("fresh_authority", "posture"), F_POSTURE),
        (("fresh_authority", "kind"), F_KIND),
        (("fresh_authority", "schema"), SCHEMA_REL),
        (("fresh_authority", "digest"), F_DIGEST),
        (("fresh_authority", "negative_fixture_policy"), F_POLICY),
    ),
    "spec/examples/removable.media.local.post_detach.export.bundle.json": (
        (("fresh_authority", "posture"), F_POSTURE),
        (("fresh_authority", "kind"), F_KIND),
        (("fresh_authority", "schema"), SCHEMA_REL),
        (("fresh_authority", "digest"), F_DIGEST),
        (("fresh_authority", "negative_fixture_policy"), F_POLICY),
    ),
    "spec/examples/removable.media.local.post_detach.query.projection.json": (
        (("fresh_authority", "posture"), F_POSTURE),
        (("fresh_authority", "kind"), F_KIND),
        (("fresh_authority", "schema"), SCHEMA_REL),
        (("fresh_authority", "digest"), F_DIGEST),
        (("fresh_authority", "negative_fixture_policy"), F_POLICY),
    ),
    "spec/examples/removable.media.local.post_detach.recovery.evidence.json": (
        (("query_projection", "fresh_authority_posture"), F_POSTURE),
        (("query_projection", "fresh_authority_kind"), F_KIND),
        (("query_projection", "fresh_authority_schema"), SCHEMA_REL),
        (("query_projection", "fresh_authority_digest"), F_DIGEST),
        (("query_projection", "fresh_authority_negative_fixture_policy"), F_POLICY),
        (("query_projection", "fresh_authority_required"), True),
    ),
    "spec/examples/removable.media.local.post_detach.contract.json": (
        (("backend_evidence", "fresh_authority_posture"), F_POSTURE),
        (("backend_evidence", "fresh_authority_kind"), F_KIND),
        (("backend_evidence", "fresh_authority_schema"), SCHEMA_REL),
        (("backend_evidence", "fresh_authority_digest"), F_DIGEST),
        (("backend_evidence", "fresh_authority_negative_fixture_policy"), F_POLICY),
        (("backend_evidence", "fresh_authority_required"), True),
        (("failure_policy", "successor_authority_without_fresh_authority_receipt"), "fail-closed"),
    ),
    "spec/examples/content.import.plan.removable-media-local-ingest.json": (
        (("execution", "post_detach_fresh_authority_posture"), F_POSTURE),
        (("execution", "post_detach_fresh_authority_digest"), F_DIGEST),
        (("execution", "post_detach_fresh_authority_schema"), SCHEMA_REL),
        (("execution", "post_detach_fresh_authority_negative_fixture_policy"), F_POLICY),
        (("execution", "post_detach_fresh_authority_required"), True),
        (("operations", 0, "params", "post_detach_fresh_authority_posture"), F_POSTURE),
    ),
    "spec/examples/content.import.receipt.removable-media-local-ingest.json": (
        (("execution", "post_detach_fresh_authority_posture"), F_POSTURE),
        (("execution", "post_detach_fresh_authority_digest"), F_DIGEST),
        (("execution", "post_detach_fresh_authority_schema"), SCHEMA_REL),
        (("execution", "post_detach_fresh_authority_negative_fixture_policy"), F_POLICY),
        (("execution", "post_detach_fresh_authority_required"), True),
    ),
    "spec/examples/preopen.map.removable-media-local-ingest-post-detach.json": (
        (("fresh_authority_posture",), F_POSTURE),
        (("fresh_authority_digest",), F_DIGEST),
        (("fresh_authority_schema",), SCHEMA_REL),
        (("fresh_authority_negative_fixture_policy",), F_POLICY),
        (("fresh_authority_required",), True),
    ),
}

SCHEMA_FIELDS = {
    SCHEMA_REL: (
        F_KIND,
        FIXTURE_SCHEMA_REL,
        "post-detach-fresh-authority-generic-runtime-schema-plus-exact-fixture-split",
        "fresh-lease-issued-with-new-digest-subject",
        "fresh-lease-and-policy-decision-required-after-denial",
        "exact-new-digest-subjects-only-same-or-narrower-than-original",
        "stale_handle_reused",
        "tombstone_mutated_or_deleted",
    ),
    FIXTURE_SCHEMA_REL: (F_KIND, F_POSTURE, F_DIGEST, F_POLICY, "fresh-lease-issued-with-new-digest-subject"),
    "spec/removable.media.local.post_detach.denial.receipt.schema.json": ("fresh_authority", F_POSTURE, F_DIGEST, F_POLICY),
    "spec/removable.media.local.post_detach.revocation.tombstone.schema.json": ("fresh_authority", F_POSTURE, F_DIGEST, F_POLICY),
    "spec/removable.media.local.post_detach.export.bundle.schema.json": ("fresh_authority", F_POSTURE, F_DIGEST, F_POLICY),
    "spec/removable.media.local.post_detach.query.projection.schema.json": ("fresh_authority", F_POSTURE, F_DIGEST, F_POLICY),
    "spec/removable.media.local.post_detach.recovery.evidence.schema.json": ("fresh_authority_posture", F_POSTURE, F_POLICY, "sha256Digest"),
    "spec/removable.media.local.post_detach.recovery.evidence.fixture.schema.json": ("fresh_authority_posture", F_DIGEST, F_POLICY),
    "spec/removable.media.local.post_detach.contract.schema.json": ("fresh_authority_posture", "fresh_authority_required", "successor_authority_without_fresh_authority_receipt"),
    "spec/content.import.plan.schema.json": ("post_detach_fresh_authority_posture", "post_detach_fresh_authority_negative_fixture_policy"),
    "spec/content.import.receipt.schema.json": ("post_detach_fresh_authority_posture", "post_detach_fresh_authority_negative_fixture_policy"),
    "spec/preopen.map.schema.json": ("fresh_authority_posture", "fresh_authority_negative_fixture_policy"),
}

TEXT_REQUIREMENTS = {
    "docs/766-removable-media-local-fallback-post-detach-fresh-authority-reissue-is-typed-and-negative-tested.md": (F_POSTURE, F_DIGEST, F_POLICY, SCHEMA_REL, EXAMPLE_REL, INVALID_DIR, "fresh-lease-issued-with-new-digest-subject"),
    "adrs/ADR-0355-removable-media-local-fallback-post-detach-fresh-authority-reissue-is-typed-and-negative-tested.md": (F_POSTURE, F_DIGEST, F_POLICY, SCHEMA_REL, INVALID_DIR),
    "docs/765-removable-media-local-fallback-post-detach-denial-receipts-are-typed-and-negative-tested.md": (F_POSTURE, F_DIGEST, F_POLICY, SCHEMA_REL),
    "docs/764-removable-media-local-fallback-post-detach-revocation-tombstones-are-typed-and-negative-tested.md": (F_POSTURE, F_DIGEST),
    "docs/763-removable-media-local-fallback-post-detach-export-bundles-are-redacted-and-negative-tested.md": (F_POSTURE, "fresh-authority"),
    "docs/762-removable-media-local-fallback-post-detach-query-projection-is-typed-and-negative-tested.md": (F_POSTURE, "fresh-authority"),
    "docs/293-attribute-indexed-metadata-and-live-queries.md": (F_POSTURE, "fresh-authority receipt"),
    "docs/266-open-questions-and-risk-register.md": (F_POSTURE, F_POLICY),
    "docs/98-archive-hygiene.md": ("check_removable_media_local_post_detach_fresh_authority_receipt.py", F_POSTURE),
    "docs/99-llm-runbook.md": ("check_removable_media_local_post_detach_fresh_authority_receipt.py", F_POSTURE),
    "docs/110-juicy-os-lessons.md": (F_POSTURE, "fresh-lease-issued-with-new-digest-subject"),
    "README.md": ("ADR-0355", F_POSTURE),
    "docs/00-index.md": ("ADR-0355", "docs/766-removable-media-local-fallback-post-detach-fresh-authority-reissue-is-typed-and-negative-tested.md", F_POSTURE),
    "CHANGELOG.md": ("2026-05-22r511", "2026-05-30r531", "check_removable_media_local_post_detach_fresh_authority_receipt.py", F_POSTURE, "post-detach-fresh-authority-generic-runtime-schema-plus-exact-fixture-split"),
    "docs/786-removable-media-local-fallback-post-detach-terminal-closure-access-and-fresh-authority-schema-split.md": ("post-detach-fresh-authority-generic-runtime-schema-plus-exact-fixture-split", FIXTURE_SCHEMA_REL),
}


def fail(msg: str) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(1)


def load_json(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def nested_value(obj, path):
    cur = obj
    for part in path:
        cur = cur[part]
    return cur


def validation_errors(validator: Draft202012Validator, obj: object) -> list[str]:
    return [e.message for e in sorted(validator.iter_errors(obj), key=lambda e: list(e.absolute_path))]


def main() -> None:
    schema = load_json(SCHEMA_REL)
    example = load_json(EXAMPLE_REL)
    validator = Draft202012Validator(schema)
    fixture_validator = Draft202012Validator(load_json(FIXTURE_SCHEMA_REL))

    errs = validation_errors(validator, example)
    if errs:
        fail(f"{EXAMPLE_REL} must validate against {SCHEMA_REL}: {errs[:10]}")
    fixture_errs = validation_errors(fixture_validator, example)
    if fixture_errs:
        fail(f"{EXAMPLE_REL} must validate against exact fixture {FIXTURE_SCHEMA_REL}: {fixture_errs[:10]}")

    if schema.get("additionalProperties") is not False:
        fail(f"{SCHEMA_REL} must be closed-world at the root")
    if "$defs" not in schema:
        fail(f"{SCHEMA_REL} must be runtime-shaped with $defs")
    if "allOf" not in load_json(FIXTURE_SCHEMA_REL):
        fail(f"{FIXTURE_SCHEMA_REL} must preserve the exact historical fixture schema under allOf")

    if example["contract_binding"]["denial_receipt_digest"] != DENIAL_DIGEST:
        fail(f"{EXAMPLE_REL} must bind r510 denial receipt digest {DENIAL_DIGEST}")
    if example["contract_binding"]["revocation_tombstone_digest"] != TOMBSTONE_DIGEST:
        fail(f"{EXAMPLE_REL} must bind r509 tombstone digest {TOMBSTONE_DIGEST}")
    if example["successor_subjects"]["old_handle_reused"] is not False:
        fail(f"{EXAMPLE_REL} must not reuse the stale handle")
    if example["authority_decision"]["offline_copy_erasure_claimed"] is not False:
        fail(f"{EXAMPLE_REL} must not claim offline-copy erasure")

    invalid_dir = ROOT / INVALID_DIR
    observed = {p.name for p in invalid_dir.glob("*.json")}
    missing = sorted(set(REQUIRED_INVALID_FIXTURES) - observed)
    if missing:
        fail(f"missing invalid fixtures under {INVALID_DIR}: {missing}")

    for name in sorted(REQUIRED_INVALID_FIXTURES):
        rel = f"{INVALID_DIR}/{name}"
        bad = load_json(rel)
        if not validation_errors(validator, bad):
            fail(f"invalid fixture unexpectedly validates: {rel}")

    for rel, reqs in JSON_REQUIREMENTS.items():
        obj = load_json(rel)
        for path, expected in reqs:
            try:
                actual = nested_value(obj, path)
            except (KeyError, IndexError, TypeError) as exc:
                fail(f"{rel} missing {'.'.join(map(str, path))}: {exc}")
            if actual != expected:
                fail(f"{rel} {'.'.join(map(str, path))} = {actual!r}, expected {expected!r}")

    for rel, fields in SCHEMA_FIELDS.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for field in fields:
            if f'"{field}"' not in text and field not in text:
                fail(f"{rel} missing schema field/token {field}")

    for rel, needles in TEXT_REQUIREMENTS.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                fail(f"{rel} missing {needle!r}")

    hygiene = (ROOT / "tools" / "hygiene.py").read_text(encoding="utf-8")
    if "check_removable_media_local_post_detach_fresh_authority_receipt.py" not in hygiene:
        fail("tools/hygiene.py must include check_removable_media_local_post_detach_fresh_authority_receipt.py")

    print("removable-media post-detach fresh-authority receipt check passed")


if __name__ == "__main__":
    main()
