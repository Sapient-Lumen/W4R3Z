#!/usr/bin/env python3
"""Validate the FT-0181 owner request packet prep lane."""
from __future__ import annotations

import csv
import json
import tempfile
from datetime import date
from pathlib import Path

from prepare_ft0181_owner_request_packet import build_packet

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_REVISION = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8')).get('revision')
EXPECTED_COLUMNS = [
    'row_id',
    'required_owner_reply',
    'owner_response',
    'local_only_check',
    'intake_note',
]
EXPECTED_ROW_IDS = [str(i) for i in range(1, 9)]
REQUIRED_EMAIL_TERMS = [
    'not a request for learner-level records',
    'raw LMS exports',
    'protected-status facts',
    'small-cell cuts',
    'NO-OWNER-PACKET',
    'not a mock',
]
REQUIRED_NO_PACKET_TERMS = [
    'NO-OWNER-PACKET',
    'not SRC2+',
    'not real pilot evidence',
    'Keep `FT-0181` live',
    'Do not widen the request',
]

REQUIRED_CHECKLIST_TERMS = [
    'PREPARED_NOT_SENT',
    'NO-OWNER-PACKET-YET',
    'not evidence',
    'does not close `FT-0181`',
    'make owner-field-next',
    'FIELD-NEXT-ACTION.md',
    'returned, owner-attested CSV',
    'FIELD-TEXTURE-MEMO.md',
]


def fail(errors: list[str], msg: str) -> None:
    errors.append(msg)


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        columns = reader.fieldnames or []
    return columns, rows


