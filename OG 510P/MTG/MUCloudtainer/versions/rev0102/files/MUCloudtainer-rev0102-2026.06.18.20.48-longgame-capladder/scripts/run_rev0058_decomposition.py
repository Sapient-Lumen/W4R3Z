#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Iterable, Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.cpp_rollout import finalize_cpp_shadow_rollout, prepare_cpp_shadow_rollout
from src.muc5.cpp_trace import finalize_cpp_trace_batch, prepare_public_traces_for_cpp
from src.muc5.mulligan_ranker import make_mulligan_agent
from src.muc5.payoff import aggregate_payoff_rows, write_csv
from src.muc5.public_agents import make_public_agent
from src.muc5.replay import record_public_decision_trace, replay_public_decision_trace, write_trace_jsonl
from src.muc5.terminal_clean import mark_terminal_clean_rows, summarize_terminal_clean_rows
from src.muc5.terminal_decomposition import (
    annotate_decomposition_rows,
    decomposition_mechanism_rows,
    decomposition_specs,
    decomposition_summary_rows,
    rev0058_decomposition_arms,
)
from src.muc5.terminal_mechanisms import target_summary_rows

REV = "rev0058"
CODENAME = "deckpilotablate-endurancegate"
DATA = ROOT / "data"
REPS = 4
TERMINAL_MAX_DECISIONS = 900
BASE_SEED = 5858000


def dump_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _record_replay_samples(specs, count: int = 8):
    agent_cache = {}
    mulligan_cache = {}

    def agent(name: str):
        if name not in agent_cache:
            agent_cache[name] = make_public_agent(name)
        return agent_cache[name]

    def mull(name: str):
        if name not in mulligan_cache:
            mulligan_cache[name] = make_mulligan_agent(name)
        return mulligan_cache[name]

    if not specs:
        return [], []
    # Evenly span the panel instead of taking only the earliest arm.
    if len(specs) <= count:
        sample_indices = list(range(len(specs)))
    else:
        sample_indices = sorted({round(i * (len(specs) - 1) / (count - 1)) for i in range(count)})
    traces = []
    results = []
    for idx in sample_indices:
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
            mulligan_agents=(mull(spec.mulligan0), mull(spec.mulligan1)),
        )
        traces.append(trace)
        results.append(replay_public_decision_trace(trace).as_dict())
    return traces, results


