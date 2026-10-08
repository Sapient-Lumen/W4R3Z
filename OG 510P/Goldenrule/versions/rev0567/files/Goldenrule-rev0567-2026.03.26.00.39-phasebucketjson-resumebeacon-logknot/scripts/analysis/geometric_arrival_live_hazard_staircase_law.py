#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.geometric_arrival_live_deadline_formula_law import (
    compute_state_live_deadline_formula,
    compute_universal_live_deadline_formula,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_dense_index_law import (
    build_all_realized_feasible_interval_states,
)


class GeometricArrivalLiveHazardStaircaseLawError(RuntimeError):
    pass


STATE_GRID = tuple(tuple(state) for state in build_all_realized_feasible_interval_states())
BATCH_GRID = tuple(range(1, 9))
ARRIVAL_GRID = (
    Fraction(1, 8),
    Fraction(1, 4),
    Fraction(3, 8),
    Fraction(1, 2),
    Fraction(5, 8),
    Fraction(3, 4),
    Fraction(7, 8),
    Fraction(1, 1),
)
HOLD_COST_GRID = (Fraction(1, 20), Fraction(1, 10), Fraction(1, 4), Fraction(1, 2))
POSITIVE_TARGET_MARGIN_GRID = (Fraction(1, 4), Fraction(1, 2), Fraction(1, 1), Fraction(2, 1))

SCHEDULE_ORDER = {
    'impossible': 0,
    'asymptotic_only': 1,
    'finite': 2,
}


def _serialize_fraction(value: Fraction) -> dict[str, int | float]:
    return {
        'numerator': value.numerator,
        'denominator': value.denominator,
        'decimal': float(value),
    }


def _schedule_rank(schedule_class: str) -> int:
    if schedule_class not in SCHEDULE_ORDER:
        raise GeometricArrivalLiveHazardStaircaseLawError(f'unknown schedule class: {schedule_class}')
    return SCHEDULE_ORDER[schedule_class]


@lru_cache(maxsize=None)
def compute_state_live_hazard_staircase_profile(
    state: tuple[int, int],
    current_batch_length: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    target_margin_bits_numerator: int,
    target_margin_bits_denominator: int,
) -> dict[str, Any]:
    hold_cost = Fraction(hold_cost_bits_numerator, hold_cost_bits_denominator)
    target_margin = Fraction(target_margin_bits_numerator, target_margin_bits_denominator)

    ladder: list[dict[str, Any]] = []
    for p in ARRIVAL_GRID:
        profile = compute_state_live_deadline_formula(
            state,
            current_batch_length,
            p.numerator,
            p.denominator,
            hold_cost.numerator,
            hold_cost.denominator,
            target_margin.numerator,
            target_margin.denominator,
        )
        ladder.append(
            {
                'arrival_probability_per_tick': _serialize_fraction(p),
                'schedule_class': str(profile['schedule_class']),
                'minimum_nominal_live_deadline_ticks': profile['minimum_nominal_live_deadline_ticks'],
            }
        )

    return {
        'state': list(state),
        'current_batch_length': int(current_batch_length),
        'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
        'target_margin_bits_per_script': _serialize_fraction(target_margin),
        'hazard_staircase_rule': (
            'for fixed state, batch, hold cost, and positive realized margin, the same-deadline live schedule class '
            'is nondecreasing in arrival hazard under impossible < asymptotic_only < finite, and every finite '
            'minimum deadline lies on the odd ladder 1,3,5,... and is nonincreasing as hazard rises'
        ),
        'ladder': ladder,
    }


