#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = str(META.get('revision', 'rev0118'))
REVUP = REV.upper()
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)


def read(rel: str) -> str:
    path = ROOT / rel
    return path.read_text(encoding='utf-8', errors='replace') if path.exists() else ''


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    run_alias = read('artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh')
    run = read(f'artifacts/capture-kit/{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh')
    one = read(f'artifacts/capture-kit/{REVUP}_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh')
    prep = read(f'artifacts/capture-kit/{REVUP}_PREPARE_TINYLLAMA_SNAPSHOT.sh')
    gate = read('tools/public_trace_readiness_gate.py')
    smoke = read('tools/smoke_validate.py')

    required_files = [
        'artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh',
        f'artifacts/capture-kit/{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh',
        f'artifacts/capture-kit/{REVUP}_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh',
        f'artifacts/capture-kit/{REVUP}_PREPARE_TINYLLAMA_SNAPSHOT.sh',
        'tools/public_trace_readiness_gate.py',
        'tools/public_trace_fast_prereq_gate.py',
        'tools/smoke_validate.py',
        'tools/snapshot_prepare_phase_order_audit.py',
        'tools/snapshot_integrity_contract_audit.py',
        'tools/hf_snapshot_integrity.py',
        'tools/public_trace_capture_start_preflight_report.py',
        'tools/public_trace_capture_local_only_contract_audit.py',
    ]
    for rel in required_files:
        if not (ROOT / rel).is_file():
            errors.append('missing_required_failfast_surface:' + rel)

    if f'{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh' not in run_alias:
        errors.append('stable_run_alias_not_current_revision')
    if 'public_trace_fast_prereq_gate.py --phase capture --local-only --strict' not in run:
        errors.append('current_run_wrapper_does_not_strict_local_fast_prereq_gate')
    if 'public_trace_fast_prereq_gate.py --phase capture --download --strict' in run:
        errors.append('current_run_wrapper_should_not_offer_download_capture_gate')
    if 'public_trace_readiness_gate.py --local-only --strict' not in run:
        errors.append('current_run_wrapper_does_not_strict_local_readiness_gate')
    if 'public_trace_readiness_gate.py --download --strict' in run:
        errors.append('current_run_wrapper_should_not_offer_download_readiness_gate')
    if 'public_trace_readiness_gate.py --local-only || true' in run or 'public_trace_readiness_gate.py --download || true' in run:
        errors.append('current_run_wrapper_still_ignores_readiness_gate')
    if 'public_trace_env_preflight.py --strict trace' not in one:
        errors.append('one_shot_capture_does_not_strict_env_preflight')
    if 'public_trace_env_preflight.py --strict trace' not in prep:
        errors.append('snapshot_prepare_does_not_strict_env_preflight')
    for marker in ['blocked_here_fail_fast', 'fail_fast_prerequisite_blockers', '--continue-after-prereq-blockers', 'EXPENSIVE_OR_POSTTRACE_STEPS', 'prerequisite_blockers']:
        if marker not in gate:
            errors.append('readiness_gate_missing_failfast_marker:' + marker)
    if 'readiness_failfast' not in smoke:
        errors.append('smoke_does_not_guard_readiness_failfast_contract')
    if 'fast_prereq' not in smoke:
        errors.append('smoke_does_not_guard_fast_prereq_contract')
    if 'snapshot_prepare' not in smoke:
        errors.append('smoke_does_not_guard_snapshot_prepare_phase_contract')
    if 'snapshot_integrity_contract' not in smoke:
        errors.append('smoke_does_not_guard_snapshot_integrity_contract')
    if 'public_trace_fast_prereq_gate.py --phase snapshot --local-only --strict' not in prep:
        errors.append('snapshot_prepare_local_gate_not_snapshot_phase')
    if 'public_trace_fast_prereq_gate.py --phase snapshot --download --strict' not in prep:
        errors.append('snapshot_prepare_download_gate_not_snapshot_phase')
    if 'snapshot_integrity_contract_audit.py' not in prep:
        errors.append('snapshot_prepare_does_not_run_snapshot_integrity_contract_audit')
    if 'hf_snapshot_materializer.py --download --strict' not in prep:
        errors.append('snapshot_prepare_does_not_strictly_materialize_download_snapshot')
    if 'public_trace_dependency_lock_audit.py || true' not in prep:
        errors.append('snapshot_prepare_dependency_lock_is_still_fatal')
    if 'TRACE_GATE_STEP_TIMEOUT' not in gate:
        warnings.append('readiness_gate_step_timeout_marker_missing')

    audit: dict[str, Any] = {
        'revision': REV,
        'revision_number': int(REV.replace('rev','')),
        'package_name': META.get('package_name'),
        'archive_name': META.get('archive_name'),
        'status': 'pass' if not errors else 'fail',
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
        'summary': 'Audits the current live-path refactor: the top-level run command now stops at a strict local-only capture-start report and fast prerequisite gate before broad readiness prerequisites, one-shot capture cannot ignore env preflight blockers, and smoke guards the contract.',
        'checked_files': required_files,
        'errors': errors,
        'warnings': warnings,
        'decision': 'fail_fast_contract_guarded' if not errors else 'repair_fail_fast_contract_before_handoff',
    }
    (OUT / f'{REVUP}_READINESS_FAILFAST_CONTRACT_AUDIT.json').write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    (OUT / f'{REVUP}_READINESS_FAILFAST_CONTRACT_AUDIT.md').write_text(
        f'# Readiness fail-fast contract audit — {REVUP}\n\n'
        f"Status: `{audit['status']}`  \nPromotion allowed: `false`\n\n"
        '## Errors\n\n' + ('\n'.join(f'- `{e}`' for e in errors) if errors else '- none') + '\n\n'
        '## Warnings\n\n' + ('\n'.join(f'- `{w}`' for w in warnings) if warnings else '- none') + '\n\n'
        '## Interpretation\n\nThis is an anti-waste guard, not performance evidence. It prevents a known blocked runtime from entering expensive backend/model probes or capture attempts before prerequisites are repaired.\n',
        encoding='utf-8'
    )
    print(json.dumps({'status': audit['status'], 'errors': errors, 'warnings': warnings}, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
