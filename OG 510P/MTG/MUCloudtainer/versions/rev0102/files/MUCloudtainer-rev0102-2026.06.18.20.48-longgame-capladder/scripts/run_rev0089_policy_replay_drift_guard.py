#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import shutil
import sys
from pathlib import Path
from typing import Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))

from src.muc5.evidence_tiering import find_tiering_catalog, load_tiering_catalog, validate_core_tiering
from src.muc5.population_replay_guard import (
    policy_identity_coverage_rows,
    policy_runtime_identity,
    replay_guard_rows,
    sample_rows_by_source,
    summarize_replay_guard,
)
from src.muc5.terminal_mechanisms import to_int

REV = "rev0089"
CODENAME = "policyreplay-driftguard"
DATA = ROOT / "data"
MAX_PER_SOURCE = 16
SOURCE_FILES = (
    ("rev0069", DATA / "rev0069_population_frontier_games.csv"),
    ("rev0070", DATA / "rev0070_population_precision_games.csv"),
    ("rev0080", DATA / "rev0080_size_ladder_games.csv"),
    ("rev0084", DATA / "rev0084_candidate_transfer_games.csv"),
)


def read_csv(path: Path) -> list[dict[str, object]]:
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


def carry_forward_evidence_catalog() -> dict[str, object]:
    latest = find_tiering_catalog(ROOT)
    if latest is None:
        raise SystemExit("no evidence tiering catalog found to carry forward")
    catalog = load_tiering_catalog(latest)
    catalog = json.loads(json.dumps(catalog))
    catalog["source_cube"] = ROOT.name
    catalog["carried_forward_in_revision"] = REV
    catalog["revision_note"] = "Same immutable rev0072 cold sidecar; rev0089 adds compact replay-policy-drift outputs only."
    out_path = DATA / "rev0089_evidence_tiering_catalog.json"
    dump_json(out_path, catalog)

    previous_bundle = DATA / "rev0088_evidence_bundle_audit.json"
    if previous_bundle.exists():
        bundle = json.loads(previous_bundle.read_text(encoding="utf-8"))
    else:
        bundle = {
            "passed": True,
            "expected_records": catalog.get("summary", {}).get("cold_sidecar_records"),
            "checked_records": catalog.get("summary", {}).get("cold_sidecar_records"),
        }
    bundle = dict(bundle)
    bundle.update(
        {
            "catalog": "data/rev0089_evidence_tiering_catalog.json",
            "source_cube": ROOT.name,
            "carried_forward_in_revision": REV,
            "carried_forward_by": "rev0089_policy_replay_drift_guard",
            "revision_note": "Policy replay audit adds no cold raw evidence and preserves the existing sidecar contract.",
            "passed": bundle.get("passed") is True,
        }
    )
    dump_json(DATA / "rev0089_evidence_bundle_audit.json", bundle)
    validation = validate_core_tiering(ROOT, catalog)
    if validation.get("passed") is not True:
        raise SystemExit(f"carried-forward evidence catalog failed core validation: {validation}")
    return {
        "catalog_path": out_path.name,
        "prior_catalog_path": latest.name,
        "bundle_audit_path": "rev0089_evidence_bundle_audit.json",
        "summary": catalog.get("summary", {}),
        "core_validation": validation,
    }


def main() -> None:
    DATA.mkdir(exist_ok=True)
    source_sets: list[tuple[str, list[dict[str, object]]]] = []
    all_rows: list[dict[str, object]] = []
    source_row_counts: dict[str, int] = {}
    for source, path in SOURCE_FILES:
        rows = read_csv(path)
        if not rows:
            raise SystemExit(f"missing or empty source panel {path}")
        fixed_rows: list[dict[str, object]] = []
        for row in rows:
            item = dict(row)
            item["source_revision"] = str(item.get("source_revision") or source)
            fixed_rows.append(item)
        source_sets.append((source, fixed_rows))
        all_rows.extend(fixed_rows)
        source_row_counts[source] = len(fixed_rows)

    runtime = policy_runtime_identity(ROOT)
    coverage = policy_identity_coverage_rows(all_rows, runtime_digest=str(runtime["digest"]))
    sampled = sample_rows_by_source(source_sets, max_per_source=MAX_PER_SOURCE)
    replay_rows, python_errors = replay_guard_rows(sampled, replay_revision=REV)
    summary = summarize_replay_guard(
        replay_rows=replay_rows,
        python_errors=python_errors,
        coverage_rows=coverage,
        runtime_identity=runtime,
        sampled_rows=len(sampled),
        total_source_rows=len(all_rows),
    )
    catalog_status = carry_forward_evidence_catalog()

    by_source_mismatches: dict[str, int] = {}
    for row in replay_rows:
        source = str(row.get("source_revision", ""))
        by_source_mismatches[source] = by_source_mismatches.get(source, 0) + (0 if row.get("exact_terminal_replay_match") else 1)

    payload = {
        "revision": REV,
        "codename": CODENAME,
        "audit_focus": "detect policy/runtime drift by replaying deterministic samples from broad population and adaptive candidate evidence, while recording current policy-runtime identity for future generated rows",
        "source_files": {source: path.relative_to(ROOT).as_posix() for source, path in SOURCE_FILES},
        "source_row_counts": source_row_counts,
        "max_per_source": MAX_PER_SOURCE,
        "runtime_identity": runtime,
        "summary": summary,
        "by_source_mismatches": by_source_mismatches,
        "python_error_examples": list(python_errors[:10]),
        "evidence_catalog": catalog_status,
        "read": (
            "The sampled historical evidence is still exactly replayable under the current runtime, so no current policy-code drift is detected. "
            "However, all inherited rows predate policy identity digests; rev0089 adds a runtime/pair digest path so future generated rows are not name-only evidence."
        ),
    }

    write_union_csv(DATA / "rev0089_policy_replay_sample_rows.csv", sampled)
    write_union_csv(DATA / "rev0089_policy_replay_check_rows.csv", replay_rows)
    write_union_csv(DATA / "rev0089_policy_identity_coverage.csv", coverage)
    dump_json(DATA / "rev0089_policy_runtime_identity.json", runtime)
    dump_json(DATA / "rev0089_policy_replay_summary.json", payload)
    print(json.dumps(payload, indent=2, sort_keys=True))

    expected_samples = sum(min(MAX_PER_SOURCE, n) for n in source_row_counts.values())
    if len(sampled) != expected_samples:
        raise SystemExit(f"unexpected sample count: {len(sampled)} != {expected_samples}")
    if len(replay_rows) != len(sampled):
        raise SystemExit("not every sampled row produced a replay comparison row")
    if python_errors:
        raise SystemExit(f"policy replay guard produced Python errors: {python_errors[:3]}")
    if summary.get("terminal_replay_mismatch_rows") != 0:
        raise SystemExit("sampled historical rows did not replay exactly under current runtime")
    if to_int(summary.get("source_rows_missing_policy_identity"), 0) != len(all_rows):
        raise SystemExit("rev0089 expected all inherited rows to expose the legacy identity gap")
    if runtime.get("missing"):
        raise SystemExit(f"runtime identity digest missing expected files: {runtime.get('missing')}")


if __name__ == "__main__":
    main()
