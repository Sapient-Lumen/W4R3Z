#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
import jsonschema
ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / 'schemas' / 'rematch_world_benchmark_publication_chain_receipt.schema.json'
EXAMPLE = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_publication_chain_receipt.json'
TOOL = ROOT / 'scripts' / 'tools' / 'build_rematch_world_benchmark_publication_chain_receipt.py'
EXPECTED_STAGES = ['frozen_seed_rebuild_audit','compiled_artifact_copy_forward_audit','durable_publication_spine_audit','post_prune_zip_readiness_audit']
EXPECTED_QUESTION_IDS = ['SQ-003','SQ-004','SQ-005','SQ-006','SQ-007','SQ-008','SQ-009','SQ-010','SQ-011','SQ-018','SQ-019','SQ-020','SQ-021','SQ-022','SQ-014','SQ-016','SQ-013','SQ-015','SQ-012','SQ-017','SQ-023','SQ-024','SQ-025','SQ-026']
def fail(msg: str) -> int:
    print(f'rematch-world-benchmark-publication-chain-receipt: {msg}', file=sys.stderr); return 1
def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))
def main() -> int:
    for path in [SCHEMA, EXAMPLE, TOOL]:
        if not path.exists(): return fail(f'missing {path.relative_to(ROOT)}')
    schema = load_json(SCHEMA)
    if schema.get('title') != 'Rematch World Benchmark Publication Chain Receipt': return fail('schema title mismatch')
    receipt = load_json(EXAMPLE)
    jsonschema.Draft202012Validator.check_schema(schema); jsonschema.validate(receipt, schema)
    proc = subprocess.run([sys.executable, str(TOOL), '--strict'], cwd=ROOT, capture_output=True, text=True, check=False)
    if proc.returncode != 0: return fail(f'tool exited nonzero: {proc.stderr or proc.stdout}')
    live_receipt = json.loads(proc.stdout)
    if receipt != live_receipt: return fail('example receipt should match the current live tool output exactly')
    if [row['stage'] for row in receipt['chain_links']] != EXPECTED_STAGES: return fail('unexpected chain stages')
    if any(row['ready'] is not True for row in receipt['chain_links']): return fail('every chain link should be ready in the standing example')
    if receipt['compiled_artifact_path'] != 'examples/snapshots/rematch_world_benchmark_compiled_artifact.json': return fail('expected standing compiled artifact path')
    if receipt['coverage']['copied_frozen_section_count'] != 8: return fail('expected 8 copied frozen sections')
    if receipt['coverage']['durable_publication_object_count'] != 6: return fail('expected 6 durable publication objects after prune')
    if receipt['coverage']['question_id_count'] != 24: return fail('expected 24 unique linked question ids')
    if receipt['coverage']['question_ids'] != EXPECTED_QUESTION_IDS: return fail('unexpected question id ordering')
    if receipt['status_counts'] != {'overall_chain_ready': True,'ready_link_count': 4,'total_link_count': 4,'transient_cleared_count': 4}: return fail('unexpected status counts')
    if receipt['archive_posture']['prefer_citation_over_recopy'] is not True: return fail('archive posture should prefer citation over recopy')
    print('rematch-world-benchmark-publication-chain-receipt: ok (one compact chain receipt covers frozen seed, copy-forward, durable publication, and post-prune zip readiness)')
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
