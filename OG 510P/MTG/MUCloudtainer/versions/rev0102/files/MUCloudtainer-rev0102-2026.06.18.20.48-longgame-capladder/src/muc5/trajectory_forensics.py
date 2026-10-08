from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from random import Random
from statistics import mean, median
from typing import Any, Iterable, Mapping, Sequence

from .action_schema import Action
from .cpp_rollout import CppShadowGameSpec
from .decision import apply_decision_index, build_decision_frame
from .engine import GameState, start_game
from .mulligan_ranker import make_mulligan_agent
from .public_agents import make_public_agent
from .terminal_mechanisms import annotate_target_mechanism, terminal_mechanism, to_float, to_int


@dataclass(frozen=True)
class PlayerTrajectoryStats:
    player: int
    start_library: int
    final_library: int
    min_library: int
    max_library_drawdown: int
    start_life: int
    final_life: int
    min_life: int
    max_jace_loyalty: int
    final_jace_loyalty: int | None
    max_overlord_creatures: int
    final_overlord_creatures: int
    pass_actions: int
    play_island_actions: int
    cast_jace: int
    cast_overlord_impending: int
    cast_overlord_full_cost: int
    cast_counterspell: int
    cast_force_pitch: int
    cast_force_mana: int
    activate_jace_plus2_self: int
    activate_jace_plus2_opponent: int
    activate_jace_zero: int
    activate_jace_minus1: int
    activate_jace_ultimate_self: int
    activate_jace_ultimate_opponent: int
    attack_actions: int
    attack_to_player_total: int
    attack_to_jace_total: int
    block_actions: int
    block_player_attackers_total: int
    block_jace_attackers_total: int
    discard_choices: int
    cleanup_discard_choices: int
    jace_plus2_leave_choices: int
    jace_plus2_bottom_choices: int
    jace_brainstorm_putback_choices: int
    jace_legend_choices: int
    nonpass_actions: int

    def as_dict(self, prefix: str) -> dict[str, object]:
        base = asdict(self)
        return {f"{prefix}_{k}": v for k, v in base.items() if k != "player"}


def _overlord_creatures(state: GameState, player: int) -> int:
    p = state.players[player]
    return int(p.overlord_ready + p.overlord_sick + p.overlord_tapped)


def _jace_loyalty_as_floor(value: int | None) -> int:
    return int(value) if value is not None else 0


def _init_player_counters() -> dict[str, int]:
    return {
        "pass_actions": 0,
        "play_island_actions": 0,
        "cast_jace": 0,
        "cast_overlord_impending": 0,
        "cast_overlord_full_cost": 0,
        "cast_counterspell": 0,
        "cast_force_pitch": 0,
        "cast_force_mana": 0,
        "activate_jace_plus2_self": 0,
        "activate_jace_plus2_opponent": 0,
        "activate_jace_zero": 0,
        "activate_jace_minus1": 0,
        "activate_jace_ultimate_self": 0,
        "activate_jace_ultimate_opponent": 0,
        "attack_actions": 0,
        "attack_to_player_total": 0,
        "attack_to_jace_total": 0,
        "block_actions": 0,
        "block_player_attackers_total": 0,
        "block_jace_attackers_total": 0,
        "discard_choices": 0,
        "cleanup_discard_choices": 0,
        "jace_plus2_leave_choices": 0,
        "jace_plus2_bottom_choices": 0,
        "jace_brainstorm_putback_choices": 0,
        "jace_legend_choices": 0,
        "nonpass_actions": 0,
    }


