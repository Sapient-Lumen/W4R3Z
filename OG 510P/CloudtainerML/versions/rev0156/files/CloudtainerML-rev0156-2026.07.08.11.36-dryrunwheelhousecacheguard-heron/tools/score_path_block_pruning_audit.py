#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = META.get('revision', 'rev0051')
REVUP = REV.upper()
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)
ART_REL = f'artifacts/probe-results/{REVUP}_SCORE_PATH_BLOCK_PRUNING.json'


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
    if not (ROOT / ART_REL).exists():
        errors.append('missing score-path block-pruning artifact')
        data: dict[str, Any] = {}
    else:
        data = load(ART_REL)
    rows = data.get('rows', []) if isinstance(data, dict) else []
    by = {(r.get('regime'), r.get('method')): r for r in rows}
    summary = data.get('summary', {}) if isinstance(data, dict) else {}

    if data.get('revision') != REV:
        errors.append('artifact revision mismatch')
    if summary.get('promotion_allowed') is not False:
        errors.append('score-path artifact must keep promotion blocked')
    rp = data.get('run_provenance') or {}
    for key, hash_key in [('source_path', 'source_sha256'), ('wrapper_path', 'wrapper_sha256')]:
        rel = rp.get(key)
        expected = rp.get(hash_key)
        if not rel or not (ROOT / rel).exists():
            errors.append(f'missing provenance path: {key}')
        elif not expected or sha256_file(ROOT / rel) != expected:
            errors.append(f'provenance hash mismatch: {rel}')

    if any(r.get('is_gpu_kernel_claim') for r in rows):
        errors.append('GPU/fused-kernel claim leaked into CPU score-path artifact')
    if any(r.get('selection_uses_dense_output') for r in rows):
        errors.append('dense-output oracle leakage in selector rows')
    if any(r.get('selection_uses_values') for r in rows):
        errors.append('selector read value vectors in score-path artifact')

    hist_rows = [r for r in rows if r.get('method') == 'dense_score_mass_histogram_0p95_sparse']
    block_rows = [r for r in rows if r.get('method') == 'block_upper_bound_pruned_0p95_sparse']
    if len(hist_rows) != 4 or len(block_rows) != 4:
        errors.append('expected exactly four histogram and four block-pruned regime rows')
    if not all(r.get('computes_all_qk_scores_before_selection') is True for r in hist_rows):
        errors.append('dense-score histogram rows must state that all QK scores are computed before selection')
    if not all(abs(float(r.get('qk_dot_fraction_vs_dense', 0.0)) - 1.0) < 1e-9 for r in hist_rows):
        errors.append('dense-score histogram rows should have qk_dot_fraction_vs_dense == 1')
    if any(r.get('exact_dense_scores_required') for r in block_rows):
        errors.append('block-bound pruning rows should not require exact dense scores')
    if not all(r.get('block_upper_bound_pruning') is True for r in block_rows):
        errors.append('block rows missing block_upper_bound_pruning=true')
    if any(float(r.get('mean_lower_bound_mass_certificate', 0.0)) < 0.95 for r in block_rows):
        errors.append('block-bound mass certificate below target in at least one regime')

    peaked = by.get(('clustered_peaked_tight_bounds', 'block_upper_bound_pruned_0p95_sparse'), {})
    broad = by.get(('broad_unstructured_loose_bounds', 'block_upper_bound_pruned_0p95_sparse'), {})
    loose = by.get(('peaked_but_loose_bounds', 'block_upper_bound_pruned_0p95_sparse'), {})
    multi = by.get(('clustered_multipeak_tight_bounds', 'block_upper_bound_pruned_0p95_sparse'), {})
    if peaked:
        if float(peaked.get('qk_dot_fraction_vs_dense', 1.0)) >= 0.25:
            errors.append('tight peaked block pruning did not skip enough QK score work')
        if float(peaked.get('speedup_vs_dense', 0.0)) <= 1.0:
            errors.append('tight peaked block pruning was not a CPU speed win')
        if float(peaked.get('quality_bar_rate', 0.0)) < 0.95:
            errors.append('tight peaked block pruning failed quality bar')
    else:
        errors.append('missing tight peaked block-pruning row')
    if broad:
        if float(broad.get('qk_dot_fraction_vs_dense', 0.0)) < 0.90:
            errors.append('broad unstructured regime did not expose near-dense QK collapse')
        if float(broad.get('speedup_vs_dense', 2.0)) >= 1.0:
            errors.append('broad unstructured regime unexpectedly claims a speed win')
    else:
        errors.append('missing broad block-pruning row')
    if loose:
        if float(loose.get('qk_dot_fraction_vs_dense', 0.0)) < 0.90:
            errors.append('loose-bound peaked regime did not expose bound looseness collapse')
    else:
        errors.append('missing loose-bound block-pruning row')
    if multi and float(multi.get('quality_bar_rate', 1.0)) < 0.85:
        warnings.append('multipeak tight-bound row preserves mass but does not always pass output quality; use as a follow-up value-geometry stressor')

    report = {
        'project': 'CloudtainerML',
        'revision': REV,
        'report': 'score_path_block_pruning_audit',
        'status': 'pass' if not errors else 'fail',
        'promotion_allowed': False,
        'artifact': ART_REL,
        'histogram_rows_checked': len(hist_rows),
        'block_rows_checked': len(block_rows),
        'peaked_block_qk_dot_fraction': peaked.get('qk_dot_fraction_vs_dense'),
        'peaked_block_speedup_vs_dense': peaked.get('speedup_vs_dense'),
        'broad_block_qk_dot_fraction': broad.get('qk_dot_fraction_vs_dense'),
        'loose_block_qk_dot_fraction': loose.get('qk_dot_fraction_vs_dense'),
        'multipeak_block_quality_bar_rate': multi.get('quality_bar_rate'),
        'errors': errors,
        'warnings': warnings,
        'interpretation': 'rev0051 closes a claim-boundary gap: dense-score sparse selectors are not allowed to imply score-path sparsity. The block-bound path shows score computation can be skipped in a tight clustered regime, but broad or loose-bound regimes correctly collapse toward dense scoring.',
    }
    (OUT / f'{REVUP}_SCORE_PATH_BLOCK_PRUNING_AUDIT.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    md = [f'# Score-path block-pruning audit — {REV}', '', f'**Status: {report["status"]}**', '', f'- peaked QK fraction: `{report["peaked_block_qk_dot_fraction"]}`', f'- peaked speedup vs dense: `{report["peaked_block_speedup_vs_dense"]}`', f'- broad QK fraction: `{report["broad_block_qk_dot_fraction"]}`', f'- loose-bound QK fraction: `{report["loose_block_qk_dot_fraction"]}`', f'- multipeak quality rate: `{report["multipeak_block_quality_bar_rate"]}`', '', '## Interpretation', '', report['interpretation']]
    if warnings:
        md += ['', '## Warnings', *[f'- {w}' for w in warnings]]
    if errors:
        md += ['', '## Errors', *[f'- {e}' for e in errors]]
    (OUT / f'{REVUP}_SCORE_PATH_BLOCK_PRUNING_AUDIT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'errors': len(errors), 'warnings': len(warnings)}, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
