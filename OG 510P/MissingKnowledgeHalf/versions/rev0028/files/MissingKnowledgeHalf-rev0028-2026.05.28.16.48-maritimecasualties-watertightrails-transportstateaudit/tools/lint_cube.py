#!/usr/bin/env python3
from __future__ import annotations
import json, re, sys, hashlib
from pathlib import Path
import jsonschema
ROOT = Path(__file__).resolve().parents[1]
REV='rev0028'
PREV='rev0027'
BUNDLE_RE = r'^MissingKnowledgeHalf\-rev0028\-2026\.05\.28\.16\.48\-maritimecasualties\-watertightrails\-transportstateaudit\.zip$'
EXPECTED_COUNTS = {'CTL': 8, 'ENG': 39, 'GEN': 3, 'INF': 57, 'MET': 11, 'NEG': 13, 'PAT': 21, 'REP': 8, 'SRC': 252}
EXPECTED_NEW = {'MKH-ENG-0043', 'MKH-SRC-0249', 'MKH-SRC-0252', 'MKH-SRC-0250', 'MKH-SRC-0243', 'MKH-SRC-0246', 'MKH-ENG-0042', 'MKH-SRC-0244', 'MKH-SRC-0247', 'MKH-INF-0057', 'MKH-INF-0056', 'MKH-SRC-0251', 'MKH-INF-0054', 'MKH-INF-0055', 'MKH-SRC-0245', 'MKH-CTL-0008', 'MKH-ENG-0041', 'MKH-SRC-0248', 'MKH-ENG-0044', 'MKH-PAT-0023'}
REQUIRED_FILES = ['START_HERE.md', 'README.md', 'REVISION-RECEIPT.json', 'RELEASE-MANIFEST.json', 'SURFACE-STATUS.json', 'context-pack.json', 'MARINE-SAFETY-LEDGER.json', 'MARITIME-FACTOR-AUDIT-LEDGER.json', 'TRANSPORT-STATE-REFACTOR-LEDGER.json', 'FLIGHTDECK-STATE-LEDGER.json', 'HUMAN-FACTORS-FACTOR-AUDIT-LEDGER.json', 'COCKPIT-RESOURCE-MANAGEMENT-RAIL-AUDIT.json', 'ENGINEERING-CAUSAL-GRAIN-AUDIT-LEDGER.json', 'EVIDENCE-REFERENCE-LEDGER.json', 'PATTERN-REDTEAM-LEDGER.json', 'PATTERN-CONTROL-LEDGER.json', 'CONTROL-COVERAGE-MATRIX.json', 'CALIBRATION-CONTROL-LEDGER.json', 'GRAPH-EDGES.json', 'SOURCE-VOCABULARY-CONTROL-LEDGER.json', 'CUBE-AUDIT-LEDGER.json', 'FACTORING-LEDGER.json', 'SCHEMA-DEBT-LEDGER.json', 'LOCATOR-DEBT-LEDGER.json', 'LOCATOR-AUDIT-LEDGER.json', 'REFACTOR-QUEUE.json', 'REVISION-HISTORY-COVERAGE-LEDGER.json', 'CUBE-TOPOLOGY.json', 'records/index.json', 'CLAIM-STATUS-LEDGER.json', 'SOURCE-PERMANENCE-LEDGER.json', 'SOURCE-ACQUISITION-LEDGER.json', 'CANDIDATE-CASE-QUEUE.json', 'FOLLOWTHROUGH-QUEUE.json', 'docs/00-meta/rev0028-conversation-receipt.md', 'docs/10-method/maritime-watertight-stability-and-evacuation-state.md', 'docs/20-schema/maritime-factor-axes.md', 'docs/40-pilot-lanes/marine-casualty-lane-rev0028.md', 'docs/60-synthesis/marine-watertight-state-crosscase-memo-rev0028.md', 'docs/70-audit/transport-state-factor-refactor-rev0028.md', 'schemas/source-record.schema.json', 'schemas/unified-record.schema.json', 'schemas/pattern-record.schema.json', 'schemas/control-record.schema.json', 'schemas/evidence-ref.schema.json', 'schemas/graph-edge-ledger.schema.json', 'tools/audit_cube.py', 'tools/package_release.py', 'FILE-MANIFEST.json']
SCHEMA_BY_TYPE = {'CTL':'schemas/control-record.schema.json','ENG':'schemas/engineering-incident-record.schema.json','GEN':'schemas/genealogy-record.schema.json','INF':'schemas/infrastructure-record.schema.json','MET':'schemas/metaresearch-audit-record.schema.json','NEG':'schemas/negative-result-record.schema.json','PAT':'schemas/pattern-record.schema.json','REP':'schemas/replication-program-record.schema.json','SRC':'schemas/source-record.schema.json'}
WEAK_RE = re.compile(r'(search\s+locator|search\s+locators|search\s+result|\bsnippet\b|not extracted|not yet|dynamic page source-index)', re.I)
def fail(msg): print(f'lint fail: {msg}', file=sys.stderr); sys.exit(1)
def load(rel):
    p=ROOT/rel
    if not p.exists(): fail(f'missing {rel}')
    return json.loads(p.read_text(encoding='utf-8'))
