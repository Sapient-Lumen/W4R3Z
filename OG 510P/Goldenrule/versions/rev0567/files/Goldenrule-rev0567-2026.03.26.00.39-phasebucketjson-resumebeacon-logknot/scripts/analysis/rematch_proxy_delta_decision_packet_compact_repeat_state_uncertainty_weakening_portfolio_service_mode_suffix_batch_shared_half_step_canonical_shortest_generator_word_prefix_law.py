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
    FEASIBLE_INTERVAL_STATE_COUNT,
    build_all_realized_feasible_interval_states,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_prefix_law import (
    decode_feasible_interval_state_from_prefix_bits,
    encode_feasible_interval_state_as_prefix_bits,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_feasible_interval_law import (
    serialize_feasible_interval_kernel_state,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_law import (
    GeneratorWord,
    build_canonical_shortest_generator_word_for_feasible_interval_state,
    decode_shortest_generator_word_to_feasible_interval_state,
    serialize_generator_word,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_prefix_law import (
    PREFIX_SHORT_BIT_LENGTH as EXACT_WORD_PREFIX_SHORT_BIT_LENGTH,
    encode_shortest_generator_word_as_prefix_bits,
)


class WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepCanonicalShortestGeneratorWordPrefixLawError(RuntimeError):
    pass


CANONICAL_SHORTEST_GENERATOR_WORD_COUNT = FEASIBLE_INTERVAL_STATE_COUNT
FIXED_WIDTH_EXACT_WORD_BIT_LENGTH = 10
FIXED_WIDTH_STATE_DENSE_INDEX_BIT_LENGTH = 8


@lru_cache(maxsize=1)
def build_canonical_shortest_generator_word_catalog() -> tuple[tuple[tuple[int, int], GeneratorWord], ...]:
    return tuple(
        (state, build_canonical_shortest_generator_word_for_feasible_interval_state(state))
        for state in build_all_realized_feasible_interval_states()
    )


@lru_cache(maxsize=None)
def encode_canonical_shortest_generator_word_as_prefix_bits(generator_word: GeneratorWord) -> str:
    state = decode_shortest_generator_word_to_feasible_interval_state(generator_word)
    canonical_word = build_canonical_shortest_generator_word_for_feasible_interval_state(state)
    if generator_word != canonical_word:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepCanonicalShortestGeneratorWordPrefixLawError(
            'canonical shortest-word prefix transport only accepts the deterministic canonical shortest generator word for its state'
        )
    return encode_feasible_interval_state_as_prefix_bits(state)


@lru_cache(maxsize=None)
def decode_canonical_shortest_generator_word_from_prefix_bits(
    bitstream: str,
    start_offset: int = 0,
) -> tuple[GeneratorWord, int]:
    state, bits_consumed = decode_feasible_interval_state_from_prefix_bits(bitstream, start_offset)
    return build_canonical_shortest_generator_word_for_feasible_interval_state(state), bits_consumed


@lru_cache(maxsize=1)
def build_canonical_shortest_generator_word_prefix_examples() -> list[dict[str, Any]]:
    example_states = ((0, 16), (4, 16), (0, 11), (3, 8), (5, 5))
    examples: list[dict[str, Any]] = []
    for state in example_states:
        canonical_word = build_canonical_shortest_generator_word_for_feasible_interval_state(state)
        prefix_bits = encode_canonical_shortest_generator_word_as_prefix_bits(canonical_word)
        examples.append(
            {
                'canonical_shortest_generator_word_prefix_example': {
                    'interval_kernel_state': serialize_feasible_interval_kernel_state(state),
                    'canonical_shortest_generator_word': serialize_generator_word(canonical_word),
                    'prefix_bits': prefix_bits,
                    'prefix_bit_length': len(prefix_bits),
                }
            }
        )
    return examples


@lru_cache(maxsize=1)
def build_canonical_shortest_generator_word_prefix_validation_summary() -> dict[str, Any]:
    prefix_catalog: dict[GeneratorWord, str] = {}
    exact_word_roundtrip_count = 0
    exact_state_roundtrip_count = 0
    exact_sequential_stream_roundtrip_count = 0
    total_prefix_bits = 0
    total_global_exact_word_prefix_bits = 0

    concatenated_stream_parts: list[str] = []
    canonical_word_sequence: list[GeneratorWord] = []

    for state, canonical_word in build_canonical_shortest_generator_word_catalog():
        prefix_bits = encode_canonical_shortest_generator_word_as_prefix_bits(canonical_word)
        decoded_word, consumed_bits = decode_canonical_shortest_generator_word_from_prefix_bits(prefix_bits)
        if decoded_word != canonical_word:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepCanonicalShortestGeneratorWordPrefixLawError(
                f'canonical shortest-word prefix roundtrip mismatch for state {state}'
            )
        if consumed_bits != len(prefix_bits):
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepCanonicalShortestGeneratorWordPrefixLawError(
                f'canonical shortest-word prefix decode must consume the full code for state {state}'
            )
        exact_word_roundtrip_count += 1

        decoded_state = decode_shortest_generator_word_to_feasible_interval_state(decoded_word)
        if decoded_state != state:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepCanonicalShortestGeneratorWordPrefixLawError(
                f'canonical shortest-word prefix decode must preserve feasible interval state for state {state}'
            )
        exact_state_roundtrip_count += 1

        prefix_catalog[canonical_word] = prefix_bits
        concatenated_stream_parts.append(prefix_bits)
        canonical_word_sequence.append(canonical_word)
        total_prefix_bits += len(prefix_bits)
        total_global_exact_word_prefix_bits += len(encode_shortest_generator_word_as_prefix_bits(canonical_word))

    prefix_free_catalog = True
    canonical_words = tuple(prefix_catalog)
    for left_word in canonical_words:
        left_bits = prefix_catalog[left_word]
        for right_word in canonical_words:
            if left_word == right_word:
                continue
            if prefix_catalog[right_word].startswith(left_bits):
                prefix_free_catalog = False
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepCanonicalShortestGeneratorWordPrefixLawError(
                    f'prefix collision: canonical word {serialize_generator_word(left_word)} prefixes canonical word {serialize_generator_word(right_word)}'
                )

    concatenated_stream = ''.join(concatenated_stream_parts)
    cursor = 0
    for canonical_word in canonical_word_sequence:
        decoded_word, consumed_bits = decode_canonical_shortest_generator_word_from_prefix_bits(concatenated_stream, cursor)
        if decoded_word != canonical_word:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepCanonicalShortestGeneratorWordPrefixLawError(
                f'sequential canonical-word stream decode mismatch at bit cursor {cursor}'
            )
        cursor += consumed_bits
        exact_sequential_stream_roundtrip_count += 1
    if cursor != len(concatenated_stream):
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepCanonicalShortestGeneratorWordPrefixLawError(
            'sequential canonical shortest-word prefix decode must consume the full concatenated stream exactly'
        )

    fixed_width_exact_word_total_bits = CANONICAL_SHORTEST_GENERATOR_WORD_COUNT * FIXED_WIDTH_EXACT_WORD_BIT_LENGTH
    fixed_width_state_dense_total_bits = CANONICAL_SHORTEST_GENERATOR_WORD_COUNT * FIXED_WIDTH_STATE_DENSE_INDEX_BIT_LENGTH
    saved_bits_vs_global_exact_word_prefix = total_global_exact_word_prefix_bits - total_prefix_bits
    saved_bits_vs_fixed_width_exact_word = fixed_width_exact_word_total_bits - total_prefix_bits
    saved_bits_vs_fixed_width_state_dense = fixed_width_state_dense_total_bits - total_prefix_bits

    return {
        'represented_canonical_shortest_generator_word_count': CANONICAL_SHORTEST_GENERATOR_WORD_COUNT,
        'exact_prefix_word_roundtrip_count': exact_word_roundtrip_count,
        'exact_prefix_state_roundtrip_count': exact_state_roundtrip_count,
        'exact_prefix_sequential_stream_roundtrip_count': exact_sequential_stream_roundtrip_count,
        'prefix_catalog_is_prefix_free': prefix_free_catalog,
        'total_prefix_bits_over_canonical_catalog': total_prefix_bits,
        'global_exact_shortest_word_prefix_total_bits_over_canonical_catalog': total_global_exact_word_prefix_bits,
        'fixed_width_exact_word_total_bits_over_canonical_catalog': fixed_width_exact_word_total_bits,
        'fixed_width_state_dense_total_bits_over_canonical_catalog': fixed_width_state_dense_total_bits,
        'saved_bits_vs_global_exact_word_prefix': saved_bits_vs_global_exact_word_prefix,
        'saved_bits_share_vs_global_exact_word_prefix': saved_bits_vs_global_exact_word_prefix / total_global_exact_word_prefix_bits,
        'saved_bits_vs_fixed_width_exact_word': saved_bits_vs_fixed_width_exact_word,
        'saved_bits_share_vs_fixed_width_exact_word': saved_bits_vs_fixed_width_exact_word / fixed_width_exact_word_total_bits,
        'saved_bits_vs_fixed_width_state_dense': saved_bits_vs_fixed_width_state_dense,
        'saved_bits_share_vs_fixed_width_state_dense': saved_bits_vs_fixed_width_state_dense / fixed_width_state_dense_total_bits,
        'mean_prefix_bit_length': total_prefix_bits / CANONICAL_SHORTEST_GENERATOR_WORD_COUNT,
        'mean_bit_savings_vs_global_exact_word_prefix': saved_bits_vs_global_exact_word_prefix / CANONICAL_SHORTEST_GENERATOR_WORD_COUNT,
        'mean_bit_savings_vs_fixed_width_exact_word': saved_bits_vs_fixed_width_exact_word / CANONICAL_SHORTEST_GENERATOR_WORD_COUNT,
        'mean_bit_savings_vs_fixed_width_state_dense': saved_bits_vs_fixed_width_state_dense / CANONICAL_SHORTEST_GENERATOR_WORD_COUNT,
        'exact_uniform_entropy_lower_bound_bits': math.log2(CANONICAL_SHORTEST_GENERATOR_WORD_COUNT),
        'global_exact_word_prefix_short_bit_length_on_canonical_subset': EXACT_WORD_PREFIX_SHORT_BIT_LENGTH,
        'every_canonical_shortest_generator_word_uses_nine_bits_under_the_global_exact_word_prefix': True,
        'canonical_shortest_generator_word_prefix_is_exactly_the_existing_interval_state_prefix_codec': True,
        'canonical_shortest_generator_word_prefix_requires_no_extra_script_only_block_beyond_interval_state_decode': True,
    }


@lru_cache(maxsize=1)
def build_headline_findings() -> dict[str, Any]:
    validation = build_canonical_shortest_generator_word_prefix_validation_summary()
    return {
        'standalone_canonical_shortest_script_transport_collapses_exactly_to_existing_interval_state_prefix_transport': True,
        'mean_prefix_bit_length': validation['mean_prefix_bit_length'],
        'mean_bit_savings_vs_global_exact_word_prefix': validation['mean_bit_savings_vs_global_exact_word_prefix'],
        'saved_bits_vs_global_exact_word_prefix': validation['saved_bits_vs_global_exact_word_prefix'],
        'validation_summary': validation,
    }


@lru_cache(maxsize=1)
def build_decision_rules() -> list[str]:
    return [
        'When standalone transport only needs one deterministic shortest script per exact normalized interval state, do not use the larger 513-word exact-script prefix catalog; encode the canonical shortest generator word by first recovering its interval state and then writing the existing interval-state prefix directly.',
        'Encode canonical shortest generator words by reusing the exact interval-state prefix codec unchanged: identity and all canonical one- or two-generator representatives inherit the same 103 seven-bit and 50 eight-bit leaves already validated for interval states.',
        'Decode by reading the interval-state prefix first, then rebuild the canonical shortest generator word from the decoded feasible interval [a,b] using the earlier shortest-word law; no extra script-only dense index or lookup table is required.',
        'Use this codec only when deterministic canonicalization is acceptable. If the exact noncanonical shortest word itself must survive, keep using the broader 513-word global exact-script prefix or the state-known local-choice path instead.',
        'Keep the older global exact-word prefix when a downstream consumer needs the precise shortest-word branch. This new pass is specifically the cheaper standalone transport for the canonical representative only.',
    ]


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_shared_half_step_canonical_shortest_generator_word_prefix_snapshot() -> dict[str, Any]:
    return {
        'focus': 'Standalone transport of deterministic canonical shortest half-step generator words collapses exactly to the existing interval-state prefix codec.',
        'headline_findings': build_headline_findings(),
        'decision_rules': build_decision_rules(),
        'canonical_shortest_generator_word_prefix_examples': build_canonical_shortest_generator_word_prefix_examples(),
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_prefix_law_snapshot_20260309.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_law_snapshot_20260309.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_prefix_law_snapshot_20260309.json',
        ],
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_canonical_shortest_generator_word_prefix_law.py',
    }


if __name__ == '__main__':
    print(json.dumps(build_service_mode_suffix_batch_shared_half_step_canonical_shortest_generator_word_prefix_snapshot(), indent=2, sort_keys=True))
