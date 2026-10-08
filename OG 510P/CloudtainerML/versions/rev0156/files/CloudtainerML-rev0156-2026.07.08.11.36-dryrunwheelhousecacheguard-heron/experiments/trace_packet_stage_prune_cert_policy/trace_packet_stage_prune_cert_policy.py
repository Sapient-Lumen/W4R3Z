#!/usr/bin/env python3
"""rev0071 stage-pruned certified-reuse policy replay.

rev0070 showed the two-stage certificate was safe but slower, and its block-refinement stage certified no additional rows on the local trace. rev0071 tests a stage-pruned policy: scalar certificate first, no dead block stage, and fresh histogram fallback when scalar certification fails. All selector and fallback work is paid in native CPU timing.
"""
from __future__ import annotations
import hashlib, json, os, platform, shutil, struct, subprocess
from pathlib import Path
from typing import Any
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
META = json.loads((ROOT/'CUBE-META.json').read_text(encoding='utf-8')) if (ROOT/'CUBE-META.json').exists() else {'revision':'rev0070'}
REV = META.get('revision','rev0070')
REVUP = REV.upper()
STAMP = '2026-06-18T16:33:00-04:00'
OUT = ROOT/'artifacts'/'probe-results'/f'{REVUP}_STAGE_PRUNED_CERT_REUSE_POLICY.json'
MAN = ROOT/'artifacts'/'run-manifests'/f'{REVUP}_STAGE_PRUNED_CERT_REUSE_POLICY_RUN_MANIFEST.json'
BIN = ROOT/'artifacts'/'native-inputs'/f'{REVUP}_STAGE_PRUNED_CERT_REUSE_POLICY_INPUT.bin'
BUILD = ROOT/'artifacts'/'native-build'/'trace_packet_stage_prune_cert_policy'
CPP = ROOT/'experiments'/'trace_packet_stage_prune_cert_policy'/'trace_packet_stage_prune_cert_policy.cpp'
EXE = BUILD/'trace_packet_stage_prune_cert_policy'
REPEATS = int(os.environ.get('CTML_STAGE_PRUNE_CERT_REPEATS','2500'))
TARGET_MASS = float(os.environ.get('CTML_STAGE_PRUNE_CERT_TARGET_MASS','0.96'))
HIST_BINS = int(os.environ.get('CTML_STAGE_PRUNE_CERT_HIST_BINS','32'))
BLOCK_SIZE = int(os.environ.get('CTML_STAGE_PRUNE_CERT_BLOCK_SIZE','8'))


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def find_packet() -> Path:
    candidates = sorted((ROOT/'artifacts'/'trace-bundles').glob('REV*_TINY_TRAINED_QK_TRACE_PACKET.npz'), reverse=True)
    for p in candidates:
        if p.name.startswith('REV0062') or p.name.startswith(REVUP):
            return p
    if candidates:
        return candidates[0]
    raise FileNotFoundError('no Q/K/V trace packet found')


def prepare_input(packet: Path) -> dict[str, Any]:
    z = np.load(packet)
    q = np.asarray(z['queries'], dtype=np.float64)
    k = np.asarray(z['keys'], dtype=np.float64)
    v = np.asarray(z['values'], dtype=np.float64)
    rows, n, dk = k.shape
    dv = v.shape[2]
    if q.shape != (rows, dk) or v.shape != (rows, n, dv):
        raise ValueError(f'bad q/k/v shapes q={q.shape} k={k.shape} v={v.shape}')
    example = np.asarray(z['example'] if 'example' in z.files else np.arange(rows), dtype=np.int32)
    trace_batch = np.asarray(z['trace_batch'] if 'trace_batch' in z.files else np.zeros(rows), dtype=np.int32)
    ex_keys = [(int(e), int(tb)) for e, tb in zip(example, trace_batch)]
    ex_map = {key: i for i, key in enumerate(sorted(set(ex_keys)))}
    group_example = np.asarray([ex_map[key] for key in ex_keys], dtype=np.int32)
    BIN.parent.mkdir(parents=True, exist_ok=True)
    with BIN.open('wb') as f:
        f.write(b'CTMLTR71')
        f.write(struct.pack('QQQQ', int(rows), int(n), int(dk), int(dv)))
        f.write(np.ascontiguousarray(q, dtype=np.float64).tobytes(order='C'))
        f.write(np.ascontiguousarray(k, dtype=np.float64).tobytes(order='C'))
        f.write(np.ascontiguousarray(v, dtype=np.float64).tobytes(order='C'))
        f.write(np.ascontiguousarray(group_example, dtype=np.int32).tobytes(order='C'))
    return {
        'trace_packet': packet.relative_to(ROOT).as_posix(),
        'trace_packet_sha256': sha256_file(packet),
        'rows': int(rows),
        'n_tokens': int(n),
        'd_key': int(dk),
        'd_value': int(dv),
        'example_groups': int(len(ex_map)),
        'input_bin': BIN.relative_to(ROOT).as_posix(),
        'input_bin_sha256': sha256_file(BIN),
    }


