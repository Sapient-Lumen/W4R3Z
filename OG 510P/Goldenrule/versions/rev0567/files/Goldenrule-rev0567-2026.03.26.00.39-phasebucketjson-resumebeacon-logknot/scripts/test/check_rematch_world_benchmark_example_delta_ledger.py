#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'scripts' / 'report' / 'build_rematch_world_benchmark_example_delta_ledger.py'
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_example_delta_ledger.json'
DOC = ROOT / 'docs' / 'REMATCH_WORLD_BENCHMARK_EXAMPLE_DELTA_LEDGER.md'


def fail(msg: str) -> int:
    print(f'rematch-world-benchmark-example-delta-ledger: {msg}', file=sys.stderr)
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
    if report['total_changed_path_count'] != 33:
        return fail(f"expected 33 changed paths, got {report['total_changed_path_count']}")
    if report['required_publishable_change_count'] != 30:
        return fail(f"expected 30 required publication changes, got {report['required_publishable_change_count']}")
    if report['optional_change_count'] != 3:
        return fail(f"expected 3 optional row insertions, got {report['optional_change_count']}")
    if not report['compiled_snapshot_matches_live_toolchain']:
        return fail('expected compiled example snapshot to match the live packet->artifact toolchain')
    if not report['patch_elision_ready']:
        return fail('expected example publication bundle to be patch-elision ready')

    expected_classes = {
        'metadata_binding': 1,
        'metadata_transition': 1,
        'optional_row_insertion': 3,
        'section_status_flip': 5,
        'world_fill_blocker_clear': 23,
    }
    if report['change_class_counts'] != expected_classes:
        return fail(f"unexpected class counts: {report['change_class_counts']}")

    expected_optional = [
        'occupancy_accounting_contract.policy_rows[1]',
        'paired_ranking_views_contract.leaderboard_rows[1]',
        'turnover_tempo_contract.policy_rows[1]',
    ]
    if sorted(report['optional_paths']) != expected_optional:
        return fail(f"unexpected optional paths: {report['optional_paths']}")

    frozen = set(report['unchanged_frozen_roots'])
    for root_name in [
        'canonicalization_planner_contract',
        'winner_triage_handoff',
        'delta_shortlist_handoff',
        'paired_ranking_interpretation_handoff',
        'matching_state_interpretation_handoff',
        'turnover_tempo_interpretation_handoff',
        'world_semantics_interpretation_handoff',
        'compact_decision_bundle',
    ]:
        if root_name not in frozen:
            return fail(f'frozen root missing from untouched set: {root_name}')

    text = DOC.read_text(encoding='utf-8')
    for needle in [
        '# Rematch-world benchmark example delta ledger',
        '## Change counts',
        '## Section delta summary',
        '## Exact changed paths',
        '## Frozen roots that stay untouched',
    ]:
        if needle not in text:
            return fail(f'missing markdown section: {needle}')

    print('rematch-world-benchmark-example-delta-ledger: ok (the synthetic rematch-world compiled example now has one exact 33-path mutation ledger with the 30-path publication floor separated from the 3 optional row insertions)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
