#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / 'scripts' / 'tools' / 'cooperation_benchmark_card.py'
EXAMPLE_JSON = ROOT / 'examples' / 'snapshots' / 'cooperation_benchmark_card_example.json'


def fail(msg: str) -> int:
    print(f'cooperation-benchmark-card-readiness-lint: {msg}', file=sys.stderr)
    return 1


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)


def main() -> int:
    good = run('python3', str(TOOL), 'lint', str(EXAMPLE_JSON))
    if good.returncode != 0:
        return fail(f'example card should pass lint: {good.stderr.strip()}')
    if 'claim-ready' not in good.stdout:
        return fail('expected success output to mention claim-ready status')

    with tempfile.TemporaryDirectory() as tmp:
        draft_path = Path(tmp) / 'draft.json'
        scaffold = run(
            'python3', str(TOOL), 'scaffold',
            '--id', 'draft-example',
            '--benchmark-name', 'Draft Example Benchmark',
            '--output', str(draft_path),
        )
        if scaffold.returncode != 0:
            return fail(f'scaffold command failed: {scaffold.stderr.strip()}')
        bad = run('python3', str(TOOL), 'lint', str(draft_path))
        if bad.returncode == 0:
            return fail('scaffold draft should fail readiness lint until TODO placeholders are resolved')
        combined = (bad.stdout + '\n' + bad.stderr).lower()
        if 'todo' not in combined:
            return fail('expected lint failure to mention unresolved TODO placeholders')

    print('cooperation-benchmark-card-readiness-lint: ok')
    print(f'cooperation-benchmark-card-readiness-lint: validated {TOOL.relative_to(ROOT)} claim-ready gating')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
