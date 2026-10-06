#!/usr/bin/env python3
"""Guard r517 removable-media post-detach reader-use ledger receipts.

The r516 reader-use receipt proves a result was budgeted and redacted. This
check closes the next seam: the budget debit must be committed to a monotonic
ledger root before result release, so concurrent brokers cannot double-spend,
fork, roll back, or silently restore pre-debit observation budget.
"""
from __future__ import annotations

from pathlib import Path

from removable_media_post_detach_guardrail_lib import (
    fail,
    require_hygiene_entry,
    require_invalid_fixtures_fail,
    require_positive_fixture_valid,
    require_json_values,
    require_tokens,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_REL = 'spec/removable.media.local.post_detach.reader.use.ledger.receipt.schema.json'
EXAMPLE_REL = 'spec/examples/removable.media.local.post_detach.reader.use.ledger.receipt.json'
INVALID_DIR = 'spec/examples/invalid/removable-media/post-detach-reader-use-ledger-receipt'
C_KIND = 'removable.media.local.post_detach.reader.use.ledger.receipt'
C_POSTURE = 'typed-post-detach-reader-use-ledger-positive-and-negative-fixture-guarded'
C_DIGEST = 'sha256:f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7'
C_POLICY = 'known-bad-post-detach-reader-use-ledger-shapes-must-fail-validation'
C_OUTCOME = 'post-detach-reader-use-ledger-root-monotonic-and-committed'
C_FLOOR = 'reader-use-ledger-committed-before-result-release'
R516_DIGEST = 'sha256:e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6'
CHECKER_NAME = 'check_removable_media_local_post_detach_reader_use_ledger_receipt.py'
REQUIRED_INVALID_FIXTURES = ['debit-not-committed-before-result.json', 'double-spend-accepted.json', 'filename-indexed.json', 'forked-ledger-root-accepted.json', 'ledger-root-not-cas-bound.json', 'live-subscription-ledgered.json', 'missing-reader-use-receipt.json', 'non-monotonic-ledger-sequence.json', 'raw-locator-indexed.json', 'replay-token-present.json', 'result-visible-before-ledger-commit.json', 'rollback-accepted.json', 'secret-material-present.json', 'stale-root-accepted.json', 'unbounded-retention.json']

JSON_REQUIREMENTS = {
    EXAMPLE_REL: (
        (("contract_binding", "reader_use_digest"), R516_DIGEST),
        (("contract_binding", "reader_use_ledger_posture"), C_POSTURE),
        (("contract_binding", "reader_use_ledger_digest"), C_DIGEST),
        (("contract_binding", "reader_use_ledger_floor"), C_FLOOR),
        (("ledger_precondition", "stale_root_accepted"), False),
        (("budget_debit_commit", "debit_committed_before_result_release"), True),
        (("budget_debit_commit", "double_spend_accepted"), False),
        (("ledger_commit", "monotonic_sequence"), True),
        (("ledger_commit", "compare_and_swap_result"), "committed"),
        (("ledger_commit", "forked_ledger_root_accepted"), False),
        (("ledger_commit", "rollback_accepted"), False),
        (("ledger_commit", "result_release_after_commit"), True),
        (("projection_redaction", "raw_locator_indexed"), False),
        (("ledger_decision", "outcome"), C_OUTCOME),
    ),
    'spec/examples/removable.media.local.post_detach.reader.use.receipt.json': (
        (("reader_use_ledger_receipt", "posture"), C_POSTURE),
        (("reader_use_ledger_receipt", "kind"), C_KIND),
        (("reader_use_ledger_receipt", "schema"), SCHEMA_REL),
        (("reader_use_ledger_receipt", "digest"), C_DIGEST),
        (("reader_use_ledger_receipt", "negative_fixture_policy"), C_POLICY),
        (("reader_use_ledger_receipt", "ledger_floor"), C_FLOOR),
        (("reader_use_ledger_receipt", "ledger_receipt_required"), True),
        (("reader_use_ledger_receipt", "ledger_commit_before_result_release"), True),
        (("reader_use_ledger_receipt", "ledger_without_commit"), False),
        (("verifier_model", "reader_use_ledger_required"), True),
    ),
    'spec/examples/removable.media.local.post_detach.reader.admission.receipt.json': (
        (("reader_use_receipt", "ledger_posture"), C_POSTURE),
        (("reader_use_receipt", "ledger_kind"), C_KIND),
        (("reader_use_receipt", "ledger_schema"), SCHEMA_REL),
        (("reader_use_receipt", "ledger_digest"), C_DIGEST),
        (("reader_use_receipt", "ledger_negative_fixture_policy"), C_POLICY),
        (("reader_use_receipt", "ledger_required"), True),
        (("reader_use_receipt", "ledger_floor"), C_FLOOR),
    ),
    'spec/examples/removable.media.local.post_detach.contract.json': (
        (("backend_evidence", "successor_index_reader_use_ledger_posture"), C_POSTURE),
        (("backend_evidence", "successor_index_reader_use_ledger_kind"), C_KIND),
        (("backend_evidence", "successor_index_reader_use_ledger_schema"), SCHEMA_REL),
        (("backend_evidence", "successor_index_reader_use_ledger_digest"), C_DIGEST),
        (("backend_evidence", "successor_index_reader_use_ledger_negative_fixture_policy"), C_POLICY),
        (("backend_evidence", "successor_index_reader_use_ledger_required"), True),
        (("failure_policy", "successor_index_reader_use_ledger_missing"), "fail-closed"),
        (("failure_policy", "successor_index_reader_use_ledger_rollback_or_fork"), "fail-closed"),
        (("failure_policy", "successor_index_reader_use_ledger_double_spend"), "fail-closed"),
    ),
    'spec/examples/content.import.plan.removable-media-local-ingest.json': (
        (("execution", "post_detach_successor_index_reader_use_ledger_posture"), C_POSTURE),
        (("execution", "post_detach_successor_index_reader_use_ledger_digest"), C_DIGEST),
        (("execution", "post_detach_successor_index_reader_use_ledger_schema"), SCHEMA_REL),
        (("execution", "post_detach_successor_index_reader_use_ledger_negative_fixture_policy"), C_POLICY),
        (("execution", "post_detach_successor_index_reader_use_ledger_required"), True),
        (("operations", 0, "params", "post_detach_successor_index_reader_use_ledger_posture"), C_POSTURE),
    ),
    'spec/examples/content.import.receipt.removable-media-local-ingest.json': (
        (("execution", "post_detach_successor_index_reader_use_ledger_posture"), C_POSTURE),
        (("execution", "post_detach_successor_index_reader_use_ledger_digest"), C_DIGEST),
        (("execution", "post_detach_successor_index_reader_use_ledger_schema"), SCHEMA_REL),
        (("execution", "post_detach_successor_index_reader_use_ledger_negative_fixture_policy"), C_POLICY),
        (("execution", "post_detach_successor_index_reader_use_ledger_required"), True),
    ),
    'spec/examples/preopen.map.removable-media-local-ingest-post-detach.json': (
        (("successor_index_reader_use_ledger_posture",), C_POSTURE),
        (("successor_index_reader_use_ledger_digest",), C_DIGEST),
        (("successor_index_reader_use_ledger_schema",), SCHEMA_REL),
        (("successor_index_reader_use_ledger_negative_fixture_policy",), C_POLICY),
        (("successor_index_reader_use_ledger_required",), True),
    ),
}

SCHEMA_FIELDS = {
    SCHEMA_REL: (C_KIND, C_POSTURE, C_DIGEST, C_POLICY, C_OUTCOME, 'compare_and_swap_result', 'forked_ledger_root_accepted'),
    'spec/removable.media.local.post_detach.reader.use.receipt.schema.json': ('reader_use_ledger_receipt', C_POSTURE, C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.reader.admission.receipt.schema.json': ('ledger_posture', C_POSTURE, C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.contract.schema.json': ('successor_index_reader_use_ledger_posture', 'successor_index_reader_use_ledger_missing', C_POLICY),
    'spec/content.import.plan.schema.json': ('post_detach_successor_index_reader_use_ledger_posture', 'post_detach_successor_index_reader_use_ledger_negative_fixture_policy'),
    'spec/content.import.receipt.schema.json': ('post_detach_successor_index_reader_use_ledger_posture', 'post_detach_successor_index_reader_use_ledger_negative_fixture_policy'),
    'spec/preopen.map.schema.json': ('successor_index_reader_use_ledger_posture', 'successor_index_reader_use_ledger_negative_fixture_policy'),
}

TEXT_REQUIREMENTS = {
    'docs/772-removable-media-local-fallback-post-detach-reader-use-ledger-is-typed-and-negative-tested.md': (C_POSTURE, C_DIGEST, C_POLICY, SCHEMA_REL, EXAMPLE_REL, INVALID_DIR, C_OUTCOME, 'removable_media_post_detach_guardrail_lib.py', 'require_positive_fixture_valid'),
    'adrs/ADR-0361-removable-media-local-fallback-post-detach-reader-use-ledger-is-typed-and-negative-tested.md': (C_POSTURE, C_DIGEST, C_POLICY, SCHEMA_REL, INVALID_DIR, C_OUTCOME),
    'docs/771-removable-media-local-fallback-post-detach-reader-use-is-typed-and-negative-tested.md': (C_POSTURE, C_DIGEST, C_OUTCOME),
    'docs/293-attribute-indexed-metadata-and-live-queries.md': (C_POSTURE, 'ledger root'),
    'docs/266-open-questions-and-risk-register.md': (C_POSTURE, C_POLICY),
    'docs/98-archive-hygiene.md': (CHECKER_NAME, C_POSTURE, 'removable_media_post_detach_guardrail_lib.py'),
    'docs/99-llm-runbook.md': (CHECKER_NAME, C_POSTURE),
    'docs/110-juicy-os-lessons.md': (C_POSTURE, C_OUTCOME),
    'README.md': ('ADR-0361', C_POSTURE),
    'docs/00-index.md': ('ADR-0361', 'docs/772-removable-media-local-fallback-post-detach-reader-use-ledger-is-typed-and-negative-tested.md', C_POSTURE),
    'CHANGELOG.md': ('2026-05-25r517', CHECKER_NAME, C_POSTURE, 'removable_media_post_detach_guardrail_lib.py'),
}


def main() -> None:
    require_positive_fixture_valid(ROOT, SCHEMA_REL, EXAMPLE_REL)
    require_invalid_fixtures_fail(ROOT, SCHEMA_REL, INVALID_DIR, REQUIRED_INVALID_FIXTURES)
    require_json_values(ROOT, JSON_REQUIREMENTS)
    require_tokens(ROOT, SCHEMA_FIELDS, 'schema token')
    require_tokens(ROOT, TEXT_REQUIREMENTS, 'text token')
    require_hygiene_entry(ROOT, CHECKER_NAME)

    print('removable-media post-detach reader-use ledger receipt check passed')


if __name__ == '__main__':
    main()