@lru_cache(maxsize=None)
def compute_universal_live_hazard_staircase_profile(
    current_batch_length: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    target_margin_bits_numerator: int,
    target_margin_bits_denominator: int,
) -> dict[str, Any]:
    hold_cost = Fraction(hold_cost_bits_numerator, hold_cost_bits_denominator)
    target_margin = Fraction(target_margin_bits_numerator, target_margin_bits_denominator)

    ladder: list[dict[str, Any]] = []
    for p in ARRIVAL_GRID:
        profile = compute_universal_live_deadline_formula(
            current_batch_length,
            p.numerator,
            p.denominator,
            hold_cost.numerator,
            hold_cost.denominator,
            target_margin.numerator,
            target_margin.denominator,
        )
        ladder.append(
            {
                'arrival_probability_per_tick': _serialize_fraction(p),
                'schedule_class': str(profile['schedule_class']),
                'minimum_nominal_live_deadline_ticks': profile['minimum_nominal_live_deadline_ticks'],
            }
        )

    return {
        'guarantee_scope': 'all_realized_states',
        'guarantee_state_prefix_bits': 7,
        'current_batch_length': int(current_batch_length),
        'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
        'target_margin_bits_per_script': _serialize_fraction(target_margin),
        'hazard_staircase_rule': (
            'for fixed batch, hold cost, and positive universal realized margin, the same-deadline live schedule class '
            'is nondecreasing in arrival hazard under impossible < asymptotic_only < finite, and every finite '
            'minimum deadline lies on the odd ladder 1,3,5,... and is nonincreasing as hazard rises'
        ),
        'ladder': ladder,
    }


