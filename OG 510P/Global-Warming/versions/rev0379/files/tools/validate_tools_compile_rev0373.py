#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
problems=[]; count=0
for path in sorted((ROOT/'tools').glob('*.py')):
    count+=1
    try:
        compile(path.read_text(encoding='utf-8'), str(path), 'exec')
    except Exception as exc:
        problems.append(f'{path.relative_to(ROOT)}:{exc.__class__.__name__}:{exc}')
if problems:
    print('FAIL tools_compile_rev0373 '+ '; '.join(problems[:20])); sys.exit(1)
print(f'PASS tools_compile_rev0373 files={count}')
