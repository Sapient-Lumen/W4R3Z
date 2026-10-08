#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'scripts' / 'report' / 'build_rematch_world_benchmark_native_fill_map.py'
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_native_fill_map.json'
DOC = ROOT / 'docs' / 'REMATCH_WORLD_BENCHMARK_NATIVE_FILL_MAP.md'


def fail(msg: str) -> int:
    print(f'rematch-world-benchmark-native-fill-map: {msg}', file=sys.stderr)
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
    counts = report['minimum_publishable_mutation_set']
    if counts['explicit_fill_blocker_count'] != 24:
        return fail(f"expected 24 explicit fill blockers, got {counts['explicit_fill_blocker_count']}")
    if counts['template_blocker_count'] != 13:
        return fail(f"expected 13 template blockers, got {counts['template_blocker_count']}")
    if counts['null_blocker_count'] != 11:
        return fail(f"expected 11 null blockers, got {counts['null_blocker_count']}")
    if counts['section_status_flip_count'] != 5:
        return fail(f"expected 5 status flips, got {counts['section_status_flip_count']}")
    if counts['additional_metadata_transition_count'] != 1:
        return fail(f"expected 1 additional metadata transition, got {counts['additional_metadata_transition_count']}")
    if counts['mutable_prefix_count'] != 12:
        return fail(f"expected 12 mutable prefixes, got {counts['mutable_prefix_count']}")
    if counts['total_required_edit_count'] != 30:
        return fail(f"expected 30 total required edits, got {counts['total_required_edit_count']}")
    if report['native_section_count'] != 5:
        return fail(f"expected 5 native sections, got {report['native_section_count']}")
    if report['allowed_decision_null_count'] != 3:
        return fail(f"expected 3 allowed decision nulls, got {report['allowed_decision_null_count']}")
    if len(report['metadata_actions']) != 2:
        return fail(f"expected 2 metadata actions, got {len(report['metadata_actions'])}")
    if sum(1 for row in report['metadata_actions'] if row['currently_blocking']) != 1:
        return fail('expected exactly one blocking metadata action')

    section_map = {row['section']: row for row in report['section_rows']}
    expected_counts = {
        'world_semantics_contract': (6, 6, 0),
        'matching_state_contract': (3, 2, 1),
        'occupancy_accounting_contract': (5, 1, 4),
        'turnover_tempo_contract': (4, 2, 2),
        'paired_ranking_views_contract': (5, 1, 4),
    }
    for section, (total, templates, nulls) in expected_counts.items():
        row = section_map.get(section)
        if row is None:
            return fail(f'missing section row for {section}')
        got = (row['blocking_slot_count'], row['template_blocker_count'], row['null_blocker_count'])
        if got != (total, templates, nulls):
            return fail(f'unexpected blocker counts for {section}: {got}')

    text = DOC.read_text(encoding='utf-8')
    for needle in [
        '# Rematch-world benchmark native-fill map',
        '## Minimum publishable mutation set',
        '## Metadata actions',
        '## Native section execution map',
        '## Exact blocker loci by section',
        '## Allowed nulls that are not blockers',
    ]:
        if needle not in text:
            return fail(f'missing markdown section: {needle}')

    print('rematch-world-benchmark-native-fill-map: ok (one compact map now names the exact blocker loci, legal edit prefixes, and minimum publishability edits)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
