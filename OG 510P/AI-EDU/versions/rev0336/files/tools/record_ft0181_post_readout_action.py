#!/usr/bin/env python3
"""Record a bounded FT-0181 post-readout action dispatch.

This is a local scratch artifact only. It prevents a terminal live-window readout
from becoming silent service-record mutation, lifecycle movement, public-language
change, custody, acceptance, or closure. It records only source hashes, action
classes, bounded counts, and a due/recheck date.
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
    LIVE_WINDOW_READOUT_SOURCE_TRUTH_CLASSES,
    POST_READOUT_ACTION_DISPATCH_LANES,
    POST_READOUT_NEXT_ASK_CLASSES,
    POST_READOUT_OWNER_ACTION_BY_LANE,
    POST_READOUT_PUBLIC_LANGUAGE_ACTIONS,
    READOUT_DISPOSITION_TO_ACTION_LANE,
    archive_relative,
    field_scratch_lane_error,
    output_allowed,
    owner_live_window_readout_integrity_error,
    owner_post_readout_action_integrity_error,
)

ROOT = Path(__file__).resolve().parents[1]
REVISION = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8')).get('revision', 'unknown')
DEFAULT_OUTPUT_ROOT = ROOT / 'scratch' / 'field' / 'ft0181' / 'owner-post-readout-actions'
OPERATOR_CONFIRMATION = 'human-recorded-post-readout-action-no-closure'
CLAIM_CEILING = (
    'Post-readout action dispatch only; not evidence, not SRC2+ acceptance, '
    'not custody evidence, not closure evidence, and not public-summary support.'
)

LANE_ALIASES = {
    'blocked-no-real-packet': 'blocked_no_real_packet',
    'blocked_no_real_packet': 'blocked_no_real_packet',
    'stop': 'stop',
    'rollback-confirmed': 'rollback_confirmed',
    'rollback_confirmed': 'rollback_confirmed',
    'rerun-narrower': 'rerun_narrower',
    'rerun_narrower': 'rerun_narrower',
    'continue-same-ceiling': 'continue_same_ceiling',
    'continue_same_ceiling': 'continue_same_ceiling',
    'quarantine': 'quarantine',
    'no-change-trim': 'no_change_trim',
    'no_change_trim': 'no_change_trim',
}

LANE_TO_STATE = {
    'blocked_no_real_packet': 'BLOCKED_NO_REAL_READOUT',
    'stop': 'DISPATCH_RECORDED_NOT_CLOSURE',
    'rollback_confirmed': 'ROLLBACK_CONFIRMED_NOT_CLOSURE',
    'rerun_narrower': 'DISPATCH_RECORDED_NOT_CLOSURE',
    'continue_same_ceiling': 'DISPATCH_RECORDED_NOT_CLOSURE',
    'quarantine': 'QUARANTINED',
    'no_change_trim': 'DISPATCH_RECORDED_NOT_CLOSURE',
}

LANE_TO_NEXT_ASK = {
    'blocked_no_real_packet': 'owner-packet-route-repair',
    'stop': 'fallback-availability-check',
    'rollback_confirmed': 'fallback-availability-check',
    'rerun_narrower': 'rerun-narrower-owner-packet',
    'continue_same_ceiling': 'bounded-owner-recheck',
    'quarantine': 'quarantine-resolution-ask',
    'no_change_trim': 'no-new-ask-with-trim-record',
}

LANE_TO_PUBLIC_ACTION = {
    'blocked_no_real_packet': 'frozen-example-only',
    'stop': 'suppress-public-language',
    'rollback_confirmed': 'narrow-existing-language',
    'rerun_narrower': 'frozen-example-only',
    'continue_same_ceiling': 'frozen-example-only',
    'quarantine': 'suppress-public-language',
    'no_change_trim': 'no-public-language-change',
}

DEFAULT_DROP_CLASSES = [
    'drop-raw-learner-material',
    'drop-protected-route-facts',
    'drop-small-cell-material',
    'drop-security-payload-material',
    'drop-vendor-authored-outcome-claims',
]

DEFAULT_REASK_CLASSES_BY_LANE = {
    'rerun_narrower': ['reask-only-minimized-decision-field'],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Record a bounded FT-0181 post-readout action dispatch.')
    parser.add_argument('--readout', required=True, type=Path, help='scratch/.../live-window-readout.json from owner-live-window-readout.')
    parser.add_argument('--dispatch-lane', required=True, choices=sorted(LANE_ALIASES), help='Post-readout lane; dashed or underscored forms accepted.')
    parser.add_argument('--source-truth-class', required=True, choices=sorted(LIVE_WINDOW_READOUT_SOURCE_TRUTH_CLASSES), help='Must match source readout.')
    parser.add_argument('--allowed-action-count', type=int, required=True, help='0-5 allowed actions before next review; most lanes need at least 1.')
    parser.add_argument('--prohibited-action-count', type=int, required=True, help='2-10 prohibited actions before next review.')
    parser.add_argument('--field-to-reask-count', type=int, required=True, help='0-8 bounded re-ask field classes.')
    parser.add_argument('--field-to-drop-count', type=int, required=True, help='0-8 field classes dropped from future asks; rerun/no-change require at least 1.')
    parser.add_argument('--reviewer-role-count', type=int, required=True, help='2-5 reviewer/owner roles covered by dispatch.')
    parser.add_argument('--unresolved-disagreement-count', type=int, default=0, help='0-5 unresolved action disagreements.')
    parser.add_argument('--due-or-recheck-date', required=True, help='YYYY-MM-DD due/recheck date for the owner action lane.')
    parser.add_argument('--owner-action-class', choices=sorted(set(POST_READOUT_OWNER_ACTION_BY_LANE.values())), help='Optional override; defaults from lane and must match lane.')
    parser.add_argument('--next-evidence-ask-class', choices=sorted(POST_READOUT_NEXT_ASK_CLASSES), help='Optional override; defaults from lane.')
    parser.add_argument('--public-language-action', choices=sorted(POST_READOUT_PUBLIC_LANGUAGE_ACTIONS), help='Optional override; defaults from lane.')
    parser.add_argument('--operator-confirmation', required=True, help=f'Exact token: {OPERATOR_CONFIRMATION}')
    parser.add_argument('--no-expansion-confirmed', action='store_true')
    parser.add_argument('--no-public-claim-upgrade', action='store_true')
    parser.add_argument('--no-service-record-edit', action='store_true')
    parser.add_argument('--no-lifecycle-change', action='store_true')
    parser.add_argument('--no-closure-from-dispatch', action='store_true')
    parser.add_argument('--raw-learner-data-present', action='store_true')
    parser.add_argument('--protected-facts-present', action='store_true')
    parser.add_argument('--security-payloads-present', action='store_true')
    parser.add_argument('--public-claim-upgrade-requested', action='store_true')
    parser.add_argument('--output-dir', type=Path, help='Local/scratch output directory for the dispatch.')
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


def default_output_dir(readout_path: Path) -> Path:
    digest = sha256_file(readout_path)[:12]
    return DEFAULT_OUTPUT_ROOT / f'aiedu-sr-003-{digest}'


def normalize_lane(value: str) -> str:
    try:
        return LANE_ALIASES[value]
    except KeyError as exc:
        raise ValueError(f'dispatch-lane {value!r} is not supported') from exc


def source_readout_snapshot(readout_path: Path, readout_data: dict[str, Any]) -> dict[str, Any]:
    return {
        'reference': relative_to_root(readout_path),
        'readout_sha256': sha256_file(readout_path),
        'readout_state': readout_data.get('readout_state'),
        'window_disposition': readout_data.get('window_disposition'),
        'source_truth_class': readout_data.get('source_truth_class'),
        'public_claim_ceiling': readout_data.get('public_claim_ceiling'),
        'acceptance_state': readout_data.get('acceptance_state'),
        'evidence_state': readout_data.get('evidence_state'),
        'readout_effect': readout_data.get('readout_effect'),
        'closure_effect': readout_data.get('closure_effect'),
        'readout_counts': readout_data.get('readout_counts'),
        'revalidated_for_post_readout_action': True,
    }


def build_summary(record: dict[str, Any]) -> str:
    counts = record['dispatch_counts']
    return f"""# FT-0181 post-readout action dispatch

