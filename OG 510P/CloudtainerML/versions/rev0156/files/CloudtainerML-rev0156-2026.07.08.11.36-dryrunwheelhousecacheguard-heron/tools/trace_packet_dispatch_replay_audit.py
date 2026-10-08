#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = META.get('revision', 'rev0060')
REVUP = REV.upper()
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()

def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))

def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    art_rel = f'artifacts/probe-results/{REVUP}_TRACE_PACKET_DISPATCH_REPLAY.json'
    gate_rel = f'artifacts/probe-results/{REVUP}_TRACE_PACKET_PUBLIC_GATE_EVAL.json'
    man_rel = f'artifacts/run-manifests/{REVUP}_TRACE_PACKET_DISPATCH_REPLAY_RUN_MANIFEST.json'
    src_rel = 'experiments/trace_packet_dispatch_replay/trace_packet_dispatch_replay.py'
    current = [art_rel, gate_rel, man_rel, src_rel]
    missing = [rel for rel in current if not (ROOT / rel).exists()]
    errors += ['missing rev0060 trace replay artifact/source: ' + rel for rel in missing]
    art = load(art_rel) if (ROOT / art_rel).exists() else {}
    gate = load(gate_rel) if (ROOT / gate_rel).exists() else {}
    man = load(man_rel) if (ROOT / man_rel).exists() else {}
    summary = art.get('summary', {}) if art else {}
    packet = art.get('trace_packet', {}) if art else {}
    if art:
        if art.get('promotion_allowed') is not False or summary.get('promotion_allowed') is not False:
            errors.append('trace packet replay overclaims promotion')
        if art.get('public_pretrained_trace_loaded') is not False or summary.get('public_pretrained_trace_loaded') is not False:
            errors.append('trace packet replay overclaims public/pretrained trace evidence')
        if art.get('gpu_kernel_claim') is not False or art.get('gpu_fused_kernel_measured') is not False:
            errors.append('trace packet replay overclaims GPU/fused-kernel evidence')
        scope = str(art.get('measurement_scope', '')).lower()
        if 'not gpu' not in scope or 'not a fused cuda' not in scope or 'not public/pretrained' not in scope:
            errors.append('measurement scope does not fence GPU/public-pretrained claims')
        if summary.get('trace_packet_rows', 0) < 128:
            errors.append('trace packet too small for this replay gate')
        if summary.get('public_pretrained_rows') != 0:
            errors.append('some replay rows claim public/pretrained provenance')
        if summary.get('oracle_leakage_rows') != 0:
            errors.append('oracle leakage detected in trace gate rows')
        if summary.get('strict_materialization_free_sparse_row_count') != 0:
            errors.append('strict materialization-free gate promoted sparse rows')
        if summary.get('materialization_free_sparse_schedule_has_no_learned_trace_speed_win') is not True:
            errors.append('learned trace no-speed-win materialization-free veto missing')
        if summary.get('learned_trace_dispatch_gate_missing_closed') is not True:
            errors.append('learned-trace dispatch gate blocker was not closed')
        if summary.get('public_trace_blocker_closed') is not False:
            errors.append('public trace blocker incorrectly marked closed')
        if summary.get('score_storage_allowed_not_fused_claim') is not True:
            errors.append('materialized score-storage result not fenced off from fused claim')
        storage = art.get('policy_summary', {}).get('score_storage_allowed_cpu_gate', {})
        strict = art.get('policy_summary', {}).get('strict_materialization_free_gate', {})
        if float(storage.get('sparse_row_rate', 0.0)) <= 0.0:
            errors.append('score-storage-allowed gate should expose a nonzero learned-trace sparse opportunity')
        if int(storage.get('materialized_sparse_row_count', 0)) != int(storage.get('sparse_row_count', -1)):
            errors.append('score-storage-allowed sparse rows must all be materialized and non-fused')
        if float(strict.get('sparse_row_rate', 1.0)) != 0.0:
            errors.append('strict no-score-storage sparse rate should be zero')
        if 'qk_schedule_tax_too_high_for_fused_claim' not in strict.get('top_vetoes', []):
            errors.append('strict gate did not expose qk schedule tax veto')
        for b in ['actual_public_pretrained_trace_bundle_missing','gpu_fused_attention_kernel_timing_missing','strict_materialization_free_sparse_schedule_has_no_learned_trace_speed_win']:
            if b not in summary.get('remaining_blockers', []):
                errors.append('missing blocker: ' + b)
        pkt_rel = packet.get('npz')
        pkt_man_rel = packet.get('manifest')
        if pkt_rel and (ROOT / pkt_rel).exists():
            if packet.get('npz_sha256') != sha256_file(ROOT / pkt_rel):
                errors.append('trace packet npz hash mismatch')
        else:
            errors.append('missing trace packet npz')
        if pkt_man_rel and (ROOT / pkt_man_rel).exists():
            if packet.get('manifest_sha256') != sha256_file(ROOT / pkt_man_rel):
                errors.append('trace packet manifest hash mismatch')
            pkt_man = load(pkt_man_rel)
            if pkt_man.get('public_pretrained_trace_loaded') is not False:
                errors.append('trace packet manifest overclaims public/pretrained evidence')
            if 'GPU/fused-kernel timing' not in pkt_man.get('prohibited_claims', []):
                errors.append('trace packet manifest does not prohibit GPU/fused timing claims')
        else:
            errors.append('missing trace packet manifest')
    if gate:
        if gate.get('trace_gate_status') != 'external_npz_loaded_claims_public_pretrained_false':
            errors.append('trace gate status should keep public/pretrained false')
        if gate.get('external_trace_loaded') is not True:
            errors.append('trace gate did not treat packet as external NPZ')
        if gate.get('public_pretrained_trace_loaded') is not False:
            errors.append('trace gate overclaims public/pretrained trace')
        if gate.get('summary', {}).get('oracle_leakage_rows') != 0:
            errors.append('trace gate detected oracle leakage')
    if man and (ROOT / src_rel).exists():
        if man.get('source_sha256') != sha256_file(ROOT / src_rel):
            errors.append('run manifest source hash mismatch')
    report = {
        'project': 'CloudtainerML',
        'revision': REV,
        'report': 'trace_packet_dispatch_replay_audit',
        'status': 'pass' if not errors else 'fail',
        'promotion_allowed': False,
        'current_artifacts': current,
        'missing_current_artifacts': missing,
        'key_metrics': {
            'trace_packet_rows': summary.get('trace_packet_rows'),
            'strict_materialization_free_sparse_row_count': summary.get('strict_materialization_free_sparse_row_count'),
            'score_storage_allowed_sparse_row_rate': summary.get('score_storage_allowed_sparse_row_rate'),
            'public_pretrained_trace_loaded': summary.get('public_pretrained_trace_loaded'),
            'oracle_leakage_rows': summary.get('oracle_leakage_rows'),
        },
        'errors': errors,
        'warnings': warnings,
        'interpretation': 'rev0060 closes the learned-trace dispatch-gate gap with a replayable local trace packet while keeping public/pretrained, GPU, and fused-kernel promotion blocked.',
    }
    (OUT / f'{REVUP}_TRACE_PACKET_DISPATCH_REPLAY_AUDIT.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    md = [f'# Trace packet dispatch replay audit — {REV}', '', f'**Status: {report["status"]}**', '', report['interpretation'], '', '## Key metrics']
    for k, v in report['key_metrics'].items():
        md.append(f'- `{k}`: `{v}`')
    if errors:
        md += ['', '## Errors', *[f'- {e}' for e in errors]]
    (OUT / f'{REVUP}_TRACE_PACKET_DISPATCH_REPLAY_AUDIT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'errors': len(errors), 'warnings': len(warnings)}, indent=2))
    return 0 if not errors else 1

if __name__ == '__main__':
    raise SystemExit(main())
