from __future__ import annotations

import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import build  # noqa: E402


def make_config(mode: str) -> build.BuildConfig:
    compile_flags, link_flags = build.compile_flags_for_mode(mode, native=False)
    return build.BuildConfig(
        cxx=sys.executable,
        mode=mode,
        native=False,
        build_dir=ROOT / "build" / "python-build-tool-test",
        target_names=("tests",),
        compile_flags=tuple(compile_flags),
        link_flags=tuple(link_flags),
        jobs=1,
        incremental=True,
        verbose=False,
        budget_sec=None,
        release_fast_build_opt_level="1",
        release_core_hotspot_opt_level="1",
        sanitize_validation_opt_level="0",
        sanitize_validation_debug_level="1",
    )


def check_sanitizer_validation_hotspot() -> None:
    config = make_config("sanitize")
    validation_flags = build.compile_flags_for_source(config, ROOT / "src" / "validation.cpp")
    engine_flags = build.compile_flags_for_source(config, ROOT / "src" / "engine.cpp")

    assert "-fsanitize=address,undefined" in validation_flags
    assert "-O0" in validation_flags and "-O1" not in validation_flags
    assert "-g1" in validation_flags and "-g3" not in validation_flags
    assert "-O1" in engine_flags and "-g3" in engine_flags


def check_hard_subprocess_timeout() -> None:
    begin = time.perf_counter()
    try:
        build.run_command(
            [sys.executable, "-c", "import time; time.sleep(5)"],
            ROOT,
            verbose=False,
            timeout_sec=0.1,
        )
    except build.BudgetExceeded:
        pass
    else:  # pragma: no cover - indicates the hard budget guard is broken
        raise AssertionError("run_command did not enforce timeout_sec")
    assert time.perf_counter() - begin < 2.0


def check_pre_action_budget() -> None:
    try:
        build.remaining_budget(time.perf_counter() - 2.0, 0.1, "unit-test action")
    except build.BudgetExceeded:
        return
    raise AssertionError("remaining_budget accepted an exhausted deadline")


def check_all_benchmark_sources_are_build_targets() -> None:
    benchmark_sources = {path.resolve() for path in (ROOT / "benchmarks").glob("*.cpp")}
    wired_sources = {
        source.resolve()
        for target_sources in build.TARGET_SOURCES.values()
        for source in target_sources
        if source.parent == ROOT / "benchmarks"
    }
    assert wired_sources == benchmark_sources, (
        f"benchmark build target drift: missing={sorted(map(str, benchmark_sources - wired_sources))} "
        f"extra={sorted(map(str, wired_sources - benchmark_sources))}"
    )


if __name__ == "__main__":
    check_sanitizer_validation_hotspot()
    check_hard_subprocess_timeout()
    check_pre_action_budget()
    check_all_benchmark_sources_are_build_targets()
    print("build tool guards ok")
