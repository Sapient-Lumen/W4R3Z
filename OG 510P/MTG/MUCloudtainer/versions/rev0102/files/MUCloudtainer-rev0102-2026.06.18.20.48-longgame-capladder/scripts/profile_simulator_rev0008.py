from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.payoff import load_seed_decks
from src.muc5.perf import benchmark_agent_games, profile_agent_games


def main() -> None:
    decks = load_seed_decks(ROOT / "data" / "seed_decks.json")
    deck0 = decks["forty_force_jace_pressure"]
    deck1 = decks["sixty_overlord_heavy"]
    fast = benchmark_agent_games(deck0, deck1, games=120, max_decisions=500, starting_life=20, validate_actions=False, record_log=False)
    validated = benchmark_agent_games(deck0, deck1, games=120, max_decisions=500, starting_life=20, validate_actions=True, record_log=False)
    logged = benchmark_agent_games(deck0, deck1, games=120, max_decisions=500, starting_life=20, validate_actions=False, record_log=True)
    profile_text = profile_agent_games(deck0, deck1, games=40, max_decisions=500, starting_life=20, validate_actions=False, limit=40)
    speedup = validated.seconds / max(1e-12, fast.seconds)
    log_overhead = logged.seconds / max(1e-12, fast.seconds)
    summary = {
        "revision": "rev0008",
        "benchmark_decks": ["forty_force_jace_pressure", "sixty_overlord_heavy"],
        "fast_unvalidated": fast.as_dict(),
        "validated": validated.as_dict(),
        "logged_unvalidated": logged.as_dict(),
        "validated_seconds_div_fast_seconds": speedup,
        "logged_seconds_div_fast_seconds": log_overhead,
        "interpretation": "Values vary by machine. The useful signal is whether trusted legal actions avoid enough duplicate legal_action enumeration to matter.",
    }
    (ROOT / "data" / "rev0008_simulator_profile_summary.json").write_text(json.dumps(summary, indent=2))
    (ROOT / "data" / "rev0008_cprofile_top.txt").write_text(profile_text)
    print(json.dumps(summary, indent=2))
    print("\n--- cProfile top cumulative ---")
    print(profile_text)


if __name__ == "__main__":
    main()
