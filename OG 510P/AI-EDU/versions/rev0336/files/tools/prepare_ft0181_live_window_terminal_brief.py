#!/usr/bin/env python3
"""Prepare a bounded FT-0181 live-window terminal-state brief.

This scratch-only bridge sits after a staged/active live-window card and before
recording a terminal card state. It exists to prevent the late-field window from
stalling in a nonterminal local state or drifting into readout/closure language
without a human-recorded terminal window card. It emits command skeletons only;
it does not record a new card, readout, action dispatch, evidence, custody,
public claim support, lifecycle movement, service-record mutation, or closure.
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
    owner_live_window_card_integrity_error,
    owner_live_window_terminal_brief_integrity_error,
)
from record_ft0181_live_window_card import OPERATOR_CONFIRMATION as LIVE_WINDOW_CONFIRMATION

ROOT = Path(__file__).resolve().parents[1]
REVISION = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8')).get('revision', 'unknown')
DEFAULT_OUTPUT_ROOT = ROOT / 'scratch' / 'field' / 'ft0181' / 'owner-live-window-terminal-briefs'
CLAIM_CEILING = (
    'Live-window terminal-state brief only; not a live-window card, not a readout, '
    'not evidence, not SRC2+ acceptance, not custody evidence, not closure evidence, '
    'not public-summary support, and not proof of learning, safety, access, workload, '
    'compliance, scale, or effectiveness.'
)

TERMINAL_COMMAND_STATES = {
    'paused_stop_state': 'paused',
    'rolled_back_stop_state': 'rolled-back',
    'completed_no_closure': 'completed-no-closure',
    'quarantined_stop_state': 'quarantined',
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Prepare a bounded FT-0181 live-window terminal-state brief from a staged/active live-window card.')
    parser.add_argument('--card', required=True, type=Path, help='scratch/.../live-window-card.json in staged or active state.')
    parser.add_argument('--output-dir', type=Path, help='Local/scratch output directory for the terminal-state brief.')
    parser.add_argument('--overwrite', action='store_true', help='Replace an existing terminal-state brief directory.')
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


def default_output_dir(card_path: Path) -> Path:
    digest = sha256_file(card_path)[:12] if card_path.exists() and card_path.is_file() else 'missingcard'
    stem = card_path.parent.name.replace(' ', '-').replace('/', '-')[:48] or 'live-window-card'
    return DEFAULT_OUTPUT_ROOT / f'{stem}-{digest}'


def shell_quote(value: str) -> str:
    if value.replace('/', '').replace('-', '').replace('_', '').replace('.', '').isalnum():
        return value
    return "'" + value.replace("'", "'\\''") + "'"


def source_card_snapshot(card_path: Path, card_data: dict[str, Any]) -> dict[str, Any]:
    return {
        'reference': relative(card_path),
        'card_sha256': sha256_file(card_path),
        'window_state': card_data.get('window_state'),
        'source_truth_class': card_data.get('source_truth_class'),
        'public_claim_ceiling': card_data.get('public_claim_ceiling'),
        'window_controls': card_data.get('window_controls'),
        'source_post_decision_change_ticket': card_data.get('source_post_decision_change_ticket'),
        'acceptance_state': card_data.get('acceptance_state'),
        'evidence_state': card_data.get('evidence_state'),
        'readout_effect': card_data.get('readout_effect'),
        'live_window_card_effect': card_data.get('live_window_card_effect'),
        'revalidated_for_terminal_brief': True,
    }


def terminal_card_commands(card_data: dict[str, Any], card_digest: str) -> dict[str, str]:
    source_ticket = card_data.get('source_post_decision_change_ticket') if isinstance(card_data.get('source_post_decision_change_ticket'), dict) else {}
    ticket_ref = str(source_ticket.get('reference') or 'scratch/MISSING/post-decision-change-ticket.json')
    controls = card_data.get('window_controls') if isinstance(card_data.get('window_controls'), dict) else {}
    source_truth = str(card_data.get('source_truth_class') or 'SRC2')
    public_ceiling = str(card_data.get('public_claim_ceiling') or 'example-only-no-outcome-claim')
    common = (
        f'TICKET={shell_quote(ticket_ref)} '
        f'SOURCE_TRUTH_CLASS={source_truth} '
        f'WINDOW_DAY_COUNT={int(controls.get("window_day_count") or 1)} '
        f'ALLOWED_ACTIVITY_COUNT={int(controls.get("allowed_activity_count") or 1)} '
        f'PROHIBITED_ACTIVITY_COUNT={int(controls.get("prohibited_activity_count") or 5)} '
        f'STOP_TRIGGER_COUNT={int(controls.get("stop_trigger_count") or 3)} '
        f'ROLLBACK_STEP_COUNT={int(controls.get("rollback_step_count") or 3)} '
        f'ROLLBACK_OWNER_ROLE_COUNT={int(controls.get("rollback_owner_role_count") or 1)} '
        f'EVIDENCE_READOUT_COUNT={int(controls.get("evidence_readout_count") or 3)} '
        f'PUBLIC_CLAIM_CEILING={public_ceiling} '
        'NO_EXPANSION_CONFIRMED=1 HUMAN_PAUSE_CONFIRMED=1 FALLBACK_ROUTE_CONFIRMED=1 '
        f'CONFIRM={LIVE_WINDOW_CONFIRMATION}'
    )
    commands: dict[str, str] = {}
    for key, state in TERMINAL_COMMAND_STATES.items():
        out_state = state.replace('-', '-')
        commands[key] = (
            f'make owner-live-window-card WINDOW_STATE={state} {common} '
            f'OUT=scratch/field/ft0181/owner-live-window-cards/aiedu-sr-003-terminal-{out_state}-{card_digest}'
        )
    return commands


def build_markdown(brief: dict[str, Any]) -> str:
    card = brief['source_live_window_card']
    lines = [
        '# FT-0181 live-window terminal-state brief',
        '',
        f"Brief state: `{brief['brief_state']}`",
        f"Source card: `{card['reference']}`",
        f"Card SHA-256: `{card['card_sha256']}`",
        f"Current window state: `{card['window_state']}`",
        f"Source truth class: `{card['source_truth_class']}`",
        f"Acceptance state: `{brief['acceptance_state']}`",
        'Evidence effect: `not_evidence`',
        'Closure effect: `does_not_close_ft0181`',
        '',
        '## Human job',
        '',
        'Choose exactly one terminal state only after the real bounded live-window condition is true: pause/stop, rollback, completed-with-no-closure, or quarantine. Do not use this brief to edit service records, upgrade public language, accept evidence, create custody, record a readout, or close FT-0181.',
    ]
    for title, command in brief['terminal_card_command_templates'].items():
        lines.extend(['', f'### {title.replace("_", " ")}', '', '```bash', command, '```'])
    lines.extend([
        '',
        '## Hard boundary',
        '',
        'This brief does not record the terminal card. It only revalidates the nonterminal live-window card and prepares bounded card-recording commands. A terminal card must still be recorded by a human before the router can emit the end-of-window readout gate.',
    ])
    return '\n'.join(lines) + '\n'


def build_terminal_brief(*, card: Path, output_dir: Path | None = None, overwrite: bool = False) -> dict[str, Any]:
    card_path = card if card.is_absolute() else ROOT / card
    card_path = card_path.resolve()
    inside, parts = archive_relative(card_path, archive_root=ROOT)
    lane_error = field_scratch_lane_error(card_path, archive_root=ROOT, field_name='card')
    if lane_error or card_path.name != 'live-window-card.json':
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'LIVE-WINDOW-TERMINAL-BRIEF-CARD-BLOCKED',
            'message': 'Terminal-state brief requires a scratch-local live-window-card.json source.',
            'card': relative(card_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if not card_path.exists() or not card_path.is_file():
        raise FileNotFoundError(f'live-window card not found: {card_path}')
    card_data = load_json(card_path)
    card_error = owner_live_window_card_integrity_error(card_data, archive_root=ROOT)
    if card_error:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'LIVE-WINDOW-TERMINAL-BRIEF-SOURCE-CARD-BLOCKED',
            'message': card_error,
            'card': relative(card_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if card_data.get('window_state') not in {'staged', 'active'}:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'LIVE-WINDOW-TERMINAL-BRIEF-NONTERMINAL-CARD-REQUIRED',
            'message': 'Terminal-state brief can only be prepared from staged or active live-window cards.',
            'window_state': card_data.get('window_state'),
            'card': relative(card_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    out = output_dir or default_output_dir(card_path)
    allowed, boundary = output_allowed(out, archive_root=ROOT)
    if not allowed:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'LIVE-WINDOW-TERMINAL-BRIEF-OUTPUT-BLOCKED',
            'message': boundary,
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if out.exists() and any(out.iterdir()):
        if not overwrite:
            raise FileExistsError(f'output directory exists and is not empty: {out}')
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)

    digest = sha256_file(card_path)[:12]
    brief = {
        'brief_type': 'FT-0181-live-window-terminal-state-brief',
        'brief_version': REVISION,
        'followthrough_id': 'FT-0181',
        'service_record_id': 'AIEDU-SR-003',
        'created_at_utc': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'brief_state': 'TERMINAL_STATE_BRIEF_PREPARED_NOT_RECORDED',
        'acceptance_state': 'NOT_ACCEPTED',
        'terminal_card_effect': 'does_not_record_live_window_card',
        'readout_effect': 'does_not_record_readout',
        'evidence_state': 'not_evidence',
        'closure_effect': 'does_not_close_ft0181',
        'public_claim_effect': 'none',
        'claim_ceiling': CLAIM_CEILING,
        'source_live_window_card': source_card_snapshot(card_path, card_data),
        'terminal_card_command_templates': terminal_card_commands(card_data, digest),
        'allowed_terminal_states': ['paused', 'rolled_back', 'completed_no_closure', 'quarantined'],
        'required_next_surface': 'docs/30-operations/ft0181-live-window-stop-rollback-card.md',
        'ft0181_status': 'live',
        'terminal_boundary': 'This brief does not record a terminal live-window card; a human must record exactly one terminal card before readout routing.',
        'content_minimization': {
            'copies_owner_answers': False,
            'copies_raw_csv_rows': False,
            'copies_live_window_card_text': False,
            'copies_contact_details': False,
            'copies_learner_identifiers_or_protected_facts': False,
            'source_live_window_card_revalidated': True,
            'contains_hashes_counts_and_command_skeletons_only': True,
        },
        'forbidden_effects': [
            'terminal-card-recording',
            'readout-recording',
            'service-record-mutation',
            'public-claim-upgrade',
            'custody-or-acceptance',
            'lifecycle-or-closure',
        ],
        'output_boundary': boundary,
    }
    brief_error = owner_live_window_terminal_brief_integrity_error(brief, archive_root=ROOT)
    if brief_error:
        raise AssertionError('generated terminal-state brief failed integrity check: ' + brief_error)
    (out / 'terminal-brief.json').write_text(json.dumps(brief, indent=2) + '\n', encoding='utf-8')
    (out / 'TERMINAL-STATE-BRIEF.md').write_text(build_markdown(brief), encoding='utf-8')
    result = dict(brief)
    result.update({
        'ok': True,
        'outcome': 'LIVE-WINDOW-TERMINAL-BRIEF-PREPARED',
        'output_dir': relative(out),
        'brief_path': relative(out / 'terminal-brief.json'),
        'markdown_path': relative(out / 'TERMINAL-STATE-BRIEF.md'),
    })
    return result


def main() -> int:
    args = parse_args()
    try:
        result = build_terminal_brief(card=args.card, output_dir=args.output_dir, overwrite=args.overwrite)
    except Exception as exc:  # noqa: BLE001 - CLI emits structured failure.
        print(str(exc))
        return 1
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"LIVE-WINDOW-TERMINAL-BRIEF-PREPARED: {result['brief_path']}")
        print(f"NEXT: choose one command from {result['markdown_path']} only after a real terminal window condition exists")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
