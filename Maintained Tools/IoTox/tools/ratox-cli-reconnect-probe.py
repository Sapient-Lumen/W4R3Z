#!/usr/bin/env python3
"""Qualify one production Ratox CLI process across genuine route loss.

The probe deliberately drives the installed ``iotox terminal --reconnect``
client through a pseudoterminal.  It does not speak the private terminal socket
protocol.  A parent Sandwurm harness owns the route fault and releases each
phase through owner-only checkpoint files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pty
import re
import select
import signal
import subprocess
import sys
import time
from pathlib import Path


HEX_KEY = re.compile(r"[0-9A-Fa-f]{64}")
SESSION_BANNER = re.compile(rb"Ratox session=([0-9A-F]{32}) ")
RECONNECT_WAIT = (
    b"Ratox reconnect: waiting for the exact retained session on a higher "
    b"authenticated epoch"
)
RECONNECT_RESUMED = re.compile(
    rb"Ratox reconnect: resumed exact session generation=([0-9]+) "
    rb"attempts=([0-9]+)"
)
HEARTBEAT_WARNING = (
    b"Ratox heartbeat: remote attachment is unresponsive; session retained "
    b"for authoritative route loss or manual detach"
)


class ProbeError(RuntimeError):
    pass


def monotonic_us() -> int:
    return time.monotonic_ns() // 1000


def atomic_text(path: Path, value: str) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(value, encoding="ascii")
    os.chmod(temporary, 0o600)
    os.replace(temporary, path)


def atomic_json(path: Path, value: dict[str, object]) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    os.chmod(temporary, 0o600)
    os.replace(temporary, path)


def key_values(output: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in output.splitlines():
        for field in line.split():
            if "=" in field:
                key, value = field.split("=", 1)
                values.setdefault(key, value)
    return values


def invoke(binary: str, runtime: Path, *arguments: str, timeout: float) -> str:
    try:
        completed = subprocess.run(
            [binary, "--runtime", str(runtime), *arguments],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise ProbeError(f"iotox {' '.join(arguments)} failed: {error}") from error
    if completed.returncode != 0:
        raise ProbeError(
            f"iotox {' '.join(arguments)} returned {completed.returncode}: "
            f"{completed.stderr.strip()}"
        )
    return completed.stdout


def observation(
    binary: str, runtime: Path, peer_hex: str, timeout: float
) -> dict[str, str | int]:
    session_output = invoke(binary, runtime, "session", peer_hex, timeout=timeout)
    session = key_values(session_output)
    authority = key_values(
        invoke(binary, runtime, "authority-session", peer_hex, timeout=timeout)
    )
    peer: dict[str, str] = {}
    for line in invoke(binary, runtime, "peers", timeout=timeout).splitlines():
        candidate = key_values(line)
        if candidate.get("public-key", "").upper() == peer_hex.upper():
            peer = candidate
            break
    epoch = session.get("online-epoch", "0")
    if not epoch.isdecimal():
        raise ProbeError("session online epoch is not canonical decimal")
    return {
        "session_state": session.get("state", "absent"),
        "online_epoch": int(epoch),
        "connection": peer.get("connection", "absent"),
        "capability_observed": int("ratox-interactive-v1" in session_output),
        "claimant_proof_sent": int(authority.get("claimant-state") == "proof-sent"),
        "claimant_principal_present": int(
            re.fullmatch(
                r"[0-9A-Fa-f]{64}",
                authority.get("local-claimant-principal", ""),
            )
            is not None
            and authority.get("local-claimant-principal") != "0" * 64
        ),
    }


def client_snapshot(
    binary: str, runtime: Path, peer_hex: str, timeout: float
) -> dict[str, str | int]:
    decimal = ("incarnation", "generation", "next-input", "output-base", "output-next")
    deadline = time.monotonic() + timeout
    last_output = ""
    while time.monotonic() < deadline:
        last_output = invoke(
            binary,
            runtime,
            "terminal-sessions",
            peer_hex,
            timeout=max(0.1, deadline - time.monotonic()),
        )
        values = key_values(last_output)
        if (
            values
            and all(values.get(key, "").isdecimal() for key in decimal)
            and re.fullmatch(r"[0-9A-F]{32}", values.get("session", ""))
            is not None
        ):
            return {
                "session": values["session"],
                "state": values.get("state", "absent"),
                **{key.replace("-", "_"): int(values[key]) for key in decimal},
            }
        time.sleep(0.02)
    detail = last_output.encode("ascii", "backslashreplace").hex()
    raise ProbeError(
        "production client session snapshot remained absent or malformed; "
        f"last-output-hex={detail}"
    )


def process_start_ticks(pid: int) -> int:
    try:
        record = Path(f"/proc/{pid}/stat").read_text(encoding="ascii")
    except OSError as error:
        raise ProbeError(f"cannot inspect production CLI process identity: {error}") from error
    end = record.rfind(")")
    fields = record[end + 2 :].split()
    if end < 1 or len(fields) < 20 or not fields[19].isdecimal():
        raise ProbeError("production CLI process identity is malformed")
    return int(fields[19])


class PseudoTerminalProcess:
    def __init__(self, argv: list[str]):
        pid, descriptor = pty.fork()
        if pid == 0:
            try:
                os.execvp(argv[0], argv)
            except OSError:
                os._exit(127)
        self.pid = pid
        self.descriptor = descriptor
        os.set_blocking(descriptor, False)
        self.output = bytearray()
        self.cursor = 0
        self.wait_status: int | None = None

    def drain(self, timeout: float) -> int:
        readable, _, _ = select.select([self.descriptor], [], [], timeout)
        if not readable:
            return monotonic_us()
        while True:
            try:
                chunk = os.read(self.descriptor, 65536)
            except BlockingIOError:
                break
            except OSError:
                break
            if not chunk:
                break
            self.output.extend(chunk)
            if len(self.output) > 1024 * 1024:
                raise ProbeError("production CLI output exceeded the bounded capture")
        return monotonic_us()

    def wait_bytes(self, needle: bytes, timeout: float) -> int:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            found = bytes(self.output).find(needle, self.cursor)
            if found >= 0:
                self.cursor = found + len(needle)
                return monotonic_us()
            self.require_running()
            self.drain(min(0.1, max(0.0, deadline - time.monotonic())))
        raise ProbeError(f"production CLI did not emit expected marker {needle!r}")

    def wait_pattern(self, pattern: re.Pattern[bytes], timeout: float) -> re.Match[bytes]:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            found = pattern.search(bytes(self.output), self.cursor)
            if found is not None:
                self.cursor = found.end()
                return found
            self.require_running()
            self.drain(min(0.1, max(0.0, deadline - time.monotonic())))
        raise ProbeError("production CLI did not emit the expected structured marker")

    def prove_quiet_liveness(self, duration: float) -> tuple[int, int]:
        started = monotonic_us()
        baseline = len(self.output)
        deadline = time.monotonic() + duration
        while time.monotonic() < deadline:
            self.require_running()
            self.drain(min(0.1, max(0.0, deadline - time.monotonic())))
            if HEARTBEAT_WARNING in self.output[baseline:]:
                raise ProbeError("production CLI heartbeat warned on a healthy route")
        return started, monotonic_us()

    def discard_matchable_output(self) -> None:
        self.drain(0.05)
        self.cursor = len(self.output)

    def write(self, payload: bytes) -> None:
        offset = 0
        while offset < len(payload):
            try:
                written = os.write(self.descriptor, payload[offset:])
            except BlockingIOError:
                select.select([], [self.descriptor], [], 0.1)
                continue
            if written <= 0:
                raise ProbeError("production CLI pseudoterminal accepted no input")
            offset += written

    def poll(self) -> int | None:
        if self.wait_status is not None:
            return os.waitstatus_to_exitcode(self.wait_status)
        pid, status = os.waitpid(self.pid, os.WNOHANG)
        if pid == 0:
            return None
        self.wait_status = status
        return os.waitstatus_to_exitcode(status)

    def require_running(self) -> None:
        result = self.poll()
        if result is not None:
            raise ProbeError(f"production CLI exited early with status {result}")

    def wait(self, timeout: float) -> int:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            self.drain(0.05)
            result = self.poll()
            if result is not None:
                return result
        raise ProbeError("production CLI did not exit after local detach")

    def terminate(self) -> None:
        if self.poll() is None:
            try:
                os.kill(self.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            deadline = time.monotonic() + 2.0
            while time.monotonic() < deadline and self.poll() is None:
                time.sleep(0.02)
            if self.poll() is None:
                try:
                    os.kill(self.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                os.waitpid(self.pid, 0)
        try:
            os.close(self.descriptor)
        except OSError:
            pass


def await_release(directory: Path, name: str, timeout: float) -> int:
    path = directory / name
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            path.unlink()
            return monotonic_us()
        except FileNotFoundError:
            time.sleep(0.01)
    raise ProbeError(f"phase release {name} did not arrive")


def checkpoint(directory: Path, name: str, session: str) -> None:
    atomic_text(
        directory / name,
        "\n".join(
            (
                "schema\tiotox-ratox-cli-reconnect-checkpoint-v1",
                f"phase\t{name}",
                "session-sha256\t"
                + hashlib.sha256(bytes.fromhex(session)).hexdigest(),
                "",
            )
        ),
    )


def run(args: argparse.Namespace) -> None:
    if HEX_KEY.fullmatch(args.peer) is None:
        raise ProbeError("peer must be exactly 64 hexadecimal characters")
    if args.expected_connection not in {"udp", "tcp"}:
        raise ProbeError("expected connection must be udp or tcp")
    runtime = args.runtime.resolve()
    timeout = args.timeout_ms / 1000.0
    process = PseudoTerminalProcess(
        [
            args.iotox,
            "--runtime",
            str(runtime),
            "--timeout-ms",
            str(min(args.timeout_ms, 60000)),
            "terminal",
            args.peer,
            "--reconnect",
        ]
    )
    started_us = monotonic_us()
    start_ticks = process_start_ticks(process.pid)
    capture_rows: list[str] = []
    heartbeat_rows: list[str] = []
    success = False
    try:
        banner = process.wait_pattern(SESSION_BANNER, timeout)
        session = banner.group(1).decode("ascii")
        process.discard_matchable_output()
        initial_before = client_snapshot(args.iotox, runtime, args.peer, 10.0)
        initial_observation = observation(args.iotox, runtime, args.peer, 10.0)
        if not (
            initial_before["session"] == session
            and initial_before["state"] == "attached"
            and initial_before["incarnation"] > 0
            and initial_before["generation"] == 1
            and initial_before["next_input"] == 1
            and initial_before["output_next"] == 1
            and initial_observation["session_state"] == "confirmed"
            and initial_observation["connection"] == args.expected_connection
            and initial_observation["online_epoch"] > 0
            and initial_observation["capability_observed"] == 1
            and initial_observation["claimant_proof_sent"] == 1
            and initial_observation["claimant_principal_present"] == 1
        ):
            raise ProbeError("production CLI initial attachment is not exact and authenticated")

        initial_started = monotonic_us()
        process.write(b"\n")
        initial_returned = process.wait_bytes(b"\n", timeout)
        initial_after = client_snapshot(args.iotox, runtime, args.peer, 10.0)
        if not (
            initial_after["session"] == session
            and initial_after["incarnation"] == initial_before["incarnation"]
            and initial_after["generation"] == 1
            and initial_after["next_input"] == 2
            and initial_after["output_next"] == 2
        ):
            raise ProbeError("production CLI initial byte position is not exactly committed")
        capture_rows.append(
            f"sample\t1\t{initial_started}\t{initial_returned}\t{initial_returned}"
            f"\t{session.lower()}\t1\t2\t1\t2\t0"
        )
        healthy_start, healthy_end = process.prove_quiet_liveness(3.5)
        heartbeat_rows.append(
            f"sample\t1\t{healthy_start}\t{healthy_end}\t{session.lower()}"
        )
        checkpoint(args.checkpoint_dir, "client.ratox-route-loss-attached", session)

        transitions: list[dict[str, object]] = []
        previous_observation = initial_observation
        for ordinal in range(1, args.interruptions + 1):
            suffix = "" if ordinal == 1 else f"-{ordinal}"
            loss_release_us = await_release(
                args.release_dir, f"ratox-route-loss-active{suffix}", timeout
            )
            heartbeat_warning_us = process.wait_bytes(HEARTBEAT_WARNING, timeout)
            heartbeat_loss = observation(args.iotox, runtime, args.peer, 10.0)
            if not (
                heartbeat_loss["session_state"] == "confirmed"
                and heartbeat_loss["connection"] == args.expected_connection
                and heartbeat_loss["online_epoch"]
                == previous_observation["online_epoch"]
            ):
                raise ProbeError(
                    "production heartbeat warning did not precede route authority loss"
                )
            checkpoint(
                args.checkpoint_dir,
                f"client.ratox-route-loss-heartbeat-missed{suffix}",
                session,
            )

            reconnect_wait_us = process.wait_bytes(RECONNECT_WAIT, timeout)
            offline_deadline = time.monotonic() + timeout
            offline: dict[str, str | int] = {}
            while time.monotonic() < offline_deadline:
                offline = observation(args.iotox, runtime, args.peer, 10.0)
                if (
                    offline["session_state"] == "offline"
                    and offline["connection"] == "offline"
                ):
                    break
                process.require_running()
                time.sleep(0.05)
            if (
                offline.get("session_state") != "offline"
                or offline.get("connection") != "offline"
            ):
                raise ProbeError(
                    "production reconnect wait has no authoritative offline state"
                )
            detached = client_snapshot(args.iotox, runtime, args.peer, 10.0)
            retained_sequence = ordinal + 1
            if not (
                detached["session"] == session
                and detached["state"] == "detached"
                and detached["incarnation"] == initial_before["incarnation"]
                and detached["generation"] == ordinal
                and detached["next_input"] == retained_sequence
                and detached["output_next"] == retained_sequence
            ):
                raise ProbeError(
                    "production reconnect wait did not retain the exact detached session"
                )
            checkpoint(
                args.checkpoint_dir,
                f"client.ratox-route-loss-offline{suffix}",
                session,
            )

            recovery_release_us = await_release(
                args.release_dir, f"ratox-route-loss-recover{suffix}", timeout
            )
            resumed = process.wait_pattern(RECONNECT_RESUMED, timeout)
            resume_opened_us = monotonic_us()
            process.discard_matchable_output()
            resumed_generation = int(resumed.group(1))
            retry_attempts = int(resumed.group(2))
            recovered_observation = observation(
                args.iotox, runtime, args.peer, 10.0
            )
            recovered_before = client_snapshot(
                args.iotox, runtime, args.peer, 10.0
            )
            expected_generation = ordinal + 1
            if not (
                resumed_generation == expected_generation
                and retry_attempts > 0
                and recovered_before["session"] == session
                and recovered_before["state"] == "attached"
                and recovered_before["incarnation"]
                == initial_before["incarnation"]
                and recovered_before["generation"] == expected_generation
                and recovered_before["next_input"] == retained_sequence
                and recovered_before["output_next"] == retained_sequence
                and recovered_observation["session_state"] == "confirmed"
                and recovered_observation["connection"]
                == args.expected_connection
                and recovered_observation["online_epoch"]
                > previous_observation["online_epoch"]
                and recovered_observation["capability_observed"] == 1
                and recovered_observation["claimant_proof_sent"] == 1
                and recovered_observation["claimant_principal_present"] == 1
            ):
                raise ProbeError(
                    "production CLI did not resume the exact session on a higher epoch"
                )

            recovered_heartbeat_start, recovered_heartbeat_end = (
                process.prove_quiet_liveness(3.5)
            )
            sample = ordinal + 1
            heartbeat_rows.append(
                f"sample\t{sample}\t{recovered_heartbeat_start}"
                f"\t{recovered_heartbeat_end}\t{session.lower()}"
            )
            recovered_started = monotonic_us()
            process.write(b"\n")
            recovered_returned = process.wait_bytes(b"\n", timeout)
            recovered_after = client_snapshot(
                args.iotox, runtime, args.peer, 10.0
            )
            next_sequence = ordinal + 2
            if not (
                recovered_after["session"] == session
                and recovered_after["incarnation"]
                == initial_before["incarnation"]
                and recovered_after["generation"] == expected_generation
                and recovered_after["next_input"] == next_sequence
                and recovered_after["output_next"] == next_sequence
            ):
                raise ProbeError(
                    "production CLI recovered byte position is not exactly committed"
                )
            capture_rows.append(
                f"sample\t{sample}\t{recovered_started}\t{recovered_returned}"
                f"\t{recovered_returned}\t{session.lower()}"
                f"\t{retained_sequence}\t{next_sequence}"
                f"\t{retained_sequence}\t{next_sequence}\t0"
            )
            transition = {
                "ordinal": ordinal,
                "loss": {
                    "release_us": loss_release_us,
                    "heartbeat_warning_us": heartbeat_warning_us,
                    "carrier_at_heartbeat_warning": heartbeat_loss["connection"],
                    "session_state_at_heartbeat_warning": heartbeat_loss[
                        "session_state"
                    ],
                    "online_epoch_at_heartbeat_warning": heartbeat_loss[
                        "online_epoch"
                    ],
                    "reconnect_wait_us": reconnect_wait_us,
                    "offline": offline,
                    "retained": detached,
                },
                "recovery": {
                    "release_us": recovery_release_us,
                    "resume_opened_us": resume_opened_us,
                    "retry_attempts": retry_attempts,
                    **recovered_observation,
                    "incarnation": recovered_before["incarnation"],
                    "generation": recovered_before["generation"],
                    "input_sequence": recovered_before["next_input"],
                    "output_sequence": recovered_before["output_next"],
                    "healthy_heartbeat_start_us": recovered_heartbeat_start,
                    "healthy_heartbeat_end_us": recovered_heartbeat_end,
                    "terminal_started_us": recovered_started,
                    "terminal_returned_us": recovered_returned,
                },
            }
            transitions.append(transition)
            previous_observation = recovered_observation
            checkpoint(
                args.checkpoint_dir,
                f"client.ratox-route-loss-recovered-{ordinal}",
                session,
            )

        # Every sampled byte is a newline, so the local escape filter is at a
        # line boundary. This detach is consumed locally and creates no extra
        # remote input event.
        process.write(b"~d")
        exit_status = process.wait(10.0)
        if exit_status != 0:
            raise ProbeError(f"production CLI detach returned {exit_status}")
        finished_us = monotonic_us()

        peer_commitment = hashlib.sha256(bytes.fromhex(args.peer)).hexdigest()
        atomic_text(
            args.output,
            "\n".join(
                (
                    f"peer-public-key-sha256\t{peer_commitment}",
                    f"samples\t{args.interruptions + 1}",
                    "schema\tiotox-ratox-terminal-probe-v1",
                    *capture_rows,
                    "",
                )
            ),
        )
        atomic_text(
            args.heartbeat_output,
            "\n".join(
                (
                    f"peer-public-key-sha256\t{peer_commitment}",
                    f"samples\t{args.interruptions + 1}",
                    "schema\tiotox-ratox-heartbeat-probe-v1",
                    *heartbeat_rows,
                    "",
                )
            ),
        )
        lifecycle: dict[str, object] = {
            "schema": (
                "iotox-ratox-cli-reconnect-probe-v1"
                if args.interruptions == 1
                else "iotox-ratox-cli-reconnect-probe-v2"
            ),
            "status": "passed",
            "peer_public_key_sha256": peer_commitment,
            "session_id_sha256": hashlib.sha256(
                bytes.fromhex(session)
            ).hexdigest(),
            "process": {
                "client": "iotox-terminal-reconnect",
                "pid": process.pid,
                "start_ticks": start_ticks,
                "started_us": started_us,
                "finished_us": finished_us,
                "process_restarts": 0,
                "exit_status": exit_status,
            },
            "initial": {
                **initial_observation,
                "incarnation": initial_before["incarnation"],
                "generation": 1,
                "input_sequence": 1,
                "output_sequence": 1,
                "healthy_heartbeat_start_us": healthy_start,
                "healthy_heartbeat_end_us": healthy_end,
                "terminal_started_us": initial_started,
                "terminal_returned_us": initial_returned,
            },
            "cli_output_sha256": hashlib.sha256(process.output).hexdigest(),
        }
        if args.interruptions == 1:
            lifecycle["loss"] = transitions[0]["loss"]
            lifecycle["recovery"] = transitions[0]["recovery"]
        else:
            lifecycle["interruption_count"] = args.interruptions
            lifecycle["interruptions"] = transitions
        atomic_json(args.lifecycle_output, lifecycle)
        success = True
    finally:
        if not success:
            process.terminate()
        else:
            try:
                os.close(process.descriptor)
            except OSError:
                pass


def self_test() -> None:
    assert HEX_KEY.fullmatch("ab" * 32)
    assert SESSION_BANNER.search(b"Ratox session=" + b"A1" * 16 + b" escape=")
    assert RECONNECT_RESUMED.search(
        b"Ratox reconnect: resumed exact session generation=2 attempts=7\r\n"
    )
    values = key_values(
        "session=" + "A1" * 16 + " state=attached incarnation=1 generation=2"
        " next-input=3 output-base=3 output-next=3\n"
    )
    assert values["generation"] == "2" and values["next-input"] == "3"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", type=Path)
    parser.add_argument("--peer")
    parser.add_argument("--expected-connection")
    parser.add_argument("--timeout-ms", type=int, default=300000)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--heartbeat-output", type=Path)
    parser.add_argument("--lifecycle-output", type=Path)
    parser.add_argument("--checkpoint-dir", type=Path)
    parser.add_argument("--release-dir", type=Path)
    parser.add_argument("--interruptions", type=int, default=1)
    parser.add_argument("--iotox", default="iotox")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        print("ratox CLI reconnect probe self-test: PASS")
        return 0
    required = (
        "runtime",
        "peer",
        "expected_connection",
        "output",
        "heartbeat_output",
        "lifecycle_output",
        "checkpoint_dir",
        "release_dir",
    )
    missing = [name for name in required if getattr(args, name) is None]
    if missing:
        parser.error("missing required arguments: " + ", ".join(missing))
    if not 1000 <= args.timeout_ms <= 600000:
        parser.error("--timeout-ms must be in 1000..600000")
    if not 1 <= args.interruptions <= 4:
        parser.error("--interruptions must be in 1..4")
    try:
        run(args)
    except (OSError, ProbeError) as error:
        print(f"ratox-cli-reconnect-probe: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
