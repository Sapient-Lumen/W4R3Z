#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
LANDING_LADDER_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_landing_ladder.json'
CLAIM_FRONTIER_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_claim_frontier.json'
OPEN_TOUCHPOINT_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_open_touchpoint_resolution_map.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_stage_yield_ledger.json'
OUT_MD = ROOT / 'docs' / 'REMATCH_WORLD_BENCHMARK_STAGE_YIELD_LEDGER.md'

TITLE = '# Rematch-world benchmark stage-yield ledger'
SUBTITLE = (
    'Generated stage-by-stage yield ledger for the first endogenous rematch-world benchmark. '
    'Use it to see what each native fill stage actually buys: which blocker work it clears, '
    'which open touchpoints it resolves, which claim families become safe, and which stages are prerequisites or metadata-only rather than immediate claim unlocks.'
)

UTILITY_SUMMARIES = {
    'benchmark_anchor': 'Anchors the artifact to one concrete benchmark id before any world-native rows are publishable.',
    'claim_unlock': 'Directly makes at least one additional claim family safe once this stage lands.',
    'resolver_only_prerequisite': 'Closes real native blocker work and an open seed-local question, but does not immediately unlock a claim family on its own.',
    'metadata_closeout': 'Does not clear a new native question or claim family; it only marks the artifact as filled after every blocker is already gone.',
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def classify_stage_utility(order: int, new_claim_count: int, new_touchpoint_count: int, changed_prefixes: list[str]) -> str:
    if order == 1:
        return 'benchmark_anchor'
    if new_claim_count > 0:
        return 'claim_unlock'
    if any(prefix == 'artifact_state' for prefix in changed_prefixes):
        return 'metadata_closeout'
    if new_touchpoint_count > 0:
        return 'resolver_only_prerequisite'
    raise RuntimeError(f'unclassifiable stage utility for order={order}')


def build_report() -> dict[str, Any]:
    for path in [LANDING_LADDER_REPORT, CLAIM_FRONTIER_REPORT, OPEN_TOUCHPOINT_REPORT]:
        if not path.exists():
            raise RuntimeError(f'missing required input: {path.relative_to(ROOT)}')

    ladder = load_json(LANDING_LADDER_REPORT)
    frontier = load_json(CLAIM_FRONTIER_REPORT)
    touchpoints = load_json(OPEN_TOUCHPOINT_REPORT)

    stage_rows = ladder['edit_stage_rows']
    frontier_rows = frontier['frontier_rows']
    resolution_rows = touchpoints['resolution_rows']

    safe_now_claim_ids = sorted(row['claim_family_id'] for row in frontier_rows if row['frontier_kind'] == 'safe_to_cite_now')
    engine_gap_claim_ids = sorted(row['claim_family_id'] for row in frontier_rows if row['frontier_kind'] == 'blocked_by_engine_gap')
    native_claim_rows_by_cumulative: dict[int, list[dict[str, Any]]] = {}
    for row in frontier_rows:
        if row['frontier_kind'] == 'native_stage_unlock':
            native_claim_rows_by_cumulative.setdefault(int(row['cumulative_required_edit_count']), []).append(row)
    seed_rows = [row for row in resolution_rows if row['closure_scope'] == 'seed_local_native_fill']
    seed_rows_by_cumulative: dict[int, list[dict[str, Any]]] = {}
    for row in seed_rows:
        seed_rows_by_cumulative.setdefault(int(row['cumulative_required_edit_count']), []).append(row)

    if len(stage_rows) != 7:
        raise RuntimeError(f'expected 7 landing stages, found {len(stage_rows)}')
    if len(safe_now_claim_ids) != 2:
        raise RuntimeError(f'expected 2 safe-now claims, found {len(safe_now_claim_ids)}')
    if len(engine_gap_claim_ids) != 3:
        raise RuntimeError(f'expected 3 engine-gap claims, found {len(engine_gap_claim_ids)}')
    if len(seed_rows) != 5:
        raise RuntimeError(f'expected 5 seed-local touchpoints, found {len(seed_rows)}')

    cumulative_claim_ids = set(safe_now_claim_ids)
    cumulative_touchpoint_ids: set[str] = set()
    rendered_stage_rows: list[dict[str, Any]] = []
    for row in stage_rows:
        cumulative = int(row['cumulative_required_edit_count'])
        new_claim_rows = sorted(native_claim_rows_by_cumulative.get(cumulative, []), key=lambda item: item['claim_family_id'])
        new_touch_rows = sorted(seed_rows_by_cumulative.get(cumulative, []), key=lambda item: item['resolver_id'])
        cumulative_claim_ids.update(item['claim_family_id'] for item in new_claim_rows)
        cumulative_touchpoint_ids.update(item['resolver_id'] for item in new_touch_rows)
        utility = classify_stage_utility(int(row['order']), len(new_claim_rows), len(new_touch_rows), row['changed_prefixes'])
        rendered_stage_rows.append({
            'order': int(row['order']),
            'stage_key': row['stage_key'],
            'stage': row['stage'],
            'required_edit_count': int(row['required_edit_count']),
            'cumulative_required_edit_count': cumulative,
            'blocker_clear_count': int(row['blocker_clear_count']),
            'section_status_flip_count': int(row.get('section_status_flip_count', 0)),
            'changed_prefixes': row['changed_prefixes'],
            'linked_question_ids': row.get('linked_question_ids', []),
            'dependency_reason': row['dependency_reason'],
            'newly_resolved_touchpoint_ids': [item['resolver_id'] for item in new_touch_rows],
            'newly_resolved_touchpoint_count': len(new_touch_rows),
            'newly_unlocked_claim_family_ids': [item['claim_family_id'] for item in new_claim_rows],
            'newly_unlocked_claim_family_count': len(new_claim_rows),
            'cumulative_safe_claim_family_count': len(cumulative_claim_ids),
            'cumulative_resolved_seed_touchpoint_count': len(cumulative_touchpoint_ids),
            'remaining_seed_touchpoint_count': len(seed_rows) - len(cumulative_touchpoint_ids),
            'remaining_native_stage_unlock_claim_count': len([item for item in frontier_rows if item['frontier_kind'] == 'native_stage_unlock' and item['claim_family_id'] not in cumulative_claim_ids]),
            'remaining_engine_gap_claim_family_count': len(engine_gap_claim_ids),
            'safe_claim_fraction': f"{len(cumulative_claim_ids)}/{len(frontier_rows)}",
            'stage_utility_kind': utility,
            'stage_utility_summary': UTILITY_SUMMARIES[utility],
        })

    counts = {
        'stage_count': len(rendered_stage_rows),
        'claim_unlock_stage_count': sum(1 for row in rendered_stage_rows if row['stage_utility_kind'] == 'claim_unlock'),
        'resolver_only_prerequisite_stage_count': sum(1 for row in rendered_stage_rows if row['stage_utility_kind'] == 'resolver_only_prerequisite'),
        'benchmark_anchor_stage_count': sum(1 for row in rendered_stage_rows if row['stage_utility_kind'] == 'benchmark_anchor'),
        'metadata_closeout_stage_count': sum(1 for row in rendered_stage_rows if row['stage_utility_kind'] == 'metadata_closeout'),
        'safe_to_cite_now_claim_family_count': len(safe_now_claim_ids),
        'max_safe_claim_family_count_after_seed_local_fill': max(row['cumulative_safe_claim_family_count'] for row in rendered_stage_rows),
        'seed_local_touchpoint_count': len(seed_rows),
        'max_resolved_seed_touchpoint_count': max(row['cumulative_resolved_seed_touchpoint_count'] for row in rendered_stage_rows),
        'remaining_engine_gap_claim_family_count': len(engine_gap_claim_ids),
    }
    utility_buckets = []
    for utility in ['benchmark_anchor', 'claim_unlock', 'resolver_only_prerequisite', 'metadata_closeout']:
        bucket = [row for row in rendered_stage_rows if row['stage_utility_kind'] == utility]
        utility_buckets.append({
            'stage_utility_kind': utility,
            'stage_count': len(bucket),
            'stage_keys': [row['stage_key'] for row in bucket],
            'summary': UTILITY_SUMMARIES[utility],
        })

    main_findings = [
        'Only 3 of the 7 edit stages directly unlock any new claim family; 2 stages are prerequisite-only question closures, 1 is a benchmark-id anchor, and the final stage is metadata-only closeout.',
        'The two easy-to-miss prerequisite-only stages are `matching_state_contract` at 12 cumulative edits and `turnover_tempo_contract` at 23 cumulative edits: they clear real blocker work and open questions even though the safe-claim count does not move immediately.',
        'After 18 cumulative edits, 4 of the 8 claim families are already safe and 3 of the 5 seed-local touchpoints are closed; after 29 edits, 5 claim families are safe and all 5 seed-local touchpoints are closed.',
        'The final `artifact_state` flip at 30 cumulative edits changes no claim family and closes no touchpoint; it only converts the fully filled seed into a publishable filled-benchmark artifact while the 3 `SG-003` claim families remain citation-first.',
    ]
    return {
        'analysis_script': Path(__file__).relative_to(ROOT).as_posix(),
        'focus': 'show what each native fill stage actually buys for the first rematch-world publication: blocker work cleared, touchpoints resolved, claim families unlocked, and the stages that are prerequisites or metadata-only rather than immediate claim unlocks',
        'counts': counts,
        'main_findings': main_findings,
        'utility_buckets': utility_buckets,
        'stage_rows': rendered_stage_rows,
        'stage_yield_matrix': [{
            'order': row['order'],
            'stage_key': row['stage_key'],
            'required_edit_count': row['required_edit_count'],
            'cumulative_required_edit_count': row['cumulative_required_edit_count'],
            'newly_resolved_touchpoint_ids': row['newly_resolved_touchpoint_ids'],
            'newly_unlocked_claim_family_ids': row['newly_unlocked_claim_family_ids'],
            'cumulative_safe_claim_family_count': row['cumulative_safe_claim_family_count'],
            'remaining_seed_touchpoint_count': row['remaining_seed_touchpoint_count'],
            'stage_utility_kind': row['stage_utility_kind'],
        } for row in rendered_stage_rows],
        'recommended_next_move': 'Use this ledger when sequencing native work: do not drop the 12-edit or 23-edit stages just because the safe-claim total holds flat there, and treat the 30th edit as publication-state closeout rather than as a new evidentiary unlock.',
    }


def render(report: dict[str, Any]) -> str:
    counts = report['counts']
    lines = [TITLE, '', f"Focus: {report['focus']}", '', SUBTITLE, '', '## Main findings', '']
    lines.extend(f'- {item}' for item in report['main_findings'])
    lines.extend(['', '## Counts', ''])
    for key in ['stage_count', 'claim_unlock_stage_count', 'resolver_only_prerequisite_stage_count', 'benchmark_anchor_stage_count', 'metadata_closeout_stage_count', 'safe_to_cite_now_claim_family_count', 'max_safe_claim_family_count_after_seed_local_fill', 'seed_local_touchpoint_count', 'max_resolved_seed_touchpoint_count', 'remaining_engine_gap_claim_family_count']:
        lines.append(f'- {key}: {counts[key]}')
    lines.extend(['', '## Utility buckets', '', '| stage_utility_kind | stage_count | stage_keys | summary |', '|---|---:|---|---|'])
    for row in report['utility_buckets']:
        stage_keys = ', '.join(f"`{key}`" for key in row['stage_keys']) if row['stage_keys'] else '—'
        lines.append(f"| `{row['stage_utility_kind']}` | {row['stage_count']} | {stage_keys} | {row['summary']} |")
    lines.extend(['', '## Stage yield matrix', '', '| order | stage_key | required_edits | cumulative_edits | touchpoints_closed_now | claims_unlocked_now | cumulative_safe_claims | remaining_seed_touchpoints | utility |', '|---:|---|---:|---:|---|---|---:|---:|---|'])
    for row in report['stage_yield_matrix']:
        touchpoints = ', '.join(f"`{x}`" for x in row['newly_resolved_touchpoint_ids']) if row['newly_resolved_touchpoint_ids'] else '—'
        claims = ', '.join(f"`{x}`" for x in row['newly_unlocked_claim_family_ids']) if row['newly_unlocked_claim_family_ids'] else '—'
        lines.append(f"| {row['order']} | `{row['stage_key']}` | {row['required_edit_count']} | {row['cumulative_required_edit_count']} | {touchpoints} | {claims} | {row['cumulative_safe_claim_family_count']} | {row['remaining_seed_touchpoint_count']} | `{row['stage_utility_kind']}` |")
    lines.extend(['', '## Stage details', ''])
    for row in report['stage_rows']:
        lines.extend([
            f"### Stage {row['order']} — {row['stage']}",
            '',
            f"- stage_key: `{row['stage_key']}`",
            f"- stage_utility_kind: `{row['stage_utility_kind']}`",
            f"- stage_utility_summary: {row['stage_utility_summary']}",
            f"- required_edit_count: {row['required_edit_count']}",
            f"- cumulative_required_edit_count: {row['cumulative_required_edit_count']}",
            f"- blocker_clear_count: {row['blocker_clear_count']}",
            f"- section_status_flip_count: {row['section_status_flip_count']}",
            f"- changed_prefixes: {', '.join(f'`{x}`' for x in row['changed_prefixes'])}",
            f"- linked_question_ids: {', '.join(f'`{x}`' for x in row['linked_question_ids']) if row['linked_question_ids'] else 'none'}",
            f"- newly_resolved_touchpoint_ids: {', '.join(f'`{x}`' for x in row['newly_resolved_touchpoint_ids']) if row['newly_resolved_touchpoint_ids'] else 'none'}",
            f"- newly_unlocked_claim_family_ids: {', '.join(f'`{x}`' for x in row['newly_unlocked_claim_family_ids']) if row['newly_unlocked_claim_family_ids'] else 'none'}",
            f"- cumulative_safe_claim_family_count: {row['cumulative_safe_claim_family_count']} ({row['safe_claim_fraction']})",
            f"- cumulative_resolved_seed_touchpoint_count: {row['cumulative_resolved_seed_touchpoint_count']}/{report['counts']['seed_local_touchpoint_count']}",
            f"- remaining_native_stage_unlock_claim_count: {row['remaining_native_stage_unlock_claim_count']}",
            f"- remaining_seed_touchpoint_count: {row['remaining_seed_touchpoint_count']}",
            f"- remaining_engine_gap_claim_family_count: {row['remaining_engine_gap_claim_family_count']}",
            f"- dependency_reason: {row['dependency_reason']}",
            '',
        ])
    lines.extend(['## Recommended next move', '', f"- {report['recommended_next_move']}", ''])
    return '\n'.join(lines)


def main() -> int:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    OUT_MD.write_text(render(report), encoding='utf-8')
    print(f'wrote {OUT_JSON.relative_to(ROOT)} and {OUT_MD.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
