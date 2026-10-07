#!/usr/bin/env python3
"""Build a non-authorizing publication blocker ledger from the freeze plan."""
from __future__ import annotations
import argparse, hashlib, json, pathlib, sys
from typing import Any

RECIPES={
 "explicit_publication_decision":{
  "required_resolution":"write a completed publication decision note naming source, hash, target, evidence pack, compile witness, freeze packet, queue note, citation-head update, and receipt obligation",
  "close_command":"python3 -B publishing/check_publication_decision_authorization.py --root . --write-report reports/publication_decision_authorization.json",
  "evidence_surface":"reports/publication_decision_authorization.json",
 },
 "metadata_and_provenance_refresh":{
  "required_resolution":"after any gate-closing change, rebuild research metadata, provenance, manifest, schemas, invariants, and packaging surfaces",
  "close_command":"python3 -B publishing/rebuild_archive_surfaces.py --root .",
  "evidence_surface":"reports/research_metadata_integrity.json",
 },
 "manual_clean_latex_compile":{
  "required_resolution":"refresh a current deterministic clean LaTeX compile witness",
  "close_command":"python3 -B publishing/build_freeze_compile_witness.py --root . --force-compile",
  "evidence_surface":"reports/freeze_compile_witness.json",
 },
}
BOUND=[
 "release_queue/NEXT_RELEASE_FREEZE_PLAN.json",
 "reports/publication_rehearsal.json",
 "reports/freeze_toolchain.json",
 "reports/freeze_compile_witness.json",
 "reports/evidence_pack_integrity.json",
 "reports/freeze_packet_integrity.json",
 "reports/publication_decision_template.json",
 "reports/publication_decision_authorization.json",
 "reports/publication_boundary.json",
 "reports/research_metadata_integrity.json",
 "reports/archive_packaging_recipe.json",
]

def load(p:pathlib.Path)->Any: return json.loads(p.read_text(encoding='utf-8'))
def sha(p:pathlib.Path)->str:
 h=hashlib.sha256();
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()

def surface(root:pathlib.Path, rel:str)->dict[str,Any]:
 p=root/rel
 return {"path":rel,"exists":p.exists(),"sha256":sha(p) if p.exists() else ""}

def build(root:pathlib.Path)->dict[str,Any]:
 release=load(root/'RELEASE_MANIFEST.json')
 plan=load(root/'release_queue/NEXT_RELEASE_FREEZE_PLAN.json')
 rehearsal=load(root/'reports/publication_rehearsal.json')
 selected=plan.get('selected_source',{}) if isinstance(plan.get('selected_source'),dict) else {}
 gates=[g for g in plan.get('gates',[]) if isinstance(g,dict)]
 open_gates=[g for g in gates if g.get('blocking',True) and g.get('status')!='pass']
 blockers=[]
 for i,g in enumerate(open_gates,1):
  name=str(g.get('name',''))
  recipe=RECIPES.get(name,{})
  blockers.append({
   "id":f"BLK-{i:03d}","gate":name,"status":g.get('status',''),"blocking":bool(g.get('blocking',True)),"detail":g.get('detail',''),
   "required_resolution":recipe.get('required_resolution','resolve this freeze-plan gate'),
   "close_command":recipe.get('close_command','python3 -B publishing/rebuild_archive_surfaces.py --root .'),
   "evidence_surface":recipe.get('evidence_surface','release_queue/NEXT_RELEASE_FREEZE_PLAN.json'),
  })
 failures=[]
 for label, obj in [('freeze_plan',plan),('publication_rehearsal',rehearsal)]:
  if obj.get('publication_authorized') is True: failures.append({'surface':label,'reason':'publication_authorized_true'})
  if obj.get('generated_for_revision') not in {None, release['revision']} or obj.get('checked_bundle') not in {None, release['bundle']}:
   failures.append({'surface':label,'reason':'revision_or_bundle_mismatch'})
 rb=[b.get('gate') for b in rehearsal.get('blocking_gates',[]) if isinstance(b,dict)]
 pb=[b['gate'] for b in blockers]
 if sorted(rb)!=sorted(pb): failures.append({'surface':'publication_rehearsal','reason':'blocker_set_mismatch','rehearsal':rb,'freeze_plan':pb})
 src=str(selected.get('source_tex','')); expected=str(selected.get('source_sha256',''))
 if src and (root/src).exists() and sha(root/src)!=expected: failures.append({'surface':'selected_source','reason':'source_hash_mismatch'})
 gate_counts={"passed":sum(1 for g in gates if g.get('status')=='pass'),"pending":sum(1 for g in gates if g.get('status')=='pending'),"failed":sum(1 for g in gates if g.get('status')=='fail'),"blocking_open":len(blockers),"total":len(gates)}
 return {
  "version":1,
  "generated_for_revision":release['revision'],"checked_bundle":release['bundle'],"publication_authorized":False,
  "ledger_type":"non_authorizing_publication_blocker_ledger",
  "status":"pass" if not failures else "fail",
  "ready_to_publish":False,
  "selected_source":{"source_tex":src,"source_sha256":expected,"title":selected.get('title',''),"decision_note":selected.get('decision_note',''),"prospective_target":selected.get('prospective_target','')},
  "gate_counts":gate_counts,"blockers":blockers,
  "passed_gates":[{"gate":g.get('name',''),"detail":g.get('detail','')} for g in gates if g.get('status')=='pass'],
  "surface_digests":[surface(root,r) for r in BOUND],
  "summary":{"checks_failed":len(failures),"blocker_count":len(blockers),"surface_failure_count":len(failures),"ready_to_publish":False},
  "failures":failures[:50],
  "fail_closed_rule":"If this ledger is missing, stale, or disagrees with the freeze plan/rehearsal, default to no publication.",
 }

