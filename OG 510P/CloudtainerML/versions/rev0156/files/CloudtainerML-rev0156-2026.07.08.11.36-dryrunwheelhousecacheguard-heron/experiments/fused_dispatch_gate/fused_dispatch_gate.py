#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REV = 'rev0059'
REVUP = 'REV0059'
STAMP = '2026-06-18T07:49:00-04:00'
INPUT_REL = 'artifacts/probe-results/REV0058_FUSED_STREAMING_SCHEDULE_NATIVE.json'
OUT_REL = f'artifacts/probe-results/{REVUP}_FUSED_DISPATCH_GATE.json'
MAN_REL = f'artifacts/run-manifests/{REVUP}_FUSED_DISPATCH_GATE_RUN_MANIFEST.json'

MIN_SPEEDUP = 1.05
MAX_SPARSE_SELECTED_FRACTION = 0.50
MAX_FUSED_QK_FRACTION = 1.25
QUALITY_MIN = 1.0

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()

def load_json(rel: str):
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))

def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else 0.0

def by_method_regime(rows):
    return {(r['method'], r['regime']): r for r in rows}

def dense_for(regime, m):
    return m[('dense_online_one_pass', regime)]

def method_for(method, regime, m):
    return m[(method, regime)]

def vetoes_for(row, *, require_no_score_storage: bool, require_sparse_fraction: bool, require_speedup: bool, require_quality: bool, require_low_qk_fraction: bool):
    vetoes = []
    if require_quality and float(row.get('quality_bar_rate', 0.0)) < QUALITY_MIN:
        vetoes.append('quality_bar_failure')
    if require_speedup and float(row.get('speedup_vs_dense_online', 0.0)) < MIN_SPEEDUP:
        vetoes.append('no_measured_speedup')
    if require_sparse_fraction and float(row.get('selected_fraction', 1.0)) > MAX_SPARSE_SELECTED_FRACTION:
        vetoes.append('near_dense_value_reads')
    if require_no_score_storage and float(row.get('mean_score_memory_writes', 0.0)) > 0.0:
        vetoes.append('global_score_storage_required')
    if require_no_score_storage and row.get('materializes_scores') is True:
        vetoes.append('materializes_dense_scores')
    if require_low_qk_fraction and float(row.get('qk_dot_fraction_vs_dense_online', 999.0)) > MAX_FUSED_QK_FRACTION:
        vetoes.append('qk_recompute_schedule_tax')
    if row.get('uses_values_for_selection') is True:
        vetoes.append('uses_values_for_selection')
    if row.get('uses_dense_output_for_selection') is True:
        vetoes.append('uses_dense_output_for_selection')
    return vetoes

def choose(policy: str, regime: str, m):
    dense = dense_for(regime, m)
    mat = method_for('materialized_score_histogram_mass_0p95', regime, m)
    stream = method_for('streaming_recompute_histogram_mass_0p95', regime, m)
    candidates = []
    if policy == 'speed_only_materialized_negative_control':
        # Deliberately unsafe: ignores score storage and sparse fraction.  Used to expose false wins.
        candidates = [('materialized_score_histogram_mass_0p95', mat, vetoes_for(mat, require_no_score_storage=False, require_sparse_fraction=False, require_speedup=True, require_quality=True, require_low_qk_fraction=False))]
    elif policy == 'score_storage_allowed_sparse_cpu_gate':
        # Allows materialized dense scores but refuses near-dense selections and quality failures.
        candidates = [('materialized_score_histogram_mass_0p95', mat, vetoes_for(mat, require_no_score_storage=False, require_sparse_fraction=True, require_speedup=True, require_quality=True, require_low_qk_fraction=False))]
    elif policy == 'streaming_no_storage_negative_control':
        # Allows no-score-storage streaming even when it is slower; exposes that value-read savings alone are insufficient.
        candidates = [('streaming_recompute_histogram_mass_0p95', stream, vetoes_for(stream, require_no_score_storage=True, require_sparse_fraction=True, require_speedup=False, require_quality=True, require_low_qk_fraction=False))]
    elif policy == 'strict_materialization_free_deployable_gate':
        # The strongest promotion gate: no score storage, quality pass, real speedup, non-near-dense values, and no QK schedule blowup.
        candidates = [('streaming_recompute_histogram_mass_0p95', stream, vetoes_for(stream, require_no_score_storage=True, require_sparse_fraction=True, require_speedup=True, require_quality=True, require_low_qk_fraction=True))]
    else:
        raise ValueError('unknown policy ' + policy)
    accepted = [(name, row) for name, row, veto in candidates if not veto]
    if accepted:
        # If multiple policy candidates are ever added, prefer lowest ns among accepted.
        name, row = min(accepted, key=lambda x: float(x[1].get('ns_per_row', 1e300)))
        fallback = False
        veto = []
    else:
        name, row = 'dense_online_one_pass', dense
        fallback = True
        veto = candidates[0][2] if candidates else ['no_candidate']
    return {
        'policy': policy,
        'regime': regime,
        'chosen_method': name,
        'fallback_to_dense': fallback,
        'vetoes': veto,
        'ns_per_row': float(row['ns_per_row']),
        'speedup_vs_dense_online': float(row['speedup_vs_dense_online']),
        'quality_bar_rate': float(row['quality_bar_rate']),
        'selected_fraction': float(row['selected_fraction']),
        'mean_qk_dot_products': float(row['mean_qk_dot_products']),
        'qk_dot_fraction_vs_dense_online': float(row['qk_dot_fraction_vs_dense_online']),
        'mean_value_reads': float(row['mean_value_reads']),
        'mean_score_memory_writes': float(row['mean_score_memory_writes']),
        'mean_score_memory_reads': float(row['mean_score_memory_reads']),
        'materializes_scores': bool(row.get('materializes_scores', False)),
        'materialization_free_streaming': bool(row.get('materialization_free_streaming', False)),
    }

