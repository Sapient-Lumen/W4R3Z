#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json
from pathlib import Path
from typing import Any
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_HOTSPOT_RECEIPT = ROOT / 'examples' / 'snapshots' / 'archive_report_hotspot_receipt.json'
DEFAULT_SEMANTIC_HANDLE_RECEIPT = ROOT / 'examples' / 'snapshots' / 'archive_report_semantic_handle_receipt.json'
DEFAULT_CANDIDATE_RECEIPT = ROOT / 'examples' / 'snapshots' / 'archive_report_compaction_candidate_receipt.json'
DEFAULT_OUTPUT = ROOT / 'examples' / 'snapshots' / 'archive_report_compaction_gap_receipt.json'
EXCLUDED_HANDLE_PATHS = {'docs/AGENT_LOG.md','docs/SCHEMA_INVENTORY.md','docs/VALIDATOR_INVENTORY.md','examples/snapshots/archive_report_hotspot_receipt.json','examples/snapshots/archive_report_semantic_handle_receipt.json','examples/snapshots/archive_report_compaction_candidate_receipt.json','examples/snapshots/archive_report_compaction_gap_receipt.json','examples/snapshots/archive_report_compaction_manifest_receipt.json','examples/snapshots/archive_report_compaction_rehearsal_receipt.json','examples/snapshots/archive_report_compaction_stage_receipt.json',
    'examples/snapshots/archive_report_compaction_execution_receipt.json'}
PRIMARY_DOC_PATHS = {'docs/DATA_MANAGEMENT.md','docs/BENCHMARK_PROGRAM.md','docs/BUCKET.md','docs/RESEARCH_AGENDA.md','docs/TRANCHES.md','docs/TRANCHES_SUMMARY.md'}
SEARCH_ROOTS = [ROOT / 'docs' / 'LIBRARY' / 'topics', ROOT / 'examples' / 'snapshots']
TOP_HOTSPOT_LIMIT = 10

