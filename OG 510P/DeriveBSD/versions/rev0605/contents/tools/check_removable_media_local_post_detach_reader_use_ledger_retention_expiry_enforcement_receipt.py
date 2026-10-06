#!/usr/bin/env python3
"""Guard r520 removable-media post-detach reader-use ledger retention expiry enforcement receipts.

The r519 expiry receipt says expired compacted roots are denied-or-fresh-authority
only. This check makes that denial path explicit: post-expiry query/export/
rehydration attempts must emit a redacted enforcement receipt before any new
observation can occur.
"""
from __future__ import annotations

from pathlib import Path

from removable_media_post_detach_guardrail_lib import require_absent_tokens, require_guardrail_contract

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_REL = 'spec/removable.media.local.post_detach.reader.use.ledger.retention.expiry.enforcement.receipt.schema.json'
EXAMPLE_REL = 'spec/examples/removable.media.local.post_detach.reader.use.ledger.retention.expiry.enforcement.receipt.json'
INVALID_DIR = 'spec/examples/invalid/removable-media/post-detach-reader-use-ledger-retention-expiry-enforcement-receipt'
C_KIND = 'removable.media.local.post_detach.reader.use.ledger.retention.expiry.enforcement.receipt'
C_POSTURE = 'typed-post-detach-reader-use-ledger-retention-expiry-enforcement-positive-and-negative-fixture-guarded'
C_DIGEST = 'sha256:2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a'
C_POLICY = 'known-bad-post-detach-reader-use-ledger-retention-expiry-enforcement-shapes-must-fail-validation'
C_OUTCOME = 'post-detach-reader-use-ledger-retention-expiry-enforcement-denied-redacted-and-fresh-authority-gated'
C_FLOOR = 'retention-expiry-enforcement-denies-expired-roots-before-new-observation'
R519_DIGEST = 'sha256:1919191919191919191919191919191919191919191919191919191919191919'
CHECKER_NAME = 'check_removable_media_local_post_detach_reader_use_ledger_retention_expiry_enforcement_receipt.py'
REQUIRED_INVALID_FIXTURES = ['allow-export-after-expiry.json', 'allow-new-observation.json', 'allow-rehydration-after-expiry.json', 'body-text-indexed.json', 'forked-enforcement-accepted.json', 'fresh-authority-not-required.json', 'full-text-indexed.json', 'host-identity-present.json', 'missing-expiry-receipt.json', 'missing-rate-limit-debit.json', 'non-monotonic-enforcement-sequence.json', 'raw-handle-present.json', 'raw-locator-present.json', 'rollback-accepted.json', 'secret-material-present.json', 'silent-success-without-denial.json', 'stale-root-accepted.json', 'support-raw-payload-visible.json', 'unbounded-retry-window.json', 'untrusted-filename-present.json']

