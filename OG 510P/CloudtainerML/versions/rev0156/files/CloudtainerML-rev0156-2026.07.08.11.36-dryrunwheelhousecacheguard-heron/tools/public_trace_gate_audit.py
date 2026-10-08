#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = META.get('revision', 'rev0049')
REVUP = REV.upper()
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)
ART_REL = f'artifacts/probe-results/{REVUP}_PUBLIC_TRACE_GATE_SURROGATE.json'


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


def load_json(rel: str) -> Any:
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    p = ROOT / ART_REL
    if not p.exists():
        errors.append('missing public trace gate artifact')
        payload: dict[str, Any] = {}
    else:
        payload = load_json(ART_REL)
    rows = payload.get('rows', [])
    summary = payload.get('summary', {})
    risk = summary.get('risk_surface', {})
    ds = summary.get('dataset_summary', {})
    methods = sorted({r.get('method') for r in rows})
    regimes = sorted({r.get('regime') for r in rows})
    trace_source_types = sorted({r.get('trace_source_type') for r in rows})
    required_methods = {
        'full_dense',
        'exact_topk_16',
        'mass_histogram_0p95_bins32',
        'value_norm_exception_mass_0p95_bins32',
    }
    missing_methods = sorted(required_methods - set(methods))
    if missing_methods:
        errors.append('missing required methods: ' + ', '.join(missing_methods))
    required_regimes = {
        'retrieval_peaked', 'local_window', 'sink_plus_local', 'multi_peak_induction',
        'broad_high_entropy', 'value_tail_outlier'
    }
    missing_regimes = sorted(required_regimes - set(regimes))
    if missing_regimes:
        errors.append('missing surrogate regimes: ' + ', '.join(missing_regimes))
    if payload.get('kind') != 'offline_attention_trace_importer_and_surrogate_suite':
        errors.append('wrong artifact kind')
    if payload.get('trace_gate_status') != 'surrogate_only_importer_ready_public_pretrained_missing':
        errors.append('default trace gate status does not honestly say public/pretrained traces are missing')
    if payload.get('external_trace_loaded') is not False:
        errors.append('default surrogate run must not claim an external trace was loaded')
    if payload.get('public_pretrained_trace_loaded') is not False:
        errors.append('default run must not claim public/pretrained traces were loaded')
    if payload.get('promotion_allowed') is not False:
        errors.append('artifact must not allow promotion')
    schema = payload.get('external_trace_schema') or {}
    if not schema.get('npz_scores_values') or not schema.get('npz_qkv'):
        errors.append('external NPZ trace schema missing or incomplete')
    leaks = [r for r in rows if r.get('selection_oracle_leakage_detected') or r.get('selection_uses_values') or r.get('selection_uses_dense_output')]
    if leaks:
        errors.append(f'selection oracle leakage detected in {len(leaks)} rows')
    cert_errors = [float(r.get('certificate_error_abs') or 0.0) for r in rows if r.get('certified_mass_from_scores') is not None]
    if cert_errors and max(cert_errors) > 1e-9:
        errors.append('score mass certificate mismatch exceeds tolerance')
    if float(risk.get('broad_mass_hist_selected_fraction', 0.0)) < 0.90:
        errors.append('broad_high_entropy does not force near-dense mass-histogram value reads')
    if float(risk.get('tail_mass_hist_quality_rate', 1.0)) > 0.20:
        errors.append('value_tail_outlier does not expose mass-only output-quality failure')
    if float(risk.get('tail_value_norm_exception_quality_rate', 0.0)) < 0.90:
        errors.append('value-norm exception does not repair value-tail quality')
    if float(risk.get('retrieval_mass_hist_selected_fraction', 1.0)) > 0.70:
        warnings.append('retrieval surrogate is less sparse than desired; still usable as a conservative trace gate')
    # Source/refactor checks.
    src = ROOT / 'experiments' / 'public_trace_gate_surrogate' / 'public_trace_gate_surrogate.py'
    core = ROOT / 'experiments' / 'attention_compiler_core' / 'attention_core.py'
    if 'guarded_mass_aware_compiler_points_for_row' not in core.read_text(encoding='utf-8'):
        errors.append('attention core refactor helper missing')
    text = src.read_text(encoding='utf-8') if src.exists() else ''
    for pat, label in [
        (r'def\s+iter_npz_rows', 'NPZ importer'),
        (r'surrogate_public_like_offline', 'surrogate source labeling'),
        (r'external_trace_loaded', 'external trace flag'),
        (r'public_loaded = bool\(external_loaded and public_pretrained_trace\)', 'separate external/public-pretrained claim boundary'),
        (r'public_pretrained_trace_loaded', 'public/pretrained flag'),
        (r'selection_oracle_leakage_detected', 'oracle leakage row flag'),
    ]:
        if not re.search(pat, text):
            errors.append(f'missing source contract: {label}')
    if '"public_pretrained_trace_loaded": bool(external_loaded)' in text:
        errors.append('old external-equals-public/pretrained bug is still present')
    rp = payload.get('run_provenance', {})
    source_rel = rp.get('source_path')
    source_hash_ok = None
    if source_rel and (ROOT / source_rel).exists() and rp.get('source_sha256'):
        source_hash_ok = sha256_file(ROOT / source_rel) == rp.get('source_sha256')
        if not source_hash_ok:
            errors.append('source hash mismatch for public trace gate artifact')
    else:
        errors.append('run provenance missing source path/hash')
    report = {
        'project': 'CloudtainerML',
        'revision': REV,
        'report': 'public_trace_gate_audit',
        'status': 'pass' if not errors else 'fail',
        'promotion_allowed': False,
        'artifact': ART_REL,
        'trace_gate_status': payload.get('trace_gate_status'),
        'external_trace_loaded': payload.get('external_trace_loaded'),
        'public_pretrained_trace_loaded': payload.get('public_pretrained_trace_loaded'),
        'trace_source_types': trace_source_types,
        'regimes': regimes,
        'methods': methods,
        'row_count': len(rows),
        'trace_row_count': summary.get('trace_row_count'),
        'risk_surface': risk,
        'source_hash_ok': source_hash_ok,
        'oracle_leakage_rows': len(leaks),
        'max_certificate_error_abs': max(cert_errors) if cert_errors else None,
        'dataset_summary_keys': sorted(ds.keys()),
        'errors': errors,
        'warnings': warnings,
        'interpretation': 'rev0049 keeps the default trace gate surrogate-only, and verifies that the public/pretrained flag is separated from arbitrary external NPZ loading. It still does not close the public/pretrained trace blocker.',
    }
    (OUT / f'{REVUP}_PUBLIC_TRACE_GATE_AUDIT.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    md = [f'# Public/pretrained trace gate audit — {REV}', '', f'**Status: {report["status"]}**', '', f'- artifact: `{ART_REL}`', f'- trace gate status: `{report["trace_gate_status"]}`', f'- external trace loaded: `{report["external_trace_loaded"]}`', f'- public/pretrained trace loaded: `{report["public_pretrained_trace_loaded"]}`', f'- trace rows: {report["trace_row_count"]}', f'- result rows: {report["row_count"]}', f'- oracle leakage rows: {report["oracle_leakage_rows"]}', '']
    md += ['## Risk surface', '']
    for k, v in risk.items():
        md.append(f'- {k}: {v}')
    md += ['', '## Interpretation', '', report['interpretation']]
    if warnings:
        md += ['', '## Warnings', *[f'- {w}' for w in warnings]]
    if errors:
        md += ['', '## Errors', *[f'- {e}' for e in errors]]
    (OUT / f'{REVUP}_PUBLIC_TRACE_GATE_AUDIT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'errors': len(errors), 'warnings': len(warnings), 'risk_surface': risk}, indent=2))
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
