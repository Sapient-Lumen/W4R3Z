#!/usr/bin/env python3
"""Validate the FT-0181 live-window terminal-state brief bridge."""
from __future__ import annotations

import csv
import json
import shutil
import tempfile
from pathlib import Path

from ft0181_validation_fixtures import build_valid_sent_contact_status
from run_ft0181_returned_reply_work import build_returned_reply_work
from record_ft0181_workbench_review import OPERATOR_CONFIRMATION as REVIEW_CONFIRMATION, build_review
from record_ft0181_first_packet_decision import OPERATOR_CONFIRMATION as DECISION_CONFIRMATION, build_decision
from record_ft0181_activation_receipt import OPERATOR_CONFIRMATION as ACTIVATION_CONFIRMATION, build_activation_receipt
from record_ft0181_post_decision_change_ticket import OPERATOR_CONFIRMATION as TICKET_CONFIRMATION, build_change_ticket
from record_ft0181_live_window_card import OPERATOR_CONFIRMATION as LIVE_WINDOW_CONFIRMATION, build_live_window_card
from prepare_ft0181_live_window_terminal_brief import build_terminal_brief
from ft0181_field_guards import owner_live_window_terminal_brief_integrity_error

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / 'scratch' / 'field' / 'ft0181' / 'validation' / 'ft0181-live-window-terminal-brief'


def fail(msg: str) -> None:
    raise SystemExit(f'check_ft0181_live_window_terminal_brief: FAIL: {msg}')


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def write_contact_status(path: Path) -> Path:
    try:
        return build_valid_sent_contact_status(
            path,
            root=ROOT,
            sent_date='2026-06-16',
            response_due_date='2026-06-23',
            status_date='2026-06-16',
            source_slug='ft0181-live-window-terminal-brief-source-send-log',
        )
    except RuntimeError as exc:
        raise SystemExit(str(exc))


