#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SPEC_LEDGER_PATH = ROOT / 'docs' / 'spec_ledger.md'
CITATION_MATRIX_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_citation_witness_matrix.json'
NATIVE_FILL_MAP_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_native_fill_map.json'
LANDING_LADDER_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_landing_ladder.json'
WORLD_EMISSION_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_world_emission_card.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_open_touchpoint_resolution_map.json'
OUT_MD = ROOT / 'docs' / 'REMATCH_WORLD_BENCHMARK_OPEN_TOUCHPOINT_RESOLUTION_MAP.md'

TITLE = '# Rematch-world benchmark open touchpoint resolution map'
SUBTITLE = (
    'Generated compact closure map for the first endogenous rematch-world benchmark. '
    'Use it to turn the still-open assumptions/questions/gap into one small implementation queue: '
    'which claim families each touchpoint blocks, which native section it lands in, and which bridge surfaces remain sufficient until closure.'
)
ASSUMPTION_DEP_RE = re.compile(r'Until (?P<resolver>[A-Z]{2}-\d{3}) resolves,', re.IGNORECASE)
ORDERED_RESOLVERS = ['SG-003', 'SQ-012', 'SQ-013', 'SQ-014', 'SQ-015', 'SQ-016']


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def parse_spec_ledger(path: Path) -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        stripped = line.strip()
        if not stripped.startswith('|'):
            continue
        parts = [part.strip() for part in stripped.strip('|').split('|')]
        if len(parts) != 6:
            continue
        if parts[0] == 'id' or set(parts[0]) == {'-'}:
            continue
        rows[parts[0]] = {
            'id': parts[0],
            'kind': parts[1],
            'status': parts[2],
            'owner': parts[3],
            'review_by': parts[4],
            'summary': parts[5],
        }
    return rows


def resolver_from_assumption(summary: str) -> str:
    match = ASSUMPTION_DEP_RE.search(summary)
    if not match:
        raise RuntimeError(f'could not infer resolver id from assumption summary: {summary!r}')
    return match.group('resolver').upper()


