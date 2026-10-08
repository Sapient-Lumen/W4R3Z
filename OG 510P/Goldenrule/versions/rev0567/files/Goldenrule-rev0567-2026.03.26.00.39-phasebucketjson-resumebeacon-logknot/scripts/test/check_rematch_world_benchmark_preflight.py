#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
PREFLIGHT_TOOL = ROOT / 'scripts' / 'tools' / 'rematch_world_benchmark_publication_preflight.py'
PREFLIGHT_SCHEMA = ROOT / 'schemas' / 'rematch_world_benchmark_preflight.schema.json'
PREFLIGHT_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_preflight_snapshot_20260316.json'
PATCH_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_fill_patch.json'
SEED_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_seed.json'
APPLIER_PATH = ROOT / 'scripts' / 'tools' / 'apply_rematch_world_benchmark_fill_patch.py'


def fail(msg: str) -> int:
    print(f'rematch-world-benchmark-preflight: {msg}', file=sys.stderr)
    return 1


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding='utf-8'))


def run_json(args: list[str]) -> tuple[int, dict[str, object], str]:
    proc = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=False)
    payload = json.loads(proc.stdout) if proc.stdout.strip() else {}
    return proc.returncode, payload, proc.stderr


def main() -> int:
    for path in [PREFLIGHT_TOOL, PREFLIGHT_SCHEMA, PREFLIGHT_REPORT, PATCH_PATH, SEED_PATH, APPLIER_PATH]:
        if not path.exists():
            return fail(f'missing {path.relative_to(ROOT)}')

    schema = load_json(PREFLIGHT_SCHEMA)
    report = load_json(PREFLIGHT_REPORT)
    try:
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.validate(report, schema)
    except jsonschema.ValidationError as exc:
        return fail(f'preflight report validation failed: {exc.message}')
    except jsonschema.SchemaError as exc:
        return fail(f'invalid preflight schema: {exc.message}')

    code, payload, stderr = run_json([sys.executable, str(PREFLIGHT_TOOL), '--patch', str(PATCH_PATH), '--json'])
    if code != 0:
        return fail(f'preflight tool exited nonzero on patch without strict mode: {stderr}')
    try:
        jsonschema.validate(payload, schema)
    except jsonschema.ValidationError as exc:
        return fail(f'preflight tool payload failed schema validation: {exc.message}')

    if payload['inspection_mode'] != 'patch_compile':
        return fail('preflight patch mode should report inspection_mode=patch_compile')
    if payload['inspection_target_path'] != PATCH_PATH.relative_to(ROOT).as_posix():
        return fail('preflight patch mode should point to the patch path')
    if payload['preflight_ready']:
        return fail('template patch should not yet be publication-ready')
    if not payload['mutation_surface_ok']:
        return fail('template patch should stay inside the allowed mutation surface once compiled')
    if payload['completion_ready']:
        return fail('template patch should still fail completion readiness')
    if not payload['decision_bundle_digest_matches_contract']:
        return fail('template patch should preserve copied decision-bundle digest equality')
    expected_counts = {
        'blocking_fill_slot_count': 24,
        'template_blocker_count': 13,
        'null_blocker_count': 11,
        'allowed_decision_null_count': 3,
        'forbidden_changed_path_count': 0,
        'filled_world_section_count': 5,
        'pending_world_section_status_count': 0,
    }
    for key, expected in expected_counts.items():
        if payload['status_counts'][key] != expected:
            return fail(f'unexpected {key}: expected {expected}, got {payload['status_counts'][key]}')

    strict = subprocess.run([sys.executable, str(PREFLIGHT_TOOL), '--patch', str(PATCH_PATH), '--strict'], cwd=ROOT, capture_output=True, text=True, check=False)
    if strict.returncode == 0:
        return fail('strict preflight should fail on the template patch')

    with tempfile.TemporaryDirectory() as tmpdir:
        candidate_path = Path(tmpdir) / 'candidate.json'
        compile_proc = subprocess.run([sys.executable, str(APPLIER_PATH), str(PATCH_PATH), '--output', str(candidate_path)], cwd=ROOT, capture_output=True, text=True, check=False)
        if compile_proc.returncode != 0:
            return fail(f'could not build candidate artifact: {compile_proc.stderr or compile_proc.stdout}')
        candidate = load_json(candidate_path)
        candidate['compact_decision_bundle']['analysis_script'] = 'scripts/report/forbidden_drift.py'
        candidate_path.write_text(json.dumps(candidate, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        drift_code, drift_payload, drift_stderr = run_json([sys.executable, str(PREFLIGHT_TOOL), str(candidate_path), '--json'])
        if drift_code != 0:
            return fail(f'preflight tool exited nonzero on drift artifact without strict mode: {drift_stderr}')
        if drift_payload['mutation_surface_ok']:
            return fail('drift artifact should fail mutation-surface checks')
        if drift_payload['status_counts']['forbidden_changed_path_count'] <= 0:
            return fail('drift artifact should report forbidden changed paths')
        if drift_payload['decision_bundle_digest_matches_contract']:
            return fail('drift artifact should break decision-bundle digest equality')

    print('rematch-world-benchmark-preflight: ok (one command now summarizes compile, mutation, completion, and fingerprint state)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
