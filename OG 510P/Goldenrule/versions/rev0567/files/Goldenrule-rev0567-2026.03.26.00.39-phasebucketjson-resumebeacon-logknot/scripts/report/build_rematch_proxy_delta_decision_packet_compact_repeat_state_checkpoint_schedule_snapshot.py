#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GROWTH_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_growth_snapshot_20260307.json'
OPERATING_MODES_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_operating_modes_snapshot_20260308.json'
TRANSITION_BUDGET_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_transition_budget_snapshot_20260307.json'
UNCERTAINTY_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_repeat_uncertainty_snapshot_20260307.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_checkpoint_schedule_snapshot_20260308.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_checkpoint_schedule_snapshot_20260308.md'
REFERENCE_GAIN_SHARES = [0.95, 0.85]


INTERVAL_RE = re.compile(r'(?P<kind>[a-z\-]+) (?P<start>\d+)–(?P<end>\d+)$')


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text())


def _parse_interval_summary(interval_summary: str) -> list[dict[str, object]]:
    rows = []
    for chunk in interval_summary.split('; '):
        match = INTERVAL_RE.fullmatch(chunk)
        if match is None:
            raise ValueError(f'unexpected interval chunk: {chunk!r}')
        rows.append(
            {
                'state_kind_label': match.group('kind'),
                'start_unique_appends': int(match.group('start')),
                'end_unique_appends': int(match.group('end')),
            }
        )
    return rows



def _interval_transition_boundaries(interval_summary: str) -> list[int]:
    interval_rows = _parse_interval_summary(interval_summary)
    return [row['start_unique_appends'] for row in interval_rows[1:]]



def _mode_boundary_row(
    label: str,
    anchor_row: dict[str, object],
    *,
    minimum_gain_share_of_full_dynamic_savings: float,
    minimum_dwell_unique_appends: int,
) -> dict[str, object]:
    transition_boundaries = _interval_transition_boundaries(anchor_row['interval_summary'])
    return {
        'mode': label,
        'minimum_gain_share_of_full_dynamic_savings': minimum_gain_share_of_full_dynamic_savings,
        'minimum_dwell_unique_appends': minimum_dwell_unique_appends,
        'expected_repeat_lookups': anchor_row['expected_repeat_lookups'],
        'selected_transition_count': anchor_row['selected_transition_count'],
        'gain_share_of_full_dynamic_savings': anchor_row['gain_share_of_full_dynamic_savings'],
        'transition_boundaries_unique_appends': transition_boundaries,
        'interval_summary': anchor_row['interval_summary'],
    }



