#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_post_amortization_selector_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_post_amortization_selector_snapshot_20260308.md'
MASTER_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_master_calendar_amortization_snapshot_20260308.json'
SELECTOR_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_constraint_selector_snapshot_20260308.json'

ORDER = ['lower_guarantee', 'near_optimal', 'near_exact']


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _tier_rows() -> tuple[int, list[dict[str, Any]]]:
    master = _load(MASTER_REPORT)
    selector = _load(SELECTOR_REPORT)
    full_master_count = int(master['headline_findings']['full_master_audit_checkpoint_count'])
    rows: list[dict[str, Any]] = []
    for row in selector['tier_rows']:
        rows.append(
            {
                'tier': str(row['tier']),
                'minimum_gain_share_of_full_dynamic_savings': float(row['minimum_gain_share_of_full_dynamic_savings']),
                'exact_hard_cap': int(row['exact_hard_cap']),
                'mode_specific_checkpoint_count': int(row['union_transition_checkpoint_count']),
                'post_amortized_checkpoint_count': full_master_count,
                'minimum_anchor_slack_unique_appends': int(row['minimum_anchor_slack_unique_appends']),
                'exact_dwell_band_width_unique_appends': int(row['exact_dwell_band_width_unique_appends']),
                'representative_anchor_minimum_dwell_unique_appends': int(row['representative_anchor_minimum_dwell_unique_appends']),
                'exact_dwell_band_start_unique_appends': int(row['exact_dwell_band_start_unique_appends']),
                'exact_dwell_band_end_unique_appends': int(row['exact_dwell_band_end_unique_appends']),
            }
        )
    rows.sort(key=lambda item: ORDER.index(item['tier']))
    return full_master_count, rows


def _strongest_feasible(
    tiers: list[dict[str, Any]],
    *,
    max_hard_cap: int | None = None,
    min_anchor_slack: int | None = None,
    min_band_width: int | None = None,
) -> str | None:
    feasible: list[dict[str, Any]] = []
    for row in tiers:
        if max_hard_cap is not None and row['exact_hard_cap'] > max_hard_cap:
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


