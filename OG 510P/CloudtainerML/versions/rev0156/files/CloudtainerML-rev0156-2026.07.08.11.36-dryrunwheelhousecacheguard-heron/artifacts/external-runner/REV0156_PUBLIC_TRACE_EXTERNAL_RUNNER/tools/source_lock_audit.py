#!/usr/bin/env python3
from __future__ import annotations
import json, re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = str(META.get('revision', 'rev0095'))
REVUP = REV.upper()
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)
HEX40 = re.compile(r'^[0-9a-fA-F]{40}$')


def load(rel: str) -> dict[str, Any]:
    p = ROOT / rel
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}


def main() -> int:
    lock = load(f'artifacts/run-manifests/{REVUP}_TINYLLAMA_SOURCE_LOCK.json')
    packet = load(f'artifacts/run-manifests/{REVUP}_TINYLLAMA_PUBLIC_TRACE_RUN_PACKET.json')
    errors: list[str] = []
    warnings: list[str] = []
    if lock.get('revision') != REV:
        errors.append('source_lock_revision_not_current')
    if lock.get('revision_number') is not None and int(lock.get('revision_number')) != int(REV.replace('rev','')):
        errors.append('source_lock_revision_number_not_current')
    if lock.get('package_name') and lock.get('package_name') != META.get('package_name'):
        errors.append('source_lock_package_name_not_current')
    if lock.get('archive_name') and lock.get('archive_name') != META.get('archive_name'):
        errors.append('source_lock_archive_name_not_current')

    target = lock.get('target_model', {})
    packet_target = packet.get('target_model', {})
    full = str(target.get('model_revision', ''))
    if target.get('model_id') != 'TinyLlama/TinyLlama-1.1B-Chat-v1.0':
        errors.append('source_lock_model_id_not_tinyllama_chat_v1')
    if not HEX40.match(full):
        errors.append('source_lock_revision_not_full_40_hex_commit')
    if target.get('tokenizer_revision') != full:
        errors.append('source_lock_tokenizer_revision_not_equal_model_revision')
    if str(target.get('license', '')).lower() != 'apache-2.0':
        errors.append('source_lock_license_not_apache_2_0')
    if full and full not in str(target.get('weights_source', '')):
        errors.append('weights_source_does_not_contain_full_revision')
    if '/tree/' not in str(target.get('weights_source', '')):
        errors.append('weights_source_not_hf_tree_url')
    if target != packet_target:
        errors.append('run_packet_target_differs_from_source_lock')
    facts = lock.get('source_facts', [])
    if len(facts) < 5:
        errors.append('too_few_source_facts_recorded')
    for fact in facts:
        if not fact.get('url') or not fact.get('observed_lines_from_web_run'):
            warnings.append('source_fact_missing_url_or_observed_lines')
    audit = {
        'revision': REV,
        'revision_number': int(REV.replace('rev','')),
        'package_name': META.get('package_name'),
        'archive_name': META.get('archive_name'),
        'status': 'pass' if not errors else 'fail',
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
        'summary': 'Validates that the public-trace target is locked to an immutable HF tree, license/source facts are recorded, current source-lock metadata matches CUBE-META, and the run packet consumes the same target.',
        'source_lock': f'artifacts/run-manifests/{REVUP}_TINYLLAMA_SOURCE_LOCK.json',
        'run_packet': f'artifacts/run-manifests/{REVUP}_TINYLLAMA_PUBLIC_TRACE_RUN_PACKET.json',
        'errors': errors,
        'warnings': warnings,
        'decision': 'source_lock_ok_run_environment_next' if not errors else 'repair_source_lock_before_trace',
    }
    (OUT / f'{REVUP}_SOURCE_LOCK_AUDIT.json').write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    (OUT / f'{REVUP}_SOURCE_LOCK_AUDIT.md').write_text(
        f'# Source lock audit — {REVUP}\n\n'
        f"Status: `{audit['status']}`  \nPromotion allowed: `false`\n\n"
        f"Target: `{target.get('model_id')}` at `{target.get('model_revision')}`\n\n"
        '## Errors\n\n' + ('\n'.join(f'- `{e}`' for e in errors) if errors else '- none') + '\n\n'
        '## Warnings\n\n' + ('\n'.join(f'- `{w}`' for w in warnings) if warnings else '- none') + '\n\n'
        '## Interpretation\n\nThe model choice is no longer a blocker. The remaining risk is execution environment and hardware timing, not ambiguous source provenance.\n',
        encoding='utf-8'
    )
    print(json.dumps({'status': audit['status'], 'errors': errors, 'warnings': warnings}, indent=2))
    return 0 if not errors else 1

if __name__ == '__main__':
    raise SystemExit(main())
