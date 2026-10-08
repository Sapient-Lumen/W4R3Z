#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
FRONTIER_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_patch_prefix_frontier.json'
SHARDS_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_external_test_patch_shards.json'
PATCHSET_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_external_test_patchset.json'
REHEARSAL_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_external_test_patch_rehearsal.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rust_comeback_execution_card.json'
OUT_MD = ROOT / 'docs' / 'RUST_COMEBACK_EXECUTION_CARD.md'


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def _round(value: float) -> float:
    return round(float(value), 5)


def _unique(items: list[str]) -> list[str]:
    out: list[str] = []
    for item in items:
        if item not in out:
            out.append(item)
    return out


def _cumulative_apply_hint(entries: list[dict[str, Any]]) -> str:
    return ' && '.join(f"git apply {entry['patch_path']}" for entry in entries)


def _test_target_from_file(path: str) -> str:
    return Path(path).stem


def _lane_smoke_commands(target_files: list[str]) -> list[str]:
    return [f"cargo test -p gr_engine --test {_test_target_from_file(path)}" for path in target_files]


def _plateau_card(
    *,
    label: str,
    objective: str,
    prefix_index: int,
    prefixes_by_index: dict[int, dict[str, Any]],
    shard_entries: list[dict[str, Any]],
    monolithic_apply_hint: str | None = None,
) -> dict[str, Any]:
    prefix = prefixes_by_index[prefix_index]
    cumulative = prefix['cumulative']
    shard_slice = shard_entries[:prefix_index]
    latest_shard = shard_entries[prefix_index - 1]
    new_exact_witness_commands = _unique(list(latest_shard.get('future_cargo_hints') or []))
    cumulative_exact_witness_commands = _unique(
        [hint for entry in shard_slice for hint in entry.get('future_cargo_hints') or []]
    )
    target_files = list(cumulative['target_files'])
    test_targets = [_test_target_from_file(path) for path in target_files]
    card: dict[str, Any] = {
        'label': label,
        'prefix_index': int(prefix_index),
        'objective': objective,
        'rows_covered': int(cumulative['rows_covered']),
        'rows_remaining': int(cumulative['rows_remaining']),
        'rows_coverage_fraction': _round(cumulative['rows_coverage_fraction']),
        'added_lines': int(cumulative['added_lines']),
        'helper_count': int(cumulative['helper_count']),
        'test_count': int(cumulative['test_count']),
        'lane_count': int(cumulative['lane_count']),
        'lanes': list(cumulative['lanes']),
        'lift_band_counts': dict(cumulative['lift_band_counts']),
        'target_files': target_files,
        'test_targets': test_targets,
        'latest_patch_path': str(prefix['latest_patch_path']),
        'latest_seed_path': str(prefix['latest_seed_path']),
        'latest_lane_mix': str(prefix['latest_lane_mix']),
        'latest_bundle_strategy': str(prefix['latest_bundle_strategy']),
        'milestones_hit': list(prefix['milestones_hit']),
        'apply_hint': _cumulative_apply_hint(shard_slice),
        'new_exact_witness_count': len(new_exact_witness_commands),
        'new_exact_witness_commands': new_exact_witness_commands,
        'cumulative_exact_witness_count': len(cumulative_exact_witness_commands),
        'cumulative_exact_witness_commands': cumulative_exact_witness_commands,
        'lane_smoke_commands': _lane_smoke_commands(target_files),
        'latest_shard_exact_witnesses_by_target': {
            target: len([cmd for cmd in new_exact_witness_commands if f'--test {target} ' in cmd])
            for target in test_targets
        },
        'cumulative_exact_witnesses_by_target': {
            target: len([cmd for cmd in cumulative_exact_witness_commands if f'--test {target} ' in cmd])
            for target in test_targets
        },
    }
    if monolithic_apply_hint and label == 'full_closure':
        card['alternate_apply_hint'] = monolithic_apply_hint
    return card


