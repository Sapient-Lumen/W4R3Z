#!/usr/bin/env python3
"""Record a bounded local FT-0181 first-packet decision-board artifact.

This is the first executable step after a proceed-capable workbench review. It
captures only five decision-slice classes, counts, hashes, and the source review
reference. It deliberately copies no owner answers, raw CSV rows, contact
details, learner data, protected facts, or security payloads. The output is
local/scratch only: it is not evidence, not custody, not acceptance, not closure,
and not public-summary support.
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
    owner_first_packet_decision_integrity_error,
    owner_workbench_review_integrity_error,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = ROOT / 'scratch' / 'field' / 'ft0181' / 'owner-first-packet-decisions'
OPERATOR_CONFIRMATION = 'human-recorded-five-slice-decision-board'
CLAIM_CEILING = (
    'First-packet decision-board record only; not evidence, not SRC2+ acceptance, '
    'not custody evidence, not closure evidence, not public-summary support, and '
    'not proof of learning, safety, access, workload, compliance, scale, or effectiveness.'
)

AUTHORITY_ACTIONS = {'keep-lower-ceiling', 'revise-ceiling', 'block', 'no-change'}
EVIDENCE_ACTIONS = {'suppress', 'downgrade', 'keep-example-only', 'stage-claim-with-expiry', 'no-change'}
CONSTRUCT_ACTIONS = {'add-stop-trigger', 'keep-teacher-review', 'require-unaided-segment', 'fall-back-service', 'no-change'}
PUBLIC_ACTIONS = {'publish-limited', 'revise-claims', 'suppress', 'draft-only', 'no-change'}
LIFECYCLE_ACTIONS = {'sandbox', 'pilot', 'watch', 'deprecate', 'archive-only', 'quarantine', 'no-change'}
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
    parser = argparse.ArgumentParser(description='Record a local bounded FT-0181 first-packet decision-board artifact.')
    parser.add_argument('--review', required=True, type=Path, help='scratch/.../workbench-review.json with PROCEED-DECISION-BOARD decision.')
    parser.add_argument('--authority-action', required=True, choices=sorted(AUTHORITY_ACTIONS))
    parser.add_argument('--evidence-action', required=True, choices=sorted(EVIDENCE_ACTIONS))
    parser.add_argument('--construct-action', required=True, choices=sorted(CONSTRUCT_ACTIONS))
    parser.add_argument('--public-action', required=True, choices=sorted(PUBLIC_ACTIONS))
    parser.add_argument('--lifecycle-action', required=True, choices=sorted(LIFECYCLE_ACTIONS))
    parser.add_argument('--changed-slice-count', type=int, required=True, help='Number of non-no-change decision slices; 1-5 for proceed reviews.')
    parser.add_argument('--rollback-owner-role-count', type=int, default=1, help='Count of rollback owner roles named locally; 1-5.')
    parser.add_argument('--operator-confirmation', required=True, help='Exact local confirmation token emitted by the router; not evidence.')
    parser.add_argument('--raw-learner-data-present', action='store_true')
    parser.add_argument('--protected-facts-present', action='store_true')
    parser.add_argument('--security-payloads-present', action='store_true')
    parser.add_argument('--public-claim-upgrade-requested', action='store_true')
    parser.add_argument('--output-dir', type=Path, help='Local/scratch output directory for the decision record.')
    parser.add_argument('--overwrite', action='store_true', help='Replace an existing decision directory.')
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


def default_output_dir(review_path: Path) -> Path:
    digest = sha256_file(review_path)[:12]
    return DEFAULT_OUTPUT_ROOT / f'aiedu-sr-003-{digest}'


def forbidden_argument_term(*values: str) -> str | None:
    text = ' '.join(value for value in values if value).lower()
    for term in sorted(FORBIDDEN_TERMS):
        if term in text:
            return term
    return None


def count_error(value: int, field: str, upper: int) -> str | None:
    if value < 0:
        return f'{field} cannot be negative'
    if value > upper:
        return f'{field} cannot exceed {upper}'
    return None


def non_no_change_count(slices: dict[str, str]) -> int:
    return sum(1 for value in slices.values() if value != 'no-change')


def build_summary(record: dict[str, Any]) -> str:
    slices = record['decision_slices']
    flags = record['risk_flags']
    return f"""# FT-0181 first-packet decision-board record