for rel in REQUIRED_FILES:
    if not (ROOT/rel).exists(): fail(f'missing required file {rel}')
receipt=load('REVISION-RECEIPT.json'); manifest=load('RELEASE-MANIFEST.json'); surface=load('SURFACE-STATUS.json'); index=load('records/index.json')
for obj,name in [(receipt,'receipt'),(manifest,'manifest'),(surface,'surface'),(index,'index')]:
    if obj.get('revision') != REV: fail(f'{name} revision mismatch')
if receipt.get('previous_revision') != PREV or manifest.get('previous_revision') != PREV or surface.get('previous_revision') != PREV: fail('previous revision mismatch')
if not re.match(BUNDLE_RE, manifest.get('bundle','')): fail('bundle name mismatch')
if set(manifest.get('new_records',[])) != EXPECTED_NEW: fail('new_records set mismatch')
records=index.get('records',[]); ids=[r['id'] for r in records]
if len(ids) != len(set(ids)): fail('duplicate ids in index')
counts={}; record_by_id={}
for r in records:
    counts[r['record_type']]=counts.get(r['record_type'],0)+1
    p=ROOT/r['path']
    if not p.exists(): fail(f'index path missing {r["path"]}')
    d=json.loads(p.read_text(encoding='utf-8'))
    if d.get('id') != r['id'] or d.get('record_type') != r['record_type']: fail(f'index mismatch for {r["id"]}')
    record_by_id[r['id']] = d
for k,v in EXPECTED_COUNTS.items():
    if counts.get(k) != v: fail(f'count mismatch {k}: got {counts.get(k)} expected {v}')
unified_validator=jsonschema.Draft202012Validator(load('schemas/unified-record.schema.json'))
validators={rt:jsonschema.Draft202012Validator(load(path)) for rt,path in SCHEMA_BY_TYPE.items()}
for rid,d in record_by_id.items():
    errs=list(unified_validator.iter_errors(d))
    if errs: fail(f'unified schema error {rid}: {errs[0].message}')
    validator=validators.get(d.get('record_type'))
    if validator:
        errs=list(validator.iter_errors(d))
        if errs: fail(f'{d.get("record_type")} schema error {rid}: {errs[0].message}')
