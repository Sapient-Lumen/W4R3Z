#!/usr/bin/env python3
"""Record the guarded local FT-0181 state after an actual human owner send.

This utility compresses the post-send bookkeeping that previously required a
send-log command, a router rerun, and a contact-status command. It still requires
the human-send confirmation token and a scratch packet manifest. It does not
send mail, store recipients, import owner answers, create evidence, support a
public claim, or close FT-0181.
"""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from ft0181_field_guards import FIRST_CONTACT_MAX_DAYS, operator_today_iso, output_allowed
from record_ft0181_owner_contact_status import build_status
from record_ft0181_owner_send_log import OPERATOR_CONFIRMATION, build_send_log, resolve_packet_manifest

ROOT = Path(__file__).resolve().parents[1]
SERVICE_ID = 'aiedu-sr-003'
DEFAULT_SESSION_ROOT = ROOT / 'scratch' / 'field' / 'ft0181' / 'owner-after-human-send'


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='After a real human bounded owner send/adaptation, record the local send log and SENT_AWAITING_REPLY clock in one guarded step.'
    )
    parser.add_argument('--packet-manifest', required=True, help='Scratch packet-manifest.json produced by owner-request-packet/owner-field-work.')
    parser.add_argument('--sent-date', default=operator_today_iso(), help='Human send/adaptation date, YYYY-MM-DD. Defaults to the operator-local date (CUBE_AS_OF_DATE override, then CUBE_OPERATOR_TIMEZONE).')
    parser.add_argument('--response-due-date', default='', help=f'Local response-clock due date, YYYY-MM-DD. Defaults to sent-date + {FIRST_CONTACT_MAX_DAYS} days.')
    parser.add_argument('--status-date', default='', help='Date this local SENT clock is recorded. Defaults to sent-date.')
    parser.add_argument('--output-dir', default='', help='Local/scratch session output directory. Defaults to scratch/field/ft0181/owner-after-human-send/aiedu-sr-003-sent-<date>.')
    parser.add_argument('--send-log-dir', default='', help='Local/scratch send-log output directory. Defaults to scratch/field/ft0181/owner-send-logs/aiedu-sr-003-sent-<date>.')
    parser.add_argument('--contact-status-dir', default='', help='Local/scratch contact-status output directory. Defaults to scratch/field/ft0181/owner-contact-status/aiedu-sr-003-sent-<date>.')
    parser.add_argument('--service-label', default='AIEDU-SR-003 draft reminder pilot', help='Non-sensitive service label.')
    parser.add_argument('--owner-role', default='accountable service owner route', help='Role/contact path class, not a person name or address.')
    parser.add_argument('--source-record-set', default='owner-maintained local service record set', help='Aggregate source record-set label.')
    parser.add_argument('--date-range', default='owner-named date boundary', help='Aggregate date/date-range boundary.')
    parser.add_argument('--send-channel-class', default='email', help='Class of send route; do not include recipient or platform details.')
    parser.add_argument('--owner-route-class', default='accountable-owner', help='Class of accountable owner route; do not include recipient or contact details.')
    parser.add_argument('--adapted-from-packet', action='store_true', help='Set when the human sent an adapted but still bounded version of the generated packet.')
    parser.add_argument('--operator-confirmation', required=True, help=f'Must be {OPERATOR_CONFIRMATION!r}; local assertion only, not evidence.')
    parser.add_argument('--minimal-send-note', default='', help='Optional local route-class note only; no names, addresses, owner answers, or raw/protected facts.')
    parser.add_argument('--overwrite', action='store_true', help='Replace existing session/send-log/contact-status directories.')
    parser.add_argument('--json', action='store_true', help='Print machine-readable result.')
    return parser.parse_args()


def parse_iso(value: str, field: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f'{field} must be YYYY-MM-DD') from exc


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def defaulted_dirs(sent: date, *, output_dir: str, send_log_dir: str, contact_status_dir: str) -> tuple[Path, Path, Path]:
    slug = f'{SERVICE_ID}-sent-{sent.isoformat()}'
    session_dir = Path(output_dir) if output_dir else DEFAULT_SESSION_ROOT / slug
    send_dir = Path(send_log_dir) if send_log_dir else ROOT / 'scratch' / 'field' / 'ft0181' / 'owner-send-logs' / slug
    contact_dir = Path(contact_status_dir) if contact_status_dir else ROOT / 'scratch' / 'field' / 'ft0181' / 'owner-contact-status' / slug
    return session_dir, send_dir, contact_dir


def clean_or_block_output(path: Path, *, overwrite: bool) -> tuple[bool, str]:
    allowed, boundary = output_allowed(path, archive_root=ROOT)
    if not allowed:
        return False, boundary
    if path.exists() and any(path.iterdir()):
        if not overwrite:
            return False, 'use --overwrite or choose an empty directory'
        for child in path.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    path.mkdir(parents=True, exist_ok=True)
    return True, boundary


