#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
FRONTIER_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_frontier_snapshot.py'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_transition_budget_snapshot_20260307.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_transition_budget_snapshot_20260307.md'
FOCAL_EXPECTED_REPEAT_LOOKUPS = 0.18
MAX_UNIQUE_APPENDS = 256
REFERENCE_MAX_TRANSITION_COUNTS = [0, 1, 2, 3, 4, 5, 12, 256]


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module



def _interval_summary(interval_rows: list[dict[str, object]]) -> str:
    kind_labels = {
        'paged_catalog_only': 'pages',
        'paged_catalog_with_filters': 'filters',
        'paged_catalog_with_route_blocks': 'route-blocks',
    }
    return '; '.join(
        f"{kind_labels[row['recommended_state_kind']]} {row['start_unique_appends']}–{row['end_unique_appends']}"
        for row in interval_rows
    )



def _share(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 6)



def _build_summary() -> dict[str, object]:
    packet = _load_module(PACKET_PATH, 'rematch_proxy_delta_decision_packet')
    frontier_builder = _load_module(FRONTIER_BUILDER_PATH, 'frontier_snapshot')
    deterministic_packets = frontier_builder._frontier_test_packets(packet)
    fingerprints = [packet.packet_semantic_fingerprint(row['packet']) for row in deterministic_packets]
    pages = packet.fingerprint_catalog_pages(fingerprints, page_size=packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE)
    horizon_metrics = packet.fingerprint_catalog_compact_repeat_state_horizon_metrics(
        pages,
        max_unique_appends=MAX_UNIQUE_APPENDS,
        page_size=packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
    )
    frontier = packet.fingerprint_catalog_compact_repeat_state_transition_budget_frontier_from_metrics(
        horizon_metrics,
        expected_repeat_lookups=FOCAL_EXPECTED_REPEAT_LOOKUPS,
    )
    frontier_rows = []
    fixed_route_blocks_cost = frontier['frontier_rows'][0]['cumulative_objective_without_transition_penalty']
    full_dynamic_cost = frontier['dynamic_cumulative_objective_without_transition_penalty']
    full_dynamic_gain = round(fixed_route_blocks_cost - full_dynamic_cost, 6)
    for row in frontier['frontier_rows']:
        cumulative_gain_vs_fixed_route_blocks = round(
            fixed_route_blocks_cost - row['cumulative_objective_without_transition_penalty'],
            6,
        )
        frontier_rows.append({
            'budget_start_transition_count': row['budget_start_transition_count'],
            'budget_end_transition_count': row['budget_end_transition_count'],
            'selected_transition_count': row['selected_transition_count'],
            'cumulative_objective_without_transition_penalty': row['cumulative_objective_without_transition_penalty'],
            'objective_improvement_vs_previous_budget': row['objective_improvement_vs_previous_budget'],
            'regret_vs_unbounded_dynamic': row['regret_vs_unbounded_dynamic'],
            'cumulative_gain_vs_fixed_route_blocks': cumulative_gain_vs_fixed_route_blocks,
            'gain_share_of_full_dynamic_savings': _share(cumulative_gain_vs_fixed_route_blocks, full_dynamic_gain),
            'state_counts': row['state_counts'],
            'interval_summary': _interval_summary(row['interval_rows']),
        })

    reference_budget_rows = []
    for max_transition_count in REFERENCE_MAX_TRANSITION_COUNTS:
        plan = packet.recommend_fingerprint_catalog_compact_repeat_state_horizon_policy_with_transition_budget_from_metrics(
            horizon_metrics,
            expected_repeat_lookups=FOCAL_EXPECTED_REPEAT_LOOKUPS,
            max_transition_count=max_transition_count,
        )
        reference_budget_rows.append({
            'max_transition_count': max_transition_count,
            'effective_max_transition_count': plan['effective_max_transition_count'],
            'selected_transition_count': plan['selected_transition_count'],
            'cumulative_objective_without_transition_penalty': plan['cumulative_objective_without_transition_penalty'],
            'regret_vs_unbounded_dynamic': plan['regret_vs_unbounded_dynamic'],
            'objective_improvement_vs_previous_budget': plan['objective_improvement_vs_previous_budget'],
            'recommended_state_counts': plan['recommended_state_counts'],
            'interval_summary': _interval_summary(plan['interval_rows']),
        })

    row_by_budget = {row['budget_start_transition_count']: row for row in frontier_rows}
    return {
        'focus': 'Choose compact repeat-sidecar schedules by an explicit rewrite-count budget so the archive can spend a few sidecar transitions on the biggest savings first.',
        'packet_script': str(PACKET_PATH.relative_to(ROOT)),
        'deterministic_frontier_packet_count': len(deterministic_packets),
        'default_page_size': packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
        'max_unique_appends': MAX_UNIQUE_APPENDS,
        'focal_expected_repeat_lookups': FOCAL_EXPECTED_REPEAT_LOOKUPS,
        'reference_max_transition_counts': REFERENCE_MAX_TRANSITION_COUNTS,
        'headline_findings': {
            'entry_count': frontier['entry_count'],
            'page_count': frontier['page_count'],
            'tail_entry_count': frontier['tail_entry_count'],
            'route_block_bitmap_len': frontier['route_block_bitmap_len'],
            'dynamic_transition_count': frontier['dynamic_transition_count'],
            'dynamic_cumulative_objective_without_transition_penalty': frontier['dynamic_cumulative_objective_without_transition_penalty'],
            'full_dynamic_gain_vs_fixed_route_blocks': full_dynamic_gain,
            'first_switch_gain_vs_fixed_route_blocks_bytes': row_by_budget[1]['objective_improvement_vs_previous_budget'],
            'third_switch_gain_vs_second_budget_bytes': row_by_budget[3]['objective_improvement_vs_previous_budget'],
            'first_four_switch_gain_share_of_full_dynamic_savings': row_by_budget[4]['gain_share_of_full_dynamic_savings'],
            'fifth_switch_gain_bytes': row_by_budget[5]['objective_improvement_vs_previous_budget'],
            'sixth_switch_gain_bytes': row_by_budget[6]['objective_improvement_vs_previous_budget'],
            'practical_transition_budget_ceiling': 4,
            'main_rule': 'when rewrite count is the real constraint, spend the first few sidecar transitions on the big structural bands first and stop before the single-step cliff fallbacks unless those last bytes matter.',
        },
        'frontier_rows': frontier_rows,
        'reference_budget_rows': reference_budget_rows,
        'source_script': str(Path(__file__).relative_to(ROOT)),
        'sources': [
            str(PACKET_PATH.relative_to(ROOT)),
            str(FRONTIER_BUILDER_PATH.relative_to(ROOT)),
        ],
    }



