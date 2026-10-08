#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import sys
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_dense_index_law import (
    build_all_realized_feasible_interval_states,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_feasible_interval_law import (
    FeasibleIntervalKernelState,
    serialize_feasible_interval_kernel_state,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_threshold_law import (
    build_shared_interval_state_equiprobable_exact_shortest_script_threshold_profile,
    summarize_shared_interval_state_exact_shortest_script_batch_by_equiprobable_mean,
)


class WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptMeanCostLawError(RuntimeError):
    pass


@lru_cache(maxsize=None)
def _normalize_state(state: tuple[int, int] | list[int]) -> FeasibleIntervalKernelState:
    if len(state) != 2:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptMeanCostLawError(
            'feasible interval state must contain exactly two ranks'
        )
    lower_rank = int(state[0])
    upper_rank = int(state[1])
    if lower_rank < 0 or upper_rank < lower_rank or upper_rank > 16:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptMeanCostLawError(
            'feasible interval state must stay within the realized 17-rank path bounds'
        )
    return lower_rank, upper_rank


MEAN_COST_FAMILY_FORMULAS: dict[str, dict[str, Any]] = {
    'seven_bit_unique_word_cost': {
        'local_mean_numerator': 0,
        'local_mean_denominator': 1,
        'overhead_numerator': 7,
        'formula': '7/n',
        'state_class_description': 'identity and 7-bit one-sided unique-word states',
    },
    'eight_bit_unique_word_cost': {
        'local_mean_numerator': 0,
        'local_mean_denominator': 1,
        'overhead_numerator': 8,
        'formula': '8/n',
        'state_class_description': '8-bit one-sided unique-word states',
    },
    'seven_bit_interior_nonsingleton_cost': {
        'local_mean_numerator': 1,
        'local_mean_denominator': 1,
        'overhead_numerator': 7,
        'formula': '1 + 7/n',
        'state_class_description': '7-bit interior nonsingleton states',
    },
    'eight_bit_interior_nonsingleton_cost': {
        'local_mean_numerator': 1,
        'local_mean_denominator': 1,
        'overhead_numerator': 8,
        'formula': '1 + 8/n',
        'state_class_description': '8-bit interior nonsingleton states',
    },
    'seven_bit_interior_singleton_cost': {
        'local_mean_numerator': 38,
        'local_mean_denominator': 9,
        'overhead_numerator': 7,
        'formula': '38/9 + 7/n',
        'state_class_description': '7-bit interior singleton states',
    },
    'eight_bit_interior_singleton_cost': {
        'local_mean_numerator': 38,
        'local_mean_denominator': 9,
        'overhead_numerator': 8,
        'formula': '38/9 + 8/n',
        'state_class_description': '8-bit interior singleton states',
    },
}


@lru_cache(maxsize=None)
def classify_shared_interval_state_equiprobable_exact_shortest_script_mean_cost_family(
    state: tuple[int, int] | list[int],
) -> str:
    state = _normalize_state(state)
    profile = build_shared_interval_state_equiprobable_exact_shortest_script_threshold_profile(state)
    signature = (
        str(profile['state_category']),
        int(profile['state_prefix_bit_length']),
        int(profile['family_cardinality']),
        int(profile['total_local_choice_prefix_bits']),
    )
    signature_to_family = {
        ('identity', 7, 1, 0): 'seven_bit_unique_word_cost',
        ('one_sided_nonidentity', 7, 1, 0): 'seven_bit_unique_word_cost',
        ('one_sided_nonidentity', 8, 1, 0): 'eight_bit_unique_word_cost',
        ('interior_nonsingleton', 7, 2, 2): 'seven_bit_interior_nonsingleton_cost',
        ('interior_nonsingleton', 8, 2, 2): 'eight_bit_interior_nonsingleton_cost',
        ('interior_singleton', 7, 18, 76): 'seven_bit_interior_singleton_cost',
        ('interior_singleton', 8, 18, 76): 'eight_bit_interior_singleton_cost',
    }
    try:
        return signature_to_family[signature]
    except KeyError as exc:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptMeanCostLawError(
            f'unrecognized mean-cost signature for state {state}: {signature}'
        ) from exc


@lru_cache(maxsize=None)
def build_shared_interval_state_equiprobable_exact_shortest_script_mean_cost_profile(
    state: tuple[int, int] | list[int],
) -> dict[str, Any]:
    state = _normalize_state(state)
    threshold_profile = build_shared_interval_state_equiprobable_exact_shortest_script_threshold_profile(state)
    family_name = classify_shared_interval_state_equiprobable_exact_shortest_script_mean_cost_family(state)
    formula = MEAN_COST_FAMILY_FORMULAS[family_name]
    local_mean = Fraction(int(formula['local_mean_numerator']), int(formula['local_mean_denominator']))
    overhead = Fraction(int(formula['overhead_numerator']), 1)
    return {
        **threshold_profile,
        'mean_cost_family': family_name,
        'mean_cost_formula': formula['formula'],
        'mean_cost_state_class_description': formula['state_class_description'],
        'equiprobable_local_choice_floor_bits_per_script': {
            'numerator': local_mean.numerator,
            'denominator': local_mean.denominator,
            'decimal': float(local_mean),
        },
        'state_prefix_overhead_bits': {
            'numerator': overhead.numerator,
            'denominator': overhead.denominator,
            'decimal': float(overhead),
        },
    }


@lru_cache(maxsize=None)
def evaluate_shared_interval_state_equiprobable_exact_shortest_script_mean_cost(
    state: tuple[int, int] | list[int],
    batch_length: int,
) -> dict[str, Any]:
    state = _normalize_state(state)
    batch_length = int(batch_length)
    if batch_length <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptMeanCostLawError(
            'batch length must be positive'
        )
    profile = build_shared_interval_state_equiprobable_exact_shortest_script_mean_cost_profile(state)
    local_floor = Fraction(
        int(profile['equiprobable_local_choice_floor_bits_per_script']['numerator']),
        int(profile['equiprobable_local_choice_floor_bits_per_script']['denominator']),
    )
    overhead = Fraction(int(profile['state_prefix_overhead_bits']['numerator']), 1)
    per_script_cost = local_floor + overhead / batch_length
    return {
        **profile,
        'batch_length': batch_length,
        'equiprobable_mean_shared_state_transport_bits_per_script': {
            'numerator': per_script_cost.numerator,
            'denominator': per_script_cost.denominator,
            'decimal': float(per_script_cost),
        },
    }


def _serialize_fraction(value: Fraction) -> dict[str, int | float]:
    return {
        'numerator': value.numerator,
        'denominator': value.denominator,
        'decimal': float(value),
    }


@lru_cache(maxsize=None)
def compute_min_batch_length_for_state_target_mean_cost(
    state: tuple[int, int] | list[int],
    target_bits_numerator: int,
    target_bits_denominator: int = 1,
) -> dict[str, Any]:
    state = _normalize_state(state)
    target = Fraction(int(target_bits_numerator), int(target_bits_denominator))
    profile = build_shared_interval_state_equiprobable_exact_shortest_script_mean_cost_profile(state)
    local_floor = Fraction(
        int(profile['equiprobable_local_choice_floor_bits_per_script']['numerator']),
        int(profile['equiprobable_local_choice_floor_bits_per_script']['denominator']),
    )
    overhead = Fraction(int(profile['state_prefix_overhead_bits']['numerator']), 1)

    if target <= local_floor:
        return {
            **profile,
            'target_mean_cost_bits_per_script': _serialize_fraction(target),
            'minimum_batch_length': None,
            'attainable_with_finite_batch': False,
            'reason': 'target_at_or_below_local_choice_floor',
            'previous_batch_mean_cost_bits_per_script': None,
            'achieved_mean_cost_bits_per_script': None,
        }

    required = Fraction(overhead, target - local_floor)
    minimum_batch_length = max(1, math.ceil(required.numerator / required.denominator))
    achieved = local_floor + overhead / minimum_batch_length
    previous = local_floor + overhead / (minimum_batch_length - 1) if minimum_batch_length > 1 else None
    return {
        **profile,
        'target_mean_cost_bits_per_script': _serialize_fraction(target),
        'minimum_batch_length': minimum_batch_length,
        'attainable_with_finite_batch': True,
        'reason': 'closed_form_ceiling_inversion',
        'previous_batch_mean_cost_bits_per_script': _serialize_fraction(previous) if previous is not None else None,
        'achieved_mean_cost_bits_per_script': _serialize_fraction(achieved),
    }


@lru_cache(maxsize=None)
def compute_universal_min_batch_length_for_target_mean_cost(
    target_bits_numerator: int,
    target_bits_denominator: int = 1,
) -> dict[str, Any]:
    target = Fraction(int(target_bits_numerator), int(target_bits_denominator))
    local_floor = Fraction(38, 9)
    overhead = Fraction(8, 1)
    if target <= local_floor:
        return {
            'target_mean_cost_bits_per_script': _serialize_fraction(target),
            'minimum_batch_length': None,
            'attainable_with_finite_batch': False,
            'guarantee_scope': 'all_realized_states',
            'guarantee_family': 'eight_bit_interior_singleton_cost',
            'guarantee_formula': '38/9 + 8/n',
            'reason': 'target_at_or_below_universal_asymptotic_floor',
        }
    required = Fraction(overhead, target - local_floor)
    minimum_batch_length = max(1, math.ceil(required.numerator / required.denominator))
    achieved = local_floor + overhead / minimum_batch_length
    previous = local_floor + overhead / (minimum_batch_length - 1) if minimum_batch_length > 1 else None
    return {
        'target_mean_cost_bits_per_script': _serialize_fraction(target),
        'minimum_batch_length': minimum_batch_length,
        'attainable_with_finite_batch': True,
        'guarantee_scope': 'all_realized_states',
        'guarantee_family': 'eight_bit_interior_singleton_cost',
        'guarantee_formula': '38/9 + 8/n',
        'reason': 'closed_form_ceiling_inversion',
        'achieved_mean_cost_bits_per_script': _serialize_fraction(achieved),
        'previous_batch_mean_cost_bits_per_script': _serialize_fraction(previous) if previous is not None else None,
    }


@lru_cache(maxsize=1)
def build_mean_cost_family_summary() -> dict[str, Any]:
    states = build_all_realized_feasible_interval_states()
    family_counts: Counter[str] = Counter()
    representatives: dict[str, list[int]] = {}
    for raw_state in states:
        state = tuple(raw_state)
        family = classify_shared_interval_state_equiprobable_exact_shortest_script_mean_cost_family(state)
        family_counts[family] += 1
        representatives.setdefault(family, list(state))

    ordered_families = []
    for family_name in [
        'seven_bit_unique_word_cost',
        'eight_bit_unique_word_cost',
        'seven_bit_interior_nonsingleton_cost',
        'eight_bit_interior_nonsingleton_cost',
        'seven_bit_interior_singleton_cost',
        'eight_bit_interior_singleton_cost',
    ]:
        formula = MEAN_COST_FAMILY_FORMULAS[family_name]
        ordered_families.append({
            'family_name': family_name,
            'state_count': family_counts[family_name],
            'representative_state': serialize_feasible_interval_kernel_state(tuple(representatives[family_name])),
            'mean_cost_formula': formula['formula'],
            'state_class_description': formula['state_class_description'],
        })

    return {
        'family_count': len(family_counts),
        'families': ordered_families,
    }


@lru_cache(maxsize=1)
def build_mean_cost_validation_summary() -> dict[str, Any]:
    states = [tuple(state) for state in build_all_realized_feasible_interval_states()]
    audited_batch_lengths = tuple(range(1, 9))
    matched_cost_cases = 0
    for raw_state in states:
        for batch_length in audited_batch_lengths:
            direct = summarize_shared_interval_state_exact_shortest_script_batch_by_equiprobable_mean(raw_state, batch_length)
            direct_per_script = Fraction(
                int(direct['equiprobable_mean_shared_state_transport_bits']['numerator']),
                int(direct['equiprobable_mean_shared_state_transport_bits']['denominator']),
            ) / batch_length
            law = evaluate_shared_interval_state_equiprobable_exact_shortest_script_mean_cost(raw_state, batch_length)
            law_cost = Fraction(
                int(law['equiprobable_mean_shared_state_transport_bits_per_script']['numerator']),
                int(law['equiprobable_mean_shared_state_transport_bits_per_script']['denominator']),
            )
            if direct_per_script != law_cost:
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptMeanCostLawError(
                    f'mean cost mismatch for state {raw_state}, batch length {batch_length}: {direct_per_script} != {law_cost}'
                )
            matched_cost_cases += 1

    audited_targets = [Fraction(5, 1), Fraction(6, 1), Fraction(7, 1), Fraction(8, 1), Fraction(9, 1)]
    state_target_matches = 0
    for raw_state in states:
        for target in audited_targets:
            summary = compute_min_batch_length_for_state_target_mean_cost(raw_state, target.numerator, target.denominator)
            n = summary['minimum_batch_length']
            if n is None:
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptMeanCostLawError(
                    f'audited target {target} unexpectedly unattainable for state {raw_state}'
                )
            achieved = Fraction(
                int(summary['achieved_mean_cost_bits_per_script']['numerator']),
                int(summary['achieved_mean_cost_bits_per_script']['denominator']),
            )
            if achieved > target:
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptMeanCostLawError(
                    f'target {target} missed for state {raw_state} at batch length {n}'
                )
            if n > 1:
                previous = Fraction(
                    int(summary['previous_batch_mean_cost_bits_per_script']['numerator']),
                    int(summary['previous_batch_mean_cost_bits_per_script']['denominator']),
                )
                if previous <= target:
                    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptMeanCostLawError(
                        f'threshold not minimal for state {raw_state} and target {target}'
                    )
            state_target_matches += 1

    universal_targets = [Fraction(5, 1), Fraction(6, 1), Fraction(7, 1), Fraction(8, 1), Fraction(9, 1)]
    universal_matches = 0
    for target in universal_targets:
        summary = compute_universal_min_batch_length_for_target_mean_cost(target.numerator, target.denominator)
        n = summary['minimum_batch_length']
        if n is None:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptMeanCostLawError(
                f'audited universal target {target} unexpectedly unattainable'
            )
        for raw_state in states:
            achieved = Fraction(
                int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_mean_cost(raw_state, n)['equiprobable_mean_shared_state_transport_bits_per_script']['numerator']),
                int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_mean_cost(raw_state, n)['equiprobable_mean_shared_state_transport_bits_per_script']['denominator']),
            )
            if achieved > target:
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptMeanCostLawError(
                    f'universal target {target} missed for state {raw_state} at batch length {n}'
                )
        if n > 1:
            previous_worst = max(
                Fraction(
                    int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_mean_cost(raw_state, n - 1)['equiprobable_mean_shared_state_transport_bits_per_script']['numerator']),
                    int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_mean_cost(raw_state, n - 1)['equiprobable_mean_shared_state_transport_bits_per_script']['denominator']),
                )
                for raw_state in states
            )
            if previous_worst <= target:
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptMeanCostLawError(
                    f'universal threshold not minimal for target {target}'
                )
        universal_matches += 1

    impossible_universal_targets = [Fraction(4, 1), Fraction(38, 9)]
    impossible_target_matches = 0
    for target in impossible_universal_targets:
        summary = compute_universal_min_batch_length_for_target_mean_cost(target.numerator, target.denominator)
        if summary['minimum_batch_length'] is not None or summary['attainable_with_finite_batch']:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptMeanCostLawError(
                f'universal target {target} should be impossible'
            )
        impossible_target_matches += 1

    maximum_universal_cost_by_batch_length = []
    for batch_length in audited_batch_lengths:
        costs = [
            Fraction(
                int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_mean_cost(state, batch_length)['equiprobable_mean_shared_state_transport_bits_per_script']['numerator']),
                int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_mean_cost(state, batch_length)['equiprobable_mean_shared_state_transport_bits_per_script']['denominator']),
            )
            for state in states
        ]
        worst_cost = max(costs)
        maximizers = [
            state for state in states
            if Fraction(
                int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_mean_cost(state, batch_length)['equiprobable_mean_shared_state_transport_bits_per_script']['numerator']),
                int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_mean_cost(state, batch_length)['equiprobable_mean_shared_state_transport_bits_per_script']['denominator']),
            ) == worst_cost
        ]
        maximum_universal_cost_by_batch_length.append({
            'batch_length': batch_length,
            'maximum_cost_bits_per_script': _serialize_fraction(worst_cost),
            'maximizer_count': len(maximizers),
            'representative_maximizer_state': serialize_feasible_interval_kernel_state(maximizers[0]),
            'maximizer_mean_cost_family': classify_shared_interval_state_equiprobable_exact_shortest_script_mean_cost_family(maximizers[0]),
        })

    return {
        'audited_state_count': len(states),
        'audited_batch_lengths': list(audited_batch_lengths),
        'validated_state_batch_cost_pairs': matched_cost_cases,
        'audited_target_count': len(audited_targets),
        'validated_state_target_pairs': state_target_matches,
        'validated_universal_targets': universal_matches,
        'validated_impossible_universal_targets': impossible_target_matches,
        'maximum_universal_cost_by_batch_length': maximum_universal_cost_by_batch_length,
        'universal_upper_envelope_formula': '38/9 + 8/n',
        'universal_asymptotic_floor_bits_per_script': _serialize_fraction(Fraction(38, 9)),
    }


