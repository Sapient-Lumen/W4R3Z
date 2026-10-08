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

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_feasible_interval_law import (
    FeasibleIntervalKernelState,
    MAX_SOURCE_RANK,
    build_half_step_kernel_from_feasible_interval_state,
    serialize_feasible_interval_kernel_state,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_index_law import (
    build_shortest_generator_word_choice_index_bit_width_for_feasible_interval_state,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_law import (
    build_canonical_shortest_generator_word_for_feasible_interval_state,
    serialize_generator_word,
)


class WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepFeasibleIntervalStateDenseIndexLawError(RuntimeError):
    pass


FEASIBLE_INTERVAL_STATE_COUNT = ((MAX_SOURCE_RANK + 1) * (MAX_SOURCE_RANK + 2)) // 2
MAX_FEASIBLE_INTERVAL_STATE_DENSE_INDEX = FEASIBLE_INTERVAL_STATE_COUNT - 1
FEASIBLE_INTERVAL_STATE_DENSE_INDEX_BIT_WIDTH = MAX_FEASIBLE_INTERVAL_STATE_DENSE_INDEX.bit_length()
RAW_ENDPOINT_PAIR_BIT_WIDTH = 2 * MAX_SOURCE_RANK.bit_length()


@lru_cache(maxsize=None)
def _normalize_feasible_interval_state(
    state: tuple[int, int] | list[int],
) -> FeasibleIntervalKernelState:
    if len(state) != 2:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepFeasibleIntervalStateDenseIndexLawError(
            'feasible interval state must contain exactly two ranks'
        )
    lower_rank = int(state[0])
    upper_rank = int(state[1])
    if lower_rank < 0 or upper_rank < lower_rank or upper_rank > MAX_SOURCE_RANK:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepFeasibleIntervalStateDenseIndexLawError(
            'feasible interval state must stay within the realized 17-state path bounds'
        )
    return lower_rank, upper_rank


@lru_cache(maxsize=None)
def build_feasible_interval_state_dense_index_prefix(lower_rank: int) -> int:
    lower_rank = int(lower_rank)
    if lower_rank < 0 or lower_rank > MAX_SOURCE_RANK:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepFeasibleIntervalStateDenseIndexLawError(
            'lower rank must stay within the realized 17-state path bounds'
        )
    return (lower_rank * (2 * (MAX_SOURCE_RANK + 1) + 1 - lower_rank)) // 2


@lru_cache(maxsize=None)
def encode_feasible_interval_state_as_dense_index(
    state: tuple[int, int] | list[int],
) -> int:
    lower_rank, upper_rank = _normalize_feasible_interval_state(state)
    return build_feasible_interval_state_dense_index_prefix(lower_rank) + (upper_rank - lower_rank)


@lru_cache(maxsize=None)
def decode_feasible_interval_state_from_dense_index(
    dense_index: int,
) -> FeasibleIntervalKernelState:
    dense_index = int(dense_index)
    if dense_index < 0 or dense_index > MAX_FEASIBLE_INTERVAL_STATE_DENSE_INDEX:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepFeasibleIntervalStateDenseIndexLawError(
            'dense interval-state index must stay within 0..152 on the current path'
        )

    remaining_index = dense_index
    for lower_rank in range(MAX_SOURCE_RANK + 1):
        span = MAX_SOURCE_RANK + 1 - lower_rank
        if remaining_index < span:
            return lower_rank, lower_rank + remaining_index
        remaining_index -= span

    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepFeasibleIntervalStateDenseIndexLawError(
        'dense interval-state index should always decode inside the realized triangular catalog'
    )


@lru_cache(maxsize=1)
def build_all_realized_feasible_interval_states() -> tuple[FeasibleIntervalKernelState, ...]:
    return tuple(
        (lower_rank, upper_rank)
        for lower_rank in range(MAX_SOURCE_RANK + 1)
        for upper_rank in range(lower_rank, MAX_SOURCE_RANK + 1)
    )


@lru_cache(maxsize=1)
def build_feasible_interval_state_dense_index_examples() -> list[dict[str, Any]]:
    example_states = ((0, 0), (0, MAX_SOURCE_RANK), (1, 1), (3, 8), (MAX_SOURCE_RANK, MAX_SOURCE_RANK))
    return [
        {
            'feasible_interval_state_dense_index_example': {
                'interval_kernel_state': serialize_feasible_interval_kernel_state(state),
                'dense_index_prefix_formula': f"{state[0]}*(35-{state[0]})/2",
                'dense_index': encode_feasible_interval_state_as_dense_index(state),
                'decoded_interval_kernel_state': serialize_feasible_interval_kernel_state(
                    decode_feasible_interval_state_from_dense_index(encode_feasible_interval_state_as_dense_index(state))
                ),
                'canonical_shortest_generator_word': serialize_generator_word(
                    build_canonical_shortest_generator_word_for_feasible_interval_state(state)
                ),
            }
        }
        for state in example_states
    ]


@lru_cache(maxsize=1)
def build_feasible_interval_state_dense_index_validation_summary() -> dict[str, Any]:
    realized_states = build_all_realized_feasible_interval_states()
    seen_dense_indices: set[int] = set()
    exact_roundtrip_count = 0
    canonical_shortest_word_roundtrip_count = 0
    exact_half_step_kernel_roundtrip_count = 0
    total_word_weighted_choice_bits = 0

    for state in realized_states:
        dense_index = encode_feasible_interval_state_as_dense_index(state)
        decoded_state = decode_feasible_interval_state_from_dense_index(dense_index)
        if decoded_state != state:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepFeasibleIntervalStateDenseIndexLawError(
                f'dense interval-state roundtrip mismatch: expected {state}, got {decoded_state}'
            )
        seen_dense_indices.add(dense_index)
        exact_roundtrip_count += 1

        if build_half_step_kernel_from_feasible_interval_state(decoded_state) != build_half_step_kernel_from_feasible_interval_state(state):
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepFeasibleIntervalStateDenseIndexLawError(
                f'decoded interval state must preserve the exact half-step kernel: {state}'
            )
        exact_half_step_kernel_roundtrip_count += 1

        decoded_canonical_word = build_canonical_shortest_generator_word_for_feasible_interval_state(decoded_state)
        original_canonical_word = build_canonical_shortest_generator_word_for_feasible_interval_state(state)
        if decoded_canonical_word != original_canonical_word:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepFeasibleIntervalStateDenseIndexLawError(
                f'decoded interval state must preserve the canonical shortest word: {state}'
            )
        canonical_shortest_word_roundtrip_count += 1
        total_word_weighted_choice_bits += build_shortest_generator_word_choice_index_bit_width_for_feasible_interval_state(state)

    contiguous_dense_index_catalog = seen_dense_indices == set(range(FEASIBLE_INTERVAL_STATE_COUNT))
    if not contiguous_dense_index_catalog:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepFeasibleIntervalStateDenseIndexLawError(
            'feasible interval-state dense indices must fill the full 0..152 range without gaps'
        )

    dense_index_bit_savings_vs_raw_endpoint_pair = RAW_ENDPOINT_PAIR_BIT_WIDTH - FEASIBLE_INTERVAL_STATE_DENSE_INDEX_BIT_WIDTH
    return {
        'reachable_exact_feasible_interval_kernel_count': len(realized_states),
        'maximum_feasible_interval_state_dense_index': MAX_FEASIBLE_INTERVAL_STATE_DENSE_INDEX,
        'dense_index_bit_width': FEASIBLE_INTERVAL_STATE_DENSE_INDEX_BIT_WIDTH,
        'raw_endpoint_pair_bit_width': RAW_ENDPOINT_PAIR_BIT_WIDTH,
        'dense_index_bit_savings_vs_raw_endpoint_pair': dense_index_bit_savings_vs_raw_endpoint_pair,
        'dense_index_bit_savings_share_vs_raw_endpoint_pair': dense_index_bit_savings_vs_raw_endpoint_pair / RAW_ENDPOINT_PAIR_BIT_WIDTH,
        'exact_dense_index_roundtrip_count': exact_roundtrip_count,
        'exact_half_step_kernel_roundtrip_count': exact_half_step_kernel_roundtrip_count,
        'exact_canonical_shortest_word_roundtrip_count': canonical_shortest_word_roundtrip_count,
        'dense_index_catalog_is_contiguous': contiguous_dense_index_catalog,
        'dense_index_zero_state': list(decode_feasible_interval_state_from_dense_index(0)),
        'dense_index_max_state': list(decode_feasible_interval_state_from_dense_index(MAX_FEASIBLE_INTERVAL_STATE_DENSE_INDEX)),
        'mean_local_choice_bit_width_once_dense_interval_index_is_known': total_word_weighted_choice_bits / len(realized_states),
        'every_dense_interval_index_decodes_to_a_unique_exact_interval_kernel_state': True,
    }


@lru_cache(maxsize=1)
def build_headline_findings() -> dict[str, Any]:
    validation = build_feasible_interval_state_dense_index_validation_summary()
    return {
        'every_exact_normalized_half_step_interval_kernel_state_is_addressable_by_dense_triangular_index': True,
        'dense_index_bit_width': validation['dense_index_bit_width'],
        'maximum_feasible_interval_state_dense_index': validation['maximum_feasible_interval_state_dense_index'],
        'dense_index_bit_savings_vs_raw_endpoint_pair': validation['dense_index_bit_savings_vs_raw_endpoint_pair'],
        'validation_summary': validation,
    }


@lru_cache(maxsize=1)
def build_decision_rules() -> list[str]:
    return [
        'When the exact normalized downstream state itself is what matters, persist the feasible interval as one dense triangular index 0..152 instead of two separate endpoint ranks or a shortest-word script.',
        'Use lower-major triangular indexing: index([a,b]) = a*(35-a)/2 + (b-a) on the current 17-rank path.',
        'Decode by walking the triangular lower-rank blocks until the remaining offset lands inside one block; the decoded state then recovers the exact half-step kernel, the canonical shortest generator word, and any local choice-index family.',
        'Treat the dense interval index as the base exact state codec and use the earlier local choice index only when a noncanonical shortest script must also be preserved.',
        'Do not spend 10 fixed bits on raw endpoint pairs when 8 fixed bits already cover the full realized 153-state catalog exactly on the current path.',
    ]


@lru_cache(maxsize=1)
def build_source_reports() -> list[str]:
    return [
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_index_law_snapshot_20260309.md',
        'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_dense_index_law.py',
    ]


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_shared_half_step_feasible_interval_state_dense_index_snapshot() -> dict[str, Any]:
    return {
        'focus': 'Every exact normalized half-step feasible interval kernel state is now addressable by one dense triangular index instead of an endpoint pair or shortest-word script.',
        'headline_findings': build_headline_findings(),
        'decision_rules': build_decision_rules(),
        'feasible_interval_state_dense_index_examples': build_feasible_interval_state_dense_index_examples(),
        'source_reports': build_source_reports(),
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_dense_index_law.py',
    }


def main() -> None:
    print(json.dumps(build_service_mode_suffix_batch_shared_half_step_feasible_interval_state_dense_index_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
