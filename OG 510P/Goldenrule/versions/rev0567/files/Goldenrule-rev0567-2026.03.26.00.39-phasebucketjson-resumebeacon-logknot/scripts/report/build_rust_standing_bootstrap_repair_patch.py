#!/usr/bin/env python3
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.report import build_cloudtainer_standing_bootstrap_delta as delta_mod
from scripts.report import build_rust_standing_bootstrap_guard as guard_mod

SOURCE_PATH = ROOT / 'crates' / 'gr_engine' / 'src' / 'probe.rs'
DELTA_REPORT = ROOT / 'artifacts' / 'reports' / 'cloudtainer_standing_bootstrap_delta.json'
GUARD_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_guard.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_repair_patch.json'
OUT_MD = ROOT / 'docs' / 'RUST_STANDING_BOOTSTRAP_REPAIR_PATCH.md'
PATCH_PATH = ROOT / 'artifacts' / 'patches' / 'rust_standing_bootstrap_repair.patch'
TARGET_FILE = 'crates/gr_engine/src/probe.rs'

IMPORT_OLD = 'use crate::spec::{NoiseModelSpec, StrategySpec, TaskSpec, TerminationRuleSpec, WorldSpec};\n'
IMPORT_NEW = 'use crate::spec::{\n    NoiseModelSpec, ReputationModelSpec, StrategySpec, TaskSpec, TerminationRuleSpec, WorldSpec,\n};\n'
HELPER = '''fn bootstrap_task_standing_from_world(task: &mut TaskSpec) {\n    if let ReputationModelSpec::SimpleStanding { initial_standing, .. } = &task.world.reputation {\n        task.standing_a = *initial_standing;\n        task.standing_b = *initial_standing;\n    }\n}\n\n'''
EXPAND_ANCHOR = '''            let mut task = TaskSpec::new(\n                &format!("{}/{}__rep{}", probe.id, matchup.id, rep),\n                probe.world.clone(),\n                matchup.strategy_a.clone(),\n                matchup.strategy_b.clone(),\n                match_seed,\n            );\n            task.trace_rounds = matchup.trace_rounds;\n'''
EXPAND_REPLACEMENT = '''            let mut task = TaskSpec::new(\n                &format!("{}/{}__rep{}", probe.id, matchup.id, rep),\n                probe.world.clone(),\n                matchup.strategy_a.clone(),\n                matchup.strategy_b.clone(),\n                match_seed,\n            );\n            bootstrap_task_standing_from_world(&mut task);\n            task.trace_rounds = matchup.trace_rounds;\n'''
RUN_ANCHOR = '''            let mut task = TaskSpec::new(\n                &format!("{}/{}__{}", probe.id, matchup.id, rep),\n                probe.world.clone(),\n                matchup.strategy_a.clone(),\n                matchup.strategy_b.clone(),\n                match_seed,\n            );\n            task.trace_rounds = matchup.trace_rounds;\n            let artifact = crate::sim::run_match(&task)?;\n'''
RUN_REPLACEMENT = '''            let mut task = TaskSpec::new(\n                &format!("{}/{}__{}", probe.id, matchup.id, rep),\n                probe.world.clone(),\n                matchup.strategy_a.clone(),\n                matchup.strategy_b.clone(),\n                match_seed,\n            );\n            bootstrap_task_standing_from_world(&mut task);\n            task.trace_rounds = matchup.trace_rounds;\n            let artifact = crate::sim::run_match(&task)?;\n'''


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_delta_report() -> dict[str, Any]:
    if DELTA_REPORT.exists():
        return json.loads(DELTA_REPORT.read_text(encoding='utf-8'))
    return delta_mod.collect()


def _load_guard_report() -> dict[str, Any]:
    if GUARD_REPORT.exists():
        return json.loads(GUARD_REPORT.read_text(encoding='utf-8'))
    return guard_mod.collect()[0]


def _apply_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'rust-standing-bootstrap-repair-patch: expected exactly one {label} anchor, found {count}')
    return text.replace(old, new, 1)