def main() -> None:
    errors: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / 'aiedu-sr-003-first-contact'
        result = build_packet(
            output_dir=out,
            service_label='AIEDU-SR-003 draft reminder pilot',
            owner_role='accountable service owner',
            source_record_set='aggregate local service record set',
            date_range='2026 pilot-prep window',
            return_date='2026-06-20',
        )
        if not result.get('ok'):
            fail(errors, f'packet build failed: {result}')
        if result.get('packet_state') != 'PREPARED_NOT_SENT':
            fail(errors, 'packet_state must be PREPARED_NOT_SENT')
        if result.get('evidence_state') != 'NO-OWNER-PACKET-YET':
            fail(errors, 'evidence_state must be NO-OWNER-PACKET-YET')
        if result.get('followthrough_id') != 'FT-0181':
            fail(errors, 'followthrough_id must be FT-0181')

        csv_path = out / 'AIEDU-SR-003-eight-row-owner-reply-template.csv'
        email_path = out / 'AIEDU-SR-003-owner-request-email.txt'
        checklist_path = out / 'SEND-CHECKLIST.md'
        no_packet_path = out / 'NO-OWNER-PACKET-NOTE.md'
        field_texture_path = out / 'FIELD-TEXTURE-MEMO.md'
        send_brief_path = out / 'SEND-NOW-BRIEF.md'
        manifest_path = out / 'packet-manifest.json'
        for path in [csv_path, email_path, checklist_path, no_packet_path, field_texture_path, send_brief_path, manifest_path]:
            if not path.exists():
                fail(errors, f'expected packet file missing: {path.name}')

        columns, rows = read_csv(csv_path)
        if columns != EXPECTED_COLUMNS:
            fail(errors, 'prepared CSV columns changed')
        if [row.get('row_id') for row in rows] != EXPECTED_ROW_IDS:
            fail(errors, 'prepared CSV row ids changed')
        if any(row.get('owner_response') for row in rows):
            fail(errors, 'prepared CSV must leave owner_response blank')

        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        if manifest.get('packet_version') != EXPECTED_REVISION:
            fail(errors, f'manifest packet_version must match current revision {EXPECTED_REVISION}')
        created_at = manifest.get('created_at_utc')
        if not isinstance(created_at, str) or not created_at.endswith('Z') or 'T' not in created_at:
            fail(errors, 'manifest must include created_at_utc as an ISO UTC timestamp ending in Z')
        operator_local_date = manifest.get('operator_local_date')
        if not isinstance(operator_local_date, str):
            fail(errors, 'manifest must include operator_local_date for field clock routing')
        else:
            try:
                date.fromisoformat(operator_local_date)
            except ValueError:
                fail(errors, 'manifest operator_local_date must be YYYY-MM-DD')
        if manifest.get('source_truth_class') != 'not_evidence':
            fail(errors, 'manifest must mark packet not_evidence')
        if manifest.get('closure_effect') != 'does_not_close_ft0181':
            fail(errors, 'manifest must not close FT-0181')
        exclusions = set(manifest.get('request_exclusions', []))
        for required in [
            'learner_identifiers',
            'raw_lms_exports',
            'protected_status_facts',
            'small_cell_cuts',
            'security_payloads_or_credentials',
            'vendor_dashboard_dumps',
        ]:
            if required not in exclusions:
                fail(errors, f'manifest missing exclusion: {required}')

        email = email_path.read_text(encoding='utf-8')
        for term in REQUIRED_EMAIL_TERMS:
            if term not in email:
                fail(errors, f'email missing boundary term: {term}')
        no_packet = no_packet_path.read_text(encoding='utf-8')
        for term in REQUIRED_NO_PACKET_TERMS:
            if term not in no_packet:
                fail(errors, f'no-packet note missing term: {term}')
        checklist = checklist_path.read_text(encoding='utf-8')
        for term in REQUIRED_CHECKLIST_TERMS:
            if term not in checklist:
                fail(errors, f'checklist missing term: {term}')
        no_packet_note = no_packet_path.read_text(encoding='utf-8')
        for term in ['NO-OWNER-PACKET', 'not SRC2+', 'not real pilot evidence', 'Do not widen the request', 'Keep `FT-0181` live']:
            if term not in no_packet_note:
                fail(errors, f'NO-OWNER-PACKET note missing term: {term}')
        if 'NO-OWNER-PACKET-NOTE.md' not in manifest.get('generated_files', []):
            fail(errors, 'manifest missing NO-OWNER-PACKET-NOTE.md generated file')
        if 'FIELD-TEXTURE-MEMO.md' not in manifest.get('generated_files', []):
            fail(errors, 'manifest missing FIELD-TEXTURE-MEMO.md generated file')
        if 'SEND-NOW-BRIEF.md' not in manifest.get('generated_files', []):
            fail(errors, 'manifest missing SEND-NOW-BRIEF.md generated file')
        field_texture = field_texture_path.read_text(encoding='utf-8')
        for term in ['LOCAL_FIELD_TEXTURE_NOT_EVIDENCE', 'not real pilot evidence', 'local learning only', 'must not copy recipient names', 'cannot be used as evidence', 'cannot support a public claim']:
            if term not in field_texture:
                fail(errors, f'field-texture memo missing term: {term}')
        send_brief = send_brief_path.read_text(encoding='utf-8')
        for term in ['OPERATOR_SEND_AID_NOT_EVIDENCE', 'Attach only', 'After the human send/adaptation is complete', 'make owner-route-block', 'human-confirmed-owner-route-block-no-send', 'make owner-after-human-send', 'PACKET=', 'CONFIRM=', 'send-log.json', 'SENT_AWAITING_REPLY', 'not real pilot evidence', 'does not prove', 'bounded no-owner-packet outcome']:
            if term not in send_brief:
                fail(errors, f'send-now brief missing term: {term}')
        manifest_commands = '\n'.join(manifest.get('next_commands', []))
        if 'owner-reply-intake-bundle.json' in checklist or 'owner-reply-intake-bundle.json' in manifest_commands:
            fail(errors, 'packet must pass the owner-reply intake bundle directory, not owner-reply-intake-bundle.json')
        if 'YYYY-MM-DD' in checklist or 'YYYY-MM-DD' in manifest_commands:
            fail(errors, 'packet checklist/manifest must route through owner-field-next instead of stale date placeholders')
        if 'make owner-field-next OUT=scratch/field/ft0181/ft0181-field-next-action/aiedu-sr-003-after-send' not in manifest_commands:
            fail(errors, 'manifest missing owner-field-next after-send router command')
        if 'make owner-field-next CSV=/path/to/returned-owner-reply.csv' not in manifest_commands:
            fail(errors, 'manifest missing returned CSV router command')
        router_outcomes = '\n'.join(manifest.get('router_expected_outcomes', []))
        for expected in ['make owner-route-block', 'ROUTE-BLOCK-RECORDED', 'make owner-after-human-send', 'PACKET', 'STATUS=sent-awaiting-reply', 'STATUS=reask-awaiting-reply', 'STATUS=no-owner-packet', 'CONFIRM', 'SOURCE_ARTIFACT', 'non-fixture returned CSV']:
            if expected not in router_outcomes:
                fail(errors, f'manifest router outcome note missing: {expected}')
        if 'make owner-reply-intake CSV=/path/to/returned-owner-reply.csv' in manifest_commands:
            fail(errors, 'manifest must not bypass returned-CSV router with direct intake command')
        if 'make owner-reply-workbench-seed BUNDLE=' in manifest_commands:
            fail(errors, 'manifest must not bypass after-intake router with direct workbench seed command')
        if 'make owner-field-next OUT=scratch/field/ft0181/ft0181-field-next-action/after-intake' not in manifest_commands:
            fail(errors, 'manifest missing after-intake router command')

        second = build_packet(
            output_dir=out,
            service_label='AIEDU-SR-003 draft reminder pilot',
            owner_role='accountable service owner',
            source_record_set='aggregate local service record set',
            date_range='2026 pilot-prep window',
            return_date='2026-06-20',
        )
        if second.get('ok') or second.get('error') != 'OWNER-REQUEST-OUTPUT-EXISTS':
            fail(errors, 'existing non-empty output should be blocked')

        stale_path = out / 'STALE.txt'
        stale_path.write_text('stale local file', encoding='utf-8')
        overwritten = build_packet(
            output_dir=out,
            service_label='AIEDU-SR-003 draft reminder pilot',
            owner_role='accountable service owner',
            source_record_set='aggregate local service record set',
            date_range='2026 pilot-prep window',
            return_date='2026-06-21',
            overwrite=True,
        )
        if not overwritten.get('ok'):
            fail(errors, f'overwrite should rebuild packet directory: {overwritten}')
        if stale_path.exists():
            fail(errors, 'overwrite should remove stale packet directory files')

        arg_blocked = build_packet(
            output_dir=Path(tmp) / 'blocked-args',
            service_label='AIEDU-SR-003 raw LMS export request',
            owner_role='accountable service owner',
            source_record_set='aggregate local service record set',
            date_range='2026 pilot-prep window',
            return_date='2026-06-20',
        )
        if arg_blocked.get('ok') or arg_blocked.get('error') != 'OWNER-REQUEST-ARG-BLOCKED':
            fail(errors, 'forbidden first-contact arguments should be blocked')


        bad_args = build_packet(
            output_dir=Path(tmp) / 'bad-args',
            service_label='AIEDU-SR-003 draft reminder pilot',
            owner_role='accountable service owner',
            source_record_set='raw LMS export with student id rows',
            date_range='2026 pilot-prep window',
            return_date='2026-06-20',
        )
        if bad_args.get('ok') or bad_args.get('error') != 'OWNER-REQUEST-ARG-BLOCKED':
            fail(errors, 'forbidden first-contact argument terms should be blocked')

        blocked = build_packet(
            output_dir=ROOT / 'docs' / 'owner-request-packets' / 'bad',
            service_label='AIEDU-SR-003 draft reminder pilot',
            owner_role='accountable service owner',
            source_record_set='aggregate local service record set',
            date_range='2026 pilot-prep window',
            return_date='2026-06-20',
        )
        if blocked.get('ok') or blocked.get('error') != 'OWNER-REQUEST-OUTPUT-BLOCKED':
            fail(errors, 'archive-controlled output should be blocked')

    if errors:
        raise SystemExit('FT-0181 owner request packet validation errors:\n' + '\n'.join(errors))
    print('check_ft0181_owner_request_packet: OK')


if __name__ == '__main__':
    main()
