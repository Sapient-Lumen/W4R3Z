from __future__ import annotations
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for name in ['manifest.json','schema.json','validation-rules.json']:
    a=(ROOT/name).read_text(encoding='utf-8')
    b=(ROOT/'cube'/name).read_text(encoding='utf-8')
    if a != b:
        raise SystemExit(f'{name} root/cube mismatch')
    obj=json.loads(a)
    if obj.get('revision') != 'rev0376':
        raise SystemExit(f'{name} revision mismatch: {obj.get("revision")}')
print('PASS manifest/schema/rules root-cube sync rev0376')
