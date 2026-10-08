#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from random import Random

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.cards import CARD_JACE
from src.muc5.decision import PublicHeuristicAgent, build_decision_frame, apply_decision_index
from src.muc5.deckspace import DeckVector
from src.muc5.engine import PendingChoice, start_game
from src.muc5.fairness import audit_observation_shape, summarize_checks
from src.muc5.mulligan import POLICY_LAND_BAND


def main() -> None:
    deck = DeckVector(40, 24, 6, 4, 3, 3)
    state = start_game(deck, deck, seed=9909, starting_player=0, mulligan_policy=POLICY_LAND_BAND, record_log=False)

    # Synthetic Jace +2 private-information frame: player 0 sees player 1's top card.
    state.pending_choice = PendingChoice(0, "jace_plus2", {"target_player": 1, "seen_top_card": CARD_JACE, "resume": "MAIN"})
    checks = []
    checks.extend(audit_observation_shape(state, 0))
    checks.extend(audit_observation_shape(state, 1))

    obs_actor = state.observation(0)
    obs_non_actor = state.observation(1)
    actor_sees = obs_actor["pending_choice_data"].get("seen_top_card") == CARD_JACE
    non_actor_redacted = obs_non_actor["pending_choice_data"].get("redacted") is True and "seen_top_card" not in obs_non_actor["pending_choice_data"]
    checks_payload = summarize_checks(checks)
    checks_payload["actor_sees_jace_plus2_card"] = actor_sees
    checks_payload["non_actor_pending_data_redacted"] = non_actor_redacted

    # Decision-frame fast path: using the same frame twice must fail after revision advances.
    state.pending_choice = None
    frame = build_decision_frame(state)
    rng = Random(9909)
    idx = PublicHeuristicAgent().choose_action_index(frame, rng)
    chosen = apply_decision_index(state, frame, idx, rng)
    stale_rejected = False
    try:
        apply_decision_index(state, frame, idx, rng)
    except ValueError:
        stale_rejected = True
    checks_payload["decision_frame_action"] = chosen.compact()
    checks_payload["decision_frame_stale_reuse_rejected"] = stale_rejected
    checks_payload["overall_passed"] = checks_payload["failed"] == 0 and actor_sees and non_actor_redacted and stale_rejected

    out = ROOT / "data" / "rev0009_leakage_audit.json"
    out.write_text(json.dumps(checks_payload, indent=2, sort_keys=True))
    print(json.dumps(checks_payload, indent=2, sort_keys=True))
    if not checks_payload["overall_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
