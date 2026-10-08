#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = META.get('revision', 'rev0064')
REVUP = REV.upper()
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)
ART_REL = f'artifacts/probe-results/{REVUP}_TRACE_PACKET_VALUE_LAYOUT_ENVELOPE.json'
MAN_REL = f'artifacts/run-manifests/{REVUP}_TRACE_PACKET_VALUE_LAYOUT_ENVELOPE_RUN_MANIFEST.json'
INPUT_REL = f'artifacts/native-inputs/{REVUP}_TRACE_PACKET_VALUE_LAYOUT_ENVELOPE_INPUT.bin'


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
        errors.append('missing trace packet value-layout envelope artifact')
    if not man:
        errors.append('missing trace packet value-layout envelope run manifest')
    if not (ROOT / INPUT_REL).exists():
        errors.append('missing native value-layout input')
    s = art.get('summary', {}) if art else {}
    native = art.get('native_result', {}) if art else {}
    timing = native.get('timing', {}) if native else {}
    acct = native.get('accounting', {}) if native else {}
    support = art.get('oracle_topp96_support', {}) if art else {}
    scope = str(art.get('measurement_scope', '')).lower()
    if art:
        if art.get('revision') != REV:
            errors.append('artifact revision mismatch')
        if art.get('promotion_allowed') is not False or s.get('promotion_allowed') is not False:
            errors.append('value-layout envelope overclaims promotion')
        if art.get('public_pretrained_trace_loaded') is not False or s.get('public_pretrained_trace_loaded') is not False:
            errors.append('value-layout envelope overclaims public/pretrained evidence')
        if art.get('gpu_fused_kernel_measured') is not False or s.get('gpu_fused_kernel_measured') is not False:
            errors.append('value-layout envelope overclaims GPU/fused timing')
        if s.get('qk_score_computation_measured_for_qk_included_paths') is not True:
            errors.append('qk-included paths must measure QK score computation')
        if s.get('oracle_support_upper_bound_measured') is not True:
            errors.append('artifact must expose oracle support upper bound')
        if s.get('oracle_topp96_support_is_promotional') is not False or support.get('support_is_promotional') is not False:
            errors.append('oracle Top-p support must stay non-promotional')
        if support.get('support_is_oracle_upper_bound') is not True or acct.get('oracle_support_supplied') is not True:
            errors.append('oracle support must be explicitly supplied upper bound')
        if acct.get('packed_value_layout_supplied') is not True or acct.get('packed_value_layout_is_promotional') is not False:
            errors.append('packed value layout must be a non-promotional supplied side input')
        if acct.get('qk_dot_fraction_qk_included_sparse') != 1.0:
            errors.append('qk-included sparse paths must still compute all QK scores')
        if acct.get('score_storage_required_for_oracle_support') is not True:
            errors.append('oracle support path must expose score-storage/materialization requirement')
        if float(s.get('oracle_topp96_quality_rate', 0.0)) < 0.99:
            errors.append('oracle Top-p value-layout quality below local bar')
        if not (0.05 < float(s.get('oracle_topp96_mean_selected_fraction', 0.0)) < 0.90):
            errors.append('selected fraction should be sparse but nontrivial')
        required_timing = [
            'dense_qk_online_ms','dense_value_only_ms','mask_scan_sparse_value_only_ms','rank_index_sparse_value_only_ms','sorted_index_sparse_value_only_ms','packed_sparse_value_only_ms','oracle_topp96_qk_included_sorted_ms','oracle_topp96_qk_included_packed_ms','packed_layout_build_ms',
            'mask_scan_sparse_value_only_speedup_vs_dense_value_only','rank_index_sparse_value_only_speedup_vs_dense_value_only','sorted_index_sparse_value_only_speedup_vs_dense_value_only','packed_sparse_value_only_speedup_vs_dense_value_only','oracle_topp96_qk_included_sorted_speedup_vs_dense','oracle_topp96_qk_included_packed_speedup_vs_dense','packed_layout_build_equivalent_replays'
        ]
        for key in required_timing:
            if key not in timing:
                errors.append('native timing missing key: ' + key)
        if float(timing.get('rank_index_sparse_value_only_speedup_vs_dense_value_only', 0.0)) <= float(timing.get('mask_scan_sparse_value_only_speedup_vs_dense_value_only', 0.0)):
            warnings.append('selected-index gather did not beat mask scan; locality/layout hypothesis not supported in this run')
        if float(timing.get('packed_sparse_value_only_speedup_vs_dense_value_only', 0.0)) <= 1.0:
            warnings.append('packed sparse value-only path did not beat dense value-only; value layout does not rescue this trace')
        if float(timing.get('oracle_topp96_qk_included_packed_speedup_vs_dense', 0.0)) > 1.0:
            warnings.append('oracle packed qk-included path clears dense; this is layout headroom, not deployable selector evidence')
        if float(timing.get('packed_layout_build_equivalent_replays', 999.0)) > 2.0:
            warnings.append('packed layout build cost is more than two packed replays; reuse must be justified')
        for phrase in ['oracle upper bound', 'not public/pretrained', 'not gpu', 'not fused', 'not a deployable sparse selector', 'packed layout']:
            if phrase not in scope:
                errors.append('measurement scope missing phrase: ' + phrase)
        blockers = set(s.get('remaining_blockers', []))
        for b in ['actual_public_pretrained_trace_bundle_missing','gpu_fused_attention_kernel_timing_missing','oracle_topp96_support_is_not_deployable_selector','packed_value_layout_is_oracle_side_input','packed_layout_build_cost_not_paid_by_single_query_path','qk_included_sparse_paths_still_compute_all_qk_scores']:
            if b not in blockers:
                errors.append('missing blocker: ' + b)
    if man:
        if man.get('artifact_sha256') != sha256_file(ROOT / ART_REL):
            errors.append('run manifest artifact hash mismatch')
        if man.get('python_source_sha256') != sha256_file(ROOT / 'experiments' / 'trace_packet_value_layout_envelope' / 'trace_packet_value_layout_envelope.py'):
            errors.append('run manifest python source hash mismatch')
        if man.get('source_sha256') != sha256_file(ROOT / 'experiments' / 'trace_packet_value_layout_envelope' / 'trace_packet_value_layout_envelope.cpp'):
            errors.append('run manifest C++ source hash mismatch')
        if man.get('native_input_sha256') != sha256_file(ROOT / INPUT_REL):
            errors.append('run manifest native input hash mismatch')
        if 'packed values' not in str(man.get('claim_boundary', '')).lower():
            errors.append('run manifest claim boundary missing packed-value warning')
    cpp = (ROOT / 'experiments' / 'trace_packet_value_layout_envelope' / 'trace_packet_value_layout_envelope.cpp').read_text(encoding='utf-8')
    for token in ['CTMLTR64', 'packed_sparse_value_only_row', 'oracle_qk_included_packed_row', 'time_packed_build', 'packed_value_layout_is_promotional']:
        if token not in cpp:
            errors.append('native source missing expected token: ' + token)
    py = (ROOT / 'experiments' / 'trace_packet_value_layout_envelope' / 'trace_packet_value_layout_envelope.py').read_text(encoding='utf-8')
    for forbidden in ['public_pretrained_trace_loaded": True', 'gpu_fused_kernel_measured": True', 'promotion_allowed = True']:
        if forbidden in py:
            errors.append('source contains forbidden promotion literal: ' + forbidden)
    report = {
        'project': 'CloudtainerML',
        'revision': REV,
        'report': 'trace_packet_value_layout_envelope_audit',
        'status': 'pass' if not errors else 'fail',
        'promotion_allowed': False,
        'artifact': ART_REL,
        'packed_value_only_speedup_vs_dense_value_only': s.get('packed_value_only_speedup_vs_dense_value_only'),
        'oracle_topp96_qk_included_packed_speedup_vs_dense': s.get('oracle_topp96_qk_included_packed_speedup_vs_dense'),
        'mask_scan_value_only_speedup_vs_dense_value_only': s.get('mask_scan_value_only_speedup_vs_dense_value_only'),
        'oracle_topp96_quality_rate': s.get('oracle_topp96_quality_rate'),
        'packed_layout_build_equivalent_replays': timing.get('packed_layout_build_equivalent_replays'),
        'errors': errors,
        'warnings': warnings,
        'interpretation': 'rev0064 separates mask-scan, selected-index gather, sorted gather, and prepacked selected-value schedules. It can show value-layout headroom, but all exact Top-p support and packed-value paths are oracle/non-deployable upper bounds.',
    }
    (OUT / f'{REVUP}_TRACE_PACKET_VALUE_LAYOUT_ENVELOPE_AUDIT.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    md = [f'# Trace packet value-layout envelope audit — {REV}', '', f'**Status: {report["status"]}**', '', report['interpretation'], '', '## Key metrics', f'- mask-scan value-only speedup vs dense value-only: `{report["mask_scan_value_only_speedup_vs_dense_value_only"]}`', f'- packed value-only speedup vs dense value-only: `{report["packed_value_only_speedup_vs_dense_value_only"]}`', f'- oracle packed QK-included speedup vs dense: `{report["oracle_topp96_qk_included_packed_speedup_vs_dense"]}`', f'- quality rate: `{report["oracle_topp96_quality_rate"]}`', f'- packed layout build equivalent replays: `{report["packed_layout_build_equivalent_replays"]}`']
    if warnings:
        md += ['', '## Warnings', *[f'- {w}' for w in warnings]]
    if errors:
        md += ['', '## Errors', *[f'- {e}' for e in errors]]
    (OUT / f'{REVUP}_TRACE_PACKET_VALUE_LAYOUT_ENVELOPE_AUDIT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'errors': len(errors), 'warnings': len(warnings), 'packed_value_speedup': report['packed_value_only_speedup_vs_dense_value_only'], 'packed_qk_speedup': report['oracle_topp96_qk_included_packed_speedup_vs_dense']}, indent=2))
    return 0 if not errors else 1

if __name__ == '__main__':
    raise SystemExit(main())
