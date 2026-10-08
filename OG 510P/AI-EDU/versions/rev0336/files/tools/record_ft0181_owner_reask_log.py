#!/usr/bin/env python3
"""Record a minimal local FT-0181 owner reask-send log.

This utility sits between a bounded clarification trigger and a REASK contact
clock. It does not send mail, store recipients, copy owner answers, import
evidence, or close FT-0181. It only records that a human operator asserts the
one allowed clarification was sent or adapted through a class of local owner
route, so a later REASK clock is sourced from a distinct local reask artifact
rather than directly from triage or review output.
"""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from ft0181_field_guards import (
    REASK_MAX_DAYS,
    archive_relative,
    field_scratch_lane_error,
    output_allowed,
    owner_reask_log_integrity_error,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / 'scratch' / 'field' / 'ft0181' / 'owner-reask-logs' / 'aiedu-sr-003'

OPERATOR_CONFIRMATION = 'human-sent-bounded-reask'
REASK_CHANNEL_CLASSES = {
    'email',
    'ticket',
    'form',
    'delegated-local-route',
    'other-bounded-route',
}
OWNER_ROUTE_CLASSES = {
    'same-accountable-owner-route',
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
    parser = argparse.ArgumentParser(description='Record a local FT-0181 owner reask-send log without contact details or evidence effects.')
    parser.add_argument('--source-artifact', required=True, help='Scratch artifact that triggered the bounded reask: prior SENT clock, RE-ASK-ONCE intake bundle, or REASK-OWNER workbench review.')
    parser.add_argument('--sent-date', required=True, help='Human reask send/adaptation date, YYYY-MM-DD.')
    parser.add_argument('--response-due-date', required=True, help='Local clarification response-clock due date, YYYY-MM-DD; max three days after sent-date.')
    parser.add_argument('--output-dir', default=str(DEFAULT_OUTPUT), help='Local/scratch output directory for the reask log.')
    parser.add_argument('--service-label', default='AIEDU-SR-003 draft reminder pilot', help='Non-sensitive service label.')
    parser.add_argument('--owner-role', default='accountable service owner route', help='Role/contact path class, not a person name or address.')
    parser.add_argument('--source-record-set', default='owner-maintained local service record set', help='Aggregate source record-set label.')
    parser.add_argument('--date-range', default='owner-named date boundary', help='Aggregate date/date-range boundary.')
    parser.add_argument('--reask-channel-class', choices=sorted(REASK_CHANNEL_CLASSES), default='email', help='Class of reask route; do not include recipient or platform details.')
    parser.add_argument('--owner-route-class', choices=sorted(OWNER_ROUTE_CLASSES), default='same-accountable-owner-route', help='Class of accountable owner route; do not include recipient or contact details.')
    parser.add_argument('--adapted-from-template', action='store_true', help='Set when the human sent an adapted but still bounded version of the reask template.')
    parser.add_argument('--operator-confirmation', required=True, help=f'Must be {OPERATOR_CONFIRMATION!r}; local assertion only, not evidence.')
    parser.add_argument('--minimal-reask-note', default='', help='Optional local note class only; no names, addresses, owner answers, or raw/protected facts.')
    parser.add_argument('--overwrite', action='store_true', help='Replace an existing reask-log directory.')
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


def resolve_source_artifact(source_artifact: str | Path) -> Path:
    candidate = Path(source_artifact)
    if candidate.is_absolute():
        return candidate
    return ROOT / candidate


def reask_note(manifest: dict[str, Any]) -> str:
    return f"""# FT-0181 owner reask send log

Reask-log state: `LOCAL_REASK_LOG_NOT_EVIDENCE`
Evidence state: `not_evidence`
Closure effect: `does_not_close_ft0181`
Service: `{manifest['service_label']}`
Reask source artifact: `{manifest['reask_source_ref']}`
Sent date: `{manifest['sent_date']}`
Response due date: `{manifest['response_due_date']}`
Reask channel class: `{manifest['reask_channel_class']}`
Owner route class: `{manifest['owner_route_class']}`
Adapted from bounded reask template: `{manifest['adapted_from_template']}`

This log is a local operator assertion that exactly one bounded clarification was
sent or adapted through a class of owner route. It stores no recipient name,
address, owner answer, learner record, protected fact, screenshot, transcript,
dashboard, credential, or raw export. It is not evidence and cannot close
`FT-0181`.

## Next command

Run the field router and execute only the contact-status command it emits:

```bash
make owner-field-next OUT=scratch/field/ft0181/ft0181-field-next-action/after-reask-log OVERWRITE=1
```

The router should now source `STATUS=reask-awaiting-reply` from this
`reask-log.json`, not directly from the intake bundle, prior contact clock, or
workbench review.
"""


def validate_source_artifact_for_reask(source_artifact: Path, sent_date: str) -> tuple[bool, str, str, dict[str, Any] | None]:
    resolved = source_artifact.resolve()
    inside, parts = archive_relative(resolved, archive_root=ROOT)
    if not inside or not parts or parts[0] != 'scratch':
        return False, 'source-artifact must resolve under archive scratch/', 'blocked-boundary', None
    lane_error = field_scratch_lane_error(resolved, archive_root=ROOT, field_name='source-artifact')
    if lane_error:
        return False, lane_error, 'blocked-boundary', None
    if not resolved.exists() or not resolved.is_file():
        return False, 'source-artifact must point to an existing scratch JSON file', 'missing-file', None
    data = load_json(resolved)
    if data is None:
        return False, 'source-artifact is not readable JSON', 'bad-json', None
    # Delegate the detailed class checks to the shared guard by building a tiny
    # draft manifest around the source. This keeps source rules in one place.
    draft = {
        'reask_log_type': 'FT-0181-owner-reask-log',
        'reask_log_version': 'rev0282',
        'followthrough_id': 'FT-0181',
        'service_record_id': 'AIEDU-SR-003',
        'reask_source_ref': archive_ref(resolved),
        'sent_date': sent_date,
        'response_due_date': sent_date,
        'max_response_clock_days': REASK_MAX_DAYS,
        'reask_channel_class': 'email',
        'owner_route_class': 'same-accountable-owner-route',
        'adapted_from_template': False,
        'operator_confirmation': OPERATOR_CONFIRMATION,
        'evidence_state': 'not_evidence',
        'source_truth_class': 'not_evidence',
        'closure_effect': 'does_not_close_ft0181',
        'public_claim_effect': 'none',
        'contact_status_effect': 'may_source_reask_awaiting_reply_clock_only',
        'no_contact_details_stored': True,
        'no_raw_or_protected_material_stored': True,
        'no_widening_confirmation': True,
        'created_at_utc': '2026-01-01T00:00:00Z',
    }
    error = owner_reask_log_integrity_error(draft, archive_root=ROOT)
    if error:
        return False, f'reask source artifact failed integrity checks: {error}', 'reask-source', data
    if resolved.name == 'contact-status.json':
        source_type = 'prior-sent-contact-status'
    elif resolved.name == 'bundle-manifest.json':
        source_type = 'reask-once-intake-bundle'
    elif resolved.name == 'workbench-review.json':
        source_type = 'reask-owner-workbench-review'
    else:
        source_type = 'unknown'
    return True, 'reask-source-artifact-ok', source_type, data


def build_reask_log(
    *,
    output_dir: Path,
    source_artifact: Path,
    sent_date: str,
    response_due_date: str,
    service_label: str,
    owner_role: str,
    source_record_set: str,
    date_range: str,
    reask_channel_class: str,
    owner_route_class: str,
    adapted_from_template: bool = False,
    operator_confirmation: str,
    minimal_reask_note: str = '',
    overwrite: bool = False,
) -> dict[str, Any]:
    forbidden = argument_boundary_error(
        service_label,
        owner_role,
        source_record_set,
        date_range,
        reask_channel_class,
        owner_route_class,
        minimal_reask_note,
        source_artifact.as_posix(),
    )
    if forbidden:
        return {
            'ok': False,
            'error': 'OWNER-REASK-LOG-ARG-BLOCKED',
            'reason': f'argument includes forbidden reask-log term: {forbidden}',
            'state': 'NOT_RECORDED',
            'output_dir': str(output_dir),
        }
    allowed, output_boundary = output_allowed(output_dir, archive_root=ROOT)
    if not allowed:
        return {
            'ok': False,
            'error': 'OWNER-REASK-LOG-OUTPUT-BLOCKED',
            'reason': output_boundary,
            'state': 'NOT_RECORDED',
            'output_dir': str(output_dir),
        }
    if operator_confirmation.strip() != OPERATOR_CONFIRMATION:
        return {
            'ok': False,
            'error': 'OWNER-REASK-LOG-CONFIRMATION-BLOCKED',
            'reason': f'operator-confirmation must be {OPERATOR_CONFIRMATION!r}',
            'state': 'NOT_RECORDED',
            'output_dir': str(output_dir),
        }
    if reask_channel_class not in REASK_CHANNEL_CLASSES:
        return {
            'ok': False,
            'error': 'OWNER-REASK-LOG-CHANNEL-BLOCKED',
            'reason': f'reask-channel-class must be one of {sorted(REASK_CHANNEL_CLASSES)}',
            'state': 'NOT_RECORDED',
            'output_dir': str(output_dir),
        }
    if owner_route_class not in OWNER_ROUTE_CLASSES:
        return {
            'ok': False,
            'error': 'OWNER-REASK-LOG-ROUTE-BLOCKED',
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
            'error': 'OWNER-REASK-LOG-CLOCK-BLOCKED',
            'reason': str(exc),
            'state': 'NOT_RECORDED',
            'output_dir': str(output_dir),
        }
    if due < sent:
        return {
            'ok': False,
            'error': 'OWNER-REASK-LOG-CLOCK-BLOCKED',
            'reason': 'response-due-date must be on or after sent-date',
            'state': 'NOT_RECORDED',
            'output_dir': str(output_dir),
        }
    if (due - sent).days > REASK_MAX_DAYS:
        return {
            'ok': False,
            'error': 'OWNER-REASK-LOG-CLOCK-BLOCKED',
            'reason': f'reask response clock cannot exceed {REASK_MAX_DAYS} days from sent-date',
            'state': 'NOT_RECORDED',
            'output_dir': str(output_dir),
        }
    source_path = source_artifact.resolve()
    source_ok, source_reason, source_type, source_data = validate_source_artifact_for_reask(source_path, sent.isoformat())
    if not source_ok or source_data is None:
        return {
            'ok': False,
            'error': 'OWNER-REASK-LOG-SOURCE-BLOCKED',
            'reason': source_reason,
            'state': 'NOT_RECORDED',
            'source_artifact_type': source_type,
            'output_dir': str(output_dir),
        }
    if output_dir.exists() and any(output_dir.iterdir()):
        if not overwrite:
            return {
                'ok': False,
                'error': 'OWNER-REASK-LOG-OUTPUT-EXISTS',
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
        'reask_log_type': 'FT-0181-owner-reask-log',
        'reask_log_version': 'rev0282',
        'followthrough_id': 'FT-0181',
        'service_record_id': 'AIEDU-SR-003',
        'service_label': service_label,
        'owner_role_class': owner_role,
        'source_record_set': source_record_set,
        'date_range': date_range,
        'reask_source_ref': archive_ref(source_path),
        'reask_source_type': source_type,
        'reask_source_created_at_utc': source_data.get('created_at_utc'),
        'sent_date': sent.isoformat(),
        'response_due_date': due.isoformat(),
        'max_response_clock_days': REASK_MAX_DAYS,
        'reask_channel_class': reask_channel_class,
        'owner_route_class': owner_route_class,
        'adapted_from_template': bool(adapted_from_template),
        'operator_confirmation': OPERATOR_CONFIRMATION,
        'minimal_reask_note': minimal_reask_note or 'one bounded clarification sent/adapted without storing recipient details or owner answers',
        'evidence_state': 'not_evidence',
        'source_truth_class': 'not_evidence',
        'closure_effect': 'does_not_close_ft0181',
        'public_claim_effect': 'none',
        'contact_status_effect': 'may_source_reask_awaiting_reply_clock_only',
        'no_contact_details_stored': True,
        'no_raw_or_protected_material_stored': True,
        'no_widening_confirmation': True,
        'local_only': True,
        'created_at_utc': created,
        'output_boundary': output_boundary,
        'generated_files': ['reask-log.json', 'REASK-LOG.md'],
        'allowed_next_commands': [
            'make owner-field-next OUT=scratch/field/ft0181/ft0181-field-next-action/after-reask-log OVERWRITE=1',
            'then run only the emitted make owner-contact-status STATUS=reask-awaiting-reply command',
        ],
        'forbidden_effects': [
            'does_not_send_email',
            'does_not_store_recipient_details',
            'does_not_import_owner_answers',
            'does_not_upgrade_to_SRC2+',
            'does_not_close_FT-0181',
            'does_not_support_public_claims',
            'does_not_create_a_second_reask',
            'does_not_widen_request_scope',
        ],
    }
    integrity_error = owner_reask_log_integrity_error(manifest, archive_root=ROOT)
    if integrity_error:
        return {
            'ok': False,
            'error': 'OWNER-REASK-LOG-INTEGRITY-BLOCKED',
            'reason': integrity_error,
            'state': 'NOT_RECORDED',
            'output_dir': str(output_dir),
        }
    (output_dir / 'reask-log.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    (output_dir / 'REASK-LOG.md').write_text(reask_note(manifest), encoding='utf-8')
    return {
        'ok': True,
        'state': 'LOCAL_REASK_LOG_NOT_EVIDENCE',
        'output_dir': str(output_dir),
        'manifest': str(output_dir / 'reask-log.json'),
        'note': str(output_dir / 'REASK-LOG.md'),
        'next_action': 'run_owner_field_next_to_record_reask_clock_from_reask_log',
        'evidence_effect': 'none',
        'closure_effect': 'does_not_close_ft0181',
    }


def main() -> None:
    args = parse_args()
    result = build_reask_log(
        output_dir=Path(args.output_dir),
        source_artifact=resolve_source_artifact(args.source_artifact),
        sent_date=args.sent_date,
        response_due_date=args.response_due_date,
        service_label=args.service_label,
        owner_role=args.owner_role,
        source_record_set=args.source_record_set,
        date_range=args.date_range,
        reask_channel_class=args.reask_channel_class,
        owner_route_class=args.owner_route_class,
        adapted_from_template=args.adapted_from_template,
        operator_confirmation=args.operator_confirmation,
        minimal_reask_note=args.minimal_reask_note,
        overwrite=args.overwrite,
    )
    if args.json:
        print(json.dumps(result, indent=2))
    elif result.get('ok'):
        print('record_ft0181_owner_reask_log: OK (LOCAL_REASK_LOG_NOT_EVIDENCE)')
        print(f"manifest: {result['manifest']}")
        print(f"next_action: {result['next_action']}")
    else:
        raise SystemExit(f"record_ft0181_owner_reask_log: {result.get('error')} ({result.get('reason')})")


if __name__ == '__main__':
    main()
