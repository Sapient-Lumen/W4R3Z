#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PUBLICATION_CONTRACT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_world_publication_contract_snapshot_20260316.json'
DECISION_CONTRACT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_decision_contract_snapshot_20260316.json'
OUT_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_seed.json'

HANDOFF_TOOL_PATH = ROOT / 'scripts' / 'tools' / 'build_rematch_world_benchmark_canonicalization_handoff.py'
DELTA_HANDOFF_TOOL_PATH = ROOT / 'scripts' / 'tools' / 'build_rematch_world_benchmark_delta_shortlist_handoff.py'
WINNER_HANDOFF_TOOL_PATH = ROOT / 'scripts' / 'tools' / 'build_rematch_world_benchmark_winner_triage_handoff.py'
RANK_HANDOFF_TOOL_PATH = ROOT / 'scripts' / 'tools' / 'build_rematch_world_benchmark_paired_ranking_interpretation_handoff.py'
MATCHING_HANDOFF_TOOL_PATH = ROOT / 'scripts' / 'tools' / 'build_rematch_world_benchmark_matching_state_interpretation_handoff.py'
TURNOVER_INTERPRETATION_HANDOFF_TOOL_PATH = ROOT / 'scripts' / 'tools' / 'build_rematch_world_benchmark_turnover_tempo_interpretation_handoff.py'
WORLD_SEMANTICS_INTERPRETATION_HANDOFF_TOOL_PATH = ROOT / 'scripts' / 'tools' / 'build_rematch_world_benchmark_world_semantics_interpretation_handoff.py'


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'could not load module {name} from {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

SECTIONS = [
    'world_semantics_contract',
    'matching_state_contract',
    'occupancy_accounting_contract',
    'turnover_tempo_contract',
    'paired_ranking_views_contract',
    'compact_decision_bundle',
]
TEMPLATE_POLICY = 'TEMPLATE_replace_with_policy_id'


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding='utf-8'))


