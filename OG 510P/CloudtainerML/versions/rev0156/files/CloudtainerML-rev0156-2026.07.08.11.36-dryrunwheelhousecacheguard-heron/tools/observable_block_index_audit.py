#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = META.get('revision', 'rev0052')
REVUP = REV.upper()
ART_REL = f'artifacts/probe-results/{REVUP}_OBSERVABLE_BLOCK_INDEX_PRUNING.json'
MAN_REL = f'artifacts/run-manifests/{REVUP}_OBSERVABLE_BLOCK_INDEX_PRUNING_RUN_MANIFEST.json'
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
    if not art_path.exists():
        errors.append('missing artifact: ' + ART_REL)
        art = {}
    else:
        art = load(ART_REL)
    if not man_path.exists():
        errors.append('missing run manifest: ' + MAN_REL)
        man = {}
    else:
        man = load(MAN_REL)

    if art.get('revision') != REV:
        errors.append('artifact revision mismatch')
    if art.get('summary', {}).get('promotion_allowed') is not False:
        errors.append('observable block-index artifact must keep promotion blocked')
    if art.get('gpu_kernel_claim') is not False:
        errors.append('artifact must not claim GPU/fused-kernel evidence')
    if art.get('public_pretrained_trace_loaded') is not False:
        errors.append('artifact must not claim public/pretrained trace evidence')
    if man and art_path.exists() and man.get('artifact_sha256') != sha256_file(art_path):
        errors.append('run manifest artifact hash mismatch')
    src_rel = 'experiments/observable_block_index_pruning/observable_block_index_pruning.cpp'
    wrap_rel = 'experiments/observable_block_index_pruning/run_observable_block_index_pruning.py'
    if man:
        if man.get('source') != src_rel:
            errors.append('run manifest source path mismatch')
        if (ROOT / src_rel).exists() and man.get('source_sha256') != sha256_file(ROOT / src_rel):
            errors.append('run manifest source hash mismatch')
    for rel in [src_rel, wrap_rel]:
        if not (ROOT / rel).exists():
            errors.append('missing source/wrapper: ' + rel)

    rows = art.get('rows', []) if isinstance(art, dict) else []
    if len(rows) != 16:
        errors.append(f'expected 16 rows, got {len(rows)}')
    by = {(r.get('regime'), r.get('method')): r for r in rows}
    hist = [r for r in rows if r.get('method') == 'dense_score_mass_histogram_0p95_sparse']
    obs = [r for r in rows if r.get('method') == 'observable_mean_radius_block_pruned_0p95_sparse']
    unsafe = [r for r in rows if r.get('method') == 'unsafe_sampled_radius4_block_pruned_0p95_sparse']
    dense = [r for r in rows if r.get('method') == 'dense_full_attention']
    if len(hist) != 4 or len(obs) != 4 or len(unsafe) != 4 or len(dense) != 4:
        errors.append('expected four dense, histogram, observable, and unsafe rows')
    if any(r.get('selection_uses_values') or r.get('selection_uses_dense_output') for r in rows):
        errors.append('selector oracle leakage: values or dense outputs used during selection')
    if any(r.get('uses_generator_oracle_bounds') for r in rows):
        errors.append('generator-oracle block bounds should not appear in rev0052 current rows')
    if any(not r.get('computes_all_qk_scores_before_selection') for r in hist):
        errors.append('dense-score histogram rows must be marked dense-score dependent')
    if any(abs(float(r.get('qk_dot_fraction_vs_dense', 0.0)) - 1.0) > 1e-9 for r in hist):
        errors.append('dense-score histogram rows must have qk_dot_fraction_vs_dense == 1')

    for r in obs:
        if not r.get('observable_index_from_key_cache'):
            errors.append('observable block row missing observable_index_from_key_cache=true')
        if r.get('unsafe_sampled_radius'):
            errors.append('observable block row mislabeled unsafe')
        if not r.get('bound_is_certified'):
            errors.append('observable block row should be certified')
        if float(r.get('mean_bound_violation_rate', 1.0)) > 1e-12:
            errors.append('observable block row has nonzero bound violation rate')
        if r.get('exact_dense_scores_required'):
            errors.append('observable block row should not require dense exact scores')
    for r in unsafe:
        if not r.get('unsafe_sampled_radius'):
            errors.append('unsafe sampled-radius row missing unsafe flag')
        if r.get('bound_is_certified'):
            errors.append('unsafe sampled-radius row must not be certified')
        if float(r.get('mean_bound_violation_rate', 0.0)) <= 0.10:
            errors.append('unsafe sampled-radius row did not expose enough bound violations')

    tight = by.get(('tight_clustered_peaked_queries', 'observable_mean_radius_block_pruned_0p95_sparse'), {})
    multi = by.get(('tight_clustered_multipeak_queries', 'observable_mean_radius_block_pruned_0p95_sparse'), {})
    broad = by.get(('broad_unstructured_queries', 'observable_mean_radius_block_pruned_0p95_sparse'), {})
    loose = by.get(('loose_clustered_peaked_queries', 'observable_mean_radius_block_pruned_0p95_sparse'), {})
    unsafe_broad = by.get(('broad_unstructured_queries', 'unsafe_sampled_radius4_block_pruned_0p95_sparse'), {})
    if tight:
        if float(tight.get('qk_dot_fraction_vs_dense', 1.0)) >= 0.15:
            errors.append('tight observable index did not skip enough QK score work')
        if float(tight.get('quality_bar_rate', 0.0)) < 0.95:
            errors.append('tight observable index failed quality bar')
        if float(tight.get('speedup_vs_dense_with_index_reuse_32', 0.0)) <= 1.0:
            errors.append('tight observable index is not a reuse-amortized CPU speed win')
    else:
        errors.append('missing tight observable row')
    if multi:
        if float(multi.get('qk_dot_fraction_vs_dense', 1.0)) >= 0.50:
            errors.append('multipeak observable index opened too much score work for tight-bound regime')
        if float(multi.get('speedup_vs_dense_query_only', 1.0)) >= 1.0:
            warnings.append('multipeak tight-bound query path is not faster despite pruning; sorting/softmax overhead dominates on CPU')
    if broad:
        if float(broad.get('qk_dot_fraction_vs_dense', 0.0)) < 0.95:
            errors.append('broad observable index did not collapse toward dense QK work')
        if float(broad.get('speedup_vs_dense_query_only', 2.0)) >= 1.0:
            errors.append('broad observable index unexpectedly claims a CPU speed win')
    else:
        errors.append('missing broad observable row')
    if loose:
        if float(loose.get('qk_dot_fraction_vs_dense', 0.0)) < 0.95:
            errors.append('loose observable index did not collapse toward dense QK work')
    else:
        errors.append('missing loose observable row')
    if unsafe_broad and float(unsafe_broad.get('quality_bar_rate', 1.0)) >= 0.95:
        warnings.append('unsafe broad negative control still passes many rows; bound-violation flag, not quality alone, is the veto')

    report = {
        'project': 'CloudtainerML',
        'revision': REV,
        'report': 'observable_block_index_audit',
        'status': 'pass' if not errors else 'fail',
        'promotion_allowed': False,
        'artifact': ART_REL,
        'manifest': MAN_REL,
        'dense_rows_checked': len(dense),
        'histogram_rows_checked': len(hist),
        'observable_rows_checked': len(obs),
        'unsafe_rows_checked': len(unsafe),
        'tight_observable_qk_fraction': tight.get('qk_dot_fraction_vs_dense'),
        'tight_observable_speedup_reuse32': tight.get('speedup_vs_dense_with_index_reuse_32'),
        'multipeak_observable_qk_fraction': multi.get('qk_dot_fraction_vs_dense'),
        'broad_observable_qk_fraction': broad.get('qk_dot_fraction_vs_dense'),
        'loose_observable_qk_fraction': loose.get('qk_dot_fraction_vs_dense'),
        'unsafe_broad_bound_violation_rate': unsafe_broad.get('mean_bound_violation_rate'),
        'errors': errors,
        'warnings': warnings,
        'interpretation': 'rev0052 removes generator-bound privilege from the score-path pruning story. Observable key-cache centroids/radii still give a speed win only for tight peaked caches; broad and loose caches collapse toward dense scoring. The sampled-radius negative control shows that approximate block indexes can look sparse while their upper-bound certificate is false.',
    }
    (OUT / f'{REVUP}_OBSERVABLE_BLOCK_INDEX_AUDIT.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    md = [f'# Observable block-index audit — {REV}', '', f'**Status: {report["status"]}**', '', f'- tight observable QK fraction: `{report["tight_observable_qk_fraction"]}`', f'- tight speedup with 32-query index reuse: `{report["tight_observable_speedup_reuse32"]}`', f'- multipeak observable QK fraction: `{report["multipeak_observable_qk_fraction"]}`', f'- broad observable QK fraction: `{report["broad_observable_qk_fraction"]}`', f'- loose observable QK fraction: `{report["loose_observable_qk_fraction"]}`', f'- unsafe broad bound-violation rate: `{report["unsafe_broad_bound_violation_rate"]}`', '', '## Interpretation', '', report['interpretation']]
    if warnings:
        md += ['', '## Warnings', *[f'- {w}' for w in warnings]]
    if errors:
        md += ['', '## Errors', *[f'- {e}' for e in errors]]
    (OUT / f'{REVUP}_OBSERVABLE_BLOCK_INDEX_AUDIT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'errors': len(errors), 'warnings': len(warnings)}, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
