#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from functools import lru_cache
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_budget_live_action_surface import (
    build_marginal_live_flips,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_budget_selector import (
    select_weakening_regime_by_recovered_case_budget,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_hysteresis import (
    decide_saved_state_with_weakening_hysteresis,
)


class WeakeningReleaseValueClassesError(RuntimeError):
    pass


VALUE_CLASS_LABELS: dict[tuple[int, int, int, int], str] = {
    (2, 3, 1, 3): 'relaxed_suffix_savings_bundle',
    (6, 6, 5, 10): 'middle_precision_relief_bundle',
    (8, 9, 6, 13): 'full_precision_relaxed_release_bundle',
}


def _decision_for_threshold(current_state: int, floor: str, threshold: int) -> dict[str, Any]:
    return decide_saved_state_with_weakening_hysteresis(
        current_dwell_unique_appends=current_state,
        required_gain_share_floor=floor,
        max_hard_cap_budget_inclusive=11,
        minimum_anchor_slack_unique_appends=0,
        minimum_band_width_unique_appends=1,
        max_pre_amortization_checkpoint_budget_inclusive=14,
        max_forced_weakening_shift_unique_appends=threshold,
    )



def _savings_vector(decision: dict[str, Any]) -> tuple[int, int, int, int]:
    payload = decision['forgone_steady_state_savings_vs_current_band']
    if payload is None:
        raise WeakeningReleaseValueClassesError('expected deferred weakening decision with savings payload')
    vector = (
        payload['exact_hard_cap_units'],
        payload['mode_specific_checkpoint_units'],
        payload['minimum_anchor_slack_units'],
        payload['exact_dwell_band_width_units'],
    )
    return vector



def _value_class_label(vector: tuple[int, int, int, int]) -> str:
    if vector not in VALUE_CLASS_LABELS:
        raise WeakeningReleaseValueClassesError(f'unrecognized savings vector: {vector!r}')
    return VALUE_CLASS_LABELS[vector]



@lru_cache(maxsize=1)
def build_marginal_release_steps() -> list[dict[str, Any]]:
    steps: list[dict[str, Any]] = []
    for flip in build_marginal_live_flips():
        budget = flip['state_transition_budget_step']
        previous_selector = select_weakening_regime_by_recovered_case_budget(budget - 1)
        current_selector = select_weakening_regime_by_recovered_case_budget(budget)
        previous_threshold = previous_selector['selected_threshold_unique_appends']
        current_threshold = current_selector['selected_threshold_unique_appends']
        previous_decision = _decision_for_threshold(
            flip['current_state_unique_appends'],
            flip['required_gain_share_floor'],
            previous_threshold,
        )
        current_decision = _decision_for_threshold(
            flip['current_state_unique_appends'],
            flip['required_gain_share_floor'],
            current_threshold,
        )
        if not previous_decision['deferred_weaken']:
            raise WeakeningReleaseValueClassesError(f'expected deferred weakening before budget step {budget}')
        if current_decision['action_family'] != 'weaken':
            raise WeakeningReleaseValueClassesError(f'expected weakening to be released at budget step {budget}')

        savings_vector = _savings_vector(previous_decision)
        steps.append(
            {
                'budget_step': budget,
                'threshold_unique_appends': current_threshold,
                'threshold_increment_unique_appends': current_threshold - previous_threshold,
                'current_state_unique_appends': flip['current_state_unique_appends'],
                'current_state_label': flip['current_state_label'],
                'required_gain_share_floor': flip['required_gain_share_floor'],
                'released_route_unique_appends': current_decision['route_plan']['route_unique_appends'],
                'released_route_shift_unique_appends': current_decision['weakening_shift_unique_appends'],
                'released_steady_tier': current_decision['selected_steady_tier'],
                'savings_vector': {
                    'exact_hard_cap_units': savings_vector[0],
                    'mode_specific_checkpoint_units': savings_vector[1],
                    'minimum_anchor_slack_units': savings_vector[2],
                    'exact_dwell_band_width_units': savings_vector[3],
                },
                'value_class_label': _value_class_label(savings_vector),
                'released_live_case_label': flip['activated_live_case_label'],
            }
        )
    return steps



@lru_cache(maxsize=1)
def build_value_classes() -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in build_marginal_release_steps():
        grouped[row['value_class_label']].append(row)

    value_classes: list[dict[str, Any]] = []
    for class_label, rows in grouped.items():
        exemplar = rows[0]['savings_vector']
        value_classes.append(
            {
                'value_class_label': class_label,
                'member_budget_steps': [row['budget_step'] for row in rows],
                'member_live_cases': [
                    {
                        'current_state_unique_appends': row['current_state_unique_appends'],
                        'current_state_label': row['current_state_label'],
                        'required_gain_share_floor': row['required_gain_share_floor'],
                    }
                    for row in rows
                ],
                'member_thresholds_unique_appends': [row['threshold_unique_appends'] for row in rows],
                'member_route_shifts_unique_appends': [row['released_route_shift_unique_appends'] for row in rows],
                'member_threshold_increments_unique_appends': [row['threshold_increment_unique_appends'] for row in rows],
                'recovered_steady_state_savings_vector': exemplar,
                'member_count': len(rows),
                'is_shift_ordered_within_class': [row['released_route_shift_unique_appends'] for row in rows]
                == sorted(row['released_route_shift_unique_appends'] for row in rows),
            }
        )
    return sorted(value_classes, key=lambda row: (-row['member_count'], row['value_class_label']))



def build_weakening_release_value_classes_snapshot() -> dict[str, Any]:
    steps = build_marginal_release_steps()
    value_classes = build_value_classes()

    repeated_classes = [row for row in value_classes if row['member_count'] > 1]
    if len(repeated_classes) != 1:
        raise WeakeningReleaseValueClassesError(f'expected exactly one repeated value class, found {len(repeated_classes)}')
    repeated = repeated_classes[0]

    if not repeated['is_shift_ordered_within_class']:
        raise WeakeningReleaseValueClassesError('expected repeated value class to be ordered by released route shift')

    return {
        'focus': 'Group weakening-budget release steps by recovered steady-state savings vectors so inheritors can see when later breakpoints buy new value versus merely extend the same value bundle to harder-to-move live states.',
        'headline_findings': {
            'marginal_release_step_count': len(steps),
            'release_value_class_count': len(value_classes),
            'value_class_membership_by_budget_step': {
                row['value_class_label']: row['member_budget_steps'] for row in value_classes
            },
            'repeated_value_class_label': repeated['value_class_label'],
            'repeated_value_class_budget_steps': repeated['member_budget_steps'],
            'repeated_value_class_route_shifts_unique_appends': repeated['member_route_shifts_unique_appends'],
            'repeated_value_class_thresholds_unique_appends': repeated['member_thresholds_unique_appends'],
            'repeated_value_class_is_cheapest_shift_first': repeated['is_shift_ordered_within_class'],
            'unique_value_class_labels': [row['value_class_label'] for row in value_classes if row['member_count'] == 1],
        },
        'decision_rules': [
            'Read each budget step as one live weakening release plus its recovered steady-state savings vector, not only as a scalar threshold increase.',
            'When multiple released cases share the same savings vector, treat their breakpoint order as a cheapest-shift-first ordering over harder-to-move states rather than as increasing steady-state value.',
            'Use later steps in a repeated value class only when governance wants the same relaxed savings bundle to cover additional live states with larger one-shot move costs.',
            'Reserve unique value-class steps for genuinely new savings bundles: middle-band precision relief and full relaxed release from the precision anchor.',
            'Treat any future policy edit that changes a release-step savings vector or breaks the within-class shift ordering as a substantive redesign of the weakening menu.',
        ],
        'marginal_release_steps': steps,
        'release_value_classes': value_classes,
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_release_value_classes.py',
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_budget_live_action_surface_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_hysteresis_snapshot_20260308.json',
        ],
    }



def main() -> None:
    print(json.dumps(build_weakening_release_value_classes_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
