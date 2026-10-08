#!/usr/bin/env python3
from __future__ import annotations
import json, pathlib, collections, re
ROOT = pathlib.Path(__file__).resolve().parents[1]
WEAK_RE = re.compile(r'(search\s+locator|search\s+locators|search\s+result|\bsnippet\b|not extracted|not yet|dynamic page source-index)', re.I)

def load(rel: str): return json.loads((ROOT/rel).read_text(encoding='utf-8'))
def main() -> int:
    paths=sorted((ROOT/'records').glob('*/*.json'))
    records=[]; by_id={}; by_type=collections.Counter()
    for p in paths:
        d=json.loads(p.read_text(encoding='utf-8')); records.append((p,d)); by_id[d['id']]=d; by_type[d['record_type']]+=1
    ids=set(by_id); idx=load('records/index.json'); index_ids={r['id'] for r in idx['records']}
    claims=[]; evidence_refs=0; unknown_refs=[]; non_source_refs=[]; legacy_support=[]; weak_claims=[]; missing_evidence=[]; missing_unknown_next=[]
    for p,d in records:
        rid=d['id']
        if d.get('record_type')!='SRC' and (not d.get('unknowns') or not d.get('next_actions')): missing_unknown_next.append(rid)
        if d.get('record_type')=='SRC': continue
        for c in d.get('claims',[]):
            claims.append(c.get('id'))
            if 'source_support' in c: legacy_support.append((rid,c.get('id'),'source_support'))
            refs=c.get('evidence_refs') or []
            if not refs: missing_evidence.append((rid,c.get('id')))
            for ev in refs:
                evidence_refs += 1
                ref=ev.get('ref_id')
                if ref not in ids and ref not in set(claims): unknown_refs.append((rid,c.get('id'),ref))
                if ref and not ref.startswith('MKH-SRC-'): non_source_refs.append((rid,c.get('id'),ref))
                if WEAK_RE.search(str(ev.get('locator',''))+' '+str(ev.get('support_type',''))): weak_claims.append((rid,c.get('id'),ref))
    cl=load('CLAIM-STATUS-LEDGER.json')
    ledger_legacy=sum(1 for e in cl.get('entries',[]) if 'sources_or_support' in e)
    weak_sources=[]; perm=load('SOURCE-PERMANENCE-LEDGER.json'); perm_by_id={e.get('source_id'):e for e in perm.get('entries',[])}; source_support_mismatches=[]
    for p,d in records:
        if d.get('record_type')!='SRC': continue
        sp=d.get('source_payload',{}); locs=sp.get('line_locators_used') or []; notes=' '.join(sp.get('extraction_notes') or [])
        if (not locs) or WEAK_RE.search(' | '.join(map(str,locs))+' '+notes): weak_sources.append(d['id'])
        expected=sp.get('supports_record_ids') or []; observed=(perm_by_id.get(d['id']) or {}).get('record_ids_supported') or []
        if expected != observed: source_support_mismatches.append((d['id'],expected,observed))
    graph=load('GRAPH-EDGES.json')
    red=load('PATTERN-REDTEAM-LEDGER.json')
    vocab=load('SOURCE-VOCABULARY-CONTROL-LEDGER.json')
    print('audit summary')
    print('-------------')
    print('records by type:', dict(sorted(by_type.items())))
    print('records total:', len(records))
    print('claims:', len(claims), 'unique:', len(set(claims)))
    print('claim evidence refs:', evidence_refs)
    print('legacy source_support fields:', len(legacy_support))
    print('legacy claim-ledger sources_or_support entries:', ledger_legacy)
    print('index missing ids:', sorted(ids-index_ids))
    print('index stale ids:', sorted(index_ids-ids))
    print('unknown evidence refs:', len(unknown_refs))
    print('non-source evidence refs:', len(non_source_refs))
    print('weak claim locators:', len(weak_claims))
    print('weak source locators:', len(weak_sources))
    print('weak source ids:', ', '.join(weak_sources[:30]) + (' ...' if len(weak_sources)>30 else ''))
    print('graph edges:', len(graph.get('edges',[])))
    print('pattern red-team entries:', len(red.get('entries',[])))
    print('source vocabulary overlay entries:', len(vocab.get('entries',[])))
    print('source permanence support mismatches:', len(source_support_mismatches))
    print('non-source records missing unknowns/next_actions:', missing_unknown_next)
    critical=sorted(ids-index_ids) or sorted(index_ids-ids) or unknown_refs or legacy_support or ledger_legacy or missing_evidence or source_support_mismatches or missing_unknown_next
    return 1 if critical else 0
if __name__=='__main__': raise SystemExit(main())
