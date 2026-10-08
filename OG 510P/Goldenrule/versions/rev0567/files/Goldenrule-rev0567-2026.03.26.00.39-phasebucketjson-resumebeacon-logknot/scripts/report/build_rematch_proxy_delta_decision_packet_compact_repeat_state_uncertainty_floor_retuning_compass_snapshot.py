#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_retuning_compass_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_retuning_compass_snapshot_20260308.md'
UPGRADE_BOUNDARY_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_upgrade_boundary_targets_snapshot_20260308.json'
RELAXATION_BOUNDARY_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_relaxation_boundary_targets_snapshot_20260308.json'
TARGET_DWELL_ATLAS_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_target_dwell_atlas_snapshot_20260308.json'
FLOOR_SUPPORT_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_conditioned_dwell_support_snapshot_20260308.json'


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def _compass_points() -> list[dict[str, Any]]:
    atlas = _load(TARGET_DWELL_ATLAS_REPORT)
    atlas_rows = {row['region_label']: row for row in atlas['atlas_rows']}
    return [
        {
            'dwell_unique_appends': 2,
            'region_label': '{2}',
            'role': 'precision_singleton',
            'exact_floor_ceiling': atlas_rows['{2}']['maximum_actual_certified_gain_share_floor_of_full_dynamic_savings'],
            'exact_hard_cap': atlas_rows['{2}']['exact_hard_cap'],
            'mode_specific_checkpoint_count': atlas_rows['{2}']['mode_specific_checkpoint_count'],
            'most_important_rule': 'Dwell 2 is the only current exact landing point above floor 0.980481 and the terminal strengthening target for every saved floor-driven upgrade path.',
        },
        {
            'dwell_unique_appends': 8,
            'region_label': '[8, 18]',
            'role': 'neutral_band_entry_boundary',
            'exact_floor_ceiling': atlas_rows['[8, 18]']['maximum_actual_certified_gain_share_floor_of_full_dynamic_savings'],
            'exact_hard_cap': atlas_rows['[8, 18]']['exact_hard_cap'],
            'mode_specific_checkpoint_count': atlas_rows['[8, 18]']['mode_specific_checkpoint_count'],
            'most_important_rule': 'Dwell 8 is the first newly unlocked non-fragile landing point when a precision-only requirement weakens.',
        },
        {
            'dwell_unique_appends': 18,
            'region_label': '[8, 18]',
            'role': 'neutral_band_exit_boundary_for_strengthening',
            'exact_floor_ceiling': atlas_rows['[8, 18]']['maximum_actual_certified_gain_share_floor_of_full_dynamic_savings'],
            'exact_hard_cap': atlas_rows['[8, 18]']['exact_hard_cap'],
            'mode_specific_checkpoint_count': atlas_rows['[8, 18]']['mode_specific_checkpoint_count'],
            'most_important_rule': 'Dwell 18 is the first stronger non-precision landing point when a relaxed-suffix request must leave [19,32] but does not yet need singleton precision.',
        },
        {
            'dwell_unique_appends': 19,
            'region_label': '[19, 32]',
            'role': 'relaxed_suffix_entry_boundary',
            'exact_floor_ceiling': atlas_rows['[19, 32]']['maximum_actual_certified_gain_share_floor_of_full_dynamic_savings'],
            'exact_hard_cap': atlas_rows['[19, 32]']['exact_hard_cap'],
            'mode_specific_checkpoint_count': atlas_rows['[19, 32]']['mode_specific_checkpoint_count'],
            'most_important_rule': 'Dwell 19 is the first newly unlocked relaxed landing point when a neutral-band requirement weakens into the lower-guarantee lane.',
        },
    ]


