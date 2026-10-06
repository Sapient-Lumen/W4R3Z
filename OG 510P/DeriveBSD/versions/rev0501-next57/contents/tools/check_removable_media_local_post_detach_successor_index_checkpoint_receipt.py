#!/usr/bin/env python3
"""Validate removable-media post-detach successor-index checkpoint receipts.

This guardrail keeps r514 from treating the r513 cutover as enough by itself.
Post-cutover brokers need a typed, monotonic checkpoint so stale index roots,
restored old handles, and dual-active snapshots cannot silently regain authority.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_REL = 'spec/removable.media.local.post_detach.successor.index.checkpoint.receipt.schema.json'
EXAMPLE_REL = 'spec/examples/removable.media.local.post_detach.successor.index.checkpoint.receipt.json'
INVALID_DIR = 'spec/examples/invalid/removable-media/post-detach-successor-index-checkpoint-receipt'
C_KIND = 'removable.media.local.post_detach.successor.index.checkpoint.receipt'
C_POSTURE = 'typed-post-detach-successor-index-checkpoint-positive-and-negative-fixture-guarded'
C_DIGEST = 'sha256:c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8'
C_POLICY = 'known-bad-post-detach-successor-index-checkpoint-shapes-must-fail-validation'
C_OUTCOME = 'successor-index-checkpoint-cutover-root-anchored-and-rollback-denied'
CUTOVER_KIND = 'removable.media.local.post_detach.successor.index.cutover.receipt'
CUTOVER_DIGEST = 'sha256:b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3'
CUTOVER_POSTURE = 'typed-post-detach-successor-index-cutover-positive-and-negative-fixture-guarded'
REQUIRED_INVALID_FIXTURES = ['checkpoint-sequence-not-monotonic.json', 'dual-active-snapshot-accepted.json', 'filename-indexed.json', 'full-text-indexed.json', 'missing-cutover-receipt.json', 'missing-reader-fence.json', 'mutable-checkpoint.json', 'old-handle-root-restored.json', 'raw-locator-included.json', 'secret-material-present.json', 'stale-index-root-accepted.json', 'unanchored-checkpoint.json']

JSON_REQUIREMENTS = {
    'spec/examples/removable.media.local.post_detach.successor.index.cutover.receipt.json': (
        (("successor_index_checkpoint", "posture"), C_POSTURE),
        (("successor_index_checkpoint", "kind"), C_KIND),
        (("successor_index_checkpoint", "schema"), SCHEMA_REL),
        (("successor_index_checkpoint", "digest"), C_DIGEST),
        (("successor_index_checkpoint", "negative_fixture_policy"), C_POLICY),
        (("successor_index_checkpoint", "successor_index_checkpoint_required"), True),
        (("successor_index_checkpoint", "minimum_accepted_sequence"), 44),
    ),
    'spec/examples/removable.media.local.post_detach.fresh.authority.consumption.receipt.json': (
        (("successor_index_cutover", "successor_index_checkpoint_posture"), C_POSTURE),
        (("successor_index_cutover", "successor_index_checkpoint_digest"), C_DIGEST),
    ),
    'spec/examples/removable.media.local.post_detach.fresh.authority.receipt.json': (
        (("consumption_receipt", "successor_index_cutover", "successor_index_checkpoint_posture"), C_POSTURE),
        (("consumption_receipt", "successor_index_cutover", "successor_index_checkpoint_digest"), C_DIGEST),
    ),
    'spec/examples/removable.media.local.post_detach.denial.receipt.json': (
        (("fresh_authority", "consumption_receipt", "successor_index_cutover", "successor_index_checkpoint_posture"), C_POSTURE),
        (("fresh_authority", "consumption_receipt", "successor_index_cutover", "successor_index_checkpoint_digest"), C_DIGEST),
    ),
    'spec/examples/removable.media.local.post_detach.revocation.tombstone.json': (
        (("fresh_authority", "consumption_receipt", "successor_index_cutover", "successor_index_checkpoint_posture"), C_POSTURE),
        (("fresh_authority", "consumption_receipt", "successor_index_cutover", "successor_index_checkpoint_digest"), C_DIGEST),
    ),
    'spec/examples/removable.media.local.post_detach.export.bundle.json': (
        (("fresh_authority", "consumption_receipt", "successor_index_cutover", "successor_index_checkpoint_posture"), C_POSTURE),
        (("fresh_authority", "consumption_receipt", "successor_index_cutover", "successor_index_checkpoint_digest"), C_DIGEST),
    ),
    'spec/examples/removable.media.local.post_detach.query.projection.json': (
        (("fresh_authority", "consumption_receipt", "successor_index_cutover", "successor_index_checkpoint_posture"), C_POSTURE),
        (("fresh_authority", "consumption_receipt", "successor_index_cutover", "successor_index_checkpoint_digest"), C_DIGEST),
    ),
    'spec/examples/removable.media.local.post_detach.recovery.evidence.json': (
        (("query_projection", "successor_index_checkpoint_posture"), C_POSTURE),
        (("query_projection", "successor_index_checkpoint_kind"), C_KIND),
        (("query_projection", "successor_index_checkpoint_schema"), SCHEMA_REL),
        (("query_projection", "successor_index_checkpoint_digest"), C_DIGEST),
        (("query_projection", "successor_index_checkpoint_negative_fixture_policy"), C_POLICY),
        (("query_projection", "successor_index_checkpoint_required"), True),
    ),
    'spec/examples/removable.media.local.post_detach.contract.json': (
        (("backend_evidence", "successor_index_checkpoint_posture"), C_POSTURE),
        (("backend_evidence", "successor_index_checkpoint_kind"), C_KIND),
        (("backend_evidence", "successor_index_checkpoint_schema"), SCHEMA_REL),
        (("backend_evidence", "successor_index_checkpoint_digest"), C_DIGEST),
        (("backend_evidence", "successor_index_checkpoint_negative_fixture_policy"), C_POLICY),
        (("backend_evidence", "successor_index_checkpoint_required"), True),
        (("failure_policy", "successor_index_checkpoint_missing"), "fail-closed"),
        (("failure_policy", "successor_index_checkpoint_rollback"), "fail-closed"),
    ),
    'spec/examples/content.import.plan.removable-media-local-ingest.json': (
        (("execution", "post_detach_successor_index_checkpoint_posture"), C_POSTURE),
        (("execution", "post_detach_successor_index_checkpoint_digest"), C_DIGEST),
        (("execution", "post_detach_successor_index_checkpoint_schema"), SCHEMA_REL),
        (("execution", "post_detach_successor_index_checkpoint_negative_fixture_policy"), C_POLICY),
        (("execution", "post_detach_successor_index_checkpoint_required"), True),
        (("operations", 0, "params", "post_detach_successor_index_checkpoint_posture"), C_POSTURE),
    ),
    'spec/examples/content.import.receipt.removable-media-local-ingest.json': (
        (("execution", "post_detach_successor_index_checkpoint_posture"), C_POSTURE),
        (("execution", "post_detach_successor_index_checkpoint_digest"), C_DIGEST),
        (("execution", "post_detach_successor_index_checkpoint_schema"), SCHEMA_REL),
        (("execution", "post_detach_successor_index_checkpoint_negative_fixture_policy"), C_POLICY),
        (("execution", "post_detach_successor_index_checkpoint_required"), True),
    ),
    'spec/examples/preopen.map.removable-media-local-ingest-post-detach.json': (
        (("successor_index_checkpoint_posture",), C_POSTURE),
        (("successor_index_checkpoint_digest",), C_DIGEST),
        (("successor_index_checkpoint_schema",), SCHEMA_REL),
        (("successor_index_checkpoint_negative_fixture_policy",), C_POLICY),
        (("successor_index_checkpoint_required",), True),
    ),
}

SCHEMA_FIELDS = {
    SCHEMA_REL: (C_KIND, C_POSTURE, C_DIGEST, C_POLICY, C_OUTCOME, 'stale_index_root', 'old_handle_root_restored', 'dual_active_snapshot'),
    'spec/removable.media.local.post_detach.successor.index.cutover.receipt.schema.json': ('successor_index_checkpoint', C_POSTURE, C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.fresh.authority.consumption.receipt.schema.json': ('successor_index_checkpoint_posture', C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.fresh.authority.receipt.schema.json': ('successor_index_checkpoint_posture', C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.denial.receipt.schema.json': ('successor_index_checkpoint_posture', C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.revocation.tombstone.schema.json': ('successor_index_checkpoint_posture', C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.export.bundle.schema.json': ('successor_index_checkpoint_posture', C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.query.projection.schema.json': ('successor_index_checkpoint_posture', C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.recovery.evidence.schema.json': ('successor_index_checkpoint_posture', C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.contract.schema.json': ('successor_index_checkpoint_posture', 'successor_index_checkpoint_missing', 'successor_index_checkpoint_rollback'),
    'spec/content.import.plan.schema.json': ('post_detach_successor_index_checkpoint_posture', 'post_detach_successor_index_checkpoint_negative_fixture_policy'),
    'spec/content.import.receipt.schema.json': ('post_detach_successor_index_checkpoint_posture', 'post_detach_successor_index_checkpoint_negative_fixture_policy'),
    'spec/preopen.map.schema.json': ('successor_index_checkpoint_posture', 'successor_index_checkpoint_negative_fixture_policy'),
}

TEXT_REQUIREMENTS = {
    'docs/769-removable-media-local-fallback-post-detach-successor-index-checkpoint-is-typed-and-negative-tested.md': (C_POSTURE, C_DIGEST, C_POLICY, SCHEMA_REL, EXAMPLE_REL, INVALID_DIR, C_OUTCOME),
    'adrs/ADR-0358-removable-media-local-fallback-post-detach-successor-index-checkpoint-is-typed-and-negative-tested.md': (C_POSTURE, C_DIGEST, C_POLICY, SCHEMA_REL, INVALID_DIR),
    'docs/768-removable-media-local-fallback-post-detach-successor-index-cutover-is-typed-and-negative-tested.md': (C_POSTURE, C_DIGEST, C_OUTCOME),
    'docs/293-attribute-indexed-metadata-and-live-queries.md': (C_POSTURE, 'successor-index checkpoint'),
    'docs/266-open-questions-and-risk-register.md': (C_POSTURE, C_POLICY),
    'docs/98-archive-hygiene.md': ('check_removable_media_local_post_detach_successor_index_checkpoint_receipt.py', C_POSTURE),
    'docs/99-llm-runbook.md': ('check_removable_media_local_post_detach_successor_index_checkpoint_receipt.py', C_POSTURE),
    'docs/110-juicy-os-lessons.md': (C_POSTURE, C_OUTCOME),
    'README.md': ('ADR-0358', C_POSTURE),
    'docs/00-index.md': ('ADR-0358', 'docs/769-removable-media-local-fallback-post-detach-successor-index-checkpoint-is-typed-and-negative-tested.md', C_POSTURE),
    'CHANGELOG.md': ('2026-05-23r514', 'check_removable_media_local_post_detach_successor_index_checkpoint_receipt.py', C_POSTURE),
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
    example = load_json(EXAMPLE_REL)
    validator = Draft202012Validator(schema)

    errs = validation_errors(validator, example)
    if errs:
        fail(f"{EXAMPLE_REL} must validate against {SCHEMA_REL}: {errs[:10]}")

    if schema.get('additionalProperties') is not False:
        fail(f"{SCHEMA_REL} must be closed-world at the root")
    if example['contract_binding']['successor_index_cutover_digest'] != CUTOVER_DIGEST:
        fail(f"{EXAMPLE_REL} must join to the r513 cutover digest")
    if example['checkpoint_decision']['outcome'] != C_OUTCOME:
        fail(f"{EXAMPLE_REL} must record {C_OUTCOME}")
    if example['reader_fence']['minimum_accepted_sequence'] != 44:
        fail(f"{EXAMPLE_REL} must set reader fence to sequence 44")
    if example['reader_fence']['stale_index_root_accepted'] is not False:
        fail(f"{EXAMPLE_REL} must reject stale roots")

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
    if 'check_removable_media_local_post_detach_successor_index_checkpoint_receipt.py' not in hygiene:
        fail('tools/hygiene.py must include check_removable_media_local_post_detach_successor_index_checkpoint_receipt.py')

    print('removable-media post-detach successor-index checkpoint receipt check passed')


if __name__ == '__main__':
    main()