def _sample_transition_rows(rows, *, limit: int = 240) -> list[dict[str, object]]:
    """Keep compact C++ evidence instead of shipping every chosen transition row."""

    out = []
    for row in rows:
        if (not row.supported_by_cpp) or row.cpp_match is False:
            out.append(row.as_dict())
    if len(out) >= limit:
        return out[:limit]
    stride = max(1, len(rows) // max(1, limit - len(out))) if rows else 1
    seen = {r["case_id"] for r in out}
    for i, row in enumerate(rows):
        if i % stride != 0:
            continue
        d = row.as_dict()
        if d["case_id"] in seen:
            continue
        out.append(d)
        if len(out) >= limit:
            break
    return out


def _compare_by_life(summary_rows: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    by = {(str(r["arm_id"]), int(r["starting_life"])): r for r in summary_rows}
    out = []
    for life in sorted({life for (_arm, life) in by}):
        original = by.get(("A_original_size_skew", life), {})
        pilot_swap = by.get(("B_pilot_swap_size_skew", life), {})
        equal40 = by.get(("C_equalized_40v40", life), {})
        equal60 = by.get(("D_equalized_60v60", life), {})
        same_counter = by.get(("E_same_deck_counter60_pilot", life), {})
        same_overlord = by.get(("F_same_deck_overlord40_pilot", life), {})

        def score(row):
            try:
                return float(row.get("target_mean_score_draw_half", 0.0))
            except Exception:
                return 0.0

        def lib_share(row):
            try:
                return float(row.get("library_out_win_share", 0.0))
            except Exception:
                return 0.0

        orig_s = score(original)
        swap_s = score(pilot_swap)
        eq40_s = score(equal40)
        eq60_s = score(equal60)
        control_s = score(same_counter)
        threatdeck_s = score(same_overlord)
        if orig_s >= 0.60 and swap_s <= 0.40:
            provisional = "edge_follows_counterwall_deck_shell_more_than_cf34_pilot"
        elif orig_s >= 0.60 and swap_s >= 0.60:
            provisional = "edge_may_follow_cf34_pilot"
        elif orig_s >= 0.60 and eq40_s < 0.55 and eq60_s < 0.55:
            provisional = "edge_may_require_size_skew"
        else:
            provisional = "inconclusive_small_panel"
        out.append(
            {
                "starting_life": life,
                "original_score": orig_s,
                "pilot_swap_score": swap_s,
                "equalized_40v40_score": eq40_s,
                "equalized_60v60_score": eq60_s,
                "same_counter60_pilot_score": control_s,
                "same_overlord40_pilot_score": threatdeck_s,
                "original_library_out_win_share": lib_share(original),
                "pilot_swap_library_out_win_share": lib_share(pilot_swap),
                "equalized_40v40_library_out_win_share": lib_share(equal40),
                "equalized_60v60_library_out_win_share": lib_share(equal60),
                "provisional_read": provisional,
            }
        )
    return out


def _gate(summary: Mapping[str, object], replay_results: list[Mapping[str, object]], rows: list[Mapping[str, object]]) -> dict[str, object]:
    errors = []
    warnings = []
    if int(summary.get("games", 0)) < 180:
        errors.append("fewer than 180 decomposition games")
    if int(summary.get("truncations", 0)) != 0:
        errors.append("terminal-clean gate failed: truncations present")
    if int(summary.get("python_errors", 0)) != 0:
        errors.append("python errors occurred during C++ shadow rollout")
    cpp = summary.get("cpp_shadow_summary", {})
    if isinstance(cpp, Mapping):
        if int(cpp.get("mismatches", 0)) != 0:
            errors.append("C++ shadow mismatches present")
        if int(cpp.get("skipped_events", 0)) != 0:
            warnings.append("C++ shadow skipped events present")
    if sum(1 for r in replay_results if r.get("passed") is True) < 8:
        errors.append("fewer than 8 replay samples passed")
    if not any(str(r.get("arm_id")) == "B_pilot_swap_size_skew" for r in rows):
        errors.append("pilot-swap arm missing")
    if not any(str(r.get("arm_id")) == "C_equalized_40v40" for r in rows):
        errors.append("40v40 equalization arm missing")
    if not any(str(r.get("arm_id")) == "D_equalized_60v60" for r in rows):
        errors.append("60v60 equalization arm missing")
    return {"passed": not errors, "errors": errors, "warnings": warnings}


def main() -> None:
    DATA.mkdir(exist_ok=True)
    arms = rev0058_decomposition_arms(DATA / "seed_decks.json")
    specs, meta = decomposition_specs(
        arms,
        simulator_revision=REV,
        reps=REPS,
        base_seed=BASE_SEED,
        max_decisions=TERMINAL_MAX_DECISIONS,
    )
    prepared = prepare_cpp_shadow_rollout(specs, revision=REV)
    cpp_summary, cpp_transition_rows = finalize_cpp_shadow_rollout(prepared)
    game_rows = mark_terminal_clean_rows(
        list(prepared.game_rows),
        revision=REV,
        max_decisions=TERMINAL_MAX_DECISIONS,
        strict=False,
    )
    annotated_rows = annotate_decomposition_rows(game_rows, meta)
    terminal_summary = summarize_terminal_clean_rows(annotated_rows, revision=REV, max_decisions=TERMINAL_MAX_DECISIONS)
    arm_summary = decomposition_summary_rows(annotated_rows)
    mechanism_rows = decomposition_mechanism_rows(annotated_rows)
    life_rollup = target_summary_rows(annotated_rows, group_keys=("starting_life",))
    comparisons = _compare_by_life(arm_summary)
    aggregate = aggregate_payoff_rows(annotated_rows)

    replay_traces, replay_results = _record_replay_samples(specs, count=8)
    prepared_trace = prepare_public_traces_for_cpp(replay_traces, revision=REV)
    cpp_trace_summary, cpp_trace_rows = finalize_cpp_trace_batch(prepared_trace)

    write_csv(DATA / "rev0058_decomposition_games.csv", annotated_rows)
    write_csv(DATA / "rev0058_decomposition_aggregate.csv", aggregate)
    write_csv(DATA / "rev0058_decomposition_arm_summary.csv", arm_summary)
    write_csv(DATA / "rev0058_decomposition_mechanisms.csv", mechanism_rows)
    write_csv(DATA / "rev0058_decomposition_life_rollup.csv", life_rollup)
    write_csv(DATA / "rev0058_decomposition_comparisons.csv", comparisons)
    write_csv(DATA / "rev0058_decomposition_cpp_transition_sample.csv", _sample_transition_rows(cpp_transition_rows))
    write_csv(DATA / "rev0058_decomposition_cpp_trace_rows.csv", [r.as_dict() for r in cpp_trace_rows])
    write_trace_jsonl(replay_traces, DATA / "rev0058_decomposition_replay_traces.jsonl")
    dump_json(DATA / "rev0058_decomposition_replay_results.json", replay_results)
    dump_json(DATA / "rev0058_decomposition_arms.json", [a.as_dict() for a in arms])

    summary = {
        "revision": REV,
        "codename": CODENAME,
        "purpose": "Decompose the rev0056 cf34_counter_wall vs pub_threat_overlord result into pilot, deck-size, and terminal-mechanism effects.",
        "reps_per_seat_start_life_arm": REPS,
        "base_seed": BASE_SEED,
        "max_decisions": TERMINAL_MAX_DECISIONS,
        "arms": [a.as_dict() for a in arms],
        "games": len(annotated_rows),
        "python_errors": len(prepared.python_errors),
        "terminal_clean_summary": terminal_summary.as_dict(),
        "cpp_shadow_summary": cpp_summary.as_dict(),
        "cpp_trace_summary": cpp_trace_summary.as_dict(),
        "replay_samples": len(replay_results),
        "replay_passed": int(sum(1 for r in replay_results if r.get("passed") is True)),
        "raw_cpp_transition_rows_generated_but_not_shipped": len(cpp_transition_rows),
        "cpp_transition_sample_rows_shipped": min(240, len(cpp_transition_rows)),
        "arm_summary_rows": arm_summary,
        "life_rollup": life_rollup,
        "comparisons": comparisons,
        "decomposition_gate": {},
        "notes": [
            "This revision intentionally ships a compact C++ transition sample rather than the full transition table to reduce raw evidence ballast.",
            "Scores are target-perspective within each arm; B_pilot_swap_size_skew target is the cf34 pilot on the Overlord 40-card shell.",
            "This is a decomposition panel, not a promotion claim; small cells should be treated as directional evidence until a seed-disjoint follow-up repeats the explanatory cells.",
        ],
    }
    summary["decomposition_gate"] = _gate(summary, replay_results, annotated_rows)
    dump_json(DATA / "rev0058_decomposition_summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
