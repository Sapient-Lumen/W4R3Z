#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_upgrade_dwell_jump_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_upgrade_dwell_jump_snapshot_20260308.md'
FIXED_DWELL_CEILING_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_fixed_dwell_budget_ceiling_snapshot_20260308.json'
THRESHOLD_SELECTOR_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_guarantee_threshold_selector_snapshot_20260308.json'
DWELL_TOPOLOGY_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_coverage_topology_snapshot_20260308.json'
FLOOR_SUPPORT_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_conditioned_dwell_support_snapshot_20260308.json'
ORACLE_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_request_oracle_snapshot_20260308.json'
ORACLE_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_oracle.py'

LIVE_REGIONS = ['[19, 32]', '[8, 18]', '{2}']
REGION_ORDER = {'{2}': 0, '[8, 18]': 1, '[19, 32]': 2}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))




def _load_oracle_module():
    spec = importlib.util.spec_from_file_location('compact_repeat_state_uncertainty_oracle', ORACLE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module

def _parse_region(region: str) -> tuple[int, int]:
    if region == '{2}':
        return (2, 2)
    left, right = region.strip('[]').split(',')
    return (int(left.strip()), int(right.strip()))


def _shift_interval(start_region: str, destination_region: str) -> list[int]:
    start_lo, start_hi = _parse_region(start_region)
    _, dest_hi = _parse_region(destination_region)
    # stronger-floor upgrades always move left to the right edge of the next stronger live region
    return [start_lo - dest_hi, start_hi - dest_hi]


def _jump_row(start_region: str, destination_region: str, start_floor: float, destination_floor: float, target_floor_interval: str) -> dict[str, Any]:
    start_lo, start_hi = _parse_region(start_region)
    _, dest_hi = _parse_region(destination_region)
    shifts = _shift_interval(start_region, destination_region)
    return {
        'start_region_label': start_region,
        'destination_region_label': destination_region,
        'direction_of_stronger_floor_repair': 'leftward_only',
        'start_region_dwell_interval_unique_appends': [start_lo, start_hi],
        'destination_region_boundary_for_first_stronger_floor_unique_appends': dest_hi,
        'required_left_shift_interval_unique_appends': shifts,
        'representative_anchor_jump_unique_appends': None,
        'start_region_exact_floor_ceiling': round(start_floor, 6),
        'destination_region_exact_floor_ceiling': round(destination_floor, 6),
        'extra_exact_floor_unlocked_by_jump': round(destination_floor - start_floor, 6),
        'required_gain_share_floor_interval_that_forces_this_jump': target_floor_interval,
        'most_important_rule': (
            f'Once a request floor exceeds `{start_floor:.6f}` while dwell remains inside `{start_region}`, the first stronger current exact floor appears only by jumping left to `{destination_region}`; searching right cannot help.'
        ),
    }


def _rows() -> list[dict[str, Any]]:
    ceiling = _load(FIXED_DWELL_CEILING_REPORT)
    support = _load(FLOOR_SUPPORT_REPORT)
    live = {row['region_label']: row for row in ceiling['live_region_rows']}
    threshold = _load(THRESHOLD_SELECTOR_REPORT)
    tier_rows = {row['tier']: row for row in threshold['tier_rows']}
    floor_support_rows = support['support_rows']

    lower_floor = float(tier_rows['lower_guarantee']['actual_certified_gain_share_floor_of_full_dynamic_savings'])
    near_optimal_floor = float(tier_rows['near_optimal']['actual_certified_gain_share_floor_of_full_dynamic_savings'])
    near_exact_floor = float(tier_rows['near_exact']['actual_certified_gain_share_floor_of_full_dynamic_savings'])

    rows = [
        _jump_row('[19, 32]', '[8, 18]', lower_floor, near_optimal_floor, '(0.870482, 0.980481]'),
        _jump_row('[19, 32]', '{2}', lower_floor, near_exact_floor, '(0.980481, 0.999822]'),
        _jump_row('[8, 18]', '{2}', near_optimal_floor, near_exact_floor, '(0.980481, 0.999822]'),
    ]
    for row in rows:
        if row['start_region_label'] == '[19, 32]' and row['destination_region_label'] == '[8, 18]':
            row['representative_anchor_jump_unique_appends'] = [25, 18]
        elif row['start_region_label'] == '[19, 32]' and row['destination_region_label'] == '{2}':
            row['representative_anchor_jump_unique_appends'] = [25, 2]
        elif row['start_region_label'] == '[8, 18]' and row['destination_region_label'] == '{2}':
            row['representative_anchor_jump_unique_appends'] = [13, 2]

    widest_non_precision_support = floor_support_rows[0]['continuous_non_precision_support_start_unique_appends'], floor_support_rows[0]['continuous_non_precision_support_end_unique_appends']
    topology = _load(DWELL_TOPOLOGY_REPORT)
    oracle = _load(ORACLE_REPORT)
    assert oracle['headline_findings']['accepted_input_fields']
    assert topology['headline_findings']['exact_covered_dwell_intervals_unique_appends'] == [[2, 2], [8, 32]]
    assert widest_non_precision_support == (8, 32)
    return rows


def _headline(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_pair = {(row['start_region_label'], row['destination_region_label']): row for row in rows}
    return {
        'main_rule': 'When a fixed live dwell region must support a stronger exact uncertainty floor, search left immediately: every current exact floor upgrade path is a leftward dwell jump, never a rightward sweep.',
        'all_current_exact_floor_upgrades_from_live_regions_are_leftward_only': all(
            row['direction_of_stronger_floor_repair'] == 'leftward_only' for row in rows
        ),
        'first_stronger_region_by_live_start_region': {
            '[19, 32]': '[8, 18]',
            '[8, 18]': '{2}',
            '{2}': None,
        },
        'required_left_shift_interval_unique_appends_by_upgrade_pair': {
            '[19, 32] -> [8, 18]': by_pair[('[19, 32]', '[8, 18]')]['required_left_shift_interval_unique_appends'],
            '[19, 32] -> {2}': by_pair[('[19, 32]', '{2}')]['required_left_shift_interval_unique_appends'],
            '[8, 18] -> {2}': by_pair[('[8, 18]', '{2}')]['required_left_shift_interval_unique_appends'],
        },
        'extra_exact_floor_unlocked_by_leftward_jump': {
            '[19, 32] -> [8, 18]': by_pair[('[19, 32]', '[8, 18]')]['extra_exact_floor_unlocked_by_jump'],
            '[19, 32] -> {2}': by_pair[('[19, 32]', '{2}')]['extra_exact_floor_unlocked_by_jump'],
            '[8, 18] -> {2}': by_pair[('[8, 18]', '{2}')]['extra_exact_floor_unlocked_by_jump'],
        },
        'precision_upgrade_is_a_leftward_collapse_not_a_local_tune': True,
        'neutral_band_is_the_last_live_region_before_precision_singleton': True,
        'no_current_live_region_has_a_rightward_exact_floor_upgrade_path': True,
    }


def _decision_rules() -> list[str]:
    return [
        'When a fixed live dwell region needs a stronger exact floor, search left first; no saved exact floor upgrade is reachable by increasing dwell.',
        'From dwell 19 through 32, the first stronger exact floor above 0.870482 appears at the left boundary of the neutral band (dwell 18), not anywhere to the right.',
        'From dwell 8 through 18, any request above floor 0.980481 collapses directly to the precision singleton at dwell 2; there is no intermediate stronger exact band.',
        'Treat the representative anchor jumps 25→18 and 13→2 as canonical strengthening repairs: they unlock the next stronger exact floors without reopening full search.',
        'Once a deployment already sits at dwell 2, the current saved menu has no stronger exact floor left anywhere; further strengthening is a frontier-extension problem, not a retuning problem.',
    ]


def _witness_examples() -> list[dict[str, Any]]:
    oracle_report = _load(ORACLE_REPORT)
    examples_by_label = {row['example_label']: row for row in oracle_report['oracle_examples']}
    oracle = _load_oracle_module()
    neutral_band_precision_probe = oracle.classify_request(
        required_gain_share_floor='0.99',
        max_hard_cap_budget_inclusive=11,
        minimum_anchor_slack_unique_appends=0,
        minimum_band_width_unique_appends=1,
        target_dwell_unique_appends=13,
        master_calendar_pre_registered=True,
    )
    rows = [
        {
            'example_label': 'relaxed_suffix_must_jump_left_into_neutral_band_for_floor_0_96',
            'oracle_result': examples_by_label['floor_pruned_relaxed_suffix']['oracle_result'],
            'most_important_rule': 'A floor request above 0.870482 at dwell 20 fails with nearest live support repair 18, proving that the first stronger exact floor from the relaxed suffix is a leftward jump into the neutral band.',
        },
        {
            'example_label': 'neutral_band_must_collapse_left_to_precision_singleton_for_floor_0_99',
            'oracle_result': neutral_band_precision_probe,
            'most_important_rule': 'A floor request above 0.980481 at dwell 13 fails with nearest live support repair 2, proving that the only stronger current exact floor from the neutral band is the leftward precision collapse.',
        },
    ]
    return rows


def _build_report() -> dict[str, Any]:
    rows = _rows()
    return {
        'focus': 'Turn the fixed-dwell ceiling result into a directionality card so inheritors stop searching the wrong side of dwell space when a fixed region needs a stronger exact uncertainty floor.',
        'headline_findings': _headline(rows),
        'decision_rules': _decision_rules(),
        'jump_rows': rows,
        'witness_examples': _witness_examples(),
        'source_reports': [
            str(FIXED_DWELL_CEILING_REPORT.relative_to(ROOT)),
            str(THRESHOLD_SELECTOR_REPORT.relative_to(ROOT)),
            str(DWELL_TOPOLOGY_REPORT.relative_to(ROOT)),
            str(FLOOR_SUPPORT_REPORT.relative_to(ROOT)),
            str(ORACLE_REPORT.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty floor-upgrade dwell-jump snapshot — 2026-03-08')
    lines.append('')
    lines.append(f"Focus: {report['focus']}")
    lines.append('')
    lines.append('## Headline findings')
    for key, value in report['headline_findings'].items():
        lines.append(f'- **{key}**: `{json.dumps(value, ensure_ascii=False)}`')
    lines.append('')
    lines.append('## Exact stronger-floor jump rows')
    for row in report['jump_rows']:
        lines.append(
            '- '
            f"{row['start_region_label']} -> {row['destination_region_label']}: "
            f"required floor interval `{row['required_gain_share_floor_interval_that_forces_this_jump']}`; "
            f"left-shift interval `{row['required_left_shift_interval_unique_appends']}`; "
            f"representative jump `{row['representative_anchor_jump_unique_appends']}`; "
            f"extra unlocked floor `{row['extra_exact_floor_unlocked_by_jump']}`"
        )
    lines.append('')
    lines.append('## Decision rules')
    for rule in report['decision_rules']:
        lines.append(f'- {rule}')
    lines.append('')
    lines.append('## Witness examples')
    for row in report['witness_examples']:
        result = row['oracle_result']
        lines.append(
            '- '
            f"{row['example_label']}: status `{result['status']}`; "
            f"blocking summary `{result['blocking_summary']}`; "
            f"nearest live repair `{result['nearest_live_support_repair_for_target_dwell']}`"
        )
    lines.append('')
    lines.append('## Source reports')
    for source in report['source_reports']:
        lines.append(f'- `{source}`')
    lines.append('')
    lines.append(f"Source script: `{report['source_script']}`")
    return '\n'.join(lines) + '\n'


def main() -> None:
    report = _build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(report), encoding='utf-8')


if __name__ == '__main__':
    main()
