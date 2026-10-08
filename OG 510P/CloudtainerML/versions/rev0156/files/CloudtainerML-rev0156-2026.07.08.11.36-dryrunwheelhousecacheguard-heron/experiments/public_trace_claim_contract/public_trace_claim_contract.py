#!/usr/bin/env python3
"""Frozen historical rev0072 public-trace claim contract probe.

This is not another surrogate attention result. It hardens the riskiest open
blocker: an external NPZ trace must not become "public/pretrained evidence" by
operator flag alone. rev0072 builds a local fixture bundle and verifies that the
public/pretrained claim is rejected without a valid provenance manifest and is
also rejected with a manifest that reveals fixture/surrogate origin.
"""
from __future__ import annotations
import hashlib, importlib.util, json, platform, sys
from pathlib import Path
from typing import Any
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HISTORICAL_RUNNER = True
ORIGINAL_REV = 'rev0072'
REV = ORIGINAL_REV
REVUP = REV.upper()
STAMP = '2026-06-18T17:18:00-04:00'
OUT = ROOT/'artifacts'/'probe-results'/f'{REVUP}_PUBLIC_TRACE_CLAIM_CONTRACT.json'
MAN = ROOT/'artifacts'/'run-manifests'/f'{REVUP}_PUBLIC_TRACE_CLAIM_CONTRACT_RUN_MANIFEST.json'
FIX = ROOT/'artifacts'/'trace-bundles'/f'{REVUP}_TRACE_CLAIM_FIXTURE_QKV.npz'
BADPROV = ROOT/'artifacts'/'trace-bundles'/f'{REVUP}_TRACE_CLAIM_FIXTURE_BAD_PROVENANCE.json'
SCRIPT = ROOT/'experiments'/'public_trace_gate_surrogate'/'public_trace_gate_surrogate.py'

def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for c in iter(lambda:f.read(1<<20), b''): h.update(c)
    return h.hexdigest()