def _render_target_text(source_text: str) -> str:
    target = _apply_once(source_text, IMPORT_OLD, IMPORT_NEW, 'import')
    helper_anchor = 'pub fn expand_probe(probe: &ProbeSpec) -> Result<ExpandedProbe, ProbeError> {\n'
    target = _apply_once(target, helper_anchor, HELPER + helper_anchor, 'helper insertion')
    target = _apply_once(target, EXPAND_ANCHOR, EXPAND_REPLACEMENT, 'expand_probe standing bootstrap')
    target = _apply_once(target, RUN_ANCHOR, RUN_REPLACEMENT, 'run_probe standing bootstrap')
    return target


def _render_patch(source_text: str, target_text: str) -> str:
    diff_lines = difflib.unified_diff(
        source_text.splitlines(keepends=True),
        target_text.splitlines(keepends=True),
        fromfile=f'a/{TARGET_FILE}',
        tofile=f'b/{TARGET_FILE}',
        lineterm='',
    )
    return ''.join(line if line.endswith('\n') else line + '\n' for line in diff_lines)


def render_markdown(report: dict[str, Any]) -> str:
    summary = report['summary']
    lines = [
        '# Rust Standing Bootstrap Repair Patch',
        '',
        'Generated by `scripts/report/build_rust_standing_bootstrap_repair_patch.py`. This emits the smallest source-level Rust patch that repairs the current simple-standing bootstrap seam on the probe-generated task path.',
        '',
        '## Snapshot',
        '',
        f"- target file: `{report['target_file']}`",
        f"- patch artifact: `{report['patch_path']}`",
        f"- apply hint: `{summary['apply_hint']}`",
        f"- target_sha256: `{summary['target_sha256']}`",
        f"- patch_sha256: `{summary['patch_sha256']}`",
        f"- changed files: `{summary['changed_file_count']}`",
        f"- added lines: `{summary['lines_added']}`",
        f"- removed lines: `{summary['lines_removed']}`",
        f"- scope boundary: `{summary['scope_boundary']}`",
        '',
        '## Why this patch is intentionally narrow',
        '',
        '- The diagnosed seam is on the probe path: `expand_probe(...)` and the inner `run_probe(...)` replication loop both create fresh `TaskSpec`s via `TaskSpec::new(...)`, which defaults both standing fields to `1.0`.',
        '- This patch keeps `TaskSpec::new(...)` itself untouched. That avoids widening semantics for non-probe callers or for serialized task inputs while still repairing the exact path that the blocked-session oracle and guard discovered.',
        '- It adds one small helper that copies `world.reputation.initial_standing` into `task.standing_a` and `task.standing_b` only when the world uses `simple_standing`, then calls that helper at the two affected probe task-construction sites.',
        '',
        '## Expected semantic effect on the current comeback seeds',
        '',
        f"- affected seed count carried from the delta card: `{summary['affected_seed_count']}`",
        f"- current classification across those seeds: `{summary['expected_seed_classification']}`",
        '- For the currently affected comeback seeds, the blocked-session delta surface already shows the effect is trace-only: round-0 standing traces repair to the declared bootstrap while mean payoff/cooperation headlines stay invariant.',
        '- This means the first Rust-capable inheritor can land this source fix and then use the standalone guard tests to verify the trace seam directly, without expecting the current comeback score headlines to move.',
        '',
        '## Affected comeback rows carried by this patch',
        '',
        '| Seed | Queue rows | Declared bootstrap | Current task bootstrap | Delta classification |',
        '| --- | --- | ---: | ---: | --- |',
    ]
    for seed in report['affected_seeds']:
        queue_rows = ', '.join(seed['queue_rows'])
        lines.append(
            f"| `{seed['seed_path']}` | `{queue_rows}` | `{seed['declared_initial_standing']}` | `{seed['current_task_initial_standing']}` | `{seed['classification']}` |"
        )
    lines.extend([
        '',
        '## First-machine follow-up',
        '',
        '1. Apply this source patch first so probe-generated tasks honor the declared simple-standing bootstrap.',
        f"2. Apply the standalone guard patch from `{report['guard_patch_path']}` immediately after the repair.",
        '3. Run the dedicated guard tests below before reopening the broader comeback patchset.',
        '',
        '### Guard cargo hints',
        '',
    ])
    for hint in report['guard_cargo_hints']:
        lines.append(f"- `{hint}`")
    lines.extend([
        '',
        '## Open boundary left intentionally unresolved',
        '',
        '- This patch does **not** redefine how raw `TaskSpec` JSON without explicit `standing_a` / `standing_b` should be interpreted. If the future engine wants world-level bootstrap semantics for all task-ingress paths, that should be a separate, broader decision with its own tests.',
        '',
    ])
    return '\n'.join(lines)


