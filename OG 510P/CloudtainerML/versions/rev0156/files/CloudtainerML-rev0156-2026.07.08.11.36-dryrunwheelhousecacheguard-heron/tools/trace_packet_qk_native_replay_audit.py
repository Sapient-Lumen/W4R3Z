#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = META.get('revision', 'rev0062')
REVUP = REV.upper()
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)
ART_REL = f'artifacts/probe-results/{REVUP}_TRACE_PACKET_QK_NATIVE_REPLAY.json'
MAN_REL = f'artifacts/run-manifests/{REVUP}_TRACE_PACKET_QK_NATIVE_REPLAY_RUN_MANIFEST.json'


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
    art = load(ART_REL) if (ROOT / ART_REL).exists() else {}
    man = load(MAN_REL) if (ROOT / MAN_REL).exists() else {}
    if not art:
        errors.append('missing QK native replay artifact')
    if not man:
        errors.append('missing QK native replay run manifest')
    s = art.get('summary', {}) if art else {}
    native = art.get('native_result', {}) if art else {}
    timing = native.get('timing', {}) if native else {}
    qka = native.get('qk_accounting', {}) if native else {}
    packet_manifest = art.get('trace_packet_manifest', {}) if art else {}
    scope = str(art.get('measurement_scope', '')).lower()
    if art:
        if art.get('promotion_allowed') is not False or s.get('promotion_allowed') is not False:
            errors.append('QK native replay overclaims promotion')
        if art.get('public_pretrained_trace_loaded') is not False or s.get('public_pretrained_trace_loaded') is not False:
            errors.append('QK native replay overclaims public/pretrained evidence')
        if art.get('gpu_kernel_claim') is not False or art.get('gpu_fused_kernel_measured') is not False or s.get('gpu_fused_kernel_measured') is not False:
            errors.append('QK native replay overclaims GPU/fused evidence')
        if art.get('qk_score_computation_measured') is not True or s.get('qk_score_computation_measured') is not True:
            errors.append('QK native replay must explicitly measure QK score construction')
        if art.get('score_storage_required_for_materialized_histogram') is not True or s.get('materialized_score_storage_required') is not True:
            errors.append('materialized histogram must expose score-storage requirement')
        if art.get('streaming_no_score_storage_measured') is not True or s.get('streaming_no_score_storage_measured') is not True:
            errors.append('streaming no-score-storage path must be measured')
        for phrase in ['qk score computation is measured', 'not gpu', 'not fused', 'not public/pretrained', 'stores global scores']:
            if phrase not in scope:
                errors.append('measurement scope missing phrase: ' + phrase)
        if packet_manifest.get('qk_vectors_included') is not True:
            errors.append('trace packet manifest must include Q/K vectors')
        if packet_manifest.get('public_pretrained_trace_loaded') is not False:
            errors.append('trace packet manifest overclaims public/pretrained evidence')
        if int(s.get('trace_packet_rows', 0)) < 128 or s.get('trace_packet_rows') != native.get('rows'):
            errors.append('trace packet row count mismatch or below 128')
        if float(s.get('native_mass_histogram_quality_rate', 0.0)) < 0.99:
            errors.append('materialized QK histogram quality rate below 0.99')
        if not (0.0 < float(s.get('native_mass_histogram_mean_selected_fraction', 0.0)) < 0.9):
            errors.append('selected fraction should be a nontrivial sparse value-read path')
        if float(s.get('native_mass_histogram_speedup_vs_dense_qk_online', 99.0)) >= 1.0:
            errors.append('materialized QK histogram unexpectedly passes speed bar; review before any promotion')
        if float(s.get('streaming_recompute_speedup_vs_dense_qk_online', 99.0)) >= 1.0:
            errors.append('streaming no-score-storage path unexpectedly passes speed bar; review before any promotion')
        if float(qka.get('materialized_histogram_qk_dot_fraction', -1)) != 1.0:
            errors.append('materialized histogram should compute all QK dots in this benchmark')
        if float(qka.get('streaming_recompute_histogram_qk_dot_fraction', 0)) < 3.0:
            errors.append('streaming recompute path should expose multi-pass QK tax')
        if qka.get('materialized_score_storage_required') is not True or qka.get('streaming_score_storage_required') is not False:
            errors.append('QK accounting score-storage flags are inconsistent')
        if s.get('materialized_qk_speed_bar_passed') is not False or s.get('streaming_speed_bar_passed') is not False:
            errors.append('speed bar flags should be false on this local QK trace')
        blockers = set(s.get('remaining_blockers', []))
        for b in ['actual_public_pretrained_trace_bundle_missing','gpu_fused_attention_kernel_timing_missing','strict_materialization_free_sparse_schedule_has_no_qk_replay_speed_win','materialized_sparse_qk_path_requires_global_score_storage','local_tiny_qk_trace_not_public_pretrained_evidence']:
            if b not in blockers:
                errors.append('missing blocker: ' + b)
        if float(timing.get('mass_histogram_speedup_vs_dense_qk_online', -1.0)) != float(s.get('native_mass_histogram_speedup_vs_dense_qk_online', -2.0)):
            errors.append('native timing summary mismatch')
    if man:
        if man.get('artifact_sha256') != sha256_file(ROOT / ART_REL):
            errors.append('run manifest artifact hash mismatch')
        if man.get('source_sha256') != sha256_file(ROOT / 'experiments' / 'trace_packet_qk_native_replay' / 'trace_packet_qk_native_replay.py'):
            errors.append('run manifest python source hash mismatch')
        if man.get('native_source_sha256') != sha256_file(ROOT / 'experiments' / 'trace_packet_qk_native_replay' / 'trace_packet_qk_native_replay.cpp'):
            errors.append('run manifest native source hash mismatch')
    cpp = (ROOT / 'experiments' / 'trace_packet_qk_native_replay' / 'trace_packet_qk_native_replay.cpp').read_text(encoding='utf-8')
    for token in ['CTMLTR62', 'qk_score', 'dense_qk_row', 'materialized_hist_qk_row', 'streaming_recompute_hist_row']:
        if token not in cpp:
            errors.append('native source missing expected token: ' + token)
    py = (ROOT / 'experiments' / 'trace_packet_qk_native_replay' / 'trace_packet_qk_native_replay.py').read_text(encoding='utf-8')
    for f in ['public_pretrained_trace_loaded": True', 'gpu_fused_kernel_measured": True', 'promotion_allowed = True']:
        if f in py:
            errors.append('source contains forbidden promotion literal: ' + f)
    report = {
        'project': 'CloudtainerML',
        'revision': REV,
        'report': 'trace_packet_qk_native_replay_audit',
        'status': 'pass' if not errors else 'fail',
        'promotion_allowed': False,
        'artifact': ART_REL,
        'qk_score_computation_measured': s.get('qk_score_computation_measured'),
        'materialized_qk_speedup_vs_dense': s.get('native_mass_histogram_speedup_vs_dense_qk_online'),
        'streaming_recompute_speedup_vs_dense': s.get('streaming_recompute_speedup_vs_dense_qk_online'),
        'quality_rate': s.get('native_mass_histogram_quality_rate'),
        'selected_fraction': s.get('native_mass_histogram_mean_selected_fraction'),
        'errors': errors,
        'warnings': warnings,
        'interpretation': 'rev0062 measures QK score construction inside the native CPU trace replay. The materialized histogram path remains slower than dense and requires global score storage; the no-score-storage streaming path pays a large QK recompute tax.',
    }
    (OUT / f'{REVUP}_TRACE_PACKET_QK_NATIVE_REPLAY_AUDIT.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    md = [f'# Trace packet QK native replay audit — {REV}', '', f'**Status: {report["status"]}**', '', report['interpretation'], '', '## Key metrics', f'- materialized QK speedup vs dense: `{report["materialized_qk_speedup_vs_dense"]}`', f'- streaming recompute speedup vs dense: `{report["streaming_recompute_speedup_vs_dense"]}`', f'- quality rate: `{report["quality_rate"]}`', f'- selected fraction: `{report["selected_fraction"]}`']
    if errors:
        md += ['', '## Errors', *[f'- {e}' for e in errors]]
    (OUT / f'{REVUP}_TRACE_PACKET_QK_NATIVE_REPLAY_AUDIT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'errors': len(errors), 'materialized_qk_speedup': report['materialized_qk_speedup_vs_dense'], 'streaming_speedup': report['streaming_recompute_speedup_vs_dense']}, indent=2))
    return 0 if not errors else 1

if __name__ == '__main__':
    raise SystemExit(main())
