#!/usr/bin/env python3
"""Validate FT-0181 post-decision change-ticket brief bridge."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from ft0181_validation_fixtures import build_valid_sent_contact_status
from prepare_ft0181_post_decision_change_ticket_brief import build_change_ticket_brief
from record_ft0181_first_packet_decision import OPERATOR_CONFIRMATION as DECISION_CONFIRMATION, build_decision
from record_ft0181_workbench_review import OPERATOR_CONFIRMATION as REVIEW_CONFIRMATION, build_review
from ft0181_field_guards import owner_post_decision_change_ticket_brief_integrity_error

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / 'scratch' / 'field' / 'ft0181' / 'validation' / 'ft0181-post-decision-change-ticket-brief'


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def write_source_contact_status(path: Path) -> Path:
    try:
        return build_valid_sent_contact_status(
            path,
            root=ROOT,
            sent_date='2026-06-13',
            response_due_date='2026-06-20',
            status_date='2026-06-13',
            source_slug='ft0181-post-decision-change-ticket-brief-source-send-log',
        )
    except RuntimeError as exc:
        raise SystemExit(str(exc))


def write_seed(path: Path, source_contact_status: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        'seed_type': 'FT-0181-owner-packet-workbench-seed',
        'seed_version': 'rev0297',
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


if TMP.exists():
    shutil.rmtree(TMP)
TMP.mkdir(parents=True, exist_ok=True)
errors: list[str] = []

source_contact = write_source_contact_status(TMP / 'owner-contact-status' / 'sent' / 'contact-status.json')
seed = write_seed(TMP / 'owner-reply-workbench-seeds' / 'aiedu-sr-003' / 'workbench-seed.json', source_contact)
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
review = TMP / 'owner-workbench-reviews' / 'proceed' / 'workbench-review.json'
build_decision(
    review=review,
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
decision = TMP / 'owner-first-packet-decisions' / 'valid' / 'first-packet-decision.json'
summary = build_change_ticket_brief(
    decision=decision,
    output_dir=TMP / 'owner-post-decision-change-ticket-briefs' / 'prepared',
)
if summary.get('outcome') != 'POST-DECISION-CHANGE-TICKET-BRIEF-PREPARED':
    fail(errors, f'valid post-decision change-ticket brief should prepare: {summary}')
brief_path = TMP / 'owner-post-decision-change-ticket-briefs' / 'prepared' / 'change-ticket-brief.json'
brief = load_json(brief_path)
err = owner_post_decision_change_ticket_brief_integrity_error(brief, archive_root=ROOT)
if err:
    fail(errors, f'valid post-decision change-ticket brief should pass guard: {err}')
if brief.get('ticket_effect') != 'does_not_record_change_ticket' or brief.get('acceptance_state') != 'NOT_ACCEPTED':
    fail(errors, 'change-ticket brief must remain non-ticket and NOT_ACCEPTED')
if brief.get('required_next_surface') != 'docs/30-operations/ft0181-post-decision-change-ticket.md':
    fail(errors, 'change-ticket brief must route only to post-decision change-ticket surface')
commands = brief.get('bounded_change_ticket_command_templates', {})
expected = ['ready_for_real_packet_sandbox', 'ready_for_real_packet_trim', 'blocked_no_real_packet', 'quarantine', 'active_change_after_activation_receipt_only']
if sorted(commands) != sorted(expected):
    fail(errors, f'change-ticket brief commands missing expected routes: {sorted(commands)}')
for name, command in commands.items():
    if not command.startswith('make owner-post-decision-change-ticket '):
        fail(errors, f'{name} must be an owner-post-decision-change-ticket command')
    if rel(decision) not in command or 'CONFIRM=human-recorded-bounded-post-decision-change-ticket' not in command:
        fail(errors, f'{name} command missing decision path or confirmation token: {command}')
    if name != 'active_change_after_activation_receipt_only' and 'ACTIVATION_RECEIPT=' in command:
        fail(errors, f'{name} command must not jump to activation receipt: {command}')
    if name == 'active_change_after_activation_receipt_only' and '<scratch/.../activation-receipt.json>' not in command:
        fail(errors, f'{name} command must require a placeholder activation receipt: {command}')
text = brief_path.read_text(encoding='utf-8') + (TMP / 'owner-post-decision-change-ticket-briefs' / 'prepared' / 'POST-DECISION-CHANGE-TICKET-BRIEF.md').read_text(encoding='utf-8')
for forbidden in ['eligible 120', 'course operations lead via', 'Human fallback is normal staff outreach', 'raw LMS telemetry is attached', '@example']:
    if forbidden in text:
        fail(errors, f'change-ticket brief leaked owner answer/contact content: {forbidden}')

# Tampered decisions cannot source ticket briefs.
tampered_decision = TMP / 'owner-first-packet-decisions' / 'tampered' / 'first-packet-decision.json'
tampered_decision.parent.mkdir(parents=True, exist_ok=True)
tampered_data = load_json(decision)
tampered_data['acceptance_state'] = 'ACCEPTED'
tampered_decision.write_text(json.dumps(tampered_data, indent=2) + '\n', encoding='utf-8')
try:
    build_change_ticket_brief(decision=tampered_decision, output_dir=TMP / 'owner-post-decision-change-ticket-briefs' / 'tampered')
    fail(errors, 'tampered accepted first-packet decision should not source a change-ticket brief')
except ValueError as exc:
    payload = json.loads(str(exc))
    if payload.get('outcome') != 'POST-DECISION-CHANGE-TICKET-BRIEF-DECISION-BLOCKED':
        fail(errors, f'tampered decision block missing code: {payload}')

try:
    build_change_ticket_brief(decision=decision, output_dir=ROOT / 'docs' / 'bad-post-decision-change-ticket-brief')
    fail(errors, 'post-decision change-ticket brief output to docs should be blocked')
except ValueError as exc:
    payload = json.loads(str(exc))
    if payload.get('outcome') != 'POST-DECISION-CHANGE-TICKET-BRIEF-OUTPUT-BLOCKED':
        fail(errors, f'controlled output block missing code: {payload}')
if (ROOT / 'docs' / 'bad-post-decision-change-ticket-brief').exists():
    fail(errors, 'blocked change-ticket brief output must not create docs directory')

if errors:
    shutil.rmtree(TMP)
    raise SystemExit('check_ft0181_post_decision_change_ticket_brief: FAIL\n- ' + '\n- '.join(errors))
shutil.rmtree(TMP)
print('check_ft0181_post_decision_change_ticket_brief: OK (change-ticket brief bridge, source-decision validation, activation-boundary command skeletons, blocks, output boundary)')