def update_action_counters(counters: dict[str, int], action: Action) -> None:
    """Update a flat player-action feature map from one MUC-5 macro-action.

    The names are intentionally stable report fields rather than card-engine internals.
    They let later scripts ask whether a terminal edge was driven by draw/Jace,
    countering, Overlord pressure, or plain pass/endurance behavior.
    """

    kind = action.kind
    params = action.params
    if kind == "PASS":
        counters["pass_actions"] += 1
        return
    counters["nonpass_actions"] += 1
    if kind == "PLAY_ISLAND":
        counters["play_island_actions"] += 1
    elif kind == "CAST":
        card = str(params.get("card", ""))
        if card == "JaceTheMindSculptor":
            counters["cast_jace"] += 1
        elif card == "OverlordOfTheFloodpits":
            mode = str(params.get("mode", "full_cost"))
            if mode == "impending":
                counters["cast_overlord_impending"] += 1
            else:
                counters["cast_overlord_full_cost"] += 1
        elif card == "Counterspell":
            counters["cast_counterspell"] += 1
        elif card == "ForceOfWill":
            payment = str(params.get("payment", ""))
            if payment == "pitch":
                counters["cast_force_pitch"] += 1
            else:
                counters["cast_force_mana"] += 1
    elif kind == "ACTIVATE_JACE":
        mode = str(params.get("mode", ""))
        target = str(params.get("target_player", ""))
        if mode == "plus2":
            if target == "self":
                counters["activate_jace_plus2_self"] += 1
            else:
                counters["activate_jace_plus2_opponent"] += 1
        elif mode == "zero":
            counters["activate_jace_zero"] += 1
        elif mode == "minus1":
            counters["activate_jace_minus1"] += 1
        elif mode == "ultimate":
            if target == "self":
                counters["activate_jace_ultimate_self"] += 1
            else:
                counters["activate_jace_ultimate_opponent"] += 1
    elif kind == "ATTACK":
        counters["attack_actions"] += 1
        counters["attack_to_player_total"] += to_int(params.get("to_player"), 0)
        counters["attack_to_jace_total"] += to_int(params.get("to_jace"), 0)
    elif kind == "BLOCK":
        counters["block_actions"] += 1
        counters["block_player_attackers_total"] += to_int(params.get("block_player_attackers"), 0)
        counters["block_jace_attackers_total"] += to_int(params.get("block_jace_attackers"), 0)
    elif kind == "CHOOSE_FOR_EFFECT":
        effect = str(params.get("effect", ""))
        if effect == "discard":
            counters["discard_choices"] += 1
        elif effect == "cleanup_discard":
            counters["cleanup_discard_choices"] += 1
        elif effect == "jace_plus2":
            if str(params.get("put", "")) == "bottom":
                counters["jace_plus2_bottom_choices"] += 1
            else:
                counters["jace_plus2_leave_choices"] += 1
        elif effect == "jace_brainstorm_putback":
            counters["jace_brainstorm_putback_choices"] += 1
        elif effect == "jace_legend":
            counters["jace_legend_choices"] += 1


def _player_stats_from_state_path(
    *,
    player: int,
    start_libraries: Sequence[int],
    start_lives: Sequence[int],
    min_libraries: Sequence[int],
    min_lives: Sequence[int],
    max_jace: Sequence[int],
    max_overlords: Sequence[int],
    final_state: GameState,
    counters: Mapping[str, int],
) -> PlayerTrajectoryStats:
    p = final_state.players[player]
    start_library = int(start_libraries[player])
    final_library = int(len(p.library))
    min_library = int(min_libraries[player])
    return PlayerTrajectoryStats(
        player=int(player),
        start_library=start_library,
        final_library=final_library,
        min_library=min_library,
        max_library_drawdown=int(start_library - min_library),
        start_life=int(start_lives[player]),
        final_life=int(p.life),
        min_life=int(min_lives[player]),
        max_jace_loyalty=int(max_jace[player]),
        final_jace_loyalty=None if p.jace_loyalty is None else int(p.jace_loyalty),
        max_overlord_creatures=int(max_overlords[player]),
        final_overlord_creatures=_overlord_creatures(final_state, player),
        **{k: int(counters.get(k, 0)) for k in _init_player_counters()},
    )


