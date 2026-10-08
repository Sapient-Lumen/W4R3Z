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

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_dense_index_law import (
    MAX_FEASIBLE_INTERVAL_STATE_DENSE_INDEX,
    build_all_realized_feasible_interval_states,
    decode_feasible_interval_state_from_dense_index,
    encode_feasible_interval_state_as_dense_index,
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
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_dense_index_law import (
    EXACT_SHORTEST_GENERATOR_WORD_COUNT,
    INTERIOR_NONSINGLETON_BLOCK_START,
    INTERIOR_SINGLETON_BLOCK_START,
    MAX_EXACT_SHORTEST_GENERATOR_WORD_DENSE_INDEX,
    ONE_SIDED_BLOCK_START,
    build_interior_nonsingleton_state_prefix,
    decode_shortest_generator_word_dense_index_to_state_and_choice,
    decode_shortest_generator_word_from_dense_index,
    encode_shortest_generator_word_as_dense_index,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_law import (
    GeneratorWord,
    serialize_generator_word,
)


class WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepDenseCodecArithmeticDecodeLawError(RuntimeError):
    pass


INTERVAL_DENSE_INDEX_ROOT_COEFFICIENT = 2 * MAX_SOURCE_RANK + 3
INTERVAL_DENSE_INDEX_DISCRIMINANT_MAX = INTERVAL_DENSE_INDEX_ROOT_COEFFICIENT**2
INTERIOR_NONSINGLETON_ROOT_COEFFICIENT = 2 * MAX_SOURCE_RANK - 3
INTERIOR_NONSINGLETON_DISCRIMINANT_MAX = INTERIOR_NONSINGLETON_ROOT_COEFFICIENT**2
ONE_SIDED_NONIDENTITY_WORD_COUNT = 2 * MAX_SOURCE_RANK
INTERIOR_SINGLETON_LOCAL_CHOICE_COUNT = MAX_SOURCE_RANK + 2


@lru_cache(maxsize=None)
def ceil_sqrt(nonnegative_integer: int) -> int:
    nonnegative_integer = int(nonnegative_integer)
    if nonnegative_integer < 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepDenseCodecArithmeticDecodeLawError(
            'ceil_sqrt only accepts nonnegative integers'
        )
    if nonnegative_integer == 0:
        return 0
    return math.isqrt(nonnegative_integer - 1) + 1


@lru_cache(maxsize=None)
def decode_feasible_interval_state_from_dense_index_by_arithmetic(
    dense_index: int,
) -> FeasibleIntervalKernelState:
    dense_index = int(dense_index)
    if dense_index < 0 or dense_index > MAX_FEASIBLE_INTERVAL_STATE_DENSE_INDEX:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepDenseCodecArithmeticDecodeLawError(
            'dense interval-state index must stay within 0..152 on the current path'
        )

    discriminant = INTERVAL_DENSE_INDEX_DISCRIMINANT_MAX - 8 * dense_index
    lower_rank = (INTERVAL_DENSE_INDEX_ROOT_COEFFICIENT - ceil_sqrt(discriminant)) // 2
    prefix = (lower_rank * (INTERVAL_DENSE_INDEX_ROOT_COEFFICIENT - lower_rank)) // 2
    upper_rank = lower_rank + (dense_index - prefix)
    return lower_rank, upper_rank


@lru_cache(maxsize=None)
def decode_interior_nonsingleton_state_offset_by_arithmetic(
    state_offset: int,
) -> FeasibleIntervalKernelState:
    state_offset = int(state_offset)
    max_state_offset = ((MAX_SOURCE_RANK - 1) * (MAX_SOURCE_RANK - 2)) // 2 - 1
    if state_offset < 0 or state_offset > max_state_offset:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepDenseCodecArithmeticDecodeLawError(
            'interior nonsingleton state offset must stay within 0..104 on the current path'
        )

    discriminant = INTERIOR_NONSINGLETON_DISCRIMINANT_MAX - 8 * state_offset
    lower_rank = 1 + (INTERIOR_NONSINGLETON_ROOT_COEFFICIENT - ceil_sqrt(discriminant)) // 2
    prefix = build_interior_nonsingleton_state_prefix(lower_rank)
    upper_rank = lower_rank + 1 + (state_offset - prefix)
    return lower_rank, upper_rank


@lru_cache(maxsize=None)
def decode_shortest_generator_word_dense_index_to_state_and_choice_by_arithmetic(
    dense_index: int,
) -> tuple[FeasibleIntervalKernelState, int]:
    dense_index = int(dense_index)
    if dense_index < 0 or dense_index > MAX_EXACT_SHORTEST_GENERATOR_WORD_DENSE_INDEX:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepDenseCodecArithmeticDecodeLawError(
            'dense shortest-word index must stay within 0..512 on the current path'
        )

    if dense_index == 0:
        return (0, MAX_SOURCE_RANK), 0

    if dense_index < INTERIOR_NONSINGLETON_BLOCK_START:
        one_sided_offset = dense_index - ONE_SIDED_BLOCK_START
        if one_sided_offset < MAX_SOURCE_RANK:
            return (0, one_sided_offset), 0
        return (one_sided_offset - MAX_SOURCE_RANK + 1, MAX_SOURCE_RANK), 0

    if dense_index < INTERIOR_SINGLETON_BLOCK_START:
        nonsingleton_offset = dense_index - INTERIOR_NONSINGLETON_BLOCK_START
        state_offset, choice_index = divmod(nonsingleton_offset, 2)
        return decode_interior_nonsingleton_state_offset_by_arithmetic(state_offset), choice_index

    singleton_offset = dense_index - INTERIOR_SINGLETON_BLOCK_START
    lower_rank, choice_index = divmod(singleton_offset, INTERIOR_SINGLETON_LOCAL_CHOICE_COUNT)
    lower_rank += 1
    return (lower_rank, lower_rank), choice_index


@lru_cache(maxsize=None)
def decode_shortest_generator_word_from_dense_index_by_arithmetic(
    dense_index: int,
) -> GeneratorWord:
    state, choice_index = decode_shortest_generator_word_dense_index_to_state_and_choice_by_arithmetic(dense_index)
    return decode_shortest_generator_word_from_choice_index(state, choice_index)


@lru_cache(maxsize=1)
def build_dense_codec_arithmetic_decode_examples() -> list[dict[str, Any]]:
    example_interval_indices = (0, 16, 17, 58, MAX_FEASIBLE_INTERVAL_STATE_DENSE_INDEX)
    example_word_indices = (0, 11, 32, 33, 77, 243, MAX_EXACT_SHORTEST_GENERATOR_WORD_DENSE_INDEX)
    examples: list[dict[str, Any]] = []
    for dense_index in example_interval_indices:
        state = decode_feasible_interval_state_from_dense_index_by_arithmetic(dense_index)
        examples.append(
            {
                'dense_interval_decode_example': {
                    'dense_index': dense_index,
                    'interval_discriminant': INTERVAL_DENSE_INDEX_DISCRIMINANT_MAX - 8 * dense_index,
                    'decoded_interval_kernel_state': serialize_feasible_interval_kernel_state(state),
                    'reencoded_dense_index': encode_feasible_interval_state_as_dense_index(state),
                }
            }
        )
    for dense_index in example_word_indices:
        state, choice_index = decode_shortest_generator_word_dense_index_to_state_and_choice_by_arithmetic(dense_index)
        examples.append(
            {
                'dense_word_decode_example': {
                    'dense_index': dense_index,
                    'decoded_interval_kernel_state': serialize_feasible_interval_kernel_state(state),
                    'decoded_local_choice_index': choice_index,
                    'decoded_generator_word': serialize_generator_word(
                        decode_shortest_generator_word_from_dense_index_by_arithmetic(dense_index)
                    ),
                }
            }
        )
    return examples


@lru_cache(maxsize=1)
def build_dense_codec_arithmetic_decode_validation_summary() -> dict[str, Any]:
    interval_roundtrip_count = 0
    interval_decoder_equivalence_count = 0
    interval_total_legacy_scan_iterations = 0
    interval_max_legacy_scan_iterations = 0

    for dense_index in range(MAX_FEASIBLE_INTERVAL_STATE_DENSE_INDEX + 1):
        arithmetic_state = decode_feasible_interval_state_from_dense_index_by_arithmetic(dense_index)
        legacy_state = decode_feasible_interval_state_from_dense_index(dense_index)
        if arithmetic_state != legacy_state:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepDenseCodecArithmeticDecodeLawError(
                f'arithmetic dense interval decoder mismatch at index {dense_index}: {arithmetic_state} != {legacy_state}'
            )
        if encode_feasible_interval_state_as_dense_index(arithmetic_state) != dense_index:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepDenseCodecArithmeticDecodeLawError(
                f'arithmetic dense interval decoder must roundtrip at index {dense_index}'
            )
        interval_roundtrip_count += 1
        interval_decoder_equivalence_count += 1
        scan_iterations = arithmetic_state[0] + 1
        interval_total_legacy_scan_iterations += scan_iterations
        interval_max_legacy_scan_iterations = max(interval_max_legacy_scan_iterations, scan_iterations)

    word_roundtrip_count = 0
    word_decoder_equivalence_count = 0
    state_and_choice_equivalence_count = 0
    word_total_legacy_scan_iterations = 0
    word_max_legacy_scan_iterations = 0
    exact_shortest_word_count = 0
    exact_local_choice_branch_count = 0

    for state in build_all_realized_feasible_interval_states():
        choice_count = build_shortest_generator_word_choice_count_for_feasible_interval_state(state)
        exact_local_choice_branch_count += choice_count
        for choice_index in range(choice_count):
            word = decode_shortest_generator_word_from_choice_index(state, choice_index)
            dense_index = encode_shortest_generator_word_as_dense_index(word)
            arithmetic_state, arithmetic_choice = decode_shortest_generator_word_dense_index_to_state_and_choice_by_arithmetic(
                dense_index
            )
            legacy_state, legacy_choice = decode_shortest_generator_word_dense_index_to_state_and_choice(dense_index)
            if (arithmetic_state, arithmetic_choice) != (legacy_state, legacy_choice):
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepDenseCodecArithmeticDecodeLawError(
                    f'arithmetic dense shortest-word state/choice decoder mismatch at index {dense_index}'
                )
            if arithmetic_state != state or arithmetic_choice != choice_index:
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepDenseCodecArithmeticDecodeLawError(
                    f'arithmetic dense shortest-word state/choice decoder must preserve state and choice at index {dense_index}'
                )
            state_and_choice_equivalence_count += 1

            arithmetic_word = decode_shortest_generator_word_from_dense_index_by_arithmetic(dense_index)
            legacy_word = decode_shortest_generator_word_from_dense_index(dense_index)
            if arithmetic_word != legacy_word or arithmetic_word != word:
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepDenseCodecArithmeticDecodeLawError(
                    f'arithmetic dense shortest-word decoder mismatch at index {dense_index}'
                )
            if encode_shortest_generator_word_as_dense_index(arithmetic_word) != dense_index:
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepDenseCodecArithmeticDecodeLawError(
                    f'arithmetic dense shortest-word decoder must roundtrip at index {dense_index}'
                )
            word_roundtrip_count += 1
            word_decoder_equivalence_count += 1
            exact_shortest_word_count += 1

            if INTERIOR_NONSINGLETON_BLOCK_START <= dense_index < INTERIOR_SINGLETON_BLOCK_START:
                scan_iterations = state[0]
                word_total_legacy_scan_iterations += scan_iterations
                word_max_legacy_scan_iterations = max(word_max_legacy_scan_iterations, scan_iterations)

    if exact_shortest_word_count != EXACT_SHORTEST_GENERATOR_WORD_COUNT:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepDenseCodecArithmeticDecodeLawError(
            'the exact shortest-word catalog size must remain 513 on the current path'
        )

    total_legacy_scan_iterations = interval_total_legacy_scan_iterations + word_total_legacy_scan_iterations
    return {
        'exact_dense_interval_state_decoder_equivalence_count': interval_decoder_equivalence_count,
        'exact_dense_interval_state_roundtrip_count': interval_roundtrip_count,
        'exact_dense_shortest_word_state_choice_decoder_equivalence_count': state_and_choice_equivalence_count,
        'exact_dense_shortest_word_decoder_equivalence_count': word_decoder_equivalence_count,
        'exact_dense_shortest_word_roundtrip_count': word_roundtrip_count,
        'exact_shortest_word_catalog_count': exact_shortest_word_count,
        'exact_local_choice_branch_count': exact_local_choice_branch_count,
        'interval_dense_decode_legacy_scan_iteration_total': interval_total_legacy_scan_iterations,
        'interval_dense_decode_legacy_scan_iteration_mean': interval_total_legacy_scan_iterations / (MAX_FEASIBLE_INTERVAL_STATE_DENSE_INDEX + 1),
        'interval_dense_decode_legacy_scan_iteration_max': interval_max_legacy_scan_iterations,
        'shortest_word_dense_decode_legacy_scan_iteration_total': word_total_legacy_scan_iterations,
        'shortest_word_dense_decode_legacy_scan_iteration_mean_over_full_catalog': word_total_legacy_scan_iterations / EXACT_SHORTEST_GENERATOR_WORD_COUNT,
        'shortest_word_dense_decode_legacy_scan_iteration_max': word_max_legacy_scan_iterations,
        'total_legacy_scan_iterations_removed_by_exhaustive_arithmetic_revalidation': total_legacy_scan_iterations,
        'interval_dense_decode_formula': 'a = (35 - ceil_sqrt(1225 - 8*i)) // 2; b = a + i - a*(35-a)//2',
        'interior_nonsingleton_dense_decode_formula': 'a = 1 + (29 - ceil_sqrt(841 - 8*s)) // 2; b = a + 1 + s - (a-1)*(30-a)//2',
        'dense_interval_and_dense_word_codecs_now_admit_tableless_arithmetic_decode': True,
    }


@lru_cache(maxsize=1)
def build_headline_findings() -> dict[str, Any]:
    validation = build_dense_codec_arithmetic_decode_validation_summary()
    return {
        'dense_interval_and_dense_word_codecs_now_decode_by_closed_form_arithmetic': True,
        'interval_dense_decode_discriminant_max': INTERVAL_DENSE_INDEX_DISCRIMINANT_MAX,
        'interior_nonsingleton_dense_decode_discriminant_max': INTERIOR_NONSINGLETON_DISCRIMINANT_MAX,
        'validation_summary': validation,
    }


@lru_cache(maxsize=1)
def build_decision_rules() -> list[str]:
    return [
        'Decode the dense interval-state codec 0..152 by closed-form arithmetic instead of scanning triangular lower-rank blocks: a = (35 - ceil_sqrt(1225 - 8*i)) // 2 and b = a + i - a*(35-a)//2 on the current 17-rank path.',
        'Route the dense exact shortest-word codec 0..512 by its existing four block ranges, then decode the interior nonsingleton subblock by the matching arithmetic inverse over state offset s = (index-33) // 2.',
        'Use ceil_sqrt(n) = isqrt(n-1) + 1 for positive integers n when an exact integer ceiling root is needed. This keeps the inverse dense decoders tableless and branch-light.',
        'Keep the dense interval-state codec as the base exact state representation and the dense global shortest-word codec as the one-scalar exact script representation; this pass only tightens their decode path.',
        'Do not keep triangular scan loops in inheritor-facing implementations when the same exact decoders now exist in closed form and were revalidated exhaustively on the full 153-state and 513-word catalogs.',
    ]


@lru_cache(maxsize=1)
def build_source_reports() -> list[str]:
    return [
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_dense_index_law_snapshot_20260309.md',
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_dense_index_law_snapshot_20260309.md',
        'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_dense_codec_arithmetic_decode_law.py',
    ]


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_shared_half_step_dense_codec_arithmetic_decode_snapshot() -> dict[str, Any]:
    return {
        'focus': 'The exact normalized half-step dense interval-state codec and dense shortest-word codec now admit closed-form arithmetic decoders, so inheritors no longer need triangular scan loops.',
        'headline_findings': build_headline_findings(),
        'decision_rules': build_decision_rules(),
        'dense_codec_arithmetic_decode_examples': build_dense_codec_arithmetic_decode_examples(),
        'source_reports': build_source_reports(),
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_dense_codec_arithmetic_decode_law.py',
    }


def main() -> None:
    print(json.dumps(build_service_mode_suffix_batch_shared_half_step_dense_codec_arithmetic_decode_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
