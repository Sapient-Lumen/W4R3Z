#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = META.get('revision', 'rev0065')
REVUP = REV.upper()
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)
ART_REL = f'artifacts/probe-results/{REVUP}_DEPLOYABLE_SELECTOR_LAYOUT_OVERHEAD.json'
MAN_REL = f'artifacts/run-manifests/{REVUP}_DEPLOYABLE_SELECTOR_LAYOUT_OVERHEAD_RUN_MANIFEST.json'
INPUT_REL = f'artifacts/native-inputs/{REVUP}_DEPLOYABLE_SELECTOR_LAYOUT_OVERHEAD_INPUT.bin'
PY_SRC_REL = 'experiments/trace_packet_deployable_selector_layout/trace_packet_deployable_selector_layout.py'
CPP_SRC_REL = 'experiments/trace_packet_deployable_selector_layout/trace_packet_deployable_selector_layout.cpp'


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
    for rel in [ART_REL, MAN_REL, INPUT_REL, PY_SRC_REL, CPP_SRC_REL]:
        if not (ROOT / rel).exists():
            errors.append('missing required file: ' + rel)
    art = load(ART_REL) if (ROOT / ART_REL).exists() else {}
    man = load(MAN_REL) if (ROOT / MAN_REL).exists() else {}
    s = art.get('summary', {}) if art else {}
    native = art.get('native_result', {}) if art else {}
    acct = native.get('accounting', {}) if native else {}
    timing = native.get('timing', {}) if native else {}
    if art:
        if art.get('revision') != REV:
            errors.append('artifact revision mismatch')
        if art.get('promotion_allowed') is not False or s.get('promotion_allowed') is not False:
            errors.append('artifact overclaims promotion')
        if art.get('public_pretrained_trace_loaded') is not False or s.get('public_pretrained_trace_loaded') is not False:
            errors.append('artifact overclaims public/pretrained evidence')
        if art.get('gpu_fused_kernel_measured') is not False or s.get('gpu_fused_kernel_measured') is not False:
            errors.append('artifact overclaims GPU/fused evidence')
        if s.get('selector_layout_overhead_paid_in_timed_loop') is not True or acct.get('selector_layout_cost_paid_in_timed_loop') is not True:
            errors.append('selector/layout overhead must be paid in timed loop')
        if s.get('selectors_use_values_or_dense_outputs') is not False:
            errors.append('selectors must not use values or dense outputs')
        if acct.get('selectors_use_values') is not False or acct.get('selectors_use_dense_outputs') is not False:
            errors.append('native accounting says selectors use V/dense outputs')
        if s.get('qk_score_computation_measured') is not True:
            errors.append('QK computation must be measured')
        if acct.get('qk_dot_fraction_deployable_sparse') != 1.0 or s.get('qk_dot_fraction_deployable_sparse') != 1.0:
            errors.append('deployable selector-layout paths must expose that all QK dots are still computed')
        if acct.get('packed_layout_constructed_per_query') is not True or acct.get('index_layout_constructed_per_query') is not True:
            errors.append('index and packed layout construction must be per-query, not supplied')
        if acct.get('row_local_score_prob_storage_required') is not True:
            errors.append('artifact must expose row-local score/prob storage requirement')
        if acct.get('global_score_storage_required') is not False:
            errors.append('artifact should not overclaim global score storage when only row-local storage is used')
        if s.get('deployable_promoted_paths') not in ([], None):
            errors.append('no deployable paths should be promoted while QK fraction is 1.0')
        for key in ['hist_index_quality_rate','hist_packed_quality_rate','exact_sort_index_quality_rate','exact_sort_packed_quality_rate']:
            if float(s.get(key, 0.0)) < 0.99:
                errors.append('quality below bar: ' + key)
        for key in ['hist_index_mean_selected_fraction','exact_sort_index_mean_selected_fraction']:
            if not (0.05 < float(s.get(key, 0.0)) < 0.95):
                errors.append('selected fraction out of useful range: ' + key)
        if float(s.get('hist_index_speedup_vs_dense', 0.0)) >= 1.0:
            warnings.append('histogram index path clears dense locally; still non-promotional because all QK dots are computed')
        else:
            warnings.append('histogram index path is slower than dense once selector/index construction is paid')
        if float(s.get('hist_packed_speedup_vs_dense', 0.0)) < float(s.get('hist_index_speedup_vs_dense', 0.0)):
            warnings.append('per-query packed layout is slower than selected-index gather; rev0064 packed headroom required supplied/reused layout')
        if float(s.get('exact_sort_index_speedup_vs_dense', 0.0)) < float(s.get('hist_index_speedup_vs_dense', 0.0)):
            warnings.append('exact-sort Top-p selector is much more expensive than histogram selection despite selecting fewer values')
        scope = str(art.get('measurement_scope', '')).lower()
        for phrase in ['selector and selected-index/packed layout construction are paid', 'not public/pretrained', 'not gpu', 'not fused', 'all qk dots are still computed']:
            if phrase not in scope:
                errors.append('measurement scope missing phrase: ' + phrase)
        blockers = set(s.get('remaining_blockers', []))
        for b in ['actual_public_pretrained_trace_bundle_missing','gpu_fused_attention_kernel_timing_missing','all_deployable_selector_layout_paths_still_compute_all_qk_scores','materialized_or_row_local_score_prob_storage_required_for_selector','no_score_path_sparse_win_measured','fused_kernel_layout_generation_not_measured']:
            if b not in blockers:
                errors.append('missing blocker: ' + b)
        for key in ['dense_qk_online_ms','qk_only_ms','hist_index_qk_included_ms','hist_packed_qk_included_ms','exact_sort_index_qk_included_ms','exact_sort_packed_qk_included_ms']:
            if key not in timing:
                errors.append('missing timing key: ' + key)
    if man:
        if man.get('artifact_sha256') != sha256_file(ROOT / ART_REL):
            errors.append('run manifest artifact hash mismatch')
        if man.get('python_source_sha256') != sha256_file(ROOT / PY_SRC_REL):
            errors.append('run manifest python source hash mismatch')
        if man.get('source_sha256') != sha256_file(ROOT / CPP_SRC_REL):
            errors.append('run manifest C++ source hash mismatch')
        if man.get('native_input_sha256') != sha256_file(ROOT / INPUT_REL):
            errors.append('run manifest native input hash mismatch')
        boundary = str(man.get('claim_boundary', '')).lower()
        for phrase in ['paid in-loop', 'q/k scores', 'not gpu', 'not fused', 'not score-path sparse']:
            if phrase not in boundary:
                errors.append('run manifest claim boundary missing phrase: ' + phrase)
    cpp = (ROOT / CPP_SRC_REL).read_text(encoding='utf-8') if (ROOT / CPP_SRC_REL).exists() else ''
    for token in ['CTMLTR65', 'histogram_mass_select', 'exact_sort_topp_select', 'packed_layout_constructed_per_query', 'qk_dot_fraction_deployable_sparse']:
        if token not in cpp:
            errors.append('native source missing expected token: ' + token)
    py = (ROOT / PY_SRC_REL).read_text(encoding='utf-8') if (ROOT / PY_SRC_REL).exists() else ''
    for forbidden in ['public_pretrained_trace_loaded": True', 'gpu_fused_kernel_measured": True', 'promotion_allowed = True']:
        if forbidden in py:
            errors.append('source contains forbidden promotion literal: ' + forbidden)
    report = {
        'project': 'CloudtainerML',
        'revision': REV,
        'report': 'deployable_selector_layout_audit',
        'status': 'pass' if not errors else 'fail',
        'promotion_allowed': False,
        'artifact': ART_REL,
        'key_metrics': {
            'hist_index_speedup_vs_dense': s.get('hist_index_speedup_vs_dense'),
            'hist_index_quality_rate': s.get('hist_index_quality_rate'),
            'hist_index_mean_selected_fraction': s.get('hist_index_mean_selected_fraction'),
            'hist_packed_speedup_vs_dense': s.get('hist_packed_speedup_vs_dense'),
            'exact_sort_index_speedup_vs_dense': s.get('exact_sort_index_speedup_vs_dense'),
            'qk_only_fraction_of_dense_time': s.get('qk_only_fraction_of_dense_time'),
            'best_deployable_speedup_vs_dense': s.get('best_deployable_speedup_vs_dense'),
        },
        'errors': errors,
        'warnings': warnings,
        'interpretation': 'rev0065 pays score-only selector and selected-layout construction inside native replay. It tests whether rev0064 value-layout headroom survives without oracle support/packed side inputs while preserving all public/pretrained, GPU/fused, and score-path blockers.',
    }
    (OUT / f'{REVUP}_DEPLOYABLE_SELECTOR_LAYOUT_AUDIT.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    md = [f'# Deployable selector-layout audit — {REV}', '', f'**Status: {report["status"]}**', '', report['interpretation'], '', '## Key metrics']
    for k, v in report['key_metrics'].items():
        md.append(f'- {k}: `{v}`')
    if warnings:
        md += ['', '## Warnings', *[f'- {w}' for w in warnings]]
    if errors:
        md += ['', '## Errors', *[f'- {e}' for e in errors]]
    (OUT / f'{REVUP}_DEPLOYABLE_SELECTOR_LAYOUT_AUDIT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'errors': len(errors), 'warnings': len(warnings), 'hist_index_speedup': s.get('hist_index_speedup_vs_dense'), 'best_speedup': s.get('best_deployable_speedup_vs_dense')}, indent=2))
    return 0 if not errors else 1

if __name__ == '__main__':
    raise SystemExit(main())
