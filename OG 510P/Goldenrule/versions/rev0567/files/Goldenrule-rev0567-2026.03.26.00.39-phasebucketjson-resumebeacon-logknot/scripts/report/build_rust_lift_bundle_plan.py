#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from build_rust_external_test_queue import build_queue

ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rust_lift_bundle_plan.json'
OUT_MD = ROOT / 'docs' / 'RUST_LIFT_BUNDLE_PLAN.md'


def to_snake(text: str) -> str:
    cleaned = re.sub(r'[^a-zA-Z0-9]+', '_', text)
    cleaned = re.sub(r'_+', '_', cleaned).strip('_')
    if not cleaned:
        return 'seed'
    lowered = cleaned.lower()
    if lowered[0].isdigit():
        lowered = f'seed_{lowered}'
    return lowered


ASSERTION_ENUM = {
    'avg_payoff_a_at_least': 'AvgPayoffAAtLeast',
    'avg_payoff_b_at_least': 'AvgPayoffBAtLeast',
    'coop_rate_a_at_least': 'CoopRateAAtLeast',
    'coop_rate_b_at_least': 'CoopRateBAtLeast',
    'mutual_coop_rate_at_least': 'MutualCoopRateAtLeast',
    'mutual_defect_rate_at_most': 'MutualDefectRateAtMost',
}


