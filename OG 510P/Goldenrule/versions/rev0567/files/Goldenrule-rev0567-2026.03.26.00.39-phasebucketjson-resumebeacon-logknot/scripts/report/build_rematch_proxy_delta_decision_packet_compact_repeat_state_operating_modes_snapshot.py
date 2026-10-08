#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_operating_modes_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_operating_modes_snapshot_20260308.md'

FIXED_POLICY_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_fixed_policy_snapshot_20260307.json'
TRANSITION_BUDGET_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_transition_budget_snapshot_20260307.json'
MIN_DWELL_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_snapshot_20260307.json'
ANCHOR_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_anchor_snapshot_20260307.json'
REPEAT_UNCERTAINTY_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_repeat_uncertainty_snapshot_20260307.json'
STAGING_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_staging_snapshot_20260307.json'


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text())


def _build_summary() -> dict[str, object]:
    fixed_policy = _load(FIXED_POLICY_REPORT)
    transition_budget = _load(TRANSITION_BUDGET_REPORT)
    min_dwell = _load(MIN_DWELL_REPORT)
    anchor = _load(ANCHOR_REPORT)
    repeat_uncertainty = _load(REPEAT_UNCERTAINTY_REPORT)
    staging = _load(STAGING_REPORT)

    fixed = fixed_policy['headline_findings']
    budget = transition_budget['headline_findings']
    dwell = min_dwell['headline_findings']
    anchor_findings = anchor['headline_findings']
    uncertainty = repeat_uncertainty['headline_findings']
    stage = staging['headline_findings']

    operating_rows = [
        {
            'mode': 'exact_dynamic',
            'when_to_choose': 'only when repeat estimates are trusted and the archive is willing to replay every profitable upgrade and downgrade band',
            'policy_form': 'exact staged planner',
            'repeat_scope': 'single trusted repeat estimate',
            'rewrite_scope': 'up to 12 transitions on the current 0.18-repeat horizon',
            'measured_preserved_gain_share_of_full_dynamic_savings': 1.0,
            'worst_case_transition_range': '12-12',
            'key_measure': {
                'dynamic_transition_count_at_0_18_repeats': fixed['focal_dynamic_transition_count'],
                'first_route_interval': stage['first_route_interval'],
                'bitmap_cliff_page_reentry_interval': stage['bitmap_cliff_page_reentry_interval'],
            },
        },
        {
            'mode': 'rewrite_budgeted',
            'when_to_choose': 'when rewrite count is the hard operational bottleneck but the archive still wants most of the dynamic savings',
            'policy_form': 'transition-budgeted staged planner',
            'repeat_scope': 'single trusted repeat estimate',
            'rewrite_scope': '4 transitions',
            'measured_preserved_gain_share_of_full_dynamic_savings': budget['first_four_switch_gain_share_of_full_dynamic_savings'],
            'worst_case_transition_range': '4-4',
            'key_measure': {
                'practical_transition_budget_ceiling': budget['practical_transition_budget_ceiling'],
                'first_switch_gain_vs_fixed_route_blocks_bytes': budget['first_switch_gain_vs_fixed_route_blocks_bytes'],
                'third_switch_gain_vs_second_budget_bytes': budget['third_switch_gain_vs_second_budget_bytes'],
            },
        },
        {
            'mode': 'uncertainty_robust_default',
            'when_to_choose': 'default inheritor preset when repeat volume is only known approximately inside the current 0.15-0.25 band',
            'policy_form': 'minimum dwell = 9',
            'repeat_scope': 'repeat band 0.15-0.25',
            'rewrite_scope': 'implicit dwell-based schedule',
            'measured_preserved_gain_share_of_full_dynamic_savings': uncertainty['ninety_five_percent_worst_case_gain_share_of_full_dynamic_savings'],
            'worst_case_transition_range': f"{uncertainty['ninety_five_percent_minimum_selected_transition_count']}-{uncertainty['ninety_five_percent_maximum_selected_transition_count']}",
            'key_measure': {
                'anchor_minimum_dwell_unique_appends': uncertainty['ninety_five_percent_anchor_minimum_dwell_unique_appends'],
                'anchor_margin_unique_appends': uncertainty['ninety_five_percent_anchor_margin_unique_appends'],
                'overlap_end_unique_appends': uncertainty['ninety_five_percent_overlap_end_unique_appends'],
            },
        },
        {
            'mode': 'uncertainty_robust_simplicity',
            'when_to_choose': 'when repeat volume is uncertain but the archive prefers a broader safety margin and allows the low-repeat edge to collapse to very few or zero transitions',
            'policy_form': 'minimum dwell = 16',
            'repeat_scope': 'repeat band 0.15-0.25',
            'rewrite_scope': 'implicit dwell-based schedule',
            'measured_preserved_gain_share_of_full_dynamic_savings': uncertainty['eighty_five_percent_worst_case_gain_share_of_full_dynamic_savings'],
            'worst_case_transition_range': f"{uncertainty['eighty_five_percent_minimum_selected_transition_count']}-{uncertainty['eighty_five_percent_maximum_selected_transition_count']}",
            'key_measure': {
                'anchor_minimum_dwell_unique_appends': uncertainty['eighty_five_percent_anchor_minimum_dwell_unique_appends'],
                'anchor_margin_unique_appends': uncertainty['eighty_five_percent_anchor_margin_unique_appends'],
                'overlap_end_unique_appends': uncertainty['eighty_five_percent_overlap_end_unique_appends'],
            },
        },
        {
            'mode': 'fixed_route_blocks',
            'when_to_choose': 'when sidecar rewrites are expensive enough that a fixed sidecar is cheaper overall, or when repeat volume is high enough that route blocks already match the dynamic schedule exactly',
            'policy_form': 'always-on route blocks',
            'repeat_scope': 'single trusted repeat estimate or high-repeat regime',
            'rewrite_scope': '0 transitions',
            'measured_preserved_gain_share_of_full_dynamic_savings': None,
            'worst_case_transition_range': '0-0',
            'key_measure': {
                'focal_regret_vs_dynamic_at_0_18_repeats': fixed['focal_route_blocks_regret_vs_dynamic'],
                'switch_cost_break_even_per_transition_bytes': fixed['focal_transition_penalty_break_even_per_switch_bytes'],
                'first_exact_route_block_budget': fixed['first_exact_route_block_budget'],
            },
        },
    ]

    return {
        'focus': 'Distill the compact repeat-sidecar frontier into a tiny inheritor operating ladder so future sessions can pick a deployment mode without reopening every underlying frontier report.',
        'source_reports': [
            str(FIXED_POLICY_REPORT.relative_to(ROOT)),
            str(TRANSITION_BUDGET_REPORT.relative_to(ROOT)),
            str(MIN_DWELL_REPORT.relative_to(ROOT)),
            str(ANCHOR_REPORT.relative_to(ROOT)),
            str(REPEAT_UNCERTAINTY_REPORT.relative_to(ROOT)),
            str(STAGING_REPORT.relative_to(ROOT)),
        ],
        'headline_findings': {
            'default_operating_mode': 'uncertainty_robust_default',
            'default_anchor_minimum_dwell_unique_appends': uncertainty['ninety_five_percent_anchor_minimum_dwell_unique_appends'],
            'default_anchor_margin_unique_appends': uncertainty['ninety_five_percent_anchor_margin_unique_appends'],
            'default_worst_case_gain_share_of_full_dynamic_savings': uncertainty['ninety_five_percent_worst_case_gain_share_of_full_dynamic_savings'],
            'default_transition_range': {
                'minimum_selected_transition_count': uncertainty['ninety_five_percent_minimum_selected_transition_count'],
                'maximum_selected_transition_count': uncertainty['ninety_five_percent_maximum_selected_transition_count'],
            },
            'rewrite_budget_mode_transition_ceiling': budget['practical_transition_budget_ceiling'],
            'rewrite_budget_mode_gain_share_of_full_dynamic_savings': budget['first_four_switch_gain_share_of_full_dynamic_savings'],
            'legacy_single_budget_near_optimal_anchor': anchor_findings['ninety_five_percent_anchor_minimum_dwell_unique_appends'],
            'single_budget_practical_default_minimum_dwell_unique_appends': dwell['practical_default_minimum_dwell_unique_appends'],
            'fixed_route_blocks_switch_cost_break_even_per_transition_bytes': fixed['focal_transition_penalty_break_even_per_switch_bytes'],
            'fixed_route_blocks_first_exact_repeat_budget': fixed['first_exact_route_block_budget'],
            'full_dynamic_transition_count': fixed['focal_dynamic_transition_count'],
            'main_rule': 'ship one small operating ladder: use the uncertainty-robust dwell-9 preset by default, fall back to the 4-transition staged plan when rewrite count is explicitly budgeted, widen to dwell 16 when simplicity matters more than a few extra transitions, and freeze on route blocks once switch cost or repeat volume makes rewrites not worth it.',
        },
        'decision_rules': [
            'Default to the uncertainty-robust dwell-9 preset when repeat volume is uncertain inside the current 0.15-0.25 band.',
            'Use the 4-transition staged plan when rewrite count is explicitly capped and repeat estimates are trusted.',
            'Use dwell 16 when the archive wants a broader uncertainty-safe preset and can accept the low-repeat edge collapsing to zero transitions.',
            'Use fixed route blocks when average rewrite cost clears 927.685921 bytes per transition or when expected repeats reach 0.7 and route blocks match the dynamic schedule exactly.',
            'Only replay the full 12-transition dynamic schedule when the archive truly values the last slice of byte savings and is comfortable with precise retuning around bitmap cliffs.',
        ],
        'operating_rows': operating_rows,
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(report: dict[str, object]) -> str:
    findings = report['headline_findings']
    lines = [
        '# Rematch Proxy Delta Decision Packet Compact Repeat-State Operating Modes Snapshot — 2026-03-08',
        '',
        '## Focus',
        f"- {report['focus']}",
        '',
        '## Headline findings',
        f"- default operating mode: `{findings['default_operating_mode']}`.",
        f"- the default inheritor preset is dwell `{findings['default_anchor_minimum_dwell_unique_appends']}` with a ±`{findings['default_anchor_margin_unique_appends']}`-append margin; across repeat budgets `0.15`–`0.25`, it keeps at least `{findings['default_worst_case_gain_share_of_full_dynamic_savings']}` of full dynamic savings while staying within `{findings['default_transition_range']['minimum_selected_transition_count']}`–`{findings['default_transition_range']['maximum_selected_transition_count']}` transitions.",
        f"- if rewrite count is the hard bottleneck, the current practical ceiling is `{findings['rewrite_budget_mode_transition_ceiling']}` transitions, which still preserves `{findings['rewrite_budget_mode_gain_share_of_full_dynamic_savings']}` of full dynamic savings on the focal `0.18` repeat horizon.",
        f"- the older single-budget near-optimal anchor is dwell `{findings['legacy_single_budget_near_optimal_anchor']}`, while the single-budget practical default was dwell `{findings['single_budget_practical_default_minimum_dwell_unique_appends']}`; the new synthesis prefers dwell `{findings['default_anchor_minimum_dwell_unique_appends']}` because it survives repeat uncertainty instead of one guessed repeat rate.",
        f"- fixed route blocks become the right freeze policy once rewrite cost clears `{findings['fixed_route_blocks_switch_cost_break_even_per_transition_bytes']}` bytes per transition on average, and they already match the dynamic schedule exactly by repeat budget `{findings['fixed_route_blocks_first_exact_repeat_budget']}`.",
        f"- full exact staging still exists, but it requires `{findings['full_dynamic_transition_count']}` transitions on the focal horizon and should be reserved for sessions that truly need the final slice of savings.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Operating ladder',
        '| mode | policy form | repeat scope | transition / rewrite scope | measured preserved gain share | key operational measure |',
        '|---|---|---|---|---:|---|',
    ]
    for row in report['operating_rows']:
        gain_share = row['measured_preserved_gain_share_of_full_dynamic_savings']
        gain_share_text = 'n/a' if gain_share is None else str(gain_share)
        key_measure = ', '.join(f"{key}={value}" for key, value in row['key_measure'].items())
        lines.append(
            f"| `{row['mode']}` | `{row['policy_form']}` | {row['repeat_scope']} | {row['worst_case_transition_range']} | {gain_share_text} | {key_measure} |"
        )
    lines.extend([
        '',
        '## Decision rules',
    ])
    for rule in report['decision_rules']:
        lines.append(f'- {rule}')
    lines.extend([
        '',
        '## Source reports',
    ])
    for path in report['source_reports']:
        lines.append(f'- `{path}`')
    return '\n'.join(lines) + '\n'


def main() -> None:
    report = _build_summary()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    OUT_MD.write_text(_render_md(report))
    print(f'wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'wrote {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
