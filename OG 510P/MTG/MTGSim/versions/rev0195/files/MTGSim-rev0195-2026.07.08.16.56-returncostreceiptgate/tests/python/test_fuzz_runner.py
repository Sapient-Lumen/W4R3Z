from __future__ import annotations

import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import run_fuzz  # noqa: E402


def check_repro_command_builder() -> None:
    cmd = run_fuzz.fuzz_command(pathlib.Path("build/gcc-release/mtgsim_fuzz"), 7007, 42, "risk-seams", True)
    assert cmd == [
        "build/gcc-release/mtgsim_fuzz",
        "--seed",
        "7007",
        "--steps",
        "42",
        "--profile",
        "risk-seams",
        "--require-risk-seams",
        "--json",
    ]


def check_failure_step_shrinker_binary_searches() -> None:
    original = run_fuzz.failure_reproduces
    probes: list[int] = []

    def fake_failure(_exe: pathlib.Path, seed: int, steps: int, timeout_sec: float, profile: str, require_risk_seams: bool) -> tuple[bool, str, int]:
        assert seed == 9001
        assert timeout_sec == 1.0
        assert profile == "broad"
        assert require_risk_seams is False
        probes.append(steps)
        return steps >= 5, f"synthetic failure at steps={steps}", 2

    try:
        run_fuzz.failure_reproduces = fake_failure  # type: ignore[assignment]
        result = run_fuzz.FuzzResult(
            name="fuzz_seed_9001",
            seed=9001,
            status="failed",
            duration_sec=0.01,
            returncode=2,
            message="synthetic failure",
        )
        run_fuzz.shrink_failure_steps(
            exe=pathlib.Path("build/gcc-release/mtgsim_fuzz"),
            result=result,
            original_steps=16,
            timeout_sec=1.0,
            profile="broad",
            require_risk_seams=False,
            started=time.perf_counter(),
            budget_sec=None,
        )
    finally:
        run_fuzz.failure_reproduces = original  # type: ignore[assignment]

    assert result.shrink_status == "minimized"
    assert result.minimal_failing_steps == 5
    assert "--steps 5" in result.minimal_repro_command
    assert result.shrink_attempts == len(probes)
    assert 16 in probes


def check_repro_command_quotes_shell_sensitive_parts() -> None:
    rendered = run_fuzz.command_text([
        "build/gcc-release/mtgsim_fuzz",
        "--profile",
        "risk seam with spaces",
        "--json",
    ])
    assert "'risk seam with spaces'" in rendered


if __name__ == "__main__":
    check_repro_command_builder()
    check_failure_step_shrinker_binary_searches()
    check_repro_command_quotes_shell_sensitive_parts()
    print("fuzz runner guards ok")
