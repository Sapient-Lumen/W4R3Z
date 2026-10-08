#!/usr/bin/env python3
"""Smoke-test the FT-0181 terminal live-window readout brief bridge."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from ft0181_validation_fixtures import build_valid_sent_contact_status
from prepare_ft0181_live_window_readout_brief import build_readout_brief
from record_ft0181_activation_receipt import OPERATOR_CONFIRMATION as ACTIVATION_CONFIRMATION, build_activation_receipt
from record_ft0181_first_packet_decision import OPERATOR_CONFIRMATION as DECISION_CONFIRMATION, build_decision
from record_ft0181_live_window_card import OPERATOR_CONFIRMATION as CARD_CONFIRMATION, build_live_window_card
from record_ft0181_post_decision_change_ticket import OPERATOR_CONFIRMATION as TICKET_CONFIRMATION, build_change_ticket
from record_ft0181_workbench_review import OPERATOR_CONFIRMATION as REVIEW_CONFIRMATION, build_review
from ft0181_field_guards import owner_live_window_readout_brief_integrity_error

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / 'scratch' / 'field' / 'ft0181' / 'validation' / 'ft0181-live-window-readout-brief'


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
            source_slug='ft0181-live-window-readout-brief-source-send-log',
        )
    except RuntimeError as exc:
        raise SystemExit(str(exc))


def write_seed(path: Path, source_contact_status: Path, source_packet: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        'seed_type': 'FT-0181-owner-packet-workbench-seed',
        'seed_version': 'rev0300',
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


def build_card(state: str, label: str) -> Path:
    base_dir = TMP / label
    source_packet = base_dir / 'activation-source-packets' / 'real-owner-packet.csv'
    source_packet.parent.mkdir(parents=True, exist_ok=True)
    source_packet.write_text('field_key,owner_attested_class,decision_effect\nallowed_count,aggregate_owner_attested,changes_one_bounded_slice\n', encoding='utf-8')
    source_contact = write_source_contact_status(base_dir / 'owner-contact-status' / 'sent' / 'contact-status.json')
    seed = write_seed(base_dir / 'owner-reply-workbench-seeds' / 'aiedu-sr-003' / 'workbench-seed.json', source_contact, source_packet)
    review = build_review(
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
    assert review.get('ok')
    decision = build_decision(
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
    assert decision.get('ok')
    receipt = build_activation_receipt(
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
    assert receipt.get('ok')
    ticket = build_change_ticket(
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
    assert ticket.get('ok')
    card = build_live_window_card(
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
        output_dir=base_dir / 'owner-live-window-cards' / state,
    )
    assert card.get('ok')
    return base_dir / 'owner-live-window-cards' / state / 'live-window-card.json'


if TMP.exists():
    shutil.rmtree(TMP)
for stale_packet_root in (ROOT / 'scratch' / 'field' / 'ft0181').glob(f'activation-source-validation-{TMP.name.removeprefix("check-")}*-source-packets'):
    shutil.rmtree(stale_packet_root, ignore_errors=True)
TMP.mkdir(parents=True, exist_ok=True)
errors: list[str] = []

terminal = build_card('completed-no-closure', 'terminal')
result = build_readout_brief(card=terminal, output_dir=TMP / 'owner-live-window-readout-briefs' / 'valid')
if result.get('outcome') != 'LIVE-WINDOW-READOUT-BRIEF-PREPARED':
    fail(errors, f'valid readout brief should prepare: {result}')
brief_path = TMP / 'owner-live-window-readout-briefs' / 'valid' / 'live-window-readout-brief.json'
brief = load_json(brief_path)
err = owner_live_window_readout_brief_integrity_error(brief, archive_root=ROOT)
if err:
    fail(errors, f'valid readout brief should pass guard: {err}')
primary = brief.get('readout_command_templates', {}).get('primary', '')
for token in ['make owner-live-window-readout', 'WINDOW_DISPOSITION=continue-bounded', 'CONFIRM=human-recorded-aggregate-readout-no-closure', 'NO_CLOSURE_FROM_READOUT=1']:
    if token not in primary:
        fail(errors, f'primary command missing {token}')
if 'make owner-post-readout-action' in primary or primary.startswith('make owner-live-window-card '):
    fail(errors, 'readout brief primary command must not jump to post-readout action or rewrite cards')
text = brief_path.read_text(encoding='utf-8') + (TMP / 'owner-live-window-readout-briefs' / 'valid' / 'LIVE-WINDOW-READOUT-BRIEF.md').read_text(encoding='utf-8')
for forbidden in ['student id', 'learner name', '@example', 'chat transcript', 'raw LMS telemetry']:
    if forbidden in text.lower():
        fail(errors, f'brief leaked forbidden/raw/contact/claim term: {forbidden}')

for state, disposition in [('paused', 'stopped'), ('rolled-back', 'rolled-back'), ('quarantined', 'quarantine')]:
    card = build_card(state, state)
    out = TMP / 'owner-live-window-readout-briefs' / state
    build_readout_brief(card=card, output_dir=out)
    command = load_json(out / 'live-window-readout-brief.json')['readout_command_templates']['primary']
    if f'WINDOW_DISPOSITION={disposition}' not in command:
        fail(errors, f'{state} primary readout command should use {disposition}: {command}')

nonterminal = build_card('active', 'nonterminal')
try:
    build_readout_brief(card=nonterminal, output_dir=TMP / 'owner-live-window-readout-briefs' / 'bad-nonterminal')
    fail(errors, 'nonterminal live-window card should not produce a readout brief')
except ValueError as exc:
    if 'TERMINAL-CARD-REQUIRED' not in str(exc):
        fail(errors, f'nonterminal block should name terminal-card requirement: {exc}')

tampered = dict(brief)
tampered['readout_effect'] = 'records_readout'
err = owner_live_window_readout_brief_integrity_error(tampered, archive_root=ROOT)
if not err or 'readout_effect' not in err:
    fail(errors, f'tampered brief should fail readout-effect guard, got {err}')

if errors:
    shutil.rmtree(TMP, ignore_errors=True)
    raise SystemExit('check_ft0181_live_window_readout_brief errors:\n' + '\n'.join(errors))
shutil.rmtree(TMP, ignore_errors=True)
print('check_ft0181_live_window_readout_brief: OK')
