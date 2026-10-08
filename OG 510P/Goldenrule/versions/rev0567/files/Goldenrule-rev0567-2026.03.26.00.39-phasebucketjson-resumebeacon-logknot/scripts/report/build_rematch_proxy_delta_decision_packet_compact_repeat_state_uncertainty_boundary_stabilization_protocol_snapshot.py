#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_boundary_stabilization_protocol_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_boundary_stabilization_protocol_snapshot_20260308.md'
COMPASS_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_retuning_compass_snapshot_20260308.json'
ANCHOR_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_canonical_anchor_labels_snapshot_20260308.json'
ATLAS_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_target_dwell_atlas_snapshot_20260308.json'


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def _build_band_rows() -> list[dict[str, Any]]:
    anchors = _load(ANCHOR_REPORT)
    atlas = _load(ATLAS_REPORT)

    anchor_rows = {row['tier']: row for row in anchors['tier_rows']}
    atlas_rows = {row['region_label']: row for row in atlas['atlas_rows']}

    near_exact = anchor_rows['near_exact']
    near_optimal = anchor_rows['near_optimal']
    lower_guarantee = anchor_rows['lower_guarantee']

    return [
        {
            'tier': 'near_exact',
            'region_label': '{2}',
            'canonical_anchor_minimum_dwell_unique_appends': near_exact['canonical_anchor_minimum_dwell_unique_appends'],
            'support_boundaries_unique_appends': [2],
            'boundary_to_anchor_recentering_distances_unique_appends': [0],
            'maximum_boundary_to_anchor_recentering_distance_unique_appends': 0,
            'exact_floor_ceiling': atlas_rows['{2}']['maximum_actual_certified_gain_share_floor_of_full_dynamic_savings'],
            'exact_hard_cap': atlas_rows['{2}']['exact_hard_cap'],
            'main_rule': 'Precision singleton 2 is already both the feasibility-restoring boundary and the canonical steady-mode anchor.',
        },
        {
            'tier': 'near_optimal',
            'region_label': '[8, 18]',
            'canonical_anchor_minimum_dwell_unique_appends': near_optimal['canonical_anchor_minimum_dwell_unique_appends'],
            'support_boundaries_unique_appends': [8, 18],
            'boundary_to_anchor_recentering_distances_unique_appends': [
                near_optimal['canonical_anchor_minimum_dwell_unique_appends'] - 8,
                18 - near_optimal['canonical_anchor_minimum_dwell_unique_appends'],
            ],
            'maximum_boundary_to_anchor_recentering_distance_unique_appends': 18 - near_optimal['canonical_anchor_minimum_dwell_unique_appends'],
            'exact_floor_ceiling': atlas_rows['[8, 18]']['maximum_actual_certified_gain_share_floor_of_full_dynamic_savings'],
            'exact_hard_cap': atlas_rows['[8, 18]']['exact_hard_cap'],
            'main_rule': 'Boundary landings 8 and 18 are first-step repairs only; if the strong non-fragile band becomes the new steady mode, stabilize inward to canonical anchor 13.',
        },
        {
            'tier': 'lower_guarantee',
            'region_label': '[19, 32]',
            'canonical_anchor_minimum_dwell_unique_appends': lower_guarantee['canonical_anchor_minimum_dwell_unique_appends'],
            'support_boundaries_unique_appends': [19, 32],
            'boundary_to_anchor_recentering_distances_unique_appends': [
                lower_guarantee['canonical_anchor_minimum_dwell_unique_appends'] - 19,
                32 - lower_guarantee['canonical_anchor_minimum_dwell_unique_appends'],
            ],
            'maximum_boundary_to_anchor_recentering_distance_unique_appends': 32 - lower_guarantee['canonical_anchor_minimum_dwell_unique_appends'],
            'entry_boundary_to_anchor_recentering_distance_unique_appends': lower_guarantee['canonical_anchor_minimum_dwell_unique_appends'] - 19,
            'exact_floor_ceiling': atlas_rows['[19, 32]']['maximum_actual_certified_gain_share_floor_of_full_dynamic_savings'],
            'exact_hard_cap': atlas_rows['[19, 32]']['exact_hard_cap'],
            'main_rule': 'If the relaxed suffix becomes the new steady mode after a weakening step, the first stable representative is canonical anchor 25, reached by recentering 6 steps inward from entry boundary 19.',
        },
    ]


