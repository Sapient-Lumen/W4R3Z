#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
HANDOFF_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_winner_triage_handoff.json'
SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_winner_triage_handoff.schema.json'
LIVE_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_live_contenders_snapshot_20260306.json'
WINNER_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_winner_certification_snapshot_20260306.json'
MATERIALITY_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_materiality_gate_snapshot_20260306.json'
DECISION_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_decision_contract_snapshot_20260316.json'
TOOL_PATH = ROOT / 'scripts' / 'tools' / 'build_rematch_world_benchmark_winner_triage_handoff.py'
SNAPSHOT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_winner_triage_handoff_snapshot_20260317.json'

def fail(msg: str) -> int:
    print(f'rematch-world-benchmark-winner-triage-handoff: {msg}', file=sys.stderr)
    return 1

def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding='utf-8'))

def main() -> int:
    for path in [HANDOFF_PATH, SCHEMA_PATH, LIVE_PATH, WINNER_PATH, MATERIALITY_PATH, DECISION_PATH, TOOL_PATH, SNAPSHOT_JSON]:
        if not path.exists():
            return fail(f'missing {path.relative_to(ROOT)}')
    handoff = load_json(HANDOFF_PATH)
    schema = load_json(SCHEMA_PATH)
    live = load_json(LIVE_PATH)
    winner = load_json(WINNER_PATH)
    materiality = load_json(MATERIALITY_PATH)
    snapshot = load_json(SNAPSHOT_JSON)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(handoff, schema)
    proc = subprocess.run([sys.executable, str(TOOL_PATH), '--summary-json'], cwd=ROOT, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return fail(f'tool exited nonzero: {proc.stderr or proc.stdout}')
    summary = json.loads(proc.stdout)
    if handoff['live_contender_set_union'] != ['CCEEE', 'CCDDE', 'always_c']:
        return fail('handoff should preserve the live contender union exactly')
    if handoff['leaders_observed_anywhere_in_tested_band'] != live['headline_findings']['leaders_observed_anywhere_in_tested_band']:
        return fail('handoff should preserve observed leaders exactly')
    if handoff['winner_certification_summary']['uncertified_leaders_95_ci'] != winner['headline_findings']['uncertified_leaders_95_ci']:
        return fail('handoff should preserve uncertified leader count exactly')
    if handoff['materiality_summary']['counts_by_delta'] != materiality['headline_findings']['counts_by_delta']:
        return fail('handoff should preserve materiality counts exactly')
    if handoff['live_contenders_report_sha256'] != summary['live_contenders_report_sha256']:
        return fail('handoff digest should match tool summary output')
    if snapshot['uncertified_panel_count'] != len(handoff['uncertified_panel_rows']):
        return fail('snapshot should report uncertified panel count exactly')
    if snapshot['certified_practical_tie_count'] != handoff['materiality_summary']['certified_leader_but_practical_tie_at_delta_0_005_count']:
        return fail('snapshot should report certified practical-tie count exactly')
    print('rematch-world-benchmark-winner-triage-handoff: ok (benchmark seed can carry a compact winner-triage summary copied from the proxy live-contender, certification, and materiality reports)')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