@lru_cache(maxsize=1)
def build_mean_cost_examples() -> list[dict[str, Any]]:
    examples = []
    for state in [(0, 16), (1, 2), (8, 8), (15, 15), (7, 12)]:
        profile = build_shared_interval_state_equiprobable_exact_shortest_script_mean_cost_profile(state)
        costs = {
            str(batch_length): evaluate_shared_interval_state_equiprobable_exact_shortest_script_mean_cost(state, batch_length)['equiprobable_mean_shared_state_transport_bits_per_script']
            for batch_length in (1, 2, 3, 5)
        }
        examples.append({
            'interval_kernel_state': profile['interval_kernel_state'],
            'mean_cost_family': profile['mean_cost_family'],
            'mean_cost_formula': profile['mean_cost_formula'],
            'cost_bits_per_script_by_batch_length': costs,
        })
    return examples


@lru_cache(maxsize=1)
def build_target_mean_cost_examples() -> list[dict[str, Any]]:
    examples = []
    for state, target in [
        ((0, 16), Fraction(4, 1)),
        ((7, 12), Fraction(5, 1)),
        ((8, 8), Fraction(5, 1)),
        ((15, 15), Fraction(38, 9)),
        ((1, 2), Fraction(3, 1)),
    ]:
        summary = compute_min_batch_length_for_state_target_mean_cost(state, target.numerator, target.denominator)
        examples.append({
            'interval_kernel_state': summary['interval_kernel_state'],
            'target_mean_cost_bits_per_script': summary['target_mean_cost_bits_per_script'],
            'mean_cost_family': summary['mean_cost_family'],
            'minimum_batch_length': summary['minimum_batch_length'],
            'attainable_with_finite_batch': summary['attainable_with_finite_batch'],
            'achieved_mean_cost_bits_per_script': summary['achieved_mean_cost_bits_per_script'],
            'previous_batch_mean_cost_bits_per_script': summary['previous_batch_mean_cost_bits_per_script'],
        })
    return examples


