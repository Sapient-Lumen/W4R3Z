#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = META.get('revision', 'rev0061')
REVUP = REV.upper()
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)
ART_REL = f'artifacts/probe-results/{REVUP}_TRACE_PACKET_NATIVE_REPLAY.json'
MAN_REL = f'artifacts/run-manifests/{REVUP}_TRACE_PACKET_NATIVE_REPLAY_RUN_MANIFEST.json'


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    if not (ROOT / ART_REL).exists():
        errors.append('missing native replay artifact')
        art = {}
    else:
        art = load(ART_REL)
    if not (ROOT / MAN_REL).exists():
        errors.append('missing native replay run manifest')
        man = {}
    else:
        man = load(MAN_REL)
    s = art.get('summary', {}) if art else {}
    native = art.get('native_result', {}) if art else {}
    timing = native.get('timing', {}) if native else {}
    all_rows = native.get('all_rows', {}) if native else {}
    scope = str(art.get('measurement_scope', '')).lower()
    if art:
        if art.get('promotion_allowed') is not False or s.get('promotion_allowed') is not False:
            errors.append('native trace replay overclaims promotion')
        if art.get('public_pretrained_trace_loaded') is not False or s.get('public_pretrained_trace_loaded') is not False:
            errors.append('native trace replay overclaims public/pretrained evidence')
        if art.get('gpu_kernel_claim') is not False or art.get('gpu_fused_kernel_measured') is not False or s.get('gpu_fused_kernel_measured') is not False:
            errors.append('native trace replay overclaims GPU/fused kernel timing')
        if art.get('qk_score_computation_measured') is not False or s.get('qk_score_computation_measured') is not False:
            errors.append('native trace replay claims QK computation was measured')
        if art.get('score_storage_required') is not True or s.get('score_storage_required') is not True:
            errors.append('native trace replay must expose score-storage requirement')
        for phrase in ['materialized-score', 'not qk', 'not gpu', 'not fused', 'not public/pretrained']:
            if phrase not in scope:
                errors.append('measurement scope missing phrase: ' + phrase)
        if s.get('trace_packet_rows') != native.get('rows') or int(s.get('trace_packet_rows', 0)) < 128:
            errors.append('trace packet row count mismatch or below threshold')
        if float(s.get('native_mass_histogram_quality_rate', 0.0)) < 0.999:
            errors.append('native histogram quality rate below expected bar')
        if float(all_rows.get('quality_rate', 0.0)) < 0.999:
            errors.append('native all-row quality rate below expected bar')
        native_speed = float(s.get('native_mass_histogram_speedup_vs_dense_score_consumption', -1.0))
        proxy_speed = s.get('rev0060_proxy_speedup_vs_dense_cost_proxy')
        if proxy_speed is None or float(proxy_speed) <= 1.0:
            errors.append('previous proxy speedup was not present or not >1; cannot test proxy veto')
        if native_speed >= 1.0:
            errors.append('native score-consumption path unexpectedly passes speed bar; review audit thresholds before promotion')
        if proxy_speed is not None and native_speed >= float(proxy_speed):
            errors.append('native result did not reduce proxy speedup; proxy-veto finding absent')
        if s.get('native_score_consumption_speed_bar_passed') is not False:
            errors.append('native score-consumption speed bar should be false for this packet')
        if s.get('fused_or_qk_blocker_closed') is not False:
            errors.append('fused/QK blocker was incorrectly closed')
        blockers = set(s.get('remaining_blockers', []))
        for b in ['actual_public_pretrained_trace_bundle_missing','qk_score_computation_not_measured_for_trace_packet','gpu_fused_attention_kernel_timing_missing','materialized_sparse_cpu_path_requires_global_score_storage']:
            if b not in blockers:
                errors.append('missing blocker: ' + b)
        if float(s.get('native_mass_histogram_mean_selected_fraction', 0.0)) <= 0.0 or float(s.get('native_mass_histogram_mean_selected_fraction', 1.1)) >= 1.0:
            errors.append('mean selected fraction should be a genuine partial sparse value-read path')
        if float(timing.get('mass_histogram_speedup_vs_dense_score_consumption', -1.0)) != float(s.get('native_mass_histogram_speedup_vs_dense_score_consumption', -2.0)):
            errors.append('native timing summary mismatch')
    if man:
        if man.get('artifact_sha256') != sha256_file(ROOT / ART_REL):
            errors.append('run manifest artifact hash mismatch')
        if man.get('source_sha256') != sha256_file(ROOT / 'experiments' / 'trace_packet_native_replay' / 'trace_packet_native_replay.py'):
            errors.append('run manifest python source hash mismatch')
        if man.get('native_source_sha256') != sha256_file(ROOT / 'experiments' / 'trace_packet_native_replay' / 'trace_packet_native_replay.cpp'):
            errors.append('run manifest native source hash mismatch')
    cpp = (ROOT / 'experiments' / 'trace_packet_native_replay' / 'trace_packet_native_replay.cpp').read_text(encoding='utf-8')
    if 'CTMLTR61' not in cpp or 'hist_row' not in cpp or 'dense_row' not in cpp:
        errors.append('native source missing expected dense/histogram replay functions')
    py = (ROOT / 'experiments' / 'trace_packet_native_replay' / 'trace_packet_native_replay.py').read_text(encoding='utf-8')
    forbidden = ['public_pretrained_trace_loaded": True', 'gpu_fused_kernel_measured": True', 'qk_score_computation_measured": True']
    for f in forbidden:
        if f in py:
            errors.append('source contains forbidden promotion literal: ' + f)
    report = {
        'project': 'CloudtainerML',
        'revision': REV,
        'report': 'trace_packet_native_replay_audit',
        'status': 'pass' if not errors else 'fail',
        'promotion_allowed': False,
        'artifact': ART_REL,
        'native_speedup_vs_dense_score_consumption': s.get('native_mass_histogram_speedup_vs_dense_score_consumption'),
        'rev0060_proxy_speedup': s.get('rev0060_proxy_speedup_vs_dense_cost_proxy'),
        'native_minus_proxy_speedup': s.get('native_minus_proxy_speedup'),
        'quality_rate': s.get('native_mass_histogram_quality_rate'),
        'selected_fraction': s.get('native_mass_histogram_mean_selected_fraction'),
        'errors': errors,
        'warnings': warnings,
        'interpretation': 'rev0061 measures the learned trace packet through native materialized-score CPU loops and vetoes proxy-only sparse promotion because the measured histogram score-consumption path is slower than dense on this packet.',
    }
    (OUT / f'{REVUP}_TRACE_PACKET_NATIVE_REPLAY_AUDIT.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    md = [f'# Trace packet native replay audit — {REV}', '', f'**Status: {report["status"]}**', '', report['interpretation'], '', '## Key metrics', f'- native speedup vs dense score consumption: `{report["native_speedup_vs_dense_score_consumption"]}`', f'- rev0060 proxy speedup: `{report["rev0060_proxy_speedup"]}`', f'- quality rate: `{report["quality_rate"]}`', f'- mean selected fraction: `{report["selected_fraction"]}`']
    if errors:
        md += ['', '## Errors', *[f'- {e}' for e in errors]]
    (OUT / f'{REVUP}_TRACE_PACKET_NATIVE_REPLAY_AUDIT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'errors': len(errors), 'native_speedup': report['native_speedup_vs_dense_score_consumption']}, indent=2))
    return 0 if not errors else 1

if __name__ == '__main__':
    raise SystemExit(main())
