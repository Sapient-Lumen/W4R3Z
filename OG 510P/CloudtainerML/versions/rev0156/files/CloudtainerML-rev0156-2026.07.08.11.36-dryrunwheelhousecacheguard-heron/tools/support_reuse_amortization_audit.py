#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = META.get('revision', 'rev0066')
REVUP = REV.upper()
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)
ART_REL = f'artifacts/probe-results/{REVUP}_SUPPORT_REUSE_AMORTIZATION.json'
MAN_REL = f'artifacts/run-manifests/{REVUP}_SUPPORT_REUSE_AMORTIZATION_RUN_MANIFEST.json'
INPUT_REL = f'artifacts/native-inputs/{REVUP}_SUPPORT_REUSE_AMORTIZATION_INPUT.bin'
PY_REL = 'experiments/trace_packet_support_reuse/trace_packet_support_reuse.py'
CPP_REL = 'experiments/trace_packet_support_reuse/trace_packet_support_reuse.cpp'


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    for rel in [ART_REL, MAN_REL, INPUT_REL, PY_REL, CPP_REL]:
        if not (ROOT / rel).exists():
            errors.append('missing required file: ' + rel)
    art = load(ART_REL) if (ROOT / ART_REL).exists() else {}
    man = load(MAN_REL) if (ROOT / MAN_REL).exists() else {}
    s = art.get('summary', {}) if art else {}
    native = art.get('native_result', {}) if art else {}
    acct = native.get('accounting', {}) if native else {}
    paths = native.get('all_rows', {}) if native else {}
    if art:
        if art.get('revision') != REV:
            errors.append('artifact revision mismatch')
        if art.get('promotion_allowed') is not False or s.get('promotion_allowed') is not False:
            errors.append('artifact overclaims promotion')
        if art.get('public_pretrained_trace_loaded') is not False or s.get('public_pretrained_trace_loaded') is not False:
            errors.append('artifact overclaims public/pretrained evidence')
        if art.get('gpu_fused_kernel_measured') is not False or s.get('gpu_fused_kernel_measured') is not False:
            errors.append('artifact overclaims GPU/fused evidence')
        if s.get('support_reuse_overhead_paid_in_timed_loop') is not True or acct.get('support_reuse_overhead_paid_in_timed_loop') is not True:
            errors.append('support reuse overhead must be paid in timed loop')
        if s.get('support_reuse_does_not_use_values_or_dense_outputs') is not True:
            errors.append('support reuse must be score-only')
        if acct.get('selectors_use_values') is not False or acct.get('selectors_use_dense_outputs') is not False:
            errors.append('native accounting reports selector oracle leakage')
        if s.get('deployable_promoted_paths') not in ([], None):
            errors.append('no support reuse path may be promoted')
        if float(s.get('fresh_hist_quality_rate', 0.0)) < 0.99:
            errors.append('fresh histogram baseline quality should pass')
        if float(s.get('reuse_example_anchor_qk_dot_fraction', 1.0)) >= 0.95:
            errors.append('example-anchor reuse did not actually reduce QK work')
        if float(s.get('reuse_example_anchor_quality_rate', 1.0)) >= 0.95:
            errors.append('expected anchor-reuse quality failure not exposed')
        if float(s.get('reuse_example_head_anchor_quality_rate', 1.0)) >= 0.95:
            errors.append('expected example/head anchor-reuse quality failure not exposed')
        if float(s.get('reuse_example_anchor_jaccard_mean', 1.0)) >= 0.8:
            errors.append('support stability unexpectedly high; audit assumptions need review')
        if float(s.get('union_example_hist_quality_rate', 0.0)) < 0.99:
            errors.append('union upper-bound should restore quality')
        if float(s.get('union_example_hist_mean_selected_fraction', 0.0)) < 0.95:
            errors.append('union support did not expose near-dense repair')
        if acct.get('union_support_non_promotional_upper_bound') is not True or acct.get('union_support_uses_all_group_rows') is not True:
            errors.append('union support must be marked non-promotional all-row upper bound')
        if float(s.get('union_example_hist_qk_dot_fraction', 0.0)) < 0.95:
            errors.append('union support should not be claimed as score sparse')
        scope = str(art.get('measurement_scope', '')).lower()
        for phrase in ['support construction/reuse overhead is paid', 'anchor reuse is score-only', 'union support is an all-row upper-bound', 'not public/pretrained', 'not gpu', 'not fused']:
            if phrase not in scope:
                errors.append('measurement scope missing phrase: ' + phrase)
        blockers = set(s.get('remaining_blockers', []))
        for b in ['actual_public_pretrained_trace_bundle_missing','gpu_fused_attention_kernel_timing_missing','support_reuse_anchor_quality_below_bar','support_union_restores_quality_by_becoming_near_dense','row_stability_certificate_missing','no_deployable_score_path_sparse_win_measured']:
            if b not in blockers:
                errors.append('missing blocker: ' + b)
        if float(s.get('reuse_example_anchor_speedup_vs_dense', 0.0)) > 1.0 and float(s.get('reuse_example_anchor_quality_rate', 0.0)) < 0.95:
            warnings.append('example-anchor reuse is faster but invalid because quality fails')
        if float(s.get('union_example_hist_speedup_vs_dense', 1.0)) < 1.0:
            warnings.append('union support restores quality only with near-dense/slower support')
        for key in ['fresh_hist_index','reuse_example_anchor_hist','reuse_example_head_anchor_hist','union_example_hist_upper_bound']:
            if key not in paths:
                errors.append('missing path metrics: ' + key)
    if man:
        if man.get('artifact_sha256') != sha256_file(ROOT / ART_REL):
            errors.append('run manifest artifact hash mismatch')
        if man.get('python_source_sha256') != sha256_file(ROOT / PY_REL):
            errors.append('run manifest python source hash mismatch')
        if man.get('source_sha256') != sha256_file(ROOT / CPP_REL):
            errors.append('run manifest C++ source hash mismatch')
        if man.get('native_input_sha256') != sha256_file(ROOT / INPUT_REL):
            errors.append('run manifest native input hash mismatch')
        boundary = str(man.get('claim_boundary', '')).lower()
        for phrase in ['support reuse amortization is paid', 'score-only', 'union support is a non-promotional', 'not public/pretrained', 'not gpu']:
            if phrase not in boundary:
                errors.append('manifest claim boundary missing phrase: ' + phrase)
    cpp = (ROOT / CPP_REL).read_text(encoding='utf-8') if (ROOT / CPP_REL).exists() else ''
    for token in ['CTMLTR66', 'histogram_mass_select', 'sparse_from_selected_qk_only', 'union_support_non_promotional_upper_bound', 'reuse_example_anchor_qk_dot_fraction']:
        if token not in cpp:
            errors.append('native source missing expected token: ' + token)
    py = (ROOT / PY_REL).read_text(encoding='utf-8') if (ROOT / PY_REL).exists() else ''
    for forbidden in ['public_pretrained_trace_loaded": True', 'gpu_fused_kernel_measured": True', 'promotion_allowed = True']:
        if forbidden in py:
            errors.append('source contains forbidden promotion literal: ' + forbidden)
    report = {
        'project': 'CloudtainerML',
        'revision': REV,
        'report': 'support_reuse_amortization_audit',
        'status': 'pass' if not errors else 'fail',
        'promotion_allowed': False,
        'artifact': ART_REL,
        'key_metrics': {
            'fresh_hist_quality_rate': s.get('fresh_hist_quality_rate'),
            'fresh_hist_speedup_vs_dense': s.get('fresh_hist_speedup_vs_dense'),
            'reuse_example_anchor_quality_rate': s.get('reuse_example_anchor_quality_rate'),
            'reuse_example_anchor_qk_dot_fraction': s.get('reuse_example_anchor_qk_dot_fraction'),
            'reuse_example_anchor_speedup_vs_dense': s.get('reuse_example_anchor_speedup_vs_dense'),
            'reuse_example_anchor_jaccard_mean': s.get('reuse_example_anchor_jaccard_mean'),
            'reuse_example_head_anchor_quality_rate': s.get('reuse_example_head_anchor_quality_rate'),
            'union_example_hist_quality_rate': s.get('union_example_hist_quality_rate'),
            'union_example_hist_mean_selected_fraction': s.get('union_example_hist_mean_selected_fraction'),
        },
        'errors': errors,
        'warnings': warnings,
        'interpretation': 'rev0066 tests whether support reuse can amortize selector/layout overhead. Anchor reuse saves QK work but fails quality; union support restores quality only by becoming near-dense, so reuse remains non-promotional.',
    }
    (OUT / f'{REVUP}_SUPPORT_REUSE_AMORTIZATION_AUDIT.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    md = [f'# Support reuse amortization audit — {REV}', '', f'**Status: {report["status"]}**', '', report['interpretation'], '', '## Key metrics']
    for k, v in report['key_metrics'].items():
        md.append(f'- {k}: `{v}`')
    if warnings:
        md += ['', '## Warnings', *[f'- {w}' for w in warnings]]
    if errors:
        md += ['', '## Errors', *[f'- {e}' for e in errors]]
    (OUT / f'{REVUP}_SUPPORT_REUSE_AMORTIZATION_AUDIT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'errors': len(errors), 'warnings': len(warnings), 'anchor_quality': s.get('reuse_example_anchor_quality_rate')}, indent=2))
    return 0 if not errors else 1

if __name__ == '__main__':
    raise SystemExit(main())
