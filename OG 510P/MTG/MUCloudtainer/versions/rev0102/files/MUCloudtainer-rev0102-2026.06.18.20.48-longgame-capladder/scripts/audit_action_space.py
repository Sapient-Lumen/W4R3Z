from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from random import Random
from statistics import mean, median

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.agents import HeuristicAgent
from src.muc5.deckspace import DeckVector
from src.muc5.engine import apply_action, legal_actions, start_game
from src.muc5.invariants import assert_card_conservation
from src.muc5.mulligan import POLICY_KEEP_ALWAYS, POLICY_LAND_BAND

MAX_DECISIONS = 220


def load_seed_decks(limit: int = 4):
    payload = json.loads((ROOT / "data" / "seed_decks.json").read_text())
    out = []
    for item in payload["seed_decks"][:limit]:
        counts = item["counts"]
        out.append((
            item["name"],
            DeckVector(
                item["size"],
                counts["Island"],
                counts["Counterspell"],
                counts["ForceOfWill"],
                counts["JaceTheMindSculptor"],
                counts["OverlordOfTheFloodpits"],
            ),
        ))
    return out


def main():
    agents = [HeuristicAgent("h0"), HeuristicAgent("h1")]
    rows = []
    games = 0
    seed_decks = load_seed_decks()
    policies = [("no_mulligan", None), ("land_band", POLICY_LAND_BAND)]
    for life in (20, 40):
        for policy_label, policy in policies:
            for deck_i, (name0, deck0) in enumerate(seed_decks):
                for deck_j, (name1, deck1) in enumerate(seed_decks):
                    if deck_i == deck_j and deck_i > 1:
                        continue
                    games += 1
                    seed = 700_000 + life * 1000 + 100 * deck_i + 7 * deck_j + (0 if policy is None else 3)
                    rng = Random(seed)
                    state = start_game(deck0, deck1, seed=seed, starting_life=life, mulligan_policy=policy)
                    for decision in range(1, MAX_DECISIONS + 1):
                        assert_card_conservation(state)
                        if state.winner is not None:
                            break
                        actions = legal_actions(state)
                        rows.append({
                            "game_id": games,
                            "decision": decision,
                            "starting_life": life,
                            "mulligan_policy": policy_label,
                            "deck0": name0,
                            "deck1": name1,
                            "to_act": state.current_player(),
                            "frame": state.frame,
                            "main_phase": state.main_phase,
                            "pending_choice_kind": "none" if state.pending_choice is None else state.pending_choice.kind,
                            "stack_len": len(state.stack),
                            "legal_action_count": len(actions),
                        })
                        action = agents[state.current_player()].choose_action(state, rng)
                        apply_action(state, action, rng)
                    assert_card_conservation(state)

    out_csv = ROOT / "data" / "rev0005_action_space_audit.csv"
    with out_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    counts = [int(r["legal_action_count"]) for r in rows]
    by_frame = defaultdict(list)
    by_pending = defaultdict(list)
    for r in rows:
        by_frame[r["frame"]].append(int(r["legal_action_count"]))
        by_pending[r["pending_choice_kind"]].append(int(r["legal_action_count"]))
    summary = {
        "revision": "rev0005",
        "games": games,
        "decision_rows": len(rows),
        "max_decisions_per_game": MAX_DECISIONS,
        "max_legal_action_count": max(counts),
        "mean_legal_action_count": mean(counts),
        "median_legal_action_count": median(counts),
        "p99_legal_action_count": sorted(counts)[max(0, int(0.99 * len(counts)) - 1)],
        "frame_summary": {
            k: {"rows": len(v), "max": max(v), "mean": mean(v)} for k, v in sorted(by_frame.items())
        },
        "pending_choice_summary": {
            k: {"rows": len(v), "max": max(v), "mean": mean(v)} for k, v in sorted(by_pending.items())
        },
        "slot_budget_recommendation": "max_action_slots=64 is enough for this sampled audit; keep 256 as conservative default until learned policies stress more states.",
    }
    out_json = ROOT / "data" / "rev0005_action_space_audit_summary.json"
    out_json.write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
