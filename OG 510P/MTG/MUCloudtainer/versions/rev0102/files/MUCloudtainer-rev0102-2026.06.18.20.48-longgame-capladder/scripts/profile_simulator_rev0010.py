from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.deckspace import DeckVector
from src.muc5.perf import benchmark_agent_games, benchmark_public_decision_games, profile_agent_games



def main() -> None:
    deck = DeckVector(40, 24, 6, 4, 3, 3)
    trusted_fast = benchmark_agent_games(deck, deck, games=120, max_decisions=500, validate_actions=False, record_log=False, seed_base=11100)
    trusted_validated = benchmark_agent_games(deck, deck, games=120, max_decisions=500, validate_actions=True, record_log=False, seed_base=11200)
    public_frame = benchmark_public_decision_games(deck, deck, games=120, max_decisions=500, record_log=False, seed_base=11300)
    summary = {
        "revision": "rev0010",
        "trusted_fast": trusted_fast.as_dict(),
        "trusted_validated": trusted_validated.as_dict(),
        "public_decision_frame": public_frame.as_dict(),
        "recommendation": "Keep learning/search/evolution on the public DecisionFrame path; optimize repeated observation construction before using compiled extensions.",
    }
    (ROOT / "data" / "rev0010_simulator_profile_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True))
    (ROOT / "data" / "rev0010_cprofile_top.txt").write_text(profile_agent_games(deck, deck, games=60, max_decisions=500, validate_actions=False, limit=35))
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
