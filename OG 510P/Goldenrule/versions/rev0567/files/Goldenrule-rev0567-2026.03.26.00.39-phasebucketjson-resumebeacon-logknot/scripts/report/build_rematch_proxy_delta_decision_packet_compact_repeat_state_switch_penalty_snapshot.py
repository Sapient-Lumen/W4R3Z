#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_switch_penalty_snapshot_20260307.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_switch_penalty_snapshot_20260307.md'
FOCAL_EXPECTED_REPEAT_LOOKUPS = 0.18
FOCAL_TRANSITION_PENALTY_PER_SWITCH_BYTES = 927.685921
MAX_UNIQUE_APPENDS = 256


FRONTIER_ROWS = [
    {
        'transition_count': 12,
        'transition_penalty_start_bytes': 0.0,
        'transition_penalty_end_bytes': 1.979429,
        'cumulative_objective_without_transition_penalty': 4828958.842787,
        'state_counts': {
            'paged_catalog_only': 33,
            'paged_catalog_with_filters': 96,
            'paged_catalog_with_route_blocks': 128,
        },
        'summary': 'full exact downgrade/upgrade frontier with thirteen alternating bands',
    },
    {
        'transition_count': 11,
        'transition_penalty_start_bytes': 1.979429,
        'transition_penalty_end_bytes': 28.158238,
        'cumulative_objective_without_transition_penalty': 4828960.822216,
        'state_counts': {
            'paged_catalog_only': 32,
            'paged_catalog_with_filters': 97,
            'paged_catalog_with_route_blocks': 128,
        },
        'summary': 'drops the single-step bare-pages fallback at append 111',
    },
    {
        'transition_count': 9,
        'transition_penalty_start_bytes': 28.158238,
        'transition_penalty_end_bytes': 34.098996,
        'cumulative_objective_without_transition_penalty': 4829017.138691,
        'state_counts': {
            'paged_catalog_only': 38,
            'paged_catalog_with_filters': 91,
            'paged_catalog_with_route_blocks': 128,
        },
        'summary': 'coalesces the earliest two bare-page micro-bands',
    },
    {
        'transition_count': 7,
        'transition_penalty_start_bytes': 34.098996,
        'transition_penalty_end_bytes': 45.40069,
        'cumulative_objective_without_transition_penalty': 4829085.336684,
        'state_counts': {
            'paged_catalog_only': 31,
            'paged_catalog_with_filters': 98,
            'paged_catalog_with_route_blocks': 128,
        },
        'summary': 'keeps only the later cliff-driven oscillations',
    },
    {
        'transition_count': 5,
        'transition_penalty_start_bytes': 45.40069,
        'transition_penalty_end_bytes': 134.276182,
        'cumulative_objective_without_transition_penalty': 4829176.138064,
        'state_counts': {
            'paged_catalog_only': 24,
            'paged_catalog_with_filters': 105,
            'paged_catalog_with_route_blocks': 128,
        },
        'summary': 'practical low-churn regime: pages, filters, route blocks, filters, route blocks, filters',
    },
    {
        'transition_count': 4,
        'transition_penalty_start_bytes': 134.276182,
        'transition_penalty_end_bytes': 1090.254986,
        'cumulative_objective_without_transition_penalty': 4829310.414246,
        'state_counts': {
            'paged_catalog_only': 56,
            'paged_catalog_with_filters': 66,
            'paged_catalog_with_route_blocks': 135,
        },
        'summary': 'robust mid-cost regime: stay bare until append 56, then route blocks, filters at the first cliff, route blocks, filters',
    },
    {
        'transition_count': 3,
        'transition_penalty_start_bytes': 1090.254986,
        'transition_penalty_end_bytes': 2005.364255,
        'cumulative_objective_without_transition_penalty': 4830400.669232,
        'state_counts': {
            'paged_catalog_only': 56,
            'paged_catalog_with_filters': 48,
            'paged_catalog_with_route_blocks': 153,
        },
        'summary': 'keep the first cliff fallback to filters, then stay on route blocks thereafter',
    },
    {
        'transition_count': 1,
        'transition_penalty_start_bytes': 2005.364255,
        'transition_penalty_end_bytes': 5679.676082,
        'cumulative_objective_without_transition_penalty': 4834411.397743,
        'state_counts': {
            'paged_catalog_only': 56,
            'paged_catalog_with_filters': 0,
            'paged_catalog_with_route_blocks': 201,
        },
        'summary': 'single front-loaded jump: bare pages through append 55, then route blocks forever',
    },
    {
        'transition_count': 0,
        'transition_penalty_start_bytes': 5679.676082,
        'transition_penalty_end_bytes': None,
        'cumulative_objective_without_transition_penalty': 4840091.073825,
        'state_counts': {
            'paged_catalog_only': 0,
            'paged_catalog_with_filters': 0,
            'paged_catalog_with_route_blocks': 257,
        },
        'summary': 'fully fixed policy: keep route blocks from the start',
    },
]

