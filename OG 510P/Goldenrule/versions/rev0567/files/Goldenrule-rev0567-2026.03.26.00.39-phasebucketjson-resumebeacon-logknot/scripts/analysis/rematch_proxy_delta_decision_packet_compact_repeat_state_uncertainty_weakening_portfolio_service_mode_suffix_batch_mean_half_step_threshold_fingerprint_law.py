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

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_selector_index_law import (
    build_max_half_step_selector_index,
    build_max_rank,
    build_width_one_fingerprint,
    decode_half_step_selector_index,
)


class WeakeningPortfolioServiceModeSuffixBatchMeanHalfStepThresholdFingerprintLawError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def build_adjacent_interval_midpoint_thresholds() -> list[dict[str, Any]]:
    return [
        {
            'adjacent_interval': [lower_rank, lower_rank + 1],
            'midpoint_half_step_threshold': (2 * lower_rank) + 1,
        }
        for lower_rank in range(build_max_rank())
    ]


def classify_half_step_selector_index_against_adjacent_interval_midpoint_threshold(
    *,
    half_step_selector_index: int,
    midpoint_half_step_threshold: int,
) -> dict[str, Any]:
    if half_step_selector_index < 0 or half_step_selector_index > build_max_half_step_selector_index():
        raise WeakeningPortfolioServiceModeSuffixBatchMeanHalfStepThresholdFingerprintLawError(
            'half-step selector index falls outside the source-rank path'
        )
    if midpoint_half_step_threshold % 2 != 1:
        raise WeakeningPortfolioServiceModeSuffixBatchMeanHalfStepThresholdFingerprintLawError(
            'adjacent interval midpoint threshold must be an odd half-step index'
        )
    if midpoint_half_step_threshold < 1 or midpoint_half_step_threshold > build_max_half_step_selector_index() - 1:
        raise WeakeningPortfolioServiceModeSuffixBatchMeanHalfStepThresholdFingerprintLawError(
            'adjacent interval midpoint threshold falls outside the width-1 interval family'
        )

    if half_step_selector_index < midpoint_half_step_threshold:
        relation = 'below_midpoint'
        fingerprint_symbol = 'L'
        meaning = 'lower_endpoint'
    elif half_step_selector_index == midpoint_half_step_threshold:
        relation = 'at_midpoint'
        fingerprint_symbol = 'B'
        meaning = 'both_endpoints'
    else:
        relation = 'above_midpoint'
        fingerprint_symbol = 'R'
        meaning = 'upper_endpoint'

    return {
        'half_step_selector_index': half_step_selector_index,
        'midpoint_half_step_threshold': midpoint_half_step_threshold,
        'relation': relation,
        'fingerprint_symbol': fingerprint_symbol,
        'meaning': meaning,
    }


@lru_cache(maxsize=1)
def build_monotone_fingerprint_word_catalog() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    thresholds = build_adjacent_interval_midpoint_thresholds()
    for half_step_selector_index in range(build_max_half_step_selector_index() + 1):
        symbols: list[str] = []
        symbol_rows: list[dict[str, Any]] = []
        for threshold_row in thresholds:
            classification = classify_half_step_selector_index_against_adjacent_interval_midpoint_threshold(
                half_step_selector_index=half_step_selector_index,
                midpoint_half_step_threshold=threshold_row['midpoint_half_step_threshold'],
            )
            symbols.append(classification['fingerprint_symbol'])
            symbol_rows.append(
                {
                    **threshold_row,
                    'relation': classification['relation'],
                    'fingerprint_symbol': classification['fingerprint_symbol'],
                    'meaning': classification['meaning'],
                }
            )

        fingerprint_word = ''.join(symbols)
        expected_fingerprint = build_width_one_fingerprint(half_step_selector_index=half_step_selector_index)
        if fingerprint_word != expected_fingerprint['fingerprint_word']:
            raise WeakeningPortfolioServiceModeSuffixBatchMeanHalfStepThresholdFingerprintLawError(
                'midpoint-threshold fingerprint word does not match the width-1 execution fingerprint'
            )
        rows.append(
            {
                'half_step_selector_index': half_step_selector_index,
                'selector_interval_summary': decode_half_step_selector_index(
                    half_step_selector_index=half_step_selector_index
                )['selector_interval_summary'],
                'fingerprint_word': fingerprint_word,
                'fingerprint_symbols': symbols,
                'threshold_rows': symbol_rows,
            }
        )
    return rows