def collect() -> tuple[dict[str, Any], str, str]:
    source_text = SOURCE_PATH.read_text(encoding='utf-8')
    target_text = _render_target_text(source_text)
    patch_text = _render_patch(source_text, target_text)
    delta_report = _load_delta_report()
    guard_report = _load_guard_report()
    affected_seeds = []
    for seed in delta_report['seeds']:
        affected_seeds.append({
            'seed_path': str(seed['seed_path']),
            'queue_rows': [str(row['proposed_test_name']) for row in seed['queue_rows']],
            'declared_initial_standing': float(seed['declared_initial_standing']),
            'current_task_initial_standing': float(seed['current_task_initial_standing']),
            'classification': str(seed['classification']),
        })
    patch_lines = patch_text.splitlines()
    lines_added = sum(1 for line in patch_lines if line.startswith('+') and not line.startswith('+++'))
    lines_removed = sum(1 for line in patch_lines if line.startswith('-') and not line.startswith('---'))
    target_bytes = target_text.encode('utf-8')
    patch_bytes = patch_text.encode('utf-8')
    report = {
        'tool': 'build_rust_standing_bootstrap_repair_patch',
        'source_file': str(SOURCE_PATH.relative_to(ROOT)),
        'source_delta_report': str(DELTA_REPORT.relative_to(ROOT)),
        'source_guard_report': str(GUARD_REPORT.relative_to(ROOT)),
        'target_file': TARGET_FILE,
        'patch_path': str(PATCH_PATH.relative_to(ROOT)),
        'guard_patch_path': str(Path(guard_report['patch_path']).as_posix()),
        'summary': {
            'changed_file_count': 1,
            'affected_seed_count': len(affected_seeds),
            'expected_seed_classification': 'trace_only_mean_stat_invariant',
            'scope_boundary': 'probe_generated_tasks_only',
            'target_sha256': _sha256_bytes(target_bytes),
            'target_bytes': len(target_bytes),
            'patch_sha256': _sha256_bytes(patch_bytes),
            'patch_bytes': len(patch_bytes),
            'lines_added': lines_added,
            'lines_removed': lines_removed,
            'apply_hint': f'git apply {PATCH_PATH.relative_to(ROOT).as_posix()}',
        },
        'guard_cargo_hints': [str(entry['cargo_hint']) for entry in guard_report['entries']],
        'affected_seeds': affected_seeds,
    }
    return report, render_markdown(report), patch_text


def _check(expected_report: dict[str, Any], expected_markdown: str, expected_patch: str) -> int:
    if not OUT_JSON.exists() or not OUT_MD.exists() or not PATCH_PATH.exists():
        print('rust-standing-bootstrap-repair-patch: missing report/doc/patch', file=sys.stderr)
        return 1
    actual_report = json.loads(OUT_JSON.read_text(encoding='utf-8'))
    if actual_report != expected_report:
        print('rust-standing-bootstrap-repair-patch: report drift detected', file=sys.stderr)
        return 1
    if OUT_MD.read_text(encoding='utf-8').rstrip('\n') != expected_markdown.rstrip('\n'):
        print('rust-standing-bootstrap-repair-patch: markdown drift detected', file=sys.stderr)
        return 1
    if PATCH_PATH.read_text(encoding='utf-8') != expected_patch:
        print('rust-standing-bootstrap-repair-patch: patch drift detected', file=sys.stderr)
        return 1
    print('rust-standing-bootstrap-repair-patch: ok file=probe.rs scope=probe_generated_tasks_only')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    report, markdown, patch_text = collect()
    if args.write:
        OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        PATCH_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        OUT_MD.write_text(markdown + '\n', encoding='utf-8')
        PATCH_PATH.write_text(patch_text, encoding='utf-8')
        print(f'wrote {OUT_JSON.relative_to(ROOT)}')
        print(f'wrote {OUT_MD.relative_to(ROOT)}')
        print(f'wrote {PATCH_PATH.relative_to(ROOT)}')
        return 0
    return _check(report, markdown, patch_text)


if __name__ == '__main__':
    raise SystemExit(main())
