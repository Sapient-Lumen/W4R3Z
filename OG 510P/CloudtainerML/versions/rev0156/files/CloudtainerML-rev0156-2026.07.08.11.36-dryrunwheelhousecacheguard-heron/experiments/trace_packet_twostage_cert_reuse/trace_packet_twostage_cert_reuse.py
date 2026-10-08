#!/usr/bin/env python3
"""rev0070 two-stage certified support-reuse replay.

rev0069 proved a safe support-reuse certificate but paid a token-scale outside-bound
scan. rev0070 tests a stricter engineering repair: try a scalar max-bound sidecar,
then a block-summary sidecar, and fall back to fresh full-row histogram selection
only when reuse cannot be certified. All fallback and certificate work is paid in
native CPU timing; the sidecar build is reported separately.
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
STAMP = '2026-06-18T15:55:00-04:00'
OUT = ROOT/'artifacts'/'probe-results'/f'{REVUP}_TWOSTAGE_CERTIFIED_SUPPORT_REUSE.json'
MAN = ROOT/'artifacts'/'run-manifests'/f'{REVUP}_TWOSTAGE_CERTIFIED_SUPPORT_REUSE_RUN_MANIFEST.json'
BIN = ROOT/'artifacts'/'native-inputs'/f'{REVUP}_TWOSTAGE_CERTIFIED_SUPPORT_REUSE_INPUT.bin'
BUILD = ROOT/'artifacts'/'native-build'/'trace_packet_twostage_cert_reuse'
CPP = ROOT/'experiments'/'trace_packet_twostage_cert_reuse'/'trace_packet_twostage_cert_reuse.cpp'
EXE = BUILD/'trace_packet_twostage_cert_reuse'
REPEATS = int(os.environ.get('CTML_TWOSTAGE_CERT_REPEATS','2500'))
TARGET_MASS = float(os.environ.get('CTML_TWOSTAGE_CERT_TARGET_MASS','0.96'))
HIST_BINS = int(os.environ.get('CTML_TWOSTAGE_CERT_HIST_BINS','32'))
BLOCK_SIZE = int(os.environ.get('CTML_TWOSTAGE_CERT_BLOCK_SIZE','8'))


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
        f.write(b'CTMLTR70')
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
    token = all_rows.get('full_token_certificate', {})
    fresh = all_rows.get('fresh_hist_index', {})
    summary = {
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
        'local_tiny_trace_only': True,
        'two_stage_certificate_tested': True,
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
        'two_stage_speedup_vs_dense': speeds.get('two_stage_certificate'),
        'candidate_reuse_rows': cert.get('candidate_reuse_rows'),
        'two_stage_scalar_certified_rows': cert.get('two_stage_scalar_certified_rows'),
        'two_stage_block_certified_rows': cert.get('two_stage_block_certified_rows'),
        'two_stage_certified_reuse_rows': cert.get('two_stage_certified_reuse_rows'),
        'two_stage_fallback_rows': cert.get('two_stage_fallback_rows'),
        'full_token_certified_reuse_rows': cert.get('full_token_certified_reuse_rows'),
        'two_stage_false_certified_quality_failures': cert.get('two_stage_false_certified_quality_failures'),
        'two_stage_qk_dot_fraction': acct.get('two_stage_certificate_qk_dot_fraction'),
        'full_token_qk_dot_fraction': acct.get('full_token_certificate_qk_dot_fraction'),
        'full_token_bound_scan_token_fraction': acct.get('full_token_bound_scan_token_fraction'),
        'two_stage_total_sidecar_read_fraction': acct.get('two_stage_total_sidecar_read_fraction'),
        'sidecar_vs_token_bound_read_reduction': acct.get('sidecar_vs_token_bound_read_reduction'),
        'promotion_allowed': False,
        'deployable_promoted_paths': [],
        'remaining_blockers': [
            'actual_public_pretrained_trace_bundle_missing',
            'gpu_fused_attention_kernel_timing_missing',
            'two_stage_certificate_safe_but_not_speed_positive_on_local_cpu_trace',
            'sidecar_build_and_validity_need_model_cache_integration',
            'support_reuse_still_requires_full_or_near_full_fallback_for_uncertified_rows',
        ],
    }
    interpretation = (
        'The two-stage sidecar certificate sharply reduces outside-bound metadata reads versus the rev0069 full token scan. '
        'It preserves the safety veto on raw anchor reuse, but speed is still not promoted: local CPU timing remains below dense/fresh baselines once selector, sidecar checks, and fallback are paid.'
    )
    return {
        'project': 'CloudtainerML',
        'revision': REV,
        'artifact': f'{REVUP}_TWOSTAGE_CERTIFIED_SUPPORT_REUSE',
        'generated_at': STAMP,
        'measurement_scope': 'native CPU local tiny Q/K/V trace replay; two-stage support-reuse certificate uses observable Q/K/key-cache sidecars; fallback and certificate-bound work are paid; sidecar build is reported separately; not public/pretrained; not GPU; not fused-kernel evidence',
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
            'experiments/trace_packet_twostage_cert_reuse/trace_packet_twostage_cert_reuse.py': sha256_file(Path(__file__)),
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
    doc = ROOT/'docs'/'04-audit'/'rev0070-two-stage-certified-support-reuse.md'
    s = artifact['summary']
    doc.write_text(f"""# rev0070 — two-stage certified support reuse

rev0069's certified reuse was safe but slow because every candidate needed a token-scale outside-bound scan. rev0070 adds a scalar precheck and block-summary sidecar before fallback.

## Result

- Raw anchor quality rate: `{s['raw_anchor_quality_rate']}`
- Raw anchor speedup vs dense: `{s['raw_anchor_speedup_vs_dense']}`
- Full token certificate speedup: `{s['full_token_speedup_vs_dense']}`
- Two-stage certificate quality rate: `{s['two_stage_quality_rate']}`
- Two-stage certificate speedup: `{s['two_stage_speedup_vs_dense']}`
- Scalar-certified rows: `{s['two_stage_scalar_certified_rows']}`
- Block-certified rows: `{s['two_stage_block_certified_rows']}`
- Fallback rows: `{s['two_stage_fallback_rows']}`
- False certified quality failures: `{s['two_stage_false_certified_quality_failures']}`
- Full-token outside-bound scan fraction: `{s['full_token_bound_scan_token_fraction']}`
- Two-stage sidecar read fraction: `{s['two_stage_total_sidecar_read_fraction']}`
- Bound-read reduction: `{s['sidecar_vs_token_bound_read_reduction']}`

## Interpretation

The two-stage sidecar reduces certificate metadata scans, but it remains non-promotional because speed is still negative on this native CPU trace and the sidecar has not been integrated into a real KV-cache/kernel path.
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
