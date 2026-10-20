#!/usr/bin/env python3
"""Summarize verified Sandwurm Ratox route-impairment captures.

This analyzer is deliberately narrower than verify-sandwurm-pair.py.  It
rechecks the measurement-specific schema and produces comparable phase
statistics; it does not replace independent verification of the complete
pair proof.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import statistics
import sys
import tempfile
from pathlib import Path


SCHEMA = "iotox.ratox-route-impairment-analysis.v1"
SCENARIO = "ratox-route-impairment"
SAMPLE_COUNT = 120
BASELINE_END = 20
IMPAIRMENT_END = 100
DELAY_MS = 75
JITTER_MS = 15
LOSS_PERCENT = 2
ROUTES = ("direct-udp", "forced-tcp", "tox-tor")
SHA256 = re.compile(r"[0-9a-f]{64}")
REVISION = re.compile(r"[0-9a-f]{40}")
SESSION = re.compile(r"[0-9a-f]{32}")


class AnalysisError(RuntimeError):
    pass


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise AnalysisError(detail)


def load_json(path: Path) -> dict:
    require(path.is_file() and not path.is_symlink(), f"missing regular file: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise AnalysisError(f"cannot read canonical JSON {path}: {error}") from error
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def nearest_rank(values: list[int], percentile: float) -> int:
    require(bool(values), "cannot summarize an empty sample")
    require(0.0 < percentile <= 1.0, "percentile is outside (0, 1]")
    ordered = sorted(values)
    return ordered[max(0, math.ceil(percentile * len(ordered)) - 1)]


def summarize(values: list[int]) -> dict:
    require(bool(values), "cannot summarize an empty sample")
    require(all(isinstance(value, int) and value >= 0 for value in values),
            "metric contains a negative or noninteger value")
    return {
        "samples": len(values),
        "minimum_us": min(values),
        "median_us": statistics.median(values),
        "mean_us": round(statistics.fmean(values), 3),
        "p95_us": nearest_rank(values, 0.95),
        "p99_us": nearest_rank(values, 0.99),
        "maximum_us": max(values),
    }


def parse_tsv(path: Path, schema: str, row_width: int) -> tuple[dict, list[list[str]]]:
    require(path.is_file() and not path.is_symlink(), f"missing capture: {path}")
    try:
        lines = path.read_text(encoding="ascii").splitlines()
    except (OSError, UnicodeError) as error:
        raise AnalysisError(f"cannot read ASCII capture {path}: {error}") from error
    metadata: dict[str, str] = {}
    rows: list[list[str]] = []
    for line in lines:
        fields = line.split("\t")
        if fields[0] == "sample":
            require(len(fields) == row_width, f"sample shape drifted in {path}")
            rows.append(fields)
            continue
        require(len(fields) == 2 and fields[0] not in metadata,
                f"metadata is noncanonical in {path}")
        metadata[fields[0]] = fields[1]
    require(set(metadata) == {"peer-public-key-sha256", "samples", "schema"},
            f"capture metadata keys drifted in {path}")
    require(metadata["schema"] == schema, f"capture schema drifted in {path}")
    require(metadata["samples"] == str(SAMPLE_COUNT),
            f"capture sample declaration drifted in {path}")
    require(SHA256.fullmatch(metadata["peer-public-key-sha256"]) is not None,
            f"capture peer commitment is invalid in {path}")
    require(len(rows) == SAMPLE_COUNT, f"capture sample count drifted in {path}")
    return metadata, rows


def parse_measurements(root: Path) -> tuple[Path, Path, list[dict]]:
    receipt = root / "client/live/workspace-export/guest-receipts/iotox"
    terminal_path = receipt / "ratox-controller-capture.tsv"
    heartbeat_path = receipt / "ratox-heartbeat-capture.tsv"
    terminal_metadata, terminal_rows = parse_tsv(
        terminal_path, "iotox-ratox-terminal-probe-v1", 11
    )
    heartbeat_metadata, heartbeat_rows = parse_tsv(
        heartbeat_path, "iotox-ratox-heartbeat-probe-v1", 5
    )
    require(terminal_metadata["peer-public-key-sha256"]
            == heartbeat_metadata["peer-public-key-sha256"],
            "terminal and heartbeat captures name different peers")

    measurements: list[dict] = []
    previous_render = 0
    previous_pong = 0
    observed_session = ""
    for ordinal, (terminal, heartbeat) in enumerate(
        zip(terminal_rows, heartbeat_rows), 1
    ):
        require(terminal[1] == heartbeat[1] == str(ordinal),
                "capture ordinal is not exact")
        try:
            input_us, output_us, render_us = map(int, terminal[2:5])
            input_sequence, next_input = map(int, terminal[6:8])
            output_sequence, next_output = map(int, terminal[8:10])
            queue_wait_us = int(terminal[10])
            heartbeat_start_us, heartbeat_pong_us = map(int, heartbeat[2:4])
        except ValueError as error:
            raise AnalysisError("capture metric is not decimal") from error
        session = terminal[5]
        require(SESSION.fullmatch(session) is not None and session != "0" * 32,
                "terminal session identity is invalid")
        require(heartbeat[4] == session, "heartbeat changed terminal session identity")
        if observed_session:
            require(session == observed_session, "terminal session changed during the gate")
        observed_session = session
        require(previous_pong <= heartbeat_start_us < heartbeat_pong_us <= input_us,
                "heartbeat timestamps are not ordered")
        require(previous_render <= input_us < output_us <= render_us,
                "terminal timestamps are not ordered")
        require(input_sequence > 0 and next_input == input_sequence + 1,
                "terminal input sequence is not contiguous")
        require(output_sequence > 0 and next_output == output_sequence + 1,
                "terminal output sequence is not contiguous")
        require(queue_wait_us >= 0, "interactive queue wait moved below zero")
        measurements.append({
            "ordinal": ordinal,
            "heartbeat_us": heartbeat_pong_us - heartbeat_start_us,
            "terminal_us": output_us - input_us,
            "local_render_us": render_us - output_us,
            "interactive_queue_wait_us": queue_wait_us,
        })
        previous_pong = heartbeat_pong_us
        previous_render = render_us
    return terminal_path, heartbeat_path, measurements


def phase_summary(measurements: list[dict], first: int, last: int) -> dict:
    selected = [row for row in measurements if first <= row["ordinal"] <= last]
    require(len(selected) == last - first + 1, "measurement phase is incomplete")
    return {
        "first_ordinal": first,
        "last_ordinal": last,
        "heartbeat": summarize([row["heartbeat_us"] for row in selected]),
        "terminal": summarize([row["terminal_us"] for row in selected]),
        "local_render": summarize([row["local_render_us"] for row in selected]),
        "interactive_queue_wait": summarize(
            [row["interactive_queue_wait_us"] for row in selected]
        ),
    }


def ratio_ppm(numerator: float, denominator: float) -> int:
    require(denominator > 0, "cannot normalize against a zero baseline")
    return round(numerator * 1_000_000 / denominator)


def analyze_root(proof_root: Path) -> dict:
    root = proof_root.resolve()
    manifest_path = root / "pair-manifest.json"
    manifest = load_json(manifest_path)
    route = manifest.get("route_mode")
    require(route in ROUTES, f"unsupported route mode in {manifest_path}")
    require(manifest.get("scenario") == SCENARIO and manifest.get("status") == "passed",
            f"proof is not an accepted {SCENARIO} cell")
    impairment = manifest.get("ratox_route_impairment")
    require(isinstance(impairment, dict), "Ratox impairment summary is absent")
    require(
        impairment.get("schema") == "iotox-ratox-route-impairment-v1"
        and impairment.get("sample_count") == SAMPLE_COUNT
        and impairment.get("baseline_end_ordinal") == BASELINE_END
        and impairment.get("impairment_end_ordinal") == IMPAIRMENT_END
        and impairment.get("recovery_sample_count") == SAMPLE_COUNT - IMPAIRMENT_END
        and impairment.get("delay_ms") == DELAY_MS
        and impairment.get("jitter_ms") == JITTER_MS
        and impairment.get("loss_percent") == LOSS_PERCENT,
        "Ratox impairment parameters drifted",
    )
    qdiscs = impairment.get("qdiscs")
    require(isinstance(qdiscs, list) and len(qdiscs) == 2,
            "Ratox impairment qdisc evidence is incomplete")
    require({entry.get("tap") for entry in qdiscs} == {"vm-iotoxc", "vm-iotoxd"},
            "Ratox impairment TAP set drifted")
    require(all(isinstance(entry.get("packets"), int) and entry["packets"] > 0
                and isinstance(entry.get("drops"), int) and entry["drops"] > 0
                for entry in qdiscs), "Ratox impairment did not drop on both TAPs")

    client_path = root / "client/live/workspace-export/guest-receipts/iotox/pair.json"
    device_path = root / "device/live/workspace-export/guest-receipts/iotox/pair.json"
    client = load_json(client_path)
    device = load_json(device_path)
    source_revision = client.get("source_revision")
    binary_sha256 = client.get("binary_sha256")
    require(REVISION.fullmatch(str(source_revision)) is not None,
            "client source revision is invalid")
    require(device.get("source_revision") == source_revision,
            "guest source revisions differ")
    require(SHA256.fullmatch(str(binary_sha256)) is not None
            and device.get("binary_sha256") == binary_sha256,
            "guest binary identities differ")

    terminal_path, heartbeat_path, measurements = parse_measurements(root)
    phases = {
        "baseline": phase_summary(measurements, 1, BASELINE_END),
        "impaired": phase_summary(measurements, BASELINE_END + 1, IMPAIRMENT_END),
        "recovery": phase_summary(measurements, IMPAIRMENT_END + 1, SAMPLE_COUNT),
    }
    baseline = phases["baseline"]
    impaired = phases["impaired"]
    recovery = phases["recovery"]
    containment = manifest.get("route_packet_containment")
    require(isinstance(containment, list), "route containment is not a list")
    if route == "tox-tor":
        require(len(containment) == 2
                and all(entry.get("tcp_only") is True
                        and entry.get("only_proxy_destination") is True
                        and entry.get("native_udp_packets") == 0
                        and entry.get("direct_bootstrap_packets") == 0
                        and entry.get("direct_peer_packets") == 0
                        for entry in containment),
                "strict SOCKS containment is incomplete")
    else:
        require(containment == [], "native route unexpectedly claims SOCKS containment")

    return {
        "proof_id": root.name,
        "compact_export": (root / "compact-export.json").is_file(),
        "route_mode": route,
        "source_revision": source_revision,
        "binary_sha256": binary_sha256,
        "manifest_sha256": sha256(manifest_path),
        "terminal_capture_sha256": sha256(terminal_path),
        "heartbeat_capture_sha256": sha256(heartbeat_path),
        "impairment": {
            "delay_ms": DELAY_MS,
            "jitter_ms": JITTER_MS,
            "loss_percent": LOSS_PERCENT,
            "active_wall_ms": impairment.get("active_wall_ms"),
            "tap_packets": sum(entry["packets"] for entry in qdiscs),
            "tap_drops": sum(entry["drops"] for entry in qdiscs),
        },
        "strict_socks_containment": route == "tox-tor",
        "captured_ipv4_egress_packets": sum(
            entry.get("egress_ipv4_packets", 0) for entry in containment
        ),
        "phases": phases,
        "comparisons": {
            "heartbeat_impaired_to_baseline_median_ppm": ratio_ppm(
                impaired["heartbeat"]["median_us"],
                baseline["heartbeat"]["median_us"],
            ),
            "terminal_impaired_to_baseline_median_ppm": ratio_ppm(
                impaired["terminal"]["median_us"],
                baseline["terminal"]["median_us"],
            ),
            "heartbeat_recovery_to_baseline_median_ppm": ratio_ppm(
                recovery["heartbeat"]["median_us"],
                baseline["heartbeat"]["median_us"],
            ),
            "terminal_recovery_to_baseline_median_ppm": ratio_ppm(
                recovery["terminal"]["median_us"],
                baseline["terminal"]["median_us"],
            ),
        },
    }


def analyze(roots: list[Path]) -> dict:
    require(bool(roots), "at least one proof root is required")
    runs = [analyze_root(root) for root in roots]
    route_modes = [run["route_mode"] for run in runs]
    require(len(set(route_modes)) == len(route_modes), "route mode is repeated")
    require(len({run["source_revision"] for run in runs}) == 1,
            "proof roots do not share one source revision")
    require(len({run["binary_sha256"] for run in runs}) == 1,
            "proof roots do not share one binary")
    runs.sort(key=lambda run: ROUTES.index(run["route_mode"]))
    return {
        "schema": SCHEMA,
        "status": "passed",
        "scenario": SCENARIO,
        "source_revision": runs[0]["source_revision"],
        "binary_sha256": runs[0]["binary_sha256"],
        "route_count": len(runs),
        "routes": runs,
        "interpretation_boundary": {
            "transport_presence_is_not_terminal_progress": True,
            "heartbeat_is_not_pty_progress": True,
            "partial_impairment_does_not_qualify_route_migration": True,
            "generic_socks_is_not_actual_tor": True,
        },
    }


def self_test() -> None:
    assert nearest_rank([1, 2, 3, 4, 5], 0.95) == 5
    summary = summarize([1, 2, 3, 4])
    assert summary["median_us"] == 2.5
    assert summary["p95_us"] == 4
    measurements = [
        {
            "ordinal": ordinal,
            "heartbeat_us": ordinal,
            "terminal_us": ordinal * 2,
            "local_render_us": 1,
            "interactive_queue_wait_us": 0,
        }
        for ordinal in range(1, SAMPLE_COUNT + 1)
    ]
    baseline = phase_summary(measurements, 1, BASELINE_END)
    impaired = phase_summary(measurements, BASELINE_END + 1, IMPAIRMENT_END)
    recovery = phase_summary(measurements, IMPAIRMENT_END + 1, SAMPLE_COUNT)
    assert baseline["terminal"]["samples"] == 20
    assert impaired["terminal"]["samples"] == 80
    assert recovery["terminal"]["samples"] == 20
    assert ratio_ppm(2, 1) == 2_000_000
    with tempfile.TemporaryDirectory(prefix="iotox-ratox-analysis-test.") as raw:
        path = Path(raw) / "capture.tsv"
        lines = [
            "peer-public-key-sha256\t" + "ab" * 32,
            f"samples\t{SAMPLE_COUNT}",
            "schema\tiotox-ratox-heartbeat-probe-v1",
        ]
        lines.extend(
            f"sample\t{ordinal}\t{ordinal}\t{ordinal + 1}\t" + "01" * 16
            for ordinal in range(1, SAMPLE_COUNT + 1)
        )
        path.write_text("\n".join(lines) + "\n", encoding="ascii")
        metadata, rows = parse_tsv(
            path, "iotox-ratox-heartbeat-probe-v1", 5
        )
        assert metadata["samples"] == str(SAMPLE_COUNT)
        assert len(rows) == SAMPLE_COUNT
    print("ratox route-impairment analyzer self-test: PASS")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Summarize verified Ratox route-impairment proof roots."
    )
    parser.add_argument("proof_root", nargs="*", type=Path)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    if arguments.self_test:
        self_test()
        return 0
    if not arguments.proof_root:
        parser.error("at least one proof_root is required")
    try:
        print(json.dumps(analyze(arguments.proof_root), indent=2, sort_keys=True))
    except AnalysisError as error:
        print(f"ratox route-impairment analysis failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
