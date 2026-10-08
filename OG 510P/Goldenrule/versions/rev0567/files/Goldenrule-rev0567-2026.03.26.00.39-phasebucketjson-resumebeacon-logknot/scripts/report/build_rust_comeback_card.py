#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
QUEUE_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_external_test_queue.json'
SEED_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_seed_loader_readiness.json'
BUNDLE_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_lift_bundle_plan.json'
PATCHSET_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_external_test_patchset.json'
PATCH_SHARDS_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_external_test_patch_shards.json'
PATCH_REHEARSAL_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_external_test_patch_rehearsal.json'
PREFIX_FRONTIER_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_patch_prefix_frontier.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rust_comeback_card.json'
OUT_MD = ROOT / 'docs' / 'RUST_COMEBACK_CARD.md'


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


def _milestone_card(
    *,
    label: str,
    rationale: str,
    prefix_index: int,
    prefixes_by_index: dict[int, dict[str, Any]],
    shard_entries: list[dict[str, Any]],
) -> dict[str, Any]:
    prefix = prefixes_by_index[prefix_index]
    cumulative = prefix['cumulative']
    shard_slice = shard_entries[:prefix_index]
    cargo_hints = _unique(
        [hint for entry in shard_slice for hint in entry.get('future_cargo_hints') or []]
    )
    return {
        'label': label,
        'prefix_index': int(prefix_index),
        'rationale': rationale,
        'rows_covered': int(cumulative['rows_covered']),
        'rows_remaining': int(cumulative['rows_remaining']),
        'rows_coverage_fraction': _round(cumulative['rows_coverage_fraction']),
        'added_lines': int(cumulative['added_lines']),
        'helper_count': int(cumulative['helper_count']),
        'test_count': int(cumulative['test_count']),
        'lane_count': int(cumulative['lane_count']),
        'lanes': list(cumulative['lanes']),
        'lift_band_counts': dict(cumulative['lift_band_counts']),
        'target_files': list(cumulative['target_files']),
        'target_file_count': int(cumulative['target_file_count']),
        'latest_patch_path': str(prefix['latest_patch_path']),
        'latest_seed_path': str(prefix['latest_seed_path']),
        'latest_lane_mix': str(prefix['latest_lane_mix']),
        'latest_bundle_strategy': str(prefix['latest_bundle_strategy']),
        'marginal_new_rows': int(prefix['marginal_new_rows']),
        'marginal_rows_per_added_line': _round(prefix['marginal_rows_per_added_line']),
        'milestones_hit': list(prefix['milestones_hit']),
        'cumulative_apply_hint': _cumulative_apply_hint(shard_slice),
        'cargo_hint_count': len(cargo_hints),
        'cargo_hints_sample': cargo_hints[:4],
    }


