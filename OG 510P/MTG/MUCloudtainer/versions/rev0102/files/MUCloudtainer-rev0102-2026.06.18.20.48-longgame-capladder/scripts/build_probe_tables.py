from __future__ import annotations

import csv
import heapq
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.deckspace import DeckVector, enumerate_decks, plausibility_filter, total_deck_count
from src.muc5.probability import deck_probe

DATA = ROOT / "data"


def main() -> None:
    top_heap: list[tuple[float, int, dict]] = []
    evaluated = 0
    plausible = 0
    best_by_size: dict[int, dict] = {}
    anchor_decks = [
        DeckVector(40, 24, 6, 4, 3, 3),
        DeckVector(40, 22, 8, 6, 2, 2),
        DeckVector(60, 32, 10, 6, 6, 6),
        DeckVector(60, 36, 8, 8, 4, 4),
    ]
    for idx, deck in enumerate(enumerate_decks()):
        evaluated += 1
        if not plausibility_filter(deck):
            continue
        plausible += 1
        row = deck_probe(deck).to_row()
        score = float(row["crude_probe_score"])
        entry = (score, idx, row)
        if len(top_heap) < 100:
            heapq.heappush(top_heap, entry)
        elif score > top_heap[0][0]:
            heapq.heapreplace(top_heap, entry)
        size = int(row["deck_size"])
        if size not in best_by_size or score > float(best_by_size[size]["crude_probe_score"]):
            best_by_size[size] = row
    top_rows = [entry[2] for entry in sorted(top_heap, key=lambda x: x[0], reverse=True)]
    out_csv = DATA / "probe_rankings_top100.csv"
    with out_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(top_rows[0].keys()))
        writer.writeheader()
        writer.writerows(top_rows)
    anchor_rows = [deck_probe(d).to_row() for d in anchor_decks]
    summary = {
        "total_raw_decks": total_deck_count(),
        "evaluated_raw_decks": evaluated,
        "plausible_decks_under_rev0002_filter": plausible,
        "top100_source": "exact hypergeometric probe score over plausibility-filtered raw deck vectors",
        "score_warning": "crude_probe_score is not strategic strength; it is a pregame/probability screening score for constructor debugging.",
        "best_by_size": best_by_size,
        "anchor_decks": anchor_rows,
    }
    (DATA / "probe_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps({"evaluated": evaluated, "plausible": plausible, "top_csv": str(out_csv)}, indent=2))


if __name__ == "__main__":
    main()
