#!/usr/bin/env python3
from __future__ import annotations

import json
import importlib.util
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_evidence_packet.json'
EVIDENCE_RECEIPT_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_evidence_receipt.json'
SEED_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_seed.json'
DECISION_CONTRACT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_decision_contract_snapshot_20260316.json'
ARTIFACT_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_compiled_artifact.json'
PREFLIGHT_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_preflight_receipt.json'
BUNDLE_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_publication_bundle_receipt.json'
BUNDLE_SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_publication_bundle_receipt.schema.json'
PREFLIGHT_SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_preflight.schema.json'


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'could not load module {name} from {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_json(path: Path, node: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(node, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def main() -> int:
    bundle = _load_module(
        'build_rematch_world_benchmark_publication_bundle_receipt',
        ROOT / 'scripts' / 'tools' / 'build_rematch_world_benchmark_publication_bundle_receipt.py',
    )
    preflight = _load_module(
        'rematch_world_benchmark_publication_preflight',
        ROOT / 'scripts' / 'tools' / 'rematch_world_benchmark_publication_preflight.py',
    )

    packet = load_json(PACKET_PATH)
    evidence_receipt = load_json(EVIDENCE_RECEIPT_PATH)
    seed = load_json(SEED_PATH)
    decision_contract = load_json(DECISION_CONTRACT_PATH)

    receipt, _patch, candidate = bundle.build_bundle_receipt(
        packet=packet,
        evidence_receipt=evidence_receipt,
        seed=seed,
        decision_contract=decision_contract,
        packet_path=PACKET_PATH,
        evidence_receipt_path=EVIDENCE_RECEIPT_PATH,
        seed_path=SEED_PATH,
        decision_contract_path=DECISION_CONTRACT_PATH,
        artifact_output_path=ARTIFACT_PATH,
        patch_output_path=None,
    )
    receipt['compiled_candidate']['artifact_output_path'] = ARTIFACT_PATH.relative_to(ROOT).as_posix()
    receipt['artifact_written'] = True

    preflight_receipt = preflight.build_preflight_summary(
        candidate=candidate,
        seed=seed,
        decision_contract=decision_contract,
        inspection_mode='artifact',
        inspection_target_path=ARTIFACT_PATH.relative_to(ROOT).as_posix(),
        seed_path=SEED_PATH.relative_to(ROOT).as_posix(),
        decision_contract_path=DECISION_CONTRACT_PATH.relative_to(ROOT).as_posix(),
    )

    jsonschema.validate(receipt, load_json(BUNDLE_SCHEMA_PATH))
    jsonschema.validate(preflight_receipt, load_json(PREFLIGHT_SCHEMA_PATH))

    _write_json(BUNDLE_PATH, receipt)
    _write_json(PREFLIGHT_PATH, preflight_receipt)

    print(f'publication-spine-examples: wrote {ARTIFACT_PATH.relative_to(ROOT)}')
    print(f'publication-spine-examples: wrote {PREFLIGHT_PATH.relative_to(ROOT)}')
    print(f'publication-spine-examples: wrote {BUNDLE_PATH.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
