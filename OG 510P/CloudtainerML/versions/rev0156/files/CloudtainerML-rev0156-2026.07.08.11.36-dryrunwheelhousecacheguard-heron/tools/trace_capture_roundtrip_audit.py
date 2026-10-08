#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REV = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8')).get('revision', 'rev0049')
REVUP = REV.upper()
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


def load(rel: str) -> Any:
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


def shape_of_npz(rel: str) -> dict[str, Any]:
    path = ROOT / rel
    data = np.load(path, allow_pickle=False)
    return {k: list(data[k].shape) for k in data.files}


def gate_check(rel: str) -> dict[str, Any]:
    payload = load(rel)
    rows = payload.get('rows', [])
    return {
        'artifact': rel,
        'exists': (ROOT / rel).exists(),
        'trace_gate_status': payload.get('trace_gate_status'),
        'external_trace_loaded': payload.get('external_trace_loaded'),
        'public_pretrained_trace_loaded': payload.get('public_pretrained_trace_loaded'),
        'row_count': len(rows),
        'row_external_true_count': sum(1 for r in rows if r.get('external_trace_loaded')),
        'row_public_true_count': sum(1 for r in rows if r.get('public_pretrained_trace_loaded')),
        'oracle_leakage_rows': sum(1 for r in rows if r.get('selection_oracle_leakage_detected') or r.get('selection_uses_values') or r.get('selection_uses_dense_output')),
        'trace_source_types': sorted({r.get('trace_source_type') for r in rows}),
        'source_hash_ok': bool(payload.get('run_provenance', {}).get('source_sha256')),
    }


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    roundtrip_rel = f'artifacts/probe-results/{REVUP}_TRACE_BUNDLE_ROUNDTRIP.json'
    default_rel = f'artifacts/probe-results/{REVUP}_PUBLIC_TRACE_GATE_SURROGATE.json'
    sv_gate_rel = f'artifacts/probe-results/{REVUP}_EXTERNAL_TRACE_ROUNDTRIP_SCORES_VALUES_GATE.json'
    qkv_gate_rel = f'artifacts/probe-results/{REVUP}_EXTERNAL_TRACE_ROUNDTRIP_QKV_GATE.json'
    needed = [roundtrip_rel, default_rel, sv_gate_rel, qkv_gate_rel]
    for rel in needed:
        if not (ROOT / rel).exists():
            errors.append('missing artifact: ' + rel)
    roundtrip = load(roundtrip_rel) if (ROOT / roundtrip_rel).exists() else {}
    default_gate = gate_check(default_rel) if (ROOT / default_rel).exists() else {}
    sv_gate = gate_check(sv_gate_rel) if (ROOT / sv_gate_rel).exists() else {}
    qkv_gate = gate_check(qkv_gate_rel) if (ROOT / qkv_gate_rel).exists() else {}

    if roundtrip.get('primary_metric', {}).get('value') is not True:
        errors.append('roundtrip primary invariant did not pass')
    if roundtrip.get('claims_invariant', {}).get('arbitrary_external_npz_is_not_public_pretrained') is not True:
        errors.append('claims invariant missing or false')

    bundle_infos = (roundtrip.get('bundle_artifacts') or {})
    shapes: dict[str, Any] = {}
    for key in ['scores_values', 'qkv']:
        info = bundle_infos.get(key) or {}
        rel = info.get('path')
        if not rel or not (ROOT / rel).exists():
            errors.append(f'missing {key} trace bundle')
            continue
        if info.get('sha256') and sha256_file(ROOT / rel) != info.get('sha256'):
            errors.append(f'{key} trace bundle sha mismatch')
        shapes[key] = shape_of_npz(rel)
    sv_shapes = shapes.get('scores_values', {})
    if not {'scores', 'values', 'value_norms'}.issubset(sv_shapes):
        errors.append('scores+values bundle missing required arrays')
    qkv_shapes = shapes.get('qkv', {})
    if not {'q', 'k', 'v'}.issubset(qkv_shapes):
        errors.append('qkv bundle missing required arrays')
    if sv_shapes and sv_shapes.get('scores', [None, None])[0] != sv_shapes.get('values', [None])[0]:
        errors.append('scores+values row dimension mismatch')
    if qkv_shapes and qkv_shapes.get('q', [None])[0] != qkv_shapes.get('k', [None])[0]:
        errors.append('qkv row dimension mismatch')

    for name, chk in [('scores_values_gate', sv_gate), ('qkv_gate', qkv_gate)]:
        if chk.get('trace_gate_status') != 'external_npz_loaded_claims_public_pretrained_false':
            errors.append(f'{name} did not use non-public external status')
        if chk.get('external_trace_loaded') is not True:
            errors.append(f'{name} did not mark external_trace_loaded')
        if chk.get('public_pretrained_trace_loaded') is not False:
            errors.append(f'{name} incorrectly claims public/pretrained trace loaded')
        if chk.get('row_public_true_count', 1) != 0:
            errors.append(f'{name} has row-level public/pretrained leakage')
        if chk.get('row_external_true_count', 0) <= 0:
            errors.append(f'{name} has no row-level external trace label')
        if chk.get('oracle_leakage_rows', 0) != 0:
            errors.append(f'{name} has selector oracle leakage rows')
    if default_gate.get('external_trace_loaded') is not False or default_gate.get('public_pretrained_trace_loaded') is not False:
        errors.append('default surrogate gate should not be external or public/pretrained')
    if default_gate.get('trace_gate_status') != 'surrogate_only_importer_ready_public_pretrained_missing':
        errors.append('default surrogate gate has wrong status')

    gate_src = (ROOT / 'experiments' / 'public_trace_gate_surrogate' / 'public_trace_gate_surrogate.py').read_text(encoding='utf-8')
    cap_src_path = ROOT / 'experiments' / 'public_trace_capture' / 'hf_attention_trace_capture.py'
    cap_src = cap_src_path.read_text(encoding='utf-8') if cap_src_path.exists() else ''
    source_contracts = {
        'external_and_public_flags_separated': 'external_trace_loaded' in gate_src and 'public_loaded = bool(external_loaded and public_pretrained_trace)' in gate_src,
        'old_external_equals_public_bug_absent': '"public_pretrained_trace_loaded": bool(external_loaded)' not in gate_src,
        'non_public_external_status_present': 'external_npz_loaded_claims_public_pretrained_false' in gate_src,
        'capture_helper_local_first': 'local_files_only=local_only' in cap_src and '--allow-download' in cap_src,
        'capture_helper_writes_qkv_npz': re.search(r'np\.savez_compressed\([^\)]*q=q[^\)]*k=k[^\)]*v=v', cap_src, re.S) is not None,
        'capture_helper_warns_about_public_flag': '--public-pretrained-trace' in cap_src or 'public-pretrained' in cap_src,
    }
    for k, ok in source_contracts.items():
        if not ok:
            errors.append('missing source contract: ' + k)

    report = {
        'project': 'CloudtainerML',
        'revision': REV,
        'report': 'trace_capture_roundtrip_audit',
        'status': 'pass' if not errors else 'fail',
        'promotion_allowed': False,
        'roundtrip_artifact': roundtrip_rel,
        'default_gate_check': default_gate,
        'scores_values_gate_check': sv_gate,
        'qkv_gate_check': qkv_gate,
        'bundle_shapes': shapes,
        'source_contracts': source_contracts,
        'errors': errors,
        'warnings': warnings,
        'interpretation': 'rev0049 exercises the external NPZ importer on actual scores+values and q/k/v bundles, and fixes the claims boundary so external trace loading is not automatically public/pretrained evidence.',
    }
    (OUT / f'{REVUP}_TRACE_CAPTURE_ROUNDTRIP_AUDIT.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    md = [f'# Trace capture roundtrip audit — {REV}', '', f'**Status: {report["status"]}**', '', '## Claim boundary', '', f'- default gate status: `{default_gate.get("trace_gate_status")}`', f'- scores+values external status: `{sv_gate.get("trace_gate_status")}`', f'- q/k/v external status: `{qkv_gate.get("trace_gate_status")}`', f'- external bundles claim public/pretrained: `{sv_gate.get("public_pretrained_trace_loaded")}` / `{qkv_gate.get("public_pretrained_trace_loaded")}`', '', '## Bundle shapes', '', f'- scores+values: `{shapes.get("scores_values")}`', f'- q/k/v: `{shapes.get("qkv")}`', '', '## Interpretation', '', report['interpretation']]
    if warnings:
        md += ['', '## Warnings', *[f'- {w}' for w in warnings]]
    if errors:
        md += ['', '## Errors', *[f'- {e}' for e in errors]]
    (OUT / f'{REVUP}_TRACE_CAPTURE_ROUNDTRIP_AUDIT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'errors': len(errors), 'default_status': default_gate.get('trace_gate_status'), 'sv_status': sv_gate.get('trace_gate_status'), 'qkv_status': qkv_gate.get('trace_gate_status')}, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
