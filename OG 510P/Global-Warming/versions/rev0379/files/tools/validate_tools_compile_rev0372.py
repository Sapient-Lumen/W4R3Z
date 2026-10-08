#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
errors=[]
files=sorted((ROOT/'tools').glob('*.py'))
for p in files:
    try:
        source=p.read_text(encoding='utf-8')
        compile(source, str(p), 'exec')
    except Exception as exc:
        errors.append(f'{p.relative_to(ROOT)}: {type(exc).__name__}: {exc}')
if errors:
    print('\n'.join(errors)); sys.exit(1)
print(f'PASS tools_compile_rev0372 files={len(files)}')
