#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_control_card_snapshot_20260308.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_control_card_snapshot_20260308.md'
OPERATING_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_operating_modes_snapshot_20260308.json'
UNCERTAINTY_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_repeat_uncertainty_snapshot_20260307.json'
TRANSITION_BUDGET_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_transition_budget_snapshot_20260307.json'
SWITCH_PENALTY_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_switch_penalty_snapshot_20260307.json'
FIXED_POLICY_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_fixed_policy_snapshot_20260307.json'


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text())


def _build_summary() -> dict[str, object]:
    operating = _load(OPERATING_REPORT)
    uncertainty = _load(UNCERTAINTY_REPORT)
    transition_budget = _load(TRANSITION_BUDGET_REPORT)
    switch_penalty = _load(SWITCH_PENALTY_REPORT)
    fixed_policy = _load(FIXED_POLICY_REPORT)

    operating_findings = operating['headline_findings']
    uncertainty_findings = uncertainty['headline_findings']
    transition_findings = transition_budget['headline_findings']
    switch_findings = switch_penalty['headline_findings']
    fixed_findings = fixed_policy['headline_findings']

    control_rows = [
        {
            'priority': 1,
            'trigger': (
                f"expected repeats >= {operating_findings['fixed_route_blocks_first_exact_repeat_budget']} "
                f"or rewrite cost >= {operating_findings['fixed_route_blocks_switch_cost_break_even_per_transition_bytes']} bytes per transition"
            ),
            'selected_mode': 'fixed_route_blocks',
            'action': 'freeze into route blocks immediately and stop replaying sidecar upgrades or downgrades',
            'why': 'beyond either threshold, the measured frontier says extra sidecar rewrites no longer beat the best fixed sidecar overall',
        },
        {
            'priority': 2,
            'trigger': (
                f"rewrite count is explicitly capped at <= {operating_findings['rewrite_budget_mode_transition_ceiling']} "
                'and repeat estimate is trusted'
            ),
            'selected_mode': 'rewrite_budgeted',
            'action': 'use the transition-budgeted staged plan and spend the first few rewrites on the large structural bands first',
            'why': (
                f"the first {operating_findings['rewrite_budget_mode_transition_ceiling']} rewrites preserve "
                f"{operating_findings['rewrite_budget_mode_gain_share_of_full_dynamic_savings']} of full dynamic savings"
            ),
        },
        {
            'priority': 3,
            'trigger': 'repeat estimate is uncertain inside the current 0.15-0.25 planning band',
            'selected_mode': 'uncertainty_robust_default',
            'action': (
                f"default to minimum dwell {operating_findings['default_anchor_minimum_dwell_unique_appends']}; "
                f"widen to dwell {uncertainty_findings['eighty_five_percent_anchor_minimum_dwell_unique_appends']} when simplicity matters more than a few extra transitions"
            ),
            'why': (
                f"dwell {operating_findings['default_anchor_minimum_dwell_unique_appends']} keeps at least "
                f"{operating_findings['default_worst_case_gain_share_of_full_dynamic_savings']} of full dynamic savings "
                f"while staying within {operating_findings['default_transition_range']['minimum_selected_transition_count']}–"
                f"{operating_findings['default_transition_range']['maximum_selected_transition_count']} transitions"
            ),
        },
        {
            'priority': 4,
            'trigger': (
                f"rewrite cost is known and sits between {switch_findings['micro_churn_ceiling_bytes']} and "
                f"{operating_findings['fixed_route_blocks_switch_cost_break_even_per_transition_bytes']} bytes per transition"
            ),
            'selected_mode': 'priced_switch_frontier',
            'action': 'price churn explicitly, suppress the micro-oscillations first, and keep only the large front-loaded switches that still pay',
            'why': (
                f"single-step churn disappears above {switch_findings['micro_churn_ceiling_bytes']} bytes per rewrite, "
                f"but a {switch_findings['focal_transition_count']}-transition plan still beats fixed route blocks at the focal penalty"
            ),
        },
        {
            'priority': 5,
            'trigger': 'none of the earlier constraints bind and the final slice of byte savings is worth precise retuning',
            'selected_mode': 'exact_dynamic',
            'action': 'replay the full exact staged planner',
            'why': (
                f"this is the only mode that keeps the full dynamic optimum, but it requires "
                f"{operating_findings['full_dynamic_transition_count']} transitions on the focal horizon"
            ),
        },
    ]

    return {
        'focus': 'Compress the compact repeat-sidecar operating ladder into a tiny precedence-ordered control card so future inheritors can choose a mode from a few observable thresholds instead of reopening every frontier report.',
        'headline_findings': {
            'default_mode': operating_findings['default_operating_mode'],
            'default_minimum_dwell_unique_appends': operating_findings['default_anchor_minimum_dwell_unique_appends'],
            'default_worst_case_gain_share_of_full_dynamic_savings': operating_findings['default_worst_case_gain_share_of_full_dynamic_savings'],
            'default_transition_range': operating_findings['default_transition_range'],
            'rewrite_budget_transition_ceiling': operating_findings['rewrite_budget_mode_transition_ceiling'],
            'rewrite_budget_gain_share_of_full_dynamic_savings': operating_findings['rewrite_budget_mode_gain_share_of_full_dynamic_savings'],
            'micro_churn_ceiling_bytes_per_transition': switch_findings['micro_churn_ceiling_bytes'],
            'freeze_break_even_bytes_per_transition': operating_findings['fixed_route_blocks_switch_cost_break_even_per_transition_bytes'],
            'freeze_repeat_budget_threshold': operating_findings['fixed_route_blocks_first_exact_repeat_budget'],
            'full_dynamic_transition_count': operating_findings['full_dynamic_transition_count'],
            'main_rule': 'apply the smallest control card that matches the archive\'s real constraint: freeze first when rewrites do not pay, honor any explicit rewrite cap next, use dwell 9 as the uncertainty-safe default, price churn explicitly when rewrite cost is known, and only replay the exact planner for the final slice of value.',
        },
        'control_rows': control_rows,
        'observables': [
            'expected_repeat_lookups estimate or uncertainty band',
            'rewrite count budget over the horizon',
            'rewrite cost per sidecar transition in bytes-equivalent operational regret',
            'whether the repeat estimate is trusted or only approximately known',
            'whether simplicity matters more than the last slice of byte savings',
        ],
        'source_reports': [
            str(OPERATING_REPORT.relative_to(ROOT)),
            str(UNCERTAINTY_REPORT.relative_to(ROOT)),
            str(TRANSITION_BUDGET_REPORT.relative_to(ROOT)),
            str(SWITCH_PENALTY_REPORT.relative_to(ROOT)),
            str(FIXED_POLICY_REPORT.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
        'supporting_measures': {
            'first_switch_gain_vs_fixed_route_blocks_bytes': transition_findings['first_switch_gain_vs_fixed_route_blocks_bytes'],
            'first_four_switch_gain_share_of_full_dynamic_savings': transition_findings['first_four_switch_gain_share_of_full_dynamic_savings'],
            'fixed_policy_regret_vs_dynamic_bytes': fixed_findings['focal_best_fixed_regret_vs_dynamic'],
            'micro_churn_regime_count_at_or_above_ceiling': switch_findings['practical_regime_count_at_or_above_micro_churn_ceiling'],
            'uncertainty_simplicity_dwell': uncertainty_findings['eighty_five_percent_anchor_minimum_dwell_unique_appends'],
            'uncertainty_simplicity_worst_case_gain_share': uncertainty_findings['eighty_five_percent_worst_case_gain_share_of_full_dynamic_savings'],
        },
    }


def _render_md(report: dict[str, object]) -> str:
    findings = report['headline_findings']
    lines = [
        '# Rematch Proxy Delta Decision Packet Compact Repeat-State Control Card Snapshot — 2026-03-08',
        '',
        '## Focus',
        f"- {report['focus']}",
        '',
        '## Headline findings',
        f"- default control mode: `{findings['default_mode']}`.",
        f"- the uncertainty-safe default remains minimum dwell `{findings['default_minimum_dwell_unique_appends']}`, which keeps at least `{findings['default_worst_case_gain_share_of_full_dynamic_savings']}` of full dynamic savings while staying within `{findings['default_transition_range']['minimum_selected_transition_count']}`–`{findings['default_transition_range']['maximum_selected_transition_count']}` transitions.",
        f"- if rewrite count is explicitly capped, the practical ceiling is still `{findings['rewrite_budget_transition_ceiling']}` transitions, preserving `{findings['rewrite_budget_gain_share_of_full_dynamic_savings']}` of full dynamic savings.",
        f"- if rewrite cost is known, suppress micro-churn first above `{findings['micro_churn_ceiling_bytes_per_transition']}` bytes per transition and freeze completely once cost reaches `{findings['freeze_break_even_bytes_per_transition']}` bytes per transition.",
        f"- fixed route blocks also become exact by repeat budget `{findings['freeze_repeat_budget_threshold']}`.",
        f"- reserve the full exact planner for the cases where the last slice of value matters and `{findings['full_dynamic_transition_count']}` transitions are still acceptable.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Required observables',
    ]
    for observable in report['observables']:
        lines.append(f'- {observable}')
    lines.extend([
        '',
        '## Precedence-ordered control card',
        '| priority | trigger | selected mode | action | why |',
        '|---:|---|---|---|---|',
    ])
    for row in report['control_rows']:
        lines.append(
            f"| {row['priority']} | {row['trigger']} | `{row['selected_mode']}` | {row['action']} | {row['why']} |"
        )
    lines.extend([
        '',
        '## Supporting measures',
        f"- first rewrite gain versus fixed route blocks: `{report['supporting_measures']['first_switch_gain_vs_fixed_route_blocks_bytes']}` bytes.",
        f"- first four rewrites preserve `{report['supporting_measures']['first_four_switch_gain_share_of_full_dynamic_savings']}` of full dynamic savings.",
        f"- best fixed-policy regret versus the full dynamic plan at the focal horizon: `{report['supporting_measures']['fixed_policy_regret_vs_dynamic_bytes']}` bytes.",
        f"- practical priced-churn frontier still has `{report['supporting_measures']['micro_churn_regime_count_at_or_above_ceiling']}` regimes at or above the micro-churn ceiling.",
        f"- simplicity-first uncertainty preset: dwell `{report['supporting_measures']['uncertainty_simplicity_dwell']}` with worst-case gain share `{report['supporting_measures']['uncertainty_simplicity_worst_case_gain_share']}`.",
        '',
        '## Sources',
    ])
    for source in report['source_reports']:
        lines.append(f'- `{source}`')
    return '\n'.join(lines) + '\n'


def main() -> None:
    report = _build_summary()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    OUT_MD.write_text(_render_md(report))
    print(f'wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'wrote {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
