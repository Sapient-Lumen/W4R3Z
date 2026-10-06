#!/usr/bin/env python3
"""Guard r518 removable-media post-detach reader-use ledger retention receipts.

The r517 ledger commit prevents double-spend and rollback. This check closes
the next seam: retaining that ledger must not keep raw observations forever,
and compacting it must not erase the proof needed to audit exhausted budgets,
denials, or future reader admission.
"""
from __future__ import annotations

from pathlib import Path

from removable_media_post_detach_guardrail_lib import (
    require_guardrail_contract,
    require_positive_fixture_valid,
    require_tokens,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_REL = 'spec/removable.media.local.post_detach.reader.use.ledger.retention.receipt.schema.json'
FIXTURE_SCHEMA_REL = 'spec/removable.media.local.post_detach.reader.use.ledger.retention.receipt.fixture.schema.json'
EXAMPLE_REL = 'spec/examples/removable.media.local.post_detach.reader.use.ledger.retention.receipt.json'
INVALID_DIR = 'spec/examples/invalid/removable-media/post-detach-reader-use-ledger-retention-receipt'
C_KIND = 'removable.media.local.post_detach.reader.use.ledger.retention.receipt'
C_POSTURE = 'typed-post-detach-reader-use-ledger-retention-positive-and-negative-fixture-guarded'
C_DIGEST = 'sha256:f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8'
C_POLICY = 'known-bad-post-detach-reader-use-ledger-retention-shapes-must-fail-validation'
C_OUTCOME = 'post-detach-reader-use-ledger-retention-bounded-redacted-and-auditable'
C_FLOOR = 'reader-use-ledger-retention-compacted-after-commit-without-raw-observation'
R517_DIGEST = 'sha256:f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7'
CHECKER_NAME = 'check_removable_media_local_post_detach_reader_use_ledger_retention_receipt.py'
REQUIRED_INVALID_FIXTURES = ['body-text-indexed.json', 'compaction-before-ledger-commit.json', 'filename-indexed.json', 'forked-compaction-accepted.json', 'full-text-indexed.json', 'future-query-without-compacted-root.json', 'host-identity-present.json', 'missing-audit-summary.json', 'missing-reader-use-ledger-receipt.json', 'offline-erasure-claimed.json', 'proof-carry-forward-missing.json', 'raw-locator-indexed.json', 'raw-observation-retained.json', 'raw-receipt-payload-retained.json', 'result-visible-before-ledger-commit.json', 'rollback-accepted.json', 'secret-material-present.json', 'unbounded-retention.json']

JSON_REQUIREMENTS = {
    EXAMPLE_REL: (
        (("contract_binding", "reader_use_ledger_digest"), R517_DIGEST),
        (("contract_binding", "reader_use_ledger_retention_posture"), C_POSTURE),
        (("contract_binding", "reader_use_ledger_retention_digest"), C_DIGEST),
        (("contract_binding", "reader_use_ledger_retention_floor"), C_FLOOR),
        (("retention_window", "raw_observation_retained"), False),
        (("retention_window", "raw_receipt_payload_retained"), False),
        (("retention_window", "unbounded_retention"), False),
        (("retention_window", "compaction_after_ledger_commit"), True),
        (("compaction_commit", "monotonic_retention_sequence"), True),
        (("compaction_commit", "compare_and_swap_result"), "committed"),
        (("compaction_commit", "forked_compaction_accepted"), False),
        (("compaction_commit", "rollback_accepted"), False),
        (("evidence_preservation", "debit_proof_preserved"), True),
        (("evidence_preservation", "exhausted_budget_auditable"), True),
        (("evidence_preservation", "raw_locator_indexed"), False),
        (("evidence_preservation", "secret_material_present"), False),
        (("retention_decision", "outcome"), C_OUTCOME),
        (("retention_decision", "future_query_uses_compacted_root"), True),
        (("retention_decision", "offline_copy_erasure_claimed"), False),
    ),
    'spec/examples/removable.media.local.post_detach.reader.use.ledger.receipt.json': (
        (("reader_use_ledger_retention_receipt", "posture"), C_POSTURE),
        (("reader_use_ledger_retention_receipt", "kind"), C_KIND),
        (("reader_use_ledger_retention_receipt", "schema"), SCHEMA_REL),
        (("reader_use_ledger_retention_receipt", "digest"), C_DIGEST),
        (("reader_use_ledger_retention_receipt", "negative_fixture_policy"), C_POLICY),
        (("reader_use_ledger_retention_receipt", "retention_floor"), C_FLOOR),
        (("reader_use_ledger_retention_receipt", "retention_receipt_required"), True),
        (("reader_use_ledger_retention_receipt", "raw_observation_retained"), False),
        (("verifier_model", "retention_receipt_required"), True),
    ),
    'spec/examples/removable.media.local.post_detach.contract.json': (
        (("backend_evidence", "successor_index_reader_use_ledger_retention_posture"), C_POSTURE),
        (("backend_evidence", "successor_index_reader_use_ledger_retention_kind"), C_KIND),
        (("backend_evidence", "successor_index_reader_use_ledger_retention_schema"), SCHEMA_REL),
        (("backend_evidence", "successor_index_reader_use_ledger_retention_digest"), C_DIGEST),
        (("backend_evidence", "successor_index_reader_use_ledger_retention_negative_fixture_policy"), C_POLICY),
        (("backend_evidence", "successor_index_reader_use_ledger_retention_required"), True),
        (("failure_policy", "successor_index_reader_use_ledger_retention_missing"), "fail-closed"),
        (("failure_policy", "successor_index_reader_use_ledger_retention_unbounded_or_raw"), "fail-closed"),
        (("failure_policy", "successor_index_reader_use_ledger_retention_compaction_missing"), "fail-closed"),
    ),
    'spec/examples/content.import.plan.removable-media-local-ingest.json': (
        (("execution", "post_detach_successor_index_reader_use_ledger_retention_posture"), C_POSTURE),
        (("execution", "post_detach_successor_index_reader_use_ledger_retention_digest"), C_DIGEST),
        (("execution", "post_detach_successor_index_reader_use_ledger_retention_schema"), SCHEMA_REL),
        (("execution", "post_detach_successor_index_reader_use_ledger_retention_negative_fixture_policy"), C_POLICY),
        (("execution", "post_detach_successor_index_reader_use_ledger_retention_required"), True),
        (("operations", 0, "params", "post_detach_successor_index_reader_use_ledger_retention_posture"), C_POSTURE),
    ),
    'spec/examples/content.import.receipt.removable-media-local-ingest.json': (
        (("execution", "post_detach_successor_index_reader_use_ledger_retention_posture"), C_POSTURE),
        (("execution", "post_detach_successor_index_reader_use_ledger_retention_digest"), C_DIGEST),
        (("execution", "post_detach_successor_index_reader_use_ledger_retention_schema"), SCHEMA_REL),
        (("execution", "post_detach_successor_index_reader_use_ledger_retention_negative_fixture_policy"), C_POLICY),
        (("execution", "post_detach_successor_index_reader_use_ledger_retention_required"), True),
    ),
    'spec/examples/preopen.map.removable-media-local-ingest-post-detach.json': (
        (("successor_index_reader_use_ledger_retention_posture",), C_POSTURE),
        (("successor_index_reader_use_ledger_retention_kind",), C_KIND),
        (("successor_index_reader_use_ledger_retention_schema",), SCHEMA_REL),
        (("successor_index_reader_use_ledger_retention_digest",), C_DIGEST),
        (("successor_index_reader_use_ledger_retention_negative_fixture_policy",), C_POLICY),
        (("successor_index_reader_use_ledger_retention_required",), True),
        (("successor_index_reader_use_ledger_retention_floor",), C_FLOOR),
    ),
}

TEXT_REQUIREMENTS = {
    'docs/773-removable-media-local-fallback-post-detach-reader-use-ledger-retention-is-typed-and-negative-tested.md': (C_POSTURE, C_DIGEST, C_POLICY, SCHEMA_REL, FIXTURE_SCHEMA_REL, EXAMPLE_REL, INVALID_DIR, C_OUTCOME, 'require_positive_fixture_valid', 'r518'),
    'adrs/ADR-0362-removable-media-local-fallback-post-detach-reader-use-ledger-retention-is-typed-and-negative-tested.md': (C_POSTURE, C_DIGEST, C_POLICY, C_OUTCOME, 'bounded', 'compaction'),
    'README.md': ('ADR-0362', C_POSTURE),
    'docs/00-index.md': ('ADR-0362', 'docs/773-removable-media-local-fallback-post-detach-reader-use-ledger-retention-is-typed-and-negative-tested.md', C_POSTURE),
    'CHANGELOG.md': ('2026-05-25r518', CHECKER_NAME, C_POSTURE, 'removable_media_post_detach_guardrail_lib.py'),
    'docs/99-llm-runbook.md': (CHECKER_NAME, C_POSTURE, 'reader-use ledger retention'),
    'docs/110-juicy-os-lessons.md': ('r518 removable-media reader-use ledger retention', C_POSTURE),
    'docs/266-open-questions-and-risk-register.md': ('r518 removable-media reader-use ledger retention risk note', C_POSTURE),
    'docs/293-attribute-indexed-metadata-and-live-queries.md': ('r518 removable-media reader-use ledger retention', C_POSTURE),
}


SCHEMA_FIELDS = {
    SCHEMA_REL: (C_KIND, C_POSTURE, C_POLICY, C_OUTCOME, 'reader-use-ledger-retention-generic-runtime-schema-plus-exact-fixture-split', 'sha256Digest', 'retention_sequence'),
    FIXTURE_SCHEMA_REL: ('allOf', 'const', C_DIGEST, 'historical literal regression surface'),
    'spec/removable.media.local.post_detach.reader.use.ledger.receipt.schema.json': ('reader_use_ledger_retention_receipt', C_POSTURE, 'sha256Digest', C_POLICY),
    'spec/removable.media.local.post_detach.reader.use.ledger.receipt.fixture.schema.json': ('reader_use_ledger_retention_receipt', C_POSTURE, C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.contract.schema.json': ('successor_index_reader_use_ledger_retention_posture', 'successor_index_reader_use_ledger_retention_missing', C_POLICY),
    'spec/content.import.plan.schema.json': ('post_detach_successor_index_reader_use_ledger_retention_posture', 'post_detach_successor_index_reader_use_ledger_retention_negative_fixture_policy'),
    'spec/content.import.receipt.schema.json': ('post_detach_successor_index_reader_use_ledger_retention_posture', 'post_detach_successor_index_reader_use_ledger_retention_negative_fixture_policy'),
    'spec/preopen.map.schema.json': ('successor_index_reader_use_ledger_retention_posture', 'successor_index_reader_use_ledger_retention_negative_fixture_policy'),
}

def main() -> int:
    require_positive_fixture_valid(ROOT, FIXTURE_SCHEMA_REL, EXAMPLE_REL)
    require_guardrail_contract(
        ROOT,
        schema_rel=SCHEMA_REL,
        example_rel=EXAMPLE_REL,
        invalid_dir=INVALID_DIR,
        expected_invalid_fixtures=REQUIRED_INVALID_FIXTURES,
        json_requirements=JSON_REQUIREMENTS,
        text_requirements=TEXT_REQUIREMENTS,
        checker_name=CHECKER_NAME,
        label='r518 reader-use-ledger-retention token',
    )
    require_tokens(ROOT, SCHEMA_FIELDS, 'schema token')
    print('removable-media post-detach reader-use ledger retention receipt check passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
