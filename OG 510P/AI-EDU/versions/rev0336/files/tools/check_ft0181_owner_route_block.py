#!/usr/bin/env python3
"""Self-test the FT-0181 owner-route block recorder."""
from __future__ import annotations

import json
import shutil
from datetime import date
from pathlib import Path

from prepare_ft0181_owner_request_packet import build_packet
from record_ft0181_owner_route_block import OPERATOR_CONFIRMATION, build_route_block
from decide_ft0181_field_next_action import decision_for
from ft0181_field_guards import operator_today_iso, owner_route_block_integrity_error

ROOT = Path(__file__).resolve().parents[1]
SCRATCH = ROOT / 'scratch' / 'field' / 'ft0181' / 'validation' / 'ft0181-owner-route-block'


def fail(errors: list[str], msg: str) -> None:
    errors.append(msg)


def main() -> None:
    errors: list[str] = []
    today = operator_today_iso()
    if SCRATCH.exists():
        shutil.rmtree(SCRATCH)
    packet_out = SCRATCH / 'owner-request-packets' / 'p1'
    packet = build_packet(
        output_dir=packet_out,
        service_label='AIEDU-SR-003 draft reminder pilot',
        owner_role='accountable service owner',
        source_record_set='aggregate local service record set',
        date_range='2026 pilot-prep window',
        return_date='2026-06-23',
    )
    if not packet.get('ok'):
        fail(errors, f'packet build failed: {packet}')
    packet_manifest = packet_out / 'packet-manifest.json'

    blocked_out = SCRATCH / 'owner-route-blocks' / 'r1'
    blocked = build_route_block(
        output_dir=blocked_out,
        packet_manifest=packet_manifest,
        block_date=today,
        block_class='no-accountable-owner-route',
        service_label='AIEDU-SR-003 draft reminder pilot',
        owner_role='accountable service owner route',
        source_record_set='aggregate local service record set',
        date_range='2026 pilot-prep window',
        minimal_reason='route unavailable without storing contact details',
        operator_confirmation=OPERATOR_CONFIRMATION,
    )
    if not blocked.get('ok'):
        fail(errors, f'route block should record: {blocked}')
    manifest_path = blocked_out / 'route-block.json'
    note_path = blocked_out / 'OWNER-ROUTE-BLOCK.md'
    if not manifest_path.exists() or not note_path.exists():
        fail(errors, 'route block did not emit route-block.json and OWNER-ROUTE-BLOCK.md')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    for key, expected in {
        'route_block_type': 'FT-0181-owner-route-block',
        'followthrough_id': 'FT-0181',
        'block_state': 'ROUTE_BLOCKED_NO_SEND',
        'evidence_state': 'not_evidence',
        'source_truth_class': 'not_evidence',
        'closure_effect': 'does_not_close_ft0181',
        'public_claim_effect': 'none',
        'contact_status_effect': 'does_not_create_sent_or_reask_clock',
        'operator_confirmation': OPERATOR_CONFIRMATION,
    }.items():
        if manifest.get(key) != expected:
            fail(errors, f'{key} expected {expected!r}, found {manifest.get(key)!r}')
    for flag in [
        'source_packet_verified',
        'no_owner_contact_made',
        'no_send_log_created',
        'no_contact_details_stored',
        'no_raw_or_protected_material_stored',
        'no_widening_confirmation',
    ]:
        if manifest.get(flag) is not True:
            fail(errors, f'{flag} must be true')
    if owner_route_block_integrity_error(manifest, archive_root=ROOT):
        fail(errors, 'emitted route block should pass shared integrity guard')
    note = note_path.read_text(encoding='utf-8')
    for term in ['local non-evidence', 'not sent', 'no bounded accountable owner route', 'Do not invent a recipient', 'does not', 'close `FT-0181`']:
        if term not in note:
            fail(errors, f'route-block note missing boundary term: {term}')

    decision = decision_for(scratch_root=SCRATCH, returned_csv=None, as_of_date=today)
    if decision.get('outcome') != 'OWNER-ROUTE-BLOCK-RECORDED-NO-SEND':
        fail(errors, f'router should stop on latest route block, got {decision.get("outcome")}: {decision}')
    if 'send-log' in str(decision.get('recommended_command')).lower():
        fail(errors, 'router must not recommend send-log after a route block')

    fresh_scratch = SCRATCH / 'fresh-router'
    packet2_out = fresh_scratch / 'owner-request-packets' / 'p2'
    packet2 = build_packet(
        output_dir=packet2_out,
        service_label='AIEDU-SR-003 draft reminder pilot',
        owner_role='accountable service owner',
        source_record_set='aggregate local service record set',
        date_range='2026 pilot-prep window',
        return_date='2026-06-23',
    )
    if not packet2.get('ok'):
        fail(errors, f'packet2 build failed: {packet2}')
    fallback_decision = decision_for(scratch_root=fresh_scratch, returned_csv=None, as_of_date=today)
    fallback = fallback_decision.get('fallback_command_if_no_accountable_owner_route', '')
    if fallback_decision.get('outcome') != 'RECORD-SEND-LOG-AFTER-HUMAN-SEND':
        fail(errors, 'packet-only router should still prefer send-log after human send')
    if 'owner-route-block' not in fallback or 'human-confirmed-owner-route-block-no-send' not in fallback:
        fail(errors, f'packet-only router missing route-block fallback command: {fallback}')

    bad_confirm = build_route_block(
        output_dir=SCRATCH / 'bad-confirm',
        packet_manifest=packet_manifest,
        block_date=today,
        block_class='no-accountable-owner-route',
        service_label='AIEDU-SR-003 draft reminder pilot',
        owner_role='accountable service owner route',
        source_record_set='aggregate local service record set',
        date_range='2026 pilot-prep window',
        operator_confirmation='sent-anyway',
    )
    if bad_confirm.get('ok') or bad_confirm.get('error') != 'OWNER-ROUTE-BLOCK-CONFIRMATION-BLOCKED':
        fail(errors, 'bad operator confirmation should be blocked')

    bad_args = build_route_block(
        output_dir=SCRATCH / 'bad-args',
        packet_manifest=packet_manifest,
        block_date=today,
        block_class='no-accountable-owner-route',
        service_label='AIEDU-SR-003 draft reminder pilot',
        owner_role='owner@example.edu',
        source_record_set='aggregate local service record set',
        date_range='2026 pilot-prep window',
        operator_confirmation=OPERATOR_CONFIRMATION,
    )
    if bad_args.get('ok') or bad_args.get('error') != 'OWNER-ROUTE-BLOCK-ARG-BLOCKED':
        fail(errors, 'route block args with contact details should be blocked')

    bad_output = build_route_block(
        output_dir=ROOT / 'docs' / 'bad-route-block',
        packet_manifest=packet_manifest,
        block_date=today,
        block_class='no-accountable-owner-route',
        service_label='AIEDU-SR-003 draft reminder pilot',
        owner_role='accountable service owner route',
        source_record_set='aggregate local service record set',
        date_range='2026 pilot-prep window',
        operator_confirmation=OPERATOR_CONFIRMATION,
    )
    if bad_output.get('ok') or bad_output.get('error') != 'OWNER-ROUTE-BLOCK-OUTPUT-BLOCKED':
        fail(errors, 'route block output into archive docs should be blocked')

    not_packet = SCRATCH / 'not-packet.json'
    not_packet.write_text('{"not":"packet"}\n', encoding='utf-8')
    bad_packet = build_route_block(
        output_dir=SCRATCH / 'bad-packet',
        packet_manifest=not_packet,
        block_date=today,
        block_class='no-accountable-owner-route',
        service_label='AIEDU-SR-003 draft reminder pilot',
        owner_role='accountable service owner route',
        source_record_set='aggregate local service record set',
        date_range='2026 pilot-prep window',
        operator_confirmation=OPERATOR_CONFIRMATION,
    )
    if bad_packet.get('ok') or bad_packet.get('error') != 'OWNER-ROUTE-BLOCK-PACKET-BLOCKED':
        fail(errors, 'non-packet JSON should not source a route block')

    stale_path = blocked_out / 'STALE.txt'
    stale_path.write_text('stale local file', encoding='utf-8')
    overwritten = build_route_block(
        output_dir=blocked_out,
        packet_manifest=packet_manifest,
        block_date=today,
        block_class='owner-route-ambiguous',
        service_label='AIEDU-SR-003 draft reminder pilot',
        owner_role='accountable service owner route',
        source_record_set='aggregate local service record set',
        date_range='2026 pilot-prep window',
        minimal_reason='ambiguous route class only',
        operator_confirmation=OPERATOR_CONFIRMATION,
        overwrite=True,
    )
    if not overwritten.get('ok'):
        fail(errors, f'overwrite should rebuild route-block directory: {overwritten}')
    if stale_path.exists():
        fail(errors, 'overwrite should remove stale route-block files')

    if errors:
        raise SystemExit('check_ft0181_owner_route_block errors:\n' + '\n'.join(errors))
    print('check_ft0181_owner_route_block: OK (route-block recorder, no-send boundary, router stop, fallback command, output/argument/source blocks, and overwrite cleanup)')


if __name__ == '__main__':
    main()
