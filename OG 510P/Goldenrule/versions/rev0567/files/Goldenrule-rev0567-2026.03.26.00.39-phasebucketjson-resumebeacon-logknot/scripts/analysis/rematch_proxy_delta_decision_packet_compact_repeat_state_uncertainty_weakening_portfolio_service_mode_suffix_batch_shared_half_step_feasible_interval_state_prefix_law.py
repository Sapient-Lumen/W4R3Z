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

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_dense_codec_arithmetic_decode_law import (
    decode_feasible_interval_state_from_dense_index_by_arithmetic,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_dense_index_law import (
    FEASIBLE_INTERVAL_STATE_COUNT,
    MAX_FEASIBLE_INTERVAL_STATE_DENSE_INDEX,
    decode_feasible_interval_state_from_dense_index,
    encode_feasible_interval_state_as_dense_index,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_feasible_interval_law import (
    serialize_feasible_interval_kernel_state,
)


class WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepFeasibleIntervalStatePrefixLawError(RuntimeError):
    pass


PREFIX_SHORT_BIT_LENGTH = 7
PREFIX_LONG_BIT_LENGTH = 8
PREFIX_SHORT_CODE_COUNT = (2**PREFIX_SHORT_BIT_LENGTH) - (FEASIBLE_INTERVAL_STATE_COUNT - 2**PREFIX_SHORT_BIT_LENGTH)
PREFIX_SHORT_MAX_DENSE_INDEX = PREFIX_SHORT_CODE_COUNT - 1
PREFIX_LONG_DENSE_INDEX_RANGE = [PREFIX_SHORT_CODE_COUNT, MAX_FEASIBLE_INTERVAL_STATE_DENSE_INDEX]
FIXED_WIDTH_DENSE_INDEX_BIT_LENGTH = MAX_FEASIBLE_INTERVAL_STATE_DENSE_INDEX.bit_length()


@lru_cache(maxsize=None)
def encode_feasible_interval_state_dense_index_as_prefix_bits(dense_index: int) -> str:
    dense_index = int(dense_index)
    if dense_index < 0 or dense_index > MAX_FEASIBLE_INTERVAL_STATE_DENSE_INDEX:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepFeasibleIntervalStatePrefixLawError(
            'dense interval-state index must stay within 0..152 on the current path'
        )
    if dense_index <= PREFIX_SHORT_MAX_DENSE_INDEX:
        return format(dense_index, f'0{PREFIX_SHORT_BIT_LENGTH}b')

    offset = dense_index - PREFIX_SHORT_CODE_COUNT
    return format(PREFIX_SHORT_CODE_COUNT + (offset // 2), f'0{PREFIX_SHORT_BIT_LENGTH}b') + str(offset % 2)


@lru_cache(maxsize=None)
def encode_feasible_interval_state_as_prefix_bits(
    state: tuple[int, int] | list[int],
) -> str:
    return encode_feasible_interval_state_dense_index_as_prefix_bits(
        encode_feasible_interval_state_as_dense_index(state)
    )


@lru_cache(maxsize=None)
def decode_feasible_interval_state_dense_index_from_prefix_bits(
    bitstream: str,
    start_offset: int = 0,
) -> tuple[int, int]:
    start_offset = int(start_offset)
    if start_offset < 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepFeasibleIntervalStatePrefixLawError(
            'prefix decode offset must be nonnegative'
        )
    if start_offset + PREFIX_SHORT_BIT_LENGTH > len(bitstream):
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepFeasibleIntervalStatePrefixLawError(
            'interval-state prefix decode requires at least 7 bits from the current offset'
        )

    prefix = bitstream[start_offset : start_offset + PREFIX_SHORT_BIT_LENGTH]
    prefix_value = int(prefix, 2)
    if prefix_value < PREFIX_SHORT_CODE_COUNT:
        return prefix_value, PREFIX_SHORT_BIT_LENGTH

    if start_offset + PREFIX_LONG_BIT_LENGTH > len(bitstream):
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepFeasibleIntervalStatePrefixLawError(
            'long-form interval-state prefix decode requires one extra eighth bit'
        )

    dense_index = PREFIX_SHORT_CODE_COUNT + 2 * (prefix_value - PREFIX_SHORT_CODE_COUNT) + int(
        bitstream[start_offset + PREFIX_SHORT_BIT_LENGTH], 2
    )
    return dense_index, PREFIX_LONG_BIT_LENGTH


@lru_cache(maxsize=None)
def decode_feasible_interval_state_from_prefix_bits(
    bitstream: str,
    start_offset: int = 0,
) -> tuple[tuple[int, int], int]:
    dense_index, bits_consumed = decode_feasible_interval_state_dense_index_from_prefix_bits(bitstream, start_offset)
    return decode_feasible_interval_state_from_dense_index_by_arithmetic(dense_index), bits_consumed


@lru_cache(maxsize=1)
def build_feasible_interval_state_prefix_examples() -> list[dict[str, Any]]:
    example_dense_indices = (0, 16, 102, 103, 152)
    examples: list[dict[str, Any]] = []
    for dense_index in example_dense_indices:
        state = decode_feasible_interval_state_from_dense_index_by_arithmetic(dense_index)
        prefix_bits = encode_feasible_interval_state_dense_index_as_prefix_bits(dense_index)
        examples.append(
            {
                'feasible_interval_state_prefix_example': {
                    'dense_index': dense_index,
                    'prefix_bits': prefix_bits,
                    'prefix_bit_length': len(prefix_bits),
                    'decoded_interval_kernel_state': serialize_feasible_interval_kernel_state(state),
                }
            }
        )
    return examples


@lru_cache(maxsize=1)
def build_feasible_interval_state_prefix_validation_summary() -> dict[str, Any]:
    prefix_catalog: dict[int, str] = {}
    exact_dense_index_roundtrip_count = 0
    exact_state_roundtrip_count = 0
    exact_arithmetic_state_roundtrip_count = 0
    short_prefix_code_count = 0
    long_prefix_code_count = 0
    total_prefix_bits = 0
    exact_sequential_stream_roundtrip_count = 0

    concatenated_stream_parts: list[str] = []

    for dense_index in range(FEASIBLE_INTERVAL_STATE_COUNT):
        state = decode_feasible_interval_state_from_dense_index(dense_index)
        arithmetic_state = decode_feasible_interval_state_from_dense_index_by_arithmetic(dense_index)
        if arithmetic_state != state:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepFeasibleIntervalStatePrefixLawError(
                f'arithmetic interval-state dense decode mismatch at dense index {dense_index}'
            )
        exact_arithmetic_state_roundtrip_count += 1

        prefix_bits = encode_feasible_interval_state_dense_index_as_prefix_bits(dense_index)
        decoded_dense_index, consumed_bits = decode_feasible_interval_state_dense_index_from_prefix_bits(prefix_bits)
        if decoded_dense_index != dense_index:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepFeasibleIntervalStatePrefixLawError(
                f'prefix dense-index roundtrip mismatch at dense index {dense_index}'
            )
        exact_dense_index_roundtrip_count += 1

        decoded_state, state_consumed_bits = decode_feasible_interval_state_from_prefix_bits(prefix_bits)
        if decoded_state != state:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepFeasibleIntervalStatePrefixLawError(
                f'prefix state roundtrip mismatch at dense index {dense_index}'
            )
        if consumed_bits != state_consumed_bits:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepFeasibleIntervalStatePrefixLawError(
                f'prefix dense-index and state decoders must consume the same bit count at dense index {dense_index}'
            )
        exact_state_roundtrip_count += 1

        prefix_catalog[dense_index] = prefix_bits
        concatenated_stream_parts.append(prefix_bits)
        total_prefix_bits += len(prefix_bits)
        if len(prefix_bits) == PREFIX_SHORT_BIT_LENGTH:
            short_prefix_code_count += 1
        elif len(prefix_bits) == PREFIX_LONG_BIT_LENGTH:
            long_prefix_code_count += 1
        else:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepFeasibleIntervalStatePrefixLawError(
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
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepFeasibleIntervalStatePrefixLawError(
                    f'prefix collision: dense index {left_dense_index} prefixes dense index {right_dense_index}'
                )

    concatenated_stream = ''.join(concatenated_stream_parts)
    cursor = 0
    for dense_index in range(FEASIBLE_INTERVAL_STATE_COUNT):
        decoded_dense_index, consumed_bits = decode_feasible_interval_state_dense_index_from_prefix_bits(concatenated_stream, cursor)
        if decoded_dense_index != dense_index:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepFeasibleIntervalStatePrefixLawError(
                f'sequential stream decode mismatch at dense index {dense_index}'
            )
        cursor += consumed_bits
        exact_sequential_stream_roundtrip_count += 1
    if cursor != len(concatenated_stream):
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepFeasibleIntervalStatePrefixLawError(
            'sequential prefix stream decode must consume the full concatenated interval-state stream exactly'
        )

    fixed_width_total_bits = FEASIBLE_INTERVAL_STATE_COUNT * FIXED_WIDTH_DENSE_INDEX_BIT_LENGTH
    saved_bits_vs_fixed_width_dense_index = fixed_width_total_bits - total_prefix_bits
    mean_prefix_bit_length = total_prefix_bits / FEASIBLE_INTERVAL_STATE_COUNT
    mean_bit_savings_vs_fixed_width_dense_index = saved_bits_vs_fixed_width_dense_index / FEASIBLE_INTERVAL_STATE_COUNT

    return {
        'represented_exact_interval_state_count': FEASIBLE_INTERVAL_STATE_COUNT,
        'short_prefix_bit_length': PREFIX_SHORT_BIT_LENGTH,
        'long_prefix_bit_length': PREFIX_LONG_BIT_LENGTH,
        'short_prefix_code_count': short_prefix_code_count,
        'long_prefix_code_count': long_prefix_code_count,
        'long_prefix_dense_index_range': PREFIX_LONG_DENSE_INDEX_RANGE,
        'exact_arithmetic_state_roundtrip_count': exact_arithmetic_state_roundtrip_count,
        'exact_prefix_dense_index_roundtrip_count': exact_dense_index_roundtrip_count,
        'exact_prefix_state_roundtrip_count': exact_state_roundtrip_count,
        'exact_prefix_sequential_stream_roundtrip_count': exact_sequential_stream_roundtrip_count,
        'prefix_catalog_is_prefix_free': prefix_free_catalog,
        'total_prefix_bits_over_exact_interval_catalog': total_prefix_bits,
        'fixed_width_dense_index_total_bits_over_exact_interval_catalog': fixed_width_total_bits,
        'saved_bits_vs_fixed_width_dense_index': saved_bits_vs_fixed_width_dense_index,
        'saved_bits_share_vs_fixed_width_dense_index': saved_bits_vs_fixed_width_dense_index / fixed_width_total_bits,
        'mean_prefix_bit_length': mean_prefix_bit_length,
        'mean_bit_savings_vs_fixed_width_dense_index': mean_bit_savings_vs_fixed_width_dense_index,
        'exact_uniform_entropy_lower_bound_bits': math.log2(FEASIBLE_INTERVAL_STATE_COUNT),
        'canonical_long_prefix_states': [
            list(decode_feasible_interval_state_from_dense_index_by_arithmetic(dense_index))
            for dense_index in range(PREFIX_LONG_DENSE_INDEX_RANGE[0], PREFIX_LONG_DENSE_INDEX_RANGE[0] + 2)
        ],
        'every_exact_interval_state_is_streamable_as_a_prefix_code_over_the_existing_dense_index': True,
    }


@lru_cache(maxsize=1)
def build_headline_findings() -> dict[str, Any]:
    validation = build_feasible_interval_state_prefix_validation_summary()
    return {
        'existing_dense_interval_state_index_now_has_a_prefix_code_with_103_seven_bit_states_and_50_eight_bit_states': True,
        'mean_prefix_bit_length': validation['mean_prefix_bit_length'],
        'mean_bit_savings_vs_fixed_width_dense_index': validation['mean_bit_savings_vs_fixed_width_dense_index'],
        'saved_bits_vs_fixed_width_dense_index': validation['saved_bits_vs_fixed_width_dense_index'],
        'validation_summary': validation,
    }


@lru_cache(maxsize=1)
def build_decision_rules() -> list[str]:
    return [
        'When the exact normalized feasible interval state itself must travel as a self-delimiting bitstream, keep the existing dense interval-state index but wrap it in the new canonical prefix code instead of writing all 8 dense bits unconditionally.',
        'Encode dense interval-state indices 0..102 as raw 7-bit binaries; encode dense interval-state indices 103..152 as the split 8-bit leaves under the remaining 7-bit prefixes 103..127.',
        'Decode by reading 7 bits first: if the 7-bit value is below 103, stop there; otherwise read one extra bit and compute dense index 103 + 2*(value-103) + suffix.',
        'After prefix decode, reuse the existing dense-index arithmetic interval-state decoder unchanged; this pass only shortens state transport, not the downstream semantics.',
        'Keep the earlier fixed 8-bit dense interval-state index when fixed-width random access or packing simplicity matters more than self-delimiting transport cost; this new prefix law is specifically for self-contained state streaming.',
    ]


@lru_cache(maxsize=1)
def build_source_reports() -> list[str]:
    return [
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_prefix_law_snapshot_20260309.md',
        'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_dense_index_law.py',
    ]


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_shared_half_step_feasible_interval_state_prefix_snapshot() -> dict[str, Any]:
    return {
        'focus': 'The exact normalized feasible interval-state catalog now travels as a self-delimiting canonical prefix code with 103 seven-bit states and 50 eight-bit states.',
        'headline_findings': build_headline_findings(),
        'decision_rules': build_decision_rules(),
        'feasible_interval_state_prefix_examples': build_feasible_interval_state_prefix_examples(),
        'source_reports': build_source_reports(),
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_prefix_law.py',
    }


def main() -> None:
    print(json.dumps(build_service_mode_suffix_batch_shared_half_step_feasible_interval_state_prefix_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