def _render_md(report: dict[str, object]) -> str:
    findings = report['headline_findings']
    lines = [
        '# Rematch Proxy Delta Decision Packet Compact Repeat-State Transition-Budget Snapshot — 2026-03-07',
        '',
        '## Focus',
        f"- {report['focus']}",
        '',
        '## Headline findings',
        f"- packet script: `{report['packet_script']}`.",
        f"- deterministic frontier packet count: `{report['deterministic_frontier_packet_count']}`.",
        f"- live compact catalog starts at `{findings['entry_count']}` fingerprints across `{findings['page_count']}` pages with tail count `{findings['tail_entry_count']}` and route-block bitmap width `{findings['route_block_bitmap_len']}` bytes.",
        f"- at `{report['focal_expected_repeat_lookups']}` expected repeats over the next `{report['max_unique_appends']}` novel appends, the unbounded dynamic optimum uses `{findings['dynamic_transition_count']}` sidecar transitions.",
        f"- the first allowed rewrite is worth `{findings['first_switch_gain_vs_fixed_route_blocks_bytes']}` bytes versus fixed route blocks.",
        f"- the third allowed rewrite is still highly structural: it buys `{findings['third_switch_gain_vs_second_budget_bytes']}` bytes beyond the two-transition plan.",
        f"- the first four allowed rewrites already capture `{findings['first_four_switch_gain_share_of_full_dynamic_savings']}` of the full dynamic savings against fixed route blocks.",
        f"- after that, returns collapse: the fifth rewrite buys only `{findings['fifth_switch_gain_bytes']}` bytes and the sixth only `{findings['sixth_switch_gain_bytes']}`.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Exact transition-budget frontier',
        '| max transitions | selected transitions | cumulative objective | gain vs fixed route blocks | gain share of full dynamic savings | marginal gain vs prior budget | regret vs unbounded dynamic | summary |',
        '|---:|---:|---:|---:|---:|---:|---:|---|',
    ]
    for row in report['frontier_rows']:
        budget_label = (
            f"{row['budget_start_transition_count']}–{row['budget_end_transition_count']}"
            if row['budget_start_transition_count'] != row['budget_end_transition_count']
            else str(row['budget_start_transition_count'])
        )
        lines.append(
            f"| {budget_label} | {row['selected_transition_count']} | {row['cumulative_objective_without_transition_penalty']} | {row['cumulative_gain_vs_fixed_route_blocks']} | {row['gain_share_of_full_dynamic_savings']} | {row['objective_improvement_vs_previous_budget']} | {row['regret_vs_unbounded_dynamic']} | {row['interval_summary']} |"
        )
    lines.extend([
        '',
        '## Reference max-transition budgets',
        '| max transitions | selected transitions | cumulative objective | regret vs unbounded dynamic | marginal gain vs prior budget | state counts | summary |',
        '|---:|---:|---:|---:|---:|---|---|',
    ])
    for row in report['reference_budget_rows']:
        lines.append(
            f"| {row['max_transition_count']} | {row['selected_transition_count']} | {row['cumulative_objective_without_transition_penalty']} | {row['regret_vs_unbounded_dynamic']} | {row['objective_improvement_vs_previous_budget']} | `{row['recommended_state_counts']}` | {row['interval_summary']} |"
        )
    lines.extend([
        '',
        '## Sources',
        '- `scripts/analysis/rematch_proxy_delta_decision_packet.py`',
        '- `scripts/report/build_rematch_proxy_delta_decision_packet_frontier_snapshot.py`',
    ])
    return '\n'.join(lines) + '\n'



def main() -> None:
    report = _build_summary()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    OUT_MD.write_text(_render_md(report))
    print(f'wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'wrote {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
