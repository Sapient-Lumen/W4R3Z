\
#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True
from lib_cube import write_csv_json_md_report

FIELDS=['relationship_id','relationship_family','source_surface','source_id','source_field','referenced_surface','referenced_id','expected_state','observed_state','severity','status','note']

def read_csv_rows(path: Path):
    if not path.exists(): return []
    with path.open(encoding='utf-8', newline='') as f: return list(csv.DictReader(f))

def split_pipe(value: str):
    return [x for x in (value or '').split('|') if x]

def add(rows, family, source_surface, source_id, source_field, referenced_surface, referenced_id, expected, observed, severity, status, note):
    rows.append({
        'relationship_id': f'ledger_rel_{len(rows)+1:05d}',
        'relationship_family': family,
        'source_surface': source_surface,
        'source_id': source_id,
        'source_field': source_field,
        'referenced_surface': referenced_surface,
        'referenced_id': referenced_id,
        'expected_state': expected,
        'observed_state': observed,
        'severity': severity,
        'status': status,
        'note': note,
    })

def has_file(root: Path, rel: str) -> bool:
    return bool(rel) and (root/rel).exists()

def index(rows, key):
    return {r.get(key,''): r for r in rows if r.get(key,'')}

def add_id_uniqueness(rows, surface, key, records):
    values=[r.get(key,'') for r in records]
    blank=sum(1 for v in values if not v)
    dup=[v for v,c in Counter(values).items() if v and c>1]
    add(rows,'identifier_uniqueness',surface,'.',key,surface,key,'nonblank unique identifiers',f'rows={len(records)} blank={blank} dup={len(dup)}','high' if blank or dup else 'info','fail' if blank or dup else 'pass', ('blank or duplicate ids: '+ '; '.join(dup[:8])) if blank or dup else 'identifier column is nonblank and unique')

def add_exact_coverage(rows, family, surface, field, observed_ids, target_surface, target_ids, note):
    missing=sorted(set(target_ids)-set(observed_ids))
    extra=sorted(set(observed_ids)-set(target_ids))
    ok=not missing and not extra
    add(rows,family,surface,'.',field,target_surface,'.','exact coverage',f'missing={len(missing)} extra={len(extra)}','high' if not ok else 'info','pass' if ok else 'fail', note if ok else f'missing: {"; ".join(missing[:8])}; extra: {"; ".join(extra[:8])}')

def check_ref(rows, family, source_surface, source_id, source_field, referenced_surface, referenced_id, exists, note, severity='high'):
    add(rows,family,source_surface,source_id,source_field,referenced_surface,referenced_id,'referenced id/path exists','present' if exists else 'missing', 'info' if exists else severity, 'pass' if exists else 'fail', note)

