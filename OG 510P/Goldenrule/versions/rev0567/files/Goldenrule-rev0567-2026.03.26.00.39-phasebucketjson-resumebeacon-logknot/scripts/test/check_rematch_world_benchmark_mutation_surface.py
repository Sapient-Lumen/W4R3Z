#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_mutation_surface_snapshot_20260316.json'
SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_mutation_surface.schema.json'
GUARD_PATH = ROOT / 'scripts' / 'tools' / 'rematch_world_benchmark_mutation_guard.py'
SEED_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_seed.json'
DECISION_CONTRACT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_decision_contract_snapshot_20260316.json'


def fail(msg: str) -> int:
    print(f'rematch-world-benchmark-mutation-surface: {msg}', file=sys.stderr)
    return 1


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding='utf-8'))


def load_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'could not load {module_name} from {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_synthetic_filled(seed: dict, decision: dict) -> dict:
    candidate = copy.deepcopy(seed)
    candidate['artifact_state'] = 'filled_benchmark'
    candidate['benchmark_id'] = 'endogenous_rematch_world_benchmark_demo_fill'
    candidate['section_status']['world_semantics_contract'] = 'filled'
    candidate['section_status']['matching_state_contract'] = 'filled'
    candidate['section_status']['occupancy_accounting_contract'] = 'filled'
    candidate['section_status']['turnover_tempo_contract'] = 'filled'
    candidate['section_status']['paired_ranking_views_contract'] = 'filled'

    candidate['world_semantics_contract'] = {
        'world_name': 'demo_world',
        'role_assignment_policy': 'roles alternate deterministically by rematch count parity',
        'asymmetry_trigger_policy': 'emit role-swapped companion runs whenever role payoffs are not guaranteed symmetric',
        'rematch_state_carry_policy': 'cooperation history persists across partnership continuations',
        'rematch_state_reset_policy': 'new partner identity resets partnership-local memory',
        'role_swapped_companion_policy': 'publish a swapped-role companion suite next to the primary run',
    }
    candidate['matching_state_contract'] = {
        'rematch_delay_rounds': 2,
        'matching_efficiency_model': 'search dead time is reported separately from in-match payoff',
        'search_state_fields': ['searching_round_share', 'search_wait_rounds_avg'],
        'matched_state_fields': ['matched_round_share', 'current_match_length'],
        'comparability_note': 'aggregate payoff and in-match payoff remain paired so occupancy effects stay visible',
    }
    candidate['occupancy_accounting_contract']['policy_rows'] = [
        {
            'policy': 'always_c',
            'aggregate_avg_payoff': 2.1,
            'matched_round_share': 0.81,
            'dead_round_share': 0.19,
            'in_match_avg_payoff': 2.59,
        },
        {
            'policy': 'CCDDE',
            'aggregate_avg_payoff': 2.35,
            'matched_round_share': 0.84,
            'dead_round_share': 0.16,
            'in_match_avg_payoff': 2.80,
        },
    ]
    candidate['turnover_tempo_contract']['policy_rows'] = [
        {
            'policy': 'always_c',
            'avg_match_length': 7.4,
            'delay_or_search_dead_time': 1.2,
            'turnover_metric_label': 'avg_match_length',
        },
        {
            'policy': 'CCDDE',
            'avg_match_length': 8.1,
            'delay_or_search_dead_time': 1.1,
            'turnover_metric_label': 'avg_match_length',
        },
    ]
    candidate['paired_ranking_views_contract']['leaderboard_rows'] = [
        {
            'policy': 'CCDDE',
            'aggregate_rank': 1,
            'in_match_rank': 1,
            'aggregate_avg_payoff': 2.35,
            'in_match_avg_payoff': 2.80,
        },
        {
            'policy': 'always_c',
            'aggregate_rank': 2,
            'in_match_rank': 2,
            'aggregate_avg_payoff': 2.1,
            'in_match_avg_payoff': 2.59,
        },
    ]
    candidate['compact_decision_bundle'] = copy.deepcopy(decision)
    return candidate


