#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]

ANCHOR_DWELLS = {
    'near_exact': 2,
    'near_optimal': 13,
    'lower_guarantee': 25,
}

ROUTE_STEPS: dict[tuple[str, str], list[dict[str, Any]]] = {
    ('near_exact', 'near_exact'): [],
    ('near_exact', 'near_optimal'): [
        {
            'phase_label': 'boundary_widen_to_neutral_entry',
            'phase_type': 'boundary_repair',
            'from_dwell_unique_appends': 2,
            'to_dwell_unique_appends': 8,
            'why': 'Weakening from the precision singleton widens first to the neutral-band entry boundary at dwell 8.',
        },
        {
            'phase_label': 'steady_recenter_to_neutral_anchor',
            'phase_type': 'anchor_recentering',
            'from_dwell_unique_appends': 8,
            'to_dwell_unique_appends': 13,
            'why': 'Steady operation in the neutral band recenters from boundary 8 to canonical anchor 13.',
        },
    ],
    ('near_exact', 'lower_guarantee'): [
        {
            'phase_label': 'boundary_widen_to_neutral_entry',
            'phase_type': 'boundary_repair',
            'from_dwell_unique_appends': 2,
            'to_dwell_unique_appends': 8,
            'why': 'Even full relaxation from precision still starts at the neutral-band entry boundary 8.',
        },
        {
            'phase_label': 'boundary_widen_to_relaxed_entry',
            'phase_type': 'boundary_repair',
            'from_dwell_unique_appends': 8,
            'to_dwell_unique_appends': 19,
            'why': 'After entering the neutral band, the next weaker-band entry point is the relaxed-suffix boundary at dwell 19.',
        },
        {
            'phase_label': 'steady_recenter_to_lower_guarantee_anchor',
            'phase_type': 'anchor_recentering',
            'from_dwell_unique_appends': 19,
            'to_dwell_unique_appends': 25,
            'why': 'Steady operation in the relaxed suffix recenters from entry boundary 19 to canonical anchor 25.',
        },
    ],
    ('near_optimal', 'near_exact'): [
        {
            'phase_label': 'direct_collapse_to_precision_anchor',
            'phase_type': 'boundary_and_anchor',
            'from_dwell_unique_appends': 13,
            'to_dwell_unique_appends': 2,
            'why': 'Strengthening beyond floor 0.980481 collapses directly to the precision singleton at dwell 2.',
        },
    ],
    ('near_optimal', 'near_optimal'): [],
    ('near_optimal', 'lower_guarantee'): [
        {
            'phase_label': 'boundary_widen_to_relaxed_entry',
            'phase_type': 'boundary_repair',
            'from_dwell_unique_appends': 13,
            'to_dwell_unique_appends': 19,
            'why': 'Weakening from the neutral band first enters the relaxed suffix at boundary 19.',
        },
        {
            'phase_label': 'steady_recenter_to_lower_guarantee_anchor',
            'phase_type': 'anchor_recentering',
            'from_dwell_unique_appends': 19,
            'to_dwell_unique_appends': 25,
            'why': 'Steady operation in the relaxed suffix recenters from boundary 19 to anchor 25.',
        },
    ],
    ('lower_guarantee', 'near_exact'): [
        {
            'phase_label': 'direct_collapse_to_precision_anchor',
            'phase_type': 'boundary_and_anchor',
            'from_dwell_unique_appends': 25,
            'to_dwell_unique_appends': 2,
            'why': 'High-floor strengthening from the relaxed suffix bypasses the neutral band and collapses directly to dwell 2.',
        },
    ],
    ('lower_guarantee', 'near_optimal'): [
        {
            'phase_label': 'boundary_repair_to_neutral_exit',
            'phase_type': 'boundary_repair',
            'from_dwell_unique_appends': 25,
            'to_dwell_unique_appends': 18,
            'why': 'Strengthening from the relaxed suffix into the neutral band lands first on exit boundary 18.',
        },
        {
            'phase_label': 'steady_recenter_to_neutral_anchor',
            'phase_type': 'anchor_recentering',
            'from_dwell_unique_appends': 18,
            'to_dwell_unique_appends': 13,
            'why': 'Steady operation in the neutral band recenters from exit boundary 18 to canonical anchor 13.',
        },
    ],
    ('lower_guarantee', 'lower_guarantee'): [],
}


class RouteError(ValueError):
    pass


def tiers() -> list[str]:
    return list(ANCHOR_DWELLS)


def plan_anchor_route(start_tier: str, end_tier: str) -> dict[str, Any]:
    if start_tier not in ANCHOR_DWELLS:
        raise RouteError(f'unknown start tier: {start_tier}')
    if end_tier not in ANCHOR_DWELLS:
        raise RouteError(f'unknown end tier: {end_tier}')

    start_dwell = ANCHOR_DWELLS[start_tier]
    end_dwell = ANCHOR_DWELLS[end_tier]
    steps = []
    for raw_step in ROUTE_STEPS[(start_tier, end_tier)]:
        step = dict(raw_step)
        step['absolute_dwell_shift_unique_appends'] = abs(
            step['to_dwell_unique_appends'] - step['from_dwell_unique_appends']
        )
        steps.append(step)

    route = [start_dwell] + [step['to_dwell_unique_appends'] for step in steps]
    touched_transient_boundaries = sorted(
        {
            dwell
            for dwell in route
            if dwell in {8, 18, 19}
        }
    )
    direction = 'hold'
    if end_dwell > start_dwell:
        direction = 'weaken'
    elif end_dwell < start_dwell:
        direction = 'strengthen'

    return {
        'tool': str(Path(__file__).resolve()),
        'start_tier': start_tier,
        'end_tier': end_tier,
        'start_anchor_unique_appends': start_dwell,
        'end_anchor_unique_appends': end_dwell,
        'direction': direction,
        'route_unique_appends': route,
        'step_count': len(steps),
        'total_absolute_dwell_shift_unique_appends': sum(
            step['absolute_dwell_shift_unique_appends'] for step in steps
        ),
        'touches_transient_boundaries_unique_appends': touched_transient_boundaries,
        'collapses_directly_to_precision': direction == 'strengthen' and end_tier == 'near_exact',
        'steps': steps,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Exact one-shot canonical-anchor retuning route atlas.')
    parser.add_argument('--start-tier', required=True, choices=tiers())
    parser.add_argument('--end-tier', required=True, choices=tiers())
    return parser


def main() -> None:
    args = _parser().parse_args()
    print(json.dumps(plan_anchor_route(args.start_tier, args.end_tier), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
