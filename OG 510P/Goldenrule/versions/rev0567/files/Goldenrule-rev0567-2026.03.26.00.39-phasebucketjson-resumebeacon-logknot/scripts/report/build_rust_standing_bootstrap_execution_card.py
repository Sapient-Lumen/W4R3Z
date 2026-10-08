#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SELECTOR_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_state_selector.json'
ROUTE_EQUIVALENCE_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_route_equivalence.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_execution_card.json'
OUT_MD = ROOT / 'docs' / 'RUST_STANDING_BOOTSTRAP_EXECUTION_CARD.md'
TOOL_PATH = ROOT / 'scripts' / 'tools' / 'emit_rust_standing_bootstrap_execution_plan.py'


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def _route_kind(state_id: str) -> str:
    if state_id == 'clean_head':
        return 'clean_head_bundle'
    if state_id == 'patchset_only':
        return 'post_patchset_bundle'
    if state_id == 'final_full':
        return 'already_final'
    return 'explicit_remaining_layers'


def _minimality_note(state_id: str) -> str:
    if state_id == 'clean_head':
        return 'One-shot clean-head bundle is the shortest exact landing from an untouched branch.'
    if state_id == 'patchset_only':
        return 'One-shot post-patchset bundle is the shortest exact landing after the monolithic comeback patchset has already landed.'
    if state_id == 'final_full':
        return 'No further bootstrap apply step should happen here; this state is already the proved final 4-file landing.'
    return 'A convenience bundle would over-assume branch state here, so the remaining layers stay explicit and exact.'


