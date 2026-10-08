#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json
from pathlib import Path
from typing import Any
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_HOTSPOT_RECEIPT = ROOT / 'examples' / 'snapshots' / 'archive_report_hotspot_receipt.json'
DEFAULT_SEMANTIC_HANDLE_RECEIPT = ROOT / 'examples' / 'snapshots' / 'archive_report_semantic_handle_receipt.json'
DEFAULT_OUTPUT = ROOT / 'examples' / 'snapshots' / 'archive_report_compaction_candidate_receipt.json'
EXCLUDED_HANDLE_PATHS = {'docs/AGENT_LOG.md','docs/SCHEMA_INVENTORY.md','docs/VALIDATOR_INVENTORY.md','examples/snapshots/archive_report_hotspot_receipt.json','examples/snapshots/archive_report_semantic_handle_receipt.json','examples/snapshots/archive_report_compaction_candidate_receipt.json','examples/snapshots/archive_report_compaction_gap_receipt.json','examples/snapshots/archive_report_compaction_manifest_receipt.json','examples/snapshots/archive_report_compaction_rehearsal_receipt.json','examples/snapshots/archive_report_compaction_stage_receipt.json',
    'examples/snapshots/archive_report_compaction_execution_receipt.json'}
PRIMARY_DOC_PATHS = {'docs/DATA_MANAGEMENT.md','docs/BENCHMARK_PROGRAM.md','docs/BUCKET.md','docs/RESEARCH_AGENDA.md','docs/TRANCHES.md','docs/TRANCHES_SUMMARY.md'}
SEARCH_ROOTS = [ROOT / 'docs' / 'LIBRARY' / 'topics', ROOT / 'examples' / 'snapshots']

