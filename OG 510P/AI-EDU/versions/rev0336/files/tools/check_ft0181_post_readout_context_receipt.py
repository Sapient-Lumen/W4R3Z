#!/usr/bin/env python3
"""Smoke-test the FT-0181 post-readout recheck gate."""
from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from pathlib import Path

from ft0181_validation_fixtures import build_valid_sent_contact_status
from record_ft0181_activation_receipt import OPERATOR_CONFIRMATION as ACTIVATION_CONFIRMATION, build_activation_receipt
from record_ft0181_first_packet_decision import OPERATOR_CONFIRMATION as DECISION_CONFIRMATION, build_decision
from record_ft0181_live_window_card import OPERATOR_CONFIRMATION as CARD_CONFIRMATION, build_live_window_card
from record_ft0181_live_window_readout import OPERATOR_CONFIRMATION as READOUT_CONFIRMATION, build_live_window_readout
from record_ft0181_post_decision_change_ticket import OPERATOR_CONFIRMATION as TICKET_CONFIRMATION, build_change_ticket
from record_ft0181_post_readout_action import OPERATOR_CONFIRMATION as ACTION_CONFIRMATION, build_post_readout_action
from record_ft0181_post_readout_recheck import OPERATOR_CONFIRMATION as RECHECK_CONFIRMATION, build_post_readout_recheck
from record_ft0181_post_readout_context_receipt import OPERATOR_CONFIRMATION as CONTEXT_CONFIRMATION, build_post_readout_context_receipt
from intake_owner_reply_csv import bundle_intake
from seed_owner_packet_workbench import build_seed
from record_ft0181_workbench_review import OPERATOR_CONFIRMATION as REVIEW_CONFIRMATION, build_review
from ft0181_field_guards import owner_post_readout_recheck_integrity_error, owner_post_readout_context_receipt_integrity_error, owner_workbench_seed_integrity_error

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / 'scratch' / 'field' / 'ft0181' / 'validation' / 'ft0181-post-readout-context-receipt'


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
            source_slug='ft0181-post-readout-context-receipt-source-send-log',
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


def build_action(base_dir: Path, *, due_or_recheck_date: str = '2026-06-25') -> Path:
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
        operator_confirmation=CARD_CONFIRMATION,
        output_dir=base_dir / 'owner-live-window-cards' / 'terminal',
    )
    build_live_window_readout(
        card=base_dir / 'owner-live-window-cards' / 'terminal' / 'live-window-card.json',
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
        output_dir=base_dir / 'owner-live-window-readouts' / 'valid',
    )
    build_post_readout_action(
        readout=base_dir / 'owner-live-window-readouts' / 'valid' / 'live-window-readout.json',
        dispatch_lane='continue-same-ceiling',
        source_truth_class='SRC2',
        allowed_action_count=1,
        prohibited_action_count=5,
        field_to_reask_count=0,
        field_to_drop_count=0,
        reviewer_role_count=2,
        unresolved_disagreement_count=0,
        due_or_recheck_date=due_or_recheck_date,
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
        output_dir=base_dir / 'owner-post-readout-actions' / 'valid',
    )
    return base_dir / 'owner-post-readout-actions' / 'valid' / 'post-readout-action.json'



if TMP.exists():
    shutil.rmtree(TMP)
for stale_packet_root in (ROOT / 'scratch' / 'field' / 'ft0181').glob(f'activation-source-validation-{TMP.name.removeprefix("check-")}*-source-packets'):
    shutil.rmtree(stale_packet_root, ignore_errors=True)
TMP.mkdir(parents=True, exist_ok=True)
EXTERNAL_CSV_DIR = Path(tempfile.mkdtemp(prefix='ft0181-post-readout-context-'))
errors: list[str] = []
action = build_action(TMP / 'source-action')

