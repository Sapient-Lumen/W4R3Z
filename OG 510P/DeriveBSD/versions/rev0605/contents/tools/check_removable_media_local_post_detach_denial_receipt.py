#!/usr/bin/env python3
"""Guard the removable-media post-detach denial receipt contract."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_REL = "spec/removable.media.local.post_detach.denial.receipt.schema.json"
FIXTURE_SCHEMA_REL = "spec/removable.media.local.post_detach.denial.receipt.fixture.schema.json"
EXAMPLE_REL = "spec/examples/removable.media.local.post_detach.denial.receipt.json"
INVALID_DIR = "spec/examples/invalid/removable-media/post-detach-denial-receipt"
DR_POSTURE = "typed-post-detach-denial-receipt-positive-and-negative-fixture-guarded"
DR_DIGEST = "sha256:6868686868686868686868686868686868686868686868686868686868686868"
DR_POLICY = "known-bad-post-detach-denial-receipt-shapes-must-fail-validation"
DR_KIND = "removable.media.local.post_detach.denial.receipt"
TOMBSTONE_DIGEST = "sha256:6666666666666666666666666666666666666666666666666666666666666666"
TOMBSTONE_SCHEMA_REL = "spec/removable.media.local.post_detach.revocation.tombstone.schema.json"

REQUIRED_INVALID_FIXTURES = ['export-denial-allows-success.json', 'host-identity-leaked.json', 'missing-monotonic-sequence.json', 'query-denial-without-tombstone.json', 'raw-handle-included.json', 'raw-locator-included.json', 'rehydration-denial-allows-success.json', 'retry-not-rate-limited.json', 'successor-without-fresh-lease.json', 'untrusted-filename-included.json']

JSON_REQUIREMENTS = {
    "spec/examples/removable.media.local.post_detach.revocation.tombstone.json": (
        (("denial_receipt", "posture"), DR_POSTURE),
        (("denial_receipt", "kind"), DR_KIND),
        (("denial_receipt", "schema"), SCHEMA_REL),
        (("denial_receipt", "digest"), DR_DIGEST),
        (("denial_receipt", "negative_fixture_policy"), DR_POLICY),
        (("denial_receipt", "denial_receipt_required"), True),
        (("evidence_state", "denial_receipt_digest"), DR_DIGEST),
        (("verifier_model", "deny_after_tombstone_receipt_required"), True),
        (("failure_policy", "silent_denial_without_receipt"), "fail-closed"),
    ),
    "spec/examples/removable.media.local.post_detach.export.bundle.json": (
        (("denial_receipt", "posture"), DR_POSTURE),
        (("denial_receipt", "kind"), DR_KIND),
        (("denial_receipt", "schema"), SCHEMA_REL),
        (("denial_receipt", "digest"), DR_DIGEST),
        (("denial_receipt", "negative_fixture_policy"), DR_POLICY),
        (("failure_policy", "silent_denial_without_receipt"), "fail-closed"),
    ),
    "spec/examples/removable.media.local.post_detach.query.projection.json": (
        (("denial_receipt", "posture"), DR_POSTURE),
        (("denial_receipt", "kind"), DR_KIND),
        (("denial_receipt", "schema"), SCHEMA_REL),
        (("denial_receipt", "digest"), DR_DIGEST),
        (("denial_receipt", "negative_fixture_policy"), DR_POLICY),
        (("failure_policy", "silent_denial_without_receipt"), "fail-closed"),
    ),
    "spec/examples/removable.media.local.post_detach.recovery.evidence.json": (
        (("query_projection", "denial_receipt_posture"), DR_POSTURE),
        (("query_projection", "denial_receipt_kind"), DR_KIND),
        (("query_projection", "denial_receipt_schema"), SCHEMA_REL),
        (("query_projection", "denial_receipt_digest"), DR_DIGEST),
        (("query_projection", "denial_receipt_negative_fixture_policy"), DR_POLICY),
        (("query_projection", "denial_receipt_required"), True),
    ),
    "spec/examples/removable.media.local.post_detach.contract.json": (
        (("backend_evidence", "denial_receipt_posture"), DR_POSTURE),
        (("backend_evidence", "denial_receipt_kind"), DR_KIND),
        (("backend_evidence", "denial_receipt_schema"), SCHEMA_REL),
        (("backend_evidence", "denial_receipt_digest"), DR_DIGEST),
        (("backend_evidence", "denial_receipt_negative_fixture_policy"), DR_POLICY),
        (("backend_evidence", "denial_receipt_required"), True),
        (("failure_policy", "silent_denial_without_receipt"), "fail-closed"),
    ),
    "spec/examples/content.import.plan.removable-media-local-ingest.json": (
        (("execution", "post_detach_denial_receipt_posture"), DR_POSTURE),
        (("execution", "post_detach_denial_receipt_digest"), DR_DIGEST),
        (("execution", "post_detach_denial_receipt_schema"), SCHEMA_REL),
        (("execution", "post_detach_denial_receipt_negative_fixture_policy"), DR_POLICY),
        (("execution", "post_detach_denial_receipt_required"), True),
        (("operations", 0, "params", "post_detach_denial_receipt_posture"), DR_POSTURE),
    ),
    "spec/examples/content.import.receipt.removable-media-local-ingest.json": (
        (("execution", "post_detach_denial_receipt_posture"), DR_POSTURE),
        (("execution", "post_detach_denial_receipt_digest"), DR_DIGEST),
        (("execution", "post_detach_denial_receipt_schema"), SCHEMA_REL),
        (("execution", "post_detach_denial_receipt_negative_fixture_policy"), DR_POLICY),
        (("execution", "post_detach_denial_receipt_required"), True),
    ),
    "spec/examples/preopen.map.removable-media-local-ingest-post-detach.json": (
        (("denial_receipt_posture",), DR_POSTURE),
        (("denial_receipt_digest",), DR_DIGEST),
        (("denial_receipt_schema",), SCHEMA_REL),
        (("denial_receipt_negative_fixture_policy",), DR_POLICY),
        (("denial_receipt_required",), True),
    ),
}

SCHEMA_FIELDS = {
    SCHEMA_REL: (
        DR_KIND,
        "spec/removable.media.local.post_detach.denial.receipt.fixture.schema.json",
        "post-detach-denial-receipt-generic-runtime-schema-plus-exact-fixture-split",
        "deny-fail-closed-stale-authority",
        "deny-and-record-redacted-denial-receipt",
        "deny-digest-join-unless-new-authority-and-record",
        "redacted-denial-summary-visible-by-digest-and-reason-code",
        "bounded-retry-requires-fresh-lease-or-stays-denied",
    ),
    FIXTURE_SCHEMA_REL: (
        DR_KIND,
        DR_POSTURE,
        DR_DIGEST,
        DR_POLICY,
        "deny-fail-closed-stale-authority",
    ),
    TOMBSTONE_SCHEMA_REL: ("denial_receipt", DR_POSTURE, DR_POLICY, "silent_denial_without_receipt"),
    "spec/removable.media.local.post_detach.export.bundle.schema.json": ("denial_receipt", DR_POSTURE, DR_POLICY),
    "spec/removable.media.local.post_detach.query.projection.schema.json": ("denial_receipt", DR_POSTURE, DR_POLICY),
    "spec/removable.media.local.post_detach.recovery.evidence.schema.json": ("denial_receipt_posture", DR_POLICY),
    "spec/removable.media.local.post_detach.contract.schema.json": ("denial_receipt_posture", "denial_receipt_required", "silent_denial_without_receipt"),
    "spec/content.import.plan.schema.json": ("post_detach_denial_receipt_posture", "post_detach_denial_receipt_negative_fixture_policy"),
    "spec/content.import.receipt.schema.json": ("post_detach_denial_receipt_posture", "post_detach_denial_receipt_negative_fixture_policy"),
    "spec/preopen.map.schema.json": ("denial_receipt_posture", "denial_receipt_negative_fixture_policy"),
}

TEXT_REQUIREMENTS = {
    "docs/765-removable-media-local-fallback-post-detach-denial-receipts-are-typed-and-negative-tested.md": (DR_POSTURE, DR_DIGEST, DR_POLICY, SCHEMA_REL, EXAMPLE_REL, INVALID_DIR, "deny-fail-closed-stale-authority"),
    "adrs/ADR-0354-removable-media-local-fallback-post-detach-denial-receipts-are-typed-and-negative-tested.md": (DR_POSTURE, DR_DIGEST, DR_POLICY, SCHEMA_REL, INVALID_DIR),
    "docs/764-removable-media-local-fallback-post-detach-revocation-tombstones-are-typed-and-negative-tested.md": (DR_POSTURE, DR_DIGEST, DR_POLICY, SCHEMA_REL),
    "docs/763-removable-media-local-fallback-post-detach-export-bundles-are-redacted-and-negative-tested.md": (DR_POSTURE, DR_DIGEST),
    "docs/762-removable-media-local-fallback-post-detach-query-projection-is-typed-and-negative-tested.md": (DR_POSTURE, "redacted denial receipt"),
    "docs/293-attribute-indexed-metadata-and-live-queries.md": (DR_POSTURE, "stale-handle denial receipts"),
    "docs/266-open-questions-and-risk-register.md": (DR_POSTURE, DR_POLICY),
    "docs/98-archive-hygiene.md": ("check_removable_media_local_post_detach_denial_receipt.py", DR_POSTURE),
    "docs/99-llm-runbook.md": ("check_removable_media_local_post_detach_denial_receipt.py", DR_POSTURE),
    "docs/110-juicy-os-lessons.md": (DR_POSTURE, "deny-fail-closed-stale-authority"),
    "README.md": ("ADR-0354", DR_POSTURE),
    "docs/00-index.md": ("ADR-0354", "docs/765-removable-media-local-fallback-post-detach-denial-receipts-are-typed-and-negative-tested.md", DR_POSTURE),
    "CHANGELOG.md": ("2026-05-22r510", "2026-05-30r530", "check_removable_media_local_post_detach_denial_receipt.py", DR_POSTURE, "post-detach-denial-receipt-generic-runtime-schema-plus-exact-fixture-split"),
    "docs/785-removable-media-local-fallback-post-detach-terminal-closure-and-denial-receipt-schema-split.md": ("post-detach-denial-receipt-generic-runtime-schema-plus-exact-fixture-split", FIXTURE_SCHEMA_REL),
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

    if example["contract_binding"]["revocation_tombstone_digest"] != TOMBSTONE_DIGEST:
        fail(f"{EXAMPLE_REL} must bind the r509 tombstone digest {TOMBSTONE_DIGEST}")
    if example["denial_decision"]["offline_copy_erasure_claimed"] is not False:
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
    if "check_removable_media_local_post_detach_denial_receipt.py" not in hygiene:
        fail("tools/hygiene.py must include check_removable_media_local_post_detach_denial_receipt.py")

    print("removable-media post-detach denial-receipt check passed")


if __name__ == "__main__":
    main()
