#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / 'scripts' / 'report' / 'build_cooperation_benchmark_card_scope_surface.py'
REPORT = ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_scope_surface.json'
DOC = ROOT / 'docs' / 'COOPERATION_BENCHMARK_CARD_SCOPE_SURFACE.md'
SELF_ELIDED = {
    'artifacts/reports/cooperation_benchmark_card_scope_surface.json',
    'docs/COOPERATION_BENCHMARK_CARD_SCOPE_SURFACE.md',
}


def fail(msg: str) -> int:
    print(f'cooperation-benchmark-card-scope-surface: {msg}', file=sys.stderr)
    return 1


def main() -> int:
    proc = subprocess.run([sys.executable, str(BUILDER)], cwd=ROOT, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        return fail(proc.stderr.strip() or proc.stdout.strip() or 'scope surface builder failed')
    if not REPORT.exists():
        return fail(f'missing report {REPORT.relative_to(ROOT)}')
    if not DOC.exists():
        return fail(f'missing doc {DOC.relative_to(ROOT)}')
    data = json.loads(REPORT.read_text(encoding='utf-8'))
    if data.get('scope_surface_kind') != 'cooperation_benchmark_card_scope_surface':
        return fail('unexpected scope_surface_kind')
    if data.get('preferred_for_subsystem_boundary') is not True:
        return fail('preferred_for_subsystem_boundary should be true')
    if data.get('subsystem_id') != 'compact-cooperation-benchmark-card-stack':
        return fail('unexpected subsystem_id')
    categories = data.get('categories', [])
    counts = data.get('counts', {})
    if counts.get('category_count') != len(categories):
        return fail('category_count does not match categories length')
    flat = [row for category in categories for row in category.get('paths', [])]
    if counts.get('path_count') != len(flat):
        return fail('path_count does not match flattened paths length')
    if counts.get('source_path_count') != sum(1 for row in flat if row.get('stage') == 'source'):
        return fail('source_path_count does not match flattened paths')
    if counts.get('generated_path_count') != sum(1 for row in flat if row.get('stage') == 'generated'):
        return fail('generated_path_count does not match flattened paths')
    if counts.get('hashed_path_count') != sum(1 for row in flat if row.get('integrity_mode') == 'hashed'):
        return fail('hashed_path_count does not match flattened paths')
    if counts.get('path_only_path_count') != sum(1 for row in flat if row.get('integrity_mode') == 'path-only'):
        return fail('path_only_path_count does not match flattened paths')
    if counts.get('self_elided_path_count') != sum(1 for row in flat if row.get('integrity_mode') == 'self-elided'):
        return fail('self_elided_path_count does not match flattened paths')
    category_ids = [row.get('category_id') for row in categories]
    if len(category_ids) != len(set(category_ids)):
        return fail('category_id values should be unique')
    paths = [row.get('path') for row in flat]
    if len(paths) != len(set(paths)):
        return fail('scope paths should be unique across categories')
    self_elided = {row['path'] for row in flat if row.get('integrity_mode') == 'self-elided'}
    if self_elided != SELF_ELIDED:
        return fail(f'self-elided paths should equal {sorted(SELF_ELIDED)}')
    if len(data.get('boundary_rules', [])) < 3:
        return fail('expected at least three boundary_rules')
    if len(data.get('verification_commands', [])) < 2:
        return fail('expected at least two verification_commands')
    if len(data.get('refresh_commands', [])) < 2:
        return fail('expected at least two refresh_commands')
    print('cooperation-benchmark-card-scope-surface: ok')
    print(f'cooperation-benchmark-card-scope-surface: validated {REPORT.relative_to(ROOT)} and {DOC.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
