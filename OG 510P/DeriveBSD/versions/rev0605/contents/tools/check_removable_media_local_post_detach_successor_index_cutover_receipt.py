#!/usr/bin/env python3
"""Validate removable-media post-detach successor-index cutover receipts.

This guardrail keeps r513 from treating the r512 successor-index update as an
untyped digest. Fresh-authority consumption must be followed by a typed cutover
receipt that makes old handles terminal, activates only exact successor rows,
and preserves redaction.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_REL = 'spec/removable.media.local.post_detach.successor.index.cutover.receipt.schema.json'
FIXTURE_SCHEMA_REL = 'spec/removable.media.local.post_detach.successor.index.cutover.receipt.fixture.schema.json'
EXAMPLE_REL = 'spec/examples/removable.media.local.post_detach.successor.index.cutover.receipt.json'
INVALID_DIR = 'spec/examples/invalid/removable-media/post-detach-successor-index-cutover-receipt'
C_KIND = 'removable.media.local.post_detach.successor.index.cutover.receipt'
C_POSTURE = 'typed-post-detach-successor-index-cutover-positive-and-negative-fixture-guarded'
C_DIGEST = 'sha256:b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3'
C_POLICY = 'known-bad-post-detach-successor-index-cutover-shapes-must-fail-validation'
C_OUTCOME = 'successor-index-cutover-old-handles-terminal-successors-exact'
CONSUMPTION_DIGEST = 'sha256:a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4'
REQUIRED_INVALID_FIXTURES = ['dual-active-window-allowed.json', 'filename-indexed.json', 'forked-successor-allowed.json', 'full-text-indexed.json', 'missing-consumption-receipt.json', 'missing-cutover-marker.json', 'old-handle-still-live.json', 'orphan-successor-allowed.json', 'pattern-successor-subject.json', 'raw-locator-indexed.json', 'rollback-allowed.json', 'secret-material-present.json']

JSON_REQUIREMENTS = {
    'spec/examples/removable.media.local.post_detach.fresh.authority.consumption.receipt.json': (
        (("successor_index_cutover", "posture"), C_POSTURE),
        (("successor_index_cutover", "kind"), C_KIND),
        (("successor_index_cutover", "schema"), SCHEMA_REL),
        (("successor_index_cutover", "digest"), C_DIGEST),
        (("successor_index_cutover", "negative_fixture_policy"), C_POLICY),
        (("successor_index_cutover", "successor_index_cutover_required"), True),
    ),
    'spec/examples/removable.media.local.post_detach.fresh.authority.receipt.json': ((("consumption_receipt", "successor_index_cutover", "posture"), C_POSTURE), (("consumption_receipt", "successor_index_cutover", "digest"), C_DIGEST)),
    'spec/examples/removable.media.local.post_detach.denial.receipt.json': ((("fresh_authority", "consumption_receipt", "successor_index_cutover", "posture"), C_POSTURE), (("fresh_authority", "consumption_receipt", "successor_index_cutover", "digest"), C_DIGEST)),
    'spec/examples/removable.media.local.post_detach.revocation.tombstone.json': ((("fresh_authority", "consumption_receipt", "successor_index_cutover", "posture"), C_POSTURE), (("fresh_authority", "consumption_receipt", "successor_index_cutover", "digest"), C_DIGEST)),
    'spec/examples/removable.media.local.post_detach.export.bundle.json': ((("fresh_authority", "consumption_receipt", "successor_index_cutover", "posture"), C_POSTURE), (("fresh_authority", "consumption_receipt", "successor_index_cutover", "digest"), C_DIGEST)),
    'spec/examples/removable.media.local.post_detach.query.projection.json': ((("fresh_authority", "consumption_receipt", "successor_index_cutover", "posture"), C_POSTURE), (("fresh_authority", "consumption_receipt", "successor_index_cutover", "digest"), C_DIGEST)),
    'spec/examples/removable.media.local.post_detach.recovery.evidence.json': (
        (("query_projection", "successor_index_cutover_posture"), C_POSTURE),
        (("query_projection", "successor_index_cutover_kind"), C_KIND),
        (("query_projection", "successor_index_cutover_schema"), SCHEMA_REL),
        (("query_projection", "successor_index_cutover_digest"), C_DIGEST),
        (("query_projection", "successor_index_cutover_negative_fixture_policy"), C_POLICY),
        (("query_projection", "successor_index_cutover_required"), True),
    ),
    'spec/examples/removable.media.local.post_detach.contract.json': (
        (("backend_evidence", "successor_index_cutover_posture"), C_POSTURE),
        (("backend_evidence", "successor_index_cutover_kind"), C_KIND),
        (("backend_evidence", "successor_index_cutover_schema"), SCHEMA_REL),
        (("backend_evidence", "successor_index_cutover_digest"), C_DIGEST),
        (("backend_evidence", "successor_index_cutover_negative_fixture_policy"), C_POLICY),
        (("backend_evidence", "successor_index_cutover_required"), True),
        (("failure_policy", "successor_index_cutover_missing"), "fail-closed"),
    ),
    'spec/examples/content.import.plan.removable-media-local-ingest.json': (
        (("execution", "post_detach_successor_index_cutover_posture"), C_POSTURE),
        (("execution", "post_detach_successor_index_cutover_digest"), C_DIGEST),
        (("execution", "post_detach_successor_index_cutover_schema"), SCHEMA_REL),
        (("execution", "post_detach_successor_index_cutover_negative_fixture_policy"), C_POLICY),
        (("execution", "post_detach_successor_index_cutover_required"), True),
        (("operations", 0, "params", "post_detach_successor_index_cutover_posture"), C_POSTURE),
    ),
    'spec/examples/content.import.receipt.removable-media-local-ingest.json': (
        (("execution", "post_detach_successor_index_cutover_posture"), C_POSTURE),
        (("execution", "post_detach_successor_index_cutover_digest"), C_DIGEST),
        (("execution", "post_detach_successor_index_cutover_schema"), SCHEMA_REL),
        (("execution", "post_detach_successor_index_cutover_negative_fixture_policy"), C_POLICY),
        (("execution", "post_detach_successor_index_cutover_required"), True),
    ),
    'spec/examples/preopen.map.removable-media-local-ingest-post-detach.json': (
        (("successor_index_cutover_posture",), C_POSTURE),
        (("successor_index_cutover_digest",), C_DIGEST),
        (("successor_index_cutover_schema",), SCHEMA_REL),
        (("successor_index_cutover_negative_fixture_policy",), C_POLICY),
        (("successor_index_cutover_required",), True),
    ),
}

SCHEMA_FIELDS = {
    SCHEMA_REL: (C_KIND, 'exact-successors-from-consumption-only', C_OUTCOME, 'old_handle_still_live', 'dual_active_window', 'rollback_to_old_index'),
    FIXTURE_SCHEMA_REL: ('Exact Fixture (r513)', C_KIND, C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.fresh.authority.consumption.receipt.schema.json': ('successor_index_cutover', C_POSTURE, 'sha256Digest', C_POLICY),
    'spec/removable.media.local.post_detach.fresh.authority.consumption.receipt.fixture.schema.json': ('successor_index_cutover', C_POSTURE, C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.fresh.authority.receipt.schema.json': ('successor_index_cutover', C_POSTURE, C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.denial.receipt.schema.json': ('successor_index_cutover', C_POSTURE, C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.revocation.tombstone.schema.json': ('successor_index_cutover', C_POSTURE, C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.export.bundle.schema.json': ('successor_index_cutover', C_POSTURE, C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.query.projection.schema.json': ('successor_index_cutover', C_POSTURE, C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.recovery.evidence.schema.json': ('successor_index_cutover_posture', C_POSTURE, C_POLICY, 'sha256Digest'),
    'spec/removable.media.local.post_detach.recovery.evidence.fixture.schema.json': ('successor_index_cutover_posture', C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.contract.schema.json': ('successor_index_cutover_posture', 'successor_index_cutover_missing'),
    'spec/content.import.plan.schema.json': ('post_detach_successor_index_cutover_posture', 'post_detach_successor_index_cutover_negative_fixture_policy'),
    'spec/content.import.receipt.schema.json': ('post_detach_successor_index_cutover_posture', 'post_detach_successor_index_cutover_negative_fixture_policy'),
    'spec/preopen.map.schema.json': ('successor_index_cutover_posture', 'successor_index_cutover_negative_fixture_policy'),
}

TEXT_REQUIREMENTS = {
    'docs/768-removable-media-local-fallback-post-detach-successor-index-cutover-is-typed-and-negative-tested.md': (C_POSTURE, C_DIGEST, C_POLICY, SCHEMA_REL, EXAMPLE_REL, INVALID_DIR, C_OUTCOME),
    'adrs/ADR-0357-removable-media-local-fallback-post-detach-successor-index-cutover-is-typed-and-negative-tested.md': (C_POSTURE, C_DIGEST, C_POLICY, SCHEMA_REL, INVALID_DIR),
    'docs/767-removable-media-local-fallback-post-detach-fresh-authority-consumption-is-typed-and-negative-tested.md': (C_POSTURE, C_DIGEST, C_OUTCOME),
    'docs/293-attribute-indexed-metadata-and-live-queries.md': (C_POSTURE, 'successor-index cutover'),
    'docs/266-open-questions-and-risk-register.md': (C_POSTURE, C_POLICY),
    'docs/98-archive-hygiene.md': ('check_removable_media_local_post_detach_successor_index_cutover_receipt.py', C_POSTURE),
    'docs/99-llm-runbook.md': ('check_removable_media_local_post_detach_successor_index_cutover_receipt.py', C_POSTURE),
    'docs/110-juicy-os-lessons.md': (C_POSTURE, C_OUTCOME),
    'README.md': ('ADR-0357', C_POSTURE),
    'docs/00-index.md': ('ADR-0357', 'docs/768-removable-media-local-fallback-post-detach-successor-index-cutover-is-typed-and-negative-tested.md', C_POSTURE),
    'CHANGELOG.md': ('2026-05-23r513', '2026-05-30r533', 'check_removable_media_local_post_detach_successor_index_cutover_receipt.py', C_POSTURE, 'post-detach-successor-index-cutover-generic-runtime-schema-plus-exact-fixture-split'),
}


def fail(msg: str) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(1)


def load_json(rel: str):
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


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
        fail(f"{EXAMPLE_REL} must validate against {FIXTURE_SCHEMA_REL}: {fixture_errs[:10]}")

    if schema.get('additionalProperties') is not False:
        fail(f"{SCHEMA_REL} must be closed-world at the root")
    if example['consumed_authority']['fresh_authority_consumption_receipt_digest'] != CONSUMPTION_DIGEST:
        fail(f"{EXAMPLE_REL} must join to the r512 consumption digest")
    if example['cutover_decision']['outcome'] != C_OUTCOME:
        fail(f"{EXAMPLE_REL} must record {C_OUTCOME}")
    if example['old_index_state']['old_handles_still_live'] is not False:
        fail(f"{EXAMPLE_REL} must make old handles terminal")
    if example['successor_index_state']['orphan_successor_allowed'] is not False:
        fail(f"{EXAMPLE_REL} must deny orphan successors")

    invalid_root = ROOT / INVALID_DIR
    if not invalid_root.is_dir():
        fail(f"Missing invalid fixture directory {INVALID_DIR}")
    fixture_names = sorted(p.name for p in invalid_root.glob('*.json'))
    if fixture_names != REQUIRED_INVALID_FIXTURES:
        fail(f"Invalid fixture set mismatch: {fixture_names} != {REQUIRED_INVALID_FIXTURES}")
    for path in sorted(invalid_root.glob('*.json')):
        obj = json.loads(path.read_text(encoding='utf-8'))
        if not validation_errors(validator, obj):
            fail(f"Invalid fixture unexpectedly validates: {path.relative_to(ROOT)}")

    for rel, requirements in JSON_REQUIREMENTS.items():
        obj = load_json(rel)
        for path, expected in requirements:
            actual = nested_value(obj, path)
            if actual != expected:
                fail(f"{rel}: {'.'.join(map(str, path))} = {actual!r}, expected {expected!r}")

    for rel, tokens in SCHEMA_FIELDS.items():
        text = (ROOT / rel).read_text(encoding='utf-8')
        for token in tokens:
            if token not in text:
                fail(f"{rel} missing schema token {token!r}")

    for rel, tokens in TEXT_REQUIREMENTS.items():
        text = (ROOT / rel).read_text(encoding='utf-8')
        for token in tokens:
            if token not in text:
                fail(f"{rel} missing text token {token!r}")

    hygiene = (ROOT / 'tools' / 'hygiene.py').read_text(encoding='utf-8')
    if 'check_removable_media_local_post_detach_successor_index_cutover_receipt.py' not in hygiene:
        fail('tools/hygiene.py must include check_removable_media_local_post_detach_successor_index_cutover_receipt.py')

    print('removable-media post-detach successor-index cutover receipt check passed')


if __name__ == '__main__':
    main()
