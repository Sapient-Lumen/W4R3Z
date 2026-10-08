#!/usr/bin/env python3
"""Record a bounded local FT-0181 live-window stop/rollback card.

This utility is the executable step after a valid post-decision change ticket.
It captures only window state, scope/count classes, stop/rollback controls,
hashes, and source-ticket references. It copies no owner answers, raw rows,
contact details, learner data, protected facts, security payloads, or public
claim text. The output is scratch/local only: not evidence, not custody, not
acceptance, not closure, and not public-summary support.
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
    POST_DECISION_SRC2_PLUS,
    archive_relative,
    field_scratch_lane_error,
    output_allowed,
    owner_live_window_card_integrity_error,
    owner_post_decision_change_ticket_integrity_error,
)

ROOT = Path(__file__).resolve().parents[1]
REVISION = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8')).get('revision', 'unknown')
DEFAULT_OUTPUT_ROOT = ROOT / 'scratch' / 'field' / 'ft0181' / 'owner-live-window-cards'
OPERATOR_CONFIRMATION = 'human-recorded-bounded-live-window-card'
CLAIM_CEILING = (
    'Live-window stop/rollback card only; not evidence, not SRC2+ acceptance, '
    'not custody evidence, not closure evidence, not public-summary support, and '
    'not proof of learning, safety, access, workload, compliance, scale, or effectiveness.'
)

WINDOW_STATE_CHOICES = {
    'blocked-no-real-packet': 'blocked_no_real_packet',
    'blocked-incomplete-ticket': 'blocked_incomplete_ticket',
    'staged': 'staged',
    'active': 'active',
    'paused': 'paused',
    'rolled-back': 'rolled_back',
    'completed-no-closure': 'completed_no_closure',
    'quarantined': 'quarantined',
}
SOURCE_TRUTH_CHOICES = {'SRC0', 'SRC2', 'SRC3', 'SRC4'}
PUBLIC_CEILING_CHOICES = {
    'example-only-no-outcome-claim',
    'draft-only-no-outcome-claim',
    'suppress-public-language',
    'limited-process-language-no-outcome-claim',
}
FORBIDDEN_TERMS = {
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
    'accommodation facts',
    'disability facts',
    'discipline record',
    'safeguarding record',
}
LIVE_SOURCE_STATES = {'staged', 'active', 'paused', 'rolled_back', 'completed_no_closure'}
READOUT_READY_STATES = {'paused', 'rolled_back', 'completed_no_closure', 'quarantined'}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Record a local bounded FT-0181 live-window card.')
    parser.add_argument('--ticket', required=True, type=Path, help='scratch/.../post-decision-change-ticket.json.')
    parser.add_argument('--window-state', required=True, choices=sorted(WINDOW_STATE_CHOICES))
    parser.add_argument('--source-truth-class', required=True, choices=sorted(SOURCE_TRUTH_CHOICES))
    parser.add_argument('--window-day-count', type=int, required=True, help='0 for blocked rehearsal; 1-14 for live/staged windows.')
    parser.add_argument('--allowed-activity-count', type=int, required=True, help='0-5 allowed activities; active/staged need at least 1.')
    parser.add_argument('--prohibited-activity-count', type=int, required=True, help='1-10 prohibited activities.')
    parser.add_argument('--stop-trigger-count', type=int, required=True, help='1-10 stop/rollback triggers.')
    parser.add_argument('--rollback-step-count', type=int, required=True, help='1-10 rollback steps.')
    parser.add_argument('--rollback-owner-role-count', type=int, default=1, help='1-5 rollback owner roles.')
    parser.add_argument('--evidence-readout-count', type=int, required=True, help='0 for blocked rehearsal; 1-7 aggregate readout classes.')
    parser.add_argument('--public-claim-ceiling', default='example-only-no-outcome-claim', choices=sorted(PUBLIC_CEILING_CHOICES))
    parser.add_argument('--operator-confirmation', required=True, help='Exact local confirmation token emitted by the router.')
    parser.add_argument('--no-expansion-confirmed', action='store_true')
    parser.add_argument('--human-pause-confirmed', action='store_true')
    parser.add_argument('--fallback-route-confirmed', action='store_true')
    parser.add_argument('--raw-learner-data-present', action='store_true')
    parser.add_argument('--protected-facts-present', action='store_true')
    parser.add_argument('--security-payloads-present', action='store_true')
    parser.add_argument('--public-claim-upgrade-requested', action='store_true')
    parser.add_argument('--output-dir', type=Path, help='Local/scratch output directory for the card.')
    parser.add_argument('--overwrite', action='store_true', help='Replace an existing card directory.')
    parser.add_argument('--json', action='store_true', help='Print machine-readable result.')
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def relative_to_root(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def default_output_dir(ticket_path: Path) -> Path:
    digest = sha256_file(ticket_path)[:12]
    return DEFAULT_OUTPUT_ROOT / f'aiedu-sr-003-{digest}'


def forbidden_argument_term(*values: str) -> str | None:
    text = ' '.join(value for value in values if value).lower()
    for term in sorted(FORBIDDEN_TERMS):
        if term in text:
            return term
    return None


def bounded_count_error(value: int, field: str, upper: int, *, minimum: int = 0) -> str | None:
    if value < minimum:
        return f'{field} must be at least {minimum}'
    if value > upper:
        return f'{field} cannot exceed {upper}'
    return None


def build_summary(record: dict[str, Any]) -> str:
    controls = record['window_controls']
    flags = record['risk_flags']
    return f"""# FT-0181 live-window stop/rollback card

