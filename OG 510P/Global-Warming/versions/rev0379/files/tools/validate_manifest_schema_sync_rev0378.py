from __future__ import annotations
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for name in ['manifest.json','schema.json','validation-rules.json']:
    root=json.loads((ROOT/name).read_text(encoding='utf-8'))
    cube=json.loads((ROOT/'cube'/name).read_text(encoding='utf-8'))
    if root!=cube:
        raise SystemExit(f'{name} root/cube mismatch')
    if root.get('revision')!='rev0378':
        raise SystemExit(f'{name} not rev0378')
print('PASS manifest_schema_sync_rev0378')
