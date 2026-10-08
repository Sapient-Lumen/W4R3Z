#!/usr/bin/env python3
"""Validate FT-0181 runnable field next-action routing utility."""
from __future__ import annotations

import csv
import hashlib
import os
import json
import shutil
import shlex
import tempfile
import time
from datetime import date, timedelta
from pathlib import Path

from decide_ft0181_field_next_action import decide_and_write, run_safe_local_field_session
from prepare_ft0181_owner_request_packet import build_packet, default_return_date
from record_ft0181_owner_send_log import OPERATOR_CONFIRMATION as SEND_LOG_CONFIRMATION, build_send_log
from record_ft0181_owner_after_human_send import build_after_human_send
from record_ft0181_owner_reask_log import OPERATOR_CONFIRMATION as REASK_LOG_CONFIRMATION, build_reask_log
from prepare_ft0181_workbench_review_brief import build_review_brief
from prepare_ft0181_first_packet_decision_brief import build_decision_brief
from prepare_ft0181_post_decision_change_ticket_brief import build_change_ticket_brief
from prepare_ft0181_activation_live_window_brief import build_activation_live_window_brief
from prepare_ft0181_live_window_terminal_brief import build_terminal_brief
from prepare_ft0181_live_window_readout_brief import build_readout_brief
from prepare_ft0181_post_readout_action_brief import build_post_readout_action_brief
from prepare_ft0181_post_readout_recheck_brief import build_post_readout_recheck_brief
from record_ft0181_workbench_review import OPERATOR_CONFIRMATION as WORKBENCH_REVIEW_CONFIRMATION, build_review
from record_ft0181_first_packet_decision import OPERATOR_CONFIRMATION as FIRST_PACKET_DECISION_CONFIRMATION, build_decision
from record_ft0181_post_decision_change_ticket import OPERATOR_CONFIRMATION as POST_DECISION_TICKET_CONFIRMATION, build_change_ticket
from record_ft0181_activation_receipt import OPERATOR_CONFIRMATION as ACTIVATION_RECEIPT_CONFIRMATION, build_activation_receipt
from record_ft0181_live_window_card import OPERATOR_CONFIRMATION as LIVE_WINDOW_CONFIRMATION, build_live_window_card
from record_ft0181_live_window_readout import OPERATOR_CONFIRMATION as LIVE_WINDOW_READOUT_CONFIRMATION, build_live_window_readout
from record_ft0181_post_readout_action import OPERATOR_CONFIRMATION as POST_READOUT_ACTION_CONFIRMATION, build_post_readout_action
from record_ft0181_post_readout_recheck import OPERATOR_CONFIRMATION as POST_READOUT_RECHECK_CONFIRMATION, build_post_readout_recheck
from record_ft0181_post_readout_context_receipt import OPERATOR_CONFIRMATION as POST_READOUT_CONTEXT_RECEIPT_CONFIRMATION, build_post_readout_context_receipt
from ft0181_field_guards import operator_due_date_iso, operator_today_iso
from record_ft0181_owner_contact_status import (
    OPERATOR_CONFIRMATIONS,
    build_status,
    validate_contact_clock,
    validate_operator_confirmation,
)
from report_ft0181_field_lane import scan_lane

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_REVISION = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8')).get('revision')
TMP = ROOT / 'scratch' / 'field' / 'ft0181' / 'validation' / 'ft0181-field-next-action'
FIELD_TMP = ROOT / 'scratch' / 'field' / 'ft0181' / 'field-next-action-validation'
SUPPORT_TMP = ROOT / 'scratch' / 'field' / 'ft0181' / 'field-next-action-source-anchor-support'


def fail(msg: str) -> None:
    raise SystemExit(f'check_ft0181_field_next_action: FAIL: {msg}')


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def context_for(status: str, source: Path | str) -> dict[str, str]:
    source_text = rel(source) if isinstance(source, Path) else source
    return {
        'operator_confirmation': OPERATOR_CONFIRMATIONS[status],
        'source_artifact': source_text,
    }




def assert_operator_date_defaults() -> None:
    old_as_of = os.environ.get('CUBE_AS_OF_DATE')
    old_legacy = os.environ.get('FT0181_AS_OF_DATE')
    old_tz = os.environ.get('CUBE_OPERATOR_TIMEZONE')
    try:
        os.environ['CUBE_AS_OF_DATE'] = '2026-06-16'
        os.environ.pop('FT0181_AS_OF_DATE', None)
        os.environ['CUBE_OPERATOR_TIMEZONE'] = 'America/New_York'
        if operator_today_iso() != '2026-06-16':
            fail('operator_today_iso must honor CUBE_AS_OF_DATE for cloudtainer/local-date drift')
        if operator_due_date_iso(7) != '2026-06-23':
            fail('operator_due_date_iso must anchor to the operator-local date override')
        if default_return_date() != '2026-06-23':
            fail('owner request packet default return date must use the operator-local date helper')
    finally:
        for key, old in [
            ('CUBE_AS_OF_DATE', old_as_of),
            ('FT0181_AS_OF_DATE', old_legacy),
            ('CUBE_OPERATOR_TIMEZONE', old_tz),
        ]:
            if old is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old

def contact_session_root(path: Path) -> Path:
    parts = list(path.parts)
    if 'owner-contact-status' in parts:
        idx = parts.index('owner-contact-status')
        return Path(*parts[:idx])
    return path.parent.parent


def write_dummy_contact_source(path: Path, *, contact_status: str, sent_date: str, response_due_date: str, status_date: str, attempt_count: int) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        'status_id': 'AIEDU-SR-003-OWNER-CONTACT-STATUS',
        'followthrough_id': 'FT-0181',
        'contact_status': contact_status,
        'sent_date': sent_date,
        'response_due_date': response_due_date,
        'status_date': status_date,
        'attempt_count': attempt_count,
        'max_response_clock_days': 7 if contact_status == 'SENT_AWAITING_REPLY' else 3,
        'created_at_utc': f'{status_date}T00:00:00Z',
        'evidence_state': 'not_evidence',
        'source_truth_class': 'not_evidence',
        'closure_effect': 'does_not_close_ft0181',
        'public_claim_effect': 'none',
        'source_artifact_verified': True,
        'source_artifact_ref': 'scratch/checks/check-fixture/source-artifact.json',
        'source_artifact_type': 'send-log' if contact_status == 'SENT_AWAITING_REPLY' else 'reask-log',
        'no_widening_confirmation': True,
    }, indent=2) + '\n', encoding='utf-8')
    return path


def build_source_send_log(session_root: Path, name: str, *, sent_date: str, response_due_date: str) -> Path:
    source_root = SUPPORT_TMP / rel(session_root).replace('/', '__')
    packet_dir = source_root / 'owner-request-packets' / name
    packet = build_packet(
        output_dir=packet_dir,
        service_label='AIEDU-SR-003 draft reminder pilot',
        owner_role='accountable service owner route',
        source_record_set='owner-maintained local service record set',
        date_range='2026-06-01 through 2026-06-07',
        return_date=response_due_date,
        overwrite=True,
    )
    if not packet.get('ok'):
        fail(f'{name} packet fixture did not build for contact source: {packet}')
    send_dir = source_root / 'owner-send-logs' / name
    send = build_send_log(
        output_dir=send_dir,
        packet_manifest=packet_dir / 'packet-manifest.json',
        sent_date=sent_date,
        response_due_date=response_due_date,
        service_label='AIEDU-SR-003 draft reminder pilot',
        owner_role='accountable service owner route',
        source_record_set='owner-maintained local service record set',
        date_range='2026-06-01 through 2026-06-07',
        send_channel_class='email',
        owner_route_class='accountable-owner',
        operator_confirmation=SEND_LOG_CONFIRMATION,
        overwrite=True,
    )
    if not send.get('ok'):
        fail(f'{name} send-log fixture did not build for contact source: {send}')
    return send_dir / 'send-log.json'


def write_contact_source(path: Path, *, contact_status: str, sent_date: str, response_due_date: str, status_date: str, attempt_count: int) -> Path:
    # Deliberately ignored check/smoke/test/fixture lanes only need dummy JSON so
    # the router firebreak can prove it does not inspect them. Routable positive
    # fixtures need a real source log because returned-owner intake now re-anchors
    # contact clocks to their source send/reask artifact.
    if any(part.startswith(('check-', 'smoke-', 'test-', 'fixture-')) or part in {'checks', 'releases'} for part in path.parts):
        return write_dummy_contact_source(
            path,
            contact_status=contact_status,
            sent_date=sent_date,
            response_due_date=response_due_date,
            status_date=status_date,
            attempt_count=attempt_count,
        )

    session_root = contact_session_root(path)
    name = path.parent.name or 'contact-source'
    if contact_status == 'SENT_AWAITING_REPLY':
        source = build_source_send_log(session_root, f'{name}-send-source', sent_date=sent_date, response_due_date=response_due_date)
        status_key = 'sent-awaiting-reply'
    elif contact_status == 'REASK_AWAITING_REPLY':
        reask_sent = date.fromisoformat(sent_date)
        prior_sent = reask_sent - timedelta(days=7)
        prior_due = reask_sent - timedelta(days=1)
        prior_sent_status = write_contact_source(
            session_root / 'owner-contact-status' / f'{name}-prior-sent' / 'contact-status.json',
            contact_status='SENT_AWAITING_REPLY',
            sent_date=prior_sent.isoformat(),
            response_due_date=prior_due.isoformat(),
            status_date=prior_sent.isoformat(),
            attempt_count=1,
        )
        reask_dir = session_root / 'owner-reask-logs' / f'{name}-reask-source'
        reask = build_reask_log(
            output_dir=reask_dir,
            source_artifact=prior_sent_status,
            sent_date=sent_date,
            response_due_date=response_due_date,
            service_label='AIEDU-SR-003 draft reminder pilot',
            owner_role='accountable service owner route',
            source_record_set='owner-maintained local service record set',
            date_range='2026-06-01 through 2026-06-07',
            reask_channel_class='email',
            owner_route_class='same-accountable-owner-route',
            operator_confirmation=REASK_LOG_CONFIRMATION,
            overwrite=True,
        )
        if not reask.get('ok'):
            fail(f'{name} reask-log fixture did not build for contact source: {reask}')
        source = reask_dir / 'reask-log.json'
        status_key = 'reask-awaiting-reply'
    else:
        return write_dummy_contact_source(
            path,
            contact_status=contact_status,
            sent_date=sent_date,
            response_due_date=response_due_date,
            status_date=status_date,
            attempt_count=attempt_count,
        )

    status_dir = path.parent
    result = build_status(
        output_dir=status_dir,
        status=status_key,
        service_label='AIEDU-SR-003 draft reminder pilot',
        owner_role='accountable service owner route',
        source_record_set='owner-maintained local service record set',
        date_range='2026-06-01 through 2026-06-07',
        sent_date=sent_date,
        response_due_date=response_due_date,
        status_date=status_date,
        attempt_count=attempt_count,
        operator_confirmation=OPERATOR_CONFIRMATIONS[status_key],
        source_artifact=rel(source),
        overwrite=True,
    )
    if not result.get('ok'):
        fail(f'{name} contact-source fixture did not build: {result}')
    status_path = status_dir / 'contact-status.json'
    status_data = json.loads(status_path.read_text(encoding='utf-8'))
    status_data['created_at_utc'] = f'{status_date}T00:00:00Z'
    status_path.write_text(json.dumps(status_data, indent=2) + '\n', encoding='utf-8')
    return status_path


def expect(decision: dict, outcome: str) -> dict:
    if not decision.get('ok'):
        fail(f'expected {outcome}, got blocked decision: {decision}')
    if decision.get('outcome') != outcome:
        fail(f'expected outcome {outcome}, got {decision.get("outcome")}: {decision}')
    if decision.get('evidence_effect') != 'not_evidence':
        fail('decision docket must be not_evidence')
    if decision.get('closure_effect') != 'does_not_close_ft0181':
        fail('decision docket must not close FT-0181')
    if 'not evidence' not in decision.get('claim_ceiling', '').lower():
        fail('claim ceiling must say not evidence')
    if decision.get('decision_version') != EXPECTED_REVISION:
        fail(f'field-next decision_version should match current revision {EXPECTED_REVISION}: {decision.get("decision_version")}')
    return decision




def command_vars(command: str) -> dict[str, str]:
    return dict(token.split('=', 1) for token in shlex.split(command) if '=' in token)


