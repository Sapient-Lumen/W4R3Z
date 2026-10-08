#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
HANDOFF_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_turnover_tempo_interpretation_handoff.json'
SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_turnover_tempo_interpretation_handoff.schema.json'
TURNOVER_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_turnover_tempo_snapshot_20260306.json'
TOOL_PATH = ROOT / 'scripts' / 'tools' / 'build_rematch_world_benchmark_turnover_tempo_interpretation_handoff.py'
SNAPSHOT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_turnover_tempo_interpretation_handoff_snapshot_20260317.json'


def fail(msg: str) -> int:
    print(f'rematch-world-benchmark-turnover-tempo-interpretation-handoff: {msg}', file=sys.stderr)
    return 1


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> int:
    for path in [HANDOFF_PATH, SCHEMA_PATH, TURNOVER_PATH, TOOL_PATH, SNAPSHOT_JSON]:
        if not path.exists():
            return fail(f'missing {path.relative_to(ROOT)}')
    handoff = load_json(HANDOFF_PATH)
    schema = load_json(SCHEMA_PATH)
    turnover = load_json(TURNOVER_PATH)
    snapshot = load_json(SNAPSHOT_JSON)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(handoff, schema)
    proc = subprocess.run([sys.executable, str(TOOL_PATH), '--summary-json'], cwd=ROOT, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return fail(f'tool exited nonzero: {proc.stderr or proc.stdout}')
    summary = json.loads(proc.stdout)
    headline = turnover['headline_findings']
    if handoff['tempo_scaling_summary']['scenario_means_checked'] != headline['scenario_means_checked']:
        return fail('handoff should preserve checked scenario count exactly')
    if handoff['tempo_scaling_summary']['highest_vs_lowest_churn_delay2_matched_share_loss_ratio'] != headline['highest_vs_lowest_churn_delay2_matched_share_loss_ratio']:
        return fail('handoff should preserve highest-vs-lowest churn ratio exactly')
    if handoff['turnover_tempo_contract_guidance']['required_policy_row_fields'] != ['avg_match_length', 'delay_or_search_dead_time', 'turnover_metric_label']:
        return fail('handoff should preserve required turnover-policy-row fields exactly')
    if handoff['turnover_tempo_report_sha256'] != summary['turnover_tempo_report_sha256']:
        return fail('handoff digest should match tool summary output')
    if snapshot['scenario_means_checked'] != handoff['tempo_scaling_summary']['scenario_means_checked']:
        return fail('snapshot should report checked scenario count exactly')
    if snapshot['highest_churn_delay2_cell'] != handoff['tempo_scaling_summary']['highest_churn_delay2_cell']:
        return fail('snapshot should report highest-churn anchor exactly')
    print('rematch-world-benchmark-turnover-tempo-interpretation-handoff: ok (benchmark seed can carry a compact tempo-scaled delay interpretation copied from the proxy turnover report)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
