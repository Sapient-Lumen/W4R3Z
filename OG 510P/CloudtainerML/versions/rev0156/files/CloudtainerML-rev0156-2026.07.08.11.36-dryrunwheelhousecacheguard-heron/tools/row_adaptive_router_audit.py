#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = META.get('revision', 'rev0054')
REVUP = REV.upper()
ART_REL = f'artifacts/probe-results/{REVUP}_ROW_ADAPTIVE_ATTENTION_ROUTER.json'
MAN_REL = f'artifacts/run-manifests/{REVUP}_ROW_ADAPTIVE_ATTENTION_ROUTER_RUN_MANIFEST.json'
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


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    art_path = ROOT / ART_REL
    man_path = ROOT / MAN_REL
    art: dict[str, Any] = {}
    man: dict[str, Any] = {}
    if not art_path.exists():
        errors.append('missing artifact: ' + ART_REL)
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
            errors.append('row-adaptive artifact must keep promotion blocked')
        if art.get('gpu_kernel_claim') is not False:
            errors.append('artifact must not claim GPU/fused-kernel evidence')
        if art.get('public_pretrained_trace_loaded') is not False:
            errors.append('artifact must not claim public/pretrained trace evidence')
        if float(art.get('train_metrics', {}).get('eval_accuracy', 0.0)) < 0.95:
            errors.append('tiny trace model did not train to high retrieval accuracy')
        if int(art.get('raw_row_count', 0)) < 400:
            errors.append('too few raw row-method observations')
        if 'heldout' not in art.get('configuration', {}).get('partition_rule', ''):
            errors.append('partition rule does not expose heldout evaluation')
        if art.get('selection_contract', '').find('may not inspect V vectors') < 0:
            errors.append('selection contract does not explicitly forbid value inspection')
        if art.get('selection_contract', '').find('heldout quality labels') < 0:
            errors.append('selection contract does not forbid heldout label leakage')

    if man and art_path.exists():
        if man.get('artifact_sha256') != sha256_file(art_path):
            errors.append('run manifest artifact hash mismatch')
        src = ROOT / str(man.get('source', ''))
        if not src.exists() or man.get('source_sha256') != sha256_file(src):
            errors.append('run manifest source hash mismatch')
        if man.get('public_pretrained_trace_loaded') is not False:
            errors.append('manifest claims public/pretrained trace evidence')
        if man.get('gpu_kernel_claim') is not False:
            errors.append('manifest claims GPU evidence')

    rows = art.get('rows', []) if art else []
    if len(rows) != 15:
        errors.append(f'expected 15 aggregate rows, got {len(rows)}')
    methods = {r.get('method') for r in rows}
    expected = {
        'dense_full_attention',
        'dense_score_mass_histogram_0p95_sparse',
        'pca_block_bound_pruned_0p95_sparse',
        'adaptive_bound_gate_router_calibrated',
        'adaptive_block_attempt_then_fallback_router_calibrated',
    }
    if methods and methods != expected:
        errors.append('unexpected method set: ' + repr(sorted(methods)))
    if any(r.get('selection_uses_values') or r.get('selection_uses_dense_output') for r in rows):
        errors.append('selector oracle leakage: values or dense outputs used during selection')
    if any(r.get('public_pretrained_trace_loaded') for r in rows):
        errors.append('row-level public/pretrained claim leaked')
    if any(r.get('gpu_kernel_claim') for r in rows):
        errors.append('row-level GPU claim leaked')

    by = {(r.get('partition'), r.get('method')): r for r in rows}
    held_dense = by.get(('heldout', 'dense_full_attention'), {})
    held_hist = by.get(('heldout', 'dense_score_mass_histogram_0p95_sparse'), {})
    held_pca = by.get(('heldout', 'pca_block_bound_pruned_0p95_sparse'), {})
    held_router = by.get(('heldout', 'adaptive_bound_gate_router_calibrated'), {})
    held_attempt = by.get(('heldout', 'adaptive_block_attempt_then_fallback_router_calibrated'), {})
    cal_router = by.get(('calibration', 'adaptive_bound_gate_router_calibrated'), {})
    if not held_router:
        errors.append('missing heldout adaptive router row')
    if not cal_router:
        errors.append('missing calibration adaptive router row')
    if held_hist and abs(float(held_hist.get('qk_dot_fraction_vs_dense', 0.0)) - 1.0) > 1e-9:
        errors.append('dense-score histogram must pay all QK score work')
    if held_pca and float(held_pca.get('qk_dot_fraction_vs_dense', 9.0)) >= 1.0:
        warnings.append('PCA block pruning did not skip aggregate QK work on heldout')
    if held_router:
        if float(held_router.get('quality_bar_rate', 0.0)) < 0.985:
            errors.append('heldout adaptive bound-gate quality below calibration floor')
        paths = held_router.get('path_counts', {})
        if not {'block_pruned_after_bound_precheck', 'dense_score_mass_histogram_after_bound_precheck'} <= set(paths):
            errors.append('adaptive bound-gate did not exercise both block and dense-score fallback paths')
        if float(held_router.get('mean_failed_probe_exact_token_dots', 0.0)) != 0.0:
            errors.append('bound-gate router should not pay exact failed-probe dots before fallback')
        if float(held_router.get('block_bound_precheck_dots', 0.0) or 0.0) < 0:
            errors.append('invalid block-bound precheck accounting')
    if held_attempt:
        if float(held_attempt.get('mean_failed_probe_exact_token_dots', 0.0)) <= 0.0:
            errors.append('block-attempt fallback did not expose failed exact-probe overhead')
        if held_router and float(held_attempt.get('mean_total_work_units', 0.0)) <= float(held_router.get('mean_total_work_units', 0.0)):
            errors.append('block-attempt router should be worse than precheck router in this stress test')
    if held_dense and held_router:
        if float(held_router.get('mean_total_work_units', 1e9)) >= float(held_dense.get('mean_total_work_units', 0.0)):
            errors.append('adaptive router did not beat dense under equal work units')
    if held_hist and held_router:
        if float(held_router.get('mean_total_work_units', 0.0)) < float(held_hist.get('mean_total_work_units', 0.0)):
            warnings.append('adaptive router unexpectedly beat dense-score histogram under equal units; recheck cost model')
        else:
            warnings.append('adaptive router does not beat dense-score histogram under equal units; this is an honest non-promotion result')

    summary = art.get('summary', {}) if art else {}
    breakeven = summary.get('qk_weight_break_even_adaptive_bound_gate_vs_histogram')
    if breakeven is None or float(breakeven) <= 1.0:
        errors.append('missing or implausible QK-weight break-even vs histogram')
    if summary.get('adaptive_bound_gate_beats_dense_score_histogram_equal_units') is not False:
        errors.append('summary should record that adaptive router does not beat histogram under equal units')
    if summary.get('block_attempt_overhead_exposed') is not True:
        errors.append('summary should expose block-attempt overhead')
    sensitivity = summary.get('cost_model_sensitivity', [])
    if len(sensitivity) < 5:
        errors.append('cost model sensitivity table missing or too small')

    report = {
        'project': 'CloudtainerML',
        'revision': REV,
        'report': 'row_adaptive_router_audit',
        'status': 'pass' if not errors else 'fail',
        'promotion_allowed': False,
        'artifact': ART_REL,
        'manifest': MAN_REL,
        'train_eval_accuracy': art.get('train_metrics', {}).get('eval_accuracy') if art else None,
        'raw_row_count': art.get('raw_row_count') if art else None,
        'heldout_dense_work_units': held_dense.get('mean_total_work_units'),
        'heldout_hist_work_units': held_hist.get('mean_total_work_units'),
        'heldout_pca_work_units': held_pca.get('mean_total_work_units'),
        'heldout_adaptive_work_units': held_router.get('mean_total_work_units'),
        'heldout_adaptive_quality_rate': held_router.get('quality_bar_rate'),
        'heldout_adaptive_qk_fraction': held_router.get('qk_dot_fraction_vs_dense'),
        'heldout_adaptive_path_counts': held_router.get('path_counts'),
        'heldout_block_attempt_failed_probe_dots': held_attempt.get('mean_failed_probe_exact_token_dots'),
        'qk_weight_break_even_adaptive_vs_histogram': breakeven,
        'errors': errors,
        'warnings': warnings,
        'interpretation': 'rev0054 calibrates a tiny row-adaptive router on calibration rows and evaluates heldout rows with failed-route costs charged. The result is useful but non-promotional: the adaptive bound gate beats dense full attention under equal units, but not the simpler dense-score mass histogram unless QK score work is weighted much more heavily than value reads. The aggressive block-attempt fallback exposes avoidable wasted exact-score work.',
    }
    (OUT / f'{REVUP}_ROW_ADAPTIVE_ROUTER_AUDIT.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    md = [
        f'# Row-adaptive router audit — {REV}', '', f'**Status: {report["status"]}**', '',
        f'- train eval accuracy: `{report["train_eval_accuracy"]}`',
        f'- heldout dense work units: `{report["heldout_dense_work_units"]}`',
        f'- heldout histogram work units: `{report["heldout_hist_work_units"]}`',
        f'- heldout adaptive work units: `{report["heldout_adaptive_work_units"]}`',
        f'- heldout adaptive quality rate: `{report["heldout_adaptive_quality_rate"]}`',
        f'- heldout adaptive path counts: `{report["heldout_adaptive_path_counts"]}`',
        f'- block-attempt failed exact probe dots: `{report["heldout_block_attempt_failed_probe_dots"]}`',
        f'- QK-weight break-even vs histogram: `{report["qk_weight_break_even_adaptive_vs_histogram"]}`',
        '', '## Interpretation', '', report['interpretation'],
    ]
    if warnings:
        md += ['', '## Warnings', *[f'- {w}' for w in warnings]]
    if errors:
        md += ['', '## Errors', *[f'- {e}' for e in errors]]
    (OUT / f'{REVUP}_ROW_ADAPTIVE_ROUTER_AUDIT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'errors': len(errors), 'warnings': len(warnings)}, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