def expect_valid_after_human_send_command(command: str, expected_packet: Path) -> None:
    values = command_vars(command)
    required = ['PACKET', 'SENT_DATE', 'RESPONSE_DUE_DATE', 'CONFIRM', 'OUT']
    missing = [key for key in required if key not in values]
    if missing:
        fail('owner-after-human-send command missing fields: ' + ', '.join(missing))
    if values['PACKET'] != rel(expected_packet):
        fail(f'owner-after-human-send command should point at selected packet manifest, got {values["PACKET"]}')
    if values['CONFIRM'] != SEND_LOG_CONFIRMATION:
        fail('owner-after-human-send command must carry the human-send confirmation token')
    if 'YYYY-MM-DD' in command:
        fail('owner-after-human-send command must not emit date placeholders')
    if not command.startswith('make owner-after-human-send '):
        fail('packet-only decision should route to the guarded owner-after-human-send helper')
    if not values['OUT'].startswith('scratch/field/ft0181/owner-after-human-send/aiedu-sr-003-sent-'):
        fail('owner-after-human-send command should use a date-keyed scratch session output')



def expect_valid_reask_log_command(command: str, expected_source: Path) -> None:
    values = command_vars(command)
    required = ['SOURCE_ARTIFACT', 'SENT_DATE', 'RESPONSE_DUE_DATE', 'CONFIRM', 'OUT']
    missing = [key for key in required if key not in values]
    if missing:
        fail('owner-reask-log command missing fields: ' + ', '.join(missing))
    if values['SOURCE_ARTIFACT'] != rel(expected_source):
        fail(f'owner-reask-log command should point at selected source artifact, got {values["SOURCE_ARTIFACT"]}')
    if values['CONFIRM'] != REASK_LOG_CONFIRMATION:
        fail('owner-reask-log command must carry the reask-log confirmation token')
    if 'YYYY-MM-DD' in command:
        fail('owner-reask-log command must not emit date placeholders')
    if not values['OUT'].startswith('scratch/field/ft0181/owner-reask-logs/aiedu-sr-003-reask-'):
        fail('owner-reask-log command should use a date-keyed scratch owner-reask-logs output')


def expect_valid_contact_command(command: str, status: str) -> None:
    values = command_vars(command)
    required = ['STATUS', 'SENT_DATE', 'RESPONSE_DUE_DATE', 'STATUS_DATE', 'CONFIRM', 'SOURCE_ARTIFACT']
    missing = [key for key in required if key not in values]
    if missing:
        fail('owner-contact command missing fields: ' + ', '.join(missing))
    if values['STATUS'] != status:
        fail(f'owner-contact command status mismatch: expected {status}, got {values["STATUS"]}')
    ok, reason = validate_contact_clock(
        status=values['STATUS'],
        sent_date=values['SENT_DATE'],
        response_due_date=values['RESPONSE_DUE_DATE'],
        status_date=values['STATUS_DATE'],
        attempt_count=int(values.get('ATTEMPT_COUNT', '1')),
    )
    if not ok:
        fail(f'owner-contact command should pass clock validation: {reason}; command={command}')
    ok, reason = validate_operator_confirmation(
        status=values['STATUS'],
        operator_confirmation=values['CONFIRM'],
        source_artifact=values['SOURCE_ARTIFACT'],
    )
    if not ok:
        fail(f'owner-contact command should pass operator confirmation validation: {reason}; command={command}')