claim_ids=[]; evidence_ref_count=0; non_source_evidence=0; unknown=[]; weak_claims=[]
for rid,d in record_by_id.items():
    if d.get('record_type')!='SRC' and not d.get('sources'): fail(f'non-source record missing sources: {rid}')
    if d.get('record_type')!='SRC':
        if not d.get('unknowns'): fail(f'non-source record missing unknowns: {rid}')
        if not d.get('next_actions'): fail(f'non-source record missing next_actions: {rid}')
    for s in d.get('sources',[]):
        if s not in record_by_id: fail(f'{rid} references unknown source/record {s}')
    if d.get('record_type') == 'INF':
        tp=d.get('type_payload',{})
        for field in ['infrastructure_class','signal_capture_model','outputs','limitations']:
            if field not in tp: fail(f'{rid} INF missing {field}')
    if d.get('record_type') == 'CTL':
        tp=d.get('type_payload',{})
        for field in ['control_class','calibrates_patterns','fit_rationale','limits']:
            if field not in tp: fail(f'{rid} CTL missing {field}')
    if d.get('record_type') == 'PAT':
        if 'candidate' not in d.get('status','') and 'not_mature' not in d.get('status','') and 'not_theory' not in d.get('status',''): fail(f'pattern not marked candidate: {rid}')
        rtc=d.get('type_payload',{}).get('red_team_controls')
        if not rtc: fail(f'pattern missing red_team_controls: {rid}')
        for f in ['positive_controls_needed','negative_controls_needed','counterexamples_to_seek','rollback_triggers','maturity_gate']:
            if not rtc.get(f): fail(f'{rid} red_team_controls missing {f}')
    if d.get('record_type') != 'SRC':
        for c in d.get('claims',[]):
            cid=c.get('id'); claim_ids.append(cid)
            if 'source_support' in c: fail(f'legacy source_support present {rid}/{cid}')
            refs=c.get('evidence_refs') or []
            if not refs: fail(f'claim missing evidence_refs {rid}/{cid}')
            for ev in refs:
                evidence_ref_count += 1
                ref=ev.get('ref_id')
                if not ref: fail(f'evidence_ref missing ref_id {rid}/{cid}')
                if ref not in record_by_id and not ref.startswith('MKH-CLA-'): unknown.append((rid,cid,ref))
                if not ev.get('ref_kind') or not ev.get('support_role') or not ev.get('confidence'): fail(f'incomplete evidence_ref {rid}/{cid}')
                if ref and not ref.startswith('MKH-SRC-'): non_source_evidence += 1
                if WEAK_RE.search(str(ev.get('locator',''))+' '+str(ev.get('support_type',''))): weak_claims.append((rid,cid,ref))
if unknown: fail(f'unknown evidence refs: {unknown[:3]}')
cl=load('CLAIM-STATUS-LEDGER.json')
if cl.get('revision') != REV: fail('claim ledger revision mismatch')
ledger_claims={}
for e in cl.get('entries',[]):
    if 'sources_or_support' in e: fail(f'legacy sources_or_support in claim ledger {e.get("claim_id")}')
    if not e.get('evidence_refs'): fail(f'claim ledger missing evidence_refs {e.get("claim_id")}')
    cid=e.get('claim_id'); ledger_claims[cid]=e
    if e.get('record_id') not in record_by_id: fail(f'claim {cid} references unknown record {e.get("record_id")}')
if len(claim_ids) != len(set(claim_ids)): fail('duplicate record claim ids')
if len(ledger_claims) != len(claim_ids): fail(f'claim ledger count mismatch: {len(ledger_claims)} / {len(claim_ids)}')
for cid in claim_ids:
    if cid not in ledger_claims: fail(f'record claim {cid} missing from ledger')
