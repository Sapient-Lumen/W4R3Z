#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_saved_state_resolver import (
    classify_saved_state,
    decide_saved_state_resolution,
    saved_states,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_hysteresis import (
    decide_saved_state_with_weakening_hysteresis,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_regime_normal_form import (
    REGIME_BANDS,
)

DEFAULT_CURRENT_STATES = saved_states()
DEFAULT_FLOORS = ['0.84', '0.95', '0.99']
REFERENCE_THRESHOLDS = [band['representative_threshold_unique_appends'] for band in REGIME_BANDS]


class WeakeningRecoveryLadderError(RuntimeError):
    pass



def _base_decision(current_state: int, floor: str) -> dict[str, Any]:
    return decide_saved_state_resolution(
        current_dwell_unique_appends=current_state,
        required_gain_share_floor=floor,
        max_hard_cap_budget_inclusive=11,
        minimum_anchor_slack_unique_appends=0,
        minimum_band_width_unique_appends=1,
        max_pre_amortization_checkpoint_budget_inclusive=14,
    )



def _overlay_decision(current_state: int, floor: str, threshold: int) -> dict[str, Any]:
    return decide_saved_state_with_weakening_hysteresis(
        current_dwell_unique_appends=current_state,
        required_gain_share_floor=floor,
        max_hard_cap_budget_inclusive=11,
        minimum_anchor_slack_unique_appends=0,
        minimum_band_width_unique_appends=1,
        max_pre_amortization_checkpoint_budget_inclusive=14,
        max_forced_weakening_shift_unique_appends=threshold,
    )



def _decision_signature(decision: dict[str, Any]) -> tuple[Any, ...]:
    route = None if decision['route_plan'] is None else tuple(decision['route_plan']['route_unique_appends'])
    return (
        decision['action_family'],
        decision['status'],
        decision['selected_steady_tier'],
        decision['selected_anchor_unique_appends'],
        route,
    )



@lru_cache(maxsize=1)
def base_weakening_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for current_state in DEFAULT_CURRENT_STATES:
        state = classify_saved_state(current_state)
        for floor in DEFAULT_FLOORS:
            base = _base_decision(current_state, floor)
            if base['action_family'] != 'weaken':
                continue
            route = base['route_plan']['route_unique_appends']
            shift = base['route_plan']['total_absolute_dwell_shift_unique_appends']
            cases.append(
                {
                    'current_state_unique_appends': current_state,
                    'current_state_label': state['state_label'],
                    'current_tier': state['current_tier'],
                    'required_gain_share_floor': floor,
                    'base_status': base['status'],
                    'selected_steady_tier': base['selected_steady_tier'],
                    'selected_anchor_unique_appends': base['selected_anchor_unique_appends'],
                    'route_unique_appends': route,
                    'one_shot_shift_unique_appends': shift,
                    'selected_minus_current_band_deltas': base['selected_minus_current_band_deltas'],
                }
            )
    cases.sort(key=lambda row: (row['one_shot_shift_unique_appends'], row['current_state_unique_appends'], row['required_gain_share_floor']))
    return cases



def minimal_threshold_for_case(case: dict[str, Any]) -> int:
    base = _base_decision(case['current_state_unique_appends'], case['required_gain_share_floor'])
    base_sig = _decision_signature(base)
    for threshold in range(0, 24):
        overlay = _overlay_decision(case['current_state_unique_appends'], case['required_gain_share_floor'], threshold)
        if _decision_signature(overlay) == base_sig:
            return threshold
    raise WeakeningRecoveryLadderError(
        f"case never recovers base decision: state={case['current_state_unique_appends']} floor={case['required_gain_share_floor']}"
    )



@lru_cache(maxsize=1)
def build_recovery_ladder() -> list[dict[str, Any]]:
    ladder: list[dict[str, Any]] = []
    for case in base_weakening_cases():
        threshold = minimal_threshold_for_case(case)
        state = classify_saved_state(case['current_state_unique_appends'])
        relaxed_release = case['selected_anchor_unique_appends'] == 25 and case['current_state_unique_appends'] != 25
        ladder.append(
            {
                **case,
                'minimal_recovery_threshold_unique_appends': threshold,
                'recovery_kind': (
                    'direct_precision_relaxed_release'
                    if case['current_state_unique_appends'] == 2 and case['selected_anchor_unique_appends'] == 25
                    else 'middle_band_precision_relief'
                    if case['current_state_unique_appends'] == 2 and case['selected_anchor_unique_appends'] == 13
                    else 'direct_entry_boundary_relaxed_release'
                    if case['current_state_unique_appends'] == 8 and relaxed_release
                    else 'neutral_anchor_relaxed_release'
                    if case['current_state_unique_appends'] == 13 and relaxed_release
                    else 'suffix_only_relaxed_release'
                    if case['current_state_unique_appends'] == 18 and relaxed_release
                    else 'other'
                ),
                'recovered_case_label': (
                    f"{state['state_label']} @ floor {case['required_gain_share_floor']} -> {case['selected_steady_tier']} via {case['route_unique_appends']}"
                ),
            }
        )
    ladder.sort(key=lambda row: row['minimal_recovery_threshold_unique_appends'])
    return ladder



@lru_cache(maxsize=1)
def build_threshold_band_progression() -> list[dict[str, Any]]:
    ladder = build_recovery_ladder()
    recovered_by_threshold = {
        threshold: {
            (row['current_state_unique_appends'], row['required_gain_share_floor'])
            for row in ladder
            if row['minimal_recovery_threshold_unique_appends'] <= threshold
        }
        for threshold in REFERENCE_THRESHOLDS
    }
    rows: list[dict[str, Any]] = []
    prior: set[tuple[int, str]] = set()
    for band in REGIME_BANDS:
        threshold = band['representative_threshold_unique_appends']
        recovered = recovered_by_threshold.get(threshold, set())
        new_cases = sorted(recovered - prior)
        deferred = sorted(
            (row['current_state_unique_appends'], row['required_gain_share_floor'])
            for row in ladder
            if (row['current_state_unique_appends'], row['required_gain_share_floor']) not in recovered
        )
        rows.append(
            {
                'threshold_band_label': band['threshold_band_label'],
                'representative_threshold_unique_appends': threshold,
                'recovered_case_count': len(recovered),
                'remaining_deferred_case_count': len(deferred),
                'newly_recovered_cases': [
                    {'current_state_unique_appends': state, 'required_gain_share_floor': floor}
                    for state, floor in new_cases
                ],
                'remaining_deferred_cases': [
                    {'current_state_unique_appends': state, 'required_gain_share_floor': floor}
                    for state, floor in deferred
                ],
            }
        )
        prior = recovered
    return rows



def build_reference_examples() -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []
    for row in build_recovery_ladder():
        overlay_before = _overlay_decision(
            row['current_state_unique_appends'],
            row['required_gain_share_floor'],
            max(row['minimal_recovery_threshold_unique_appends'] - 1, 0),
        )
        overlay_at = _overlay_decision(
            row['current_state_unique_appends'],
            row['required_gain_share_floor'],
            row['minimal_recovery_threshold_unique_appends'],
        )
        examples.append(
            {
                'recovery_kind': row['recovery_kind'],
                'current_state_unique_appends': row['current_state_unique_appends'],
                'required_gain_share_floor': row['required_gain_share_floor'],
                'minimal_recovery_threshold_unique_appends': row['minimal_recovery_threshold_unique_appends'],
                'decision_just_below_threshold': {
                    'threshold': max(row['minimal_recovery_threshold_unique_appends'] - 1, 0),
                    'status': overlay_before['status'],
                    'action_family': overlay_before['action_family'],
                    'route_unique_appends': None if overlay_before['route_plan'] is None else overlay_before['route_plan']['route_unique_appends'],
                },
                'decision_at_threshold': {
                    'threshold': row['minimal_recovery_threshold_unique_appends'],
                    'status': overlay_at['status'],
                    'action_family': overlay_at['action_family'],
                    'route_unique_appends': None if overlay_at['route_plan'] is None else overlay_at['route_plan']['route_unique_appends'],
                },
            }
        )
    return examples



def build_weakening_recovery_ladder_snapshot() -> dict[str, Any]:
    ladder = build_recovery_ladder()
    progression = build_threshold_band_progression()
    thresholds = [row['minimal_recovery_threshold_unique_appends'] for row in ladder]
    if thresholds != [7, 11, 12, 17, 23]:
        raise WeakeningRecoveryLadderError(f'unexpected recovery thresholds: {thresholds}')
    if thresholds != sorted(set(thresholds)):
        raise WeakeningRecoveryLadderError('recovery thresholds are not unique serial breakpoints')

    return {
        'focus': 'Audit the exact withheld base weakening cases and show that the weakening threshold menu is a serial recovery ladder: every breakpoint restores exactly one previously deferred base weakening case.',
        'headline_findings': {
            'base_weakening_case_count': len(ladder),
            'recovery_breakpoints_unique_appends': thresholds,
            'serial_recovery': True,
            'recovered_case_counts_by_threshold_band': {
                row['threshold_band_label']: row['recovered_case_count'] for row in progression
            },
            'remaining_deferred_case_counts_by_threshold_band': {
                row['threshold_band_label']: row['remaining_deferred_case_count'] for row in progression
            },
            'recovery_kinds_in_order': [row['recovery_kind'] for row in ladder],
        },
        'decision_rules': [
            'Interpret the weakening threshold as the size of a prefix of the five-case deferred-weakening menu that you want to restore, not as an opaque scalar knob.',
            'Every breakpoint in the exact menu recovers one and only one base weakening case, so there are no hidden coupled releases or skipped cases.',
            'Threshold `7` restores only suffix-only relaxed release from boundary `18`; threshold `11` then adds only middle-band precision relief `2→13`.',
            'Threshold `12` adds neutral-anchor relaxed release `13→25`, threshold `17` adds direct entry-boundary relaxed release `8→25`, and threshold `23` finally restores direct precision relaxed release `2→25`.',
            'Because the recovery order is serial and prefix-closed, any future policy change that inserts a new breakpoint or merges two breakpoints is a substantive menu change that should be audited case-by-case.',
        ],
        'recovery_ladder': ladder,
        'threshold_band_progression': progression,
        'reference_examples': build_reference_examples(),
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_recovery_ladder.py',
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_hysteresis_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_regime_normal_form_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_capability_selector_snapshot_20260308.json',
        ],
    }



def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Audit the exact serial recovery ladder of deferred weakening cases.')
    parser.add_argument('--pretty', action='store_true')
    return parser



def main() -> None:
    args = _parser().parse_args()
    report = build_weakening_recovery_ladder_snapshot()
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))


if __name__ == '__main__':
    main()
