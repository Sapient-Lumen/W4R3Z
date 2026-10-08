#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SEED_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_seed.json'
DECISION_CONTRACT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_decision_contract_snapshot_20260316.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_mutation_surface_snapshot_20260316.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_mutation_surface_snapshot_20260316.md'
SCHEMA_PATH = 'schemas/rematch_world_benchmark_mutation_surface.schema.json'
VALIDATOR_PATH = 'scripts/test/check_rematch_world_benchmark_mutation_surface.py'
GUARD_PATH = 'scripts/tools/rematch_world_benchmark_mutation_guard.py'


def load_module(path: Path, module_name: str) -> Any:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'could not load {module_name} from {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_snapshot() -> dict[str, Any]:
    guard = load_module(ROOT / GUARD_PATH, 'rematch_world_benchmark_mutation_guard')
    seed = guard.load_json(SEED_PATH)
    decision = guard.load_json(DECISION_CONTRACT_PATH)
    guard_summary = guard.inspect_candidate_mutations(seed, seed, decision)

    rows = guard.ALLOWED_MUTABLE_PREFIX_ROWS
    frozen = guard.FROZEN_PREFIX_ROWS
    snapshot = {
        'focus': 'freeze the copied contract surface and define the exact edit surface the inheritor may mutate while filling the first endogenous rematch-world benchmark',
        'snapshot_date': '2026-03-16',
        'seed_artifact_path': SEED_PATH.relative_to(ROOT).as_posix(),
        'decision_contract_path': DECISION_CONTRACT_PATH.relative_to(ROOT).as_posix(),
        'mutation_guard_path': GUARD_PATH,
        'mutable_prefix_rows': rows,
        'frozen_prefix_rows': frozen,
        'allowed_decision_null_rows': guard_summary['allowed_decision_null_rows'],
        'status_counts': {
            'mutable_prefix_count': len(rows),
            'metadata_mutable_prefix_count': sum(1 for row in rows if row['mutation_kind'].startswith('metadata_')),
            'status_flip_prefix_count': sum(1 for row in rows if row['mutation_kind'] == 'section_status_flip'),
            'world_section_mutable_prefix_count': sum(1 for row in rows if row['mutation_kind'] == 'world_section_fill'),
            'frozen_prefix_count': len(frozen),
            'allowed_decision_null_count': len(guard_summary['allowed_decision_null_rows']),
        },
        'main_findings': [
            'A filled rematch benchmark should mutate only 12 seed-designated prefixes: 2 metadata paths, 5 world-section status flips, and 5 world-data prefixes.',
            'The copied canonicalization planner handoff, world-semantics interpretation handoff, winner triage handoff, delta shortlist handoff, paired-ranking interpretation handoff, matching-state interpretation handoff, turnover-tempo interpretation handoff, and compact decision bundle are all frozen alongside the publication / decision-contract pointers.',
            'The three row-based world sections stay prefix-open, so inheritors can add benchmark rows inside the retained artifact instead of creating extra sidecar report families.',
            'The three allowed open-ended decision-contract nulls remain acceptable because they live inside the copied compact decision bundle rather than in unfinished world telemetry.',
        ],
        'recommended_next_move': 'When the first endogenous benchmark is filled, mutate only the listed edit-surface prefixes, keep all seven copied handoff sections plus the compact decision bundle and contract pointers frozen, and run both the mutation guard and the completion gate before publication.',
        'analysis_script': Path(__file__).relative_to(ROOT).as_posix(),
        'schema_path': SCHEMA_PATH,
        'validator_path': VALIDATOR_PATH,
        'source_artifacts': [
            SEED_PATH.relative_to(ROOT).as_posix(),
            DECISION_CONTRACT_PATH.relative_to(ROOT).as_posix(),
            'artifacts/reports/rematch_world_benchmark_fill_status_snapshot_20260316.json',
            'artifacts/reports/rematch_world_publication_contract_snapshot_20260316.json',
        ],
    }
    return snapshot


def render_md(snapshot: dict[str, Any]) -> str:
    lines = [
        '# Rematch world benchmark mutation-surface snapshot — 2026-03-16',
        '',
        'Focus: freeze copied contract state while allowing only the seed edit surface to change during the first endogenous rematch-world benchmark fill',
        '',
        '## Main findings',
    ]
    for finding in snapshot['main_findings']:
        lines.append(f'- {finding}')
    lines.extend([
        '',
        '## Allowed mutable prefixes',
        '',
        '| prefix | kind | linked questions | why it may change |',
        '|---|---|---|---|',
    ])
    for row in snapshot['mutable_prefix_rows']:
        linked = ', '.join(row['linked_question_ids']) if row['linked_question_ids'] else '—'
        lines.append(f"| `{row['prefix']}` | `{row['mutation_kind']}` | {linked} | {row['reason']} |")
    lines.extend([
        '',
        '## Frozen prefixes',
        '',
        '| prefix | frozen kind | why it stays frozen |',
        '|---|---|---|',
    ])
    for row in snapshot['frozen_prefix_rows']:
        lines.append(f"| `{row['prefix']}` | `{row['frozen_kind']}` | {row['reason']} |")
    lines.extend([
        '',
        '## Allowed nulls inside the copied compact decision bundle',
        '',
    ])
    for row in snapshot['allowed_decision_null_rows']:
        lines.append(f"- `{row['path']}` — {row['reason']}")
    lines.extend([
        '',
        '## Recommended next move',
        '',
        snapshot['recommended_next_move'],
        '',
    ])
    return '\n'.join(lines)


def main() -> int:
    snapshot = build_snapshot()
    OUT_JSON.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(render_md(snapshot), encoding='utf-8')
    print(f'mutation-surface-snapshot: wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'mutation-surface-snapshot: wrote {OUT_MD.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