def write_dummy_csv(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as fh:
        writer = csv.writer(fh)
        writer.writerow(['row_id', 'required_owner_reply', 'owner_response', 'local_only_check', 'intake_note'])
        writer.writerow(['1', 'boundary', 'owner-attested aggregate boundary', 'no raw/protected data', ''])


assert_operator_date_defaults()

if TMP.exists():
    shutil.rmtree(TMP)
if FIELD_TMP.exists():
    shutil.rmtree(FIELD_TMP)
if SUPPORT_TMP.exists():
    shutil.rmtree(SUPPORT_TMP)
TMP.mkdir(parents=True, exist_ok=True)
FIELD_TMP.mkdir(parents=True, exist_ok=True)

# Empty scratch: prepare the first-contact packet.
decision = decide_and_write(
    scratch_root=TMP / 'empty-scratch',
    returned_csv=None,
    as_of_date='2026-06-13',
    output_dir=TMP / 'dockets' / 'empty',
)
expect(decision, 'PREPARE-FIRST-CONTACT-PACKET')
if 'owner-request-packet' not in decision.get('recommended_command', ''):
    fail('empty decision should route to owner-request-packet')
docket_path = TMP / 'dockets' / 'empty' / 'FIELD-NEXT-ACTION.md'
if not docket_path.exists():
    fail('decision markdown docket missing')
docket_text = docket_path.read_text(encoding='utf-8')
for required in ['## Observed local state', 'Artifact counts:', 'Latest artifact candidates:', 'Selected artifact:']:
    if required not in docket_text:
        fail(f'decision markdown docket missing compact session summary section: {required}')
if decision.get('scratch_selection_rule') != 'manifest-clock-first-file-mtime-tiebreaker-only':
    fail('field router decisions should document manifest-clock-first scratch selection')
summary = decision.get('field_session_summary', {})
if summary.get('selection_rule') != 'manifest-clock-first-file-mtime-tiebreaker-only' or summary.get('no_evidence_or_closure_effect') is not True:
    fail(f'field_session_summary should compactly preserve selection and non-evidence state: {summary}')
if 'scratch_firebreak_rule' not in decision or 'non-field' not in decision.get('scratch_firebreak_rule', ''):
    fail('field router should document the non-field scratch firebreak')

# Checker/lint scratch must not contaminate live field routing. Artifacts under
# check/smoke/test/fixture subtrees, and helper artifacts that point back to
# those subtrees, are not field state.
firebreak_scratch = TMP / 'firebreak-scratch'
check_contact = write_contact_source(
    firebreak_scratch / 'check-router-contamination' / 'owner-contact-status' / 'sent' / 'contact-status.json',
    contact_status='SENT_AWAITING_REPLY',
    sent_date='2026-06-13',
    response_due_date='2026-06-20',
    status_date='2026-06-13',
    attempt_count=1,
)
check_seed = firebreak_scratch / 'check-router-contamination' / 'owner-reply-workbench-seeds' / 'proceed' / 'workbench-seed.json'
check_seed.parent.mkdir(parents=True, exist_ok=True)
check_seed.write_text(json.dumps({'acceptance_state': 'NOT_ACCEPTED'}, indent=2) + '\n', encoding='utf-8')
contaminating_brief = firebreak_scratch / 'owner-workbench-review-briefs' / 'from-check' / 'review-brief.json'
contaminating_brief.parent.mkdir(parents=True, exist_ok=True)
contaminating_brief.write_text(json.dumps({
    'brief_type': 'FT-0181-workbench-review-brief',
    'brief_state': 'REVIEW_BRIEF_PREPARED_NOT_REVIEWED',
    'source_seed': {'reference': rel(check_seed)},
    'contact_fixture': rel(check_contact),
    'evidence_state': 'not_evidence',
    'closure_effect': 'does_not_close_ft0181',
}, indent=2) + '\n', encoding='utf-8')
firebreak_decision = decide_and_write(
    scratch_root=firebreak_scratch,
    returned_csv=None,
    as_of_date='2026-06-13',
    output_dir=TMP / 'dockets' / 'firebreak-scratch',
)
expect(firebreak_decision, 'PREPARE-FIRST-CONTACT-PACKET')
if any(firebreak_decision.get('observed_artifact_counts', {}).values()):
    fail(f'non-field checker scratch should be ignored by router counts: {firebreak_decision}')
if firebreak_decision.get('latest_artifact_candidates'):
    fail(f'non-field checker scratch should not create latest candidates: {firebreak_decision}')

# Field-shaped validation fixture lanes are allowed for validator harnesses but
# must never become live router/report state in a later operator session.
validation_firebreak_scratch = TMP / 'validation-fixture-firebreak-root'
write_contact_source(
    validation_firebreak_scratch / 'validation' / 'owner-contact-status' / 'sent' / 'contact-status.json',
    contact_status='SENT_AWAITING_REPLY',
    sent_date='2026-06-13',
    response_due_date='2026-06-20',
    status_date='2026-06-13',
    attempt_count=1,
)
built_validation_packet = build_packet(
    output_dir=validation_firebreak_scratch / 'field-next-action-validation' / 'owner-request-packets' / 'p1',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    return_date='2026-06-20',
)
if not built_validation_packet.get('ok'):
    fail(f'validation-lane packet fixture did not build: {built_validation_packet}')
validation_firebreak_decision = decide_and_write(
    scratch_root=validation_firebreak_scratch,
    returned_csv=None,
    as_of_date='2026-06-13',
    output_dir=TMP / 'dockets' / 'validation-firebreak-scratch',
)
expect(validation_firebreak_decision, 'PREPARE-FIRST-CONTACT-PACKET')
if any(validation_firebreak_decision.get('observed_artifact_counts', {}).values()):
    fail(f'field validation fixtures should be ignored by router counts: {validation_firebreak_decision}')
if validation_firebreak_decision.get('latest_artifact_candidates'):
    fail(f'field validation fixtures should not create latest candidates: {validation_firebreak_decision}')
if 'validation fixture lanes' not in validation_firebreak_decision.get('scratch_firebreak_rule', ''):
    fail('router firebreak rule should name field-lane validation fixture lanes')
validation_report_scan = scan_lane(validation_firebreak_scratch, date.fromisoformat('2026-06-13'))
if validation_report_scan.get('artifact_count_total') != 0:
    fail(f'field report scan should ignore validation fixture artifacts: {validation_report_scan}')
if validation_report_scan.get('ignored_validation_fixture_artifact_count', 0) < 2:
    fail(f'field report scan should count ignored validation fixture artifacts: {validation_report_scan}')

# Safe local field-work mode collapses only router -> packet prep -> router.
safe_scratch = TMP / 'safe-local-scratch'
safe_decision = run_safe_local_field_session(
    scratch_root=safe_scratch,
    returned_csv=None,
    as_of_date='2026-06-13',
    output_dir=TMP / 'dockets' / 'safe-local-field-work',
    packet_output_dir=safe_scratch / 'owner-request-packets' / 'first-contact',
    overwrite=False,
)
expect(safe_decision, 'RECORD-SEND-LOG-AFTER-HUMAN-SEND')
local = safe_decision.get('safe_local_execution', {})
if local.get('state') != 'prepared-first-contact-packet':
    fail(f'safe local session should prepare exactly the first-contact packet: {local}')
if local.get('no_evidence_or_closure_effect') is not True:
    fail('safe local session must preserve no-evidence/no-closure effect')
packet_manifest = safe_scratch / 'owner-request-packets' / 'first-contact' / 'packet-manifest.json'
if not packet_manifest.exists():
    fail('safe local session did not create a packet manifest under the selected scratch root')
if 'owner-after-human-send' not in safe_decision.get('recommended_command', ''):
    fail('safe local session should reroute after packet prep to the guarded after-human-send fork')
if 'owner-route-block' not in safe_decision.get('fallback_command_if_no_accountable_owner_route', ''):
    fail('safe local session should preserve the no-accountable-route fallback')
session_md = TMP / 'dockets' / 'safe-local-field-work' / 'SAFE-LOCAL-FIELD-SESSION.md'
if not session_md.exists() or 'human-owned' not in session_md.read_text(encoding='utf-8'):
    fail('safe local session should write a human-action boundary memo')

# Returned CSV path must tie to an active field contact clock before intake.
# The CSV itself is kept outside the archive so checker scratch cannot masquerade
# as a returned owner packet.
external_csv_dir = Path(tempfile.mkdtemp(prefix='ft0181-returned-csv-'))
returned_csv = external_csv_dir / 'returned owner.csv'
write_dummy_csv(returned_csv)
missing_clock = decide_and_write(
    scratch_root=TMP / 'empty-scratch',
    returned_csv=returned_csv,
    as_of_date='2026-06-13',
    output_dir=TMP / 'dockets' / 'returned-csv-missing-clock',
)
if missing_clock.get('ok') or missing_clock.get('outcome') != 'RETURNED-CSV-SOURCE-PROVENANCE-MISSING':
    fail(f'returned CSV without source provenance should block: {missing_clock}')

returned_scratch = TMP / 'returned-csv-source-scratch'
source_contact = write_contact_source(
    returned_scratch / 'owner-contact-status' / 'sent' / 'contact-status.json',
    contact_status='SENT_AWAITING_REPLY',
    sent_date='2026-06-13',
    response_due_date='2026-06-20',
    status_date='2026-06-13',
    attempt_count=1,
)
decision = decide_and_write(
    scratch_root=returned_scratch,
    returned_csv=returned_csv,
    as_of_date='2026-06-13',
    output_dir=TMP / 'dockets' / 'returned-csv',
)
expect(decision, 'RUN-RETURNED-REPLY-WORK')
command = decision.get('recommended_command', '')
if str(returned_csv) not in command:
    fail('returned CSV decision should cite the returned path')
if 'make owner-returned-reply-work CSV=' not in command:
    fail('returned CSV decision should route to returned-reply work through the Make target')
if 'SOURCE_CONTACT_STATUS=' not in command or rel(source_contact) not in command:
    fail('returned-reply work command must carry the active source contact-status gate')
if 'OUT=scratch/field/ft0181/owner-reply-intakes/aiedu-sr-003' in command:
    fail('returned-reply work command must use digest-keyed defaults, not the stale fixed aiedu-sr-003 directory')
if "CSV='/" not in command or 'returned owner.csv' not in command:
    fail('returned CSV command should shell-quote paths with spaces')

# Missing returned CSV is blocked rather than inventing a local import.
missing = decide_and_write(
    scratch_root=TMP / 'empty-scratch',
    returned_csv=TMP / 'missing.csv',
    as_of_date='2026-06-13',
    output_dir=TMP / 'dockets' / 'missing-csv',
)
if missing.get('ok') or missing.get('outcome') != 'RETURNED-CSV-MISSING':
    fail('missing returned CSV should block')

# Archive-controlled fixtures/examples must not be routed as plausible returned field CSVs.
fixture_csv = ROOT / 'fixtures' / 'owner-reply-pipeline' / 'ft0181-proceed-staged-smoke.csv'
fixture_block = decide_and_write(
    scratch_root=TMP / 'empty-scratch',
    returned_csv=fixture_csv,
    as_of_date='2026-06-13',
    output_dir=TMP / 'dockets' / 'fixture-csv',
)
if fixture_block.get('ok') or fixture_block.get('outcome') != 'RETURNED-CSV-SOURCE-BLOCKED':
    fail('archive-controlled smoke fixture CSV should be blocked before intake routing')

# Validator scratch CSVs must not be accepted as plausible returned-owner inputs.
checker_scratch = ROOT / 'scratch' / 'checks' / 'ft0181-field-next-action-returned-csv-negative'
if checker_scratch.exists():
    shutil.rmtree(checker_scratch)
checker_scratch.mkdir(parents=True, exist_ok=True)
checker_csv = checker_scratch / 'non-field-returned-owner.csv'
write_dummy_csv(checker_csv)
checker_csv_block = decide_and_write(
    scratch_root=TMP / 'empty-scratch',
    returned_csv=checker_csv,
    as_of_date='2026-06-13',
    output_dir=TMP / 'dockets' / 'checker-csv',
)
if checker_csv_block.get('ok') or checker_csv_block.get('outcome') != 'RETURNED-CSV-SOURCE-BLOCKED':
    fail(f'checker scratch returned CSV should be blocked before intake routing: {checker_csv_block}')
if 'archive-nonfield-scratch-returned-csv' not in checker_csv_block.get('error', ''):
    fail(f'checker scratch CSV block should name the non-field scratch boundary: {checker_csv_block}')

# Even if copied into scratch, smoke/fixture markers are blocked before becoming the next action.
local_smoke = external_csv_dir / 'local smoke.csv'
local_smoke.write_text(fixture_csv.read_text(encoding='utf-8'), encoding='utf-8')
smoke_block = decide_and_write(
    scratch_root=TMP / 'empty-scratch',
    returned_csv=local_smoke,
    as_of_date='2026-06-13',
    output_dir=TMP / 'dockets' / 'local-smoke-csv',
)
if smoke_block.get('ok') or smoke_block.get('outcome') != 'RETURNED-CSV-SMOKE-BLOCKED':
    fail('local smoke-marker CSV should be blocked before intake routing')

# Prepared packet but no contact clock: record sent after human send/adaptation.
scratch = TMP / 'packet-scratch'
built = build_packet(
    output_dir=scratch / 'owner-request-packets' / 'p1',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    return_date='2026-06-20',
)
if not built.get('ok'):
    fail(f'packet fixture did not build: {built}')
packet_manifest = scratch / 'owner-request-packets' / 'p1' / 'packet-manifest.json'
decision = decide_and_write(
    scratch_root=scratch,
    returned_csv=None,
    as_of_date='2026-06-13',
    output_dir=TMP / 'dockets' / 'packet-only',
)
expect(decision, 'RECORD-SEND-LOG-AFTER-HUMAN-SEND')
command = decision.get('recommended_command', '')
if 'make owner-after-human-send' not in command:
    fail('packet-only decision should record the guarded after-human-send local state after a real human send')
if 'SENT_DATE=2026-06-13' not in command or 'RESPONSE_DUE_DATE=2026-06-20' not in command:
    fail('packet-only decision should produce a runnable after-human-send command for the decision date and packet return date')
if 'SOURCE_ARTIFACT=' in command or 'STATUS=sent-awaiting-reply' in command:
    fail('packet-only decision must not source a sent contact clock directly from the prepared packet')
expect_valid_after_human_send_command(command, packet_manifest)
candidates = decision.get('latest_artifact_candidates', {})
if 'packet' not in candidates or candidates['packet'].get('path') != rel(packet_manifest):
    fail(f'packet-only decision should include latest artifact candidate context, got {candidates}')

# After a real human send/adaptation, the guarded helper records both the send log and SENT clock.
after_send_scratch = TMP / 'after-human-send-scratch'
after_packet = build_packet(
    output_dir=after_send_scratch / 'owner-request-packets' / 'p1',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    return_date='2026-06-20',
)
if not after_packet.get('ok'):
    fail(f'after-human-send packet fixture did not build: {after_packet}')
after_packet_manifest = after_send_scratch / 'owner-request-packets' / 'p1' / 'packet-manifest.json'
after_send = build_after_human_send(
    packet_manifest=after_packet_manifest,
    sent_date='2026-06-13',
    response_due_date='2026-06-20',
    status_date='2026-06-13',
    output_dir=after_send_scratch / 'owner-after-human-send' / 'sent-session',
    send_log_dir=after_send_scratch / 'owner-send-logs' / 'sent-source',
    contact_status_dir=after_send_scratch / 'owner-contact-status' / 'sent',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    send_channel_class='email',
    owner_route_class='accountable-owner',
    operator_confirmation=SEND_LOG_CONFIRMATION,
)
if not after_send.get('ok'):
    fail(f'after-human-send helper should record send log and sent clock: {after_send}')
for expected in ['send_log_manifest', 'contact_status_manifest', 'session_manifest']:
    if not Path(after_send[expected]).exists():
        fail(f'after-human-send helper missing {expected}: {after_send}')
decision = decide_and_write(
    scratch_root=after_send_scratch,
    returned_csv=None,
    as_of_date='2026-06-14',
    output_dir=TMP / 'dockets' / 'after-human-send-open-clock',
)
expect(decision, 'AWAIT-OWNER-REPLY')
if decision.get('source_artifact') != rel(Path(after_send['contact_status_manifest'])):
    fail(f'after-human-send should leave the sent contact clock as router source, got {decision.get("source_artifact")}')

# Packet selection must use created_at_utc, not requested_return_date; otherwise an older
# packet with a farther due date can suppress a newer regenerated packet.
packet_clock_scratch = TMP / 'packet-created-clock-scratch'
older_packet = build_packet(
    output_dir=packet_clock_scratch / 'owner-request-packets' / 'old-long-return',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    return_date='2026-07-10',
)
newer_packet = build_packet(
    output_dir=packet_clock_scratch / 'owner-request-packets' / 'new-short-return',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    return_date='2026-06-20',
)
if not older_packet.get('ok') or not newer_packet.get('ok'):
    fail(f'packet created-clock fixtures did not build: old={older_packet}, new={newer_packet}')
old_manifest = packet_clock_scratch / 'owner-request-packets' / 'old-long-return' / 'packet-manifest.json'
old_data = json.loads(old_manifest.read_text(encoding='utf-8'))
old_data['created_at_utc'] = '2026-06-01T00:00:00Z'
old_manifest.write_text(json.dumps(old_data, indent=2) + '\n', encoding='utf-8')
new_manifest = packet_clock_scratch / 'owner-request-packets' / 'new-short-return' / 'packet-manifest.json'
new_data = json.loads(new_manifest.read_text(encoding='utf-8'))
new_data['created_at_utc'] = '2026-06-13T00:00:00Z'
new_manifest.write_text(json.dumps(new_data, indent=2) + '\n', encoding='utf-8')
decision = decide_and_write(
    scratch_root=packet_clock_scratch,
    returned_csv=None,
    as_of_date='2026-06-13',
    output_dir=TMP / 'dockets' / 'packet-created-clock',
)
expect(decision, 'RECORD-SEND-LOG-AFTER-HUMAN-SEND')
selected = decision.get('selected_artifact', {})
if 'new-short-return' not in selected.get('path', ''):
    fail(f'packet selection should prefer created_at_utc over requested_return_date, selected={selected}')
if 'RESPONSE_DUE_DATE=2026-06-20' not in decision.get('recommended_command', ''):
    fail('router should use the newer packet requested_return_date after created_at_utc selection')
expect_valid_after_human_send_command(decision.get('recommended_command', ''), new_manifest)

# A locally edited packet manifest must not drive a send-log/sent clock or imply evidence/closure.
malformed_packet_scratch = TMP / 'malformed-packet-scratch'
malformed_packet_dir = malformed_packet_scratch / 'owner-request-packets' / 'locally-edited-sent'
malformed_packet_dir.mkdir(parents=True, exist_ok=True)
(malformed_packet_dir / 'packet-manifest.json').write_text(json.dumps({
    'packet_id': 'AIEDU-SR-003-OWNER-REQUEST',
    'followthrough_id': 'FT-0181',
    'packet_state': 'SENT_BY_HAND',
    'evidence_state': 'SRC2',
    'source_truth_class': 'SRC2',
    'closure_effect': 'closes_ft0181',
    'public_claim_effect': 'supports_claims',
    'requested_return_date': '2026-06-20',
    'generated_files': ['AIEDU-SR-003-eight-row-owner-reply-template.csv'],
}, indent=2) + '\n', encoding='utf-8')
decision = decide_and_write(
    scratch_root=malformed_packet_scratch,
    returned_csv=None,
    as_of_date='2026-06-13',
    output_dir=TMP / 'dockets' / 'malformed-packet',
)
expect(decision, 'OWNER-REQUEST-PACKET-INTEGRITY-BLOCKED')
if 'no field command' not in decision.get('recommended_command', '') or 'SENT_BY_HAND' not in decision.get('reason', ''):
    fail('locally edited packet manifest should block routing without emitting a send-log or sent command')

# A stale prepared packet return date is refreshed rather than producing an impossible sent/due clock.
decision = decide_and_write(
    scratch_root=scratch,
    returned_csv=None,
    as_of_date='2026-06-25',
    output_dir=TMP / 'dockets' / 'stale-packet',
)
expect(decision, 'RECORD-SEND-LOG-AFTER-HUMAN-SEND')
command = decision.get('recommended_command', '')
if 'SENT_DATE=2026-06-25' not in command or 'RESPONSE_DUE_DATE=2026-07-02' not in command:
    fail('stale packet return date should refresh to a valid seven-day send-log clock')
if 'OUT=scratch/field/ft0181/owner-after-human-send/aiedu-sr-003-sent-2026-06-25' not in command:
    fail('stale packet after-human-send command should use a date-keyed session output directory')
expect_valid_after_human_send_command(command, packet_manifest)

# A send-log exists: record SENT_AWAITING_REPLY from the send-log, not from the packet manifest.
send_log = build_send_log(
    output_dir=scratch / 'owner-send-logs' / 'sent-source',
    packet_manifest=packet_manifest,
    sent_date='2026-06-13',
    response_due_date='2026-06-20',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    send_channel_class='email',
    owner_route_class='accountable-owner',
    operator_confirmation=SEND_LOG_CONFIRMATION,
)
if not send_log.get('ok'):
    fail(f'send-log fixture did not build: {send_log}')
send_log_manifest = scratch / 'owner-send-logs' / 'sent-source' / 'send-log.json'
decision = decide_and_write(
    scratch_root=scratch,
    returned_csv=None,
    as_of_date='2026-06-13',
    output_dir=TMP / 'dockets' / 'send-log-only',
)
expect(decision, 'RECORD-SENT-FROM-SEND-LOG')
command = decision.get('recommended_command', '')
if 'STATUS=sent-awaiting-reply' not in command or 'SOURCE_ARTIFACT=' not in command:
    fail('send-log decision should emit a sent contact-clock command with a source artifact')
if rel(send_log_manifest) not in command:
    fail('send-log decision should source the sent clock from send-log.json')
if rel(packet_manifest) in command:
    fail('send-log decision must not source the sent clock directly from packet-manifest.json')
expect_valid_contact_command(command, 'sent-awaiting-reply')

# First clock past due: send one bounded reask/follow-up.
time.sleep(0.02)
sent = build_status(
    output_dir=scratch / 'owner-contact-status' / 'sent',
    status='sent-awaiting-reply',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    sent_date='2026-06-13',
    response_due_date='2026-06-20',
    status_date='2026-06-13',
    attempt_count=1,
    **context_for('sent-awaiting-reply', send_log_manifest),
)
if not sent.get('ok'):
    fail(f'sent fixture did not build: {sent}')
decision = decide_and_write(
    scratch_root=scratch,
    returned_csv=None,
    as_of_date='2026-06-15',
    output_dir=TMP / 'dockets' / 'await-open-clock',
)
expect(decision, 'AWAIT-OWNER-REPLY')
command = decision.get('recommended_command', '')
if not command.startswith('make owner-field-next CSV=/path/to/returned-owner-reply.csv'):
    fail('open contact clock should route a returned CSV through owner-field-next, not direct intake')
if 'make owner-reply-intake CSV=' in command:
    fail('open contact clock must not bypass router-first source firebreak')

decision = decide_and_write(
    scratch_root=scratch,
    returned_csv=None,
    as_of_date='2026-06-21',
    output_dir=TMP / 'dockets' / 'past-first-clock',
)
expect(decision, 'RECORD-REASK-LOG-AFTER-FIRST-CLOCK')
command = decision.get('recommended_command', '')
if 'make owner-reask-log' not in command:
    fail('past first clock should record a reask-log before any reask contact clock')
if 'SENT_DATE=2026-06-21' not in command or 'RESPONSE_DUE_DATE=2026-06-24' not in command:
    fail('reask-log command should be runnable with a fresh three-day response clock')
if 'OUT=scratch/field/ft0181/owner-reask-logs/aiedu-sr-003-reask-2026-06-21' not in command:
    fail('reask-log command should use a date-keyed output directory')
if 'CONFIRM=human-sent-bounded-reask' not in command or 'SOURCE_ARTIFACT=' not in command:
    fail('reask-log command must carry explicit operator confirmation and source-artifact trace')
if 'STATUS=reask-awaiting-reply' in command or 'YYYY-MM-DD' in command:
    fail('past first clock must not create a reask contact clock directly or emit date placeholders')
expect_valid_reask_log_command(command, scratch / 'owner-contact-status' / 'sent' / 'contact-status.json')

# Reask clock past due: record no-owner-packet instead of widening the ask.
time.sleep(0.02)
reask_log = build_reask_log(
    output_dir=scratch / 'owner-reask-logs' / 'reask-source',
    source_artifact=scratch / 'owner-contact-status' / 'sent' / 'contact-status.json',
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
    fail(f'reask-log fixture did not build: {reask_log}')
reask_log_manifest = scratch / 'owner-reask-logs' / 'reask-source' / 'reask-log.json'
# The router now converts the reask log into the actual REASK_AWAITING_REPLY clock.
decision = decide_and_write(
    scratch_root=scratch,
    returned_csv=None,
    as_of_date='2026-06-21',
    output_dir=TMP / 'dockets' / 'reask-log-only',
)
expect(decision, 'RECORD-REASK-FROM-REASK-LOG')
command = decision.get('recommended_command', '')
if 'STATUS=reask-awaiting-reply' not in command or rel(reask_log_manifest) not in command:
    fail('reask-log decision should emit a reask contact-clock command sourced from reask-log.json')
expect_valid_contact_command(command, 'reask-awaiting-reply')

reask = build_status(
    output_dir=scratch / 'owner-contact-status' / 'reask',
    status='reask-awaiting-reply',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    sent_date='2026-06-21',
    response_due_date='2026-06-24',
    status_date='2026-06-21',
    attempt_count=2,
    **context_for('reask-awaiting-reply', reask_log_manifest),
)
if not reask.get('ok'):
    fail(f'reask fixture did not build: {reask}')
decision = decide_and_write(
    scratch_root=scratch,
    returned_csv=None,
    as_of_date='2026-06-25',
    output_dir=TMP / 'dockets' / 'past-reask-clock',
)
expect(decision, 'RECORD-NO-OWNER-PACKET')
command = decision.get('recommended_command', '')
if 'STATUS=no-owner-packet' not in command:
    fail('past reask clock should route to no-owner-packet')
if 'STATUS_DATE=2026-06-25' not in command:
    fail('no-owner-packet command should use the decision date as status date')
if 'OUT=scratch/field/ft0181/owner-contact-status/aiedu-sr-003-no-owner-packet-2026-06-25' not in command:
    fail('no-owner-packet command should use a date-keyed output directory')
if 'CONFIRM=bounded-clock-passed-no-viable-owner-packet' not in command or 'SOURCE_ARTIFACT=' not in command:
    fail('no-owner-packet command must carry explicit operator confirmation and source-artifact trace')
if 'YYYY-MM-DD' in command:
    fail('no-owner-packet decision must not emit date placeholders in the runnable command')
expect_valid_contact_command(command, 'no-owner-packet')

# Recorded no-owner-packet: no more field command; keep open/block without claims.
time.sleep(0.02)
no_packet = build_status(
    output_dir=scratch / 'owner-contact-status' / 'no-owner-packet',
    status='no-owner-packet',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    sent_date='2026-06-21',
    response_due_date='2026-06-24',
    status_date='2026-06-25',
    attempt_count=2,
    **context_for('no-owner-packet', scratch / 'owner-contact-status' / 'reask' / 'contact-status.json'),
)
if not no_packet.get('ok'):
    fail(f'no-owner-packet fixture did not build: {no_packet}')
decision = decide_and_write(
    scratch_root=scratch,
    returned_csv=None,
    as_of_date='2026-06-25',
    output_dir=TMP / 'dockets' / 'no-owner-recorded',
)
expect(decision, 'NO-OWNER-PACKET-RECORDED')
if 'no field command' not in decision.get('recommended_command', '').lower():
    fail('recorded no-owner-packet should not recommend more packet commands')

# A copied old SENT status with a newer filesystem mtime must not regress a recorded NO_OWNER_PACKET state.
time.sleep(0.02)
copied_stale_sent = build_status(
    output_dir=scratch / 'owner-contact-status' / 'copied-stale-sent',
    status='sent-awaiting-reply',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    sent_date='2026-06-13',
    response_due_date='2026-06-20',
    status_date='2026-06-13',
    attempt_count=1,
    **context_for('sent-awaiting-reply', send_log_manifest),
)
if not copied_stale_sent.get('ok'):
    fail(f'copied stale sent fixture did not build: {copied_stale_sent}')
# Simulate a copied historical SENT status: copying may refresh filesystem mtime,
# but the manifest clock must remain older than the terminal NO_OWNER_PACKET.
copied_stale_manifest = scratch / 'owner-contact-status' / 'copied-stale-sent' / 'contact-status.json'
copied_stale_data = json.loads(copied_stale_manifest.read_text(encoding='utf-8'))
copied_stale_data['created_at_utc'] = '2026-06-13T00:00:00Z'
copied_stale_manifest.write_text(json.dumps(copied_stale_data, indent=2) + '\n', encoding='utf-8')
decision = decide_and_write(
    scratch_root=scratch,
    returned_csv=None,
    as_of_date='2026-06-25',
    output_dir=TMP / 'dockets' / 'copied-stale-status',
)
expect(decision, 'NO-OWNER-PACKET-RECORDED')
selected = decision.get('selected_artifact', {})
if 'no-owner-packet' not in selected.get('path', ''):
    fail(f'manifest-clock selection should ignore newer-mtime copied stale status; selected={selected}')

# A newly generated SENT/REASK status in the same scratch root must not reopen a recorded NO_OWNER_PACKET state.
new_context_packet = build_packet(
    output_dir=scratch / 'owner-request-packets' / 'new-context',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    return_date='2026-07-03',
)
if not new_context_packet.get('ok'):
    fail(f'new context packet fixture did not build: {new_context_packet}')
post_terminal_send_log = build_send_log(
    output_dir=scratch / 'owner-send-logs' / 'post-terminal-send-log',
    packet_manifest=scratch / 'owner-request-packets' / 'new-context' / 'packet-manifest.json',
    sent_date='2026-06-26',
    response_due_date='2026-07-03',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    send_channel_class='email',
    owner_route_class='accountable-owner',
    operator_confirmation=SEND_LOG_CONFIRMATION,
)
if not post_terminal_send_log.get('ok'):
    fail(f'post-terminal send-log fixture did not build: {post_terminal_send_log}')
post_terminal_sent = build_status(
    output_dir=scratch / 'owner-contact-status' / 'post-terminal-sent-regression',
    status='sent-awaiting-reply',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    sent_date='2026-06-26',
    response_due_date='2026-07-03',
    status_date='2026-06-26',
    attempt_count=1,
    **context_for('sent-awaiting-reply', scratch / 'owner-send-logs' / 'post-terminal-send-log' / 'send-log.json'),
)
if not post_terminal_sent.get('ok'):
    fail(f'post-terminal sent fixture did not build: {post_terminal_sent}')
post_terminal_manifest = scratch / 'owner-contact-status' / 'post-terminal-sent-regression' / 'contact-status.json'
post_terminal_data = json.loads(post_terminal_manifest.read_text(encoding='utf-8'))
post_terminal_data['created_at_utc'] = '2026-06-26T00:00:00Z'
post_terminal_manifest.write_text(json.dumps(post_terminal_data, indent=2) + '\n', encoding='utf-8')
decision = decide_and_write(
    scratch_root=scratch,
    returned_csv=None,
    as_of_date='2026-06-26',
    output_dir=TMP / 'dockets' / 'terminal-regression',
)
expect(decision, 'CONTACT-STATUS-TERMINAL-REGRESSION-BLOCKED')
if 'no field command' not in decision.get('recommended_command', '') or 'NO_OWNER_PACKET status already exists' not in decision.get('reason', ''):
    fail('post-terminal contact status should block without reopening the field session')
selected = decision.get('selected_artifact', {})
if 'post-terminal-sent-regression' not in selected.get('path', ''):
    fail(f'terminal regression block should identify the later unsafe contact status, selected={selected}')

# A malformed newer contact status should block routing rather than be interpreted as await/reask/no-packet.
corrupt_contact_scratch = TMP / 'corrupt-contact-scratch'
corrupt_dir = corrupt_contact_scratch / 'owner-contact-status' / 'corrupt-latest'
corrupt_dir.mkdir(parents=True, exist_ok=True)
(corrupt_dir / 'contact-status.json').write_text(json.dumps({
    'contact_status': 'LOCALLY_ACCEPTED',
    'sent_date': '2026-06-13',
    'response_due_date': '2026-06-20',
    'status_date': '2026-06-13',
    'attempt_count': 2,
    'created_at_utc': '2026-06-25T00:00:00Z',
    'ft0181_status': 'closed',
}, indent=2) + '\n', encoding='utf-8')
decision = decide_and_write(
    scratch_root=corrupt_contact_scratch,
    returned_csv=None,
    as_of_date='2026-06-25',
    output_dir=TMP / 'dockets' / 'corrupt-contact',
)
expect(decision, 'CONTACT-STATUS-INTEGRITY-BLOCKED')
if 'no field command' not in decision.get('recommended_command', ''):
    fail('malformed contact status should not emit another field command')

# RE-ASK-ONCE intake routes to one dated clarification clock, not a prose shortcut.
reask_intake_scratch = TMP / 'reask-intake-scratch'
reask_intake_dir = reask_intake_scratch / 'owner-reply-intakes' / 'needs-clarification'
reask_intake_dir.mkdir(parents=True, exist_ok=True)
(reask_intake_dir / 'bundle-manifest.json').write_text(json.dumps({
    'bundle_type': 'FT-0181-owner-reply-local-intake-bundle',
    'triage_outcome': 'RE-ASK-ONCE',
    'ft0181_status': 'live',
    'created_at_utc': '2026-06-13T00:00:00Z',
}, indent=2) + '\n', encoding='utf-8')
decision = decide_and_write(
    scratch_root=reask_intake_scratch,
    returned_csv=None,
    as_of_date='2026-06-13',
    output_dir=TMP / 'dockets' / 'intake-reask',
)
expect(decision, 'RECORD-REASK-LOG-FROM-INTAKE')
command = decision.get('recommended_command', '')
if 'make owner-reask-log' not in command:
    fail('RE-ASK-ONCE intake should emit a runnable reask-log command, not a direct contact clock')
if 'SENT_DATE=2026-06-13' not in command or 'RESPONSE_DUE_DATE=2026-06-16' not in command:
    fail('RE-ASK-ONCE intake reask-log command should use a fresh three-day clock from the decision date')
if 'OUT=scratch/field/ft0181/owner-reask-logs/aiedu-sr-003-reask-2026-06-13' not in command:
    fail('RE-ASK-ONCE intake reask-log command should use a date-keyed output directory')
if 'CONFIRM=human-sent-bounded-reask' not in command or 'SOURCE_ARTIFACT=' not in command:
    fail('RE-ASK-ONCE intake reask-log command must carry explicit operator confirmation and source-artifact trace')
if 'STATUS=reask-awaiting-reply' in command or 'open scratch owner-reply intake outcome note' in command or 'YYYY-MM-DD' in command:
    fail('RE-ASK-ONCE intake must not create a direct contact clock, fall back to prose, or emit date placeholders')
expect_valid_reask_log_command(command, reask_intake_dir / 'bundle-manifest.json')

intake_reask_source = write_contact_source(
    reask_intake_scratch / 'owner-contact-status' / 'intake-reask-source' / 'contact-status.json',
    contact_status='REASK_AWAITING_REPLY',
    sent_date='2026-06-13',
    response_due_date='2026-06-16',
    status_date='2026-06-13',
    attempt_count=2,
)

# A newer contact clock must outrank an older RE-ASK-ONCE intake; otherwise the router can loop on re-asks.
newer_no_owner = build_status(
    output_dir=reask_intake_scratch / 'owner-contact-status' / 'no-owner-after-intake-reask',
    status='no-owner-packet',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    sent_date='2026-06-13',
    response_due_date='2026-06-16',
    status_date='2026-06-17',
    attempt_count=2,
    **context_for('no-owner-packet', intake_reask_source),
)
if not newer_no_owner.get('ok'):
    fail(f'newer no-owner status fixture did not build: {newer_no_owner}')
decision = decide_and_write(
    scratch_root=reask_intake_scratch,
    returned_csv=None,
    as_of_date='2026-06-17',
    output_dir=TMP / 'dockets' / 'intake-reask-then-no-owner',
)
expect(decision, 'NO-OWNER-PACKET-RECORDED')
selected = decision.get('selected_artifact', {})
if selected.get('kind') != 'contact_status' or 'no-owner-after-intake-reask' not in selected.get('path', ''):
    fail(f'newer contact status should outrank older RE-ASK-ONCE intake, selected={selected}')
if decision.get('latest_artifact_candidates', {}).get('intake_bundle') is None:
    fail('decision should preserve latest intake candidate context even when a newer contact status is selected')

# Intake bundle routes to workbench seed; later seed routes to a review brief; later brief routes to bounded workbench review; later review routes onward.
intake_scratch = FIELD_TMP / 'intake-scratch'
intake_dir = intake_scratch / 'owner-reply-intakes' / 'aiedu-sr-003'
intake_dir.mkdir(parents=True, exist_ok=True)
(intake_dir / 'bundle-manifest.json').write_text(json.dumps({
    'bundle_type': 'FT-0181-owner-reply-local-intake-bundle',
    'triage_outcome': 'PROCEED-STAGED',
    'ft0181_status': 'live',
}, indent=2) + '\n', encoding='utf-8')
decision = decide_and_write(
    scratch_root=intake_scratch,
    returned_csv=None,
    as_of_date='2026-06-13',
    output_dir=TMP / 'dockets' / 'intake-proceed',
)
expect(decision, 'SEED-WORKBENCH')
seed_command = decision.get('recommended_command', '')
if 'owner-reply-workbench-seed' not in seed_command:
    fail('proceed intake should route to workbench seed')
if 'OUT=scratch/field/ft0181/owner-reply-workbench-seeds/aiedu-sr-003' in seed_command:
    fail('workbench seed command must use digest-keyed default output, not the stale fixed aiedu-sr-003 directory')

time.sleep(0.02)
seed_source_contact = write_contact_source(
    intake_scratch / 'owner-contact-status' / 'seed-source' / 'contact-status.json',
    contact_status='SENT_AWAITING_REPLY',
    sent_date='2026-06-13',
    response_due_date='2026-06-20',
    status_date='2026-06-13',
    attempt_count=1,
)
source_packet = intake_scratch / 'returned-owner-source-packets' / 'real-owner-packet.csv'
source_packet.parent.mkdir(parents=True, exist_ok=True)
source_packet.write_text('field_key,owner_attested_class,decision_effect\nallowed_count,aggregate_owner_attested,changes_one_bounded_slice\n', encoding='utf-8')
seed_dir = intake_scratch / 'owner-reply-workbench-seeds' / 'aiedu-sr-003'
seed_dir.mkdir(parents=True, exist_ok=True)
(seed_dir / 'workbench-seed.json').write_text(json.dumps({
    'seed_type': 'FT-0181-owner-packet-workbench-seed',
    'seed_version': 'rev0275',
    'created_at_utc': '2026-06-13T00:00:01Z',
    'source_truth_status': 'UNVERIFIED_OWNER_REPLY_PENDING_CUSTODY',
    'acceptance_state': 'NOT_ACCEPTED',
    'required_next_surface': 'docs/30-operations/ft0181-owner-packet-workbench.md',
    'source_contact_status': {
        'reference': rel(seed_source_contact),
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
decision = decide_and_write(
    scratch_root=intake_scratch,
    returned_csv=None,
    as_of_date='2026-06-13',
    output_dir=TMP / 'dockets' / 'seeded',
)
expect(decision, 'PREPARE-WORKBENCH-REVIEW-BRIEF')
brief_command = decision.get('recommended_command', '')
if 'owner-workbench-review-brief' not in brief_command:
    fail('seeded decision should route to a bounded workbench review brief before human review')
if 'owner-workbench-review ' in brief_command:
    fail('seeded decision must not bypass the review brief and jump directly to owner-workbench-review')
if 'NOT_ACCEPTED' not in decision.get('reason', ''):
    fail('seeded decision must preserve NOT_ACCEPTED boundary')

build_review_brief(
    seed=seed_dir / 'workbench-seed.json',
    output_dir=intake_scratch / 'owner-workbench-review-briefs' / 'prepared',
    overwrite=True,
)
decision = decide_and_write(
    scratch_root=intake_scratch,
    returned_csv=None,
    as_of_date='2026-06-13',
    output_dir=TMP / 'dockets' / 'review-brief-prepared',
)
expect(decision, 'RECORD-WORKBENCH-REVIEW-NOT-ACCEPTED')
review_command = decision.get('recommended_command', '')
if 'owner-workbench-review' not in review_command or 'CONFIRM=human-reviewed-minimized-workbench-record' not in review_command:
    fail('review-brief decision must route to a bounded workbench-review record with confirmation token')
if 'SOURCE_TRUTH_CLASS=SRC2-CANDIDATE-NOT-ACCEPTED' not in review_command or 'SOURCE_TRUTH_CLASS=SRC2 ' in review_command:
    fail('review-brief router command must use the pre-acceptance SRC2 candidate class, not bare SRC2')
if 'not a human review' not in decision.get('reason', '').lower():
    fail('review-brief route must state that the brief is not the human review')

# A proceed-capable workbench review first routes to a safe local decision-brief bridge, still without acceptance.
build_review(
    seed=seed_dir / 'workbench-seed.json',
    decision='proceed-decision-board',
    source_truth_class='SRC2-CANDIDATE-NOT-ACCEPTED',
    review_basis='owner-attested-aggregate',
    surviving_field_count=2,
    decision_changed_count=1,
    local_only_field_count=0,
    trimmed_field_count=1,
    reask_field_count=0,
    reviewer_role_count=2,
    raw_learner_data_present=False,
    protected_facts_present=False,
    security_payloads_present=False,
    public_claim_upgrade_requested=False,
    operator_confirmation=WORKBENCH_REVIEW_CONFIRMATION,
    output_dir=intake_scratch / 'owner-workbench-reviews' / 'proceed',
)
review_path = intake_scratch / 'owner-workbench-reviews' / 'proceed' / 'workbench-review.json'
decision = decide_and_write(
    scratch_root=intake_scratch,
    returned_csv=None,
    as_of_date='2026-06-13',
    output_dir=TMP / 'dockets' / 'workbench-reviewed-proceed',
)
expect(decision, 'PREPARE-FIRST-PACKET-DECISION-BRIEF')
command = decision.get('recommended_command', '')
if 'owner-first-packet-decision-brief' not in command or rel(review_path) not in command:
    fail('proceed workbench review should route to first-packet decision brief prep')
if 'owner-first-packet-decision ' in command:
    fail('proceed workbench review must not bypass the decision brief and jump directly to owner-first-packet-decision')
if 'NOT_ACCEPTED' not in decision.get('reason', ''):
    fail('proceed workbench review route must preserve NOT_ACCEPTED boundary')

# Safe local field-work may prepare the decision brief, but still stops before board recording.
safe_decision_brief = run_safe_local_field_session(
    scratch_root=intake_scratch,
    returned_csv=None,
    as_of_date='2026-06-13',
    output_dir=TMP / 'dockets' / 'safe-local-decision-brief',
    packet_output_dir=None,
    overwrite=False,
)
expect(safe_decision_brief, 'RECORD-FIRST-PACKET-DECISION-NOT-ACCEPTED')
local = safe_decision_brief.get('safe_local_execution', {})
if local.get('state') != 'prepared-first-packet-decision-brief':
    fail(f'safe local field work should prepare the decision brief and stop before board recording: {local}')
if local.get('no_evidence_or_closure_effect') is not True:
    fail('safe local decision-brief prep must preserve no-evidence/no-closure effect')
if 'owner-first-packet-decision ' not in safe_decision_brief.get('recommended_command', ''):
    fail('after decision-brief prep the router should expose the human board record command')

build_decision_brief(
    review=review_path,
    output_dir=intake_scratch / 'owner-first-packet-decision-briefs' / 'prepared',
    overwrite=True,
)
decision = decide_and_write(
    scratch_root=intake_scratch,
    returned_csv=None,
    as_of_date='2026-06-13',
    output_dir=TMP / 'dockets' / 'decision-brief-prepared',
)
expect(decision, 'RECORD-FIRST-PACKET-DECISION-NOT-ACCEPTED')
command = decision.get('recommended_command', '')
if 'owner-first-packet-decision' not in command or 'CONFIRM=human-recorded-five-slice-decision-board' not in command:
    fail('decision-brief route should expose a bounded first-packet decision command with confirmation token')
if 'not a board decision' not in decision.get('reason', '').lower():
    fail('decision-brief route must state that the brief is not the board decision')

build_decision(
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
    operator_confirmation=FIRST_PACKET_DECISION_CONFIRMATION,
    output_dir=intake_scratch / 'owner-first-packet-decisions' / 'valid',
)
first_decision_path = intake_scratch / 'owner-first-packet-decisions' / 'valid' / 'first-packet-decision.json'
decision = decide_and_write(
    scratch_root=intake_scratch,
    returned_csv=None,
    as_of_date='2026-06-13',
    output_dir=TMP / 'dockets' / 'first-packet-decision',
)
expect(decision, 'PREPARE-POST-DECISION-CHANGE-TICKET-BRIEF')
command = decision.get('recommended_command', '')
if 'owner-post-decision-change-ticket-brief' not in command or rel(first_decision_path) not in command:
    fail('first-packet decision should route to activation/live-window entry brief prep')
if 'owner-post-decision-change-ticket ' in command:
    fail('first-packet decision must not bypass the change-ticket brief and jump directly to ticket recording')
if 'NOT_ACCEPTED' not in decision.get('reason', ''):
    fail('first-packet decision route must preserve NOT_ACCEPTED boundary')

# Safe local field-work may prepare the change-ticket brief, but still stops before ticket recording.
safe_change_ticket_brief = run_safe_local_field_session(
    scratch_root=intake_scratch,
    returned_csv=None,
    as_of_date='2026-06-13',
    output_dir=TMP / 'dockets' / 'safe-local-change-ticket-brief',
    packet_output_dir=None,
    overwrite=False,
)
expect(safe_change_ticket_brief, 'RECORD-POST-DECISION-CHANGE-TICKET-NOT-ACCEPTED')
local = safe_change_ticket_brief.get('safe_local_execution', {})
if local.get('state') != 'prepared-post-decision-change-ticket-brief':
    fail(f'safe local field work should prepare the change-ticket brief and stop before ticket recording: {local}')
if local.get('no_evidence_or_closure_effect') is not True:
    fail('safe local change-ticket-brief prep must preserve no-evidence/no-closure effect')
change_ticket_command = safe_change_ticket_brief.get('recommended_command', '')
if 'owner-post-decision-change-ticket ' not in change_ticket_command or 'CONFIRM=human-recorded-bounded-post-decision-change-ticket' not in change_ticket_command:
    fail('after change-ticket-brief prep the router should expose the human post-decision ticket record command')
if 'ACTIVATION_RECEIPT=' in change_ticket_command:
    fail('default post-decision ticket route must not jump to active-change with activation receipt')

build_change_ticket_brief(
    decision=first_decision_path,
    output_dir=intake_scratch / 'owner-post-decision-change-ticket-briefs' / 'prepared',
    overwrite=True,
)
decision = decide_and_write(
    scratch_root=intake_scratch,
    returned_csv=None,
    as_of_date='2026-06-13',
    output_dir=TMP / 'dockets' / 'change-ticket-brief-prepared',
)
expect(decision, 'RECORD-POST-DECISION-CHANGE-TICKET-NOT-ACCEPTED')
command = decision.get('recommended_command', '')
if 'owner-post-decision-change-ticket ' not in command or 'CONFIRM=human-recorded-bounded-post-decision-change-ticket' not in command:
    fail('change-ticket brief route should expose a bounded post-decision ticket command with confirmation token')
if 'not a change ticket' not in decision.get('reason', '').lower():
    fail('change-ticket brief route must state that the brief is not the change ticket')

build_change_ticket(
    decision=intake_scratch / 'owner-first-packet-decisions' / 'valid' / 'first-packet-decision.json',
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
    operator_confirmation=POST_DECISION_TICKET_CONFIRMATION,
    output_dir=intake_scratch / 'owner-post-decision-change-tickets' / 'valid',
)
decision = decide_and_write(
    scratch_root=intake_scratch,
    returned_csv=None,
    as_of_date='2026-06-13',
    output_dir=TMP / 'dockets' / 'post-decision-change-ticket',
)
expect(decision, 'PREPARE-ACTIVATION-LIVE-WINDOW-BRIEF')
command = decision.get('recommended_command', '')
if 'owner-activation-live-window-brief' not in command or rel(intake_scratch / 'owner-post-decision-change-tickets' / 'valid' / 'post-decision-change-ticket.json') not in command:
    fail('ready_for_real_packet ticket should route to the activation/live-window entry brief')
if 'owner-live-window-card' in command or 'owner-activation-receipt' in command:
    fail('ready_for_real_packet ticket must not emit activation receipt or live-window card commands before the entry brief')
if 'same real owner-reviewed source packet' not in decision.get('reason', '') or 'live-window card' not in decision.get('reason', ''):
    fail('ready_for_real_packet brief route must name the source-packet/live-window laundering risk')

safe_activation_brief = run_safe_local_field_session(
    scratch_root=intake_scratch,
    returned_csv=None,
    as_of_date='2026-06-13',
    output_dir=TMP / 'dockets' / 'safe-local-activation-brief-ready',
    packet_output_dir=None,
    overwrite=False,
)
expect(safe_activation_brief, 'RECORD-ACTIVATION-RECEIPT-FROM-REAL-PACKET-NOT-ACCEPTANCE')
local = safe_activation_brief.get('safe_local_execution', {})
if local.get('state') != 'prepared-activation-live-window-brief':
    fail(f'safe local field work should prepare the activation/live-window brief and stop before receipt/card recording: {local}')
if local.get('no_evidence_or_closure_effect') is not True:
    fail('safe local activation/live-window brief prep must preserve no-evidence/no-closure effect')
ready_command = safe_activation_brief.get('recommended_command', '')
if 'owner-activation-receipt' not in ready_command or 'SOURCE_PACKET=/path/to/same-returned-owner-csv-that-seeded-this-decision.csv' not in ready_command:
    fail('after ready activation/live-window brief prep the router should expose the same-source activation receipt command')
if 'owner-live-window-card' in ready_command:
    fail('ready activation/live-window brief route must still not expose a live-window-card command')

source_packet.write_text('field_key,owner_attested_class,decision_effect\nallowed_count,aggregate_owner_attested,changes_one_bounded_slice\n', encoding='utf-8')
build_activation_receipt(
    decision=intake_scratch / 'owner-first-packet-decisions' / 'valid' / 'first-packet-decision.json',
    source_packet=source_packet,
    source_truth_class='SRC2',
    accepted_field_count=1,
    reviewer_role_count=2,
    dictionary_or_map_ref_count=1,
    blocked_or_trimmed_field_count=1,
    operator_confirmation=ACTIVATION_RECEIPT_CONFIRMATION,
    output_dir=intake_scratch / 'owner-activation-receipts' / 'accepted',
)
receipt_decision = decide_and_write(
    scratch_root=intake_scratch,
    returned_csv=None,
    as_of_date='2026-06-13',
    output_dir=TMP / 'dockets' / 'activation-receipt',
)
expect(receipt_decision, 'RECORD-ACTIVE-CHANGE-TICKET-FROM-ACTIVATION-RECEIPT')
receipt_command = receipt_decision.get('recommended_command', '')
if 'owner-post-decision-change-ticket' not in receipt_command or 'ACTIVATION_RECEIPT=' not in receipt_command or 'TICKET_STATE=active-change' not in receipt_command:
    fail('activation receipt should route to an active_change ticket command with ACTIVATION_RECEIPT')

build_change_ticket(
    decision=intake_scratch / 'owner-first-packet-decisions' / 'valid' / 'first-packet-decision.json',
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
    operator_confirmation=POST_DECISION_TICKET_CONFIRMATION,
    activation_receipt=intake_scratch / 'owner-activation-receipts' / 'accepted' / 'activation-receipt.json',
    output_dir=intake_scratch / 'owner-post-decision-change-tickets' / 'active',
)
active_decision = decide_and_write(
    scratch_root=intake_scratch,
    returned_csv=None,
    as_of_date='2026-06-13',
    output_dir=TMP / 'dockets' / 'post-decision-active-ticket',
)
expect(active_decision, 'PREPARE-ACTIVATION-LIVE-WINDOW-BRIEF')
active_command = active_decision.get('recommended_command', '')
active_ticket_path = intake_scratch / 'owner-post-decision-change-tickets' / 'active' / 'post-decision-change-ticket.json'
if 'owner-activation-live-window-brief' not in active_command or rel(active_ticket_path) not in active_command:
    fail('active_change ticket should route to the activation/live-window entry brief before live-window card recording')
if 'owner-live-window-card' in active_command:
    fail('active_change ticket must not bypass the entry brief and jump directly to a live-window card')

build_activation_live_window_brief(
    ticket=active_ticket_path,
    output_dir=intake_scratch / 'owner-activation-live-window-briefs' / 'active',
    overwrite=True,
)
active_decision = decide_and_write(
    scratch_root=intake_scratch,
    returned_csv=None,
    as_of_date='2026-06-13',
    output_dir=TMP / 'dockets' / 'active-activation-live-window-brief',
)
expect(active_decision, 'RECORD-LIVE-WINDOW-CARD-FROM-ACTIVE-CHANGE-BRIEF')
active_command = active_decision.get('recommended_command', '')
if 'owner-live-window-card' not in active_command or 'CONFIRM=human-recorded-bounded-live-window-card' not in active_command:
    fail('active_change brief should route to a bounded live-window card record with confirmation token')

build_live_window_card(
    ticket=intake_scratch / 'owner-post-decision-change-tickets' / 'active' / 'post-decision-change-ticket.json',
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
    output_dir=intake_scratch / 'owner-live-window-cards' / 'staged',
)
staged_decision = decide_and_write(
    scratch_root=intake_scratch,
    returned_csv=None,
    as_of_date='2026-06-18',
    output_dir=TMP / 'dockets' / 'live-window-card-staged',
)
expect(staged_decision, 'PREPARE-LIVE-WINDOW-TERMINAL-STATE-BRIEF')
if 'owner-live-window-terminal-brief' not in staged_decision.get('recommended_command', ''):
    fail('nonterminal live-window card should route to terminal-state brief prep')
if 'closure' not in staged_decision.get('reason', '').lower() or 'readout' not in staged_decision.get('reason', '').lower():
    fail('nonterminal live-window card route must keep readout and closure boundaries visible')

safe_terminal_brief = run_safe_local_field_session(
    scratch_root=intake_scratch,
    returned_csv=None,
    as_of_date='2026-06-18',
    output_dir=TMP / 'dockets' / 'safe-local-live-window-terminal-brief',
    packet_output_dir=None,
    overwrite=False,
)
expect(safe_terminal_brief, 'RECORD-LIVE-WINDOW-TERMINAL-CARD-NOT-READOUT')
local = safe_terminal_brief.get('safe_local_execution', {})
if local.get('state') != 'prepared-live-window-terminal-brief':
    fail(f'safe local field work should prepare the terminal-state brief and stop before terminal card recording: {local}')
terminal_command = safe_terminal_brief.get('recommended_command', '')
if 'owner-live-window-card' not in terminal_command or 'WINDOW_STATE=completed-no-closure' not in terminal_command:
    fail('after terminal brief prep the router should expose a bounded terminal live-window-card command')
if 'owner-live-window-readout' in terminal_command:
    fail('terminal brief route must not jump directly to readout')

time.sleep(0.02)
build_live_window_card(
    ticket=intake_scratch / 'owner-post-decision-change-tickets' / 'active' / 'post-decision-change-ticket.json',
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
    output_dir=intake_scratch / 'owner-live-window-cards' / 'completed',
)
decision = decide_and_write(
    scratch_root=intake_scratch,
    returned_csv=None,
    as_of_date='2026-06-18',
    output_dir=TMP / 'dockets' / 'live-window-card-completed',
)
expect(decision, 'PREPARE-LIVE-WINDOW-READOUT-BRIEF')
if 'owner-live-window-readout-brief' not in decision.get('recommended_command', ''):
    fail('terminal live-window card should route to readout brief prep before bounded readout recording')
if 'closure' not in decision.get('reason', '').lower() or 'post-readout' not in decision.get('reason', '').lower():
    fail('terminal live-window card route must keep post-readout and closure boundaries visible')

safe_readout_brief = run_safe_local_field_session(
    scratch_root=intake_scratch,
    returned_csv=None,
    as_of_date='2026-06-18',
    output_dir=TMP / 'dockets' / 'safe-local-live-window-readout-brief',
    packet_output_dir=None,
    overwrite=False,
)
expect(safe_readout_brief, 'RECORD-LIVE-WINDOW-READOUT-FROM-BRIEF-NOT-CLOSURE')
local = safe_readout_brief.get('safe_local_execution', {})
if local.get('state') != 'prepared-live-window-readout-brief':
    fail(f'safe local field work should prepare the readout brief and stop before aggregate readout recording: {local}')
readout_command = safe_readout_brief.get('recommended_command', '')
if 'owner-live-window-readout' not in readout_command or 'CONFIRM=human-recorded-aggregate-readout-no-closure' not in readout_command:
    fail('after readout brief prep the router should expose a bounded aggregate readout command')
if 'owner-post-readout-action' in readout_command:
    fail('readout brief route must not jump directly to post-readout action')

build_readout_brief(
    card=intake_scratch / 'owner-live-window-cards' / 'completed' / 'live-window-card.json',
    output_dir=intake_scratch / 'owner-live-window-readout-briefs' / 'completed',
    overwrite=True,
)
brief_decision = decide_and_write(
    scratch_root=intake_scratch,
    returned_csv=None,
    as_of_date='2026-06-18',
    output_dir=TMP / 'dockets' / 'live-window-readout-brief-completed',
)
expect(brief_decision, 'RECORD-LIVE-WINDOW-READOUT-FROM-BRIEF-NOT-CLOSURE')
if 'owner-live-window-readout' not in brief_decision.get('recommended_command', '') or 'CONFIRM=human-recorded-aggregate-readout-no-closure' not in brief_decision.get('recommended_command', ''):
    fail('readout brief should route to bounded live-window readout record with confirmation token')
build_live_window_readout(
    card=intake_scratch / 'owner-live-window-cards' / 'completed' / 'live-window-card.json',
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
    operator_confirmation=LIVE_WINDOW_READOUT_CONFIRMATION,
    output_dir=intake_scratch / 'owner-live-window-readouts' / 'completed',
)
readout_decision = decide_and_write(
    scratch_root=intake_scratch,
    returned_csv=None,
    as_of_date='2026-06-18',
    output_dir=TMP / 'dockets' / 'live-window-readout-completed',
)
expect(readout_decision, 'PREPARE-POST-READOUT-ACTION-BRIEF')
readout_command = readout_decision.get('recommended_command', '')
if 'owner-post-readout-action-brief' not in readout_command:
    fail('live-window readout should route to post-readout action brief before dispatch recording')
if 'owner-post-readout-action ' in readout_command or 'CONFIRM=human-recorded-post-readout-action-no-closure' in readout_command:
    fail('live-window readout route must not jump directly to post-readout dispatch')

safe_action_brief = run_safe_local_field_session(
    scratch_root=intake_scratch,
    returned_csv=None,
    as_of_date='2026-06-18',
    output_dir=TMP / 'dockets' / 'safe-local-post-readout-action-brief',
    packet_output_dir=None,
    overwrite=False,
)
expect(safe_action_brief, 'RECORD-POST-READOUT-ACTION-FROM-BRIEF-NOT-CLOSURE')
local = safe_action_brief.get('safe_local_execution', {})
if local.get('state') != 'prepared-post-readout-action-brief':
    fail(f'safe local field work should prepare the post-readout action brief and stop before dispatch recording: {local}')
action_command = safe_action_brief.get('recommended_command', '')
if 'owner-post-readout-action' not in action_command or 'CONFIRM=human-recorded-post-readout-action-no-closure' not in action_command:
    fail('after action brief prep the router should expose a bounded post-readout action command')
if 'owner-post-readout-recheck' in action_command or 'owner-post-readout-context-receipt' in action_command:
    fail('post-readout action brief route must not jump directly to recheck or context receipt')

build_post_readout_action_brief(
    readout=intake_scratch / 'owner-live-window-readouts' / 'completed' / 'live-window-readout.json',
    as_of_date='2026-06-18',
    output_dir=intake_scratch / 'owner-post-readout-action-briefs' / 'completed',
    overwrite=True,
)
action_brief_decision = decide_and_write(
    scratch_root=intake_scratch,
    returned_csv=None,
    as_of_date='2026-06-18',
    output_dir=TMP / 'dockets' / 'post-readout-action-brief-completed',
)
expect(action_brief_decision, 'RECORD-POST-READOUT-ACTION-FROM-BRIEF-NOT-CLOSURE')
action_brief_command = action_brief_decision.get('recommended_command', '')
if 'owner-post-readout-action' not in action_brief_command or 'CONFIRM=human-recorded-post-readout-action-no-closure' not in action_brief_command:
    fail('post-readout action brief should route to bounded dispatch record with confirmation token')
if 'NO_SERVICE_RECORD_EDIT=1' not in action_brief_command or 'NO_CLOSURE_FROM_DISPATCH=1' not in action_brief_command:
    fail('post-readout action command from brief must carry service/closure firebreak confirmations')
build_post_readout_action(
    readout=intake_scratch / 'owner-live-window-readouts' / 'completed' / 'live-window-readout.json',
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
    operator_confirmation=POST_READOUT_ACTION_CONFIRMATION,
    output_dir=intake_scratch / 'owner-post-readout-actions' / 'completed',
)
post_action_wait_decision = decide_and_write(
    scratch_root=intake_scratch,
    returned_csv=None,
    as_of_date='2026-06-24',
    output_dir=TMP / 'dockets' / 'post-readout-action-wait',
)
expect(post_action_wait_decision, 'AWAIT-POST-READOUT-ACTION-RECHECK')
if 'no field command' not in post_action_wait_decision.get('recommended_command', '') or 'due/recheck date 2026-06-25' not in post_action_wait_decision.get('reason', ''):
    fail('post-readout action before due date should wait without another archive command')

post_action_decision = decide_and_write(
    scratch_root=intake_scratch,
    returned_csv=None,
    as_of_date='2026-06-25',
    output_dir=TMP / 'dockets' / 'post-readout-action-completed',
)
expect(post_action_decision, 'PREPARE-POST-READOUT-RECHECK-BRIEF')
recheck_brief_command = post_action_decision.get('recommended_command', '')
if 'owner-post-readout-recheck-brief' not in recheck_brief_command or 'ACTION=' not in recheck_brief_command:
    fail('post-readout action at due date should route to bounded owner-post-readout-recheck-brief')
if 'AS_OF_DATE=2026-06-25' not in recheck_brief_command:
    fail('post-readout recheck brief command must carry the due/check date')
if 'service-record edit' not in post_action_decision.get('reason', '').lower() or 'closure' not in post_action_decision.get('reason', '').lower():
    fail('post-readout recheck brief route must keep record-edit and closure boundaries visible')

build_post_readout_recheck_brief(
    action=intake_scratch / 'owner-post-readout-actions' / 'completed' / 'post-readout-action.json',
    as_of_date='2026-06-25',
    output_dir=intake_scratch / 'owner-post-readout-recheck-briefs' / 'completed',
)
recheck_brief_decision = decide_and_write(
    scratch_root=intake_scratch,
    returned_csv=None,
    as_of_date='2026-06-25',
    output_dir=TMP / 'dockets' / 'post-readout-recheck-brief-completed',
)
expect(recheck_brief_decision, 'RECORD-POST-READOUT-RECHECK-FROM-BRIEF-NOT-CLOSURE')
recheck_command = recheck_brief_decision.get('recommended_command', '')
if 'owner-post-readout-recheck' not in recheck_command or 'CONFIRM=human-recorded-post-readout-recheck-no-closure' not in recheck_command:
    fail('post-readout recheck brief should route to bounded owner-post-readout-recheck with confirmation token')
if 'CHECK_DATE=2026-06-25' not in recheck_command or 'NO_CLOSURE_FROM_RECHECK=1' not in recheck_command:
    fail('post-readout recheck command must carry check date and closure firebreak confirmation')
if 'context receipt' not in recheck_brief_decision.get('reason', '').lower() or 'closure' not in recheck_brief_decision.get('reason', '').lower():
    fail('post-readout recheck-from-brief route must keep context and closure boundaries visible')

build_post_readout_recheck(
    action=intake_scratch / 'owner-post-readout-actions' / 'completed' / 'post-readout-action.json',
    check_date='2026-06-25',
    recheck_outcome='no-new-owner-context',
    reviewer_role_count=2,
    operator_confirmation=POST_READOUT_RECHECK_CONFIRMATION,
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
    output_dir=intake_scratch / 'owner-post-readout-rechecks' / 'no-context',
)
recheck_decision = decide_and_write(
    scratch_root=intake_scratch,
    returned_csv=None,
    as_of_date='2026-06-25',
    output_dir=TMP / 'dockets' / 'post-readout-recheck-no-context',
)
expect(recheck_decision, 'POST-READOUT-RECHECK-RECORDED-NO-FURTHER-ARCHIVE-ACTION')
if 'no field command' not in recheck_decision.get('recommended_command', ''):
    fail('post-readout recheck without new owner context should stop with no archive field command')
if 'service-record edits' not in recheck_decision.get('reason', '') or 'closure' not in recheck_decision.get('reason', '').lower():
    fail('post-readout recheck stop must keep service-record and closure boundaries visible')

# A post-readout recheck with new owner context must first link the actual CSV to a receipt,
# then route intake from that receipt rather than an old source-contact clock.
new_context_scratch = TMP / 'post-readout-new-context-scratch'
shutil.copytree(intake_scratch, new_context_scratch, dirs_exist_ok=True)
# Remove the no-context recheck copied from the prior scratch root so the new-context recheck is selected cleanly.
shutil.rmtree(new_context_scratch / 'owner-post-readout-rechecks', ignore_errors=True)
build_post_readout_recheck(
    action=new_context_scratch / 'owner-post-readout-actions' / 'completed' / 'post-readout-action.json',
    check_date='2026-06-26',
    recheck_outcome='new-owner-context-available',
    reviewer_role_count=2,
    operator_confirmation=POST_READOUT_RECHECK_CONFIRMATION,
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
    output_dir=new_context_scratch / 'owner-post-readout-rechecks' / 'new-context',
)
post_readout_csv = external_csv_dir / 'post readout owner context.csv'
write_dummy_csv(post_readout_csv)
receipt_needed_decision = decide_and_write(
    scratch_root=new_context_scratch,
    returned_csv=post_readout_csv,
    as_of_date='2026-06-26',
    output_dir=TMP / 'dockets' / 'post-readout-context-receipt-needed',
)
expect(receipt_needed_decision, 'RECORD-POST-READOUT-CONTEXT-RECEIPT-BEFORE-INTAKE')
receipt_command = receipt_needed_decision.get('recommended_command', '')
if 'owner-post-readout-context-receipt' not in receipt_command or 'SOURCE_CONTACT_STATUS' in receipt_command:
    fail('post-readout new context must route to context receipt before intake, not to old contact status')
if 'CONFIRM=human-linked-post-readout-owner-context-receipt' not in receipt_command or 'NO_CLOSURE_FROM_CONTEXT_RECEIPT=1' not in receipt_command:
    fail('post-readout context receipt command must carry confirmation and closure firebreak')

build_post_readout_context_receipt(
    recheck=new_context_scratch / 'owner-post-readout-rechecks' / 'new-context' / 'post-readout-recheck.json',
    csv_path=post_readout_csv,
    reviewer_role_count=2,
    operator_confirmation=POST_READOUT_CONTEXT_RECEIPT_CONFIRMATION,
    no_expansion_confirmed=True,
    no_public_claim_upgrade=True,
    no_service_record_edit=True,
    no_lifecycle_change=True,
    no_closure_from_context_receipt=True,
    raw_learner_data_present=False,
    protected_facts_present=False,
    security_payloads_present=False,
    public_claim_upgrade_requested=False,
    output_dir=new_context_scratch / 'owner-post-readout-context-receipts' / 'valid',
)
receipt_only_decision = decide_and_write(
    scratch_root=new_context_scratch,
    returned_csv=None,
    as_of_date='2026-06-26',
    output_dir=TMP / 'dockets' / 'post-readout-context-receipt-only',
)
expect(receipt_only_decision, 'POST-READOUT-CONTEXT-RECEIPT-RECORDED-ROUTE-ACTUAL-CONTEXT-CSV')
receipt_only_command = receipt_only_decision.get('recommended_command', '')
if 'make owner-field-next CSV=' not in receipt_only_command or 'owner-reply-intake' in receipt_only_command:
    fail('post-readout context receipt without CSV must reroute through owner-field-next with the actual CSV, not directly intake or fall through')
if 'same-returned-owner-context' not in receipt_only_command and post_readout_csv.name not in receipt_only_command:
    fail('post-readout context receipt reroute should name the same returned owner context, not a generic packet/contact path')
context_intake_decision = decide_and_write(
    scratch_root=new_context_scratch,
    returned_csv=post_readout_csv,
    as_of_date='2026-06-26',
    output_dir=TMP / 'dockets' / 'post-readout-context-intake',
)
expect(context_intake_decision, 'RUN-RETURNED-REPLY-WORK-FROM-POST-READOUT-CONTEXT-RECEIPT')
context_command = context_intake_decision.get('recommended_command', '')
if 'SOURCE_POST_READOUT_CONTEXT_RECEIPT=' not in context_command or 'SOURCE_CONTACT_STATUS=' in context_command:
    fail('post-readout context intake command must use the context receipt and not an old contact status')
if rel(new_context_scratch / 'owner-post-readout-context-receipts' / 'valid' / 'post-readout-context-receipt.json') not in context_command:
    fail('post-readout context intake command must point to the matching context receipt')

# A newer new-context recheck with the same CSV hash must require a fresh receipt tied to that
# current recheck, rather than reusing an older receipt from a prior post-readout cycle.
time.sleep(0.02)
build_post_readout_recheck(
    action=new_context_scratch / 'owner-post-readout-actions' / 'completed' / 'post-readout-action.json',
    check_date='2026-06-27',
    recheck_outcome='new-owner-context-available',
    reviewer_role_count=2,
    operator_confirmation=POST_READOUT_RECHECK_CONFIRMATION,
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
    output_dir=new_context_scratch / 'owner-post-readout-rechecks' / 'new-context-later',
)
stale_receipt_decision = decide_and_write(
    scratch_root=new_context_scratch,
    returned_csv=post_readout_csv,
    as_of_date='2026-06-27',
    output_dir=TMP / 'dockets' / 'post-readout-context-stale-receipt',
)
expect(stale_receipt_decision, 'RECORD-POST-READOUT-CONTEXT-RECEIPT-BEFORE-INTAKE')
if rel(new_context_scratch / 'owner-post-readout-rechecks' / 'new-context-later' / 'post-readout-recheck.json') not in stale_receipt_decision.get('recommended_command', ''):
    fail('post-readout context receipt reuse must be blocked when a newer new-context recheck is selected')
if rel(new_context_scratch / 'owner-post-readout-context-receipts' / 'valid' / 'post-readout-context-receipt.json') in stale_receipt_decision.get('recommended_command', ''):
    fail('router must not reuse an older context receipt for a newer new-context recheck, even with the same CSV hash')

wrong_post_readout_csv = external_csv_dir / 'post readout owner context wrong.csv'
write_dummy_csv(wrong_post_readout_csv)
with wrong_post_readout_csv.open('a', encoding='utf-8') as fh:
    fh.write('2,boundary,changed aggregate,no raw/protected data,\n')
wrong_context_decision = decide_and_write(
    scratch_root=new_context_scratch,
    returned_csv=wrong_post_readout_csv,
    as_of_date='2026-06-26',
    output_dir=TMP / 'dockets' / 'post-readout-context-wrong-csv',
)
expect(wrong_context_decision, 'RECORD-POST-READOUT-CONTEXT-RECEIPT-BEFORE-INTAKE')
if 'owner-post-readout-context-receipt' not in wrong_context_decision.get('recommended_command', ''):
    fail('a different CSV hash must require its own post-readout context receipt')

# A reask workbench review emits one bounded reask contact-clock command and can source the contact recorder.
reask_scratch = TMP / 'reask-review-scratch'
reask_source_contact = write_contact_source(
    reask_scratch / 'owner-contact-status' / 'seed-source' / 'contact-status.json',
    contact_status='SENT_AWAITING_REPLY',
    sent_date='2026-06-13',
    response_due_date='2026-06-20',
    status_date='2026-06-13',
    attempt_count=1,
)
reask_seed_dir = reask_scratch / 'owner-reply-workbench-seeds' / 'aiedu-sr-003'
reask_seed_dir.mkdir(parents=True, exist_ok=True)
(reask_seed_dir / 'workbench-seed.json').write_text(json.dumps({
    'seed_type': 'FT-0181-owner-packet-workbench-seed',
    'seed_version': 'rev0275',
    'created_at_utc': '2026-06-13T00:00:01Z',
    'source_truth_status': 'UNVERIFIED_OWNER_REPLY_PENDING_CUSTODY',
    'acceptance_state': 'NOT_ACCEPTED',
    'required_next_surface': 'docs/30-operations/ft0181-owner-packet-workbench.md',
    'source_contact_status': {
        'reference': rel(reask_source_contact),
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
build_review(
    seed=reask_seed_dir / 'workbench-seed.json',
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
    operator_confirmation=WORKBENCH_REVIEW_CONFIRMATION,
    output_dir=reask_scratch / 'owner-workbench-reviews' / 'reask',
)
decision = decide_and_write(
    scratch_root=reask_scratch,
    returned_csv=None,
    as_of_date='2026-06-21',
    output_dir=TMP / 'dockets' / 'workbench-reviewed-reask',
)
expect(decision, 'RECORD-REASK-LOG-FROM-WORKBENCH-REVIEW')
command = decision.get('recommended_command', '')
if 'make owner-reask-log' not in command or 'SOURCE_ARTIFACT=' not in command or 'workbench-review.json' not in command:
    fail('reask workbench review should emit a runnable reask-log command sourced from the review')
if 'STATUS=reask-awaiting-reply' in command:
    fail('reask workbench review must not create a contact clock before a reask-log exists')
expect_valid_reask_log_command(command, reask_scratch / 'owner-workbench-reviews' / 'reask' / 'workbench-review.json')

invalid_seed_scratch = TMP / 'invalid-seed-scratch'
invalid_seed_source = write_contact_source(
    invalid_seed_scratch / 'owner-contact-status' / 'seed-source' / 'contact-status.json',
    contact_status='SENT_AWAITING_REPLY',
    sent_date='2026-06-13',
    response_due_date='2026-06-20',
    status_date='2026-06-13',
    attempt_count=1,
)
invalid_seed_dir = invalid_seed_scratch / 'owner-reply-workbench-seeds' / 'locally-edited-accepted'
invalid_seed_dir.mkdir(parents=True, exist_ok=True)
(invalid_seed_dir / 'workbench-seed.json').write_text(json.dumps({
    'seed_type': 'FT-0181-owner-packet-workbench-seed',
    'acceptance_state': 'ACCEPTED',
    'ft0181_status': 'closed',
    'created_at_utc': '2026-06-14T00:00:00Z',
    'source_contact_status': {'reference': rel(invalid_seed_source)},
}, indent=2) + '\n', encoding='utf-8')
decision = decide_and_write(
    scratch_root=invalid_seed_scratch,
    returned_csv=None,
    as_of_date='2026-06-14',
    output_dir=TMP / 'dockets' / 'invalid-seed',
)
expect(decision, 'WORKBENCH-SEED-INTEGRITY-BLOCKED')
if 'no field command' not in decision.get('recommended_command', '') or 'workbench seed cannot drive a review brief' not in decision.get('reason', ''):
    fail('locally edited or weak workbench seed should block routing without creating evidence or closure')

invalid_review_scratch = TMP / 'invalid-review-scratch'
invalid_review_dir = invalid_review_scratch / 'owner-workbench-reviews' / 'locally-edited-accepted'
invalid_review_dir.mkdir(parents=True, exist_ok=True)
(invalid_review_dir / 'workbench-review.json').write_text(json.dumps({
    'review_type': 'FT-0181-owner-packet-workbench-review',
    'review_state': 'REVIEWED_ACCEPTED',
    'acceptance_state': 'ACCEPTED',
    'evidence_state': 'SRC2+',
    'created_at_utc': '2026-06-15T00:00:00Z',
}, indent=2) + '\n', encoding='utf-8')
decision = decide_and_write(
    scratch_root=invalid_review_scratch,
    returned_csv=None,
    as_of_date='2026-06-15',
    output_dir=TMP / 'dockets' / 'invalid-review',
)
expect(decision, 'WORKBENCH-REVIEW-INTEGRITY-BLOCKED')
if 'no field command' not in decision.get('recommended_command', '') or 'workbench review cannot drive' not in decision.get('reason', ''):
    fail('locally edited workbench review should block routing without creating evidence or closure')

invalid_decision_scratch = TMP / 'invalid-first-packet-decision-scratch'
invalid_decision_dir = invalid_decision_scratch / 'owner-first-packet-decisions' / 'locally-edited-accepted'
invalid_decision_dir.mkdir(parents=True, exist_ok=True)
(invalid_decision_dir / 'first-packet-decision.json').write_text(json.dumps({
    'decision_type': 'FT-0181-first-packet-decision-board',
    'board_state': 'DECISION_ACCEPTED',
    'acceptance_state': 'ACCEPTED',
    'evidence_state': 'SRC2+',
    'created_at_utc': '2026-06-15T00:00:00Z',
}, indent=2) + '\n', encoding='utf-8')
decision = decide_and_write(
    scratch_root=invalid_decision_scratch,
    returned_csv=None,
    as_of_date='2026-06-15',
    output_dir=TMP / 'dockets' / 'invalid-first-packet-decision',
)
expect(decision, 'FIRST-PACKET-DECISION-INTEGRITY-BLOCKED')
if 'no field command' not in decision.get('recommended_command', '') or 'first-packet decision cannot drive' not in decision.get('reason', ''):
    fail('locally edited first-packet decision should block routing without creating evidence or closure')

invalid_ticket_scratch = TMP / 'invalid-post-decision-ticket-scratch'
invalid_ticket_dir = invalid_ticket_scratch / 'owner-post-decision-change-tickets' / 'locally-edited-active'
invalid_ticket_dir.mkdir(parents=True, exist_ok=True)
(invalid_ticket_dir / 'post-decision-change-ticket.json').write_text(json.dumps({
    'ticket_type': 'FT-0181-post-decision-change-ticket',
    'ticket_state': 'active_change',
    'acceptance_state': 'ACCEPTED',
    'evidence_state': 'SRC2+',
    'created_at_utc': '2026-06-15T00:00:00Z',
}, indent=2) + '\n', encoding='utf-8')
decision = decide_and_write(
    scratch_root=invalid_ticket_scratch,
    returned_csv=None,
    as_of_date='2026-06-15',
    output_dir=TMP / 'dockets' / 'invalid-post-decision-ticket',
)
expect(decision, 'POST-DECISION-CHANGE-TICKET-INTEGRITY-BLOCKED')
if 'no field command' not in decision.get('recommended_command', '') or 'post-decision change ticket cannot drive' not in decision.get('reason', ''):
    fail('locally edited post-decision change ticket should block routing without creating evidence or closure')

invalid_card_scratch = TMP / 'invalid-live-window-card-scratch'
invalid_card_dir = invalid_card_scratch / 'owner-live-window-cards' / 'locally-edited-active'
invalid_card_dir.mkdir(parents=True, exist_ok=True)
(invalid_card_dir / 'live-window-card.json').write_text(json.dumps({
    'card_type': 'FT-0181-live-window-stop-rollback-card',
    'window_state': 'active',
    'acceptance_state': 'ACCEPTED',
    'evidence_state': 'SRC2+',
    'created_at_utc': '2026-06-15T00:00:00Z',
}, indent=2) + '\n', encoding='utf-8')
decision = decide_and_write(
    scratch_root=invalid_card_scratch,
    returned_csv=None,
    as_of_date='2026-06-15',
    output_dir=TMP / 'dockets' / 'invalid-live-window-card',
)
expect(decision, 'LIVE-WINDOW-CARD-INTEGRITY-BLOCKED')
if 'no field command' not in decision.get('recommended_command', '') or 'live-window card cannot drive' not in decision.get('reason', ''):
    fail('locally edited live-window card should block routing without creating evidence or closure')

# Output to controlled or nonscratch archive space is blocked.
blocked = decide_and_write(
    scratch_root=TMP / 'empty-scratch',
    returned_csv=None,
    as_of_date='2026-06-13',
    output_dir=ROOT / 'docs' / 'bad-field-next-action',
)
if blocked.get('ok') or blocked.get('outcome') != 'FIELD-NEXT-ACTION-OUTPUT-BLOCKED':
    fail('controlled docs output should be blocked')
leak_block = decide_and_write(
    scratch_root=TMP / 'empty-scratch',
    returned_csv=None,
    as_of_date='2026-06-13',
    output_dir=ROOT / 'local-field-next-leak',
)
if leak_block.get('ok') or leak_block.get('outcome') != 'FIELD-NEXT-ACTION-OUTPUT-BLOCKED':
    fail('nonscratch top-level archive output should be blocked')

shutil.rmtree(TMP)
shutil.rmtree(FIELD_TMP, ignore_errors=True)
shutil.rmtree(SUPPORT_TMP, ignore_errors=True)
shutil.rmtree(ROOT / 'scratch' / 'checks' / 'ft0181-field-next-action-returned-csv-negative', ignore_errors=True)
shutil.rmtree(external_csv_dir, ignore_errors=True)
print('check_ft0181_field_next_action: OK (packet/route-block/contact/returned-reply-work/reask/seed/review-brief/no-packet routing, cross-type manifest-clock artifact selection, packet created_at_utc ranking, compact session docket, safe-local packet prep, packet/route-block/terminal/contact local artifact integrity blocks, date-keyed contact outputs, returned CSV source/smoke/source-provenance guard, checker-scratch returned CSV block, router-first awaiting state, workbench review-brief/review gates, first-packet decision-brief/decision gates, post-decision change-ticket-brief/ticket gates, live-window card/readout-brief gate, post-readout action due-date recheck-brief gate, post-readout context receipt gate, context-receipt reroute, current-recheck receipt match, non-field scratch firebreak, field validation fixture firebreak, output block)')
