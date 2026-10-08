from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping, Sequence

from .counter_response import COUNTER_GUARD_AGENT, GUARDED_COUNTER_AXIS
from .cpp_rollout import CppShadowGameSpec
from .deckspace import DeckVector
from .library_buffer_sweep import scale_deck_to_legal_size
from .payoff import StrategyBundle, load_seed_decks
from .terminal_decomposition import CF34_MULLIGAN, THREAT_MULLIGAN
from .terminal_mechanisms import target_summary_rows, to_float, to_int
from .threat_closure import THREAT_CLOSURE_AGENT
from .threat_response import (
    CLOSURE_THREAT_AXIS,
    PRESSURE_THREAT_AXIS,
    THREAT_PRESSURE_AGENT,
    ThreatResponseArm,
    annotate_threat_response_rows,
    threat_response_mechanism_rows,
    threat_response_specs,
    threat_response_stress_specs,
    threat_response_summary_rows,
)

THREAT_SURGE_AGENT = "threat_surge"
SURGE_THREAT_AXIS = "face_protect_threat_surge"

RESPONSE_THREAT_POLICIES: tuple[tuple[str, str, str], ...] = (
    (
        THREAT_CLOSURE_AGENT,
        CLOSURE_THREAT_AXIS,
        "Library-aware closure baseline repaired in rev0063/rev0064.",
    ),
    (
        THREAT_PRESSURE_AGENT,
        PRESSURE_THREAT_AXIS,
        "Jace-pressure response from rev0066.",
    ),
    (
        THREAT_SURGE_AGENT,
        SURGE_THREAT_AXIS,
        "Face/protection surge: spends stack interaction to protect threats and prioritizes safe player damage.",
    ),
)


def _bundle(strategy_id: str, deck_name: str, deck: DeckVector, agent: str, mulligan: str) -> StrategyBundle:
    return StrategyBundle(strategy_id, deck_name, deck, agent, mulligan)


def rev0067_response_matrix_arms(seed_decks_path) -> list[ThreatResponseArm]:
    """Build the next response matrix around the live ``counter_guard`` candidate.

    rev0066 tested one new threat response.  This helper makes the response cycle
    explicit: every size cell is evaluated against closure, pressure, and surge
    with the same counter deck/policy target.  The output intentionally reuses
    ``ThreatResponseArm`` so older threat-response runners and forensics remain
    compatible.
    """

    decks = load_seed_decks(seed_decks_path)
    counter60 = decks["sixty_counterwall_jace"]
    threat40 = decks["forty_overlord_impending"]
    counter40 = scale_deck_to_legal_size(counter60, 40)
    threat60 = scale_deck_to_legal_size(threat40, 60)

    def counter(size: int) -> StrategyBundle:
        deck = counter60 if size == 60 else counter40
        deck_name = "sixty_counterwall_jace" if size == 60 else "forty_counterwall_scaled_from60"
        return _bundle(f"guard_counter_wall{size}", deck_name, deck, COUNTER_GUARD_AGENT, CF34_MULLIGAN)

    def threat(size: int, policy: str) -> StrategyBundle:
        deck = threat40 if size == 40 else threat60
        deck_name = "forty_overlord_impending" if size == 40 else "sixty_overlord_scaled_from40"
        short = {
            THREAT_CLOSURE_AGENT: "closure",
            THREAT_PRESSURE_AGENT: "pressure",
            THREAT_SURGE_AGENT: "surge",
        }[policy]
        return _bundle(f"pub_threat{size}_{short}", deck_name, deck, policy, THREAT_MULLIGAN)

    plan = [
        ("A", 40, 40, "40-vs-40 legal-size response cell."),
        ("B", 60, 40, "60-vs-40 size-skew response cell."),
        ("C", 60, 60, "60-vs-60 normalized response cell."),
    ]
    arms: list[ThreatResponseArm] = []
    for prefix, counter_size, threat_size, question in plan:
        for policy, axis, interpretation in RESPONSE_THREAT_POLICIES:
            label = {
                THREAT_CLOSURE_AGENT: "closure",
                THREAT_PRESSURE_AGENT: "pressure",
                THREAT_SURGE_AGENT: "surge",
            }[policy]
            arms.append(
                ThreatResponseArm(
                    arm_id=f"{prefix}_{label}_counter{counter_size}_vs_threat{threat_size}",
                    question=question,
                    target=counter(counter_size),
                    opponent=threat(threat_size, policy),
                    counter_policy_axis=GUARDED_COUNTER_AXIS,
                    threat_policy_axis=axis,
                    size_axis=f"counter{counter_size}_vs_threat{threat_size}",
                    interpretation=interpretation,
                )
            )
    return arms