| Field | Value |
|---|---|
| Window state | `{record['window_state']}` |
| Acceptance state | `{record['acceptance_state']}` |
| Evidence state | `{record['evidence_state']}` |
| Source ticket | `{record['source_post_decision_change_ticket']['reference']}` |
| Source truth class | `{record['source_truth_class']}` |
| Public claim ceiling | `{record['public_claim_ceiling']}` |
| Window day count | `{controls['window_day_count']}` |
| Allowed activity count | `{controls['allowed_activity_count']}` |
| Prohibited activity count | `{controls['prohibited_activity_count']}` |
| Stop trigger count | `{controls['stop_trigger_count']}` |
| Rollback step count | `{controls['rollback_step_count']}` |
| Rollback owner role count | `{controls['rollback_owner_role_count']}` |
| Evidence readout count | `{controls['evidence_readout_count']}` |
| No expansion confirmed | `{controls['no_expansion_confirmed']}` |
| Human pause confirmed | `{controls['human_pause_confirmed']}` |
| Fallback route confirmed | `{controls['fallback_route_confirmed']}` |
| Raw learner data present | `{flags['raw_learner_data_present']}` |
| Protected facts present | `{flags['protected_facts_present']}` |
| Security payloads present | `{flags['security_payloads_present']}` |
| Public claim upgrade requested | `{flags['public_claim_upgrade_requested']}` |
| Required next surface | `{record['required_next_surface']}` |

## Boundary

