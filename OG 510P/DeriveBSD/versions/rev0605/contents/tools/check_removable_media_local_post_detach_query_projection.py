#!/usr/bin/env python3
"""Guard removable-media post-detach query projection evidence.

The first host-local removable-media fallback must not let successful recovery
turn receipts into an ambient metadata/search surface. Query projection evidence
is typed, redacted, lease-bound, and negative-tested.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_REL = "spec/removable.media.local.post_detach.query.projection.schema.json"
FIXTURE_SCHEMA_REL = "spec/removable.media.local.post_detach.query.projection.fixture.schema.json"
EXAMPLE_REL = "spec/examples/removable.media.local.post_detach.query.projection.json"
INVALID_DIR = "spec/examples/invalid/removable-media/post-detach-query-projection"
QP_POSTURE = "typed-post-detach-query-projection-positive-and-negative-fixture-guarded"
QP_DIGEST = "sha256:5656565656565656565656565656565656565656565656565656565656565656"
QP_POLICY = "known-bad-query-projection-shapes-must-fail-validation"
QP_KIND = "removable.media.local.post_detach.query.projection"
RECOVERY_SCHEMA_REL = "spec/removable.media.local.post_detach.recovery.evidence.schema.json"
RECOVERY_FIXTURE_SCHEMA_REL = "spec/removable.media.local.post_detach.recovery.evidence.fixture.schema.json"
CONTRACT_SCHEMA_REL = "spec/removable.media.local.post_detach.contract.schema.json"

REQUIRED_INVALID_FIXTURES = {
    "query-without-lease.json",
    "raw-media-path-leaked.json",
    "observed-hints-indexed.json",
    "full-text-indexing-enabled.json",
    "host-identity-leaked.json",
    "live-subscription-open-ended.json",
    "retention-unbounded.json",
    "cross-lane-query-without-explicit-join.json",
    "filename-indexed.json",
}

JSON_REQUIREMENTS = {
    "spec/examples/removable.media.local.post_detach.recovery.evidence.json": (
        (("query_projection", "posture"), QP_POSTURE),
        (("query_projection", "kind"), QP_KIND),
        (("query_projection", "schema"), SCHEMA_REL),
        (("query_projection", "digest"), QP_DIGEST),
        (("query_projection", "negative_fixture_policy"), QP_POLICY),
        (("query_projection", "ambient_query_absent"), True),
    ),
    "spec/examples/removable.media.local.post_detach.contract.json": (
        (("backend_evidence", "query_projection_posture"), QP_POSTURE),
        (("backend_evidence", "query_projection_kind"), QP_KIND),
        (("backend_evidence", "query_projection_schema"), SCHEMA_REL),
        (("backend_evidence", "query_projection_digest"), QP_DIGEST),
        (("backend_evidence", "query_projection_negative_fixture_policy"), QP_POLICY),
        (("backend_evidence", "query_projection_required"), True),
    ),
    "spec/examples/content.import.plan.removable-media-local-ingest.json": (
        (("execution", "post_detach_query_projection_posture"), QP_POSTURE),
        (("execution", "post_detach_query_projection_digest"), QP_DIGEST),
        (("execution", "post_detach_query_projection_schema"), SCHEMA_REL),
        (("execution", "post_detach_query_projection_negative_fixture_policy"), QP_POLICY),
        (("execution", "post_detach_query_projection_required"), True),
        (("operations", 0, "params", "post_detach_query_projection_posture"), QP_POSTURE),
    ),
    "spec/examples/content.import.receipt.removable-media-local-ingest.json": (
        (("execution", "post_detach_query_projection_posture"), QP_POSTURE),
        (("execution", "post_detach_query_projection_digest"), QP_DIGEST),
        (("execution", "post_detach_query_projection_schema"), SCHEMA_REL),
        (("execution", "post_detach_query_projection_negative_fixture_policy"), QP_POLICY),
        (("execution", "post_detach_query_projection_required"), True),
    ),
    "spec/examples/preopen.map.removable-media-local-ingest-post-detach.json": (
        (("query_projection_posture",), QP_POSTURE),
        (("query_projection_digest",), QP_DIGEST),
        (("query_projection_schema",), SCHEMA_REL),
        (("query_projection_negative_fixture_policy",), QP_POLICY),
        (("query_projection_required",), True),
    ),
}

SCHEMA_FIELDS = {
    SCHEMA_REL: (
        "removable.media.local.post_detach.query.projection",
        "lease-required-no-ambient-index-read",
        "raw_media_hints_indexed",
        "original_media_path_indexed",
        "host_user_home",
        "body_text",
        "filename_untrusted_text",
        "cross_lane_join",
        "aggregate_counts",
    ),
    FIXTURE_SCHEMA_REL: (
        "removable.media.local.post_detach.query.projection",
        QP_POSTURE,
        QP_DIGEST,
        QP_POLICY,
        "lease-required-no-ambient-index-read",
    ),
    RECOVERY_SCHEMA_REL: (
        "query_projection",
        QP_POSTURE,
        "sha256Digest",
    ),
    RECOVERY_FIXTURE_SCHEMA_REL: (
        "query_projection",
        QP_POSTURE,
        QP_DIGEST,
    ),
    CONTRACT_SCHEMA_REL: (
        "query_projection_posture",
        "query_projection_digest",
        "query_projection_required",
    ),
    "spec/content.import.plan.schema.json": (
        "post_detach_query_projection_posture",
        "post_detach_query_projection_digest",
        "post_detach_query_projection_schema",
        "post_detach_query_projection_negative_fixture_policy",
    ),
    "spec/content.import.receipt.schema.json": (
        "post_detach_query_projection_posture",
        "post_detach_query_projection_digest",
        "post_detach_query_projection_schema",
        "post_detach_query_projection_negative_fixture_policy",
    ),
    "spec/preopen.map.schema.json": (
        "query_projection_posture",
        "query_projection_digest",
        "query_projection_schema",
        "query_projection_negative_fixture_policy",
    ),
}

TEXT_REQUIREMENTS = {
    "docs/762-removable-media-local-fallback-post-detach-query-projection-is-typed-and-negative-tested.md": (
        QP_POSTURE,
        QP_DIGEST,
        QP_POLICY,
        SCHEMA_REL,
        EXAMPLE_REL,
        INVALID_DIR,
        "lease-required-no-ambient-index-read",
        "raw media paths",
    ),
    "adrs/ADR-0351-removable-media-local-fallback-post-detach-query-projection-is-typed-and-negative-tested.md": (
        QP_POSTURE,
        QP_DIGEST,
        QP_POLICY,
        SCHEMA_REL,
        INVALID_DIR,
    ),
    "docs/761-removable-media-local-fallback-post-detach-recovery-evidence-is-typed-and-negative-tested.md": (
        QP_POSTURE,
        QP_DIGEST,
        SCHEMA_REL,
    ),
    "docs/293-attribute-indexed-metadata-and-live-queries.md": (
        QP_POSTURE,
        "lease-required-no-ambient-index-read",
        "derived-snapshot-not-authority",
    ),
    "docs/98-archive-hygiene.md": (
        "check_removable_media_local_post_detach_query_projection.py",
        QP_POSTURE,
    ),
    "docs/99-llm-runbook.md": (
        "check_removable_media_local_post_detach_query_projection.py",
        QP_POSTURE,
    ),
    "docs/266-open-questions-and-risk-register.md": (
        QP_POSTURE,
        QP_POLICY,
    ),
    "README.md": (
        "ADR-0351",
        QP_POSTURE,
    ),
    "docs/00-index.md": (
        "ADR-0351",
        "docs/762-removable-media-local-fallback-post-detach-query-projection-is-typed-and-negative-tested.md",
        QP_POSTURE,
    ),
    "CHANGELOG.md": (
        "2026-05-21r507",
        "check_removable_media_local_post_detach_query_projection.py",
        QP_POSTURE,
    ),
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
    fixture_schema = load_json(FIXTURE_SCHEMA_REL)
    example = load_json(EXAMPLE_REL)
    validator = Draft202012Validator(schema)
    fixture_validator = Draft202012Validator(fixture_schema)

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
    if "allOf" not in fixture_schema:
        fail(f"{FIXTURE_SCHEMA_REL} must preserve the exact historical fixture schema under allOf")

    invalid_dir = ROOT / INVALID_DIR
    observed = {p.name for p in invalid_dir.glob("*.json")}
    missing = sorted(REQUIRED_INVALID_FIXTURES - observed)
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

    print("removable-media post-detach query-projection check passed")


if __name__ == "__main__":
    main()
