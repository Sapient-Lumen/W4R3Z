from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping, Sequence

from .cpp_rollout import CppShadowGameSpec
from .deckspace import DeckVector
from .library_buffer_sweep import scale_deck_to_legal_size
from .payoff import StrategyBundle, load_seed_decks
from .terminal_decomposition import CF34_AGENT, CF34_MULLIGAN, THREAT_MULLIGAN
from .terminal_mechanisms import annotate_target_mechanism, mechanism_profile_rows, target_summary_rows, to_float, to_int
from .threat_closure import THREAT_CLOSURE_AGENT, THREAT_RUSH_AGENT


@dataclass(frozen=True)
class ClosureVsCounterArm:
    """One matched threat-policy arm against an active counter-wall target.

    The focal target is the counter-wall strategy.  The opponent is the Overlord
    threat shell with either the legacy rush policy or the guarded closure policy.
    This lets rev0064 ask whether rev0056--rev0062 counter-wall claims were mainly
    exploiting a bad threat pilot, rather than discovering robust counter strategy.
    """

    arm_id: str
    question: str
    target: StrategyBundle
    opponent: StrategyBundle
    threat_policy_axis: str
    size_axis: str
    interpretation: str

    def as_dict(self) -> dict[str, Any]:
        out = asdict(self)
        out["target"] = self.target.as_dict()
        out["opponent"] = self.opponent.as_dict()
        return out


def _bundle(strategy_id: str, deck_name: str, deck: DeckVector, agent: str, mulligan: str) -> StrategyBundle:
    return StrategyBundle(strategy_id, deck_name, deck, agent, mulligan)


def rev0064_closure_vs_counter_arms(seed_decks_path) -> list[ClosureVsCounterArm]:
    """Matched active counter-wall controls for the guarded threat policy.

    rev0063 proved that ``threat_closure`` closes much better than ``threat_rush``
    against inert all-Island targets.  That did not yet answer the claim-relevant
    question: does the original counter-wall edge survive against a threat pilot
    that no longer self-decks casually?  These arms keep the counter target fixed
    while swapping only the threat public policy, and also include 40-vs-40 and
    60-vs-60 size-normalized controls.
    """

    decks = load_seed_decks(seed_decks_path)
    counter60 = decks["sixty_counterwall_jace"]
    threat40 = decks["forty_overlord_impending"]
    counter40 = scale_deck_to_legal_size(counter60, 40)
    threat60 = scale_deck_to_legal_size(threat40, 60)

    def counter(size: int) -> StrategyBundle:
        if size == 60:
            return _bundle("cf34_counter_wall60", "sixty_counterwall_jace", counter60, CF34_AGENT, CF34_MULLIGAN)
        return _bundle("cf34_counter_wall40_scaled", "forty_counterwall_scaled_from60", counter40, CF34_AGENT, CF34_MULLIGAN)

    def threat(size: int, policy: str) -> StrategyBundle:
        deck = threat40 if size == 40 else threat60
        suffix = "rush" if policy == THREAT_RUSH_AGENT else "closure"
        name = "forty_overlord_impending" if size == 40 else "sixty_overlord_scaled_from40"
        return _bundle(f"pub_threat{size}_{suffix}", name, deck, policy, THREAT_MULLIGAN)

    plan = [
        ("A", 60, 40, "Anchor: original 60-card counter-wall target against original 40-card threat shell."),
        ("B", 40, 40, "Size-normalized 40-vs-40 active-shell control."),
        ("C", 60, 60, "Size-normalized 60-vs-60 active-shell control."),
    ]
    arms: list[ClosureVsCounterArm] = []
    for prefix, target_size, threat_size, question in plan:
        for policy in (THREAT_RUSH_AGENT, THREAT_CLOSURE_AGENT):
            policy_label = "legacy_threat_rush" if policy == THREAT_RUSH_AGENT else "library_aware_threat_closure"
            arms.append(
                ClosureVsCounterArm(
                    arm_id=f"{prefix}_{'legacy' if policy == THREAT_RUSH_AGENT else 'closure'}_counter{target_size}_vs_threat{threat_size}",
                    question=question,
                    target=counter(target_size),
                    opponent=threat(threat_size, policy),
                    threat_policy_axis=policy_label,
                    size_axis=f"counter{target_size}_vs_threat{threat_size}",
                    interpretation=(
                        "Legacy threat baseline.  If counter score is high here but collapses under closure, the old edge was threat-pilot-sensitive."
                        if policy == THREAT_RUSH_AGENT
                        else "Guarded threat test.  If counter score remains high here, the counter-wall edge survives the closure audit."
                    ),
                )
            )
    return arms


