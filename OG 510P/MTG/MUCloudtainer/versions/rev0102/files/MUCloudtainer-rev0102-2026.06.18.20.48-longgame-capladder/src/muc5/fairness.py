from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, Iterable, List, Mapping, Sequence

from .cards import CARD_ORDER
from .engine import GameState, PendingChoice


@dataclass(frozen=True)
class ObservationLeakCheck:
    name: str
    passed: bool
    detail: str

    def as_dict(self) -> Dict[str, object]:
        return asdict(self)


PUBLIC_PLAYER_KEYS = {
    "life",
    "mulligans_taken",
    "library_count",
    "hand_count",
    "graveyard",
    "exile",
    "exile_count",
    "islands_untapped",
    "islands_tapped",
    "jace_loyalty",
    "jace_used_this_turn",
    "overlord_ready",
    "overlord_sick",
    "overlord_tapped",
    "impending_4",
    "impending_3",
    "impending_2",
    "impending_1",
}

OBSERVATION_TOP_LEVEL_KEYS = {
    "player",
    "active_player",
    "to_act",
    "frame",
    "main_phase",
    "turn_number",
    "starting_life",
    "starting_life_total",
    "own_hand",
    "own_library_count",
    "public_self",
    "public_opponent",
    "stack",
    "pending_choice_kind",
    "pending_choice_data",
}


def audit_observation_shape(state: GameState, player: int) -> List[ObservationLeakCheck]:
    """Cheap static checks for the public observation boundary.

    This cannot prove absence of all leaks, but it catches the easy failures that
    tend to creep into card-game environments: opponent hand contents, opponent
    library order, and private pending-choice payloads shown to the wrong player.
    """

    obs = state.observation(player)
    checks: List[ObservationLeakCheck] = []
    keys = set(obs.keys())
    extras = sorted(keys - OBSERVATION_TOP_LEVEL_KEYS)
    checks.append(ObservationLeakCheck("top_level_key_allowlist", not extras, f"extras={extras}"))

    opp_public = obs.get("public_opponent", {}) or {}
    opp_public_keys = set(opp_public.keys())
    extras = sorted(opp_public_keys - PUBLIC_PLAYER_KEYS)
    checks.append(ObservationLeakCheck("opponent_public_key_allowlist", not extras, f"extras={extras}"))

    for forbidden_key in ("hand", "library", "library_order", "deck", "starting_deck_counts"):
        checks.append(
            ObservationLeakCheck(
                f"no_forbidden_top_key_{forbidden_key}",
                forbidden_key not in obs,
                "absent" if forbidden_key not in obs else "present",
            )
        )
        checks.append(
            ObservationLeakCheck(
                f"no_forbidden_opp_public_key_{forbidden_key}",
                forbidden_key not in opp_public,
                "absent" if forbidden_key not in opp_public else "present",
            )
        )

    pending = state.pending_choice
    pending_data = obs.get("pending_choice_data")
    if pending is not None and pending.player != player:
        contains_seen_card = isinstance(pending_data, Mapping) and "seen_top_card" in pending_data
        checks.append(
            ObservationLeakCheck(
                "pending_choice_redacted_for_non_actor",
                not contains_seen_card and isinstance(pending_data, Mapping) and pending_data.get("redacted") is True,
                f"pending_data={pending_data}",
            )
        )
    return checks


def all_checks_pass(checks: Iterable[ObservationLeakCheck]) -> bool:
    return all(c.passed for c in checks)


def summarize_checks(checks: Sequence[ObservationLeakCheck]) -> Dict[str, object]:
    failed = [c.as_dict() for c in checks if not c.passed]
    return {
        "checks": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "failed_checks": failed,
    }
