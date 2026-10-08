#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
problems=[]
for name in ['manifest.json','schema.json','validation-rules.json']:
    root=json.loads((ROOT/name).read_text(encoding='utf-8'))
    cube=json.loads((ROOT/'cube'/name).read_text(encoding='utf-8'))
    if root!=cube: problems.append(name+'_root_cube_mismatch')
    if root.get('revision')!='rev0373': problems.append(name+'_revision_not_rev0373')
front=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8')).get('front_door_canon')
if front!='580-nuclear-emergency-preparedness-meetingwatch-sourcegraph-activesurface-refactor-compact-canon.md': problems.append('front_door_mismatch')
claim=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8')).get('claim_state','').lower()
for phrase in ['claim-frozen','no local readiness conclusion','public-meeting-watch-open','source-graph-synced']:
    if phrase not in claim: problems.append('claim_state_missing_'+phrase)
if problems:
    print('FAIL manifest_schema_sync_rev0373 '+ '; '.join(problems)); sys.exit(1)
print('PASS manifest_schema_sync_rev0373 root_cube_json_synced')
