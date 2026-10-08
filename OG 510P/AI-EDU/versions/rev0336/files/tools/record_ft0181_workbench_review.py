#!/usr/bin/env python3
"""Record a bounded local FT-0181 workbench-review decision.

This utility is the first step after a NOT_ACCEPTED workbench seed. It records
only counts, route classes, and a revalidated seed reference. It deliberately
copies no owner answers, raw CSV rows, contact details, learner data, protected
facts, or security payloads. The output is local/scratch only, not evidence,
not acceptance, not custody, not closure, and not public-summary support.
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
    owner_workbench_review_integrity_error,
    owner_workbench_seed_integrity_error,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = ROOT / 'scratch' / 'field' / 'ft0181' / 'owner-workbench-reviews'
OPERATOR_CONFIRMATION = 'human-reviewed-minimized-workbench-record'
CLAIM_CEILING = (
    'Workbench review record only; not SRC2+ acceptance, not custody evidence, '
    'not closure evidence, not public-summary support, and not proof of learning, '
    'safety, access, workload, compliance, scale, or effectiveness.'
)
DECISION_CHOICES = {
    'proceed-decision-board': 'PROCEED-DECISION-BOARD',
    'reask-owner': 'REASK-OWNER',
    'block-overbroad': 'BLOCK-OVERBROAD',
    'block-protected': 'BLOCK-PROTECTED',
    'block-security': 'BLOCK-SECURITY',
    'block-evidence': 'BLOCK-EVIDENCE',
    'no-change-trim': 'NO-CHANGE-TRIM',
}
REVIEW_BASIS_CHOICES = {
    'owner-attested-aggregate',
    'needs-clarification',
    'raw-or-protected-risk',
    'weak-evidence-only',
    'decision-neutral',
    'security-abstraction-needed',
    'overbroad-export-risk',
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
    parser = argparse.ArgumentParser(description='Record a local bounded FT-0181 owner-packet workbench review.')
    parser.add_argument('--seed', required=True, type=Path, help='scratch/.../workbench-seed.json produced by owner-reply-workbench-seed.')
    parser.add_argument('--decision', required=True, choices=sorted(DECISION_CHOICES), help='Bounded workbench-review decision route.')
    parser.add_argument('--source-truth-class', required=True, help='Reviewer source truth class claim, e.g. SRC2 or UNVERIFIED-OWNER-REPLY.')
    parser.add_argument('--review-basis', required=True, choices=sorted(REVIEW_BASIS_CHOICES), help='Short class label for why this route was selected; no raw details.')
    parser.add_argument('--surviving-field-count', type=int, required=True, help='Count of fields that survive to the next board; 0-8.')
    parser.add_argument('--decision-changed-count', type=int, required=True, help='Count of fields that changed a decision; 0-8.')
    parser.add_argument('--local-only-field-count', type=int, default=0, help='Count of fields kept local; 0-8.')
    parser.add_argument('--trimmed-field-count', type=int, default=0, help='Count of fields trimmed; 0-8.')
    parser.add_argument('--reask-field-count', type=int, default=0, help='Count of fields needing a bounded re-ask; 0-8.')
    parser.add_argument('--reviewer-role-count', type=int, default=1, help='Number of distinct reviewer roles represented; proceed requires at least 2.')
    parser.add_argument('--operator-confirmation', required=True, help='Exact local confirmation token emitted in docs/router; not evidence.')
    parser.add_argument('--raw-learner-data-present', action='store_true', help='Set only if raw learner data appeared and was blocked/kept local.')
    parser.add_argument('--protected-facts-present', action='store_true', help='Set only if protected facts appeared and were blocked/kept local.')
    parser.add_argument('--security-payloads-present', action='store_true', help='Set only if security payloads appeared and were blocked/kept local.')
    parser.add_argument('--public-claim-upgrade-requested', action='store_true', help='Set only if someone asked for a stronger public claim than the evidence supports.')
    parser.add_argument('--output-dir', type=Path, help='Local/scratch output directory for the review record.')
    parser.add_argument('--overwrite', action='store_true', help='Replace an existing review directory.')
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


def default_output_dir(seed_path: Path) -> Path:
    digest = sha256_file(seed_path)[:12]
    return DEFAULT_OUTPUT_ROOT / f'aiedu-sr-003-{digest}'


def forbidden_argument_term(*values: str) -> str | None:
    text = ' '.join(value for value in values if value).lower()
    for term in sorted(FORBIDDEN_TERMS):
        if term in text:
            return term
    return None


def count_error(value: int, field: str) -> str | None:
    if value < 0:
        return f'{field} cannot be negative'
    if value > 8:
        return f'{field} cannot exceed the eight-row owner reply bound'
    return None


def build_summary(record: dict[str, Any]) -> str:
    counts = record['field_counts']
    flags = record['risk_flags']
    return f"""# FT-0181 workbench review record

