#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
META=json.loads((ROOT/'CUBE-META.json').read_text())
REV=META.get('revision','rev0000'); REVUP=REV.upper()
AUD=ROOT/'artifacts'/'audit'; AUD.mkdir(parents=True, exist_ok=True)
claims=[
 {'rank':1,'claim':'DCT+attention residual may be the default tiny operator baseline','evidence_tier':'A','novelty_caution':'CHIAR already reports DCT+attention collapse; CloudtainerML evidence is tiny-scale held-out/HPO pressure and alias-guard framing.','next_test':'tiny trained/operator routing model'},
 {'rank':2,'claim':'Phase smoothness / monitorability may be an architecture metric','evidence_tier':'A-','novelty_caution':'The phase-transition theory is external; using monitorability as a promotion criterion is the project-specific twist.','next_test':'one-head copy task training'},
 {'rank':3,'claim':'Sparse attention is an arbitration problem, not a single method class','evidence_tier':'A-','novelty_caution':'MoSA/LoLA are known; the combined router frontier is the project-specific pressure.','next_test':'matrix-level MoSA-vs-LoLA-vs-hybrid'},
 {'rank':4,'claim':'Functional component rank allocation should be tested before generic low-rank compression','evidence_tier':'B+','novelty_caution':'A3/STAR-KV already motivate it; small phase surfaces are under-tested.','next_test':'real random-matrix/SVD sweep'},
 {'rank':5,'claim':'FFN sparsity may export computation into attention','evidence_tier':'B','novelty_caution':'Redistribution is already a paper lane; guard-field requirement is the project contribution.','next_test':'one-layer trained sparse-FFN toy'},
 {'rank':6,'claim':'Cheap-screen regret is a discovery filter','evidence_tier':'B','novelty_caution':'Methodological rather than architectural novelty.','next_test':'make regret/cost guards mandatory for P0 promotion'},
 {'rank':7,'claim':'Exact-copy/needle exactness should veto efficient-memory claims','evidence_tier':'B-','novelty_caution':'Copy benchmarks are known; the veto role across all efficient architectures is project-specific.','next_test':'shared exactness harness'},
]
# basic checks
missing=[]
for rel in ['NOVELTY-HYPOTHESES.md','PROJECT-SALIENCE.md','SURPRISE-LEDGER.json','PROJECT-CHARTER.md']:
    if not (ROOT/rel).exists(): missing.append(rel)
status='pass' if not missing else 'fail'
report={'project':'CloudtainerML','revision':REV,'status':status,'claim_count':len(claims),'p0_candidate_count':4,'claims':claims,'missing_required':missing,'note':'Audit ranks under-tested or internally surprising hypotheses without claiming global novelty.'}
(AUD/f'{REVUP}_NOVELTY_SALIENCE_AUDIT.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
md=['# Novelty/salience audit — '+REV,'',f'Status: **{status}**','',f'Claims ranked: {len(claims)}','']
for c in claims:
    md.append(f"{c['rank']}. **{c['claim']}** — tier {c['evidence_tier']}. {c['novelty_caution']} Next: {c['next_test']}.")
if missing:
    md += ['', '## Missing', *[f'- `{m}`' for m in missing]]
(AUD/f'{REVUP}_NOVELTY_SALIENCE_AUDIT.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
print(json.dumps({'status':status,'claims':len(claims),'missing':missing},indent=2))
raise SystemExit(0 if status=='pass' else 1)
