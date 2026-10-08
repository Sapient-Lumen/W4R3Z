from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .counter_response import GUARDED_COUNTER_AXIS, LEGACY_COUNTER_AXIS
from .cpp_rollout import CppShadowGameSpec
from .deckspace import DeckVector
from .library_buffer_sweep import scale_deck_to_legal_size
from .payoff import StrategyBundle, load_seed_decks
from .population_frontier import population_gate_bool
from .statgate import hoeffding_interval
from .terminal_decomposition import CF34_AGENT, CF34_MULLIGAN, THREAT_MULLIGAN
from .terminal_mechanisms import to_float, to_int
from .threat_closure import THREAT_CLOSURE_AGENT
from .threat_response import CLOSURE_THREAT_AXIS, ThreatResponseArm

REPAIR_COUNTER_AXIS = "public_counter_life20_stabilizer"
REPAIR_COUNTER_AGENT = "counter_life20_stabilizer"


def _bundle(strategy_id: str, deck_name: str, deck: DeckVector, agent: str, mulligan: str) -> StrategyBundle:
    return StrategyBundle(strategy_id, deck_name, deck, agent, mulligan)


def deficient_cell_counterprobe_arms(seed_decks_path) -> list[ThreatResponseArm]:
    """Build a narrow counter-policy probe for the rev0082 deficient fine cell.

    The probe is intentionally not a new broad population.  It targets only the
    upper-bound-deficient rev0082 context: counter40 vs threat40 at life 20
    against the library-aware closure threat.  Legacy and existing guard rows
    are rerun on the same paired seed grid as the new repair candidate so the
    first question is whether the candidate expands the counter set at all.
    """

    decks = load_seed_decks(seed_decks_path)
    counter60 = decks["sixty_counterwall_jace"]
    counter40 = scale_deck_to_legal_size(counter60, 40)
    threat40 = decks["forty_overlord_impending"]

    counters: tuple[tuple[str, str, str, str], ...] = (
        (LEGACY_COUNTER_AXIS, "legacy_counter_wall40", CF34_AGENT, "Historical CF34 counter ranker control."),
        (GUARDED_COUNTER_AXIS, "guard_counter_wall40", "counter_guard", "Existing public counter_guard control."),
        (REPAIR_COUNTER_AXIS, "life20_stabilizer_counter_wall40", REPAIR_COUNTER_AGENT, "New public stabilizer probe: keep mana up, counter Overlord/Jace, and treat life-20 face pressure as critical."),
    )
    threat = _bundle("pub_threat40_closure", "forty_overlord_impending", threat40, THREAT_CLOSURE_AGENT, THREAT_MULLIGAN)
    arms: list[ThreatResponseArm] = []
    for axis, strategy_id, agent, note in counters:
        target = _bundle(strategy_id, "forty_counterwall_scaled_from60", counter40, agent, CF34_MULLIGAN)
        arms.append(
            ThreatResponseArm(
                arm_id=f"D_{axis}_counter40_vs_threat40_life20_closure_probe",
                question="Targeted rev0082 upper-bound-deficient fine cell: counter40 vs threat40, life 20, closure threat.",
                target=target,
                opponent=threat,
                counter_policy_axis=axis,
                threat_policy_axis=CLOSURE_THREAT_AXIS,
                size_axis="counter40_vs_threat40",
                interpretation=note,
            )
        )
    return arms


