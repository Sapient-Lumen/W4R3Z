#!/usr/bin/env python3
"""Parallel scenario-file runner for MTGSim.

Scenario tests are intentionally data files rather than C++ test functions. The
C++ mtgsim_scenario executable owns the engine API calls; this Python runner
owns discovery, filtering, sharding, parallel subprocess execution, timeouts,
JSON/JUnit reporting, and SQLite metrics.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import pathlib
import random
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from typing import Any

os.environ.setdefault("TZ", "America/New_York")
if hasattr(time, "tzset"):
    time.tzset()

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "harness"
SCENARIO_DIR = ROOT / "tests" / "scenarios"


@dataclass(frozen=True)
class ScenarioCase:
    name: str
    path: pathlib.Path


@dataclass
class ScenarioResult:
    name: str
    path: str
    status: str
    duration_sec: float
    assertions: int
    lines: int
    command: list[str]
    returncode: int | None = None
    stdout_tail: str = ""
    stderr_tail: str = ""
    message: str = ""


class BudgetExceeded(RuntimeError):
    pass


def rel(path: pathlib.Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def tail(text: str, limit: int = 4000) -> str:
    return text[-limit:] if len(text) > limit else text


def append_jsonl(path: pathlib.Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def resolve_executable(mode: str, explicit: pathlib.Path | None) -> pathlib.Path:
    if explicit is not None:
        return explicit if explicit.is_absolute() else ROOT / explicit
    return ROOT / "build" / f"gcc-{mode}" / "mtgsim_scenario"


def discover_scenarios(scenario_dir: pathlib.Path = SCENARIO_DIR) -> list[ScenarioCase]:
    cases = [ScenarioCase(name=path.stem, path=path) for path in sorted(scenario_dir.glob("*.mtgscn"))]
    return cases


def parse_binary_report(stdout: str) -> dict[str, Any]:
    for line in reversed(stdout.splitlines()):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                return {}
    return {}


def run_scenario(exe: pathlib.Path, case: ScenarioCase, timeout_sec: float | None) -> ScenarioResult:
    cmd = [str(exe), "--scenario", str(case.path), "--json"]
    begin = time.perf_counter()
    try:
        proc = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout_sec)
        duration = time.perf_counter() - begin
        parsed = parse_binary_report(proc.stdout)
        return ScenarioResult(
            name=case.name,
            path=rel(case.path),
            status="passed" if proc.returncode == 0 else "failed",
            duration_sec=float(parsed.get("duration_sec") or duration),
            assertions=int(parsed.get("assertions") or 0),
            lines=int(parsed.get("lines") or 0),
            command=cmd,
            returncode=proc.returncode,
            stdout_tail=tail(proc.stdout),
            stderr_tail=tail(proc.stderr),
            message=str(parsed.get("message") or ""),
        )
    except subprocess.TimeoutExpired as exc:
        duration = time.perf_counter() - begin
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        return ScenarioResult(
            name=case.name,
            path=rel(case.path),
            status="timeout",
            duration_sec=duration,
            assertions=0,
            lines=0,
            command=cmd,
            returncode=124,
            stdout_tail=tail(stdout),
            stderr_tail=tail(stderr),
            message=f"scenario timed out after {timeout_sec:.3f}s" if timeout_sec is not None else "scenario timed out",
        )


def stable_hash_mod(value: str, modulus: int) -> int:
    digest = hashlib.sha256(value.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % modulus


def assign_shards(cases: list[ScenarioCase], shard_count: int, shard_index: int) -> list[ScenarioCase]:
    if shard_count <= 0:
        raise ValueError("shard_count must be positive")
    if shard_index < 0 or shard_index >= shard_count:
        raise ValueError("shard_index must be in [0, shard_count)")
    return [case for case in cases if stable_hash_mod(case.name, shard_count) == shard_index]


def check_budget(started: float, budget_sec: float | None) -> None:
    if budget_sec is not None and time.perf_counter() - started > budget_sec:
        raise BudgetExceeded(f"scenario budget exhausted after {time.perf_counter() - started:.3f}s")


def budget_poll_timeout(started: float, budget_sec: float | None, *, poll_sec: float = 0.25) -> float:
    if budget_sec is None:
        return poll_sec
    remaining = budget_sec - (time.perf_counter() - started)
    if remaining <= 0.0:
        raise BudgetExceeded(f"scenario budget exhausted after {time.perf_counter() - started:.3f}s")
    return max(0.001, min(poll_sec, remaining))


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


def resolve_parallelism(jobs_arg: str, total_jobs: int, mode: str) -> int:
    if jobs_arg == "auto":
        cpu_cap = min(os.cpu_count() or 1, auto_parallelism_cap(mode))
        return max(1, min(cpu_cap, total_jobs if total_jobs else 1))
    return max(1, int(jobs_arg))


def run_scenarios_bounded(
    *,
    exe: pathlib.Path,
    selected: list[ScenarioCase],
    parallelism: int,
    timeout_sec: float | None,
    started: float,
    budget_sec: float | None,
    verbose: bool,
) -> list[ScenarioResult]:
    """Run scenarios with at most one wave of subprocesses in flight.

    This mirrors the C++ runner's bounded scheduler. The aggregate budget is
    checked before launching new work rather than after the full suite has
    already been submitted to the executor.
    """
    results: list[ScenarioResult] = []
    case_iter = iter(selected)
    future_to_case: dict[concurrent.futures.Future[ScenarioResult], ScenarioCase] = {}

    def submit_next(executor: concurrent.futures.ThreadPoolExecutor) -> bool:
        check_budget(started, budget_sec)
        try:
            case = next(case_iter)
        except StopIteration:
            return False
        future_to_case[executor.submit(run_scenario, exe, case, timeout_sec)] = case
        return True

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=parallelism)
    try:
        for _ in range(parallelism):
            if not submit_next(executor):
                break
        while future_to_case:
            done, _ = concurrent.futures.wait(
                future_to_case,
                timeout=budget_poll_timeout(started, budget_sec),
                return_when=concurrent.futures.FIRST_COMPLETED,
            )
            if not done:
                check_budget(started, budget_sec)
                continue
            for future in done:
                future_to_case.pop(future)
                result = future.result()
                results.append(result)
                if verbose or result.status != "passed":
                    print(f"[{result.status}] {result.name} {result.duration_sec:.6f}s", flush=True)
            while len(future_to_case) < parallelism:
                if not submit_next(executor):
                    break
    except BudgetExceeded:
        for pending in future_to_case:
            pending.cancel()
        raise
    finally:
        executor.shutdown(wait=True, cancel_futures=True)
    return results


def write_junit(path: pathlib.Path, results: list[ScenarioResult]) -> None:
    suite = ET.Element("testsuite", {
        "name": "mtgsim_scenarios",
        "tests": str(len(results)),
        "failures": str(sum(1 for result in results if result.status == "failed")),
        "errors": str(sum(1 for result in results if result.status == "timeout")),
        "time": f"{sum(result.duration_sec for result in results):.6f}",
    })
    for result in results:
        case = ET.SubElement(suite, "testcase", {
            "classname": "mtgsim.scenario",
            "name": result.name,
            "time": f"{result.duration_sec:.6f}",
        })
        if result.status == "failed":
            failure = ET.SubElement(case, "failure", {"message": result.message or f"returncode={result.returncode}"})
            failure.text = (result.stderr_tail or result.stdout_tail or result.message)[:4000]
        elif result.status == "timeout":
            error = ET.SubElement(case, "error", {"message": result.message})
            error.text = (result.stderr_tail or result.stdout_tail or result.message)[:4000]
        if result.stdout_tail:
            stdout = ET.SubElement(case, "system-out")
            stdout.text = result.stdout_tail
        if result.stderr_tail:
            stderr = ET.SubElement(case, "system-err")
            stderr.text = result.stderr_tail
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(suite).write(path, encoding="utf-8", xml_declaration=True)


def run_all(*,
            mode: str,
            exe: pathlib.Path,
            jobs_arg: str,
            case_filter: str,
            timeout_sec: float | None,
            budget_sec: float | None,
            shuffle_seed: int | None,
            shard_count: int,
            shard_index: int,
            verbose: bool) -> tuple[int, dict[str, Any]]:
    started = time.perf_counter()
    discovered = discover_scenarios()
    filtered = [case for case in discovered if not case_filter or case_filter in case.name or case_filter in rel(case.path)]
    selected = assign_shards(filtered, shard_count, shard_index)
    if shuffle_seed is not None:
        rng = random.Random(shuffle_seed)
        rng.shuffle(selected)
    parallelism = resolve_parallelism(jobs_arg, len(selected), mode)

    print(
        f"scenario-runner discovered={len(discovered)} filtered={len(filtered)} "
        f"shard={shard_index}/{shard_count} selected={len(selected)} parallelism={parallelism} exe={rel(exe)}",
        flush=True,
    )

    results: list[ScenarioResult] = []
    if selected:
        if parallelism == 1:
            for case in selected:
                check_budget(started, budget_sec)
                result = run_scenario(exe, case, timeout_sec)
                results.append(result)
                if verbose or result.status != "passed":
                    print(f"[{result.status}] {result.name} {result.duration_sec:.6f}s", flush=True)
        else:
            results.extend(run_scenarios_bounded(
                exe=exe,
                selected=selected,
                parallelism=parallelism,
                timeout_sec=timeout_sec,
                started=started,
                budget_sec=budget_sec,
                verbose=verbose,
            ))

    results.sort(key=lambda item: item.name)
    failures = sum(1 for result in results if result.status != "passed")
    report = {
        "schema": "mtgsim.scenario_parallel_report.v1",
        "created_at_local": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "status": "passed" if failures == 0 else "failed",
        "duration_sec": time.perf_counter() - started,
        "config": {
            "mode": mode,
            "executable": rel(exe),
            "jobs": jobs_arg,
            "parallelism": parallelism,
            "case_filter": case_filter,
            "timeout_sec": timeout_sec,
            "budget_sec": budget_sec,
            "shuffle_seed": shuffle_seed,
            "shard_count": shard_count,
            "shard_index": shard_index,
        },
        "selection": {
            "scenarios_discovered": len(discovered),
            "scenarios_filtered_before_shard": len(filtered),
            "scenarios_selected_on_shard": len(selected),
            "scenario_names": [case.name for case in selected],
        },
        "summary": {
            "scenarios": len(results),
            "passed": sum(1 for result in results if result.status == "passed"),
            "failed": sum(1 for result in results if result.status == "failed"),
            "timeouts": sum(1 for result in results if result.status == "timeout"),
            "assertions": sum(result.assertions for result in results),
        },
        "results": [asdict(result) for result in results],
    }
    return (0 if failures == 0 else 1), report


def record_sqlite(report: dict[str, Any], report_path: pathlib.Path) -> None:
    try:
        sys.path.insert(0, str(ROOT / "tools"))
        import metrics_db  # type: ignore
        metrics_db.record_scenario_report(report, report_path)
    except Exception as exc:  # pragma: no cover - metrics must not mask tests
        print(f"warning: unable to record scenario report in sqlite: {exc}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["debug", "release", "sanitize", "profile"], default="release")
    parser.add_argument("--exe", type=pathlib.Path, default=None)
    parser.add_argument("--jobs", default="auto")
    parser.add_argument("--filter", default="")
    parser.add_argument("--scenario-timeout-sec", type=float, default=5.0)
    parser.add_argument("--budget-sec", type=float, default=None)
    parser.add_argument("--shuffle-seed", type=int, default=None)
    parser.add_argument("--shard-count", type=int, default=1)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--report", type=pathlib.Path, default=REPORT_DIR / "scenario_parallel_latest.json")
    parser.add_argument("--junit", type=pathlib.Path, default=REPORT_DIR / "scenario_parallel_latest.xml")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    exe = resolve_executable(args.mode, args.exe)
    if not exe.exists():
        print(f"scenario executable not found: {rel(exe)}; build target 'scenario' or 'all' first", file=sys.stderr)
        return 2

    try:
        code, report = run_all(
            mode=args.mode,
            exe=exe,
            jobs_arg=args.jobs,
            case_filter=args.filter,
            timeout_sec=args.scenario_timeout_sec,
            budget_sec=args.budget_sec,
            shuffle_seed=args.shuffle_seed,
            shard_count=args.shard_count,
            shard_index=args.shard_index,
            verbose=args.verbose,
        )
    except BudgetExceeded as exc:
        report = {
            "schema": "mtgsim.scenario_parallel_report.v1",
            "created_at_local": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "status": "failed",
            "duration_sec": args.budget_sec or 0.0,
            "config": {
                "mode": args.mode,
                "executable": rel(exe),
                "jobs": args.jobs,
                "case_filter": args.filter,
                "timeout_sec": args.scenario_timeout_sec,
                "budget_sec": args.budget_sec,
                "shuffle_seed": args.shuffle_seed,
                "shard_count": args.shard_count,
                "shard_index": args.shard_index,
            },
            "selection": {},
            "summary": {"scenarios": 0, "passed": 0, "failed": 0, "timeouts": 0, "assertions": 0, "errors": 1},
            "error": str(exc),
            "results": [],
        }
        code = 124

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    append_jsonl(args.report.parent / "scenario_parallel_history.jsonl", report)
    write_junit(args.junit, [ScenarioResult(**item) for item in report["results"]])
    record_sqlite(report, args.report)

    if args.json:
        print(json.dumps(report, sort_keys=True))
    else:
        summary = report["summary"]
        print(
            f"scenarios status={report['status']} passed={summary['passed']}/{summary['scenarios']} "
            f"assertions={summary['assertions']} duration={report['duration_sec']:.3f}s report={rel(args.report)}"
        )
    return code


if __name__ == "__main__":
    raise SystemExit(main())
