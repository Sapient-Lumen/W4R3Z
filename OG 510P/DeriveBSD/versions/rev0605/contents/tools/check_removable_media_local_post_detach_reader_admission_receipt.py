#!/usr/bin/env python3
"""Validate removable-media post-detach reader-admission receipts.

This guardrail keeps r515 from treating the r514 checkpoint as passive state.
Every post-checkpoint broker must prove it observed the fenced root before using
query, export, rehydration, remote-locator, or managed-copy authority.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_REL = 'spec/removable.media.local.post_detach.reader.admission.receipt.schema.json'
FIXTURE_SCHEMA_REL = 'spec/removable.media.local.post_detach.reader.admission.receipt.fixture.schema.json'
EXAMPLE_REL = 'spec/examples/removable.media.local.post_detach.reader.admission.receipt.json'
INVALID_DIR = 'spec/examples/invalid/removable-media/post-detach-reader-admission-receipt'
C_KIND = 'removable.media.local.post_detach.reader.admission.receipt'
C_POSTURE = 'typed-post-detach-reader-admission-positive-and-negative-fixture-guarded'
C_DIGEST = 'sha256:d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5'
C_POLICY = 'known-bad-post-detach-reader-admission-shapes-must-fail-validation'
C_OUTCOME = 'post-detach-reader-admission-checkpoint-observed-and-stale-roots-denied'
CHECKPOINT_KIND = 'removable.media.local.post_detach.successor.index.checkpoint.receipt'
CHECKPOINT_DIGEST = 'sha256:c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8'
CHECKPOINT_POSTURE = 'typed-post-detach-successor-index-checkpoint-positive-and-negative-fixture-guarded'
CHECKPOINT_POLICY = 'known-bad-post-detach-successor-index-checkpoint-shapes-must-fail-validation'
REQUIRED_INVALID_FIXTURES = ['below-checkpoint-sequence.json', 'broad-reader-scope.json', 'broker-use-before-admission.json', 'checkpoint-not-observed.json', 'dual-active-snapshot-accepted.json', 'filename-indexed.json', 'live-subscription-requested.json', 'missing-checkpoint-receipt.json', 'old-handle-root-accepted.json', 'raw-locator-included.json', 'secret-material-present.json', 'stale-index-root-accepted.json']

JSON_REQUIREMENTS = {
    'spec/examples/removable.media.local.post_detach.successor.index.checkpoint.receipt.json': (
        (("reader_admission", "posture"), C_POSTURE),
        (("reader_admission", "kind"), C_KIND),
        (("reader_admission", "schema"), SCHEMA_REL),
        (("reader_admission", "digest"), C_DIGEST),
        (("reader_admission", "negative_fixture_policy"), C_POLICY),
        (("reader_admission", "reader_admission_required"), True),
        (("reader_admission", "minimum_accepted_sequence"), 44),
    ),
    'spec/examples/removable.media.local.post_detach.successor.index.cutover.receipt.json': (
        (("successor_index_checkpoint", "reader_admission_posture"), C_POSTURE),
        (("successor_index_checkpoint", "reader_admission_kind"), C_KIND),
        (("successor_index_checkpoint", "reader_admission_schema"), SCHEMA_REL),
        (("successor_index_checkpoint", "reader_admission_digest"), C_DIGEST),
        (("successor_index_checkpoint", "reader_admission_negative_fixture_policy"), C_POLICY),
        (("successor_index_checkpoint", "reader_admission_required"), True),
    ),
    'spec/examples/removable.media.local.post_detach.fresh.authority.consumption.receipt.json': (
        (("successor_index_cutover", "successor_index_reader_admission_posture"), C_POSTURE),
        (("successor_index_cutover", "successor_index_reader_admission_digest"), C_DIGEST),
    ),
    'spec/examples/removable.media.local.post_detach.fresh.authority.receipt.json': (
        (("consumption_receipt", "successor_index_cutover", "successor_index_reader_admission_posture"), C_POSTURE),
        (("consumption_receipt", "successor_index_cutover", "successor_index_reader_admission_digest"), C_DIGEST),
    ),
    'spec/examples/removable.media.local.post_detach.denial.receipt.json': (
        (("fresh_authority", "consumption_receipt", "successor_index_cutover", "successor_index_reader_admission_posture"), C_POSTURE),
        (("fresh_authority", "consumption_receipt", "successor_index_cutover", "successor_index_reader_admission_digest"), C_DIGEST),
    ),
    'spec/examples/removable.media.local.post_detach.revocation.tombstone.json': (
        (("fresh_authority", "consumption_receipt", "successor_index_cutover", "successor_index_reader_admission_posture"), C_POSTURE),
        (("fresh_authority", "consumption_receipt", "successor_index_cutover", "successor_index_reader_admission_digest"), C_DIGEST),
    ),
    'spec/examples/removable.media.local.post_detach.export.bundle.json': (
        (("fresh_authority", "consumption_receipt", "successor_index_cutover", "successor_index_reader_admission_posture"), C_POSTURE),
        (("fresh_authority", "consumption_receipt", "successor_index_cutover", "successor_index_reader_admission_digest"), C_DIGEST),
    ),
    'spec/examples/removable.media.local.post_detach.query.projection.json': (
        (("fresh_authority", "consumption_receipt", "successor_index_cutover", "successor_index_reader_admission_posture"), C_POSTURE),
        (("fresh_authority", "consumption_receipt", "successor_index_cutover", "successor_index_reader_admission_digest"), C_DIGEST),
    ),
    'spec/examples/removable.media.local.post_detach.recovery.evidence.json': (
        (("query_projection", "successor_index_reader_admission_posture"), C_POSTURE),
        (("query_projection", "successor_index_reader_admission_kind"), C_KIND),
        (("query_projection", "successor_index_reader_admission_schema"), SCHEMA_REL),
        (("query_projection", "successor_index_reader_admission_digest"), C_DIGEST),
        (("query_projection", "successor_index_reader_admission_negative_fixture_policy"), C_POLICY),
        (("query_projection", "successor_index_reader_admission_required"), True),
    ),
    'spec/examples/removable.media.local.post_detach.contract.json': (
        (("backend_evidence", "successor_index_reader_admission_posture"), C_POSTURE),
        (("backend_evidence", "successor_index_reader_admission_kind"), C_KIND),
        (("backend_evidence", "successor_index_reader_admission_schema"), SCHEMA_REL),
        (("backend_evidence", "successor_index_reader_admission_digest"), C_DIGEST),
        (("backend_evidence", "successor_index_reader_admission_negative_fixture_policy"), C_POLICY),
        (("backend_evidence", "successor_index_reader_admission_required"), True),
        (("failure_policy", "successor_index_reader_admission_missing"), "fail-closed"),
        (("failure_policy", "successor_index_reader_admission_stale_root"), "fail-closed"),
    ),
    'spec/examples/content.import.plan.removable-media-local-ingest.json': (
        (("execution", "post_detach_successor_index_reader_admission_posture"), C_POSTURE),
        (("execution", "post_detach_successor_index_reader_admission_digest"), C_DIGEST),
        (("execution", "post_detach_successor_index_reader_admission_schema"), SCHEMA_REL),
        (("execution", "post_detach_successor_index_reader_admission_negative_fixture_policy"), C_POLICY),
        (("execution", "post_detach_successor_index_reader_admission_required"), True),
        (("operations", 0, "params", "post_detach_successor_index_reader_admission_posture"), C_POSTURE),
    ),
    'spec/examples/content.import.receipt.removable-media-local-ingest.json': (
        (("execution", "post_detach_successor_index_reader_admission_posture"), C_POSTURE),
        (("execution", "post_detach_successor_index_reader_admission_digest"), C_DIGEST),
        (("execution", "post_detach_successor_index_reader_admission_schema"), SCHEMA_REL),
        (("execution", "post_detach_successor_index_reader_admission_negative_fixture_policy"), C_POLICY),
        (("execution", "post_detach_successor_index_reader_admission_required"), True),
    ),
    'spec/examples/preopen.map.removable-media-local-ingest-post-detach.json': (
        (("successor_index_reader_admission_posture",), C_POSTURE),
        (("successor_index_reader_admission_digest",), C_DIGEST),
        (("successor_index_reader_admission_schema",), SCHEMA_REL),
        (("successor_index_reader_admission_negative_fixture_policy",), C_POLICY),
        (("successor_index_reader_admission_required",), True),
    ),
}

SCHEMA_FIELDS = {
    SCHEMA_REL: (C_KIND, FIXTURE_SCHEMA_REL, C_POSTURE, C_DIGEST, C_POLICY, C_OUTCOME, 'broker_use_before_admission', 'stale_index_root_accepted', 'post-detach-reader-admission-generic-runtime-schema-plus-exact-fixture-split'),
    FIXTURE_SCHEMA_REL: (C_KIND, C_POSTURE, C_DIGEST, C_POLICY, C_OUTCOME),
    'spec/removable.media.local.post_detach.successor.index.checkpoint.receipt.schema.json': ('reader_admission', C_POSTURE, 'sha256Digest', C_POLICY),
    'spec/removable.media.local.post_detach.successor.index.checkpoint.receipt.fixture.schema.json': ('reader_admission', C_POSTURE, C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.successor.index.cutover.receipt.schema.json': ('reader_admission_posture', C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.fresh.authority.consumption.receipt.schema.json': ('successor_index_reader_admission_posture', 'sha256Digest', C_POLICY),
    'spec/removable.media.local.post_detach.fresh.authority.consumption.receipt.fixture.schema.json': ('successor_index_reader_admission_posture', C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.fresh.authority.receipt.schema.json': ('successor_index_reader_admission_posture', C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.denial.receipt.schema.json': ('successor_index_reader_admission_posture', C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.revocation.tombstone.schema.json': ('successor_index_reader_admission_posture', C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.export.bundle.schema.json': ('successor_index_reader_admission_posture', C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.query.projection.schema.json': ('successor_index_reader_admission_posture', C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.recovery.evidence.schema.json': ('successor_index_reader_admission_posture', C_POSTURE, C_POLICY, 'sha256Digest'),
    'spec/removable.media.local.post_detach.recovery.evidence.fixture.schema.json': ('successor_index_reader_admission_posture', C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.contract.schema.json': ('successor_index_reader_admission_posture', 'successor_index_reader_admission_missing', 'successor_index_reader_admission_stale_root'),
    'spec/content.import.plan.schema.json': ('post_detach_successor_index_reader_admission_posture', 'post_detach_successor_index_reader_admission_negative_fixture_policy'),
    'spec/content.import.receipt.schema.json': ('post_detach_successor_index_reader_admission_posture', 'post_detach_successor_index_reader_admission_negative_fixture_policy'),
    'spec/preopen.map.schema.json': ('successor_index_reader_admission_posture', 'successor_index_reader_admission_negative_fixture_policy'),
}

TEXT_REQUIREMENTS = {
    'docs/770-removable-media-local-fallback-post-detach-reader-admission-is-typed-and-negative-tested.md': (C_POSTURE, C_DIGEST, C_POLICY, SCHEMA_REL, EXAMPLE_REL, INVALID_DIR, C_OUTCOME),
    'adrs/ADR-0359-removable-media-local-fallback-post-detach-reader-admission-is-typed-and-negative-tested.md': (C_POSTURE, C_DIGEST, C_POLICY, SCHEMA_REL, INVALID_DIR),
    'docs/769-removable-media-local-fallback-post-detach-successor-index-checkpoint-is-typed-and-negative-tested.md': (C_POSTURE, C_DIGEST, C_OUTCOME),
    'docs/293-attribute-indexed-metadata-and-live-queries.md': (C_POSTURE, 'reader admission'),
    'docs/266-open-questions-and-risk-register.md': (C_POSTURE, C_POLICY),
    'docs/98-archive-hygiene.md': ('check_removable_media_local_post_detach_reader_admission_receipt.py', C_POSTURE),
    'docs/99-llm-runbook.md': ('check_removable_media_local_post_detach_reader_admission_receipt.py', C_POSTURE),
    'docs/110-juicy-os-lessons.md': (C_POSTURE, C_OUTCOME),
    'README.md': ('ADR-0359', C_POSTURE),
    'docs/00-index.md': ('ADR-0359', 'docs/770-removable-media-local-fallback-post-detach-reader-admission-is-typed-and-negative-tested.md', C_POSTURE),
    'CHANGELOG.md': ('2026-05-24r515', '2026-05-30r532', 'check_removable_media_local_post_detach_reader_admission_receipt.py', C_POSTURE, 'post-detach-reader-admission-generic-runtime-schema-plus-exact-fixture-split'),
    'docs/787-removable-media-local-fallback-post-detach-terminal-closure-successor-authority-and-reader-admission-schema-split.md': ('post-detach-reader-admission-generic-runtime-schema-plus-exact-fixture-split', FIXTURE_SCHEMA_REL, C_POSTURE),
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


def semantic_errors(obj) -> list[str]:
    errors: list[str] = []
    if obj.get('kind') != C_KIND:
        errors.append('kind mismatch')
    if obj.get('negative_fixture_policy') != C_POLICY:
        errors.append('negative fixture policy mismatch')
    cb = obj.get('checkpoint_binding')
    if not isinstance(cb, dict):
        errors.append('checkpoint_binding must be present')
    else:
        if cb.get('successor_index_checkpoint_receipt_digest') != CHECKPOINT_DIGEST:
            errors.append('checkpoint digest must match r514 checkpoint')
        if cb.get('checkpoint_observed') is not True:
            errors.append('checkpoint must be observed')
        if cb.get('checkpoint_mutable') is not False:
            errors.append('checkpoint must be immutable')
        if cb.get('checkpoint_sequence') != 44 or cb.get('minimum_accepted_sequence') != 44:
            errors.append('checkpoint floor must remain sequence 44')
    req = obj.get('reader_request') if isinstance(obj.get('reader_request'), dict) else {}
    if req.get('request_scope') != 'single-successor-digest':
        errors.append('reader scope must be one exact successor digest')
    for key in ['pattern_or_prefix_subject', 'live_subscription_requested', 'raw_locator_requested', 'untrusted_filename_requested']:
        if req.get(key) is not False:
            errors.append(f'reader_request {key} must be false')
    state = obj.get('admission_state') if isinstance(obj.get('admission_state'), dict) else {}
    if state.get('observed_checkpoint_sequence') != 44:
        errors.append('observed checkpoint sequence must be 44')
    for key in ['root_at_or_above_checkpoint', 'reader_fence_applied']:
        if state.get(key) is not True:
            errors.append(f'admission_state {key} must be true')
    for key in ['stale_index_root_accepted', 'old_handle_root_accepted', 'dual_active_snapshot_accepted', 'rollback_to_pre_checkpoint_root_allowed', 'broker_use_before_admission']:
        if state.get(key) is not False:
            errors.append(f'admission_state {key} must be false')
    red = obj.get('redaction') if isinstance(obj.get('redaction'), dict) else {}
    for key in ['raw_locator_values_included', 'untrusted_filename_indexed', 'host_identity_included', 'full_text_indexed', 'body_text_included', 'recipient_text_included', 'raw_receipt_payload_included', 'secret_material_present']:
        if red.get(key) is not False:
            errors.append(f'redaction {key} must be false')
    auth = obj.get('admitted_authority') if isinstance(obj.get('admitted_authority'), dict) else {}
    for key in ['authority_broadened', 'stale_handle_accepted']:
        if auth.get(key) is not False:
            errors.append(f'admitted_authority {key} must be false')
    if auth.get('successor_digest_exact') is not True:
        errors.append('successor digest must be exact')
    dec = obj.get('admission_decision') if isinstance(obj.get('admission_decision'), dict) else {}
    if dec.get('outcome') != C_OUTCOME:
        errors.append('admission outcome mismatch')
    for key in ['admission_required_before_broker_use', 'checkpoint_observed_before_use', 'reader_root_floor_enforced', 'redaction_preserved']:
        if dec.get(key) is not True:
            errors.append(f'admission_decision {key} must be true')
    if dec.get('offline_copy_erasure_claimed') is not False:
        errors.append('offline copy erasure must not be claimed')
    return errors

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
    sem = semantic_errors(example)
    if sem:
        fail(f"{EXAMPLE_REL} semantic errors: {sem[:10]}")

    if schema.get('additionalProperties') is not False:
        fail(f"{SCHEMA_REL} must be closed-world at the root")
    if '$defs' not in schema:
        fail(f"{SCHEMA_REL} must be runtime-shaped with $defs")
    if 'allOf' not in load_json(FIXTURE_SCHEMA_REL):
        fail(f"{FIXTURE_SCHEMA_REL} must preserve exact historical fixture under allOf")
    if example['checkpoint_binding']['successor_index_checkpoint_receipt_digest'] != CHECKPOINT_DIGEST:
        fail(f"{EXAMPLE_REL} must join to the r514 checkpoint digest")
    if example['admission_decision']['outcome'] != C_OUTCOME:
        fail(f"{EXAMPLE_REL} must record {C_OUTCOME}")
    if example['admission_state']['observed_checkpoint_sequence'] != 44:
        fail(f"{EXAMPLE_REL} must observe checkpoint sequence 44")
    if example['admission_state']['broker_use_before_admission'] is not False:
        fail(f"{EXAMPLE_REL} must deny broker use before admission")

    invalid_root = ROOT / INVALID_DIR
    if not invalid_root.is_dir():
        fail(f"Missing invalid fixture directory {INVALID_DIR}")
    fixture_names = sorted(p.name for p in invalid_root.glob('*.json'))
    if fixture_names != REQUIRED_INVALID_FIXTURES:
        fail(f"Invalid fixture set mismatch: {fixture_names} != {REQUIRED_INVALID_FIXTURES}")
    for path in sorted(invalid_root.glob('*.json')):
        obj = json.loads(path.read_text(encoding='utf-8'))
        if not validation_errors(validator, obj) and not semantic_errors(obj):
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
    if 'check_removable_media_local_post_detach_reader_admission_receipt.py' not in hygiene:
        fail('tools/hygiene.py must include check_removable_media_local_post_detach_reader_admission_receipt.py')

    print('removable-media post-detach reader-admission receipt check passed')


if __name__ == '__main__':
    main()