# A no-context recheck must not source a post-readout context receipt.
no_context_summary = build_post_readout_recheck(
    action=action,
    check_date='2026-06-25',
    recheck_outcome='no-new-owner-context',
    reviewer_role_count=2,
    operator_confirmation=RECHECK_CONFIRMATION,
    no_expansion_confirmed=True,
    no_public_claim_upgrade=True,
    no_service_record_edit=True,
    no_lifecycle_change=True,
    no_closure_from_recheck=True,
    new_owner_context_held_outside_archive=False,
    raw_learner_data_present=False,
    protected_facts_present=False,
    security_payloads_present=False,
    public_claim_upgrade_requested=False,
    output_dir=TMP / 'owner-post-readout-rechecks' / 'no-context',
)
if no_context_summary.get('outcome') != 'POST-READOUT-RECHECK-RECORDED':
    fail(errors, f'no-context recheck setup failed: {no_context_summary}')

new_context_summary = build_post_readout_recheck(
    action=action,
    check_date='2026-06-26',
    recheck_outcome='new-owner-context-available',
    reviewer_role_count=2,
    operator_confirmation=RECHECK_CONFIRMATION,
    no_expansion_confirmed=True,
    no_public_claim_upgrade=True,
    no_service_record_edit=True,
    no_lifecycle_change=True,
    no_closure_from_recheck=True,
    new_owner_context_held_outside_archive=True,
    raw_learner_data_present=False,
    protected_facts_present=False,
    security_payloads_present=False,
    public_claim_upgrade_requested=False,
    output_dir=TMP / 'owner-post-readout-rechecks' / 'new-context',
)
if new_context_summary.get('outcome') != 'POST-READOUT-RECHECK-RECORDED':
    fail(errors, f'new-context recheck setup failed: {new_context_summary}')
recheck_path = TMP / 'owner-post-readout-rechecks' / 'new-context' / 'post-readout-recheck.json'

owner_context_csv = EXTERNAL_CSV_DIR / 'post-readout-owner-context.csv'
owner_context_csv.parent.mkdir(parents=True, exist_ok=True)
owner_context_csv.write_text(
    'row_id,required_owner_reply,owner_response,local_only_check,intake_note\n'
    '1,service/date/source,"AIEDU-SR-003 capped draft-reminder workflow; course operations lead via local course ops mailbox; local reminder queue; 2026-05-01 to 2026-05-31.",route class only,post-readout context\n'
    '2,aggregate counts,"Aggregate counts above local threshold: eligible 120, draft-reminder 43, human-sent 31, discarded 12, fallback/manual route 5, corrections 2, incidents 0.",aggregate only,post-readout context\n'
    '3,authority ceiling,"Draft-only queue note; no automatic send; no durable write or posting; no penalty or grading effect; no protected-status inference.",authority bounded,post-readout context\n'
    '4,rollback owner,"Human fallback is normal staff outreach; rollback owner is course operations lead; incident class labels none; stop if fallback count spikes or any penalty route appears.",role class only,post-readout context\n'
    '5,workload signal,"Workload signal unknown for first packet; method not yet instrumented beyond owner estimate.",unknown allowed,post-readout context\n'
    '6,guidance,"Guidance note: staff received short local workflow guidance owned by course operations; no named staff evaluation attached.",class label only,post-readout context\n'
    '7,public ceiling,"Public claim ceiling: process-only staging note; do not claim learning, safety, access, workload, compliance, scale, or effectiveness.",claim ceiling,post-readout context\n'
    '8,redaction,"Real owner-attested operational aggregate; raw learner data, protected facts, small cells, gradebook rows, messages, and security details were removed, withheld, or kept local.",redaction assertion,post-readout context\n',
    encoding='utf-8',
)

summary = build_post_readout_context_receipt(
    recheck=recheck_path,
    csv_path=owner_context_csv,
    reviewer_role_count=2,
    operator_confirmation=CONTEXT_CONFIRMATION,
    no_expansion_confirmed=True,
    no_public_claim_upgrade=True,
    no_service_record_edit=True,
    no_lifecycle_change=True,
    no_closure_from_context_receipt=True,
    raw_learner_data_present=False,
    protected_facts_present=False,
    security_payloads_present=False,
    public_claim_upgrade_requested=False,
    output_dir=TMP / 'owner-post-readout-context-receipts' / 'valid',
)
if summary.get('outcome') != 'POST-READOUT-CONTEXT-RECEIPT-RECORDED':
    fail(errors, f'valid context receipt should record: {summary}')
