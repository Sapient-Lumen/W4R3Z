from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.muc5.code_policy import make_code_policy_agent
from src.muc5.cpp_trace import check_public_traces_with_cpp
from src.muc5.deckspace import DeckVector
from src.muc5.public_agents import make_public_agent
from src.muc5.replay import record_public_decision_trace, write_trace_jsonl

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REV = "rev0020"


def trace_decks() -> list[DeckVector]:
    return [
        DeckVector(40, 30, 0, 0, 10, 0),  # Jace-only coverage deck: ultimates happen often.
        DeckVector(40, 24, 4, 4, 8, 0),
        DeckVector(40, 22, 8, 6, 3, 1),
        DeckVector(60, 40, 0, 0, 20, 0),
        DeckVector(60, 34, 4, 12, 8, 2),
        DeckVector(60, 30, 10, 8, 8, 4),
    ]


def main() -> None:
    DATA.mkdir(exist_ok=True)
    decks = trace_decks()
    ultimator = make_code_policy_agent("code_jace_ultimator_rev0020")
    agents = [
        ultimator,
        make_code_policy_agent("code_jace_lock_rev0013"),
        make_code_policy_agent("code_overlord_clock_rev0013"),
        make_public_agent("patient"),
        make_public_agent("counter_happy"),
    ]
    traces = []
    for i in range(36):
        if i < 12:
            # Coverage-heavy mirrors deliberately create ultimate events.
            d0 = decks[0 if i % 2 == 0 else 3]
            d1 = decks[0 if i % 3 else 3]
            a0 = ultimator
            a1 = ultimator if i % 2 else make_public_agent("patient")
            mulligans = ("keep_always", "keep_always")
        else:
            d0 = decks[i % len(decks)]
            d1 = decks[(i * 2 + 1) % len(decks)]
            a0 = agents[i % len(agents)]
            a1 = agents[(i + 2) % len(agents)]
            mulligans = ("land_band", "land_band_business") if i % 2 else ("keep_always", "land_band")
        trace = record_public_decision_trace(
            d0,
            d1,
            a0,
            a1,
            seed=202000 + i,
            transition_seed=202000 + i,
            agent_seed=302000 + i,
            starting_player=i % 2,
            starting_life=20 if i % 3 else 40,
            max_decisions=460,
            mulligan_policies=mulligans,
        )
        trace["trace_id"] = f"{REV}_trace_{i:03d}"
        traces.append(trace)

    write_trace_jsonl(traces, DATA / f"{REV}_public_traces.jsonl")
    summary, rows = check_public_traces_with_cpp(traces, revision=REV)
    row_dicts = [r.as_dict() for r in rows]
    pd.DataFrame(row_dicts).to_csv(DATA / f"{REV}_cpp_trace_rows.csv", index=False)
    payload = summary.as_dict()
    payload["jace_ultimate_events"] = int(sum(1 for r in row_dicts if "mode=ultimate" in str(r.get("action", ""))))
    payload["jace_ultimate_supported_events"] = int(sum(1 for r in row_dicts if "mode=ultimate" in str(r.get("action", "")) and bool(r.get("supported_by_cpp"))))
    payload["trace_ids_with_ultimate"] = sorted({str(r.get("trace_id")) for r in row_dicts if "mode=ultimate" in str(r.get("action", ""))})
    (DATA / f"{REV}_cpp_trace_summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if payload["python_replay_errors"] or payload["mismatches"] or payload["skipped_events"] or payload["jace_ultimate_events"] <= 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
