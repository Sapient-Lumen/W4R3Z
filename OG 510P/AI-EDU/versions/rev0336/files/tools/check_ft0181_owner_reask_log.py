#!/usr/bin/env python3
"""Validate the FT-0181 owner-reask-log recorder."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from prepare_ft0181_owner_request_packet import build_packet
from record_ft0181_owner_contact_status import OPERATOR_CONFIRMATIONS, build_status
from record_ft0181_owner_send_log import OPERATOR_CONFIRMATION as SEND_LOG_CONFIRMATION, build_send_log
from record_ft0181_owner_reask_log import OPERATOR_CONFIRMATION, build_reask_log
from ft0181_field_guards import owner_reask_log_integrity_error

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / 'scratch' / 'field' / 'ft0181' / 'validation' / 'ft0181-owner-reask-log'


def fail(msg: str) -> None:
    raise SystemExit(f'check_ft0181_owner_reask_log: FAIL: {msg}')


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def load_manifest(path: Path) -> dict:
    return json.loads((path / 'reask-log.json').read_text(encoding='utf-8'))


def write_contact_source(path: Path, *, sent_date: str, response_due_date: str, status_date: str = '2026-06-13') -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    slug = path.parent.name
    packet_dir = TMP / 'owner-request-packets' / slug
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
        fail(f'contact-source packet fixture did not build: {packet}')
    send_log_dir = TMP / 'owner-send-logs' / slug
    send_log = build_send_log(
        output_dir=send_log_dir,
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
    if not send_log.get('ok'):
        fail(f'contact-source send-log fixture did not build: {send_log}')
    path.write_text(json.dumps({
        'status_id': 'AIEDU-SR-003-OWNER-CONTACT-STATUS',
        'followthrough_id': 'FT-0181',
        'contact_status': 'SENT_AWAITING_REPLY',
        'sent_date': sent_date,
        'response_due_date': response_due_date,
        'status_date': status_date,
        'attempt_count': 1,
        'max_response_clock_days': 7,
        'created_at_utc': f'{status_date}T00:00:00Z',
        'evidence_state': 'not_evidence',
        'source_truth_class': 'not_evidence',
        'closure_effect': 'does_not_close_ft0181',
        'public_claim_effect': 'none',
        'source_artifact_verified': True,
        'source_artifact_ref': rel(send_log_dir / 'send-log.json'),
        'source_artifact_type': 'send-log',
        'source_artifact_verification': 'verified local owner-send log',
        'no_widening_confirmation': True,
    }, indent=2) + '\n', encoding='utf-8')
    return path


def write_reask_intake_source(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        'bundle_type': 'FT-0181-owner-reply-local-intake-bundle',
        'bundle_version': 'rev0282',
        'followthrough_id': 'FT-0181',
        'service_record_id': 'AIEDU-SR-003',
        'created_at_utc': '2026-06-21T00:00:00Z',
        'triage_outcome': 'RE-ASK-ONCE',
        'ft0181_status': 'live',
        'claim_ceiling': 'not evidence; bounded clarification only',
        'evidence_state': 'not_evidence',
    }, indent=2) + '\n', encoding='utf-8')
    return path


if TMP.exists():
    shutil.rmtree(TMP)
TMP.mkdir(parents=True, exist_ok=True)

sent_source = write_contact_source(
    TMP / 'owner-contact-status' / 'sent-source' / 'contact-status.json',
    sent_date='2026-06-13',
    response_due_date='2026-06-20',
)
open_sent_source = write_contact_source(
    TMP / 'owner-contact-status' / 'open-sent-source' / 'contact-status.json',
    sent_date='2026-06-16',
    response_due_date='2026-06-23',
    status_date='2026-06-16',
)
intake_source = write_reask_intake_source(TMP / 'owner-reply-intake-bundles' / 'reask-once' / 'bundle-manifest.json')

out = TMP / 'owner-reask-logs' / 'from-sent-clock'
result = build_reask_log(
    output_dir=out,
    source_artifact=sent_source,
    sent_date='2026-06-21',
    response_due_date='2026-06-24',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    reask_channel_class='email',
    owner_route_class='same-accountable-owner-route',
    adapted_from_template=True,
    operator_confirmation=OPERATOR_CONFIRMATION,
    minimal_reask_note='bounded clarification class only',
)
if not result.get('ok'):
    fail(f'reask log did not build from expired sent clock: {result}')
manifest = load_manifest(out)
for key, expected in {
    'reask_log_type': 'FT-0181-owner-reask-log',
    'followthrough_id': 'FT-0181',
    'service_record_id': 'AIEDU-SR-003',
    'evidence_state': 'not_evidence',
    'source_truth_class': 'not_evidence',
    'closure_effect': 'does_not_close_ft0181',
    'public_claim_effect': 'none',
    'contact_status_effect': 'may_source_reask_awaiting_reply_clock_only',
}.items():
    if manifest.get(key) != expected:
        fail(f'{key} should be {expected}')
if manifest.get('reask_source_ref') != rel(sent_source):
    fail('reask log must preserve archive-relative source artifact ref')
if manifest.get('reask_source_type') != 'prior-sent-contact-status':
    fail('reask log should classify prior SENT clock source')
if manifest.get('operator_confirmation') != OPERATOR_CONFIRMATION:
    fail('reask log must preserve operator confirmation token')
if manifest.get('no_contact_details_stored') is not True:
    fail('reask log must assert no contact details stored')
if manifest.get('no_raw_or_protected_material_stored') is not True:
    fail('reask log must assert no raw/protected material stored')
if manifest.get('no_widening_confirmation') is not True:
    fail('reask log must assert no widening')
if manifest.get('max_response_clock_days') != 3:
    fail('reask log must cap clarification response clock at 3 days')
if owner_reask_log_integrity_error(manifest, archive_root=ROOT):
    fail('fresh reask log should pass shared integrity guard')
if not (out / 'REASK-LOG.md').exists():
    fail('REASK-LOG.md note missing')
if 'owner answer' in json.dumps(manifest).lower() or '@' in json.dumps(manifest).lower():
    fail('manifest should not store owner answers or contact addresses')

# The reask contact clock must be sourced from the reask-log, not the prior SENT
# clock or the intake/workbench artifact that created the clarification need.
clock_dir = TMP / 'owner-contact-status' / 'reask-clock-from-log'
result = build_status(
    output_dir=clock_dir,
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
    source_artifact=rel(out / 'reask-log.json'),
)
if not result.get('ok'):
    fail(f'reask clock sourced from reask log should build: {result}')
clock_manifest = json.loads((clock_dir / 'contact-status.json').read_text(encoding='utf-8'))
if clock_manifest.get('source_artifact_type') != 'reask-log':
    fail('reask contact status must classify source artifact as reask-log')

blocked = build_status(
    output_dir=TMP / 'owner-contact-status' / 'blocked-direct-clock-source',
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
    source_artifact=rel(sent_source),
)
if blocked.get('ok') or blocked.get('error') != 'OWNER-CONTACT-SOURCE-ARTIFACT-BLOCKED':
    fail('prior SENT clock should not directly source a REASK contact clock')

intake_out = TMP / 'owner-reask-logs' / 'from-intake-reask-once'
result = build_reask_log(
    output_dir=intake_out,
    source_artifact=intake_source,
    sent_date='2026-06-21',
    response_due_date='2026-06-24',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    reask_channel_class='ticket',
    owner_route_class='governance-intake',
    operator_confirmation=OPERATOR_CONFIRMATION,
)
if not result.get('ok'):
    fail(f'reask log should build from RE-ASK-ONCE intake source: {result}')
if load_manifest(intake_out).get('reask_source_type') != 'reask-once-intake-bundle':
    fail('reask log should classify RE-ASK-ONCE intake source')

blocked = build_reask_log(
    output_dir=ROOT / 'docs' / 'bad-owner-reask-log',
    source_artifact=sent_source,
    sent_date='2026-06-21',
    response_due_date='2026-06-24',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    reask_channel_class='email',
    owner_route_class='same-accountable-owner-route',
    operator_confirmation=OPERATOR_CONFIRMATION,
)
if blocked.get('ok') or blocked.get('error') != 'OWNER-REASK-LOG-OUTPUT-BLOCKED':
    fail('archive-controlled docs output should be blocked')

blocked = build_reask_log(
    output_dir=TMP / 'bad-confirm',
    source_artifact=sent_source,
    sent_date='2026-06-21',
    response_due_date='2026-06-24',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    reask_channel_class='email',
    owner_route_class='same-accountable-owner-route',
    operator_confirmation='sent-reask',
)
if blocked.get('ok') or blocked.get('error') != 'OWNER-REASK-LOG-CONFIRMATION-BLOCKED':
    fail('wrong operator confirmation should be blocked')

blocked = build_reask_log(
    output_dir=TMP / 'bad-clock',
    source_artifact=sent_source,
    sent_date='2026-06-21',
    response_due_date='2026-06-30',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    reask_channel_class='email',
    owner_route_class='same-accountable-owner-route',
    operator_confirmation=OPERATOR_CONFIRMATION,
)
if blocked.get('ok') or blocked.get('error') != 'OWNER-REASK-LOG-CLOCK-BLOCKED':
    fail('open-ended reask clock should be blocked')

blocked = build_reask_log(
    output_dir=TMP / 'bad-open-source-clock',
    source_artifact=open_sent_source,
    sent_date='2026-06-21',
    response_due_date='2026-06-24',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    reask_channel_class='email',
    owner_route_class='same-accountable-owner-route',
    operator_confirmation=OPERATOR_CONFIRMATION,
)
if blocked.get('ok') or blocked.get('error') != 'OWNER-REASK-LOG-SOURCE-BLOCKED':
    fail('open first-contact clock should not source a reask log')

blocked = build_reask_log(
    output_dir=TMP / 'bad-arg',
    source_artifact=sent_source,
    sent_date='2026-06-21',
    response_due_date='2026-06-24',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route with email address',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    reask_channel_class='email',
    owner_route_class='same-accountable-owner-route',
    operator_confirmation=OPERATOR_CONFIRMATION,
)
if blocked.get('ok') or blocked.get('error') != 'OWNER-REASK-LOG-ARG-BLOCKED':
    fail('contact-detail-like arguments should be blocked')

stale = TMP / 'owner-reask-logs' / 'stale-overwrite'
stale.mkdir()
(stale / 'old.txt').write_text('stale\n', encoding='utf-8')
(stale / 'nested').mkdir()
(stale / 'nested' / 'old.txt').write_text('stale\n', encoding='utf-8')
result = build_reask_log(
    output_dir=stale,
    source_artifact=sent_source,
    sent_date='2026-06-21',
    response_due_date='2026-06-24',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    reask_channel_class='delegated-local-route',
    owner_route_class='delegated-local-owner-route',
    operator_confirmation=OPERATOR_CONFIRMATION,
    overwrite=True,
)
if not result.get('ok'):
    fail(f'overwrite reask log did not build: {result}')
if (stale / 'old.txt').exists() or (stale / 'nested').exists():
    fail('overwrite should clear stale reask-log files and directories')

shutil.rmtree(TMP)
print('check_ft0181_owner_reask_log: OK (bounded reask-send log, reask-log-to-contact-clock firebreak, source/output/argument/clock guards, and overwrite cleanup)')
