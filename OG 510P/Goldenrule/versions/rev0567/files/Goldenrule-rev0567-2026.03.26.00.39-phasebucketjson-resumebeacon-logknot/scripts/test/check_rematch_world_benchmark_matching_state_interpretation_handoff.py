#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
HANDOFF_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_matching_state_interpretation_handoff.json'
SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_matching_state_interpretation_handoff.schema.json'
MATCHING_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_matching_friction_snapshot_20260306.json'
OCCUPANCY_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_occupancy_accounting_snapshot_20260306.json'
TOOL_PATH = ROOT / 'scripts' / 'tools' / 'build_rematch_world_benchmark_matching_state_interpretation_handoff.py'
SNAPSHOT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_matching_state_interpretation_handoff_snapshot_20260317.json'


def fail(msg: str) -> int:
    print(f'rematch-world-benchmark-matching-state-interpretation-handoff: {msg}', file=sys.stderr)
    return 1


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> int:
    for path in [HANDOFF_PATH, SCHEMA_PATH, MATCHING_PATH, OCCUPANCY_PATH, TOOL_PATH, SNAPSHOT_JSON]:
        if not path.exists():
            return fail(f'missing {path.relative_to(ROOT)}')
    handoff = load_json(HANDOFF_PATH)
    schema = load_json(SCHEMA_PATH)
    matching = load_json(MATCHING_PATH)
    occupancy = load_json(OCCUPANCY_PATH)
    snapshot = load_json(SNAPSHOT_JSON)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(handoff, schema)
    proc = subprocess.run([sys.executable, str(TOOL_PATH), '--summary-json'], cwd=ROOT, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return fail(f'tool exited nonzero: {proc.stderr or proc.stdout}')
    summary = json.loads(proc.stdout)
    if handoff['delay_tax_summary']['tested_cells'] != matching['headline_findings']['tested_cells']:
        return fail('handoff should preserve tested-cell count exactly')
    if handoff['occupancy_accounting_summary']['mean_share_component_fraction_of_delay_loss'] != occupancy['headline_findings']['mean_share_component_fraction_of_delay_loss']:
        return fail('handoff should preserve occupancy delay-loss fraction exactly')
    if handoff['matching_state_contract_guidance']['required_search_state_fields'] != ['searching_round_share', 'search_wait_rounds_avg']:
        return fail('handoff should preserve required search-state fields exactly')
    if handoff['matching_state_contract_guidance']['required_matched_state_fields'] != ['matched_round_share', 'current_match_length']:
        return fail('handoff should preserve required matched-state fields exactly')
    if handoff['matching_friction_report_sha256'] != summary['matching_friction_report_sha256']:
        return fail('handoff digest should match tool summary output')
    if snapshot['tested_cells'] != handoff['delay_tax_summary']['tested_cells']:
        return fail('snapshot should report tested-cell count exactly')
    if snapshot['largest_mean_delay_tax_policy'] != handoff['delay_tax_summary']['largest_mean_delay_tax_policy']:
        return fail('snapshot should report largest delay-tax policy exactly')
    print('rematch-world-benchmark-matching-state-interpretation-handoff: ok (benchmark seed can carry a compact delay-tax and matched-vs-search interpretation copied from the proxy reports)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