def build_report() -> dict[str, Any]:
    for path in [SPEC_LEDGER_PATH, CITATION_MATRIX_REPORT, NATIVE_FILL_MAP_REPORT, LANDING_LADDER_REPORT, WORLD_EMISSION_REPORT]:
        if not path.exists():
            raise RuntimeError(f'missing required input: {path.relative_to(ROOT)}')

    spec_ledger = parse_spec_ledger(SPEC_LEDGER_PATH)
    citation = load_json(CITATION_MATRIX_REPORT)
    native_fill_map = load_json(NATIVE_FILL_MAP_REPORT)
    landing_ladder = load_json(LANDING_LADDER_REPORT)
    world_emission = load_json(WORLD_EMISSION_REPORT)

    claim_rows = {row['claim_family_id']: row for row in citation['claim_family_rows']}
    open_spec_rows = {row['id']: row for row in citation['open_spec_rows']}
    section_rows_by_question: dict[str, dict[str, Any]] = {}
    for section_row in native_fill_map['section_rows']:
        linked = section_row['linked_question_ids']
        if len(linked) != 1:
            raise RuntimeError(f'expected exactly one linked question id for section {section_row["section"]}, got {linked}')
        section_rows_by_question[linked[0]] = section_row
    stage_rows_by_question: dict[str, dict[str, Any]] = {}
    for stage_row in landing_ladder['edit_stage_rows']:
        for question_id in stage_row.get('linked_question_ids', []):
            stage_rows_by_question[question_id] = stage_row

    folded_assumptions: list[dict[str, Any]] = []
    assumption_ids_by_resolver: dict[str, list[str]] = {}
    for spec_id, open_row in open_spec_rows.items():
        row = spec_ledger[spec_id]
        if row['kind'] != 'assumption' or row['status'] != 'open':
            continue
        resolver_id = resolver_from_assumption(row['summary'])
        if resolver_id not in ORDERED_RESOLVERS:
            continue
        assumption_ids_by_resolver.setdefault(resolver_id, []).append(spec_id)
        folded_assumptions.append(
            {
                'id': spec_id,
                'resolver_id': resolver_id,
                'status': row['status'],
                'summary': row['summary'],
                'touched_by_claim_family_ids': sorted(open_row.get('touched_by_claim_family_ids', [])),
            }
        )

    resolution_rows: list[dict[str, Any]] = []
    all_affected_claim_ids: set[str] = set()
    total_seed_local_blocker_slots = 0
    total_seed_local_required_edits = 0
    total_seed_local_section_status_flips = 0

    for resolver_id in ORDERED_RESOLVERS:
        if resolver_id not in spec_ledger:
            raise RuntimeError(f'missing resolver in spec ledger: {resolver_id}')
        if resolver_id not in open_spec_rows:
            raise RuntimeError(f'missing resolver in citation matrix open spec rows: {resolver_id}')
        resolver_row = spec_ledger[resolver_id]
        direct_claim_ids = set(open_spec_rows[resolver_id]['touched_by_claim_family_ids'])
        dependent_assumption_ids = sorted(assumption_ids_by_resolver.get(resolver_id, []))
        dependent_assumption_summaries = [spec_ledger[assumption_id]['summary'] for assumption_id in dependent_assumption_ids]
        dependent_claim_ids: set[str] = set()
        for assumption_id in dependent_assumption_ids:
            dependent_claim_ids.update(open_spec_rows.get(assumption_id, {}).get('touched_by_claim_family_ids', []))
        affected_claim_ids = sorted(direct_claim_ids | dependent_claim_ids)
        all_affected_claim_ids.update(affected_claim_ids)

        bridge_paths = sorted(
            {
                path
                for claim_id in affected_claim_ids
                for path in claim_rows[claim_id]['minimal_citation_paths']
            }
        )

        base_row: dict[str, Any] = {
            'resolver_id': resolver_id,
            'resolver_kind': resolver_row['kind'],
            'resolver_status': resolver_row['status'],
            'resolver_summary': resolver_row['summary'],
            'dependent_assumption_ids': dependent_assumption_ids,
            'dependent_assumption_count': len(dependent_assumption_ids),
            'dependent_assumption_summaries': dependent_assumption_summaries,
            'affected_claim_family_ids': affected_claim_ids,
            'affected_claim_family_count': len(affected_claim_ids),
            'current_bridge_paths': bridge_paths,
            'current_bridge_path_count': len(bridge_paths),
        }

        if resolver_id == 'SG-003':
            base_row.update(
                {
                    'closure_scope': 'cross_section_engine_gap',
                    'native_section': None,
                    'fill_order_index': None,
                    'required_edit_count': None,
                    'cumulative_required_edit_count': None,
                    'blocking_slot_count': None,
                    'template_blocker_count': None,
                    'null_blocker_count': None,
                    'section_status_flip_count': None,
                    'status_gate_path': None,
                    'data_prefix': None,
                    'dependency_reason': 'No single seed-local fill section removes this dependency; the copied phase-3 decision contract remains citation-first until the engine-level endogenous rematching and canonicalization contract exists.',
                    'closure_target_paths': [],
                    'closure_target_path_count': 0,
                    'closure_target_summary': (
                        f"Keep the copied decision bundle frozen and citation-first until the engine gap closes; the current seed-local publication floor still covers "
                        f"{native_fill_map['minimum_publishable_mutation_set']['explicit_fill_blocker_count']} blocker loci, but none of those edits alone replaces the missing world-aware canonicalization contract."
                    ),
                }
            )
        else:
            section_row = section_rows_by_question[resolver_id]
            stage_row = stage_rows_by_question[resolver_id]
            closure_target_paths = [blocker_row['path'] for blocker_row in section_row['blocker_rows']]
            total_seed_local_blocker_slots += section_row['blocking_slot_count']
            total_seed_local_required_edits += stage_row['required_edit_count']
            total_seed_local_section_status_flips += stage_row['section_status_flip_count']
            base_row.update(
                {
                    'closure_scope': 'seed_local_native_fill',
                    'native_section': section_row['section'],
                    'fill_order_index': section_row['fill_order_index'],
                    'required_edit_count': stage_row['required_edit_count'],
                    'cumulative_required_edit_count': stage_row['cumulative_required_edit_count'],
                    'blocking_slot_count': section_row['blocking_slot_count'],
                    'template_blocker_count': section_row['template_blocker_count'],
                    'null_blocker_count': section_row['null_blocker_count'],
                    'section_status_flip_count': stage_row['section_status_flip_count'],
                    'status_gate_path': section_row['status_prefix'],
                    'data_prefix': section_row['data_prefix'],
                    'dependency_reason': stage_row['dependency_reason'],
                    'closure_target_paths': closure_target_paths,
                    'closure_target_path_count': len(closure_target_paths),
                    'closure_target_summary': (
                        f"Fill {section_row['section']} and flip `{section_row['status_prefix']}` to `{section_row['status_after_fill']}`; "
                        f"this clears {section_row['blocking_slot_count']} seed-local blocker slots at stage {section_row['fill_order_index']} of the native landing ladder."
                    ),
                }
            )
        resolution_rows.append(base_row)

    counts = {
        'open_touchpoint_count': citation['counts']['open_spec_touchpoint_count'],
        'closure_target_count': len(resolution_rows),
        'native_question_target_count': sum(1 for row in resolution_rows if row['resolver_kind'] == 'question'),
        'cross_section_gap_target_count': sum(1 for row in resolution_rows if row['resolver_kind'] == 'gap'),
        'folded_assumption_count': len(folded_assumptions),
        'affected_claim_family_count': len(all_affected_claim_ids),
        'seed_local_blocker_slot_count': total_seed_local_blocker_slots,
        'seed_local_required_edit_count': total_seed_local_required_edits,
        'seed_local_section_status_flip_count': total_seed_local_section_status_flips,
        'pending_native_section_count': world_emission['pending_native_section_count'],
    }

    main_findings = [
        f"{counts['open_touchpoint_count']} open rematch-world touchpoints collapse onto {counts['closure_target_count']} actual closure targets.",
        f"{counts['native_question_target_count']} closure targets are seed-local native fills covering {counts['seed_local_blocker_slot_count']} blocker slots and {counts['seed_local_required_edit_count']} required edits; the remaining target is the cross-section engine gap `{ORDERED_RESOLVERS[0]}`.",
        f"Only {counts['folded_assumption_count']} rows are pure interpretation disciplines; they now fold under the same 6 closure targets instead of floating separately in the caution surface.",
        f"`RWC-008` stays outside this map because final package authority is already closed; this map only tracks the {counts['affected_claim_family_count']} claim families whose interpretation or publication path still depends on open rematch-world questions.",
    ]

    return {
        'analysis_script': Path(__file__).relative_to(ROOT).as_posix(),
        'focus': 'collapse the still-open rematch-world assumptions/questions/gap into one exact closure queue that maps each resolver onto affected claim families, bridge citations, and seed-local landing work where applicable',
        'counts': counts,
        'main_findings': main_findings,
        'resolution_rows': resolution_rows,
        'folded_assumption_rows': sorted(folded_assumptions, key=lambda row: row['id']),
        'recommended_next_move': 'Use this map when deciding the next native rematch-world fill: land one resolver at a time in ladder order, cite only the listed bridge surfaces while it remains open, and do not treat the engine gap as solved merely because all five seed-local sections are filled.',
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
    lines.extend([f"- {row}" for row in report['main_findings']])
    lines.extend(
        [
            '',
            '## Counts',
            '',
            f"- open_touchpoint_count: {counts['open_touchpoint_count']}",
            f"- closure_target_count: {counts['closure_target_count']}",
            f"- native_question_target_count: {counts['native_question_target_count']}",
            f"- cross_section_gap_target_count: {counts['cross_section_gap_target_count']}",
            f"- folded_assumption_count: {counts['folded_assumption_count']}",
            f"- affected_claim_family_count: {counts['affected_claim_family_count']}",
            f"- seed_local_blocker_slot_count: {counts['seed_local_blocker_slot_count']}",
            f"- seed_local_required_edit_count: {counts['seed_local_required_edit_count']}",
            f"- seed_local_section_status_flip_count: {counts['seed_local_section_status_flip_count']}",
            f"- pending_native_section_count: {counts['pending_native_section_count']}",
            '',
            '## Closure target matrix',
            '',
            '| resolver_id | kind | closure_scope | native_section | affected_claims | dependent_assumptions | blocker_slots | required_edits | bridge_paths |',
            '|---|---|---|---|---|---|---:|---:|---:|',
        ]
    )
    for row in report['resolution_rows']:
        lines.append(
            f"| `{row['resolver_id']}` | `{row['resolver_kind']}` | `{row['closure_scope']}` | "
            f"{('`' + row['native_section'] + '`') if row['native_section'] else '—'} | "
            f"{', '.join(f'`{cid}`' for cid in row['affected_claim_family_ids'])} | "
            f"{', '.join(f'`{aid}`' for aid in row['dependent_assumption_ids']) if row['dependent_assumption_ids'] else '—'} | "
            f"{row['blocking_slot_count'] if row['blocking_slot_count'] is not None else '—'} | "
            f"{row['required_edit_count'] if row['required_edit_count'] is not None else '—'} | "
            f"{row['current_bridge_path_count']} |"
        )

    lines.extend(['', '## Closure target details', ''])
    for row in report['resolution_rows']:
        lines.extend(
            [
                f"### {row['resolver_id']}",
                '',
                f"- resolver_kind: `{row['resolver_kind']}`",
                f"- resolver_summary: {row['resolver_summary']}",
                f"- closure_scope: `{row['closure_scope']}`",
                f"- closure_target_summary: {row['closure_target_summary']}",
                f"- affected_claim_family_ids: {', '.join(f'`{cid}`' for cid in row['affected_claim_family_ids'])}",
                f"- dependent_assumption_ids: {', '.join(f'`{aid}`' for aid in row['dependent_assumption_ids']) if row['dependent_assumption_ids'] else 'none'}",
            ]
        )
        if row['native_section']:
            lines.extend(
                [
                    f"- native_section: `{row['native_section']}`",
                    f"- fill_order_index: {row['fill_order_index']}",
                    f"- blocker_slots: {row['blocking_slot_count']} total ({row['template_blocker_count']} template + {row['null_blocker_count']} null)",
                    f"- required_edit_count: {row['required_edit_count']} (cumulative `{row['cumulative_required_edit_count']}`)",
                    f"- section_status_gate: `{row['status_gate_path']}`",
                    f"- data_prefix: `{row['data_prefix']}`",
                    f"- dependency_reason: {row['dependency_reason']}",
                    '- closure_target_paths:',
                ]
            )
            lines.extend([f"  - `{path}`" for path in row['closure_target_paths']])
        else:
            lines.extend(
                [
                    '- native_section: none (cross-section engine contract gap)',
                    f"- dependency_reason: {row['dependency_reason']}",
                    '- closure_target_paths: none (not a seed-local blocker list)',
                ]
            )
        lines.append('- current_bridge_paths:')
        lines.extend([f"  - `{path}`" for path in row['current_bridge_paths']])
        if row['dependent_assumption_summaries']:
            lines.append('- folded_assumption_summaries:')
            lines.extend([f"  - {summary}" for summary in row['dependent_assumption_summaries']])
        else:
            lines.append('- folded_assumption_summaries: none')
        lines.append('')

    lines.extend(
        [
            '## Folded assumptions',
            '',
            '| id | resolver_id | touched_by | summary |',
            '|---|---|---|---|',
        ]
    )
    for row in report['folded_assumption_rows']:
        lines.append(
            f"| `{row['id']}` | `{row['resolver_id']}` | {', '.join(f'`{cid}`' for cid in row['touched_by_claim_family_ids'])} | {row['summary']} |"
        )

    lines.extend(['', '## Recommended next move', '', f"- {report['recommended_next_move']}", ''])
    return '\n'.join(lines)


def main() -> int:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(render(report), encoding='utf-8')
    print(f'wrote {OUT_JSON.relative_to(ROOT)} and {OUT_MD.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
