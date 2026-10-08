#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
NATIVE_FILL_MAP = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_native_fill_map.json'
WORLD_EMISSION_CARD = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_world_emission_card.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_landing_ladder.json'
OUT_MD = ROOT / 'docs' / 'REMATCH_WORLD_BENCHMARK_LANDING_LADDER.md'

SECTION_REASON = {
    'world_semantics_contract': 'Define role assignment plus carry/reset semantics before attaching quantitative benchmark rows to one institution.',
    'matching_state_contract': 'Declare rematch delay versus matching-efficiency semantics before any dead-round or turnover comparison is interpreted.',
    'occupancy_accounting_contract': 'Populate aggregate-versus-in-match welfare decomposition only after the matching-state terms are concrete.',
    'turnover_tempo_contract': 'Bind turnover metrics after the matching-state semantics and occupancy decomposition are already fixed.',
    'paired_ranking_views_contract': 'Publish aggregate-versus-in-match leaderboards only after the underlying payoff decomposition has been filled.',
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def build_report() -> dict[str, Any]:
    native = load_json(NATIVE_FILL_MAP)
    emission = load_json(WORLD_EMISSION_CARD)

    metadata_actions = native['metadata_actions']
    blocking_metadata = [row for row in metadata_actions if row['currently_blocking']]
    nonblocking_metadata = [row for row in metadata_actions if not row['currently_blocking']]
    if len(blocking_metadata) != 1 or len(nonblocking_metadata) != 1:
        raise RuntimeError('expected exactly one blocking and one nonblocking metadata action')

    edit_stage_rows: list[dict[str, Any]] = []
    cumulative = 0

    benchmark_row = blocking_metadata[0]
    cumulative += 1
    edit_stage_rows.append(
        {
            'order': 1,
            'stage': 'bind benchmark identity',
            'stage_key': 'benchmark_id_binding',
            'required_edit_count': 1,
            'cumulative_required_edit_count': cumulative,
            'blocker_clear_count': 1,
            'section_status_flip_count': 0,
            'changed_prefixes': [benchmark_row['prefix']],
            'linked_question_ids': benchmark_row['linked_question_ids'],
            'dependency_reason': 'Anchor the retained artifact to one concrete benchmark id before publishing native rows or package receipts against it.',
        }
    )

    for row in sorted(native['section_rows'], key=lambda item: item['fill_order_index']):
        required = row['blocking_slot_count'] + 1
        cumulative += required
        edit_stage_rows.append(
            {
                'order': len(edit_stage_rows) + 1,
                'stage': f"fill {row['section']}",
                'stage_key': row['section'],
                'required_edit_count': required,
                'cumulative_required_edit_count': cumulative,
                'blocker_clear_count': row['blocking_slot_count'],
                'section_status_flip_count': 1,
                'changed_prefixes': [row['data_prefix'], row['status_prefix']],
                'linked_question_ids': row['linked_question_ids'],
                'template_blocker_count': row['template_blocker_count'],
                'null_blocker_count': row['null_blocker_count'],
                'dependency_reason': SECTION_REASON[row['section']],
            }
        )

    artifact_row = nonblocking_metadata[0]
    cumulative += 1
    edit_stage_rows.append(
        {
            'order': len(edit_stage_rows) + 1,
            'stage': 'flip artifact state',
            'stage_key': 'artifact_state_transition',
            'required_edit_count': 1,
            'cumulative_required_edit_count': cumulative,
            'blocker_clear_count': 0,
            'section_status_flip_count': 0,
            'changed_prefixes': [artifact_row['prefix']],
            'linked_question_ids': artifact_row['linked_question_ids'],
            'dependency_reason': 'Only mark the artifact `filled_benchmark` after every blocking native locus has been replaced with concrete content.',
        }
    )

    if cumulative != native['minimum_publishable_mutation_set']['total_required_edit_count']:
        raise RuntimeError('edit ladder total does not match native fill map total')

    landing_steps = emission['landing_steps']
    closeout_phase_rows = [
        {
            'order': 1,
            'phase': 'seed guards',
            'landing_step_orders': [1, 2],
            'step_count': 2,
            'receipts': [landing_steps[0]['receipt_path'], landing_steps[1]['receipt_path']],
            'tools': [landing_steps[0]['tool_path'], landing_steps[1]['tool_path']],
            'success_summaries': [landing_steps[0]['success_summary'], landing_steps[1]['success_summary']],
            'why_now': 'Prove the copied surface is still frozen and retain only tiny provenance before compiling a filled artifact.',
        },
        {
            'order': 2,
            'phase': 'filled artifact validation',
            'landing_step_orders': [3, 4],
            'step_count': 2,
            'receipts': [landing_steps[2]['receipt_path'], landing_steps[3]['receipt_path']],
            'tools': [landing_steps[2]['tool_path'], landing_steps[3]['tool_path']],
            'success_summaries': [landing_steps[2]['success_summary'], landing_steps[3]['success_summary']],
            'why_now': 'Compile the in-place fill, run the mutation/completion gates, and prove the copied handoffs survived unchanged.',
        },
        {
            'order': 3,
            'phase': 'retained emission proof',
            'landing_step_orders': [5, 6],
            'step_count': 2,
            'receipts': [landing_steps[4]['receipt_path'], landing_steps[5]['receipt_path']],
            'tools': [landing_steps[4]['tool_path'], landing_steps[5]['tool_path']],
            'success_summaries': [landing_steps[4]['success_summary'], landing_steps[5]['success_summary']],
            'why_now': 'Collapse the phase-3 benchmark emission into one compact retained bundle and then audit the durable publication spine.',
        },
        {
            'order': 4,
            'phase': 'transient exit and prune',
            'landing_step_orders': [7, 8, 9],
            'step_count': 3,
            'receipts': [landing_steps[6]['receipt_path'], landing_steps[7]['receipt_path'], landing_steps[8]['receipt_path']],
            'tools': [landing_steps[6]['tool_path'], landing_steps[7]['tool_path'], landing_steps[8]['tool_path']],
            'success_summaries': [landing_steps[6]['success_summary'], landing_steps[7]['success_summary'], landing_steps[8]['success_summary']],
            'why_now': 'Decide which intermediates may exit, prune them by rule, and prove the cleaned tree is actually zip-ready.',
        },
        {
            'order': 5,
            'phase': 'final authority receipts',
            'landing_step_orders': [10],
            'step_count': 1,
            'receipts': [landing_steps[9]['receipt_path']],
            'tools': [landing_steps[9]['tool_path']],
            'success_summaries': [landing_steps[9]['success_summary']],
            'why_now': 'Emit the inheritor-facing chain and package proofs only after the post-prune tree is already known good.',
        },
    ]

    cumulative_sequence = [row['cumulative_required_edit_count'] for row in edit_stage_rows]
    required_total = native['minimum_publishable_mutation_set']['total_required_edit_count']

    return {
        'focus': 'collapse the first native rematch-world publication into one exact edit ladder plus one exact closeout ladder so the next implementor can land the benchmark without reopening scattered receipts',
        'analysis_script': Path(__file__).relative_to(ROOT).as_posix(),
        'upstream_reports': [
            NATIVE_FILL_MAP.relative_to(ROOT).as_posix(),
            WORLD_EMISSION_CARD.relative_to(ROOT).as_posix(),
        ],
        'required_edit_total': required_total,
        'edit_stage_count': len(edit_stage_rows),
        'closeout_phase_count': len(closeout_phase_rows),
        'edit_stage_rows': edit_stage_rows,
        'closeout_phase_rows': closeout_phase_rows,
        'cumulative_required_edit_sequence': cumulative_sequence,
        'main_findings': [
            f"The minimum publishable native-fill path is an exact 7-stage edit ladder ending at {required_total} required edits with cumulative checkpoints {', '.join(str(item) for item in cumulative_sequence)}.",
            'The only blocking metadata mutation is `benchmark_id`; every other required edit belongs to one of the five native world sections, and `artifact_state` flips only after those blockers are gone.',
            'The section order is not arbitrary: define institution semantics first, then define matching/dead-time semantics, then publish occupancy and turnover telemetry, and only then publish paired ranking views.',
            'After the edit ladder, the closeout path compresses to five proof phases: seed guards, filled-artifact validation, retained emission proof, transient exit/prune, and final chain/package authority.',
        ],
        'recommended_next_move': 'Replay the 7-stage edit ladder to reach the 30-edit publication floor, then walk the 5-phase closeout ladder in order instead of improvising receipts or retaining extra scratch.',
    }


def render_md(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append('# Rematch-world benchmark landing ladder')
    lines.append('')
    lines.append(f"Focus: {report['focus']}")
    lines.append('')
    lines.append('## Local result')
    for item in report['main_findings']:
        lines.append(f'- {item}')
    lines.append('')
    lines.append('## Exact edit ladder')
    lines.append('')
    lines.append('| order | stage | required edits | cumulative | blocker clears | status flips | prefixes | why this order |')
    lines.append('|---|---|---:|---:|---:|---:|---|---|')
    for row in report['edit_stage_rows']:
        prefixes = ', '.join(f'`{item}`' for item in row['changed_prefixes'])
        lines.append(
            f"| {row['order']} | {row['stage']} | `{row['required_edit_count']}` | `{row['cumulative_required_edit_count']}` | `{row['blocker_clear_count']}` | `{row['section_status_flip_count']}` | {prefixes} | {row['dependency_reason']} |"
        )
    lines.append('')
    lines.append('## Post-edit closeout ladder')
    lines.append('')
    lines.append('| order | phase | landing steps | receipts | why now |')
    lines.append('|---|---|---|---|---|')
    for row in report['closeout_phase_rows']:
        step_orders = ', '.join(str(item) for item in row['landing_step_orders'])
        receipts = '; '.join(f'`{item}`' for item in row['receipts'])
        lines.append(f"| {row['order']} | {row['phase']} | `{step_orders}` | {receipts} | {row['why_now']} |")
    lines.append('')
    lines.append('## Implementor takeaway')
    lines.append('')
    lines.append(report['recommended_next_move'])
    lines.append('')
    return '\n'.join(lines)


def main() -> int:
    report = build_report()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(render_md(report) + '\n', encoding='utf-8')
    print(f'rematch-world-benchmark-landing-ladder: wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'rematch-world-benchmark-landing-ladder: wrote {OUT_MD.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
