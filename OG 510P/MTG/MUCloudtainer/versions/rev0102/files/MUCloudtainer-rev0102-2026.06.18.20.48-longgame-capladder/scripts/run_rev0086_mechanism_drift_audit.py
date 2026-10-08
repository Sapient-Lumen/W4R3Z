#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))

from src.muc5.counter_response import GUARDED_COUNTER_AXIS
from src.muc5.population_counterprobe import REPAIR_COUNTER_AXIS
from src.muc5.population_pair_forensics import (
    grouped_mechanism_drift_rows,
    mechanism_drift_summary,
    same_score_mechanism_flip_rows,
)

REV = "rev0086"
CODENAME = "mechanismdrift-tiecontract"
DATA = ROOT / "data"
INPUT_REV = "rev0084"
ALPHA = 0.05
PRIMARY_FAMILY_TESTS = 3


def read_csv(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def write_union_csv(path: Path, rows: Sequence[Mapping[str, object]], *, fallback_fields: Sequence[str] = ()) -> None:
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


def _primary_rows(deltas: Sequence[Mapping[str, object]]) -> dict[str, list[Mapping[str, object]]]:
    return {
        "overall": list(deltas),
        "selected_cell_holdout": [row for row in deltas if row.get("sampling_design") == "selected_cell_seed_disjoint_holdout"],
        "transfer_panel": [row for row in deltas if row.get("sampling_design") == "adaptive_candidate_transfer_seedpaired"],
    }


def main() -> None:
    DATA.mkdir(exist_ok=True)
    deltas = read_csv(DATA / f"{INPUT_REV}_candidate_transfer_paired_deltas.csv")
    if not deltas:
        raise SystemExit("rev0086 requires rev0084 paired-delta inputs")

    primary: list[dict[str, object]] = []
    for label, rows in _primary_rows(deltas).items():
        drift = mechanism_drift_summary(rows, label=label, alpha=ALPHA, family_tests=PRIMARY_FAMILY_TESTS).as_dict()
        drift["test_family"] = "primary_same_score_mechanism_drift"
        primary.append(drift)

    context_axes_sets = (
        ("sampling_design",),
        ("size_axis",),
        ("threat_policy_axis",),
        ("starting_life",),
        ("sampling_design", "size_axis"),
        ("sampling_design", "threat_policy_axis"),
        ("sampling_design", "starting_life"),
        ("sampling_design", "size_axis", "starting_life", "threat_policy_axis"),
    )
    exploratory_tests = 0
    for axes in context_axes_sets:
        exploratory_tests += len(grouped_mechanism_drift_rows(deltas, group_axes=axes, alpha=ALPHA, family_tests=1))
    context_rows: list[dict[str, object]] = []
    for axes in context_axes_sets:
        context_rows.extend(grouped_mechanism_drift_rows(deltas, group_axes=axes, alpha=ALPHA, family_tests=max(1, exploratory_tests)))

    flip_rows = same_score_mechanism_flip_rows(deltas)
    overall = next(row for row in primary if row["label"] == "overall")
    holdout = next(row for row in primary if row["label"] == "selected_cell_holdout")
    transfer = next(row for row in primary if row["label"] == "transfer_panel")
    supported = [row for row in primary if row.get("candidate_library_shift_familywise_supported") is True]
    reverse_supported = [row for row in primary if row.get("candidate_life_shift_familywise_supported") is True]

    status = (
        "candidate_quarantined_score_tie_library_out_drift"
        if supported
        else "candidate_quarantined_without_familywise_mechanism_drift"
    )

    payload = {
        "revision": REV,
        "codename": CODENAME,
        "input_revision": INPUT_REV,
        "audit_focus": "mechanism-aware tie contract for rev0084 guard/candidate transfer evidence",
        "baseline_axis": GUARDED_COUNTER_AXIS,
        "candidate_axis": REPAIR_COUNTER_AXIS,
        "alpha": ALPHA,
        "primary_family_tests": PRIMARY_FAMILY_TESTS,
        "primary_adjusted_alpha": ALPHA / PRIMARY_FAMILY_TESTS,
        "paired_delta_rows": len(deltas),
        "primary_mechanism_drift": primary,
        "exploratory_context_mechanism_drift_rows": len(context_rows),
        "same_score_mechanism_flip_rows": len(flip_rows),
        "overall_same_score_pairs": overall["same_score_pairs"],
        "overall_score_and_mechanism_equivalent_pairs": overall["score_and_mechanism_equivalent_pairs"],
        "overall_same_score_mechanism_flip_pairs": overall["same_score_mechanism_flip_pairs"],
        "overall_life_to_library_flips": overall["life_to_library_flips"],
        "overall_library_to_life_flips": overall["library_to_life_flips"],
        "overall_one_sided_p_candidate_library_shift": overall["one_sided_p_candidate_library_shift"],
        "overall_candidate_library_shift_familywise_supported": overall["candidate_library_shift_familywise_supported"],
        "holdout_candidate_library_shift_familywise_supported": holdout["candidate_library_shift_familywise_supported"],
        "transfer_candidate_library_shift_familywise_supported": transfer["candidate_library_shift_familywise_supported"],
        "candidate_library_shift_supported_primary_rows": len(supported),
        "candidate_life_shift_supported_primary_rows": len(reverse_supported),
        "candidate_broad_pool_eligible": False,
        "candidate_pool_eligible": False,
        "status": status,
        "read": (
            "The stabilizer remains quarantined. Among score ties, it is not behaviorally equivalent to the guard: "
            "18 same-score pairs flip terminal mechanism, with 16 shifts from life-total termination under the guard to library-out termination under the candidate. "
            "The overall and selected-cell primary rows support this library-out drift after family correction, so future candidate gates must distinguish score-only ties from score+mechanism equivalence."
        ),
    }

    write_union_csv(DATA / "rev0086_primary_mechanism_drift.csv", primary)
    write_union_csv(DATA / "rev0086_context_mechanism_drift.csv", context_rows)
    write_union_csv(DATA / "rev0086_same_score_mechanism_flips.csv", flip_rows)
    dump_json(DATA / "rev0086_mechanism_drift_summary.json", payload)
    print(json.dumps(payload, indent=2, sort_keys=True))

    if int(payload["paired_delta_rows"]) != 240:
        raise SystemExit("rev0086 expected the full rev0084 paired-delta panel")
    if int(payload["same_score_mechanism_flip_rows"]) != 18:
        raise SystemExit("rev0086 should explain all 18 rev0085 same-score mechanism flips")
    if int(payload["overall_score_and_mechanism_equivalent_pairs"]) >= int(payload["overall_same_score_pairs"]):
        raise SystemExit("score ties were falsely treated as full mechanism equivalence")
    if not bool(payload["overall_candidate_library_shift_familywise_supported"]):
        raise SystemExit("overall mechanism-drift direction should remain familywise supported")
    if bool(payload["transfer_candidate_library_shift_familywise_supported"]):
        raise SystemExit("transfer-panel mechanism drift should remain score-negative but not mechanism-drift significant")
    if bool(payload["candidate_broad_pool_eligible"]) or bool(payload["candidate_pool_eligible"]):
        raise SystemExit("adaptive stabilizer cannot enter broad/candidate pools")


if __name__ == "__main__":
    main()
