#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_publication_bundle_receipt.json'
SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_publication_bundle_receipt.schema.json'


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'could not load module {name} from {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    builder = _load_module(
        'build_rematch_world_benchmark_publication_bundle_receipt',
        ROOT / 'scripts' / 'tools' / 'build_rematch_world_benchmark_publication_bundle_receipt.py',
    )
    packet_path = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_evidence_packet.json'
    evidence_receipt_path = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_evidence_receipt.json'
    seed_path = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_seed.json'
    decision_contract_path = ROOT / 'artifacts' / 'reports' / 'rematch_decision_contract_snapshot_20260316.json'

    receipt, _patch, _candidate = builder.build_bundle_receipt(
        packet=load_json(packet_path),
        evidence_receipt=load_json(evidence_receipt_path),
        seed=load_json(seed_path),
        decision_contract=load_json(decision_contract_path),
        packet_path=packet_path,
        evidence_receipt_path=evidence_receipt_path,
        seed_path=seed_path,
        decision_contract_path=decision_contract_path,
        artifact_output_path=None,
        patch_output_path=None,
    )
    schema = load_json(SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(receipt, schema)
    OUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(f'publication-bundle-example: wrote {OUT.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
