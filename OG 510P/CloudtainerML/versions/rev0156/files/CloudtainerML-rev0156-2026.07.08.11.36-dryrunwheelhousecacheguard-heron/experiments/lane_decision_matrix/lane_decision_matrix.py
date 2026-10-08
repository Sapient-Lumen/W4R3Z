#!/usr/bin/env python3
"""rev0072 lane decision matrix.

This is a waste-prevention artifact, not a doctrine expansion. It turns recent
measured results into stop/continue decisions so the cube stops spending turns on
lanes that have become safe-but-slower or fast-but-invalid on the local trace.
"""
from __future__ import annotations
import hashlib, json, platform
from pathlib import Path
from typing import Any
ROOT = Path(__file__).resolve().parents[2]
META = json.loads((ROOT/'CUBE-META.json').read_text(encoding='utf-8'))
REV = META.get('revision','rev0072'); REVUP = REV.upper(); STAMP='2026-06-18T17:18:00-04:00'
OUT = ROOT/'artifacts'/'probe-results'/f'{REVUP}_LANE_DECISION_MATRIX.json'
MAN = ROOT/'artifacts'/'run-manifests'/f'{REVUP}_LANE_DECISION_MATRIX_RUN_MANIFEST.json'

def sha256_file(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda:f.read(1<<20), b''): h.update(c)
    return h.hexdigest()

def load_rel(rel: str) -> dict[str, Any]:
    p = ROOT/rel
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}

def f(x, default=None):
    try: return float(x)
    except Exception: return default

