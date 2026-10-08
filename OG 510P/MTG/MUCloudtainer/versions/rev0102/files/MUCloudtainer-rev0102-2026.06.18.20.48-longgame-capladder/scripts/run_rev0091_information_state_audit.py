#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from random import Random

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))

from src.muc5.action_schema import activate_jace, choose
from src.muc5.cards import CARD_COUNTERSPELL, CARD_FORCE, CARD_ISLAND, CARD_JACE
from src.muc5.decision import PublicHeuristicAgent
from src.muc5.deckspace import DeckVector
from src.muc5.engine import GameState, PlayerState, StackSpell, apply_action, legal_actions
from src.muc5.fairness import all_checks_pass, audit_observation_shape
from src.muc5.replay import record_public_decision_trace, replay_public_decision_trace

REVISION = "rev0091"


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    detail: dict[str, object]


def add(checks: list[Check], name: str, passed: bool, **detail: object) -> None:
    checks.append(Check(name=name, passed=bool(passed), detail=detail))


def jace_leave_state() -> GameState:
    return GameState(
        players=[
            PlayerState(library=[CARD_ISLAND], jace_loyalty=3),
            PlayerState(library=[CARD_ISLAND, CARD_FORCE]),
        ],
        active_player=0,
        frame="MAIN",
    )


def run() -> dict[str, object]:
    checks: list[Check] = []

    state = jace_leave_state()
    apply_action(state, activate_jace("plus2", target_player="opponent"), Random(9101))
    actor_info_pending = state.information_state(0)
    non_actor_info_pending = state.information_state(1)
    add(
        checks,
        "jace_plus2_pending_private_card_only_for_actor",
        actor_info_pending["known_top_cards"] == {"1": CARD_FORCE}
        and CARD_FORCE not in json.dumps(non_actor_info_pending, sort_keys=True),
        actor_known=actor_info_pending["known_top_cards"],
        non_actor_public_event_kinds=[ev["kind"] for ev in non_actor_info_pending["public_events"]],
    )
    add(
        checks,
        "jace_plus2_observation_allowlist",
        all_checks_pass(audit_observation_shape(state, 0)) and all_checks_pass(audit_observation_shape(state, 1)),
        actor_checks=len(audit_observation_shape(state, 0)),
        non_actor_checks=len(audit_observation_shape(state, 1)),
    )
    apply_action(state, choose("jace_plus2", put="leave"), Random(9101))
    actor_info_resolved = state.information_state(0)
    add(
        checks,
        "jace_plus2_leave_persists_after_choice_resolution",
        state.pending_choice is None and actor_info_resolved["known_top_cards"] == {"1": CARD_FORCE},
        known_top_cards=actor_info_resolved["known_top_cards"],
        public_events=[ev for ev in actor_info_resolved["public_events"] if ev["kind"].startswith("JACE_PLUS2")],
    )

    bottom_state = jace_leave_state()
    apply_action(bottom_state, activate_jace("plus2", target_player="opponent"), Random(9102))
    apply_action(bottom_state, choose("jace_plus2", put="bottom"), Random(9102))
    add(
        checks,
        "jace_plus2_bottom_clears_known_top",
        bottom_state.information_state(0)["known_top_cards"] == {} and bottom_state.players[1].library[0] == CARD_FORCE,
        known_top_cards=bottom_state.information_state(0)["known_top_cards"],
        bottom_card=bottom_state.players[1].library[0],
    )

    force_state = GameState(
        players=[
            PlayerState(hand={CARD_FORCE: 1, CARD_COUNTERSPELL: 1}, life=20),
            PlayerState(),
        ],
        active_player=1,
        priority_player=0,
        frame="RESPONSE",
        stack=[StackSpell(1, 1, CARD_JACE)],
    )
    force_action = next(
        a
        for a in legal_actions(force_state)
        if a.kind == "CAST" and a.params.get("card") == CARD_FORCE and a.params.get("payment") == "pitch"
    )
    apply_action(force_state, force_action, Random(9103))
    opp_obs = force_state.observation(1)
    add(
        checks,
        "force_pitch_identity_is_public_exile_and_event",
        opp_obs["public_opponent"].get("exile", {}).get(CARD_COUNTERSPELL) == 1
        and any(ev["kind"] == "FORCE_PITCH_PAYMENT" and ev.get("pitch_card") == CARD_COUNTERSPELL for ev in force_state.public_events),
        public_opponent_exile=opp_obs["public_opponent"].get("exile", {}),
        force_events=[ev for ev in force_state.public_events if ev["kind"] == "FORCE_PITCH_PAYMENT"],
    )

    deck = DeckVector(40, 24, 6, 4, 3, 3)
    trace = record_public_decision_trace(
        deck,
        deck,
        PublicHeuristicAgent(),
        PublicHeuristicAgent(),
        seed=9104,
        transition_seed=9105,
        agent_seed=9106,
        max_decisions=18,
    )
    replay = replay_public_decision_trace(trace)
    tampered = dict(trace)
    tampered["events"] = [dict(event) for event in trace["events"]]
    if tampered["events"]:
        tampered["events"][0]["information_state_fingerprint"] = "not-the-real-info-hash"
    tampered_replay = replay_public_decision_trace(tampered)
    add(
        checks,
        "replay_trace_records_and_checks_information_state_hash",
        bool(trace["events"])
        and "information_state_fingerprint" in trace["events"][0]
        and replay.passed
        and not tampered_replay.passed
        and tampered_replay.errors
        and "information_state_fingerprint" in tampered_replay.errors[0],
        event_fields=sorted(trace["events"][0].keys()) if trace["events"] else [],
        replay_passed=replay.passed,
        tampered_errors=list(tampered_replay.errors),
    )

    payload = {
        "revision": REVISION,
        "schema": "muc5.information_state_audit.v1",
        "passed": all(check.passed for check in checks),
        "checks": [asdict(check) for check in checks],
        "summary": {
            "check_count": len(checks),
            "passed_count": sum(1 for check in checks if check.passed),
            "failed_count": sum(1 for check in checks if not check.passed),
            "substantive_changes": [
                "DecisionFrame carries an information_state alongside observation and legal_actions.",
                "Jace +2 top-card knowledge persists after leave and clears after bottom.",
                "Force pitch identities are public through exile identity and public events.",
                "Replay traces can bind information-state fingerprints without invalidating old traces.",
            ],
        },
    }
    return payload


def main() -> None:
    output = ROOT / "data" / f"{REVISION}_information_state_audit.json"
    payload = run()
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"revision": REVISION, "passed": payload["passed"], "checks": payload["summary"]}, indent=2, sort_keys=True))
    if not payload["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