def run(root: Path):
    rows=[]
    cand=read_csv_rows(root/'Candidate-Ledger-current.csv')
    claims=read_csv_rows(root/'Claim-Ledger-current.csv')
    sources=read_csv_rows(root/'Source-Registry-current.csv')
    offices=read_csv_rows(root/'Office-Card-Index-current.csv')
    debt=read_csv_rows(root/'Evidence-Debt-current.csv')
    refresh=read_csv_rows(root/'Refresh-Index-current.csv')
    perm=read_csv_rows(root/'GOVERNANCE/Permission-State-Ledger-current.csv')
    public_elig=read_csv_rows(root/'META/Public-Export-Eligibility-current.csv')
    gov_snap=read_csv_rows(root/'META/Candidate-Governance-Snapshot-current.csv')
    claim_strength=read_csv_rows(root/'META/Claim-Evidence-Strength-current.csv')
    claim_quar=read_csv_rows(root/'META/Public-Claim-Quarantine-current.csv')
    claim_release=read_csv_rows(root/'META/Public-Claim-Release-Ledger-current.csv')
    source_matrix=read_csv_rows(root/'META/Claim-Source-Boundary-Matrix-current.csv')
    discovery=read_csv_rows(root/'META/Candidate-Discovery-Log-current.csv')
    overlay=read_csv_rows(root/'META/Normalized-Code-Overlay-current.csv')

    cand_by=index(cand,'candidate_id'); claim_by=index(claims,'claim_id'); source_by=index(sources,'source_id'); office_by=index(offices,'office_id'); refresh_by=index(refresh,'refresh_id')
    perm_by_candidate={r.get('candidate_id',''):r for r in perm if r.get('candidate_id')}
    quarantine_by=index(claim_quar,'quarantine_id')

    for surface,key,records in [
        ('Candidate-Ledger-current.csv','candidate_id',cand),('Claim-Ledger-current.csv','claim_id',claims),('Source-Registry-current.csv','source_id',sources),('Office-Card-Index-current.csv','office_id',offices),('Refresh-Index-current.csv','refresh_id',refresh),('GOVERNANCE/Permission-State-Ledger-current.csv','permission_state_id',perm),('META/Public-Claim-Quarantine-current.csv','quarantine_id',claim_quar),('META/Public-Claim-Release-Ledger-current.csv','release_id',claim_release),('META/Normalized-Code-Overlay-current.csv','overlay_id',overlay)]:
        add_id_uniqueness(rows,surface,key,records)

    # Candidate file/office/source relationships.
    for r in cand:
        cid=r.get('candidate_id','')
        check_ref(rows,'candidate_file_path','Candidate-Ledger-current.csv',cid,'file_path',r.get('file_path',''),r.get('file_path',''),has_file(root,r.get('file_path','')),'candidate ledger file_path resolves to an actual candidate file')
        for oid in split_pipe(r.get('office_ids','')):
            check_ref(rows,'candidate_office_join','Candidate-Ledger-current.csv',cid,'office_ids','Office-Card-Index-current.csv',oid,oid in office_by,'candidate office_ids must resolve to Office-Card-Index')
        for sid in split_pipe(r.get('source_ids','')):
            check_ref(rows,'candidate_source_join','Candidate-Ledger-current.csv',cid,'source_ids','Source-Registry-current.csv',sid,sid in source_by,'candidate source_ids must resolve to Source-Registry')

    # Claim joins.
    for r in claims:
        cid=r.get('candidate_id',''); clid=r.get('claim_id','')
        check_ref(rows,'claim_candidate_join','Claim-Ledger-current.csv',clid,'candidate_id','Candidate-Ledger-current.csv',cid,cid in cand_by,'claim candidate_id must resolve to Candidate-Ledger')
        if cid in cand_by:
            ok=r.get('candidate_name','')==cand_by[cid].get('name','')
            add(rows,'claim_candidate_name_sync','Claim-Ledger-current.csv',clid,'candidate_name','Candidate-Ledger-current.csv',cid,'candidate_name equals Candidate-Ledger name','match' if ok else 'mismatch','info' if ok else 'high','pass' if ok else 'fail','claim display name must not drift from candidate ledger')
        for sid in split_pipe(r.get('evidence_source_ids','')):
            check_ref(rows,'claim_source_join','Claim-Ledger-current.csv',clid,'evidence_source_ids','Source-Registry-current.csv',sid,sid in source_by,'claim evidence_source_ids must resolve to Source-Registry')

    # Source joins.
    for r in sources:
        sid=r.get('source_id','')
        for cid in split_pipe(r.get('candidate_ids','')):
            check_ref(rows,'source_candidate_join','Source-Registry-current.csv',sid,'candidate_ids','Candidate-Ledger-current.csv',cid,cid in cand_by,'source candidate_ids must resolve to Candidate-Ledger')
        for rid in split_pipe(r.get('refresh_ids','')):
            check_ref(rows,'source_refresh_join','Source-Registry-current.csv',sid,'refresh_ids','Refresh-Index-current.csv',rid,rid in refresh_by,'source refresh_ids must resolve to Refresh-Index')
        for rel in split_pipe(r.get('seen_in_files','')):
            check_ref(rows,'source_seen_in_file_path','Source-Registry-current.csv',sid,'seen_in_files',rel,rel,has_file(root,rel),'source seen_in_files paths must resolve to package files')

    # Evidence debt / refresh / governance/public exact candidate coverage.
    for r in debt:
        cid=r.get('candidate_id','')
        check_ref(rows,'evidence_debt_candidate_join','Evidence-Debt-current.csv',r.get('debt_id',''),'candidate_id','Candidate-Ledger-current.csv',cid,cid in cand_by,'evidence debt candidate_id must resolve')
    for r in refresh:
        rid=r.get('refresh_id','')
        check_ref(rows,'refresh_file_path','Refresh-Index-current.csv',rid,'file_path',r.get('file_path',''),r.get('file_path',''),has_file(root,r.get('file_path','')),'refresh-index file_path resolves to a refresh note')
        for cid in split_pipe(r.get('related_candidate_ids','')):
            check_ref(rows,'refresh_candidate_join','Refresh-Index-current.csv',rid,'related_candidate_ids','Candidate-Ledger-current.csv',cid,cid in cand_by,'refresh related_candidate_ids must resolve to Candidate-Ledger')
    cand_ids=set(cand_by)
    add_exact_coverage(rows,'permission_candidate_coverage','GOVERNANCE/Permission-State-Ledger-current.csv','candidate_id',{r.get('candidate_id','') for r in perm},'Candidate-Ledger-current.csv',cand_ids,'permission ledger covers exactly every candidate')
    add_exact_coverage(rows,'public_eligibility_candidate_coverage','META/Public-Export-Eligibility-current.csv','candidate_id',{r.get('candidate_id','') for r in public_elig},'Candidate-Ledger-current.csv',cand_ids,'public eligibility covers exactly every candidate')
    add_exact_coverage(rows,'governance_snapshot_candidate_coverage','META/Candidate-Governance-Snapshot-current.csv','candidate_id',{r.get('candidate_id','') for r in gov_snap},'Candidate-Ledger-current.csv',cand_ids,'governance snapshot covers exactly every candidate')
    add_exact_coverage(rows,'claim_strength_claim_coverage','META/Claim-Evidence-Strength-current.csv','claim_id',{r.get('claim_id','') for r in claim_strength},'Claim-Ledger-current.csv',set(claim_by),'claim evidence strength covers exactly every claim')

    # Claim quarantine/release and matrix relationships.
    for r in claim_quar:
        qid=r.get('quarantine_id',''); clid=r.get('claim_id',''); cid=r.get('candidate_id','')
        check_ref(rows,'claim_quarantine_claim_join','META/Public-Claim-Quarantine-current.csv',qid,'claim_id','Claim-Ledger-current.csv',clid,clid in claim_by,'quarantine claim_id must resolve')
        check_ref(rows,'claim_quarantine_candidate_join','META/Public-Claim-Quarantine-current.csv',qid,'candidate_id','Candidate-Ledger-current.csv',cid,cid in cand_by,'quarantine candidate_id must resolve')
    for r in claim_release:
        rid=r.get('release_id',''); clid=r.get('claim_id',''); cid=r.get('candidate_id',''); qid=r.get('released_from_quarantine_id','')
        check_ref(rows,'claim_release_claim_join','META/Public-Claim-Release-Ledger-current.csv',rid,'claim_id','Claim-Ledger-current.csv',clid,clid in claim_by,'release claim_id must resolve')
        check_ref(rows,'claim_release_candidate_join','META/Public-Claim-Release-Ledger-current.csv',rid,'candidate_id','Candidate-Ledger-current.csv',cid,cid in cand_by,'release candidate_id must resolve')
        for sid in split_pipe(r.get('source_registry_ids','')):
            check_ref(rows,'claim_release_source_join','META/Public-Claim-Release-Ledger-current.csv',rid,'source_registry_ids','Source-Registry-current.csv',sid,sid in source_by,'release source_registry_ids must resolve')
        if qid.startswith('qclaim_'):
            qr=quarantine_by.get(qid)
            ok=bool(qr) and qr.get('claim_id')==clid and qr.get('candidate_id')==cid
            add(rows,'claim_release_quarantine_pointer','META/Public-Claim-Release-Ledger-current.csv',rid,'released_from_quarantine_id','META/Public-Claim-Quarantine-current.csv',qid,'current qclaim id must resolve to same claim/candidate, or use historical_* pointer','match' if ok else ('missing' if not qr else f"mismatch current_claim={qr.get('claim_id')}") ,'info' if ok else 'high','pass' if ok else 'fail','prevents a released claim from pointing at an unrelated current quarantine row')
        else:
            ok=bool(qid) and qid.startswith('historical_')
            add(rows,'claim_release_quarantine_pointer','META/Public-Claim-Release-Ledger-current.csv',rid,'released_from_quarantine_id','historical_release_pointer',qid,'non-current release pointer must be explicit historical_*','historical' if ok else 'blank_or_unclassified','info' if ok else 'high','pass' if ok else 'fail','released claims may keep a historical pointer, but must not masquerade as a current qclaim row')
    for r in source_matrix:
        mid=r.get('matrix_id',''); clid=r.get('claim_id',''); sid=r.get('source_id',''); cid=r.get('candidate_id','')
        check_ref(rows,'claim_source_matrix_claim_join','META/Claim-Source-Boundary-Matrix-current.csv',mid,'claim_id','Claim-Ledger-current.csv',clid,clid in claim_by,'claim-source matrix claim_id must resolve')
        check_ref(rows,'claim_source_matrix_source_join','META/Claim-Source-Boundary-Matrix-current.csv',mid,'source_id','Source-Registry-current.csv',sid,sid in source_by,'claim-source matrix source_id must resolve')
        check_ref(rows,'claim_source_matrix_candidate_join','META/Claim-Source-Boundary-Matrix-current.csv',mid,'candidate_id','Candidate-Ledger-current.csv',cid,cid in cand_by,'claim-source matrix candidate_id must resolve')

    # Discovery log relationships.
    for r in discovery:
        did=r.get('discovery_id','')
        cid=r.get('proposed_candidate_id','')
        if r.get('discovery_status')=='promoted_to_candidate' and cid:
            check_ref(rows,'discovery_promoted_candidate_join','META/Candidate-Discovery-Log-current.csv',did,'proposed_candidate_id','Candidate-Ledger-current.csv',cid,cid in cand_by,'promoted discovery candidate must resolve')
        for sid in split_pipe(r.get('source_ids','')):
            check_ref(rows,'discovery_source_join','META/Candidate-Discovery-Log-current.csv',did,'source_ids','Source-Registry-current.csv',sid,sid in source_by,'discovery source_ids must resolve when recorded')

    # Normalized-code overlay targets, using target_id_field rather than assuming surface primary key.
    surface_indexes={
        'Candidate-Ledger-current.csv': {'candidate_id': set(cand_by)},
        'Claim-Ledger-current.csv': {'claim_id': set(claim_by), 'candidate_id': set(cand_by)},
        'Source-Registry-current.csv': {'source_id': set(source_by), 'candidate_id': set(cand_by)},
        'GOVERNANCE/Permission-State-Ledger-current.csv': {'permission_state_id': {r.get('permission_state_id','') for r in perm}, 'candidate_id': {r.get('candidate_id','') for r in perm}},
        'META/Public-Export-Eligibility-current.csv': {'candidate_id': {r.get('candidate_id','') for r in public_elig}},
    }
    for r in overlay:
        surf=r.get('target_surface',''); field=r.get('target_id_field',''); tid=r.get('target_id','')
        valid=tid in surface_indexes.get(surf,{}).get(field,set())
        check_ref(rows,'normalized_overlay_target_join','META/Normalized-Code-Overlay-current.csv',r.get('overlay_id',''),'target_surface/target_id',surf,tid,valid,'normalized-code overlay target_id_field/target_id must resolve to the named target surface')

    high=sum(1 for r in rows if r.get('severity')=='high' and r.get('status')!='pass')
    add(rows,'relationship_audit_summary','META/Ledger-Relationship-Audit-current.csv','.','all audited relationship rows','.','.',f'high_failures=0 total_rows_before_summary={len(rows)}',f'high_failures={high} total_rows_before_summary={len(rows)}','info','pass' if high==0 else 'fail','row-level cross-ledger relationship audit summary; high failures block gate_081')
    return rows

