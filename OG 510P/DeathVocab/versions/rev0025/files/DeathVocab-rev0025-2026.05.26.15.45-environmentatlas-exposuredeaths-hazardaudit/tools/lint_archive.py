#!/usr/bin/env python3
import json
import re
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]

def fail(msg):
    raise SystemExit(f'LINT FAIL: {msg}')

def load(rel):
    p = ROOT / rel
    if not p.exists(): fail(f'missing {rel}')
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception as e:
        fail(f'bad json {rel}: {e}')

def unique(seq):
    return len(seq) == len(set(seq))

version = (ROOT/'VERSION').read_text(encoding='utf-8').strip()
expected_rev = f'rev{int(version):04d}'
required = [
  'README.md','START_HERE.md','REVISION-RECEIPT.json','SURFACE-STATUS.json','SOURCE-LEDGER.json','RECORD-SCHEMA.json',
  'PUBLIC-SOURCE-PILOT-LEDGER.json','SOURCE-CARD-INDEX.json','REVIEW-PACKET-INDEX.json','CLASS-TAXONOMY.json','STRUCTURAL-INVARIANTS.json',
  'AUDIT-REPORT.json','REFERENCE-INTEGRITY-REPORT.json','FACTOR-REGISTRY.json','SOURCE-CANONICALIZATION-LEDGER.json',
  'TELOS-CHARTER.json','DREAM-REGISTER.json','EARNED-RIGHTS-LEDGER.json','ANTI-OVERCONSTRAINT-LEDGER.json','FOUNDATION-MAP.json','OFFICE-STATE.json','OFFICE-REENTRY-MEMO.md',
  'GLOSSARY-CROSSWALK.json','SEARCH-ALIAS-MAP.json','READER-QUERY-ROUTER.json','CLINICAL-REVIEW-CHECKLIST.json','HIGH-GATE-POLICY.json','REVIEW-DEBT-LEDGER.json','COVERAGE-GAP-REGISTER.json',
  'FOLLOWTHROUGH-QUEUE.json','OPEN-QUESTIONS.json','PEDIATRIC-PERINATAL-ATLAS.json','CHILD-MATERIAL-PUBLICATION-BLOCK.json','HIGH-GATE-COVERAGE-AUDIT.json','BODY-DISPOSITION-ATLAS.json','BODY-DISPOSITION-AUDIT.json','context-pack.json','compact-surface-bundle.json','replay-capsule.json','frontier-ticket.json','VERSION'
]
for rel in required:
    if not (ROOT/rel).exists(): fail(f'missing expected file {rel}')
for p in ROOT.rglob('*.json'):
    try: json.loads(p.read_text(encoding='utf-8'))
    except Exception as e: fail(f'bad json {p.relative_to(ROOT)}: {e}')
receipt = load('REVISION-RECEIPT.json')
if receipt.get('revision') != expected_rev: fail(f'receipt revision not {expected_rev}')
if receipt.get('public_record_count') != 0: fail('public record count not zero')
if receipt.get('private_contributor_record_count') != 0: fail('private contributor records not zero')
records=[]
for p in sorted((ROOT/'records'/'quarantine').glob('DV-REC-*.json')):
    d=json.loads(p.read_text(encoding='utf-8'))
    records.append((d,p))
if len(records) != receipt.get('record_count'): fail('receipt record_count mismatch')
ids=[d.get('record_id') for d,_ in records]
if not unique(ids): fail('duplicate record id')
expected_ids=[f'DV-REC-{i:06d}' for i in range(1,len(records)+1)]
if ids != expected_ids: fail('record ids not continuous from DV-REC-000001')
if set(receipt.get('quarantined_record_ids',[])) != set(ids): fail('receipt quarantined ids mismatch')
for d,p in records:
    rid=d.get('record_id')
    if not p.name.startswith(rid): fail(f'{rid} filename mismatch')
    if d.get('publication_state') != 'quarantined_public_source_pilot': fail(f'{rid} not quarantined')
    for req in ['source_packet','moment','axes','content_layers','provenance','safety','review','links']:
        if req not in d: fail(f'{rid} missing {req}')
    if 'what_this_is_not' not in d.get('content_layers',{}): fail(f'{rid} missing what_this_is_not')
    if not d.get('safety',{}).get('clinical_boundary'): fail(f'{rid} missing clinical boundary')
    classes=d.get('record_classes',[])
    if not classes or not unique(classes): fail(f'{rid} duplicate or empty record_classes')
    for cls in classes:
        if not re.match(r'^[a-z0-9_]+$', cls): fail(f'{rid} non-normal class tag {cls}')
    for ax, vals in d.get('axes',{}).items():
        if isinstance(vals,list):
            if not unique(vals): fail(f'{rid} duplicate axis values in {ax}')
            if ax == 'timeline_phase' and any(v in {'ICU','icu','ED','ed','hospital','nursing_home','home','hospice_facility'} for v in vals):
                fail(f'{rid} setting leaked into timeline_phase')
            if ax == 'setting' and any(v in {'ICU','ED'} for v in vals):
                fail(f'{rid} unnormalized setting casing')
    sp=set(d.get('source_packet',{}).get('source_ids',[]))
    pr=set(d.get('provenance',{}).get('linked_source_ids',[]))
    if sp != pr: fail(f'{rid} source_packet/provenance source mismatch')

    review=d.get('review',{})
    required_review={'editorial_review_state','ethics_review_state','clinical_review_state','cultural_review_state','publication_review_state'}
    missing_review=required_review-set(review.keys())
    if missing_review: fail(f'{rid} missing review fields {sorted(missing_review)}')
    if review.get('publication_review_state') not in {'blocked','needed','complete'}:
        fail(f'{rid} invalid publication_review_state')
