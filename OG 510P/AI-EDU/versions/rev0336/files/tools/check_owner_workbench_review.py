#!/usr/bin/env python3
"""Validate FT-0181 owner workbench-review local gate."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from ft0181_validation_fixtures import build_valid_sent_contact_status
from record_ft0181_workbench_review import OPERATOR_CONFIRMATION, build_review
from record_ft0181_owner_contact_status import (
    OPERATOR_CONFIRMATIONS,
    build_status,
    verify_source_artifact,
)
from record_ft0181_owner_reask_log import OPERATOR_CONFIRMATION as REASK_LOG_CONFIRMATION, build_reask_log
from ft0181_field_guards import owner_workbench_review_integrity_error

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / 'scratch' / 'field' / 'ft0181' / 'validation' / 'owner-workbench-review'


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
            source_slug='owner-workbench-review-source-send-log',
        )
    except RuntimeError as exc:
        raise SystemExit(str(exc))


def write_seed(path: Path, source_contact_status: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        'seed_type': 'FT-0181-owner-packet-workbench-seed',
        'seed_version': 'rev0275',
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
source_contact = write_source_contact_status(TMP / 'owner-contact-status' / 'sent' / 'contact-status.json')
seed = write_seed(TMP / 'owner-reply-workbench-seeds' / 'aiedu-sr-003' / 'workbench-seed.json', source_contact)
errors: list[str] = []

# A proceed-capable review remains NOT_ACCEPTED and copies no owner answer text.
summary = build_review(
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
    operator_confirmation=OPERATOR_CONFIRMATION,
    output_dir=TMP / 'owner-workbench-reviews' / 'proceed',
)
if summary.get('outcome') != 'WORKBENCH-REVIEW-RECORDED':
    fail(errors, f'valid workbench review should be recorded: {summary}')
review_path = TMP / 'owner-workbench-reviews' / 'proceed' / 'workbench-review.json'
review = load_json(review_path)
err = owner_workbench_review_integrity_error(review, archive_root=ROOT)
if err:
    fail(errors, f'valid review should pass shared integrity guard: {err}')
if review.get('acceptance_state') != 'NOT_ACCEPTED' or review.get('evidence_state') != 'not_evidence':
    fail(errors, 'review must remain NOT_ACCEPTED and not_evidence')
if review.get('required_next_surface') != 'docs/30-operations/ft0181-first-packet-decision-board.md':
    fail(errors, 'proceed review must route only to first-packet decision board')
text = review_path.read_text(encoding='utf-8') + (TMP / 'owner-workbench-reviews' / 'proceed' / 'WORKBENCH-REVIEW-SUMMARY.md').read_text(encoding='utf-8')
for forbidden in ['eligible 120', 'course operations lead via', 'Human fallback is normal staff outreach', 'raw LMS telemetry is attached', '@example']:
    if forbidden in text:
        fail(errors, f'workbench review leaked owner answer/contact content: {forbidden}')

# Proceed cannot be recorded from weak source class, a single reviewer, pending reask, or raw/protected/security flags.
blocked_cases = [
    ({'source_truth_class': 'UNVERIFIED-OWNER-REPLY'}, 'source truth'),
    ({'reviewer_role_count': 1}, 'reviewer role'),
    ({'reask_field_count': 1}, 'pending reask'),
    ({'raw_learner_data_present': True}, 'raw learner'),
    ({'protected_facts_present': True}, 'protected'),
    ({'security_payloads_present': True}, 'security'),
    ({'public_claim_upgrade_requested': True}, 'public claim'),
]
base = dict(
    seed=seed,
    decision='proceed-decision-board',
    source_truth_class='SRC2',
    review_basis='owner-attested-aggregate',
    surviving_field_count=2,
    decision_changed_count=1,
    local_only_field_count=0,
    trimmed_field_count=0,
    reask_field_count=0,
    reviewer_role_count=2,
    raw_learner_data_present=False,
    protected_facts_present=False,
    security_payloads_present=False,
    public_claim_upgrade_requested=False,
    operator_confirmation=OPERATOR_CONFIRMATION,
)
for overrides, label in blocked_cases:
    args = dict(base)
    args.update(overrides)
    args['output_dir'] = TMP / 'owner-workbench-reviews' / f'blocked-{label.replace(" ", "-")}'
    try:
        build_review(**args)
        fail(errors, f'proceed review with {label} problem should block')
    except ValueError as exc:
        payload = json.loads(str(exc))
        if payload.get('ok') is not False or 'WORKBENCH-REVIEW' not in payload.get('outcome', ''):
            fail(errors, f'{label} block should be machine-readable: {payload}')

# A reask review can source exactly one clarification reask-log before any contact clock.
reask_summary = build_review(
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
    operator_confirmation=OPERATOR_CONFIRMATION,
    output_dir=TMP / 'owner-workbench-reviews' / 'reask',
)
if reask_summary.get('decision') != 'REASK-OWNER':
    fail(errors, f'reask workbench review should record REASK-OWNER: {reask_summary}')
reask_log = build_reask_log(
    output_dir=TMP / 'owner-reask-logs' / 'from-review',
    source_artifact=TMP / 'owner-workbench-reviews' / 'reask' / 'workbench-review.json',
    sent_date='2026-06-21',
    response_due_date='2026-06-24',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    reask_channel_class='email',
    owner_route_class='same-accountable-owner-route',
    operator_confirmation=REASK_LOG_CONFIRMATION,
)
if not reask_log.get('ok'):
    fail(errors, f'REASK-OWNER workbench review should source a reask log: {reask_log}')
reask_log_path = TMP / 'owner-reask-logs' / 'from-review' / 'reask-log.json'
ok, reason, source_type = verify_source_artifact(
    status='reask-awaiting-reply',
    source_artifact=rel(reask_log_path),
    sent_date='2026-06-21',
    response_due_date='2026-06-24',
    status_date='2026-06-21',
    attempt_count=2,
)
if not ok or source_type != 'reask-log':
    fail(errors, f'reask-log should source reask contact clock: {reason} ({source_type})')
status = build_status(
    output_dir=TMP / 'owner-contact-status' / 'reask-from-review',
    status='reask-awaiting-reply',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    sent_date='2026-06-21',
    response_due_date='2026-06-24',
    status_date='2026-06-21',
    attempt_count=2,
    operator_confirmation=OPERATOR_CONFIRMATIONS['reask-awaiting-reply'],
    source_artifact=rel(reask_log_path),
)
if not status.get('ok'):
    fail(errors, f'reask status from review reask-log should build: {status}')

# Tampered seed/source boundaries and output destinations are blocked.
tampered_seed = TMP / 'owner-reply-workbench-seeds' / 'tampered' / 'workbench-seed.json'
write_seed(tampered_seed, source_contact)
tampered_data = load_json(tampered_seed)
tampered_data['acceptance_state'] = 'ACCEPTED'
tampered_seed.write_text(json.dumps(tampered_data, indent=2) + '\n', encoding='utf-8')
try:
    build_review(**{**base, 'seed': tampered_seed, 'output_dir': TMP / 'owner-workbench-reviews' / 'tampered-seed'})
    fail(errors, 'tampered accepted seed should not source workbench review')
except ValueError as exc:
    payload = json.loads(str(exc))
    if payload.get('outcome') != 'WORKBENCH-REVIEW-SEED-BLOCKED':
        fail(errors, f'tampered seed block missing code: {payload}')

try:
    build_review(**{**base, 'output_dir': ROOT / 'docs' / 'bad-workbench-review'})
    fail(errors, 'workbench review output to docs should be blocked')
except ValueError as exc:
    payload = json.loads(str(exc))
    if payload.get('outcome') != 'WORKBENCH-REVIEW-OUTPUT-BLOCKED':
        fail(errors, f'docs output block missing code: {payload}')
if (ROOT / 'docs' / 'bad-workbench-review').exists():
    fail(errors, 'blocked workbench review output must not create docs directory')

if errors:
    raise SystemExit('owner workbench review validation errors:\n' + '\n'.join(errors))
shutil.rmtree(TMP)
print('check_owner_workbench_review: OK (source-seed gate, proceed/reask route, no owner-answer/contact leakage, reask-log/contact-clock source, tampered seed block, output guard, NOT_ACCEPTED boundary)')
