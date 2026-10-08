#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
RETENTION_EXIT_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_retention_exit_receipt.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_prune_snapshot_20260316.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_prune_snapshot_20260316.md'
SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_prune_receipt.schema.json'


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'could not load module {name} from {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _mib(byte_count: int) -> float:
    return round(byte_count / (1024 * 1024), 6)


def build_snapshot() -> dict[str, Any]:
    prune_tool = _load_module(
        'prune_rematch_world_benchmark_transients',
        ROOT / 'scripts' / 'tools' / 'prune_rematch_world_benchmark_transients.py',
    )
    retention_exit_receipt = prune_tool.load_json(RETENTION_EXIT_PATH)
    receipt = prune_tool.build_prune_receipt(
        retention_exit_receipt,
        RETENTION_EXIT_PATH,
        root=ROOT,
        execute=False,
        prune_empty_dirs=True,
    )
    counts = receipt['counts']
    transient_rows = receipt['transient_rows']
    concrete_rows = [row for row in transient_rows if row['path'] is not None]
    already_elided_rows = [row for row in transient_rows if row['path'] is None]

    findings = [
        (
            f"The standing retention-exit receipt is already prune-ready in dry-run mode: {counts['would_delete_count']} concrete transient files "
            f"cover {counts['concrete_exit_bytes']} bytes ({_mib(int(counts['concrete_exit_bytes']))} MiB) and can leave by rule rather than by memory."
        ),
        (
            f"The reconstructible compiled fill patch is already elided from the retained example workflow, so the only remaining concrete exit candidates are the {counts['would_delete_count']} hashed scratch-source files."
        ),
        (
            f"Dry-run pruning finds {counts['blocked_count']} blocked rows and {counts['already_absent_count']} already-absent rows, so the current retained example demonstrates a clean cleanup boundary instead of a speculative one."
        ),
    ]

    snapshot = {
        'focus': 'turn the rematch-world retention-exit receipt into one explicit cleanup action so future sessions can delete scratch/intermediate objects by rule after the publication spine is stable',
        'snapshot_date': '2026-03-16',
        'analysis_script': 'scripts/report/build_rematch_world_benchmark_prune_snapshot.py',
        'retention_exit_receipt_path': RETENTION_EXIT_PATH.relative_to(ROOT).as_posix(),
        'dry_run_receipt': receipt,
        'headline_findings': findings,
        'concrete_exit_candidates': [
            {
                'label': row['label'],
                'path': row['path'],
                'byte_count': row['byte_count'],
                'status': row['status'],
            }
            for row in concrete_rows
        ],
        'already_elided_transients': [
            {
                'label': row['label'],
                'byte_count': row['byte_count'],
                'status': row['status'],
            }
            for row in already_elided_rows
        ],
    }
    return snapshot


def render_md(snapshot: dict[str, Any]) -> str:
    receipt = snapshot['dry_run_receipt']
    counts = receipt['counts']
    lines = [
        '# Rematch World Benchmark Prune Snapshot',
        '',
        f"- snapshot_date: {snapshot['snapshot_date']}",
        f"- retention_exit_receipt_path: `{snapshot['retention_exit_receipt_path']}`",
        f"- execution_mode: `{receipt['execution_mode']}`",
        f"- prune_ready: `{str(receipt['prune_ready']).lower()}`",
        '',
        '## Headline findings',
        '',
    ]
    for finding in snapshot['headline_findings']:
        lines.append(f'- {finding}')
    lines.extend(
        [
            '',
            '## Dry-run counts',
            '',
            f"- total transient rows: `{counts['total_transient_count']}`",
            f"- concrete exit candidates: `{counts['concrete_path_count']}`",
            f"- would delete now: `{counts['would_delete_count']}`",
            f"- already elided / unlinked: `{counts['already_elided_unlinked_count']}`",
            f"- blocked rows: `{counts['blocked_count']}`",
            f"- concrete exit bytes: `{counts['concrete_exit_bytes']}`",
            '',
            '## Concrete exit candidates',
            '',
            '| label | path | byte_count | status |',
            '|---|---|---:|---|',
        ]
    )
    for row in snapshot['concrete_exit_candidates']:
        lines.append(f"| {row['label']} | `{row['path']}` | {row['byte_count']} | {row['status']} |")
    if not snapshot['concrete_exit_candidates']:
        lines.append('| _none_ |  | 0 | _n/a_ |')
    lines.extend(
        [
            '',
            '## Already-elided transient rows',
            '',
            '| label | byte_count | status |',
            '|---|---:|---|',
        ]
    )
    for row in snapshot['already_elided_transients']:
        lines.append(f"| {row['label']} | {row['byte_count']} | {row['status']} |")
    if not snapshot['already_elided_transients']:
        lines.append('| _none_ | 0 | _n/a_ |')
    lines.append('')
    return '\n'.join(lines)


def main() -> int:
    snapshot = build_snapshot()
    receipt_schema = json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
    jsonschema.Draft202012Validator.check_schema(receipt_schema)
    jsonschema.validate(snapshot['dry_run_receipt'], receipt_schema)

    OUT_JSON.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(render_md(snapshot), encoding='utf-8')
    print(f'rematch-world-benchmark-prune-snapshot: wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'rematch-world-benchmark-prune-snapshot: wrote {OUT_MD.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