def write_field_schema(root: Path):
    fields=[
        ('relationship_id','yes','ledger_rel_NNNNN','Stable audit row id.'),
        ('relationship_family','yes','slug','Relationship family being checked.'),
        ('source_surface','yes','package-relative CSV/report path','Surface containing the reference.'),
        ('source_id','yes','row id or .','Row identifier in the source surface.'),
        ('source_field','yes','field name','Field containing the reference.'),
        ('referenced_surface','yes','package-relative path or logical target','Target surface or logical target.'),
        ('referenced_id','yes','identifier/path or .','Referenced identifier or path.'),
        ('expected_state','yes','free text','Expected join/coverage state.'),
        ('observed_state','yes','free text','Observed join/coverage state.'),
        ('severity','yes','info|high','High rows block release.'),
        ('status','yes','pass|fail','Relationship check status.'),
        ('note','yes','free text','Review note; never public-release permission.'),
    ]
    rows=[{'field':a,'required':b,'allowed_values_or_pattern':c,'meaning':d} for a,b,c,d in fields]
    write_csv_json_md_report(root,'SCHEMA/Ledger-Relationship-Audit-Fields-current.csv',['field','required','allowed_values_or_pattern','meaning'],rows,'Ledger Relationship Audit Fields','tools/ledger_relationship_audit.py',columns=['field','required','allowed_values_or_pattern','meaning'])

def write_reports(root: Path, rows):
    write_field_schema(root)
    bad=[r for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    write_csv_json_md_report(root,'META/Ledger-Relationship-Audit-current.csv',FIELDS,rows,'Ledger Relationship Audit','tools/ledger_relationship_audit.py',columns=['relationship_family','source_surface','source_id','source_field','referenced_surface','referenced_id','severity','status','note'],intro_lines=[f'Rows: {len(rows)}',f'High failures: {len(bad)}','This gate converts scattered cross-ledger assumptions into row-level join checks. It is not public-release permission.'],max_md_rows=360)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report: write_reports(root, rows)
    bad=[r for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    print(f"{'FAIL' if bad else 'PASS'} ledger relationship audit rows={len(rows)} high_fail={len(bad)}")
    for r in bad[:20]: print(f"HIGH {r['relationship_family']} {r['source_surface']} {r['source_id']}->{r['referenced_id']}: {r['note']}")
    if args.fail_on_high and bad: sys.exit(1)
if __name__=='__main__': main()
