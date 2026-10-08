#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = META.get('revision', 'rev0063')
REVUP = REV.upper()
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)
ART_REL = f'artifacts/probe-results/{REVUP}_TRACE_PACKET_SPEED_ENVELOPE.json'
MAN_REL = f'artifacts/run-manifests/{REVUP}_TRACE_PACKET_SPEED_ENVELOPE_RUN_MANIFEST.json'
INPUT_REL = f'artifacts/native-inputs/{REVUP}_TRACE_PACKET_SPEED_ENVELOPE_INPUT.bin'


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
        errors.append('missing trace packet speed envelope artifact')
    if not man:
        errors.append('missing trace packet speed envelope run manifest')
    if not (ROOT / INPUT_REL).exists():
        errors.append('missing native speed-envelope input')
    s = art.get('summary', {}) if art else {}
    native = art.get('native_result', {}) if art else {}
    timing = native.get('timing', {}) if native else {}
    acct = native.get('accounting', {}) if native else {}
    oracle = art.get('oracle_topp96_mask', {}) if art else {}
    scope = str(art.get('measurement_scope', '')).lower()
    if art:
        if art.get('revision') != REV:
            errors.append('artifact revision mismatch')
        if art.get('promotion_allowed') is not False or s.get('promotion_allowed') is not False:
            errors.append('speed envelope overclaims promotion')
        if art.get('public_pretrained_trace_loaded') is not False or s.get('public_pretrained_trace_loaded') is not False:
            errors.append('speed envelope overclaims public/pretrained evidence')
        if art.get('gpu_fused_kernel_measured') is not False or s.get('gpu_fused_kernel_measured') is not False:
            errors.append('speed envelope overclaims GPU/fused timing')
        if s.get('qk_score_computation_measured') is not True:
            errors.append('speed envelope must measure QK score computation')
        if s.get('oracle_selector_upper_bound_measured') is not True:
            errors.append('speed envelope must mark oracle/free-selector upper bound')
        if s.get('oracle_topp96_mask_is_promotional') is not False or oracle.get('mask_is_promotional') is not False:
            errors.append('oracle Top-p mask must be non-promotional')
        if oracle.get('mask_is_oracle_upper_bound') is not True or acct.get('oracle_mask_supplied') is not True:
            errors.append('oracle Top-p mask must be explicitly identified as supplied upper bound')
        if float(s.get('oracle_topp96_quality_rate', 0.0)) < 0.99:
            errors.append('oracle Top-p envelope should meet the local quality bar')
        if not (0.05 < float(s.get('oracle_topp96_mean_selected_fraction', 0.0)) < 0.90):
            errors.append('oracle selected fraction should be nontrivial and not near-dense')
        for key in ['dense_qk_online_ms','qk_scores_only_ms','dense_value_only_ms','oracle_topp96_value_only_ms','oracle_topp96_qk_included_ms','oracle_topp96_qk_included_speedup_vs_dense','oracle_topp96_value_only_speedup_vs_dense_value_only']:
            if key not in timing:
                errors.append('native timing missing key: ' + key)
        if acct.get('qk_dot_fraction_oracle_topp96_qk_included') != 1.0:
            errors.append('oracle qk-included path must still account for all QK dots')
        if acct.get('selector_cost_oracle_topp96_qk_included') != 0.0:
            errors.append('oracle selector path should declare zero selector cost by construction')
        if acct.get('score_storage_required_for_oracle_qk_included') is not True:
            errors.append('oracle qk-included path must expose score storage/materialization requirement')
        for phrase in ['oracle upper bound', 'not public/pretrained', 'not gpu', 'not fused', 'not deployable sparse selector']:
            if phrase not in scope:
                errors.append('measurement scope missing phrase: ' + phrase)
        if float(timing.get('oracle_topp96_qk_included_speedup_vs_dense', 0.0)) > 1.0:
            warnings.append('oracle/free-selector qk-included path clears dense in this noisy CPU run; this is headroom, not a deployable selector result')
        if float(timing.get('oracle_topp96_value_only_speedup_vs_dense_value_only', 0.0)) < 1.0:
            warnings.append('sparse value-only accumulation is slower than dense value-only here; branch/gather overhead remains material')
        blockers = set(s.get('remaining_blockers', []))
        for b in ['actual_public_pretrained_trace_bundle_missing','gpu_fused_attention_kernel_timing_missing','oracle_topp96_mask_is_not_deployable_selector','materialized_sparse_paths_still_compute_all_qk_scores','strict_materialization_free_sparse_schedule_has_no_measured_speed_win']:
            if b not in blockers:
                errors.append('missing blocker: ' + b)
    if man:
        if man.get('artifact_sha256') != sha256_file(ROOT / ART_REL):
            errors.append('run manifest artifact hash mismatch')
        if man.get('python_source_sha256') != sha256_file(ROOT / 'experiments' / 'trace_packet_speed_envelope' / 'trace_packet_speed_envelope.py'):
            errors.append('run manifest python source hash mismatch')
        if man.get('source_sha256') != sha256_file(ROOT / 'experiments' / 'trace_packet_speed_envelope' / 'trace_packet_speed_envelope.cpp'):
            errors.append('run manifest C++ source hash mismatch')
        if man.get('native_input_sha256') != sha256_file(ROOT / INPUT_REL):
            errors.append('run manifest native input hash mismatch')
        if 'not a deployable selector' not in str(man.get('claim_boundary', '')).lower():
            errors.append('run manifest claim boundary missing deployability warning')
    cpp = (ROOT / 'experiments' / 'trace_packet_speed_envelope' / 'trace_packet_speed_envelope.cpp').read_text(encoding='utf-8')
    for token in ['CTMLTR63', 'oracle_topp96_qk_included_row', 'qk_scores_only_row', 'dense_value_only_row', 'selector_cost_oracle_topp96_qk_included']:
        if token not in cpp:
            errors.append('native source missing expected token: ' + token)
    py = (ROOT / 'experiments' / 'trace_packet_speed_envelope' / 'trace_packet_speed_envelope.py').read_text(encoding='utf-8')
    for forbidden in ['public_pretrained_trace_loaded": True', 'gpu_fused_kernel_measured": True', 'promotion_allowed = True']:
        if forbidden in py:
            errors.append('source contains forbidden promotion literal: ' + forbidden)
    report = {
        'project': 'CloudtainerML',
        'revision': REV,
        'report': 'trace_packet_speed_envelope_audit',
        'status': 'pass' if not errors else 'fail',
        'promotion_allowed': False,
        'artifact': ART_REL,
        'oracle_topp96_qk_included_speedup_vs_dense': s.get('oracle_topp96_qk_included_speedup_vs_dense'),
        'oracle_topp96_value_only_speedup_vs_dense_value_only': s.get('oracle_topp96_value_only_speedup_vs_dense_value_only'),
        'oracle_topp96_quality_rate': s.get('oracle_topp96_quality_rate'),
        'oracle_topp96_selected_fraction': s.get('oracle_topp96_mean_selected_fraction'),
        'errors': errors,
        'warnings': warnings,
        'interpretation': 'rev0063 measures an oracle/free-selector sparse speed envelope. It can show headroom, but cannot promote the mechanism because the Top-p support is supplied from full-score oracle information and all QK scores are still computed.',
    }
    (OUT / f'{REVUP}_TRACE_PACKET_SPEED_ENVELOPE_AUDIT.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    md = [f'# Trace packet speed envelope audit — {REV}', '', f'**Status: {report["status"]}**', '', report['interpretation'], '', '## Key metrics', f'- oracle Top-p 0.96 QK-included speedup vs dense: `{report["oracle_topp96_qk_included_speedup_vs_dense"]}`', f'- oracle Top-p 0.96 value-only speedup vs dense value-only: `{report["oracle_topp96_value_only_speedup_vs_dense_value_only"]}`', f'- quality rate: `{report["oracle_topp96_quality_rate"]}`', f'- selected fraction: `{report["oracle_topp96_selected_fraction"]}`']
    if warnings:
        md += ['', '## Warnings', *[f'- {w}' for w in warnings]]
    if errors:
        md += ['', '## Errors', *[f'- {e}' for e in errors]]
    (OUT / f'{REVUP}_TRACE_PACKET_SPEED_ENVELOPE_AUDIT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'errors': len(errors), 'warnings': len(warnings), 'oracle_qk_speedup': report['oracle_topp96_qk_included_speedup_vs_dense']}, indent=2))
    return 0 if not errors else 1

if __name__ == '__main__':
    raise SystemExit(main())
