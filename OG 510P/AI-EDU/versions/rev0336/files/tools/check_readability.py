"""Fail on very long Markdown prose lines that make re-entry and review brittle."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_LEN = 1000
violations: list[tuple[int, str, int]] = []

for path in sorted(ROOT.rglob('*.md')):
    if any(part == '__pycache__' for part in path.parts):
        continue
    in_code = False
    for lineno, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith(('```', '~~~')):
            in_code = not in_code
            continue
        if in_code or stripped.startswith('|'):
            continue
        if len(line) > MAX_LEN:
            violations.append((len(line), path.relative_to(ROOT).as_posix(), lineno))

if violations:
    print(f'check_readability: FAIL ({len(violations)} markdown prose lines > {MAX_LEN} chars)')
    for length, rel, lineno in sorted(violations, reverse=True)[:25]:
        print(f'  {length:5d} {rel}:{lineno}')
    raise SystemExit(1)
print(f'check_readability: OK (no markdown prose lines > {MAX_LEN} chars)')
