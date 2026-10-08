#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CITATION_MATRIX_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_citation_witness_matrix.json'
OPEN_TOUCHPOINT_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_open_touchpoint_resolution_map.json'
LANDING_LADDER_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_landing_ladder.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_claim_frontier.json'
OUT_MD = ROOT / 'docs' / 'REMATCH_WORLD_BENCHMARK_CLAIM_FRONTIER.md'

TITLE = '# Rematch-world benchmark claim frontier'
SUBTITLE = (
    'Generated readiness frontier for the first endogenous rematch-world benchmark. '
    'Use it to answer, in one small receipt, which claim families are already safe to cite now, '
    'which ones unlock after concrete native-fill stages, and which ones stay blocked by the cross-section engine gap.'
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def build_report() -> dict[str, Any]:
    for path in [CITATION_MATRIX_REPORT, OPEN_TOUCHPOINT_REPORT, LANDING_LADDER_REPORT]:
        if not path.exists():
            raise RuntimeError(f'missing required input: {path.relative_to(ROOT)}')

    citation = load_json(CITATION_MATRIX_REPORT)
    touchpoints = load_json(OPEN_TOUCHPOINT_REPORT)
    ladder = load_json(LANDING_LADDER_REPORT)

    claim_rows = {row['claim_family_id']: row for row in citation['claim_family_rows']}
    resolution_rows = touchpoints['resolution_rows']
    if len(claim_rows) != 8:
        raise RuntimeError(f"expected 8 claim families, found {len(claim_rows)}")

    benchmark_identity_row = next(
        (row for row in ladder['edit_stage_rows'] if row['stage_key'] == 'benchmark_id_binding'),
        None,
    )
    if benchmark_identity_row is None:
        raise RuntimeError('missing benchmark_id_binding stage in landing ladder')

    cross_section_row = next(
        (row for row in resolution_rows if row['closure_scope'] == 'cross_section_engine_gap'),
        None,
    )
    if cross_section_row is None:
        raise RuntimeError('missing cross-section engine gap row in touchpoint resolution map')
    cross_section_claim_ids = set(cross_section_row['affected_claim_family_ids'])

    seed_rows_by_claim: dict[str, list[dict[str, Any]]] = {}
    for row in resolution_rows:
        if row['closure_scope'] != 'seed_local_native_fill':
            continue
        for claim_id in row['affected_claim_family_ids']:
            seed_rows_by_claim.setdefault(claim_id, []).append(row)

    staged_rows: list[dict[str, Any]] = []
    blocked_rows: list[dict[str, Any]] = []
    closed_now_rows: list[dict[str, Any]] = []

    for claim_id in sorted(claim_rows):
        claim = claim_rows[claim_id]
        posture = claim['posture']
        if claim_id in cross_section_claim_ids:
            blocked_rows.append(
                {
                    'claim_family_id': claim_id,
                    'claim_label': claim['claim_label'],
                    'frontier_kind': 'blocked_by_engine_gap',
                    'frontier_label': 'blocked_by_engine_gap',
                    'claim_summary': claim['claim_summary'],
                    'why_it_matters': claim['why_it_matters'],
                    'blocking_resolver_id': cross_section_row['resolver_id'],
                    'blocking_resolver_summary': cross_section_row['resolver_summary'],
                    'current_bridge_paths': cross_section_row['current_bridge_paths'],
                    'open_spec_ids': claim['open_spec_ids'],
                    'posture': posture,
                }
            )
            continue

        dependent_rows = seed_rows_by_claim.get(claim_id, [])
        if dependent_rows:
            cumulative_required_edit_count = max(int(row['cumulative_required_edit_count']) for row in dependent_rows)
            frontier_stage_row = next(
                row for row in ladder['edit_stage_rows'] if int(row['cumulative_required_edit_count']) == cumulative_required_edit_count
            )
            staged_rows.append(
                {
                    'claim_family_id': claim_id,
                    'claim_label': claim['claim_label'],
                    'frontier_kind': 'native_stage_unlock',
                    'frontier_label': f'closes_after_{cumulative_required_edit_count}_cumulative_edits',
                    'claim_summary': claim['claim_summary'],
                    'why_it_matters': claim['why_it_matters'],
                    'posture': posture,
                    'resolver_ids': [row['resolver_id'] for row in dependent_rows],
                    'native_sections': [row['native_section'] for row in dependent_rows],
                    'required_edit_total': sum(int(row['required_edit_count']) for row in dependent_rows),
                    'cumulative_required_edit_count': cumulative_required_edit_count,
                    'frontier_stage_key': frontier_stage_row['stage_key'],
                    'frontier_stage': frontier_stage_row['stage'],
                    'frontier_dependency_reason': frontier_stage_row['dependency_reason'],
                    'blocking_slot_total': sum(int(row['blocking_slot_count']) for row in dependent_rows),
                    'benchmark_identity_prerequisite_edit_count': int(benchmark_identity_row['required_edit_count']),
                    'benchmark_identity_cumulative_edit_count': int(benchmark_identity_row['cumulative_required_edit_count']),
                    'minimal_citation_paths': claim['minimal_citation_paths'],
                    'open_spec_ids': claim['open_spec_ids'],
                }
            )
            continue

        closed_now_rows.append(
            {
                'claim_family_id': claim_id,
                'claim_label': claim['claim_label'],
                'frontier_kind': 'safe_to_cite_now',
                'frontier_label': 'safe_to_cite_now',
                'claim_summary': claim['claim_summary'],
                'why_it_matters': claim['why_it_matters'],
                'posture': posture,
                'minimal_citation_paths': claim['minimal_citation_paths'],
                'open_spec_ids': claim['open_spec_ids'],
            }
        )

    staged_rows.sort(key=lambda row: (row['cumulative_required_edit_count'], row['claim_family_id']))
    blocked_rows.sort(key=lambda row: row['claim_family_id'])
    closed_now_rows.sort(key=lambda row: row['claim_family_id'])

    actionable_frontiers = sorted({row['cumulative_required_edit_count'] for row in staged_rows})
    if actionable_frontiers != [8, 18, 29]:
        raise RuntimeError(f'unexpected actionable frontiers: {actionable_frontiers}')

    frontier_rows = closed_now_rows + staged_rows + blocked_rows
    if len(frontier_rows) != len(claim_rows):
        raise RuntimeError('claim frontier did not classify every claim family exactly once')

    counts = {
        'claim_family_count': len(frontier_rows),
        'safe_to_cite_now_count': len(closed_now_rows),
        'native_stage_unlock_count': len(staged_rows),
        'blocked_by_engine_gap_count': len(blocked_rows),
        'distinct_actionable_frontier_count': len(actionable_frontiers),
        'actionable_cumulative_frontier_sequence': actionable_frontiers,
        'benchmark_identity_prerequisite_edit_count': int(benchmark_identity_row['required_edit_count']),
    }

    frontier_buckets = [
        {
            'frontier_kind': 'safe_to_cite_now',
            'claim_family_ids': [row['claim_family_id'] for row in closed_now_rows],
            'claim_family_count': len(closed_now_rows),
            'summary': 'These claim families already have enough compact evidence in the archive and do not wait on any remaining rematch-world open question or engine gap.',
        },
        {
            'frontier_kind': 'native_stage_unlock',
            'claim_family_ids': [row['claim_family_id'] for row in staged_rows],
            'claim_family_count': len(staged_rows),
            'summary': 'These claim families become world-native safe only after the listed cumulative native-fill stages are complete; the benchmark-id bind is a prerequisite but closes no claim family by itself.',
        },
        {
            'frontier_kind': 'blocked_by_engine_gap',
            'claim_family_ids': [row['claim_family_id'] for row in blocked_rows],
            'claim_family_count': len(blocked_rows),
            'summary': 'These claim families remain citation-first even after seed-local fills because they still depend on the unresolved cross-section engine contract `SG-003`.',
        },
    ]

    main_findings = [
        f"{counts['safe_to_cite_now_count']} claim families are already safe to cite now, {counts['native_stage_unlock_count']} unlock at concrete native frontiers, and {counts['blocked_by_engine_gap_count']} remain blocked by `SG-003`.",
        f"The actionable cumulative native claim frontiers are {', '.join(str(value) for value in actionable_frontiers)} edits — not 7/17/28 — because the benchmark-id bind consumes the first prerequisite edit before any claim family closes.",
        f"Role/state disclosure closes first at {actionable_frontiers[0]} cumulative edits, welfare decomposition closes at {actionable_frontiers[1]}, and paired leaderboard interpretation closes at {actionable_frontiers[2]}.",
        'The editable-surface, mutation-witness, and phase-3 world-emission claim families still stay citation-first after all seed-local fills because the engine-level world-aware rematching contract is not yet endogenous.',
    ]

    return {
        'analysis_script': Path(__file__).relative_to(ROOT).as_posix(),
        'focus': 'classify each first-publication rematch-world claim family as already safe now, unlocked by a concrete cumulative native-fill frontier, or still blocked by the cross-section engine gap',
        'counts': counts,
        'main_findings': main_findings,
        'frontier_buckets': frontier_buckets,
        'frontier_rows': frontier_rows,
        'recommended_next_move': 'Use this frontier before filling or citing the benchmark: close native claim families in 8 -> 18 -> 29 cumulative-edit order, and keep the SG-003 families citation-first until the engine contract itself exists.',
    }


def render(report: dict[str, Any]) -> str:
    counts = report['counts']
    lines = [
        TITLE,
        '',
        f"Focus: {report['focus']}",
        '',
        SUBTITLE,
        '',
        '## Main findings',
        '',
    ]
    lines.extend(f'- {row}' for row in report['main_findings'])
    lines.extend([
        '',
        '## Counts',
        '',
        f"- claim_family_count: {counts['claim_family_count']}",
        f"- safe_to_cite_now_count: {counts['safe_to_cite_now_count']}",
        f"- native_stage_unlock_count: {counts['native_stage_unlock_count']}",
        f"- blocked_by_engine_gap_count: {counts['blocked_by_engine_gap_count']}",
        f"- distinct_actionable_frontier_count: {counts['distinct_actionable_frontier_count']}",
        f"- actionable_cumulative_frontier_sequence: {', '.join(str(v) for v in counts['actionable_cumulative_frontier_sequence'])}",
        f"- benchmark_identity_prerequisite_edit_count: {counts['benchmark_identity_prerequisite_edit_count']}",
        '',
        '## Frontier buckets',
        '',
        '| frontier_kind | claim_family_count | claim_family_ids | summary |',
        '|---|---:|---|---|',
    ])
    for row in report['frontier_buckets']:
        claim_ids = ', '.join(f"`{claim_id}`" for claim_id in row['claim_family_ids']) if row['claim_family_ids'] else '—'
        lines.append(f"| `{row['frontier_kind']}` | {row['claim_family_count']} | {claim_ids} | {row['summary']} |")

    lines.extend([
        '',
        '## Claim frontier matrix',
        '',
        '| claim_family_id | frontier_kind | claim_label | frontier_or_blocker |',
        '|---|---|---|---|',
    ])
    for row in report['frontier_rows']:
        if row['frontier_kind'] == 'native_stage_unlock':
            frontier = f"`{row['cumulative_required_edit_count']}` edits via `{row['frontier_stage_key']}`"
        elif row['frontier_kind'] == 'blocked_by_engine_gap':
            frontier = f"`{row['blocking_resolver_id']}`"
        else:
            frontier = 'ready now'
        lines.append(f"| `{row['claim_family_id']}` | `{row['frontier_kind']}` | {row['claim_label']} | {frontier} |")

    lines.extend(['', '## Claim family details', ''])
    for row in report['frontier_rows']:
        lines.extend([
            f"### {row['claim_family_id']} — {row['claim_label']}",
            '',
            f"- frontier_kind: `{row['frontier_kind']}`",
            f"- claim_summary: {row['claim_summary']}",
            f"- why_it_matters: {row['why_it_matters']}",
        ])
        if row['frontier_kind'] == 'native_stage_unlock':
            lines.extend([
                f"- cumulative_required_edit_count: {row['cumulative_required_edit_count']}",
                f"- frontier_stage: `{row['frontier_stage_key']}` ({row['frontier_stage']})",
                f"- resolver_ids: {', '.join(f'`{rid}`' for rid in row['resolver_ids'])}",
                f"- native_sections: {', '.join(f'`{section}`' for section in row['native_sections'])}",
                f"- blocking_slot_total: {row['blocking_slot_total']}",
                f"- benchmark_identity_prerequisite_edit_count: {row['benchmark_identity_prerequisite_edit_count']}",
                f"- frontier_dependency_reason: {row['frontier_dependency_reason']}",
            ])
        elif row['frontier_kind'] == 'blocked_by_engine_gap':
            lines.extend([
                f"- blocking_resolver_id: `{row['blocking_resolver_id']}`",
                f"- blocking_resolver_summary: {row['blocking_resolver_summary']}",
                '- current_bridge_paths:',
            ])
            lines.extend(f"  - `{path}`" for path in row['current_bridge_paths'])
        else:
            lines.append('- current_state: already safe to cite from retained compact surfaces')
        if row['minimal_citation_paths'] if 'minimal_citation_paths' in row else None:
            lines.append('- minimal_citation_paths:')
            lines.extend(f"  - `{path}`" for path in row['minimal_citation_paths'])
        if row['open_spec_ids']:
            lines.append(f"- open_spec_ids: {', '.join(f'`{spec_id}`' for spec_id in row['open_spec_ids'])}")
        else:
            lines.append('- open_spec_ids: none')
        lines.append('')

    lines.extend(['## Recommended next move', '', f"- {report['recommended_next_move']}", ''])
    return '\n'.join(lines)


def main() -> int:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(render(report), encoding='utf-8')
    print(f'wrote {OUT_JSON.relative_to(ROOT)} and {OUT_MD.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
