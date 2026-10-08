#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable, Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))

from src.muc5.reduced_cfr import (
    BOTTOM_TOP,
    JACE_PLUS2,
    LEAVE_TOP,
    PITCH_ISLAND,
    PITCH_JACE,
    PITCH_NONE,
    ReducedMUCCFRGame,
    ReducedMUCState,
    TabularCFRSolver,
    TOP_BLANK,
    TOP_THREAT,
)

REVISION = "rev0093"
CHECKPOINTS = (1, 10, 50, 200, 1000, 5000)


def write_csv(path: Path, rows: Iterable[Mapping[str, object]]) -> None:
    material = [dict(row) for row in rows]
    fieldnames = sorted({key for row in material for key in row})
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in material:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def mechanism_projection_audit(game: ReducedMUCCFRGame) -> dict[str, object]:
    p0_threat = game.information_state_key(
        ReducedMUCState(TOP_THREAT, PITCH_NONE, opening=JACE_PLUS2),
        0,
    )
    p0_blank = game.information_state_key(
        ReducedMUCState(TOP_BLANK, PITCH_NONE, opening=JACE_PLUS2),
        0,
    )
    p1_bottom_threat = game.information_state_key(
        ReducedMUCState(TOP_THREAT, PITCH_NONE, opening=JACE_PLUS2, jace_order=BOTTOM_TOP),
        1,
    )
    p1_bottom_blank = game.information_state_key(
        ReducedMUCState(TOP_BLANK, PITCH_NONE, opening=JACE_PLUS2, jace_order=BOTTOM_TOP),
        1,
    )
    p1_leave_threat = game.information_state_key(
        ReducedMUCState(TOP_THREAT, PITCH_NONE, opening=JACE_PLUS2, jace_order=LEAVE_TOP),
        1,
    )
    p1_leave_blank = game.information_state_key(
        ReducedMUCState(TOP_BLANK, PITCH_NONE, opening=JACE_PLUS2, jace_order=LEAVE_TOP),
        1,
    )
    p1_force_island = game.information_state_key(
        ReducedMUCState(
            TOP_THREAT,
            PITCH_ISLAND,
            opening=JACE_PLUS2,
            jace_order=BOTTOM_TOP,
            pressure_action="cast_threat",
            control_response="force_pitch:Island",
        ),
        1,
    )
    p1_force_jace = game.information_state_key(
        ReducedMUCState(
            TOP_THREAT,
            PITCH_JACE,
            opening=JACE_PLUS2,
            jace_order=BOTTOM_TOP,
            pressure_action="cast_threat",
            control_response="force_pitch:Jace",
        ),
        1,
    )
    return {
        "p0_jace_infoset_distinguishes_seen_top": p0_threat != p0_blank,
        "p1_bottom_infoset_redacts_seen_top": p1_bottom_threat == p1_bottom_blank,
        "p1_leave_infoset_redacts_seen_top": p1_leave_threat == p1_leave_blank,
        "p1_force_infoset_reveals_pitch_identity": p1_force_island != p1_force_jace
        and "force_pitch:Island" in p1_force_island
        and "force_pitch:Jace" in p1_force_jace,
        "sample_keys": {
            "p0_jace_threat": p0_threat,
            "p0_jace_blank": p0_blank,
            "p1_bottom": p1_bottom_threat,
            "p1_leave": p1_leave_threat,
            "p1_force_island": p1_force_island,
            "p1_force_jace": p1_force_jace,
        },
    }


