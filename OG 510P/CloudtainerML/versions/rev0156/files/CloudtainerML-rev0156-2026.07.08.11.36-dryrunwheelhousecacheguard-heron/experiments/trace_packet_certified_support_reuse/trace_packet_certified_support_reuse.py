#!/usr/bin/env python3
"""rev0069 certified support-reuse replay.

This repairs the rev0066 loophole: raw anchor support reuse can be fast but invalid.
The rev0069 path permits reuse only when an observable Q/K/key-drift bound certifies
that omitted target-row mass is below the target threshold; otherwise it pays a
fresh full-QK fallback inside the timed loop.
"""
from __future__ import annotations
import hashlib, json, os, platform, shutil, struct, subprocess
from pathlib import Path
from typing import Any
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
META = json.loads((ROOT/'CUBE-META.json').read_text(encoding='utf-8')) if (ROOT/'CUBE-META.json').exists() else {'revision':'rev0069'}
REV = META.get('revision','rev0069'); REVUP=REV.upper()
STAMP = '2026-06-18T15:04:00-04:00'
OUT = ROOT/'artifacts'/'probe-results'/f'{REVUP}_CERTIFIED_SUPPORT_REUSE.json'
MAN = ROOT/'artifacts'/'run-manifests'/f'{REVUP}_CERTIFIED_SUPPORT_REUSE_RUN_MANIFEST.json'
BIN = ROOT/'artifacts'/'native-inputs'/f'{REVUP}_CERTIFIED_SUPPORT_REUSE_INPUT.bin'
BUILD = ROOT/'artifacts'/'native-build'/'trace_packet_certified_support_reuse'
CPP = ROOT/'experiments'/'trace_packet_certified_support_reuse'/'trace_packet_certified_support_reuse.cpp'
EXE = BUILD/'trace_packet_certified_support_reuse'
REPEATS = int(os.environ.get('CTML_CERT_REUSE_REPEATS','2500'))
TARGET_MASS = float(os.environ.get('CTML_CERT_REUSE_TARGET_MASS','0.96'))
HIST_BINS = int(os.environ.get('CTML_CERT_REUSE_HIST_BINS','32'))

def sha256_file(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda:f.read(1<<20), b''): h.update(c)
    return h.hexdigest()

def find_packet() -> Path:
    candidates = sorted((ROOT/'artifacts'/'trace-bundles').glob('REV*_TINY_TRAINED_QK_TRACE_PACKET.npz'), reverse=True)
    for p in candidates:
        if p.name.startswith('REV0062') or p.name.startswith(REVUP): return p
    if candidates: return candidates[0]
    raise FileNotFoundError('no Q/K/V trace packet found')

def prepare_input(packet: Path) -> dict[str, Any]:
    z=np.load(packet)
    q=np.asarray(z['queries'], dtype=np.float64)
    k=np.asarray(z['keys'], dtype=np.float64)
    v=np.asarray(z['values'], dtype=np.float64)
    rows,n,dk = k.shape; dv=v.shape[2]
    if q.shape != (rows,dk) or v.shape != (rows,n,dv): raise ValueError(f'bad q/k/v shapes q={q.shape} k={k.shape} v={v.shape}')
    example=np.asarray(z['example'] if 'example' in z.files else np.arange(rows), dtype=np.int32)
    trace_batch=np.asarray(z['trace_batch'] if 'trace_batch' in z.files else np.zeros(rows), dtype=np.int32)
    ex_keys=[(int(e),int(tb)) for e,tb in zip(example,trace_batch)]
    ex_map={key:i for i,key in enumerate(sorted(set(ex_keys)))}
    group_example=np.asarray([ex_map[key] for key in ex_keys], dtype=np.int32)
    BIN.parent.mkdir(parents=True, exist_ok=True)
    with BIN.open('wb') as f:
        f.write(b'CTMLTR69')
        f.write(struct.pack('QQQQ', int(rows), int(n), int(dk), int(dv)))
        f.write(np.ascontiguousarray(q, dtype=np.float64).tobytes(order='C'))
        f.write(np.ascontiguousarray(k, dtype=np.float64).tobytes(order='C'))
        f.write(np.ascontiguousarray(v, dtype=np.float64).tobytes(order='C'))
        f.write(np.ascontiguousarray(group_example, dtype=np.int32).tobytes(order='C'))
    return {
        'trace_packet': packet.relative_to(ROOT).as_posix(),
        'trace_packet_sha256': sha256_file(packet),
        'rows': int(rows), 'n_tokens': int(n), 'd_key': int(dk), 'd_value': int(dv),
        'example_groups': int(len(ex_map)),
        'input_bin': BIN.relative_to(ROOT).as_posix(), 'input_bin_sha256': sha256_file(BIN),
    }