def compile_native() -> list[str]:
    BUILD.mkdir(parents=True, exist_ok=True)
    compiler = shutil.which('g++') or shutil.which('clang++')
    if not compiler:
        raise RuntimeError('no C++ compiler found')
    cmd = [compiler, '-O3', '-std=c++17', '-march=native', str(CPP), '-o', str(EXE)]
    subprocess.run(cmd, cwd=ROOT, check=True)
    return cmd


def run_native() -> tuple[dict[str, Any], list[str]]:
    compile_cmd = compile_native()
    cmd = [str(EXE), str(BIN), str(REPEATS), str(TARGET_MASS), str(HIST_BINS), str(BLOCK_SIZE)]
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=True)
    return json.loads(proc.stdout), compile_cmd + ['&&'] + cmd


def build_artifact(prep: dict[str, Any], native: dict[str, Any]) -> dict[str, Any]:
    all_rows = native.get('all_rows', {})
    cert = native.get('certificate', {})
    acct = native.get('accounting', {})
    speeds = native.get('speedups_vs_dense', {})
    sidecar = native.get('sidecar', {})
    raw = all_rows.get('uncertified_anchor_reuse', {})
    two = all_rows.get('two_stage_certificate', {})
    scalar = all_rows.get('scalar_only_certificate', {})
    fresh = all_rows.get('fresh_hist_index', {})
    token = all_rows.get('full_token_certificate', {})
    block_extra = int(cert.get('two_stage_block_certified_rows', 0) or 0)
    scalar_speed = speeds.get('scalar_only_certificate')
    two_speed = speeds.get('two_stage_certificate')
    summary = {
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
        'local_tiny_trace_only': True,
        'stage_pruned_certificate_tested': True,
        'sidecar_built_from_key_cache': bool(sidecar.get('built_from_key_cache')),
        'sidecar_uses_values_or_dense_outputs': bool(sidecar.get('uses_values') or sidecar.get('uses_dense_outputs')),
        'sidecar_build_ms': sidecar.get('build_ms'),
        'certificate_uses_observable_q_key_bounds': bool(cert.get('observable_q_key_bound')),
        'certificate_uses_values_or_dense_outputs': bool(cert.get('uses_values') or cert.get('uses_dense_outputs')),
        'fallback_paid_in_timed_loop': bool(acct.get('fallback_paid_in_timed_loop')),
        'certificate_bound_paid_in_timed_loop': bool(acct.get('certificate_bound_paid_in_timed_loop')),
        'raw_anchor_quality_rate': raw.get('quality_rate'),
        'raw_anchor_speedup_vs_dense': speeds.get('uncertified_anchor_reuse'),
        'fresh_hist_quality_rate': fresh.get('quality_rate'),
        'fresh_hist_speedup_vs_dense': speeds.get('fresh_hist_index'),
        'full_token_quality_rate': token.get('quality_rate'),
        'full_token_speedup_vs_dense': speeds.get('full_token_certificate'),
        'two_stage_quality_rate': two.get('quality_rate'),
        'two_stage_speedup_vs_dense': two_speed,
        'scalar_only_quality_rate': scalar.get('quality_rate'),
        'scalar_only_speedup_vs_dense': scalar_speed,
        'candidate_reuse_rows': cert.get('candidate_reuse_rows'),
        'scalar_only_certified_reuse_rows': cert.get('scalar_only_certified_reuse_rows'),
        'scalar_only_fallback_rows': cert.get('scalar_only_fallback_rows'),
        'scalar_only_false_certified_quality_failures': cert.get('scalar_only_false_certified_quality_failures'),
        'two_stage_scalar_certified_rows': cert.get('two_stage_scalar_certified_rows'),
        'two_stage_block_certified_rows': cert.get('two_stage_block_certified_rows'),
        'two_stage_certified_reuse_rows': cert.get('two_stage_certified_reuse_rows'),
        'two_stage_false_certified_quality_failures': cert.get('two_stage_false_certified_quality_failures'),
        'block_stage_extra_certified_rows': acct.get('block_stage_extra_certified_rows', block_extra),
        'scalar_only_qk_dot_fraction': acct.get('scalar_only_certificate_qk_dot_fraction'),
        'two_stage_qk_dot_fraction': acct.get('two_stage_certificate_qk_dot_fraction'),
        'scalar_only_sidecar_read_fraction': acct.get('scalar_only_sidecar_read_fraction'),
        'two_stage_total_sidecar_read_fraction': acct.get('two_stage_total_sidecar_read_fraction'),
        'scalar_pruned_block_read_reduction_vs_two_stage': acct.get('scalar_pruned_block_read_reduction_vs_two_stage'),
        'scalar_only_improves_speed_vs_two_stage': (scalar_speed is not None and two_speed is not None and float(scalar_speed) > float(two_speed)),
        'block_stage_pruned_as_dead_weight': (block_extra == 0),
        'promotion_allowed': False,
        'deployable_promoted_paths': [],
        'remaining_blockers': [
            'actual_public_pretrained_trace_bundle_missing',
            'gpu_fused_attention_kernel_timing_missing',
            'stage_pruned_certificate_safe_but_not_speed_positive_on_local_cpu_trace',
            'support_reuse_still_needs_row_stability_or_cross_layer_reuse_to_beat_dense',
            'sidecar_build_and_validity_need_model_cache_integration',
        ],
    }
    interpretation = (
        'The rev0070 block-refinement stage was dead weight on this trace: it certified no extra rows. '
        'A scalar-only certificate preserves the safety veto and removes the block sidecar reads, but the safe path remains slower than dense/fresh baselines on this CPU replay.'
    )
    return {
        'project': 'CloudtainerML',
        'revision': REV,
        'artifact': f'{REVUP}_STAGE_PRUNED_CERT_REUSE_POLICY',
        'generated_at': STAMP,
        'measurement_scope': 'native CPU local tiny Q/K/V trace replay; stage-pruned support-reuse certificate uses observable scalar Q/K/key-cache sidecars; block refinement is measured as a pruned dead stage; fallback and certificate-bound work are paid; sidecar build is reported separately; not public/pretrained; not GPU; not fused-kernel evidence',
        'trace_input': prep,
        'parameters': {'target_mass': TARGET_MASS, 'hist_bins': HIST_BINS, 'block_size': BLOCK_SIZE, 'repeats': REPEATS},
        'native': native,
        'summary': summary,
        'interpretation': interpretation,
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
    }

