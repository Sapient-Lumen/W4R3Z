#!/usr/bin/env python3
"""Record a bounded FT-0181 post-readout action recheck.

This is a scratch-only local artifact. It prevents a post-readout dispatch with a
past due/recheck date from silently expiring, being treated as owner action
completion, or becoming service-record/public/lifecycle/custody/closure movement.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from ft0181_field_guards import (
    POST_READOUT_RECHECK_OUTCOMES,
    archive_relative,
    field_scratch_lane_error,
    output_allowed,
    owner_post_readout_action_integrity_error,
    owner_post_readout_recheck_integrity_error,
)

ROOT = Path(__file__).resolve().parents[1]
REVISION = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8')).get('revision', 'unknown')
DEFAULT_OUTPUT_ROOT = ROOT / 'scratch' / 'field' / 'ft0181' / 'owner-post-readout-rechecks'
OPERATOR_CONFIRMATION = 'human-recorded-post-readout-recheck-no-closure'
CLAIM_CEILING = (
    'Post-readout recheck only; not evidence, not SRC2+ acceptance, not custody '
    'evidence, not closure evidence, and not public-summary support.'
)

OUTCOME_ALIASES = {
    'no-new-owner-context': 'no_new_owner_context',
    'no_new_owner_context': 'no_new_owner_context',
    'new-owner-context-available': 'new_owner_context_available',
    'new_owner_context_available': 'new_owner_context_available',
    'owner-action-complete-no-closure': 'owner_action_complete_no_closure',
    'owner_action_complete_no_closure': 'owner_action_complete_no_closure',
    'route-blocked-no-owner': 'route_blocked_no_owner',
    'route_blocked_no_owner': 'route_blocked_no_owner',
}

OUTCOME_TO_STATE = {
    'no_new_owner_context': 'RECHECK_RECORDED_NO_NEW_OWNER_CONTEXT',
    'new_owner_context_available': 'RECHECK_RECORDED_NEW_OWNER_CONTEXT_NOT_INTAKEN',
    'owner_action_complete_no_closure': 'OWNER_ACTION_RECHECKED_COMPLETE_NOT_CLOSURE',
    'route_blocked_no_owner': 'RECHECK_RECORDED_ROUTE_BLOCKED_NO_OWNER',
}

OUTCOME_TO_NEXT_STEP = {
    'no_new_owner_context': 'no field command; keep FT-0181 live and recheck only if new real owner context appears',
    'new_owner_context_available': 'rerun owner-field-next with the actual returned owner-context CSV path; do not intake from this recheck record',
    'owner_action_complete_no_closure': 'no field command; preserve action completion as local context only and do not close FT-0181',
    'route_blocked_no_owner': 'no field command; keep FT-0181 live as blocked by missing owner route or missing packet',
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Record a bounded FT-0181 post-readout action recheck.')
    parser.add_argument('--action', required=True, type=Path, help='scratch/.../post-readout-action.json from owner-post-readout-action.')
    parser.add_argument('--check-date', required=True, help='YYYY-MM-DD date of the owner-action/recheck check; must be on/after dispatch due_or_recheck_date.')
    parser.add_argument('--recheck-outcome', required=True, choices=sorted(OUTCOME_ALIASES), help='Bounded recheck outcome; dashed or underscored form accepted.')
    parser.add_argument('--reviewer-role-count', type=int, required=True, help='2-5 roles covered by the recheck.')
    parser.add_argument('--operator-confirmation', required=True, help=f'Exact token: {OPERATOR_CONFIRMATION}')
    parser.add_argument('--no-expansion-confirmed', action='store_true')
    parser.add_argument('--no-public-claim-upgrade', action='store_true')
    parser.add_argument('--no-service-record-edit', action='store_true')
    parser.add_argument('--no-lifecycle-change', action='store_true')
    parser.add_argument('--no-closure-from-recheck', action='store_true')
    parser.add_argument('--new-owner-context-held-outside-archive', action='store_true', help='Required only when recheck-outcome is new-owner-context-available; the returned context itself must be routed later via owner-field-next CSV=...')
    parser.add_argument('--raw-learner-data-present', action='store_true')
    parser.add_argument('--protected-facts-present', action='store_true')
    parser.add_argument('--security-payloads-present', action='store_true')
    parser.add_argument('--public-claim-upgrade-requested', action='store_true')
    parser.add_argument('--output-dir', type=Path, help='Local/scratch output directory for the recheck.')
    parser.add_argument('--overwrite', action='store_true')
    parser.add_argument('--json', action='store_true')
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


def default_output_dir(action_path: Path, check_date: str) -> Path:
    digest = sha256_file(action_path)[:12]
    return DEFAULT_OUTPUT_ROOT / f'aiedu-sr-003-{check_date}-{digest}'


def normalize_outcome(value: str) -> str:
    try:
        return OUTCOME_ALIASES[value]
    except KeyError as exc:
        raise ValueError(f'recheck-outcome {value!r} is not supported') from exc


def parse_date(value: str, field: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f'{field} must be YYYY-MM-DD') from exc


def source_action_snapshot(action_path: Path, action_data: dict[str, Any]) -> dict[str, Any]:
    return {
        'reference': relative_to_root(action_path),
        'action_sha256': sha256_file(action_path),
        'dispatch_state': action_data.get('dispatch_state'),
        'dispatch_lane': action_data.get('dispatch_lane'),
        'owner_action_class': action_data.get('owner_action_class'),
        'next_evidence_ask_class': action_data.get('next_evidence_ask_class'),
        'source_truth_class': action_data.get('source_truth_class'),
        'due_or_recheck_date': action_data.get('due_or_recheck_date'),
        'acceptance_state': action_data.get('acceptance_state'),
        'evidence_state': action_data.get('evidence_state'),
        'closure_effect': action_data.get('closure_effect'),
        'post_readout_action_effect': action_data.get('post_readout_action_effect'),
        'dispatch_counts': action_data.get('dispatch_counts'),
        'revalidated_for_post_readout_recheck': True,
    }


def build_summary(record: dict[str, Any]) -> str:
    source = record['source_post_readout_action']
    counts = record['recheck_counts']
    return f"""# FT-0181 post-readout action recheck

