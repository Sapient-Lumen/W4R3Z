from __future__ import annotations
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for rel in ['manifest.json','schema.json','validation-rules.json']:
    root=json.loads((ROOT/rel).read_text(encoding='utf-8'))
    cube=json.loads((ROOT/'cube'/rel).read_text(encoding='utf-8'))
    if root != cube: raise SystemExit(f'{rel} root/cube mismatch')
    if root.get('revision')!='rev0377': raise SystemExit(f'{rel} not rev0377')
print('PASS manifest/schema/rules root-cube sync rev0377')