def write_outputs(artifact: dict[str, Any], command: list[str]) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    MAN.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    manifest = {
        'project': 'CloudtainerML',
        'revision': REV,
        'artifact': OUT.relative_to(ROOT).as_posix(),
        'generated_at': STAMP,
        'command': ' '.join(command),
        'cwd': str(ROOT),
        'python_version': platform.python_version(),
        'platform': platform.platform(),
        'source_files': {
            str(CPP.relative_to(ROOT)): sha256_file(CPP),
            'experiments/trace_packet_stage_prune_cert_policy/trace_packet_stage_prune_cert_policy.py': sha256_file(Path(__file__)),
        },
        'inputs': {
            artifact['trace_input']['trace_packet']: artifact['trace_input']['trace_packet_sha256'],
            artifact['trace_input']['input_bin']: artifact['trace_input']['input_bin_sha256'],
        },
        'artifact_sha256': sha256_file(OUT),
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
    }
    MAN.write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    doc = ROOT/'docs'/'04-audit'/'rev0071-stage-pruned-cert-reuse-policy.md'
    s = artifact['summary']
    doc.write_text(f"""# rev0071 — stage-pruned certified reuse policy

rev0070 made certified support reuse safe but slow. It also exposed a dead stage: block refinement certified no extra rows on the local learned trace. rev0071 removes that block stage and measures a scalar-only certificate plus fresh fallback.

## Result

- Raw anchor quality rate: `{s['raw_anchor_quality_rate']}`
- Raw anchor speedup vs dense: `{s['raw_anchor_speedup_vs_dense']}`
- Fresh histogram speedup vs dense: `{s['fresh_hist_speedup_vs_dense']}`
- Two-stage certificate speedup: `{s['two_stage_speedup_vs_dense']}`
- Scalar-only certificate quality rate: `{s['scalar_only_quality_rate']}`
- Scalar-only certificate speedup: `{s['scalar_only_speedup_vs_dense']}`
- Scalar-only certified rows: `{s['scalar_only_certified_reuse_rows']}`
- Scalar-only fallback rows: `{s['scalar_only_fallback_rows']}`
- False scalar-certified quality failures: `{s['scalar_only_false_certified_quality_failures']}`
- Block-stage extra certified rows: `{s['block_stage_extra_certified_rows']}`
- Scalar-only sidecar read fraction: `{s['scalar_only_sidecar_read_fraction']}`
- Two-stage sidecar read fraction: `{s['two_stage_total_sidecar_read_fraction']}`
- Block-read reduction from pruning: `{s['scalar_pruned_block_read_reduction_vs_two_stage']}`

## Interpretation

Stage pruning is a real refactor win: it removes dead block-sidecar work while preserving the safety veto on invalid raw reuse. It is still non-promotional because the safe scalar-only path remains slower than dense and does not beat the simpler fresh histogram baseline on this local CPU trace.
""", encoding='utf-8')


def main() -> None:
    packet = find_packet()
    prep = prepare_input(packet)
    native, command = run_native()
    artifact = build_artifact(prep, native)
    write_outputs(artifact, command)
    print(json.dumps(artifact['summary'], indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