def session_markdown(manifest: dict[str, Any]) -> str:
    return f"""# FT-0181 after-human-send session

Session state: `{manifest['session_state']}`
Evidence effect: `{manifest['evidence_effect']}`
Closure effect: `{manifest['closure_effect']}`
Public claim effect: `{manifest['public_claim_effect']}`

This session records only local bookkeeping after an actual human send/adaptation
of the bounded first-contact packet. The operator confirmation is a local
assertion, not delivery evidence, owner evidence, custody, acceptance, public
support, or closure.

## Source packet

Packet manifest: `{manifest['packet_manifest_ref']}`

## Local records written

Send log: `{manifest['send_log_manifest_ref']}`
Contact status: `{manifest['contact_status_manifest_ref']}`
Sent date: `{manifest['sent_date']}`
Response due date: `{manifest['response_due_date']}`
Status date: `{manifest['status_date']}`

## Next action

Wait for a real returned owner CSV/source packet or rerun the router when the
bounded clock needs attention:

```bash
make owner-field-next OUT=scratch/field/ft0181/ft0181-field-next-action/after-sent-clock
```

If a real owner-attested CSV comes back, route it through the router first:

```bash
make owner-field-next CSV=/path/to/returned-owner-reply.csv OUT=scratch/field/ft0181/ft0181-field-next-action/returned-owner-reply
```

## Hard boundary

Do not paste recipient names, email addresses, owner answers, raw learner rows,
protected facts, screenshots, transcripts, vendor dashboards, credentials, or
small-cell material into this session. Do not create a second local status record
to postpone the no-owner-packet outcome; the router controls the bounded clock.
"""


