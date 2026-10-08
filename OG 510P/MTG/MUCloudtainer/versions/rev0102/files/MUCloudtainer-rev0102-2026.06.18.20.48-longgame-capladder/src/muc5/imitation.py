from __future__ import annotations

from dataclasses import asdict, dataclass
from random import Random
from typing import Iterable, Mapping, Sequence

from .action_features import action_feature_dict, action_feature_names
from .cards import CARD_COUNTERSPELL, CARD_FORCE, CARD_ISLAND, CARD_JACE, CARD_ORDER, CARD_OVERLORD
from .decision import PublicDecisionAgent, apply_decision_index, build_decision_frame
from .deckspace import DeckVector
from .engine import start_game
from .mulligan import MulliganPolicy


CONTEXT_FEATURE_NAMES: tuple[str, ...] = (
    "ctx_frame_main", "ctx_frame_response", "ctx_frame_attack", "ctx_frame_block",
    "ctx_main_precombat", "ctx_main_postcombat",
    "ctx_life20", "ctx_life40", "ctx_own_life_frac", "ctx_opp_life_frac",
    "ctx_own_untapped_norm", "ctx_opp_untapped_norm", "ctx_own_tapped_norm", "ctx_opp_tapped_norm",
    "ctx_own_hand_norm", "ctx_opp_hand_norm", "ctx_own_library_norm", "ctx_opp_library_norm",
    "ctx_own_has_jace", "ctx_opp_has_jace", "ctx_own_jace_loyalty_norm", "ctx_opp_jace_loyalty_norm",
    "ctx_own_overlord_ready_norm", "ctx_opp_overlord_ready_norm",
    "ctx_own_overlord_total_norm", "ctx_opp_overlord_total_norm",
    "ctx_stack_depth_norm", "ctx_pending_choice", "ctx_pending_discard", "ctx_pending_jace_choice",
) + tuple(f"ctx_hand_{card.lower()}_norm" for card in CARD_ORDER)


@dataclass(frozen=True)
class ImitationCollectionSummary:
    games: int
    decisions: int
    rows: int
    chosen_rows: int
    terminal_games: int
    truncated_games: int
    max_action_count: int
    mean_action_count: float

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def context_feature_names() -> tuple[str, ...]:
    return CONTEXT_FEATURE_NAMES


def _zone(obs: Mapping[str, object], key: str) -> Mapping[str, object]:
    value = obs.get(key)
    return value if isinstance(value, Mapping) else {}


def _norm(x: float, denom: float) -> float:
    if denom <= 0:
        return 0.0
    value = float(x) / float(denom)
    if value < 0:
        return 0.0
    if value > 1:
        return 1.0
    return value


def context_feature_dict(obs: Mapping[str, object]) -> dict[str, float]:
    frame = str(obs.get("frame", ""))
    main = str(obs.get("main_phase", ""))
    starting_life = float(obs.get("starting_life", 20) or 20)
    self_public = _zone(obs, "public_self")
    opp_public = _zone(obs, "public_opponent")
    own_hand = _zone(obs, "own_hand")
    pending_kind = str(obs.get("pending_choice_kind") or "")
    stack = obs.get("stack", [])
    stack_depth = len(stack) if isinstance(stack, list) else 0

    own_overlord_total = sum(int(self_public.get(k, 0) or 0) for k in ("overlord_ready", "overlord_sick", "overlord_tapped"))
    opp_overlord_total = sum(int(opp_public.get(k, 0) or 0) for k in ("overlord_ready", "overlord_sick", "overlord_tapped"))
    own_jace = self_public.get("jace_loyalty")
    opp_jace = opp_public.get("jace_loyalty")

    out = {name: 0.0 for name in CONTEXT_FEATURE_NAMES}
    out["ctx_frame_main"] = 1.0 if frame == "MAIN" else 0.0
    out["ctx_frame_response"] = 1.0 if frame == "RESPONSE" else 0.0
    out["ctx_frame_attack"] = 1.0 if frame == "ATTACK" else 0.0
    out["ctx_frame_block"] = 1.0 if frame == "BLOCK" else 0.0
    out["ctx_main_precombat"] = 1.0 if main == "precombat" else 0.0
    out["ctx_main_postcombat"] = 1.0 if main == "postcombat" else 0.0
    out["ctx_life20"] = 1.0 if int(starting_life) == 20 else 0.0
    out["ctx_life40"] = 1.0 if int(starting_life) == 40 else 0.0
    out["ctx_own_life_frac"] = _norm(float(self_public.get("life", starting_life) or 0), starting_life)
    out["ctx_opp_life_frac"] = _norm(float(opp_public.get("life", starting_life) or 0), starting_life)
    out["ctx_own_untapped_norm"] = _norm(float(self_public.get("islands_untapped", 0) or 0), 10.0)
    out["ctx_opp_untapped_norm"] = _norm(float(opp_public.get("islands_untapped", 0) or 0), 10.0)
    out["ctx_own_tapped_norm"] = _norm(float(self_public.get("islands_tapped", 0) or 0), 10.0)
    out["ctx_opp_tapped_norm"] = _norm(float(opp_public.get("islands_tapped", 0) or 0), 10.0)
    out["ctx_own_hand_norm"] = _norm(float(self_public.get("hand_count", 0) or 0), 12.0)
    out["ctx_opp_hand_norm"] = _norm(float(opp_public.get("hand_count", 0) or 0), 12.0)
    out["ctx_own_library_norm"] = _norm(float(self_public.get("library_count", 0) or 0), 60.0)
    out["ctx_opp_library_norm"] = _norm(float(opp_public.get("library_count", 0) or 0), 60.0)
    out["ctx_own_has_jace"] = 1.0 if own_jace is not None else 0.0
    out["ctx_opp_has_jace"] = 1.0 if opp_jace is not None else 0.0
    out["ctx_own_jace_loyalty_norm"] = _norm(float(own_jace or 0), 15.0)
    out["ctx_opp_jace_loyalty_norm"] = _norm(float(opp_jace or 0), 15.0)
    out["ctx_own_overlord_ready_norm"] = _norm(float(self_public.get("overlord_ready", 0) or 0), 4.0)
    out["ctx_opp_overlord_ready_norm"] = _norm(float(opp_public.get("overlord_ready", 0) or 0), 4.0)
    out["ctx_own_overlord_total_norm"] = _norm(float(own_overlord_total), 6.0)
    out["ctx_opp_overlord_total_norm"] = _norm(float(opp_overlord_total), 6.0)
    out["ctx_stack_depth_norm"] = _norm(float(stack_depth), 6.0)
    out["ctx_pending_choice"] = 1.0 if pending_kind and pending_kind != "None" else 0.0
    out["ctx_pending_discard"] = 1.0 if pending_kind in {"discard", "cleanup_discard"} else 0.0
    out["ctx_pending_jace_choice"] = 1.0 if pending_kind.startswith("jace_") else 0.0
    for card in CARD_ORDER:
        out[f"ctx_hand_{card.lower()}_norm"] = _norm(float(own_hand.get(card, 0) or 0), 8.0)
    return out