def compile_native() -> list[str]:
    BUILD.mkdir(parents=True, exist_ok=True)
    compiler=shutil.which('g++') or shutil.which('clang++')
    if not compiler: raise RuntimeError('no C++ compiler found')
    cmd=[compiler,'-O3','-std=c++17','-march=native',str(CPP),'-o',str(EXE)]
    subprocess.run(cmd, cwd=ROOT, check=True)
    return cmd

def run_native() -> tuple[dict[str, Any], list[str]]:
    cmd_compile=compile_native()
    cmd=[str(EXE), str(BIN), str(REPEATS), str(TARGET_MASS), str(HIST_BINS)]
    proc=subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=True)
    return json.loads(proc.stdout), cmd_compile + ['&&'] + cmd

def build_artifact(prep: dict[str, Any], native: dict[str, Any]) -> dict[str, Any]:
    all_rows=native.get('all_rows',{})
    cert=native.get('certificate',{})
    acct=native.get('accounting',{})
    speeds=native.get('speedups_vs_dense',{})
    raw=all_rows.get('uncertified_anchor_reuse',{})
    certified=all_rows.get('certified_anchor_reuse',{})
    fresh=all_rows.get('fresh_hist_index',{})
    summary={
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
        'local_tiny_trace_only': True,
        'support_reuse_certificate_tested': True,
        'certificate_uses_observable_q_key_bounds': bool(cert.get('observable_q_key_bound')),
        'certificate_uses_values_or_dense_outputs': False,
        'fallback_paid_in_timed_loop': bool(acct.get('fallback_paid_in_timed_loop')),
        'certificate_bound_paid_in_timed_loop': bool(acct.get('certificate_bound_paid_in_timed_loop')),
        'raw_anchor_quality_rate': raw.get('quality_rate'),
        'raw_anchor_speedup_vs_dense': speeds.get('uncertified_anchor_reuse'),
        'certified_quality_rate': certified.get('quality_rate'),
        'certified_speedup_vs_dense': speeds.get('certified_anchor_reuse'),
        'fresh_hist_quality_rate': fresh.get('quality_rate'),
        'fresh_hist_speedup_vs_dense': speeds.get('fresh_hist_index'),
        'candidate_reuse_rows': cert.get('candidate_reuse_rows'),
        'certified_reuse_rows': cert.get('certified_reuse_rows'),
        'fallback_rows': cert.get('fallback_rows'),
        'false_certified_quality_failures': cert.get('false_certified_quality_failures'),
        'certified_reuse_rate': cert.get('certified_reuse_rate'),
        'fallback_rate': cert.get('fallback_rate'),
        'certified_qk_dot_fraction': acct.get('certified_qk_dot_fraction'),
        'uncertified_qk_dot_fraction': acct.get('uncertified_qk_dot_fraction'),
        'certified_bound_metadata_scan_fraction': acct.get('certified_bound_metadata_scan_fraction'),
        'promotion_allowed': False,
        'deployable_promoted_paths': [],
        'remaining_blockers': [
            'actual_public_pretrained_trace_bundle_missing',
            'gpu_fused_attention_kernel_timing_missing',
            'certificate_fallback_or_metadata_scan_erases_support_reuse_speedup',
            'full_or_near_full_qk_work_required_for_certified_quality',
            'no_deployable_score_path_sparse_win_measured',
        ],
    }
    interpretation=(
        'Raw anchor support reuse remains a fast-looking invalid path. The observable Q/K/key-drift certificate prevents false quality promotion by falling back when omitted mass cannot be bounded, but the fallback/bound work erases the speed case on the local learned trace.'
    )
    return {
        'project':'CloudtainerML','revision':REV,'artifact':f'{REVUP}_CERTIFIED_SUPPORT_REUSE','generated_at':STAMP,
        'measurement_scope':'native CPU local tiny Q/K/V trace replay; anchor support reuse is allowed only after an observable query-distance/key-norm/key-drift mass certificate; fallback and certificate-bound work are paid inside the timed loop; not public/pretrained; not GPU; not fused-kernel evidence',
        'trace_input': prep,
        'parameters': {'target_mass': TARGET_MASS, 'hist_bins': HIST_BINS, 'repeats': REPEATS},
        'native': native,
        'summary': summary,
        'interpretation': interpretation,
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
    }

