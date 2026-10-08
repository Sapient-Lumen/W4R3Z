#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / 'docs' / 'BENCHMARK_PROGRAM.md'

REQUIRED_COMMANDS = [
    './grpy ./scripts/tools/cooperation_benchmark_card.py scaffold',
    './grpy ./scripts/tools/cooperation_benchmark_card.py render',
    './grpy ./scripts/tools/cooperation_benchmark_card.py lint',
    './grpy ./scripts/tools/cooperation_benchmark_card.py freeze',
    './grpy ./scripts/tools/cooperation_benchmark_card.py compare',
    './grpy ./scripts/report/build_cooperation_benchmark_card_inventory.py --write',
    './grpy ./scripts/report/build_cooperation_benchmark_card_heads.py --write',
    './grpy ./scripts/report/build_cooperation_benchmark_card_review_queue.py --write',
    './grpy ./scripts/report/build_cooperation_benchmark_card_citation_surface.py --write',
    './grpy ./scripts/report/build_cooperation_benchmark_card_handoff_pack.py --write',
    './grpy ./scripts/report/build_cooperation_benchmark_card_control_plane.py --write',
    './grpy ./scripts/report/build_cooperation_benchmark_card_next_action.py --write',
    './grpy ./scripts/report/build_cooperation_benchmark_card_next_action_witness.py --write',
    './grpy ./scripts/report/build_cooperation_benchmark_card_execution_lanes.py --write',
]
LEGACY_PATTERN = re.compile(r'`python3 ./scripts/(?:tools|report|test)/(?:cooperation_benchmark_card|build_cooperation_benchmark_card|check_cooperation_benchmark_card)[^`]*`')

def fail(msg: str) -> int:
    print(f'cooperation-benchmark-program-compact-card-command-surface: {msg}', file=sys.stderr)
    return 1

def main() -> int:
    text = DOC.read_text(encoding='utf-8')
    legacy_matches = LEGACY_PATTERN.findall(text)
    if legacy_matches:
        return fail(f'legacy bare-python compact-card commands remain in docs/BENCHMARK_PROGRAM.md: {legacy_matches[0]}')
    missing = [cmd for cmd in REQUIRED_COMMANDS if cmd not in text]
    if missing:
        return fail(f'missing wrapper-normalized compact-card command in docs/BENCHMARK_PROGRAM.md: {missing[0]}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