def response_matrix_specs(
    arms: Sequence[ThreatResponseArm],
    *,
    simulator_revision: str,
    life_totals: Sequence[int] = (20, 40),
    reps: int = 2,
    base_seed: int = 6767000,
    max_decisions: int = 900,
) -> tuple[tuple[CppShadowGameSpec, ...], dict[str, dict[str, Any]]]:
    return threat_response_specs(
        arms,
        simulator_revision=simulator_revision,
        life_totals=life_totals,
        reps=reps,
        base_seed=base_seed,
        max_decisions=max_decisions,
    )


def response_matrix_stress_specs(
    arms: Sequence[ThreatResponseArm],
    *,
    candidate_cells: Sequence[tuple[str, int]],
    simulator_revision: str,
    reps: int = 3,
    base_seed: int = 6767900,
    max_decisions: int = 900,
) -> tuple[tuple[CppShadowGameSpec, ...], dict[str, dict[str, Any]]]:
    return threat_response_stress_specs(
        arms,
        candidate_cells=candidate_cells,
        simulator_revision=simulator_revision,
        reps=reps,
        base_seed=base_seed,
        max_decisions=max_decisions,
    )


def compare_response_matrix_by_life(summary_rows: Iterable[Mapping[str, Any]]) -> list[dict[str, object]]:
    """Compare policy responses without converting absent evidence into a zero score.

    Before rev0068, a missing policy row was silently represented by ``{}`` and
    then coerced to score 0.0.  That could make an incomplete matrix look like a
    decisive refutation.  Incomplete cells now remain explicit and unclassified.
    """

    by: dict[tuple[str, str, int], Mapping[str, Any]] = {}
    for row in summary_rows:
        key = (
            str(row.get("size_axis", "")),
            str(row.get("threat_policy_axis", "")),
            to_int(row.get("starting_life"), 0),
        )
        by[key] = row
    cells = sorted({(axis, life) for (axis, _policy, life) in by if axis and life})
    required_axes = (CLOSURE_THREAT_AXIS, PRESSURE_THREAT_AXIS, SURGE_THREAT_AXIS)
    out: list[dict[str, object]] = []
    for axis, life in cells:
        rows_by_policy = {policy: by.get((axis, policy, life)) for policy in required_axes}
        missing = [policy for policy, row in rows_by_policy.items() if row is None]
        if missing:
            out.append(
                {
                    "size_axis": axis,
                    "starting_life": life,
                    "counter_score_vs_closure": None,
                    "counter_score_vs_pressure": None,
                    "counter_score_vs_surge": None,
                    "surge_minus_pressure_counter_score_delta": None,
                    "surge_minus_closure_counter_score_delta": None,
                    "best_threat_axis_for_this_cell": None,
                    "closure_target_library_out_wins": None,
                    "pressure_target_library_out_wins": None,
                    "surge_target_library_out_wins": None,
                    "closure_target_life_total_wins": None,
                    "pressure_target_life_total_wins": None,
                    "surge_target_life_total_wins": None,
                    "missing_threat_policy_axes": missing,
                    "provisional_read": "incomplete_matrix",
                }
            )
            continue

        closure = rows_by_policy[CLOSURE_THREAT_AXIS]
        pressure = rows_by_policy[PRESSURE_THREAT_AXIS]
        surge = rows_by_policy[SURGE_THREAT_AXIS]
        assert closure is not None and pressure is not None and surge is not None
        closure_score = to_float(closure.get("target_mean_score_draw_half"), 0.0)
        pressure_score = to_float(pressure.get("target_mean_score_draw_half"), 0.0)
        surge_score = to_float(surge.get("target_mean_score_draw_half"), 0.0)
        best_threat_axis = min(
            (
                (closure_score, CLOSURE_THREAT_AXIS),
                (pressure_score, PRESSURE_THREAT_AXIS),
                (surge_score, SURGE_THREAT_AXIS),
            ),
            key=lambda x: x[0],
        )[1]
        if surge_score <= 0.40:
            read = "threat_surge_refutes_counter_guard"
        elif surge_score <= 0.50 and surge_score <= pressure_score - 0.15:
            read = "threat_surge_materially_weakens_counter_guard"
        elif surge_score >= 0.60 and surge_score >= pressure_score - 0.10:
            read = "counter_guard_survives_surge"
        elif surge_score > pressure_score + 0.15:
            read = "threat_surge_backfires"
        else:
            read = "mixed_or_underpowered"
        out.append(
            {
                "size_axis": axis,
                "starting_life": life,
                "counter_score_vs_closure": closure_score,
                "counter_score_vs_pressure": pressure_score,
                "counter_score_vs_surge": surge_score,
                "surge_minus_pressure_counter_score_delta": surge_score - pressure_score,
                "surge_minus_closure_counter_score_delta": surge_score - closure_score,
                "best_threat_axis_for_this_cell": best_threat_axis,
                "closure_target_library_out_wins": to_int(closure.get("target_library_out_wins"), 0),
                "pressure_target_library_out_wins": to_int(pressure.get("target_library_out_wins"), 0),
                "surge_target_library_out_wins": to_int(surge.get("target_library_out_wins"), 0),
                "closure_target_life_total_wins": to_int(closure.get("target_life_total_wins"), 0),
                "pressure_target_life_total_wins": to_int(pressure.get("target_life_total_wins"), 0),
                "surge_target_life_total_wins": to_int(surge.get("target_life_total_wins"), 0),
                "missing_threat_policy_axes": [],
                "provisional_read": read,
            }
        )
    return out


