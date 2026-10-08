#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_publication_bundle_receipt.schema.json'
EXAMPLE_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_publication_bundle_receipt.json'
TOOL_PATH = ROOT / 'scripts' / 'tools' / 'build_rematch_world_benchmark_publication_bundle_receipt.py'


def fail(msg: str) -> int:
    print(f'publication-bundle-receipt: {msg}', file=sys.stderr)
    return 1


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> int:
    if not SCHEMA_PATH.exists():
        return fail(f'missing {SCHEMA_PATH.relative_to(ROOT)}')
    if not EXAMPLE_PATH.exists():
        return fail(f'missing {EXAMPLE_PATH.relative_to(ROOT)}')

    schema = load_json(SCHEMA_PATH)
    receipt = load_json(EXAMPLE_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(receipt, schema)

    if not receipt['patch_elision_ready']:
        return fail('expected patch_elision_ready=true for example receipt')
    if receipt['patch_retention_required']:
        return fail('expected patch_retention_required=false for example receipt')
    if receipt['patch_written']:
        return fail('expected example receipt to leave patch transient')
    if receipt['preflight']['blocking_fill_slot_count'] != 0:
        return fail('expected zero blocking fill slots in example receipt')
    if receipt['preflight']['forbidden_changed_path_count'] != 0:
        return fail('expected zero forbidden changed paths in example receipt')
    if receipt['preflight']['allowed_decision_null_count'] != 3:
        return fail('expected three allowed decision nulls in example receipt')
    if not receipt['evidence_receipt_matches_packet']:
        return fail('expected packet/evidence receipt digest alignment')
    if not receipt['evidence_receipt_strict_coverage_passed']:
        return fail('expected strict evidence coverage to pass')
    if 'compiled_benchmark_artifact' not in receipt['recommended_retained_objects']:
        return fail('recommended retained objects missing compiled benchmark artifact')
    if not receipt['decision_emission']['world_emission_ready']:
        return fail('expected publication bundle to mark phase-3 world emission ready')
    if not receipt['decision_emission']['bundle_matches_standing_contract']:
        return fail('expected copied decision bundle to match the standing contract')
    if receipt['decision_emission']['standing_contract_sha256'] != receipt['decision_contract_sha256']:
        return fail('expected decision_emission to carry the same standing decision contract digest as the receipt')
    if receipt['decision_emission']['emitted_question_id_count'] != 10:
        return fail('expected all ten SG-003 phase-3 questions to be covered explicitly')
    if receipt['decision_emission']['allowed_open_interval_count'] != 3:
        return fail('expected three allowed open-ended winner intervals in decision emission summary')
    section_names = [row['section'] for row in receipt['decision_emission']['emitted_sections']]
    if section_names != ['delay_contract', 'winner_contract', 'delta_contract']:
        return fail('expected decision emission sections in canonical delay/winner/delta order')

    with tempfile.TemporaryDirectory() as tmpdir:
        artifact_path = Path(tmpdir) / 'compiled_benchmark.json'
        output_path = Path(tmpdir) / 'bundle_receipt.json'
        proc = subprocess.run(
            [
                sys.executable,
                str(TOOL_PATH),
                '--artifact-output',
                str(artifact_path),
                '--output',
                str(output_path),
                '--strict',
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            return fail(f'cli strict mode failed: {proc.stderr or proc.stdout}')
        if not artifact_path.exists():
            return fail('expected artifact output file to be written')
        emitted = load_json(output_path)
        if not emitted['artifact_written']:
            return fail('expected emitted receipt to record artifact_written=true')
        if emitted['compiled_candidate']['artifact_output_path'] != str(artifact_path):
            return fail('artifact_output_path mismatch in emitted receipt')
        if emitted['patch_written']:
            return fail('expected emitted receipt to keep patch transient by default')
        if not emitted['decision_emission']['world_emission_ready']:
            return fail('expected emitted receipt to preserve explicit phase-3 emission proof')

    print('publication-bundle-receipt: ok (example validates, keeps the patch transient, and explicitly proves phase-3 decision emission)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
