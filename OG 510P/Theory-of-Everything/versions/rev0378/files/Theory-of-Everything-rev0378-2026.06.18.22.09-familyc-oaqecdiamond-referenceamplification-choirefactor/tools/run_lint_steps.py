#!/usr/bin/env python3
"""Run the archive lint path with explicit step timing and fail-fast progress.

This wrapper keeps `make lint` observable in small cloudtainers: each expensive
phase has a named start/end line and elapsed time, child output is staged in a
temporary file and flushed deterministically after completion, and every phase
has a hard timeout.  A file-backed log avoids pipe-EOF hangs when an imported
library or short-lived descendant inherits stdout, while preserving fail-fast
attribution and bounded parent memory.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import tempfile
import sys
import time
from pathlib import Path

# The cloudtainer's normal Python startup imports a large site stack before this
# tiny orchestrator runs.  Keeping that ~hundreds-of-MiB parent resident while
# schema/archive validators allocate their own working sets creates avoidable
# pressure.  Re-exec this orchestration process without site initialization;
# child validators still run with the normal interpreter and dependencies.
if not sys.flags.no_site and os.environ.get("TOE_LINT_NO_SITE_REEXEC") != "1":
    clean_env = dict(os.environ)
    clean_env["TOE_LINT_NO_SITE_REEXEC"] = "1"
    os.execve(
        sys.executable,
        [sys.executable, "-S", os.path.abspath(__file__), *sys.argv[1:]],
        clean_env,
    )

sys.dont_write_bytecode = True

from lint_steps_config import DEFAULT_LINT_STEPS


def run_step(root: Path, name: str, script_args: list[str]) -> None:
    cmd = [sys.executable, *script_args]
    start = time.monotonic()
    print(f"LINT STEP START {name}: {' '.join(cmd)}", flush=True)
    child_env = dict(os.environ)
    child_env["PYTHONDONTWRITEBYTECODE"] = "1"
    child_env["PYTHONUNBUFFERED"] = "1"
    timeout_s = 600
    with tempfile.TemporaryFile(mode="w+t", encoding="utf-8") as child_log:
        try:
            completed = subprocess.run(
                cmd,
                cwd=root,
                env=child_env,
                text=True,
                stdout=child_log,
                stderr=subprocess.STDOUT,
                timeout=timeout_s,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            child_log.flush()
            child_log.seek(0)
            output = child_log.read()
            if output:
                print(output, end="" if output.endswith("\n") else "\n", flush=True)
            elapsed = time.monotonic() - start
            print(f"LINT STEP TIMEOUT {name} elapsed={elapsed:.2f}s limit={timeout_s}s", flush=True)
            raise SystemExit(124) from exc
        child_log.flush()
        child_log.seek(0)
        output = child_log.read()
    if output:
        print(output, end="" if output.endswith("\n") else "\n", flush=True)
    elapsed = time.monotonic() - start
    if completed.returncode != 0:
        print(f"LINT STEP FAIL {name} elapsed={elapsed:.2f}s", flush=True)
        raise SystemExit(completed.returncode)
    print(f"LINT STEP OK {name} elapsed={elapsed:.2f}s", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-step", default="", help="start at the named step")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    steps = DEFAULT_LINT_STEPS
    if args.from_step:
        names = [name for name, _ in steps]
        if args.from_step not in names:
            print(f"unknown lint step {args.from_step!r}; known: {', '.join(names)}", file=sys.stderr)
            return 2
        steps = steps[names.index(args.from_step):]
    total_start = time.monotonic()
    for name, script_args in steps:
        run_step(root, name, script_args)
    print(f"LINT STEPS OK total_elapsed={time.monotonic() - total_start:.2f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
