from __future__ import annotations

from dataclasses import asdict, dataclass
from math import floor
from typing import Any, Iterable, Mapping, Sequence

from .cpp_rollout import CppShadowGameSpec
from .deckspace import DeckVector
from .payoff import StrategyBundle, load_seed_decks
from .terminal_decomposition import CF34_AGENT, CF34_MULLIGAN, THREAT_AGENT, THREAT_MULLIGAN
from .terminal_mechanisms import annotate_target_mechanism, mechanism_profile_rows, target_summary_rows, to_float, to_int

_CARD_FIELDS = ("island", "counterspell", "force", "jace", "overlord")


@dataclass(frozen=True)
class LibraryBufferArm:
    arm_id: str
    question: str
    target: StrategyBundle
    opponent: StrategyBundle
    size_axis: str
    active_axis: str
    interpretation: str

    def as_dict(self) -> dict[str, Any]:
        out = asdict(self)
        out["target"] = self.target.as_dict()
        out["opponent"] = self.opponent.as_dict()
        return out


def _validate(deck: DeckVector) -> DeckVector:
    deck.validate()
    return deck


def all_island_deck(size: int) -> DeckVector:
    """Return the legally inert deck for a requested MUC-5 size."""

    return _validate(DeckVector(int(size), int(size), 0, 0, 0, 0))


def scale_deck_to_legal_size(deck: DeckVector, size: int, *, preserve_positive: bool = True) -> DeckVector:
    """Deterministically resize a 40/60-card seed deck while preserving card ratios.

    MUC-5 only permits 40 and 60 cards, so this is not a general deck-construction
    rule.  It is an experiment-control helper: it builds the closest legal-size
    analogue of a seed deck so a panel can compare active-card content against
    passive library-size advantage without silently changing both at once.

    The allocation uses largest remainders after proportional scaling.  When
    ``preserve_positive`` is true, every card present in the source deck stays
    present in the scaled deck if the target size has enough slots.  Ties are
    resolved in the stable MUC-5 card order, which makes outputs reproducible and
    easy to test.
    """

    target_size = int(size)
    if target_size == int(deck.size):
        deck.validate()
        return deck
    if target_size not in {40, 60}:
        raise ValueError(f"MUC-5 legal deck sizes are 40 and 60, got {target_size}")
    source_counts = {field: int(getattr(deck, field)) for field in _CARD_FIELDS}
    raw = {field: source_counts[field] * target_size / int(deck.size) for field in _CARD_FIELDS}
    counts = {field: int(floor(raw[field])) for field in _CARD_FIELDS}
    if preserve_positive:
        positive_fields = [field for field in _CARD_FIELDS if source_counts[field] > 0]
        if len(positive_fields) > target_size:
            raise ValueError("target deck too small to preserve every positive source card")
        for field in positive_fields:
            counts[field] = max(1, counts[field])

    total = sum(counts.values())
    if total < target_size:
        remainders = sorted(
            ((raw[field] - floor(raw[field]), -idx, field) for idx, field in enumerate(_CARD_FIELDS)),
            reverse=True,
        )
        i = 0
        while total < target_size:
            field = remainders[i % len(remainders)][2]
            counts[field] += 1
            total += 1
            i += 1
    elif total > target_size:
        # Remove excess from the smallest remainders first, never violating the
        # positive-card floor when preserve_positive is active.
        remainders = sorted((raw[field] - floor(raw[field]), idx, field) for idx, field in enumerate(_CARD_FIELDS))
        i = 0
        while total > target_size:
            field = remainders[i % len(remainders)][2]
            floor_min = 1 if preserve_positive and source_counts[field] > 0 else 0
            if counts[field] > floor_min:
                counts[field] -= 1
                total -= 1
            i += 1
            if i > 1000:  # pragma: no cover - impossible for two legal sizes, defensive only
                raise RuntimeError("failed to normalize scaled deck counts")

    return _validate(
        DeckVector(
            target_size,
            counts["island"],
            counts["counterspell"],
            counts["force"],
            counts["jace"],
            counts["overlord"],
        )
    )


