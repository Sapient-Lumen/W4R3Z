from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping, Sequence

from .closure_vs_counter import ClosureVsCounterArm
from .cpp_rollout import CppShadowGameSpec
from .deckspace import DeckVector
from .library_buffer_sweep import scale_deck_to_legal_size
from .payoff import StrategyBundle, load_seed_decks
from .terminal_decomposition import CF34_AGENT, CF34_MULLIGAN, THREAT_MULLIGAN
from .terminal_mechanisms import annotate_target_mechanism, mechanism_profile_rows, target_summary_rows, to_float, to_int
from .threat_closure import THREAT_CLOSURE_AGENT

COUNTER_GUARD_AGENT = "counter_guard"
LEGACY_COUNTER_AXIS = "legacy_cf34_counter_ranker"
GUARDED_COUNTER_AXIS = "public_counter_guard"
CLOSURE_THREAT_AXIS = "library_aware_threat_closure"


@dataclass(frozen=True)
class CounterResponseArm:
    """One counter-policy response arm against the guarded threat baseline.

    rev0064 demoted the old counter-wall edge because it collapsed when the
    Overlord opponent used ``threat_closure`` instead of ``threat_rush``.  This
    arm asks the next necessary question: is the counter-wall *deck* dead, or was
    the old CF34/ranker pilot also stale once the threat side stopped self-decking?
    """

    arm_id: str
    question: str
    target: StrategyBundle
    opponent: StrategyBundle
    counter_policy_axis: str
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


def rev0065_counter_response_arms(seed_decks_path) -> list[CounterResponseArm]:
    """Build a matched counter-policy response panel against ``threat_closure``.

    The opponent is held at the guarded threat policy.  The counter deck and
    size cell are held fixed while the target policy changes from the historical
    CF34 counter ranker to the new public ``counter_guard`` profile.
    """

    decks = load_seed_decks(seed_decks_path)
    counter60 = decks["sixty_counterwall_jace"]
    threat40 = decks["forty_overlord_impending"]
    counter40 = scale_deck_to_legal_size(counter60, 40)
    threat60 = scale_deck_to_legal_size(threat40, 60)

    def counter(size: int, policy: str) -> StrategyBundle:
        deck = counter60 if size == 60 else counter40
        deck_name = "sixty_counterwall_jace" if size == 60 else "forty_counterwall_scaled_from60"
        if policy == CF34_AGENT:
            return _bundle(
                f"cf34_counter_wall{size}",
                deck_name,
                deck,
                CF34_AGENT,
                CF34_MULLIGAN,
            )
        return _bundle(
            f"guard_counter_wall{size}",
            deck_name,
            deck,
            COUNTER_GUARD_AGENT,
            CF34_MULLIGAN,
        )

    def threat(size: int) -> StrategyBundle:
        deck = threat40 if size == 40 else threat60
        deck_name = "forty_overlord_impending" if size == 40 else "sixty_overlord_scaled_from40"
        return _bundle(f"pub_threat{size}_closure", deck_name, deck, THREAT_CLOSURE_AGENT, THREAT_MULLIGAN)

    plan = [
        ("A", 60, 40, "Original size-skew cell, but with guarded threat closure fixed."),
        ("B", 40, 40, "Size-normalized 40-vs-40 response cell against guarded threat closure."),
        ("C", 60, 60, "Size-normalized 60-vs-60 response cell against guarded threat closure."),
    ]
    arms: list[CounterResponseArm] = []
    for prefix, counter_size, threat_size, question in plan:
        for policy in (CF34_AGENT, COUNTER_GUARD_AGENT):
            legacy = policy == CF34_AGENT
            axis = LEGACY_COUNTER_AXIS if legacy else GUARDED_COUNTER_AXIS
            arms.append(
                CounterResponseArm(
                    arm_id=f"{prefix}_{'legacy' if legacy else 'guard'}_counter{counter_size}_vs_threat{threat_size}",
                    question=question,
                    target=counter(counter_size, policy),
                    opponent=threat(threat_size),
                    counter_policy_axis=axis,
                    threat_policy_axis=CLOSURE_THREAT_AXIS,
                    size_axis=f"counter{counter_size}_vs_threat{threat_size}",
                    interpretation=(
                        "Historical counter policy under the guarded threat baseline.  This is the rev0064-demoted control."
                        if legacy
                        else "Public counter response policy with library-aware Jace/Force/attack guards.  Improvement here is a counter-deck rescue candidate, not a proven claim."
                    ),
                )
            )
    return arms


def counter_response_specs(
    arms: Sequence[CounterResponseArm],
    *,
    simulator_revision: str,
    life_totals: Sequence[int] = (20, 40),
    reps: int = 3,
    base_seed: int = 6565000,
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
                            "counter_policy_axis": arm.counter_policy_axis,
                            "threat_policy_axis": arm.threat_policy_axis,
                            "size_axis": arm.size_axis,
                        }
                        k += 1
    return tuple(specs), meta




