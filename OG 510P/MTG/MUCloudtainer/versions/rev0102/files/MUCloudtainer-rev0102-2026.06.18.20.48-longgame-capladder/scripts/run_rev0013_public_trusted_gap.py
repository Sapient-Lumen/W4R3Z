from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.agents import make_agent, play_agent_game, play_public_agent_game
from src.muc5.mulligan import POLICY_LAND_BAND, RuleMulliganAgent
from src.muc5.payoff import load_seed_decks, write_csv
from src.muc5.public_agents import make_public_agent


def score(winner, player: int) -> float:
    if winner is None:
        return 0.5
    return 1.0 if winner == player else 0.0


def main() -> None:
    data = ROOT / "data"
    decks = load_seed_decks(data / "seed_decks.json")
    deck_names = [
        "forty_force_jace_pressure",
        "forty_overlord_impending",
        "sixty_counterwall_jace",
        "sixty_overlord_heavy",
    ]
    comparisons = [
        ("heuristic_exact", "heuristic", "legacy_heuristic"),
        ("heuristic_profile", "heuristic", "heuristic"),
        ("counter_happy_profile", "counter_happy", "counter_happy"),
        ("threat_rush_profile", "threat_rush", "threat_rush"),
    ]
    rows = []
    k = 0
    for life in (20, 40):
        for left_name in deck_names:
            for right_name in deck_names:
                for label, trusted_name, public_name in comparisons:
                    for starting_player in (0, 1):
                        seed = 91300 + k
                        trusted_state, trusted_result = play_agent_game(
                            decks[left_name],
                            decks[right_name],
                            make_agent(trusted_name),
                            make_agent(trusted_name),
                            seed=seed,
                            starting_player=starting_player,
                            starting_life=life,
                            max_decisions=400,
                            mulligan_policy=None,
                            mulligan_agents=(RuleMulliganAgent(POLICY_LAND_BAND), RuleMulliganAgent(POLICY_LAND_BAND)),
                            record_log=False,
                        )
                        public_state, public_result = play_public_agent_game(
                            decks[left_name],
                            decks[right_name],
                            make_public_agent(public_name),
                            make_public_agent(public_name),
                            seed=seed,
                            starting_player=starting_player,
                            starting_life=life,
                            max_decisions=400,
                            mulligan_policy=None,
                            mulligan_agents=(RuleMulliganAgent(POLICY_LAND_BAND), RuleMulliganAgent(POLICY_LAND_BAND)),
                            record_log=False,
                        )
                        rows.append(
                            {
                                "comparison": label,
                                "deck0": left_name,
                                "deck1": right_name,
                                "trusted_agent": trusted_name,
                                "public_agent": public_name,
                                "starting_life": life,
                                "starting_player": starting_player,
                                "seed": seed,
                                "trusted_winner": "None" if trusted_result.winner is None else trusted_result.winner,
                                "public_winner": "None" if public_result.winner is None else public_result.winner,
                                "same_winner": trusted_result.winner == public_result.winner,
                                "trusted_loss_reason": trusted_result.loss_reason,
                                "public_loss_reason": public_result.loss_reason,
                                "same_loss_reason": trusted_result.loss_reason == public_result.loss_reason,
                                "trusted_decisions": trusted_result.decisions,
                                "public_decisions": public_result.decisions,
                                "decision_delta": public_result.decisions - trusted_result.decisions,
                                "trusted_p0_score": score(trusted_result.winner, 0),
                                "public_p0_score": score(public_result.winner, 0),
                                "p0_score_delta_public_minus_trusted": score(public_result.winner, 0) - score(trusted_result.winner, 0),
                            }
                        )
                        k += 1
    out_path = data / "rev0013_public_trusted_gap.csv"
    write_csv(out_path, rows)
    groups = {}
    for row in rows:
        groups.setdefault(row["comparison"], []).append(row)
    summary_rows = []
    for label, group in sorted(groups.items()):
        n = len(group)
        summary_rows.append(
            {
                "comparison": label,
                "rows": n,
                "same_winner_rate": sum(1 for r in group if str(r["same_winner"]) == "True") / n,
                "same_loss_reason_rate": sum(1 for r in group if str(r["same_loss_reason"]) == "True") / n,
                "mean_abs_decision_delta": sum(abs(int(r["decision_delta"])) for r in group) / n,
                "mean_p0_score_delta_public_minus_trusted": sum(float(r["p0_score_delta_public_minus_trusted"]) for r in group) / n,
            }
        )
    write_csv(data / "rev0013_public_trusted_gap_summary.csv", summary_rows)
    payload = {"revision": "rev0013", "rows": len(rows), "summary": summary_rows, "warning": "Gaps are diagnostics, not proof of leakage; public_profile agents are not byte-for-byte identical to old trusted agents except heuristic_exact."}
    (data / "rev0013_public_trusted_gap_summary.json").write_text(json.dumps(payload, indent=2, sort_keys=True))
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