def load_json(path: Path) -> Any: return json.loads(path.read_text(encoding='utf-8'))
def _sha256_json(node: Any) -> str: return hashlib.sha256(json.dumps(node, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')).hexdigest()
def _relativize(path: Path) -> str: return path.resolve().relative_to(ROOT).as_posix() if path.resolve().is_relative_to(ROOT) else str(path)

def _load_search_index() -> list[tuple[str,str]]:
    rows=[]
    for root in SEARCH_ROOTS:
        if not root.exists(): continue
        for path in sorted(root.rglob('*')):
            if not path.is_file() or path.suffix not in {'.md','.json'}: continue
            rel=path.relative_to(ROOT).as_posix()
            if rel in EXCLUDED_HANDLE_PATHS: continue
            rows.append((rel,path.read_text(encoding='utf-8',errors='ignore').lower()))
    for rel in sorted(PRIMARY_DOC_PATHS):
        path=ROOT/rel
        if path.exists(): rows.append((rel,path.read_text(encoding='utf-8',errors='ignore').lower()))
    return rows

def _handle_kind(rel:str)->str:
    if rel.startswith('docs/LIBRARY/topics/'): return 'library_topic'
    if rel.startswith('examples/snapshots/'): return 'snapshot'
    return 'doc'

def _find_literal_handles(family:str, search_index, limit:int=3):
    needle=family.lower(); found=[]; seen=set()
    for rel,text in search_index:
        if needle not in text or rel in seen: continue
        seen.add(rel); found.append({'path':rel,'kind':_handle_kind(rel)})
    found.sort(key=lambda r: ({'library_topic':0,'snapshot':1,'doc':2}[r['kind']],r['path']))
    return found[:limit]

def _family_alias_keys(family:str):
    keys=[family]
    if family.endswith('_snapshot'):
        keys.append(family[:-9])
    return keys

def _load_semantic_alias_map(semantic_handle_receipt):
    out={}
    for row in semantic_handle_receipt.get('semantic_aliases',[]):
        h=row.get('matched_handle',{}); path=str(h.get('path','')); kind=str(h.get('kind',_handle_kind(path)))
        if not path: continue
        for key in _family_alias_keys(str(row['family'])):
            out.setdefault(key,[]).append({'path':path,'kind':kind})
    return out

def _combine_handles(family, search_index, alias_map, limit=3):
    found=[]; seen=set(); semantic_alias_count=0
    for handle in alias_map.get(family,[]):
        key=(handle['path'],handle['kind'])
        if key in seen: continue
        seen.add(key); semantic_alias_count += 1; found.append(handle)
    for handle in _find_literal_handles(family, search_index, limit=limit*2):
        key=(handle['path'],handle['kind'])
        if key in seen: continue
        seen.add(key); found.append(handle)
    found.sort(key=lambda r: ({'library_topic':0,'snapshot':1,'doc':2}[r['kind']],r['path']))
    return found[:limit], semantic_alias_count

def _readiness(handles, has_pair):
    kinds={r['kind'] for r in handles}
    if 'library_topic' in kinds and has_pair: return 'citation_ready_pair'
    if 'library_topic' in kinds: return 'citation_ready'
    if 'snapshot' in kinds and has_pair: return 'artifact_backed_pair'
    if 'snapshot' in kinds: return 'artifact_backed'
    return 'doc_backed'

def _rationale(handles, has_pair, semantic_alias_used):
    kinds={r['kind'] for r in handles}; prefix='Existing semantic aliasing shows that this family is already carried by a durable handle, so ' if semantic_alias_used else ''
    if 'library_topic' in kinds and has_pair: return prefix + 'future work can cite the library topic instead of retaining another JSON+MD pair here.'
    if 'library_topic' in kinds: return prefix + 'future work can cite the library topic instead of keeping more report fanout here.'
    if 'snapshot' in kinds and has_pair: return prefix + 'future work can cite retained snapshot artifacts instead of retaining another JSON+MD pair here.'
    if 'snapshot' in kinds: return prefix + 'future work can cite retained snapshot artifacts instead of growing report fanout here.'
    return prefix + 'archive shaping can treat this family as a citation-backed compaction candidate.'

def build_receipt(hotspot_receipt, hotspot_receipt_path, semantic_handle_receipt, semantic_handle_receipt_path):
    search_index=_load_search_index(); alias_map=_load_semantic_alias_map(semantic_handle_receipt); families=hotspot_receipt.get('largest_report_families',[])
    candidates=[]
    for row in families:
        handles, alias_count=_combine_handles(str(row['family']), search_index, alias_map)
        if not handles: continue
        kinds=sorted({h['kind'] for h in handles})
        candidates.append({'family':row['family'],'file_count':row['file_count'],'raw_bytes':row['raw_bytes'],'raw_mebibytes':row['raw_mebibytes'],'share_of_report_bucket_raw_bytes':row['share_of_report_bucket_raw_bytes'],'has_json_md_pair':row['has_json_md_pair'],'backing_handle_count':len(handles),'backing_handle_kinds':kinds,'backing_handles':handles,'semantic_alias_used':alias_count>=1,'semantic_alias_handle_count':alias_count,'compaction_readiness':_readiness(handles,bool(row['has_json_md_pair'])),'rationale':_rationale(handles,bool(row['has_json_md_pair']),alias_count>=1)})
    rank={'citation_ready_pair':0,'citation_ready':1,'artifact_backed_pair':2,'artifact_backed':3,'doc_backed':4}
    candidates.sort(key=lambda r:(rank[r['compaction_readiness']],-r['raw_bytes'],r['family']))
    priority=candidates[:6]; bucket=int(hotspot_receipt.get('report_bucket_totals',{}).get('raw_bytes',0)); raw=sum(int(r['raw_bytes']) for r in priority)
    summary={'priority_candidate_count':len(priority),'priority_candidate_raw_bytes':raw,'priority_candidate_raw_mebibytes':round(raw/(1024*1024),3),'priority_candidate_share_of_report_bucket_raw_bytes':round(raw/bucket,6) if bucket else 0.0,'priority_candidate_pair_count':sum(1 for r in priority if r['has_json_md_pair']),'priority_candidates_with_library_topic_count':sum(1 for r in priority if 'library_topic' in r['backing_handle_kinds']),'priority_candidates_with_snapshot_count':sum(1 for r in priority if 'snapshot' in r['backing_handle_kinds']),'priority_candidates_using_semantic_alias_count':sum(1 for r in priority if r['semantic_alias_used'])}
    hotspot_names={r['family'] for r in families[:10]}
    checks={'hotspot_receipt_ready':bool(hotspot_receipt.get('status_counts',{}).get('ready_to_cite')),'semantic_handle_receipt_ready':bool(semantic_handle_receipt.get('status_counts',{}).get('ready_to_cite')),'priority_candidates_nonempty':bool(priority) or int(hotspot_receipt.get('report_bucket_totals',{}).get('raw_bytes',0)) == 0,'priority_candidates_all_have_backing_handles':all(r['backing_handle_count']>=1 for r in priority),'priority_candidates_are_hotspot_families':all(r['family'] in hotspot_names for r in priority),'priority_candidates_sorted_by_readiness_then_size':priority==sorted(priority,key=lambda r:(rank[r['compaction_readiness']],-r['raw_bytes'],r['family'])),'priority_candidates_need_no_new_library_topics':all(r['backing_handle_count']>=1 for r in priority)}
    passed=sum(1 for v in checks.values() if v); ready=passed==len(checks); top=priority[0] if priority else None
    return {'receipt_kind':'archive_report_compaction_candidate_receipt','receipt_version':'2026-03-17.archive_report_compaction_candidate_receipt.v1','analysis_script':'scripts/tools/build_archive_report_compaction_candidate_receipt.py','hotspot_receipt_path':_relativize(hotspot_receipt_path),'hotspot_receipt_sha256':_sha256_json(hotspot_receipt),'semantic_handle_receipt_path':_relativize(semantic_handle_receipt_path),'semantic_handle_receipt_sha256':_sha256_json(semantic_handle_receipt),'measurement_scope':{'candidate_search_roots':[p.relative_to(ROOT).as_posix() for p in SEARCH_ROOTS],'excluded_handle_paths':sorted(EXCLUDED_HANDLE_PATHS),'primary_doc_paths':sorted(PRIMARY_DOC_PATHS),'max_backing_handles_per_family':3},'summary_metrics':summary,'priority_candidates':priority,'policy_checks':checks,'status_counts':{'passed_check_count':passed,'total_check_count':len(checks),'ready_to_cite':ready},'archive_posture':{'intended_retention_class':'durable_compaction_candidate_receipt','prefer_citation_over_recopy':True,'size_discipline_note':'Carry one tiny compaction-candidate receipt that turns the bulky hotspot table into an evidence-backed first trim list, including families recovered through semantic handle reuse rather than redundant new notes.'},'headline_findings':[f"The first {len(priority)} citation-backed compaction candidates cover {summary['priority_candidate_raw_bytes']} raw bytes of the reports bucket ({summary['priority_candidate_share_of_report_bucket_raw_bytes']} share) without reopening bulky report families by hand." if priority else 'No citation-backed compaction candidates were found among the current report hotspots.',f"The highest-readiness candidate is `{top['family']}` at {top['raw_bytes']} bytes, backed by {top['backing_handle_count']} durable non-report handle(s)." if top else 'No highest-readiness candidate is available.',f"{summary['priority_candidates_using_semantic_alias_count']} of the priority candidates are recovered through semantic handle reuse, so archive shaping can stay citation-first without minting redundant new notes."],'recommended_next_move':('No live citation-backed compaction candidate remains because the current measured report frontier is empty; keep the archive citation-first and avoid reintroducing retained report fanout unless a new durable contract is being added.' if summary['priority_candidate_count'] == 0 else 'When a future session needs to save bytes near the current hotspot surface, cite the listed durable handles first and avoid retaining another report pair for those families unless a genuinely new machine-readable contract is being added.') if ready else 'Do not treat these compaction candidates as stable yet; rebuild the hotspot and semantic-handle receipts and restore durable backing handles before using this receipt to guide archive shaping.'}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--hotspot-receipt',default=str(DEFAULT_HOTSPOT_RECEIPT)); ap.add_argument('--semantic-handle-receipt',default=str(DEFAULT_SEMANTIC_HANDLE_RECEIPT)); ap.add_argument('--output',default=str(DEFAULT_OUTPUT)); ap.add_argument('--strict',action='store_true'); a=ap.parse_args()
    receipt=build_receipt(load_json(Path(a.hotspot_receipt)),Path(a.hotspot_receipt),load_json(Path(a.semantic_handle_receipt)),Path(a.semantic_handle_receipt))
    Path(a.output).write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    return 0 if (not a.strict or receipt['status_counts']['ready_to_cite']) else 1
if __name__=='__main__': raise SystemExit(main())