| Field | Value |
|---|---|
| Recheck state | `{record['recheck_state']}` |
| Recheck outcome | `{record['recheck_outcome']}` |
| Source dispatch | `{source['reference']}` |
| Source dispatch lane | `{source['dispatch_lane']}` |
| Source due/recheck date | `{source['due_or_recheck_date']}` |
| Check date | `{record['check_date']}` |
| Reviewer role count | `{counts['reviewer_role_count']}` |
| New owner context held outside archive | `{record['new_owner_context_held_outside_archive']}` |
| Required next action | `{record['required_next_action']}` |

## Boundary

This local recheck records only whether the owner-held action/recheck lane has
new real owner context after the dispatch due date. It is not evidence, not
accepted `SRC2+`, not custody, not a service-record edit, not a lifecycle move,
not public-summary support, and not FT-0181 closure.
"""


def build_post_readout_recheck(
    *,
    action: Path,
    check_date: str,
    recheck_outcome: str,
    reviewer_role_count: int,
    operator_confirmation: str,
    no_expansion_confirmed: bool,
    no_public_claim_upgrade: bool,
    no_service_record_edit: bool,
    no_lifecycle_change: bool,
    no_closure_from_recheck: bool,
    new_owner_context_held_outside_archive: bool,
    raw_learner_data_present: bool,
    protected_facts_present: bool,
    security_payloads_present: bool,
    public_claim_upgrade_requested: bool,
    output_dir: Path | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    outcome = normalize_outcome(recheck_outcome)
    action_path = action if action.is_absolute() else ROOT / action
    action_path = action_path.resolve()
    inside, parts = archive_relative(action_path, archive_root=ROOT)
    lane_error = field_scratch_lane_error(action_path, archive_root=ROOT, field_name='action')
    if lane_error or action_path.name != 'post-readout-action.json':
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-RECHECK-SOURCE-BLOCKED',
            'message': 'Post-readout recheck requires a scratch-local post-readout-action.json source.',
            'action': relative_to_root(action_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if not action_path.exists() or not action_path.is_file():
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-RECHECK-SOURCE-MISSING',
            'message': 'Referenced post-readout action dispatch does not exist.',
            'action': relative_to_root(action_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    try:
        action_data = load_json(action_path)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-RECHECK-SOURCE-BLOCKED',
            'message': 'Referenced post-readout action dispatch is not readable JSON.',
            'error': str(exc),
            'action': relative_to_root(action_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    action_error = owner_post_readout_action_integrity_error(action_data, archive_root=ROOT)
    if action_error:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-RECHECK-SOURCE-BLOCKED',
            'message': 'Referenced post-readout action dispatch failed integrity checks: ' + action_error,
            'action': relative_to_root(action_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    check_day = parse_date(check_date, 'check-date')
    due_day = parse_date(str(action_data.get('due_or_recheck_date') or ''), 'source due_or_recheck_date')
    if check_day < due_day:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-RECHECK-TOO-EARLY-BLOCKED',
            'message': 'Post-readout recheck cannot be recorded before the dispatch due_or_recheck_date.',
            'check_date': check_day.isoformat(),
            'source_due_or_recheck_date': due_day.isoformat(),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if operator_confirmation.strip() != OPERATOR_CONFIRMATION:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-RECHECK-CONFIRMATION-BLOCKED',
            'message': f'operator-confirmation must be {OPERATOR_CONFIRMATION!r}',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if not (no_expansion_confirmed and no_public_claim_upgrade and no_service_record_edit and no_lifecycle_change and no_closure_from_recheck):
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-RECHECK-FIREBREAK-BLOCKED',
            'message': 'Recheck requires explicit no-expansion/no-public/no-service/no-lifecycle/no-closure confirmations.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if any([raw_learner_data_present, protected_facts_present, security_payloads_present, public_claim_upgrade_requested]):
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-RECHECK-RISK-FLAG-BLOCKED',
            'message': 'Post-readout recheck cannot proceed with raw/protected/security/public-claim-upgrade flags.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if outcome == 'new_owner_context_available' and not new_owner_context_held_outside_archive:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-RECHECK-NEW-CONTEXT-BOUNDARY-BLOCKED',
            'message': 'New owner context cannot be copied into the recheck; hold it outside the archive and route the actual CSV through owner-field-next CSV=...',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if outcome != 'new_owner_context_available' and new_owner_context_held_outside_archive:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-RECHECK-NEW-CONTEXT-FLAG-BLOCKED',
            'message': 'new-owner-context-held-outside-archive is only allowed with new_owner_context_available.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    out_dir = output_dir or default_output_dir(action_path, check_day.isoformat())
    out_dir = out_dir if out_dir.is_absolute() else ROOT / out_dir
    allowed, boundary = output_allowed(out_dir, archive_root=ROOT)
    if not allowed:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-RECHECK-OUTPUT-BLOCKED',
            'message': f'Output directory is not allowed for local post-readout rechecks: {boundary}',
            'output_dir': relative_to_root(out_dir),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if out_dir.exists():
        if not overwrite:
            raise ValueError(json.dumps({
                'ok': False,
                'outcome': 'POST-READOUT-RECHECK-OUTPUT-EXISTS',
                'message': 'Output directory already exists; pass --overwrite to regenerate local scratch output.',
                'output_dir': relative_to_root(out_dir),
                'claim_ceiling': CLAIM_CEILING,
            }, indent=2))
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    record = {
        'recheck_type': 'FT-0181-post-readout-action-recheck',
        'recheck_version': REVISION,
        'created_at_utc': now,
        'followthrough_id': 'FT-0181',
        'service_record_id': 'AIEDU-SR-003',
        'recheck_state': OUTCOME_TO_STATE[outcome],
        'recheck_outcome': outcome,
        'check_date': check_day.isoformat(),
        'source_truth_class': action_data.get('source_truth_class'),
        'acceptance_state': 'NOT_ACCEPTED',
        'evidence_state': 'not_evidence',
        'closure_permitted': False,
        'closure_effect': 'does_not_close_ft0181',
        'public_claim_effect': 'does_not_upgrade_public_claims',
        'service_record_effect': 'does_not_edit_service_records_from_recheck',
        'lifecycle_effect': 'does_not_change_lifecycle_from_recheck',
        'ft0181_status': 'live',
        'operator_confirmation': operator_confirmation,
        'source_post_readout_action': source_action_snapshot(action_path, action_data),
        'recheck_counts': {
            'reviewer_role_count': reviewer_role_count,
            'new_owner_context_count': 1 if outcome == 'new_owner_context_available' else 0,
        },
        'new_owner_context_held_outside_archive': bool(new_owner_context_held_outside_archive),
        'required_next_action': OUTCOME_TO_NEXT_STEP[outcome],
        'allowed_next_steps': [
            'owner-field-next-with-actual-returned-csv-only' if outcome == 'new_owner_context_available' else 'wait-for-new-real-owner-context',
            'local-recheck-record-only',
        ],
        'prohibited_next_steps': [
            'service-record-edit-from-recheck',
            'public-claim-upgrade-from-recheck',
            'lifecycle-change-from-recheck',
            'custody-or-acceptance-from-recheck',
            'ft0181-closure-from-recheck',
            'copy-owner-context-into-recheck',
        ],
        'no_expansion_confirmation': True,
        'no_public_claim_upgrade': True,
        'no_service_record_edit_from_recheck': True,
        'no_lifecycle_change_from_recheck': True,
        'no_closure_from_recheck': True,
        'risk_flags': {
            'raw_learner_data_present': False,
            'protected_facts_present': False,
            'security_payloads_present': False,
            'public_claim_upgrade_requested': False,
        },
        'content_minimization': {
            'copies_owner_answers': False,
            'copies_raw_csv_rows': False,
            'copies_live_window_notes': False,
            'copies_contact_details': False,
            'copies_public_claim_text': False,
            'copies_new_owner_context': False,
            'contains_status_counts_hashes_and_due_dates_only': True,
            'source_post_readout_action_revalidated': True,
        },
        'claim_ceiling': CLAIM_CEILING,
        'post_readout_recheck_effect': 'may_route_new_owner_context_to_router_or_stop_only',
        'closure_boundary': 'This local post-readout recheck does not close FT-0181 and does not prove service claims, learning, safety, access, workload, compliance, scale, or effectiveness.',
        'output_boundary': boundary,
    }
    integrity_error = owner_post_readout_recheck_integrity_error(record, archive_root=ROOT)
    if integrity_error:
        shutil.rmtree(out_dir, ignore_errors=True)
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-RECHECK-INTEGRITY-BLOCKED',
            'message': integrity_error,
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    (out_dir / 'post-readout-recheck.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    (out_dir / 'POST-READOUT-RECHECK-SUMMARY.md').write_text(build_summary(record), encoding='utf-8')
    return {
        'ok': True,
        'outcome': 'POST-READOUT-RECHECK-RECORDED',
        'post_readout_recheck': relative_to_root(out_dir / 'post-readout-recheck.json'),
        'summary': relative_to_root(out_dir / 'POST-READOUT-RECHECK-SUMMARY.md'),
        'recheck_outcome': outcome,
        'source_post_readout_action': relative_to_root(action_path),
        'claim_ceiling': CLAIM_CEILING,
    }


def main() -> None:
    args = parse_args()
    try:
        result = build_post_readout_recheck(
            action=args.action,
            check_date=args.check_date,
            recheck_outcome=args.recheck_outcome,
            reviewer_role_count=args.reviewer_role_count,
            operator_confirmation=args.operator_confirmation,
            no_expansion_confirmed=args.no_expansion_confirmed,
            no_public_claim_upgrade=args.no_public_claim_upgrade,
            no_service_record_edit=args.no_service_record_edit,
            no_lifecycle_change=args.no_lifecycle_change,
            no_closure_from_recheck=args.no_closure_from_recheck,
            new_owner_context_held_outside_archive=args.new_owner_context_held_outside_archive,
            raw_learner_data_present=args.raw_learner_data_present,
            protected_facts_present=args.protected_facts_present,
            security_payloads_present=args.security_payloads_present,
            public_claim_upgrade_requested=args.public_claim_upgrade_requested,
            output_dir=args.output_dir,
            overwrite=args.overwrite,
        )
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
