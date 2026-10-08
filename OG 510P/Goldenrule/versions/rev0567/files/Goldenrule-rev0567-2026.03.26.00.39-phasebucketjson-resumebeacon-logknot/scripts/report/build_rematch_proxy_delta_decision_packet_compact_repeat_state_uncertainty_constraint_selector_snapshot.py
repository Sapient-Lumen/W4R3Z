#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_constraint_selector_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_constraint_selector_snapshot_20260308.md'
CAP_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_cap_staircase_snapshot_20260308.json'
CHECKPOINT_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_checkpoint_staircase_snapshot_20260308.json'
TOLERANCE_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_tolerance_staircase_snapshot_20260308.json'

TIER_ORDER = ['lower_guarantee', 'near_optimal', 'near_exact']
TIER_RANK = {tier: index for index, tier in enumerate(TIER_ORDER)}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _combine_tier_rows() -> list[dict[str, Any]]:
    cap = _load(CAP_REPORT)
    checkpoint = _load(CHECKPOINT_REPORT)
    tolerance = _load(TOLERANCE_REPORT)
    checkpoint_by_tier = {row['tier']: row for row in checkpoint['tier_rows']}
    tolerance_by_tier = {row['tier']: row for row in tolerance['tier_rows']}

    rows: list[dict[str, Any]] = []
    for row in cap['tier_rows']:
        tier = str(row['tier'])
        check_row = checkpoint_by_tier[tier]
        tol_row = tolerance_by_tier[tier]
        rows.append(
            {
                'tier': tier,
                'minimum_gain_share_of_full_dynamic_savings': float(row['minimum_gain_share_of_full_dynamic_savings']),
                'exact_hard_cap': int(row['exact_hard_cap']),
                'representative_anchor_minimum_dwell_unique_appends': int(row['representative_anchor_minimum_dwell_unique_appends']),
                'exact_dwell_band_start_unique_appends': int(row['exact_dwell_band_start_unique_appends']),
                'exact_dwell_band_end_unique_appends': int(row['exact_dwell_band_end_unique_appends']),
                'union_transition_checkpoint_count': int(check_row['union_transition_checkpoint_count']),
                'minimum_anchor_slack_unique_appends': int(tol_row['minimum_anchor_slack_unique_appends']),
                'exact_dwell_band_width_unique_appends': int(tol_row['exact_dwell_band_width_unique_appends']),
            }
        )
    rows.sort(key=lambda item: item['minimum_gain_share_of_full_dynamic_savings'])
    return rows


def _strongest_feasible(
    tiers: list[dict[str, Any]],
    *,
    max_hard_cap: int | None = None,
    max_checkpoints: int | None = None,
    min_anchor_slack: int | None = None,
    min_band_width: int | None = None,
) -> str | None:
    feasible: list[dict[str, Any]] = []
    for row in tiers:
        if max_hard_cap is not None and row['exact_hard_cap'] > max_hard_cap:
            continue
        if max_checkpoints is not None and row['union_transition_checkpoint_count'] > max_checkpoints:
            continue
        if min_anchor_slack is not None and row['minimum_anchor_slack_unique_appends'] < min_anchor_slack:
            continue
        if min_band_width is not None and row['exact_dwell_band_width_unique_appends'] < min_band_width:
            continue
        feasible.append(row)
    if not feasible:
        return None
    best = max(feasible, key=lambda item: item['minimum_gain_share_of_full_dynamic_savings'])
    return str(best['tier'])


def _axis_rows(tiers: list[dict[str, Any]], axis: str) -> list[dict[str, Any]]:
    if axis == 'max_hard_cap':
        budgets = [0, 1, 2, 3, 4, 5, 10, 11]
    elif axis == 'max_checkpoints':
        budgets = [0, 1, 4, 5, 7, 8, 13, 14]
    elif axis == 'min_anchor_slack':
        budgets = [0, 1, 5, 6, 7]
    elif axis == 'min_band_width':
        budgets = [1, 2, 11, 12, 14, 15]
    else:
        raise ValueError(axis)

    rows: list[dict[str, Any]] = []
    for budget in budgets:
        kwargs = {axis: budget}
        rows.append(
            {
                'axis': axis,
                'budget_or_requirement': budget,
                'strongest_feasible_tier': _strongest_feasible(tiers, **kwargs),
            }
        )
    return rows


