#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
HISTORICAL_AUDIT = True
ORIGINAL_REV='rev0072'
REV=ORIGINAL_REV; REVUP=REV.upper()
ART=ROOT/'artifacts'/'probe-results'/f'{REVUP}_PUBLIC_TRACE_CLAIM_CONTRACT.json'
OUT=ROOT/'artifacts'/'audit'; OUT.mkdir(parents=True, exist_ok=True)

def load(p: Path): return json.loads(p.read_text(encoding='utf-8'))

def main() -> int:
    errors=[]; warnings=[]
    if not ART.exists():
        errors.append('missing '+ART.relative_to(ROOT).as_posix()); art={}; s={}; cases={}
    else:
        art=load(ART); s=art.get('summary',{}); cases=art.get('cases',{})
    if art:
        if art.get('revision') != REV: errors.append('revision mismatch')
        if art.get('promotion_allowed') is not False or s.get('promotion_allowed') is not False: errors.append('promotion overclaim')
        if art.get('public_pretrained_trace_loaded') is not False or s.get('public_pretrained_trace_loaded') is not False: errors.append('public/pretrained overclaim')
        if art.get('gpu_fused_kernel_measured') is not False: errors.append('GPU/fused overclaim')
        if s.get('public_claim_requires_provenance_manifest') is not True: errors.append('manifest requirement missing')
        if s.get('public_claim_rejected_without_manifest') is not True: errors.append('flag-only public claim was not rejected')
        if s.get('public_claim_rejected_with_fixture_manifest') is not True: errors.append('fixture manifest public claim was not rejected')
        if s.get('schema_only_external_trace_loaded') is not True or s.get('schema_only_external_trace_not_public') is not True: errors.append('schema-only control failed')
        if int(s.get('oracle_leakage_rows_total',-1)) != 0: errors.append('oracle leakage rows present in claim contract runs')
        if s.get('public_pretrained_trace_blocker_remains') is not True: errors.append('blocker should remain open')
        no=cases.get('flag_only_no_manifest',{}); bad=cases.get('bad_fixture_provenance',{}); ctrl=cases.get('schema_only_control',{})
        if no.get('public_pretrained_trace_loaded') is not False or 'rejected' not in str(no.get('trace_gate_status')): errors.append('no-manifest case not rejected')
        if no.get('provenance_status') != 'missing_provenance_manifest': errors.append('no-manifest provenance status wrong')
        if bad.get('public_pretrained_trace_loaded') is not False or bad.get('provenance_status') != 'public_pretrained_claim_rejected': errors.append('bad fixture provenance was not rejected')
        errs=' '.join(bad.get('provenance_errors',[])).lower()
        for phrase in ['source_type', 'local tiny', 'public_pretrained_trace']:
            if phrase not in errs: warnings.append('bad provenance errors do not mention '+phrase)
        if ctrl.get('external_trace_loaded') is not True or ctrl.get('public_pretrained_trace_loaded') is not False: errors.append('schema-only external control wrong')
        if ctrl.get('trace_row_count') is None or int(ctrl.get('trace_row_count')) <= 0: errors.append('control trace rows missing')
        scope=art.get('measurement_scope','').lower()
        for phrase in ['fixture', 'must not be promoted', 'no gpu', 'no public/pretrained evidence']:
            if phrase not in scope: warnings.append('measurement scope missing phrase: '+phrase)
    report={'project':'CloudtainerML','revision':REV,'report':'public_trace_claim_contract_audit','status':'pass' if not errors else 'fail','promotion_allowed':False,'artifact':ART.relative_to(ROOT).as_posix(),'errors':errors,'warnings':warnings,'key_metrics':s,'interpretation':'Public/pretrained trace status now requires a provenance manifest; flag-only and fixture-origin claims are rejected while schema-only import remains allowed as non-public evidence.'}
    (OUT/f'{REVUP}_PUBLIC_TRACE_CLAIM_CONTRACT_AUDIT.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n', encoding='utf-8')
    (OUT/f'{REVUP}_PUBLIC_TRACE_CLAIM_CONTRACT_AUDIT.md').write_text('# Public trace claim contract audit — '+REV+'\n\n**Status: '+report['status']+'**\n\n'+report['interpretation']+'\n', encoding='utf-8')
    print(json.dumps({'status':report['status'],'errors':len(errors),'warnings':len(warnings)}, indent=2))
    return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
