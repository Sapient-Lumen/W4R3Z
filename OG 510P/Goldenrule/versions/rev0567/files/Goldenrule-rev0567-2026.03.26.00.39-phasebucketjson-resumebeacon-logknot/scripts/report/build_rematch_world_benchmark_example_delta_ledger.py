#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SEED_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_seed.json'
COMPILED_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_compiled_artifact.json'
PACKET_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_evidence_packet.json'
EVIDENCE_RECEIPT_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_evidence_receipt.json'
DECISION_CONTRACT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_decision_contract_snapshot_20260316.json'
NATIVE_FILL_MAP_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_native_fill_map.json'
LANDING_LADDER_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_landing_ladder.json'
BUNDLE_TOOL_PATH = ROOT / 'scripts' / 'tools' / 'build_rematch_world_benchmark_publication_bundle_receipt.py'
MUTATION_GUARD_PATH = ROOT / 'scripts' / 'tools' / 'rematch_world_benchmark_mutation_guard.py'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_example_delta_ledger.json'
OUT_MD = ROOT / 'docs' / 'REMATCH_WORLD_BENCHMARK_EXAMPLE_DELTA_LEDGER.md'

OPTIONAL_INSERTION_PATHS = {
    'occupancy_accounting_contract.policy_rows[1]': 'extra occupancy row beyond the one-row publication floor',
    'turnover_tempo_contract.policy_rows[1]': 'extra turnover row beyond the one-row publication floor',
    'paired_ranking_views_contract.leaderboard_rows[1]': 'extra paired-ranking row beyond the one-row publication floor',
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'could not load {name} from {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def summarize(value: Any) -> str:
    if value is None:
        return 'null'
    if isinstance(value, str):
        return value if len(value) <= 96 else value[:93] + '...'
    if isinstance(value, (int, float, bool)):
        return json.dumps(value)
    if isinstance(value, list):
        return f'list(len={len(value)})'
    if isinstance(value, dict):
        keys = list(value)
        preview = ', '.join(keys[:3])
        suffix = '' if len(keys) <= 3 else ', ...'
        return f'dict(keys={preview}{suffix})'
    return repr(value)


def collect_changed_paths(before: Any, after: Any, path: str = '') -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if type(before) is not type(after):
        rows.append({'path': path, 'change_mode': 'type_or_null_fill', 'before_value': before, 'after_value': after})
        return rows
    if isinstance(before, dict):
        for key in sorted(set(before) | set(after)):
            child = f'{path}.{key}' if path else key
            if key not in before:
                rows.append({'path': child, 'change_mode': 'added', 'before_value': None, 'after_value': after[key]})
            elif key not in after:
                rows.append({'path': child, 'change_mode': 'removed', 'before_value': before[key], 'after_value': None})
            else:
                rows.extend(collect_changed_paths(before[key], after[key], child))
        return rows
    if isinstance(before, list):
        shared = min(len(before), len(after))
        for idx in range(shared):
            rows.extend(collect_changed_paths(before[idx], after[idx], f'{path}[{idx}]'))
        for idx in range(shared, len(after)):
            rows.append({'path': f'{path}[{idx}]', 'change_mode': 'added', 'before_value': None, 'after_value': after[idx]})
        for idx in range(shared, len(before)):
            rows.append({'path': f'{path}[{idx}]', 'change_mode': 'removed', 'before_value': before[idx], 'after_value': None})
        return rows
    if before != after:
        rows.append({'path': path, 'change_mode': 'value_change', 'before_value': before, 'after_value': after})
    return rows


def classify_change(path: str, row: dict[str, Any], native: dict[str, Any], allowed_rows: list[dict[str, Any]]) -> dict[str, Any]:
    allowed_prefixes = [item['prefix'] for item in allowed_rows]
    matching_prefix = next(
        (
            prefix
            for prefix in sorted(allowed_prefixes, key=len, reverse=True)
            if path == prefix or path.startswith(prefix + '.') or path.startswith(prefix + '[')
        ),
        None,
    )
    if matching_prefix is None:
        raise RuntimeError(f'changed path outside allowed mutable prefixes: {path}')

    section = path.split('.', 1)[0].split('[', 1)[0]
    linked_question_ids: list[str] = []
    required = False
    change_class = 'other_allowed_change'
    blocker_kind = None
    reason = 'Allowed mutation under the standing rematch-world fill surface.'

    if path in OPTIONAL_INSERTION_PATHS:
        required = False
        change_class = 'optional_row_insertion'
        blocker_kind = 'row_insertion'
        if path.startswith('occupancy_accounting_contract'):
            section = 'occupancy_accounting_contract'
            linked_question_ids = ['SQ-014']
        elif path.startswith('turnover_tempo_contract'):
            section = 'turnover_tempo_contract'
            linked_question_ids = ['SQ-015']
        else:
            section = 'paired_ranking_views_contract'
            linked_question_ids = ['SQ-016']
        reason = OPTIONAL_INSERTION_PATHS[path]
    elif path == 'artifact_state':
        required = True
        change_class = 'metadata_transition'
        blocker_kind = 'metadata_transition'
        action = next(item for item in native['metadata_actions'] if item['prefix'] == 'artifact_state')
        linked_question_ids = action['linked_question_ids']
        reason = action['reason']
        section = 'benchmark_metadata'
    elif path == 'benchmark_id':
        required = True
        change_class = 'metadata_binding'
        blocker_kind = 'template_string'
        action = next(item for item in native['metadata_actions'] if item['prefix'] == 'benchmark_id')
        linked_question_ids = action['linked_question_ids']
        reason = action['reason']
        section = 'benchmark_metadata'
    elif path.startswith('section_status.'):
        required = True
        change_class = 'section_status_flip'
        blocker_kind = 'section_status_flip'
        status_section = path.split('.', 1)[1]
        rule = next(item for item in allowed_rows if item['prefix'] == path)
        linked_question_ids = rule['linked_question_ids']
        reason = rule['reason']
        section = status_section
    else:
        matched = None
        for section_row in native['section_rows']:
            for blocker in section_row['blocker_rows']:
                if blocker['path'] == path:
                    matched = (section_row, blocker)
                    break
            if matched is not None:
                break
        if matched is None:
            raise RuntimeError(f'unclassified changed path inside allowed surface: {path}')
        section_row, blocker = matched
        required = True
        change_class = 'world_fill_blocker_clear'
        blocker_kind = blocker['blocker_kind']
        linked_question_ids = blocker['linked_question_ids']
        reason = f"clear {blocker['blocker_kind']} under {section_row['section']}"
        section = section_row['section']

    return {
        'path': path,
        'allowed_prefix': matching_prefix,
        'section': section,
        'required_for_publishable': required,
        'change_class': change_class,
        'blocker_kind': blocker_kind,
        'linked_question_ids': linked_question_ids,
        'reason': reason,
        'change_mode': row['change_mode'],
        'before_summary': summarize(row['before_value']),
        'after_summary': summarize(row['after_value']),
    }


def build_report() -> dict[str, Any]:
    seed = load_json(SEED_PATH)
    compiled_snapshot = load_json(COMPILED_PATH)
    native = load_json(NATIVE_FILL_MAP_PATH)
    ladder = load_json(LANDING_LADDER_PATH)
    mutation_guard = load_module('rematch_world_benchmark_mutation_guard', MUTATION_GUARD_PATH)
    bundle_tool = load_module('build_rematch_world_benchmark_publication_bundle_receipt', BUNDLE_TOOL_PATH)
    decision_contract = load_json(DECISION_CONTRACT_PATH) if DECISION_CONTRACT_PATH.exists() else seed['compact_decision_bundle']

    receipt, _patch, compiled_from_tool = bundle_tool.build_bundle_receipt(
        packet=load_json(PACKET_PATH),
        evidence_receipt=load_json(EVIDENCE_RECEIPT_PATH),
        seed=seed,
        decision_contract=decision_contract,
        packet_path=PACKET_PATH,
        evidence_receipt_path=EVIDENCE_RECEIPT_PATH,
        seed_path=SEED_PATH,
        decision_contract_path=DECISION_CONTRACT_PATH,
        artifact_output_path=None,
        patch_output_path=None,
    )
    if compiled_snapshot != compiled_from_tool:
        raise RuntimeError('compiled benchmark snapshot drifted from the canonical packet->patch->artifact toolchain')
    if not receipt['patch_elision_ready']:
        raise RuntimeError('expected example publication bundle receipt to be patch-elision ready')

    raw_changes = collect_changed_paths(seed, compiled_snapshot)
    if len(raw_changes) != 33:
        raise RuntimeError(f'expected 33 real changed JSON paths, found {len(raw_changes)}')

    changed_rows = [classify_change(item['path'], item, native, mutation_guard.ALLOWED_MUTABLE_PREFIX_ROWS) for item in raw_changes]
    changed_rows.sort(key=lambda row: (not row['required_for_publishable'], row['section'], row['path']))
    for idx, row in enumerate(changed_rows, start=1):
        row['order'] = idx

    required_rows = [row for row in changed_rows if row['required_for_publishable']]
    optional_rows = [row for row in changed_rows if not row['required_for_publishable']]
    if len(required_rows) != native['minimum_publishable_mutation_set']['total_required_edit_count']:
        raise RuntimeError('required changed-path count does not match native fill map publishability floor')
    if len(optional_rows) != 3:
        raise RuntimeError('expected exactly three optional row insertions in compiled example')

    class_counts = Counter(row['change_class'] for row in changed_rows)
    section_delta_rows = []
    section_order = ['benchmark_metadata', *[row['section'] for row in native['section_rows']]]
    for section in section_order:
        scoped = [row for row in changed_rows if row['section'] == section]
        if not scoped:
            continue
        section_delta_rows.append(
            {
                'section': section,
                'required_change_count': sum(1 for row in scoped if row['required_for_publishable']),
                'optional_change_count': sum(1 for row in scoped if not row['required_for_publishable']),
                'changed_paths': [row['path'] for row in scoped],
                'linked_question_ids': sorted({qid for row in scoped for qid in row['linked_question_ids']}),
            }
        )

    frozen_roots = [
        'canonicalization_planner_contract',
        'winner_triage_handoff',
        'delta_shortlist_handoff',
        'paired_ranking_interpretation_handoff',
        'matching_state_interpretation_handoff',
        'turnover_tempo_interpretation_handoff',
        'world_semantics_interpretation_handoff',
        'compact_decision_bundle',
    ]
    unchanged_frozen_roots = [name for name in frozen_roots if seed[name] == compiled_snapshot[name]]

    return {
        'focus': 'derive one exact seed-to-compiled change ledger for the synthetic first rematch-world publication so the eventual implementor can see the concrete mutation shape without reopening the seed, compiled artifact, and native-fill map separately',
        'analysis_script': Path(__file__).relative_to(ROOT).as_posix(),
        'input_paths': {
            'seed_path': SEED_PATH.relative_to(ROOT).as_posix(),
            'compiled_artifact_path': COMPILED_PATH.relative_to(ROOT).as_posix(),
            'evidence_packet_path': PACKET_PATH.relative_to(ROOT).as_posix(),
            'evidence_receipt_path': EVIDENCE_RECEIPT_PATH.relative_to(ROOT).as_posix(),
            'decision_contract_path': DECISION_CONTRACT_PATH.relative_to(ROOT).as_posix(),
        },
        'upstream_reports': [
            NATIVE_FILL_MAP_PATH.relative_to(ROOT).as_posix(),
            LANDING_LADDER_PATH.relative_to(ROOT).as_posix(),
        ],
        'total_changed_path_count': len(changed_rows),
        'required_publishable_change_count': len(required_rows),
        'optional_change_count': len(optional_rows),
        'change_class_counts': dict(sorted(class_counts.items())),
        'changed_path_rows': changed_rows,
        'section_delta_rows': section_delta_rows,
        'optional_paths': [row['path'] for row in optional_rows],
        'unchanged_frozen_roots': unchanged_frozen_roots,
        'compiled_snapshot_matches_live_toolchain': True,
        'patch_elision_ready': bool(receipt['patch_elision_ready']),
        'main_findings': [
            f"The synthetic compiled artifact changes exactly {len(changed_rows)} real JSON paths relative to the standing seed: {len(required_rows)} are the minimum publication changes and {len(optional_rows)} are purely optional second-row insertions.",
            'Every changed path stays inside the already-allowed mutable prefixes from the native-fill map; no copied handoff root and no compact decision-contract content changes at all.',
            f"The exact required part of the example matches the landing ladder’s publication floor of {ladder['required_edit_total']} edits, while the extra occupancy / turnover / paired-ranking row insertions show how larger policy sets fit inside the same legal edit surface.",
            'Because the compiled example is rebuilt live from the evidence-packet toolchain before diffing, this ledger doubles as a stale-snapshot guard rather than only another prose summary.',
        ],
        'recommended_next_move': 'Use this ledger as the smallest concrete mutation witness when the first real native fill starts: follow the 30 required paths first, then decide deliberately whether any second-row additions are worth retaining beyond that publication floor.',
    }


def render_md(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append('# Rematch-world benchmark example delta ledger')
    lines.append('')
    lines.append(f"Focus: {report['focus']}")
    lines.append('')
    lines.append('## Local result')
    for item in report['main_findings']:
        lines.append(f'- {item}')
    lines.append('')
    lines.append('## Change counts')
    lines.append('')
    lines.append('| category | count | note |')
    lines.append('|---|---:|---|')
    lines.append(f"| total changed paths | `{report['total_changed_path_count']}` | exact seed-to-compiled JSON paths, excluding redundant list-length pseudo-diffs |")
    lines.append(f"| required publication changes | `{report['required_publishable_change_count']}` | matches the standing publication floor from the native-fill map / landing ladder |")
    lines.append(f"| optional changes | `{report['optional_change_count']}` | extra second-row insertions inside already-allowed mutable arrays |")
    for key, value in sorted(report['change_class_counts'].items()):
        lines.append(f"| {key.replace('_', ' ')} | `{value}` | exact class count in the synthetic compiled example |")
    lines.append('')
    lines.append('## Section delta summary')
    lines.append('')
    lines.append('| section | required | optional | linked questions |')
    lines.append('|---|---:|---:|---|')
    for row in report['section_delta_rows']:
        linked = ', '.join(f'`{qid}`' for qid in row['linked_question_ids']) if row['linked_question_ids'] else '—'
        lines.append(f"| `{row['section']}` | `{row['required_change_count']}` | `{row['optional_change_count']}` | {linked} |")
    lines.append('')
    lines.append('## Exact changed paths')
    lines.append('')
    lines.append('| # | path | class | required | before | after |')
    lines.append('|---:|---|---|---|---|---|')
    for row in report['changed_path_rows']:
        lines.append(
            f"| {row['order']} | `{row['path']}` | `{row['change_class']}` | {'yes' if row['required_for_publishable'] else 'no'} | `{row['before_summary']}` | `{row['after_summary']}` |"
        )
    lines.append('')
    lines.append('## Frozen roots that stay untouched')
    lines.append('')
    for item in report['unchanged_frozen_roots']:
        lines.append(f'- `{item}`')
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
    print(f'rematch-world-benchmark-example-delta-ledger: wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'rematch-world-benchmark-example-delta-ledger: wrote {OUT_MD.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
