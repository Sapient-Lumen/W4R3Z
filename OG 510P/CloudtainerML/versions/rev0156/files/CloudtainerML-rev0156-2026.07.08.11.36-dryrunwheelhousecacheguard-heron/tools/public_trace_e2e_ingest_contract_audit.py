#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
HISTORICAL_AUDIT = True
ORIGINAL_REV = 'rev0073'
REV = ORIGINAL_REV; REVUP = REV.upper()
ART = ROOT/'artifacts'/'probe-results'/f'{REVUP}_PUBLIC_TRACE_E2E_INGEST_CONTRACT.json'
OUT = ROOT/'artifacts'/'audit'; OUT.mkdir(parents=True, exist_ok=True)

def load(p: Path): return json.loads(p.read_text(encoding='utf-8'))

def main() -> int:
    errors=[]; warnings=[]
    if not ART.exists():
        subprocess.run([sys.executable,'experiments/public_trace_e2e_ingest_contract/public_trace_e2e_ingest_contract.py'], cwd=ROOT, check=False)
    if not ART.exists():
        errors.append('missing '+ART.relative_to(ROOT).as_posix())
        data={}; s={}
    else:
        data=load(ART); s=data.get('summary',{})
    if data:
        if data.get('promotion_allowed') is not False: errors.append('artifact promoted unexpectedly')
        if data.get('public_pretrained_trace_loaded') is not False: errors.append('public pretrained trace loaded unexpectedly')
        if data.get('gpu_fused_kernel_measured') is not False: errors.append('gpu fused timing overclaim')
        if s.get('legacy_manifest_only_contract_would_have_accepted_forged_fixture') is not True: errors.append('negative control did not expose legacy manifest-only loophole')
        if s.get('rev0073_rejected_forged_legacy_fixture_by_npz_self_attestation') is not True: errors.append('forged legacy fixture was not rejected by rev0073 gate')
        if s.get('rev0073_rejected_self_declared_local_fixture') is not True: errors.append('self-declared local fixture was not rejected')
        if s.get('schema_only_external_trace_still_loads_without_public_claim') is not True: errors.append('schema-only external control did not load as non-public external trace')
        if int(s.get('oracle_leakage_rows_total',-1)) != 0: errors.append('oracle leakage rows detected')
        if s.get('public_capture_contract_ready') is not True: errors.append('public capture contract not ready')
        env=data.get('capture_environment',{})
        if not env.get('capture_helper_present'): errors.append('capture helper missing')
        if env.get('transformers',{}).get('available') is True and env.get('cached_model_count_sampled',0) > 0:
            warnings.append('environment may now be able to capture a public trace; run the capture helper instead of treating this as blocked')
        tmpl=data.get('manifest_controls',{}).get('public_pretrained_manifest_template',{}).get('path')
        if not tmpl or not (ROOT/tmpl).exists(): errors.append('provenance template missing')
    report={'project':'CloudtainerML','revision':REV,'report':'public_trace_e2e_ingest_contract_audit','status':'pass' if not errors else 'fail','promotion_allowed':False,'errors':errors,'warnings':warnings,'key_metrics':s,'interpretation':'rev0073 passes if public/pretrained trace promotion requires both a JSON provenance manifest and matching NPZ self-attestation, while schema-valid local fixtures still load only as non-public external traces.'}
    (OUT/f'{REVUP}_PUBLIC_TRACE_E2E_INGEST_CONTRACT_AUDIT.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n', encoding='utf-8')
    (OUT/f'{REVUP}_PUBLIC_TRACE_E2E_INGEST_CONTRACT_AUDIT.md').write_text('# Public trace E2E ingest contract audit — '+REV+'\n\n**Status: '+report['status']+'**\n\n'+report['interpretation']+'\n', encoding='utf-8')
    print(json.dumps({'status':report['status'],'errors':len(errors),'warnings':len(warnings)}, indent=2))
    return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