def _build_rows(tiers: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    cap_budgets = [2, 3, 4, 5, 10, 11]
    slack_requirements = [0, 1, 5, 6, 7]
    width_requirements = [1, 2, 11, 12, 14, 15]

    return {
        'max_hard_cap_with_zero_slack': [
            {
                'max_hard_cap': budget,
                'min_anchor_slack': 0,
                'min_band_width': 1,
                'strongest_feasible_tier': _strongest_feasible(
                    tiers, max_hard_cap=budget, min_anchor_slack=0, min_band_width=1
                ),
            }
            for budget in cap_budgets
        ],
        'max_hard_cap_with_positive_slack': [
            {
                'max_hard_cap': budget,
                'min_anchor_slack': 1,
                'min_band_width': 2,
                'strongest_feasible_tier': _strongest_feasible(
                    tiers, max_hard_cap=budget, min_anchor_slack=1, min_band_width=2
                ),
            }
            for budget in cap_budgets
        ],
        'min_anchor_slack_with_cap_11': [
            {
                'max_hard_cap': 11,
                'min_anchor_slack': requirement,
                'min_band_width': 1,
                'strongest_feasible_tier': _strongest_feasible(
                    tiers, max_hard_cap=11, min_anchor_slack=requirement, min_band_width=1
                ),
            }
            for requirement in slack_requirements
        ],
        'min_band_width_with_cap_11': [
            {
                'max_hard_cap': 11,
                'min_anchor_slack': 0,
                'min_band_width': requirement,
                'strongest_feasible_tier': _strongest_feasible(
                    tiers, max_hard_cap=11, min_anchor_slack=0, min_band_width=requirement
                ),
            }
            for requirement in width_requirements
        ],
    }


def _selector_examples(tiers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    examples = [
        {
            'case': 'full_future_proof_precision',
            'master_calendar_pre_registered': True,
            'max_hard_cap': 11,
            'min_anchor_slack': 0,
            'min_band_width': 1,
        },
        {
            'case': 'full_future_proof_non_fragile_default',
            'master_calendar_pre_registered': True,
            'max_hard_cap': 11,
            'min_anchor_slack': 1,
            'min_band_width': 2,
        },
        {
            'case': 'full_future_proof_high_slack_relaxation',
            'master_calendar_pre_registered': True,
            'max_hard_cap': 11,
            'min_anchor_slack': 6,
            'min_band_width': 12,
        },
        {
            'case': 'full_future_proof_cap_limited_relaxation',
            'master_calendar_pre_registered': True,
            'max_hard_cap': 4,
            'min_anchor_slack': 1,
            'min_band_width': 2,
        },
        {
            'case': 'full_future_proof_no_exact_tier_left',
            'master_calendar_pre_registered': True,
            'max_hard_cap': 11,
            'min_anchor_slack': 7,
            'min_band_width': 15,
        },
    ]
    for row in examples:
        row['selected_tier'] = _strongest_feasible(
            tiers,
            max_hard_cap=row['max_hard_cap'],
            min_anchor_slack=row['min_anchor_slack'],
            min_band_width=row['min_band_width'],
        )
    return examples


def _build_report() -> dict[str, Any]:
    full_master_count, tiers = _tier_rows()
    rows = _build_rows(tiers)
    examples = _selector_examples(tiers)

    report = {
        'focus': 'Turn the pre-registered 17-point master calendar into an exact post-amortization selector so inheritors know which bottlenecks still matter after checkpoint budgets have been paid once.',
        'headline_findings': {
            'full_master_audit_checkpoint_count': full_master_count,
            'pre_registering_full_master_calendar_removes_checkpoint_budget_from_current_exact_selector': True,
            'strongest_future_proof_tier_with_cap_11_and_zero_slack': _strongest_feasible(
                tiers, max_hard_cap=11, min_anchor_slack=0, min_band_width=1
            ),
            'strongest_future_proof_tier_with_cap_11_and_positive_slack': _strongest_feasible(
                tiers, max_hard_cap=11, min_anchor_slack=1, min_band_width=2
            ),
            'strongest_future_proof_tier_with_cap_11_and_minimum_anchor_slack_six': _strongest_feasible(
                tiers, max_hard_cap=11, min_anchor_slack=6, min_band_width=12
            ),
            'strongest_future_proof_tier_with_cap_4_and_positive_slack': _strongest_feasible(
                tiers, max_hard_cap=4, min_anchor_slack=1, min_band_width=2
            ),
            'strongest_future_proof_tier_with_cap_11_and_minimum_anchor_slack_seven': _strongest_feasible(
                tiers, max_hard_cap=11, min_anchor_slack=7, min_band_width=15
            ),
            'near_optimal_is_strongest_non_fragile_future_proof_tier': (
                _strongest_feasible(tiers, max_hard_cap=11, min_anchor_slack=1, min_band_width=2) == 'near_optimal'
            ),
            'minimum_band_width_two_already_rules_out_near_exact': (
                _strongest_feasible(tiers, max_hard_cap=11, min_anchor_slack=0, min_band_width=2) != 'near_exact'
            ),
            'main_rule': 'once the 17-point master calendar is pre-registered, stop choosing among the current exact uncertainty tiers by checkpoint count; from that point onward the exact selector collapses to hard-cap and tolerance requirements, and the strongest non-fragile future-proof tier is the exact 0.95 lane.',
        },
        'decision_rules': [
            'If the full 17-point master calendar has already been pre-registered, treat per-tier checkpoint counts as sunk cost for the current exact uncertainty-safe modes.',
            'Reserve the exact 0.99 tier for precision deployments only: it still needs hard cap 11 and it fails immediately under either any positive minimum anchor-slack requirement or any minimum band-width requirement above 1.',
            'Treat the exact 0.95 tier as the strongest future-proof non-fragile default once checkpoints are amortized: it survives hard-cap budgets 5-11, positive minimum slack up to 5, and band-width requirements up to 11.',
            'Drop to the exact 0.85 tier when cap budget is only 3-4 or when the deployment insists on minimum anchor slack 6 or band width 12-14.',
            'Do not promise any current exact uncertainty tier after amortization when hard-cap budget is below 3, minimum anchor slack is 7 or more, or minimum dwell-band width is 15 or more.',
        ],
        'tier_rows': tiers,
        'post_amortization_selector_rows': rows,
        'selector_examples': examples,
        'source_reports': [
            str(MASTER_REPORT.relative_to(ROOT)),
            str(SELECTOR_REPORT.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }
    return report


def _render_table(rows: list[dict[str, Any]], first_header: str, first_key: str) -> list[str]:
    lines = [f'| {first_header} | min anchor slack | min band width | strongest feasible exact tier |', '|---:|---:|---:|---|']
    for row in rows:
        lines.append(
            f"| {row[first_key]} | {row['min_anchor_slack']} | {row['min_band_width']} | {row['strongest_feasible_tier']} |"
        )
    return lines


def _render_md(report: dict[str, Any]) -> str:
    findings = report['headline_findings']
    lines = [
        '# Rematch Proxy Delta Decision Packet Compact Repeat-State Post-Amortization Selector Snapshot — 2026-03-08',
        '',
        '## Focus',
        f"- {report['focus']}",
        '',
        '## Headline findings',
        f"- full master calendar size: `{findings['full_master_audit_checkpoint_count']}` checkpoints.",
        f"- checkpoint budgets removed from current exact selector once master is pre-registered: `{findings['pre_registering_full_master_calendar_removes_checkpoint_budget_from_current_exact_selector']}`.",
        f"- strongest future-proof tier at cap `11`, slack `0`, band width `1`: `{findings['strongest_future_proof_tier_with_cap_11_and_zero_slack']}`.",
        f"- strongest future-proof tier at cap `11`, positive slack, band width `2`: `{findings['strongest_future_proof_tier_with_cap_11_and_positive_slack']}`.",
        f"- strongest future-proof tier at cap `11`, slack `6`, band width `12`: `{findings['strongest_future_proof_tier_with_cap_11_and_minimum_anchor_slack_six']}`.",
        f"- strongest future-proof tier at cap `4`, positive slack, band width `2`: `{findings['strongest_future_proof_tier_with_cap_4_and_positive_slack']}`.",
        f"- strongest future-proof tier at cap `11`, slack `7`, band width `15`: `{findings['strongest_future_proof_tier_with_cap_11_and_minimum_anchor_slack_seven']}`.",
        f"- minimum band width `2` already rules out near-exact: `{findings['minimum_band_width_two_already_rules_out_near_exact']}`.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Exact tiers after checkpoint amortization',
        '| tier | min gain floor | hard cap | mode-specific checkpoint count | post-amortized checkpoint count | minimum anchor slack | band width | dwell band | anchor |',
        '|---|---:|---:|---:|---:|---:|---:|---|---:|',
    ]
    for row in report['tier_rows']:
        lines.append(
            f"| {row['tier']} | {row['minimum_gain_share_of_full_dynamic_savings']} | {row['exact_hard_cap']} | {row['mode_specific_checkpoint_count']} | {row['post_amortized_checkpoint_count']} | {row['minimum_anchor_slack_unique_appends']} | {row['exact_dwell_band_width_unique_appends']} | {row['exact_dwell_band_start_unique_appends']}–{row['exact_dwell_band_end_unique_appends']} | {row['representative_anchor_minimum_dwell_unique_appends']} |"
        )
    lines.extend([
        '',
        '## Hard-cap thresholds after checkpoint amortization with zero slack',
        *_render_table(report['post_amortization_selector_rows']['max_hard_cap_with_zero_slack'], 'max hard cap', 'max_hard_cap'),
        '',
        '## Hard-cap thresholds after checkpoint amortization with positive slack',
        *_render_table(report['post_amortization_selector_rows']['max_hard_cap_with_positive_slack'], 'max hard cap', 'max_hard_cap'),
        '',
        '## Minimum slack thresholds after checkpoint amortization at cap 11',
        *_render_table(report['post_amortization_selector_rows']['min_anchor_slack_with_cap_11'], 'min anchor slack', 'min_anchor_slack'),
        '',
        '## Minimum band-width thresholds after checkpoint amortization at cap 11',
        *_render_table(report['post_amortization_selector_rows']['min_band_width_with_cap_11'], 'min band width', 'min_band_width'),
        '',
        '## Combined selector examples',
        '| case | master pre-registered | max hard cap | min slack | min band width | selected tier |',
        '|---|---|---:|---:|---:|---|',
    ])
    for row in report['selector_examples']:
        lines.append(
            f"| {row['case']} | {row['master_calendar_pre_registered']} | {row['max_hard_cap']} | {row['min_anchor_slack']} | {row['min_band_width']} | {row['selected_tier']} |"
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
