from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .counter_response import COUNTER_GUARD_AGENT, GUARDED_COUNTER_AXIS
from .cpp_rollout import CppShadowGameSpec
from .deckspace import DeckVector
from .library_buffer_sweep import scale_deck_to_legal_size
from .payoff import StrategyBundle, load_seed_decks
from .population_counterprobe import REPAIR_COUNTER_AGENT, REPAIR_COUNTER_AXIS
from .population_frontier import THREAT_POPULATION
from .terminal_decomposition import CF34_MULLIGAN, THREAT_MULLIGAN
from .terminal_mechanisms import to_float, to_int
from .threat_response import CLOSURE_THREAT_AXIS, PRESSURE_THREAT_AXIS, ThreatResponseArm
from .response_matrix import SURGE_THREAT_AXIS


COUNTER_CANDIDATE_POPULATION: tuple[tuple[str, str, str], ...] = (
    (
        GUARDED_COUNTER_AXIS,
        COUNTER_GUARD_AGENT,
        "Existing public counter_guard baseline; this remains the only broad-pool candidate unless a challenger proves transfer-safe.",
    ),
    (
        REPAIR_COUNTER_AXIS,
        REPAIR_COUNTER_AGENT,
        "Adaptive low-life stabilizer from rev0083; must pass holdout/transfer before entering broad counter populations.",
    ),
)


@dataclass(frozen=True)
class CandidateTransferSummary:
    rows: int
    pairs: int
    candidate_better_pairs: int
    guard_better_pairs: int
    same_score_pairs: int
    candidate_mean_delta: float
    candidate_win_share: float
    candidate_nonnegative_share: float
    candidate_dominates_pairwise: bool
    candidate_negative_transfer_detected: bool
    status: str

    def as_dict(self) -> dict[str, object]:
        return {
            "rows": self.rows,
            "pairs": self.pairs,
            "candidate_better_pairs": self.candidate_better_pairs,
            "guard_better_pairs": self.guard_better_pairs,
            "same_score_pairs": self.same_score_pairs,
            "candidate_mean_delta": self.candidate_mean_delta,
            "candidate_win_share": self.candidate_win_share,
            "candidate_nonnegative_share": self.candidate_nonnegative_share,
            "candidate_dominates_pairwise": self.candidate_dominates_pairwise,
            "candidate_negative_transfer_detected": self.candidate_negative_transfer_detected,
            "status": self.status,
        }


def _bundle(strategy_id: str, deck_name: str, deck: DeckVector, agent: str, mulligan: str) -> StrategyBundle:
    return StrategyBundle(strategy_id, deck_name, deck, agent, mulligan)


def candidate_transfer_arms(seed_decks_path, *, threat_axes: Sequence[str] | None = None, size_axes: Sequence[str] | None = None) -> list[ThreatResponseArm]:
    """Build a seed-pairable guard-vs-stabilizer transfer panel.

    rev0083 deliberately invented ``public_counter_life20_stabilizer`` from an
    adaptive selected cell.  This arm generator does not add it to the official
    broad counter population.  It builds a separate transfer panel that can ask
    whether the candidate dominates the current guard under public-information
    policies, threat axes, sizes, and life totals before any later promotion.
    """

    decks = load_seed_decks(seed_decks_path)
    counter60 = decks["sixty_counterwall_jace"]
    threat40 = decks["forty_overlord_impending"]
    counter40 = scale_deck_to_legal_size(counter60, 40)
    threat60 = scale_deck_to_legal_size(threat40, 60)

    allowed_threat_axes = set(threat_axes or [axis for axis, _agent, _note in THREAT_POPULATION])
    allowed_size_axes = set(size_axes or ["counter40_vs_threat40", "counter60_vs_threat40", "counter60_vs_threat60"])

    def counter(size: int, counter_axis: str, agent: str) -> StrategyBundle:
        deck = counter60 if size == 60 else counter40
        deck_name = "sixty_counterwall_jace" if size == 60 else "forty_counterwall_scaled_from60"
        label = "guard" if counter_axis == GUARDED_COUNTER_AXIS else "life20_stabilizer"
        return _bundle(f"{label}_counter_wall{size}", deck_name, deck, agent, CF34_MULLIGAN)

    def threat(size: int, threat_axis: str, agent: str) -> StrategyBundle:
        deck = threat40 if size == 40 else threat60
        deck_name = "forty_overlord_impending" if size == 40 else "sixty_overlord_scaled_from40"
        label = {
            CLOSURE_THREAT_AXIS: "closure",
            PRESSURE_THREAT_AXIS: "pressure",
            SURGE_THREAT_AXIS: "surge",
        }[threat_axis]
        return _bundle(f"pub_threat{size}_{label}", deck_name, deck, agent, THREAT_MULLIGAN)

    plan = (
        ("A", 40, 40, "40-vs-40 targeted-cell neighborhood and normalized transfer cell."),
        ("B", 60, 40, "60-vs-40 size-skew transfer cell."),
        ("C", 60, 60, "60-vs-60 normalized transfer cell."),
    )
    arms: list[ThreatResponseArm] = []
    for prefix, counter_size, threat_size, question in plan:
        size_axis = f"counter{counter_size}_vs_threat{threat_size}"
        if size_axis not in allowed_size_axes:
            continue
        for counter_axis, counter_agent, counter_note in COUNTER_CANDIDATE_POPULATION:
            counter_label = "guard" if counter_axis == GUARDED_COUNTER_AXIS else "stabilizer"
            for threat_axis, threat_agent, threat_note in THREAT_POPULATION:
                if threat_axis not in allowed_threat_axes:
                    continue
                threat_label = {
                    CLOSURE_THREAT_AXIS: "closure",
                    PRESSURE_THREAT_AXIS: "pressure",
                    SURGE_THREAT_AXIS: "surge",
                }[threat_axis]
                arms.append(
                    ThreatResponseArm(
                        arm_id=f"{prefix}_{counter_label}_vs_{threat_label}_counter{counter_size}_vs_threat{threat_size}",
                        question=question,
                        target=counter(counter_size, counter_axis, counter_agent),
                        opponent=threat(threat_size, threat_axis, threat_agent),
                        counter_policy_axis=counter_axis,
                        threat_policy_axis=threat_axis,
                        size_axis=size_axis,
                        interpretation=f"{counter_note} Opponent axis: {threat_note}",
                    )
                )
    return arms