JSON_REQUIREMENTS = {
    EXAMPLE_REL: (
        (("contract_binding", "reader_use_ledger_retention_expiry_digest"), R519_DIGEST),
        (("contract_binding", "reader_use_ledger_retention_expiry_enforcement_posture"), C_POSTURE),
        (("contract_binding", "reader_use_ledger_retention_expiry_enforcement_digest"), C_DIGEST),
        (("contract_binding", "reader_use_ledger_retention_expiry_enforcement_floor"), C_FLOOR),
        (("expiry_binding", "retention_finalized"), True),
        (("post_expiry_attempt", "fresh_authority_present"), False),
        (("post_expiry_attempt", "raw_handle_present"), False),
        (("post_expiry_attempt", "raw_locator_present"), False),
        (("enforcement_decision", "outcome"), C_OUTCOME),
        (("enforcement_decision", "fresh_authority_required"), True),
        (("enforcement_decision", "allow_new_observation"), False),
        (("enforcement_decision", "allow_export"), False),
        (("enforcement_decision", "allow_rehydration"), False),
        (("enforcement_decision", "rate_limit_debited"), True),
        (("enforcement_decision", "rollback_accepted"), False),
        (("enforcement_decision", "forked_enforcement_accepted"), False),
        (("enforcement_decision", "stale_root_accepted"), False),
        (("evidence_after_enforcement", "expired_root_not_queryable"), True),
        (("evidence_after_enforcement", "raw_payload_visible"), False),
        (("evidence_after_enforcement", "secret_material_present"), False),
    ),
    'spec/examples/removable.media.local.post_detach.reader.use.ledger.retention.expiry.receipt.json': (
        (("expiry_enforcement_receipt", "posture"), C_POSTURE),
        (("expiry_enforcement_receipt", "kind"), C_KIND),
        (("expiry_enforcement_receipt", "schema"), SCHEMA_REL),
        (("expiry_enforcement_receipt", "digest"), C_DIGEST),
        (("expiry_enforcement_receipt", "negative_fixture_policy"), C_POLICY),
        (("expiry_enforcement_receipt", "enforcement_floor"), C_FLOOR),
        (("expiry_enforcement_receipt", "enforcement_receipt_required"), True),
        (("expiry_enforcement_receipt", "expired_root_new_observation_allowed"), False),
        (("expiry_enforcement_receipt", "post_expiry_fresh_authority_required"), True),
    ),
    'spec/examples/removable.media.local.post_detach.contract.json': (
        (("backend_evidence", "successor_index_reader_use_ledger_retention_expiry_enforcement_posture"), C_POSTURE),
        (("backend_evidence", "successor_index_reader_use_ledger_retention_expiry_enforcement_kind"), C_KIND),
        (("backend_evidence", "successor_index_reader_use_ledger_retention_expiry_enforcement_schema"), SCHEMA_REL),
        (("backend_evidence", "successor_index_reader_use_ledger_retention_expiry_enforcement_digest"), C_DIGEST),
        (("backend_evidence", "successor_index_reader_use_ledger_retention_expiry_enforcement_negative_fixture_policy"), C_POLICY),
        (("backend_evidence", "successor_index_reader_use_ledger_retention_expiry_enforcement_required"), True),
        (("backend_evidence", "successor_index_reader_use_ledger_retention_expiry_enforcement_floor"), C_FLOOR),
        (("failure_policy", "successor_index_reader_use_ledger_retention_expiry_enforcement_missing"), "fail-closed"),
        (("failure_policy", "successor_index_reader_use_ledger_retention_expiry_enforcement_expired_root_allowed"), "fail-closed"),
        (("failure_policy", "successor_index_reader_use_ledger_retention_expiry_enforcement_raw_attempt_leak"), "fail-closed"),
    ),
    'spec/examples/content.import.plan.removable-media-local-ingest.json': (
        (("execution", "post_detach_successor_index_reader_use_ledger_retention_expiry_enforcement_posture"), C_POSTURE),
        (("execution", "post_detach_successor_index_reader_use_ledger_retention_expiry_enforcement_digest"), C_DIGEST),
        (("execution", "post_detach_successor_index_reader_use_ledger_retention_expiry_enforcement_schema"), SCHEMA_REL),
        (("execution", "post_detach_successor_index_reader_use_ledger_retention_expiry_enforcement_negative_fixture_policy"), C_POLICY),
        (("execution", "post_detach_successor_index_reader_use_ledger_retention_expiry_enforcement_required"), True),
        (("operations", 0, "params", "post_detach_successor_index_reader_use_ledger_retention_expiry_enforcement_posture"), C_POSTURE),
    ),
    'spec/examples/content.import.receipt.removable-media-local-ingest.json': (
        (("execution", "post_detach_successor_index_reader_use_ledger_retention_expiry_enforcement_posture"), C_POSTURE),
        (("execution", "post_detach_successor_index_reader_use_ledger_retention_expiry_enforcement_digest"), C_DIGEST),
        (("execution", "post_detach_successor_index_reader_use_ledger_retention_expiry_enforcement_schema"), SCHEMA_REL),
        (("execution", "post_detach_successor_index_reader_use_ledger_retention_expiry_enforcement_negative_fixture_policy"), C_POLICY),
        (("execution", "post_detach_successor_index_reader_use_ledger_retention_expiry_enforcement_required"), True),
    ),
    'spec/examples/preopen.map.removable-media-local-ingest-post-detach.json': (
        (("successor_index_reader_use_ledger_retention_expiry_enforcement_posture",), C_POSTURE),
        (("successor_index_reader_use_ledger_retention_expiry_enforcement_kind",), C_KIND),
        (("successor_index_reader_use_ledger_retention_expiry_enforcement_schema",), SCHEMA_REL),
        (("successor_index_reader_use_ledger_retention_expiry_enforcement_digest",), C_DIGEST),
        (("successor_index_reader_use_ledger_retention_expiry_enforcement_negative_fixture_policy",), C_POLICY),
        (("successor_index_reader_use_ledger_retention_expiry_enforcement_required",), True),
        (("successor_index_reader_use_ledger_retention_expiry_enforcement_floor",), C_FLOOR),
    ),
}

