#!/usr/bin/env python3
import json, re
from pathlib import Path
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1]

def fail(msg):
    raise SystemExit('CHECK FAIL: '+msg)
def load(rel):
    try: return json.loads((ROOT/rel).read_text(encoding='utf-8'))
    except Exception as e: fail(f'bad json or missing {rel}: {e}')
# JSON parse all files
for p in ROOT.rglob('*.json'):
    try: json.loads(p.read_text(encoding='utf-8'))
    except Exception as e: fail(f'bad json {p.relative_to(ROOT)}: {e}')
version=(ROOT/'VERSION').read_text(encoding='utf-8').strip()
rev=f'rev{int(version):04d}'
receipt=load('REVISION-RECEIPT.json')
if receipt.get('revision') != rev: fail('revision receipt mismatch')
records=[]
for p in sorted((ROOT/'records'/'quarantine').glob('DV-REC-*.json')):
    records.append((json.loads(p.read_text(encoding='utf-8')),p))
ids=[d.get('record_id') for d,_ in records]
expected=[f'DV-REC-{i:06d}' for i in range(1,len(records)+1)]
if ids != expected: fail('record ids are not continuous')
if len(records) != receipt.get('record_count'): fail('receipt record_count mismatch')
if receipt.get('public_record_count') != 0 or receipt.get('private_contributor_record_count') != 0: fail('receipt public/private counts nonzero')
if len(set(ids)) != len(ids): fail('duplicate record ids')
# Required record fields and publication block
required_review={'editorial_review_state','ethics_review_state','clinical_review_state','cultural_review_state','publication_review_state'}
for d,p in records:
    rid=d['record_id']
    if not p.name.startswith(rid): fail(f'{rid} filename mismatch')
    if d.get('publication_state')!='quarantined_public_source_pilot': fail(f'{rid} publication state not quarantine')
    for req in ['source_packet','moment','axes','content_layers','provenance','safety','review','links']:
        if req not in d: fail(f'{rid} missing {req}')
    if 'what_this_is_not' not in d.get('content_layers',{}): fail(f'{rid} missing what_this_is_not')
    if not d.get('safety',{}).get('clinical_boundary'): fail(f'{rid} missing clinical boundary')
    classes=d.get('record_classes',[])
    if not classes or len(classes)!=len(set(classes)): fail(f'{rid} classes empty or duplicated')
    for cls in classes:
        if not re.match(r'^[a-z0-9_]+$', cls): fail(f'{rid} bad class {cls}')
    axes=d.get('axes',{})
    for ax in ['trajectory','setting','perspective','cultural_tradition_frame','stability','phenomenology','timeline_phase']:
        if not axes.get(ax): fail(f'{rid} missing axis {ax}')
    if 'body_disposition_axis' in classes and not axes.get('body_disposition'): fail(f'{rid} missing body_disposition axis')
    if 'environment_exposure_axis' in classes:
        if not axes.get('environment_exposure'): fail(f'{rid} missing environment_exposure axis')
        ev=d.get('provenance',{}).get('evidence_class',{})
        if not ev.get('environment_exposure_channel'): fail(f'{rid} missing evidence environment_exposure_channel')
        if not d.get('safety',{}).get('environment_exposure_gate'): fail(f'{rid} missing environment_exposure_gate')
        if not d.get('review',{}).get('environment_exposure_review_state'): fail(f'{rid} missing environment exposure review state')
    if 'official_trace_axis' in classes:
        for field in ['official_trace','absence_axis']:
            if not axes.get(field): fail(f'{rid} missing {field}')
        ev=d.get('provenance',{}).get('evidence_class',{})
        for field in ['official_trace_channel','absence_channel']:
            if not ev.get(field): fail(f'{rid} missing evidence {field}')
        if not d.get('review',{}).get('official_trace_review_state'): fail(f'{rid} missing official trace review state')
    if not required_review.issubset(d.get('review',{}).keys()): fail(f'{rid} missing required review fields')
    if d.get('review',{}).get('publication_review_state')!='blocked': fail(f'{rid} not publication-blocked')
    sp=set(d.get('source_packet',{}).get('source_ids',[])); pr=set(d.get('provenance',{}).get('linked_source_ids',[]))
    if sp != pr: fail(f'{rid} source packet/provenance mismatch')
