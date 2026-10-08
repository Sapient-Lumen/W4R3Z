#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, platform, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
META = json.loads((ROOT/'CUBE-META.json').read_text(encoding='utf-8')) if (ROOT/'CUBE-META.json').exists() else {'revision':'rev0050'}
REV = META.get('revision','rev0050'); REVUP = REV.upper()
SRC = Path(__file__).with_name('value_norm_sidecar_cpu_path.cpp')
BIN = Path(__file__).with_name('value_norm_sidecar_cpu_path.bin')
OUT = ROOT/'artifacts'/'probe-results'/f'{REVUP}_VALUE_NORM_SIDECAR_CPU_PATH.json'
MAN = ROOT/'artifacts'/'run-manifests'/f'{REVUP}_VALUE_NORM_SIDECAR_CPU_PATH_RUN_MANIFEST.json'

def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda: f.read(1<<20), b''):
            h.update(c)
    return h.hexdigest()

def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True); MAN.parent.mkdir(parents=True, exist_ok=True)
    compile_cmd = ['g++','-std=c++17','-O3','-march=native',str(SRC.relative_to(ROOT)),'-o',str(BIN.relative_to(ROOT))]
    subprocess.run(compile_cmd, check=True, cwd=ROOT)
    subprocess.run([str(BIN.relative_to(ROOT)), str(OUT.relative_to(ROOT))], check=True, cwd=ROOT)
    data = json.loads(OUT.read_text(encoding='utf-8'))
    rows = data.get('rows', [])
    by = {(r['regime'], r['method']): r for r in rows}
    regimes = sorted({r['regime'] for r in rows})
    summary = {}
    for regime in regimes:
        dense = by[(regime, 'dense_full_softmax')]
        mass = by[(regime, 'mass_histogram_0p95_sparse')]
        sidecar = by[(regime, 'value_norm_exception_sidecar_0p95_sparse')]
        onfly = by[(regime, 'value_norm_exception_onthefly_0p95_sparse')]
        summary[regime] = {
            'dense_ns_per_row': dense['mean_ns_per_row'],
            'mass_hist_quality_rate': mass['quality_bar_rate'],
            'sidecar_quality_rate': sidecar['quality_bar_rate'],
            'sidecar_speedup_excluding_build': sidecar['speedup_vs_dense'],
            'sidecar_speedup_reuse_1': sidecar['speedup_vs_dense_with_sidecar_build_reuse_1'],
            'sidecar_speedup_reuse_8': sidecar['speedup_vs_dense_with_sidecar_build_reuse_8'],
            'sidecar_speedup_reuse_32': sidecar['speedup_vs_dense_with_sidecar_build_reuse_32'],
            'on_the_fly_speedup': onfly['speedup_vs_dense'],
            'on_the_fly_selection_uses_values': onfly['selection_uses_values'],
            'sidecar_selection_uses_values': sidecar['selection_uses_values'],
            'sidecar_selected_fraction': sidecar['selected_fraction'],
            'sidecar_norm_reads': sidecar['mean_norm_metadata_reads'],
            'on_the_fly_value_reads_for_selection': onfly['mean_value_reads_for_selection'],
        }
    blockers = [
        'actual_public_pretrained_trace_bundle_missing',
        'gpu_fused_attention_kernel_timing_missing',
        'gpu_sidecar_metadata_kernel_path_missing',
    ]
    data.update({
        'revision': REV,
        'summary': {
            'regime_summary': summary,
            'promotion_allowed': False,
            'claim_scope': 'native CPU single-row attention with value-norm sidecar accounting; not a GPU fused kernel or model-throughput claim',
            'main_veto': 'GPU/fused-kernel sidecar integration and public/pretrained traces remain missing',
            'sidecar_contract_repaired': True,
            'free_metadata_assumption_removed': True,
            'guard_fields': data.get('guard_fields', []),
        },
        'run_provenance': {
            'source_path': str(SRC.relative_to(ROOT)),
            'source_sha256': sha(SRC),
            'wrapper_path': str(Path(__file__).relative_to(ROOT)),
            'wrapper_sha256': sha(Path(__file__)),
            'compile_command': ' '.join(compile_cmd),
            'run_command': f'{BIN.relative_to(ROOT)} {OUT.relative_to(ROOT)}',
            'platform': platform.platform(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python': sys.version.split()[0],
        },
        'remaining_blockers': blockers,
        'interpretation': 'rev0050 removes the free value-norm metadata assumption by measuring precomputed sidecar reads separately from on-the-fly norm computation. On-the-fly norm computation reads all values during selection and is therefore a negative sparse control. Precomputed sidecars are more plausible but still need fused GPU/kernel integration and public/pretrained trace prevalence.'
    })
    OUT.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    MAN.write_text(json.dumps({
        'project': 'CloudtainerML',
        'revision': REV,
        'run': 'value_norm_sidecar_cpu_path',
        'artifact': str(OUT.relative_to(ROOT)),
        'artifact_sha256': sha(OUT),
        'source': str(SRC.relative_to(ROOT)),
        'source_sha256': sha(SRC),
        'wrapper': str(Path(__file__).relative_to(ROOT)),
        'wrapper_sha256': sha(Path(__file__)),
        'compile_command': ' '.join(compile_cmd),
        'platform': platform.platform(),
        'promotion_scope': 'E2_5_native_cpu_sidecar_accounting_not_E3_gpu_kernel',
    }, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'artifact': str(OUT.relative_to(ROOT)), 'rows': len(rows), 'summary': summary}, indent=2))

if __name__ == '__main__':
    main()
