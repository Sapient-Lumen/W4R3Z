#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_premium_vs_trusted_repeat_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_premium_vs_trusted_repeat_snapshot_20260308.md'
CONTROL_CARD_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_control_card_snapshot_20260308.json'
CHECKPOINT_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_checkpoint_schedule_snapshot_20260308.json'
CAP_STAIRCASE_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_cap_staircase_snapshot_20260308.json'
UNCERTAINTY_CHECKPOINT_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_checkpoint_staircase_snapshot_20260308.json'


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _trusted_repeat_baseline() -> dict[str, Any]:
    control = _load(CONTROL_CARD_REPORT)
    checkpoints = _load(CHECKPOINT_REPORT)
    rewrite_row = checkpoints['rewrite_budget_row']
    findings = control['headline_findings']
    return {
        'mode': 'trusted_repeat_rewrite_budgeted',
        'repeat_scope': 'single trusted repeat estimate',
        'focal_expected_repeat_lookups': 0.18,
        'preserved_gain_share_of_full_dynamic_savings': float(findings['rewrite_budget_gain_share_of_full_dynamic_savings']),
        'selected_transition_count': int(findings['rewrite_budget_transition_ceiling']),
        'transition_checkpoints_unique_appends': [int(x) for x in rewrite_row['transition_boundaries_unique_appends']],
        'transition_checkpoint_count': len(rewrite_row['transition_boundaries_unique_appends']),
        'interval_summary': str(rewrite_row['interval_summary']),
    }


def _uncertainty_tier_rows() -> list[dict[str, Any]]:
    cap = _load(CAP_STAIRCASE_REPORT)
    checkpoint = _load(UNCERTAINTY_CHECKPOINT_REPORT)
    checkpoint_by_tier = {row['tier']: row for row in checkpoint['tier_rows']}
    rows: list[dict[str, Any]] = []
    for row in cap['tier_rows']:
        tier = str(row['tier'])
        check_row = checkpoint_by_tier[tier]
        rows.append(
            {
                'tier': tier,
                'minimum_gain_share_of_full_dynamic_savings': float(row['minimum_gain_share_of_full_dynamic_savings']),
                'focal_gain_share_of_full_dynamic_savings_at_0_18_repeats': float(row['focal_gain_share_of_full_dynamic_savings']),
                'exact_hard_cap': int(row['exact_hard_cap']),
                'representative_anchor_minimum_dwell_unique_appends': int(row['representative_anchor_minimum_dwell_unique_appends']),
                'exact_dwell_band_start_unique_appends': int(row['exact_dwell_band_start_unique_appends']),
                'exact_dwell_band_end_unique_appends': int(row['exact_dwell_band_end_unique_appends']),
                'union_transition_checkpoints_unique_appends': [int(x) for x in check_row['union_transition_checkpoints_unique_appends']],
                'union_transition_checkpoint_count': int(check_row['union_transition_checkpoint_count']),
            }
        )
    order = {'lower_guarantee': 0, 'near_optimal': 1, 'near_exact': 2}
    rows.sort(key=lambda item: order[item['tier']])
    return rows