# Source card dependencies
src_ledger=load('SOURCE-LEDGER.json')
src_ids={s['source_id'] for s in src_ledger.get('sources',[])}
deps=defaultdict(set)
for d,_ in records:
    for sid in d.get('source_packet',{}).get('source_ids',[]):
        if sid not in src_ids: fail(f'{d["record_id"]} unknown source {sid}')
        deps[sid].add(d['record_id'])
card_index=load('SOURCE-CARD-INDEX.json')
for card in card_index.get('source_cards',[]):
    p=ROOT/card['path']
    if not p.exists(): fail(f'missing source card {card["path"]}')
    cd=json.loads(p.read_text(encoding='utf-8'))
    expected=sorted(deps.get(card['source_id'],set()))
    if card['source_id'] in deps and sorted(cd.get('dependent_record_ids',[])) != expected:
        fail(f'source card deps mismatch {card["source_id"]}')
    if sorted(card.get('dependent_record_ids',[])) != sorted(cd.get('dependent_record_ids',[])):
        fail(f'source card index deps mismatch {card["source_id"]}')
# Aliases/glossary/review packet references
s_alias=load('SEARCH-ALIAS-MAP.json').get('aliases',[])
r_alias=load('READER-QUERY-ROUTER.json').get('aliases',[])
if {a.get('alias_id') for a in s_alias} != {a.get('alias_id') for a in r_alias}: fail('alias ids mismatch')
for a in s_alias+r_alias:
    for rid in a.get('routes_to',[]):
        if rid not in ids: fail(f'alias routes to unknown {rid}')
packets=load('REVIEW-PACKET-INDEX.json').get('packets',[])
for pkt in packets:
    if not (ROOT/pkt['path']).exists(): fail(f'missing review packet {pkt["path"]}')
    for rid in pkt.get('record_ids',[]):
        if rid not in ids: fail(f'packet routes to unknown {rid}')
for t in load('GLOSSARY-CROSSWALK.json').get('terms',[]):
    for rid in t.get('record_ids',[]):
        if rid not in ids: fail(f'glossary unknown record {rid}')
# Audit report counts
body_count=sum(1 for d,_ in records if 'body_disposition_axis' in d.get('record_classes',[]))
environment_count=sum(1 for d,_ in records if 'environment_exposure_axis' in d.get('record_classes',[]))
official_count=sum(1 for d,_ in records if 'official_trace_axis' in d.get('record_classes',[]))
inst_count=sum(1 for d,_ in records if 'institutional_opacity_axis' in d.get('record_classes',[]))
postvention_count=sum(1 for d,_ in records if 'postvention_axis' in d.get('record_classes',[]))
work_count=sum(1 for d,_ in records if 'worker_distress_axis' in d.get('record_classes',[]))
if load('BODY-DISPOSITION-AUDIT.json')['scope']['body_disposition_axis_records'] != body_count: fail('body audit count mismatch')
if load('ENVIRONMENT-EXPOSURE-AUDIT.json')['scope']['environment_exposure_axis_records'] != environment_count: fail('environment exposure audit count mismatch')
if load('OFFICIAL-TRACE-AUDIT.json')['scope']['official_trace_axis_records'] != official_count: fail('official trace audit count mismatch')
if load('INSTITUTIONAL-OPACITY-AUDIT.json')['scope']['institutional_opacity_axis_records'] != inst_count: fail('institutional audit count mismatch')
if load('POSTVENTION-SAFE-SURFACE-AUDIT.json')['scope']['postvention_axis_records'] != postvention_count: fail('postvention audit count mismatch')
if load('WORKFORCE-AXIS-AUDIT.json')['scope']['worker_distress_axis_records'] != work_count: fail('workforce audit count mismatch')
print(f'CHECK OK: {rev}, {len(records)} quarantined records, {len(card_index.get("source_cards",[]))} source cards, {len(packets)} review packets, body_disposition_axis={body_count}, environment_exposure_axis={environment_count}')
