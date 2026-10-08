#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_evidence_packet.json'
PACKET_SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_evidence_packet.schema.json'
PATCH_SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_fill_patch.schema.json'
SEED_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_seed.json'
DECISION_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_decision_contract_snapshot_20260316.json'
COMPILER_PATH = ROOT / 'scripts' / 'tools' / 'compile_rematch_world_benchmark_fill_patch_from_evidence_packet.py'
APPLIER_PATH = ROOT / 'scripts' / 'tools' / 'apply_rematch_world_benchmark_fill_patch.py'
PREFLIGHT_PATH = ROOT / 'scripts' / 'tools' / 'rematch_world_benchmark_publication_preflight.py'


def fail(msg: str) -> int:
    print(f'rematch-world-benchmark-evidence-packet: {msg}', file=sys.stderr)
    return 1


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> int:
    for path in [
        PACKET_PATH,
        PACKET_SCHEMA_PATH,
        PATCH_SCHEMA_PATH,
        SEED_PATH,
        DECISION_PATH,
        COMPILER_PATH,
        APPLIER_PATH,
        PREFLIGHT_PATH,
    ]:
        if not path.exists():
            return fail(f'missing {path.relative_to(ROOT)}')

    packet = load_json(PACKET_PATH)
    packet_schema = load_json(PACKET_SCHEMA_PATH)
    patch_schema = load_json(PATCH_SCHEMA_PATH)

    try:
        jsonschema.Draft202012Validator.check_schema(packet_schema)
        jsonschema.Draft202012Validator.check_schema(patch_schema)
        jsonschema.validate(packet, packet_schema)
    except jsonschema.ValidationError as exc:
        return fail(f'packet schema validation failed: {exc.message}')
    except jsonschema.SchemaError as exc:
        return fail(f'invalid schema: {exc.message}')

    if packet['benchmark_id'].startswith('TEMPLATE_'):
        return fail('example evidence packet should already replace the benchmark_id template')
    if 'compact_decision_bundle' in packet:
        return fail('evidence packet should not retain compact_decision_bundle bytes')

    with tempfile.TemporaryDirectory() as tmpdir:
        patch_out = Path(tmpdir) / 'compiled_patch.json'
        artifact_out = Path(tmpdir) / 'compiled_artifact.json'
        proc_patch = subprocess.run(
            [sys.executable, str(COMPILER_PATH), str(PACKET_PATH), '--output', str(patch_out)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc_patch.returncode != 0:
            return fail(f'packet compiler exited nonzero: {proc_patch.stderr or proc_patch.stdout}')
        if not patch_out.exists():
            return fail('packet compiler did not write patch output')
        patch = load_json(patch_out)

        try:
            jsonschema.validate(patch, patch_schema)
        except jsonschema.ValidationError as exc:
            return fail(f'compiled patch schema validation failed: {exc.message}')

        proc_apply = subprocess.run(
            [sys.executable, str(APPLIER_PATH), str(patch_out), '--output', str(artifact_out)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc_apply.returncode != 0:
            return fail(f'patch applier exited nonzero: {proc_apply.stderr or proc_apply.stdout}')
        if not artifact_out.exists():
            return fail('patch applier did not write compiled artifact')

        proc_preflight = subprocess.run(
            [sys.executable, str(PREFLIGHT_PATH), str(artifact_out), '--strict'],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc_preflight.returncode != 0:
            return fail(f'compiled artifact should be preflight-ready: {proc_preflight.stderr or proc_preflight.stdout}')

        compiled_artifact = load_json(artifact_out)
        seed = load_json(SEED_PATH)
        if compiled_artifact['canonicalization_planner_contract'] != seed['canonicalization_planner_contract']:
            return fail('compiled artifact should preserve the copied canonicalization handoff from the seed')
        if compiled_artifact['winner_triage_handoff'] != seed['winner_triage_handoff']:
            return fail('compiled artifact should preserve the copied winner triage handoff from the seed')
        if compiled_artifact['delta_shortlist_handoff'] != seed['delta_shortlist_handoff']:
            return fail('compiled artifact should preserve the copied delta shortlist handoff from the seed')
        if compiled_artifact['paired_ranking_interpretation_handoff'] != seed['paired_ranking_interpretation_handoff']:
            return fail('compiled artifact should preserve the copied paired-ranking interpretation handoff from the seed')
        if compiled_artifact['matching_state_interpretation_handoff'] != seed['matching_state_interpretation_handoff']:
            return fail('compiled artifact should preserve the copied matching-state interpretation handoff from the seed')
        if compiled_artifact['turnover_tempo_interpretation_handoff'] != seed['turnover_tempo_interpretation_handoff']:
            return fail('compiled artifact should preserve the copied turnover-tempo interpretation handoff from the seed')

    if patch['benchmark_id'] != packet['benchmark_id']:
        return fail('compiled patch should preserve benchmark_id from packet')
    if patch['world_semantics_contract']['world_name'] != packet['world_semantics_observations']['world_name']:
        return fail('compiled patch should preserve world_name from evidence packet')
    if len(patch['occupancy_accounting_contract']['policy_rows']) != len(packet['occupancy_policy_rows']):
        return fail('compiled patch should preserve occupancy row count')
    if len(patch['turnover_tempo_contract']['policy_rows']) != len(packet['turnover_policy_rows']):
        return fail('compiled patch should preserve turnover row count')
    if len(patch['paired_ranking_views_contract']['leaderboard_rows']) != len(packet['leaderboard_rows']):
        return fail('compiled patch should preserve leaderboard row count')

    print('rematch-world-benchmark-evidence-packet: ok (tiny packet compiles into a preflight-ready benchmark path)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
