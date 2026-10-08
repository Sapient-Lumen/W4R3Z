#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = META.get('revision', 'rev0058')
REVUP = REV.upper()
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    current = [
        f'artifacts/probe-results/{REVUP}_FUSED_STREAMING_SCHEDULE_TAX.json',
        f'artifacts/probe-results/{REVUP}_FUSED_STREAMING_SCHEDULE_NATIVE.json',
        f'artifacts/run-manifests/{REVUP}_FUSED_STREAMING_SCHEDULE_TAX_RUN_MANIFEST.json',
    ]
    missing = [rel for rel in current if not (ROOT / rel).exists()]
    errors += ['missing current artifact: ' + rel for rel in missing]
    art = load(current[0]) if (ROOT / current[0]).exists() else {}
    native = load(current[1]) if (ROOT / current[1]).exists() else {}
    man = load(current[2]) if (ROOT / current[2]).exists() else {}
    rows = native.get('rows', []) if native else []
    summary = art.get('summary', {}) if art else {}

    def row(method: str, regime: str):
        matches = [r for r in rows if r.get('method') == method and r.get('regime') == regime]
        return matches[0] if matches else None

    if art:
        if art.get('promotion_allowed') is not False:
            errors.append('fused schedule artifact overclaims promotion')
        if art.get('gpu_kernel_claim') is not False or art.get('gpu_fused_kernel_measured') is not False:
            errors.append('artifact overclaims GPU/fused-kernel measurement')
        if art.get('public_pretrained_trace_loaded') is not False:
            errors.append('artifact overclaims public/pretrained trace evidence')
        scope = str(art.get('measurement_scope', '')).lower()
        if 'native cpu' not in scope or 'not gpu' not in scope or 'not a fused cuda kernel' not in scope:
            errors.append('measurement scope does not clearly fence out GPU/CUDA kernel claims')
        if summary.get('streaming_recompute_schedule_tax_exposed') is not True:
            errors.append('streaming recompute schedule tax was not exposed')
        if summary.get('materialized_path_requires_global_score_storage') is not True:
            errors.append('materialized histogram path was not marked as requiring score storage')
        if summary.get('streaming_path_avoids_global_score_storage') is not True:
            errors.append('streaming path was not marked as score-storage-free')
        if summary.get('mass_only_value_tail_failure_still_visible') is not True:
            errors.append('value-tail mass-only failure should remain visible')
    if native:
        gpu_probe = native.get('gpu_environment_probe', {})
        if gpu_probe.get('gpu_kernel_measured') is not False:
            errors.append('native GPU probe claims measured kernel')
        regimes = {r.get('regime') for r in rows}
        required_regimes = {'peaked_low_support', 'medium_support', 'broad_high_entropy', 'value_tail_outlier'}
        if not required_regimes.issubset(regimes):
            errors.append('missing required regimes: ' + ', '.join(sorted(required_regimes - regimes)))
        for regime in required_regimes:
            mat = row('materialized_score_histogram_mass_0p95', regime)
            stream = row('streaming_recompute_histogram_mass_0p95', regime)
            dense = row('dense_online_one_pass', regime)
            if not (mat and stream and dense):
                errors.append('missing dense/materialized/streaming rows for ' + regime)
                continue
            if float(mat.get('mean_score_memory_writes', -1)) < float(native.get('n_ctx', 1024)):
                errors.append('materialized path did not charge global score writes for ' + regime)
            if float(stream.get('mean_score_memory_writes', -1)) != 0.0:
                errors.append('streaming path unexpectedly writes scores for ' + regime)
            if float(stream.get('qk_dot_fraction_vs_dense_online', 0)) < 3.0:
                errors.append('streaming path did not charge QK recompute/schedule tax for ' + regime)
            if stream.get('materialization_free_streaming') is not True:
                errors.append('streaming path not labeled materialization-free for ' + regime)
            if mat.get('materializes_scores') is not True:
                errors.append('materialized path not labeled materializing for ' + regime)
            if mat.get('uses_values_for_selection') or stream.get('uses_values_for_selection'):
                errors.append('selector uses values in ' + regime)
            if mat.get('uses_dense_output_for_selection') or stream.get('uses_dense_output_for_selection'):
                errors.append('selector uses dense output in ' + regime)
        tail = row('materialized_score_histogram_mass_0p95', 'value_tail_outlier')
        if tail and float(tail.get('quality_bar_rate', 1.0)) >= 1.0:
            errors.append('value-tail mass-only quality failure disappeared unexpectedly')
    if man and (ROOT / current[0]).exists() and (ROOT / current[1]).exists():
        if man.get('artifact_sha256') != sha256_file(ROOT / current[0]):
            errors.append('run manifest artifact hash mismatch')
        if man.get('native_artifact_sha256') != sha256_file(ROOT / current[1]):
            errors.append('run manifest native artifact hash mismatch')
        if man.get('gpu_kernel_claim') is not False:
            errors.append('run manifest overclaims GPU kernel claim')

    source_paths = [
        'experiments/fused_streaming_schedule/fused_streaming_schedule.cpp',
        'experiments/fused_streaming_schedule/run_fused_streaming_schedule.py',
        'tools/fused_streaming_schedule_audit.py',
    ]
    for rel in source_paths:
        if not (ROOT / rel).exists():
            errors.append('missing source/refactor file: ' + rel)

    report = {
        'project': 'CloudtainerML',
        'revision': REV,
        'report': 'fused_streaming_schedule_audit',
        'status': 'pass' if not errors else 'fail',
        'promotion_allowed': False,
        'current_artifacts': current,
        'missing_current_artifacts': missing,
        'max_materialized_minus_streaming_speedup_gap': summary.get('max_materialized_minus_streaming_speedup_gap'),
        'mean_materialized_minus_streaming_speedup_gap': summary.get('mean_materialized_minus_streaming_speedup_gap'),
        'streaming_recompute_qk_fraction_by_regime': summary.get('streaming_recompute_qk_fraction_by_regime'),
        'materialized_score_writes_by_regime': summary.get('materialized_score_writes_by_regime'),
        'streaming_score_writes_by_regime': summary.get('streaming_score_writes_by_regime'),
        'value_tail_mass_only_quality_materialized': summary.get('value_tail_mass_only_quality_materialized'),
        'gpu_environment_probe': native.get('gpu_environment_probe', {}) if native else {},
        'errors': errors,
        'warnings': warnings,
        'interpretation': 'rev0058 audits the schedule tax hidden by materialized dense-score selectors. The materialized path can look faster on CPU because it stores all scores; the score-storage-free streaming path avoids global score memory but pays QK recomputation and remains non-promotional without actual GPU/fused-kernel timing.',
    }
    (OUT / f'{REVUP}_FUSED_STREAMING_SCHEDULE_AUDIT.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    md = [
        f'# Fused streaming schedule audit — {REV}', '',
        f'**Status: {report["status"]}**', '',
        f'- max materialized-minus-streaming speedup gap: `{report["max_materialized_minus_streaming_speedup_gap"]}`',
        f'- streaming QK fractions: `{report["streaming_recompute_qk_fraction_by_regime"]}`',
        f'- materialized score writes: `{report["materialized_score_writes_by_regime"]}`',
        f'- streaming score writes: `{report["streaming_score_writes_by_regime"]}`',
        f'- value-tail mass-only quality rate: `{report["value_tail_mass_only_quality_materialized"]}`',
        '', '## Interpretation', '', report['interpretation'],
    ]
    if warnings:
        md += ['', '## Warnings', *[f'- {w}' for w in warnings]]
    if errors:
        md += ['', '## Errors', *[f'- {e}' for e in errors]]
    (OUT / f'{REVUP}_FUSED_STREAMING_SCHEDULE_AUDIT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'errors': len(errors), 'warnings': len(warnings)}, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
