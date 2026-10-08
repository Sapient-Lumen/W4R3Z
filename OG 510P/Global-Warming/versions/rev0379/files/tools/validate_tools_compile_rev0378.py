from __future__ import annotations
import py_compile, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
fail=[]; count=0
for p in (ROOT/'tools').glob('*.py'):
    count+=1
    try:
        py_compile.compile(str(p), doraise=True)
    except Exception as e:
        fail.append((p.name,str(e)))
if fail:
    raise SystemExit('compile failures: '+repr(fail[:10]))
print(f'PASS tools_compile_rev0378 files={count}')
