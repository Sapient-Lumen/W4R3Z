#!/usr/bin/env python3
"""mxdoctor: a fast command that checks the repo is runnable.

This is aimed at future LLMs (and humans) picking up the archive.  By default it
runs a bounded preflight instead of the full pytest suite; use ``--full`` when
you want the expensive lane from this single command.
"""

from __future__ import annotations

import argparse
import os
import platform
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

FAST_PYTEST_TARGETS = [
    # Keep the default doctor lean: smoke/runtime sanity plus the highest-risk
    # handoff seams.  The broader suite belongs to --full/--chunked mxtest.
    "tests/test_smoke.py",
    "tests/test_stdlib_startup.py",
    "tests/test_mxdoctor.py::test_mxdoctor_default_preflight_command_is_bounded_risk_lane",
    "tests/test_editor_fs_open_save.py::test_ed_open_and_save_are_capability_gated",
    "tests/test_editor_fs_read.py::test_fs_read_is_capability_gated",
    "tests/test_editor_fs_list.py::test_fs_list_is_capability_gated",
    "tests/test_editor_fs_stat.py::test_fs_stat_is_capability_gated",
    "tests/test_editor_script_context_fs_caps.py::test_scripted_ed_command_cannot_bypass_cap_fs_open",
    "tests/test_editor_hostcall_state_argument_boundary.py",
    "tests/test_editor_timer_authority.py::test_ed_after_enforces_pending_timer_budget",
    "tests/test_editor_macro_authority.py::test_script_cannot_play_trusted_saved_macro_without_capability",
    "tests/test_plugin_containment_and_caps.py::test_plugin_callback_root_requires_current_generation_after_reload",
    "tests/test_plugin_containment_and_caps.py::test_plugin_reload_prunes_old_generation_macros_but_keeps_staged_macros",
    "tests/test_plugin_reload_recovery.py::test_plugin_reload_failure_cleans_staged_side_effects_and_keeps_old_runtime",
    "tests/test_mxtest.py::test_mxtest_run_chunks_max_new_chunks_writes_partial_manifest",
]

# Keep default preflight children bounded without spawning dozens of tiny pytest
# interpreters.  Constrained cloudtainers made the old broad lane spend more
# time in subprocess/cache teardown than in the selected tests.  The explicit
# --full/--chunked lanes remain available for full-suite evidence.
PREFLIGHT_GROUP_SIZE = 6
DEFAULT_TEST_MANIFEST = ".artifacts/mxtest-all-64.json"
DEFAULT_LINT_TIMEOUT_SECONDS = 120
DEFAULT_PREFLIGHT_TIMEOUT_SECONDS = 45
DEFAULT_CHUNKED_MAX_RUNTIME_SECONDS = 18.0
DEFAULT_CHUNKED_MAX_NEW_TESTS = 60
DEFAULT_CHUNKED_MAX_NEW_FILES = 4
DEFAULT_CHUNKED_TEST_BATCH_SIZE = 10
DEFAULT_CHUNKED_FILE_TIMEOUT_SECONDS = 45
NATIVE_THREAD_LIMIT_ENV_KEYS = [
    "OPENBLAS_NUM_THREADS",
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "BLIS_NUM_THREADS",
]


def isolated_pytest_env() -> dict[str, str]:
    """Return an environment for deterministic local pytest runs.

    Host-level pytest plugin autoloading can make an otherwise boring archive
    behave differently across containers.  Numeric libraries can also start one
    native thread per visible CPU in every pytest/forkserver interpreter.  Keep
    doctor aligned with ``scripts/test.sh`` while allowing explicit overrides.
    """

    env = os.environ.copy()
    env.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    env.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    for key in NATIVE_THREAD_LIMIT_ENV_KEYS:
        env.setdefault(key, "1")
    return env


def check_stdlib_resource() -> int:
    """Check that package-resource stdlib startup is visible and healthy."""

    if str(SRC) not in sys.path:
        sys.path.insert(0, str(SRC))
    from micromax import VM

    vm = VM(strict_stdlib=True)
    health = vm.stdlib_health()
    has_finally = vm.find_word("finally") is not None
    ok = bool(vm.stdlib_loaded and has_finally and health.get("state") == "loaded")
    state = health.get("state")
    if ok:
        print("stdlib: loaded package resource micromax/stdlib/core.mx")
        return 0
    print(f"stdlib: unhealthy state={state!r} health={health!r}")
    return 1