def _protocol_rows() -> list[dict[str, Any]]:
    compass = _load(COMPASS_REPORT)
    transitions = {(row['direction'], row['start_region_label'], row['target_floor_interval']): row for row in compass['transition_rows']}
    anchors = {row['tier']: row['canonical_anchor_minimum_dwell_unique_appends'] for row in _load(ANCHOR_REPORT)['tier_rows']}

    return [
        {
            'protocol_label': 'strengthen_relaxed_suffix_to_neutral_band',
            'direction': 'strengthen',
            'start_region_label': '[19, 32]',
            'required_floor_interval_after_change': '(0.870482, 0.980481]',
            'first_boundary_target_unique_appends': transitions[('strengthen', '[19, 32]', '(0.870482, 0.980481]')]['first_compass_target_unique_appends'],
            'destination_region_label': '[8, 18]',
            'canonical_anchor_target_unique_appends': anchors['near_optimal'],
            'optional_recentering_distance_unique_appends': transitions[('strengthen', '[19, 32]', '(0.870482, 0.980481]')]['first_compass_target_unique_appends'] - anchors['near_optimal'],
            'steady_mode_rule': 'Jump to 18 to restore support under the stronger floor; if the neutral band is now the steady operating mode, recenter to 13.',
        },
        {
            'protocol_label': 'strengthen_any_live_region_to_precision_singleton',
            'direction': 'strengthen',
            'start_region_label': '[8, 18] or [19, 32]',
            'required_floor_interval_after_change': '(0.980481, 0.999822]',
            'first_boundary_target_unique_appends': 2,
            'destination_region_label': '{2}',
            'canonical_anchor_target_unique_appends': anchors['near_exact'],
            'optional_recentering_distance_unique_appends': 0,
            'steady_mode_rule': 'Dwell 2 is already both the first surviving support point and the stable precision anchor.',
        },
        {
            'protocol_label': 'weaken_precision_to_neutral_band',
            'direction': 'weaken',
            'start_region_label': '{2}',
            'required_floor_interval_after_change': '(0.870482, 0.980481]',
            'first_boundary_target_unique_appends': transitions[('weaken', '{2}', '(0.870482, 0.980481]')]['first_compass_target_unique_appends'],
            'destination_region_label': '[8, 18]',
            'canonical_anchor_target_unique_appends': anchors['near_optimal'],
            'optional_recentering_distance_unique_appends': anchors['near_optimal'] - transitions[('weaken', '{2}', '(0.870482, 0.980481]')]['first_compass_target_unique_appends'],
            'steady_mode_rule': 'Jump to 8 to regain non-fragile support; if the neutral band is now the steady operating mode, recenter to 13.',
        },
        {
            'protocol_label': 'weaken_neutral_band_to_relaxed_suffix',
            'direction': 'weaken',
            'start_region_label': '[8, 18]',
            'required_floor_interval_after_change': '[0, 0.870482]',
            'first_boundary_target_unique_appends': transitions[('weaken', '[8, 18]', '[0, 0.870482]')]['first_compass_target_unique_appends'],
            'destination_region_label': '[19, 32]',
            'canonical_anchor_target_unique_appends': anchors['lower_guarantee'],
            'optional_recentering_distance_unique_appends': anchors['lower_guarantee'] - transitions[('weaken', '[8, 18]', '[0, 0.870482]')]['first_compass_target_unique_appends'],
            'steady_mode_rule': 'Jump to 19 to enter the relaxed suffix; if that suffix is now the steady operating mode, recenter to 25.',
        },
    ]


def _headline_findings(band_rows: list[dict[str, Any]], protocol_rows: list[dict[str, Any]]) -> dict[str, Any]:
    band_rows_by_tier = {row['tier']: row for row in band_rows}
    optional_recentering = [row['optional_recentering_distance_unique_appends'] for row in protocol_rows]
    return {
        'main_rule': 'Repair floor-driven exact uncertainty changes at the nearest surviving support boundary first, then recenter to the canonical anchor only if that destination band becomes the new steady operating mode.',
        'canonical_anchor_targets_unique_appends': [2, 13, 25],
        'first_step_boundary_targets_unique_appends': [2, 8, 18, 19],
        'precision_singleton_needs_no_recentering': True,
        'neutral_band_boundary_to_anchor_recentering_is_symmetric': band_rows_by_tier['near_optimal']['boundary_to_anchor_recentering_distances_unique_appends'] == [5, 5],
        'neutral_band_boundary_to_anchor_recentering_distance_unique_appends': 5,
        'relaxed_suffix_entry_boundary_to_anchor_recentering_distance_unique_appends': band_rows_by_tier['lower_guarantee']['entry_boundary_to_anchor_recentering_distance_unique_appends'],
        'maximum_optional_recentering_distance_unique_appends': max(optional_recentering),
        'all_steady_mode_recentering_targets_are_canonical_anchors': True,
        'boundary_landings_8_18_19_are_transient_by_default': True,
    }


