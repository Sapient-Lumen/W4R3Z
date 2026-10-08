#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
BRIDGE_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_canonicalization_bridge_receipt.json'
SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_canonicalization_handoff.schema.json'


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def sha256_json(node: Any) -> str:
    blob = json.dumps(node, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(blob).hexdigest()


def build_handoff(bridge_receipt: dict[str, Any]) -> dict[str, Any]:
    planner_modes = []
    for row in bridge_receipt['planner_contract']['mode_rows']:
        planner_modes.append(
            {
                'mode_id': row['id'],
                'label': row['label'],
                'planner_kind': row['planner_kind'],
                'recommended_key_fields': list(row['recommended_key_fields']),
                'minimal_exact_horizon': row['minimal_exact_horizon'],
                'regime_count': row['regime_count'],
            }
        )

    return {
        'contract_kind': 'rematch_world_benchmark_canonicalization_handoff',
        'contract_version': '2026-03-17.rematch_world_benchmark_canonicalization_handoff.v1',
        'planner_origin': 'copy the current SG-003 bridge receipt into the benchmark seed until a native rematch-world planner manifest exists',
        'bridge_receipt_path': 'examples/snapshots/rematch_world_canonicalization_bridge_receipt.json',
        'bridge_receipt_sha256': sha256_json(bridge_receipt),
        'mode_rows': planner_modes,
        'zero_noise_dispatch_contract': {
            'support_signature_count': bridge_receipt['zero_noise_classifier_contract']['support_signature_count'],
            'ordered_rule_count': bridge_receipt['zero_noise_classifier_contract']['ordered_rule_count'],
            'dispatch_surface_reduction_factor': bridge_receipt['zero_noise_classifier_contract']['dispatch_surface_reduction_factor'],
        },
        'invalidation_triggers': list(bridge_receipt['must_regenerate_when']),
        'upgrade_requirement': 'Replace this copied bridge-derived handoff with engine-measured world rows once a native rematch-world planner manifest is emitted; until then, keep this section citation-first and do not paste wide signature tables into benchmark artifacts.',
        'size_discipline_note': 'Carry only compact planner rows, bridge hashes, and dispatch compression totals inside the benchmark artifact; keep wide canonicalization tables scratch-only or in cited reports.',
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Build the compact canonicalization handoff section to copy into the rematch-world benchmark seed.')
    parser.add_argument('--bridge', default=str(BRIDGE_PATH), help='Path to the rematch-world canonicalization bridge receipt JSON.')
    parser.add_argument('--output', help='Write the handoff JSON to this path instead of stdout.')
    parser.add_argument('--summary-json', action='store_true', help='Emit only a compact summary instead of the full handoff JSON.')
    args = parser.parse_args()

    bridge_path = Path(args.bridge)
    if not bridge_path.is_absolute():
        bridge_path = (ROOT / bridge_path).resolve()

    bridge_receipt = load_json(bridge_path)
    handoff = build_handoff(bridge_receipt)
    schema = load_json(SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(handoff, schema)

    if args.summary_json:
        summary = {
            'bridge_receipt_path': bridge_path.relative_to(ROOT).as_posix() if bridge_path.is_relative_to(ROOT) else str(bridge_path),
            'bridge_receipt_sha256': handoff['bridge_receipt_sha256'],
            'mode_count': len(handoff['mode_rows']),
            'mode_horizons': {row['mode_id']: row['minimal_exact_horizon'] for row in handoff['mode_rows']},
            'ordered_rule_count': handoff['zero_noise_dispatch_contract']['ordered_rule_count'],
            'dispatch_surface_reduction_factor': handoff['zero_noise_dispatch_contract']['dispatch_surface_reduction_factor'],
        }
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    rendered = json.dumps(handoff, indent=2, sort_keys=True) + '\n'
    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = ROOT / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding='utf-8')
        print(f'rematch-world-benchmark-canonicalization-handoff: wrote {output_path.relative_to(ROOT).as_posix()}')
        return 0

    print(rendered, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