@lru_cache(maxsize=1)
def build_universal_target_schedule() -> list[dict[str, Any]]:
    targets = [Fraction(5, 1), Fraction(6, 1), Fraction(7, 1), Fraction(8, 1), Fraction(9, 1)]
    schedule = []
    for target in targets:
        summary = compute_universal_min_batch_length_for_target_mean_cost(target.numerator, target.denominator)
        schedule.append({
            'target_mean_cost_bits_per_script': summary['target_mean_cost_bits_per_script'],
            'minimum_batch_length': summary['minimum_batch_length'],
            'achieved_mean_cost_bits_per_script': summary['achieved_mean_cost_bits_per_script'],
        })
    schedule.append({
        'target_mean_cost_bits_per_script': _serialize_fraction(Fraction(38, 9)),
        'minimum_batch_length': None,
        'attainable_with_finite_batch': False,
    })
    return schedule


@lru_cache(maxsize=1)
def build_headline_findings() -> dict[str, Any]:
    return {
        'catalog_state_count': 153,
        'mean_cost_family_count': 6,
        'universal_upper_envelope_formula': '38/9 + 8/n',
        'universal_asymptotic_floor_bits_per_script': _serialize_fraction(Fraction(38, 9)),
        'no_finite_universal_batch_at_or_below_floor': True,
        'universal_examples': {
            'target_5_bits_per_script': 11,
            'target_6_bits_per_script': 5,
            'target_7_bits_per_script': 3,
            'target_8_bits_per_script': 3,
            'target_9_bits_per_script': 2,
        },
    }


