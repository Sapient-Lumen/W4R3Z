#!/usr/bin/env python3
from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = str(META.get('revision', 'rev0100'))
REVUP = REV.upper()
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)

CAPTURE_HELPER = ROOT / 'experiments' / 'public_trace_capture' / 'hf_attention_trace_capture.py'
CURRENT_RUNNER = ROOT / 'artifacts' / 'capture-kit' / 'RUN_CURRENT_PUBLIC_TRACE.sh'
ONE_SHOT = ROOT / 'artifacts' / 'capture-kit' / f'{REVUP}_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh'
RUNNER = ROOT / 'artifacts' / 'capture-kit' / f'{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh'


def text(path: Path) -> str:
    return path.read_text(encoding='utf-8') if path.exists() else ''


def main() -> int:
    blockers: list[str] = []
    warnings: list[str] = []
    helper = text(CAPTURE_HELPER)
    one = text(ONE_SHOT)
    runner = text(RUNNER)
    current = text(CURRENT_RUNNER)
    checks: dict[str, Any] = {
        'capture_helper_exists': CAPTURE_HELPER.exists(),
        'current_runner_exists': CURRENT_RUNNER.exists(),
        'rev_runner_exists': RUNNER.exists(),
        'rev_one_shot_exists': ONE_SHOT.exists(),
        'helper_accepts_public_model_id': '--public-model-id' in helper,
        'helper_writes_model_load_source': 'model_load_source' in helper,
        'helper_detects_local_path': 'model_load_source_is_local_path' in helper and 'load_model_revision' in helper,
        'one_shot_passes_public_model_id': '--public-model-id "$MODEL_ID"' in one,
        'one_shot_uses_local_snapshot_dir_as_loader_only': 'CAPTURE_MODEL="$LOCAL_SNAPSHOT_DIR"' in one and '--model "$CAPTURE_MODEL"' in one,
        'one_shot_keeps_bundle_model_id': '--bundle-model-id "$MODEL_ID"' in one,
        'runner_calls_snapshot_intake_when_local_snapshot_dir_set': 'public_trace_snapshot_intake_audit.py --snapshot-dir "$LOCAL_SNAPSHOT_DIR" --strict' in runner,
        'current_runner_points_to_current_revision': f'{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh' in current,
    }
    for key, ok in checks.items():
        if not ok:
            blockers.append('failed_' + key)
    stale_current = re.findall(r'REV00(9[0-9])_RUN_TINYLLAMA_PUBLIC_TRACE\.sh', current)
    if stale_current:
        blockers.append('current_runner_stale_revision_alias')
    if 'REV0099' in one or 'REV0100' in current:
        warnings.append('one_shot_or_current_contains_legacy_revision_text')
    status = 'pass' if not blockers and not warnings else ('pass_with_warnings' if not blockers else 'blocked_here')
    audit = {
        'revision': REV,
        'revision_number': int(REV.replace('rev', '')),
        'package_name': META.get('package_name'),
        'archive_name': META.get('archive_name'),
        'status': status,
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
        'summary': 'Static refactor audit for the rev0100 loader/public-identity split. It prevents local snapshot paths from replacing canonical public model identity in public trace provenance.',
        'checks': checks,
        'blockers': blockers,
        'warnings': warnings,
        'why_it_matters': 'Transformers from_pretrained can load from a local directory, while the public trace evidence should still identify the public HF repo and immutable commit. Mixing these fields would make a real trace harder to audit or compare.',
    }
    (OUT / f'{REVUP}_CAPTURE_MODEL_IDENTITY_AUDIT.json').write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    (OUT / f'{REVUP}_CAPTURE_MODEL_IDENTITY_AUDIT.md').write_text(
        f'# Capture model identity audit — {REVUP}\n\n'
        f"Status: `{status}`  \nPromotion allowed: `false`\n\n"
        '## Blockers\n\n' + ('\n'.join(f'- `{b}`' for b in blockers) if blockers else '- none') + '\n\n'
        '## Warnings\n\n' + ('\n'.join(f'- `{w}`' for w in warnings) if warnings else '- none') + '\n\n'
        '## Interpretation\n\nThis audit checks that `LOCAL_SNAPSHOT_DIR` is used only as a loader path and that `MODEL_ID` remains the public identity written into provenance and gate declarations.\n',
        encoding='utf-8')
    print(json.dumps({'status': status, 'blockers': blockers, 'warnings': warnings}, indent=2))
    return 0 if not blockers else 1

if __name__ == '__main__':
    raise SystemExit(main())