def _decision_rules() -> list[str]:
    return [
        'Use the four-point boundary compass `{2, 8, 18, 19}` for the first repair step whenever a floor change makes the current dwell region infeasible or newly over-constrained.',
        'Treat boundary landings `8`, `18`, and `19` as transient feasibility-restoring points by default rather than as stable inheritor-facing operating labels.',
        'If the destination band will become the new steady operating mode, stabilize inward to its canonical anchor: `13` for `[8,18]`, `25` for `[19,32]`, and `2` for `{2}`.',
        'The near-optimal band has symmetric stabilization cost: both boundary repairs `8→13` and `18→13` cost exactly 5 dwell steps.',
        'The relaxed suffix stabilizes from its entry boundary as `19→25`, costing 6 dwell steps; precision singleton `2` needs no stabilization step because boundary and anchor coincide.',
        'Do not force this protocol when dwell is physically fixed by deployment constraints; in that case the fixed-dwell ceiling and oracle cards remain the correct tools.',
    ]


def _examples() -> list[dict[str, Any]]:
    return [
        {
            'example_label': 'relaxed_suffix_strengthens_then_recenters_to_13',
            'start_dwell_unique_appends': 25,
            'required_floor_interval_after_change': '(0.870482, 0.980481]',
            'first_boundary_target_unique_appends': 18,
            'steady_mode_anchor_unique_appends': 13,
        },
        {
            'example_label': 'precision_weakens_then_recenters_to_13',
            'start_dwell_unique_appends': 2,
            'required_floor_interval_after_change': '(0.870482, 0.980481]',
            'first_boundary_target_unique_appends': 8,
            'steady_mode_anchor_unique_appends': 13,
        },
        {
            'example_label': 'neutral_band_weakens_then_recenters_to_25',
            'start_dwell_unique_appends': 13,
            'required_floor_interval_after_change': '[0, 0.870482]',
            'first_boundary_target_unique_appends': 19,
            'steady_mode_anchor_unique_appends': 25,
        },
        {
            'example_label': 'high_floor_strengthening_stops_at_2',
            'start_dwell_unique_appends': 13,
            'required_floor_interval_after_change': '(0.980481, 0.999822]',
            'first_boundary_target_unique_appends': 2,
            'steady_mode_anchor_unique_appends': 2,
        },
    ]


def _build_report() -> dict[str, Any]:
    band_rows = _build_band_rows()
    protocol_rows = _protocol_rows()
    return {
        'focus': 'Turn the boundary compass plus canonical anchor labels into a two-phase stabilization protocol: repair feasibility at the right support boundary first, then recenter to the destination band\'s canonical anchor only if that band becomes the new steady mode.',
        'headline_findings': _headline_findings(band_rows, protocol_rows),
        'decision_rules': _decision_rules(),
        'band_rows': band_rows,
        'protocol_rows': protocol_rows,
        'examples': _examples(),
        'source_reports': [
            str(COMPASS_REPORT.relative_to(ROOT)),
            str(ANCHOR_REPORT.relative_to(ROOT)),
            str(ATLAS_REPORT.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty boundary-stabilization protocol snapshot — 2026-03-08')
    lines.append('')
    lines.append(f"Focus: {report['focus']}")
    lines.append('')
    lines.append('## Headline findings')
    for key, value in report['headline_findings'].items():
        lines.append(f'- **{key}**: `{json.dumps(value, ensure_ascii=False)}`')
    lines.append('')
    lines.append('## Band rows')
    for row in report['band_rows']:
        lines.append(
            '- '
            f"tier `{row['tier']}` in `{row['region_label']}`; canonical anchor `{row['canonical_anchor_minimum_dwell_unique_appends']}`; "
            f"boundaries `{row['support_boundaries_unique_appends']}`; boundary-to-anchor recenter `{row['boundary_to_anchor_recentering_distances_unique_appends']}`"
        )
    lines.append('')
    lines.append('## Protocol rows')
    for row in report['protocol_rows']:
        lines.append(
            '- '
            f"{row['protocol_label']}`: boundary `{row['first_boundary_target_unique_appends']}` then steady-mode anchor `{row['canonical_anchor_target_unique_appends']}`; "
            f"optional recenter `{row['optional_recentering_distance_unique_appends']}`"
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
