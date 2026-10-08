#!/usr/bin/env python3
"""Measure two real selective-sync services over an exact sparse >4 TiB tree.

This is a namespace and process-memory gate, not a dense-media throughput test.
Each service owns 4,097 sparse 512 MiB regular files under a metadata-only
policy. A descendant materialization rule prevents root pruning, so the rooted
scanner must classify every file while opening no selected payload bytes.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import signal
import stat
import subprocess
import tempfile
import time
from typing import Any

from test_anonsync_service_configuration_status import (
    linked_peer_configuration,
    wait_for_status,
    write_private_json,
)
from test_anonsync_service_process import (
    finish_service,
    wait_for_service_status_socket,
)
from test_anonsync_sync_process import (
    fail,
    generate_tls_fixture,
    init_combined,
    reserve_port,
    run_json,
)


FILE_COUNT_PER_SHARE = 4_097
FILE_LOGICAL_BYTES = 512 * 1024 * 1024
SHARE_LOGICAL_BYTES = FILE_COUNT_PER_SHARE * FILE_LOGICAL_BYTES
AGGREGATE_LOGICAL_BYTES = 2 * SHARE_LOGICAL_BYTES
MAXIMUM_PHYSICAL_FIXTURE_BYTES = 64 * 1024 * 1024
MAXIMUM_AGGREGATE_PSS_KIB = 1024 * 1024
MAXIMUM_AGGREGATE_PEAK_RSS_KIB = 1536 * 1024
RESOURCE_SAMPLES = 24
RESOURCE_INTERVAL_MILLISECONDS = 75
CHECKS = 0


def require(condition: bool, message: str) -> None:
    global CHECKS
    CHECKS += 1
    if not condition:
        raise RuntimeError(message)


def create_sparse_tree(root: Path) -> int:
    allocated = 0
    for index in range(FILE_COUNT_PER_SHARE):
        path = root / f"media-{index:06d}.bin"
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            os.ftruncate(descriptor, FILE_LOGICAL_BYTES)
        finally:
            os.close(descriptor)
        allocated += path.stat().st_blocks * 512
    return allocated


def start_service(
    *,
    sync: Path,
    config: Path,
) -> subprocess.Popen[str]:
    environment = os.environ.copy()
    environment.pop("NOTIFY_SOCKET", None)
    return subprocess.Popen(
        [str(sync), "run", "--config", str(config)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=environment,
    )


def terminate(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    process.send_signal(signal.SIGTERM)
    try:
        process.communicate(timeout=5.0)
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate(timeout=2.0)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--replica", required=True, type=Path)
    parser.add_argument("--folder", required=True, type=Path)
    parser.add_argument("--sync", required=True, type=Path)
    args = parser.parse_args()
    replica = args.replica.resolve(strict=True)
    folder = args.folder.resolve(strict=True)
    sync = args.sync.resolve(strict=True)
    openssl_executable = shutil.which("openssl")
    if openssl_executable is None:
        fail("openssl executable is unavailable")

    require(
        AGGREGATE_LOGICAL_BYTES == 4_399_120_252_928
        and AGGREGATE_LOGICAL_BYTES > 4 * 1024**4,
        "sparse fixture did not exceed four TiB exactly",
    )

    with tempfile.TemporaryDirectory(
        prefix="anonsync-sparse-multiterabyte-selective-"
    ) as raw:
        root = Path(raw)
        os.chmod(root, 0o700)
        certificates = root / "certificates"
        certificates.mkdir(mode=0o700)
        generate_tls_fixture(certificates, openssl_executable)

        source_manifest, source_files = init_combined(
            replica, root / "source", "source"
        )
        receiver_manifest, receiver_files = init_combined(
            replica, root / "receiver", "receiver"
        )
        run_json(
            [str(folder), "init", "--manifest", str(source_manifest)],
            label="sparse source folder initialization",
        )
        run_json(
            [str(folder), "init", "--manifest", str(receiver_manifest)],
            label="sparse receiver folder initialization",
        )

        allocated = create_sparse_tree(source_files)
        allocated += create_sparse_tree(receiver_files)
        require(
            allocated < MAXIMUM_PHYSICAL_FIXTURE_BYTES,
            f"sparse fixture allocated {allocated} physical bytes",
        )

        for label, manifest in (
            ("source", source_manifest),
            ("receiver", receiver_manifest),
        ):
            run_json(
                [
                    str(sync), "selective-sync-set",
                    "--manifest", str(manifest),
                    "--default", "metadata_only",
                    "--rule", "materialize=needle/keep",
                ],
                label=f"{label} sparse selective policy",
            )

        source_pin = run_json(
            [
                str(replica), "certificate-spki", "--certificate",
                str(certificates / "source.pem"),
            ],
            label="sparse source certificate pin",
        )["spki_sha256"]
        receiver_pin = run_json(
            [
                str(replica), "certificate-spki", "--certificate",
                str(certificates / "receiver.pem"),
            ],
            label="sparse receiver certificate pin",
        )["spki_sha256"]
        run_json(
            [
                str(replica), "membership-publish", "--manifest",
                str(source_manifest), "--policy-epoch", "1", "--peer",
                f"receiver:1:{receiver_pin}",
            ],
            label="sparse source membership publication",
        )
        run_json(
            [
                str(replica), "membership-publish", "--manifest",
                str(receiver_manifest), "--policy-epoch", "1", "--peer",
                f"source:1:{source_pin}",
            ],
            label="sparse receiver membership publication",
        )

        runtime = root / "runtime"
        runtime.mkdir(mode=0o700)
        source_socket = runtime / "source.sock"
        receiver_socket = runtime / "receiver.sock"
        source_config = runtime / "source.json"
        receiver_config = runtime / "receiver.json"
        source_listen = reserve_port()
        receiver_listen = reserve_port()
        source_unreachable = reserve_port()
        receiver_unreachable = reserve_port()
        used = {source_listen}
        for name, value in (
            ("receiver listen", receiver_listen),
            ("source unreachable", source_unreachable),
            ("receiver unreachable", receiver_unreachable),
        ):
            while value in used:
                value = reserve_port()
            used.add(value)
            if name == "receiver listen":
                receiver_listen = value
            elif name == "source unreachable":
                source_unreachable = value
            else:
                receiver_unreachable = value

        source_value = linked_peer_configuration(
            manifest=source_manifest,
            certificates=certificates,
            local_device="source",
            remote_device="receiver",
            remote_pin=receiver_pin,
            listen_port=source_listen,
            remote_port=source_unreachable,
            status_socket=source_socket,
        )
        receiver_value = linked_peer_configuration(
            manifest=receiver_manifest,
            certificates=certificates,
            local_device="receiver",
            remote_device="source",
            remote_pin=source_pin,
            listen_port=receiver_listen,
            remote_port=receiver_unreachable,
            status_socket=receiver_socket,
        )
        source_value["service"]["maximum_service_runtime_seconds"] = 60
        receiver_value["service"]["maximum_service_runtime_seconds"] = 60
        write_private_json(source_config, source_value)
        write_private_json(receiver_config, receiver_value)

        source_process = start_service(sync=sync, config=source_config)
        receiver_process = start_service(sync=sync, config=receiver_config)
        source_terminal: dict[str, Any] | None = None
        receiver_terminal: dict[str, Any] | None = None
        try:
            wait_for_service_status_socket(
                source_process, source_socket, "sparse source service"
            )
            wait_for_service_status_socket(
                receiver_process, receiver_socket, "sparse receiver service"
            )

            series = run_json(
                [
                    str(sync), "resources-watch",
                    "--socket", str(source_socket),
                    "--socket", str(receiver_socket),
                    "--samples", str(RESOURCE_SAMPLES),
                    "--interval-milliseconds",
                    str(RESOURCE_INTERVAL_MILLISECONDS),
                    "--timeout-milliseconds", "10000",
                ],
                label="sparse multi-service resource series",
                timeout=20.0,
            )
            require(
                series.get("schema")
                == "anonsync.local-process-resources.series.v1",
                "sparse resource series schema mismatch",
            )
            require(series.get("process_count") == 2, "sparse series process count mismatch")
            require(series.get("sample_count") == RESOURCE_SAMPLES, "sparse series sample count mismatch")
            require(
                series.get("interval_milliseconds")
                == RESOURCE_INTERVAL_MILLISECONDS,
                "sparse series interval mismatch",
            )
            points = series.get("points")
            require(
                isinstance(points, list) and len(points) == RESOURCE_SAMPLES,
                "sparse resource series point shape mismatch",
            )
            require(
                all(
                    point.get("index") == index
                    and point.get("scheduled_offset_milliseconds")
                    == index * RESOURCE_INTERVAL_MILLISECONDS
                    for index, point in enumerate(points)
                ),
                "sparse resource series was not fixed-schedule",
            )
            processes = series.get("processes")
            require(
                isinstance(processes, list) and len(processes) == 2,
                "sparse process envelopes missing",
            )
            require(
                {
                    item.get("server_pid")
                    for item in processes
                    if isinstance(item, dict)
                }
                == {source_process.pid, receiver_process.pid}
                and all(
                    item.get("first_resources", {}).get(
                        "process_start_time_clock_ticks"
                    )
                    == item.get("last_resources", {}).get(
                        "process_start_time_clock_ticks"
                    )
                    for item in processes
                ),
                "sparse service process identities changed",
            )
            peaks = series.get("observed_peak_sums")
            if not isinstance(peaks, dict):
                fail("sparse resource series omitted observed peaks")
            peak_pss = peaks.get("pss_sum_kib")
            peak_rss = peaks.get("peak_rss_sum_kib")
            require(
                isinstance(peak_pss, int)
                and peak_pss < MAXIMUM_AGGREGATE_PSS_KIB,
                f"sparse services exceeded PSS frontier: {peak_pss!r} KiB",
            )
            require(
                isinstance(peak_rss, int)
                and peak_rss < MAXIMUM_AGGREGATE_PEAK_RSS_KIB,
                f"sparse services exceeded lifetime RSS frontier: {peak_rss!r} KiB",
            )
            require(
                series.get("measurement_is_diagnostic_only") is True,
                "sparse resource series overstated authority",
            )
            require(
                series.get("between_point_peaks_may_be_missed") is True,
                "sparse resource series hid sampled-peak limits",
            )

            source_status = wait_for_status(
                sync, source_process, source_socket, "source", "receiver",
                source_config, "sparse source service",
            )
            receiver_status = wait_for_status(
                sync, receiver_process, receiver_socket, "receiver", "source",
                receiver_config, "sparse receiver service",
            )
            require(source_status.get("ready") is True, "sparse source service was not ready")
            require(receiver_status.get("ready") is True, "sparse receiver service was not ready")

            source_stop = run_json(
                [str(sync), "stop", "--socket", str(source_socket)],
                label="sparse source stop",
            )
            receiver_stop = run_json(
                [str(sync), "stop", "--socket", str(receiver_socket)],
                label="sparse receiver stop",
            )
            require(source_stop.get("terminal_class") == "completed", "sparse source stop failed")
            require(receiver_stop.get("terminal_class") == "completed", "sparse receiver stop failed")
            source_terminal = finish_service(
                source_process, "sparse source service", timeout=15.0
            )
            receiver_terminal = finish_service(
                receiver_process, "sparse receiver service", timeout=15.0
            )
            require(
                source_terminal.get("terminal_class") == "completed"
                and source_terminal.get("stop_reason") == "local_stop_requested",
                "sparse source terminal state was not clean: "
                + json.dumps(source_terminal, sort_keys=True),
            )
            require(
                receiver_terminal.get("terminal_class") == "completed"
                and receiver_terminal.get("stop_reason") == "local_stop_requested",
                "sparse receiver terminal state was not clean: "
                + json.dumps(receiver_terminal, sort_keys=True),
            )
        finally:
            terminate(source_process)
            terminate(receiver_process)

        source_pass = run_json(
            [str(folder), "run", "--manifest", str(source_manifest)],
            label="sparse source diagnostic pass",
            timeout=60.0,
        )
        receiver_pass = run_json(
            [str(folder), "run", "--manifest", str(receiver_manifest)],
            label="sparse receiver diagnostic pass",
            timeout=60.0,
        )

        require(
            source_pass.get("metadata_only_regular_files")
            == FILE_COUNT_PER_SHARE
            and source_pass.get("metadata_only_regular_file_logical_bytes")
            == SHARE_LOGICAL_BYTES,
            "sparse source logical-byte accounting mismatch",
        )
        require(
            receiver_pass.get("metadata_only_regular_files")
            == FILE_COUNT_PER_SHARE
            and receiver_pass.get("metadata_only_regular_file_logical_bytes")
            == SHARE_LOGICAL_BYTES,
            "sparse receiver logical-byte accounting mismatch",
        )
        require(
            source_pass.get("regular_files") == 0
            and source_pass.get("classified_regular_file_bytes") == 0
            and source_pass.get("exact_local_file_bytes") == 0
            and source_pass.get("payload_mutation_work_bytes") == 0,
            "sparse source opened selected payload work",
        )
        require(
            receiver_pass.get("regular_files") == 0
            and receiver_pass.get("classified_regular_file_bytes") == 0
            and receiver_pass.get("exact_local_file_bytes") == 0
            and receiver_pass.get("payload_mutation_work_bytes") == 0,
            "sparse receiver opened selected payload work",
        )
        require(
            source_pass.get("visited_entries") == FILE_COUNT_PER_SHARE
            and source_pass.get("local_directory_enumeration_passes") == 2
            and source_pass.get(
                "local_peak_buffered_directory_component_batch_count"
            ) == 4_096
            and source_pass.get(
                "local_peak_simultaneously_buffered_directory_component_count"
            ) == 4_096
            and source_pass.get("completed_local_scan_epoch") is True
            and source_pass.get("local_scan_stop_reason") == "end_of_namespace",
            "sparse source bounded traversal diagnostics mismatch",
        )
        require(
            receiver_pass.get("visited_entries") == FILE_COUNT_PER_SHARE
            and receiver_pass.get("local_directory_enumeration_passes") == 2
            and receiver_pass.get(
                "local_peak_buffered_directory_component_batch_count"
            ) == 4_096
            and receiver_pass.get(
                "local_peak_simultaneously_buffered_directory_component_count"
            ) == 4_096
            and receiver_pass.get("completed_local_scan_epoch") is True
            and receiver_pass.get("local_scan_stop_reason") == "end_of_namespace",
            "sparse receiver bounded traversal diagnostics mismatch",
        )

    print(
        "sparse multi-terabyte selective resource test passed "
        f"({CHECKS} checks, {AGGREGATE_LOGICAL_BYTES} logical bytes, "
        f"peak aggregate PSS {peak_pss} KiB, lifetime peak RSS sum "
        f"{peak_rss} KiB)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
