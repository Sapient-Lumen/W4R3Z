#!/usr/bin/env python3
"""Validate FT-0181 first-packet decision brief bridge."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from ft0181_validation_fixtures import build_valid_sent_contact_status
from prepare_ft0181_first_packet_decision_brief import build_decision_brief
from record_ft0181_workbench_review import OPERATOR_CONFIRMATION as REVIEW_CONFIRMATION, build_review
from ft0181_field_guards import owner_first_packet_decision_brief_integrity_error

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / 'scratch' / 'field' / 'ft0181' / 'validation' / 'ft0181-first-packet-decision-brief'


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
            source_slug='ft0181-first-packet-decision-brief-source-send-log',
        )
    except RuntimeError as exc:
        raise SystemExit(str(exc))


def write_seed(path: Path, source_contact_status: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        'seed_type': 'FT-0181-owner-packet-workbench-seed',
        'seed_version': 'rev0296',
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
summary = build_decision_brief(
    review=review,
    output_dir=TMP / 'owner-first-packet-decision-briefs' / 'prepared',
)
if summary.get('outcome') != 'FIRST-PACKET-DECISION-BRIEF-PREPARED':
    fail(errors, f'valid first-packet decision brief should prepare: {summary}')
brief_path = TMP / 'owner-first-packet-decision-briefs' / 'prepared' / 'decision-brief.json'
brief = load_json(brief_path)
err = owner_first_packet_decision_brief_integrity_error(brief, archive_root=ROOT)
if err:
    fail(errors, f'valid first-packet decision brief should pass guard: {err}')
if brief.get('decision_effect') != 'does_not_record_decision' or brief.get('acceptance_state') != 'NOT_ACCEPTED':
    fail(errors, 'decision brief must remain non-decision and NOT_ACCEPTED')
if brief.get('required_next_surface') != 'docs/30-operations/ft0181-first-packet-decision-board.md':
    fail(errors, 'decision brief must route only to first-packet decision-board surface')
commands = brief.get('bounded_decision_command_templates', {})
if sorted(commands) != sorted(['conservative_watch', 'sandbox_adjustment', 'suppress_or_quarantine', 'pilot_with_expiry_candidate', 'no_public_change_watch']):
    fail(errors, f'decision brief commands missing expected routes: {sorted(commands)}')
for name, command in commands.items():
    if not command.startswith('make owner-first-packet-decision '):
        fail(errors, f'{name} must be an owner-first-packet-decision command')
    if rel(review) not in command or 'CONFIRM=human-recorded-five-slice-decision-board' not in command:
        fail(errors, f'{name} command missing review path or confirmation token: {command}')
    if 'SOURCE_PACKET=' in command or 'ACTIVATION_RECEIPT=' in command:
        fail(errors, f'{name} command must not jump to activation/source-packet work: {command}')
text = brief_path.read_text(encoding='utf-8') + (TMP / 'owner-first-packet-decision-briefs' / 'prepared' / 'FIRST-PACKET-DECISION-BRIEF.md').read_text(encoding='utf-8')
for forbidden in ['eligible 120', 'course operations lead via', 'Human fallback is normal staff outreach', 'raw LMS telemetry is attached', '@example']:
    if forbidden in text:
        fail(errors, f'decision brief leaked owner answer/contact content: {forbidden}')

# Non-proceed reviews cannot prepare board briefs.
build_review(
    seed=seed,
    decision='reask-owner',
    source_truth_class='UNVERIFIED-OWNER-REPLY',
    review_basis='needs-clarification',
    surviving_field_count=1,
    decision_changed_count=0,
    local_only_field_count=0,
    trimmed_field_count=0,
    reask_field_count=1,
    reviewer_role_count=1,
    raw_learner_data_present=False,
    protected_facts_present=False,
    security_payloads_present=False,
    public_claim_upgrade_requested=False,
    operator_confirmation=REVIEW_CONFIRMATION,
    output_dir=TMP / 'owner-workbench-reviews' / 'reask',
)
try:
    build_decision_brief(
        review=TMP / 'owner-workbench-reviews' / 'reask' / 'workbench-review.json',
        output_dir=TMP / 'owner-first-packet-decision-briefs' / 'from-reask',
    )
    fail(errors, 'reask workbench review should not source first-packet decision brief')
except ValueError as exc:
    payload = json.loads(str(exc))
    if payload.get('outcome') != 'FIRST-PACKET-DECISION-BRIEF-REVIEW-BLOCKED':
        fail(errors, f'reask review block missing code: {payload}')

# Tampered review/source boundaries and output destinations are blocked.
tampered_review = TMP / 'owner-workbench-reviews' / 'tampered' / 'workbench-review.json'
tampered_review.parent.mkdir(parents=True, exist_ok=True)
tampered_data = load_json(review)
tampered_data['acceptance_state'] = 'ACCEPTED'
tampered_review.write_text(json.dumps(tampered_data, indent=2) + '\n', encoding='utf-8')
try:
    build_decision_brief(review=tampered_review, output_dir=TMP / 'owner-first-packet-decision-briefs' / 'tampered-review')
    fail(errors, 'tampered accepted review should not source decision brief')
except ValueError as exc:
    payload = json.loads(str(exc))
    if payload.get('outcome') != 'FIRST-PACKET-DECISION-BRIEF-REVIEW-BLOCKED':
        fail(errors, f'tampered review block missing code: {payload}')

try:
    build_decision_brief(review=review, output_dir=ROOT / 'docs' / 'bad-first-packet-decision-brief')
    fail(errors, 'first-packet decision brief output to docs should be blocked')
except ValueError as exc:
    payload = json.loads(str(exc))
    if payload.get('outcome') != 'FIRST-PACKET-DECISION-BRIEF-OUTPUT-BLOCKED':
        fail(errors, f'controlled output block missing code: {payload}')
if (ROOT / 'docs' / 'bad-first-packet-decision-brief').exists():
    fail(errors, 'blocked decision brief output must not create docs directory')

if errors:
    shutil.rmtree(TMP)
    raise SystemExit('check_ft0181_first_packet_decision_brief: FAIL\n- ' + '\n- '.join(errors))
shutil.rmtree(TMP)
print('check_ft0181_first_packet_decision_brief: OK (decision brief bridge, source-review validation, command skeleton minimization, blocks, output boundary)')
