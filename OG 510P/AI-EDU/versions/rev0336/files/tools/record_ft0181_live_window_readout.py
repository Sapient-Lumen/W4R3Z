#!/usr/bin/env python3
"""Record a bounded local FT-0181 terminal live-window readout.

This utility is the executable firebreak after a terminal live-window card. It
records only aggregate count classes, a bounded disposition, source-card hashes,
and route boundaries. It copies no owner answers, learner data, protected facts,
security payloads, contact details, live notes, screenshots, or public-claim
language. The output is scratch/local only: not evidence, not custody, not
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
    LIVE_WINDOW_READOUT_SOURCE_TRUTH_CLASSES,
    LIVE_WINDOW_READOUT_TERMINAL_STATES,
    LIVE_WINDOW_STATE_TO_DISPOSITIONS,
    archive_relative,
    field_scratch_lane_error,
    output_allowed,
    owner_live_window_card_integrity_error,
    owner_live_window_readout_integrity_error,
)

ROOT = Path(__file__).resolve().parents[1]
REVISION = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8')).get('revision', 'unknown')
DEFAULT_OUTPUT_ROOT = ROOT / 'scratch' / 'field' / 'ft0181' / 'owner-live-window-readouts'
OPERATOR_CONFIRMATION = 'human-recorded-aggregate-readout-no-closure'
CLAIM_CEILING = (
    'Terminal live-window readout only; not evidence, not SRC2+ acceptance, not custody evidence, '
    'not closure evidence, does not close FT-0181, not public-summary support, and not proof of '
    'learning, safety, access, workload, compliance, scale, or effectiveness.'
)

WINDOW_DISPOSITION_CHOICES = {
    'stopped': 'stopped',
    'rolled-back': 'rolled_back',
    'continue-bounded': 'continue_bounded',
    'rerun-narrower': 'rerun_narrower',
    'quarantine': 'quarantine',
    'no-change': 'no_change',
}
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
    'small-cell',
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Record a local bounded FT-0181 terminal live-window readout.')
    parser.add_argument('--card', required=True, type=Path, help='scratch/.../live-window-card.json in a terminal state.')
    parser.add_argument('--window-disposition', required=True, choices=sorted(WINDOW_DISPOSITION_CHOICES))
    parser.add_argument('--source-truth-class', required=True, choices=sorted(LIVE_WINDOW_READOUT_SOURCE_TRUTH_CLASSES))
    parser.add_argument('--aggregate-evidence-read-count', type=int, required=True, help='1-7 aggregate readout classes.')
    parser.add_argument('--claim-family-effect-count', type=int, required=True, help='1-8 claim family rows touched by the readout.')
    parser.add_argument('--decision-delta-count', type=int, required=True, help='0-8 bounded deltas; continue/rerun need at least 1.')
    parser.add_argument('--field-trim-count', type=int, required=True, help='0-8 fields to trim; rerun/no-change need at least 1.')
    parser.add_argument('--reviewer-role-count', type=int, required=True, help='2-5 reviewer/owner roles represented.')
    parser.add_argument('--unresolved-disagreement-count', type=int, default=0, help='0-5 unresolved disagreements/calibration items.')
    parser.add_argument('--public-claim-ceiling', default='example-only-no-outcome-claim', choices=sorted(PUBLIC_CEILING_CHOICES))
    parser.add_argument('--operator-confirmation', required=True, help='Exact local confirmation token emitted by the router.')
    parser.add_argument('--no-public-claim-upgrade', action='store_true')
    parser.add_argument('--no-service-record-edit', action='store_true')
    parser.add_argument('--no-lifecycle-change', action='store_true')
    parser.add_argument('--no-closure-from-readout', action='store_true')
    parser.add_argument('--raw-learner-data-present', action='store_true')
    parser.add_argument('--protected-facts-present', action='store_true')
    parser.add_argument('--security-payloads-present', action='store_true')
    parser.add_argument('--public-claim-upgrade-requested', action='store_true')
    parser.add_argument('--output-dir', type=Path, help='Local/scratch output directory for the readout.')
    parser.add_argument('--overwrite', action='store_true', help='Replace an existing readout directory.')
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


def default_output_dir(card_path: Path) -> Path:
    digest = sha256_file(card_path)[:12]
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


def source_card_snapshot(card_path: Path, card_data: dict[str, Any]) -> dict[str, Any]:
    return {
        'reference': relative_to_root(card_path),
        'card_sha256': sha256_file(card_path),
        'window_state': card_data.get('window_state'),
        'source_truth_class': card_data.get('source_truth_class'),
        'public_claim_ceiling': card_data.get('public_claim_ceiling'),
        'window_controls': card_data.get('window_controls'),
        'acceptance_state': card_data.get('acceptance_state'),
        'evidence_state': card_data.get('evidence_state'),
        'readout_effect': card_data.get('readout_effect'),
        'live_window_card_effect': card_data.get('live_window_card_effect'),
        'revalidated_for_live_window_readout': True,
    }


def build_summary(record: dict[str, Any]) -> str:
    counts = record['readout_counts']
    flags = record['risk_flags']
    return f"""# FT-0181 terminal live-window readout

