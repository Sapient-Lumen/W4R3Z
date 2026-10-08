#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = META.get('revision', 'rev0045')
REVUP = REV.upper()
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)
ART = ROOT / 'artifacts' / 'probe-results' / f'{REVUP}_MASS_CERTIFIED_ATTENTION_COMPILER.json'
CORE = ROOT / 'experiments' / 'attention_compiler_core' / 'attention_core.py'


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def fmean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else None


def source_oracle_check() -> tuple[list[str], dict[str, Any]]:
    """AST check: selector functions must not reference values/dense output helpers."""
    errors: list[str] = []
    info: dict[str, Any] = {}
    tree = ast.parse(CORE.read_text(encoding='utf-8'))
    selector_names = {
        'delta_grid_mass_selection',
        'histogram_mass_selection',
        'block_local_topb_mass_selection',
    }
    forbidden_names = {'values', 'dense_out', 'sparse_out', 'output_metrics', 'sparse_attention_output'}
    forbidden_attrs = {'values'}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in selector_names:
            names = {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}
            attrs = {n.attr for n in ast.walk(node) if isinstance(n, ast.Attribute)}
            bad = sorted((names & forbidden_names) | (attrs & forbidden_attrs))
            info[node.name] = {'forbidden_references': bad, 'oracle_free_source': not bad}
            if bad:
                errors.append(f'{node.name} references forbidden selection-time symbol(s): {bad}')
    missing = selector_names - set(info)
    if missing:
        errors.append('missing selector functions: ' + ', '.join(sorted(missing)))
    return errors, info


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    findings: dict[str, Any] = {}
    if not ART.exists():
        errors.append('missing mass-certified attention compiler artifact')
        payload = None
    else:
        payload = load(ART)
        if payload.get('kind') != 'python_mass_certified_attention_compiler_benchmark':
            errors.append('mass-certified artifact kind is wrong')
        rows = payload.get('rows', [])
        summary = payload.get('summary', {})
        guards = set(summary.get('guard_fields', []))
        required = {
            'mass_retained', 'certified_mass_from_scores', 'certificate_error_abs',
            'selection_uses_values', 'selection_uses_dense_output', 'mass_certificate',
            'mass_certified_without_values', 'value_reads', 'value_read_fraction',
            'attention_rel_l2_error', 'output_cosine', 'passes_quality_bar',
            'sort_free_selector', 'score_reads', 'selector_passes', 'bytes_touched_est',
        }
        missing = sorted(required - guards)
        if missing:
            errors.append('guard fields missing from mass-certified artifact: ' + ', '.join(missing))
        if not rows:
            errors.append('mass-certified artifact has no rows')
        leak_rows = [r for r in rows if r.get('selection_uses_values') or r.get('selection_uses_dense_output')]
        if leak_rows:
            errors.append(f'selection oracle leakage rows detected: {len(leak_rows)}')
        cert_errors = [float(r.get('certificate_error_abs') or 0.0) for r in rows if r.get('mass_certificate') != 'not_mass_certified']
        if cert_errors and max(cert_errors) > 1e-9:
            errors.append(f'mass certificate mismatch exceeds tolerance: {max(cert_errors)}')
        if summary.get('oracle_leakage_rows') != 0 or not summary.get('mass_certified_candidate_oracle_free'):
            errors.append('summary reports oracle leakage or non-oracle-free mass-certified candidates')
        dataset_summary = summary.get('dataset_summary', {})
        findings['datasets'] = {}
        for dataset, ds in dataset_summary.items():
            cs = ds.get('compiler_summary', {})
            exact = next((v for k, v in cs.items() if k.startswith('exact_topk_')), {})
            hist = next((v for k, v in cs.items() if k.startswith('mass_histogram')), {})
            delta = cs.get('mass_delta_grid_0p95', {})
            topp = cs.get('ordered_topp_0p95_bound', {})
            dense = cs.get('full_dense', {})
            findings['datasets'][dataset] = {
                'row_count': ds.get('row_count'),
                'exact_topk_quality_bar_rate': exact.get('quality_bar_rate'),
                'exact_topk_mean_selected_count': exact.get('mean_selected_count'),
                'exact_topk_mean_mass_retained': exact.get('mean_mass_retained'),
                'ordered_topp_mean_selected_count': topp.get('mean_selected_count'),
                'ordered_topp_quality_bar_rate': topp.get('quality_bar_rate'),
                'histogram_mean_selected_count': hist.get('mean_selected_count'),
                'histogram_quality_bar_rate': hist.get('quality_bar_rate'),
                'delta_mean_selected_count': delta.get('mean_selected_count'),
                'delta_quality_bar_rate': delta.get('quality_bar_rate'),
                'dense_mean_selected_count': dense.get('mean_selected_count'),
            }
            if dataset == 'tiny_trained_transformer_trace_rows':
                if (hist.get('quality_bar_rate') or 0.0) < 0.90:
                    warnings.append('tiny trace histogram quality is below 0.90; deployable mass compiler is weak')
                if (hist.get('mean_selected_count') or 1e9) >= (dense.get('mean_selected_count') or 0.0):
                    warnings.append('tiny trace histogram does not reduce value reads versus dense')
            if dataset == 'synthetic_attention_rows':
                if (hist.get('mean_value_read_fraction') or 1.0) > 0.85:
                    warnings.append('synthetic histogram remains very wide; broad-attention regimes are not sparse wins')

    src_errors, src_info = source_oracle_check()
    errors.extend(src_errors)
    findings['source_oracle_check'] = src_info
    report = {
        'project': 'CloudtainerML',
        'revision': REV,
        'report': 'mass_certified_attention_audit',
        'status': 'pass' if not errors else 'fail',
        'promotion_allowed': False,
        'artifact': ART.relative_to(ROOT).as_posix(),
        'source': CORE.relative_to(ROOT).as_posix(),
        'findings': findings,
        'warnings': warnings,
        'errors': errors,
        'interpretation': 'rev0045 tests a real next step after the Top-K veto: score-only mass-certified selection. Passing this audit means the selector evidence is not using V vectors or dense outputs as an oracle; it does not mean the Python selector is a kernel-speed claim.',
    }
    (OUT / f'{REVUP}_MASS_CERTIFIED_ATTENTION_AUDIT.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    md = [f'# Mass-certified attention audit — {REV}', '', f'**Status: {report["status"]}**', '', '## Dataset findings', '']
    for dataset, vals in findings.get('datasets', {}).items():
        md.append(f'### {dataset}')
        for k, v in vals.items():
            md.append(f'- {k}: {v}')
        md.append('')
    md += ['## Source oracle check', '']
    for name, vals in src_info.items():
        md.append(f'- `{name}`: oracle_free_source={vals.get("oracle_free_source")}, forbidden_references={vals.get("forbidden_references")}')
    if warnings:
        md += ['', '## Warnings', *[f'- {w}' for w in warnings]]
    if errors:
        md += ['', '## Errors', *[f'- {e}' for e in errors]]
    md += ['', '## Interpretation', '', report['interpretation']]
    (OUT / f'{REVUP}_MASS_CERTIFIED_ATTENTION_AUDIT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'warnings': len(warnings), 'errors': len(errors), 'findings': findings}, indent=2))
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