def write_owner_csv(path: Path) -> Path:
    rows = [
        ['1', 'Selected service / owner path / source / date range', 'AIEDU-SR-003 draft reminder pilot; accountable owner route; owner-maintained local service record set; 2026 spring pilot.', 'no raw/protected data', ''],
        ['2', 'Aggregate workflow counts', '12 aggregate draft reminder candidates, 9 human reviewed, 0 automatic sends; no learner-level rows included.', 'aggregate only', ''],
        ['3', 'Action boundary', 'Draft queue note only; no automatic send; no durable write; no penalty and no grade effect; no protected status inference.', 'authority bounded', ''],
        ['4', 'Fallback / rollback / stop condition', 'Local owner can stop the workflow and roll back draft queue rules; human fallback exists.', 'local rollback owner', ''],
        ['5', 'Workload signal', 'Staff review burden observed as aggregate routing time only; no claim of workload reduction.', 'aggregate signal only', ''],
        ['6', 'Training or use guidance', 'Training guidance tells staff to review drafts manually and keep protected facts local.', 'guidance only', ''],
        ['7', 'Public claim ceiling', 'No claim of learning, safety, access, workload, compliance, scale, or effectiveness is supported.', 'claim ceiling', ''],
        ['8', 'Redaction and owner attestation', 'Owner attests this is real operational material with raw, protected, small-cell, and security material withheld and kept local.', 'redacted owner attestation', ''],
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as fh:
        writer = csv.writer(fh)
        writer.writerow(['row_id', 'required_owner_reply', 'owner_response', 'local_only_check', 'intake_note'])
        writer.writerows(rows)
    return path


if TMP.exists():
    shutil.rmtree(TMP)
TMP.mkdir(parents=True, exist_ok=True)
EXTERNAL_CSV_DIR = Path(tempfile.mkdtemp(prefix='ft0181-owner-reply-check-'))

contact = write_contact_status(TMP / 'owner-contact-status' / 'sent' / 'contact-status.json')
owner_csv = write_owner_csv(EXTERNAL_CSV_DIR / 'owner-reply.csv')
reply = build_returned_reply_work(
    csv_path=owner_csv,
    source_contact_status=contact,
    output_dir=TMP / 'sessions' / 'returned-reply-work',
    intake_dir=TMP / 'owner-reply-intakes' / 'proceed',
    seed_dir=TMP / 'owner-reply-workbench-seeds' / 'proceed',
    review_brief_dir=TMP / 'owner-workbench-review-briefs' / 'proceed',
    overwrite=True,
)
if not reply.get('ok'):
    fail(f'returned-reply work failed: {reply}')
seed_path = ROOT / reply['seed_result']['seed_path']
review = build_review(
    seed=seed_path,
    decision='proceed-decision-board',
    source_truth_class='SRC2-CANDIDATE-NOT-ACCEPTED',
    review_basis='owner-attested-aggregate',
    surviving_field_count=8,
    decision_changed_count=5,
    local_only_field_count=0,
    trimmed_field_count=0,
    reask_field_count=0,
    reviewer_role_count=2,
    raw_learner_data_present=False,
    protected_facts_present=False,
    security_payloads_present=False,
    public_claim_upgrade_requested=False,
    operator_confirmation=REVIEW_CONFIRMATION,
    output_dir=TMP / 'owner-workbench-reviews' / 'reviewed',
    overwrite=True,
)
review_path = ROOT / review['review_path']
decision = build_decision(
    review=review_path,
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
    output_dir=TMP / 'owner-first-packet-decisions' / 'decided',
    overwrite=True,
)
decision_path = ROOT / decision['decision_path']
receipt = build_activation_receipt(
    decision=decision_path,
    source_packet=owner_csv,
    source_truth_class='SRC2',
    accepted_field_count=1,
    reviewer_role_count=2,
    dictionary_or_map_ref_count=1,
    blocked_or_trimmed_field_count=1,
    operator_confirmation=ACTIVATION_CONFIRMATION,
    output_dir=TMP / 'owner-activation-receipts' / 'accepted',
    overwrite=True,
)
active_ticket = build_change_ticket(
    decision=decision_path,
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
    activation_receipt=ROOT / receipt['receipt_path'],
    output_dir=TMP / 'owner-post-decision-change-tickets' / 'active',
    overwrite=True,
)
card = build_live_window_card(
    ticket=ROOT / active_ticket['ticket_path'],
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
    operator_confirmation=LIVE_WINDOW_CONFIRMATION,
    output_dir=TMP / 'owner-live-window-cards' / 'staged',
    overwrite=True,
)
card_path = ROOT / card['card_path']
brief = build_terminal_brief(card=card_path, output_dir=TMP / 'owner-live-window-terminal-briefs' / 'staged', overwrite=True)
brief_path = ROOT / brief['brief_path']
if not brief_path.exists():
    fail('terminal brief file missing')
if brief.get('brief_state') != 'TERMINAL_STATE_BRIEF_PREPARED_NOT_RECORDED':
    fail(f'terminal brief state mismatch: {brief.get("brief_state")}')
if brief.get('terminal_card_effect') != 'does_not_record_live_window_card' or brief.get('readout_effect') != 'does_not_record_readout':
    fail('terminal brief must not record a card or readout')
if brief.get('evidence_state') != 'not_evidence' or brief.get('closure_effect') != 'does_not_close_ft0181':
    fail('terminal brief must preserve no-evidence/no-closure effects')
error = owner_live_window_terminal_brief_integrity_error(json.loads(brief_path.read_text(encoding='utf-8')), archive_root=ROOT)
if error:
    fail('generated terminal brief failed integrity: ' + error)
commands = brief.get('terminal_card_command_templates') or {}
for key, state in {
    'paused_stop_state': 'paused',
    'rolled_back_stop_state': 'rolled-back',
    'completed_no_closure': 'completed-no-closure',
    'quarantined_stop_state': 'quarantined',
}.items():
    command = commands.get(key, '')
    if f'WINDOW_STATE={state}' not in command or 'CONFIRM=human-recorded-bounded-live-window-card' not in command:
        fail(f'terminal command {key} missing state or confirmation token: {command}')
    if 'OUT=scratch/field/ft0181/owner-live-window-cards/' not in command:
        fail(f'terminal command {key} should write to a non-conflicting scratch output: {command}')
for forbidden in ['Draft queue note only', 'Owner attests this is real operational material', 'student id', 'email address', '@']:
    if forbidden in brief_path.read_text(encoding='utf-8'):
        fail('terminal brief must not copy owner/raw/contact terms: ' + forbidden)

# Completed terminal cards should not be eligible for another terminal brief.
completed = build_live_window_card(
    ticket=ROOT / active_ticket['ticket_path'],
    window_state='completed-no-closure',
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
    operator_confirmation=LIVE_WINDOW_CONFIRMATION,
    output_dir=TMP / 'owner-live-window-cards' / 'completed',
    overwrite=True,
)
try:
    build_terminal_brief(card=ROOT / completed['card_path'], output_dir=TMP / 'owner-live-window-terminal-briefs' / 'completed', overwrite=True)
except ValueError as exc:
    if 'staged or active' not in str(exc):
        fail('terminal brief should reject terminal cards with staged/active message')
else:
    fail('terminal brief should reject already-terminal cards')

print('check_ft0181_live_window_terminal_brief: OK')
