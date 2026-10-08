#!/usr/bin/env python3
"""Timed, decomposable GCC-first build helper for MTGSim.

Design goals:
- no non-stdlib Python dependencies;
- object-level incremental rebuilds with command/dependency fingerprints;
- per-action timing reports for continuous optimization;
- target-level decomposition for cloud containers with tight wall-clock budgets.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import pathlib
import platform
import signal
import shlex
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from typing import Iterable

# Reports should use the project/user timezone for readable revision artifacts.
os.environ.setdefault("TZ", "America/New_York")
if hasattr(time, "tzset"):
    time.tzset()

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "build"

CORE_SOURCES = [
    ROOT / "src" / "types.cpp",
    ROOT / "src" / "rng.cpp",
    ROOT / "src" / "engine.cpp",
    ROOT / "src" / "validation.cpp",
    ROOT / "src" / "rules.cpp",
]

TARGET_SOURCES = {
    "tests": [ROOT / "tests" / "cpp" / "test_engine.cpp"],
    "scenario": [ROOT / "apps" / "mtgsim_scenario.cpp"],
    "fuzz": [ROOT / "apps" / "mtgsim_fuzz.cpp"],
    "cli": [ROOT / "apps" / "mtgsim_cli.cpp"],
    "bench": [ROOT / "benchmarks" / "bench_turns.cpp"],
    "bench-branch": [ROOT / "benchmarks" / "bench_branch_clearall.cpp"],
    "bench-frontier": [ROOT / "benchmarks" / "bench_legal_action_frontier.cpp"],
}

TARGET_OUTPUTS = {
    "tests": "mtgsim_tests",
    "scenario": "mtgsim_scenario",
    "fuzz": "mtgsim_fuzz",
    "cli": "mtgsim_cli",
    "bench": "bench_turns",
    "bench-branch": "bench_branch_clearall",
    "bench-frontier": "bench_legal_action_frontier",
}


class BudgetExceeded(RuntimeError):
    pass


@dataclass
class ActionRecord:
    name: str
    command: list[str]
    duration_sec: float
    status: str
    returncode: int | None = None
    stdout_tail: str = ""
    stderr_tail: str = ""
    skipped: bool = False


@dataclass(frozen=True)
class BuildConfig:
    cxx: str
    mode: str
    native: bool
    build_dir: pathlib.Path
    target_names: tuple[str, ...]
    compile_flags: tuple[str, ...]
    link_flags: tuple[str, ...]
    jobs: int
    incremental: bool
    verbose: bool
    budget_sec: float | None
    release_fast_build_opt_level: str | None
    release_core_hotspot_opt_level: str | None
    sanitize_validation_opt_level: str | None
    sanitize_validation_debug_level: str | None


def rel(path: pathlib.Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def tail(text: str, limit: int = 4000) -> str:
    return text[-limit:] if len(text) > limit else text


def digest_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def source_to_object(build_dir: pathlib.Path, source: pathlib.Path) -> pathlib.Path:
    safe = rel(source).replace("/", "__").replace("..", "__")
    return build_dir / "obj" / f"{safe}.o"


def depfile_for_object(obj: pathlib.Path) -> pathlib.Path:
    return obj.with_suffix(obj.suffix + ".d")


def hashfile_for_output(output: pathlib.Path) -> pathlib.Path:
    return output.with_suffix(output.suffix + ".cmdhash") if output.suffix else output.with_name(output.name + ".cmdhash")


def command_hash(cmd: Iterable[str]) -> str:
    return digest_text("\0".join(cmd))


def normalize_opt_flag(raw: str | None) -> str | None:
    """Normalize an optimization-level knob into a compiler flag.

    The release harness can lower optimization on compile-time hotspots while
    keeping release semantics. This protects validation loops in small cloud
    containers where glue-heavy units, validation, and occasionally the large
    engine reducer translation unit can dominate wall-clock time.
    """
    if raw is None:
        return None
    value = raw.strip()
    if not value or value.lower() in {"none", "default"}:
        return None
    if value.startswith("-O"):
        return value
    if value in {"0", "1", "2", "3", "s", "z", "g", "fast"}:
        return f"-O{value}"
    raise ValueError(f"invalid optimization level {raw!r}; use 0,1,2,3,s,z,g,fast,default,or a -O* flag")


def normalize_debug_flag(raw: str | None) -> str | None:
    """Normalize a debug-information knob into a compiler flag."""
    if raw is None:
        return None
    value = raw.strip()
    if not value or value.lower() in {"none", "default"}:
        return None
    if value.startswith("-g"):
        return value
    if value in {"0", "1", "2", "3"}:
        return f"-g{value}"
    raise ValueError(f"invalid debug level {raw!r}; use 0,1,2,3,default,or a -g* flag")


def compile_flags_for_source(config: BuildConfig, source: pathlib.Path) -> list[str]:
    flags = list(config.compile_flags)
    rel_source = rel(source)
    is_executable_driver = rel_source.startswith(("tests/", "apps/", "benchmarks/"))
    is_validation_hotspot = rel_source == "src/validation.cpp"
    is_engine_hotspot = rel_source == "src/engine.cpp"
    if config.mode == "sanitize" and is_validation_hotspot:
        # GCC's optimizer plus full -g3 debug information makes this large,
        # branch-heavy validator translation unit disproportionately expensive
        # in small cloud containers. ASan/UBSan instrumentation remains enabled;
        # only this unit defaults to the cheaper O0/g1 compile posture.
        opt_flag = normalize_opt_flag(config.sanitize_validation_opt_level)
        debug_flag = normalize_debug_flag(config.sanitize_validation_debug_level)
        if opt_flag is not None:
            flags = [flag for flag in flags if not flag.startswith("-O")]
            flags.append(opt_flag)
        if debug_flag is not None:
            flags = [flag for flag in flags if not flag.startswith("-g")]
            flags.append(debug_flag)
    elif config.mode == "release" and is_engine_hotspot:
        opt_flag = normalize_opt_flag(config.release_core_hotspot_opt_level)
        if opt_flag is not None:
            flags = [flag for flag in flags if not flag.startswith("-O")]
            flags.append(opt_flag)
    elif config.mode == "release" and (is_executable_driver or is_validation_hotspot):
        opt_flag = normalize_opt_flag(config.release_fast_build_opt_level)
        if opt_flag is not None:
            flags = [flag for flag in flags if not flag.startswith("-O")]
            flags.append(opt_flag)
    return flags


def read_make_depfile(depfile: pathlib.Path) -> list[pathlib.Path]:
    if not depfile.exists():
        return []
    text = depfile.read_text(encoding="utf-8", errors="replace")
    text = text.replace("\\\n", " ")
    if ":" in text:
        text = text.split(":", 1)[1]
    deps: list[pathlib.Path] = []
    for raw in text.split():
        if not raw:
            continue
        deps.append((ROOT / raw).resolve() if not pathlib.Path(raw).is_absolute() else pathlib.Path(raw))
    return deps


def is_outdated(output: pathlib.Path, hashfile: pathlib.Path, expected_hash: str, deps: Iterable[pathlib.Path]) -> bool:
    if not output.exists() or not hashfile.exists():
        return True
    if hashfile.read_text(encoding="utf-8", errors="replace").strip() != expected_hash:
        return True
    out_mtime = output.stat().st_mtime
    for dep in deps:
        if dep.exists() and dep.stat().st_mtime > out_mtime:
            return True
    return False


def remaining_budget(start: float, budget_sec: float | None, next_action: str) -> float | None:
    if budget_sec is None:
        return None
    elapsed = time.perf_counter() - start
    remaining = budget_sec - elapsed
    if remaining <= 0.0:
        raise BudgetExceeded(f"time budget {budget_sec:.2f}s exceeded before {next_action}; elapsed={elapsed:.3f}s")
    return remaining


def check_budget(start: float, budget_sec: float | None, next_action: str) -> None:
    """Compatibility wrapper for callers that only need a pre-action check."""
    remaining_budget(start, budget_sec, next_action)


def run_command(cmd: list[str], cwd: pathlib.Path, verbose: bool, timeout_sec: float | None = None) -> ActionRecord:
    display = " ".join(shlex.quote(part) for part in cmd)
    print("+", display, flush=True)
    begin = time.perf_counter()
    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=(os.name == "posix"),
    )
    try:
        stdout, stderr = proc.communicate(timeout=timeout_sec)
    except subprocess.TimeoutExpired as exc:
        if os.name == "posix":
            # Kill the compiler driver and descendants such as cc1plus. Killing
            # only the immediate g++ process can leave an orphan consuming the
            # cloudtainer after the advertised build budget has expired.
            os.killpg(proc.pid, signal.SIGKILL)
        else:  # pragma: no cover - the linked-revision cloudtainer is POSIX
            proc.kill()
        stdout, stderr = proc.communicate()
        duration = time.perf_counter() - begin
        raise BudgetExceeded(
            f"time budget expired during {display}; command_elapsed={duration:.3f}s"
        ) from exc
    duration = time.perf_counter() - begin
    if verbose and stdout:
        print(stdout, end="")
    if stderr:
        print(stderr, end="", file=sys.stderr)
    status = "passed" if proc.returncode == 0 else "failed"
    return ActionRecord(
        name=cmd[0],
        command=cmd,
        duration_sec=duration,
        status=status,
        returncode=proc.returncode,
        stdout_tail=tail(stdout),
        stderr_tail=tail(stderr),
    )


def compile_flags_for_mode(mode: str, native: bool) -> tuple[list[str], list[str]]:
    compile_flags = [
        "-std=c++20",
        "-Wall",
        "-Wextra",
        "-Wpedantic",
        "-Wconversion",
        "-Wshadow",
        "-fdiagnostics-color=always",
    ]
    link_flags: list[str] = []
    if mode == "release":
        compile_flags.extend(["-O3", "-DNDEBUG"])
    elif mode == "debug":
        compile_flags.extend(["-O0", "-g3"])
    elif mode == "sanitize":
        compile_flags.extend(["-O1", "-g3", "-fsanitize=address,undefined", "-fno-omit-frame-pointer"])
        link_flags.extend(["-fsanitize=address,undefined"])
    elif mode == "profile":
        compile_flags.extend(["-O3", "-g", "-fno-omit-frame-pointer"])
    else:
        raise ValueError(f"unknown build mode: {mode}")
    if native:
        compile_flags.append("-march=native")
    return compile_flags, link_flags


def normalize_targets(target: str) -> tuple[str, ...]:
    if target == "all":
        return tuple(TARGET_SOURCES)
    if target not in TARGET_SOURCES:
        raise ValueError(f"unknown target: {target}")
    return (target,)


def plan_sources(targets: Iterable[str]) -> list[pathlib.Path]:
    ordered: list[pathlib.Path] = []
    seen: set[pathlib.Path] = set()
    for src in CORE_SOURCES:
        if src not in seen:
            ordered.append(src)
            seen.add(src)
    for target in targets:
        for src in TARGET_SOURCES[target]:
            if src not in seen:
                ordered.append(src)
                seen.add(src)
    return ordered


def compile_one(config: BuildConfig, source: pathlib.Path, started_at: float) -> tuple[pathlib.Path, ActionRecord]:
    timeout_sec = remaining_budget(started_at, config.budget_sec, f"compile {rel(source)}")
    obj = source_to_object(config.build_dir, source)
    depfile = depfile_for_object(obj)
    hashfile = hashfile_for_output(obj)
    obj.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        config.cxx,
        *compile_flags_for_source(config, source),
        "-Iinclude",
        "-MMD",
        "-MP",
        "-MF",
        rel(depfile),
        "-c",
        rel(source),
        "-o",
        rel(obj),
    ]
    expected_hash = command_hash(cmd)
    deps = [source, *read_make_depfile(depfile)]
    if config.incremental and not is_outdated(obj, hashfile, expected_hash, deps):
        return obj, ActionRecord(
            name=f"compile {rel(source)}",
            command=cmd,
            duration_sec=0.0,
            status="skipped",
            skipped=True,
        )
    action = run_command(cmd, ROOT, config.verbose, timeout_sec=timeout_sec)
    action.name = f"compile {rel(source)}"
    if action.returncode != 0:
        return obj, action
    hashfile.write_text(expected_hash + "\n", encoding="utf-8")
    return obj, action


def link_target(config: BuildConfig, target: str, objects: list[pathlib.Path], started_at: float) -> ActionRecord:
    timeout_sec = remaining_budget(started_at, config.budget_sec, f"link {target}")
    exe = config.build_dir / TARGET_OUTPUTS[target]
    exe.parent.mkdir(parents=True, exist_ok=True)
    hashfile = hashfile_for_output(exe)
    cmd = [config.cxx, *[rel(obj) for obj in objects], *config.link_flags, "-o", rel(exe)]
    expected_hash = command_hash(cmd)
    if config.incremental and not is_outdated(exe, hashfile, expected_hash, objects):
        return ActionRecord(
            name=f"link {target}",
            command=cmd,
            duration_sec=0.0,
            status="skipped",
            skipped=True,
        )
    action = run_command(cmd, ROOT, config.verbose, timeout_sec=timeout_sec)
    action.name = f"link {target}"
    if action.returncode == 0:
        hashfile.write_text(expected_hash + "\n", encoding="utf-8")
    return action


def write_compile_commands(config: BuildConfig, sources: list[pathlib.Path]) -> None:
    entries = []
    for source in sources:
        obj = source_to_object(config.build_dir, source)
        cmd = [
            config.cxx,
            *compile_flags_for_source(config, source),
            "-Iinclude",
            "-c",
            rel(source),
            "-o",
            rel(obj),
        ]
        entries.append({
            "directory": str(ROOT),
            "command": " ".join(shlex.quote(part) for part in cmd),
            "file": str(source),
            "output": str(obj),
        })
    (config.build_dir / "compile_commands.json").write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")


def append_jsonl(path: pathlib.Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def build(config: BuildConfig) -> dict:
    start = time.perf_counter()
    wall_started = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    config.build_dir.mkdir(parents=True, exist_ok=True)
    sources = plan_sources(config.target_names)
    write_compile_commands(config, sources)

    actions: list[ActionRecord] = []
    object_by_source: dict[pathlib.Path, pathlib.Path] = {}
    print(f"Build mode={config.mode} targets={','.join(config.target_names)} jobs={config.jobs} incremental={config.incremental}")

    if config.jobs == 1:
        for source in sources:
            obj, action = compile_one(config, source, start)
            actions.append(action)
            object_by_source[source] = obj
            if action.status == "failed":
                raise subprocess.CalledProcessError(action.returncode or 1, action.command)
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=config.jobs) as executor:
            futures = {executor.submit(compile_one, config, source, start): source for source in sources}
            for future in concurrent.futures.as_completed(futures):
                source = futures[future]
                obj, action = future.result()
                actions.append(action)
                object_by_source[source] = obj
                if action.status == "failed":
                    # Drain already-completed jobs, then fail. This keeps reports useful while avoiding unsafe links.
                    raise subprocess.CalledProcessError(action.returncode or 1, action.command)

    # Keep report deterministic-ish: sorted compiles by source path, links in target order.
    actions.sort(key=lambda action: action.name)

    core_objects = [object_by_source[src] for src in CORE_SOURCES]
    for target in config.target_names:
        target_objects = core_objects + [object_by_source[src] for src in TARGET_SOURCES[target]]
        action = link_target(config, target, target_objects, start)
        actions.append(action)
        if action.status == "failed":
            raise subprocess.CalledProcessError(action.returncode or 1, action.command)

    elapsed = time.perf_counter() - start
    report = {
        "schema": "mtgsim.build_report.v2",
        "started_at_local": wall_started,
        "duration_sec": elapsed,
        "root": str(ROOT),
        "system": {
            "platform": platform.platform(),
            "python": sys.version.split()[0],
        },
        "config": {
            "cxx": config.cxx,
            "mode": config.mode,
            "native": config.native,
            "build_dir": rel(config.build_dir),
            "targets": list(config.target_names),
            "compile_flags": list(config.compile_flags),
            "link_flags": list(config.link_flags),
            "jobs": config.jobs,
            "incremental": config.incremental,
            "budget_sec": config.budget_sec,
            "release_fast_build_opt_level": config.release_fast_build_opt_level,
            "release_core_hotspot_opt_level": config.release_core_hotspot_opt_level,
            "sanitize_validation_opt_level": config.sanitize_validation_opt_level,
            "sanitize_validation_debug_level": config.sanitize_validation_debug_level,
        },
        "summary": {
            "actions": len(actions),
            "compiled": sum(1 for action in actions if action.name.startswith("compile") and not action.skipped),
            "linked": sum(1 for action in actions if action.name.startswith("link") and not action.skipped),
            "skipped": sum(1 for action in actions if action.skipped),
        },
        "actions": [asdict(action) for action in actions],
    }
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    latest = REPORT_DIR / "build_report_latest.json"
    latest.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    append_jsonl(REPORT_DIR / "build_history.jsonl", report)
    try:
        sys.path.insert(0, str(ROOT / "tools"))
        import metrics_db  # type: ignore
        metrics_db.record_build_report(report, latest)
    except Exception as exc:  # pragma: no cover - metrics must not mask build failures
        print(f"warning: unable to record build report in sqlite: {exc}", file=sys.stderr)
    print(f"Built artifacts in {rel(config.build_dir)} in {elapsed:.3f}s; report={rel(latest)}")
    return report


def parse_positive_env_int(name: str, default: int) -> int:
    raw = os.environ.get(name, str(default))
    try:
        return max(1, int(raw))
    except ValueError:
        return default


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["debug", "release", "sanitize", "profile"], default="release")
    parser.add_argument("--target", choices=["all", *TARGET_SOURCES.keys()], default="all")
    parser.add_argument("--cxx", default=os.environ.get("CXX", "g++"))
    parser.add_argument("--native", action="store_true", help="Add -march=native for local benchmarking builds.")
    parser.add_argument("--jobs", default="auto", help="Compile parallelism: auto or an integer.")
    parser.add_argument("--clean", action="store_true", help="Remove the selected build directory before building.")
    parser.add_argument("--no-incremental", action="store_true", help="Force recompilation/relinking.")
    parser.add_argument("--time-budget-sec", type=float, default=None, help="Enforce a hard wall-clock deadline across compile and link subprocesses.")
    parser.add_argument(
        "--release-fast-build-opt-level",
        "--release-driver-opt-level",
        "--release-test-opt-level",
        dest="release_fast_build_opt_level",
        default=os.environ.get(
            "MTGSIM_RELEASE_FAST_BUILD_OPT_LEVEL",
            os.environ.get("MTGSIM_RELEASE_DRIVER_OPT_LEVEL", os.environ.get("MTGSIM_RELEASE_TEST_OPT_LEVEL", "1")),
        ),
        help="Optimization level for release-mode compile-time hotspots: validation plus executable driver translation units. Default 1 avoids O3 cloud-container stalls; use 3 to restore full release optimization for those files.",
    )
    parser.add_argument(
        "--release-core-hotspot-opt-level",
        "--release-engine-opt-level",
        dest="release_core_hotspot_opt_level",
        default=os.environ.get("MTGSIM_RELEASE_CORE_HOTSPOT_OPT_LEVEL", os.environ.get("MTGSIM_RELEASE_ENGINE_OPT_LEVEL", "1")),
        help="Optimization level for release-mode core hotspot src/engine.cpp. Default 1 keeps clean linked-revision builds practical; use 3 for full performance-oriented release optimization.",
    )
    parser.add_argument(
        "--sanitize-validation-opt-level",
        default=os.environ.get("MTGSIM_SANITIZE_VALIDATION_OPT_LEVEL", "0"),
        help="Optimization level for sanitizer-mode src/validation.cpp. Default 0 avoids pathological GCC sanitizer compile time while retaining ASan/UBSan instrumentation.",
    )
    parser.add_argument(
        "--sanitize-validation-debug-level",
        default=os.environ.get("MTGSIM_SANITIZE_VALIDATION_DEBUG_LEVEL", "1"),
        help="Debug-information level for sanitizer-mode src/validation.cpp. Default 1 retains line information without the cloud cost of -g3.",
    )
    parser.add_argument("--verbose", action="store_true", help="Print captured stdout for compiler commands.")
    args = parser.parse_args(argv)

    compile_flags, link_flags = compile_flags_for_mode(args.mode, args.native)
    targets = normalize_targets(args.target)
    if args.jobs == "auto":
        jobs = max(1, min(os.cpu_count() or 1, parse_positive_env_int("MTGSIM_BUILD_AUTO_JOBS", 8), len(plan_sources(targets))))
    else:
        jobs = max(1, int(args.jobs))
    build_dir = ROOT / "build" / f"gcc-{args.mode}"
    if args.clean and build_dir.exists():
        shutil.rmtree(build_dir)

    config = BuildConfig(
        cxx=args.cxx,
        mode=args.mode,
        native=args.native,
        build_dir=build_dir,
        target_names=targets,
        compile_flags=tuple(compile_flags),
        link_flags=tuple(link_flags),
        jobs=jobs,
        incremental=not args.no_incremental,
        verbose=args.verbose,
        budget_sec=args.time_budget_sec,
        release_fast_build_opt_level=args.release_fast_build_opt_level,
        release_core_hotspot_opt_level=args.release_core_hotspot_opt_level,
        sanitize_validation_opt_level=args.sanitize_validation_opt_level,
        sanitize_validation_debug_level=args.sanitize_validation_debug_level,
    )
    try:
        build(config)
    except BudgetExceeded as exc:
        print(f"BUILD BUDGET EXCEEDED: {exc}", file=sys.stderr)
        return 124
    except subprocess.CalledProcessError as exc:
        print(f"BUILD FAILED: {' '.join(map(shlex.quote, exc.cmd if isinstance(exc.cmd, list) else [str(exc.cmd)]))}", file=sys.stderr)
        return exc.returncode or 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