def paired_candidate_transfer_specs(
    arms: Sequence[ThreatResponseArm],
    *,
    simulator_revision: str,
    life_totals: Sequence[int] = (20, 40),
    reps: int = 2,
    base_seed: int = 8484000,
    max_decisions: int = 900,
    design_label: str = "adaptive_candidate_transfer_seedpaired",
    game_prefix: str = "t",
) -> tuple[tuple[CppShadowGameSpec, ...], dict[str, dict[str, Any]]]:
    """Create seed-paired specs for guard-vs-candidate transfer checks.

    Pairing is by size/threat/life/target-seat/starting-player/rep.  The same
    seed is used for each counter policy in that scenario, which turns the audit
    from a noisy mean comparison into a direct public-policy transfer check.
    """

    arms_by_key: dict[tuple[str, str], list[ThreatResponseArm]] = {}
    for arm in arms:
        arms_by_key.setdefault((arm.size_axis, arm.threat_policy_axis), []).append(arm)

    specs: list[CppShadowGameSpec] = []
    meta: dict[str, dict[str, Any]] = {}
    scenario_index = 0
    spec_index = 0
    for (size_axis, threat_axis), group in sorted(arms_by_key.items()):
        group_sorted = sorted(group, key=lambda arm: str(arm.counter_policy_axis))
        policies = {arm.counter_policy_axis for arm in group_sorted}
        if {GUARDED_COUNTER_AXIS, REPAIR_COUNTER_AXIS} - policies:
            continue
        for life in life_totals:
            for target_seat in (0, 1):
                for starting_player in (0, 1):
                    for rep in range(int(reps)):
                        paired_seed = int(base_seed + scenario_index)
                        pair_key = f"{design_label}|{size_axis}|{threat_axis}|life{int(life)}|seat{target_seat}|sp{starting_player}|r{rep}"
                        for arm in group_sorted:
                            left, right = (arm.target, arm.opponent) if target_seat == 0 else (arm.opponent, arm.target)
                            gid = f"{game_prefix}{spec_index:05d}_{arm.counter_policy_axis}_life{life}_seat{target_seat}_sp{starting_player}_r{rep}"
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
                                    starting_life=int(life),
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
                                "pair_key": pair_key,
                                "paired_seed": paired_seed,
                                "sampling_design": design_label,
                                "broad_pool_eligible": False,
                                "candidate_pool_eligible": False,
                            }
                            spec_index += 1
                        scenario_index += 1
    return tuple(specs), meta