def counter_response_stress_specs(
    arms: Sequence[CounterResponseArm],
    *,
    candidate_cells: Sequence[tuple[str, int]],
    simulator_revision: str,
    reps: int = 4,
    base_seed: int = 6565900,
    max_decisions: int = 900,
) -> tuple[tuple[CppShadowGameSpec, ...], dict[str, dict[str, Any]]]:
    """Generate seed-disjoint confirmation specs for selected rescue cells.

    ``counter_response_specs`` gives the broad panel.  This helper keeps the
    scientific follow-up narrow: only cells whose first pass suggests a possible
    counter-deck rescue are expanded, and both counter policies are retained so
    the stress pass remains a matched policy comparison rather than a victory lap.
    """

    wanted = {(str(axis), int(life)) for axis, life in candidate_cells}
    specs: list[CppShadowGameSpec] = []
    meta: dict[str, dict[str, Any]] = {}
    k = 0
    for arm in arms:
        for axis, life in sorted(wanted):
            if arm.size_axis != axis:
                continue
            for target_seat in (0, 1):
                left, right = (arm.target, arm.opponent) if target_seat == 0 else (arm.opponent, arm.target)
                for starting_player in (0, 1):
                    for rep in range(int(reps)):
                        gid = f"s{k:05d}_{arm.arm_id}_life{life}_seat{target_seat}_sp{starting_player}_r{rep}"
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
                            "counter_policy_axis": arm.counter_policy_axis,
                            "threat_policy_axis": arm.threat_policy_axis,
                            "size_axis": arm.size_axis,
                            "stress_cell": f"{arm.size_axis}_life{life}",
                            "stress_seed_disjoint": True,
                        }
                        k += 1
    return tuple(specs), meta

