#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEED_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_seed.json'
OUT_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_fill_patch.json'
WORLD_SECTIONS = [
    'world_semantics_contract',
    'matching_state_contract',
    'occupancy_accounting_contract',
    'turnover_tempo_contract',
    'paired_ranking_views_contract',
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def build_patch(seed: dict) -> dict:
    return {
        'patch_version': '2026-03-16.rematch_world_benchmark_fill_patch.v1',
        'patch_intent': 'fill only the mutable seed surface, then compile back to one retained benchmark artifact',
        'seed_artifact_path': 'examples/snapshots/rematch_world_benchmark_seed.json',
        'decision_contract_path': 'artifacts/reports/rematch_decision_contract_snapshot_20260316.json',
        'artifact_state': 'filled_benchmark',
        'benchmark_id': seed['benchmark_id'],
        **{section: copy.deepcopy(seed[section]) for section in WORLD_SECTIONS},
    }


def main() -> int:
    seed = load_json(SEED_PATH)
    patch = build_patch(seed)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(patch, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(f'rematch-world-benchmark-fill-patch-example: wrote {OUT_PATH.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