def closure_vs_counter_specs(
    arms: Sequence[ClosureVsCounterArm],
    *,
    simulator_revision: str,
    life_totals: Sequence[int] = (20, 40),
    reps: int = 3,
    base_seed: int = 6464000,
    max_decisions: int = 900,
) -> tuple[tuple[CppShadowGameSpec, ...], dict[str, dict[str, Any]]]:
    specs: list[CppShadowGameSpec] = []
    meta: dict[str, dict[str, Any]] = {}
    k = 0
    for arm in arms:
        for life in life_totals:
            for target_seat in (0, 1):
                left, right = (arm.target, arm.opponent) if target_seat == 0 else (arm.opponent, arm.target)
                for starting_player in (0, 1):
                    for rep in range(int(reps)):
                        gid = f"g{k:05d}_{arm.arm_id}_life{life}_seat{target_seat}_sp{starting_player}_r{rep}"
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
                                seed=int(base_seed + k),
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
                            "threat_policy_axis": arm.threat_policy_axis,
                            "size_axis": arm.size_axis,
                        }
                        k += 1
    return tuple(specs), meta


def annotate_closure_vs_counter_rows(rows: Sequence[Mapping[str, Any]], meta: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        gid = str(row.get("cpp_shadow_game_id", ""))
        merged = dict(row)
        merged.update(meta.get(gid, {}))
        seat = to_int(merged.get("target_seat"), 0)
        merged["focus_target_seat"] = seat
        merged["focus_target_score"] = to_float(merged.get("p0_score" if seat == 0 else "p1_score"), 0.5)
        out.append(annotate_target_mechanism(merged))
    return out


def closure_vs_counter_summary_rows(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return target_summary_rows(
        rows,
        group_keys=(
            "arm_id",
            "starting_life",
            "size_axis",
            "threat_policy_axis",
            "target_deck_size",
            "opponent_deck_size",
            "target",
            "opponent",
        ),
    )


def closure_vs_counter_mechanism_rows(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return mechanism_profile_rows(rows, group_keys=("arm_id", "starting_life", "size_axis", "threat_policy_axis", "target", "opponent"))


def compare_closure_vs_counter_by_life(summary_rows: Iterable[Mapping[str, Any]]) -> list[dict[str, object]]:
    """Compute legacy-vs-closure deltas, failing closed on incomplete cells."""

    by: dict[tuple[str, str, int], Mapping[str, Any]] = {}
    for row in summary_rows:
        by[(str(row.get("size_axis", "")), str(row.get("threat_policy_axis", "")), to_int(row.get("starting_life"), 0))] = row
    cells = sorted({(axis, life) for (axis, _policy, life) in by if axis and life})
    required_axes = ("legacy_threat_rush", "library_aware_threat_closure")
    out: list[dict[str, object]] = []
    for axis, life in cells:
        rows_by_policy = {policy: by.get((axis, policy, life)) for policy in required_axes}
        missing = [policy for policy, row in rows_by_policy.items() if row is None]
        if missing:
            out.append(
                {
                    "size_axis": axis,
                    "starting_life": life,
                    "legacy_counter_score": None,
                    "closure_counter_score": None,
                    "closure_minus_legacy_counter_score_delta": None,
                    "legacy_library_out_win_share": None,
                    "closure_library_out_win_share": None,
                    "legacy_target_library_out_wins": None,
                    "closure_target_library_out_wins": None,
                    "legacy_target_life_total_wins": None,
                    "closure_target_life_total_wins": None,
                    "missing_threat_policy_axes": missing,
                    "provisional_read": "incomplete_matrix",
                }
            )
            continue

        legacy = rows_by_policy["legacy_threat_rush"]
        closure = rows_by_policy["library_aware_threat_closure"]
        assert legacy is not None and closure is not None
        legacy_score = to_float(legacy.get("target_mean_score_draw_half"), 0.0)
        closure_score = to_float(closure.get("target_mean_score_draw_half"), 0.0)
        legacy_lib_share = to_float(legacy.get("library_out_win_share"), 0.0)
        closure_lib_share = to_float(closure.get("library_out_win_share"), 0.0)
        delta = closure_score - legacy_score
        if closure_score >= 0.60 and abs(delta) <= 0.15:
            read = "counter_edge_survives_guarded_threat"
        elif closure_score < 0.45 and delta <= -0.20:
            read = "counter_edge_mostly_legacy_threat_artifact"
        elif closure_score >= 0.50 and delta <= -0.20:
            read = "counter_edge_weakened_but_not_erased"
        elif delta >= 0.15:
            read = "guarded_threat_worse_in_this_cell"
        else:
            read = "mixed_or_underpowered"
        out.append(
            {
                "size_axis": axis,
                "starting_life": life,
                "legacy_counter_score": legacy_score,
                "closure_counter_score": closure_score,
                "closure_minus_legacy_counter_score_delta": delta,
                "legacy_library_out_win_share": legacy_lib_share,
                "closure_library_out_win_share": closure_lib_share,
                "legacy_target_library_out_wins": to_int(legacy.get("target_library_out_wins"), 0),
                "closure_target_library_out_wins": to_int(closure.get("target_library_out_wins"), 0),
                "legacy_target_life_total_wins": to_int(legacy.get("target_life_total_wins"), 0),
                "closure_target_life_total_wins": to_int(closure.get("target_life_total_wins"), 0),
                "missing_threat_policy_axes": [],
                "provisional_read": read,
            }
        )
    return out


def closure_vs_counter_gate_report(summary: Mapping[str, object], feature_rows: Sequence[Mapping[str, object]], *, min_games: int = 120) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    if int(summary.get("games", 0)) < int(min_games):
        errors.append(f"fewer than {min_games} closure-vs-counter games")
    if int(summary.get("truncations", 0)) != 0:
        errors.append("terminal-clean gate failed: truncations present")
    if int(summary.get("python_errors", 0)) != 0:
        errors.append("python errors occurred during C++ shadow rollout")
    if int(summary.get("closure_feature_games", 0)) != int(summary.get("games", -1)):
        errors.append("closure feature rerun did not cover every game")
    cpp = summary.get("cpp_shadow_summary", {})
    if isinstance(cpp, Mapping):
        if int(cpp.get("mismatches", 0)) != 0:
            errors.append("C++ shadow mismatches present")
        if int(cpp.get("skipped_events", 0)) != 0:
            warnings.append("C++ shadow skipped events present")
    policies = {str(r.get("threat_policy_axis")) for r in feature_rows}
    for required in ("legacy_threat_rush", "library_aware_threat_closure"):
        if required not in policies:
            errors.append(f"required threat policy missing: {required}")
    size_axes = {str(r.get("size_axis")) for r in feature_rows}
    for required in ("counter60_vs_threat40", "counter40_vs_threat40", "counter60_vs_threat60"):
        if required not in size_axes:
            errors.append(f"required size axis missing: {required}")
    return {"passed": not errors, "errors": errors, "warnings": warnings}

def compare_closure_vs_counter_features_by_life(summary_rows: Sequence[Mapping[str, Any]]) -> list[dict[str, object]]:
    """Compare threat closure features under legacy vs guarded policies.

    ``summarize_threat_closure_features`` can be reused for any focal target; this
    adapter makes its output readable for the rev0064 active-counter panel by
    keying on ``size_axis`` rather than the rev0063 inert-only ``target_size_axis``.
    """

    by: dict[tuple[str, str, int], Mapping[str, Any]] = {}
    for row in summary_rows:
        by[(str(row.get("size_axis", "")), str(row.get("threat_policy_axis", "")), to_int(row.get("starting_life"), 0))] = row
    cells = sorted({(axis, life) for (axis, _policy, life) in by if axis and life})
    out: list[dict[str, object]] = []
    for axis, life in cells:
        legacy = by.get((axis, "legacy_threat_rush", life), {})
        closure = by.get((axis, "library_aware_threat_closure", life), {})
        def f(row: Mapping[str, Any], name: str) -> float:
            return to_float(row.get(name), 0.0)
        legacy_selfdeck_rate = f(legacy, "mean_threat_selfdeck_on_attack_trigger") + f(legacy, "mean_threat_selfdeck_on_overlord_cast") + f(legacy, "mean_threat_selfdeck_on_jace_zero")
        closure_selfdeck_rate = f(closure, "mean_threat_selfdeck_on_attack_trigger") + f(closure, "mean_threat_selfdeck_on_overlord_cast") + f(closure, "mean_threat_selfdeck_on_jace_zero")
        out.append(
            {
                "size_axis": axis,
                "starting_life": life,
                "legacy_counter_score": f(legacy, "mean_target_score"),
                "closure_counter_score": f(closure, "mean_target_score"),
                "closure_minus_legacy_counter_score_delta": f(closure, "mean_target_score") - f(legacy, "mean_target_score"),
                "legacy_threat_score": f(legacy, "mean_threat_score"),
                "closure_threat_score": f(closure, "mean_threat_score"),
                "legacy_threat_selfdeck_event_rate": legacy_selfdeck_rate,
                "closure_threat_selfdeck_event_rate": closure_selfdeck_rate,
                "legacy_mean_jace_zero_actions": f(legacy, "mean_threat_jace_zero_actions"),
                "closure_mean_jace_zero_actions": f(closure, "mean_threat_jace_zero_actions"),
                "legacy_mean_attackers_to_player": f(legacy, "mean_threat_declared_attackers_to_player"),
                "closure_mean_attackers_to_player": f(closure, "mean_threat_declared_attackers_to_player"),
                "legacy_threat_selfdeck_losses": to_int(legacy.get("threat_selfdeck_losses"), 0),
                "closure_threat_selfdeck_losses": to_int(closure.get("threat_selfdeck_losses"), 0),
                "provisional_read": (
                    "closure_guard_reduces_selfdeck_and_counter_score"
                    if closure_selfdeck_rate < legacy_selfdeck_rate and f(closure, "mean_target_score") + 0.15 < f(legacy, "mean_target_score")
                    else "closure_changes_counter_score_without_selfdeck_drop"
                    if f(closure, "mean_target_score") + 0.15 < f(legacy, "mean_target_score")
                    else "no_clear_guard_improvement"
                ),
            }
        )
    return out
