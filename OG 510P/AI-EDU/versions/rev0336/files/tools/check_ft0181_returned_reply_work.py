#!/usr/bin/env python3
"""Validate bounded FT-0181 returned-reply local work compression."""
from __future__ import annotations

import csv
import json
import shutil
import tempfile
from pathlib import Path

from prepare_ft0181_owner_request_packet import build_packet
from record_ft0181_owner_contact_status import OPERATOR_CONFIRMATIONS, build_status
from record_ft0181_owner_send_log import OPERATOR_CONFIRMATION as SEND_LOG_CONFIRMATION, build_send_log
from run_ft0181_returned_reply_work import build_returned_reply_work

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / 'scratch' / 'field' / 'ft0181' / 'validation' / 'ft0181-returned-reply-work'


def fail(msg: str) -> None:
    raise SystemExit(f'check_ft0181_returned_reply_work: FAIL: {msg}')


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def write_contact_status(path: Path) -> Path:
    packet_dir = TMP / 'source-artifacts' / 'owner-request-packets' / 'source-packet'
    packet = build_packet(
        output_dir=packet_dir,
        service_label='AIEDU-SR-003 draft reminder pilot',
        owner_role='accountable service owner route',
        source_record_set='owner-maintained local service record set',
        date_range='2026-06-01 through 2026-06-07',
        return_date='2026-06-23',
        overwrite=True,
    )
    if not packet.get('ok'):
        fail(f'contact-status source packet did not build: {packet}')
    send_dir = TMP / 'source-artifacts' / 'owner-send-logs' / 'source-send-log'
    send_log = build_send_log(
        output_dir=send_dir,
        packet_manifest=packet_dir / 'packet-manifest.json',
        sent_date='2026-06-16',
        response_due_date='2026-06-23',
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
        fail(f'contact-status source send-log did not build: {send_log}')
    status = build_status(
        output_dir=path.parent,
        status='sent-awaiting-reply',
        service_label='AIEDU-SR-003 draft reminder pilot',
        owner_role='accountable service owner route',
        source_record_set='owner-maintained local service record set',
        date_range='2026-06-01 through 2026-06-07',
        sent_date='2026-06-16',
        response_due_date='2026-06-23',
        status_date='2026-06-16',
        attempt_count=1,
        operator_confirmation=OPERATOR_CONFIRMATIONS['sent-awaiting-reply'],
        source_artifact=rel(send_dir / 'send-log.json'),
        overwrite=True,
    )
    if not status.get('ok'):
        fail(f'contact-status fixture did not build: {status}')
    return path


def write_owner_csv(path: Path, *, proceed: bool) -> Path:
    rows = [
        ['1', 'Selected service / owner path / source / date range', 'AIEDU-SR-003 draft reminder pilot; accountable owner route; owner-maintained local service record set; 2026 spring pilot.', 'no raw/protected data', ''],
        ['2', 'Aggregate workflow counts', '12 aggregate draft reminder candidates, 9 human reviewed, 0 automatic sends; no learner-level rows included.', 'aggregate only', ''],
        ['3', 'Action boundary', 'Draft queue note only; no automatic send; no durable write; no penalty and no grade effect; no protected status inference.', 'authority bounded', ''],
        ['4', 'Fallback / rollback / stop condition', 'Local owner can stop the workflow and roll back draft queue rules; human fallback exists.', 'local rollback owner', ''],
        ['5', 'Workload signal', 'Staff review burden observed as aggregate routing time only; no claim of workload reduction.', 'aggregate signal only', ''],
        ['6', 'Training or use guidance', 'Training guidance tells staff to review drafts manually and keep protected facts local.', 'guidance only', ''],
        ['7', 'Public claim ceiling', 'No claim of learning, safety, access, workload, compliance, scale, or effectiveness is supported.', 'claim ceiling', ''],
        ['8', 'Redaction and owner attestation', 'Owner attests this is real operational material with raw, protected, small-cell, and security material withheld and kept local.', 'redacted owner attestation', ''],
    ]
    if not proceed:
        rows[5][2] = ''
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as fh:
        writer = csv.writer(fh)
        writer.writerow(['row_id', 'required_owner_reply', 'owner_response', 'local_only_check', 'intake_note'])
        writer.writerows(rows)
    return path


if TMP.exists():
    shutil.rmtree(TMP)
TMP.mkdir(parents=True, exist_ok=True)
EXTERNAL_CSV_DIR = Path(tempfile.mkdtemp(prefix='ft0181-returned-reply-work-'))

contact = write_contact_status(TMP / 'owner-contact-status' / 'sent' / 'contact-status.json')
proceed_csv = write_owner_csv(EXTERNAL_CSV_DIR / 'aiedu-sr-003-owner-reply.csv', proceed=True)
result = build_returned_reply_work(
    csv_path=proceed_csv,
    source_contact_status=contact,
    output_dir=TMP / 'sessions' / 'proceed',
    intake_dir=TMP / 'owner-reply-intakes' / 'proceed',
    seed_dir=TMP / 'owner-reply-workbench-seeds' / 'proceed',
    review_brief_dir=TMP / 'owner-workbench-review-briefs' / 'proceed',
    overwrite=True,
)
if not result.get('ok'):
    fail(f'proceed returned-reply work should succeed: {result}')
if result.get('session_state') != 'review-brief-created-human-review-required':
    fail(f'proceed returned-reply work should create a review brief and then stop at human review: {result.get("session_state")}')
if result.get('evidence_effect') != 'not_evidence' or result.get('closure_effect') != 'does_not_close_ft0181' or result.get('public_claim_effect') != 'none':
    fail('returned-reply work must preserve no-evidence/no-closure/no-public-claim effects')
seed = result.get('seed_result') or {}
if seed.get('acceptance_state') != 'NOT_ACCEPTED':
    fail('workbench seed must remain NOT_ACCEPTED')
seed_path = ROOT / seed.get('seed_path', '')
if not seed_path.exists():
    fail('workbench seed file missing')
brief = result.get('review_brief_result') or {}
if brief.get('review_effect') != 'does_not_record_review':
    fail('returned-reply work must prepare only a review brief, not record human review')
brief_path = ROOT / brief.get('brief_path', '')
if not brief_path.exists():
    fail('review brief file missing')
session_path = ROOT / result.get('session_artifact', '')
if not session_path.exists():
    fail('session artifact missing')
session_text = session_path.read_text(encoding='utf-8') + '\n' + brief_path.read_text(encoding='utf-8')
for forbidden in ['Draft queue note only', 'Owner attests this is real operational material']:
    if forbidden in session_text:
        fail('session manifest/review brief must not copy raw/minimized owner answers: ' + forbidden)

reask_csv = write_owner_csv(EXTERNAL_CSV_DIR / 'aiedu-sr-003-owner-reply-reask.csv', proceed=False)
reask = build_returned_reply_work(
    csv_path=reask_csv,
    source_contact_status=contact,
    output_dir=TMP / 'sessions' / 'reask',
    intake_dir=TMP / 'owner-reply-intakes' / 'reask',
    seed_dir=TMP / 'owner-reply-workbench-seeds' / 'reask',
    overwrite=True,
)
if not reask.get('ok'):
    fail(f'non-proceed intake should still complete local routing: {reask}')
if reask.get('session_state') != 'intake-routed-non-proceed':
    fail('non-proceed CSV must not create a workbench seed')
if reask.get('seed_result') is not None:
    fail('non-proceed session must leave seed_result empty')
if (TMP / 'owner-reply-workbench-seeds' / 'reask' / 'workbench-seed.json').exists():
    fail('non-proceed session wrote a seed unexpectedly')

blocked = build_returned_reply_work(
    csv_path=ROOT / 'fixtures' / 'owner-reply-pipeline' / 'ft0181-proceed-staged-smoke.csv',
    source_contact_status=contact,
    output_dir=TMP / 'sessions' / 'fixture-block',
    intake_dir=TMP / 'owner-reply-intakes' / 'fixture-block',
    seed_dir=TMP / 'owner-reply-workbench-seeds' / 'fixture-block',
    overwrite=True,
)
if blocked.get('ok') is not False or blocked.get('outcome') != 'RETURNED-REPLY-WORK-INTAKE-BLOCKED':
    fail(f'archive-controlled smoke fixture must be blocked by returned-reply work: {blocked}')
if (TMP / 'owner-reply-workbench-seeds' / 'fixture-block' / 'workbench-seed.json').exists():
    fail('blocked fixture path must not write a seed')

missing_provenance = build_returned_reply_work(
    csv_path=proceed_csv,
    output_dir=TMP / 'sessions' / 'missing-provenance',
    overwrite=True,
)
if missing_provenance.get('ok') is not False or missing_provenance.get('outcome') != 'RETURNED-REPLY-WORK-SOURCE-PROVENANCE-BLOCKED':
    fail('returned-reply work must require exactly one provenance source')

shutil.rmtree(EXTERNAL_CSV_DIR, ignore_errors=True)
shutil.rmtree(TMP, ignore_errors=True)
print('check_ft0181_returned_reply_work: OK')
