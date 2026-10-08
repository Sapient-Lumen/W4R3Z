from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.cpp_rollout import finalize_cpp_shadow_rollout, prepare_cpp_shadow_rollout, strategy_pair_specs
from src.muc5.cpp_trace import finalize_cpp_trace_batch, prepare_public_traces_for_cpp
from src.muc5.mulligan_ranker import make_mulligan_agent
from src.muc5.payoff import aggregate_payoff_rows, write_csv
from src.muc5.promotion import PromotionGateConfig, audit_promotion_rows, strategy_standings
from src.muc5.public_agents import make_public_agent
from src.muc5.replay import record_public_decision_trace, replay_public_decision_trace, write_trace_jsonl
from src.muc5.statgate import audit_statistical_gate, pairwise_stat_rows, statistical_standings
from src.muc5.strategy_sets import yield_counterfactual_action_ranker_bundles
from src.muc5.truncation_rescue import annotate_rescued_rows, summarize_rescue, truncation_by_pair, truncation_by_strategy

REV = "rev0048"
CODENAME = "truncrescue-terminalgate"
DATA = ROOT / "data"
BASELINE_REV = "rev0047"
BASELINE_MAX_DECISIONS = 380
FINAL_MAX_DECISIONS = 900
BASE_SEED = 4747000


