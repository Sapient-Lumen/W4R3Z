#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = META.get('revision', 'rev0044')
REVUP = REV.upper()
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)
FRONTIER = ROOT / 'artifacts' / 'probe-results' / f'{REVUP}_ATTENTION_MASS_FRONTIER.json'
TRACE = ROOT / 'artifacts' / 'probe-results' / f'{REVUP}_TINY_TRANSFORMER_ATTENTION_TRACE_PROBE.json'


def load(p: Path):
    return json.loads(p.read_text(encoding='utf-8'))


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    findings: dict = {}

    if not FRONTIER.exists():
        errors.append('missing attention mass frontier artifact')
    else:
        f = load(FRONTIER)
        rows = f.get('rows', [])
        summ = f.get('summary', {})
        overall = summ.get('overall', {})
        guards = set(summ.get('guard_fields', []))
        required = {'min_k_for_mass_0p95', 'topk_32_mass', 'effective_support', 'attention_rel_l2_error', 'output_cosine', 'bytes_touched_est'}
        missing = sorted(required - guards)
        if missing:
            errors.append('frontier guard fields missing: ' + ', '.join(missing))
        if f.get('kind') != 'python_attention_frontier_benchmark':
            errors.append('frontier artifact kind is wrong')
        if not rows:
            errors.append('frontier has no rows')
        if overall.get('mean_min_k_for_mass_0p95', 0) <= 32:
            warnings.append('frontier says 0.95 mass often fits inside K=32; negative Top-K finding may have weakened')
        findings['frontier'] = {
            'row_count': len(rows),
            'mean_min_k_for_mass_0p95': overall.get('mean_min_k_for_mass_0p95'),
            'p90_min_k_for_mass_0p95': overall.get('p90_min_k_for_mass_0p95'),
            'mean_topk32_mass': overall.get('mean_topk32_mass'),
            'topk32_pass_rate_mass_0p95': overall.get('topk32_pass_rate_mass_0p95'),
            'share_min_k_0p95_le_4xK': overall.get('share_min_k_0p95_le_4xK'),
            'share_min_k_0p95_le_8xK': overall.get('share_min_k_0p95_le_8xK'),
        }

    if not TRACE.exists():
        errors.append('missing tiny transformer trace artifact')
    else:
        t = load(TRACE)
        rows = t.get('rows', [])
        summ = t.get('summary', {})
        score_source = summ.get('score_source', '')
        guards = set(summ.get('guard_fields', []))
        method_summary = summ.get('method_summary', {})
        required = {'attention_rel_l2_error', 'output_cosine', 'mass_retained', 'needle_selected', 'model_accuracy_snapshot', 'bytes_touched_est'}
        missing = sorted(required - guards)
        if missing:
            errors.append('trace guard fields missing: ' + ', '.join(missing))
        if t.get('kind') != 'python_tiny_model_attention_trace_benchmark':
            errors.append('trace artifact kind is wrong')
        if 'trained PyTorch transformer' not in score_source or 'QK logits' not in score_source or '@ V' not in score_source:
            errors.append('trace score_source does not bind trained model Q/K/V to dense/sparse output')
        if not rows:
            errors.append('trace has no rows')
        train_acc = summ.get('train_metrics', {}).get('eval_accuracy')
        if train_acc is not None and train_acc < 0.75:
            warnings.append(f'tiny transformer eval accuracy is low ({train_acc}); traces may be undertrained')
        exact = method_summary.get('exact_topk_8', {})
        topp = method_summary.get('topp_0p95', {})
        findings['trace'] = {
            'row_count': len(rows),
            'eval_accuracy': train_acc,
            'exact_topk_8_mean_mass_retained': exact.get('mean_mass_retained'),
            'exact_topk_8_quality_bar_rate': exact.get('quality_bar_rate'),
            'topp_0p95_mean_selected_count': topp.get('mean_selected_count'),
            'topp_0p95_quality_bar_rate': topp.get('quality_bar_rate'),
        }

    report = {
        'project': 'CloudtainerML',
        'revision': REV,
        'report': 'attention_frontier_trace_audit',
        'status': 'pass' if not errors else 'fail',
        'promotion_allowed': False,
        'artifacts': {
            'frontier': FRONTIER.relative_to(ROOT).as_posix(),
            'trace': TRACE.relative_to(ROOT).as_posix(),
        },
        'findings': findings,
        'warnings': warnings,
        'errors': errors,
        'interpretation': 'rev0044 adds a mass/value-read frontier and toy trained-model Q/K/V traces. This closes part of the synthetic-only attention gap but remains below E3 because the trace is toy-scale and timing is not a kernel implementation.',
    }
    (OUT / f'{REVUP}_ATTENTION_FRONTIER_TRACE_AUDIT.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    md = [f'# Attention frontier/trace audit — {REV}', '', f'**Status: {report["status"]}**', '', '## Findings', '']
    for k, v in findings.items():
        md.append(f'### {k}')
        for kk, vv in v.items():
            md.append(f'- {kk}: {vv}')
        md.append('')
    if warnings:
        md += ['## Warnings', *[f'- {w}' for w in warnings], '']
    if errors:
        md += ['## Errors', *[f'- {e}' for e in errors], '']
    md += ['## Interpretation', '', report['interpretation']]
    (OUT / f'{REVUP}_ATTENTION_FRONTIER_TRACE_AUDIT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'warnings': len(warnings), 'errors': len(errors), 'findings': findings}, indent=2))
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
