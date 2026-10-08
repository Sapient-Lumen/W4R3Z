#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, platform, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8')) if (ROOT / 'CUBE-META.json').exists() else {'revision': 'rev0051'}
REV = META.get('revision', 'rev0051')
REVUP = REV.upper()
SRC = Path(__file__).with_name('score_path_block_pruning.cpp')
BIN = Path(__file__).with_name('score_path_block_pruning.bin')
OUT = ROOT / 'artifacts' / 'probe-results' / f'{REVUP}_SCORE_PATH_BLOCK_PRUNING.json'
MAN = ROOT / 'artifacts' / 'run-manifests' / f'{REVUP}_SCORE_PATH_BLOCK_PRUNING_RUN_MANIFEST.json'


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    MAN.parent.mkdir(parents=True, exist_ok=True)
    compile_cmd = ['g++', '-std=c++17', '-O3', '-march=native', str(SRC.relative_to(ROOT)), '-o', str(BIN.relative_to(ROOT))]
    subprocess.run(compile_cmd, check=True, cwd=ROOT)
    subprocess.run([str(BIN.relative_to(ROOT)), str(OUT.relative_to(ROOT))], check=True, cwd=ROOT)
    data = json.loads(OUT.read_text(encoding='utf-8'))
    rows = data.get('rows', [])
    by = {(r['regime'], r['method']): r for r in rows}
    regimes = sorted({r['regime'] for r in rows})
    regime_summary = {}
    for regime in regimes:
        dense = by[(regime, 'dense_full_attention')]
        hist = by[(regime, 'dense_score_mass_histogram_0p95_sparse')]
        block = by[(regime, 'block_upper_bound_pruned_0p95_sparse')]
        regime_summary[regime] = {
            'dense_ns_per_row': dense['mean_ns_per_row'],
            'hist_speedup_vs_dense': hist['speedup_vs_dense'],
            'hist_qk_dot_fraction': hist['qk_dot_fraction_vs_dense'],
            'hist_selected_value_fraction': hist['selected_value_fraction'],
            'hist_quality_bar_rate': hist['quality_bar_rate'],
            'block_speedup_vs_dense': block['speedup_vs_dense'],
            'block_qk_dot_fraction': block['qk_dot_fraction_vs_dense'],
            'block_opened_block_fraction': block['opened_block_fraction'],
            'block_selected_value_fraction': block['selected_value_fraction'],
            'block_quality_bar_rate': block['quality_bar_rate'],
            'block_lower_bound_mass_certificate': block['mean_lower_bound_mass_certificate'],
        }
    blockers = [
        'actual_public_pretrained_trace_bundle_missing',
        'gpu_fused_attention_kernel_timing_missing',
        'model_trace_block_bound_tightness_missing',
    ]
    data.update({
        'revision': REV,
        'summary': {
            **data.get('summary', {}),
            'regime_summary': regime_summary,
            'promotion_allowed': False,
            'claim_scope': 'native CPU single-row score-path accounting; not GPU/fused-kernel or public/pretrained model evidence',
            'score_path_contract_repaired': True,
            'dense_score_selector_claim_boundary_added': True,
            'main_veto': 'sparse selectors must either avoid dense QK scoring or state that they only sparsify V/softmax after dense scoring',
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
        'interpretation': 'rev0051 attacks the QK score-path blind spot. The dense-score histogram method may look sparse in value reads, but it explicitly computes all token scores first. The block upper-bound method demonstrates a conservative route to skip token QK scores in tight clustered regimes, while broad or loose-bound regimes correctly collapse toward dense computation.',
    })
    OUT.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    MAN.write_text(json.dumps({
        'project': 'CloudtainerML',
        'revision': REV,
        'run': 'score_path_block_pruning',
        'artifact': str(OUT.relative_to(ROOT)),
        'artifact_sha256': sha(OUT),
        'source': str(SRC.relative_to(ROOT)),
        'source_sha256': sha(SRC),
        'wrapper': str(Path(__file__).relative_to(ROOT)),
        'wrapper_sha256': sha(Path(__file__)),
        'compile_command': ' '.join(compile_cmd),
        'platform': platform.platform(),
        'promotion_scope': 'E2_5_native_cpu_score_path_microbench_not_E3_gpu_kernel',
    }, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'artifact': str(OUT.relative_to(ROOT)), 'rows': len(rows), 'summary': regime_summary}, indent=2))


if __name__ == '__main__':
    main()
