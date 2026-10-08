#!/usr/bin/env python3
from __future__ import annotations
import json
import tempfile
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.hf_snapshot_integrity import REQUIRED_SNAPSHOT_FILES, inspect_snapshot

META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = str(META.get('revision', 'rev0121'))
REVUP = REV.upper()
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)


def read(rel: str) -> str:
    p = ROOT / rel
    return p.read_text(encoding='utf-8', errors='replace') if p.exists() else ''


def make_fake_snapshot(path: Path) -> None:
    for name in REQUIRED_SNAPSHOT_FILES:
        (path / name).write_bytes(b'')
    (path / 'config.json').write_text(json.dumps({
        'model_type': 'llama',
        'architectures': ['LlamaForCausalLM'],
        'hidden_size': 2048,
        'intermediate_size': 5632,
        'num_attention_heads': 32,
        'num_key_value_heads': 4,
        'num_hidden_layers': 22,
        'max_position_embeddings': 2048,
    }), encoding='utf-8')
    (path / 'generation_config.json').write_text('{}', encoding='utf-8')
    (path / 'special_tokens_map.json').write_text('{}', encoding='utf-8')
    (path / 'tokenizer_config.json').write_text('{}', encoding='utf-8')


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    run = read(f'artifacts/capture-kit/{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh')
    prep = read(f'artifacts/capture-kit/{REVUP}_PREPARE_TINYLLAMA_SNAPSHOT.sh')
    fast = read('tools/public_trace_fast_prereq_gate.py')
    materializer = read('tools/hf_snapshot_materializer.py')
    integrity = read('tools/hf_snapshot_integrity.py')
    smoke = read('tools/smoke_validate.py')
    if '--phase capture --local-only --strict' not in run:
        errors.append('run_wrapper_missing_capture_phase_marker:--phase capture --local-only --strict')
    if '--phase capture --download --strict' in run:
        errors.append('run_wrapper_should_not_have_download_capture_phase_marker')
    for marker in ['--phase snapshot --local-only --strict', '--phase snapshot --download --strict']:
        if marker not in prep:
            errors.append('prepare_wrapper_missing_snapshot_phase_marker:' + marker)
    for marker in ['EXPECTED_MODEL_SAFETENSORS_SHA256', 'model_safetensors_header_parse_failed', 'model_safetensors_sparse_or_not_fully_materialized']:
        if marker not in fast and marker not in materializer and marker not in integrity:
            errors.append('snapshot_integrity_marker_missing:' + marker)
    if 'snapshot_integrity_contract' not in smoke:
        errors.append('smoke_does_not_guard_snapshot_integrity_contract')
    with tempfile.TemporaryDirectory() as td:
        fake = Path(td) / 'fake-tinyllama-snapshot'
        fake.mkdir()
        make_fake_snapshot(fake)
        fake_report = inspect_snapshot(fake)
    if fake_report.get('complete_required_snapshot'):
        errors.append('filename_only_fake_snapshot_passed_integrity')
    expected_fake_blockers = {'snapshot_file_too_small:model.safetensors', 'model_safetensors_smaller_than_expected_remote_file', 'model_safetensors_too_small_for_header'}
    missing_expected = sorted(expected_fake_blockers.difference(set(fake_report.get('blockers', []))))
    if missing_expected:
        errors.append('fake_snapshot_missing_expected_blockers:' + ','.join(missing_expected))
    audit = {
        'revision': REV,
        'revision_number': int(REV.replace('rev','')),
        'package_name': META.get('package_name'),
        'archive_name': META.get('archive_name'),
        'status': 'pass' if not errors else 'fail',
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
        'summary': 'Executable audit/refactor guard for rev0121: local-only snapshot preparation must not require transformers, but a fake snapshot with only required filenames must be rejected before any capture attempt.',
        'fake_snapshot_result': fake_report,
        'errors': errors,
        'warnings': warnings,
        'decision': 'snapshot_phase_and_integrity_contract_guarded' if not errors else 'repair_snapshot_phase_or_integrity_contract',
        'online_source_basis': [
            {'url': 'https://huggingface.co/docs/transformers/en/installation', 'fact': 'Offline model loading requires files to be downloaded and cached ahead of time.'},
            {'url': 'https://huggingface.co/docs/huggingface_hub/en/package_reference/file_download', 'fact': 'snapshot_download returns a local snapshot path and supports local_files_only, allow_patterns, and incomplete snapshot errors.'},
            {'url': 'https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0/blob/main/model.safetensors', 'fact': 'The selected TinyLlama safetensors file is published as a 2.2 GB file with a SHA256 digest.'},
            {'url': 'https://huggingface.co/docs/safetensors/en/metadata_parsing', 'fact': 'Safetensors metadata is in a parseable header separate from tensor bytes.'},
        ],
    }
    (OUT / f'{REVUP}_SNAPSHOT_INTEGRITY_CONTRACT_AUDIT.json').write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    lines = [
        f'# Snapshot integrity contract audit — {REVUP}',
        '',
        f"Status: `{audit['status']}`  ",
        'Promotion allowed: `false`',
        '',
        '## Errors',
        '',
    ]
    lines.extend([f'- `{e}`' for e in errors] if errors else ['- none'])
    lines.extend(['', '## Interpretation', '', 'This audit is deliberately executable: it creates a throwaway required-filename snapshot and verifies that the shared integrity layer rejects it.'])
    (OUT / f'{REVUP}_SNAPSHOT_INTEGRITY_CONTRACT_AUDIT.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({'status': audit['status'], 'errors': errors, 'warnings': warnings}, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
