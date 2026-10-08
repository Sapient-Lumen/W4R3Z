#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.population_frontier import (
    COUNTER_POPULATION,
    population_column_rescue_rows,
    summarize_population_column_rescue,
)
from src.muc5.terminal_mechanisms import to_float

REV = "rev0082"
CODENAME = "rescueenvelope-countersetaudit"
DATA = ROOT / "data"
ROW_POLICIES = tuple(axis for axis, _agent, _note in COUNTER_POPULATION)
SOURCE_FRONTIER = DATA / "rev0081_opponent_frontier_familywise.csv"
THRESHOLD = 0.50


def read_csv(path: Path) -> list[dict[str, object]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def write_union_csv(path: Path, rows: Sequence[Mapping[str, object]], fallback_fields: Sequence[str] = ()) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row.keys():
            key_s = str(key)
            if key_s not in seen:
                seen.add(key_s)
                fieldnames.append(key_s)
    if not fieldnames:
        fieldnames = list(fallback_fields)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def dump_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def layer_rows(rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    summary = summarize_population_column_rescue(rows)
    layer_counts = summary["hierarchy_layer_rescue_status_counts"]
    out: list[dict[str, object]] = []
    for layer in ("global", "by_life", "by_size", "by_size_life"):
        subset = [row for row in rows if row.get("hierarchy_layer") == layer]
        sub = summarize_population_column_rescue(subset)
        out.append(
            {
                "hierarchy_layer": layer,
                "rows": sub["rows"],
                "rescue_status_counts": json.dumps(layer_counts.get(layer, {}), sort_keys=True),
                "existing_counter_certified_rows": sub["existing_counter_certified_rows"],
                "ucb_rescue_possible_rows": sub["ucb_rescue_possible_rows"],
                "mandatory_current_counter_set_deficient_rows": sub["mandatory_current_counter_set_deficient_rows"],
                "mandatory_certification_limited_rows": sub["mandatory_certification_limited_rows"],
                "mandatory_mean_below_rescuable_rows": sub["mandatory_mean_below_rescuable_rows"],
                "min_ucb_gap_to_threshold": sub["min_ucb_gap_to_threshold"],
                "max_ucb_gap_to_threshold": sub["max_ucb_gap_to_threshold"],
            }
        )
    return out


def main() -> None:
    DATA.mkdir(exist_ok=True)
    frontier = read_csv(SOURCE_FRONTIER)
    rescue = population_column_rescue_rows(
        frontier,
        row_policies=ROW_POLICIES,
        conservative_floor_threshold=THRESHOLD,
    )
    summary = summarize_population_column_rescue(rescue)
    layers = layer_rows(rescue)

    mandatory = [row for row in rescue if str(row.get("hierarchy_layer_mandatory", "")).lower() in {"true", "1"}]
    global_rows = [row for row in rescue if row.get("hierarchy_layer") == "global"]
    deficient_rows = [row for row in rescue if row.get("rescue_status") == "current_counter_set_deficient_even_by_upper_bound"]
    certification_limited = [row for row in rescue if row.get("rescue_status") == "certification_limited_existing_counter_candidate"]
    mean_below_rescuable = [row for row in rescue if row.get("rescue_status") == "mean_below_threshold_but_upper_bound_allows_rescue"]

    payload = {
        "revision": REV,
        "codename": CODENAME,
        "audit_focus": "distinguish existing-counter certification gaps from current counter-set deficiency after rev0081 found no credible threat-column answers",
        "source_frontier_rows": len(frontier),
        "rescue_rows": len(rescue),
        "global_rows": len(global_rows),
        "mandatory_rows": len(mandatory),
        "summary": summary,
        "rescue_status_counts": summary["rescue_status_counts"],
        "existing_counter_certified_rows": summary["existing_counter_certified_rows"],
        "ucb_rescue_possible_rows": summary["ucb_rescue_possible_rows"],
        "current_counter_set_deficient_rows": len(deficient_rows),
        "certification_limited_rows": len(certification_limited),
        "mean_below_threshold_but_upper_bound_allows_rescue_rows": len(mean_below_rescuable),
        "mandatory_current_counter_set_deficient_rows": summary["mandatory_current_counter_set_deficient_rows"],
        "mandatory_certification_limited_rows": summary["mandatory_certification_limited_rows"],
        "mandatory_mean_below_rescuable_rows": summary["mandatory_mean_below_rescuable_rows"],
        "global_rescue_status_counts": summarize_population_column_rescue(global_rows)["rescue_status_counts"],
        "weakest_ucb_case": {
            "threat_policy_axis": summary["weakest_ucb_threat_policy_axis"],
            "hierarchy_layer": summary["weakest_ucb_hierarchy_layer"],
            "size_axis": summary["weakest_ucb_size_axis"] or "",
            "starting_life": summary["weakest_ucb_starting_life"] or "",
            "best_policy": summary["weakest_ucb_best_policy"],
            "ucb_gap_to_threshold": summary["min_ucb_gap_to_threshold"],
        },
        "read": (
            "counter_set_expansion_required_for_at_least_one_fine_cell; broad_global_failures_are_still_certification_or_mean_below_uncertain_not_definitively_impossible"
            if len(deficient_rows) else "current_counter_set_not_ruled_out_by_upper_bounds"
        ),
    }

    write_union_csv(DATA / "rev0082_counterset_rescue_envelope.csv", rescue)
    write_union_csv(DATA / "rev0082_counterset_rescue_layer_summary.csv", layers)
    dump_json(DATA / "rev0082_counterset_rescue_summary.json", payload)
    print(json.dumps(payload, indent=2, sort_keys=True))

    if payload["source_frontier_rows"] != 36 or payload["rescue_rows"] != 36:
        raise SystemExit("rescue audit must account for all 36 rev0081 frontier rows")
    if payload["existing_counter_certified_rows"] != 0:
        raise SystemExit("rescue audit unexpectedly certified an existing counter answer")
    if payload["current_counter_set_deficient_rows"] < 1:
        raise SystemExit("rescue audit should identify at least one current counter-set-deficient cell")
    if payload["mandatory_current_counter_set_deficient_rows"] != 0:
        raise SystemExit("mandatory broad layers should not be declared impossible by upper bound yet")
    if payload["global_rescue_status_counts"].get("certification_limited_existing_counter_candidate") != 2:
        raise SystemExit("global rescue split changed: expected two certification-limited threat columns")
    if payload["global_rescue_status_counts"].get("mean_below_threshold_but_upper_bound_allows_rescue") != 1:
        raise SystemExit("global rescue split changed: expected one mean-below but upper-bound-rescuable threat column")
    gap = to_float(payload["weakest_ucb_case"].get("ucb_gap_to_threshold"), 0.0)
    if gap >= 0.0:
        raise SystemExit("weakest upper-bound case should be below threshold")


if __name__ == "__main__":
    main()
