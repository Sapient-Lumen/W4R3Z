#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT/'CUBE-META.json').read_text(encoding='utf-8'))
REV = META.get('revision','rev0071'); REVUP = REV.upper()
ART = ROOT/'artifacts'/'probe-results'/f'{REVUP}_STAGE_PRUNED_CERT_REUSE_POLICY.json'
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
        if s.get('stage_pruned_certificate_tested') is not True: errors.append('stage-pruned certificate flag missing')
        if s.get('sidecar_built_from_key_cache') is not True: errors.append('sidecar should be key-cache-derived')
        if s.get('sidecar_uses_values_or_dense_outputs') is not False: errors.append('sidecar uses forbidden data')
        if s.get('certificate_uses_observable_q_key_bounds') is not True: errors.append('observable Q/K certificate flag missing')
        if s.get('certificate_uses_values_or_dense_outputs') is not False: errors.append('certificate leakage flag wrong')
        if s.get('fallback_paid_in_timed_loop') is not True or s.get('certificate_bound_paid_in_timed_loop') is not True: errors.append('fallback/certificate work must be paid')
        if int(s.get('scalar_only_false_certified_quality_failures',-1)) != 0: errors.append('scalar-only certified rows produced quality failures')
        if f(s.get('scalar_only_quality_rate')) < 0.99: errors.append('scalar-only quality below bar')
        if f(s.get('raw_anchor_quality_rate'),1.0) >= 0.95: errors.append('raw anchor negative control did not expose invalid quality')
        if f(s.get('raw_anchor_speedup_vs_dense')) <= 1.0: errors.append('raw negative control no longer shows tempting speed')
        if int(s.get('block_stage_extra_certified_rows',-1)) != 0: errors.append('block stage unexpectedly certified extra rows; stage-prune claim invalid')
        if s.get('block_stage_pruned_as_dead_weight') is not True: errors.append('dead block-stage pruning flag missing')
        if f(s.get('scalar_pruned_block_read_reduction_vs_two_stage')) < 0.75: errors.append('stage pruning did not remove enough block-sidecar read work')
        if f(s.get('scalar_only_sidecar_read_fraction'),9.0) >= f(s.get('two_stage_total_sidecar_read_fraction'),0.0): errors.append('scalar-only sidecar reads not below two-stage')
        if f(s.get('scalar_only_speedup_vs_dense'),0.0) <= f(s.get('two_stage_speedup_vs_dense'),0.0): errors.append('scalar-only path did not improve over two-stage timing')
        if f(s.get('scalar_only_speedup_vs_dense'),9.0) >= 1.0: errors.append('scalar-only path unexpectedly became a dense speed win; require new promotion audit')
        if f(s.get('scalar_only_speedup_vs_dense'),0.0) < f(s.get('fresh_hist_speedup_vs_dense'),0.0): warnings.append('scalar-only safe reuse remains slower than fresh histogram; expected blocker')
        if f(s.get('scalar_only_qk_dot_fraction')) >= 0.95: warnings.append('scalar-only certified reuse remains near/full dense in QK accounting')
        if side.get('built_from_key_cache') is not True or side.get('uses_values') is not False or side.get('uses_dense_outputs') is not False: errors.append('native sidecar contract wrong')
        for key in ['observable_q_key_bound','uses_query_distance','uses_key_norms','uses_key_drift_norms']:
            if cert.get(key) is not True: errors.append('certificate missing '+key)
        if cert.get('uses_values') is not False or cert.get('uses_dense_outputs') is not False: errors.append('certificate uses forbidden data')
        if acct.get('fallback_paid_in_timed_loop') is not True or acct.get('certificate_bound_paid_in_timed_loop') is not True: errors.append('native accounting missing paid fallback/bound')
        if acct.get('sidecar_build_excluded_from_main_timing_but_reported') is not True: errors.append('sidecar build reporting flag missing')
        for phrase in ['stage-pruned support-reuse certificate', 'block refinement', 'fallback', 'not public/pretrained', 'not gpu', 'not fused']:
            if phrase not in scope: errors.append('measurement scope missing phrase: '+phrase)
    report={
        'project':'CloudtainerML','revision':REV,'report':'stage_prune_cert_policy_audit',
        'status':'pass' if not errors else 'fail','promotion_allowed':False,
        'artifact': ART.relative_to(ROOT).as_posix(),
        'key_metrics': {
            'raw_anchor_quality_rate': s.get('raw_anchor_quality_rate'),
            'raw_anchor_speedup_vs_dense': s.get('raw_anchor_speedup_vs_dense'),
            'fresh_hist_speedup_vs_dense': s.get('fresh_hist_speedup_vs_dense'),
            'two_stage_speedup_vs_dense': s.get('two_stage_speedup_vs_dense'),
            'scalar_only_quality_rate': s.get('scalar_only_quality_rate'),
            'scalar_only_speedup_vs_dense': s.get('scalar_only_speedup_vs_dense'),
            'scalar_only_certified_reuse_rows': s.get('scalar_only_certified_reuse_rows'),
            'scalar_only_fallback_rows': s.get('scalar_only_fallback_rows'),
            'block_stage_extra_certified_rows': s.get('block_stage_extra_certified_rows'),
            'scalar_only_sidecar_read_fraction': s.get('scalar_only_sidecar_read_fraction'),
            'two_stage_total_sidecar_read_fraction': s.get('two_stage_total_sidecar_read_fraction'),
            'scalar_pruned_block_read_reduction_vs_two_stage': s.get('scalar_pruned_block_read_reduction_vs_two_stage'),
        },
        'errors':errors,'warnings':warnings,
        'interpretation':'The block-refinement stage is pruned as dead weight on this trace: scalar-only certification preserves safety and removes most sidecar reads, but remains slower than dense and the fresh histogram baseline.'
    }
    (OUT/f'{REVUP}_STAGE_PRUNE_CERT_POLICY_AUDIT.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    (OUT/f'{REVUP}_STAGE_PRUNE_CERT_POLICY_AUDIT.md').write_text('# Stage-pruned certified reuse audit — '+REV+'\n\n**Status: '+report['status']+'**\n\n'+report['interpretation']+'\n', encoding='utf-8')
    print(json.dumps({'status':report['status'],'errors':len(errors),'warnings':len(warnings)}, indent=2))
    return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