def build_after_human_send(
    *,
    packet_manifest: Path,
    sent_date: str,
    response_due_date: str,
    status_date: str,
    output_dir: Path,
    send_log_dir: Path,
    contact_status_dir: Path,
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
    try:
        sent = parse_iso(sent_date, 'sent-date')
        due = parse_iso(response_due_date, 'response-due-date') if response_due_date else sent + timedelta(days=FIRST_CONTACT_MAX_DAYS)
        status = parse_iso(status_date, 'status-date') if status_date else sent
    except ValueError as exc:
        return {
            'ok': False,
            'error': 'AFTER-HUMAN-SEND-CLOCK-BLOCKED',
            'reason': str(exc),
            'state': 'NOT_RECORDED',
            'output_dir': str(output_dir),
        }
    if operator_confirmation.strip() != OPERATOR_CONFIRMATION:
        return {
            'ok': False,
            'error': 'AFTER-HUMAN-SEND-CONFIRMATION-BLOCKED',
            'reason': f'operator-confirmation must be {OPERATOR_CONFIRMATION!r}',
            'state': 'NOT_RECORDED',
            'output_dir': str(output_dir),
        }
    session_ok, session_boundary = clean_or_block_output(output_dir, overwrite=overwrite)
    if not session_ok:
        return {
            'ok': False,
            'error': 'AFTER-HUMAN-SEND-OUTPUT-BLOCKED',
            'reason': session_boundary,
            'state': 'NOT_RECORDED',
            'output_dir': str(output_dir),
        }

    send_result = build_send_log(
        output_dir=send_log_dir,
        packet_manifest=packet_manifest,
        sent_date=sent.isoformat(),
        response_due_date=due.isoformat(),
        service_label=service_label,
        owner_role=owner_role,
        source_record_set=source_record_set,
        date_range=date_range,
        send_channel_class=send_channel_class,
        owner_route_class=owner_route_class,
        adapted_from_packet=adapted_from_packet,
        operator_confirmation=operator_confirmation,
        minimal_send_note=minimal_send_note,
        overwrite=overwrite,
    )
    if not send_result.get('ok'):
        return {
            'ok': False,
            'error': 'AFTER-HUMAN-SEND-SEND-LOG-BLOCKED',
            'reason': send_result.get('reason'),
            'state': 'NOT_RECORDED',
            'output_dir': str(output_dir),
            'send_log_result': send_result,
        }

    send_log_manifest = Path(str(send_result['manifest']))
    contact_result = build_status(
        output_dir=contact_status_dir,
        status='sent-awaiting-reply',
        service_label=service_label,
        owner_role=owner_role,
        source_record_set=source_record_set,
        date_range=date_range,
        sent_date=sent.isoformat(),
        response_due_date=due.isoformat(),
        status_date=status.isoformat(),
        attempt_count=1,
        minimal_reason='Bounded owner request clock opened after human send/adaptation; no owner reply has been imported.',
        operator_confirmation=operator_confirmation,
        source_artifact=relative(send_log_manifest),
        overwrite=overwrite,
    )
    if not contact_result.get('ok'):
        return {
            'ok': False,
            'error': 'AFTER-HUMAN-SEND-CONTACT-STATUS-BLOCKED',
            'reason': contact_result.get('reason'),
            'state': 'PARTIAL_SEND_LOG_RECORDED_CONTACT_BLOCKED',
            'output_dir': str(output_dir),
            'send_log_result': send_result,
            'contact_result': contact_result,
        }

    contact_manifest = contact_status_dir / 'contact-status.json'
    created = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    session_manifest: dict[str, Any] = {
        'session_type': 'FT-0181-after-human-send-local-record',
        'session_version': json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8')).get('revision', 'unknown'),
        'followthrough_id': 'FT-0181',
        'service_record_id': 'AIEDU-SR-003',
        'session_state': 'SENT_CLOCK_RECORDED_AFTER_HUMAN_SEND',
        'created_at_utc': created,
        'sent_date': sent.isoformat(),
        'response_due_date': due.isoformat(),
        'status_date': status.isoformat(),
        'operator_confirmation': operator_confirmation,
        'packet_manifest_ref': relative(packet_manifest),
        'send_log_manifest_ref': relative(send_log_manifest),
        'contact_status_manifest_ref': relative(contact_manifest),
        'evidence_effect': 'not_evidence',
        'source_truth_class': 'not_evidence',
        'closure_effect': 'does_not_close_ft0181',
        'public_claim_effect': 'none',
        'contact_status': 'SENT_AWAITING_REPLY',
        'no_contact_details_stored': True,
        'no_raw_or_protected_material_stored': True,
        'no_widening_confirmation': True,
        'output_boundary': session_boundary,
        'generated_files': ['after-human-send-session.json', 'AFTER-HUMAN-SEND-SESSION.md'],
        'allowed_next_commands': [
            'make owner-field-next CSV=/path/to/returned-owner-reply.csv OUT=scratch/field/ft0181/ft0181-field-next-action/returned-owner-reply',
            'make owner-field-next OUT=scratch/field/ft0181/ft0181-field-next-action/after-sent-clock',
        ],
        'forbidden_effects': [
            'does_not_send_email',
            'does_not_store_recipient_details',
            'does_not_import_owner_answers',
            'does_not_upgrade_to_SRC2+',
            'does_not_close_FT-0181',
            'does_not_support_public_claims',
            'does_not_extend_bounded_contact_clock',
        ],
    }
    (output_dir / 'after-human-send-session.json').write_text(json.dumps(session_manifest, indent=2) + '\n', encoding='utf-8')
    (output_dir / 'AFTER-HUMAN-SEND-SESSION.md').write_text(session_markdown(session_manifest), encoding='utf-8')
    return {
        'ok': True,
        'state': session_manifest['session_state'],
        'output_dir': str(output_dir),
        'session_manifest': str(output_dir / 'after-human-send-session.json'),
        'session_note': str(output_dir / 'AFTER-HUMAN-SEND-SESSION.md'),
        'send_log_manifest': str(send_log_manifest),
        'contact_status_manifest': str(contact_manifest),
        'contact_status': session_manifest['contact_status'],
        'evidence_effect': 'none',
        'closure_effect': 'does_not_close_ft0181',
        'next_action': 'await_real_owner_reply_or_rerun_owner_field_next_when_clock_needs_attention',
    }


def main() -> None:
    args = parse_args()
    try:
        sent = parse_iso(args.sent_date, 'sent-date')
    except ValueError as exc:
        raise SystemExit(f'record_ft0181_owner_after_human_send: AFTER-HUMAN-SEND-CLOCK-BLOCKED ({exc})')
    output_dir, send_log_dir, contact_status_dir = defaulted_dirs(
        sent,
        output_dir=args.output_dir,
        send_log_dir=args.send_log_dir,
        contact_status_dir=args.contact_status_dir,
    )
    result = build_after_human_send(
        packet_manifest=resolve_packet_manifest(args.packet_manifest),
        sent_date=args.sent_date,
        response_due_date=args.response_due_date,
        status_date=args.status_date,
        output_dir=output_dir,
        send_log_dir=send_log_dir,
        contact_status_dir=contact_status_dir,
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
        print('record_ft0181_owner_after_human_send: OK (SENT_CLOCK_RECORDED_AFTER_HUMAN_SEND)')
        print(f"send_log: {result['send_log_manifest']}")
        print(f"contact_status: {result['contact_status_manifest']}")
        print(f"next_action: {result['next_action']}")
    else:
        raise SystemExit(f"record_ft0181_owner_after_human_send: {result.get('error')} ({result.get('reason')})")


if __name__ == '__main__':
    main()
