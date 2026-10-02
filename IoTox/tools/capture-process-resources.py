#!/usr/bin/env python3
"""Bind one process resource interval to monotonic time and IoTox cadence."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
from pathlib import Path


SCHEMA = "iotox-process-resource-interval-v1"


class CaptureError(RuntimeError):
    pass


def read_key_values(path: Path, separator: str) -> dict[str, int]:
    values: dict[str, int] = {}
    for line in path.read_text(encoding="ascii").splitlines():
        key, found, value = line.partition(separator)
        if not found:
            continue
        tokens = value.strip().split(maxsplit=1)
        if not tokens:
            continue
        token = tokens[0]
        try:
            values[key] = int(token)
        except ValueError:
            continue
    return values


def process_sample(pid: int, runtime_status: Path) -> dict[str, int]:
    proc = Path("/proc") / str(pid)
    stat_text = (proc / "stat").read_text(encoding="ascii")
    close = stat_text.rfind(")")
    if close < 2:
        raise CaptureError("process stat record is malformed")
    fields = stat_text[close + 2 :].split()
    if len(fields) < 22:
        raise CaptureError("process stat record is incomplete")
    status = read_key_values(proc / "status", ":")
    io = read_key_values(proc / "io", ":")
    runtime = read_key_values(runtime_status, "=")
    return {
        "monotonic-ns": time.monotonic_ns(),
        "process-start-ticks": int(fields[19]),
        "user-cpu-ticks": int(fields[11]),
        "system-cpu-ticks": int(fields[12]),
        "minor-faults": int(fields[7]),
        "major-faults": int(fields[9]),
        "resident-pages": int(fields[21]),
        "resident-high-water-kib": status.get("VmHWM", 0),
        "voluntary-context-switches": status.get("voluntary_ctxt_switches", 0),
        "involuntary-context-switches": status.get(
            "nonvoluntary_ctxt_switches", 0
        ),
        "read-bytes": io.get("read_bytes", 0),
        "write-bytes": io.get("write_bytes", 0),
        "open-descriptors": len(list((proc / "fd").iterdir())),
        "transport-iterations": runtime.get("transport-iteration-count", 0),
        "transport-requested-iteration-ms": runtime.get(
            "transport-requested-iteration-ms", 0
        ),
        "transport-effective-iteration-ms": runtime.get(
            "transport-effective-iteration-ms", 0
        ),
        "ratox-latency-mode-active": runtime.get(
            "ratox-latency-mode-active", 0
        ),
        "ratox-active-service-interval-ms": runtime.get(
            "ratox-active-service-interval-ms", 0
        ),
        "ratox-active-transport-iteration-interval-ms": runtime.get(
            "ratox-active-transport-iteration-interval-ms", 0
        ),
    }


def atomic_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "wb", closefd=True) as output:
            output.write(payload)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def begin(pid: int, runtime_status: Path, state_path: Path, role: str) -> None:
    record = {
        "schema": SCHEMA,
        "role": role,
        "pid": pid,
        "clock-ticks-per-second": os.sysconf("SC_CLK_TCK"),
        "page-size-bytes": os.sysconf("SC_PAGE_SIZE"),
        "start": process_sample(pid, runtime_status),
    }
    atomic_bytes(
        state_path,
        (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode(
            "ascii"
        ),
    )


def finish(pid: int, runtime_status: Path, state_path: Path, output: Path) -> None:
    state = json.loads(state_path.read_text(encoding="ascii"))
    if (
        state.get("schema") != SCHEMA
        or state.get("pid") != pid
        or not isinstance(state.get("start"), dict)
    ):
        raise CaptureError("resource interval state does not name this process")
    end = process_sample(pid, runtime_status)
    start = state["start"]
    if start.get("process-start-ticks") != end["process-start-ticks"]:
        raise CaptureError("resource interval crossed a process incarnation")

    delta_keys = (
        "monotonic-ns",
        "user-cpu-ticks",
        "system-cpu-ticks",
        "minor-faults",
        "major-faults",
        "voluntary-context-switches",
        "involuntary-context-switches",
        "read-bytes",
        "write-bytes",
        "transport-iterations",
    )
    lines = [
        f"schema\t{SCHEMA}",
        f"role\t{state['role']}",
        f"pid\t{pid}",
        f"process-start-ticks\t{end['process-start-ticks']}",
        f"clock-ticks-per-second\t{state['clock-ticks-per-second']}",
        f"page-size-bytes\t{state['page-size-bytes']}",
    ]
    for key in sorted(start):
        lines.append(f"start-{key}\t{start[key]}")
    for key in sorted(end):
        lines.append(f"end-{key}\t{end[key]}")
    for key in delta_keys:
        delta = end[key] - start[key]
        if delta < 0:
            raise CaptureError(f"resource counter moved backwards: {key}")
        lines.append(f"delta-{key}\t{delta}")
    atomic_bytes(output, ("\n".join(lines) + "\n").encode("ascii"))
    state_path.unlink()


def self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="iotox-resource-test-") as directory:
        root = Path(directory)
        status = root / "status"
        status.write_text(
            "transport-iteration-count=7\n"
            "transport-requested-iteration-ms=50\n"
            "transport-effective-iteration-ms=20\n"
            "ratox-latency-mode-active=0\n"
            "ratox-active-service-interval-ms=5\n"
            "ratox-active-transport-iteration-interval-ms=5\n",
            encoding="ascii",
        )
        state = root / "state.json"
        output = root / "result.tsv"
        begin(os.getpid(), status, state, "self")
        finish(os.getpid(), status, state, output)
        text = output.read_text(encoding="ascii")
        assert f"schema\t{SCHEMA}\n" in text
        assert "role\tself\n" in text
        assert "delta-monotonic-ns\t" in text
        assert not state.exists()
    print("process resource capture self-test: PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    subparsers = parser.add_subparsers(dest="command")
    for command in ("begin", "finish"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("--pid", type=int, required=True)
        subparser.add_argument("--runtime-status", type=Path, required=True)
        subparser.add_argument("--state", type=Path, required=True)
        if command == "begin":
            subparser.add_argument("--role", choices=("client", "device"), required=True)
        else:
            subparser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    if arguments.self_test:
        self_test()
        return 0
    if arguments.command is None:
        parser.error("begin or finish is required")
    try:
        if arguments.command == "begin":
            begin(
                arguments.pid,
                arguments.runtime_status,
                arguments.state,
                arguments.role,
            )
        else:
            finish(
                arguments.pid,
                arguments.runtime_status,
                arguments.state,
                arguments.output,
            )
    except (CaptureError, OSError, ValueError, KeyError) as error:
        print(f"process resource capture: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
