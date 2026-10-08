#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.population_score_audit import MISMATCH_COLUMNS, audit_population_score_orientation_sources

DATA = ROOT / "data"
REV = "rev0076"
SOURCES = [
    DATA / "rev0069_population_frontier_games.csv",
    DATA / "rev0070_population_precision_games.csv",
    DATA / "rev0075_stratum_challenge_games.csv",
]


def read_csv(path: Path) -> list[dict[str, object]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = [dict(row) for row in csv.DictReader(handle)]
    revision = path.name.split("_")[0]
    for row in rows:
        row.setdefault("source_revision", row.get("simulator_revision") or revision)
        if not row.get("source_revision"):
            row["source_revision"] = revision
    return rows


def write_csv(path: Path, rows: list[Mapping[str, object]], *, fallback_fields: tuple[str, ...]) -> None:
    fields: list[str]
    if rows:
        seen: list[str] = []
        for row in rows:
            for key in row.keys():
                if key not in seen:
                    seen.append(str(key))
        fields = seen
    else:
        fields = list(fallback_fields)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fields})


def flatten_by_source(rows: list[Mapping[str, object]]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for row in rows:
        item = {
            "source_file": row.get("source_file", ""),
            "rows": row.get("rows", 0),
            "mismatches": row.get("mismatches", 0),
            "passed": row.get("passed", False),
            "target_seat_0_rows": row.get("target_seat_0_rows", 0),
            "target_seat_1_rows": row.get("target_seat_1_rows", 0),
            "source_revisions": json.dumps(row.get("source_revisions", {}), sort_keys=True),
            "expected_result_counts": json.dumps(row.get("expected_result_counts", {}), sort_keys=True),
            "expected_terminal_mechanism_counts": json.dumps(row.get("expected_terminal_mechanism_counts", {}), sort_keys=True),
            "terminal_clean_status_counts": json.dumps(row.get("terminal_clean_status_counts", {}), sort_keys=True),
        }
        out.append(item)
    return out


def main() -> None:
    source_rows = []
    missing = [path.as_posix() for path in SOURCES if not path.exists()]
    if missing:
        raise SystemExit(f"missing raw population game sources: {missing}")
    for path in SOURCES:
        source_rows.append((path.relative_to(ROOT).as_posix(), read_csv(path)))

    result = audit_population_score_orientation_sources(source_rows)
    mismatches = list(result["mismatches"])
    by_source = flatten_by_source(list(result["by_source"]))
    summary = dict(result["summary"])
    summary["audit_focus"] = "target score/result/terminal orientation recomputed from raw p0/p1 scores, target seats, winner, and loss_reason"
    summary["risk_closed"] = "seat-flipped target rows no longer rely on duplicated hand-written p0/p1 score selection"

    (DATA / f"{REV}_score_orientation_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(DATA / f"{REV}_score_orientation_by_source.csv", by_source, fallback_fields=("source_file", "rows", "mismatches", "passed"))
    write_csv(DATA / f"{REV}_score_orientation_mismatches.csv", mismatches, fallback_fields=MISMATCH_COLUMNS)
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not summary.get("passed"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