def _selector_examples(tiers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    examples = [
        {'case': 'precision_budget_exact', 'max_hard_cap': 11, 'max_checkpoints': 14, 'min_anchor_slack': 0, 'min_band_width': 1},
        {'case': 'positive_slack_rules_out_near_exact', 'max_hard_cap': 11, 'max_checkpoints': 14, 'min_anchor_slack': 1, 'min_band_width': 1},
        {'case': 'moderate_budgets_keep_upgrade_knee', 'max_hard_cap': 5, 'max_checkpoints': 8, 'min_anchor_slack': 5, 'min_band_width': 2},
        {'case': 'checkpoint_bottleneck_demotes_to_lower', 'max_hard_cap': 11, 'max_checkpoints': 7, 'min_anchor_slack': 5, 'min_band_width': 2},
        {'case': 'slack_requirement_seven_leaves_no_exact_tier', 'max_hard_cap': 11, 'max_checkpoints': 14, 'min_anchor_slack': 7, 'min_band_width': 1},
    ]
    for row in examples:
        row['selected_tier'] = _strongest_feasible(
            tiers,
            max_hard_cap=row['max_hard_cap'],
            max_checkpoints=row['max_checkpoints'],
            min_anchor_slack=row['min_anchor_slack'],
            min_band_width=row['min_band_width'],
        )
    return examples


def _build_report() -> dict[str, Any]:
    tiers = _combine_tier_rows()
    by_tier = {row['tier']: row for row in tiers}
    cap_rows = _axis_rows(tiers, 'max_hard_cap')
    checkpoint_rows = _axis_rows(tiers, 'max_checkpoints')
    slack_rows = _axis_rows(tiers, 'min_anchor_slack')
    width_rows = _axis_rows(tiers, 'min_band_width')
    examples = _selector_examples(tiers)

    report = {
        'focus': 'Turn the exact uncertainty tiers into a compact feasibility selector so inheritors can ask for the strongest still-certifiable tier under concrete cap, checkpoint, and dwell-slack constraints instead of comparing reports manually.',
        'headline_findings': {
            'hard_cap_thresholds_for_strongest_feasible_tier': [
                {'maximum_hard_cap_budget_inclusive': 2, 'selected_tier': None},
                {'maximum_hard_cap_budget_inclusive': 4, 'selected_tier': 'lower_guarantee'},
                {'maximum_hard_cap_budget_inclusive': 10, 'selected_tier': 'near_optimal'},
                {'maximum_hard_cap_budget_inclusive': 11, 'selected_tier': 'near_exact'},
            ],
            'checkpoint_thresholds_for_strongest_feasible_tier': [
                {'maximum_checkpoint_budget_inclusive': 4, 'selected_tier': None},
                {'maximum_checkpoint_budget_inclusive': 7, 'selected_tier': 'lower_guarantee'},
                {'maximum_checkpoint_budget_inclusive': 13, 'selected_tier': 'near_optimal'},
                {'maximum_checkpoint_budget_inclusive': 14, 'selected_tier': 'near_exact'},
            ],
            'positive_minimum_anchor_slack_requirement_rules_out_near_exact': _strongest_feasible(tiers, min_anchor_slack=1) != 'near_exact',
            'strongest_feasible_tier_with_minimum_anchor_slack_zero': _strongest_feasible(tiers, min_anchor_slack=0),
            'strongest_feasible_tier_with_minimum_anchor_slack_one': _strongest_feasible(tiers, min_anchor_slack=1),
            'strongest_feasible_tier_with_minimum_anchor_slack_six': _strongest_feasible(tiers, min_anchor_slack=6),
            'strongest_feasible_tier_with_minimum_anchor_slack_seven': _strongest_feasible(tiers, min_anchor_slack=7),
            'minimum_band_width_requirements_demote_tiers_at_exact_cut_points': {
                '1': _strongest_feasible(tiers, min_band_width=1),
                '2': _strongest_feasible(tiers, min_band_width=2),
                '12': _strongest_feasible(tiers, min_band_width=12),
                '15': _strongest_feasible(tiers, min_band_width=15),
            },
            'main_rule': 'choose the strongest exact uncertainty tier by the tightest bottleneck: hard-cap budgets below 5 or checkpoint budgets below 8 rule out the 0.95 knee, any positive minimum-slack requirement rules out the 0.99 precision tier, and demanding at least seven dwell steps of minimum slack rules out every current exact tier.',
        },
        'decision_rules': [
            'Treat the strongest exact tier as a feasibility question, not a taste question: ask which lane survives your tightest budget first.',
            'Use the exact 0.99 lane only when hard-cap budget reaches 11, checkpoint budget reaches 14, and zero minimum slack is acceptable.',
            'Use the exact 0.95 lane as the strongest non-fragile selector outcome: it survives hard-cap budgets 5-10, checkpoint budgets 8-13, and positive minimum slack requirements up to 5.',
            'Drop to the exact 0.85 lane when either the hard-cap budget is only 3-4, the checkpoint budget is only 5-7, or the minimum slack requirement rises to 6.',
            'Do not promise any current exact uncertainty tier when the checkpoint budget is below 5, the hard-cap budget is below 3, or the required minimum slack is 7 or more.',
        ],
        'tier_rows': tiers,
        'axis_rows': {
            'max_hard_cap': cap_rows,
            'max_checkpoints': checkpoint_rows,
            'min_anchor_slack': slack_rows,
            'min_band_width': width_rows,
        },
        'selector_examples': examples,
        'source_reports': [
            str(CAP_REPORT.relative_to(ROOT)),
            str(CHECKPOINT_REPORT.relative_to(ROOT)),
            str(TOLERANCE_REPORT.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }
    return report


def _render_rows(rows: list[dict[str, Any]], axis_label: str, value_key: str) -> list[str]:
    lines = [f'| {axis_label} | strongest feasible exact tier |', '|---:|---|']
    for row in rows:
        value = row[value_key]
        tier = row['strongest_feasible_tier']
        lines.append(f'| {value} | {tier} |')
    return lines


def _render_md(report: dict[str, Any]) -> str:
    findings = report['headline_findings']
    lines = [
        '# Rematch Proxy Delta Decision Packet Compact Repeat-State Uncertainty Constraint Selector Snapshot — 2026-03-08',
        '',
        '## Focus',
        f"- {report['focus']}",
        '',
        '## Headline findings',
        f"- positive minimum slack rules out near-exact: `positive_minimum_anchor_slack_requirement_rules_out_near_exact = {findings['positive_minimum_anchor_slack_requirement_rules_out_near_exact']}`.",
        f"- strongest exact tier at minimum slack `0`: `{findings['strongest_feasible_tier_with_minimum_anchor_slack_zero']}`; at slack `1`: `{findings['strongest_feasible_tier_with_minimum_anchor_slack_one']}`; at slack `6`: `{findings['strongest_feasible_tier_with_minimum_anchor_slack_six']}`; at slack `7`: `{findings['strongest_feasible_tier_with_minimum_anchor_slack_seven']}`.",
        f"- band-width cut points: `{findings['minimum_band_width_requirements_demote_tiers_at_exact_cut_points']}`.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Exact certified tiers used by the selector',
        '| tier | min gain floor | hard cap | checkpoint count | minimum anchor slack | dwell band | band width | representative anchor |',
        '|---|---:|---:|---:|---:|---|---:|---:|',
    ]
    for row in report['tier_rows']:
        lines.append(
            f"| {row['tier']} | {row['minimum_gain_share_of_full_dynamic_savings']} | {row['exact_hard_cap']} | {row['union_transition_checkpoint_count']} | {row['minimum_anchor_slack_unique_appends']} | {row['exact_dwell_band_start_unique_appends']}–{row['exact_dwell_band_end_unique_appends']} | {row['exact_dwell_band_width_unique_appends']} | {row['representative_anchor_minimum_dwell_unique_appends']} |"
        )
    lines.extend([
        '',
        '## Selector thresholds by hard-cap budget',
        *_render_rows(report['axis_rows']['max_hard_cap'], 'maximum hard-cap budget', 'budget_or_requirement'),
        '',
        '## Selector thresholds by checkpoint budget',
        *_render_rows(report['axis_rows']['max_checkpoints'], 'maximum checkpoint budget', 'budget_or_requirement'),
        '',
        '## Selector thresholds by minimum anchor slack requirement',
        *_render_rows(report['axis_rows']['min_anchor_slack'], 'minimum anchor slack requirement', 'budget_or_requirement'),
        '',
        '## Selector thresholds by minimum dwell-band width requirement',
        *_render_rows(report['axis_rows']['min_band_width'], 'minimum dwell-band width requirement', 'budget_or_requirement'),
        '',
        '## Combined selector examples',
        '| case | cap budget | checkpoint budget | min slack | min band width | selected tier |',
        '|---|---:|---:|---:|---:|---|',
    ])
    for row in report['selector_examples']:
        lines.append(
            f"| {row['case']} | {row['max_hard_cap']} | {row['max_checkpoints']} | {row['min_anchor_slack']} | {row['min_band_width']} | {row['selected_tier']} |"
        )
    lines.extend([
        '',
        '## Decision rules',
    ])
    for rule in report['decision_rules']:
        lines.append(f'- {rule}')
    lines.extend([
        '',
        '## Provenance',
        f"- source reports: {', '.join(report['source_reports'])}",
        f"- source script: `{report['source_script']}`",
        '',
    ])
    return '\n'.join(lines)


def main() -> None:
    report = _build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2) + '\n')
    OUT_MD.write_text(_render_md(report))
    print(f'wrote {OUT_JSON.relative_to(ROOT)} and {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