def load_gate_module():
    spec = importlib.util.spec_from_file_location('public_trace_gate_surrogate_rev0072', SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError('could not load public trace gate script')
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod

def make_fixture() -> dict[str, Any]:
    candidates = sorted((ROOT/'artifacts'/'trace-bundles').glob('REV*_TINY_TRAINED_QK_TRACE_PACKET.npz'), reverse=True)
    if not candidates:
        raise FileNotFoundError('no local Q/K/V trace packet available')
    src = candidates[0]
    z = np.load(src)
    if {'q','k','v'}.issubset(set(z.files)):
        q = np.asarray(z['q'], dtype=np.float64)
        k = np.asarray(z['k'], dtype=np.float64)
        v = np.asarray(z['v'], dtype=np.float64)
    else:
        q = np.asarray(z['queries'], dtype=np.float64)
        k = np.asarray(z['keys'], dtype=np.float64)
        v = np.asarray(z['values'], dtype=np.float64)
    # Keep the fixture small enough for the slim capsule, while preserving the
    # actual learned local trace distribution used by the replay lane.
    limit = min(64, q.shape[0])
    meta = {}
    for name in ['regime','layer','head','position','example','trace_batch']:
        if name in z.files:
            meta[name] = z[name][:limit]
    FIX.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(FIX, q=q[:limit], k=k[:limit], v=v[:limit], **meta)
    bad = {
        'trace_claim_version': 'public_trace_claim_v1',
        'public_pretrained_trace': False,
        'source_type': 'local_fixture_from_tiny_trained_trace',
        'model_id': 'local_tiny_transformer_fixture_not_public',
        'weights_source': 'local synthetic training run',
        'license': 'not applicable; fixture only',
        'trace_npz_sha256': sha256_file(FIX),
        'schema': 'qkv_npz_v1',
        'capture_tool': 'experiments/public_trace_claim_contract/public_trace_claim_contract.py',
        'capture_tool_sha256': sha256_file(Path(__file__)),
        'generated_from_local_tiny_model': True,
        'uses_random_weights': False,
        'provenance_reviewed': True,
        'why_rejected': 'The fixture is external-NPZ compatible but not public/pretrained evidence.',
    }
    BADPROV.write_text(json.dumps(bad, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    return {
        'source_trace_packet': src.relative_to(ROOT).as_posix(),
        'source_trace_packet_sha256': sha256_file(src),
        'fixture_npz': FIX.relative_to(ROOT).as_posix(),
        'fixture_npz_sha256': sha256_file(FIX),
        'bad_provenance_json': BADPROV.relative_to(ROOT).as_posix(),
        'bad_provenance_sha256': sha256_file(BADPROV),
        'rows': int(limit), 'n_tokens': int(k.shape[1]), 'd_key': int(q.shape[-1]), 'd_value': int(v.shape[-1]),
    }

def compact_case(payload: dict[str, Any]) -> dict[str, Any]:
    decl = payload.get('external_trace_declaration', {})
    ps = decl.get('provenance_status', {})
    summ = payload.get('summary', {})
    return {
        'trace_gate_status': payload.get('trace_gate_status'),
        'external_trace_loaded': payload.get('external_trace_loaded'),
        'public_pretrained_trace_loaded': payload.get('public_pretrained_trace_loaded'),
        'accepted_as_public_pretrained_trace': decl.get('accepted_as_public_pretrained_trace'),
        'provenance_status': ps.get('status'),
        'provenance_errors': ps.get('errors', []),
        'trace_row_count': summ.get('trace_row_count'),
        'result_row_count': summ.get('result_row_count'),
        'oracle_leakage_rows': summ.get('oracle_leakage_rows'),
        'trace_source_types': summ.get('trace_source_types'),
    }

def main() -> int:
    gate = load_gate_module()
    fixture = make_fixture()
    no_manifest = gate.run(FIX, public_pretrained_trace=True, trace_source_label='rev0072_fixture_no_manifest', bundle_model_id='local_fixture', bundle_license='not_public_fixture', provenance_json=None)
    bad_manifest = gate.run(FIX, public_pretrained_trace=True, trace_source_label='rev0072_fixture_bad_manifest', bundle_model_id='local_fixture', bundle_license='not_public_fixture', provenance_json=BADPROV)
    control = gate.run(FIX, public_pretrained_trace=False, trace_source_label='rev0072_fixture_schema_only', bundle_model_id='local_fixture', bundle_license='not_public_fixture', provenance_json=None)
    c0, c1, c2 = compact_case(no_manifest), compact_case(bad_manifest), compact_case(control)
    summary = {
        'public_claim_requires_provenance_manifest': True,
        'public_claim_rejected_without_manifest': c0['public_pretrained_trace_loaded'] is False and 'rejected' in str(c0['trace_gate_status']),
        'public_claim_rejected_with_fixture_manifest': c1['public_pretrained_trace_loaded'] is False and c1['provenance_status'] == 'public_pretrained_claim_rejected',
        'schema_only_external_trace_loaded': c2['external_trace_loaded'] is True,
        'schema_only_external_trace_not_public': c2['public_pretrained_trace_loaded'] is False,
        'oracle_leakage_rows_total': sum(int(c.get('oracle_leakage_rows') or 0) for c in [c0,c1,c2]),
        'public_pretrained_trace_loaded': False,
        'promotion_allowed': False,
        'public_pretrained_trace_blocker_remains': True,
        'next_substantive_step': 'run HF/TransformerLens capture on an actual public pretrained model and provide a valid provenance manifest; then replay dispatch/native QK evidence on that bundle',
    }
    artifact = {
        'project':'CloudtainerML', 'revision': REV, 'artifact': f'{REVUP}_PUBLIC_TRACE_CLAIM_CONTRACT', 'generated_at': STAMP,
        'measurement_scope': 'claim-contract hardening for external trace ingestion; fixture is local tiny-trace derived and must not be promoted as public/pretrained; no GPU/fused timing; no public/pretrained evidence claimed',
        'trace_fixture': fixture,
        'cases': {'flag_only_no_manifest': c0, 'bad_fixture_provenance': c1, 'schema_only_control': c2},
        'summary': summary,
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
        'interpretation': 'rev0072 closes the public-trace flag loophole: schema-valid external NPZ bundles are not public/pretrained evidence unless a provenance manifest proves that status. The local fixture is deliberately rejected.',
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    manifest = {
        'project':'CloudtainerML','revision':REV,'artifact':OUT.relative_to(ROOT).as_posix(),'generated_at':STAMP,
        'command':'python experiments/public_trace_claim_contract/public_trace_claim_contract.py',
        'python_version': platform.python_version(), 'platform': platform.platform(),
        'source_files': {str(Path(__file__).relative_to(ROOT)): sha256_file(Path(__file__)), str(SCRIPT.relative_to(ROOT)): sha256_file(SCRIPT)},
        'inputs': {fixture['source_trace_packet']: fixture['source_trace_packet_sha256'], fixture['fixture_npz']: fixture['fixture_npz_sha256'], fixture['bad_provenance_json']: fixture['bad_provenance_sha256']},
        'artifact_sha256': sha256_file(OUT), 'promotion_allowed': False,
    }
    MAN.parent.mkdir(parents=True, exist_ok=True)
    MAN.write_text(json.dumps(manifest, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    print(json.dumps({'status':'pass', 'summary': summary}, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
