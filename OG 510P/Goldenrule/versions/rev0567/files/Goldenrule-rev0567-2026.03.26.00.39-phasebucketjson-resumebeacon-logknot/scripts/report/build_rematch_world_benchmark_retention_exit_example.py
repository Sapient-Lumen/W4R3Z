#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_retention_exit_receipt.json'
PACKET_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_evidence_packet.json'
EVIDENCE_RECEIPT_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_evidence_receipt.json'
SEED_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_seed.json'
DECISION_CONTRACT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_decision_contract_snapshot_20260316.json'
ARTIFACT_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_compiled_artifact.json'
PREFLIGHT_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_preflight_receipt.json'
BUNDLE_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_publication_bundle_receipt.json'
AUDIT_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_publication_spine_audit_receipt.json'


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'could not load module {name} from {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> int:
    tool = _load_module(
        'build_rematch_world_benchmark_retention_exit_receipt',
        ROOT / 'scripts' / 'tools' / 'build_rematch_world_benchmark_retention_exit_receipt.py',
    )
    receipt = tool.build_retention_exit_receipt(
        packet=load_json(PACKET_PATH),
        evidence_receipt=load_json(EVIDENCE_RECEIPT_PATH),
        seed=load_json(SEED_PATH),
        decision_contract=load_json(DECISION_CONTRACT_PATH),
        compiled_artifact=load_json(ARTIFACT_PATH),
        preflight_receipt=load_json(PREFLIGHT_PATH),
        bundle_receipt=load_json(BUNDLE_PATH),
        audit_receipt=load_json(AUDIT_PATH),
        packet_path=PACKET_PATH,
        evidence_receipt_path=EVIDENCE_RECEIPT_PATH,
        seed_path=SEED_PATH,
        decision_contract_path=DECISION_CONTRACT_PATH,
        compiled_artifact_path=ARTIFACT_PATH,
        preflight_receipt_path=PREFLIGHT_PATH,
        bundle_receipt_path=BUNDLE_PATH,
        audit_receipt_path=AUDIT_PATH,
    )
    OUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(f'retention-exit-example: wrote {OUT.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
