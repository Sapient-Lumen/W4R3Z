#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, zipfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT.parent
manifest = json.loads((ROOT / 'RELEASE-MANIFEST.json').read_text(encoding='utf-8'))
bundle = BASE / manifest['bundle']
subprocess.run(['python', str(ROOT / 'tools/lint_cube.py')], check=True)
if bundle.exists(): bundle.unlink()
with zipfile.ZipFile(bundle, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for p in sorted(ROOT.rglob('*')):
        if p.is_file():
            z.write(p, p.relative_to(ROOT.parent))
print(bundle)
