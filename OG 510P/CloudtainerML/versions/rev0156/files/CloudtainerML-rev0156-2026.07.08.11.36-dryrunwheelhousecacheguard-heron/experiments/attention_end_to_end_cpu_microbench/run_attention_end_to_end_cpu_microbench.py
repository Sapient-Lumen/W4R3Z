#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, platform, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
META = json.loads((ROOT/'CUBE-META.json').read_text(encoding='utf-8')) if (ROOT/'CUBE-META.json').exists() else {'revision':'rev0047'}
REV = META.get('revision','rev0047'); REVUP = REV.upper()
SRC = Path(__file__).with_name('attention_end_to_end_cpu_microbench.cpp')
BIN = Path(__file__).with_name('attention_end_to_end_cpu_microbench.bin')
OUT = ROOT/'artifacts'/'probe-results'/f'{REVUP}_ATTENTION_END_TO_END_CPU_MICROBENCH.json'
MAN = ROOT/'artifacts'/'run-manifests'/f'{REVUP}_ATTENTION_END_TO_END_CPU_MICROBENCH_RUN_MANIFEST.json'

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
    dense_by_regime = {r['regime']: r for r in rows if r['method'] == 'dense_full_softmax'}
    summary = {}
    for regime in sorted({r['regime'] for r in rows}):
        rr = [r for r in rows if r['regime'] == regime]
        summary[regime] = {
            'dense_ns_per_row': dense_by_regime[regime]['mean_ns_per_row'],
            'best_quality_sparse_method': max([r for r in rr if r['method'] != 'dense_full_softmax'], key=lambda r: (r['quality_bar_rate'], -r['mean_selected_count']))['method'],
            'fastest_sparse_method': min([r for r in rr if r['method'] != 'dense_full_softmax'], key=lambda r: r['mean_ns_per_row'])['method'],
            'sparse_methods_passing_quality': [r['method'] for r in rr if r['method'] != 'dense_full_softmax' and r['quality_bar_rate'] >= 0.95],
        }
    data.update({
        'revision': REV,
        'summary': {
            'regime_summary': summary,
            'promotion_allowed': False,
            'claim_scope': 'native CPU single-row attention timing only; not a GPU fused-kernel or model-throughput claim',
            'main_veto': 'public/pretrained traces and real fused-kernel timing remain missing',
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
        'interpretation': 'This closes the selector-only timing gap by measuring score computation, selector work, sparse/dense softmax, and V accumulation on a named native CPU path. It is still not a GPU attention kernel, and broad-attention regimes remain sparse-hostile.'
    })
    OUT.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    MAN.write_text(json.dumps({
        'project': 'CloudtainerML',
        'revision': REV,
        'run': 'attention_end_to_end_cpu_microbench',
        'artifact': str(OUT.relative_to(ROOT)),
        'artifact_sha256': sha(OUT),
        'source': str(SRC.relative_to(ROOT)),
        'source_sha256': sha(SRC),
        'wrapper': str(Path(__file__).relative_to(ROOT)),
        'wrapper_sha256': sha(Path(__file__)),
        'compile_command': ' '.join(compile_cmd),
        'platform': platform.platform(),
        'promotion_scope': 'E2_native_cpu_row_microbench_not_E3_gpu_kernel',
    }, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'artifact': str(OUT.relative_to(ROOT)), 'rows': len(rows), 'summary': summary}, indent=2))

if __name__ == '__main__':
    main()
