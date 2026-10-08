from __future__ import annotations

"""Finite process boundary for the platform web-browser launcher."""

from dataclasses import dataclass
from pathlib import Path
import math
import sys

from .host_process import run_argv_bounded


DEFAULT_OPEN_URL_TIMEOUT_SECONDS = 6.0
DEFAULT_OPEN_URL_OUTPUT_BYTES = 16_384


@dataclass(frozen=True)
class OpenUrlProcessResult:
    ok: bool
    reason: str
    returncode: int
    timed_out: bool = False
    output_truncated: bool = False


def _positive_timeout(value: object) -> float:
    if isinstance(value, bool):
        return DEFAULT_OPEN_URL_TIMEOUT_SECONDS
    try:
        parsed = float(value)
    except (TypeError, ValueError, OverflowError):
        return DEFAULT_OPEN_URL_TIMEOUT_SECONDS
    if not math.isfinite(parsed) or parsed <= 0:
        return DEFAULT_OPEN_URL_TIMEOUT_SECONDS
    return parsed


def _nonnegative_output_limit(value: object) -> int:
    if isinstance(value, bool):
        return DEFAULT_OPEN_URL_OUTPUT_BYTES
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        return DEFAULT_OPEN_URL_OUTPUT_BYTES
    if parsed < 0:
        return DEFAULT_OPEN_URL_OUTPUT_BYTES
    return parsed


def open_external_url_bounded(
    url: str,
    *,
    timeout_seconds: object = DEFAULT_OPEN_URL_TIMEOUT_SECONDS,
    max_output_bytes: object = DEFAULT_OPEN_URL_OUTPUT_BYTES,
    python_executable: str | None = None,
) -> OpenUrlProcessResult:
    """Open ``url`` outside the editor process under one finite launch deadline.

    The child runs with isolated-path and no-site startup before importing only
    the standard-library ``webbrowser`` module.  It is
    started through :func:`run_argv_bounded`, which gives it a new process group,
    caps diagnostic output, and tears down same-group descendants when a
    text-mode browser or platform launcher outlives the deadline.
    """

    child = Path(__file__).with_name("open_url_child.py")
    executable = str(python_executable or sys.executable or "").strip()
    if not executable:
        return OpenUrlProcessResult(False, "open-url helper: Python executable unavailable", 127)

    timeout = _positive_timeout(timeout_seconds)
    output_limit = _nonnegative_output_limit(max_output_bytes)
    result = run_argv_bounded(
        [executable, "-I", "-S", str(child), str(url)],
        timeout_seconds=timeout,
        max_output_bytes=output_limit,
        label="open-url helper",
    )
    if result.returncode == 0 and not result.timed_out and not result.output_truncated:
        return OpenUrlProcessResult(True, "", 0)

    reason = str(result.stderr or "").strip()
    if not reason:
        if result.returncode < 0:
            reason = f"open-url helper: terminated by signal {-result.returncode}"
        else:
            reason = f"open-url helper: browser launch failed ({result.returncode})"
    return OpenUrlProcessResult(
        False,
        reason,
        int(result.returncode),
        timed_out=bool(result.timed_out),
        output_truncated=bool(result.output_truncated),
    )
