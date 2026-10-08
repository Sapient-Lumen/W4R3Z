from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from random import Random
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.cards import CARD_ORDER
from src.muc5.deckspace import DeckVector
from src.muc5.engine import deck_to_library
from src.muc5.mulligan import MULLIGAN_POLICY_NAMES, london_mulligan_opening_hand

SAMPLES_PER_DECK_POLICY = 1000


def load_seed_decks():
    payload = json.loads((ROOT / "data" / "seed_decks.json").read_text())
    out = []
    for item in payload["seed_decks"]:
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


def summarize_deck_policy(name: str, deck: DeckVector, policy: str, base_seed: int) -> dict:
    records = []
    for i in range(SAMPLES_PER_DECK_POLICY):
        rng = Random(base_seed + i)
        library = deck_to_library(deck, rng)
        hand, result = london_mulligan_opening_hand(library, rng, policy, player=0)
        row = result.to_row()
        row["opening_total"] = sum(hand.values())
        row["library_after_opening"] = len(library)
        records.append(row)
    summary = {
        "deck_name": name,
        "deck_size": deck.size,
        "island": deck.island,
        "counterspell": deck.counterspell,
        "force": deck.force,
        "jace": deck.jace,
        "overlord": deck.overlord,
        "policy_name": policy,
        "samples": SAMPLES_PER_DECK_POLICY,
        "avg_mulligans_taken": mean(r["mulligans_taken"] for r in records),
        "p_any_mulligan": mean(1 if r["mulligans_taken"] >= 1 else 0 for r in records),
        "p_two_or_more_mulligans": mean(1 if r["mulligans_taken"] >= 2 else 0 for r in records),
        "avg_kept_hand_size": mean(r["kept_hand_size"] for r in records),
        "avg_opening_islands": mean(r.get("opening_Island", 0) for r in records),
        "avg_opening_blue_nonlands": mean(sum(r.get(f"opening_{card}", 0) for card in CARD_ORDER if card != "Island") for r in records),
        "avg_bottomed_cards": mean(sum(r.get(f"bottomed_{card}", 0) for card in CARD_ORDER) for r in records),
    }
    for card in CARD_ORDER:
        summary[f"avg_opening_{card}"] = mean(r.get(f"opening_{card}", 0) for r in records)
        summary[f"avg_bottomed_{card}"] = mean(r.get(f"bottomed_{card}", 0) for r in records)
    return summary


def main():
    rows = []
    for deck_i, (name, deck) in enumerate(load_seed_decks()):
        for policy_i, policy in enumerate(MULLIGAN_POLICY_NAMES):
            rows.append(summarize_deck_policy(name, deck, policy, 500_000 + 10_000 * deck_i + 100 * policy_i))
    out_csv = ROOT / "data" / "rev0005_mulligan_probe.csv"
    with out_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    by_policy = defaultdict(list)
    for row in rows:
        by_policy[row["policy_name"]].append(row)
    summary = {
        "revision": "rev0005",
        "samples_per_deck_policy": SAMPLES_PER_DECK_POLICY,
        "decks": len(load_seed_decks()),
        "rows": len(rows),
        "policies": list(MULLIGAN_POLICY_NAMES),
        "policy_summary": {
            p: {
                "mean_p_any_mulligan": mean(r["p_any_mulligan"] for r in rs),
                "mean_avg_kept_hand_size": mean(r["avg_kept_hand_size"] for r in rs),
                "mean_avg_opening_islands": mean(r["avg_opening_islands"] for r in rs),
            }
            for p, rs in by_policy.items()
        },
    }
    out_json = ROOT / "data" / "rev0005_mulligan_probe_summary.json"
    out_json.write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
