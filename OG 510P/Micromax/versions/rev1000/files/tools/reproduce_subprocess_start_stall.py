#!/usr/bin/env python3
"""Reproduce a synchronous constructor stall and Micromax's finite handoff.

The witness deliberately injects a blocking constructor instead of relying on
``preexec_fn`` or platform-private process internals. Python documents
``preexec_fn`` as unsafe in threaded applications, so using it to manufacture a
real ``Popen`` deadlock would be the wrong production lesson.

The run proves four narrow properties: a raw synchronous constructor can remain
blocked; a deadline-owned caller returns; a second caller cannot accumulate
another unresolved starter; and late cleanup releases the gate for later work.
"""

from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass

from micromax.subprocess_start import (
    SubprocessStartTimeoutError,
    start_subprocess_with_deadline,
)

SCHEMA = "micromax.subprocess-start-stall-witness.v1"
_OBSERVATION_SECONDS = 0.05
_DEADLINE_SECONDS = 0.05
_RECOVERY_SECONDS = 2.0


@dataclass(frozen=True)
class _FakeProcess:
    label: str


def _wait(event: threading.Event, seconds: float, message: str) -> None:
    if not event.wait(max(0.0, float(seconds))):
        raise RuntimeError(message)


def run_witness(
    *,
    observation_seconds: float = _OBSERVATION_SECONDS,
    deadline_seconds: float = _DEADLINE_SECONDS,
) -> dict[str, object]:
    observation = max(0.001, float(observation_seconds))
    lease = max(0.001, float(deadline_seconds))

    # Control: direct synchronous ownership has no deadline seam.
    raw_entered = threading.Event()
    raw_release = threading.Event()
    raw_done = threading.Event()

    def raw_constructor() -> None:
        raw_entered.set()
        raw_release.wait()
        raw_done.set()

    raw_thread = threading.Thread(target=raw_constructor, daemon=True)
    raw_thread.start()
    _wait(raw_entered, _RECOVERY_SECONDS, "raw constructor did not enter")
    raw_still_blocked = not raw_done.wait(observation)
    raw_release.set()
    _wait(raw_done, _RECOVERY_SECONDS, "raw constructor did not recover")
    raw_thread.join(_RECOVERY_SECONDS)

    first_entered = threading.Event()
    release_first = threading.Event()
    first_cleanup = threading.Event()
    second_factory_calls = 0
    cleaned_labels: list[str] = []

    def first_factory() -> _FakeProcess:
        first_entered.set()
        release_first.wait()
        return _FakeProcess("late-first")

    def cleanup(process: _FakeProcess) -> None:
        cleaned_labels.append(process.label)
        first_cleanup.set()

    started = time.monotonic()
    first_timed_out = False
    try:
        start_subprocess_with_deadline(
            first_factory,
            cleanup=cleanup,
            deadline=started + lease,
            timeout_seconds=lease,
            operation="injected first Popen",
        )
    except SubprocessStartTimeoutError:
        first_timed_out = True
    first_elapsed = time.monotonic() - started
    _wait(first_entered, _RECOVERY_SECONDS, "bounded constructor did not enter")

    def second_factory() -> _FakeProcess:
        nonlocal second_factory_calls
        second_factory_calls += 1
        return _FakeProcess("unexpected-second")

    second_started = time.monotonic()
    second_timed_out = False
    try:
        start_subprocess_with_deadline(
            second_factory,
            cleanup=cleanup,
            deadline=second_started + lease,
            timeout_seconds=lease,
            operation="injected second Popen",
        )
    except SubprocessStartTimeoutError:
        second_timed_out = True
    second_elapsed = time.monotonic() - second_started

    release_first.set()
    _wait(first_cleanup, _RECOVERY_SECONDS, "late constructor cleanup did not finish")

    recovery_started = time.monotonic()
    recovered = start_subprocess_with_deadline(
        lambda: _FakeProcess("recovered"),
        cleanup=cleanup,
        deadline=recovery_started + max(lease, 0.25),
        timeout_seconds=max(lease, 0.25),
        operation="post-stall recovery Popen",
    )

    return {
        "schema": SCHEMA,
        "observation_seconds": observation,
        "deadline_seconds": lease,
        "raw_constructor_still_blocked": raw_still_blocked,
        "first_caller_timed_out": first_timed_out,
        "first_caller_elapsed_seconds": round(first_elapsed, 6),
        "second_caller_timed_out": second_timed_out,
        "second_caller_elapsed_seconds": round(second_elapsed, 6),
        "second_factory_calls": second_factory_calls,
        "late_cleanup_finished": first_cleanup.is_set(),
        "cleaned_labels": cleaned_labels,
        "later_start_recovered": recovered.label == "recovered",
    }


def main() -> int:
    result = run_witness()
    print(json.dumps(result, indent=2, sort_keys=True))
    passed = (
        result["raw_constructor_still_blocked"] is True
        and result["first_caller_timed_out"] is True
        and result["second_caller_timed_out"] is True
        and result["second_factory_calls"] == 0
        and result["late_cleanup_finished"] is True
        and result["later_start_recovered"] is True
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
