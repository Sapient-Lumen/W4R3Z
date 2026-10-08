#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from functools import lru_cache
from itertools import product
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
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_feasible_interval_law import (
    FeasibleIntervalKernelState,
    serialize_feasible_interval_kernel_state,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_index_law import (
    encode_shortest_generator_word_as_choice_index,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_prefix_law import (
    encode_shortest_generator_word_as_choice_prefix_bits,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_family_law import (
    build_closed_form_shortest_generator_words_for_feasible_interval_state,
    build_shortest_generator_word_family_cardinality_for_feasible_interval_state,
    classify_feasible_interval_state,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_prefix_law import (
    encode_shortest_generator_word_as_prefix_bits,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_script_transport_frontier_law import (
    recommend_shortest_script_transport,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_law import (
    GeneratorWord,
    serialize_generator_word,
)


class WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateExactShortestScriptTransportLawError(RuntimeError):
    pass


@lru_cache(maxsize=None)
def _normalize_feasible_interval_state(
    state: tuple[int, int] | list[int],
) -> FeasibleIntervalKernelState:
    if len(state) != 2:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateExactShortestScriptTransportLawError(
            'feasible interval state must contain exactly two ranks'
        )
    lower_rank = int(state[0])
    upper_rank = int(state[1])
    if lower_rank < 0 or upper_rank < lower_rank or upper_rank > 16:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateExactShortestScriptTransportLawError(
            'feasible interval state must stay within the realized 17-rank path bounds'
        )
    return lower_rank, upper_rank


@lru_cache(maxsize=None)
def encode_shared_interval_state_exact_shortest_script_batch_as_state_prefix_plus_choice_prefixes(
    state: tuple[int, int] | list[int],
    generator_word_batch: tuple[GeneratorWord, ...],
) -> str:
    state = _normalize_feasible_interval_state(state)
    state_bits = encode_feasible_interval_state_dense_index_as_prefix_bits(
        encode_feasible_interval_state_as_dense_index(state)
    )
    choice_bits = ''.join(
        encode_shortest_generator_word_as_choice_prefix_bits(state, word)
        for word in generator_word_batch
    )
    return state_bits + choice_bits


@lru_cache(maxsize=None)
def encode_exact_shortest_script_batch_as_global_exact_word_prefixes(
    generator_word_batch: tuple[GeneratorWord, ...],
) -> str:
    return ''.join(encode_shortest_generator_word_as_prefix_bits(word) for word in generator_word_batch)


@lru_cache(maxsize=None)
def summarize_shared_interval_state_exact_shortest_script_batch(
    state: tuple[int, int] | list[int],
    generator_word_batch: tuple[GeneratorWord, ...],
) -> dict[str, Any]:
    state = _normalize_feasible_interval_state(state)
    family = build_closed_form_shortest_generator_words_for_feasible_interval_state(state)
    family_set = set(family)
    if not generator_word_batch:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateExactShortestScriptTransportLawError(
            'shared-state exact shortest-script batches must contain at least one word'
        )
    if any(word not in family_set for word in generator_word_batch):
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateExactShortestScriptTransportLawError(
            f'every batch word must belong to the shortest-word family for state {state}'
        )

    shared_state_bits = encode_shared_interval_state_exact_shortest_script_batch_as_state_prefix_plus_choice_prefixes(state, generator_word_batch)
    global_bits = encode_exact_shortest_script_batch_as_global_exact_word_prefixes(generator_word_batch)
    shared_state_length = len(shared_state_bits)
    global_length = len(global_bits)
    if shared_state_length < global_length:
        status = 'strict_win'
    elif shared_state_length == global_length:
        status = 'tie'
    else:
        status = 'loss'

    return {
        'interval_kernel_state': serialize_feasible_interval_kernel_state(state),
        'batch_length': len(generator_word_batch),
        'family_cardinality': len(family),
        'batch_local_choice_indices': [
            encode_shortest_generator_word_as_choice_index(state, word)
            for word in generator_word_batch
        ],
        'batch_generator_words': [serialize_generator_word(word) for word in generator_word_batch],
        'shared_state_transport_bit_length': shared_state_length,
        'global_exact_word_transport_bit_length': global_length,
        'winning_margin_bits': global_length - shared_state_length,
        'comparison_status': status,
    }


@lru_cache(maxsize=1)
def build_shared_interval_state_exact_shortest_script_transport_validation_summary() -> dict[str, Any]:
    comparison_counts_by_batch_length: dict[int, Counter[str]] = defaultdict(Counter)
    exact_case_count_by_batch_length: Counter[int] = Counter()
    strict_dominance_threshold_counter: Counter[int] = Counter()
    state_category_threshold_counter: Counter[str] = Counter()
    tie_state_counter_by_batch_length: dict[int, Counter[str]] = defaultdict(Counter)
    tie_choice_pattern_counter_by_batch_length: dict[int, Counter[str]] = defaultdict(Counter)

    strict_win_example = None
    tie_example = None
    loss_example = None

    max_strict_dominance_threshold = 0

    for state in build_all_realized_feasible_interval_states():
        family = build_closed_form_shortest_generator_words_for_feasible_interval_state(state)
        state_prefix_bit_length = len(
            encode_feasible_interval_state_dense_index_as_prefix_bits(
                encode_feasible_interval_state_as_dense_index(state)
            )
        )
        family_cardinality = build_shortest_generator_word_family_cardinality_for_feasible_interval_state(state)
        category = classify_feasible_interval_state(state)

        strict_threshold_for_state = None
        for batch_length in (1, 2, 3):
            all_strict = True
            for generator_word_batch in product(family, repeat=batch_length):
                summary = summarize_shared_interval_state_exact_shortest_script_batch(state, generator_word_batch)
                status = summary['comparison_status']
                comparison_counts_by_batch_length[batch_length][status] += 1
                exact_case_count_by_batch_length[batch_length] += 1
                if status != 'strict_win':
                    all_strict = False
                if status == 'tie':
                    tie_state_counter_by_batch_length[batch_length][f'{state[0]}-{state[1]}'] += 1
                    choice_pattern = '/'.join(str(choice_index) for choice_index in summary['batch_local_choice_indices'])
                    tie_choice_pattern_counter_by_batch_length[batch_length][choice_pattern] += 1
                    if tie_example is None:
                        tie_example = summary
                elif status == 'loss' and loss_example is None:
                    loss_example = summary
                elif status == 'strict_win' and strict_win_example is None:
                    strict_win_example = summary
            if all_strict and strict_threshold_for_state is None:
                strict_threshold_for_state = batch_length
        if strict_threshold_for_state is None:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateExactShortestScriptTransportLawError(
                f'state {state} failed to reach strict shared-state dominance by batch length 3'
            )
        strict_dominance_threshold_counter[strict_threshold_for_state] += 1
        state_category_threshold_counter[f'{category}|state_prefix_bits={state_prefix_bit_length}|family_cardinality={family_cardinality}|strict_threshold={strict_threshold_for_state}'] += 1
        max_strict_dominance_threshold = max(max_strict_dominance_threshold, strict_threshold_for_state)

    if comparison_counts_by_batch_length[1] != Counter({'loss': 270, 'strict_win': 179, 'tie': 64}):
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateExactShortestScriptTransportLawError(
            f'unexpected batch-length-1 comparison counts: {comparison_counts_by_batch_length[1]}'
        )
    if comparison_counts_by_batch_length[2] != Counter({'strict_win': 5197, 'tie': 116}):
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateExactShortestScriptTransportLawError(
            f'unexpected batch-length-2 comparison counts: {comparison_counts_by_batch_length[2]}'
        )
    if comparison_counts_by_batch_length[3] != Counter({'strict_win': 88353}):
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateExactShortestScriptTransportLawError(
            f'unexpected batch-length-3 comparison counts: {comparison_counts_by_batch_length[3]}'
        )
    if strict_dominance_threshold_counter != Counter({1: 106, 2: 39, 3: 8}):
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateExactShortestScriptTransportLawError(
            f'unexpected strict-dominance thresholds: {strict_dominance_threshold_counter}'
        )
    if max_strict_dominance_threshold != 3:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateExactShortestScriptTransportLawError(
            'shared-state exact shortest-script transport should become strictly dominant by batch length 3 on the current path'
        )
    if sum(exact_case_count_by_batch_length.values()) != 94179:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateExactShortestScriptTransportLawError(
            'unexpected total audited shared-state exact shortest-script batch count'
        )

    return {
        'audited_batch_lengths': [1, 2, 3],
        'exact_case_count_by_batch_length': dict(sorted(exact_case_count_by_batch_length.items())),
        'total_exact_case_count': sum(exact_case_count_by_batch_length.values()),
        'comparison_counts_by_batch_length': {
            str(batch_length): dict(sorted(counter.items()))
            for batch_length, counter in sorted(comparison_counts_by_batch_length.items())
        },
        'strict_dominance_threshold_counter': {str(key): value for key, value in sorted(strict_dominance_threshold_counter.items())},
        'max_strict_dominance_threshold': max_strict_dominance_threshold,
        'state_category_threshold_counter': dict(sorted(state_category_threshold_counter.items())),
        'tie_state_counter_by_batch_length': {
            str(batch_length): dict(sorted(counter.items()))
            for batch_length, counter in sorted(tie_state_counter_by_batch_length.items())
        },
        'tie_choice_pattern_counter_by_batch_length': {
            str(batch_length): dict(sorted(counter.items()))
            for batch_length, counter in sorted(tie_choice_pattern_counter_by_batch_length.items())
        },
        'strict_win_example': strict_win_example,
        'tie_example': tie_example,
        'loss_example': loss_example,
        'shared_state_transport_never_loses_at_batch_length_2': comparison_counts_by_batch_length[2].get('loss', 0) == 0,
        'shared_state_transport_is_strictly_dominant_for_every_audited_case_at_batch_length_3': comparison_counts_by_batch_length[3] == Counter({'strict_win': exact_case_count_by_batch_length[3]}),
        'single_word_exact_transport_should_still_defer_to_the_frontier_law': comparison_counts_by_batch_length[1].get('loss', 0) > 0,
    }


@lru_cache(maxsize=None)
def recommend_shared_interval_state_exact_shortest_script_transport(
    state: tuple[int, int] | list[int],
    batch_length: int,
) -> dict[str, Any]:
    state = _normalize_feasible_interval_state(state)
    batch_length = int(batch_length)
    if batch_length <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateExactShortestScriptTransportLawError(
            'batch length must be positive'
        )

    family_cardinality = build_shortest_generator_word_family_cardinality_for_feasible_interval_state(state)
    state_prefix_bit_length = len(
        encode_feasible_interval_state_dense_index_as_prefix_bits(
            encode_feasible_interval_state_as_dense_index(state)
        )
    )
    category = classify_feasible_interval_state(state)

    if batch_length >= 3:
        recommendation = 'shared_interval_state_prefix_plus_local_choice_prefixes'
        guarantee = 'strict_win'
        rationale = 'Every audited shared-state exact batch of length at least three strictly favored state-once transport over per-word global exact prefixes.'
    elif batch_length == 2:
        recommendation = 'shared_interval_state_prefix_plus_local_choice_prefixes'
        guarantee = 'weak_win'
        rationale = 'Every audited shared-state exact batch of length two was either a strict win or a tie for state-once transport; there were no losses.'
    else:
        if family_cardinality == 1:
            recommendation = 'shared_interval_state_prefix_plus_local_choice_prefixes'
            guarantee = 'strict_win'
            rationale = 'This state has a unique shortest script, so sending the interval state alone is already enough and is shorter than the global exact-word prefix.'
        elif category == 'interior_nonsingleton' and state_prefix_bit_length == 7:
            recommendation = 'shared_interval_state_prefix_plus_local_choice_prefixes'
            guarantee = 'strict_win'
            rationale = 'This 7-bit interior nonsingleton state pays only one local choice bit, so the state-once path costs 8 bits against the 9-bit global exact word.'
        elif category == 'interior_nonsingleton' and state_prefix_bit_length == 8:
            recommendation = 'either_tie'
            guarantee = 'tie'
            rationale = 'This 8-bit interior nonsingleton state ties the global exact-word prefix at one word: 8 bits of state plus 1 choice bit versus one 9-bit global exact word.'
        else:
            frontier = recommend_shortest_script_transport(
                state_is_known_to_decoder=False,
                exact_noncanonical_branch_must_survive=True,
            )
            recommendation = frontier['recommended_transport']
            guarantee = 'strict_loss_for_shared_state_path'
            rationale = 'Interior singleton one-word exact transport still favors the standalone global exact-word prefix; shared-state amortization has not started yet.'

    return {
        'interval_kernel_state': serialize_feasible_interval_kernel_state(state),
        'batch_length': batch_length,
        'state_category': category,
        'family_cardinality': family_cardinality,
        'state_prefix_bit_length': state_prefix_bit_length,
        'recommendation': recommendation,
        'guarantee': guarantee,
        'rationale': rationale,
    }


@lru_cache(maxsize=1)
def build_shared_interval_state_exact_shortest_script_transport_examples() -> list[dict[str, Any]]:
    strict_win_state = (0, 16)
    tie_state = (8, 8)
    loss_state = (1, 1)

    unique_word = build_closed_form_shortest_generator_words_for_feasible_interval_state(strict_win_state)[0]
    tie_family = build_closed_form_shortest_generator_words_for_feasible_interval_state(tie_state)
    loss_family = build_closed_form_shortest_generator_words_for_feasible_interval_state(loss_state)

    return [
        {
            'unique_state_already_prefers_state_once_transport_for_one_exact_word': summarize_shared_interval_state_exact_shortest_script_batch(
                strict_win_state,
                (unique_word,),
            )
        },
        {
            'eight_bit_interior_singleton_can_tie_at_two_words_before_strict_dominance_kicks_in': summarize_shared_interval_state_exact_shortest_script_batch(
                tie_state,
                (tie_family[0], tie_family[1]),
            )
        },
        {
            'the_same_eight_bit_interior_singleton_becomes_a_strict_win_by_three_words': summarize_shared_interval_state_exact_shortest_script_batch(
                tie_state,
                (tie_family[0], tie_family[1], tie_family[2]),
            )
        },
        {
            'interior_singleton_one_word_should_still_use_the_frontier_law': summarize_shared_interval_state_exact_shortest_script_batch(
                loss_state,
                (loss_family[0],),
            )
        },
    ]


@lru_cache(maxsize=1)
def build_headline_findings() -> dict[str, Any]:
    summary = build_shared_interval_state_exact_shortest_script_transport_validation_summary()
    return {
        'audited_batch_lengths': summary['audited_batch_lengths'],
        'total_exact_case_count': summary['total_exact_case_count'],
        'shared_state_transport_never_loses_at_batch_length_2': summary['shared_state_transport_never_loses_at_batch_length_2'],
        'shared_state_transport_is_strictly_dominant_for_every_audited_case_at_batch_length_3': summary['shared_state_transport_is_strictly_dominant_for_every_audited_case_at_batch_length_3'],
        'strict_dominance_threshold_counter': summary['strict_dominance_threshold_counter'],
        'comparison_counts_by_batch_length': summary['comparison_counts_by_batch_length'],
    }


@lru_cache(maxsize=1)
def build_decision_rules() -> list[str]:
    return [
        'When all exact shortest scripts in a batch share one feasible interval state and the batch length is at least three, send the interval-state prefix once and then send only state-conditional local choice prefixes for each exact script.',
        'When all exact shortest scripts in a batch share one feasible interval state and the batch length is two, the same state-once path is never worse than per-word global exact-word prefixes; ties survive only in a narrow eight-bit interior-singleton corner.',
        'When the shared-state exact batch length is one, keep using the earlier shortest-script frontier as the default rule. The state-once path wins immediately only for unique-word states and seven-bit interior nonsingleton states, ties for eight-bit interior nonsingletons, and loses for interior singletons.',
        'Treat this pass as an amortization law, not a replacement for the standalone exact-word frontier. The new guarantee starts only after the encoder can prove that every exact script in the batch shares one feasible interval state.',
    ]


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_shared_half_step_shared_interval_state_exact_shortest_script_transport_snapshot() -> dict[str, Any]:
    return {
        'focus': 'Once exact shortest scripts share one feasible interval state, state-once transport with local choice prefixes quickly dominates standalone global exact-word prefixes.',
        'headline_findings': build_headline_findings(),
        'decision_rules': build_decision_rules(),
        'shared_state_transport_examples': build_shared_interval_state_exact_shortest_script_transport_examples(),
        'validation_summary': build_shared_interval_state_exact_shortest_script_transport_validation_summary(),
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_prefix_law_snapshot_20260309.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_prefix_law_snapshot_20260309.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_prefix_law_snapshot_20260309.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_script_transport_frontier_law_snapshot_20260309.json',
        ],
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_exact_shortest_script_transport_law.py',
    }


if __name__ == '__main__':
    print(json.dumps(build_service_mode_suffix_batch_shared_half_step_shared_interval_state_exact_shortest_script_transport_snapshot(), indent=2, sort_keys=True))