def paired_deficient_cell_specs(
    arms: Sequence[ThreatResponseArm],
    *,
    simulator_revision: str,
    reps: int = 16,
    base_seed: int = 8383000,
    max_decisions: int = 900,
) -> tuple[tuple[CppShadowGameSpec, ...], dict[str, dict[str, Any]]]:
    """Create same-seed specs across counter policies for the deficient cell.

    ``threat_response_specs`` increments the seed across arms.  That is fine for
    population sampling, but a counter-set repair probe is more interpretable if
    legacy, current guard, and repair candidates face the same target-seat /
    starting-player / repetition seed grid.  The target deck is identical across
    the public guard and repair candidates, so seed-pairing reduces noise without
    using hidden information.
    """

    specs: list[CppShadowGameSpec] = []
    meta: dict[str, dict[str, Any]] = {}
    k = 0
    for arm in arms:
        for target_seat in (0, 1):
            left, right = (arm.target, arm.opponent) if target_seat == 0 else (arm.opponent, arm.target)
            for starting_player in (0, 1):
                for rep in range(int(reps)):
                    paired_seed = int(base_seed + target_seat * 10000 + starting_player * 1000 + rep)
                    gid = f"p{k:05d}_{arm.counter_policy_axis}_seat{target_seat}_sp{starting_player}_r{rep}"
                    specs.append(
                        CppShadowGameSpec(
                            game_id=gid,
                            strategy0=left.strategy_id,
                            strategy1=right.strategy_id,
                            deck0_name=left.deck_name,
                            deck1_name=right.deck_name,
                            deck0=left.deck,
                            deck1=right.deck,
                            agent0=left.agent_name,
                            agent1=right.agent_name,
                            mulligan0=str(left.mulligan_policy),
                            mulligan1=str(right.mulligan_policy),
                            seed=paired_seed,
                            starting_player=int(starting_player),
                            starting_life=20,
                            max_decisions=int(max_decisions),
                            simulator_revision=simulator_revision,
                        )
                    )
                    meta[gid] = {
                        "arm_id": arm.arm_id,
                        "question": arm.question,
                        "interpretation": arm.interpretation,
                        "target": arm.target.strategy_id,
                        "opponent": arm.opponent.strategy_id,
                        "target_deck": arm.target.deck_name,
                        "opponent_deck": arm.opponent.deck_name,
                        "target_agent": arm.target.agent_name,
                        "opponent_agent": arm.opponent.agent_name,
                        "target_mulligan": str(arm.target.mulligan_policy),
                        "opponent_mulligan": str(arm.opponent.mulligan_policy),
                        "target_deck_size": arm.target.deck.size,
                        "opponent_deck_size": arm.opponent.deck.size,
                        "target_island_count": arm.target.deck.island,
                        "target_counterspell_count": arm.target.deck.counterspell,
                        "target_force_count": arm.target.deck.force,
                        "target_jace_count": arm.target.deck.jace,
                        "target_overlord_count": arm.target.deck.overlord,
                        "opponent_island_count": arm.opponent.deck.island,
                        "opponent_counterspell_count": arm.opponent.deck.counterspell,
                        "opponent_force_count": arm.opponent.deck.force,
                        "opponent_jace_count": arm.opponent.deck.jace,
                        "opponent_overlord_count": arm.opponent.deck.overlord,
                        "target_seat": int(target_seat),
                        "threat_seat": int(1 - target_seat),
                        "rep": int(rep),
                        "counter_policy_axis": arm.counter_policy_axis,
                        "threat_policy_axis": arm.threat_policy_axis,
                        "size_axis": arm.size_axis,
                        "sampling_design": "targeted_counterprobe_same_seed_grid",
                    }
                    k += 1
    return tuple(specs), meta


def counterprobe_policy_delta_rows(summary_rows: Sequence[Mapping[str, object]], *, baseline_axis: str = GUARDED_COUNTER_AXIS, candidate_axis: str = REPAIR_COUNTER_AXIS) -> list[dict[str, object]]:
    """Compare target-score means and conservative bounds between probe policies."""

    by_axis = {str(row.get("counter_policy_axis", "")): dict(row) for row in summary_rows}
    baseline = by_axis.get(baseline_axis, {})
    axes = sorted(by_axis)
    baseline_games = to_int(baseline.get("games"), 0) if baseline else 0
    baseline_mean = to_float(baseline.get("target_mean_score_draw_half"), float("nan")) if baseline else float("nan")
    baseline_ci = hoeffding_interval(baseline_mean, baseline_games, alpha=0.05 / max(1, len(axes))) if baseline_games > 0 else None
    baseline_ucb = float("nan") if baseline_ci is None else baseline_ci.high
    candidate = by_axis.get(candidate_axis, {})
    out: list[dict[str, object]] = []
    for axis in axes:
        row = by_axis[axis]
        games = to_int(row.get("games"), 0)
        mean = to_float(row.get("target_mean_score_draw_half"), float("nan"))
        ci = hoeffding_interval(mean, games, alpha=0.05 / max(1, len(axes))) if games > 0 else None
        out.append(
            {
                "counter_policy_axis": axis,
                "games": games,
                "target_mean_score_draw_half": mean,
                "target_score_lcb_familywise_probe": "" if ci is None else ci.low,
                "target_score_ucb_familywise_probe": "" if ci is None else ci.high,
                "terminal_wins": to_int(row.get("target_terminal_wins"), 0),
                "terminal_losses": to_int(row.get("target_terminal_losses"), 0),
                "library_out_wins": to_int(row.get("target_library_out_wins"), 0),
                "life_total_wins": to_int(row.get("target_life_total_wins"), 0),
                "target_library_out_losses": to_int(row.get("target_library_out_losses"), 0),
                "baseline_axis": baseline_axis,
                "candidate_axis": candidate_axis,
                "mean_delta_vs_baseline": mean - to_float(baseline.get("target_mean_score_draw_half"), float("nan")) if baseline else "",
                "ucb_delta_vs_baseline": "" if ci is None or baseline_ci is None else ci.high - baseline_ucb,
                "is_candidate": axis == candidate_axis,
                "is_baseline": axis == baseline_axis,
            }
        )
    return out


