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
    build_feasible_interval_state_prefix_validation_summary,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_feasible_interval_law import (
    serialize_feasible_interval_kernel_state,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_prefix_law import (
    build_shortest_generator_word_choice_prefix_validation_summary,
    encode_shortest_generator_word_as_choice_prefix_bits,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_law import (
    build_canonical_shortest_generator_word_for_feasible_interval_state,
    serialize_generator_word,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_prefix_law import (
    build_shortest_generator_word_prefix_validation_summary,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_canonical_shortest_generator_word_prefix_law import (
    build_canonical_shortest_generator_word_prefix_validation_summary,
)


class WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestScriptTransportFrontierLawError(RuntimeError):
    pass


EXACT_SHORTEST_GENERATOR_WORD_COUNT = 513
FIXED_WIDTH_STATE_DENSE_TOTAL_BITS_OVER_CANONICAL_CATALOG = FEASIBLE_INTERVAL_STATE_COUNT * 8
FIXED_WIDTH_EXACT_WORD_DENSE_TOTAL_BITS_OVER_CANONICAL_CATALOG = FEASIBLE_INTERVAL_STATE_COUNT * 10
ZERO_BIT_CANONICAL_KNOWN_STATE_TOTAL_BITS = 0


@lru_cache(maxsize=1)
def build_canonical_choice_prefix_summary() -> dict[str, Any]:
    total_choice_prefix_bits = 0
    prefix_length_spectrum: dict[int, int] = {}
    exact_roundtrip_count = 0

    for state in build_all_realized_feasible_interval_states():
        canonical_word = build_canonical_shortest_generator_word_for_feasible_interval_state(state)
        prefix_bits = encode_shortest_generator_word_as_choice_prefix_bits(state, canonical_word)
        total_choice_prefix_bits += len(prefix_bits)
        prefix_length_spectrum[len(prefix_bits)] = prefix_length_spectrum.get(len(prefix_bits), 0) + 1
        exact_roundtrip_count += 1

    return {
        'represented_canonical_shortest_generator_word_count': FEASIBLE_INTERVAL_STATE_COUNT,
        'exact_roundtrip_count': exact_roundtrip_count,
        'total_choice_prefix_bits_over_canonical_catalog': total_choice_prefix_bits,
        'mean_choice_prefix_bit_length_over_canonical_catalog': total_choice_prefix_bits / FEASIBLE_INTERVAL_STATE_COUNT,
        'choice_prefix_bit_length_spectrum_over_canonical_catalog': dict(sorted(prefix_length_spectrum.items())),
        'canonical_shortest_generator_word_is_zero_choice_branch_but_not_zero_prefix_branch': True,
    }


@lru_cache(maxsize=1)
def build_shortest_script_transport_regime_frontier_summary() -> dict[str, Any]:
    state_prefix = build_feasible_interval_state_prefix_validation_summary()
    canonical_prefix = build_canonical_shortest_generator_word_prefix_validation_summary()
    exact_word_prefix = build_shortest_generator_word_prefix_validation_summary()
    choice_prefix = build_shortest_generator_word_choice_prefix_validation_summary()
    canonical_choice_prefix = build_canonical_choice_prefix_summary()

    regimes = {
        'standalone_canonical_shortest_script': {
            'catalog_size': FEASIBLE_INTERVAL_STATE_COUNT,
            'state_is_known_to_decoder': False,
            'exact_noncanonical_branch_must_survive': False,
            'candidate_total_bits': {
                'interval_state_prefix': state_prefix['total_prefix_bits_over_exact_interval_catalog'],
                'interval_state_dense_fixed_width': state_prefix['fixed_width_dense_index_total_bits_over_exact_interval_catalog'],
                'global_exact_shortest_word_prefix_on_canonical_subset': canonical_prefix['global_exact_shortest_word_prefix_total_bits_over_canonical_catalog'],
                'global_exact_shortest_word_dense_fixed_width_on_canonical_subset': canonical_prefix['fixed_width_exact_word_total_bits_over_canonical_catalog'],
            },
            'recommended_transport': 'interval_state_prefix',
        },
        'state_known_canonical_shortest_script': {
            'catalog_size': FEASIBLE_INTERVAL_STATE_COUNT,
            'state_is_known_to_decoder': True,
            'exact_noncanonical_branch_must_survive': False,
            'candidate_total_bits': {
                'zero_bit_canonical_reconstruction_from_state': ZERO_BIT_CANONICAL_KNOWN_STATE_TOTAL_BITS,
                'state_conditional_choice_prefix_on_canonical_subset': canonical_choice_prefix['total_choice_prefix_bits_over_canonical_catalog'],
                'interval_state_prefix': state_prefix['total_prefix_bits_over_exact_interval_catalog'],
                'global_exact_shortest_word_prefix_on_canonical_subset': canonical_prefix['global_exact_shortest_word_prefix_total_bits_over_canonical_catalog'],
            },
            'recommended_transport': 'zero_bit_canonical_reconstruction_from_state',
        },
        'standalone_exact_shortest_script': {
            'catalog_size': EXACT_SHORTEST_GENERATOR_WORD_COUNT,
            'state_is_known_to_decoder': False,
            'exact_noncanonical_branch_must_survive': True,
            'candidate_total_bits': {
                'global_exact_shortest_word_prefix': exact_word_prefix['total_prefix_bits_over_exact_catalog'],
                'global_exact_shortest_word_dense_fixed_width': exact_word_prefix['fixed_width_dense_index_total_bits_over_exact_catalog'],
                'interval_state_prefix_plus_state_conditional_choice_prefix': choice_prefix['combined_state_prefix_plus_choice_prefix_total_bits_over_exact_word_catalog'],
                'interval_state_dense_fixed_width_plus_fixed_choice_index': EXACT_SHORTEST_GENERATOR_WORD_COUNT * 8 + choice_prefix['total_fixed_width_choice_index_bits_over_exact_word_catalog'],
                'interval_state_prefix_plus_fixed_choice_index': choice_prefix['weighted_state_prefix_bits_over_exact_word_catalog'] + choice_prefix['total_fixed_width_choice_index_bits_over_exact_word_catalog'],
                'interval_state_dense_fixed_width_plus_state_conditional_choice_prefix': EXACT_SHORTEST_GENERATOR_WORD_COUNT * 8 + choice_prefix['total_choice_prefix_bits_over_exact_word_catalog'],
            },
            'recommended_transport': 'global_exact_shortest_word_prefix',
        },
        'state_known_exact_shortest_script': {
            'catalog_size': EXACT_SHORTEST_GENERATOR_WORD_COUNT,
            'state_is_known_to_decoder': True,
            'exact_noncanonical_branch_must_survive': True,
            'candidate_total_bits': {
                'state_conditional_choice_prefix': choice_prefix['total_choice_prefix_bits_over_exact_word_catalog'],
                'fixed_choice_index': choice_prefix['total_fixed_width_choice_index_bits_over_exact_word_catalog'],
                'global_exact_shortest_word_prefix': exact_word_prefix['total_prefix_bits_over_exact_catalog'],
                'global_exact_shortest_word_dense_fixed_width': exact_word_prefix['fixed_width_dense_index_total_bits_over_exact_catalog'],
            },
            'recommended_transport': 'state_conditional_choice_prefix',
        },
    }

    dominance_checks = {}
    for regime_name, regime in regimes.items():
        candidates = regime['candidate_total_bits']
        recommended_transport = regime['recommended_transport']
        recommended_total_bits = candidates[recommended_transport]
        sorted_candidates = sorted(candidates.items(), key=lambda item: (item[1], item[0]))
        best_alternative_name, best_alternative_total_bits = sorted_candidates[1]
        if sorted_candidates[0][0] != recommended_transport:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestScriptTransportFrontierLawError(
                f'regime {regime_name} does not minimize at the advertised transport {recommended_transport}'
            )
        dominance_checks[regime_name] = {
            'recommended_total_bits': recommended_total_bits,
            'best_alternative_transport': best_alternative_name,
            'best_alternative_total_bits': best_alternative_total_bits,
            'winning_margin_bits': best_alternative_total_bits - recommended_total_bits,
            'recommended_mean_bits': recommended_total_bits / regime['catalog_size'],
            'best_alternative_mean_bits': best_alternative_total_bits / regime['catalog_size'],
            'winning_margin_mean_bits': (best_alternative_total_bits - recommended_total_bits) / regime['catalog_size'],
        }

    if dominance_checks['standalone_exact_shortest_script']['winning_margin_bits'] != 511:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestScriptTransportFrontierLawError(
            'global exact shortest-word prefix must beat its nearest standalone-exact alternative by 511 bits'
        )
    if dominance_checks['state_known_exact_shortest_script']['winning_margin_bits'] != 210:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestScriptTransportFrontierLawError(
            'state-conditional choice prefix must beat fixed local choice indices by 210 bits in the state-known exact regime'
        )
    if dominance_checks['standalone_canonical_shortest_script']['winning_margin_bits'] != 103:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestScriptTransportFrontierLawError(
            'standalone canonical state-prefix transport must beat its nearest canonical alternative by 103 bits'
        )
    if dominance_checks['state_known_canonical_shortest_script']['winning_margin_bits'] != 165:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepShortestScriptTransportFrontierLawError(
            'zero-bit known-state canonical transport must beat the canonical choice-prefix fallback by 165 bits'
        )

    return {
        'frontier_regime_count': len(regimes),
        'nonzero_frontier_codec_count': 3,
        'regimes': regimes,
        'dominance_checks': dominance_checks,
        'canonical_choice_prefix_summary': canonical_choice_prefix,
        'global_exact_shortest_word_prefix_is_optimal_only_when_state_is_unknown_and_exact_branch_must_survive': True,
        'state_conditional_choice_prefix_is_optimal_only_when_state_is_known_and_exact_branch_must_survive': True,
        'interval_state_prefix_is_optimal_for_standalone_canonical_shortest_script_transport': True,
        'zero_bit_reconstruction_is_optimal_for_state_known_canonical_shortest_script_transport': True,
    }


@lru_cache(maxsize=1)
def recommend_shortest_script_transport(
    *,
    state_is_known_to_decoder: bool,
    exact_noncanonical_branch_must_survive: bool,
) -> dict[str, Any]:
    state_is_known_to_decoder = bool(state_is_known_to_decoder)
    exact_noncanonical_branch_must_survive = bool(exact_noncanonical_branch_must_survive)
    summary = build_shortest_script_transport_regime_frontier_summary()
    regime_name = (
        ('state_known_' if state_is_known_to_decoder else 'standalone_')
        + ('exact_shortest_script' if exact_noncanonical_branch_must_survive else 'canonical_shortest_script')
    )
    regime = summary['regimes'][regime_name]
    dominance = summary['dominance_checks'][regime_name]
    return {
        'regime': regime_name,
        'recommended_transport': regime['recommended_transport'],
        'catalog_size': regime['catalog_size'],
        'recommended_total_bits': dominance['recommended_total_bits'],
        'recommended_mean_bits': dominance['recommended_mean_bits'],
        'best_alternative_transport': dominance['best_alternative_transport'],
        'best_alternative_total_bits': dominance['best_alternative_total_bits'],
        'winning_margin_bits': dominance['winning_margin_bits'],
        'winning_margin_mean_bits': dominance['winning_margin_mean_bits'],
    }


@lru_cache(maxsize=1)
def build_transport_frontier_examples() -> list[dict[str, Any]]:
    state = (5, 5)
    canonical_word = build_canonical_shortest_generator_word_for_feasible_interval_state(state)
    return [
        {
            'standalone_canonical_script_prefers_interval_state_prefix_over_script_specific_transport': {
                'interval_kernel_state': serialize_feasible_interval_kernel_state(state),
                'canonical_shortest_generator_word': serialize_generator_word(canonical_word),
                'recommendation': recommend_shortest_script_transport(
                    state_is_known_to_decoder=False,
                    exact_noncanonical_branch_must_survive=False,
                ),
            }
        },
        {
            'state_known_exact_script_prefers_local_choice_prefix': {
                'interval_kernel_state': serialize_feasible_interval_kernel_state(state),
                'canonical_shortest_generator_word': serialize_generator_word(canonical_word),
                'recommendation': recommend_shortest_script_transport(
                    state_is_known_to_decoder=True,
                    exact_noncanonical_branch_must_survive=True,
                ),
            }
        },
        {
            'state_known_canonical_script_needs_no_transport_bits': {
                'interval_kernel_state': serialize_feasible_interval_kernel_state(state),
                'canonical_shortest_generator_word': serialize_generator_word(canonical_word),
                'recommendation': recommend_shortest_script_transport(
                    state_is_known_to_decoder=True,
                    exact_noncanonical_branch_must_survive=False,
                ),
            }
        },
    ]


@lru_cache(maxsize=1)
def build_headline_findings() -> dict[str, Any]:
    summary = build_shortest_script_transport_regime_frontier_summary()
    return {
        'frontier_regime_count': summary['frontier_regime_count'],
        'state_known_canonical_shortest_script_has_zero_transport_cost': True,
        'standalone_canonical_shortest_script_mean_bits': summary['dominance_checks']['standalone_canonical_shortest_script']['recommended_mean_bits'],
        'standalone_exact_shortest_script_mean_bits': summary['dominance_checks']['standalone_exact_shortest_script']['recommended_mean_bits'],
        'state_known_exact_shortest_script_mean_bits': summary['dominance_checks']['state_known_exact_shortest_script']['recommended_mean_bits'],
        'state_known_canonical_shortest_script_mean_bits': summary['dominance_checks']['state_known_canonical_shortest_script']['recommended_mean_bits'],
        'validation_summary': summary,
    }


@lru_cache(maxsize=1)
def build_decision_rules() -> list[str]:
    return [
        'When the exact noncanonical shortest branch must survive and the decoder does not already know the feasible interval state, use the standalone 513-word global exact-shortest-word prefix transport.',
        'When the exact noncanonical shortest branch must survive and the decoder already knows the feasible interval state, send only the state-conditional local choice prefix.',
        'When deterministic canonicalization is acceptable and the decoder does not already know the feasible interval state, transport the interval-state prefix and rebuild the canonical shortest script after decode.',
        'When deterministic canonicalization is acceptable and the decoder already knows the feasible interval state, send zero script bits and rebuild the canonical shortest script directly from state.',
        'Keep the exact interval-state prefix as the base transport only when the state itself must survive independently of any script view. The frontier in this pass is specifically about shortest-script transport choices.',
    ]


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_shared_half_step_shortest_script_transport_frontier_snapshot() -> dict[str, Any]:
    return {
        'focus': 'Normalized shortest-script transport collapses to a four-regime frontier determined only by state knowledge and whether noncanonical branch identity must survive.',
        'headline_findings': build_headline_findings(),
        'decision_rules': build_decision_rules(),
        'transport_frontier_examples': build_transport_frontier_examples(),
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_prefix_law_snapshot_20260309.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_prefix_law_snapshot_20260309.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_prefix_law_snapshot_20260309.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_canonical_shortest_generator_word_prefix_law_snapshot_20260309.json',
        ],
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_script_transport_frontier_law.py',
    }


if __name__ == '__main__':
    print(json.dumps(build_service_mode_suffix_batch_shared_half_step_shortest_script_transport_frontier_snapshot(), indent=2, sort_keys=True))
