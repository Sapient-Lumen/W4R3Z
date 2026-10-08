#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_seed.json'
DEFAULT_DECISION_CONTRACT = ROOT / 'artifacts' / 'reports' / 'rematch_decision_contract_snapshot_20260316.json'
WORLD_SECTIONS = [
    'world_semantics_contract',
    'matching_state_contract',
    'occupancy_accounting_contract',
    'turnover_tempo_contract',
    'paired_ranking_views_contract',
]
EXPECTED_TOP_LEVEL_SECTIONS = WORLD_SECTIONS + ['compact_decision_bundle']
QUESTION_IDS_BY_SECTION = {
    'world_semantics_contract': ['SQ-012'],
    'matching_state_contract': ['SQ-013'],
    'occupancy_accounting_contract': ['SQ-014'],
    'turnover_tempo_contract': ['SQ-015'],
    'paired_ranking_views_contract': ['SQ-016'],
    'compact_decision_bundle': [f'SQ-0{i}' for i in range(17, 27)],
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def _path_join(base: str, key: str) -> str:
    return f'{base}.{key}' if base else key


def _section_for_path(path: str) -> str:
    if path == 'benchmark_id':
        return 'benchmark_metadata'
    for section in EXPECTED_TOP_LEVEL_SECTIONS:
        if path == section or path.startswith(f'{section}.'):
            return section
    return 'unknown'


def _question_ids_for_section(section: str) -> list[str]:
    return QUESTION_IDS_BY_SECTION.get(section, [])


def _walk_collect(node: Any, path: str = '') -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    template_rows: list[dict[str, Any]] = []
    null_rows: list[dict[str, Any]] = []
    if node is None:
        null_rows.append({'path': path, 'section': _section_for_path(path), 'linked_question_ids': _question_ids_for_section(_section_for_path(path))})
        return template_rows, null_rows
    if isinstance(node, str):
        if 'TEMPLATE' in node:
            template_rows.append(
                {
                    'path': path,
                    'section': _section_for_path(path),
                    'linked_question_ids': _question_ids_for_section(_section_for_path(path)),
                    'placeholder_value': node,
                }
            )
        return template_rows, null_rows
    if isinstance(node, dict):
        for key, value in node.items():
            child_templates, child_nulls = _walk_collect(value, _path_join(path, key))
            template_rows.extend(child_templates)
            null_rows.extend(child_nulls)
        return template_rows, null_rows
    if isinstance(node, list):
        for idx, value in enumerate(node):
            child_templates, child_nulls = _walk_collect(value, f'{path}[{idx}]')
            template_rows.extend(child_templates)
            null_rows.extend(child_nulls)
    return template_rows, null_rows


def summarize_completion_status(
    artifact: dict[str, Any],
    decision_contract: dict[str, Any],
) -> dict[str, Any]:
    template_rows, null_rows = _walk_collect(artifact)
    allowed_decision_null_rows: list[dict[str, Any]] = []
    unexpected_null_rows: list[dict[str, Any]] = []

    for row in null_rows:
        path = row['path']
        if path.startswith('compact_decision_bundle.'):
            allowed_decision_null_rows.append(
                {
                    **row,
                    'reason': 'open_ended_interval_from_copied_decision_contract',
                }
            )
        else:
            unexpected_null_rows.append(row)

    status = artifact.get('section_status', {})
    world_status_blockers: list[dict[str, Any]] = []
    for section in WORLD_SECTIONS:
        if status.get(section) != 'filled':
            world_status_blockers.append(
                {
                    'section': section,
                    'current_status': status.get(section),
                    'required_status': 'filled',
                    'linked_question_ids': _question_ids_for_section(section),
                }
            )

    compact_status_ok = status.get('compact_decision_bundle') == 'copied_from_standing_contract'
    decision_bundle_matches = artifact.get('compact_decision_bundle') == decision_contract
    completion_ready = (
        artifact.get('artifact_state') == 'filled_benchmark'
        and not template_rows
        and not unexpected_null_rows
        and not world_status_blockers
        and compact_status_ok
        and decision_bundle_matches
    )

    blocker_rows = [
        *[
            {
                'blocker_kind': 'template_string',
                'path': row['path'],
                'section': row['section'],
                'linked_question_ids': row['linked_question_ids'],
                'current_value_summary': row['placeholder_value'],
            }
            for row in template_rows
        ],
        *[
            {
                'blocker_kind': 'null_fill_required',
                'path': row['path'],
                'section': row['section'],
                'linked_question_ids': row['linked_question_ids'],
                'current_value_summary': 'null',
            }
            for row in unexpected_null_rows
        ],
        *[
            {
                'blocker_kind': 'section_status_pending',
                'path': f'section_status.{row["section"]}',
                'section': row['section'],
                'linked_question_ids': row['linked_question_ids'],
                'current_value_summary': str(row['current_status']),
            }
            for row in world_status_blockers
        ],
    ]
    blocker_rows.sort(key=lambda row: (row['section'], row['path'], row['blocker_kind']))

    counts = Counter(row['section'] for row in blocker_rows if row['blocker_kind'] != 'section_status_pending')
    return {
        'completion_ready': completion_ready,
        'artifact_state': artifact.get('artifact_state'),
        'decision_bundle_matches_standing_contract': decision_bundle_matches,
        'compact_decision_bundle_status_ok': compact_status_ok,
        'blocking_slot_rows': blocker_rows,
        'allowed_decision_null_rows': sorted(allowed_decision_null_rows, key=lambda row: row['path']),
        'status_counts': {
            'blocking_slot_count': len([row for row in blocker_rows if row['blocker_kind'] != 'section_status_pending']),
            'template_blocker_count': sum(1 for row in blocker_rows if row['blocker_kind'] == 'template_string'),
            'null_blocker_count': sum(1 for row in blocker_rows if row['blocker_kind'] == 'null_fill_required'),
            'world_section_status_pending_count': len(world_status_blockers),
            'allowed_decision_null_count': len(allowed_decision_null_rows),
            'sections_with_fill_blockers': len(counts),
        },
        'blocking_slot_counts_by_section': dict(sorted(counts.items())),
        'world_section_status_blockers': world_status_blockers,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Assess whether a rematch-world benchmark artifact is still a template or is ready for publication.')
    parser.add_argument('artifact', nargs='?', default=str(DEFAULT_ARTIFACT), help='Path to the benchmark JSON artifact to inspect.')
    parser.add_argument('--decision-contract', default=str(DEFAULT_DECISION_CONTRACT), help='Path to the standing compact decision contract JSON.')
    parser.add_argument('--json', action='store_true', help='Emit the full completion summary as JSON.')
    args = parser.parse_args()

    artifact_path = Path(args.artifact)
    decision_path = Path(args.decision_contract)
    artifact = load_json(artifact_path)
    decision = load_json(decision_path)
    summary = summarize_completion_status(artifact, decision)
    summary['artifact_path'] = artifact_path.resolve().relative_to(ROOT).as_posix() if artifact_path.resolve().is_relative_to(ROOT) else str(artifact_path)
    summary['decision_contract_path'] = decision_path.resolve().relative_to(ROOT).as_posix() if decision_path.resolve().is_relative_to(ROOT) else str(decision_path)

    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    state = 'ready' if summary['completion_ready'] else 'not_ready'
    print(
        'rematch-world-benchmark-completion-gate: '
        f"{state} ({summary['status_counts']['blocking_slot_count']} fill blockers, "
        f"{summary['status_counts']['allowed_decision_null_count']} allowed decision nulls, "
        f"{summary['status_counts']['world_section_status_pending_count']} pending world section statuses)"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
