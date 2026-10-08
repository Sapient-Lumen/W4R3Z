#!/usr/bin/env python3
"""Validate FT-0181 activation/live-window entry brief bridge."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from ft0181_validation_fixtures import build_valid_sent_contact_status
from prepare_ft0181_activation_live_window_brief import build_activation_live_window_brief
from record_ft0181_activation_receipt import OPERATOR_CONFIRMATION as ACTIVATION_CONFIRMATION, build_activation_receipt
from record_ft0181_first_packet_decision import OPERATOR_CONFIRMATION as DECISION_CONFIRMATION, build_decision
from record_ft0181_post_decision_change_ticket import OPERATOR_CONFIRMATION as TICKET_CONFIRMATION, build_change_ticket
from record_ft0181_workbench_review import OPERATOR_CONFIRMATION as REVIEW_CONFIRMATION, build_review
from ft0181_field_guards import owner_activation_live_window_brief_integrity_error

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / 'scratch' / 'field' / 'ft0181' / 'validation' / 'ft0181-activation-live-window-brief'


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
            source_slug='ft0181-activation-live-window-brief-source-send-log',
        )
    except RuntimeError as exc:
        raise SystemExit(str(exc))


def write_seed(path: Path, source_contact_status: Path, source_packet: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        'seed_type': 'FT-0181-owner-packet-workbench-seed',
        'seed_version': 'rev0298',
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


def build_ready_ticket(decision: Path) -> Path:
    build_change_ticket(
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
        operator_confirmation=TICKET_CONFIRMATION,
        output_dir=TMP / 'owner-post-decision-change-tickets' / 'ready',
    )
    return TMP / 'owner-post-decision-change-tickets' / 'ready' / 'post-decision-change-ticket.json'


def build_active_ticket(decision: Path, source_packet: Path) -> Path:
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
    build_change_ticket(
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
        operator_confirmation=TICKET_CONFIRMATION,
        activation_receipt=TMP / 'owner-activation-receipts' / 'valid' / 'activation-receipt.json',
        output_dir=TMP / 'owner-post-decision-change-tickets' / 'active',
    )
    return TMP / 'owner-post-decision-change-tickets' / 'active' / 'post-decision-change-ticket.json'


if TMP.exists():
    shutil.rmtree(TMP)
for stale_packet_root in (ROOT / 'scratch' / 'field' / 'ft0181').glob(f'activation-source-validation-{TMP.name.removeprefix("check-")}*-source-packets'):
    shutil.rmtree(stale_packet_root, ignore_errors=True)
TMP.mkdir(parents=True, exist_ok=True)
errors: list[str] = []
source_packet = TMP / 'activation-source-packets' / 'real-owner-packet.csv'
source_packet.parent.mkdir(parents=True, exist_ok=True)
source_packet.write_text('field_key,owner_attested_class,decision_effect\nallowed_count,aggregate_owner_attested,changes_one_bounded_slice\n', encoding='utf-8')
decision = build_valid_decision(source_packet)
ready_ticket = build_ready_ticket(decision)

summary = build_activation_live_window_brief(
    ticket=ready_ticket,
    output_dir=TMP / 'owner-activation-live-window-briefs' / 'ready',
)
if summary.get('outcome') != 'ACTIVATION-LIVE-WINDOW-BRIEF-PREPARED':
    fail(errors, f'valid ready ticket should prepare activation entry brief: {summary}')
ready_brief_path = TMP / 'owner-activation-live-window-briefs' / 'ready' / 'activation-live-window-brief.json'
ready_brief = load_json(ready_brief_path)
err = owner_activation_live_window_brief_integrity_error(ready_brief, archive_root=ROOT)
if err:
    fail(errors, f'valid ready activation/live-window brief should pass guard: {err}')
if ready_brief.get('brief_state') != 'ACTIVATION_ENTRY_BRIEF_PREPARED_NOT_ACCEPTED':
    fail(errors, 'ready ticket brief must remain a pre-activation NOT_ACCEPTED entry brief')
if not ready_brief.get('activation_receipt_command_template', '').startswith('make owner-activation-receipt '):
    fail(errors, 'ready ticket brief must expose only the activation receipt handoff')
if ready_brief.get('live_window_card_command_templates'):
    fail(errors, 'ready ticket brief must not expose live-window card commands')
if 'make owner-live-window-card' in ready_brief_path.read_text(encoding='utf-8'):
    fail(errors, 'ready ticket brief JSON must not contain live-window card command text')

active_ticket = build_active_ticket(decision, source_packet)
summary = build_activation_live_window_brief(
    ticket=active_ticket,
    output_dir=TMP / 'owner-activation-live-window-briefs' / 'active',
)
if summary.get('outcome') != 'ACTIVATION-LIVE-WINDOW-BRIEF-PREPARED':
    fail(errors, f'valid active ticket should prepare live-window entry brief: {summary}')
active_brief_path = TMP / 'owner-activation-live-window-briefs' / 'active' / 'activation-live-window-brief.json'
active_brief = load_json(active_brief_path)
err = owner_activation_live_window_brief_integrity_error(active_brief, archive_root=ROOT)
if err:
    fail(errors, f'valid active activation/live-window brief should pass guard: {err}')
if active_brief.get('brief_state') != 'LIVE_WINDOW_ENTRY_BRIEF_PREPARED_NOT_RECORDED':
    fail(errors, 'active ticket brief must remain pre-live-window-card')
if active_brief.get('activation_receipt_command_template') is not None:
    fail(errors, 'active ticket brief must not request a duplicate activation receipt')
commands = active_brief.get('live_window_card_command_templates', {})
expected = {'staged_small_window', 'active_small_window', 'paused_stop_state', 'quarantine_without_expansion'}
if set(commands) != expected:
    fail(errors, f'active ticket brief commands missing expected routes: {sorted(commands)}')
for name, command in commands.items():
    if not command.startswith('make owner-live-window-card '):
        fail(errors, f'{name} command must be an owner-live-window-card command')
    for token in [rel(active_ticket), 'CONFIRM=human-recorded-bounded-live-window-card', 'NO_EXPANSION_CONFIRMED=1', 'HUMAN_PAUSE_CONFIRMED=1', 'FALLBACK_ROUTE_CONFIRMED=1']:
        if token not in command:
            fail(errors, f'{name} command missing required token {token}: {command}')

text = ready_brief_path.read_text(encoding='utf-8') + active_brief_path.read_text(encoding='utf-8')
for forbidden in ['eligible 120', 'course operations lead via', 'Human fallback is normal staff outreach', 'raw LMS telemetry is attached', '@example']:
    if forbidden in text:
        fail(errors, f'activation/live-window brief leaked owner answer/contact content: {forbidden}')

# Block unsupported ticket states.
blocked_ticket = TMP / 'owner-post-decision-change-tickets' / 'blocked' / 'post-decision-change-ticket.json'
blocked_ticket.parent.mkdir(parents=True, exist_ok=True)
blocked_data = load_json(ready_ticket)
blocked_data['ticket_state'] = 'blocked_no_real_packet'
blocked_ticket.write_text(json.dumps(blocked_data, indent=2) + '\n', encoding='utf-8')
try:
    build_activation_live_window_brief(ticket=blocked_ticket, output_dir=TMP / 'owner-activation-live-window-briefs' / 'blocked')
    fail(errors, 'blocked_no_real_packet ticket should not prepare activation/live-window brief')
except ValueError as exc:
    payload = json.loads(str(exc))
    if payload.get('outcome') not in {'ACTIVATION-LIVE-WINDOW-BRIEF-TICKET-BLOCKED', 'ACTIVATION-LIVE-WINDOW-BRIEF-STATE-BLOCKED'}:
        fail(errors, f'unsupported ticket state block missing code: {payload}')

try:
    build_activation_live_window_brief(ticket=ready_ticket, output_dir=ROOT / 'docs' / 'bad-activation-live-window-brief')
    fail(errors, 'activation/live-window brief output to docs should be blocked')
except ValueError as exc:
    payload = json.loads(str(exc))
    if payload.get('outcome') != 'ACTIVATION-LIVE-WINDOW-BRIEF-OUTPUT-BLOCKED':
        fail(errors, f'controlled output block missing code: {payload}')
if (ROOT / 'docs' / 'bad-activation-live-window-brief').exists():
    fail(errors, 'blocked activation/live-window brief output must not create docs directory')

if errors:
    shutil.rmtree(TMP)
    raise SystemExit('check_ft0181_activation_live_window_brief: FAIL\n- ' + '\n- '.join(errors))
shutil.rmtree(TMP)
for stale_packet_root in (ROOT / 'scratch' / 'field' / 'ft0181').glob(f'activation-source-validation-{TMP.name.removeprefix("check-")}*-source-packets'):
    shutil.rmtree(stale_packet_root, ignore_errors=True)
print('check_ft0181_activation_live_window_brief: OK (ready/active entry brief, command minimization, source-ticket validation, leakage blocks, output boundary)')
