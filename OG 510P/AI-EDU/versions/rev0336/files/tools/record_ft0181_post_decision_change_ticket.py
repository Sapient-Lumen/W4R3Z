#!/usr/bin/env python3
"""Record a bounded local FT-0181 post-decision change ticket artifact.

This utility is the executable step after a valid first-packet decision-board
record. It captures only change classes, counts, route flags, hashes, and the
source decision reference. It deliberately copies no owner answers, raw CSV rows,
contact details, learner data, protected facts, security payloads, or public
claim text. The output is local/scratch only: it is not evidence, not custody,
not acceptance, not closure, and not public-summary support.
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
    activation_receipt_integrity_error,
    owner_first_packet_decision_integrity_error,
    owner_post_decision_change_ticket_integrity_error,
)

ROOT = Path(__file__).resolve().parents[1]
REVISION = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8')).get('revision', 'unknown')
DEFAULT_OUTPUT_ROOT = ROOT / 'scratch' / 'field' / 'ft0181' / 'owner-post-decision-change-tickets'
OPERATOR_CONFIRMATION = 'human-recorded-bounded-post-decision-change-ticket'
CLAIM_CEILING = (
    'Post-decision change-ticket record only; not evidence, not SRC2+ acceptance, '
    'not custody evidence, not closure evidence, not public-summary support, and '
    'not proof of learning, safety, access, workload, compliance, scale, or effectiveness.'
)

TICKET_STATE_CHOICES = {
    'blocked-no-real-packet': 'blocked_no_real_packet',
    'blocked-incomplete-board': 'blocked_incomplete_board',
    'ready-for-real-packet': 'ready_for_real_packet',
    'active-change': 'active_change',
    'rolled-back': 'rolled_back',
    'quarantined': 'quarantined',
}
CHANGE_CLASS_CHOICES = {
    'pct-a-trim': 'PCT-A-trim',
    'pct-b-suppress': 'PCT-B-suppress',
    'pct-c-sandbox-adjustment': 'PCT-C-sandbox-adjustment',
    'pct-d-bounded-pilot': 'PCT-D-bounded-pilot',
    'pct-x-quarantine': 'PCT-X-quarantine',
}
SOURCE_TRUTH_CHOICES = {'SRC0', 'SRC1', 'SRC2', 'SRC3', 'SRC4', 'SRCX', 'UNVERIFIED-OWNER-REPLY', 'not_evidence'}
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Record a local bounded FT-0181 post-decision change ticket.')
    parser.add_argument('--decision', required=True, type=Path, help='scratch/.../first-packet-decision.json produced by owner-first-packet-decision.')
    parser.add_argument('--ticket-state', required=True, choices=sorted(TICKET_STATE_CHOICES), help='Bounded ticket state; no free text.')
    parser.add_argument('--change-class', required=True, choices=sorted(CHANGE_CLASS_CHOICES), help='PCT change class label; no free text.')
    parser.add_argument('--source-truth-required', required=True, choices=sorted(SOURCE_TRUTH_CHOICES), help='Lowest source class required before the change can be active.')
    parser.add_argument('--public-claim-ceiling', default='example-only-no-outcome-claim', choices=sorted(PUBLIC_CEILING_CHOICES), help='Maximum public language class allowed by the ticket.')
    parser.add_argument('--allowed-change-count', type=int, required=True, help='Count of exact allowed changes; 0-5, no content copied.')
    parser.add_argument('--prohibited-change-count', type=int, required=True, help='Count of prohibited changes named locally; 1-10.')
    parser.add_argument('--rollback-trigger-count', type=int, required=True, help='Count of rollback/stop triggers named locally; 1-10.')
    parser.add_argument('--rollback-owner-role-count', type=int, default=1, help='Count of rollback owner roles named locally; 1-5.')
    parser.add_argument('--live-window-required', action='store_true', help='Required for active_change or PCT-D; routes only to the live-window stop/rollback card.')
    parser.add_argument('--activation-receipt', type=Path, help='Required for active_change: scratch/.../activation-receipt.json produced by owner-activation-receipt.')
    parser.add_argument('--operator-confirmation', required=True, help='Exact local confirmation token emitted by the router; not evidence.')
    parser.add_argument('--raw-learner-data-present', action='store_true')
    parser.add_argument('--protected-facts-present', action='store_true')
    parser.add_argument('--security-payloads-present', action='store_true')
    parser.add_argument('--public-claim-upgrade-requested', action='store_true')
    parser.add_argument('--output-dir', type=Path, help='Local/scratch output directory for the change ticket.')
    parser.add_argument('--overwrite', action='store_true', help='Replace an existing ticket directory.')
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


def default_output_dir(decision_path: Path) -> Path:
    digest = sha256_file(decision_path)[:12]
    return DEFAULT_OUTPUT_ROOT / f'aiedu-sr-003-{digest}'


def activation_receipt_snapshot(receipt_path: Path, receipt_data: dict[str, Any]) -> dict[str, Any]:
    return {
        'reference': relative_to_root(receipt_path),
        'receipt_sha256': sha256_file(receipt_path),
        'activation_state': receipt_data.get('activation_state'),
        'acceptance_state': receipt_data.get('acceptance_state'),
        'evidence_state': receipt_data.get('evidence_state'),
        'source_truth_class': receipt_data.get('source_truth_class'),
        'activation_counts': receipt_data.get('activation_counts'),
        'change_ticket_effect': receipt_data.get('change_ticket_effect'),
        'revalidated_for_active_change_ticket': True,
    }


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
    flags = record['risk_flags']
    counts = record['change_counts']
    return f"""# FT-0181 post-decision change-ticket record