def timeout_seconds_from_env(name: str, default: int | None) -> int | None:
    """Return a positive timeout from an environment variable or default.

    A value of 0 disables the timeout for explicit long lanes such as
    ``--full``.  Invalid values fall back to the supplied default so an
    accidental typo does not silently unbound the default preflight.
    """

    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default if default is None or int(default) > 0 else None
    try:
        value = int(raw)
    except ValueError:
        return default if default is None or int(default) > 0 else None
    return value if value > 0 else None


def lint_timeout_seconds() -> int | None:
    """Return the mxlint child timeout used by doctor."""

    return timeout_seconds_from_env("MXDOCTOR_LINT_TIMEOUT_SECONDS", DEFAULT_LINT_TIMEOUT_SECONDS)


def preflight_timeout_seconds() -> int | None:
    """Return the per-pytest-child timeout used by the default doctor lane."""

    return timeout_seconds_from_env("MXDOCTOR_PREFLIGHT_TIMEOUT_SECONDS", DEFAULT_PREFLIGHT_TIMEOUT_SECONDS)


def full_timeout_seconds() -> int | None:
    """Return the optional full-suite pytest timeout used by doctor."""

    return timeout_seconds_from_env("MXDOCTOR_FULL_TIMEOUT_SECONDS", None)


def chunked_supervisor_timeout_seconds() -> int | None:
    """Return the optional outer timeout for the mxtest chunked lane."""

    return timeout_seconds_from_env("MXDOCTOR_CHUNKED_SUPERVISOR_TIMEOUT_SECONDS", None)


def default_test_manifest() -> str:
    """Return the aggregate manifest path shared with the handoff Makefile."""

    return os.environ.get("MXDOCTOR_TEST_MANIFEST") or DEFAULT_TEST_MANIFEST


def _confirmed_child_process_group_id(proc: subprocess.Popen[object]) -> int | None:
    """Return the child's separate POSIX process-group id when confirmed."""

    if os.name != "posix":
        return None
    pid = getattr(proc, "pid", None)
    if not isinstance(pid, int) or pid <= 0:
        return None
    try:
        pgid = os.getpgid(pid)
    except ProcessLookupError:
        return None
    except OSError:
        return None
    return int(pgid) if int(pgid) == int(pid) else None


def _signal_process_group_or_child(proc: subprocess.Popen[object], sig: int, *, pgid: int | None) -> None:
    """Signal only a confirmed child process group, else the direct child."""

    if os.name == "posix" and isinstance(pgid, int) and pgid > 0:
        try:
            os.killpg(pgid, sig)
            return
        except ProcessLookupError:
            return
        except OSError:
            pass
    if sig == signal.SIGTERM:
        proc.terminate()
    else:
        proc.kill()


