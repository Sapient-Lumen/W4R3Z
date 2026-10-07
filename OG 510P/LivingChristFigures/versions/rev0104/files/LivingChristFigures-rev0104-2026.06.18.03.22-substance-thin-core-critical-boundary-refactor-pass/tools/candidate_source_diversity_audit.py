#!/usr/bin/env python3
from __future__ import annotations
import argparse, sys
from pathlib import Path
sys.dont_write_bytecode = True
from lib_cube import read_csv_rows, write_csv_json_md_report

FIELDS=['audit_id','candidate_id','candidate_name','check','severity','status','detail','recommendation']
PROMOTED_STATUSES={'promoted_to_candidate'}
INTERNAL_POLICIES={'internal_only_case_extractable','internal_only_contact_rich','internal_only_map_or_route_risk','internal_only_image_sensitive'}

def split(v: str):
    return [x for x in (v or '').split('|') if x]

def run(root: Path):
    candidates={r.get('candidate_id',''): r for r in read_csv_rows(root/'Candidate-Ledger-current.csv')}
    sources={r.get('source_id',''): r for r in read_csv_rows(root/'Source-Registry-current.csv')}
    claims=read_csv_rows(root/'Claim-Ledger-current.csv')
    discovery=[r for r in read_csv_rows(root/'META/Candidate-Discovery-Log-current.csv') if r.get('discovery_status') in PROMOTED_STATUSES]
    claim_sources_by_candidate={}
    boundary_claims_by_candidate={}
    for cr in claims:
        cid=cr.get('candidate_id','')
        claim_sources_by_candidate.setdefault(cid,set()).update(split(cr.get('evidence_source_ids','')))
        if cr.get('claim_type')=='risk_boundary_or_caution' or cr.get('overclaim_risk')=='high' or 'boundary' in (cr.get('claim_status','') or ''):
            boundary_claims_by_candidate.setdefault(cid,0)
            boundary_claims_by_candidate[cid]+=1
    rows=[]
    def add(cid,name,check,severity,status,detail,rec):
        rows.append({'audit_id':f'candidate_source_pack_audit_{len(rows)+1:04d}','candidate_id':cid,'candidate_name':name,'check':check,'severity':severity,'status':status,'detail':detail,'recommendation':rec})
    if not discovery:
        add('','','promoted_discovery_rows_present','high','fail','no promoted discovery rows found','promoted candidates should be discoverable from Candidate-Discovery-Log')
        return rows
    for d in discovery:
        cid=d.get('proposed_candidate_id','')
        cand=candidates.get(cid,{})
        name=cand.get('name') or d.get('candidate_name','')
        declared=split(d.get('source_ids','')) or split(cand.get('source_ids',''))
        registry_rows=[sources.get(sid,{}) for sid in declared if sid in sources]
        domains={r.get('domain','') for r in registry_rows if r.get('domain')}
        types={r.get('source_type','') for r in registry_rows if r.get('source_type')}
        policies={r.get('public_link_policy','') for r in registry_rows if r.get('public_link_policy')}
        harm={r.get('harm_proximity','') for r in registry_rows if r.get('harm_proximity')}
        owners={r.get('source_owner_type','') for r in registry_rows if r.get('source_owner_type')}
        missing=[sid for sid in declared if sid not in sources]
        add(cid,name,'source_ids_resolve','info' if not missing else 'high','pass' if not missing else 'fail',f'declared={len(declared)} missing={len(missing)}'+((' missing: '+ '|'.join(missing[:5])) if missing else ''),'all promoted-candidate source ids must resolve to Source Registry')
        add(cid,name,'minimum_source_count','info' if len(registry_rows)>=3 else 'high','pass' if len(registry_rows)>=3 else 'fail',f'{len(registry_rows)} resolved source row(s)','promoted candidates should carry at least three source rows unless an explicit exception is logged')
        add(cid,name,'domain_diversity','info' if len(domains)>=2 else 'medium','pass' if len(domains)>=2 else 'fail',f'{len(domains)} domain(s): '+ '|'.join(sorted(domains)),'use more than one domain when promoting a candidate, or document why only one exists')
        add(cid,name,'source_type_diversity','info' if len(types)>=2 else 'medium','pass' if len(types)>=2 else 'fail',f'{len(types)} type(s): '+ '|'.join(sorted(types)),'avoid relying on only one source type for promoted candidate office shape')
        add(cid,name,'owner_diversity_visible','info' if owners else 'medium','pass' if owners else 'fail','owner types: '+ '|'.join(sorted(owners)),'source_owner_type should be populated so source power position is visible')
        claim_srcs=claim_sources_by_candidate.get(cid,set())
        unused=sorted(set(declared)-claim_srcs)
        add(cid,name,'declared_sources_used_by_claims','info' if not unused else 'medium','pass' if not unused else 'fail','all declared sources appear in claim evidence' if not unused else 'declared but not claim-used: '+ '|'.join(unused[:8]),'canonical source ids should either support claims or be moved to parked/context rows')
        missing_from_declared=sorted(claim_srcs-set(declared))
        add(cid,name,'claim_sources_declared_by_candidate','info' if not missing_from_declared else 'high','pass' if not missing_from_declared else 'fail','all claim evidence sources declared by candidate' if not missing_from_declared else 'claim-only sources: '+ '|'.join(missing_from_declared[:8]),'claim evidence sources must be in the promoted candidate source pack')
        has_internal=bool(policies & INTERNAL_POLICIES)
        has_boundary_note='public_link_allowed_with_boundary_note' in policies
        add(cid,name,'public_link_policy_diversity','info' if (has_internal or has_boundary_note) else 'high','pass' if (has_internal or has_boundary_note) else 'fail','policies: '+ '|'.join(sorted(policies)),'source pack must carry internal-only or boundary-note URL posture; public URL exposure is not authorized by discovery')
        add(cid,name,'harm_posture_visible','info' if harm else 'high','pass' if harm else 'fail','harm: '+ '|'.join(sorted(harm)),'harm_proximity must be visible for all promoted source packs')
        bcount=boundary_claims_by_candidate.get(cid,0)
        add(cid,name,'boundary_claim_present','info' if bcount>=1 else 'high','pass' if bcount>=1 else 'fail',f'{bcount} boundary/high-risk claim row(s)','promoted candidates need an explicit risk_boundary_or_caution or high-risk release-control claim')
    return rows

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report:
        write_csv_json_md_report(root, 'META/Candidate-Source-Diversity-Audit-current.csv', FIELDS, rows, 'Candidate Source Diversity Audit', 'tools/candidate_source_diversity_audit.py', intro_lines=['Checks promoted discovery candidates for resolvable, diverse, claim-used, boundary-aware source packs. This audit does not authorize public URL release.'])
    for r in rows:
        print(f"{r.get('status','').upper()} {r.get('severity')} {r.get('candidate_id')} {r.get('check')} {r.get('detail')}")
    bad=[r for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    if args.fail_on_high and bad: sys.exit(1)
if __name__=='__main__': main()