def build_report() -> dict[str, Any]:
    queue = _load(QUEUE_REPORT)
    seed = _load(SEED_REPORT)
    bundle = _load(BUNDLE_REPORT)
    patchset = _load(PATCHSET_REPORT)
    shards = _load(PATCH_SHARDS_REPORT)
    rehearsal = _load(PATCH_REHEARSAL_REPORT)
    frontier = _load(PREFIX_FRONTIER_REPORT)

    shard_entries = list(shards.get('entries') or [])
    prefixes_by_index = {int(entry['prefix_index']): entry for entry in frontier.get('prefixes') or []}
    stop_points = {str(entry['label']): entry for entry in frontier.get('stop_points') or []}
    milestones = {str(entry['label']): entry for entry in frontier.get('milestones') or []}

    direct_probe_ready = int(seed['summary']['direct_probe_ready'])
    total_queue_rows = int(queue['summary']['queue_entries'])
    shard_count = len(shard_entries)
    full_closure_prefix = int(frontier['summary']['full_closure_prefix'])
    final_shard = shard_entries[-1]

    milestone_cards = [
        _milestone_card(
            label='quick_foothold',
            rationale=str(stop_points['quick_foothold']['why_stop_here']),
            prefix_index=int(stop_points['quick_foothold']['prefix_index']),
            prefixes_by_index=prefixes_by_index,
            shard_entries=shard_entries,
        ),
        _milestone_card(
            label='lift_first_closure',
            rationale=str(stop_points['lift_first_closure']['why_stop_here']),
            prefix_index=int(stop_points['lift_first_closure']['prefix_index']),
            prefixes_by_index=prefixes_by_index,
            shard_entries=shard_entries,
        ),
        _milestone_card(
            label='first_externalize_now',
            rationale=str(milestones['first_externalize_now']['rationale']),
            prefix_index=int(milestones['first_externalize_now']['prefix_index']),
            prefixes_by_index=prefixes_by_index,
            shard_entries=shard_entries,
        ),
        _milestone_card(
            label='full_closure',
            rationale=str(stop_points['full_closure']['why_stop_here']),
            prefix_index=full_closure_prefix,
            prefixes_by_index=prefixes_by_index,
            shard_entries=shard_entries,
        ),
    ]

    headline_findings = [
        (
            f"All {direct_probe_ready} current weak-row comeback entries are direct `ProbeSpec` loads, so the future Rust lane does not have to "
            f"spend its first pass on wrapper/template translation before adding tests."
        ),
        (
            f"The comeback surface is smaller than the raw queue implies: {bundle['summary']['queue_entries']} queue rows collapse into "
            f"{bundle['summary']['bundle_count']} generated bundles, saving {bundle['summary']['rows_saved_via_bundling']} repeated rows."
        ),
        (
            f"The clean first plateau is still shard prefix {frontier['summary']['all_lift_first_prefix']}: it lands every `lift_first` row "
            f"in {stop_points['lift_first_closure']['added_lines']} added lines without touching the final dual-lane shard."
        ),
        (
            f"Shard prefix {frontier['summary']['first_externalize_now_prefix']} is the first point that reaches any `externalize_now` row and also "
            f"the best marginal value prefix at {frontier['summary']['best_marginal_rows_per_added_line']} rows per added line."
        ),
        (
            f"The monolithic patch and the 10-shard cumulative series were rehearsal-applied to scratch copies and finished with identical target-file "
            f"states (`final_state_equivalent={rehearsal['summary']['final_state_equivalent']}`)."
        ),
    ]

    landing_recipe = [
        {
            'rank': 1,
            'action': 'Start from a clean branch/worktree on a real Rust-capable machine and refresh the static reports before editing tests.',
            'command': 'make update-rust-comeback-card',
        },
        {
            'rank': 2,
            'action': 'For the smallest proving move, apply only shard 01 and run the exact witness test it introduces.',
            'command': milestone_cards[0]['cumulative_apply_hint'],
            'followup': milestone_cards[0]['cargo_hints_sample'][:1],
        },
        {
            'rank': 3,
            'action': 'For the cleanest first closure, stop after shard prefix 06 so every `lift_first` row has landed.',
            'command': milestone_cards[1]['cumulative_apply_hint'],
            'followup': milestone_cards[1]['cargo_hints_sample'][:3],
        },
        {
            'rank': 4,
            'action': 'If you need the first `externalize_now` witness, continue through shard prefix 07 rather than jumping straight to the full patch.',
            'command': milestone_cards[2]['cumulative_apply_hint'],
            'followup': milestone_cards[2]['cargo_hints_sample'][:3],
        },
        {
            'rank': 5,
            'action': 'For full queue closure, either apply all 10 shards in order or use the monolithic patch once.',
            'command': milestone_cards[3]['cumulative_apply_hint'],
            'alternate_command': str(patchset['patch']['apply_hint']),
            'followup': milestone_cards[3]['cargo_hints_sample'][:4],
        },
        {
            'rank': 6,
            'action': 'Do not front-load the dual-lane metamorphic work: it is isolated to the final shard, so you can hold it back until the probe-only lane is green.',
            'command': f"git apply {final_shard['patch_path']}",
        },
    ]

    return {
        'metadata': {
            'inventory_version': 1,
            'source_reports': [
                QUEUE_REPORT.relative_to(ROOT).as_posix(),
                SEED_REPORT.relative_to(ROOT).as_posix(),
                BUNDLE_REPORT.relative_to(ROOT).as_posix(),
                PATCHSET_REPORT.relative_to(ROOT).as_posix(),
                PATCH_SHARDS_REPORT.relative_to(ROOT).as_posix(),
                PATCH_REHEARSAL_REPORT.relative_to(ROOT).as_posix(),
                PREFIX_FRONTIER_REPORT.relative_to(ROOT).as_posix(),
            ],
        },
        'summary': {
            'total_queue_rows': total_queue_rows,
            'direct_probe_ready_rows': direct_probe_ready,
            'direct_probe_ready_fraction': _round(direct_probe_ready / max(1, total_queue_rows)),
            'bundle_count': int(bundle['summary']['bundle_count']),
            'rows_saved_via_bundling': int(bundle['summary']['rows_saved_via_bundling']),
            'shard_count': shard_count,
            'full_closure_prefix': full_closure_prefix,
            'lift_first_closure_prefix': int(frontier['summary']['all_lift_first_prefix']),
            'first_externalize_now_prefix': int(frontier['summary']['first_externalize_now_prefix']),
            'best_marginal_prefix': int(frontier['summary']['best_marginal_prefix']),
            'best_marginal_rows_per_added_line': _round(frontier['summary']['best_marginal_rows_per_added_line']),
            'monolithic_patch_added_lines': int(patchset['summary']['added_lines']),
            'monolithic_patch_hunks': int(patchset['summary']['patch_hunks']),
            'monolithic_patch_apply_hint': str(patchset['patch']['apply_hint']),
            'final_state_equivalent': bool(rehearsal['summary']['final_state_equivalent']),
            'monolithic_apply_ok': bool(rehearsal['summary']['monolithic_apply_ok']),
            'shard_series_apply_ok': bool(rehearsal['summary']['shard_series_apply_ok']),
            'dual_lane_final_shard_index': int(final_shard['series_index']),
            'dual_lane_final_shard_path': str(final_shard['patch_path']),
        },
        'milestone_cards': milestone_cards,
        'landing_recipe': landing_recipe,
        'headline_findings': headline_findings,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report['summary']
    lines = [
        '# Rust Comeback Card',
        '',
        'Generated by `scripts/report/build_rust_comeback_card.py`. This fuses the external-test queue, seed-loader audit, lift bundle plan, patchset/shard reports, patch rehearsal, and prefix frontier into one landing-order card for the first Rust-capable inheritor.',
        '',
        '## Summary',
        '',
        f"- queue rows: `{summary['total_queue_rows']}`",
        f"- direct probe-ready rows: `{summary['direct_probe_ready_rows']}` / `{summary['total_queue_rows']}` (`{summary['direct_probe_ready_fraction']}`)",
        f"- generated bundles: `{summary['bundle_count']}` (rows saved via bundling `{summary['rows_saved_via_bundling']}`)",
        f"- cumulative shard count: `{summary['shard_count']}`",
        f"- key prefixes: lift-first closure `{summary['lift_first_closure_prefix']}`, first externalize-now `{summary['first_externalize_now_prefix']}`, full closure `{summary['full_closure_prefix']}`",
        f"- monolithic patch: `{summary['monolithic_patch_added_lines']}` added lines across `{summary['monolithic_patch_hunks']}` hunks via `{summary['monolithic_patch_apply_hint']}`",
        f"- rehearsal equivalence: `final_state_equivalent={summary['final_state_equivalent']}` / `monolithic_apply_ok={summary['monolithic_apply_ok']}` / `shard_series_apply_ok={summary['shard_series_apply_ok']}`",
        f"- deferred dual-lane shard: prefix `{summary['dual_lane_final_shard_index']}` / `{summary['dual_lane_final_shard_path']}`",
        '',
        '## Headline findings',
        '',
    ]
    for item in report['headline_findings']:
        lines.append(f'- {item}')

    lines.extend([
        '',
        '## Milestone cards',
        '',
        '| milestone | prefix | rows covered | rows remaining | added lines | lanes | latest patch |',
        '|---|---:|---:|---:|---:|---|---|',
    ])
    for card in report['milestone_cards']:
        lines.append(
            f"| `{card['label']}` | {card['prefix_index']} | {card['rows_covered']} | {card['rows_remaining']} | {card['added_lines']} | `{','.join(card['lanes'])}` | `{card['latest_patch_path']}` |"
        )

    lines.extend([
        '',
        '## Per-milestone notes',
        '',
    ])
    for card in report['milestone_cards']:
        lines.extend([
            f"### {card['label']}",
            '',
            f"- rationale: {card['rationale']}",
            f"- cumulative shard apply hint: `{card['cumulative_apply_hint']}`",
            f"- coverage: `{card['rows_covered']}` rows landed, `{card['rows_remaining']}` remaining (`{card['rows_coverage_fraction']}` of queue)",
            f"- code surface: `{card['added_lines']}` added lines, `{card['helper_count']}` helpers, `{card['test_count']}` tests, `{card['target_file_count']}` target files",
            f"- latest shard: `{card['latest_patch_path']}` from `{card['latest_seed_path']}`",
            f"- lane mix: `{card['latest_lane_mix']}` via `{card['latest_bundle_strategy']}`",
            f"- marginal efficiency at this boundary: `{card['marginal_new_rows']}` new rows for `{card['marginal_rows_per_added_line']}` rows-per-line",
            f"- cargo hint sample count: `{card['cargo_hint_count']}`",
        ])
        if card['cargo_hints_sample']:
            lines.append(f"- cargo hint sample: `{card['cargo_hints_sample'][0]}`")
            for hint in card['cargo_hints_sample'][1:]:
                lines.append(f"  - `{hint}`")
        lines.append('')

    lines.extend([
        '## Landing recipe',
        '',
    ])
    for row in report['landing_recipe']:
        lines.append(f"{row['rank']}. {row['action']} Command: `{row['command']}`.")
        if row.get('alternate_command'):
            lines.append(f"   Alternate: `{row['alternate_command']}`.")
        for hint in row.get('followup') or []:
            lines.append(f"   Follow with: `{hint}`.")

    lines.extend([
        '',
        '## Why this card exists',
        '',
        'The archive already had the queue, bundle plan, patch series, rehearsal proof, and prefix frontier, but the first Rust-capable inheritor still had to reopen several neighboring generated docs to answer one simple operational question: what is the cleanest first landing order once Cargo exists again? This card keeps that answer compact and citation-first inside the archive.',
        '',
    ])
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description='Build the Rust comeback card.')
    parser.add_argument('--write', action='store_true', help='Write the markdown report.')
    args = parser.parse_args()

    report = build_report()
    rendered = render_markdown(report)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')

    if args.write or not OUT_MD.exists():
        OUT_MD.write_text(rendered, encoding='utf-8')
        print(f"rust-comeback-card: wrote {OUT_MD}")
        print(f"rust-comeback-card: wrote {OUT_JSON}")
        return 0

    current = OUT_MD.read_text(encoding='utf-8')
    if current != rendered:
        print('rust-comeback-card: drift detected; run with --write')
        return 1

    print(
        'rust-comeback-card: ok '
        f"(rows={report['summary']['total_queue_rows']} full_prefix={report['summary']['full_closure_prefix']} shards={report['summary']['shard_count']})"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