def _read_csv_rows(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    return pd.read_csv(path).to_dict(orient="records")


def _record_replay_samples(specs, count: int = 8):
    agent_cache = {}
    mulligan_cache = {}

    def agent(name: str):
        if name not in agent_cache:
            agent_cache[name] = make_public_agent(name)
        return agent_cache[name]

    def mulligan(name: str):
        if name not in mulligan_cache:
            mulligan_cache[name] = make_mulligan_agent(name)
        return mulligan_cache[name]

    # Include early, middle, late, and some historically truncation-prone cells.
    sample_indices = [0, 1, 2, 3, 17, 31, len(specs) // 2, len(specs) - 1]
    traces = []
    results = []
    seen = set()
    for idx in sample_indices:
        if idx in seen or idx < 0 or idx >= len(specs):
            continue
        seen.add(idx)
        spec = specs[idx]
        trace = record_public_decision_trace(
            spec.deck0,
            spec.deck1,
            agent(spec.agent0),
            agent(spec.agent1),
            seed=int(spec.seed),
            transition_seed=int(spec.seed),
            agent_seed=int(spec.seed) + 1000003,
            starting_player=int(spec.starting_player),
            starting_life=int(spec.starting_life),
            max_decisions=int(spec.max_decisions),
            mulligan_agents=(mulligan(spec.mulligan0), mulligan(spec.mulligan1)),
        )
        traces.append(trace)
        results.append(replay_public_decision_trace(trace).as_dict())
        if len(traces) >= count:
            break
    return traces, results


def main() -> None:
    DATA.mkdir(exist_ok=True)
    strategies = yield_counterfactual_action_ranker_bundles(DATA / "seed_decks.json")[:6]
    baseline_rows = _read_csv_rows(DATA / "rev0047_yield_ranker_games.csv")
    if not baseline_rows:
        raise SystemExit("Missing rev0047_yield_ranker_games.csv; run rev0047 first or unpack an archive containing it.")

    specs = strategy_pair_specs(
        strategies,
        simulator_revision=REV,
        life_totals=(20, 40),
        reps=1,
        base_seed=BASE_SEED,
        max_decisions=FINAL_MAX_DECISIONS,
    )
    prepared = prepare_cpp_shadow_rollout(specs, revision=REV)
    cpp_summary, cpp_transition_rows = finalize_cpp_shadow_rollout(prepared)
    final_rows = list(prepared.game_rows)
    annotated_rows = annotate_rescued_rows(
        baseline_rows,
        final_rows,
        revision=REV,
        baseline_max_decisions=BASELINE_MAX_DECISIONS,
        final_max_decisions=FINAL_MAX_DECISIONS,
    )
    rescue_summary = summarize_rescue(
        annotated_rows,
        revision=REV,
        baseline_max_decisions=BASELINE_MAX_DECISIONS,
        final_max_decisions=FINAL_MAX_DECISIONS,
    )

    aggregate = aggregate_payoff_rows(annotated_rows)
    standings = strategy_standings(annotated_rows)
    stat_standings = statistical_standings(annotated_rows, min_games_for_claim=24)
    pairwise = pairwise_stat_rows(annotated_rows, min_games_for_claim=4)
    by_strategy = truncation_by_strategy(annotated_rows)
    by_pair = truncation_by_pair(annotated_rows)

    replay_traces, replay_results = _record_replay_samples(specs, count=8)
    prepared_trace = prepare_public_traces_for_cpp(replay_traces, revision=REV)
    cpp_trace_summary, cpp_trace_rows = finalize_cpp_trace_batch(prepared_trace)

    promotion = audit_promotion_rows(
        annotated_rows,
        replay_results=replay_results,
        config=PromotionGateConfig(simulator_revision=REV, min_rows=120, min_replay_traces=6, max_truncation_rate=0.10),
    )
    stat_gate = audit_statistical_gate(annotated_rows, stat_standings, pairwise, min_raw_rows=120, max_truncation_rate=0.10)

    write_csv(DATA / "rev0048_truncation_rescue_games.csv", annotated_rows)
    write_csv(DATA / "rev0048_truncation_rescue_aggregate.csv", aggregate)
    write_csv(DATA / "rev0048_truncation_rescue_standings.csv", standings)
    write_csv(DATA / "rev0048_truncation_rescue_stat_standings.csv", stat_standings)
    write_csv(DATA / "rev0048_truncation_rescue_pairwise.csv", pairwise)
    write_csv(DATA / "rev0048_truncation_rescue_by_strategy.csv", by_strategy)
    write_csv(DATA / "rev0048_truncation_rescue_by_pair.csv", by_pair)
    write_csv(DATA / "rev0048_truncation_rescue_cpp_transitions.csv", [r.as_dict() for r in cpp_transition_rows])
    write_csv(DATA / "rev0048_truncation_rescue_cpp_trace_rows.csv", [r.as_dict() for r in cpp_trace_rows])
    write_trace_jsonl(replay_traces, DATA / "rev0048_truncation_rescue_replay_traces.jsonl")
    (DATA / "rev0048_truncation_rescue_replay_results.json").write_text(json.dumps(replay_results, indent=2))

    baseline_trunc = int(sum(1 for r in baseline_rows if str(r.get("is_truncation", "")).lower() in {"true", "1"}))
    final_trunc = int(sum(1 for r in annotated_rows if str(r.get("is_truncation", "")).lower() in {"true", "1"}))
    summary = {
        "revision": REV,
        "codename": CODENAME,
        "baseline_revision": BASELINE_REV,
        "baseline_max_decisions": BASELINE_MAX_DECISIONS,
        "final_max_decisions": FINAL_MAX_DECISIONS,
        "strategies": len(strategies),
        "games": len(annotated_rows),
        "baseline_truncations": baseline_trunc,
        "final_truncations": final_trunc,
        "rescue_summary": rescue_summary.as_dict(),
        "promotion": promotion.as_dict(),
        "statistical_gate": stat_gate.as_dict(),
        "cpp_shadow_summary": cpp_summary.as_dict(),
        "cpp_trace_summary": cpp_trace_summary.as_dict(),
        "replay_samples": len(replay_results),
        "replay_passed": int(sum(1 for r in replay_results if r.get("passed") is True)),
        "notes": [
            "rev0048 reruns the rev0047 yield-ranker panel at a higher decision ceiling using the same seeds and strategy bundles.",
            "Rows expose baseline_is_truncation and resolved_from_truncation so truncation changes cannot hide inside aggregate scores.",
            "The final table is intended for reporting/evaluation only; any remaining truncation rows still must not be used as terminal training reward.",
            "C++ transition shadow is run on the full higher-ceiling payoff panel, and replay/C++ trace checks are run on a sample.",
        ],
    }
    (DATA / "rev0048_truncation_rescue_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