def _build_summary() -> dict[str, object]:
    growth = _load_json(GROWTH_REPORT)
    operating = _load_json(OPERATING_MODES_REPORT)
    transition_budget = _load_json(TRANSITION_BUDGET_REPORT)
    uncertainty = _load_json(UNCERTAINTY_REPORT)

    page_birth_rows = [row for row in growth['event_rows'] if 'new_page_birth' in row['event_kinds']]
    page_birth_checkpoints = [row['unique_append_count'] for row in page_birth_rows]
    page_birth_spacings = [
        page_birth_checkpoints[index + 1] - page_birth_checkpoints[index]
        for index in range(len(page_birth_checkpoints) - 1)
    ]
    priority_checkpoint_rows = [
        {
            'unique_append_count': row['unique_append_count'],
            'event_kinds': row['event_kinds'],
            'page_count': row['page_count'],
            'route_block_bitmap_len': row['route_block_bitmap_len'],
            'filter_minus_route_compact_state_bytes': row['filter_minus_route_compact_state_bytes'],
        }
        for row in growth['event_rows']
        if any(kind in {'filter_route_state_order_flip', 'route_block_bitmap_cliff'} for kind in row['event_kinds'])
    ]
    priority_checkpoints = [row['unique_append_count'] for row in priority_checkpoint_rows]

    operating_row_by_mode = {row['mode']: row for row in operating['operating_rows']}
    default_mode = operating_row_by_mode['uncertainty_robust_default']
    simplicity_mode = operating_row_by_mode['uncertainty_robust_simplicity']
    rewrite_budget_mode = operating_row_by_mode['rewrite_budgeted']

    uncertainty_row_by_gain = {
        row['minimum_gain_share_of_full_dynamic_savings']: row
        for row in uncertainty['uncertainty_rows']
    }
    mode_boundary_rows = []
    uncertainty_mode_rows = []
    for minimum_gain_share in REFERENCE_GAIN_SHARES:
        uncertainty_row = uncertainty_row_by_gain[minimum_gain_share]
        boundary_rows = [
            _mode_boundary_row(
                'uncertainty_robust_default' if minimum_gain_share == 0.95 else 'uncertainty_robust_simplicity',
                anchor_row,
                minimum_gain_share_of_full_dynamic_savings=minimum_gain_share,
                minimum_dwell_unique_appends=uncertainty_row['anchor_minimum_dwell_unique_appends'],
            )
            for anchor_row in uncertainty_row['anchor_rows']
        ]
        union_checkpoints = sorted(
            {
                checkpoint
                for boundary_row in boundary_rows
                for checkpoint in boundary_row['transition_boundaries_unique_appends']
            }
        )
        mode_boundary_rows.extend(boundary_rows)
        uncertainty_mode_rows.append(
            {
                'mode': 'uncertainty_robust_default' if minimum_gain_share == 0.95 else 'uncertainty_robust_simplicity',
                'minimum_gain_share_of_full_dynamic_savings': minimum_gain_share,
                'minimum_dwell_unique_appends': uncertainty_row['anchor_minimum_dwell_unique_appends'],
                'repeat_band_start_expected_repeat_lookups': uncertainty_row['expected_repeat_lookups_start'],
                'repeat_band_end_expected_repeat_lookups': uncertainty_row['expected_repeat_lookups_end'],
                'minimum_selected_transition_count': uncertainty_row['minimum_selected_transition_count'],
                'maximum_selected_transition_count': uncertainty_row['maximum_selected_transition_count'],
                'union_transition_checkpoints_unique_appends': union_checkpoints,
                'union_transition_checkpoint_count': len(union_checkpoints),
            }
        )

    rewrite_budget_frontier_row = next(
        row for row in transition_budget['frontier_rows'] if row['selected_transition_count'] == 4
    )
    rewrite_budget_transition_checkpoints = _interval_transition_boundaries(
        rewrite_budget_frontier_row['interval_summary']
    )

    findings = {
        'first_page_birth_unique_appends': page_birth_checkpoints[0],
        'routine_page_birth_spacing_unique_appends': page_birth_spacings[0],
        'mandatory_structural_checkpoints_unique_appends': priority_checkpoints,
        'default_robust_minimum_dwell_unique_appends': default_mode['key_measure']['anchor_minimum_dwell_unique_appends'],
        'default_robust_union_transition_checkpoints_unique_appends': uncertainty_mode_rows[0]['union_transition_checkpoints_unique_appends'],
        'default_robust_union_transition_checkpoint_count': uncertainty_mode_rows[0]['union_transition_checkpoint_count'],
        'simplicity_robust_minimum_dwell_unique_appends': simplicity_mode['key_measure']['anchor_minimum_dwell_unique_appends'],
        'simplicity_robust_union_transition_checkpoints_unique_appends': uncertainty_mode_rows[1]['union_transition_checkpoints_unique_appends'],
        'simplicity_robust_union_transition_checkpoint_count': uncertainty_mode_rows[1]['union_transition_checkpoint_count'],
        'rewrite_budget_transition_count': rewrite_budget_mode['key_measure']['practical_transition_budget_ceiling'],
        'rewrite_budget_transition_checkpoints_unique_appends': rewrite_budget_transition_checkpoints,
        'first_route_block_bitmap_cliff_unique_appends': priority_checkpoints[1],
        'second_route_block_bitmap_cliff_unique_appends': priority_checkpoints[3],
        'main_rule': 'pre-register a small checkpoint set per operating mode: use routine page-birth checks for sparse maintenance, never skip the structural flip-and-cliff checkpoints, and avoid per-append sidecar reconsideration.',
    }

    return {
        'focus': 'Compile compact repeat-sidecar reevaluation into a finite checkpoint schedule so the inheritor can maintain the archive with sparse triggers instead of reconsidering every append.',
        'headline_findings': findings,
        'routine_page_birth_checkpoints_unique_appends': page_birth_checkpoints,
        'priority_checkpoint_rows': priority_checkpoint_rows,
        'uncertainty_mode_rows': uncertainty_mode_rows,
        'mode_boundary_rows': mode_boundary_rows,
        'rewrite_budget_row': {
            'selected_transition_count': rewrite_budget_frontier_row['selected_transition_count'],
            'gain_share_of_full_dynamic_savings': rewrite_budget_frontier_row['gain_share_of_full_dynamic_savings'],
            'transition_boundaries_unique_appends': rewrite_budget_transition_checkpoints,
            'interval_summary': rewrite_budget_frontier_row['interval_summary'],
        },
        'source_reports': [
            str(GROWTH_REPORT.relative_to(ROOT)),
            str(OPERATING_MODES_REPORT.relative_to(ROOT)),
            str(TRANSITION_BUDGET_REPORT.relative_to(ROOT)),
            str(UNCERTAINTY_REPORT.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }



def _render_md(report: dict[str, object]) -> str:
    findings = report['headline_findings']
    lines = [
        '# Rematch Proxy Delta Decision Packet Compact Repeat-State Checkpoint Schedule Snapshot — 2026-03-08',
        '',
        '## Focus',
        f"- {report['focus']}",
        '',
        '## Headline findings',
        f"- routine page births arrive every `{findings['routine_page_birth_spacing_unique_appends']}` unique appends starting at `{findings['first_page_birth_unique_appends']}`.",
        f"- the uncertainty-robust default dwell-`{findings['default_robust_minimum_dwell_unique_appends']}` preset only ever needs `{findings['default_robust_union_transition_checkpoint_count']}` possible transition checkpoints across the whole `0.15`–`0.25` repeat band: `{findings['default_robust_union_transition_checkpoints_unique_appends']}`.",
        f"- the broader simplicity-first dwell-`{findings['simplicity_robust_minimum_dwell_unique_appends']}` preset compresses that to `{findings['simplicity_robust_union_transition_checkpoint_count']}` possible checkpoints: `{findings['simplicity_robust_union_transition_checkpoints_unique_appends']}`.",
        f"- the practical `{findings['rewrite_budget_transition_count']}`-transition mode at the focal `0.18` repeat horizon rewrites only at `{findings['rewrite_budget_transition_checkpoints_unique_appends']}` while still preserving `0.968419` of the full dynamic savings.",
        f"- the mandatory structural checkpoints are `{findings['mandatory_structural_checkpoints_unique_appends']}` because those are the measured filter/route order flips and route-block bitmap cliffs.",
        f"- the first two route-block bitmap cliffs land at `{findings['first_route_block_bitmap_cliff_unique_appends']}` and `{findings['second_route_block_bitmap_cliff_unique_appends']}`.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Routine maintenance cadence',
        f"- page births provide a natural sparse baseline: `{report['routine_page_birth_checkpoints_unique_appends']}`.",
        f"- that spacing is already at least as wide as the current robust dwell presets (`{findings['default_robust_minimum_dwell_unique_appends']}` and `{findings['simplicity_robust_minimum_dwell_unique_appends']}`), so the archive does not need per-append polling just to respect the anti-churn presets.",
        '',
        '## Mandatory structural checkpoints',
        '| unique appends | event kinds | page count | route-block bitmap bytes | filter minus route compact-state bytes | why it matters |',
        '|---:|---|---:|---:|---:|---|',
    ]
    why_by_checkpoint = {
        79: 'route blocks first become state-cheaper than filters before the bitmap cliff.',
        111: 'the first route-block bitmap cliff lands and flips the compact-state order back toward filters.',
        191: 'route blocks regain the compact-state lead before the second bitmap cliff.',
        239: 'the second bitmap cliff lands and flips the compact-state order back toward filters.',
    }
    for row in report['priority_checkpoint_rows']:
        lines.append(
            f"| {row['unique_append_count']} | {', '.join(row['event_kinds'])} | {row['page_count']} | {row['route_block_bitmap_len']} | {row['filter_minus_route_compact_state_bytes']} | {why_by_checkpoint[row['unique_append_count']]} |"
        )
    lines.extend([
        '',
        '## Uncertainty-robust transition checkpoint unions',
        '| mode | dwell | repeat band | transition range | union checkpoints |',
        '|---|---:|---|---|---|',
    ])
    for row in report['uncertainty_mode_rows']:
        lines.append(
            f"| {row['mode']} | {row['minimum_dwell_unique_appends']} | {row['repeat_band_start_expected_repeat_lookups']}–{row['repeat_band_end_expected_repeat_lookups']} | {row['minimum_selected_transition_count']}–{row['maximum_selected_transition_count']} | {row['union_transition_checkpoints_unique_appends']} |"
        )
    lines.extend([
        '',
        '## Checkpoints by repeat budget inside the uncertainty band',
        '| mode | repeat budget | selected transitions | checkpoints | summary |',
        '|---|---:|---:|---|---|',
    ])
    for row in report['mode_boundary_rows']:
        lines.append(
            f"| {row['mode']} | {row['expected_repeat_lookups']} | {row['selected_transition_count']} | {row['transition_boundaries_unique_appends']} | {row['interval_summary']} |"
        )
    lines.extend([
        '',
        '## Practical rewrite-budgeted checkpoints',
        f"- selected transitions: `{report['rewrite_budget_row']['selected_transition_count']}`.",
        f"- checkpoints: `{report['rewrite_budget_row']['transition_boundaries_unique_appends']}`.",
        f"- summary: `{report['rewrite_budget_row']['interval_summary']}`.",
        '',
        '## Sources',
    ])
    lines.extend(f"- `{path}`" for path in report['source_reports'])
    return '\n'.join(lines) + '\n'



def main() -> None:
    report = _build_summary()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    OUT_MD.write_text(_render_md(report))
    print(f'wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'wrote {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
