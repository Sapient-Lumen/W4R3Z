#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_saved_state_resolver import (
    classify_saved_state,
    saved_states,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_hysteresis import (
    decide_saved_state_with_weakening_hysteresis,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_hysteresis_closure import (
    build_threshold_closure_matrix,
    simulate_persistent_request_under_fixed_weakening_threshold,
)

ROOT = Path(__file__).resolve().parents[2]
CURRENT_STATES = saved_states()
FLOOR_INTERVALS = [
    ('up_to_lower_guarantee_floor', '0.84', 'floor ≤ 0.870482'),
    ('middle_band', '0.95', '0.870482 < floor ≤ 0.980481'),
    ('precision_band', '0.99', '0.980481 < floor ≤ 0.999822'),
]
REGIME_BANDS = [
    {
        'threshold_band_label': '0–6',
        'representative_threshold_unique_appends': 0,
        'regime_code': 'fully_sticky',
        'regime_label': 'fully sticky',
        'operator_summary': 'defer every weakening; only strengthening, hold, and boundary stabilization remain live',
    },
    {
        'threshold_band_label': '7–10',
        'representative_threshold_unique_appends': 7,
        'regime_code': 'suffix_release',
        'regime_label': 'suffix release',
        'operator_summary': 'permit only the cheapest neutral-exit release into the relaxed suffix',
    },
    {
        'threshold_band_label': '11–11',
        'representative_threshold_unique_appends': 11,
        'regime_code': 'middle_only_precision_relief',
        'regime_label': 'middle-only precision relief',
        'operator_summary': 'unlock precision→neutral release in the middle band without enlarging the relaxed-floor basin',
    },
    {
        'threshold_band_label': '12–16',
        'representative_threshold_unique_appends': 12,
        'regime_code': 'staged_relaxed_release',
        'regime_label': 'staged relaxed release',
        'operator_summary': 'admit neutral-anchor weakening and thereby allow entry-boundary state 8 to reach the relaxed anchor only after one stabilization cycle',
    },
    {
        'threshold_band_label': '17–22',
        'representative_threshold_unique_appends': 17,
        'regime_code': 'direct_entry_relaxed_release',
        'regime_label': 'direct entry relaxed release',
        'operator_summary': 'upgrade staged relaxed release by allowing the direct 8→25 jump, reducing settlement depth without changing the eventual basin',
    },
    {
        'threshold_band_label': '23–∞',
        'representative_threshold_unique_appends': 23,
        'regime_code': 'full_release',
        'regime_label': 'full release',
        'operator_summary': 'recover the base cheapest-tier controller, including direct precision release to the relaxed anchor',
    },
]


class WeakeningRegimeNormalFormError(ValueError):
    pass


def _decision(current_state: int, floor_value: str, threshold: int) -> dict[str, Any]:
    return decide_saved_state_with_weakening_hysteresis(
        current_dwell_unique_appends=current_state,
        required_gain_share_floor=floor_value,
        max_hard_cap_budget_inclusive=11,
        minimum_anchor_slack_unique_appends=0,
        minimum_band_width_unique_appends=1,
        master_calendar_pre_registered=False,
        max_pre_amortization_checkpoint_budget_inclusive=14,
        max_forced_weakening_shift_unique_appends=threshold,
    )


def _case_label(current_state: int, floor_label: str, decision: dict[str, Any]) -> str:
    state = classify_saved_state(current_state)
    return f"{current_state}:{state['state_label']}@{floor_label}->{decision['base_resolver_decision']['selected_steady_tier']}"


def _forced_weakening_case_labels(threshold: int) -> list[str]:
    labels: list[str] = []
    for current_state in CURRENT_STATES:
        for floor_label, floor_value, _notation in FLOOR_INTERVALS:
            decision = _decision(current_state, floor_value, threshold)
            if decision['base_resolver_decision']['action_family'] != 'weaken':
                continue
            if decision['deferred_weaken']:
                continue
            labels.append(_case_label(current_state, floor_label, decision))
    return sorted(labels)


def _relaxed_release_state_sets(threshold: int) -> dict[str, list[int]]:
    stronger_eventual: list[int] = []
    stronger_direct: list[int] = []
    all_eventual: list[int] = []
    all_direct: list[int] = []
    for current_state in CURRENT_STATES:
        state = classify_saved_state(current_state)
        closure = simulate_persistent_request_under_fixed_weakening_threshold(
            current_dwell_unique_appends=current_state,
            required_gain_share_floor='0.84',
            max_hard_cap_budget_inclusive=11,
            minimum_anchor_slack_unique_appends=0,
            minimum_band_width_unique_appends=1,
            max_pre_amortization_checkpoint_budget_inclusive=14,
            max_forced_weakening_shift_unique_appends=threshold,
        )
        first = _decision(current_state, '0.84', threshold)
        route = None if first['route_plan'] is None else first['route_plan']['route_unique_appends']

        if closure['final_state_unique_appends'] == 25:
            all_eventual.append(current_state)
            if state['current_tier'] != 'lower_guarantee':
                stronger_eventual.append(current_state)
        if current_state == 25 or (route is not None and route[-1] == 25):
            all_direct.append(current_state)
            if state['current_tier'] != 'lower_guarantee':
                stronger_direct.append(current_state)

    return {
        'eventual_relaxed_anchor_states_all': all_eventual,
        'direct_relaxed_anchor_states_all': all_direct,
        'eventual_relaxed_anchor_states_from_stronger_tiers': stronger_eventual,
        'direct_relaxed_anchor_states_from_stronger_tiers': stronger_direct,
    }


def _middle_band_neutral_release_states(threshold: int) -> list[int]:
    states: list[int] = []
    for current_state in CURRENT_STATES:
        decision = _decision(current_state, '0.95', threshold)
        route = None if decision['route_plan'] is None else decision['route_plan']['route_unique_appends']
        if route is not None and route[-1] == 13:
            base = decision['base_resolver_decision']
            if base['action_family'] == 'weaken' and not decision['deferred_weaken']:
                states.append(current_state)
    return states


def _threshold_band_for(threshold: int) -> dict[str, Any]:
    if threshold < 0:
        raise WeakeningRegimeNormalFormError('threshold must be non-negative')
    for band in REGIME_BANDS[:-1]:
        label = band['threshold_band_label']
        start_str, end_str = label.split('–')
        start = int(start_str)
        end = int(end_str)
        if start <= threshold <= end:
            return band
    return REGIME_BANDS[-1]


def normalize_weakening_threshold(threshold: int) -> dict[str, Any]:
    band = _threshold_band_for(threshold)
    representative_threshold = band['representative_threshold_unique_appends']
    closure_rows = {row['threshold_band_label']: row for row in build_threshold_closure_matrix()}
    forced_cases = _forced_weakening_case_labels(representative_threshold)
    previous_band = None
    for candidate in REGIME_BANDS:
        if candidate['threshold_band_label'] == band['threshold_band_label']:
            break
        previous_band = candidate
    previous_forced = [] if previous_band is None else _forced_weakening_case_labels(previous_band['representative_threshold_unique_appends'])
    release_sets = _relaxed_release_state_sets(representative_threshold)

    return {
        'tool': str(Path(__file__).resolve()),
        'input_threshold_unique_appends': threshold,
        'normalized_threshold_unique_appends': representative_threshold,
        'threshold_band_label': band['threshold_band_label'],
        'regime_code': band['regime_code'],
        'regime_label': band['regime_label'],
        'operator_summary': band['operator_summary'],
        'forced_one_shot_weakening_cases': forced_cases,
        'newly_admitted_one_shot_weakening_cases': [case for case in forced_cases if case not in previous_forced],
        'eventual_relaxed_anchor_states_all': release_sets['eventual_relaxed_anchor_states_all'],
        'direct_relaxed_anchor_states_all': release_sets['direct_relaxed_anchor_states_all'],
        'eventual_relaxed_anchor_states_from_stronger_tiers': release_sets['eventual_relaxed_anchor_states_from_stronger_tiers'],
        'direct_relaxed_anchor_states_from_stronger_tiers': release_sets['direct_relaxed_anchor_states_from_stronger_tiers'],
        'middle_band_neutral_release_states': _middle_band_neutral_release_states(representative_threshold),
        'closure_summary': closure_rows[band['threshold_band_label']],
    }



def build_weakening_regime_normal_form_snapshot() -> dict[str, Any]:
    regimes = [normalize_weakening_threshold(band['representative_threshold_unique_appends']) for band in REGIME_BANDS]
    return {
        'focus': 'Collapse numeric weakening thresholds into a small operator-grade regime normal form so inheritors can choose stickiness policies by behavior rather than memorizing raw shift values.',
        'headline_findings': {
            'main_rule': 'The weakening hysteresis threshold compresses to six exact named regimes; only one of them (`11`) changes middle-band precision release without enlarging the relaxed-floor basin.',
            'named_regime_count': len(regimes),
            'regime_breakpoints_unique_appends': [7, 11, 12, 17, 23],
            'middle_only_regime_threshold_unique_appends': 11,
            'staged_vs_direct_relaxed_release_bands_share_final_counts': ['12–16', '17–22'],
            'full_base_policy_regime_threshold_unique_appends': 23,
        },
        'decision_rules': [
            'Pick a weakening threshold by regime semantics, not by raw magnitude alone.',
            'Treat threshold `11` as a special middle-band-only release: it admits `2→13` under a middle floor but does not enlarge the relaxed-floor release set beyond what threshold `7` already allows.',
            'Use threshold `12` when staged relaxed release from boundary `8` is acceptable; use threshold `17` only when the direct `8→25` jump itself matters.',
            'Use threshold `23` only when relaxed-floor requests should be able to discharge precision anchor `2` immediately.',
            'Because strengthenings remain mandatory in every regime, this normal form only governs optional weakening behavior.',
        ],
        'regimes': regimes,
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_regime_normal_form.py',
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_hysteresis_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_hysteresis_closure_snapshot_20260308.json',
        ],
    }



def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Normalize a weakening-hysteresis threshold into a named operator regime.')
    parser.add_argument('--max-forced-weakening-shift-unique-appends', required=True, type=int)
    return parser



def main() -> None:
    args = _parser().parse_args()
    print(json.dumps(normalize_weakening_threshold(args.max_forced_weakening_shift_unique_appends), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
