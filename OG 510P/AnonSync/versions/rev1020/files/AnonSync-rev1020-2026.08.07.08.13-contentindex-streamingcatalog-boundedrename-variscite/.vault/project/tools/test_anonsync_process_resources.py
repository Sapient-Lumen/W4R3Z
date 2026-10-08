#!/usr/bin/env python3
"""Real-process proof for owner-only Linux resource sampling and aggregation."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time
from typing import Any


CHECKS = 0


def require(condition: bool, message: str) -> None:
    global CHECKS
    CHECKS += 1
    if not condition:
        raise RuntimeError(message)


def run_json(
    argv: list[str], *, expect_success: bool = True, timeout: float = 30.0
) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    result = subprocess.run(
        argv,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )
    if expect_success and result.returncode != 0:
        raise RuntimeError(
            f"command failed ({result.returncode}): {' '.join(argv)}\n"
            f"stdout={result.stdout}\nstderr={result.stderr}"
        )
    document: dict[str, Any] = {}
    if result.stdout.strip():
        try:
            value = json.loads(result.stdout.splitlines()[0])
        except json.JSONDecodeError as error:
            raise RuntimeError(
                f"command did not emit a valid first JSON line: {result.stdout!r}"
            ) from error
        if not isinstance(value, dict):
            raise RuntimeError("command JSON response is not an object")
        document = value
    return result, document


def wait_for_socket(path: Path, process: subprocess.Popen[str]) -> None:
    deadline = time.monotonic() + 10.0
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"fixture exited early with status {process.returncode}")
        try:
            mode = path.lstat().st_mode
        except FileNotFoundError:
            time.sleep(0.01)
            continue
        if stat.S_ISSOCK(mode) and stat.S_IMODE(mode) == 0o600:
            return
        time.sleep(0.01)
    raise RuntimeError(f"timed out waiting for private socket {path}")


def terminate_fixture(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=3)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=3)


def process_start_ticks() -> int:
    stat_text = Path("/proc/self/stat").read_text(encoding="ascii")
    command_end = stat_text.rfind(") ")
    if command_end < 0:
        raise RuntimeError("synthetic server could not parse /proc/self/stat")
    fields = stat_text[command_end + 2 :].split()
    if len(fields) < 20:
        raise RuntimeError("synthetic server stat omitted field 22")
    return int(fields[19])


def synthetic_response(*, start_ticks: int, sequence: int = 0) -> dict[str, Any]:
    memory = {
        "rss_kib": 1,
        "pss_kib": 1,
        "pss_dirty_kib": 0,
        "pss_anon_kib": 1,
        "pss_file_kib": 0,
        "pss_shmem_kib": 0,
        "shared_clean_kib": 0,
        "shared_dirty_kib": 0,
        "private_clean_kib": 1,
        "private_dirty_kib": 0,
        "private_resident_kib": 1,
        "shared_resident_kib": 0,
        "referenced_kib": 1,
        "anonymous_kib": 1,
        "anonymous_huge_pages_kib": 0,
        "shared_hugetlb_kib": 0,
        "private_hugetlb_kib": 0,
        "swap_kib": 0,
        "swap_pss_kib": 0,
        "locked_kib": 0,
    }
    usage = {
        "peak_rss_kib": 1 + sequence,
        "minor_page_faults": sequence,
        "major_page_faults": 0,
        "filesystem_input_operations": 0,
        "filesystem_output_operations": 0,
        "voluntary_context_switches": sequence,
        "involuntary_context_switches": 0,
    }
    return {
        "schema": "anonsync.local-process-resources.response.v1",
        "command": "resources",
        "terminal_class": "completed",
        "server_pid": os.getpid(),
        "process_start_time_clock_ticks": start_ticks,
        "clock_ticks_per_second": os.sysconf("SC_CLK_TCK"),
        "page_size_bytes": os.sysconf("SC_PAGE_SIZE"),
        "sample_monotonic_milliseconds": max(1, int(time.monotonic() * 1000)),
        "memory": memory,
        "usage": usage,
        "open_file_descriptors": 4,
        "threads": 1,
    }


def receive_request(connection: socket.socket) -> bytes:
    request = b""
    while not request.endswith(b"\n") and len(request) < 64:
        part = connection.recv(64 - len(request))
        if not part:
            break
        request += part
    return request


def delayed_server(socket_path: Path, delay_milliseconds: int) -> int:
    if not socket_path.is_absolute():
        raise RuntimeError("delayed server socket must be absolute")
    listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        listener.bind(str(socket_path))
        os.chmod(socket_path, 0o600)
        listener.listen(1)
        connection, _ = listener.accept()
        with connection:
            if receive_request(connection) != b"resources\n":
                return 2
            time.sleep(delay_milliseconds / 1000.0)
            response = synthetic_response(start_ticks=process_start_ticks())
            try:
                connection.sendall(
                    (json.dumps(response, separators=(",", ":")) + "\n").encode()
                )
            except BrokenPipeError:
                pass
            time.sleep(0.1)
    finally:
        listener.close()
        try:
            socket_path.unlink()
        except FileNotFoundError:
            pass
    return 0


def changing_identity_server(socket_path: Path) -> int:
    if not socket_path.is_absolute():
        raise RuntimeError("changing-identity server socket must be absolute")
    listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    base_ticks = process_start_ticks()
    try:
        listener.bind(str(socket_path))
        os.chmod(socket_path, 0o600)
        listener.listen(2)
        for sequence in range(2):
            connection, _ = listener.accept()
            with connection:
                if receive_request(connection) != b"resources\n":
                    return 2
                response = synthetic_response(
                    start_ticks=base_ticks + sequence, sequence=sequence
                )
                connection.sendall(
                    (json.dumps(response, separators=(",", ":")) + "\n").encode()
                )
                time.sleep(0.05)
    finally:
        listener.close()
        try:
            socket_path.unlink()
        except FileNotFoundError:
            pass
    return 0


def totals_from_samples(samples: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "rss_sum_kib": sum(item["memory"]["rss_kib"] for item in samples),
        "pss_sum_kib": sum(item["memory"]["pss_kib"] for item in samples),
        "pss_anon_sum_kib": sum(item["memory"]["pss_anon_kib"] for item in samples),
        "pss_file_sum_kib": sum(item["memory"]["pss_file_kib"] for item in samples),
        "pss_shmem_sum_kib": sum(item["memory"]["pss_shmem_kib"] for item in samples),
        "private_resident_sum_kib": sum(
            item["memory"]["private_resident_kib"] for item in samples
        ),
        "swap_pss_sum_kib": sum(item["memory"]["swap_pss_kib"] for item in samples),
        "peak_rss_sum_kib": sum(item["usage"]["peak_rss_kib"] for item in samples),
        "open_file_descriptors_sum": sum(item["open_file_descriptors"] for item in samples),
        "threads_sum": sum(item["threads"] for item in samples),
    }


def main() -> int:
    if "--delayed-server" in sys.argv:
        parser = argparse.ArgumentParser()
        parser.add_argument("--delayed-server", action="store_true")
        parser.add_argument("--socket", required=True, type=Path)
        parser.add_argument("--delay-milliseconds", required=True, type=int)
        args = parser.parse_args()
        return delayed_server(args.socket, args.delay_milliseconds)
    if "--changing-identity-server" in sys.argv:
        parser = argparse.ArgumentParser()
        parser.add_argument("--changing-identity-server", action="store_true")
        parser.add_argument("--socket", required=True, type=Path)
        args = parser.parse_args()
        return changing_identity_server(args.socket)

    parser = argparse.ArgumentParser()
    parser.add_argument("--sync", required=True, type=Path)
    parser.add_argument("--fixture", required=True, type=Path)
    args = parser.parse_args()
    sync = args.sync.resolve(strict=True)
    fixture = args.fixture.resolve(strict=True)

    with tempfile.TemporaryDirectory(prefix="anonsync-resources-process-") as raw:
        root = Path(raw)
        os.chmod(root, 0o700)
        socket_a = root / "share-a.sock"
        socket_a_alias = root / "share-a-alias.sock"
        socket_b = root / "share-b.sock"
        growth_trigger = root / "grow-share-b"
        out_a = (root / "a.out").open("w", encoding="utf-8")
        err_a = (root / "a.err").open("w", encoding="utf-8")
        out_b = (root / "b.out").open("w", encoding="utf-8")
        err_b = (root / "b.err").open("w", encoding="utf-8")
        process_a = subprocess.Popen(
            [
                str(fixture),
                "--socket", str(socket_a),
                "--socket", str(socket_a_alias),
                "--anonymous-bytes", "0",
            ],
            text=True,
            stdout=out_a,
            stderr=err_a,
        )
        process_b = subprocess.Popen(
            [
                str(fixture),
                "--socket", str(socket_b),
                "--anonymous-bytes", str(48 * 1024 * 1024),
                "--trigger-file", str(growth_trigger),
                "--trigger-anonymous-bytes", str(48 * 1024 * 1024),
            ],
            text=True,
            stdout=out_b,
            stderr=err_b,
        )
        try:
            wait_for_socket(socket_a, process_a)
            wait_for_socket(socket_a_alias, process_a)
            wait_for_socket(socket_b, process_b)
            require(process_a.pid != process_b.pid, "fixtures did not use distinct processes")

            _, aggregate = run_json([
                str(sync), "resources",
                "--socket", str(socket_a),
                "--socket", str(socket_b),
                "--timeout-milliseconds", "5000",
            ])
            require(aggregate.get("schema") == "anonsync.local-process-resources.aggregate.v1", "aggregate schema mismatch")
            require(aggregate.get("command") == "resources", "aggregate command mismatch")
            require(aggregate.get("terminal_class") == "completed", "aggregate did not complete")
            require(aggregate.get("process_count") == 2, "aggregate process count mismatch")
            require(aggregate.get("requested_timeout_milliseconds") == 5000, "aggregate timeout mismatch")
            require(aggregate.get("timeout_is_one_aggregate_deadline") is True, "aggregate did not bind one total deadline")
            require(aggregate.get("rss_sum_double_counts_shared_pages") is True, "aggregate omitted RSS caveat")
            require(aggregate.get("pss_values_use_kernel_share_adjustment") is True, "aggregate omitted PSS caveat")
            require(aggregate.get("samples_are_sequential_not_atomic") is True, "aggregate omitted sequential caveat")
            require(aggregate.get("measurement_is_diagnostic_only") is True, "aggregate overstated authority")
            require(aggregate.get("ordinary_status_remains_procfs_cold") is True, "aggregate omitted status boundary")
            samples = aggregate.get("samples")
            require(isinstance(samples, list) and len(samples) == 2, "aggregate sample list mismatch")
            by_socket = {item["socket"]: item["resources"] for item in samples}
            require(set(by_socket) == {str(socket_a), str(socket_b)}, "aggregate socket identities mismatch")
            first = by_socket[str(socket_a)]
            second = by_socket[str(socket_b)]
            require(first["server_pid"] == process_a.pid, "first sample PID mismatch")
            require(second["server_pid"] == process_b.pid, "second sample PID mismatch")
            require(second["memory"]["pss_anon_kib"] >= first["memory"]["pss_anon_kib"] + 40 * 1024, "48 MiB reservation missing from PSS_Anon")
            require(second["memory"]["private_resident_kib"] >= first["memory"]["private_resident_kib"] + 40 * 1024, "48 MiB reservation missing from private resident")
            expected_totals = totals_from_samples([first, second])
            for key, value in expected_totals.items():
                require(aggregate.get(key) == value, f"aggregate {key} disagreed with samples")

            duplicate, duplicate_json = run_json([
                str(sync), "resources",
                "--socket", str(socket_a),
                "--socket", str(socket_a_alias),
            ], expect_success=False)
            require(duplicate.returncode != 0, "one process was double-counted")
            require(duplicate_json.get("terminal_class") == "stopped", "duplicate rejection lacked structured error")
            require("same live process" in duplicate_json.get("message", ""), "duplicate rejection was not explicit")

            def trigger_growth() -> None:
                time.sleep(0.25)
                growth_trigger.write_bytes(b"grow\n")
                os.chmod(growth_trigger, 0o600)

            trigger_thread = threading.Thread(target=trigger_growth, daemon=True)
            trigger_thread.start()
            _, series = run_json([
                str(sync), "resources-watch",
                "--socket", str(socket_a),
                "--socket", str(socket_b),
                "--samples", "16",
                "--interval-milliseconds", "75",
                "--timeout-milliseconds", "5000",
            ], timeout=15)
            trigger_thread.join(timeout=2)
            require(not trigger_thread.is_alive(), "resource-series growth trigger did not complete")
            require(growth_trigger.is_file(), "resource-series growth trigger was not published")
            require(series.get("schema") == "anonsync.local-process-resources.series.v1", "series schema mismatch")
            require(series.get("command") == "resources-watch", "series command mismatch")
            require(series.get("terminal_class") == "completed", "series did not complete")
            require(series.get("process_count") == 2, "series process count mismatch")
            require(series.get("sample_count") == 16, "series sample count mismatch")
            require(series.get("interval_milliseconds") == 75, "series interval mismatch")
            require(series.get("requested_timeout_milliseconds") == 5000, "series deadline mismatch")
            require(series.get("maximum_processes") == 256, "series process frontier mismatch")
            require(series.get("maximum_samples") == 1024, "series sample frontier mismatch")
            for key in (
                "timeout_is_one_series_deadline",
                "schedule_is_anchored_to_command_start",
                "process_identity_must_remain_stable",
                "restarts_fail_closed",
                "retained_shape_is_processes_plus_samples",
                "full_process_by_sample_matrix_is_not_retained",
                "rss_sum_double_counts_shared_pages",
                "pss_values_use_kernel_share_adjustment",
                "rounds_and_processes_are_sampled_sequentially_not_atomically",
                "between_point_peaks_may_be_missed",
                "target_processes_are_not_paused",
                "measurement_is_diagnostic_only",
                "ordinary_status_remains_procfs_cold",
                "cgroup_pressure_is_not_measured",
            ):
                require(series.get(key) is True, f"series flag {key} is not true")
            points = series.get("points")
            require(isinstance(points, list) and len(points) == 16, "series point shape mismatch")
            previous_completed = 0
            for index, point in enumerate(points):
                require(point.get("index") == index, "series point index mismatch")
                require(point.get("scheduled_offset_milliseconds") == index * 75, "series fixed schedule mismatch")
                require(point.get("started_offset_milliseconds", -1) >= index * 75, "series started before schedule")
                require(point.get("completed_offset_milliseconds", -1) >= point.get("started_offset_milliseconds", 0), "series completion preceded start")
                require(point.get("completed_offset_milliseconds", -1) >= previous_completed, "series completion regressed")
                previous_completed = point["completed_offset_milliseconds"]
                require(isinstance(point.get("schedule_lag_milliseconds"), int) and point["schedule_lag_milliseconds"] >= 0, "series schedule lag is invalid")
                require(isinstance(point.get("sample_span_milliseconds"), int) and point["sample_span_milliseconds"] >= 0, "series sample span is invalid")
                totals = point.get("totals")
                require(isinstance(totals, dict) and "resources" not in totals, "series point retained a full response matrix")
            require(series.get("series_duration_milliseconds", 999999) < 5000, "series exceeded its deadline")
            require(series.get("maximum_schedule_lag_milliseconds") == max(p["schedule_lag_milliseconds"] for p in points), "series max schedule lag mismatch")
            require(series.get("maximum_round_sample_span_milliseconds") == max(p["sample_span_milliseconds"] for p in points), "series max sample span mismatch")

            first_totals = series.get("first_totals")
            last_totals = series.get("last_totals")
            peak_totals = series.get("observed_peak_sums")
            require(isinstance(first_totals, dict) and isinstance(last_totals, dict) and isinstance(peak_totals, dict), "series totals missing")
            require(peak_totals["pss_anon_sum_kib"] >= first_totals["pss_anon_sum_kib"] + 40 * 1024, "resource-series missed triggered 48 MiB anonymous-PSS rise")
            require(peak_totals["private_resident_sum_kib"] >= first_totals["private_resident_sum_kib"] + 40 * 1024, "resource-series missed triggered private-resident rise")
            require(last_totals["pss_anon_sum_kib"] >= first_totals["pss_anon_sum_kib"] + 40 * 1024, "series final sample preceded triggered growth")
            require(points[0]["totals"] == first_totals, "series first totals mismatch")
            require(points[-1]["totals"] == last_totals, "series last totals mismatch")
            for key in first_totals:
                require(peak_totals[key] >= max(point["totals"][key] for point in points), f"series peak {key} is too small")
            delta = series.get("aggregate_usage_delta")
            require(isinstance(delta, dict) and all(isinstance(v, int) and v >= 0 for v in delta.values()), "aggregate usage delta is not nonnegative")

            processes = series.get("processes")
            require(isinstance(processes, list) and len(processes) == 2, "series process envelope count mismatch")
            envelopes = {item["socket"]: item for item in processes}
            require(set(envelopes) == {str(socket_a), str(socket_b)}, "series envelope sockets mismatch")
            for path, pid in ((socket_a, process_a.pid), (socket_b, process_b.pid)):
                envelope = envelopes[str(path)]
                require(envelope.get("server_pid") == pid, "series envelope PID mismatch")
                require(envelope.get("sample_count") == 16, "series envelope sample count mismatch")
                require(envelope["first_resources"]["server_pid"] == pid, "series first identity mismatch")
                require(envelope["last_resources"]["server_pid"] == pid, "series last identity mismatch")
                require(envelope["first_resources"]["process_start_time_clock_ticks"] == envelope["last_resources"]["process_start_time_clock_ticks"], "series process identity changed")
                require(all(isinstance(v, int) and v >= 0 for v in envelope["usage_delta"].values()), "process usage delta is not nonnegative")
            growing = envelopes[str(socket_b)]
            require(growing["observed_peaks"]["pss_anon_kib"] >= growing["first_resources"]["memory"]["pss_anon_kib"] + 40 * 1024, "process envelope missed triggered PSS_Anon rise")
            require(growing["observed_peaks"]["private_resident_kib"] >= growing["first_resources"]["memory"]["private_resident_kib"] + 40 * 1024, "process envelope missed private-resident rise")

            duplicate_series, duplicate_series_json = run_json([
                str(sync), "resources-watch",
                "--socket", str(socket_a),
                "--socket", str(socket_a_alias),
                "--samples", "2",
                "--interval-milliseconds", "20",
                "--timeout-milliseconds", "1000",
            ], expect_success=False)
            require(duplicate_series.returncode != 0, "series double-counted one process")
            require("same live process" in duplicate_series_json.get("message", ""), "series alias rejection was not explicit")

            impossible, impossible_json = run_json([
                str(sync), "resources-watch",
                "--socket", str(socket_a),
                "--samples", "10",
                "--interval-milliseconds", "100",
                "--timeout-milliseconds", "900",
            ], expect_success=False)
            require(impossible.returncode == 2, "impossible series schedule was not an argument error")
            require("final scheduled sample" in impossible_json.get("message", ""), "impossible schedule preflight was not explicit")

            changing_socket = root / "changing.sock"
            changing = subprocess.Popen([
                sys.executable, "-B", "-S", str(Path(__file__).resolve()),
                "--changing-identity-server", "--socket", str(changing_socket),
            ], text=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            try:
                wait_for_socket(changing_socket, changing)
                changed, changed_json = run_json([
                    str(sync), "resources-watch",
                    "--socket", str(changing_socket),
                    "--samples", "2",
                    "--interval-milliseconds", "100",
                    "--timeout-milliseconds", "1000",
                ], expect_success=False)
                require(changed.returncode != 0, "series accepted changed process identity")
                require("restart or socket identity change" in changed_json.get("message", ""), "changed process identity rejection was not explicit")
                require(changing.wait(timeout=3) == 0, "changing identity server did not exit")
            finally:
                terminate_fixture(changing)

            delayed_a = root / "delayed-a.sock"
            delayed_b = root / "delayed-b.sock"
            delayed_processes = [
                subprocess.Popen([
                    sys.executable, "-B", "-S", str(Path(__file__).resolve()),
                    "--delayed-server", "--socket", str(path),
                    "--delay-milliseconds", "250",
                ], text=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                for path in (delayed_a, delayed_b)
            ]
            try:
                for path, process in zip((delayed_a, delayed_b), delayed_processes):
                    wait_for_socket(path, process)
                deadline_started = time.monotonic()
                deadline_result, deadline_json = run_json([
                    str(sync), "resources",
                    "--socket", str(delayed_a),
                    "--socket", str(delayed_b),
                    "--timeout-milliseconds", "400",
                ], expect_success=False)
                deadline_elapsed = time.monotonic() - deadline_started
                require(deadline_result.returncode != 0, "aggregate multiplied its timeout")
                require(deadline_json.get("terminal_class") == "stopped", "aggregate deadline lacked structured error")
                require("timed out" in deadline_json.get("message", "") or "deadline" in deadline_json.get("message", ""), "aggregate deadline failure was not explicit")
                require(deadline_elapsed < 0.8, f"aggregate deadline multiplied across sockets ({deadline_elapsed:.3f}s)")
            finally:
                for process in delayed_processes:
                    try:
                        process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        terminate_fixture(process)

            _, status_a = run_json([str(sync), "status", "--socket", str(socket_a)])
            require(status_a.get("schema") == "anonsync.resource-fixture.status.v1", "resource sampling changed ordinary status")
            require(status_a.get("anonymous_bytes") == 0, "ordinary status changed after sampling")
            require(status_a.get("trigger_anonymous_bytes") == 0, "ordinary status trigger field mismatch")

            _, stop_a = run_json([str(sync), "stop", "--socket", str(socket_a)])
            _, stop_b = run_json([str(sync), "stop", "--socket", str(socket_b)])
            require(stop_a.get("terminal_class") == "completed", "first fixture stop failed")
            require(stop_b.get("terminal_class") == "completed", "second fixture stop failed")
            require(process_a.wait(timeout=10) == 0, "first fixture did not stop")
            require(process_b.wait(timeout=10) == 0, "second fixture did not stop")
            require(not socket_a.exists() and not socket_a_alias.exists() and not socket_b.exists(), "fixture left socket pathnames")
        finally:
            terminate_fixture(process_a)
            terminate_fixture(process_b)
            out_a.close()
            err_a.close()
            out_b.close()
            err_b.close()

    print(f"process resource aggregation test passed ({CHECKS} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
