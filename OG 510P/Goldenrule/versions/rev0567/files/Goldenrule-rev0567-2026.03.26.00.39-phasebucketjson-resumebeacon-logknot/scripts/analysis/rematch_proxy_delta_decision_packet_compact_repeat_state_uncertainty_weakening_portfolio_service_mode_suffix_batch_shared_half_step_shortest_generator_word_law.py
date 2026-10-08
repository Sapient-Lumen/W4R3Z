#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_boundary_generator_law import (
    build_distinct_one_sided_generator_intervals,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_feasible_interval_law import (
    FeasibleIntervalKernelState,
    build_feasible_interval_kernel_state_from_generator_stream,
    build_half_step_kernel_from_feasible_interval_state,
    serialize_feasible_interval_kernel_state,
    update_feasible_interval_kernel_state,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_normal_form_law import (
    HALF_STEP_SELECTOR_INDEX_COUNT,
    MAX_SOURCE_RANK,
    apply_generator_stream_directly,
)


class WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordLawError(RuntimeError):
    pass


GeneratorInterval = tuple[int, int]
GeneratorWord = tuple[GeneratorInterval, ...]


@lru_cache(maxsize=1)
def build_one_sided_generator_catalog() -> tuple[GeneratorInterval, ...]:
    return tuple(tuple(interval) for interval in build_distinct_one_sided_generator_intervals())


@lru_cache(maxsize=None)
def _normalize_feasible_interval_state(
    state: tuple[int, int] | list[int],
) -> FeasibleIntervalKernelState:
    if len(state) != 2:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordLawError(
            'feasible interval state must contain exactly two ranks'
        )
    lower_rank = int(state[0])
    upper_rank = int(state[1])
    if lower_rank < 0 or upper_rank < lower_rank or upper_rank > MAX_SOURCE_RANK:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordLawError(
            'feasible interval state must stay within the realized 17-state path bounds'
        )
    return lower_rank, upper_rank


@lru_cache(maxsize=None)
def build_canonical_shortest_generator_word_for_feasible_interval_state(
    state: tuple[int, int] | list[int],
) -> GeneratorWord:
    lower_rank, upper_rank = _normalize_feasible_interval_state(state)
    if lower_rank == 0 and upper_rank == MAX_SOURCE_RANK:
        return ()
    if upper_rank == MAX_SOURCE_RANK:
        return ((lower_rank, MAX_SOURCE_RANK),)
    if lower_rank == 0:
        return ((0, upper_rank),)
    return ((lower_rank, MAX_SOURCE_RANK), (0, upper_rank))


@lru_cache(maxsize=None)
def decode_shortest_generator_word_to_feasible_interval_state(
    generator_word: GeneratorWord,
) -> FeasibleIntervalKernelState:
    state: FeasibleIntervalKernelState = (0, MAX_SOURCE_RANK)
    for interval in generator_word:
        state = update_feasible_interval_kernel_state(state, interval)
    return state


@lru_cache(maxsize=1)
def build_shortest_generator_words_by_feasible_interval_state() -> dict[FeasibleIntervalKernelState, tuple[GeneratorWord, ...]]:
    generator_catalog = build_one_sided_generator_catalog()
    shortest_length_by_state: dict[FeasibleIntervalKernelState, int] = {(0, MAX_SOURCE_RANK): 0}
    shortest_words_by_state: dict[FeasibleIntervalKernelState, list[GeneratorWord]] = {(0, MAX_SOURCE_RANK): [()]}

    for generator_interval in generator_catalog:
        word = (generator_interval,)
        state = decode_shortest_generator_word_to_feasible_interval_state(word)
        shortest_length = shortest_length_by_state.get(state)
        if shortest_length is None or shortest_length > 1:
            shortest_length_by_state[state] = 1
            shortest_words_by_state[state] = [word]
        elif shortest_length == 1:
            shortest_words_by_state[state].append(word)

    for first_interval in generator_catalog:
        for second_interval in generator_catalog:
            word = (first_interval, second_interval)
            state = decode_shortest_generator_word_to_feasible_interval_state(word)
            shortest_length = shortest_length_by_state.get(state)
            if shortest_length is None or shortest_length > 2:
                shortest_length_by_state[state] = 2
                shortest_words_by_state[state] = [word]
            elif shortest_length == 2:
                shortest_words_by_state[state].append(word)

    realized_states = {
        (lower_rank, upper_rank)
        for lower_rank in range(MAX_SOURCE_RANK + 1)
        for upper_rank in range(lower_rank, MAX_SOURCE_RANK + 1)
    }
    if set(shortest_words_by_state) != realized_states:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordLawError(
            'every realized feasible interval state should admit at least one shortest generator word of length 0, 1, or 2'
        )

    return {
        state: tuple(sorted(words))
        for state, words in shortest_words_by_state.items()
    }


@lru_cache(maxsize=None)
def serialize_generator_word(word: GeneratorWord) -> list[list[int]]:
    return [list(interval) for interval in word]


@lru_cache(maxsize=1)
def build_batch_shared_half_step_shortest_generator_word_examples() -> list[dict[str, Any]]:
    identity_state = (0, MAX_SOURCE_RANK)
    floor_only_state = (4, MAX_SOURCE_RANK)
    cap_only_state = (0, 11)
    interior_state = (3, 8)
    singleton_state = (5, 5)
    shortest_words = build_shortest_generator_words_by_feasible_interval_state()
    return [
        {
            'identity_interval_uses_the_empty_generator_word': {
                'interval_kernel_state': serialize_feasible_interval_kernel_state(identity_state),
                'canonical_shortest_generator_word': serialize_generator_word(
                    build_canonical_shortest_generator_word_for_feasible_interval_state(identity_state)
                ),
            }
        },
        {
            'one_sided_floor_interval_has_one_shortest_generator_word': {
                'interval_kernel_state': serialize_feasible_interval_kernel_state(floor_only_state),
                'canonical_shortest_generator_word': serialize_generator_word(
                    build_canonical_shortest_generator_word_for_feasible_interval_state(floor_only_state)
                ),
                'shortest_generator_word_count': len(shortest_words[floor_only_state]),
            }
        },
        {
            'one_sided_cap_interval_has_one_shortest_generator_word': {
                'interval_kernel_state': serialize_feasible_interval_kernel_state(cap_only_state),
                'canonical_shortest_generator_word': serialize_generator_word(
                    build_canonical_shortest_generator_word_for_feasible_interval_state(cap_only_state)
                ),
                'shortest_generator_word_count': len(shortest_words[cap_only_state]),
            }
        },
        {
            'interior_nonsingleton_interval_has_two_shortest_generator_words': {
                'interval_kernel_state': serialize_feasible_interval_kernel_state(interior_state),
                'canonical_shortest_generator_word': serialize_generator_word(
                    build_canonical_shortest_generator_word_for_feasible_interval_state(interior_state)
                ),
                'all_shortest_generator_words': [
                    serialize_generator_word(word) for word in shortest_words[interior_state]
                ],
            }
        },
        {
            'interior_singleton_interval_has_eighteen_shortest_generator_words_but_one_canonical_choice': {
                'interval_kernel_state': serialize_feasible_interval_kernel_state(singleton_state),
                'canonical_shortest_generator_word': serialize_generator_word(
                    build_canonical_shortest_generator_word_for_feasible_interval_state(singleton_state)
                ),
                'shortest_generator_word_count': len(shortest_words[singleton_state]),
                'sample_shortest_generator_words': [
                    serialize_generator_word(word) for word in shortest_words[singleton_state][:4]
                ],
            }
        },
    ]


@lru_cache(maxsize=1)
def build_batch_shared_half_step_shortest_generator_word_validation_summary() -> dict[str, Any]:
    shortest_words_by_state = build_shortest_generator_words_by_feasible_interval_state()
    shortest_length_spectrum = Counter(len(words[0]) for words in shortest_words_by_state.values())
    shortest_word_multiplicity_spectrum = Counter(len(words) for words in shortest_words_by_state.values())

    unique_shortest_word_states = sorted(state for state, words in shortest_words_by_state.items() if len(words) == 1)
    two_shortest_word_states = sorted(state for state, words in shortest_words_by_state.items() if len(words) == 2)
    eighteen_shortest_word_states = sorted(state for state, words in shortest_words_by_state.items() if len(words) == 18)

    canonical_matches_shortest_depth = True
    canonical_is_member_of_shortest_word_set = True
    represented_half_step_input_output_case_count = 0
    for state, shortest_words in shortest_words_by_state.items():
        canonical_word = build_canonical_shortest_generator_word_for_feasible_interval_state(state)
        if len(canonical_word) != len(shortest_words[0]):
            canonical_matches_shortest_depth = False
        if canonical_word not in shortest_words:
            canonical_is_member_of_shortest_word_set = False
        canonical_output = tuple(apply_generator_stream_directly(canonical_word))
        expected_output = build_half_step_kernel_from_feasible_interval_state(state)
        if canonical_output != expected_output:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordLawError(
                'every canonical shortest generator word must realize exactly the same half-step kernel as its feasible interval state'
            )
        represented_half_step_input_output_case_count += HALF_STEP_SELECTOR_INDEX_COUNT

    interior_singleton_states = [state for state in eighteen_shortest_word_states if 0 < state[0] == state[1] < MAX_SOURCE_RANK]
    if len(interior_singleton_states) != 15:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordLawError(
            'exactly the 15 interior singleton intervals should have eighteen shortest generator words'
        )

    shortest_word_multiplicity_by_category: dict[str, dict[int, int]] = defaultdict(dict)
    category_counter: dict[str, Counter[int]] = defaultdict(Counter)
    for state, words in shortest_words_by_state.items():
        if state == (0, MAX_SOURCE_RANK):
            category = 'identity'
        elif state[0] == 0 or state[1] == MAX_SOURCE_RANK:
            category = 'one_sided_nonidentity'
        elif state[0] == state[1]:
            category = 'interior_singleton'
        else:
            category = 'interior_nonsingleton'
        category_counter[category][len(words)] += 1
    shortest_word_multiplicity_by_category = {
        category: dict(sorted(counter.items())) for category, counter in sorted(category_counter.items())
    }

    return {
        'reachable_exact_feasible_interval_kernel_count': len(shortest_words_by_state),
        'canonical_shortest_generator_word_length_spectrum': dict(sorted(shortest_length_spectrum.items())),
        'shortest_generator_word_multiplicity_spectrum': dict(sorted(shortest_word_multiplicity_spectrum.items())),
        'unique_shortest_generator_word_count': len(unique_shortest_word_states),
        'two_shortest_generator_word_count': len(two_shortest_word_states),
        'eighteen_shortest_generator_word_count': len(eighteen_shortest_word_states),
        'represented_half_step_input_output_case_count': represented_half_step_input_output_case_count,
        'canonical_shortest_generator_word_matches_shortest_depth_for_every_state': canonical_matches_shortest_depth,
        'canonical_shortest_generator_word_is_always_one_of_the_shortest_words': canonical_is_member_of_shortest_word_set,
        'all_exact_interval_states_admit_a_shortest_generator_word_of_length_at_most_two': max(shortest_length_spectrum) == 2,
        'identity_interval_uses_only_the_empty_word': shortest_words_by_state[(0, MAX_SOURCE_RANK)] == ((),),
        'interior_singleton_intervals_have_uniform_shortest_word_multiplicity': all(
            len(shortest_words_by_state[state]) == 18 for state in interior_singleton_states
        ),
        'interior_singleton_shortest_word_multiplicity': 18,
        'shortest_word_multiplicity_by_category': shortest_word_multiplicity_by_category,
        'canonical_codec_examples_cover_depths_zero_one_and_two': True,
    }


@lru_cache(maxsize=1)
def build_headline_findings() -> dict[str, Any]:
    validation = build_batch_shared_half_step_shortest_generator_word_validation_summary()
    return {
        'every_exact_normalized_half_step_interval_state_has_a_canonical_shortest_generator_word': True,
        'reachable_exact_feasible_interval_kernel_count': validation['reachable_exact_feasible_interval_kernel_count'],
        'canonical_shortest_generator_word_length_spectrum': validation['canonical_shortest_generator_word_length_spectrum'],
        'shortest_generator_word_multiplicity_spectrum': validation['shortest_generator_word_multiplicity_spectrum'],
        'represented_half_step_input_output_case_count': validation['represented_half_step_input_output_case_count'],
        'validation_summary': validation,
    }


@lru_cache(maxsize=1)
def build_decision_rules() -> list[str]:
    return [
        'When a future inheritor wants a script-like representation of an exact normalized downstream state, encode feasible interval [a,b] by its canonical shortest generator word instead of persisting longer one-sided generator histories.',
        'Use the empty word only for the identity interval [0,16]. Use one generator for one-sided intervals [a,16] or [0,b]. Use the canonical two-generator word [[a,16],[0,b]] for every interior interval with 0 < a <= b < 16.',
        'Treat that canonical encoding as shortest by construction on the current path: every realized exact feasible interval state admits some shortest word of length 0, 1, or 2, and no state requires length 3 or more.',
        'Do not infer uniqueness from shortness. Interior nonsingleton intervals have exactly two shortest words, while every interior singleton interval [c,c] has exactly eighteen shortest words even though the canonical codec still chooses one deterministic representative.',
        'Because the canonical shortest word reproduces the same half-step witness kernel as the interval state on all 33 selector classes, the codec is safe for storage, replay, and inheritor-facing explanation.',
    ]


@lru_cache(maxsize=1)
def build_source_reports() -> list[str]:
    return [
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_feasible_interval_law_snapshot_20260309.md',
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_boundary_generator_law_snapshot_20260309.md',
        'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_law.py',
    ]


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_shared_half_step_shortest_generator_word_snapshot() -> dict[str, Any]:
    return {
        'focus': 'Every exact normalized half-step feasible interval state has a canonical shortest generator-word codec of length 0, 1, or 2.',
        'headline_findings': build_headline_findings(),
        'decision_rules': build_decision_rules(),
        'shortest_generator_word_examples': build_batch_shared_half_step_shortest_generator_word_examples(),
        'source_reports': build_source_reports(),
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_law.py',
    }


def main() -> None:
    print(json.dumps(build_service_mode_suffix_batch_shared_half_step_shortest_generator_word_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
