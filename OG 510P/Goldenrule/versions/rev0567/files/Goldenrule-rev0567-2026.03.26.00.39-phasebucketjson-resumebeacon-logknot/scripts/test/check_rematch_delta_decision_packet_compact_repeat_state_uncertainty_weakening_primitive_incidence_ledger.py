#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_incidence_ledger import (
    build_cumulative_primitive_budget_path,
    build_marginal_release_factorizations,
    build_primitive_signature_classes,
    build_weakening_primitive_incidence_ledger_snapshot,
)


def _assert_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise SystemExit(f'{label}: expected {expected!r}, got {actual!r}')



def main() -> None:
    factorizations = build_marginal_release_factorizations()
    _assert_equal(len(factorizations), 5, 'factorization count')
    _assert_equal(
        [row['primitive_signature'] for row in factorizations],
        [
            {'middle_precision_relief_units': 0, 'relaxed_suffix_release_units': 1},
            {'middle_precision_relief_units': 1, 'relaxed_suffix_release_units': 0},
            {'middle_precision_relief_units': 0, 'relaxed_suffix_release_units': 1},
            {'middle_precision_relief_units': 0, 'relaxed_suffix_release_units': 1},
            {'middle_precision_relief_units': 1, 'relaxed_suffix_release_units': 1},
        ],
        'primitive signatures by budget step',
    )
    _assert_equal(
        [row['primitive_signature_label'] for row in factorizations],
        ['P0_S1', 'P1_S0', 'P0_S1', 'P0_S1', 'P1_S1'],
        'primitive signature labels by budget step',
    )

    signature_classes = build_primitive_signature_classes()
    _assert_equal(len(signature_classes), 3, 'signature class count')
    class_map = {row['primitive_signature_label']: row for row in signature_classes}
    _assert_equal(class_map['P0_S1']['member_budget_steps'], [1, 3, 4], 'suffix-only budget steps')
    _assert_equal(class_map['P1_S0']['member_budget_steps'], [2], 'precision-only budget steps')
    _assert_equal(class_map['P1_S1']['member_budget_steps'], [5], 'composite budget steps')

    path = build_cumulative_primitive_budget_path()
    _assert_equal(
        [row['cumulative_primitive_signature'] for row in path],
        [
            {'middle_precision_relief_units': 0, 'relaxed_suffix_release_units': 0},
            {'middle_precision_relief_units': 0, 'relaxed_suffix_release_units': 1},
            {'middle_precision_relief_units': 1, 'relaxed_suffix_release_units': 1},
            {'middle_precision_relief_units': 1, 'relaxed_suffix_release_units': 2},
            {'middle_precision_relief_units': 1, 'relaxed_suffix_release_units': 3},
            {'middle_precision_relief_units': 2, 'relaxed_suffix_release_units': 4},
        ],
        'cumulative primitive budget path',
    )

    report = build_weakening_primitive_incidence_ledger_snapshot()
    _assert_equal(report['headline_findings']['primitive_signature_class_count'], 3, 'headline signature class count')
    _assert_equal(report['headline_findings']['suffix_only_budget_steps'], [1, 3, 4], 'headline suffix-only steps')
    _assert_equal(report['headline_findings']['precision_only_budget_steps'], [2], 'headline precision-only steps')
    _assert_equal(report['headline_findings']['composite_budget_steps'], [5], 'headline composite steps')
    _assert_equal(report['headline_findings']['no_second_precision_unit_without_extra_suffix_unit'], True, 'headline impossibility flag')

    print('weakening primitive incidence ledger checks passed')


if __name__ == '__main__':
    main()
