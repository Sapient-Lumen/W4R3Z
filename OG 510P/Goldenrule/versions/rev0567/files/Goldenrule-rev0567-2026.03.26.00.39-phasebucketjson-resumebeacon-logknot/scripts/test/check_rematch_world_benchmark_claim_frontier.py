#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'scripts' / 'report' / 'build_rematch_world_benchmark_claim_frontier.py'
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_claim_frontier.json'
DOC = ROOT / 'docs' / 'REMATCH_WORLD_BENCHMARK_CLAIM_FRONTIER.md'


def fail(msg: str) -> int:
    print(f'rematch-world-benchmark-claim-frontier: {msg}', file=sys.stderr)
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
    if counts['claim_family_count'] != 8:
        return fail(f"expected 8 claim families, got {counts['claim_family_count']}")
    if counts['safe_to_cite_now_count'] != 2:
        return fail(f"expected 2 safe-now families, got {counts['safe_to_cite_now_count']}")
    if counts['native_stage_unlock_count'] != 3:
        return fail(f"expected 3 staged unlock families, got {counts['native_stage_unlock_count']}")
    if counts['blocked_by_engine_gap_count'] != 3:
        return fail(f"expected 3 engine-gap-blocked families, got {counts['blocked_by_engine_gap_count']}")
    if counts['actionable_cumulative_frontier_sequence'] != [8, 18, 29]:
        return fail(f"expected actionable frontier sequence [8, 18, 29], got {counts['actionable_cumulative_frontier_sequence']}")
    if counts['benchmark_identity_prerequisite_edit_count'] != 1:
        return fail('expected benchmark identity prerequisite edit count to stay at 1')

    rows = {row['claim_family_id']: row for row in report['frontier_rows']}
    expected_kinds = {
        'RWC-001': 'blocked_by_engine_gap',
        'RWC-002': 'blocked_by_engine_gap',
        'RWC-003': 'safe_to_cite_now',
        'RWC-004': 'blocked_by_engine_gap',
        'RWC-005': 'native_stage_unlock',
        'RWC-006': 'native_stage_unlock',
        'RWC-007': 'native_stage_unlock',
        'RWC-008': 'safe_to_cite_now',
    }
    if set(rows) != set(expected_kinds):
        return fail(f'unexpected claim family ids: {sorted(rows)}')
    for claim_id, expected_kind in expected_kinds.items():
        if rows[claim_id]['frontier_kind'] != expected_kind:
            return fail(f'{claim_id} frontier kind drifted: expected {expected_kind}, got {rows[claim_id]["frontier_kind"]}')

    if rows['RWC-005']['cumulative_required_edit_count'] != 8:
        return fail('expected RWC-005 to unlock at cumulative edit 8')
    if rows['RWC-006']['cumulative_required_edit_count'] != 18:
        return fail('expected RWC-006 to unlock at cumulative edit 18')
    if rows['RWC-007']['cumulative_required_edit_count'] != 29:
        return fail('expected RWC-007 to unlock at cumulative edit 29')
    if rows['RWC-006']['resolver_ids'] != ['SQ-013', 'SQ-014']:
        return fail(f"expected RWC-006 resolver ids ['SQ-013', 'SQ-014'], got {rows['RWC-006']['resolver_ids']}")
    if rows['RWC-001']['blocking_resolver_id'] != 'SG-003':
        return fail('expected RWC-001 to stay blocked by SG-003')
    if 'not 7/17/28' not in ' '.join(report['main_findings']):
        return fail('expected main findings to mention the 8/18/29 vs 7/17/28 nuance')

    text = DOC.read_text(encoding='utf-8')
    for needle in [
        '# Rematch-world benchmark claim frontier',
        '## Frontier buckets',
        '## Claim frontier matrix',
        '## Claim family details',
        '8, 18, 29',
    ]:
        if needle not in text:
            return fail(f'missing markdown section or nuance: {needle}')

    print('rematch-world-benchmark-claim-frontier: ok (the first rematch-world publication now has one exact readiness frontier showing which two claim families are safe now, which three unlock at 8/18/29 cumulative edits, and which three remain blocked by SG-003)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