def main() -> int:
    if not REPORT_PATH.exists():
        return fail(f'missing {REPORT_PATH.relative_to(ROOT)}')
    if not SCHEMA_PATH.exists():
        return fail(f'missing {SCHEMA_PATH.relative_to(ROOT)}')
    report = load_json(REPORT_PATH)
    schema = load_json(SCHEMA_PATH)

    try:
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.validate(report, schema)
    except jsonschema.ValidationError as exc:
        return fail(f'schema validation failed: {exc.message}')
    except jsonschema.SchemaError as exc:
        return fail(f'invalid schema: {exc.message}')

    if report['status_counts']['mutable_prefix_count'] != 12:
        return fail('expected 12 mutable prefixes')
    if report['status_counts']['frozen_prefix_count'] != 26:
        return fail('expected 26 frozen prefixes')
    if report['status_counts']['allowed_decision_null_count'] != 3:
        return fail('expected 3 allowed decision nulls')

    prefixes = [row['prefix'] for row in report['mutable_prefix_rows']]
    if 'compact_decision_bundle' in prefixes:
        return fail('compact_decision_bundle must remain frozen')
    if 'canonicalization_planner_contract' in prefixes:
        return fail('canonicalization_planner_contract must remain frozen')
    if 'winner_triage_handoff' in prefixes:
        return fail('winner_triage_handoff must remain frozen')
    if 'delta_shortlist_handoff' in prefixes:
        return fail('delta_shortlist_handoff must remain frozen')
    if 'paired_ranking_interpretation_handoff' in prefixes:
        return fail('paired_ranking_interpretation_handoff must remain frozen')
    if 'matching_state_interpretation_handoff' in prefixes:
        return fail('matching_state_interpretation_handoff must remain frozen')
    if 'turnover_tempo_interpretation_handoff' in prefixes:
        return fail('turnover_tempo_interpretation_handoff must remain frozen')
    if 'world_semantics_interpretation_handoff' in prefixes:
        return fail('world_semantics_interpretation_handoff must remain frozen')
    if 'world_semantics_contract' not in prefixes:
        return fail('expected world_semantics_contract in mutable prefixes')

    guard = load_module(GUARD_PATH, 'rematch_world_benchmark_mutation_guard')
    seed = load_json(SEED_PATH)
    decision = load_json(DECISION_CONTRACT_PATH)

    seed_summary = guard.inspect_candidate_mutations(seed, seed, decision)
    if not seed_summary['mutation_surface_ok']:
        return fail('seed should not violate the edit surface')
    if seed_summary['status_counts']['forbidden_changed_path_count'] != 0:
        return fail('seed should have zero forbidden changed paths')
    if seed_summary['completion_ready']:
        return fail('seed should not be completion ready')

    filled = build_synthetic_filled(seed, decision)
    filled_summary = guard.inspect_candidate_mutations(filled, seed, decision)
    if not filled_summary['mutation_surface_ok']:
        return fail('synthetic filled benchmark should stay inside the edit surface')
    if not filled_summary['completion_ready']:
        return fail('synthetic filled benchmark should be completion ready')
    if filled_summary['status_counts']['forbidden_changed_path_count'] != 0:
        return fail('synthetic filled benchmark should have zero forbidden changed paths')

    drift = copy.deepcopy(filled)
    drift['compact_decision_bundle']['delay_contract']['headline_findings'][0] = 'drifted headline'
    drift_summary = guard.inspect_candidate_mutations(drift, seed, decision)
    if drift_summary['mutation_surface_ok']:
        return fail('decision bundle drift should violate the edit surface')
    if drift_summary['status_counts']['forbidden_changed_path_count'] < 1:
        return fail('expected at least one forbidden changed path under compact_decision_bundle drift')

    handoff_drift = copy.deepcopy(filled)
    handoff_drift['canonicalization_planner_contract']['zero_noise_dispatch_contract']['ordered_rule_count'] = 999
    handoff_drift_summary = guard.inspect_candidate_mutations(handoff_drift, seed, decision)
    if handoff_drift_summary['mutation_surface_ok']:
        return fail('canonicalization planner drift should violate the edit surface')
    if handoff_drift_summary['status_counts']['forbidden_changed_path_count'] < 1:
        return fail('expected at least one forbidden changed path under canonicalization_planner_contract drift')

    winner_handoff_drift = copy.deepcopy(filled)
    winner_handoff_drift['winner_triage_handoff']['uncertified_panel_rows'][0]['leader_margin_ci_high'] = 9.999999
    winner_handoff_drift_summary = guard.inspect_candidate_mutations(winner_handoff_drift, seed, decision)
    if winner_handoff_drift_summary['mutation_surface_ok']:
        return fail('winner triage handoff drift should violate the edit surface')
    if winner_handoff_drift_summary['status_counts']['forbidden_changed_path_count'] < 1:
        return fail('expected at least one forbidden changed path under winner_triage_handoff drift')

    delta_handoff_drift = copy.deepcopy(filled)
    delta_handoff_drift['delta_shortlist_handoff']['primary_shortlist_rows'][0]['shared_core_anchor_delta'] = 0.12345
    delta_handoff_drift_summary = guard.inspect_candidate_mutations(delta_handoff_drift, seed, decision)
    if delta_handoff_drift_summary['mutation_surface_ok']:
        return fail('delta shortlist handoff drift should violate the edit surface')
    if delta_handoff_drift_summary['status_counts']['forbidden_changed_path_count'] < 1:
        return fail('expected at least one forbidden changed path under delta_shortlist_handoff drift')

    rank_handoff_drift = copy.deepcopy(filled)
    rank_handoff_drift['paired_ranking_interpretation_handoff']['rank_disagreement_summary']['largest_disagreement_panel']['pairwise_inversion_count'] = 999
    rank_handoff_drift_summary = guard.inspect_candidate_mutations(rank_handoff_drift, seed, decision)
    if rank_handoff_drift_summary['mutation_surface_ok']:
        return fail('paired-ranking interpretation handoff drift should violate the edit surface')
    if rank_handoff_drift_summary['status_counts']['forbidden_changed_path_count'] < 1:
        return fail('expected at least one forbidden changed path under paired_ranking_interpretation_handoff drift')

    matching_handoff_drift = copy.deepcopy(filled)
    matching_handoff_drift['matching_state_interpretation_handoff']['matching_state_contract_guidance']['required_search_state_fields'][0] = 'drifted_search_field'
    matching_handoff_drift_summary = guard.inspect_candidate_mutations(matching_handoff_drift, seed, decision)
    if matching_handoff_drift_summary['mutation_surface_ok']:
        return fail('matching-state interpretation handoff drift should violate the edit surface')
    if matching_handoff_drift_summary['status_counts']['forbidden_changed_path_count'] < 1:
        return fail('expected at least one forbidden changed path under matching_state_interpretation_handoff drift')

    turnover_interpretation_handoff_drift = copy.deepcopy(filled)
    turnover_interpretation_handoff_drift['turnover_tempo_interpretation_handoff']['turnover_tempo_contract_guidance']['required_policy_row_fields'][0] = 'drifted_turnover_field'
    turnover_interpretation_handoff_drift_summary = guard.inspect_candidate_mutations(turnover_interpretation_handoff_drift, seed, decision)
    if turnover_interpretation_handoff_drift_summary['mutation_surface_ok']:
        return fail('turnover-tempo interpretation handoff drift should violate the edit surface')
    if turnover_interpretation_handoff_drift_summary['status_counts']['forbidden_changed_path_count'] < 1:
        return fail('expected at least one forbidden changed path under turnover_tempo_interpretation_handoff drift')

    world_semantics_interpretation_handoff_drift = copy.deepcopy(filled)
    world_semantics_interpretation_handoff_drift['world_semantics_interpretation_handoff']['world_semantics_contract_guidance']['required_world_section_fields'][0] = 'drifted_world_field'
    world_semantics_interpretation_handoff_drift_summary = guard.inspect_candidate_mutations(world_semantics_interpretation_handoff_drift, seed, decision)
    if world_semantics_interpretation_handoff_drift_summary['mutation_surface_ok']:
        return fail('world-semantics interpretation handoff drift should violate the edit surface')
    if world_semantics_interpretation_handoff_drift_summary['status_counts']['forbidden_changed_path_count'] < 1:
        return fail('expected at least one forbidden changed path under world_semantics_interpretation_handoff drift')

    print('rematch-world-benchmark-mutation-surface: ok (12 mutable prefixes, 26 frozen prefixes, copied handoffs frozen)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