receipt_path = TMP / 'owner-post-readout-context-receipts' / 'valid' / 'post-readout-context-receipt.json'
receipt = load_json(receipt_path)
err = owner_post_readout_context_receipt_integrity_error(receipt, archive_root=ROOT)
if err:
    fail(errors, f'valid context receipt should pass guard: {err}')
if receipt.get('source_csv', {}).get('sha256') != sha256_file(owner_context_csv):
    fail(errors, 'context receipt must hash the actual returned owner-context CSV')
if receipt.get('source_post_readout_recheck', {}).get('recheck_outcome') != 'new_owner_context_available':
    fail(errors, 'context receipt must point to a new-context recheck')
text = receipt_path.read_text(encoding='utf-8') + (TMP / 'owner-post-readout-context-receipts' / 'valid' / 'POST-READOUT-CONTEXT-RECEIPT-SUMMARY.md').read_text(encoding='utf-8')
for forbidden in ['Aggregate count above threshold', 'AIEDU-SR-003 bounded post-readout owner context']:
    if forbidden in text:
        fail(errors, f'context receipt leaked owner context content: {forbidden}')

# The new receipt can source intake and seed without falling back to an old contact clock.
intake_dir = TMP / 'owner-reply-intakes' / 'from-context-receipt'
intake = bundle_intake(owner_context_csv, intake_dir, source_contact_status=None, source_post_readout_context_receipt=receipt_path)
if intake.get('triage_outcome') != 'PROCEED-STAGED':
    fail(errors, f'intake from post-readout context receipt should proceed-staged: {intake}')
manifest = load_json(intake_dir / 'bundle-manifest.json')
if manifest.get('source_contact_status') is not None:
    fail(errors, 'post-readout context intake must not attach an old source_contact_status')
if manifest.get('source_post_readout_context_receipt', {}).get('reference') != rel(receipt_path):
    fail(errors, 'intake manifest must preserve source_post_readout_context_receipt reference')
if manifest.get('content_minimization', {}).get('source_post_readout_context_receipt_required') is not True:
    fail(errors, 'intake manifest must record post-readout context receipt gate')
seed_summary = build_seed(intake_dir, TMP / 'owner-reply-workbench-seeds' / 'from-context-receipt')
if seed_summary.get('acceptance_state') != 'NOT_ACCEPTED':
    fail(errors, f'seed from post-readout context receipt must stay NOT_ACCEPTED: {seed_summary}')
seed = load_json(TMP / 'owner-reply-workbench-seeds' / 'from-context-receipt' / 'workbench-seed.json')
seed_err = owner_workbench_seed_integrity_error(seed, archive_root=ROOT)
if seed_err:
    fail(errors, f'seed from context receipt should pass shared guard: {seed_err}')
if seed.get('source_contact_status') is not None:
    fail(errors, 'seed from post-readout context must not resurrect source_contact_status')
if seed.get('source_post_readout_context_receipt', {}).get('revalidated_for_seed') is not True:
    fail(errors, 'seed must revalidate source_post_readout_context_receipt')

