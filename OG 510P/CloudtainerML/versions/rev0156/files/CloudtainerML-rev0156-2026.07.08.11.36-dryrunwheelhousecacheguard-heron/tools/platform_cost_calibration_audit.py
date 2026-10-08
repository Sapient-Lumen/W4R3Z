#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = META.get('revision', 'rev0057')
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
    art_rel = f'artifacts/probe-results/{REVUP}_PLATFORM_COST_CALIBRATED_ROUTER.json'
    native_rel = f'artifacts/probe-results/{REVUP}_PLATFORM_PRIMITIVE_COST_NATIVE.json'
    man_rel = f'artifacts/run-manifests/{REVUP}_PLATFORM_COST_CALIBRATED_ROUTER_RUN_MANIFEST.json'
    for rel in [art_rel, native_rel, man_rel]:
        if not (ROOT / rel).exists():
            errors.append('missing platform cost calibration file: ' + rel)
    art = load(art_rel) if (ROOT / art_rel).exists() else {}
    native = load(native_rel) if (ROOT / native_rel).exists() else {}
    man = load(man_rel) if (ROOT / man_rel).exists() else {}
    if art:
        if art.get('promotion_allowed') is not False or art.get('summary', {}).get('promotion_allowed') is not False:
            errors.append('platform calibration overclaims promotion')
        if art.get('gpu_kernel_claim') is not False or art.get('public_pretrained_trace_loaded') is not False:
            errors.append('platform calibration overclaims public/GPU evidence')
        scope = str(art.get('measurement_scope', '')).lower()
        if 'native cpu primitive' not in scope or 'not a fused attention kernel' not in scope:
            errors.append('measurement scope does not explicitly limit claim to CPU primitives')
        summary = art.get('summary', {})
        qk = summary.get('measured_qk_weight_router_d8_vs_sequential_value_accum')
        br = summary.get('rev0056_first_qk_weight_router_beats_histogram_all')
        if not isinstance(qk, (int, float)) or qk <= 0:
            errors.append('missing positive measured qk/value ratio')
        if not isinstance(br, (int, float)) or br <= 1.0:
            errors.append('missing rev0056 all-row break-even greater than one')
        if isinstance(qk, (int, float)) and isinstance(br, (int, float)) and not (qk < br):
            errors.append('measured qk/value ratio unexpectedly reaches router break-even')
        if summary.get('measured_router_beats_histogram_all_seq8') is not False:
            errors.append('measured CPU d8 model should not promote router over histogram on all rows')
        if summary.get('measured_router_beats_histogram_high_support_seq8') is not False:
            errors.append('measured CPU d8 model should not promote router over histogram on high-support rows')
        if summary.get('measured_platform_cost_model_claim_blocked') is not True:
            errors.append('measured platform claim gate did not block promotion')
        comps = art.get('measured_cost_comparisons_seq_value', [])
        low = [c for c in comps if c.get('selector') == 'low_support']
        if low and low[0].get('router_beats_histogram') is True:
            warnings.append('router beats histogram only on low-support slice under measured CPU ratio; all-row/high-support gates remain blocking')
        for row in comps + art.get('measured_cost_comparisons_sparse_gather_value', []):
            if row.get('router_quality_bar_rate', 0) < 0.985 or row.get('histogram_quality_bar_rate', 0) < 0.985:
                errors.append('quality floor violated in measured comparison: ' + str(row.get('selector')))
    if native:
        rows = native.get('rows', [])
        primitives = {(r.get('primitive'), int(r.get('d', -1))) for r in rows}
        required = {
            ('qk_dot_sequential', 8),
            ('value_accumulate_sequential', 8),
            ('value_accumulate_sparse_gather', 8),
            ('block_centroid_bound_dot', 8),
            ('qk_dot_sequential', 64),
            ('value_accumulate_sequential', 64),
            ('value_accumulate_sparse_gather', 64),
        }
        missing = sorted(required - primitives)
        if missing:
            errors.append('native primitive measurements missing: ' + repr(missing))
        for r in rows:
            if float(r.get('ns_per_vector', 0)) <= 0:
                errors.append('nonpositive primitive timing for ' + str(r.get('primitive')))
            if int(r.get('vectors', 0)) < 100000:
                warnings.append('low primitive vector count for ' + str(r.get('primitive')))
    if man and (ROOT / art_rel).exists():
        if man.get('artifact_sha256') != sha256_file(ROOT / art_rel):
            errors.append('manifest artifact hash mismatch')
        if man.get('native_artifact_sha256') != sha256_file(ROOT / native_rel):
            errors.append('manifest native artifact hash mismatch')
        if man.get('gpu_kernel_claim') is not False or man.get('public_pretrained_trace_loaded') is not False:
            errors.append('manifest overclaims public/GPU evidence')
    summary = art.get('summary', {}) if art else {}
    report = {
        'project': 'CloudtainerML',
        'revision': REV,
        'report': 'platform_cost_calibration_audit',
        'status': 'pass' if not errors else 'fail',
        'promotion_allowed': False,
        'artifact': art_rel,
        'native_artifact': native_rel,
        'manifest': man_rel,
        'measured_qk_weight_router_d8_vs_sequential_value_accum': summary.get('measured_qk_weight_router_d8_vs_sequential_value_accum'),
        'measured_qk_weight_router_d8_vs_sparse_gather_value_accum': summary.get('measured_qk_weight_router_d8_vs_sparse_gather_value_accum'),
        'rev0056_first_qk_weight_router_beats_histogram_all': summary.get('rev0056_first_qk_weight_router_beats_histogram_all'),
        'break_even_gap_ratio_all_vs_measured_seq8': summary.get('break_even_gap_ratio_all_vs_measured_seq8'),
        'measured_router_beats_histogram_all_seq8': summary.get('measured_router_beats_histogram_all_seq8'),
        'measured_router_beats_histogram_high_support_seq8': summary.get('measured_router_beats_histogram_high_support_seq8'),
        'errors': errors,
        'warnings': warnings,
        'interpretation': 'rev0057 audits a measured CPU primitive calibration against the rev0056 router cost frontier. The measured d=8 QK/value ratio is far below the all-row break-even required for the adaptive router to beat the dense-score histogram, so measured-platform promotion remains blocked.',
    }
    (OUT / f'{REVUP}_PLATFORM_COST_CALIBRATION_AUDIT.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    md = [
        f'# Platform cost calibration audit — {REV}', '',
        f'**Status: {report["status"]}**', '',
        f'- measured d=8 QK/value ratio: `{report["measured_qk_weight_router_d8_vs_sequential_value_accum"]}`',
        f'- measured d=8 QK/sparse-gather-value ratio: `{report["measured_qk_weight_router_d8_vs_sparse_gather_value_accum"]}`',
        f'- rev0056 all-row break-even: `{report["rev0056_first_qk_weight_router_beats_histogram_all"]}`',
        f'- break-even / measured ratio: `{report["break_even_gap_ratio_all_vs_measured_seq8"]}`',
        f'- router beats histogram on all rows under measured CPU ratio: `{report["measured_router_beats_histogram_all_seq8"]}`',
        '', '## Interpretation', '', report['interpretation'],
    ]
    if warnings:
        md += ['', '## Warnings', *[f'- {w}' for w in warnings]]
    if errors:
        md += ['', '## Errors', *[f'- {e}' for e in errors]]
    (OUT / f'{REVUP}_PLATFORM_COST_CALIBRATION_AUDIT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'errors': len(errors), 'warnings': len(warnings)}, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
