from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.map_elites import archive_summary, build_static_map_elites_archive
from src.muc5.payoff import load_seed_decks, write_csv


def main() -> None:
    data = ROOT / "data"
    decks = list(load_seed_decks(data / "seed_decks.json").values())
    cells = build_static_map_elites_archive(decks, seed=14014, random_samples=3000, mutations_per_seed=160)
    rows = [c.as_dict() for c in cells]
    write_csv(data / "rev0014_map_elites_archive.csv", rows)
    summary = archive_summary(cells)
    summary.update({
        "revision": "rev0014",
        "note": "Static MAP-Elites-style illumination archive; quality is a pre-simulation prior, not matchup truth.",
        "seed_decks": len(decks),
        "random_samples": 3000,
        "mutations_per_seed": 160,
        "top_cells": rows[:12],
    })
    (data / "rev0014_map_elites_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True))
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
