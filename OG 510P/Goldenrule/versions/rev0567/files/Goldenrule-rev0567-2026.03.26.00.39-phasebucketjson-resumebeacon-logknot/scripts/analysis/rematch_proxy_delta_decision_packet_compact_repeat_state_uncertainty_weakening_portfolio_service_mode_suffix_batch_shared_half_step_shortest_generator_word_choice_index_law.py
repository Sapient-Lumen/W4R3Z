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

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_normal_form_law import (
    MAX_SOURCE_RANK,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_family_law import (
    build_closed_form_shortest_generator_words_for_feasible_interval_state,
    build_shortest_generator_word_family_cardinality_for_feasible_interval_state,
    classify_feasible_interval_state,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_law import (
    GeneratorWord,
    build_canonical_shortest_generator_word_for_feasible_interval_state,
    build_shortest_generator_words_by_feasible_interval_state,
    serialize_generator_word,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_feasible_interval_law import (
    FeasibleIntervalKernelState,
    serialize_feasible_interval_kernel_state,
)


class WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordChoiceIndexLawError(RuntimeError):
    pass


@lru_cache(maxsize=None)
def _normalize_feasible_interval_state(
    state: tuple[int, int] | list[int],
) -> FeasibleIntervalKernelState:
    if len(state) != 2:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordChoiceIndexLawError(
            'feasible interval state must contain exactly two ranks'
        )
    lower_rank = int(state[0])
    upper_rank = int(state[1])
    if lower_rank < 0 or upper_rank < lower_rank or upper_rank > MAX_SOURCE_RANK:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordChoiceIndexLawError(
            'feasible interval state must stay within the realized 17-state path bounds'
        )
    return lower_rank, upper_rank


@lru_cache(maxsize=None)
def build_shortest_generator_word_choice_count_for_feasible_interval_state(
    state: tuple[int, int] | list[int],
) -> int:
    return build_shortest_generator_word_family_cardinality_for_feasible_interval_state(_normalize_feasible_interval_state(state))


@lru_cache(maxsize=None)
def build_max_shortest_generator_word_choice_index_for_feasible_interval_state(
    state: tuple[int, int] | list[int],
) -> int:
    return build_shortest_generator_word_choice_count_for_feasible_interval_state(_normalize_feasible_interval_state(state)) - 1


@lru_cache(maxsize=None)
def build_shortest_generator_word_choice_index_bit_width_for_feasible_interval_state(
    state: tuple[int, int] | list[int],
) -> int:
    max_index = build_max_shortest_generator_word_choice_index_for_feasible_interval_state(_normalize_feasible_interval_state(state))
    return max_index.bit_length()


@lru_cache(maxsize=None)
def decode_shortest_generator_word_from_choice_index(
    state: tuple[int, int] | list[int],
    choice_index: int,
) -> GeneratorWord:
    lower_rank, upper_rank = _normalize_feasible_interval_state(state)
    choice_index = int(choice_index)
    if choice_index < 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordChoiceIndexLawError(
            'choice index must be nonnegative'
        )

    category = classify_feasible_interval_state((lower_rank, upper_rank))
    if category in {'identity', 'one_sided_nonidentity'}:
        if choice_index != 0:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordChoiceIndexLawError(
                'unique shortest-word families admit only choice index 0'
            )
        return build_canonical_shortest_generator_word_for_feasible_interval_state((lower_rank, upper_rank))

    if category == 'interior_nonsingleton':
        if choice_index == 0:
            return ((lower_rank, MAX_SOURCE_RANK), (0, upper_rank))
        if choice_index == 1:
            return ((0, upper_rank), (lower_rank, MAX_SOURCE_RANK))
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordChoiceIndexLawError(
            'interior nonsingleton intervals admit only choice indices 0 or 1'
        )

    if choice_index <= MAX_SOURCE_RANK - lower_rank:
        return ((lower_rank + choice_index, MAX_SOURCE_RANK), (0, upper_rank))
    if choice_index <= MAX_SOURCE_RANK + 1:
        return ((0, MAX_SOURCE_RANK + 1 - choice_index), (lower_rank, MAX_SOURCE_RANK))
    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordChoiceIndexLawError(
        'interior singleton intervals admit only choice indices 0..17'
    )


@lru_cache(maxsize=None)
def encode_shortest_generator_word_as_choice_index(
    state: tuple[int, int] | list[int],
    generator_word: GeneratorWord,
) -> int:
    lower_rank, upper_rank = _normalize_feasible_interval_state(state)
    family = build_closed_form_shortest_generator_words_for_feasible_interval_state((lower_rank, upper_rank))
    if generator_word not in family:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordChoiceIndexLawError(
            f'generator word {generator_word} is not a shortest word for state {(lower_rank, upper_rank)}'
        )

    category = classify_feasible_interval_state((lower_rank, upper_rank))
    if category in {'identity', 'one_sided_nonidentity'}:
        return 0
    if category == 'interior_nonsingleton':
        return 0 if generator_word == ((lower_rank, MAX_SOURCE_RANK), (0, upper_rank)) else 1

    first_interval = generator_word[0]
    if first_interval[1] == MAX_SOURCE_RANK:
        return first_interval[0] - lower_rank
    return MAX_SOURCE_RANK + 1 - first_interval[1]


@lru_cache(maxsize=1)
def build_shortest_generator_word_choice_examples() -> list[dict[str, Any]]:
    interior_nonsingleton = (3, 8)
    interior_singleton = (5, 5)
    one_sided = (0, 11)

    return [
        {
            'one_sided_interval_needs_no_extra_choice_bits': {
                'interval_kernel_state': serialize_feasible_interval_kernel_state(one_sided),
                'choice_count': build_shortest_generator_word_choice_count_for_feasible_interval_state(one_sided),
                'choice_index_bit_width': build_shortest_generator_word_choice_index_bit_width_for_feasible_interval_state(one_sided),
                'choice_index_to_shortest_word': {
                    '0': serialize_generator_word(decode_shortest_generator_word_from_choice_index(one_sided, 0))
                },
            }
        },
        {
            'interior_nonsingleton_interval_uses_one_swap_bit': {
                'interval_kernel_state': serialize_feasible_interval_kernel_state(interior_nonsingleton),
                'choice_count': build_shortest_generator_word_choice_count_for_feasible_interval_state(interior_nonsingleton),
                'choice_index_bit_width': build_shortest_generator_word_choice_index_bit_width_for_feasible_interval_state(interior_nonsingleton),
                'choice_index_to_shortest_word': {
                    str(choice_index): serialize_generator_word(
                        decode_shortest_generator_word_from_choice_index(interior_nonsingleton, choice_index)
                    )
                    for choice_index in range(2)
                },
            }
        },
        {
            'interior_singleton_interval_uses_canonical_first_local_indices': {
                'interval_kernel_state': serialize_feasible_interval_kernel_state(interior_singleton),
                'choice_count': build_shortest_generator_word_choice_count_for_feasible_interval_state(interior_singleton),
                'choice_index_bit_width': build_shortest_generator_word_choice_index_bit_width_for_feasible_interval_state(interior_singleton),
                'canonical_choice_index': encode_shortest_generator_word_as_choice_index(
                    interior_singleton,
                    build_canonical_shortest_generator_word_for_feasible_interval_state(interior_singleton),
                ),
                'sample_choice_index_to_shortest_word': {
                    str(choice_index): serialize_generator_word(
                        decode_shortest_generator_word_from_choice_index(interior_singleton, choice_index)
                    )
                    for choice_index in (0, 1, 11, 12, 17)
                },
            }
        },
    ]


@lru_cache(maxsize=1)
def build_shortest_generator_word_choice_validation_summary() -> dict[str, Any]:
    brute_force = build_shortest_generator_words_by_feasible_interval_state()
    exact_roundtrip_word_count = 0
    exact_roundtrip_index_count = 0
    represented_exact_shortest_word_count = 0
    canonical_choice_is_zero_for_every_state = True
    all_choice_indices_decode_to_closed_form_shortest_words = True
    all_closed_form_shortest_words_encode_to_unique_choice_indices = True

    max_index_spectrum = Counter()
    bit_width_spectrum = Counter()
    choice_count_spectrum = Counter()
    bit_width_by_category: dict[str, Counter[int]] = defaultdict(Counter)
    total_state_local_choice_bits = 0
    total_word_weighted_local_choice_bits = 0

    for state, shortest_words in brute_force.items():
        category = classify_feasible_interval_state(state)
        choice_count = build_shortest_generator_word_choice_count_for_feasible_interval_state(state)
        max_index = build_max_shortest_generator_word_choice_index_for_feasible_interval_state(state)
        bit_width = build_shortest_generator_word_choice_index_bit_width_for_feasible_interval_state(state)
        canonical_word = build_canonical_shortest_generator_word_for_feasible_interval_state(state)
        canonical_choice_index = encode_shortest_generator_word_as_choice_index(state, canonical_word)
        if canonical_choice_index != 0:
            canonical_choice_is_zero_for_every_state = False

        max_index_spectrum[max_index] += 1
        bit_width_spectrum[bit_width] += 1
        choice_count_spectrum[choice_count] += 1
        bit_width_by_category[category][bit_width] += 1
        total_state_local_choice_bits += bit_width
        total_word_weighted_local_choice_bits += len(shortest_words) * bit_width

        seen_choice_indices: set[int] = set()
        decoded_family = []
        for choice_index in range(choice_count):
            decoded_word = decode_shortest_generator_word_from_choice_index(state, choice_index)
            encoded_index = encode_shortest_generator_word_as_choice_index(state, decoded_word)
            if encoded_index != choice_index:
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordChoiceIndexLawError(
                    f'choice index roundtrip mismatch for state {state}: expected {choice_index}, got {encoded_index}'
                )
            decoded_family.append(decoded_word)
            seen_choice_indices.add(choice_index)
            exact_roundtrip_index_count += 1

        if tuple(sorted(decoded_family)) != shortest_words:
            all_choice_indices_decode_to_closed_form_shortest_words = False
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordChoiceIndexLawError(
                f'decoded choice-index family mismatch for state {state}'
            )

        for word in shortest_words:
            encoded_index = encode_shortest_generator_word_as_choice_index(state, word)
            decoded_word = decode_shortest_generator_word_from_choice_index(state, encoded_index)
            if decoded_word != word:
                all_closed_form_shortest_words_encode_to_unique_choice_indices = False
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordChoiceIndexLawError(
                    f'word roundtrip mismatch for state {state}: expected {word}, got {decoded_word}'
                )
            exact_roundtrip_word_count += 1

        if len(seen_choice_indices) != choice_count:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestGeneratorWordChoiceIndexLawError(
                f'each state must use every local choice index exactly once: {state}'
            )
        represented_exact_shortest_word_count += len(shortest_words)

    return {
        'reachable_exact_feasible_interval_kernel_count': len(brute_force),
        'represented_exact_shortest_word_count': represented_exact_shortest_word_count,
        'exact_word_roundtrip_count': exact_roundtrip_word_count,
        'exact_choice_index_roundtrip_count': exact_roundtrip_index_count,
        'maximum_local_choice_index': max(max_index_spectrum),
        'local_choice_count_spectrum': dict(sorted(choice_count_spectrum.items())),
        'maximum_local_choice_index_spectrum': dict(sorted(max_index_spectrum.items())),
        'local_choice_bit_width_spectrum': dict(sorted(bit_width_spectrum.items())),
        'local_choice_bit_width_by_interval_category': {
            category: dict(sorted(counter.items())) for category, counter in sorted(bit_width_by_category.items())
        },
        'canonical_choice_index_is_zero_for_every_state': canonical_choice_is_zero_for_every_state,
        'all_choice_indices_decode_to_closed_form_shortest_words': all_choice_indices_decode_to_closed_form_shortest_words,
        'all_closed_form_shortest_words_encode_to_unique_choice_indices': all_closed_form_shortest_words_encode_to_unique_choice_indices,
        'total_minimal_fixed_width_local_choice_bits_over_states': total_state_local_choice_bits,
        'mean_minimal_fixed_width_local_choice_bits_over_states': total_state_local_choice_bits / len(brute_force),
        'total_minimal_fixed_width_local_choice_bits_over_exact_word_catalog': total_word_weighted_local_choice_bits,
        'mean_minimal_fixed_width_local_choice_bits_over_exact_word_catalog': total_word_weighted_local_choice_bits / represented_exact_shortest_word_count,
        'represented_exact_shortest_word_catalog_is_addressable_without_search': True,
    }


@lru_cache(maxsize=1)
def build_headline_findings() -> dict[str, Any]:
    validation = build_shortest_generator_word_choice_validation_summary()
    return {
        'every_exact_shortest_half_step_generator_word_is_addressable_by_state_local_choice_index': True,
        'maximum_local_choice_index': validation['maximum_local_choice_index'],
        'local_choice_bit_width_spectrum': validation['local_choice_bit_width_spectrum'],
        'canonical_choice_index_is_zero_for_every_state': validation['canonical_choice_index_is_zero_for_every_state'],
        'mean_minimal_fixed_width_local_choice_bits_over_states': validation['mean_minimal_fixed_width_local_choice_bits_over_states'],
        'validation_summary': validation,
    }


@lru_cache(maxsize=1)
def build_decision_rules() -> list[str]:
    return [
        'When the normalized feasible interval state is already known, address any exact shortest generator word by local choice index instead of storing or searching a per-state shortest-word subcatalog.',
        'Use choice index 0 for the canonical shortest word in every state; the earlier canonical shortest-word codec is now the zero-choice branch of a larger exact family codec.',
        'For every interior nonsingleton interval [a,b], one extra bit is enough: choice index 0 means [[a,16],[0,b]] and choice index 1 means the swapped ordering [[0,b],[a,16]].',
        'For every interior singleton [c,c], use choice indices 0..(16-c) for the right-floor fan [[c+i,16],[0,c]] and choice indices (17-c)..17 for the left-cap fan [[0,17-i],[c,16]].',
        'Do not persist explicit shortest-word arrays when the interval state is already stored. The exact local choice payload is bounded by 5 bits on the current path, with only the fifteen interior singleton states needing more than one bit.',
    ]


@lru_cache(maxsize=1)
def build_source_reports() -> list[str]:
    return [
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_family_law_snapshot_20260309.md',
        'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_index_law.py',
    ]


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_index_snapshot() -> dict[str, Any]:
    return {
        'focus': 'Every exact shortest normalized half-step generator word is now addressable by a closed-form local choice index once the interval state is known.',
        'headline_findings': build_headline_findings(),
        'decision_rules': build_decision_rules(),
        'shortest_generator_word_choice_examples': build_shortest_generator_word_choice_examples(),
        'source_reports': build_source_reports(),
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_index_law.py',
    }


def main() -> None:
    print(json.dumps(build_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_index_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
