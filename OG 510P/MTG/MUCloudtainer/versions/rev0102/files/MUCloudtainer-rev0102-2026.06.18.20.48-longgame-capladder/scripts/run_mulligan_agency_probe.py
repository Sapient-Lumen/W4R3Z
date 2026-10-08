from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from random import Random
from statistics import mean
from typing import Dict, List
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.cards import CARD_ORDER
from src.muc5.deckspace import DeckVector
from src.muc5.engine import deck_to_library
from src.muc5.mulligan import MULLIGAN_POLICY_NAMES, RuleMulliganAgent, london_mulligan_agent_opening_hand

DATA = ROOT / "data"


def deck_from_record(record: Dict[str, object]) -> DeckVector:
    counts = record["counts"]
    assert isinstance(counts, dict)
    return DeckVector(
        int(record["size"]),
        int(counts["Island"]),
        int(counts["Counterspell"]),
        int(counts["ForceOfWill"]),
        int(counts["JaceTheMindSculptor"]),
        int(counts["OverlordOfTheFloodpits"]),
    )


def load_seed_decks() -> List[Dict[str, object]]:
    payload = json.loads((DATA / "seed_decks.json").read_text())
    return list(payload["seed_decks"])


def summarize(records: List[Dict[str, object]]) -> Dict[str, object]:
    if not records:
        return {}
    return {
        "samples": len(records),
        "avg_mulligans_taken": mean(float(r["mulligans_taken"]) for r in records),
        "p_any_mulligan": mean(1.0 if int(r["mulligans_taken"]) >= 1 else 0.0 for r in records),
        "p_two_or_more_mulligans": mean(1.0 if int(r["mulligans_taken"]) >= 2 else 0.0 for r in records),
        "avg_kept_hand_size": mean(float(r["kept_hand_size"]) for r in records),
        "avg_decision_count": mean(float(r["decision_count"]) for r in records),
        "avg_bottomed_total": mean(float(r["bottomed_total"]) for r in records),
        "avg_kept_islands": mean(float(r["opening_Island"]) for r in records),
        "avg_kept_blue_nonlands": mean(
            sum(float(r[f"opening_{card}"]) for card in CARD_ORDER if card != "Island") for r in records
        ),
    }


def main() -> None:
    seed_decks = load_seed_decks()
    rows: List[Dict[str, object]] = []
    event_rows: List[Dict[str, object]] = []
    samples_per_deck_policy = 750
    base_seed = 600_000

    for deck_idx, rec in enumerate(seed_decks):
        deck = deck_from_record(rec)
        for policy in MULLIGAN_POLICY_NAMES:
            agent = RuleMulliganAgent(policy)
            for sample in range(samples_per_deck_policy):
                seed = base_seed + deck_idx * 100_000 + MULLIGAN_POLICY_NAMES.index(policy) * 10_000 + sample
                rng = Random(seed)
                library = deck_to_library(deck, rng)
                hand, result, events = london_mulligan_agent_opening_hand(library, rng, agent, player=0)
                row = {
                    "seed": seed,
                    "deck_name": rec["name"],
                    "deck_tuple": deck.as_tuple(),
                    "policy": policy,
                    "agent_name": agent.name,
                    "mulligans_taken": result.mulligans_taken,
                    "kept_hand_size": result.kept_hand_size,
                    "decision_count": result.decision_count,
                    "bottomed_total": sum(result.bottomed.values()),
                    "library_count_after_mulligan": len(library),
                }
                for card in CARD_ORDER:
                    row[f"opening_{card}"] = int(result.opening_hand.get(card, 0))
                    row[f"bottomed_{card}"] = int(result.bottomed.get(card, 0))
                rows.append(row)
                for event_index, event in enumerate(events):
                    erow = event.to_row()
                    erow.update({
                        "seed": seed,
                        "deck_name": rec["name"],
                        "policy": policy,
                        "event_index": event_index,
                    })
                    event_rows.append(erow)

    out_csv = DATA / "rev0006_mulligan_agency_probe.csv"
    with out_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    out_events = DATA / "rev0006_mulligan_decision_events.csv"
    with out_events.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(event_rows[0].keys()))
        writer.writeheader()
        writer.writerows(event_rows)

    by_policy: Dict[str, List[Dict[str, object]]] = defaultdict(list)
    by_deck_policy: Dict[str, List[Dict[str, object]]] = defaultdict(list)
    action_counts: Counter[str] = Counter()
    for row in rows:
        by_policy[str(row["policy"])].append(row)
        by_deck_policy[f'{row["deck_name"]}|{row["policy"]}'].append(row)
    for erow in event_rows:
        action_counts[str(erow["action"])] += 1

    summary = {
        "rev": "rev0006",
        "rows": len(rows),
        "event_rows": len(event_rows),
        "seed_decks": len(seed_decks),
        "policies": list(MULLIGAN_POLICY_NAMES),
        "samples_per_deck_policy": samples_per_deck_policy,
        "by_policy": {policy: summarize(recs) for policy, recs in sorted(by_policy.items())},
        "by_deck_policy": {key: summarize(recs) for key, recs in sorted(by_deck_policy.items())},
        "action_counts": dict(action_counts),
        "note": "This probe exercises the explicit pregame action interface: KEEP/MULLIGAN plus one-card-at-a-time BOTTOM choices.",
    }
    out_json = DATA / "rev0006_mulligan_agency_probe_summary.json"
    out_json.write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