@lru_cache(maxsize=1)
def build_geometric_arrival_live_hazard_staircase_validation_summary() -> dict[str, Any]:
    validated_state_ladders = 0
    validated_universal_ladders = 0
    validated_state_contexts = 0
    validated_universal_contexts = 0
    state_monotone_class_ladders = 0
    universal_monotone_class_ladders = 0
    state_nonincreasing_finite_deadline_ladders = 0
    universal_nonincreasing_finite_deadline_ladders = 0
    state_suffix_finite_ladders = 0
    universal_suffix_finite_ladders = 0
    state_finite_deadline_observations = 0
    universal_finite_deadline_observations = 0
    state_odd_finite_deadline_observations = 0
    universal_odd_finite_deadline_observations = 0
    state_deadline_drop_ladders = 0
    universal_deadline_drop_ladders = 0
    state_deadline_drop_events = 0
    universal_deadline_drop_events = 0
    state_class_improvement_ladders = 0
    universal_class_improvement_ladders = 0

    state_drop_example: dict[str, Any] | None = None
    state_impossible_example: dict[str, Any] | None = None
    universal_drop_example: dict[str, Any] | None = None
    universal_impossible_example: dict[str, Any] | None = None

    for state in STATE_GRID:
        for current_batch_length in BATCH_GRID:
            for hold_cost in HOLD_COST_GRID:
                for target_margin in POSITIVE_TARGET_MARGIN_GRID:
                    profile = compute_state_live_hazard_staircase_profile(
                        state,
                        current_batch_length,
                        hold_cost.numerator,
                        hold_cost.denominator,
                        target_margin.numerator,
                        target_margin.denominator,
                    )
                    ladder = profile['ladder']
                    validated_state_ladders += 1
                    validated_state_contexts += len(ladder)

                    class_ranks = [_schedule_rank(str(entry['schedule_class'])) for entry in ladder]
                    if class_ranks == sorted(class_ranks):
                        state_monotone_class_ladders += 1
                    else:
                        raise GeometricArrivalLiveHazardStaircaseLawError('state class ladder regressed with higher arrival hazard')

                    if any(class_ranks[i] > class_ranks[i + 1] for i in range(len(class_ranks) - 1)):
                        raise GeometricArrivalLiveHazardStaircaseLawError('state class rank decreased along hazard ladder')
                    if any(class_ranks[i] < class_ranks[i + 1] for i in range(len(class_ranks) - 1)):
                        state_class_improvement_ladders += 1

                    finite_flags = [entry['schedule_class'] == 'finite' for entry in ladder]
                    first_finite_index = next((i for i, flag in enumerate(finite_flags) if flag), None)
                    if first_finite_index is None or all(finite_flags[first_finite_index:]):
                        state_suffix_finite_ladders += 1
                    else:
                        raise GeometricArrivalLiveHazardStaircaseLawError('state finite region was not a hazard suffix')

                    finite_deadlines = [int(entry['minimum_nominal_live_deadline_ticks']) for entry in ladder if entry['schedule_class'] == 'finite']
                    state_finite_deadline_observations += len(finite_deadlines)
                    state_odd_finite_deadline_observations += sum(deadline % 2 == 1 for deadline in finite_deadlines)
                    if any(deadline % 2 == 0 for deadline in finite_deadlines):
                        raise GeometricArrivalLiveHazardStaircaseLawError('state finite minimum deadline was not odd')
                    if finite_deadlines == sorted(finite_deadlines, reverse=True):
                        state_nonincreasing_finite_deadline_ladders += 1
                    else:
                        raise GeometricArrivalLiveHazardStaircaseLawError('state finite deadlines increased with higher arrival hazard')
                    drop_events = sum(
                        finite_deadlines[i] > finite_deadlines[i + 1]
                        for i in range(len(finite_deadlines) - 1)
                    )
                    state_deadline_drop_events += drop_events
                    if drop_events > 0:
                        state_deadline_drop_ladders += 1
                        if state_drop_example is None:
                            state_drop_example = profile

                    if all(entry['schedule_class'] == 'impossible' for entry in ladder) and state_impossible_example is None:
                        state_impossible_example = profile

    for current_batch_length in BATCH_GRID:
        for hold_cost in HOLD_COST_GRID:
            for target_margin in POSITIVE_TARGET_MARGIN_GRID:
                profile = compute_universal_live_hazard_staircase_profile(
                    current_batch_length,
                    hold_cost.numerator,
                    hold_cost.denominator,
                    target_margin.numerator,
                    target_margin.denominator,
                )
                ladder = profile['ladder']
                validated_universal_ladders += 1
                validated_universal_contexts += len(ladder)

                class_ranks = [_schedule_rank(str(entry['schedule_class'])) for entry in ladder]
                if class_ranks == sorted(class_ranks):
                    universal_monotone_class_ladders += 1
                else:
                    raise GeometricArrivalLiveHazardStaircaseLawError('universal class ladder regressed with higher arrival hazard')
                if any(class_ranks[i] < class_ranks[i + 1] for i in range(len(class_ranks) - 1)):
                    universal_class_improvement_ladders += 1

                finite_flags = [entry['schedule_class'] == 'finite' for entry in ladder]
                first_finite_index = next((i for i, flag in enumerate(finite_flags) if flag), None)
                if first_finite_index is None or all(finite_flags[first_finite_index:]):
                    universal_suffix_finite_ladders += 1
                else:
                    raise GeometricArrivalLiveHazardStaircaseLawError('universal finite region was not a hazard suffix')

                finite_deadlines = [int(entry['minimum_nominal_live_deadline_ticks']) for entry in ladder if entry['schedule_class'] == 'finite']
                universal_finite_deadline_observations += len(finite_deadlines)
                universal_odd_finite_deadline_observations += sum(deadline % 2 == 1 for deadline in finite_deadlines)
                if any(deadline % 2 == 0 for deadline in finite_deadlines):
                    raise GeometricArrivalLiveHazardStaircaseLawError('universal finite minimum deadline was not odd')
                if finite_deadlines == sorted(finite_deadlines, reverse=True):
                    universal_nonincreasing_finite_deadline_ladders += 1
                else:
                    raise GeometricArrivalLiveHazardStaircaseLawError('universal finite deadlines increased with higher arrival hazard')
                drop_events = sum(
                    finite_deadlines[i] > finite_deadlines[i + 1]
                    for i in range(len(finite_deadlines) - 1)
                )
                universal_deadline_drop_events += drop_events
                if drop_events > 0:
                    universal_deadline_drop_ladders += 1
                    if universal_drop_example is None:
                        universal_drop_example = profile

                if all(entry['schedule_class'] == 'impossible' for entry in ladder) and universal_impossible_example is None:
                    universal_impossible_example = profile

    if state_drop_example is None or state_impossible_example is None:
        raise GeometricArrivalLiveHazardStaircaseLawError('expected both state drop and impossible examples on the audited grid')
    if universal_drop_example is None or universal_impossible_example is None:
        raise GeometricArrivalLiveHazardStaircaseLawError('expected both universal drop and impossible examples on the audited grid')

    return {
        'validated_state_ladders': validated_state_ladders,
        'validated_state_contexts': validated_state_contexts,
        'validated_universal_ladders': validated_universal_ladders,
        'validated_universal_contexts': validated_universal_contexts,
        'state_monotone_class_ladders': state_monotone_class_ladders,
        'universal_monotone_class_ladders': universal_monotone_class_ladders,
        'state_nonincreasing_finite_deadline_ladders': state_nonincreasing_finite_deadline_ladders,
        'universal_nonincreasing_finite_deadline_ladders': universal_nonincreasing_finite_deadline_ladders,
        'state_suffix_finite_ladders': state_suffix_finite_ladders,
        'universal_suffix_finite_ladders': universal_suffix_finite_ladders,
        'state_finite_deadline_observations': state_finite_deadline_observations,
        'universal_finite_deadline_observations': universal_finite_deadline_observations,
        'state_odd_finite_deadline_observations': state_odd_finite_deadline_observations,
        'universal_odd_finite_deadline_observations': universal_odd_finite_deadline_observations,
        'state_deadline_drop_ladders': state_deadline_drop_ladders,
        'universal_deadline_drop_ladders': universal_deadline_drop_ladders,
        'state_deadline_drop_events': state_deadline_drop_events,
        'universal_deadline_drop_events': universal_deadline_drop_events,
        'state_class_improvement_ladders': state_class_improvement_ladders,
        'universal_class_improvement_ladders': universal_class_improvement_ladders,
        'state_drop_example': state_drop_example,
        'state_impossible_example': state_impossible_example,
        'universal_drop_example': universal_drop_example,
        'universal_impossible_example': universal_impossible_example,
    }


