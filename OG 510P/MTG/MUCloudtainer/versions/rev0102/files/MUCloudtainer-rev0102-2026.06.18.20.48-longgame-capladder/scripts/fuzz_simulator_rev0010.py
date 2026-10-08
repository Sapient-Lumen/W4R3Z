from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.readiness import run_public_decision_fuzz



def main() -> None:
    summary = run_public_decision_fuzz(
        ROOT / "data" / "seed_decks.json",
        games=300,
        max_decisions=250,
        seed_base=10100,
    ).as_dict()
    path = ROOT / "data" / "rev0010_fuzz_summary.json"
    path.write_text(json.dumps(summary, indent=2, sort_keys=True))
    print(json.dumps(summary, indent=2, sort_keys=True))
    if summary["failures"] != 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
