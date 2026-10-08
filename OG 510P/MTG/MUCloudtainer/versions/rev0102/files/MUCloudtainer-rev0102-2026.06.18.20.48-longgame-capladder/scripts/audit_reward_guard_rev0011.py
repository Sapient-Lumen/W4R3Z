from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.agents import HeuristicAgent, play_agent_game
from src.muc5.deckspace import DeckVector
from src.muc5.mulligan import POLICY_LAND_BAND
from src.muc5.reward_guard import audit_reward_packet, audit_payoff_like_row, reward_packet_from_state, trajectory_diagnostics


def main() -> None:
    deck = DeckVector(40, 24, 6, 4, 3, 3)
    terminal_state, terminal_result = play_agent_game(
        deck,
        deck,
        HeuristicAgent(),
        HeuristicAgent(),
        seed=314,
        starting_life=20,
        max_decisions=500,
        mulligan_policy=POLICY_LAND_BAND,
        validate_actions=False,
        record_log=False,
    )
    trunc_state, trunc_result = play_agent_game(
        deck,
        deck,
        HeuristicAgent(),
        HeuristicAgent(),
        seed=315,
        starting_life=40,
        max_decisions=1,
        mulligan_policy=POLICY_LAND_BAND,
        validate_actions=False,
        record_log=False,
    )
    rows = []
    packet_results = []
    for label, state, result in [
        ("ordinary_game", terminal_state, terminal_result),
        ("forced_truncation", trunc_state, trunc_result),
    ]:
        diag = trajectory_diagnostics(state, decisions=result.decisions)
        for perspective in (0, 1):
            packet = reward_packet_from_state(state, perspective)
            training_ok, training_errors = audit_reward_packet(packet)
            reporting_ok, reporting_errors = audit_reward_packet(packet, allow_truncation_training_reward=True)
            row = {"case": label, **packet.as_dict(), **{f"diag_{k}": v for k, v in diag.items()}}
            rows.append(row)
            packet_results.append(
                {
                    "case": label,
                    "perspective": perspective,
                    "training_ok_without_truncation_optin": training_ok,
                    "training_errors": list(training_errors),
                    "reporting_ok_with_optin": reporting_ok,
                    "reporting_errors": list(reporting_errors),
                }
            )

    out_csv = ROOT / "data" / "rev0011_reward_guard_packets.csv"
    fieldnames = sorted({k for row in rows for k in row})
    with out_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    payoff_rows_checked = 0
    payoff_errors = []
    payoff_path = ROOT / "data" / "rev0009_mulligan_bundle_payoff_games.csv"
    if payoff_path.exists():
        for row in csv.DictReader(payoff_path.open()):
            payoff_rows_checked += 1
            ok, errors = audit_payoff_like_row(row)
            if not ok:
                payoff_errors.append({"row": payoff_rows_checked, "errors": list(errors)})
                if len(payoff_errors) >= 10:
                    break

    summary = {
        "revision": "rev0011",
        "packet_rows": len(rows),
        "packet_results": packet_results,
        "payoff_rows_checked": payoff_rows_checked,
        "payoff_errors_sample": payoff_errors,
        "payoff_rows_passed": not payoff_errors,
        "forced_truncation_detected": trunc_state.loss_reason == "max_decisions_reached",
        "ordinary_game_loss_reason": terminal_state.loss_reason,
        "note": "Truncation is allowed for reporting but requires explicit opt-in before becoming a training reward.",
    }
    out_summary = ROOT / "data" / "rev0011_reward_guard_summary.json"
    out_summary.write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    if payoff_errors or not summary["forced_truncation_detected"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
