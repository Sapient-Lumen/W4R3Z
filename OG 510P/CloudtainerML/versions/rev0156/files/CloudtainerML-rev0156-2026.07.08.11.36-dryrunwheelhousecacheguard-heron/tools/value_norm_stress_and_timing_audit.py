#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = META.get('revision', 'rev0046')
REVUP = REV.upper()
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)
STRESS = ROOT / 'artifacts' / 'probe-results' / f'{REVUP}_VALUE_NORM_GUARDED_ATTENTION_STRESS.json'
CPU = ROOT / 'artifacts' / 'probe-results' / f'{REVUP}_ATTENTION_SELECTOR_CPU_MICROBENCH.json'
CORE = ROOT / 'experiments' / 'attention_compiler_core' / 'attention_core.py'


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def fmean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else None


def selector_source_check() -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    info: dict[str, Any] = {}
    tree = ast.parse(CORE.read_text(encoding='utf-8'))
    selector_names = {
        'value_norm_guarded_histogram_selection',
        'value_norm_exception_mass_selection',
        'histogram_mass_selection',
    }
    forbidden = {'values', 'dense_out', 'sparse_out', 'output_metrics', 'sparse_attention_output'}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in selector_names:
            names = {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}
            # value_norms is allowed; actual V vectors are not.
            bad = sorted(names & forbidden)
            info[node.name] = {'forbidden_references': bad, 'oracle_free_source': not bad}
            if bad:
                errors.append(f'{node.name} references forbidden selector-time symbol(s): {bad}')
    missing = selector_names - set(info)
    if missing:
        errors.append('missing selector functions: ' + ', '.join(sorted(missing)))
    return errors, info


