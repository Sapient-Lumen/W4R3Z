#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
EXECUTION_CARD_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_execution_card.json'
VERIFICATION_LADDER_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_verification_ladder.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_checkpoints.json'
OUT_MD = ROOT / 'docs' / 'RUST_STANDING_BOOTSTRAP_CHECKPOINTS.md'
RUNTIME_TOOL = ROOT / 'scripts' / 'tools' / 'emit_rust_standing_bootstrap_checkpoints.py'
SELECTOR_TOOL = ROOT / 'scripts' / 'tools' / 'choose_rust_standing_bootstrap_path.py'
EXECUTION_TOOL = ROOT / 'scripts' / 'tools' / 'emit_rust_standing_bootstrap_execution_plan.py'

TRANSITIONS: dict[str, list[tuple[str, str]]] = {
    'clean_head': [('git apply artifacts/patches/rust_standing_bootstrap_comeback_bundle.patch', 'final_full')],
    'repair_only': [
        ('git apply artifacts/patches/rust_standing_bootstrap_guard.patch', 'repair_guard'),
        ('git apply artifacts/patches/rust_external_test_patchset.patch', 'final_full'),
    ],
    'guard_only': [
        ('git apply artifacts/patches/rust_standing_bootstrap_repair.patch', 'repair_guard'),
        ('git apply artifacts/patches/rust_external_test_patchset.patch', 'final_full'),
    ],
    'repair_guard': [('git apply artifacts/patches/rust_external_test_patchset.patch', 'final_full')],
    'patchset_only': [('git apply artifacts/patches/rust_standing_bootstrap_post_patchset_bundle.patch', 'final_full')],
    'patchset_repair': [('git apply artifacts/patches/rust_standing_bootstrap_guard.patch', 'final_full')],
    'patchset_guard': [('git apply artifacts/patches/rust_standing_bootstrap_repair.patch', 'final_full')],
    'final_full': [],
}
COMMAND_TO_PATCH_KIND = {
    'git apply artifacts/patches/rust_standing_bootstrap_comeback_bundle.patch': 'bundle',
    'git apply artifacts/patches/rust_standing_bootstrap_guard.patch': 'guard',
    'git apply artifacts/patches/rust_external_test_patchset.patch': 'patchset',
    'git apply artifacts/patches/rust_standing_bootstrap_repair.patch': 'repair',
    'git apply artifacts/patches/rust_standing_bootstrap_post_patchset_bundle.patch': 'post_patchset_bundle',
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def build_report() -> dict[str, Any]:
    execution = _load(EXECUTION_CARD_REPORT)
    verification = _load(VERIFICATION_LADDER_REPORT)
    target_files = execution['target_files']
    by_state = {state['state_id']: state for state in execution['state_plans']}
    states: list[dict[str, Any]] = []
    for state in execution['state_plans']:
        state_id = state['state_id']
        transitions = TRANSITIONS[state_id]
        checkpoints: list[dict[str, Any]] = []
        cumulative_patch_kinds: list[str] = []
        for step_index, (command, next_state_id) in enumerate(transitions, start=1):
            next_state = by_state[next_state_id]
            patch_kind = COMMAND_TO_PATCH_KIND[command]
            cumulative_patch_kinds.append(patch_kind)
            checkpoints.append(
                {
                    'step_index': step_index,
                    'apply_command': command,
                    'applied_patch_kind': patch_kind,
                    'cumulative_patch_kinds': list(cumulative_patch_kinds),
                    'expected_state_id': next_state_id,
                    'expected_label': next_state['label'],
                    'expected_combined_hash': next_state['observed_combined_hash'],
                    'expected_action_kind': next_state['action_kind'],
                    'expected_remaining_apply_command_count': len(next_state['apply_commands']),
                    'expected_remaining_apply_commands': list(next_state['apply_commands']),
                    'selector_check_command': 'python3 scripts/tools/choose_rust_standing_bootstrap_path.py --target-root . --json',
                    'execution_plan_check_command': 'python3 scripts/tools/emit_rust_standing_bootstrap_execution_plan.py --target-root . --json',
                    'checkpoint_note': (
                        'After this apply, re-run the selector or execution-plan tool and confirm the checkout is now '
                        f"`{next_state_id}` before moving on."
                    ),
                    'final_verification_handoff': next_state_id == 'final_full',
                }
            )
        states.append(
            {
                'state_id': state_id,
                'label': state['label'],
                'route_kind': state['route_kind'],
                'action_kind': state['action_kind'],
                'summary': state['summary'],
                'file_hashes': state['file_hashes'],
                'observed_combined_hash': state['observed_combined_hash'],
                'apply_commands': list(state['apply_commands']),
                'verification_commands': list(state['verification_commands']),
                'expected_final_combined_hash': state['expected_final_combined_hash'],
                'post_apply_expectation': state['post_apply_expectation'],
                'checkpoint_count': len(checkpoints),
                'checkpoints': checkpoints,
                'final_verification_gate_command': 'python3 scripts/tools/emit_rust_standing_bootstrap_verification_ladder.py --target-root . --json',
                'final_verification_stage_count': len(verification['stages']),
            }
        )
    total_checkpoint_count = sum(state['checkpoint_count'] for state in states)
    return {
        'metadata': {
            'inventory_version': 1,
            'source_reports': [
                EXECUTION_CARD_REPORT.relative_to(ROOT).as_posix(),
                VERIFICATION_LADDER_REPORT.relative_to(ROOT).as_posix(),
            ],
            'runtime_tool': RUNTIME_TOOL.relative_to(ROOT).as_posix(),
            'selector_tool': SELECTOR_TOOL.relative_to(ROOT).as_posix(),
            'execution_tool': EXECUTION_TOOL.relative_to(ROOT).as_posix(),
        },
        'target_files': target_files,
        'summary': {
            'recognized_state_count': len(states),
            'recognized_nonfinal_state_count': len([state for state in states if state['state_id'] != 'final_full']),
            'states_with_intermediate_checkpoint_count': len([state for state in states if state['checkpoint_count'] > 1]),
            'total_checkpoint_count': total_checkpoint_count,
            'canonical_final_combined_hash': execution['summary']['canonical_final_combined_hash'],
            'tool_invocation': 'python3 scripts/tools/emit_rust_standing_bootstrap_checkpoints.py --target-root . --json',
            'selector_invocation': 'python3 scripts/tools/choose_rust_standing_bootstrap_path.py --target-root . --json',
        },
        'headline_findings': [
            'The bootstrap comeback lane now has exact intermediate checkpoints, not just exact starting-state routing and final-state verification.',
            'For every recognized non-final bootstrap branch state, each emitted apply command is paired with the exact state id and 4-file combined hash that should appear immediately after that step.',
            'The convenience bundles remain one-step paths; the layered states now expose the smallest safe pause points so the inheritor can detect a bad partial landing before charging into the next patch.',
            'The final checkpoint handoff is explicit: once a step lands `final_full`, switch from apply sequencing to the verification-ladder tool rather than improvising a broader smoke run.',
        ],
        'state_checkpoints': states,
        'unknown_policy': {
            'summary': 'Unknown or mixed branch state: do not trust intermediate checkpoints. Re-run the state selector, inspect diffs, and restore one of the exact known branch states first.',
            'action_kind': execution['unknown_policy']['action_kind'],
            'selector_command': 'python3 scripts/tools/choose_rust_standing_bootstrap_path.py --target-root . --json',
            'execution_plan_command': 'python3 scripts/tools/emit_rust_standing_bootstrap_execution_plan.py --target-root . --json',
            'checkpoint_count': 0,
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    s = report['summary']
    lines = [
        '# Rust Standing Bootstrap Checkpoints',
        '',
        'Generated by `scripts/report/build_rust_standing_bootstrap_checkpoints.py`. This turns the bootstrap execution card into exact post-apply pause points: after each emitted patch command, the first Rust-capable inheritor can re-run the selector or execution-plan tool and confirm the checkout reached the exact expected intermediate state before moving on.',
        '',
        '## Snapshot',
        '',
        f"- recognized_state_count: `{s['recognized_state_count']}`",
        f"- recognized_nonfinal_state_count: `{s['recognized_nonfinal_state_count']}`",
        f"- states_with_intermediate_checkpoint_count: `{s['states_with_intermediate_checkpoint_count']}`",
        f"- total_checkpoint_count: `{s['total_checkpoint_count']}`",
        f"- canonical_final_combined_hash: `{s['canonical_final_combined_hash']}`",
        f"- tool invocation: `{s['tool_invocation']}`",
        '',
        '## Why this exists',
        '',
    ]
    for finding in report['headline_findings']:
        lines.append(f'- {finding}')
    lines.extend([
        '',
        '## State summary',
        '',
        '| state | apply cmds | checkpoints | final handoff |',
        '|---|---:|---:|---|',
    ])
    for state in report['state_checkpoints']:
        handoff = state['checkpoints'][-1]['expected_state_id'] if state['checkpoints'] else state['state_id']
        lines.append(f"| `{state['state_id']}` | {len(state['apply_commands'])} | {state['checkpoint_count']} | `{handoff}` |")
    lines.extend([
        '',
        '## Exact checkpoints by recognized state',
        '',
    ])
    for state in report['state_checkpoints']:
        lines.extend([
            f"### `{state['state_id']}`",
            '',
            f"- route_kind: `{state['route_kind']}`",
            f"- action_kind: `{state['action_kind']}`",
            f"- observed_combined_hash: `{state['observed_combined_hash']}`",
            f"- checkpoint_count: `{state['checkpoint_count']}`",
            '',
        ])
        if not state['checkpoints']:
            lines.extend([
                '- No further apply checkpoints. This state is already final; switch to the verification ladder instead.',
                f"- verification handoff: `{state['final_verification_gate_command']}`",
                '',
            ])
            continue
        for checkpoint in state['checkpoints']:
            lines.extend([
                f"#### Step {checkpoint['step_index']}",
                '',
                f"- apply_command: `{checkpoint['apply_command']}`",
                f"- expected_state_id: `{checkpoint['expected_state_id']}`",
                f"- expected_combined_hash: `{checkpoint['expected_combined_hash']}`",
                f"- expected_remaining_apply_command_count: `{checkpoint['expected_remaining_apply_command_count']}`",
                f"- selector_check_command: `{checkpoint['selector_check_command']}`",
                f"- execution_plan_check_command: `{checkpoint['execution_plan_check_command']}`",
                f"- checkpoint_note: {checkpoint['checkpoint_note']}",
                '',
            ])
        lines.extend([
            f"- final verification handoff after last checkpoint: `{state['final_verification_gate_command']}`",
            '',
        ])
    lines.extend([
        '## Safe operational reading',
        '',
        '1. Use this only after the state selector recognizes an exact known bootstrap branch state. Mixed or drifted states are intentionally excluded.',
        '2. After every apply step, re-run the selector or execution-plan tool and compare the reported state id plus combined hash against the checkpoint in this card.',
        '3. Once the final checkpoint reaches `final_full`, stop applying patches and switch to `emit_rust_standing_bootstrap_verification_ladder.py` for the cheapest exact post-apply proof.',
        '',
    ])
    return '\n'.join(lines)


def _check(expected_report: dict[str, Any], expected_markdown: str) -> int:
    if not OUT_JSON.exists() or not OUT_MD.exists():
        print('rust-standing-bootstrap-checkpoints: missing outputs; run with --write', file=sys.stderr)
        return 1
    if json.loads(OUT_JSON.read_text(encoding='utf-8')) != expected_report:
        print('rust-standing-bootstrap-checkpoints: report drift detected', file=sys.stderr)
        return 1
    if OUT_MD.read_text(encoding='utf-8').rstrip('\n') != expected_markdown.rstrip('\n'):
        print('rust-standing-bootstrap-checkpoints: markdown drift detected', file=sys.stderr)
        return 1
    print('rust-standing-bootstrap-checkpoints: ok exact intermediate checkpoint states remain reproducible')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    report = build_report()
    markdown = render_markdown(report)
    if args.write:
        OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        OUT_MD.write_text(markdown + '\n', encoding='utf-8')
        print(f'wrote {OUT_JSON.relative_to(ROOT)}')
        print(f'wrote {OUT_MD.relative_to(ROOT)}')
        return 0
    return _check(report, markdown)


if __name__ == '__main__':
    raise SystemExit(main())