def annotate_counter_response_rows(rows: Sequence[Mapping[str, Any]], meta: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
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


def counter_response_summary_rows(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return target_summary_rows(
        rows,
        group_keys=(
            "arm_id",
            "starting_life",
            "size_axis",
            "counter_policy_axis",
            "threat_policy_axis",
            "target_deck_size",
            "opponent_deck_size",
            "target",
            "opponent",
        ),
    )


def counter_response_mechanism_rows(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return mechanism_profile_rows(rows, group_keys=("arm_id", "starting_life", "size_axis", "counter_policy_axis", "target", "opponent"))


def compare_counter_response_by_life(summary_rows: Iterable[Mapping[str, Any]]) -> list[dict[str, object]]:
    """Compare counter policies without turning absent rows into a zero score."""

    by: dict[tuple[str, str, int], Mapping[str, Any]] = {}
    for row in summary_rows:
        by[(str(row.get("size_axis", "")), str(row.get("counter_policy_axis", "")), to_int(row.get("starting_life"), 0))] = row
    cells = sorted({(axis, life) for (axis, _policy, life) in by if axis and life})
    required_axes = (LEGACY_COUNTER_AXIS, GUARDED_COUNTER_AXIS)
    out: list[dict[str, object]] = []
    for axis, life in cells:
        rows_by_policy = {policy: by.get((axis, policy, life)) for policy in required_axes}
        missing = [policy for policy, row in rows_by_policy.items() if row is None]
        if missing:
            out.append(
                {
                    "size_axis": axis,
                    "starting_life": life,
                    "legacy_cf34_counter_score": None,
                    "public_counter_guard_score": None,
                    "guard_minus_legacy_counter_score_delta": None,
                    "legacy_library_out_win_share": None,
                    "guard_library_out_win_share": None,
                    "legacy_target_library_out_wins": None,
                    "guard_target_library_out_wins": None,
                    "legacy_target_life_total_wins": None,
                    "guard_target_life_total_wins": None,
                    "missing_counter_policy_axes": missing,
                    "provisional_read": "incomplete_matrix",
                }
            )
            continue

        legacy = rows_by_policy[LEGACY_COUNTER_AXIS]
        guard = rows_by_policy[GUARDED_COUNTER_AXIS]
        assert legacy is not None and guard is not None
        legacy_score = to_float(legacy.get("target_mean_score_draw_half"), 0.0)
        guard_score = to_float(guard.get("target_mean_score_draw_half"), 0.0)
        delta = guard_score - legacy_score
        if guard_score >= 0.60 and delta >= 0.20:
            read = "counter_deck_rescue_candidate"
        elif guard_score >= 0.50 and delta >= 0.15:
            read = "counter_policy_improves_but_underpowered"
        elif abs(delta) < 0.15 and guard_score < 0.45:
            read = "no_counter_policy_rescue"
        elif delta <= -0.15:
            read = "counter_guard_worse_than_legacy"
        else:
            read = "mixed_or_underpowered"
        out.append(
            {
                "size_axis": axis,
                "starting_life": life,
                "legacy_cf34_counter_score": legacy_score,
                "public_counter_guard_score": guard_score,
                "guard_minus_legacy_counter_score_delta": delta,
                "legacy_library_out_win_share": to_float(legacy.get("library_out_win_share"), 0.0),
                "guard_library_out_win_share": to_float(guard.get("library_out_win_share"), 0.0),
                "legacy_target_library_out_wins": to_int(legacy.get("target_library_out_wins"), 0),
                "guard_target_library_out_wins": to_int(guard.get("target_library_out_wins"), 0),
                "legacy_target_life_total_wins": to_int(legacy.get("target_life_total_wins"), 0),
                "guard_target_life_total_wins": to_int(guard.get("target_life_total_wins"), 0),
                "missing_counter_policy_axes": [],
                "provisional_read": read,
            }
        )
    return out


def counter_response_gate_report(summary: Mapping[str, object], rows: Sequence[Mapping[str, object]], *, min_games: int = 120) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    if int(summary.get("games", 0)) < int(min_games):
        errors.append(f"fewer than {min_games} counter-response games")
    if int(summary.get("truncations", 0)) != 0:
        errors.append("terminal-clean gate failed: truncations present")
    if int(summary.get("python_errors", 0)) != 0:
        errors.append("python errors occurred during C++ shadow rollout")
    if int(summary.get("forensic_games", 0)) != int(summary.get("games", -1)):
        errors.append("forensic rerun did not cover every game")
    if int(summary.get("closure_feature_games", 0)) != int(summary.get("games", -1)):
        errors.append("closure feature rerun did not cover every game")
    cpp = summary.get("cpp_shadow_summary", {})
    if isinstance(cpp, Mapping):
        if int(cpp.get("mismatches", 0)) != 0:
            errors.append("C++ shadow mismatches present")
        if int(cpp.get("skipped_events", 0)) != 0:
            warnings.append("C++ shadow skipped events present")
    policies = {str(r.get("counter_policy_axis")) for r in rows}
    for required in (LEGACY_COUNTER_AXIS, GUARDED_COUNTER_AXIS):
        if required not in policies:
            errors.append(f"required counter policy missing: {required}")
    size_axes = {str(r.get("size_axis")) for r in rows}
    for required in ("counter60_vs_threat40", "counter40_vs_threat40", "counter60_vs_threat60"):
        if required not in size_axes:
            errors.append(f"required size axis missing: {required}")
    return {"passed": not errors, "errors": errors, "warnings": warnings}


def claim_quarantine_rows(
    closure_vs_counter_comparisons: Sequence[Mapping[str, object]],
    counter_response_comparisons: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    """Create a compact live quarantine table for historical counter-wall claims.

    This is intentionally an executable table, not prose.  A cell is quarantined
    when the old counter score was materially dependent on the legacy threat
    baseline.  Counter-response rows are then attached to show whether the new
    public counter guard rescues the same cell against ``threat_closure``.
    """

    response_by = {
        (str(r.get("size_axis")), to_int(r.get("starting_life"), 0)): r
        for r in counter_response_comparisons
    }
    out: list[dict[str, object]] = []
    for old in closure_vs_counter_comparisons:
        axis = str(old.get("size_axis", ""))
        life = to_int(old.get("starting_life"), 0)
        if (axis, life) not in response_by:
            continue
        response = response_by[(axis, life)]
        legacy_score = to_float(old.get("legacy_counter_score"), 0.0)
        closure_score = to_float(old.get("closure_counter_score"), 0.0)
        closure_delta = to_float(old.get("closure_minus_legacy_counter_score_delta"), closure_score - legacy_score)
        guard_score = to_float(response.get("public_counter_guard_score"), 0.0)
        guard_delta = to_float(response.get("guard_minus_legacy_counter_score_delta"), 0.0)
        if closure_score < 0.45 and closure_delta <= -0.20:
            status = "quarantined_old_edge_threat_baseline_artifact"
        elif closure_score >= 0.55:
            status = "survives_guarded_threat_baseline"
        else:
            status = "mixed_requires_more_reps"
        if guard_score >= 0.60 and guard_delta >= 0.20:
            rescue = "counter_guard_rescue_candidate"
        elif guard_score >= 0.50 and guard_delta >= 0.15:
            rescue = "partial_counter_guard_rescue"
        elif guard_score < 0.45:
            rescue = "no_current_counter_guard_rescue"
        else:
            rescue = "unclear_counter_guard_rescue"
        out.append(
            {
                "size_axis": axis,
                "starting_life": life,
                "historical_legacy_threat_score": legacy_score,
                "guarded_threat_score": closure_score,
                "guarded_minus_legacy_threat_delta": closure_delta,
                "public_counter_guard_score_against_guarded_threat": guard_score,
                "counter_guard_minus_legacy_cf34_delta": guard_delta,
                "quarantine_status": status,
                "counter_response_status": rescue,
                "required_next_action": (
                    "Do not cite old counter-wall edge unless rerun against threat_closure or a stronger named threat baseline."
                    if status.startswith("quarantined")
                    else "May cite only with policy/baseline labels and current guarded-threat caveat."
                ),
            }
        )
    return out