def _comparison_rows(baseline: dict[str, Any], tiers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    base_checkpoints = set(baseline['transition_checkpoints_unique_appends'])
    rows: list[dict[str, Any]] = []
    for row in tiers:
        target_checkpoints = set(row['union_transition_checkpoints_unique_appends'])
        added = sorted(target_checkpoints - base_checkpoints)
        dropped = sorted(base_checkpoints - target_checkpoints)
        rows.append(
            {
                'from_mode': baseline['mode'],
                'to_tier': row['tier'],
                'minimum_gain_share_of_full_dynamic_savings': row['minimum_gain_share_of_full_dynamic_savings'],
                'focal_gain_share_of_full_dynamic_savings_at_0_18_repeats': row['focal_gain_share_of_full_dynamic_savings_at_0_18_repeats'],
                'hard_cap_delta': int(row['exact_hard_cap'] - baseline['selected_transition_count']),
                'net_checkpoint_count_delta': int(row['union_transition_checkpoint_count'] - baseline['transition_checkpoint_count']),
                'gross_added_checkpoint_count': len(added),
                'gross_dropped_checkpoint_count': len(dropped),
                'checkpoints_added_unique_appends': added,
                'checkpoints_dropped_unique_appends': dropped,
                'focal_gain_share_delta_at_0_18_repeats': round(
                    row['focal_gain_share_of_full_dynamic_savings_at_0_18_repeats']
                    - baseline['preserved_gain_share_of_full_dynamic_savings'],
                    6,
                ),
                'representative_anchor_minimum_dwell_unique_appends': row['representative_anchor_minimum_dwell_unique_appends'],
                'exact_dwell_band': [
                    row['exact_dwell_band_start_unique_appends'],
                    row['exact_dwell_band_end_unique_appends'],
                ],
            }
        )
    return rows


def _build_report() -> dict[str, Any]:
    baseline = _trusted_repeat_baseline()
    tiers = _uncertainty_tier_rows()
    comparisons = _comparison_rows(baseline, tiers)
    comparison_by_tier = {row['to_tier']: row for row in comparisons}

    report = {
        'focus': 'Price repeat-estimate uncertainty as an explicit operating premium by comparing the trusted 4-transition rewrite-budgeted plan against the exact uncertainty-safe compact repeat-sidecar tiers.',
        'headline_findings': {
            'trusted_repeat_baseline_transition_count': baseline['selected_transition_count'],
            'trusted_repeat_baseline_transition_checkpoints_unique_appends': baseline['transition_checkpoints_unique_appends'],
            'trusted_repeat_baseline_preserved_gain_share_of_full_dynamic_savings_at_0_18_repeats': baseline['preserved_gain_share_of_full_dynamic_savings'],
            'near_optimal_uncertainty_premium_over_trusted_repeat': {
                'hard_cap_delta': comparison_by_tier['near_optimal']['hard_cap_delta'],
                'net_checkpoint_count_delta': comparison_by_tier['near_optimal']['net_checkpoint_count_delta'],
                'focal_gain_share_delta_at_0_18_repeats': comparison_by_tier['near_optimal']['focal_gain_share_delta_at_0_18_repeats'],
                'checkpoints_added_unique_appends': comparison_by_tier['near_optimal']['checkpoints_added_unique_appends'],
                'checkpoints_dropped_unique_appends': comparison_by_tier['near_optimal']['checkpoints_dropped_unique_appends'],
            },
            'lower_guarantee_uncertainty_premium_over_trusted_repeat': {
                'hard_cap_delta': comparison_by_tier['lower_guarantee']['hard_cap_delta'],
                'net_checkpoint_count_delta': comparison_by_tier['lower_guarantee']['net_checkpoint_count_delta'],
                'focal_gain_share_delta_at_0_18_repeats': comparison_by_tier['lower_guarantee']['focal_gain_share_delta_at_0_18_repeats'],
                'checkpoints_added_unique_appends': comparison_by_tier['lower_guarantee']['checkpoints_added_unique_appends'],
                'checkpoints_dropped_unique_appends': comparison_by_tier['lower_guarantee']['checkpoints_dropped_unique_appends'],
            },
            'near_exact_uncertainty_premium_over_trusted_repeat': {
                'hard_cap_delta': comparison_by_tier['near_exact']['hard_cap_delta'],
                'net_checkpoint_count_delta': comparison_by_tier['near_exact']['net_checkpoint_count_delta'],
                'focal_gain_share_delta_at_0_18_repeats': comparison_by_tier['near_exact']['focal_gain_share_delta_at_0_18_repeats'],
                'checkpoints_added_unique_appends': comparison_by_tier['near_exact']['checkpoints_added_unique_appends'],
                'checkpoints_dropped_unique_appends': comparison_by_tier['near_exact']['checkpoints_dropped_unique_appends'],
            },
            'uncertainty_is_not_a_monotone_transition_tax': comparison_by_tier['lower_guarantee']['hard_cap_delta'] < 0,
            'near_optimal_is_smallest_upgrade_that_adds_band_robustness_without_losing_focal_gain': True,
            'main_rule': 'treat repeat-estimate uncertainty as a priced operating premium: the exact 0.95 lane buys band-robustness over the trusted 4-transition plan for only +1 hard-cap step and net +4 checkpoints while improving focal 0.18 preservation by 0.012062, whereas the relaxed exact 0.85 lane is actually cheaper on transition cap but pays for that with lower focal preservation.',
        },
        'decision_rules': [
            'When repeat estimates are truly trusted and rewrites are tightly capped at four, the trusted rewrite-budgeted plan remains the smallest exact trusted-repeat operating mode.',
            'When repeat estimates are not trusted across the current 0.15-0.25 band, price the uncertainty upgrade explicitly instead of treating it as folklore.',
            'Use the exact 0.95 lane as the main uncertainty-safe premium: it costs only one extra hard-cap step relative to the trusted 4-transition plan and keeps focal 0.18 preservation higher, while also covering the full current repeat band.',
            'Use the exact 0.85 lane only when the archive intentionally wants the cheaper uncertainty-safe transition cap and can afford the focal-performance drop.',
            'Reserve the exact 0.99 lane for precision preservation objectives, because its uncertainty premium over the trusted 4-transition plan is structurally large: +7 cap steps and net +10 checkpoints.',
        ],
        'trusted_repeat_baseline': baseline,
        'uncertainty_tier_rows': tiers,
        'comparison_rows': comparisons,
        'source_reports': [
            str(CONTROL_CARD_REPORT.relative_to(ROOT)),
            str(CHECKPOINT_REPORT.relative_to(ROOT)),
            str(CAP_STAIRCASE_REPORT.relative_to(ROOT)),
            str(UNCERTAINTY_CHECKPOINT_REPORT.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }
    return report


def _render_md(report: dict[str, Any]) -> str:
    findings = report['headline_findings']
    baseline = report['trusted_repeat_baseline']
    lines = [
        '# Rematch Proxy Delta Decision Packet Compact Repeat-State Uncertainty Premium vs Trusted Repeat Snapshot — 2026-03-08',
        '',
        '## Focus',
        f"- {report['focus']}",
        '',
        '## Headline findings',
        f"- trusted-repeat baseline: `{baseline['selected_transition_count']}` transitions, `{baseline['transition_checkpoint_count']}` checkpoints, focal preserved gain share `{baseline['preserved_gain_share_of_full_dynamic_savings']}` at `0.18` repeats.",
        f"- near-optimal `0.95` uncertainty premium: `{findings['near_optimal_uncertainty_premium_over_trusted_repeat']}`.",
        f"- relaxed `0.85` uncertainty premium: `{findings['lower_guarantee_uncertainty_premium_over_trusted_repeat']}`.",
        f"- near-exact `0.99` uncertainty premium: `{findings['near_exact_uncertainty_premium_over_trusted_repeat']}`.",
        f"- uncertainty is not a monotone transition tax: `uncertainty_is_not_a_monotone_transition_tax = {findings['uncertainty_is_not_a_monotone_transition_tax']}`.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Trusted-repeat baseline',
        '| mode | repeat scope | focal repeats | preserved gain share at 0.18 | transitions | checkpoints | interval summary |',
        '|---|---|---:|---:|---:|---|---|',
        f"| {baseline['mode']} | {baseline['repeat_scope']} | {baseline['focal_expected_repeat_lookups']} | {baseline['preserved_gain_share_of_full_dynamic_savings']} | {baseline['selected_transition_count']} | {baseline['transition_checkpoints_unique_appends']} | {baseline['interval_summary']} |",
        '',
        '## Exact uncertainty tiers compared against the trusted-repeat baseline',
        '| tier | min gain floor | focal gain at 0.18 | hard cap | dwell band | representative anchor | checkpoint union |',
        '|---|---:|---:|---:|---|---:|---|',
    ]
    for row in report['uncertainty_tier_rows']:
        lines.append(
            f"| {row['tier']} | {row['minimum_gain_share_of_full_dynamic_savings']} | {row['focal_gain_share_of_full_dynamic_savings_at_0_18_repeats']} | {row['exact_hard_cap']} | {row['exact_dwell_band_start_unique_appends']}–{row['exact_dwell_band_end_unique_appends']} | {row['representative_anchor_minimum_dwell_unique_appends']} | {row['union_transition_checkpoints_unique_appends']} |"
        )
    lines.extend([
        '',
        '## Uncertainty premium relative to the trusted-repeat baseline',
        '| target tier | hard-cap delta | net checkpoint delta | focal gain delta at 0.18 | checkpoints added | checkpoints dropped |',
        '|---|---:|---:|---:|---|---|',
    ])
    for row in report['comparison_rows']:
        lines.append(
            f"| {row['to_tier']} | {row['hard_cap_delta']} | {row['net_checkpoint_count_delta']} | {row['focal_gain_share_delta_at_0_18_repeats']} | {row['checkpoints_added_unique_appends']} | {row['checkpoints_dropped_unique_appends']} |"
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
    for src in report['source_reports']:
        lines.append(f'- `{src}`')
    return '\n'.join(lines) + '\n'


def main() -> None:
    report = _build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2) + '\n')
    OUT_MD.write_text(_render_md(report))
    print(f'wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'wrote {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
