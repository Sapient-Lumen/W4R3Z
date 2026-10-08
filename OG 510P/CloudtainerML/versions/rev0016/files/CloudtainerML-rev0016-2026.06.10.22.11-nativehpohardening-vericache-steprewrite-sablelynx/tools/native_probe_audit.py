#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8')) if (ROOT / 'CUBE-META.json').exists() else {}
REV = META.get('revision', 'rev0016')
REVUP = REV.upper()
AUDIT_DIR = ROOT / 'artifacts' / 'audit'
PROBE_DIR = ROOT / 'artifacts' / 'probe-results'

OUTPUT_NAMES = {
    'express_coreset.cpp': 'EXPRESS_STREAMING_CORESET',
    'token_precision_frontier.cpp': 'NATIVE_TOKEN_PRECISION_FRONTIER',
    'residual_stream_kv.cpp': 'RESIDUAL_STREAM_KV',
    'query_move_probe.cpp': 'QUERY_MOVE_CACHE',
    'gated_delta_memory_probe.cpp': 'GATED_DELTA_MEMORY',
    'residual_kv_sensitivity.cpp': 'RESIDUAL_KV_SENSITIVITY',
    'query_move_phase_scan.cpp': 'QUERY_MOVE_PHASE_SCAN',
    'lrkv_head_diversity.cpp': 'LRKV_HEAD_DIVERSITY',
    'stochastic_sparse_attention.cpp': 'STOCHASTIC_SPARSE_ATTENTION',
    'kvcat_compressibility.cpp': 'KVCAT_COMPRESSIBILITY',
    'native_hpo_phase.cpp': 'NATIVE_HPO_PHASE',
    'hypergraph_trace_probe.cpp': 'HYPERGRAPH_MEMORY_TRACE',
    'memory_sycophancy_probe.cpp': 'MEMORY_SYCOPHANCY_TRAP',
    'dfssm_quant_probe.cpp': 'DFSSM_QUANT_SCAFFOLD',
    'vericache_guard_probe.cpp': 'VERICACHE_GUARD',
    'step_rewrite_probe.cpp': 'PERIODIC_CACHE_REWRITE',
    'memory_provenance_phase.cpp': 'MEMORY_PROVENANCE_PHASE',
}

def slug_from_cpp(path: Path) -> str:
    return OUTPUT_NAMES.get(path.name, re.sub(r'[^A-Za-z0-9]+', '_', path.stem).strip('_').upper())

