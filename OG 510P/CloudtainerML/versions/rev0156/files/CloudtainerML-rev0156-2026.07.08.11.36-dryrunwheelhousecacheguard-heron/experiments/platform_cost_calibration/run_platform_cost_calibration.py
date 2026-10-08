#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8')) if (ROOT / 'CUBE-META.json').exists() else {'revision': 'rev0057'}
REV = META.get('revision', 'rev0057')
REVUP = REV.upper()
SRC = Path(__file__).with_name('platform_cost_calibration.cpp')
BIN = Path(__file__).with_name('platform_cost_calibration.bin')
NATIVE_OUT = ROOT / 'artifacts' / 'probe-results' / f'{REVUP}_PLATFORM_PRIMITIVE_COST_NATIVE.json'
OUT = ROOT / 'artifacts' / 'probe-results' / f'{REVUP}_PLATFORM_COST_CALIBRATED_ROUTER.json'
MAN = ROOT / 'artifacts' / 'run-manifests' / f'{REVUP}_PLATFORM_COST_CALIBRATED_ROUTER_RUN_MANIFEST.json'
PREV = ROOT / 'artifacts' / 'probe-results' / 'REV0056_ROUTER_COST_FRONTIER.json'

GENERATED_AT = '2026-06-18T06:33:00-04:00'


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


def mean_row(rows: list[dict[str, Any]], primitive: str, d: int) -> dict[str, Any]:
    matches = [r for r in rows if r.get('primitive') == primitive and int(r.get('d', -1)) == d]
    if not matches:
        raise KeyError((primitive, d))
    return matches[0]


def frontier_row(prev: dict[str, Any], selector: str, method: str, qk_weight: float = 1.0) -> dict[str, Any]:
    matches = [r for r in prev.get('rows', []) if r.get('selector') == selector and r.get('method') == method and abs(float(r.get('qk_weight', -999.0)) - qk_weight) < 1e-12]
    if not matches:
        raise KeyError((selector, method, qk_weight))
    return matches[0]


def weighted_cost(frontier: dict[str, Any], qk_weight: float) -> float:
    return float(qk_weight * float(frontier['mean_qk_dot_products']) + float(frontier['mean_selected_values']))


def compare_selector(prev: dict[str, Any], selector: str, qk_weight: float) -> dict[str, Any]:
    router = frontier_row(prev, selector, 'cost_calibrated_adaptive_bound_gate_router')
    hist = frontier_row(prev, selector, 'dense_score_mass_histogram_0p95_sparse')
    dense = frontier_row(prev, selector, 'dense_full_attention')
    r_cost = weighted_cost(router, qk_weight)
    h_cost = weighted_cost(hist, qk_weight)
    d_cost = weighted_cost(dense, qk_weight)
    return {
        'selector': selector,
        'measured_qk_weight': qk_weight,
        'router_cost_measured_units': r_cost,
        'histogram_cost_measured_units': h_cost,
        'dense_cost_measured_units': d_cost,
        'router_beats_histogram': bool(r_cost < h_cost and float(router['quality_bar_rate']) >= float(prev['summary']['quality_floor'])),
        'histogram_beats_router': bool(h_cost <= r_cost and float(hist['quality_bar_rate']) >= float(prev['summary']['quality_floor'])),
        'router_speedup_vs_dense_measured_units': float(d_cost / max(1e-12, r_cost)),
        'histogram_speedup_vs_dense_measured_units': float(d_cost / max(1e-12, h_cost)),
        'router_quality_bar_rate': router['quality_bar_rate'],
        'histogram_quality_bar_rate': hist['quality_bar_rate'],
        'router_mean_qk_dot_products': router['mean_qk_dot_products'],
        'histogram_mean_qk_dot_products': hist['mean_qk_dot_products'],
        'router_mean_selected_values': router['mean_selected_values'],
        'histogram_mean_selected_values': hist['mean_selected_values'],
    }