blocked_cases = [
    ({'recheck': TMP / 'owner-post-readout-rechecks' / 'no-context' / 'post-readout-recheck.json'}, 'no context recheck'),
    ({'operator_confirmation': 'human-says-ok'}, 'bad confirmation'),
    ({'reviewer_role_count': 1}, 'single reviewer'),
    ({'no_expansion_confirmed': False}, 'expansion firebreak'),
    ({'no_public_claim_upgrade': False}, 'public firebreak'),
    ({'no_service_record_edit': False}, 'service firebreak'),
    ({'no_lifecycle_change': False}, 'lifecycle firebreak'),
    ({'no_closure_from_context_receipt': False}, 'closure firebreak'),
    ({'raw_learner_data_present': True}, 'raw learner'),
    ({'protected_facts_present': True}, 'protected facts'),
    ({'security_payloads_present': True}, 'security payload'),
    ({'public_claim_upgrade_requested': True}, 'public claim upgrade'),
]
base = dict(
    recheck=recheck_path,
    csv_path=owner_context_csv,
    reviewer_role_count=2,
    operator_confirmation=CONTEXT_CONFIRMATION,
    no_expansion_confirmed=True,
    no_public_claim_upgrade=True,
    no_service_record_edit=True,
    no_lifecycle_change=True,
    no_closure_from_context_receipt=True,
    raw_learner_data_present=False,
    protected_facts_present=False,
    security_payloads_present=False,
    public_claim_upgrade_requested=False,
)
for overrides, label in blocked_cases:
    args = dict(base)
    args.update(overrides)
    args['output_dir'] = TMP / 'owner-post-readout-context-receipts' / f'blocked-{label.replace(" ", "-")}'
    try:
        build_post_readout_context_receipt(**args)
        fail(errors, f'post-readout context receipt with {label} problem should block')
    except ValueError as exc:
        payload = json.loads(str(exc))
        if payload.get('ok') is not False or 'POST-READOUT-CONTEXT' not in payload.get('outcome', ''):
            fail(errors, f'{label} block should be machine-readable: {payload}')

smoke_csv = EXTERNAL_CSV_DIR / 'smoke.csv'
smoke_csv.write_text('row_id,owner_response\n1,synthetic smoke fixture only\n', encoding='utf-8')
try:
    build_post_readout_context_receipt(**{**base, 'csv_path': smoke_csv, 'output_dir': TMP / 'owner-post-readout-context-receipts' / 'blocked-smoke'})
    fail(errors, 'smoke-labeled returned context should be blocked')
except ValueError as exc:
    payload = json.loads(str(exc))
    if payload.get('outcome') != 'POST-READOUT-CONTEXT-CSV-SMOKE-BLOCKED':
        fail(errors, f'smoke context block missing code: {payload}')

try:
    build_post_readout_context_receipt(**{**base, 'output_dir': ROOT / 'docs' / 'bad-post-readout-context-receipt'})
    fail(errors, 'context receipt output to docs should be blocked')
except ValueError as exc:
    payload = json.loads(str(exc))
    if payload.get('outcome') != 'POST-READOUT-CONTEXT-RECEIPT-OUTPUT-BLOCKED':
        fail(errors, f'controlled output block missing code: {payload}')

wrong_csv = EXTERNAL_CSV_DIR / 'wrong.csv'
wrong_csv.write_text(owner_context_csv.read_text(encoding='utf-8') + '\n', encoding='utf-8')
try:
    bundle_intake(wrong_csv, TMP / 'owner-reply-intakes' / 'wrong-context-hash', source_contact_status=None, source_post_readout_context_receipt=receipt_path)
    fail(errors, 'intake with CSV hash mismatch should be blocked')
except ValueError as exc:
    payload = json.loads(str(exc))
    if payload.get('outcome') != 'INTAKE-SOURCE-POST-READOUT-CONTEXT-HASH-BLOCKED':
        fail(errors, f'intake hash block missing code: {payload}')

if errors:
    shutil.rmtree(TMP, ignore_errors=True)
    shutil.rmtree(EXTERNAL_CSV_DIR, ignore_errors=True)
    raise SystemExit('check_ft0181_post_readout_context_receipt: FAIL\n- ' + '\n- '.join(errors))
shutil.rmtree(TMP, ignore_errors=True)
shutil.rmtree(EXTERNAL_CSV_DIR, ignore_errors=True)
print('check_ft0181_post_readout_context_receipt: OK (new-context recheck-to-CSV receipt, hash match, intake/seed provenance, no old clock fallback, minimization, and output/source blocks)')
