#!/usr/bin/env python3
"""Smoke-test the FT-0181 post-readout recheck due-date gate."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from ft0181_validation_fixtures import build_valid_sent_contact_status
from record_ft0181_activation_receipt import OPERATOR_CONFIRMATION as ACTIVATION_CONFIRMATION, build_activation_receipt
from record_ft0181_first_packet_decision import OPERATOR_CONFIRMATION as DECISION_CONFIRMATION, build_decision
from record_ft0181_live_window_card import OPERATOR_CONFIRMATION as CARD_CONFIRMATION, build_live_window_card
from record_ft0181_live_window_readout import OPERATOR_CONFIRMATION as READOUT_CONFIRMATION, build_live_window_readout
from record_ft0181_post_decision_change_ticket import OPERATOR_CONFIRMATION as TICKET_CONFIRMATION, build_change_ticket
from record_ft0181_post_readout_action import OPERATOR_CONFIRMATION as ACTION_CONFIRMATION, build_post_readout_action
from record_ft0181_workbench_review import OPERATOR_CONFIRMATION as REVIEW_CONFIRMATION, build_review
from ft0181_field_guards import owner_post_readout_action_integrity_error

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / 'scratch' / 'field' / 'ft0181' / 'validation' / 'ft0181-post-readout-action'


def fail(errors: list[str], msg: str) -> None:
    errors.append(msg)


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


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
            source_slug='ft0181-post-readout-action-source-send-log',
        )
    except RuntimeError as exc:
        raise SystemExit(str(exc))


def write_seed(path: Path, source_contact_status: Path, source_packet: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        'seed_type': 'FT-0181-owner-packet-workbench-seed',
        'seed_version': 'rev0288',
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


def build_readout(base_dir: Path, *, window_state: str = 'completed-no-closure', disposition: str = 'continue-bounded', field_trim_count: int = 0) -> Path:
    source_packet = base_dir / 'activation-source-packets' / 'real-owner-packet.csv'
    source_packet.parent.mkdir(parents=True, exist_ok=True)
    source_packet.write_text('field_key,owner_attested_class,decision_effect\nallowed_count,aggregate_owner_attested,changes_one_bounded_slice\n', encoding='utf-8')
    source_contact = write_source_contact_status(base_dir / 'owner-contact-status' / 'sent' / 'contact-status.json')
    seed = write_seed(base_dir / 'owner-reply-workbench-seeds' / 'aiedu-sr-003' / 'workbench-seed.json', source_contact, source_packet)
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
        output_dir=base_dir / 'owner-workbench-reviews' / 'proceed',
    )
    build_decision(
        review=base_dir / 'owner-workbench-reviews' / 'proceed' / 'workbench-review.json',
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
        output_dir=base_dir / 'owner-first-packet-decisions' / 'valid',
    )
    build_activation_receipt(
        decision=base_dir / 'owner-first-packet-decisions' / 'valid' / 'first-packet-decision.json',
        source_packet=source_packet,
        source_truth_class='SRC2',
        accepted_field_count=1,
        reviewer_role_count=2,
        dictionary_or_map_ref_count=1,
        blocked_or_trimmed_field_count=1,
        operator_confirmation=ACTIVATION_CONFIRMATION,
        output_dir=base_dir / 'owner-activation-receipts' / 'valid',
    )
    build_change_ticket(
        decision=base_dir / 'owner-first-packet-decisions' / 'valid' / 'first-packet-decision.json',
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
        activation_receipt=base_dir / 'owner-activation-receipts' / 'valid' / 'activation-receipt.json',
        output_dir=base_dir / 'owner-post-decision-change-tickets' / 'valid',
    )
    build_live_window_card(
        ticket=base_dir / 'owner-post-decision-change-tickets' / 'valid' / 'post-decision-change-ticket.json',
        window_state=window_state,
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
        operator_confirmation=CARD_CONFIRMATION,
        output_dir=base_dir / 'owner-live-window-cards' / 'terminal',
    )
    build_live_window_readout(
        card=base_dir / 'owner-live-window-cards' / 'terminal' / 'live-window-card.json',
        window_disposition=disposition,
        source_truth_class='SRC2',
        aggregate_evidence_read_count=3,
        claim_family_effect_count=2,
        decision_delta_count=1 if disposition in {'continue-bounded', 'rerun-narrower'} else 0,
        field_trim_count=field_trim_count,
        reviewer_role_count=2,
        unresolved_disagreement_count=0,
        public_claim_ceiling='example-only-no-outcome-claim',
        no_public_claim_upgrade=True,
        no_service_record_edit=True,
        no_lifecycle_change=True,
        no_closure_from_readout=True,
        raw_learner_data_present=False,
        protected_facts_present=False,
        security_payloads_present=False,
        public_claim_upgrade_requested=False,
        operator_confirmation=READOUT_CONFIRMATION,
        output_dir=base_dir / 'owner-live-window-readouts' / 'valid',
    )
    return base_dir / 'owner-live-window-readouts' / 'valid' / 'live-window-readout.json'


if TMP.exists():
    shutil.rmtree(TMP)
for stale_packet_root in (ROOT / 'scratch' / 'field' / 'ft0181').glob(f'activation-source-validation-{TMP.name.removeprefix("check-")}*-source-packets'):
    shutil.rmtree(stale_packet_root, ignore_errors=True)
TMP.mkdir(parents=True, exist_ok=True)
errors: list[str] = []
readout = build_readout(TMP / 'source-continue')
summary = build_post_readout_action(
    readout=readout,
    dispatch_lane='continue-same-ceiling',
    source_truth_class='SRC2',
    allowed_action_count=1,
    prohibited_action_count=5,
    field_to_reask_count=0,
    field_to_drop_count=0,
    reviewer_role_count=2,
    unresolved_disagreement_count=0,
    due_or_recheck_date='2026-06-25',
    owner_action_class=None,
    next_evidence_ask_class=None,
    public_language_action=None,
    no_expansion_confirmed=True,
    no_public_claim_upgrade=True,
    no_service_record_edit=True,
    no_lifecycle_change=True,
    no_closure_from_dispatch=True,
    raw_learner_data_present=False,
    protected_facts_present=False,
    security_payloads_present=False,
    public_claim_upgrade_requested=False,
    operator_confirmation=ACTION_CONFIRMATION,
    output_dir=TMP / 'owner-post-readout-actions' / 'valid',
)
if summary.get('outcome') != 'POST-READOUT-ACTION-DISPATCH-RECORDED':
    fail(errors, f'valid post-readout action should record: {summary}')
action_path = TMP / 'owner-post-readout-actions' / 'valid' / 'post-readout-action.json'
action = load_json(action_path)
err = owner_post_readout_action_integrity_error(action, archive_root=ROOT)
if err:
    fail(errors, f'valid post-readout action should pass guard: {err}')
if action.get('dispatch_lane') != 'continue_same_ceiling' or action.get('closure_permitted') is not False:
    fail(errors, 'post-readout action should normalize lane and preserve non-closure')
if action.get('service_record_effect') != 'does_not_edit_service_records_without_separate_owner_action':
    fail(errors, 'post-readout action must not edit service records by itself')
for field, bad_value in [
    ('next_evidence_ask_class', 'quarantine-resolution-ask'),
    ('public_language_action', 'suppress-public-language'),
]:
    tampered = json.loads(json.dumps(action))
    tampered[field] = bad_value
    err = owner_post_readout_action_integrity_error(tampered, archive_root=ROOT)
    if not err or field not in err or 'dispatch_lane' not in err:
        fail(errors, f'tampered {field} should fail lane-class guard, got {err}')
text = action_path.read_text(encoding='utf-8') + (TMP / 'owner-post-readout-actions' / 'valid' / 'POST-READOUT-ACTION-SUMMARY.md').read_text(encoding='utf-8')
for forbidden in ['eligible 120', 'course operations lead via', 'raw LMS telemetry is attached', '@example', 'chat transcript']:
    if forbidden in text:
        fail(errors, f'post-readout action leaked raw/contact content: {forbidden}')

blocked_cases = [
    ({'dispatch_lane': 'rerun-narrower'}, 'lane mismatch'),
    ({'source_truth_class': 'SRC3'}, 'source truth mismatch'),
    ({'allowed_action_count': 0}, 'no allowed action'),
    ({'prohibited_action_count': 1}, 'too few prohibitions'),
    ({'reviewer_role_count': 1}, 'single reviewer'),
    ({'no_expansion_confirmed': False}, 'expansion firebreak'),
    ({'no_public_claim_upgrade': False}, 'public claim firebreak'),
    ({'no_service_record_edit': False}, 'service firebreak'),
    ({'no_lifecycle_change': False}, 'lifecycle firebreak'),
    ({'no_closure_from_dispatch': False}, 'closure firebreak'),
    ({'raw_learner_data_present': True}, 'raw learner'),
    ({'protected_facts_present': True}, 'protected'),
    ({'security_payloads_present': True}, 'security'),
    ({'public_claim_upgrade_requested': True}, 'public claim upgrade'),
    ({'next_evidence_ask_class': 'quarantine-resolution-ask'}, 'next ask lane-class mismatch'),
    ({'public_language_action': 'suppress-public-language'}, 'public language lane-class mismatch'),
]
base = dict(
    readout=readout,
    dispatch_lane='continue-same-ceiling',
    source_truth_class='SRC2',
    allowed_action_count=1,
    prohibited_action_count=5,
    field_to_reask_count=0,
    field_to_drop_count=0,
    reviewer_role_count=2,
    unresolved_disagreement_count=0,
    due_or_recheck_date='2026-06-25',
    owner_action_class=None,
    next_evidence_ask_class=None,
    public_language_action=None,
    no_expansion_confirmed=True,
    no_public_claim_upgrade=True,
    no_service_record_edit=True,
    no_lifecycle_change=True,
    no_closure_from_dispatch=True,
    raw_learner_data_present=False,
    protected_facts_present=False,
    security_payloads_present=False,
    public_claim_upgrade_requested=False,
    operator_confirmation=ACTION_CONFIRMATION,
)
for overrides, label in blocked_cases:
    args = dict(base)
    args.update(overrides)
    args['output_dir'] = TMP / 'owner-post-readout-actions' / f'blocked-{label.replace(" ", "-")}'
    try:
        build_post_readout_action(**args)
        fail(errors, f'post-readout action with {label} problem should block')
    except ValueError as exc:
        payload = json.loads(str(exc))
        if payload.get('ok') is not False or 'POST-READOUT-ACTION' not in payload.get('outcome', ''):
            fail(errors, f'{label} block should be machine-readable: {payload}')

rerun_readout = build_readout(TMP / 'source-rerun', disposition='rerun-narrower', field_trim_count=1)
try:
    build_post_readout_action(**{**base, 'readout': rerun_readout, 'dispatch_lane': 'rerun-narrower', 'field_to_reask_count': 0, 'field_to_drop_count': 1, 'output_dir': TMP / 'owner-post-readout-actions' / 'rerun-no-reask'})
    fail(errors, 'rerun_narrower dispatch without a reask field should block')
except ValueError as exc:
    payload = json.loads(str(exc))
    if payload.get('outcome') != 'POST-READOUT-ACTION-INTEGRITY-BLOCKED':
        fail(errors, f'rerun no-reask block missing code: {payload}')
try:
    build_post_readout_action(**{**base, 'readout': readout, 'output_dir': ROOT / 'docs' / 'bad-post-readout-action'})
    fail(errors, 'post-readout action output to docs should be blocked')
except ValueError as exc:
    payload = json.loads(str(exc))
    if payload.get('outcome') != 'POST-READOUT-ACTION-OUTPUT-BLOCKED':
        fail(errors, f'controlled output block missing code: {payload}')

if errors:
    shutil.rmtree(TMP, ignore_errors=True)
    raise SystemExit('check_ft0181_post_readout_action: FAIL\n- ' + '\n- '.join(errors))
shutil.rmtree(TMP, ignore_errors=True)
print('check_ft0181_post_readout_action: OK (readout hash gate, lane mapping, no-service/no-public/no-closure firebreak, minimization, output boundary)')