| Field | Value |
|---|---|
| Board state | `{record['board_state']}` |
| Acceptance state | `{record['acceptance_state']}` |
| Evidence state | `{record['evidence_state']}` |
| Input review | `{record['source_workbench_review']['reference']}` |
| Source truth class | `{record['source_workbench_review']['source_truth_class']}` |
| Authority action | `{slices['authority_action']}` |
| Evidence action | `{slices['evidence_action']}` |
| Construct action | `{slices['construct_action']}` |
| Public action | `{slices['public_action']}` |
| Lifecycle action | `{slices['lifecycle_action']}` |
| Changed slice count | `{record['changed_slice_count']}` |
| Rollback owner role count | `{record['rollback_owner_role_count']}` |
| Raw learner data present | `{flags['raw_learner_data_present']}` |
| Protected facts present | `{flags['protected_facts_present']}` |
| Security payloads present | `{flags['security_payloads_present']}` |
| Public claim upgrade requested | `{flags['public_claim_upgrade_requested']}` |
| Required next surface | `{record['required_next_surface']}` |

## Boundary

This local decision-board record preserves only five bounded slice classes,
counts, hashes, and the source review reference. It is not evidence, not `SRC2+`
acceptance, not custody evidence, not closure evidence, and not public-summary
support. Do not paste owner answer text, raw CSV rows, contact details, learner
identifiers, protected facts, small cells, security payloads, screenshots, or
claim language into this record.
"""


def build_decision(
    *,
    review: Path,
    authority_action: str,
    evidence_action: str,
    construct_action: str,
    public_action: str,
    lifecycle_action: str,
    changed_slice_count: int,
    rollback_owner_role_count: int,
    raw_learner_data_present: bool,
    protected_facts_present: bool,
    security_payloads_present: bool,
    public_claim_upgrade_requested: bool,
    operator_confirmation: str,
    output_dir: Path | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    review_path = review if review.is_absolute() else ROOT / review
    review_path = review_path.resolve()
    inside, parts = archive_relative(review_path, archive_root=ROOT)
    lane_error = field_scratch_lane_error(review_path, archive_root=ROOT, field_name='review')
    if lane_error or review_path.name != 'workbench-review.json':
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'FIRST-PACKET-DECISION-REVIEW-BLOCKED',
            'message': 'First-packet decision requires a scratch-local workbench-review.json source.',
            'review': relative_to_root(review_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if not review_path.exists() or not review_path.is_file():
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'FIRST-PACKET-DECISION-REVIEW-MISSING',
            'message': 'Referenced workbench review does not exist.',
            'review': relative_to_root(review_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    try:
        review_data = load_json(review_path)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'FIRST-PACKET-DECISION-REVIEW-BLOCKED',
            'message': 'Referenced workbench review is not readable JSON.',
            'error': str(exc),
            'review': relative_to_root(review_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    review_error = owner_workbench_review_integrity_error(review_data, archive_root=ROOT)
    if review_error:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'FIRST-PACKET-DECISION-REVIEW-BLOCKED',
            'message': 'Referenced workbench review failed integrity checks: ' + review_error,
            'review': relative_to_root(review_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if review_data.get('decision') != 'PROCEED-DECISION-BOARD':
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'FIRST-PACKET-DECISION-REVIEW-BLOCKED',
            'message': 'First-packet decision board requires a PROCEED-DECISION-BOARD workbench review.',
            'decision': review_data.get('decision'),
            'review': relative_to_root(review_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    slices = {
        'authority_action': authority_action,
        'evidence_action': evidence_action,
        'construct_action': construct_action,
        'public_action': public_action,
        'lifecycle_action': lifecycle_action,
    }
    forbidden = forbidden_argument_term(operator_confirmation, *slices.values())
    if forbidden:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'FIRST-PACKET-DECISION-CONTENT-BLOCKED',
            'message': f'First-packet decision arguments include forbidden raw/protected/contact/security term: {forbidden}',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if operator_confirmation != OPERATOR_CONFIRMATION:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'FIRST-PACKET-DECISION-CONFIRMATION-BLOCKED',
            'message': f'operator_confirmation must be exactly {OPERATOR_CONFIRMATION}',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    for value, field, upper in [
        (changed_slice_count, 'changed_slice_count', 5),
        (rollback_owner_role_count, 'rollback_owner_role_count', 5),
    ]:
        err = count_error(value, field, upper)
        if err:
            raise ValueError(json.dumps({'ok': False, 'outcome': 'FIRST-PACKET-DECISION-COUNT-BLOCKED', 'message': err, 'claim_ceiling': CLAIM_CEILING}, indent=2))
    if rollback_owner_role_count < 1:
        raise ValueError(json.dumps({'ok': False, 'outcome': 'FIRST-PACKET-DECISION-COUNT-BLOCKED', 'message': 'rollback_owner_role_count must be at least 1', 'claim_ceiling': CLAIM_CEILING}, indent=2))
    actual_changed = non_no_change_count(slices)
    if changed_slice_count != actual_changed:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'FIRST-PACKET-DECISION-COUNT-BLOCKED',
            'message': f'changed_slice_count={changed_slice_count} must equal the number of non-no-change slice actions ({actual_changed})',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if changed_slice_count < 1:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'FIRST-PACKET-DECISION-NO-CHANGE-BLOCKED',
            'message': 'A proceed-capable workbench review requires at least one bounded decision slice before a change ticket can be opened.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if any([raw_learner_data_present, protected_facts_present, security_payloads_present, public_claim_upgrade_requested]):
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'FIRST-PACKET-DECISION-RISK-FLAG-BLOCKED',
            'message': 'First-packet decision cannot proceed while raw/protected/security/public-claim-upgrade flags are present; route back to block, trim, or re-ask review.',
            'risk_flags': {
                'raw_learner_data_present': raw_learner_data_present,
                'protected_facts_present': protected_facts_present,
                'security_payloads_present': security_payloads_present,
                'public_claim_upgrade_requested': public_claim_upgrade_requested,
            },
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    out_dir = output_dir or default_output_dir(review_path)
    out_dir = out_dir if out_dir.is_absolute() else ROOT / out_dir
    allowed, boundary = output_allowed(out_dir, archive_root=ROOT)
    if not allowed:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'FIRST-PACKET-DECISION-OUTPUT-BLOCKED',
            'message': f'Output directory is not allowed for local decision artifacts: {boundary}',
            'output_dir': relative_to_root(out_dir),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if out_dir.exists():
        if not overwrite:
            raise ValueError(json.dumps({
                'ok': False,
                'outcome': 'FIRST-PACKET-DECISION-OUTPUT-EXISTS',
                'message': 'Output directory already exists; pass --overwrite to regenerate local scratch output.',
                'output_dir': relative_to_root(out_dir),
                'claim_ceiling': CLAIM_CEILING,
            }, indent=2))
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    source_review = {
        'reference': relative_to_root(review_path),
        'review_sha256': sha256_file(review_path),
        'decision': review_data.get('decision'),
        'review_state': review_data.get('review_state'),
        'acceptance_state': review_data.get('acceptance_state'),
        'source_truth_class': review_data.get('source_truth_class'),
        'decision_changed_count': review_data.get('field_counts', {}).get('decision_changed_count'),
        'surviving_field_count': review_data.get('field_counts', {}).get('surviving_field_count'),
        'reviewer_role_count': review_data.get('reviewer_role_count'),
        'revalidated_for_decision_board': True,
    }
    record = {
        'decision_type': 'FT-0181-first-packet-decision-board',
        'decision_version': 'rev0276',
        'created_at_utc': now,
        'followthrough_id': 'FT-0181',
        'service_record_id': 'AIEDU-SR-003',
        'board_state': 'DECISION_RECORDED_NOT_ACCEPTED',
        'acceptance_state': 'NOT_ACCEPTED',
        'evidence_state': 'not_evidence',
        'closure_effect': 'does_not_close_ft0181',
        'public_claim_effect': 'none',
        'ft0181_status': 'live',
        'operator_confirmation': operator_confirmation,
        'source_workbench_review': source_review,
        'decision_slices': slices,
        'changed_slice_count': changed_slice_count,
        'rollback_owner_role_count': rollback_owner_role_count,
        'risk_flags': {
            'raw_learner_data_present': raw_learner_data_present,
            'protected_facts_present': protected_facts_present,
            'security_payloads_present': security_payloads_present,
            'public_claim_upgrade_requested': public_claim_upgrade_requested,
        },
        'content_minimization': {
            'copies_owner_answers': False,
            'copies_raw_csv_rows': False,
            'copies_workbench_review_text': False,
            'copies_contact_details': False,
            'contains_slice_classes_counts_hashes_and_routes_only': True,
            'source_workbench_review_revalidated': True,
        },
        'claim_ceiling': CLAIM_CEILING,
        'required_next_surface': 'docs/30-operations/ft0181-post-decision-change-ticket.md',
        'change_ticket_effect': 'may_source_post_decision_change_ticket_only',
    }
    record_error = owner_first_packet_decision_integrity_error(record, archive_root=ROOT)
    if record_error:
        shutil.rmtree(out_dir)
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'FIRST-PACKET-DECISION-INTEGRITY-BLOCKED',
            'message': 'Generated first-packet decision failed integrity checks: ' + record_error,
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    decision_path = out_dir / 'first-packet-decision.json'
    summary_path = out_dir / 'FIRST-PACKET-DECISION-SUMMARY.md'
    decision_path.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    summary_path.write_text(build_summary(record), encoding='utf-8')
    return {
        'ok': True,
        'outcome': 'FIRST-PACKET-DECISION-RECORDED',
        'decision': 'DECISION_RECORDED_NOT_ACCEPTED',
        'output_dir': relative_to_root(out_dir),
        'decision_path': relative_to_root(decision_path),
        'summary_path': relative_to_root(summary_path),
        'required_next_surface': record['required_next_surface'],
        'claim_ceiling': CLAIM_CEILING,
    }


def main() -> int:
    args = parse_args()
    try:
        result = build_decision(
            review=args.review,
            authority_action=args.authority_action,
            evidence_action=args.evidence_action,
            construct_action=args.construct_action,
            public_action=args.public_action,
            lifecycle_action=args.lifecycle_action,
            changed_slice_count=args.changed_slice_count,
            rollback_owner_role_count=args.rollback_owner_role_count,
            raw_learner_data_present=args.raw_learner_data_present,
            protected_facts_present=args.protected_facts_present,
            security_payloads_present=args.security_payloads_present,
            public_claim_upgrade_requested=args.public_claim_upgrade_requested,
            operator_confirmation=args.operator_confirmation,
            output_dir=args.output_dir,
            overwrite=args.overwrite,
        )
    except ValueError as exc:
        text = str(exc)
        print(text)
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"record_ft0181_first_packet_decision: {result['outcome']} -> {result['decision_path']}")
        print(f"required_next_surface: {result['required_next_surface']}")
        print(f"claim_ceiling: {CLAIM_CEILING}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
