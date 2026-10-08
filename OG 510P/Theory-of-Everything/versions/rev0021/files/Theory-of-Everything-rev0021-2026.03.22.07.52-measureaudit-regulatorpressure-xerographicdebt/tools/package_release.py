#!/usr/bin/env python3
from pathlib import Path
import json
import zipfile

root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / 'RELEASE-MANIFEST.json').read_text())
out = root.parent / manifest['bundle']
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zf:
    for p in root.rglob('*'):
        if p.is_file() and p.name != out.name:
            zf.write(p, p.relative_to(root.parent))
print(out)