def main() -> None:
    data = ROOT / "data"
    game = ReducedMUCCFRGame()
    solver = TabularCFRSolver(game)
    metrics = solver.train(max(CHECKPOINTS), checkpoints=CHECKPOINTS)
    final = metrics[-1]
    strategy_rows = solver.strategy_rows()
    convergence_rows = [metric.as_dict() for metric in metrics]
    projection = mechanism_projection_audit(game)
    infoset_counts = Counter(str(row["player"]) for row in strategy_rows)
    leak_rows = [row for row in strategy_rows if bool(row.get("reveals_jace_top_to_pressure"))]
    force_visible_rows = [row for row in strategy_rows if bool(row.get("reveals_force_pitch_publicly"))]
    jace_private_rows = [row for row in strategy_rows if bool(row.get("contains_jace_private_top"))]

    summary = {
        "revision": REVISION,
        "schema": "muc5.reduced_cfr_summary.v1",
        "purpose": (
            "First tabular CFR calibration on an independently represented reduced game preserving "
            "Jace private known-top semantics, public leave/bottom events, Force pitch visibility, and closure."
        ),
        "game": {
            "name": "ReducedMUCCFRGame",
            "chance_deals": len(game.chance_deals()),
            "top_probs": dict(game.top_probs),
            "pitch_probs": dict(game.pitch_probs),
            "payoff_range": [-1.0, 1.0],
            "players": {"0": "control_jace_force", "1": "pressure"},
            "scope": "calibration subgame only; not a full MUC-5 solve",
        },
        "training": {
            "algorithm": "vanilla tabular CFR",
            "iterations": max(CHECKPOINTS),
            "checkpoints": list(CHECKPOINTS),
            "deterministic": True,
            "best_response": "imperfect-information best response grouped by information set; no concrete-state peeking",
        },
        "final_metrics": final.as_dict(),
        "first_metrics": metrics[0].as_dict(),
        "exploitability_reduction_factor": metrics[0].exploitability / final.exploitability,
        "infoset_counts_by_player": dict(sorted(infoset_counts.items())),
        "information_projection": projection,
        "qualitative_strategy_notes": {
            "root_force_island": solver.average_strategy().get("P0|public=root|private=force=Island", {}),
            "root_force_jace": solver.average_strategy().get("P0|public=root|private=force=Jace", {}),
            "root_no_force": solver.average_strategy().get("P0|public=root|private=force=none", {}),
        },
    }
    audit = {
        "revision": REVISION,
        "schema": "muc5.reduced_cfr_audit.v1",
        "passed": (
            len(game.chance_deals()) == 6
            and final.infosets == 33
            and final.exploitability < 1e-4
            and metrics[0].exploitability > final.exploitability * 1000.0
            and projection["p0_jace_infoset_distinguishes_seen_top"] is True
            and projection["p1_bottom_infoset_redacts_seen_top"] is True
            and projection["p1_leave_infoset_redacts_seen_top"] is True
            and projection["p1_force_infoset_reveals_pitch_identity"] is True
            and not leak_rows
            and bool(force_visible_rows)
            and bool(jace_private_rows)
        ),
        "checks": {
            "chance_deals": len(game.chance_deals()),
            "infosets": final.infosets,
            "final_exploitability": final.exploitability,
            "initial_exploitability": metrics[0].exploitability,
            "exploitability_reduction_factor": metrics[0].exploitability / final.exploitability,
            "projection": projection,
            "pressure_jace_top_leak_rows": len(leak_rows),
            "force_pitch_visible_strategy_rows": len(force_visible_rows),
            "jace_private_strategy_rows": len(jace_private_rows),
        },
        "artifact_files": {
            "summary": "data/rev0093_reduced_cfr_summary.json",
            "audit": "data/rev0093_reduced_cfr_audit.json",
            "convergence": "data/rev0093_reduced_cfr_convergence.csv",
            "strategy": "data/rev0093_reduced_cfr_strategy.csv",
        },
    }
    write_csv(data / "rev0093_reduced_cfr_convergence.csv", convergence_rows)
    write_csv(data / "rev0093_reduced_cfr_strategy.csv", strategy_rows)
    (data / "rev0093_reduced_cfr_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    (data / "rev0093_reduced_cfr_audit.json").write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"summary": summary, "audit": audit}, indent=2, sort_keys=True))
    if not audit["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