| Field | Value |
|---|---|
| Readout state | `{record['readout_state']}` |
| Window disposition | `{record['window_disposition']}` |
| Acceptance state | `{record['acceptance_state']}` |
| Evidence state | `{record['evidence_state']}` |
| Source card | `{record['source_live_window_card']['reference']}` |
| Source card state | `{record['source_live_window_card']['window_state']}` |
| Source truth class | `{record['source_truth_class']}` |
| Public claim ceiling | `{record['public_claim_ceiling']}` |
| Aggregate evidence read count | `{counts['aggregate_evidence_read_count']}` |
| Claim family effect count | `{counts['claim_family_effect_count']}` |
| Decision delta count | `{counts['decision_delta_count']}` |
| Field trim count | `{counts['field_trim_count']}` |
| Reviewer role count | `{counts['reviewer_role_count']}` |
| Unresolved disagreement count | `{counts['unresolved_disagreement_count']}` |
| No public claim upgrade | `{record['no_public_claim_upgrade']}` |
| No service record edit | `{record['no_service_record_edit']}` |
| No lifecycle change | `{record['no_lifecycle_change']}` |
| No closure from readout | `{record['no_closure_from_readout']}` |
| Raw learner data present | `{flags['raw_learner_data_present']}` |
| Protected facts present | `{flags['protected_facts_present']}` |
| Security payloads present | `{flags['security_payloads_present']}` |
| Public claim upgrade requested | `{flags['public_claim_upgrade_requested']}` |
| Required next surface | `{record['required_next_surface']}` |

## Boundary

