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
from src.muc5.population_candidate_gate import build_candidate_gate
from src.muc5.population_counterprobe import REPAIR_COUNTER_AXIS

REV = "rev0087"
CODENAME = "mechanismgate-candidatefirewall"
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


def main() -> None:
    DATA.mkdir(exist_ok=True)
    deltas = read_csv(DATA / f"{INPUT_REV}_candidate_transfer_paired_deltas.csv")
    games = read_csv(DATA / f"{INPUT_REV}_candidate_transfer_games.csv")
    if len(deltas) != 240 or len(games) != 480:
        raise SystemExit("rev0087 requires the full rev0084 candidate-transfer paired-delta and game panels")

    gate, components, leaks = build_candidate_gate(
        deltas,
        games,
        alpha=ALPHA,
        primary_family_tests=PRIMARY_FAMILY_TESTS,
        baseline_axis=GUARDED_COUNTER_AXIS,
        candidate_axis=REPAIR_COUNTER_AXIS,
    )
    gate_row = gate.as_dict()
    component_statuses = {f"{row.get('label')}:{row.get('component')}": row.get("status") for row in components}
    hard_components = [row for row in components if row.get("hard_fail") is True]
    payload = {
        "revision": REV,
        "codename": CODENAME,
        "input_revision": INPUT_REV,
        "audit_focus": "enforceable mechanism-aware firewall for adaptive counter candidates",
        "baseline_axis": GUARDED_COUNTER_AXIS,
        "candidate_axis": REPAIR_COUNTER_AXIS,
        "alpha": ALPHA,
        "primary_family_tests": PRIMARY_FAMILY_TESTS,
        "candidate_gate": gate_row,
        "component_rows": len(components),
        "hard_component_rows": len(hard_components),
        "leak_audit_rows": len(leaks),
        "component_statuses": component_statuses,
        "candidate_rejected": gate.status.startswith("candidate_rejected"),
        "candidate_broad_pool_eligible": gate.broad_pool_eligible,
        "candidate_pool_eligible": gate.candidate_pool_eligible,
        "score_gate_passed": gate.score_gate_passed,
        "mechanism_gate_passed": gate.mechanism_gate_passed,
        "pool_leak_gate_passed": gate.pool_leak_gate_passed,
        "score_hard_fail_rows": gate.score_hard_fail_rows,
        "mechanism_hard_fail_rows": gate.mechanism_hard_fail_rows,
        "pool_leak_fail_rows": gate.pool_leak_fail_rows,
        "same_score_mechanism_flip_rows_across_primary_components": gate.same_score_mechanism_flip_rows,
        "read": (
            "The stabilizer is blocked by a reusable firewall, not only by prose: the transfer-panel paired-sign component hard-fails "
            "and the overall/selected-cell same-score mechanism-drift components hard-fail. The source game rows did not leak into broad or candidate pools."
        ),
    }

    write_union_csv(DATA / "rev0087_candidate_gate_rows.csv", [gate_row])
    write_union_csv(DATA / "rev0087_candidate_gate_component_rows.csv", components)
    write_union_csv(DATA / "rev0087_candidate_gate_leak_audit.csv", leaks)
    dump_json(DATA / "rev0087_candidate_gate_summary.json", payload)
    print(json.dumps(payload, indent=2, sort_keys=True))

    if gate.paired_delta_rows != 240 or gate.game_rows != 480:
        raise SystemExit("candidate gate did not read the complete rev0084 paired panel")
    if gate.score_hard_fail_rows != 1:
        raise SystemExit("transfer-panel exact sign failure should be the single score hard fail")
    if gate.mechanism_hard_fail_rows != 2:
        raise SystemExit("overall and selected-cell mechanism drift should be the two mechanism hard fails")
    if gate.pool_leak_fail_rows != 0 or not gate.pool_leak_gate_passed:
        raise SystemExit("adaptive candidate rows should be explicitly excluded, not leaked")
    if gate.candidate_pool_eligible or gate.broad_pool_eligible:
        raise SystemExit("stabilizer must not be eligible for candidate or broad pools")
    if gate.status != "candidate_rejected_score_and_mechanism_firewall":
        raise SystemExit(f"unexpected rev0087 gate status: {gate.status}")


if __name__ == "__main__":
    main()
