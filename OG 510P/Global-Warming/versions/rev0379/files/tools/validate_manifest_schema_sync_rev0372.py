#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json, sys
ROOT = Path(__file__).resolve().parents[1]
REV='rev0372'
FRONT='579-nuclear-emergency-preparedness-deepread-compilefix-wasteburn-sourceledger-refactor-compact-canon.md'
paths=['manifest.json','cube/manifest.json','schema.json','cube/schema.json','validation-rules.json','cube/validation-rules.json']
errors=[]
for name in paths:
    p=ROOT/name
    try:
        data=json.loads(p.read_text(encoding='utf-8'))
    except Exception as exc:
        errors.append(f'cannot_read_json {name}: {exc}'); continue
    if data.get('revision') != REV:
        errors.append(f'bad_revision {name}={data.get("revision")}')
    if data.get('front_door_canon') != FRONT:
        errors.append(f'bad_front_door {name}={data.get("front_door_canon")}')
for a,b in [('manifest.json','cube/manifest.json'),('schema.json','cube/schema.json'),('validation-rules.json','cube/validation-rules.json')]:
    da=json.loads((ROOT/a).read_text(encoding='utf-8'))
    db=json.loads((ROOT/b).read_text(encoding='utf-8'))
    if da != db:
        errors.append(f'root_cube_mismatch {a} vs {b}')
if errors:
    print('\n'.join(errors)); sys.exit(1)
print('PASS manifest_schema_sync_rev0372 files=6')
