from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Iterable, Mapping, Sequence

from .cpp_rollout import CppShadowGameSpec
from .deckspace import DeckVector
from .mulligan import POLICY_LAND_BAND_BUSINESS
from .payoff import StrategyBundle, load_seed_decks
from .terminal_mechanisms import annotate_target_mechanism, mechanism_profile_rows, target_summary_rows, to_float, to_int

CF34_AGENT = "counterfactual_ranker_blend_counter_rev0034"
CF34_MULLIGAN = "mulligan_outcome_ranker_rev0027"
THREAT_AGENT = "threat_rush"
THREAT_MULLIGAN = POLICY_LAND_BAND_BUSINESS


@dataclass(frozen=True)
class DecompositionArm:
    arm_id: str
    question: str
    target: StrategyBundle
    opponent: StrategyBundle
    interpretation: str

    def as_dict(self) -> dict[str, Any]:
        out = asdict(self)
        out["target"] = self.target.as_dict()
        out["opponent"] = self.opponent.as_dict()
        return out


def proportional_counterwall_40() -> DeckVector:
    """40-card control shell preserving the rev0056 counter-wall ratios approximately."""

    deck = DeckVector(40, 21, 10, 5, 3, 1)
    deck.validate()
    return deck


def proportional_overlord_60() -> DeckVector:
    """60-card threat shell preserving the rev0056 Overlord ratios approximately."""

    deck = DeckVector(60, 32, 10, 6, 3, 9)
    deck.validate()
    return deck


def rev0058_decomposition_arms(seed_decks_path) -> list[DecompositionArm]:
    """Concrete ablation arms for the rev0056 life-cell mechanism claim."""

    decks = load_seed_decks(seed_decks_path)
    counter60 = decks["sixty_counterwall_jace"]
    overlord40 = decks["forty_overlord_impending"]
    counter40 = proportional_counterwall_40()
    overlord60 = proportional_overlord_60()

    def bundle(strategy_id: str, deck_name: str, deck: DeckVector, agent: str, mulligan: str) -> StrategyBundle:
        return StrategyBundle(strategy_id, deck_name, deck, agent, mulligan)

    return [
        DecompositionArm(
            "A_original_size_skew",
            "Replicate the exact rev0056 size-skewed target/opponent contrast as the anchor.",
            bundle("cf34_counter_wall", "sixty_counterwall_jace", counter60, CF34_AGENT, CF34_MULLIGAN),
            bundle("pub_threat_overlord", "forty_overlord_impending", overlord40, THREAT_AGENT, THREAT_MULLIGAN),
            "If this reproduces library-out wins, the new panel is anchored to rev0056.",
        ),
        DecompositionArm(
            "B_pilot_swap_size_skew",
            "Swap pilots and mulligan policies across the same two deck shells.",
            bundle("cf34pilot_on_overlord40", "forty_overlord_impending", overlord40, CF34_AGENT, CF34_MULLIGAN),
            bundle("threatpilot_on_counter60", "sixty_counterwall_jace", counter60, THREAT_AGENT, THREAT_MULLIGAN),
            "If the cf34 pilot still wins, the edge follows pilot; if not, it follows the deck shell/size.",
        ),
        DecompositionArm(
            "C_equalized_40v40",
            "Keep pilots fixed but put both shells at forty cards.",
            bundle("cf34_counter_wall_40", "counterwall_jace_proportional40", counter40, CF34_AGENT, CF34_MULLIGAN),
            bundle("pub_threat_overlord", "forty_overlord_impending", overlord40, THREAT_AGENT, THREAT_MULLIGAN),
            "If the target edge collapses here, the 60-card library buffer was doing major work.",
        ),
        DecompositionArm(
            "D_equalized_60v60",
            "Keep pilots fixed but put both shells at sixty cards.",
            bundle("cf34_counter_wall", "sixty_counterwall_jace", counter60, CF34_AGENT, CF34_MULLIGAN),
            bundle("pub_threat_overlord_60", "overlord_impending_proportional60", overlord60, THREAT_AGENT, THREAT_MULLIGAN),
            "If the target edge weakens here, opponent 40-card self-decking was a major contributor.",
        ),
        DecompositionArm(
            "E_same_deck_counter60_pilot",
            "Hold the counter-wall deck fixed on both sides and compare pilots only.",
            bundle("cf34pilot_on_counter60", "sixty_counterwall_jace", counter60, CF34_AGENT, CF34_MULLIGAN),
            bundle("threatpilot_on_counter60", "sixty_counterwall_jace", counter60, THREAT_AGENT, THREAT_MULLIGAN),
            "Same-deck pilot-only control for the counter-wall shell.",
        ),
        DecompositionArm(
            "F_same_deck_overlord40_pilot",
            "Hold the Overlord deck fixed on both sides and compare pilots only.",
            bundle("cf34pilot_on_overlord40", "forty_overlord_impending", overlord40, CF34_AGENT, CF34_MULLIGAN),
            bundle("threatpilot_on_overlord40", "forty_overlord_impending", overlord40, THREAT_AGENT, THREAT_MULLIGAN),
            "Same-deck pilot-only control for the Overlord shell.",
        ),
    ]


