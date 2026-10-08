#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
META=json.loads((ROOT/'CUBE-META.json').read_text(encoding='utf-8'))
REV=META.get('revision','rev0069'); REVUP=REV.upper()
ART=ROOT/'artifacts'/'probe-results'/f'{REVUP}_CERTIFIED_SUPPORT_REUSE.json'
OUT=ROOT/'artifacts'/'audit'; OUT.mkdir(parents=True, exist_ok=True)

def load(p: Path): return json.loads(p.read_text(encoding='utf-8'))

def main() -> int:
    errors=[]; warnings=[]
    if not ART.exists():
        errors.append(f'missing artifact {ART.relative_to(ROOT)}')
        art={}; s={}; native={}
    else:
        art=load(ART); s=art.get('summary',{}); native=art.get('native',{})
    cert=native.get('certificate',{}) if native else {}
    acct=native.get('accounting',{}) if native else {}
    scope=art.get('measurement_scope','').lower() if art else ''
    if art:
        if art.get('revision') != REV: errors.append('artifact revision mismatch')
        if art.get('promotion_allowed') is not False or s.get('promotion_allowed') is not False: errors.append('promotion must remain blocked')
        if art.get('public_pretrained_trace_loaded') is not False or s.get('public_pretrained_trace_loaded') is not False: errors.append('public/pretrained overclaim')
        if art.get('gpu_fused_kernel_measured') is not False or s.get('gpu_fused_kernel_measured') is not False: errors.append('GPU/fused overclaim')
        if s.get('support_reuse_certificate_tested') is not True: errors.append('certificate test flag missing')
        if s.get('certificate_uses_observable_q_key_bounds') is not True: errors.append('observable Q/K certificate flag missing')
        if s.get('certificate_uses_values_or_dense_outputs') is not False: errors.append('certificate leakage flag wrong')
        if s.get('fallback_paid_in_timed_loop') is not True or s.get('certificate_bound_paid_in_timed_loop') is not True: errors.append('fallback/certificate work must be paid')
        if int(s.get('false_certified_quality_failures',-1)) != 0: errors.append('certified rows produced quality failures')
        if float(s.get('certified_quality_rate',0.0)) < 0.99: errors.append('certified path quality below bar')
        if float(s.get('raw_anchor_quality_rate',1.0)) >= 0.95: errors.append('raw anchor negative control did not expose invalid quality')
        if float(s.get('raw_anchor_speedup_vs_dense',0.0)) <= 1.0: errors.append('raw negative control no longer shows tempting fast path')
        if float(s.get('certified_speedup_vs_dense',9.0)) >= 1.0: errors.append('certified path unexpectedly became a speed win; require new promotion audit')
        if float(s.get('certified_qk_dot_fraction',0.0)) < 0.95: warnings.append('certified QK fraction below near-dense; inspect whether certificate has become useful')
        if float(s.get('certified_bound_metadata_scan_fraction',0.0)) <= 0.0: errors.append('metadata-bound scan accounting missing')
        for key in ['observable_q_key_bound','uses_query_distance','uses_key_norms','uses_key_drift_norms']:
            if cert.get(key) is not True: errors.append('certificate missing '+key)
        if cert.get('uses_values') is not False or cert.get('uses_dense_outputs') is not False: errors.append('certificate uses forbidden data')
        if acct.get('fallback_paid_in_timed_loop') is not True or acct.get('certificate_bound_paid_in_timed_loop') is not True: errors.append('native accounting missing paid fallback/bound')
        for phrase in ['observable query-distance/key-norm/key-drift', 'fallback', 'paid inside the timed loop', 'not public/pretrained', 'not gpu', 'not fused']:
            if phrase not in scope: errors.append('measurement scope missing phrase: '+phrase)
    report={
        'project':'CloudtainerML','revision':REV,'report':'certified_support_reuse_audit',
        'status':'pass' if not errors else 'fail','promotion_allowed':False,
        'artifact': ART.relative_to(ROOT).as_posix(),
        'key_metrics': {
            'raw_anchor_quality_rate': s.get('raw_anchor_quality_rate'),
            'raw_anchor_speedup_vs_dense': s.get('raw_anchor_speedup_vs_dense'),
            'certified_quality_rate': s.get('certified_quality_rate'),
            'certified_speedup_vs_dense': s.get('certified_speedup_vs_dense'),
            'candidate_reuse_rows': s.get('candidate_reuse_rows'),
            'certified_reuse_rows': s.get('certified_reuse_rows'),
            'fallback_rows': s.get('fallback_rows'),
            'false_certified_quality_failures': s.get('false_certified_quality_failures'),
            'certified_qk_dot_fraction': s.get('certified_qk_dot_fraction'),
            'certified_bound_metadata_scan_fraction': s.get('certified_bound_metadata_scan_fraction'),
        },
        'errors': errors, 'warnings': warnings,
        'interpretation': 'The Q/K-bound certificate blocks the invalid fast support-reuse path. It preserves quality with zero false certified failures, but fallback and metadata-bound work erase the speed case on the local trace.'
    }
    (OUT/f'{REVUP}_CERTIFIED_SUPPORT_REUSE_AUDIT.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    (OUT/f'{REVUP}_CERTIFIED_SUPPORT_REUSE_AUDIT.md').write_text('# Certified support reuse audit — '+REV+'\n\n**Status: '+report['status']+'**\n\n'+report['interpretation']+'\n', encoding='utf-8')
    print(json.dumps({'status':report['status'],'errors':len(errors),'warnings':len(warnings)}, indent=2))
    return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