@lru_cache(maxsize=1)
def build_geometric_arrival_live_hazard_staircase_snapshot() -> dict[str, Any]:
    summary = build_geometric_arrival_live_hazard_staircase_validation_summary()
    return {
        'focus': 'same-deadline live positive promise admission over arrival hazard',
        'headline_findings': {
            'state_ladders_validated': summary['validated_state_ladders'],
            'universal_ladders_validated': summary['validated_universal_ladders'],
            'state_deadline_drop_ladders': summary['state_deadline_drop_ladders'],
            'universal_deadline_drop_ladders': summary['universal_deadline_drop_ladders'],
            'state_deadline_drop_events': summary['state_deadline_drop_events'],
            'universal_deadline_drop_events': summary['universal_deadline_drop_events'],
            'state_class_improvement_ladders': summary['state_class_improvement_ladders'],
            'universal_class_improvement_ladders': summary['universal_class_improvement_ladders'],
        },
        'decision_rules': [
            'for a fixed positive same-deadline live promise, higher arrival hazard never requires a longer minimum deadline',
            'schedule classes can only improve with hazard under impossible < asymptotic_only < finite',
            'every finite minimum same-deadline live deadline lies on the odd ladder 1,3,5,...',
            'so hazard uncertainty can be compiled into a one-way odd staircase rather than a fresh solve at each arrival estimate',
        ],
        'state_drop_example': summary['state_drop_example'],
        'state_impossible_example': summary['state_impossible_example'],
        'universal_drop_example': summary['universal_drop_example'],
        'universal_impossible_example': summary['universal_impossible_example'],
        'validation_summary': {
            key: value for key, value in summary.items() if key not in {
                'state_drop_example',
                'state_impossible_example',
                'universal_drop_example',
                'universal_impossible_example',
            }
        },
        'analysis_script': 'scripts/analysis/geometric_arrival_live_hazard_staircase_law.py',
        'source_reports': [
            'artifacts/reports/geometric_arrival_live_deadline_formula_law_snapshot_20260316.json',
            'artifacts/reports/geometric_arrival_live_arrival_floor_law_snapshot_20260316.json',
        ],
    }


def main() -> None:
    json.dump(build_geometric_arrival_live_hazard_staircase_snapshot(), sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write('\n')


if __name__ == '__main__':
    main()
