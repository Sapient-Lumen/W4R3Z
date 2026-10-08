#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_tolerance_staircase_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_tolerance_staircase_snapshot_20260308.md'
UPGRADE_TARIFF_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_upgrade_tariff_snapshot_20260308.json'


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _tolerance_rows() -> list[dict[str, Any]]:
    tariff = _load(UPGRADE_TARIFF_REPORT)
    rows: list[dict[str, Any]] = []
    for row in tariff['tier_rows']:
        start = int(row['exact_dwell_band_start_unique_appends'])
        end = int(row['exact_dwell_band_end_unique_appends'])
        anchor = int(row['representative_anchor_minimum_dwell_unique_appends'])
        width = int(row['exact_dwell_band_width_unique_appends'])
        left_slack = anchor - start
        right_slack = end - anchor
        rows.append(
            {
                'tier': str(row['tier']),
                'minimum_gain_share_of_full_dynamic_savings': float(row['minimum_gain_share_of_full_dynamic_savings']),
                'exact_hard_cap': int(row['exact_hard_cap']),
                'representative_anchor_minimum_dwell_unique_appends': anchor,
                'exact_dwell_band_start_unique_appends': start,
                'exact_dwell_band_end_unique_appends': end,
                'exact_dwell_band_width_unique_appends': width,
                'anchor_left_slack_unique_appends': left_slack,
                'anchor_right_slack_unique_appends': right_slack,
                'minimum_anchor_slack_unique_appends': min(left_slack, right_slack),
                'retuning_error_budget_unique_appends': width - 1,
                'union_transition_checkpoint_count': int(row['union_transition_checkpoint_count']),
            }
        )
    return rows


def _make_shift(from_row: dict[str, Any], to_row: dict[str, Any]) -> dict[str, Any]:
    return {
        'from_tier': from_row['tier'],
        'to_tier': to_row['tier'],
        'gain_floor_delta': round(
            to_row['minimum_gain_share_of_full_dynamic_savings'] - from_row['minimum_gain_share_of_full_dynamic_savings'], 6
        ),
        'hard_cap_delta': to_row['exact_hard_cap'] - from_row['exact_hard_cap'],
        'checkpoint_count_delta': to_row['union_transition_checkpoint_count'] - from_row['union_transition_checkpoint_count'],
        'dwell_band_width_delta_unique_appends': (
            to_row['exact_dwell_band_width_unique_appends'] - from_row['exact_dwell_band_width_unique_appends']
        ),
        'retuning_error_budget_delta_unique_appends': (
            to_row['retuning_error_budget_unique_appends'] - from_row['retuning_error_budget_unique_appends']
        ),
        'minimum_anchor_slack_delta_unique_appends': (
            to_row['minimum_anchor_slack_unique_appends'] - from_row['minimum_anchor_slack_unique_appends']
        ),
        'anchor_shift_unique_appends': (
            to_row['representative_anchor_minimum_dwell_unique_appends']
            - from_row['representative_anchor_minimum_dwell_unique_appends']
        ),
    }


def _build_report() -> dict[str, Any]:
    rows = _tolerance_rows()
    by_tier = {row['tier']: row for row in rows}
    lower = by_tier['lower_guarantee']
    near_optimal = by_tier['near_optimal']
    near_exact = by_tier['near_exact']

    lower_to_near_optimal = _make_shift(lower, near_optimal)
    near_optimal_to_near_exact = _make_shift(near_optimal, near_exact)
    lower_to_near_exact = _make_shift(lower, near_exact)

    near_exact_is_precision_mode = (
        near_exact['exact_dwell_band_width_unique_appends'] == 1
        and near_exact['minimum_anchor_slack_unique_appends'] == 0
        and near_exact['retuning_error_budget_unique_appends'] == 0
    )
    near_optimal_is_tolerance_band = near_optimal['minimum_anchor_slack_unique_appends'] >= 5
    lower_is_widest_certified_band = (
        lower['exact_dwell_band_width_unique_appends'] > near_optimal['exact_dwell_band_width_unique_appends']
        > near_exact['exact_dwell_band_width_unique_appends']
    )

    report = {
        'focus': 'Summarize the certified uncertainty tiers as a dwell-tolerance staircase so inheritors can see how much tuning slack each guarantee tier really leaves before a lane change becomes necessary.',
        'headline_findings': {
            'near_exact_is_single_point_precision_mode': near_exact_is_precision_mode,
            'near_optimal_is_true_tolerance_band': near_optimal_is_tolerance_band,
            'lower_guarantee_is_widest_certified_band': lower_is_widest_certified_band,
            'exact_dwell_band_widths_by_descending_guarantee': [
                near_exact['exact_dwell_band_width_unique_appends'],
                near_optimal['exact_dwell_band_width_unique_appends'],
                lower['exact_dwell_band_width_unique_appends'],
            ],
            'minimum_anchor_slacks_by_descending_guarantee': [
                near_exact['minimum_anchor_slack_unique_appends'],
                near_optimal['minimum_anchor_slack_unique_appends'],
                lower['minimum_anchor_slack_unique_appends'],
            ],
            'near_optimal_to_near_exact_band_width_delta_unique_appends': near_optimal_to_near_exact['dwell_band_width_delta_unique_appends'],
            'near_optimal_to_near_exact_minimum_anchor_slack_delta_unique_appends': near_optimal_to_near_exact['minimum_anchor_slack_delta_unique_appends'],
            'lower_to_near_optimal_band_width_delta_unique_appends': lower_to_near_optimal['dwell_band_width_delta_unique_appends'],
            'lower_to_near_optimal_minimum_anchor_slack_delta_unique_appends': lower_to_near_optimal['minimum_anchor_slack_delta_unique_appends'],
            'main_rule': 'treat the exact 0.99 lane as a precision mode, not a forgiving operating band: it collapses the certified dwell width from 11 at 0.95 to 1 at 0.99 and deletes all anchor slack, whereas the 0.95 and 0.85 tiers remain true tolerance bands with at least five dwell steps of slack on both sides of their representative anchors.',
        },
        'decision_rules': [
            'Use the exact 0.95 lane when the archive wants strong uncertainty safety without fragile retuning: anchor 13 sits inside an 8–18 band with five dwell steps of slack on each side.',
            'Use the exact 0.85 lane when even more tuning forgiveness matters and the weaker guarantee is acceptable: anchor 25 sits inside a 19–32 band with six steps of left slack and seven of right slack.',
            'Reserve the exact 0.99 lane for deliberate precision deployments only: anchor 2 is the whole certified band, so any dwell drift leaves the lane immediately.',
            'When a future implementor talks about “just tightening the guarantee a little,” remember that the 0.95 -> 0.99 move is also a tolerance collapse: -10 dwell-width steps and -5 minimum anchor-slack steps.',
        ],
        'tier_rows': rows,
        'tolerance_shift_rows': [lower_to_near_optimal, near_optimal_to_near_exact, lower_to_near_exact],
        'source_reports': [str(UPGRADE_TARIFF_REPORT.relative_to(ROOT))],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }
    return report