def trajectory_forensics_from_spec(spec: CppShadowGameSpec, *, target_seat: int | None = None) -> dict[str, object]:
    """Re-run one public-agent game and emit compact transition-level diagnostics.

    This deliberately mirrors ``prepare_cpp_shadow_rollout`` seeds and agents, but
    returns aggregate explanatory features instead of a full transition CSV.  It is
    a safer default for claim forensics because the linked cube gets substance
    without tens or hundreds of MiB of raw rows.
    """

    transition_rng = Random(int(spec.seed))
    agent_rng = Random(int(spec.seed) + 1000003)
    state = start_game(
        spec.deck0,
        spec.deck1,
        seed=int(spec.seed),
        starting_player=int(spec.starting_player),
        starting_life=int(spec.starting_life),
        mulligan_agents=(make_mulligan_agent(spec.mulligan0), make_mulligan_agent(spec.mulligan1)),
        record_log=False,
    )
    agents = [make_public_agent(spec.agent0), make_public_agent(spec.agent1)]
    counters = [_init_player_counters(), _init_player_counters()]
    start_libraries = [len(state.players[0].library), len(state.players[1].library)]
    start_lives = [state.players[0].life, state.players[1].life]
    min_libraries = list(start_libraries)
    min_lives = list(start_lives)
    max_jace = [_jace_loyalty_as_floor(state.players[0].jace_loyalty), _jace_loyalty_as_floor(state.players[1].jace_loyalty)]
    max_overlords = [_overlord_creatures(state, 0), _overlord_creatures(state, 1)]
    first_jace_step = [0, 0]
    first_overlord_creature_step = [0, 0]
    first_library_below_10_step = [0, 0]
    decision_players: Counter[int] = Counter()
    action_kinds: Counter[str] = Counter()
    decision_count = 0

    for step in range(1, int(spec.max_decisions) + 1):
        if state.winner is not None:
            break
        frame = build_decision_frame(state)
        if frame.action_count <= 0:
            break
        action_index = agents[frame.player].choose_action_index(frame, agent_rng)  # type: ignore[attr-defined]
        if action_index < 0 or action_index >= frame.action_count:
            raise ValueError(f"{spec.game_id}: illegal action index {action_index}/{frame.action_count}")
        action = frame.legal_actions[action_index]
        decision_players[int(frame.player)] += 1
        action_kinds[str(action.kind)] += 1
        update_action_counters(counters[int(frame.player)], action)
        apply_decision_index(state, frame, action_index, transition_rng)
        decision_count = int(step)
        for pidx in (0, 1):
            player = state.players[pidx]
            min_libraries[pidx] = min(min_libraries[pidx], len(player.library))
            min_lives[pidx] = min(min_lives[pidx], int(player.life))
            max_jace[pidx] = max(max_jace[pidx], _jace_loyalty_as_floor(player.jace_loyalty))
            max_overlords[pidx] = max(max_overlords[pidx], _overlord_creatures(state, pidx))
            if first_jace_step[pidx] == 0 and player.jace_loyalty is not None:
                first_jace_step[pidx] = int(step)
            if first_overlord_creature_step[pidx] == 0 and _overlord_creatures(state, pidx) > 0:
                first_overlord_creature_step[pidx] = int(step)
            if first_library_below_10_step[pidx] == 0 and len(player.library) < 10:
                first_library_below_10_step[pidx] = int(step)

    truncated = state.winner is None and decision_count >= int(spec.max_decisions)
    if truncated:
        state.frame = "GAME_OVER"
        state.loss_reason = "max_decisions_reached"
    pstats = [
        _player_stats_from_state_path(
            player=0,
            start_libraries=start_libraries,
            start_lives=start_lives,
            min_libraries=min_libraries,
            min_lives=min_lives,
            max_jace=max_jace,
            max_overlords=max_overlords,
            final_state=state,
            counters=counters[0],
        ),
        _player_stats_from_state_path(
            player=1,
            start_libraries=start_libraries,
            start_lives=start_lives,
            min_libraries=min_libraries,
            min_lives=min_lives,
            max_jace=max_jace,
            max_overlords=max_overlords,
            final_state=state,
            counters=counters[1],
        ),
    ]
    p0_score = 0.5 if state.winner is None else (1.0 if state.winner == 0 else 0.0)
    p1_score = 0.5 if state.winner is None else (1.0 if state.winner == 1 else 0.0)
    legacy_terminal_row_decisions = int(decision_count + (1 if state.winner is not None else 0))
    row: dict[str, object] = {
        "cpp_shadow_game_id": spec.game_id,
        "strategy0": spec.strategy0,
        "strategy1": spec.strategy1,
        "deck0": spec.deck0_name,
        "deck1": spec.deck1_name,
        "agent0": spec.agent0,
        "agent1": spec.agent1,
        "mulligan0": spec.mulligan0,
        "mulligan1": spec.mulligan1,
        "starting_life": int(spec.starting_life),
        "starting_player": int(spec.starting_player),
        "seed": int(spec.seed),
        "winner": "None" if state.winner is None else str(state.winner),
        "p0_score": p0_score,
        "p1_score": p1_score,
        "loss_reason": state.loss_reason,
        "terminal_mechanism": terminal_mechanism(state.loss_reason),
        "is_truncation": bool(truncated),
        "decisions": int(decision_count),
        "applied_decisions": int(decision_count),
        "legacy_terminal_row_decisions": legacy_terminal_row_decisions,
        "turn_number": int(state.turn_number),
        "p0_decision_count": int(decision_players[0]),
        "p1_decision_count": int(decision_players[1]),
        "action_kind_counts": dict(sorted(action_kinds.items())),
        "p0_first_jace_step": int(first_jace_step[0]),
        "p1_first_jace_step": int(first_jace_step[1]),
        "p0_first_overlord_creature_step": int(first_overlord_creature_step[0]),
        "p1_first_overlord_creature_step": int(first_overlord_creature_step[1]),
        "p0_first_library_below_10_step": int(first_library_below_10_step[0]),
        "p1_first_library_below_10_step": int(first_library_below_10_step[1]),
    }
    row.update(pstats[0].as_dict("p0"))
    row.update(pstats[1].as_dict("p1"))
    if target_seat is not None:
        seat = int(target_seat)
        opp = 1 - seat
        row["focus_target_seat"] = seat
        row["focus_target_score"] = p0_score if seat == 0 else p1_score
        row.update(annotate_target_mechanism(row))
        for field in (
            "start_library",
            "final_library",
            "min_library",
            "max_library_drawdown",
            "start_life",
            "final_life",
            "min_life",
            "max_jace_loyalty",
            "max_overlord_creatures",
            "pass_actions",
            "nonpass_actions",
            "cast_jace",
            "cast_overlord_impending",
            "cast_overlord_full_cost",
            "cast_counterspell",
            "cast_force_pitch",
            "cast_force_mana",
            "activate_jace_plus2_self",
            "activate_jace_plus2_opponent",
            "activate_jace_zero",
            "activate_jace_minus1",
            "activate_jace_ultimate_opponent",
            "attack_actions",
            "attack_to_player_total",
            "attack_to_jace_total",
            "discard_choices",
            "jace_brainstorm_putback_choices",
        ):
            row[f"target_{field}"] = row.get(f"p{seat}_{field}", 0)
            row[f"opponent_{field}"] = row.get(f"p{opp}_{field}", 0)
        row["target_library_buffer_final"] = to_int(row.get("target_final_library"), 0) - to_int(row.get("opponent_final_library"), 0)
        row["target_library_buffer_start"] = to_int(row.get("target_start_library"), 0) - to_int(row.get("opponent_start_library"), 0)
        row["opponent_minus_target_library_drawdown"] = to_int(row.get("opponent_max_library_drawdown"), 0) - to_int(row.get("target_max_library_drawdown"), 0)
        row["target_minus_opponent_jace_zero"] = to_int(row.get("target_activate_jace_zero"), 0) - to_int(row.get("opponent_activate_jace_zero"), 0)
        row["target_minus_opponent_overlord_pressure"] = to_int(row.get("target_attack_to_player_total"), 0) - to_int(row.get("opponent_attack_to_player_total"), 0)
    return row