def paired_candidate_delta_rows(
    rows: Sequence[Mapping[str, object]],
    *,
    baseline_axis: str = GUARDED_COUNTER_AXIS,
    candidate_axis: str = REPAIR_COUNTER_AXIS,
) -> list[dict[str, object]]:
    by_pair: dict[str, dict[str, Mapping[str, object]]] = {}
    for row in rows:
        pair_key = str(row.get("pair_key", ""))
        axis = str(row.get("counter_policy_axis", ""))
        if not pair_key or not axis:
            continue
        by_pair.setdefault(pair_key, {})[axis] = row

    out: list[dict[str, object]] = []
    for pair_key, policies in sorted(by_pair.items()):
        baseline = policies.get(baseline_axis)
        candidate = policies.get(candidate_axis)
        if baseline is None or candidate is None:
            out.append({"pair_key": pair_key, "complete_pair": False, "present_policies": ";".join(sorted(policies))})
            continue
        baseline_score = to_float(baseline.get("focus_target_score"), float("nan"))
        candidate_score = to_float(candidate.get("focus_target_score"), float("nan"))
        if candidate_score > baseline_score:
            comparison = "candidate_better"
        elif baseline_score > candidate_score:
            comparison = "guard_better"
        else:
            comparison = "same_score"
        out.append(
            {
                "pair_key": pair_key,
                "complete_pair": True,
                "sampling_design": candidate.get("sampling_design", baseline.get("sampling_design", "")),
                "size_axis": candidate.get("size_axis", baseline.get("size_axis", "")),
                "starting_life": to_int(candidate.get("starting_life", baseline.get("starting_life", -1)), -1),
                "threat_policy_axis": candidate.get("threat_policy_axis", baseline.get("threat_policy_axis", "")),
                "target_seat": to_int(candidate.get("target_seat", baseline.get("target_seat", -1)), -1),
                "starting_player": to_int(candidate.get("starting_player", baseline.get("starting_player", -1)), -1),
                "rep": to_int(candidate.get("rep", baseline.get("rep", -1)), -1),
                "paired_seed": to_int(candidate.get("paired_seed", baseline.get("paired_seed", -1)), -1),
                "baseline_axis": baseline_axis,
                "candidate_axis": candidate_axis,
                "baseline_score": baseline_score,
                "candidate_score": candidate_score,
                "candidate_minus_baseline_score": candidate_score - baseline_score,
                "comparison": comparison,
                "baseline_mechanism": baseline.get("focus_terminal_mechanism", ""),
                "candidate_mechanism": candidate.get("focus_terminal_mechanism", ""),
                "baseline_loss_reason": baseline.get("loss_reason", ""),
                "candidate_loss_reason": candidate.get("loss_reason", ""),
            }
        )
    return out


def summarize_candidate_transfer_rows(rows: Sequence[Mapping[str, object]]) -> CandidateTransferSummary:
    complete = [row for row in rows if str(row.get("complete_pair", "")).lower() == "true" or row.get("complete_pair") is True]
    pairs = len(complete)
    candidate_better = sum(1 for row in complete if row.get("comparison") == "candidate_better")
    guard_better = sum(1 for row in complete if row.get("comparison") == "guard_better")
    same = sum(1 for row in complete if row.get("comparison") == "same_score")
    deltas = [to_float(row.get("candidate_minus_baseline_score"), 0.0) for row in complete]
    mean_delta = sum(deltas) / pairs if pairs else 0.0
    win_share = candidate_better / pairs if pairs else 0.0
    nonnegative_share = (candidate_better + same) / pairs if pairs else 0.0
    dominates = pairs > 0 and guard_better == 0 and candidate_better > 0 and mean_delta >= 0.0
    negative_transfer = guard_better > candidate_better or mean_delta < 0.0
    if dominates:
        status = "candidate_transfer_dominates_guard_pairwise"
    elif negative_transfer:
        status = "candidate_quarantined_negative_transfer"
    elif candidate_better == 0 and guard_better == 0:
        status = "candidate_indistinguishable_from_guard_on_pairs"
    else:
        status = "candidate_quarantined_mixed_transfer"
    return CandidateTransferSummary(
        rows=len(rows),
        pairs=pairs,
        candidate_better_pairs=candidate_better,
        guard_better_pairs=guard_better,
        same_score_pairs=same,
        candidate_mean_delta=mean_delta,
        candidate_win_share=win_share,
        candidate_nonnegative_share=nonnegative_share,
        candidate_dominates_pairwise=dominates,
        candidate_negative_transfer_detected=negative_transfer,
        status=status,
    )


def transfer_context_summary_rows(rows: Sequence[Mapping[str, object]], *, context_axes: Sequence[str] = ("sampling_design", "size_axis", "starting_life", "threat_policy_axis")) -> list[dict[str, object]]:
    groups: dict[tuple[object, ...], list[Mapping[str, object]]] = {}
    for row in rows:
        if str(row.get("complete_pair", "")).lower() != "true" and row.get("complete_pair") is not True:
            continue
        key = tuple(row.get(axis, "") for axis in context_axes)
        groups.setdefault(key, []).append(row)
    out: list[dict[str, object]] = []
    for key, group in sorted(groups.items(), key=lambda item: tuple(str(x) for x in item[0])):
        summary = summarize_candidate_transfer_rows(group)
        item = {axis: value for axis, value in zip(context_axes, key)}
        item.update(summary.as_dict())
        out.append(item)
    return out


__all__ = [
    "COUNTER_CANDIDATE_POPULATION",
    "CandidateTransferSummary",
    "candidate_transfer_arms",
    "paired_candidate_delta_rows",
    "paired_candidate_transfer_specs",
    "summarize_candidate_transfer_rows",
    "transfer_context_summary_rows",
]