def load_json(rel_path: str) -> object | None:
    full = ROOT / rel_path
    if not full.exists():
        return None
    try:
        return json.loads(full.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return None


def include_path_for_test(seed_path: str) -> str:
    return f'../../{seed_path}'


def helper_name(seed_path: str, example_id: str | None, probe_id: str | None) -> str:
    basis = probe_id or example_id or Path(seed_path).stem
    return f'load_{to_snake(basis)}'


def load_probe_metadata(seed_path: str) -> dict[str, object]:
    payload = load_json(seed_path)
    if not isinstance(payload, dict):
        return {
            'probe_id': None,
            'first_matchup_id': None,
            'matchup_count': 0,
            'world_id': None,
        }
    matchups = payload.get('matchups') if isinstance(payload.get('matchups'), list) else []
    first_matchup_id = None
    if matchups and isinstance(matchups[0], dict):
        first_matchup_id = matchups[0].get('id') if isinstance(matchups[0].get('id'), str) else None
    world = payload.get('world') if isinstance(payload.get('world'), dict) else {}
    return {
        'probe_id': payload.get('id') if isinstance(payload.get('id'), str) else None,
        'first_matchup_id': first_matchup_id,
        'matchup_count': len(matchups),
        'world_id': world.get('id') if isinstance(world.get('id'), str) else None,
    }


def helper_snippet(seed_path: str, helper_fn: str) -> str:
    return (
        f'fn {helper_fn}() -> ProbeSpec {{\n'
        f'    serde_json::from_str(include_str!("{include_path_for_test(seed_path)}")).unwrap()\n'
        f'}}'
    )


def probe_body_snippet(row: dict[str, object], helper_fn: str, probe_meta: dict[str, object]) -> str:
    family = str(row['family'])
    variant = str(row['variant'])
    test_name = str(row['proposed_test_name'])
    probe_id = probe_meta.get('probe_id')
    matchup_id = probe_meta.get('first_matchup_id')
    lines = [
        '#[test]',
        f'fn {test_name}() {{',
        f'    let probe = {helper_fn}();',
    ]
    if family == 'assertion_kind':
        enum_name = ASSERTION_ENUM.get(variant, 'AvgPayoffAAtLeast')
        lines.extend([
            '    let out = run_probe(&probe).unwrap();',
            '    let assertion = out',
            '        .matchups',
            '        .iter()',
            '        .flat_map(|m| m.assertions.iter())',
            f'        .find(|a| matches!(a.assertion, AssertionSpec::{enum_name} {{ .. }}))',
            f'        .expect("{variant} assertion present");',
            '    assert!(assertion.observed.is_finite());',
        ])
    elif family == 'noise_kind':
        lines.extend([
            '    let r1 = run_probe(&probe).unwrap();',
            '    let r2 = run_probe(&probe).unwrap();',
            '    assert_eq!(serde_json::to_value(&r1).unwrap(), serde_json::to_value(&r2).unwrap());',
        ])
    else:
        lines.append('    let out = run_probe(&probe).unwrap();')
        if probe_id:
            lines.append(f'    assert_eq!(out.probe_id, "{probe_id}");')
        if matchup_id:
            lines.extend([
                '    let matchup = out',
                '        .matchups',
                '        .iter()',
                f'        .find(|m| m.id == "{matchup_id}")',
                '        .expect("matchup present");',
                '    assert!(!matchup.replications_detail.is_empty());',
            ])
        else:
            lines.append('    assert!(!out.matchups.is_empty());')
    lines.append('}')
    return '\n'.join(lines)


def scaling_prefix_config(seed_path: str) -> tuple[int, int]:
    payload = load_json(seed_path)
    base_rounds = 20
    if isinstance(payload, dict):
        world = payload.get('world') if isinstance(payload.get('world'), dict) else {}
        termination = world.get('termination') if isinstance(world.get('termination'), dict) else {}
        rounds = termination.get('rounds')
        if isinstance(rounds, int) and rounds > 0:
            base_rounds = rounds
    return base_rounds, base_rounds * 3


def metamorphic_body_snippet(row: dict[str, object], helper_fn: str, seed_path: str) -> str:
    test_name = str(row['proposed_test_name'])
    check_id = f'{to_snake(test_name)}_check'
    reg_id = f'{to_snake(test_name)}_registry'
    suite_id = f'{to_snake(test_name)}_suite'
    base_rounds, extended_rounds = scaling_prefix_config(seed_path)
    return '\n'.join([
        '#[test]',
        f'fn {test_name}() {{',
        f'    let probe = {helper_fn}();',
        '    let reg = MetamorphicRegistrySpec {',
        '        schema_version: 1,',
        f'        id: "{reg_id}".to_string(),',
        '        description: "".to_string(),',
        '        checks: vec![MetamorphicCheckSpec {',
        '            schema_version: 1,',
        f'            id: "{check_id}".to_string(),',
        '            description: "".to_string(),',
        '            kind: MetamorphicKind::ScalingPrefixStability,',
        f'            scaling_prefix: Some(ScalingPrefixConfig {{ base_rounds: {base_rounds}, extended_rounds: {extended_rounds} }}),',
        '            probe,',
        '        }],',
        '    };',
        '    let suite = MetamorphicSuiteSpec {',
        '        schema_version: 1,',
        f'        id: "{suite_id}".to_string(),',
        '        description: "".to_string(),',
        f'        check_ids: vec!["{check_id}".to_string()],',
        '    };',
        '    let out = run_metamorphic_suite(&reg, &suite).unwrap();',
        '    assert!(out.passed);',
        '    assert_eq!(out.check_results.len(), 1);',
        '}',
    ])


def bundle_strategy(rows: list[dict[str, object]]) -> str:
    lanes = {str(row['target_lane']) for row in rows}
    if len(lanes) > 1:
        return 'shared_seed_dual_lane'
    if len(rows) > 1:
        return 'shared_seed_multi_row_single_lane'
    return 'single_seed_single_row'


def action_hint(rows: list[dict[str, object]], helper_fn: str) -> str:
    strategy = bundle_strategy(rows)
    if strategy == 'shared_seed_dual_lane':
        return f'keep `{helper_fn}()` lane-local in each Rust test file; reuse the same fixture path but do not force a cross-file test helper before cargo is back'
    if strategy == 'shared_seed_multi_row_single_lane':
        return f'add `{helper_fn}()` once, then hang multiple narrow tests from it so one fixture literal covers several weak rows without duplicating include_str blocks'
    return f'add `{helper_fn}()` next to the target test and keep the first lift as one narrow fixture-backed check'


def build_report() -> dict[str, object]:
    queue = build_queue()
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in queue['entries']:
        preferred = row.get('preferred_seed')
        if preferred is None:
            continue
        grouped[str(preferred['path'])].append(row)

    entries: list[dict[str, object]] = []
    lane_mix_counts = {
        'probe_run_only': 0,
        'metamorphic_suite_only': 0,
        'dual_lane': 0,
    }
    strategy_counts = {
        'single_seed_single_row': 0,
        'shared_seed_multi_row_single_lane': 0,
        'shared_seed_dual_lane': 0,
    }

    for seed_path, rows in grouped.items():
        rows = sorted(rows, key=lambda row: (str(row['target_lane']), str(row['family']), str(row['variant'])))
        preferred = rows[0]['preferred_seed']
        seed_meta = load_probe_metadata(seed_path)
        helper_fn = helper_name(seed_path, preferred.get('example_id'), seed_meta.get('probe_id'))
        lanes = sorted({str(row['target_lane']) for row in rows})
        lane_mix = 'dual_lane' if len(lanes) > 1 else ('probe_run_only' if lanes == ['probe_run'] else 'metamorphic_suite_only')
        lane_mix_counts[lane_mix] += 1
        strategy = bundle_strategy(rows)
        strategy_counts[strategy] += 1
        lane_snippets = []
        for lane in lanes:
            lane_rows = [row for row in rows if str(row['target_lane']) == lane]
            snippets = []
            for row in lane_rows:
                if lane == 'metamorphic_suite':
                    snippets.append(metamorphic_body_snippet(row, helper_fn, seed_path))
                else:
                    snippets.append(probe_body_snippet(row, helper_fn, seed_meta))
            lane_snippets.append({
                'lane': lane,
                'target_file': str(lane_rows[0]['target_test_file']),
                'test_names': [str(row['proposed_test_name']) for row in lane_rows],
                'snippets': snippets,
            })
        entries.append({
            'seed_path': seed_path,
            'seed_line': preferred['line'],
            'example_id': preferred.get('example_id'),
            'probe_id': seed_meta.get('probe_id'),
            'world_id': seed_meta.get('world_id'),
            'matchup_count': seed_meta.get('matchup_count'),
            'first_matchup_id': seed_meta.get('first_matchup_id'),
            'row_count': len(rows),
            'lanes': lanes,
            'lane_mix': lane_mix,
            'bundle_strategy': strategy,
            'shared_helper_name': helper_fn,
            'helper_snippet': helper_snippet(seed_path, helper_fn),
            'action_hint': action_hint(rows, helper_fn),
            'rows': [
                {
                    'family': row['family'],
                    'variant': row['variant'],
                    'status': row['status'],
                    'lift_band': row['lift_band'],
                    'target_lane': row['target_lane'],
                    'target_test_file': row['target_test_file'],
                    'proposed_test_name': row['proposed_test_name'],
                    'test_focus': row['test_focus'],
                }
                for row in rows
            ],
            'lane_snippets': lane_snippets,
        })

    entries.sort(key=lambda entry: (-int(entry['row_count']), 0 if entry['lane_mix'] == 'dual_lane' else 1, entry['seed_path']))
    queue_entries = len(queue['entries'])
    bundle_count = len(entries)
    return {
        'metadata': {
            'inventory_version': '2026-03-23.rust_lift_bundle_plan.v1',
            'crate': 'gr_engine',
            'source_report': 'artifacts/reports/rust_external_test_queue.json',
        },
        'summary': {
            'queue_entries': queue_entries,
            'bundle_count': bundle_count,
            'rows_saved_via_bundling': queue_entries - bundle_count,
            'multi_row_bundles': sum(1 for entry in entries if int(entry['row_count']) > 1),
            'dual_lane_bundles': sum(1 for entry in entries if entry['lane_mix'] == 'dual_lane'),
            'lane_mix_counts': lane_mix_counts,
            'bundle_strategy_counts': strategy_counts,
        },
        'entries': entries,
    }


def render_markdown(report: dict[str, object]) -> str:
    s = report['summary']
    lines = [
        '# Rust Lift Bundle Plan',
        '',
        'Generated by `scripts/report/build_rust_lift_bundle_plan.py`. This is the compact code-minded handoff that collapses the weak-scenario external-test queue into shared fixture bundles, so a later Rust-capable inheritor can add narrow tests without exploding duplicated `include_str!` blocks.',
        '',
        '## Snapshot',
        '',
        '- crate: `gr_engine`',
        f"- queue_entries: {s['queue_entries']}",
        f"- bundle_count: {s['bundle_count']}",
        f"- rows_saved_via_bundling: {s['rows_saved_via_bundling']}",
        f"- multi_row_bundles: {s['multi_row_bundles']}",
        f"- dual_lane_bundles: {s['dual_lane_bundles']}",
        f"- probe_run_only bundles: {s['lane_mix_counts']['probe_run_only']}",
        f"- metamorphic_suite_only bundles: {s['lane_mix_counts']['metamorphic_suite_only']}",
        f"- dual_lane bundles: {s['lane_mix_counts']['dual_lane']}",
        '',
        '## Bundle table',
        '',
        '| seed | rows | lane mix | helper | coverage rows |',
        '|---|---:|---|---|---|',
    ]
    for entry in report['entries']:
        coverage = ', '.join(f"`{row['variant']}`" for row in entry['rows'])
        lines.append(
            f"| `{entry['seed_path']}` | {entry['row_count']} | `{entry['lane_mix']}` | `{entry['shared_helper_name']}` | {coverage} |"
        )
    lines.extend(['', '## Bundles', ''])
    for entry in report['entries']:
        lines.extend([
            f"### `{entry['seed_path']}`",
            '',
            f"- example_id: `{entry['example_id'] or '—'}`",
            f"- probe_id: `{entry['probe_id'] or '—'}`",
            f"- world_id: `{entry['world_id'] or '—'}`",
            f"- row_count: {entry['row_count']}",
            f"- lane_mix: `{entry['lane_mix']}`",
            f"- bundle_strategy: `{entry['bundle_strategy']}`",
            f"- first_matchup_id: `{entry['first_matchup_id'] or '—'}`",
            f"- action_hint: {entry['action_hint']}",
            '',
            'Coverage rows:',
            '',
        ])
        for row in entry['rows']:
            lines.append(
                f"- `{row['family']}` / `{row['variant']}` → `{row['proposed_test_name']}` in `{row['target_test_file']}` ({row['lift_band']})"
            )
        lines.extend([
            '',
            'Shared helper:',
            '',
            '```rust',
            entry['helper_snippet'],
            '```',
            '',
        ])
        for lane_block in entry['lane_snippets']:
            lines.extend([
                f"Lane `{lane_block['lane']}` → `{lane_block['target_file']}`",
                '',
            ])
            for snippet in lane_block['snippets']:
                lines.extend([
                    '```rust',
                    snippet,
                    '```',
                    '',
                ])
    return '\n'.join(lines).rstrip() + '\n'


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Bundle the Rust external-test lift queue into shared fixture/code bundles.')
    parser.add_argument('--write', action='store_true', help='write outputs instead of diff-checking them')
    args = parser.parse_args(argv)

    report = build_report()
    js = json.dumps(report, indent=2, sort_keys=True) + '\n'
    md = render_markdown(report)

    if args.write:
        OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        OUT_MD.parent.mkdir(parents=True, exist_ok=True)
        OUT_JSON.write_text(js, encoding='utf-8')
        OUT_MD.write_text(md, encoding='utf-8')
        print(f'rust-lift-bundle-plan: wrote {OUT_JSON.relative_to(ROOT)}')
        print(f'rust-lift-bundle-plan: wrote {OUT_MD.relative_to(ROOT)}')
        return 0

    missing = []
    if not OUT_JSON.exists():
        missing.append(OUT_JSON.relative_to(ROOT).as_posix())
    if not OUT_MD.exists():
        missing.append(OUT_MD.relative_to(ROOT).as_posix())
    if missing:
        for item in missing:
            print(f'rust-lift-bundle-plan: missing {item}', file=sys.stderr)
        return 1

    if OUT_JSON.read_text(encoding='utf-8') != js or OUT_MD.read_text(encoding='utf-8') != md:
        print('rust-lift-bundle-plan: outputs are stale; run with --write', file=sys.stderr)
        return 1

    print(
        'rust-lift-bundle-plan: ok '
        f"({report['summary']['bundle_count']} bundles, {report['summary']['rows_saved_via_bundling']} duplicated rows collapsed)"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
