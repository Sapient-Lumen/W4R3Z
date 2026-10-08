#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_anchor_routes import (
    ANCHOR_DWELLS,
    plan_anchor_route,
)
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_canonical_anchor_path_atlas_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_canonical_anchor_path_atlas_snapshot_20260308.md'
BOUNDARY_PROTOCOL_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_boundary_stabilization_protocol_snapshot_20260308.json'
COMPASS_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_retuning_compass_snapshot_20260308.json'
UPGRADE_BOUNDARY_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_upgrade_boundary_targets_snapshot_20260308.json'
RELAXATION_BOUNDARY_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_relaxation_boundary_targets_snapshot_20260308.json'
ANCHOR_LABEL_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_canonical_anchor_labels_snapshot_20260308.json'

ORDERED_TIERS = ['near_exact', 'near_optimal', 'lower_guarantee']


def _route_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for start_tier in ORDERED_TIERS:
        for end_tier in ORDERED_TIERS:
            if start_tier == end_tier:
                continue
            rows.append(plan_anchor_route(start_tier, end_tier))
    return rows


def _headline(route_rows: list[dict[str, Any]]) -> dict[str, Any]:
    route_by_pair = {(row['start_tier'], row['end_tier']): row for row in route_rows}
    unique_totals = sorted({row['total_absolute_dwell_shift_unique_appends'] for row in route_rows})
    transient_nodes = sorted({
        dwell
        for row in route_rows
        for dwell in row['touches_transient_boundaries_unique_appends']
    })
    return {
        'canonical_anchor_targets_unique_appends': [ANCHOR_DWELLS[tier] for tier in ORDERED_TIERS],
        'ordered_distinct_anchor_routes': len(route_rows),
        'unique_total_shift_values_unique_appends': unique_totals,
        'adjacent_pair_total_shifts_unique_appends': {
            'near_exact_to_near_optimal': route_by_pair[('near_exact', 'near_optimal')]['total_absolute_dwell_shift_unique_appends'],
            'near_optimal_to_near_exact': route_by_pair[('near_optimal', 'near_exact')]['total_absolute_dwell_shift_unique_appends'],
            'near_optimal_to_lower_guarantee': route_by_pair[('near_optimal', 'lower_guarantee')]['total_absolute_dwell_shift_unique_appends'],
            'lower_guarantee_to_near_optimal': route_by_pair[('lower_guarantee', 'near_optimal')]['total_absolute_dwell_shift_unique_appends'],
        },
        'outer_pair_total_shift_unique_appends': route_by_pair[('near_exact', 'lower_guarantee')]['total_absolute_dwell_shift_unique_appends'],
        'outer_pair_total_shift_is_symmetric': route_by_pair[('near_exact', 'lower_guarantee')]['total_absolute_dwell_shift_unique_appends'] == route_by_pair[('lower_guarantee', 'near_exact')]['total_absolute_dwell_shift_unique_appends'],
        'outer_pair_phase_count_asymmetry': {
            'near_exact_to_lower_guarantee': route_by_pair[('near_exact', 'lower_guarantee')]['step_count'],
            'lower_guarantee_to_near_exact': route_by_pair[('lower_guarantee', 'near_exact')]['step_count'],
        },
        'strengthening_routes_to_precision_collapse_directly': all(
            route_by_pair[(start_tier, 'near_exact')]['route_unique_appends'][-1] == 2
            and route_by_pair[(start_tier, 'near_exact')]['step_count'] == 1
            for start_tier in ['near_optimal', 'lower_guarantee']
        ),
        'weakening_from_precision_starts_at_boundary_8': all(
            route_by_pair[('near_exact', end_tier)]['route_unique_appends'][1] == 8
            for end_tier in ['near_optimal', 'lower_guarantee']
        ),
        'weakening_to_lower_guarantee_requires_boundary_19_before_anchor_25': route_by_pair[('near_exact', 'lower_guarantee')]['route_unique_appends'][-2:] == [19, 25],
        'unique_transient_boundary_nodes_unique_appends': transient_nodes,
    }