This local readout preserves only source-card hashes, aggregate count classes,
a bounded disposition, and route controls. It is not evidence, not `SRC2+`
acceptance, not custody evidence, not closure evidence, and not public-summary
support. Do not paste owner answer text, raw CSV rows, contact details, learner
identifiers, protected facts, small cells, security payloads, screenshots, live
notes, or claim language into this record.
"""


def build_live_window_readout(
    *,
    card: Path,
    window_disposition: str,
    source_truth_class: str,
    aggregate_evidence_read_count: int,
    claim_family_effect_count: int,
    decision_delta_count: int,
    field_trim_count: int,
    reviewer_role_count: int,
    unresolved_disagreement_count: int,
    public_claim_ceiling: str,
    no_public_claim_upgrade: bool,
    no_service_record_edit: bool,
    no_lifecycle_change: bool,
    no_closure_from_readout: bool,
    raw_learner_data_present: bool,
    protected_facts_present: bool,
    security_payloads_present: bool,
    public_claim_upgrade_requested: bool,
    operator_confirmation: str,
    output_dir: Path | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    card_path = card if card.is_absolute() else ROOT / card
    card_path = card_path.resolve()
    inside, parts = archive_relative(card_path, archive_root=ROOT)
    lane_error = field_scratch_lane_error(card_path, archive_root=ROOT, field_name='card')
    if lane_error or card_path.name != 'live-window-card.json':
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'LIVE-WINDOW-READOUT-CARD-BLOCKED',
            'message': 'Live-window readout requires a scratch-local terminal live-window-card.json source.',
            'card': relative_to_root(card_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if not card_path.exists() or not card_path.is_file():
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'LIVE-WINDOW-READOUT-CARD-MISSING',
            'message': 'Referenced live-window card does not exist.',
            'card': relative_to_root(card_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    try:
        card_data = load_json(card_path)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'LIVE-WINDOW-READOUT-CARD-BLOCKED',
            'message': 'Referenced live-window card is not readable JSON.',
            'error': str(exc),
            'card': relative_to_root(card_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    card_error = owner_live_window_card_integrity_error(card_data, archive_root=ROOT)
    if card_error:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'LIVE-WINDOW-READOUT-CARD-BLOCKED',
            'message': 'Referenced live-window card failed integrity checks: ' + card_error,
            'card': relative_to_root(card_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    normalized_disposition = WINDOW_DISPOSITION_CHOICES[window_disposition]
    source_state = card_data.get('window_state')
    if source_state not in LIVE_WINDOW_READOUT_TERMINAL_STATES:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'LIVE-WINDOW-READOUT-NONTERMINAL-CARD-BLOCKED',
            'message': 'Live-window readout requires paused, rolled_back, completed_no_closure, or quarantined source card state.',
            'source_window_state': source_state,
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    allowed_dispositions = LIVE_WINDOW_STATE_TO_DISPOSITIONS.get(str(source_state), set())
    if normalized_disposition not in allowed_dispositions:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'LIVE-WINDOW-READOUT-DISPOSITION-BLOCKED',
            'message': f'Disposition {normalized_disposition!r} is not allowed for source card state {source_state!r}.',
            'allowed_dispositions': sorted(allowed_dispositions),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    forbidden = forbidden_argument_term(window_disposition, source_truth_class, public_claim_ceiling, operator_confirmation)
    if forbidden:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'LIVE-WINDOW-READOUT-ARGUMENT-BLOCKED',
            'message': f'Live-window readout arguments include forbidden raw/protected/contact term: {forbidden}',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if operator_confirmation.strip() != OPERATOR_CONFIRMATION:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'LIVE-WINDOW-READOUT-CONFIRMATION-BLOCKED',
            'message': f'operator-confirmation must be {OPERATOR_CONFIRMATION!r}',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if source_truth_class != card_data.get('source_truth_class'):
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'LIVE-WINDOW-READOUT-SOURCE-TRUTH-BLOCKED',
            'message': 'Readout source-truth class must match the terminal live-window card.',
            'card_source_truth_class': card_data.get('source_truth_class'),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    for field, value, upper, minimum in [
        ('aggregate-evidence-read-count', aggregate_evidence_read_count, 7, 1),
        ('claim-family-effect-count', claim_family_effect_count, 8, 1),
        ('decision-delta-count', decision_delta_count, 8, 0),
        ('field-trim-count', field_trim_count, 8, 0),
        ('reviewer-role-count', reviewer_role_count, 5, 2),
        ('unresolved-disagreement-count', unresolved_disagreement_count, 5, 0),
    ]:
        err = bounded_count_error(value, field, upper, minimum=minimum)
        if err:
            raise ValueError(json.dumps({
                'ok': False,
                'outcome': 'LIVE-WINDOW-READOUT-COUNT-BLOCKED',
                'message': err,
                'claim_ceiling': CLAIM_CEILING,
            }, indent=2))
    source_readout_count = card_data.get('window_controls', {}).get('evidence_readout_count')
    if isinstance(source_readout_count, int) and aggregate_evidence_read_count < source_readout_count:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'LIVE-WINDOW-READOUT-COUNT-BLOCKED',
            'message': 'aggregate-evidence-read-count cannot be below the source card evidence-readout count.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if normalized_disposition in {'continue_bounded', 'rerun_narrower'} and decision_delta_count < 1:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'LIVE-WINDOW-READOUT-DELTA-BLOCKED',
            'message': 'continue/rerun readouts require at least one bounded decision delta.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if normalized_disposition in {'rerun_narrower', 'no_change'} and field_trim_count < 1:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'LIVE-WINDOW-READOUT-TRIM-BLOCKED',
            'message': 'rerun/no-change readouts must trim at least one field before the next request.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if not (no_public_claim_upgrade and no_service_record_edit and no_lifecycle_change and no_closure_from_readout):
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'LIVE-WINDOW-READOUT-FIREBREAK-BLOCKED',
            'message': 'Readout requires explicit no-public-claim-upgrade, no-service-record-edit, no-lifecycle-change, and no-closure confirmations.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if any([raw_learner_data_present, protected_facts_present, security_payloads_present, public_claim_upgrade_requested]):
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'LIVE-WINDOW-READOUT-RISK-FLAG-BLOCKED',
            'message': 'Live-window readout cannot proceed with raw/protected/security/public-claim-upgrade flags.',
            'risk_flags': {
                'raw_learner_data_present': raw_learner_data_present,
                'protected_facts_present': protected_facts_present,
                'security_payloads_present': security_payloads_present,
                'public_claim_upgrade_requested': public_claim_upgrade_requested,
            },
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    out_dir = output_dir or default_output_dir(card_path)
    out_dir = out_dir if out_dir.is_absolute() else ROOT / out_dir
    allowed, boundary = output_allowed(out_dir, archive_root=ROOT)
    if not allowed:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'LIVE-WINDOW-READOUT-OUTPUT-BLOCKED',
            'message': f'Output directory is not allowed for local live-window readouts: {boundary}',
            'output_dir': relative_to_root(out_dir),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if out_dir.exists():
        if not overwrite:
            raise ValueError(json.dumps({
                'ok': False,
                'outcome': 'LIVE-WINDOW-READOUT-OUTPUT-EXISTS',
                'message': 'Output directory already exists; pass --overwrite to regenerate local scratch output.',
                'output_dir': relative_to_root(out_dir),
                'claim_ceiling': CLAIM_CEILING,
            }, indent=2))
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    record = {
        'readout_type': 'FT-0181-live-window-readout-record',
        'readout_version': REVISION,
        'created_at_utc': now,
        'followthrough_id': 'FT-0181',
        'service_record_id': 'AIEDU-SR-003',
        'readout_state': 'quarantined' if normalized_disposition == 'quarantine' else 'readout_complete',
        'window_disposition': normalized_disposition,
        'source_truth_class': source_truth_class,
        'public_claim_ceiling': public_claim_ceiling,
        'acceptance_state': 'NOT_ACCEPTED',
        'evidence_state': 'not_evidence',
        'closure_permitted': False,
        'closure_effect': 'does_not_close_ft0181',
        'public_claim_effect': 'none',
        'ft0181_status': 'live',
        'operator_confirmation': operator_confirmation,
        'source_live_window_card': source_card_snapshot(card_path, card_data),
        'readout_counts': {
            'aggregate_evidence_read_count': aggregate_evidence_read_count,
            'claim_family_effect_count': claim_family_effect_count,
            'decision_delta_count': decision_delta_count,
            'field_trim_count': field_trim_count,
            'reviewer_role_count': reviewer_role_count,
            'unresolved_disagreement_count': unresolved_disagreement_count,
        },
        'no_public_claim_upgrade': True,
        'no_service_record_edit': True,
        'no_lifecycle_change': True,
        'no_closure_from_readout': True,
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
            'contains_aggregate_counts_disposition_hashes_and_routes_only': True,
            'source_live_window_card_revalidated': True,
        },
        'claim_ceiling': CLAIM_CEILING,
        'required_next_surface': 'docs/30-operations/ft0181-post-readout-action-dispatch.md',
        'readout_effect': 'may_source_post_readout_action_dispatch_only',
        'public_language_effect': 'does_not_authorize_public_language_without_dispatch',
        'closure_boundary': 'This local readout does not close FT-0181 and does not prove service claims, learning, safety, access, workload, compliance, scale, or effectiveness.',
        'output_boundary': boundary,
    }
    integrity_error = owner_live_window_readout_integrity_error(record, archive_root=ROOT)
    if integrity_error:
        shutil.rmtree(out_dir, ignore_errors=True)
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'LIVE-WINDOW-READOUT-INTEGRITY-BLOCKED',
            'message': integrity_error,
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    (out_dir / 'live-window-readout.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    (out_dir / 'LIVE-WINDOW-READOUT-SUMMARY.md').write_text(build_summary(record), encoding='utf-8')
    return {
        'ok': True,
        'outcome': 'LIVE-WINDOW-READOUT-RECORDED',
        'readout': relative_to_root(out_dir / 'live-window-readout.json'),
        'summary': relative_to_root(out_dir / 'LIVE-WINDOW-READOUT-SUMMARY.md'),
        'window_disposition': normalized_disposition,
        'source_live_window_card': relative_to_root(card_path),
        'claim_ceiling': CLAIM_CEILING,
    }


def main() -> None:
    args = parse_args()
    try:
        result = build_live_window_readout(
            card=args.card,
            window_disposition=args.window_disposition,
            source_truth_class=args.source_truth_class,
            aggregate_evidence_read_count=args.aggregate_evidence_read_count,
            claim_family_effect_count=args.claim_family_effect_count,
            decision_delta_count=args.decision_delta_count,
            field_trim_count=args.field_trim_count,
            reviewer_role_count=args.reviewer_role_count,
            unresolved_disagreement_count=args.unresolved_disagreement_count,
            public_claim_ceiling=args.public_claim_ceiling,
            no_public_claim_upgrade=args.no_public_claim_upgrade,
            no_service_record_edit=args.no_service_record_edit,
            no_lifecycle_change=args.no_lifecycle_change,
            no_closure_from_readout=args.no_closure_from_readout,
            raw_learner_data_present=args.raw_learner_data_present,
            protected_facts_present=args.protected_facts_present,
            security_payloads_present=args.security_payloads_present,
            public_claim_upgrade_requested=args.public_claim_upgrade_requested,
            operator_confirmation=args.operator_confirmation,
            output_dir=args.output_dir,
            overwrite=args.overwrite,
        )
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"record_ft0181_live_window_readout: OK ({result['outcome']})")
        print(result['readout'])


if __name__ == '__main__':
    main()
