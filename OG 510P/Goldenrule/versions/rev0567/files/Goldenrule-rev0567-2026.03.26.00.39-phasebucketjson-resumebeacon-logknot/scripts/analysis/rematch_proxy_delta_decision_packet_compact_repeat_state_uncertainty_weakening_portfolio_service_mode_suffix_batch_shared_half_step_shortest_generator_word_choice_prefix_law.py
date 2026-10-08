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

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_dense_index_law import (
    build_all_realized_feasible_interval_states,
    encode_feasible_interval_state_as_dense_index,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_prefix_law import (
    encode_feasible_interval_state_dense_index_as_prefix_bits,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_index_law import (
    build_shortest_generator_word_choice_count_for_feasible_interval_state,
    build_shortest_generator_word_choice_index_bit_width_for_feasible_interval_state,
    decode_shortest_generator_word_from_choice_index,
    encode_shortest_generator_word_as_choice_index,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_dense_index_law import (
    EXACT_SHORTEST_GENERATOR_WORD_COUNT,
    decode_shortest_generator_word_dense_index_to_state_and_choice,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_law import (
    GeneratorWord,
    serialize_generator_word,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_feasible_interval_law import (
    FeasibleIntervalKernelState,
    serialize_feasible_interval_kernel_state,
)


class WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordChoicePrefixLawError(RuntimeError):
    pass


INTERIOR_SINGLETON_SHORT_BIT_LENGTH = 4
INTERIOR_SINGLETON_LONG_BIT_LENGTH = 5
INTERIOR_SINGLETON_SHORT_PREFIX_COUNT = 14
INTERIOR_SINGLETON_LONG_PREFIX_BASE = '1110'
FIXED_INTERIOR_SINGLETON_CHOICE_INDEX_BIT_WIDTH = 5


@lru_cache(maxsize=None)
def _normalize_feasible_interval_state(
    state: tuple[int, int] | list[int],
) -> FeasibleIntervalKernelState:
    if len(state) != 2:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordChoicePrefixLawError(
            'feasible interval state must contain exactly two ranks'
        )
    lower_rank = int(state[0])
    upper_rank = int(state[1])
    if lower_rank < 0 or upper_rank < lower_rank or upper_rank > 16:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordChoicePrefixLawError(
            'feasible interval state must stay within the realized 17-rank path bounds'
        )
    return lower_rank, upper_rank


@lru_cache(maxsize=None)
def encode_shortest_generator_word_choice_index_as_prefix_bits(
    state: tuple[int, int] | list[int],
    choice_index: int,
) -> str:
    state = _normalize_feasible_interval_state(state)
    choice_index = int(choice_index)
    choice_count = build_shortest_generator_word_choice_count_for_feasible_interval_state(state)
    if choice_index < 0 or choice_index >= choice_count:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordChoicePrefixLawError(
            f'choice index {choice_index} is outside the legal range 0..{choice_count - 1} for state {state}'
        )

    if choice_count == 1:
        return ''
    if choice_count == 2:
        return str(choice_index)
    if choice_count != 18:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordChoicePrefixLawError(
            f'unexpected shortest-word choice family size {choice_count} for state {state}'
        )
    if choice_index < INTERIOR_SINGLETON_SHORT_PREFIX_COUNT:
        return format(choice_index, f'0{INTERIOR_SINGLETON_SHORT_BIT_LENGTH}b')
    long_offset = choice_index - INTERIOR_SINGLETON_SHORT_PREFIX_COUNT
    return format(14 + (long_offset // 2), f'0{INTERIOR_SINGLETON_SHORT_BIT_LENGTH}b') + str(long_offset % 2)


@lru_cache(maxsize=None)
def encode_shortest_generator_word_as_choice_prefix_bits(
    state: tuple[int, int] | list[int],
    generator_word: GeneratorWord,
) -> str:
    state = _normalize_feasible_interval_state(state)
    return encode_shortest_generator_word_choice_index_as_prefix_bits(
        state,
        encode_shortest_generator_word_as_choice_index(state, generator_word),
    )


@lru_cache(maxsize=None)
def decode_shortest_generator_word_choice_index_from_prefix_bits(
    state: tuple[int, int] | list[int],
    bitstream: str,
    start_offset: int = 0,
) -> tuple[int, int]:
    state = _normalize_feasible_interval_state(state)
    start_offset = int(start_offset)
    if start_offset < 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordChoicePrefixLawError(
            'prefix decode offset must be nonnegative'
        )

    choice_count = build_shortest_generator_word_choice_count_for_feasible_interval_state(state)
    if choice_count == 1:
        return 0, 0
    if choice_count == 2:
        if start_offset + 1 > len(bitstream):
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordChoicePrefixLawError(
                'two-choice prefix decode requires one bit from the current offset'
            )
        return int(bitstream[start_offset]), 1
    if choice_count != 18:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordChoicePrefixLawError(
            f'unexpected shortest-word choice family size {choice_count} for state {state}'
        )
    if start_offset + INTERIOR_SINGLETON_SHORT_BIT_LENGTH > len(bitstream):
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordChoicePrefixLawError(
            'interior singleton choice prefix decode requires at least four bits from the current offset'
        )

    prefix = bitstream[start_offset : start_offset + INTERIOR_SINGLETON_SHORT_BIT_LENGTH]
    prefix_value = int(prefix, 2)
    if prefix_value < INTERIOR_SINGLETON_SHORT_PREFIX_COUNT:
        return prefix_value, INTERIOR_SINGLETON_SHORT_BIT_LENGTH

    if start_offset + INTERIOR_SINGLETON_LONG_BIT_LENGTH > len(bitstream):
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordChoicePrefixLawError(
            'long-form interior singleton choice decode requires one extra fifth bit'
        )
    suffix_bit = int(bitstream[start_offset + INTERIOR_SINGLETON_SHORT_BIT_LENGTH])
    return INTERIOR_SINGLETON_SHORT_PREFIX_COUNT + 2 * (prefix_value - INTERIOR_SINGLETON_SHORT_PREFIX_COUNT) + suffix_bit, INTERIOR_SINGLETON_LONG_BIT_LENGTH


@lru_cache(maxsize=None)
def decode_shortest_generator_word_from_choice_prefix_bits(
    state: tuple[int, int] | list[int],
    bitstream: str,
    start_offset: int = 0,
) -> tuple[GeneratorWord, int]:
    state = _normalize_feasible_interval_state(state)
    choice_index, bits_consumed = decode_shortest_generator_word_choice_index_from_prefix_bits(state, bitstream, start_offset)
    return decode_shortest_generator_word_from_choice_index(state, choice_index), bits_consumed


@lru_cache(maxsize=1)
def build_shortest_generator_word_choice_prefix_examples() -> list[dict[str, Any]]:
    one_sided = (0, 11)
    interior_nonsingleton = (3, 8)
    interior_singleton = (5, 5)
    return [
        {
            'unique_interval_state_needs_no_choice_bits': {
                'interval_kernel_state': serialize_feasible_interval_kernel_state(one_sided),
                'choice_count': build_shortest_generator_word_choice_count_for_feasible_interval_state(one_sided),
                'choice_index_bit_width_before_prefix': build_shortest_generator_word_choice_index_bit_width_for_feasible_interval_state(one_sided),
                'choice_index_to_prefix_bits': {'0': encode_shortest_generator_word_choice_index_as_prefix_bits(one_sided, 0)},
            }
        },
        {
            'interior_nonsingleton_interval_keeps_the_one_bit_swap_branch': {
                'interval_kernel_state': serialize_feasible_interval_kernel_state(interior_nonsingleton),
                'choice_count': build_shortest_generator_word_choice_count_for_feasible_interval_state(interior_nonsingleton),
                'choice_index_bit_width_before_prefix': build_shortest_generator_word_choice_index_bit_width_for_feasible_interval_state(interior_nonsingleton),
                'choice_index_to_prefix_bits': {
                    str(choice_index): encode_shortest_generator_word_choice_index_as_prefix_bits(interior_nonsingleton, choice_index)
                    for choice_index in range(2)
                },
            }
        },
        {
            'interior_singleton_interval_splits_into_fourteen_short_and_four_long_choice_codes': {
                'interval_kernel_state': serialize_feasible_interval_kernel_state(interior_singleton),
                'choice_count': build_shortest_generator_word_choice_count_for_feasible_interval_state(interior_singleton),
                'choice_index_bit_width_before_prefix': build_shortest_generator_word_choice_index_bit_width_for_feasible_interval_state(interior_singleton),
                'short_choice_index_examples': {
                    str(choice_index): encode_shortest_generator_word_choice_index_as_prefix_bits(interior_singleton, choice_index)
                    for choice_index in (0, 1, 12, 13)
                },
                'long_choice_index_examples': {
                    str(choice_index): encode_shortest_generator_word_choice_index_as_prefix_bits(interior_singleton, choice_index)
                    for choice_index in (14, 15, 16, 17)
                },
                'decoded_shortest_word_examples': {
                    str(choice_index): serialize_generator_word(
                        decode_shortest_generator_word_from_choice_prefix_bits(
                            interior_singleton,
                            encode_shortest_generator_word_choice_index_as_prefix_bits(interior_singleton, choice_index),
                        )[0]
                    )
                    for choice_index in (0, 13, 14, 17)
                },
            }
        },
    ]


@lru_cache(maxsize=1)
def build_shortest_generator_word_choice_prefix_validation_summary() -> dict[str, Any]:
    exact_choice_index_roundtrip_count = 0
    exact_word_roundtrip_count = 0
    exact_state_roundtrip_count = 0
    exact_prefix_sequential_stream_roundtrip_count = 0
    all_state_local_choice_prefix_families_are_prefix_free = True
    canonical_choice_index_is_zero_for_every_state = True

    total_prefix_bits_over_exact_word_catalog = 0
    total_fixed_width_choice_bits_over_exact_word_catalog = 0
    total_state_prefix_bits_over_exact_word_catalog = 0

    prefix_length_spectrum_over_exact_words: Counter[int] = Counter()
    prefix_length_spectrum_by_state_category: dict[str, Counter[int]] = defaultdict(Counter)
    total_prefix_bits_by_state_category: Counter[str] = Counter()
    state_local_family_total_bits_spectrum: Counter[int] = Counter()

    concatenated_stream_parts: list[str] = []
    sequential_state_schedule: list[FeasibleIntervalKernelState] = []

    for state in build_all_realized_feasible_interval_states():
        state_prefix_bits = encode_feasible_interval_state_dense_index_as_prefix_bits(
            encode_feasible_interval_state_as_dense_index(state)
        )
        choice_count = build_shortest_generator_word_choice_count_for_feasible_interval_state(state)
        fixed_width_choice_bits = build_shortest_generator_word_choice_index_bit_width_for_feasible_interval_state(state)

        family_prefix_catalog = {
            choice_index: encode_shortest_generator_word_choice_index_as_prefix_bits(state, choice_index)
            for choice_index in range(choice_count)
        }

        choice_indices = tuple(family_prefix_catalog)
        for left_choice_index in choice_indices:
            left_bits = family_prefix_catalog[left_choice_index]
            for right_choice_index in choice_indices:
                if left_choice_index == right_choice_index:
                    continue
                if family_prefix_catalog[right_choice_index].startswith(left_bits):
                    all_state_local_choice_prefix_families_are_prefix_free = False
                    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordChoicePrefixLawError(
                        f'state-local prefix collision for state {state}: choice {left_choice_index} prefixes {right_choice_index}'
                    )

        family_total_bits = 0
        if encode_shortest_generator_word_as_choice_index(
            state,
            decode_shortest_generator_word_from_choice_index(state, 0),
        ) != 0:
            canonical_choice_index_is_zero_for_every_state = False
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordChoicePrefixLawError(
                f'canonical shortest word must remain at local choice index 0 for state {state}'
            )

        if choice_count == 1:
            category = 'unique_state'
        elif choice_count == 2:
            category = 'interior_nonsingleton'
        elif choice_count == 18:
            category = 'interior_singleton'
        else:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordChoicePrefixLawError(
                f'unexpected shortest-word choice family size {choice_count} for state {state}'
            )

        for choice_index in range(choice_count):
            prefix_bits = family_prefix_catalog[choice_index]
            decoded_choice_index, consumed_bits = decode_shortest_generator_word_choice_index_from_prefix_bits(state, prefix_bits)
            if decoded_choice_index != choice_index:
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordChoicePrefixLawError(
                    f'choice-prefix roundtrip mismatch for state {state} at choice index {choice_index}'
                )
            if consumed_bits != len(prefix_bits):
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordChoicePrefixLawError(
                    f'choice-prefix decode must consume the full local code for state {state} at choice index {choice_index}'
                )
            exact_choice_index_roundtrip_count += 1

            generator_word = decode_shortest_generator_word_from_choice_index(state, choice_index)
            decoded_word, word_consumed_bits = decode_shortest_generator_word_from_choice_prefix_bits(state, prefix_bits)
            if decoded_word != generator_word:
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordChoicePrefixLawError(
                    f'word prefix roundtrip mismatch for state {state} at choice index {choice_index}'
                )
            if word_consumed_bits != consumed_bits:
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordChoicePrefixLawError(
                    f'word and choice decoders must consume the same bits for state {state} at choice index {choice_index}'
                )
            exact_word_roundtrip_count += 1
            exact_state_roundtrip_count += 1

            total_prefix_bits_over_exact_word_catalog += len(prefix_bits)
            total_fixed_width_choice_bits_over_exact_word_catalog += fixed_width_choice_bits
            total_state_prefix_bits_over_exact_word_catalog += len(state_prefix_bits)
            prefix_length_spectrum_over_exact_words[len(prefix_bits)] += 1
            prefix_length_spectrum_by_state_category[category][len(prefix_bits)] += 1
            total_prefix_bits_by_state_category[category] += len(prefix_bits)
            family_total_bits += len(prefix_bits)

            concatenated_stream_parts.append(prefix_bits)
            sequential_state_schedule.append(state)

        state_local_family_total_bits_spectrum[family_total_bits] += 1

    concatenated_stream = ''.join(concatenated_stream_parts)
    cursor = 0
    for state in sequential_state_schedule:
        choice_index, consumed_bits = decode_shortest_generator_word_choice_index_from_prefix_bits(state, concatenated_stream, cursor)
        generator_word = decode_shortest_generator_word_from_choice_index(state, choice_index)
        decoded_word, word_consumed_bits = decode_shortest_generator_word_from_choice_prefix_bits(state, concatenated_stream, cursor)
        if decoded_word != generator_word or word_consumed_bits != consumed_bits:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordChoicePrefixLawError(
                f'sequential stream decode mismatch for state {state} at bit cursor {cursor}'
            )
        cursor += consumed_bits
        exact_prefix_sequential_stream_roundtrip_count += 1
    if cursor != len(concatenated_stream):
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordChoicePrefixLawError(
            'sequential choice-prefix decode must consume the full concatenated stream exactly'
        )

    saved_bits_vs_fixed_width_choice_indices = (
        total_fixed_width_choice_bits_over_exact_word_catalog - total_prefix_bits_over_exact_word_catalog
    )
    mean_prefix_bit_length_over_exact_word_catalog = total_prefix_bits_over_exact_word_catalog / EXACT_SHORTEST_GENERATOR_WORD_COUNT
    mean_fixed_width_choice_bit_length_over_exact_word_catalog = (
        total_fixed_width_choice_bits_over_exact_word_catalog / EXACT_SHORTEST_GENERATOR_WORD_COUNT
    )
    mean_bit_savings_vs_fixed_width_choice_indices = (
        saved_bits_vs_fixed_width_choice_indices / EXACT_SHORTEST_GENERATOR_WORD_COUNT
    )
    combined_state_prefix_plus_choice_prefix_total_bits = (
        total_state_prefix_bits_over_exact_word_catalog + total_prefix_bits_over_exact_word_catalog
    )

    return {
        'reachable_exact_feasible_interval_kernel_count': len(build_all_realized_feasible_interval_states()),
        'represented_exact_shortest_word_count': EXACT_SHORTEST_GENERATOR_WORD_COUNT,
        'exact_choice_index_roundtrip_count': exact_choice_index_roundtrip_count,
        'exact_word_roundtrip_count': exact_word_roundtrip_count,
        'exact_state_roundtrip_count': exact_state_roundtrip_count,
        'exact_choice_prefix_sequential_stream_roundtrip_count': exact_prefix_sequential_stream_roundtrip_count,
        'all_state_local_choice_prefix_families_are_prefix_free': all_state_local_choice_prefix_families_are_prefix_free,
        'canonical_choice_index_is_zero_for_every_state': canonical_choice_index_is_zero_for_every_state,
        'interior_singleton_short_prefix_count': INTERIOR_SINGLETON_SHORT_PREFIX_COUNT,
        'interior_singleton_long_prefix_count': 18 - INTERIOR_SINGLETON_SHORT_PREFIX_COUNT,
        'interior_singleton_short_prefix_bit_length': INTERIOR_SINGLETON_SHORT_BIT_LENGTH,
        'interior_singleton_long_prefix_bit_length': INTERIOR_SINGLETON_LONG_BIT_LENGTH,
        'choice_prefix_bit_length_spectrum_over_exact_words': dict(sorted(prefix_length_spectrum_over_exact_words.items())),
        'choice_prefix_bit_length_spectrum_by_state_category': {
            category: dict(sorted(counter.items())) for category, counter in sorted(prefix_length_spectrum_by_state_category.items())
        },
        'state_local_choice_family_total_prefix_bits_spectrum': dict(sorted(state_local_family_total_bits_spectrum.items())),
        'total_choice_prefix_bits_over_exact_word_catalog': total_prefix_bits_over_exact_word_catalog,
        'total_fixed_width_choice_index_bits_over_exact_word_catalog': total_fixed_width_choice_bits_over_exact_word_catalog,
        'saved_bits_vs_fixed_width_choice_indices_over_exact_word_catalog': saved_bits_vs_fixed_width_choice_indices,
        'mean_choice_prefix_bit_length_over_exact_word_catalog': mean_prefix_bit_length_over_exact_word_catalog,
        'mean_fixed_width_choice_index_bit_length_over_exact_word_catalog': mean_fixed_width_choice_bit_length_over_exact_word_catalog,
        'mean_bit_savings_vs_fixed_width_choice_indices_over_exact_word_catalog': mean_bit_savings_vs_fixed_width_choice_indices,
        'total_choice_prefix_bits_by_state_category': dict(sorted(total_prefix_bits_by_state_category.items())),
        'weighted_state_prefix_bits_over_exact_word_catalog': total_state_prefix_bits_over_exact_word_catalog,
        'combined_state_prefix_plus_choice_prefix_total_bits_over_exact_word_catalog': combined_state_prefix_plus_choice_prefix_total_bits,
        'combined_state_prefix_plus_choice_prefix_mean_bits_over_exact_word_catalog': combined_state_prefix_plus_choice_prefix_total_bits / EXACT_SHORTEST_GENERATOR_WORD_COUNT,
        'state_known_local_choice_prefix_is_strictly_smaller_than_global_exact_word_prefix': total_prefix_bits_over_exact_word_catalog < 4619,
        'state_prefix_plus_choice_prefix_is_strictly_larger_than_global_exact_word_prefix': combined_state_prefix_plus_choice_prefix_total_bits > 4619,
        'represented_exact_shortest_word_catalog_is_streamable_without_search_once_interval_state_is_known': True,
    }


@lru_cache(maxsize=1)
def build_headline_findings() -> dict[str, Any]:
    validation = build_shortest_generator_word_choice_prefix_validation_summary()
    return {
        'state_conditional_local_choice_prefixes_address_every_exact_shortest_word_without_search': True,
        'choice_prefix_bit_length_spectrum_over_exact_words': validation['choice_prefix_bit_length_spectrum_over_exact_words'],
        'mean_choice_prefix_bit_length_over_exact_word_catalog': validation['mean_choice_prefix_bit_length_over_exact_word_catalog'],
        'saved_bits_vs_fixed_width_choice_indices_over_exact_word_catalog': validation['saved_bits_vs_fixed_width_choice_indices_over_exact_word_catalog'],
        'validation_summary': validation,
    }


@lru_cache(maxsize=1)
def build_decision_rules() -> list[str]:
    return [
        'When the exact normalized feasible interval state is already known, stream any noncanonical shortest generator script by a state-conditional local choice prefix instead of writing a fixed-width local choice field.',
        'Keep the zero-choice branch for the 33 unique states. They now consume no local bits at all once the interval state is present.',
        'Keep the single swap bit for the 105 interior nonsingleton states. Their two shortest scripts still need exactly one local bit.',
        'For each of the 15 interior singleton states, replace the old fixed 5-bit local choice field by the canonical local prefix family: choices 0..13 use raw 4-bit binaries and choices 14..17 use the four 5-bit leaves 11100, 11101, 11110, 11111.',
        'Do not use this local choice prefix when the interval state itself is absent. In that standalone-script regime, the earlier 9.0039-bit global shortest-word prefix remains smaller than sending a state prefix plus this conditional local choice prefix.',
    ]


@lru_cache(maxsize=1)
def build_source_reports() -> list[str]:
    return [
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_index_law_snapshot_20260309.md',
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_prefix_law_snapshot_20260309.md',
        'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_prefix_law.py',
    ]


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_prefix_snapshot() -> dict[str, Any]:
    return {
        'focus': 'Once the normalized feasible interval state is already known, every exact shortest downstream generator word is now streamable by a smaller state-conditional local choice prefix.',
        'headline_findings': build_headline_findings(),
        'decision_rules': build_decision_rules(),
        'shortest_generator_word_choice_prefix_examples': build_shortest_generator_word_choice_prefix_examples(),
        'source_reports': build_source_reports(),
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_prefix_law.py',
    }


def main() -> None:
    json.dump(
        build_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_prefix_snapshot(),
        sys.stdout,
        indent=2,
        sort_keys=True,
    )
    sys.stdout.write('\n')


if __name__ == '__main__':
    main()
