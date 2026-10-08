from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.cpp_trace import check_public_traces_with_cpp
from src.muc5.mulligan_counterfactual import (
    COUNTERFACTUAL_MODEL_NAME,
    counterfactual_model_path,
    counterfactual_training_rows_from_pairs,
    load_counterfactual_mulligan_agent,
    load_counterfactual_mulligan_model,
    save_counterfactual_mulligan_model,
    train_counterfactual_mulligan_model,
)
from src.muc5.payoff import aggregate_payoff_rows, load_seed_decks, write_csv
from src.muc5.promotion import PromotionGateConfig, audit_promotion_rows, strategy_standings
from src.muc5.public_agents import make_public_agent
from src.muc5.public_payoff import play_public_strategy_pair_row
from src.muc5.replay import record_public_decision_trace, replay_public_decision_trace, write_trace_jsonl
from src.muc5.statgate import audit_statistical_gate, pairwise_stat_rows, statistical_standings
from src.muc5.strategy_sets import counterfactual_mulligan_gate_bundles
from src.muc5.nochoice_segments import aggregate_nochoice_summaries, play_public_game_with_nochoice_audit

REV = "rev0029"
DATA = ROOT / "data"


def read_csv_dicts(path: Path) -> list[dict[str, object]]:
    with path.open(newline="") as f:
        return [dict(row) for row in csv.DictReader(f)]


def train_from_rev0028_pairs() -> tuple[dict[str, object], pd.DataFrame]:
    pair_path = DATA / "rev0028_opening_counterfactual_pairs.csv"
    if not pair_path.exists():
        raise FileNotFoundError("rev0028 counterfactual pairs are required; run scripts/run_rev0028_opening_counterfactual.py first")
    pairs = read_csv_dicts(pair_path)
    seed_decks = load_seed_decks(DATA / "seed_decks.json")
    deck_counts = {name: deck.counts() for name, deck in seed_decks.items()}
    training_rows = counterfactual_training_rows_from_pairs(pairs, deck_counts)
    model, metrics = train_counterfactual_mulligan_model(training_rows)
    save_counterfactual_mulligan_model(model, counterfactual_model_path())
    df = pd.DataFrame(training_rows)
    df.to_csv(DATA / "rev0029_counterfactual_mulligan_training_rows.csv", index=False)
    return metrics, df


def same_shell_policy_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    scores = defaultdict(list)
    wins = defaultdict(list)
    trunc = defaultdict(int)
    for row in rows:
        for side in (0, 1):
            strategy = str(row[f"strategy{side}"])
            shell, suffix = strategy.rsplit("_", 1)
            key = (shell, suffix)
            scores[key].append(float(row[f"p{side}_score"]))
            wins[key].append(float(row[f"p{side}_terminal_win"]))
            trunc[key] += 1 if str(row.get("is_truncation", "False")).lower() in {"true", "1"} else 0
    out = []
    for (shell, suffix), vals in sorted(scores.items()):
        out.append({
            "shell": shell,
            "policy_suffix": suffix,
            "games": len(vals),
            "mean_score_draw_half": sum(vals) / len(vals) if vals else 0.0,
            "terminal_win_rate": sum(wins[(shell, suffix)]) / len(wins[(shell, suffix)]) if wins[(shell, suffix)] else 0.0,
            "truncations": trunc[(shell, suffix)],
        })
    out.sort(key=lambda r: (r["shell"], -r["mean_score_draw_half"], r["policy_suffix"]))
    return out


def build_same_shell_payoff_rows(strategies) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    agent_cache = {}
    mulligan_cache = {}

    def cached_agent(name):
        if name not in agent_cache:
            agent_cache[name] = make_public_agent(name)
        return agent_cache[name]

    def cached_mulligan(policy):
        key = str(policy)
        if key not in mulligan_cache:
            from src.muc5.mulligan_ranker import make_mulligan_agent
            mulligan_cache[key] = make_mulligan_agent(policy)
        return mulligan_cache[key]

    by_shell = defaultdict(list)
    for bundle in strategies:
        shell, _suffix = bundle.strategy_id.rsplit("_", 1)
        by_shell[shell].append(bundle)
    k = 0
    for shell, bundles in sorted(by_shell.items()):
        for life in (20, 40):
            for i, left in enumerate(bundles):
                for j, right in enumerate(bundles):
                    for starting_player in (0, 1):
                        row = play_public_strategy_pair_row(
                            left,
                            right,
                            simulator_revision=REV,
                            seed=2902900 + k,
                            starting_player=starting_player,
                            starting_life=life,
                            max_decisions=560,
                            agent0=cached_agent(left.agent_name),
                            agent1=cached_agent(right.agent_name),
                            mulligan_agent0=cached_mulligan(left.mulligan_policy),
                            mulligan_agent1=cached_mulligan(right.mulligan_policy),
                        )
                        row["shell"] = shell
                        row["pair_index"] = f"{shell}:{i}:{j}"
                        row["rep"] = 0
                        rows.append(row)
                        k += 1
    return rows


def trace_specs(strategies):
    name_to_idx = {s.strategy_id: i for i, s in enumerate(strategies)}
    pairs = [
        ("fjace_code_cf", "fjace_code_outcome", 20, 0),
        ("fjace_code_cf", "fjace_code_business", 40, 1),
        ("overlord_threat_cf", "overlord_threat_outcome", 20, 1),
        ("overlord_threat_cf", "overlord_threat_band", 40, 0),
        ("wall_counter_cf", "wall_counter_outcome", 20, 0),
        ("wall_counter_cf", "wall_counter_pseudo", 40, 1),
        ("fjace_code_cf", "wall_counter_cf", 20, 0),
        ("overlord_threat_cf", "fjace_code_cf", 40, 1),
    ]
    return [(name_to_idx[a], name_to_idx[b], life, start) for a, b, life, start in pairs]


