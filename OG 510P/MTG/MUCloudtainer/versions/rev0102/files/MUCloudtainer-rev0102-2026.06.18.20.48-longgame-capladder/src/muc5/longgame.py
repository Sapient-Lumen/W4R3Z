from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable, Mapping, Sequence

from .agents import play_public_agent_game
from .evaluation_design import balanced_pair_cells
from .psro import EmpiricalEvaluationConfig, EmpiricalGameEvaluator, PairEstimate, estimate_scores, stable_seed
from .payoff import StrategyBundle


@dataclass(frozen=True)
class LongGameAxisSummary:
    """Diagnostic summary for a focal strategy on a long-game stress axis.

    This is intentionally not an adjudication rule.  Nonterminal cap rows remain
    scored as 0.5 under the ordinary payoff convention.  The snapshot fields and
    diagnostic advantage classify *why* a cap was reached so later revisions can
    either raise caps, improve pilots, or register a draw-like subgame.
    """

    focal_strategy: str
    opponent_strategy: str
    games: int
    mean_score: float
    ci_low: float
    ci_high: float
    truncations: int
    max_decisions: int
    max_turn_number: int
    mean_decisions: float
    nonterminal_diagnostic_min: float
    nonterminal_diagnostic_max: float
    nonterminal_class_counts: dict[str, int]
    confidence_floor_cleared: bool
    threshold: float = 0.5

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def _count_zone(zone: Mapping[str, int]) -> int:
    return int(sum(int(value) for value in zone.values()))


def _jace_value(loyalty: int | None) -> int:
    return -1 if loyalty is None else int(loyalty)


def _overlord_total(player) -> int:  # type: ignore[no-untyped-def]
    return int(player.overlord_ready + player.overlord_sick + player.overlord_tapped + player.impending_1 + player.impending_2 + player.impending_3 + player.impending_4)


def _nonterminal_advantage(state, focal_player: int) -> float:  # type: ignore[no-untyped-def]
    """Return a bounded diagnostic resource index for cap rows.

    Positive values favor the focal player.  The weights deliberately remain
    conservative and are never used to replace terminal payoff.  They exist to
    distinguish an obvious-but-slow win from a near-symmetric control lock.
    """

    opponent = 1 - int(focal_player)
    focal = state.players[int(focal_player)]
    other = state.players[opponent]
    starting_life = max(1.0, float(state.starting_life or 1))
    max_deck = max(1.0, float(max(sum(state.starting_deck_counts[int(focal_player)].values()), sum(state.starting_deck_counts[opponent].values()))))
    life_component = (float(focal.life) - float(other.life)) / starting_life
    library_component = (float(focal.total_library()) - float(other.total_library())) / max_deck
    hand_component = (float(focal.total_hand()) - float(other.total_hand())) / 10.0
    jace_component = (float(_jace_value(focal.jace_loyalty)) - float(_jace_value(other.jace_loyalty))) / 12.0
    overlord_component = (float(_overlord_total(focal)) - float(_overlord_total(other))) / 8.0
    raw = 0.30 * life_component + 0.25 * library_component + 0.15 * hand_component + 0.20 * jace_component + 0.10 * overlord_component
    return max(-1.0, min(1.0, float(raw)))


def classify_nonterminal_snapshot(snapshot: Mapping[str, object], *, threshold: float = 0.20) -> str:
    if snapshot.get("loss_reason") != "max_decisions_reached":
        return "terminal"
    advantage = float(snapshot.get("diagnostic_focal_advantage", 0.0) or 0.0)
    focal_library = int(snapshot.get("focal_library_count", 0) or 0)
    opponent_library = int(snapshot.get("opponent_library_count", 0) or 0)
    if min(focal_library, opponent_library) <= 2:
        return "library_edge_cap"
    if advantage >= threshold:
        return "focal_apparent_advantage_cap"
    if advantage <= -threshold:
        return "opponent_apparent_advantage_cap"
    return "balanced_control_cap"


