#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_dense_index_law import (
    FEASIBLE_INTERVAL_STATE_DENSE_INDEX_BIT_WIDTH,
    build_all_realized_feasible_interval_states,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_feasible_interval_law import (
    FeasibleIntervalKernelState,
    MAX_SOURCE_RANK,
    serialize_feasible_interval_kernel_state,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_index_law import (
    build_shortest_generator_word_choice_count_for_feasible_interval_state,
    decode_shortest_generator_word_from_choice_index,
    encode_shortest_generator_word_as_choice_index,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_family_law import (
    classify_feasible_interval_state,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_law import (
    GeneratorWord,
    decode_shortest_generator_word_to_feasible_interval_state,
    serialize_generator_word,
)


class WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordDenseIndexLawError(RuntimeError):
    pass


IDENTITY_BLOCK_START = 0
ONE_SIDED_BLOCK_START = 1
ONE_SIDED_BLOCK_COUNT = 2 * MAX_SOURCE_RANK
INTERIOR_NONSINGLETON_BLOCK_START = ONE_SIDED_BLOCK_START + ONE_SIDED_BLOCK_COUNT
INTERIOR_NON_SINGLETON_STATE_COUNT = ((MAX_SOURCE_RANK - 1) * (MAX_SOURCE_RANK - 2)) // 2
INTERIOR_NONSINGLETON_BLOCK_COUNT = 2 * INTERIOR_NON_SINGLETON_STATE_COUNT
INTERIOR_SINGLETON_BLOCK_START = INTERIOR_NONSINGLETON_BLOCK_START + INTERIOR_NONSINGLETON_BLOCK_COUNT
INTERIOR_SINGLETON_STATE_COUNT = MAX_SOURCE_RANK - 1
INTERIOR_SINGLETON_BLOCK_COUNT = INTERIOR_SINGLETON_STATE_COUNT * (MAX_SOURCE_RANK + 2)
EXACT_SHORTEST_GENERATOR_WORD_COUNT = (
    1 + ONE_SIDED_BLOCK_COUNT + INTERIOR_NONSINGLETON_BLOCK_COUNT + INTERIOR_SINGLETON_BLOCK_COUNT
)
MAX_EXACT_SHORTEST_GENERATOR_WORD_DENSE_INDEX = EXACT_SHORTEST_GENERATOR_WORD_COUNT - 1
EXACT_SHORTEST_GENERATOR_WORD_DENSE_INDEX_BIT_WIDTH = MAX_EXACT_SHORTEST_GENERATOR_WORD_DENSE_INDEX.bit_length()
FIXED_WIDTH_DENSE_STATE_AND_LOCAL_CHOICE_PAIR_BIT_WIDTH = FEASIBLE_INTERVAL_STATE_DENSE_INDEX_BIT_WIDTH + MAX_SOURCE_RANK.bit_length()


@lru_cache(maxsize=None)
def _normalize_feasible_interval_state(
    state: tuple[int, int] | list[int],
) -> FeasibleIntervalKernelState:
    if len(state) != 2:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordDenseIndexLawError(
            'feasible interval state must contain exactly two ranks'
        )
    lower_rank = int(state[0])
    upper_rank = int(state[1])
    if lower_rank < 0 or upper_rank < lower_rank or upper_rank > MAX_SOURCE_RANK:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordDenseIndexLawError(
            'feasible interval state must stay within the realized 17-rank path bounds'
        )
    return lower_rank, upper_rank


@lru_cache(maxsize=None)
def build_interior_nonsingleton_state_prefix(lower_rank: int) -> int:
    lower_rank = int(lower_rank)
    if lower_rank < 1 or lower_rank >= MAX_SOURCE_RANK - 1:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordDenseIndexLawError(
            'interior nonsingleton lower rank must lie in 1..14 on the current path'
        )
    return ((lower_rank - 1) * (2 * (MAX_SOURCE_RANK - 1) - lower_rank)) // 2


@lru_cache(maxsize=None)
def encode_shortest_generator_word_as_dense_index(
    generator_word: GeneratorWord,
) -> int:
    state = _normalize_feasible_interval_state(decode_shortest_generator_word_to_feasible_interval_state(generator_word))
    choice_index = encode_shortest_generator_word_as_choice_index(state, generator_word)
    lower_rank, upper_rank = state
    category = classify_feasible_interval_state(state)

    if category == 'identity':
        return IDENTITY_BLOCK_START
    if category == 'one_sided_nonidentity':
        if lower_rank == 0:
            return ONE_SIDED_BLOCK_START + upper_rank
        return ONE_SIDED_BLOCK_START + MAX_SOURCE_RANK + lower_rank - 1
    if category == 'interior_nonsingleton':
        state_offset = build_interior_nonsingleton_state_prefix(lower_rank) + (upper_rank - lower_rank - 1)
        return INTERIOR_NONSINGLETON_BLOCK_START + 2 * state_offset + choice_index
    return INTERIOR_SINGLETON_BLOCK_START + (lower_rank - 1) * (MAX_SOURCE_RANK + 2) + choice_index


@lru_cache(maxsize=None)
def decode_shortest_generator_word_from_dense_index(
    dense_index: int,
) -> GeneratorWord:
    dense_index = int(dense_index)
    if dense_index < 0 or dense_index > MAX_EXACT_SHORTEST_GENERATOR_WORD_DENSE_INDEX:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordDenseIndexLawError(
            'dense shortest-word index must stay within 0..512 on the current path'
        )

    if dense_index == IDENTITY_BLOCK_START:
        return decode_shortest_generator_word_from_choice_index((0, MAX_SOURCE_RANK), 0)

    if dense_index < INTERIOR_NONSINGLETON_BLOCK_START:
        one_sided_offset = dense_index - ONE_SIDED_BLOCK_START
        if one_sided_offset < MAX_SOURCE_RANK:
            state = (0, one_sided_offset)
        else:
            state = (one_sided_offset - MAX_SOURCE_RANK + 1, MAX_SOURCE_RANK)
        return decode_shortest_generator_word_from_choice_index(state, 0)

    if dense_index < INTERIOR_SINGLETON_BLOCK_START:
        nonsingleton_offset = dense_index - INTERIOR_NONSINGLETON_BLOCK_START
        state_offset, choice_index = divmod(nonsingleton_offset, 2)
        remaining = state_offset
        for lower_rank in range(1, MAX_SOURCE_RANK - 1):
            span = (MAX_SOURCE_RANK - 1) - lower_rank
            if remaining < span:
                state = (lower_rank, lower_rank + 1 + remaining)
                return decode_shortest_generator_word_from_choice_index(state, choice_index)
            remaining -= span
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordDenseIndexLawError(
            'interior nonsingleton dense index should always decode inside the realized catalog'
        )

    singleton_offset = dense_index - INTERIOR_SINGLETON_BLOCK_START
    lower_rank = singleton_offset // (MAX_SOURCE_RANK + 2) + 1
    choice_index = singleton_offset % (MAX_SOURCE_RANK + 2)
    state = (lower_rank, lower_rank)
    return decode_shortest_generator_word_from_choice_index(state, choice_index)


@lru_cache(maxsize=None)
def decode_shortest_generator_word_dense_index_to_state_and_choice(
    dense_index: int,
) -> tuple[FeasibleIntervalKernelState, int]:
    word = decode_shortest_generator_word_from_dense_index(dense_index)
    state = _normalize_feasible_interval_state(decode_shortest_generator_word_to_feasible_interval_state(word))
    choice_index = encode_shortest_generator_word_as_choice_index(state, word)
    return state, choice_index


@lru_cache(maxsize=1)
def build_shortest_generator_word_dense_index_examples() -> list[dict[str, Any]]:
    example_words: tuple[GeneratorWord, ...] = (
        (),
        ((0, 11),),
        ((3, 16), (0, 8)),
        ((0, 8), (3, 16)),
        ((0, 0), (5, 16)),
        ((16, 16), (0, 5)),
    )
    examples: list[dict[str, Any]] = []
    for word in example_words:
        dense_index = encode_shortest_generator_word_as_dense_index(word)
        state, choice_index = decode_shortest_generator_word_dense_index_to_state_and_choice(dense_index)
        examples.append(
            {
                'shortest_generator_word_dense_index_example': {
                    'generator_word': serialize_generator_word(word),
                    'dense_index': dense_index,
                    'decoded_generator_word': serialize_generator_word(
                        decode_shortest_generator_word_from_dense_index(dense_index)
                    ),
                    'decoded_interval_kernel_state': serialize_feasible_interval_kernel_state(state),
                    'decoded_local_choice_index': choice_index,
                }
            }
        )
    return examples


@lru_cache(maxsize=1)
def build_shortest_generator_word_dense_index_validation_summary() -> dict[str, Any]:
    exact_word_roundtrip_count = 0
    exact_state_roundtrip_count = 0
    exact_choice_roundtrip_count = 0
    seen_dense_indices: set[int] = set()
    represented_exact_shortest_word_count = 0
    represented_exact_interval_state_count = 0
    canonical_dense_index_count = 0

    represented_states: set[FeasibleIntervalKernelState] = set()

    for state in build_all_realized_feasible_interval_states():
        represented_states.add(state)
        represented_exact_interval_state_count += 1
        choice_count = build_shortest_generator_word_choice_count_for_feasible_interval_state(state)
        for choice_index in range(choice_count):
            word = decode_shortest_generator_word_from_choice_index(state, choice_index)
            dense_index = encode_shortest_generator_word_as_dense_index(word)
            decoded_word = decode_shortest_generator_word_from_dense_index(dense_index)
            if decoded_word != word:
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordDenseIndexLawError(
                    f'dense shortest-word roundtrip mismatch for state {state} and choice {choice_index}'
                )
            exact_word_roundtrip_count += 1
            represented_exact_shortest_word_count += 1
            seen_dense_indices.add(dense_index)

            decoded_state, decoded_choice = decode_shortest_generator_word_dense_index_to_state_and_choice(dense_index)
            if decoded_state != state:
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordDenseIndexLawError(
                    f'dense shortest-word index must preserve the exact feasible interval state: {state}'
                )
            exact_state_roundtrip_count += 1
            if decoded_choice != choice_index:
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordDenseIndexLawError(
                    f'dense shortest-word index must preserve the exact local choice index: {state}'
                )
            exact_choice_roundtrip_count += 1
            if choice_index == 0:
                canonical_dense_index_count += 1

    dense_index_catalog_is_contiguous = seen_dense_indices == set(range(EXACT_SHORTEST_GENERATOR_WORD_COUNT))
    if not dense_index_catalog_is_contiguous:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordDenseIndexLawError(
            'dense shortest-word indices must fill the full 0..512 range without gaps'
        )

    fixed_width_bit_savings_vs_dense_state_and_local_choice_pair = (
        FIXED_WIDTH_DENSE_STATE_AND_LOCAL_CHOICE_PAIR_BIT_WIDTH
        - EXACT_SHORTEST_GENERATOR_WORD_DENSE_INDEX_BIT_WIDTH
    )
    return {
        'reachable_exact_feasible_interval_kernel_count': represented_exact_interval_state_count,
        'represented_exact_shortest_generator_word_count': represented_exact_shortest_word_count,
        'maximum_exact_shortest_generator_word_dense_index': MAX_EXACT_SHORTEST_GENERATOR_WORD_DENSE_INDEX,
        'dense_index_bit_width': EXACT_SHORTEST_GENERATOR_WORD_DENSE_INDEX_BIT_WIDTH,
        'fixed_width_dense_state_and_local_choice_pair_bit_width': FIXED_WIDTH_DENSE_STATE_AND_LOCAL_CHOICE_PAIR_BIT_WIDTH,
        'fixed_width_bit_savings_vs_dense_state_and_local_choice_pair': fixed_width_bit_savings_vs_dense_state_and_local_choice_pair,
        'fixed_width_bit_savings_share_vs_dense_state_and_local_choice_pair': (
            fixed_width_bit_savings_vs_dense_state_and_local_choice_pair
            / FIXED_WIDTH_DENSE_STATE_AND_LOCAL_CHOICE_PAIR_BIT_WIDTH
        ),
        'dense_index_catalog_is_contiguous': dense_index_catalog_is_contiguous,
        'exact_dense_index_word_roundtrip_count': exact_word_roundtrip_count,
        'exact_dense_index_state_roundtrip_count': exact_state_roundtrip_count,
        'exact_dense_index_choice_roundtrip_count': exact_choice_roundtrip_count,
        'canonical_choice_zero_dense_index_count': canonical_dense_index_count,
        'identity_dense_index_range': [IDENTITY_BLOCK_START, IDENTITY_BLOCK_START],
        'one_sided_dense_index_range': [ONE_SIDED_BLOCK_START, INTERIOR_NONSINGLETON_BLOCK_START - 1],
        'interior_nonsingleton_dense_index_range': [INTERIOR_NONSINGLETON_BLOCK_START, INTERIOR_SINGLETON_BLOCK_START - 1],
        'interior_singleton_dense_index_range': [INTERIOR_SINGLETON_BLOCK_START, MAX_EXACT_SHORTEST_GENERATOR_WORD_DENSE_INDEX],
        'dense_index_zero_word': serialize_generator_word(decode_shortest_generator_word_from_dense_index(0)),
        'dense_index_max_word': serialize_generator_word(
            decode_shortest_generator_word_from_dense_index(MAX_EXACT_SHORTEST_GENERATOR_WORD_DENSE_INDEX)
        ),
        'every_exact_shortest_generator_word_is_addressable_as_one_dense_scalar': True,
    }


@lru_cache(maxsize=1)
def build_headline_findings() -> dict[str, Any]:
    validation = build_shortest_generator_word_dense_index_validation_summary()
    return {
        'every_exact_shortest_half_step_generator_word_is_addressable_by_dense_global_index': True,
        'dense_index_bit_width': validation['dense_index_bit_width'],
        'maximum_exact_shortest_generator_word_dense_index': validation['maximum_exact_shortest_generator_word_dense_index'],
        'fixed_width_bit_savings_vs_dense_state_and_local_choice_pair': validation[
            'fixed_width_bit_savings_vs_dense_state_and_local_choice_pair'
        ],
        'validation_summary': validation,
    }


@lru_cache(maxsize=1)
def build_decision_rules() -> list[str]:
    return [
        'When the exact normalized shortest generator script itself must survive as one scalar, address it by the dense global index 0..512 instead of storing a dense interval-state field plus a separate local choice field.',
        'Use the block decomposition directly: 0 is the identity word, 1..32 are the 32 one-sided nonidentity words, 33..242 are the interior nonsingleton words, and 243..512 are the 270 interior singleton words.',
        'Encode one-sided words in closed form: [0,b] maps to 1+b for b in 0..15, while [a,16] maps to 16+a for a in 1..16.',
        'Encode interior nonsingleton words [a,b] by their lower-major interior-state offset with one parity bit for the two orderings; encode interior singleton words [c,c] by the closed-form block 243 + 18*(c-1) + local_choice_index.',
        'Keep using the earlier local choice index when the feasible interval state is already stored elsewhere. The new dense global index is for the different case where the exact shortest script itself must travel alone as one scalar.',
    ]


@lru_cache(maxsize=1)
def build_source_reports() -> list[str]:
    return [
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_index_law_snapshot_20260309.md',
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_dense_index_law_snapshot_20260309.md',
        'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_dense_index_law.py',
    ]


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_shared_half_step_shortest_generator_word_dense_index_snapshot() -> dict[str, Any]:
    return {
        'focus': 'Every exact normalized shortest half-step generator word is now addressable by one dense global scalar when the script itself must survive without a separate interval-state field.',
        'headline_findings': build_headline_findings(),
        'decision_rules': build_decision_rules(),
        'shortest_generator_word_dense_index_examples': build_shortest_generator_word_dense_index_examples(),
        'source_reports': build_source_reports(),
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_dense_index_law.py',
    }


def main() -> None:
    print(json.dumps(build_service_mode_suffix_batch_shared_half_step_shortest_generator_word_dense_index_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
