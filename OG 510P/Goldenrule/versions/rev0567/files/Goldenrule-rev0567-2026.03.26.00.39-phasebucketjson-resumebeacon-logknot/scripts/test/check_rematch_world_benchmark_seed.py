#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SEED_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_seed.json'
SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_seed.schema.json'
PUBLICATION_CONTRACT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_world_publication_contract_snapshot_20260316.json'
DECISION_CONTRACT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_decision_contract_snapshot_20260316.json'
HANDOFF_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_canonicalization_handoff.json'
WINNER_HANDOFF_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_winner_triage_handoff.json'
DELTA_HANDOFF_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_delta_shortlist_handoff.json'
RANK_HANDOFF_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_paired_ranking_interpretation_handoff.json'
MATCHING_HANDOFF_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_matching_state_interpretation_handoff.json'
TURNOVER_INTERPRETATION_HANDOFF_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_turnover_tempo_interpretation_handoff.json'
WORLD_SEMANTICS_INTERPRETATION_HANDOFF_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_world_semantics_interpretation_handoff.json'
EXPECTED_SECTIONS = [
    'world_semantics_contract',
    'matching_state_contract',
    'occupancy_accounting_contract',
    'turnover_tempo_contract',
    'paired_ranking_views_contract',
    'compact_decision_bundle',
]
TEMPLATE_POLICY = 'TEMPLATE_replace_with_policy_id'


