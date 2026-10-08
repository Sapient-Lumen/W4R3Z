#!/usr/bin/env python3
"""Validate FT-0181 post-decision change-ticket local gate."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from ft0181_validation_fixtures import build_valid_sent_contact_status
from record_ft0181_workbench_review import OPERATOR_CONFIRMATION as REVIEW_CONFIRMATION, build_review
from record_ft0181_first_packet_decision import OPERATOR_CONFIRMATION as DECISION_CONFIRMATION, build_decision
from record_ft0181_post_decision_change_ticket import OPERATOR_CONFIRMATION, build_change_ticket
from record_ft0181_activation_receipt import OPERATOR_CONFIRMATION as ACTIVATION_CONFIRMATION, build_activation_receipt
from ft0181_field_guards import owner_post_decision_change_ticket_integrity_error

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / 'scratch' / 'field' / 'ft0181' / 'validation' / 'ft0181-post-decision-change-ticket'


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
            source_slug='ft0181-post-decision-change-ticket-source-send-log',
        )
    except RuntimeError as exc:
        raise SystemExit(str(exc))


def write_seed(path: Path, source_contact_status: Path, source_packet: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        'seed_type': 'FT-0181-owner-packet-workbench-seed',
        'seed_version': 'rev0278',
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
        source_truth_class='SRC2',
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
shutil.rmtree(ROOT / 'scratch' / 'checks' / 'ft0181-post-decision-ticket-source-chain-negative', ignore_errors=True)
for stale_packet_root in (ROOT / 'scratch' / 'field' / 'ft0181').glob(f'activation-source-validation-{TMP.name.removeprefix("check-")}*-source-packets'):
    shutil.rmtree(stale_packet_root, ignore_errors=True)
TMP.mkdir(parents=True, exist_ok=True)
errors: list[str] = []
source_packet = TMP / 'activation-source-packets' / 'real-owner-packet.csv'
source_packet.parent.mkdir(parents=True, exist_ok=True)
source_packet.write_text('field_key,owner_attested_class,decision_effect\nallowed_count,aggregate_owner_attested,changes_one_bounded_slice\n', encoding='utf-8')
decision = build_valid_decision(source_packet)

summary = build_change_ticket(
    decision=decision,
    ticket_state='ready-for-real-packet',
    change_class='pct-c-sandbox-adjustment',
    source_truth_required='SRC2',
    public_claim_ceiling='example-only-no-outcome-claim',
    allowed_change_count=1,
    prohibited_change_count=4,
    rollback_trigger_count=3,
    rollback_owner_role_count=1,
    live_window_required=True,
    raw_learner_data_present=False,
    protected_facts_present=False,
    security_payloads_present=False,
    public_claim_upgrade_requested=False,
    operator_confirmation=OPERATOR_CONFIRMATION,
    output_dir=TMP / 'owner-post-decision-change-tickets' / 'valid',
)
if summary.get('outcome') != 'POST-DECISION-CHANGE-TICKET-RECORDED':
    fail(errors, f'valid post-decision change ticket should record: {summary}')
ticket_path = TMP / 'owner-post-decision-change-tickets' / 'valid' / 'post-decision-change-ticket.json'
ticket = load_json(ticket_path)
err = owner_post_decision_change_ticket_integrity_error(ticket, archive_root=ROOT)
if err:
    fail(errors, f'valid change ticket should pass guard: {err}')
if ticket.get('acceptance_state') != 'NOT_ACCEPTED' or ticket.get('evidence_state') != 'not_evidence':
    fail(errors, 'post-decision ticket must remain NOT_ACCEPTED and not_evidence')
if ticket.get('required_next_surface') != 'docs/30-operations/ft0181-live-window-stop-rollback-card.md':
    fail(errors, 'post-decision ticket must route only to live-window stop/rollback card')

stale_hash_ticket = dict(ticket)
stale_hash_ticket['source_first_packet_decision'] = dict(ticket.get('source_first_packet_decision', {}))
stale_hash_ticket['source_first_packet_decision']['decision_sha256'] = '0' * 64
err = owner_post_decision_change_ticket_integrity_error(stale_hash_ticket, archive_root=ROOT)
if err != 'source_first_packet_decision.decision_sha256 does not match referenced decision':
    fail(errors, f'stale decision hash should block post-decision ticket integrity: {err}')

build_activation_receipt(
    decision=decision,
    source_packet=source_packet,
    source_truth_class='SRC2',
    accepted_field_count=1,
    reviewer_role_count=2,
    dictionary_or_map_ref_count=1,
    blocked_or_trimmed_field_count=1,
    operator_confirmation=ACTIVATION_CONFIRMATION,
    output_dir=TMP / 'owner-activation-receipts' / 'valid',
)
active_summary = build_change_ticket(
    decision=decision,
    ticket_state='active-change',
    change_class='pct-c-sandbox-adjustment',
    source_truth_required='SRC2',
    public_claim_ceiling='example-only-no-outcome-claim',
    allowed_change_count=1,
    prohibited_change_count=4,
    rollback_trigger_count=3,
    rollback_owner_role_count=1,
    live_window_required=True,
    raw_learner_data_present=False,
    protected_facts_present=False,
    security_payloads_present=False,
    public_claim_upgrade_requested=False,
    operator_confirmation=OPERATOR_CONFIRMATION,
    activation_receipt=TMP / 'owner-activation-receipts' / 'valid' / 'activation-receipt.json',
    output_dir=TMP / 'owner-post-decision-change-tickets' / 'active-with-receipt',
)
if active_summary.get('outcome') != 'POST-DECISION-CHANGE-TICKET-RECORDED':
    fail(errors, f'active_change with valid activation receipt should record: {active_summary}')
active_ticket = load_json(TMP / 'owner-post-decision-change-tickets' / 'active-with-receipt' / 'post-decision-change-ticket.json')
err = owner_post_decision_change_ticket_integrity_error(active_ticket, archive_root=ROOT)
if err:
    fail(errors, f'active_change with valid activation receipt should pass guard: {err}')
if not isinstance(active_ticket.get('source_activation_receipt'), dict):
    fail(errors, 'active_change ticket must snapshot source_activation_receipt')
text = ticket_path.read_text(encoding='utf-8') + (TMP / 'owner-post-decision-change-tickets' / 'valid' / 'POST-DECISION-CHANGE-TICKET-SUMMARY.md').read_text(encoding='utf-8')
for forbidden in ['eligible 120', 'course operations lead via', 'Human fallback is normal staff outreach', 'raw LMS telemetry is attached', '@example']:
    if forbidden in text:
        fail(errors, f'post-decision change ticket leaked owner answer/contact content: {forbidden}')

blocked_cases = [
    ({'ticket_state': 'active-change'}, 'active without activation receipt'),
    ({'allowed_change_count': 0, 'ticket_state': 'active-change'}, 'active without allowed change'),
    ({'prohibited_change_count': 0}, 'missing prohibited change'),
    ({'rollback_trigger_count': 0}, 'missing rollback trigger'),
    ({'rollback_owner_role_count': 0}, 'missing rollback owner'),
    ({'live_window_required': False, 'ticket_state': 'active-change'}, 'active without live-window card'),
    ({'change_class': 'pct-d-bounded-pilot', 'source_truth_required': 'SRC1'}, 'pilot weak source'),
    ({'change_class': 'pct-d-bounded-pilot', 'live_window_required': False}, 'pilot no live window'),
    ({'raw_learner_data_present': True}, 'raw learner'),
    ({'protected_facts_present': True}, 'protected'),
    ({'security_payloads_present': True}, 'security'),
    ({'public_claim_upgrade_requested': True}, 'public claim upgrade'),
]
base = dict(
    decision=decision,
    ticket_state='ready-for-real-packet',
    change_class='pct-c-sandbox-adjustment',
    source_truth_required='SRC2',
    public_claim_ceiling='example-only-no-outcome-claim',
    allowed_change_count=1,
    prohibited_change_count=4,
    rollback_trigger_count=3,
    rollback_owner_role_count=1,
    live_window_required=True,
    raw_learner_data_present=False,
    protected_facts_present=False,
    security_payloads_present=False,
    public_claim_upgrade_requested=False,
    operator_confirmation=OPERATOR_CONFIRMATION,
)
for overrides, label in blocked_cases:
    args = dict(base)
    args.update(overrides)
    args['output_dir'] = TMP / 'owner-post-decision-change-tickets' / f'blocked-{label.replace(" ", "-")}'
    try:
        build_change_ticket(**args)
        fail(errors, f'post-decision change ticket with {label} problem should block')
    except ValueError as exc:
        payload = json.loads(str(exc))
        if payload.get('ok') is not False or 'POST-DECISION-CHANGE-TICKET' not in payload.get('outcome', ''):
            fail(errors, f'{label} block should be machine-readable: {payload}')

# Tampered first-packet decisions cannot source a ticket.
tampered_decision = TMP / 'owner-first-packet-decisions' / 'tampered' / 'first-packet-decision.json'
tampered_decision.parent.mkdir(parents=True, exist_ok=True)
tampered_data = load_json(decision)
tampered_data['acceptance_state'] = 'ACCEPTED'
tampered_decision.write_text(json.dumps(tampered_data, indent=2) + '\n', encoding='utf-8')
try:
    build_change_ticket(**{**base, 'decision': tampered_decision, 'output_dir': TMP / 'owner-post-decision-change-tickets' / 'tampered-decision'})
    fail(errors, 'tampered accepted first-packet decision should not source a post-decision ticket')
except ValueError as exc:
    payload = json.loads(str(exc))
    if payload.get('outcome') != 'POST-DECISION-CHANGE-TICKET-DECISION-BLOCKED':
        fail(errors, f'tampered decision block missing code: {payload}')


# Byte-identical checker-scratch decisions must not source a field change ticket.
checker_decision = ROOT / 'scratch' / 'checks' / 'ft0181-post-decision-ticket-source-chain-negative' / 'first-packet-decision.json'
checker_decision.parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(decision, checker_decision)
try:
    build_change_ticket(**{**base, 'decision': checker_decision, 'output_dir': TMP / 'owner-post-decision-change-tickets' / 'checker-decision-source'})
    fail(errors, 'checker-scratch first-packet decision should not source a post-decision ticket')
except ValueError as exc:
    payload = json.loads(str(exc))
    if payload.get('outcome') != 'POST-DECISION-CHANGE-TICKET-DECISION-BLOCKED':
        fail(errors, f'checker-scratch decision block missing code: {payload}')
    if 'scratch/field/ft0181' not in payload.get('message', ''):
        fail(errors, f'checker-scratch decision block should name the field-lane boundary: {payload}')

try:
    build_change_ticket(**{**base, 'output_dir': ROOT / 'docs' / 'bad-post-decision-ticket'})
    fail(errors, 'post-decision change ticket output to docs should be blocked')
except ValueError as exc:
    payload = json.loads(str(exc))
    if payload.get('outcome') != 'POST-DECISION-CHANGE-TICKET-OUTPUT-BLOCKED':
        fail(errors, f'controlled output block missing code: {payload}')

if errors:
    shutil.rmtree(TMP)
    shutil.rmtree(ROOT / 'scratch' / 'checks' / 'ft0181-post-decision-ticket-source-chain-negative', ignore_errors=True)
    raise SystemExit('check_ft0181_post_decision_change_ticket: FAIL\n- ' + '\n- '.join(errors))
shutil.rmtree(TMP)
shutil.rmtree(ROOT / 'scratch' / 'checks' / 'ft0181-post-decision-ticket-source-chain-negative', ignore_errors=True)
for stale_packet_root in (ROOT / 'scratch' / 'field' / 'ft0181').glob(f'activation-source-validation-{TMP.name.removeprefix("check-")}*-source-packets'):
    shutil.rmtree(stale_packet_root, ignore_errors=True)
print('check_ft0181_post_decision_change_ticket: OK (source-decision validation, source-chain field-lane firebreak, minimized ticket, live-window boundary, blocks, output guard)')
