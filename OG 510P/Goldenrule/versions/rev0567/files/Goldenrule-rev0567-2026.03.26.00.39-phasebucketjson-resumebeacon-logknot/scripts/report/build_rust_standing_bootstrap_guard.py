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

DELTA_REPORT = ROOT / 'artifacts' / 'reports' / 'cloudtainer_standing_bootstrap_delta.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_guard.json'
OUT_MD = ROOT / 'docs' / 'RUST_STANDING_BOOTSTRAP_GUARD.md'
PATCH_PATH = ROOT / 'artifacts' / 'patches' / 'rust_standing_bootstrap_guard.patch'
TARGET_FILE = 'crates/gr_engine/tests/probe_standing_bootstrap.rs'


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_delta_report() -> dict[str, Any]:
    if DELTA_REPORT.exists():
        return json.loads(DELTA_REPORT.read_text(encoding='utf-8'))
    return delta_mod.collect()


def _to_slug(seed_path: str) -> str:
    stem = Path(seed_path).stem
    return ''.join(ch if ch.isalnum() else '_' for ch in stem).strip('_').lower()


def _loader_name(seed_path: str) -> str:
    return f"load_{_to_slug(seed_path)}_v1"


def _test_name(seed_path: str) -> str:
    return f"probe_trace_bootstraps_declared_initial_standing_{_to_slug(seed_path)}"


