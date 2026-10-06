#!/usr/bin/env python3
"""Guard removable-media post-detach export/debug bundles.

The first host-local removable-media fallback must not reintroduce raw receipt,
path, filename, device, host-identity, body-text, or secret exposure through a
support/debug bundle after query projection has deliberately redacted it.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_REL = "spec/removable.media.local.post_detach.export.bundle.schema.json"
FIXTURE_SCHEMA_REL = "spec/removable.media.local.post_detach.export.bundle.fixture.schema.json"
EXAMPLE_REL = "spec/examples/removable.media.local.post_detach.export.bundle.json"
INVALID_DIR = "spec/examples/invalid/removable-media/post-detach-export-bundle"
EB_POSTURE = "typed-post-detach-export-bundle-positive-and-negative-fixture-guarded"
EB_DIGEST = "sha256:6262626262626262626262626262626262626262626262626262626262626262"
EB_POLICY = "known-bad-post-detach-export-bundle-shapes-must-fail-validation"
EB_KIND = "removable.media.local.post_detach.export.bundle"
QP_SCHEMA_REL = "spec/removable.media.local.post_detach.query.projection.schema.json"
QP_EXAMPLE_REL = "spec/examples/removable.media.local.post_detach.query.projection.json"
QP_DIGEST = "sha256:5656565656565656565656565656565656565656565656565656565656565656"

REQUIRED_INVALID_FIXTURES = {
    "export-without-approval.json",
    "raw-media-path-included.json",
    "raw-receipt-payload-included.json",
    "host-identity-included.json",
    "untrusted-filename-included.json",
    "body-text-included.json",
    "recipient-unbound.json",
    "retention-unbounded.json",
    "live-locator-present.json",
    "secret-material-included.json",
}

JSON_REQUIREMENTS = {
    QP_EXAMPLE_REL: (
        (("export_bundle", "posture"), EB_POSTURE),
        (("export_bundle", "kind"), EB_KIND),
        (("export_bundle", "schema"), SCHEMA_REL),
        (("export_bundle", "digest"), EB_DIGEST),
        (("export_bundle", "negative_fixture_policy"), EB_POLICY),
        (("export_bundle", "raw_export_forbidden"), True),
        (("export_policy", "export_bundle_posture"), EB_POSTURE),
        (("export_policy", "raw_debug_bundle_export"), "forbidden"),
    ),
    "spec/examples/removable.media.local.post_detach.recovery.evidence.json": (
        (("query_projection", "export_bundle_posture"), EB_POSTURE),
        (("query_projection", "export_bundle_schema"), SCHEMA_REL),
        (("query_projection", "export_bundle_digest"), EB_DIGEST),
        (("query_projection", "export_bundle_negative_fixture_policy"), EB_POLICY),
        (("query_projection", "raw_export_forbidden"), True),
    ),
    "spec/examples/removable.media.local.post_detach.contract.json": (
        (("backend_evidence", "export_bundle_posture"), EB_POSTURE),
        (("backend_evidence", "export_bundle_kind"), EB_KIND),
        (("backend_evidence", "export_bundle_schema"), SCHEMA_REL),
        (("backend_evidence", "export_bundle_digest"), EB_DIGEST),
        (("backend_evidence", "export_bundle_negative_fixture_policy"), EB_POLICY),
        (("backend_evidence", "export_bundle_required"), True),
        (("failure_policy", "raw_debug_bundle_export"), "fail-closed"),
    ),
    "spec/examples/content.import.plan.removable-media-local-ingest.json": (
        (("execution", "post_detach_export_bundle_posture"), EB_POSTURE),
        (("execution", "post_detach_export_bundle_digest"), EB_DIGEST),
        (("execution", "post_detach_export_bundle_schema"), SCHEMA_REL),
        (("execution", "post_detach_export_bundle_negative_fixture_policy"), EB_POLICY),
        (("execution", "post_detach_export_bundle_required"), True),
        (("operations", 0, "params", "post_detach_export_bundle_posture"), EB_POSTURE),
    ),
    "spec/examples/content.import.receipt.removable-media-local-ingest.json": (
        (("execution", "post_detach_export_bundle_posture"), EB_POSTURE),
        (("execution", "post_detach_export_bundle_digest"), EB_DIGEST),
        (("execution", "post_detach_export_bundle_schema"), SCHEMA_REL),
        (("execution", "post_detach_export_bundle_negative_fixture_policy"), EB_POLICY),
        (("execution", "post_detach_export_bundle_required"), True),
    ),
    "spec/examples/preopen.map.removable-media-local-ingest-post-detach.json": (
        (("export_bundle_posture",), EB_POSTURE),
        (("export_bundle_digest",), EB_DIGEST),
        (("export_bundle_schema",), SCHEMA_REL),
        (("export_bundle_negative_fixture_policy",), EB_POLICY),
        (("export_bundle_required",), True),
    ),
}

SCHEMA_FIELDS = {
    SCHEMA_REL: (
        EB_KIND,
        "explicit-human-approved-export-no-ambient-debug-dump",
        "export-starts-from-redacted-query-projection-not-raw-receipts",
        "raw_authoritative_receipts_included",
        "raw_media_paths",
        "host_identity",
        "filename_untrusted_text",
        "body_text",
        "recipient-digest-required",
        "bounded-explicit-expiry",
        "spec/removable.media.local.post_detach.export.bundle.fixture.schema.json",
    ),
    QP_SCHEMA_REL: (
        "export_bundle",
        EB_POSTURE,
        EB_DIGEST,
        EB_POLICY,
        "raw_debug_bundle_export",
    ),
    "spec/removable.media.local.post_detach.recovery.evidence.schema.json": (
        "export_bundle_posture",
        EB_DIGEST,
        EB_POLICY,
    ),
    "spec/removable.media.local.post_detach.contract.schema.json": (
        "export_bundle_posture",
        "export_bundle_required",
        "raw_debug_bundle_export",
    ),
    "spec/content.import.plan.schema.json": (
        "post_detach_export_bundle_posture",
        "post_detach_export_bundle_negative_fixture_policy",
    ),
    "spec/content.import.receipt.schema.json": (
        "post_detach_export_bundle_posture",
        "post_detach_export_bundle_negative_fixture_policy",
    ),
    "spec/preopen.map.schema.json": (
        "export_bundle_posture",
        "export_bundle_negative_fixture_policy",
    ),
}

TEXT_REQUIREMENTS = {
    "docs/763-removable-media-local-fallback-post-detach-export-bundles-are-redacted-and-negative-tested.md": (
        EB_POSTURE,
        EB_DIGEST,
        EB_POLICY,
        SCHEMA_REL,
        EXAMPLE_REL,
        INVALID_DIR,
        "explicit-human-approved-export-no-ambient-debug-dump",
        "raw debug bundle",
    ),
    "docs/783-removable-media-local-fallback-post-detach-export-bundle-access-and-schema-split.md": (
        "post-detach-export-bundle-generic-runtime-schema-plus-exact-fixture-split",
        "spec/removable.media.local.post_detach.export.bundle.fixture.schema.json",
    ),
    "adrs/ADR-0352-removable-media-local-fallback-post-detach-export-bundles-are-redacted-and-negative-tested.md": (
        EB_POSTURE,
        EB_DIGEST,
        EB_POLICY,
        SCHEMA_REL,
        INVALID_DIR,
    ),
    "docs/762-removable-media-local-fallback-post-detach-query-projection-is-typed-and-negative-tested.md": (
        EB_POSTURE,
        EB_DIGEST,
        EB_POLICY,
        SCHEMA_REL,
    ),
    "docs/293-attribute-indexed-metadata-and-live-queries.md": (
        EB_POSTURE,
        "raw debug bundles",
    ),
    "docs/266-open-questions-and-risk-register.md": (
        EB_POSTURE,
        EB_POLICY,
    ),
    "docs/98-archive-hygiene.md": (
        "check_removable_media_local_post_detach_export_bundle.py",
        EB_POSTURE,
    ),
    "docs/99-llm-runbook.md": (
        "check_removable_media_local_post_detach_export_bundle.py",
        EB_POSTURE,
    ),
    "docs/110-juicy-os-lessons.md": (
        EB_POSTURE,
        "raw debug bundle",
    ),
    "docs/783-removable-media-local-fallback-post-detach-export-bundle-access-and-schema-split.md": (
        "post-detach-export-bundle-generic-runtime-schema-plus-exact-fixture-split",
        "spec/removable.media.local.post_detach.export.bundle.fixture.schema.json",
    ),
    "README.md": (
        "ADR-0352",
        EB_POSTURE,
    ),
    "docs/00-index.md": (
        "ADR-0352",
        "docs/763-removable-media-local-fallback-post-detach-export-bundles-are-redacted-and-negative-tested.md",
        EB_POSTURE,
    ),
    "CHANGELOG.md": (
        "2026-05-21r508",
        "check_removable_media_local_post_detach_export_bundle.py",
        EB_POSTURE,
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
        fail(f"{EXAMPLE_REL} must validate against {FIXTURE_SCHEMA_REL}: {fixture_errs[:10]}")

    if schema.get("additionalProperties") is not False:
        fail(f"{SCHEMA_REL} must be closed-world at the root")

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

    # The export bundle must start from the redacted projection, not invent a new digest.
    if example["source_projection"]["query_projection_digest"] != QP_DIGEST:
        fail(f"{EXAMPLE_REL} source_projection.query_projection_digest must equal {QP_DIGEST}")

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
    if "check_removable_media_local_post_detach_export_bundle.py" not in hygiene:
        fail("tools/hygiene.py must include check_removable_media_local_post_detach_export_bundle.py")

    print("removable-media post-detach export-bundle check passed")


if __name__ == "__main__":
    main()