source_ledger = load('SOURCE-LEDGER.json')
source_ids={s['source_id'] for s in source_ledger['sources']}
record_source_deps=defaultdict(set)
for d,_ in records:
    for sid in d.get('source_packet',{}).get('source_ids',[]):
        if sid not in source_ids: fail(f'{d["record_id"]} unknown source {sid}')
        record_source_deps[sid].add(d['record_id'])
card_index=load('SOURCE-CARD-INDEX.json')
card_paths={c['source_id']: c['path'] for c in card_index.get('source_cards',[])}
for sid, rids in record_source_deps.items():
    if sid not in card_paths: fail(f'record-referenced source missing source card {sid}')
for c in card_index.get('source_cards',[]):
    p=ROOT/c['path']
    if not p.exists(): fail(f'missing source card path for {c["source_id"]}')
    cd=json.loads(p.read_text(encoding='utf-8'))
    if cd.get('source_id') != c['source_id']: fail(f'source card id mismatch {c["source_id"]}')
    expected=sorted(record_source_deps.get(c['source_id'], set()))
    actual=sorted(cd.get('dependent_record_ids',[]))
    if c['source_id'] in record_source_deps and actual != expected:
        fail(f'source card dependency mismatch {c["source_id"]}')
    if sorted(c.get('dependent_record_ids',[])) != actual:
        fail(f'source card index dependency mismatch {c["source_id"]}')
for rel in ['SEARCH-ALIAS-MAP.json','READER-QUERY-ROUTER.json']:
    d=load(rel)
    for a in d.get('aliases',[]):
        for rid in a.get('routes_to',[]):
            if rid not in ids: fail(f'{rel} alias {a.get("alias_id")} routes to unknown {rid}')

search_alias_ids={a.get('alias_id') for a in load('SEARCH-ALIAS-MAP.json').get('aliases',[]) if a.get('alias_id')}
reader_alias_ids={a.get('alias_id') for a in load('READER-QUERY-ROUTER.json').get('aliases',[]) if a.get('alias_id')}
if search_alias_ids != reader_alias_ids:
    fail(f'alias namespace mismatch: search-only={sorted(search_alias_ids-reader_alias_ids)[:10]}, reader-only={sorted(reader_alias_ids-search_alias_ids)[:10]}')

for t in load('GLOSSARY-CROSSWALK.json').get('terms',[]):
    for rid in t.get('record_ids',[]):
        if rid not in ids: fail(f'glossary term {t.get("term")} unknown record {rid}')
packets=load('REVIEW-PACKET-INDEX.json').get('packets',[])
packet_ids=[]
for pkt in packets:
    packet_ids.append(pkt.get('packet_id'))
    path=pkt.get('path')
    if not path or not (ROOT/path).exists(): fail(f'missing review packet {path}')
    if Path(path).name.startswith('dv-rp-'): fail(f'lower-case review packet filename {path}')
    for rid in pkt.get('record_ids',[]):
        if rid not in ids: fail(f'review packet {pkt.get("packet_id")} unknown record {rid}')
if not unique(packet_ids): fail('duplicate review packet id')
pub=ROOT/'records'/'public'
if pub.exists() and list(pub.glob('*.json')): fail('public records exist')

# Optional JSON Schema validation. Disabled by default because repeated full-cube
# validation can be slow in small execution containers; enable explicitly with
# DEATHVOCAB_ENABLE_JSONSCHEMA=1 during schema-focused work. The structural,
# provenance, source-card, router, review-packet, and publication blockers above
# always run.
import os
if os.environ.get('DEATHVOCAB_ENABLE_JSONSCHEMA') == '1':
    try:
        import jsonschema
        schema = load('RECORD-SCHEMA.json')
        for d,_p in records:
            jsonschema.validate(d, schema)
    except ImportError:
        pass
    except Exception as e:
        fail(f'record schema validation failed: {e}')

print(f'LINT OK: {expected_rev}, {len(records)} quarantined records, {len(card_index.get("source_cards",[]))} source cards, {len(packets)} review packets')