def summarize_policy(policy: str, decisions, m):
    relevant = [d for d in decisions if d['policy'] == policy]
    regimes = [d['regime'] for d in relevant]
    dense_ns = [float(dense_for(r, m)['ns_per_row']) for r in regimes]
    chosen_ns = [d['ns_per_row'] for d in relevant]
    chosen_sparse = [d for d in relevant if d['chosen_method'] != 'dense_online_one_pass']
    near_dense_chosen = [d['regime'] for d in chosen_sparse if d['selected_fraction'] > MAX_SPARSE_SELECTED_FRACTION]
    materialized_chosen = [d['regime'] for d in chosen_sparse if d['materializes_scores']]
    streaming_chosen = [d['regime'] for d in chosen_sparse if d['materialization_free_streaming']]
    return {
        'policy': policy,
        'aggregate_dense_ns_per_row': mean(dense_ns),
        'aggregate_chosen_ns_per_row': mean(chosen_ns),
        'aggregate_speedup_vs_dense': mean(dense_ns) / max(1e-12, mean(chosen_ns)),
        'sparse_regimes_chosen': [d['regime'] for d in chosen_sparse],
        'dense_fallback_regimes': [d['regime'] for d in relevant if d['chosen_method'] == 'dense_online_one_pass'],
        'materialized_score_regimes_chosen': materialized_chosen,
        'streaming_no_score_storage_regimes_chosen': streaming_chosen,
        'near_dense_sparse_regimes_chosen': near_dense_chosen,
        'mean_selected_fraction': mean(d['selected_fraction'] for d in relevant),
        'mean_qk_fraction_vs_dense': mean(d['qk_dot_fraction_vs_dense_online'] for d in relevant),
        'mean_score_writes': mean(d['mean_score_memory_writes'] for d in relevant),
        'mean_value_reads': mean(d['mean_value_reads'] for d in relevant),
        'min_quality_bar_rate': min((d['quality_bar_rate'] for d in relevant), default=0.0),
    }