def decode_half_step_selector_index_from_monotone_fingerprint_word(*, fingerprint_word: str) -> dict[str, Any]:
    if len(fingerprint_word) != build_max_rank():
        raise WeakeningPortfolioServiceModeSuffixBatchMeanHalfStepThresholdFingerprintLawError(
            'fingerprint word must have one symbol for each adjacent width-1 interval'
        )
    if any(symbol not in {'L', 'B', 'R'} for symbol in fingerprint_word):
        raise WeakeningPortfolioServiceModeSuffixBatchMeanHalfStepThresholdFingerprintLawError(
            'fingerprint word may only use L, B, and R'
        )

    leading_r_count = 0
    while leading_r_count < len(fingerprint_word) and fingerprint_word[leading_r_count] == 'R':
        leading_r_count += 1

    remainder = fingerprint_word[leading_r_count:]
    if remainder.startswith('B'):
        has_midpoint_tie_symbol = True
        tail = remainder[1:]
    else:
        has_midpoint_tie_symbol = False
        tail = remainder

    if any(symbol != 'L' for symbol in tail):
        raise WeakeningPortfolioServiceModeSuffixBatchMeanHalfStepThresholdFingerprintLawError(
            'fingerprint word must be monotone: R*B?L*'
        )
    if has_midpoint_tie_symbol and 'B' in tail:
        raise WeakeningPortfolioServiceModeSuffixBatchMeanHalfStepThresholdFingerprintLawError(
            'fingerprint word may contain at most one midpoint-tie symbol'
        )

    half_step_selector_index = (2 * leading_r_count) + (1 if has_midpoint_tie_symbol else 0)
    if half_step_selector_index > build_max_half_step_selector_index():
        raise WeakeningPortfolioServiceModeSuffixBatchMeanHalfStepThresholdFingerprintLawError(
            'decoded half-step selector index falls outside the source-rank path'
        )

    return {
        'fingerprint_word': fingerprint_word,
        'leading_r_count': leading_r_count,
        'has_midpoint_tie_symbol': has_midpoint_tie_symbol,
        'half_step_selector_index': half_step_selector_index,
        **decode_half_step_selector_index(half_step_selector_index=half_step_selector_index),
    }


@lru_cache(maxsize=1)
def build_batch_mean_half_step_threshold_fingerprint_examples() -> list[dict[str, Any]]:
    catalog = build_monotone_fingerprint_word_catalog()
    return [
        {
            'boundary_singleton_word': catalog[0]['fingerprint_word'],
            'decoded_boundary_singleton': decode_half_step_selector_index_from_monotone_fingerprint_word(
                fingerprint_word=catalog[0]['fingerprint_word']
            ),
        },
        {
            'interior_singleton_word': catalog[14]['fingerprint_word'],
            'decoded_interior_singleton': decode_half_step_selector_index_from_monotone_fingerprint_word(
                fingerprint_word=catalog[14]['fingerprint_word']
            ),
        },
        {
            'interior_tie_word': catalog[15]['fingerprint_word'],
            'decoded_interior_tie': decode_half_step_selector_index_from_monotone_fingerprint_word(
                fingerprint_word=catalog[15]['fingerprint_word']
            ),
        },
        {
            'top_singleton_word': catalog[32]['fingerprint_word'],
            'decoded_top_singleton': decode_half_step_selector_index_from_monotone_fingerprint_word(
                fingerprint_word=catalog[32]['fingerprint_word']
            ),
        },
        {
            'threshold_example': classify_half_step_selector_index_against_adjacent_interval_midpoint_threshold(
                half_step_selector_index=15,
                midpoint_half_step_threshold=15,
            ),
        },
    ]


