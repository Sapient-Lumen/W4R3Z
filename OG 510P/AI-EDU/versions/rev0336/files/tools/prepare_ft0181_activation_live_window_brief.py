#!/usr/bin/env python3
"""Prepare a bounded FT-0181 activation/live-window entry brief.

This scratch-only bridge sits after a post-decision change ticket and before the
most failure-prone late field steps. For a ``ready_for_real_packet`` ticket it
prepares the activation-receipt handoff for the same real owner-reviewed source
packet that seeded the decision chain. For an ``active_change`` ticket it
prepares minimized live-window card command skeletons. It never accepts a source
packet, records an activation receipt, records a change ticket, starts a live
window, edits service records, supports public claims, creates custody, moves
lifecycle state, or closes FT-0181.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ft0181_field_guards import (
    archive_relative,
    field_scratch_lane_error,
    output_allowed,
    owner_activation_live_window_brief_integrity_error,
    owner_post_decision_change_ticket_integrity_error,
)
from record_ft0181_activation_receipt import OPERATOR_CONFIRMATION as ACTIVATION_CONFIRMATION
from record_ft0181_live_window_card import OPERATOR_CONFIRMATION as LIVE_WINDOW_CONFIRMATION
from record_ft0181_post_decision_change_ticket import OPERATOR_CONFIRMATION as CHANGE_TICKET_CONFIRMATION

ROOT = Path(__file__).resolve().parents[1]
REVISION = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8')).get('revision', 'unknown')
DEFAULT_OUTPUT_ROOT = ROOT / 'scratch' / 'field' / 'ft0181' / 'owner-activation-live-window-briefs'
CLAIM_CEILING = (
    'Activation/live-window entry brief only; not an activation receipt, not a live-window card, '
    'not evidence, not SRC2+ acceptance, not custody evidence, not closure evidence, '
    'not public-summary support, and not proof of learning, safety, access, workload, '
    'compliance, scale, or effectiveness.'
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Prepare a bounded FT-0181 activation/live-window entry brief from a post-decision ticket.')
    parser.add_argument('--ticket', required=True, type=Path, help='scratch/.../post-decision-change-ticket.json from owner-post-decision-change-ticket.')
    parser.add_argument('--output-dir', type=Path, help='Local/scratch output directory for the activation/live-window brief.')
    parser.add_argument('--overwrite', action='store_true', help='Replace an existing activation/live-window brief directory.')
    parser.add_argument('--json', action='store_true', help='Print machine-readable result.')
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def default_output_dir(ticket_path: Path) -> Path:
    digest = sha256_file(ticket_path)[:12] if ticket_path.exists() and ticket_path.is_file() else 'missingticket'
    stem = ticket_path.parent.name.replace(' ', '-').replace('/', '-')[:48] or 'post-decision-ticket'
    return DEFAULT_OUTPUT_ROOT / f'{stem}-{digest}'


def shell_quote(value: str) -> str:
    if value.replace('/', '').replace('-', '').replace('_', '').replace('.', '').isalnum():
        return value
    return "'" + value.replace("'", "'\\''") + "'"


def source_ticket_snapshot(ticket_path: Path, ticket_data: dict[str, Any]) -> dict[str, Any]:
    return {
        'reference': relative(ticket_path),
        'ticket_sha256': sha256_file(ticket_path),
        'ticket_state': ticket_data.get('ticket_state'),
        'change_class': ticket_data.get('change_class'),
        'source_truth_required': ticket_data.get('source_truth_required'),
        'public_claim_ceiling': ticket_data.get('public_claim_ceiling'),
        'live_window_required': ticket_data.get('live_window_required'),
        'change_counts': ticket_data.get('change_counts'),
        'rollback_owner_role_count': ticket_data.get('rollback_owner_role_count'),
        'acceptance_state': ticket_data.get('acceptance_state'),
        'evidence_state': ticket_data.get('evidence_state'),
        'source_first_packet_decision': ticket_data.get('source_first_packet_decision'),
        'source_activation_receipt': ticket_data.get('source_activation_receipt'),
        'live_window_effect': ticket_data.get('live_window_effect'),
        'change_ticket_effect': ticket_data.get('change_ticket_effect'),
        'revalidated_for_activation_live_window_brief': True,
    }


def activation_receipt_command(decision_ref: str) -> str:
    return (
        f'make owner-activation-receipt DECISION={shell_quote(decision_ref)} '
        'SOURCE_PACKET=/path/to/same-returned-owner-csv-that-seeded-this-decision.csv '
        'SOURCE_TRUTH_CLASS=SRC2 ACCEPTED_FIELD_COUNT=<1-8> REVIEWER_ROLE_COUNT=<2-5> '
        'DICTIONARY_OR_MAP_REF_COUNT=<1-10> BLOCKED_OR_TRIMMED_FIELD_COUNT=<0-8> '
        f'CONFIRM={ACTIVATION_CONFIRMATION}'
    )


def active_change_ticket_command(decision_ref: str) -> str:
    return (
        f'make owner-post-decision-change-ticket DECISION={shell_quote(decision_ref)} '
        'TICKET_STATE=active-change CHANGE_CLASS=pct-c-sandbox-adjustment SOURCE_TRUTH_REQUIRED=SRC2 '
        'PUBLIC_CLAIM_CEILING=example-only-no-outcome-claim ALLOWED_CHANGE_COUNT=1 '
        'PROHIBITED_CHANGE_COUNT=4 ROLLBACK_TRIGGER_COUNT=3 ROLLBACK_OWNER_ROLE_COUNT=<1-5> '
        'LIVE_WINDOW_REQUIRED=1 ACTIVATION_RECEIPT=<scratch/.../activation-receipt.json> '
        f'CONFIRM={CHANGE_TICKET_CONFIRMATION}'
    )


def live_window_commands(ticket_ref: str) -> dict[str, str]:
    ticket = shell_quote(ticket_ref)
    base = f'make owner-live-window-card TICKET={ticket} '
    common = (
        'SOURCE_TRUTH_CLASS=SRC2 WINDOW_DAY_COUNT=<1-14> ALLOWED_ACTIVITY_COUNT=1 '
        'PROHIBITED_ACTIVITY_COUNT=5 STOP_TRIGGER_COUNT=3 ROLLBACK_STEP_COUNT=3 '
        'ROLLBACK_OWNER_ROLE_COUNT=<1-5> EVIDENCE_READOUT_COUNT=3 '
        'NO_EXPANSION_CONFIRMED=1 HUMAN_PAUSE_CONFIRMED=1 FALLBACK_ROUTE_CONFIRMED=1 '
        f'CONFIRM={LIVE_WINDOW_CONFIRMATION}'
    )
    return {
        'staged_small_window': base + 'WINDOW_STATE=staged ' + common,
        'active_small_window': base + 'WINDOW_STATE=active ' + common,
        'paused_stop_state': base + 'WINDOW_STATE=paused ' + common,
        'quarantine_without_expansion': (
            base + 'WINDOW_STATE=quarantined SOURCE_TRUTH_CLASS=SRC2 WINDOW_DAY_COUNT=1 '
            'ALLOWED_ACTIVITY_COUNT=1 PROHIBITED_ACTIVITY_COUNT=5 STOP_TRIGGER_COUNT=3 '
            'ROLLBACK_STEP_COUNT=3 ROLLBACK_OWNER_ROLE_COUNT=<1-5> EVIDENCE_READOUT_COUNT=1 '
            'NO_EXPANSION_CONFIRMED=1 HUMAN_PAUSE_CONFIRMED=1 FALLBACK_ROUTE_CONFIRMED=1 '
            f'CONFIRM={LIVE_WINDOW_CONFIRMATION}'
        ),
    }


def build_markdown(brief: dict[str, Any]) -> str:
    ticket = brief['source_post_decision_change_ticket']
    lines = [
        '# FT-0181 activation/live-window entry brief',
        '',
        f"Brief state: `{brief['brief_state']}`",
        f"Source ticket: `{ticket['reference']}`",
        f"Ticket SHA-256: `{ticket['ticket_sha256']}`",
        f"Ticket state: `{ticket['ticket_state']}`",
        f"Change class: `{ticket['change_class']}`",
        f"Source truth required: `{ticket['source_truth_required']}`",
        f"Acceptance state: `{brief['acceptance_state']}`",
        'Evidence effect: `not_evidence`',
        'Closure effect: `does_not_close_ft0181`',
        '',
        '## Human job',
        '',
        'Use this as a one-screen handoff only. Replace placeholders with bounded counts and the same real owner-reviewed source packet path already preserved by the decision chain. Do not paste owner answers, raw CSV rows, contact details, learner facts, protected facts, screenshots, security payloads, or public claim text into any command.',
    ]
    if brief.get('activation_receipt_command_template'):
        lines.extend([
            '',
            '## If the same real owner-reviewed SRC2+ source packet is now available',
            '',
            'First record the activation receipt. This still is not evidence, custody, public-summary support, lifecycle movement, or closure.',
            '',
            '```bash',
            brief['activation_receipt_command_template'],
            '```',
            '',
            'Only after that receipt exists may a human record the active-change ticket from the same decision and receipt:',
            '',
            '```bash',
            brief['active_change_ticket_command_template'],
            '```',
        ])
    commands = brief.get('live_window_card_command_templates') or {}
    if commands:
        lines.extend([
            '',
            '## If the source ticket is already active_change',
            '',
            'Choose one bounded live-window card route. The card is still local, `NOT_ACCEPTED`, and must be read out before any service-record, lifecycle, public-summary, custody, acceptance, or closure step.',
        ])
        for title, command in commands.items():
            lines.extend(['', f'### {title.replace("_", " ")}', '', '```bash', command, '```'])
    lines.extend([
        '',
        '## Hard boundary',
        '',
        'This brief does not create an activation receipt, active-change ticket, live-window card, evidence, custody, public-summary support, service-record mutation, lifecycle movement, or closure. It only prevents the operator from confusing ready-for-real-packet with active-change, or active-change with an already-started live window.',
    ])
    return '\n'.join(lines) + '\n'


def build_activation_live_window_brief(*, ticket: Path, output_dir: Path | None = None, overwrite: bool = False) -> dict[str, Any]:
    ticket_path = ticket if ticket.is_absolute() else ROOT / ticket
    ticket_path = ticket_path.resolve()
    inside, parts = archive_relative(ticket_path, archive_root=ROOT)
    lane_error = field_scratch_lane_error(ticket_path, archive_root=ROOT, field_name='ticket')
    if lane_error or ticket_path.name != 'post-decision-change-ticket.json':
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'ACTIVATION-LIVE-WINDOW-BRIEF-TICKET-BLOCKED',
            'message': 'Activation/live-window brief requires a scratch-local post-decision-change-ticket.json source.',
            'ticket': relative(ticket_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if not ticket_path.exists() or not ticket_path.is_file():
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'ACTIVATION-LIVE-WINDOW-BRIEF-TICKET-MISSING',
            'message': 'Referenced post-decision change ticket does not exist.',
            'ticket': relative(ticket_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    try:
        ticket_data = load_json(ticket_path)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'ACTIVATION-LIVE-WINDOW-BRIEF-TICKET-BLOCKED',
            'message': 'Referenced post-decision ticket is not readable JSON.',
            'error': str(exc),
            'ticket': relative(ticket_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    ticket_error = owner_post_decision_change_ticket_integrity_error(ticket_data, archive_root=ROOT)
    if ticket_error:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'ACTIVATION-LIVE-WINDOW-BRIEF-TICKET-BLOCKED',
            'message': 'Referenced post-decision ticket failed integrity checks: ' + ticket_error,
            'ticket': relative(ticket_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    ticket_state = ticket_data.get('ticket_state')
    if ticket_state not in {'ready_for_real_packet', 'active_change'}:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'ACTIVATION-LIVE-WINDOW-BRIEF-STATE-BLOCKED',
            'message': 'Activation/live-window brief is only for ready_for_real_packet or active_change tickets.',
            'ticket_state': ticket_state,
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    out = output_dir if output_dir is not None else default_output_dir(ticket_path)
    out = out if out.is_absolute() else ROOT / out
    allowed, boundary = output_allowed(out, archive_root=ROOT)
    if not allowed:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'ACTIVATION-LIVE-WINDOW-BRIEF-OUTPUT-BLOCKED',
            'message': 'Activation/live-window briefs are local/scratch artifacts and cannot be written into release-controlled surfaces.',
            'output_dir': relative(out),
            'output_boundary': boundary,
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if out.exists():
        if overwrite:
            if out.is_dir():
                shutil.rmtree(out)
            else:
                out.unlink()
        else:
            raise FileExistsError(f'output already exists: {out}; pass --overwrite to replace it')
    out.mkdir(parents=True, exist_ok=True)

    created = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    ticket_ref = relative(ticket_path)
    source_decision = ticket_data.get('source_first_packet_decision') if isinstance(ticket_data.get('source_first_packet_decision'), dict) else {}
    decision_ref = str(source_decision.get('reference') or 'scratch/MISSING/first-packet-decision.json')
    ready_for_activation = ticket_state == 'ready_for_real_packet'
    active_for_live_window = ticket_state == 'active_change'
    brief = {
        'brief_type': 'FT-0181-activation-live-window-entry-brief',
        'brief_version': REVISION,
        'created_at_utc': created,
        'followthrough_id': 'FT-0181',
        'service_record_id': 'AIEDU-SR-003',
        'brief_state': 'ACTIVATION_ENTRY_BRIEF_PREPARED_NOT_ACCEPTED' if ready_for_activation else 'LIVE_WINDOW_ENTRY_BRIEF_PREPARED_NOT_RECORDED',
        'source_post_decision_change_ticket': source_ticket_snapshot(ticket_path, ticket_data),
        'acceptance_state': 'NOT_ACCEPTED',
        'evidence_state': 'not_evidence',
        'closure_effect': 'does_not_close_ft0181',
        'public_claim_effect': 'none',
        'ft0181_status': 'live',
        'recommended_next_action': 'human-confirm-real-source-packet-and-record-activation-receipt' if ready_for_activation else 'human-record-bounded-live-window-card',
        'required_next_surface': 'docs/30-operations/ft0181-post-decision-change-ticket.md' if ready_for_activation else 'docs/30-operations/ft0181-live-window-stop-rollback-card.md',
        'activation_receipt_command_template': activation_receipt_command(decision_ref) if ready_for_activation else None,
        'active_change_ticket_command_template': active_change_ticket_command(decision_ref) if ready_for_activation else None,
        'live_window_card_command_templates': live_window_commands(ticket_ref) if active_for_live_window else {},
        'activation_boundary': 'ready_for_real_packet requires a same-hash real owner-reviewed SRC2+ source packet and owner-activation-receipt before active_change; this brief does not create acceptance.',
        'live_window_boundary': 'active_change requires a separate owner-live-window-card before any bounded window; this brief does not start, stage, pause, roll back, or complete a window.',
        'claim_ceiling': CLAIM_CEILING,
        'content_minimization': {
            'copies_owner_answers': False,
            'copies_raw_csv_rows': False,
            'copies_post_decision_ticket_text': False,
            'copies_contact_details': False,
            'copies_learner_identifiers_or_protected_facts': False,
            'source_post_decision_ticket_revalidated': True,
            'contains_hashes_counts_and_command_skeletons_only': True,
        },
        'forbidden_effects': [
            'source-packet-acceptance',
            'activation-receipt-creation',
            'active-change-ticket-recording',
            'live-window-card-recording',
            'raw-answer-copy-to-release',
            'custody-or-acceptance',
            'service-record-edit',
            'public-claim-upgrade',
            'lifecycle-or-closure',
        ],
    }
    brief_error = owner_activation_live_window_brief_integrity_error(brief, archive_root=ROOT)
    if brief_error:
        shutil.rmtree(out)
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'ACTIVATION-LIVE-WINDOW-BRIEF-BLOCKED',
            'message': brief_error,
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    brief_path = out / 'activation-live-window-brief.json'
    summary_path = out / 'ACTIVATION-LIVE-WINDOW-BRIEF.md'
    brief_path.write_text(json.dumps(brief, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    summary_path.write_text(build_markdown(brief), encoding='utf-8')
    return {
        'ok': True,
        'outcome': 'ACTIVATION-LIVE-WINDOW-BRIEF-PREPARED',
        'output_dir': relative(out),
        'brief_path': relative(brief_path),
        'summary_path': relative(summary_path),
        'source_ticket': ticket_ref,
        'ticket_state': ticket_state,
        'acceptance_state': 'NOT_ACCEPTED',
        'evidence_state': 'not_evidence',
        'closure_effect': 'does_not_close_ft0181',
        'public_claim_effect': 'none',
        'required_next_surface': brief['required_next_surface'],
        'claim_ceiling': CLAIM_CEILING,
    }


def main() -> int:
    args = parse_args()
    try:
        result = build_activation_live_window_brief(ticket=args.ticket, output_dir=args.output_dir, overwrite=args.overwrite)
    except Exception as exc:
        if args.json:
            try:
                payload = json.loads(str(exc))
            except json.JSONDecodeError:
                payload = {'ok': False, 'outcome': 'ACTIVATION-LIVE-WINDOW-BRIEF-ERROR', 'message': str(exc), 'claim_ceiling': CLAIM_CEILING}
            print(json.dumps(payload, indent=2))
            return 1
        raise
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