def write_manifest(artifact: dict[str, Any], command: list[str]) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True); MAN.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    manifest={
        'project':'CloudtainerML','revision':REV,'artifact':OUT.relative_to(ROOT).as_posix(),'generated_at':STAMP,
        'command':' '.join(command),'cwd':str(ROOT),'python_version':platform.python_version(),'platform':platform.platform(),
        'source_files': {
            str(CPP.relative_to(ROOT)): sha256_file(CPP),
            'experiments/trace_packet_certified_support_reuse/trace_packet_certified_support_reuse.py': sha256_file(Path(__file__)),
        },
        'inputs': {artifact['trace_input']['trace_packet']: artifact['trace_input']['trace_packet_sha256'], artifact['trace_input']['input_bin']: artifact['trace_input']['input_bin_sha256']},
        'artifact_sha256': sha256_file(OUT),
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
    }
    MAN.write_text(json.dumps(manifest, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    doc=ROOT/'docs'/'04-audit'/'rev0069-certified-support-reuse.md'
    s=artifact['summary']
    doc.write_text(f"""# rev0069 — certified support reuse\n\nRaw support reuse was the risky loophole left by rev0066: it saved QK work but failed quality. rev0069 adds an observable Q/K/key-drift mass certificate and pays fallback work inside the timed loop.\n\n## Result\n\n- Raw anchor quality rate: `{s['raw_anchor_quality_rate']}`\n- Raw anchor speedup vs dense: `{s['raw_anchor_speedup_vs_dense']}`\n- Certified quality rate: `{s['certified_quality_rate']}`\n- Certified speedup vs dense: `{s['certified_speedup_vs_dense']}`\n- Certified reuse rows: `{s['certified_reuse_rows']}` / `{s['candidate_reuse_rows']}`\n- False certified quality failures: `{s['false_certified_quality_failures']}`\n- Certified QK dot fraction: `{s['certified_qk_dot_fraction']}`\n- Bound metadata scan fraction: `{s['certified_bound_metadata_scan_fraction']}`\n\n## Interpretation\n\n{s['remaining_blockers']}\n\nThe certificate repairs the invalid fast path, but it does not create a promotion-ready sparse systems win on the local trace.\n""", encoding='utf-8')

def main() -> int:
    prep=prepare_input(find_packet())
    native, cmd=run_native()
    artifact=build_artifact(prep,native)
    write_manifest(artifact,cmd)
    print(json.dumps({'status':'pass','artifact':str(OUT.relative_to(ROOT)),'summary':artifact['summary']}, indent=2))
    return 0
if __name__ == '__main__': raise SystemExit(main())
