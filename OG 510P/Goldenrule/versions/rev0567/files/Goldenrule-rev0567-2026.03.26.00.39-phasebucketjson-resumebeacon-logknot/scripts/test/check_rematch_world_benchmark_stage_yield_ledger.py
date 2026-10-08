#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'scripts' / 'report' / 'build_rematch_world_benchmark_stage_yield_ledger.py'
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_stage_yield_ledger.json'
DOC = ROOT / 'docs' / 'REMATCH_WORLD_BENCHMARK_STAGE_YIELD_LEDGER.md'


def fail(msg: str) -> int:
    print(f'rematch-world-benchmark-stage-yield-ledger: {msg}', file=sys.stderr)
    return 1


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> int:
    for path in [SCRIPT, REPORT, DOC]:
        if not path.exists():
            return fail(f'missing {path.relative_to(ROOT)}')
    proc = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return fail(f'builder exited nonzero: {proc.stderr or proc.stdout}')
    report = load_json(REPORT)
    counts = report['counts']
    if counts['stage_count'] != 7:
        return fail(f"expected 7 stages, got {counts['stage_count']}")
    if counts['claim_unlock_stage_count'] != 3:
        return fail(f"expected 3 claim-unlock stages, got {counts['claim_unlock_stage_count']}")
    if counts['resolver_only_prerequisite_stage_count'] != 2:
        return fail(f"expected 2 resolver-only stages, got {counts['resolver_only_prerequisite_stage_count']}")
    if counts['benchmark_anchor_stage_count'] != 1:
        return fail(f"expected 1 benchmark anchor stage, got {counts['benchmark_anchor_stage_count']}")
    if counts['metadata_closeout_stage_count'] != 1:
        return fail(f"expected 1 metadata closeout stage, got {counts['metadata_closeout_stage_count']}")
    rows = {row['stage_key']: row for row in report['stage_rows']}
    if rows['benchmark_id_binding']['stage_utility_kind'] != 'benchmark_anchor':
        return fail('expected benchmark_id_binding to be benchmark_anchor')
    if rows['matching_state_contract']['stage_utility_kind'] != 'resolver_only_prerequisite':
        return fail('expected matching_state_contract to be resolver_only_prerequisite')
    if rows['turnover_tempo_contract']['stage_utility_kind'] != 'resolver_only_prerequisite':
        return fail('expected turnover_tempo_contract to be resolver_only_prerequisite')
    if rows['artifact_state_transition']['stage_utility_kind'] != 'metadata_closeout':
        return fail('expected artifact_state_transition to be metadata_closeout')
    if rows['world_semantics_contract']['newly_unlocked_claim_family_ids'] != ['RWC-005']:
        return fail('expected world_semantics_contract to unlock RWC-005')
    if rows['occupancy_accounting_contract']['newly_unlocked_claim_family_ids'] != ['RWC-006']:
        return fail('expected occupancy_accounting_contract to unlock RWC-006')
    if rows['paired_ranking_views_contract']['newly_unlocked_claim_family_ids'] != ['RWC-007']:
        return fail('expected paired_ranking_views_contract to unlock RWC-007')
    if rows['matching_state_contract']['newly_unlocked_claim_family_count'] != 0:
        return fail('expected matching_state_contract to unlock zero claims immediately')
    if rows['turnover_tempo_contract']['newly_unlocked_claim_family_count'] != 0:
        return fail('expected turnover_tempo_contract to unlock zero claims immediately')
    if rows['artifact_state_transition']['newly_resolved_touchpoint_count'] != 0:
        return fail('expected artifact_state_transition to resolve zero touchpoints')
    text = DOC.read_text(encoding='utf-8')
    for needle in ['# Rematch-world benchmark stage-yield ledger', '## Utility buckets', '## Stage yield matrix', 'Stage 3 — fill matching_state_contract', 'resolver_only_prerequisite', 'metadata_closeout']:
        if needle not in text:
            return fail(f'missing markdown section or nuance: {needle}')
    print('rematch-world-benchmark-stage-yield-ledger: ok (the first rematch-world native publication now has one exact per-stage yield ledger showing which stages unlock claims, which are prerequisite-only, and which final stage is metadata-only closeout)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
