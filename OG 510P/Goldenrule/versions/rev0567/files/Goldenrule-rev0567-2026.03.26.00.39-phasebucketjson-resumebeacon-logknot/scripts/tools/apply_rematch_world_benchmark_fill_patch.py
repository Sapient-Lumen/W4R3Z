#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PATCH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_fill_patch.json'
DEFAULT_SEED = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_seed.json'
PATCH_SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_fill_patch.schema.json'
SEED_SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_seed.schema.json'
DEFAULT_DECISION_CONTRACT = ROOT / 'artifacts' / 'reports' / 'rematch_decision_contract_snapshot_20260316.json'
WORLD_SECTIONS = [
    'world_semantics_contract',
    'matching_state_contract',
    'occupancy_accounting_contract',
    'turnover_tempo_contract',
    'paired_ranking_views_contract',
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'could not load module {name} from {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_candidate_from_patch(patch: dict[str, Any], seed: dict[str, Any]) -> dict[str, Any]:
    candidate = copy.deepcopy(seed)
    candidate['artifact_state'] = patch['artifact_state']
    candidate['benchmark_id'] = patch['benchmark_id']
    candidate['decision_contract_path'] = patch['decision_contract_path']
    for section in WORLD_SECTIONS:
        candidate[section] = copy.deepcopy(patch[section])
        candidate['section_status'][section] = 'filled'
    return candidate


def summarize_application(candidate: dict[str, Any], seed: dict[str, Any], decision_contract: dict[str, Any]) -> dict[str, Any]:
    mutation_guard = _load_module('rematch_world_benchmark_mutation_guard', ROOT / 'scripts' / 'tools' / 'rematch_world_benchmark_mutation_guard.py')
    completion_gate = _load_module('rematch_world_benchmark_completion_gate', ROOT / 'scripts' / 'tools' / 'rematch_world_benchmark_completion_gate.py')
    mutation = mutation_guard.inspect_candidate_mutations(candidate, seed, decision_contract)
    completion = completion_gate.summarize_completion_status(candidate, decision_contract)
    return {
        'mutation_surface_ok': mutation['mutation_surface_ok'],
        'completion_ready': completion['completion_ready'],
        'allowed_changed_path_count': mutation['status_counts']['allowed_changed_path_count'],
        'forbidden_changed_path_count': mutation['status_counts']['forbidden_changed_path_count'],
        'blocking_fill_slot_count': completion['status_counts']['blocking_slot_count'],
        'allowed_decision_null_count': completion['status_counts']['allowed_decision_null_count'],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Apply a compact rematch-world benchmark fill patch back onto the standing seed artifact.')
    parser.add_argument('patch', nargs='?', default=str(DEFAULT_PATCH), help='Path to the fill-patch JSON.')
    parser.add_argument('--seed', default=str(DEFAULT_SEED), help='Path to the standing benchmark seed JSON.')
    parser.add_argument('--decision-contract', default=str(DEFAULT_DECISION_CONTRACT), help='Path to the standing compact decision contract JSON.')
    parser.add_argument('--output', help='Write the compiled benchmark artifact to this path instead of stdout.')
    parser.add_argument('--summary-json', action='store_true', help='Emit only a compact JSON summary instead of the compiled artifact.')
    args = parser.parse_args()

    patch_path = Path(args.patch)
    seed_path = Path(args.seed)
    decision_path = Path(args.decision_contract)

    patch = load_json(patch_path)
    seed = load_json(seed_path)
    decision = load_json(decision_path)
    patch_schema = load_json(PATCH_SCHEMA_PATH)
    seed_schema = load_json(SEED_SCHEMA_PATH)

    jsonschema.Draft202012Validator.check_schema(patch_schema)
    jsonschema.Draft202012Validator.check_schema(seed_schema)
    jsonschema.validate(patch, patch_schema)
    jsonschema.validate(seed, seed_schema)

    candidate = build_candidate_from_patch(patch, seed)
    summary = summarize_application(candidate, seed, decision)
    summary['patch_path'] = patch_path.resolve().relative_to(ROOT).as_posix() if patch_path.resolve().is_relative_to(ROOT) else str(patch_path)
    summary['seed_path'] = seed_path.resolve().relative_to(ROOT).as_posix() if seed_path.resolve().is_relative_to(ROOT) else str(seed_path)
    summary['decision_contract_path'] = decision_path.resolve().relative_to(ROOT).as_posix() if decision_path.resolve().is_relative_to(ROOT) else str(decision_path)

    if args.summary_json:
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    rendered = json.dumps(candidate, indent=2, sort_keys=True) + '\n'
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding='utf-8')
        print(
            'rematch-world-benchmark-fill-patch: '
            f"wrote {output_path} ({summary['allowed_changed_path_count']} allowed changed paths, "
            f"{summary['blocking_fill_slot_count']} remaining fill blockers)"
        )
        return 0

    print(rendered, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
