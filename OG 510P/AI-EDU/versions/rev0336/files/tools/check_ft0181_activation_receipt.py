#!/usr/bin/env python3
"""Validate FT-0181 activation receipt gate before active_change ticketing."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from ft0181_validation_fixtures import build_valid_sent_contact_status
from record_ft0181_workbench_review import OPERATOR_CONFIRMATION as REVIEW_CONFIRMATION, build_review
from record_ft0181_first_packet_decision import OPERATOR_CONFIRMATION as DECISION_CONFIRMATION, build_decision
from record_ft0181_activation_receipt import OPERATOR_CONFIRMATION, build_activation_receipt
from ft0181_field_guards import activation_receipt_integrity_error

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / 'scratch' / 'field' / 'ft0181' / 'activation-receipt-validation'


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def write_source_contact_status(path: Path) -> Path:
    try:
        return build_valid_sent_contact_status(
            path,
            root=ROOT,
            sent_date='2026-06-13',
            response_due_date='2026-06-20',
            status_date='2026-06-13',
            source_slug='activation-receipt-source-send-log',
        )
    except RuntimeError as exc:
        raise SystemExit(str(exc))


def write_seed(path: Path, source_contact_status: Path, source_packet: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        'seed_type': 'FT-0181-owner-packet-workbench-seed',
        'seed_version': 'rev0285',
        'created_at_utc': '2026-06-13T00:00:01Z',
        'source_truth_status': 'UNVERIFIED_OWNER_REPLY_PENDING_CUSTODY',
        'acceptance_state': 'NOT_ACCEPTED',
        'required_next_surface': 'docs/30-operations/ft0181-owner-packet-workbench.md',
        'source_contact_status': {
            'reference': rel(source_contact_status),
            'contact_status': 'SENT_AWAITING_REPLY',
            'sent_date': '2026-06-13',
            'response_due_date': '2026-06-20',
            'status_date': '2026-06-13',
            'attempt_count': 1,
            'evidence_state': 'not_evidence',
            'claim_effect': 'none; provenance gate only',
            'revalidated_for_seed': True,
        },
        'source_csv': {
            'basename': source_packet.name,
            'sha256': sha256_file(source_packet),
            'reference': rel(source_packet),
            'path_scope': 'inside_archive_tree',
        },
        'content_minimization': {
            'copies_owner_answers': False,
            'copies_raw_csv_rows': False,
            'copies_proceed_staged_row_text': False,
            'copies_contact_details': False,
            'source_contact_status_revalidated': True,
            'contains_hashes_and_next_steps_only': True,
        },
        'claim_ceiling': 'Workbench seed only; not SRC2+ acceptance, not custody evidence, not closure evidence, not public-summary support.',
        'ft0181_status': 'live',
    }, indent=2) + '\n', encoding='utf-8')
    return path


def build_valid_decision(source_packet: Path) -> Path:
    source_contact = write_source_contact_status(TMP / 'owner-contact-status' / 'sent' / 'contact-status.json')
    seed = write_seed(TMP / 'owner-reply-workbench-seeds' / 'aiedu-sr-003' / 'workbench-seed.json', source_contact, source_packet)
    build_review(
        seed=seed,
        decision='proceed-decision-board',
        source_truth_class='SRC2-CANDIDATE-NOT-ACCEPTED',
        review_basis='owner-attested-aggregate',
        surviving_field_count=3,
        decision_changed_count=2,
        local_only_field_count=1,
        trimmed_field_count=2,
        reask_field_count=0,
        reviewer_role_count=2,
        raw_learner_data_present=False,
        protected_facts_present=False,
        security_payloads_present=False,
        public_claim_upgrade_requested=False,
        operator_confirmation=REVIEW_CONFIRMATION,
        output_dir=TMP / 'owner-workbench-reviews' / 'proceed',
    )
    build_decision(
        review=TMP / 'owner-workbench-reviews' / 'proceed' / 'workbench-review.json',
        authority_action='keep-lower-ceiling',
        evidence_action='downgrade',
        construct_action='keep-teacher-review',
        public_action='draft-only',
        lifecycle_action='watch',
        changed_slice_count=5,
        rollback_owner_role_count=1,
        raw_learner_data_present=False,
        protected_facts_present=False,
        security_payloads_present=False,
        public_claim_upgrade_requested=False,
        operator_confirmation=DECISION_CONFIRMATION,
        output_dir=TMP / 'owner-first-packet-decisions' / 'valid',
    )
    return TMP / 'owner-first-packet-decisions' / 'valid' / 'first-packet-decision.json'


if TMP.exists():
    shutil.rmtree(TMP)
TMP.mkdir(parents=True, exist_ok=True)
errors: list[str] = []
source_packet = TMP / 'returned-owner-source-packets' / 'real-owner-packet.csv'
source_packet.parent.mkdir(parents=True, exist_ok=True)
source_packet.write_text('field_key,owner_attested_class,decision_effect\nallowed_count,aggregate_owner_attested,changes_one_bounded_slice\n', encoding='utf-8')
decision = build_valid_decision(source_packet)

summary = build_activation_receipt(
    decision=decision,
    source_packet=source_packet,
    source_truth_class='SRC2',
    accepted_field_count=1,
    reviewer_role_count=2,
    dictionary_or_map_ref_count=1,
    blocked_or_trimmed_field_count=1,
    operator_confirmation=OPERATOR_CONFIRMATION,
    output_dir=TMP / 'owner-activation-receipts' / 'valid',
)
if summary.get('outcome') != 'ACTIVATION-RECEIPT-RECORDED':
    fail(errors, f'valid activation receipt should record: {summary}')
receipt_path = TMP / 'owner-activation-receipts' / 'valid' / 'activation-receipt.json'
receipt = load_json(receipt_path)
err = activation_receipt_integrity_error(receipt, archive_root=ROOT)
if err:
    fail(errors, f'valid activation receipt should pass guard: {err}')
if receipt.get('source_truth_class') != 'SRC2' or receipt.get('evidence_state') != 'not_evidence':
    fail(errors, 'activation receipt must bind SRC2 source class while remaining not_evidence')
if receipt.get('source_packet', {}).get('matches_decision_chain_source_csv_sha256') is not True:
    fail(errors, 'activation receipt must assert source packet hash matches decision-chain source CSV hash')
if receipt.get('source_packet', {}).get('decision_chain_source_csv_sha256') != sha256_file(source_packet):
    fail(errors, 'activation receipt must preserve the exact source CSV hash from the decision chain')
if receipt.get('decision_source_chain', {}).get('workbench_seed_reference') is None:
    fail(errors, 'activation receipt must preserve decision source-chain seed reference')
text = receipt_path.read_text(encoding='utf-8') + (TMP / 'owner-activation-receipts' / 'valid' / 'ACTIVATION-RECEIPT-SUMMARY.md').read_text(encoding='utf-8')
for forbidden in ['eligible 120', 'course operations lead via', 'Human fallback is normal staff outreach', 'raw LMS telemetry is attached', '@example']:
    if forbidden in text:
        fail(errors, f'activation receipt leaked owner answer/contact content: {forbidden}')

blocked_cases = [
    ({'source_truth_class': 'SRC1'}, 'weak source truth'),
    ({'accepted_field_count': 0}, 'no accepted fields'),
    ({'reviewer_role_count': 1}, 'single reviewer'),
    ({'dictionary_or_map_ref_count': 0}, 'no dictionary or map'),
    ({'operator_confirmation': 'human-reviewed-minimized-workbench-record'}, 'wrong confirmation'),
]
base = dict(
    decision=decision,
    source_packet=source_packet,
    source_truth_class='SRC2',
    accepted_field_count=1,
    reviewer_role_count=2,
    dictionary_or_map_ref_count=1,
    blocked_or_trimmed_field_count=0,
    operator_confirmation=OPERATOR_CONFIRMATION,
)
for overrides, label in blocked_cases:
    args = dict(base)
    args.update(overrides)
    args['output_dir'] = TMP / 'owner-activation-receipts' / f'blocked-{label.replace(" ", "-")}'
    try:
        build_activation_receipt(**args)
        fail(errors, f'activation receipt with {label} problem should block')
    except ValueError as exc:
        payload = json.loads(str(exc))
        if payload.get('ok') is not False or 'ACTIVATION-RECEIPT' not in payload.get('outcome', ''):
            fail(errors, f'{label} block should be machine-readable: {payload}')

unrelated_packet = TMP / 'returned-owner-source-packets' / 'unrelated-owner-packet.csv'
unrelated_packet.write_text('field_key,owner_attested_class,decision_effect\nother_count,aggregate_owner_attested,unrelated\n', encoding='utf-8')
try:
    build_activation_receipt(**{**base, 'source_packet': unrelated_packet, 'output_dir': TMP / 'owner-activation-receipts' / 'unrelated-packet'})
    fail(errors, 'unrelated source packet with a different hash must not activate a decision chain')
except ValueError as exc:
    payload = json.loads(str(exc))
    if payload.get('outcome') != 'ACTIVATION-RECEIPT-SOURCE-LINEAGE-BLOCKED':
        fail(errors, f'unrelated packet block missing lineage code: {payload}')

try:
    build_activation_receipt(**{**base, 'source_packet': ROOT / 'examples' / 'real-import-acceptance' / 'no-real-data-ft0181-acceptance.json', 'output_dir': TMP / 'owner-activation-receipts' / 'controlled-example'})
    fail(errors, 'archive examples must not be accepted as real source packets')
except ValueError as exc:
    payload = json.loads(str(exc))
    if payload.get('outcome') != 'ACTIVATION-RECEIPT-SOURCE-PACKET-BLOCKED':
        fail(errors, f'controlled source-packet block missing code: {payload}')

try:
    checker_packet = ROOT / 'scratch' / 'checks' / 'check-ft0181-activation-source-packet' / 'same-hash-owner-packet.csv'
    checker_packet.parent.mkdir(parents=True, exist_ok=True)
    checker_packet.write_text(source_packet.read_text(encoding='utf-8'), encoding='utf-8')
    build_activation_receipt(**{**base, 'source_packet': checker_packet, 'output_dir': TMP / 'owner-activation-receipts' / 'checker-source-packet'})
    fail(errors, 'checker-scratch source packet with a matching hash must not activate a real-packet receipt')
except ValueError as exc:
    payload = json.loads(str(exc))
    if payload.get('outcome') != 'ACTIVATION-RECEIPT-SOURCE-PACKET-BLOCKED':
        fail(errors, f'checker source-packet block missing code: {payload}')
finally:
    shutil.rmtree(ROOT / 'scratch' / 'checks' / 'check-ft0181-activation-source-packet', ignore_errors=True)

smoke_packet = TMP / 'returned-owner-source-packets' / 'smoke.csv'
smoke_packet.write_text('synthetic smoke fixture,src0-smoke,not a returned owner packet\n', encoding='utf-8')
try:
    build_activation_receipt(**{**base, 'source_packet': smoke_packet, 'output_dir': TMP / 'owner-activation-receipts' / 'smoke'})
    fail(errors, 'smoke-marked packet must not be accepted as activation evidence')
except ValueError as exc:
    payload = json.loads(str(exc))
    if payload.get('outcome') not in {'ACTIVATION-RECEIPT-INTEGRITY-BLOCKED', 'ACTIVATION-RECEIPT-SOURCE-LINEAGE-BLOCKED'}:
        fail(errors, f'smoke source-packet block missing code: {payload}')

try:
    build_activation_receipt(**{**base, 'output_dir': ROOT / 'docs' / 'bad-activation-receipt'})
    fail(errors, 'activation receipt output to docs should be blocked')
except ValueError as exc:
    payload = json.loads(str(exc))
    if payload.get('outcome') != 'ACTIVATION-RECEIPT-OUTPUT-BLOCKED':
        fail(errors, f'controlled output block missing code: {payload}')

if errors:
    shutil.rmtree(TMP)
    raise SystemExit('check_ft0181_activation_receipt: FAIL\n- ' + '\n- '.join(errors))
shutil.rmtree(TMP)
print('check_ft0181_activation_receipt: OK (field-lane source packet guard, two-role activation receipt, no active-change bypass)')