def fail(msg: str) -> int:
    print(f'rematch-world-benchmark-seed: {msg}', file=sys.stderr)
    return 1


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> int:
    for path in [SEED_PATH, SCHEMA_PATH, PUBLICATION_CONTRACT_PATH, DECISION_CONTRACT_PATH, HANDOFF_PATH, WINNER_HANDOFF_PATH, DELTA_HANDOFF_PATH, RANK_HANDOFF_PATH, MATCHING_HANDOFF_PATH, TURNOVER_INTERPRETATION_HANDOFF_PATH, WORLD_SEMANTICS_INTERPRETATION_HANDOFF_PATH]:
        if not path.exists():
            return fail(f'missing {path.relative_to(ROOT)}')

    seed = load_json(SEED_PATH)
    schema = load_json(SCHEMA_PATH)
    publication = load_json(PUBLICATION_CONTRACT_PATH)
    decision = load_json(DECISION_CONTRACT_PATH)
    handoff = load_json(HANDOFF_PATH)
    winner_handoff = load_json(WINNER_HANDOFF_PATH)
    delta_handoff = load_json(DELTA_HANDOFF_PATH)
    rank_handoff = load_json(RANK_HANDOFF_PATH)
    matching_handoff = load_json(MATCHING_HANDOFF_PATH)
    turnover_interpretation_handoff = load_json(TURNOVER_INTERPRETATION_HANDOFF_PATH)
    world_semantics_interpretation_handoff = load_json(WORLD_SEMANTICS_INTERPRETATION_HANDOFF_PATH)

    try:
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.validate(seed, schema)
    except jsonschema.ValidationError as exc:
        return fail(f'schema validation failed: {exc.message}')
    except jsonschema.SchemaError as exc:
        return fail(f'invalid schema: {exc.message}')

    if seed['artifact_state'] != 'seed_template':
        return fail('artifact_state must be seed_template')
    if seed['benchmark_kind'] != 'endogenous_rematch_world_benchmark':
        return fail('unexpected benchmark_kind')
    if seed['required_sections'] != EXPECTED_SECTIONS:
        return fail('required_sections drift from world publication contract')
    if seed['recommended_fill_order'] != EXPECTED_SECTIONS:
        return fail('recommended_fill_order must match section order exactly')

    if seed['publication_contract_path'] != 'artifacts/reports/rematch_world_publication_contract_snapshot_20260316.json':
        return fail('publication_contract_path mismatch')
    if seed['publication_contract_schema_path'] != publication['schema_path']:
        return fail('publication_contract_schema_path mismatch')
    if seed['publication_contract_validator_path'] != publication['validator_path']:
        return fail('publication_contract_validator_path mismatch')
    if seed['decision_contract_path'] != 'artifacts/reports/rematch_decision_contract_snapshot_20260316.json':
        return fail('decision_contract_path mismatch')
    if seed['decision_contract_schema_path'] != publication['publication_contract_shape']['decision_contract_schema_path']:
        return fail('decision_contract_schema_path mismatch')
    if seed['decision_contract_validator_path'] != publication['publication_contract_shape']['decision_contract_validator_path']:
        return fail('decision_contract_validator_path mismatch')

    status = seed['section_status']
    for section in EXPECTED_SECTIONS[:-1]:
        if status[section] != 'pending_fill':
            return fail(f'{section}: expected pending_fill')
    if status['canonicalization_planner_contract'] != 'copied_from_bridge_contract':
        return fail('canonicalization_planner_contract: expected copied_from_bridge_contract')
    if status['winner_triage_handoff'] != 'copied_from_proxy_winner_triage_contract':
        return fail('winner_triage_handoff: expected copied_from_proxy_winner_triage_contract')
    if status['delta_shortlist_handoff'] != 'copied_from_publishability_contract':
        return fail('delta_shortlist_handoff: expected copied_from_publishability_contract')
    if status['paired_ranking_interpretation_handoff'] != 'copied_from_proxy_rank_interpretation_contract':
        return fail('paired_ranking_interpretation_handoff: expected copied_from_proxy_rank_interpretation_contract')
    if status['matching_state_interpretation_handoff'] != 'copied_from_proxy_matching_interpretation_contract':
        return fail('matching_state_interpretation_handoff: expected copied_from_proxy_matching_interpretation_contract')
    if status['turnover_tempo_interpretation_handoff'] != 'copied_from_proxy_turnover_tempo_contract':
        return fail('turnover_tempo_interpretation_handoff: expected copied_from_proxy_turnover_tempo_contract')
    if status['world_semantics_interpretation_handoff'] != 'copied_from_sq012_contract':
        return fail('world_semantics_interpretation_handoff: expected copied_from_sq012_contract')
    if status['compact_decision_bundle'] != 'copied_from_standing_contract':
        return fail('compact_decision_bundle: expected copied_from_standing_contract')

    if seed['canonicalization_planner_contract'] != handoff:
        return fail('canonicalization_planner_contract must copy the standing benchmark handoff exactly')
    if seed['winner_triage_handoff'] != winner_handoff:
        return fail('winner_triage_handoff must copy the standing benchmark winner-triage handoff exactly')
    if seed['delta_shortlist_handoff'] != delta_handoff:
        return fail('delta_shortlist_handoff must copy the standing benchmark delta shortlist handoff exactly')
    if seed['paired_ranking_interpretation_handoff'] != rank_handoff:
        return fail('paired_ranking_interpretation_handoff must copy the standing benchmark paired-ranking interpretation handoff exactly')
    if seed['matching_state_interpretation_handoff'] != matching_handoff:
        return fail('matching_state_interpretation_handoff must copy the standing benchmark matching-state interpretation handoff exactly')
    if seed['turnover_tempo_interpretation_handoff'] != turnover_interpretation_handoff:
        return fail('turnover_tempo_interpretation_handoff must copy the standing benchmark turnover-tempo interpretation handoff exactly')
    if seed['world_semantics_interpretation_handoff'] != world_semantics_interpretation_handoff:
        return fail('world_semantics_interpretation_handoff must copy the standing benchmark world-semantics interpretation handoff exactly')

    if seed['compact_decision_bundle'] != decision:
        return fail('compact_decision_bundle must copy the standing decision contract exactly')

    occ_rows = seed['occupancy_accounting_contract']['policy_rows']
    tempo_rows = seed['turnover_tempo_contract']['policy_rows']
    rank_rows = seed['paired_ranking_views_contract']['leaderboard_rows']
    if len(occ_rows) != len(tempo_rows) or len(occ_rows) != len(rank_rows):
        return fail('template policy rows should align across sections')
    if {row['policy'] for row in occ_rows} != {TEMPLATE_POLICY}:
        return fail('occupancy template should use one placeholder policy row')
    if {row['policy'] for row in tempo_rows} != {TEMPLATE_POLICY}:
        return fail('tempo template should use one placeholder policy row')
    if {row['policy'] for row in rank_rows} != {TEMPLATE_POLICY}:
        return fail('ranking template should use one placeholder policy row')

    for row in occ_rows:
        if any(row[field] is not None for field in ['aggregate_avg_payoff', 'matched_round_share', 'dead_round_share', 'in_match_avg_payoff']):
            return fail('occupancy template should leave measured fields null')
    for row in tempo_rows:
        if row['avg_match_length'] is not None or row['delay_or_search_dead_time'] is not None:
            return fail('tempo template should leave measured fields null')
    for row in rank_rows:
        if any(row[field] is not None for field in ['aggregate_rank', 'in_match_rank', 'aggregate_avg_payoff', 'in_match_avg_payoff']):
            return fail('ranking template should leave measured fields null')

    print('rematch-world-benchmark-seed: ok (seed scaffold preserves one-artifact benchmark shape)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