| Field | Value |
|---|---|
| Dispatch state | `{record['dispatch_state']}` |
| Dispatch lane | `{record['dispatch_lane']}` |
| Owner action class | `{record['owner_action_class']}` |
| Source readout | `{record['source_live_window_readout']['reference']}` |
| Source disposition | `{record['source_live_window_readout']['window_disposition']}` |
| Source truth class | `{record['source_truth_class']}` |
| Public language action | `{record['public_language_action']}` |
| Due or recheck date | `{record['due_or_recheck_date']}` |
| Allowed action count | `{counts['allowed_action_count']}` |
| Prohibited action count | `{counts['prohibited_action_count']}` |
| Field-to-reask count | `{counts['field_to_reask_count']}` |
| Field-to-drop count | `{counts['field_to_drop_count']}` |
| Reviewer role count | `{counts['reviewer_role_count']}` |
| Closure permitted | `{record['closure_permitted']}` |
| Required next surface | `{record['required_next_surface']}` |

## Boundary

This local dispatch records only a bounded owner-action/recheck lane from one
hash-checked terminal readout. It is not evidence, not custody, not accepted
`SRC2+`, not a service-record edit, not a lifecycle move, not public-summary
support, and not FT-0181 closure.
"""


def build_post_readout_action(
    *,
    readout: Path,
    dispatch_lane: str,
    source_truth_class: str,
    allowed_action_count: int,
    prohibited_action_count: int,
    field_to_reask_count: int,
    field_to_drop_count: int,
    reviewer_role_count: int,
    unresolved_disagreement_count: int,
    due_or_recheck_date: str,
    owner_action_class: str | None,
    next_evidence_ask_class: str | None,
    public_language_action: str | None,
    no_expansion_confirmed: bool,
    no_public_claim_upgrade: bool,
    no_service_record_edit: bool,
    no_lifecycle_change: bool,
    no_closure_from_dispatch: bool,
    raw_learner_data_present: bool,
    protected_facts_present: bool,
    security_payloads_present: bool,
    public_claim_upgrade_requested: bool,
    operator_confirmation: str,
    output_dir: Path | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    lane = normalize_lane(dispatch_lane)
    readout_path = readout if readout.is_absolute() else ROOT / readout
    readout_path = readout_path.resolve()
    inside, parts = archive_relative(readout_path, archive_root=ROOT)
    lane_error = field_scratch_lane_error(readout_path, archive_root=ROOT, field_name='readout')
    if lane_error or readout_path.name != 'live-window-readout.json':
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-ACTION-SOURCE-BLOCKED',
            'message': 'Post-readout action requires a scratch-local live-window-readout.json source.',
            'readout': relative_to_root(readout_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if not readout_path.exists() or not readout_path.is_file():
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-ACTION-SOURCE-MISSING',
            'message': 'Referenced live-window readout does not exist.',
            'readout': relative_to_root(readout_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    try:
        readout_data = load_json(readout_path)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-ACTION-SOURCE-BLOCKED',
            'message': 'Referenced readout is not readable JSON.',
            'error': str(exc),
            'readout': relative_to_root(readout_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    readout_error = owner_live_window_readout_integrity_error(readout_data, archive_root=ROOT)
    if readout_error:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-ACTION-SOURCE-BLOCKED',
            'message': 'Referenced live-window readout failed integrity checks: ' + readout_error,
            'readout': relative_to_root(readout_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    expected_lane = READOUT_DISPOSITION_TO_ACTION_LANE.get(readout_data.get('window_disposition'))
    if lane != expected_lane:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-ACTION-LANE-BLOCKED',
            'message': f'Dispatch lane {lane!r} does not match source readout disposition {readout_data.get("window_disposition")!r}.',
            'expected_lane': expected_lane,
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if source_truth_class != readout_data.get('source_truth_class'):
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-ACTION-SOURCE-TRUTH-BLOCKED',
            'message': 'Dispatch source-truth class must match the terminal live-window readout.',
            'readout_source_truth_class': readout_data.get('source_truth_class'),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if operator_confirmation.strip() != OPERATOR_CONFIRMATION:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-ACTION-CONFIRMATION-BLOCKED',
            'message': f'operator-confirmation must be {OPERATOR_CONFIRMATION!r}',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if not (no_expansion_confirmed and no_public_claim_upgrade and no_service_record_edit and no_lifecycle_change and no_closure_from_dispatch):
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-ACTION-FIREBREAK-BLOCKED',
            'message': 'Dispatch requires explicit no-expansion/no-public/no-service/no-lifecycle/no-closure confirmations.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if any([raw_learner_data_present, protected_facts_present, security_payloads_present, public_claim_upgrade_requested]):
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-ACTION-RISK-FLAG-BLOCKED',
            'message': 'Post-readout action cannot proceed with raw/protected/security/public-claim-upgrade flags.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    owner_action = owner_action_class or POST_READOUT_OWNER_ACTION_BY_LANE[lane]
    expected_owner_action = POST_READOUT_OWNER_ACTION_BY_LANE[lane]
    next_ask = next_evidence_ask_class or LANE_TO_NEXT_ASK[lane]
    expected_next_ask = LANE_TO_NEXT_ASK[lane]
    public_action = public_language_action or LANE_TO_PUBLIC_ACTION[lane]
    expected_public_action = LANE_TO_PUBLIC_ACTION[lane]
    lane_class_errors = []
    if owner_action != expected_owner_action:
        lane_class_errors.append(f'owner_action_class={owner_action!r} must match {expected_owner_action!r}')
    if next_ask != expected_next_ask:
        lane_class_errors.append(f'next_evidence_ask_class={next_ask!r} must match {expected_next_ask!r}')
    if public_action != expected_public_action:
        lane_class_errors.append(f'public_language_action={public_action!r} must match {expected_public_action!r}')
    if lane_class_errors:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-ACTION-LANE-CLASS-BLOCKED',
            'message': f'Dispatch lane {lane!r} requires its bounded owner-action, next-ask, and public-language classes.',
            'errors': lane_class_errors,
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    reask_classes = list(DEFAULT_REASK_CLASSES_BY_LANE.get(lane, []))[:field_to_reask_count]
    if field_to_reask_count > len(reask_classes):
        reask_classes.extend(f'reask-minimized-decision-field-{i}' for i in range(len(reask_classes) + 1, field_to_reask_count + 1))
    drop_classes = DEFAULT_DROP_CLASSES[:]
    if field_to_drop_count > len(drop_classes):
        drop_classes.extend(f'drop-decision-neutral-field-{i}' for i in range(len(drop_classes) + 1, field_to_drop_count + 1))
    elif field_to_drop_count > 0:
        # Keep all mandatory forbidden-material drop classes visible even when the bounded count is smaller.
        drop_classes = DEFAULT_DROP_CLASSES[:]

    out_dir = output_dir or default_output_dir(readout_path)
    out_dir = out_dir if out_dir.is_absolute() else ROOT / out_dir
    allowed, boundary = output_allowed(out_dir, archive_root=ROOT)
    if not allowed:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-ACTION-OUTPUT-BLOCKED',
            'message': f'Output directory is not allowed for local post-readout actions: {boundary}',
            'output_dir': relative_to_root(out_dir),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if out_dir.exists():
        if not overwrite:
            raise ValueError(json.dumps({
                'ok': False,
                'outcome': 'POST-READOUT-ACTION-OUTPUT-EXISTS',
                'message': 'Output directory already exists; pass --overwrite to regenerate local scratch output.',
                'output_dir': relative_to_root(out_dir),
                'claim_ceiling': CLAIM_CEILING,
            }, indent=2))
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    record = {
        'action_type': 'FT-0181-post-readout-action-dispatch',
        'action_version': REVISION,
        'created_at_utc': now,
        'followthrough_id': 'FT-0181',
        'service_record_id': 'AIEDU-SR-003',
        'dispatch_state': LANE_TO_STATE[lane],
        'dispatch_lane': lane,
        'owner_action_class': owner_action,
        'source_truth_class': source_truth_class,
        'public_language_action': public_action,
        'acceptance_state': 'NOT_ACCEPTED',
        'evidence_state': 'not_evidence',
        'closure_permitted': False,
        'closure_effect': 'does_not_close_ft0181',
        'public_claim_effect': 'does_not_upgrade_public_claims',
        'service_record_effect': 'does_not_edit_service_records_without_separate_owner_action',
        'lifecycle_effect': 'does_not_change_lifecycle_without_separate_owner_action',
        'ft0181_status': 'live',
        'operator_confirmation': operator_confirmation,
        'source_live_window_readout': source_readout_snapshot(readout_path, readout_data),
        'dispatch_counts': {
            'allowed_action_count': allowed_action_count,
            'prohibited_action_count': prohibited_action_count,
            'field_to_reask_count': field_to_reask_count,
            'field_to_drop_count': field_to_drop_count,
            'reviewer_role_count': reviewer_role_count,
            'unresolved_disagreement_count': unresolved_disagreement_count,
        },
        'next_evidence_ask_class': next_ask,
        'next_evidence_ask': {
            'owner_route_class': 'accountable-owner-route-or-route-block-record',
            'date_range_class': 'same-or-narrower-window-date-range',
            'packet_ceiling': 'aggregate-owner-attested-fields-only',
            'decision_question_class': next_ask,
            'field_minimization_rule': 'ask only fields needed for the named dispatch lane and drop forbidden/materially neutral fields',
            'fallback_if_unavailable': 'record route block or keep FT-0181 live without service/public/closure change',
        },
        'fields_to_reask_classes': reask_classes,
        'fields_to_drop_classes': drop_classes,
        'due_or_recheck_date': due_or_recheck_date,
        'no_expansion_confirmation': True,
        'no_public_claim_upgrade': True,
        'no_service_record_edit_from_dispatch': True,
        'no_lifecycle_change_from_dispatch': True,
        'no_closure_from_dispatch': True,
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
            'contains_action_classes_counts_hashes_and_due_dates_only': True,
            'source_live_window_readout_revalidated': True,
        },
        'claim_ceiling': CLAIM_CEILING,
        'required_next_surface': 'owner-held action/recheck outside archive, then rerun owner-field-next only with new real owner context',
        'post_readout_action_effect': 'may_source_owner_action_or_recheck_only',
        'closure_boundary': 'This local post-readout action dispatch does not close FT-0181 and does not prove service claims, learning, safety, access, workload, compliance, scale, or effectiveness.',
        'output_boundary': boundary,
    }
    integrity_error = owner_post_readout_action_integrity_error(record, archive_root=ROOT)
    if integrity_error:
        shutil.rmtree(out_dir, ignore_errors=True)
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-ACTION-INTEGRITY-BLOCKED',
            'message': integrity_error,
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    (out_dir / 'post-readout-action.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    (out_dir / 'POST-READOUT-ACTION-SUMMARY.md').write_text(build_summary(record), encoding='utf-8')
    return {
        'ok': True,
        'outcome': 'POST-READOUT-ACTION-DISPATCH-RECORDED',
        'post_readout_action': relative_to_root(out_dir / 'post-readout-action.json'),
        'summary': relative_to_root(out_dir / 'POST-READOUT-ACTION-SUMMARY.md'),
        'dispatch_lane': lane,
        'source_live_window_readout': relative_to_root(readout_path),
        'claim_ceiling': CLAIM_CEILING,
    }


def main() -> None:
    args = parse_args()
    try:
        result = build_post_readout_action(
            readout=args.readout,
            dispatch_lane=args.dispatch_lane,
            source_truth_class=args.source_truth_class,
            allowed_action_count=args.allowed_action_count,
            prohibited_action_count=args.prohibited_action_count,
            field_to_reask_count=args.field_to_reask_count,
            field_to_drop_count=args.field_to_drop_count,
            reviewer_role_count=args.reviewer_role_count,
            unresolved_disagreement_count=args.unresolved_disagreement_count,
            due_or_recheck_date=args.due_or_recheck_date,
            owner_action_class=args.owner_action_class,
            next_evidence_ask_class=args.next_evidence_ask_class,
            public_language_action=args.public_language_action,
            no_expansion_confirmed=args.no_expansion_confirmed,
            no_public_claim_upgrade=args.no_public_claim_upgrade,
            no_service_record_edit=args.no_service_record_edit,
            no_lifecycle_change=args.no_lifecycle_change,
            no_closure_from_dispatch=args.no_closure_from_dispatch,
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
        raise SystemExit(2)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