def action_ranker_feature_names() -> tuple[str, ...]:
    return CONTEXT_FEATURE_NAMES + action_feature_names()


def collect_action_imitation_rows(
    games: Sequence[tuple[DeckVector, DeckVector, PublicDecisionAgent, PublicDecisionAgent, int, int, tuple[str | MulliganPolicy | None, str | MulliganPolicy | None]]],
    *,
    seed_base: int = 2002000,
    max_decisions: int = 360,
) -> tuple[list[dict[str, object]], ImitationCollectionSummary]:
    """Collect listwise candidate-action rows from public DecisionFrame agents.

    Every row is one legal action candidate. The target label is `chosen`, one per
    decision frame. Features are public observation features plus stable action
    features; no `GameState` or opponent hidden hand/library is exposed.
    """

    rows: list[dict[str, object]] = []
    decisions = 0
    terminal_games = 0
    truncated_games = 0
    action_counts: list[int] = []
    for game_i, (deck0, deck1, agent0, agent1, starting_player, starting_life, mulligans) in enumerate(games):
        state_seed = seed_base + game_i
        state_rng = Random(state_seed)
        agent_rng = Random(seed_base + 100000 + game_i)
        state = start_game(
            deck0,
            deck1,
            seed=state_seed,
            starting_player=starting_player,
            starting_life=starting_life,
            mulligan_policies=mulligans,
            record_log=False,
        )
        agents = [agent0, agent1]
        for step in range(1, max_decisions + 1):
            if state.winner is not None:
                break
            frame = build_decision_frame(state)
            if frame.action_count <= 0:
                break
            chosen_idx = int(agents[frame.player].choose_action_index(frame, agent_rng))
            if chosen_idx < 0 or chosen_idx >= frame.action_count:
                raise ValueError(f"agent chose illegal action index {chosen_idx}")
            decisions += 1
            action_counts.append(frame.action_count)
            ctx = context_feature_dict(frame.observation)
            decision_id = f"g{game_i:04d}_s{step:04d}"
            for action_idx, action in enumerate(frame.legal_actions):
                feats = {}
                feats.update(ctx)
                feats.update(action_feature_dict(action, frame.observation))
                row: dict[str, object] = {
                    "game_index": game_i,
                    "decision_id": decision_id,
                    "step": step,
                    "player": frame.player,
                    "agent_name": getattr(agents[frame.player], "name", type(agents[frame.player]).__name__),
                    "starting_player": starting_player,
                    "starting_life": starting_life,
                    "action_index": action_idx,
                    "action_count": frame.action_count,
                    "chosen": 1 if action_idx == chosen_idx else 0,
                    "action": action.compact(),
                }
                row.update(feats)
                rows.append(row)
            apply_decision_index(state, frame, chosen_idx, state_rng)
        if state.winner is not None:
            terminal_games += 1
        else:
            truncated_games += 1
    summary = ImitationCollectionSummary(
        games=len(games),
        decisions=decisions,
        rows=len(rows),
        chosen_rows=sum(int(r["chosen"]) for r in rows),
        terminal_games=terminal_games,
        truncated_games=truncated_games,
        max_action_count=max(action_counts) if action_counts else 0,
        mean_action_count=(sum(action_counts) / len(action_counts)) if action_counts else 0.0,
    )
    return rows, summary
