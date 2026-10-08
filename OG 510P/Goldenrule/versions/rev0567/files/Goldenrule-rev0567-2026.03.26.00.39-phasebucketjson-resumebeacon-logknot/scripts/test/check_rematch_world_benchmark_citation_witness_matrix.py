#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'scripts' / 'report' / 'build_rematch_world_benchmark_citation_witness_matrix.py'
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_citation_witness_matrix.json'
DOC = ROOT / 'docs' / 'REMATCH_WORLD_BENCHMARK_CITATION_WITNESS_MATRIX.md'


def fail(msg: str) -> int:
    print(f'rematch-world-benchmark-citation-witness-matrix: {msg}', file=sys.stderr)
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
    if counts['bridge_ready_count'] != 4:
        return fail(f"expected 4 bridge-ready families, got {counts['bridge_ready_count']}")
    if counts['provisional_interpretation_count'] != 3:
        return fail(f"expected 3 provisional families, got {counts['provisional_interpretation_count']}")
    if counts['final_authority_count'] != 1:
        return fail(f"expected 1 final-authority family, got {counts['final_authority_count']}")
    if counts['minimal_unique_surface_count'] != 7:
        return fail(f"expected 7 cited surfaces, got {counts['minimal_unique_surface_count']}")
    if counts['open_spec_touchpoint_count'] != 11:
        return fail(f"expected 11 open spec touchpoints, got {counts['open_spec_touchpoint_count']}")

    rows = {row['claim_family_id']: row for row in report['claim_family_rows']}
    expected_postures = {
        'RWC-001': 'bridge_ready',
        'RWC-002': 'bridge_ready',
        'RWC-003': 'bridge_ready',
        'RWC-004': 'bridge_ready',
        'RWC-005': 'provisional_interpretation',
        'RWC-006': 'provisional_interpretation',
        'RWC-007': 'provisional_interpretation',
        'RWC-008': 'final_authority',
    }
    if set(rows) != set(expected_postures):
        return fail(f'unexpected claim family ids: {sorted(rows)}')
    for claim_id, posture in expected_postures.items():
        if rows[claim_id]['posture'] != posture:
            return fail(f'{claim_id} posture drifted: expected {posture}, got {rows[claim_id]["posture"]}')

    if rows['RWC-002']['minimal_citation_count'] != 2:
        return fail('expected RWC-002 to cite exactly two surfaces')
    if rows['RWC-008']['open_spec_ids']:
        return fail('expected final-authority row to have no open spec ids')
    if 'package_ready=True' not in rows['RWC-008']['claim_summary']:
        return fail('expected final-authority summary to expose package_ready=True')
    if '33 JSON paths' not in rows['RWC-002']['claim_summary']:
        return fail('expected mutation witness summary to mention the 33-path exact delta')
    if '7 ordered edit stages' not in rows['RWC-003']['claim_summary']:
        return fail('expected landing-order summary to mention the 7-stage ladder')

    text = DOC.read_text(encoding='utf-8')
    for needle in [
        '# Rematch-world benchmark citation witness matrix',
        '## Claim family matrix',
        '## Claim family details',
        '## Cited surfaces',
        '## Open spec touchpoints',
    ]:
        if needle not in text:
            return fail(f'missing markdown section: {needle}')

    print('rematch-world-benchmark-citation-witness-matrix: ok (the first rematch-world publication now has one minimal citation witness surface mapping eight claim families onto seven small citation paths and eleven open spec touchpoints)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