def validate_forensics_against_game_row(forensic_row: Mapping[str, Any], expected_row: Mapping[str, Any]) -> list[str]:
    """Return replay/forensic mismatches against a stored terminal game row."""

    errors: list[str] = []
    checks = (
        ("winner", str),
        ("loss_reason", str),
        ("starting_life", int),
        ("starting_player", int),
    )
    for key, coerce in checks:
        try:
            got = coerce(forensic_row.get(key))
            want = coerce(expected_row.get(key))
        except Exception:
            got = forensic_row.get(key)
            want = expected_row.get(key)
        if got != want:
            errors.append(f"{key}: got {got!r} expected {want!r}")
    for key in ("p0_score", "p1_score"):
        if abs(to_float(forensic_row.get(key), -9.0) - to_float(expected_row.get(key), -8.0)) > 1e-12:
            errors.append(f"{key}: got {forensic_row.get(key)!r} expected {expected_row.get(key)!r}")
    # Historical terminal game rows before rev0060 overcounted terminal decisions by one,
    # while live rev0060+ rollout rows report corrected applied decisions.  Accept both
    # contracts so one forensic validator can safely compare against old evidence and
    # fresh runs without forcing scripts to know which artifact era they are reading.
    applied = to_int(forensic_row.get("applied_decisions", forensic_row.get("decisions")), -3)
    legacy = to_int(forensic_row.get("legacy_terminal_row_decisions"), -1)
    expected_decisions = to_int(expected_row.get("decisions"), -2)
    if expected_decisions not in {applied, legacy}:
        errors.append(
            "decisions: got applied "
            f"{applied!r} / legacy {legacy!r} expected {expected_decisions!r}"
        )
    return errors


