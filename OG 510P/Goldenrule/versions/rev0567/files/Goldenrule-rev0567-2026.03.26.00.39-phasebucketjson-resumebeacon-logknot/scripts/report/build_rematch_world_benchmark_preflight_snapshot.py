#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SEED_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_seed.json'
PATCH_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_fill_patch.json'
DECISION_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_decision_contract_snapshot_20260316.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_preflight_snapshot_20260316.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_preflight_snapshot_20260316.md'


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'could not load module {name} from {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_snapshot() -> dict[str, Any]:
    patch_builder = _load_module('build_rematch_world_benchmark_fill_patch_example', ROOT / 'scripts' / 'report' / 'build_rematch_world_benchmark_fill_patch_example.py')
    applier = _load_module('apply_rematch_world_benchmark_fill_patch', ROOT / 'scripts' / 'tools' / 'apply_rematch_world_benchmark_fill_patch.py')
    preflight = _load_module('rematch_world_benchmark_publication_preflight', ROOT / 'scripts' / 'tools' / 'rematch_world_benchmark_publication_preflight.py')

    seed = load_json(SEED_PATH)
    decision = load_json(DECISION_PATH)
    patch = patch_builder.build_patch(seed)
    PATCH_PATH.write_text(json.dumps(patch, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    candidate = applier.build_candidate_from_patch(patch, seed)
    snapshot = preflight.build_preflight_summary(
        candidate=candidate,
        seed=seed,
        decision_contract=decision,
        inspection_mode='patch_compile',
        inspection_target_path=PATCH_PATH.relative_to(ROOT).as_posix(),
        seed_path=SEED_PATH.relative_to(ROOT).as_posix(),
        decision_contract_path=DECISION_PATH.relative_to(ROOT).as_posix(),
    )
    snapshot['analysis_script'] = 'scripts/report/build_rematch_world_benchmark_preflight_snapshot.py'
    snapshot['compiled_candidate_artifact_bytes'] = len(json.dumps(candidate, indent=2, sort_keys=True).encode('utf-8'))
    snapshot['patch_bytes'] = len(PATCH_PATH.read_bytes())
    snapshot['strict_mode_exit_code_if_run_now'] = 0 if snapshot['preflight_ready'] else 1
    return snapshot


def render_md(snapshot: dict[str, Any]) -> str:
    lines = [
        '# Rematch World Benchmark Preflight Snapshot — 2026-03-16',
        '',
        f"Focus: {snapshot['focus']}",
        '',
        '## Main local result',
        '',
        '- The archive now has one consolidated preflight receipt that compiles the fill patch, checks the mutation surface, checks completion readiness, and fingerprints the frozen copied contract surface in one step.',
        f"- On the standing template patch, the preflight is `{'ready' if snapshot['preflight_ready'] else 'not ready'}` with `{snapshot['status_counts']['forbidden_changed_path_count']}` forbidden changed paths, `{snapshot['status_counts']['blocking_fill_slot_count']}` real fill blockers, and `{snapshot['status_counts']['allowed_decision_null_count']}` allowed open-ended decision nulls.",
        f"- The compiled candidate currently fills `{snapshot['status_counts']['filled_world_section_count']}` world-section statuses while preserving decision-bundle digest equality with the standing contract: `{snapshot['decision_bundle_digest_matches_contract']}`.",
        '',
        '## Why this is useful',
        '',
        '- The inheritor no longer needs to remember a three-step publication ritual at the end of benchmark fill work.',
        '- One command can now say both “did you stay inside the seed edit surface?” and “is the resulting benchmark actually publishable yet?” while also giving a stable artifact digest for handoff notes.',
        '',
        '## Current strict-mode implication',
        '',
        f"- Running strict preflight on the current template patch would exit with code `{snapshot['strict_mode_exit_code_if_run_now']}` because the world-dependent template slots are still unresolved.",
        f"- Recommended next move: {snapshot['recommended_next_move']}",
        ''
    ]
    return '\n'.join(lines)


def main() -> int:
    snapshot = build_snapshot()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(render_md(snapshot), encoding='utf-8')
    print(f'rematch-world-benchmark-preflight-snapshot: wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'rematch-world-benchmark-preflight-snapshot: wrote {OUT_MD.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
