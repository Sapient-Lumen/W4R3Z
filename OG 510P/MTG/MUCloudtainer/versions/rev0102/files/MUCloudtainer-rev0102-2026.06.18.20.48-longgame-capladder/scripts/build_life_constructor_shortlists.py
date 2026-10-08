from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, List
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.life_constructor import LIFE_CONSTRUCTOR_LABELS, top_life_dial_decks_all_labels

DATA = ROOT / "data"


def main() -> None:
    by_label = top_life_dial_decks_all_labels(n=25)
    rows: List[Dict[str, object]] = []
    top_by_label: Dict[str, List[Dict[str, object]]] = {}
    for label in LIFE_CONSTRUCTOR_LABELS:
        top_by_label[label] = []
        for rank, score in enumerate(by_label[label], start=1):
            row = {"rank": rank, **score.to_row()}
            rows.append(row)
            top_by_label[label].append(row)

    out_csv = DATA / "rev0004_life_constructor_shortlists.csv"
    with out_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "rev": "rev0004",
        "labels": list(LIFE_CONSTRUCTOR_LABELS),
        "rows": len(rows),
        "per_label": {label: len(top_by_label[label]) for label in LIFE_CONSTRUCTOR_LABELS},
        "top1": {label: top_by_label[label][0] for label in LIFE_CONSTRUCTOR_LABELS},
        "caveat": "These are static pre-simulation priors to make the life-total construction dial testable before learned constructors exist. They are not strategic truth.",
    }
    (DATA / "rev0004_life_constructor_shortlists_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