def compiler_summary(stress: dict, regime: str, compiler: str) -> dict:
    return stress.get('summary', {}).get('regime_summary', {}).get(regime, {}).get('compiler_summary', {}).get(compiler, {})


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    findings: dict[str, Any] = {}

    if not STRESS.exists():
        errors.append('missing value-norm stress artifact')
        stress = None
    else:
        stress = load(STRESS)
        rows = stress.get('rows', [])
        summary = stress.get('summary', {})
        if stress.get('kind') != 'python_value_norm_guarded_attention_stress':
            errors.append('value-norm stress artifact kind is wrong')
        if not rows:
            errors.append('value-norm stress artifact has no rows')
        required = {
            'mass_retained', 'attention_rel_l2_error', 'output_cosine', 'passes_quality_bar',
            'selection_uses_values', 'selection_uses_dense_output', 'selection_uses_value_norms',
            'value_norm_reads', 'metadata_reads', 'metadata_read_fraction',
            'value_error_bound_from_scores_and_norms', 'passes_value_norm_bound',
            'outlier_weighted_value_norm', 'outlier_recall', 'bytes_touched_plus_norm_metadata_est',
        }
        guards = set(summary.get('guard_fields', []))
        missing_guards = sorted(required - guards)
        if missing_guards:
            errors.append('value-norm stress missing guard fields: ' + ', '.join(missing_guards))
        leak_rows = [r for r in rows if r.get('selection_uses_values') or r.get('selection_uses_dense_output')]
        if leak_rows or summary.get('selection_oracle_leakage_rows') != 0:
            errors.append(f'value-norm stress selector oracle leakage rows: {len(leak_rows)}')
        repairs = summary.get('failure_repair_summary', {})
        failures = int(repairs.get('mass_only_rows_with_target_mass_but_bad_output') or 0)
        exception_repairs = int(repairs.get('value_norm_exception_repairs') or 0)
        findings['failure_repair_summary'] = repairs
        if failures <= 0:
            errors.append('stress failed to expose any mass-only target-mass/output failures')
        if exception_repairs <= 0:
            errors.append('value-norm exception selector repaired no mass-only failures')
        if repairs.get('repair_rate_exception_given_mass_failure', 0.0) < 0.5:
            warnings.append('value-norm exception repair rate below 0.5 on mass-only failures')
        labels = {
            'mass_hist': 'mass_histogram_0p95_bins32',
            'norm_exception': 'value_norm_exception_mass_0p95_bins32',
            'norm_guarded_hist': 'value_norm_guarded_histogram_0p95_bins32',
            'topp': 'ordered_topp_0p95_bound',
        }
        single_mass = compiler_summary(stress, 'single_tail_value_spike', labels['mass_hist'])
        single_exc = compiler_summary(stress, 'single_tail_value_spike', labels['norm_exception'])
        multi_mass = compiler_summary(stress, 'multi_tail_value_spikes', labels['mass_hist'])
        multi_exc = compiler_summary(stress, 'multi_tail_value_spikes', labels['norm_exception'])
        broad_mass = compiler_summary(stress, 'broad_bounded', labels['mass_hist'])
        findings['regime_key_results'] = {
            'single_tail_mass_hist_quality': single_mass.get('quality_bar_rate'),
            'single_tail_norm_exception_quality': single_exc.get('quality_bar_rate'),
            'single_tail_norm_exception_selected_count': single_exc.get('mean_selected_count'),
            'multi_tail_mass_hist_quality': multi_mass.get('quality_bar_rate'),
            'multi_tail_norm_exception_quality': multi_exc.get('quality_bar_rate'),
            'broad_mass_hist_selected_count': broad_mass.get('mean_selected_count'),
            'broad_mass_hist_quality': broad_mass.get('quality_bar_rate'),
        }
        if (single_mass.get('quality_bar_rate') or 1.0) > 0.25:
            warnings.append('single-tail mass-only failure is weaker than expected')
        if (single_exc.get('quality_bar_rate') or 0.0) < 0.9:
            errors.append('single-tail value-norm exception repair did not pass strongly')
        if (multi_exc.get('quality_bar_rate') or 0.0) < 0.9:
            errors.append('multi-tail value-norm exception repair did not pass strongly')
        if (broad_mass.get('mean_selected_count') or 0.0) < 0.8 * 512:
            warnings.append('broad bounded regime no longer forces wide reads')

    if not CPU.exists():
        errors.append('missing selector CPU microbenchmark artifact')
        cpu = None
    else:
        cpu = load(CPU)
        rows = cpu.get('rows', [])
        if cpu.get('kind') != 'cpp_attention_selector_cpu_microbench':
            errors.append('CPU selector artifact kind is wrong')
        if cpu.get('timing_scope') != 'selector_only_native_cpu_not_attention_kernel':
            errors.append('CPU selector timing scope is not explicit enough')
        if len(rows) < 6:
            errors.append('CPU selector microbench has too few rows')
        if not cpu.get('run_provenance', {}).get('compile_command'):
            errors.append('CPU selector microbench missing compile provenance')
        methods = sorted({r.get('method') for r in rows})
        findings['cpu_microbench'] = {
            'row_count': len(rows),
            'methods': methods,
            'timing_scope': cpu.get('timing_scope'),
            'min_ns_per_row': min((float(r.get('mean_ns_per_row') or 0.0) for r in rows), default=None),
            'max_ns_per_row': max((float(r.get('mean_ns_per_row') or 0.0) for r in rows), default=None),
            'mean_selected_fraction_by_method': {m: fmean(float(r['selected_fraction']) for r in rows if r.get('method') == m) for m in methods},
        }
        required_methods = {'exact_topk_32_nth_element', 'mass_histogram_0p95_bins32', 'value_norm_exception_mass_0p95_bins32'}
        if not required_methods.issubset(set(methods)):
            errors.append('CPU selector microbench missing methods: ' + ', '.join(sorted(required_methods - set(methods))))

    src_errors, src_info = selector_source_check()
    errors.extend(src_errors)
    findings['selector_source_check'] = src_info

    report = {
        'project': 'CloudtainerML',
        'revision': REV,
        'report': 'value_norm_stress_and_timing_audit',
        'status': 'pass' if not errors else 'fail',
        'promotion_allowed': False,
        'stress_artifact': STRESS.relative_to(ROOT).as_posix(),
        'cpu_microbench_artifact': CPU.relative_to(ROOT).as_posix(),
        'findings': findings,
        'warnings': warnings,
        'errors': errors,
        'interpretation': 'rev0046 blocks the unsafe inference that target probability mass alone certifies attention output. Value-norm metadata can repair adversarial tail-risk rows without V/output oracle leakage, but this adds sidecar and kernel obligations. Native CPU selector timing is useful implementation pressure, not an E3 attention-kernel speed claim.',
    }
    (OUT / f'{REVUP}_VALUE_NORM_STRESS_AND_TIMING_AUDIT.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    md = [f'# Value-norm stress and timing audit — {REV}', '', f'**Status: {report["status"]}**', '', '## Key findings', '']
    for k, v in findings.get('failure_repair_summary', {}).items():
        md.append(f'- {k}: {v}')
    md += ['', '## Regime key results', '']
    for k, v in findings.get('regime_key_results', {}).items():
        md.append(f'- {k}: {v}')
    md += ['', '## CPU selector microbench', '']
    for k, v in findings.get('cpu_microbench', {}).items():
        md.append(f'- {k}: {v}')
    md += ['', '## Source oracle check', '']
    for name, vals in src_info.items():
        md.append(f'- `{name}`: oracle_free_source={vals.get("oracle_free_source")}, forbidden_references={vals.get("forbidden_references")}')
    if warnings:
        md += ['', '## Warnings', *[f'- {w}' for w in warnings]]
    if errors:
        md += ['', '## Errors', *[f'- {e}' for e in errors]]
    md += ['', '## Interpretation', '', report['interpretation']]
    (OUT / f'{REVUP}_VALUE_NORM_STRESS_AND_TIMING_AUDIT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'warnings': len(warnings), 'errors': len(errors), 'findings': findings}, indent=2))
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
