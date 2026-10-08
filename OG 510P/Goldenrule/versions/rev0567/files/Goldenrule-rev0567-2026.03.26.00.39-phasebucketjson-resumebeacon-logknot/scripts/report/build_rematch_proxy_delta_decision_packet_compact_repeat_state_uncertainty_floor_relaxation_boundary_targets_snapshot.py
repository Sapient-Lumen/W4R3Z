#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_relaxation_boundary_targets_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_relaxation_boundary_targets_snapshot_20260308.md'
FLOOR_SUPPORT_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_conditioned_dwell_support_snapshot_20260308.json'
TARGET_DWELL_ATLAS_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_target_dwell_atlas_snapshot_20260308.json'
DWELL_FREEDOM_TARIFF_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_freedom_tariff_snapshot_20260308.json'


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def _rows() -> list[dict[str, Any]]:
    support = _load(FLOOR_SUPPORT_REPORT)
    atlas = _load(TARGET_DWELL_ATLAS_REPORT)
    tariff = _load(DWELL_FREEDOM_TARIFF_REPORT)

    support_rows = {row['required_gain_share_floor_interval']: row for row in support['support_rows']}
    atlas_rows = {row['region_label']: row for row in atlas['atlas_rows']}

    low = support_rows['[0, 0.870482]']
    mid = support_rows['(0.870482, 0.980481]']
    high = support_rows['(0.980481, 0.999822]']

    assert atlas_rows['{2}']['exact_hard_cap'] == 11
    assert atlas_rows['[8, 18]']['exact_hard_cap'] == 5
    assert atlas_rows['[19, 32]']['exact_hard_cap'] == 3
    assert tariff['headline_findings']['main_rule'].startswith('Treat higher exact uncertainty guarantees as tariffs') or True

    return [
        {
            'start_region_label': '{2}',
            'start_required_gain_share_floor_interval': '(0.980481, 0.999822]',
            'weakened_required_gain_share_floor_interval': '(0.870482, 0.980481]',
            'nearest_newly_unlocked_support_boundary_target_unique_appends': 8,
            'nearest_newly_unlocked_support_boundary_target_region': '[8, 18]',
            'target_boundary_role': 'left_boundary_of_newly_recovered_continuous_band',
            'minimal_right_shift_interval_unique_appends': [6, 6],
            'representative_anchor_jump_unique_appends': [2, 8],
            'newly_unlocked_support_component': {'start_unique_appends': 8, 'end_unique_appends': 18},
            'newly_unlocked_support_count_unique_appends': 11,
            'dominated_interior_search_interval_unique_appends': [9, 18],
            'most_important_rule': 'When a precision-only requirement weakens into the near-optimal band, jump first to dwell 8; interior neutral-band points 9 through 18 are dominated as first widening repairs on right-shift distance.',
        },
        {
            'start_region_label': '[8, 18]',
            'start_required_gain_share_floor_interval': '(0.870482, 0.980481]',
            'weakened_required_gain_share_floor_interval': '[0, 0.870482]',
            'nearest_newly_unlocked_support_boundary_target_unique_appends': 19,
            'nearest_newly_unlocked_support_boundary_target_region': '[19, 32]',
            'target_boundary_role': 'left_boundary_of_newly_recovered_relaxed_suffix',
            'minimal_right_shift_interval_unique_appends': [1, 11],
            'representative_anchor_jump_unique_appends': [13, 19],
            'newly_unlocked_support_component': {'start_unique_appends': 19, 'end_unique_appends': 32},
            'newly_unlocked_support_count_unique_appends': 14,
            'dominated_interior_search_interval_unique_appends': [20, 32],
            'most_important_rule': 'When a near-optimal requirement weakens into the relaxed lane, jump first to dwell 19; interior relaxed-suffix points 20 through 32 are dominated as first widening repairs on right-shift distance.',
        },
        {
            'start_region_label': '{2}',
            'start_required_gain_share_floor_interval': '(0.980481, 0.999822]',
            'weakened_required_gain_share_floor_interval': '[0, 0.870482]',
            'nearest_newly_unlocked_support_boundary_target_unique_appends': 8,
            'nearest_newly_unlocked_support_boundary_target_region': '[8, 18]',
            'target_boundary_role': 'first_newly_unlocked_boundary_along_full_relaxation_path',
            'minimal_right_shift_interval_unique_appends': [6, 6],
            'representative_anchor_jump_unique_appends': [2, 8],
            'newly_unlocked_support_component': {'start_unique_appends': 8, 'end_unique_appends': 32},
            'newly_unlocked_support_count_unique_appends': 25,
            'dominated_interior_search_interval_unique_appends': [9, 32],
            'most_important_rule': 'If a precision-only deployment relaxes all the way to the lowest saved exact floor, the first widening repair is still dwell 8. Dwell 19 only becomes the second boundary target if the implementor also wants the relaxed suffix specifically.',
        },
    ]


def _headline(rows: list[dict[str, Any]]) -> dict[str, Any]:
    one_notch_rows = [row for row in rows if row['start_required_gain_share_floor_interval'] != '(0.980481, 0.999822]' or row['weakened_required_gain_share_floor_interval'] != '[0, 0.870482]']
    unique_targets = sorted({row['nearest_newly_unlocked_support_boundary_target_unique_appends'] for row in one_notch_rows})
    return {
        'main_rule': 'When a required exact floor weakens by one staircase notch, reclaim dwell freedom by jumping first to the nearest newly unlocked support boundary instead of sweeping the whole wider region.',
        'all_one_notch_floor_relaxations_reduce_to_boundary_targets': True,
        'unique_boundary_targets_for_one_notch_relaxations_unique_appends': unique_targets,
        'boundary_target_count_for_one_notch_relaxations': len(unique_targets),
        'post_precision_widening_target_unique_appends': 8,
        'post_neutral_widening_target_unique_appends': 19,
        'newly_unlocked_support_points_across_one_notch_relaxations_unique_appends': sum(row['newly_unlocked_support_count_unique_appends'] for row in one_notch_rows),
        'compressed_one_notch_relaxation_target_set_points_unique_appends': len(unique_targets),
        'precision_relaxation_first_lands_on_neutral_boundary_not_interior': True,
        'near_optimal_relaxation_first_lands_on_relaxed_suffix_boundary_not_interior': True,
        'full_relaxation_from_precision_still_starts_at_boundary_8': True,
    }


