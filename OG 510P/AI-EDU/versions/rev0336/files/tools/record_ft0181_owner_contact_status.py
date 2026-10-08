#!/usr/bin/env python3
"""Record the local FT-0181 owner-contact clock state.

This utility is for the gap between preparing the AIEDU-SR-003 owner-request
packet and receiving a viable owner CSV. It records only local, non-evidence
status: sent/awaiting reply, one clarification sent, or NO-OWNER-PACKET after
the response clock. It does not send email, import evidence, close FT-0181, or
support any public claim.
"""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from ft0181_field_guards import field_scratch_lane_error, FIRST_CONTACT_MAX_DAYS, REASK_MAX_DAYS, archive_relative, operator_today_iso, output_allowed, owner_reask_log_integrity_error, owner_send_log_integrity_error

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / 'scratch' / 'field' / 'ft0181' / 'owner-contact-status' / 'aiedu-sr-003'

FORBIDDEN_TERMS = [
    'student id',
    'learner id',
    'student name',
    'learner name',
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
STATUS_CHOICES = {
    'sent-awaiting-reply': 'SENT_AWAITING_REPLY',
    'reask-awaiting-reply': 'REASK_AWAITING_REPLY',
    'no-owner-packet': 'NO_OWNER_PACKET',
}
OPERATOR_CONFIRMATIONS = {
    'sent-awaiting-reply': 'human-sent-bounded-owner-request',
    'reask-awaiting-reply': 'human-sent-bounded-reask',
    'no-owner-packet': 'bounded-clock-passed-no-viable-owner-packet',
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Record local FT-0181 owner-contact status without importing evidence.')
    parser.add_argument('--status', required=True, choices=sorted(STATUS_CHOICES), help='Current bounded owner-contact state.')
    parser.add_argument('--output-dir', default=str(DEFAULT_OUTPUT), help='Local/scratch output directory for the status note.')
    parser.add_argument('--service-label', default='AIEDU-SR-003 draft reminder pilot', help='Non-sensitive service label.')
    parser.add_argument('--owner-role', default='accountable service owner', help='Role/contact path, not learner data.')
    parser.add_argument('--source-record-set', default='owner-named local service record set', help='One aggregate source record-set label.')
    parser.add_argument('--date-range', default='owner-named reminder cycle or short date range', help='One date/date-range boundary.')
    parser.add_argument('--sent-date', required=True, help='Date the bounded request or clarification was sent, YYYY-MM-DD.')
    parser.add_argument('--response-due-date', required=True, help='Local response-clock due date, YYYY-MM-DD.')
    parser.add_argument('--status-date', default='', help='Date this status is recorded; defaults to today, YYYY-MM-DD.')
    parser.add_argument('--attempt-count', type=int, default=1, help='Bounded contact attempts used so far; max 2 for first ask plus one clarification.')
    parser.add_argument('--minimal-reason', default='', help='Short local reason for no-owner-packet or awaiting state; no raw/protected details.')
    parser.add_argument('--operator-confirmation', required=True, help='Status-specific local assertion token printed by the field router; not evidence.')
    parser.add_argument('--source-artifact', required=True, help='Relative local scratch artifact that caused this status route; no contact or learner details.')
    parser.add_argument('--overwrite', action='store_true', help='Replace an existing status directory.')
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


def validate_operator_confirmation(*, status: str, operator_confirmation: str, source_artifact: str) -> tuple[bool, str]:
    expected = OPERATOR_CONFIRMATIONS.get(status)
    if expected is None:
        return False, f'unknown status for operator confirmation: {status}'
    if operator_confirmation.strip() != expected:
        return False, f'operator-confirmation must be {expected!r} for {status}'
    if not source_artifact.strip():
        return False, 'source-artifact is required so contact status can be traced to a packet, prior clock, or intake bundle'
    forbidden = argument_boundary_error(source_artifact)
    if forbidden:
        return False, f'source-artifact includes forbidden local-status term: {forbidden}'
    return True, 'operator-confirmation-ok'




def load_json_artifact(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def source_artifact_path(source_artifact: str) -> Path:
    candidate = Path(source_artifact.strip())
    if candidate.is_absolute():
        return candidate
    return ROOT / candidate


def verify_source_artifact(
    *,
    status: str,
    source_artifact: str,
    sent_date: str,
    response_due_date: str,
    status_date: str,
    attempt_count: int,
) -> tuple[bool, str, str]:
    """Verify that SOURCE_ARTIFACT is an existing local scratch artifact.

    Rev0271 keeps SOURCE_ARTIFACT inspected and now requires the SENT clock to be
    sourced from a local send-log artifact rather than from the prepared packet.
    The recorder still cannot prove that an email was actually delivered or that
    an owner replied, but it can prevent a phantom path, release-controlled file,
    prepared-only packet, stale pre-packet note, or wrong artifact class from
    driving the local contact clock.
    """
    raw = source_artifact.strip()
    if not raw:
        return False, 'source-artifact is required', 'missing'
    resolved = source_artifact_path(raw).resolve()
    inside, parts = archive_relative(resolved, archive_root=ROOT)
    if not inside or not parts or parts[0] != 'scratch':
        return False, 'source-artifact must resolve to an existing file under archive scratch/', 'blocked-boundary'
    lane_error = field_scratch_lane_error(resolved, archive_root=ROOT, field_name='source-artifact')
    if lane_error:
        return False, lane_error, 'blocked-boundary'
    if not resolved.exists() or not resolved.is_file():
        return False, f'source-artifact does not exist as a file: {raw}', 'missing-file'
    data = load_json_artifact(resolved)
    if data is None:
        return False, f'source-artifact is not readable JSON: {raw}', 'bad-json'
    rel = '/'.join(parts)

    if status == 'sent-awaiting-reply':
        if not rel.startswith('scratch/field/ft0181/owner-send-logs/') and '/owner-send-logs/' not in rel:
            return False, 'sent-awaiting-reply source-artifact must be a local owner-send log', 'wrong-source-type'
        if resolved.name != 'send-log.json':
            return False, 'sent-awaiting-reply source-artifact must end with send-log.json', 'wrong-source-type'
        send_log_error = owner_send_log_integrity_error(data, archive_root=ROOT)
        if send_log_error:
            return False, f'sent source send log failed integrity checks: {send_log_error}', 'send-log'
        if data.get('sent_date') != sent_date:
            return False, 'sent source send-log sent_date must match contact status sent-date', 'send-log'
        if data.get('response_due_date') != response_due_date:
            return False, 'sent source send-log response_due_date must match contact status response-due-date', 'send-log'
        return True, 'verified local owner-send log', 'send-log'

    if status == 'reask-awaiting-reply':
        if not rel.startswith('scratch/field/ft0181/owner-reask-logs/') and '/owner-reask-logs/' not in rel:
            return False, 'reask-awaiting-reply source-artifact must be a local owner-reask log', 'wrong-source-type'
        if resolved.name != 'reask-log.json':
            return False, 'reask-awaiting-reply source-artifact must end with reask-log.json', 'wrong-source-type'
        reask_log_error = owner_reask_log_integrity_error(data, archive_root=ROOT)
        if reask_log_error:
            return False, f'reask source reask log failed integrity checks: {reask_log_error}', 'reask-log'
        if data.get('sent_date') != sent_date:
            return False, 'reask source reask-log sent_date must match contact status sent-date', 'reask-log'
        if data.get('response_due_date') != response_due_date:
            return False, 'reask source reask-log response_due_date must match contact status response-due-date', 'reask-log'
        return True, 'verified local owner-reask log', 'reask-log'

    if status == 'no-owner-packet':
        if resolved.name != 'contact-status.json':
            return False, 'no-owner-packet source-artifact must be a prior REASK contact-status.json', 'wrong-source-type'
        if data.get('contact_status') != 'REASK_AWAITING_REPLY':
            return False, 'no-owner-packet source contact status must be REASK_AWAITING_REPLY', 'contact-status'
        try:
            source_attempt = int(data.get('attempt_count') or 0)
        except (TypeError, ValueError):
            return False, 'no-owner-packet source contact status must have numeric attempt_count=2', 'contact-status'
        if source_attempt != 2:
            return False, 'no-owner-packet source contact status must have attempt_count=2', 'contact-status'
        source_due = str(data.get('response_due_date') or '')
        try:
            source_due_date = parse_iso_date(source_due, 'source response_due_date')
            recorded = parse_iso_date(status_date, 'status-date')
        except ValueError as exc:
            return False, str(exc), 'contact-status'
        if source_due_date > recorded:
            return False, 'no-owner-packet cannot be sourced from a REASK clock whose response due date has not passed', 'contact-status'
        if str(data.get('sent_date') or '') != sent_date:
            return False, 'no-owner-packet sent-date must match the source REASK contact status sent_date', 'contact-status'
        if source_due != response_due_date:
            return False, 'no-owner-packet response-due-date must match the source REASK contact status response_due_date', 'contact-status'
        return True, 'verified prior REASK_AWAITING_REPLY contact status', 'contact-status'

    return False, f'unknown contact status for source-artifact verification: {status}', 'unknown'

def validate_contact_clock(*, status: str, sent_date: str, response_due_date: str, status_date: str, attempt_count: int) -> tuple[bool, str]:
    try:
        sent = parse_iso_date(sent_date, 'sent-date')
        due = parse_iso_date(response_due_date, 'response-due-date')
        recorded = parse_iso_date(status_date, 'status-date')
    except ValueError as exc:
        return False, str(exc)
    if due < sent:
        return False, 'response-due-date must be on or after sent-date'
    if recorded < sent:
        return False, 'status-date must be on or after sent-date'
    if attempt_count < 1:
        return False, 'attempt-count must be at least 1'
    if attempt_count > 2:
        return False, 'attempt-count cannot exceed first ask plus one clarification'
    if status == 'sent-awaiting-reply' and attempt_count != 1:
        return False, 'sent-awaiting-reply requires attempt-count 1'
    if status == 'reask-awaiting-reply' and attempt_count != 2:
        return False, 'reask-awaiting-reply requires attempt-count 2'
    if status == 'no-owner-packet' and attempt_count != 2:
        return False, 'no-owner-packet requires attempt-count 2'
    max_days = FIRST_CONTACT_MAX_DAYS if status == 'sent-awaiting-reply' else REASK_MAX_DAYS
    if (due - sent).days > max_days:
        return False, f'{status} response clock cannot exceed {max_days} days from sent-date'
    if status == 'no-owner-packet' and recorded < due:
        return False, 'no-owner-packet cannot be recorded before the response-due-date'
    return True, 'clock-ok'


def note_filename(status: str) -> str:
    if status == 'no-owner-packet':
        return 'NO-OWNER-PACKET-OUTCOME.md'
    if status == 'reask-awaiting-reply':
        return 'REASK-AWAITING-REPLY.md'
    return 'SENT-AWAITING-REPLY.md'


def next_action_for(status: str) -> str:
    if status == 'no-owner-packet':
        return 'keep_ft0181_live_without_widening_or_closure_claim'
    if status == 'reask-awaiting-reply':
        return 'await_one_clarification_reply_then_stage_or_record_no_owner_packet'
    return 'await_owner_reply_or_record_no_owner_packet_after_clock'


def status_note(*, status: str, service_label: str, owner_role: str, source_record_set: str, date_range: str, sent_date: str, response_due_date: str, status_date: str, attempt_count: int, minimal_reason: str, operator_confirmation: str, source_artifact: str, source_artifact_type: str) -> str:
    display = STATUS_CHOICES[status]
    reason = minimal_reason or ('No viable owner packet returned after the bounded clock.' if status == 'no-owner-packet' else 'Bounded owner request clock is open.')
    return f"""# FT-0181 owner contact status

| Field | Value |
|---|---|
| Contact status | `{display}` |
| Evidence state | `not_evidence` |
| Closure effect | `does_not_close_ft0181` |
| Service attempted | `{service_label}` |
| Owner route attempted | `{owner_role}` |
| Source/date boundary attempted | `{source_record_set}; {date_range}` |
| Sent date | `{sent_date}` |
| Response due date | `{response_due_date}` |
| Status date | `{status_date}` |
| Attempt count | `{attempt_count}` |
| Operator confirmation | `{operator_confirmation}` |
| Source artifact reference | `{source_artifact}` |
| Source artifact verification | `verified:{source_artifact_type}` |
| Minimal reason | `{reason}` |
| Next action | `{next_action_for(status)}` |

## No-widening rule

This status note is local non-evidence. It does not upgrade source truth, open a
live window, authorize an import, support a public claim, or close `FT-0181`.
Do not add a full export request, new registry, raw learner request,
protected-route request, vendor detour, or closure workaround because the contact
clock is open or because no viable owner packet returned.

## Local-only exclusions

Do not paste recipient names, learner identifiers, learner messages, assignment
text, gradebook rows, screenshots, protected support facts, small cells, raw
telemetry, credentials, system prompts, exploit strings, or vendor marketing
material into this note.
"""


def build_status(
    *,
    output_dir: Path,
    status: str,
    service_label: str,
    owner_role: str,
    source_record_set: str,
    date_range: str,
    sent_date: str,
    response_due_date: str,
    status_date: str,
    attempt_count: int,
    minimal_reason: str = '',
    operator_confirmation: str = '',
    source_artifact: str = '',
    overwrite: bool = False,
) -> dict[str, Any]:
    forbidden = argument_boundary_error(service_label, owner_role, source_record_set, date_range, minimal_reason, source_artifact)
    if forbidden:
        return {
            'ok': False,
            'error': 'OWNER-CONTACT-ARG-BLOCKED',
            'reason': f'argument includes forbidden local-status term: {forbidden}',
            'state': 'NOT_RECORDED',
            'output_dir': str(output_dir),
        }
    allowed, output_boundary = output_allowed(output_dir, archive_root=ROOT)
    if not allowed:
        return {
            'ok': False,
            'error': 'OWNER-CONTACT-OUTPUT-BLOCKED',
            'reason': output_boundary,
            'state': 'NOT_RECORDED',
            'output_dir': str(output_dir),
        }
    clock_ok, clock_reason = validate_contact_clock(
        status=status,
        sent_date=sent_date,
        response_due_date=response_due_date,
        status_date=status_date,
        attempt_count=attempt_count,
    )
    if not clock_ok:
        return {
            'ok': False,
            'error': 'OWNER-CONTACT-CLOCK-BLOCKED',
            'reason': clock_reason,
            'state': 'NOT_RECORDED',
            'output_dir': str(output_dir),
        }
    confirmation_ok, confirmation_reason = validate_operator_confirmation(
        status=status,
        operator_confirmation=operator_confirmation,
        source_artifact=source_artifact,
    )
    if not confirmation_ok:
        return {
            'ok': False,
            'error': 'OWNER-CONTACT-CONFIRMATION-BLOCKED',
            'reason': confirmation_reason,
            'state': 'NOT_RECORDED',
            'output_dir': str(output_dir),
        }
    source_ok, source_reason, source_artifact_type = verify_source_artifact(
        status=status,
        source_artifact=source_artifact,
        sent_date=sent_date,
        response_due_date=response_due_date,
        status_date=status_date,
        attempt_count=attempt_count,
    )
    if not source_ok:
        return {
            'ok': False,
            'error': 'OWNER-CONTACT-SOURCE-ARTIFACT-BLOCKED',
            'reason': source_reason,
            'state': 'NOT_RECORDED',
            'source_artifact_type': source_artifact_type,
            'output_dir': str(output_dir),
        }
    if output_dir.exists() and any(output_dir.iterdir()) and not overwrite:
        return {
            'ok': False,
            'error': 'OWNER-CONTACT-OUTPUT-EXISTS',
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
    contact_status = STATUS_CHOICES[status]
    note_path = output_dir / note_filename(status)
    manifest_path = output_dir / 'contact-status.json'
    note_path.write_text(
        status_note(
            status=status,
            service_label=service_label,
            owner_role=owner_role,
            source_record_set=source_record_set,
            date_range=date_range,
            sent_date=sent_date,
            response_due_date=response_due_date,
            status_date=status_date,
            attempt_count=attempt_count,
            minimal_reason=minimal_reason,
            operator_confirmation=operator_confirmation,
            source_artifact=source_artifact,
            source_artifact_type=source_artifact_type,
        ),
        encoding='utf-8',
    )

    manifest = {
        'status_id': 'AIEDU-SR-003-OWNER-CONTACT-STATUS',
        'followthrough_id': 'FT-0181',
        'contact_status': contact_status,
        'created_at_utc': created,
        'evidence_state': 'not_evidence',
        'source_truth_class': 'not_evidence',
        'closure_effect': 'does_not_close_ft0181',
        'public_claim_effect': 'none',
        'service_label': service_label,
        'owner_role_label': owner_role,
        'source_record_set_label': source_record_set,
        'date_range_label': date_range,
        'sent_date': sent_date,
        'response_due_date': response_due_date,
        'status_date': status_date,
        'attempt_count': attempt_count,
        'max_response_clock_days': FIRST_CONTACT_MAX_DAYS if status == 'sent-awaiting-reply' else REASK_MAX_DAYS,
        'minimal_reason': minimal_reason or ('No viable owner packet returned after the bounded clock.' if status == 'no-owner-packet' else 'Bounded owner request clock is open.'),
        'operator_confirmation': operator_confirmation,
        'source_artifact_ref': source_artifact,
        'confirmation_effect': 'local_operator_assertion_not_evidence',
        'source_artifact_verified': True,
        'source_artifact_type': source_artifact_type,
        'source_artifact_verification': source_reason,
        'output_boundary': output_boundary,
        'generated_files': [note_path.name, manifest_path.name],
        'no_widening_confirmation': True,
        'next_action': next_action_for(status),
        'allowed_next_commands': [
            'make owner-field-next CSV=/path/to/returned-owner-reply.csv OUT=scratch/field/ft0181/ft0181-field-next-action/returned-owner-reply',
            'make owner-field-next OUT=scratch/field/ft0181/ft0181-field-next-action/after-contact-clock',
            'execute only the command emitted by FIELD-NEXT-ACTION.md; do not bypass the router-first source firebreak or contact-clock validator',
        ],
        'forbidden_actions': [
            'close_ft0181',
            'upgrade_to_src2_from_status_note',
            'claim_real_pilot_evidence',
            'claim_learning_or_service_effectiveness',
            'request_full_export_or_raw_learner_records',
            'extend_response_clock_to_avoid_no_owner_packet',
            'create_new_registry_or_doctrine_surface_to_replace_missing_owner_packet',
        ],
        'local_only_exclusions': [
            'recipient_names_or_contact_details_in_release_archive',
            'learner_identifiers_or_messages',
            'raw_lms_exports_or_gradebook_rows',
            'protected_support_facts_or_small_cells',
            'credentials_or_security_payloads',
            'vendor_marketing_or_unreviewed_dashboard_claims',
        ],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return {
        'ok': True,
        'contact_status': contact_status,
        'evidence_state': manifest['evidence_state'],
        'followthrough_id': manifest['followthrough_id'],
        'output_dir': str(output_dir),
        'files': manifest['generated_files'],
        'manifest': manifest,
    }


def main() -> None:
    args = parse_args()
    result = build_status(
        output_dir=Path(args.output_dir),
        status=args.status,
        service_label=args.service_label,
        owner_role=args.owner_role,
        source_record_set=args.source_record_set,
        date_range=args.date_range,
        sent_date=args.sent_date,
        response_due_date=args.response_due_date,
        status_date=args.status_date or operator_today_iso(),
        attempt_count=args.attempt_count,
        minimal_reason=args.minimal_reason,
        operator_confirmation=args.operator_confirmation,
        source_artifact=args.source_artifact,
        overwrite=args.overwrite,
    )
    if args.json:
        print(json.dumps(result, indent=2))
    elif result.get('ok'):
        print(
            'record_ft0181_owner_contact_status: OK '
            f"({result['contact_status']}, {result['evidence_state']}, {result['output_dir']})"
        )
    else:
        raise SystemExit(f"record_ft0181_owner_contact_status: {result['error']} ({result['reason']})")


if __name__ == '__main__':
    main()
