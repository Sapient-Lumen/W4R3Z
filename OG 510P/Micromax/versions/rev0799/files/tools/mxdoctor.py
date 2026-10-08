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
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

FAST_PYTEST_TARGETS = [
    # Keep the default doctor lean: smoke/runtime sanity plus the highest-risk
    # handoff seams.  The broader suite belongs to --full/--chunked mxtest.
    "tests/test_smoke.py",
    "tests/test_stdlib_startup.py",
    "tests/test_mxdoctor.py",
    "tests/test_editor_fs_open_save.py",
    "tests/test_editor_fs_read.py",
    "tests/test_editor_fs_list.py",
    "tests/test_editor_fs_stat.py",
    "tests/test_editor_script_context_fs_caps.py",
    "tests/test_editor_state_clear_authority.py",
    "tests/test_editor_prompt_history_authority.py",
    "tests/test_editor_clipboard_authority.py",
    "tests/test_editor_recent_register_authority.py",
    "tests/test_editor_undo_authority.py",
    "tests/test_editor_highlight_and_timers.py",
    "tests/test_editor_persistence_cap_persist.py",
    "tests/test_editor_readonly_option.py",
    "tests/test_docs_index.py",
    "tests/test_editor_hostcall_state_argument_boundary.py",
    "tests/test_editor_hostcall_boundary.py",
    "tests/test_editor_hostcall_transactions.py",
    "tests/test_editor_with_undo_transaction.py",
    "tests/test_editor_help_docs_boundary.py",
    "tests/test_plugin_reload_recovery.py",
    "tests/test_plugin_containment_and_caps.py",
]

# Keep default preflight children bounded without spawning dozens of tiny pytest
# interpreters.  Constrained cloudtainers made the old one-file-per-child lane
# spend more time in subprocess/cache teardown than in the selected tests.  The
# explicit --full/--chunked lanes remain available for full-suite evidence.
PREFLIGHT_GROUP_SIZE = 3



def isolated_pytest_env() -> dict[str, str]:
    """Return an environment for deterministic local pytest runs.

    Host-level pytest plugin autoloading can make an otherwise boring archive
    behave differently across containers.  Keep doctor aligned with
    ``scripts/test.sh`` while allowing callers to opt back in explicitly.
    """

    env = os.environ.copy()
    env.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    env.setdefault("PYTHONDONTWRITEBYTECODE", "1")
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


def run(cmd: list[str], *, env: dict[str, str] | None = None) -> int:
    print("$", " ".join(cmd))
    sys.stdout.flush()
    return subprocess.call(cmd, cwd=str(ROOT), env=env)


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


def chunked_command(*, chunks: int = 8) -> list[str]:
    """Return the resumable mxtest command for full-suite evidence."""

    return [
        sys.executable,
        "tools/mxtest.py",
        "--run-chunks",
        str(max(1, int(chunks))),
        "--strategy",
        "segment",
        "--isolate-files",
        "--resume",
        "--json",
        ".artifacts/mxtest-all.json",
    ]


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
    ap.add_argument("--chunks", type=int, default=8, help="chunk count for --chunked (default: 8)")
    args = ap.parse_args(argv)

    print("micromax doctor")
    print("python:", sys.version.replace("\n", " "))
    print("platform:", platform.platform())
    print("cwd:", os.getcwd())
    print()

    rc = 0
    rc |= check_stdlib_resource()
    rc |= run([sys.executable, "tools/mxlint.py"])
    if args.chunked:
        print(f"pytest: full chunked suite via mxtest ({max(1, int(args.chunks))} chunks)")
        rc |= run(chunked_command(chunks=int(args.chunks)), env=isolated_pytest_env())
    else:
        if args.full:
            print("pytest: full suite requested via --full")
            rc |= run(pytest_command(full=True), env=isolated_pytest_env())
        else:
            print(
                "pytest: fast bounded preflight; use --full, --chunked, "
                "or make test-all-chunks for full-suite evidence"
            )
            for command in preflight_commands():
                rc |= run(command, env=isolated_pytest_env())
                if rc:
                    break

    warn_about_transient_caches()
    report_optional_tools()

    return int(bool(rc))


if __name__ == "__main__":
    raise SystemExit(main())