eref=load('EVIDENCE-REFERENCE-LEDGER.json')
if eref.get('revision') != REV: fail('evidence ref ledger revision mismatch')
if eref['migration_summary']['claim_count'] != len(claim_ids): fail('evidence claim count mismatch')
if eref['migration_summary']['evidence_ref_count'] != evidence_ref_count: fail('evidence ref count mismatch')
if eref['migration_summary']['non_source_evidence_ref_count'] != non_source_evidence: fail('non-source evidence ref count mismatch')
red=load('PATTERN-REDTEAM-LEDGER.json')
if red.get('revision') != REV or len(red.get('entries',[])) != EXPECTED_COUNTS['PAT']: fail('pattern redteam ledger mismatch')
cm=load('CONTROL-COVERAGE-MATRIX.json')
if cm.get('revision') != REV or len(cm.get('entries',[])) != EXPECTED_COUNTS['PAT']: fail('control coverage matrix mismatch')
if cm.get('summary_metrics',{}).get('patterns_allowed_to_mature') != 0: fail('control matrix allows maturity unexpectedly')
ctl=load('CALIBRATION-CONTROL-LEDGER.json')
ctl_ids={e.get('control_id') for e in ctl.get('entries',[])}
expected_ctl_ids={rid for rid,d in record_by_id.items() if d.get('record_type')=='CTL'}
if ctl.get('revision') != REV or ctl_ids != expected_ctl_ids: fail('calibration control ledger mismatch')
graph=load('GRAPH-EDGES.json')
jsonschema.Draft202012Validator(load('schemas/graph-edge-ledger.schema.json')).validate(graph)
if graph.get('revision') != REV or len(graph.get('edges',[])) < 800: fail('graph edge ledger too thin')
for edge in graph.get('edges',[]):
    if edge['from_id'] not in record_by_id and not edge['from_id'].startswith('MKH-CLA-'): fail(f'graph edge unknown from {edge}')
    if edge['to_id'] not in record_by_id and not edge['to_id'].startswith('MKH-CLA-'): fail(f'graph edge unknown to {edge}')
vocab=load('SOURCE-VOCABULARY-CONTROL-LEDGER.json')
if vocab.get('revision') != REV or len(vocab.get('entries',[])) != EXPECTED_COUNTS['SRC']: fail('source vocabulary ledger mismatch')
perm=load('SOURCE-PERMANENCE-LEDGER.json'); perm_by_id={e.get('source_id'):e for e in perm.get('entries',[])}
for sid,d in record_by_id.items():
    if d.get('record_type')=='SRC':
        if sid not in perm_by_id: fail(f'source permanence missing {sid}')
        expected=d.get('source_payload',{}).get('supports_record_ids') or []
        observed=perm_by_id[sid].get('record_ids_supported') or []
        if expected != observed: fail(f'source permanence support mismatch {sid}')
loc=load('LOCATOR-AUDIT-LEDGER.json')
if loc.get('revision') != REV: fail('locator audit revision mismatch')
if loc.get('metrics',{}).get('weak_claim_ref_count') != len(weak_claims): fail('weak claim locator metric mismatch')
metrics=load('CUBE-AUDIT-LEDGER.json')['metrics']
if metrics['claims_total'] != len(claim_ids) or metrics['claim_evidence_ref_count'] != evidence_ref_count or metrics['graph_edge_count'] != len(graph.get('edges',[])): fail('audit metrics mismatch')
for n in [f'{i:04d}' for i in range(1,29)]:
    if not (ROOT/f'docs/00-meta/rev{n}-conversation-receipt.md').exists(): fail(f'missing rev{n} receipt')
ctx=load('context-pack.json')
if ctx.get('revision') != REV or ('marine' not in ctx.get('one_line','') and 'maritime' not in ctx.get('one_line','')): fail('context pack invalid/stale')
fm=load('FILE-MANIFEST.json')
if fm.get('revision') != REV: fail('file manifest revision mismatch')
paths={e['path'] for e in fm.get('files',[])}
for rel in REQUIRED_FILES:
    if rel not in paths: fail(f'file manifest missing {rel}')
for e in fm.get('files',[]):
    p=ROOT/e['path']
    if not p.exists(): fail(f'file listed missing {e["path"]}')
    if e['path']=='FILE-MANIFEST.json': continue
    if hashlib.sha256(p.read_bytes()).hexdigest() != e.get('sha256'): fail(f'hash mismatch {e["path"]}')
print(f'lint ok: MissingKnowledgeHalf {REV} with {EXPECTED_COUNTS}; {len(claim_ids)} claims, {evidence_ref_count} evidence_refs, {non_source_evidence} non-source evidence refs, {len(graph.get("edges",[]))} graph edges, locator weak source count {loc["metrics"]["weak_source_locator_count"]}')