def load_json(path: Path) -> Any: return json.loads(path.read_text(encoding='utf-8'))
def _sha256_json(node: Any) -> str: return hashlib.sha256(json.dumps(node, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')).hexdigest()
def _relativize(path: Path) -> str: return path.resolve().relative_to(ROOT).as_posix() if path.resolve().is_relative_to(ROOT) else str(path)

def _load_search_index():
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

def _handle_kind(rel):
    if rel.startswith('docs/LIBRARY/topics/'): return 'library_topic'
    if rel.startswith('examples/snapshots/'): return 'snapshot'
    return 'doc'

def _find_literal_handles(family, search_index, limit=3):
    needle=family.lower(); found=[]; seen=set()
    for rel,text in search_index:
        if needle not in text or rel in seen: continue
        seen.add(rel); found.append({'path':rel,'kind':_handle_kind(rel)})
    found.sort(key=lambda r: ({'library_topic':0,'snapshot':1,'doc':2}[r['kind']],r['path']))
    return found[:limit]

def _load_semantic_alias_map(semantic_handle_receipt):
    out={}
    for row in semantic_handle_receipt.get('semantic_aliases',[]):
        h=row.get('matched_handle',{}); path=str(h.get('path','')); kind=str(h.get('kind',_handle_kind(path)))
        if path: out.setdefault(str(row['family']),[]).append({'path':path,'kind':kind})
    return out

def _combine_handles(family, search_index, alias_map, limit=3):
    found=[]; seen=set()
    for handle in alias_map.get(family,[]):
        key=(handle['path'],handle['kind'])
        if key in seen: continue
        seen.add(key); found.append(handle)
    for handle in _find_literal_handles(family, search_index, limit=limit*2):
        key=(handle['path'],handle['kind'])
        if key in seen: continue
        seen.add(key); found.append(handle)
    found.sort(key=lambda r: ({'library_topic':0,'snapshot':1,'doc':2}[r['kind']],r['path']))
    return found[:limit]

def _recommended_handle_kind(row):
    if bool(row['has_json_md_pair']): return 'library_topic'
    fam=str(row['family'])
    if fam.startswith('rematch_proxy_') or fam.startswith('rematch_world_'): return 'snapshot'
    return 'doc'

def _unlock_move(row, kind):
    if kind=='library_topic': return 'Add one compact library-topic note that states the standing claim for this family, so future archive shaping can cite that note instead of retaining another paired report surface here.'
    if kind=='snapshot': return 'Add one compact retained snapshot or receipt that names this family explicitly, so future sessions can cite a durable artifact rather than reopening the larger report file directly.'
    return 'Add one short durable doc note that names this family explicitly, so future sessions can cite a stable handle instead of carrying more report fanout nearby.'

def build_receipt(hotspot_receipt, hotspot_receipt_path, semantic_handle_receipt, semantic_handle_receipt_path, candidate_receipt, candidate_receipt_path):
    search_index=_load_search_index(); alias_map=_load_semantic_alias_map(semantic_handle_receipt); hotspot=hotspot_receipt.get('largest_report_families',[])[:TOP_HOTSPOT_LIMIT]; blocked=[]
    for row in hotspot:
        if _combine_handles(str(row['family']), search_index, alias_map): continue
        kind=_recommended_handle_kind(row)
        blocked.append({'family':row['family'],'file_count':row['file_count'],'raw_bytes':row['raw_bytes'],'raw_mebibytes':row['raw_mebibytes'],'share_of_report_bucket_raw_bytes':row['share_of_report_bucket_raw_bytes'],'has_json_md_pair':row['has_json_md_pair'],'backing_handle_count':0,'backing_handles':[],'gap_class':'missing_durable_handle','recommended_handle_kind':kind,'unlock_move':_unlock_move(row,kind)})
    blocked.sort(key=lambda r:(-r['raw_bytes'],r['family']))
    bucket=int(hotspot_receipt.get('report_bucket_totals',{}).get('raw_bytes',0)); top_raw=sum(int(r['raw_bytes']) for r in hotspot); blocked_raw=sum(int(r['raw_bytes']) for r in blocked); first_raw=int(candidate_receipt.get('summary_metrics',{}).get('priority_candidate_raw_bytes',0))
    summary={'blocked_hotspot_count':len(blocked),'blocked_hotspot_raw_bytes':blocked_raw,'blocked_hotspot_raw_mebibytes':round(blocked_raw/(1024*1024),3),'blocked_hotspot_pair_count':sum(1 for r in blocked if r['has_json_md_pair']),'blocked_hotspot_share_of_report_bucket_raw_bytes':round(blocked_raw/bucket,6) if bucket else 0.0,'blocked_hotspot_share_of_top_hotspot_raw_bytes':round(blocked_raw/top_raw,6) if top_raw else 0.0,'first_pass_candidate_raw_bytes':first_raw,'combined_first_pass_and_gap_raw_bytes':first_raw+blocked_raw,'combined_first_pass_and_gap_share_of_report_bucket_raw_bytes':round((first_raw+blocked_raw)/bucket,6) if bucket else 0.0}
    names={r['family'] for r in hotspot}; checks={'hotspot_receipt_ready':bool(hotspot_receipt.get('status_counts',{}).get('ready_to_cite')),'semantic_handle_receipt_ready':bool(semantic_handle_receipt.get('status_counts',{}).get('ready_to_cite')),'compaction_candidate_receipt_ready':bool(candidate_receipt.get('status_counts',{}).get('ready_to_cite')),'blocked_hotspots_unique': len({r['family'] for r in blocked}) == len(blocked),'blocked_hotspots_are_current_hotspot_families':all(r['family'] in names for r in blocked),'blocked_hotspots_have_zero_backing_handles':all(r['backing_handle_count']==0 for r in blocked),'blocked_hotspots_sorted_by_size':blocked==sorted(blocked,key=lambda r:(-r['raw_bytes'],r['family'])),'blocked_hotspots_exhaust_true_handle_gaps': {r['family'] for r in blocked} == {str(r['family']) for r in hotspot if not _combine_handles(str(r['family']), search_index, alias_map)}}
    passed=sum(1 for v in checks.values() if v); ready=passed==len(checks); top=blocked[0] if blocked else None
    return {'receipt_kind':'archive_report_compaction_gap_receipt','receipt_version':'2026-03-17.archive_report_compaction_gap_receipt.v1','analysis_script':'scripts/tools/build_archive_report_compaction_gap_receipt.py','hotspot_receipt_path':_relativize(hotspot_receipt_path),'hotspot_receipt_sha256':_sha256_json(hotspot_receipt),'semantic_handle_receipt_path':_relativize(semantic_handle_receipt_path),'semantic_handle_receipt_sha256':_sha256_json(semantic_handle_receipt),'compaction_candidate_receipt_path':_relativize(candidate_receipt_path),'compaction_candidate_receipt_sha256':_sha256_json(candidate_receipt),'measurement_scope':{'candidate_search_roots':[p.relative_to(ROOT).as_posix() for p in SEARCH_ROOTS],'excluded_handle_paths':sorted(EXCLUDED_HANDLE_PATHS),'primary_doc_paths':sorted(PRIMARY_DOC_PATHS),'top_hotspot_limit':TOP_HOTSPOT_LIMIT,'max_backing_handles_per_family':3},'summary_metrics':summary,'blocked_hotspots':blocked,'policy_checks':checks,'status_counts':{'passed_check_count':passed,'total_check_count':len(checks),'ready_to_cite':ready},'archive_posture':{'intended_retention_class':'durable_compaction_gap_receipt','prefer_citation_over_recopy':True,'size_discipline_note':'Carry one tiny handle-gap receipt that shows which large report hotspots still lack any durable non-report handle even after semantic handle reuse, so the next retained addition can unlock later compaction instead of widening report fanout again.'},'headline_findings':[f"After semantic handle reuse, only {len(blocked)} of the current top {TOP_HOTSPOT_LIMIT} report hotspots still lacks any durable non-report handle, leaving {blocked_raw} raw bytes of true second-pass compaction gap ({summary['blocked_hotspot_share_of_report_bucket_raw_bytes']} share of the reports bucket)." if blocked else 'All current top report hotspots already have at least one durable non-report handle once semantic aliasing is taken into account.',f"The remaining true handle gap is `{top['family']}` at {top['raw_bytes']} bytes; one compact `{top['recommended_handle_kind']}` addition would unlock citation-first trimming there." if top else 'No true remaining handle gap is present after semantic-handle reuse; the current top hotspot surface is fully covered by durable non-report handles.',f"Together, the first-pass compaction candidates plus this remaining true gap account for {summary['combined_first_pass_and_gap_raw_bytes']} raw bytes ({summary['combined_first_pass_and_gap_share_of_report_bucket_raw_bytes']} share of the reports bucket), which is the current practical archive-shaping frontier."],'recommended_next_move':('When the archive needs another byte-saving pass after the current citation-backed candidates, mint the smallest durable handle for the remaining blocked hotspot families listed here—starting with the largest row—before retaining any new report fanout nearby.' if blocked else 'No new durable handle is currently needed for the top hotspot surface; reuse the existing candidate and semantic-handle receipts before minting any new note.') if ready else 'Do not use this handle-gap receipt yet; rebuild the hotspot, semantic-handle, and compaction-candidate receipts first, then regenerate the gap receipt on the current tree.'}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--hotspot-receipt',default=str(DEFAULT_HOTSPOT_RECEIPT)); ap.add_argument('--semantic-handle-receipt',default=str(DEFAULT_SEMANTIC_HANDLE_RECEIPT)); ap.add_argument('--candidate-receipt',default=str(DEFAULT_CANDIDATE_RECEIPT)); ap.add_argument('--output',default=str(DEFAULT_OUTPUT)); ap.add_argument('--strict',action='store_true'); a=ap.parse_args()
    receipt=build_receipt(load_json(Path(a.hotspot_receipt)),Path(a.hotspot_receipt),load_json(Path(a.semantic_handle_receipt)),Path(a.semantic_handle_receipt),load_json(Path(a.candidate_receipt)),Path(a.candidate_receipt))
    Path(a.output).write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    return 0 if (not a.strict or receipt['status_counts']['ready_to_cite']) else 1
if __name__=='__main__': raise SystemExit(main())
