#!/usr/bin/env python3
"""Validate the FT-0181 owner-contact status recorder."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from prepare_ft0181_owner_request_packet import build_packet
from record_ft0181_owner_contact_status import OPERATOR_CONFIRMATIONS, build_status
from record_ft0181_owner_send_log import OPERATOR_CONFIRMATION as SEND_LOG_CONFIRMATION, build_send_log
from record_ft0181_owner_reask_log import OPERATOR_CONFIRMATION as REASK_LOG_CONFIRMATION, build_reask_log
from ft0181_field_guards import owner_contact_status_integrity_error

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / 'scratch' / 'field' / 'ft0181' / 'validation' / 'ft0181-owner-contact-status'


def fail(msg: str) -> None:
    raise SystemExit(f'check_ft0181_owner_contact_status: FAIL: {msg}')


def load_manifest(path: Path) -> dict:
    return json.loads((path / 'contact-status.json').read_text(encoding='utf-8'))


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def context_for(status: str, source: Path | str) -> dict[str, str]:
    source_text = rel(source) if isinstance(source, Path) else source
    return {
        'operator_confirmation': OPERATOR_CONFIRMATIONS[status],
        'source_artifact': source_text,
    }


def build_sent_contact_source(name: str, *, sent_date: str, response_due_date: str, status_date: str) -> Path:
    packet_dir = TMP / 'source-artifacts' / 'owner-request-packets' / name
    packet_built = build_packet(
        output_dir=packet_dir,
        service_label='AIEDU-SR-003 draft reminder pilot',
        owner_role='accountable service owner route',
        source_record_set='owner-maintained local service record set',
        date_range='2026-06-01 through 2026-06-07',
        return_date=response_due_date,
        overwrite=True,
    )
    if not packet_built.get('ok'):
        fail(f'{name} packet source fixture did not build: {packet_built}')
    send_dir = TMP / 'source-artifacts' / 'owner-send-logs' / name
    send_log_built = build_send_log(
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
    if not send_log_built.get('ok'):
        fail(f'{name} send-log source fixture did not build: {send_log_built}')
    status_dir = TMP / 'source-artifacts' / 'owner-contact-status' / name
    status_built = build_status(
        output_dir=status_dir,
        status='sent-awaiting-reply',
        service_label='AIEDU-SR-003 draft reminder pilot',
        owner_role='accountable service owner route',
        source_record_set='owner-maintained local service record set',
        date_range='2026-06-01 through 2026-06-07',
        sent_date=sent_date,
        response_due_date=response_due_date,
        status_date=status_date,
        attempt_count=1,
        operator_confirmation=OPERATOR_CONFIRMATIONS['sent-awaiting-reply'],
        source_artifact=rel(send_dir / 'send-log.json'),
        overwrite=True,
    )
    if not status_built.get('ok'):
        fail(f'{name} contact-status source fixture did not build: {status_built}')
    return status_dir / 'contact-status.json'


def build_reask_contact_source(name: str, *, reask_log_source: Path, sent_date: str, response_due_date: str, status_date: str) -> Path:
    status_dir = TMP / 'source-artifacts' / 'owner-contact-status' / name
    status_built = build_status(
        output_dir=status_dir,
        status='reask-awaiting-reply',
        service_label='AIEDU-SR-003 draft reminder pilot',
        owner_role='accountable service owner route',
        source_record_set='owner-maintained local service record set',
        date_range='2026-06-01 through 2026-06-07',
        sent_date=sent_date,
        response_due_date=response_due_date,
        status_date=status_date,
        attempt_count=2,
        operator_confirmation=OPERATOR_CONFIRMATIONS['reask-awaiting-reply'],
        source_artifact=rel(reask_log_source),
        overwrite=True,
    )
    if not status_built.get('ok'):
        fail(f'{name} reask contact-status source fixture did not build: {status_built}')
    return status_dir / 'contact-status.json'


if TMP.exists():
    shutil.rmtree(TMP)
TMP.mkdir(parents=True, exist_ok=True)

packet_source_dir = TMP / 'source-artifacts' / 'owner-request-packets' / 'p1'
packet_built = build_packet(
    output_dir=packet_source_dir,
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    return_date='2026-06-20',
)
if not packet_built.get('ok'):
    fail(f'packet source fixture did not build: {packet_built}')
packet_source = packet_source_dir / 'packet-manifest.json'
send_log_source_dir = TMP / 'source-artifacts' / 'owner-send-logs' / 'send1'
send_log_built = build_send_log(
    output_dir=send_log_source_dir,
    packet_manifest=packet_source,
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
if not send_log_built.get('ok'):
    fail(f'send-log source fixture did not build: {send_log_built}')
send_log_source = send_log_source_dir / 'send-log.json'
sent_source = build_sent_contact_source(
    'sent-source',
    sent_date='2026-06-13',
    response_due_date='2026-06-20',
    status_date='2026-06-13',
)
future_sent_source = build_sent_contact_source(
    'future-sent-source',
    sent_date='2026-06-16',
    response_due_date='2026-06-23',
    status_date='2026-06-16',
)
reask_log_source_dir = TMP / 'source-artifacts' / 'owner-reask-logs' / 'reask1'
reask_log_built = build_reask_log(
    output_dir=reask_log_source_dir,
    source_artifact=sent_source,
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
if not reask_log_built.get('ok'):
    fail(f'reask-log source fixture did not build: {reask_log_built}')
reask_log_source = reask_log_source_dir / 'reask-log.json'
reask_source = build_reask_contact_source(
    'reask-source',
    reask_log_source=reask_log_source,
    sent_date='2026-06-21',
    response_due_date='2026-06-24',
    status_date='2026-06-21',
)

sent_dir = TMP / 'sent'
result = build_status(
    output_dir=sent_dir,
    status='sent-awaiting-reply',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    sent_date='2026-06-13',
    response_due_date='2026-06-20',
    status_date='2026-06-13',
    attempt_count=1,
    minimal_reason='Bounded first ask sent through local owner route.',
    **context_for('sent-awaiting-reply', send_log_source),
)
if not result.get('ok'):
    fail(f'sent status did not build: {result}')
manifest = load_manifest(sent_dir)
if manifest['contact_status'] != 'SENT_AWAITING_REPLY':
    fail('sent contact_status mismatch')
if not str(manifest.get('created_at_utc', '')).endswith('Z'):
    fail('sent manifest must include created_at_utc for manifest-clock field routing')
for key, expected in {
    'evidence_state': 'not_evidence',
    'source_truth_class': 'not_evidence',
    'closure_effect': 'does_not_close_ft0181',
    'public_claim_effect': 'none',
}.items():
    if manifest.get(key) != expected:
        fail(f'{key} should be {expected}')
if not manifest.get('no_widening_confirmation'):
    fail('sent manifest must carry no_widening_confirmation')
if manifest.get('operator_confirmation') != OPERATOR_CONFIRMATIONS['sent-awaiting-reply']:
    fail('sent manifest must preserve the operator confirmation token')
if manifest.get('confirmation_effect') != 'local_operator_assertion_not_evidence':
    fail('operator confirmation must be explicitly non-evidence')
if manifest.get('source_artifact_ref') != rel(send_log_source):
    fail('sent manifest should preserve the source artifact reference')
if manifest.get('source_artifact_verified') is not True or manifest.get('source_artifact_type') != 'send-log':
    fail('sent manifest must verify the source artifact as a send log')
if owner_contact_status_integrity_error(manifest, archive_root=ROOT):
    fail('sent manifest should pass archive-root source-anchor integrity')
missing_source_manifest = dict(manifest)
missing_source_manifest['source_artifact_ref'] = rel(TMP / 'source-artifacts' / 'owner-send-logs' / 'missing' / 'send-log.json')
missing_source_error = owner_contact_status_integrity_error(missing_source_manifest, archive_root=ROOT)
if 'existing source artifact file' not in str(missing_source_error):
    fail(f'missing source artifact should be blocked by contact source-anchor guard: {missing_source_error}')
mismatched_source_manifest = dict(manifest)
mismatched_source_manifest['response_due_date'] = '2026-06-19'
mismatched_source_error = owner_contact_status_integrity_error(mismatched_source_manifest, archive_root=ROOT)
if 'response_due_date must match referenced send-log.json' not in str(mismatched_source_error):
    fail(f'mismatched source due date should be blocked by contact source-anchor guard: {mismatched_source_error}')
allowed_commands = '\n'.join(manifest.get('allowed_next_commands', []))
if 'YYYY-MM-DD' in allowed_commands or 'make owner-reply-intake CSV=' in allowed_commands:
    fail('sent manifest allowed_next_commands must route through owner-field-next without date placeholders or direct intake')
if not (sent_dir / 'SENT-AWAITING-REPLY.md').exists():
    fail('sent note missing')
if 'raw' in ' '.join(manifest.get('generated_files', [])).lower():
    fail('generated files should not suggest raw content')

reask_dir = TMP / 'reask'
result = build_status(
    output_dir=reask_dir,
    status='reask-awaiting-reply',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    sent_date='2026-06-21',
    response_due_date='2026-06-24',
    status_date='2026-06-21',
    attempt_count=2,
    minimal_reason='One bounded clarification sent for a missing row meaning.',
    **context_for('reask-awaiting-reply', reask_log_source),
)
if not result.get('ok'):
    fail(f'reask status did not build: {result}')
reask_manifest = load_manifest(reask_dir)
if reask_manifest['contact_status'] != 'REASK_AWAITING_REPLY':
    fail('reask contact_status mismatch')
if reask_manifest.get('source_artifact_ref') != rel(reask_log_source) or reask_manifest.get('source_artifact_type') != 'reask-log':
    fail('reask manifest must verify source artifact as a reask log')
if not (reask_dir / 'REASK-AWAITING-REPLY.md').exists():
    fail('reask note missing')

no_packet_dir = TMP / 'no-owner-packet'
result = build_status(
    output_dir=no_packet_dir,
    status='no-owner-packet',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    sent_date='2026-06-21',
    response_due_date='2026-06-24',
    status_date='2026-06-24',
    attempt_count=2,
    minimal_reason='No viable owner reply returned after first ask and one clarification.',
    **context_for('no-owner-packet', reask_source),
)
if not result.get('ok'):
    fail(f'no-owner-packet status did not build: {result}')
manifest = load_manifest(no_packet_dir)
if manifest['contact_status'] != 'NO_OWNER_PACKET':
    fail('no-owner-packet contact_status mismatch')
if manifest.get('max_response_clock_days') != 3:
    fail('no-owner-packet manifest must preserve the bounded re-ask response clock cap')
if manifest['next_action'] != 'keep_ft0181_live_without_widening_or_closure_claim':
    fail('no-owner-packet next_action mismatch')
if 'create_new_registry_or_doctrine_surface_to_replace_missing_owner_packet' not in manifest.get('forbidden_actions', []):
    fail('no-owner-packet must forbid registry/doctrine workaround')
if not (no_packet_dir / 'NO-OWNER-PACKET-OUTCOME.md').exists():
    fail('no-owner-packet outcome note missing')

# Overwrite must clear stale note files; otherwise a reused local directory can carry
# an old SENT or REASK note alongside the new status and mislead the operator.
stale_dir = TMP / 'stale-overwrite'
stale_dir.mkdir()
(stale_dir / 'SENT-AWAITING-REPLY.md').write_text('stale sent note\n', encoding='utf-8')
(stale_dir / 'nested').mkdir()
(stale_dir / 'nested' / 'old.txt').write_text('stale nested file\n', encoding='utf-8')
result = build_status(
    output_dir=stale_dir,
    status='no-owner-packet',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    sent_date='2026-06-21',
    response_due_date='2026-06-24',
    status_date='2026-06-25',
    attempt_count=2,
    overwrite=True,
    **context_for('no-owner-packet', reask_source),
)
if not result.get('ok'):
    fail(f'overwrite status did not build: {result}')
if (stale_dir / 'SENT-AWAITING-REPLY.md').exists() or (stale_dir / 'nested').exists():
    fail('overwrite should remove stale files and directories before writing the new status')
if not (stale_dir / 'NO-OWNER-PACKET-OUTCOME.md').exists():
    fail('overwrite should leave only the new status note and manifest')

blocked = build_status(
    output_dir=ROOT / 'docs' / 'bad-owner-contact-status',
    status='sent-awaiting-reply',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    sent_date='2026-06-13',
    response_due_date='2026-06-20',
    status_date='2026-06-13',
    attempt_count=1,
    **context_for('sent-awaiting-reply', send_log_source),
)
if blocked.get('ok') or blocked.get('error') != 'OWNER-CONTACT-OUTPUT-BLOCKED':
    fail('archive-controlled docs output should be blocked')

blocked = build_status(
    output_dir=TMP / 'blocked-arg',
    status='sent-awaiting-reply',
    service_label='AIEDU-SR-003 draft reminder pilot with student name list',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    sent_date='2026-06-13',
    response_due_date='2026-06-20',
    status_date='2026-06-13',
    attempt_count=1,
    **context_for('sent-awaiting-reply', send_log_source),
)
if blocked.get('ok') or blocked.get('error') != 'OWNER-CONTACT-ARG-BLOCKED':
    fail('forbidden argument should be blocked')

blocked = build_status(
    output_dir=TMP / 'blocked-clock',
    status='sent-awaiting-reply',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    sent_date='2026-06-20',
    response_due_date='2026-06-13',
    status_date='2026-06-20',
    attempt_count=1,
    **context_for('sent-awaiting-reply', send_log_source),
)
if blocked.get('ok') or blocked.get('error') != 'OWNER-CONTACT-CLOCK-BLOCKED':
    fail('due date before sent date should be blocked')

blocked = build_status(
    output_dir=TMP / 'blocked-confirmation',
    status='sent-awaiting-reply',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    sent_date='2026-06-13',
    response_due_date='2026-06-20',
    status_date='2026-06-13',
    attempt_count=1,
    operator_confirmation='copied-command-without-human-send',
    source_artifact='scratch/field/ft0181/owner-request-packets/p1/packet-manifest.json',
)
if blocked.get('ok') or blocked.get('error') != 'OWNER-CONTACT-CONFIRMATION-BLOCKED':
    fail('wrong operator confirmation should be blocked')

blocked = build_status(
    output_dir=TMP / 'blocked-prepared-packet-source',
    status='sent-awaiting-reply',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    sent_date='2026-06-13',
    response_due_date='2026-06-20',
    status_date='2026-06-13',
    attempt_count=1,
    operator_confirmation=OPERATOR_CONFIRMATIONS['sent-awaiting-reply'],
    source_artifact=rel(packet_source),
)
if blocked.get('ok') or blocked.get('error') != 'OWNER-CONTACT-SOURCE-ARTIFACT-BLOCKED':
    fail('prepared packet manifest should not directly source a sent contact clock')

blocked = build_status(
    output_dir=TMP / 'blocked-source',
    status='sent-awaiting-reply',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    sent_date='2026-06-13',
    response_due_date='2026-06-20',
    status_date='2026-06-13',
    attempt_count=1,
    operator_confirmation=OPERATOR_CONFIRMATIONS['sent-awaiting-reply'],
    source_artifact='',
)
if blocked.get('ok') or blocked.get('error') != 'OWNER-CONTACT-CONFIRMATION-BLOCKED':
    fail('missing source artifact should be blocked')

blocked = build_status(
    output_dir=TMP / 'blocked-phantom-source',
    status='sent-awaiting-reply',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    sent_date='2026-06-13',
    response_due_date='2026-06-20',
    status_date='2026-06-13',
    attempt_count=1,
    operator_confirmation=OPERATOR_CONFIRMATIONS['sent-awaiting-reply'],
    source_artifact='scratch/field/ft0181/owner-request-packets/missing/packet-manifest.json',
)
if blocked.get('ok') or blocked.get('error') != 'OWNER-CONTACT-SOURCE-ARTIFACT-BLOCKED':
    fail('phantom source artifact should be blocked')

blocked = build_status(
    output_dir=TMP / 'blocked-controlled-source',
    status='sent-awaiting-reply',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    sent_date='2026-06-13',
    response_due_date='2026-06-20',
    status_date='2026-06-13',
    attempt_count=1,
    operator_confirmation=OPERATOR_CONFIRMATIONS['sent-awaiting-reply'],
    source_artifact='examples/release-candidates/rev0275-external-data-gate.json',
)
if blocked.get('ok') or blocked.get('error') != 'OWNER-CONTACT-SOURCE-ARTIFACT-BLOCKED':
    fail('release-controlled source artifact should be blocked')

blocked = build_status(
    output_dir=TMP / 'blocked-early-reask-source',
    status='reask-awaiting-reply',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    sent_date='2026-06-21',
    response_due_date='2026-06-24',
    status_date='2026-06-21',
    attempt_count=2,
    **context_for('reask-awaiting-reply', future_sent_source),
)
if blocked.get('ok') or blocked.get('error') != 'OWNER-CONTACT-SOURCE-ARTIFACT-BLOCKED':
    fail('reask sourced from an open first clock should be blocked')

blocked = build_status(
    output_dir=TMP / 'blocked-early-no-owner',
    status='no-owner-packet',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    sent_date='2026-06-13',
    response_due_date='2026-06-20',
    status_date='2026-06-19',
    attempt_count=2,
    **context_for('no-owner-packet', reask_source),
)
if blocked.get('ok') or blocked.get('error') != 'OWNER-CONTACT-CLOCK-BLOCKED':
    fail('early no-owner-packet should be blocked')

blocked = build_status(
    output_dir=TMP / 'blocked-no-owner-source-mismatch',
    status='no-owner-packet',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    sent_date='2026-06-20',
    response_due_date='2026-06-23',
    status_date='2026-06-24',
    attempt_count=2,
    **context_for('no-owner-packet', reask_source),
)
if blocked.get('ok') or blocked.get('error') != 'OWNER-CONTACT-SOURCE-ARTIFACT-BLOCKED':
    fail('no-owner-packet must preserve the source reask clock dates')

blocked = build_status(
    output_dir=TMP / 'blocked-long-sent-clock',
    status='sent-awaiting-reply',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    sent_date='2026-06-13',
    response_due_date='2026-06-30',
    status_date='2026-06-13',
    attempt_count=1,
    **context_for('sent-awaiting-reply', send_log_source),
)
if blocked.get('ok') or blocked.get('error') != 'OWNER-CONTACT-CLOCK-BLOCKED':
    fail('sent status open-ended clock should be blocked')

blocked = build_status(
    output_dir=TMP / 'blocked-long-reask-clock',
    status='reask-awaiting-reply',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    sent_date='2026-06-21',
    response_due_date='2026-06-30',
    status_date='2026-06-21',
    attempt_count=2,
    **context_for('reask-awaiting-reply', sent_source),
)
if blocked.get('ok') or blocked.get('error') != 'OWNER-CONTACT-CLOCK-BLOCKED':
    fail('reask status open-ended clock should be blocked')

blocked = build_status(
    output_dir=TMP / 'blocked-reask-attempt',
    status='reask-awaiting-reply',
    service_label='AIEDU-SR-003 draft reminder pilot',
    owner_role='accountable service owner route',
    source_record_set='owner-maintained local service record set',
    date_range='2026-06-01 through 2026-06-07',
    sent_date='2026-06-21',
    response_due_date='2026-06-24',
    status_date='2026-06-21',
    attempt_count=1,
    **context_for('reask-awaiting-reply', sent_source),
)
if blocked.get('ok') or blocked.get('error') != 'OWNER-CONTACT-CLOCK-BLOCKED':
    fail('reask with one attempt should be blocked')

shutil.rmtree(TMP)
print('check_ft0181_owner_contact_status: OK (sent/reask/no-owner-packet status, operator confirmation guard, verified source trace, stale overwrite cleanup, output block, argument block, clock bounds, and no-owner source-clock matching)')
