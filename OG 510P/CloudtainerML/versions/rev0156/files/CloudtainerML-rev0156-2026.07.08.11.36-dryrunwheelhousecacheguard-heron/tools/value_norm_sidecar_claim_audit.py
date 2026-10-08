#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = META.get('revision', 'rev0050')
REVUP = REV.upper()
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)
ART_REL = f'artifacts/probe-results/{REVUP}_VALUE_NORM_SIDECAR_CPU_PATH.json'


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


def load(rel: str) -> Any:
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


def row(rows: list[dict[str, Any]], regime: str, method: str) -> dict[str, Any]:
    for r in rows:
        if r.get('regime') == regime and r.get('method') == method:
            return r
    return {}


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    if not (ROOT / ART_REL).exists():
        errors.append('missing sidecar CPU path artifact')
        payload: dict[str, Any] = {}
    else:
        payload = load(ART_REL)
    rows = payload.get('rows', [])
    summary = payload.get('summary', {})
    contract = payload.get('sidecar_contract', {})
    required_regimes = {'peaked_bounded', 'broad_bounded', 'peaked_tail_norm_spikes'}
    required_methods = {
        'dense_full_softmax',
        'exact_topk_32_sparse',
        'mass_histogram_0p95_sparse',
        'value_norm_exception_sidecar_0p95_sparse',
        'value_norm_exception_onthefly_0p95_sparse',
    }
    regimes = {r.get('regime') for r in rows}
    methods = {r.get('method') for r in rows}
    missing_regimes = sorted(required_regimes - regimes)
    missing_methods = sorted(required_methods - methods)
    if missing_regimes:
        errors.append('missing regimes: ' + ', '.join(missing_regimes))
    if missing_methods:
        errors.append('missing methods: ' + ', '.join(missing_methods))
    if payload.get('revision') != REV:
        errors.append('revision mismatch in sidecar artifact')
    if payload.get('kind') != 'cpp_native_cpu_row_attention_sidecar_microbench':
        errors.append('wrong sidecar artifact kind')
    if payload.get('summary', {}).get('promotion_allowed') is not False:
        errors.append('sidecar artifact must not allow promotion')
    if contract.get('value_norm_bound_update_mode') != 'incremental_aggregate':
        errors.append('sidecar contract does not record incremental aggregate bound update')
    if contract.get('sidecar_selection_reads_value_vectors') is not False:
        errors.append('sidecar contract must say precomputed sidecar selection does not read V vectors')
    if contract.get('on_the_fly_norms_read_value_vectors_for_selection') is not True:
        errors.append('on-the-fly negative control must record V reads during selection')

    for r in rows:
        if r.get('is_gpu_kernel_claim') is not False:
            errors.append('GPU kernel claim leaked into row: ' + str((r.get('regime'), r.get('method'))))
        if r.get('selection_uses_dense_output') is not False:
            errors.append('dense-output selector leakage in row: ' + str((r.get('regime'), r.get('method'))))
        if r.get('method') == 'value_norm_exception_sidecar_0p95_sparse':
            if r.get('uses_precomputed_sidecar') is not True:
                errors.append('sidecar method missing uses_precomputed_sidecar=true')
            if r.get('selection_uses_values') is not False:
                errors.append('sidecar method should not read value vectors during selection')
            if float(r.get('mean_norm_metadata_reads', 0.0)) <= 0:
                errors.append('sidecar method did not count norm metadata reads')
            if float(r.get('mean_value_reads_for_selection', 1.0)) != 0.0:
                errors.append('sidecar method counted value-vector reads during selection')
        if r.get('method') == 'value_norm_exception_onthefly_0p95_sparse':
            if r.get('selection_uses_values') is not True:
                errors.append('on-the-fly negative control should flag selection_uses_values=true')
            if float(r.get('mean_value_reads_for_selection', 0.0)) < float(payload.get('N', 0)):
                errors.append('on-the-fly negative control did not count all value reads for norm computation')

    tail_mass = row(rows, 'peaked_tail_norm_spikes', 'mass_histogram_0p95_sparse')
    tail_side = row(rows, 'peaked_tail_norm_spikes', 'value_norm_exception_sidecar_0p95_sparse')
    tail_onfly = row(rows, 'peaked_tail_norm_spikes', 'value_norm_exception_onthefly_0p95_sparse')
    broad_side = row(rows, 'broad_bounded', 'value_norm_exception_sidecar_0p95_sparse')
    if tail_mass and float(tail_mass.get('quality_bar_rate', 1.0)) > 0.20:
        errors.append('tail stress did not expose mass-only quality failure')
    if tail_side and float(tail_side.get('quality_bar_rate', 0.0)) < 0.95:
        errors.append('sidecar exception path did not repair tail quality')
    if tail_onfly and tail_side and abs(float(tail_onfly.get('quality_bar_rate', 0.0)) - float(tail_side.get('quality_bar_rate', 0.0))) > 1e-9:
        errors.append('on-the-fly and sidecar quality diverged unexpectedly')
    if broad_side and float(broad_side.get('selected_fraction', 0.0)) < 0.90:
        errors.append('broad bounded regime did not expose near-dense value reads')

    # Source/refactor checks: the Python and C++ implementations must use the rev0050
    # incremental aggregate update rather than rescanning every token per exception.
    core_src = (ROOT / 'experiments/attention_compiler_core/attention_core.py').read_text(encoding='utf-8')
    cpp_src = (ROOT / 'experiments/value_norm_sidecar_cpu_path/value_norm_sidecar_cpu_path.cpp').read_text(encoding='utf-8')
    source_contracts = {
        'python_core_bound_update_incremental': 'bound_update_mode": "incremental_aggregate"' in core_src or "bound_update_mode': 'incremental_aggregate'" in core_src,
        'cpp_sidecar_bound_update_incremental': 'value_norm_bound_update_mode\\\": \\\"incremental_aggregate' in cpp_src or 'rev0050 refactor: compute certificate aggregates once' in cpp_src,
        'cpp_negative_control_computes_norms_from_values': 'select_value_norm_exception_on_the_fly' in cpp_src and 'compute_norms_from_values(r)' in cpp_src,
        'cpp_sidecar_method_uses_precomputed_norms': 'select_value_norm_exception_sidecar' in cpp_src and 'r.norms' in cpp_src,
    }
    for k, ok in source_contracts.items():
        if not ok:
            errors.append('missing source contract: ' + k)

    rp = payload.get('run_provenance') or {}
    source_rel = rp.get('source_path')
    if not source_rel or not (ROOT / source_rel).exists():
        errors.append('missing run provenance source')
    elif rp.get('source_sha256') != sha256_file(ROOT / source_rel):
        errors.append('run provenance source hash mismatch')

    sidecar_speedups = [float(r.get('speedup_vs_dense', 0.0)) for r in rows if r.get('method') == 'value_norm_exception_sidecar_0p95_sparse']
    cpu_sidecar_any_speed_win = any(v > 1.0 for v in sidecar_speedups)
    if not cpu_sidecar_any_speed_win:
        warnings.append('precomputed sidecar repaired quality but was not a CPU speed win in these regimes')

    report = {
        'project': 'CloudtainerML',
        'revision': REV,
        'report': 'value_norm_sidecar_claim_audit',
        'status': 'pass' if not errors else 'fail',
        'promotion_allowed': False,
        'artifact': ART_REL,
        'row_count': len(rows),
        'regimes': sorted(regimes),
        'methods': sorted(methods),
        'source_contracts': source_contracts,
        'tail_mass_hist_quality_rate': tail_mass.get('quality_bar_rate'),
        'tail_sidecar_quality_rate': tail_side.get('quality_bar_rate'),
        'tail_sidecar_speedup_excluding_build': tail_side.get('speedup_vs_dense'),
        'tail_sidecar_speedup_reuse_32': tail_side.get('speedup_vs_dense_with_sidecar_build_reuse_32'),
        'broad_sidecar_selected_fraction': broad_side.get('selected_fraction'),
        'cpu_sidecar_any_speed_win': cpu_sidecar_any_speed_win,
        'errors': errors,
        'warnings': warnings,
        'interpretation': 'rev0050 removes the free value-norm metadata assumption. The sidecar path repairs value-tail quality without reading V vectors during selection, but the measured native CPU implementation is not a speed win here; on-the-fly norm computation is correctly demoted because it reads all V vectors during selection.',
    }
    (OUT / f'{REVUP}_VALUE_NORM_SIDECAR_CLAIM_AUDIT.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    md = [f'# Value-norm sidecar claim audit — {REV}', '', f'**Status: {report["status"]}**', '', f'- artifact: `{ART_REL}`', f'- tail mass-hist quality rate: `{report["tail_mass_hist_quality_rate"]}`', f'- tail sidecar quality rate: `{report["tail_sidecar_quality_rate"]}`', f'- tail sidecar speedup excluding build: `{report["tail_sidecar_speedup_excluding_build"]}`', f'- tail sidecar speedup with 32x sidecar reuse: `{report["tail_sidecar_speedup_reuse_32"]}`', f'- broad sidecar selected fraction: `{report["broad_sidecar_selected_fraction"]}`', '', '## Interpretation', '', report['interpretation']]
    if warnings:
        md += ['', '## Warnings', *[f'- {w}' for w in warnings]]
    if errors:
        md += ['', '## Errors', *[f'- {e}' for e in errors]]
    (OUT / f'{REVUP}_VALUE_NORM_SIDECAR_CLAIM_AUDIT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'errors': len(errors), 'warnings': len(warnings), 'tail_sidecar_quality_rate': report['tail_sidecar_quality_rate'], 'cpu_sidecar_any_speed_win': cpu_sidecar_any_speed_win}, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
