#!/usr/bin/env python3
"""Parallel seed fan-out runner for the MTGSim legal-action fuzz binary."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import pathlib
import random
import shlex
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


@dataclass
class FuzzResult:
    name: str
    seed: int
    status: str
    duration_sec: float
    returncode: int
    stdout_tail: str = ""
    stderr_tail: str = ""
    message: str = ""
    metrics: dict[str, Any] | None = None
    # Failure triage fields are populated only when a seed fails.  They turn a
    # broad fuzz miss into an immediately replayable, smaller counterexample.
    repro_command: str = ""
    minimal_failing_steps: int = 0
    minimal_repro_command: str = ""
    shrink_status: str = ""
    shrink_attempts: int = 0
    shrink_message: str = ""


class BudgetExceeded(RuntimeError):
    pass


def rel(path: pathlib.Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def tail(text: str, limit: int = 4000) -> str:
    return text[-limit:] if len(text) > limit else text


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


def resolve_jobs(value: str, total: int, mode: str) -> int:
    if value == "auto":
        cpu_cap = min(os.cpu_count() or 1, auto_parallelism_cap(mode))
        return max(1, min(total, cpu_cap))
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("jobs must be positive or auto")
    return max(1, min(parsed, total))


def check_budget(started: float, budget_sec: float | None) -> None:
    if budget_sec is not None and time.perf_counter() - started > budget_sec:
        raise BudgetExceeded(f"fuzz budget exhausted after {time.perf_counter() - started:.3f}s")


def budget_poll_timeout(started: float, budget_sec: float | None, *, poll_sec: float = 0.25) -> float:
    if budget_sec is None:
        return poll_sec
    remaining = budget_sec - (time.perf_counter() - started)
    if remaining <= 0.0:
        raise BudgetExceeded(f"fuzz budget exhausted after {time.perf_counter() - started:.3f}s")
    return max(0.001, min(poll_sec, remaining))


def executable_for(mode: str) -> pathlib.Path:
    return ROOT / "build" / f"gcc-{mode}" / "mtgsim_fuzz"


def parse_json_line(text: str) -> dict[str, Any]:
    for line in reversed(text.splitlines()):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            return json.loads(line)
    return {}


def fuzz_command(exe: pathlib.Path, seed: int, steps: int, profile: str, require_risk_seams: bool) -> list[str]:
    cmd = [str(exe), "--seed", str(seed), "--steps", str(steps), "--profile", profile]
    if require_risk_seams:
        cmd.append("--require-risk-seams")
    cmd.append("--json")
    return cmd


def command_text(cmd: list[str]) -> str:
    rendered: list[str] = []
    for index, part in enumerate(cmd):
        path = pathlib.Path(part)
        if index == 0 and path.exists():
            rendered.append(rel(path))
        else:
            rendered.append(part)
    return " ".join(shlex.quote(part) for part in rendered)


def run_one(exe: pathlib.Path, seed: int, steps: int, timeout_sec: float, profile: str, require_risk_seams: bool) -> FuzzResult:
    cmd = fuzz_command(exe, seed, steps, profile, require_risk_seams)
    begin = time.perf_counter()
    try:
        proc = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout_sec)
        duration = time.perf_counter() - begin
        metrics = parse_json_line(proc.stdout) if proc.stdout.strip() else {}
        status = "passed" if proc.returncode == 0 and metrics.get("status", "passed") == "passed" else "failed"
        return FuzzResult(
            name=f"fuzz_seed_{seed}",
            seed=seed,
            status=status,
            duration_sec=duration,
            returncode=proc.returncode,
            stdout_tail=tail(proc.stdout),
            stderr_tail=tail(proc.stderr),
            message=str(metrics.get("message", "")),
            metrics=metrics,
            repro_command=command_text(cmd),
        )
    except subprocess.TimeoutExpired as exc:
        duration = time.perf_counter() - begin
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        return FuzzResult(
            name=f"fuzz_seed_{seed}",
            seed=seed,
            status="failed",
            duration_sec=duration,
            returncode=124,
            stdout_tail=tail(stdout),
            stderr_tail=tail(stderr),
            message=f"timeout after {timeout_sec:.3f}s",
            metrics={},
            repro_command=command_text(cmd),
        )


def failure_reproduces(exe: pathlib.Path, seed: int, steps: int, timeout_sec: float, profile: str, require_risk_seams: bool) -> tuple[bool, str, int]:
    result = run_one(exe, seed, steps, timeout_sec, profile, require_risk_seams)
    message = result.message or result.stderr_tail or result.stdout_tail
    return result.status != "passed", message, result.returncode


def shrink_failure_steps(
    *,
    exe: pathlib.Path,
    result: FuzzResult,
    original_steps: int,
    timeout_sec: float,
    profile: str,
    require_risk_seams: bool,
    started: float,
    budget_sec: float | None,
) -> None:
    if result.status == "passed" or original_steps <= 1:
        return
    if result.returncode == 124:
        result.shrink_status = "skipped-timeout"
        result.shrink_message = "timeout failures are left at the original step budget"
        return

    attempts = 0

    def probe(steps: int) -> tuple[bool, str, int]:
        nonlocal attempts
        check_budget(started, budget_sec)
        attempts += 1
        return failure_reproduces(exe, result.seed, steps, timeout_sec, profile, require_risk_seams)

    try:
        still_fails, message, returncode = probe(original_steps)
        if not still_fails:
            result.shrink_status = "not-reproduced"
            result.shrink_message = "original failing seed did not reproduce during shrink replay"
            result.shrink_attempts = attempts
            return
        low = 1
        high = original_steps
        best_message = message
        best_returncode = returncode
        while low < high:
            mid = (low + high) // 2
            fails, message, returncode = probe(mid)
            if fails:
                high = mid
                best_message = message
                best_returncode = returncode
            else:
                low = mid + 1
        result.minimal_failing_steps = high
        result.minimal_repro_command = command_text(fuzz_command(exe, result.seed, high, profile, require_risk_seams))
        result.shrink_status = "minimized"
        result.shrink_attempts = attempts
        result.shrink_message = tail(best_message, 1000)
        if result.message == "":
            result.message = f"minimal failing steps={high} returncode={best_returncode}"
    except BudgetExceeded as exc:
        result.shrink_status = "budget-exhausted"
        result.shrink_attempts = attempts
        result.shrink_message = str(exc)


def shrink_failed_results(
    *,
    exe: pathlib.Path,
    results: list[FuzzResult],
    steps: int,
    timeout_sec: float,
    profile: str,
    require_risk_seams: bool,
    started: float,
    budget_sec: float | None,
    enabled: bool,
) -> None:
    if not enabled:
        for result in results:
            if result.status != "passed":
                result.shrink_status = "disabled"
        return
    for result in results:
        if result.status == "passed":
            continue
        shrink_failure_steps(
            exe=exe,
            result=result,
            original_steps=steps,
            timeout_sec=timeout_sec,
            profile=profile,
            require_risk_seams=require_risk_seams,
            started=started,
            budget_sec=budget_sec,
        )


def write_junit(path: pathlib.Path, results: list[FuzzResult]) -> None:
    suite = ET.Element("testsuite", {
        "name": "mtgsim_fuzz",
        "tests": str(len(results)),
        "failures": str(sum(1 for result in results if result.status != "passed")),
        "time": f"{sum(result.duration_sec for result in results):.6f}",
    })
    for result in results:
        case = ET.SubElement(suite, "testcase", {"name": result.name, "time": f"{result.duration_sec:.6f}"})
        if result.status != "passed":
            failure = ET.SubElement(case, "failure", {"message": result.message or f"returncode={result.returncode}"})
            repro = result.minimal_repro_command or result.repro_command
            shrink_note = f"\nminimal_repro={repro}" if repro else ""
            failure.text = ((result.stderr_tail or result.stdout_tail or result.message) + shrink_note)[:4000]
        if result.stdout_tail:
            ET.SubElement(case, "system-out").text = result.stdout_tail
        if result.stderr_tail:
            ET.SubElement(case, "system-err").text = result.stderr_tail
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(suite).write(path, encoding="utf-8", xml_declaration=True)


def append_jsonl(path: pathlib.Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def run_fuzz_bounded(
    *,
    exe: pathlib.Path,
    seeds: list[int],
    jobs: int,
    steps: int,
    timeout_sec: float,
    profile: str,
    require_risk_seams: bool,
    started: float,
    budget_sec: float | None,
    verbose: bool,
) -> list[FuzzResult]:
    results: list[FuzzResult] = []
    seed_iter = iter(seeds)
    future_to_seed: dict[concurrent.futures.Future[FuzzResult], int] = {}

    def submit_next(pool: concurrent.futures.ThreadPoolExecutor) -> bool:
        check_budget(started, budget_sec)
        try:
            seed = next(seed_iter)
        except StopIteration:
            return False
        future_to_seed[pool.submit(run_one, exe, seed, steps, timeout_sec, profile, require_risk_seams)] = seed
        return True

    pool = concurrent.futures.ThreadPoolExecutor(max_workers=jobs)
    try:
        for _ in range(jobs):
            if not submit_next(pool):
                break
        while future_to_seed:
            done, _ = concurrent.futures.wait(
                future_to_seed,
                timeout=budget_poll_timeout(started, budget_sec),
                return_when=concurrent.futures.FIRST_COMPLETED,
            )
            if not done:
                check_budget(started, budget_sec)
                continue
            for future in done:
                future_to_seed.pop(future)
                result = future.result()
                results.append(result)
                if verbose:
                    print(f"[{result.status}] {result.name} {result.duration_sec:.6f}s")
            while len(future_to_seed) < jobs:
                if not submit_next(pool):
                    break
    except BudgetExceeded:
        for pending in future_to_seed:
            pending.cancel()
        raise
    finally:
        pool.shutdown(wait=True, cancel_futures=True)
    return results


def build_report(args: argparse.Namespace, seeds: list[int], results: list[FuzzResult], duration: float) -> dict[str, Any]:
    passed = sum(1 for result in results if result.status == "passed")
    failed = len(results) - passed
    metric_dicts = [result.metrics or {} for result in results]
    action_counter_keys = [
        "applied_actions",
        "pass_actions",
        "cast_actions",
        "land_actions",
        "mana_actions",
        "activated_actions",
        "attack_actions",
        "block_actions",
        "combat_damage_order_actions",
        "trigger_stack_actions",
        "loyalty_actions",
        "forced_advances",
        "invariant_checks",
        "event_count",
    ]
    aggregate_action_counters = {
        key: sum(int(m.get(key) or 0) for m in metric_dicts)
        for key in action_counter_keys
    }
    total_actions = aggregate_action_counters["applied_actions"]
    total_invariants = aggregate_action_counters["invariant_checks"]
    pass_pct = (100.0 * aggregate_action_counters["pass_actions"] / total_actions) if total_actions else 0.0
    risk_seams = {
        "trigger_stack_actions": aggregate_action_counters["trigger_stack_actions"],
        "loyalty_actions": aggregate_action_counters["loyalty_actions"],
        "combat_damage_order_actions": aggregate_action_counters["combat_damage_order_actions"],
        "hit_required": aggregate_action_counters["trigger_stack_actions"] > 0 and aggregate_action_counters["loyalty_actions"] > 0,
    }
    return {
        "schema": "mtgsim.fuzz_parallel_report.v1",
        "created_at_local": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "status": "passed" if failed == 0 else "failed",
        "duration_sec": duration,
        "config": {
            "mode": args.mode,
            "jobs": args.jobs,
            "seed_base": args.seed_base,
            "seeds": args.seeds,
            "steps": args.steps,
            "fuzz_timeout_sec": args.fuzz_timeout_sec,
            "profile": args.profile,
            "require_risk_seams": args.require_risk_seams,
            "budget_sec": args.budget_sec,
            "shuffle_seed": args.shuffle_seed,
        },
        "summary": {
            "selected": len(results),
            "passed": passed,
            "failed": failed,
            "total_actions": total_actions,
            "total_invariant_checks": total_invariants,
            "aggregate_action_counters": aggregate_action_counters,
            "pass_action_pct": round(pass_pct, 3),
            "risk_seams": risk_seams,
            "shrunk_failures": sum(1 for result in results if result.shrink_status == "minimized"),
            "failed_repro_commands": [result.minimal_repro_command or result.repro_command for result in results if result.status != "passed"],
        },
        "seeds": seeds,
        "results": [asdict(result) for result in results],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["debug", "release", "sanitize", "profile"], default="release")
    parser.add_argument("--exe", type=pathlib.Path, default=None)
    parser.add_argument("--jobs", default="auto")
    parser.add_argument("--seed-base", type=int, default=7000)
    parser.add_argument("--seeds", type=int, default=12)
    parser.add_argument("--steps", type=int, default=120)
    parser.add_argument("--profile", choices=["broad", "risk-seams"], default="broad")
    parser.add_argument("--require-risk-seams", action="store_true", help="fail unless aggregate trigger-stack and loyalty actions are both exercised")
    parser.add_argument("--fuzz-timeout-sec", type=float, default=5.0)
    parser.add_argument("--budget-sec", type=float, default=None)
    parser.add_argument("--shuffle-seed", type=int, default=None)
    parser.add_argument("--report", type=pathlib.Path, default=REPORT_DIR / "fuzz_parallel_latest.json")
    parser.add_argument("--junit", type=pathlib.Path, default=REPORT_DIR / "fuzz_parallel_latest.xml")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--no-shrink-failures", action="store_true", help="do not rerun failed seeds to find the smallest failing step count")
    args = parser.parse_args(argv)

    if args.seeds <= 0:
        raise SystemExit("--seeds must be positive")
    if args.steps <= 0:
        raise SystemExit("--steps must be positive")
    exe = args.exe or executable_for(args.mode)
    if not exe.exists():
        raise SystemExit(f"fuzz executable not found: {rel(exe)}")

    seeds = [args.seed_base + i for i in range(args.seeds)]
    if args.shuffle_seed is not None:
        rng = random.Random(args.shuffle_seed)
        rng.shuffle(seeds)
    jobs = resolve_jobs(args.jobs, len(seeds), args.mode)

    print(f"fuzz-runner seeds={len(seeds)} steps={args.steps} profile={args.profile} jobs={jobs} exe={rel(exe)}", flush=True)
    begin = time.perf_counter()
    results: list[FuzzResult] = []
    budget_error = ""
    try:
        results = run_fuzz_bounded(
            exe=exe,
            seeds=seeds,
            jobs=jobs,
            steps=args.steps,
            timeout_sec=args.fuzz_timeout_sec,
            profile=args.profile,
            require_risk_seams=args.require_risk_seams,
            started=begin,
            budget_sec=args.budget_sec,
            verbose=args.verbose,
        )
    except BudgetExceeded as exc:
        budget_error = str(exc)
    results.sort(key=lambda result: result.seed)
    shrink_failed_results(
        exe=exe,
        results=results,
        steps=args.steps,
        timeout_sec=args.fuzz_timeout_sec,
        profile=args.profile,
        require_risk_seams=args.require_risk_seams,
        started=begin,
        budget_sec=args.budget_sec,
        enabled=not args.no_shrink_failures,
    )
    duration = time.perf_counter() - begin
    report = build_report(args, seeds, results, duration)
    if args.require_risk_seams and report.get("status") == "passed" and not report["summary"]["risk_seams"]["hit_required"]:
        report["status"] = "failed"
        report["error"] = "required risk seams were not exercised: expected trigger_stack_actions>0 and loyalty_actions>0"
    if budget_error:
        report["status"] = "failed"
        report["error"] = budget_error
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    append_jsonl(args.report.parent / "fuzz_parallel_history.jsonl", report)
    write_junit(args.junit, results)
    try:
        import metrics_db
        metrics_db.record_fuzz_report(report, args.report)
    except Exception:
        pass
    if args.json:
        print(json.dumps(report, sort_keys=True))
    else:
        summary = report["summary"]
        risk = summary["risk_seams"]
        print(f"fuzz status={report['status']} passed={summary['passed']}/{summary['selected']} actions={summary['total_actions']} pass_pct={summary['pass_action_pct']} trigger_stack={risk['trigger_stack_actions']} loyalty={risk['loyalty_actions']} damage_order={risk['combat_damage_order_actions']} invariants={summary['total_invariant_checks']} duration={duration:.3f}s report={rel(args.report)}")
    return 124 if budget_error else (0 if report["status"] == "passed" else 1)


if __name__ == "__main__":
    raise SystemExit(main())
