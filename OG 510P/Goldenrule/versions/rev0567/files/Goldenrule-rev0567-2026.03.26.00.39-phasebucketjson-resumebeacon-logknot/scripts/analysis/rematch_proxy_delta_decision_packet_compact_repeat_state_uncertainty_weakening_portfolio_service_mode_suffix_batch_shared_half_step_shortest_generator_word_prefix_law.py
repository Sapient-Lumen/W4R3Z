#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_dense_index_law import (
    EXACT_SHORTEST_GENERATOR_WORD_COUNT,
    MAX_EXACT_SHORTEST_GENERATOR_WORD_DENSE_INDEX,
    decode_shortest_generator_word_from_dense_index,
    decode_shortest_generator_word_dense_index_to_state_and_choice,
    encode_shortest_generator_word_as_dense_index,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_law import (
    GeneratorWord,
    serialize_generator_word,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_feasible_interval_law import (
    serialize_feasible_interval_kernel_state,
)


class WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordPrefixLawError(RuntimeError):
    pass


PREFIX_SHORT_BIT_LENGTH = 9
PREFIX_LONG_BIT_LENGTH = 10
PREFIX_SHORT_CATALOG_COUNT = 2**PREFIX_SHORT_BIT_LENGTH - 1
PREFIX_LONG_SUFFIX_BASE = '1' * PREFIX_SHORT_BIT_LENGTH
PREFIX_LONG_CATALOG_COUNT = EXACT_SHORTEST_GENERATOR_WORD_COUNT - PREFIX_SHORT_CATALOG_COUNT
PREFIX_SHORT_MAX_DENSE_INDEX = PREFIX_SHORT_CATALOG_COUNT - 1
PREFIX_LONG_DENSE_INDEX_RANGE = [PREFIX_SHORT_CATALOG_COUNT, MAX_EXACT_SHORTEST_GENERATOR_WORD_DENSE_INDEX]
FIXED_WIDTH_DENSE_INDEX_BIT_LENGTH = MAX_EXACT_SHORTEST_GENERATOR_WORD_DENSE_INDEX.bit_length()


@lru_cache(maxsize=None)
def encode_shortest_generator_word_dense_index_as_prefix_bits(dense_index: int) -> str:
    dense_index = int(dense_index)
    if dense_index < 0 or dense_index > MAX_EXACT_SHORTEST_GENERATOR_WORD_DENSE_INDEX:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordPrefixLawError(
            'dense shortest-word index must stay within 0..512 on the current path'
        )
    if dense_index <= PREFIX_SHORT_MAX_DENSE_INDEX:
        return format(dense_index, f'0{PREFIX_SHORT_BIT_LENGTH}b')
    return PREFIX_LONG_SUFFIX_BASE + format(dense_index - PREFIX_SHORT_CATALOG_COUNT, '01b')


@lru_cache(maxsize=None)
def encode_shortest_generator_word_as_prefix_bits(generator_word: GeneratorWord) -> str:
    return encode_shortest_generator_word_dense_index_as_prefix_bits(
        encode_shortest_generator_word_as_dense_index(generator_word)
    )


@lru_cache(maxsize=None)
def decode_shortest_generator_word_dense_index_from_prefix_bits(
    bitstream: str,
    start_offset: int = 0,
) -> tuple[int, int]:
    start_offset = int(start_offset)
    if start_offset < 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordPrefixLawError(
            'prefix decode offset must be nonnegative'
        )
    if start_offset + PREFIX_SHORT_BIT_LENGTH > len(bitstream):
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordPrefixLawError(
            'prefix decode requires at least 9 bits from the current offset'
        )

    prefix = bitstream[start_offset : start_offset + PREFIX_SHORT_BIT_LENGTH]
    prefix_value = int(prefix, 2)
    if prefix_value < PREFIX_SHORT_CATALOG_COUNT:
        return prefix_value, PREFIX_SHORT_BIT_LENGTH

    if start_offset + PREFIX_LONG_BIT_LENGTH > len(bitstream):
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordPrefixLawError(
            'long-form prefix decode requires one extra tenth bit'
        )

    dense_index = PREFIX_SHORT_CATALOG_COUNT + int(bitstream[start_offset + PREFIX_SHORT_BIT_LENGTH], 2)
    return dense_index, PREFIX_LONG_BIT_LENGTH


@lru_cache(maxsize=None)
def decode_shortest_generator_word_from_prefix_bits(
    bitstream: str,
    start_offset: int = 0,
) -> tuple[GeneratorWord, int]:
    dense_index, bits_consumed = decode_shortest_generator_word_dense_index_from_prefix_bits(bitstream, start_offset)
    return decode_shortest_generator_word_from_dense_index(dense_index), bits_consumed


@lru_cache(maxsize=1)
def build_shortest_generator_word_prefix_examples() -> list[dict[str, Any]]:
    example_dense_indices = (0, 32, 242, 510, 511, 512)
    examples: list[dict[str, Any]] = []
    for dense_index in example_dense_indices:
        word = decode_shortest_generator_word_from_dense_index(dense_index)
        state, choice_index = decode_shortest_generator_word_dense_index_to_state_and_choice(dense_index)
        prefix_bits = encode_shortest_generator_word_dense_index_as_prefix_bits(dense_index)
        examples.append(
            {
                'shortest_generator_word_prefix_example': {
                    'dense_index': dense_index,
                    'prefix_bits': prefix_bits,
                    'prefix_bit_length': len(prefix_bits),
                    'decoded_interval_kernel_state': serialize_feasible_interval_kernel_state(state),
                    'decoded_local_choice_index': choice_index,
                    'decoded_generator_word': serialize_generator_word(word),
                }
            }
        )
    return examples


@lru_cache(maxsize=1)
def build_shortest_generator_word_prefix_validation_summary() -> dict[str, Any]:
    prefix_catalog: dict[int, str] = {}
    exact_dense_index_roundtrip_count = 0
    exact_word_roundtrip_count = 0
    exact_state_roundtrip_count = 0
    exact_choice_roundtrip_count = 0
    short_prefix_code_count = 0
    long_prefix_code_count = 0
    total_prefix_bits = 0
    exact_sequential_stream_roundtrip_count = 0

    concatenated_stream_parts: list[str] = []

    for dense_index in range(EXACT_SHORTEST_GENERATOR_WORD_COUNT):
        word = decode_shortest_generator_word_from_dense_index(dense_index)
        state, choice_index = decode_shortest_generator_word_dense_index_to_state_and_choice(dense_index)
        prefix_bits = encode_shortest_generator_word_dense_index_as_prefix_bits(dense_index)
        decoded_dense_index, consumed_bits = decode_shortest_generator_word_dense_index_from_prefix_bits(prefix_bits)
        if decoded_dense_index != dense_index:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordPrefixLawError(
                f'prefix dense-index roundtrip mismatch at dense index {dense_index}'
            )
        exact_dense_index_roundtrip_count += 1

        decoded_word, word_consumed_bits = decode_shortest_generator_word_from_prefix_bits(prefix_bits)
        if decoded_word != word:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordPrefixLawError(
                f'prefix word roundtrip mismatch at dense index {dense_index}'
            )
        exact_word_roundtrip_count += 1
        if consumed_bits != word_consumed_bits:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordPrefixLawError(
                f'prefix dense-index and word decoders must consume the same bit count at dense index {dense_index}'
            )

        decoded_state, decoded_choice = decode_shortest_generator_word_dense_index_to_state_and_choice(decoded_dense_index)
        if decoded_state != state:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordPrefixLawError(
                f'prefix dense-index decode must preserve feasible interval state at dense index {dense_index}'
            )
        if decoded_choice != choice_index:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordPrefixLawError(
                f'prefix dense-index decode must preserve local choice at dense index {dense_index}'
            )
        exact_state_roundtrip_count += 1
        exact_choice_roundtrip_count += 1

        prefix_catalog[dense_index] = prefix_bits
        concatenated_stream_parts.append(prefix_bits)
        total_prefix_bits += len(prefix_bits)
        if len(prefix_bits) == PREFIX_SHORT_BIT_LENGTH:
            short_prefix_code_count += 1
        elif len(prefix_bits) == PREFIX_LONG_BIT_LENGTH:
            long_prefix_code_count += 1
        else:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordPrefixLawError(
                f'unexpected prefix bit length {len(prefix_bits)} at dense index {dense_index}'
            )

    prefix_free_catalog = True
    dense_indices = tuple(prefix_catalog)
    for left_dense_index in dense_indices:
        left_bits = prefix_catalog[left_dense_index]
        for right_dense_index in dense_indices:
            if left_dense_index == right_dense_index:
                continue
            if prefix_catalog[right_dense_index].startswith(left_bits):
                prefix_free_catalog = False
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordPrefixLawError(
                    f'prefix collision: dense index {left_dense_index} prefixes dense index {right_dense_index}'
                )

    concatenated_stream = ''.join(concatenated_stream_parts)
    cursor = 0
    for dense_index in range(EXACT_SHORTEST_GENERATOR_WORD_COUNT):
        decoded_dense_index, consumed_bits = decode_shortest_generator_word_dense_index_from_prefix_bits(concatenated_stream, cursor)
        if decoded_dense_index != dense_index:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordPrefixLawError(
                f'sequential stream decode mismatch at dense index {dense_index}'
            )
        cursor += consumed_bits
        exact_sequential_stream_roundtrip_count += 1
    if cursor != len(concatenated_stream):
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordPrefixLawError(
            'sequential prefix stream decode must consume the full concatenated stream exactly'
        )

    fixed_width_total_bits = EXACT_SHORTEST_GENERATOR_WORD_COUNT * FIXED_WIDTH_DENSE_INDEX_BIT_LENGTH
    saved_bits_vs_fixed_width_dense_index = fixed_width_total_bits - total_prefix_bits
    mean_prefix_bit_length = total_prefix_bits / EXACT_SHORTEST_GENERATOR_WORD_COUNT
    mean_bit_savings_vs_fixed_width_dense_index = saved_bits_vs_fixed_width_dense_index / EXACT_SHORTEST_GENERATOR_WORD_COUNT

    return {
        'represented_exact_shortest_generator_word_count': EXACT_SHORTEST_GENERATOR_WORD_COUNT,
        'short_prefix_bit_length': PREFIX_SHORT_BIT_LENGTH,
        'long_prefix_bit_length': PREFIX_LONG_BIT_LENGTH,
        'short_prefix_code_count': short_prefix_code_count,
        'long_prefix_code_count': long_prefix_code_count,
        'long_prefix_dense_index_range': PREFIX_LONG_DENSE_INDEX_RANGE,
        'exact_prefix_dense_index_roundtrip_count': exact_dense_index_roundtrip_count,
        'exact_prefix_word_roundtrip_count': exact_word_roundtrip_count,
        'exact_prefix_state_roundtrip_count': exact_state_roundtrip_count,
        'exact_prefix_choice_roundtrip_count': exact_choice_roundtrip_count,
        'exact_prefix_sequential_stream_roundtrip_count': exact_sequential_stream_roundtrip_count,
        'prefix_catalog_is_prefix_free': prefix_free_catalog,
        'total_prefix_bits_over_exact_catalog': total_prefix_bits,
        'fixed_width_dense_index_total_bits_over_exact_catalog': fixed_width_total_bits,
        'saved_bits_vs_fixed_width_dense_index': saved_bits_vs_fixed_width_dense_index,
        'saved_bits_share_vs_fixed_width_dense_index': saved_bits_vs_fixed_width_dense_index / fixed_width_total_bits,
        'mean_prefix_bit_length': mean_prefix_bit_length,
        'mean_bit_savings_vs_fixed_width_dense_index': mean_bit_savings_vs_fixed_width_dense_index,
        'exact_uniform_entropy_lower_bound_bits': math.log2(EXACT_SHORTEST_GENERATOR_WORD_COUNT),
        'canonical_long_prefix_words': [
            serialize_generator_word(decode_shortest_generator_word_from_dense_index(dense_index))
            for dense_index in PREFIX_LONG_DENSE_INDEX_RANGE
        ],
        'every_exact_shortest_generator_word_is_streamable_as_a_prefix_code_over_the_existing_dense_index': True,
    }


@lru_cache(maxsize=1)
def build_headline_findings() -> dict[str, Any]:
    validation = build_shortest_generator_word_prefix_validation_summary()
    return {
        'existing_dense_exact_shortest_word_index_now_has_a_prefix_code_with_only_two_ten_bit_exceptions': True,
        'mean_prefix_bit_length': validation['mean_prefix_bit_length'],
        'mean_bit_savings_vs_fixed_width_dense_index': validation['mean_bit_savings_vs_fixed_width_dense_index'],
        'saved_bits_vs_fixed_width_dense_index': validation['saved_bits_vs_fixed_width_dense_index'],
        'validation_summary': validation,
    }


@lru_cache(maxsize=1)
def build_decision_rules() -> list[str]:
    return [
        'When an exact normalized shortest generator word must travel alone as a self-delimiting bitstream, keep the existing dense global shortest-word index but wrap it in the new canonical prefix code instead of writing all 10 dense bits unconditionally.',
        'Encode dense indices 0..510 as their raw 9-bit binary forms; only dense indices 511 and 512 consume a tenth bit, as 1111111110 and 1111111111.',
        'Decode by reading 9 bits first: if the 9-bit value is below 511, stop there; if it is exactly 511, read one more bit and return dense index 511 or 512 accordingly.',
        'After prefix decode, reuse the existing dense-index arithmetic and exact shortest-word decode laws unchanged; this pass only shortens the transport code, not the downstream semantics.',
        'Keep the earlier local-choice codec when the feasible interval state is already stored elsewhere; this new prefix law is specifically for self-contained exact-script transport.',
    ]


@lru_cache(maxsize=1)
def build_source_reports() -> list[str]:
    return [
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_prefix_law_snapshot_20260309.md',
        'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_dense_index_law.py',
    ]


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_shared_half_step_shortest_generator_word_prefix_snapshot() -> dict[str, Any]:
    return {
        'focus': 'The exact normalized shortest half-step generator-word catalog now travels as a self-delimiting canonical prefix code with 511 nine-bit words and only two ten-bit exceptions.',
        'headline_findings': build_headline_findings(),
        'decision_rules': build_decision_rules(),
        'shortest_generator_word_prefix_examples': build_shortest_generator_word_prefix_examples(),
        'source_reports': build_source_reports(),
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_prefix_law.py',
    }


def main() -> None:
    print(json.dumps(build_service_mode_suffix_batch_shared_half_step_shortest_generator_word_prefix_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
