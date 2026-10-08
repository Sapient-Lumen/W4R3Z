#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
META=json.loads((ROOT/'CUBE-META.json').read_text(encoding='utf-8'))
REV=META.get('revision','rev0072'); REVUP=REV.upper()
ART=ROOT/'artifacts'/'probe-results'/f'{REVUP}_LANE_DECISION_MATRIX.json'
OUT=ROOT/'artifacts'/'audit'; OUT.mkdir(parents=True, exist_ok=True)

def load(p: Path): return json.loads(p.read_text(encoding='utf-8'))

def main() -> int:
    errors=[]; warnings=[]
    if not ART.exists():
        errors.append('missing '+ART.relative_to(ROOT).as_posix()); art={}; s={}; decisions=[]; pq=[]
    else:
        art=load(ART); s=art.get('summary',{}); decisions=art.get('decisions',[]); pq=art.get('priority_queue',[])
    by={d.get('lane'):d for d in decisions}
    if art:
        if art.get('revision') != REV: errors.append('revision mismatch')
        if art.get('promotion_allowed') is not False or s.get('promotion_allowed') is not False: errors.append('promotion overclaim')
        if art.get('public_pretrained_trace_loaded') is not False or art.get('gpu_fused_kernel_measured') is not False: errors.append('public/GPU claim leakage')
        if s.get('support_reuse_should_not_be_next_default') is not True: errors.append('support reuse stop signal missing')
        if s.get('highest_priority_lane') != 'public_pretrained_trace_capture': errors.append('public trace should be highest priority')
        if s.get('public_trace_claim_gate_hardened') is not True: errors.append('public trace claim gate hardening not reflected')
        if by.get('raw_anchor_support_reuse',{}).get('decision') != 'retire_invalid_fast_path': errors.append('raw anchor reuse not retired')
        if not str(by.get('certified_support_reuse',{}).get('decision','')).startswith('pause'): errors.append('certified support reuse not paused')
        if not str(by.get('boundary_refined_selector',{}).get('decision','')).startswith('retire'): errors.append('boundary refined selector not retired as deployable path')
        if by.get('public_pretrained_trace_capture',{}).get('decision') != 'continue_highest_priority': errors.append('public trace capture not prioritized')
        if not pq or pq[0].get('work_item') != 'capture_or_import_public_pretrained_trace_bundle_with_manifest': errors.append('priority queue top item wrong')
        if len(s.get('retired_or_paused_lanes',[])) < 3: warnings.append('fewer paused/retired lanes than expected')
    report={'project':'CloudtainerML','revision':REV,'report':'lane_decision_matrix_audit','status':'pass' if not errors else 'fail','promotion_allowed':False,'artifact':ART.relative_to(ROOT).as_posix(),'errors':errors,'warnings':warnings,'key_metrics':s,'interpretation':'The lane matrix prevents waste: raw/uncertified reuse is retired, safe-but-slower support reuse is paused, boundary refinement is non-deployable on local CPU, and public/pretrained trace capture becomes the next priority.'}
    (OUT/f'{REVUP}_LANE_DECISION_MATRIX_AUDIT.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n', encoding='utf-8')
    (OUT/f'{REVUP}_LANE_DECISION_MATRIX_AUDIT.md').write_text('# Lane decision matrix audit — '+REV+'\n\n**Status: '+report['status']+'**\n\n'+report['interpretation']+'\n', encoding='utf-8')
    print(json.dumps({'status':report['status'],'errors':len(errors),'warnings':len(warnings)}, indent=2))
    return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
