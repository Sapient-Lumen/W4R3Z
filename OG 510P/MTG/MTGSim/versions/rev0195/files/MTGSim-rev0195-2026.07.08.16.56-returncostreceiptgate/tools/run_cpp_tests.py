#!/usr/bin/env python3
"""Parallel and shardable C++ test runner for MTGSim.

The C++ binary owns case registration plus tags/rule metadata. This runner owns
orchestration: discovery, filtering, deterministic sharding, optional historical
balancing from SQLite, parallel subprocess execution, budgets, JUnit, JSON, and
history recording.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import pathlib
import random
import shlex
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from typing import Any

os.environ.setdefault("TZ", "America/New_York")
if hasattr(time, "tzset"):
    time.tzset()

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "harness"


@dataclass(frozen=True)
class DiscoveredCase:
    name: str
    tags: list[str] = field(default_factory=list)
    rules: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CaseJob:
    case: DiscoveredCase
    repeat_index: int


@dataclass
class CaseResult:
    name: str
    repeat_index: int
    status: str
    duration_sec: float
    command: list[str]
    returncode: int | None = None
    tags: list[str] = field(default_factory=list)
    rules: list[str] = field(default_factory=list)
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


def compact_history_record(report: dict[str, Any], report_path: pathlib.Path) -> dict[str, Any]:
    """Keep append-only history useful without carrying every per-case result.

    Full detail remains in the named report file. The JSONL history is for quick
    trend review and package hygiene; rev0151 keeps it below the datacube large
    file warning threshold so audits do not start failing due to their own logs.
    """
    config = report.get("config", {}) if isinstance(report.get("config"), dict) else {}
    summary = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}
    return {
        "schema": "mtgsim.cpp_parallel_history.compact.v1",
        "source_schema": report.get("schema"),
        "created_at_local": report.get("created_at_local"),
        "status": report.get("status"),
        "duration_sec": report.get("duration_sec"),
        "mode": config.get("mode"),
        "jobs": config.get("jobs"),
        "executable": config.get("executable"),
        "report": rel(report_path),
        "summary": {
            "case_jobs": summary.get("case_jobs"),
            "passed": summary.get("passed"),
            "failed": summary.get("failed"),
            "timeouts": summary.get("timeouts"),
            "errors": summary.get("errors"),
            "rules_touched_count": len(summary.get("rules_touched", {})) if isinstance(summary.get("rules_touched"), dict) else 0,
        },
    }


def resolve_executable(mode: str, explicit: pathlib.Path | None) -> pathlib.Path:
    if explicit is not None:
        return explicit if explicit.is_absolute() else ROOT / explicit
    return ROOT / "build" / f"gcc-{mode}" / "mtgsim_tests"


def discover_cases(exe: pathlib.Path) -> list[DiscoveredCase]:
    proc = subprocess.run([str(exe), "--list-json"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise RuntimeError(f"failed to discover C++ tests from {exe}: {tail(proc.stderr or proc.stdout)}")
    raw = json.loads(proc.stdout)
    cases: list[DiscoveredCase] = []
    for item in raw:
        cases.append(DiscoveredCase(
            name=str(item["name"]),
            tags=[str(v) for v in item.get("tags", [])],
            rules=[str(v) for v in item.get("rules", [])],
        ))
    cases.sort(key=lambda case: case.name)
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


def run_case(exe: pathlib.Path, job: CaseJob, timeout_sec: float | None) -> CaseResult:
    cmd = [str(exe), "--case", job.case.name, "--json"]
    begin = time.perf_counter()
    try:
        proc = subprocess.run(
            cmd,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_sec,
        )
        duration = time.perf_counter() - begin
        parsed = parse_binary_report(proc.stdout)
        message = ""
        if parsed.get("results"):
            message = str(parsed["results"][0].get("message", ""))
        return CaseResult(
            name=job.case.name,
            repeat_index=job.repeat_index,
            status="passed" if proc.returncode == 0 else "failed",
            duration_sec=duration,
            command=cmd,
            returncode=proc.returncode,
            tags=job.case.tags,
            rules=job.case.rules,
            stdout_tail=tail(proc.stdout),
            stderr_tail=tail(proc.stderr),
            message=message,
        )
    except subprocess.TimeoutExpired as exc:
        duration = time.perf_counter() - begin
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        return CaseResult(
            name=job.case.name,
            repeat_index=job.repeat_index,
            status="timeout",
            duration_sec=duration,
            command=cmd,
            returncode=124,
            tags=job.case.tags,
            rules=job.case.rules,
            stdout_tail=tail(stdout),
            stderr_tail=tail(stderr),
            message=f"case timed out after {timeout_sec:.3f}s" if timeout_sec is not None else "case timed out",
        )


def check_budget(started: float, budget_sec: float | None) -> None:
    if budget_sec is not None and time.perf_counter() - started > budget_sec:
        raise BudgetExceeded(f"C++ test budget exhausted after {time.perf_counter() - started:.3f}s")


def budget_poll_timeout(started: float, budget_sec: float | None, *, poll_sec: float = 0.25) -> float:
    if budget_sec is None:
        return poll_sec
    remaining = budget_sec - (time.perf_counter() - started)
    if remaining <= 0.0:
        raise BudgetExceeded(f"C++ test budget exhausted after {time.perf_counter() - started:.3f}s")
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


def run_case_jobs_bounded(
    *,
    exe: pathlib.Path,
    jobs: list[CaseJob],
    parallelism: int,
    timeout_sec: float | None,
    started: float,
    budget_sec: float | None,
    verbose: bool,
    fail_fast: bool,
) -> list[CaseResult]:
    """Run cases without pre-submitting the entire suite.

    The previous parallel runner submitted every case to the executor before
    checking the aggregate wall-clock budget. That worked for short release
    runs, but sanitizer/stress invocations could keep a cloud container busy
    well after the harness budget was already exhausted. This scheduler keeps
    only ``parallelism`` futures in flight, so any budget overshoot is bounded
    by the per-case timeout of the currently running wave.
    """
    results: list[CaseResult] = []
    job_iter = iter(jobs)
    future_to_job: dict[concurrent.futures.Future[CaseResult], CaseJob] = {}
    stop_submitting = False

    def submit_next(executor: concurrent.futures.ThreadPoolExecutor) -> bool:
        nonlocal stop_submitting
        if stop_submitting:
            return False
        check_budget(started, budget_sec)
        try:
            job = next(job_iter)
        except StopIteration:
            return False
        future_to_job[executor.submit(run_case, exe, job, timeout_sec)] = job
        return True

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=parallelism)
    try:
        for _ in range(parallelism):
            if not submit_next(executor):
                break
        while future_to_job:
            done, _ = concurrent.futures.wait(
                future_to_job,
                timeout=budget_poll_timeout(started, budget_sec),
                return_when=concurrent.futures.FIRST_COMPLETED,
            )
            if not done:
                check_budget(started, budget_sec)
                continue
            for future in done:
                future_to_job.pop(future)
                result = future.result()
                results.append(result)
                if verbose or result.status != "passed":
                    print(f"[{result.status}] {result.name} repeat={result.repeat_index} {result.duration_sec:.6f}s", flush=True)
                if fail_fast and result.status != "passed":
                    stop_submitting = True
            while not stop_submitting and len(future_to_job) < parallelism:
                if not submit_next(executor):
                    break
    except BudgetExceeded:
        stop_submitting = True
        for pending in future_to_job:
            pending.cancel()
        raise
    finally:
        executor.shutdown(wait=True, cancel_futures=True)
    return results


def case_matches(case: DiscoveredCase,
                 text_filter: str,
                 include_tags: list[str],
                 exclude_tags: list[str],
                 include_rules: list[str]) -> bool:
    haystack = [case.name, *case.tags, *case.rules]
    if text_filter and not any(text_filter in value for value in haystack):
        return False
    if include_tags and not all(tag in case.tags for tag in include_tags):
        return False
    if exclude_tags and any(tag in case.tags for tag in exclude_tags):
        return False
    if include_rules and not any(any(rule_filter in rule for rule in case.rules) for rule_filter in include_rules):
        return False
    return True


def load_duration_estimates(enabled: bool) -> dict[str, float]:
    if not enabled:
        return {}
    try:
        sys.path.insert(0, str(ROOT / "tools"))
        import metrics_db  # type: ignore
        return metrics_db.case_duration_estimates()
    except Exception:
        return {}


def stable_hash_mod(value: str, modulus: int) -> int:
    digest = hashlib.sha256(value.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % modulus


def assign_shards(cases: list[DiscoveredCase],
                  shard_count: int,
                  strategy: str,
                  durations: dict[str, float]) -> tuple[list[list[DiscoveredCase]], list[float]]:
    if shard_count <= 0:
        raise ValueError("shard_count must be positive")
    shards: list[list[DiscoveredCase]] = [[] for _ in range(shard_count)]
    loads = [0.0 for _ in range(shard_count)]
    if shard_count == 1:
        shards[0] = list(cases)
        loads[0] = sum(max(durations.get(case.name, 0.001), 0.001) for case in cases)
        return shards, loads

    if strategy == "hash":
        for case in cases:
            index = stable_hash_mod(case.name, shard_count)
            shards[index].append(case)
            loads[index] += max(durations.get(case.name, 0.001), 0.001)
    elif strategy == "duration-greedy":
        weighted = sorted(cases, key=lambda case: (-max(durations.get(case.name, 0.001), 0.001), case.name))
        for case in weighted:
            index = min(range(shard_count), key=lambda idx: (loads[idx], len(shards[idx]), idx))
            shards[index].append(case)
            loads[index] += max(durations.get(case.name, 0.001), 0.001)
    elif strategy == "round-robin":
        for index, case in enumerate(cases):
            shard = index % shard_count
            shards[shard].append(case)
            loads[shard] += max(durations.get(case.name, 0.001), 0.001)
    else:
        raise ValueError(f"unknown shard strategy: {strategy}")

    for shard in shards:
        shard.sort(key=lambda case: case.name)
    return shards, loads


def env_int(*names: str) -> int | None:
    for name in names:
        raw = os.environ.get(name)
        if raw is None or raw == "":
            continue
        try:
            return int(raw)
        except ValueError as exc:
            raise ValueError(f"invalid integer in ${name}: {raw!r}") from exc
    return None


def touch_shard_status_file() -> None:
    path = os.environ.get("TEST_SHARD_STATUS_FILE") or os.environ.get("GTEST_SHARD_STATUS_FILE")
    if path:
        status = pathlib.Path(path)
        status.parent.mkdir(parents=True, exist_ok=True)
        status.touch()


def write_junit(path: pathlib.Path, results: list[CaseResult]) -> None:
    suite = ET.Element("testsuite", {
        "name": "mtgsim_cpp_parallel",
        "tests": str(len(results)),
        "failures": str(sum(1 for result in results if result.status == "failed")),
        "errors": str(sum(1 for result in results if result.status == "timeout")),
        "time": f"{sum(result.duration_sec for result in results):.6f}",
    })
    for result in results:
        case = ET.SubElement(suite, "testcase", {
            "classname": "mtgsim.cpp",
            "name": f"{result.name}[{result.repeat_index}]",
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


def run_all(
    *,
    mode: str,
    exe: pathlib.Path,
    jobs_arg: str,
    repeat: int,
    case_filter: str,
    include_tags: list[str],
    exclude_tags: list[str],
    include_rules: list[str],
    shuffle_seed: int | None,
    timeout_sec: float | None,
    budget_sec: float | None,
    verbose: bool,
    shard_count: int,
    shard_index: int,
    shard_strategy: str,
    history_balance: bool,
    fail_fast: bool,
) -> tuple[int, dict[str, Any]]:
    started = time.perf_counter()
    discovered = discover_cases(exe)
    if not discovered:
        raise RuntimeError("C++ test executable reported zero cases")
    filtered = [case for case in discovered if case_matches(case, case_filter, include_tags, exclude_tags, include_rules)]
    if not filtered:
        raise RuntimeError("no C++ test cases selected before sharding")
    if shard_index < 0 or shard_index >= shard_count:
        raise ValueError("shard_index must be in [0, shard_count)")
    durations = load_duration_estimates(history_balance)
    shards, estimated_loads = assign_shards(filtered, shard_count, shard_strategy, durations)
    cases = shards[shard_index]
    jobs: list[CaseJob] = [CaseJob(case=case, repeat_index=repeat_index) for repeat_index in range(repeat) for case in cases]
    if shuffle_seed is not None:
        rng = random.Random(shuffle_seed)
        rng.shuffle(jobs)
    parallelism = resolve_parallelism(jobs_arg, len(jobs), mode)

    print(
        f"cpp-test-runner discovered={len(discovered)} filtered={len(filtered)} "
        f"shard={shard_index}/{shard_count} cases={len(cases)} jobs={len(jobs)} "
        f"parallelism={parallelism} strategy={shard_strategy} exe={rel(exe)}",
        flush=True,
    )
    results: list[CaseResult] = []
    if jobs:
        if parallelism == 1:
            for job in jobs:
                check_budget(started, budget_sec)
                result = run_case(exe, job, timeout_sec)
                results.append(result)
                if verbose or result.status != "passed":
                    print(f"[{result.status}] {result.name} repeat={result.repeat_index} {result.duration_sec:.6f}s", flush=True)
                if fail_fast and result.status != "passed":
                    break
        else:
            results.extend(run_case_jobs_bounded(
                exe=exe,
                jobs=jobs,
                parallelism=parallelism,
                timeout_sec=timeout_sec,
                started=started,
                budget_sec=budget_sec,
                verbose=verbose,
                fail_fast=fail_fast,
            ))

    results.sort(key=lambda item: (item.name, item.repeat_index))
    duration = time.perf_counter() - started
    failures = sum(1 for result in results if result.status != "passed")
    rule_touch_counts: dict[str, int] = {}
    tag_counts: dict[str, int] = {}
    for result in results:
        for rule in result.rules:
            rule_touch_counts[rule] = rule_touch_counts.get(rule, 0) + 1
        for tag in result.tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    report = {
        "schema": "mtgsim.cpp_parallel_report.v2",
        "created_at_local": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "status": "passed" if failures == 0 else "failed",
        "duration_sec": duration,
        "config": {
            "mode": mode,
            "executable": str(rel(exe)),
            "jobs": jobs_arg,
            "parallelism": parallelism,
            "repeat": repeat,
            "case_filter": case_filter,
            "include_tags": include_tags,
            "exclude_tags": exclude_tags,
            "include_rules": include_rules,
            "shuffle_seed": shuffle_seed,
            "timeout_sec": timeout_sec,
            "budget_sec": budget_sec,
            "fail_fast": fail_fast,
            "shard_count": shard_count,
            "shard_index": shard_index,
            "shard_strategy": shard_strategy,
            "history_balance": history_balance,
        },
        "selection": {
            "cases_discovered": len(discovered),
            "cases_filtered_before_shard": len(filtered),
            "cases_selected_on_shard": len(cases),
            "case_names": [case.name for case in cases],
            "estimated_shard_loads_sec": [round(value, 6) for value in estimated_loads],
            "estimated_selected_shard_load_sec": round(estimated_loads[shard_index] if shard_index < len(estimated_loads) else 0.0, 6),
            "historical_duration_samples": len(durations),
        },
        "summary": {
            "case_jobs": len(jobs),
            "passed": sum(1 for result in results if result.status == "passed"),
            "failed": sum(1 for result in results if result.status == "failed"),
            "timeouts": sum(1 for result in results if result.status == "timeout"),
            "rules_touched": dict(sorted(rule_touch_counts.items())),
            "tags_touched": dict(sorted(tag_counts.items())),
        },
        "results": [asdict(result) for result in results],
    }
    return (0 if failures == 0 else 1), report


def record_sqlite(report: dict[str, Any], report_path: pathlib.Path) -> None:
    try:
        sys.path.insert(0, str(ROOT / "tools"))
        import metrics_db  # type: ignore
        metrics_db.record_cpp_test_report(report, report_path)
    except Exception as exc:  # pragma: no cover - history must never mask test failure
        print(f"warning: unable to record C++ test report in sqlite: {exc}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["debug", "release", "sanitize", "profile"], default="release")
    parser.add_argument("--exe", type=pathlib.Path, default=None)
    parser.add_argument("--jobs", default="auto")
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--filter", default="")
    parser.add_argument("--tag", action="append", default=[], help="Require a tag. Repeat to require multiple tags.")
    parser.add_argument("--exclude-tag", action="append", default=[], help="Exclude cases with this tag. Repeatable.")
    parser.add_argument("--rule", action="append", default=[], help="Select cases whose rule refs contain this value. Repeatable OR.")
    parser.add_argument("--shuffle-seed", type=int, default=None)
    parser.add_argument("--case-timeout-sec", type=float, default=5.0)
    parser.add_argument("--budget-sec", type=float, default=None)
    parser.add_argument("--shard-count", type=int, default=None, help="Total shards. Defaults to TEST_TOTAL_SHARDS/GTEST_TOTAL_SHARDS or 1.")
    parser.add_argument("--shard-index", type=int, default=None, help="This shard index. Defaults to TEST_SHARD_INDEX/GTEST_SHARD_INDEX or 0.")
    parser.add_argument("--shard-strategy", choices=["round-robin", "hash", "duration-greedy"], default="round-robin")
    parser.add_argument("--no-history-balance", action="store_true", help="Disable SQLite duration estimates for duration-greedy sharding.")
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument("--list-selected-json", action="store_true", help="Print discovered/filtered/sharded case names and exit without running cases.")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--report", type=pathlib.Path, default=REPORT_DIR / "cpp_parallel_report_latest.json")
    parser.add_argument("--junit", type=pathlib.Path, default=REPORT_DIR / "cpp_parallel_junit_latest.xml")
    parser.add_argument("--json", action="store_true", help="Print compact JSON report as final stdout line.")
    args = parser.parse_args(argv)

    if args.repeat <= 0:
        raise SystemExit("--repeat must be positive")
    exe = resolve_executable(args.mode, args.exe)
    if not exe.exists():
        raise SystemExit(f"C++ test executable is missing: {exe}")

    shard_count = args.shard_count if args.shard_count is not None else (env_int("TEST_TOTAL_SHARDS", "GTEST_TOTAL_SHARDS") or 1)
    shard_index = args.shard_index if args.shard_index is not None else (env_int("TEST_SHARD_INDEX", "GTEST_SHARD_INDEX") or 0)
    touch_shard_status_file()

    if args.list_selected_json:
        discovered = discover_cases(exe)
        filtered = [case for case in discovered if case_matches(case, args.filter, args.tag, args.exclude_tag, args.rule)]
        durations = load_duration_estimates(not args.no_history_balance)
        shards, loads = assign_shards(filtered, shard_count, args.shard_strategy, durations)
        selected = shards[shard_index] if 0 <= shard_index < shard_count else []
        print(json.dumps({
            "schema": "mtgsim.cpp_selection.v1",
            "discovered": len(discovered),
            "filtered_before_shard": len(filtered),
            "shard_count": shard_count,
            "shard_index": shard_index,
            "shard_strategy": args.shard_strategy,
            "estimated_shard_loads_sec": [round(value, 6) for value in loads],
            "cases": [asdict(case) for case in selected],
        }, indent=2, sort_keys=True))
        return 0

    try:
        exit_code, report = run_all(
            mode=args.mode,
            exe=exe,
            jobs_arg=args.jobs,
            repeat=args.repeat,
            case_filter=args.filter,
            include_tags=args.tag,
            exclude_tags=args.exclude_tag,
            include_rules=args.rule,
            shuffle_seed=args.shuffle_seed,
            timeout_sec=args.case_timeout_sec,
            budget_sec=args.budget_sec,
            verbose=args.verbose,
            shard_count=shard_count,
            shard_index=shard_index,
            shard_strategy=args.shard_strategy,
            history_balance=not args.no_history_balance,
            fail_fast=args.fail_fast,
        )
    except BudgetExceeded as exc:
        report = {
            "schema": "mtgsim.cpp_parallel_report.v2",
            "created_at_local": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "status": "failed",
            "duration_sec": args.budget_sec or 0.0,
            "summary": {"errors": 1},
            "error": str(exc),
            "results": [],
        }
        exit_code = 124
    except Exception as exc:
        report = {
            "schema": "mtgsim.cpp_parallel_report.v2",
            "created_at_local": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "status": "failed",
            "duration_sec": 0.0,
            "summary": {"errors": 1},
            "error": str(exc),
            "results": [],
        }
        exit_code = 2

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    append_jsonl(REPORT_DIR / "cpp_parallel_history.jsonl", compact_history_record(report, args.report))
    write_junit(args.junit, [CaseResult(**result) for result in report.get("results", [])])
    record_sqlite(report, args.report)

    print(f"cpp tests {report['status']} in {report['duration_sec']:.3f}s; report={rel(args.report)} junit={rel(args.junit)}")
    if args.json:
        print(json.dumps(report, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