def longgame_snapshot(state, result, *, focal_player: int) -> dict[str, object]:  # type: ignore[no-untyped-def]
    """Flatten public/count-only terminal state diagnostics for CSV evidence.

    The snapshot avoids hidden card identities in hand or library.  It exposes
    counts, public zones, and Jace/board state needed to audit long control games.
    """

    focal_player = int(focal_player)
    opponent_player = 1 - focal_player
    players = state.players
    focal = players[focal_player]
    opponent = players[opponent_player]
    advantage = _nonterminal_advantage(state, focal_player)
    payload = {
        "winner": "None" if result.winner is None else int(result.winner),
        "loss_reason": str(result.loss_reason),
        "decisions": int(result.decisions),
        "turn_number": int(state.turn_number),
        "event_seq": int(getattr(state, "event_seq", 0)),
        "starting_life_total": int(state.starting_life),
        "focal_player": focal_player,
        "opponent_player": opponent_player,
        "focal_life": int(focal.life),
        "opponent_life": int(opponent.life),
        "focal_library_count": int(focal.total_library()),
        "opponent_library_count": int(opponent.total_library()),
        "focal_hand_count": int(focal.total_hand()),
        "opponent_hand_count": int(opponent.total_hand()),
        "focal_graveyard_count": _count_zone(focal.graveyard),
        "opponent_graveyard_count": _count_zone(opponent.graveyard),
        "focal_exile_count": _count_zone(focal.exile),
        "opponent_exile_count": _count_zone(opponent.exile),
        "focal_jace_loyalty": _jace_value(focal.jace_loyalty),
        "opponent_jace_loyalty": _jace_value(opponent.jace_loyalty),
        "focal_overlord_total": _overlord_total(focal),
        "opponent_overlord_total": _overlord_total(opponent),
        "focal_islands_total": int(focal.islands_untapped + focal.islands_tapped),
        "opponent_islands_total": int(opponent.islands_untapped + opponent.islands_tapped),
        "diagnostic_focal_advantage": advantage,
        "hidden_identity_leakage_guard": "counts_only_no_hand_or_library_identities",
    }
    payload["nonterminal_class"] = classify_nonterminal_snapshot(payload)
    return payload


def evaluate_focal_pair_with_snapshots(
    evaluator: EmpiricalGameEvaluator,
    focal: StrategyBundle,
    opponent: StrategyBundle,
    config: EmpiricalEvaluationConfig,
    *,
    stage: str,
) -> tuple[PairEstimate, list[dict[str, object]]]:
    scores: list[float] = []
    rows: list[dict[str, object]] = []
    truncations = 0
    for cell in balanced_pair_cells(config.life_totals, config.reps):
        life = int(cell.starting_life)
        rep = int(cell.rep)
        orientation = int(cell.orientation)
        starting_player = int(cell.starting_player)
        seat0, seat1 = (focal, opponent) if orientation == 0 else (opponent, focal)
        focal_player = int(cell.focal_player)
        seed = stable_seed(
            config.base_seed,
            stage,
            focal.strategy_id,
            opponent.strategy_id,
            life,
            rep,
            orientation,
            starting_player,
        )
        state, result = play_public_agent_game(
            seat0.deck,
            seat1.deck,
            evaluator.agent(seat0, 0),  # type: ignore[arg-type]
            evaluator.agent(seat1, 1),  # type: ignore[arg-type]
            seed=seed,
            transition_seed=seed,
            agent_seed=seed + 1000003,
            starting_player=starting_player,
            starting_life=life,
            max_decisions=int(config.max_decisions),
            mulligan_agents=(evaluator.mulligan(seat0, 0), evaluator.mulligan(seat1, 1)),  # type: ignore[arg-type]
            record_log=False,
            episode_id=f"{stage}:{focal.strategy_id}:{opponent.strategy_id}:{life}:{rep}:{orientation}:{starting_player}",
        )
        score = 0.5 if result.winner is None else (1.0 if result.winner == focal_player else 0.0)
        truncation = result.loss_reason == "max_decisions_reached"
        scores.append(score)
        truncations += int(truncation)
        snapshot = longgame_snapshot(state, result, focal_player=focal_player)
        rows.append(
            {
                "stage": stage,
                "focal_strategy": focal.strategy_id,
                "opponent_strategy": opponent.strategy_id,
                "strategy0": seat0.strategy_id,
                "strategy1": seat1.strategy_id,
                "starting_life": life,
                "rep": rep,
                "orientation": orientation,
                "starting_player": starting_player,
                "seed": seed,
                "transition_seed": seed,
                "agent_seed": seed + 1000003,
                "score": score,
                "truncation": truncation,
                "interface": "public_decision_frame+information_state",
                **snapshot,
            }
        )
    estimate = estimate_scores(
        focal.strategy_id,
        opponent.strategy_id,
        scores,
        truncations=truncations,
        confidence_z=config.confidence_z,
    )
    return estimate, rows