def make_artifact(native: dict[str, Any], prev: dict[str, Any]) -> dict[str, Any]:
    rows = native['rows']
    qk8 = mean_row(rows, 'qk_dot_sequential', 8)
    vseq8 = mean_row(rows, 'value_accumulate_sequential', 8)
    vgather8 = mean_row(rows, 'value_accumulate_sparse_gather', 8)
    block8 = mean_row(rows, 'block_centroid_bound_dot', 8)
    qk64 = mean_row(rows, 'qk_dot_sequential', 64)
    vseq64 = mean_row(rows, 'value_accumulate_sequential', 64)
    vgather64 = mean_row(rows, 'value_accumulate_sparse_gather', 64)

    qk_weight_seq8 = float(qk8['ns_per_vector']) / max(1e-12, float(vseq8['ns_per_vector']))
    qk_weight_gather8 = float(qk8['ns_per_vector']) / max(1e-12, float(vgather8['ns_per_vector']))
    qk_weight_seq64 = float(qk64['ns_per_vector']) / max(1e-12, float(vseq64['ns_per_vector']))
    qk_weight_gather64 = float(qk64['ns_per_vector']) / max(1e-12, float(vgather64['ns_per_vector']))
    block_vs_qk8 = float(block8['ns_per_vector']) / max(1e-12, float(qk8['ns_per_vector']))

    break_even_all = prev['summary'].get('first_qk_weight_router_beats_histogram_all')
    break_even_high = prev['summary'].get('first_qk_weight_router_beats_histogram_high_support')
    continuous_break_even_all = prev['summary'].get('continuous_break_even_qk_weight_all_using_equal_unit_config')

    comparisons_seq8 = [compare_selector(prev, sel, qk_weight_seq8) for sel in ['all', 'heldout_odd', 'low_support', 'middle_support', 'high_support']]
    comparisons_gather8 = [compare_selector(prev, sel, qk_weight_gather8) for sel in ['all', 'heldout_odd', 'low_support', 'middle_support', 'high_support']]
    all_seq8 = next(c for c in comparisons_seq8 if c['selector'] == 'all')
    high_seq8 = next(c for c in comparisons_seq8 if c['selector'] == 'high_support')

    qk_weights = {
        'router_dimension_d8_vs_sequential_value_accum': qk_weight_seq8,
        'router_dimension_d8_vs_sparse_gather_value_accum': qk_weight_gather8,
        'wide_d64_vs_sequential_value_accum': qk_weight_seq64,
        'wide_d64_vs_sparse_gather_value_accum': qk_weight_gather64,
    }
    measured_values = list(qk_weights.values())
    max_measured = max(measured_values)
    min_measured = min(measured_values)
    break_even_gap_ratio_all = float(break_even_all / max(1e-12, qk_weight_seq8)) if break_even_all else None
    promotion_allowed = False
    summary = {
        'promotion_allowed': promotion_allowed,
        'primary_claim': 'Measured native CPU primitive ratios keep the adaptive router below the rev0056 break-even; the proxy QK-weight router win is not supported on this CPU path.',
        'measured_qk_weight_router_d8_vs_sequential_value_accum': qk_weight_seq8,
        'measured_qk_weight_router_d8_vs_sparse_gather_value_accum': qk_weight_gather8,
        'measured_qk_weight_range': [min_measured, max_measured],
        'block_centroid_bound_dot_cost_vs_qk_dot_d8': block_vs_qk8,
        'rev0056_first_qk_weight_router_beats_histogram_all': break_even_all,
        'rev0056_first_qk_weight_router_beats_histogram_high_support': break_even_high,
        'rev0056_continuous_break_even_all_using_equal_unit_config': continuous_break_even_all,
        'measured_router_beats_histogram_all_seq8': all_seq8['router_beats_histogram'],
        'measured_router_beats_histogram_high_support_seq8': high_seq8['router_beats_histogram'],
        'measured_platform_cost_model_claim_blocked': True,
        'measured_qk_weight_below_all_row_break_even': bool(break_even_all is not None and qk_weight_seq8 < float(break_even_all)),
        'break_even_gap_ratio_all_vs_measured_seq8': break_even_gap_ratio_all,
        'measured_native_cpu_scope_only': True,
        'gpu_kernel_claim': False,
        'public_pretrained_trace_loaded': False,
        'remaining_blockers': [
            'public_pretrained_trace_bundle_missing',
            'gpu_fused_attention_kernel_timing_missing',
            'adaptive_router_kernel_path_missing',
            'platform_cost_calibration_is_cpu_primitive_not_end_to_end_gpu',
            'router_validated_only_on_tiny_learned_trace',
        ],
    }
    return {
        'project': 'CloudtainerML',
        'revision': REV,
        'artifact': f'{REVUP}_PLATFORM_COST_CALIBRATED_ROUTER',
        'probe': 'platform_cost_calibration',
        'kind': 'native_cpu_primitive_cost_calibrated_router_veto',
        'evidence_tier': 'E2p85_native_cpu_primitive_cost_calibration_for_router_claims',
        'generated_at': GENERATED_AT,
        'promotion_allowed': promotion_allowed,
        'public_pretrained_trace_loaded': False,
        'gpu_kernel_claim': False,
        'trace_source_type': prev.get('trace_source_type', 'tiny_trained_transformer_qkv_trace'),
        'measurement_scope': 'native CPU primitive timing for QK dot/value accumulation/block-bound metadata; not a fused attention kernel, GPU timing, or public/pretrained trace result',
        'selection_contract': 'no new selection algorithm is promoted; rev0057 recalculates rev0056 router-vs-histogram costs using measured primitive ratios and keeps oracle/public/GPU claim flags false',
        'cost_contract': 'measured qk_weight is ns_per_qk_vector divided by ns_per_value_vector on this CPU primitive path; row router promotion is blocked unless measured end-to-end target-platform costs beat the histogram baseline with quality preserved',
        'configuration': {
            'source_revision_compared': 'rev0056',
            'router_seq': 48,
            'router_d_head': 8,
            'native_rows': qk8['rows'],
            'native_repeats': qk8['repeats'],
            'compiler_flags': '-std=c++17 -O3 -march=native',
        },
        'native_primitive_measurements': native,
        'measured_qk_weight_models': qk_weights,
        'rev0056_cost_frontier_summary': prev.get('summary', {}),
        'measured_cost_comparisons_seq_value': comparisons_seq8,
        'measured_cost_comparisons_sparse_gather_value': comparisons_gather8,
        'summary': summary,
        'run_provenance': {},
        'interpretation': 'rev0057 closes the measured-platform-cost-ratio blocker for one narrow CPU primitive path. The result strengthens the veto from rev0056: the adaptive router needed a very high proxy QK/value weight to beat histogram, but measured CPU primitive ratios are far below that break-even. This does not settle GPU/fused kernels, but it prevents treating the proxy frontier as a systems win.',
    }


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    MAN.parent.mkdir(parents=True, exist_ok=True)
    compile_cmd = ['g++', '-std=c++17', '-O3', '-march=native', str(SRC.relative_to(ROOT)), '-o', str(BIN.relative_to(ROOT))]
    subprocess.run(compile_cmd, check=True, cwd=ROOT)
    subprocess.run([str(BIN.relative_to(ROOT)), str(NATIVE_OUT.relative_to(ROOT))], check=True, cwd=ROOT)
    native = json.loads(NATIVE_OUT.read_text(encoding='utf-8'))
    prev = json.loads(PREV.read_text(encoding='utf-8'))
    artifact = make_artifact(native, prev)
    wrapper = Path(__file__)
    artifact['run_provenance'] = {
        'source_path': str(SRC.relative_to(ROOT)),
        'source_sha256': sha(SRC),
        'wrapper_path': str(wrapper.relative_to(ROOT)),
        'wrapper_sha256': sha(wrapper),
        'previous_frontier_artifact': str(PREV.relative_to(ROOT)),
        'previous_frontier_artifact_sha256': sha(PREV),
        'native_artifact': str(NATIVE_OUT.relative_to(ROOT)),
        'native_artifact_sha256': sha(NATIVE_OUT),
        'compile_command': ' '.join(compile_cmd),
        'run_command': f'{BIN.relative_to(ROOT)} {NATIVE_OUT.relative_to(ROOT)}',
        'python': sys.version.split()[0],
        'platform': platform.platform(),
        'machine': platform.machine(),
        'processor': platform.processor(),
    }
    OUT.write_text(json.dumps(artifact, indent=2) + '\n', encoding='utf-8')
    MAN.write_text(json.dumps({
        'project': 'CloudtainerML',
        'revision': REV,
        'run': 'platform_cost_calibrated_router',
        'artifact': str(OUT.relative_to(ROOT)),
        'artifact_sha256': sha(OUT),
        'native_artifact': str(NATIVE_OUT.relative_to(ROOT)),
        'native_artifact_sha256': sha(NATIVE_OUT),
        'source': str(SRC.relative_to(ROOT)),
        'source_sha256': sha(SRC),
        'wrapper': str(wrapper.relative_to(ROOT)),
        'wrapper_sha256': sha(wrapper),
        'previous_frontier_artifact': str(PREV.relative_to(ROOT)),
        'previous_frontier_artifact_sha256': sha(PREV),
        'compile_command': ' '.join(compile_cmd),
        'measurement_scope': artifact['measurement_scope'],
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_kernel_claim': False,
    }, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({
        'status': 'ok',
        'artifact': str(OUT.relative_to(ROOT)),
        'native_artifact': str(NATIVE_OUT.relative_to(ROOT)),
        'measured_qk_weight_d8_seq': artifact['summary']['measured_qk_weight_router_d8_vs_sequential_value_accum'],
        'break_even_all': artifact['summary']['rev0056_first_qk_weight_router_beats_histogram_all'],
        'router_beats_histogram_all': artifact['summary']['measured_router_beats_histogram_all_seq8'],
    }, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