def build_report() -> dict[str, Any]:
    selector = _load(SELECTOR_REPORT)
    route = _load(ROUTE_EQUIVALENCE_REPORT)
    canonical_final_hash = str(route['summary']['canonical_final_hash'])
    target_files = list(selector['target_files'])
    state_plans: list[dict[str, Any]] = []
    for state in selector['states']:
        rec = state['recommendation']
        next_commands = list(rec.get('next_commands') or [])
        apply_commands = [cmd for cmd in next_commands if cmd.startswith('git apply ')]
        verification_commands = [cmd for cmd in next_commands if not cmd.startswith('git apply ')]
        state_plans.append(
            {
                'state_id': state['state_id'],
                'label': state['label'],
                'summary': rec['summary'],
                'action_kind': rec['action_kind'],
                'route_kind': _route_kind(state['state_id']),
                'minimality_note': _minimality_note(state['state_id']),
                'target_files': target_files,
                'file_hashes': dict(state['file_hashes']),
                'observed_combined_hash': state['combined_hash'],
                'apply_command_count': len(apply_commands),
                'apply_commands': apply_commands,
                'verification_command_count': len(verification_commands),
                'verification_commands': verification_commands,
                'primary_apply_hint': rec.get('primary_apply_hint'),
                'expected_final_state_id': 'final_full',
                'expected_final_combined_hash': canonical_final_hash,
                'post_apply_expectation': (
                    'Re-run the execution-plan tool; it should now recognize the checkout as final_full and report zero apply commands.'
                    if state['state_id'] != 'final_full'
                    else 'Do not apply another bootstrap patch; just run the exact witnesses and lane-smoke commands.'
                ),
                'notes': list(state.get('notes') or []),
            }
        )

    unknown_policy = {
        'state_id': selector['unknown_policy']['state_id'],
        'notes': list(selector['unknown_policy'].get('notes') or []),
        'action_kind': selector['unknown_policy']['recommendation']['action_kind'],
        'summary': selector['unknown_policy']['recommendation']['summary'],
        'primary_apply_hint': selector['unknown_policy']['recommendation'].get('primary_apply_hint'),
        'apply_commands': [],
        'verification_commands': list(selector['unknown_policy']['recommendation'].get('next_commands') or []),
        'expected_final_state_id': None,
        'expected_final_combined_hash': None,
    }

    nonfinal_count = len([plan for plan in state_plans if plan['state_id'] != 'final_full'])
    bundle_count = len([plan for plan in state_plans if 'bundle' in plan['route_kind']])
    layered_count = len([plan for plan in state_plans if plan['route_kind'] == 'explicit_remaining_layers'])

    return {
        'metadata': {
            'inventory_version': 1,
            'source_reports': [
                SELECTOR_REPORT.relative_to(ROOT).as_posix(),
                ROUTE_EQUIVALENCE_REPORT.relative_to(ROOT).as_posix(),
            ],
            'tool_path': TOOL_PATH.relative_to(ROOT).as_posix(),
        },
        'summary': {
            'state_plan_count': len(state_plans),
            'recognized_nonfinal_state_count': nonfinal_count,
            'bundle_route_count': bundle_count,
            'layered_route_count': layered_count,
            'canonical_final_state_id': 'final_full',
            'canonical_final_combined_hash': canonical_final_hash,
            'route_equivalence_final_state_equivalent': bool(route['summary']['final_state_equivalent']),
            'route_equivalence_all_routes_apply_ok': bool(route['summary']['all_routes_apply_ok']),
            'tool_invocation': 'python3 scripts/tools/emit_rust_standing_bootstrap_execution_plan.py --target-root . --json',
        },
        'target_files': target_files,
        'state_plans': state_plans,
        'unknown_policy': unknown_policy,
        'headline_findings': [
            'Every recognized non-final bootstrap branch state now carries a smallest-safe apply sequence plus the exact final combined hash it should converge to.',
            'The one-shot bundle routes are only offered where the archive already proved them exact for that branch state (`clean_head` and `patchset_only`).',
            'Partial-layer states remain explicit on purpose: the execution card preserves minimal exact continuation instead of guessing with a convenience bundle.',
            'The execution-plan tool now collapses selector + route-equivalence knowledge into one first-machine command that tells the inheritor what to apply next and what final hash to expect.',
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report['summary']
    lines = [
        '# Rust Standing Bootstrap Execution Card',
        '',
        'Generated by `scripts/report/build_rust_standing_bootstrap_execution_card.py`. This turns the exact-state selector plus the route-equivalence proof into one first-machine execution card for the bootstrap comeback lane: from each known branch state, it records the smallest safe apply sequence, the exact witness commands to run next, and the final 4-file hash the route should converge to.',
        '',
        '## Snapshot',
        '',
        f"- state_plan_count: `{summary['state_plan_count']}`",
        f"- recognized_nonfinal_state_count: `{summary['recognized_nonfinal_state_count']}`",
        f"- bundle_route_count: `{summary['bundle_route_count']}`",
        f"- layered_route_count: `{summary['layered_route_count']}`",
        f"- canonical_final_state_id: `{summary['canonical_final_state_id']}`",
        f"- canonical_final_combined_hash: `{summary['canonical_final_combined_hash']}`",
        f"- route_equivalence_final_state_equivalent: `{str(summary['route_equivalence_final_state_equivalent']).lower()}`",
        f"- tool invocation: `{summary['tool_invocation']}`",
        '',
        '## What this buys the inheritor',
        '',
    ]
    for finding in report['headline_findings']:
        lines.append(f'- {finding}')
    lines.extend([
        '',
        '## State summary',
        '',
        '| state | route kind | apply commands | verification commands | final hash |',
        '|---|---|---:|---:|---|',
    ])
    for plan in report['state_plans']:
        lines.append(
            f"| `{plan['state_id']}` | `{plan['route_kind']}` | {plan['apply_command_count']} | {plan['verification_command_count']} | `{plan['expected_final_combined_hash']}` |"
        )
    lines.extend([
        '',
        '## How to use it on the first Rust-capable machine',
        '',
        '1. Run `python3 scripts/tools/emit_rust_standing_bootstrap_execution_plan.py --target-root . --json` before applying any bootstrap patch.',
        '2. If the tool reports a recognized state, follow its `apply_commands` in order.',
        '3. After the apply phase, re-run the same tool; it should now report `final_full` and no more bootstrap apply commands.',
        '4. Then run the emitted `verification_commands` on the real Rust-capable machine.',
        '',
        '## Per-state details',
        '',
    ])
    for plan in report['state_plans']:
        lines.extend([
            f"### `{plan['state_id']}`",
            '',
            f"- label: `{plan['label']}`",
            f"- route_kind: `{plan['route_kind']}`",
            f"- summary: {plan['summary']}",
            f"- observed_combined_hash: `{plan['observed_combined_hash']}`",
            f"- expected_final_combined_hash: `{plan['expected_final_combined_hash']}`",
            f"- minimality_note: {plan['minimality_note']}",
            f"- post_apply_expectation: {plan['post_apply_expectation']}",
            '',
            '**Apply commands**',
            '',
        ])
        if plan['apply_commands']:
            for cmd in plan['apply_commands']:
                lines.append(f"- `{cmd}`")
        else:
            lines.append('- none')
        lines.extend([
            '',
            '**Verification commands**',
            '',
        ])
        if plan['verification_commands']:
            for cmd in plan['verification_commands']:
                lines.append(f"- `{cmd}`")
        else:
            lines.append('- none')
        if plan['notes']:
            lines.extend([
                '',
                '**Notes**',
                '',
            ])
            for note in plan['notes']:
                lines.append(f'- {note}')
        lines.append('')
    lines.extend([
        '## Unknown-state policy',
        '',
        f"- action_kind: `{report['unknown_policy']['action_kind']}`",
        f"- summary: {report['unknown_policy']['summary']}",
        '',
    ])
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()

    report = build_report()
    rendered = render_markdown(report)
    current_json = json.dumps(report, indent=2, sort_keys=True) + '\n'

    if args.write:
        OUT_JSON.write_text(current_json, encoding='utf-8')
        OUT_MD.write_text(rendered + '\n', encoding='utf-8')
        print(f"rust-standing-bootstrap-execution-card: wrote {OUT_JSON.relative_to(ROOT)}")
        print(f"rust-standing-bootstrap-execution-card: wrote {OUT_MD.relative_to(ROOT)}")
        return 0

    if not OUT_JSON.exists() or not OUT_MD.exists():
        print('rust-standing-bootstrap-execution-card: outputs missing; run with --write')
        return 1

    existing_json = OUT_JSON.read_text(encoding='utf-8')
    existing_md = OUT_MD.read_text(encoding='utf-8')
    if existing_json != current_json or existing_md != rendered + '\n':
        print('rust-standing-bootstrap-execution-card: drift detected; run with --write')
        return 1

    print(
        'rust-standing-bootstrap-execution-card: ok '
        f"(states={report['summary']['state_plan_count']} final={report['summary']['canonical_final_state_id']})"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
