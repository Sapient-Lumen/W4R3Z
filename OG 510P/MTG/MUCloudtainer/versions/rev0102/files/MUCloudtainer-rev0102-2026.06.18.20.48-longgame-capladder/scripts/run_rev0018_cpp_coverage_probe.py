from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.muc5.cpp_coverage import collect_transition_coverage
from src.muc5.deckspace import DeckVector

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REV = "rev0018"


def main() -> None:
    DATA.mkdir(exist_ok=True)
    decks = [
        DeckVector(40, 22, 8, 6, 3, 1),
        DeckVector(40, 20, 4, 8, 5, 3),
        DeckVector(40, 24, 2, 8, 4, 2),
        DeckVector(60, 30, 10, 8, 8, 4),
        DeckVector(60, 34, 4, 12, 5, 5),
        DeckVector(60, 28, 14, 10, 4, 4),
    ]
    summary, rows = collect_transition_coverage(decks, games=48, max_decisions=450, seed=180180)
    pd.DataFrame([r.as_dict() for r in rows]).to_csv(DATA / f"{REV}_cpp_transition_coverage_rows.csv", index=False)
    out = summary.as_dict()
    (DATA / f"{REV}_cpp_transition_coverage_summary.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