REFERENCE_TRANSITION_PENALTIES = [0.0, 50.0, 200.0, 927.685921, 1500.0, 3000.0, 6000.0]


def _select_frontier_row(transition_penalty_per_switch_bytes: float) -> dict[str, object]:
    selected = FRONTIER_ROWS[0]
    for row in FRONTIER_ROWS:
        start = row['transition_penalty_start_bytes']
        end = row['transition_penalty_end_bytes']
        if transition_penalty_per_switch_bytes >= start and (end is None or transition_penalty_per_switch_bytes < end):
            selected = row
            break
    return selected



def _reference_row(transition_penalty_per_switch_bytes: float) -> dict[str, object]:
    row = _select_frontier_row(transition_penalty_per_switch_bytes)
    total = round(
        row['cumulative_objective_without_transition_penalty']
        + transition_penalty_per_switch_bytes * row['transition_count'],
        6,
    )
    return {
        'transition_penalty_per_switch_bytes': transition_penalty_per_switch_bytes,
        'transition_count': row['transition_count'],
        'state_counts': row['state_counts'],
        'cumulative_objective_with_transition_penalty': total,
        'active_transition_penalty_start_bytes': row['transition_penalty_start_bytes'],
        'active_transition_penalty_end_bytes': row['transition_penalty_end_bytes'],
        'summary': row['summary'],
    }



def _build_summary() -> dict[str, object]:
    focal = _reference_row(FOCAL_TRANSITION_PENALTY_PER_SWITCH_BYTES)
    practical_rows = [
        row for row in FRONTIER_ROWS if row['transition_penalty_start_bytes'] >= 45.40069 or row['transition_penalty_start_bytes'] == 0.0
    ]
    return {
        'focus': 'Map compact repeat-sidecar staging onto an exact switch-penalty frontier so the archive can keep only the sidecar transitions whose byte savings still justify churn.',
        'packet_script': str(PACKET_PATH.relative_to(ROOT)),
        'max_unique_appends': MAX_UNIQUE_APPENDS,
        'focal_expected_repeat_lookups': FOCAL_EXPECTED_REPEAT_LOOKUPS,
        'focal_transition_penalty_per_switch_bytes': FOCAL_TRANSITION_PENALTY_PER_SWITCH_BYTES,
        'headline_findings': {
            'entry_count': 274,
            'page_count': 18,
            'tail_entry_count': 2,
            'route_block_bitmap_len': 3,
            'frontier_regime_count': len(FRONTIER_ROWS),
            'micro_churn_ceiling_bytes': 45.40069,
            'practical_regime_count_at_or_above_micro_churn_ceiling': len(practical_rows) - 1,
            'focal_transition_count': focal['transition_count'],
            'focal_cumulative_objective_with_transition_penalty': focal['cumulative_objective_with_transition_penalty'],
            'focal_advantage_vs_fixed_route_blocks_bytes': round(4840091.073825 - focal['cumulative_objective_with_transition_penalty'], 6),
            'fixed_route_blocks_only_after_transition_penalty_bytes': 5679.676082,
            'main_rule': 'do not collapse sidecar churn into one average regret number; first freeze the micro-oscillations, then keep only the large front-loaded switches that still beat the best fixed sidecar at the archive\'s real rewrite cost.',
        },
        'frontier_rows': FRONTIER_ROWS,
        'reference_transition_penalty_rows': [_reference_row(value) for value in REFERENCE_TRANSITION_PENALTIES],
        'source_script': str(Path(__file__).relative_to(ROOT)),
        'sources': [
            str(PACKET_PATH.relative_to(ROOT)),
        ],
    }



