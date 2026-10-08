#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = META.get('revision', 'rev0047')
REVUP = REV.upper()
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)
ART = ROOT / 'artifacts' / 'probe-results' / f'{REVUP}_ATTENTION_END_TO_END_CPU_MICROBENCH.json'


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def by(regime_rows: list[dict[str, Any]], method: str) -> dict[str, Any]:
    return next((r for r in regime_rows if r.get('method') == method), {})


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    findings: dict[str, Any] = {}

    if not ART.exists():
        errors.append('missing end-to-end CPU attention artifact')
        payload: dict[str, Any] = {}
    else:
        payload = load(ART)
        rows = payload.get('rows', [])
        if payload.get('kind') != 'cpp_native_cpu_row_attention_end_to_end_microbench':
            errors.append('wrong artifact kind')
        if payload.get('timing_scope') != 'native_cpu_row_attention_end_to_end_not_gpu_kernel_not_model_throughput':
            errors.append('timing scope is missing or unsafe')
        if not payload.get('run_provenance', {}).get('compile_command'):
            errors.append('missing compile/run provenance')
        if len(rows) < 12:
            errors.append('too few benchmark rows')
        required_methods = {'dense_full_softmax', 'exact_topk_32_sparse', 'mass_histogram_0p95_sparse', 'value_norm_exception_0p95_sparse'}
        regimes = sorted({r.get('regime') for r in rows})
        methods = {r.get('method') for r in rows}
        missing_methods = sorted(required_methods - methods)
        if missing_methods:
            errors.append('missing methods: ' + ', '.join(missing_methods))
        guard_fields = set(payload.get('summary', {}).get('guard_fields', []))
        required_guards = {
            'mean_ns_per_row', 'speedup_vs_dense', 'mean_selected_count', 'mean_value_reads',
            'mean_norm_metadata_reads', 'mean_mass_retained', 'mean_attention_rel_l2_error',
            'mean_output_cosine', 'quality_bar_rate', 'timing_includes_qk_scores',
            'timing_includes_softmax', 'timing_includes_value_accumulation', 'is_gpu_kernel_claim'
        }
        missing_guards = sorted(required_guards - guard_fields)
        if missing_guards:
            errors.append('artifact does not declare required timing/quality guards: ' + ', '.join(missing_guards))
        overclaim = [r for r in rows if r.get('is_gpu_kernel_claim') or not r.get('timing_includes_qk_scores') or not r.get('timing_includes_softmax') or not r.get('timing_includes_value_accumulation')]
        if overclaim:
            errors.append(f'{len(overclaim)} row(s) have unsafe timing-scope flags')
        by_regime: dict[str, dict[str, Any]] = {}
        for regime in regimes:
            rr = [r for r in rows if r.get('regime') == regime]
            dense = by(rr, 'dense_full_softmax')
            topk = by(rr, 'exact_topk_32_sparse')
            hist = by(rr, 'mass_histogram_0p95_sparse')
            exc = by(rr, 'value_norm_exception_0p95_sparse')
            by_regime[regime] = {
                'dense_ns_per_row': dense.get('mean_ns_per_row'),
                'topk_speedup': topk.get('speedup_vs_dense'),
                'topk_quality_bar_rate': topk.get('quality_bar_rate'),
                'hist_speedup': hist.get('speedup_vs_dense'),
                'hist_quality_bar_rate': hist.get('quality_bar_rate'),
                'hist_selected_fraction': hist.get('selected_fraction'),
                'exception_speedup': exc.get('speedup_vs_dense'),
                'exception_quality_bar_rate': exc.get('quality_bar_rate'),
                'exception_selected_fraction': exc.get('selected_fraction'),
                'exception_norm_metadata_reads': exc.get('mean_norm_metadata_reads'),
            }
            if not dense or abs(float(dense.get('speedup_vs_dense', 0.0)) - 1.0) > 0.05:
                errors.append(f'{regime}: dense baseline speedup is not ~1')
            if dense and float(dense.get('quality_bar_rate', 0.0)) < 1.0:
                errors.append(f'{regime}: dense baseline does not pass quality')
        findings['regime_summary'] = by_regime

        broad = by_regime.get('broad_bounded', {})
        peaked = by_regime.get('peaked_bounded', {})
        tail = by_regime.get('peaked_tail_norm_spikes', {})
        if float(broad.get('hist_selected_fraction', 0.0)) < 0.9:
            errors.append('broad regime did not force wide mass-histogram reads')
        if float(broad.get('hist_speedup', 99.0)) >= 1.0:
            warnings.append('broad mass-histogram unexpectedly faster than dense; inspect benchmark stability')
        if float(peaked.get('hist_speedup', 0.0)) <= 1.0:
            warnings.append('peaked mass-histogram did not beat dense; sparse benefit weaker than expected')
        if float(tail.get('hist_quality_bar_rate', 1.0)) > 0.2:
            errors.append('tail regime failed to expose mass-only output-quality failure')
        if float(tail.get('exception_quality_bar_rate', 0.0)) < 0.9:
            errors.append('value-norm exception did not repair tail-regime quality strongly')
        if float(tail.get('exception_speedup', 99.0)) >= 1.0:
            warnings.append('tail exception repair unexpectedly faster than dense; inspect if norm overhead is being counted')
        if float(tail.get('exception_norm_metadata_reads', 0.0)) < 512:
            errors.append('value-norm exception method is not counting norm metadata reads')

    report = {
        'project': 'CloudtainerML',
        'revision': REV,
        'report': 'attention_end_to_end_cpu_audit',
        'status': 'pass' if not errors else 'fail',
        'promotion_allowed': False,
        'artifact': ART.relative_to(ROOT).as_posix(),
        'findings': findings,
        'warnings': warnings,
        'errors': errors,
        'interpretation': 'rev0047 upgrades timing pressure from selector-only to native CPU row attention, including QK score computation, softmax, selection, and V accumulation. The result is a mixed veto: quality-preserving histogram selection can be faster in peaked bounded rows, but broad rows become dense-width and value-norm repair restores tail quality at a CPU cost. This is E2/E2.8 evidence, not GPU/fused-kernel or model-throughput evidence.',
    }
    (OUT / f'{REVUP}_ATTENTION_END_TO_END_CPU_AUDIT.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    md = [f'# End-to-end CPU attention audit — {REV}', '', f'**Status: {report["status"]}**', '', '## Regime summary', '']
    for regime, vals in findings.get('regime_summary', {}).items():
        md.append(f'### {regime}')
        for k, v in vals.items():
            md.append(f'- {k}: {v}')
        md.append('')
    if warnings:
        md += ['## Warnings', *[f'- {w}' for w in warnings], '']
    if errors:
        md += ['## Errors', *[f'- {e}' for e in errors], '']
    md += ['## Interpretation', '', report['interpretation']]
    (OUT / f'{REVUP}_ATTENTION_END_TO_END_CPU_AUDIT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'warnings': len(warnings), 'errors': len(errors), 'findings': findings}, indent=2))
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
