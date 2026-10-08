#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

EXPECTED_STRICT_PACKETS = {
    'U-123',
    'PB-01',
    'SEARCH-RESP-01A',
    'SEARCH-RESP-01B-BUDDY',
    'SEARCH-RESP-01C-ROOM',
    'SEARCH-RESP-PARSE-BUDGET-A',
    'SEARCH-RESP-PARSE-BUDGET-B',
}
EXPECTED_PUBLIC_ROWS = {'PUBLIC-PATH-JOIN-PR-3781', 'PUBLIC-PATH-JOIN-PR-3723'}
FORBIDDEN_PARTS = {'__pycache__', '.pytest_cache', 'source-trees', 'git-full', '.git'}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def main() -> int:
    cube = Path(__file__).resolve().parents[1]
    checks: list[dict[str, object]] = []
    errors: list[str] = []

    # Inherited handoff export helper must still pass.
    helper = cube / 'tools' / 'probe_rev0048_handoff_export.py'
    proc = subprocess.run([sys.executable, str(helper)], cwd=str(cube), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
    try:
        helper_out = json.loads(proc.stdout)
    except json.JSONDecodeError:
        helper_out = {'status': 'unparseable', 'stdout': proc.stdout, 'stderr': proc.stderr}
    helper_pass = proc.returncode == 0 and helper_out.get('status') == 'pass'
    checks.append({'check': 'rev0048 handoff export helper', 'status': 'pass' if helper_pass else 'fail', 'returncode': proc.returncode, 'helper_status': helper_out.get('status')})
    if not helper_pass:
        errors.append('rev0048 handoff export helper did not pass')

    strict_rows = read_csv(cube / 'data' / 'rev0049_strict_promotions.csv')
    strict_packets = {row.get('packet', '') for row in strict_rows}
    strict_ok = strict_packets == EXPECTED_STRICT_PACKETS and len(strict_rows) == 7
    checks.append({'check': 'strict packet set unchanged', 'status': 'pass' if strict_ok else 'fail', 'packets': sorted(strict_packets)})
    if not strict_ok:
        errors.append(f'strict packet set mismatch: {sorted(strict_packets)}')

    public_rows = read_csv(cube / 'data' / 'rev0049_public_path_watch.csv')
    public_ids = {row.get('row', '') for row in public_rows}
    public_ok = public_ids == EXPECTED_PUBLIC_ROWS and all('no private packet opened' in row.get('cube_decision', '') for row in public_rows)
    checks.append({'check': 'public path watch rows are non-promoted', 'status': 'pass' if public_ok else 'fail', 'rows': sorted(public_ids)})
    if not public_ok:
        errors.append('public path watch rows are missing or not marked non-promoted')

    refactor_rows = read_csv(cube / 'data' / 'rev0049_handoff_gate_refactor.csv')
    required_bundles = {'01-transfer-session-identity', '02-peer-primary-election', '03-search-response-source-admission', '04-search-response-parser-budget', 'public-watch-only'}
    bundle_set = {row.get('bundle', '') for row in refactor_rows}
    refactor_ok = bundle_set == required_bundles
    checks.append({'check': 'handoff gate refactor rows', 'status': 'pass' if refactor_ok else 'fail', 'bundles': sorted(bundle_set)})
    if not refactor_ok:
        errors.append('handoff gate refactor bundle rows mismatch')

    # Basic package hygiene from the unpacked tree.
    bad_paths = []
    for path in cube.rglob('*'):
        if any(part in FORBIDDEN_PARTS for part in path.relative_to(cube).parts):
            bad_paths.append(str(path.relative_to(cube)))
    checks.append({'check': 'package hygiene forbidden paths', 'status': 'pass' if not bad_paths else 'fail', 'bad_path_count': len(bad_paths), 'bad_paths': bad_paths[:20]})
    if bad_paths:
        errors.append('forbidden cache/source path present')

    start = (cube / 'docs' / 'START-HERE.md').read_text(encoding='utf-8', errors='replace')
    readme = (cube / 'README.md').read_text(encoding='utf-8', errors='replace')
    text_ok = 'rev0049' in start and 'PUBLIC-PATH-JOIN-PR-3781' in start and 'rev0049' in readme
    checks.append({'check': 'rev0049 start/readme markers', 'status': 'pass' if text_ok else 'fail'})
    if not text_ok:
        errors.append('START-HERE/README rev0049 markers missing')

    out = {
        'revision': 'rev0049',
        'status': 'pass' if not errors else 'fail',
        'strict_packet_count': len(strict_rows),
        'public_watch_count': len(public_rows),
        'checks': checks,
        'errors': errors,
    }
    print(json.dumps(out, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
