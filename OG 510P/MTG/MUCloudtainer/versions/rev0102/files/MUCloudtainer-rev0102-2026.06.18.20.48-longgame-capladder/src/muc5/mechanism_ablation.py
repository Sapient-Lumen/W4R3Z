from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping, Sequence

from .cpp_rollout import CppShadowGameSpec
from .deckspace import DeckVector
from .payoff import StrategyBundle, load_seed_decks
from .terminal_decomposition import CF34_AGENT, CF34_MULLIGAN, THREAT_AGENT, THREAT_MULLIGAN
from .terminal_mechanisms import annotate_target_mechanism, mechanism_profile_rows, target_summary_rows, to_float, to_int


@dataclass(frozen=True)
class MechanismAblationArm:
    arm_id: str
    question: str
    target: StrategyBundle
    opponent: StrategyBundle
    ablation_axis: str
    interpretation: str

    def as_dict(self) -> dict[str, Any]:
        out = asdict(self)
        out["target"] = self.target.as_dict()
        out["opponent"] = self.opponent.as_dict()
        return out


def _validate_same_size(deck: DeckVector) -> DeckVector:
    deck.validate()
    return deck


def replace_jace_with_islands(deck: DeckVector) -> DeckVector:
    """Remove Jace copies while preserving deck size and the other nonland counts.

    This is a conservative ablation: it tests whether the shell's active Jace/
    Brainstorm machinery is necessary while keeping the library buffer, countermagic,
    Force pitch density, and Overlord count unchanged.  The replacement card is an
    Island because it is the least strategically expressive MUC-5 card once the game
    already has enough mana.
    """

    return _validate_same_size(DeckVector(deck.size, deck.island + deck.jace, deck.counterspell, deck.force, 0, deck.overlord))


def replace_counterspell_with_islands(deck: DeckVector) -> DeckVector:
    """Remove Counterspell copies while preserving deck size and all threats.

    This is intentionally harsher than a smooth ratio shrink.  It asks whether the
    claimed endurance shell is merely a large library with Jace, or whether dense
    two-mana permission is doing indispensable survival work.
    """

    return _validate_same_size(DeckVector(deck.size, deck.island + deck.counterspell, 0, deck.force, deck.jace, deck.overlord))


def replace_jace_and_counterspell_with_islands(deck: DeckVector) -> DeckVector:
    """Remove both active Jace and Counterspell while preserving the 60-card buffer."""

    return _validate_same_size(DeckVector(deck.size, deck.island + deck.jace + deck.counterspell, 0, deck.force, 0, deck.overlord))


def all_island_buffer_deck(size: int = 60) -> DeckVector:
    """A deliberately inert deck that isolates passive library-size pressure."""

    return _validate_same_size(DeckVector(int(size), int(size), 0, 0, 0, 0))


