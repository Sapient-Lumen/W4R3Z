#!/usr/bin/env python3
"""Guard r516 removable-media post-detach reader-use receipts.

The r515 reader-admission receipt proves a broker saw the checkpoint.  This
check keeps the next step honest: every admitted reader action must be
budgeted, sequenced, redacted, and receipt-visible before the observation
result is exposed.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_REL = 'spec/removable.media.local.post_detach.reader.use.receipt.schema.json'
FIXTURE_SCHEMA_REL = 'spec/removable.media.local.post_detach.reader.use.receipt.fixture.schema.json'
EXAMPLE_REL = 'spec/examples/removable.media.local.post_detach.reader.use.receipt.json'
INVALID_DIR = 'spec/examples/invalid/removable-media/post-detach-reader-use-receipt'
C_KIND = 'removable.media.local.post_detach.reader.use.receipt'
C_POSTURE = 'typed-post-detach-reader-use-positive-and-negative-fixture-guarded'
C_DIGEST = 'sha256:e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6'
C_POLICY = 'known-bad-post-detach-reader-use-shapes-must-fail-validation'
C_OUTCOME = 'post-detach-reader-use-budgeted-sequenced-and-redacted'
C_FLOOR = 'admitted-reader-use-receipted-before-observation-result'
ADMISSION_DIGEST = 'sha256:d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5'
REQUIRED_INVALID_FIXTURES = ['admission-reused-as-use-receipt.json', 'body-text-returned.json', 'broad-reader-scope.json', 'budget-exhausted-before-use-accepted.json', 'budget-not-debited-before-result.json', 'double-spend-allowed.json', 'export-granted-by-read.json', 'filename-returned.json', 'host-identity-leaked.json', 'live-subscription-requested.json', 'missing-reader-admission-receipt.json', 'raw-locator-returned.json', 'replay-token-present.json', 'result-visible-before-receipt.json', 'secret-material-present.json']

JSON_REQUIREMENTS = {
    EXAMPLE_REL: (
        (("contract_binding", "reader_admission_digest"), ADMISSION_DIGEST),
        (("contract_binding", "reader_use_posture"), C_POSTURE),
        (("contract_binding", "reader_use_digest"), C_DIGEST),
        (("contract_binding", "reader_use_floor"), C_FLOOR),
        (("admission_binding", "admission_reusable_as_use_receipt"), False),
        (("use_budget", "debit_before_result_visibility"), True),
        (("use_budget", "double_spend_allowed"), False),
        (("result_sealing", "result_visible_before_receipt"), False),
        (("reader_use_decision", "outcome"), C_OUTCOME),
    ),
    'spec/examples/removable.media.local.post_detach.reader.admission.receipt.json': (
        (("reader_use_receipt", "posture"), C_POSTURE),
        (("reader_use_receipt", "kind"), C_KIND),
        (("reader_use_receipt", "schema"), SCHEMA_REL),
        (("reader_use_receipt", "digest"), C_DIGEST),
        (("reader_use_receipt", "negative_fixture_policy"), C_POLICY),
        (("reader_use_receipt", "reader_use_required"), True),
        (("reader_use_receipt", "use_floor"), C_FLOOR),
    ),
    'spec/examples/removable.media.local.post_detach.successor.index.checkpoint.receipt.json': (
        (("reader_admission", "reader_use_posture"), C_POSTURE),
        (("reader_admission", "reader_use_kind"), C_KIND),
        (("reader_admission", "reader_use_schema"), SCHEMA_REL),
        (("reader_admission", "reader_use_digest"), C_DIGEST),
        (("reader_admission", "reader_use_negative_fixture_policy"), C_POLICY),
        (("reader_admission", "reader_use_required"), True),
    ),
    'spec/examples/removable.media.local.post_detach.successor.index.cutover.receipt.json': (
        (("successor_index_checkpoint", "reader_use_posture"), C_POSTURE),
        (("successor_index_checkpoint", "reader_use_kind"), C_KIND),
        (("successor_index_checkpoint", "reader_use_schema"), SCHEMA_REL),
        (("successor_index_checkpoint", "reader_use_digest"), C_DIGEST),
        (("successor_index_checkpoint", "reader_use_negative_fixture_policy"), C_POLICY),
        (("successor_index_checkpoint", "reader_use_required"), True),
    ),
    'spec/examples/removable.media.local.post_detach.fresh.authority.consumption.receipt.json': (
        (("successor_index_cutover", "successor_index_reader_use_posture"), C_POSTURE),
        (("successor_index_cutover", "successor_index_reader_use_kind"), C_KIND),
        (("successor_index_cutover", "successor_index_reader_use_schema"), SCHEMA_REL),
        (("successor_index_cutover", "successor_index_reader_use_digest"), C_DIGEST),
        (("successor_index_cutover", "successor_index_reader_use_negative_fixture_policy"), C_POLICY),
        (("successor_index_cutover", "successor_index_reader_use_required"), True),
    ),
    'spec/examples/removable.media.local.post_detach.fresh.authority.receipt.json': (
        (("consumption_receipt", "successor_index_cutover", "successor_index_reader_use_posture"), C_POSTURE),
        (("consumption_receipt", "successor_index_cutover", "successor_index_reader_use_kind"), C_KIND),
        (("consumption_receipt", "successor_index_cutover", "successor_index_reader_use_schema"), SCHEMA_REL),
        (("consumption_receipt", "successor_index_cutover", "successor_index_reader_use_digest"), C_DIGEST),
        (("consumption_receipt", "successor_index_cutover", "successor_index_reader_use_negative_fixture_policy"), C_POLICY),
        (("consumption_receipt", "successor_index_cutover", "successor_index_reader_use_required"), True),
    ),
    'spec/examples/removable.media.local.post_detach.recovery.evidence.json': (
        (("query_projection", "successor_index_reader_use_posture"), C_POSTURE),
        (("query_projection", "successor_index_reader_use_kind"), C_KIND),
        (("query_projection", "successor_index_reader_use_schema"), SCHEMA_REL),
        (("query_projection", "successor_index_reader_use_digest"), C_DIGEST),
        (("query_projection", "successor_index_reader_use_negative_fixture_policy"), C_POLICY),
        (("query_projection", "successor_index_reader_use_required"), True),
    ),
    'spec/examples/removable.media.local.post_detach.contract.json': (
        (("backend_evidence", "successor_index_reader_use_posture"), C_POSTURE),
        (("backend_evidence", "successor_index_reader_use_kind"), C_KIND),
        (("backend_evidence", "successor_index_reader_use_schema"), SCHEMA_REL),
        (("backend_evidence", "successor_index_reader_use_digest"), C_DIGEST),
        (("backend_evidence", "successor_index_reader_use_negative_fixture_policy"), C_POLICY),
        (("backend_evidence", "successor_index_reader_use_required"), True),
        (("failure_policy", "successor_index_reader_use_missing"), "fail-closed"),
        (("failure_policy", "successor_index_reader_use_budget_exhausted"), "fail-closed"),
        (("failure_policy", "successor_index_reader_use_replay_or_double_spend"), "fail-closed"),
    ),
    'spec/examples/content.import.plan.removable-media-local-ingest.json': (
        (("execution", "post_detach_successor_index_reader_use_posture"), C_POSTURE),
        (("execution", "post_detach_successor_index_reader_use_digest"), C_DIGEST),
        (("execution", "post_detach_successor_index_reader_use_schema"), SCHEMA_REL),
        (("execution", "post_detach_successor_index_reader_use_negative_fixture_policy"), C_POLICY),
        (("execution", "post_detach_successor_index_reader_use_required"), True),
        (("operations", 0, "params", "post_detach_successor_index_reader_use_posture"), C_POSTURE),
    ),
    'spec/examples/content.import.receipt.removable-media-local-ingest.json': (
        (("execution", "post_detach_successor_index_reader_use_posture"), C_POSTURE),
        (("execution", "post_detach_successor_index_reader_use_digest"), C_DIGEST),
        (("execution", "post_detach_successor_index_reader_use_schema"), SCHEMA_REL),
        (("execution", "post_detach_successor_index_reader_use_negative_fixture_policy"), C_POLICY),
        (("execution", "post_detach_successor_index_reader_use_required"), True),
    ),
    'spec/examples/preopen.map.removable-media-local-ingest-post-detach.json': (
        (("successor_index_reader_use_posture",), C_POSTURE),
        (("successor_index_reader_use_digest",), C_DIGEST),
        (("successor_index_reader_use_schema",), SCHEMA_REL),
        (("successor_index_reader_use_negative_fixture_policy",), C_POLICY),
        (("successor_index_reader_use_required",), True),
    ),
}

SCHEMA_FIELDS = {
    SCHEMA_REL: (C_KIND, C_POSTURE, C_POLICY, C_OUTCOME, 'debit_before_result_visibility', 'result_visible_before_receipt'),
    FIXTURE_SCHEMA_REL: (C_KIND, C_POSTURE, C_DIGEST, C_POLICY, C_OUTCOME, 'debit_before_result_visibility', 'result_visible_before_receipt'),
    'spec/removable.media.local.post_detach.reader.admission.receipt.schema.json': ('reader_use_receipt', C_POSTURE, C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.successor.index.checkpoint.receipt.schema.json': ('reader_use_posture', 'sha256Digest', C_POLICY),
    'spec/removable.media.local.post_detach.successor.index.checkpoint.receipt.fixture.schema.json': ('reader_use_posture', C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.successor.index.cutover.receipt.schema.json': ('reader_use_posture', C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.fresh.authority.consumption.receipt.schema.json': ('successor_index_reader_use_posture', 'sha256Digest', C_POLICY),
    'spec/removable.media.local.post_detach.fresh.authority.consumption.receipt.fixture.schema.json': ('successor_index_reader_use_posture', C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.fresh.authority.receipt.schema.json': ('successor_index_reader_use_posture', C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.denial.receipt.schema.json': ('successor_index_reader_use_posture', C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.revocation.tombstone.schema.json': ('successor_index_reader_use_posture', C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.export.bundle.schema.json': ('successor_index_reader_use_posture', C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.query.projection.schema.json': ('successor_index_reader_use_posture', C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.recovery.evidence.schema.json': ('successor_index_reader_use_posture', C_POSTURE, C_POLICY, 'sha256Digest'),
    'spec/removable.media.local.post_detach.recovery.evidence.fixture.schema.json': ('successor_index_reader_use_posture', C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.contract.schema.json': ('successor_index_reader_use_posture', 'successor_index_reader_use_missing', 'successor_index_reader_use_budget_exhausted'),
    'spec/content.import.plan.schema.json': ('post_detach_successor_index_reader_use_posture', 'post_detach_successor_index_reader_use_negative_fixture_policy'),
    'spec/content.import.receipt.schema.json': ('post_detach_successor_index_reader_use_posture', 'post_detach_successor_index_reader_use_negative_fixture_policy'),
    'spec/preopen.map.schema.json': ('successor_index_reader_use_posture', 'successor_index_reader_use_negative_fixture_policy'),
}

TEXT_REQUIREMENTS = {
    'docs/771-removable-media-local-fallback-post-detach-reader-use-is-typed-and-negative-tested.md': (C_POSTURE, C_DIGEST, C_POLICY, SCHEMA_REL, EXAMPLE_REL, INVALID_DIR, C_OUTCOME),
    'adrs/ADR-0360-removable-media-local-fallback-post-detach-reader-use-is-typed-and-negative-tested.md': (C_POSTURE, C_DIGEST, C_POLICY, SCHEMA_REL, INVALID_DIR),
    'docs/770-removable-media-local-fallback-post-detach-reader-admission-is-typed-and-negative-tested.md': (C_POSTURE, C_DIGEST, C_OUTCOME),
    'docs/293-attribute-indexed-metadata-and-live-queries.md': (C_POSTURE, 'reader use'),
    'docs/266-open-questions-and-risk-register.md': (C_POSTURE, C_POLICY),
    'docs/98-archive-hygiene.md': ('check_removable_media_local_post_detach_reader_use_receipt.py', C_POSTURE),
    'docs/99-llm-runbook.md': ('check_removable_media_local_post_detach_reader_use_receipt.py', C_POSTURE),
    'docs/110-juicy-os-lessons.md': (C_POSTURE, C_OUTCOME),
    'README.md': ('ADR-0360', C_POSTURE),
    'docs/00-index.md': ('ADR-0360', 'docs/771-removable-media-local-fallback-post-detach-reader-use-is-typed-and-negative-tested.md', C_POSTURE),
    'CHANGELOG.md': ('2026-05-24r516', 'check_removable_media_local_post_detach_reader_use_receipt.py', C_POSTURE),
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
        fail(f"{EXAMPLE_REL} must validate against exact fixture {FIXTURE_SCHEMA_REL}: {fixture_errs[:10]}")

    if schema.get('additionalProperties') is not False:
        fail(f"{SCHEMA_REL} must be closed-world at the root")
    if '$defs' not in schema:
        fail(f"{SCHEMA_REL} must be runtime-shaped with $defs")
    if 'allOf' not in fixture_schema:
        fail(f"{FIXTURE_SCHEMA_REL} must preserve the exact historical fixture schema under allOf")
    if example['admission_binding']['reader_admission_receipt_digest'] != ADMISSION_DIGEST:
        fail(f"{EXAMPLE_REL} must join to the r515 reader-admission digest")
    if example['reader_use_decision']['outcome'] != C_OUTCOME:
        fail(f"{EXAMPLE_REL} must record {C_OUTCOME}")
    if example['use_budget']['debit_before_result_visibility'] is not True:
        fail(f"{EXAMPLE_REL} must debit the reader budget before result visibility")
    if example['result_sealing']['result_visible_before_receipt'] is not False:
        fail(f"{EXAMPLE_REL} must prevent result visibility before receipt visibility")

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
    if 'check_removable_media_local_post_detach_reader_use_receipt.py' not in hygiene:
        fail('tools/hygiene.py must include ' + 'check_removable_media_local_post_detach_reader_use_receipt.py')

    print('removable-media post-detach reader-use receipt check passed')


if __name__ == '__main__':
    main()