def response_matrix_gate_report(
    summary: Mapping[str, object],
    rows: Sequence[Mapping[str, object]],
    ownership_rows: Sequence[Mapping[str, object]],
    *,
    min_games: int = 120,
) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    if int(summary.get("games", 0)) < int(min_games):
        errors.append(f"fewer than {min_games} response-matrix games")
    if int(summary.get("truncations", 0)) != 0:
        errors.append("terminal-clean gate failed: truncations present")
    if int(summary.get("python_errors", 0)) != 0:
        errors.append("python errors occurred during C++ shadow rollout")
    if int(summary.get("forensic_games", 0)) != int(summary.get("games", -1)):
        errors.append("forensic rerun did not cover every game")
    if int(summary.get("closure_feature_games", 0)) != int(summary.get("games", -1)):
        errors.append("closure feature rerun did not cover every game")
    if int(summary.get("counter_ownership_games", 0)) != int(summary.get("games", -1)):
        errors.append("counter ownership audit did not cover every game")
    cpp = summary.get("cpp_shadow_summary", {})
    if isinstance(cpp, Mapping):
        if int(cpp.get("mismatches", 0)) != 0:
            errors.append("C++ shadow mismatches present")
        if int(cpp.get("skipped_events", 0)) != 0:
            warnings.append("C++ shadow skipped events present")
    required_threat_axes = tuple(axis for _agent, axis, _description in RESPONSE_THREAT_POLICIES)
    required_size_axes = ("counter40_vs_threat40", "counter60_vs_threat40", "counter60_vs_threat60")
    required_lives = (20, 40)
    threat_axes = {str(r.get("threat_policy_axis")) for r in rows}
    for required in required_threat_axes:
        if required not in threat_axes:
            errors.append(f"required threat policy missing: {required}")
    size_axes = {str(r.get("size_axis")) for r in rows}
    for required in required_size_axes:
        if required not in size_axes:
            errors.append(f"required size axis missing: {required}")

    observed_cells = {
        (
            str(row.get("size_axis", "")),
            str(row.get("threat_policy_axis", "")),
            to_int(row.get("starting_life"), 0),
        )
        for row in rows
    }
    expected_cells = {
        (size_axis, threat_axis, life)
        for size_axis in required_size_axes
        for threat_axis in required_threat_axes
        for life in required_lives
    }
    missing_cells = sorted(expected_cells - observed_cells)
    if missing_cells:
        rendered = [f"{size}/{threat}/life{life}" for size, threat, life in missing_cells]
        errors.append(f"response matrix is incomplete; missing cells: {rendered}")

    own_spell_counters = sum(to_int(r.get("selected_own_spell_counters"), 0) for r in ownership_rows)
    if own_spell_counters != 0:
        errors.append(f"selected own-spell counters remain after target-ownership guard: {own_spell_counters}")
    return {
        "passed": not errors,
        "errors": errors,
        "warnings": warnings,
        "scope": "operational_integrity_only",
        "expected_matrix_cells": len(expected_cells),
        "observed_matrix_cells": len(expected_cells & observed_cells),
    }


__all__ = [
    "THREAT_SURGE_AGENT",
    "SURGE_THREAT_AXIS",
    "RESPONSE_THREAT_POLICIES",
    "rev0067_response_matrix_arms",
    "response_matrix_specs",
    "response_matrix_stress_specs",
    "compare_response_matrix_by_life",
    "response_matrix_gate_report",
    "annotate_threat_response_rows",
    "threat_response_summary_rows",
    "threat_response_mechanism_rows",
]