@lru_cache(maxsize=1)
def build_batch_mean_half_step_threshold_fingerprint_validation_summary() -> dict[str, Any]:
    catalog = build_monotone_fingerprint_word_catalog()
    thresholds = build_adjacent_interval_midpoint_thresholds()
    fingerprint_words = [row['fingerprint_word'] for row in catalog]
    decoded_indices = [
        decode_half_step_selector_index_from_monotone_fingerprint_word(
            fingerprint_word=row['fingerprint_word']
        )['half_step_selector_index']
        for row in catalog
    ]
    if decoded_indices != list(range(build_max_half_step_selector_index() + 1)):
        raise WeakeningPortfolioServiceModeSuffixBatchMeanHalfStepThresholdFingerprintLawError(
            'fingerprint decoder should recover every half-step selector index exactly once'
        )

    signatures_by_omission: dict[str, int] = {}
    all_words = [tuple(word) for word in fingerprint_words]
    distinct_full_word_count = len(set(all_words))
    if distinct_full_word_count != build_max_half_step_selector_index() + 1:
        raise WeakeningPortfolioServiceModeSuffixBatchMeanHalfStepThresholdFingerprintLawError(
            'fingerprint words should separate all half-step selector classes'
        )

    omission_is_minimal = True
    for omission_index, threshold in enumerate(thresholds):
        omitted_signatures = {
            tuple(symbol for idx, symbol in enumerate(word) if idx != omission_index)
            for word in all_words
        }
        signatures_by_omission[str(threshold['adjacent_interval'])] = len(omitted_signatures)
        if len(omitted_signatures) == distinct_full_word_count:
            omission_is_minimal = False

    tie_word_count = sum('B' in word for word in fingerprint_words)
    singleton_word_count = len(fingerprint_words) - tie_word_count
    max_leading_r_count = max(
        decode_half_step_selector_index_from_monotone_fingerprint_word(fingerprint_word=word)['leading_r_count']
        for word in fingerprint_words
    )
    return {
        'validated_half_step_selector_index_class_count': len(catalog),
        'adjacent_width_one_interval_count': len(thresholds),
        'adjacent_midpoint_thresholds': [row['midpoint_half_step_threshold'] for row in thresholds],
        'distinct_monotone_fingerprint_word_count': distinct_full_word_count,
        'fingerprint_words_match_width_one_execution_fingerprints': True,
        'fingerprint_words_decode_back_to_half_step_selector_indices': True,
        'fingerprint_word_alphabet': ['L', 'B', 'R'],
        'singleton_word_count': singleton_word_count,
        'tie_word_count': tie_word_count,
        'max_leading_r_count': max_leading_r_count,
        'minimal_complete_separating_family_by_single_omission': omission_is_minimal,
        'single_omission_signature_count_is_uniform': len(set(signatures_by_omission.values())) == 1,
        'single_omission_signature_count': next(iter(signatures_by_omission.values())),
        'distinct_signature_count_by_adjacent_interval_omission': signatures_by_omission,
        'fingerprint_word_examples': {
            'boundary_singleton_index_0': catalog[0]['fingerprint_word'],
            'interior_singleton_index_14': catalog[14]['fingerprint_word'],
            'interior_tie_index_15': catalog[15]['fingerprint_word'],
            'boundary_singleton_index_32': catalog[32]['fingerprint_word'],
        },
    }


@lru_cache(maxsize=1)
def build_headline_findings() -> dict[str, Any]:
    validation = build_batch_mean_half_step_threshold_fingerprint_validation_summary()
    return {
        'path_l2_selector_classes_have_a_closed_form_adjacent_interval_fingerprint_word': validation[
            'distinct_monotone_fingerprint_word_count'
        ],
        'fingerprint_words_decode_back_to_the_same_33_half_step_selector_classes': validation[
            'fingerprint_words_decode_back_to_half_step_selector_indices'
        ],
        'the_16_adjacent_width_one_intervals_remain_a_minimal_complete_separating_family': validation[
            'minimal_complete_separating_family_by_single_omission'
        ],
        'validation_summary': validation,
    }


@lru_cache(maxsize=1)
def build_decision_rules() -> list[str]:
    return [
        'If you need an audit certificate for a path-L2 selector class, record its 16-symbol adjacent-interval fingerprint word over the width-1 intervals [0,1] through [15,16].',
        'Generate each symbol by comparing half_step_selector_index = h against the odd midpoint threshold 2j+1 of interval [j, j+1]: use L when h is below, B when h equals, and R when h is above.',
        'Decode any valid fingerprint word by counting its leading R symbols and then checking whether the next symbol is B: the index is 2 * leading_R_count for singleton words and 2 * leading_R_count + 1 for tie words.',
        'Expect valid fingerprint words to be exactly the monotone ternary forms R^kL^(16-k) or R^kBL^(15-k); anything else is an invalid selector certificate.',
        'Use this word as a compact regression certificate, not as a substitute for the feasible-band clamp law; witness execution still clamps the selector class into the doubled feasible band.',
        'If any future revision needs more than 16 adjacent intervals or yields a non-monotone word, treat that as a redesign signal for the current path-L2 selector geometry.',
    ]


@lru_cache(maxsize=1)
def build_source_reports() -> list[str]:
    return [
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_selector_index_law_snapshot_20260309.md',
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_feasible_band_clamp_law_snapshot_20260309.md',
    ]


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_mean_half_step_threshold_fingerprint_snapshot() -> dict[str, Any]:
    return {
        'focus': 'Closed-form adjacent-interval fingerprint words for path-L2 half-step selector classes',
        'headline_findings': build_headline_findings(),
        'decision_rules': build_decision_rules(),
        'selection_examples': build_batch_mean_half_step_threshold_fingerprint_examples(),
        'source_reports': build_source_reports(),
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_threshold_fingerprint_law.py',
    }


def main() -> None:
    print(json.dumps(build_service_mode_suffix_batch_mean_half_step_threshold_fingerprint_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
