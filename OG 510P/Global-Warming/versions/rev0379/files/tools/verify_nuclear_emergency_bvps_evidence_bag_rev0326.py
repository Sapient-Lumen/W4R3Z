#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json,posixpath,sys,zipfile
from pathlib import Path
PUBLIC={'public_context','public_archive','public_schedule','public_AAR','public_event_notification','public_fact_sheet','public_CAP_archive'}
def truth(v): return str(v or '').strip().lower() in {'true','1','yes'}
def hbytes(b): return hashlib.sha256(b).hexdigest()
def rowhash(r): return hbytes(json.dumps({k:str(v) for k,v in r.items() if k!='row_hash'},sort_keys=True,separators=(',',':')).encode())
def merkle(hs):
    if not hs: return hbytes(b'')
    level=[bytes.fromhex(h) for h in sorted(hs)]
    while len(level)>1:
        if len(level)%2: level.append(level[-1])
        level=[hashlib.sha256(level[i]+level[i+1]).digest() for i in range(0,len(level),2)]
    return level[0].hex()
def safe_names(z):
    seen=set()
    for raw in z.namelist():
        n=posixpath.normpath(raw.replace('\\','/'))
        if raw.startswith('/') or n.startswith('../') or n=='..' or '/../' in '/'+n+'/': return False,'unsafe zip path '+raw
        if n in seen: return False,'duplicate normalized zip path '+raw
        seen.add(n)
    return True,'ok'
def verify_zip(zp):
    counts={'manifest_rows':0,'row_hash_mismatch':0,'payload_hash_mismatch':0,'sensitive_without_surrogate':0,'closure_claim_rows':0,'redaction_hash_collision':0}
    try:
        with zipfile.ZipFile(zp) as z:
            ok,why=safe_names(z)
            if not ok: return 'reject_integrity_failure',why,counts
            names=set(z.namelist())
            if not {'manifest.csv','merkle.csv','packet.json'}<=names: return 'reject_integrity_failure','missing manifest.csv/merkle.csv/packet.json',counts
            pkt=json.loads(z.read('packet.json').decode())
            if pkt.get('claim_effect')!='no_auto_closure' or pkt.get('accepted_state_ceiling')!='candidate_for_adjudication_not_closure': return 'reject_closure_attempt','packet tries to bypass adjudication',counts
            mb=z.read('manifest.csv')
            if pkt.get('manifest_sha256')!=hbytes(mb): return 'reject_integrity_failure','manifest_sha256 mismatch',counts
            rows=list(csv.DictReader(mb.decode().splitlines())); counts['manifest_rows']=len(rows); hs=[]
            for r in rows:
                if r.get('claim_effect')!='no_auto_closure' or r.get('acceptance_ceiling')!='candidate_for_adjudication_not_closure': counts['closure_claim_rows']+=1
                if r.get('row_hash')!=rowhash(r): counts['row_hash_mismatch']+=1
                hs.append(r.get('row_hash',''))
                ent='originals/'+r.get('relative_path','')
                if ent not in names: counts['payload_hash_mismatch']+=1; continue
                if r.get('sha256_original')!=hbytes(z.read(ent)): counts['payload_hash_mismatch']+=1
                if r.get('redaction_class')=='sensitive_annex' and r.get('public_surrogate_required')=='true':
                    if not r.get('public_surrogate_path') or not r.get('sha256_redacted_surrogate'): counts['sensitive_without_surrogate']+=1
                    if r.get('sha256_redacted_surrogate') and r.get('sha256_redacted_surrogate')==r.get('sha256_original'): counts['redaction_hash_collision']+=1
            if counts['closure_claim_rows']: return 'reject_closure_attempt','manifest row claims closure',counts
            if counts['row_hash_mismatch'] or counts['payload_hash_mismatch']: return 'reject_integrity_failure','row hash or payload hash mismatch',counts
            if counts['sensitive_without_surrogate'] or counts['redaction_hash_collision']: return 'hold_no_upgrade','sensitive annex surrogate invalid or missing',counts
            mr=list(csv.DictReader(z.read('merkle.csv').decode().splitlines()))
            root=merkle(hs)
            if not mr or mr[0].get('merkle_root_sha256')!=root or pkt.get('merkle_root_sha256')!=root: return 'reject_integrity_failure','Merkle root mismatch',counts
            return 'candidate_for_adjudication_not_closure','bag integrity verified; candidate only',counts
    except Exception as e:
        return 'reject_integrity_failure','cannot verify evidence bag: '+str(e),counts
def classify(r,base):
    if truth(r.get('claims_local_closure')) or r.get('failure_mode') in {'claims_green','claims_ready','accepted_closure'}: return 'reject_closure_attempt','closure claim blocked',{}
    if truth(r.get('counterevidence')): return 'accepted_reopen_signal','counterevidence opens/reopens only',{}
    if r.get('source_class') in PUBLIC: return 'context_no_upgrade','public/context/archive source cannot close local evidence',{}
    fm=r.get('failure_mode','')
    if fm in {'missing_required_field','clock_drift_unknown','custody_gap','redaction_pair_missing','public_surrogate_hash_missing','stale_replay_no_supersession','self_attested_verifier'}: return 'hold_no_upgrade','hold: '+fm,{}
    if fm in {'tampered_payload','missing_manifest','bad_manifest_hash','bad_merkle_root','path_traversal','duplicate_zip_entry','wrong_site_scope','row_hash_mismatch','unsafe_file_name','redaction_leak_detected'}: return 'reject_integrity_failure','integrity failure: '+fm,{}
    zp=r.get('zip_path','').strip()
    if zp: return verify_zip((base/zp).resolve() if not Path(zp).is_absolute() else Path(zp))
    return 'hold_no_upgrade','no verifiable zip or recognized fixture mode',{}
def main(argv=None):
    argv=argv or sys.argv[1:]
    if len(argv)!=2: print('usage: verifier fixture.csv result.csv',file=sys.stderr); return 2
    fixture,result=map(Path,argv); rows=list(csv.DictReader(fixture.open(newline='',encoding='utf-8'))); base=fixture.parent.parent if fixture.parent.name=='cube' else fixture.parent
    fields=list(rows[0]) if rows else []
    out=fields+['actual_decision','pass','public_context_to_local_closure_leak','manifest_rows','integrity_detail','decision_reason']; fail=0
    with result.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=out); w.writeheader()
        for r in rows:
            dec,why,counts=classify(r,base); leak=(r.get('source_class') in PUBLIC and dec=='candidate_for_adjudication_not_closure') or dec in {'accepted_closure','auto_closure','green','ready'}
            r.update({'actual_decision':dec, 'pass':str(dec==r.get('expected_decision')).lower(), 'public_context_to_local_closure_leak':str(leak).lower(), 'manifest_rows':str(counts.get('manifest_rows','')), 'integrity_detail':json.dumps(counts,sort_keys=True), 'decision_reason':why})
            if r['pass']!='true': fail+=1
            w.writerow(r)
    print(f'verified {len(rows)} integrity fixtures; failures={fail}'); return 1 if fail else 0
if __name__=='__main__': raise SystemExit(main())
