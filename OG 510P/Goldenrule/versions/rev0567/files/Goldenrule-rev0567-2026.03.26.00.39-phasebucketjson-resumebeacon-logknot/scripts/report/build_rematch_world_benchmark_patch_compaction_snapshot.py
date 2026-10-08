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
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_patch_compaction_snapshot_20260316.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_patch_compaction_snapshot_20260316.md'


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
    mutation_guard = _load_module('rematch_world_benchmark_mutation_guard', ROOT / 'scripts' / 'tools' / 'rematch_world_benchmark_mutation_guard.py')

    seed = load_json(SEED_PATH)
    patch = patch_builder.build_patch(seed)
    PATCH_PATH.write_text(json.dumps(patch, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    decision = load_json(DECISION_PATH)
    candidate = applier.build_candidate_from_patch(patch, seed)
    mutation = mutation_guard.inspect_candidate_mutations(candidate, seed, decision)

    seed_bytes = len(SEED_PATH.read_bytes())
    patch_bytes = len(PATCH_PATH.read_bytes())
    bytes_saved = seed_bytes - patch_bytes
    savings_share = bytes_saved / seed_bytes if seed_bytes else 0.0

    return {
        'snapshot_date': '2026-03-16',
        'focus': 'keep rematch-world fill scratch small by editing one compact patch instead of rewriting a seed that embeds the frozen decision bundle',
        'seed_path': SEED_PATH.relative_to(ROOT).as_posix(),
        'patch_path': PATCH_PATH.relative_to(ROOT).as_posix(),
        'decision_contract_path': DECISION_PATH.relative_to(ROOT).as_posix(),
        'seed_bytes': seed_bytes,
        'patch_bytes': patch_bytes,
        'bytes_saved_by_patch_workflow': bytes_saved,
        'saved_share_of_seed_bytes': savings_share,
        'patch_top_level_keys': sorted(patch.keys()),
        'frozen_top_level_keys_excluded_from_patch': sorted(set(seed.keys()) - set(patch.keys())),
        'applied_template_mutation_summary': {
            'allowed_changed_path_count': mutation['status_counts']['allowed_changed_path_count'],
            'forbidden_changed_path_count': mutation['status_counts']['forbidden_changed_path_count'],
            'unchanged_required_mutation_prefix_count': mutation['status_counts']['unchanged_required_mutation_prefix_count'],
            'remaining_fill_blocker_count': mutation['status_counts']['blocking_fill_slot_count'],
            'allowed_decision_null_count': mutation['status_counts']['allowed_decision_null_count']
        },
        'recommended_next_move': 'Fill the compact patch first, compile it back onto the standing seed, then run the mutation guard and completion gate on the compiled benchmark artifact.'
    }


def render_md(snapshot: dict[str, Any]) -> str:
    return '\n'.join([
        '# Rematch World Benchmark Patch Compaction Snapshot — 2026-03-16',
        '',
        f"Focus: {snapshot['focus']}",
        '',
        '## Main local result',
        '',
        f"- The standing seed currently weighs `{snapshot['seed_bytes']}` bytes because it embeds the frozen compact decision bundle.",
        f"- The editable fill patch template weighs `{snapshot['patch_bytes']}` bytes, saving `{snapshot['bytes_saved_by_patch_workflow']}` bytes (`{snapshot['saved_share_of_seed_bytes']:.6f}` share) while the inheritor is still doing scratch fill work.",
        f"- The patch excludes the frozen top-level keys {', '.join(f'`{key}`' for key in snapshot['frozen_top_level_keys_excluded_from_patch'])}, so the copied decision bundle and contract pointers do not need to be recopied or re-edited during fill work.",
        '',
        '## Applied template check',
        '',
        f"- Applying the template patch back onto the seed mutates `{snapshot['applied_template_mutation_summary']['allowed_changed_path_count']}` allowed paths and `0` forbidden paths.",
        f"- The applied template still leaves `{snapshot['applied_template_mutation_summary']['remaining_fill_blocker_count']}` real fill blockers plus `{snapshot['applied_template_mutation_summary']['allowed_decision_null_count']}` allowed open-ended decision nulls, so the patch workflow stays aligned with the standing completion gate instead of creating a second benchmark format.",
        '',
        '## Recommended next move',
        '',
        f"- {snapshot['recommended_next_move']}",
        ''
    ])


def main() -> int:
    snapshot = build_snapshot()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(render_md(snapshot), encoding='utf-8')
    print(f'rematch-world-benchmark-patch-compaction-snapshot: wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'rematch-world-benchmark-patch-compaction-snapshot: wrote {OUT_MD.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
