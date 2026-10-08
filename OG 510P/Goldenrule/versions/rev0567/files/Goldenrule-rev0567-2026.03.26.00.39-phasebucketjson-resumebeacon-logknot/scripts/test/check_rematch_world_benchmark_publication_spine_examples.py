#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_evidence_packet.json'
EVIDENCE_RECEIPT_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_evidence_receipt.json'
SEED_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_seed.json'
DECISION_CONTRACT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_decision_contract_snapshot_20260316.json'
ARTIFACT_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_compiled_artifact.json'
PREFLIGHT_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_preflight_receipt.json'
BUNDLE_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_publication_bundle_receipt.json'


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def fail(message: str) -> int:
    print(f'publication-spine-examples: {message}', file=sys.stderr)
    return 1


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'could not load module {name} from {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    bundle_tool = _load_module(
        'build_rematch_world_benchmark_publication_bundle_receipt',
        ROOT / 'scripts' / 'tools' / 'build_rematch_world_benchmark_publication_bundle_receipt.py',
    )
    preflight_tool = _load_module(
        'rematch_world_benchmark_publication_preflight',
        ROOT / 'scripts' / 'tools' / 'rematch_world_benchmark_publication_preflight.py',
    )

    packet = load_json(PACKET_PATH)
    evidence_receipt = load_json(EVIDENCE_RECEIPT_PATH)
    seed = load_json(SEED_PATH)
    decision_contract = load_json(DECISION_CONTRACT_PATH)
    compiled_artifact = load_json(ARTIFACT_PATH)
    preflight_receipt = load_json(PREFLIGHT_PATH)
    bundle_receipt = load_json(BUNDLE_PATH)

    expected_bundle, _patch, expected_candidate = bundle_tool.build_bundle_receipt(
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
    expected_bundle['compiled_candidate']['artifact_output_path'] = ARTIFACT_PATH.relative_to(ROOT).as_posix()
    expected_bundle['artifact_written'] = True
    expected_preflight = preflight_tool.build_preflight_summary(
        candidate=expected_candidate,
        seed=seed,
        decision_contract=decision_contract,
        inspection_mode='artifact',
        inspection_target_path=ARTIFACT_PATH.relative_to(ROOT).as_posix(),
        seed_path=SEED_PATH.relative_to(ROOT).as_posix(),
        decision_contract_path=DECISION_CONTRACT_PATH.relative_to(ROOT).as_posix(),
    )

    if compiled_artifact != expected_candidate:
        return fail('compiled artifact drift detected; rerun publication spine builder')
    if preflight_receipt != expected_preflight:
        return fail('preflight receipt drift detected; rerun publication spine builder')
    if bundle_receipt != expected_bundle:
        return fail('publication bundle receipt drift detected; rerun publication spine builder')
    if not bundle_receipt['artifact_written']:
        return fail('expected artifact_written=true in publication bundle receipt')
    if bundle_receipt['compiled_candidate']['artifact_output_path'] != ARTIFACT_PATH.relative_to(ROOT).as_posix():
        return fail('publication bundle receipt should point at retained compiled artifact path')
    if not preflight_receipt['preflight_ready']:
        return fail('expected retained compiled artifact to stay preflight-ready')
    if preflight_receipt['status_counts']['blocking_fill_slot_count'] != 0:
        return fail('expected zero blocking fill slots in retained compiled artifact preflight receipt')
    if preflight_receipt['status_counts']['forbidden_changed_path_count'] != 0:
        return fail('expected zero forbidden changed paths in retained compiled artifact preflight receipt')
    print('publication-spine-examples: ok')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
