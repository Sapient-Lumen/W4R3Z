#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / 'scripts' / 'report' / 'build_cooperation_benchmark_card_execution_lanes.py'
REPORT = ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_execution_lanes.json'
DOC = ROOT / 'docs' / 'COOPERATION_BENCHMARK_CARD_EXECUTION_LANES.md'


def fail(msg: str) -> int:
    print(f'cooperation-benchmark-card-execution-lanes: {msg}', file=sys.stderr)
    return 1


def main() -> int:
    proc = subprocess.run([sys.executable, str(BUILDER)], cwd=ROOT, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        return fail(proc.stderr.strip() or proc.stdout.strip() or 'execution lane builder failed')
    if not REPORT.exists():
        return fail(f'missing report {REPORT.relative_to(ROOT)}')
    if not DOC.exists():
        return fail(f'missing doc {DOC.relative_to(ROOT)}')
    data = json.loads(REPORT.read_text(encoding='utf-8'))
    if data.get('execution_surface_kind') != 'cooperation_benchmark_card_execution_lanes':
        return fail('unexpected execution_surface_kind')
    if data.get('preferred_for_environment_handoff') is not True:
        return fail('expected preferred_for_environment_handoff=true')
    lanes = data.get('lanes', [])
    if len(lanes) < 2:
        return fail('expected at least two execution lanes')
    lane_ids = {row.get('lane_id') for row in lanes}
    if 'python-integrity' not in lane_ids:
        return fail('missing python-integrity lane')
    if 'rust-harness' not in lane_ids:
        return fail('missing rust-harness lane')
    if data.get('preferred_lane_id') not in lane_ids:
        return fail('preferred_lane_id missing from lanes')
    counts = data.get('counts', {})
    if counts.get('available_lane_count', -1) + counts.get('blocked_lane_count', -1) != len(lanes):
        return fail('lane counts do not sum to lane list length')
    python_lane = next(row for row in lanes if row['lane_id'] == 'python-integrity')
    if 'python3' not in python_lane.get('required_capabilities', []):
        return fail('python-integrity lane must require python3')
    rust_lane = next(row for row in lanes if row['lane_id'] == 'rust-harness')
    if 'cargo' not in rust_lane.get('required_capabilities', []):
        return fail('rust-harness lane must require cargo')
    observation = data.get('observation', {})
    junest_home_path = observation.get('junest_home_path')
    if not isinstance(junest_home_path, str) or not junest_home_path:
        return fail('observation.junest_home_path must be a non-empty string')
    junest_home_candidate = Path(junest_home_path)
    if junest_home_candidate.is_absolute():
        try:
            if junest_home_candidate.resolve(strict=False).is_relative_to(ROOT.resolve(strict=False)):
                return fail('observation.junest_home_path must be repo-relative when it points inside the archive root')
        except Exception:
            pass
    print('cooperation-benchmark-card-execution-lanes: ok')
    print(f'cooperation-benchmark-card-execution-lanes: validated {REPORT.relative_to(ROOT)} and {DOC.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
