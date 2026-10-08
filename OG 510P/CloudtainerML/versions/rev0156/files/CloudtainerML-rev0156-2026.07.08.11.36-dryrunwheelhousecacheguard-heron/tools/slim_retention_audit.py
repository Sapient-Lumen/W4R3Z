#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
meta=json.loads((root/'CUBE-META.json').read_text())
report=json.loads((root/'SLIM-RETENTION-REPORT.json').read_text())
rev=meta.get('revision')
required=[
    'artifacts/probe-results/REV0066_SUPPORT_REUSE_AMORTIZATION.json',
    'artifacts/native-inputs/REV0066_SUPPORT_REUSE_AMORTIZATION_INPUT.bin',
    'artifacts/trace-bundles/REV0062_TINY_TRAINED_QK_TRACE_PACKET.npz',
    'PRUNED-ARTIFACTS.jsonl','START_HERE_SLIM.md',
]
missing=[p for p in required if not (root/p).exists()]
assert report['revision'] in ('rev0067', rev)
assert report['source_revision']=='rev0066'
assert report['pruned_file_count']>1000
assert report['summary_files_created']>0
assert not missing, missing
print(json.dumps({'status':'pass','current_revision':rev,'slim_capsule_revision':report['revision'],'source_revision':report['source_revision'],'pruned_file_count':report['pruned_file_count'],'summary_files_created':report['summary_files_created'],'missing_required':missing},indent=2))