def rev0062_library_buffer_arms(seed_decks_path) -> list[LibraryBufferArm]:
    """Legal-size controls for the passive-library-buffer hypothesis.

    rev0061 showed that a 60-Island target can be competitive against a 40-card
    Overlord shell.  The risky open question is whether this is a broad strategic
    result or a deck-size asymmetry artifact.  These arms compare inert and active
    targets at legal 40/60 sizes against both the original 40-card opponent and a
    size-normalized 60-card opponent.
    """

    decks = load_seed_decks(seed_decks_path)
    counter60 = decks["sixty_counterwall_jace"]
    overlord40 = decks["forty_overlord_impending"]
    counter40_scaled = scale_deck_to_legal_size(counter60, 40)
    overlord60_scaled = scale_deck_to_legal_size(overlord40, 60)
    buffer40 = all_island_deck(40)
    buffer60 = all_island_deck(60)

    def bundle(strategy_id: str, deck_name: str, deck: DeckVector, agent: str, mulligan: str) -> StrategyBundle:
        return StrategyBundle(strategy_id, deck_name, deck, agent, mulligan)

    threat40 = bundle("pub_threat_overlord40", "forty_overlord_impending", overlord40, THREAT_AGENT, THREAT_MULLIGAN)
    threat60 = bundle("pub_threat_overlord60_scaled", "sixty_overlord_scaled_from40", overlord60_scaled, THREAT_AGENT, THREAT_MULLIGAN)

    return [
        LibraryBufferArm(
            arm_id="A_counter60_vs_threat40",
            question="Anchor: original 60-card counter-wall shell into the original 40-card Overlord threat shell.",
            target=bundle("cf34_counter_wall60", "sixty_counterwall_jace", counter60, CF34_AGENT, CF34_MULLIGAN),
            opponent=threat40,
            size_axis="target60_opponent40",
            active_axis="active_counterwall_vs_active_threat",
            interpretation="If this remains strong, the panel matches the historical edge under fresh seeds.",
        ),
        LibraryBufferArm(
            arm_id="K_buffer40_vs_threat40",
            question="Inert 40-Island target against the original 40-card threat shell: no library-size edge, no active cards.",
            target=bundle("cf34_buffer_only_all_island40", "forty_all_island_buffer", buffer40, CF34_AGENT, CF34_MULLIGAN),
            opponent=threat40,
            size_axis="target40_opponent40",
            active_axis="passive_buffer_only_vs_active_threat",
            interpretation="This is the lower baseline for passive buffer claims.  If it also wins, the opponent shell self-decks even without a size skew.",
        ),
        LibraryBufferArm(
            arm_id="J_buffer60_vs_threat40",
            question="Inert 60-Island target against the original 40-card threat shell: isolate passive 60-vs-40 library buffer.",
            target=bundle("cf34_buffer_only_all_island60", "sixty_all_island_buffer", buffer60, CF34_AGENT, CF34_MULLIGAN),
            opponent=threat40,
            size_axis="target60_opponent40",
            active_axis="passive_buffer_only_vs_active_threat",
            interpretation="If this beats K, the size buffer itself is causal; if it beats A, active cards may be a liability in some seeds.",
        ),
        LibraryBufferArm(
            arm_id="L_buffer60_vs_threat60",
            question="Inert 60-Island target against a size-normalized 60-card threat shell: remove opponent self-deck asymmetry.",
            target=bundle("cf34_buffer_only_all_island60", "sixty_all_island_buffer", buffer60, CF34_AGENT, CF34_MULLIGAN),
            opponent=threat60,
            size_axis="target60_opponent60",
            active_axis="passive_buffer_only_vs_scaled_active_threat",
            interpretation="If J is strong and L collapses, the edge is specifically a 60-vs-40 exploit, not a durable 60-card strategy.",
        ),
        LibraryBufferArm(
            arm_id="M_counter40_vs_threat40",
            question="Size-normalized 40-card counter-wall analogue against the original 40-card threat shell.",
            target=bundle("cf34_counter_wall40_scaled", "forty_counterwall_scaled_from60", counter40_scaled, CF34_AGENT, CF34_MULLIGAN),
            opponent=threat40,
            size_axis="target40_opponent40",
            active_axis="active_counterwall_vs_active_threat",
            interpretation="This estimates active counter-wall value after removing the 60-card buffer.",
        ),
        LibraryBufferArm(
            arm_id="N_counter60_vs_threat60",
            question="Original 60-card counter-wall shell against a size-normalized 60-card threat shell.",
            target=bundle("cf34_counter_wall60", "sixty_counterwall_jace", counter60, CF34_AGENT, CF34_MULLIGAN),
            opponent=threat60,
            size_axis="target60_opponent60",
            active_axis="active_counterwall_vs_scaled_active_threat",
            interpretation="This estimates the active shell under equal 60-card library budgets.",
        ),
        LibraryBufferArm(
            arm_id="O_buffer40_vs_threat60",
            question="Inert 40-Island target against a size-normalized 60-card threat shell: negative control for size disadvantage.",
            target=bundle("cf34_buffer_only_all_island40", "forty_all_island_buffer", buffer40, CF34_AGENT, CF34_MULLIGAN),
            opponent=threat60,
            size_axis="target40_opponent60",
            active_axis="passive_buffer_only_vs_scaled_active_threat",
            interpretation="This should be bad for the target.  If not, the threat shell is globally self-destructive rather than only exploitable by size skew.",
        ),
    ]


