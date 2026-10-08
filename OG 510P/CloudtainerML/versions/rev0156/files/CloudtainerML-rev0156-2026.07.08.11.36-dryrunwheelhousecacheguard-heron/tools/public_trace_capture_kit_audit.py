#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
HISTORICAL_AUDIT = True
ORIGINAL_REV = 'rev0074'
REV = ORIGINAL_REV; REVUP = REV.upper()
ART = ROOT/'artifacts'/'probe-results'/f'{REVUP}_PUBLIC_TRACE_CAPTURE_KIT.json'
OUT = ROOT/'artifacts'/'audit'; OUT.mkdir(parents=True, exist_ok=True)

def load(p: Path): return json.loads(p.read_text(encoding='utf-8'))

def main() -> int:
    errors=[]; warnings=[]
    if not ART.exists():
        subprocess.run([sys.executable,'experiments/public_trace_capture_kit/public_trace_capture_kit.py'], cwd=ROOT, check=False)
    if not ART.exists():
        errors.append('missing '+ART.relative_to(ROOT).as_posix()); art={}; s={}
    else:
        art=load(ART); s=art.get('summary',{})
    if art:
        if art.get('promotion_allowed') is not False: errors.append('capture-kit artifact promoted unexpectedly')
        if art.get('public_pretrained_trace_loaded') is not False: errors.append('local capture-kit dry-run overclaims public/pretrained trace')
        if art.get('gpu_fused_kernel_measured') is not False: errors.append('GPU/fused timing overclaim')
        if s.get('public_replay_adapter_ready') is not True: errors.append('public replay adapter did not dry-run successfully')
        if s.get('external_trace_loaded') is not True: errors.append('external trace dry-run did not load')
        if int(s.get('native_qk_replay_rows',0)) <= 0: errors.append('native QK replay did not process rows')
        if float(s.get('native_mass_histogram_quality_rate',0.0)) < 0.999: errors.append('dry-run native quality unexpectedly below bar')
        if int(s.get('oracle_leakage_rows',-1)) != 0: errors.append('oracle leakage rows detected')
        gate=art.get('gate_result',{})
        if gate.get('public_pretrained_trace_loaded') is not False: errors.append('gate overclaims public/pretrained dry-run')
        if gate.get('accepted_as_public_pretrained_trace') is not False: errors.append('gate accepted non-public dry-run as public')
        if gate.get('npz_metadata_status') != 'metadata_self_attestation_present': errors.append('dry-run fixture self-attestation missing')
        if not gate.get('npz_red_flag_terms'): errors.append('dry-run fixture red flags not surfaced')
        for rel in art.get('capture_kit_files',{}):
            if not (ROOT/rel).exists(): errors.append('missing capture-kit file '+rel)
        native=art.get('native_result',{})
        if native.get('rows') != s.get('native_qk_replay_rows'): errors.append('native rows summary mismatch')
        if native.get('qk_accounting',{}).get('materialized_histogram_qk_dot_fraction') != 1:
            errors.append('materialized histogram QK accounting should remain dense-score fraction 1')
        env=art.get('environment',{})
        if env.get('transformers',{}).get('available') is True and env.get('cached_model_count_sampled',0) > 0:
            warnings.append('environment may be able to capture public traces; run capture kit with --claim-public after provenance review')
    report={
        'project':'CloudtainerML','revision':REV,'report':'public_trace_capture_kit_audit',
        'status':'pass' if not errors else 'fail','promotion_allowed':False,
        'errors':errors,'warnings':warnings,'key_metrics':s,
        'interpretation':'rev0074 passes if the portable capture/replay kit exists, the non-public dry-run is replayable natively, and no local fixture is promoted as public/pretrained evidence.'
    }
    (OUT/f'{REVUP}_PUBLIC_TRACE_CAPTURE_KIT_AUDIT.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n', encoding='utf-8')
    (OUT/f'{REVUP}_PUBLIC_TRACE_CAPTURE_KIT_AUDIT.md').write_text('# Public trace capture kit audit — '+REV+'\n\n**Status: '+report['status']+'**\n\n'+report['interpretation']+'\n', encoding='utf-8')
    print(json.dumps({'status':report['status'],'errors':len(errors),'warnings':len(warnings)}, indent=2))
    return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
