#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
HANDOFF_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_paired_ranking_interpretation_handoff.json'
SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_paired_ranking_interpretation_handoff.schema.json'
OCCUPANCY_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_occupancy_accounting_snapshot_20260306.json'
TURNOVER_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_turnover_tempo_snapshot_20260306.json'
RANK_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_rank_decomposition_snapshot_20260306.json'
TOOL_PATH = ROOT / 'scripts' / 'tools' / 'build_rematch_world_benchmark_paired_ranking_interpretation_handoff.py'
SNAPSHOT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_paired_ranking_interpretation_handoff_snapshot_20260317.json'


def fail(msg: str) -> int:
    print(f'rematch-world-benchmark-paired-ranking-interpretation-handoff: {msg}', file=sys.stderr)
    return 1


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> int:
    for path in [HANDOFF_PATH, SCHEMA_PATH, OCCUPANCY_PATH, TURNOVER_PATH, RANK_PATH, TOOL_PATH, SNAPSHOT_JSON]:
        if not path.exists():
            return fail(f'missing {path.relative_to(ROOT)}')
    handoff = load_json(HANDOFF_PATH)
    schema = load_json(SCHEMA_PATH)
    occupancy = load_json(OCCUPANCY_PATH)
    turnover = load_json(TURNOVER_PATH)
    rank = load_json(RANK_PATH)
    snapshot = load_json(SNAPSHOT_JSON)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(handoff, schema)
    proc = subprocess.run([sys.executable, str(TOOL_PATH), '--summary-json'], cwd=ROOT, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return fail(f'tool exited nonzero: {proc.stderr or proc.stdout}')
    summary = json.loads(proc.stdout)

    canonical = ['CCEEE', 'CCDDE', 'DCECC', 'always_c', 'courteous_firm']
    if handoff['canonical_occupancy_normalized_rank_order'] != canonical:
        return fail('handoff should preserve the canonical occupancy-normalized rank order exactly')
    if handoff['extortions_sharing_canonical_order'] != [20, 50, 80]:
        return fail('handoff should preserve the extortions sharing the canonical order exactly')
    if handoff['occupancy_loss_summary']['mean_share_component_fraction_of_delay_loss'] != occupancy['headline_findings']['mean_share_component_fraction_of_delay_loss']:
        return fail('handoff should preserve the occupancy loss mean-share summary exactly')
    if handoff['tempo_scaling_summary']['highest_vs_lowest_churn_delay2_matched_share_loss_ratio'] != turnover['headline_findings']['highest_vs_lowest_churn_delay2_matched_share_loss_ratio']:
        return fail('handoff should preserve the tempo scaling ratio exactly')
    if handoff['rank_disagreement_summary']['nonzero_delay_panels_with_raw_vs_occupancy_normalized_rank_disagreement'] != rank['headline_findings']['nonzero_delay_panels_with_raw_vs_occupancy_normalized_rank_disagreement']:
        return fail('handoff should preserve the rank disagreement count exactly')
    if handoff['ranking_interpretation_rule'].count('occupancy') < 1:
        return fail('handoff should encode the occupancy-artifact interpretation rule')
    if handoff['rank_decomposition_report_sha256'] != summary['rank_decomposition_report_sha256']:
        return fail('handoff digest should match tool summary output')
    if snapshot['canonical_occupancy_normalized_rank_order'] != handoff['canonical_occupancy_normalized_rank_order']:
        return fail('snapshot should preserve canonical order exactly')
    if snapshot['total_pairwise_inversions_overall_vs_occupancy_normalized_in_nonzero_delay_panels'] != handoff['rank_disagreement_summary']['total_pairwise_inversions_overall_vs_occupancy_normalized_in_nonzero_delay_panels']:
        return fail('snapshot should preserve the total inversion count exactly')

    print('rematch-world-benchmark-paired-ranking-interpretation-handoff: ok (benchmark seed can carry a compact ranking-interpretation summary copied from the proxy occupancy, tempo, and rank-decomposition reports)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
