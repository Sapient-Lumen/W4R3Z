#!/usr/bin/env python3
"""Prepare a bounded FT-0181 post-readout action dispatch brief.

This scratch-only bridge sits after a human-recorded terminal live-window
readout and before the post-readout action dispatch. It collapses the dense
owner-post-readout-action command into one state-matched handoff, but it never
records the dispatch, performs owner-held action, edits service records, moves
lifecycle state, supports public language, creates custody/acceptance, or closes
FT-0181.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from ft0181_field_guards import (
    POST_READOUT_OWNER_ACTION_BY_LANE,
    POST_READOUT_NEXT_ASK_CLASSES,
    POST_READOUT_PUBLIC_LANGUAGE_ACTIONS,
    READOUT_DISPOSITION_TO_ACTION_LANE,
    archive_relative,
    field_scratch_lane_error,
    output_allowed,
    operator_today_iso,
    owner_live_window_readout_integrity_error,
    owner_post_readout_action_brief_integrity_error,
)
from record_ft0181_post_readout_action import OPERATOR_CONFIRMATION as ACTION_CONFIRMATION

ROOT = Path(__file__).resolve().parents[1]
REVISION = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8')).get('revision', 'unknown')
DEFAULT_OUTPUT_ROOT = ROOT / 'scratch' / 'field' / 'ft0181' / 'owner-post-readout-action-briefs'
CLAIM_CEILING = (
    'Post-readout action brief only; not a dispatch, not evidence, not SRC2+ acceptance, '
    'not custody evidence, not closure evidence, not public-summary support, and not proof '
    'of learning, safety, access, workload, compliance, scale, or effectiveness.'
)

LANE_TO_DASHED = {
    'blocked_no_real_packet': 'blocked-no-real-packet',
    'stop': 'stop',
    'rollback_confirmed': 'rollback-confirmed',
    'rerun_narrower': 'rerun-narrower',
    'continue_same_ceiling': 'continue-same-ceiling',
    'quarantine': 'quarantine',
    'no_change_trim': 'no-change-trim',
}
LANE_TO_DEFAULT_NEXT_ASK = {
    'blocked_no_real_packet': 'owner-packet-route-repair',
    'stop': 'fallback-availability-check',
    'rollback_confirmed': 'fallback-availability-check',
    'rerun_narrower': 'rerun-narrower-owner-packet',
    'continue_same_ceiling': 'bounded-owner-recheck',
    'quarantine': 'quarantine-resolution-ask',
    'no_change_trim': 'no-new-ask-with-trim-record',
}
LANE_TO_DEFAULT_PUBLIC_ACTION = {
    'blocked_no_real_packet': 'frozen-example-only',
    'stop': 'suppress-public-language',
    'rollback_confirmed': 'narrow-existing-language',
    'rerun_narrower': 'frozen-example-only',
    'continue_same_ceiling': 'frozen-example-only',
    'quarantine': 'suppress-public-language',
    'no_change_trim': 'no-public-language-change',
}
COMMAND_ORDER = ['primary', 'repair_route', 'stop_or_pause', 'rollback_confirmed', 'rerun_narrower', 'continue_same_ceiling', 'quarantine', 'no_change_trim']


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Prepare a bounded FT-0181 post-readout action brief from a terminal live-window readout.')
    parser.add_argument('--readout', required=True, type=Path, help='scratch/.../live-window-readout.json from owner-live-window-readout.')
    parser.add_argument('--as-of-date', default=operator_today_iso(), help='YYYY-MM-DD operator-local date used to propose the default +7 day recheck date.')
    parser.add_argument('--output-dir', type=Path, help='Local/scratch output directory for the action brief.')
    parser.add_argument('--overwrite', action='store_true', help='Replace an existing action brief directory.')
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


def default_output_dir(readout_path: Path) -> Path:
    digest = sha256_file(readout_path)[:12] if readout_path.exists() and readout_path.is_file() else 'missingreadout'
    stem = readout_path.parent.name.replace(' ', '-').replace('/', '-')[:48] or 'terminal-readout'
    return DEFAULT_OUTPUT_ROOT / f'{stem}-{digest}'


def source_readout_snapshot(readout_path: Path, readout_data: dict[str, Any]) -> dict[str, Any]:
    return {
        'reference': relative(readout_path),
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
        'source_live_window_card': readout_data.get('source_live_window_card'),
        'revalidated_for_post_readout_action_brief': True,
    }


def lane_counts(lane: str, readout_data: dict[str, Any]) -> dict[str, int]:
    readout_counts = readout_data.get('readout_counts') if isinstance(readout_data.get('readout_counts'), dict) else {}
    reviewer_count = max(2, int(readout_counts.get('reviewer_role_count') or 2))
    field_drop_count = int(readout_counts.get('field_trim_count') or 0)
    field_reask_count = 1 if lane == 'rerun_narrower' else 0
    if lane in {'rerun_narrower', 'no_change_trim'} and field_drop_count < 1:
        field_drop_count = 1
    allowed_action_count = 0 if lane in {'blocked_no_real_packet', 'quarantine'} else 1
    return {
        'allowed_action_count': allowed_action_count,
        'prohibited_action_count': 5,
        'field_to_reask_count': field_reask_count,
        'field_to_drop_count': field_drop_count,
        'reviewer_role_count': reviewer_count,
        'unresolved_disagreement_count': 0,
    }


def action_command(readout_path: Path, readout_data: dict[str, Any], lane: str, due_date: date, digest: str, label: str) -> str:
    counts = lane_counts(lane, readout_data)
    out = f'scratch/field/ft0181/owner-post-readout-actions/aiedu-sr-003-{label}-{digest}'
    return (
        f'make owner-post-readout-action READOUT={shell_quote(relative(readout_path))} '
        f'DISPATCH_LANE={LANE_TO_DASHED[lane]} '
        f'SOURCE_TRUTH_CLASS={shell_quote(str(readout_data.get("source_truth_class") or "SRC2"))} '
        f'ALLOWED_ACTION_COUNT={counts["allowed_action_count"]} '
        f'PROHIBITED_ACTION_COUNT={counts["prohibited_action_count"]} '
        f'FIELD_TO_REASK_COUNT={counts["field_to_reask_count"]} '
        f'FIELD_TO_DROP_COUNT={counts["field_to_drop_count"]} '
        f'REVIEWER_ROLE_COUNT={counts["reviewer_role_count"]} '
        f'DUE_OR_RECHECK_DATE={due_date.isoformat()} '
        f'OWNER_ACTION_CLASS={POST_READOUT_OWNER_ACTION_BY_LANE[lane]} '
        f'NEXT_EVIDENCE_ASK_CLASS={LANE_TO_DEFAULT_NEXT_ASK[lane]} '
        f'PUBLIC_LANGUAGE_ACTION={LANE_TO_DEFAULT_PUBLIC_ACTION[lane]} '
        'NO_EXPANSION_CONFIRMED=1 NO_PUBLIC_CLAIM_UPGRADE=1 NO_SERVICE_RECORD_EDIT=1 '
        'NO_LIFECYCLE_CHANGE=1 NO_CLOSURE_FROM_DISPATCH=1 '
        f'CONFIRM={ACTION_CONFIRMATION} OUT={out}'
    )


def action_commands(readout_path: Path, readout_data: dict[str, Any], due_date: date, digest: str) -> dict[str, str]:
    source_disposition = str(readout_data.get('window_disposition') or '')
    primary_lane = READOUT_DISPOSITION_TO_ACTION_LANE[source_disposition]
    labels = {
        'blocked_no_real_packet': 'repair_route',
        'stop': 'stop_or_pause',
        'rollback_confirmed': 'rollback_confirmed',
        'rerun_narrower': 'rerun_narrower',
        'continue_same_ceiling': 'continue_same_ceiling',
        'quarantine': 'quarantine',
        'no_change_trim': 'no_change_trim',
    }
    commands = {'primary': action_command(readout_path, readout_data, primary_lane, due_date, digest, 'primary')}
    commands[labels[primary_lane]] = action_command(readout_path, readout_data, primary_lane, due_date, digest, labels[primary_lane])
    return {key: commands[key] for key in COMMAND_ORDER if key in commands}


def build_markdown(brief: dict[str, Any]) -> str:
    readout = brief['source_live_window_readout']
    lines = [
        '# FT-0181 post-readout action brief',
        '',
        f"Brief state: `{brief['brief_state']}`",
        f"Source readout: `{readout['reference']}`",
        f"Readout SHA-256: `{readout['readout_sha256']}`",
        f"Window disposition: `{readout['window_disposition']}`",
        f"Primary dispatch lane: `{brief['primary_dispatch_lane']}`",
        f"Proposed due/recheck date: `{brief['proposed_due_or_recheck_date']}`",
        f"Acceptance state: `{brief['acceptance_state']}`",
        'Evidence effect: `not_evidence`',
        'Closure effect: `does_not_close_ft0181`',
        '',
        '## Human job',
        '',
        'Choose the bounded post-readout dispatch route that matches the already-recorded aggregate readout. Keep the action lane outside the archive until the due/recheck date or until new real owner context appears. Do not paste owner answers, learner facts, live-window notes, contact details, public claim text, screenshots, protected-route facts, or security payloads.',
    ]
    for title, command in brief['post_readout_action_command_templates'].items():
        lines.extend(['', f'### {title.replace("_", " ")}', '', '```bash', command, '```'])
    lines.extend([
        '',
        '## Hard boundary',
        '',
        'This brief does not record a post-readout action dispatch. It only revalidates the terminal readout and prepares bounded dispatch command skeletons. The resulting dispatch, if a human records it, still cannot edit service records, move lifecycle state, upgrade public language, create custody or acceptance, or close FT-0181.',
    ])
    return '\n'.join(lines) + '\n'


def build_post_readout_action_brief(*, readout: Path, as_of_date: str | None = None, output_dir: Path | None = None, overwrite: bool = False) -> dict[str, Any]:
    as_of = parse_iso_date(as_of_date or operator_today_iso(), 'as-of-date')
    readout_path = readout if readout.is_absolute() else ROOT / readout
    readout_path = readout_path.resolve()
    inside, parts = archive_relative(readout_path, archive_root=ROOT)
    lane_error = field_scratch_lane_error(readout_path, archive_root=ROOT, field_name='readout')
    if lane_error or readout_path.name != 'live-window-readout.json':
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-ACTION-BRIEF-READOUT-BLOCKED',
            'message': 'Post-readout action brief requires a scratch-local live-window-readout.json source.',
            'readout': relative(readout_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if not readout_path.exists() or not readout_path.is_file():
        raise FileNotFoundError(f'live-window readout not found: {readout_path}')
    readout_data = load_json(readout_path)
    readout_error = owner_live_window_readout_integrity_error(readout_data, archive_root=ROOT)
    if readout_error:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-ACTION-BRIEF-SOURCE-READOUT-BLOCKED',
            'message': readout_error,
            'readout': relative(readout_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    disposition = readout_data.get('window_disposition')
    if disposition not in READOUT_DISPOSITION_TO_ACTION_LANE:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-ACTION-BRIEF-DISPOSITION-BLOCKED',
            'message': 'Source readout disposition cannot be mapped to a bounded post-readout action lane.',
            'window_disposition': disposition,
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    out = output_dir or default_output_dir(readout_path)
    out = out if out.is_absolute() else ROOT / out
    allowed, boundary = output_allowed(out, archive_root=ROOT)
    if not allowed:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-ACTION-BRIEF-OUTPUT-BLOCKED',
            'message': boundary,
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if out.exists() and any(out.iterdir()):
        if not overwrite:
            raise FileExistsError(f'output directory exists and is not empty: {out}')
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)

    digest = sha256_file(readout_path)[:12]
    primary_lane = READOUT_DISPOSITION_TO_ACTION_LANE[str(disposition)]
    due = as_of + timedelta(days=7)
    brief = {
        'brief_type': 'FT-0181-post-readout-action-brief',
        'brief_version': REVISION,
        'followthrough_id': 'FT-0181',
        'service_record_id': 'AIEDU-SR-003',
        'created_at_utc': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'as_of_date': as_of.isoformat(),
        'brief_state': 'POST_READOUT_ACTION_BRIEF_PREPARED_NOT_DISPATCHED',
        'acceptance_state': 'NOT_ACCEPTED',
        'action_effect': 'does_not_record_post_readout_action',
        'evidence_state': 'not_evidence',
        'closure_effect': 'does_not_close_ft0181',
        'public_claim_effect': 'none',
        'service_record_effect': 'does_not_edit_service_records',
        'lifecycle_effect': 'does_not_change_lifecycle_state',
        'claim_ceiling': CLAIM_CEILING,
        'source_live_window_readout': source_readout_snapshot(readout_path, readout_data),
        'primary_dispatch_lane': primary_lane,
        'owner_action_class': POST_READOUT_OWNER_ACTION_BY_LANE[primary_lane],
        'next_evidence_ask_class': LANE_TO_DEFAULT_NEXT_ASK[primary_lane],
        'public_language_action': LANE_TO_DEFAULT_PUBLIC_ACTION[primary_lane],
        'proposed_due_or_recheck_date': due.isoformat(),
        'allowed_dispatch_lanes': [primary_lane],
        'post_readout_action_command_templates': action_commands(readout_path, readout_data, due, digest),
        'required_next_surface': 'docs/30-operations/ft0181-post-readout-action-dispatch.md',
        'ft0181_status': 'live',
        'dispatch_boundary': 'This brief does not record a post-readout action dispatch; a human must record the dispatch before any owner-held action lane or recheck clock can start.',
        'content_minimization': {
            'copies_owner_answers': False,
            'copies_raw_csv_rows': False,
            'copies_live_window_notes': False,
            'copies_contact_details': False,
            'copies_public_claim_text': False,
            'copies_learner_identifiers_or_protected_facts': False,
            'source_live_window_readout_revalidated': True,
            'contains_hashes_counts_dates_and_command_skeletons_only': True,
        },
        'forbidden_effects': [
            'post-readout-action-dispatch-recording',
            'owner-action-completion',
            'service-record-mutation',
            'public-claim-upgrade',
            'custody-or-acceptance',
            'lifecycle-or-closure',
        ],
        'output_dir': relative(out),
        'brief_path': relative(out / 'post-readout-action-brief.json'),
        'markdown_path': relative(out / 'POST-READOUT-ACTION-BRIEF.md'),
        'output_boundary': boundary,
    }
    error = owner_post_readout_action_brief_integrity_error(brief, archive_root=ROOT)
    if error:
        shutil.rmtree(out, ignore_errors=True)
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-READOUT-ACTION-BRIEF-INTEGRITY-BLOCKED',
            'message': error,
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    (out / 'post-readout-action-brief.json').write_text(json.dumps(brief, indent=2) + '\n', encoding='utf-8')
    (out / 'POST-READOUT-ACTION-BRIEF.md').write_text(build_markdown(brief), encoding='utf-8')
    return {
        'ok': True,
        'outcome': 'POST-READOUT-ACTION-BRIEF-PREPARED',
        'output_dir': relative(out),
        'brief_path': relative(out / 'post-readout-action-brief.json'),
        'markdown_path': relative(out / 'POST-READOUT-ACTION-BRIEF.md'),
        'source_live_window_readout': relative(readout_path),
        'brief_state': 'POST_READOUT_ACTION_BRIEF_PREPARED_NOT_DISPATCHED',
        'claim_ceiling': CLAIM_CEILING,
    }


def main() -> None:
    args = parse_args()
    try:
        result = build_post_readout_action_brief(
            readout=args.readout,
            as_of_date=args.as_of_date,
            output_dir=args.output_dir,
            overwrite=args.overwrite,
        )
    except (ValueError, FileNotFoundError, FileExistsError) as exc:
        raise SystemExit(str(exc)) from exc
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"prepare_ft0181_post_readout_action_brief: OK ({result['outcome']})")
        print(result['brief_path'])


if __name__ == '__main__':
    main()