def summarize_counterprobe_rescue(rows: Sequence[Mapping[str, object]], *, threshold: float = 0.50, candidate_axis: str = REPAIR_COUNTER_AXIS) -> dict[str, object]:
    finite = [row for row in rows if to_int(row.get("games"), 0) > 0]
    best_mean = max(finite, key=lambda row: to_float(row.get("target_mean_score_draw_half"), float("nan"))) if finite else {}
    best_ucb = max(finite, key=lambda row: to_float(row.get("target_score_ucb_familywise_probe"), float("nan"))) if finite else {}
    candidate = next((row for row in finite if row.get("counter_policy_axis") == candidate_axis), {})
    candidate_mean = to_float(candidate.get("target_mean_score_draw_half"), float("nan")) if candidate else float("nan")
    candidate_lcb = to_float(candidate.get("target_score_lcb_familywise_probe"), float("nan")) if candidate else float("nan")
    candidate_ucb = to_float(candidate.get("target_score_ucb_familywise_probe"), float("nan")) if candidate else float("nan")
    best_ucb_value = to_float(best_ucb.get("target_score_ucb_familywise_probe"), float("nan")) if best_ucb else float("nan")
    if candidate and candidate_lcb >= float(threshold):
        status = "candidate_counter_repair_certified_for_targeted_cell"
    elif best_ucb and best_ucb_value < float(threshold):
        status = "targeted_probe_still_counter_set_deficient_even_by_upper_bound"
    elif candidate and candidate_mean >= float(threshold):
        status = "candidate_counter_repair_certification_limited"
    elif candidate and candidate_ucb >= float(threshold):
        status = "candidate_counter_repair_possible_but_mean_below_threshold"
    else:
        status = "targeted_probe_incomplete_or_uninterpretable"
    return {
        "rows": len(rows),
        "threshold": float(threshold),
        "candidate_axis": candidate_axis,
        "candidate_mean": candidate_mean if candidate else None,
        "candidate_lcb": candidate_lcb if candidate else None,
        "candidate_ucb": candidate_ucb if candidate else None,
        "candidate_games": to_int(candidate.get("games"), 0) if candidate else 0,
        "best_mean_axis": best_mean.get("counter_policy_axis", "") if best_mean else "",
        "best_mean": to_float(best_mean.get("target_mean_score_draw_half"), float("nan")) if best_mean else None,
        "best_ucb_axis": best_ucb.get("counter_policy_axis", "") if best_ucb else "",
        "best_ucb": best_ucb_value if best_ucb else None,
        "status": status,
        "candidate_certified": status == "candidate_counter_repair_certified_for_targeted_cell",
        "counter_set_deficient_even_by_upper_bound": status == "targeted_probe_still_counter_set_deficient_even_by_upper_bound",
        "candidate_gate_passed_bool": population_gate_bool(status == "candidate_counter_repair_certified_for_targeted_cell"),
    }


__all__ = [
    "REPAIR_COUNTER_AGENT",
    "REPAIR_COUNTER_AXIS",
    "counterprobe_policy_delta_rows",
    "deficient_cell_counterprobe_arms",
    "paired_deficient_cell_specs",
    "summarize_counterprobe_rescue",
]
