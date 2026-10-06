#!/usr/bin/env python3
"""Guardrail for removable-media post-detach revocation tombstones.

Revocation is authority, not cleanup folklore. Stale query/export/rehydration
handles must fail after an exact-subject tombstone, while the receipt must not
claim impossible erasure of unmanaged offline copies.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_REL = "spec/removable.media.local.post_detach.revocation.tombstone.schema.json"
FIXTURE_SCHEMA_REL = "spec/removable.media.local.post_detach.revocation.tombstone.fixture.schema.json"
EXAMPLE_REL = "spec/examples/removable.media.local.post_detach.revocation.tombstone.json"
INVALID_DIR = "spec/examples/invalid/removable-media/post-detach-revocation-tombstone"
RT_POSTURE = "typed-post-detach-revocation-tombstone-positive-and-negative-fixture-guarded"
RT_DIGEST = "sha256:6666666666666666666666666666666666666666666666666666666666666666"
RT_POLICY = "known-bad-post-detach-revocation-tombstone-shapes-must-fail-validation"
RT_KIND = "removable.media.local.post_detach.revocation.tombstone"
EXPORT_SCHEMA_REL = "spec/removable.media.local.post_detach.export.bundle.schema.json"
EXPORT_EXAMPLE_REL = "spec/examples/removable.media.local.post_detach.export.bundle.json"
EXPORT_DIGEST = "sha256:6262626262626262626262626262626262626262626262626262626262626262"

REQUIRED_INVALID_FIXTURES = {
    "query-after-tombstone.json",
    "export-after-tombstone.json",
    "rehydration-after-tombstone.json",
    "pattern-prefix-revocation.json",
    "raw-locator-included.json",
    "offline-erasure-claimed.json",
    "missing-deletion-receipt.json",
    "unbounded-retention.json",
    "secret-material-present.json",
    "successor-without-fresh-lease.json",
}

JSON_REQUIREMENTS = {
    EXPORT_EXAMPLE_REL: (
        (("revocation_tombstone", "posture"), RT_POSTURE),
        (("revocation_tombstone", "kind"), RT_KIND),
        (("revocation_tombstone", "schema"), SCHEMA_REL),
        (("revocation_tombstone", "digest"), RT_DIGEST),
        (("revocation_tombstone", "negative_fixture_policy"), RT_POLICY),
        (("revocation_tombstone", "revocation_check_required"), True),
        (("revocation_tombstone", "offline_copy_claim"), "not-claimed-erased-only-future-authority-denied"),
        (("failure_policy", "stale_handle_after_tombstone"), "fail-closed"),
    ),
    "spec/examples/removable.media.local.post_detach.query.projection.json": (
        (("revocation_tombstone", "posture"), RT_POSTURE),
        (("revocation_tombstone", "kind"), RT_KIND),
        (("revocation_tombstone", "schema"), SCHEMA_REL),
        (("revocation_tombstone", "digest"), RT_DIGEST),
        (("revocation_tombstone", "negative_fixture_policy"), RT_POLICY),
        (("revocation_tombstone", "query_after_tombstone"), "deny-stale-handle-fail-closed"),
        (("failure_policy", "query_after_tombstone"), "fail-closed"),
    ),
    "spec/examples/removable.media.local.post_detach.recovery.evidence.json": (
        (("query_projection", "revocation_tombstone_posture"), RT_POSTURE),
        (("query_projection", "revocation_tombstone_kind"), RT_KIND),
        (("query_projection", "revocation_tombstone_schema"), SCHEMA_REL),
        (("query_projection", "revocation_tombstone_digest"), RT_DIGEST),
        (("query_projection", "revocation_tombstone_negative_fixture_policy"), RT_POLICY),
        (("query_projection", "revocation_tombstone_required"), True),
    ),
    "spec/examples/removable.media.local.post_detach.contract.json": (
        (("backend_evidence", "revocation_tombstone_posture"), RT_POSTURE),
        (("backend_evidence", "revocation_tombstone_kind"), RT_KIND),
        (("backend_evidence", "revocation_tombstone_schema"), SCHEMA_REL),
        (("backend_evidence", "revocation_tombstone_digest"), RT_DIGEST),
        (("backend_evidence", "revocation_tombstone_negative_fixture_policy"), RT_POLICY),
        (("backend_evidence", "revocation_tombstone_required"), True),
        (("failure_policy", "stale_query_or_export_after_tombstone"), "fail-closed"),
    ),
    "spec/examples/content.import.plan.removable-media-local-ingest.json": (
        (("execution", "post_detach_revocation_tombstone_posture"), RT_POSTURE),
        (("execution", "post_detach_revocation_tombstone_digest"), RT_DIGEST),
        (("execution", "post_detach_revocation_tombstone_schema"), SCHEMA_REL),
        (("execution", "post_detach_revocation_tombstone_negative_fixture_policy"), RT_POLICY),
        (("execution", "post_detach_revocation_tombstone_required"), True),
        (("operations", 0, "params", "post_detach_revocation_tombstone_posture"), RT_POSTURE),
    ),
    "spec/examples/content.import.receipt.removable-media-local-ingest.json": (
        (("execution", "post_detach_revocation_tombstone_posture"), RT_POSTURE),
        (("execution", "post_detach_revocation_tombstone_digest"), RT_DIGEST),
        (("execution", "post_detach_revocation_tombstone_schema"), SCHEMA_REL),
        (("execution", "post_detach_revocation_tombstone_negative_fixture_policy"), RT_POLICY),
        (("execution", "post_detach_revocation_tombstone_required"), True),
    ),
    "spec/examples/preopen.map.removable-media-local-ingest-post-detach.json": (
        (("revocation_tombstone_posture",), RT_POSTURE),
        (("revocation_tombstone_digest",), RT_DIGEST),
        (("revocation_tombstone_schema",), SCHEMA_REL),
        (("revocation_tombstone_negative_fixture_policy",), RT_POLICY),
        (("revocation_tombstone_required",), True),
    ),
}

SCHEMA_FIELDS = {
    SCHEMA_REL: (
        RT_KIND,
        "same-surface-explicit-revocation-or-expiry-no-ambient-cleanup",
        "exact-digest-subjects-only-no-pattern-or-prefix-revocation",
        "deny-stale-handle-fail-closed",
        "deny-digest-join-unless-new-authority",
        "not-claimed-erased-only-future-authority-denied",
        "tombstone-removes-future-authority-not-historical-existence",
        "spec/removable.media.local.post_detach.revocation.tombstone.fixture.schema.json",
    ),
    EXPORT_SCHEMA_REL: (
        "revocation_tombstone",
        RT_POSTURE,
        RT_DIGEST,
        RT_POLICY,
        "stale_handle_after_tombstone",
    ),
    "spec/removable.media.local.post_detach.query.projection.schema.json": (
        "revocation_tombstone",
        RT_POSTURE,
        RT_DIGEST,
        RT_POLICY,
        "query_after_tombstone",
    ),
    "spec/removable.media.local.post_detach.recovery.evidence.schema.json": (
        "revocation_tombstone_posture",
        RT_POSTURE,
        RT_POLICY,
        "sha256Digest",
    ),
    "spec/removable.media.local.post_detach.recovery.evidence.fixture.schema.json": (
        "revocation_tombstone_posture",
        RT_DIGEST,
        RT_POLICY,
    ),
    "spec/removable.media.local.post_detach.contract.schema.json": (
        "revocation_tombstone_posture",
        "revocation_tombstone_required",
        "stale_query_or_export_after_tombstone",
    ),
    "spec/content.import.plan.schema.json": (
        "post_detach_revocation_tombstone_posture",
        "post_detach_revocation_tombstone_negative_fixture_policy",
    ),
    "spec/content.import.receipt.schema.json": (
        "post_detach_revocation_tombstone_posture",
        "post_detach_revocation_tombstone_negative_fixture_policy",
    ),
    "spec/preopen.map.schema.json": (
        "revocation_tombstone_posture",
        "revocation_tombstone_negative_fixture_policy",
    ),
}

TEXT_REQUIREMENTS = {
    "docs/764-removable-media-local-fallback-post-detach-revocation-tombstones-are-typed-and-negative-tested.md": (
        RT_POSTURE,
        RT_DIGEST,
        RT_POLICY,
        SCHEMA_REL,
        EXAMPLE_REL,
        INVALID_DIR,
        "not-claimed-erased-only-future-authority-denied",
    ),
    "adrs/ADR-0353-removable-media-local-fallback-post-detach-revocation-tombstones-are-typed-and-negative-tested.md": (
        RT_POSTURE,
        RT_DIGEST,
        RT_POLICY,
        SCHEMA_REL,
        INVALID_DIR,
    ),
    "docs/763-removable-media-local-fallback-post-detach-export-bundles-are-redacted-and-negative-tested.md": (
        RT_POSTURE,
        RT_DIGEST,
        RT_POLICY,
        SCHEMA_REL,
    ),
    "docs/762-removable-media-local-fallback-post-detach-query-projection-is-typed-and-negative-tested.md": (
        RT_POSTURE,
        "deny-stale-handle-fail-closed",
    ),
    "docs/293-attribute-indexed-metadata-and-live-queries.md": (
        RT_POSTURE,
        "stale query handles",
    ),
    "docs/266-open-questions-and-risk-register.md": (
        RT_POSTURE,
        RT_POLICY,
    ),
    "docs/98-archive-hygiene.md": (
        "check_removable_media_local_post_detach_revocation_tombstone.py",
        RT_POSTURE,
    ),
    "docs/99-llm-runbook.md": (
        "check_removable_media_local_post_detach_revocation_tombstone.py",
        RT_POSTURE,
    ),
    "docs/110-juicy-os-lessons.md": (
        RT_POSTURE,
        "not-claimed-erased-only-future-authority-denied",
    ),
    "README.md": (
        "ADR-0353",
        RT_POSTURE,
    ),
    "docs/00-index.md": (
        "ADR-0353",
        "docs/764-removable-media-local-fallback-post-detach-revocation-tombstones-are-typed-and-negative-tested.md",
        RT_POSTURE,
    ),
    "CHANGELOG.md": (
        "2026-05-21r509",
        "2026-05-30r529",
        "check_removable_media_local_post_detach_revocation_tombstone.py",
        RT_POSTURE,
        "post-detach-revocation-tombstone-generic-runtime-schema-plus-exact-fixture-split",
    ),
    "docs/784-removable-media-local-fallback-post-detach-export-bundle-deletion-and-revocation-tombstone-schema-split.md": (
        "post-detach-revocation-tombstone-generic-runtime-schema-plus-exact-fixture-split",
        "spec/removable.media.local.post_detach.revocation.tombstone.fixture.schema.json",
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

    if example["contract_binding"]["export_bundle_digest"] != EXPORT_DIGEST:
        fail(f"{EXAMPLE_REL} must bind the r508 export bundle digest {EXPORT_DIGEST}")
    if example["effect"]["offline_copy_claim"] != "not-claimed-erased-only-future-authority-denied":
        fail(f"{EXAMPLE_REL} must not claim external offline copy erasure")

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

    hygiene = (ROOT / "tools" / "hygiene.py").read_text(encoding="utf-8")
    if "check_removable_media_local_post_detach_revocation_tombstone.py" not in hygiene:
        fail("tools/hygiene.py must include check_removable_media_local_post_detach_revocation_tombstone.py")

    print("removable-media post-detach revocation-tombstone check passed")


if __name__ == "__main__":
    main()
