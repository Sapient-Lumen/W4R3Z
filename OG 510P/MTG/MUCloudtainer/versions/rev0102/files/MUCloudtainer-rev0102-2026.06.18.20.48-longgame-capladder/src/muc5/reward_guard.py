from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Tuple

from .engine import GameState


@dataclass(frozen=True)
class RewardPacket:
    """Explicit reward/evaluation packet for one perspective.

    The project intentionally separates terminal outcome, draw convention,
    truncation, and diagnostic quantities so later learning code cannot silently
    optimize a proxy that was only meant for reporting.
    """

    perspective: int
    winner: int | None
    loss_reason: str
    terminal_win: bool
    terminal_loss: bool
    is_nonterminal_draw: bool
    is_truncation: bool
    draw_half_score: float
    terminal_only_score: float | None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "perspective": self.perspective,
            "winner": self.winner,
            "loss_reason": self.loss_reason,
            "terminal_win": self.terminal_win,
            "terminal_loss": self.terminal_loss,
            "is_nonterminal_draw": self.is_nonterminal_draw,
            "is_truncation": self.is_truncation,
            "draw_half_score": self.draw_half_score,
            "terminal_only_score": self.terminal_only_score,
        }


def reward_packet_from_state(state: GameState, perspective: int) -> RewardPacket:
    if perspective not in (0, 1):
        raise ValueError("perspective must be 0 or 1")
    winner = state.winner
    is_truncation = state.loss_reason == "max_decisions_reached"
    terminal_win = winner == perspective
    terminal_loss = winner is not None and winner != perspective
    is_nonterminal_draw = winner is None
    draw_half_score = 1.0 if terminal_win else 0.0 if terminal_loss else 0.5
    terminal_only_score = 1.0 if terminal_win else 0.0 if terminal_loss else None
    return RewardPacket(
        perspective=perspective,
        winner=winner,
        loss_reason=state.loss_reason,
        terminal_win=terminal_win,
        terminal_loss=terminal_loss,
        is_nonterminal_draw=is_nonterminal_draw,
        is_truncation=is_truncation,
        draw_half_score=draw_half_score,
        terminal_only_score=terminal_only_score,
    )


def audit_reward_packet(packet: RewardPacket, *, allow_truncation_training_reward: bool = False) -> Tuple[bool, Tuple[str, ...]]:
    errors = []
    if packet.terminal_win and packet.terminal_loss:
        errors.append("packet cannot be both terminal_win and terminal_loss")
    if packet.is_nonterminal_draw and packet.terminal_only_score is not None:
        errors.append("nonterminal draw should not have terminal_only_score")
    if packet.is_truncation and packet.draw_half_score != 0.5:
        errors.append("truncation should be scored only by explicit draw convention")
    if packet.is_truncation and not allow_truncation_training_reward:
        # This is a warning-shaped failure for training configs. It is fine for
        # reporting, but should not be silently used as a dense reward target.
        errors.append("truncation reward requires explicit opt-in for training")
    return (not errors, tuple(errors))


def trajectory_diagnostics(state: GameState, *, decisions: int | None = None) -> Dict[str, Any]:
    return {
        "winner": state.winner,
        "loss_reason": state.loss_reason,
        "is_truncation": state.loss_reason == "max_decisions_reached",
        "is_terminal_winloss": state.winner is not None,
        "turn_number": state.turn_number,
        "decisions": decisions,
        "starting_life": state.starting_life,
        "p0_life": state.players[0].life,
        "p1_life": state.players[1].life,
        "p0_library_count": len(state.players[0].library),
        "p1_library_count": len(state.players[1].library),
        "p0_hand_count": state.players[0].total_hand(),
        "p1_hand_count": state.players[1].total_hand(),
        "p0_jace_loyalty": state.players[0].jace_loyalty,
        "p1_jace_loyalty": state.players[1].jace_loyalty,
        "p0_overlord_creatures": state.players[0].total_overlord_creatures(),
        "p1_overlord_creatures": state.players[1].total_overlord_creatures(),
        "p0_impending_total": state.players[0].impending_1 + state.players[0].impending_2 + state.players[0].impending_3 + state.players[0].impending_4,
        "p1_impending_total": state.players[1].impending_1 + state.players[1].impending_2 + state.players[1].impending_3 + state.players[1].impending_4,
    }


def audit_payoff_like_row(row: Mapping[str, Any]) -> Tuple[bool, Tuple[str, ...]]:
    """Cheap guard for CSV payoff rows before they become training labels."""
    errors = []
    if "is_truncation" in row and str(row.get("is_truncation")).lower() in {"true", "1"}:
        if str(row.get("p0_terminal_win", "False")).lower() in {"true", "1"}:
            errors.append("truncation row should not also claim p0_terminal_win")
        if str(row.get("p1_terminal_win", "False")).lower() in {"true", "1"}:
            errors.append("truncation row should not also claim p1_terminal_win")
    for key in ("p0_score", "p1_score"):
        if key in row:
            try:
                v = float(row[key])
            except Exception:
                errors.append(f"{key} is not numeric")
                continue
            if not (0.0 <= v <= 1.0):
                errors.append(f"{key} outside [0, 1]")
    return (not errors, tuple(errors))
