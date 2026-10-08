from __future__ import annotations
import py_compile, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
errors=[]
for p in sorted((ROOT/'tools').glob('*.py')):
    try:
        py_compile.compile(str(p), doraise=True)
    except Exception as e:
        errors.append(f'{p.name}: {e}')
if errors:
    raise SystemExit('\n'.join(errors[:20]))
print(f'PASS tools compile: {len(list((ROOT/"tools").glob("*.py")))} python files')