def summarize_forensic_rows(rows: Sequence[Mapping[str, Any]], *, group_keys: Sequence[str]) -> list[dict[str, object]]:
    """Aggregate compact forensics by arbitrary groups."""

    buckets: dict[tuple[object, ...], list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        buckets[tuple(row.get(k, "") for k in group_keys)].append(row)
    numeric_fields = (
        "focus_target_score",
        "decisions",
        "turn_number",
        "target_final_library",
        "opponent_final_library",
        "target_library_buffer_final",
        "target_max_library_drawdown",
        "opponent_max_library_drawdown",
        "opponent_minus_target_library_drawdown",
        "target_min_life",
        "opponent_min_life",
        "target_cast_jace",
        "opponent_cast_jace",
        "target_activate_jace_zero",
        "opponent_activate_jace_zero",
        "target_activate_jace_plus2_opponent",
        "opponent_activate_jace_plus2_opponent",
        "target_cast_counterspell",
        "opponent_cast_counterspell",
        "target_cast_force_pitch",
        "opponent_cast_force_pitch",
        "target_cast_force_mana",
        "opponent_cast_force_mana",
        "target_cast_overlord_impending",
        "opponent_cast_overlord_impending",
        "target_cast_overlord_full_cost",
        "opponent_cast_overlord_full_cost",
        "target_attack_to_player_total",
        "opponent_attack_to_player_total",
        "target_discard_choices",
        "opponent_discard_choices",
        "target_jace_brainstorm_putback_choices",
        "opponent_jace_brainstorm_putback_choices",
    )
    out: list[dict[str, object]] = []
    for group, group_rows in sorted(buckets.items()):
        row = {k: v for k, v in zip(group_keys, group)}
        n = len(group_rows)
        row["games"] = int(n)
        for field in numeric_fields:
            values = [to_float(r.get(field), 0.0) for r in group_rows]
            row[f"mean_{field}"] = mean(values) if values else 0.0
            if field in {"decisions", "turn_number", "target_library_buffer_final", "opponent_minus_target_library_drawdown"}:
                row[f"median_{field}"] = median(values) if values else 0.0
        row["target_wins"] = int(sum(1 for r in group_rows if to_float(r.get("focus_target_score"), 0.5) > 0.5))
        row["library_out_wins"] = int(sum(1 for r in group_rows if str(r.get("focus_terminal_mechanism")) == "library_out" and str(r.get("focus_terminal_loser_role")) == "opponent"))
        row["target_self_deck_losses"] = int(sum(1 for r in group_rows if str(r.get("focus_terminal_mechanism")) == "library_out" and str(r.get("focus_terminal_loser_role")) == "target"))
        row["life_total_wins"] = int(sum(1 for r in group_rows if str(r.get("focus_terminal_mechanism")) == "life_total" and str(r.get("focus_terminal_loser_role")) == "opponent"))
        out.append(row)
    return out


def metric_deltas_by_arm(
    summary_rows: Sequence[Mapping[str, Any]],
    *,
    left_arm: str = "A_original_size_skew",
    right_arm: str = "B_pilot_swap_size_skew",
) -> list[dict[str, object]]:
    """Compute left-minus-right deltas for matching summary rows.

    The expected input is usually the output of ``summarize_forensic_rows`` grouped
    by at least ``arm_id``.  This helper keeps the comparison table small and
    directly reportable in claim cards.
    """

    by_arm = {str(r.get("arm_id")): r for r in summary_rows}
    left = by_arm.get(left_arm)
    right = by_arm.get(right_arm)
    if not left or not right:
        return []
    interesting = [
        "mean_focus_target_score",
        "mean_target_library_buffer_final",
        "mean_opponent_minus_target_library_drawdown",
        "mean_target_activate_jace_zero",
        "mean_opponent_activate_jace_zero",
        "mean_target_attack_to_player_total",
        "mean_opponent_attack_to_player_total",
        "mean_target_cast_counterspell",
        "mean_opponent_cast_counterspell",
        "mean_target_cast_force_pitch",
        "mean_opponent_cast_force_pitch",
        "mean_target_discard_choices",
        "mean_opponent_discard_choices",
    ]
    out: list[dict[str, object]] = []
    for field in interesting:
        out.append(
            {
                "metric": field,
                left_arm: to_float(left.get(field), 0.0),
                right_arm: to_float(right.get(field), 0.0),
                "left_minus_right": to_float(left.get(field), 0.0) - to_float(right.get(field), 0.0),
            }
        )
    return out