def run_nochoice_audit(strategies) -> tuple[list[dict[str, object]], dict[str, object]]:
    selected = strategies[:6]
    agent_cache = {s.agent_name: make_public_agent(s.agent_name) for s in selected}
    from src.muc5.mulligan_ranker import make_mulligan_agent
    mulligan_cache = {str(s.mulligan_policy): make_mulligan_agent(s.mulligan_policy) for s in selected}
    summaries = []
    k = 0
    for life in (20, 40):
        for i, left in enumerate(selected):
            right = selected[(i + 2) % len(selected)]
            for starting_player in (0, 1):
                _state, _result, summary = play_public_game_with_nochoice_audit(
                    left.deck,
                    right.deck,
                    agent_cache[left.agent_name],
                    agent_cache[right.agent_name],
                    game_id=f"rev0029_nochoice_{k:03d}",
                    seed=2909000 + k,
                    transition_seed=2909000 + k,
                    agent_seed=3909003 + k,
                    starting_player=starting_player,
                    starting_life=life,
                    max_decisions=560,
                    mulligan_agents=(mulligan_cache[str(left.mulligan_policy)], mulligan_cache[str(right.mulligan_policy)]),
                )
                summaries.append(summary)
                k += 1
    aggregate = aggregate_nochoice_summaries(summaries)
    return [s.as_dict() for s in summaries], aggregate.as_dict()


def main() -> None:
    DATA.mkdir(exist_ok=True)
    metrics, train_df = train_from_rev0028_pairs()
    loaded = load_counterfactual_mulligan_model()
    lint_agent = load_counterfactual_mulligan_agent()
    lint = {
        "agent_name": lint_agent.name,
        "model_id": loaded.model_id,
        "feature_count": len(loaded.feature_names),
        "fallback_mulligan": loaded.fallback_mulligan,
        "test_decision_accuracy_ties_count_as_correct": metrics.get("test_decision_accuracy_ties_count_as_correct"),
    }

    strategies = counterfactual_mulligan_gate_bundles(DATA / "seed_decks.json")
    rows = build_same_shell_payoff_rows(strategies)
    write_csv(DATA / "rev0029_counterfactual_mulligan_games.csv", rows)
    aggregate = aggregate_payoff_rows(rows)
    standings = strategy_standings(rows)
    same_shell = same_shell_policy_summary(rows)
    pairwise = pairwise_stat_rows(rows, min_games_for_claim=4)
    stat_stand = statistical_standings(rows, min_games_for_claim=24)
    write_csv(DATA / "rev0029_counterfactual_mulligan_aggregate.csv", aggregate)
    write_csv(DATA / "rev0029_counterfactual_mulligan_standings.csv", standings)
    write_csv(DATA / "rev0029_counterfactual_mulligan_same_shell.csv", same_shell)
    write_csv(DATA / "rev0029_counterfactual_mulligan_pairwise.csv", pairwise)
    write_csv(DATA / "rev0029_counterfactual_mulligan_stat_standings.csv", stat_stand)
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
            seed=2910000 + t,
            transition_seed=2911000 + t,
            agent_seed=2912000 + t,
            starting_player=starting_player,
            starting_life=life,
            max_decisions=560,
            mulligan_agents=(left.mulligan_policy, right.mulligan_policy),
        )
        trace["trace_id"] = f"rev0029_counterfactual_mulligan_trace_{t:03d}"
        traces.append(trace)
        replay_results.append(replay_public_decision_trace(trace).as_dict())
    write_trace_jsonl(traces, DATA / "rev0029_counterfactual_mulligan_replay_traces.jsonl")
    (DATA / "rev0029_counterfactual_mulligan_replay_results.json").write_text(json.dumps(replay_results, indent=2, sort_keys=True), encoding="utf-8")
    cpp_summary, cpp_rows = check_public_traces_with_cpp(traces, revision=REV)
    write_csv(DATA / "rev0029_counterfactual_mulligan_cpp_trace_rows.csv", [r.as_dict() for r in cpp_rows])
    (DATA / "rev0029_counterfactual_mulligan_cpp_trace_summary.json").write_text(json.dumps(cpp_summary.as_dict(), indent=2, sort_keys=True), encoding="utf-8")

    promo = audit_promotion_rows(
        rows,
        replay_results=replay_results,
        config=PromotionGateConfig(simulator_revision=REV, min_rows=len(rows), max_truncation_rate=0.12, min_replay_traces=len(traces)),
    )
    nochoice_rows, nochoice_summary = run_nochoice_audit(strategies)
    write_csv(DATA / "rev0029_nochoice_segment_audit.csv", nochoice_rows)
    (DATA / "rev0029_nochoice_segment_summary.json").write_text(json.dumps(nochoice_summary, indent=2, sort_keys=True), encoding="utf-8")

    summary = {
        "revision": REV,
        "codename": "counterfactmull-nochoiceseg",
        "training_metrics": metrics,
        "training_rows": int(len(train_df)),
        "lint": lint,
        "strategy_count": len(strategies),
        "games": len(rows),
        "aggregate_rows": len(aggregate),
        "same_shell_rows": len(same_shell),
        "promotion_gate": promo.as_dict(),
        "statistical_gate": stat_gate.as_dict(),
        "replay_count": len(traces),
        "replay_passed": sum(1 for r in replay_results if r.get("passed")),
        "cpp_trace_summary": cpp_summary.as_dict(),
        "nochoice_segment_summary": nochoice_summary,
        "model_contract": "first-look keep/take only; bottom and later mulligans delegate to mulligan_outcome_ranker_rev0027",
    }
    (DATA / "rev0029_counterfactual_mulligan_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