def rev0061_mechanism_ablation_arms(seed_decks_path) -> list[MechanismAblationArm]:
    """Focused causal ablations for the counter-wall endurance claim.

    The arms keep the public threat opponent fixed and perturb the target counter-wall
    shell.  They are deliberately fewer and sharper than a new registry sweep: the
    live risk is mistaking passive library size for active Jace/counter machinery.
    """

    decks = load_seed_decks(seed_decks_path)
    counter60 = decks["sixty_counterwall_jace"]
    overlord40 = decks["forty_overlord_impending"]
    no_jace = replace_jace_with_islands(counter60)
    no_counterspell = replace_counterspell_with_islands(counter60)
    no_jace_no_counterspell = replace_jace_and_counterspell_with_islands(counter60)
    all_island60 = all_island_buffer_deck(60)

    def bundle(strategy_id: str, deck_name: str, deck: DeckVector, agent: str, mulligan: str) -> StrategyBundle:
        return StrategyBundle(strategy_id, deck_name, deck, agent, mulligan)

    opponent = bundle("pub_threat_overlord", "forty_overlord_impending", overlord40, THREAT_AGENT, THREAT_MULLIGAN)
    return [
        MechanismAblationArm(
            arm_id="A_original_size_skew",
            question="Anchor the current seed-disjoint panel to the original 60-card counter-wall vs 40-card threat shell.",
            target=bundle("cf34_counter_wall", "sixty_counterwall_jace", counter60, CF34_AGENT, CF34_MULLIGAN),
            opponent=opponent,
            ablation_axis="none_anchor",
            interpretation="If this arm is positive and terminal-clean, the ablation panel is comparable to rev0056-rev0060.",
        ),
        MechanismAblationArm(
            arm_id="G_target_no_jace60",
            question="Remove target Jace/Brainstorm while preserving 60-card size, counter count, Force count, and singleton Overlord.",
            target=bundle("cf34_counter_wall_no_jace60", "sixty_counterwall_no_jace_islands", no_jace, CF34_AGENT, CF34_MULLIGAN),
            opponent=opponent,
            ablation_axis="target_jace_removed",
            interpretation="If the edge persists, passive 60-card/counter endurance may be sufficient; if it collapses, active Jace machinery matters.",
        ),
        MechanismAblationArm(
            arm_id="H_target_no_counterspell60",
            question="Remove target Counterspell while preserving 60-card size, Jace count, Force count, and singleton Overlord.",
            target=bundle("cf34_counter_wall_no_counterspell60", "sixty_counterwall_no_counterspell_islands", no_counterspell, CF34_AGENT, CF34_MULLIGAN),
            opponent=opponent,
            ablation_axis="target_counterspell_removed",
            interpretation="If the edge collapses here, dense permission is survival-critical rather than merely decorative.",
        ),
        MechanismAblationArm(
            arm_id="I_target_no_jace_no_counterspell60",
            question="Remove both target Jace and Counterspell while preserving the 60-card library buffer.",
            target=bundle(
                "cf34_counter_wall_no_jace_no_counterspell60",
                "sixty_counterwall_no_jace_no_counterspell_islands",
                no_jace_no_counterspell,
                CF34_AGENT,
                CF34_MULLIGAN,
            ),
            opponent=opponent,
            ablation_axis="target_jace_and_counterspell_removed",
            interpretation="If only this collapses, the shell has redundant endurance tools; if no-Jace/no-Counterspell each collapse, both axes matter independently.",
        ),
        MechanismAblationArm(
            arm_id="J_target_all_island60",
            question="Use an inert 60-Island target to test whether the opponent can lose to deck-size/library pressure alone.",
            target=bundle("cf34_buffer_only_all_island60", "sixty_all_island_buffer", all_island60, CF34_AGENT, CF34_MULLIGAN),
            opponent=opponent,
            ablation_axis="passive_library_buffer_only",
            interpretation="If this arm wins at a meaningful rate, the current claim is mostly a deck-size/self-deck exploit rather than a strategic counter-wall shell.",
        ),
    ]


def mechanism_ablation_specs(
    arms: Sequence[MechanismAblationArm],
    *,
    simulator_revision: str,
    life_totals: Sequence[int] = (20, 40),
    reps: int = 6,
    base_seed: int = 6161000,
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
                            "ablation_axis": arm.ablation_axis,
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
                            "target_jace_count": arm.target.deck.jace,
                            "target_counterspell_count": arm.target.deck.counterspell,
                            "target_force_count": arm.target.deck.force,
                            "target_island_count": arm.target.deck.island,
                            "target_overlord_count": arm.target.deck.overlord,
                            "target_seat": int(target_seat),
                            "rep": int(rep),
                        }
                        k += 1
    return tuple(specs), meta


