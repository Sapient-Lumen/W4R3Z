#!/usr/bin/env python3
"""Record a local FT-0181 owner-route block before any send.

This utility covers the field-execution gap where a packet exists but no real
accountable owner route can be found. It does not send the packet, create a
contact clock, import owner evidence, close FT-0181, or support any public claim.
It only records a bounded local block so the operator does not fake a send log
or compensate with new doctrine.
"""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from ft0181_field_guards import (
    archive_relative,
    field_scratch_lane_error,
    output_allowed,
    owner_request_packet_integrity_error,
    operator_today_iso,
    owner_route_block_integrity_error,
)

ROOT = Path(__file__).resolve().parents[1]
REVISION = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8')).get('revision', 'unknown')
DEFAULT_OUTPUT = ROOT / 'scratch' / 'field' / 'ft0181' / 'owner-route-blocks' / 'aiedu-sr-003'

OPERATOR_CONFIRMATION = 'human-confirmed-owner-route-block-no-send'
BLOCK_CLASSES = {
    'no-accountable-owner-route',
    'owner-route-ambiguous',
    'owner-route-requires-authorization',
    'owner-route-wrong-domain',
    'owner-route-unavailable',
}
FORBIDDEN_TERMS = [
    'student id',
    'learner id',
    'student name',
    'learner name',
    'email address',
    '@',
    'raw lms export',
    'gradebook row',
    'screenshot',
    'chat transcript',
    'api key',
    'credential',
    'protected status',
    'disability facts',
    'accommodation facts',
    'discipline record',
    'safeguarding record',
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Record a local FT-0181 owner-route block without sending or storing contact details.')
    parser.add_argument('--packet-manifest', required=True, help='Scratch packet-manifest.json produced by owner-request-packet.')
    parser.add_argument('--block-date', default='', help='Date the route block was determined, YYYY-MM-DD; defaults to today.')
    parser.add_argument('--block-class', choices=sorted(BLOCK_CLASSES), default='no-accountable-owner-route', help='Bounded route-block class; do not include names or contact details.')
    parser.add_argument('--output-dir', default=str(DEFAULT_OUTPUT), help='Local/scratch output directory for the route-block record.')
    parser.add_argument('--service-label', default='AIEDU-SR-003 draft reminder pilot', help='Non-sensitive service label.')
    parser.add_argument('--owner-role', default='accountable service owner route', help='Role/contact path class, not a person name or address.')
    parser.add_argument('--source-record-set', default='owner-maintained local service record set', help='Aggregate source record-set label.')
    parser.add_argument('--date-range', default='owner-named date boundary', help='Aggregate date/date-range boundary.')
    parser.add_argument('--minimal-reason', default='', help='Optional local reason class only; no names, addresses, owner answers, or raw/protected facts.')
    parser.add_argument('--operator-confirmation', required=True, help=f'Must be {OPERATOR_CONFIRMATION!r}; local assertion only, not evidence.')
    parser.add_argument('--overwrite', action='store_true', help='Replace an existing route-block directory.')
    parser.add_argument('--json', action='store_true', help='Print machine-readable result.')
    return parser.parse_args()


def parse_iso_date(value: str, field: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f'{field} must be YYYY-MM-DD') from exc


def argument_boundary_error(*values: str) -> str | None:
    combined = ' '.join(value for value in values if value).lower()
    for term in FORBIDDEN_TERMS:
        if term in combined:
            return term
    return None


def archive_ref(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def packet_created_date(packet: dict[str, Any]) -> date | None:
    operator_local = packet.get('operator_local_date')
    if isinstance(operator_local, str):
        try:
            return date.fromisoformat(operator_local)
        except ValueError:
            pass
    created = packet.get('created_at_utc')
    if not isinstance(created, str) or not created.endswith('Z'):
        return None
    try:
        return datetime.fromisoformat(created[:-1] + '+00:00').astimezone(timezone.utc).date()
    except ValueError:
        return None


def packet_boundary_error(packet_path: Path, packet: dict[str, Any], block_date: date) -> str | None:
    inside, parts = archive_relative(packet_path.resolve(), archive_root=ROOT)
    if not inside or not parts or parts[0] != 'scratch':
        return 'packet-manifest must resolve under archive scratch/'
    lane_error = field_scratch_lane_error(packet_path, archive_root=ROOT, field_name='packet-manifest')
    if lane_error:
        return lane_error
    if packet_path.name != 'packet-manifest.json' or not packet_path.exists() or not packet_path.is_file():
        return 'packet-manifest must point to an existing packet-manifest.json file'
    packet_error = owner_request_packet_integrity_error(packet)
    if packet_error:
        return f'packet-manifest failed packet integrity: {packet_error}'
    created = packet_created_date(packet)
    if created is not None and block_date < created:
        return 'block-date cannot precede packet operator-local creation date'
    return None


def route_block_note(*, manifest: dict[str, Any]) -> str:
    reason = manifest['minimal_reason'] or 'No accountable owner route was available for the bounded first-contact packet.'
    return f"""# FT-0181 owner-route block

| Field | Value |
|---|---|
| Route block state | `{manifest['block_state']}` |
| Evidence state | `{manifest['evidence_state']}` |
| Closure effect | `{manifest['closure_effect']}` |
| Service attempted | `{manifest['service_label']}` |
| Owner route attempted | `{manifest['owner_role_label']}` |
| Source/date boundary attempted | `{manifest['source_record_set_label']}; {manifest['date_range_label']}` |
| Packet manifest | `{manifest['packet_manifest_ref']}` |
| Block date | `{manifest['block_date']}` |
| Block class | `{manifest['block_class']}` |
| Operator confirmation | `{manifest['operator_confirmation']}` |
| Minimal reason | `{reason}` |
| Next action | `{manifest['next_action']}` |

## Boundary

This route-block record is local non-evidence. It records that the packet was
not sent because no bounded accountable owner route was available. It does not
upgrade source truth, open a contact clock, authorize an import, support a
public claim, or close `FT-0181`.

Do not invent a recipient, store contact details, broaden the request, create a
new registry/doctrine surface, or record a send log unless a real accountable
owner route later exists and a human actually sends or adapts the bounded packet.
"""


def build_route_block(
    *,
    output_dir: Path,
    packet_manifest: Path,
    block_date: str,
    block_class: str,
    service_label: str,
    owner_role: str,
    source_record_set: str,
    date_range: str,
    minimal_reason: str = '',
    operator_confirmation: str = '',
    overwrite: bool = False,
) -> dict[str, Any]:
    forbidden = argument_boundary_error(service_label, owner_role, source_record_set, date_range, minimal_reason, str(packet_manifest))
    if forbidden:
        return {
            'ok': False,
            'error': 'OWNER-ROUTE-BLOCK-ARG-BLOCKED',
            'reason': f'argument includes forbidden route-block term: {forbidden}',
            'state': 'NOT_RECORDED',
            'output_dir': str(output_dir),
        }
    allowed, output_boundary = output_allowed(output_dir, archive_root=ROOT)
    if not allowed:
        return {
            'ok': False,
            'error': 'OWNER-ROUTE-BLOCK-OUTPUT-BLOCKED',
            'reason': output_boundary,
            'state': 'NOT_RECORDED',
            'output_dir': str(output_dir),
        }
    if block_class not in BLOCK_CLASSES:
        return {
            'ok': False,
            'error': 'OWNER-ROUTE-BLOCK-CLASS-BLOCKED',
            'reason': f'block-class must be one of {sorted(BLOCK_CLASSES)}',
            'state': 'NOT_RECORDED',
            'output_dir': str(output_dir),
        }
    if operator_confirmation.strip() != OPERATOR_CONFIRMATION:
        return {
            'ok': False,
            'error': 'OWNER-ROUTE-BLOCK-CONFIRMATION-BLOCKED',
            'reason': f'operator-confirmation must be {OPERATOR_CONFIRMATION!r}',
            'state': 'NOT_RECORDED',
            'output_dir': str(output_dir),
        }
    try:
        recorded_date = parse_iso_date(block_date or operator_today_iso(), 'block-date')
    except ValueError as exc:
        return {
            'ok': False,
            'error': 'OWNER-ROUTE-BLOCK-DATE-BLOCKED',
            'reason': str(exc),
            'state': 'NOT_RECORDED',
            'output_dir': str(output_dir),
        }
    packet_path = packet_manifest if packet_manifest.is_absolute() else ROOT / packet_manifest
    packet = load_json(packet_path)
    if packet is None:
        return {
            'ok': False,
            'error': 'OWNER-ROUTE-BLOCK-PACKET-BLOCKED',
            'reason': 'packet-manifest is not readable JSON',
            'state': 'NOT_RECORDED',
            'output_dir': str(output_dir),
        }
    packet_error = packet_boundary_error(packet_path, packet, recorded_date)
    if packet_error:
        return {
            'ok': False,
            'error': 'OWNER-ROUTE-BLOCK-PACKET-BLOCKED',
            'reason': packet_error,
            'state': 'NOT_RECORDED',
            'output_dir': str(output_dir),
        }
    if output_dir.exists() and any(output_dir.iterdir()) and not overwrite:
        return {
            'ok': False,
            'error': 'OWNER-ROUTE-BLOCK-OUTPUT-EXISTS',
            'reason': 'use --overwrite or choose an empty directory',
            'state': 'NOT_RECORDED',
            'output_dir': str(output_dir),
        }
    if output_dir.exists() and overwrite:
        for child in output_dir.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    output_dir.mkdir(parents=True, exist_ok=True)

    created = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    packet_ref = archive_ref(packet_path)
    manifest_path = output_dir / 'route-block.json'
    note_path = output_dir / 'OWNER-ROUTE-BLOCK.md'
    manifest: dict[str, Any] = {
        'route_block_type': 'FT-0181-owner-route-block',
        'route_block_version': REVISION,
        'followthrough_id': 'FT-0181',
        'service_record_id': 'AIEDU-SR-003',
        'created_at_utc': created,
        'block_state': 'ROUTE_BLOCKED_NO_SEND',
        'block_date': recorded_date.isoformat(),
        'block_class': block_class,
        'evidence_state': 'not_evidence',
        'source_truth_class': 'not_evidence',
        'closure_effect': 'does_not_close_ft0181',
        'public_claim_effect': 'none',
        'contact_status_effect': 'does_not_create_sent_or_reask_clock',
        'service_label': service_label,
        'owner_role_label': owner_role,
        'source_record_set_label': source_record_set,
        'date_range_label': date_range,
        'minimal_reason': minimal_reason,
        'operator_confirmation': operator_confirmation,
        'packet_manifest_ref': packet_ref,
        'packet_requested_return_date': packet.get('requested_return_date'),
        'source_packet_verified': True,
        'output_boundary': output_boundary,
        'generated_files': [note_path.name, manifest_path.name],
        'no_owner_contact_made': True,
        'no_send_log_created': True,
        'no_contact_details_stored': True,
        'no_raw_or_protected_material_stored': True,
        'no_widening_confirmation': True,
        'next_action': 'keep_ft0181_live_until_real_accountable_owner_route_or_new_context',
        'allowed_next_commands': [
            'make owner-field-next OUT=scratch/field/ft0181/ft0181-field-next-action/after-route-block',
            'only start a new routed packet/send path if a real accountable owner route later exists',
        ],
        'forbidden_actions': [
            'record_send_log_without_human_send',
            'create_contact_clock_without_send_log',
            'invent_recipient_or_contact_details',
            'widen_owner_request_or_ask_for_raw_export',
            'upgrade_to_src2_from_route_block',
            'claim_real_pilot_evidence',
            'close_ft0181',
            'create_new_registry_or_doctrine_surface_to_replace_missing_owner_route',
        ],
    }
    integrity_error = owner_route_block_integrity_error(manifest, archive_root=ROOT)
    if integrity_error:
        return {
            'ok': False,
            'error': 'OWNER-ROUTE-BLOCK-INTEGRITY-BLOCKED',
            'reason': integrity_error,
            'state': 'NOT_RECORDED',
            'output_dir': str(output_dir),
        }
    note_path.write_text(route_block_note(manifest=manifest), encoding='utf-8')
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return {
        'ok': True,
        'route_block_state': manifest['block_state'],
        'evidence_state': manifest['evidence_state'],
        'followthrough_id': manifest['followthrough_id'],
        'output_dir': str(output_dir),
        'files': manifest['generated_files'],
        'manifest': manifest,
    }


def main() -> None:
    args = parse_args()
    result = build_route_block(
        output_dir=Path(args.output_dir),
        packet_manifest=Path(args.packet_manifest),
        block_date=args.block_date or operator_today_iso(),
        block_class=args.block_class,
        service_label=args.service_label,
        owner_role=args.owner_role,
        source_record_set=args.source_record_set,
        date_range=args.date_range,
        minimal_reason=args.minimal_reason,
        operator_confirmation=args.operator_confirmation,
        overwrite=args.overwrite,
    )
    if args.json:
        print(json.dumps(result, indent=2))
    elif result.get('ok'):
        print(
            'record_ft0181_owner_route_block: OK '
            f"({result['route_block_state']}, {result['evidence_state']}, {result['output_dir']})"
        )
    else:
        raise SystemExit(f"record_ft0181_owner_route_block: {result['error']} ({result['reason']})")


if __name__ == '__main__':
    main()
