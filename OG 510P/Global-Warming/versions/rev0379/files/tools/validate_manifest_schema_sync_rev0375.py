#!/usr/bin/env python3
from __future__ import annotations
import hashlib, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def digest(rel): return hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
problems=[]
for name in ['manifest.json','schema.json','validation-rules.json']:
    root=name; cube='cube/'+name
    if not (ROOT/root).exists(): problems.append('missing_'+root)
    if not (ROOT/cube).exists(): problems.append('missing_'+cube)
    if (ROOT/root).exists() and (ROOT/cube).exists() and digest(root)!=digest(cube): problems.append('mismatch_'+name)
text=(ROOT/'manifest.json').read_text(encoding='utf-8')
if 'rev0375' not in text or '582-nuclear' not in text: problems.append('manifest_not_rev0375')
if problems:
    print('FAIL manifest_schema_sync_rev0375 '+ '; '.join(problems)); sys.exit(1)
print('PASS manifest_schema_sync_rev0375 root_cube_json_synced')