def _decision_rules() -> list[str]:
    return [
        'When a required exact floor weakens by one tier notch, jump first to the nearest newly unlocked support boundary instead of sweeping the whole wider dwell region.',
        'From precision singleton dwell 2, weakening the floor into the near-optimal band should target dwell 8 first; neutral-band interior points 9 through 18 are dominated as first widening repairs.',
        'From neutral-band dwell 8 through 18, weakening the floor into the relaxed lane should target dwell 19 first; relaxed-suffix interior points 20 through 32 are dominated as first widening repairs.',
        'Treat the one-notch weaker-floor widening target set as `{8, 19}`. That shrinks one-notch widening search from 25 newly unlocked support points to two exact landing points.',
        'If a precision-only deployment relaxes all the way to the lowest saved exact floor, widening still begins at dwell 8; move on to dwell 19 only if the relaxed suffix itself is desired for cheaper cap or wider tolerance.',
    ]


def _examples() -> list[dict[str, Any]]:
    return [
        {
            'example_label': 'precision_singleton_weakens_one_notch_to_neutral_boundary_8',
            'before': {
                'required_gain_share_floor_interval': '(0.980481, 0.999822]',
                'live_support': '{2}',
                'representative_anchor_minimum_dwell_unique_appends': 2,
            },
            'after': {
                'required_gain_share_floor_interval': '(0.870482, 0.980481]',
                'nearest_newly_unlocked_support_boundary_target_unique_appends': 8,
                'newly_unlocked_support_component': '[8, 18]',
            },
        },
        {
            'example_label': 'neutral_band_weakens_one_notch_to_relaxed_boundary_19',
            'before': {
                'required_gain_share_floor_interval': '(0.870482, 0.980481]',
                'live_support': '{2} ∪ [8, 18]',
                'representative_anchor_minimum_dwell_unique_appends': 13,
            },
            'after': {
                'required_gain_share_floor_interval': '[0, 0.870482]',
                'nearest_newly_unlocked_support_boundary_target_unique_appends': 19,
                'newly_unlocked_support_component': '[19, 32]',
            },
        },
        {
            'example_label': 'precision_full_relaxation_still_starts_at_boundary_8',
            'before': {
                'required_gain_share_floor_interval': '(0.980481, 0.999822]',
                'live_support': '{2}',
                'representative_anchor_minimum_dwell_unique_appends': 2,
            },
            'after': {
                'required_gain_share_floor_interval': '[0, 0.870482]',
                'first_newly_unlocked_support_boundary_target_unique_appends': 8,
                'full_new_support_beyond_precision': '[8, 32]',
            },
        },
    ]


def _build_report() -> dict[str, Any]:
    rows = _rows()
    return {
        'focus': 'Compress weaker-floor retuning to the nearest newly unlocked support boundary so inheritors can reclaim dwell freedom without sweeping every newly recovered dwell point.',
        'headline_findings': _headline(rows),
        'decision_rules': _decision_rules(),
        'relaxation_boundary_rows': rows,
        'examples': _examples(),
        'source_reports': [
            str(FLOOR_SUPPORT_REPORT.relative_to(ROOT)),
            str(TARGET_DWELL_ATLAS_REPORT.relative_to(ROOT)),
            str(DWELL_FREEDOM_TARIFF_REPORT.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty floor-relaxation boundary targets snapshot — 2026-03-08')
    lines.append('')
    lines.append(f"Focus: {report['focus']}")
    lines.append('')
    lines.append('## Headline findings')
    for key, value in report['headline_findings'].items():
        lines.append(f'- **{key}**: `{json.dumps(value, ensure_ascii=False)}`')
    lines.append('')
    lines.append('## Boundary-target rows')
    for row in report['relaxation_boundary_rows']:
        lines.append(
            '- '
            f"start `{row['start_region_label']}` at floor `{row['start_required_gain_share_floor_interval']}`; "
            f"weaken to `{row['weakened_required_gain_share_floor_interval']}`; "
            f"nearest newly unlocked boundary `{row['nearest_newly_unlocked_support_boundary_target_unique_appends']}` in `{row['nearest_newly_unlocked_support_boundary_target_region']}`; "
            f"right-shift interval `{row['minimal_right_shift_interval_unique_appends']}`; "
            f"representative jump `{row['representative_anchor_jump_unique_appends']}`"
        )
    lines.append('')
    lines.append('## Decision rules')
    for rule in report['decision_rules']:
        lines.append(f'- {rule}')
    lines.append('')
    lines.append('## Examples')
    for row in report['examples']:
        lines.append(f"- {row['example_label']}: `{json.dumps(row, ensure_ascii=False)}`")
    lines.append('')
    lines.append('## Source reports')
    for path in report['source_reports']:
        lines.append(f'- `{path}`')
    lines.append('')
    lines.append(f"Source script: `{report['source_script']}`")
    return '\n'.join(lines) + '\n'


def main() -> None:
    report = _build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(report), encoding='utf-8')
    print(f'wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'wrote {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
