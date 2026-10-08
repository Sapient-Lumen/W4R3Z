#!/usr/bin/env python3
"""Validate FT-0181 live-window stop/rollback card local gate."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from ft0181_validation_fixtures import build_valid_sent_contact_status
from record_ft0181_workbench_review import OPERATOR_CONFIRMATION as REVIEW_CONFIRMATION, build_review
from record_ft0181_first_packet_decision import OPERATOR_CONFIRMATION as DECISION_CONFIRMATION, build_decision
from record_ft0181_post_decision_change_ticket import OPERATOR_CONFIRMATION as TICKET_CONFIRMATION, build_change_ticket
from record_ft0181_activation_receipt import OPERATOR_CONFIRMATION as ACTIVATION_CONFIRMATION, build_activation_receipt
from record_ft0181_live_window_card import OPERATOR_CONFIRMATION, build_live_window_card
from ft0181_field_guards import owner_live_window_card_integrity_error

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / 'scratch' / 'field' / 'ft0181' / 'validation' / 'ft0181-live-window-card'


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
            source_slug='ft0181-live-window-card-source-send-log',
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


def build_valid_ticket() -> Path:
    source_packet = TMP / 'activation-source-packets' / 'real-owner-packet.csv'
    source_packet.parent.mkdir(parents=True, exist_ok=True)
    source_packet.write_text('field_key,owner_attested_class,decision_effect\nallowed_count,aggregate_owner_attested,changes_one_bounded_slice\n', encoding='utf-8')
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
    build_activation_receipt(
        decision=TMP / 'owner-first-packet-decisions' / 'valid' / 'first-packet-decision.json',
        source_packet=source_packet,
        source_truth_class='SRC2',
        accepted_field_count=1,
        reviewer_role_count=2,
        dictionary_or_map_ref_count=1,
        blocked_or_trimmed_field_count=1,
        operator_confirmation=ACTIVATION_CONFIRMATION,
        output_dir=TMP / 'owner-activation-receipts' / 'valid',
    )
    build_change_ticket(
        decision=TMP / 'owner-first-packet-decisions' / 'valid' / 'first-packet-decision.json',
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
        operator_confirmation=TICKET_CONFIRMATION,
        activation_receipt=TMP / 'owner-activation-receipts' / 'valid' / 'activation-receipt.json',
        output_dir=TMP / 'owner-post-decision-change-tickets' / 'valid',
    )
    return TMP / 'owner-post-decision-change-tickets' / 'valid' / 'post-decision-change-ticket.json'


if TMP.exists():
    shutil.rmtree(TMP)
for stale_packet_root in (ROOT / 'scratch' / 'field' / 'ft0181').glob(f'activation-source-validation-{TMP.name.removeprefix("check-")}*-source-packets'):
    shutil.rmtree(stale_packet_root, ignore_errors=True)
TMP.mkdir(parents=True, exist_ok=True)
errors: list[str] = []
ticket = build_valid_ticket()

summary = build_live_window_card(
    ticket=ticket,
    window_state='staged',
    source_truth_class='SRC2',
    window_day_count=5,
    allowed_activity_count=1,
    prohibited_activity_count=5,
    stop_trigger_count=3,
    rollback_step_count=3,
    rollback_owner_role_count=1,
    evidence_readout_count=3,
    public_claim_ceiling='example-only-no-outcome-claim',
    no_expansion_confirmed=True,
    human_pause_confirmed=True,
    fallback_route_confirmed=True,
    raw_learner_data_present=False,
    protected_facts_present=False,
    security_payloads_present=False,
    public_claim_upgrade_requested=False,
    operator_confirmation=OPERATOR_CONFIRMATION,
    output_dir=TMP / 'owner-live-window-cards' / 'valid',
)
if summary.get('outcome') != 'LIVE-WINDOW-CARD-RECORDED':
    fail(errors, f'valid live-window card should record: {summary}')
card_path = TMP / 'owner-live-window-cards' / 'valid' / 'live-window-card.json'
card = load_json(card_path)
err = owner_live_window_card_integrity_error(card, archive_root=ROOT)
if err:
    fail(errors, f'valid live-window card should pass guard: {err}')
if card.get('acceptance_state') != 'NOT_ACCEPTED' or card.get('evidence_state') != 'not_evidence':
    fail(errors, 'live-window card must remain NOT_ACCEPTED and not_evidence')
if card.get('required_next_surface') != 'docs/30-operations/ft0181-end-of-window-readout-disposition-gate.md':
    fail(errors, 'live-window card must route only to end-of-window readout gate')

stale_hash_card = dict(card)
stale_hash_card['source_post_decision_change_ticket'] = dict(card.get('source_post_decision_change_ticket', {}))
stale_hash_card['source_post_decision_change_ticket']['ticket_sha256'] = '0' * 64
err = owner_live_window_card_integrity_error(stale_hash_card, archive_root=ROOT)
if err != 'source_post_decision_change_ticket.ticket_sha256 does not match referenced ticket':
    fail(errors, f'stale ticket hash should block live-window card integrity: {err}')

text = card_path.read_text(encoding='utf-8') + (TMP / 'owner-live-window-cards' / 'valid' / 'LIVE-WINDOW-CARD-SUMMARY.md').read_text(encoding='utf-8')
for forbidden in ['eligible 120', 'course operations lead via', 'Human fallback is normal staff outreach', 'raw LMS telemetry is attached', '@example']:
    if forbidden in text:
        fail(errors, f'live-window card leaked owner answer/contact content: {forbidden}')

blocked_cases = [
    ({'window_day_count': 15}, 'overlong window'),
    ({'allowed_activity_count': 0, 'window_state': 'staged'}, 'staged without allowed activity'),
    ({'prohibited_activity_count': 0}, 'missing prohibition'),
    ({'stop_trigger_count': 0}, 'missing stop trigger'),
    ({'rollback_step_count': 0}, 'missing rollback step'),
    ({'rollback_owner_role_count': 0}, 'missing rollback owner'),
    ({'evidence_readout_count': 0, 'window_state': 'active'}, 'active without readout'),
    ({'no_expansion_confirmed': False}, 'missing no-expansion confirmation'),
    ({'human_pause_confirmed': False}, 'missing human pause confirmation'),
    ({'fallback_route_confirmed': False}, 'missing fallback confirmation'),
    ({'source_truth_class': 'SRC0', 'window_state': 'active'}, 'active weak source'),
    ({'window_state': 'blocked-no-real-packet', 'source_truth_class': 'SRC2'}, 'blocked with SRC2'),
    ({'window_state': 'blocked-no-real-packet', 'window_day_count': 1}, 'blocked with day'),
    ({'raw_learner_data_present': True}, 'raw learner'),
    ({'protected_facts_present': True}, 'protected'),
    ({'security_payloads_present': True}, 'security'),
    ({'public_claim_upgrade_requested': True}, 'public claim upgrade'),
]
base = dict(
    ticket=ticket,
    window_state='staged',
    source_truth_class='SRC2',
    window_day_count=5,
    allowed_activity_count=1,
    prohibited_activity_count=5,
    stop_trigger_count=3,
    rollback_step_count=3,
    rollback_owner_role_count=1,
    evidence_readout_count=3,
    public_claim_ceiling='example-only-no-outcome-claim',
    no_expansion_confirmed=True,
    human_pause_confirmed=True,
    fallback_route_confirmed=True,
    raw_learner_data_present=False,
    protected_facts_present=False,
    security_payloads_present=False,
    public_claim_upgrade_requested=False,
    operator_confirmation=OPERATOR_CONFIRMATION,
)
for overrides, label in blocked_cases:
    args = dict(base)
    args.update(overrides)
    args['output_dir'] = TMP / 'owner-live-window-cards' / f'blocked-{label.replace(" ", "-")}'
    try:
        build_live_window_card(**args)
        fail(errors, f'live-window card with {label} problem should block')
    except ValueError as exc:
        payload = json.loads(str(exc))
        if payload.get('ok') is not False or 'LIVE-WINDOW-CARD' not in payload.get('outcome', ''):
            fail(errors, f'{label} block should be machine-readable: {payload}')


# A ready_for_real_packet ticket cannot source a live/staged window; it must wait for active_change.
ready_ticket = TMP / 'owner-post-decision-change-tickets' / 'ready' / 'post-decision-change-ticket.json'
ready_ticket.parent.mkdir(parents=True, exist_ok=True)
ready_data = load_json(ticket)
ready_data['ticket_state'] = 'ready_for_real_packet'
ready_data['source_activation_receipt'] = None
ready_ticket.write_text(json.dumps(ready_data, indent=2) + '\n', encoding='utf-8')
try:
    build_live_window_card(**{**base, 'ticket': ready_ticket, 'output_dir': TMP / 'owner-live-window-cards' / 'ready-ticket-block'})
    fail(errors, 'ready_for_real_packet ticket should not source a live-window card')
except ValueError as exc:
    payload = json.loads(str(exc))
    if payload.get('outcome') != 'LIVE-WINDOW-CARD-TICKET-STATE-BLOCKED':
        fail(errors, f'ready-ticket live-window block missing code: {payload}')

# Tampered post-decision tickets cannot source a live-window card.
tampered_ticket = TMP / 'owner-post-decision-change-tickets' / 'tampered' / 'post-decision-change-ticket.json'
tampered_ticket.parent.mkdir(parents=True, exist_ok=True)
tampered_data = load_json(ticket)
tampered_data['acceptance_state'] = 'ACCEPTED'
tampered_ticket.write_text(json.dumps(tampered_data, indent=2) + '\n', encoding='utf-8')
try:
    build_live_window_card(**{**base, 'ticket': tampered_ticket, 'output_dir': TMP / 'owner-live-window-cards' / 'tampered-ticket'})
    fail(errors, 'tampered accepted post-decision ticket should not source a live-window card')
except ValueError as exc:
    payload = json.loads(str(exc))
    if payload.get('outcome') != 'LIVE-WINDOW-CARD-TICKET-BLOCKED':
        fail(errors, f'tampered ticket block missing code: {payload}')

# Output into controlled docs space is blocked.
try:
    build_live_window_card(**{**base, 'output_dir': ROOT / 'docs' / 'bad-live-window-card'})
    fail(errors, 'live-window card output to docs should be blocked')
except ValueError as exc:
    payload = json.loads(str(exc))
    if payload.get('outcome') != 'LIVE-WINDOW-CARD-OUTPUT-BLOCKED':
        fail(errors, f'controlled output block missing code: {payload}')

if errors:
    shutil.rmtree(TMP)
    raise SystemExit('check_ft0181_live_window_card: FAIL\n- ' + '\n- '.join(errors))
shutil.rmtree(TMP)
for stale_packet_root in (ROOT / 'scratch' / 'field' / 'ft0181').glob(f'activation-source-validation-{TMP.name.removeprefix("check-")}*-source-packets'):
    shutil.rmtree(stale_packet_root, ignore_errors=True)
print('check_ft0181_live_window_card: OK (source-ticket validation, stop/rollback counts, no-expansion controls, minimization, blocks, output boundary)')
