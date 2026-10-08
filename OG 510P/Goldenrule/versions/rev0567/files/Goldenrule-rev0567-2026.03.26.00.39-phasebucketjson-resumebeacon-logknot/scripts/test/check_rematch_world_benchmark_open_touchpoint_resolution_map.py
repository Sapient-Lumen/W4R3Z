#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'scripts' / 'report' / 'build_rematch_world_benchmark_open_touchpoint_resolution_map.py'
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_open_touchpoint_resolution_map.json'
DOC = ROOT / 'docs' / 'REMATCH_WORLD_BENCHMARK_OPEN_TOUCHPOINT_RESOLUTION_MAP.md'


def fail(msg: str) -> int:
    print(f'rematch-world-benchmark-open-touchpoint-resolution-map: {msg}', file=sys.stderr)
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
    if counts['open_touchpoint_count'] != 11:
        return fail(f"expected 11 open touchpoints, got {counts['open_touchpoint_count']}")
    if counts['closure_target_count'] != 6:
        return fail(f"expected 6 closure targets, got {counts['closure_target_count']}")
    if counts['native_question_target_count'] != 5:
        return fail(f"expected 5 native-question targets, got {counts['native_question_target_count']}")
    if counts['cross_section_gap_target_count'] != 1:
        return fail(f"expected 1 cross-section gap target, got {counts['cross_section_gap_target_count']}")
    if counts['folded_assumption_count'] != 5:
        return fail(f"expected 5 folded assumptions, got {counts['folded_assumption_count']}")
    if counts['affected_claim_family_count'] != 6:
        return fail(f"expected 6 affected claim families, got {counts['affected_claim_family_count']}")
    if counts['seed_local_blocker_slot_count'] != 23:
        return fail(f"expected 23 seed-local blocker slots, got {counts['seed_local_blocker_slot_count']}")
    if counts['seed_local_required_edit_count'] != 28:
        return fail(f"expected 28 seed-local required edits, got {counts['seed_local_required_edit_count']}")
    if counts['seed_local_section_status_flip_count'] != 5:
        return fail(f"expected 5 section-status flips, got {counts['seed_local_section_status_flip_count']}")
    if counts['pending_native_section_count'] != 5:
        return fail(f"expected 5 pending native sections, got {counts['pending_native_section_count']}")

    rows = {row['resolver_id']: row for row in report['resolution_rows']}
    expected_ids = ['SG-003', 'SQ-012', 'SQ-013', 'SQ-014', 'SQ-015', 'SQ-016']
    if list(rows) != expected_ids:
        return fail(f'unexpected resolver ids or order: {list(rows)}')

    if rows['SG-003']['native_section'] is not None:
        return fail('expected SG-003 to stay cross-section with no native section')
    if rows['SG-003']['dependent_assumption_ids'] != ['SA-003']:
        return fail(f"expected SG-003 to fold SA-003, got {rows['SG-003']['dependent_assumption_ids']}")
    if rows['SG-003']['affected_claim_family_ids'] != ['RWC-001', 'RWC-002', 'RWC-004']:
        return fail(f"unexpected SG-003 affected claims: {rows['SG-003']['affected_claim_family_ids']}")

    sq012 = rows['SQ-012']
    if sq012['native_section'] != 'world_semantics_contract':
        return fail(f"SQ-012 native section drifted: {sq012['native_section']}")
    if sq012['blocking_slot_count'] != 6 or sq012['required_edit_count'] != 7:
        return fail('expected SQ-012 to keep the 6-slot / 7-edit landing requirement')
    if sq012['dependent_assumption_ids'] != ['SA-011']:
        return fail(f"expected SQ-012 to fold SA-011, got {sq012['dependent_assumption_ids']}")

    sq013 = rows['SQ-013']
    if sq013['native_section'] != 'matching_state_contract':
        return fail(f"SQ-013 native section drifted: {sq013['native_section']}")
    if sq013['blocking_slot_count'] != 3 or sq013['required_edit_count'] != 4:
        return fail('expected SQ-013 to keep the 3-slot / 4-edit landing requirement')
    if sq013['dependent_assumption_ids'] != ['SA-012']:
        return fail(f"expected SQ-013 to fold SA-012, got {sq013['dependent_assumption_ids']}")

    sq014 = rows['SQ-014']
    if sq014['native_section'] != 'occupancy_accounting_contract':
        return fail(f"SQ-014 native section drifted: {sq014['native_section']}")
    if sq014['blocking_slot_count'] != 5 or sq014['required_edit_count'] != 6:
        return fail('expected SQ-014 to keep the 5-slot / 6-edit landing requirement')
    if sq014['dependent_assumption_ids'] != ['SA-013']:
        return fail(f"expected SQ-014 to fold SA-013, got {sq014['dependent_assumption_ids']}")

    sq015 = rows['SQ-015']
    if sq015['native_section'] != 'turnover_tempo_contract':
        return fail(f"SQ-015 native section drifted: {sq015['native_section']}")
    if sq015['blocking_slot_count'] != 4 or sq015['required_edit_count'] != 5:
        return fail('expected SQ-015 to keep the 4-slot / 5-edit landing requirement')
    if sq015['dependent_assumption_ids']:
        return fail(f"expected SQ-015 to have no folded assumptions, got {sq015['dependent_assumption_ids']}")

    sq016 = rows['SQ-016']
    if sq016['native_section'] != 'paired_ranking_views_contract':
        return fail(f"SQ-016 native section drifted: {sq016['native_section']}")
    if sq016['blocking_slot_count'] != 5 or sq016['required_edit_count'] != 6:
        return fail('expected SQ-016 to keep the 5-slot / 6-edit landing requirement')
    if sq016['dependent_assumption_ids'] != ['SA-015']:
        return fail(f"expected SQ-016 to fold SA-015, got {sq016['dependent_assumption_ids']}")

    text = DOC.read_text(encoding='utf-8')
    for needle in [
        '# Rematch-world benchmark open touchpoint resolution map',
        '## Closure target matrix',
        '## Closure target details',
        '## Folded assumptions',
        'seed_local_required_edit_count: 28',
    ]:
        if needle not in text:
            return fail(f'missing markdown section or fact: {needle}')

    print('rematch-world-benchmark-open-touchpoint-resolution-map: ok (the first rematch-world publication now compresses eleven open touchpoints into six actionable closure targets, with five folded assumptions and an explicit 23-slot / 28-edit seed-local landing queue)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
