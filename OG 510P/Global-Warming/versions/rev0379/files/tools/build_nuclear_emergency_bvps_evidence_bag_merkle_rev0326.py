#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,json,mimetypes,posixpath,zipfile
from datetime import datetime,timezone
from pathlib import Path
SENSITIVE=('pii','medical','patient','student','afn','route','credential','password','security','dosimetry')
def hbytes(b): return hashlib.sha256(b).hexdigest()
def hfile(p):
    x=hashlib.sha256()
    with Path(p).open('rb') as f:
        for c in iter(lambda:f.read(1048576),b''): x.update(c)
    return x.hexdigest()
def norm_rel(p,base):
    rel=Path(p).relative_to(base).as_posix(); n=posixpath.normpath(rel)
    if n.startswith('../') or n=='..' or n.startswith('/') or '\\' in rel: raise ValueError('unsafe path '+rel)
    return n
def rowhash(r): return hbytes(json.dumps({k:str(v) for k,v in r.items() if k!='row_hash'},sort_keys=True,separators=(',',':')).encode())
def merkle(hs):
    if not hs: return hbytes(b'')
    level=[bytes.fromhex(h) for h in sorted(hs)]
    while len(level)>1:
        if len(level)%2: level.append(level[-1])
        level=[hashlib.sha256(level[i]+level[i+1]).digest() for i in range(0,len(level),2)]
    return level[0].hex()
def main(argv=None):
    ap=argparse.ArgumentParser(); ap.add_argument('--input-dir',required=True); ap.add_argument('--output-dir',required=True); ap.add_argument('--bag-id',required=True); ap.add_argument('--packet-id',required=True); ap.add_argument('--site-or-overlay',default='BVPS_ANON_EXERCISE')
    a=ap.parse_args(argv); base=Path(a.input_dir).resolve(); out=Path(a.output_dir); out.mkdir(parents=True,exist_ok=True)
    paths=sorted(p for p in base.rglob('*') if p.is_file()); rels={norm_rel(p,base) for p in paths}; now=datetime.now(timezone.utc).replace(microsecond=0).isoformat(); rows=[]
    for i,p in enumerate(paths,1):
        rel=norm_rel(p,base); low=rel.lower(); red='public_surrogate' if rel.startswith('surrogates/') else ('sensitive_annex' if any(s in low for s in SENSITIVE) else 'ordinary_local_artifact')
        surr=''; sh=''; req='false'
        if red=='sensitive_annex':
            req='true'; cand='surrogates/'+posixpath.basename(rel)+'.surrogate.txt'
            if cand in rels: surr=cand; sh=hfile(base/cand)
        r={'bag_id':a.bag_id,'packet_id':a.packet_id,'artifact_id':f'{a.bag_id}-ART-{i:04d}','relative_path':rel,'media_type':mimetypes.guess_type(p.name)[0] or 'application/octet-stream','byte_size':str(p.stat().st_size),'sha256_original':hfile(p),'redaction_class':red,'public_surrogate_required':req,'public_surrogate_path':surr,'sha256_redacted_surrogate':sh,'capture_time_utc':now,'custody_event_id':a.bag_id+'-CUSTODY-001','claim_effect':'no_auto_closure','acceptance_ceiling':'candidate_for_adjudication_not_closure'}
        r['row_hash']=rowhash(r); rows.append(r)
    root=merkle([r['row_hash'] for r in rows])
    mf=out/(a.bag_id+'-manifest.csv'); fields=list(rows[0]) if rows else ['bag_id','packet_id','artifact_id','relative_path','row_hash']
    with mf.open('w',newline='',encoding='utf-8') as f: w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    mk=out/(a.bag_id+'-merkle.csv')
    with mk.open('w',newline='',encoding='utf-8') as f: w=csv.DictWriter(f,fieldnames=['bag_id','row_count','merkle_root_sha256','hash_algorithm','claim_effect']); w.writeheader(); w.writerow({'bag_id':a.bag_id,'row_count':len(rows),'merkle_root_sha256':root,'hash_algorithm':'SHA-256/FIPS-180-4','claim_effect':'no_auto_closure'})
    pkt={'bag_id':a.bag_id,'packet_id':a.packet_id,'site_or_overlay':a.site_or_overlay,'created_utc':now,'artifact_count':len(rows),'manifest_sha256':hfile(mf),'merkle_root_sha256':root,'claim_effect':'no_auto_closure','accepted_state_ceiling':'candidate_for_adjudication_not_closure'}
    pf=out/(a.bag_id+'-packet.json'); pf.write_text(json.dumps(pkt,indent=2,sort_keys=True),encoding='utf-8')
    zf=out/(a.bag_id+'-evidence-bag.zip')
    with zipfile.ZipFile(zf,'w',compression=zipfile.ZIP_DEFLATED) as z:
        z.write(mf,'manifest.csv'); z.write(mk,'merkle.csv'); z.write(pf,'packet.json')
        for p in paths: z.write(p,'originals/'+norm_rel(p,base))
    print(json.dumps({'bag_id':a.bag_id,'artifact_count':len(rows),'merkle_root_sha256':root,'zip':str(zf),'claim_effect':'no_auto_closure'},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
