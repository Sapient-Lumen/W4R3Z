from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.cpp_trace import check_public_traces_with_cpp
from src.muc5.payoff import aggregate_payoff_rows, write_csv
from src.muc5.promotion import PromotionGateConfig, audit_promotion_rows, strategy_standings
from src.muc5.public_agents import make_public_agent
from src.muc5.public_payoff import build_public_payoff_rows
from src.muc5.replay import record_public_decision_trace, replay_public_decision_trace, write_trace_jsonl
from src.muc5.statgate import audit_statistical_gate, pairwise_stat_rows, statistical_standings
from src.muc5.strategy_sets import mulligan_policy_gate_bundles

REV = "rev0023"
DATA = ROOT / "data"


def same_shell_policy_summary(rows):
    scores = defaultdict(list)
    terminal_wins = defaultdict(list)
    for row in rows:
        for side in (0, 1):
            strategy = str(row[f"strategy{side}"])
            bits = strategy.split("_")
            policy = bits[-1]
            shell = "_".join(bits[:-1])
            scores[(shell, policy)].append(float(row[f"p{side}_score"]))
            terminal_wins[(shell, policy)].append(float(row[f"p{side}_terminal_win"]))
    out = []
    for (shell, policy), vals in sorted(scores.items()):
        wins = terminal_wins[(shell, policy)]
        out.append({
            "shell": shell,
            "policy_suffix": policy,
            "games": len(vals),
            "mean_score_draw_half": sum(vals) / len(vals) if vals else 0.0,
            "terminal_win_rate": sum(wins) / len(wins) if wins else 0.0,
        })
    out.sort(key=lambda r: (r["shell"], -r["mean_score_draw_half"], r["policy_suffix"]))
    return out


def trace_specs(strategies):
    return [
        (0, 1, 20, 0),
        (2, 3, 20, 1),
        (4, 5, 40, 0),
        (6, 7, 40, 1),
        (8, 0, 20, 1),
        (1, 8, 40, 0),
    ]


def main() -> None:
    DATA.mkdir(exist_ok=True)
    strategies = mulligan_policy_gate_bundles(DATA / "seed_decks.json")
    rows = build_public_payoff_rows(strategies, simulator_revision=REV, reps=1, base_seed=2307000, max_decisions=560)
    write_csv(DATA / f"{REV}_mulligan_policy_gate_games.csv", rows)
    aggregate = aggregate_payoff_rows(rows)
    write_csv(DATA / f"{REV}_mulligan_policy_gate_aggregate.csv", aggregate)
    standings = strategy_standings(rows)
    write_csv(DATA / f"{REV}_mulligan_policy_gate_standings.csv", standings)
    shell_summary = same_shell_policy_summary(rows)
    write_csv(DATA / f"{REV}_mulligan_policy_gate_same_shell.csv", shell_summary)
    pairwise = pairwise_stat_rows(rows, min_games_for_claim=4)
    stat_stand = statistical_standings(rows, min_games_for_claim=24)
    write_csv(DATA / f"{REV}_mulligan_policy_gate_pairwise.csv", pairwise)
    write_csv(DATA / f"{REV}_mulligan_policy_gate_stat_standings.csv", stat_stand)
    stat_gate = audit_statistical_gate(rows, stat_stand, pairwise, min_raw_rows=len(rows), max_truncation_rate=0.12)

    traces = []
    replay_results = []
    for t, (i, j, life, starting_player) in enumerate(trace_specs(strategies)):
        left = strategies[i]
        right = strategies[j]
        trace = record_public_decision_trace(
            left.deck,
            right.deck,
            make_public_agent(left.agent_name),
            make_public_agent(right.agent_name),
            seed=2308000 + t,
            transition_seed=2309000 + t,
            agent_seed=2310000 + t,
            starting_player=starting_player,
            starting_life=life,
            max_decisions=560,
            mulligan_policies=(left.mulligan_policy, right.mulligan_policy),
        )
        trace["trace_id"] = f"{REV}_mulligan_gate_trace_{t:03d}"
        traces.append(trace)
        replay_results.append(replay_public_decision_trace(trace).as_dict())
    write_trace_jsonl(traces, DATA / f"{REV}_mulligan_policy_gate_replay_traces.jsonl")
    (DATA / f"{REV}_mulligan_policy_gate_replay_results.json").write_text(json.dumps(replay_results, indent=2, sort_keys=True), encoding="utf-8")
    cpp_summary, cpp_rows = check_public_traces_with_cpp(traces, revision=REV)
    write_csv(DATA / f"{REV}_mulligan_policy_gate_cpp_trace_rows.csv", [r.as_dict() for r in cpp_rows])
    (DATA / f"{REV}_mulligan_policy_gate_cpp_trace_summary.json").write_text(json.dumps(cpp_summary.as_dict(), indent=2, sort_keys=True), encoding="utf-8")

    promo = audit_promotion_rows(
        rows,
        replay_results=replay_results,
        config=PromotionGateConfig(simulator_revision=REV, min_rows=len(rows), max_truncation_rate=0.12, min_replay_traces=len(traces)),
    )
    policies = sorted({str(s.mulligan_policy) for s in strategies})
    summary = {
        "revision": REV,
        "strategy_count": len(strategies),
        "games": len(rows),
        "aggregate_rows": len(aggregate),
        "mulligan_policies": policies,
        "promotion_gate": promo.as_dict(),
        "statistical_gate": stat_gate.as_dict(),
        "cpp_trace_summary": cpp_summary.as_dict(),
        "replay_passed": sum(1 for r in replay_results if r.get("passed") is True),
        "replay_count": len(replay_results),
        "top_standings": standings[:8],
        "same_shell_policy_summary": shell_summary,
    }
    (DATA / f"{REV}_mulligan_policy_gate_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not promo.passed or not stat_gate.passed or cpp_summary.mismatches != 0 or cpp_summary.skipped_events != 0 or cpp_summary.python_replay_errors != 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
