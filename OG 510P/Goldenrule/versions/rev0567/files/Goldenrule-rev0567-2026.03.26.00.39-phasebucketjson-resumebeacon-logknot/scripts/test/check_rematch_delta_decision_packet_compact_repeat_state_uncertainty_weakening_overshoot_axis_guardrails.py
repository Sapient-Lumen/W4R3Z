#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_overshoot_axis_guardrails import (
    build_guardrail_profile_partition,
    build_overshoot_axis_guardrail_profiles,
    build_weakening_overshoot_axis_guardrails_snapshot,
    select_budget_by_primitive_demand_under_axis_guardrails,
)


def _assert_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise SystemExit(f'{label}: expected {expected!r}, got {actual!r}')


def main() -> None:
    profiles = build_overshoot_axis_guardrail_profiles()
    _assert_equal(
        [(row['profile_label'], row['admitted_coordinate_count'], row['rejected_coordinate_count']) for row in profiles],
        [
            ('exact_only', 6, 9),
            ('precision_hitchhike_only', 10, 5),
            ('suffix_hitchhike_only', 11, 4),
            ('any_single_axis_hitchhike', 15, 0),
        ],
        'guardrail coverage counts',
    )
    _assert_equal(
        [row['admitted_hitchhike_axis_families'] for row in profiles],
        [
            [],
            ['precision_only_hitchhike'],
            ['suffix_only_hitchhike'],
            ['precision_only_hitchhike', 'suffix_only_hitchhike'],
        ],
        'guardrail admitted hitchhike families',
    )

    partition = build_guardrail_profile_partition()
    _assert_equal(
        [(row['profile_label'], row['member_count']) for row in partition],
        [
            ('exact_only', 6),
            ('precision_hitchhike_only', 4),
            ('suffix_hitchhike_only', 5),
            ('any_single_axis_hitchhike', 0),
        ],
        'minimal profile partition counts',
    )

    _assert_equal(
        select_budget_by_primitive_demand_under_axis_guardrails(0, 2, allow_precision_hitchhike=False, allow_suffix_hitchhike=False)['admissible_under_axis_guardrails'],
        False,
        'exact-only rejects deep suffix demand',
    )
    _assert_equal(
        select_budget_by_primitive_demand_under_axis_guardrails(0, 2, allow_precision_hitchhike=True, allow_suffix_hitchhike=False)['admissible_under_axis_guardrails'],
        True,
        'precision hitchhike admits deep suffix demand',
    )
    _assert_equal(
        select_budget_by_primitive_demand_under_axis_guardrails(2, 1, allow_precision_hitchhike=False, allow_suffix_hitchhike=True)['admissible_under_axis_guardrails'],
        True,
        'suffix hitchhike admits early second precision demand',
    )
    _assert_equal(
        select_budget_by_primitive_demand_under_axis_guardrails(2, 1, allow_precision_hitchhike=True, allow_suffix_hitchhike=False)['admissible_under_axis_guardrails'],
        False,
        'precision hitchhike still rejects early second precision demand',
    )

    report = build_weakening_overshoot_axis_guardrails_snapshot()
    _assert_equal(
        report['headline_findings']['coverage_count_by_guardrail_profile'],
        {
            'exact_only': 6,
            'precision_hitchhike_only': 10,
            'suffix_hitchhike_only': 11,
            'any_single_axis_hitchhike': 15,
        },
        'headline coverage counts',
    )
    _assert_equal(
        report['headline_findings']['minimal_profile_partition_counts'],
        {
            'exact_only': 6,
            'precision_hitchhike_only': 4,
            'suffix_hitchhike_only': 5,
            'any_single_axis_hitchhike': 0,
        },
        'headline minimal partition counts',
    )
    _assert_equal(
        report['headline_findings']['no_demand_requires_both_hitchhike_permissions_simultaneously'],
        True,
        'headline no-dual-axis-necessity flag',
    )
    _assert_equal(
        report['headline_findings']['dual_axis_permission_is_portfolio_level_not_single_request_level'],
        True,
        'headline portfolio-level flag',
    )

    print('weakening overshoot axis guardrails checks passed')


if __name__ == '__main__':
    main()
