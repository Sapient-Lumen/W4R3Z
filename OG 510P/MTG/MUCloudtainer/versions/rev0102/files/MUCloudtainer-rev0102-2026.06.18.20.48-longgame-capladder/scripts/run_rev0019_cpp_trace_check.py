from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.muc5.cpp_trace import check_public_traces_with_cpp
from src.muc5.deckspace import DeckVector
from src.muc5.public_agents import make_public_agent
from src.muc5.replay import record_public_decision_trace, write_trace_jsonl
from src.muc5.mulligan import POLICY_KEEP_ALWAYS, POLICY_LAND_BAND, POLICY_LAND_BAND_BUSINESS

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REV = "rev0019"


def trace_decks() -> list[DeckVector]:
    return [
        DeckVector(40, 22, 8, 6, 3, 1),
        DeckVector(40, 20, 4, 8, 5, 3),
        DeckVector(40, 24, 2, 8, 4, 2),
        DeckVector(60, 30, 10, 8, 8, 4),
        DeckVector(60, 34, 4, 12, 5, 5),
        DeckVector(60, 28, 14, 10, 4, 4),
    ]


def main() -> None:
    DATA.mkdir(exist_ok=True)
    agents = [make_public_agent(name) for name in ("heuristic", "counter_happy", "threat_rush", "patient", "random")]
    mulligans = [POLICY_KEEP_ALWAYS, POLICY_LAND_BAND, POLICY_LAND_BAND_BUSINESS]
    decks = trace_decks()
    traces = []
    # Small but varied: both life totals, all mulligan policies, several public agents.
    for i in range(30):
        d0 = decks[i % len(decks)]
        d1 = decks[(i * 2 + 1) % len(decks)]
        a0 = agents[i % len(agents)]
        a1 = agents[(i + 2) % len(agents)]
        life = 20 if i % 2 == 0 else 40
        policy0 = mulligans[i % len(mulligans)]
        policy1 = mulligans[(i + 1) % len(mulligans)]
        trace = record_public_decision_trace(
            d0,
            d1,
            a0,
            a1,
            seed=190000 + i,
            transition_seed=190000 + i,
            agent_seed=290000 + i,
            starting_player=i % 2,
            starting_life=life,
            max_decisions=420,
            mulligan_policies=(policy0, policy1),
        )
        trace["trace_id"] = f"{REV}_trace_{i:03d}"
        traces.append(trace)

    write_trace_jsonl(traces, DATA / f"{REV}_public_traces.jsonl")
    summary, rows = check_public_traces_with_cpp(traces, revision=REV)
    pd.DataFrame([r.as_dict() for r in rows]).to_csv(DATA / f"{REV}_cpp_trace_rows.csv", index=False)
    (DATA / f"{REV}_cpp_trace_summary.json").write_text(json.dumps(summary.as_dict(), indent=2), encoding="utf-8")
    print(json.dumps(summary.as_dict(), indent=2))
    if summary.python_replay_errors or summary.mismatches:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
