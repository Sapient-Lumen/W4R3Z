from __future__ import annotations
import py_compile, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
files=sorted((ROOT/'tools').glob('*.py'))
for p in files:
    py_compile.compile(str(p), doraise=True)
print(f'PASS tools compile: {len(files)} python files')
