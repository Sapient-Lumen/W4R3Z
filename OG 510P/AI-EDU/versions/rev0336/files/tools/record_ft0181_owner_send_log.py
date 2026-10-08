#!/usr/bin/env python3
"""Record a minimal local FT-0181 owner-send log.

This utility sits between packet prep and contact-status recording. It does not
send mail, store recipients, copy owner answers, import evidence, or close
FT-0181. It only records that a human operator asserts the bounded packet was
sent or adapted through a class of local owner route, so a later SENT clock is
sourced from a distinct local send artifact rather than from a prepared packet.
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
    owner_send_log_integrity_error,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / 'scratch' / 'field' / 'ft0181' / 'owner-send-logs' / 'aiedu-sr-003'

OPERATOR_CONFIRMATION = 'human-sent-bounded-owner-request'
FIRST_CONTACT_MAX_DAYS = 7
SEND_CHANNEL_CLASSES = {
    'email',
    'ticket',
    'form',
    'delegated-local-route',
    'other-bounded-route',
}
OWNER_ROUTE_CLASSES = {
    'accountable-owner',
    'delegated-local-owner-route',
    'governance-intake',
    'other-bounded-owner-route',
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
    parser = argparse.ArgumentParser(description='Record a local FT-0181 owner-send log without contact details or evidence effects.')
    parser.add_argument('--packet-manifest', required=True, help='Scratch packet-manifest.json produced by owner-request-packet.')
    parser.add_argument('--sent-date', required=True, help='Human send/adaptation date, YYYY-MM-DD.')
    parser.add_argument('--response-due-date', required=True, help='Local response-clock due date, YYYY-MM-DD.')
    parser.add_argument('--output-dir', default=str(DEFAULT_OUTPUT), help='Local/scratch output directory for the send log.')
    parser.add_argument('--service-label', default='AIEDU-SR-003 draft reminder pilot', help='Non-sensitive service label.')
    parser.add_argument('--owner-role', default='accountable service owner route', help='Role/contact path class, not a person name or address.')
    parser.add_argument('--source-record-set', default='owner-maintained local service record set', help='Aggregate source record-set label.')
    parser.add_argument('--date-range', default='owner-named date boundary', help='Aggregate date/date-range boundary.')
    parser.add_argument('--send-channel-class', choices=sorted(SEND_CHANNEL_CLASSES), default='email', help='Class of send route; do not include recipient or platform details.')
    parser.add_argument('--owner-route-class', choices=sorted(OWNER_ROUTE_CLASSES), default='accountable-owner', help='Class of accountable owner route; do not include recipient or contact details.')
    parser.add_argument('--adapted-from-packet', action='store_true', help='Set when the human sent an adapted but still bounded version of the generated packet.')
    parser.add_argument('--operator-confirmation', required=True, help=f'Must be {OPERATOR_CONFIRMATION!r}; local assertion only, not evidence.')
    parser.add_argument('--minimal-send-note', default='', help='Optional local note class only; no names, addresses, owner answers, or raw/protected facts.')
    parser.add_argument('--overwrite', action='store_true', help='Replace an existing send-log directory.')
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


def resolve_packet_manifest(packet_manifest: str | Path) -> Path:
    candidate = Path(packet_manifest)
    if candidate.is_absolute():
        return candidate
    return ROOT / candidate


def validate_packet_manifest(packet_manifest: Path) -> tuple[bool, str, dict[str, Any] | None]:
    resolved = packet_manifest.resolve()
    inside, parts = archive_relative(resolved, archive_root=ROOT)
    if not inside or not parts or parts[0] != 'scratch':
        return False, 'packet-manifest must resolve under archive scratch/', None
    lane_error = field_scratch_lane_error(resolved, archive_root=ROOT, field_name='packet-manifest')
    if lane_error:
        return False, lane_error, None
    if resolved.name != 'packet-manifest.json' or not resolved.exists() or not resolved.is_file():
        return False, 'packet-manifest must point to an existing scratch packet-manifest.json file', None
    data = load_json(resolved)
    if data is None:
        return False, 'packet-manifest is not readable JSON', None
    error = owner_request_packet_integrity_error(data)
    if error:
        return False, f'packet-manifest failed integrity checks: {error}', data
    return True, 'packet-manifest-ok', data


def send_note(manifest: dict[str, Any]) -> str:
    return f"""# FT-0181 owner send log

Send-log state: `LOCAL_SEND_LOG_NOT_EVIDENCE`
Evidence state: `not_evidence`
Closure effect: `does_not_close_ft0181`
Service: `{manifest['service_label']}`
Packet manifest: `{manifest['packet_manifest_ref']}`
Sent date: `{manifest['sent_date']}`
Response due date: `{manifest['response_due_date']}`
Send channel class: `{manifest['send_channel_class']}`
Owner route class: `{manifest['owner_route_class']}`
Adapted from generated packet: `{manifest['adapted_from_packet']}`

