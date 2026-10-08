from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.deckspace import DeckVector
from src.muc5.mulligan import POLICY_KEEP_ALWAYS, POLICY_LAND_BAND
from src.muc5.payoff import StrategyBundle, aggregate_payoff_rows, write_csv
from src.muc5.public_payoff import build_public_payoff_rows
from src.muc5.promotion import PromotionGateConfig, audit_promotion_rows
from src.muc5.statgate import audit_statistical_gate, pairwise_stat_rows, statistical_standings

REV = "rev0015"


def main() -> None:
    strategies = [
        StrategyBundle("stall_wall_60", "stall_wall_60_no_threats", DeckVector(60, 34, 16, 10, 0, 0), "stall", POLICY_KEEP_ALWAYS),
        StrategyBundle("stall_jacewall_60", "stall_jacewall_60", DeckVector(60, 31, 16, 8, 5, 0), "stall", POLICY_LAND_BAND),
        StrategyBundle("threat_fast_40", "threat_fast_40", DeckVector(40, 20, 7, 4, 2, 7), "threat_rush", POLICY_LAND_BAND),
        StrategyBundle("counter_jace_40", "counter_jace_40", DeckVector(40, 21, 9, 5, 5, 0), "counter_happy", POLICY_LAND_BAND),
    ]
    # Low max_decisions is intentional: the point is to test that stall/truncation
    # is visible and fails strict promotion rather than quietly becoming a 0.5 reward.
    rows = build_public_payoff_rows(strategies, simulator_revision=REV, reps=2, base_seed=151900, max_decisions=160)
    data = ROOT / "data"
    write_csv(data / "rev0015_stall_adversary_games.csv", rows)
    write_csv(data / "rev0015_stall_adversary_aggregate.csv", aggregate_payoff_rows(rows))
    standings = statistical_standings(rows, min_games_for_claim=24)
    pair_rows = pairwise_stat_rows(rows, min_games_for_claim=4)
    write_csv(data / "rev0015_stall_adversary_standings.csv", standings)
    write_csv(data / "rev0015_stall_adversary_pairwise.csv", pair_rows)
    strict_promo = audit_promotion_rows(rows, replay_results=[], config=PromotionGateConfig(simulator_revision=REV, min_rows=len(rows), require_replay_sample=False, max_truncation_rate=0.00))
    relaxed_stat = audit_statistical_gate(rows, standings, pair_rows, min_raw_rows=len(rows), max_truncation_rate=0.80)
    truncation_games = sum(1 for r in rows if r.get("is_truncation"))
    stall_involved_truncations = sum(1 for r in rows if r.get("is_truncation") and ("stall" in str(r.get("strategy0")) or "stall" in str(r.get("strategy1"))))
    summary = {
        "revision": REV,
        "games": len(rows),
        "strategies": [s.as_dict() for s in strategies],
        "truncation_games": truncation_games,
        "stall_involved_truncations": stall_involved_truncations,
        "strict_promotion_gate_expected_to_fail": strict_promo.as_dict(),
        "relaxed_statistical_gate_for_diagnostics": relaxed_stat.as_dict(),
        "guard_detected_stall_truncation": truncation_games > 0 and not strict_promo.passed,
        "note": "This is an adversarial diagnostic, not a promotable payoff table. It should make truncation visible.",
    }
    (data / "rev0015_stall_adversary_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True))
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
