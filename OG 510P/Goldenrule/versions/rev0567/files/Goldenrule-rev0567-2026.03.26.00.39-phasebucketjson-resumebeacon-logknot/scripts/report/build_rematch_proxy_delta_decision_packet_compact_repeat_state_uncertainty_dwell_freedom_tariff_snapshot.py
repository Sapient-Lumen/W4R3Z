#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_freedom_tariff_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_freedom_tariff_snapshot_20260308.md'
FLOOR_SUPPORT_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_conditioned_dwell_support_snapshot_20260308.json'
GUARANTEE_SELECTOR_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_guarantee_threshold_selector_snapshot_20260308.json'


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _round(value: float) -> float:
    return round(value, 6)


def _continuous_non_precision_count(row: dict[str, Any]) -> int:
    start = row['continuous_non_precision_support_start_unique_appends']
    end = row['continuous_non_precision_support_end_unique_appends']
    if start is None or end is None:
        return 0
    return int(end) - int(start) + 1


def _component_points(components: list[dict[str, Any]]) -> list[int]:
    points: list[int] = []
    for component in components:
        start = int(component['start_unique_appends'])
        end = int(component['end_unique_appends'])
        points.extend(range(start, end + 1))
    return sorted(set(points))


def _points_to_notation(points: list[int]) -> str:
    if not points:
        return '∅'
    runs: list[tuple[int, int]] = []
    start = prev = points[0]
    for point in points[1:]:
        if point == prev + 1:
            prev = point
            continue
        runs.append((start, prev))
        start = prev = point
    runs.append((start, prev))
    pieces = []
    for start, end in runs:
        if start == end:
            pieces.append(f'{{{start}}}')
        else:
            pieces.append(f'[{start}, {end}]')
    return ' ∪ '.join(pieces)


def _tier_rows() -> list[dict[str, Any]]:
    support = _load(FLOOR_SUPPORT_REPORT)
    selector = _load(GUARANTEE_SELECTOR_REPORT)
    actual_floor = {
        row['tier']: float(row['actual_certified_gain_share_floor_of_full_dynamic_savings'])
        for row in selector['tier_rows']
    }
    rows: list[dict[str, Any]] = []
    for row in support['support_rows']:
        tier = str(row['strongest_exact_tier_still_needed'])
        if tier == 'none':
            continue
        supported = int(row['supported_dwell_count_unique_appends'])
        continuous = _continuous_non_precision_count(row)
        rows.append(
            {
                'tier': tier,
                'actual_certified_gain_share_floor_of_full_dynamic_savings': actual_floor[tier],
                'required_gain_share_floor_interval': str(row['required_gain_share_floor_interval']),
                'live_support_set_notation': str(row['live_support_set_notation']),
                'live_support_points_unique_appends': _component_points(list(row['live_support_components'])),
                'supported_dwell_count_unique_appends': supported,
                'continuous_non_precision_support_count_unique_appends': continuous,
                'continuous_non_precision_support_present': continuous > 0,
                'canonical_anchor_choices_unique_appends': list(row['canonical_anchor_choices_unique_appends']),
                'largest_removed_suffix_if_floor_tightens_again': row['largest_removed_suffix_if_floor_tightens_again'],
            }
        )
    return rows


def _upgrade(from_row: dict[str, Any], to_row: dict[str, Any]) -> dict[str, Any]:
    lost = from_row['supported_dwell_count_unique_appends'] - to_row['supported_dwell_count_unique_appends']
    cont_lost = (
        from_row['continuous_non_precision_support_count_unique_appends']
        - to_row['continuous_non_precision_support_count_unique_appends']
    )
    gain_delta = _round(
        to_row['actual_certified_gain_share_floor_of_full_dynamic_savings']
        - from_row['actual_certified_gain_share_floor_of_full_dynamic_savings']
    )
    removed_points = sorted(
        set(from_row['live_support_points_unique_appends']) - set(to_row['live_support_points_unique_appends'])
    )
    return {
        'from_tier': from_row['tier'],
        'to_tier': to_row['tier'],
        'from_live_support_set_notation': from_row['live_support_set_notation'],
        'to_live_support_set_notation': to_row['live_support_set_notation'],
        'lost_live_dwell_count_unique_appends': lost,
        'retained_live_dwell_count_unique_appends': to_row['supported_dwell_count_unique_appends'],
        'retained_live_dwell_fraction': _round(
            to_row['supported_dwell_count_unique_appends'] / from_row['supported_dwell_count_unique_appends']
        ),
        'lost_continuous_non_precision_dwell_count_unique_appends': cont_lost,
        'realized_worst_case_gain_share_delta': gain_delta,
        'realized_worst_case_gain_share_delta_per_lost_live_dwell': _round(gain_delta / lost),
        'removed_live_support_suffix_or_component': _points_to_notation(removed_points),
        'destroys_all_continuous_non_precision_support': (
            from_row['continuous_non_precision_support_present'] and not to_row['continuous_non_precision_support_present']
        ),
    }


