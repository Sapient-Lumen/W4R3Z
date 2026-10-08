#!/usr/bin/env python3
"""Validate FT-0181 first-packet decision-board local gate."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from ft0181_validation_fixtures import build_valid_sent_contact_status
from record_ft0181_workbench_review import OPERATOR_CONFIRMATION as REVIEW_CONFIRMATION, build_review
from record_ft0181_first_packet_decision import OPERATOR_CONFIRMATION, build_decision
from ft0181_field_guards import owner_first_packet_decision_integrity_error

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / 'scratch' / 'field' / 'ft0181' / 'validation' / 'ft0181-first-packet-decision'


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
            source_slug='ft0181-first-packet-decision-source-send-log',
        )
    except RuntimeError as exc:
        raise SystemExit(str(exc))


def write_seed(path: Path, source_contact_status: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        'seed_type': 'FT-0181-owner-packet-workbench-seed',
        'seed_version': 'rev0276',
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
review = TMP / 'owner-workbench-reviews' / 'proceed' / 'workbench-review.json'

summary = build_decision(
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
    operator_confirmation=OPERATOR_CONFIRMATION,
    output_dir=TMP / 'owner-first-packet-decisions' / 'valid',
)
if summary.get('outcome') != 'FIRST-PACKET-DECISION-RECORDED':
    fail(errors, f'valid first-packet decision should record: {summary}')
decision_path = TMP / 'owner-first-packet-decisions' / 'valid' / 'first-packet-decision.json'
decision = load_json(decision_path)
err = owner_first_packet_decision_integrity_error(decision, archive_root=ROOT)
if err:
    fail(errors, f'valid first-packet decision should pass guard: {err}')
if decision.get('acceptance_state') != 'NOT_ACCEPTED' or decision.get('evidence_state') != 'not_evidence':
    fail(errors, 'first-packet decision must remain NOT_ACCEPTED and not_evidence')
if decision.get('required_next_surface') != 'docs/30-operations/ft0181-post-decision-change-ticket.md':
    fail(errors, 'first-packet decision must route only to post-decision change ticket')
text = decision_path.read_text(encoding='utf-8') + (TMP / 'owner-first-packet-decisions' / 'valid' / 'FIRST-PACKET-DECISION-SUMMARY.md').read_text(encoding='utf-8')
for forbidden in ['eligible 120', 'course operations lead via', 'Human fallback is normal staff outreach', 'raw LMS telemetry is attached', '@example']:
    if forbidden in text:
        fail(errors, f'first-packet decision leaked owner answer/contact content: {forbidden}')

blocked_cases = [
    ({'changed_slice_count': 4}, 'changed count mismatch'),
    ({'authority_action': 'no-change', 'evidence_action': 'no-change', 'construct_action': 'no-change', 'public_action': 'no-change', 'lifecycle_action': 'no-change', 'changed_slice_count': 0}, 'all no change'),
    ({'rollback_owner_role_count': 0}, 'missing rollback owner'),
    ({'raw_learner_data_present': True}, 'raw learner'),
    ({'protected_facts_present': True}, 'protected'),
    ({'security_payloads_present': True}, 'security'),
    ({'public_claim_upgrade_requested': True}, 'public claim upgrade'),
]
base = dict(
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
    operator_confirmation=OPERATOR_CONFIRMATION,
)
for overrides, label in blocked_cases:
    args = dict(base)
    args.update(overrides)
    args['output_dir'] = TMP / 'owner-first-packet-decisions' / f'blocked-{label.replace(" ", "-")}'
    try:
        build_decision(**args)
        fail(errors, f'first-packet decision with {label} problem should block')
    except ValueError as exc:
        payload = json.loads(str(exc))
        if payload.get('ok') is not False or 'FIRST-PACKET-DECISION' not in payload.get('outcome', ''):
            fail(errors, f'{label} block should be machine-readable: {payload}')

# Non-proceed reviews cannot source the decision board.
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
    build_decision(**{**base, 'review': TMP / 'owner-workbench-reviews' / 'reask' / 'workbench-review.json', 'output_dir': TMP / 'owner-first-packet-decisions' / 'from-reask'})
    fail(errors, 'non-proceed workbench review should not source first-packet decision board')
except ValueError as exc:
    payload = json.loads(str(exc))
    if payload.get('outcome') != 'FIRST-PACKET-DECISION-REVIEW-BLOCKED':
        fail(errors, f'non-proceed review block missing code: {payload}')

# Tampered review/source boundaries and output destinations are blocked.
tampered_review = TMP / 'owner-workbench-reviews' / 'tampered' / 'workbench-review.json'
tampered_review.parent.mkdir(parents=True, exist_ok=True)
tampered_data = load_json(review)
tampered_data['acceptance_state'] = 'ACCEPTED'
tampered_review.write_text(json.dumps(tampered_data, indent=2) + '\n', encoding='utf-8')
try:
    build_decision(**{**base, 'review': tampered_review, 'output_dir': TMP / 'owner-first-packet-decisions' / 'tampered-review'})
    fail(errors, 'tampered accepted review should not source first-packet decision')
except ValueError as exc:
    payload = json.loads(str(exc))
    if payload.get('outcome') != 'FIRST-PACKET-DECISION-REVIEW-BLOCKED':
        fail(errors, f'tampered review block missing code: {payload}')

try:
    build_decision(**{**base, 'output_dir': ROOT / 'docs' / 'bad-first-packet-decision'})
    fail(errors, 'first-packet decision output to docs should be blocked')
except ValueError as exc:
    payload = json.loads(str(exc))
    if payload.get('outcome') != 'FIRST-PACKET-DECISION-OUTPUT-BLOCKED':
        fail(errors, f'controlled output block missing code: {payload}')

if errors:
    shutil.rmtree(TMP)
    raise SystemExit('check_ft0181_first_packet_decision: FAIL\n- ' + '\n- '.join(errors))
shutil.rmtree(TMP)
print('check_ft0181_first_packet_decision: OK (five-slice decision-board gate, source-review validation, minimization, blocks, output boundary)')