def build_report() -> dict[str, Any]:
    frontier = _load(FRONTIER_REPORT)
    shards = _load(SHARDS_REPORT)
    patchset = _load(PATCHSET_REPORT)
    rehearsal = _load(REHEARSAL_REPORT)

    shard_entries = list(shards.get('entries') or [])
    prefixes_by_index = {int(entry['prefix_index']): entry for entry in frontier.get('prefixes') or []}
    stop_points = {str(entry['label']): entry for entry in frontier.get('stop_points') or []}
    milestones = {str(entry['label']): entry for entry in frontier.get('milestones') or []}
    if not shard_entries:
        raise ValueError('rust_comeback_execution_card: shard report has no entries')

    final_shard = shard_entries[-1]
    probe_only_prefixes = [
        int(entry['prefix_index'])
        for entry in frontier.get('prefixes') or []
        if list((entry.get('cumulative') or {}).get('lanes') or []) == ['probe_run']
    ]
    last_probe_only_prefix = max(probe_only_prefixes) if probe_only_prefixes else 0
    all_probe_run_prefix = int(frontier['summary']['all_probe_run_prefix'])
    full_closure_prefix = int(frontier['summary']['full_closure_prefix'])
    probe_run_closure_requires_dual_lane = (
        all_probe_run_prefix == full_closure_prefix
        and str(final_shard.get('lane_mix')) == 'dual_lane'
        and 'metamorphic_suite' in (final_shard.get('lanes') or [])
        and 'probe_run' in (final_shard.get('lanes') or [])
    )

    plateau_cards = [
        _plateau_card(
            label='quick_foothold',
            objective=str(stop_points['quick_foothold']['why_stop_here']),
            prefix_index=int(stop_points['quick_foothold']['prefix_index']),
            prefixes_by_index=prefixes_by_index,
            shard_entries=shard_entries,
        ),
        _plateau_card(
            label='lift_first_closure',
            objective=str(stop_points['lift_first_closure']['why_stop_here']),
            prefix_index=int(stop_points['lift_first_closure']['prefix_index']),
            prefixes_by_index=prefixes_by_index,
            shard_entries=shard_entries,
        ),
        _plateau_card(
            label='first_externalize_now',
            objective=str(milestones['first_externalize_now']['rationale']),
            prefix_index=int(milestones['first_externalize_now']['prefix_index']),
            prefixes_by_index=prefixes_by_index,
            shard_entries=shard_entries,
        ),
        _plateau_card(
            label='full_closure',
            objective=str(stop_points['full_closure']['why_stop_here']),
            prefix_index=full_closure_prefix,
            prefixes_by_index=prefixes_by_index,
            shard_entries=shard_entries,
            monolithic_apply_hint=str(patchset['patch']['apply_hint']),
        ),
    ]

    all_exact_witness_commands = _unique(
        [hint for entry in shard_entries for hint in entry.get('future_cargo_hints') or []]
    )
    all_test_targets = _unique(
        [_test_target_from_file(path) for entry in frontier.get('prefixes') or [] for path in (entry.get('cumulative') or {}).get('target_files') or []]
    )
    full_card = plateau_cards[-1]

    headline_findings = [
        (
            f"There is no pure probe-only closure plateau: the last probe witness lands only in shard prefix {all_probe_run_prefix}, "
            f"and that same shard is dual-lane, so full `probe_run` closure and full queue closure coincide."
        ),
        (
            f"Shard prefixes 1 through {last_probe_only_prefix} remain single-target `probe_run` work; `metamorphic_suite` only enters the execution surface in shard {final_shard['series_index']}."
        ),
        (
            f"The full comeback asks for {len(all_exact_witness_commands)} exact witness commands across {len(all_test_targets)} test targets; "
            f"{full_card['cumulative_exact_witnesses_by_target'].get('probe_run', 0)} of them stay in `probe_run`."
        ),
        (
            f"The first clean closure is still prefix {plateau_cards[1]['prefix_index']}: it lands {plateau_cards[1]['cumulative_exact_witness_count']} exact witnesses "
            f"while keeping the execution surface to one test target."
        ),
        (
            f"Patch-application equivalence remains preserved at full closure (`final_state_equivalent={rehearsal['summary']['final_state_equivalent']}`), "
            f"so the stepwise execution plan and the monolithic patch still converge on the same file state, and a post-patchset bootstrap follow-on can now be compressed into one extra apply step."
        ),
    ]

    execution_recipe = [
        {
            'rank': 1,
            'action': 'Refresh the static runbook before editing on the first Rust-capable machine.',
            'command': 'make update-rust-comeback-execution-card',
        },
        {
            'rank': 2,
            'action': 'Choose one plateau instead of freehanding an apply/run sequence.',
            'recommended_labels': [card['label'] for card in plateau_cards],
        },
        {
            'rank': 3,
            'action': 'Apply only the cumulative shard prefix for that plateau and run the new exact witnesses first.',
            'plateau_apply_hints': {card['label']: card['apply_hint'] for card in plateau_cards},
        },
        {
            'rank': 4,
            'action': 'After the exact witnesses pass, broaden to the lane-level smoke commands for the touched test targets.',
            'plateau_lane_smoke_hints': {card['label']: card['lane_smoke_commands'] for card in plateau_cards},
        },
        {
            'rank': 5,
            'action': 'Use the monolithic patch only when you intentionally want full closure in one jump.',
            'command': str(patchset['patch']['apply_hint']),
            'post_patchset_followon': 'git apply artifacts/patches/rust_standing_bootstrap_post_patchset_bundle.patch',
        },
    ]

    return {
        'metadata': {
            'inventory_version': 1,
            'source_reports': [
                FRONTIER_REPORT.relative_to(ROOT).as_posix(),
                SHARDS_REPORT.relative_to(ROOT).as_posix(),
                PATCHSET_REPORT.relative_to(ROOT).as_posix(),
                REHEARSAL_REPORT.relative_to(ROOT).as_posix(),
            ],
        },
        'summary': {
            'plateau_count': len(plateau_cards),
            'full_closure_prefix': full_closure_prefix,
            'all_probe_run_prefix': all_probe_run_prefix,
            'last_probe_only_prefix': last_probe_only_prefix,
            'probe_run_closure_requires_dual_lane': probe_run_closure_requires_dual_lane,
            'exact_witness_total': len(all_exact_witness_commands),
            'test_target_total': len(all_test_targets),
            'probe_run_exact_witness_total': int(full_card['cumulative_exact_witnesses_by_target'].get('probe_run', 0)),
            'metamorphic_exact_witness_total': int(full_card['cumulative_exact_witnesses_by_target'].get('metamorphic_suite', 0)),
            'full_closure_test_targets': list(full_card['test_targets']),
            'monolithic_apply_hint': str(patchset['patch']['apply_hint']),
            'final_state_equivalent': bool(rehearsal['summary']['final_state_equivalent']),
            'monolithic_apply_ok': bool(rehearsal['summary']['monolithic_apply_ok']),
            'shard_series_apply_ok': bool(rehearsal['summary']['shard_series_apply_ok']),
            'final_dual_lane_shard_index': int(final_shard['series_index']),
            'final_dual_lane_shard_path': str(final_shard['patch_path']),
        },
        'plateau_cards': plateau_cards,
        'execution_recipe': execution_recipe,
        'headline_findings': headline_findings,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report['summary']
    lines = [
        '# Rust Comeback Execution Card',
        '',
        'Generated by `scripts/report/build_rust_comeback_execution_card.py`. This turns the shard-prefix frontier into a first-machine apply/run card so the eventual Rust-capable inheritor can choose a plateau and know exactly which new witnesses and lane-smoke commands to run next.',
        '',
        '## Snapshot',
        '',
        f"- plateau_count: {summary['plateau_count']}",
        f"- all_probe_run_prefix: {summary['all_probe_run_prefix']}",
        f"- last_probe_only_prefix: {summary['last_probe_only_prefix']}",
        f"- full_closure_prefix: {summary['full_closure_prefix']}",
        f"- probe_run_closure_requires_dual_lane: {summary['probe_run_closure_requires_dual_lane']}",
        f"- exact_witness_total: {summary['exact_witness_total']}",
        f"- probe_run_exact_witness_total: {summary['probe_run_exact_witness_total']}",
        f"- metamorphic_exact_witness_total: {summary['metamorphic_exact_witness_total']}",
        f"- final_state_equivalent: {summary['final_state_equivalent']}",
        '',
        '## Headline findings',
        '',
    ]
    for finding in report['headline_findings']:
        lines.append(f'- {finding}')
    lines.extend([
        '',
        '## Plateau card',
        '',
        '| Plateau | Prefix | Rows covered | Added lines | Exact witnesses | Test targets | New witness commands |',
        '| --- | ---: | ---: | ---: | ---: | --- | ---: |',
    ])
    for card in report['plateau_cards']:
        targets = ', '.join(f"`{target}`" for target in card['test_targets'])
        lines.append(
            f"| `{card['label']}` | {card['prefix_index']} | {card['rows_covered']} | {card['added_lines']} | {card['cumulative_exact_witness_count']} | {targets} | {card['new_exact_witness_count']} |"
        )
    lines.extend([
        '',
        '## Plateau details',
        '',
    ])
    for card in report['plateau_cards']:
        lines.extend([
            f"### `{card['label']}`",
            '',
            f"- objective: {card['objective']}",
            f"- prefix_index: {card['prefix_index']}",
            f"- rows_covered: {card['rows_covered']}",
            f"- rows_remaining: {card['rows_remaining']}",
            f"- rows_coverage_fraction: {card['rows_coverage_fraction']}",
            f"- added_lines: {card['added_lines']}",
            f"- helper_count: {card['helper_count']}",
            f"- test_count: {card['test_count']}",
            f"- lanes: {', '.join(f'`{lane}`' for lane in card['lanes'])}",
            f"- latest_patch_path: `{card['latest_patch_path']}`",
            f"- latest_seed_path: `{card['latest_seed_path']}`",
            f"- latest_lane_mix: `{card['latest_lane_mix']}`",
            f"- latest_bundle_strategy: `{card['latest_bundle_strategy']}`",
            f"- apply_hint: `{card['apply_hint']}`",
        ])
        if card.get('alternate_apply_hint'):
            lines.append(f"- alternate_apply_hint: `{card['alternate_apply_hint']}`")
        lines.extend([
            f"- lane_smoke_commands: {', '.join(f'`{cmd}`' for cmd in card['lane_smoke_commands'])}",
            f"- cumulative_exact_witnesses_by_target: {', '.join(f'{target}={count}' for target, count in card['cumulative_exact_witnesses_by_target'].items())}",
            '',
            '**Run the new exact witnesses first**',
            '',
        ])
        for command in card['new_exact_witness_commands']:
            lines.append(f"- `{command}`")
        lines.extend([
            '',
            '**Then the cumulative exact witnesses for this plateau**',
            '',
        ])
        for command in card['cumulative_exact_witness_commands']:
            lines.append(f"- `{command}`")
        lines.append('')
    lines.extend([
        '## Execution recipe',
        '',
    ])
    for step in report['execution_recipe']:
        lines.append(f"{step['rank']}. {step['action']}")
        if 'command' in step:
            lines.append(f"   - `{step['command']}`")
        if 'recommended_labels' in step:
            lines.append('   - ' + ', '.join(f"`{label}`" for label in step['recommended_labels']))
        if 'plateau_apply_hints' in step:
            for label, command in step['plateau_apply_hints'].items():
                lines.append(f"   - `{label}` → `{command}`")
        if 'plateau_lane_smoke_hints' in step:
            for label, commands in step['plateau_lane_smoke_hints'].items():
                joined = ', '.join(f"`{command}`" for command in commands)
                lines.append(f"   - `{label}` → {joined}")
    lines.append('')
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
        OUT_MD.write_text(rendered, encoding='utf-8')
        print(f"rust-comeback-execution-card: wrote {OUT_JSON.relative_to(ROOT)}")
        print(f"rust-comeback-execution-card: wrote {OUT_MD.relative_to(ROOT)}")
        return 0

    if not OUT_JSON.exists() or not OUT_MD.exists():
        print('rust-comeback-execution-card: outputs missing; run with --write')
        return 1

    existing_json = OUT_JSON.read_text(encoding='utf-8')
    existing_md = OUT_MD.read_text(encoding='utf-8')
    if existing_json != current_json or existing_md != rendered:
        print('rust-comeback-execution-card: drift detected; run with --write')
        return 1

    print(
        'rust-comeback-execution-card: ok '
        f"(plateaus={report['summary']['plateau_count']} full={report['summary']['full_closure_prefix']})"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
