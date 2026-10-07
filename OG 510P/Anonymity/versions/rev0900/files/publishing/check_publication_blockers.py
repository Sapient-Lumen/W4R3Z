#!/usr/bin/env python3
"""Validate the non-authorizing publication blocker ledger."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, pathlib, sys
from typing import Any

def load(p:pathlib.Path)->Any: return json.loads(p.read_text(encoding='utf-8'))
def sha(p:pathlib.Path)->str:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
def rec(checks,name,ok,details): checks.append({'name':name,'status':'pass' if ok else 'fail','details':details})
def expected(root:pathlib.Path)->dict[str,Any]:
 spec=importlib.util.spec_from_file_location('build_publication_blockers',root/'publishing/build_publication_blockers.py')
 mod=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(mod)  # type: ignore
 return mod.build(root)  # type: ignore

def check(root:pathlib.Path)->dict[str,Any]:
 release=load(root/'RELEASE_MANIFEST.json'); path=root/'release_queue/PUBLICATION_BLOCKERS.json'; md=root/'release_queue/PUBLICATION_BLOCKERS.md'; checks=[]
 rec(checks,'ledger_files_present',path.exists() and md.exists(),f'json={path.exists()} md={md.exists()}')
 ledger=load(path) if path.exists() else {}; exp=expected(root) if path.exists() else {}
 rec(checks,'revision_bundle_bound',ledger.get('generated_for_revision')==release['revision'] and ledger.get('checked_bundle')==release['bundle'],f"rev={ledger.get('generated_for_revision')} bundle={ledger.get('checked_bundle')}")
 rec(checks,'non_authorizing',ledger.get('publication_authorized') is False and ledger.get('ready_to_publish') is False,f"publication_authorized={ledger.get('publication_authorized')} ready={ledger.get('ready_to_publish')}")
 rec(checks,'blocker_set_current',[b.get('gate') for b in ledger.get('blockers',[])]==[b.get('gate') for b in exp.get('blockers',[])],f"ledger={[b.get('gate') for b in ledger.get('blockers',[])]} expected={[b.get('gate') for b in exp.get('blockers',[])]}")
 rec(checks,'gate_counts_current',ledger.get('gate_counts')==exp.get('gate_counts'),f"ledger={ledger.get('gate_counts')} expected={exp.get('gate_counts')}")
 src=ledger.get('selected_source',{}) if isinstance(ledger.get('selected_source'),dict) else {}; srcp=root/str(src.get('source_tex',''))
 rec(checks,'selected_source_hash_bound',srcp.exists() and sha(srcp)==src.get('source_sha256'),f"source={src.get('source_tex')}")
 digest_fail=[]
 for row in ledger.get('surface_digests',[]):
  if not isinstance(row,dict): digest_fail.append({'row':row}); continue
  p=root/str(row.get('path',''))
  if not p.exists() or row.get('exists') is not True or sha(p)!=row.get('sha256'):
   digest_fail.append({'path':row.get('path')})
 rec(checks,'bound_surface_digests_current',not digest_fail,f'failures={len(digest_fail)}')
 rec(checks,'current_status_pass',ledger.get('status')=='pass' and ledger.get('summary',{}).get('checks_failed')==0,f"status={ledger.get('status')} failed={ledger.get('summary',{}).get('checks_failed')}")
 failures=[c for c in checks if c['status']=='fail']
 return {'status':'pass' if not failures else 'fail','generated_for_revision':release['revision'],'checked_bundle':release['bundle'],'publication_authorized':False,'ledger':'release_queue/PUBLICATION_BLOCKERS.json','checks':checks,'summary':{'checks_failed':len(failures),'checks_passed':len(checks)-len(failures),'blocker_count':len(ledger.get('blockers',[])),'ready_to_publish':False},'failures':failures,'fail_closed_rule':'If the blocker ledger fails validation, default to no publication.'}

def main()->int:
 ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.'); ap.add_argument('--write-report',default=''); args=ap.parse_args(); root=pathlib.Path(args.root).resolve(); report=check(root); text=json.dumps(report,indent=2)+'\n';
 if args.write_report:
  out=root/args.write_report; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(text,encoding='utf-8')
 sys.stdout.write(text); return 0 if report['status']=='pass' else 1
if __name__=='__main__': raise SystemExit(main())
