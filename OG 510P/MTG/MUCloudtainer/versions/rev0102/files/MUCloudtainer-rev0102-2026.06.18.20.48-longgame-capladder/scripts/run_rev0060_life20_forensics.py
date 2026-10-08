#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.cpp_rollout import CppShadowGameSpec
from src.muc5.payoff import load_seed_decks, write_csv
from src.muc5.terminal_decomposition import proportional_counterwall_40, proportional_overlord_60
from src.muc5.trajectory_forensics import (
    metric_deltas_by_arm,
    summarize_forensic_rows,
    trajectory_forensics_from_spec,
    validate_forensics_against_game_row,
)

REV = "rev0060"
CODENAME = "life20-trajectory-forensics"
DATA = ROOT / "data"
MAX_DECISIONS = 900
ARM_IDS = {"A_original_size_skew", "B_pilot_swap_size_skew"}
SOURCES = (
    ("rev0058_decomposition", DATA / "rev0058_decomposition_games.csv"),
    ("rev0059_seed_disjoint", DATA / "rev0059_seed_disjoint_games.csv"),
    ("rev0059_life20_pilotstress", DATA / "rev0059_life20_pilotstress_games.csv"),
)


def dump_json(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return [dict(row) for row in csv.DictReader(f)]


def wanted_rows() -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for source_tag, path in SOURCES:
        for idx, row in enumerate(read_csv_dicts(path)):
            if str(row.get("arm_id")) not in ARM_IDS:
                continue
            if int(float(row.get("starting_life", 0) or 0)) != 20:
                continue
            enriched = dict(row)
            enriched["source_run"] = source_tag
            enriched["source_row_index"] = str(idx)
            out.append(enriched)
    return out


def deck_map() -> dict[str, Any]:
    decks = load_seed_decks(DATA / "seed_decks.json")
    decks["counterwall_jace_proportional40"] = proportional_counterwall_40()
    decks["overlord_impending_proportional60"] = proportional_overlord_60()
    return decks


def spec_from_row(row: Mapping[str, Any], decks: Mapping[str, Any]) -> CppShadowGameSpec:
    game_id = f"{row.get('source_run')}__{row.get('cpp_shadow_game_id', row.get('source_row_index'))}"
    return CppShadowGameSpec(
        game_id=str(game_id),
        strategy0=str(row["strategy0"]),
        strategy1=str(row["strategy1"]),
        deck0_name=str(row["deck0"]),
        deck1_name=str(row["deck1"]),
        deck0=decks[str(row["deck0"])],
        deck1=decks[str(row["deck1"])],
        agent0=str(row["agent0"]),
        agent1=str(row["agent1"]),
        mulligan0=str(row["mulligan0"]),
        mulligan1=str(row["mulligan1"]),
        seed=int(float(row["seed"])),
        starting_player=int(float(row["starting_player"])),
        starting_life=int(float(row["starting_life"])),
        max_decisions=int(float(row.get("terminal_clean_max_decisions", MAX_DECISIONS) or MAX_DECISIONS)),
        simulator_revision=REV,
    )


def slim_case(row: Mapping[str, Any]) -> dict[str, object]:
    keys = [
        "source_run",
        "seed",
        "arm_id",
        "target_seat",
        "focus_target_score",
        "focus_terminal_mechanism",
        "focus_terminal_loser_role",
        "loss_reason",
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
        "target_attack_to_player_total",
        "opponent_attack_to_player_total",
        "target_cast_counterspell",
        "opponent_cast_counterspell",
        "target_cast_force_pitch",
        "opponent_cast_force_pitch",
        "target_discard_choices",
        "opponent_discard_choices",
    ]
    return {k: row.get(k, "") for k in keys}


def main() -> None:
    source_rows = wanted_rows()
    decks = deck_map()
    forensic_rows: list[dict[str, object]] = []
    validation_errors: list[dict[str, object]] = []
    stored_decision_exact_count = 0
    stored_decision_legacy_plus_one_count = 0
    for row in source_rows:
        spec = spec_from_row(row, decks)
        target_seat = int(float(row.get("target_seat", 0) or 0))
        forensic = trajectory_forensics_from_spec(spec, target_seat=target_seat)
        for key in (
            "source_run",
            "source_row_index",
            "arm_id",
            "target",
            "opponent",
            "target_deck",
            "opponent_deck",
            "target_agent",
            "opponent_agent",
            "target_mulligan",
            "opponent_mulligan",
            "target_deck_size",
            "opponent_deck_size",
            "target_seat",
            "rep",
        ):
            forensic[key] = row.get(key, "")
        stored_decisions = int(float(row.get("decisions", 0) or 0))
        applied_decisions = int(forensic.get("applied_decisions", forensic.get("decisions", 0)) or 0)
        if stored_decisions == applied_decisions:
            stored_decision_exact_count += 1
        if stored_decisions == applied_decisions + 1:
            stored_decision_legacy_plus_one_count += 1
        errors = validate_forensics_against_game_row(forensic, row)
        if errors:
            validation_errors.append(
                {
                    "source_run": row.get("source_run"),
                    "source_row_index": row.get("source_row_index"),
                    "source_game_id": row.get("cpp_shadow_game_id"),
                    "forensic_game_id": forensic.get("cpp_shadow_game_id"),
                    "errors": errors,
                }
            )
        forensic_rows.append(forensic)

    arm_summary = summarize_forensic_rows(forensic_rows, group_keys=("arm_id",))
    arm_result_summary = summarize_forensic_rows(forensic_rows, group_keys=("arm_id", "focus_target_result", "focus_terminal_mechanism", "focus_terminal_loser_role"))
    source_arm_summary = summarize_forensic_rows(forensic_rows, group_keys=("source_run", "arm_id"))
    deltas = metric_deltas_by_arm(arm_summary)
    b_wins = [r for r in forensic_rows if r.get("arm_id") == "B_pilot_swap_size_skew" and float(r.get("focus_target_score", 0.5)) > 0.5]
    b_losses = [r for r in forensic_rows if r.get("arm_id") == "B_pilot_swap_size_skew" and float(r.get("focus_target_score", 0.5)) < 0.5]
    a_losses = [r for r in forensic_rows if r.get("arm_id") == "A_original_size_skew" and float(r.get("focus_target_score", 0.5)) < 0.5]
    surprise_cases = [slim_case(r) for r in sorted(b_wins, key=lambda r: (str(r.get("focus_terminal_mechanism")), int(r.get("decisions", 0))))[:24]]
    failure_cases = [slim_case(r) for r in sorted(a_losses + b_losses, key=lambda r: (str(r.get("arm_id")), int(r.get("decisions", 0))))[:36]]

    write_csv(DATA / "rev0060_life20_forensics_games.csv", forensic_rows)
    write_csv(DATA / "rev0060_life20_forensics_arm_summary.csv", arm_summary)
    write_csv(DATA / "rev0060_life20_forensics_arm_result_summary.csv", arm_result_summary)
    write_csv(DATA / "rev0060_life20_forensics_source_arm_summary.csv", source_arm_summary)
    write_csv(DATA / "rev0060_life20_forensics_ab_metric_deltas.csv", deltas)
    write_csv(DATA / "rev0060_life20_forensics_pilotswap_win_cases.csv", surprise_cases)
    write_csv(DATA / "rev0060_life20_forensics_failure_cases.csv", failure_cases)

    summary = {
        "revision": REV,
        "codename": CODENAME,
        "purpose": "Transition-level forensic rerun of cumulative life-20 A/B games to explain whether wins follow library buffer, Jace/Brainstorm, countering, or Overlord pressure.",
        "source_files": [str(path.relative_to(ROOT)) for _tag, path in SOURCES],
        "source_rows_considered": len(source_rows),
        "forensic_games": len(forensic_rows),
        "validation_error_count": len(validation_errors),
        "decision_count_audit": {
            "stored_decision_exact_count": stored_decision_exact_count,
            "stored_decision_legacy_plus_one_count": stored_decision_legacy_plus_one_count,
            "note": "Historical terminal rollout rows overcounted applied decisions by one; rev0060 forensics reports corrected applied_decisions and a legacy-compatible field for artifact reproduction.",
        },
        "validation_errors": validation_errors[:10],
        "arm_summary": arm_summary,
        "arm_result_summary": arm_result_summary,
        "source_arm_summary": source_arm_summary,
        "ab_metric_deltas": deltas,
        "pilotswap_target_wins": len(b_wins),
        "pilotswap_target_losses": len(b_losses),
        "original_target_losses": len(a_losses),
        "gate": {
            "passed": len(validation_errors) == 0 and len(forensic_rows) >= 160,
            "errors": ([] if len(validation_errors) == 0 else ["forensic rerun did not reproduce stored terminal row(s)"]) + ([] if len(forensic_rows) >= 160 else ["too few cumulative life-20 A/B games"]),
        },
        "interpretation": [
            "This is not a new promotion gate; it is an explanation/diagnostic gate on the cumulative life-20 A/B contradiction.",
            "The run deliberately ships compact feature rows, not full transition traces.",
        ],
    }
    dump_json(DATA / "rev0060_life20_forensics_summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