@lru_cache(maxsize=1)
def build_decision_rules() -> list[str]:
    return [
        'When the equiprobable shared-state exact-branch model is active, budget expected shared-state transport directly in bits per script as `local_choice_floor + state_prefix_bits / batch_length` instead of recomputing batch totals.',
        'Use `38/9 + 8/n` as the current universal upper envelope over all realized states; it is the only formula needed for all-state guarantees.',
        'Treat `38/9` bits per script as a hard asymptotic floor for the current all-state guarantee: no finite shared-state batch can force every realized state to or below that ceiling.',
        'Invert the budget rule by `ceil(state_prefix_bits / (target_bits_per_script - local_choice_floor_bits_per_script))` whenever the target lies strictly above the local floor.',
    ]


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_mean_cost_snapshot() -> dict[str, Any]:
    return {
        'focus': 'Under the equiprobable shared-state exact-branch model, expected shared-state transport cost per script collapses to six reciprocal-overhead families with one universal all-state envelope.',
        'headline_findings': build_headline_findings(),
        'decision_rules': build_decision_rules(),
        'mean_cost_family_summary': build_mean_cost_family_summary(),
        'mean_cost_examples': build_mean_cost_examples(),
        'target_mean_cost_examples': build_target_mean_cost_examples(),
        'universal_target_schedule': build_universal_target_schedule(),
        'validation_summary': build_mean_cost_validation_summary(),
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_affine_margin_law_snapshot_20260309.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_target_margin_law_snapshot_20260309.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_threshold_law_snapshot_20260309.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_prefix_law_snapshot_20260309.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_prefix_law_snapshot_20260309.json',
        ],
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_mean_cost_law.py',
    }


if __name__ == '__main__':
    print(json.dumps(build_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_mean_cost_snapshot(), indent=2, sort_keys=True))