| Field | Value |
|---|---|
| Decision | `{record['decision']}` |
| Review state | `{record['review_state']}` |
| Acceptance state | `{record['acceptance_state']}` |
| Evidence state | `{record['evidence_state']}` |
| Source truth class | `{record['source_truth_class']}` |
| Review basis | `{record['review_basis']}` |
| Input seed | `{record['input_seed']['reference']}` |
| Surviving fields | `{counts['surviving_field_count']}` |
| Decision-changing fields | `{counts['decision_changed_count']}` |
| Local-only fields | `{counts['local_only_field_count']}` |
| Trimmed fields | `{counts['trimmed_field_count']}` |
| Re-ask fields | `{counts['reask_field_count']}` |
| Reviewer role count | `{record['reviewer_role_count']}` |
| Raw learner data present | `{flags['raw_learner_data_present']}` |
| Protected facts present | `{flags['protected_facts_present']}` |
| Security payloads present | `{flags['security_payloads_present']}` |
| Public claim upgrade requested | `{flags['public_claim_upgrade_requested']}` |
| Required next surface | `{record['required_next_surface']}` |

## Boundary

This local review record preserves only counts, route classes, hashes, and the
next surface. It is not `SRC2+` acceptance, custody evidence, closure evidence,
or public-summary support. Do not paste owner answer text, raw CSV rows, contact
details, learner identifiers, protected facts, small cells, security payloads,
or screenshots into this record.
"""


def build_review(
    *,
    seed: Path,
    decision: str,
    source_truth_class: str,
    review_basis: str,
    surviving_field_count: int,
    decision_changed_count: int,
    local_only_field_count: int,
    trimmed_field_count: int,
    reask_field_count: int,
    reviewer_role_count: int,
    raw_learner_data_present: bool,
    protected_facts_present: bool,
    security_payloads_present: bool,
    public_claim_upgrade_requested: bool,
    operator_confirmation: str,
    output_dir: Path | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    seed_path = seed if seed.is_absolute() else ROOT / seed
    seed_path = seed_path.resolve()
    inside, parts = archive_relative(seed_path, archive_root=ROOT)
    lane_error = field_scratch_lane_error(seed_path, archive_root=ROOT, field_name='seed')
    if lane_error or seed_path.name != 'workbench-seed.json':
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'WORKBENCH-REVIEW-SEED-BLOCKED',
            'message': 'Workbench review requires a scratch-local workbench-seed.json source.',
            'seed': relative_to_root(seed_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if not seed_path.exists() or not seed_path.is_file():
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'WORKBENCH-REVIEW-SEED-MISSING',
            'message': 'Referenced workbench seed does not exist.',
            'seed': relative_to_root(seed_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    try:
        seed_data = load_json(seed_path)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'WORKBENCH-REVIEW-SEED-BLOCKED',
            'message': 'Referenced workbench seed is not readable JSON.',
            'error': str(exc),
            'seed': relative_to_root(seed_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    seed_error = owner_workbench_seed_integrity_error(seed_data, archive_root=ROOT)
    if seed_error:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'WORKBENCH-REVIEW-SEED-BLOCKED',
            'message': 'Referenced workbench seed failed integrity checks: ' + seed_error,
            'seed': relative_to_root(seed_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    forbidden = forbidden_argument_term(source_truth_class, review_basis, operator_confirmation)
    if forbidden:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'WORKBENCH-REVIEW-ARGUMENT-BLOCKED',
            'message': f'Workbench review arguments include forbidden raw/protected/contact term: {forbidden}',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if operator_confirmation.strip() != OPERATOR_CONFIRMATION:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'WORKBENCH-REVIEW-CONFIRMATION-BLOCKED',
            'message': f'operator-confirmation must be {OPERATOR_CONFIRMATION!r}',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    for field, value in {
        'surviving-field-count': surviving_field_count,
        'decision-changed-count': decision_changed_count,
        'local-only-field-count': local_only_field_count,
        'trimmed-field-count': trimmed_field_count,
        'reask-field-count': reask_field_count,
    }.items():
        err = count_error(value, field)
        if err:
            raise ValueError(json.dumps({
                'ok': False,
                'outcome': 'WORKBENCH-REVIEW-COUNT-BLOCKED',
                'message': err,
                'claim_ceiling': CLAIM_CEILING,
            }, indent=2))

    out = output_dir if output_dir is not None else default_output_dir(seed_path)
    out = out if out.is_absolute() else ROOT / out
    allowed, output_boundary = output_allowed(out, archive_root=ROOT)
    if not allowed:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'WORKBENCH-REVIEW-OUTPUT-BLOCKED',
            'output_dir': relative_to_root(out),
            'output_boundary': output_boundary,
            'message': 'Workbench reviews are local/scratch artifacts and cannot be written into release-controlled surfaces.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    normalized_decision = DECISION_CHOICES[decision]
    required_next_surface = (
        'docs/30-operations/ft0181-first-packet-decision-board.md'
        if normalized_decision == 'PROCEED-DECISION-BOARD'
        else 'docs/30-operations/ft0181-owner-packet-workbench.md'
    )
    decision_board_effect = (
        'may_source_first_packet_decision_board_only'
        if normalized_decision == 'PROCEED-DECISION-BOARD'
        else 'none'
    )
    created = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    seed_hash = sha256_file(seed_path)
    record = {
        'review_type': 'FT-0181-owner-packet-workbench-review',
        'review_version': 'rev0275',
        'created_at_utc': created,
        'followthrough_id': 'FT-0181',
        'service_record_id': 'AIEDU-SR-003',
        'input_seed': {
            'reference': relative_to_root(seed_path),
            'seed_sha256': seed_hash,
            'seed_version': seed_data.get('seed_version'),
            'acceptance_state': seed_data.get('acceptance_state'),
            'source_truth_status': seed_data.get('source_truth_status'),
        },
        'review_state': 'REVIEWED_NOT_ACCEPTED',
        'decision': normalized_decision,
        'source_truth_class': source_truth_class,
        'review_basis': review_basis,
        'decision_board_effect': decision_board_effect,
        'required_next_surface': required_next_surface,
        'field_counts': {
            'surviving_field_count': surviving_field_count,
            'decision_changed_count': decision_changed_count,
            'local_only_field_count': local_only_field_count,
            'trimmed_field_count': trimmed_field_count,
            'reask_field_count': reask_field_count,
        },
        'risk_flags': {
            'raw_learner_data_present': raw_learner_data_present,
            'protected_facts_present': protected_facts_present,
            'security_payloads_present': security_payloads_present,
            'public_claim_upgrade_requested': public_claim_upgrade_requested,
        },
        'reviewer_role_count': reviewer_role_count,
        'operator_confirmation': operator_confirmation,
        'acceptance_state': 'NOT_ACCEPTED',
        'source_truth_status': 'UNVERIFIED_OWNER_REPLY_REVIEWED_NOT_ACCEPTED',
        'evidence_state': 'not_evidence',
        'closure_effect': 'does_not_close_ft0181',
        'public_claim_effect': 'none',
        'claim_ceiling': CLAIM_CEILING,
        'ft0181_status': 'live',
        'content_minimization': {
            'copies_owner_answers': False,
            'copies_raw_csv_rows': False,
            'copies_proceed_staged_row_text': False,
            'copies_contact_details': False,
            'source_seed_revalidated': True,
            'contains_counts_hashes_and_routes_only': True,
        },
    }
    record_error = owner_workbench_review_integrity_error(record, archive_root=ROOT)
    if record_error:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'WORKBENCH-REVIEW-BLOCKED',
            'message': record_error,
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
    review_path = out / 'workbench-review.json'
    review_path.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    summary_path = out / 'WORKBENCH-REVIEW-SUMMARY.md'
    summary_path.write_text(build_summary(record), encoding='utf-8')
    return {
        'ok': True,
        'outcome': 'WORKBENCH-REVIEW-RECORDED',
        'output_dir': relative_to_root(out),
        'review_path': relative_to_root(review_path),
        'summary_path': relative_to_root(summary_path),
        'decision': normalized_decision,
        'required_next_surface': required_next_surface,
        'acceptance_state': 'NOT_ACCEPTED',
        'evidence_state': 'not_evidence',
        'closure_effect': 'does_not_close_ft0181',
        'public_claim_effect': 'none',
        'claim_ceiling': CLAIM_CEILING,
    }


def main() -> int:
    args = parse_args()
    try:
        result = build_review(
            seed=args.seed,
            decision=args.decision,
            source_truth_class=args.source_truth_class,
            review_basis=args.review_basis,
            surviving_field_count=args.surviving_field_count,
            decision_changed_count=args.decision_changed_count,
            local_only_field_count=args.local_only_field_count,
            trimmed_field_count=args.trimmed_field_count,
            reask_field_count=args.reask_field_count,
            reviewer_role_count=args.reviewer_role_count,
            raw_learner_data_present=args.raw_learner_data_present,
            protected_facts_present=args.protected_facts_present,
            security_payloads_present=args.security_payloads_present,
            public_claim_upgrade_requested=args.public_claim_upgrade_requested,
            operator_confirmation=args.operator_confirmation,
            output_dir=args.output_dir,
            overwrite=args.overwrite,
        )
    except Exception as exc:
        if args.json:
            try:
                payload = json.loads(str(exc))
            except json.JSONDecodeError:
                payload = {'ok': False, 'outcome': 'WORKBENCH-REVIEW-ERROR', 'message': str(exc), 'claim_ceiling': CLAIM_CEILING}
            print(json.dumps(payload, indent=2))
            return 1
        raise
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