| Field | Value |
|---|---|
| Ticket state | `{record['ticket_state']}` |
| Acceptance state | `{record['acceptance_state']}` |
| Evidence state | `{record['evidence_state']}` |
| Source decision | `{record['source_first_packet_decision']['reference']}` |
| Change class | `{record['change_class']}` |
| Source truth required | `{record['source_truth_required']}` |
| Public claim ceiling | `{record['public_claim_ceiling']}` |
| Allowed change count | `{counts['allowed_change_count']}` |
| Prohibited change count | `{counts['prohibited_change_count']}` |
| Rollback trigger count | `{counts['rollback_trigger_count']}` |
| Rollback owner role count | `{record['rollback_owner_role_count']}` |
| Live window required | `{record['live_window_required']}` |
| Raw learner data present | `{flags['raw_learner_data_present']}` |
| Protected facts present | `{flags['protected_facts_present']}` |
| Security payloads present | `{flags['security_payloads_present']}` |
| Public claim upgrade requested | `{flags['public_claim_upgrade_requested']}` |
| Required next surface | `{record['required_next_surface']}` |

## Boundary

This local change-ticket record preserves only change classes, counts, hashes,
route flags, and the source decision reference. It is not evidence, not `SRC2+`
acceptance, not custody evidence, not closure evidence, and not public-summary
support. Do not paste owner answer text, raw CSV rows, contact details, learner
identifiers, protected facts, small cells, security payloads, screenshots, or
claim language into this record.
"""


def build_change_ticket(
    *,
    decision: Path,
    ticket_state: str,
    change_class: str,
    source_truth_required: str,
    public_claim_ceiling: str,
    allowed_change_count: int,
    prohibited_change_count: int,
    rollback_trigger_count: int,
    rollback_owner_role_count: int,
    live_window_required: bool,
    raw_learner_data_present: bool,
    protected_facts_present: bool,
    security_payloads_present: bool,
    public_claim_upgrade_requested: bool,
    operator_confirmation: str,
    activation_receipt: Path | None = None,
    output_dir: Path | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    decision_path = decision if decision.is_absolute() else ROOT / decision
    decision_path = decision_path.resolve()
    inside, parts = archive_relative(decision_path, archive_root=ROOT)
    lane_error = field_scratch_lane_error(decision_path, archive_root=ROOT, field_name='decision')
    if lane_error or decision_path.name != 'first-packet-decision.json':
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-DECISION-CHANGE-TICKET-DECISION-BLOCKED',
            'message': lane_error or 'Post-decision change ticket requires a scratch-local first-packet-decision.json source.',
            'decision': relative_to_root(decision_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if not decision_path.exists() or not decision_path.is_file():
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-DECISION-CHANGE-TICKET-DECISION-MISSING',
            'message': 'Referenced first-packet decision does not exist.',
            'decision': relative_to_root(decision_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    try:
        decision_data = load_json(decision_path)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-DECISION-CHANGE-TICKET-DECISION-BLOCKED',
            'message': 'Referenced first-packet decision is not readable JSON.',
            'error': str(exc),
            'decision': relative_to_root(decision_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    decision_error = owner_first_packet_decision_integrity_error(decision_data, archive_root=ROOT)
    if decision_error:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-DECISION-CHANGE-TICKET-DECISION-BLOCKED',
            'message': 'Referenced first-packet decision failed integrity checks: ' + decision_error,
            'decision': relative_to_root(decision_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    forbidden = forbidden_argument_term(ticket_state, change_class, source_truth_required, public_claim_ceiling, operator_confirmation)
    if forbidden:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-DECISION-CHANGE-TICKET-ARGUMENT-BLOCKED',
            'message': f'Change-ticket arguments include forbidden raw/protected/contact term: {forbidden}',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if operator_confirmation.strip() != OPERATOR_CONFIRMATION:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-DECISION-CHANGE-TICKET-CONFIRMATION-BLOCKED',
            'message': f'operator-confirmation must be {OPERATOR_CONFIRMATION!r}',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    normalized_state = TICKET_STATE_CHOICES[ticket_state]
    normalized_class = CHANGE_CLASS_CHOICES[change_class]
    for field, value, upper, minimum in [
        ('allowed-change-count', allowed_change_count, 5, 0),
        ('prohibited-change-count', prohibited_change_count, 10, 1),
        ('rollback-trigger-count', rollback_trigger_count, 10, 1),
        ('rollback-owner-role-count', rollback_owner_role_count, 5, 1),
    ]:
        err = bounded_count_error(value, field, upper, minimum=minimum)
        if err:
            raise ValueError(json.dumps({
                'ok': False,
                'outcome': 'POST-DECISION-CHANGE-TICKET-COUNT-BLOCKED',
                'message': err,
                'claim_ceiling': CLAIM_CEILING,
            }, indent=2))
    if normalized_state in {'ready_for_real_packet', 'active_change'} and allowed_change_count < 1:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-DECISION-CHANGE-TICKET-COUNT-BLOCKED',
            'message': 'ready_for_real_packet and active_change tickets require at least one bounded allowed change class.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if normalized_state == 'active_change' and not live_window_required:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-DECISION-CHANGE-TICKET-LIVE-WINDOW-BLOCKED',
            'message': 'active_change requires a live-window stop/rollback card before use.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if normalized_class == 'PCT-D-bounded-pilot' and (source_truth_required not in {'SRC2', 'SRC3', 'SRC4'} or not live_window_required):
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-DECISION-CHANGE-TICKET-PILOT-BLOCKED',
            'message': 'PCT-D bounded pilot requires SRC2/SRC3/SRC4 source truth and a live-window stop/rollback card.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if normalized_class == 'PCT-X-quarantine' and normalized_state not in {'quarantined', 'rolled_back'}:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-DECISION-CHANGE-TICKET-QUARANTINE-BLOCKED',
            'message': 'PCT-X quarantine must use quarantined or rolled_back ticket state.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if any([raw_learner_data_present, protected_facts_present, security_payloads_present, public_claim_upgrade_requested]):
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-DECISION-CHANGE-TICKET-RISK-FLAG-BLOCKED',
            'message': 'Change ticket cannot proceed while raw/protected/security/public-claim-upgrade flags are present; block, quarantine, or revise the decision board first.',
            'risk_flags': {
                'raw_learner_data_present': raw_learner_data_present,
                'protected_facts_present': protected_facts_present,
                'security_payloads_present': security_payloads_present,
                'public_claim_upgrade_requested': public_claim_upgrade_requested,
            },
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    receipt_data: dict[str, Any] | None = None
    receipt_path: Path | None = None
    if normalized_state == 'active_change':
        if activation_receipt is None:
            raise ValueError(json.dumps({
                'ok': False,
                'outcome': 'POST-DECISION-CHANGE-TICKET-ACTIVATION-RECEIPT-REQUIRED',
                'message': 'active_change tickets require a scratch-local activation-receipt.json from owner-activation-receipt; do not activate directly from a local first-packet decision.',
                'claim_ceiling': CLAIM_CEILING,
            }, indent=2))
        receipt_path = activation_receipt if activation_receipt.is_absolute() else ROOT / activation_receipt
        receipt_path = receipt_path.resolve()
        inside_receipt, receipt_parts = archive_relative(receipt_path, archive_root=ROOT)
        receipt_lane_error = field_scratch_lane_error(receipt_path, archive_root=ROOT, field_name='activation_receipt')
        if receipt_lane_error or receipt_path.name != 'activation-receipt.json':
            raise ValueError(json.dumps({
                'ok': False,
                'outcome': 'POST-DECISION-CHANGE-TICKET-ACTIVATION-RECEIPT-BLOCKED',
                'message': 'active_change activation receipt must be a scratch-local activation-receipt.json.',
                'activation_receipt': relative_to_root(receipt_path),
                'claim_ceiling': CLAIM_CEILING,
            }, indent=2))
        if not receipt_path.exists() or not receipt_path.is_file():
            raise ValueError(json.dumps({
                'ok': False,
                'outcome': 'POST-DECISION-CHANGE-TICKET-ACTIVATION-RECEIPT-MISSING',
                'message': 'Referenced activation receipt does not exist.',
                'activation_receipt': relative_to_root(receipt_path),
                'claim_ceiling': CLAIM_CEILING,
            }, indent=2))
        try:
            receipt_data = load_json(receipt_path)
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(json.dumps({
                'ok': False,
                'outcome': 'POST-DECISION-CHANGE-TICKET-ACTIVATION-RECEIPT-BLOCKED',
                'message': 'Referenced activation receipt is not readable JSON.',
                'error': str(exc),
                'activation_receipt': relative_to_root(receipt_path),
                'claim_ceiling': CLAIM_CEILING,
            }, indent=2))
        receipt_error = activation_receipt_integrity_error(receipt_data, archive_root=ROOT)
        if receipt_error:
            raise ValueError(json.dumps({
                'ok': False,
                'outcome': 'POST-DECISION-CHANGE-TICKET-ACTIVATION-RECEIPT-BLOCKED',
                'message': 'Referenced activation receipt failed integrity checks: ' + receipt_error,
                'activation_receipt': relative_to_root(receipt_path),
                'claim_ceiling': CLAIM_CEILING,
            }, indent=2))
        receipt_decision = receipt_data.get('source_first_packet_decision', {})
        if receipt_decision.get('reference') != relative_to_root(decision_path) or receipt_decision.get('decision_sha256') != sha256_file(decision_path):
            raise ValueError(json.dumps({
                'ok': False,
                'outcome': 'POST-DECISION-CHANGE-TICKET-ACTIVATION-DECISION-MISMATCH',
                'message': 'Activation receipt must reference the same first-packet decision and hash as the requested active_change ticket.',
                'activation_receipt': relative_to_root(receipt_path),
                'decision': relative_to_root(decision_path),
                'claim_ceiling': CLAIM_CEILING,
            }, indent=2))
        if receipt_data.get('source_truth_class') != source_truth_required:
            raise ValueError(json.dumps({
                'ok': False,
                'outcome': 'POST-DECISION-CHANGE-TICKET-ACTIVATION-SOURCE-TRUTH-MISMATCH',
                'message': 'active_change source_truth_required must match the activation receipt source_truth_class.',
                'activation_receipt_source_truth_class': receipt_data.get('source_truth_class'),
                'source_truth_required': source_truth_required,
                'claim_ceiling': CLAIM_CEILING,
            }, indent=2))
    elif activation_receipt is not None:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-DECISION-CHANGE-TICKET-ACTIVATION-RECEIPT-NOT-ALLOWED',
            'message': 'activation-receipt is allowed only for active_change tickets.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    out_dir = output_dir or default_output_dir(decision_path)
    out_dir = out_dir if out_dir.is_absolute() else ROOT / out_dir
    allowed, boundary = output_allowed(out_dir, archive_root=ROOT)
    if not allowed:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-DECISION-CHANGE-TICKET-OUTPUT-BLOCKED',
            'message': f'Output directory is not allowed for local change-ticket artifacts: {boundary}',
            'output_dir': relative_to_root(out_dir),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if out_dir.exists():
        if not overwrite:
            raise ValueError(json.dumps({
                'ok': False,
                'outcome': 'POST-DECISION-CHANGE-TICKET-OUTPUT-EXISTS',
                'message': 'Output directory already exists; pass --overwrite to regenerate local scratch output.',
                'output_dir': relative_to_root(out_dir),
                'claim_ceiling': CLAIM_CEILING,
            }, indent=2))
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    source_decision = {
        'reference': relative_to_root(decision_path),
        'decision_sha256': sha256_file(decision_path),
        'board_state': decision_data.get('board_state'),
        'acceptance_state': decision_data.get('acceptance_state'),
        'evidence_state': decision_data.get('evidence_state'),
        'changed_slice_count': decision_data.get('changed_slice_count'),
        'rollback_owner_role_count': decision_data.get('rollback_owner_role_count'),
        'decision_slices': decision_data.get('decision_slices'),
        'source_truth_class': decision_data.get('source_workbench_review', {}).get('source_truth_class'),
        'change_ticket_effect': decision_data.get('change_ticket_effect'),
        'revalidated_for_change_ticket': True,
    }
    record = {
        'ticket_type': 'FT-0181-post-decision-change-ticket',
        'ticket_version': REVISION,
        'created_at_utc': now,
        'followthrough_id': 'FT-0181',
        'service_record_id': 'AIEDU-SR-003',
        'ticket_state': normalized_state,
        'change_class': normalized_class,
        'source_truth_required': source_truth_required,
        'acceptance_state': 'NOT_ACCEPTED',
        'evidence_state': 'not_evidence',
        'closure_effect': 'does_not_close_ft0181',
        'public_claim_effect': 'none',
        'ft0181_status': 'live',
        'operator_confirmation': operator_confirmation,
        'source_first_packet_decision': source_decision,
        'source_activation_receipt': activation_receipt_snapshot(receipt_path, receipt_data) if receipt_path is not None and receipt_data is not None else None,
        'change_counts': {
            'allowed_change_count': allowed_change_count,
            'prohibited_change_count': prohibited_change_count,
            'rollback_trigger_count': rollback_trigger_count,
        },
        'rollback_owner_role_count': rollback_owner_role_count,
        'live_window_required': live_window_required,
        'risk_flags': {
            'raw_learner_data_present': raw_learner_data_present,
            'protected_facts_present': protected_facts_present,
            'security_payloads_present': security_payloads_present,
            'public_claim_upgrade_requested': public_claim_upgrade_requested,
        },
        'content_minimization': {
            'copies_owner_answers': False,
            'copies_raw_csv_rows': False,
            'copies_first_packet_decision_text': False,
            'copies_contact_details': False,
            'contains_change_classes_counts_hashes_and_routes_only': True,
            'source_first_packet_decision_revalidated': True,
        },
        'public_claim_ceiling': public_claim_ceiling,
        'claim_ceiling': CLAIM_CEILING,
        'required_next_surface': 'docs/30-operations/ft0181-live-window-stop-rollback-card.md',
        'live_window_effect': 'may_source_live_window_stop_rollback_card_only',
        'change_ticket_effect': 'does_not_modify_service_records_without_live_window_card',
    }
    ticket_error = owner_post_decision_change_ticket_integrity_error(record, archive_root=ROOT)
    if ticket_error:
        shutil.rmtree(out_dir)
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-DECISION-CHANGE-TICKET-INTEGRITY-BLOCKED',
            'message': 'Generated post-decision change ticket failed integrity checks: ' + ticket_error,
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    ticket_path = out_dir / 'post-decision-change-ticket.json'
    summary_path = out_dir / 'POST-DECISION-CHANGE-TICKET-SUMMARY.md'
    ticket_path.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    summary_path.write_text(build_summary(record), encoding='utf-8')
    return {
        'ok': True,
        'outcome': 'POST-DECISION-CHANGE-TICKET-RECORDED',
        'ticket_state': normalized_state,
        'change_class': normalized_class,
        'output_dir': relative_to_root(out_dir),
        'ticket_path': relative_to_root(ticket_path),
        'summary_path': relative_to_root(summary_path),
        'required_next_surface': record['required_next_surface'],
        'claim_ceiling': CLAIM_CEILING,
    }


def main() -> int:
    args = parse_args()
    try:
        result = build_change_ticket(
            decision=args.decision,
            ticket_state=args.ticket_state,
            change_class=args.change_class,
            source_truth_required=args.source_truth_required,
            public_claim_ceiling=args.public_claim_ceiling,
            allowed_change_count=args.allowed_change_count,
            prohibited_change_count=args.prohibited_change_count,
            rollback_trigger_count=args.rollback_trigger_count,
            rollback_owner_role_count=args.rollback_owner_role_count,
            live_window_required=args.live_window_required,
            raw_learner_data_present=args.raw_learner_data_present,
            protected_facts_present=args.protected_facts_present,
            security_payloads_present=args.security_payloads_present,
            public_claim_upgrade_requested=args.public_claim_upgrade_requested,
            operator_confirmation=args.operator_confirmation,
            activation_receipt=args.activation_receipt,
            output_dir=args.output_dir,
            overwrite=args.overwrite,
        )
    except ValueError as exc:
        print(str(exc))
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"record_ft0181_post_decision_change_ticket: {result['outcome']} -> {result['ticket_path']}")
        print(f"required_next_surface: {result['required_next_surface']}")
        print(f"claim_ceiling: {CLAIM_CEILING}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
