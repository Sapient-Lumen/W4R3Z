#!/usr/bin/env python3
"""Smoke-test the FT-0181 terminal live-window readout gate."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from ft0181_validation_fixtures import build_valid_sent_contact_status
from record_ft0181_activation_receipt import OPERATOR_CONFIRMATION as ACTIVATION_CONFIRMATION, build_activation_receipt
from record_ft0181_first_packet_decision import OPERATOR_CONFIRMATION as DECISION_CONFIRMATION, build_decision
from record_ft0181_live_window_card import OPERATOR_CONFIRMATION as CARD_CONFIRMATION, build_live_window_card
from record_ft0181_live_window_readout import OPERATOR_CONFIRMATION as READOUT_CONFIRMATION, build_live_window_readout
from record_ft0181_post_decision_change_ticket import OPERATOR_CONFIRMATION as TICKET_CONFIRMATION, build_change_ticket
from record_ft0181_workbench_review import OPERATOR_CONFIRMATION as REVIEW_CONFIRMATION, build_review
from ft0181_field_guards import owner_live_window_readout_integrity_error

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / 'scratch' / 'field' / 'ft0181' / 'validation' / 'ft0181-live-window-readout'


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def sha256_file(path: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def fail(errors: list[str], msg: str) -> None:
    errors.append(msg)


def write_source_contact_status(path: Path) -> Path:
    try:
        return build_valid_sent_contact_status(
            path,
            root=ROOT,
            sent_date='2026-06-13',
            response_due_date='2026-06-20',
            status_date='2026-06-13',
            source_slug='ft0181-live-window-readout-source-send-log',
        )
    except RuntimeError as exc:
        raise SystemExit(str(exc))


def write_seed(path: Path, source_contact_status: Path, source_packet: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        'seed_type': 'FT-0181-owner-packet-workbench-seed',
        'seed_version': 'rev0286',
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


def build_terminal_card(state: str = 'completed-no-closure', label: str = 'terminal') -> Path:
    base_dir = TMP / label
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
        window_state=state,
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
    return base_dir / 'owner-live-window-cards' / 'terminal' / 'live-window-card.json'


if TMP.exists():
    shutil.rmtree(TMP)
for stale_packet_root in (ROOT / 'scratch' / 'field' / 'ft0181').glob(f'activation-source-validation-{TMP.name.removeprefix("check-")}*-source-packets'):
    shutil.rmtree(stale_packet_root, ignore_errors=True)
TMP.mkdir(parents=True, exist_ok=True)
errors: list[str] = []
card = build_terminal_card('completed-no-closure')
summary = build_live_window_readout(
    card=card,
    window_disposition='continue-bounded',
    source_truth_class='SRC2',
    aggregate_evidence_read_count=3,
    claim_family_effect_count=2,
    decision_delta_count=1,
    field_trim_count=0,
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
    output_dir=TMP / 'owner-live-window-readouts' / 'valid',
)
if summary.get('outcome') != 'LIVE-WINDOW-READOUT-RECORDED':
    fail(errors, f'valid readout should record: {summary}')
readout_path = TMP / 'owner-live-window-readouts' / 'valid' / 'live-window-readout.json'
readout = load_json(readout_path)
err = owner_live_window_readout_integrity_error(readout, archive_root=ROOT)
if err:
    fail(errors, f'valid readout should pass guard: {err}')
if readout.get('closure_permitted') is not False or readout.get('closure_effect') != 'does_not_close_ft0181':
    fail(errors, 'readout must not permit closure')
if readout.get('required_next_surface') != 'docs/30-operations/ft0181-post-readout-action-dispatch.md':
    fail(errors, 'readout must route only to post-readout action dispatch')
text = readout_path.read_text(encoding='utf-8') + (TMP / 'owner-live-window-readouts' / 'valid' / 'LIVE-WINDOW-READOUT-SUMMARY.md').read_text(encoding='utf-8')
for forbidden in ['eligible 120', 'course operations lead via', 'raw LMS telemetry is attached', '@example', 'chat transcript']:
    if forbidden in text:
        fail(errors, f'readout leaked owner/contact/raw content: {forbidden}')

blocked_cases = [
    ({'aggregate_evidence_read_count': 2}, 'below source readout count'),
    ({'claim_family_effect_count': 0}, 'missing claim family effect'),
    ({'decision_delta_count': 0}, 'continue without delta'),
    ({'reviewer_role_count': 1}, 'single reviewer'),
    ({'no_public_claim_upgrade': False}, 'public claim firebreak'),
    ({'no_service_record_edit': False}, 'service edit firebreak'),
    ({'no_lifecycle_change': False}, 'lifecycle firebreak'),
    ({'no_closure_from_readout': False}, 'closure firebreak'),
    ({'source_truth_class': 'SRC3'}, 'mismatched source truth'),
    ({'raw_learner_data_present': True}, 'raw learner'),
    ({'protected_facts_present': True}, 'protected'),
    ({'security_payloads_present': True}, 'security'),
    ({'public_claim_upgrade_requested': True}, 'public claim upgrade'),
]
base = dict(
    card=card,
    window_disposition='continue-bounded',
    source_truth_class='SRC2',
    aggregate_evidence_read_count=3,
    claim_family_effect_count=2,
    decision_delta_count=1,
    field_trim_count=0,
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
)
for overrides, label in blocked_cases:
    args = dict(base)
    args.update(overrides)
    args['output_dir'] = TMP / 'owner-live-window-readouts' / f'blocked-{label.replace(" ", "-")}'
    try:
        build_live_window_readout(**args)
        fail(errors, f'readout with {label} problem should block')
    except ValueError as exc:
        payload = json.loads(str(exc))
        if payload.get('ok') is not False or 'LIVE-WINDOW-READOUT' not in payload.get('outcome', ''):
            fail(errors, f'{label} block should be machine-readable: {payload}')

# Nonterminal cards cannot source readouts.
staged_card = build_terminal_card('staged', label='staged-source')
try:
    build_live_window_readout(**{**base, 'card': staged_card, 'output_dir': TMP / 'owner-live-window-readouts' / 'staged-card-block'})
    fail(errors, 'staged live-window card should not source terminal readout')
except ValueError as exc:
    payload = json.loads(str(exc))
    if payload.get('outcome') != 'LIVE-WINDOW-READOUT-NONTERMINAL-CARD-BLOCKED':
        fail(errors, f'nonterminal card block missing code: {payload}')

# Output into controlled docs space is blocked.
try:
    build_live_window_readout(**{**base, 'card': card, 'output_dir': ROOT / 'docs' / 'bad-live-window-readout'})
    fail(errors, 'live-window readout output to docs should be blocked')
except ValueError as exc:
    payload = json.loads(str(exc))
    if payload.get('outcome') != 'LIVE-WINDOW-READOUT-OUTPUT-BLOCKED':
        fail(errors, f'controlled output block missing code: {payload}')

if errors:
    shutil.rmtree(TMP, ignore_errors=True)
    raise SystemExit('check_ft0181_live_window_readout: FAIL\n- ' + '\n- '.join(errors))
shutil.rmtree(TMP, ignore_errors=True)
print('check_ft0181_live_window_readout: OK (terminal-card validation, aggregate readout counts, no-closure firebreak, minimization, blocks, output boundary)')