This local live-window card preserves only source-ticket hashes, bounded window
state, count classes, and route controls. It is not evidence, not `SRC2+`
acceptance, not custody evidence, not closure evidence, and not public-summary
support. Do not paste owner answer text, raw CSV rows, contact details, learner
identifiers, protected facts, small cells, security payloads, screenshots, or
claim language into this record.
"""


def source_ticket_snapshot(ticket_path: Path, ticket_data: dict[str, Any]) -> dict[str, Any]:
    return {
        'reference': relative_to_root(ticket_path),
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
        'live_window_effect': ticket_data.get('live_window_effect'),
        'revalidated_for_live_window_card': True,
    }


def build_live_window_card(
    *,
    ticket: Path,
    window_state: str,
    source_truth_class: str,
    window_day_count: int,
    allowed_activity_count: int,
    prohibited_activity_count: int,
    stop_trigger_count: int,
    rollback_step_count: int,
    rollback_owner_role_count: int,
    evidence_readout_count: int,
    public_claim_ceiling: str,
    no_expansion_confirmed: bool,
    human_pause_confirmed: bool,
    fallback_route_confirmed: bool,
    raw_learner_data_present: bool,
    protected_facts_present: bool,
    security_payloads_present: bool,
    public_claim_upgrade_requested: bool,
    operator_confirmation: str,
    output_dir: Path | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    ticket_path = ticket if ticket.is_absolute() else ROOT / ticket
    ticket_path = ticket_path.resolve()
    inside, parts = archive_relative(ticket_path, archive_root=ROOT)
    lane_error = field_scratch_lane_error(ticket_path, archive_root=ROOT, field_name='ticket')
    if lane_error or ticket_path.name != 'post-decision-change-ticket.json':
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'LIVE-WINDOW-CARD-TICKET-BLOCKED',
            'message': 'Live-window card requires a scratch-local post-decision-change-ticket.json source.',
            'ticket': relative_to_root(ticket_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if not ticket_path.exists() or not ticket_path.is_file():
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'LIVE-WINDOW-CARD-TICKET-MISSING',
            'message': 'Referenced post-decision change ticket does not exist.',
            'ticket': relative_to_root(ticket_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    try:
        ticket_data = load_json(ticket_path)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'LIVE-WINDOW-CARD-TICKET-BLOCKED',
            'message': 'Referenced post-decision change ticket is not readable JSON.',
            'error': str(exc),
            'ticket': relative_to_root(ticket_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    ticket_error = owner_post_decision_change_ticket_integrity_error(ticket_data, archive_root=ROOT)
    if ticket_error:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'LIVE-WINDOW-CARD-TICKET-BLOCKED',
            'message': 'Referenced post-decision change ticket failed integrity checks: ' + ticket_error,
            'ticket': relative_to_root(ticket_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    normalized_state = WINDOW_STATE_CHOICES[window_state]
    forbidden = forbidden_argument_term(window_state, source_truth_class, public_claim_ceiling, operator_confirmation)
    if forbidden:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'LIVE-WINDOW-CARD-ARGUMENT-BLOCKED',
            'message': f'Live-window arguments include forbidden raw/protected/contact term: {forbidden}',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if operator_confirmation.strip() != OPERATOR_CONFIRMATION:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'LIVE-WINDOW-CARD-CONFIRMATION-BLOCKED',
            'message': f'operator-confirmation must be {OPERATOR_CONFIRMATION!r}',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    for field, value, upper, minimum in [
        ('window-day-count', window_day_count, 14, 0),
        ('allowed-activity-count', allowed_activity_count, 5, 0),
        ('prohibited-activity-count', prohibited_activity_count, 10, 1),
        ('stop-trigger-count', stop_trigger_count, 10, 1),
        ('rollback-step-count', rollback_step_count, 10, 1),
        ('rollback-owner-role-count', rollback_owner_role_count, 5, 1),
        ('evidence-readout-count', evidence_readout_count, 7, 0),
    ]:
        err = bounded_count_error(value, field, upper, minimum=minimum)
        if err:
            raise ValueError(json.dumps({
                'ok': False,
                'outcome': 'LIVE-WINDOW-CARD-COUNT-BLOCKED',
                'message': err,
                'claim_ceiling': CLAIM_CEILING,
            }, indent=2))

    ticket_source_truth = ticket_data.get('source_truth_required')
    ticket_roles = int(ticket_data.get('rollback_owner_role_count') or 0)
    if rollback_owner_role_count < ticket_roles:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'LIVE-WINDOW-CARD-ROLLBACK-BLOCKED',
            'message': 'rollback-owner-role-count cannot be lower than the source ticket count.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if normalized_state in {'blocked_no_real_packet', 'blocked_incomplete_ticket'}:
        if source_truth_class != 'SRC0' or window_day_count != 0 or allowed_activity_count != 0:
            raise ValueError(json.dumps({
                'ok': False,
                'outcome': 'LIVE-WINDOW-CARD-BLOCKED-STATE-BLOCKED',
                'message': 'blocked window cards require SRC0, zero days, and zero allowed live activities.',
                'claim_ceiling': CLAIM_CEILING,
            }, indent=2))
    if normalized_state in LIVE_SOURCE_STATES:
        if ticket_data.get('ticket_state') != 'active_change':
            raise ValueError(json.dumps({
                'ok': False,
                'outcome': 'LIVE-WINDOW-CARD-TICKET-STATE-BLOCKED',
                'message': 'ready_for_real_packet tickets cannot source staged, active, paused, rolled-back, or completed live-window cards; record active_change only after the real source packet is accepted through the required gate.',
                'ticket_state': ticket_data.get('ticket_state'),
                'claim_ceiling': CLAIM_CEILING,
            }, indent=2))
        if source_truth_class not in POST_DECISION_SRC2_PLUS or ticket_source_truth not in POST_DECISION_SRC2_PLUS:
            raise ValueError(json.dumps({
                'ok': False,
                'outcome': 'LIVE-WINDOW-CARD-SOURCE-TRUTH-BLOCKED',
                'message': 'live, staged, paused, rolled-back, or completed cards require SRC2+ source truth from the source ticket.',
                'claim_ceiling': CLAIM_CEILING,
            }, indent=2))
        if window_day_count < 1 or allowed_activity_count < 1 or evidence_readout_count < 1:
            raise ValueError(json.dumps({
                'ok': False,
                'outcome': 'LIVE-WINDOW-CARD-ACTIVITY-BLOCKED',
                'message': 'live/staged window cards require at least one day, allowed activity, and aggregate readout class.',
                'claim_ceiling': CLAIM_CEILING,
            }, indent=2))
        if not (no_expansion_confirmed and human_pause_confirmed and fallback_route_confirmed):
            raise ValueError(json.dumps({
                'ok': False,
                'outcome': 'LIVE-WINDOW-CARD-CONTROL-BLOCKED',
                'message': 'live/staged window cards require no-expansion, human-pause, and fallback-route confirmations.',
                'claim_ceiling': CLAIM_CEILING,
            }, indent=2))
    if normalized_state == 'active' and ticket_data.get('live_window_required') is not True:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'LIVE-WINDOW-CARD-TICKET-BLOCKED',
            'message': 'active live-window cards require a source ticket with live_window_required=true.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if any([raw_learner_data_present, protected_facts_present, security_payloads_present, public_claim_upgrade_requested]):
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'LIVE-WINDOW-CARD-RISK-FLAG-BLOCKED',
            'message': 'Live-window card cannot proceed with raw/protected/security/public-claim-upgrade flags.',
            'risk_flags': {
                'raw_learner_data_present': raw_learner_data_present,
                'protected_facts_present': protected_facts_present,
                'security_payloads_present': security_payloads_present,
                'public_claim_upgrade_requested': public_claim_upgrade_requested,
            },
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    out_dir = output_dir or default_output_dir(ticket_path)
    out_dir = out_dir if out_dir.is_absolute() else ROOT / out_dir
    allowed, boundary = output_allowed(out_dir, archive_root=ROOT)
    if not allowed:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'LIVE-WINDOW-CARD-OUTPUT-BLOCKED',
            'message': f'Output directory is not allowed for local live-window cards: {boundary}',
            'output_dir': relative_to_root(out_dir),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if out_dir.exists():
        if not overwrite:
            raise ValueError(json.dumps({
                'ok': False,
                'outcome': 'LIVE-WINDOW-CARD-OUTPUT-EXISTS',
                'message': 'Output directory already exists; pass --overwrite to regenerate local scratch output.',
                'output_dir': relative_to_root(out_dir),
                'claim_ceiling': CLAIM_CEILING,
            }, indent=2))
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    record = {
        'card_type': 'FT-0181-live-window-stop-rollback-card',
        'card_version': REVISION,
        'created_at_utc': now,
        'followthrough_id': 'FT-0181',
        'service_record_id': 'AIEDU-SR-003',
        'window_state': normalized_state,
        'source_truth_class': source_truth_class,
        'acceptance_state': 'NOT_ACCEPTED',
        'evidence_state': 'not_evidence',
        'closure_effect': 'does_not_close_ft0181',
        'public_claim_effect': 'none',
        'ft0181_status': 'live',
        'operator_confirmation': operator_confirmation,
        'source_post_decision_change_ticket': source_ticket_snapshot(ticket_path, ticket_data),
        'window_controls': {
            'window_day_count': window_day_count,
            'allowed_activity_count': allowed_activity_count,
            'prohibited_activity_count': prohibited_activity_count,
            'stop_trigger_count': stop_trigger_count,
            'rollback_step_count': rollback_step_count,
            'rollback_owner_role_count': rollback_owner_role_count,
            'evidence_readout_count': evidence_readout_count,
            'no_expansion_confirmed': no_expansion_confirmed,
            'human_pause_confirmed': human_pause_confirmed,
            'fallback_route_confirmed': fallback_route_confirmed,
        },
        'readout_ready_states': sorted(READOUT_READY_STATES),
        'risk_flags': {
            'raw_learner_data_present': raw_learner_data_present,
            'protected_facts_present': protected_facts_present,
            'security_payloads_present': security_payloads_present,
            'public_claim_upgrade_requested': public_claim_upgrade_requested,
        },
        'content_minimization': {
            'copies_owner_answers': False,
            'copies_raw_csv_rows': False,
            'copies_post_decision_ticket_text': False,
            'copies_contact_details': False,
            'contains_window_counts_hashes_and_routes_only': True,
            'source_post_decision_ticket_revalidated': True,
        },
        'public_claim_ceiling': public_claim_ceiling,
        'claim_ceiling': CLAIM_CEILING,
        'required_next_surface': 'docs/30-operations/ft0181-end-of-window-readout-disposition-gate.md',
        'readout_effect': 'may_source_end_of_window_readout_only_after_terminal_window_state',
        'live_window_card_effect': 'does_not_modify_service_records_or_public_summaries_without_readout',
    }
    card_error = owner_live_window_card_integrity_error(record, archive_root=ROOT)
    if card_error:
        shutil.rmtree(out_dir)
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'LIVE-WINDOW-CARD-INTEGRITY-BLOCKED',
            'message': 'Generated live-window card failed integrity checks: ' + card_error,
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    card_path = out_dir / 'live-window-card.json'
    summary_path = out_dir / 'LIVE-WINDOW-CARD-SUMMARY.md'
    card_path.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    summary_path.write_text(build_summary(record), encoding='utf-8')
    return {
        'ok': True,
        'outcome': 'LIVE-WINDOW-CARD-RECORDED',
        'window_state': normalized_state,
        'source_truth_class': source_truth_class,
        'output_dir': relative_to_root(out_dir),
        'card_path': relative_to_root(card_path),
        'summary_path': relative_to_root(summary_path),
        'required_next_surface': record['required_next_surface'],
        'claim_ceiling': CLAIM_CEILING,
    }


def main() -> int:
    args = parse_args()
    try:
        result = build_live_window_card(
            ticket=args.ticket,
            window_state=args.window_state,
            source_truth_class=args.source_truth_class,
            window_day_count=args.window_day_count,
            allowed_activity_count=args.allowed_activity_count,
            prohibited_activity_count=args.prohibited_activity_count,
            stop_trigger_count=args.stop_trigger_count,
            rollback_step_count=args.rollback_step_count,
            rollback_owner_role_count=args.rollback_owner_role_count,
            evidence_readout_count=args.evidence_readout_count,
            public_claim_ceiling=args.public_claim_ceiling,
            no_expansion_confirmed=args.no_expansion_confirmed,
            human_pause_confirmed=args.human_pause_confirmed,
            fallback_route_confirmed=args.fallback_route_confirmed,
            raw_learner_data_present=args.raw_learner_data_present,
            protected_facts_present=args.protected_facts_present,
            security_payloads_present=args.security_payloads_present,
            public_claim_upgrade_requested=args.public_claim_upgrade_requested,
            operator_confirmation=args.operator_confirmation,
            output_dir=args.output_dir,
            overwrite=args.overwrite,
        )
    except ValueError as exc:
        print(str(exc))
        return 2
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(result['outcome'])
        print(result['card_path'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
