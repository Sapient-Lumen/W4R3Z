#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
RETENTION_EXIT_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_retention_exit_receipt.json'
PACKET_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_evidence_packet.json'
EVIDENCE_RECEIPT_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_evidence_receipt.json'
OUT_PRUNE_RECEIPT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_prune_execute_receipt.json'
OUT_AUDIT_RECEIPT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_post_prune_audit_receipt.json'
PRUNE_SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_prune_receipt.schema.json'
AUDIT_SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_post_prune_audit_receipt.schema.json'


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'could not load module {name} from {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _copy_rel(src: Path, temp_root: Path) -> Path:
    rel = src.relative_to(ROOT)
    dst = temp_root / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return dst


def build_examples() -> tuple[dict[str, Any], dict[str, Any]]:
    compile_module = _load_module(
        'compile_rematch_world_benchmark_fill_patch_from_evidence_packet',
        ROOT / 'scripts' / 'tools' / 'compile_rematch_world_benchmark_fill_patch_from_evidence_packet.py',
    )
    prune_module = _load_module(
        'prune_rematch_world_benchmark_transients',
        ROOT / 'scripts' / 'tools' / 'prune_rematch_world_benchmark_transients.py',
    )
    audit_module = _load_module(
        'audit_rematch_world_benchmark_post_prune_state',
        ROOT / 'scripts' / 'tools' / 'audit_rematch_world_benchmark_post_prune_state.py',
    )

    retention_exit = json.loads(RETENTION_EXIT_PATH.read_text(encoding='utf-8'))
    evidence_receipt = json.loads(EVIDENCE_RECEIPT_PATH.read_text(encoding='utf-8'))

    with tempfile.TemporaryDirectory() as tmpdir:
        temp_root = Path(tmpdir)

        for row in retention_exit['durable_retained_objects']:
            _copy_rel(ROOT / row['path'], temp_root)

        temp_packet = _copy_rel(PACKET_PATH, temp_root)
        temp_retention_exit = json.loads(json.dumps(retention_exit))
        temp_retention_exit['exit_conditions']['scratch_hashes_match_receipt_now'] = True
        temp_retention_exit['exit_conditions']['retention_exit_ready'] = True
        for row in temp_retention_exit['exit_ready_transient_objects']:
            row['exit_ready'] = True

        patch_rel = Path('examples/scratch/rematch_world_benchmark/compiled_fill_patch.json')
        patch_path = temp_root / patch_rel
        patch_path.parent.mkdir(parents=True, exist_ok=True)
        patch = compile_module.build_fill_patch(compile_module.load_json(temp_packet))
        patch_path.write_text(json.dumps(patch, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        patch_blob = patch_path.read_bytes()
        temp_retention_exit['exit_ready_transient_objects'][0]['path'] = patch_rel.as_posix()
        temp_retention_exit['exit_ready_transient_objects'][0]['byte_count'] = len(patch_blob)
        temp_retention_exit['exit_ready_transient_objects'][0]['sha256'] = prune_module._sha256_json(json.loads(patch_blob.decode('utf-8')))

        for index, source in enumerate(evidence_receipt['scratch_sources'], start=1):
            src = ROOT / source['scratch_path']
            if src.exists():
                copied = _copy_rel(src, temp_root)
                temp_retention_exit['exit_ready_transient_objects'][index]['path'] = copied.relative_to(temp_root).as_posix()
            else:
                temp_retention_exit['exit_ready_transient_objects'][index]['path'] = source['scratch_path']

        temp_retention_exit_path = temp_root / 'examples' / 'snapshots' / 'rematch_world_benchmark_retention_exit_receipt.json'
        temp_retention_exit_path.parent.mkdir(parents=True, exist_ok=True)
        temp_retention_exit_path.write_text(json.dumps(temp_retention_exit, indent=2, sort_keys=True) + '\n', encoding='utf-8')

        prune_receipt_path = temp_root / 'examples' / 'snapshots' / 'rematch_world_benchmark_prune_execute_receipt.json'
        prune_receipt = prune_module.build_prune_receipt(
            temp_retention_exit,
            temp_retention_exit_path,
            root=temp_root,
            execute=True,
            prune_empty_dirs=True,
        )
        prune_receipt_path.write_text(json.dumps(prune_receipt, indent=2, sort_keys=True) + '\n', encoding='utf-8')

        audit_receipt = audit_module.build_post_prune_audit_receipt(
            temp_retention_exit,
            temp_retention_exit_path,
            prune_receipt,
            prune_receipt_path,
            root=temp_root,
        )
        audit_receipt_path = temp_root / 'examples' / 'snapshots' / 'rematch_world_benchmark_post_prune_audit_receipt.json'
        audit_receipt_path.write_text(json.dumps(audit_receipt, indent=2, sort_keys=True) + '\n', encoding='utf-8')

        prune_schema = json.loads(PRUNE_SCHEMA_PATH.read_text(encoding='utf-8'))
        jsonschema.Draft202012Validator.check_schema(prune_schema)
        jsonschema.validate(prune_receipt, prune_schema)
        audit_schema = json.loads(AUDIT_SCHEMA_PATH.read_text(encoding='utf-8'))
        jsonschema.Draft202012Validator.check_schema(audit_schema)
        jsonschema.validate(audit_receipt, audit_schema)

        OUT_PRUNE_RECEIPT.write_text(prune_receipt_path.read_text(encoding='utf-8'), encoding='utf-8')
        OUT_AUDIT_RECEIPT.write_text(audit_receipt_path.read_text(encoding='utf-8'), encoding='utf-8')
        return prune_receipt, audit_receipt


def main() -> int:
    build_examples()
    print(f'rematch-world-benchmark-post-prune-examples: wrote {OUT_PRUNE_RECEIPT.relative_to(ROOT)}')
    print(f'rematch-world-benchmark-post-prune-examples: wrote {OUT_AUDIT_RECEIPT.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
