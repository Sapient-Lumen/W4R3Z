#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'scripts' / 'report' / 'build_rematch_world_benchmark_landing_ladder.py'
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_landing_ladder.json'
DOC = ROOT / 'docs' / 'REMATCH_WORLD_BENCHMARK_LANDING_LADDER.md'


def fail(msg: str) -> int:
    print(f'rematch-world-benchmark-landing-ladder: {msg}', file=sys.stderr)
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
    if report['required_edit_total'] != 30:
        return fail(f"expected 30 required edits, got {report['required_edit_total']}")
    if report['edit_stage_count'] != 7:
        return fail(f"expected 7 edit stages, got {report['edit_stage_count']}")
    if report['closeout_phase_count'] != 5:
        return fail(f"expected 5 closeout phases, got {report['closeout_phase_count']}")
    if report['cumulative_required_edit_sequence'] != [1, 8, 12, 18, 23, 29, 30]:
        return fail(f"unexpected cumulative sequence: {report['cumulative_required_edit_sequence']}")

    rows = report['edit_stage_rows']
    if rows[0]['stage_key'] != 'benchmark_id_binding' or rows[0]['required_edit_count'] != 1:
        return fail('first edit stage should be single benchmark_id binding')
    if rows[-1]['stage_key'] != 'artifact_state_transition' or rows[-1]['required_edit_count'] != 1:
        return fail('last edit stage should be single artifact_state transition')

    expected_sections = [
        ('world_semantics_contract', 7),
        ('matching_state_contract', 4),
        ('occupancy_accounting_contract', 6),
        ('turnover_tempo_contract', 5),
        ('paired_ranking_views_contract', 6),
    ]
    got_sections = [(row['stage_key'], row['required_edit_count']) for row in rows[1:-1]]
    if got_sections != expected_sections:
        return fail(f'unexpected section edit rows: {got_sections}')

    expected_phase_orders = [[1, 2], [3, 4], [5, 6], [7, 8, 9], [10]]
    got_phase_orders = [row['landing_step_orders'] for row in report['closeout_phase_rows']]
    if got_phase_orders != expected_phase_orders:
        return fail(f'unexpected closeout phase orders: {got_phase_orders}')

    text = DOC.read_text(encoding='utf-8')
    for needle in [
        '# Rematch-world benchmark landing ladder',
        '## Exact edit ladder',
        '## Post-edit closeout ladder',
        '## Implementor takeaway',
    ]:
        if needle not in text:
            return fail(f'missing markdown section: {needle}')

    print('rematch-world-benchmark-landing-ladder: ok (one compact ladder now names the exact 7 edit stages and 5 closeout phases for the first native rematch-world publication)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