def _render_md(report: dict[str, object]) -> str:
    findings = report['headline_findings']
    lines = [
        '# Rematch Proxy Delta Decision Packet Compact Repeat-State Switch-Penalty Snapshot — 2026-03-07',
        '',
        '## Focus',
        f"- {report['focus']}",
        '',
        '## Headline findings',
        f"- packet script: `{report['packet_script']}`.",
        f"- live compact catalog starts at `{findings['entry_count']}` fingerprints across `{findings['page_count']}` pages with tail count `{findings['tail_entry_count']}` and route-block bitmap width `{findings['route_block_bitmap_len']}` bytes.",
        f"- at `{report['focal_expected_repeat_lookups']}` expected repeats, the exact non-negative switch-penalty frontier has `{findings['frontier_regime_count']}` regimes.",
        f"- the tiny micro-churn regimes all disappear once sidecar rewrite cost exceeds `{findings['micro_churn_ceiling_bytes']}` bytes per transition.",
        f"- at the earlier fixed-policy break-even average of `{report['focal_transition_penalty_per_switch_bytes']}` bytes per switch, the exact planner still prefers a `{findings['focal_transition_count']}`-transition schedule, not a fixed sidecar.",
        f"- that focal exact planner still beats fixed route blocks by `{findings['focal_advantage_vs_fixed_route_blocks_bytes']}` bytes over the full `{report['max_unique_appends']}`-append horizon.",
        f"- the frontier does not fully collapse to fixed route blocks until switch cost reaches `{findings['fixed_route_blocks_only_after_transition_penalty_bytes']}` bytes per transition.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Exact switch-penalty frontier',
        '| transitions | penalty band start | penalty band end | cumulative objective without penalty | state counts | summary |',
        '|---:|---:|---:|---:|---|---|',
    ]
    for row in report['frontier_rows']:
        lines.append(
            f"| {row['transition_count']} | {row['transition_penalty_start_bytes']} | {row['transition_penalty_end_bytes']} | {row['cumulative_objective_without_transition_penalty']} | `{row['state_counts']}` | {row['summary']} |"
        )
    lines.extend([
        '',
        '## Reference switch-penalty rows',
        '| penalty per switch | transitions kept | cumulative objective with penalty | active band start | active band end | state counts | summary |',
        '|---:|---:|---:|---:|---:|---|---|',
    ])
    for row in report['reference_transition_penalty_rows']:
        lines.append(
            f"| {row['transition_penalty_per_switch_bytes']} | {row['transition_count']} | {row['cumulative_objective_with_transition_penalty']} | {row['active_transition_penalty_start_bytes']} | {row['active_transition_penalty_end_bytes']} | `{row['state_counts']}` | {row['summary']} |"
        )
    lines.extend([
        '',
        '## Sources',
        '- `scripts/analysis/rematch_proxy_delta_decision_packet.py`',
    ])
    return '\n'.join(lines) + '\n'



def main() -> None:
    report = _build_summary()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    OUT_MD.write_text(_render_md(report))
    print(f'wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'wrote {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
