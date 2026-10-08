#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_conditioned_dwell_support_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_conditioned_dwell_support_snapshot_20260308.md'
GUARANTEE_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_guarantee_threshold_selector_snapshot_20260308.json'
TOLERANCE_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_tolerance_staircase_snapshot_20260308.json'
TOPOLOGY_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_coverage_topology_snapshot_20260308.json'
CANONICAL_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_canonical_anchor_labels_snapshot_20260308.json'

ORDER = ['lower_guarantee', 'near_optimal', 'near_exact']


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _interval_cardinality(component: dict[str, int]) -> int:
    return component['end_unique_appends'] - component['start_unique_appends'] + 1


def _merge_touching(components: list[dict[str, int]]) -> list[dict[str, int]]:
    merged: list[dict[str, int]] = []
    for component in sorted(components, key=lambda c: (c['start_unique_appends'], c['end_unique_appends'])):
        if not merged:
            merged.append(dict(component))
            continue
        last = merged[-1]
        if component['start_unique_appends'] <= last['end_unique_appends'] + 1:
            last['end_unique_appends'] = max(last['end_unique_appends'], component['end_unique_appends'])
        else:
            merged.append(dict(component))
    return merged


def _support_rows() -> list[dict[str, Any]]:
    guarantee = _load(GUARANTEE_REPORT)
    threshold_rows = guarantee['threshold_rows']
    guarantee_tier_rows = {row['tier']: row for row in guarantee['tier_rows']}
    tolerance_rows = {row['tier']: row for row in _load(TOLERANCE_REPORT)['tier_rows']}
    anchor_rows = {row['tier']: row for row in _load(CANONICAL_REPORT)['tier_rows']}

    rows: list[dict[str, Any]] = []
    for row in threshold_rows:
        interval = row['required_gain_share_floor_interval']
        tier = row['cheapest_exact_feasible_tier']
        if tier == 'none':
            rows.append(
                {
                    'required_gain_share_floor_interval': interval,
                    'strongest_exact_tier_still_needed': 'none',
                    'live_support_components': [],
                    'live_support_set_notation': '∅',
                    'live_support_component_count': 0,
                    'supported_dwell_count_unique_appends': 0,
                    'continuous_non_precision_support_start_unique_appends': None,
                    'continuous_non_precision_support_end_unique_appends': None,
                    'canonical_anchor_choices_unique_appends': [],
                    'largest_removed_suffix_if_floor_tightens_again': None,
                    'most_compact_rule': 'No current exact dwell support survives above floor 0.999822.',
                }
            )
            continue

        eligible_tiers = [
            name
            for name in ORDER
            if row['maximum_required_gain_share_floor_inclusive']
            <= guarantee_tier_rows[name]['actual_certified_gain_share_floor_of_full_dynamic_savings']
        ]
        components: list[dict[str, int]] = []
        anchors: list[int] = []
        for eligible in eligible_tiers:
            trow = tolerance_rows[eligible]
            anchors.append(anchor_rows[eligible]['canonical_anchor_minimum_dwell_unique_appends'])
            start = trow['exact_dwell_band_start_unique_appends']
            end = trow['exact_dwell_band_end_unique_appends']
            comp = {'start_unique_appends': start, 'end_unique_appends': end}
            if comp not in components:
                components.append(comp)
        components = _merge_touching(components)
        total_supported = sum(_interval_cardinality(component) for component in components)
        set_notation = ' ∪ '.join(
            f"{{{c['start_unique_appends']}}}" if c['start_unique_appends'] == c['end_unique_appends'] else f"[{c['start_unique_appends']}, {c['end_unique_appends']}]"
            for c in components
        )
        non_precision = next((c for c in components if c['start_unique_appends'] >= 8), None)

        if tier == 'lower_guarantee':
            removed_suffix = '[19, 32]'
            compact_rule = 'Any floor demand above 0.870482 deletes the relaxed 19–32 dwell suffix; only dwell 2 and the 8–18 band remain live.'
        elif tier == 'near_optimal':
            removed_suffix = '[8, 18]'
            compact_rule = 'Any floor demand above 0.980481 collapses the continuous non-precision support entirely; only dwell 2 remains live.'
        else:
            removed_suffix = '{2}'
            compact_rule = 'The near-exact interval is already a singleton precision point, so any further floor tightening leaves no current exact support.'

        rows.append(
            {
                'required_gain_share_floor_interval': interval,
                'strongest_exact_tier_still_needed': tier,
                'live_support_components': components,
                'live_support_set_notation': set_notation,
                'live_support_component_count': len(components),
                'supported_dwell_count_unique_appends': total_supported,
                'continuous_non_precision_support_start_unique_appends': None if non_precision is None else non_precision['start_unique_appends'],
                'continuous_non_precision_support_end_unique_appends': None if non_precision is None else non_precision['end_unique_appends'],
                'canonical_anchor_choices_unique_appends': sorted(set(anchors)),
                'largest_removed_suffix_if_floor_tightens_again': removed_suffix,
                'most_compact_rule': compact_rule,
            }
        )
    return rows