This log is a local operator assertion that the bounded packet was sent or
adapted through a class of owner route. It stores no recipient name, address,
owner answer, learner record, protected fact, screenshot, transcript, dashboard,
credential, or raw export. It is not evidence and cannot close `FT-0181`.

## Next command

Run the field router and execute only the contact-status command it emits:

```bash
make owner-field-next OUT=scratch/field/ft0181/ft0181-field-next-action/after-send-log OVERWRITE=1
```

The router should now source `STATUS=sent-awaiting-reply` from this
`send-log.json`, not directly from the prepared packet manifest.
"""


def build_send_log(
    *,
    output_dir: Path,
    packet_manifest: Path,
    sent_date: str,
    response_due_date: str,
    service_label: str,
    owner_role: str,
    source_record_set: str,
    date_range: str,
    send_channel_class: str,
    owner_route_class: str,
    adapted_from_packet: bool = False,
    operator_confirmation: str,
    minimal_send_note: str = '',
    overwrite: bool = False,
) -> dict[str, Any]:
    forbidden = argument_boundary_error(
        service_label,
        owner_role,
        source_record_set,
        date_range,
        send_channel_class,
        owner_route_class,
        minimal_send_note,
        packet_manifest.as_posix(),
    )
    if forbidden:
        return {
            'ok': False,
            'error': 'OWNER-SEND-LOG-ARG-BLOCKED',
            'reason': f'argument includes forbidden send-log term: {forbidden}',
            'state': 'NOT_RECORDED',
            'output_dir': str(output_dir),
        }
    allowed, output_boundary = output_allowed(output_dir, archive_root=ROOT)
    if not allowed:
        return {
            'ok': False,
            'error': 'OWNER-SEND-LOG-OUTPUT-BLOCKED',
            'reason': output_boundary,
            'state': 'NOT_RECORDED',
            'output_dir': str(output_dir),
        }
    if operator_confirmation.strip() != OPERATOR_CONFIRMATION:
        return {
            'ok': False,
            'error': 'OWNER-SEND-LOG-CONFIRMATION-BLOCKED',
            'reason': f'operator-confirmation must be {OPERATOR_CONFIRMATION!r}',
            'state': 'NOT_RECORDED',
            'output_dir': str(output_dir),
        }
    if send_channel_class not in SEND_CHANNEL_CLASSES:
        return {
            'ok': False,
            'error': 'OWNER-SEND-LOG-CHANNEL-BLOCKED',
            'reason': f'send-channel-class must be one of {sorted(SEND_CHANNEL_CLASSES)}',
            'state': 'NOT_RECORDED',
            'output_dir': str(output_dir),
        }
    if owner_route_class not in OWNER_ROUTE_CLASSES:
        return {
            'ok': False,
            'error': 'OWNER-SEND-LOG-ROUTE-BLOCKED',
            'reason': f'owner-route-class must be one of {sorted(OWNER_ROUTE_CLASSES)}',
            'state': 'NOT_RECORDED',
            'output_dir': str(output_dir),
        }
    try:
        sent = parse_iso_date(sent_date, 'sent-date')
        due = parse_iso_date(response_due_date, 'response-due-date')
    except ValueError as exc:
        return {
            'ok': False,
            'error': 'OWNER-SEND-LOG-CLOCK-BLOCKED',
            'reason': str(exc),
            'state': 'NOT_RECORDED',
            'output_dir': str(output_dir),
        }
    if due < sent:
        return {
            'ok': False,
            'error': 'OWNER-SEND-LOG-CLOCK-BLOCKED',
            'reason': 'response-due-date must be on or after sent-date',
            'state': 'NOT_RECORDED',
            'output_dir': str(output_dir),
        }
    if (due - sent).days > FIRST_CONTACT_MAX_DAYS:
        return {
            'ok': False,
            'error': 'OWNER-SEND-LOG-CLOCK-BLOCKED',
            'reason': f'first owner response clock cannot exceed {FIRST_CONTACT_MAX_DAYS} days from sent-date',
            'state': 'NOT_RECORDED',
            'output_dir': str(output_dir),
        }
    packet_path = packet_manifest.resolve()
    packet_ok, packet_reason, packet_data = validate_packet_manifest(packet_path)
    if not packet_ok or packet_data is None:
        return {
            'ok': False,
            'error': 'OWNER-SEND-LOG-PACKET-BLOCKED',
            'reason': packet_reason,
            'state': 'NOT_RECORDED',
            'output_dir': str(output_dir),
        }
    if output_dir.exists() and any(output_dir.iterdir()):
        if not overwrite:
            return {
                'ok': False,
                'error': 'OWNER-SEND-LOG-OUTPUT-EXISTS',
                'reason': 'use --overwrite or choose an empty directory',
                'state': 'NOT_RECORDED',
                'output_dir': str(output_dir),
            }
        for child in output_dir.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    output_dir.mkdir(parents=True, exist_ok=True)
    created = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    manifest: dict[str, Any] = {
        'send_log_type': 'FT-0181-owner-send-log',
        'send_log_version': 'rev0275',
        'followthrough_id': 'FT-0181',
        'service_record_id': 'AIEDU-SR-003',
        'service_label': service_label,
        'owner_role_class': owner_role,
        'source_record_set': source_record_set,
        'date_range': date_range,
        'packet_manifest_ref': archive_ref(packet_path),
        'packet_manifest_created_at_utc': packet_data.get('created_at_utc'),
        'sent_date': sent.isoformat(),
        'response_due_date': due.isoformat(),
        'max_response_clock_days': FIRST_CONTACT_MAX_DAYS,
        'send_channel_class': send_channel_class,
        'owner_route_class': owner_route_class,
        'adapted_from_packet': bool(adapted_from_packet),
        'operator_confirmation': OPERATOR_CONFIRMATION,
        'minimal_send_note': minimal_send_note or 'bounded packet sent/adapted without storing recipient details or owner answers',
        'evidence_state': 'not_evidence',
        'source_truth_class': 'not_evidence',
        'closure_effect': 'does_not_close_ft0181',
        'public_claim_effect': 'none',
        'contact_status_effect': 'may_source_sent_awaiting_reply_clock_only',
        'no_contact_details_stored': True,
        'no_raw_or_protected_material_stored': True,
        'no_widening_confirmation': True,
        'local_only': True,
        'created_at_utc': created,
        'output_boundary': output_boundary,
        'generated_files': ['send-log.json', 'SEND-LOG.md'],
        'allowed_next_commands': [
            'make owner-field-next OUT=scratch/field/ft0181/ft0181-field-next-action/after-send-log OVERWRITE=1',
            'then run only the emitted make owner-contact-status command',
        ],
        'forbidden_effects': [
            'does_not_send_email',
            'does_not_store_recipient_details',
            'does_not_import_owner_answers',
            'does_not_upgrade_to_SRC2+',
            'does_not_close_FT-0181',
            'does_not_support_public_claims',
            'does_not_create_an_open_ended_wait_clock',
        ],
    }
    integrity_error = owner_send_log_integrity_error(manifest, archive_root=ROOT)
    if integrity_error:
        return {
            'ok': False,
            'error': 'OWNER-SEND-LOG-INTEGRITY-BLOCKED',
            'reason': integrity_error,
            'state': 'NOT_RECORDED',
            'output_dir': str(output_dir),
        }
    (output_dir / 'send-log.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    (output_dir / 'SEND-LOG.md').write_text(send_note(manifest), encoding='utf-8')
    return {
        'ok': True,
        'state': 'LOCAL_SEND_LOG_NOT_EVIDENCE',
        'output_dir': str(output_dir),
        'manifest': str(output_dir / 'send-log.json'),
        'note': str(output_dir / 'SEND-LOG.md'),
        'next_action': 'run_owner_field_next_to_record_sent_clock_from_send_log',
        'evidence_effect': 'none',
        'closure_effect': 'does_not_close_ft0181',
    }


def main() -> None:
    args = parse_args()
    result = build_send_log(
        output_dir=Path(args.output_dir),
        packet_manifest=resolve_packet_manifest(args.packet_manifest),
        sent_date=args.sent_date,
        response_due_date=args.response_due_date,
        service_label=args.service_label,
        owner_role=args.owner_role,
        source_record_set=args.source_record_set,
        date_range=args.date_range,
        send_channel_class=args.send_channel_class,
        owner_route_class=args.owner_route_class,
        adapted_from_packet=args.adapted_from_packet,
        operator_confirmation=args.operator_confirmation,
        minimal_send_note=args.minimal_send_note,
        overwrite=args.overwrite,
    )
    if args.json:
        print(json.dumps(result, indent=2))
    elif result.get('ok'):
        print('record_ft0181_owner_send_log: OK (LOCAL_SEND_LOG_NOT_EVIDENCE)')
        print(f"manifest: {result['manifest']}")
        print(f"next_action: {result['next_action']}")
    else:
        raise SystemExit(f"record_ft0181_owner_send_log: {result.get('error')} ({result.get('reason')})")


if __name__ == '__main__':
    main()