def render(ledger:dict[str,Any])->str:
 src=ledger['selected_source']; lines=["# Publication Blocker Ledger","",f"- Generated for revision: `{ledger['generated_for_revision']}`",f"- Checked bundle: `{ledger['checked_bundle']}`",f"- Publication authorized: `{str(ledger['publication_authorized']).lower()}`",f"- Ready to publish: `{str(ledger['ready_to_publish']).lower()}`",f"- Status: `{ledger['status']}`","","## Selected dry-run source","",f"- Source: `{src.get('source_tex','')}`",f"- SHA-256: `{src.get('source_sha256','')}`",f"- Queue note: `{src.get('decision_note','')}`",f"- Prospective target: `{src.get('prospective_target','')}`","","## Open blocking gates",""]
 if ledger.get('blockers'):
  for b in ledger['blockers']:
   lines += [f"### {b['id']} — {b['gate']}","",f"- Status: `{b['status']}`",f"- Detail: {b['detail']}",f"- Required resolution: {b['required_resolution']}",f"- Command: `{b['close_command']}`",f"- Evidence surface: `{b['evidence_surface']}`",""]
 else:
  lines.append('No open blockers are recorded. This still does not authorize publication without a completed decision and guarded helper execution.\n')
 lines += ["## Bound surfaces",""]
 for s in ledger.get('surface_digests',[]): lines.append(f"- `{s['path']}` — {'present' if s.get('exists') else 'missing'}, sha256-prefix `{s.get('sha256','')[:16]}`")
 return '\n'.join(lines)+'\n'

def main()->int:
 ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.'); ap.add_argument('--write-json',default='release_queue/PUBLICATION_BLOCKERS.json'); ap.add_argument('--write-md',default='release_queue/PUBLICATION_BLOCKERS.md'); args=ap.parse_args(); root=pathlib.Path(args.root).resolve(); ledger=build(root); (root/args.write_json).write_text(json.dumps(ledger,indent=2)+'\n',encoding='utf-8'); (root/args.write_md).write_text(render(ledger),encoding='utf-8'); print(json.dumps({'status':ledger['status'],'blockers':len(ledger['blockers']),'written':[args.write_json,args.write_md]},indent=2)); return 0 if ledger['status']=='pass' else 1
if __name__=='__main__': raise SystemExit(main())
