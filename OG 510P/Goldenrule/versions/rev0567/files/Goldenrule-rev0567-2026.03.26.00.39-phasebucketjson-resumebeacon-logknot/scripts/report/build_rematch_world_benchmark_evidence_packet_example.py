#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_evidence_packet.json'


def build_packet() -> dict[str, object]:
    return {
        'packet_version': '2026-03-16.rematch_world_benchmark_evidence_packet.v1',
        'packet_intent': 'distill one tiny retained evidence packet from a rematch-world run, then compile it into the standard fill patch',
        'scratch_retention_note': 'raw run traces and bulky intermediate tables may remain scratch-only once these distilled facts are retained',
        'source_run_label': 'synthetic_rematch_world_example_run_v1',
        'decision_contract_path': 'artifacts/reports/rematch_decision_contract_snapshot_20260316.json',
        'benchmark_id': 'synthetic_rematch_world_example_benchmark_v1',
        'world_semantics_observations': {
            'world_name': 'synthetic_pairwise_search_world_v1',
            'role_assignment_policy': 'assign roles by ordered policy pair and emit a companion run whenever the payoff function is role-sensitive',
            'role_swapped_companion_policy': 'require one role-swapped companion run for each ordered pair whenever role-sensitive payoffs are enabled',
            'asymmetry_trigger_policy': 'treat payoff asymmetry as active whenever role order changes realized payoffs or continuation probabilities',
            'rematch_state_carry_policy': 'carry forward bilateral continuation state inside the same partnership but not unmatched search history',
            'rematch_state_reset_policy': 'reset bilateral continuation state whenever a policy forms a new partnership after search',
        },
        'matching_observations': {
            'comparability_note': 'report search dead time separately from matched payoff so aggregate averages span all rounds while in-match averages span matched rounds only',
            'matched_state_fields': ['matched_round_share', 'current_match_length'],
            'matching_efficiency_model': 'count search dead time as unmatched waiting rounds and do not fold it into average match length or market-thickness summaries',
            'rematch_delay_rounds': 2,
            'search_state_fields': ['searching_round_share', 'search_wait_rounds_avg'],
        },
        'occupancy_policy_rows': [
            {
                'policy': 'reciprocal_anchor',
                'aggregate_avg_payoff': 2.31,
                'dead_round_share': 0.11,
                'in_match_avg_payoff': 2.59,
                'matched_round_share': 0.89,
            },
            {
                'policy': 'search_hawk',
                'aggregate_avg_payoff': 1.84,
                'dead_round_share': 0.24,
                'in_match_avg_payoff': 2.42,
                'matched_round_share': 0.76,
            },
        ],
        'turnover_policy_rows': [
            {
                'policy': 'reciprocal_anchor',
                'avg_match_length': 6.7,
                'delay_or_search_dead_time': 1.2,
                'turnover_metric_label': 'avg_match_length',
            },
            {
                'policy': 'search_hawk',
                'avg_match_length': 4.1,
                'delay_or_search_dead_time': 2.6,
                'turnover_metric_label': 'avg_match_length',
            },
        ],
        'leaderboard_rows': [
            {
                'policy': 'reciprocal_anchor',
                'aggregate_avg_payoff': 2.31,
                'aggregate_rank': 1,
                'in_match_avg_payoff': 2.59,
                'in_match_rank': 1,
            },
            {
                'policy': 'search_hawk',
                'aggregate_avg_payoff': 1.84,
                'aggregate_rank': 2,
                'in_match_avg_payoff': 2.42,
                'in_match_rank': 2,
            },
        ],
    }


def main() -> int:
    packet = build_packet()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(packet, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(f'rematch-world-benchmark-evidence-packet-example: wrote {OUT.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
