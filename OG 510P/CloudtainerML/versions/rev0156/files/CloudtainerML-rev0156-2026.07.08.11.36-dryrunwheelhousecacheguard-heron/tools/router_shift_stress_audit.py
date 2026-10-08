#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = META.get('revision', 'rev0055')
REVUP = REV.upper()
ART_REL = f'artifacts/probe-results/{REVUP}_ROUTER_SHIFT_STRESS.json'
MAN_REL = f'artifacts/run-manifests/{REVUP}_ROUTER_SHIFT_STRESS_RUN_MANIFEST.json'
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
        errors.append('missing router shift artifact: ' + ART_REL)
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
            errors.append('router shift artifact must keep promotion blocked')
        if art.get('public_pretrained_trace_loaded') is not False:
            errors.append('artifact must not claim public/pretrained trace evidence')
        if art.get('gpu_kernel_claim') is not False:
            errors.append('artifact must not claim GPU/fused kernel evidence')
        if float(art.get('train_metrics', {}).get('eval_accuracy', 0.0)) < 0.95:
            errors.append('tiny trace model did not train to high accuracy')
        if int(art.get('raw_case_count', 0)) < 90:
            errors.append('too few raw cases for shift stress')
        if 'heldout quality labels' not in art.get('selection_contract', ''):
            errors.append('selection contract does not explicitly forbid heldout quality label leakage')

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
    if len(rows) < 40:
        errors.append(f'expected at least 40 scenario rows, got {len(rows)}')
    if any(r.get('selection_uses_values') or r.get('selection_uses_dense_output') for r in rows):
        errors.append('selector oracle leakage: values or dense output used during routing/selection')
    if any(r.get('public_pretrained_trace_loaded') or r.get('gpu_kernel_claim') for r in rows):
        errors.append('row-level public/GPU claim leaked')

    summary = art.get('summary', {}) if art else {}
    if summary.get('low_only_to_high_is_slower_than_dense') is not True:
        errors.append('OOD negative control did not expose low-support calibration as dense-worse')
    if float(summary.get('low_only_to_high_speedup_proxy_vs_dense') or 9.0) >= 1.0:
        errors.append('low-support calibration should be slower than dense on high-support test')
    if summary.get('bucket_robust_to_high_beats_dense') is not True:
        errors.append('bucket-robust calibration did not beat dense on high-support test')
    if summary.get('bucket_robust_to_high_beats_low_only_shifted') is not True:
        errors.append('bucket-robust calibration did not improve over shifted low-only router')
    if float(summary.get('bucket_robust_to_high_quality_bar_rate') or 0.0) < 0.985:
        errors.append('bucket-robust high-support quality below floor')
    if summary.get('bucket_robust_to_high_beats_histogram_equal_units') is not False:
        errors.append('summary should preserve the equal-unit histogram baseline as unbeaten')
    low_cfg = art.get('calibrations', {}).get('low_only', {}).get('selected_config', {})
    robust_cfg = art.get('calibrations', {}).get('bucket_robust', {}).get('selected_config', {})
    if float(robust_cfg.get('hist_selected_fraction_threshold', 0.0)) <= float(low_cfg.get('hist_selected_fraction_threshold', 0.0)):
        errors.append('robust calibration did not relax histogram threshold relative to low-only negative control')
    if art.get('calibrations', {}).get('bucket_robust', {}).get('selection_reason') != 'minimize_worst_support_slice_work_subject_to_each_slice_quality_floor':
        errors.append('bucket-robust calibration reason missing or wrong')

    # Direct row checks for the main OOD scenario.
    by = {(r.get('scenario'), r.get('method')): r for r in rows}
    low_to_high = by.get(('ood_low_calibration_high_support_test', 'min_work_on_low_support'), {})
    robust_high = by.get(('ood_low_calibration_high_support_test', 'bucket_robust_minimax_low_mid_high'), {})
    dense_high = by.get(('ood_low_calibration_high_support_test', 'dense_full_attention'), {})
    hist_high = by.get(('ood_low_calibration_high_support_test', 'dense_score_mass_histogram_0p95_sparse'), {})
    if low_to_high and dense_high and float(low_to_high.get('mean_total_work_units', 0.0)) <= float(dense_high.get('mean_total_work_units', 1e9)):
        errors.append('low-support calibrated router row is not dense-worse on high-support test')
    if robust_high and dense_high and float(robust_high.get('mean_total_work_units', 1e9)) >= float(dense_high.get('mean_total_work_units', 0.0)):
        errors.append('robust router row does not beat dense on high-support test')
    if robust_high and hist_high and float(robust_high.get('mean_total_work_units', 0.0)) <= float(hist_high.get('mean_total_work_units', 1e9)):
        warnings.append('robust router beat histogram under equal units; interpretation may need updating')
    else:
        warnings.append('dense-score histogram remains unbeaten under equal units on the high-support shift test')

    report = {
        'project': 'CloudtainerML',
        'revision': REV,
        'report': 'router_shift_stress_audit',
        'status': 'pass' if not errors else 'fail',
        'promotion_allowed': False,
        'artifact': ART_REL,
        'manifest': MAN_REL,
        'train_eval_accuracy': art.get('train_metrics', {}).get('eval_accuracy') if art else None,
        'raw_case_count': art.get('raw_case_count') if art else None,
        'scenario_rows': len(rows),
        'low_only_to_high_work_units': summary.get('low_only_to_high_mean_work_units'),
        'low_only_to_high_speedup': summary.get('low_only_to_high_speedup_proxy_vs_dense'),
        'bucket_robust_to_high_work_units': summary.get('bucket_robust_to_high_mean_work_units'),
        'bucket_robust_to_high_speedup': summary.get('bucket_robust_to_high_speedup_proxy_vs_dense'),
        'histogram_high_work_units': summary.get('histogram_high_mean_work_units'),
        'dense_high_work_units': summary.get('dense_high_mean_work_units'),
        'low_only_config': low_cfg,
        'bucket_robust_config': robust_cfg,
        'errors': errors,
        'warnings': warnings,
        'interpretation': 'rev0055 exposes a real router-calibration failure: thresholds tuned only on low-support rows route high-support rows to dense full attention after precheck overhead and become slower than dense. Bucket-robust calibration fixes that shifted failure on the tiny trace, but does not beat the dense-score histogram under equal units, so promotion remains blocked.',
    }
    (OUT / f'{REVUP}_ROUTER_SHIFT_STRESS_AUDIT.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    md = [
        f'# Router shift stress audit — {REV}', '', f'**Status: {report["status"]}**', '',
        f'- train eval accuracy: `{report["train_eval_accuracy"]}`',
        f'- raw cases: `{report["raw_case_count"]}`',
        f'- low-only → high-support work units: `{report["low_only_to_high_work_units"]}`',
        f'- low-only → high-support speedup vs dense: `{report["low_only_to_high_speedup"]}`',
        f'- bucket-robust → high-support work units: `{report["bucket_robust_to_high_work_units"]}`',
        f'- bucket-robust → high-support speedup vs dense: `{report["bucket_robust_to_high_speedup"]}`',
        f'- dense-score histogram high-support work units: `{report["histogram_high_work_units"]}`',
        '', '## Interpretation', '', report['interpretation']
    ]
    if warnings:
        md += ['', '## Warnings', *[f'- {w}' for w in warnings]]
    if errors:
        md += ['', '## Errors', *[f'- {e}' for e in errors]]
    (OUT / f'{REVUP}_ROUTER_SHIFT_STRESS_AUDIT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'errors': len(errors), 'warnings': len(warnings)}, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