def _build_report() -> dict[str, Any]:
    tiers = _tier_rows()
    rows = {row['tier']: row for row in tiers}
    lower_to_near_optimal = _upgrade(rows['lower_guarantee'], rows['near_optimal'])
    near_optimal_to_near_exact = _upgrade(rows['near_optimal'], rows['near_exact'])
    lower_to_near_exact = _upgrade(rows['lower_guarantee'], rows['near_exact'])
    efficiency_advantage = _round(
        lower_to_near_optimal['realized_worst_case_gain_share_delta_per_lost_live_dwell']
        / near_optimal_to_near_exact['realized_worst_case_gain_share_delta_per_lost_live_dwell']
    )

    return {
        'focus': 'Price higher exact compact repeat-state uncertainty floors by lost dwell freedom so inheritors can see how quickly live support collapses, not just how caps and checkpoints rise.',
        'headline_findings': {
            'near_optimal_is_last_exact_tier_with_continuous_non_precision_support': True,
            'lower_to_near_optimal_lost_live_dwell_count_unique_appends': lower_to_near_optimal['lost_live_dwell_count_unique_appends'],
            'lower_to_near_optimal_realized_worst_case_gain_share_delta': lower_to_near_optimal['realized_worst_case_gain_share_delta'],
            'lower_to_near_optimal_realized_worst_case_gain_share_delta_per_lost_live_dwell': lower_to_near_optimal['realized_worst_case_gain_share_delta_per_lost_live_dwell'],
            'lower_to_near_optimal_retained_live_dwell_fraction': lower_to_near_optimal['retained_live_dwell_fraction'],
            'near_optimal_to_near_exact_lost_live_dwell_count_unique_appends': near_optimal_to_near_exact['lost_live_dwell_count_unique_appends'],
            'near_optimal_to_near_exact_realized_worst_case_gain_share_delta': near_optimal_to_near_exact['realized_worst_case_gain_share_delta'],
            'near_optimal_to_near_exact_realized_worst_case_gain_share_delta_per_lost_live_dwell': near_optimal_to_near_exact['realized_worst_case_gain_share_delta_per_lost_live_dwell'],
            'near_optimal_to_near_exact_retained_live_dwell_fraction': near_optimal_to_near_exact['retained_live_dwell_fraction'],
            'first_upgrade_support_efficiency_advantage_over_second': efficiency_advantage,
            'direct_lower_to_near_exact_lost_live_dwell_count_unique_appends': lower_to_near_exact['lost_live_dwell_count_unique_appends'],
            'main_rule': 'Treat exact 0.95 as the last uncertainty tier that preserves any continuous non-precision dwell freedom: tightening from 0.95 to 0.99 burns 11 of the 12 remaining live dwell targets for only +0.019341 floor, whereas tightening from 0.85 to 0.95 loses 14 dwell targets but buys +0.109999 and still leaves the exact 8–18 non-fragile band alive.',
        },
        'decision_rules': [
            'If the deployment still wants any continuous non-precision dwell latitude, never escalate beyond the exact 0.95 tier; exact 0.99 collapses the menu to the singleton precision point at dwell 2.',
            'Use the exact 0.95 tier as the last floor increase that still preserves a real retuning band; it is not just the cap knee, it is also the dwell-freedom knee.',
            'Treat exact 0.99 as paying almost entirely for floor, not for menu breadth: it retains only 1 of the 12 live dwell targets that survive at exact 0.95.',
            'If future retuning across late dwells 19–32 matters, do not tighten beyond the exact 0.85 tier unless the higher floor requirement is truly substantive.',
        ],
        'tier_rows': tiers,
        'support_tariff_rows': [lower_to_near_optimal, near_optimal_to_near_exact, lower_to_near_exact],
        'source_reports': [
            str(FLOOR_SUPPORT_REPORT.relative_to(ROOT)),
            str(GUARANTEE_SELECTOR_REPORT.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(report: dict[str, Any]) -> str:
    findings = report['headline_findings']
    lines = [
        '# Rematch Proxy Delta Decision Packet Compact Repeat-State Uncertainty Dwell-Freedom Tariff Snapshot — 2026-03-08',
        '',
        '## Focus',
        f"- {report['focus']}",
        '',
        '## Headline findings',
        f"- exact `0.95` is the last tier with continuous non-precision dwell support: `near_optimal_is_last_exact_tier_with_continuous_non_precision_support = {findings['near_optimal_is_last_exact_tier_with_continuous_non_precision_support']}`.",
        f"- tightening `0.85 -> 0.95` loses `{findings['lower_to_near_optimal_lost_live_dwell_count_unique_appends']}` live dwells while buying `+{findings['lower_to_near_optimal_realized_worst_case_gain_share_delta']}` floor, which is `{findings['lower_to_near_optimal_realized_worst_case_gain_share_delta_per_lost_live_dwell']}` floor per lost dwell and retains `{findings['lower_to_near_optimal_retained_live_dwell_fraction']}` of the previous live support.",
        f"- tightening `0.95 -> 0.99` loses `{findings['near_optimal_to_near_exact_lost_live_dwell_count_unique_appends']}` live dwells while buying only `+{findings['near_optimal_to_near_exact_realized_worst_case_gain_share_delta']}` floor, which is `{findings['near_optimal_to_near_exact_realized_worst_case_gain_share_delta_per_lost_live_dwell']}` floor per lost dwell and retains only `{findings['near_optimal_to_near_exact_retained_live_dwell_fraction']}` of the previous live support.",
        f"- first-step support efficiency advantage over second-step tightening: `{findings['first_upgrade_support_efficiency_advantage_over_second']}`x.",
        f"- direct `0.85 -> 0.99` collapse removes `{findings['direct_lower_to_near_exact_lost_live_dwell_count_unique_appends']}` of the current `26` live exact dwells, leaving only the singleton precision point.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Exact support tiers',
        '| tier | actual certified floor | floor interval | live support | live dwell count | continuous non-precision count | anchors | next removable component |',
        '|---|---:|---|---|---:|---:|---|---|',
    ]
    for row in report['tier_rows']:
        lines.append(
            f"| {row['tier']} | {row['actual_certified_gain_share_floor_of_full_dynamic_savings']} | {row['required_gain_share_floor_interval']} | {row['live_support_set_notation']} | {row['supported_dwell_count_unique_appends']} | {row['continuous_non_precision_support_count_unique_appends']} | {row['canonical_anchor_choices_unique_appends']} | {row['largest_removed_suffix_if_floor_tightens_again']} |"
        )
    lines.extend([
        '',
        '## Dwell-freedom tariffs',
        '| upgrade | lost live dwell count | retained live dwell count | retained fraction | lost continuous non-precision dwells | floor delta | floor delta per lost dwell | removed component | destroys all continuous non-precision support |',
        '|---|---:|---:|---:|---:|---:|---:|---|---|',
    ])
    for row in report['support_tariff_rows']:
        lines.append(
            f"| {row['from_tier']} -> {row['to_tier']} | {row['lost_live_dwell_count_unique_appends']} | {row['retained_live_dwell_count_unique_appends']} | {row['retained_live_dwell_fraction']} | {row['lost_continuous_non_precision_dwell_count_unique_appends']} | {row['realized_worst_case_gain_share_delta']} | {row['realized_worst_case_gain_share_delta_per_lost_live_dwell']} | {row['removed_live_support_suffix_or_component']} | {row['destroys_all_continuous_non_precision_support']} |"
        )
    lines.extend([
        '',
        '## Decision rules',
    ])
    for rule in report['decision_rules']:
        lines.append(f'- {rule}')
    lines.extend([
        '',
        '## Provenance',
        f"- source reports: {', '.join(report['source_reports'])}",
        f"- source script: `{report['source_script']}`",
        '',
    ])
    return '\n'.join(lines)


def main() -> None:
    report = _build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2) + '\n')
    OUT_MD.write_text(_render_md(report))
    print(f'wrote {OUT_JSON.relative_to(ROOT)} and {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
