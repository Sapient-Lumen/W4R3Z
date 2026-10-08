#!/usr/bin/env python3
"""Reproduce raw ``Process.start()`` blocking and Micromax's finite handoff.

This is an evidence tool, not a product test.  It starts this script's private
forkserver, pauses that server with ``SIGSTOP``, and first calls raw
``Process.start()`` in a thread.  CPython's forkserver path must connect to the
server and request a child, so the call remains inside ``start()`` while the
server is paused.

The second pass routes the same injected stall through Micromax's one-shot
worker owner.  The caller returns at its startup deadline, ownership stays with
one starter thread, retries cannot accumulate another unresolved start, and the
late child is reclaimed after ``SIGCONT``.  The server is always resumed in a
``finally`` block.  Run only as a standalone POSIX process; private forkserver
PID lookup is intentionally confined to this fault injector.
"""

from __future__ import annotations

import multiprocessing as mp
import os
import signal
import sys
import threading
import time

from micromax.worker_process import (
    WorkerResultStartTimeoutError,
    collect_worker_result,
    create_one_shot_worker,
)

_OBSERVATION_SECONDS = 0.35
_STARTUP_DEADLINE_SECONDS = 0.10
_RECOVERY_SECONDS = 8.0


def _noop() -> None:
    return None


def _publish(sender: object) -> None:
    sender.put(("ok", os.getpid()))  # type: ignore[attr-defined]


def _private_forkserver_pid() -> int:
    # Private introspection is intentionally confined to this fault injector.
    from multiprocessing import forkserver

    server_pid = getattr(forkserver._forkserver, "_forkserver_pid", None)
    if not server_pid:
        raise RuntimeError("forkserver PID unavailable after warm-up")
    return int(server_pid)


def _warm_forkserver(context: mp.context.BaseContext) -> None:
    warm = context.Process(target=_noop)
    warm.start()
    warm.join(_RECOVERY_SECONDS)
    if warm.is_alive():
        warm.terminate()
        warm.join(1.0)
        raise RuntimeError("forkserver warm-up child did not exit")
    warm.close()


def _raw_start_stall(
    context: mp.context.BaseContext,
    *,
    server_pid: int,
) -> tuple[bool, dict[str, object]]:
    candidate = context.Process(target=_noop)
    completed = threading.Event()
    outcome: dict[str, object] = {}

    def start_candidate() -> None:
        started = time.monotonic()
        try:
            candidate.start()
            outcome["result"] = "started"
        except BaseException as exc:  # evidence reports every start outcome
            outcome["result"] = f"{type(exc).__name__}: {exc}"
        finally:
            outcome["elapsed_seconds"] = round(time.monotonic() - started, 6)
            completed.set()

    os.kill(server_pid, signal.SIGSTOP)
    starter = threading.Thread(target=start_candidate, daemon=True)
    starter.start()
    try:
        blocked = not completed.wait(_OBSERVATION_SECONDS)
    finally:
        os.kill(server_pid, signal.SIGCONT)

    if not completed.wait(_RECOVERY_SECONDS):
        raise RuntimeError("raw Process.start() did not recover after SIGCONT")
    starter.join(1.0)
    if candidate.pid is not None:
        candidate.join(_RECOVERY_SECONDS)
        if candidate.is_alive():
            candidate.terminate()
            candidate.join(1.0)
    candidate.close()
    return blocked, outcome


def _bounded_start_stall(
    context: mp.context.BaseContext,
    *,
    server_pid: int,
) -> dict[str, object]:
    process, channel = create_one_shot_worker(context, target=_publish)
    started = time.monotonic()
    timed_out = False
    message = ""

    os.kill(server_pid, signal.SIGSTOP)
    try:
        try:
            collect_worker_result(
                process,
                channel,
                timeout_seconds=2.0,
                startup_timeout_seconds=_STARTUP_DEADLINE_SECONDS,
                operation="paused forkserver witness",
                require_clean_exit=True,
            )
        except WorkerResultStartTimeoutError as exc:
            timed_out = True
            message = str(exc)
    finally:
        elapsed = time.monotonic() - started
        os.kill(server_pid, signal.SIGCONT)

    cleanup_deadline = time.monotonic() + _RECOVERY_SECONDS
    while channel.receiver.fileno() >= 0 and time.monotonic() < cleanup_deadline:
        time.sleep(0.01)
    late_cleanup_finished = channel.receiver.fileno() < 0

    # Prove the one-unresolved-start gate is released after late cleanup rather
    # than poisoning all later bounded work in this process.
    recovery_process, recovery_channel = create_one_shot_worker(
        context,
        target=_publish,
    )
    recovery_value = collect_worker_result(
        recovery_process,
        recovery_channel,
        timeout_seconds=2.0,
        startup_timeout_seconds=2.0,
        operation="post-stall recovery witness",
        require_clean_exit=True,
    )

    return {
        "startup_deadline_seconds": _STARTUP_DEADLINE_SECONDS,
        "caller_elapsed_seconds": round(elapsed, 6),
        "caller_timed_out": timed_out,
        "message": message,
        "late_cleanup_finished": late_cleanup_finished,
        "later_worker_recovered": (
            isinstance(recovery_value, tuple)
            and len(recovery_value) == 2
            and recovery_value[0] == "ok"
        ),
    }


def main() -> int:
    if os.name != "posix" or "forkserver" not in mp.get_all_start_methods():
        print("SKIP: forkserver/SIGSTOP reproduction requires POSIX forkserver")
        return 0

    context = mp.get_context("forkserver")
    _warm_forkserver(context)
    server_pid = _private_forkserver_pid()

    raw_blocked, raw_outcome = _raw_start_stall(
        context,
        server_pid=server_pid,
    )
    print(
        {
            "forkserver_pid": server_pid,
            "observation_seconds": _OBSERVATION_SECONDS,
            "raw_process_start_still_blocked": raw_blocked,
            "raw_outcome": raw_outcome,
        }
    )

    bounded = _bounded_start_stall(context, server_pid=server_pid)
    print(bounded)

    return 0 if (
        raw_blocked
        and raw_outcome.get("result") == "started"
        and bounded["caller_timed_out"] is True
        and bounded["late_cleanup_finished"] is True
        and bounded["later_worker_recovered"] is True
    ) else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyboardInterrupt, SystemExit):
        raise
    except BaseException as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
