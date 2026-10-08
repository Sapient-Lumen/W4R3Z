#!/usr/bin/env python3
from __future__ import annotations
import py_compile, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
problems=[]; count=0
for p in sorted((ROOT/'tools').glob('*.py')):
    count += 1
    try: py_compile.compile(str(p), doraise=True)
    except Exception as exc: problems.append(f'{p.name}:{exc}')
if problems:
    print('FAIL tools_compile_rev0375 '+ '; '.join(problems[:20])); sys.exit(1)
print(f'PASS tools_compile_rev0375 files={count}')
