#!/usr/bin/env python3
"""Prepare a bounded FT-0181 post-readout recheck brief.

This scratch-only bridge sits after a human-recorded post-readout action dispatch
has reached its due/recheck date and before the human records the due-date
recheck. It collapses the dense owner-post-readout-recheck command into one
state-matched handoff, but it never records the recheck, copies new owner
context, performs intake, edits service records, moves lifecycle state, supports
public language, creates custody/acceptance, or closes FT-0181.
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
    operator_today_iso,
    owner_post_readout_action_integrity_error,
    owner_post_readout_recheck_brief_integrity_error,
)
from record_ft0181_post_readout_recheck import OPERATOR_CONFIRMATION as RECHECK_CONFIRMATION

ROOT = Path(__file__).resolve().parents[1]
REVISION = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8')).get('revision', 'unknown')
DEFAULT_OUTPUT_ROOT = ROOT / 'scratch' / 'field' / 'ft0181' / 'owner-post-readout-recheck-briefs'
CLAIM_CEILING = (
    'Post-readout recheck brief only; not a recheck, not evidence, not SRC2+ acceptance, '
    'not custody evidence, not closure evidence, not public-summary support, not owner-context '
    'intake, and not proof of learning, safety, access, workload, compliance, scale, or effectiveness.'
)

OUTCOME_TO_DASHED = {
    'no_new_owner_context': 'no-new-owner-context',
    'new_owner_context_available': 'new-owner-context-available',
    'owner_action_complete_no_closure': 'owner-action-complete-no-closure',
    'route_blocked_no_owner': 'route-blocked-no-owner',
}
OUTCOME_TO_LABEL = {
    'no_new_owner_context': 'no-new-context',
    'new_owner_context_available': 'new-context-held-outside-archive',
    'owner_action_complete_no_closure': 'action-complete-no-closure',
    'route_blocked_no_owner': 'route-blocked-no-owner',
}
COMMAND_ORDER = [
    'primary',
    'no_new_owner_context',
    'new_owner_context_available',
    'owner_action_complete_no_closure',
    'route_blocked_no_owner',
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Prepare a bounded FT-0181 post-readout recheck brief from a post-readout action dispatch.')
    parser.add_argument('--action', required=True, type=Path, help='scratch/.../post-readout-action.json from owner-post-readout-action.')
    parser.add_argument('--as-of-date', default=operator_today_iso(), help='YYYY-MM-DD operator-local date used as the proposed recheck date; must be on/after the dispatch due_or_recheck_date.')
    parser.add_argument('--output-dir', type=Path, help='Local/scratch output directory for the recheck brief.')
    parser.add_argument('--overwrite', action='store_true', help='Replace an existing recheck brief directory.')
    parser.add_argument('--json', action='store_true', help='Print machine-readable result.')
    return parser.parse_args()


def parse_iso_date(value: str, field: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f'{field} must be YYYY-MM-DD') from exc


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


def shell_quote(value: str) -> str:
    if value.replace('/', '').replace('-', '').replace('_', '').replace('.', '').isalnum():
        return value
    return "'" + value.replace("'", "'\\''") + "'"


def default_output_dir(action_path: Path, check_date: date) -> Path:
    digest = sha256_file(action_path)[:12] if action_path.exists() and action_path.is_file() else 'missingaction'
    stem = action_path.parent.name.replace(' ', '-').replace('/', '-')[:48] or 'post-readout-action'
    return DEFAULT_OUTPUT_ROOT / f'{stem}-{check_date.isoformat()}-{digest}'


def source_action_snapshot(action_path: Path, action_data: dict[str, Any]) -> dict[str, Any]:
    return {
        'reference': relative(action_path),
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
        'next_evidence_ask': action_data.get('next_evidence_ask'),
        'revalidated_for_post_readout_recheck_brief': True,
    }


def reviewer_role_count(action_data: dict[str, Any]) -> int:
    counts = action_data.get('dispatch_counts') if isinstance(action_data.get('dispatch_counts'), dict) else {}
    return max(2, int(counts.get('reviewer_role_count') or 2))


def recheck_command(action_path: Path, action_data: dict[str, Any], outcome: str, check_date: date, digest: str) -> str:
    out = f'scratch/field/ft0181/owner-post-readout-rechecks/aiedu-sr-003-{OUTCOME_TO_LABEL[outcome]}-{check_date.isoformat()}-{digest}'
    command = (
        f'make owner-post-readout-recheck ACTION={shell_quote(relative(action_path))} '
        f'CHECK_DATE={check_date.isoformat()} '
        f'RECHECK_OUTCOME={OUTCOME_TO_DASHED[outcome]} '
        f'REVIEWER_ROLE_COUNT={reviewer_role_count(action_data)} '
        'NO_EXPANSION_CONFIRMED=1 NO_PUBLIC_CLAIM_UPGRADE=1 NO_SERVICE_RECORD_EDIT=1 '
        'NO_LIFECYCLE_CHANGE=1 NO_CLOSURE_FROM_RECHECK=1 '
    )
    if outcome == 'new_owner_context_available':
        command += 'NEW_OWNER_CONTEXT_HELD_OUTSIDE_ARCHIVE=1 '
    command += f'CONFIRM={RECHECK_CONFIRMATION} OUT={out}'
    return command


def recheck_commands(action_path: Path, action_data: dict[str, Any], check_date: date, digest: str) -> dict[str, str]:
    commands = {
        outcome: recheck_command(action_path, action_data, outcome, check_date, digest)
        for outcome in sorted(POST_READOUT_RECHECK_OUTCOMES)
    }
    commands['primary'] = commands['no_new_owner_context']
    return {key: commands[key] for key in COMMAND_ORDER if key in commands}


def build_markdown(brief: dict[str, Any]) -> str:
    action = brief['source_post_readout_action']
    lines = [
        '# FT-0181 post-readout recheck brief',
        '',
        f"Brief state: `{brief['brief_state']}`",
        f"Source dispatch: `{action['reference']}`",
        f"Dispatch SHA-256: `{action['action_sha256']}`",
        f"Dispatch lane: `{action['dispatch_lane']}`",
        f"Source due/recheck date: `{action['due_or_recheck_date']}`",
        f"Proposed check date: `{brief['proposed_check_date']}`",
        f"Acceptance state: `{brief['acceptance_state']}`",
        'Evidence effect: `not_evidence`',
        'Closure effect: `does_not_close_ft0181`',
        '',
        '## Human job',
        '',
        'Choose exactly one bounded recheck route after the due/recheck date. If new real owner context exists, keep the context outside the archive and record only the new-context-available recheck; then route the actual returned CSV/source packet through owner-field-next. Do not paste owner answers, learner facts, contact details, public claim text, screenshots, protected-route facts, or security payloads into this brief or the recheck record.',
    ]
    for title, command in brief['post_readout_recheck_command_templates'].items():
        lines.extend(['', f'### {title.replace("_", " ")}', '', '```bash', command, '```'])
    lines.extend([
        '',
        '## Hard boundary',
        '',
        'This brief does not record a post-readout recheck and does not route owner context. It only revalidates the source dispatch and prepares bounded recheck command skeletons. A later recheck, if human-recorded, still cannot edit service records, move lifecycle state, upgrade public language, create custody or acceptance, or close FT-0181.',
    ])
    return '\n'.join(lines) + '\n'


def build_post_readout_recheck_brief(*, action: Path, as_of_date: str | None = None, output_dir: Path | None = None, overwrite: bool = False) -> dict[str, Any]:
    as_of = parse_iso_date(as_of_date or operator_today_iso(), 'as-of-date')
    action_path = action if action.is_absolute() else ROOT / action
    action_path = action_path.resolve()
    inside, parts = archive_relative(action_path, archive_root=ROOT)
    lane_error = field_scratch_lane_error(action_path, archive_root=ROOT, field_name='action')
    if lane_error or action_path.name != 'post-readout-action.json':
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-RECHECK-BRIEF-ACTION-BLOCKED',
            'message': 'Post-readout recheck brief requires a scratch-local post-readout-action.json source.',
            'action': relative(action_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if not action_path.exists() or not action_path.is_file():
        raise FileNotFoundError(f'post-readout action dispatch not found: {action_path}')
    action_data = load_json(action_path)
    action_error = owner_post_readout_action_integrity_error(action_data, archive_root=ROOT)
    if action_error:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-RECHECK-BRIEF-SOURCE-ACTION-BLOCKED',
            'message': action_error,
            'action': relative(action_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    due = parse_iso_date(str(action_data.get('due_or_recheck_date') or ''), 'source due_or_recheck_date')
    if as_of < due:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-RECHECK-BRIEF-TOO-EARLY-BLOCKED',
            'message': 'Post-readout recheck brief cannot be prepared before the source dispatch due_or_recheck_date.',
            'as_of_date': as_of.isoformat(),
            'source_due_or_recheck_date': due.isoformat(),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    out = output_dir or default_output_dir(action_path, as_of)
    out = out if out.is_absolute() else ROOT / out
    allowed, boundary = output_allowed(out, archive_root=ROOT)
    if not allowed:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-RECHECK-BRIEF-OUTPUT-BLOCKED',
            'message': boundary,
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if out.exists() and any(out.iterdir()):
        if not overwrite:
            raise FileExistsError(f'output directory exists and is not empty: {out}')
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)

    digest = sha256_file(action_path)[:12]
    brief = {
        'brief_type': 'FT-0181-post-readout-recheck-brief',
        'brief_version': REVISION,
        'followthrough_id': 'FT-0181',
        'service_record_id': 'AIEDU-SR-003',
        'created_at_utc': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'as_of_date': as_of.isoformat(),
        'brief_state': 'POST_READOUT_RECHECK_BRIEF_PREPARED_NOT_RECHECKED',
        'acceptance_state': 'NOT_ACCEPTED',
        'recheck_effect': 'does_not_record_post_readout_recheck',
        'evidence_state': 'not_evidence',
        'closure_effect': 'does_not_close_ft0181',
        'public_claim_effect': 'none',
        'service_record_effect': 'does_not_edit_service_records',
        'lifecycle_effect': 'does_not_change_lifecycle_state',
        'claim_ceiling': CLAIM_CEILING,
        'source_post_readout_action': source_action_snapshot(action_path, action_data),
        'proposed_check_date': as_of.isoformat(),
        'allowed_recheck_outcomes': sorted(POST_READOUT_RECHECK_OUTCOMES),
        'default_recheck_outcome': 'no_new_owner_context',
        'post_readout_recheck_command_templates': recheck_commands(action_path, action_data, as_of, digest),
        'required_next_surface': 'docs/30-operations/ft0181-post-readout-recheck-gate.md',
        'ft0181_status': 'live',
        'recheck_boundary': 'This brief does not record a post-readout recheck; a human must choose one bounded recheck outcome after the due/recheck date before any context receipt, service-record edit, lifecycle move, public language, custody, acceptance, or closure step.',
        'content_minimization': {
            'copies_owner_answers': False,
            'copies_raw_csv_rows': False,
            'copies_live_window_notes': False,
            'copies_contact_details': False,
            'copies_public_claim_text': False,
            'copies_new_owner_context': False,
            'copies_learner_identifiers_or_protected_facts': False,
            'source_post_readout_action_revalidated': True,
            'contains_hashes_counts_dates_and_command_skeletons_only': True,
        },
        'forbidden_effects': [
            'post-readout-recheck-recording',
            'new-owner-context-intake',
            'service-record-mutation',
            'public-claim-upgrade',
            'custody-or-acceptance',
            'lifecycle-or-closure',
        ],
        'output_dir': relative(out),
        'brief_path': relative(out / 'post-readout-recheck-brief.json'),
        'markdown_path': relative(out / 'POST-READOUT-RECHECK-BRIEF.md'),
        'output_boundary': boundary,
    }
    error = owner_post_readout_recheck_brief_integrity_error(brief, archive_root=ROOT)
    if error:
        shutil.rmtree(out, ignore_errors=True)
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-RECHECK-BRIEF-INTEGRITY-BLOCKED',
            'message': error,
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    (out / 'post-readout-recheck-brief.json').write_text(json.dumps(brief, indent=2) + '\n', encoding='utf-8')
    (out / 'POST-READOUT-RECHECK-BRIEF.md').write_text(build_markdown(brief), encoding='utf-8')
    return {
        'ok': True,
        'outcome': 'POST-READOUT-RECHECK-BRIEF-PREPARED',
        'output_dir': relative(out),
        'brief_path': relative(out / 'post-readout-recheck-brief.json'),
        'markdown_path': relative(out / 'POST-READOUT-RECHECK-BRIEF.md'),
        'source_post_readout_action': relative(action_path),
        'brief_state': 'POST_READOUT_RECHECK_BRIEF_PREPARED_NOT_RECHECKED',
        'claim_ceiling': CLAIM_CEILING,
    }


def main() -> None:
    args = parse_args()
    try:
        result = build_post_readout_recheck_brief(
            action=args.action,
            as_of_date=args.as_of_date,
            output_dir=args.output_dir,
            overwrite=args.overwrite,
        )
    except (ValueError, FileNotFoundError, FileExistsError) as exc:
        raise SystemExit(str(exc)) from exc
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"prepare_ft0181_post_readout_recheck_brief: OK ({result['outcome']})")
        print(result['brief_path'])


if __name__ == '__main__':
    main()
