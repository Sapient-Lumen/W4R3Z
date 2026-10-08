#!/usr/bin/env python3
"""MTGSim unified timed harness.

Cloud-friendly goals:
- decomposable plans: rules, build, test, bench, all, matrix;
- GCC-first incremental builds with propagated wall-clock budgets;
- parallel C++ case execution via tools/run_cpp_tests.py;
- data-driven scenario execution via tools/run_scenarios.py;
- randomized legal-action invariant fuzzing via tools/run_fuzz.py;
- JSON, JSONL, JUnit, and SQLite metrics for continuous optimization.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import platform
import shlex
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from typing import Any, Callable

os.environ.setdefault("TZ", "America/New_York")
if hasattr(time, "tzset"):
    time.tzset()

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "harness"


class HarnessBudgetExceeded(RuntimeError):
    pass


@dataclass
class StepResult:
    name: str
    status: str
    duration_sec: float
    command: list[str] = field(default_factory=list)
    returncode: int | None = None
    stdout_tail: str = ""
    stderr_tail: str = ""
    metrics: dict[str, Any] = field(default_factory=dict)


@dataclass
class HarnessContext:
    mode: str
    jobs: str
    budget_sec: float | None
    started_perf: float
    keep_going: bool
    verbose: bool
    skip_build: bool
    bench_games: int
    bench_passes: int
    test_repeat: int
    case_timeout_sec: float
    fuzz_seed_base: int
    fuzz_seeds: int
    fuzz_steps: int
    fuzz_timeout_sec: float
    test_filter: str
    shuffle_seed: int | None
    record_sqlite: bool
    shard_count: int
    shard_index: int
    shard_strategy: str


def tail(text: str, limit: int = 6000) -> str:
    return text[-limit:] if len(text) > limit else text


def append_jsonl(path: pathlib.Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def display_path(path: pathlib.Path) -> str:
    """Render a report path relative to ROOT when possible.

    pathlib.Path.relative_to requires both paths to be either absolute or
    relative. The harness accepts relative --report/--junit paths, so normalize
    before rendering. This keeps custom report paths from making successful
    harness runs exit nonzero during final status printing.
    """
    normalized = path if path.is_absolute() else ROOT / path
    try:
        return normalized.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def remaining_budget(ctx: HarnessContext) -> float | None:
    if ctx.budget_sec is None:
        return None
    remaining = ctx.budget_sec - (time.perf_counter() - ctx.started_perf)
    if remaining <= 0:
        raise HarnessBudgetExceeded(f"budget {ctx.budget_sec:.2f}s exhausted")
    return remaining


def parse_last_json_line(stdout: str) -> dict[str, Any]:
    """Parse JSON produced by helper tools.

    Most MTGSim tools emit compact one-line JSON as their final line, but a few
    human-friendly tools pretty-print JSON. Try the whole payload first, then
    fall back to the historical last-line parser.
    """
    stripped = stdout.strip()
    if not stripped:
        return {}
    try:
        parsed = json.loads(stripped)
        return parsed if isinstance(parsed, dict) else {"json_value": parsed}
    except json.JSONDecodeError:
        pass
    for line in reversed(stdout.splitlines()):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            try:
                parsed = json.loads(line)
                return parsed if isinstance(parsed, dict) else {"json_value": parsed}
            except json.JSONDecodeError as exc:
                return {"json_parse_error": str(exc), "raw_stdout_tail": tail(stdout, 1000)}
    return {}


def run_command(name: str, cmd: list[str], ctx: HarnessContext, *, parse_json_stdout: bool = False) -> StepResult:
    budget = remaining_budget(ctx)
    display = " ".join(shlex.quote(part) for part in cmd)
    print(f"[{name}] + {display}", flush=True)
    begin = time.perf_counter()
    try:
        proc = subprocess.run(
            cmd,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=budget,
        )
        duration = time.perf_counter() - begin
        if ctx.verbose and proc.stdout:
            print(proc.stdout, end="")
        if proc.stderr:
            print(proc.stderr, end="", file=sys.stderr)
        metrics = parse_last_json_line(proc.stdout) if parse_json_stdout and proc.stdout.strip() else {}
        return StepResult(
            name=name,
            status="passed" if proc.returncode == 0 else "failed",
            duration_sec=duration,
            command=cmd,
            returncode=proc.returncode,
            stdout_tail=tail(proc.stdout),
            stderr_tail=tail(proc.stderr),
            metrics=metrics,
        )
    except subprocess.TimeoutExpired as exc:
        duration = time.perf_counter() - begin
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        return StepResult(
            name=name,
            status="failed",
            duration_sec=duration,
            command=cmd,
            returncode=124,
            stdout_tail=tail(stdout),
            stderr_tail=tail(stderr) + f"\nTIMEOUT after {duration:.3f}s",
        )


def build_step(target: str, mode_override: str | None = None) -> Callable[[HarnessContext], StepResult]:
    def _run(ctx: HarnessContext) -> StepResult:
        mode = mode_override or ctx.mode
        name = f"build.{mode}.{target}"
        if ctx.skip_build:
            return StepResult(name=name, status="skipped", duration_sec=0.0, metrics={"reason": "--skip-build"})
        cmd = [sys.executable, "tools/build.py", "--mode", mode, "--target", target, "--jobs", ctx.jobs]
        rem = remaining_budget(ctx)
        if rem is not None:
            cmd.extend(["--time-budget-sec", f"{rem:.3f}"])
        if ctx.verbose:
            cmd.append("--verbose")
        return run_command(name, cmd, ctx)
    return _run


def executable(name: str, mode: str) -> pathlib.Path:
    return ROOT / "build" / f"gcc-{mode}" / name


def audit_step(ctx: HarnessContext) -> StepResult:
    return run_command("audit.datacube", [sys.executable, "tools/audit_datacube.py"], ctx, parse_json_stdout=False)


def rules_step(ctx: HarnessContext) -> StepResult:
    return run_command("rules.coverage", [sys.executable, "tools/check_rule_coverage.py"], ctx)


def rules_progress_step(ctx: HarnessContext) -> StepResult:
    return run_command("rules.progress", [sys.executable, "tools/rules_progress.py"], ctx)


def manifest_step(ctx: HarnessContext) -> StepResult:
    return run_command("python.manifest", [sys.executable, "tests/python/test_manifest.py"], ctx)


def fuzz_runner_guard_step(ctx: HarnessContext) -> StepResult:
    return run_command("python.fuzz_runner", [sys.executable, "tests/python/test_fuzz_runner.py"], ctx)


def card_catalog_step(ctx: HarnessContext) -> StepResult:
    return run_command("cards.catalog", [sys.executable, "tools/card_db.py", "--json"], ctx, parse_json_stdout=True)


def cpp_parallel_step(mode_override: str | None = None) -> Callable[[HarnessContext], StepResult]:
    def _run(ctx: HarnessContext) -> StepResult:
        mode = mode_override or ctx.mode
        cmd = [
            sys.executable,
            "tools/run_cpp_tests.py",
            "--mode", mode,
            "--jobs", ctx.jobs,
            "--repeat", str(ctx.test_repeat),
            "--case-timeout-sec", f"{ctx.case_timeout_sec:.3f}",
            "--report", str(REPORT_DIR / f"cpp_parallel_{mode}_latest.json"),
            "--junit", str(REPORT_DIR / f"cpp_parallel_{mode}_latest.xml"),
            "--json",
        ]
        if ctx.test_filter:
            cmd.extend(["--filter", ctx.test_filter])
        if ctx.shuffle_seed is not None:
            cmd.extend(["--shuffle-seed", str(ctx.shuffle_seed)])
        cmd.extend(["--shard-count", str(ctx.shard_count), "--shard-index", str(ctx.shard_index), "--shard-strategy", ctx.shard_strategy])
        rem = remaining_budget(ctx)
        if rem is not None:
            cmd.extend(["--budget-sec", f"{rem:.3f}"])
        if ctx.verbose:
            cmd.append("--verbose")
        return run_command(f"cpp.parallel.{mode}", cmd, ctx, parse_json_stdout=True)
    return _run



def scenario_parallel_step(mode_override: str | None = None) -> Callable[[HarnessContext], StepResult]:
    def _run(ctx: HarnessContext) -> StepResult:
        mode = mode_override or ctx.mode
        cmd = [
            sys.executable,
            "tools/run_scenarios.py",
            "--mode", mode,
            "--jobs", ctx.jobs,
            "--scenario-timeout-sec", f"{ctx.case_timeout_sec:.3f}",
            "--report", str(REPORT_DIR / f"scenario_parallel_{mode}_latest.json"),
            "--junit", str(REPORT_DIR / f"scenario_parallel_{mode}_latest.xml"),
            "--json",
        ]
        if ctx.test_filter:
            cmd.extend(["--filter", ctx.test_filter])
        if ctx.shuffle_seed is not None:
            cmd.extend(["--shuffle-seed", str(ctx.shuffle_seed)])
        cmd.extend(["--shard-count", str(ctx.shard_count), "--shard-index", str(ctx.shard_index)])
        rem = remaining_budget(ctx)
        if rem is not None:
            cmd.extend(["--budget-sec", f"{rem:.3f}"])
        if ctx.verbose:
            cmd.append("--verbose")
        return run_command(f"scenarios.parallel.{mode}", cmd, ctx, parse_json_stdout=True)
    return _run



def fuzz_parallel_step(mode_override: str | None = None) -> Callable[[HarnessContext], StepResult]:
    def _run(ctx: HarnessContext) -> StepResult:
        mode = mode_override or ctx.mode
        cmd = [
            sys.executable,
            "tools/run_fuzz.py",
            "--mode", mode,
            "--jobs", ctx.jobs,
            "--seed-base", str(ctx.fuzz_seed_base),
            "--seeds", str(ctx.fuzz_seeds),
            "--steps", str(ctx.fuzz_steps),
            "--fuzz-timeout-sec", f"{ctx.fuzz_timeout_sec:.3f}",
            "--report", str(REPORT_DIR / f"fuzz_parallel_{mode}_latest.json"),
            "--junit", str(REPORT_DIR / f"fuzz_parallel_{mode}_latest.xml"),
            "--json",
        ]
        if ctx.shuffle_seed is not None:
            cmd.extend(["--shuffle-seed", str(ctx.shuffle_seed)])
        rem = remaining_budget(ctx)
        if rem is not None:
            cmd.extend(["--budget-sec", f"{rem:.3f}"])
        if ctx.verbose:
            cmd.append("--verbose")
        return run_command(f"fuzz.parallel.{mode}", cmd, ctx, parse_json_stdout=True)
    return _run


def cpp_shards_step(ctx: HarnessContext) -> StepResult:
    cmd = [
        sys.executable,
        "tools/run_cpp_shards.py",
        "--mode", ctx.mode,
        "--shards", str(ctx.shard_count),
        "--jobs", "1",
        "--repeat", str(ctx.test_repeat),
        "--case-timeout-sec", f"{ctx.case_timeout_sec:.3f}",
        "--shard-strategy", ctx.shard_strategy,
        "--report", str(REPORT_DIR / "cpp_shards_latest.json"),
        "--junit", str(REPORT_DIR / "cpp_shards_latest.xml"),
        "--json",
    ]
    if ctx.test_filter:
        cmd.extend(["--filter", ctx.test_filter])
    if ctx.shuffle_seed is not None:
        cmd.extend(["--shuffle-seed", str(ctx.shuffle_seed)])
    rem = remaining_budget(ctx)
    if rem is not None:
        cmd.extend(["--budget-sec", f"{rem:.3f}"])
    if ctx.verbose:
        cmd.append("--verbose")
    return run_command("cpp.shards", cmd, ctx, parse_json_stdout=True)


def bench_turns_step(ctx: HarnessContext) -> StepResult:
    return run_command(
        "bench.turns",
        [
            str(executable("bench_turns", ctx.mode)),
            "--games", str(ctx.bench_games),
            "--pass-pairs", str(ctx.bench_passes),
            "--json",
        ],
        ctx,
        parse_json_stdout=True,
    )


def metrics_summary_step(ctx: HarnessContext) -> StepResult:
    if not ctx.record_sqlite:
        return StepResult(
            name="metrics.summary",
            status="skipped",
            duration_sec=0.0,
            metrics={"reason": "--no-sqlite disables SQLite summary step"},
        )
    return run_command("metrics.summary", [sys.executable, "tools/metrics_db.py", "summary", "--json"], ctx, parse_json_stdout=True)


def test_matrix_plan_step(ctx: HarnessContext) -> StepResult:
    cmd = [
        sys.executable,
        "tools/plan_test_matrix.py",
        "--mode", ctx.mode,
        "--report", str(REPORT_DIR / "test_matrix_plan_latest.json"),
        "--fuzz-seed-base", str(ctx.fuzz_seed_base),
        "--fuzz-seeds", str(ctx.fuzz_seeds),
        "--fuzz-steps", str(ctx.fuzz_steps),
        "--json",
    ]
    if ctx.shard_count > 1:
        cmd.extend(["--target-shards", str(ctx.shard_count)])
    return run_command("test.matrix_plan", cmd, ctx, parse_json_stdout=True)


PLANS: dict[str, list[Callable[[HarnessContext], StepResult]]] = {
    "audit": [audit_step],
    "rules": [rules_step, rules_progress_step],
    "cards": [card_catalog_step],
    "build": [build_step("all")],
    "plan-tests": [build_step("scenario"), build_step("tests"), test_matrix_plan_step],
    "quick": [rules_step, build_step("tests"), cpp_parallel_step()],
    "test": [rules_step, rules_progress_step, manifest_step, fuzz_runner_guard_step, card_catalog_step, build_step("tests"), cpp_parallel_step(), build_step("scenario"), scenario_parallel_step(), build_step("fuzz"), fuzz_parallel_step()],
    "scenarios": [build_step("scenario"), scenario_parallel_step()],
    "fuzz": [build_step("fuzz"), fuzz_parallel_step()],
    "bench": [build_step("bench"), bench_turns_step],
    "shards": [rules_step, build_step("tests"), cpp_shards_step],
    "all": [rules_step, rules_progress_step, manifest_step, fuzz_runner_guard_step, card_catalog_step, build_step("all"), audit_step, test_matrix_plan_step, cpp_parallel_step(), scenario_parallel_step(), fuzz_parallel_step(), bench_turns_step, metrics_summary_step],
    "matrix": [
        rules_step,
        rules_progress_step,
        manifest_step,
        fuzz_runner_guard_step,
        card_catalog_step,
        build_step("tests", "release"),
        cpp_parallel_step("release"),
        build_step("scenario", "release"),
        scenario_parallel_step("release"),
        build_step("fuzz", "release"),
        fuzz_parallel_step("release"),
        build_step("tests", "sanitize"),
        cpp_parallel_step("sanitize"),
        build_step("scenario", "sanitize"),
        scenario_parallel_step("sanitize"),
        build_step("fuzz", "sanitize"),
        fuzz_parallel_step("sanitize"),
        metrics_summary_step,
    ],
}

PLAN_NAMES: dict[str, list[str]] = {
    "audit": ["audit.datacube"],
    "rules": ["rules.coverage", "rules.progress"],
    "cards": ["cards.catalog"],
    "build": ["build.<mode>.all"],
    "plan-tests": ["build.<mode>.scenario", "build.<mode>.tests", "test.matrix_plan"],
    "quick": ["rules.coverage", "build.<mode>.tests", "cpp.parallel.<mode>"],
    "test": ["rules.coverage", "rules.progress", "python.manifest", "python.fuzz_runner", "cards.catalog", "build.<mode>.tests", "cpp.parallel.<mode>", "build.<mode>.scenario", "scenarios.parallel.<mode>", "build.<mode>.fuzz", "fuzz.parallel.<mode>"],
    "scenarios": ["build.<mode>.scenario", "scenarios.parallel.<mode>"],
    "fuzz": ["build.<mode>.fuzz", "fuzz.parallel.<mode>"],
    "bench": ["build.<mode>.bench", "bench.turns"],
    "shards": ["rules.coverage", "build.<mode>.tests", "cpp.shards"],
    "all": ["rules.coverage", "rules.progress", "python.manifest", "python.fuzz_runner", "cards.catalog", "build.<mode>.all", "audit.datacube", "test.matrix_plan", "cpp.parallel.<mode>", "scenarios.parallel.<mode>", "fuzz.parallel.<mode>", "bench.turns", "metrics.summary"],
    "matrix": ["rules.coverage", "rules.progress", "python.manifest", "python.fuzz_runner", "cards.catalog", "build.release.tests", "cpp.parallel.release", "build.release.scenario", "scenarios.parallel.release", "build.release.fuzz", "fuzz.parallel.release", "build.sanitize.tests", "cpp.parallel.sanitize", "build.sanitize.scenario", "scenarios.parallel.sanitize", "build.sanitize.fuzz", "fuzz.parallel.sanitize", "metrics.summary"],
}


def write_junit(path: pathlib.Path, results: list[StepResult]) -> None:
    suite = ET.Element("testsuite", {
        "name": "mtgsim_harness",
        "tests": str(len(results)),
        "failures": str(sum(1 for result in results if result.status == "failed")),
        "skipped": str(sum(1 for result in results if result.status == "skipped")),
        "time": f"{sum(result.duration_sec for result in results):.6f}",
    })
    for result in results:
        case = ET.SubElement(suite, "testcase", {"name": result.name, "time": f"{result.duration_sec:.6f}"})
        if result.status == "failed":
            failure = ET.SubElement(case, "failure", {"message": f"returncode={result.returncode}"})
            failure.text = (result.stderr_tail or result.stdout_tail)[:4000]
        elif result.status == "skipped":
            ET.SubElement(case, "skipped")
        if result.stdout_tail:
            stdout = ET.SubElement(case, "system-out")
            stdout.text = result.stdout_tail
        if result.stderr_tail:
            stderr = ET.SubElement(case, "system-err")
            stderr.text = result.stderr_tail
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(suite).write(path, encoding="utf-8", xml_declaration=True)


def run_plan(action: str, ctx: HarnessContext) -> tuple[int, dict[str, Any]]:
    results: list[StepResult] = []
    exit_code = 0
    for step in PLANS[action]:
        try:
            result = step(ctx)
        except HarnessBudgetExceeded as exc:
            result = StepResult(name="budget", status="failed", duration_sec=0.0, stderr_tail=str(exc), returncode=124)
        except FileNotFoundError as exc:
            result = StepResult(name="missing_executable", status="failed", duration_sec=0.0, stderr_tail=str(exc), returncode=127)
        results.append(result)
        print(f"[{result.name}] {result.status} in {result.duration_sec:.3f}s", flush=True)
        if result.status == "failed":
            exit_code = result.returncode or 1
            if not ctx.keep_going:
                break
    duration = time.perf_counter() - ctx.started_perf
    report = {
        "schema": "mtgsim.harness_report.v3",
        "created_at_local": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "action": action,
        "duration_sec": duration,
        "status": "passed" if exit_code == 0 else "failed",
        "system": {
            "platform": platform.platform(),
            "python": sys.version.split()[0],
            "cpu_count": os.cpu_count(),
        },
        "config": {
            "mode": ctx.mode,
            "jobs": ctx.jobs,
            "budget_sec": ctx.budget_sec,
            "keep_going": ctx.keep_going,
            "skip_build": ctx.skip_build,
            "bench_games": ctx.bench_games,
            "bench_passes": ctx.bench_passes,
            "test_repeat": ctx.test_repeat,
            "case_timeout_sec": ctx.case_timeout_sec,
            "fuzz_seed_base": ctx.fuzz_seed_base,
            "fuzz_seeds": ctx.fuzz_seeds,
            "fuzz_steps": ctx.fuzz_steps,
            "fuzz_timeout_sec": ctx.fuzz_timeout_sec,
            "test_filter": ctx.test_filter,
            "shuffle_seed": ctx.shuffle_seed,
            "record_sqlite": ctx.record_sqlite,
            "shard_count": ctx.shard_count,
            "shard_index": ctx.shard_index,
            "shard_strategy": ctx.shard_strategy,
        },
        "summary": {
            "steps": len(results),
            "passed": sum(1 for result in results if result.status == "passed"),
            "failed": sum(1 for result in results if result.status == "failed"),
            "skipped": sum(1 for result in results if result.status == "skipped"),
            "bench_metrics": next((result.metrics for result in results if result.name == "bench.turns"), {}),
            "cpp_metrics": {result.name: result.metrics.get("summary", {}) for result in results if result.name.startswith("cpp.parallel")},
            "scenario_metrics": {result.name: result.metrics.get("summary", {}) for result in results if result.name.startswith("scenarios.parallel")},
            "fuzz_metrics": {result.name: result.metrics.get("summary", {}) for result in results if result.name.startswith("fuzz.parallel")},
            "test_matrix_metrics": next((result.metrics.get("summary", {}) for result in results if result.name == "test.matrix_plan"), {}),
            "card_catalog_metrics": next((result.metrics.get("summary", {}) for result in results if result.name == "cards.catalog"), {}),
        },
        "steps": [asdict(result) for result in results],
    }
    return exit_code, report


def record_sqlite(report: dict[str, Any], report_path: pathlib.Path, enabled: bool) -> None:
    if not enabled:
        return
    try:
        sys.path.insert(0, str(ROOT / "tools"))
        import metrics_db  # type: ignore
        metrics_db.record_harness_report(report, report_path)
        build_report = ROOT / "reports" / "build" / "build_report_latest.json"
        if build_report.exists():
            metrics_db.record_build_report(json.loads(build_report.read_text(encoding="utf-8")), build_report)
    except Exception as exc:  # pragma: no cover - metrics must not mask build/test failures
        print(f"warning: unable to record harness report in sqlite: {exc}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["plan", *PLANS.keys()], nargs="?", default="all")
    parser.add_argument("--mode", choices=["debug", "release", "sanitize", "profile"], default="release")
    parser.add_argument("--jobs", default="auto")
    parser.add_argument("--budget-sec", type=float, default=None)
    parser.add_argument("--keep-going", action="store_true")
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument("--bench-games", type=int, default=2000)
    parser.add_argument("--bench-passes", type=int, default=24)
    parser.add_argument("--test-repeat", type=int, default=1)
    parser.add_argument("--case-timeout-sec", type=float, default=5.0)
    parser.add_argument("--fuzz-seed-base", type=int, default=7000)
    parser.add_argument("--fuzz-seeds", type=int, default=12)
    parser.add_argument("--fuzz-steps", type=int, default=120)
    parser.add_argument("--fuzz-timeout-sec", type=float, default=5.0)
    parser.add_argument("--test-filter", default="")
    parser.add_argument("--shuffle-seed", type=int, default=None)
    parser.add_argument("--shard-count", type=int, default=1)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--shard-strategy", choices=["round-robin", "hash", "duration-greedy"], default="round-robin")
    parser.add_argument("--no-sqlite", action="store_true", help="Do not append this run to reports/metrics/mtgsim_metrics.sqlite.")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--report", type=pathlib.Path, default=REPORT_DIR / "harness_report_latest.json")
    parser.add_argument("--junit", type=pathlib.Path, default=REPORT_DIR / "harness_junit_latest.xml")
    args = parser.parse_args(argv)

    if args.action == "plan":
        print("MTGSim harness plans:")
        for action, names in PLAN_NAMES.items():
            print(f"  {action}: " + " -> ".join(names))
        return 0
    if args.test_repeat <= 0:
        raise SystemExit("--test-repeat must be positive")
    if args.fuzz_seeds <= 0:
        raise SystemExit("--fuzz-seeds must be positive")
    if args.fuzz_steps <= 0:
        raise SystemExit("--fuzz-steps must be positive")
    if args.shard_count <= 0:
        raise SystemExit("--shard-count must be positive")
    if args.shard_index < 0 or args.shard_index >= args.shard_count:
        raise SystemExit("--shard-index must be in [0, --shard-count)")

    ctx = HarnessContext(
        mode=args.mode,
        jobs=args.jobs,
        budget_sec=args.budget_sec,
        started_perf=time.perf_counter(),
        keep_going=args.keep_going,
        verbose=args.verbose,
        skip_build=args.skip_build,
        bench_games=args.bench_games,
        bench_passes=args.bench_passes,
        test_repeat=args.test_repeat,
        case_timeout_sec=args.case_timeout_sec,
        fuzz_seed_base=args.fuzz_seed_base,
        fuzz_seeds=args.fuzz_seeds,
        fuzz_steps=args.fuzz_steps,
        fuzz_timeout_sec=args.fuzz_timeout_sec,
        test_filter=args.test_filter,
        shuffle_seed=args.shuffle_seed,
        record_sqlite=not args.no_sqlite,
        shard_count=args.shard_count,
        shard_index=args.shard_index,
        shard_strategy=args.shard_strategy,
    )
    exit_code, report = run_plan(args.action, ctx)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    append_jsonl(REPORT_DIR / "harness_history.jsonl", report)
    write_junit(args.junit, [StepResult(**step) for step in report["steps"]])
    record_sqlite(report, args.report, ctx.record_sqlite)
    print(f"harness {report['status']} in {report['duration_sec']:.3f}s; report={display_path(args.report)} junit={display_path(args.junit)}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
