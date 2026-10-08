#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SEED = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_seed.json'
COMPLETION_GATE = ROOT / 'scripts' / 'tools' / 'rematch_world_benchmark_completion_gate.py'
MUTATION_GUARD = ROOT / 'scripts' / 'tools' / 'rematch_world_benchmark_mutation_guard.py'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_native_fill_map.json'
OUT_MD = ROOT / 'docs' / 'REMATCH_WORLD_BENCHMARK_NATIVE_FILL_MAP.md'


def load_module(path: Path, module_name: str) -> Any:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'could not load {module_name} from {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_report() -> dict[str, Any]:
    completion = load_module(COMPLETION_GATE, 'rematch_world_benchmark_completion_gate')
    guard = load_module(MUTATION_GUARD, 'rematch_world_benchmark_mutation_guard')

    seed = json.loads(SEED.read_text(encoding='utf-8'))
    completion_summary = completion.summarize_completion_status(seed, seed['compact_decision_bundle'])
    blocker_rows = [row for row in completion_summary['blocking_slot_rows'] if row['blocker_kind'] != 'section_status_pending']
    blocker_rows.sort(key=lambda row: (row['section'], row['path']))

    mutable_rows = [row for row in guard.ALLOWED_MUTABLE_PREFIX_ROWS if row['required_change_for_publishable']]
    metadata_rows = [row for row in mutable_rows if row['mutation_kind'].startswith('metadata_')]
    status_rows = [row for row in mutable_rows if row['mutation_kind'] == 'section_status_flip']
    data_rows = [row for row in mutable_rows if row['mutation_kind'] == 'world_section_fill']
    status_by_section = {row['prefix'].split('.', 1)[1]: row for row in status_rows}
    data_by_section: dict[str, dict[str, Any]] = {}
    for row in data_rows:
        section = row['prefix'].split('.', 1)[0]
        data_by_section[section] = row

    blockers_by_section: dict[str, list[dict[str, Any]]] = {}
    for row in blocker_rows:
        blockers_by_section.setdefault(row['section'], []).append(row)

    recommended_fill_order = [section for section in seed['recommended_fill_order'] if section in data_by_section]
    section_rows: list[dict[str, Any]] = []
    for idx, section in enumerate(recommended_fill_order, start=1):
        section_blockers = blockers_by_section.get(section, [])
        blocker_counter = Counter(row['blocker_kind'] for row in section_blockers)
        section_rows.append(
            {
                'fill_order_index': idx,
                'section': section,
                'linked_question_ids': data_by_section[section]['linked_question_ids'],
                'data_prefix': data_by_section[section]['prefix'],
                'status_prefix': status_by_section[section]['prefix'],
                'status_before_fill': seed['section_status'][section],
                'status_after_fill': 'filled',
                'blocking_slot_count': len(section_blockers),
                'template_blocker_count': blocker_counter.get('template_string', 0),
                'null_blocker_count': blocker_counter.get('null_fill_required', 0),
                'blocker_rows': section_blockers,
            }
        )

    metadata_blockers = blockers_by_section.get('benchmark_metadata', [])
    metadata_actions: list[dict[str, Any]] = []
    for row in metadata_rows:
        matching_blocker = next((item for item in metadata_blockers if item['path'] == row['prefix']), None)
        metadata_actions.append(
            {
                'prefix': row['prefix'],
                'mutation_kind': row['mutation_kind'],
                'required_change_for_publishable': True,
                'linked_question_ids': row['linked_question_ids'],
                'reason': row['reason'],
                'currently_blocking': matching_blocker is not None,
                'current_value_summary': matching_blocker['current_value_summary'] if matching_blocker else 'nonblocking_transition_required',
            }
        )

    minimum_publishable_mutation_set = {
        'explicit_fill_blocker_count': completion_summary['status_counts']['blocking_slot_count'],
        'template_blocker_count': completion_summary['status_counts']['template_blocker_count'],
        'null_blocker_count': completion_summary['status_counts']['null_blocker_count'],
        'section_status_flip_count': completion_summary['status_counts']['world_section_status_pending_count'],
        'additional_metadata_transition_count': sum(1 for row in metadata_actions if not row['currently_blocking']),
        'metadata_blocker_count': sum(1 for row in metadata_actions if row['currently_blocking']),
        'mutable_prefix_count': len(mutable_rows),
        'total_required_edit_count': (
            completion_summary['status_counts']['blocking_slot_count']
            + completion_summary['status_counts']['world_section_status_pending_count']
            + sum(1 for row in metadata_actions if not row['currently_blocking'])
        ),
    }

    return {
        'focus': 'collapse the exact editable prefixes, blocker loci, and publishability transitions for the first endogenous rematch-world benchmark into one inheritor-facing fill map',
        'analysis_script': Path(__file__).relative_to(ROOT).as_posix(),
        'seed_path': SEED.relative_to(ROOT).as_posix(),
        'completion_gate_path': COMPLETION_GATE.relative_to(ROOT).as_posix(),
        'mutation_guard_path': MUTATION_GUARD.relative_to(ROOT).as_posix(),
        'recommended_fill_order': recommended_fill_order,
        'minimum_publishable_mutation_set': minimum_publishable_mutation_set,
        'metadata_actions': metadata_actions,
        'section_rows': section_rows,
        'native_section_count': len(section_rows),
        'allowed_decision_null_rows': completion_summary['allowed_decision_null_rows'],
        'allowed_decision_null_count': completion_summary['status_counts']['allowed_decision_null_count'],
        'main_findings': [
            f"The retained seed still carries {completion_summary['status_counts']['blocking_slot_count']} explicit fill blockers: {completion_summary['status_counts']['template_blocker_count']} template strings and {completion_summary['status_counts']['null_blocker_count']} required telemetry fills.",
            f"Publication adds {completion_summary['status_counts']['world_section_status_pending_count']} required world-section status flips plus {sum(1 for row in metadata_actions if not row['currently_blocking'])} extra metadata transition (`artifact_state`), so the smallest publishable edit set is {minimum_publishable_mutation_set['total_required_edit_count']} concrete changes across {len(mutable_rows)} mutable prefixes.",
            f"All world-dependent work still fits inside {len(section_rows)} native sections in the seed order {', '.join(section['section'] for section in section_rows)}, while {completion_summary['status_counts']['allowed_decision_null_count']} copied compact-decision nulls remain explicitly allowed and should not be 'fixed'.",
            'The inheritor therefore needs one disciplined in-place fill pass, not new sidecar reports: bind benchmark identity, replace native placeholders/nulls, flip the five native section statuses, and leave the copied decision surface untouched.',
        ],
        'recommended_next_move': 'Fill the blocker loci in section order, flip `artifact_state` to `filled_benchmark` only when the blocker rows are cleared, then run the mutation guard and completion gate before any publication/prune/package steps.',
    }