def _process_group_exists(pgid: int | None) -> bool:
    """Return whether one confirmed doctor-child group still has members."""

    if os.name != "posix" or not isinstance(pgid, int) or pgid <= 0:
        return False
    try:
        if int(pgid) == int(os.getpgrp()):
            return False
        os.killpg(int(pgid), 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False


def _cleanup_residual_process_group(pgid: int | None) -> None:
    """Remove descendants left after a direct doctor child has returned."""

    if not _process_group_exists(pgid):
        return
    try:
        os.killpg(int(pgid), signal.SIGTERM)  # type: ignore[arg-type]
    except (ProcessLookupError, OSError, TypeError, ValueError):
        return
    deadline = time.monotonic() + 1.0
    while _process_group_exists(pgid) and time.monotonic() < deadline:
        time.sleep(0.02)
    if not _process_group_exists(pgid):
        return
    try:
        os.killpg(int(pgid), signal.SIGKILL)  # type: ignore[arg-type]
    except (ProcessLookupError, OSError, TypeError, ValueError):
        return


def _terminate_process_group(proc: subprocess.Popen[object], *, pgid: int | None = None) -> None:
    """Best-effort teardown for a timed-out doctor child."""

    if proc.poll() is not None:
        _cleanup_residual_process_group(pgid)
        return
    _signal_process_group_or_child(proc, signal.SIGTERM, pgid=pgid)
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        _signal_process_group_or_child(proc, signal.SIGKILL, pgid=pgid)
        proc.wait()
    _cleanup_residual_process_group(pgid)


def run(cmd: list[str], *, env: dict[str, str] | None = None, timeout: int | None = None) -> int:
    """Run a doctor child command with optional process-group timeout."""

    print("$", " ".join(cmd))
    if timeout is not None:
        print(f"doctor child timeout: {int(timeout)}s")
    sys.stdout.flush()
    popen_kwargs: dict[str, object] = {
        "cwd": str(ROOT),
        "env": env,
    }
    if os.name == "posix":
        popen_kwargs["start_new_session"] = True
    proc = subprocess.Popen(cmd, **popen_kwargs)
    child_pgid = _confirmed_child_process_group_id(proc)
    try:
        try:
            return int(proc.wait(timeout=timeout))
        except subprocess.TimeoutExpired:
            print(f"doctor: child timed out after {int(timeout or 0)}s", file=sys.stderr)
            _terminate_process_group(proc, pgid=child_pgid)
            return 124
    finally:
        _cleanup_residual_process_group(child_pgid)


def pytest_command(*, full: bool) -> list[str]:
    """Return the plain pytest command used by the explicit full lane."""

    cmd = [sys.executable, "-m", "pytest", "-q"]
    if not full:
        # Keep capture disabled in the handoff preflight.  Several risk-lane
        # tests intentionally exercise subprocess cleanup; inheriting pytest's
        # capture file descriptors can make successful child cleanup look like a
        # hung or signaled outer command in constrained cloudtainers.
        cmd.extend(["-s", "-p", "no:cacheprovider"])
        cmd.extend(FAST_PYTEST_TARGETS)
    return cmd


def _preflight_base_command() -> list[str]:
    """Return the pytest argv prefix shared by bounded doctor children."""

    return [sys.executable, "-m", "pytest", "-q", "-s", "-p", "no:cacheprovider"]


def _chunked_targets(targets: list[str], *, size: int) -> list[list[str]]:
    """Return stable groups of pytest selectors for the default preflight."""

    step = max(1, int(size))
    return [targets[i : i + step] for i in range(0, len(targets), step)]


def preflight_group_size() -> int:
    """Return the default doctor pytest-child grouping size.

    Operators can set ``MXDOCTOR_PREFLIGHT_GROUP_SIZE=1`` to bisect a fragile
    file, or a larger value to reduce interpreter churn.  Invalid values fall
    back to the conservative archive default.
    """

    raw = os.environ.get("MXDOCTOR_PREFLIGHT_GROUP_SIZE", "")
    if not raw:
        return PREFLIGHT_GROUP_SIZE
    try:
        value = int(raw)
    except ValueError:
        return PREFLIGHT_GROUP_SIZE
    return max(1, value)


def preflight_commands() -> list[list[str]]:
    """Return bounded default preflight commands.

    This intentionally stays a smoke-plus-risk-surface lane, not a growing
    miniature full suite.  Splitting the selected files across a few pytest
    children makes the default handoff command less fragile in constrained
    cloudtainers while keeping ``--chunked`` as the full-evidence runway.
    """

    return [_preflight_base_command() + group for group in _chunked_targets(FAST_PYTEST_TARGETS, size=preflight_group_size())]


def preflight_command() -> list[str]:
    """Return the historical single-process bounded preflight command.

    Kept for tests/tooling that want to inspect the full selected target set.
    ``main()`` uses ``preflight_commands()`` for the more robust grouped lane.
    """

    return pytest_command(full=False)


def chunked_max_runtime_seconds_from_env() -> float:
    """Return the default graceful runtime budget for the chunked lane.

    Constrained cloudtainers can externally terminate long children before
    mxtest reaches its own checkpoint boundary.  Keep the default chunked lane
    short and graceful, while allowing explicit local override with 0.
    """

    raw = os.environ.get("MXDOCTOR_CHUNKED_MAX_RUNTIME_SECONDS")
    if raw is None or raw == "":
        return DEFAULT_CHUNKED_MAX_RUNTIME_SECONDS
    try:
        return max(0.0, float(raw))
    except ValueError:
        return DEFAULT_CHUNKED_MAX_RUNTIME_SECONDS


def chunked_command(
    *,
    chunks: int = 64,
    manifest: str | None = None,
    max_runtime_seconds: float | None = None,
    max_new_tests: int | None = None,
    max_new_files: int | None = None,
    test_batch_size: int | None = None,
    file_timeout: int | None = None,
) -> list[str]:
    """Return the resumable mxtest command for full-suite evidence."""

    cmd = [
        sys.executable,
        "tools/mxtest.py",
        "--run-chunks",
        str(max(1, int(chunks))),
        "--strategy",
        "segment",
        "--isolate-files",
        "--resume",
        "--checkpoint-tests",
        "--max-new-tests",
        str(max(0, int(DEFAULT_CHUNKED_MAX_NEW_TESTS if max_new_tests is None else max_new_tests))),
        "--max-new-files",
        str(max(0, int(DEFAULT_CHUNKED_MAX_NEW_FILES if max_new_files is None else max_new_files))),
        "--test-batch-size",
        str(max(0, int(DEFAULT_CHUNKED_TEST_BATCH_SIZE if test_batch_size is None else test_batch_size))),
        "--file-timeout",
        str(max(0, int(DEFAULT_CHUNKED_FILE_TIMEOUT_SECONDS if file_timeout is None else file_timeout))),
        "--json",
        manifest or default_test_manifest(),
    ]
    default_budget = chunked_max_runtime_seconds_from_env()
    requested_budget = default_budget if max_runtime_seconds is None else float(max_runtime_seconds)
    budget = max(0.0, requested_budget)
    if budget:
        cmd.extend(["--max-runtime-seconds", str(budget)])
    return cmd


def warn_about_transient_caches() -> None:
    """Print archive-hygiene hints for transient local caches."""

    transient = []
    probes = (
        (".pytest_cache", (".pytest_cache",)),
        ("__pycache__", ("__pycache__", "src/__pycache__", "tests/__pycache__", "tools/__pycache__")),
        (".mypy_cache", (".mypy_cache",)),
        (".ruff_cache", (".ruff_cache",)),
        ("build", ("build",)),
        ("src/micromax.egg-info", ("src/micromax.egg-info",)),
    )
    for label, rels in probes:
        if any((ROOT / rel).exists() for rel in rels):
            transient.append(label)
    if transient:
        print("warning: transient caches present:", ", ".join(transient))
        print("         run: make pack   (to build a clean zip archive)")


def report_optional_tools() -> None:
    """Report optional developer tools without failing doctor."""

    for opt in ("ruff", "mypy"):
        try:
            subprocess.check_output([opt, "--version"], stderr=subprocess.STDOUT)
            print(f"found: {opt}")
        except Exception:
            print(f"missing: {opt} (optional)")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="check that the Micromax repo is runnable")
    lane = ap.add_mutually_exclusive_group()
    lane.add_argument(
        "--full",
        action="store_true",
        help="run the full pytest suite after lint instead of the bounded preflight set",
    )
    lane.add_argument(
        "--chunked",
        action="store_true",
        help="run the full suite through the resumable mxtest aggregate runway",
    )
    ap.add_argument("--chunks", type=int, default=64, help="chunk count for --chunked (default: 64)")
    ap.add_argument("--manifest", default=default_test_manifest(), help="mxtest manifest for --chunked")
    ap.add_argument("--max-runtime-seconds", type=float, default=None, help="mxtest wall-clock budget for --chunked (default: 25; pass 0 to disable)")
    ap.add_argument("--max-new-tests", type=int, default=DEFAULT_CHUNKED_MAX_NEW_TESTS, help="new test budget per --chunked invocation (default: 60; 0 disables)")
    ap.add_argument("--max-new-files", type=int, default=DEFAULT_CHUNKED_MAX_NEW_FILES, help="new file budget per --chunked invocation (default: 4; 0 disables)")
    ap.add_argument("--test-batch-size", type=int, default=DEFAULT_CHUNKED_TEST_BATCH_SIZE, help="per-file test batch size for --chunked (default: 10; use 1 for slow files)")
    ap.add_argument("--file-timeout", type=int, default=DEFAULT_CHUNKED_FILE_TIMEOUT_SECONDS, help="per-file timeout for --chunked isolated pytest children (default: 45; 0 disables)")
    args = ap.parse_args(argv)

    print("micromax doctor")
    print("python:", sys.version.replace("\n", " "))
    print("platform:", platform.platform())
    print("cwd:", os.getcwd())
    print()

    rc = 0
    rc |= check_stdlib_resource()
    rc |= run([sys.executable, "tools/mxlint.py"], timeout=lint_timeout_seconds())
    if args.chunked:
        print(f"pytest: full chunked suite via mxtest ({max(1, int(args.chunks))} chunks)")
        rc |= run(
            chunked_command(
                chunks=int(args.chunks),
                manifest=str(args.manifest),
                max_runtime_seconds=args.max_runtime_seconds,
                max_new_tests=args.max_new_tests,
                max_new_files=args.max_new_files,
                test_batch_size=args.test_batch_size,
                file_timeout=args.file_timeout,
            ),
            env=isolated_pytest_env(),
            timeout=chunked_supervisor_timeout_seconds(),
        )
    else:
        if args.full:
            print("pytest: full suite requested via --full")
            rc |= run(pytest_command(full=True), env=isolated_pytest_env(), timeout=full_timeout_seconds())
        else:
            print(
                "pytest: fast bounded preflight; use --full, --chunked, "
                "or make test-all-chunks for full-suite evidence"
            )
            for command in preflight_commands():
                rc |= run(command, env=isolated_pytest_env(), timeout=preflight_timeout_seconds())
                if rc:
                    break

    warn_about_transient_caches()
    report_optional_tools()

    return int(bool(rc))


if __name__ == "__main__":
    raise SystemExit(main())
