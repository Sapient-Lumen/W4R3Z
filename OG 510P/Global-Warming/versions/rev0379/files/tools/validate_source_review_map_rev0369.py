#!/usr/bin/env python3
from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
reviews=list(csv.DictReader((ROOT/'cube/source-review-event-rev0369.csv').open(newline='', encoding='utf-8')))
map_rows=list(csv.DictReader((ROOT/'cube/source-canonical-url-map-rev0369.csv').open(newline='', encoding='utf-8')))
clusters=list(csv.DictReader((ROOT/'cube/source-canonical-cluster-summary-rev0369.csv').open(newline='', encoding='utf-8')))
ids={r['source_id'] for r in map_rows}; cids={r['canonical_cluster_id'] for r in clusters}
errors=[]
for r in reviews:
    if r['source_id'] not in ids: errors.append('review_source_missing_from_map:'+r['source_id'])
    if r['canonical_cluster_id'] not in cids: errors.append('review_cluster_missing:'+r['canonical_cluster_id'])
    if 'readiness' in r.get('use_in_rev0369','').lower() and 'not' not in r.get('use_in_rev0369','').lower(): errors.append('bad_use_policy:'+r['source_id'])
for sid in ['S1359','S1365','S1366','S1367','S1368','S1369','S1370']:
    if sid not in ids: errors.append('missing_expected_source:'+sid)
if errors:
    print('FAIL source_review_map_rev0369 ' + ';'.join(errors[:50])); sys.exit(1)
print(f'PASS source_review_map_rev0369 reviews={len(reviews)} map_rows={len(map_rows)} clusters={len(clusters)}')