def render_md(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append('# Rematch-world benchmark native-fill map')
    lines.append('')
    lines.append(f"Focus: {report['focus']}")
    lines.append('')
    lines.append('## Local result')
    for item in report['main_findings']:
        lines.append(f'- {item}')
    lines.append('')
    lines.append('## Minimum publishable mutation set')
    lines.append('')
    lines.append('| category | count | note |')
    lines.append('|---|---:|---|')
    m = report['minimum_publishable_mutation_set']
    lines.append(f"| explicit fill blockers | `{m['explicit_fill_blocker_count']}` | template strings plus required telemetry fills inside the seed |")
    lines.append(f"| template blockers | `{m['template_blocker_count']}` | placeholders that must be replaced with concrete semantics or ids |")
    lines.append(f"| null blockers | `{m['null_blocker_count']}` | measured values still missing outside the copied compact decision bundle |")
    lines.append(f"| world-section status flips | `{m['section_status_flip_count']}` | `pending_fill -> filled` across the five native sections |")
    lines.append(f"| extra metadata transitions | `{m['additional_metadata_transition_count']}` | required publishability moves that are not already counted as blocker rows |")
    lines.append(f"| mutable prefixes | `{m['mutable_prefix_count']}` | exact legal edit surface from the mutation guard |")
    lines.append(f"| total required edits | `{m['total_required_edit_count']}` | blockers + status flips + nonblocking metadata transitions |")
    lines.append('')
    lines.append('## Metadata actions')
    lines.append('')
    lines.append('| prefix | kind | currently blocking | current value summary | why it changes |')
    lines.append('|---|---|---|---|---|')
    for row in report['metadata_actions']:
        lines.append(
            f"| `{row['prefix']}` | `{row['mutation_kind']}` | {'yes' if row['currently_blocking'] else 'no'} | `{row['current_value_summary']}` | {row['reason']} |"
        )
    lines.append('')
    lines.append('## Native section execution map')
    lines.append('')
    lines.append('| order | section | questions | data prefix | status prefix | blockers | templates | nulls |')
    lines.append('|---|---|---|---|---|---:|---:|---:|')
    for row in report['section_rows']:
        linked = ', '.join(f'`{qid}`' for qid in row['linked_question_ids'])
        lines.append(
            f"| {row['fill_order_index']} | `{row['section']}` | {linked} | `{row['data_prefix']}` | `{row['status_prefix']}` | `{row['blocking_slot_count']}` | `{row['template_blocker_count']}` | `{row['null_blocker_count']}` |"
        )
    lines.append('')
    lines.append('## Exact blocker loci by section')
    lines.append('')
    metadata_rows = [row for row in report['metadata_actions'] if row['currently_blocking']]
    if metadata_rows:
        lines.append('### benchmark_metadata')
        lines.append('')
        for row in metadata_rows:
            lines.append(f"- `{row['prefix']}` — currently `{row['current_value_summary']}` (`{row['mutation_kind']}`)")
        lines.append('')
    for section in report['section_rows']:
        lines.append(f"### {section['section']}")
        lines.append('')
        for row in section['blocker_rows']:
            lines.append(f"- `{row['path']}` — `{row['blocker_kind']}` / `{row['current_value_summary']}`")
        lines.append('')
    lines.append('## Allowed nulls that are not blockers')
    lines.append('')
    for row in report['allowed_decision_null_rows']:
        lines.append(f"- `{row['path']}` — {row['reason']}")
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
    print(f'rematch-world-benchmark-native-fill-map: wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'rematch-world-benchmark-native-fill-map: wrote {OUT_MD.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
