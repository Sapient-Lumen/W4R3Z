#!/usr/bin/env python3
"""Generate decomposable C++ test slices for local/CI parallel execution.

This planner does not run tests. It reads the C++ binary's case metadata,
combines it with SQLite duration history when available, discovers data-driven
scenario files, and emits rule/tag/scenario buckets plus an explicit work-unit
inventory. The point is to make future test parallelization explicit: rule-sliced
jobs, tag-sliced jobs, scenario jobs, fuzz seed jobs, and duration-greedy shards
can all be planned from the same metadata.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
import time
from collections import defaultdict
from typing import Any

os.environ.setdefault("TZ", "America/New_York")
if hasattr(time, "tzset"):
    time.tzset()

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "harness"
SCENARIO_DIR = ROOT / "tests" / "scenarios"


def rel(path: pathlib.Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def compact_history_record(record: dict[str, Any]) -> dict[str, Any]:
    """Keep matrix trend history compact while full reports stay addressable.

    rev0181: appending the entire matrix plan to JSONL made a five-run history
    larger than 2.5 MB because each line duplicated every case, rule bucket,
    scenario, command, and work unit. The latest full report remains available
    at the requested --report path; history should only preserve trend data and
    the compact hot-slice names needed for drift review.
    """
    summary = record.get("summary", {}) if isinstance(record.get("summary"), dict) else {}
    config = record.get("config", {}) if isinstance(record.get("config"), dict) else {}
    return {
        "schema": "mtgsim.test_matrix_plan_history.compact.v1",
        "source_schema": record.get("schema"),
        "created_at_local": record.get("created_at_local"),
        "status": record.get("status"),
        "duration_sec": record.get("duration_sec"),
        "config": {
            "mode": config.get("mode"),
            "executable": config.get("executable"),
        },
        "summary": {
            "cases": summary.get("cases"),
            "scenarios": summary.get("scenarios"),
            "rules": summary.get("rules"),
            "tags": summary.get("tags"),
            "work_units": summary.get("work_units"),
            "target_shards": summary.get("target_shards"),
            "suggested_local_shards": summary.get("suggested_local_shards"),
            "estimated_total_sec": summary.get("estimated_total_sec"),
            "historical_duration_samples": summary.get("historical_duration_samples"),
            "fuzz_seed_units": summary.get("fuzz_seed_units"),
            "fuzz_steps_per_seed": summary.get("fuzz_steps_per_seed"),
        },
        "hot_rules": [row.get("rule") for row in record.get("by_rule", [])[:10]],
        "hot_tags": [row.get("tag") for row in record.get("by_tag", [])[:10]],
    }


def append_jsonl(path: pathlib.Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(compact_history_record(record), sort_keys=True) + "\n")


def resolve_executable(mode: str, explicit: pathlib.Path | None) -> pathlib.Path:
    if explicit is not None:
        return explicit if explicit.is_absolute() else ROOT / explicit
    return ROOT / "build" / f"gcc-{mode}" / "mtgsim_tests"


def discover_cases(exe: pathlib.Path) -> list[dict[str, Any]]:
    proc = subprocess.run([str(exe), "--list-json"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout)[-2000:])
    raw = json.loads(proc.stdout)
    cases: list[dict[str, Any]] = []
    for item in raw:
        cases.append({
            "name": str(item.get("name", "")),
            "tags": sorted(str(v) for v in item.get("tags", [])),
            "rules": sorted(str(v) for v in item.get("rules", [])),
        })
    cases.sort(key=lambda case: case["name"])
    return cases


def discover_scenarios() -> list[dict[str, Any]]:
    scenarios = []
    for path in sorted(SCENARIO_DIR.glob("*.mtgscn")):
        scenarios.append({"name": path.stem, "path": rel(path)})
    return scenarios


def duration_estimates() -> dict[str, float]:
    try:
        sys.path.insert(0, str(ROOT / "tools"))
        import metrics_db  # type: ignore
        return metrics_db.case_duration_estimates()
    except Exception:
        return {}


def parse_positive_env_int(name: str, default: int) -> int:
    raw = os.environ.get(name, str(default))
    try:
        return max(1, int(raw))
    except ValueError:
        return default


def auto_parallelism_cap(mode: str) -> int:
    cap = parse_positive_env_int("MTGSIM_AUTO_JOBS", 8)
    if mode == "sanitize":
        cap = min(cap, parse_positive_env_int("MTGSIM_SANITIZE_AUTO_JOBS", 8))
    return cap


def suggested_parallel_shards(mode: str, total_units: int) -> int:
    if total_units <= 0:
        return 1
    return max(1, min(os.cpu_count() or 1, auto_parallelism_cap(mode), total_units))


def bucketize(cases: list[dict[str, Any]], estimates: dict[str, float], key: str) -> list[dict[str, Any]]:
    buckets: dict[str, list[str]] = defaultdict(list)
    for case in cases:
        for value in case[key]:
            buckets[value].append(case["name"])
    out: list[dict[str, Any]] = []
    for value, names in buckets.items():
        estimated = sum(max(estimates.get(name, 0.001), 0.001) for name in names)
        out.append({
            key[:-1]: value,
            "cases": len(names),
            "estimated_sec": round(estimated, 6),
            "case_names": sorted(names),
        })
    out.sort(key=lambda row: (-row["estimated_sec"], row.get(key[:-1], "")))
    return out


def command_for(mode: str, *, rule: str | None = None, tag: str | None = None, shards: int | None = None) -> list[str]:
    cmd = [sys.executable, "tools/run_cpp_tests.py", "--mode", mode, "--jobs", "auto", "--json"]
    if rule is not None:
        cmd.extend(["--rule", rule])
    if tag is not None:
        cmd.extend(["--tag", tag])
    if shards is not None and shards > 1:
        cmd.extend(["--shard-count", str(shards), "--shard-strategy", "duration-greedy"])
    return cmd


def scenario_command_for(mode: str, *, name_filter: str | None = None, shards: int | None = None) -> list[str]:
    cmd = [sys.executable, "tools/run_scenarios.py", "--mode", mode, "--jobs", "auto", "--json"]
    if name_filter:
        cmd.extend(["--filter", name_filter])
    if shards is not None and shards > 1:
        cmd.extend(["--shard-count", str(shards)])
    return cmd


def make_work_units(
    mode: str,
    cases: list[dict[str, Any]],
    scenarios: list[dict[str, Any]],
    case_estimates: dict[str, float],
    *,
    fuzz_seed_base: int,
    fuzz_seeds: int,
    fuzz_steps: int,
) -> list[dict[str, Any]]:
    units: list[dict[str, Any]] = []
    for case in cases:
        name = case["name"]
        units.append({
            "id": f"cpp::{name}",
            "kind": "cpp_case",
            "name": name,
            "tags": case["tags"],
            "rules": case["rules"],
            "estimated_sec": round(case_estimates.get(name, 0.001), 6),
            "resource_class": "cpu.small",
            "command": [sys.executable, "tools/run_cpp_tests.py", "--mode", mode, "--jobs", "1", "--case", name],
        })
    for scenario in scenarios:
        units.append({
            "id": f"scenario::{scenario['name']}",
            "kind": "scenario",
            "name": scenario["name"],
            "path": scenario["path"],
            "tags": ["scenario"],
            "rules": [],
            "estimated_sec": 0.005,
            "resource_class": "cpu.small",
            "command": [sys.executable, "tools/run_scenarios.py", "--mode", mode, "--jobs", "1", "--filter", scenario["name"]],
        })
    for offset in range(fuzz_seeds):
        seed = fuzz_seed_base + offset
        units.append({
            "id": f"fuzz::{seed}",
            "kind": "fuzz_seed",
            "name": f"fuzz_seed_{seed}",
            "seed": seed,
            "steps": fuzz_steps,
            "tags": ["fuzz", "invariants"],
            "rules": [],
            "estimated_sec": round(max(0.002, fuzz_steps * 0.00005), 6),
            "resource_class": "cpu.medium",
            "command": [sys.executable, "tools/run_fuzz.py", "--mode", mode, "--jobs", "1", "--seed-base", str(seed), "--seeds", "1", "--steps", str(fuzz_steps)],
        })
    units.sort(key=lambda row: (row["kind"], row["name"]))
    return units


def greedy_bins(work_units: list[dict[str, Any]], shard_count: int) -> list[dict[str, Any]]:
    shard_count = max(1, shard_count)
    bins: list[dict[str, Any]] = [
        {"shard_index": idx, "estimated_sec": 0.0, "units": [], "counts_by_kind": defaultdict(int)}
        for idx in range(shard_count)
    ]
    for unit in sorted(work_units, key=lambda row: (-float(row.get("estimated_sec", 0.0)), row["id"])):
        target = min(bins, key=lambda row: (row["estimated_sec"], row["shard_index"]))
        target["units"].append(unit["id"])
        target["estimated_sec"] += float(unit.get("estimated_sec", 0.0))
        target["counts_by_kind"][unit["kind"]] += 1
    for row in bins:
        row["estimated_sec"] = round(row["estimated_sec"], 6)
        row["unit_count"] = len(row["units"])
        row["counts_by_kind"] = dict(sorted(row["counts_by_kind"].items()))
    return bins


def plan(mode: str, exe: pathlib.Path, *, fuzz_seed_base: int, fuzz_seeds: int, fuzz_steps: int, target_shards: int | None) -> dict[str, Any]:
    started = time.perf_counter()
    cases = discover_cases(exe)
    scenarios = discover_scenarios()
    estimates = duration_estimates()
    case_estimates = {case["name"]: max(estimates.get(case["name"], 0.001), 0.001) for case in cases}
    total_estimated = sum(case_estimates.values())
    suggested_shards = suggested_parallel_shards(mode, len(cases))
    scenario_suggested_shards = suggested_parallel_shards(mode, len(scenarios))
    target_shards = max(1, target_shards or suggested_shards)
    work_units = make_work_units(
        mode,
        cases,
        scenarios,
        case_estimates,
        fuzz_seed_base=fuzz_seed_base,
        fuzz_seeds=fuzz_seeds,
        fuzz_steps=fuzz_steps,
    )
    duration_bins = greedy_bins(work_units, target_shards)
    total_estimated = sum(float(unit.get("estimated_sec", 0.0)) for unit in work_units)
    by_rule = bucketize(cases, estimates, "rules")
    by_tag = bucketize(cases, estimates, "tags")
    hot_rules = by_rule[:10]
    hot_tags = by_tag[:10]

    return {
        "schema": "mtgsim.test_matrix_plan.v2",
        "created_at_local": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "duration_sec": time.perf_counter() - started,
        "status": "passed",
        "config": {"mode": mode, "executable": rel(exe)},
        "summary": {
            "cases": len(cases),
            "scenarios": len(scenarios),
            "rules": len(by_rule),
            "tags": len(by_tag),
            "estimated_total_sec": round(total_estimated, 6),
            "historical_duration_samples": len(estimates),
            "suggested_local_shards": suggested_shards,
            "target_shards": target_shards,
            "work_units": len(work_units),
            "fuzz_seed_units": fuzz_seeds,
            "fuzz_steps_per_seed": fuzz_steps,
        },
        "work_units": work_units,
        "duration_greedy_bins": duration_bins,
        "cases": cases,
        "scenarios": scenarios,
        "by_rule": by_rule,
        "by_tag": by_tag,
        "commands": {
            "all_cases": command_for(mode),
            "duration_greedy_shards": command_for(mode, shards=suggested_shards),
            "all_scenarios": scenario_command_for(mode),
            "scenario_shards": scenario_command_for(mode, shards=scenario_suggested_shards),
            "scenario_slices": {row["name"]: scenario_command_for(mode, name_filter=row["name"]) for row in scenarios[:10]},
            "hot_rule_slices": {row["rule"]: command_for(mode, rule=row["rule"]) for row in hot_rules},
            "hot_tag_slices": {row["tag"]: command_for(mode, tag=row["tag"]) for row in hot_tags},
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["debug", "release", "sanitize", "profile"], default="release")
    parser.add_argument("--exe", type=pathlib.Path, default=None)
    parser.add_argument("--report", type=pathlib.Path, default=REPORT_DIR / "test_matrix_plan_latest.json")
    parser.add_argument("--fuzz-seed-base", type=int, default=7000)
    parser.add_argument("--fuzz-seeds", type=int, default=12)
    parser.add_argument("--fuzz-steps", type=int, default=120)
    parser.add_argument("--target-shards", type=int, default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    exe = resolve_executable(args.mode, args.exe)
    if not exe.exists():
        raise SystemExit(f"test executable not found: {rel(exe)}; build tests first")
    if args.fuzz_seeds <= 0:
        raise SystemExit("--fuzz-seeds must be positive")
    if args.fuzz_steps <= 0:
        raise SystemExit("--fuzz-steps must be positive")
    if args.target_shards is not None and args.target_shards <= 0:
        raise SystemExit("--target-shards must be positive")
    report = plan(
        args.mode,
        exe,
        fuzz_seed_base=args.fuzz_seed_base,
        fuzz_seeds=args.fuzz_seeds,
        fuzz_steps=args.fuzz_steps,
        target_shards=args.target_shards,
    )
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    append_jsonl(args.report.parent / "test_matrix_plan_history.jsonl", report)
    if args.json:
        print(json.dumps(report, sort_keys=True))
    else:
        summary = report["summary"]
        print(
            "test matrix: "
            f"cases={summary['cases']} scenarios={summary['scenarios']} work_units={summary['work_units']} "
            f"rules={summary['rules']} tags={summary['tags']} "
            f"target_shards={summary['target_shards']} suggested_shards={summary['suggested_local_shards']} "
            f"report={rel(args.report)}"
        )
        print("hot rule slices: " + ", ".join(row["rule"] for row in report["by_rule"][:8]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
