from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path
from random import Random

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.agents import MatchResult
from src.muc5.cards import STARTING_LIFE_OPTIONS
from src.muc5.cpp_legal import cpp_legal_tool_status, diff_legal_menus, legal_record_from_state, python_legal_menu_strings
from src.muc5.decision import apply_decision_index, build_decision_frame
from src.muc5.engine import start_game
from src.muc5.mulligan import POLICY_LAND_BAND, POLICY_LAND_BAND_BUSINESS
from src.muc5.payoff import load_seed_decks
from src.muc5.public_agents import make_public_agent


def collect_records(games: int = 72, max_decisions: int = 360) -> tuple[list, list[tuple[str, ...]], list[dict[str, object]]]:
    decks = load_seed_decks(ROOT / "data" / "seed_decks.json")
    deck_names = list(decks.keys())
    agents = ["heuristic", "counter_happy", "threat_rush", "patient", "code_jace_lock_rev0013", "code_overlord_clock_rev0013", "code_force_conservative_rev0013", "random"]
    rng = Random(16016)
    records = []
    expected: list[tuple[str, ...]] = []
    rows: list[dict[str, object]] = []
    for game_idx in range(games):
        d0_name = deck_names[game_idx % len(deck_names)]
        d1_name = deck_names[(game_idx * 3 + 1) % len(deck_names)]
        a0_name = agents[game_idx % len(agents)]
        a1_name = agents[(game_idx * 5 + 2) % len(agents)]
        life = STARTING_LIFE_OPTIONS[game_idx % len(STARTING_LIFE_OPTIONS)]
        seed = 1601600 + game_idx
        state = start_game(
            decks[d0_name],
            decks[d1_name],
            seed=seed,
            starting_player=game_idx % 2,
            starting_life=life,
            mulligan_policies=(POLICY_LAND_BAND, POLICY_LAND_BAND_BUSINESS),
            record_log=False,
        )
        game_rng = Random(seed)
        agent_objs = [make_public_agent(a0_name), make_public_agent(a1_name)]
        decisions = 0
        for decisions in range(1, max_decisions + 1):
            if state.winner is not None:
                break
            frame = build_decision_frame(state)
            if frame.action_count <= 0:
                break
            records.append(legal_record_from_state(state))
            expected.append(tuple(frame.legal_action_strings))
            idx = agent_objs[frame.player].choose_action_index(frame, game_rng)
            apply_decision_index(state, frame, idx, game_rng)
        if state.winner is None:
            state.frame = "GAME_OVER"
            state.loss_reason = "max_decisions_reached"
        rows.append(
            {
                "game_idx": game_idx,
                "deck0": d0_name,
                "deck1": d1_name,
                "agent0": a0_name,
                "agent1": a1_name,
                "starting_life": life,
                "starting_player": game_idx % 2,
                "seed": seed,
                "winner": "None" if state.winner is None else str(state.winner),
                "loss_reason": state.loss_reason,
                "decisions": decisions,
            }
        )
    return records, expected, rows


def main() -> None:
    records, expected, game_rows = collect_records()
    diffs = diff_legal_menus(records, expected)
    frames = Counter(r.frame for r in records)
    pending = Counter(r.pending_kind or "<none>" for r in records)
    action_counts = [len(x) for x in expected]
    data_dir = ROOT / "data"
    data_dir.mkdir(exist_ok=True)
    diff_path = data_dir / "rev0016_cpp_legal_diff_mismatches.json"
    summary_path = data_dir / "rev0016_cpp_legal_diff_summary.json"
    games_path = data_dir / "rev0016_cpp_legal_diff_games.csv"
    diff_path.write_text(json.dumps(diffs[:25], indent=2, sort_keys=True))
    with games_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(game_rows[0].keys()))
        writer.writeheader()
        writer.writerows(game_rows)
    summary = {
        "simulator_revision": "rev0016",
        "codename": "cpplegalmenu-seqrace",
        "tool_status": cpp_legal_tool_status().as_dict(),
        "games": len(game_rows),
        "decision_records": len(records),
        "mismatches": len(diffs),
        "diff_sample_path": str(diff_path.relative_to(ROOT)),
        "frame_counts": dict(frames),
        "pending_choice_counts": dict(pending),
        "max_legal_actions": max(action_counts) if action_counts else 0,
        "mean_legal_actions": sum(action_counts) / len(action_counts) if action_counts else 0.0,
        "games_with_truncation": sum(1 for r in game_rows if r["loss_reason"] == "max_decisions_reached"),
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True))
    print(json.dumps(summary, indent=2, sort_keys=True))
    if diffs:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