def library_buffer_specs(
    arms: Sequence[LibraryBufferArm],
    *,
    simulator_revision: str,
    life_totals: Sequence[int] = (20, 40),
    reps: int = 5,
    base_seed: int = 6262000,
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
                            "size_axis": arm.size_axis,
                            "active_axis": arm.active_axis,
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
                            "rep": int(rep),
                        }
                        k += 1
    return tuple(specs), meta


def annotate_library_buffer_rows(rows: Sequence[Mapping[str, Any]], meta: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
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


def library_buffer_summary_rows(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return target_summary_rows(
        rows,
        group_keys=(
            "arm_id",
            "starting_life",
            "size_axis",
            "active_axis",
            "target_deck_size",
            "opponent_deck_size",
            "target",
            "opponent",
            "target_deck",
            "opponent_deck",
        ),
    )


def library_buffer_mechanism_rows(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return mechanism_profile_rows(rows, group_keys=("arm_id", "starting_life", "size_axis", "active_axis", "target", "opponent"))


def compare_library_buffer_by_life(summary_rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Compare the seven-arm legal-size panel into direct causal deltas."""

    by = {(str(r.get("arm_id", "")), to_int(r.get("starting_life"), 0)): r for r in summary_rows}
    life_values = sorted({life for (_arm, life) in by if life})
    out: list[dict[str, Any]] = []
    for life in life_values:
        def score(arm_id: str) -> float:
            return to_float(by.get((arm_id, life), {}).get("target_mean_score_draw_half"), 0.0)

        def library_share(arm_id: str) -> float:
            return to_float(by.get((arm_id, life), {}).get("library_out_win_share"), 0.0)

        a = score("A_counter60_vs_threat40")
        k = score("K_buffer40_vs_threat40")
        j = score("J_buffer60_vs_threat40")
        l = score("L_buffer60_vs_threat60")
        m = score("M_counter40_vs_threat40")
        n = score("N_counter60_vs_threat60")
        o = score("O_buffer40_vs_threat60")
        passive_size_delta = j - k
        opponent_size_normalization_drop = j - l
        active_value_at_40 = m - k
        active_value_equal_60 = n - l
        active_size_delta_vs_threat40 = a - m
        negative_control_gap = l - o
        if j >= 0.60 and k <= 0.45 and l <= 0.45:
            read = "strong_60v40_passive_size_exploit"
        elif j >= 0.55 and passive_size_delta >= 0.20 and opponent_size_normalization_drop >= 0.20:
            read = "probable_60v40_passive_size_exploit"
        elif active_value_at_40 >= 0.20 or active_value_equal_60 >= 0.20:
            read = "active_shell_has_independent_value"
        elif j >= 0.55 and l >= 0.55:
            read = "inert_buffer_competitive_even_equalized"
        else:
            read = "inconclusive_small_panel"
        out.append(
            {
                "starting_life": life,
                "counter60_vs_threat40_score": a,
                "buffer40_vs_threat40_score": k,
                "buffer60_vs_threat40_score": j,
                "buffer60_vs_threat60_score": l,
                "counter40_vs_threat40_score": m,
                "counter60_vs_threat60_score": n,
                "buffer40_vs_threat60_score": o,
                "passive_size_delta_buffer60_minus_buffer40_vs_threat40": passive_size_delta,
                "opponent_size_normalization_drop_buffer60_threat40_minus_threat60": opponent_size_normalization_drop,
                "active_counterwall_value_at_40_counter40_minus_buffer40": active_value_at_40,
                "active_counterwall_value_equal_60_counter60_minus_buffer60": active_value_equal_60,
                "active_size_delta_vs_threat40_counter60_minus_counter40": active_size_delta_vs_threat40,
                "negative_control_gap_buffer60_minus_buffer40_vs_threat60": negative_control_gap,
                "buffer60_vs_threat40_library_out_win_share": library_share("J_buffer60_vs_threat40"),
                "buffer60_vs_threat60_library_out_win_share": library_share("L_buffer60_vs_threat60"),
                "counter60_vs_threat40_library_out_win_share": library_share("A_counter60_vs_threat40"),
                "counter60_vs_threat60_library_out_win_share": library_share("N_counter60_vs_threat60"),
                "provisional_read": read,
            }
        )
    return out


def compare_forensic_library_buffer_by_life(summary_rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    by = {(str(r.get("arm_id", "")), to_int(r.get("starting_life"), 0)): r for r in summary_rows}
    life_values = sorted({life for (_arm, life) in by if life})
    arms = (
        ("K_buffer40_vs_threat40", "buffer40_threat40"),
        ("J_buffer60_vs_threat40", "buffer60_threat40"),
        ("L_buffer60_vs_threat60", "buffer60_threat60"),
        ("M_counter40_vs_threat40", "counter40_threat40"),
        ("N_counter60_vs_threat60", "counter60_threat60"),
        ("O_buffer40_vs_threat60", "buffer40_threat60"),
    )
    out: list[dict[str, Any]] = []
    for life in life_values:
        row: dict[str, Any] = {"starting_life": life}
        for arm_id, label in arms:
            arm = by.get((arm_id, life), {})
            row[f"{label}_score"] = to_float(arm.get("mean_focus_target_score"), 0.0)
            row[f"{label}_final_library_buffer"] = to_float(arm.get("mean_target_library_buffer_final"), 0.0)
            row[f"{label}_opponent_drawdown_minus_target"] = to_float(arm.get("mean_opponent_minus_target_library_drawdown"), 0.0)
            row[f"{label}_target_min_life"] = to_float(arm.get("mean_target_min_life"), 0.0)
            row[f"{label}_opponent_min_life"] = to_float(arm.get("mean_opponent_min_life"), 0.0)
            row[f"{label}_opponent_overlord_attacks"] = to_float(arm.get("mean_opponent_attack_to_player_total"), 0.0)
        row["passive_size_delta_final_library_buffer"] = row["buffer60_threat40_final_library_buffer"] - row["buffer40_threat40_final_library_buffer"]
        row["normalization_drop_final_library_buffer"] = row["buffer60_threat40_final_library_buffer"] - row["buffer60_threat60_final_library_buffer"]
        out.append(row)
    return out


def library_buffer_gate_report(
    summary: Mapping[str, object],
    rows: Sequence[Mapping[str, object]],
    *,
    min_games: int = 240,
    required_arms: Sequence[str] = (
        "A_counter60_vs_threat40",
        "K_buffer40_vs_threat40",
        "J_buffer60_vs_threat40",
        "L_buffer60_vs_threat60",
        "M_counter40_vs_threat40",
        "N_counter60_vs_threat60",
        "O_buffer40_vs_threat60",
    ),
) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    if int(summary.get("games", 0)) < int(min_games):
        errors.append(f"fewer than {min_games} buffer-sweep games")
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
            errors.append(f"required buffer arm missing: {arm}")
    return {"passed": not errors, "errors": errors, "warnings": warnings}