def _headline_findings(rows: list[dict[str, Any]]) -> dict[str, Any]:
    relaxed, middle, precise, overflow = rows
    return {
        'main_rule': 'Use the required worst-case preserved-gain floor to prune dwell search *before* you spend effort on cap or tolerance tuning: floors above 0.870482 delete the relaxed 19–32 suffix, floors above 0.980481 collapse the continuous non-precision support to nothing, and floors above 0.999822 leave no current exact support at all.',
        'support_cliffs_by_floor': [
            {'floor_exclusive': 0.870482, 'removed_exact_dwell_support': '[19, 32]'},
            {'floor_exclusive': 0.980481, 'removed_exact_dwell_support': '[8, 18]'},
            {'floor_exclusive': 0.999822, 'removed_exact_dwell_support': '{2}'},
        ],
        'widest_live_support_interval': relaxed['live_support_set_notation'],
        'middle_interval_live_support': middle['live_support_set_notation'],
        'highest_floor_with_non_fragile_support': 0.980481,
        'singleton_precision_support_interval': precise['live_support_set_notation'],
        'internal_exact_gap_persists_below_near_exact': '[3, 7]',
        'supported_dwell_counts_descending_by_floor_interval': [
            {
                'required_gain_share_floor_interval': row['required_gain_share_floor_interval'],
                'supported_dwell_count_unique_appends': row['supported_dwell_count_unique_appends'],
            }
            for row in rows
        ],
        'no_current_exact_support_above_floor': overflow['required_gain_share_floor_interval'],
    }


def _render_md(summary: dict[str, Any]) -> str:
    lines = [
        '# Compact Repeat-State Uncertainty Floor-Conditioned Dwell Support Snapshot (2026-03-08)',
        '',
        '## Focus',
        f"- {summary['focus']}",
        '',
        '## Headline findings',
    ]
    findings = summary['headline_findings']
    lines.extend([
        f"- main rule: {findings['main_rule']}",
        f"- widest live support: `{findings['widest_live_support_interval']}`.",
        f"- middle support after the first floor cliff: `{findings['middle_interval_live_support']}`.",
        f"- highest floor with non-fragile support: `{findings['highest_floor_with_non_fragile_support']}`.",
        f"- singleton precision support: `{findings['singleton_precision_support_interval']}`.",
        f"- no current exact support above: `{findings['no_current_exact_support_above_floor']}`.",
        '',
        '## Support ladder',
    ])
    for row in summary['support_rows']:
        lines.append(
            f"- floor interval `{row['required_gain_share_floor_interval']}` -> support `{row['live_support_set_notation']}`, canonical anchors `{row['canonical_anchor_choices_unique_appends']}`, supported dwell count `{row['supported_dwell_count_unique_appends']}`."
        )
    lines.extend([
        '',
        '## Why this matters',
        '- the archive can now prune whole dwell regions directly from the requested worst-case guarantee instead of retuning inside dead zones that the current exact menu cannot satisfy.',
        '- the first floor cliff removes the relaxed 19–32 suffix; the second cliff removes the entire non-precision band 8–18; the third cliff removes the final singleton point at dwell 2.',
        '- this makes guarantee-first dwell search explicit: strong floors are not just more expensive, they also leave much less legal dwell space.',
        '',
        '## Sources',
    ])
    for src in summary['source_reports']:
        lines.append(f'- `{src}`')
    return '\n'.join(lines) + '\n'


def main() -> None:
    topology = _load(TOPOLOGY_REPORT)
    rows = _support_rows()
    summary = {
        'focus': 'Turn the exact uncertainty menu into a floor-conditioned dwell support ladder so inheritors can prune impossible dwell search regions immediately from the required worst-case preserved-gain floor.',
        'decision_rules': [
            'Use the required worst-case preserved-gain floor first, before cap or slack tuning, because floor tightening removes whole exact dwell regions at known certified cliffs.',
            'If the required floor exceeds 0.870482, skip dwell 19 through 32 entirely: that relaxed suffix belongs only to the exact 0.85 lane.',
            'If the required floor exceeds 0.980481, skip dwell 8 through 18 as well: the current exact menu then leaves only the singleton precision point at dwell 2.',
            'Treat floor demands above 0.999822 as leaving no current exact dwell support at all until new frontier evidence is generated.',
            'Keep the existing internal exact gap [3, 7] in mind even when the floor is loose: the widest current support is still {2} union [8, 32], not a continuous interval starting at 2.',
        ],
        'headline_findings': _headline_findings(rows),
        'support_rows': rows,
        'topology_crosscheck': {
            'exact_covered_dwell_intervals_unique_appends': topology['headline_findings']['exact_covered_dwell_intervals_unique_appends'],
            'exact_precision_band_is_isolated': topology['headline_findings']['exact_precision_band_is_isolated'],
            'next_exact_non_precision_band_starts_at_unique_appends': topology['headline_findings']['next_exact_non_precision_band_starts_at_unique_appends'],
            'largest_internal_exact_dwell_gap_unique_appends': topology['headline_findings']['largest_internal_exact_dwell_gap_unique_appends'],
        },
        'source_reports': [
            str(GUARANTEE_REPORT.relative_to(ROOT)),
            str(TOLERANCE_REPORT.relative_to(ROOT)),
            str(TOPOLOGY_REPORT.relative_to(ROOT)),
            str(CANONICAL_REPORT.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }
    OUT_JSON.write_text(json.dumps(summary, indent=2) + '\n')
    OUT_MD.write_text(_render_md(summary))
    print(str(OUT_JSON.relative_to(ROOT)))
    print(str(OUT_MD.relative_to(ROOT)))


if __name__ == '__main__':
    main()