def annotate_mechanism_ablation_rows(rows: Sequence[Mapping[str, Any]], meta_by_game: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
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


def mechanism_ablation_summary_rows(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return target_summary_rows(
        rows,
        group_keys=(
            "arm_id",
            "starting_life",
            "ablation_axis",
            "target",
            "opponent",
            "target_deck",
            "opponent_deck",
            "target_jace_count",
            "target_counterspell_count",
            "target_force_count",
            "target_deck_size",
            "opponent_deck_size",
        ),
    )


def mechanism_ablation_mechanism_rows(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return mechanism_profile_rows(rows, group_keys=("arm_id", "starting_life", "ablation_axis", "target", "opponent"))


def compare_mechanism_ablation_by_life(summary_rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    by = {(str(r.get("arm_id", "")), to_int(r.get("starting_life"), 0)): r for r in summary_rows}
    life_values = sorted({life for (_arm, life) in by if life})
    out: list[dict[str, Any]] = []
    for life in life_values:
        anchor = by.get(("A_original_size_skew", life), {})
        nojace = by.get(("G_target_no_jace60", life), {})
        nocounter = by.get(("H_target_no_counterspell60", life), {})
        noboth = by.get(("I_target_no_jace_no_counterspell60", life), {})
        bufferonly = by.get(("J_target_all_island60", life), {})
        anchor_s = to_float(anchor.get("target_mean_score_draw_half"), 0.0)
        nojace_s = to_float(nojace.get("target_mean_score_draw_half"), 0.0)
        nocounter_s = to_float(nocounter.get("target_mean_score_draw_half"), 0.0)
        noboth_s = to_float(noboth.get("target_mean_score_draw_half"), 0.0)
        buffer_s = to_float(bufferonly.get("target_mean_score_draw_half"), 0.0)
        jace_drop = anchor_s - nojace_s
        counter_drop = anchor_s - nocounter_s
        both_drop = anchor_s - noboth_s
        buffer_drop = anchor_s - buffer_s
        if anchor_s >= 0.60 and buffer_s >= 0.60:
            read = "passive_library_buffer_alone_is_competitive"
        elif anchor_s >= 0.60 and nojace_s >= 0.60 and counter_drop >= 0.20:
            read = "jace_not_required_counterspell_density_matters"
        elif anchor_s >= 0.60 and jace_drop >= 0.20 and counter_drop >= 0.20:
            read = "both_jace_and_counterspell_matter"
        elif anchor_s >= 0.60 and jace_drop >= 0.20:
            read = "active_jace_machinery_matters"
        elif anchor_s >= 0.60 and counter_drop >= 0.20:
            read = "counterspell_density_matters"
        elif anchor_s >= 0.60 and nojace_s >= 0.55 and nocounter_s >= 0.55:
            read = "passive_library_buffer_may_dominate"
        else:
            read = "inconclusive_small_panel"
        out.append(
            {
                "starting_life": life,
                "anchor_score": anchor_s,
                "no_jace_score": nojace_s,
                "no_counterspell_score": nocounter_s,
                "no_jace_no_counterspell_score": noboth_s,
                "all_island_buffer_score": buffer_s,
                "anchor_minus_no_jace": jace_drop,
                "anchor_minus_no_counterspell": counter_drop,
                "anchor_minus_no_jace_no_counterspell": both_drop,
                "anchor_minus_all_island_buffer": buffer_drop,
                "anchor_library_out_win_share": to_float(anchor.get("library_out_win_share"), 0.0),
                "no_jace_library_out_win_share": to_float(nojace.get("library_out_win_share"), 0.0),
                "no_counterspell_library_out_win_share": to_float(nocounter.get("library_out_win_share"), 0.0),
                "no_jace_no_counterspell_library_out_win_share": to_float(noboth.get("library_out_win_share"), 0.0),
                "all_island_buffer_library_out_win_share": to_float(bufferonly.get("library_out_win_share"), 0.0),
                "provisional_read": read,
            }
        )
    return out


def compare_forensic_ablation_by_life(summary_rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Compare compact trajectory features for ablation arms at each life total."""

    by = {(str(r.get("arm_id", "")), to_int(r.get("starting_life"), 0)): r for r in summary_rows}
    life_values = sorted({life for (_arm, life) in by if life})
    arms = (
        ("G_target_no_jace60", "no_jace"),
        ("H_target_no_counterspell60", "no_counterspell"),
        ("I_target_no_jace_no_counterspell60", "no_jace_no_counterspell"),
        ("J_target_all_island60", "all_island_buffer"),
    )
    out: list[dict[str, Any]] = []
    for life in life_values:
        anchor = by.get(("A_original_size_skew", life), {})
        row: dict[str, Any] = {
            "starting_life": life,
            "anchor_score": to_float(anchor.get("mean_focus_target_score"), 0.0),
            "anchor_library_buffer": to_float(anchor.get("mean_target_library_buffer_final"), 0.0),
            "anchor_target_jace_zero": to_float(anchor.get("mean_target_activate_jace_zero"), 0.0),
            "anchor_target_counterspell": to_float(anchor.get("mean_target_cast_counterspell"), 0.0),
        }
        for arm_id, label in arms:
            arm = by.get((arm_id, life), {})
            score = to_float(arm.get("mean_focus_target_score"), 0.0)
            buffer = to_float(arm.get("mean_target_library_buffer_final"), 0.0)
            row[f"{label}_score"] = score
            row[f"{label}_library_buffer"] = buffer
            row[f"anchor_minus_{label}_score"] = row["anchor_score"] - score
            row[f"anchor_minus_{label}_library_buffer"] = row["anchor_library_buffer"] - buffer
            row[f"{label}_target_jace_zero"] = to_float(arm.get("mean_target_activate_jace_zero"), 0.0)
            row[f"{label}_target_counterspell"] = to_float(arm.get("mean_target_cast_counterspell"), 0.0)
        out.append(row)
    return out


def mechanism_ablation_gate_report(
    summary: Mapping[str, object],
    rows: Sequence[Mapping[str, object]],
    *,
    min_games: int = 180,
    required_arms: Sequence[str] = (
        "A_original_size_skew",
        "G_target_no_jace60",
        "H_target_no_counterspell60",
        "I_target_no_jace_no_counterspell60",
        "J_target_all_island60",
    ),
) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    if int(summary.get("games", 0)) < int(min_games):
        errors.append(f"fewer than {min_games} ablation games")
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
    present = {str(r.get("arm_id")) for r in rows}
    for arm in required_arms:
        if arm not in present:
            errors.append(f"required ablation arm missing: {arm}")
    return {"passed": not errors, "errors": errors, "warnings": warnings}
