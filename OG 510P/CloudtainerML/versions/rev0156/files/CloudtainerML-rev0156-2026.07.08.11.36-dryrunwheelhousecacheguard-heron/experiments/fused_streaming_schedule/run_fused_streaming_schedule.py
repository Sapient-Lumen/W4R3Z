#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8')) if (ROOT / 'CUBE-META.json').exists() else {'revision': 'rev0058'}
REV = META.get('revision', 'rev0058')
REVUP = REV.upper()
SRC = Path(__file__).with_name('fused_streaming_schedule.cpp')
BIN = Path(__file__).with_name('fused_streaming_schedule.bin')
NATIVE_OUT = ROOT / 'artifacts' / 'probe-results' / f'{REVUP}_FUSED_STREAMING_SCHEDULE_NATIVE.json'
OUT = ROOT / 'artifacts' / 'probe-results' / f'{REVUP}_FUSED_STREAMING_SCHEDULE_TAX.json'
MAN = ROOT / 'artifacts' / 'run-manifests' / f'{REVUP}_FUSED_STREAMING_SCHEDULE_TAX_RUN_MANIFEST.json'
GENERATED_AT = '2026-06-18T07:12:00-04:00'


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)


def cmd_available(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def gpu_probe() -> dict[str, Any]:
    probe: dict[str, Any] = {
        'nvcc_available': cmd_available('nvcc'),
        'nvidia_smi_available': cmd_available('nvidia-smi'),
        'cuda_visible_devices_env_set': 'CUDA_VISIBLE_DEVICES' in __import__('os').environ,
        'gpu_kernel_measured': False,
        'reason_gpu_not_measured': 'No CUDA/fused attention kernel is compiled or run by this rev0058 probe; availability flags are diagnostic only.',
    }
    if probe['nvidia_smi_available']:
        try:
            smi = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
            probe['nvidia_smi_stdout'] = smi.stdout.strip()[:500]
            probe['nvidia_smi_returncode'] = smi.returncode
        except Exception as exc:  # pragma: no cover
            probe['nvidia_smi_error'] = repr(exc)
    return probe


def rows_by(native: dict[str, Any], method: str | None = None, regime: str | None = None) -> list[dict[str, Any]]:
    rows = native.get('rows', [])
    if method is not None:
        rows = [r for r in rows if r.get('method') == method]
    if regime is not None:
        rows = [r for r in rows if r.get('regime') == regime]
    return rows


def make_summary(native: dict[str, Any]) -> dict[str, Any]:
    mat = rows_by(native, 'materialized_score_histogram_mass_0p95')
    stream = rows_by(native, 'streaming_recompute_histogram_mass_0p95')
    dense2 = rows_by(native, 'streaming_two_pass_dense_reference')
    regimes = sorted({r['regime'] for r in mat})
    mat_speed = {r['regime']: float(r['speedup_vs_dense_online']) for r in mat}
    stream_speed = {r['regime']: float(r['speedup_vs_dense_online']) for r in stream}
    mat_quality = {r['regime']: float(r['quality_bar_rate']) for r in mat}
    stream_quality = {r['regime']: float(r['quality_bar_rate']) for r in stream}
    stream_qk = {r['regime']: float(r['qk_dot_fraction_vs_dense_online']) for r in stream}
    mat_score_writes = {r['regime']: float(r['mean_score_memory_writes']) for r in mat}
    stream_score_writes = {r['regime']: float(r['mean_score_memory_writes']) for r in stream}
    gaps = {reg: mat_speed[reg] - stream_speed[reg] for reg in regimes}
    value_tail_mat = next((r for r in mat if r['regime'] == 'value_tail_outlier'), {})
    value_tail_stream = next((r for r in stream if r['regime'] == 'value_tail_outlier'), {})
    return {
        'promotion_allowed': False,
        'primary_claim': 'Materialized score-histogram sparse attention is not a fused-kernel claim; materialization-free streaming selection must pay QK recompute/schedule tax in this CPU probe.',
        'regimes': regimes,
        'materialized_histogram_speedup_vs_dense_by_regime': mat_speed,
        'streaming_recompute_histogram_speedup_vs_dense_by_regime': stream_speed,
        'materialized_histogram_quality_by_regime': mat_quality,
        'streaming_recompute_histogram_quality_by_regime': stream_quality,
        'streaming_recompute_qk_fraction_by_regime': stream_qk,
        'materialized_score_writes_by_regime': mat_score_writes,
        'streaming_score_writes_by_regime': stream_score_writes,
        'max_materialized_minus_streaming_speedup_gap': max(gaps.values()) if gaps else None,
        'mean_materialized_minus_streaming_speedup_gap': sum(gaps.values()) / max(1, len(gaps)),
        'streaming_recompute_schedule_tax_exposed': any(g > 0.05 for g in gaps.values()) and all(v >= 3.0 for v in stream_qk.values()),
        'materialized_path_requires_global_score_storage': all(v >= native.get('n_ctx', 0) for v in mat_score_writes.values()),
        'streaming_path_avoids_global_score_storage': all(v == 0.0 for v in stream_score_writes.values()),
        'value_tail_mass_only_quality_materialized': value_tail_mat.get('quality_bar_rate'),
        'value_tail_mass_only_quality_streaming': value_tail_stream.get('quality_bar_rate'),
        'mass_only_value_tail_failure_still_visible': bool(float(value_tail_mat.get('quality_bar_rate', 1.0)) < 1.0 or float(value_tail_stream.get('quality_bar_rate', 1.0)) < 1.0),
        'two_pass_dense_reference_rows': len(dense2),
        'gpu_kernel_claim': False,
        'gpu_fused_kernel_measured': False,
        'public_pretrained_trace_loaded': False,
        'remaining_blockers': [
            'gpu_fused_attention_kernel_timing_missing',
            'public_pretrained_trace_bundle_missing',
            'cuda_or_target_kernel_path_not_measured',
            'materialization_free_sparse_schedule_requires_qk_recompute_in_this_probe',
            'value_tail_mass_only_quality_failure_remains_for_mass_selector',
        ],
    }


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    MAN.parent.mkdir(parents=True, exist_ok=True)
    compile_cmd = ['g++', '-std=c++17', '-O3', '-march=native', str(SRC), '-o', str(BIN)]
    cc = run(compile_cmd)
    native_proc = run([str(BIN)])
    native = json.loads(native_proc.stdout)
    native['revision'] = REV
    native['generated_at'] = GENERATED_AT
    native['measurement_scope'] = 'native CPU fused-schedule proxy: compares one-pass dense online attention, materialized score-histogram sparse selection, and materialization-free streaming recompute selection; not GPU timing and not a fused CUDA kernel'
    native['gpu_environment_probe'] = gpu_probe()
    NATIVE_OUT.write_text(json.dumps(native, indent=2) + '\n', encoding='utf-8')
    summary = make_summary(native)
    artifact = {
        'project': 'CloudtainerML',
        'revision': REV,
        'artifact': f'{REVUP}_FUSED_STREAMING_SCHEDULE_TAX',
        'probe': 'fused_streaming_schedule',
        'kind': 'native_cpu_fused_schedule_tax_audit',
        'evidence_tier': 'E2p9_native_cpu_kernel_schedule_proxy_not_gpu',
        'generated_at': GENERATED_AT,
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_kernel_claim': False,
        'gpu_fused_kernel_measured': False,
        'trace_source_type': 'deterministic_synthetic_qkv_regimes',
        'measurement_scope': native['measurement_scope'],
        'selection_contract': 'Selectors use only QK scores and score-derived histogram mass. They do not inspect V vectors or dense outputs during selection. This probe deliberately contrasts materialized score storage against materialization-free QK recompute schedules.',
        'cost_contract': 'Dense online is one QK+V streaming pass. Materialized histogram stores all scores once. Streaming histogram avoids score storage but pays multiple QK passes before selected V accumulation. All timings are native CPU row-proxy timings, not GPU/fused-kernel timings.',
        'configuration': {
            'n_ctx': native['n_ctx'],
            'd_head': native['d_head'],
            'd_value': native['d_value'],
            'rows_per_regime': native['rows_per_regime'],
            'repeats': native['repeats'],
            'target_mass': native['target_mass'],
            'compiler_flags': '-std=c++17 -O3 -march=native',
        },
        'native_results': native,
        'summary': summary,
        'run_provenance': {},
        'interpretation': 'rev0058 hardens the GPU/fused-kernel blocker by showing why materialized dense-score sparse selectors cannot be promoted as fused kernels. A no-score-storage streaming version avoids global score writes but pays QK recomputation/schedule tax. The result is an executable bridge toward kernel work, not a GPU speed claim.',
    }
    OUT.write_text(json.dumps(artifact, indent=2) + '\n', encoding='utf-8')
    manifest = {
        'project': 'CloudtainerML',
        'revision': REV,
        'artifact': str(OUT.relative_to(ROOT)),
        'native_artifact': str(NATIVE_OUT.relative_to(ROOT)),
        'generated_at': GENERATED_AT,
        'command': ' '.join(compile_cmd) + ' && ' + str(BIN),
        'python': sys.version,
        'platform': platform.platform(),
        'source': str(SRC.relative_to(ROOT)),
        'runner': str(Path(__file__).relative_to(ROOT)),
        'source_sha256': sha(SRC),
        'runner_sha256': sha(Path(__file__)),
        'artifact_sha256': sha(OUT),
        'native_artifact_sha256': sha(NATIVE_OUT),
        'compile_stdout': cc.stdout,
        'compile_stderr': cc.stderr[-4000:],
        'promotion_allowed': False,
        'gpu_kernel_claim': False,
    }
    artifact['run_provenance'] = manifest
    OUT.write_text(json.dumps(artifact, indent=2) + '\n', encoding='utf-8')
    manifest['artifact_sha256'] = sha(OUT)
    MAN.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'artifact': str(OUT.relative_to(ROOT)), 'native': str(NATIVE_OUT.relative_to(ROOT)), 'summary': summary}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
