#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
PATCH_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_fill_patch.json'
PATCH_SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_fill_patch.schema.json'
SEED_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_seed.json'
SEED_SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_seed.schema.json'
DECISION_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_decision_contract_snapshot_20260316.json'
APPLIER_PATH = ROOT / 'scripts' / 'tools' / 'apply_rematch_world_benchmark_fill_patch.py'


def fail(msg: str) -> int:
    print(f'rematch-world-benchmark-fill-patch: {msg}', file=sys.stderr)
    return 1


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> int:
    for path in [PATCH_PATH, PATCH_SCHEMA_PATH, SEED_PATH, SEED_SCHEMA_PATH, DECISION_PATH, APPLIER_PATH]:
        if not path.exists():
            return fail(f'missing {path.relative_to(ROOT)}')

    patch = load_json(PATCH_PATH)
    patch_schema = load_json(PATCH_SCHEMA_PATH)
    seed = load_json(SEED_PATH)
    seed_schema = load_json(SEED_SCHEMA_PATH)
    decision = load_json(DECISION_PATH)

    try:
        jsonschema.Draft202012Validator.check_schema(patch_schema)
        jsonschema.validate(patch, patch_schema)
    except jsonschema.ValidationError as exc:
        return fail(f'patch schema validation failed: {exc.message}')
    except jsonschema.SchemaError as exc:
        return fail(f'invalid patch schema: {exc.message}')

    if patch['benchmark_id'] != seed['benchmark_id']:
        return fail('patch should inherit the seed benchmark_id placeholder')
    if patch['artifact_state'] != 'filled_benchmark':
        return fail('patch should target filled_benchmark output state')
    if 'compact_decision_bundle' in patch:
        return fail('patch should not carry compact_decision_bundle')
    for key in ['artifact_version', 'benchmark_kind', 'required_sections', 'section_status']:
        if key in patch:
            return fail(f'patch should not duplicate frozen seed key {key}')

    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / 'candidate.json'
        proc = subprocess.run([sys.executable, str(APPLIER_PATH), str(PATCH_PATH), '--output', str(out_path)], cwd=ROOT, capture_output=True, text=True, check=False)
        if proc.returncode != 0:
            return fail(f'applier exited nonzero: {proc.stderr or proc.stdout}')
        if not out_path.exists():
            return fail('applier did not write candidate artifact')
        candidate = load_json(out_path)

    try:
        jsonschema.Draft202012Validator.check_schema(seed_schema)
        jsonschema.validate(seed, seed_schema)
    except jsonschema.ValidationError as exc:
        return fail(f'seed schema validation failed: {exc.message}')
    except jsonschema.SchemaError as exc:
        return fail(f'invalid seed schema: {exc.message}')

    if candidate['artifact_state'] != 'filled_benchmark':
        return fail('compiled candidate should be in filled_benchmark state')
    for section in ['world_semantics_contract', 'matching_state_contract', 'occupancy_accounting_contract', 'turnover_tempo_contract', 'paired_ranking_views_contract']:
        if candidate[section] != patch[section]:
            return fail(f'compiled candidate should copy patch section {section} exactly')
        if candidate['section_status'][section] != 'filled':
            return fail(f'compiled candidate should flip section_status for {section} to filled')
    if candidate['canonicalization_planner_contract'] != seed['canonicalization_planner_contract']:
        return fail('compiled candidate must preserve the copied canonicalization handoff from the seed')
    if candidate['section_status']['canonicalization_planner_contract'] != 'copied_from_bridge_contract':
        return fail('compiled candidate should preserve canonicalization_planner_contract status from the seed')
    if candidate['winner_triage_handoff'] != seed['winner_triage_handoff']:
        return fail('compiled candidate must preserve the copied winner triage handoff from the seed')
    if candidate['section_status']['winner_triage_handoff'] != 'copied_from_proxy_winner_triage_contract':
        return fail('compiled candidate should preserve winner_triage_handoff status from the seed')
    if candidate['delta_shortlist_handoff'] != seed['delta_shortlist_handoff']:
        return fail('compiled candidate must preserve the copied delta shortlist handoff from the seed')
    if candidate['section_status']['delta_shortlist_handoff'] != 'copied_from_publishability_contract':
        return fail('compiled candidate should preserve delta_shortlist_handoff status from the seed')
    if candidate['paired_ranking_interpretation_handoff'] != seed['paired_ranking_interpretation_handoff']:
        return fail('compiled candidate must preserve the copied paired-ranking interpretation handoff from the seed')
    if candidate['section_status']['paired_ranking_interpretation_handoff'] != 'copied_from_proxy_rank_interpretation_contract':
        return fail('compiled candidate should preserve paired_ranking_interpretation_handoff status from the seed')
    if candidate['matching_state_interpretation_handoff'] != seed['matching_state_interpretation_handoff']:
        return fail('compiled candidate must preserve the copied matching-state interpretation handoff from the seed')
    if candidate['section_status']['matching_state_interpretation_handoff'] != 'copied_from_proxy_matching_interpretation_contract':
        return fail('compiled candidate should preserve matching_state_interpretation_handoff status from the seed')
    if candidate['turnover_tempo_interpretation_handoff'] != seed['turnover_tempo_interpretation_handoff']:
        return fail('compiled candidate must preserve the copied turnover-tempo interpretation handoff from the seed')
    if candidate['section_status']['turnover_tempo_interpretation_handoff'] != 'copied_from_proxy_turnover_tempo_contract':
        return fail('compiled candidate should preserve turnover_tempo_interpretation_handoff status from the seed')
    if candidate['compact_decision_bundle'] != decision:
        return fail('compiled candidate must preserve the standing compact decision bundle')
    if candidate['decision_contract_path'] != patch['decision_contract_path']:
        return fail('compiled candidate should inherit decision_contract_path from patch')

    print('rematch-world-benchmark-fill-patch: ok (tiny patch compiles back onto the standing seed)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