def _transition_rows() -> list[dict[str, Any]]:
    upgrade = _load(UPGRADE_BOUNDARY_REPORT)
    relax = _load(RELAXATION_BOUNDARY_REPORT)

    upgrade_rows = {(row['start_region_label'], row['required_gain_share_floor_interval']): row for row in upgrade['upgrade_boundary_rows']}
    relax_rows = {(row['start_region_label'], row['weakened_required_gain_share_floor_interval']): row for row in relax['relaxation_boundary_rows']}

    return [
        {
            'direction': 'strengthen',
            'start_region_label': '[19, 32]',
            'target_floor_interval': '(0.870482, 0.980481]',
            'first_compass_target_unique_appends': upgrade_rows[('[19, 32]', '(0.870482, 0.980481]')]['nearest_stronger_live_support_boundary_target_unique_appends'],
            'first_compass_target_role': 'neutral_band_exit_boundary_for_strengthening',
            'distance_interval_unique_appends': upgrade_rows[('[19, 32]', '(0.870482, 0.980481]')]['minimal_left_shift_interval_unique_appends'],
            'most_important_rule': 'The first stronger non-precision repair from the relaxed suffix lands on compass point 18, not on neutral-band interior points 8–17.',
        },
        {
            'direction': 'strengthen',
            'start_region_label': '[19, 32]',
            'target_floor_interval': '(0.980481, 0.999822]',
            'first_compass_target_unique_appends': upgrade_rows[('[19, 32]', '(0.980481, 0.999822]')]['nearest_stronger_live_support_boundary_target_unique_appends'],
            'first_compass_target_role': 'precision_singleton',
            'distance_interval_unique_appends': upgrade_rows[('[19, 32]', '(0.980481, 0.999822]')]['minimal_left_shift_interval_unique_appends'],
            'most_important_rule': 'High-floor strengthening from the relaxed suffix bypasses the neutral band entirely and lands on precision singleton 2.',
        },
        {
            'direction': 'strengthen',
            'start_region_label': '[8, 18]',
            'target_floor_interval': '(0.980481, 0.999822]',
            'first_compass_target_unique_appends': upgrade_rows[('[8, 18]', '(0.980481, 0.999822]')]['nearest_stronger_live_support_boundary_target_unique_appends'],
            'first_compass_target_role': 'precision_singleton',
            'distance_interval_unique_appends': upgrade_rows[('[8, 18]', '(0.980481, 0.999822]')]['minimal_left_shift_interval_unique_appends'],
            'most_important_rule': 'Any strengthening beyond the neutral band collapses directly to singleton 2.',
        },
        {
            'direction': 'weaken',
            'start_region_label': '{2}',
            'target_floor_interval': '(0.870482, 0.980481]',
            'first_compass_target_unique_appends': relax_rows[('{2}', '(0.870482, 0.980481]')]['nearest_newly_unlocked_support_boundary_target_unique_appends'],
            'first_compass_target_role': 'neutral_band_entry_boundary',
            'distance_interval_unique_appends': relax_rows[('{2}', '(0.870482, 0.980481]')]['minimal_right_shift_interval_unique_appends'],
            'most_important_rule': 'The first weakening repair from precision lands on dwell 8, not on neutral-band interior points 9–18.',
        },
        {
            'direction': 'weaken',
            'start_region_label': '[8, 18]',
            'target_floor_interval': '[0, 0.870482]',
            'first_compass_target_unique_appends': relax_rows[('[8, 18]', '[0, 0.870482]')]['nearest_newly_unlocked_support_boundary_target_unique_appends'],
            'first_compass_target_role': 'relaxed_suffix_entry_boundary',
            'distance_interval_unique_appends': relax_rows[('[8, 18]', '[0, 0.870482]')]['minimal_right_shift_interval_unique_appends'],
            'most_important_rule': 'The first weakening repair from the neutral band lands on dwell 19, not on relaxed-suffix interior points 20–32.',
        },
        {
            'direction': 'weaken',
            'start_region_label': '{2}',
            'target_floor_interval': '[0, 0.870482]',
            'first_compass_target_unique_appends': relax_rows[('{2}', '[0, 0.870482]')]['nearest_newly_unlocked_support_boundary_target_unique_appends'],
            'first_compass_target_role': 'neutral_band_entry_boundary',
            'distance_interval_unique_appends': relax_rows[('{2}', '[0, 0.870482]')]['minimal_right_shift_interval_unique_appends'],
            'most_important_rule': 'Even full relaxation from precision still starts at dwell 8; dwell 19 becomes relevant only after that first widening step.',
        },
    ]


def _headline(compass_points: list[dict[str, Any]], transition_rows: list[dict[str, Any]]) -> dict[str, Any]:
    support = _load(FLOOR_SUPPORT_REPORT)
    widest_support = next(row for row in support['support_rows'] if row['required_gain_share_floor_interval'] == '[0, 0.870482]')
    full_live_support_points = widest_support['supported_dwell_count_unique_appends']
    strengthen_targets = sorted({row['first_compass_target_unique_appends'] for row in transition_rows if row['direction'] == 'strengthen'})
    weaken_targets = sorted({row['first_compass_target_unique_appends'] for row in transition_rows if row['direction'] == 'weaken'})
    compass = sorted(point['dwell_unique_appends'] for point in compass_points)
    return {
        'main_rule': 'Treat floor-driven exact uncertainty retuning as movement among four boundary compass points instead of a search over every live dwell value.',
        'four_point_compass_unique_appends': compass,
        'strengthening_targets_unique_appends': strengthen_targets,
        'weakening_targets_unique_appends': weaken_targets,
        'all_first_floor_driven_repairs_land_on_compass_points': True,
        'full_live_support_points_unique_appends': full_live_support_points,
        'compressed_first_step_search_points_unique_appends': len(compass),
        'search_compression_factor': round(full_live_support_points / len(compass), 3),
        'precision_singleton_is_terminal_strengthening_point': True,
        'neutral_band_is_entered_at_8_and_exited_at_18_under_floor_changes': True,
        'relaxed_suffix_is_entered_at_19_under_floor_weakening': True,
    }


