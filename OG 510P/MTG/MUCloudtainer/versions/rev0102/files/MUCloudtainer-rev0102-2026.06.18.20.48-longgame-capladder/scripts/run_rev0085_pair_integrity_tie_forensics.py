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
    grouped_sign_summary_rows,
    grouped_tie_mechanism_rows,
    paired_sign_summary,
    pair_integrity_rows,
    summarize_pair_integrity,
    tie_mechanism_summary,
)

REV = "rev0085"
CODENAME = "pairintegrity-tieforensics"
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
    games = read_csv(DATA / f"{INPUT_REV}_candidate_transfer_games.csv")
    deltas = read_csv(DATA / f"{INPUT_REV}_candidate_transfer_paired_deltas.csv")
    if not games or not deltas:
        raise SystemExit("rev0085 requires rev0084 candidate-transfer game and paired-delta inputs")

    integrity_rows = pair_integrity_rows(games, baseline_axis=GUARDED_COUNTER_AXIS, candidate_axis=REPAIR_COUNTER_AXIS)
    integrity_summary = summarize_pair_integrity(integrity_rows)

    primary: list[dict[str, object]] = []
    primary_ties: list[dict[str, object]] = []
    for label, rows in _primary_rows(deltas).items():
        sign = paired_sign_summary(rows, label=label, alpha=ALPHA, family_tests=PRIMARY_FAMILY_TESTS).as_dict()
        sign["test_family"] = "primary_candidate_transfer_panels"
        primary.append(sign)
        ties = tie_mechanism_summary(rows, label=label).as_dict()
        ties["test_family"] = "primary_candidate_transfer_panels"
        primary_ties.append(ties)

    context_sign_rows: list[dict[str, object]] = []
    context_tie_rows: list[dict[str, object]] = []
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
        # Count groups first so the exploratory Bonferroni column has a real denominator.
        grouped = grouped_sign_summary_rows(deltas, group_axes=axes, alpha=ALPHA, family_tests=1)
        exploratory_tests += len(grouped)
    for axes in context_axes_sets:
        context_sign_rows.extend(grouped_sign_summary_rows(deltas, group_axes=axes, alpha=ALPHA, family_tests=max(1, exploratory_tests)))
        context_tie_rows.extend(grouped_tie_mechanism_rows(deltas, group_axes=axes))

    overall = next(row for row in primary if row["label"] == "overall")
    holdout = next(row for row in primary if row["label"] == "selected_cell_holdout")
    transfer = next(row for row in primary if row["label"] == "transfer_panel")
    overall_ties = next(row for row in primary_ties if row["label"] == "overall")

    familywise_supported_primary = [row for row in primary if row.get("negative_transfer_familywise_supported") is True]
    candidate_dominance_primary = [row for row in primary if row.get("candidate_dominance_familywise_supported") is True]
    status = (
        "candidate_quarantined_transfer_panel_exact_sign_negative_transfer"
        if transfer.get("negative_transfer_familywise_supported") is True
        else "candidate_quarantined_no_dominance_but_negative_transfer_not_familywise_confirmed"
    )

    payload = {
        "revision": REV,
        "codename": CODENAME,
        "input_revision": INPUT_REV,
        "audit_focus": "paired exposure integrity, exact sign-test calibration, and tie-mechanism forensics for the rev0084 adaptive stabilizer transfer audit",
        "baseline_axis": GUARDED_COUNTER_AXIS,
        "candidate_axis": REPAIR_COUNTER_AXIS,
        "alpha": ALPHA,
        "primary_family_tests": PRIMARY_FAMILY_TESTS,
        "primary_adjusted_alpha": ALPHA / PRIMARY_FAMILY_TESTS,
        "games": len(games),
        "paired_delta_rows": len(deltas),
        "pair_integrity": integrity_summary.as_dict(),
        "primary_sign_tests": primary,
        "primary_tie_forensics": primary_ties,
        "exploratory_context_sign_tests": len(context_sign_rows),
        "exploratory_context_tie_forensics": len(context_tie_rows),
        "overall_one_sided_p_candidate_worse": overall["one_sided_p_candidate_worse"],
        "holdout_one_sided_p_candidate_worse": holdout["one_sided_p_candidate_worse"],
        "transfer_one_sided_p_candidate_worse": transfer["one_sided_p_candidate_worse"],
        "overall_familywise_negative_supported": overall["negative_transfer_familywise_supported"],
        "holdout_familywise_negative_supported": holdout["negative_transfer_familywise_supported"],
        "transfer_familywise_negative_supported": transfer["negative_transfer_familywise_supported"],
        "candidate_dominance_supported_primary_rows": len(candidate_dominance_primary),
        "negative_transfer_supported_primary_rows": len(familywise_supported_primary),
        "overall_same_score_pairs": overall_ties["same_score_pairs"],
        "overall_same_score_mechanism_flip_pairs": overall_ties["same_score_mechanism_flip_pairs"],
        "overall_mechanism_flip_share_of_ties": overall_ties["mechanism_flip_share_of_ties"],
        "tie_equivalence_warning": overall_ties["tie_equivalence_warning"],
        "candidate_broad_pool_eligible": False,
        "candidate_pool_eligible": False,
        "status": status,
        "read": (
            "rev0084's broad quarantine remains correct, but rev0085 narrows the reason: the selected-cell holdout has a negative point estimate without familywise exact-sign support, "
            "while the broader transfer panel has exact paired sign-test support for guard superiority. Same-score pairs are not all mechanistically identical."
        ),
    }

    write_union_csv(DATA / "rev0085_pair_integrity_rows.csv", integrity_rows)
    write_union_csv(DATA / "rev0085_primary_sign_tests.csv", primary)
    write_union_csv(DATA / "rev0085_context_sign_tests.csv", context_sign_rows)
    write_union_csv(DATA / "rev0085_tie_mechanism_forensics.csv", primary_ties + context_tie_rows)
    dump_json(DATA / "rev0085_pair_integrity_summary.json", payload)
    print(json.dumps(payload, indent=2, sort_keys=True))

    if not integrity_summary.passed:
        raise SystemExit("paired exposure integrity failed")
    if int(payload["games"]) != 480 or int(payload["paired_delta_rows"]) != 240:
        raise SystemExit("rev0085 expected the full rev0084 paired transfer panel")
    if bool(payload["candidate_dominance_supported_primary_rows"]):
        raise SystemExit("candidate unexpectedly dominates a primary paired sign test")
    if transfer.get("negative_transfer_familywise_supported") is not True:
        raise SystemExit("transfer panel no longer supports negative transfer by exact paired sign test")
    if holdout.get("negative_transfer_familywise_supported") is True:
        raise SystemExit("holdout should remain a point-negative but not familywise-confirmed result")
    if int(payload["overall_same_score_mechanism_flip_pairs"]) <= 0:
        raise SystemExit("tie forensics should expose non-identical same-score mechanisms")


if __name__ == "__main__":
    main()
