#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = META.get('revision', 'rev0056')
REVUP = REV.upper()
ART_REL = f'artifacts/probe-results/{REVUP}_ROUTER_COST_FRONTIER.json'
MAN_REL = f'artifacts/run-manifests/{REVUP}_ROUTER_COST_FRONTIER_RUN_MANIFEST.json'
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


def load(rel: str) -> Any:
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


def row_by(rows: list[dict[str, Any]], selector: str, qk_weight: float, method: str) -> dict[str, Any]:
    for r in rows:
        if r.get('selector') == selector and float(r.get('qk_weight')) == float(qk_weight) and r.get('method') == method:
            return r
    return {}


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    art_path = ROOT / ART_REL
    man_path = ROOT / MAN_REL
    art: dict[str, Any] = {}
    man: dict[str, Any] = {}
    if not art_path.exists():
        errors.append('missing router cost frontier artifact: ' + ART_REL)
    else:
        art = load(ART_REL)
    if not man_path.exists():
        errors.append('missing run manifest: ' + MAN_REL)
    else:
        man = load(MAN_REL)

    if art:
        if art.get('revision') != REV:
            errors.append('artifact revision mismatch')
        if art.get('promotion_allowed') is not False or art.get('summary', {}).get('promotion_allowed') is not False:
            errors.append('router cost frontier artifact must keep promotion blocked')
        if art.get('public_pretrained_trace_loaded') is not False:
            errors.append('artifact must not claim public/pretrained trace evidence')
        if art.get('gpu_kernel_claim') is not False:
            errors.append('artifact must not claim GPU/fused kernel evidence')
        if float(art.get('train_metrics', {}).get('eval_accuracy', 0.0)) < 0.95:
            errors.append('tiny trace model did not train to high accuracy')
        if int(art.get('raw_case_count', 0)) < 90:
            errors.append('too few raw cases for cost frontier')
        if 'qk_weight/value_weight is an explicit proxy assumption' not in art.get('cost_contract', ''):
            errors.append('cost contract does not explicitly flag proxy assumption')
        if 'heldout quality labels' not in art.get('selection_contract', ''):
            errors.append('selection contract does not forbid heldout quality leakage')

    if man and art_path.exists():
        if man.get('artifact_sha256') != sha256_file(art_path):
            errors.append('run manifest artifact hash mismatch')
        src = ROOT / str(man.get('source', ''))
        if not src.exists() or man.get('source_sha256') != sha256_file(src):
            errors.append('run manifest source hash mismatch')
        if man.get('public_pretrained_trace_loaded') is not False:
            errors.append('manifest claims public/pretrained trace evidence')
        if man.get('gpu_kernel_claim') is not False:
            errors.append('manifest claims GPU/fused kernel evidence')

    rows = art.get('rows', []) if art else []
    if len(rows) < 200:
        errors.append(f'expected at least 200 cost frontier rows, got {len(rows)}')
    if any(r.get('selection_uses_values') or r.get('selection_uses_dense_output') for r in rows):
        errors.append('selector oracle leakage: values or dense output used during routing/selection')
    if any(r.get('public_pretrained_trace_loaded') or r.get('gpu_kernel_claim') for r in rows):
        errors.append('row-level public/GPU claim leaked')
    if any(float(r.get('quality_bar_rate') or 0.0) < 0.985 for r in rows if r.get('method') == 'cost_calibrated_adaptive_bound_gate_router'):
        errors.append('some cost-calibrated router rows fall below quality floor')

    summary = art.get('summary', {}) if art else {}
    if summary.get('equal_unit_router_beats_histogram_all') is not False:
        errors.append('equal-unit router should not beat histogram on all rows')
    if summary.get('equal_unit_router_beats_histogram_high_support') is not False:
        errors.append('equal-unit router should not beat histogram on high-support rows')
    if summary.get('cost_model_dependency_exposed') is not True:
        errors.append('cost-model dependency was not exposed')
    if summary.get('unmeasured_cost_model_claim_blocked') is not True:
        errors.append('unmeasured cost-model claim gate was not blocked')
    first_all = summary.get('first_qk_weight_router_beats_histogram_all')
    if first_all is None or float(first_all) <= 1.0:
        errors.append('router should only beat histogram on all rows after qk_weight exceeds 1')
    if summary.get('first_qk_weight_router_beats_histogram_high_support') is not None:
        errors.append('router should not beat histogram on high-support rows anywhere on this grid')
    best_all = summary.get('best_methods_all', [])
    if not any(x.get('qk_weight') == 1.0 and x.get('best_quality_feasible_method') == 'dense_score_mass_histogram_0p95_sparse' for x in best_all):
        errors.append('equal-unit best method on all rows should be dense-score histogram')
    if not any(float(x.get('qk_weight')) >= 12.0 and x.get('best_quality_feasible_method') == 'pca_block_bound_pruned_0p95_sparse' for x in best_all):
        errors.append('high-qk all-row frontier did not surface static block-pruned path')

    if rows:
        all_eq_router = row_by(rows, 'all', 1.0, 'cost_calibrated_adaptive_bound_gate_router')
        all_eq_hist = row_by(rows, 'all', 1.0, 'dense_score_mass_histogram_0p95_sparse')
        all_hi_router = row_by(rows, 'all', float(first_all) if first_all is not None else 12.0, 'cost_calibrated_adaptive_bound_gate_router')
        all_hi_hist = row_by(rows, 'all', float(first_all) if first_all is not None else 12.0, 'dense_score_mass_histogram_0p95_sparse')
        high_max_router = row_by(rows, 'high_support', 32.0, 'cost_calibrated_adaptive_bound_gate_router')
        high_max_hist = row_by(rows, 'high_support', 32.0, 'dense_score_mass_histogram_0p95_sparse')
        if all_eq_router and all_eq_hist and float(all_eq_router['mean_weighted_cost_units']) <= float(all_eq_hist['mean_weighted_cost_units']):
            errors.append('row check failed: equal-unit router all-row cost is not above histogram')
        if all_hi_router and all_hi_hist and float(all_hi_router['mean_weighted_cost_units']) >= float(all_hi_hist['mean_weighted_cost_units']):
            errors.append('row check failed: high-qk router all-row cost is not below histogram at first winning grid point')
        if high_max_router and high_max_hist and float(high_max_router['mean_weighted_cost_units']) <= float(high_max_hist['mean_weighted_cost_units']):
            errors.append('row check failed: high-support router should remain above histogram even at qk_weight=32')
        if high_max_router and float(high_max_router.get('speedup_vs_dense_weighted') or 9.0) >= 1.0:
            warnings.append('high-support router is not slower than dense at qk_weight=32; interpretation may need updating')

    report = {
        'project': 'CloudtainerML',
        'revision': REV,
        'report': 'router_cost_frontier_audit',
        'status': 'pass' if not errors else 'fail',
        'promotion_allowed': False,
        'artifact': ART_REL,
        'manifest': MAN_REL,
        'train_eval_accuracy': art.get('train_metrics', {}).get('eval_accuracy') if art else None,
        'raw_case_count': art.get('raw_case_count') if art else None,
        'frontier_rows': len(rows),
        'equal_unit_router_all_cost_units': summary.get('equal_unit_router_all_cost_units'),
        'equal_unit_histogram_all_cost_units': summary.get('equal_unit_histogram_all_cost_units'),
        'first_qk_weight_router_beats_histogram_all': summary.get('first_qk_weight_router_beats_histogram_all'),
        'first_qk_weight_router_beats_histogram_high_support': summary.get('first_qk_weight_router_beats_histogram_high_support'),
        'errors': errors,
        'warnings': warnings,
        'interpretation': 'rev0056 exposes proxy-cost dependence: the adaptive router does not beat the dense-score histogram under equal units and only crosses it on all rows at high assumed QK weight, while high-support rows keep the histogram baseline unbeaten. This blocks promotion until measured platform costs and kernel paths exist.',
    }
    (OUT / f'{REVUP}_ROUTER_COST_FRONTIER_AUDIT.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    md = [
        f'# Router cost frontier audit — {REV}', '', f'**Status: {report["status"]}**', '',
        f'- train eval accuracy: `{report["train_eval_accuracy"]}`',
        f'- raw cases: `{report["raw_case_count"]}`',
        f'- frontier rows: `{report["frontier_rows"]}`',
        f'- equal-unit router all-row cost: `{report["equal_unit_router_all_cost_units"]}`',
        f'- equal-unit histogram all-row cost: `{report["equal_unit_histogram_all_cost_units"]}`',
        f'- first qk weight where router beats histogram on all rows: `{report["first_qk_weight_router_beats_histogram_all"]}`',
        f'- first qk weight where router beats histogram on high-support rows: `{report["first_qk_weight_router_beats_histogram_high_support"]}`',
        '', '## Interpretation', '', report['interpretation']
    ]
    if warnings:
        md += ['', '## Warnings', *[f'- {w}' for w in warnings]]
    if errors:
        md += ['', '## Errors', *[f'- {e}' for e in errors]]
    (OUT / f'{REVUP}_ROUTER_COST_FRONTIER_AUDIT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'errors': len(errors), 'warnings': len(warnings)}, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