def main() -> int:
    inp = load_json(INPUT_REL)
    rows = inp['rows']
    m = by_method_regime(rows)
    regimes = sorted({r['regime'] for r in rows})
    policies = [
        'speed_only_materialized_negative_control',
        'score_storage_allowed_sparse_cpu_gate',
        'streaming_no_storage_negative_control',
        'strict_materialization_free_deployable_gate',
    ]
    decisions = []
    for policy in policies:
        for regime in regimes:
            decisions.append(choose(policy, regime, m))
    policy_summaries = {p: summarize_policy(p, decisions, m) for p in policies}
    speed_only_near_dense = policy_summaries['speed_only_materialized_negative_control']['near_dense_sparse_regimes_chosen']
    strict = policy_summaries['strict_materialization_free_deployable_gate']
    storage_allowed = policy_summaries['score_storage_allowed_sparse_cpu_gate']
    streaming_negative = policy_summaries['streaming_no_storage_negative_control']
    tail_safe_dense = [d for d in decisions if d['regime'] == 'value_tail_outlier' and d['policy'] in ['score_storage_allowed_sparse_cpu_gate', 'strict_materialization_free_deployable_gate'] and d['chosen_method'] == 'dense_online_one_pass']
    summary = {
        'promotion_allowed': False,
        'primary_claim': 'A deployable fused sparse-attention path must pass quality, speed, score-storage, selected-fraction, and QK-schedule gates; current measured CPU schedule rows do not promote any materialization-free sparse schedule.',
        'policies_evaluated': policies,
        'strict_materialization_free_sparse_promoted': False,
        'strict_materialization_free_sparse_regimes': strict['sparse_regimes_chosen'],
        'strict_materialization_free_aggregate_speedup_vs_dense': strict['aggregate_speedup_vs_dense'],
        'strict_materialization_free_dense_fallback_regimes': strict['dense_fallback_regimes'],
        'score_storage_allowed_sparse_regimes': storage_allowed['sparse_regimes_chosen'],
        'score_storage_allowed_aggregate_speedup_vs_dense': storage_allowed['aggregate_speedup_vs_dense'],
        'score_storage_allowed_not_fused_claim': True,
        'streaming_no_storage_negative_control_sparse_regimes': streaming_negative['sparse_regimes_chosen'],
        'streaming_no_storage_negative_control_aggregate_speedup_vs_dense': streaming_negative['aggregate_speedup_vs_dense'],
        'speed_only_materialized_negative_control_near_dense_false_wins': speed_only_near_dense,
        'speed_only_materialized_negative_control_materialized_regimes': policy_summaries['speed_only_materialized_negative_control']['materialized_score_regimes_chosen'],
        'value_tail_dense_fallback_under_safe_gates': len(tail_safe_dense) == 2,
        'value_tail_mass_only_veto': True,
        'score_storage_forbidden_no_sparse_speed_win': len(strict['sparse_regimes_chosen']) == 0,
        'near_dense_value_read_veto_active': bool(speed_only_near_dense),
        'materialized_path_requires_global_score_storage': True,
        'streaming_path_avoids_global_score_storage_but_pays_qk_schedule_tax': True,
        'remaining_blockers': [
            'gpu_fused_attention_kernel_timing_missing',
            'public_pretrained_trace_bundle_missing',
            'materialization_free_sparse_schedule_has_no_measured_speed_win_in_current_cpu_proxy',
            'materialized_sparse_cpu_path_requires_global_score_storage',
            'value_tail_mass_only_quality_failure_remains_for_mass_selector',
            'learned_or_public_trace_dispatch_gate_missing',
        ],
    }
    artifact = {
        'project': 'CloudtainerML',
        'revision': REV,
        'artifact': f'{REVUP}_FUSED_DISPATCH_GATE',
        'probe': 'fused_dispatch_gate',
        'kind': 'dispatch_gate_materialization_audit',
        'evidence_tier': 'E2p9_native_cpu_schedule_dispatch_analysis_not_gpu',
        'generated_at': STAMP,
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_kernel_claim': False,
        'gpu_fused_kernel_measured': False,
        'input_artifact': INPUT_REL,
        'input_artifact_sha256': sha256_file(ROOT / INPUT_REL),
        'trace_source_type': 'deterministic_synthetic_qkv_regimes_from_rev0058_native_cpu_schedule_proxy',
        'measurement_scope': 'dispatch/claim gate over measured native CPU row-schedule results; not GPU timing, not a fused CUDA/Triton kernel, and not public/pretrained model traces',
        'selection_contract': 'Dispatch policies may inspect measured schedule metadata from the current probe. They do not use V vectors or dense outputs to select sparse rows at runtime; value-tail quality failure is treated as a veto in this evidence gate.',
        'cost_contract': 'A sparse win must state whether it materializes dense scores, writes/reads score memory, pays QK recompute passes, and actually selects a non-near-dense value set. Saving value reads alone is not promotion evidence.',
        'configuration': {
            'min_speedup_vs_dense': MIN_SPEEDUP,
            'max_sparse_selected_fraction': MAX_SPARSE_SELECTED_FRACTION,
            'max_fused_qk_fraction_vs_dense': MAX_FUSED_QK_FRACTION,
            'quality_min_rate': QUALITY_MIN,
        },
        'policy_summaries': policy_summaries,
        'dispatch_decisions': decisions,
        'summary': summary,
    }
    out = ROOT / OUT_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(artifact, indent=2) + '\n', encoding='utf-8')
    man = {
        'project': 'CloudtainerML',
        'revision': REV,
        'artifact': OUT_REL,
        'generated_at': STAMP,
        'command': 'python experiments/fused_dispatch_gate/fused_dispatch_gate.py',
        'source': 'experiments/fused_dispatch_gate/fused_dispatch_gate.py',
        'source_sha256': sha256_file(Path(__file__).resolve()),
        'input_artifact': INPUT_REL,
        'input_artifact_sha256': sha256_file(ROOT / INPUT_REL),
        'artifact_sha256': sha256_file(out),
        'gpu_kernel_claim': False,
        'public_pretrained_trace_loaded': False,
        'promotion_allowed': False,
    }
    man_path = ROOT / MAN_REL
    man_path.parent.mkdir(parents=True, exist_ok=True)
    man_path.write_text(json.dumps(man, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'wrote': OUT_REL, 'status': 'promotion_blocked', 'strict_sparse_regimes': summary['strict_materialization_free_sparse_regimes']}, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