def _decision_rules() -> list[str]:
    return [
        'Use the canonical-anchor path atlas when the archive wants to change steady exact-uncertainty modes under the current saved menu without reopening full dwell search.',
        'Weakening out of precision always widens through boundary 8 first; do not try to jump directly from anchor 2 to anchor 25.',
        'Weakening into the relaxed suffix enters boundary 19 before recentering to anchor 25.',
        'Strengthening to precision collapses directly to anchor 2 from either anchor 13 or anchor 25; no intermediate neutral-band anchor is required.',
        'Adjacent anchor changes cost exact total shifts of 11 appends for the precision/non-fragile pair and 12 appends for the non-fragile/relaxed pair.',
        'These routes are exact only for the current saved menu and should be regenerated if the dwell support, floor cliffs, or canonical anchors change.',
    ]


def _examples() -> list[dict[str, Any]]:
    labels = [
        ('near_exact', 'near_optimal', 'precision_weakening_to_non_fragile_anchor'),
        ('near_exact', 'lower_guarantee', 'precision_full_relaxation_to_relaxed_anchor'),
        ('lower_guarantee', 'near_exact', 'relaxed_suffix_high_floor_collapse_to_precision'),
        ('lower_guarantee', 'near_optimal', 'relaxed_suffix_strengthening_to_non_fragile_anchor'),
    ]
    examples = []
    for start_tier, end_tier, label in labels:
        route = plan_anchor_route(start_tier, end_tier)
        examples.append(
            {
                'example_label': label,
                'start_tier': start_tier,
                'end_tier': end_tier,
                'route_unique_appends': route['route_unique_appends'],
                'step_count': route['step_count'],
                'total_absolute_dwell_shift_unique_appends': route['total_absolute_dwell_shift_unique_appends'],
            }
        )
    return examples


def _build_report() -> dict[str, Any]:
    route_rows = _route_rows()
    return {
        'focus': 'Turn one-shot steady-mode retuning among canonical exact-uncertainty anchors into a tiny exact route atlas so inheritors can react to floor changes without reopening the full dwell frontier.',
        'headline_findings': _headline(route_rows),
        'decision_rules': _decision_rules(),
        'route_rows': route_rows,
        'examples': _examples(),
        'source_reports': [
            str(BOUNDARY_PROTOCOL_REPORT.relative_to(ROOT)),
            str(COMPASS_REPORT.relative_to(ROOT)),
            str(UPGRADE_BOUNDARY_REPORT.relative_to(ROOT)),
            str(RELAXATION_BOUNDARY_REPORT.relative_to(ROOT)),
            str(ANCHOR_LABEL_REPORT.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty canonical-anchor path atlas snapshot — 2026-03-08')
    lines.append('')
    lines.append(f"Focus: {report['focus']}")
    lines.append('')
    lines.append('## Headline findings')
    for key, value in report['headline_findings'].items():
        lines.append(f'- **{key}**: `{json.dumps(value, ensure_ascii=False)}`')
    lines.append('')
    lines.append('## Route rows')
    for row in report['route_rows']:
        lines.append(
            '- '
            f"`{row['start_tier']}` → `{row['end_tier']}` uses route `{row['route_unique_appends']}`; "
            f"steps `{row['step_count']}`; total shift `{row['total_absolute_dwell_shift_unique_appends']}`; transient boundaries `{row['touches_transient_boundaries_unique_appends']}`"
        )
        for step in row['steps']:
            lines.append(
                '  - '
                f"`{step['phase_label']}`: `{step['from_dwell_unique_appends']}→{step['to_dwell_unique_appends']}` "
                f"as `{step['phase_type']}` with shift `{step['absolute_dwell_shift_unique_appends']}`"
            )
    lines.append('')
    lines.append('## Decision rules')
    for rule in report['decision_rules']:
        lines.append(f'- {rule}')
    lines.append('')
    lines.append('## Examples')
    for row in report['examples']:
        lines.append(f"- {row['example_label']}: `{json.dumps(row, ensure_ascii=False)}`")
    lines.append('')
    lines.append('## Source reports')
    for path in report['source_reports']:
        lines.append(f'- `{path}`')
    lines.append('')
    lines.append(f"Source script: `{report['source_script']}`")
    return '\n'.join(lines) + '\n'


def main() -> None:
    report = _build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(report), encoding='utf-8')
    print(f'wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'wrote {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