def _render_target_file(delta_report: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    seeds = list(delta_report['seeds'])
    entries: list[dict[str, Any]] = []
    lines = [
        'use gr_engine::probe::{run_probe, ProbeMatchupResult, ProbeSpec};',
        'use gr_engine::spec::ReputationModelSpec;',
        '',
    ]
    for seed in seeds:
        loader = _loader_name(str(seed['seed_path']))
        lines.extend([
            f'fn {loader}() -> ProbeSpec {{',
            f'    serde_json::from_str(include_str!("../../{seed["seed_path"]}")).unwrap()',
            '}',
            '',
        ])
    lines.extend([
        'fn declared_initial_standing(probe: &ProbeSpec) -> f64 {',
        '    match &probe.world.reputation {',
        '        ReputationModelSpec::SimpleStanding { initial_standing, .. } => *initial_standing,',
        '        ReputationModelSpec::None => panic!("expected simple_standing reputation"),',
        '    }',
        '}',
        '',
        'fn first_trace_standing(matchup: &ProbeMatchupResult) -> (f64, f64) {',
        '    let replication = matchup.replications_detail.first().expect("replication detail");',
        '    let trace = replication.trace.as_ref().expect("trace");',
        '    let round0 = trace.first().expect("round 0 trace");',
        '    (round0.standing_a, round0.standing_b)',
        '}',
        '',
        'fn assert_close(actual: f64, expected: f64) {',
        '    let diff = (actual - expected).abs();',
        '    assert!(diff <= 1e-12, "expected first trace standing {expected}, got {actual} (diff={diff})");',
        '}',
        '',
    ])
    for seed in seeds:
        seed_path = str(seed['seed_path'])
        loader = _loader_name(seed_path)
        test_name = _test_name(seed_path)
        matchup_id = str(seed['matchup_id'])
        probe_id = str(seed['probe_id'])
        declared = float(seed['declared_initial_standing'])
        queue_rows = [str(row['proposed_test_name']) for row in seed['queue_rows']]
        entries.append({
            'seed_path': seed_path,
            'probe_id': probe_id,
            'matchup_id': matchup_id,
            'declared_initial_standing': declared,
            'test_name': test_name,
            'loader_name': loader,
            'cargo_hint': f'cargo test -p gr_engine --test probe_standing_bootstrap {test_name} -- --exact',
            'queue_rows': queue_rows,
        })
        lines.extend([
            '#[test]',
            f'fn {test_name}() {{',
            f'    let probe = {loader}();',
            f'    assert_eq!(probe.id, "{probe_id}");',
            '    assert!(probe.matchups.iter().all(|m| m.trace_rounds > 0), "seed must request trace_rounds");',
            '    let expected = declared_initial_standing(&probe);',
            '    let out = run_probe(&probe).unwrap();',
            f'    let matchup = out.matchups.iter().find(|m| m.id == "{matchup_id}").expect("matchup result");',
            '    let (standing_a, standing_b) = first_trace_standing(matchup);',
            '    assert_close(standing_a, expected);',
            '    assert_close(standing_b, expected);',
            f'    assert_close(expected, {declared});',
            '}',
            '',
        ])
    return '\n'.join(lines).rstrip() + '\n', entries


def _render_patch(target_text: str) -> str:
    diff_lines = difflib.unified_diff([], target_text.splitlines(keepends=True), fromfile='/dev/null', tofile=f'b/{TARGET_FILE}', lineterm='')
    return ''.join(line if line.endswith('\n') else line + '\n' for line in diff_lines)


def render_markdown(report: dict[str, Any]) -> str:
    summary = report['summary']
    lines = [
        '# Rust Standing Bootstrap Guard',
        '',
        'Generated by `scripts/report/build_rust_standing_bootstrap_guard.py`. This emits one small standalone Rust test file patch for the simple-standing bootstrap seam discovered in the blocked cloudtainer lane.',
        '',
        '## Snapshot',
        '',
        f"- affected seed count: `{summary['affected_seed_count']}`",
        f"- generated test count: `{summary['generated_test_count']}`",
        f"- target file: `{report['target_file']}`",
        f"- patch artifact: `{report['patch_path']}`",
        f"- apply hint: `{summary['apply_hint']}`",
        f"- target_sha256: `{summary['target_sha256']}`",
        f"- patch_sha256: `{summary['patch_sha256']}`",
        '',
        '## What this patch guards',
        '',
        '- It adds a dedicated external Rust test file rather than touching `probe_run.rs`, so the guard stays independent of the larger comeback patchset.',
        '- Each generated test loads an existing simple-standing probe seed, runs `run_probe`, opens the first recorded round trace, and asserts that `standing_a` and `standing_b` equal the declared `world.reputation.initial_standing`.',
        '- On the current head these tests are expected to fail, because probe expansion still seeds `TaskSpec` standing from `1.0` instead of from the declared world bootstrap.',
        '- After a future bootstrap repair, this patch becomes the smallest direct regression guard for that seam.',
        '',
        '## Seed table',
        '',
        '| Seed | Probe / matchup | Declared initial standing | Generated test | Queue rows carried |',
        '| --- | --- | ---: | --- | --- |',
    ]
    for entry in report['entries']:
        lines.append(f"| `{entry['seed_path']}` | `{entry['probe_id']}` / `{entry['matchup_id']}` | `{entry['declared_initial_standing']}` | `{entry['test_name']}` | `{', '.join(entry['queue_rows'])}` |")
    lines.extend([
        '',
        '## Cargo hints',
        '',
    ])
    for entry in report['entries']:
        lines.append(f"- `{entry['cargo_hint']}`")
    lines.extend([
        '',
        '## Practical use',
        '',
        '1. Keep the larger comeback patchset for the existing 14 queue rows as-is; this guard is intentionally narrower and post-repair-focused.',
        '2. Once a Rust-capable inheritor repairs the bootstrap seam, apply this patch and run the two exact tests above before broadening any standing-sensitive scenarios.',
        '3. If these guards still fail after the seam repair, inspect whether trace recording or task bootstrap still diverges from the declared world reputation bootstrap rather than reopening the whole oracle stack first.',
        '',
    ])
    return '\n'.join(lines)


def collect() -> tuple[dict[str, Any], str, str]:
    delta_report = _load_delta_report()
    target_text, entries = _render_target_file(delta_report)
    patch_text = _render_patch(target_text)
    target_bytes = target_text.encode('utf-8')
    patch_bytes = patch_text.encode('utf-8')
    report = {
        'tool': 'build_rust_standing_bootstrap_guard',
        'source_delta_report': str(DELTA_REPORT.relative_to(ROOT)),
        'target_file': TARGET_FILE,
        'patch_path': str(PATCH_PATH.relative_to(ROOT)),
        'summary': {
            'affected_seed_count': len(entries),
            'generated_test_count': len(entries),
            'target_file_count': 1,
            'current_failure_mode': 'current head still seeds TaskSpec standing from 1.0 during probe expansion, so these tests are expected to fail until the bootstrap seam is repaired',
            'target_sha256': _sha256_bytes(target_bytes),
            'target_bytes': len(target_bytes),
            'patch_sha256': _sha256_bytes(patch_bytes),
            'patch_bytes': len(patch_bytes),
            'apply_hint': f'git apply {PATCH_PATH.relative_to(ROOT).as_posix()}',
        },
        'entries': entries,
    }
    return report, render_markdown(report), patch_text


def _check(expected_report: dict[str, Any], expected_markdown: str, expected_patch: str) -> int:
    if not OUT_JSON.exists() or not OUT_MD.exists() or not PATCH_PATH.exists():
        print('rust-standing-bootstrap-guard: missing report/doc/patch', file=sys.stderr)
        return 1
    actual_report = json.loads(OUT_JSON.read_text(encoding='utf-8'))
    if actual_report != expected_report:
        print('rust-standing-bootstrap-guard: report drift detected', file=sys.stderr)
        return 1
    if OUT_MD.read_text(encoding='utf-8').rstrip('\n') != expected_markdown.rstrip('\n'):
        print('rust-standing-bootstrap-guard: markdown drift detected', file=sys.stderr)
        return 1
    if PATCH_PATH.read_text(encoding='utf-8') != expected_patch:
        print('rust-standing-bootstrap-guard: patch drift detected', file=sys.stderr)
        return 1
    print('rust-standing-bootstrap-guard: ok seeds=2 tests=2 target=probe_standing_bootstrap.rs')
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