def run_cap_ladder_cell(
    evaluator: EmpiricalGameEvaluator,
    focal: StrategyBundle,
    opponent: StrategyBundle,
    *,
    original_stage: str,
    ladder_stage: str,
    base_seed: int,
    starting_life: int,
    rep: int,
    orientation: int,
    starting_player: int,
    max_decision_caps: Sequence[int],
) -> list[dict[str, object]]:
    if not max_decision_caps:
        raise ValueError("max_decision_caps cannot be empty")
    rows: list[dict[str, object]] = []
    seed = stable_seed(
        int(base_seed),
        original_stage,
        focal.strategy_id,
        opponent.strategy_id,
        int(starting_life),
        int(rep),
        int(orientation),
        int(starting_player),
    )
    for cap in max_decision_caps:
        seat0, seat1 = (focal, opponent) if int(orientation) == 0 else (opponent, focal)
        focal_player = 0 if int(orientation) == 0 else 1
        state, result = play_public_agent_game(
            seat0.deck,
            seat1.deck,
            evaluator.agent(seat0, 0),  # type: ignore[arg-type]
            evaluator.agent(seat1, 1),  # type: ignore[arg-type]
            seed=seed,
            transition_seed=seed,
            agent_seed=seed + 1000003,
            starting_player=int(starting_player),
            starting_life=int(starting_life),
            max_decisions=int(cap),
            mulligan_agents=(evaluator.mulligan(seat0, 0), evaluator.mulligan(seat1, 1)),  # type: ignore[arg-type]
            record_log=False,
            episode_id=f"{ladder_stage}:{focal.strategy_id}:{opponent.strategy_id}:{starting_life}:{rep}:{orientation}:{starting_player}:{cap}",
        )
        score = 0.5 if result.winner is None else (1.0 if result.winner == focal_player else 0.0)
        snapshot = longgame_snapshot(state, result, focal_player=focal_player)
        rows.append(
            {
                "stage": ladder_stage,
                "original_stage": original_stage,
                "focal_strategy": focal.strategy_id,
                "opponent_strategy": opponent.strategy_id,
                "strategy0": seat0.strategy_id,
                "strategy1": seat1.strategy_id,
                "starting_life": int(starting_life),
                "rep": int(rep),
                "orientation": int(orientation),
                "starting_player": int(starting_player),
                "seed": seed,
                "transition_seed": seed,
                "agent_seed": seed + 1000003,
                "max_decisions": int(cap),
                "score": score,
                "truncation": result.loss_reason == "max_decisions_reached",
                "interface": "public_decision_frame+information_state",
                **snapshot,
            }
        )
    return rows


def summarize_longgame_axis(
    estimate: PairEstimate,
    rows: Sequence[Mapping[str, object]],
    *,
    max_decisions: int,
    threshold: float = 0.5,
) -> LongGameAxisSummary:
    material = [dict(row) for row in rows]
    nonterminal = [row for row in material if str(row.get("loss_reason")) == "max_decisions_reached"]
    class_counts: dict[str, int] = {}
    diagnostics: list[float] = []
    for row in nonterminal:
        label = str(row.get("nonterminal_class", "unknown"))
        class_counts[label] = class_counts.get(label, 0) + 1
        diagnostics.append(float(row.get("diagnostic_focal_advantage", 0.0) or 0.0))
    return LongGameAxisSummary(
        focal_strategy=estimate.focal_strategy,
        opponent_strategy=estimate.opponent_strategy,
        games=int(estimate.games),
        mean_score=float(estimate.mean_score),
        ci_low=float(estimate.ci_low),
        ci_high=float(estimate.ci_high),
        truncations=int(estimate.truncations),
        max_decisions=int(max_decisions),
        max_turn_number=max((int(row.get("turn_number", 0) or 0) for row in material), default=0),
        mean_decisions=float(sum(float(row.get("decisions", 0) or 0) for row in material) / max(1, len(material))),
        nonterminal_diagnostic_min=min(diagnostics) if diagnostics else 0.0,
        nonterminal_diagnostic_max=max(diagnostics) if diagnostics else 0.0,
        nonterminal_class_counts=class_counts,
        confidence_floor_cleared=bool(float(estimate.ci_low) > float(threshold) and int(estimate.truncations) == 0),
        threshold=float(threshold),
    )


def cap_ladder_summary(rows: Iterable[Mapping[str, object]]) -> dict[str, object]:
    material = [dict(row) for row in rows]
    caps = sorted({int(row["max_decisions"]) for row in material})
    terminal_caps = [int(row["max_decisions"]) for row in material if str(row.get("loss_reason")) != "max_decisions_reached"]
    return {
        "schema": "muc5.longgame.cap_ladder_summary.v1",
        "rows": len(material),
        "caps": caps,
        "resolved": bool(terminal_caps),
        "first_terminal_cap": min(terminal_caps) if terminal_caps else None,
        "remaining_truncated_at_max_cap": bool(material and str(max(material, key=lambda row: int(row["max_decisions"])).get("loss_reason")) == "max_decisions_reached"),
        "class_counts": _count_by(material, "nonterminal_class"),
        "loss_reason_counts": _count_by(material, "loss_reason"),
    }


def _count_by(rows: Sequence[Mapping[str, object]], key: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for row in rows:
        value = str(row.get(key, ""))
        out[value] = out.get(value, 0) + 1
    return out
