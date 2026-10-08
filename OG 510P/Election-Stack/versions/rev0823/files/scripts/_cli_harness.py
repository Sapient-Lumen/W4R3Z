#!/usr/bin/env python3
"""Small in-process CLI harness for release-gate drift tests.

The release gate itself keeps child checks isolated in subprocesses. Some child
checks, however, need to invoke repository-local Python CLIs many times or with
precise stdout/stderr assertions. This harness preserves the CLI contract inside
one child process by isolating argv, stdio, cwd, sys.path, and bytecode-writing
state around a ``runpy.run_path(..., run_name='__main__')`` call.

It is intentionally stdlib-only and is not a general test framework.
"""

from __future__ import annotations

import io
import os
import runpy
import sys
import traceback
from pathlib import Path
from typing import Iterable


def _coerce_exit_code(code: object) -> int:
    if code is None:
        return 0
    if isinstance(code, int):
        return code
    return 1


def run_python_cli(
    script: Path,
    args: Iterable[object] = (),
    *,
    extra_sys_path: Iterable[Path | str] = (),
    cwd: Path | None = None,
) -> tuple[int, str, str]:
    """Run a repository-local Python CLI in-process.

    Returns ``(exit_code, stdout, stderr)``. Exceptions are rendered to stderr
    and returned as exit code 1, matching the diagnostic posture expected by
    release-gate drift tests.
    """

    script = Path(script)
    if not script.is_file() or script.suffix != ".py":
        return 127, "", f"unsupported Python CLI script: {script}\n"

    old_argv = sys.argv[:]
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    old_path = sys.path[:]
    old_cwd = Path.cwd()
    old_dont_write = sys.dont_write_bytecode

    out = io.StringIO()
    err = io.StringIO()
    rc = 0

    try:
        sys.argv = [str(script)] + [str(a) for a in args]
        sys.stdout = out
        sys.stderr = err
        sys.dont_write_bytecode = True
        for entry in reversed([str(Path(p)) for p in extra_sys_path]):
            if entry and entry not in sys.path:
                sys.path.insert(0, entry)
        if cwd is not None:
            os.chdir(cwd)
        try:
            runpy.run_path(str(script), run_name="__main__")
            rc = 0
        except SystemExit as exc:
            rc = _coerce_exit_code(exc.code)
            if exc.code is not None and not isinstance(exc.code, int):
                print(exc.code, file=sys.stderr)
        except Exception:
            rc = 1
            traceback.print_exc(file=sys.stderr)
    finally:
        try:
            os.chdir(old_cwd)
        except Exception:
            pass
        sys.argv = old_argv
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        sys.path = old_path
        sys.dont_write_bytecode = old_dont_write

    return rc, out.getvalue(), err.getvalue()
