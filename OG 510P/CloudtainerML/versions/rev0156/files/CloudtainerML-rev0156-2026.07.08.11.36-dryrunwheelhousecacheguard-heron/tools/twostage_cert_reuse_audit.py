#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT/'CUBE-META.json').read_text(encoding='utf-8'))
REV = META.get('revision','rev0070'); REVUP = REV.upper()
ART = ROOT/'artifacts'/'probe-results'/f'{REVUP}_TWOSTAGE_CERTIFIED_SUPPORT_REUSE.json'
OUT = ROOT/'artifacts'/'audit'; OUT.mkdir(parents=True, exist_ok=True)

def load(p: Path): return json.loads(p.read_text(encoding='utf-8'))
def f(x, default=0.0):
    try: return float(x)
    except Exception: return default

def main() -> int:
    errors=[]; warnings=[]
    if not ART.exists():
        errors.append(f'missing artifact {ART.relative_to(ROOT)}'); art={}; s={}; native={}
    else:
        art=load(ART); s=art.get('summary',{}); native=art.get('native',{})
    cert=native.get('certificate',{}) if native else {}
    acct=native.get('accounting',{}) if native else {}
    side=native.get('sidecar',{}) if native else {}
    scope=art.get('measurement_scope','').lower() if art else ''
    if art:
        if art.get('revision') != REV: errors.append('artifact revision mismatch')
        if art.get('promotion_allowed') is not False or s.get('promotion_allowed') is not False: errors.append('promotion must remain blocked')
        if art.get('public_pretrained_trace_loaded') is not False or s.get('public_pretrained_trace_loaded') is not False: errors.append('public/pretrained overclaim')
        if art.get('gpu_fused_kernel_measured') is not False or s.get('gpu_fused_kernel_measured') is not False: errors.append('GPU/fused overclaim')
        if s.get('two_stage_certificate_tested') is not True: errors.append('two-stage certificate flag missing')
        if s.get('sidecar_built_from_key_cache') is not True: errors.append('sidecar should be key-cache-derived')
        if s.get('sidecar_uses_values_or_dense_outputs') is not False: errors.append('sidecar uses forbidden data')
        if s.get('certificate_uses_observable_q_key_bounds') is not True: errors.append('observable Q/K certificate flag missing')
        if s.get('certificate_uses_values_or_dense_outputs') is not False: errors.append('certificate leakage flag wrong')
        if s.get('fallback_paid_in_timed_loop') is not True or s.get('certificate_bound_paid_in_timed_loop') is not True: errors.append('fallback/certificate work must be paid')
        if int(s.get('two_stage_false_certified_quality_failures',-1)) != 0: errors.append('two-stage certified rows produced quality failures')
        if f(s.get('two_stage_quality_rate')) < 0.99: errors.append('two-stage quality below bar')
        if f(s.get('raw_anchor_quality_rate'),1.0) >= 0.95: errors.append('raw anchor negative control did not expose invalid quality')
        if f(s.get('raw_anchor_speedup_vs_dense')) <= 1.0: errors.append('raw negative control no longer shows tempting speed')
        if f(s.get('two_stage_speedup_vs_dense'),9.0) >= 1.0: errors.append('two-stage path unexpectedly became a dense speed win; require new promotion audit')
        if f(s.get('two_stage_speedup_vs_dense')) <= f(s.get('full_token_speedup_vs_dense')): errors.append('two-stage path did not improve over full token-scan certificate')
        if f(s.get('sidecar_vs_token_bound_read_reduction')) < 0.5: errors.append('two-stage sidecar did not materially reduce bound reads')
        if int(s.get('two_stage_certified_reuse_rows',-1)) != int(s.get('full_token_certified_reuse_rows',-2)): warnings.append('two-stage and token-scan certificate certify different row counts; inspect bound looseness/tightness')
        if f(s.get('two_stage_total_sidecar_read_fraction')) >= f(s.get('full_token_bound_scan_token_fraction'),1.0): errors.append('two-stage sidecar reads not below full token scan')
        if f(s.get('two_stage_qk_dot_fraction')) >= 1.2: warnings.append('two-stage QK accounting exceeds dense by a large margin')
        if side.get('built_from_key_cache') is not True or side.get('uses_values') is not False or side.get('uses_dense_outputs') is not False: errors.append('native sidecar contract wrong')
        for key in ['observable_q_key_bound','uses_query_distance','uses_key_norms','uses_key_drift_norms']:
            if cert.get(key) is not True: errors.append('certificate missing '+key)
        if cert.get('uses_values') is not False or cert.get('uses_dense_outputs') is not False: errors.append('certificate uses forbidden data')
        if acct.get('fallback_paid_in_timed_loop') is not True or acct.get('certificate_bound_paid_in_timed_loop') is not True: errors.append('native accounting missing paid fallback/bound')
        if acct.get('sidecar_build_excluded_from_main_timing_but_reported') is not True: errors.append('sidecar build reporting flag missing')
        for phrase in ['two-stage support-reuse certificate', 'fallback', 'sidecar build is reported', 'not public/pretrained', 'not gpu', 'not fused']:
            if phrase not in scope: errors.append('measurement scope missing phrase: '+phrase)
    report={
        'project':'CloudtainerML','revision':REV,'report':'twostage_cert_reuse_audit',
        'status':'pass' if not errors else 'fail','promotion_allowed':False,
        'artifact': ART.relative_to(ROOT).as_posix(),
        'key_metrics': {
            'raw_anchor_quality_rate': s.get('raw_anchor_quality_rate'),
            'raw_anchor_speedup_vs_dense': s.get('raw_anchor_speedup_vs_dense'),
            'full_token_speedup_vs_dense': s.get('full_token_speedup_vs_dense'),
            'two_stage_quality_rate': s.get('two_stage_quality_rate'),
            'two_stage_speedup_vs_dense': s.get('two_stage_speedup_vs_dense'),
            'two_stage_certified_reuse_rows': s.get('two_stage_certified_reuse_rows'),
            'two_stage_fallback_rows': s.get('two_stage_fallback_rows'),
            'two_stage_false_certified_quality_failures': s.get('two_stage_false_certified_quality_failures'),
            'two_stage_qk_dot_fraction': s.get('two_stage_qk_dot_fraction'),
            'full_token_bound_scan_token_fraction': s.get('full_token_bound_scan_token_fraction'),
            'two_stage_total_sidecar_read_fraction': s.get('two_stage_total_sidecar_read_fraction'),
            'sidecar_vs_token_bound_read_reduction': s.get('sidecar_vs_token_bound_read_reduction'),
        },
        'errors':errors,'warnings':warnings,
        'interpretation':'The two-stage key-cache sidecar reduces certificate-bound metadata reads and preserves the quality veto on raw reuse. It is still non-promotional because the safe path remains slower than dense/fresh histogram on the local CPU trace and lacks public/GPU/fused evidence.'
    }
    (OUT/f'{REVUP}_TWOSTAGE_CERT_REUSE_AUDIT.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    (OUT/f'{REVUP}_TWOSTAGE_CERT_REUSE_AUDIT.md').write_text('# Two-stage certified support reuse audit — '+REV+'\n\n**Status: '+report['status']+'**\n\n'+report['interpretation']+'\n', encoding='utf-8')
    print(json.dumps({'status':report['status'],'errors':len(errors),'warnings':len(warnings)}, indent=2))
    return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
