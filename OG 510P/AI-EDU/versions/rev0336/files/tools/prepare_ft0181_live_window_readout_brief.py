#!/usr/bin/env python3
"""Prepare a bounded FT-0181 terminal live-window readout brief.

This scratch-only bridge sits after a human-recorded terminal live-window card
and before a terminal aggregate readout. It makes the readout command small and
state-matched, but it never records the readout, copies owner/live-window notes,
edits service records, supports public language, creates custody/acceptance,
moves lifecycle state, or closes FT-0181.
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
    LIVE_WINDOW_READOUT_TERMINAL_STATES,
    LIVE_WINDOW_STATE_TO_DISPOSITIONS,
    archive_relative,
    field_scratch_lane_error,
    output_allowed,
    owner_live_window_card_integrity_error,
    owner_live_window_readout_brief_integrity_error,
)
from record_ft0181_live_window_readout import OPERATOR_CONFIRMATION as READOUT_CONFIRMATION

ROOT = Path(__file__).resolve().parents[1]
REVISION = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8')).get('revision', 'unknown')
DEFAULT_OUTPUT_ROOT = ROOT / 'scratch' / 'field' / 'ft0181' / 'owner-live-window-readout-briefs'
CLAIM_CEILING = (
    'Terminal live-window readout brief only; not a readout, not evidence, not SRC2+ acceptance, '
    'not custody evidence, not closure evidence, not public-summary support, and not proof of '
    'learning, safety, access, workload, compliance, scale, or effectiveness.'
)
PREFERRED_DISPOSITION = {
    'paused': 'stopped',
    'rolled_back': 'rolled-back',
    'completed_no_closure': 'continue-bounded',
    'quarantined': 'quarantine',
}
COMMAND_ORDER = ['primary', 'stop_or_pause', 'rollback_confirmed', 'continue_same_ceiling', 'rerun_narrower', 'quarantine', 'no_change_trim']


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Prepare a bounded FT-0181 readout brief from a terminal live-window card.')
    parser.add_argument('--card', required=True, type=Path, help='scratch/.../live-window-card.json in paused, rolled_back, completed_no_closure, or quarantined state.')
    parser.add_argument('--output-dir', type=Path, help='Local/scratch output directory for the readout brief.')
    parser.add_argument('--overwrite', action='store_true', help='Replace an existing readout brief directory.')
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


def shell_quote(value: str) -> str:
    if value.replace('/', '').replace('-', '').replace('_', '').replace('.', '').isalnum():
        return value
    return "'" + value.replace("'", "'\\''") + "'"


def default_output_dir(card_path: Path) -> Path:
    digest = sha256_file(card_path)[:12] if card_path.exists() and card_path.is_file() else 'missingcard'
    stem = card_path.parent.name.replace(' ', '-').replace('/', '-')[:48] or 'terminal-live-window-card'
    return DEFAULT_OUTPUT_ROOT / f'{stem}-{digest}'


def source_card_snapshot(card_path: Path, card_data: dict[str, Any]) -> dict[str, Any]:
    return {
        'reference': relative(card_path),
        'card_sha256': sha256_file(card_path),
        'window_state': card_data.get('window_state'),
        'source_truth_class': card_data.get('source_truth_class'),
        'public_claim_ceiling': card_data.get('public_claim_ceiling'),
        'window_controls': card_data.get('window_controls'),
        'acceptance_state': card_data.get('acceptance_state'),
        'evidence_state': card_data.get('evidence_state'),
        'readout_effect': card_data.get('readout_effect'),
        'live_window_card_effect': card_data.get('live_window_card_effect'),
        'source_post_decision_change_ticket': card_data.get('source_post_decision_change_ticket'),
        'revalidated_for_live_window_readout_brief': True,
    }


def readout_command(card_path: Path, card_data: dict[str, Any], disposition: str, digest: str, label: str) -> str:
    controls = card_data.get('window_controls') if isinstance(card_data.get('window_controls'), dict) else {}
    evidence_count = max(1, int(controls.get('evidence_readout_count') or 1))
    reviewer_count = max(2, int(controls.get('rollback_owner_role_count') or 1))
    decision_delta = 1 if disposition in {'continue-bounded', 'rerun-narrower'} else 0
    field_trim = 1 if disposition in {'rerun-narrower', 'no-change'} else 0
    out = f'scratch/field/ft0181/owner-live-window-readouts/aiedu-sr-003-{label}-{digest}'
    return (
        f'make owner-live-window-readout CARD={shell_quote(relative(card_path))} '
        f'WINDOW_DISPOSITION={disposition} '
        f'SOURCE_TRUTH_CLASS={shell_quote(str(card_data.get("source_truth_class") or "SRC2"))} '
        f'AGGREGATE_EVIDENCE_READ_COUNT={evidence_count} CLAIM_FAMILY_EFFECT_COUNT=2 '
        f'DECISION_DELTA_COUNT={decision_delta} FIELD_TRIM_COUNT={field_trim} '
        f'REVIEWER_ROLE_COUNT={reviewer_count} '
        'NO_PUBLIC_CLAIM_UPGRADE=1 NO_SERVICE_RECORD_EDIT=1 NO_LIFECYCLE_CHANGE=1 NO_CLOSURE_FROM_READOUT=1 '
        f'CONFIRM={READOUT_CONFIRMATION} OUT={out}'
    )


def readout_commands(card_path: Path, card_data: dict[str, Any], digest: str) -> dict[str, str]:
    source_state = str(card_data.get('window_state'))
    allowed = LIVE_WINDOW_STATE_TO_DISPOSITIONS.get(source_state, set())
    templates: dict[str, str] = {}
    preferred = PREFERRED_DISPOSITION[source_state]
    templates['primary'] = readout_command(card_path, card_data, preferred, digest, 'primary')
    for disposition, label in [
        ('stopped', 'stop_or_pause'),
        ('rolled-back', 'rollback_confirmed'),
        ('continue-bounded', 'continue_same_ceiling'),
        ('rerun-narrower', 'rerun_narrower'),
        ('quarantine', 'quarantine'),
        ('no-change', 'no_change_trim'),
    ]:
        normalized = disposition.replace('-', '_')
        if normalized in allowed:
            templates[label] = readout_command(card_path, card_data, disposition, digest, label)
    return {key: templates[key] for key in COMMAND_ORDER if key in templates}


def build_markdown(brief: dict[str, Any]) -> str:
    card = brief['source_live_window_card']
    lines = [
        '# FT-0181 terminal live-window readout brief',
        '',
        f"Brief state: `{brief['brief_state']}`",
        f"Source card: `{card['reference']}`",
        f"Card SHA-256: `{card['card_sha256']}`",
        f"Terminal window state: `{card['window_state']}`",
        f"Source truth class: `{card['source_truth_class']}`",
        f"Acceptance state: `{brief['acceptance_state']}`",
        'Evidence effect: `not_evidence`',
        'Closure effect: `does_not_close_ft0181`',
        '',
        '## Human job',
        '',
        'Choose one aggregate readout disposition that matches the already-recorded terminal live-window card. Use only aggregate counts and route choices. Do not paste owner answers, live notes, raw CSV rows, learner facts, protected facts, screenshots, security payloads, contact details, or public claim text.',
    ]
    for title, command in brief['readout_command_templates'].items():
        lines.extend(['', f'### {title.replace("_", " ")}', '', '```bash', command, '```'])
    lines.extend([
        '',
        '## Hard boundary',
        '',
        'This brief does not record the readout. It only revalidates the terminal live-window card and prepares bounded readout command skeletons. The resulting readout, if a human records it, still cannot edit service records, move lifecycle state, upgrade public language, create custody or acceptance, or close FT-0181.',
    ])
    return '\n'.join(lines) + '\n'


def build_readout_brief(*, card: Path, output_dir: Path | None = None, overwrite: bool = False) -> dict[str, Any]:
    card_path = card if card.is_absolute() else ROOT / card
    card_path = card_path.resolve()
    inside, parts = archive_relative(card_path, archive_root=ROOT)
    lane_error = field_scratch_lane_error(card_path, archive_root=ROOT, field_name='card')
    if lane_error or card_path.name != 'live-window-card.json':
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'LIVE-WINDOW-READOUT-BRIEF-CARD-BLOCKED',
            'message': 'Readout brief requires a scratch-local terminal live-window-card.json source.',
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
            'outcome': 'LIVE-WINDOW-READOUT-BRIEF-SOURCE-CARD-BLOCKED',
            'message': card_error,
            'card': relative(card_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if card_data.get('window_state') not in LIVE_WINDOW_READOUT_TERMINAL_STATES:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'LIVE-WINDOW-READOUT-BRIEF-TERMINAL-CARD-REQUIRED',
            'message': 'Readout brief can only be prepared from paused, rolled_back, completed_no_closure, or quarantined live-window cards.',
            'window_state': card_data.get('window_state'),
            'card': relative(card_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    out = output_dir or default_output_dir(card_path)
    out = out if out.is_absolute() else ROOT / out
    allowed, boundary = output_allowed(out, archive_root=ROOT)
    if not allowed:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'LIVE-WINDOW-READOUT-BRIEF-OUTPUT-BLOCKED',
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
        'brief_type': 'FT-0181-live-window-readout-brief',
        'brief_version': REVISION,
        'followthrough_id': 'FT-0181',
        'service_record_id': 'AIEDU-SR-003',
        'created_at_utc': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'brief_state': 'READOUT_BRIEF_PREPARED_NOT_RECORDED',
        'acceptance_state': 'NOT_ACCEPTED',
        'readout_effect': 'does_not_record_readout',
        'evidence_state': 'not_evidence',
        'closure_effect': 'does_not_close_ft0181',
        'public_claim_effect': 'none',
        'claim_ceiling': CLAIM_CEILING,
        'source_live_window_card': source_card_snapshot(card_path, card_data),
        'preferred_readout_disposition': PREFERRED_DISPOSITION[str(card_data.get('window_state'))].replace('-', '_'),
        'allowed_readout_dispositions': sorted(LIVE_WINDOW_STATE_TO_DISPOSITIONS[str(card_data.get('window_state'))]),
        'readout_command_templates': readout_commands(card_path, card_data, digest),
        'required_next_surface': 'docs/30-operations/ft0181-end-of-window-readout-disposition-gate.md',
        'ft0181_status': 'live',
        'readout_boundary': 'This brief does not record a live-window readout; a human must record the aggregate readout before post-readout dispatch routing.',
        'content_minimization': {
            'copies_owner_answers': False,
            'copies_raw_csv_rows': False,
            'copies_live_window_notes': False,
            'copies_contact_details': False,
            'copies_learner_identifiers_or_protected_facts': False,
            'source_live_window_card_revalidated': True,
            'contains_hashes_counts_and_command_skeletons_only': True,
        },
        'forbidden_effects': [
            'readout-recording',
            'post-readout-action-dispatch',
            'service-record-mutation',
            'public-claim-upgrade',
            'custody-or-acceptance',
            'lifecycle-or-closure',
        ],
        'output_dir': relative(out),
        'brief_path': relative(out / 'live-window-readout-brief.json'),
        'markdown_path': relative(out / 'LIVE-WINDOW-READOUT-BRIEF.md'),
        'output_boundary': boundary,
    }
    error = owner_live_window_readout_brief_integrity_error(brief, archive_root=ROOT)
    if error:
        shutil.rmtree(out, ignore_errors=True)
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'LIVE-WINDOW-READOUT-BRIEF-INTEGRITY-BLOCKED',
            'message': error,
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    (out / 'live-window-readout-brief.json').write_text(json.dumps(brief, indent=2) + '\n', encoding='utf-8')
    (out / 'LIVE-WINDOW-READOUT-BRIEF.md').write_text(build_markdown(brief), encoding='utf-8')
    return {
        'ok': True,
        'outcome': 'LIVE-WINDOW-READOUT-BRIEF-PREPARED',
        'output_dir': relative(out),
        'brief_path': relative(out / 'live-window-readout-brief.json'),
        'markdown_path': relative(out / 'LIVE-WINDOW-READOUT-BRIEF.md'),
        'source_live_window_card': relative(card_path),
        'brief_state': 'READOUT_BRIEF_PREPARED_NOT_RECORDED',
        'claim_ceiling': CLAIM_CEILING,
    }


def main() -> None:
    args = parse_args()
    try:
        result = build_readout_brief(card=args.card, output_dir=args.output_dir, overwrite=args.overwrite)
    except (ValueError, FileNotFoundError, FileExistsError) as exc:
        raise SystemExit(str(exc)) from exc
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"prepare_ft0181_live_window_readout_brief: OK ({result['outcome']})")
        print(result['brief_path'])


if __name__ == '__main__':
    main()
