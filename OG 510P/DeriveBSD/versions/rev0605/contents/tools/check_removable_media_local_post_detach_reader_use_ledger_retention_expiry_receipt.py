#!/usr/bin/env python3
"""Guard r519 removable-media post-detach reader-use ledger retention expiry receipts.

The r518 retention receipt bounds and compacts the reader-use ledger. This
check closes the next seam: retention expiry must be explicit, redacted,
monotonic, and denial-auditable so bounded retention cannot silently become
indefinite or lose the proof needed to explain future denied reads.
"""
from __future__ import annotations

from pathlib import Path

from removable_media_post_detach_guardrail_lib import (
    require_guardrail_contract,
    require_positive_fixture_valid,
    require_tokens,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_REL = 'spec/removable.media.local.post_detach.reader.use.ledger.retention.expiry.receipt.schema.json'
FIXTURE_SCHEMA_REL = 'spec/removable.media.local.post_detach.reader.use.ledger.retention.expiry.receipt.fixture.schema.json'
EXAMPLE_REL = 'spec/examples/removable.media.local.post_detach.reader.use.ledger.retention.expiry.receipt.json'
INVALID_DIR = 'spec/examples/invalid/removable-media/post-detach-reader-use-ledger-retention-expiry-receipt'
C_KIND = 'removable.media.local.post_detach.reader.use.ledger.retention.expiry.receipt'
C_POSTURE = 'typed-post-detach-reader-use-ledger-retention-expiry-positive-and-negative-fixture-guarded'
C_DIGEST = 'sha256:1919191919191919191919191919191919191919191919191919191919191919'
C_POLICY = 'known-bad-post-detach-reader-use-ledger-retention-expiry-shapes-must-fail-validation'
C_OUTCOME = 'post-detach-reader-use-ledger-retention-expiry-finalized-redacted-and-denial-auditable'
C_FLOOR = 'reader-use-ledger-retention-expiry-finalized-with-proof-carry-forward-no-silent-extension'
R518_DIGEST = 'sha256:f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8'
CHECKER_NAME = 'check_removable_media_local_post_detach_reader_use_ledger_retention_expiry_receipt.py'
REQUIRED_INVALID_FIXTURES = ['audit-summary-deleted.json', 'body-text-indexed.json', 'expired-root-still-queryable.json', 'expiry-before-retention-window-end.json', 'filename-indexed.json', 'forked-expiry-accepted.json', 'full-text-indexed.json', 'future-reader-admission-without-fresh-authority.json', 'host-identity-present.json', 'missing-proof-carry-forward.json', 'missing-retention-receipt.json', 'non-monotonic-expiry-sequence.json', 'offline-erasure-claimed.json', 'raw-locator-indexed.json', 'rollback-accepted.json', 'secret-material-present.json', 'silent-extension-accepted.json', 'silent-extension-requested.json', 'stale-compacted-root-accepted.json', 'unbounded-post-expiry-retention.json']

JSON_REQUIREMENTS = {
    EXAMPLE_REL: (
        (("contract_binding", "reader_use_ledger_retention_digest"), R518_DIGEST),
        (("contract_binding", "reader_use_ledger_retention_expiry_posture"), C_POSTURE),
        (("contract_binding", "reader_use_ledger_retention_expiry_digest"), C_DIGEST),
        (("contract_binding", "reader_use_ledger_retention_expiry_floor"), C_FLOOR),
        (("expiry_trigger", "expiry_not_before_retention_expires_at"), True),
        (("expiry_trigger", "silent_extension_requested"), False),
        (("expiry_commit", "monotonic_expiry_sequence"), True),
        (("expiry_commit", "compare_and_swap_result"), "committed"),
        (("expiry_commit", "rollback_accepted"), False),
        (("expiry_commit", "forked_expiry_accepted"), False),
        (("evidence_after_expiry", "proof_carry_forward_digest_retained"), "sha256:" + "fd" * 32),
        (("evidence_after_expiry", "expired_root_queryable_for_new_reads"), False),
        (("evidence_after_expiry", "future_reader_admission_requires_fresh_authority"), True),
        (("evidence_after_expiry", "raw_locator_indexed"), False),
        (("evidence_after_expiry", "secret_material_present"), False),
        (("expiry_decision", "outcome"), C_OUTCOME),
        (("expiry_decision", "silent_extension_allowed"), False),
        (("expiry_decision", "stale_compacted_root_accepted"), False),
        (("expiry_decision", "offline_copy_erasure_claimed"), False),
    ),
    'spec/examples/removable.media.local.post_detach.reader.use.ledger.retention.receipt.json': (
        (("reader_use_ledger_retention_expiry_receipt", "posture"), C_POSTURE),
        (("reader_use_ledger_retention_expiry_receipt", "kind"), C_KIND),
        (("reader_use_ledger_retention_expiry_receipt", "schema"), SCHEMA_REL),
        (("reader_use_ledger_retention_expiry_receipt", "digest"), C_DIGEST),
        (("reader_use_ledger_retention_expiry_receipt", "negative_fixture_policy"), C_POLICY),
        (("reader_use_ledger_retention_expiry_receipt", "expiry_floor"), C_FLOOR),
        (("reader_use_ledger_retention_expiry_receipt", "expiry_receipt_required"), True),
        (("reader_use_ledger_retention_expiry_receipt", "expired_root_queryable_for_new_reads"), False),
        (("verifier_model", "expiry_receipt_required"), True),
    ),
    'spec/examples/removable.media.local.post_detach.contract.json': (
        (("backend_evidence", "successor_index_reader_use_ledger_retention_expiry_posture"), C_POSTURE),
        (("backend_evidence", "successor_index_reader_use_ledger_retention_expiry_kind"), C_KIND),
        (("backend_evidence", "successor_index_reader_use_ledger_retention_expiry_schema"), SCHEMA_REL),
        (("backend_evidence", "successor_index_reader_use_ledger_retention_expiry_digest"), C_DIGEST),
        (("backend_evidence", "successor_index_reader_use_ledger_retention_expiry_negative_fixture_policy"), C_POLICY),
        (("backend_evidence", "successor_index_reader_use_ledger_retention_expiry_required"), True),
        (("failure_policy", "successor_index_reader_use_ledger_retention_expiry_missing"), "fail-closed"),
        (("failure_policy", "successor_index_reader_use_ledger_retention_expiry_silent_extension"), "fail-closed"),
        (("failure_policy", "successor_index_reader_use_ledger_retention_expiry_stale_root"), "fail-closed"),
    ),
    'spec/examples/content.import.plan.removable-media-local-ingest.json': (
        (("execution", "post_detach_successor_index_reader_use_ledger_retention_expiry_posture"), C_POSTURE),
        (("execution", "post_detach_successor_index_reader_use_ledger_retention_expiry_digest"), C_DIGEST),
        (("execution", "post_detach_successor_index_reader_use_ledger_retention_expiry_schema"), SCHEMA_REL),
        (("execution", "post_detach_successor_index_reader_use_ledger_retention_expiry_negative_fixture_policy"), C_POLICY),
        (("execution", "post_detach_successor_index_reader_use_ledger_retention_expiry_required"), True),
        (("operations", 0, "params", "post_detach_successor_index_reader_use_ledger_retention_expiry_posture"), C_POSTURE),
    ),
    'spec/examples/content.import.receipt.removable-media-local-ingest.json': (
        (("execution", "post_detach_successor_index_reader_use_ledger_retention_expiry_posture"), C_POSTURE),
        (("execution", "post_detach_successor_index_reader_use_ledger_retention_expiry_digest"), C_DIGEST),
        (("execution", "post_detach_successor_index_reader_use_ledger_retention_expiry_schema"), SCHEMA_REL),
        (("execution", "post_detach_successor_index_reader_use_ledger_retention_expiry_negative_fixture_policy"), C_POLICY),
        (("execution", "post_detach_successor_index_reader_use_ledger_retention_expiry_required"), True),
    ),
    'spec/examples/preopen.map.removable-media-local-ingest-post-detach.json': (
        (("successor_index_reader_use_ledger_retention_expiry_posture",), C_POSTURE),
        (("successor_index_reader_use_ledger_retention_expiry_kind",), C_KIND),
        (("successor_index_reader_use_ledger_retention_expiry_schema",), SCHEMA_REL),
        (("successor_index_reader_use_ledger_retention_expiry_digest",), C_DIGEST),
        (("successor_index_reader_use_ledger_retention_expiry_negative_fixture_policy",), C_POLICY),
        (("successor_index_reader_use_ledger_retention_expiry_required",), True),
        (("successor_index_reader_use_ledger_retention_expiry_floor",), C_FLOOR),
    ),
}

TEXT_REQUIREMENTS = {
    'docs/774-removable-media-local-fallback-post-detach-reader-use-ledger-retention-expiry-is-typed-and-negative-tested.md': (C_POSTURE, C_DIGEST, C_POLICY, SCHEMA_REL, FIXTURE_SCHEMA_REL, EXAMPLE_REL, INVALID_DIR, C_OUTCOME, C_FLOOR, 'require_positive_fixture_valid'),
    'adrs/ADR-0363-removable-media-local-fallback-post-detach-reader-use-ledger-retention-expiry-is-typed-and-negative-tested.md': (C_POSTURE, C_DIGEST, C_POLICY, C_OUTCOME, 'expiry', 'silent extension'),
    'README.md': ('ADR-0363', C_POSTURE),
    'docs/00-index.md': ('ADR-0363', 'docs/774-removable-media-local-fallback-post-detach-reader-use-ledger-retention-expiry-is-typed-and-negative-tested.md', C_POSTURE),
    'CHANGELOG.md': ('2026-05-25r519', CHECKER_NAME, C_POSTURE, 'require_positive_fixture_valid'),
    'docs/99-llm-runbook.md': (CHECKER_NAME, C_POSTURE, 'retention expiry'),
    'docs/110-juicy-os-lessons.md': ('r519 removable-media reader-use ledger retention expiry', C_POSTURE),
    'docs/266-open-questions-and-risk-register.md': ('r519 removable-media reader-use ledger retention expiry risk note', C_POSTURE),
    'docs/293-attribute-indexed-metadata-and-live-queries.md': ('r519 removable-media reader-use ledger retention expiry', C_POSTURE),
    'docs/98-archive-hygiene.md': (CHECKER_NAME, C_POSTURE, 'require_guardrail_contract'),
}


SCHEMA_FIELDS = {
    SCHEMA_REL: (C_KIND, C_POSTURE, C_POLICY, C_OUTCOME, 'reader-use-ledger-retention-expiry-generic-runtime-schema-plus-exact-fixture-split', 'sha256Digest', 'expiry_sequence'),
    FIXTURE_SCHEMA_REL: ('allOf', 'const', C_DIGEST, 'historical literal regression surface'),
    'spec/removable.media.local.post_detach.reader.use.ledger.retention.receipt.schema.json': ('reader_use_ledger_retention_expiry_receipt', C_POSTURE, 'sha256Digest', C_POLICY),
    'spec/removable.media.local.post_detach.reader.use.ledger.retention.receipt.fixture.schema.json': ('reader_use_ledger_retention_expiry_receipt', C_POSTURE, C_DIGEST, C_POLICY),
    'spec/removable.media.local.post_detach.reader.use.ledger.retention.expiry.enforcement.receipt.schema.json': ('reader_use_ledger_retention_expiry_digest', 'sha256', C_POSTURE),
    'spec/removable.media.local.post_detach.reader.use.ledger.retention.expiry.enforcement.receipt.fixture.schema.json': ('reader_use_ledger_retention_expiry_digest', C_DIGEST, C_POSTURE),
    'spec/removable.media.local.post_detach.contract.schema.json': ('successor_index_reader_use_ledger_retention_expiry_posture', 'successor_index_reader_use_ledger_retention_expiry_missing', C_POLICY),
    'spec/content.import.plan.schema.json': ('post_detach_successor_index_reader_use_ledger_retention_expiry_posture', 'post_detach_successor_index_reader_use_ledger_retention_expiry_negative_fixture_policy'),
    'spec/content.import.receipt.schema.json': ('post_detach_successor_index_reader_use_ledger_retention_expiry_posture', 'post_detach_successor_index_reader_use_ledger_retention_expiry_negative_fixture_policy'),
    'spec/preopen.map.schema.json': ('successor_index_reader_use_ledger_retention_expiry_posture', 'successor_index_reader_use_ledger_retention_expiry_negative_fixture_policy'),
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
        label='r519 reader-use-ledger-retention-expiry token',
    )
    require_tokens(ROOT, SCHEMA_FIELDS, 'schema token')
    print('removable-media post-detach reader-use ledger retention expiry receipt check passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