def _decision_rules() -> list[str]:
    return [
        'For floor-driven retuning, start from the four-point compass `{2, 8, 18, 19}` before you consider any interior dwell values.',
        'Use `{18, 2}` for stronger-floor repairs: 18 is the first stronger non-precision landing point, and 2 is the terminal precision landing point.',
        'Use `{8, 19}` for weaker-floor widening: 8 is the first non-fragile landing point from precision, and 19 is the first relaxed landing point from the neutral band.',
        'Treat interior dwells as second-step or policy-specific refinements only after the relevant compass target has been evaluated.',
        'This rule is specific to floor-driven retuning on the current saved exact menu; if target dwell is physically fixed or the frontier changes, re-run the oracle/frontier builders instead of forcing the compass beyond its support.',
    ]


def _examples() -> list[dict[str, Any]]:
    return [
        {
            'example_label': 'stronger_floor_from_relaxed_suffix_mid_band_targets_18',
            'start_region_label': '[19, 32]',
            'required_floor_interval_after_change': '(0.870482, 0.980481]',
            'first_compass_target_unique_appends': 18,
        },
        {
            'example_label': 'stronger_floor_beyond_neutral_band_targets_2',
            'start_region_label': '[8, 18]',
            'required_floor_interval_after_change': '(0.980481, 0.999822]',
            'first_compass_target_unique_appends': 2,
        },
        {
            'example_label': 'weaker_floor_from_precision_targets_8',
            'start_region_label': '{2}',
            'required_floor_interval_after_change': '(0.870482, 0.980481]',
            'first_compass_target_unique_appends': 8,
        },
        {
            'example_label': 'weaker_floor_from_neutral_band_targets_19',
            'start_region_label': '[8, 18]',
            'required_floor_interval_after_change': '[0, 0.870482]',
            'first_compass_target_unique_appends': 19,
        },
    ]


def _build_report() -> dict[str, Any]:
    points = _compass_points()
    transitions = _transition_rows()
    return {
        'focus': 'Compress floor-driven exact uncertainty retuning to four boundary compass points so inheritors can choose the correct first landing point without re-searching the whole live dwell menu.',
        'headline_findings': _headline(points, transitions),
        'decision_rules': _decision_rules(),
        'compass_points': points,
        'transition_rows': transitions,
        'examples': _examples(),
        'source_reports': [
            str(UPGRADE_BOUNDARY_REPORT.relative_to(ROOT)),
            str(RELAXATION_BOUNDARY_REPORT.relative_to(ROOT)),
            str(TARGET_DWELL_ATLAS_REPORT.relative_to(ROOT)),
            str(FLOOR_SUPPORT_REPORT.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty floor-retuning compass snapshot — 2026-03-08')
    lines.append('')
    lines.append(f"Focus: {report['focus']}")
    lines.append('')
    lines.append('## Headline findings')
    for key, value in report['headline_findings'].items():
        lines.append(f'- **{key}**: `{json.dumps(value, ensure_ascii=False)}`')
    lines.append('')
    lines.append('## Compass points')
    for row in report['compass_points']:
        lines.append(
            '- '
            f"dwell `{row['dwell_unique_appends']}` in `{row['region_label']}`; role `{row['role']}`; "
            f"ceiling floor `{row['exact_floor_ceiling']}`; cap `{row['exact_hard_cap']}`; checkpoints `{row['mode_specific_checkpoint_count']}`"
        )
    lines.append('')
    lines.append('## Transition rows')
    for row in report['transition_rows']:
        lines.append(
            '- '
            f"{row['direction']}` from `{row['start_region_label']}` toward floor `{row['target_floor_interval']}` lands first on `{row['first_compass_target_unique_appends']}`; distance interval `{row['distance_interval_unique_appends']}`"
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