TEXT_REQUIREMENTS = {
    'docs/775-removable-media-local-fallback-post-detach-reader-use-ledger-retention-expiry-enforcement-is-typed-and-negative-tested.md': (C_POSTURE, C_DIGEST, C_POLICY, SCHEMA_REL, EXAMPLE_REL, INVALID_DIR, C_OUTCOME, C_FLOOR, 'require_absent_tokens'),
    'adrs/ADR-0364-removable-media-local-fallback-post-detach-reader-use-ledger-retention-expiry-enforcement-is-typed-and-negative-tested.md': (C_POSTURE, C_DIGEST, C_POLICY, C_OUTCOME, 'expired roots', 'fresh authority'),
    'README.md': ('ADR-0364', C_POSTURE),
    'docs/00-index.md': ('ADR-0364', 'docs/775-removable-media-local-fallback-post-detach-reader-use-ledger-retention-expiry-enforcement-is-typed-and-negative-tested.md', C_POSTURE),
    'CHANGELOG.md': ('2026-05-25r520', CHECKER_NAME, C_POSTURE, 'require_absent_tokens'),
    'docs/99-llm-runbook.md': (CHECKER_NAME, C_POSTURE, 'post-expiry enforcement'),
    'docs/110-juicy-os-lessons.md': ('r520 removable-media reader-use ledger retention expiry enforcement', C_POSTURE),
    'docs/266-open-questions-and-risk-register.md': ('r520 removable-media reader-use ledger retention expiry enforcement risk note', C_POSTURE),
    'docs/293-attribute-indexed-metadata-and-live-queries.md': ('r520 removable-media reader-use ledger retention expiry enforcement', C_POSTURE),
    'docs/98-archive-hygiene.md': (CHECKER_NAME, C_POSTURE, 'require_absent_tokens'),
}

FORBIDDEN_TOKENS = {
    EXAMPLE_REL: ('/media/', '/Volumes/', 'file://', 'raw-path:', 'johnny', 'j30385433', 'secret=')
}


def main() -> int:
    require_guardrail_contract(
        ROOT,
        schema_rel=SCHEMA_REL,
        example_rel=EXAMPLE_REL,
        invalid_dir=INVALID_DIR,
        expected_invalid_fixtures=REQUIRED_INVALID_FIXTURES,
        json_requirements=JSON_REQUIREMENTS,
        text_requirements=TEXT_REQUIREMENTS,
        checker_name=CHECKER_NAME,
        label='r520 reader-use-ledger-retention-expiry-enforcement token',
    )
    require_absent_tokens(ROOT, FORBIDDEN_TOKENS, label='raw post-expiry enforcement sample')
    print('removable-media post-detach reader-use ledger retention expiry enforcement receipt check passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
