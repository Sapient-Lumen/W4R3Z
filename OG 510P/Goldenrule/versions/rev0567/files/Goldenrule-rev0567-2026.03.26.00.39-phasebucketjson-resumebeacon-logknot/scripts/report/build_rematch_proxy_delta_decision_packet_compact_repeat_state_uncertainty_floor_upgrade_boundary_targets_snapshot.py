#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_upgrade_boundary_targets_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_upgrade_boundary_targets_snapshot_20260308.md'
FLOOR_SUPPORT_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_conditioned_dwell_support_snapshot_20260308.json'
FIXED_DWELL_CEILING_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_fixed_dwell_budget_ceiling_snapshot_20260308.json'
UPGRADE_JUMP_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_upgrade_dwell_jump_snapshot_20260308.json'
ORACLE_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_oracle.py'


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def _load_oracle_module():
    spec = importlib.util.spec_from_file_location('compact_repeat_state_uncertainty_oracle', ORACLE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _rows() -> list[dict[str, Any]]:
    support = _load(FLOOR_SUPPORT_REPORT)
    ceiling = _load(FIXED_DWELL_CEILING_REPORT)
    jump = _load(UPGRADE_JUMP_REPORT)
    support_rows = {row['required_gain_share_floor_interval']: row for row in support['support_rows']}
    ceiling_rows = {row['region_label']: row for row in ceiling['live_region_rows']}
    jump_rows = {(row['start_region_label'], row['destination_region_label']): row for row in jump['jump_rows']}

    rows = [
        {
            'start_region_label': '[19, 32]',
            'required_gain_share_floor_interval': '(0.870482, 0.980481]',
            'nearest_stronger_live_support_boundary_target_unique_appends': 18,
            'nearest_stronger_live_support_boundary_target_region': '[8, 18]',
            'target_boundary_role': 'right_boundary_of_next_stronger_continuous_band',
            'minimal_left_shift_interval_unique_appends': jump_rows[('[19, 32]', '[8, 18]')]['required_left_shift_interval_unique_appends'],
            'representative_anchor_jump_unique_appends': [25, 18],
            'surviving_live_support_after_floor_prune': support_rows['(0.870482, 0.980481]']['live_support_components'],
            'dominated_interior_search_interval_unique_appends': [8, 17],
            'most_important_rule': 'Above floor 0.870482, the relaxed suffix can only strengthen by landing on dwell 18 first; interior neutral-band points 8 through 17 never beat that first repair target on left-shift distance.',
        },
        {
            'start_region_label': '[19, 32]',
            'required_gain_share_floor_interval': '(0.980481, 0.999822]',
            'nearest_stronger_live_support_boundary_target_unique_appends': 2,
            'nearest_stronger_live_support_boundary_target_region': '{2}',
            'target_boundary_role': 'singleton_precision_support',
            'minimal_left_shift_interval_unique_appends': jump_rows[('[19, 32]', '{2}')]['required_left_shift_interval_unique_appends'],
            'representative_anchor_jump_unique_appends': [25, 2],
            'surviving_live_support_after_floor_prune': support_rows['(0.980481, 0.999822]']['live_support_components'],
            'dominated_interior_search_interval_unique_appends': None,
            'most_important_rule': 'Above floor 0.980481, the relaxed suffix has no non-precision rescue left; the nearest stronger saved exact support is the singleton dwell 2.',
        },
        {
            'start_region_label': '[8, 18]',
            'required_gain_share_floor_interval': '(0.980481, 0.999822]',
            'nearest_stronger_live_support_boundary_target_unique_appends': 2,
            'nearest_stronger_live_support_boundary_target_region': '{2}',
            'target_boundary_role': 'singleton_precision_support',
            'minimal_left_shift_interval_unique_appends': jump_rows[('[8, 18]', '{2}')]['required_left_shift_interval_unique_appends'],
            'representative_anchor_jump_unique_appends': [13, 2],
            'surviving_live_support_after_floor_prune': support_rows['(0.980481, 0.999822]']['live_support_components'],
            'dominated_interior_search_interval_unique_appends': None,
            'most_important_rule': 'Above floor 0.980481, the neutral band has exactly one stronger saved exact landing point: dwell 2.',
        },
    ]

    assert ceiling_rows['[19, 32]']['next_region_needed_for_stronger_exact_floor'] == '[8, 18]'
    assert ceiling_rows['[8, 18]']['next_region_needed_for_stronger_exact_floor'] == '{2}'
    return rows


def _headline(rows: list[dict[str, Any]]) -> dict[str, Any]:
    unique_targets = sorted({row['nearest_stronger_live_support_boundary_target_unique_appends'] for row in rows})
    return {
        'main_rule': 'When a fixed live dwell region needs a stronger current exact uncertainty floor, jump to the nearest surviving support boundary target instead of re-searching interior dwell points.',
        'all_current_stronger_floor_repairs_reduce_to_boundary_targets': True,
        'unique_boundary_targets_for_all_current_stronger_floor_repairs_unique_appends': unique_targets,
        'boundary_target_count': len(unique_targets),
        'first_non_precision_strengthening_target_unique_appends': 18,
        'precision_collapse_target_unique_appends': 2,
        'relaxed_suffix_first_stronger_target_is_boundary_not_band_interior': True,
        'neutral_band_has_no_stronger_boundary_target_except_precision_singleton': True,
        'full_live_search_space_points_unique_appends': 26,
        'compressed_upgrade_target_set_points_unique_appends': len(unique_targets),
    }


def _decision_rules() -> list[str]:
    return [
        'When a fixed live dwell request fails only because the required exact floor rose, jump first to the nearest surviving support boundary target instead of sweeping the whole stronger region.',
        'From dwell 19 through 32, requests above floor 0.870482 should target dwell 18 first; interior neutral-band dwells 8 through 17 are dominated as first repairs because they require at least as much left shift and never less.',
        'From dwell 8 through 18, requests above floor 0.980481 should target dwell 2 immediately; there is no stronger intermediate band to inspect.',
        'Treat the current stronger-floor repair target set as `{18, 2}`. That shrinks live upgrade search from 26 current support points to two exact landing points.',
        'Once the deployment already sits at the relevant target boundary, any further strengthening question stops being a retuning search and becomes a menu/frontier question.',
    ]


def _witness_examples() -> list[dict[str, Any]]:
    oracle = _load_oracle_module()
    examples = [
        (
            'relaxed_suffix_mid_floor_upgrade_targets_boundary_18',
            dict(
                required_gain_share_floor='0.96',
                max_hard_cap_budget_inclusive=11,
                minimum_anchor_slack_unique_appends=0,
                minimum_band_width_unique_appends=1,
                target_dwell_unique_appends=20,
                master_calendar_pre_registered=True,
            ),
        ),
        (
            'relaxed_suffix_high_floor_upgrade_targets_precision_2',
            dict(
                required_gain_share_floor='0.99',
                max_hard_cap_budget_inclusive=11,
                minimum_anchor_slack_unique_appends=0,
                minimum_band_width_unique_appends=1,
                target_dwell_unique_appends=25,
                master_calendar_pre_registered=True,
            ),
        ),
        (
            'neutral_band_high_floor_upgrade_targets_precision_2',
            dict(
                required_gain_share_floor='0.99',
                max_hard_cap_budget_inclusive=11,
                minimum_anchor_slack_unique_appends=0,
                minimum_band_width_unique_appends=1,
                target_dwell_unique_appends=13,
                master_calendar_pre_registered=True,
            ),
        ),
    ]
    rows: list[dict[str, Any]] = []
    for label, kwargs in examples:
        result = oracle.classify_request(**kwargs)
        payload = dict(kwargs)
        payload['required_gain_share_floor'] = float(payload['required_gain_share_floor'])
        rows.append({'example_label': label, 'input': payload, 'oracle_result': result})
    return rows


def _build_report() -> dict[str, Any]:
    rows = _rows()
    return {
        'focus': 'Compress stronger-floor retuning from whole dwell bands to the nearest surviving support boundary targets so inheritors can jump directly to the first exact landing point that can possibly work.',
        'headline_findings': _headline(rows),
        'decision_rules': _decision_rules(),
        'upgrade_boundary_rows': rows,
        'witness_examples': _witness_examples(),
        'source_reports': [
            str(FLOOR_SUPPORT_REPORT.relative_to(ROOT)),
            str(FIXED_DWELL_CEILING_REPORT.relative_to(ROOT)),
            str(UPGRADE_JUMP_REPORT.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty floor-upgrade boundary targets snapshot — 2026-03-08')
    lines.append('')
    lines.append(f"Focus: {report['focus']}")
    lines.append('')
    lines.append('## Headline findings')
    for key, value in report['headline_findings'].items():
        lines.append(f'- **{key}**: `{json.dumps(value, ensure_ascii=False)}`')
    lines.append('')
    lines.append('## Boundary-target rows')
    for row in report['upgrade_boundary_rows']:
        lines.append(
            '- '
            f"start `{row['start_region_label']}`; floor interval `{row['required_gain_share_floor_interval']}`; "
            f"nearest target dwell `{row['nearest_stronger_live_support_boundary_target_unique_appends']}` in `{row['nearest_stronger_live_support_boundary_target_region']}`; "
            f"left-shift interval `{row['minimal_left_shift_interval_unique_appends']}`; "
            f"representative jump `{row['representative_anchor_jump_unique_appends']}`"
        )
    lines.append('')
    lines.append('## Decision rules')
    for rule in report['decision_rules']:
        lines.append(f'- {rule}')
    lines.append('')
    lines.append('## Witness examples')
    for row in report['witness_examples']:
        lines.append(
            '- '
            f"{row['example_label']}: status `{row['oracle_result']['status']}`; "
            f"blocking summary `{row['oracle_result']['blocking_summary']}`; "
            f"nearest live repair `{row['oracle_result']['nearest_live_support_repair_for_target_dwell']}`"
        )
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