def _render_md(report: dict[str, Any]) -> str:
    findings = report['headline_findings']
    lines = [
        '# Rematch Proxy Delta Decision Packet Compact Repeat-State Uncertainty Dwell-Tolerance Staircase Snapshot — 2026-03-08',
        '',
        '## Focus',
        f"- {report['focus']}",
        '',
        '## Headline findings',
        f"- near-exact `0.99` is a single-point precision mode: `near_exact_is_single_point_precision_mode = {findings['near_exact_is_single_point_precision_mode']}`.",
        f"- near-optimal `0.95` remains a true tolerance band: `near_optimal_is_true_tolerance_band = {findings['near_optimal_is_true_tolerance_band']}`.",
        f"- relaxed `0.85` is the widest certified band: `lower_guarantee_is_widest_certified_band = {findings['lower_guarantee_is_widest_certified_band']}`.",
        f"- exact dwell-band widths by descending guarantee are `{findings['exact_dwell_band_widths_by_descending_guarantee']}` and minimum anchor slacks are `{findings['minimum_anchor_slacks_by_descending_guarantee']}`.",
        f"- tightening `0.95 -> 0.99` changes width by `{findings['near_optimal_to_near_exact_band_width_delta_unique_appends']}` and minimum anchor slack by `{findings['near_optimal_to_near_exact_minimum_anchor_slack_delta_unique_appends']}`.",
        f"- tightening `0.85 -> 0.95` changes width by `{findings['lower_to_near_optimal_band_width_delta_unique_appends']}` and minimum anchor slack by `{findings['lower_to_near_optimal_minimum_anchor_slack_delta_unique_appends']}`.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Exact tier tolerance rows',
        '| tier | min gain floor | hard cap | anchor dwell | dwell band | band width | left slack | right slack | minimum slack | retuning error budget | checkpoint count |',
        '|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|',
    ]
    for row in report['tier_rows']:
        lines.append(
            f"| {row['tier']} | {row['minimum_gain_share_of_full_dynamic_savings']} | {row['exact_hard_cap']} | {row['representative_anchor_minimum_dwell_unique_appends']} | {row['exact_dwell_band_start_unique_appends']}–{row['exact_dwell_band_end_unique_appends']} | {row['exact_dwell_band_width_unique_appends']} | {row['anchor_left_slack_unique_appends']} | {row['anchor_right_slack_unique_appends']} | {row['minimum_anchor_slack_unique_appends']} | {row['retuning_error_budget_unique_appends']} | {row['union_transition_checkpoint_count']} |"
        )
    lines.extend([
        '',
        '## Tolerance shifts between exact tiers',
        '| shift | gain floor delta | hard-cap delta | checkpoint delta | width delta | retuning budget delta | minimum slack delta | anchor shift |',
        '|---|---:|---:|---:|---:|---:|---:|---:|',
    ])
    for row in report['tolerance_shift_rows']:
        lines.append(
            f"| {row['from_tier']} -> {row['to_tier']} | {row['gain_floor_delta']} | {row['hard_cap_delta']} | {row['checkpoint_count_delta']} | {row['dwell_band_width_delta_unique_appends']} | {row['retuning_error_budget_delta_unique_appends']} | {row['minimum_anchor_slack_delta_unique_appends']} | {row['anchor_shift_unique_appends']} |"
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