def run(cmd: list[str], cwd: Path | None = None, timeout: int = 60) -> dict:
    t0 = time.time()
    try:
        cp = subprocess.run([str(x) for x in cmd], cwd=str(cwd) if cwd else None,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
        return {'cmd': cmd, 'returncode': cp.returncode, 'stdout': cp.stdout[-2000:], 'stderr': cp.stderr[-2000:], 'seconds': round(time.time()-t0, 4)}
    except subprocess.TimeoutExpired as e:
        return {'cmd': cmd, 'returncode': 124, 'stdout': '', 'stderr': 'timeout', 'seconds': round(time.time()-t0, 4), 'timeout': timeout}
    except Exception as e:
        return {'cmd': cmd, 'returncode': 999, 'stdout': '', 'stderr': repr(e), 'seconds': round(time.time()-t0, 4)}

def inspect_json(path: Path) -> dict:
    info = {'internal_revision': None, 'json_probe': None, 'has_primary_metric': False, 'row_count': None}
    if not path.exists():
        return info
    try:
        obj = json.loads(path.read_text(encoding='utf-8'))
        info['internal_revision'] = obj.get('revision')
        info['json_probe'] = obj.get('probe')
        rows = obj.get('rows')
        info['row_count'] = len(rows) if isinstance(rows, list) else rows if isinstance(rows, int) else None
        summary = obj.get('summary') if isinstance(obj.get('summary'), dict) else {}
        info['has_primary_metric'] = isinstance(summary.get('primary_metric'), dict)
    except Exception as e:
        info['json_error'] = repr(e)
    return info

def main() -> int:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    PROBE_DIR.mkdir(parents=True, exist_ok=True)
    cpp_paths = sorted((ROOT / 'experiments').glob('*/*.cpp'), key=lambda p: p.as_posix())
    cpp_files = [p.relative_to(ROOT).as_posix() for p in cpp_paths]
    gpp = shutil.which('g++')
    gcc = shutil.which('gcc')
    results = []
    status = 'pass'
    if not gpp:
        status = 'fail'
    else:
        for target in cpp_paths:
            slug = slug_from_cpp(target)
            out = PROBE_DIR / f'{REVUP}_{slug}_SMOKE.json'
            # Compile-only syntax/object sanity avoids checked-in binaries and keeps audit stable.
            compile_result = run([gpp, '-O1', '-std=c++17', '-fsyntax-only', str(target)], timeout=90)
            if compile_result['returncode'] != 0:
                status = 'fail'
            info = inspect_json(out)
            output_exists = out.exists()
            run_result = {'skipped': 'audit inspects current-revision smoke output; probes are run by smoke-generation commands before audit', 'returncode': 0 if output_exists else 1, 'seconds': 0}
            if not output_exists:
                status = 'fail'
            if info.get('internal_revision') not in (None, REV):
                status = 'fail'
            if not info.get('has_primary_metric'):
                status = 'fail'
            results.append({
                'source': str(target.relative_to(ROOT)),
                'slug': slug,
                'compile': compile_result,
                'run': run_result,
                'output': str(out.relative_to(ROOT)),
                'output_exists': output_exists,
                **info,
            })
    checked_in_binaries = []
    for p in (ROOT / 'experiments').rglob('*'):
        if p.is_file() and p.stat().st_mode & 0o111 and p.suffix not in {'.py', '.sh'}:
            checked_in_binaries.append(p.relative_to(ROOT).as_posix())
    if checked_in_binaries:
        status = 'fail'
    revision_mismatches = [r for r in results if r.get('internal_revision') not in (None, REV)]
    missing_primary_metric = [r for r in results if not r.get('has_primary_metric')]
    report = {
        'project': 'CloudtainerML',
        'revision': REV,
        'status': status,
        'gcc': gcc,
        'gpp': gpp,
        'mode': 'compile_syntax_and_inspect_current_outputs',
        'cpp_files': cpp_files,
        'compiled_probe_count': len(results),
        'revision_mismatches': revision_mismatches,
        'missing_primary_metric': missing_primary_metric,
        'checked_in_binary_candidates': checked_in_binaries,
        'results': results,
        'note': 'Native audit syntax-compiles every experiments/*/*.cpp source, verifies current-revision JSON outputs with primary_metric, and rejects checked-in binaries. It does not retain compiled binaries.',
    }
    (AUDIT_DIR / f'{REVUP}_NATIVE_PROBE_AUDIT.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    md = [
        f'# Native probe audit — {REV}', '', f'Status: **{status}**', '',
        f'- mode: `{report["mode"]}`', f'- gcc: `{gcc}`', f'- g++: `{gpp}`', f'- C/C++ source files: {len(cpp_files)}',
        f'- syntax-compiled probe count: {len(results)}', f'- revision mismatches: {len(revision_mismatches)}',
        f'- missing primary metrics: {len(missing_primary_metric)}', f'- checked-in binary candidates: {len(checked_in_binaries)}',
        '', '## Probes', ''
    ]
    for r in results:
        md.append(f"- `{r['source']}` → `{r['output']}` syntax rc={r['compile']['returncode']} output={r['output_exists']} rows={r.get('row_count')} internal_rev={r.get('internal_revision')} metric={r.get('has_primary_metric')}")
    if checked_in_binaries:
        md.extend(['', '## Binary candidates', *[f'- `{x}`' for x in checked_in_binaries]])
    (AUDIT_DIR / f'{REVUP}_NATIVE_PROBE_AUDIT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'status': status, 'mode': report['mode'], 'gcc': gcc, 'gpp': gpp, 'cpp_files': len(cpp_files), 'compiled_probe_count': len(results), 'revision_mismatches': len(revision_mismatches), 'missing_primary_metric': len(missing_primary_metric), 'checked_in_binary_candidates': len(checked_in_binaries)}, indent=2))
    return 0 if status == 'pass' else 1

if __name__ == '__main__':
    raise SystemExit(main())
