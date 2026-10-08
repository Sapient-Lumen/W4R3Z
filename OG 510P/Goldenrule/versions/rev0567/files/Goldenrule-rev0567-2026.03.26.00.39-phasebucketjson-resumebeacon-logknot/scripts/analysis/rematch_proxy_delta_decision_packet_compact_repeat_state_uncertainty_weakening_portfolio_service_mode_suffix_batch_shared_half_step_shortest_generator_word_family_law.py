#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_feasible_interval_law import (
    FeasibleIntervalKernelState,
    serialize_feasible_interval_kernel_state,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_normal_form_law import (
    MAX_SOURCE_RANK,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_law import (
    GeneratorInterval,
    GeneratorWord,
    build_shortest_generator_words_by_feasible_interval_state,
    serialize_generator_word,
)


class WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordFamilyLawError(RuntimeError):
    pass


IntervalCategory = Literal[
    'identity',
    'one_sided_nonidentity',
    'interior_nonsingleton',
    'interior_singleton',
]


@lru_cache(maxsize=None)
def _normalize_feasible_interval_state(
    state: tuple[int, int] | list[int],
) -> FeasibleIntervalKernelState:
    if len(state) != 2:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordFamilyLawError(
            'feasible interval state must contain exactly two ranks'
        )
    lower_rank = int(state[0])
    upper_rank = int(state[1])
    if lower_rank < 0 or upper_rank < lower_rank or upper_rank > MAX_SOURCE_RANK:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordFamilyLawError(
            'feasible interval state must stay within the realized 17-state path bounds'
        )
    return lower_rank, upper_rank


@lru_cache(maxsize=None)
def classify_feasible_interval_state(
    state: tuple[int, int] | list[int],
) -> IntervalCategory:
    lower_rank, upper_rank = _normalize_feasible_interval_state(state)
    if lower_rank == 0 and upper_rank == MAX_SOURCE_RANK:
        return 'identity'
    if lower_rank == 0 or upper_rank == MAX_SOURCE_RANK:
        return 'one_sided_nonidentity'
    if lower_rank == upper_rank:
        return 'interior_singleton'
    return 'interior_nonsingleton'


@lru_cache(maxsize=None)
def build_closed_form_shortest_generator_words_for_feasible_interval_state(
    state: tuple[int, int] | list[int],
) -> tuple[GeneratorWord, ...]:
    lower_rank, upper_rank = _normalize_feasible_interval_state(state)
    category = classify_feasible_interval_state((lower_rank, upper_rank))
    if category == 'identity':
        return ((),)
    if category == 'one_sided_nonidentity':
        if upper_rank == MAX_SOURCE_RANK:
            return (((lower_rank, MAX_SOURCE_RANK),),)
        return (((0, upper_rank),),)
    if category == 'interior_nonsingleton':
        return tuple(
            sorted(
                (
                    ((lower_rank, MAX_SOURCE_RANK), (0, upper_rank)),
                    ((0, upper_rank), (lower_rank, MAX_SOURCE_RANK)),
                )
            )
        )

    left_cap_fan = [((0, cap_rank), (lower_rank, MAX_SOURCE_RANK)) for cap_rank in range(lower_rank + 1)]
    right_floor_fan = [((floor_rank, MAX_SOURCE_RANK), (0, upper_rank)) for floor_rank in range(lower_rank, MAX_SOURCE_RANK + 1)]
    return tuple(sorted((*left_cap_fan, *right_floor_fan)))


@lru_cache(maxsize=None)
def build_shortest_generator_word_family_cardinality_for_feasible_interval_state(
    state: tuple[int, int] | list[int],
) -> int:
    lower_rank, upper_rank = _normalize_feasible_interval_state(state)
    category = classify_feasible_interval_state((lower_rank, upper_rank))
    if category in {'identity', 'one_sided_nonidentity'}:
        return 1
    if category == 'interior_nonsingleton':
        return 2
    return MAX_SOURCE_RANK + 2


@lru_cache(maxsize=1)
def build_batch_shared_half_step_shortest_generator_word_family_examples() -> list[dict[str, Any]]:
    interior_nonsingleton = (3, 8)
    interior_singleton = (5, 5)
    endpoint_singleton = (0, 0)

    singleton_family = build_closed_form_shortest_generator_words_for_feasible_interval_state(interior_singleton)
    left_cap_fan = [word for word in singleton_family if len(word) == 2 and word[0][0] == 0]
    right_floor_fan = [word for word in singleton_family if len(word) == 2 and word[0][1] == MAX_SOURCE_RANK]

    return [
        {
            'identity_interval_has_the_unique_empty_shortest_word': {
                'interval_kernel_state': serialize_feasible_interval_kernel_state((0, MAX_SOURCE_RANK)),
                'closed_form_shortest_generator_words': [serialize_generator_word(word) for word in build_closed_form_shortest_generator_words_for_feasible_interval_state((0, MAX_SOURCE_RANK))],
            }
        },
        {
            'endpoint_singleton_is_still_one_sided_and_has_one_shortest_word': {
                'interval_kernel_state': serialize_feasible_interval_kernel_state(endpoint_singleton),
                'category': classify_feasible_interval_state(endpoint_singleton),
                'closed_form_shortest_generator_words': [serialize_generator_word(word) for word in build_closed_form_shortest_generator_words_for_feasible_interval_state(endpoint_singleton)],
            }
        },
        {
            'interior_nonsingleton_interval_has_exactly_the_two_orderings_of_floor_and_cap': {
                'interval_kernel_state': serialize_feasible_interval_kernel_state(interior_nonsingleton),
                'closed_form_shortest_generator_words': [serialize_generator_word(word) for word in build_closed_form_shortest_generator_words_for_feasible_interval_state(interior_nonsingleton)],
            }
        },
        {
            'interior_singleton_interval_splits_into_left_cap_and_right_floor_fans': {
                'interval_kernel_state': serialize_feasible_interval_kernel_state(interior_singleton),
                'left_cap_fan_cardinality': len(left_cap_fan),
                'right_floor_fan_cardinality': len(right_floor_fan),
                'total_shortest_word_count': len(singleton_family),
                'sample_left_cap_fan_words': [serialize_generator_word(word) for word in left_cap_fan[:3]],
                'sample_right_floor_fan_words': [serialize_generator_word(word) for word in right_floor_fan[:3]],
            }
        },
    ]


@lru_cache(maxsize=1)
def build_batch_shared_half_step_shortest_generator_word_family_validation_summary() -> dict[str, Any]:
    brute_force = build_shortest_generator_words_by_feasible_interval_state()
    category_state_counter: Counter[str] = Counter()
    category_word_counter: Counter[str] = Counter()
    category_multiplicity_counter: dict[str, Counter[int]] = {
        'identity': Counter(),
        'one_sided_nonidentity': Counter(),
        'interior_nonsingleton': Counter(),
        'interior_singleton': Counter(),
    }

    total_shortest_word_count = 0
    all_closed_form_families_match_bruteforce = True
    all_cardinality_formulas_match = True
    interior_singleton_fan_split_is_exact = True
    interior_nonsingleton_words_are_exactly_the_two_orderings = True
    all_nontrivial_nonuniqueness_beyond_swapped_order_is_concentrated_in_interior_singletons = True

    for state, brute_force_words in brute_force.items():
        category = classify_feasible_interval_state(state)
        closed_form_words = build_closed_form_shortest_generator_words_for_feasible_interval_state(state)
        if closed_form_words != brute_force_words:
            all_closed_form_families_match_bruteforce = False
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordFamilyLawError(
                f'closed-form shortest generator word family mismatch for state {state}: expected {brute_force_words}, got {closed_form_words}'
            )
        expected_cardinality = build_shortest_generator_word_family_cardinality_for_feasible_interval_state(state)
        if len(closed_form_words) != expected_cardinality:
            all_cardinality_formulas_match = False
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordFamilyLawError(
                f'shortest generator word family cardinality mismatch for state {state}'
            )

        category_state_counter[category] += 1
        category_word_counter[category] += len(closed_form_words)
        category_multiplicity_counter[category][len(closed_form_words)] += 1
        total_shortest_word_count += len(closed_form_words)

        if category == 'interior_singleton':
            lower_rank, _ = state
            left_cap_fan = tuple(((0, cap_rank), (lower_rank, MAX_SOURCE_RANK)) for cap_rank in range(lower_rank + 1))
            right_floor_fan = tuple(((floor_rank, MAX_SOURCE_RANK), (0, lower_rank)) for floor_rank in range(lower_rank, MAX_SOURCE_RANK + 1))
            if tuple(sorted((*left_cap_fan, *right_floor_fan))) != closed_form_words:
                interior_singleton_fan_split_is_exact = False
        elif category == 'interior_nonsingleton':
            lower_rank, upper_rank = state
            expected_two_orderings = tuple(sorted((((lower_rank, MAX_SOURCE_RANK), (0, upper_rank)), ((0, upper_rank), (lower_rank, MAX_SOURCE_RANK)))))
            if closed_form_words != expected_two_orderings:
                interior_nonsingleton_words_are_exactly_the_two_orderings = False
        elif len(closed_form_words) > 2:
            all_nontrivial_nonuniqueness_beyond_swapped_order_is_concentrated_in_interior_singletons = False

    singleton_shortest_word_share = category_word_counter['interior_singleton'] / total_shortest_word_count

    return {
        'reachable_exact_feasible_interval_kernel_count': len(brute_force),
        'all_closed_form_shortest_word_families_match_bruteforce': all_closed_form_families_match_bruteforce,
        'all_shortest_word_family_cardinality_formulas_match': all_cardinality_formulas_match,
        'total_exact_shortest_generator_word_count': total_shortest_word_count,
        'state_count_by_interval_category': dict(sorted(category_state_counter.items())),
        'total_shortest_generator_word_count_by_interval_category': dict(sorted(category_word_counter.items())),
        'shortest_word_family_multiplicity_by_interval_category': {
            category: dict(sorted(counter.items())) for category, counter in sorted(category_multiplicity_counter.items())
        },
        'interior_singleton_fan_split_is_exact': interior_singleton_fan_split_is_exact,
        'interior_nonsingleton_words_are_exactly_the_two_orderings': interior_nonsingleton_words_are_exactly_the_two_orderings,
        'all_nontrivial_nonuniqueness_beyond_swapped_order_is_concentrated_in_interior_singletons': all_nontrivial_nonuniqueness_beyond_swapped_order_is_concentrated_in_interior_singletons,
        'interior_singleton_share_of_total_shortest_words': singleton_shortest_word_share,
        'represented_exact_shortest_word_catalog_is_closed_form_without_search': True,
    }


@lru_cache(maxsize=1)
def build_headline_findings() -> dict[str, Any]:
    validation = build_batch_shared_half_step_shortest_generator_word_family_validation_summary()
    return {
        'every_exact_shortest_half_step_generator_word_family_is_closed_form': True,
        'reachable_exact_feasible_interval_kernel_count': validation['reachable_exact_feasible_interval_kernel_count'],
        'total_exact_shortest_generator_word_count': validation['total_exact_shortest_generator_word_count'],
        'shortest_word_family_multiplicity_by_interval_category': validation['shortest_word_family_multiplicity_by_interval_category'],
        'interior_singleton_share_of_total_shortest_words': validation['interior_singleton_share_of_total_shortest_words'],
        'validation_summary': validation,
    }


@lru_cache(maxsize=1)
def build_decision_rules() -> list[str]:
    return [
        'When a future inheritor needs all exact shortest scripts for a normalized downstream interval state, derive them from the interval endpoints by closed form instead of enumerating generator words by search.',
        'Use the interval category first. Identity [0,16] has only the empty word. Every non-identity one-sided interval has only itself as a one-generator shortest word.',
        'For every interior nonsingleton interval [a,b] with 0 < a < b < 16, the exact shortest-word family is just the two orderings [[a,16],[0,b]] and [[0,b],[a,16]].',
        'For every interior singleton [c,c], the exact shortest-word family is the union of two fans: [[0,k],[c,16]] for k in 0..c and [[k,16],[0,c]] for k in c..16. Those two fans together always contribute exactly eighteen shortest words.',
        'Treat the canonical shortest-word codec as a deterministic representative chooser inside that larger closed-form family. The only shortest-word multiplicities above two occur for the fifteen interior singleton intervals.',
    ]


@lru_cache(maxsize=1)
def build_source_reports() -> list[str]:
    return [
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_law_snapshot_20260309.md',
        'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_family_law.py',
    ]


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_shared_half_step_shortest_generator_word_family_snapshot() -> dict[str, Any]:
    return {
        'focus': 'Every exact shortest normalized half-step generator-word family is now given by a closed-form interval-category rule.',
        'headline_findings': build_headline_findings(),
        'decision_rules': build_decision_rules(),
        'shortest_generator_word_family_examples': build_batch_shared_half_step_shortest_generator_word_family_examples(),
        'source_reports': build_source_reports(),
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_family_law.py',
    }


def main() -> None:
    print(json.dumps(build_service_mode_suffix_batch_shared_half_step_shortest_generator_word_family_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
