#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, os, platform, shutil, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REV = 'rev0052'
REVUP = REV.upper()
SRC = ROOT / 'experiments' / 'observable_block_index_pruning' / 'observable_block_index_pruning.cpp'
OUT = ROOT / 'artifacts' / 'probe-results' / f'{REVUP}_OBSERVABLE_BLOCK_INDEX_PRUNING.json'
BIN_DIR = ROOT / 'artifacts' / 'bin'
BIN = BIN_DIR / f'{REVUP}_observable_block_index_pruning'
MAN = ROOT / 'artifacts' / 'run-manifests' / f'{REVUP}_OBSERVABLE_BLOCK_INDEX_PRUNING_RUN_MANIFEST.json'


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    MAN.parent.mkdir(parents=True, exist_ok=True)
    compiler = shutil.which('g++') or shutil.which('clang++')
    if not compiler:
        raise SystemExit('no C++ compiler available')
    compile_cmd = [compiler, '-std=c++17', '-O3', '-march=native', str(SRC), '-o', str(BIN)]
    t0 = time.time()
    subprocess.run(compile_cmd, cwd=ROOT, check=True)
    compile_s = time.time() - t0
    run_cmd = [str(BIN), str(OUT)]
    t1 = time.time()
    subprocess.run(run_cmd, cwd=ROOT, check=True)
    run_s = time.time() - t1
    artifact = json.loads(OUT.read_text(encoding='utf-8'))
    manifest = {
        'project': 'CloudtainerML',
        'revision': REV,
        'artifact': OUT.relative_to(ROOT).as_posix(),
        'source': SRC.relative_to(ROOT).as_posix(),
        'binary': BIN.relative_to(ROOT).as_posix(),
        'source_sha256': sha256(SRC),
        'binary_sha256': sha256(BIN),
        'artifact_sha256': sha256(OUT),
        'compiler': compiler,
        'compile_cmd': compile_cmd,
        'run_cmd': run_cmd,
        'compile_seconds': compile_s,
        'run_seconds': run_s,
        'python': sys.version,
        'platform': platform.platform(),
        'processor': platform.processor(),
        'pid': os.getpid(),
        'generated_at_unix': time.time(),
        'benchmark_scope': artifact.get('benchmark_scope'),
        'promotion_allowed': artifact.get('summary', {}).get('promotion_allowed'),
        'public_pretrained_trace_loaded': artifact.get('public_pretrained_trace_loaded'),
        'gpu_kernel_claim': artifact.get('gpu_kernel_claim'),
    }
    MAN.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'artifact': str(OUT), 'manifest': str(MAN), 'rows': len(artifact.get('rows', [])), 'run_seconds': run_s}, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
