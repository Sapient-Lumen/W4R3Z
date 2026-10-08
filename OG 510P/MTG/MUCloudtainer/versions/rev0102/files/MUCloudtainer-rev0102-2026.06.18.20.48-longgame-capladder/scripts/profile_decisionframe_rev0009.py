#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.deckspace import DeckVector
from src.muc5.perf import benchmark_agent_games, benchmark_public_decision_games


def main() -> None:
    deck0 = DeckVector(40, 24, 6, 4, 3, 3)
    deck1 = DeckVector(60, 32, 12, 8, 4, 4)
    runs = {
        "trusted_state_agent_fastpath": benchmark_agent_games(deck0, deck1, games=150, validate_actions=False, record_log=False).as_dict(),
        "trusted_state_agent_validated": benchmark_agent_games(deck0, deck1, games=150, validate_actions=True, record_log=False).as_dict(),
        "public_decision_frame": benchmark_public_decision_games(deck0, deck1, games=150, record_log=False).as_dict(),
    }
    fast = runs["trusted_state_agent_fastpath"]["decisions_per_second"]
    pub = runs["public_decision_frame"]["decisions_per_second"]
    runs["summary"] = {
        "public_vs_fast_decision_throughput_ratio": pub / fast if fast else None,
        "note": "DecisionFrame is a fairness boundary first and a safe fast path second; small overhead is acceptable if it blocks state leakage.",
    }
    out = ROOT / "data" / "rev0009_decisionframe_profile_summary.json"
    out.write_text(json.dumps(runs, indent=2, sort_keys=True))
    print(json.dumps(runs, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