def decomposition_specs(
    arms: Sequence[DecompositionArm],
    *,
    simulator_revision: str,
    life_totals: Sequence[int] = (20, 40),
    reps: int = 8,
    base_seed: int = 5858000,
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
                            "target_seat": int(target_seat),
                            "rep": int(rep),
                        }
                        k += 1
    return tuple(specs), meta


def annotate_decomposition_rows(rows: Sequence[Mapping[str, Any]], meta_by_game: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for raw in rows:
        row = dict(raw)
        meta = dict(meta_by_game.get(str(row.get("cpp_shadow_game_id", "")), {}))
        row.update(meta)
        score = None
        if row.get("target_seat") == 0 or str(row.get("target_seat")) == "0":
            score = to_float(row.get("p0_score"), 0.5)
        elif row.get("target_seat") == 1 or str(row.get("target_seat")) == "1":
            score = to_float(row.get("p1_score"), 0.5)
        row["focus_target_score"] = "" if score is None else score
        row["focus_target_terminal_win"] = "" if score is None else (1.0 if score > 0.5 else 0.0)
        row["focus_target_seat"] = row.get("target_seat", "")
        out.append(annotate_target_mechanism(row))
    return out


def decomposition_summary_rows(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return target_summary_rows(
        rows,
        group_keys=(
            "arm_id",
            "starting_life",
            "target",
            "opponent",
            "target_deck",
            "opponent_deck",
            "target_deck_size",
            "opponent_deck_size",
            "target_agent",
            "opponent_agent",
        ),
    )


def decomposition_mechanism_rows(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return mechanism_profile_rows(rows, group_keys=("arm_id", "starting_life", "target", "opponent"))


def score_from_summary_row(row: Mapping[str, Any], *, key: str = "target_mean_score_draw_half") -> float:
    """Safe score reader for comparison tables."""

    return to_float(row.get(key), 0.0)


def library_share_from_summary_row(row: Mapping[str, Any]) -> float:
    """Safe library-out win-share reader for comparison tables."""

    return to_float(row.get("library_out_win_share"), 0.0)


def summary_by_arm_life(summary_rows: Iterable[Mapping[str, Any]]) -> dict[tuple[str, int], Mapping[str, Any]]:
    """Index decomposition summary rows by ``(arm_id, starting_life)``."""

    out: dict[tuple[str, int], Mapping[str, Any]] = {}
    for row in summary_rows:
        arm = str(row.get("arm_id", ""))
        if not arm:
            continue
        out[(arm, to_int(row.get("starting_life"), 0))] = row
    return out


def compare_decomposition_by_life(summary_rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Compare the named decomposition arms at each life total.

    This is the reusable version of the rev0058 script-local comparison helper.
    The gate is deliberately directional: it asks where the observed edge appears
    to travel, not whether a matchup claim is promoted.
    """

    by = summary_by_arm_life(summary_rows)
    out: list[dict[str, Any]] = []
    life_values = sorted({life for (_arm, life) in by if life})
    for life in life_values:
        original = by.get(("A_original_size_skew", life), {})
        pilot_swap = by.get(("B_pilot_swap_size_skew", life), {})
        equal40 = by.get(("C_equalized_40v40", life), {})
        equal60 = by.get(("D_equalized_60v60", life), {})
        same_counter = by.get(("E_same_deck_counter60_pilot", life), {})
        same_overlord = by.get(("F_same_deck_overlord40_pilot", life), {})

        orig_s = score_from_summary_row(original)
        swap_s = score_from_summary_row(pilot_swap)
        eq40_s = score_from_summary_row(equal40)
        eq60_s = score_from_summary_row(equal60)
        control_s = score_from_summary_row(same_counter)
        threatdeck_s = score_from_summary_row(same_overlord)
        if orig_s >= 0.60 and swap_s <= 0.45 and (orig_s - swap_s) >= 0.15:
            provisional = "edge_follows_counterwall_deck_shell_more_than_cf34_pilot"
        elif orig_s >= 0.60 and swap_s >= 0.60:
            provisional = "edge_may_follow_cf34_pilot"
        elif orig_s >= 0.60 and eq40_s < 0.55 and eq60_s < 0.55:
            provisional = "edge_may_require_size_skew"
        else:
            provisional = "inconclusive_small_panel"
        out.append(
            {
                "starting_life": life,
                "original_score": orig_s,
                "pilot_swap_score": swap_s,
                "equalized_40v40_score": eq40_s,
                "equalized_60v60_score": eq60_s,
                "same_counter60_pilot_score": control_s if same_counter else "",
                "same_overlord40_pilot_score": threatdeck_s if same_overlord else "",
                "original_minus_pilot_swap": orig_s - swap_s,
                "original_minus_equalized_40v40": orig_s - eq40_s,
                "original_minus_equalized_60v60": orig_s - eq60_s,
                "equalized_60v60_minus_40v40": eq60_s - eq40_s,
                "original_library_out_win_share": library_share_from_summary_row(original),
                "pilot_swap_library_out_win_share": library_share_from_summary_row(pilot_swap),
                "equalized_40v40_library_out_win_share": library_share_from_summary_row(equal40),
                "equalized_60v60_library_out_win_share": library_share_from_summary_row(equal60),
                "provisional_read": provisional,
            }
        )
    return out


def sample_transition_rows(rows: Iterable[Any], *, limit: int = 240) -> list[dict[str, object]]:
    """Keep compact C++ evidence while preserving all failures first.

    ``rows`` may contain dataclass rows with ``as_dict`` or plain mappings.
    All unsupported/mismatching rows are retained before evenly spaced successful
    evidence rows are sampled.  This prevents the linked cube from ballooning
    with full transition CSVs while keeping enough material for quick inspection.
    """

    materialized = list(rows)

    def as_dict(row: Any) -> dict[str, object]:
        return dict(row.as_dict() if hasattr(row, "as_dict") else row)

    out: list[dict[str, object]] = []
    for raw in materialized:
        row = as_dict(raw)
        supported = str(row.get("supported_by_cpp", "")).lower() in {"true", "1", "yes"} or row.get("supported_by_cpp") is True
        mismatch = row.get("cpp_match") is False or str(row.get("cpp_match", "")).lower() == "false"
        if (not supported) or mismatch:
            out.append(row)
    if len(out) >= limit:
        return out[:limit]
    stride = max(1, len(materialized) // max(1, limit - len(out))) if materialized else 1
    seen = {str(r.get("case_id", "")) for r in out}
    for i, raw in enumerate(materialized):
        if i % stride != 0:
            continue
        row = as_dict(raw)
        case_id = str(row.get("case_id", f"row{i}"))
        if case_id in seen:
            continue
        out.append(row)
        seen.add(case_id)
        if len(out) >= limit:
            break
    return out


def decomposition_gate_report(
    summary: Mapping[str, object],
    replay_results: Sequence[Mapping[str, object]],
    rows: Sequence[Mapping[str, object]],
    *,
    min_games: int = 180,
    required_arms: Sequence[str] = ("B_pilot_swap_size_skew", "C_equalized_40v40", "D_equalized_60v60"),
    min_replay_passed: int = 8,
) -> dict[str, object]:
    """Reusable cleanliness/parity gate for decomposition runs."""

    errors: list[str] = []
    warnings: list[str] = []
    if int(summary.get("games", 0)) < int(min_games):
        errors.append(f"fewer than {min_games} decomposition games")
    if int(summary.get("truncations", 0)) != 0:
        errors.append("terminal-clean gate failed: truncations present")
    if int(summary.get("python_errors", 0)) != 0:
        errors.append("python errors occurred during C++ shadow rollout")
    cpp = summary.get("cpp_shadow_summary", {})
    if isinstance(cpp, Mapping):
        if int(cpp.get("mismatches", 0)) != 0:
            errors.append("C++ shadow mismatches present")
        if int(cpp.get("skipped_events", 0)) != 0:
            warnings.append("C++ shadow skipped events present")
    trace = summary.get("cpp_trace_summary", {})
    if isinstance(trace, Mapping):
        if int(trace.get("mismatches", 0)) != 0:
            errors.append("C++ trace mismatches present")
    if sum(1 for r in replay_results if r.get("passed") is True) < int(min_replay_passed):
        errors.append(f"fewer than {min_replay_passed} replay samples passed")
    present_arms = {str(r.get("arm_id")) for r in rows}
    for arm_id in required_arms:
        if arm_id not in present_arms:
            errors.append(f"required arm missing: {arm_id}")
    return {"passed": not errors, "errors": errors, "warnings": warnings}
