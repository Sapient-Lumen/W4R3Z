#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
TRANSITION_BUDGET_REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_transition_budget_snapshot_20260307.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_snapshot_20260307.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_snapshot_20260307.md'


def _build_summary() -> dict[str, object]:
    return {
        'focus': 'Choose compact repeat-sidecar schedules by a minimum regime dwell length so the archive can kill cliff toggles and other short-lived rewrites with one simple online rule.',
        'packet_script': str(PACKET_PATH.relative_to(ROOT)),
        'deterministic_frontier_packet_count': 274,
        'default_page_size': 16,
        'max_unique_appends': 256,
        'focal_expected_repeat_lookups': 0.18,
        'reference_minimum_dwell_unique_appends': [1, 2, 7, 8, 19, 49, 57, 256],
        'headline_findings': {
            'entry_count': 274,
            'page_count': 18,
            'tail_entry_count': 2,
            'route_block_bitmap_len': 3,
            'dynamic_transition_count': 12,
            'dynamic_cumulative_objective_without_transition_penalty': 4828958.842787,
            'frontier_regime_count': 7,
            'min_dwell_two_suppresses_one_step_cliffs_transition_count': 11,
            'min_dwell_eight_transition_count': 5,
            'min_dwell_eight_regret_vs_unbounded_dynamic': 217.295277,
            'min_dwell_eight_gain_share_of_full_dynamic_savings': 0.980481,
            'min_dwell_nineteen_transition_count': 3,
            'min_dwell_nineteen_gain_share_of_full_dynamic_savings': 0.870482,
            'min_dwell_forty_nine_transition_count': 1,
            'min_dwell_forty_nine_gain_share_of_full_dynamic_savings': 0.510201,
            'route_blocks_only_threshold_minimum_dwell_unique_appends': 57,
            'practical_default_minimum_dwell_unique_appends': 8,
            'main_rule': 'set a minimum dwell length first; eight novel appends is the current sweet spot because it kills the short cliff oscillations while preserving almost all of the dynamic savings.',
        },
        'frontier_rows': [
            {
                'minimum_dwell_start_unique_appends': 1,
                'minimum_dwell_end_unique_appends': 1,
                'selected_transition_count': 12,
                'minimum_interval_dwell_unique_appends': 1,
                'cumulative_objective_without_transition_penalty': 4828958.842787,
                'regret_vs_unbounded_dynamic': 0.0,
                'cumulative_gain_vs_fixed_route_blocks': 11132.231038,
                'gain_share_of_full_dynamic_savings': 1.0,
                'state_counts': {
                    'paged_catalog_only': 33,
                    'paged_catalog_with_filters': 96,
                    'paged_catalog_with_route_blocks': 128,
                },
                'interval_summary': 'pages 0–8; filters 9–14; pages 15–23; filters 24–30; pages 31–37; filters 38–46; pages 47–53; filters 54–62; route-blocks 63–110; pages 111–111; filters 112–158; route-blocks 159–238; filters 239–256',
            },
            {
                'minimum_dwell_start_unique_appends': 2,
                'minimum_dwell_end_unique_appends': 6,
                'selected_transition_count': 11,
                'minimum_interval_dwell_unique_appends': 6,
                'cumulative_objective_without_transition_penalty': 4828960.822216,
                'regret_vs_unbounded_dynamic': 1.979429,
                'cumulative_gain_vs_fixed_route_blocks': 11130.251609,
                'gain_share_of_full_dynamic_savings': 0.999822,
                'state_counts': {
                    'paged_catalog_only': 32,
                    'paged_catalog_with_filters': 97,
                    'paged_catalog_with_route_blocks': 128,
                },
                'interval_summary': 'pages 0–8; filters 9–14; pages 15–23; filters 24–30; pages 31–37; filters 38–46; pages 47–53; filters 54–62; route-blocks 63–110; filters 111–158; route-blocks 159–238; filters 239–256',
            },
            {
                'minimum_dwell_start_unique_appends': 7,
                'minimum_dwell_end_unique_appends': 7,
                'selected_transition_count': 9,
                'minimum_interval_dwell_unique_appends': 7,
                'cumulative_objective_without_transition_penalty': 4829017.138691,
                'regret_vs_unbounded_dynamic': 58.295904,
                'cumulative_gain_vs_fixed_route_blocks': 11073.935134,
                'gain_share_of_full_dynamic_savings': 0.994763,
                'state_counts': {
                    'paged_catalog_only': 24,
                    'paged_catalog_with_filters': 115,
                    'paged_catalog_with_route_blocks': 118,
                },
                'interval_summary': 'pages 0–23; filters 24–30; pages 31–37; filters 38–46; pages 47–53; filters 54–62; route-blocks 63–110; filters 111–158; route-blocks 159–238; filters 239–256',
            },
            {
                'minimum_dwell_start_unique_appends': 8,
                'minimum_dwell_end_unique_appends': 18,
                'selected_transition_count': 5,
                'minimum_interval_dwell_unique_appends': 18,
                'cumulative_objective_without_transition_penalty': 4829176.138064,
                'regret_vs_unbounded_dynamic': 217.295277,
                'cumulative_gain_vs_fixed_route_blocks': 10914.935761,
                'gain_share_of_full_dynamic_savings': 0.980481,
                'state_counts': {
                    'paged_catalog_only': 24,
                    'paged_catalog_with_filters': 115,
                    'paged_catalog_with_route_blocks': 118,
                },
                'interval_summary': 'pages 0–23; filters 24–62; route-blocks 63–110; filters 111–158; route-blocks 159–238; filters 239–256',
            },
            {
                'minimum_dwell_start_unique_appends': 19,
                'minimum_dwell_end_unique_appends': 48,
                'selected_transition_count': 3,
                'minimum_interval_dwell_unique_appends': 48,
                'cumulative_objective_without_transition_penalty': 4830400.669232,
                'regret_vs_unbounded_dynamic': 1441.826445,
                'cumulative_gain_vs_fixed_route_blocks': 9690.404593,
                'gain_share_of_full_dynamic_savings': 0.870482,
                'state_counts': {
                    'paged_catalog_only': 56,
                    'paged_catalog_with_filters': 48,
                    'paged_catalog_with_route_blocks': 153,
                },
                'interval_summary': 'pages 0–55; route-blocks 56–110; filters 111–158; route-blocks 159–256',
            },
            {
                'minimum_dwell_start_unique_appends': 49,
                'minimum_dwell_end_unique_appends': 56,
                'selected_transition_count': 1,
                'minimum_interval_dwell_unique_appends': 56,
                'cumulative_objective_without_transition_penalty': 4834411.397743,
                'regret_vs_unbounded_dynamic': 5452.554956,
                'cumulative_gain_vs_fixed_route_blocks': 5679.676082,
                'gain_share_of_full_dynamic_savings': 0.510201,
                'state_counts': {
                    'paged_catalog_only': 56,
                    'paged_catalog_with_filters': 0,
                    'paged_catalog_with_route_blocks': 201,
                },
                'interval_summary': 'pages 0–55; route-blocks 56–256',
            },
            {
                'minimum_dwell_start_unique_appends': 57,
                'minimum_dwell_end_unique_appends': 257,
                'selected_transition_count': 0,
                'minimum_interval_dwell_unique_appends': 257,
                'cumulative_objective_without_transition_penalty': 4840091.073825,
                'regret_vs_unbounded_dynamic': 11132.231038,
                'cumulative_gain_vs_fixed_route_blocks': 0.0,
                'gain_share_of_full_dynamic_savings': 0.0,
                'state_counts': {
                    'paged_catalog_only': 0,
                    'paged_catalog_with_filters': 0,
                    'paged_catalog_with_route_blocks': 257,
                },
                'interval_summary': 'route-blocks 0–256',
            },
        ],
        'reference_rows': [
            {
                'minimum_dwell_unique_appends': 1,
                'effective_minimum_dwell_unique_appends': 1,
                'selected_transition_count': 12,
                'minimum_interval_dwell_unique_appends': 1,
                'cumulative_objective_without_transition_penalty': 4828958.842787,
                'regret_vs_unbounded_dynamic': 0.0,
                'recommended_state_counts': {
                    'paged_catalog_only': 33,
                    'paged_catalog_with_filters': 96,
                    'paged_catalog_with_route_blocks': 128,
                },
                'interval_summary': 'pages 0–8; filters 9–14; pages 15–23; filters 24–30; pages 31–37; filters 38–46; pages 47–53; filters 54–62; route-blocks 63–110; pages 111–111; filters 112–158; route-blocks 159–238; filters 239–256',
            },
            {
                'minimum_dwell_unique_appends': 2,
                'effective_minimum_dwell_unique_appends': 2,
                'selected_transition_count': 11,
                'minimum_interval_dwell_unique_appends': 6,
                'cumulative_objective_without_transition_penalty': 4828960.822216,
                'regret_vs_unbounded_dynamic': 1.979429,
                'recommended_state_counts': {
                    'paged_catalog_only': 32,
                    'paged_catalog_with_filters': 97,
                    'paged_catalog_with_route_blocks': 128,
                },
                'interval_summary': 'pages 0–8; filters 9–14; pages 15–23; filters 24–30; pages 31–37; filters 38–46; pages 47–53; filters 54–62; route-blocks 63–110; filters 111–158; route-blocks 159–238; filters 239–256',
            },
            {
                'minimum_dwell_unique_appends': 7,
                'effective_minimum_dwell_unique_appends': 7,
                'selected_transition_count': 9,
                'minimum_interval_dwell_unique_appends': 7,
                'cumulative_objective_without_transition_penalty': 4829017.138691,
                'regret_vs_unbounded_dynamic': 58.295904,
                'recommended_state_counts': {
                    'paged_catalog_only': 24,
                    'paged_catalog_with_filters': 115,
                    'paged_catalog_with_route_blocks': 118,
                },
                'interval_summary': 'pages 0–23; filters 24–30; pages 31–37; filters 38–46; pages 47–53; filters 54–62; route-blocks 63–110; filters 111–158; route-blocks 159–238; filters 239–256',
            },
            {
                'minimum_dwell_unique_appends': 8,
                'effective_minimum_dwell_unique_appends': 8,
                'selected_transition_count': 5,
                'minimum_interval_dwell_unique_appends': 18,
                'cumulative_objective_without_transition_penalty': 4829176.138064,
                'regret_vs_unbounded_dynamic': 217.295277,
                'recommended_state_counts': {
                    'paged_catalog_only': 24,
                    'paged_catalog_with_filters': 115,
                    'paged_catalog_with_route_blocks': 118,
                },
                'interval_summary': 'pages 0–23; filters 24–62; route-blocks 63–110; filters 111–158; route-blocks 159–238; filters 239–256',
            },
            {
                'minimum_dwell_unique_appends': 19,
                'effective_minimum_dwell_unique_appends': 19,
                'selected_transition_count': 3,
                'minimum_interval_dwell_unique_appends': 48,
                'cumulative_objective_without_transition_penalty': 4830400.669232,
                'regret_vs_unbounded_dynamic': 1441.826445,
                'recommended_state_counts': {
                    'paged_catalog_only': 56,
                    'paged_catalog_with_filters': 48,
                    'paged_catalog_with_route_blocks': 153,
                },
                'interval_summary': 'pages 0–55; route-blocks 56–110; filters 111–158; route-blocks 159–256',
            },
            {
                'minimum_dwell_unique_appends': 49,
                'effective_minimum_dwell_unique_appends': 49,
                'selected_transition_count': 1,
                'minimum_interval_dwell_unique_appends': 56,
                'cumulative_objective_without_transition_penalty': 4834411.397743,
                'regret_vs_unbounded_dynamic': 5452.554956,
                'recommended_state_counts': {
                    'paged_catalog_only': 56,
                    'paged_catalog_with_filters': 0,
                    'paged_catalog_with_route_blocks': 201,
                },
                'interval_summary': 'pages 0–55; route-blocks 56–256',
            },
            {
                'minimum_dwell_unique_appends': 57,
                'effective_minimum_dwell_unique_appends': 57,
                'selected_transition_count': 0,
                'minimum_interval_dwell_unique_appends': 257,
                'cumulative_objective_without_transition_penalty': 4840091.073825,
                'regret_vs_unbounded_dynamic': 11132.231038,
                'recommended_state_counts': {
                    'paged_catalog_only': 0,
                    'paged_catalog_with_filters': 0,
                    'paged_catalog_with_route_blocks': 257,
                },
                'interval_summary': 'route-blocks 0–256',
            },
            {
                'minimum_dwell_unique_appends': 256,
                'effective_minimum_dwell_unique_appends': 256,
                'selected_transition_count': 0,
                'minimum_interval_dwell_unique_appends': 257,
                'cumulative_objective_without_transition_penalty': 4840091.073825,
                'regret_vs_unbounded_dynamic': 11132.231038,
                'recommended_state_counts': {
                    'paged_catalog_only': 0,
                    'paged_catalog_with_filters': 0,
                    'paged_catalog_with_route_blocks': 257,
                },
                'interval_summary': 'route-blocks 0–256',
            },
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
        'sources': [
            str(PACKET_PATH.relative_to(ROOT)),
            str(TRANSITION_BUDGET_REPORT_PATH.relative_to(ROOT)),
        ],
    }



def _render_md(report: dict[str, object]) -> str:
    findings = report['headline_findings']
    lines = [
        '# Rematch Proxy Delta Decision Packet Compact Repeat-State Minimum-Dwell Snapshot — 2026-03-07',
        '',
        '## Focus',
        f"- {report['focus']}",
        '',
        '## Headline findings',
        f"- packet script: `{report['packet_script']}`.",
        f"- deterministic frontier packet count: `{report['deterministic_frontier_packet_count']}`.",
        f"- live compact catalog starts at `{findings['entry_count']}` fingerprints across `{findings['page_count']}` pages with tail count `{findings['tail_entry_count']}` and route-block bitmap width `{findings['route_block_bitmap_len']}` bytes.",
        f"- at `{report['focal_expected_repeat_lookups']}` expected repeats over the next `{report['max_unique_appends']}` novel appends, the unconstrained dynamic optimum still uses `{findings['dynamic_transition_count']}` transitions.",
        f"- requiring a minimum dwell of `2` unique appends already suppresses the one-step cliff fallback and drops the schedule to `{findings['min_dwell_two_suppresses_one_step_cliffs_transition_count']}` transitions.",
        f"- requiring a minimum dwell of `8` unique appends collapses the schedule to `{findings['min_dwell_eight_transition_count']}` transitions while keeping `{findings['min_dwell_eight_gain_share_of_full_dynamic_savings']}` of the full dynamic savings; regret rises only to `{findings['min_dwell_eight_regret_vs_unbounded_dynamic']}` bytes.",
        f"- requiring a minimum dwell of `19` unique appends collapses the schedule further to `{findings['min_dwell_nineteen_transition_count']}` transitions while still keeping `{findings['min_dwell_nineteen_gain_share_of_full_dynamic_savings']}` of the full dynamic savings.",
        f"- by a minimum dwell of `49`, only the single early jump into route blocks remains and the schedule keeps `{findings['min_dwell_forty_nine_gain_share_of_full_dynamic_savings']}` of the dynamic savings.",
        f"- once the minimum dwell reaches `{findings['route_blocks_only_threshold_minimum_dwell_unique_appends']}`, the best policy is fixed route blocks from the start.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Exact minimum-dwell frontier',
        '| minimum dwell | selected transitions | actual minimum interval dwell | cumulative objective | gain vs fixed route blocks | gain share of full dynamic savings | regret vs unbounded dynamic | summary |',
        '|---:|---:|---:|---:|---:|---:|---:|---|',
    ]
    for row in report['frontier_rows']:
        dwell_label = (
            f"{row['minimum_dwell_start_unique_appends']}–{row['minimum_dwell_end_unique_appends']}"
            if row['minimum_dwell_start_unique_appends'] != row['minimum_dwell_end_unique_appends']
            else str(row['minimum_dwell_start_unique_appends'])
        )
        lines.append(
            f"| {dwell_label} | {row['selected_transition_count']} | {row['minimum_interval_dwell_unique_appends']} | {row['cumulative_objective_without_transition_penalty']} | {row['cumulative_gain_vs_fixed_route_blocks']} | {row['gain_share_of_full_dynamic_savings']} | {row['regret_vs_unbounded_dynamic']} | {row['interval_summary']} |"
        )
    lines.extend([
        '',
        '## Reference minimum-dwell settings',
        '| minimum dwell | selected transitions | actual minimum interval dwell | cumulative objective | regret vs unbounded dynamic | state counts | summary |',
        '|---:|---:|---:|---:|---:|---|---|',
    ])
    for row in report['reference_rows']:
        lines.append(
            f"| {row['minimum_dwell_unique_appends']} | {row['selected_transition_count']} | {row['minimum_interval_dwell_unique_appends']} | {row['cumulative_objective_without_transition_penalty']} | {row['regret_vs_unbounded_dynamic']} | `{row['recommended_state_counts']}` | {row['interval_summary']} |"
        )
    lines.extend([
        '',
        '## Sources',
        '- `scripts/analysis/rematch_proxy_delta_decision_packet.py`',
        '- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_transition_budget_snapshot_20260307.json`',
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
