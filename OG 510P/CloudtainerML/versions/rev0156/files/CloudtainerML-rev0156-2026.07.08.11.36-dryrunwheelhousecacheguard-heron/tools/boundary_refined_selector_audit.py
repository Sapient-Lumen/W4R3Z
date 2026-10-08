#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = META.get('revision', 'rev0068')
REVUP = REV.upper()
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)
ART_REL = f'artifacts/probe-results/{REVUP}_BOUNDARY_REFINED_SELECTOR_LAYOUT.json'


def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    if not (ROOT / ART_REL).exists():
        errors.append('missing artifact: ' + ART_REL)
        art = {}
    else:
        art = load(ART_REL)
    s = art.get('summary', {}) if art else {}
    native = art.get('native_result', {}) if art else {}
    timing = native.get('timing', {}) if native else {}
    if art:
        if art.get('revision') != REV:
            errors.append('artifact revision mismatch')
        if art.get('promotion_allowed') is not False or s.get('promotion_allowed') is not False:
            errors.append('promotion overclaim')
        if art.get('public_pretrained_trace_loaded') is not False or s.get('public_pretrained_trace_loaded') is not False:
            errors.append('public/pretrained trace overclaim')
        if art.get('gpu_fused_kernel_measured') is not False or s.get('gpu_fused_kernel_measured') is not False:
            errors.append('GPU/fused timing overclaim')
        if s.get('selector_layout_overhead_paid_in_timed_loop') is not True:
            errors.append('selector/layout overhead was not marked as paid')
        if s.get('selectors_use_values_or_dense_outputs') is not False:
            errors.append('selector leakage flag wrong')
        if float(s.get('qk_dot_fraction_deployable_sparse', 0.0)) != 1.0:
            errors.append('rev0068 must admit all deployable selectors still compute full QK')
        if s.get('row_local_score_prob_storage_required') is not True:
            errors.append('row-local score/prob storage requirement missing')
        if s.get('boundary_bucket_sort_paid') is not True:
            errors.append('boundary bucket sort not paid/declared')
        if float(s.get('refined_hist_quality_rate', 0.0)) < 0.99:
            errors.append('refined histogram quality below bar')
        if float(s.get('coarse_hist_quality_rate', 0.0)) < 0.99:
            errors.append('coarse histogram quality below bar')
        if float(s.get('refined_hist_mean_selected_fraction', 1.0)) >= float(s.get('coarse_hist_mean_selected_fraction', 1.0)) - 0.10:
            errors.append('boundary refinement did not materially reduce selected fraction')
        if s.get('refined_reduces_histogram_overshoot') is not True:
            errors.append('refinement did not reduce overshoot against exact Top-p')
        if abs(float(s.get('refined_minus_exact_mean_selected_count', 999.0))) > 1e-9:
            errors.append('refined selector should match exact Top-p support count on this trace/bucket setup')
        if float(s.get('refined_hist_speedup_vs_dense', 99.0)) >= 1.0:
            warnings.append('refined histogram is locally faster than dense; still fenced by full-QK/materialization blockers')
        if float(s.get('refined_hist_speedup_vs_dense', 0.0)) <= float(s.get('exact_sort_speedup_vs_dense', 0.0)):
            errors.append('boundary refinement should be faster than exact full sort')
        for blocker in [
            'all_deployable_selectors_still_compute_full_qk_scores',
            'row_local_score_storage_or_prob_storage_still_required',
            'boundary_refinement_overhead_not_a_fused_kernel_win',
            'no_deployable_score_path_sparse_win_measured',
        ]:
            if blocker not in s.get('remaining_blockers', []):
                errors.append('missing blocker: ' + blocker)
        scope = art.get('measurement_scope', '').lower()
        for phrase in ['boundary bucket sort paid', 'all deployable paths compute full qk', 'not public/pretrained', 'not gpu', 'not fused']:
            if phrase not in scope:
                errors.append('measurement_scope missing phrase: ' + phrase)
    for rel in [
        'experiments/trace_packet_boundary_refined_selector/trace_packet_boundary_refined_selector.py',
        'experiments/trace_packet_boundary_refined_selector/trace_packet_boundary_refined_selector.cpp',
    ]:
        if not (ROOT / rel).exists():
            errors.append('missing source: ' + rel)
    report = {
        'project': 'CloudtainerML',
        'revision': REV,
        'report': 'boundary_refined_selector_audit',
        'status': 'pass' if not errors else 'fail',
        'promotion_allowed': False,
        'artifact': ART_REL,
        'key_metrics': {
            'coarse_hist_mean_selected_fraction': s.get('coarse_hist_mean_selected_fraction'),
            'refined_hist_mean_selected_fraction': s.get('refined_hist_mean_selected_fraction'),
            'exact_sort_mean_selected_fraction': s.get('exact_sort_mean_selected_fraction'),
            'coarse_minus_exact_mean_selected_count': s.get('coarse_minus_exact_mean_selected_count'),
            'refined_minus_exact_mean_selected_count': s.get('refined_minus_exact_mean_selected_count'),
            'refined_hist_speedup_vs_dense': s.get('refined_hist_speedup_vs_dense'),
            'exact_sort_speedup_vs_dense': s.get('exact_sort_speedup_vs_dense'),
            'qk_only_fraction_of_dense': timing.get('qk_only_fraction_of_dense'),
        },
        'errors': errors,
        'warnings': warnings,
        'interpretation': 'Boundary-bin refinement fixes the coarse histogram over-selection and is cheaper than exact full sort, but it is still slower than dense on this CPU trace and remains blocked because every deployable path computes all QK scores and stores row-local probabilities.',
    }
    (OUT / f'{REVUP}_BOUNDARY_REFINED_SELECTOR_AUDIT.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    md = [f'# Boundary-refined selector audit — {REV}', '', f"**Status: {report['status']}**", '', report['interpretation'], '', '## Key metrics']
    md += [f'- `{k}`: {v}' for k, v in report['key_metrics'].items()]
    if errors:
        md += ['', '## Errors'] + [f'- {e}' for e in errors]
    if warnings:
        md += ['', '## Warnings'] + [f'- {w}' for w in warnings]
    (OUT / f'{REVUP}_BOUNDARY_REFINED_SELECTOR_AUDIT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'errors': len(errors), 'warnings': len(warnings)}, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
