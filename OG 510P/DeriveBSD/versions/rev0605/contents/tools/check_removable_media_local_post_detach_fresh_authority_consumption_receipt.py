#!/usr/bin/env python3
"""Validate removable-media post-detach fresh-authority consumption receipts.

This guardrail keeps r512 from turning a fresh-authority receipt into a reusable
renewal token. Reissued post-tombstone authority must be consumed once, bound to
exact successor artifacts, and redacted like the rest of the post-detach chain.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_REL = 'spec/removable.media.local.post_detach.fresh.authority.consumption.receipt.schema.json'
FIXTURE_SCHEMA_REL = 'spec/removable.media.local.post_detach.fresh.authority.consumption.receipt.fixture.schema.json'
EXAMPLE_REL = 'spec/examples/removable.media.local.post_detach.fresh.authority.consumption.receipt.json'
INVALID_DIR = 'spec/examples/invalid/removable-media/post-detach-fresh-authority-consumption-receipt'
C_KIND = 'removable.media.local.post_detach.fresh.authority.consumption.receipt'
C_POSTURE = 'typed-post-detach-fresh-authority-consumption-positive-and-negative-fixture-guarded'
C_DIGEST = 'sha256:a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4'
C_POLICY = 'known-bad-post-detach-fresh-authority-consumption-shapes-must-fail-validation'
FRESH_DIGEST = 'sha256:7171717171717171717171717171717171717171717171717171717171717171'
LEASE_DIGEST = 'sha256:7272727272727272727272727272727272727272727272727272727272727272'
REQUIRED_INVALID_FIXTURES = ['broad-successor-scope.json', 'double-spend-allowed.json', 'lease-reuse-allowed.json', 'missing-consumed-marker.json', 'missing-fresh-authority-receipt.json', 'missing-successor-index-update.json', 'offline-erasure-claimed.json', 'pattern-successor-subject.json', 'raw-locator-included.json', 'secret-material-present.json', 'tombstone-mutated.json']

JSON_REQUIREMENTS = {
    "spec/examples/removable.media.local.post_detach.fresh.authority.receipt.json": (
        (("consumption_receipt", "posture"), C_POSTURE),
        (("consumption_receipt", "kind"), C_KIND),
        (("consumption_receipt", "schema"), SCHEMA_REL),
        (("consumption_receipt", "digest"), C_DIGEST),
        (("consumption_receipt", "negative_fixture_policy"), C_POLICY),
        (("consumption_receipt", "one_shot_consumption"), True),
    ),
    "spec/examples/removable.media.local.post_detach.denial.receipt.json": ((("fresh_authority", "consumption_receipt", "posture"), C_POSTURE), (("fresh_authority", "consumption_receipt", "digest"), C_DIGEST)),
    "spec/examples/removable.media.local.post_detach.revocation.tombstone.json": ((("fresh_authority", "consumption_receipt", "posture"), C_POSTURE), (("fresh_authority", "consumption_receipt", "digest"), C_DIGEST)),
    "spec/examples/removable.media.local.post_detach.export.bundle.json": ((("fresh_authority", "consumption_receipt", "posture"), C_POSTURE), (("fresh_authority", "consumption_receipt", "digest"), C_DIGEST)),
    "spec/examples/removable.media.local.post_detach.query.projection.json": ((("fresh_authority", "consumption_receipt", "posture"), C_POSTURE), (("fresh_authority", "consumption_receipt", "digest"), C_DIGEST)),
    "spec/examples/removable.media.local.post_detach.recovery.evidence.json": (
        (("query_projection", "fresh_authority_consumption_posture"), C_POSTURE),
        (("query_projection", "fresh_authority_consumption_kind"), C_KIND),
        (("query_projection", "fresh_authority_consumption_schema"), SCHEMA_REL),
        (("query_projection", "fresh_authority_consumption_digest"), C_DIGEST),
        (("query_projection", "fresh_authority_consumption_negative_fixture_policy"), C_POLICY),
        (("query_projection", "fresh_authority_consumption_required"), True),
    ),
    "spec/examples/removable.media.local.post_detach.contract.json": (
        (("backend_evidence", "fresh_authority_consumption_posture"), C_POSTURE),
        (("backend_evidence", "fresh_authority_consumption_kind"), C_KIND),
        (("backend_evidence", "fresh_authority_consumption_schema"), SCHEMA_REL),
        (("backend_evidence", "fresh_authority_consumption_digest"), C_DIGEST),
        (("backend_evidence", "fresh_authority_consumption_negative_fixture_policy"), C_POLICY),
        (("backend_evidence", "fresh_authority_consumption_required"), True),
        (("failure_policy", "fresh_authority_reuse_without_consumption_receipt"), "fail-closed"),
    ),
    "spec/examples/content.import.plan.removable-media-local-ingest.json": (
        (("execution", "post_detach_fresh_authority_consumption_posture"), C_POSTURE),
        (("execution", "post_detach_fresh_authority_consumption_digest"), C_DIGEST),
        (("execution", "post_detach_fresh_authority_consumption_schema"), SCHEMA_REL),
        (("execution", "post_detach_fresh_authority_consumption_negative_fixture_policy"), C_POLICY),
        (("execution", "post_detach_fresh_authority_consumption_required"), True),
        (("operations", 0, "params", "post_detach_fresh_authority_consumption_posture"), C_POSTURE),
    ),
    "spec/examples/content.import.receipt.removable-media-local-ingest.json": (
        (("execution", "post_detach_fresh_authority_consumption_posture"), C_POSTURE),
        (("execution", "post_detach_fresh_authority_consumption_digest"), C_DIGEST),
        (("execution", "post_detach_fresh_authority_consumption_schema"), SCHEMA_REL),
        (("execution", "post_detach_fresh_authority_consumption_negative_fixture_policy"), C_POLICY),
        (("execution", "post_detach_fresh_authority_consumption_required"), True),
    ),
    "spec/examples/preopen.map.removable-media-local-ingest-post-detach.json": (
        (("fresh_authority_consumption_posture",), C_POSTURE),
        (("fresh_authority_consumption_digest",), C_DIGEST),
        (("fresh_authority_consumption_schema",), SCHEMA_REL),
        (("fresh_authority_consumption_negative_fixture_policy",), C_POLICY),
        (("fresh_authority_consumption_required",), True),
    ),
}

SCHEMA_FIELDS = {
    SCHEMA_REL: (C_KIND, "single-consumption", "fresh-authority-consumed-once-successor-artifacts-bound", "lease_reuse_or_double_spend", "successor_scope_broadened", "fresh-authority-consumption-generic-runtime-schema-plus-exact-fixture-split", "sha256Digest"),
    FIXTURE_SCHEMA_REL: ("allOf", "const", C_DIGEST, "historical literal regression surface"),
    "spec/removable.media.local.post_detach.fresh.authority.receipt.schema.json": ("consumption_receipt", C_POSTURE, C_DIGEST, C_POLICY),
    "spec/removable.media.local.post_detach.denial.receipt.schema.json": ("consumption_receipt", C_POSTURE, C_DIGEST, C_POLICY),
    "spec/removable.media.local.post_detach.revocation.tombstone.schema.json": ("consumption_receipt", C_POSTURE, C_DIGEST, C_POLICY),
    "spec/removable.media.local.post_detach.export.bundle.schema.json": ("consumption_receipt", C_POSTURE, C_DIGEST, C_POLICY),
    "spec/removable.media.local.post_detach.query.projection.schema.json": ("consumption_receipt", C_POSTURE, C_DIGEST, C_POLICY),
    "spec/removable.media.local.post_detach.recovery.evidence.schema.json": ("fresh_authority_consumption_posture", C_POSTURE, C_POLICY, "sha256Digest"),
    "spec/removable.media.local.post_detach.recovery.evidence.fixture.schema.json": ("fresh_authority_consumption_posture", C_DIGEST, C_POLICY),
    "spec/removable.media.local.post_detach.contract.schema.json": ("fresh_authority_consumption_posture", "fresh_authority_reuse_without_consumption_receipt"),
    "spec/content.import.plan.schema.json": ("post_detach_fresh_authority_consumption_posture", "post_detach_fresh_authority_consumption_negative_fixture_policy"),
    "spec/content.import.receipt.schema.json": ("post_detach_fresh_authority_consumption_posture", "post_detach_fresh_authority_consumption_negative_fixture_policy"),
    "spec/preopen.map.schema.json": ("fresh_authority_consumption_posture", "fresh_authority_consumption_negative_fixture_policy"),
}

TEXT_REQUIREMENTS = {
    "docs/767-removable-media-local-fallback-post-detach-fresh-authority-consumption-is-typed-and-negative-tested.md": (C_POSTURE, C_DIGEST, C_POLICY, SCHEMA_REL, FIXTURE_SCHEMA_REL, EXAMPLE_REL, INVALID_DIR, "fresh-authority-consumed-once-successor-artifacts-bound"),
    "adrs/ADR-0356-removable-media-local-fallback-post-detach-fresh-authority-consumption-is-typed-and-negative-tested.md": (C_POSTURE, C_DIGEST, C_POLICY, SCHEMA_REL, FIXTURE_SCHEMA_REL, INVALID_DIR),
    "docs/766-removable-media-local-fallback-post-detach-fresh-authority-reissue-is-typed-and-negative-tested.md": (C_POSTURE, C_DIGEST, "one-shot"),
    "docs/293-attribute-indexed-metadata-and-live-queries.md": (C_POSTURE, "fresh-authority consumption"),
    "docs/266-open-questions-and-risk-register.md": (C_POSTURE, C_POLICY),
    "docs/98-archive-hygiene.md": ("check_removable_media_local_post_detach_fresh_authority_consumption_receipt.py", C_POSTURE),
    "docs/99-llm-runbook.md": ("check_removable_media_local_post_detach_fresh_authority_consumption_receipt.py", C_POSTURE),
    "docs/110-juicy-os-lessons.md": (C_POSTURE, "fresh-authority-consumed-once-successor-artifacts-bound"),
    "README.md": ("ADR-0356", C_POSTURE),
    "docs/00-index.md": ("ADR-0356", "docs/767-removable-media-local-fallback-post-detach-fresh-authority-consumption-is-typed-and-negative-tested.md", C_POSTURE),
    "CHANGELOG.md": ("2026-05-22r512", "check_removable_media_local_post_detach_fresh_authority_consumption_receipt.py", C_POSTURE),
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
        fail(f"{EXAMPLE_REL} must validate against exact fixture schema {FIXTURE_SCHEMA_REL}: {fixture_errs[:10]}")

    if schema.get("additionalProperties") is not False:
        fail(f"{SCHEMA_REL} must be closed-world at the root")
    schema_text = (ROOT / SCHEMA_REL).read_text(encoding="utf-8")
    if schema_text.count('\"const\"') > 50 or '\"$defs\"' not in schema_text:
        fail(f"{SCHEMA_REL} must stay generic runtime-shaped after the fixture split")
    if example["consumed_authority"]["fresh_authority_receipt_digest"] != FRESH_DIGEST:
        fail(f"{EXAMPLE_REL} must consume fresh-authority digest {FRESH_DIGEST}")
    if example["consumed_authority"]["fresh_lease_digest"] != LEASE_DIGEST:
        fail(f"{EXAMPLE_REL} must consume fresh lease digest {LEASE_DIGEST}")
    if example["consumed_authority"]["lease_reuse_allowed"] is not False:
        fail(f"{EXAMPLE_REL} must reject fresh-authority lease reuse")
    if example["consumption_decision"]["fresh_authority_consumed_once"] is not True:
        fail(f"{EXAMPLE_REL} must record one-shot consumption")
    if example["consumption_decision"]["double_spend_allowed"] is not False:
        fail(f"{EXAMPLE_REL} must reject double-spend/reuse")

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
    if "check_removable_media_local_post_detach_fresh_authority_consumption_receipt.py" not in hygiene:
        fail("tools/hygiene.py must include check_removable_media_local_post_detach_fresh_authority_consumption_receipt.py")

    print("removable-media post-detach fresh-authority consumption receipt check passed")


if __name__ == "__main__":
    main()