def main() -> int:
    # Pull only the handful of recent artifacts needed to avoid repeating dead-end work.
    a65 = load_rel('artifacts/probe-results/REV0065_DEPLOYABLE_SELECTOR_LAYOUT_OVERHEAD.json').get('summary',{})
    a66 = load_rel('artifacts/probe-results/REV0066_SUPPORT_REUSE_AMORTIZATION.json').get('summary',{})
    a68 = load_rel('artifacts/probe-results/REV0068_BOUNDARY_REFINED_SELECTOR_LAYOUT.json').get('summary',{})
    a69 = load_rel('artifacts/probe-results/REV0069_CERTIFIED_SUPPORT_REUSE.json').get('summary',{})
    a70 = load_rel('artifacts/probe-results/REV0070_TWOSTAGE_CERTIFIED_SUPPORT_REUSE.json').get('summary',{})
    a71 = load_rel('artifacts/probe-results/REV0071_STAGE_PRUNED_CERT_REUSE_POLICY.json').get('summary',{})
    claim = load_rel(f'artifacts/probe-results/{REVUP}_PUBLIC_TRACE_CLAIM_CONTRACT.json').get('summary',{})
    decisions = []
    def add(lane, decision, confidence, evidence, next_condition, risk):
        decisions.append({'lane': lane, 'decision': decision, 'confidence': confidence, 'evidence': evidence, 'resume_or_promote_only_if': next_condition, 'risk_if_ignored': risk})
    add('raw_anchor_support_reuse', 'retire_invalid_fast_path', 'high', {
        'rev0066_anchor_quality_rate': a66.get('reuse_example_anchor_quality_rate'),
        'rev0066_anchor_speedup_vs_dense': a66.get('reuse_example_anchor_speedup_vs_dense'),
        'rev0071_raw_anchor_quality_rate': a71.get('raw_anchor_quality_rate'),
        'rev0071_raw_anchor_speedup_vs_dense': a71.get('raw_anchor_speedup_vs_dense'),
    }, 'never; only certified reuse can be considered', 'fast but invalid reuse would corrupt attention output')
    add('certified_support_reuse', 'pause_until_stronger_row_stability_signal', 'medium_high', {
        'rev0069_certified_quality_rate': a69.get('certified_quality_rate') or a69.get('safe_certified_quality_rate'),
        'rev0070_two_stage_speedup_vs_dense': a70.get('two_stage_speedup_vs_dense'),
        'rev0071_scalar_only_speedup_vs_dense': a71.get('scalar_only_speedup_vs_dense'),
        'rev0071_fresh_hist_speedup_vs_dense': a71.get('fresh_hist_speedup_vs_dense'),
        'rev0071_scalar_only_sidecar_read_fraction': a71.get('scalar_only_sidecar_read_fraction'),
    }, 'public/pretrained traces show much higher certified reuse rate and measured speedup > fresh histogram after all certificate work is paid', 'safe-but-slower certificate consumes revisions without addressing public/GPU blockers')
    add('boundary_refined_selector', 'retire_as_cpu_deployable_path_keep_as_oracle_gap_diagnostic', 'high', {
        'rev0068_boundary_quality_rate': a68.get('boundary_refined_quality_rate'),
        'rev0068_boundary_speedup_vs_dense': a68.get('boundary_refined_speedup_vs_dense'),
        'rev0068_exact_sort_speedup_vs_dense': a68.get('exact_sort_speedup_vs_dense'),
    }, 'new platform/kernel makes boundary refine faster than dense with QK and layout construction paid', 'keeps optimizing a selector that fixes over-selection but remains slower than dense')
    add('deployable_score_only_selector_layout', 'pause_on_local_cpu_trace', 'high', {
        'rev0065_hist_quality_rate': a65.get('histogram_quality_rate'),
        'rev0065_hist_index_speedup_vs_dense': a65.get('histogram_index_speedup_vs_dense'),
        'rev0065_exact_sort_index_speedup_vs_dense': a65.get('exact_sort_index_speedup_vs_dense'),
        'rev0065_qk_fraction': a65.get('qk_dot_fraction_vs_dense'),
    }, 'public/pretrained trace or GPU fused path demonstrates speedup with QK, selector, layout, and quality all paid', 'mistakes value-read savings for end-to-end speed')
    add('public_pretrained_trace_capture', 'continue_highest_priority', 'high', {
        'rev0072_public_claim_requires_manifest': claim.get('public_claim_requires_provenance_manifest'),
        'rev0072_fixture_rejected_without_manifest': claim.get('public_claim_rejected_without_manifest'),
        'rev0072_fixture_rejected_with_manifest': claim.get('public_claim_rejected_with_fixture_manifest'),
        'public_pretrained_trace_blocker_remains': claim.get('public_pretrained_trace_blocker_remains'),
    }, 'valid provenance manifest plus public/pretrained Q/K/V or scores/values bundle is captured and replayed through native QK/dispatch audits', 'local tiny-trace conclusions may not transfer')
    add('gpu_or_fused_kernel_path', 'continue_when_hardware_or_kernel_toolchain_available', 'medium', {
        'reason': 'strict materialization-free gates promote zero regimes on CPU; GPU/fused timing remains unmeasured',
    }, 'named hardware run measures dense vs sparse fused kernels with score storage/recompute explicitly accounted', 'CPU proxy results can mis-rank QK/value/layout costs')
    add('observable_low_support_block_bounds', 'conditional_watch_not_primary', 'medium', {
        'reason': 'learned-trace low-support rows had some QK pruning, but broad/high-support rows erased advantage and public traces are missing',
    }, 'public/pretrained traces show many low-support rows with tight observable key bounds and native/GPU speedup', 'overfits to local trace geometry')
    retired = [d['lane'] for d in decisions if d['decision'].startswith('retire') or d['decision'].startswith('pause')]
    priority_queue = [
        {'rank': 1, 'work_item': 'capture_or_import_public_pretrained_trace_bundle_with_manifest', 'why': 'largest remaining scientific transfer blocker'},
        {'rank': 2, 'work_item': 'native_replay_public_trace_bundle_through_qk_dispatch_and_value_layout_audits', 'why': 'turn public trace into comparable measured evidence'},
        {'rank': 3, 'work_item': 'gpu_fused_kernel_or_named_hardware_timing_harness', 'why': 'remaining systems blocker after CPU negatives'},
    ]
    summary = {
        'lanes_retired_or_paused_count': len(retired),
        'retired_or_paused_lanes': retired,
        'highest_priority_lane': 'public_pretrained_trace_capture',
        'support_reuse_should_not_be_next_default': True,
        'public_trace_claim_gate_hardened': bool(claim.get('public_claim_requires_provenance_manifest')),
        'promotion_allowed': False,
        'deployable_promoted_paths': [],
    }
    artifact = {
        'project':'CloudtainerML','revision':REV,'artifact':f'{REVUP}_LANE_DECISION_MATRIX','generated_at':STAMP,
        'measurement_scope':'machine-readable stop/continue decisions derived from recent measured artifacts; prevents spending more revisions on invalid-fast or safe-slow lanes; not a promotion artifact',
        'summary': summary, 'decisions': decisions, 'priority_queue': priority_queue,
        'promotion_allowed': False, 'public_pretrained_trace_loaded': False, 'gpu_fused_kernel_measured': False,
        'interpretation': 'The cube should stop defaulting to support-reuse and boundary-refinement work. The next scarce-effort path is real public/pretrained trace capture and native replay, followed by named hardware/fused-kernel timing.',
    }
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(artifact, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    man = {'project':'CloudtainerML','revision':REV,'artifact':OUT.relative_to(ROOT).as_posix(),'generated_at':STAMP,'command':'python experiments/lane_decision_matrix/lane_decision_matrix.py','python_version':platform.python_version(),'platform':platform.platform(),'source_files':{str(Path(__file__).relative_to(ROOT)):sha256_file(Path(__file__))},'artifact_sha256':sha256_file(OUT),'promotion_allowed':False}
    MAN.parent.mkdir(parents=True, exist_ok=True); MAN.write_text(json.dumps(man, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    print(json.dumps({'status':'pass','summary':summary}, indent=2))
    return 0
if __name__=='__main__': raise SystemExit(main())
