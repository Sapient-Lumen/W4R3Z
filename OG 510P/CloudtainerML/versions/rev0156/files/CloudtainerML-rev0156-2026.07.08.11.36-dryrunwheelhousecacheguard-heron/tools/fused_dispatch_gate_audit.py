#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = META.get('revision', 'rev0059')
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
        f'artifacts/probe-results/{REVUP}_FUSED_DISPATCH_GATE.json',
        f'artifacts/run-manifests/{REVUP}_FUSED_DISPATCH_GATE_RUN_MANIFEST.json',
        'experiments/fused_dispatch_gate/fused_dispatch_gate.py',
    ]
    missing = [rel for rel in current if not (ROOT / rel).exists()]
    errors += ['missing current dispatch artifact/source: ' + rel for rel in missing]
    art = load(current[0]) if (ROOT / current[0]).exists() else {}
    man = load(current[1]) if (ROOT / current[1]).exists() else {}
    summary = art.get('summary', {}) if art else {}
    policies = art.get('policy_summaries', {}) if art else {}
    decisions = art.get('dispatch_decisions', []) if art else []

    if art:
        if art.get('promotion_allowed') is not False or summary.get('promotion_allowed') is not False:
            errors.append('dispatch gate overclaims promotion')
        if art.get('gpu_kernel_claim') is not False or art.get('gpu_fused_kernel_measured') is not False:
            errors.append('dispatch artifact overclaims GPU/fused kernel evidence')
        if art.get('public_pretrained_trace_loaded') is not False:
            errors.append('dispatch artifact overclaims public/pretrained trace evidence')
        scope = str(art.get('measurement_scope', '')).lower()
        if 'native cpu' not in scope or 'not gpu' not in scope or 'not a fused cuda' not in scope:
            errors.append('measurement scope does not fence out GPU/fused kernel claims')
        if summary.get('strict_materialization_free_sparse_promoted') is not False:
            errors.append('strict materialization-free sparse path was promoted')
        if summary.get('strict_materialization_free_sparse_regimes') not in ([], None):
            errors.append('strict materialization-free gate should choose no sparse regimes')
        if summary.get('score_storage_forbidden_no_sparse_speed_win') is not True:
            errors.append('score-storage-forbidden no-win veto missing')
        if summary.get('near_dense_value_read_veto_active') is not True:
            errors.append('near-dense value-read veto not active')
        if summary.get('value_tail_dense_fallback_under_safe_gates') is not True:
            errors.append('value-tail safe-gate dense fallback missing')
        if summary.get('streaming_path_avoids_global_score_storage_but_pays_qk_schedule_tax') is not True:
            errors.append('streaming QK schedule tax not recorded')
        if summary.get('materialized_path_requires_global_score_storage') is not True:
            errors.append('materialized score-storage requirement not recorded')
        false_wins = summary.get('speed_only_materialized_negative_control_near_dense_false_wins', [])
        if not {'medium_support', 'broad_high_entropy'}.issubset(set(false_wins)):
            errors.append('speed-only negative control failed to expose near-dense false wins')
        storage_allowed = policies.get('score_storage_allowed_sparse_cpu_gate', {})
        if storage_allowed.get('sparse_regimes_chosen') != ['peaked_low_support']:
            errors.append('score-storage-allowed sparse CPU gate should only choose peaked_low_support')
        strict = policies.get('strict_materialization_free_deployable_gate', {})
        if strict.get('aggregate_speedup_vs_dense') != 1.0:
            errors.append('strict gate should fall back to dense everywhere, aggregate speedup 1.0')
        streaming_neg = policies.get('streaming_no_storage_negative_control', {})
        if float(streaming_neg.get('aggregate_speedup_vs_dense', 999.0)) >= 1.0:
            errors.append('streaming no-storage negative control unexpectedly faster than dense')
        # Per-decision checks: strict sparse fallback should cite qk schedule tax or speed failure for peaked.
        strict_decisions = [d for d in decisions if d.get('policy') == 'strict_materialization_free_deployable_gate']
        if len(strict_decisions) != 4:
            errors.append('strict gate missing regime decisions')
        for d in strict_decisions:
            if d.get('chosen_method') != 'dense_online_one_pass':
                errors.append('strict gate did not fall back to dense for ' + d.get('regime', '?'))
            if d.get('regime') == 'peaked_low_support' and 'qk_recompute_schedule_tax' not in d.get('vetoes', []):
                errors.append('peaked strict fallback should expose qk recompute schedule tax')
            if d.get('regime') == 'value_tail_outlier' and 'quality_bar_failure' not in d.get('vetoes', []):
                errors.append('value-tail strict fallback should expose quality failure')
    if man:
        if man.get('artifact_sha256') != sha256_file(ROOT / current[0]):
            errors.append('run manifest artifact hash mismatch')
        if man.get('input_artifact_sha256') != sha256_file(ROOT / 'artifacts/probe-results/REV0058_FUSED_STREAMING_SCHEDULE_NATIVE.json'):
            errors.append('run manifest input hash mismatch')
        if man.get('source_sha256') != sha256_file(ROOT / current[2]):
            errors.append('run manifest source hash mismatch')
        if man.get('gpu_kernel_claim') is not False or man.get('promotion_allowed') is not False:
            errors.append('run manifest overclaims promotion/GPU')

    for rel in [
        'experiments/fused_dispatch_gate/fused_dispatch_gate.py',
        'tools/fused_dispatch_gate_audit.py',
    ]:
        if not (ROOT / rel).exists():
            errors.append('missing source/refactor file: ' + rel)

    report = {
        'project': 'CloudtainerML',
        'revision': REV,
        'report': 'fused_dispatch_gate_audit',
        'status': 'pass' if not errors else 'fail',
        'promotion_allowed': False,
        'current_artifacts': current,
        'strict_materialization_free_sparse_promoted': summary.get('strict_materialization_free_sparse_promoted'),
        'score_storage_allowed_sparse_regimes': summary.get('score_storage_allowed_sparse_regimes'),
        'streaming_no_storage_negative_control_aggregate_speedup_vs_dense': summary.get('streaming_no_storage_negative_control_aggregate_speedup_vs_dense'),
        'speed_only_near_dense_false_wins': summary.get('speed_only_materialized_negative_control_near_dense_false_wins'),
        'remaining_blockers': summary.get('remaining_blockers', []),
        'errors': errors,
        'warnings': warnings,
        'interpretation': 'rev0059 adds a dispatch/claim gate over the measured rev0058 schedule rows. It blocks fused sparse promotion when score storage is forbidden, exposes near-dense materialized false wins, and forces dense fallback on the value-tail quality failure.',
    }
    (OUT / f'{REVUP}_FUSED_DISPATCH_GATE_AUDIT.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    md = [
        f'# Fused dispatch gate audit — {REV}', '',
        f'**Status: {report["status"]}**', '',
        f'- strict materialization-free sparse promoted: `{report["strict_materialization_free_sparse_promoted"]}`',
        f'- score-storage-allowed sparse regimes: `{report["score_storage_allowed_sparse_regimes"]}`',
        f'- streaming no-storage negative-control speedup: `{report["streaming_no_storage_negative_control_aggregate_speedup_vs_dense"]}`',
        f'- near-dense false wins exposed: `{report["speed_only_near_dense_false_wins"]}`',
        '', '## Interpretation', '', report['interpretation'],
    ]
    if warnings:
        md += ['', '## Warnings', *[f'- {w}' for w in warnings]]
    if errors:
        md += ['', '## Errors', *[f'- {e}' for e in errors]]
    (OUT / f'{REVUP}_FUSED_DISPATCH_GATE_AUDIT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'errors': len(errors), 'warnings': len(warnings)}, indent=2))
    return 0 if not errors else 1

if __name__ == '__main__':
    raise SystemExit(main())
