#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = META.get('revision', 'rev0043')
REVUP = REV.upper()
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)
ART = ROOT / 'artifacts' / 'probe-results' / f'{REVUP}_ATTENTION_ROW_COMPILER_BENCHMARK.json'

REQUIRED_ROW_FIELDS = {
    'attention_rel_l2_error', 'attention_l2_error', 'output_cosine',
    'mass_retained', 'dense_attention_output_norm', 'topk_hit_rate',
    'selected_count', 'value_reads', 'qk_dot_products', 'bytes_touched_est',
    'elapsed_ns_python', 'quality_score', 'compiler'
}


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    report = {
        'project': 'CloudtainerML',
        'revision': REV,
        'report': 'attention_workload_audit',
        'status': 'fail',
        'promotion_allowed': False,
        'artifact': ART.relative_to(ROOT).as_posix(),
    }
    if not ART.exists():
        errors.append('missing attention row benchmark artifact')
        report['errors'] = errors
    else:
        payload = json.loads(ART.read_text(encoding='utf-8'))
        rows = payload.get('rows', [])
        summary = payload.get('summary', {})
        compiler_summary = summary.get('compiler_summary', {})
        score_source = summary.get('score_source', '')
        if payload.get('kind') != 'python_attention_workload_benchmark':
            errors.append('artifact kind is not python_attention_workload_benchmark')
        if 'QK' not in score_source or 'softmax' not in score_source or '@ V' not in score_source:
            errors.append('score_source does not explicitly bind QK scores to softmax/V output')
        if not rows:
            errors.append('attention workload has no rows')
        else:
            sample_keys = set().union(*(set(r) for r in rows[: min(64, len(rows))]))
            missing = sorted(REQUIRED_ROW_FIELDS - sample_keys)
            if missing:
                errors.append('missing required row output fields: ' + ', '.join(missing))
            bad_dense = [r for r in rows if r.get('compiler') == 'dense_full' and (abs(r.get('mass_retained', 0) - 1.0) > 1e-9 or r.get('attention_rel_l2_error') != 0)]
            if bad_dense:
                errors.append('dense_full is not exact against itself')
        exact = compiler_summary.get('exact_topk_sparse', {})
        topp = compiler_summary.get('topp_0p95', {})
        prev = compiler_summary.get('prev_only_reuse', {})
        semantic_findings = {
            'exact_topk_sparse_mean_topk_hit_rate': exact.get('mean_topk_hit_rate'),
            'exact_topk_sparse_mean_mass_retained': exact.get('mean_mass_retained'),
            'exact_topk_sparse_mean_rel_l2': exact.get('mean_attention_rel_l2_error'),
            'topp_0p95_mean_selected_count': topp.get('mean_selected_count'),
            'topp_0p95_mean_mass_retained': topp.get('mean_mass_retained'),
            'topp_0p95_quality_bar_rate': topp.get('quality_bar_rate'),
            'prev_only_reuse_mean_qk_dot_products': prev.get('mean_qk_dot_products'),
            'prev_only_reuse_mean_rel_l2': prev.get('mean_attention_rel_l2_error'),
        }
        if exact and exact.get('mean_topk_hit_rate', 0) >= 0.999 and exact.get('mean_mass_retained', 1) < 0.35:
            warnings.append('exact Top-K is exact as a selector but loses most dense attention mass on this workload')
        if topp and topp.get('mean_mass_retained', 0) >= 0.94 and topp.get('mean_selected_count', 0) > 10 * 32:
            warnings.append('Top-p preserves output far better but is too wide to count as a strong sparse win')
        report.update({
            'row_count': len(rows),
            'compiler_count': len(compiler_summary),
            'semantic_findings': semantic_findings,
            'warnings': warnings,
            'errors': errors,
            'status': 'pass' if not errors else 'fail',
            'interpretation': 'The current attention workload keeps the QK/softmax/V output guard alive. It exposes a substantive negative result: exact Top-K can be selector-exact while badly wrong as dense attention output approximation; Top-p quality is a quality bound rather than a sparse win when it selects most of the row.',
        })
    (OUT / f'{REVUP}_ATTENTION_WORKLOAD_AUDIT.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    md = [f'# Attention workload audit — {REV}', '', f'**Status: {report["status"]}**', '', f'- artifact: `{report["artifact"]}`']
    if 'row_count' in report:
        md += [f'- rows: {report["row_count"]}', f'- compilers: {report["compiler_count"]}', '']
        md += ['## Semantic findings', '']
        for k, v in report.get('semantic_findings', {}).items():
            md.append(f'- {k}: {v}')
    if warnings:
        md += ['', '## Warnings', *[f'- {w}' for w in warnings]]
    if errors:
        md += ['', '## Errors', *[f'- {e}' for e in errors]]
    md += ['', '## Interpretation', '', report.get('interpretation', '')]
    (OUT / f'{REVUP}_ATTENTION_WORKLOAD_AUDIT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'warnings': len(warnings), 'errors': len(errors)}, indent=2))
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