def build_seed() -> dict[str, object]:
    publication = load_json(PUBLICATION_CONTRACT_PATH)
    decision = load_json(DECISION_CONTRACT_PATH)
    handoff_tool = _load_module('build_rematch_world_benchmark_canonicalization_handoff', HANDOFF_TOOL_PATH)
    handoff = handoff_tool.build_handoff(handoff_tool.load_json(handoff_tool.BRIDGE_PATH))
    delta_handoff_tool = _load_module('build_rematch_world_benchmark_delta_shortlist_handoff', DELTA_HANDOFF_TOOL_PATH)
    delta_handoff = delta_handoff_tool.build_handoff(
        delta_handoff_tool.load_json(delta_handoff_tool.PUBLISHABILITY_PATH),
        delta_handoff_tool.load_json(delta_handoff_tool.DECISION_CONTRACT_PATH),
    )
    winner_handoff_tool = _load_module('build_rematch_world_benchmark_winner_triage_handoff', WINNER_HANDOFF_TOOL_PATH)
    winner_handoff = winner_handoff_tool.build_handoff(
        winner_handoff_tool.load_json(winner_handoff_tool.LIVE_PATH),
        winner_handoff_tool.load_json(winner_handoff_tool.WINNER_PATH),
        winner_handoff_tool.load_json(winner_handoff_tool.MATERIALITY_PATH),
        winner_handoff_tool.load_json(winner_handoff_tool.DECISION_CONTRACT_PATH),
    )
    rank_handoff_tool = _load_module('build_rematch_world_benchmark_paired_ranking_interpretation_handoff', RANK_HANDOFF_TOOL_PATH)
    rank_handoff = rank_handoff_tool.build_handoff(
        rank_handoff_tool.load_json(rank_handoff_tool.OCCUPANCY_PATH),
        rank_handoff_tool.load_json(rank_handoff_tool.TURNOVER_PATH),
        rank_handoff_tool.load_json(rank_handoff_tool.RANK_PATH),
    )
    matching_handoff_tool = _load_module('build_rematch_world_benchmark_matching_state_interpretation_handoff', MATCHING_HANDOFF_TOOL_PATH)
    matching_handoff = matching_handoff_tool.build_handoff(
        matching_handoff_tool.load_json(matching_handoff_tool.MATCHING_PATH),
        matching_handoff_tool.load_json(matching_handoff_tool.OCCUPANCY_PATH),
    )
    turnover_interpretation_handoff_tool = _load_module('build_rematch_world_benchmark_turnover_tempo_interpretation_handoff', TURNOVER_INTERPRETATION_HANDOFF_TOOL_PATH)
    turnover_interpretation_handoff = turnover_interpretation_handoff_tool.build_handoff(
        turnover_interpretation_handoff_tool.load_json(turnover_interpretation_handoff_tool.TURNOVER_PATH),
    )
    world_semantics_interpretation_handoff_tool = _load_module('build_rematch_world_benchmark_world_semantics_interpretation_handoff', WORLD_SEMANTICS_INTERPRETATION_HANDOFF_TOOL_PATH)
    world_semantics_interpretation_handoff = world_semantics_interpretation_handoff_tool.build_handoff(
        world_semantics_interpretation_handoff_tool.load_json(world_semantics_interpretation_handoff_tool.PUBLICATION_PATH),
        world_semantics_interpretation_handoff_tool.ROLE_NOTE_PATH.read_text(encoding='utf-8'),
        world_semantics_interpretation_handoff_tool.INHERITOR_BRIEF_PATH.read_text(encoding='utf-8'),
    )

    return {
        'artifact_state': 'seed_template',
        'artifact_version': 1,
        'benchmark_id': 'TEMPLATE_first_endogenous_rematch_world_benchmark',
        'benchmark_kind': 'endogenous_rematch_world_benchmark',
        'publication_contract_path': publication['analysis_script'].replace(
            'scripts/report/build_rematch_world_publication_contract_snapshot.py',
            'artifacts/reports/rematch_world_publication_contract_snapshot_20260316.json',
        ),
        'publication_contract_schema_path': publication['schema_path'],
        'publication_contract_validator_path': publication['validator_path'],
        'decision_contract_path': 'artifacts/reports/rematch_decision_contract_snapshot_20260316.json',
        'decision_contract_schema_path': publication['publication_contract_shape']['decision_contract_schema_path'],
        'decision_contract_validator_path': publication['publication_contract_shape']['decision_contract_validator_path'],
        'required_sections': list(publication['publication_contract_shape']['required_sections']),
        'recommended_fill_order': list(SECTIONS),
        'section_status': {
            'canonicalization_planner_contract': 'copied_from_bridge_contract',
            'winner_triage_handoff': 'copied_from_proxy_winner_triage_contract',
            'delta_shortlist_handoff': 'copied_from_publishability_contract',
            'paired_ranking_interpretation_handoff': 'copied_from_proxy_rank_interpretation_contract',
            'matching_state_interpretation_handoff': 'copied_from_proxy_matching_interpretation_contract',
            'turnover_tempo_interpretation_handoff': 'copied_from_proxy_turnover_tempo_contract',
            'world_semantics_interpretation_handoff': 'copied_from_sq012_contract',
            'world_semantics_contract': 'pending_fill',
            'matching_state_contract': 'pending_fill',
            'occupancy_accounting_contract': 'pending_fill',
            'turnover_tempo_contract': 'pending_fill',
            'paired_ranking_views_contract': 'pending_fill',
            'compact_decision_bundle': 'copied_from_standing_contract',
        },
        'canonicalization_planner_contract': handoff,
        'winner_triage_handoff': winner_handoff,
        'delta_shortlist_handoff': delta_handoff,
        'paired_ranking_interpretation_handoff': rank_handoff,
        'matching_state_interpretation_handoff': matching_handoff,
        'turnover_tempo_interpretation_handoff': turnover_interpretation_handoff,
        'world_semantics_interpretation_handoff': world_semantics_interpretation_handoff,
        'world_semantics_contract': {
            'world_name': 'TEMPLATE_replace_with_world_name',
            'role_assignment_policy': 'TEMPLATE_declare_how_roles_are_assigned_and_swapped',
            'asymmetry_trigger_policy': 'TEMPLATE_declare_when_role_swapped_companion_runs_are_required',
            'rematch_state_carry_policy': 'TEMPLATE_declare_which_state_persists_across_partnership_continuations',
            'rematch_state_reset_policy': 'TEMPLATE_declare_when_new_partnerships_reset_state',
            'role_swapped_companion_policy': 'TEMPLATE_required_when_asymmetry_is_in_play',
        },
        'matching_state_contract': {
            'rematch_delay_rounds': None,
            'matching_efficiency_model': 'TEMPLATE_describe_search_dead_time_separately_from_market_thickness',
            'search_state_fields': ['searching_round_share', 'search_wait_rounds_avg'],
            'matched_state_fields': ['matched_round_share', 'current_match_length'],
            'comparability_note': 'TEMPLATE_explain_how_search_dead_time_is_reported_separately_from_matched_payoff',
        },
        'occupancy_accounting_contract': {
            'policy_rows': [
                {
                    'policy': TEMPLATE_POLICY,
                    'aggregate_avg_payoff': None,
                    'matched_round_share': None,
                    'dead_round_share': None,
                    'in_match_avg_payoff': None,
                }
            ]
        },
        'turnover_tempo_contract': {
            'policy_rows': [
                {
                    'policy': TEMPLATE_POLICY,
                    'avg_match_length': None,
                    'delay_or_search_dead_time': None,
                    'turnover_metric_label': 'TEMPLATE_choose_avg_match_length_or_equivalent_turnover_metric',
                }
            ]
        },
        'paired_ranking_views_contract': {
            'leaderboard_rows': [
                {
                    'policy': TEMPLATE_POLICY,
                    'aggregate_rank': None,
                    'in_match_rank': None,
                    'aggregate_avg_payoff': None,
                    'in_match_avg_payoff': None,
                }
            ]
        },
        'compact_decision_bundle': decision,
    }


def main() -> int:
    seed = build_seed()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(seed, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(OUT_PATH.relative_to(ROOT).as_posix())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
