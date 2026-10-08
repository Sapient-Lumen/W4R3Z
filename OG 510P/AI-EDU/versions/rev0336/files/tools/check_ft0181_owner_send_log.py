#!/usr/bin/env python3
"""Validate the FT-0181 owner-send-log recorder."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from prepare_ft0181_owner_request_packet import build_packet
from record_ft0181_owner_send_log import OPERATOR_CONFIRMATION, build_send_log
from ft0181_field_guards import owner_send_log_integrity_error

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / 'scratch' / 'field' / 'ft0181' / 'validation' / 'ft0181-owner-send-log'


def fail(msg: str) -> None:
    raise SystemExit(f'check_ft0181_owner_send_log: FAIL: {msg}')


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def load_manifest(path: Path) -> dict:
    return json.loads((path / 'send-log.json').read_text(encoding='utf-8'))


if TMP.exists():
    shutil.rmtree(TMP)
TMP.mkdir(parents=True, exist_ok=True)

packet_dir = TMP / 'owner-request-packets' / 'p1'
packet = build_packet(
    output_dir=packet_dir,
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    return_date='2026-06-20',
)
if not packet.get('ok'):
    fail(f'packet fixture did not build: {packet}')
packet_manifest = packet_dir / 'packet-manifest.json'

out = TMP / 'send-log'
result = build_send_log(
    output_dir=out,
    packet_manifest=packet_manifest,
    sent_date='2026-06-13',
    response_due_date='2026-06-20',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    send_channel_class='email',
    owner_route_class='accountable-owner',
    adapted_from_packet=True,
    operator_confirmation=OPERATOR_CONFIRMATION,
    minimal_send_note='bounded route class only',
)
if not result.get('ok'):
    fail(f'send log did not build: {result}')
manifest = load_manifest(out)
for key, expected in {
    'send_log_type': 'FT-0181-owner-send-log',
    'followthrough_id': 'FT-0181',
    'service_record_id': 'AIEDU-SR-003',
    'evidence_state': 'not_evidence',
    'source_truth_class': 'not_evidence',
    'closure_effect': 'does_not_close_ft0181',
    'public_claim_effect': 'none',
    'contact_status_effect': 'may_source_sent_awaiting_reply_clock_only',
}.items():
    if manifest.get(key) != expected:
        fail(f'{key} should be {expected}')
if manifest.get('packet_manifest_ref') != rel(packet_manifest):
    fail('send log must preserve archive-relative packet manifest ref')
if manifest.get('operator_confirmation') != OPERATOR_CONFIRMATION:
    fail('send log must preserve operator confirmation token')
if manifest.get('no_contact_details_stored') is not True:
    fail('send log must assert no contact details stored')
if manifest.get('no_raw_or_protected_material_stored') is not True:
    fail('send log must assert no raw/protected material stored')
if manifest.get('no_widening_confirmation') is not True:
    fail('send log must assert no widening')
if manifest.get('max_response_clock_days') != 7:
    fail('send log must cap first-contact response clock at 7 days')
if owner_send_log_integrity_error(manifest, archive_root=ROOT):
    fail('fresh send log should pass shared integrity guard')
if not (out / 'SEND-LOG.md').exists():
    fail('SEND-LOG.md note missing')
joined = json.dumps(manifest).lower() + '\n' + (out / 'SEND-LOG.md').read_text(encoding='utf-8').lower()
for forbidden in ['recipient name', 'owner answer', 'student id', 'learner name', 'raw lms export']:
    # These may appear only as exclusions, not generated data fields. Check the
    # manifest itself stays clean of raw/contact hints.
    if forbidden in json.dumps(manifest).lower():
        fail(f'manifest should not store forbidden contact/raw hint: {forbidden}')

blocked = build_send_log(
    output_dir=ROOT / 'docs' / 'bad-owner-send-log',
    packet_manifest=packet_manifest,
    sent_date='2026-06-13',
    response_due_date='2026-06-20',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    send_channel_class='email',
    owner_route_class='accountable-owner',
    operator_confirmation=OPERATOR_CONFIRMATION,
)
if blocked.get('ok') or blocked.get('error') != 'OWNER-SEND-LOG-OUTPUT-BLOCKED':
    fail('archive-controlled docs output should be blocked')

blocked = build_send_log(
    output_dir=TMP / 'bad-confirm',
    packet_manifest=packet_manifest,
    sent_date='2026-06-13',
    response_due_date='2026-06-20',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    send_channel_class='email',
    owner_route_class='accountable-owner',
    operator_confirmation='I-sent-it',
)
if blocked.get('ok') or blocked.get('error') != 'OWNER-SEND-LOG-CONFIRMATION-BLOCKED':
    fail('wrong operator confirmation should be blocked')

blocked = build_send_log(
    output_dir=TMP / 'bad-clock',
    packet_manifest=packet_manifest,
    sent_date='2026-06-21',
    response_due_date='2026-06-20',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    send_channel_class='email',
    owner_route_class='accountable-owner',
    operator_confirmation=OPERATOR_CONFIRMATION,
)
if blocked.get('ok') or blocked.get('error') != 'OWNER-SEND-LOG-CLOCK-BLOCKED':
    fail('due date before sent date should be blocked')

blocked = build_send_log(
    output_dir=TMP / 'bad-long-clock',
    packet_manifest=packet_manifest,
    sent_date='2026-06-13',
    response_due_date='2026-07-01',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    send_channel_class='email',
    owner_route_class='accountable-owner',
    operator_confirmation=OPERATOR_CONFIRMATION,
)
if blocked.get('ok') or blocked.get('error') != 'OWNER-SEND-LOG-CLOCK-BLOCKED':
    fail('open-ended first-contact clock should be blocked')

blocked = build_send_log(
    output_dir=TMP / 'bad-arg',
    packet_manifest=packet_manifest,
    sent_date='2026-06-13',
    response_due_date='2026-06-20',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route with email address',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    send_channel_class='email',
    owner_route_class='accountable-owner',
    operator_confirmation=OPERATOR_CONFIRMATION,
)
if blocked.get('ok') or blocked.get('error') != 'OWNER-SEND-LOG-ARG-BLOCKED':
    fail('contact-detail-like arguments should be blocked')

outside_packet = TMP / 'not-scratch' / 'packet-manifest.json'
outside_packet.parent.mkdir(parents=True, exist_ok=True)
outside_packet.write_text(packet_manifest.read_text(encoding='utf-8'), encoding='utf-8')
blocked = build_send_log(
    output_dir=TMP / 'bad-packet',
    packet_manifest=ROOT / 'templates' / 'ft0181-eight-row-owner-reply-template.csv',
    sent_date='2026-06-13',
    response_due_date='2026-06-20',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    send_channel_class='email',
    owner_route_class='accountable-owner',
    operator_confirmation=OPERATOR_CONFIRMATION,
)
if blocked.get('ok') or blocked.get('error') != 'OWNER-SEND-LOG-PACKET-BLOCKED':
    fail('archive-controlled/non-json packet manifest should be blocked')

stale = TMP / 'stale-overwrite'
stale.mkdir()
(stale / 'old.txt').write_text('stale\n', encoding='utf-8')
(stale / 'nested').mkdir()
(stale / 'nested' / 'old.txt').write_text('stale\n', encoding='utf-8')
result = build_send_log(
    output_dir=stale,
    packet_manifest=packet_manifest,
    sent_date='2026-06-13',
    response_due_date='2026-06-20',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    send_channel_class='ticket',
    owner_route_class='delegated-local-owner-route',
    operator_confirmation=OPERATOR_CONFIRMATION,
    overwrite=True,
)
if not result.get('ok'):
    fail(f'overwrite send log did not build: {result}')
if (stale / 'old.txt').exists() or (stale / 'nested').exists():
    fail('overwrite should clear stale send-log files and directories')

print('check_ft0181_owner_send_log: OK')
