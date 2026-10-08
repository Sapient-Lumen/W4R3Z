#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = META.get('revision', 'rev0053')
REVUP = REV.upper()
ART_REL = f'artifacts/probe-results/{REVUP}_LEARNED_TRACE_BLOCK_BOUNDS.json'
MAN_REL = f'artifacts/run-manifests/{REVUP}_LEARNED_TRACE_BLOCK_BOUNDS_RUN_MANIFEST.json'
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
            errors.append('learned trace block-bound artifact must keep promotion blocked')
        if art.get('gpu_kernel_claim') is not False:
            errors.append('artifact must not claim GPU/fused-kernel evidence')
        if art.get('public_pretrained_trace_loaded') is not False:
            errors.append('artifact must not claim public/pretrained trace evidence')
        if art.get('trace_source_type') != 'tiny_trained_transformer_qkv_trace':
            errors.append('trace source type should be tiny trained transformer')
        if float(art.get('train_metrics', {}).get('eval_accuracy', 0.0)) < 0.95:
            errors.append('tiny trace model did not train to high retrieval accuracy')
        if int(art.get('raw_row_count', 0)) < 400:
            errors.append('too few raw learned trace method rows')
        if art.get('selection_contract', '').find('may not inspect V vectors') < 0:
            errors.append('selection contract does not explicitly forbid value/dense-output inspection')
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
    by = {(r.get('support_bucket'), r.get('method')): r for r in rows}
    methods = {r.get('method') for r in rows}
    expected_methods = {
        'dense_full_attention',
        'dense_score_mass_histogram_0p95_sparse',
        'position_mean_radius_block_pruned_0p95_sparse',
        'pca_sorted_mean_radius_block_pruned_0p95_sparse',
        'unsafe_pca_sampled_radius2_block_pruned_0p95_sparse',
    }
    if methods and methods != expected_methods:
        errors.append(f'unexpected method set: {sorted(methods)}')
    if len(rows) != 25:
        errors.append(f'expected 25 aggregate rows, got {len(rows)}')
    if any(r.get('selection_uses_values') or r.get('selection_uses_dense_output') for r in rows):
        errors.append('selector oracle leakage: values or dense outputs used during selection')
    if any(r.get('uses_generator_oracle_bounds') for r in rows):
        errors.append('generator-oracle block bounds leaked into learned trace rows')
    if any(r.get('is_gpu_kernel_claim') for r in rows):
        errors.append('row-level GPU kernel claim leaked')
    certified = [r for r in rows if r.get('block_upper_bound_pruning') and not r.get('unsafe_sampled_radius')]
    unsafe = [r for r in rows if r.get('unsafe_sampled_radius')]
    hist = [r for r in rows if r.get('method') == 'dense_score_mass_histogram_0p95_sparse']
    if any(float(r.get('mean_bound_violation_rate', 1.0)) > 1e-12 for r in certified):
        errors.append('certified learned block-bound rows have nonzero bound violations')
    if any(r.get('bound_is_certified') for r in unsafe):
        errors.append('unsafe sampled-radius learned rows must not be certified')
    if unsafe and max(float(r.get('mean_bound_violation_rate', 0.0)) for r in unsafe) < 0.25:
        errors.append('unsafe sampled-radius negative control did not expose bound violations')
    if any(abs(float(r.get('qk_dot_fraction_vs_dense', 0.0)) - 1.0) > 1e-9 for r in hist):
        errors.append('dense-score mass histogram must report full QK score work')

    all_pca = by.get(('all', 'pca_sorted_mean_radius_block_pruned_0p95_sparse'), {})
    low_pca = by.get(('low_support_le_q25', 'pca_sorted_mean_radius_block_pruned_0p95_sparse'), {})
    high_pca = by.get(('high_support_ge_q75', 'pca_sorted_mean_radius_block_pruned_0p95_sparse'), {})
    all_pos = by.get(('all', 'position_mean_radius_block_pruned_0p95_sparse'), {})
    all_hist = by.get(('all', 'dense_score_mass_histogram_0p95_sparse'), {})
    all_unsafe = by.get(('all', 'unsafe_pca_sampled_radius2_block_pruned_0p95_sparse'), {})
    if all_pca:
        if float(all_pca.get('quality_bar_rate', 0.0)) < 0.95:
            errors.append('PCA block-bound learned trace quality is below bar')
        if float(all_pca.get('qk_dot_fraction_vs_dense', 0.0)) >= 1.0:
            warnings.append('PCA block-bound does not reduce total QK dot count on aggregate learned trace')
    else:
        errors.append('missing all/PCA learned block row')
    if low_pca:
        if float(low_pca.get('qk_dot_fraction_vs_dense', 1.0)) >= 0.70:
            errors.append('low-support learned PCA block row did not skip enough QK score work')
    else:
        errors.append('missing low-support PCA learned block row')
    if high_pca:
        if float(high_pca.get('qk_dot_fraction_vs_dense', 0.0)) <= 1.0:
            warnings.append('high-support PCA block row did not expose near-dense/overhead collapse')
    else:
        errors.append('missing high-support PCA learned block row')

    report = {
        'project': 'CloudtainerML',
        'revision': REV,
        'report': 'learned_trace_block_bounds_audit',
        'status': 'pass' if not errors else 'fail',
        'promotion_allowed': False,
        'artifact': ART_REL,
        'manifest': MAN_REL,
        'train_eval_accuracy': art.get('train_metrics', {}).get('eval_accuracy') if art else None,
        'trace_rows': art.get('trace_meta', {}).get('trace_rows') if art else None,
        'aggregate_rows': len(rows),
        'all_hist_qk_fraction': all_hist.get('qk_dot_fraction_vs_dense'),
        'all_position_qk_fraction': all_pos.get('qk_dot_fraction_vs_dense'),
        'all_pca_qk_fraction': all_pca.get('qk_dot_fraction_vs_dense'),
        'low_support_pca_qk_fraction': low_pca.get('qk_dot_fraction_vs_dense'),
        'high_support_pca_qk_fraction': high_pca.get('qk_dot_fraction_vs_dense'),
        'all_pca_quality_bar_rate': all_pca.get('quality_bar_rate'),
        'unsafe_pca_bound_violation_rate': all_unsafe.get('mean_bound_violation_rate'),
        'errors': errors,
        'warnings': warnings,
        'interpretation': 'rev0053 tests score-path block pruning on Q/K/V rows emitted by a tiny trained retrieval transformer. PCA-sorted observable blocks can skip score work on low-support learned rows, but high-support rows erase the advantage and sampled-radius shortcuts are vetoed by bound violations. This is still tiny-model evidence, not public/pretrained or GPU-kernel evidence.',
    }
    (OUT / f'{REVUP}_LEARNED_TRACE_BLOCK_BOUNDS_AUDIT.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    md = [f'# Learned trace block-bound audit — {REV}', '', f'**Status: {report["status"]}**', '', f'- train eval accuracy: `{report["train_eval_accuracy"]}`', f'- trace rows: `{report["trace_rows"]}`', f'- all PCA QK fraction: `{report["all_pca_qk_fraction"]}`', f'- low-support PCA QK fraction: `{report["low_support_pca_qk_fraction"]}`', f'- high-support PCA QK fraction: `{report["high_support_pca_qk_fraction"]}`', f'- unsafe PCA bound-violation rate: `{report["unsafe_pca_bound_violation_rate"]}`', '', '## Interpretation', '', report['interpretation']]
    if warnings:
        md += ['', '## Warnings', *[f'- {w}' for w in warnings]]
    if errors:
        md += ['', '## Errors', *[f'- {e}' for e in errors]]
    (OUT / f'{REVUP}_LEARNED_TRACE_BLOCK_BOUNDS_AUDIT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'errors': len(errors), 'warnings': len(warnings)}, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
