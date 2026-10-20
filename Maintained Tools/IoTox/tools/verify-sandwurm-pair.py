#!/usr/bin/env python3
"""Verify a content-free two-guest IoTox Sandwurm pair proof."""

from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import math
import re
import signal
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SHA256 = re.compile(r"[0-9a-f]{64}")
MAX_I2P_ROUTER_FAULT_DENIALS = 384
ROLES = ("client", "device")
ACTUAL_TOR_SOCKS_PORTS = {"client": 39051, "device": 39052}
ACTUAL_TOR_UPSTREAM_SOCKS_PORTS = {"client": 39151, "device": 39152}
I2P_SOCKS5_PORT = 39053
TOR_APPLICATION_CIRCUIT_PURPOSES = {"GENERAL", "CONFLUX_LINKED"}
ROUTES = {
    "direct-udp": "udp",
    "forced-tcp": "tcp",
    "tox-tor": "tcp",
    "tox-i2p": "tcp",
    "tox-i2p-construction": "tcp",
}
I2P_ROUTES = {"tox-i2p", "tox-i2p-construction"}
COMPACT_SCHEMA = "iotox.sandwurm-pair-compact-export.v0"
PAIR_NAME = re.compile(r"pair\.[A-Za-z0-9_]+")
RATOX_MATRIX_SCENARIOS = {
    "ratox-matrix-idle",
    "ratox-matrix-bulk-1",
    "ratox-matrix-bulk-8",
    "ratox-matrix-bulk-16",
    "ratox-matrix-bulk-32",
    "ratox-matrix-bulk-64",
}
RATOX_BULK_SCENARIOS = {
    "ratox-bulk-1": 1,
    "ratox-bulk-8": 8,
    "ratox-bulk-16": 16,
    "ratox-bulk-32": 32,
    "ratox-bulk-64": 64,
    "ratox-matrix-bulk-1": 1,
    "ratox-matrix-bulk-8": 8,
    "ratox-matrix-bulk-16": 16,
    "ratox-matrix-bulk-32": 32,
    "ratox-matrix-bulk-64": 64,
    "ratox-stripe-32": 32,
    "ratox-stripe-40": 40,
    "ratox-stripe-48": 48,
    "ratox-stripe-56": 56,
    "ratox-stripe-64": 64,
    "ratox-stripe-recovery-32": 32,
    "ratox-stripe-live-loss-32": 32,
    "ratox-stripe-protected-live-loss-24": 24,
}
RATOX_SCENARIOS = {
    "ratox-idle",
    "ratox-matrix-idle",
    "ratox-route-impairment",
    "ratox-route-loss",
    "ratox-cli-reconnect",
    "ratox-cli-reconnect-repeated",
    "ratox-route-actual-tor-loss",
    "ratox-route-actual-tor-soak",
    "ratox-route-actual-tor-adversary",
    "sync-tree-route-loss",
    "sync-tree-route-loss-cancel",
    "sync-tree-route-cancel-loss",
    "sync-tree-route-cancel-race",
    "sync-tree-route-cancel-race-loss-first",
    "sync-tree-route-startup-order",
    "sync-tree-route-balance",
    "sync-tree-route-population",
    "sync-tree-route-population-loss",
    "sync-tree-route-loss-admission",
    "sync-tree-route-startup-admission",
    "sync-tree-route-throughput",
    "sync-tree-route-concurrent-cancel",
    "sync-tree-route-common-link-fairness",
    "sync-tree-route-cancel",
    *RATOX_BULK_SCENARIOS,
}
MUTABLE_SCENARIOS = {"mutable-profile-status"}
BIDIRECTIONAL_SYNC_SCENARIOS = {"sync-bidirectional"}
AUTOMATION_SYNC_SCENARIOS = {"sync-automation"}
SIGNED_UPDATE_SCENARIOS = {"signed-update", "update-service"}
RATOX_STRIPE_SCENARIOS = {
    "ratox-stripe-32": 4,
    "ratox-stripe-40": 4,
    "ratox-stripe-48": 4,
    "ratox-stripe-56": 4,
    "ratox-stripe-64": 4,
    "ratox-stripe-recovery-32": 4,
    "ratox-stripe-live-loss-32": 4,
    "ratox-stripe-protected-live-loss-24": 4,
}
RATOX_LIVE_LOSS_SCENARIOS = {
    "ratox-stripe-live-loss-32",
    "ratox-stripe-protected-live-loss-24",
}
SYNC_SCENARIOS = {
    "sync-tree": 4_194_601,
    "sync-tree-admission": 4_194_601,
    "sync-tree-route-loss": 4_194_601,
    "sync-tree-route-loss-cancel": 4_194_601,
    "sync-tree-route-cancel-loss": 4_194_601,
    "sync-tree-route-cancel-race": 4_194_601,
    "sync-tree-route-cancel-race-loss-first": 4_194_601,
    "sync-tree-route-startup-order": 4_194_601,
    "sync-tree-route-private-mixed": 4_194_601,
    "sync-tree-route-private-actual-tor": 4_194_601,
    "sync-tree-route-private-actual-tor-payload": 4_194_601,
    "sync-tree-route-private-actual-i2p-payload": 131_369,
    "sync-tree-route-private-actual-i2p-loss": 131_369,
    "sync-file-range-actual-i2p": 4 * 1024 * 1024,
    "sync-file-range-actual-i2p-loss": 4 * 1024 * 1024,
    "sync-tree-route-private-actual-tor-loss": 16_777_513,
    "sync-tree-route-balance": 4_194_601,
    "sync-tree-route-population": 131_369,
    "sync-tree-route-population-loss": 131_369,
    "sync-tree-route-loss-admission": 131_369,
    "sync-tree-route-startup-admission": 131_369,
    "sync-tree-route-throughput": 131_369,
    "sync-tree-route-concurrent-cancel": 131_369,
    "sync-tree-route-common-link-fairness": 131_369,
    "sync-tree-route-cancel": 4_194_601,
    "sync-tree-adversity": 4_194_601,
    "sync-tree-pressure": 4_194_601,
    "sync-tree-quota": 4_194_601,
    "sync-tree-object-quota": 4_194_601,
    "sync-tree-read-only": 4_194_601,
    "sync-tree-memory": 4_194_601,
    "sync-tree-source-corrupt": 4_194_601,
    "sync-tree-destination-corrupt": 4_194_601,
    "sync-tree-control-replay": 4_194_601,
    "sync-file": 4 * 1024 * 1024,
    "sync-content": 4 * 1024 * 1024,
    "sync-content-same-source-lanes": 4 * 1024 * 1024,
    "sync-content-restart-cap-2": 8 * 1024 * 1024,
    "sync-content-restart-cap-4": 8 * 1024 * 1024,
    "sync-content-lane-science": 8 * 1024 * 1024,
    "sync-content-lane-science-reverse": 8 * 1024 * 1024,
    "sync-content-ratox-latency-science": 8 * 1024 * 1024,
    "sync-content-ratox-cap-2-sla": 8 * 1024 * 1024,
    "sync-content-ratox-post-bulk-admission": 8 * 1024 * 1024,
    "sync-content-route-private-actual-tor": 4 * 1024 * 1024,
    "sync-content-same-source-multi-route-actual-tor": 4 * 1024 * 1024,
    "sync-content-multi-route-actual-tor": 4 * 1024 * 1024,
    "sync-content-multi-route-actual-tor-loss": 4 * 1024 * 1024,
    "sync-content-multi-source": 4 * 1024 * 1024,
    "sync-content-multi-source-loss": 4 * 1024 * 1024,
    # 4 MiB inert payload plus the frozen 320-byte signed update manifest.
    "signed-update": 4 * 1024 * 1024 + 320,
    # One padded native service image plus the same frozen manifest.
    "update-service": 4 * 1024 * 1024 + 320,
    "sync-file-range": 4 * 1024 * 1024,
    "sync-file-corrupt-basis": 4 * 1024 * 1024,
    "sync-file-range-retry": 4 * 1024 * 1024,
    "sync-file-range-route-loss": 4 * 1024 * 1024,
    "sync-file-range-late-route-loss": 4 * 1024 * 1024,
    "sync-file-range-repeated-route-loss": 4 * 1024 * 1024,
    "sync-file-range-triple-route-loss": 4 * 1024 * 1024,
    "sync-file-range-restart-resume": 4 * 1024 * 1024,
    "sync-file-repair": 4 * 1024 * 1024,
    "sync-file-restart": 8 * 1024 * 1024,
    "sync-file-restart-resume": 8 * 1024 * 1024,
    "sync-file-guest-restart": 8 * 1024 * 1024,
    "sync-file-pause": 8 * 1024 * 1024,
    "sync-file-cancel": 8 * 1024 * 1024,
    "sync-file-disconnect": 8 * 1024 * 1024,
}
CONTENT_MULTI_SOURCE_SCENARIOS = {
    "sync-content-multi-route-actual-tor",
    "sync-content-multi-route-actual-tor-loss",
    "sync-content-multi-source",
    "sync-content-multi-source-loss",
}
CONTENT_LANE_SCIENCE_SCENARIOS = {
    "sync-content-lane-science",
    "sync-content-lane-science-reverse",
    "sync-content-ratox-latency-science",
    "sync-content-ratox-cap-2-sla",
    "sync-content-ratox-post-bulk-admission",
}
CONTENT_RESTART_SCENARIOS = {
    "sync-content-restart-cap-2": 2,
    "sync-content-restart-cap-4": 4,
}
CONTENT_SCENARIOS = {
    "sync-content",
    "sync-content-same-source-lanes",
    *CONTENT_RESTART_SCENARIOS,
    *CONTENT_LANE_SCIENCE_SCENARIOS,
    "sync-content-route-private-actual-tor",
    "sync-content-same-source-multi-route-actual-tor",
    *CONTENT_MULTI_SOURCE_SCENARIOS,
}


def content_completion_fields(
    scenario: str,
    atomic_multi_source: bool,
) -> list[str]:
    fields = ["convergence", "activation"]
    if scenario in CONTENT_RESTART_SCENARIOS:
        fields.append("restart")
    fields.extend(
        [
            "generation",
            "head-record",
            "artifact-sha256",
            "manifest-sha256",
            "artifact-bytes",
            "manifest-bytes",
            "content-format",
            "content-chunks",
            "content-pages",
            "content-objects",
        ]
    )
    if scenario in CONTENT_LANE_SCIENCE_SCENARIOS:
        fields.extend(
            [
                "content-lane-science",
                "content-lane-science-phase-order",
                "content-lane-science-restarts",
                "content-lane-science-activations",
            ]
        )
        for cap in (1, 2, 4, 8):
            fields.extend(
                [
                    f"content-lane-science-cap-{cap}-duration-ms",
                    f"content-lane-science-cap-{cap}-bps",
                    f"content-lane-science-cap-{cap}-active",
                ]
            )
        fields.append("content-lane-science-summary-sha256")
        if scenario == "sync-content-ratox-post-bulk-admission":
            fields.extend(
                [
                    "content-ratox-post-bulk",
                    "content-ratox-post-bulk-cap",
                    "content-ratox-post-bulk-samples",
                    "content-ratox-post-bulk-origin-us",
                    "content-ratox-post-bulk-origin-to-open-sent-us",
                    "content-ratox-post-bulk-origin-to-opened-us",
                    "content-ratox-post-bulk-open-round-trip-us",
                    "content-ratox-post-bulk-online-epoch",
                    "content-ratox-post-bulk-readiness-sha256",
                    "content-ratox-post-bulk-capture-sha256",
                    "content-ratox-post-bulk-admission-sha256",
                ]
            )
    if scenario in CONTENT_MULTI_SOURCE_SCENARIOS:
        if atomic_multi_source:
            fields.append("content-atomic-pull")
        fields.extend(
            [
                "content-primary-chunks",
                "content-secondary-chunks",
                "content-source-count",
                "content-availability-requests",
                "content-availability-results",
            ]
        )
        if scenario in {
            "sync-content-multi-source-loss",
            "sync-content-multi-route-actual-tor-loss",
        }:
            fields.extend(
                [
                    "content-loss-observed",
                    "content-loss-recovery",
                    "content-loss-first-job",
                    "content-loss-replacement-job",
                    "content-loss-committed-objects",
                    "content-loss-fetched-bytes",
                    "content-loss-initial-epoch",
                    "content-loss-recovered-epoch",
                    "content-loss-staging-clean",
                    "content-loss-head-fenced",
                    "content-loss-activation-fenced",
                ]
            )
            if scenario == "sync-content-multi-route-actual-tor-loss":
                fields.extend(
                    [
                        "content-route-loss",
                        "content-route-loss-target",
                        "content-route-loss-fault-worker",
                        "content-route-loss-recovered-worker",
                        "content-route-loss-position-bytes",
                        "content-route-loss-carrier-losses",
                        "content-route-loss-reassignments",
                        "content-route-loss-recoveries",
                        "content-route-loss-primary-epoch",
                        "content-route-loss-secondary-epoch",
                    ]
                )
    return fields


SYNC_TREE_SCENARIOS = {
    "sync-tree",
    "sync-tree-admission",
    "sync-tree-route-loss",
    "sync-tree-route-loss-cancel",
    "sync-tree-route-cancel-loss",
    "sync-tree-route-cancel-race",
    "sync-tree-route-cancel-race-loss-first",
    "sync-tree-route-startup-order",
    "sync-tree-route-private-mixed",
    "sync-tree-route-private-actual-tor",
    "sync-tree-route-private-actual-tor-payload",
    "sync-tree-route-private-actual-i2p-payload",
    "sync-tree-route-private-actual-i2p-loss",
    "sync-tree-route-private-actual-tor-loss",
    "sync-tree-route-balance",
    "sync-tree-route-population",
    "sync-tree-route-population-loss",
    "sync-tree-route-loss-admission",
    "sync-tree-route-startup-admission",
    "sync-tree-route-throughput",
    "sync-tree-route-concurrent-cancel",
    "sync-tree-route-common-link-fairness",
    "sync-tree-route-cancel",
    "sync-tree-adversity",
    "sync-tree-pressure",
    "sync-tree-quota",
    "sync-tree-object-quota",
    "sync-tree-read-only",
    "sync-tree-memory",
    "sync-tree-source-corrupt",
    "sync-tree-destination-corrupt",
    "sync-tree-control-replay",
}
MULTI_ROUTE_SYNC_SCENARIOS = {
    "sync-content-route-private-actual-tor",
    "sync-content-same-source-multi-route-actual-tor",
    "sync-content-multi-route-actual-tor",
    "sync-content-multi-route-actual-tor-loss",
    "sync-tree-route-loss",
    "sync-tree-route-loss-cancel",
    "sync-tree-route-cancel-loss",
    "sync-tree-route-cancel-race",
    "sync-tree-route-cancel-race-loss-first",
    "sync-tree-route-startup-order",
    "sync-tree-route-private-mixed",
    "sync-tree-route-private-actual-tor",
    "sync-tree-route-private-actual-tor-payload",
    "sync-tree-route-private-actual-i2p-payload",
    "sync-tree-route-private-actual-i2p-loss",
    "sync-file-range-actual-i2p",
    "sync-file-range-actual-i2p-loss",
    "sync-file-range-route-loss",
    "sync-file-range-late-route-loss",
    "sync-file-range-repeated-route-loss",
    "sync-file-range-triple-route-loss",
    "sync-tree-route-private-actual-tor-loss",
    "sync-tree-route-balance",
    "sync-tree-route-population",
    "sync-tree-route-population-loss",
    "sync-tree-route-loss-admission",
    "sync-tree-route-startup-admission",
    "sync-tree-route-throughput",
    "sync-tree-route-concurrent-cancel",
    "sync-tree-route-common-link-fairness",
    "sync-tree-route-cancel",
}
SYNC_CANCELLATION_SCENARIOS = {
    "sync-file-cancel",
    "sync-tree-route-cancel",
    "sync-tree-route-loss-cancel",
    "sync-tree-route-cancel-loss",
    "sync-tree-route-cancel-race",
    "sync-tree-route-cancel-race-loss-first",
}
SYNC_CONCURRENT_CANCEL_SCENARIOS = {
    "sync-tree-route-concurrent-cancel",
    "sync-tree-route-common-link-fairness",
}
SYNC_CONCURRENT_CANCEL_ARTIFACT_BYTES = {
    "sync-tree-route-concurrent-cancel": 262_211,
    "sync-tree-route-common-link-fairness": 1_048_643,
}
SYNC_ROUTE_CANCEL_RACE_SCENARIOS = {
    "sync-tree-route-cancel-race": (500, 500, None),
    "sync-tree-route-cancel-race-loss-first": (250, 1000, "loss-first"),
}
SYNC_ROUTE_LOSS_SCENARIOS = {
    "sync-tree-route-loss",
    "sync-tree-route-loss-cancel",
    "sync-tree-route-cancel-loss",
    "sync-tree-route-cancel-race",
    "sync-tree-route-cancel-race-loss-first",
    "sync-tree-route-private-actual-tor-loss",
    "sync-file-range-route-loss",
    "sync-file-range-late-route-loss",
    "sync-file-range-repeated-route-loss",
    "sync-file-range-triple-route-loss",
}

REPEATED_RANGE_LOSS_COUNTS = {
    "sync-file-range-repeated-route-loss": 2,
    "sync-file-range-triple-route-loss": 3,
}


def ratox_sample_count(scenario: str) -> int:
    if scenario == "ratox-route-impairment":
        return RATOX_IMPAIRMENT_SAMPLES
    if scenario == "ratox-cli-reconnect-repeated":
        return 3
    if scenario in {
        "ratox-route-loss",
        "ratox-cli-reconnect",
        "ratox-route-actual-tor-loss",
        "ratox-route-actual-tor-adversary",
    }:
        return 2
    if scenario == "ratox-route-actual-tor-soak":
        return RATOX_ACTUAL_TOR_SOAK_SAMPLES
    return 1000 if scenario in RATOX_MATRIX_SCENARIOS else 40
SYNC_TREE_QUOTA_SCENARIOS = {"sync-tree-quota", "sync-tree-object-quota"}
SYNC_RANGE_SCENARIOS = {
    "sync-file-range",
    "sync-file-range-actual-i2p",
    "sync-file-range-actual-i2p-loss",
    "sync-file-corrupt-basis",
    "sync-file-range-retry",
    "sync-file-range-route-loss",
    "sync-file-range-late-route-loss",
    "sync-file-range-repeated-route-loss",
    "sync-file-range-triple-route-loss",
    "sync-file-range-restart-resume",
}
SYNC_POSITIVE_RANGE_SCENARIOS = SYNC_RANGE_SCENARIOS - {
    "sync-file-corrupt-basis"
}
GUEST_RESTART_SCENARIOS = {"guest-restart", "sync-file-guest-restart"}
PACKET_LOSS_PERCENT = 5
RATOX_IMPAIRMENT_SAMPLES = 120
RATOX_IMPAIRMENT_BASELINE_END = 20
RATOX_IMPAIRMENT_END = 100
RATOX_IMPAIRMENT_DELAY_MS = 75
RATOX_IMPAIRMENT_JITTER_MS = 15
RATOX_IMPAIRMENT_LOSS_PERCENT = 2
RATOX_ACTUAL_TOR_SOAK_SAMPLES = 120
RATOX_ACTUAL_TOR_SOAK_INTERVAL_MS = 1000
RATOX_ACTUAL_TOR_SOAK_CHURNS = (("client", 20), ("device", 100))
RATOX_IMPAIRMENT_SEEDS = {
    "vm-iotoxc": 20_260_827,
    "vm-iotoxd": 20_260_828,
}
PACKET_LOSS_PROBE_COUNT = 128
PACKET_LOSS_SEEDS = {
    "vm-iotoxc": 20_260_824,
    "vm-iotoxd": 20_260_825,
}
PACKET_LOSS_LINE = re.compile(
    r"burst-probe\tordinal\t([1-9][0-9]*)\tnonce\t([1-9][0-9]*)"
    r"\trtt-us\t(miss|[0-9]+)\tarrival-rank\t(miss|[1-9][0-9]*)"
    r"\tcopies\t([0-9]+)\tsend-error\t([a-z-]+)"
)
LEGACY_REPAIR_BINARY_SHA256 = {
    "782a1f2792ce0576fd7d2de696c5d88641ab652eed19a8c009719a32c85e0f51"
}
RESOURCE_SAMPLE_KEYS = {
    "monotonic-ns",
    "process-start-ticks",
    "user-cpu-ticks",
    "system-cpu-ticks",
    "minor-faults",
    "major-faults",
    "resident-pages",
    "resident-high-water-kib",
    "voluntary-context-switches",
    "involuntary-context-switches",
    "read-bytes",
    "write-bytes",
    "open-descriptors",
    "transport-iterations",
    "transport-requested-iteration-ms",
    "transport-effective-iteration-ms",
    "ratox-latency-mode-active",
    "ratox-active-service-interval-ms",
    "ratox-active-transport-iteration-interval-ms",
}
RESOURCE_DELTA_KEYS = {
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
}

CAP_2_SLA_MIN_OVERLAP = 40
CAP_2_SLA_P50_US = 250_000
CAP_2_SLA_P95_US = 500_000
CAP_2_SLA_P99_US = 1_000_000
CAP_2_SLA_MAX_US = 1_500_000
CAP_2_SLA_QUEUE_P95_US = 10_000


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def nearest_rank(values: list[int], percent: int) -> int:
    ordered = sorted(values)
    return ordered[math.ceil(len(ordered) * percent / 100) - 1]


def cap_2_interactive_sla_passes(
    round_trips: list[int], queue_waits: list[int]
) -> bool:
    return (
        len(round_trips) >= CAP_2_SLA_MIN_OVERLAP
        and len(queue_waits) == len(round_trips)
        and nearest_rank(round_trips, 50) <= CAP_2_SLA_P50_US
        and nearest_rank(round_trips, 95) <= CAP_2_SLA_P95_US
        and nearest_rank(round_trips, 99) <= CAP_2_SLA_P99_US
        and max(round_trips) <= CAP_2_SLA_MAX_US
        and nearest_rank(queue_waits, 95) <= CAP_2_SLA_QUEUE_P95_US
    )


def expected_network(route: str) -> str:
    if route == "tox-tor":
        return "Tox/Tor"
    if route == "tox-i2p":
        return "Tox/I2P"
    if route == "tox-i2p-construction":
        return "Tox/I2P-construction"
    return "Tox/native"


def actual_i2p_router_restart_expected(scenario: object) -> bool:
    return scenario in {
        "i2p-router-restart",
        "sync-tree-route-private-actual-i2p-loss",
        "sync-file-range-actual-i2p-loss",
    }


def verify_actual_i2p_evidence(
    proof_root: Path, manifest: dict, enabled: bool
) -> None:
    expected_router_restarts = int(
        actual_i2p_router_restart_expected(manifest.get("scenario"))
    )
    expected_front_restarts = int(
        manifest.get("scenario") == "i2p-service-restart"
    )
    expected_recovery = bool(expected_router_restarts or expected_front_restarts)
    require(manifest.get("actual_i2p", False) is enabled, "actual-I2P mode mismatch")
    if not enabled:
        require(
            manifest.get("actual_i2p_topology_ready", False) is False
            and manifest.get("actual_i2p_topology_path") is None
            and manifest.get("actual_i2p_topology_sha256") is None
            and manifest.get("actual_i2p_node_records_sha256", "") == ""
            and manifest.get("actual_i2p_front_count", 0) == 0
            and manifest.get("actual_i2p_router_restart_count", 0) == 0
            and manifest.get("actual_i2p_front_restart_count", 0) == 0,
            "non-I2P proof claims an I2P topology",
        )
        return
    topology_path = confined(
        proof_root,
        manifest.get("actual_i2p_topology_path"),
        "i2p-fronts/topology-final.json",
    )
    require(
        manifest.get("actual_i2p_topology_ready") is True
        and manifest.get("actual_i2p_topology_sha256") == digest(topology_path)
        and manifest.get("actual_i2p_front_count") == 3
        and manifest.get("actual_i2p_router_restart_count", 0)
        == expected_router_restarts
        and manifest.get("actual_i2p_front_restart_count", 0)
        == expected_front_restarts,
        "actual-I2P manifest topology binding is invalid",
    )
    topology = load(topology_path)
    destinations = topology.get("destination_commitments")
    certificate_fields_present = any(
        key in topology
        for key in (
            "router_certificates_relative_path",
            "router_certificates_tree_sha256",
            "router_certificates_file_count",
            "router_reseed_signature_verification",
        )
    )
    require(
        (
            certificate_fields_present
            and topology.get("router_certificates_relative_path")
            == "contrib/certificates"
            and SHA256.fullmatch(
                str(topology.get("router_certificates_tree_sha256", ""))
            )
            is not None
            and topology.get("router_certificates_file_count") == 21
            and topology.get("router_reseed_signature_verification") is True
        )
        or (not certificate_fields_present and not expected_recovery),
        "actual-I2P router certificate binding is invalid",
    )
    socket_attribution = topology.get("router_socket_attribution")
    if socket_attribution is not None:
        require(
            isinstance(socket_attribution, dict)
            and set(socket_attribution) == {"initial", "recovered_client"}
            and isinstance(socket_attribution.get("initial"), list)
            and len(socket_attribution["initial"]) == 2,
            "actual-I2P router socket attribution is invalid",
        )
        initial_sockets = socket_attribution["initial"]
        require(
            [record.get("role") for record in initial_sockets]
            == ["server", "client"]
            and len({record.get("pid") for record in initial_sockets}) == 2,
            "actual-I2P initial router process attribution is invalid",
        )
        for record in initial_sockets:
            require(
                isinstance(record, dict)
                and isinstance(record.get("pid"), int)
                and record["pid"] > 1
                and isinstance(record.get("process_start_ticks"), int)
                and record["process_start_ticks"] > 0
                and record.get("sam_listener_owned") is True
                and isinstance(record.get("public_tcp_remote_count"), int)
                and 1 <= record["public_tcp_remote_count"] <= 65535
                and SHA256.fullmatch(
                    str(record.get("public_tcp_remote_set_sha256", ""))
                )
                is not None
                and record.get("contains_secrets") is False,
                "actual-I2P router socket record is invalid",
            )
        recovered_socket = socket_attribution.get("recovered_client")
        if expected_router_restarts:
            require(
                isinstance(recovered_socket, dict)
                and recovered_socket.get("role") == "client"
                and isinstance(recovered_socket.get("pid"), int)
                and recovered_socket["pid"] > 1
                and recovered_socket["pid"] != initial_sockets[1]["pid"]
                and isinstance(recovered_socket.get("process_start_ticks"), int)
                and recovered_socket["process_start_ticks"]
                > initial_sockets[1]["process_start_ticks"]
                and recovered_socket.get("sam_listener_owned") is True
                and isinstance(recovered_socket.get("public_tcp_remote_count"), int)
                and 1 <= recovered_socket["public_tcp_remote_count"] <= 65535
                and SHA256.fullmatch(
                    str(recovered_socket.get("public_tcp_remote_set_sha256", ""))
                )
                is not None
                and recovered_socket.get("contains_secrets") is False,
                "actual-I2P recovered router socket attribution is invalid",
            )
        else:
            require(
                recovered_socket is None,
                "baseline actual-I2P proof claims recovered router sockets",
            )
    require(
        topology.get("schema") == "iotox.i2p-tox-fronts.v1"
        and topology.get("status") == "passed"
        and topology.get("front_count") == 3
        and topology.get("proxy_endpoint") == "10.0.0.1:39053"
        and topology.get("contains_secrets") is False
        and str(topology.get("router_version", "")).startswith(
            "i2pd version 2.60.0 (0.9.69)\n"
        )
        and SHA256.fullmatch(str(topology.get("router_binary_sha256", "")))
        is not None
        and SHA256.fullmatch(str(topology.get("router_source_tree_sha256", "")))
        is not None
        and isinstance(topology.get("router_source_file_count"), int)
        and topology["router_source_file_count"] > 0
        and isinstance(destinations, list)
        and len(destinations) == 3
        and len(set(destinations)) == 3
        and all(SHA256.fullmatch(str(value)) is not None for value in destinations)
        and topology.get("node_records_sha256")
        == manifest.get("actual_i2p_node_records_sha256")
        and topology.get("client_router_restart_count", 0)
        == expected_router_restarts
        and topology.get("server_front_restart_count", 0)
        == expected_front_restarts,
        "actual-I2P topology receipt is invalid",
    )
    fault = topology.get("client_router_fault", {})
    if expected_router_restarts:
        require(
            isinstance(fault, dict)
            and fault.get("kind") == "client-router-process-restart"
            and isinstance(fault.get("old_client_router_pid"), int)
            and isinstance(fault.get("new_client_router_pid"), int)
            and fault["old_client_router_pid"] > 1
            and fault["new_client_router_pid"] > 1
            and fault["old_client_router_pid"] != fault["new_client_router_pid"]
            and fault.get("process_replaced") is True
            and fault.get("router_datadir_preserved") is True
            and fault.get("adapter_listener_reachable_while_sam_down") is True
            and fault.get("client_sam_listener_absent_during_fault") is True
            and fault.get("adapter_generation_one_lost") is True
            and fault.get("adapter_generation_two_ready") is True
            and isinstance(fault.get("fault_hold_ns"), int)
            and fault["fault_hold_ns"] > 0
            and fault.get("contains_secrets") is False,
            "actual-I2P client-router fault evidence is invalid",
        )
        if socket_attribution is not None:
            require(
                socket_attribution["initial"][1]["pid"]
                == fault["old_client_router_pid"]
                and socket_attribution["recovered_client"]["pid"]
                == fault["new_client_router_pid"],
                "actual-I2P router fault is not joined to socket ownership",
            )
    else:
        require(fault == {}, "baseline actual-I2P proof claims a router fault")
    front_fault = topology.get("server_front_fault", {})
    if expected_front_restarts:
        old_pids = front_fault.get("old_server_front_pids") if isinstance(front_fault, dict) else None
        new_pids = front_fault.get("new_server_front_pids") if isinstance(front_fault, dict) else None
        require(
            isinstance(front_fault, dict)
            and front_fault.get("kind") == "server-front-process-restart"
            and isinstance(old_pids, list)
            and isinstance(new_pids, list)
            and len(old_pids) == len(new_pids) == 3
            and len(set(old_pids)) == len(set(new_pids)) == 3
            and all(isinstance(pid, int) and pid > 1 for pid in [*old_pids, *new_pids])
            and set(old_pids).isdisjoint(new_pids)
            and front_fault.get("processes_replaced") is True
            and front_fault.get("destination_keys_preserved") is True
            and front_fault.get("adapter_listener_preserved") is True
            and front_fault.get("server_sam_listener_preserved") is True
            and front_fault.get("client_sam_listener_preserved") is True
            and front_fault.get("routers_preserved") is True
            and isinstance(front_fault.get("fault_started_ns"), int)
            and isinstance(front_fault.get("fault_recovered_ns"), int)
            and front_fault["fault_started_ns"] > 0
            and front_fault["fault_recovered_ns"] > front_fault["fault_started_ns"]
            and front_fault.get("fault_hold_ns")
            == front_fault["fault_recovered_ns"] - front_fault["fault_started_ns"]
            and front_fault.get("contains_secrets") is False,
            "actual-I2P server-front fault evidence is invalid",
        )
    else:
        require(front_fault == {}, "non-service-restart proof claims a server-front fault")
    audits = topology.get("audits")
    expected_audit_count = 7 if expected_front_restarts else 4
    require(
        isinstance(audits, list) and len(audits) == expected_audit_count,
        "actual-I2P audit set is invalid",
    )
    expected_paths = ["adapter.audit.jsonl", *[f"forward-{index}.audit.jsonl" for index in range(1, 4)]]
    if expected_front_restarts:
        expected_paths.extend(
            f"forward-restart-{index}.audit.jsonl" for index in range(1, 4)
        )
    for index, (entry, expected_path) in enumerate(zip(audits, expected_paths)):
        require(isinstance(entry, dict), "actual-I2P audit entry is invalid")
        audit_path = confined(
            proof_root,
            f"i2p-fronts/{entry.get('path', '')}",
            f"i2p-fronts/{expected_path}",
        )
        records = [
            json.loads(line)
            for line in audit_path.read_text(encoding="ascii").splitlines()
        ]
        outcomes: dict[str, int] = {}
        for record in records:
            require(isinstance(record, dict), "actual-I2P audit record is invalid")
            outcome = str(record.get("outcome", ""))
            outcomes[outcome] = outcomes.get(outcome, 0) + 1
        require(
            entry.get("path") == expected_path
            and entry.get("sha256") == digest(audit_path)
            and entry.get("records") == len(records)
            and entry.get("outcomes") == outcomes,
            "actual-I2P audit summary mismatch",
        )
        if index == 0:
            connection_records = [
                record
                for record in records
                if record.get("event") == "socks5-i2p-connect"
            ]
            admitted_records = [
                record
                for record in connection_records
                if record.get("outcome") == "admitted"
            ]
            denied_records = [
                record
                for record in connection_records
                if record.get("outcome") != "admitted"
            ]
            session_records = [
                record for record in records if record.get("event") == "sam-session"
            ]
            expected_session_outcomes = (
                ["ready", "lost", "ready"]
                if expected_router_restarts
                else ["ready"]
            )
            expected_session_generations = (
                [1, 1, 2] if expected_router_restarts else [1]
            )
            allowed_denials = (
                {
                    "denied-stream",
                    "denied-sam-unavailable",
                    "denied-stale-generation",
                }
                if expected_router_restarts
                else {"denied-stream"}
            )
            require(
                len(records) == len(connection_records) + len(session_records)
                and 6 <= len(admitted_records) <= 24
                and len(denied_records)
                <= (MAX_I2P_ROUTER_FAULT_DENIALS if expected_recovery else 6)
                and len(admitted_records) + len(denied_records)
                == len(connection_records)
                and outcomes.get("admitted", 0) == len(admitted_records)
                and [record.get("outcome") for record in session_records]
                == expected_session_outcomes
                and [record.get("generation") for record in session_records]
                == expected_session_generations
                and set(outcomes).issubset(
                    {"ready", "lost", "admitted", *allowed_denials}
                )
                and all(
                    record.get("outcome") in {"admitted", *allowed_denials}
                    and record.get("destination_sha256") in destinations
                    for record in connection_records
                )
                and {
                    record.get("destination_sha256")
                    for record in admitted_records
                }
                == set(destinations),
                "actual-I2P adapter did not admit both three-front guests cleanly",
            )
            if expected_router_restarts:
                generation_one = [
                    record
                    for record in admitted_records
                    if record.get("generation") == 1
                ]
                generation_two = [
                    record
                    for record in admitted_records
                    if record.get("generation") == 2
                ]
                require(
                    {
                        record.get("destination_sha256")
                        for record in generation_one
                    }
                    == set(destinations),
                    "actual-I2P generation one did not admit every front",
                )
                require(
                    len(generation_two) >= 2
                    and {
                        record.get("destination_sha256")
                        for record in generation_two
                    }.issubset(set(destinations)),
                    "actual-I2P generation two did not admit both recovering guests",
                )
            if expected_front_restarts:
                started = front_fault["fault_started_ns"]
                recovered = front_fault["fault_recovered_ns"]
                pre_fault = [
                    record
                    for record in admitted_records
                    if isinstance(record.get("monotonic_ns"), int)
                    and record["monotonic_ns"] < started
                ]
                post_recovery = [
                    record
                    for record in admitted_records
                    if isinstance(record.get("monotonic_ns"), int)
                    and record["monotonic_ns"] > recovered
                ]
                require(
                    {record.get("destination_sha256") for record in pre_fault}
                    == set(destinations),
                    "actual-I2P adapter did not admit every front before replacement",
                )
                require(
                    len(post_recovery) >= 2
                    and {
                        record.get("destination_sha256")
                        for record in post_recovery
                    }.issubset(set(destinations)),
                    "actual-I2P adapter did not admit both guests after front replacement",
                )
        else:
            require(
                outcomes.get("ready", 0) == 1 and outcomes.get("lost", 0) == 0,
                "actual-I2P service front was not stable",
            )
            require(
                outcomes.get("created", 0) == (1 if index <= 3 else 0)
                and outcomes.get("loaded", 0) == (1 if index > 3 else 0),
                "actual-I2P service-front key lifecycle is invalid",
            )


def verify_actual_i2p_fail_closed_loss(
    proof_root: Path, manifest: dict, expected: bool
) -> None:
    evidence = manifest.get("actual_i2p_fail_closed_loss", {})
    if not expected:
        require(
            evidence == {}
            and manifest.get("actual_i2p_fail_closed_loss_path") is None
            and manifest.get("actual_i2p_fail_closed_loss_sha256") is None,
            "non-I2P-loss proof claims fail-closed loss evidence",
        )
        return
    range_loss = manifest.get("scenario") == "sync-file-range-actual-i2p-loss"
    loss_position_ceiling = (
        manifest.get("sync_range_fetched_bytes")
        if range_loss
        else SYNC_SCENARIOS["sync-tree-route-private-actual-i2p-loss"]
    )
    expected_keys = {
        "adapter_generation_one_lost",
        "adapter_generation_two_ready",
        "adapter_listener_reachable_while_sam_down",
        "blocked_jobs",
        "carrier_losses",
        "client_sam_listener_absent_during_fault",
        "contains_secrets",
        "fault_hold_ns",
        "loss_observation_ns",
        "new_client_router_pid",
        "old_client_router_pid",
        "old_job_cancelled",
        "original_job_id",
        "position_bytes",
        "reassignments",
        "recoveries",
        "replacement_job_id",
        "replacement_same_carrier",
        "role",
        "route_worker_restarts",
        "router_datadir_preserved",
        "router_recovery_ns",
        "schema",
        "stopped_carrier",
        "stopped_carrier_sha256",
    }
    if range_loss:
        expected_keys.update({
            "manifest_reused_locally",
            "replacement_committed_objects",
            "replacement_requested_objects",
        })
    require(
        isinstance(evidence, dict)
        and set(evidence) == expected_keys
        and evidence.get("schema")
        == (
            "iotox-actual-i2p-fail-closed-loss-v2"
            if range_loss
            else "iotox-actual-i2p-fail-closed-loss-v1"
        )
        and evidence.get("role") == "client"
        and isinstance(evidence.get("original_job_id"), int)
        and evidence["original_job_id"] > 0
        and isinstance(evidence.get("replacement_job_id"), int)
        and evidence["replacement_job_id"] > 0
        and evidence["replacement_job_id"] != evidence["original_job_id"]
        and isinstance(evidence.get("position_bytes"), int)
        and isinstance(loss_position_ceiling, int)
        and 65_536
        <= evidence["position_bytes"]
        < loss_position_ceiling
        and re.fullmatch(
            r"[0-9A-F]{64}", str(evidence.get("stopped_carrier", ""))
        )
        is not None
        and hashlib.sha256(
            evidence["stopped_carrier"].encode("ascii")
        ).hexdigest()
        == evidence.get("stopped_carrier_sha256")
        == manifest.get("actual_i2p_payload_carrier_sha256")
        and evidence.get("carrier_losses") == 1
        and evidence.get("reassignments") == 0
        and evidence.get("blocked_jobs") == 1
        and evidence.get("recoveries") == 1
        and evidence.get("route_worker_restarts") == 0
        and evidence.get("old_job_cancelled") is True
        and evidence.get("replacement_same_carrier") is True
        and isinstance(evidence.get("old_client_router_pid"), int)
        and evidence["old_client_router_pid"] > 1
        and isinstance(evidence.get("new_client_router_pid"), int)
        and evidence["new_client_router_pid"] > 1
        and evidence["new_client_router_pid"]
        != evidence["old_client_router_pid"]
        and evidence.get("router_datadir_preserved") is True
        and evidence.get("adapter_listener_reachable_while_sam_down")
        is True
        and evidence.get("client_sam_listener_absent_during_fault") is True
        and evidence.get("adapter_generation_one_lost") is True
        and evidence.get("adapter_generation_two_ready") is True
        and isinstance(evidence.get("fault_hold_ns"), int)
        and evidence["fault_hold_ns"] > 0
        and isinstance(evidence.get("loss_observation_ns"), int)
        and evidence["loss_observation_ns"] > 0
        and isinstance(evidence.get("router_recovery_ns"), int)
        and evidence["router_recovery_ns"] > 0
        and (
            evidence.get("replacement_requested_objects") == 1
            and evidence.get("replacement_committed_objects") == 2
            and evidence.get("manifest_reused_locally") is True
            if range_loss
            else True
        )
        and evidence.get("contains_secrets") is False,
        "actual-I2P fail-closed loss summary is invalid",
    )
    evidence_path = confined(
        proof_root,
        manifest.get("actual_i2p_fail_closed_loss_path"),
        "actual-i2p-fail-closed-loss.json",
    )
    require(
        manifest.get("actual_i2p_fail_closed_loss_sha256")
        == digest(evidence_path)
        and load(evidence_path) == evidence,
        "actual-I2P fail-closed loss file disagrees with the manifest",
    )
    topology = load(
        confined(
            proof_root,
            manifest.get("actual_i2p_topology_path"),
            "i2p-fronts/topology-final.json",
        )
    )
    fault = topology.get("client_router_fault")
    require(
        isinstance(fault, dict)
        and fault.get("old_client_router_pid")
        == evidence["old_client_router_pid"]
        and fault.get("new_client_router_pid")
        == evidence["new_client_router_pid"]
        and fault.get("fault_hold_ns") == evidence["fault_hold_ns"]
        and fault.get("router_datadir_preserved") is True
        and fault.get("adapter_generation_one_lost") is True
        and fault.get("adapter_generation_two_ready") is True,
        "actual-I2P loss record is not joined to router-process evidence",
    )


def verify_route_balance_summary(
    evidence: dict, expected: bool, label: str
) -> None:
    fixed_a = evidence.get("sync_tree_route_balance_fixed_carrier_a", "")
    fixed_b = evidence.get("sync_tree_route_balance_fixed_carrier_b", "")
    adaptive_a = evidence.get(
        "sync_tree_route_balance_adaptive_carrier_a", ""
    )
    adaptive_b = evidence.get(
        "sync_tree_route_balance_adaptive_carrier_b", ""
    )
    phase_order = evidence.get("sync_tree_route_balance_phase_order", "")
    common = (
        evidence.get("sync_tree_route_balance_observed", False) is expected
        and evidence.get(
            "sync_tree_route_balance_fixed_same_carrier", False
        )
        is expected
        and evidence.get(
            "sync_tree_route_balance_adaptive_distinct_carriers", False
        )
        is expected
    )
    if expected:
        values = (
            re.fullmatch(r"[0-9A-F]{64}", str(fixed_a)) is not None
            and fixed_a == fixed_b
            and re.fullmatch(r"[0-9A-F]{64}", str(adaptive_a)) is not None
            and re.fullmatch(r"[0-9A-F]{64}", str(adaptive_b)) is not None
            and adaptive_a != adaptive_b
            and phase_order in {"", "fixed-adaptive", "adaptive-fixed"}
            and evidence.get("sync_tree_route_balance_fixed_selections", 0)
            == 2
            and evidence.get(
                "sync_tree_route_balance_adaptive_selections", 0
            )
            == 2
            and evidence.get(
                "sync_tree_route_balance_fixed_duration_ms", 0
            )
            > 0
            and evidence.get(
                "sync_tree_route_balance_adaptive_duration_ms", 0
            )
            > 0
            and evidence.get("sync_tree_route_balance_activations", 0) == 4
            and evidence.get(
                "sync_tree_route_balance_artifact_bytes", 0
            )
            == 8259
            and evidence.get(
                "sync_tree_route_balance_fixed_head_retries", 0
            )
            >= 0
            and evidence.get(
                "sync_tree_route_balance_fixed_head_retries", 0
            )
            <= 16
            and evidence.get(
                "sync_tree_route_balance_adaptive_head_retries", 0
            )
            >= 0
            and evidence.get(
                "sync_tree_route_balance_adaptive_head_retries", 0
            )
            <= 16
        )
    else:
        values = (
            fixed_a == ""
            and fixed_b == ""
            and adaptive_a == ""
            and adaptive_b == ""
            and phase_order == ""
            and evidence.get("sync_tree_route_balance_fixed_selections", 0)
            == 0
            and evidence.get(
                "sync_tree_route_balance_adaptive_selections", 0
            )
            == 0
            and evidence.get(
                "sync_tree_route_balance_fixed_duration_ms", 0
            )
            == 0
            and evidence.get(
                "sync_tree_route_balance_adaptive_duration_ms", 0
            )
            == 0
            and evidence.get("sync_tree_route_balance_activations", 0) == 0
            and evidence.get(
                "sync_tree_route_balance_artifact_bytes", 0
            )
            == 0
            and evidence.get(
                "sync_tree_route_balance_fixed_head_retries", 0
            )
            == 0
            and evidence.get(
                "sync_tree_route_balance_adaptive_head_retries", 0
            )
            == 0
        )
    require(common and values, f"{label} route-balance evidence is invalid")


def verify_route_startup_order_receipt(
    evidence: dict, expected: bool, label: str
) -> None:
    phase_one = evidence.get(
        "sync_tree_route_startup_phase_one_first", ""
    )
    phase_two = evidence.get(
        "sync_tree_route_startup_phase_two_first", ""
    )
    if expected:
        valid = (
            evidence.get("sync_tree_route_startup_order_observed", False)
            is True
            and evidence.get("sync_tree_route_startup_delay_ms", 0)
            == 20_000
            and evidence.get("sync_tree_route_startup_restart_count", 0)
            == 1
            and evidence.get(
                "sync_tree_route_startup_phase_one_stable_samples", 0
            )
            == 10
            and evidence.get(
                "sync_tree_route_startup_phase_two_stable_samples", 0
            )
            == 10
            and re.fullmatch(r"[0-9A-F]{64}", str(phase_one)) is not None
            and re.fullmatch(r"[0-9A-F]{64}", str(phase_two)) is not None
            and phase_one != phase_two
            and 0
            < evidence.get("sync_tree_route_startup_phase_one_ms", 0)
            < 20_000
            and 0
            < evidence.get("sync_tree_route_startup_phase_two_ms", 0)
            < 20_000
        )
    else:
        valid = (
            evidence.get("sync_tree_route_startup_order_observed", False)
            is False
            and evidence.get("sync_tree_route_startup_delay_ms", 0) == 0
            and evidence.get("sync_tree_route_startup_restart_count", 0)
            == 0
            and evidence.get(
                "sync_tree_route_startup_phase_one_stable_samples", 0
            )
            == 0
            and evidence.get(
                "sync_tree_route_startup_phase_two_stable_samples", 0
            )
            == 0
            and evidence.get("sync_tree_route_startup_phase_one_ms", 0) == 0
            and evidence.get("sync_tree_route_startup_phase_two_ms", 0) == 0
            and phase_one == ""
            and phase_two == ""
        )
    require(valid, f"{label} route startup-order evidence is invalid")


def verify_route_population_summary(
    evidence: dict, expected: bool, label: str
) -> None:
    fixed_resource = evidence.get(
        "sync_tree_route_population_fixed_resource_sha256", ""
    )
    adaptive_resource = evidence.get(
        "sync_tree_route_population_adaptive_resource_sha256", ""
    )
    observed = (
        evidence.get("sync_tree_route_population_observed", False)
        is expected
    )
    if expected:
        values = (
            evidence.get("sync_tree_route_population_jobs") == 8
            and 131_072
            < evidence.get("sync_tree_route_population_artifact_bytes", 0)
            < 262_144
            and evidence.get("sync_tree_route_population_fixed_pattern")
            == "00001111"
            and evidence.get("sync_tree_route_population_adaptive_pattern")
            == "01010101"
            and evidence.get(
                "sync_tree_route_population_fixed_max_prefix_imbalance"
            )
            == 4
            and evidence.get(
                "sync_tree_route_population_adaptive_max_prefix_imbalance"
            )
            == 1
            and evidence.get(
                "sync_tree_route_population_fixed_progress_jobs"
            )
            == 8
            and evidence.get(
                "sync_tree_route_population_adaptive_progress_jobs"
            )
            == 8
            and evidence.get(
                "sync_tree_route_population_fixed_progress_observation_spread_ms", -1
            )
            >= 0
            and evidence.get(
                "sync_tree_route_population_adaptive_progress_observation_spread_ms",
                -1,
            )
            >= 0
            and evidence.get(
                "sync_tree_route_population_fixed_duration_ms", 0
            )
            > 0
            and evidence.get(
                "sync_tree_route_population_adaptive_duration_ms", 0
            )
            > 0
            and evidence.get("sync_tree_route_population_activations") == 16
            and SHA256.fullmatch(str(fixed_resource)) is not None
            and SHA256.fullmatch(str(adaptive_resource)) is not None
        )
    else:
        integer_fields = (
            "sync_tree_route_population_jobs",
            "sync_tree_route_population_artifact_bytes",
            "sync_tree_route_population_fixed_max_prefix_imbalance",
            "sync_tree_route_population_adaptive_max_prefix_imbalance",
            "sync_tree_route_population_fixed_progress_jobs",
            "sync_tree_route_population_adaptive_progress_jobs",
            "sync_tree_route_population_fixed_progress_observation_spread_ms",
            "sync_tree_route_population_adaptive_progress_observation_spread_ms",
            "sync_tree_route_population_fixed_duration_ms",
            "sync_tree_route_population_adaptive_duration_ms",
            "sync_tree_route_population_activations",
        )
        values = (
            all(evidence.get(field, 0) == 0 for field in integer_fields)
            and evidence.get(
                "sync_tree_route_population_fixed_pattern", ""
            )
            == ""
            and evidence.get(
                "sync_tree_route_population_adaptive_pattern", ""
            )
            == ""
            and fixed_resource == ""
            and adaptive_resource == ""
        )
    require(observed and values, f"{label} route-population evidence is invalid")


def verify_route_concurrent_cancel_summary(
    evidence: dict,
    expected: bool,
    label: str,
    expected_artifact_bytes: int = 262_211,
) -> None:
    resource = evidence.get(
        "sync_tree_route_concurrent_cancel_resource_sha256", ""
    )
    observed = (
        evidence.get("sync_tree_route_concurrent_cancel_observed", False)
        is expected
    )
    if "sync_tree_route_concurrent_cancel_observed_role_count" in evidence:
        observed = (
            evidence.get(
                "sync_tree_route_concurrent_cancel_observed_role_count", 0
            )
            == int(expected)
        )
    if expected:
        values = (
            evidence.get("sync_tree_route_concurrent_cancel_jobs") == 8
            and evidence.get(
                "sync_tree_route_concurrent_cancel_artifact_bytes"
            )
            == expected_artifact_bytes
            and evidence.get("sync_tree_route_concurrent_cancel_requested")
            == 4
            and evidence.get("sync_tree_route_concurrent_cancel_completed")
            == 4
            and evidence.get("sync_tree_route_concurrent_cancel_survivors")
            == 4
            and evidence.get(
                "sync_tree_route_concurrent_cancel_survivor_activations"
            )
            == 4
            and evidence.get("sync_tree_route_concurrent_cancel_pattern")
            == "01010101"
            and evidence.get("sync_tree_route_concurrent_cancel_route_zero")
            == 2
            and evidence.get("sync_tree_route_concurrent_cancel_route_one")
            == 2
            and 0
            <= evidence.get("sync_tree_route_concurrent_cancel_tail_ms", -1)
            <= 5000
            and evidence.get(
                "sync_tree_route_concurrent_cancel_work_before", 0
            )
            > 0
            and evidence.get("sync_tree_route_concurrent_cancel_work_after")
            == 0
            and evidence.get(
                "sync_tree_route_concurrent_cancel_reassignments_delta"
            )
            == 0
            and evidence.get(
                "sync_tree_route_concurrent_cancel_adaptive_selections"
            )
            == 8
            and SHA256.fullmatch(str(resource)) is not None
        )
    else:
        integer_fields = (
            "sync_tree_route_concurrent_cancel_jobs",
            "sync_tree_route_concurrent_cancel_artifact_bytes",
            "sync_tree_route_concurrent_cancel_requested",
            "sync_tree_route_concurrent_cancel_completed",
            "sync_tree_route_concurrent_cancel_survivors",
            "sync_tree_route_concurrent_cancel_survivor_activations",
            "sync_tree_route_concurrent_cancel_route_zero",
            "sync_tree_route_concurrent_cancel_route_one",
            "sync_tree_route_concurrent_cancel_tail_ms",
            "sync_tree_route_concurrent_cancel_work_before",
            "sync_tree_route_concurrent_cancel_work_after",
            "sync_tree_route_concurrent_cancel_reassignments_delta",
            "sync_tree_route_concurrent_cancel_adaptive_selections",
        )
        values = (
            all(evidence.get(field, 0) == 0 for field in integer_fields)
            and evidence.get(
                "sync_tree_route_concurrent_cancel_pattern", ""
            )
            == ""
            and resource == ""
        )
    require(
        observed and values,
        f"{label} concurrent route-cancellation evidence is invalid",
    )


def verify_common_link_fairness_qdisc(
    evidence: object, expected: bool, label: str
) -> None:
    require(isinstance(evidence, dict), f"{label} is not an object")
    if not expected:
        require(evidence == {}, f"{label} appears outside its scenario")
        return
    expected_keys = {
        "schema",
        "tap",
        "root_kind",
        "root_handle",
        "class_kind",
        "class_handle",
        "rate_bytes_per_second",
        "ceil_bytes_per_second",
        "leaf_kind",
        "leaf_handle",
        "leaf_parent",
        "leaf_limit_packets",
        "active_leaf_flow_count",
        "fq_codel_bytes",
        "fq_codel_packets",
        "fq_codel_drops",
        "fq_codel_overlimits",
        "fq_codel_requeues",
        "htb_bytes",
        "htb_packets",
        "htb_drops",
        "htb_overlimits",
        "htb_requeues",
    }
    require(set(evidence) == expected_keys, f"{label} schema drifted")
    require(
        evidence.get("schema") == "iotox-common-link-fairness-v1"
        and evidence.get("tap") == "vm-iotoxc"
        and evidence.get("root_kind") == "htb"
        and evidence.get("root_handle") == "1:"
        and evidence.get("class_kind") == "htb"
        and evidence.get("class_handle") == "1:1"
        and evidence.get("rate_bytes_per_second") == 500_000
        and evidence.get("ceil_bytes_per_second") == 500_000
        and evidence.get("leaf_kind") == "fq_codel"
        and evidence.get("leaf_handle") == "10:"
        and evidence.get("leaf_parent") == "1:1"
        and evidence.get("leaf_limit_packets") == 1000,
        f"{label} topology or rate drifted",
    )
    for field in expected_keys - {
        "schema",
        "tap",
        "root_kind",
        "root_handle",
        "class_kind",
        "class_handle",
        "leaf_kind",
        "leaf_handle",
        "leaf_parent",
    }:
        require(
            isinstance(evidence[field], int) and evidence[field] >= 0,
            f"{label} has invalid {field}",
        )
    require(
        evidence["fq_codel_bytes"] > 0
        and evidence["fq_codel_packets"] > 0
        and evidence["htb_bytes"] > 0
        and evidence["htb_packets"] > 0,
        f"{label} did not carry traffic",
    )


def verify_route_population_loss_summary(
    evidence: dict, expected: bool, label: str, admission: bool = False
) -> None:
    resource = evidence.get(
        "sync_tree_route_population_loss_resource_sha256", ""
    )
    stopped = evidence.get(
        "sync_tree_route_population_loss_stopped_carrier", ""
    )
    observed = (
        evidence.get("sync_tree_route_population_loss_observed", False)
        is expected
    )
    if "sync_tree_route_population_loss_observed_role_count" in evidence:
        observed = (
            evidence.get(
                "sync_tree_route_population_loss_observed_role_count", 0
            )
            == int(expected)
        )
    if expected:
        expected_jobs = 4 if admission else 8
        expected_pattern = "00" if admission else "00001111"
        expected_affected = 2 if admission else 4
        expected_selections = 6 if admission else 12
        expected_work = 4 if admission else 16
        expected_delay = 1 if admission else 750
        survivor = evidence.get(
            "sync_tree_route_loss_admission_surviving_carrier", ""
        )
        values = (
            evidence.get("sync_tree_route_population_loss_jobs")
            == expected_jobs
            and evidence.get(
                "sync_tree_route_population_loss_artifact_bytes"
            )
            == 524_355
            and evidence.get("sync_tree_route_population_loss_pattern")
            == expected_pattern
            and evidence.get(
                "sync_tree_route_population_loss_affected_jobs"
            )
            == expected_affected
            and evidence.get(
                "sync_tree_route_population_loss_carrier_losses"
            )
            == 1
            and evidence.get(
                "sync_tree_route_population_loss_reassignments"
            )
            == expected_affected
            and evidence.get(
                "sync_tree_route_population_loss_stale_terminals", 0
            )
            >= 1
            and evidence.get("sync_tree_route_population_loss_recoveries")
            == 1
            and evidence.get(
                "sync_tree_route_population_loss_fixed_selections"
            )
            == expected_selections
            and evidence.get("sync_tree_route_population_loss_activations")
            == expected_jobs
            and evidence.get("sync_tree_route_population_loss_work_before")
            == expected_work
            and evidence.get("sync_tree_route_population_loss_work_after")
            == 0
            and evidence.get(
                "sync_tree_route_population_loss_fault_delay_ms"
            )
            == expected_delay
            and 65_536
            <= evidence.get(
                "sync_tree_route_population_loss_fault_position_bytes", 0
            )
            < 524_355
            and evidence.get(
                "sync_tree_route_population_loss_duration_ms", 0
            )
            > 0
            and re.fullmatch(r"[0-9A-F]{64}", str(stopped)) is not None
            and SHA256.fullmatch(str(resource)) is not None
            and evidence.get(
                "sync_tree_route_loss_admission_started_jobs", 0
            )
            == (2 if admission else 0)
            and evidence.get(
                "sync_tree_route_loss_admission_ready_bulk", 0
            )
            == (1 if admission else 0)
            and (
                re.fullmatch(r"[0-9A-F]{64}", str(survivor)) is not None
                and survivor != stopped
                if admission
                else survivor == ""
            )
        )
    else:
        integer_fields = (
            "sync_tree_route_population_loss_jobs",
            "sync_tree_route_population_loss_artifact_bytes",
            "sync_tree_route_population_loss_affected_jobs",
            "sync_tree_route_population_loss_carrier_losses",
            "sync_tree_route_population_loss_reassignments",
            "sync_tree_route_population_loss_stale_terminals",
            "sync_tree_route_population_loss_recoveries",
            "sync_tree_route_population_loss_fixed_selections",
            "sync_tree_route_population_loss_activations",
            "sync_tree_route_population_loss_work_before",
            "sync_tree_route_population_loss_work_after",
            "sync_tree_route_population_loss_fault_delay_ms",
            "sync_tree_route_population_loss_fault_position_bytes",
            "sync_tree_route_population_loss_duration_ms",
            "sync_tree_route_loss_admission_started_jobs",
            "sync_tree_route_loss_admission_ready_bulk",
        )
        values = (
            all(evidence.get(field, 0) == 0 for field in integer_fields)
            and evidence.get("sync_tree_route_population_loss_pattern", "")
            == ""
            and stopped == ""
            and resource == ""
            and evidence.get(
                "sync_tree_route_loss_admission_surviving_carrier", ""
            )
            == ""
        )
    require(
        observed and values,
        f"{label} route-population loss evidence is invalid",
    )


def verify_route_startup_admission_summary(
    evidence: dict, expected: bool, label: str
) -> None:
    carrier = evidence.get(
        "sync_tree_route_startup_admission_carrier", ""
    )
    resource = evidence.get(
        "sync_tree_route_startup_admission_resource_sha256", ""
    )
    observed = (
        evidence.get("sync_tree_route_startup_admission_observed", False)
        is expected
    )
    if "sync_tree_route_startup_admission_observed_role_count" in evidence:
        observed = (
            evidence.get(
                "sync_tree_route_startup_admission_observed_role_count", 0
            )
            == int(expected)
        )
    if expected:
        values = (
            evidence.get("sync_tree_route_startup_admission_jobs") == 2
            and evidence.get(
                "sync_tree_route_startup_admission_artifact_bytes"
            )
            == 16_777_283
            and evidence.get("sync_tree_route_startup_admission_delay_ms")
            == 20_000
            and evidence.get(
                "sync_tree_route_startup_admission_restart_count"
            )
            == 1
            and evidence.get(
                "sync_tree_route_startup_admission_ready_bulk_before"
            )
            == 1
            and evidence.get(
                "sync_tree_route_startup_admission_ready_bulk_after"
            )
            == 2
            and evidence.get(
                "sync_tree_route_startup_admission_stable_samples", 0
            )
            >= 10
            and re.fullmatch(r"[0-9A-F]{64}", str(carrier)) is not None
            and evidence.get(
                "sync_tree_route_startup_admission_live_jobs_after_join"
            )
            == 2
            and evidence.get(
                "sync_tree_route_startup_admission_preserved_carriers"
            )
            == 2
            and evidence.get(
                "sync_tree_route_startup_admission_adaptive_selections"
            )
            == 2
            and evidence.get(
                "sync_tree_route_startup_admission_activations"
            )
            == 2
            and evidence.get(
                "sync_tree_route_startup_admission_work_before"
            )
            == 4
            and evidence.get(
                "sync_tree_route_startup_admission_work_after"
            )
            == 0
            and evidence.get(
                "sync_tree_route_startup_admission_duration_ms", 0
            )
            > 0
            and SHA256.fullmatch(str(resource)) is not None
        )
    else:
        integer_fields = (
            "sync_tree_route_startup_admission_jobs",
            "sync_tree_route_startup_admission_artifact_bytes",
            "sync_tree_route_startup_admission_delay_ms",
            "sync_tree_route_startup_admission_restart_count",
            "sync_tree_route_startup_admission_ready_bulk_before",
            "sync_tree_route_startup_admission_ready_bulk_after",
            "sync_tree_route_startup_admission_stable_samples",
            "sync_tree_route_startup_admission_live_jobs_after_join",
            "sync_tree_route_startup_admission_preserved_carriers",
            "sync_tree_route_startup_admission_adaptive_selections",
            "sync_tree_route_startup_admission_activations",
            "sync_tree_route_startup_admission_work_before",
            "sync_tree_route_startup_admission_work_after",
            "sync_tree_route_startup_admission_duration_ms",
        )
        values = (
            all(evidence.get(field, 0) == 0 for field in integer_fields)
            and carrier == ""
            and resource == ""
        )
    require(
        observed and values,
        f"{label} route-startup admission evidence is invalid",
    )


def verify_route_throughput_summary(
    evidence: dict, expected: bool, label: str
) -> None:
    observed = (
        evidence.get("sync_tree_route_throughput_observed", False)
        is expected
    )
    if "sync_tree_route_throughput_observed_role_count" in evidence:
        observed = (
            evidence.get(
                "sync_tree_route_throughput_observed_role_count", 0
            )
            == int(expected)
        )
    duration_fields = (
        "sync_tree_route_throughput_fixed_a_duration_ms",
        "sync_tree_route_throughput_adaptive_a_duration_ms",
        "sync_tree_route_throughput_adaptive_b_duration_ms",
        "sync_tree_route_throughput_fixed_b_duration_ms",
    )
    skew_fields = (
        "sync_tree_route_throughput_fixed_a_completion_skew_ms",
        "sync_tree_route_throughput_adaptive_a_completion_skew_ms",
        "sync_tree_route_throughput_adaptive_b_completion_skew_ms",
        "sync_tree_route_throughput_fixed_b_completion_skew_ms",
    )
    resource_fields = (
        "sync_tree_route_throughput_fixed_a_resource_sha256",
        "sync_tree_route_throughput_adaptive_a_resource_sha256",
        "sync_tree_route_throughput_adaptive_b_resource_sha256",
        "sync_tree_route_throughput_fixed_b_resource_sha256",
    )
    durations = tuple(evidence.get(field, 0) for field in duration_fields)
    skews = tuple(evidence.get(field, 0) for field in skew_fields)
    resources = tuple(evidence.get(field, "") for field in resource_fields)
    fixed_total = evidence.get(
        "sync_tree_route_throughput_fixed_total_duration_ms", 0
    )
    adaptive_total = evidence.get(
        "sync_tree_route_throughput_adaptive_total_duration_ms", 0
    )
    policy_bytes = 4 * 16_777_283
    if expected:
        values = (
            evidence.get("sync_tree_route_throughput_jobs_per_phase") == 2
            and evidence.get("sync_tree_route_throughput_phases") == 4
            and evidence.get("sync_tree_route_throughput_artifact_bytes")
            == 16_777_283
            and evidence.get("sync_tree_route_throughput_phase_order")
            == "fixed-a,adaptive-a,adaptive-b,fixed-b"
            and evidence.get("sync_tree_route_throughput_restart_count") == 4
            and evidence.get(
                "sync_tree_route_throughput_restart_hold_ms"
            )
            == 5000
            and evidence.get("sync_tree_route_throughput_fixed_patterns")
            == "00,00"
            and evidence.get("sync_tree_route_throughput_adaptive_patterns")
            == "01,01"
            and all(value > 0 for value in durations)
            and all(
                0 <= skew <= duration
                for skew, duration in zip(skews, durations)
            )
            and fixed_total == durations[0] + durations[3]
            and adaptive_total == durations[1] + durations[2]
            and evidence.get("sync_tree_route_throughput_fixed_artifact_bps")
            == policy_bytes * 1000 // fixed_total
            and evidence.get(
                "sync_tree_route_throughput_adaptive_artifact_bps"
            )
            == policy_bytes * 1000 // adaptive_total
            and evidence.get(
                "sync_tree_route_throughput_adaptive_speedup_ppm"
            )
            == fixed_total * 1_000_000 // adaptive_total
            and evidence.get("sync_tree_route_throughput_fixed_selections")
            == 4
            and evidence.get("sync_tree_route_throughput_adaptive_selections")
            == 4
            and evidence.get("sync_tree_route_throughput_reassignments") == 0
            and evidence.get("sync_tree_route_throughput_activations") == 8
            and evidence.get("sync_tree_route_throughput_peak_work") == 4
            and evidence.get("sync_tree_route_throughput_work_after") == 0
            and all(SHA256.fullmatch(str(value)) is not None for value in resources)
        )
    else:
        integer_fields = (
            "sync_tree_route_throughput_jobs_per_phase",
            "sync_tree_route_throughput_phases",
            "sync_tree_route_throughput_artifact_bytes",
            "sync_tree_route_throughput_restart_count",
            "sync_tree_route_throughput_restart_hold_ms",
            *duration_fields,
            *skew_fields,
            "sync_tree_route_throughput_fixed_total_duration_ms",
            "sync_tree_route_throughput_adaptive_total_duration_ms",
            "sync_tree_route_throughput_fixed_artifact_bps",
            "sync_tree_route_throughput_adaptive_artifact_bps",
            "sync_tree_route_throughput_adaptive_speedup_ppm",
            "sync_tree_route_throughput_fixed_selections",
            "sync_tree_route_throughput_adaptive_selections",
            "sync_tree_route_throughput_reassignments",
            "sync_tree_route_throughput_activations",
            "sync_tree_route_throughput_peak_work",
            "sync_tree_route_throughput_work_after",
        )
        values = (
            all(evidence.get(field, 0) == 0 for field in integer_fields)
            and evidence.get("sync_tree_route_throughput_phase_order", "")
            == ""
            and evidence.get("sync_tree_route_throughput_fixed_patterns", "")
            == ""
            and evidence.get(
                "sync_tree_route_throughput_adaptive_patterns", ""
            )
            == ""
            and all(value == "" for value in resources)
        )
    require(
        observed and values,
        f"{label} route-throughput evidence is invalid",
    )


def verify_loss_before_cancel_order(evidence: dict, label: str) -> None:
    cancel_carrier = evidence.get("sync_tree_route_cancel_carrier", "")
    final_carrier = evidence.get("sync_tree_route_loss_final_carrier", "")
    stopped_carrier = evidence.get(
        "sync_tree_route_loss_stopped_carrier", ""
    )
    require(
        evidence.get("sync_tree_route_loss_observed", False) is True
        and evidence.get("sync_tree_route_cancel_observed", False) is True
        and evidence.get("sync_tree_route_loss_position_bytes", 0) >= 65_536
        and evidence.get("sync_tree_route_loss_carrier_losses") == 1
        and evidence.get("sync_tree_route_loss_reassignments") == 1
        and evidence.get("sync_tree_route_loss_stale_terminals", 0) >= 1
        and evidence.get("sync_tree_route_loss_recoveries") == 1
        and evidence.get("sync_tree_route_cancel_adaptive_selections") == 2
        and evidence.get("sync_tree_route_cancel_reassignments_delta") == 0
        and re.fullmatch(r"[0-9A-F]{64}", str(cancel_carrier)) is not None
        and cancel_carrier == final_carrier
        and cancel_carrier != stopped_carrier
        and re.fullmatch(r"[0-9A-F]{64}", str(stopped_carrier)) is not None,
        f"{label} loss-before-cancel order is invalid",
    )


def verify_route_resume(
    evidence: dict,
    allowed: bool,
    label: str,
    expected_attempts: int | None = None,
) -> None:
    observed = evidence.get("sync_tree_route_resume_observed", False)
    retained = evidence.get("sync_tree_route_loss_retained_partials", 0)
    retained_attempts = evidence.get(
        "sync_tree_route_loss_retained_attempts", 0
    )
    retained_bytes = evidence.get("sync_tree_route_loss_retained_bytes", 0)
    retention_fallbacks = evidence.get(
        "sync_tree_route_loss_retention_fallbacks", 0
    )
    attempts = evidence.get("sync_tree_route_loss_resumed_attempts", 0)
    resumed = evidence.get("sync_tree_route_loss_resumed_bytes", 0)
    position = evidence.get("sync_tree_route_loss_position_bytes", 0)
    require(
        isinstance(observed, bool)
        and (
            observed is True
            and allowed
            and retained == 0
            and (
                retained_attempts == expected_attempts
                if expected_attempts is not None
                else 1 <= retained_attempts <= 2
            )
            and (
                retained_bytes > position
                if expected_attempts is not None
                and expected_attempts > 1
                else retained_bytes >= position
            )
            and retention_fallbacks == 0
            and attempts == retained_attempts
            and resumed == retained_bytes
            and resumed >= 65_536
            or observed is False
            and retained == 0
            and retained_attempts == 0
            and retained_bytes == 0
            and retention_fallbacks == 0
            and attempts == 0
            and resumed == 0
        ),
        f"{label} route-prefix resume evidence is invalid",
    )


def verify_cancel_before_loss_order(evidence: dict, label: str) -> None:
    cancel_carrier = evidence.get("sync_tree_route_cancel_carrier", "")
    final_carrier = evidence.get("sync_tree_route_loss_final_carrier", "")
    stopped_carrier = evidence.get(
        "sync_tree_route_loss_stopped_carrier", ""
    )
    require(
        evidence.get("sync_tree_route_cancel_loss_observed", False) is True
        and evidence.get("sync_tree_route_loss_observed", False) is True
        and evidence.get("sync_tree_route_cancel_observed", False) is True
        and evidence.get("sync_tree_route_loss_position_bytes", -1) == 0
        and evidence.get("sync_tree_route_loss_carrier_losses") == 1
        and evidence.get("sync_tree_route_loss_reassignments") == 0
        and evidence.get("sync_tree_route_loss_stale_terminals", 0) >= 1
        and evidence.get("sync_tree_route_loss_recoveries") == 1
        and evidence.get("sync_tree_route_cancel_adaptive_selections") == 1
        and evidence.get("sync_tree_route_cancel_reassignments_delta") == 0
        and re.fullmatch(r"[0-9A-F]{64}", str(cancel_carrier)) is not None
        and cancel_carrier == final_carrier == stopped_carrier,
        f"{label} cancel-before-loss order is invalid",
    )


def verify_cancel_loss_race_order(
    evidence: dict,
    label: str,
    expected_fault_delay: int = 500,
    expected_cancel_delay: int = 500,
    required_outcome: str | None = None,
) -> None:
    cancel_carrier = evidence.get("sync_tree_route_cancel_carrier", "")
    final_carrier = evidence.get("sync_tree_route_loss_final_carrier", "")
    stopped_carrier = evidence.get(
        "sync_tree_route_loss_stopped_carrier", ""
    )
    reassignments = evidence.get("sync_tree_route_loss_reassignments")
    outcome = evidence.get("sync_tree_route_cancel_race_outcome", "")
    require(
        evidence.get("sync_tree_route_cancel_race_observed", False) is True
        and evidence.get("sync_tree_route_loss_observed", False) is True
        and evidence.get("sync_tree_route_cancel_observed", False) is True
        and 65_536
        <= evidence.get("sync_tree_route_loss_position_bytes", 0)
        < SYNC_SCENARIOS["sync-tree-route-cancel-race"]
        and evidence.get("sync_tree_route_loss_carrier_losses") == 1
        and reassignments in {0, 1}
        and evidence.get("sync_tree_route_loss_stale_terminals", -1) >= 0
        and evidence.get("sync_tree_route_loss_recoveries") == 1
        and evidence.get("sync_tree_route_cancel_reassignments_delta")
        == reassignments
        and evidence.get("sync_tree_route_cancel_adaptive_selections")
        == 1 + reassignments
        and evidence.get("sync_tree_route_cancel_race_fault_delay_ms")
        == expected_fault_delay
        and evidence.get("sync_tree_route_cancel_race_cancel_delay_ms")
        == expected_cancel_delay
        and evidence.get("sync_tree_route_cancel_race_cleanup_retries")
        in {0, 1}
        and re.fullmatch(r"[0-9A-F]{64}", str(cancel_carrier)) is not None
        and cancel_carrier == stopped_carrier
        and (required_outcome is None or outcome == required_outcome)
        and (
            outcome == "cancel-first"
            and reassignments == 0
            and final_carrier == stopped_carrier
            or outcome == "loss-first"
            and reassignments == 1
            and final_carrier != stopped_carrier
            and re.fullmatch(r"[0-9A-F]{64}", str(final_carrier))
            is not None
        ),
        f"{label} cancel/loss race order is invalid",
    )


def verify_ratox_agent_status(text: str, role: str) -> None:
    lines = text.splitlines()
    for field in (
        "transport-pending-events",
        "transport-maximum-pending-events",
        "transport-required-event-backpressure-count",
        "transport-required-event-backpressure-total-us",
        "transport-required-event-backpressure-maximum-us",
    ):
        require(
            sum(line.startswith(field + "=") for line in lines) == 1,
            f"{role} Ratox agent status lacks {field}",
        )

    pacing_fields = (
        "transport-file-pacing-paused-transfers",
        "transport-file-pacing-high-watermark",
        "transport-file-pacing-low-watermark",
        "transport-file-pacing-minimum-hold-us",
        "transport-file-pacing-pause-count",
        "transport-file-pacing-resume-count",
        "transport-file-pacing-pause-failure-count",
        "transport-file-pacing-resume-failure-count",
        "transport-file-pacing-total-hold-us",
        "transport-file-pacing-maximum-hold-us",
    )
    matching = {
        field: [line for line in lines if line.startswith(field + "=")]
        for field in pacing_fields
    }
    present = sum(bool(values) for values in matching.values())
    # Proofs captured before ADR 0160 remain valid. Once any pacing evidence
    # appears, require the complete scheduler state rather than a partial view.
    require(
        present in {0, len(pacing_fields)},
        f"{role} Ratox file-pacing evidence is incomplete",
    )
    if present == 0:
        return

    values: dict[str, int] = {}
    for field, records in matching.items():
        require(
            len(records) == 1,
            f"{role} Ratox agent status duplicates {field}",
        )
        value = records[0].removeprefix(field + "=")
        require(
            value.isascii() and value.isdecimal(),
            f"{role} Ratox agent status has noncanonical {field}",
        )
        values[field] = int(value)

    paused = values["transport-file-pacing-paused-transfers"]
    high = values["transport-file-pacing-high-watermark"]
    low = values["transport-file-pacing-low-watermark"]
    hold = values["transport-file-pacing-minimum-hold-us"]
    pauses = values["transport-file-pacing-pause-count"]
    resumes = values["transport-file-pacing-resume-count"]
    total_hold = values["transport-file-pacing-total-hold-us"]
    maximum_hold = values["transport-file-pacing-maximum-hold-us"]
    require(paused == 0, f"{role} Ratox file pacer did not quiesce")
    require(0 <= low < high, f"{role} Ratox file-pacing watermarks are invalid")
    require(
        100 <= hold <= 1_000_000,
        f"{role} Ratox file-pacing minimum hold is invalid",
    )
    require(
        pauses >= resumes,
        f"{role} Ratox file-pacing resume count exceeds pause count",
    )
    if resumes == 0:
        require(
            total_hold == 0 and maximum_hold == 0,
            f"{role} Ratox file-pacing hold time lacks a resume",
        )
    else:
        require(
            total_hold >= maximum_hold >= hold,
            f"{role} Ratox file-pacing hold accounting is invalid",
        )

    external_pause_field = "transport-file-pacing-external-pause-count"
    external_pause_records = [
        line for line in lines if line.startswith(external_pause_field + "=")
    ]
    require(
        len(external_pause_records) <= 1,
        f"{role} Ratox agent status duplicates {external_pause_field}",
    )
    if external_pause_records:
        external_pause = external_pause_records[0].removeprefix(
            external_pause_field + "="
        )
        require(
            external_pause.isascii() and external_pause.isdecimal(),
            f"{role} Ratox agent status has noncanonical {external_pause_field}",
        )
        require(
            values["transport-file-pacing-pause-failure-count"] == 0
            and values["transport-file-pacing-resume-failure-count"] == 0,
            f"{role} coordinated file pacing recorded a control failure",
        )
        last_events = [
            line.removeprefix("last-event=")
            for line in lines
            if line.startswith("last-event=")
        ]
        require(
            len(last_events) == 1
            and not last_events[0].startswith("file-transfer-failed:"),
            f"{role} coordinated file pacing ended on a file-transfer failure",
        )

    batch_fields = (
        "transport-file-pacing-resume-batch-limit",
        "transport-file-pacing-resume-batch-count",
        "transport-file-pacing-resume-batch-maximum",
    )
    batch_matching = {
        field: [line for line in lines if line.startswith(field + "=")]
        for field in batch_fields
    }
    batch_present = sum(bool(records) for records in batch_matching.values())
    # ADR 0160 proofs predate bounded resume batches. If a new scheduler field
    # appears, require the complete generation and its accounting invariants.
    require(
        batch_present in {0, len(batch_fields)},
        f"{role} Ratox file-pacing batch evidence is incomplete",
    )
    if batch_present != 0:
        batch_values: dict[str, int] = {}
        for field, records in batch_matching.items():
            require(
                len(records) == 1,
                f"{role} Ratox agent status duplicates {field}",
            )
            value = records[0].removeprefix(field + "=")
            require(
                value.isascii() and value.isdecimal(),
                f"{role} Ratox agent status has noncanonical {field}",
            )
            batch_values[field] = int(value)
        batch_limit = batch_values["transport-file-pacing-resume-batch-limit"]
        batch_count = batch_values["transport-file-pacing-resume-batch-count"]
        batch_maximum = batch_values[
            "transport-file-pacing-resume-batch-maximum"
        ]
        require(
            1 <= batch_limit <= 1024
            and batch_count <= resumes
            and batch_maximum <= batch_limit
            and (
                batch_count == 0 and batch_maximum == 0 and resumes == 0
                or batch_count > 0
                and batch_maximum > 0
                and resumes <= batch_count * batch_limit
            ),
            f"{role} Ratox file-pacing batch accounting is invalid",
        )

    carrier_fields = (
        "file-carrier-window-per-peer",
        "file-carrier-rotation-quantum-ms",
        "file-carrier-runnable-receives",
        "file-carrier-waiting-receives",
        "file-carrier-admission-count",
        "file-carrier-rotation-count",
        "file-carrier-pause-count",
        "file-carrier-resume-count",
        "file-carrier-control-failure-count",
        "file-carrier-total-wait-us",
        "file-carrier-maximum-wait-us",
    )
    carrier_matching = {
        field: [line for line in lines if line.startswith(field + "=")]
        for field in carrier_fields
    }
    carrier_present = sum(
        bool(records) for records in carrier_matching.values()
    )
    require(
        carrier_present in {0, len(carrier_fields)},
        f"{role} Ratox file-carrier evidence is incomplete",
    )
    if carrier_present == 0:
        return
    carrier_values: dict[str, int] = {}
    for field, records in carrier_matching.items():
        require(
            len(records) == 1,
            f"{role} Ratox agent status duplicates {field}",
        )
        value = records[0].removeprefix(field + "=")
        require(
            value.isascii() and value.isdecimal(),
            f"{role} Ratox agent status has noncanonical {field}",
        )
        carrier_values[field] = int(value)
    window = carrier_values["file-carrier-window-per-peer"]
    quantum = carrier_values["file-carrier-rotation-quantum-ms"]
    runnable = carrier_values["file-carrier-runnable-receives"]
    waiting = carrier_values["file-carrier-waiting-receives"]
    admissions = carrier_values["file-carrier-admission-count"]
    rotations = carrier_values["file-carrier-rotation-count"]
    carrier_pauses = carrier_values["file-carrier-pause-count"]
    carrier_resumes = carrier_values["file-carrier-resume-count"]
    failures = carrier_values["file-carrier-control-failure-count"]
    total_wait = carrier_values["file-carrier-total-wait-us"]
    maximum_wait = carrier_values["file-carrier-maximum-wait-us"]
    require(
        1 <= window <= 256
        and 5 <= quantum <= 1000
        and runnable == 0
        and waiting == 0
        and admissions == carrier_resumes
        and rotations <= carrier_pauses
        and rotations <= carrier_resumes
        and failures == 0
        and total_wait >= maximum_wait
        and (
            carrier_resumes != 0
            or rotations == 0
            and carrier_pauses == 0
            and total_wait == 0
            and maximum_wait == 0
        ),
        f"{role} Ratox file-carrier accounting is invalid",
    )


def verify_ratox_bulk_state_accounting(
    records: dict[str, str], before: int, after: int
) -> None:
    present_before = int(records.get("present-before", "-1"))
    active_before = int(records.get("active-before", "-1"))
    paused_before = int(records.get("paused-before", "-1"))
    present_after = int(records.get("present-after", "-1"))
    active_after = int(records.get("active-after", "-1"))
    paused_after = int(records.get("paused-after", "-1"))
    require(
        records.get("state-accounting") == "active-or-paused"
        and present_before == before
        and active_before >= 0
        and paused_before >= 0
        and active_before + paused_before == present_before
        and present_after == after
        and active_after >= 0
        and paused_after >= 0
        and active_after + paused_after == present_after,
        "Ratox bulk state accounting is invalid",
    )


def verify_resource_interval(
    path: Path,
    role: str,
    ratox_active_boundary: tuple[int, int] = (0, 0),
) -> None:
    records: dict[str, str] = {}
    for line in path.read_text(encoding="ascii").splitlines():
        fields = line.split("\t")
        require(
            len(fields) == 2 and fields[0] not in records and fields[1] != "",
            f"{role} Ratox resource interval is noncanonical",
        )
        records[fields[0]] = fields[1]
    expected = {
        "schema",
        "role",
        "pid",
        "process-start-ticks",
        "clock-ticks-per-second",
        "page-size-bytes",
        *(f"start-{key}" for key in RESOURCE_SAMPLE_KEYS),
        *(f"end-{key}" for key in RESOURCE_SAMPLE_KEYS),
        *(f"delta-{key}" for key in RESOURCE_DELTA_KEYS),
    }
    require(set(records) == expected, f"{role} Ratox resource fields changed")
    require(
        records["schema"] == "iotox-process-resource-interval-v1"
        and records["role"] == role,
        f"{role} Ratox resource identity is invalid",
    )
    numeric = {
        key: int(value)
        for key, value in records.items()
        if key not in {"schema", "role"}
    }
    require(
        numeric["pid"] > 0
        and numeric["process-start-ticks"] > 0
        and numeric["clock-ticks-per-second"] > 0
        and numeric["page-size-bytes"] > 0
        and numeric["start-process-start-ticks"]
        == numeric["process-start-ticks"]
        == numeric["end-process-start-ticks"],
        f"{role} Ratox resource process incarnation is invalid",
    )
    require(
        numeric["start-ratox-latency-mode-active"]
        == ratox_active_boundary[0]
        and numeric["end-ratox-latency-mode-active"]
        == ratox_active_boundary[1]
        and numeric["start-ratox-active-service-interval-ms"] == 5
        and numeric["end-ratox-active-service-interval-ms"] == 5
        and numeric[
            "start-ratox-active-transport-iteration-interval-ms"
        ]
        == 5
        and numeric[
            "end-ratox-active-transport-iteration-interval-ms"
        ]
        == 5,
        f"{role} Ratox active/idle cadence boundary is invalid",
    )
    require(
        numeric["delta-monotonic-ns"] > 0
        and numeric["delta-transport-iterations"] > 0
        and numeric["start-open-descriptors"] > 0
        and numeric["end-open-descriptors"] > 0
        and numeric["start-resident-pages"] > 0
        and numeric["end-resident-pages"] > 0,
        f"{role} Ratox resource interval did not observe a live workload",
    )
    for key in RESOURCE_DELTA_KEYS:
        require(
            numeric[f"delta-{key}"]
            == numeric[f"end-{key}"] - numeric[f"start-{key}"],
            f"{role} Ratox resource delta is inconsistent: {key}",
        )


def is_legacy_repair_evidence(manifest: dict) -> bool:
    receipt_entries = manifest.get("receipts", {})
    if not isinstance(receipt_entries, dict):
        return False
    binary_digests = {
        entry.get("binary_sha256")
        for entry in receipt_entries.values()
        if isinstance(entry, dict)
    }
    return binary_digests == LEGACY_REPAIR_BINARY_SHA256


def load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            value.update(chunk)
    return value.hexdigest()


def verify_content_ratox_latency(
    proof_root: Path, receipt: dict[str, object], *, enforce_cap_2_sla: bool
) -> None:
    caps = (1, 2, 4, 8) if enforce_cap_2_sla else (1, 4, 8)
    phase_order = ",".join(str(cap) for cap in caps)
    samples_per_phase = 240
    total_samples = samples_per_phase * len(caps)
    metadata_schema = (
        "iotox-content-ratox-overlap-metadata-v2"
        if enforce_cap_2_sla
        else "iotox-content-ratox-overlap-metadata-v1"
    )
    summary_schema = (
        "iotox-content-ratox-latency-sla-v1"
        if enforce_cap_2_sla
        else "iotox-content-ratox-latency-science-v1"
    )
    base = "client/live/workspace-export/guest-receipts/iotox/"
    metadata = confined(
        proof_root,
        base + "content-ratox-overlap-metadata.tsv",
        base + "content-ratox-overlap-metadata.tsv",
    )
    summary = confined(
        proof_root,
        base + "content-ratox-latency.tsv",
        base + "content-ratox-latency.tsv",
    )
    metadata_lines = metadata.read_text(encoding="ascii").splitlines()
    require(
        metadata_lines[:6]
        == [
            f"schema\t{metadata_schema}",
            f"phase-order\t{phase_order}",
            f"samples-per-phase\t{samples_per_phase}",
            f"samples-total\t{total_samples}",
            "sample-interval-ms\t100",
            "columns\tcap\tcontent-start-us\tcontent-end-us\tcontent-duration-ms\tcontent-bps\tmax-active-lanes\tsample-first\tsample-last\tcapture-sha256\ttox-online-epoch\tphase-ready-delay-ms",
        ]
        and len(metadata_lines) == 6 + len(caps),
        "content/Ratox overlap metadata is noncanonical",
    )
    summary_lines = summary.read_text(encoding="ascii").splitlines()
    require(
        summary_lines[:5]
        == [
            f"schema\t{summary_schema}",
            f"phase-order\t{phase_order}",
            f"samples-per-phase\t{samples_per_phase}",
            f"samples-total\t{total_samples}",
            "sample-interval-ms\t100",
        ]
        and len(summary_lines) == 7 + len(caps)
        and summary_lines[5].startswith("tox-online-epoch\t")
        and summary_lines[6]
        == "columns\tcap\tcontent-duration-ms\tcontent-bps\tmax-active-lanes\tphase-ready-delay-ms\toverlap-samples\trtt-p50-us\trtt-p95-us\trtt-p99-us\trtt-max-us\tqueue-p95-us\tqueue-max-us\tsession-sha256\tcapture-sha256",
        "content/Ratox latency summary is noncanonical",
    )
    try:
        summary_epoch = int(summary_lines[5].split("\t", 1)[1])
    except (IndexError, ValueError) as error:
        raise ValueError("content/Ratox summary epoch is invalid") from error
    require(summary_epoch > 0, "content/Ratox summary epoch is zero")
    readiness_relative = (
        "client/live/workspace-export/iotox-rendezvous/"
        "client.content-ratox-readiness"
    )
    readiness_path = confined(
        proof_root, readiness_relative, readiness_relative
    )
    readiness: dict[str, str] = {}
    for line in readiness_path.read_text(encoding="ascii").splitlines():
        fields = line.split("\t")
        require(
            len(fields) == 2 and fields[0] not in readiness,
            "content/Ratox readiness snapshot is noncanonical",
        )
        readiness[fields[0]] = fields[1]
    require(
        readiness
        == {
            "schema": "iotox-content-ratox-readiness-v1",
            "cap": "8",
            "session-confirmed": "1",
            "capability-observed": "1",
            "claimant-proof-sent": "1",
            "claimant-principal-present": "1",
            "connection": readiness.get("connection", ""),
            "online-epoch": str(summary_epoch),
            "stable-samples": "3",
        }
        and readiness["connection"] in {"udp", "tcp"},
        "content/Ratox final readiness snapshot is invalid",
    )

    capture_relative = base + "content-ratox-timeline.tsv"
    capture = confined(proof_root, capture_relative, capture_relative)
    capture_digest = digest(capture)
    lines = capture.read_text(encoding="ascii").splitlines()
    require(
        f"samples\t{total_samples}" in lines
        and "sample-interval-ms\t100" in lines
        and "schema\tiotox-ratox-terminal-probe-v1" in lines,
        "persistent content/Ratox capture metadata is invalid",
    )
    commitments = [
        line.split("\t", 1)[1]
        for line in lines
        if line.startswith("peer-public-key-sha256\t")
    ]
    require(
        len(commitments) == 1 and SHA256.fullmatch(commitments[0]) is not None,
        "persistent content/Ratox peer commitment is invalid",
    )
    rows = [line.split("\t") for line in lines if line.startswith("sample\t")]
    require(
        len(rows) == total_samples,
        "persistent Ratox sample count is invalid",
    )
    previous_render = 0
    sessions: set[str] = set()
    parsed_rows: list[tuple[int, int, int]] = []
    for ordinal, row in enumerate(rows, 1):
        require(len(row) == 11, "persistent Ratox sample shape is invalid")
        try:
            observed, started, returned, rendered = map(int, row[1:5])
            input_sequence, next_input = map(int, row[6:8])
            output_sequence, next_output = map(int, row[8:10])
            queue_wait = int(row[10])
        except ValueError as error:
            raise ValueError("persistent Ratox sample is nondecimal") from error
        require(
            observed == ordinal
            and previous_render <= started < returned <= rendered
            and re.fullmatch(r"[0-9a-f]{32}", row[5]) is not None
            and next_input == input_sequence + 1
            and next_output == output_sequence + 1
            and queue_wait >= 0,
            "persistent Ratox sample is inconsistent",
        )
        previous_render = rendered
        sessions.add(row[5])
        parsed_rows.append((started, returned, queue_wait))
    require(len(sessions) == 1, "Ratox session changed across content phases")
    terminal_session = next(iter(sessions))

    epochs: set[int] = set()
    previous_content_end = 0
    for index, (cap, metadata_line, summary_line) in enumerate(zip(
        caps, metadata_lines[6:], summary_lines[7:], strict=True
    )):
        expected_first = index * samples_per_phase + 1
        expected_last = expected_first + samples_per_phase - 1
        fields = metadata_line.split("\t")
        require(
            len(fields) == 12
            and fields[:2] == ["phase", str(cap)]
            and SHA256.fullmatch(fields[9]) is not None,
            f"cap-{cap} content/Ratox metadata row is invalid",
        )
        try:
            (
                start_us,
                end_us,
                duration_ms,
                content_bps,
                active,
                first_sample,
                last_sample,
                epoch,
                phase_ready_delay_ms,
            ) = (
                int(fields[field_index])
                for field_index in (2, 3, 4, 5, 6, 7, 8, 10, 11)
            )
        except ValueError as error:
            raise ValueError(
                f"cap-{cap} content/Ratox metadata is nondecimal"
            ) from error
        require(
            previous_content_end < start_us < end_us
            and duration_ms > 0
            and abs(duration_ms - ((end_us - start_us) // 1000)) <= 2
            and content_bps == (8 * 1024 * 1024 * 1000) // duration_ms
            and 1 <= active <= cap
            and first_sample == expected_first
            and last_sample == expected_last
            and fields[9] == capture_digest
            and duration_ms
            == receipt.get(f"content_lane_science_cap_{cap}_duration_ms")
            and content_bps
            == receipt.get(f"content_lane_science_cap_{cap}_bps")
            and active == receipt.get(f"content_lane_science_cap_{cap}_active")
            and epoch > 0
            and 0 <= phase_ready_delay_ms <= 180_000,
            f"cap-{cap} content/Ratox metadata disagrees with lane evidence",
        )
        previous_content_end = end_us
        epochs.add(epoch)

        segment = parsed_rows[first_sample - 1 : last_sample]
        require(
            len(segment) == samples_per_phase and segment[0][1] < start_us,
            f"cap-{cap} persistent Ratox segment lacks a pre-transfer sample",
        )
        overlap = [
            row for row in segment if start_us <= row[0] <= end_us
        ]
        require(
            len(overlap) >= (
                CAP_2_SLA_MIN_OVERLAP
                if enforce_cap_2_sla and cap == 2
                else 20
            ),
            f"cap-{cap} Ratox timeline does not genuinely overlap content",
        )
        round_trips = [returned - started for started, returned, _ in overlap]
        queue_waits = [queue_wait for _, _, queue_wait in overlap]

        expected = [
            "phase",
            str(cap),
            str(duration_ms),
            str(content_bps),
            str(active),
            str(phase_ready_delay_ms),
            str(len(round_trips)),
            str(nearest_rank(round_trips, 50)),
            str(nearest_rank(round_trips, 95)),
            str(nearest_rank(round_trips, 99)),
            str(max(round_trips)),
            str(nearest_rank(queue_waits, 95)),
            str(max(queue_waits)),
            hashlib.sha256(bytes.fromhex(terminal_session)).hexdigest(),
            capture_digest,
        ]
        require(
            summary_line.split("\t") == expected,
            f"cap-{cap} content/Ratox summary was not independently reproduced",
        )
        if enforce_cap_2_sla and cap == 2:
            require(
                cap_2_interactive_sla_passes(round_trips, queue_waits),
                "cap-2 persistent Ratox missed the frozen interactive SLA",
            )

    require(
        epochs == {summary_epoch},
        "content/Ratox phases changed the authenticated Tox epoch",
    )


def verify_content_ratox_post_bulk_admission(
    proof_root: Path, receipt: dict[str, object], connection: str
) -> None:
    base = "client/live/workspace-export/guest-receipts/iotox/"
    readiness = confined(
        proof_root,
        base + "content-ratox-post-bulk-readiness.tsv",
        base + "content-ratox-post-bulk-readiness.tsv",
    )
    capture = confined(
        proof_root,
        base + "content-ratox-post-bulk-capture.tsv",
        base + "content-ratox-post-bulk-capture.tsv",
    )
    admission = confined(
        proof_root,
        base + "content-ratox-post-bulk-admission.tsv",
        base + "content-ratox-post-bulk-admission.tsv",
    )

    def records(path: Path) -> dict[str, str]:
        result: dict[str, str] = {}
        for line in path.read_text(encoding="ascii").splitlines():
            fields = line.split("\t")
            require(
                len(fields) == 2 and fields[0] not in result and fields[1] != "",
                f"post-bulk Ratox evidence is noncanonical: {path.name}",
            )
            result[fields[0]] = fields[1]
        return result

    ready = records(readiness)
    admitted = records(admission)
    expected_admission_fields = [
        "schema",
        "origin-us",
        "probe-start-us",
        "socket-connected-us",
        "open-sent-us",
        "opened-us",
        "origin-to-open-sent-us",
        "origin-to-opened-us",
        "open-round-trip-us",
        "connection",
        "online-epoch",
        "capability-observed",
        "claimant-proof-sent",
        "claimant-principal-present",
        "session-sha256",
        "incarnation",
        "generation",
        "initial-input-sequence",
        "initial-output-sequence",
        "samples",
        "capture-sha256",
    ]
    require(
        list(admitted) == expected_admission_fields
        and admitted["schema"] == "iotox-ratox-admission-evidence-v1"
        and admitted["connection"] == connection
        and admitted["capability-observed"] == "1"
        and admitted["claimant-proof-sent"] == "1"
        and admitted["claimant-principal-present"] == "1"
        and admitted["generation"] == "1"
        and admitted["initial-input-sequence"] == "1"
        and admitted["initial-output-sequence"] == "1"
        and admitted["samples"] == "40"
        and SHA256.fullmatch(admitted["session-sha256"]) is not None
        and SHA256.fullmatch(admitted["capture-sha256"]) is not None,
        "fresh post-bulk Ratox admission identity is invalid",
    )
    try:
        origin = int(admitted["origin-us"])
        probe_started = int(admitted["probe-start-us"])
        connected = int(admitted["socket-connected-us"])
        open_sent = int(admitted["open-sent-us"])
        opened = int(admitted["opened-us"])
        origin_to_sent = int(admitted["origin-to-open-sent-us"])
        origin_to_opened = int(admitted["origin-to-opened-us"])
        open_round_trip = int(admitted["open-round-trip-us"])
        epoch = int(admitted["online-epoch"])
        incarnation = int(admitted["incarnation"])
    except ValueError as error:
        raise ValueError("fresh post-bulk Ratox admission is nondecimal") from error
    require(
        0 < origin <= probe_started <= connected <= open_sent < opened
        and origin_to_sent == open_sent - origin
        and origin_to_opened == opened - origin
        and open_round_trip == opened - open_sent
        and origin_to_sent <= 1_000_000
        and origin_to_opened <= 6_000_000
        and open_round_trip <= 5_000_000
        and epoch > 0
        and incarnation > 0,
        "fresh post-bulk Ratox OPEN missed its timing or identity bound",
    )
    require(
        ready
        == {
            "schema": "iotox-content-ratox-post-bulk-readiness-v1",
            "session-confirmed": "1",
            "capability-observed": "1",
            "claimant-proof-sent": "1",
            "claimant-principal-present": "1",
            "connection": connection,
            "online-epoch": str(epoch),
            "stable-samples": "3",
        },
        "pre-backlog Ratox readiness changed before fresh admission",
    )

    capture_lines = capture.read_text(encoding="ascii").splitlines()
    require(
        len(capture_lines) == 44
        and SHA256.fullmatch(capture_lines[0].split("\t", 1)[1]) is not None
        and capture_lines[1:4]
        == [
            "samples\t40",
            "sample-interval-ms\t0",
            "schema\tiotox-ratox-terminal-probe-v1",
        ],
        "fresh post-bulk Ratox capture metadata is invalid",
    )
    rows = [line.split("\t") for line in capture_lines[4:]]
    previous_render = opened
    sessions: set[str] = set()
    for ordinal, row in enumerate(rows, 1):
        require(len(row) == 11, "fresh post-bulk Ratox sample shape is invalid")
        try:
            observed, started, returned, rendered = map(int, row[1:5])
            input_sequence, next_input = map(int, row[6:8])
            output_sequence, next_output = map(int, row[8:10])
            queue_wait = int(row[10])
        except ValueError as error:
            raise ValueError("fresh post-bulk Ratox sample is nondecimal") from error
        require(
            observed == ordinal
            and previous_render <= started < returned <= rendered
            and re.fullmatch(r"[0-9a-f]{32}", row[5]) is not None
            and input_sequence == ordinal
            and next_input == ordinal + 1
            and output_sequence == ordinal
            and next_output == ordinal + 1
            and queue_wait >= 0,
            "fresh post-bulk Ratox sample is inconsistent",
        )
        previous_render = rendered
        sessions.add(row[5])
    require(
        len(sessions) == 1
        and hashlib.sha256(bytes.fromhex(next(iter(sessions)))).hexdigest()
        == admitted["session-sha256"]
        and digest(capture) == admitted["capture-sha256"],
        "fresh post-bulk Ratox capture changed session or digest",
    )
    require(
        receipt.get("content_ratox_post_bulk_observed") is True
        and receipt.get("content_ratox_post_bulk_cap") == 8
        and receipt.get("content_ratox_post_bulk_samples") == 40
        and receipt.get("content_ratox_post_bulk_origin_us") == origin
        and receipt.get("content_ratox_post_bulk_origin_to_open_sent_us")
        == origin_to_sent
        and receipt.get("content_ratox_post_bulk_origin_to_opened_us")
        == origin_to_opened
        and receipt.get("content_ratox_post_bulk_open_round_trip_us")
        == open_round_trip
        and receipt.get("content_ratox_post_bulk_online_epoch") == epoch
        and receipt.get("content_ratox_post_bulk_readiness_sha256")
        == digest(readiness)
        and receipt.get("content_ratox_post_bulk_capture_sha256")
        == digest(capture)
        and receipt.get("content_ratox_post_bulk_admission_sha256")
        == digest(admission),
        "fresh post-bulk Ratox receipt commitments disagree",
    )


def verify_packet_loss_report(path: Path, delivered: int, missed: int) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    require(len(lines) == PACKET_LOSS_PROBE_COUNT, "partial-loss burst row count mismatch")
    observed_ordinals = set()
    observed_nonces = set()
    observed_delivered = 0
    observed_missed = 0
    for line in lines:
        match = PACKET_LOSS_LINE.fullmatch(line)
        require(match is not None, "malformed partial-loss burst row")
        ordinal = int(match.group(1))
        nonce = int(match.group(2))
        rtt = match.group(3)
        arrival_rank = match.group(4)
        copies = int(match.group(5))
        send_error = match.group(6)
        require(1 <= ordinal <= PACKET_LOSS_PROBE_COUNT, "partial-loss ordinal escaped its burst")
        require(ordinal not in observed_ordinals, "duplicate partial-loss ordinal")
        require(nonce not in observed_nonces, "duplicate partial-loss nonce")
        require(send_error == "ok", "partial-loss probe was rejected locally")
        require((rtt == "miss") == (arrival_rank == "miss"), "partial-loss miss fields disagree")
        if rtt == "miss":
            require(copies == 0, "missed partial-loss probe claims a reply")
            observed_missed += 1
        else:
            require(copies >= 1, "delivered partial-loss probe has no reply")
            observed_delivered += 1
        observed_ordinals.add(ordinal)
        observed_nonces.add(nonce)
    require(
        observed_ordinals == set(range(1, PACKET_LOSS_PROBE_COUNT + 1)),
        "partial-loss ordinal inventory mismatch",
    )
    require(
        observed_delivered == delivered and observed_missed == missed,
        "partial-loss receipt and burst report disagree",
    )


def product_identity() -> tuple[str, str]:
    revision = (ROOT / "REVISION").read_text(encoding="utf-8").strip()
    header = (ROOT / "include/iotox/version.hpp").read_text(encoding="utf-8")
    match = re.search(r'kVersion = "([^"]+)"', header)
    require(match is not None, "IoTox version header has no kVersion")
    return match.group(1), revision


def confined(root: Path, relative: object, expected: str) -> Path:
    require(relative == expected, f"unexpected evidence path: {relative}")
    path = (root / expected).resolve()
    require(path.is_relative_to(root), "evidence path escapes the proof root")
    require(path.is_file(), f"evidence file is absent: {expected}")
    return path


SAME_SOURCE_MULTI_ROUTE_CONTENT_PATH = (
    "client/live/workspace-export/iotox-rendezvous/"
    "client.content-same-source-multi-route"
)


def verify_actual_tor_evidence(
    proof_root: Path, manifest: dict, expected: bool
) -> None:
    actual_tor_sync_loss = (
        manifest.get("scenario")
        == "sync-tree-route-private-actual-tor-loss"
    )
    actual_tor_ratox_loss = (
        manifest.get("scenario") == "ratox-route-actual-tor-loss"
    )
    actual_tor_ratox_adversary = (
        manifest.get("scenario") == "ratox-route-actual-tor-adversary"
    )
    actual_tor_loss = actual_tor_sync_loss or actual_tor_ratox_loss
    if not expected:
        require(
            manifest.get("actual_tor", False) is False
            and manifest.get("actual_tor_instance_count", 0) == 0
            and manifest.get("actual_tor_node") is None
            and manifest.get("actual_tor_binary_path") is None
            and manifest.get("actual_tor_sha256") is None
            and manifest.get("actual_tor_version") is None
            and manifest.get("actual_tor_role_evidence", []) == [],
            "non-Tor scenario claims actual-Tor evidence",
        )
        require(
            manifest.get("actual_tor_process_loss", {}) == {}
            and manifest.get("actual_tor_process_loss_path") is None
            and manifest.get("actual_tor_process_loss_sha256") is None,
            "non-Tor scenario claims actual-Tor process loss",
        )
        return

    require(manifest.get("actual_tor") is True, "actual-Tor marker is absent")
    node = manifest.get("actual_tor_node")
    require(isinstance(node, dict), "actual-Tor node record is absent")
    require(
        set(node) == {"address", "port", "public_key"},
        "actual-Tor node record fields drifted",
    )
    address = ipaddress.ip_address(str(node["address"]))
    require(
        address.version == 4 and address.is_global,
        "actual-Tor node is not public IPv4",
    )
    port = node["port"]
    public_key = node["public_key"]
    require(
        isinstance(port, int)
        and 1 <= port <= 65535
        and re.fullmatch(r"[0-9A-F]{64}", str(public_key)) is not None,
        "actual-Tor node port/key is invalid",
    )
    target = f"{address.compressed}:{port}"
    binary_path = manifest.get("actual_tor_binary_path")
    require(
        isinstance(binary_path, str)
        and binary_path.startswith("/nix/store/")
        and binary_path.endswith("/bin/tor")
        and SHA256.fullmatch(str(manifest.get("actual_tor_sha256", "")))
        is not None
        and str(manifest.get("actual_tor_version", "")).startswith("Tor version "),
        "actual-Tor binary identity is invalid",
    )
    roles = manifest.get("actual_tor_role_evidence")
    expected_instances = (
        [
            ("client", "pre-loss"),
            ("client", "recovered"),
            ("device", "continuous"),
        ]
        if actual_tor_loss
        else [("client", None), ("device", None)]
    )
    require(
        isinstance(roles, list)
        and len(roles) == len(expected_instances)
        and manifest.get("actual_tor_instance_count")
        == len(expected_instances),
        "actual-Tor role evidence count is invalid",
    )
    process_ids: set[int] = set()
    control_inodes: set[int] = set()
    for evidence, (role, phase) in zip(roles, expected_instances):
        require(isinstance(evidence, dict), f"{role} Tor evidence is not an object")
        require(
            evidence.get("phase") == phase
            if phase is not None
            else "phase" not in evidence,
            f"{role} Tor evidence phase is invalid",
        )
        expected_source = (
            "127.0.0.1"
            if actual_tor_ratox_adversary
            else "10.0.0.11"
            if role == "client"
            else "10.0.0.12"
        )
        expected_proxy = (
            f"127.0.0.1:{ACTUAL_TOR_UPSTREAM_SOCKS_PORTS[role]}"
            if actual_tor_ratox_adversary
            else f"10.0.0.1:{ACTUAL_TOR_SOCKS_PORTS[role]}"
        )
        expected_configuration = [
            "AvoidDiskWrites 1",
            "ClientOnly 1",
            "ClientUseIPv6 0",
            "CookieAuthentication 1",
            "CookieAuthFile <TOR_ROOT>/control.authcookie",
            "ControlSocket <TOR_ROOT>/control.sock",
            "DataDirectory <TOR_ROOT>/tor-data",
            "SafeSocks 0",
            f"SocksPolicy accept {expected_source}",
            "SocksPolicy reject *",
            f"SocksPort {expected_proxy}",
        ]
        configuration_digest = hashlib.sha256(
            ("\n".join(expected_configuration) + "\n").encode("ascii")
        ).hexdigest()
        require(
            evidence.get("role") == role
            and evidence.get("control_authenticated") is True
            and evidence.get("source_address") == expected_source
            and evidence.get("socks_endpoint") == expected_proxy
            and evidence.get("stream_target") == target
            and evidence.get("configuration") == expected_configuration
            and evidence.get("configuration_sha256") == configuration_digest
            and evidence.get("bootstrap_progress") == 100,
            f"{role} Tor topology/configuration evidence is invalid",
        )

        events_path = confined(
            proof_root,
            evidence.get("events_path"),
            f"tor-{role}{'-' + phase if phase else ''}-control-events.txt",
        )
        bootstrap_path = confined(
            proof_root,
            evidence.get("bootstrap_status_path"),
            f"tor-{role}{'-' + phase if phase else ''}-bootstrap-status.txt",
        )
        circuits_path = confined(
            proof_root,
            evidence.get("circuit_status_path"),
            f"tor-{role}{'-' + phase if phase else ''}-circuit-status.txt",
        )
        require(
            evidence.get("events_sha256") == digest(events_path)
            and evidence.get("bootstrap_status_sha256") == digest(bootstrap_path)
            and evidence.get("circuit_status_sha256") == digest(circuits_path),
            f"{role} Tor control evidence digest mismatch",
        )
        bootstrap = bootstrap_path.read_text(encoding="ascii")
        require(
            "PROGRESS=100" in bootstrap and "TAG=done" in bootstrap,
            f"{role} Tor raw bootstrap status is incomplete",
        )
        source_streams: dict[str, str] = {}
        succeeded: list[tuple[str, str]] = []
        event_circuits: dict[str, list[str]] = {}
        for line in events_path.read_text(encoding="ascii").splitlines():
            fields = line.split()
            require(
                len(fields) >= 2 and fields[0] == "650",
                f"{role} Tor event record is not asynchronous control evidence",
            )
            if len(fields) >= 5 and fields[1] == "CIRC":
                if fields[3] in {"BUILT", "CLOSED"}:
                    event_circuits[fields[2]] = fields[2:]
                continue
            if len(fields) < 6 or fields[1] != "STREAM":
                continue
            stream_id, state, circuit_id, stream_target = fields[2:6]
            if state == "NEW":
                sources = [
                    field.split("=", 1)[1]
                    for field in fields[6:]
                    if field.startswith("SOURCE_ADDR=")
                ]
                if len(sources) != 1:
                    continue
                source_host, separator, source_port = sources[0].rpartition(":")
                if source_host == expected_source:
                    require(
                        separator == ":"
                        and source_port.isdecimal()
                        and 1 <= int(source_port) <= 65535
                        and stream_target == target,
                        f"{role} Tor guest stream escaped its exact target",
                    )
                    source_streams[stream_id] = stream_target
            elif state == "SUCCEEDED" and stream_id in source_streams:
                require(
                    stream_target == target,
                    f"{role} Tor successful stream changed target",
                )
                succeeded.append((stream_id, circuit_id))
        require(
            len(source_streams) == evidence.get("guest_source_stream_count")
            and len(succeeded) == evidence.get("successful_guest_stream_count")
            and len(source_streams) >= 1
            and len(succeeded) >= 1,
            f"{role} Tor stream counters do not match raw control events",
        )
        current_circuits: dict[str, list[str]] = {}
        for line in circuits_path.read_text(encoding="ascii").splitlines():
            fields = line.split()
            if len(fields) >= 3 and fields[1] == "BUILT":
                current_circuits[fields[0]] = fields
        selected = None
        for stream_id, circuit_id in succeeded:
            circuit = current_circuits.get(circuit_id) or event_circuits.get(circuit_id)
            if (
                circuit is not None
                and hashlib.sha256(stream_id.encode("ascii")).hexdigest()
                == evidence.get("stream_id_sha256")
            ):
                selected = circuit
                break
        require(
            selected is not None
            and len(selected) >= 3
            and selected[1] in {"BUILT", "CLOSED"},
            f"{role} Tor successful stream lacks raw built-circuit evidence",
        )
        path = selected[2]
        purposes = [
            field.split("=", 1)[1]
            for field in selected[3:]
            if field.startswith("PURPOSE=")
        ]
        hop_count = len(path.split(","))
        require(
            len(purposes) == 1
            and purposes[0] in TOR_APPLICATION_CIRCUIT_PURPOSES
            and purposes[0] == evidence.get("circuit_purpose")
            and hop_count >= 3
            and hop_count == evidence.get("circuit_hop_count")
            and hashlib.sha256(path.encode("ascii")).hexdigest()
            == evidence.get("circuit_path_sha256"),
            f"{role} Tor circuit evidence is invalid",
        )
        process_id = evidence.get("process_pid")
        control_inode = evidence.get("control_socket_inode")
        require(
            isinstance(process_id, int)
            and process_id > 1
            and isinstance(control_inode, int)
            and control_inode > 0
            and isinstance(evidence.get("public_tcp_remote_count"), int)
            and evidence["public_tcp_remote_count"] > 0
            and SHA256.fullmatch(
                str(evidence.get("public_tcp_remote_set_sha256", ""))
            )
            is not None,
            f"{role} Tor process/socket attribution is invalid",
        )
        process_ids.add(process_id)
        control_inodes.add(control_inode)
    require(
        len(process_ids) == len(expected_instances)
        and len(control_inodes) >= 2,
        "actual-Tor instances are not process/control distinct",
    )
    process_loss = manifest.get("actual_tor_process_loss", {})
    if actual_tor_sync_loss:
        require(
            isinstance(process_loss, dict)
            and set(process_loss)
            == {
                "carrier_losses",
                "job_id",
                "loss_observation_ns",
                "position_bytes",
                "pre_loss_control_socket_inode",
                "pre_loss_process_pid",
                "reassignments",
                "recovered_control_socket_inode",
                "recovered_process_pid",
                "replacement_carrier",
                "restart_bootstrap_ns",
                "returncode",
                "role",
                "route_worker_restarts",
                "schema",
                "signal",
                "stopped_carrier",
                "stopped_carrier_sha256",
            }
            and process_loss.get("schema")
            == "iotox-actual-tor-process-loss-v1"
            and process_loss.get("role") == "client"
            and process_loss.get("signal") == signal.SIGKILL
            and process_loss.get("returncode") == -signal.SIGKILL
            and process_loss.get("pre_loss_process_pid")
            == roles[0].get("process_pid")
            and process_loss.get("pre_loss_control_socket_inode")
            == roles[0].get("control_socket_inode")
            and process_loss.get("recovered_process_pid")
            == roles[1].get("process_pid")
            and process_loss.get("recovered_control_socket_inode")
            == roles[1].get("control_socket_inode")
            and isinstance(process_loss.get("job_id"), int)
            and process_loss["job_id"] > 0
            and isinstance(process_loss.get("position_bytes"), int)
            and 65_536
            <= process_loss["position_bytes"]
            < SYNC_SCENARIOS["sync-tree-route-private-actual-tor-loss"]
            and re.fullmatch(
                r"[0-9A-F]{64}",
                str(process_loss.get("stopped_carrier", "")),
            )
            is not None
            and re.fullmatch(
                r"[0-9A-F]{64}",
                str(process_loss.get("replacement_carrier", "")),
            )
            is not None
            and process_loss["replacement_carrier"]
            != process_loss["stopped_carrier"]
            and hashlib.sha256(
                process_loss["stopped_carrier"].encode("ascii")
            ).hexdigest()
            == process_loss.get("stopped_carrier_sha256")
            and process_loss.get("carrier_losses") == 1
            and process_loss.get("reassignments") == 1
            and process_loss.get("route_worker_restarts") == 0
            and isinstance(process_loss.get("loss_observation_ns"), int)
            and process_loss["loss_observation_ns"] > 0
            and isinstance(process_loss.get("restart_bootstrap_ns"), int)
            and process_loss["restart_bootstrap_ns"] > 0,
            "actual-Tor process-loss summary is invalid",
        )
        loss_path = confined(
            proof_root,
            manifest.get("actual_tor_process_loss_path"),
            "actual-tor-process-loss.json",
        )
        require(
            manifest.get("actual_tor_process_loss_sha256")
            == digest(loss_path)
            and load(loss_path) == process_loss,
            "actual-Tor process-loss file disagrees with the manifest",
        )
    elif actual_tor_ratox_loss:
        require(
            isinstance(process_loss, dict)
            and set(process_loss)
            == {
                "controller_offline_after_loss_ns",
                "heartbeat_missed_after_loss_ns",
                "iotox_daemon_restarts",
                "pre_loss_control_socket_inode",
                "pre_loss_process_pid",
                "recovered_control_socket_inode",
                "recovered_process_pid",
                "restart_bootstrap_ns",
                "returncode",
                "role",
                "schema",
                "signal",
            }
            and process_loss.get("schema")
            == "iotox-actual-tor-ratox-process-loss-v1"
            and process_loss.get("role") == "client"
            and process_loss.get("signal") == signal.SIGKILL
            and process_loss.get("returncode") == -signal.SIGKILL
            and process_loss.get("pre_loss_process_pid")
            == roles[0].get("process_pid")
            and process_loss.get("pre_loss_control_socket_inode")
            == roles[0].get("control_socket_inode")
            and process_loss.get("recovered_process_pid")
            == roles[1].get("process_pid")
            and process_loss.get("recovered_control_socket_inode")
            == roles[1].get("control_socket_inode")
            and process_loss.get("iotox_daemon_restarts") == 0
            and isinstance(
                process_loss.get("heartbeat_missed_after_loss_ns"), int
            )
            and 1_800_000_000
            <= process_loss["heartbeat_missed_after_loss_ns"]
            < 30_000_000_000
            and isinstance(
                process_loss.get("controller_offline_after_loss_ns"), int
            )
            and process_loss["controller_offline_after_loss_ns"]
            > process_loss["heartbeat_missed_after_loss_ns"]
            and process_loss["controller_offline_after_loss_ns"]
            < 240_000_000_000
            and isinstance(process_loss.get("restart_bootstrap_ns"), int)
            and 0 < process_loss["restart_bootstrap_ns"] < 180_000_000_000,
            "actual-Tor Ratox process-loss summary is invalid",
        )
        loss_path = confined(
            proof_root,
            manifest.get("actual_tor_process_loss_path"),
            "actual-tor-process-loss.json",
        )
        require(
            manifest.get("actual_tor_process_loss_sha256")
            == digest(loss_path)
            and load(loss_path) == process_loss,
            "actual-Tor Ratox process-loss file disagrees with the manifest",
        )
    else:
        require(
            process_loss == {}
            and manifest.get("actual_tor_process_loss_path") is None
            and manifest.get("actual_tor_process_loss_sha256") is None,
            "continuous actual-Tor proof claims a process loss",
        )


def verify_actual_tor_adversarial_boundary(
    proof_root: Path, manifest: dict, expected: bool
) -> None:
    boundary = manifest.get("actual_tor_adversarial_boundary", {})
    if not expected:
        require(
            boundary == {}
            and manifest.get("actual_tor_adversarial_boundary_path") is None
            and manifest.get("actual_tor_adversarial_boundary_sha256") is None,
            "non-adversarial scenario claims an actual-Tor boundary fault",
        )
        return
    exact_keys = {
        "controller_offline_after_hold_ns",
        "fault_kind",
        "heartbeat_missed_after_hold_ns",
        "hold_active_ns",
        "hold_file_mode",
        "hold_released_ns",
        "hold_started_ns",
        "interposer_listener_inode",
        "interposer_process_pid",
        "interposer_process_restarts",
        "interposer_sha256",
        "iotox_daemon_restarts",
        "listener_reachable_during_hold",
        "role",
        "roles",
        "schema",
        "socks_connect_succeeded_during_hold",
        "tor_control_socket_inode",
        "tor_process_pid",
        "tor_process_restarts",
    }
    require(
        isinstance(boundary, dict)
        and set(boundary) == exact_keys
        and boundary.get("schema")
        == "iotox-actual-tor-adversarial-boundary-v1"
        and boundary.get("role") == "client"
        and boundary.get("fault_kind") == "established-relay-byte-hold"
        and boundary.get("hold_file_mode") == "host-owned-presence"
        and boundary.get("listener_reachable_during_hold") is True
        and boundary.get("socks_connect_succeeded_during_hold") is True
        and boundary.get("tor_process_restarts") == 0
        and boundary.get("interposer_process_restarts") == 0
        and boundary.get("iotox_daemon_restarts") == 0
        and SHA256.fullmatch(str(boundary.get("interposer_sha256", "")))
        is not None,
        "actual-Tor adversarial boundary envelope is invalid",
    )
    started = boundary.get("hold_started_ns")
    released = boundary.get("hold_released_ns")
    active = boundary.get("hold_active_ns")
    heartbeat = boundary.get("heartbeat_missed_after_hold_ns")
    offline = boundary.get("controller_offline_after_hold_ns")
    require(
        all(isinstance(value, int) for value in (started, released, active, heartbeat, offline))
        and started > 0
        and released > started
        and active == released - started
        and 1_800_000_000 <= heartbeat < 30_000_000_000
        and heartbeat < offline < 240_000_000_000
        and offline <= active < 300_000_000_000,
        "actual-Tor adversarial hold timing is invalid",
    )
    path = confined(
        proof_root,
        manifest.get("actual_tor_adversarial_boundary_path"),
        "actual-tor-adversarial-boundary.json",
    )
    require(
        manifest.get("actual_tor_adversarial_boundary_sha256") == digest(path)
        and load(path) == boundary,
        "actual-Tor adversarial boundary file disagrees with the manifest",
    )
    tor_roles = manifest.get("actual_tor_role_evidence")
    roles = boundary.get("roles")
    require(
        isinstance(tor_roles, list)
        and len(tor_roles) == 2
        and isinstance(roles, list)
        and len(roles) == 2,
        "actual-Tor adversarial role evidence is incomplete",
    )
    role_keys = {
        "admitted_count",
        "audit_path",
        "audit_sha256",
        "chain_count",
        "denied_count",
        "exact_chain_to_tor_binding",
        "guest_chain_count",
        "hold_observation_count",
        "listen_endpoint",
        "listener_inode",
        "process_pid",
        "role",
        "tor_control_events_path",
        "upstream_endpoint",
        "upstream_source_set_sha256",
    }
    for record, tor_record, role in zip(roles, tor_roles, ROLES):
        require(
            isinstance(record, dict)
            and set(record) == role_keys
            and record.get("role") == role
            and record.get("listen_endpoint")
            == f"10.0.0.1:{ACTUAL_TOR_SOCKS_PORTS[role]}"
            and record.get("upstream_endpoint")
            == f"127.0.0.1:{ACTUAL_TOR_UPSTREAM_SOCKS_PORTS[role]}"
            and record.get("exact_chain_to_tor_binding") is True
            and record.get("denied_count") == 0
            and isinstance(record.get("process_pid"), int)
            and record["process_pid"] > 1
            and str(record.get("listener_inode", "")).isdecimal()
            and int(record["listener_inode"]) > 0
            and SHA256.fullmatch(
                str(record.get("upstream_source_set_sha256", ""))
            )
            is not None,
            f"{role} adversarial interposer topology is invalid",
        )
        audit = confined(
            proof_root,
            record.get("audit_path"),
            f"actual-tor-{role}-adversary-audit.jsonl",
        )
        require(
            record.get("audit_sha256") == digest(audit),
            f"{role} adversarial audit digest mismatch",
        )
        entries = [
            json.loads(line)
            for line in audit.read_text(encoding="ascii").splitlines()
        ]
        admitted = [
            entry
            for entry in entries
            if entry.get("event") == "socks5-connect"
            and entry.get("outcome") == "admitted"
        ]
        chains = [
            entry
            for entry in entries
            if entry.get("event") == "socks5-chain"
            and entry.get("outcome") == "admitted-chain"
        ]
        holds = [
            entry
            for entry in entries
            if entry.get("event") == "relay-hold"
            and entry.get("outcome") == "held"
        ]
        denied = [
            entry
            for entry in entries
            if str(entry.get("outcome", "")).startswith("denied")
        ]
        guest_prefix = "10.0.0.11:" if role == "client" else "10.0.0.12:"
        guest_chains = [
            entry
            for entry in chains
            if str(entry.get("client_source", "")).startswith(guest_prefix)
        ]
        require(
            len(admitted) == record.get("admitted_count")
            == len(chains)
            == record.get("chain_count")
            and len(guest_chains) == record.get("guest_chain_count")
            and len(guest_chains) >= 1
            and len(holds) == record.get("hold_observation_count")
            and (len(holds) >= 1 if role == "client" else len(holds) == 0)
            and not denied,
            f"{role} adversarial audit counters are invalid",
        )
        target = (
            f"{manifest['actual_tor_node']['address']}:"
            f"{manifest['actual_tor_node']['port']}"
        )
        upstream_sources = sorted(
            str(entry.get("upstream_source", "")) for entry in chains
        )
        require(
            all(
                entry.get("target") == target
                and entry.get("upstream_destination")
                == record.get("upstream_endpoint")
                and re.fullmatch(r"127\.0\.0\.1:[1-9][0-9]{0,4}", source)
                is not None
                for entry, source in zip(chains, upstream_sources)
            )
            and hashlib.sha256(
                ("\n".join(upstream_sources) + "\n").encode("ascii")
            ).hexdigest()
            == record.get("upstream_source_set_sha256"),
            f"{role} adversarial upstream attribution is invalid",
        )
        events = confined(
            proof_root,
            record.get("tor_control_events_path"),
            f"tor-{role}-control-events.txt",
        )
        event_lines = events.read_text(encoding="ascii").splitlines()
        require(
            record.get("tor_control_events_path") == tor_record.get("events_path")
            and all(
                any(
                    f"SOURCE_ADDR={source}" in line and f" {target} " in line
                    for line in event_lines
                )
                for source in upstream_sources
            ),
            f"{role} adversarial chain lacks exact Tor control attribution",
        )
        if role == "client":
            require(
                any(
                    str(entry.get("client_source", "")).startswith("10.0.0.1:")
                    and started <= entry.get("monotonic_ns", 0) <= released
                    for entry in chains
                )
                and all(
                    started <= entry.get("monotonic_ns", 0) <= released
                    for entry in holds
                ),
                "during-hold SOCKS admission or hold observation is absent",
            )
    require(
        boundary.get("tor_process_pid") == tor_roles[0].get("process_pid")
        and boundary.get("tor_control_socket_inode")
        == tor_roles[0].get("control_socket_inode")
        and boundary.get("interposer_process_pid") == roles[0].get("process_pid")
        and boundary.get("interposer_listener_inode")
        == roles[0].get("listener_inode"),
        "adversarial lifecycle is not bound to client process identities",
    )


def verify_actual_tor_ratox_churn(
    proof_root: Path, manifest: dict, expected: bool
) -> None:
    churn = manifest.get("actual_tor_ratox_churn", {})
    if not expected:
        require(
            churn == {}
            and manifest.get("actual_tor_ratox_churn_path") is None
            and manifest.get("actual_tor_ratox_churn_sha256") is None,
            "non-soak scenario claims actual-Tor Ratox circuit churn",
        )
        return

    require(
        isinstance(churn, dict)
        and set(churn)
        == {
            "active_wall_ns",
            "churn_ordinals",
            "churns",
            "completed_ns",
            "controller_lifecycle_path",
            "controller_lifecycle_sha256",
            "iotox_daemon_restarts",
            "sample_count",
            "sample_interval_ms",
            "schema",
            "started_ns",
            "tor_process_restarts",
        }
        and churn.get("schema") == "iotox-actual-tor-ratox-churn-v3"
        and churn.get("sample_count") == RATOX_ACTUAL_TOR_SOAK_SAMPLES
        and churn.get("sample_interval_ms")
        == RATOX_ACTUAL_TOR_SOAK_INTERVAL_MS
        and churn.get("churn_ordinals")
        == [ordinal for _, ordinal in RATOX_ACTUAL_TOR_SOAK_CHURNS]
        and churn.get("iotox_daemon_restarts") == 0
        and churn.get("tor_process_restarts") == 0
        and isinstance(churn.get("started_ns"), int)
        and isinstance(churn.get("completed_ns"), int)
        and isinstance(churn.get("active_wall_ns"), int)
        and 0 < churn["started_ns"] < churn["completed_ns"]
        and churn["active_wall_ns"]
        == churn["completed_ns"] - churn["started_ns"]
        and churn["active_wall_ns"] < 600_000_000_000,
        "actual-Tor Ratox churn envelope is invalid",
    )
    churn_path = confined(
        proof_root,
        manifest.get("actual_tor_ratox_churn_path"),
        "actual-tor-ratox-churn.json",
    )
    require(
        manifest.get("actual_tor_ratox_churn_sha256") == digest(churn_path)
        and load(churn_path) == churn,
        "actual-Tor Ratox churn file disagrees with the manifest",
    )
    lifecycle_path = confined(
        proof_root,
        churn.get("controller_lifecycle_path"),
        "client/live/workspace-export/guest-receipts/iotox/"
        "ratox-circuit-churn-probe.json",
    )
    lifecycle = load(lifecycle_path)
    require(
        churn.get("controller_lifecycle_sha256") == digest(lifecycle_path)
        and set(lifecycle)
        == {
            "final_generation",
            "initial",
            "peer_public_key_sha256",
            "resume_count",
            "schema",
            "session_id_sha256",
            "status",
            "transitions",
        }
        and lifecycle.get("schema")
        == "iotox-ratox-circuit-churn-probe-v2"
        and lifecycle.get("status") == "passed"
        and SHA256.fullmatch(
            str(lifecycle.get("peer_public_key_sha256", ""))
        )
        is not None
        and SHA256.fullmatch(str(lifecycle.get("session_id_sha256", "")))
        is not None,
        "actual-Tor Ratox controller churn lifecycle is invalid",
    )
    capture_path = confined(
        proof_root,
        "client/live/workspace-export/guest-receipts/iotox/"
        "ratox-controller-capture.tsv",
        "client/live/workspace-export/guest-receipts/iotox/"
        "ratox-controller-capture.tsv",
    )
    capture_lines = capture_path.read_text(encoding="ascii").splitlines()
    capture_peers = [
        line.split("\t", 1)[1]
        for line in capture_lines
        if line.startswith("peer-public-key-sha256\t")
    ]
    capture_rows = [
        line.split("\t") for line in capture_lines if line.startswith("sample\t")
    ]
    require(
        capture_peers == [lifecycle["peer_public_key_sha256"]]
        and len(capture_rows) == RATOX_ACTUAL_TOR_SOAK_SAMPLES
        and len({row[5] for row in capture_rows}) == 1
        and hashlib.sha256(bytes.fromhex(capture_rows[0][5])).hexdigest()
        == lifecycle["session_id_sha256"],
        "actual-Tor Ratox churn lifecycle disagrees with terminal capture",
    )
    initial = lifecycle.get("initial")
    observation_keys = {
        "capability_observed",
        "claimant_principal_present",
        "claimant_proof_sent",
        "connection",
        "generation",
        "incarnation",
        "input_sequence",
        "online_epoch",
        "output_sequence",
        "session_state",
    }
    require(
        isinstance(initial, dict)
        and set(initial) == observation_keys
        and initial.get("session_state") == "confirmed"
        and initial.get("connection") == "tcp"
        and isinstance(initial.get("online_epoch"), int)
        and initial["online_epoch"] > 0
        and isinstance(initial.get("incarnation"), int)
        and initial["incarnation"] > 0
        and initial.get("generation") == 1
        and initial.get("input_sequence") == 1
        and initial.get("output_sequence") == 1
        and initial.get("capability_observed") == 1
        and initial.get("claimant_proof_sent") == 1
        and initial.get("claimant_principal_present") == 1,
        "actual-Tor Ratox churn initial controller identity is invalid",
    )
    lifecycle_transitions = lifecycle.get("transitions")
    transition_keys = {
        "capability_observed",
        "claimant_principal_present",
        "claimant_proof_sent",
        "connection",
        "controller_error_detail_sha256",
        "generation_after",
        "generation_before",
        "input_sequence",
        "ordinal",
        "outcome",
        "observed_us",
        "output_sequence",
        "previous_online_epoch",
        "recovered_online_epoch",
        "release_us",
        "resume_opened_us",
        "route_ready_us",
    }
    require(
        isinstance(lifecycle_transitions, list)
        and len(lifecycle_transitions) == len(RATOX_ACTUAL_TOR_SOAK_CHURNS),
        "actual-Tor Ratox churn controller transitions are incomplete",
    )
    previous_epoch = initial["online_epoch"]
    previous_generation = initial["generation"]
    observed_resumes = 0
    for index, (transition, (_, ordinal)) in enumerate(
        zip(lifecycle_transitions, RATOX_ACTUAL_TOR_SOAK_CHURNS), 1
    ):
        expected_input = int(capture_rows[ordinal - 1][7])
        expected_output = int(capture_rows[ordinal - 1][9])
        outcome = transition.get("outcome") if isinstance(transition, dict) else None
        explicit_resume = outcome == "explicit-resume"
        require(
            isinstance(transition, dict)
            and set(transition) == transition_keys
            and outcome in {"attachment-continuous", "explicit-resume"}
            and transition.get("ordinal") == ordinal
            and transition.get("connection") == "tcp"
            and transition.get("generation_before") == previous_generation
            and transition.get("generation_after")
            == previous_generation + int(explicit_resume)
            and transition.get("previous_online_epoch") == previous_epoch
            and isinstance(transition.get("recovered_online_epoch"), int)
            and (
                transition["recovered_online_epoch"] > previous_epoch
                if explicit_resume
                else transition["recovered_online_epoch"] == previous_epoch
            )
            and transition.get("input_sequence") == expected_input
            and transition.get("output_sequence") == expected_output
            and transition.get("capability_observed") == 1
            and transition.get("claimant_proof_sent") == 1
            and transition.get("claimant_principal_present") == 1
            and isinstance(transition.get("release_us"), int)
            and isinstance(transition.get("observed_us"), int)
            and isinstance(transition.get("route_ready_us"), int)
            and isinstance(transition.get("resume_opened_us"), int)
            and transition["release_us"] <= transition["observed_us"]
            and (
                SHA256.fullmatch(
                    str(transition.get("controller_error_detail_sha256", ""))
                )
                is not None
                and transition["observed_us"]
                <= transition["route_ready_us"]
                <= transition["resume_opened_us"]
                if explicit_resume
                else transition.get("controller_error_detail_sha256") == ""
                and transition["route_ready_us"] == transition["observed_us"]
                and transition["resume_opened_us"] == 0
            ),
            f"actual-Tor Ratox churn transition {index} is invalid",
        )
        previous_epoch = transition["recovered_online_epoch"]
        previous_generation = transition["generation_after"]
        observed_resumes += int(explicit_resume)
    require(
        lifecycle.get("resume_count") == observed_resumes
        and lifecycle.get("final_generation") == previous_generation
        and previous_generation == 1 + observed_resumes,
        "actual-Tor Ratox churn final generation/resume count is invalid",
    )

    role_evidence = manifest.get("actual_tor_role_evidence")
    require(
        isinstance(role_evidence, list) and len(role_evidence) == 2,
        "actual-Tor Ratox churn lacks continuous role evidence",
    )
    evidence_by_role = {
        entry.get("role"): entry
        for entry in role_evidence
        if isinstance(entry, dict)
    }
    require(
        set(evidence_by_role) == set(ROLES),
        "actual-Tor Ratox churn role evidence is incomplete",
    )
    node = manifest.get("actual_tor_node")
    require(isinstance(node, dict), "actual-Tor Ratox churn node is absent")
    target = f"{node.get('address')}:{node.get('port')}"
    records = churn.get("churns")
    require(
        isinstance(records, list)
        and len(records) == len(RATOX_ACTUAL_TOR_SOAK_CHURNS),
        "actual-Tor Ratox churn records are incomplete",
    )

    previous_completed = churn["started_ns"]
    phase_keys = {
        "circuit_status_path",
        "circuit_status_sha256",
        "circuit_hop_count",
        "circuit_id_sha256",
        "circuit_path_sha256",
        "circuit_purpose",
        "stream_status_path",
        "stream_status_sha256",
        "stream_id_sha256",
    }
    for record, (role, ordinal) in zip(records, RATOX_ACTUAL_TOR_SOAK_CHURNS):
        require(
            isinstance(record, dict)
            and set(record)
            == {
                "after",
                "before",
                "close_reason",
                "command",
                "completed_ns",
                "control_socket_inode",
                "ordinal",
                "process_pid",
                "recovery_ns",
                "role",
                "started_ns",
                "stream_transition",
            }
            and record.get("role") == role
            and record.get("ordinal") == ordinal
            and record.get("command") == "CLOSECIRCUIT"
            and record.get("close_reason") == "REQUESTED"
            and record.get("stream_transition")
            in {"stream-reattached", "stream-reopened"}
            and isinstance(record.get("started_ns"), int)
            and isinstance(record.get("completed_ns"), int)
            and isinstance(record.get("recovery_ns"), int)
            and previous_completed <= record["started_ns"]
            < record["completed_ns"] <= churn["completed_ns"]
            and record["recovery_ns"]
            == record["completed_ns"] - record["started_ns"]
            and 0 < record["recovery_ns"] < 180_000_000_000,
            f"{role} actual-Tor Ratox churn record is invalid",
        )
        previous_completed = record["completed_ns"]
        evidence = evidence_by_role[role]
        require(
            record.get("process_pid") == evidence.get("process_pid")
            and record.get("control_socket_inode")
            == evidence.get("control_socket_inode"),
            f"{role} Tor process/control identity changed during churn",
        )
        before = record.get("before")
        after = record.get("after")
        require(
            isinstance(before, dict)
            and isinstance(after, dict)
            and set(before) == phase_keys
            and set(after) == phase_keys
            and (
                before["stream_id_sha256"] == after["stream_id_sha256"]
            )
            == (record["stream_transition"] == "stream-reattached")
            and before["circuit_id_sha256"] != after["circuit_id_sha256"],
            f"{role} actual-Tor churn did not prove its stream transition and replacement circuit",
        )

        events_path = confined(
            proof_root,
            evidence.get("events_path"),
            f"tor-{role}-control-events.txt",
        )
        expected_source = "10.0.0.11" if role == "client" else "10.0.0.12"
        sources: dict[str, int] = {}
        successes: list[tuple[str, str, int]] = []
        stream_closes: list[tuple[str, str, int]] = []
        built: dict[str, tuple[str, str, int]] = {}
        closed: list[tuple[str, str, int]] = []
        for index, line in enumerate(
            events_path.read_text(encoding="ascii").splitlines()
        ):
            fields = line.split()
            if len(fields) >= 5 and fields[:2] == ["650", "CIRC"]:
                if fields[3] == "BUILT":
                    purposes = [
                        value.split("=", 1)[1]
                        for value in fields[5:]
                        if value.startswith("PURPOSE=")
                    ]
                    require(
                        len(purposes) == 1,
                        f"{role} Tor built circuit has ambiguous purpose",
                    )
                    built[fields[2]] = (fields[4], purposes[0], index)
                elif fields[3] == "CLOSED":
                    reasons = [
                        value.split("=", 1)[1]
                        for value in fields[4:]
                        if value.startswith("REASON=")
                    ]
                    require(
                        len(reasons) == 1,
                        f"{role} Tor closed circuit has ambiguous reason",
                    )
                    closed.append((fields[2], reasons[0], index))
                continue
            if len(fields) < 6 or fields[:2] != ["650", "STREAM"]:
                continue
            stream_id, state, circuit_id, stream_target = fields[2:6]
            if state == "NEW":
                source_values = [
                    value.split("=", 1)[1]
                    for value in fields[6:]
                    if value.startswith("SOURCE_ADDR=")
                ]
                if len(source_values) == 1:
                    source_host, _, _ = source_values[0].rpartition(":")
                    if source_host == expected_source:
                        require(
                            stream_target == target,
                            f"{role} Tor churn stream escaped its exact target",
                        )
                        sources[stream_id] = index
            elif state == "SUCCEEDED" and stream_id in sources:
                require(
                    stream_target == target,
                    f"{role} Tor churn success changed target",
                )
                successes.append((stream_id, circuit_id, index))
            elif state == "CLOSED" and stream_id in sources:
                require(
                    stream_target == target,
                    f"{role} Tor churn close changed target",
                )
                stream_closes.append((stream_id, circuit_id, index))

        resolved: list[tuple[str, str, int | None]] = []
        for phase_name, phase in (("before", before), ("after", after)):
            require(
                all(
                    SHA256.fullmatch(str(phase[key])) is not None
                    for key in (
                        "stream_id_sha256",
                        "circuit_id_sha256",
                        "circuit_path_sha256",
                    )
                )
                and isinstance(phase["circuit_hop_count"], int)
                and phase["circuit_hop_count"] >= 3
                and phase["circuit_purpose"]
                in TOR_APPLICATION_CIRCUIT_PURPOSES,
                f"{role} Tor churn phase commitment is invalid",
            )
            stream_snapshot_path = confined(
                proof_root,
                phase.get("stream_status_path"),
                f"tor-{role}-churn-{ordinal}-{phase_name}-stream-status.txt",
            )
            circuit_snapshot_path = confined(
                proof_root,
                phase.get("circuit_status_path"),
                f"tor-{role}-churn-{ordinal}-{phase_name}-circuit-status.txt",
            )
            require(
                phase.get("stream_status_sha256") == digest(stream_snapshot_path)
                and phase.get("circuit_status_sha256")
                == digest(circuit_snapshot_path),
                f"{role} Tor churn {phase_name} snapshot digest mismatch",
            )
            stream_snapshot_matches = []
            for line in stream_snapshot_path.read_text(encoding="ascii").splitlines():
                fields = line.split()
                if (
                    len(fields) >= 4
                    and hashlib.sha256(fields[0].encode("ascii")).hexdigest()
                    == phase["stream_id_sha256"]
                ):
                    stream_snapshot_matches.append(fields)
            circuit_snapshot_matches = []
            for line in circuit_snapshot_path.read_text(encoding="ascii").splitlines():
                fields = line.split()
                if (
                    len(fields) >= 3
                    and hashlib.sha256(fields[0].encode("ascii")).hexdigest()
                    == phase["circuit_id_sha256"]
                ):
                    circuit_snapshot_matches.append(fields)
            require(
                len(stream_snapshot_matches) == 1
                and len(circuit_snapshot_matches) == 1,
                f"{role} Tor churn {phase_name} snapshot identity is ambiguous",
            )
            stream_snapshot = stream_snapshot_matches[0]
            circuit_snapshot = circuit_snapshot_matches[0]
            circuit_purposes = [
                value.split("=", 1)[1]
                for value in circuit_snapshot[3:]
                if value.startswith("PURPOSE=")
            ]
            require(
                stream_snapshot[1] == "SUCCEEDED"
                and hashlib.sha256(stream_snapshot[2].encode("ascii")).hexdigest()
                == phase["circuit_id_sha256"]
                and stream_snapshot[3] == target
                and circuit_snapshot[1] == "BUILT"
                and hashlib.sha256(circuit_snapshot[2].encode("ascii")).hexdigest()
                == phase["circuit_path_sha256"]
                and len(circuit_snapshot[2].split(","))
                == phase["circuit_hop_count"]
                and circuit_purposes == [phase["circuit_purpose"]],
                f"{role} Tor churn {phase_name} authenticated snapshot is invalid",
            )
            stream_id = stream_snapshot[0]
            circuit_id = circuit_snapshot[0]
            event_matches = [
                (stream_id, circuit_id, success_index)
                for stream_id, circuit_id, success_index in successes
                if hashlib.sha256(stream_id.encode("ascii")).hexdigest()
                == phase["stream_id_sha256"]
                and hashlib.sha256(circuit_id.encode("ascii")).hexdigest()
                == phase["circuit_id_sha256"]
            ]
            needs_success_event = (
                phase_name == "before"
                or record["stream_transition"] == "stream-reopened"
            )
            require(
                (len(event_matches) == 1 if needs_success_event else len(event_matches) <= 1)
                and stream_id in sources
                and circuit_id in built,
                f"{role} Tor churn {phase_name} event attribution is invalid",
            )
            success_index = event_matches[0][2] if event_matches else None
            require(
                success_index is None or sources[stream_id] < success_index,
                f"{role} Tor churn {phase_name} event order is invalid",
            )
            path, _, _ = built[circuit_id]
            require(
                hashlib.sha256(path.encode("ascii")).hexdigest()
                == phase["circuit_path_sha256"]
                and len(path.split(",")) == phase["circuit_hop_count"],
                f"{role} Tor churn circuit commitment disagrees with raw events",
            )
            resolved.append((stream_id, circuit_id, success_index))

        before_circuit = resolved[0][1]
        requested_closes = [
            close_index
            for circuit_id, reason, close_index in closed
            if circuit_id == before_circuit and reason == "REQUESTED"
        ]
        require(
            len(requested_closes) == 1
            and resolved[0][2] is not None
            and resolved[0][2] < requested_closes[0],
            f"{role} Tor raw events do not prove requested close then recovery",
        )
        if record["stream_transition"] == "stream-reopened":
            require(
                resolved[1][2] is not None
                and requested_closes[0] < resolved[1][2],
                f"{role} Tor raw events do not prove stream reopen after close",
            )
        else:
            after_closes = [
                close_index
                for stream_id, circuit_id, close_index in stream_closes
                if stream_id == resolved[1][0]
                and circuit_id == resolved[1][1]
            ]
            require(
                len(after_closes) == 1
                and requested_closes[0] < after_closes[0],
                f"{role} Tor raw events do not prove reattached stream on replacement circuit",
            )


def verify_pair(
    proof_root: Path,
    expected_route: str | None = None,
    expected_scenario: str | None = None,
) -> dict:
    proof_root = proof_root.resolve()
    manifest = load(proof_root / "pair-manifest.json")
    route = manifest.get("route_mode")
    require(route in ROUTES, "unknown route mode")
    if expected_route is not None:
        require(route == expected_route, "route mode mismatch")
    scenario = manifest.get("scenario", "baseline")
    require(
        scenario
        in {
            "baseline",
            "relay-restart",
            "proxy-restart",
            "i2p-router-restart",
            "i2p-service-restart",
            "daemon-restart",
            "link-interruption",
            "packet-loss",
            "guest-restart",
            "ratox-idle",
            "ratox-matrix-idle",
            "ratox-route-impairment",
            "ratox-route-loss",
            "ratox-cli-reconnect",
            "ratox-cli-reconnect-repeated",
            "ratox-route-actual-tor-loss",
            "ratox-route-actual-tor-soak",
            "ratox-route-actual-tor-adversary",
            *MUTABLE_SCENARIOS,
            *BIDIRECTIONAL_SYNC_SCENARIOS,
            *AUTOMATION_SYNC_SCENARIOS,
            *SYNC_SCENARIOS,
            *RATOX_BULK_SCENARIOS,
        },
        "unknown pair scenario",
    )
    require(
        scenario != "relay-restart" or route == "forced-tcp",
        "relay restart is not a forced-TCP proof",
    )
    require(
        scenario != "proxy-restart" or route == "tox-tor",
        "proxy restart is not a Tox/Tor proof",
    )
    require(
        scenario != "i2p-router-restart" or route in I2P_ROUTES,
        "I2P router restart is not a Tox/I2P proof",
    )
    require(
        scenario != "i2p-service-restart" or route in I2P_ROUTES,
        "I2P service restart is not a Tox/I2P proof",
    )
    require(
        scenario not in {
            "ratox-route-actual-tor-loss",
            "ratox-route-actual-tor-soak",
            "ratox-route-actual-tor-adversary",
        }
        or route == "tox-tor",
        "actual-Tor Ratox scenario is not a Tox/Tor proof",
    )
    require(
        route != "tox-tor"
        or scenario
        in {
            "baseline",
            "proxy-restart",
            "ratox-route-impairment",
            "ratox-route-loss",
            "ratox-cli-reconnect",
            "ratox-route-actual-tor-loss",
            "ratox-route-actual-tor-soak",
            "ratox-route-actual-tor-adversary",
        },
        "unsupported Tox/Tor proof scenario",
    )
    require(
        route not in I2P_ROUTES
        or scenario in {"baseline", "i2p-router-restart", "i2p-service-restart"},
        "unsupported Tox/I2P proof scenario",
    )
    require(
        scenario not in RATOX_STRIPE_SCENARIOS or route == "forced-tcp",
        "Ratox stripe is not a forced-TCP proof",
    )
    require(
        scenario != "sync-content-multi-source-loss"
        or route == "direct-udp",
        "selected-source loss is not a direct-UDP proof",
    )
    mixed_context_scenarios = {
        "sync-content-route-private-actual-tor",
        "sync-content-same-source-multi-route-actual-tor",
        "sync-content-multi-route-actual-tor",
        "sync-content-multi-route-actual-tor-loss",
        "sync-tree-route-private-mixed",
        "sync-tree-route-private-actual-tor",
        "sync-tree-route-private-actual-tor-payload",
        "sync-tree-route-private-actual-i2p-payload",
        "sync-tree-route-private-actual-i2p-loss",
        "sync-file-range-actual-i2p",
        "sync-file-range-actual-i2p-loss",
        "sync-tree-route-private-actual-tor-loss",
    }
    require(
        scenario not in mixed_context_scenarios or route == "direct-udp",
        "mixed-context synchronization is not a direct-UDP proof",
    )
    if expected_scenario is not None:
        require(scenario == expected_scenario, "pair scenario mismatch")
    connection = ROUTES[route]
    require(manifest.get("schema") == "iotox.sandwurm-pair-manifest.v0", "unexpected manifest schema")
    require(manifest.get("status") == "passed", "pair manifest did not pass")
    atomic_multi_source = (
        scenario in CONTENT_MULTI_SOURCE_SCENARIOS
        and "multi_source_atomic_pull_role_count" in manifest
    )
    require(
        scenario
        not in {
            "sync-content-multi-source-loss",
            "sync-content-multi-route-actual-tor-loss",
        }
        or atomic_multi_source,
        "selected-source loss omitted atomic source admission",
    )
    require(manifest.get("expected_connection") == connection, "manifest connection mismatch")
    require(
        manifest.get("network", "Tox/native")
        == expected_network(route),
        "manifest network projection mismatch",
    )
    require(manifest.get("simultaneous_vmm_chains_observed") is True, "simultaneous VMM observation is absent")
    require(manifest.get("prepared_bridge") == "sandwurm-vm", "prepared bridge mismatch")
    require(manifest.get("bootstrap_fixture") == "pinned-host-bridge-c-toxcore-0.2.23", "bootstrap fixture mismatch")
    restart_count = manifest.get("bootstrap_fixture_restart_count", 0)
    daemon_restart_count = manifest.get("device_daemon_restart_count", 0)
    link_interruption_count = manifest.get("link_interruption_count", 0)
    packet_loss_impairment_count = manifest.get("packet_loss_impairment_count", 0)
    guest_restart_count = manifest.get("device_guest_restart_count", 0)
    bulk_stream_count = RATOX_BULK_SCENARIOS.get(scenario, 0)
    sample_count = ratox_sample_count(scenario) if scenario in RATOX_SCENARIOS else 0
    stripe_route_count = RATOX_STRIPE_SCENARIOS.get(scenario, 1)
    protected_live_loss = scenario == "ratox-stripe-protected-live-loss-24"
    protected_route_scenario = (
        protected_live_loss
        or scenario in MULTI_ROUTE_SYNC_SCENARIOS
    )
    sync_cancellation = scenario in SYNC_CANCELLATION_SCENARIOS
    mutable_scenario = scenario in MUTABLE_SCENARIOS
    stripe_route_restart_count = manifest.get("ratox_stripe_route_restart_count", 0)
    stripe_injected_restart_count = manifest.get(
        "ratox_stripe_injected_restart_count", 0
    )
    compact = manifest.get("compact_export")
    key_preserved = manifest.get("bootstrap_fixture_key_preserved", True)
    require(
        restart_count == (1 if scenario == "relay-restart" else 0),
        "bootstrap fixture restart count mismatch",
    )
    require(key_preserved is True, "bootstrap fixture key was not preserved")
    mixed_context = scenario in mixed_context_scenarios
    actual_tor = scenario in {
        "sync-content-route-private-actual-tor",
        "sync-content-same-source-multi-route-actual-tor",
        "sync-content-multi-route-actual-tor",
        "sync-content-multi-route-actual-tor-loss",
        "sync-tree-route-private-actual-tor",
        "sync-tree-route-private-actual-tor-payload",
        "sync-tree-route-private-actual-tor-loss",
        "ratox-route-actual-tor-loss",
        "ratox-route-actual-tor-soak",
        "ratox-route-actual-tor-adversary",
    }
    actual_tor_payload = scenario in {
        "sync-content-route-private-actual-tor",
        "sync-content-same-source-multi-route-actual-tor",
        "sync-content-multi-route-actual-tor",
        "sync-content-multi-route-actual-tor-loss",
        "sync-tree-route-private-actual-tor-payload",
    }
    actual_i2p_payload = scenario in {
        "sync-tree-route-private-actual-i2p-payload",
        "sync-tree-route-private-actual-i2p-loss",
        "sync-file-range-actual-i2p",
        "sync-file-range-actual-i2p-loss",
    }
    actual_i2p_loss = scenario in {
        "sync-tree-route-private-actual-i2p-loss",
        "sync-file-range-actual-i2p-loss",
    }
    actual_tor_loss = scenario == "sync-tree-route-private-actual-tor-loss"
    actual_tor_ratox_loss = scenario == "ratox-route-actual-tor-loss"
    actual_tor_ratox_soak = scenario == "ratox-route-actual-tor-soak"
    actual_tor_ratox_adversary = (
        scenario == "ratox-route-actual-tor-adversary"
    )
    actual_i2p = route in I2P_ROUTES or actual_i2p_payload
    routed_socks5 = (
        route == "tox-tor" and not actual_tor
    ) or scenario == "sync-tree-route-private-mixed"
    routed_privacy = routed_socks5 or actual_tor or actual_i2p
    verify_actual_i2p_evidence(proof_root, manifest, actual_i2p)
    verify_actual_i2p_fail_closed_loss(
        proof_root, manifest, actual_i2p_loss
    )
    verify_actual_tor_evidence(proof_root, manifest, actual_tor)
    verify_actual_tor_ratox_churn(
        proof_root, manifest, actual_tor_ratox_soak
    )
    verify_actual_tor_adversarial_boundary(
        proof_root, manifest, actual_tor_ratox_adversary
    )
    require(
        manifest.get("actual_tor_payload_observed_role_count", 0)
        == (1 if actual_tor_payload else 0)
        and (
            SHA256.fullmatch(
                str(manifest.get("actual_tor_payload_carrier_sha256", ""))
            )
            is not None
            if actual_tor_payload
            else manifest.get("actual_tor_payload_carrier_sha256", "") == ""
        )
        and manifest.get("actual_tor_payload_reassignments", 0) == 0,
        "actual-Tor payload manifest evidence is invalid",
    )
    require(
        manifest.get("actual_i2p_payload_observed_role_count", 0)
        == (1 if actual_i2p_payload else 0)
        and (
            SHA256.fullmatch(
                str(manifest.get("actual_i2p_payload_carrier_sha256", ""))
            )
            is not None
            if actual_i2p_payload
            else manifest.get("actual_i2p_payload_carrier_sha256", "") == ""
        )
        and manifest.get("actual_i2p_payload_reassignments", 0) == 0,
        "actual-I2P payload manifest evidence is invalid",
    )
    pull_attempts = manifest.get("sync_initial_pull_attempts", 0)
    pull_failures = manifest.get("sync_initial_pull_failures", 0)
    pull_error_digest = manifest.get(
        "sync_initial_pull_first_error_sha256", ""
    )
    if actual_tor_payload or actual_i2p_payload or "sync_initial_pull_attempts" in manifest:
        if scenario in SYNC_SCENARIOS:
            require(
                isinstance(pull_attempts, int)
                and pull_attempts >= 1
                and isinstance(pull_failures, int)
                and 0 <= pull_failures < pull_attempts
                and pull_attempts == pull_failures + 1
                and (
                    SHA256.fullmatch(str(pull_error_digest)) is not None
                    if pull_failures > 0
                    else pull_error_digest == ""
                ),
                "sync pull admission manifest evidence is invalid",
            )
        else:
            require(
                pull_attempts == 0
                and pull_failures == 0
                and pull_error_digest == "",
                "non-sync manifest claims sync pull admission",
            )
    require(
        manifest.get("socks5_proxy")
        == ("10.0.0.1:39050" if routed_socks5 else None)
        and manifest.get("socks5_allowed_target")
        == ("10.0.0.1:33445" if routed_socks5 else None),
        "strict SOCKS topology mismatch",
    )
    forwarder_digest = manifest.get("socks5_forwarder_sha256")
    require(
        forwarder_digest
        == (digest(ROOT / "tools/run-socks5-forwarder.py") if routed_socks5 else None),
        "SOCKS forwarder digest mismatch",
    )
    require(
        manifest.get("socks5_restart_count", 0)
        == int(scenario == "proxy-restart"),
        "SOCKS restart count mismatch",
    )
    audits = manifest.get("socks5_audits", [])
    require(
        isinstance(audits, list)
        and len(audits) == (2 if scenario == "proxy-restart" else 1 if routed_socks5 else 0),
        "SOCKS audit phase count mismatch",
    )
    admitted_total = 0
    denied_total = 0
    for index, audit in enumerate(audits):
        expected_phase = "initial" if index == 0 else "restart"
        expected_path = f"socks5-{expected_phase}-audit.jsonl"
        audit_path = confined(proof_root, audit.get("path"), expected_path)
        require(audit.get("phase") == expected_phase, "SOCKS audit phase mismatch")
        require(audit.get("sha256") == digest(audit_path), "SOCKS audit digest mismatch")
        records = [
            json.loads(line)
            for line in audit_path.read_text(encoding="ascii").splitlines()
        ]
        admitted = sum(record.get("outcome") == "admitted" for record in records)
        denied = len(records) - admitted
        require(admitted >= 2 and denied == 0, "SOCKS audit did not contain both clean routes")
        require(
            all(record.get("target") == "10.0.0.1:33445" for record in records),
            "SOCKS audit target escaped the bootstrap fixture",
        )
        require(
            audit.get("admitted") == admitted and audit.get("denied") == denied,
            "SOCKS audit counters mismatch",
        )
        admitted_total += admitted
        denied_total += denied
    require(
        manifest.get("socks5_admitted", 0) == admitted_total
        and manifest.get("socks5_denied", 0) == denied_total,
        "SOCKS aggregate counters mismatch",
    )
    containment = manifest.get("route_packet_containment", [])
    require(
        isinstance(containment, list)
        and len(containment) == (2 if routed_privacy else 0),
        "route packet-containment count mismatch",
    )
    for index, entry in enumerate(containment):
        role = ROLES[index]
        expected_tap = "vm-iotoxc" if role == "client" else "vm-iotoxd"
        capture_path = confined(
            proof_root,
            entry.get("path"),
            f"{role}.tox-i2p.pcapng" if actual_i2p else f"{role}.tox-tor.pcapng",
        )
        common_valid = (
            entry.get("role") == role
            and entry.get("tap") == expected_tap
            and entry.get("capture_sha256") == digest(capture_path)
            and isinstance(entry.get("egress_ipv4_packets"), int)
            and entry["egress_ipv4_packets"] > 0
        )
        if mixed_context:
            expected_proxy = (
                f"10.0.0.1:{I2P_SOCKS5_PORT}"
                if actual_i2p_payload
                else f"10.0.0.1:{ACTUAL_TOR_SOCKS_PORTS[role]}"
                if actual_tor
                else "10.0.0.1:39050"
            )
            require(
                common_valid
                and isinstance(entry.get("proxy_packets"), int)
                and entry["proxy_packets"] > 0
                and (
                    entry.get("proxy_endpoint") == expected_proxy
                    if actual_tor or actual_i2p_payload
                    else entry.get("proxy_endpoint", expected_proxy)
                    == expected_proxy
                )
                and isinstance(entry.get("native_udp_packets"), int)
                and entry["native_udp_packets"] > 0
                and isinstance(entry.get("native_tcp_relay_packets"), int)
                and entry["native_tcp_relay_packets"] >= 0
                and isinstance(entry.get("native_icmp_packets"), int)
                and entry["native_icmp_packets"] >= 0
                and entry.get("mixed_native_and_proxy") is True
                and entry.get("tcp_confined_to_configured_local_endpoints")
                is True
                and entry.get("unexpected_context_packets") == 0
                and entry.get("peer_ipv4")
                == ("10.0.0.12" if role == "client" else "10.0.0.11"),
                f"{role} mixed-context packet containment is invalid",
            )
        else:
            expected_strict_proxy = (
                f"10.0.0.1:{I2P_SOCKS5_PORT}"
                if actual_i2p
                else f"10.0.0.1:{ACTUAL_TOR_SOCKS_PORTS[role]}"
                if actual_tor_ratox_loss
                or actual_tor_ratox_soak
                or actual_tor_ratox_adversary
                else "10.0.0.1:39050"
            )
            require(
                common_valid
                and entry.get("allowed_destination") == expected_strict_proxy
                and entry.get("only_proxy_destination") is True
                and entry.get("tcp_only") is True
                and entry.get("native_udp_packets") == 0
                and entry.get("direct_bootstrap_packets") == 0
                and entry.get("direct_peer_packets") == 0,
                f"{role} packet containment is invalid",
            )
    if (
        actual_tor_ratox_loss
        or actual_tor_ratox_soak
        or actual_tor_ratox_adversary
    ):
        containment_path = confined(
            proof_root,
            "actual-tor-route-containment.json",
            "actual-tor-route-containment.json",
        )
        with containment_path.open("r", encoding="utf-8") as handle:
            retained_containment = json.load(handle)
        require(
            retained_containment == containment,
            "actual-Tor route containment file disagrees with the manifest",
        )
    if actual_i2p:
        containment_path = confined(
            proof_root,
            "tox-i2p-containment.json",
            "tox-i2p-containment.json",
        )
        with containment_path.open("r", encoding="utf-8") as handle:
            retained_containment = json.load(handle)
        require(
            retained_containment == containment,
            "actual-I2P route containment file disagrees with the manifest",
        )
    require(
        manifest.get("private_route_mixed_context_role_count", 0)
        == (2 if mixed_context else 0),
        "private mixed-context role count mismatch",
    )
    require(
        daemon_restart_count == (1 if scenario == "daemon-restart" else 0),
        "device daemon restart count mismatch",
    )
    require(
        link_interruption_count
        == (1 if scenario in {"link-interruption", "sync-file-disconnect"} else 0),
        "link interruption count mismatch",
    )
    packet_loss_scenario = scenario == "packet-loss"
    require(
        packet_loss_impairment_count == int(packet_loss_scenario),
        "partial-loss impairment count mismatch",
    )
    require(
        manifest.get("packet_loss_percent", 0)
        == (PACKET_LOSS_PERCENT if packet_loss_scenario else 0)
        and manifest.get("packet_loss_probe_count_per_role", 0)
        == (PACKET_LOSS_PROBE_COUNT if packet_loss_scenario else 0),
        "partial-loss manifest parameters mismatch",
    )
    qdisc_observations = manifest.get("packet_loss_qdiscs", [])
    require(
        isinstance(qdisc_observations, list)
        and len(qdisc_observations) == (2 if packet_loss_scenario else 0),
        "partial-loss qdisc observation count mismatch",
    )
    if packet_loss_scenario:
        require(
            {entry.get("tap") for entry in qdisc_observations}
            == set(PACKET_LOSS_SEEDS),
            "partial-loss TAP observation mismatch",
        )
        for entry in qdisc_observations:
            tap = entry.get("tap")
            require(
                entry.get("kind") == "netem"
                and entry.get("loss_percent") == PACKET_LOSS_PERCENT
                and entry.get("seed") == PACKET_LOSS_SEEDS[tap],
                f"partial-loss qdisc parameters changed on {tap}",
            )
            for counter in (
                "bytes",
                "packets",
                "drops",
                "overlimits",
                "requeues",
                "backlog",
                "qlen",
            ):
                value = entry.get(counter)
                require(
                    isinstance(value, int) and value >= 0,
                    f"invalid partial-loss {counter} counter on {tap}",
                )
            require(entry["packets"] > 0 and entry["drops"] > 0, f"partial loss was not exercised on {tap}")
    verify_common_link_fairness_qdisc(
        manifest.get("common_link_fairness_qdisc", {}),
        scenario == "sync-tree-route-common-link-fairness",
        "common-link fairness qdisc",
    )
    ratox_impairment_scenario = scenario == "ratox-route-impairment"
    ratox_route_loss_scenario = scenario in {
        "ratox-route-loss",
        "ratox-cli-reconnect",
        "ratox-cli-reconnect-repeated",
        "ratox-route-actual-tor-loss",
        "ratox-route-actual-tor-adversary",
    }
    ratox_cli_reconnect_scenario = scenario in {
        "ratox-cli-reconnect",
        "ratox-cli-reconnect-repeated",
    }
    ratox_cli_reconnect_repeated_scenario = (
        scenario == "ratox-cli-reconnect-repeated"
    )
    ratox_actual_tor_soak_scenario = (
        scenario == "ratox-route-actual-tor-soak"
    )
    impairment = manifest.get("ratox_route_impairment", {})
    require(isinstance(impairment, dict), "Ratox impairment summary is not an object")
    if ratox_impairment_scenario:
        exact_impairment_keys = {
            "active_wall_ms",
            "baseline_end_ordinal",
            "delay_ms",
            "impairment_end_ordinal",
            "jitter_ms",
            "loss_percent",
            "qdiscs",
            "recovery_sample_count",
            "sample_count",
            "schema",
        }
        require(set(impairment) == exact_impairment_keys,
                "Ratox impairment summary schema drifted")
        require(
            impairment["schema"] == "iotox-ratox-route-impairment-v1"
            and impairment["sample_count"] == RATOX_IMPAIRMENT_SAMPLES
            and impairment["baseline_end_ordinal"]
            == RATOX_IMPAIRMENT_BASELINE_END
            and impairment["impairment_end_ordinal"] == RATOX_IMPAIRMENT_END
            and impairment["recovery_sample_count"]
            == RATOX_IMPAIRMENT_SAMPLES - RATOX_IMPAIRMENT_END
            and impairment["delay_ms"] == RATOX_IMPAIRMENT_DELAY_MS
            and impairment["jitter_ms"] == RATOX_IMPAIRMENT_JITTER_MS
            and impairment["loss_percent"] == RATOX_IMPAIRMENT_LOSS_PERCENT
            and isinstance(impairment["active_wall_ms"], int)
            and 0 < impairment["active_wall_ms"] < 600_000,
            "Ratox impairment parameters or duration drifted",
        )
        impairment_path = proof_root / "ratox-route-impairment.json"
        require(impairment_path.is_file() and not impairment_path.is_symlink(),
                "Ratox impairment evidence file is absent")
        require(load(impairment_path) == impairment,
                "Ratox impairment file disagrees with the manifest")
        impairment_qdiscs = impairment["qdiscs"]
        require(isinstance(impairment_qdiscs, list)
                and len(impairment_qdiscs) == 2,
                "Ratox impairment qdisc evidence is incomplete")
        require({entry.get("tap") for entry in impairment_qdiscs}
                == set(RATOX_IMPAIRMENT_SEEDS),
                "Ratox impairment TAP set drifted")
        for entry in impairment_qdiscs:
            tap = entry.get("tap")
            require(
                entry.get("kind") == "netem"
                and entry.get("delay_ms") == RATOX_IMPAIRMENT_DELAY_MS
                and entry.get("jitter_ms") == RATOX_IMPAIRMENT_JITTER_MS
                and entry.get("loss_percent") == RATOX_IMPAIRMENT_LOSS_PERCENT
                and entry.get("seed") == RATOX_IMPAIRMENT_SEEDS[tap],
                f"Ratox impairment qdisc parameters changed on {tap}",
            )
            for counter in (
                "bytes", "packets", "drops", "overlimits", "requeues",
                "backlog", "qlen",
            ):
                require(isinstance(entry.get(counter), int) and entry[counter] >= 0,
                        f"Ratox impairment {counter} is invalid on {tap}")
            require(entry["packets"] > 0 and entry["drops"] > 0,
                    f"Ratox impairment was not exercised on {tap}")
    else:
        require(impairment == {}, "non-impairment scenario claims Ratox shaping")
        require(not (proof_root / "ratox-route-impairment.json").exists(),
                "non-impairment proof contains Ratox shaping evidence")
    route_loss = manifest.get("ratox_route_loss", {})
    require(isinstance(route_loss, dict), "Ratox route-loss summary is not an object")
    if actual_tor_ratox_adversary:
        require(
            set(route_loss)
            == {
                "active_wall_ms",
                "controller_offline_after_loss_ms",
                "detached_host_snapshot",
                "fault_kind",
                "heartbeat_missed_after_loss_ms",
                "heartbeat_timeout_ms",
                "qdiscs",
                "schema",
            }
            and route_loss.get("schema") == "iotox-ratox-route-loss-v3"
            and route_loss.get("fault_kind")
            == "actual-tor-established-byte-hold"
            and route_loss.get("heartbeat_timeout_ms") == 2000
            and route_loss.get("detached_host_snapshot") is True
            and route_loss.get("qdiscs") == []
            and isinstance(
                route_loss.get("heartbeat_missed_after_loss_ms"), int
            )
            and 1_800 <= route_loss["heartbeat_missed_after_loss_ms"] < 30_000
            and isinstance(
                route_loss.get("controller_offline_after_loss_ms"), int
            )
            and route_loss["heartbeat_missed_after_loss_ms"]
            < route_loss["controller_offline_after_loss_ms"]
            < 240_000
            and isinstance(route_loss.get("active_wall_ms"), int)
            and route_loss["controller_offline_after_loss_ms"]
            <= route_loss["active_wall_ms"]
            < 300_000,
            "adversarial actual-Tor Ratox route-loss summary is invalid",
        )
        route_loss_path = proof_root / "ratox-route-loss.json"
        boundary = manifest.get("actual_tor_adversarial_boundary", {})
        require(
            route_loss_path.is_file()
            and not route_loss_path.is_symlink()
            and load(route_loss_path) == route_loss
            and boundary.get("heartbeat_missed_after_hold_ns") // 1_000_000
            == route_loss["heartbeat_missed_after_loss_ms"]
            and boundary.get("controller_offline_after_hold_ns") // 1_000_000
            == route_loss["controller_offline_after_loss_ms"],
            "adversarial boundary and Ratox loss clocks disagree",
        )
    elif actual_tor_ratox_loss:
        require(
            set(route_loss)
            == {
                "active_wall_ms",
                "controller_offline_after_loss_ms",
                "detached_host_snapshot",
                "fault_kind",
                "heartbeat_missed_after_loss_ms",
                "heartbeat_timeout_ms",
                "qdiscs",
                "schema",
            }
            and route_loss.get("schema") == "iotox-ratox-route-loss-v2"
            and route_loss.get("fault_kind")
            == "actual-tor-process-sigkill"
            and route_loss.get("heartbeat_timeout_ms") == 2000
            and route_loss.get("detached_host_snapshot") is True
            and route_loss.get("qdiscs") == []
            and isinstance(
                route_loss.get("heartbeat_missed_after_loss_ms"), int
            )
            and 1_800
            <= route_loss["heartbeat_missed_after_loss_ms"]
            < 30_000
            and isinstance(
                route_loss.get("controller_offline_after_loss_ms"), int
            )
            and route_loss["controller_offline_after_loss_ms"]
            > route_loss["heartbeat_missed_after_loss_ms"]
            and route_loss["controller_offline_after_loss_ms"] < 240_000
            and isinstance(route_loss.get("active_wall_ms"), int)
            and route_loss["active_wall_ms"]
            >= route_loss["controller_offline_after_loss_ms"]
            and route_loss["active_wall_ms"] < 480_000,
            "actual-Tor Ratox route-loss timing or policy drifted",
        )
        route_loss_path = proof_root / "ratox-route-loss.json"
        require(
            route_loss_path.is_file()
            and not route_loss_path.is_symlink()
            and load(route_loss_path) == route_loss,
            "actual-Tor Ratox route-loss file disagrees with the manifest",
        )
        process_loss = manifest.get("actual_tor_process_loss", {})
        require(
            process_loss.get("heartbeat_missed_after_loss_ns") // 1_000_000
            == route_loss["heartbeat_missed_after_loss_ms"]
            and process_loss.get("controller_offline_after_loss_ns")
            // 1_000_000
            == route_loss["controller_offline_after_loss_ms"],
            "actual-Tor process and Ratox loss clocks disagree",
        )
    elif ratox_cli_reconnect_repeated_scenario:
        require(
            set(route_loss)
            == {
                "active_wall_ms",
                "controller_kind",
                "controller_offline_after_loss_ms",
                "detached_host_snapshot",
                "fault_kind",
                "heartbeat_missed_after_loss_ms",
                "heartbeat_timeout_ms",
                "interruption_count",
                "interruptions",
                "qdiscs",
                "schema",
            }
            and route_loss.get("schema") == "iotox-ratox-route-loss-v5"
            and route_loss.get("fault_kind") == "netem-total-loss"
            and route_loss.get("controller_kind")
            == "production-cli-reconnect"
            and route_loss.get("heartbeat_timeout_ms") == 3000
            and route_loss.get("detached_host_snapshot") is True
            and route_loss.get("interruption_count") == 2
            and isinstance(route_loss.get("interruptions"), list)
            and len(route_loss["interruptions"]) == 2,
            "repeated production-CLI Ratox route-loss summary is invalid",
        )
        expected_seeds = {
            1: {"vm-iotoxc": 20_260_829, "vm-iotoxd": 20_260_830},
            2: {"vm-iotoxc": 20_261_829, "vm-iotoxd": 20_261_830},
        }
        for ordinal, interruption in enumerate(
            route_loss["interruptions"], start=1
        ):
            require(
                isinstance(interruption, dict)
                and set(interruption)
                == {
                    "active_wall_ms",
                    "controller_offline_after_loss_ms",
                    "heartbeat_missed_after_loss_ms",
                    "ordinal",
                    "qdiscs",
                }
                and interruption["ordinal"] == ordinal
                and isinstance(interruption["heartbeat_missed_after_loss_ms"], int)
                and 2_500
                <= interruption["heartbeat_missed_after_loss_ms"]
                < 30_000
                and isinstance(
                    interruption["controller_offline_after_loss_ms"], int
                )
                and interruption["heartbeat_missed_after_loss_ms"]
                < interruption["controller_offline_after_loss_ms"]
                < 240_000
                and isinstance(interruption["active_wall_ms"], int)
                and interruption["controller_offline_after_loss_ms"]
                <= interruption["active_wall_ms"]
                < 300_000,
                f"production-CLI interruption {ordinal} timing is invalid",
            )
            qdiscs = interruption["qdiscs"]
            require(
                isinstance(qdiscs, list)
                and len(qdiscs) == 2
                and {entry.get("tap") for entry in qdiscs}
                == {"vm-iotoxc", "vm-iotoxd"},
                f"production-CLI interruption {ordinal} TAP set drifted",
            )
            for entry in qdiscs:
                tap = entry.get("tap")
                require(
                    entry.get("kind") == "netem"
                    and entry.get("loss_percent") == 100
                    and entry.get("seed") == expected_seeds[ordinal][tap]
                    and isinstance(entry.get("drops"), int)
                    and entry["drops"] > 0,
                    f"production-CLI interruption {ordinal} was not exercised on {tap}",
                )
        require(
            route_loss["qdiscs"] == route_loss["interruptions"][0]["qdiscs"]
            and route_loss["heartbeat_missed_after_loss_ms"]
            == route_loss["interruptions"][0]["heartbeat_missed_after_loss_ms"]
            and route_loss["controller_offline_after_loss_ms"]
            == route_loss["interruptions"][0]["controller_offline_after_loss_ms"]
            and route_loss["active_wall_ms"]
            == route_loss["interruptions"][0]["active_wall_ms"],
            "repeated route-loss compatibility fields disagree",
        )
        route_loss_path = proof_root / "ratox-route-loss.json"
        require(
            route_loss_path.is_file()
            and not route_loss_path.is_symlink()
            and load(route_loss_path) == route_loss,
            "repeated production-CLI route-loss file disagrees with the manifest",
        )
    elif ratox_cli_reconnect_scenario:
        require(
            set(route_loss)
            == {
                "active_wall_ms",
                "controller_kind",
                "controller_offline_after_loss_ms",
                "detached_host_snapshot",
                "fault_kind",
                "heartbeat_missed_after_loss_ms",
                "heartbeat_timeout_ms",
                "qdiscs",
                "schema",
            }
            and route_loss.get("schema") == "iotox-ratox-route-loss-v4"
            and route_loss.get("fault_kind") == "netem-total-loss"
            and route_loss.get("controller_kind")
            == "production-cli-reconnect"
            and route_loss.get("heartbeat_timeout_ms") == 3000
            and route_loss.get("detached_host_snapshot") is True
            and isinstance(
                route_loss.get("heartbeat_missed_after_loss_ms"), int
            )
            and 2_500 <= route_loss["heartbeat_missed_after_loss_ms"] < 30_000
            and isinstance(
                route_loss.get("controller_offline_after_loss_ms"), int
            )
            and route_loss["heartbeat_missed_after_loss_ms"]
            < route_loss["controller_offline_after_loss_ms"]
            < 240_000
            and isinstance(route_loss.get("active_wall_ms"), int)
            and route_loss["controller_offline_after_loss_ms"]
            <= route_loss["active_wall_ms"]
            < 300_000,
            "production-CLI Ratox route-loss summary is invalid",
        )
        route_loss_path = proof_root / "ratox-route-loss.json"
        require(
            route_loss_path.is_file()
            and not route_loss_path.is_symlink()
            and load(route_loss_path) == route_loss,
            "production-CLI route-loss file disagrees with the manifest",
        )
        loss_qdiscs = route_loss["qdiscs"]
        require(
            isinstance(loss_qdiscs, list) and len(loss_qdiscs) == 2,
            "production-CLI route-loss qdisc evidence is incomplete",
        )
        require(
            {entry.get("tap") for entry in loss_qdiscs}
            == {"vm-iotoxc", "vm-iotoxd"},
            "production-CLI route-loss TAP set drifted",
        )
        expected_seeds = {"vm-iotoxc": 20_260_829, "vm-iotoxd": 20_260_830}
        for entry in loss_qdiscs:
            tap = entry.get("tap")
            require(
                entry.get("kind") == "netem"
                and entry.get("loss_percent") == 100
                and entry.get("seed") == expected_seeds[tap]
                and isinstance(entry.get("drops"), int)
                and entry["drops"] > 0,
                f"production-CLI route loss was not exercised on {tap}",
            )
    elif ratox_route_loss_scenario:
        require(
            set(route_loss)
            == {
                "active_wall_ms",
                "controller_offline_after_loss_ms",
                "detached_host_snapshot",
                "heartbeat_missed_after_loss_ms",
                "heartbeat_timeout_ms",
                "loss_percent",
                "qdiscs",
                "schema",
            },
            "Ratox route-loss summary schema drifted",
        )
        require(
            route_loss["schema"] == "iotox-ratox-route-loss-v1"
            and route_loss["loss_percent"] == 100
            and route_loss["heartbeat_timeout_ms"] == 2000
            and route_loss["detached_host_snapshot"] is True
            and isinstance(route_loss["heartbeat_missed_after_loss_ms"], int)
            and 1_800 <= route_loss["heartbeat_missed_after_loss_ms"] < 30_000
            and isinstance(route_loss["controller_offline_after_loss_ms"], int)
            and route_loss["controller_offline_after_loss_ms"]
            > route_loss["heartbeat_missed_after_loss_ms"]
            and route_loss["controller_offline_after_loss_ms"] < 240_000
            and isinstance(route_loss["active_wall_ms"], int)
            and route_loss["active_wall_ms"]
            >= route_loss["controller_offline_after_loss_ms"]
            and route_loss["active_wall_ms"] < 300_000,
            "Ratox route-loss timing or policy drifted",
        )
        route_loss_path = proof_root / "ratox-route-loss.json"
        require(route_loss_path.is_file() and not route_loss_path.is_symlink(),
                "Ratox route-loss evidence file is absent")
        require(load(route_loss_path) == route_loss,
                "Ratox route-loss file disagrees with the manifest")
        loss_qdiscs = route_loss["qdiscs"]
        require(isinstance(loss_qdiscs, list) and len(loss_qdiscs) == 2,
                "Ratox route-loss qdisc evidence is incomplete")
        require({entry.get("tap") for entry in loss_qdiscs}
                == {"vm-iotoxc", "vm-iotoxd"},
                "Ratox route-loss TAP set drifted")
        expected_seeds = {"vm-iotoxc": 20_260_829, "vm-iotoxd": 20_260_830}
        for entry in loss_qdiscs:
            tap = entry.get("tap")
            require(
                set(entry)
                == {
                    "backlog", "bytes", "drops", "kind", "loss_percent",
                    "overlimits", "packets", "qlen", "requeues", "seed", "tap",
                }
                and entry["kind"] == "netem"
                and entry["loss_percent"] == 100
                and entry["seed"] == expected_seeds[tap],
                f"Ratox route-loss qdisc changed on {tap}",
            )
            for counter in (
                "bytes", "packets", "drops", "overlimits", "requeues",
                "backlog", "qlen",
            ):
                require(isinstance(entry[counter], int) and entry[counter] >= 0,
                        f"Ratox route-loss {counter} is invalid on {tap}")
            # tc reports packets/bytes after netem disposition. Under 100%
            # loss those sent counters can correctly remain zero; the drop
            # counter is the attempted-traffic witness.
            require(entry["drops"] > 0,
                    f"Ratox route loss was not exercised on {tap}")
    else:
        require(route_loss == {}, "non-route-loss scenario claims Ratox total loss")
        require(not (proof_root / "ratox-route-loss.json").exists(),
                "non-route-loss proof contains Ratox total-loss evidence")
    require(
        guest_restart_count == (1 if scenario in GUEST_RESTART_SCENARIOS else 0),
        "device guest restart count mismatch",
    )
    require(
        manifest.get("sync_file_convergence", False)
        is (scenario in SYNC_SCENARIOS and not sync_cancellation),
        "synchronization convergence classification mismatch",
    )
    require(
        manifest.get("sync_cancellation", False) is sync_cancellation,
        "synchronization cancellation classification mismatch",
    )
    require(
        manifest.get("mutable_profile_convergence", False) is mutable_scenario
        and manifest.get("mutable_authorized_role_count", 0)
        == (2 if mutable_scenario else 0)
        and manifest.get("mutable_converged_role_count", 0)
        == (2 if mutable_scenario else 0),
        "mutable profile-state classification mismatch",
    )
    bidirectional_sync = scenario in BIDIRECTIONAL_SYNC_SCENARIOS
    require(
        manifest.get("bidirectional_sync_convergence", False)
        is bidirectional_sync
        and manifest.get("bidirectional_sync_converged_role_count", 0)
        == (2 if bidirectional_sync else 0),
        "bidirectional synchronization classification mismatch",
    )
    automation_sync = scenario in AUTOMATION_SYNC_SCENARIOS
    require(
        manifest.get("automation_sync_convergence", False)
        is automation_sync
        and manifest.get("automation_sync_converged_role_count", 0)
        == (2 if automation_sync else 0),
        "unattended synchronization classification mismatch",
    )
    if scenario in SYNC_SCENARIOS:
        expected_sync_generation = (
            3
            if scenario == "sync-tree-adversity"
            else 2 if scenario in SYNC_RANGE_SCENARIOS else 1
        )
        require(
            manifest.get("sync_generation") == expected_sync_generation,
            "sync generation mismatch",
        )
        for field in (
            "sync_artifact_sha256",
            "sync_manifest_sha256",
            "sync_head_record",
        ):
            require(
                SHA256.fullmatch(str(manifest.get(field, ""))) is not None,
                f"manifest {field} is invalid",
            )
        if scenario in CONTENT_SCENARIOS:
            content_path = (
                proof_root
                / "client/live/workspace-export/iotox-rendezvous/"
                "client.sync-complete"
            )
            require(
                content_path.is_file() and not content_path.is_symlink(),
                "content-v2 completion evidence is absent",
            )
            content_lines = content_path.read_text(encoding="ascii").splitlines()
            expected_content_fields = content_completion_fields(
                scenario,
                atomic_multi_source,
            )
            require(
                len(content_lines) == len(expected_content_fields)
                and all("=" in line for line in content_lines),
                "content-v2 completion evidence is malformed",
            )
            content_fields = dict(line.split("=", 1) for line in content_lines)
            require(
                list(content_fields) == expected_content_fields
                and content_fields["convergence"] == "1"
                and content_fields["activation"] == "1"
                and content_fields["generation"]
                == str(manifest.get("sync_generation"))
                and content_fields["head-record"]
                == manifest.get("sync_head_record")
                and content_fields["artifact-sha256"]
                == manifest.get("sync_artifact_sha256")
                and content_fields["manifest-sha256"]
                == manifest.get("sync_manifest_sha256")
                and content_fields["artifact-bytes"]
                == (
                    "8388608"
                    if scenario
                    in {
                        *CONTENT_LANE_SCIENCE_SCENARIOS,
                        *CONTENT_RESTART_SCENARIOS,
                    }
                    else "4194304"
                )
                and content_fields["manifest-bytes"] == "272"
                and content_fields["content-format"] == "paged"
                and content_fields["content-chunks"]
                == (
                    "24"
                    if scenario
                    in {
                        *CONTENT_LANE_SCIENCE_SCENARIOS,
                        *CONTENT_RESTART_SCENARIOS,
                    }
                    else "4"
                )
                and content_fields["content-pages"] == "1"
                and content_fields["content-objects"]
                == (
                    "26"
                    if scenario
                    in {
                        *CONTENT_LANE_SCIENCE_SCENARIOS,
                        *CONTENT_RESTART_SCENARIOS,
                    }
                    else "4"
                ),
                "content-v2 completion shape or manifest binding is invalid",
            )
            if scenario in CONTENT_RESTART_SCENARIOS:
                require(
                    content_fields["restart"] == "1",
                    "content-v2 restart completion evidence is invalid",
                )
                content_cap = CONTENT_RESTART_SCENARIOS[scenario]
                restart_root = (
                    "client/live/workspace-export/iotox-rendezvous/"
                )
                interruption_path = confined(
                    proof_root,
                    restart_root + "client.sync-interruption-ready",
                    restart_root + "client.sync-interruption-ready",
                )
                crash_path = confined(
                    proof_root,
                    restart_root + "client.sync-crash-state",
                    restart_root + "client.sync-crash-state",
                )
                interruption = interruption_path.read_text(encoding="ascii")
                crash = crash_path.read_text(encoding="ascii")
                content_restart_interruption_fields = dict(
                    line.split("=", 1) for line in interruption.splitlines()
                )
                content_restart_crash_fields = dict(
                    line.split("=", 1) for line in crash.splitlines()
                )
                partial_pattern = "2" if content_cap == 2 else "[2-4]"
                require(
                    re.fullmatch(
                        r"sync-interruption-ready=1\n"
                        r"staging-bytes=[1-9][0-9]*\n"
                        rf"content-restart-cap={content_cap}\n"
                        rf"content-restart-live-lanes={content_cap}\n"
                        rf"content-restart-staging-temporaries={partial_pattern}\n"
                        r"content-restart-lane-set-sha256=[0-9a-f]{64}\n"
                        r"content-restart-first-job=[1-9][0-9]*\n",
                        interruption,
                    )
                    is not None
                    and re.fullmatch(
                        r"schema=iotox-sync-content-crash-state-v1\n"
                        r"stop-status=137\n"
                        rf"transport-temporaries={partial_pattern}\n"
                        rf"content-restart-cap={content_cap}\n"
                        rf"content-live-lanes={content_cap}\n"
                        r"content-transport-bytes=[1-9][0-9]*\n"
                        r"content-canonical-partials=0\n"
                        r"content-committed-objects=[2-9][0-9]*\n"
                        r"content-committed-bytes=[1-9][0-9]*\n"
                        r"content-inventory-sha256=[0-9a-f]{64}\n"
                        r"attempt-journal-present=1\n"
                        r"accepted-head-present=0\n"
                        r"activation-present=0\n",
                        crash,
                    )
                    is not None,
                    "content-v2 restart checkpoints are invalid",
                )
            if scenario == "sync-content-ratox-post-bulk-admission":
                require(
                    content_fields["content-ratox-post-bulk"] == "1"
                    and content_fields["content-ratox-post-bulk-cap"] == "8"
                    and content_fields["content-ratox-post-bulk-samples"] == "40"
                    and int(content_fields["content-ratox-post-bulk-origin-us"]) > 0
                    and 0
                    <= int(
                        content_fields[
                            "content-ratox-post-bulk-origin-to-open-sent-us"
                        ]
                    )
                    <= 1_000_000
                    and 0
                    < int(
                        content_fields[
                            "content-ratox-post-bulk-origin-to-opened-us"
                        ]
                    )
                    <= 6_000_000
                    and 0
                    < int(
                        content_fields[
                            "content-ratox-post-bulk-open-round-trip-us"
                        ]
                    )
                    <= 5_000_000
                    and int(
                        content_fields["content-ratox-post-bulk-online-epoch"]
                    )
                    > 0
                    and all(
                        SHA256.fullmatch(content_fields[field]) is not None
                        for field in (
                            "content-ratox-post-bulk-readiness-sha256",
                            "content-ratox-post-bulk-capture-sha256",
                            "content-ratox-post-bulk-admission-sha256",
                        )
                    ),
                    "fresh post-bulk Ratox completion evidence is invalid",
                )
            if scenario in CONTENT_MULTI_SOURCE_SCENARIOS:
                availability_requests = int(
                    content_fields["content-availability-requests"]
                )
                expected_relay_count = 2 if route == "forced-tcp" else 0
                relay_count = manifest.get(
                    "multi_source_tcp_relay_count",
                    0,
                )
                secondary_bootstrap_digest = str(
                    manifest.get(
                        "multi_source_secondary_bootstrap_key_sha256",
                        "",
                    )
                )
                require(
                    (
                        content_fields.get("content-atomic-pull") == "1"
                        if atomic_multi_source
                        else "content-atomic-pull" not in content_fields
                    )
                    and int(content_fields["content-primary-chunks"]) > 0
                    and int(content_fields["content-secondary-chunks"]) > 0
                    and int(content_fields["content-primary-chunks"])
                    + int(content_fields["content-secondary-chunks"])
                    == int(content_fields["content-chunks"])
                    and content_fields["content-source-count"] == "2"
                    and availability_requests >= 2
                    and int(content_fields["content-availability-results"])
                    == availability_requests
                    and manifest.get("multi_source_count") == 2
                    and (
                        manifest.get("multi_source_atomic_pull_role_count") == 2
                        if atomic_multi_source
                        else "multi_source_atomic_pull_role_count" not in manifest
                    )
                    and manifest.get("multi_source_availability_requests")
                    == availability_requests
                    and manifest.get("multi_source_availability_results")
                    == availability_requests
                    and manifest.get("multi_source_primary_objects", 0) > 1
                    and manifest.get("multi_source_secondary_objects", 0) > 0
                    and SHA256.fullmatch(
                        str(
                            manifest.get(
                                "multi_source_secondary_key_sha256", ""
                            )
                        )
                    )
                    is not None
                    and SHA256.fullmatch(
                        str(
                            manifest.get(
                                "multi_source_secondary_principal_sha256", ""
                            )
                        )
                    )
                    is not None
                    and relay_count == expected_relay_count
                    and (
                        SHA256.fullmatch(secondary_bootstrap_digest)
                        is not None
                        if route == "forced-tcp"
                        else secondary_bootstrap_digest == ""
                    ),
                    "multi-source content evidence is incomplete",
                )
                if scenario in {
                    "sync-content-multi-route-actual-tor",
                    "sync-content-multi-route-actual-tor-loss",
                }:
                    carrier_digest = str(
                        manifest.get(
                            "multi_source_auxiliary_carriers_sha256", ""
                        )
                    )
                    require(
                        manifest.get(
                            "multi_source_auxiliary_carrier_count"
                        )
                        == 2
                        and SHA256.fullmatch(carrier_digest) is not None,
                        "routed multi-source carrier set is absent",
                    )
                    carrier_record_path = (
                        proof_root
                        / "client/live/workspace-export/iotox-rendezvous/"
                        "client.content-multi-route"
                    )
                    require(
                        carrier_record_path.is_file()
                        and not carrier_record_path.is_symlink(),
                        "routed multi-source carrier record is absent",
                    )
                    carrier_text = carrier_record_path.read_text(
                        encoding="utf-8"
                    )
                    carrier_match = re.fullmatch(
                        r"schema=iotox-content-multi-route-v1\n"
                        r"job=(?P<job>[1-9][0-9]*)\n"
                        r"source-count=2\n"
                        r"primary-principal=(?P<primary_principal>[0-9a-f]{64})\n"
                        r"primary-route=(?P<primary_route>[0-9A-F]{64})\n"
                        r"(?:primary-worker=(?P<primary_worker>[1-9][0-9]*)\n)?"
                        r"secondary-principal=(?P<secondary_principal>[0-9a-f]{64})\n"
                        r"secondary-route=(?P<secondary_route>[0-9A-F]{64})\n"
                        r"(?:secondary-worker=(?P<secondary_worker>[1-9][0-9]*)\n)?"
                        r"carrier-set-sha256=(?P<carrier_digest>[0-9a-f]{64})\n",
                        carrier_text,
                    )
                    require(
                        carrier_match is not None,
                        "routed multi-source carrier record is malformed",
                    )
                    assert carrier_match is not None
                    route_loss = (
                        scenario
                        == "sync-content-multi-route-actual-tor-loss"
                    )
                    require(
                        (carrier_match.group("primary_worker") is not None)
                        is route_loss
                        and (
                            carrier_match.group("secondary_worker") is not None
                        )
                        is route_loss,
                        "routed multi-source worker checkpoint shape is invalid",
                    )
                    primary_route = carrier_match.group("primary_route")
                    secondary_route = carrier_match.group("secondary_route")
                    calculated_carriers = hashlib.sha256(
                        "".join(
                            f"{route_key}\n"
                            for route_key in sorted(
                                (primary_route, secondary_route)
                            )
                        ).encode("ascii")
                    ).hexdigest()
                    require(
                        primary_route != secondary_route
                        and carrier_match.group("carrier_digest")
                        == carrier_digest
                        and calculated_carriers == carrier_digest
                        and hashlib.sha256(
                            primary_route.encode("ascii")
                        ).hexdigest()
                        == manifest.get(
                            "actual_tor_payload_carrier_sha256"
                        ),
                        "routed multi-source carrier commitments disagree",
                    )
                if route == "forced-tcp":
                    secondary_public_id = (
                        proof_root
                        / "host-bootstrap-secondary/PUBLIC_ID.txt"
                    )
                    require(
                        secondary_public_id.is_file()
                        and not secondary_public_id.is_symlink(),
                        "secondary bootstrap public identity is absent",
                    )
                if scenario == "sync-content-multi-source-loss":
                    first_job = int(content_fields["content-loss-first-job"])
                    replacement_job = int(
                        content_fields["content-loss-replacement-job"]
                    )
                    initial_epoch = int(
                        content_fields["content-loss-initial-epoch"]
                    )
                    recovered_epoch = int(
                        content_fields["content-loss-recovered-epoch"]
                    )
                    require(
                        content_fields["content-loss-observed"] == "1"
                        and content_fields["content-loss-recovery"] == "1"
                        and first_job > 0
                        and replacement_job > 0
                        and first_job != replacement_job
                        and int(
                            content_fields[
                                "content-loss-committed-objects"
                            ]
                        )
                        > 0
                        and int(
                            content_fields["content-loss-fetched-bytes"]
                        )
                        > 0
                        and initial_epoch > 0
                        and recovered_epoch > initial_epoch
                        and content_fields["content-loss-staging-clean"]
                        == "1"
                        and content_fields["content-loss-head-fenced"] == "1"
                        and content_fields[
                            "content-loss-activation-fenced"
                        ]
                        == "1",
                        "selected-source loss completion evidence is invalid",
                    )
                    durable_replica = manifest.get(
                        "multi_source_loss_durable_replica_cold_start", False
                    )
                    constructed_reinjection = manifest.get(
                        "multi_source_loss_constructed_replica_head_reinjected"
                    )
                    require(
                        route == "direct-udp"
                        and manifest.get(
                            "multi_source_loss_observed_role_count"
                        )
                        == 2
                        and manifest.get(
                            "multi_source_loss_recovery_role_count"
                        )
                        == 2
                        and manifest.get(
                            "multi_source_loss_first_job_id"
                        )
                        == first_job
                        and manifest.get(
                            "multi_source_loss_replacement_job_id"
                        )
                        == replacement_job
                        and manifest.get(
                            "multi_source_loss_committed_objects"
                        )
                        == int(
                            content_fields[
                                "content-loss-committed-objects"
                            ]
                        )
                        and manifest.get("multi_source_loss_fetched_bytes")
                        == int(
                            content_fields["content-loss-fetched-bytes"]
                        )
                        and manifest.get("multi_source_loss_initial_epoch")
                        == initial_epoch
                        and manifest.get(
                            "multi_source_loss_recovered_epoch"
                        )
                        == recovered_epoch
                        and manifest.get("multi_source_loss_restart_count")
                        == 1
                        and manifest.get(
                            "multi_source_loss_secondary_requests_before_stop"
                        )
                        > 0
                        and manifest.get(
                            "multi_source_loss_staging_clean_role_count"
                        )
                        == 2
                        and manifest.get(
                            "multi_source_loss_head_fenced_role_count"
                        )
                        == 2
                        and manifest.get(
                            "multi_source_loss_activation_fenced_role_count"
                        )
                        == 2
                        and (
                            (
                                durable_replica is True
                                and constructed_reinjection is False
                            )
                            or (
                                durable_replica is False
                                and constructed_reinjection is True
                            )
                        ),
                        "selected-source loss manifest binding is invalid",
                    )
                    checkpoint_root = (
                        proof_root
                        / "client/live/workspace-export/iotox-rendezvous"
                    )
                    device_checkpoint_root = (
                        proof_root
                        / "device/live/workspace-export/iotox-rendezvous"
                    )
                    checkpoint_paths = {
                        "failed": checkpoint_root
                        / "client.multi-source-loss-failed",
                        "client_recovered": checkpoint_root
                        / "client.multi-source-loss-recovered",
                        "ready": device_checkpoint_root
                        / "device.multi-source-loss-ready",
                        "stopped": device_checkpoint_root
                        / "device.multi-source-loss-stopped",
                        "device_recovered": device_checkpoint_root
                        / "device.multi-source-loss-recovered",
                    }
                    replica_imported = (
                        device_checkpoint_root
                        / "device.multi-source-loss-replica-imported"
                    )
                    require(
                        all(
                            path.is_file() and not path.is_symlink()
                            for path in checkpoint_paths.values()
                        ),
                        "selected-source loss exact checkpoints are absent",
                    )
                    failed_match = re.fullmatch(
                        r"schema=iotox-content-multi-source-loss-failed-v1\n"
                        rf"job={first_job}\n"
                        r"committed-objects=([1-9][0-9]*)\n"
                        r"fetched-bytes=([1-9][0-9]*)\n"
                        r"staging-clean=1\n"
                        r"accepted-head=0\n"
                        r"activation=0\n",
                        checkpoint_paths["failed"].read_text(encoding="ascii"),
                    )
                    ready_match = re.fullmatch(
                        r"schema=iotox-content-multi-source-loss-ready-v1\n"
                        r"secondary-object-requests=([1-9][0-9]*)\n",
                        checkpoint_paths["ready"].read_text(encoding="ascii"),
                    )
                    require(
                        failed_match is not None
                        and int(failed_match.group(1))
                        == manifest["multi_source_loss_committed_objects"]
                        and int(failed_match.group(2))
                        == manifest["multi_source_loss_fetched_bytes"]
                        and ready_match is not None
                        and int(ready_match.group(1))
                        == manifest[
                            "multi_source_loss_secondary_requests_before_stop"
                        ]
                        and checkpoint_paths["client_recovered"].read_text(
                            encoding="ascii"
                        )
                        == f"replacement-job={replacement_job}\n"
                        and checkpoint_paths["stopped"].read_text(
                            encoding="ascii"
                        )
                        == "secondary-stopped=1\n"
                        and checkpoint_paths["device_recovered"].read_text(
                            encoding="ascii"
                        )
                        == (
                            "schema=iotox-content-multi-source-loss-recovered-v1\n"
                            "secondary-recovered=1\n"
                            "durable-replica-head-cold-start=1\n"
                            "published-head-absent=1\n"
                            "replica-gc-consistent=1\n"
                            if durable_replica
                            else "schema=iotox-content-multi-source-loss-recovered-v1\n"
                            "secondary-recovered=1\n"
                            "constructed-replica-head-reinjected=1\n"
                        )
                        and (
                            replica_imported.is_file()
                            and not replica_imported.is_symlink()
                            and replica_imported.read_text(encoding="ascii")
                            == "schema=iotox-content-replica-import-v1\n"
                            "namespace=sandwurm-file\n"
                            f"head-record={manifest['sync_head_record']}\n"
                            "authority=availability-only\n"
                            "published-head=0\n"
                            "replica-head=1\n"
                            if durable_replica
                            else not replica_imported.exists()
                        ),
                        "selected-source loss checkpoint binding is invalid",
                    )
                    if route == "forced-tcp":
                        secondary_public_key = secondary_public_id.read_text(
                            encoding="ascii"
                        )
                        require(
                            re.fullmatch(r"[0-9A-F]{64}", secondary_public_key)
                            is not None
                            and hashlib.sha256(
                                secondary_public_key.encode("ascii")
                            ).hexdigest()
                            == secondary_bootstrap_digest,
                            "secondary bootstrap public identity mismatch",
                        )
                if scenario == "sync-content-multi-route-actual-tor-loss":
                    first_job = int(content_fields["content-loss-first-job"])
                    replacement_job = int(
                        content_fields["content-loss-replacement-job"]
                    )
                    initial_epoch = int(
                        content_fields["content-loss-initial-epoch"]
                    )
                    recovered_epoch = int(
                        content_fields["content-loss-recovered-epoch"]
                    )
                    target = content_fields["content-route-loss-target"]
                    fault_worker = int(
                        content_fields["content-route-loss-fault-worker"]
                    )
                    recovered_worker = int(
                        content_fields[
                            "content-route-loss-recovered-worker"
                        ]
                    )
                    position = int(
                        content_fields["content-route-loss-position-bytes"]
                    )
                    primary_epoch = int(
                        content_fields["content-route-loss-primary-epoch"]
                    )
                    secondary_epoch = int(
                        content_fields[
                            "content-route-loss-secondary-epoch"
                        ]
                    )
                    require(
                        content_fields["content-loss-observed"] == "1"
                        and content_fields["content-loss-recovery"] == "1"
                        and content_fields["content-route-loss"] == "1"
                        and first_job > 0
                        and replacement_job > 0
                        and first_job != replacement_job
                        and int(
                            content_fields[
                                "content-loss-committed-objects"
                            ]
                        )
                        > 0
                        and int(
                            content_fields["content-loss-fetched-bytes"]
                        )
                        > 0
                        and initial_epoch > 0
                        and recovered_epoch == initial_epoch
                        and re.fullmatch(r"[0-9A-F]{64}", target) is not None
                        and fault_worker > 0
                        and recovered_worker > 0
                        and fault_worker != recovered_worker
                        and position >= 65_536
                        and content_fields[
                            "content-route-loss-carrier-losses"
                        ]
                        == "1"
                        and content_fields[
                            "content-route-loss-reassignments"
                        ]
                        == "0"
                        and content_fields[
                            "content-route-loss-recoveries"
                        ]
                        == "1"
                        and primary_epoch > 0
                        and secondary_epoch == initial_epoch
                        and content_fields["content-loss-staging-clean"]
                        == "1"
                        and content_fields["content-loss-head-fenced"] == "1"
                        and content_fields[
                            "content-loss-activation-fenced"
                        ]
                        == "1",
                        "exact Tor content-worker loss completion is invalid",
                    )
                    require(
                        manifest.get("multi_source_loss_observed_role_count")
                        == 2
                        and manifest.get(
                            "multi_source_loss_recovery_role_count"
                        )
                        == 2
                        and manifest.get("multi_source_loss_first_job_id")
                        == first_job
                        and manifest.get(
                            "multi_source_loss_replacement_job_id"
                        )
                        == replacement_job
                        and manifest.get("multi_source_loss_restart_count")
                        == 1
                        and manifest.get(
                            "multi_source_loss_staging_clean_role_count"
                        )
                        == 2
                        and manifest.get(
                            "multi_source_loss_head_fenced_role_count"
                        )
                        == 2
                        and manifest.get(
                            "multi_source_loss_activation_fenced_role_count"
                        )
                        == 2
                        and manifest.get(
                            "multi_source_route_loss_observed_role_count"
                        )
                        == 2
                        and manifest.get("multi_source_route_loss_target")
                        == target
                        and manifest.get(
                            "multi_source_route_loss_fault_worker"
                        )
                        == fault_worker
                        and manifest.get(
                            "multi_source_route_loss_recovered_worker"
                        )
                        == recovered_worker
                        and manifest.get(
                            "multi_source_route_loss_position_bytes"
                        )
                        == position
                        and manifest.get(
                            "multi_source_route_loss_carrier_losses"
                        )
                        == 1
                        and manifest.get(
                            "multi_source_route_loss_reassignments"
                        )
                        == 0
                        and manifest.get(
                            "multi_source_route_loss_recoveries"
                        )
                        == 1
                        and manifest.get(
                            "multi_source_route_loss_primary_epoch"
                        )
                        == primary_epoch
                        and manifest.get(
                            "multi_source_route_loss_secondary_epoch"
                        )
                        == secondary_epoch,
                        "exact Tor content-worker loss manifest is invalid",
                    )
                    checkpoint_root = (
                        proof_root
                        / "client/live/workspace-export/iotox-rendezvous"
                    )
                    failed = checkpoint_root / "client.multi-source-loss-failed"
                    recovered = (
                        checkpoint_root / "client.multi-source-loss-recovered"
                    )
                    require(
                        failed.is_file()
                        and not failed.is_symlink()
                        and recovered.is_file()
                        and not recovered.is_symlink(),
                        "exact Tor content-worker loss checkpoints are absent",
                    )
                    failed_match = re.fullmatch(
                        r"schema=iotox-content-multi-source-loss-failed-v1\n"
                        rf"job={first_job}\n"
                        r"committed-objects=([1-9][0-9]*)\n"
                        r"fetched-bytes=([1-9][0-9]*)\n"
                        r"staging-clean=1\n"
                        r"accepted-head=0\n"
                        r"activation=0\n"
                        r"route-loss=1\n"
                        rf"route={target}\n"
                        rf"worker={fault_worker}\n"
                        rf"position-bytes={position}\n"
                        r"carrier-losses=1\n"
                        r"reassignments=0\n",
                        failed.read_text(encoding="ascii"),
                    )
                    require(
                        failed_match is not None
                        and int(failed_match.group(1))
                        == manifest["multi_source_loss_committed_objects"]
                        and int(failed_match.group(2))
                        == manifest["multi_source_loss_fetched_bytes"]
                        and recovered.read_text(encoding="ascii")
                        == f"replacement-job={replacement_job}\n"
                        and carrier_match is not None
                        and int(carrier_match.group("secondary_worker"))
                        == recovered_worker
                        and carrier_match.group("secondary_route") == target,
                        "exact Tor content-worker checkpoints disagree",
                    )
            if scenario == "sync-content-same-source-multi-route-actual-tor":
                path_record = confined(
                    proof_root,
                    SAME_SOURCE_MULTI_ROUTE_CONTENT_PATH,
                    SAME_SOURCE_MULTI_ROUTE_CONTENT_PATH,
                )
                path_match = re.fullmatch(
                    r"schema=iotox-content-same-source-multi-route-v1\n"
                    r"job=(?P<job>[1-9][0-9]*)\n"
                    r"principal-count=1\n"
                    r"carrier-count=2\n"
                    r"principal=(?P<principal>[0-9a-f]{64})\n"
                    r"path-a-source=(?P<a_source>[1-9][0-9]*)\n"
                    r"path-a-principal=(?P<a_principal>[0-9a-f]{64})\n"
                    r"path-a-authority-route=(?P<a_authority_route>[0-9A-F]{64})\n"
                    r"path-a-authority-friend=(?P<a_authority_friend>[0-9]+)\n"
                    r"path-a-authority-epoch=(?P<a_authority_epoch>[1-9][0-9]*)\n"
                    r"path-a-route=(?P<a_route>[0-9A-F]{64})\n"
                    r"path-a-worker=(?P<a_worker>[1-9][0-9]*)\n"
                    r"path-a-carrier-friend=(?P<a_carrier_friend>[0-9]+)\n"
                    r"path-a-committed=(?P<a_committed>[1-9][0-9]*)\n"
                    r"path-a-fetched-bytes=(?P<a_bytes>[1-9][0-9]*)\n"
                    r"path-b-source=(?P<b_source>[1-9][0-9]*)\n"
                    r"path-b-principal=(?P<b_principal>[0-9a-f]{64})\n"
                    r"path-b-authority-route=(?P<b_authority_route>[0-9A-F]{64})\n"
                    r"path-b-authority-friend=(?P<b_authority_friend>[0-9]+)\n"
                    r"path-b-authority-epoch=(?P<b_authority_epoch>[1-9][0-9]*)\n"
                    r"path-b-route=(?P<b_route>[0-9A-F]{64})\n"
                    r"path-b-worker=(?P<b_worker>[1-9][0-9]*)\n"
                    r"path-b-carrier-friend=(?P<b_carrier_friend>[0-9]+)\n"
                    r"path-b-committed=(?P<b_committed>[1-9][0-9]*)\n"
                    r"path-b-fetched-bytes=(?P<b_bytes>[1-9][0-9]*)\n"
                    r"availability-requests=(?P<availability_requests>[2-9][0-9]*)\n"
                    r"availability-results=(?P<availability_results>[2-9][0-9]*)\n"
                    r"carrier-set-sha256=(?P<carrier_digest>[0-9a-f]{64})\n",
                    path_record.read_text(encoding="ascii"),
                )
                require(
                    path_match is not None,
                    "same-source multi-route content record is malformed",
                )
                assert path_match is not None
                a_route = path_match.group("a_route")
                b_route = path_match.group("b_route")
                carrier_digest = hashlib.sha256(
                    "".join(
                        f"{route_key}\n"
                        for route_key in sorted((a_route, b_route))
                    ).encode("ascii")
                ).hexdigest()
                require(
                    path_match.group("principal")
                    == path_match.group("a_principal")
                    == path_match.group("b_principal")
                    and path_match.group("a_authority_route")
                    == path_match.group("b_authority_route")
                    and path_match.group("a_authority_friend")
                    == path_match.group("b_authority_friend")
                    and path_match.group("a_authority_epoch")
                    == path_match.group("b_authority_epoch")
                    and path_match.group("a_source")
                    != path_match.group("b_source")
                    and a_route != b_route
                    and path_match.group("a_worker")
                    != path_match.group("b_worker")
                    and path_match.group("availability_requests")
                    == path_match.group("availability_results")
                    and path_match.group("carrier_digest") == carrier_digest
                    and hashlib.sha256(a_route.encode("ascii")).hexdigest()
                    == manifest.get("actual_tor_payload_carrier_sha256"),
                    "same-source multi-route identity or carrier binding disagrees",
                )
        tree_scenario = scenario in SYNC_TREE_SCENARIOS
        expected_tree_content_bytes = (
            131_157
            if scenario in {
                "sync-tree-route-population",
                "sync-tree-route-population-loss",
                "sync-tree-route-loss-admission",
                "sync-tree-route-startup-admission",
                "sync-tree-route-throughput",
                "sync-tree-route-concurrent-cancel",
                "sync-tree-route-common-link-fairness",
            }
            else 16_777_301
            if scenario == "sync-tree-route-private-actual-tor-loss"
            else 131_157
            if scenario
            in {
                "sync-tree-route-private-actual-i2p-payload",
                "sync-tree-route-private-actual-i2p-loss",
            }
            else 4_194_389 if tree_scenario else 0
        )
        require(
            manifest.get("sync_tree_observed_role_count", 0)
            == (2 if tree_scenario else 0)
            and manifest.get("sync_tree_directories", 0)
            == (3 if tree_scenario else 0)
            and manifest.get("sync_tree_files", 0)
            == (3 if tree_scenario else 0)
            and manifest.get("sync_tree_content_bytes", 0)
            == expected_tree_content_bytes
            and (
                SHA256.fullmatch(
                    str(manifest.get("sync_tree_payload_sha256", ""))
                )
                is not None
                if tree_scenario
                else manifest.get("sync_tree_payload_sha256", "") == ""
            ),
            "deterministic synchronization tree summary is invalid",
        )
        route_loss_scenario = scenario in SYNC_ROUTE_LOSS_SCENARIOS
        repeated_range_loss_count = REPEATED_RANGE_LOSS_COUNTS.get(
            scenario, 0
        )
        repeated_range_loss = repeated_range_loss_count != 0
        late_range_loss = scenario == "sync-file-range-late-route-loss"
        recorded_range_loss_threshold = manifest.get(
            "sync_range_route_loss_threshold_bytes", 0
        )
        recorded_range_loss_rate = manifest.get(
            "sync_range_route_loss_rate_kbit", 0
        )
        require(
            manifest.get(
                "sync_repeated_route_loss_initial_rate_kbit", 0
            )
            == (256 if repeated_range_loss else 0)
            and manifest.get(
                "sync_qualification_deferred_frames", 0
            )
            == 0
            and manifest.get(
                "sync_qualification_deferred_frame_releases", 0
            )
            == (repeated_range_loss_count - 1 if repeated_range_loss else 0),
            "repeated range-loss request-hold summary is invalid",
        )
        require(
            recorded_range_loss_threshold == 983_040
            if late_range_loss
            else recorded_range_loss_threshold in {0, 262_144}
            if scenario in {
                "sync-file-range-route-loss",
                "sync-file-range-repeated-route-loss",
                "sync-file-range-triple-route-loss",
            }
            else recorded_range_loss_threshold == 0,
            "range-loss threshold summary is invalid",
        )
        require(
            recorded_range_loss_rate == 256
            if late_range_loss
            else recorded_range_loss_rate in {0, 256}
            if repeated_range_loss
            else recorded_range_loss_rate == 0,
            "range-loss shaping summary is invalid",
        )
        expected_route_loss_count = (
            repeated_range_loss_count
            if repeated_range_loss
            else int(route_loss_scenario)
        )
        cancel_before_loss = scenario == "sync-tree-route-cancel-loss"
        cancel_loss_race = scenario in SYNC_ROUTE_CANCEL_RACE_SCENARIOS
        race_fault_delay, race_cancel_delay, required_race_outcome = (
            SYNC_ROUTE_CANCEL_RACE_SCENARIOS.get(
                scenario, (0, 0, None)
            )
        )
        route_loss_reassignments = manifest.get(
            "sync_tree_route_loss_reassignments", 0
        )
        route_loss_position = manifest.get(
            "sync_tree_route_loss_position_bytes", 0
        )
        require(
            manifest.get("sync_tree_route_loss_observed", False)
            is route_loss_scenario
            and (
                route_loss_position == 0
                if cancel_before_loss
                else (983_040 if late_range_loss else 65_536)
                <= route_loss_position
                < SYNC_SCENARIOS[scenario]
                if route_loss_scenario
                else route_loss_position == 0
            )
            and manifest.get("sync_tree_route_loss_carrier_losses", 0)
            == expected_route_loss_count
            and (
                route_loss_reassignments in {0, 1}
                if cancel_loss_race
                else route_loss_reassignments
                == (
                    expected_route_loss_count
                    if not cancel_before_loss
                    else 0
                )
            )
            and (
                manifest.get("sync_tree_route_loss_stale_terminals", -1)
                >= (
                    0
                    if cancel_loss_race
                    else expected_route_loss_count
                )
                if route_loss_scenario
                else manifest.get("sync_tree_route_loss_stale_terminals", 0)
                == 0
            )
            and manifest.get("sync_tree_route_loss_recoveries", 0)
            == expected_route_loss_count
            and manifest.get(
                "sync_tree_route_cancel_loss_observed", False
            )
            is cancel_before_loss
            and manifest.get(
                "sync_tree_route_cancel_race_observed", False
            )
            is cancel_loss_race
            and manifest.get(
                "sync_tree_route_cancel_race_outcome", ""
            )
            in (
                {"cancel-first", "loss-first"}
                if cancel_loss_race
                else {""}
            )
            and (
                required_race_outcome is None
                or manifest.get("sync_tree_route_cancel_race_outcome", "")
                == required_race_outcome
            )
            and manifest.get(
                "sync_tree_route_cancel_race_fault_delay_ms", 0
            )
            == race_fault_delay
            and manifest.get(
                "sync_tree_route_cancel_race_cancel_delay_ms", 0
            )
            == race_cancel_delay
            and manifest.get(
                "sync_tree_route_cancel_race_cleanup_retries", 0
            )
            in ({0, 1} if cancel_loss_race else {0})
            and manifest.get("sync_tree_route_ready_role_count", 0)
            == (2 if scenario in MULTI_ROUTE_SYNC_SCENARIOS else 0),
            "deterministic synchronization route-loss summary is invalid",
        )
        signed_route_role_count = manifest.get(
            "signed_route_network_class_role_count"
        )
        require(
            signed_route_role_count is None
            or signed_route_role_count
            == (2 if scenario in MULTI_ROUTE_SYNC_SCENARIOS else 0),
            "signed route network-class summary is invalid",
        )
        verify_route_resume(
            manifest,
            scenario
            in {
                "sync-tree-route-loss",
                "sync-tree-route-private-actual-tor-loss",
                "sync-file-range-route-loss",
                "sync-file-range-late-route-loss",
                "sync-file-range-repeated-route-loss",
                "sync-file-range-triple-route-loss",
            },
            "manifest synchronization",
            repeated_range_loss_count if repeated_range_loss else None,
        )
        startup_order_scenario = scenario == "sync-tree-route-startup-order"
        require(
            manifest.get(
                "sync_tree_route_startup_order_observed_role_count", 0
            )
            == (2 if startup_order_scenario else 0)
            and manifest.get("sync_tree_route_startup_delay_ms", 0)
            == (20_000 if startup_order_scenario else 0)
            and manifest.get("sync_tree_route_startup_restart_count", 0)
            == (2 if startup_order_scenario else 0)
            and manifest.get(
                "sync_tree_route_startup_minimum_stable_samples", 0
            )
            == (10 if startup_order_scenario else 0)
            and (
                0
                < manifest.get(
                    "sync_tree_route_startup_maximum_observation_ms", 0
                )
                < 20_000
                if startup_order_scenario
                else manifest.get(
                    "sync_tree_route_startup_maximum_observation_ms", 0
                )
                == 0
            ),
            "deterministic synchronization route startup-order summary is invalid",
        )
        verify_route_balance_summary(
            manifest,
            scenario == "sync-tree-route-balance",
            "manifest synchronization",
        )
        verify_route_population_summary(
            manifest,
            scenario == "sync-tree-route-population",
            "manifest synchronization",
        )
        verify_route_concurrent_cancel_summary(
            manifest,
            scenario in SYNC_CONCURRENT_CANCEL_SCENARIOS,
            "manifest synchronization",
            SYNC_CONCURRENT_CANCEL_ARTIFACT_BYTES.get(scenario, 262_211),
        )
        verify_route_population_loss_summary(
            manifest,
            scenario in {
                "sync-tree-route-population-loss",
                "sync-tree-route-loss-admission",
            },
            "manifest synchronization",
            scenario == "sync-tree-route-loss-admission",
        )
        verify_route_startup_admission_summary(
            manifest,
            scenario == "sync-tree-route-startup-admission",
            "manifest synchronization",
        )
        verify_route_throughput_summary(
            manifest,
            scenario == "sync-tree-route-throughput",
            "manifest synchronization",
        )
        route_cancel_scenario = scenario in {
            "sync-tree-route-cancel",
            "sync-tree-route-loss-cancel",
            "sync-tree-route-cancel-loss",
            "sync-tree-route-cancel-race",
            "sync-tree-route-cancel-race-loss-first",
        }
        route_loss_cancel_scenario = (
            scenario == "sync-tree-route-loss-cancel"
        )
        route_cancel_race_scenario = (
            scenario in SYNC_ROUTE_CANCEL_RACE_SCENARIOS
        )
        route_cancel_reassignments = manifest.get(
            "sync_tree_route_cancel_reassignments_delta", 0
        )
        require(
            manifest.get("sync_tree_route_cancel_observed_role_count", 0)
            == (2 if route_cancel_scenario else 0)
            and (
                SHA256.fullmatch(
                    str(manifest.get("sync_tree_route_cancel_carrier", "")).lower()
                )
                is not None
                and manifest.get("sync_tree_route_cancel_worker_id", 0) > 0
                and 0 <= manifest.get("sync_tree_route_cancel_tail_ms", -1) <= 5000
                and manifest.get("sync_tree_route_cancel_work_before", 0) > 0
                and manifest.get("sync_tree_route_cancel_work_after", -1) == 0
                and manifest.get(
                    "sync_tree_route_cancel_reassignments_delta", -1
                )
                in ({0, 1} if route_cancel_race_scenario else {0})
                and manifest.get(
                    "sync_tree_route_cancel_adaptive_selections", 0
                )
                == (
                    1 + route_cancel_reassignments
                    if route_cancel_race_scenario
                    else 2 if route_loss_cancel_scenario else 1
                )
                if route_cancel_scenario
                else manifest.get("sync_tree_route_cancel_carrier", "") == ""
                and manifest.get("sync_tree_route_cancel_worker_id", 0) == 0
                and manifest.get("sync_tree_route_cancel_tail_ms", 0) == 0
                and manifest.get("sync_tree_route_cancel_work_before", 0) == 0
                and manifest.get("sync_tree_route_cancel_work_after", 0) == 0
                and manifest.get(
                    "sync_tree_route_cancel_reassignments_delta", 0
                )
                == 0
                and manifest.get(
                    "sync_tree_route_cancel_adaptive_selections", 0
                )
                == 0
            ),
            "deterministic synchronization route-cancellation summary is invalid",
        )
        admission_scenario = scenario == "sync-tree-admission"
        require(
            manifest.get("sync_tree_admission_observed_role_count", 0)
            == (2 if admission_scenario else 0)
            and manifest.get("sync_tree_admission_receive_limit", 0)
            == (1 if admission_scenario else 0)
            and (
                manifest.get("sync_tree_admission_retry_count", 0) > 0
                if admission_scenario
                else manifest.get("sync_tree_admission_retry_count", 0) == 0
            )
            and manifest.get("sync_tree_admission_admitted_offers", 0)
            == (2 if admission_scenario else 0)
            and manifest.get("sync_tree_admission_pending_offers", 0) == 0,
            "synchronization receive-admission summary is invalid",
        )
        adversity_scenario = scenario == "sync-tree-adversity"
        require(
            manifest.get("sync_tree_rollback_refused_role_count", 0)
            == (2 if adversity_scenario else 0)
            and manifest.get("sync_tree_fork_refused_role_count", 0)
            == (2 if adversity_scenario else 0)
            and manifest.get("sync_tree_enospc_observed_role_count", 0)
            == (2 if adversity_scenario else 0)
            and manifest.get("sync_tree_enospc_retry_observed_role_count", 0)
            == (2 if adversity_scenario else 0)
            and manifest.get("sync_tree_publisher_restart_count", 0)
            == (4 if adversity_scenario else 0)
            and (
                manifest.get("sync_tree_enospc_reserved_bytes", 0)
                > SYNC_SCENARIOS[scenario]
                if adversity_scenario
                else manifest.get("sync_tree_enospc_reserved_bytes", 0) == 0
            )
            and (
                0
                <= manifest.get("sync_tree_enospc_failure_free_bytes", -1)
                < SYNC_SCENARIOS[scenario]
                if adversity_scenario
                else manifest.get("sync_tree_enospc_failure_free_bytes", 0) == 0
            ),
            "deterministic synchronization tree adversity summary is invalid",
        )
        pressure_scenario = scenario == "sync-tree-pressure"
        pressure_a = manifest.get("sync_tree_pressure_a_head_record", "")
        pressure_b = manifest.get("sync_tree_pressure_b_head_record", "")
        require(
            manifest.get("sync_tree_queue_saturation_observed_role_count", 0)
            == (2 if pressure_scenario else 0)
            and manifest.get("sync_tree_queue_retry_observed_role_count", 0)
            == (2 if pressure_scenario else 0)
            and manifest.get("sync_tree_worker_queue_bound", 0)
            == (1 if pressure_scenario else 0)
            and manifest.get("sync_tree_worker_rejected_delta", 0)
            == (1 if pressure_scenario else 0)
            and (
                SHA256.fullmatch(str(pressure_a)) is not None
                and SHA256.fullmatch(str(pressure_b)) is not None
                and pressure_a != pressure_b
                if pressure_scenario
                else pressure_a == "" and pressure_b == ""
            ),
            "deterministic synchronization tree worker-pressure summary is invalid",
        )
        quota_scenario = scenario in SYNC_TREE_QUOTA_SCENARIOS
        object_quota_scenario = scenario == "sync-tree-object-quota"
        quota_kind = manifest.get(
            "sync_tree_quota_kind",
            "bytes" if scenario == "sync-tree-quota" else "",
        )
        quota_maximum_objects = manifest.get(
            "sync_tree_quota_maximum_objects",
            32 if scenario == "sync-tree-quota" else 0,
        )
        quota_inventory_objects = manifest.get(
            "sync_tree_quota_inventory_objects",
            2 if scenario == "sync-tree-quota" else 0,
        )
        quota_head = manifest.get("sync_tree_quota_candidate_head_record", "")
        quota_artifact = manifest.get(
            "sync_tree_quota_candidate_artifact_sha256", ""
        )
        quota_manifest = manifest.get(
            "sync_tree_quota_candidate_manifest_sha256", ""
        )
        require(
            manifest.get("sync_tree_quota_observed_role_count", 0)
            == (2 if quota_scenario else 0)
            and quota_kind
            == (
                "objects"
                if object_quota_scenario
                else "bytes" if quota_scenario else ""
            )
            and manifest.get("sync_tree_quota_store_bytes", 0)
            == (
                33_554_432
                if object_quota_scenario
                else 5_242_880 if quota_scenario else 0
            )
            and manifest.get("sync_tree_quota_inventory_bytes", 0)
            == (
                4_981_173
                if object_quota_scenario
                else 4_981_169 if quota_scenario else 0
            )
            and quota_maximum_objects
            == (6 if object_quota_scenario else 32 if quota_scenario else 0)
            and quota_inventory_objects
            == (6 if object_quota_scenario else 2 if quota_scenario else 0)
            and (
                manifest["sync_tree_quota_inventory_bytes"]
                < manifest["sync_tree_quota_store_bytes"]
                and (
                    quota_inventory_objects == quota_maximum_objects
                    and manifest["sync_tree_quota_inventory_bytes"] * 2
                    <= manifest["sync_tree_quota_store_bytes"]
                    if object_quota_scenario
                    else 4_194_601
                    > manifest["sync_tree_quota_store_bytes"]
                    - manifest["sync_tree_quota_inventory_bytes"]
                    and 786_568
                    > manifest["sync_tree_quota_store_bytes"]
                    - manifest["sync_tree_quota_inventory_bytes"]
                )
                and SHA256.fullmatch(str(quota_head)) is not None
                and SHA256.fullmatch(str(quota_artifact)) is not None
                and SHA256.fullmatch(str(quota_manifest)) is not None
                and quota_head != manifest["sync_head_record"]
                and quota_artifact != manifest["sync_artifact_sha256"]
                and quota_manifest != manifest["sync_manifest_sha256"]
                if quota_scenario
                else quota_head == ""
                and quota_artifact == ""
                and quota_manifest == ""
            ),
            "deterministic synchronization tree quota summary is invalid",
        )
        read_only_scenario = scenario == "sync-tree-read-only"
        read_only_head = manifest.get("sync_tree_read_only_head_record", "")
        read_only_artifact = manifest.get(
            "sync_tree_read_only_artifact_sha256", ""
        )
        read_only_manifest = manifest.get(
            "sync_tree_read_only_manifest_sha256", ""
        )
        require(
            manifest.get("sync_tree_read_only_observed_role_count", 0)
            == (2 if read_only_scenario else 0)
            and manifest.get(
                "sync_tree_read_only_pull_refused_role_count", 0
            )
            == (2 if read_only_scenario else 0)
            and manifest.get(
                "sync_tree_read_only_activation_refused_role_count", 0
            )
            == (2 if read_only_scenario else 0)
            and manifest.get(
                "sync_tree_read_only_retry_observed_role_count", 0
            )
            == (2 if read_only_scenario else 0)
            and (
                SHA256.fullmatch(str(read_only_head)) is not None
                and SHA256.fullmatch(str(read_only_artifact)) is not None
                and SHA256.fullmatch(str(read_only_manifest)) is not None
                and read_only_head != manifest["sync_head_record"]
                and read_only_artifact != manifest["sync_artifact_sha256"]
                and read_only_manifest != manifest["sync_manifest_sha256"]
                if read_only_scenario
                else read_only_head == ""
                and read_only_artifact == ""
                and read_only_manifest == ""
            ),
            "deterministic synchronization tree read-only summary is invalid",
        )
        memory_scenario = scenario == "sync-tree-memory"
        memory_head = manifest.get("sync_tree_memory_head_record", "")
        memory_artifact = manifest.get("sync_tree_memory_artifact_sha256", "")
        memory_manifest = manifest.get("sync_tree_memory_manifest_sha256", "")
        memory_values = [
            manifest.get("sync_tree_memory_ceiling_kib", 0),
            manifest.get("sync_tree_memory_entries", 0),
            manifest.get("sync_tree_memory_artifact_bytes", 0),
            manifest.get("sync_tree_memory_publisher_baseline_hwm_kib", 0),
            manifest.get("sync_tree_memory_publisher_post_publish_hwm_kib", 0),
            manifest.get("sync_tree_memory_publisher_peak_hwm_kib", 0),
            manifest.get("sync_tree_memory_publisher_delta_hwm_kib", 0),
            manifest.get("sync_tree_memory_subscriber_baseline_hwm_kib", 0),
            manifest.get("sync_tree_memory_subscriber_post_pull_hwm_kib", 0),
            manifest.get("sync_tree_memory_subscriber_peak_hwm_kib", 0),
            manifest.get("sync_tree_memory_subscriber_delta_hwm_kib", 0),
            manifest.get("sync_tree_memory_pair_peak_hwm_kib", 0),
            manifest.get("sync_tree_memory_pair_maximum_delta_hwm_kib", 0),
        ]
        require(
            manifest.get("sync_tree_memory_observed_role_count", 0)
            == (2 if memory_scenario else 0)
            and (
                all(isinstance(value, int) for value in memory_values)
                and memory_values[0] == 65_536
                and memory_values[1] == 128
                and SYNC_SCENARIOS[scenario] < memory_values[2]
                <= 8_388_608
                and 0 < memory_values[3] <= memory_values[4]
                <= memory_values[5] <= memory_values[0]
                and memory_values[6] == memory_values[5] - memory_values[3]
                and 0 < memory_values[7] <= memory_values[8]
                <= memory_values[9] <= memory_values[0]
                and memory_values[10] == memory_values[9] - memory_values[7]
                and memory_values[11] == max(memory_values[5], memory_values[9])
                and memory_values[12] == max(memory_values[6], memory_values[10])
                and SHA256.fullmatch(str(memory_head)) is not None
                and SHA256.fullmatch(str(memory_artifact)) is not None
                and SHA256.fullmatch(str(memory_manifest)) is not None
                and memory_head != manifest["sync_head_record"]
                and memory_artifact != manifest["sync_artifact_sha256"]
                and memory_manifest != manifest["sync_manifest_sha256"]
                if memory_scenario
                else memory_values == [0] * len(memory_values)
                and memory_head == ""
                and memory_artifact == ""
                and memory_manifest == ""
            ),
            "deterministic synchronization tree memory summary is invalid",
        )
        source_corrupt_scenario = scenario == "sync-tree-source-corrupt"
        source_corrupt_head = manifest.get(
            "sync_tree_source_corrupt_head_record", ""
        )
        source_corrupt_artifact = manifest.get(
            "sync_tree_source_corrupt_artifact_sha256", ""
        )
        source_corrupt_manifest = manifest.get(
            "sync_tree_source_corrupt_manifest_sha256", ""
        )
        source_corrupt_artifact_bytes = manifest.get(
            "sync_tree_source_corrupt_artifact_bytes", 0
        )
        source_corrupt_manifest_bytes = manifest.get(
            "sync_tree_source_corrupt_manifest_bytes", 0
        )
        source_corrupt_quarantined_objects = manifest.get(
            "sync_tree_source_corrupt_quarantined_objects", 0
        )
        source_corrupt_quarantined_bytes = manifest.get(
            "sync_tree_source_corrupt_quarantined_bytes", 0
        )
        require(
            manifest.get("sync_tree_source_corrupt_observed_role_count", 0)
            == (2 if source_corrupt_scenario else 0)
            and manifest.get(
                "sync_tree_source_corrupt_refused_role_count", 0
            )
            == (2 if source_corrupt_scenario else 0)
            and manifest.get(
                "sync_tree_source_corrupt_repaired_role_count", 0
            )
            == (2 if source_corrupt_scenario else 0)
            and manifest.get(
                "sync_tree_source_corrupt_retry_observed_role_count", 0
            )
            == (2 if source_corrupt_scenario else 0)
            and (
                SHA256.fullmatch(str(source_corrupt_head)) is not None
                and SHA256.fullmatch(str(source_corrupt_artifact)) is not None
                and SHA256.fullmatch(str(source_corrupt_manifest)) is not None
                and source_corrupt_head != manifest["sync_head_record"]
                and source_corrupt_artifact != manifest["sync_artifact_sha256"]
                and source_corrupt_manifest != manifest["sync_manifest_sha256"]
                and source_corrupt_artifact_bytes
                == SYNC_SCENARIOS[scenario]
                and isinstance(source_corrupt_manifest_bytes, int)
                and 0 < source_corrupt_manifest_bytes <= 1_048_576
                and source_corrupt_quarantined_objects == 2
                and source_corrupt_quarantined_bytes
                == source_corrupt_artifact_bytes + source_corrupt_manifest_bytes
                if source_corrupt_scenario
                else source_corrupt_head == ""
                and source_corrupt_artifact == ""
                and source_corrupt_manifest == ""
                and source_corrupt_artifact_bytes == 0
                and source_corrupt_manifest_bytes == 0
                and source_corrupt_quarantined_objects == 0
                and source_corrupt_quarantined_bytes == 0
            ),
            "deterministic publisher-source corruption summary is invalid",
        )
        destination_corrupt_scenario = (
            scenario == "sync-tree-destination-corrupt"
        )
        destination_corrupt_head = manifest.get(
            "sync_tree_destination_corrupt_head_record", ""
        )
        destination_corrupt_artifact = manifest.get(
            "sync_tree_destination_corrupt_artifact_sha256", ""
        )
        destination_corrupt_manifest = manifest.get(
            "sync_tree_destination_corrupt_manifest_sha256", ""
        )
        destination_corrupt_artifact_bytes = manifest.get(
            "sync_tree_destination_corrupt_artifact_bytes", 0
        )
        destination_corrupt_manifest_bytes = manifest.get(
            "sync_tree_destination_corrupt_manifest_bytes", 0
        )
        destination_corrupt_file_id = manifest.get(
            "sync_tree_destination_corrupt_file_id", ""
        )
        destination_corrupt_position = manifest.get(
            "sync_tree_destination_corrupt_position_bytes", 0
        )
        destination_corrupt_committed = manifest.get(
            "sync_tree_destination_corrupt_committed_before_failure", 0
        )
        destination_corrupt_retry_requested = manifest.get(
            "sync_tree_destination_corrupt_retry_requested_objects", 0
        )
        require(
            manifest.get("sync_tree_destination_corrupt_observed_role_count", 0)
            == (2 if destination_corrupt_scenario else 0)
            and manifest.get(
                "sync_tree_destination_corrupt_rejected_role_count", 0
            )
            == (2 if destination_corrupt_scenario else 0)
            and manifest.get(
                "sync_tree_destination_corrupt_retry_observed_role_count", 0
            )
            == (2 if destination_corrupt_scenario else 0)
            and (
                SHA256.fullmatch(str(destination_corrupt_head)) is not None
                and SHA256.fullmatch(str(destination_corrupt_artifact))
                is not None
                and SHA256.fullmatch(str(destination_corrupt_manifest))
                is not None
                and SHA256.fullmatch(str(destination_corrupt_file_id))
                is not None
                and destination_corrupt_head != manifest["sync_head_record"]
                and destination_corrupt_artifact
                != manifest["sync_artifact_sha256"]
                and destination_corrupt_manifest
                != manifest["sync_manifest_sha256"]
                and destination_corrupt_artifact_bytes
                == SYNC_SCENARIOS[scenario]
                and isinstance(destination_corrupt_manifest_bytes, int)
                and 0 < destination_corrupt_manifest_bytes <= 1_048_576
                and isinstance(destination_corrupt_position, int)
                and 0
                < destination_corrupt_position
                < destination_corrupt_artifact_bytes
                and destination_corrupt_committed in {0, 1}
                and destination_corrupt_retry_requested
                == 2 - destination_corrupt_committed
                if destination_corrupt_scenario
                else destination_corrupt_head == ""
                and destination_corrupt_artifact == ""
                and destination_corrupt_manifest == ""
                and destination_corrupt_artifact_bytes == 0
                and destination_corrupt_manifest_bytes == 0
                and destination_corrupt_file_id == ""
                and destination_corrupt_position == 0
                and destination_corrupt_committed == 0
                and destination_corrupt_retry_requested == 0
            ),
            "deterministic subscriber-destination corruption summary is invalid",
        )
        control_replay_scenario = scenario == "sync-tree-control-replay"
        control_replay_head = manifest.get(
            "sync_tree_control_replay_head_record", ""
        )
        control_replay_artifact = manifest.get(
            "sync_tree_control_replay_artifact_sha256", ""
        )
        control_replay_manifest = manifest.get(
            "sync_tree_control_replay_manifest_sha256", ""
        )
        control_replay_role_counts = (
            "sync_tree_control_replay_observed_role_count",
            "sync_tree_control_replay_exact_replay_observed_role_count",
            "sync_tree_control_replay_reordered_result_observed_role_count",
            "sync_tree_control_replay_conflict_refused_role_count",
            "sync_tree_control_replay_activation_observed_role_count",
        )
        control_replay_counts = {
            "sync_tree_control_replay_admitted_before_replay": 2,
            "sync_tree_control_replay_publisher_head_requests_delta": 1,
            "sync_tree_control_replay_publisher_object_requests_delta": 2,
            "sync_tree_control_replay_publisher_file_offers_delta": 2,
            "sync_tree_control_replay_publisher_replay_hits_delta": 3,
            "sync_tree_control_replay_publisher_replay_conflicts_delta": 1,
            "sync_tree_control_replay_subscriber_incoming_head_results_delta": 2,
            "sync_tree_control_replay_subscriber_incoming_object_results_delta": 4,
            "sync_tree_control_replay_subscriber_outgoing_object_requests_delta": 4,
        }
        require(
            all(
                manifest.get(field, 0)
                == (2 if control_replay_scenario else 0)
                for field in control_replay_role_counts
            )
            and all(
                manifest.get(field, 0)
                == (expected if control_replay_scenario else 0)
                for field, expected in control_replay_counts.items()
            )
            and (
                SHA256.fullmatch(str(control_replay_head)) is not None
                and SHA256.fullmatch(str(control_replay_artifact)) is not None
                and SHA256.fullmatch(str(control_replay_manifest)) is not None
                and control_replay_head != manifest["sync_head_record"]
                and control_replay_artifact
                != manifest["sync_artifact_sha256"]
                and control_replay_manifest
                != manifest["sync_manifest_sha256"]
                if control_replay_scenario
                else control_replay_head == ""
                and control_replay_artifact == ""
                and control_replay_manifest == ""
            ),
            "synchronization control replay summary is invalid",
        )
        process_restart = scenario in {
            "sync-file-restart",
            "sync-file-restart-resume",
            "sync-file-range-restart-resume",
            *CONTENT_RESTART_SCENARIOS,
        }
        restart = scenario in {
            "sync-file-restart",
            "sync-file-restart-resume",
            "sync-file-guest-restart",
            "sync-file-range-restart-resume",
            *CONTENT_RESTART_SCENARIOS,
        }
        require(
            manifest.get("sync_client_daemon_restart_count", 0)
            == (1 if process_restart else 0),
            "synchronization daemon restart count mismatch",
        )
        require(
            manifest.get("sync_unclean_stop_count", 0)
            == (1 if process_restart else 0),
            "synchronization unclean-stop count mismatch",
        )
        interrupted_bytes = manifest.get("sync_interrupted_staging_bytes", 0)
        require(
            isinstance(interrupted_bytes, int)
            and (
                0
                < interrupted_bytes
                < SYNC_SCENARIOS[scenario] + 1024 * 1024
                if process_restart
                else interrupted_bytes == 0
            ),
            "synchronization interrupted staging evidence is invalid",
        )
        require(
            manifest.get("sync_restart_recovered_role_count", 0)
            == (2 if restart else 0),
            "synchronization recovered-role count mismatch",
        )
        restart_prefix_resume = scenario == "sync-file-restart-resume"
        require(
            manifest.get("sync_restart_prefix_resume_role_count", 0)
            == (2 if restart_prefix_resume else 0)
            and isinstance(
                manifest.get("sync_restart_resumed_attempts", 0), int
            )
            and isinstance(manifest.get("sync_restart_resumed_bytes", 0), int)
            and (
                1 <= manifest["sync_restart_resumed_attempts"] <= 2
                and manifest["sync_restart_resumed_bytes"]
                == interrupted_bytes
                if restart_prefix_resume
                else manifest.get("sync_restart_resumed_attempts", 0) == 0
                and manifest.get("sync_restart_resumed_bytes", 0) == 0
            ),
            "synchronization restart-prefix summary is invalid",
        )
        disconnect = scenario == "sync-file-disconnect"
        disconnect_bytes = manifest.get("sync_disconnect_staging_bytes", 0)
        require(
            isinstance(disconnect_bytes, int)
            and (
                0 < disconnect_bytes < SYNC_SCENARIOS[scenario] + 1024 * 1024
                if disconnect
                else disconnect_bytes == 0
            ),
            "synchronization disconnect staging evidence is invalid",
        )
        require(
            manifest.get("sync_disconnect_recovered_role_count", 0)
            == (2 if disconnect else 0),
            "synchronization disconnect recovery count mismatch",
        )
        require(
            manifest.get("sync_disconnect_minimum_stable_samples", 0)
            == (50 if disconnect else 0),
            "synchronization disconnect stability window mismatch",
        )
        guest_restart = scenario == "sync-file-guest-restart"
        guest_restart_bytes = manifest.get(
            "sync_guest_restart_staging_bytes", 0
        )
        require(
            isinstance(guest_restart_bytes, int)
            and (
                0
                < guest_restart_bytes
                < SYNC_SCENARIOS[scenario] + 1024 * 1024
                if guest_restart
                else guest_restart_bytes == 0
            ),
            "synchronization guest-restart staging evidence is invalid",
        )
        require(
            manifest.get("sync_guest_restart_recovered_role_count", 0)
            == (2 if guest_restart else 0),
            "synchronization guest-restart recovery count mismatch",
        )
        require(
            manifest.get("sync_guest_restart_minimum_stable_samples", 0)
            == (50 if guest_restart else 0),
            "synchronization guest-restart stability window mismatch",
        )
        cancelled_bytes = manifest.get("sync_cancelled_staging_bytes", 0)
        cancelled_receives = manifest.get("sync_cancelled_receive_count", 0)
        require(
            isinstance(cancelled_bytes, int)
            and isinstance(cancelled_receives, int)
            and (
                0 < cancelled_bytes < SYNC_SCENARIOS[scenario] + 1024 * 1024
                and 0 < cancelled_receives <= 2
                if sync_cancellation
                else cancelled_bytes == 0 and cancelled_receives == 0
            ),
            "synchronization cancellation summary is invalid",
        )
        pause = scenario == "sync-file-pause"
        pause_position = manifest.get("sync_pause_position_bytes", 0)
        require(
            manifest.get("sync_pause_observed_role_count", 0)
            == (2 if pause else 0)
            and manifest.get("sync_pause_minimum_stable_samples", 0)
            == (20 if pause else 0)
            and (
                isinstance(pause_position, int)
                and 0
                < pause_position
                < SYNC_SCENARIOS[scenario] + 1024 * 1024
                and SHA256.fullmatch(
                    str(manifest.get("sync_pause_file_id", ""))
                )
                is not None
                if pause
                else pause_position == 0
                and manifest.get("sync_pause_file_id", "") == ""
            ),
            "synchronization pause/resume summary is invalid",
        )
        range_scenario = scenario in SYNC_POSITIVE_RANGE_SCENARIOS
        fallback_scenario = scenario == "sync-file-corrupt-basis"
        retry_scenario = scenario == "sync-file-range-retry"
        range_count = manifest.get("sync_range_count", 0)
        range_reused = manifest.get("sync_range_reused_bytes", 0)
        range_fetched = manifest.get("sync_range_fetched_bytes", 0)
        require(
            manifest.get("sync_range_observed_role_count", 0)
            == (2 if range_scenario else 0)
            and manifest.get("sync_range_fallback_observed_role_count", 0)
            == (2 if fallback_scenario else 0)
            and manifest.get("sync_corrupt_basis_preserved_role_count", 0)
            == (2 if fallback_scenario else 0)
            and manifest.get("sync_range_retry_observed_role_count", 0)
            == (2 if retry_scenario else 0)
            and isinstance(range_count, int)
            and isinstance(range_reused, int)
            and isinstance(range_fetched, int)
            and (
                range_count > 0
                and range_reused > 0
                and 0 < range_fetched < SYNC_SCENARIOS[scenario]
                and range_reused + range_fetched == SYNC_SCENARIOS[scenario]
                if range_scenario
                else range_count == 0
                and range_reused == 0
                and range_fetched == 0
            ),
            "synchronization bounded-range summary is invalid",
        )
        retry_position = manifest.get("sync_range_retry_position_bytes", 0)
        retry_retained = manifest.get("sync_range_retry_retained_bytes", 0)
        retry_resumed = manifest.get("sync_range_retry_resumed_bytes", 0)
        retry_discarded = manifest.get("sync_range_retry_discarded_bytes", 0)
        retry_retention_fallbacks = manifest.get(
            "sync_range_retry_retention_fallbacks", 0
        )
        resumed_retry_evidence = all(
            field in manifest
            for field in (
                "sync_range_retry_retained_bytes",
                "sync_range_retry_resumed_bytes",
                "sync_range_retry_discarded_bytes",
                "sync_range_retry_retention_fallbacks",
            )
        )
        first_file_id = manifest.get("sync_range_retry_first_file_id", "")
        second_file_id = manifest.get("sync_range_retry_second_file_id", "")
        require(
            (
                isinstance(retry_position, int)
                and (
                    0 < retry_position == retry_retained == retry_resumed
                    < range_fetched
                    and retry_discarded == 0
                    and retry_retention_fallbacks == 0
                    if resumed_retry_evidence
                    else 0 < retry_position < range_fetched
                )
                and SHA256.fullmatch(str(first_file_id)) is not None
                and SHA256.fullmatch(str(second_file_id)) is not None
                and first_file_id != second_file_id
                if retry_scenario
                else retry_position == 0
                and retry_retained == 0
                and retry_resumed == 0
                and retry_discarded == 0
                and retry_retention_fallbacks == 0
                and first_file_id == ""
                and second_file_id == ""
            ),
            "synchronization bounded-range retry summary is invalid",
        )
        range_restart = scenario == "sync-file-range-restart-resume"
        range_restart_interrupted = manifest.get(
            "sync_range_restart_interrupted_bytes", 0
        )
        range_restart_retained = manifest.get(
            "sync_range_restart_retained_bytes", 0
        )
        range_restart_resumed_attempts = manifest.get(
            "sync_range_restart_resumed_attempts", 0
        )
        range_restart_resumed = manifest.get(
            "sync_range_restart_resumed_bytes", 0
        )
        range_restart_suffix = manifest.get(
            "sync_range_restart_suffix_bytes", 0
        )
        range_restart_jobs = (
            manifest.get("sync_range_restart_first_job_id", 0),
            manifest.get("sync_range_restart_second_job_id", 0),
        )
        range_restart_attempts = (
            manifest.get("sync_range_restart_first_attempt_id", 0),
            manifest.get("sync_range_restart_second_attempt_id", 0),
        )
        range_restart_messages = (
            manifest.get("sync_range_restart_first_message_id", 0),
            manifest.get("sync_range_restart_second_message_id", 0),
        )
        range_restart_file_ids = (
            manifest.get("sync_range_restart_first_file_id", ""),
            manifest.get("sync_range_restart_second_file_id", ""),
        )
        require(
            manifest.get("sync_range_restart_resume_role_count", 0)
            == (2 if range_restart else 0)
            and (
                all(
                    isinstance(value, int)
                    for value in (
                        range_restart_interrupted,
                        range_restart_retained,
                        range_restart_resumed_attempts,
                        range_restart_resumed,
                        range_restart_suffix,
                        *range_restart_jobs,
                        *range_restart_attempts,
                        *range_restart_messages,
                    )
                )
                and range_restart_resumed_attempts == 1
                and 0
                < range_restart_interrupted
                == range_restart_retained
                == range_restart_resumed
                < range_fetched
                and range_restart_resumed + range_restart_suffix
                == range_fetched
                and all(
                    value > 0
                    for value in (
                        *range_restart_jobs,
                        *range_restart_attempts,
                        *range_restart_messages,
                    )
                )
                and range_restart_jobs[0] != range_restart_jobs[1]
                and range_restart_attempts[0] != range_restart_attempts[1]
                and range_restart_messages[0] != range_restart_messages[1]
                and all(
                    SHA256.fullmatch(str(value)) is not None
                    for value in range_restart_file_ids
                )
                and range_restart_file_ids[0] != range_restart_file_ids[1]
                if range_restart
                else range_restart_interrupted == 0
                and range_restart_retained == 0
                and range_restart_resumed_attempts == 0
                and range_restart_resumed == 0
                and range_restart_suffix == 0
                and all(
                    value == 0
                    for value in (
                        *range_restart_jobs,
                        *range_restart_attempts,
                        *range_restart_messages,
                    )
                )
                and range_restart_file_ids == ("", "")
            ),
            "synchronization range-restart summary is invalid",
        )
        repair_scenario = scenario == "sync-file-repair"
        legacy_repair = repair_scenario and is_legacy_repair_evidence(manifest)
        gc_repair = repair_scenario and not legacy_repair
        gc_fields = (
            "sync_gc_observed_role_count",
            "sync_gc_dry_candidates",
            "sync_gc_moved_objects",
            "sync_gc_durable_objects",
            "sync_gc_outside_sentinel_count",
            "sync_gc_purge_disabled_role_count",
            "sync_gc_mount_refused_role_count",
        )
        require(
            manifest.get("sync_repair_observed_role_count", 0)
            == (2 if repair_scenario else 0)
            and manifest.get("sync_repair_recovered_role_count", 0)
            == (2 if repair_scenario else 0)
            and manifest.get("sync_repair_inspected_objects", 0)
            == (2 if repair_scenario else 0)
            and manifest.get("sync_repair_quarantined_objects", 0)
            == (1 if repair_scenario else 0)
            and manifest.get("sync_repair_quarantined_bytes", 0)
            == (SYNC_SCENARIOS[scenario] if repair_scenario else 0)
            and manifest.get("sync_gc_observed_role_count", 0)
            == (2 if gc_repair else 0)
            and manifest.get("sync_gc_dry_candidates", 0)
            == (1 if gc_repair else 0)
            and manifest.get("sync_gc_moved_objects", 0)
            == (1 if gc_repair else 0)
            and manifest.get("sync_gc_durable_objects", 0)
            == (1 if gc_repair else 0)
            and manifest.get("sync_gc_outside_sentinel_count", 0)
            == (4 if gc_repair else 0)
            and manifest.get("sync_gc_purge_disabled_role_count", 0)
            == (2 if gc_repair else 0)
            and manifest.get("sync_gc_mount_refused_role_count", 0)
            == (2 if gc_repair else 0)
            and (not legacy_repair or all(field not in manifest for field in gc_fields)),
            "synchronization repair summary is invalid",
        )
    require(
        manifest.get("ratox_bulk_stream_count", 0) == bulk_stream_count,
        "Ratox bulk stream count mismatch",
    )
    require(
        manifest.get("ratox_sample_count", sample_count) == sample_count,
        "Ratox sample count mismatch",
    )
    require(
        manifest.get("ratox_stripe_route_count", 1) == stripe_route_count,
        "Ratox stripe route count mismatch",
    )
    require(
        isinstance(stripe_route_restart_count, int)
        and 0 <= stripe_route_restart_count <= 13,
        "Ratox stripe route restart count is invalid",
    )
    require(
        stripe_injected_restart_count
        == (1 if scenario == "ratox-stripe-recovery-32" else 0),
        "Ratox injected stripe restart count mismatch",
    )
    live_stripe_loss = scenario in RATOX_LIVE_LOSS_SCENARIOS
    require(
        manifest.get("ratox_stripe_live_fault_count", 0)
        == int(live_stripe_loss)
        and manifest.get("ratox_stripe_live_observer_count", 0)
        == int(live_stripe_loss)
        and manifest.get("ratox_stripe_live_recovered_role_count", 0)
        == (2 if live_stripe_loss else 0)
        and manifest.get("ratox_stripe_live_affected_transfer_count", 0)
        == (8 if live_stripe_loss else 0)
        and manifest.get("ratox_stripe_live_reassigned_transfer_count", 0) == 0,
        "Ratox live stripe-loss manifest boundary mismatch",
    )
    if scenario in GUEST_RESTART_SCENARIOS:
        source_proof_root = proof_root
        if compact is not None:
            source_proof_root = (
                ROOT
                / ".sandwurm/lab/pairs"
                / str(compact.get("source_proof_id", ""))
            )
        initial_chain_entry = manifest.get("initial_device_chain", {})
        initial_chain_path = confined(
            proof_root,
            initial_chain_entry.get("path"),
            "device/direct-cloud-hypervisor-live-chain.json",
        )
        require(
            initial_chain_entry.get("sha256") == digest(initial_chain_path),
            "initial device chain digest mismatch",
        )
        initial_chain = load(initial_chain_path)
        require(
            initial_chain.get("status") == "blocked"
            and initial_chain.get("failure", {}).get("blockers")
            == ["live:console-not-observed"],
            "initial device chain did not bind the reboot exit",
        )
        initial_launch_entry = manifest.get("initial_device_launch", {})
        initial_launch_path = confined(
            proof_root,
            initial_launch_entry.get("path"),
            "device/live/cloud-hypervisor-launch.json",
        )
        require(
            initial_launch_entry.get("sha256") == digest(initial_launch_path),
            "initial device launch digest mismatch",
        )
        initial_launch = load(initial_launch_path)
        require(
            initial_launch.get("status") == "blocked"
            and initial_launch.get("vmm", {}).get("process_observed") is True
            and initial_launch.get("vmm", {}).get("exit_observed") is True
            and initial_launch.get("vmm", {}).get("exit_status") == 1,
            "initial device VMM reboot exit is invalid",
        )
        expected_disk = (
            f"path={source_proof_root}/device/prelaunch/runtime-root/runtime-root/"
            "sandwurm-direct-cloud.raw,readonly=off"
        )
        require(
            expected_disk in initial_launch.get("vmm", {}).get("argv", []),
            "initial device launch did not bind the persisted runtime disk",
        )
    else:
        require(manifest.get("initial_device_chain") is None, "unexpected initial device chain")
        require(manifest.get("initial_device_launch") is None, "unexpected initial device launch")
    require(manifest.get("identity_mode") == "reused-immutable-private-baseline", "identity mode mismatch")
    require(manifest.get("identity_baseline_unchanged") is True, "identity baseline changed")
    contains_private_disks = manifest.get("proof_root_contains_private_guest_disks")
    require(
        isinstance(contains_private_disks, bool),
        "private proof-root disk classification is absent",
    )
    if contains_private_disks:
        require(compact is None, "private proof root claims compact export")
    else:
        require(isinstance(compact, dict), "compact export declaration is absent")
        require(compact.get("schema") == COMPACT_SCHEMA, "compact export schema mismatch")
        require(
            compact.get("source_proof_root_contained_private_guest_disks") is True,
            "compact export lost its source private-disk warning",
        )
        require(
            SHA256.fullmatch(str(compact.get("source_manifest_sha256", "")))
            is not None,
            "compact export source manifest digest is invalid",
        )
    require(manifest.get("receipts_contain_secrets") is False, "receipts are not content-free")

    taps = manifest.get("taps")
    require(isinstance(taps, list) and len(taps) == 2, "exactly two TAP observations are required")
    require({tap.get("name") for tap in taps} == {"vm-iotoxc", "vm-iotoxd"}, "TAP identity mismatch")
    require(all(tap.get("master") == "sandwurm-vm" for tap in taps), "a TAP escaped the prepared bridge")

    version, revision = product_identity()
    binary_digests: set[str] = set()
    bootstrap_digests: set[str] = set()
    verified_receipts = {}
    observed_stripe_route_restarts = 0
    observed_stripe_injected_restarts = 0
    sync_revisions: list[tuple[object, ...]] = []
    sync_restart_evidence: dict[str, tuple[object, ...]] = {}
    ratox_capture_rows: list[list[str]] = []
    ratox_heartbeat_rows: list[list[str]] = []
    ratox_capture_peer_commitment = ""
    ratox_resource_intervals = 0
    ratox_agent_statuses = 0
    mixed_auxiliary_key_hashes: list[str] = []
    addresses = {
        "client": ("10.0.0.11", "10.0.0.12", "vm-iotoxc"),
        "device": ("10.0.0.12", "10.0.0.11", "vm-iotoxd"),
    }
    for role in ROLES:
        receipt_entry = manifest.get("receipts", {}).get(role, {})
        evidence_role = (
            "device-restart"
            if scenario in GUEST_RESTART_SCENARIOS and role == "device"
            else role
        )
        receipt_relative = f"{evidence_role}/live/workspace-export/guest-receipts/iotox/pair.json"
        receipt_path = confined(proof_root, receipt_entry.get("path"), receipt_relative)
        require(receipt_entry.get("sha256") == digest(receipt_path), f"{role} receipt digest mismatch")
        receipt = load(receipt_path)
        local_ip, peer_ip, tap_name = addresses[role]
        require(receipt.get("schema") == "iotox.sandwurm-pair.v0", f"{role} receipt schema mismatch")
        require(receipt.get("status") == "passed" and receipt.get("role") == role, f"{role} receipt did not pass")
        require(receipt.get("route_mode") == route, f"{role} route mismatch")
        require(receipt.get("scenario", "baseline") == scenario, f"{role} scenario mismatch")
        require(receipt.get("expected_connection") == connection, f"{role} expected connection mismatch")
        require(receipt.get("observed_connection") == connection, f"{role} observed connection mismatch")
        require(
            receipt.get("network", "Tox/native")
            == expected_network(route),
            f"{role} network projection mismatch",
        )
        require(receipt.get("local_ipv4") == local_ip and receipt.get("peer_ipv4") == peer_ip, f"{role} topology mismatch")
        for field in (
            "tox_friendship",
            "session_confirmed",
            "bidirectional_text",
            "reusable_identity_copy",
            "controlled_host_bridge_bootstrap",
        ):
            require(receipt.get(field) is True, f"{role} missing positive observation: {field}")
        require(
            receipt.get("private_l2_ping")
            is (route != "tox-tor" and route not in I2P_ROUTES),
            f"{role} private-L2 observation mismatch",
        )
        if scenario in BIDIRECTIONAL_SYNC_SCENARIOS:
            require(
                receipt.get("sync_bidirectional_observed") is True
                and receipt.get("sync_bidirectional_conflict_observed") is True
                and receipt.get("sync_bidirectional_resolution_observed") is True
                and receipt.get("sync_bidirectional_restart_count") == 1
                and receipt.get("sync_bidirectional_final_sha256")
                == "e3b0c44298fc1c149afbf4c8996fb924"
                "27ae41e4649b934ca495991b7852b855",
                f"{role} bidirectional sync evidence is incomplete",
            )
        else:
            require(
                receipt.get("sync_bidirectional_observed", False) is False
                and receipt.get(
                    "sync_bidirectional_conflict_observed", False
                )
                is False
                and receipt.get(
                    "sync_bidirectional_resolution_observed", False
                )
                is False
                and receipt.get("sync_bidirectional_restart_count", 0) == 0
                and receipt.get("sync_bidirectional_final_sha256", "") == "",
                f"{role} unexpectedly claims bidirectional sync",
            )
        if scenario in AUTOMATION_SYNC_SCENARIOS:
            expected_hashes = (
                "a38b63d20844a25c35a872aab9988d2280dfc4c10d2fa626d252eedbc4a83945",
                "c92740acd745679f5aa44b02b971765ccfd20a395fa3ab89615b5ed4deb5457b",
                "1cdd300ae68361bfd6bc5b9793df532325d324c8509d11a488e6fde35939f2ca",
            )
            require(
                receipt.get("sync_automation_observed") is True
                and receipt.get("sync_automation_policy_reloaded") is True
                and receipt.get("sync_automation_restart_count") == 1
                and receipt.get("sync_automation_manual_transfer_commands") == 0
                and tuple(receipt.get("sync_automation_generation_sha256", []))
                == expected_hashes,
                f"{role} unattended sync evidence is incomplete",
            )
        else:
            require(
                receipt.get("sync_automation_observed", False) is False
                and receipt.get("sync_automation_policy_reloaded", False)
                is False
                and receipt.get("sync_automation_restart_count", 0) == 0
                and receipt.get(
                    "sync_automation_manual_transfer_commands", 0
                )
                == 0
                and receipt.get("sync_automation_generation_sha256", []) == [],
                f"{role} unexpectedly claims unattended sync",
            )
        require(
            not actual_i2p
            or receipt.get("i2p_node_records_sha256")
            == manifest.get("actual_i2p_node_records_sha256"),
            f"{role} I2P node-set commitment mismatch",
        )
        if mixed_context:
            auxiliary_hash = receipt.get(
                "private_route_auxiliary_key_sha256", ""
            )
            require(
                receipt.get("private_route_mixed_context_observed") is True
                and receipt.get("private_route_primary_network") == "Tox/native"
                and receipt.get("private_route_auxiliary_network")
                == (
                    "Tox/I2P-construction"
                    if actual_i2p_payload
                    else "Tox/Tor"
                )
                and SHA256.fullmatch(str(auxiliary_hash)) is not None,
                f"{role} private mixed-context receipt is invalid",
            )
            mixed_auxiliary_key_hashes.append(str(auxiliary_hash))
        else:
            require(
                receipt.get("private_route_mixed_context_observed", False)
                is False
                and receipt.get("private_route_primary_network", "") == ""
                and receipt.get("private_route_auxiliary_network", "") == ""
                and receipt.get("private_route_auxiliary_key_sha256", "") == "",
                f"{role} non-mixed receipt claims a private route context",
            )
        payload_carrier = receipt.get(
            "actual_tor_payload_carrier_sha256", ""
        )
        require(
            receipt.get("actual_tor_payload_observed", False)
            is (actual_tor_payload and role == "client")
            and (
                SHA256.fullmatch(str(payload_carrier)) is not None
                if actual_tor_payload and role == "client"
                else payload_carrier == ""
            )
            and receipt.get("actual_tor_payload_reassignments", 0) == 0,
            f"{role} actual-Tor payload receipt is invalid",
        )
        if actual_tor_payload and role == "client":
            require(
                payload_carrier
                == receipt.get("private_route_auxiliary_key_sha256")
                == manifest.get("actual_tor_payload_carrier_sha256"),
                "actual-Tor payload carrier is not the exact Tor member",
            )
        i2p_payload_carrier = receipt.get(
            "actual_i2p_payload_carrier_sha256", ""
        )
        require(
            receipt.get("actual_i2p_payload_observed", False)
            is (actual_i2p_payload and role == "client")
            and (
                SHA256.fullmatch(str(i2p_payload_carrier)) is not None
                if actual_i2p_payload and role == "client"
                else i2p_payload_carrier == ""
            )
            and receipt.get("actual_i2p_payload_reassignments", 0) == 0,
            f"{role} actual-I2P payload receipt is invalid",
        )
        if actual_i2p_payload and role == "client":
            require(
                i2p_payload_carrier
                == receipt.get("private_route_auxiliary_key_sha256")
                == manifest.get("actual_i2p_payload_carrier_sha256"),
                "actual-I2P payload carrier is not the exact I2P member",
            )
        i2p_loss = manifest.get("actual_i2p_fail_closed_loss", {})
        if actual_i2p_loss and role == "client":
            require(
                receipt.get("actual_i2p_fail_closed_loss_observed")
                is True
                and receipt.get(
                    "actual_i2p_fail_closed_loss_position_bytes"
                )
                == i2p_loss.get("position_bytes")
                and receipt.get(
                    "actual_i2p_fail_closed_loss_carrier_sha256"
                )
                == i2p_payload_carrier
                == i2p_loss.get("stopped_carrier_sha256")
                and receipt.get(
                    "actual_i2p_fail_closed_loss_carrier_losses"
                )
                == i2p_loss.get("carrier_losses")
                == 1
                and receipt.get(
                    "actual_i2p_fail_closed_loss_reassignments"
                )
                == i2p_loss.get("reassignments")
                == 0
                and receipt.get(
                    "actual_i2p_fail_closed_loss_blocked_jobs"
                )
                == i2p_loss.get("blocked_jobs")
                == 1
                and receipt.get(
                    "actual_i2p_fail_closed_loss_recoveries"
                )
                == i2p_loss.get("recoveries")
                == 1
                and receipt.get(
                    "actual_i2p_fail_closed_loss_worker_restarts"
                )
                == i2p_loss.get("route_worker_restarts")
                == 0
                and receipt.get(
                    "actual_i2p_fail_closed_loss_original_job_id"
                )
                == i2p_loss.get("original_job_id")
                and receipt.get(
                    "actual_i2p_fail_closed_loss_replacement_job_id"
                )
                == i2p_loss.get("replacement_job_id")
                and receipt.get(
                    "actual_i2p_fail_closed_loss_old_job_cancelled"
                )
                is True
                and receipt.get(
                    "actual_i2p_fail_closed_loss_same_carrier"
                )
                is True,
                "client actual-I2P fail-closed loss receipt is invalid",
            )
        else:
            require(
                receipt.get("actual_i2p_fail_closed_loss_observed", False)
                is False
                and receipt.get(
                    "actual_i2p_fail_closed_loss_position_bytes", 0
                )
                == 0
                and receipt.get(
                    "actual_i2p_fail_closed_loss_carrier_sha256", ""
                )
                == ""
                and all(
                    receipt.get(field, 0) == 0
                    for field in (
                        "actual_i2p_fail_closed_loss_carrier_losses",
                        "actual_i2p_fail_closed_loss_reassignments",
                        "actual_i2p_fail_closed_loss_blocked_jobs",
                        "actual_i2p_fail_closed_loss_recoveries",
                        "actual_i2p_fail_closed_loss_worker_restarts",
                        "actual_i2p_fail_closed_loss_original_job_id",
                        "actual_i2p_fail_closed_loss_replacement_job_id",
                    )
                )
                and receipt.get(
                    "actual_i2p_fail_closed_loss_old_job_cancelled", False
                )
                is False
                and receipt.get(
                    "actual_i2p_fail_closed_loss_same_carrier", False
                )
                is False,
                f"{role} unexpectedly claims actual-I2P fail-closed loss",
            )
        pull_attempts = receipt.get("sync_initial_pull_attempts", 0)
        pull_failures = receipt.get("sync_initial_pull_failures", 0)
        pull_error_digest = receipt.get(
            "sync_initial_pull_first_error_sha256", ""
        )
        if actual_tor_payload or actual_i2p_payload or "sync_initial_pull_attempts" in receipt:
            if role == "client" and scenario in SYNC_SCENARIOS:
                require(
                    isinstance(pull_attempts, int)
                    and pull_attempts >= 1
                    and isinstance(pull_failures, int)
                    and 0 <= pull_failures < pull_attempts
                    and pull_attempts == pull_failures + 1
                    and (
                        SHA256.fullmatch(str(pull_error_digest)) is not None
                        if pull_failures > 0
                        else pull_error_digest == ""
                    ),
                    "client sync pull admission receipt is invalid",
                )
                if actual_tor_payload or actual_i2p_payload:
                    require(
                        pull_attempts
                        == manifest.get("sync_initial_pull_attempts")
                        and pull_failures
                        == manifest.get("sync_initial_pull_failures")
                        and pull_error_digest
                        == manifest.get(
                            "sync_initial_pull_first_error_sha256"
                        ),
                        "sync pull admission manifest does not bind the client receipt",
                    )
            else:
                require(
                    pull_attempts == 0
                    and pull_failures == 0
                    and pull_error_digest == "",
                    f"{role} unexpectedly claims sync pull admission",
                )
        initial_epoch = receipt.get("initial_online_epoch")
        recovered_epoch = receipt.get("recovered_online_epoch")
        if scenario == "relay-restart":
            require(
                isinstance(initial_epoch, int) and initial_epoch > 0,
                f"{role} initial online epoch is invalid",
            )
            require(
                isinstance(recovered_epoch, int) and recovered_epoch > initial_epoch,
                f"{role} recovered online epoch did not advance",
            )
            require(
                receipt.get("relay_interruption_observed") is True,
                f"{role} did not observe relay interruption",
            )
            require(
                receipt.get("relay_recovery_observed") is True,
                f"{role} did not observe relay recovery",
            )
        else:
            require(
                receipt.get("relay_interruption_observed", False) is False,
                f"{role} baseline claims relay interruption",
            )
            require(
                receipt.get("relay_recovery_observed", False) is False,
                f"{role} baseline claims relay recovery",
            )
        if scenario == "proxy-restart":
            require(
                isinstance(initial_epoch, int)
                and isinstance(recovered_epoch, int)
                and recovered_epoch > initial_epoch,
                f"{role} proxy recovery did not advance the online epoch",
            )
            require(
                receipt.get("proxy_interruption_observed") is True,
                f"{role} did not observe proxy interruption",
            )
            require(
                receipt.get("proxy_recovery_observed") is True,
                f"{role} did not observe proxy recovery",
            )
        else:
            require(
                receipt.get("proxy_interruption_observed", False) is False
                and receipt.get("proxy_recovery_observed", False) is False,
                f"{role} non-proxy scenario claims a proxy lifecycle",
            )
        if scenario == "i2p-router-restart":
            require(
                isinstance(initial_epoch, int)
                and isinstance(recovered_epoch, int)
                and recovered_epoch > initial_epoch,
                f"{role} I2P router recovery did not advance the online epoch",
            )
            require(
                receipt.get("i2p_router_interruption_observed") is True
                and receipt.get("i2p_router_recovery_observed") is True,
                f"{role} did not observe the I2P router lifecycle",
            )
        else:
            require(
                receipt.get("i2p_router_interruption_observed", False) is False
                and receipt.get("i2p_router_recovery_observed", False) is False,
                f"{role} non-I2P-fault scenario claims an I2P router lifecycle",
            )
        if scenario == "i2p-service-restart":
            require(
                isinstance(initial_epoch, int)
                and isinstance(recovered_epoch, int)
                and recovered_epoch > initial_epoch,
                f"{role} I2P service recovery did not advance the online epoch",
            )
            require(
                receipt.get("i2p_service_interruption_observed") is True
                and receipt.get("i2p_service_recovery_observed") is True,
                f"{role} did not observe the I2P service lifecycle",
            )
        else:
            require(
                receipt.get("i2p_service_interruption_observed", False) is False
                and receipt.get("i2p_service_recovery_observed", False) is False,
                f"{role} non-I2P-service scenario claims a service lifecycle",
            )
        if scenario == "daemon-restart":
            require(
                receipt.get("daemon_replacement_observed") is True,
                f"{role} did not observe daemon replacement",
            )
            require(
                receipt.get("daemon_identity_preserved") is True,
                f"{role} did not preserve daemon identity",
            )
            require(
                receipt.get("fresh_session_after_daemon_restart") is True,
                f"{role} did not prove a fresh daemon session",
            )
            expected_restart_count = 1 if role == "device" else 0
            require(
                receipt.get("daemon_restart_count") == expected_restart_count,
                f"{role} daemon restart count mismatch",
            )
            if role == "client":
                require(
                    receipt.get("daemon_offline_observed") is True,
                    "stable client did not observe daemon offline",
                )
                require(
                    isinstance(initial_epoch, int)
                    and isinstance(recovered_epoch, int)
                    and recovered_epoch > initial_epoch,
                    "stable client online epoch did not advance",
                )
            else:
                require(
                    receipt.get("daemon_offline_observed") is False,
                    "restarted daemon claims remote-offline observation",
                )
                require(
                    isinstance(recovered_epoch, int) and recovered_epoch > 0,
                    "restarted daemon online epoch is invalid",
                )
        else:
            require(
                receipt.get("daemon_replacement_observed", False) is False,
                f"{role} non-daemon scenario claims daemon replacement",
            )
            require(
                receipt.get("daemon_restart_count", 0) == 0,
                f"{role} non-daemon scenario claims a daemon restart",
            )
        if scenario in {"link-interruption", "sync-file-disconnect"}:
            require(
                isinstance(initial_epoch, int)
                and isinstance(recovered_epoch, int)
                and recovered_epoch > initial_epoch,
                f"{role} recovered online epoch did not advance after link restoration",
            )
            require(
                receipt.get("link_interruption_observed") is True,
                f"{role} did not observe link interruption",
            )
            require(
                receipt.get("link_recovery_observed") is True,
                f"{role} did not observe link recovery",
            )
        else:
            require(
                receipt.get("link_interruption_observed", False) is False,
                f"{role} non-link scenario claims link interruption",
            )
            require(
                receipt.get("link_recovery_observed", False) is False,
                f"{role} non-link scenario claims link recovery",
            )
        if packet_loss_scenario:
            delivered = receipt.get("packet_loss_probe_delivered")
            missed = receipt.get("packet_loss_probe_missed")
            require(
                receipt.get("packet_loss_observed") is True
                and receipt.get("packet_loss_epoch_stable") is True
                and receipt.get("packet_loss_text_delivered") is True
                and receipt.get("packet_loss_restored_text_delivered") is True,
                f"{role} partial-loss continuity evidence is incomplete",
            )
            require(
                isinstance(initial_epoch, int)
                and initial_epoch > 0
                and recovered_epoch == initial_epoch,
                f"{role} online epoch changed under partial loss",
            )
            require(
                receipt.get("packet_loss_probe_count") == PACKET_LOSS_PROBE_COUNT
                and isinstance(delivered, int)
                and delivered > 0
                and isinstance(missed, int)
                and missed >= 0
                and delivered + missed == PACKET_LOSS_PROBE_COUNT
                and receipt.get("packet_loss_probe_send_errors") == 0,
                f"{role} partial-loss burst summary is invalid",
            )
            require(
                route != "direct-udp" or missed > 0,
                f"{role} direct-UDP burst did not expose a lossy-carrier miss",
            )
            report_relative = (
                f"{evidence_role}/live/workspace-export/guest-receipts/"
                "iotox/packet-loss-burst.tsv"
            )
            report = confined(proof_root, report_relative, report_relative)
            verify_packet_loss_report(report, delivered, missed)
        else:
            require(
                receipt.get("packet_loss_observed", False) is False
                and receipt.get("packet_loss_probe_count", 0) == 0
                and receipt.get("packet_loss_probe_delivered", 0) == 0
                and receipt.get("packet_loss_probe_missed", 0) == 0
                and receipt.get("packet_loss_probe_send_errors", 0) == 0
                and receipt.get("packet_loss_epoch_stable", False) is False
                and receipt.get("packet_loss_text_delivered", False) is False
                and receipt.get("packet_loss_restored_text_delivered", False)
                is False,
                f"{role} non-loss scenario claims partial-loss evidence",
            )
        if scenario in GUEST_RESTART_SCENARIOS:
            require(
                receipt.get("guest_restart_observed") is True,
                f"{role} did not observe guest restart",
            )
            require(
                receipt.get("guest_identity_preserved") is True,
                f"{role} did not preserve guest identity",
            )
            require(
                receipt.get("fresh_session_after_guest_restart") is True,
                f"{role} did not prove a fresh post-reboot session",
            )
            initial_boot = receipt.get("initial_guest_boot_id_sha256")
            recovered_boot = receipt.get("recovered_guest_boot_id_sha256")
            require(
                isinstance(initial_boot, str)
                and isinstance(recovered_boot, str)
                and SHA256.fullmatch(initial_boot) is not None
                and SHA256.fullmatch(recovered_boot) is not None,
                f"{role} boot-ID digest is invalid",
            )
            if role == "device":
                require(initial_boot != recovered_boot, "device boot ID did not change")
                require(
                    receipt.get("guest_offline_observed") is False,
                    "rebooted device claims stable-client offline observation",
                )
                require(
                    isinstance(recovered_epoch, int) and recovered_epoch > 0,
                    "rebooted device online epoch is invalid",
                )
            else:
                require(initial_boot == recovered_boot, "stable client boot ID changed")
                require(
                    receipt.get("guest_offline_observed") is True,
                    "stable client did not observe guest offline",
                )
                require(
                    isinstance(initial_epoch, int)
                    and isinstance(recovered_epoch, int)
                    and recovered_epoch > initial_epoch,
                    "stable client epoch did not advance after guest reboot",
                )
        else:
            require(
                receipt.get("guest_restart_observed", False) is False,
                f"{role} non-guest scenario claims guest restart",
            )
            require(
                receipt.get("guest_offline_observed", False) is False,
                f"{role} non-guest scenario claims guest offline observation",
            )
        require(
            receipt.get("mutable_authority_observed", False)
            is mutable_scenario
            and receipt.get("mutable_outgoing_succeeded", False)
            is mutable_scenario
            and receipt.get("mutable_incoming_succeeded", False)
            is mutable_scenario
            and receipt.get("mutable_provider_converged", False)
            is mutable_scenario
            and receipt.get("mutable_ownership_epoch", 0)
            == (1 if mutable_scenario else 0),
            f"{role} mutable profile-state boundary mismatch",
        )
        if scenario == "sync-tree-route-population" and role == "client":
            for policy in ("fixed", "adaptive"):
                resource_relative = (
                    "client/live/workspace-export/guest-receipts/iotox/"
                    f"sync-route-population-{policy}-resource.tsv"
                )
                resource = confined(
                    proof_root, resource_relative, resource_relative
                )
                verify_resource_interval(resource, role)
                require(
                    receipt.get(
                        f"sync_tree_route_population_{policy}_resource_sha256"
                    )
                    == digest(resource),
                    f"client {policy} synchronization resource digest mismatch",
                )
        if (
            scenario in SYNC_CONCURRENT_CANCEL_SCENARIOS
            and role == "client"
        ):
            resource_relative = (
                "client/live/workspace-export/guest-receipts/iotox/"
                "sync-route-concurrent-cancel-resource.tsv"
            )
            resource = confined(
                proof_root, resource_relative, resource_relative
            )
            verify_resource_interval(resource, role)
            require(
                receipt.get(
                    "sync_tree_route_concurrent_cancel_resource_sha256"
                )
                == digest(resource),
                "client concurrent-cancellation resource digest mismatch",
            )
        if (
            scenario in {
                "sync-tree-route-population-loss",
                "sync-tree-route-loss-admission",
            }
            and role == "client"
        ):
            resource_relative = (
                "client/live/workspace-export/guest-receipts/iotox/"
                "sync-route-population-loss-resource.tsv"
            )
            resource = confined(
                proof_root, resource_relative, resource_relative
            )
            verify_resource_interval(resource, role)
            require(
                receipt.get(
                    "sync_tree_route_population_loss_resource_sha256"
                )
                == digest(resource),
                "client route-population loss resource digest mismatch",
            )
        if (
            scenario == "sync-tree-route-startup-admission"
            and role == "client"
        ):
            resource_relative = (
                "client/live/workspace-export/guest-receipts/iotox/"
                "sync-route-startup-admission-resource.tsv"
            )
            resource = confined(
                proof_root, resource_relative, resource_relative
            )
            verify_resource_interval(resource, role)
            require(
                receipt.get(
                    "sync_tree_route_startup_admission_resource_sha256"
                )
                == digest(resource),
                "client route-startup admission resource digest mismatch",
            )
        if scenario == "sync-tree-route-throughput" and role == "client":
            for phase in (
                "fixed-a",
                "adaptive-a",
                "adaptive-b",
                "fixed-b",
            ):
                resource_relative = (
                    "client/live/workspace-export/guest-receipts/iotox/"
                    f"sync-route-throughput-{phase}-resource.tsv"
                )
                resource = confined(
                    proof_root, resource_relative, resource_relative
                )
                verify_resource_interval(resource, role)
                field = (
                    "sync_tree_route_throughput_"
                    f"{phase.replace('-', '_')}_resource_sha256"
                )
                require(
                    receipt.get(field) == digest(resource),
                    f"client route-throughput {phase} resource digest "
                    "mismatch",
                )
        if scenario in CONTENT_LANE_SCIENCE_SCENARIOS and role == "client":
            lane_science_phase_order = (
                (8, 4, 2, 1)
                if scenario == "sync-content-lane-science-reverse"
                else (1, 2, 4, 8)
            )
            lane_science_phase_order_text = ",".join(
                str(cap) for cap in lane_science_phase_order
            )
            summary_relative = (
                "client/live/workspace-export/guest-receipts/iotox/"
                "content-lane-science.tsv"
            )
            summary = confined(proof_root, summary_relative, summary_relative)
            summary_text = summary.read_text(encoding="ascii")
            summary_match = re.fullmatch(
                    r"schema\tiotox-content-lane-science-v1\n"
                    r"artifact-sha256\t[0-9a-f]{64}\n"
                    r"artifact-bytes\t8388608\n"
                    r"content-chunks\t([1-9][0-9]*)\n"
                    r"content-objects\t([1-9][0-9]*)\n"
                    rf"phase-order\t{lane_science_phase_order_text}\n"
                    r"columns\tcap\tduration-ms\tartifact-bps\tmax-active-lanes\tuser-cpu-ticks\tsystem-cpu-ticks\tresident-high-water-kib\ttransport-iterations\tresource-sha256\n"
                    + "".join(
                        rf"phase\t{cap}\t[1-9][0-9]*\t[1-9][0-9]*\t[1-9][0-9]*\t[0-9]+\t[0-9]+\t[1-9][0-9]*\t[1-9][0-9]*\t[0-9a-f]{{64}}\n"
                        for cap in lane_science_phase_order
                    ),
                    summary_text,
                )
            require(
                summary_match is not None,
                "client content-lane science summary is malformed",
            )
            summary_rows = summary_text.splitlines()[7:]
            require(
                len(summary_rows) == 4,
                "client content-lane science summary has wrong phase count",
            )
            for cap, row in zip(
                lane_science_phase_order, summary_rows, strict=True
            ):
                fields = row.split("\t")
                duration = int(fields[2])
                measured_bps = int(fields[3])
                active = int(fields[4])
                require(
                    fields[1] == str(cap)
                    and measured_bps
                    == (8 * 1024 * 1024 * 1000) // duration
                    and 1 <= active <= cap
                    and active
                    == receipt.get(
                        f"content_lane_science_cap_{cap}_active", 0
                    ),
                    f"client cap-{cap} content-lane summary is inconsistent",
                )
            require(
                receipt.get("content_lane_science_summary_sha256")
                == digest(summary),
                "client content-lane science summary digest mismatch",
            )
            for cap in (1, 2, 4, 8):
                resource_relative = (
                    "client/live/workspace-export/guest-receipts/iotox/"
                    f"content-lane-science-cap-{cap}-resource.tsv"
                )
                resource = confined(
                    proof_root, resource_relative, resource_relative
                )
                ratox_boundary = (
                    {
                        1: (0, 1),
                        2: (1, 1),
                        4: (1, 1),
                        8: (1, 0),
                    }[cap]
                    if scenario in {
                        "sync-content-ratox-latency-science",
                        "sync-content-ratox-cap-2-sla",
                    }
                    else (0, 0)
                )
                verify_resource_interval(
                    resource,
                    role,
                    ratox_active_boundary=ratox_boundary,
                )
                require(
                    receipt.get(
                        f"content_lane_science_cap_{cap}_resource_sha256"
                    )
                    == digest(resource),
                    f"client cap-{cap} content-lane resource digest mismatch",
                )
            if scenario in {
                "sync-content-ratox-latency-science",
                "sync-content-ratox-cap-2-sla",
            }:
                verify_content_ratox_latency(
                    proof_root,
                    receipt,
                    enforce_cap_2_sla=(
                        scenario == "sync-content-ratox-cap-2-sla"
                    ),
                )
            elif scenario == "sync-content-ratox-post-bulk-admission":
                verify_content_ratox_post_bulk_admission(
                    proof_root, receipt, connection
                )
        if scenario in RATOX_SCENARIOS:
            status_relative = (
                f"{evidence_role}/live/workspace-export/guest-receipts/"
                "iotox/ratox-agent-status.txt"
            )
            status_candidate = proof_root / status_relative
            if status_candidate.is_file():
                agent_status = confined(
                    proof_root, status_relative, status_relative
                )
                status_text = agent_status.read_text(encoding="ascii")
                verify_ratox_agent_status(status_text, role)
                require(
                    receipt.get("ratox_agent_status_sha256", "")
                    == digest(agent_status),
                    f"{role} Ratox agent status digest mismatch",
                )
                ratox_agent_statuses += 1
            else:
                require(
                    receipt.get("ratox_agent_status_sha256", "") == "",
                    f"{role} Ratox agent status receipt is unbacked",
                )
            resource_relative = (
                f"{evidence_role}/live/workspace-export/guest-receipts/"
                "iotox/ratox-resource-interval.tsv"
            )
            resource_candidate = proof_root / resource_relative
            if resource_candidate.is_file():
                resource = confined(
                    proof_root, resource_relative, resource_relative
                )
                verify_resource_interval(resource, role)
                require(
                    receipt.get("ratox_resource_interval_sha256", "")
                    == digest(resource),
                    f"{role} Ratox resource interval digest mismatch",
                )
                ratox_resource_intervals += 1
            else:
                require(
                    receipt.get("ratox_resource_interval_sha256", "") == "",
                    f"{role} Ratox resource interval receipt is unbacked",
                )
            require(
                receipt.get("ratox_idle_observed") is True
                and receipt.get("ratox_sample_count") == sample_count,
                f"{role} Ratox capture boundary is absent",
            )
            require(
                receipt.get("ratox_bulk_observed", False)
                is (bulk_stream_count != 0)
                and receipt.get("ratox_bulk_stream_count", 0)
                == bulk_stream_count
                and receipt.get("ratox_bulk_payload_bytes", 0)
                == (1073741824 if bulk_stream_count else 0),
                f"{role} Ratox bulk boundary is invalid",
            )
            require(
                receipt.get("ratox_stripe_route_count", 1) == stripe_route_count,
                f"{role} Ratox stripe route count is invalid",
            )
            route_restarts = receipt.get("ratox_stripe_route_restart_count", 0)
            injected_restarts = receipt.get(
                "ratox_stripe_injected_restart_count", 0
            )
            require(
                isinstance(route_restarts, int)
                and 0 <= route_restarts <= 7
                and isinstance(injected_restarts, int)
                and 0 <= injected_restarts <= route_restarts,
                f"{role} Ratox stripe restart counters are invalid",
            )
            require(
                injected_restarts
                == int(
                    scenario == "ratox-stripe-recovery-32" and role == "device"
                ),
                f"{role} Ratox injected stripe restart count is invalid",
            )
            require(
                receipt.get("ratox_stripe_live_fault_injected", False)
                is (live_stripe_loss and role == "device")
                and receipt.get("ratox_stripe_live_offline_observed", False)
                is (live_stripe_loss and role == "client")
                and receipt.get("ratox_stripe_live_recovery_observed", False)
                is live_stripe_loss
                and receipt.get("ratox_stripe_live_affected_transfer_count", 0)
                == (8 if live_stripe_loss else 0)
                and receipt.get("ratox_stripe_live_reassigned_transfer_count", 0)
                == 0,
                f"{role} Ratox live stripe-loss boundary is invalid",
            )
            observed_stripe_route_restarts += route_restarts
            observed_stripe_injected_restarts += injected_restarts
            if stripe_route_count == 4:
                stripe = receipt_path.parent / "ratox-stripe-routes.tsv"
                require(stripe.is_file(), f"{role} Ratox stripe route evidence is absent")
                stripe_lines = stripe.read_text(encoding="ascii").splitlines()
                require(
                    stripe_lines[:2]
                    == ["schema\tiotox-ratox-stripe-routes-v1", "route-count\t4"],
                    f"{role} Ratox stripe metadata is invalid",
                )
                route_rows = [line.split("\t") for line in stripe_lines[2:]]
                require(len(route_rows) == 4, f"{role} Ratox stripe routes are incomplete")
                route_hashes = []
                for lane, route_row in enumerate(route_rows):
                    require(
                        len(route_row) == 6
                        and route_row[:5]
                        == ["route", str(lane), "connection", "tcp", "peer-key-sha256"]
                        and SHA256.fullmatch(route_row[5]) is not None,
                        f"{role} Ratox stripe route {lane} is invalid",
                    )
                    route_hashes.append(route_row[5])
                require(len(set(route_hashes)) == 4, f"{role} Ratox stripe routes repeat")
                require(
                    route_hashes[0] == receipt.get("peer_key_sha256"),
                    f"{role} Ratox protected route is not route zero",
                )
            if role == "client":
                capture = receipt_path.parent / "ratox-controller-capture.tsv"
                require(capture.is_file(), "Ratox controller capture is absent")
                lines = capture.read_text(encoding="ascii").splitlines()
                require(
                    f"samples\t{sample_count}" in lines
                    and "schema\tiotox-ratox-terminal-probe-v1" in lines,
                    "Ratox controller capture metadata is invalid",
                )
                interval_lines = [
                    line for line in lines
                    if line.startswith("sample-interval-ms\t")
                ]
                if ratox_actual_tor_soak_scenario:
                    require(
                        interval_lines
                        == [
                            "sample-interval-ms\t"
                            f"{RATOX_ACTUAL_TOR_SOAK_INTERVAL_MS}"
                        ],
                        "Ratox actual-Tor soak interval is invalid",
                    )
                peer_commitments = [
                    line.split("\t", 1)[1]
                    for line in lines
                    if line.startswith("peer-public-key-sha256\t")
                ]
                require(
                    len(peer_commitments) == 1
                    and SHA256.fullmatch(peer_commitments[0]) is not None,
                    "Ratox controller peer commitment is invalid",
                )
                ratox_capture_peer_commitment = peer_commitments[0]
                rows = [line.split("\t") for line in lines if line.startswith("sample\t")]
                require(
                    len(rows) == sample_count,
                    "Ratox controller capture sample count mismatch",
                )
                previous_render = 0
                for ordinal, row in enumerate(rows, 1):
                    require(len(row) == 11, "Ratox controller sample shape is invalid")
                    values = [int(value) for value in row[1:5]]
                    require(values[0] == ordinal, "Ratox controller ordinal is invalid")
                    require(
                        previous_render <= values[1] < values[2] <= values[3],
                        "Ratox controller timestamps are invalid",
                    )
                    previous_render = values[3]
                    require(
                        int(row[7]) == int(row[6]) + 1
                        and int(row[9]) == int(row[8]) + 1,
                        "Ratox controller byte span is invalid",
                    )
                    if protected_route_scenario:
                        require(
                            values[3] - values[1] < 250_000,
                            "Ratox protected-route sample exceeded 250 ms",
                        )
                if ratox_actual_tor_soak_scenario:
                    require(
                        len({row[5] for row in rows}) == 1
                        and all(
                            int(current[6]) == int(previous[7])
                            and int(current[8]) == int(previous[9])
                            for previous, current in zip(rows, rows[1:])
                        )
                        and int(rows[-1][2]) - int(rows[0][2])
                        >= (RATOX_ACTUAL_TOR_SOAK_SAMPLES - 1)
                        * RATOX_ACTUAL_TOR_SOAK_INTERVAL_MS
                        * 1000,
                        "Ratox actual-Tor soak did not preserve one sustained "
                        "session/sequence timeline",
                    )
                ratox_capture_rows = rows
                heartbeat_path = receipt_path.parent / "ratox-heartbeat-capture.tsv"
                if (
                    ratox_impairment_scenario
                    or ratox_route_loss_scenario
                    or ratox_actual_tor_soak_scenario
                ):
                    require(heartbeat_path.is_file(),
                            "Ratox heartbeat capture is absent")
                    heartbeat_lines = heartbeat_path.read_text(
                        encoding="ascii"
                    ).splitlines()
                    require(
                        f"samples\t{sample_count}" in heartbeat_lines
                        and "schema\tiotox-ratox-heartbeat-probe-v1"
                        in heartbeat_lines,
                        "Ratox heartbeat capture metadata is invalid",
                    )
                    heartbeat_rows = [
                        line.split("\t") for line in heartbeat_lines
                        if line.startswith("sample\t")
                    ]
                    require(len(heartbeat_rows) == sample_count,
                            "Ratox heartbeat sample count mismatch")
                    ratox_heartbeat_rows = heartbeat_rows
                    previous_pong = 0
                    previous_activity_end = 0
                    for ordinal, (heartbeat_row, terminal_row) in enumerate(
                        zip(heartbeat_rows, rows), 1
                    ):
                        require(len(heartbeat_row) == 5,
                                "Ratox heartbeat sample shape is invalid")
                        require(int(heartbeat_row[1]) == ordinal,
                                "Ratox heartbeat ordinal is invalid")
                        started = int(heartbeat_row[2])
                        pong = int(heartbeat_row[3])
                        if ratox_cli_reconnect_scenario:
                            # The production client gate proves both a
                            # terminal byte and a healthy heartbeat interval
                            # in each generation.  Initial attach samples the
                            # byte first; resumed attach samples the heartbeat
                            # first, so accept either honest, non-overlapping
                            # order.  Older private-controller probes have a
                            # single fixed heartbeat-before-byte order.
                            terminal_started = int(terminal_row[2])
                            terminal_finished = int(terminal_row[4])
                            require(
                                previous_activity_end
                                <= min(terminal_started, started)
                                and terminal_started <= terminal_finished
                                and started < pong
                                and (
                                    terminal_finished <= started
                                    or pong <= terminal_started
                                ),
                                "Ratox production-CLI heartbeat timestamps "
                                "are invalid",
                            )
                            previous_activity_end = max(terminal_finished, pong)
                        else:
                            require(
                                previous_pong
                                <= started
                                < pong
                                <= int(terminal_row[2]),
                                "Ratox heartbeat timestamps are invalid",
                            )
                        require(pong - started < 30_000_000,
                                "Ratox heartbeat exceeded its probe deadline")
                        require(heartbeat_row[4] == terminal_row[5],
                                "Ratox heartbeat changed terminal session identity")
                        previous_pong = pong
                else:
                    require(not heartbeat_path.exists(),
                            "ordinary Ratox proof contains heartbeat science output")
                if bulk_stream_count:
                    observation = receipt_path.parent / "ratox-bulk-observation.tsv"
                    require(observation.is_file(), "Ratox bulk observation is absent")
                    records = {}
                    for line in observation.read_text(encoding="ascii").splitlines():
                        fields = line.split("\t")
                        require(len(fields) == 2, "Ratox bulk observation shape is invalid")
                        require(fields[0] not in records, "Ratox bulk observation key repeats")
                        records[fields[0]] = fields[1]
                    observation_schema = records.get("schema")
                    require(
                        observation_schema in {
                            "iotox-ratox-bulk-observation-v1",
                            "iotox-ratox-bulk-observation-v2",
                            "iotox-ratox-bulk-observation-v3",
                            "iotox-ratox-bulk-observation-v4",
                            "iotox-ratox-bulk-observation-v5",
                            "iotox-ratox-bulk-observation-v6",
                        }
                        and int(records.get("streams", "0")) == bulk_stream_count
                        and int(records.get("routes", "1")) == stripe_route_count
                        and int(records.get("streams-per-route", str(bulk_stream_count)))
                        == (8 if protected_live_loss else bulk_stream_count // stripe_route_count)
                        and int(records.get("payload-bytes-per-stream", "0")) == 1073741824
                        and int(records.get("progressed", "0"))
                        == bulk_stream_count - (8 if live_stripe_loss else 0)
                        and int(records.get("position-total", "0")) > 0,
                        "Ratox bulk observation did not prove concurrent progress",
                    )
                    surviving_streams = bulk_stream_count - (
                        8 if live_stripe_loss else 0
                    )
                    if observation_schema == "iotox-ratox-bulk-observation-v6":
                        verify_ratox_bulk_state_accounting(
                            records, bulk_stream_count, surviving_streams
                        )
                    else:
                        require(
                            int(records.get("active-before", "0"))
                            == bulk_stream_count
                            and int(records.get("active-after", "0"))
                            == surviving_streams,
                            "legacy Ratox bulk active-state accounting is invalid",
                        )
                    if observation_schema in {
                        "iotox-ratox-bulk-observation-v2",
                        "iotox-ratox-bulk-observation-v3",
                        "iotox-ratox-bulk-observation-v4",
                        "iotox-ratox-bulk-observation-v5",
                        "iotox-ratox-bulk-observation-v6",
                    }:
                        position_min = int(records.get("position-min", "0"))
                        position_max = int(records.get("position-max", "0"))
                        require(
                            int(records.get("progress-wait-ms", "-1")) >= 0
                            and position_min > 0
                            and position_max >= position_min
                            and int(records.get("position-total", "0"))
                            >= position_min
                            * (bulk_stream_count - (8 if live_stripe_loss else 0)),
                            "Ratox bulk fairness observation is invalid",
                        )
                    if observation_schema in {
                        "iotox-ratox-bulk-observation-v3",
                        "iotox-ratox-bulk-observation-v4",
                        "iotox-ratox-bulk-observation-v5",
                        "iotox-ratox-bulk-observation-v6",
                    }:
                        require(
                            int(records.get("cancel-retry-rounds", "0")) >= 1
                            and int(records.get("cancel-wait-ms", "-1")) >= 0,
                            "Ratox bulk cancellation observation is invalid",
                        )
                        require(
                            int(records.get("position-total", "0"))
                            <= position_max
                            * (bulk_stream_count - (8 if live_stripe_loss else 0)),
                            "Ratox bulk numeric range observation is invalid",
                        )
                    if protected_live_loss:
                        require(
                            observation_schema
                            in {
                                "iotox-ratox-bulk-observation-v5",
                                "iotox-ratox-bulk-observation-v6",
                            },
                            "Ratox live stripe-loss observation schema mismatch",
                        )
                    elif live_stripe_loss:
                        require(
                            observation_schema
                            in {
                                "iotox-ratox-bulk-observation-v4",
                                "iotox-ratox-bulk-observation-v6",
                            },
                            "Ratox live stripe-loss observation schema mismatch",
                        )
                    else:
                        require(
                            observation_schema
                            in {
                                "iotox-ratox-bulk-observation-v1",
                                "iotox-ratox-bulk-observation-v2",
                                "iotox-ratox-bulk-observation-v3",
                                "iotox-ratox-bulk-observation-v6",
                            },
                            "non-loss Ratox observation uses a loss schema",
                        )
                    if live_stripe_loss:
                        unaffected_expected = bulk_stream_count - 8
                        unaffected_state_valid = False
                        if observation_schema == "iotox-ratox-bulk-observation-v6":
                            unaffected_present = int(
                                records.get(
                                    "unaffected-present-after-offline", "-1"
                                )
                            )
                            unaffected_active = int(
                                records.get(
                                    "unaffected-active-after-offline", "-1"
                                )
                            )
                            unaffected_paused = int(
                                records.get(
                                    "unaffected-paused-after-offline", "-1"
                                )
                            )
                            unaffected_state_valid = (
                                unaffected_present == unaffected_expected
                                and unaffected_active >= 0
                                and unaffected_paused >= 0
                                and unaffected_active + unaffected_paused
                                == unaffected_present
                            )
                        else:
                            unaffected_state_valid = int(
                                records.get(
                                    "unaffected-active-after-offline", "0"
                                )
                            ) == unaffected_expected
                        require(
                            int(records.get("fault-route", "-1")) == 3
                            and int(records.get("faulted-streams", "0")) == 8
                            and unaffected_state_valid
                            and int(records.get("reassigned-streams", "-1"))
                            == 0,
                            "Ratox live stripe-loss transfer outcome is invalid",
                        )
                        if protected_live_loss:
                            require(
                                int(records.get("protected-route", "-1")) == 0
                                and int(records.get("bulk-routes", "0")) == 3
                                and int(records.get("protected-cpu", "-1")) == 0
                                and int(records.get("bulk-cpu", "-1")) == 1,
                                "Ratox protected route boundary is invalid",
                            )
                        cancel_attempts = int(records.get("cancel-attempts", "0"))
                        cancel_accepted = int(records.get("cancel-accepted", "-1"))
                        cancel_rejected = int(records.get("cancel-rejected", "-1"))
                        cancel_route_restarts = int(
                            records.get("cancel-route-restarts", "-1")
                        )
                        require(
                            cancel_attempts
                            >= unaffected_expected
                            and cancel_accepted >= 0
                            and cancel_rejected >= 0
                            and cancel_accepted + cancel_rejected == cancel_attempts,
                            "Ratox live stripe-loss cancellation outcome is invalid",
                        )
                        if protected_live_loss:
                            cleanup_mode = records.get("cancel-cleanup-mode")
                            require(
                                cancel_attempts == unaffected_expected
                                and (
                                    (
                                        cleanup_mode == "control"
                                        and cancel_rejected == 0
                                        and cancel_route_restarts == 0
                                    )
                                    or (
                                        cleanup_mode
                                        == "control-then-route-restart"
                                        and cancel_rejected > 0
                                        and 1 <= cancel_route_restarts <= 2
                                    )
                                ),
                                "Ratox protected-route cleanup outcome is invalid",
                            )
                        else:
                            require(
                                cancel_rejected == 0
                                and cancel_route_restarts == 0,
                                "Ratox shared-route cleanup outcome is invalid",
                            )
            else:
                events = receipt_path.parent / "ratox-host-events.txt"
                status = receipt_path.parent / "ratox-host-status.txt"
                require(events.is_file(), "Ratox host event capture is absent")
                require(status.is_file(), "Ratox host status capture is absent")
                text = events.read_text(encoding="ascii")
                require(
                    text.count(" kind=input-staged ") == sample_count
                    and text.count(" kind=input-committed ") == sample_count
                    and text.count(" kind=output-appended ") == sample_count,
                    "Ratox host event join population is incomplete",
                )
                parsed_events: list[dict[str, str]] = []
                previous_ordinal = 0
                for line in text.splitlines():
                    fields: dict[str, str] = {}
                    for token in line.split(" "):
                        key, separator, value = token.partition("=")
                        require(
                            bool(separator) and key not in fields and bool(value),
                            "Ratox host event record is not canonical",
                        )
                        fields[key] = value
                    try:
                        ordinal = int(fields["ordinal"])
                        steady_us = int(fields["steady-us"])
                    except (KeyError, ValueError) as error:
                        raise ValueError(
                            "Ratox host event coordinates are invalid"
                        ) from error
                    require(
                        ordinal == previous_ordinal + 1 and steady_us > 0,
                        "Ratox host event order is incomplete",
                    )
                    previous_ordinal = ordinal
                    parsed_events.append(fields)

                by_kind: dict[str, list[dict[str, str]]] = {
                    kind: [
                        event
                        for event in parsed_events
                        if event.get("kind") == kind
                    ]
                    for kind in (
                        "input-staged",
                        "input-committed",
                        "output-appended",
                    )
                }
                require(
                    all(len(values) == sample_count for values in by_kind.values()),
                    "Ratox host event kind population is incomplete",
                )
                require(
                    len(ratox_capture_rows) == sample_count,
                    "Ratox controller rows were not retained for host joining",
                )
                for row in ratox_capture_rows:
                    session_id = row[5].upper()
                    input_sequence, input_next = row[6], row[7]
                    output_sequence, output_next = row[8], row[9]
                    staged = [
                        event
                        for event in by_kind["input-staged"]
                        if event.get("session-id") == session_id
                        and event.get("sequence") == input_sequence
                        and event.get("next-sequence") == input_next
                    ]
                    committed = [
                        event
                        for event in by_kind["input-committed"]
                        if event.get("session-id") == session_id
                        and event.get("sequence") == input_sequence
                        and event.get("next-sequence") == input_next
                    ]
                    output = [
                        event
                        for event in by_kind["output-appended"]
                        if event.get("session-id") == session_id
                        and event.get("sequence") == output_sequence
                        and event.get("next-sequence") == output_next
                    ]
                    require(
                        len(staged) == len(committed) == len(output) == 1,
                        "Ratox controller sample lacks one exact host event join",
                    )
                    stage, commit, appended = staged[0], committed[0], output[0]
                    require(
                        stage.get("message-id") == commit.get("message-id")
                        and stage.get("message-id") not in {None, "0"}
                        and stage.get("frame-type") == "INPUT"
                        and commit.get("frame-type") == "INPUT"
                        and appended.get("frame-type") == "OUTPUT"
                        and stage.get("event-bytes") == "1"
                        and commit.get("event-bytes") == "1"
                        and appended.get("event-bytes") == "1"
                        and stage.get("error-code") == "0"
                        and commit.get("error-code") == "0"
                        and appended.get("error-code") == "0",
                        "Ratox joined host event semantics are invalid",
                    )
                    require(
                        int(stage["ordinal"])
                        < int(commit["ordinal"])
                        < int(appended["ordinal"])
                        and int(stage["steady-us"])
                        <= int(commit["steady-us"])
                        <= int(appended["steady-us"]),
                        "Ratox joined host event order is invalid",
                    )
                if receipt.get("c_toxcore_variant") in {
                    "iotox-file-rr1",
                    "iotox-file-rr1-tcp-connect120",
                }:
                    variant = receipt["c_toxcore_variant"]
                    require(
                        "backend=c-toxcore 0.2.23 loaded from "
                        f"linked:c-toxcore+{variant}"
                        in status.read_text(encoding="ascii"),
                        "patched c-toxcore runtime provenance is absent",
                    )
        else:
            require(
                receipt.get("ratox_idle_observed", False) is False
                and receipt.get("ratox_sample_count", 0) == 0,
                f"{role} non-Ratox scenario claims terminal samples",
            )
            require(
                receipt.get("ratox_bulk_observed", False) is False
                and receipt.get("ratox_bulk_stream_count", 0) == 0
                and receipt.get("ratox_bulk_payload_bytes", 0) == 0,
                f"{role} non-Ratox scenario claims bulk evidence",
            )
        if scenario in SYNC_SCENARIOS:
            cancellation = scenario in SYNC_CANCELLATION_SCENARIOS
            require(
                receipt.get("sync_authority_observed") is True
                and receipt.get("sync_convergence_observed")
                is (not cancellation)
                and receipt.get("sync_activation_observed")
                is (not cancellation)
                and receipt.get("sync_cancellation_observed", False)
                is cancellation,
                f"{role} synchronization boundary is incomplete",
            )
            expected_sync_generation = (
                3
                if scenario == "sync-tree-adversity"
                else 2 if scenario in SYNC_RANGE_SCENARIOS else 1
            )
            require(
                receipt.get("sync_generation") == expected_sync_generation
                and receipt.get("sync_artifact_bytes")
                == SYNC_SCENARIOS[scenario]
                and isinstance(receipt.get("sync_manifest_bytes"), int)
                and 0 < receipt["sync_manifest_bytes"] <= 1048576,
                f"{role} synchronization revision shape is invalid",
            )
            for field in (
                "sync_artifact_sha256",
                "sync_manifest_sha256",
                "sync_head_record",
            ):
                require(
                    SHA256.fullmatch(str(receipt.get(field, ""))) is not None,
                    f"{role} {field} is invalid",
                )
            if scenario in CONTENT_MULTI_SOURCE_SCENARIOS:
                require(
                    receipt.get("multi_source_count") == 2
                    and (
                        receipt.get("multi_source_atomic_pull_observed") is True
                        if atomic_multi_source
                        else "multi_source_atomic_pull_observed" not in receipt
                    )
                    and isinstance(
                        receipt.get("multi_source_availability_requests"), int
                    )
                    and receipt["multi_source_availability_requests"] >= 2
                    and receipt.get("multi_source_availability_results")
                    == receipt["multi_source_availability_requests"]
                    and SHA256.fullmatch(
                        str(
                            receipt.get(
                                "multi_source_secondary_key_sha256", ""
                            )
                        )
                    )
                    is not None
                    and SHA256.fullmatch(
                        str(
                            receipt.get(
                                "multi_source_secondary_principal_sha256", ""
                            )
                        )
                    )
                    is not None
                    and (
                        role != "device"
                        or (
                            receipt.get("multi_source_primary_objects", 0) > 1
                            and receipt.get(
                                "multi_source_secondary_objects", 0
                            )
                            > 0
                        )
                    ),
                    f"{role} multi-source content receipt is invalid",
                )
                routed_multi_source = scenario in {
                    "sync-content-multi-route-actual-tor",
                    "sync-content-multi-route-actual-tor-loss",
                }
                require(
                    receipt.get(
                        "multi_source_auxiliary_carrier_count", 0
                    )
                    == (2 if routed_multi_source and role == "client" else 0)
                    and (
                        SHA256.fullmatch(
                            str(
                                receipt.get(
                                    "multi_source_auxiliary_carriers_sha256",
                                    "",
                                )
                            )
                        )
                        is not None
                        if routed_multi_source and role == "client"
                        else receipt.get(
                            "multi_source_auxiliary_carriers_sha256", ""
                        )
                        == ""
                    ),
                    f"{role} routed multi-source receipt is invalid",
                )
                native_loss = scenario == "sync-content-multi-source-loss"
                route_loss = (
                    scenario == "sync-content-multi-route-actual-tor-loss"
                )
                loss = native_loss or route_loss
                require(
                    receipt.get("multi_source_loss_observed", False) is loss
                    and receipt.get(
                        "multi_source_loss_recovery_observed", False
                    )
                    is loss
                    and receipt.get("multi_source_loss_restart_count", 0)
                    == (1 if loss else 0)
                    and receipt.get(
                        "multi_source_loss_staging_clean", False
                    )
                    is loss
                    and receipt.get(
                        "multi_source_loss_head_fenced", False
                    )
                    is loss
                    and receipt.get(
                        "multi_source_loss_activation_fenced", False
                    )
                    is loss
                    and (
                        receipt.get("multi_source_loss_first_job_id", 0) > 0
                        and receipt.get(
                            "multi_source_loss_replacement_job_id", 0
                        )
                        > 0
                        and receipt["multi_source_loss_first_job_id"]
                        != receipt["multi_source_loss_replacement_job_id"]
                        and receipt.get(
                            "multi_source_loss_committed_objects", 0
                        )
                        > 0
                        and receipt.get(
                            "multi_source_loss_fetched_bytes", 0
                        )
                        > 0
                        and receipt.get(
                            "multi_source_loss_initial_epoch", 0
                        )
                        > 0
                        and (
                            receipt.get(
                                "multi_source_loss_recovered_epoch", 0
                            )
                            > receipt["multi_source_loss_initial_epoch"]
                            if native_loss
                            else receipt.get(
                                "multi_source_loss_recovered_epoch", 0
                            )
                            == receipt["multi_source_loss_initial_epoch"]
                        )
                        if loss
                        else receipt.get(
                            "multi_source_loss_first_job_id", 0
                        )
                        == 0
                        and receipt.get(
                            "multi_source_loss_replacement_job_id", 0
                        )
                        == 0
                        and receipt.get(
                            "multi_source_loss_committed_objects", 0
                        )
                        == 0
                        and receipt.get(
                            "multi_source_loss_fetched_bytes", 0
                        )
                        == 0
                        and receipt.get(
                            "multi_source_loss_initial_epoch", 0
                        )
                        == 0
                        and receipt.get(
                            "multi_source_loss_recovered_epoch", 0
                        )
                        == 0
                    ),
                    f"{role} selected-source loss receipt is invalid",
                )
                require(
                    receipt.get(
                        "multi_source_route_loss_observed", False
                    )
                    is route_loss
                    and (
                        re.fullmatch(
                            r"[0-9A-F]{64}",
                            str(
                                receipt.get(
                                    "multi_source_route_loss_target", ""
                                )
                            ),
                        )
                        is not None
                        and receipt.get(
                            "multi_source_route_loss_fault_worker", 0
                        )
                        > 0
                        and receipt.get(
                            "multi_source_route_loss_recovered_worker", 0
                        )
                        > 0
                        and receipt[
                            "multi_source_route_loss_fault_worker"
                        ]
                        != receipt[
                            "multi_source_route_loss_recovered_worker"
                        ]
                        and receipt.get(
                            "multi_source_route_loss_position_bytes", 0
                        )
                        >= 65_536
                        and receipt.get(
                            "multi_source_route_loss_carrier_losses", 0
                        )
                        == 1
                        and receipt.get(
                            "multi_source_route_loss_reassignments", -1
                        )
                        == 0
                        and receipt.get(
                            "multi_source_route_loss_recoveries", 0
                        )
                        == 1
                        and receipt.get(
                            "multi_source_route_loss_primary_epoch", 0
                        )
                        > 0
                        and receipt.get(
                            "multi_source_route_loss_secondary_epoch", 0
                        )
                        > 0
                        if route_loss
                        else receipt.get(
                            "multi_source_route_loss_target", ""
                        )
                        == ""
                        and receipt.get(
                            "multi_source_route_loss_fault_worker", 0
                        )
                        == 0
                        and receipt.get(
                            "multi_source_route_loss_recovered_worker", 0
                        )
                        == 0
                        and receipt.get(
                            "multi_source_route_loss_position_bytes", 0
                        )
                        == 0
                        and receipt.get(
                            "multi_source_route_loss_carrier_losses", 0
                        )
                        == 0
                        and receipt.get(
                            "multi_source_route_loss_reassignments", 0
                        )
                        == 0
                        and receipt.get(
                            "multi_source_route_loss_recoveries", 0
                        )
                        == 0
                        and receipt.get(
                            "multi_source_route_loss_primary_epoch", 0
                        )
                        == 0
                        and receipt.get(
                            "multi_source_route_loss_secondary_epoch", 0
                        )
                        == 0
                    ),
                    f"{role} exact routed source-loss receipt is invalid",
                )
            if scenario == "sync-content-same-source-lanes":
                lane_digest = receipt.get("same_source_lane_set_sha256", "")
                require(
                    receipt.get("same_source_lanes_observed", False)
                    is (role == "client")
                    and receipt.get("same_source_lane_cap", 0)
                    == (2 if role == "client" else 0)
                    and receipt.get("same_source_active_lanes", 0)
                    == (2 if role == "client" else 0)
                    and receipt.get("same_source_admitted_lanes", 0)
                    == (2 if role == "client" else 0)
                    and receipt.get("same_source_distinct_requests", 0)
                    == (2 if role == "client" else 0)
                    and receipt.get("same_source_distinct_files", 0)
                    == (2 if role == "client" else 0)
                    and receipt.get("same_source_source_count", 0)
                    == (1 if role == "client" else 0)
                    and receipt.get("same_source_root_lane_count", 0) == 0
                    and (
                        SHA256.fullmatch(str(lane_digest)) is not None
                        if role == "client"
                        else lane_digest == ""
                    ),
                    f"{role} same-source content-lane receipt is invalid",
                )
            if scenario in CONTENT_LANE_SCIENCE_SCENARIOS:
                science = role == "client"
                lane_science_phase_order = (
                    "8,4,2,1"
                    if scenario == "sync-content-lane-science-reverse"
                    else "1,2,4,8"
                )
                require(
                    receipt.get("content_lane_science_observed", False)
                    is science
                    and receipt.get("content_lane_science_phase_order", "")
                    == (lane_science_phase_order if science else "")
                    and receipt.get("content_lane_science_artifact_bytes", 0)
                    == (8 * 1024 * 1024 if science else 0)
                    and receipt.get("content_lane_science_chunks", 0)
                    >= (8 if science else 0)
                    and receipt.get("content_lane_science_objects", 0)
                    >= (10 if science else 0)
                    and receipt.get("content_lane_science_restart_count", 0)
                    == 0
                    and receipt.get("content_lane_science_activation_count", 0)
                    == (4 if science else 0),
                    f"{role} content-lane science receipt is invalid",
                )
                for cap in (1, 2, 4, 8):
                    duration = receipt.get(
                        f"content_lane_science_cap_{cap}_duration_ms", 0
                    )
                    measured_bps = receipt.get(
                        f"content_lane_science_cap_{cap}_bps", 0
                    )
                    active = receipt.get(
                        f"content_lane_science_cap_{cap}_active", 0
                    )
                    resource_digest = receipt.get(
                        f"content_lane_science_cap_{cap}_resource_sha256", ""
                    )
                    require(
                        (
                            isinstance(duration, int)
                            and duration > 0
                            and isinstance(measured_bps, int)
                            and measured_bps
                            == (8 * 1024 * 1024 * 1000) // duration
                            and isinstance(active, int)
                            and 1 <= active <= cap
                            and SHA256.fullmatch(str(resource_digest))
                            is not None
                            if science
                            else duration == 0
                            and measured_bps == 0
                            and active == 0
                            and resource_digest == ""
                        ),
                        f"{role} cap-{cap} content-lane receipt is invalid",
                    )
                summary_digest = receipt.get(
                    "content_lane_science_summary_sha256", ""
                )
                require(
                    (
                        SHA256.fullmatch(str(summary_digest)) is not None
                        if science
                        else summary_digest == ""
                    ),
                    f"{role} content-lane summary commitment is invalid",
                )
                post_bulk = (
                    scenario == "sync-content-ratox-post-bulk-admission"
                    and role == "client"
                )
                require(
                    receipt.get("content_ratox_post_bulk_observed", False)
                    is post_bulk
                    and receipt.get("content_ratox_post_bulk_cap", 0)
                    == (8 if post_bulk else 0)
                    and receipt.get("content_ratox_post_bulk_samples", 0)
                    == (40 if post_bulk else 0)
                    and (
                        receipt.get("content_ratox_post_bulk_origin_us", 0) > 0
                        if post_bulk
                        else receipt.get("content_ratox_post_bulk_origin_us", 0)
                        == 0
                    )
                    and (
                        0
                        <= receipt.get(
                            "content_ratox_post_bulk_origin_to_open_sent_us", -1
                        )
                        <= 1_000_000
                        if post_bulk
                        else receipt.get(
                            "content_ratox_post_bulk_origin_to_open_sent_us", 0
                        )
                        == 0
                    )
                    and (
                        0
                        < receipt.get(
                            "content_ratox_post_bulk_origin_to_opened_us", 0
                        )
                        <= 6_000_000
                        if post_bulk
                        else receipt.get(
                            "content_ratox_post_bulk_origin_to_opened_us", 0
                        )
                        == 0
                    )
                    and (
                        0
                        < receipt.get(
                            "content_ratox_post_bulk_open_round_trip_us", 0
                        )
                        <= 5_000_000
                        if post_bulk
                        else receipt.get(
                            "content_ratox_post_bulk_open_round_trip_us", 0
                        )
                        == 0
                    )
                    and (
                        receipt.get("content_ratox_post_bulk_online_epoch", 0) > 0
                        if post_bulk
                        else receipt.get(
                            "content_ratox_post_bulk_online_epoch", 0
                        )
                        == 0
                    ),
                    f"{role} fresh post-bulk Ratox receipt is invalid",
                )
                for field in (
                    "readiness_sha256",
                    "capture_sha256",
                    "admission_sha256",
                ):
                    value = receipt.get(f"content_ratox_post_bulk_{field}", "")
                    require(
                        (
                            SHA256.fullmatch(str(value)) is not None
                            if post_bulk
                            else value == ""
                        ),
                        f"{role} fresh post-bulk Ratox {field} is invalid",
                    )
            signed_update = scenario in SIGNED_UPDATE_SCENARIOS
            update_service = scenario == "update-service"
            require(
                receipt.get("signed_update_observed", False)
                is signed_update
                and receipt.get("signed_update_release_sequence", 0)
                == (1 if signed_update else 0)
                and receipt.get("signed_update_confirmed", False)
                is signed_update
                and receipt.get("signed_update_restart_count", 0)
                == (6 if update_service else 1 if signed_update else 0)
                and receipt.get("signed_update_feature_advertised", False)
                is signed_update
                and receipt.get("signed_update_remote_stage_observed", False)
                is signed_update
                and isinstance(receipt.get("signed_update_sender_epoch", 0), int)
                and (
                    receipt.get("signed_update_sender_epoch", 0) > 0
                    if signed_update
                    else receipt.get("signed_update_sender_epoch", 0) == 0
                )
                and isinstance(receipt.get("signed_update_message_id", 0), int)
                and (
                    receipt.get("signed_update_message_id", 0) > 0
                    if signed_update
                    else receipt.get("signed_update_message_id", 0) == 0
                )
                and receipt.get("signed_update_startup_disposition", "")
                == ("health-window-opened" if signed_update else ""),
                f"{role} signed-update lifecycle boundary is invalid",
            )
            require(
                receipt.get(
                    "update_service_pre_ready_exit_observed", False
                )
                is update_service
                and receipt.get(
                    "update_service_agent_death_observed", False
                )
                is update_service
                and receipt.get(
                    "update_service_parent_death_observed", False
                )
                is update_service
                and receipt.get(
                    "update_service_health_expiry_observed", False
                )
                is update_service
                and receipt.get("update_service_ready_observed", False)
                is update_service
                and receipt.get(
                    "update_service_confirmed_recovery_observed", False
                )
                is update_service
                and receipt.get("update_service_rollback_count", 0)
                == (3 if update_service else 0)
                and receipt.get("update_service_payload_kind", "")
                == ("linux-service-v1" if update_service else "")
                and receipt.get("update_service_image_sealed", False)
                is update_service,
                f"{role} linux-service update lifecycle boundary is invalid",
            )
            for field in (
                "signed_update_payload_sha256",
                "signed_update_manifest_record",
                "signed_update_current_sha256",
            ):
                value = receipt.get(field, "")
                require(
                    (
                        SHA256.fullmatch(value) is not None
                        if signed_update
                        else value == ""
                    ),
                    f"{role} {field} is invalid",
                )
            if signed_update:
                require(
                    receipt["signed_update_payload_sha256"]
                    == receipt["signed_update_current_sha256"],
                    f"{role} activated update payload digest differs",
                )
            tree_scenario = scenario in SYNC_TREE_SCENARIOS
            expected_tree_content_bytes = (
                131_157
                if scenario in {
                    "sync-tree-route-population",
                    "sync-tree-route-population-loss",
                    "sync-tree-route-loss-admission",
                    "sync-tree-route-startup-admission",
                    "sync-tree-route-throughput",
                    "sync-tree-route-concurrent-cancel",
                    "sync-tree-route-common-link-fairness",
                }
                else 16_777_301
                if scenario == "sync-tree-route-private-actual-tor-loss"
                else 131_157
                if scenario
                in {
                    "sync-tree-route-private-actual-i2p-payload",
                    "sync-tree-route-private-actual-i2p-loss",
                }
                else 4_194_389 if tree_scenario else 0
            )
            require(
                receipt.get("sync_tree_observed", False) is tree_scenario
                and receipt.get("sync_tree_directories", 0)
                == (3 if tree_scenario else 0)
                and receipt.get("sync_tree_files", 0)
                == (3 if tree_scenario else 0)
                and receipt.get("sync_tree_content_bytes", 0)
                == expected_tree_content_bytes
                and (
                    SHA256.fullmatch(
                        str(receipt.get("sync_tree_payload_sha256", ""))
                    )
                    is not None
                    if tree_scenario
                    else receipt.get("sync_tree_payload_sha256", "") == ""
                ),
                f"{role} deterministic tree evidence is invalid",
            )
            route_loss_scenario = scenario in SYNC_ROUTE_LOSS_SCENARIOS
            route_loss_observer = route_loss_scenario and role == "client"
            repeated_range_loss_count = REPEATED_RANGE_LOSS_COUNTS.get(
                scenario, 0
            )
            repeated_range_loss_observer = (
                repeated_range_loss_count != 0 and role == "client"
            )
            late_range_loss_observer = (
                scenario == "sync-file-range-late-route-loss"
                and role == "client"
            )
            expected_route_loss_count = (
                repeated_range_loss_count
                if repeated_range_loss_observer
                else int(route_loss_observer)
            )
            require(
                receipt.get("sync_qualification_deferred_frames", 0)
                == 0
                and receipt.get(
                    "sync_qualification_deferred_frame_releases", 0
                )
                == (
                    repeated_range_loss_count - 1
                    if repeated_range_loss_observer
                    else 0
                ),
                f"{role} qualification request-hold evidence is invalid",
            )
            cancel_before_loss_observer = (
                scenario == "sync-tree-route-cancel-loss"
                and role == "client"
            )
            cancel_loss_race_observer = (
                scenario in SYNC_ROUTE_CANCEL_RACE_SCENARIOS
                and role == "client"
            )
            race_fault_delay, race_cancel_delay, required_race_outcome = (
                SYNC_ROUTE_CANCEL_RACE_SCENARIOS.get(
                    scenario, (0, 0, None)
                )
            )
            route_loss_reassignments = receipt.get(
                "sync_tree_route_loss_reassignments", 0
            )
            route_loss_position = receipt.get(
                "sync_tree_route_loss_position_bytes", 0
            )
            final_carrier = receipt.get(
                "sync_tree_route_loss_final_carrier", ""
            )
            stopped_carrier = receipt.get(
                "sync_tree_route_loss_stopped_carrier", ""
            )
            require(
                receipt.get("sync_tree_route_loss_observed", False)
                is route_loss_observer
                and (
                    route_loss_position == 0
                    if cancel_before_loss_observer
                    else (983_040 if late_range_loss_observer else 65_536)
                    <= route_loss_position
                    < SYNC_SCENARIOS[scenario]
                    if route_loss_observer
                    else route_loss_position == 0
                )
                and receipt.get("sync_tree_route_loss_carrier_losses", 0)
                == expected_route_loss_count
                and (
                    route_loss_reassignments in {0, 1}
                    if cancel_loss_race_observer
                    else route_loss_reassignments
                    == (
                        expected_route_loss_count
                        if not cancel_before_loss_observer
                        else 0
                    )
                )
                and (
                    receipt.get("sync_tree_route_loss_stale_terminals", -1)
                    >= (
                        0
                        if cancel_loss_race_observer
                        else expected_route_loss_count
                    )
                    if route_loss_observer
                    else receipt.get(
                        "sync_tree_route_loss_stale_terminals", 0
                    )
                    == 0
                )
                and receipt.get("sync_tree_route_loss_recoveries", 0)
                == expected_route_loss_count
                and (
                    receipt.get("sync_tree_route_loss_worker_restarts", 0)
                    == expected_route_loss_count
                    if repeated_range_loss_observer
                    else True
                )
                and receipt.get(
                    "sync_tree_route_cancel_loss_observed", False
                )
                is cancel_before_loss_observer
                and receipt.get(
                    "sync_tree_route_cancel_race_observed", False
                )
                is cancel_loss_race_observer
                and receipt.get(
                    "sync_tree_route_cancel_race_outcome", ""
                )
                in (
                    {"cancel-first", "loss-first"}
                    if scenario in SYNC_ROUTE_CANCEL_RACE_SCENARIOS
                    else {""}
                )
                and (
                    required_race_outcome is None
                    or receipt.get(
                        "sync_tree_route_cancel_race_outcome", ""
                    )
                    == required_race_outcome
                )
                and receipt.get(
                    "sync_tree_route_cancel_race_fault_delay_ms", 0
                )
                == (
                    race_fault_delay
                )
                and receipt.get(
                    "sync_tree_route_cancel_race_cancel_delay_ms", 0
                )
                == (
                    race_cancel_delay
                )
                and receipt.get(
                    "sync_tree_route_cancel_race_cleanup_retries", 0
                )
                in (
                    {0, 1}
                    if scenario in SYNC_ROUTE_CANCEL_RACE_SCENARIOS
                    else {0}
                )
                and receipt.get("sync_tree_route_ready_bulk", 0)
                == (2 if scenario in MULTI_ROUTE_SYNC_SCENARIOS else 0)
                and (
                    re.fullmatch(r"[0-9A-F]{64}", str(final_carrier))
                    is not None
                    and re.fullmatch(r"[0-9A-F]{64}", str(stopped_carrier))
                    is not None
                    and (
                        final_carrier == stopped_carrier
                        if repeated_range_loss_count == 2 or
                        cancel_before_loss_observer or
                        cancel_loss_race_observer and
                        route_loss_reassignments == 0
                        else final_carrier != stopped_carrier
                    )
                    if route_loss_observer
                    else final_carrier == "" and stopped_carrier == ""
                ),
                f"{role} deterministic route-loss evidence is invalid",
            )
            signed_network_classes = receipt.get(
                "signed_route_network_classes_observed"
            )
            require(
                signed_network_classes is None
                or signed_network_classes
                is (scenario in MULTI_ROUTE_SYNC_SCENARIOS),
                f"{role} signed route network-class evidence is invalid",
            )
            verify_route_resume(
                receipt,
                role == "client"
                and scenario
                in {
                    "sync-tree-route-loss",
                    "sync-tree-route-private-actual-tor-loss",
                    "sync-file-range-route-loss",
                    "sync-file-range-late-route-loss",
                    "sync-file-range-repeated-route-loss",
                    "sync-file-range-triple-route-loss",
                },
                f"{role} synchronization",
                repeated_range_loss_count
                if repeated_range_loss_observer
                else None,
            )
            if actual_tor_loss and role == "client":
                process_loss = manifest["actual_tor_process_loss"]
                require(
                    route_loss_position == process_loss["position_bytes"]
                    and stopped_carrier
                    == process_loss["stopped_carrier"]
                    and final_carrier
                    == process_loss["replacement_carrier"]
                    and receipt.get(
                        "sync_tree_route_loss_worker_restarts"
                    )
                    == process_loss["route_worker_restarts"]
                    == 0
                    and hashlib.sha256(
                        stopped_carrier.encode("ascii")
                    ).hexdigest()
                    == receipt.get(
                        "private_route_auxiliary_key_sha256", ""
                    )
                    == process_loss["stopped_carrier_sha256"],
                    "actual-Tor process loss is not bound to the guest carrier",
                )
            verify_route_startup_order_receipt(
                receipt,
                scenario == "sync-tree-route-startup-order",
                f"{role} synchronization",
            )
            verify_route_balance_summary(
                receipt,
                scenario == "sync-tree-route-balance" and role == "client",
                f"{role} synchronization",
            )
            verify_route_population_summary(
                receipt,
                scenario == "sync-tree-route-population"
                and role == "client",
                f"{role} synchronization",
            )
            verify_route_concurrent_cancel_summary(
                receipt,
                scenario in SYNC_CONCURRENT_CANCEL_SCENARIOS
                and role == "client",
                f"{role} synchronization",
                SYNC_CONCURRENT_CANCEL_ARTIFACT_BYTES.get(
                    scenario, 262_211
                ),
            )
            verify_route_population_loss_summary(
                receipt,
                scenario in {
                    "sync-tree-route-population-loss",
                    "sync-tree-route-loss-admission",
                }
                and role == "client",
                f"{role} synchronization",
                scenario == "sync-tree-route-loss-admission",
            )
            verify_route_startup_admission_summary(
                receipt,
                scenario == "sync-tree-route-startup-admission"
                and role == "client",
                f"{role} synchronization",
            )
            verify_route_throughput_summary(
                receipt,
                scenario == "sync-tree-route-throughput"
                and role == "client",
                f"{role} synchronization",
            )
            route_cancel_scenario = scenario in {
                "sync-tree-route-cancel",
                "sync-tree-route-loss-cancel",
                "sync-tree-route-cancel-loss",
                "sync-tree-route-cancel-race",
                "sync-tree-route-cancel-race-loss-first",
            }
            route_loss_cancel_scenario = (
                scenario == "sync-tree-route-loss-cancel"
            )
            route_cancel_race_scenario = (
                scenario in SYNC_ROUTE_CANCEL_RACE_SCENARIOS
            )
            route_cancel_reassignments = receipt.get(
                "sync_tree_route_cancel_reassignments_delta", 0
            )
            route_cancel_carrier = receipt.get(
                "sync_tree_route_cancel_carrier", ""
            )
            require(
                receipt.get("sync_tree_route_cancel_observed", False)
                is route_cancel_scenario
                and (
                    re.fullmatch(r"[0-9A-F]{64}", route_cancel_carrier)
                    is not None
                    and receipt.get("sync_tree_route_cancel_worker_id", 0) > 0
                    and 0
                    <= receipt.get("sync_tree_route_cancel_tail_ms", -1)
                    <= 5000
                    and receipt.get("sync_tree_route_cancel_work_before", 0)
                    > 0
                    and receipt.get("sync_tree_route_cancel_work_after", -1)
                    == 0
                    and receipt.get(
                        "sync_tree_route_cancel_reassignments_delta", -1
                    )
                    in ({0, 1} if route_cancel_race_scenario else {0})
                    and receipt.get(
                        "sync_tree_route_cancel_adaptive_selections", 0
                    )
                    == (
                        1 + route_cancel_reassignments
                        if route_cancel_race_scenario
                        else 2 if route_loss_cancel_scenario else 1
                    )
                    if route_cancel_scenario
                    else route_cancel_carrier == ""
                    and receipt.get("sync_tree_route_cancel_worker_id", 0) == 0
                    and receipt.get("sync_tree_route_cancel_tail_ms", 0) == 0
                    and receipt.get("sync_tree_route_cancel_work_before", 0)
                    == 0
                    and receipt.get("sync_tree_route_cancel_work_after", 0) == 0
                    and receipt.get(
                        "sync_tree_route_cancel_reassignments_delta", 0
                    )
                    == 0
                    and receipt.get(
                        "sync_tree_route_cancel_adaptive_selections", 0
                    )
                    == 0
                ),
                f"{role} deterministic route-cancellation evidence is invalid",
            )
            if route_loss_cancel_scenario and role == "client":
                verify_loss_before_cancel_order(
                    receipt, f"{role} synchronization"
                )
            if cancel_before_loss_observer:
                verify_cancel_before_loss_order(
                    receipt, f"{role} synchronization"
                )
            if cancel_loss_race_observer:
                verify_cancel_loss_race_order(
                    receipt,
                    f"{role} synchronization",
                    race_fault_delay,
                    race_cancel_delay,
                    required_race_outcome,
                )
            admission_scenario = scenario == "sync-tree-admission"
            require(
                receipt.get("sync_tree_admission_observed", False)
                is admission_scenario
                and receipt.get("sync_tree_admission_receive_limit", 0)
                == (1 if admission_scenario else 0)
                and (
                    receipt.get("sync_tree_admission_retry_count", 0) > 0
                    if admission_scenario
                    else receipt.get("sync_tree_admission_retry_count", 0) == 0
                )
                and receipt.get("sync_tree_admission_admitted_offers", 0)
                == (2 if admission_scenario else 0)
                and receipt.get("sync_tree_admission_pending_offers", 0) == 0,
                f"{role} synchronization receive-admission evidence is invalid",
            )
            adversity_scenario = scenario == "sync-tree-adversity"
            require(
                receipt.get("sync_tree_rollback_refused", False)
                is adversity_scenario
                and receipt.get("sync_tree_fork_refused", False)
                is adversity_scenario
                and receipt.get("sync_tree_enospc_observed", False)
                is adversity_scenario
                and receipt.get("sync_tree_enospc_retry_observed", False)
                is adversity_scenario
                and receipt.get("sync_tree_publisher_restart_count", 0)
                == (4 if adversity_scenario else 0)
                and (
                    receipt.get("sync_tree_enospc_reserved_bytes", 0)
                    > SYNC_SCENARIOS[scenario]
                    if adversity_scenario
                    else receipt.get("sync_tree_enospc_reserved_bytes", 0) == 0
                )
                and (
                    0
                    <= receipt.get("sync_tree_enospc_failure_free_bytes", -1)
                    < SYNC_SCENARIOS[scenario]
                    if adversity_scenario
                    else receipt.get("sync_tree_enospc_failure_free_bytes", 0) == 0
                ),
                f"{role} deterministic tree adversity evidence is invalid",
            )
            pressure_scenario = scenario == "sync-tree-pressure"
            pressure_a = receipt.get("sync_tree_pressure_a_head_record", "")
            pressure_b = receipt.get("sync_tree_pressure_b_head_record", "")
            require(
                receipt.get("sync_tree_queue_saturation_observed", False)
                is pressure_scenario
                and receipt.get("sync_tree_queue_retry_observed", False)
                is pressure_scenario
                and receipt.get("sync_tree_worker_queue_bound", 0)
                == (1 if pressure_scenario else 0)
                and receipt.get("sync_tree_worker_active_at_saturation", 0)
                == (1 if pressure_scenario else 0)
                and receipt.get("sync_tree_worker_queued_at_saturation", 0)
                == (1 if pressure_scenario else 0)
                and receipt.get("sync_tree_worker_rejected_delta", 0)
                == (1 if pressure_scenario else 0)
                and (
                    SHA256.fullmatch(str(pressure_a)) is not None
                    and SHA256.fullmatch(str(pressure_b)) is not None
                    and pressure_a != pressure_b
                    if pressure_scenario
                    else pressure_a == "" and pressure_b == ""
                ),
                f"{role} deterministic tree worker-pressure evidence is invalid",
            )
            quota_scenario = scenario in SYNC_TREE_QUOTA_SCENARIOS
            object_quota_scenario = scenario == "sync-tree-object-quota"
            quota_kind = receipt.get(
                "sync_tree_quota_kind",
                "bytes" if scenario == "sync-tree-quota" else "",
            )
            quota_maximum_objects = receipt.get(
                "sync_tree_quota_maximum_objects",
                32 if scenario == "sync-tree-quota" else 0,
            )
            quota_inventory_objects = receipt.get(
                "sync_tree_quota_inventory_objects",
                2 if scenario == "sync-tree-quota" else 0,
            )
            quota_head = receipt.get("sync_tree_quota_candidate_head_record", "")
            quota_artifact = receipt.get(
                "sync_tree_quota_candidate_artifact_sha256", ""
            )
            quota_manifest = receipt.get(
                "sync_tree_quota_candidate_manifest_sha256", ""
            )
            require(
                receipt.get("sync_tree_quota_observed", False)
                is quota_scenario
                and quota_kind
                == (
                    "objects"
                    if object_quota_scenario
                    else "bytes" if quota_scenario else ""
                )
                and receipt.get("sync_tree_quota_store_bytes", 0)
                == (
                    33_554_432
                    if object_quota_scenario
                    else 5_242_880 if quota_scenario else 0
                )
                and receipt.get("sync_tree_quota_inventory_bytes", 0)
                == (
                    receipt["sync_artifact_bytes"]
                    + receipt["sync_manifest_bytes"]
                    + (4 if object_quota_scenario else 0)
                    if quota_scenario
                    else 0
                )
                and quota_maximum_objects
                == (6 if object_quota_scenario else 32 if quota_scenario else 0)
                and quota_inventory_objects
                == (6 if object_quota_scenario else 2 if quota_scenario else 0)
                and (
                    receipt["sync_tree_quota_inventory_bytes"]
                    < receipt["sync_tree_quota_store_bytes"]
                    and (
                        quota_inventory_objects == quota_maximum_objects
                        and receipt["sync_tree_quota_inventory_bytes"]
                        + receipt["sync_artifact_bytes"]
                        + receipt["sync_manifest_bytes"]
                        <= receipt["sync_tree_quota_store_bytes"]
                        if object_quota_scenario
                        else receipt["sync_artifact_bytes"]
                        > receipt["sync_tree_quota_store_bytes"]
                        - receipt["sync_tree_quota_inventory_bytes"]
                        and receipt["sync_manifest_bytes"]
                        > receipt["sync_tree_quota_store_bytes"]
                        - receipt["sync_tree_quota_inventory_bytes"]
                    )
                    and SHA256.fullmatch(str(quota_head)) is not None
                    and SHA256.fullmatch(str(quota_artifact)) is not None
                    and SHA256.fullmatch(str(quota_manifest)) is not None
                    and quota_head != receipt["sync_head_record"]
                    and quota_artifact != receipt["sync_artifact_sha256"]
                    and quota_manifest != receipt["sync_manifest_sha256"]
                    if quota_scenario
                    else quota_head == ""
                    and quota_artifact == ""
                    and quota_manifest == ""
                ),
                f"{role} deterministic tree quota evidence is invalid",
            )
            read_only_scenario = scenario == "sync-tree-read-only"
            read_only_head = receipt.get(
                "sync_tree_read_only_head_record", ""
            )
            read_only_artifact = receipt.get(
                "sync_tree_read_only_artifact_sha256", ""
            )
            read_only_manifest = receipt.get(
                "sync_tree_read_only_manifest_sha256", ""
            )
            require(
                receipt.get("sync_tree_read_only_observed", False)
                is read_only_scenario
                and receipt.get("sync_tree_read_only_pull_refused", False)
                is read_only_scenario
                and receipt.get(
                    "sync_tree_read_only_activation_refused", False
                )
                is read_only_scenario
                and receipt.get(
                    "sync_tree_read_only_retry_observed", False
                )
                is read_only_scenario
                and (
                    SHA256.fullmatch(str(read_only_head)) is not None
                    and SHA256.fullmatch(str(read_only_artifact)) is not None
                    and SHA256.fullmatch(str(read_only_manifest)) is not None
                    and read_only_head != receipt["sync_head_record"]
                    and read_only_artifact != receipt["sync_artifact_sha256"]
                    and read_only_manifest != receipt["sync_manifest_sha256"]
                    if read_only_scenario
                    else read_only_head == ""
                    and read_only_artifact == ""
                    and read_only_manifest == ""
                ),
                f"{role} deterministic tree read-only evidence is invalid",
            )
            memory_scenario = scenario == "sync-tree-memory"
            memory_head = receipt.get("sync_tree_memory_head_record", "")
            memory_artifact = receipt.get(
                "sync_tree_memory_artifact_sha256", ""
            )
            memory_manifest = receipt.get(
                "sync_tree_memory_manifest_sha256", ""
            )
            memory_values = [
                receipt.get("sync_tree_memory_ceiling_kib", 0),
                receipt.get("sync_tree_memory_entries", 0),
                receipt.get("sync_tree_memory_artifact_bytes", 0),
                receipt.get("sync_tree_memory_publisher_baseline_hwm_kib", 0),
                receipt.get(
                    "sync_tree_memory_publisher_post_publish_hwm_kib", 0
                ),
                receipt.get("sync_tree_memory_publisher_peak_hwm_kib", 0),
                receipt.get("sync_tree_memory_publisher_delta_hwm_kib", 0),
                receipt.get("sync_tree_memory_subscriber_baseline_hwm_kib", 0),
                receipt.get("sync_tree_memory_subscriber_post_pull_hwm_kib", 0),
                receipt.get("sync_tree_memory_subscriber_peak_hwm_kib", 0),
                receipt.get("sync_tree_memory_subscriber_delta_hwm_kib", 0),
                receipt.get("sync_tree_memory_pair_peak_hwm_kib", 0),
                receipt.get(
                    "sync_tree_memory_pair_maximum_delta_hwm_kib", 0
                ),
            ]
            require(
                receipt.get("sync_tree_memory_observed", False)
                is memory_scenario
                and (
                    all(isinstance(value, int) for value in memory_values)
                    and memory_values[0] == 65_536
                    and memory_values[1] == 128
                    and receipt["sync_artifact_bytes"] < memory_values[2]
                    <= 8_388_608
                    and 0 < memory_values[3] <= memory_values[4]
                    <= memory_values[5] <= memory_values[0]
                    and memory_values[6] == memory_values[5] - memory_values[3]
                    and 0 < memory_values[7] <= memory_values[8]
                    <= memory_values[9] <= memory_values[0]
                    and memory_values[10] == memory_values[9] - memory_values[7]
                    and memory_values[11]
                    == max(memory_values[5], memory_values[9])
                    and memory_values[12]
                    == max(memory_values[6], memory_values[10])
                    and SHA256.fullmatch(str(memory_head)) is not None
                    and SHA256.fullmatch(str(memory_artifact)) is not None
                    and SHA256.fullmatch(str(memory_manifest)) is not None
                    and memory_head != receipt["sync_head_record"]
                    and memory_artifact != receipt["sync_artifact_sha256"]
                    and memory_manifest != receipt["sync_manifest_sha256"]
                    if memory_scenario
                    else memory_values == [0] * len(memory_values)
                    and memory_head == ""
                    and memory_artifact == ""
                    and memory_manifest == ""
                ),
                f"{role} deterministic tree memory evidence is invalid",
            )
            source_corrupt_scenario = scenario == "sync-tree-source-corrupt"
            source_corrupt_head = receipt.get(
                "sync_tree_source_corrupt_head_record", ""
            )
            source_corrupt_artifact = receipt.get(
                "sync_tree_source_corrupt_artifact_sha256", ""
            )
            source_corrupt_manifest = receipt.get(
                "sync_tree_source_corrupt_manifest_sha256", ""
            )
            source_corrupt_artifact_bytes = receipt.get(
                "sync_tree_source_corrupt_artifact_bytes", 0
            )
            source_corrupt_manifest_bytes = receipt.get(
                "sync_tree_source_corrupt_manifest_bytes", 0
            )
            source_corrupt_quarantined_objects = receipt.get(
                "sync_tree_source_corrupt_quarantined_objects", 0
            )
            source_corrupt_quarantined_bytes = receipt.get(
                "sync_tree_source_corrupt_quarantined_bytes", 0
            )
            require(
                receipt.get("sync_tree_source_corrupt_observed", False)
                is source_corrupt_scenario
                and receipt.get("sync_tree_source_corrupt_refused", False)
                is source_corrupt_scenario
                and receipt.get("sync_tree_source_corrupt_repaired", False)
                is source_corrupt_scenario
                and receipt.get(
                    "sync_tree_source_corrupt_retry_observed", False
                )
                is source_corrupt_scenario
                and (
                    SHA256.fullmatch(str(source_corrupt_head)) is not None
                    and SHA256.fullmatch(str(source_corrupt_artifact)) is not None
                    and SHA256.fullmatch(str(source_corrupt_manifest)) is not None
                    and source_corrupt_head != receipt["sync_head_record"]
                    and source_corrupt_artifact
                    != receipt["sync_artifact_sha256"]
                    and source_corrupt_manifest
                    != receipt["sync_manifest_sha256"]
                    and source_corrupt_artifact_bytes
                    == receipt["sync_artifact_bytes"]
                    and source_corrupt_manifest_bytes
                    == receipt["sync_manifest_bytes"]
                    and source_corrupt_quarantined_objects == 2
                    and source_corrupt_quarantined_bytes
                    == source_corrupt_artifact_bytes
                    + source_corrupt_manifest_bytes
                    if source_corrupt_scenario
                    else source_corrupt_head == ""
                    and source_corrupt_artifact == ""
                    and source_corrupt_manifest == ""
                    and source_corrupt_artifact_bytes == 0
                    and source_corrupt_manifest_bytes == 0
                    and source_corrupt_quarantined_objects == 0
                    and source_corrupt_quarantined_bytes == 0
                ),
                f"{role} deterministic publisher-source corruption evidence is invalid",
            )
            destination_corrupt_scenario = (
                scenario == "sync-tree-destination-corrupt"
            )
            destination_corrupt_head = receipt.get(
                "sync_tree_destination_corrupt_head_record", ""
            )
            destination_corrupt_artifact = receipt.get(
                "sync_tree_destination_corrupt_artifact_sha256", ""
            )
            destination_corrupt_manifest = receipt.get(
                "sync_tree_destination_corrupt_manifest_sha256", ""
            )
            destination_corrupt_artifact_bytes = receipt.get(
                "sync_tree_destination_corrupt_artifact_bytes", 0
            )
            destination_corrupt_manifest_bytes = receipt.get(
                "sync_tree_destination_corrupt_manifest_bytes", 0
            )
            destination_corrupt_file_id = receipt.get(
                "sync_tree_destination_corrupt_file_id", ""
            )
            destination_corrupt_position = receipt.get(
                "sync_tree_destination_corrupt_position_bytes", 0
            )
            destination_corrupt_committed = receipt.get(
                "sync_tree_destination_corrupt_committed_before_failure", 0
            )
            destination_corrupt_retry_requested = receipt.get(
                "sync_tree_destination_corrupt_retry_requested_objects", 0
            )
            require(
                receipt.get("sync_tree_destination_corrupt_observed", False)
                is destination_corrupt_scenario
                and receipt.get(
                    "sync_tree_destination_corrupt_rejected", False
                )
                is destination_corrupt_scenario
                and receipt.get(
                    "sync_tree_destination_corrupt_retry_observed", False
                )
                is destination_corrupt_scenario
                and (
                    SHA256.fullmatch(str(destination_corrupt_head)) is not None
                    and SHA256.fullmatch(str(destination_corrupt_artifact))
                    is not None
                    and SHA256.fullmatch(str(destination_corrupt_manifest))
                    is not None
                    and SHA256.fullmatch(str(destination_corrupt_file_id))
                    is not None
                    and destination_corrupt_head != receipt["sync_head_record"]
                    and destination_corrupt_artifact
                    != receipt["sync_artifact_sha256"]
                    and destination_corrupt_manifest
                    != receipt["sync_manifest_sha256"]
                    and destination_corrupt_artifact_bytes
                    == receipt["sync_artifact_bytes"]
                    and destination_corrupt_manifest_bytes
                    == receipt["sync_manifest_bytes"]
                    and isinstance(destination_corrupt_position, int)
                    and 0
                    < destination_corrupt_position
                    < destination_corrupt_artifact_bytes
                    and destination_corrupt_committed in {0, 1}
                    and destination_corrupt_retry_requested
                    == 2 - destination_corrupt_committed
                    if destination_corrupt_scenario
                    else destination_corrupt_head == ""
                    and destination_corrupt_artifact == ""
                    and destination_corrupt_manifest == ""
                    and destination_corrupt_artifact_bytes == 0
                    and destination_corrupt_manifest_bytes == 0
                    and destination_corrupt_file_id == ""
                    and destination_corrupt_position == 0
                    and destination_corrupt_committed == 0
                    and destination_corrupt_retry_requested == 0
                ),
                f"{role} deterministic subscriber-destination corruption evidence is invalid",
            )
            control_replay_scenario = scenario == "sync-tree-control-replay"
            control_replay_head = receipt.get(
                "sync_tree_control_replay_head_record", ""
            )
            control_replay_artifact = receipt.get(
                "sync_tree_control_replay_artifact_sha256", ""
            )
            control_replay_manifest = receipt.get(
                "sync_tree_control_replay_manifest_sha256", ""
            )
            control_replay_counts = {
                "sync_tree_control_replay_admitted_before_replay": 2,
                "sync_tree_control_replay_publisher_head_requests_delta": 1,
                "sync_tree_control_replay_publisher_object_requests_delta": 2,
                "sync_tree_control_replay_publisher_file_offers_delta": 2,
                "sync_tree_control_replay_publisher_replay_hits_delta": 3,
                "sync_tree_control_replay_publisher_replay_conflicts_delta": 1,
                "sync_tree_control_replay_subscriber_incoming_head_results_delta": 2,
                "sync_tree_control_replay_subscriber_incoming_object_results_delta": 4,
                "sync_tree_control_replay_subscriber_outgoing_object_requests_delta": 4,
            }
            require(
                all(
                    receipt.get(field, False) is control_replay_scenario
                    for field in (
                        "sync_tree_control_replay_observed",
                        "sync_tree_control_replay_exact_replay_observed",
                        "sync_tree_control_replay_reordered_result_observed",
                        "sync_tree_control_replay_conflict_refused",
                        "sync_tree_control_replay_activation_observed",
                    )
                )
                and all(
                    receipt.get(field, 0)
                    == (expected if control_replay_scenario else 0)
                    for field, expected in control_replay_counts.items()
                )
                and (
                    SHA256.fullmatch(str(control_replay_head)) is not None
                    and SHA256.fullmatch(str(control_replay_artifact)) is not None
                    and SHA256.fullmatch(str(control_replay_manifest)) is not None
                    and control_replay_head != receipt["sync_head_record"]
                    and control_replay_artifact
                    != receipt["sync_artifact_sha256"]
                    and control_replay_manifest
                    != receipt["sync_manifest_sha256"]
                    if control_replay_scenario
                    else control_replay_head == ""
                    and control_replay_artifact == ""
                    and control_replay_manifest == ""
                ),
                f"{role} synchronization control replay evidence is invalid",
            )
            range_scenario = scenario in SYNC_POSITIVE_RANGE_SCENARIOS
            fallback_scenario = scenario == "sync-file-corrupt-basis"
            retry_scenario = scenario == "sync-file-range-retry"
            range_count = receipt.get("sync_range_count", 0)
            range_reused = receipt.get("sync_range_reused_bytes", 0)
            range_fetched = receipt.get("sync_range_fetched_bytes", 0)
            require(
                receipt.get("sync_range_observed", False) is range_scenario
                and receipt.get("sync_range_fallback_observed", False)
                is fallback_scenario
                and receipt.get("sync_corrupt_basis_preserved", False)
                is fallback_scenario
                and receipt.get("sync_range_retry_observed", False)
                is retry_scenario
                and isinstance(range_count, int)
                and isinstance(range_reused, int)
                and isinstance(range_fetched, int)
                and (
                    range_count > 0
                    and range_reused > 0
                    and 0 < range_fetched < receipt["sync_artifact_bytes"]
                    and range_reused + range_fetched
                    == receipt["sync_artifact_bytes"]
                    if range_scenario
                    else range_count == 0
                    and range_reused == 0
                    and range_fetched == 0
                ),
                f"{role} synchronization range evidence is invalid",
            )
            retry_position = receipt.get("sync_range_retry_position_bytes", 0)
            retry_retained = receipt.get(
                "sync_range_retry_retained_bytes", 0
            )
            retry_resumed = receipt.get(
                "sync_range_retry_resumed_bytes", 0
            )
            retry_discarded = receipt.get(
                "sync_range_retry_discarded_bytes", 0
            )
            retry_retention_fallbacks = receipt.get(
                "sync_range_retry_retention_fallbacks", 0
            )
            resumed_retry_evidence = all(
                field in receipt
                for field in (
                    "sync_range_retry_retained_bytes",
                    "sync_range_retry_resumed_bytes",
                    "sync_range_retry_discarded_bytes",
                    "sync_range_retry_retention_fallbacks",
                )
            )
            first_file_id = receipt.get("sync_range_retry_first_file_id", "")
            second_file_id = receipt.get("sync_range_retry_second_file_id", "")
            require(
                (
                    isinstance(retry_position, int)
                    and (
                        0 < retry_position == retry_retained == retry_resumed
                        < range_fetched
                        and retry_discarded == 0
                        and retry_retention_fallbacks == 0
                        if resumed_retry_evidence
                        else 0 < retry_position < range_fetched
                    )
                    and SHA256.fullmatch(str(first_file_id)) is not None
                    and SHA256.fullmatch(str(second_file_id)) is not None
                    and first_file_id != second_file_id
                    if retry_scenario
                    else retry_position == 0
                    and retry_retained == 0
                    and retry_resumed == 0
                    and retry_discarded == 0
                    and retry_retention_fallbacks == 0
                    and first_file_id == ""
                    and second_file_id == ""
                ),
                f"{role} synchronization range retry evidence is invalid",
            )
            range_restart = scenario == "sync-file-range-restart-resume"
            range_restart_interrupted = receipt.get(
                "sync_range_restart_interrupted_bytes", 0
            )
            range_restart_retained = receipt.get(
                "sync_range_restart_retained_bytes", 0
            )
            range_restart_resumed_attempts = receipt.get(
                "sync_range_restart_resumed_attempts", 0
            )
            range_restart_resumed = receipt.get(
                "sync_range_restart_resumed_bytes", 0
            )
            range_restart_suffix = receipt.get(
                "sync_range_restart_suffix_bytes", 0
            )
            range_restart_jobs = (
                receipt.get("sync_range_restart_first_job_id", 0),
                receipt.get("sync_range_restart_second_job_id", 0),
            )
            range_restart_attempts = (
                receipt.get("sync_range_restart_first_attempt_id", 0),
                receipt.get("sync_range_restart_second_attempt_id", 0),
            )
            range_restart_messages = (
                receipt.get("sync_range_restart_first_message_id", 0),
                receipt.get("sync_range_restart_second_message_id", 0),
            )
            range_restart_file_ids = (
                receipt.get("sync_range_restart_first_file_id", ""),
                receipt.get("sync_range_restart_second_file_id", ""),
            )
            require(
                receipt.get("sync_range_restart_resume_observed", False)
                is range_restart
                and (
                    all(
                        isinstance(value, int)
                        for value in (
                            range_restart_interrupted,
                            range_restart_retained,
                            range_restart_resumed_attempts,
                            range_restart_resumed,
                            range_restart_suffix,
                            *range_restart_jobs,
                            *range_restart_attempts,
                            *range_restart_messages,
                        )
                    )
                    and range_restart_resumed_attempts == 1
                    and 0
                    < range_restart_interrupted
                    == range_restart_retained
                    == range_restart_resumed
                    < range_fetched
                    and range_restart_resumed + range_restart_suffix
                    == range_fetched
                    and all(
                        value > 0
                        for value in (
                            *range_restart_jobs,
                            *range_restart_attempts,
                            *range_restart_messages,
                        )
                    )
                    and range_restart_jobs[0] != range_restart_jobs[1]
                    and range_restart_attempts[0] != range_restart_attempts[1]
                    and range_restart_messages[0] != range_restart_messages[1]
                    and all(
                        SHA256.fullmatch(str(value)) is not None
                        for value in range_restart_file_ids
                    )
                    and range_restart_file_ids[0]
                    != range_restart_file_ids[1]
                    if range_restart
                    else range_restart_interrupted == 0
                    and range_restart_retained == 0
                    and range_restart_resumed_attempts == 0
                    and range_restart_resumed == 0
                    and range_restart_suffix == 0
                    and all(
                        value == 0
                        for value in (
                            *range_restart_jobs,
                            *range_restart_attempts,
                            *range_restart_messages,
                        )
                    )
                    and range_restart_file_ids == ("", "")
                ),
                f"{role} synchronization range-restart evidence is invalid",
            )
            repair_scenario = scenario == "sync-file-repair"
            receipt_gc_fields = (
                "sync_gc_observed",
                "sync_gc_dry_candidates",
                "sync_gc_moved_objects",
                "sync_gc_durable_objects",
                "sync_gc_outside_sentinels",
                "sync_gc_purge_disabled",
                "sync_gc_mount_refused",
            )
            require(
                receipt.get("sync_repair_observed", False)
                is repair_scenario
                and receipt.get("sync_repair_recovery_observed", False)
                is repair_scenario
                and receipt.get("sync_repair_clean_retry_observed", False)
                is repair_scenario
                and receipt.get("sync_repair_quarantine_preserved", False)
                is repair_scenario
                and receipt.get("sync_repair_state_preserved", False)
                is repair_scenario
                and receipt.get("sync_repair_inspected_objects", 0)
                == (2 if repair_scenario else 0)
                and receipt.get("sync_repair_quarantined_objects", 0)
                == (1 if repair_scenario else 0)
                and receipt.get("sync_repair_quarantined_bytes", 0)
                == (SYNC_SCENARIOS[scenario] if repair_scenario else 0)
                and receipt.get("sync_gc_observed", False)
                is gc_repair
                and receipt.get("sync_gc_dry_candidates", 0)
                == (1 if gc_repair else 0)
                and receipt.get("sync_gc_moved_objects", 0)
                == (1 if gc_repair else 0)
                and receipt.get("sync_gc_durable_objects", 0)
                == (1 if gc_repair else 0)
                and receipt.get("sync_gc_outside_sentinels", 0)
                == (2 if gc_repair else 0)
                and receipt.get("sync_gc_purge_disabled", False)
                is gc_repair
                and receipt.get("sync_gc_mount_refused", False)
                is gc_repair
                and (
                    not legacy_repair
                    or all(field not in receipt for field in receipt_gc_fields)
                ),
                f"{role} synchronization repair evidence is invalid",
            )
            process_restart = scenario in {
                "sync-file-restart",
                "sync-file-restart-resume",
                "sync-file-range-restart-resume",
                *CONTENT_RESTART_SCENARIOS,
            }
            guest_restart = scenario == "sync-file-guest-restart"
            restart = process_restart or guest_restart
            disconnect = scenario == "sync-file-disconnect"
            require(
                receipt.get("sync_restart_observed", False) is restart
                and receipt.get("sync_restart_recovery_observed", False)
                is restart
                and receipt.get("sync_restart_identity_preserved", False)
                is restart,
                f"{role} synchronization restart classification mismatch",
            )
            if process_restart and role == "client":
                interrupted_bytes = receipt.get("sync_interrupted_staging_bytes")
                require(
                    receipt.get("sync_daemon_restart_count") == 1
                    and receipt.get("sync_peer_offline_observed") is False
                    and receipt.get("sync_attempt_recovery_observed") is True
                    and receipt.get("sync_unclean_stop_observed") is True
                    and isinstance(interrupted_bytes, int)
                    and 0
                    < interrupted_bytes
                    < receipt["sync_artifact_bytes"]
                    + receipt["sync_manifest_bytes"],
                    "client synchronization restart evidence is incomplete",
                )
            elif process_restart:
                require(
                    receipt.get("sync_daemon_restart_count") == 0
                    and receipt.get("sync_peer_offline_observed") is True
                    and receipt.get("sync_attempt_recovery_observed") is False
                    and receipt.get("sync_unclean_stop_observed") is False
                    and receipt.get("sync_interrupted_staging_bytes") == 0
                    and receipt.get("recovered_online_epoch", 0)
                    > receipt.get("initial_online_epoch", 0),
                    "publisher synchronization restart evidence is incomplete",
                )
            elif guest_restart:
                guest_restart_bytes = receipt.get(
                    "sync_guest_restart_staging_bytes"
                )
                require(
                    receipt.get("sync_daemon_restart_count") == 0
                    and receipt.get("sync_peer_offline_observed")
                    is (role == "client")
                    and receipt.get("sync_attempt_recovery_observed") is False
                    and receipt.get("sync_unclean_stop_observed") is False
                    and receipt.get("sync_interrupted_staging_bytes") == 0
                    and receipt.get("sync_guest_restart_cleanup_observed") is True
                    and receipt.get("sync_guest_restart_retry_observed") is True
                    and receipt.get("sync_guest_restart_stable_samples") == 50
                    and receipt.get("sync_disconnect_staging_bytes", 0) == 0
                    and receipt.get("sync_disconnect_cleanup_observed", False)
                    is False
                    and receipt.get("sync_disconnect_retry_observed", False)
                    is False
                    and receipt.get("sync_disconnect_stable_samples", 0) == 0
                    and (
                        isinstance(guest_restart_bytes, int)
                        and (
                            0
                            < guest_restart_bytes
                            < receipt["sync_artifact_bytes"]
                            + receipt["sync_manifest_bytes"]
                            if role == "client"
                            else guest_restart_bytes == 0
                        )
                    ),
                    f"{role} synchronization guest-restart evidence is incomplete",
                )
            elif disconnect:
                disconnected_bytes = receipt.get(
                    "sync_disconnect_staging_bytes"
                )
                require(
                    receipt.get("sync_daemon_restart_count") == 0
                    and receipt.get("sync_peer_offline_observed") is True
                    and receipt.get("sync_attempt_recovery_observed") is False
                    and receipt.get("sync_unclean_stop_observed") is False
                    and receipt.get("sync_interrupted_staging_bytes") == 0
                    and receipt.get("sync_disconnect_cleanup_observed") is True
                    and receipt.get("sync_disconnect_retry_observed") is True
                    and receipt.get("sync_disconnect_stable_samples") == 50
                    and receipt.get("recovered_online_epoch", 0)
                    > receipt.get("initial_online_epoch", 0)
                    and (
                        isinstance(disconnected_bytes, int)
                        and 0
                        < disconnected_bytes
                        < receipt["sync_artifact_bytes"]
                        + receipt["sync_manifest_bytes"]
                        if role == "client"
                        else disconnected_bytes == 0
                    ),
                    f"{role} synchronization disconnect evidence is incomplete",
                )
            else:
                require(
                    receipt.get("sync_daemon_restart_count", 0) == 0
                    and receipt.get("sync_peer_offline_observed", False) is False
                    and receipt.get("sync_attempt_recovery_observed", False) is False
                    and receipt.get("sync_unclean_stop_observed", False) is False
                    and receipt.get("sync_interrupted_staging_bytes", 0) == 0,
                    f"{role} baseline synchronization claims restart evidence",
                )
                require(
                    receipt.get("sync_disconnect_staging_bytes", 0) == 0
                    and receipt.get(
                        "sync_disconnect_cleanup_observed", False
                    )
                    is False
                    and receipt.get("sync_disconnect_retry_observed", False)
                    is False
                    and receipt.get("sync_disconnect_stable_samples", 0) == 0,
                    f"{role} non-disconnect sync scenario claims disconnect evidence",
                )
            if scenario in CONTENT_RESTART_SCENARIOS:
                content_cap = CONTENT_RESTART_SCENARIOS[scenario]
                content_restart = role == "client"
                crash_objects = receipt.get(
                    "content_restart_crash_committed_objects", 0
                )
                recovered_objects = receipt.get(
                    "content_restart_recovered_committed_objects", 0
                )
                crash_bytes = receipt.get(
                    "content_restart_crash_committed_bytes", 0
                )
                recovered_bytes = receipt.get(
                    "content_restart_recovered_committed_bytes", 0
                )
                transport_files = receipt.get(
                    "content_restart_crash_transport_files", 0
                )
                total_chunks = receipt.get("content_restart_total_chunks", 0)
                total_objects = receipt.get("content_restart_total_objects", 0)
                require(
                    receipt.get("content_restart_observed", False)
                    is content_restart
                    and receipt.get("content_restart_cap", 0)
                    == (content_cap if content_restart else 0)
                    and receipt.get("content_restart_live_lanes", 0)
                    == (content_cap if content_restart else 0)
                    and (
                        SHA256.fullmatch(
                            str(
                                receipt.get(
                                    "content_restart_live_lane_set_sha256", ""
                                )
                            )
                        )
                        is not None
                        and receipt[
                            "content_restart_live_lane_set_sha256"
                        ]
                        == content_restart_interruption_fields[
                            "content-restart-lane-set-sha256"
                        ]
                        if content_restart
                        else receipt.get(
                            "content_restart_live_lane_set_sha256", ""
                        )
                        == ""
                    )
                    and (
                        isinstance(
                            receipt.get("content_restart_first_job_id"), int
                        )
                        and isinstance(
                            receipt.get("content_restart_second_job_id"), int
                        )
                        and receipt["content_restart_first_job_id"] > 0
                        and receipt["content_restart_second_job_id"] > 0
                        and receipt["content_restart_first_job_id"]
                        == int(
                            content_restart_interruption_fields[
                                "content-restart-first-job"
                            ]
                        )
                        and receipt["content_restart_first_job_id"]
                        != receipt["content_restart_second_job_id"]
                        and isinstance(total_chunks, int)
                        and total_chunks >= content_cap
                        and total_chunks
                        == int(content_fields["content-chunks"])
                        and isinstance(total_objects, int)
                        and total_objects >= content_cap + 2
                        and total_objects
                        == int(content_fields["content-objects"])
                        and isinstance(transport_files, int)
                        and 2 <= transport_files <= content_cap
                        and transport_files
                        == int(
                            content_restart_crash_fields[
                                "transport-temporaries"
                            ]
                        )
                        and 0
                        < receipt.get("content_restart_crash_transport_bytes", 0)
                        < receipt["sync_artifact_bytes"]
                        and receipt["content_restart_crash_transport_bytes"]
                        == int(
                            content_restart_crash_fields[
                                "content-transport-bytes"
                            ]
                        )
                        and receipt.get(
                            "content_restart_crash_canonical_partials"
                        )
                        == 0
                        and isinstance(crash_objects, int)
                        and 2 <= crash_objects < total_objects
                        and crash_objects
                        == int(
                            content_restart_crash_fields[
                                "content-committed-objects"
                            ]
                        )
                        and isinstance(recovered_objects, int)
                        and recovered_objects == crash_objects
                        and isinstance(crash_bytes, int)
                        and 0 < crash_bytes < receipt["sync_artifact_bytes"]
                        and crash_bytes
                        == int(
                            content_restart_crash_fields[
                                "content-committed-bytes"
                            ]
                        )
                        and isinstance(recovered_bytes, int)
                        and recovered_bytes == crash_bytes
                        and receipt.get(
                            "content_restart_recovery_committed_delta"
                        )
                        == recovered_objects - crash_objects
                        and receipt["content_restart_recovery_committed_delta"]
                        == 0
                        and receipt.get(
                            "content_restart_post_start_transport_files"
                        )
                        == 0
                        and receipt.get(
                            "content_restart_post_start_canonical_partials"
                        )
                        == 0
                        and all(
                            SHA256.fullmatch(str(value)) is not None
                            for value in (
                                receipt.get(
                                    "content_restart_crash_inventory_sha256", ""
                                ),
                                receipt.get(
                                    "content_restart_recovered_inventory_sha256",
                                    "",
                                ),
                            )
                        )
                        and receipt[
                            "content_restart_crash_inventory_sha256"
                        ]
                        == content_restart_crash_fields[
                            "content-inventory-sha256"
                        ]
                        and receipt[
                            "content_restart_crash_inventory_sha256"
                        ]
                        == receipt[
                            "content_restart_recovered_inventory_sha256"
                        ]
                        if content_restart
                        else receipt.get("content_restart_first_job_id", 0) == 0
                        and receipt.get("content_restart_second_job_id", 0) == 0
                        and total_chunks == 0
                        and total_objects == 0
                        and transport_files == 0
                        and receipt.get(
                            "content_restart_crash_transport_bytes", 0
                        )
                        == 0
                        and receipt.get(
                            "content_restart_crash_canonical_partials", 0
                        )
                        == 0
                        and crash_objects == 0
                        and crash_bytes == 0
                        and recovered_objects == 0
                        and recovered_bytes == 0
                        and receipt.get(
                            "content_restart_recovery_committed_delta", 0
                        )
                        == 0
                        and receipt.get(
                            "content_restart_post_start_transport_files", 0
                        )
                        == 0
                        and receipt.get(
                            "content_restart_post_start_canonical_partials", 0
                        )
                        == 0
                        and receipt.get(
                            "content_restart_crash_inventory_sha256", ""
                        )
                        == ""
                        and receipt.get(
                            "content_restart_recovered_inventory_sha256", ""
                        )
                        == ""
                    ),
                    f"{role} multi-lane content restart evidence is invalid",
                )
            restart_prefix_resume = scenario == "sync-file-restart-resume"
            require(
                receipt.get("sync_restart_prefix_resume_observed", False)
                is restart_prefix_resume
                and isinstance(
                    receipt.get("sync_restart_resumed_attempts", 0), int
                )
                and isinstance(receipt.get("sync_restart_resumed_bytes", 0), int)
                and (
                    1 <= receipt["sync_restart_resumed_attempts"] <= 2
                    and 0
                    < receipt["sync_restart_resumed_bytes"]
                    < receipt["sync_artifact_bytes"]
                    + receipt["sync_manifest_bytes"]
                    if restart_prefix_resume
                    else receipt.get("sync_restart_resumed_attempts", 0) == 0
                    and receipt.get("sync_restart_resumed_bytes", 0) == 0
                ),
                f"{role} restart-prefix continuation evidence is invalid",
            )
            if restart_prefix_resume and role == "client":
                require(
                    receipt["sync_restart_resumed_bytes"]
                    == receipt["sync_interrupted_staging_bytes"],
                    "client restart-prefix byte accounting is not exact",
                )
            if not guest_restart:
                require(
                    receipt.get("sync_guest_restart_staging_bytes", 0) == 0
                    and receipt.get(
                        "sync_guest_restart_cleanup_observed", False
                    )
                    is False
                    and receipt.get(
                        "sync_guest_restart_retry_observed", False
                    )
                    is False
                    and receipt.get("sync_guest_restart_stable_samples", 0) == 0,
                    f"{role} non-guest-restart sync scenario claims reboot evidence",
                )
            pause = scenario == "sync-file-pause"
            pause_position = receipt.get("sync_pause_position_bytes", 0)
            require(
                receipt.get("sync_pause_observed", False) is pause
                and receipt.get("sync_resume_observed", False) is pause
                and (
                    isinstance(pause_position, int)
                    and 0
                    < pause_position
                    < receipt["sync_artifact_bytes"]
                    + receipt["sync_manifest_bytes"]
                    and receipt.get("sync_pause_stable_samples") == 20
                    and SHA256.fullmatch(
                        str(receipt.get("sync_pause_file_id", ""))
                    )
                    is not None
                    if pause
                    else pause_position == 0
                    and receipt.get("sync_pause_stable_samples", 0) == 0
                    and receipt.get("sync_pause_file_id", "") == ""
                ),
                f"{role} synchronization pause/resume evidence is invalid",
            )
            if cancellation:
                require(
                    isinstance(receipt.get("sync_cancelled_job_id"), str)
                    and re.fullmatch(
                        r"[1-9][0-9]*", receipt["sync_cancelled_job_id"]
                    )
                    is not None
                    and isinstance(
                        receipt.get("sync_cancelled_staging_bytes"), int
                    )
                    and 0
                    < receipt["sync_cancelled_staging_bytes"]
                    < receipt["sync_artifact_bytes"]
                    + receipt["sync_manifest_bytes"]
                    and isinstance(
                        receipt.get("sync_cancelled_receive_count"), int
                    )
                    and 0 < receipt["sync_cancelled_receive_count"] <= 2,
                    f"{role} synchronization cancellation evidence is invalid",
                )
            else:
                require(
                    receipt.get("sync_cancellation_observed", False) is False
                    and receipt.get("sync_cancelled_staging_bytes", 0) == 0
                    and receipt.get("sync_cancelled_receive_count", 0) == 0
                    and receipt.get("sync_cancelled_job_id", "") == "",
                    f"{role} non-cancellation sync scenario claims cancellation",
                )
            sync_restart_evidence[role] = (
                receipt.get("sync_daemon_restart_count", 0),
                receipt.get("sync_interrupted_staging_bytes", 0),
                receipt.get("sync_restart_recovery_observed", False),
                receipt.get("sync_unclean_stop_observed", False),
            )
            sync_revisions.append(
                tuple(
                    receipt[field]
                    for field in (
                        "sync_generation",
                        "sync_artifact_bytes",
                        "sync_manifest_bytes",
                        "sync_artifact_sha256",
                        "sync_manifest_sha256",
                        "sync_head_record",
                    )
                )
            )
        else:
            require(
                receipt.get("sync_authority_observed", False) is False
                and receipt.get("sync_convergence_observed", False) is False
                and receipt.get("sync_activation_observed", False) is False
                and receipt.get("sync_generation", 0) == 0
                and receipt.get("sync_artifact_bytes", 0) == 0
                and receipt.get("sync_manifest_bytes", 0) == 0,
                f"{role} non-sync scenario claims synchronization evidence",
            )
            require(
                receipt.get("sync_restart_observed", False) is False
                and receipt.get("sync_peer_offline_observed", False) is False
                and receipt.get("sync_restart_recovery_observed", False) is False
                and receipt.get("sync_restart_identity_preserved", False) is False
                and receipt.get("sync_attempt_recovery_observed", False) is False
                and receipt.get("sync_unclean_stop_observed", False) is False
                and receipt.get("sync_daemon_restart_count", 0) == 0
                and receipt.get("sync_interrupted_staging_bytes", 0) == 0,
                f"{role} non-sync scenario claims synchronization restart evidence",
            )
            require(
                receipt.get("sync_cancellation_observed", False) is False
                and receipt.get("sync_cancelled_staging_bytes", 0) == 0
                and receipt.get("sync_cancelled_receive_count", 0) == 0
                and receipt.get("sync_cancelled_job_id", "") == "",
                f"{role} non-sync scenario claims synchronization cancellation",
            )
            require(
                receipt.get("sync_disconnect_staging_bytes", 0) == 0
                and receipt.get("sync_disconnect_cleanup_observed", False)
                is False
                and receipt.get("sync_disconnect_retry_observed", False) is False
                and receipt.get("sync_disconnect_stable_samples", 0) == 0,
                f"{role} non-sync scenario claims synchronization disconnect",
            )
            require(
                receipt.get("sync_pause_observed", False) is False
                and receipt.get("sync_resume_observed", False) is False
                and receipt.get("sync_pause_position_bytes", 0) == 0
                and receipt.get("sync_pause_stable_samples", 0) == 0
                and receipt.get("sync_pause_file_id", "") == "",
                f"{role} non-sync scenario claims synchronization pause/resume",
            )
        require(receipt.get("product_revision") == revision, f"{role} product revision mismatch")
        require(receipt.get("version") == f"IoTox {version} {revision}", f"{role} version mismatch")
        require(isinstance(receipt.get("source_revision"), str) and receipt["source_revision"], f"{role} source revision absent")
        require(receipt.get("package_variant") == "pinned-source-linked", f"{role} package variant mismatch")
        require(receipt.get("c_toxcore_version") == "0.2.23", f"{role} c-toxcore mismatch")
        require(
            receipt.get("c_toxcore_variant") in {
                None,
                "iotox-file-rr1",
                "iotox-file-rr1-tcp-connect120",
            },
            f"{role} c-toxcore variant mismatch",
        )
        require(receipt.get("libsodium_version") == "1.0.22", f"{role} libsodium mismatch")
        require(receipt.get("argon2_version") == "20190702", f"{role} Argon2 mismatch")
        require(receipt.get("virtualization") == "kvm", f"{role} did not observe KVM")
        require(receipt.get("cgroup_type") == "cgroup2fs", f"{role} did not observe cgroup v2")
        require(receipt.get("network_class") == "provider-egress", f"{role} network class mismatch")
        require(receipt.get("contains_secrets") is False, f"{role} receipt is not content-free")
        for field in ("binary_sha256", "peer_key_sha256", "bootstrap_key_sha256"):
            require(SHA256.fullmatch(str(receipt.get(field, ""))) is not None, f"{role} {field} is invalid")
        require(receipt_entry.get("binary_sha256") == receipt["binary_sha256"], f"{role} manifest binary mismatch")
        require(receipt_entry.get("peer_key_sha256") == receipt["peer_key_sha256"], f"{role} manifest peer mismatch")
        binary_digests.add(receipt["binary_sha256"])
        bootstrap_digests.add(receipt["bootstrap_key_sha256"])

        chain_entry = manifest.get("chains", {}).get(role, {})
        chain_relative = f"{evidence_role}/direct-cloud-hypervisor-live-chain.json"
        chain_path = confined(proof_root, chain_entry.get("path"), chain_relative)
        require(chain_entry.get("sha256") == digest(chain_path), f"{role} chain digest mismatch")
        chain = load(chain_path)
        require(chain.get("schema") == "sandwurm.direct-cloud-hypervisor-live-chain.v0", f"{role} chain schema mismatch")
        require(chain.get("status") == "guest-evidence-observed" and chain.get("failure") is None, f"{role} guest evidence failed")
        require(chain.get("receipts", {}).get("prelaunch_chain", {}).get("status") == "ready", f"{role} prelaunch was not ready")
        if scenario in GUEST_RESTART_SCENARIOS and role == "device":
            expected_prelaunch = str(
                source_proof_root
                / "device/prelaunch/direct-cloud-hypervisor-prelaunch-chain.json"
            )
            require(
                chain.get("receipts", {}).get("prelaunch_chain", {}).get("path")
                == expected_prelaunch,
                "replacement device did not reuse the initial prelaunch receipt",
            )
        require(chain.get("receipts", {}).get("live_launch", {}).get("status") == "exited", f"{role} VMM exit was not observed")
        require(chain.get("guest_evidence", {}).get("observed") is True, f"{role} guest boundary absent")
        require(chain.get("guest_evidence", {}).get("legacy_guest_receipts_complete") is True, f"{role} generic receipts incomplete")

        planned = load(proof_root / role / "prelaunch/launch/cloud-hypervisor-launch.json")
        network = planned.get("network", {})
        require(planned.get("status") == "planned", f"{role} launch was not planned")
        require(network.get("class") == "provider-egress", f"{role} planned network class mismatch")
        require(network.get("mode") == "prepared-host-tap-nat", f"{role} planned network mode mismatch")
        require(network.get("tap_interface") == tap_name, f"{role} planned TAP mismatch")
        require(network.get("prepared_host_contract", {}).get("bridge_interface") == "sandwurm-vm", f"{role} planned bridge mismatch")
        argv = planned.get("vmm", {}).get("argv", [])
        require("--net" in argv and f"tap={tap_name}" in argv, f"{role} VMM TAP argument absent")
        verified_receipts[role] = receipt_entry["sha256"]

    if ratox_cli_reconnect_repeated_scenario:
        lifecycle_path = confined(
            proof_root,
            "client/live/workspace-export/guest-receipts/iotox/"
            "ratox-route-loss-probe.json",
            "client/live/workspace-export/guest-receipts/iotox/"
            "ratox-route-loss-probe.json",
        )
        lifecycle = load(lifecycle_path)
        require(
            set(lifecycle)
            == {
                "cli_output_sha256",
                "initial",
                "interruption_count",
                "interruptions",
                "peer_public_key_sha256",
                "process",
                "schema",
                "session_id_sha256",
                "status",
            }
            and lifecycle["schema"] == "iotox-ratox-cli-reconnect-probe-v2"
            and lifecycle["status"] == "passed"
            and lifecycle["interruption_count"] == 2
            and lifecycle["peer_public_key_sha256"]
            == ratox_capture_peer_commitment
            and SHA256.fullmatch(str(lifecycle["session_id_sha256"])) is not None
            and SHA256.fullmatch(str(lifecycle["cli_output_sha256"])) is not None,
            "repeated production-CLI reconnect probe envelope is invalid",
        )
        process = lifecycle["process"]
        initial = lifecycle["initial"]
        require(
            isinstance(process, dict)
            and set(process)
            == {
                "client",
                "exit_status",
                "finished_us",
                "pid",
                "process_restarts",
                "start_ticks",
                "started_us",
            }
            and process["client"] == "iotox-terminal-reconnect"
            and isinstance(process["pid"], int)
            and process["pid"] > 1
            and isinstance(process["start_ticks"], int)
            and process["start_ticks"] > 0
            and process["process_restarts"] == 0
            and process["exit_status"] == 0
            and 0 < process["started_us"] < process["finished_us"],
            "repeated production reconnect process identity is invalid",
        )
        observation_keys = {
            "capability_observed",
            "claimant_principal_present",
            "claimant_proof_sent",
            "connection",
            "online_epoch",
            "session_state",
        }
        initial_extra = {
            "generation",
            "healthy_heartbeat_end_us",
            "healthy_heartbeat_start_us",
            "incarnation",
            "input_sequence",
            "output_sequence",
            "terminal_returned_us",
            "terminal_started_us",
        }
        require(
            isinstance(initial, dict)
            and set(initial) == observation_keys | initial_extra
            and initial["session_state"] == "confirmed"
            and initial["connection"] == connection
            and initial["online_epoch"] > 0
            and initial["capability_observed"] == 1
            and initial["claimant_proof_sent"] == 1
            and initial["claimant_principal_present"] == 1
            and initial["incarnation"] > 0
            and initial["generation"] == 1
            and initial["input_sequence"] == 1
            and initial["output_sequence"] == 1
            and initial["healthy_heartbeat_start_us"]
            < initial["healthy_heartbeat_end_us"]
            and initial["terminal_started_us"] < initial["terminal_returned_us"],
            "repeated production reconnect initial phase is invalid",
        )
        snapshot_keys = {
            "generation",
            "incarnation",
            "next_input",
            "output_base",
            "output_next",
            "session",
            "state",
        }
        recovery_extra = {
            "generation",
            "healthy_heartbeat_end_us",
            "healthy_heartbeat_start_us",
            "incarnation",
            "input_sequence",
            "output_sequence",
            "release_us",
            "resume_opened_us",
            "retry_attempts",
            "terminal_returned_us",
            "terminal_started_us",
        }
        transitions = lifecycle["interruptions"]
        require(
            isinstance(transitions, list) and len(transitions) == 2,
            "repeated production reconnect transition count is invalid",
        )
        previous_epoch = initial["online_epoch"]
        for ordinal, transition in enumerate(transitions, start=1):
            require(
                isinstance(transition, dict)
                and set(transition) == {"loss", "ordinal", "recovery"}
                and transition["ordinal"] == ordinal,
                f"production reconnect transition {ordinal} is malformed",
            )
            loss = transition["loss"]
            recovery = transition["recovery"]
            require(
                isinstance(loss, dict)
                and set(loss)
                == {
                    "carrier_at_heartbeat_warning",
                    "heartbeat_warning_us",
                    "offline",
                    "online_epoch_at_heartbeat_warning",
                    "reconnect_wait_us",
                    "release_us",
                    "retained",
                    "session_state_at_heartbeat_warning",
                }
                and isinstance(loss["offline"], dict)
                and set(loss["offline"]) == observation_keys
                and loss["offline"]["session_state"] == "offline"
                and loss["offline"]["connection"] == "offline"
                and loss["offline"]["online_epoch"] == previous_epoch
                and loss["carrier_at_heartbeat_warning"] == connection
                and loss["session_state_at_heartbeat_warning"] == "confirmed"
                and loss["online_epoch_at_heartbeat_warning"] == previous_epoch
                and loss["release_us"] < loss["heartbeat_warning_us"]
                <= loss["reconnect_wait_us"]
                and isinstance(loss["retained"], dict)
                and set(loss["retained"]) == snapshot_keys
                and loss["retained"]["state"] == "detached"
                and loss["retained"]["incarnation"] == initial["incarnation"]
                and loss["retained"]["generation"] == ordinal
                and loss["retained"]["next_input"] == ordinal + 1
                and loss["retained"]["output_next"] == ordinal + 1,
                f"production reconnect loss phase {ordinal} is invalid",
            )
            require(
                isinstance(recovery, dict)
                and set(recovery) == observation_keys | recovery_extra
                and recovery["session_state"] == "confirmed"
                and recovery["connection"] == connection
                and recovery["online_epoch"] > previous_epoch
                and recovery["capability_observed"] == 1
                and recovery["claimant_proof_sent"] == 1
                and recovery["claimant_principal_present"] == 1
                and recovery["incarnation"] == initial["incarnation"]
                and recovery["generation"] == ordinal + 1
                and recovery["input_sequence"] == ordinal + 1
                and recovery["output_sequence"] == ordinal + 1
                and recovery["retry_attempts"] > 0
                and recovery["release_us"] <= recovery["resume_opened_us"]
                and recovery["healthy_heartbeat_start_us"]
                < recovery["healthy_heartbeat_end_us"]
                and recovery["terminal_started_us"]
                < recovery["terminal_returned_us"],
                f"production reconnect recovery phase {ordinal} is invalid",
            )
            previous_epoch = recovery["online_epoch"]
        require(
            len(ratox_capture_rows) == 3
            and len(ratox_heartbeat_rows) == 3
            and hashlib.sha256(bytes.fromhex(ratox_capture_rows[0][5])).hexdigest()
            == lifecycle["session_id_sha256"]
            and len({row[5] for row in ratox_capture_rows}) == 1,
            "repeated production reconnect captures changed session identity",
        )
        phases = [initial, *(entry["recovery"] for entry in transitions)]
        for index, phase in enumerate(phases):
            require(
                int(ratox_capture_rows[index][6]) == index + 1
                and int(ratox_capture_rows[index][8]) == index + 1
                and int(ratox_capture_rows[index][2])
                == phase["terminal_started_us"]
                and int(ratox_capture_rows[index][3])
                == phase["terminal_returned_us"]
                and int(ratox_heartbeat_rows[index][2])
                == phase["healthy_heartbeat_start_us"]
                and int(ratox_heartbeat_rows[index][3])
                == phase["healthy_heartbeat_end_us"],
                f"production reconnect capture phase {index + 1} disagrees",
            )

        host_loss_status = confined(
            proof_root,
            "device/live/workspace-export/guest-receipts/iotox/"
            "ratox-host-loss-status.txt",
            "device/live/workspace-export/guest-receipts/iotox/"
            "ratox-host-loss-status.txt",
        ).read_text(encoding="ascii")
        status_values = {
            key: value
            for line in host_loss_status.splitlines()
            if "=" in line
            for key, value in [line.split("=", 1)]
        }
        require(
            status_values.get("ratox-session-count") == "1"
            and status_values.get("ratox-live-session-count") == "1"
            and status_values.get("ratox-running-process-count") == "1"
            and status_values.get("ratox-attached-session-count") == "0",
            "repeated reconnect host did not retain one detached live PTY",
        )
        host_loss_events = confined(
            proof_root,
            "device/live/workspace-export/guest-receipts/iotox/"
            "ratox-host-loss-events.txt",
            "device/live/workspace-export/guest-receipts/iotox/"
            "ratox-host-loss-events.txt",
        ).read_text(encoding="ascii")
        detached_sessions = []
        for line in host_loss_events.splitlines():
            if " kind=peer-detached " not in f" {line} ":
                continue
            fields = {
                key: value
                for token in line.split()
                for key, separator, value in [token.partition("=")]
                if separator
            }
            session_hex = fields.get("session-id", "")
            require(
                re.fullmatch(r"[0-9A-F]{32}", session_hex) is not None,
                "repeated reconnect detachment has no canonical session",
            )
            detached_sessions.append(
                hashlib.sha256(bytes.fromhex(session_hex)).hexdigest()
            )
        require(
            lifecycle["session_id_sha256"] in detached_sessions,
            "repeated reconnect host detachment names another session",
        )

    elif ratox_cli_reconnect_scenario:
        lifecycle_path = confined(
            proof_root,
            "client/live/workspace-export/guest-receipts/iotox/"
            "ratox-route-loss-probe.json",
            "client/live/workspace-export/guest-receipts/iotox/"
            "ratox-route-loss-probe.json",
        )
        lifecycle = load(lifecycle_path)
        require(
            set(lifecycle)
            == {
                "cli_output_sha256",
                "initial",
                "loss",
                "peer_public_key_sha256",
                "process",
                "recovery",
                "schema",
                "session_id_sha256",
                "status",
            }
            and lifecycle["schema"] == "iotox-ratox-cli-reconnect-probe-v1"
            and lifecycle["status"] == "passed"
            and lifecycle["peer_public_key_sha256"]
            == ratox_capture_peer_commitment
            and SHA256.fullmatch(str(lifecycle["session_id_sha256"])) is not None
            and SHA256.fullmatch(str(lifecycle["cli_output_sha256"])) is not None,
            "production-CLI reconnect probe envelope is invalid",
        )
        process = lifecycle["process"]
        initial = lifecycle["initial"]
        loss = lifecycle["loss"]
        recovery = lifecycle["recovery"]
        require(
            isinstance(process, dict)
            and set(process)
            == {
                "client",
                "exit_status",
                "finished_us",
                "pid",
                "process_restarts",
                "start_ticks",
                "started_us",
            }
            and process["client"] == "iotox-terminal-reconnect"
            and isinstance(process["pid"], int)
            and process["pid"] > 1
            and isinstance(process["start_ticks"], int)
            and process["start_ticks"] > 0
            and process["process_restarts"] == 0
            and process["exit_status"] == 0
            and 0 < process["started_us"] < process["finished_us"],
            "production reconnect process identity or lifetime is invalid",
        )
        observation_keys = {
            "capability_observed",
            "claimant_principal_present",
            "claimant_proof_sent",
            "connection",
            "online_epoch",
            "session_state",
        }
        require(
            isinstance(initial, dict)
            and set(initial)
            == observation_keys
            | {
                "generation",
                "healthy_heartbeat_end_us",
                "healthy_heartbeat_start_us",
                "incarnation",
                "input_sequence",
                "output_sequence",
                "terminal_returned_us",
                "terminal_started_us",
            }
            and initial["session_state"] == "confirmed"
            and initial["connection"] == connection
            and initial["online_epoch"] > 0
            and initial["capability_observed"] == 1
            and initial["claimant_proof_sent"] == 1
            and initial["claimant_principal_present"] == 1
            and initial["incarnation"] > 0
            and initial["generation"] == 1
            and initial["input_sequence"] == 1
            and initial["output_sequence"] == 1
            and initial["healthy_heartbeat_start_us"]
            < initial["healthy_heartbeat_end_us"]
            and initial["terminal_started_us"]
            < initial["terminal_returned_us"],
            "production reconnect initial phase is invalid",
        )
        snapshot_keys = {
            "generation",
            "incarnation",
            "next_input",
            "output_base",
            "output_next",
            "session",
            "state",
        }
        require(
            isinstance(loss, dict)
            and set(loss)
            == {
                "carrier_at_heartbeat_warning",
                "heartbeat_warning_us",
                "offline",
                "online_epoch_at_heartbeat_warning",
                "reconnect_wait_us",
                "release_us",
                "retained",
                "session_state_at_heartbeat_warning",
            }
            and isinstance(loss["offline"], dict)
            and set(loss["offline"]) == observation_keys
            and loss["offline"]["session_state"] == "offline"
            and loss["offline"]["connection"] == "offline"
            and loss["offline"]["online_epoch"] == initial["online_epoch"]
            and loss["carrier_at_heartbeat_warning"] == connection
            and loss["session_state_at_heartbeat_warning"] == "confirmed"
            and loss["online_epoch_at_heartbeat_warning"]
            == initial["online_epoch"]
            and loss["release_us"] < loss["heartbeat_warning_us"]
            <= loss["reconnect_wait_us"]
            and isinstance(loss["retained"], dict)
            and set(loss["retained"]) == snapshot_keys
            and loss["retained"]["state"] == "detached"
            and loss["retained"]["incarnation"] == initial["incarnation"]
            and loss["retained"]["generation"] == 1
            and loss["retained"]["next_input"] == 2
            and loss["retained"]["output_next"] == 2,
            "production reconnect loss phase is invalid",
        )
        require(
            isinstance(recovery, dict)
            and set(recovery)
            == observation_keys
            | {
                "generation",
                "healthy_heartbeat_end_us",
                "healthy_heartbeat_start_us",
                "incarnation",
                "input_sequence",
                "output_sequence",
                "release_us",
                "resume_opened_us",
                "retry_attempts",
                "terminal_returned_us",
                "terminal_started_us",
            }
            and recovery["session_state"] == "confirmed"
            and recovery["connection"] == connection
            and recovery["online_epoch"] > initial["online_epoch"]
            and recovery["capability_observed"] == 1
            and recovery["claimant_proof_sent"] == 1
            and recovery["claimant_principal_present"] == 1
            and recovery["incarnation"] == initial["incarnation"]
            and recovery["generation"] == 2
            and recovery["input_sequence"] == 2
            and recovery["output_sequence"] == 2
            and recovery["retry_attempts"] > 0
            and recovery["release_us"] <= recovery["resume_opened_us"]
            and recovery["healthy_heartbeat_start_us"]
            < recovery["healthy_heartbeat_end_us"]
            and recovery["terminal_started_us"]
            < recovery["terminal_returned_us"],
            "production reconnect recovery phase is invalid",
        )
        require(
            len(ratox_capture_rows) == 2
            and len(ratox_heartbeat_rows) == 2
            and hashlib.sha256(bytes.fromhex(ratox_capture_rows[0][5])).hexdigest()
            == lifecycle["session_id_sha256"]
            and ratox_capture_rows[0][5] == ratox_capture_rows[1][5]
            and int(ratox_capture_rows[0][6]) == 1
            and int(ratox_capture_rows[0][8]) == 1
            and int(ratox_capture_rows[1][6]) == 2
            and int(ratox_capture_rows[1][8]) == 2
            and int(ratox_capture_rows[0][2])
            == initial["terminal_started_us"]
            and int(ratox_capture_rows[0][3])
            == initial["terminal_returned_us"]
            and int(ratox_capture_rows[1][2])
            == recovery["terminal_started_us"]
            and int(ratox_capture_rows[1][3])
            == recovery["terminal_returned_us"]
            and int(ratox_heartbeat_rows[0][2])
            == initial["healthy_heartbeat_start_us"]
            and int(ratox_heartbeat_rows[0][3])
            == initial["healthy_heartbeat_end_us"]
            and int(ratox_heartbeat_rows[1][2])
            == recovery["healthy_heartbeat_start_us"]
            and int(ratox_heartbeat_rows[1][3])
            == recovery["healthy_heartbeat_end_us"],
            "production reconnect captures disagree with its lifecycle",
        )

        host_loss_status = confined(
            proof_root,
            "device/live/workspace-export/guest-receipts/iotox/"
            "ratox-host-loss-status.txt",
            "device/live/workspace-export/guest-receipts/iotox/"
            "ratox-host-loss-status.txt",
        ).read_text(encoding="ascii")
        status_values = {
            key: value
            for line in host_loss_status.splitlines()
            if "=" in line
            for key, value in [line.split("=", 1)]
        }
        require(
            status_values.get("ratox-session-count") == "1"
            and status_values.get("ratox-live-session-count") == "1"
            and status_values.get("ratox-running-process-count") == "1"
            and status_values.get("ratox-attached-session-count") == "0",
            "production reconnect host did not retain one detached live PTY",
        )
        host_loss_events = confined(
            proof_root,
            "device/live/workspace-export/guest-receipts/iotox/"
            "ratox-host-loss-events.txt",
            "device/live/workspace-export/guest-receipts/iotox/"
            "ratox-host-loss-events.txt",
        ).read_text(encoding="ascii")
        detached_sessions = []
        for line in host_loss_events.splitlines():
            if " kind=peer-detached " not in f" {line} ":
                continue
            fields = {
                key: value
                for token in line.split()
                for key, separator, value in [token.partition("=")]
                if separator
            }
            session_hex = fields.get("session-id", "")
            require(
                re.fullmatch(r"[0-9A-F]{32}", session_hex) is not None,
                "production reconnect detachment has no canonical session",
            )
            detached_sessions.append(
                hashlib.sha256(bytes.fromhex(session_hex)).hexdigest()
            )
        require(
            lifecycle["session_id_sha256"] in detached_sessions,
            "production reconnect host detachment names another session",
        )

    elif ratox_route_loss_scenario:
        lifecycle_path = confined(
            proof_root,
            "client/live/workspace-export/guest-receipts/iotox/"
            "ratox-route-loss-probe.json",
            "client/live/workspace-export/guest-receipts/iotox/"
            "ratox-route-loss-probe.json",
        )
        lifecycle = load(lifecycle_path)
        require(
            set(lifecycle)
            == {
                "initial",
                "loss",
                "peer_public_key_sha256",
                "recovery",
                "schema",
                "session_id_sha256",
                "status",
            }
            and lifecycle["schema"] == "iotox-ratox-route-loss-probe-v1"
            and lifecycle["status"] == "passed"
            and SHA256.fullmatch(str(lifecycle["peer_public_key_sha256"]))
            is not None
            and lifecycle["peer_public_key_sha256"]
            == ratox_capture_peer_commitment
            and SHA256.fullmatch(str(lifecycle["session_id_sha256"])) is not None,
            "Ratox route-loss probe envelope is invalid",
        )

        observation_keys = {
            "capability_observed",
            "claimant_principal_present",
            "claimant_proof_sent",
            "connection",
            "online_epoch",
            "session_state",
        }
        initial = lifecycle["initial"]
        loss = lifecycle["loss"]
        recovery = lifecycle["recovery"]
        require(isinstance(initial, dict) and isinstance(loss, dict)
                and isinstance(recovery, dict),
                "Ratox route-loss probe phases are not objects")
        require(
            set(initial)
            == observation_keys
            | {
                "generation", "heartbeat_us", "incarnation",
                "input_sequence", "output_sequence", "render_us", "terminal_us",
            },
            "Ratox route-loss initial phase schema drifted",
        )
        require(
            set(loss)
            == {
                "carrier_at_heartbeat_timeout",
                "controller_error_detail_sha256",
                "controller_outcome",
                "controller_outcome_us",
                "heartbeat_deadline_us",
                "heartbeat_started_us",
                "heartbeat_timeout_us",
                "offline",
                "online_epoch_at_heartbeat_timeout",
                "release_us",
                "session_state_at_heartbeat_timeout",
            },
            "Ratox route-loss loss-phase schema drifted",
        )
        require(
            set(recovery)
            == observation_keys
            | {
                "generation", "heartbeat_us", "incarnation",
                "input_sequence", "output_sequence", "render_us",
                "release_us", "resume_opened_us", "route_ready_us", "terminal_us",
            },
            "Ratox route-loss recovery phase schema drifted",
        )
        offline = loss["offline"]
        require(isinstance(offline, dict) and set(offline) == observation_keys,
                "Ratox route-loss offline observation schema drifted")
        require(
            initial["session_state"] == "confirmed"
            and initial["connection"] == connection
            and isinstance(initial["online_epoch"], int)
            and initial["online_epoch"] > 0
            and initial["capability_observed"] == 1
            and initial["claimant_proof_sent"] == 1
            and initial["claimant_principal_present"] == 1
            and initial["generation"] == 1
            and initial["incarnation"] > 0
            and initial["input_sequence"] == 1
            and initial["output_sequence"] == 1,
            "Ratox route-loss initial identity is invalid",
        )
        require(
            loss["carrier_at_heartbeat_timeout"] == connection
            and loss["session_state_at_heartbeat_timeout"] == "confirmed"
            and loss["online_epoch_at_heartbeat_timeout"]
            == initial["online_epoch"]
            and loss["controller_outcome"] == "error-unavailable"
            and SHA256.fullmatch(str(loss["controller_error_detail_sha256"]))
            is not None
            and offline["session_state"] == "offline"
            and offline["connection"] == "offline"
            and offline["online_epoch"] == initial["online_epoch"],
            "Ratox route-loss signal separation is invalid",
        )
        require(
            recovery["session_state"] == "confirmed"
            and recovery["connection"] == connection
            and recovery["online_epoch"] > initial["online_epoch"]
            and recovery["capability_observed"] == 1
            and recovery["claimant_proof_sent"] == 1
            and recovery["claimant_principal_present"] == 1
            and recovery["incarnation"] == initial["incarnation"]
            and recovery["generation"] == initial["generation"] + 1
            and recovery["input_sequence"] == 2
            and recovery["output_sequence"] == 2,
            "Ratox route-loss resume identity is invalid",
        )
        require(
            loss["release_us"] <= loss["heartbeat_started_us"]
            < loss["heartbeat_deadline_us"] < loss["controller_outcome_us"]
            and 1_800_000 <= loss["heartbeat_timeout_us"] <= 3_000_000
            and loss["heartbeat_timeout_us"]
            == loss["heartbeat_deadline_us"] - loss["heartbeat_started_us"]
            and recovery["release_us"] <= recovery["route_ready_us"]
            <= recovery["resume_opened_us"],
            "Ratox route-loss phase times are not ordered",
        )
        require(
            len(ratox_capture_rows) == 2
            and len(ratox_heartbeat_rows) == 2
            and hashlib.sha256(bytes.fromhex(ratox_capture_rows[0][5])).hexdigest()
            == lifecycle["session_id_sha256"]
            and ratox_capture_rows[0][5] == ratox_capture_rows[1][5]
            and int(ratox_capture_rows[0][6]) == 1
            and int(ratox_capture_rows[0][8]) == 1
            and int(ratox_capture_rows[1][6]) == 2
            and int(ratox_capture_rows[1][8]) == 2,
            "Ratox route-loss capture did not preserve session/byte identity",
        )
        require(
            initial["heartbeat_us"]
            == int(ratox_heartbeat_rows[0][3])
            - int(ratox_heartbeat_rows[0][2])
            and recovery["heartbeat_us"]
            == int(ratox_heartbeat_rows[1][3])
            - int(ratox_heartbeat_rows[1][2])
            and initial["terminal_us"]
            == int(ratox_capture_rows[0][3])
            - int(ratox_capture_rows[0][2])
            and initial["render_us"]
            == int(ratox_capture_rows[0][4])
            - int(ratox_capture_rows[0][3])
            and recovery["terminal_us"]
            == int(ratox_capture_rows[1][3])
            - int(ratox_capture_rows[1][2])
            and recovery["render_us"]
            == int(ratox_capture_rows[1][4])
            - int(ratox_capture_rows[1][3]),
            "Ratox route-loss lifecycle disagrees with raw timing captures",
        )

        host_loss_status = confined(
            proof_root,
            "device/live/workspace-export/guest-receipts/iotox/"
            "ratox-host-loss-status.txt",
            "device/live/workspace-export/guest-receipts/iotox/"
            "ratox-host-loss-status.txt",
        ).read_text(encoding="ascii")
        status_values = {
            key: value
            for line in host_loss_status.splitlines()
            if "=" in line
            for key, value in [line.split("=", 1)]
        }
        require(
            status_values.get("ratox-session-count") == "1"
            and status_values.get("ratox-live-session-count") == "1"
            and status_values.get("ratox-running-process-count") == "1"
            and status_values.get("ratox-attached-session-count") == "0",
            "Ratox host did not retain one detached live PTY",
        )
        host_loss_events = confined(
            proof_root,
            "device/live/workspace-export/guest-receipts/iotox/"
            "ratox-host-loss-events.txt",
            "device/live/workspace-export/guest-receipts/iotox/"
            "ratox-host-loss-events.txt",
        ).read_text(encoding="ascii")
        detached_sessions = []
        for line in host_loss_events.splitlines():
            if " kind=peer-detached " not in f" {line} ":
                continue
            fields = {
                key: value
                for token in line.split()
                for key, separator, value in [token.partition("=")]
                if separator
            }
            session_hex = fields.get("session-id", "")
            require(re.fullmatch(r"[0-9A-F]{32}", session_hex) is not None,
                    "Ratox peer-detached event has no canonical session")
            detached_sessions.append(
                hashlib.sha256(bytes.fromhex(session_hex)).hexdigest()
            )
        require(
            lifecycle["session_id_sha256"] in detached_sessions,
            "Ratox host detachment does not name the resumed session",
        )

    require(
        len(mixed_auxiliary_key_hashes) == (2 if mixed_context else 0)
        and (
            len(set(mixed_auxiliary_key_hashes)) == 2
            if mixed_context
            else True
        ),
        "private mixed-context auxiliary identities are not distinct",
    )

    declared_resource_intervals = manifest.get(
        "ratox_resource_interval_role_count"
    )
    if declared_resource_intervals is None:
        require(
            ratox_resource_intervals
            in ({0, 2} if scenario in RATOX_SCENARIOS else {0}),
            "Ratox resource interval evidence is only partially present",
        )
    else:
        require(
            declared_resource_intervals
            == (2 if scenario in RATOX_SCENARIOS else 0)
            == ratox_resource_intervals,
            "declared Ratox resource interval evidence is incomplete",
        )
    require(
        ratox_agent_statuses
        in ({0, 2} if scenario in RATOX_SCENARIOS else {0}),
        "Ratox agent status evidence is only partially present",
    )
    require(len(binary_digests) == 1, "guest binary digests differ")
    require(len(bootstrap_digests) == 1, "guest bootstrap fixture digests differ")
    if scenario in CONTENT_MULTI_SOURCE_SCENARIOS and route == "forced-tcp":
        require(
            manifest.get(
                "multi_source_secondary_bootstrap_key_sha256"
            )
            not in bootstrap_digests,
            "multi-source TCP relay identities are not distinct",
        )
    if scenario in SYNC_SCENARIOS:
        require(
            len(sync_revisions) == 2
            and sync_revisions[0] == sync_revisions[1],
            "guest synchronization revision evidence disagrees",
        )
        require(
            manifest.get("sync_artifact_sha256") == sync_revisions[0][3]
            and manifest.get("sync_manifest_sha256") == sync_revisions[0][4]
            and manifest.get("sync_head_record") == sync_revisions[0][5],
            "manifest synchronization identity disagrees with receipts",
        )
        if scenario in SYNC_TREE_SCENARIOS:
            client_receipt = load(
                proof_root / manifest["receipts"]["client"]["path"]
            )
            device_receipt = load(
                proof_root / manifest["receipts"]["device"]["path"]
            )
            for field in (
                "sync_tree_observed",
                "sync_tree_directories",
                "sync_tree_files",
                "sync_tree_content_bytes",
                "sync_tree_payload_sha256",
            ):
                require(
                    client_receipt[field] == device_receipt[field],
                    f"guest synchronization tree evidence disagrees on {field}",
                )
            require(
                manifest["sync_tree_payload_sha256"]
                == client_receipt["sync_tree_payload_sha256"],
                "manifest tree payload identity disagrees with receipts",
            )
            if scenario == "sync-tree-admission":
                for field in (
                    "sync_tree_admission_observed",
                    "sync_tree_admission_receive_limit",
                    "sync_tree_admission_retry_count",
                    "sync_tree_admission_admitted_offers",
                    "sync_tree_admission_pending_offers",
                ):
                    require(
                        client_receipt[field] == device_receipt[field],
                        f"guest synchronization admission evidence disagrees on {field}",
                    )
                for field in (
                    "sync_tree_admission_receive_limit",
                    "sync_tree_admission_retry_count",
                    "sync_tree_admission_admitted_offers",
                    "sync_tree_admission_pending_offers",
                ):
                    require(
                        manifest[field] == client_receipt[field],
                        f"manifest synchronization admission evidence disagrees on {field}",
                    )
            if scenario in SYNC_ROUTE_LOSS_SCENARIOS:
                for field in (
                    "sync_tree_route_loss_observed",
                    "sync_tree_route_loss_position_bytes",
                    "sync_tree_route_loss_carrier_losses",
                    "sync_tree_route_loss_reassignments",
                    "sync_tree_route_loss_stale_terminals",
                    "sync_tree_route_loss_recoveries",
                ):
                    require(
                        manifest[field] == client_receipt[field],
                        f"manifest synchronization route-loss evidence disagrees on {field}",
                    )
                require(
                    manifest["sync_tree_route_ready_role_count"] == 2
                    and client_receipt["sync_tree_route_ready_bulk"] == 2
                    and device_receipt["sync_tree_route_ready_bulk"] == 2,
                    "guest synchronization route inventory evidence disagrees",
                )
                if manifest.get("sync_tree_route_resume_observed", False):
                    for field in (
                        "sync_tree_route_resume_observed",
                        "sync_tree_route_loss_retained_partials",
                        "sync_tree_route_loss_retained_attempts",
                        "sync_tree_route_loss_retained_bytes",
                        "sync_tree_route_loss_retention_fallbacks",
                        "sync_tree_route_loss_resumed_attempts",
                        "sync_tree_route_loss_resumed_bytes",
                    ):
                        require(
                            manifest[field] == client_receipt[field],
                            "manifest synchronization route-resume evidence "
                            f"disagrees on {field}",
                        )
            if scenario == "sync-tree-route-startup-order":
                observations = tuple(
                    receipt[field]
                    for receipt in (client_receipt, device_receipt)
                    for field in (
                        "sync_tree_route_startup_phase_one_ms",
                        "sync_tree_route_startup_phase_two_ms",
                    )
                )
                stable_samples = tuple(
                    receipt[field]
                    for receipt in (client_receipt, device_receipt)
                    for field in (
                        "sync_tree_route_startup_phase_one_stable_samples",
                        "sync_tree_route_startup_phase_two_stable_samples",
                    )
                )
                require(
                    manifest[
                        "sync_tree_route_startup_order_observed_role_count"
                    ]
                    == 2
                    and manifest["sync_tree_route_startup_delay_ms"]
                    == client_receipt["sync_tree_route_startup_delay_ms"]
                    == device_receipt["sync_tree_route_startup_delay_ms"]
                    == 20_000
                    and manifest["sync_tree_route_startup_restart_count"]
                    == client_receipt[
                        "sync_tree_route_startup_restart_count"
                    ]
                    + device_receipt[
                        "sync_tree_route_startup_restart_count"
                    ]
                    == 2
                    and manifest[
                        "sync_tree_route_startup_minimum_stable_samples"
                    ]
                    == min(stable_samples)
                    == 10
                    and manifest[
                        "sync_tree_route_startup_maximum_observation_ms"
                    ]
                    == max(observations)
                    and manifest["sync_tree_route_ready_role_count"] == 2
                    and client_receipt["sync_tree_route_ready_bulk"] == 2
                    and device_receipt["sync_tree_route_ready_bulk"] == 2,
                    "guest synchronization startup-order evidence disagrees",
                )
            if scenario == "sync-tree-route-balance":
                for field in (
                    "sync_tree_route_balance_observed",
                    "sync_tree_route_balance_fixed_same_carrier",
                    "sync_tree_route_balance_adaptive_distinct_carriers",
                    "sync_tree_route_balance_fixed_carrier_a",
                    "sync_tree_route_balance_fixed_carrier_b",
                    "sync_tree_route_balance_adaptive_carrier_a",
                    "sync_tree_route_balance_adaptive_carrier_b",
                    "sync_tree_route_balance_fixed_selections",
                    "sync_tree_route_balance_adaptive_selections",
                    "sync_tree_route_balance_fixed_duration_ms",
                    "sync_tree_route_balance_adaptive_duration_ms",
                    "sync_tree_route_balance_activations",
                    "sync_tree_route_balance_artifact_bytes",
                    "sync_tree_route_balance_fixed_head_retries",
                    "sync_tree_route_balance_adaptive_head_retries",
                ):
                    require(
                        manifest[field] == client_receipt[field],
                        f"manifest synchronization route-balance evidence "
                        f"disagrees on {field}",
                    )
                require(
                    manifest.get("sync_tree_route_balance_phase_order", "")
                    == client_receipt.get(
                        "sync_tree_route_balance_phase_order", ""
                    ),
                    "manifest synchronization route-balance evidence "
                    "disagrees on sync_tree_route_balance_phase_order",
                )
                require(
                    manifest["sync_tree_route_ready_role_count"] == 2
                    and client_receipt["sync_tree_route_ready_bulk"] == 2
                    and device_receipt["sync_tree_route_ready_bulk"] == 2,
                    "guest synchronization balance route inventory disagrees",
                )
            if scenario == "sync-tree-route-population":
                for field in (
                    "sync_tree_route_population_observed",
                    "sync_tree_route_population_jobs",
                    "sync_tree_route_population_artifact_bytes",
                    "sync_tree_route_population_fixed_pattern",
                    "sync_tree_route_population_adaptive_pattern",
                    "sync_tree_route_population_fixed_max_prefix_imbalance",
                    "sync_tree_route_population_adaptive_max_prefix_imbalance",
                    "sync_tree_route_population_fixed_progress_jobs",
                    "sync_tree_route_population_adaptive_progress_jobs",
                    "sync_tree_route_population_fixed_progress_observation_spread_ms",
                    "sync_tree_route_population_adaptive_progress_observation_spread_ms",
                    "sync_tree_route_population_fixed_duration_ms",
                    "sync_tree_route_population_adaptive_duration_ms",
                    "sync_tree_route_population_activations",
                    "sync_tree_route_population_fixed_resource_sha256",
                    "sync_tree_route_population_adaptive_resource_sha256",
                ):
                    require(
                        manifest[field] == client_receipt[field],
                        "manifest synchronization route-population evidence "
                        f"disagrees on {field}",
                    )
                require(
                    manifest["sync_tree_route_ready_role_count"] == 2
                    and client_receipt["sync_tree_route_ready_bulk"] == 2
                    and device_receipt["sync_tree_route_ready_bulk"] == 2,
                    "guest synchronization population route inventory disagrees",
                )
            if scenario in {
                "sync-tree-route-population-loss",
                "sync-tree-route-loss-admission",
            }:
                for field in (
                    "sync_tree_route_population_loss_jobs",
                    "sync_tree_route_population_loss_artifact_bytes",
                    "sync_tree_route_population_loss_pattern",
                    "sync_tree_route_population_loss_affected_jobs",
                    "sync_tree_route_population_loss_carrier_losses",
                    "sync_tree_route_population_loss_reassignments",
                    "sync_tree_route_population_loss_stale_terminals",
                    "sync_tree_route_population_loss_recoveries",
                    "sync_tree_route_population_loss_fixed_selections",
                    "sync_tree_route_population_loss_activations",
                    "sync_tree_route_population_loss_work_before",
                    "sync_tree_route_population_loss_work_after",
                    "sync_tree_route_population_loss_fault_delay_ms",
                    "sync_tree_route_population_loss_fault_position_bytes",
                    "sync_tree_route_population_loss_duration_ms",
                    "sync_tree_route_population_loss_stopped_carrier",
                    "sync_tree_route_population_loss_resource_sha256",
                ):
                    require(
                        manifest[field] == client_receipt[field],
                        "manifest route-population loss evidence "
                        f"disagrees on {field}",
                    )
                if scenario == "sync-tree-route-loss-admission":
                    for field in (
                        "sync_tree_route_loss_admission_started_jobs",
                        "sync_tree_route_loss_admission_ready_bulk",
                        "sync_tree_route_loss_admission_surviving_carrier",
                    ):
                        require(
                            manifest[field] == client_receipt[field],
                            "manifest route-loss admission evidence "
                            f"disagrees on {field}",
                        )
                require(
                    manifest[
                        "sync_tree_route_population_loss_observed_role_count"
                    ]
                    == 1
                    and client_receipt[
                        "sync_tree_route_population_loss_observed"
                    ]
                    is True
                    and device_receipt[
                        "sync_tree_route_population_loss_observed"
                    ]
                    is False
                    and manifest["sync_tree_route_ready_role_count"] == 2
                    and client_receipt["sync_tree_route_ready_bulk"] == 2
                    and device_receipt["sync_tree_route_ready_bulk"] == 2,
                    "guest route-population loss inventory disagrees",
                )
            if scenario == "sync-tree-route-startup-admission":
                for field in (
                    "sync_tree_route_startup_admission_jobs",
                    "sync_tree_route_startup_admission_artifact_bytes",
                    "sync_tree_route_startup_admission_delay_ms",
                    "sync_tree_route_startup_admission_restart_count",
                    "sync_tree_route_startup_admission_ready_bulk_before",
                    "sync_tree_route_startup_admission_ready_bulk_after",
                    "sync_tree_route_startup_admission_stable_samples",
                    "sync_tree_route_startup_admission_carrier",
                    "sync_tree_route_startup_admission_live_jobs_after_join",
                    "sync_tree_route_startup_admission_preserved_carriers",
                    "sync_tree_route_startup_admission_adaptive_selections",
                    "sync_tree_route_startup_admission_activations",
                    "sync_tree_route_startup_admission_work_before",
                    "sync_tree_route_startup_admission_work_after",
                    "sync_tree_route_startup_admission_duration_ms",
                    "sync_tree_route_startup_admission_resource_sha256",
                ):
                    require(
                        manifest[field] == client_receipt[field],
                        "manifest route-startup admission evidence "
                        f"disagrees on {field}",
                    )
                require(
                    manifest[
                        "sync_tree_route_startup_admission_observed_role_count"
                    ]
                    == 1
                    and client_receipt[
                        "sync_tree_route_startup_admission_observed"
                    ]
                    is True
                    and device_receipt[
                        "sync_tree_route_startup_admission_observed"
                    ]
                    is False
                    and manifest["sync_tree_route_ready_role_count"] == 2
                    and client_receipt["sync_tree_route_ready_bulk"] == 2
                    and device_receipt["sync_tree_route_ready_bulk"] == 2,
                    "guest route-startup admission inventory disagrees",
                )
            if scenario == "sync-tree-route-throughput":
                for field in (
                    "sync_tree_route_throughput_jobs_per_phase",
                    "sync_tree_route_throughput_phases",
                    "sync_tree_route_throughput_artifact_bytes",
                    "sync_tree_route_throughput_phase_order",
                    "sync_tree_route_throughput_restart_count",
                    "sync_tree_route_throughput_restart_hold_ms",
                    "sync_tree_route_throughput_fixed_patterns",
                    "sync_tree_route_throughput_adaptive_patterns",
                    "sync_tree_route_throughput_fixed_a_duration_ms",
                    "sync_tree_route_throughput_adaptive_a_duration_ms",
                    "sync_tree_route_throughput_adaptive_b_duration_ms",
                    "sync_tree_route_throughput_fixed_b_duration_ms",
                    "sync_tree_route_throughput_fixed_a_completion_skew_ms",
                    "sync_tree_route_throughput_adaptive_a_completion_skew_ms",
                    "sync_tree_route_throughput_adaptive_b_completion_skew_ms",
                    "sync_tree_route_throughput_fixed_b_completion_skew_ms",
                    "sync_tree_route_throughput_fixed_total_duration_ms",
                    "sync_tree_route_throughput_adaptive_total_duration_ms",
                    "sync_tree_route_throughput_fixed_artifact_bps",
                    "sync_tree_route_throughput_adaptive_artifact_bps",
                    "sync_tree_route_throughput_adaptive_speedup_ppm",
                    "sync_tree_route_throughput_fixed_selections",
                    "sync_tree_route_throughput_adaptive_selections",
                    "sync_tree_route_throughput_reassignments",
                    "sync_tree_route_throughput_activations",
                    "sync_tree_route_throughput_peak_work",
                    "sync_tree_route_throughput_work_after",
                    "sync_tree_route_throughput_fixed_a_resource_sha256",
                    "sync_tree_route_throughput_adaptive_a_resource_sha256",
                    "sync_tree_route_throughput_adaptive_b_resource_sha256",
                    "sync_tree_route_throughput_fixed_b_resource_sha256",
                ):
                    require(
                        manifest[field] == client_receipt[field],
                        "manifest route-throughput evidence "
                        f"disagrees on {field}",
                    )
                require(
                    manifest[
                        "sync_tree_route_throughput_observed_role_count"
                    ]
                    == 1
                    and client_receipt[
                        "sync_tree_route_throughput_observed"
                    ]
                    is True
                    and device_receipt[
                        "sync_tree_route_throughput_observed"
                    ]
                    is False
                    and manifest["sync_tree_route_ready_role_count"] == 2
                    and client_receipt["sync_tree_route_ready_bulk"] == 2
                    and device_receipt["sync_tree_route_ready_bulk"] == 2,
                    "guest route-throughput inventory disagrees",
                )
            if scenario in SYNC_CONCURRENT_CANCEL_SCENARIOS:
                for field in (
                    "sync_tree_route_concurrent_cancel_jobs",
                    "sync_tree_route_concurrent_cancel_artifact_bytes",
                    "sync_tree_route_concurrent_cancel_requested",
                    "sync_tree_route_concurrent_cancel_completed",
                    "sync_tree_route_concurrent_cancel_survivors",
                    "sync_tree_route_concurrent_cancel_survivor_activations",
                    "sync_tree_route_concurrent_cancel_pattern",
                    "sync_tree_route_concurrent_cancel_route_zero",
                    "sync_tree_route_concurrent_cancel_route_one",
                    "sync_tree_route_concurrent_cancel_tail_ms",
                    "sync_tree_route_concurrent_cancel_work_before",
                    "sync_tree_route_concurrent_cancel_work_after",
                    "sync_tree_route_concurrent_cancel_reassignments_delta",
                    "sync_tree_route_concurrent_cancel_adaptive_selections",
                    "sync_tree_route_concurrent_cancel_resource_sha256",
                ):
                    require(
                        manifest[field] == client_receipt[field],
                        "manifest concurrent route-cancellation evidence "
                        f"disagrees on {field}",
                    )
                require(
                    manifest[
                        "sync_tree_route_concurrent_cancel_observed_role_count"
                    ]
                    == 1
                    and client_receipt[
                        "sync_tree_route_concurrent_cancel_observed"
                    ]
                    is True
                    and device_receipt[
                        "sync_tree_route_concurrent_cancel_observed"
                    ]
                    is False
                    and manifest["sync_tree_route_ready_role_count"] == 2
                    and client_receipt["sync_tree_route_ready_bulk"] == 2
                    and device_receipt["sync_tree_route_ready_bulk"] == 2,
                    "guest concurrent cancellation route inventory disagrees",
                )
            if scenario in {
                "sync-tree-route-cancel",
                "sync-tree-route-loss-cancel",
                "sync-tree-route-cancel-loss",
                "sync-tree-route-cancel-race",
                "sync-tree-route-cancel-race-loss-first",
            }:
                for field in (
                    "sync_tree_route_cancel_carrier",
                    "sync_tree_route_cancel_worker_id",
                    "sync_tree_route_cancel_tail_ms",
                    "sync_tree_route_cancel_work_before",
                    "sync_tree_route_cancel_work_after",
                    "sync_tree_route_cancel_reassignments_delta",
                    "sync_tree_route_cancel_adaptive_selections",
                ):
                    require(
                        client_receipt[field] == device_receipt[field]
                        and manifest[field] == client_receipt[field],
                        f"manifest synchronization route-cancellation evidence "
                        f"disagrees on {field}",
                    )
                require(
                    manifest["sync_tree_route_cancel_observed_role_count"] == 2
                    and client_receipt["sync_tree_route_cancel_observed"] is True
                    and device_receipt["sync_tree_route_cancel_observed"] is True
                    and manifest["sync_tree_route_ready_role_count"] == 2
                    and client_receipt["sync_tree_route_ready_bulk"] == 2
                    and device_receipt["sync_tree_route_ready_bulk"] == 2,
                    "guest synchronization cancellation route inventory disagrees",
                )
                if scenario == "sync-tree-route-loss-cancel":
                    require(
                        client_receipt["sync_tree_route_cancel_carrier"]
                        == client_receipt[
                            "sync_tree_route_loss_final_carrier"
                        ]
                        and client_receipt[
                            "sync_tree_route_cancel_carrier"
                        ]
                        != client_receipt[
                            "sync_tree_route_loss_stopped_carrier"
                        ],
                        "loss-before-cancel carrier order is invalid",
                    )
                if scenario == "sync-tree-route-cancel-loss":
                    require(
                        client_receipt[
                            "sync_tree_route_cancel_loss_observed"
                        ]
                        is True
                        and device_receipt[
                            "sync_tree_route_cancel_loss_observed"
                        ]
                        is False
                        and manifest[
                            "sync_tree_route_cancel_loss_observed"
                        ]
                        is True
                        and client_receipt[
                            "sync_tree_route_cancel_carrier"
                        ]
                        == client_receipt[
                            "sync_tree_route_loss_final_carrier"
                        ]
                        == client_receipt[
                            "sync_tree_route_loss_stopped_carrier"
                        ],
                        "cancel-before-loss carrier order is invalid",
                    )
                if scenario in SYNC_ROUTE_CANCEL_RACE_SCENARIOS:
                    require(
                        client_receipt[
                            "sync_tree_route_cancel_race_observed"
                        ]
                        is True
                        and device_receipt[
                            "sync_tree_route_cancel_race_observed"
                        ]
                        is False
                        and manifest[
                            "sync_tree_route_cancel_race_observed"
                        ]
                        is True
                        and manifest[
                            "sync_tree_route_cancel_race_outcome"
                        ]
                        == client_receipt[
                            "sync_tree_route_cancel_race_outcome"
                        ]
                        == device_receipt[
                            "sync_tree_route_cancel_race_outcome"
                        ]
                        and manifest[
                            "sync_tree_route_cancel_race_cleanup_retries"
                        ]
                        == client_receipt[
                            "sync_tree_route_cancel_race_cleanup_retries"
                        ]
                        == device_receipt[
                            "sync_tree_route_cancel_race_cleanup_retries"
                        ]
                        and client_receipt[
                            "sync_tree_route_cancel_carrier"
                        ]
                        == client_receipt[
                            "sync_tree_route_loss_stopped_carrier"
                        ],
                        "cancel/loss race carrier order is invalid",
                    )
            if scenario == "sync-tree-adversity":
                for field in (
                    "sync_tree_rollback_refused",
                    "sync_tree_fork_refused",
                    "sync_tree_enospc_observed",
                    "sync_tree_enospc_retry_observed",
                ):
                    require(
                        client_receipt[field] == device_receipt[field],
                        f"guest synchronization tree adversity evidence disagrees on {field}",
                    )
                for field in (
                    "sync_tree_enospc_reserved_bytes",
                    "sync_tree_enospc_failure_free_bytes",
                    "sync_tree_publisher_restart_count",
                ):
                    require(
                        client_receipt[field] == device_receipt[field]
                        and manifest[field] == client_receipt[field],
                        f"manifest synchronization tree adversity evidence disagrees on {field}",
                    )
            if scenario == "sync-tree-pressure":
                for field in (
                    "sync_tree_queue_saturation_observed",
                    "sync_tree_queue_retry_observed",
                    "sync_tree_worker_queue_bound",
                    "sync_tree_worker_active_at_saturation",
                    "sync_tree_worker_queued_at_saturation",
                    "sync_tree_worker_rejected_delta",
                    "sync_tree_pressure_a_head_record",
                    "sync_tree_pressure_b_head_record",
                ):
                    require(
                        client_receipt[field] == device_receipt[field],
                        f"guest synchronization tree worker-pressure evidence disagrees on {field}",
                    )
                for field in (
                    "sync_tree_worker_queue_bound",
                    "sync_tree_worker_rejected_delta",
                    "sync_tree_pressure_a_head_record",
                    "sync_tree_pressure_b_head_record",
                ):
                    require(
                        manifest[field] == client_receipt[field],
                        f"manifest synchronization tree worker-pressure evidence disagrees on {field}",
                    )
            if scenario in SYNC_TREE_QUOTA_SCENARIOS:
                for field in (
                    "sync_tree_quota_observed",
                    "sync_tree_quota_store_bytes",
                    "sync_tree_quota_inventory_bytes",
                    "sync_tree_quota_candidate_head_record",
                    "sync_tree_quota_candidate_artifact_sha256",
                    "sync_tree_quota_candidate_manifest_sha256",
                ):
                    require(
                        client_receipt[field] == device_receipt[field],
                        f"guest synchronization tree quota evidence disagrees on {field}",
                    )
                extended_fields = (
                    "sync_tree_quota_kind",
                    "sync_tree_quota_maximum_objects",
                    "sync_tree_quota_inventory_objects",
                )
                if scenario == "sync-tree-object-quota" or any(
                    field in manifest for field in extended_fields
                ):
                    for field in extended_fields:
                        require(
                            client_receipt[field] == device_receipt[field],
                            f"guest synchronization tree quota evidence disagrees on {field}",
                        )
                for field in (
                    "sync_tree_quota_store_bytes",
                    "sync_tree_quota_inventory_bytes",
                    "sync_tree_quota_candidate_head_record",
                    "sync_tree_quota_candidate_artifact_sha256",
                    "sync_tree_quota_candidate_manifest_sha256",
                ):
                    require(
                        manifest[field] == client_receipt[field],
                        f"manifest synchronization tree quota evidence disagrees on {field}",
                    )
                if scenario == "sync-tree-object-quota" or any(
                    field in manifest for field in extended_fields
                ):
                    for field in extended_fields:
                        require(
                            manifest[field] == client_receipt[field],
                            f"manifest synchronization tree quota evidence disagrees on {field}",
                        )
            if scenario == "sync-tree-read-only":
                for field in (
                    "sync_tree_read_only_observed",
                    "sync_tree_read_only_pull_refused",
                    "sync_tree_read_only_activation_refused",
                    "sync_tree_read_only_retry_observed",
                    "sync_tree_read_only_head_record",
                    "sync_tree_read_only_artifact_sha256",
                    "sync_tree_read_only_manifest_sha256",
                ):
                    require(
                        client_receipt[field] == device_receipt[field],
                        f"guest synchronization tree read-only evidence disagrees on {field}",
                    )
                for field in (
                    "sync_tree_read_only_head_record",
                    "sync_tree_read_only_artifact_sha256",
                    "sync_tree_read_only_manifest_sha256",
                ):
                    require(
                        manifest[field] == client_receipt[field],
                        f"manifest synchronization tree read-only evidence disagrees on {field}",
                    )
            if scenario == "sync-tree-memory":
                memory_fields = (
                    "sync_tree_memory_ceiling_kib",
                    "sync_tree_memory_entries",
                    "sync_tree_memory_artifact_bytes",
                    "sync_tree_memory_head_record",
                    "sync_tree_memory_artifact_sha256",
                    "sync_tree_memory_manifest_sha256",
                    "sync_tree_memory_publisher_baseline_hwm_kib",
                    "sync_tree_memory_publisher_post_publish_hwm_kib",
                    "sync_tree_memory_publisher_peak_hwm_kib",
                    "sync_tree_memory_publisher_delta_hwm_kib",
                    "sync_tree_memory_subscriber_baseline_hwm_kib",
                    "sync_tree_memory_subscriber_post_pull_hwm_kib",
                    "sync_tree_memory_subscriber_peak_hwm_kib",
                    "sync_tree_memory_subscriber_delta_hwm_kib",
                    "sync_tree_memory_pair_peak_hwm_kib",
                    "sync_tree_memory_pair_maximum_delta_hwm_kib",
                )
                require(
                    client_receipt["sync_tree_memory_observed"] is True
                    and device_receipt["sync_tree_memory_observed"] is True,
                    "guest synchronization tree memory observation is missing",
                )
                for field in memory_fields:
                    require(
                        client_receipt[field] == device_receipt[field],
                        f"guest synchronization tree memory evidence disagrees on {field}",
                    )
                    require(
                        manifest[field] == client_receipt[field],
                        f"manifest synchronization tree memory evidence disagrees on {field}",
                    )
            if scenario == "sync-tree-source-corrupt":
                source_corrupt_fields = (
                    "sync_tree_source_corrupt_head_record",
                    "sync_tree_source_corrupt_artifact_sha256",
                    "sync_tree_source_corrupt_manifest_sha256",
                    "sync_tree_source_corrupt_artifact_bytes",
                    "sync_tree_source_corrupt_manifest_bytes",
                    "sync_tree_source_corrupt_quarantined_objects",
                    "sync_tree_source_corrupt_quarantined_bytes",
                )
                for field in (
                    "sync_tree_source_corrupt_observed",
                    "sync_tree_source_corrupt_refused",
                    "sync_tree_source_corrupt_repaired",
                    "sync_tree_source_corrupt_retry_observed",
                    *source_corrupt_fields,
                ):
                    require(
                        client_receipt[field] == device_receipt[field],
                        f"guest publisher-source corruption evidence disagrees on {field}",
                    )
                for field in source_corrupt_fields:
                    require(
                        manifest[field] == client_receipt[field],
                        f"manifest publisher-source corruption evidence disagrees on {field}",
                    )
            if scenario == "sync-tree-destination-corrupt":
                destination_corrupt_fields = (
                    "sync_tree_destination_corrupt_head_record",
                    "sync_tree_destination_corrupt_artifact_sha256",
                    "sync_tree_destination_corrupt_manifest_sha256",
                    "sync_tree_destination_corrupt_artifact_bytes",
                    "sync_tree_destination_corrupt_manifest_bytes",
                    "sync_tree_destination_corrupt_file_id",
                    "sync_tree_destination_corrupt_position_bytes",
                    "sync_tree_destination_corrupt_committed_before_failure",
                    "sync_tree_destination_corrupt_retry_requested_objects",
                )
                for field in (
                    "sync_tree_destination_corrupt_observed",
                    "sync_tree_destination_corrupt_rejected",
                    "sync_tree_destination_corrupt_retry_observed",
                    *destination_corrupt_fields,
                ):
                    require(
                        client_receipt[field] == device_receipt[field],
                        f"guest subscriber-destination corruption evidence disagrees on {field}",
                    )
                for field in destination_corrupt_fields:
                    require(
                        manifest[field] == client_receipt[field],
                        f"manifest subscriber-destination corruption evidence disagrees on {field}",
                    )
            if scenario == "sync-tree-control-replay":
                control_replay_summary_fields = (
                    "sync_tree_control_replay_head_record",
                    "sync_tree_control_replay_artifact_sha256",
                    "sync_tree_control_replay_manifest_sha256",
                    "sync_tree_control_replay_admitted_before_replay",
                    "sync_tree_control_replay_publisher_head_requests_delta",
                    "sync_tree_control_replay_publisher_object_requests_delta",
                    "sync_tree_control_replay_publisher_file_offers_delta",
                    "sync_tree_control_replay_publisher_replay_hits_delta",
                    "sync_tree_control_replay_publisher_replay_conflicts_delta",
                    "sync_tree_control_replay_subscriber_incoming_head_results_delta",
                    "sync_tree_control_replay_subscriber_incoming_object_results_delta",
                    "sync_tree_control_replay_subscriber_outgoing_object_requests_delta",
                )
                for field in (
                    "sync_tree_control_replay_observed",
                    "sync_tree_control_replay_exact_replay_observed",
                    "sync_tree_control_replay_reordered_result_observed",
                    "sync_tree_control_replay_conflict_refused",
                    "sync_tree_control_replay_activation_observed",
                    *control_replay_summary_fields,
                ):
                    require(
                        client_receipt[field] == device_receipt[field],
                        f"guest synchronization control replay evidence disagrees on {field}",
                    )
                for field in control_replay_summary_fields:
                    require(
                        manifest[field] == client_receipt[field],
                        f"manifest synchronization control replay evidence disagrees on {field}",
                    )
        if scenario in {
            "sync-content-multi-source-loss",
            "sync-content-multi-route-actual-tor-loss",
        }:
            client_receipt = load(
                proof_root / manifest["receipts"]["client"]["path"]
            )
            device_receipt = load(
                proof_root / manifest["receipts"]["device"]["path"]
            )
            for field in (
                "multi_source_loss_observed",
                "multi_source_loss_recovery_observed",
                "multi_source_loss_first_job_id",
                "multi_source_loss_replacement_job_id",
                "multi_source_loss_committed_objects",
                "multi_source_loss_fetched_bytes",
                "multi_source_loss_initial_epoch",
                "multi_source_loss_recovered_epoch",
                "multi_source_loss_restart_count",
                "multi_source_loss_staging_clean",
                "multi_source_loss_head_fenced",
                "multi_source_loss_activation_fenced",
            ):
                require(
                    client_receipt[field] == device_receipt[field],
                    f"guest selected-source loss evidence disagrees on {field}",
                )
            if scenario == "sync-content-multi-route-actual-tor-loss":
                for field in (
                    "multi_source_route_loss_observed",
                    "multi_source_route_loss_target",
                    "multi_source_route_loss_fault_worker",
                    "multi_source_route_loss_recovered_worker",
                    "multi_source_route_loss_position_bytes",
                    "multi_source_route_loss_carrier_losses",
                    "multi_source_route_loss_reassignments",
                    "multi_source_route_loss_recoveries",
                    "multi_source_route_loss_primary_epoch",
                    "multi_source_route_loss_secondary_epoch",
                ):
                    require(
                        client_receipt[field] == device_receipt[field],
                        "guest exact routed source-loss evidence disagrees on "
                        f"{field}",
                    )
        if scenario in SYNC_RANGE_SCENARIOS:
            client_receipt = load(
                proof_root / manifest["receipts"]["client"]["path"]
            )
            device_receipt = load(
                proof_root / manifest["receipts"]["device"]["path"]
            )
            for field in (
                "sync_range_observed",
                "sync_range_fallback_observed",
                "sync_corrupt_basis_preserved",
                "sync_range_retry_observed",
                "sync_range_restart_resume_observed",
            ):
                require(
                    client_receipt.get(field, False)
                    == device_receipt.get(field, False),
                    f"guest {field} evidence disagrees",
                )
            for field in (
                "sync_range_count",
                "sync_range_reused_bytes",
                "sync_range_fetched_bytes",
                "sync_range_retry_position_bytes",
                "sync_range_retry_retained_bytes",
                "sync_range_retry_resumed_bytes",
                "sync_range_retry_discarded_bytes",
                "sync_range_retry_retention_fallbacks",
                "sync_range_retry_first_file_id",
                "sync_range_retry_second_file_id",
                "sync_range_restart_interrupted_bytes",
                "sync_range_restart_retained_bytes",
                "sync_range_restart_resumed_attempts",
                "sync_range_restart_resumed_bytes",
                "sync_range_restart_suffix_bytes",
                "sync_range_restart_first_job_id",
                "sync_range_restart_second_job_id",
                "sync_range_restart_first_attempt_id",
                "sync_range_restart_second_attempt_id",
                "sync_range_restart_first_message_id",
                "sync_range_restart_second_message_id",
                "sync_range_restart_first_file_id",
                "sync_range_restart_second_file_id",
            ):
                default = "" if field.endswith("file_id") else 0
                require(
                    client_receipt.get(field, default)
                    == device_receipt.get(field, default)
                    and manifest.get(field, default)
                    == client_receipt.get(field, default),
                    f"manifest {field} disagrees with range receipts",
                )
        if scenario == "sync-file-repair":
            client_receipt = load(
                proof_root / manifest["receipts"]["client"]["path"]
            )
            device_receipt = load(
                proof_root / manifest["receipts"]["device"]["path"]
            )
            repair_fields = (
                "sync_repair_observed",
                "sync_repair_recovery_observed",
                "sync_repair_clean_retry_observed",
                "sync_repair_quarantine_preserved",
                "sync_repair_state_preserved",
                "sync_repair_inspected_objects",
                "sync_repair_quarantined_objects",
                "sync_repair_quarantined_bytes",
            )
            if gc_repair:
                repair_fields += receipt_gc_fields
            for field in repair_fields:
                require(
                    client_receipt[field] == device_receipt[field],
                    f"guest synchronization repair evidence disagrees on {field}",
                )
        require(
            len(sync_restart_evidence) == 2
            and manifest.get("sync_client_daemon_restart_count", 0)
            == sync_restart_evidence["client"][0]
            and manifest.get("sync_interrupted_staging_bytes", 0)
            == sync_restart_evidence["client"][1]
            and manifest.get("sync_restart_recovered_role_count", 0)
            == sum(
                int(sync_restart_evidence[role][2]) for role in ROLES
            )
            and manifest.get("sync_unclean_stop_count", 0)
            == sum(int(sync_restart_evidence[role][3]) for role in ROLES),
            "manifest synchronization restart evidence disagrees with receipts",
        )
        if sync_cancellation:
            client_receipt = load(
                proof_root / manifest["receipts"]["client"]["path"]
            )
            device_receipt = load(
                proof_root / manifest["receipts"]["device"]["path"]
            )
            require(
                client_receipt["sync_cancelled_job_id"]
                == device_receipt["sync_cancelled_job_id"]
                and manifest.get("sync_cancelled_staging_bytes")
                == client_receipt["sync_cancelled_staging_bytes"]
                and manifest.get("sync_cancelled_receive_count")
                == client_receipt["sync_cancelled_receive_count"],
                "manifest synchronization cancellation evidence disagrees with receipts",
            )
        if scenario == "sync-file-disconnect":
            client_receipt = load(
                proof_root / manifest["receipts"]["client"]["path"]
            )
            device_receipt = load(
                proof_root / manifest["receipts"]["device"]["path"]
            )
            require(
                manifest.get("sync_disconnect_staging_bytes")
                == client_receipt["sync_disconnect_staging_bytes"]
                and manifest.get("sync_disconnect_recovered_role_count")
                == sum(
                    int(receipt["sync_disconnect_retry_observed"])
                    for receipt in (client_receipt, device_receipt)
                )
                and client_receipt["sync_disconnect_cleanup_observed"] is True
                and device_receipt["sync_disconnect_cleanup_observed"] is True
                and manifest.get("sync_disconnect_minimum_stable_samples")
                == min(
                    client_receipt["sync_disconnect_stable_samples"],
                    device_receipt["sync_disconnect_stable_samples"],
                ),
                "manifest synchronization disconnect evidence disagrees with receipts",
            )
        if scenario == "sync-file-guest-restart":
            client_receipt = load(
                proof_root / manifest["receipts"]["client"]["path"]
            )
            device_receipt = load(
                proof_root / manifest["receipts"]["device"]["path"]
            )
            require(
                manifest.get("sync_guest_restart_staging_bytes")
                == client_receipt["sync_guest_restart_staging_bytes"]
                and manifest.get("sync_guest_restart_recovered_role_count")
                == sum(
                    int(receipt["sync_guest_restart_retry_observed"])
                    for receipt in (client_receipt, device_receipt)
                )
                and client_receipt["sync_guest_restart_cleanup_observed"]
                is True
                and device_receipt["sync_guest_restart_cleanup_observed"]
                is True
                and manifest.get("sync_guest_restart_minimum_stable_samples")
                == min(
                    client_receipt["sync_guest_restart_stable_samples"],
                    device_receipt["sync_guest_restart_stable_samples"],
                ),
                "manifest synchronization guest-restart evidence disagrees with receipts",
            )
        if scenario == "sync-file-pause":
            client_receipt = load(
                proof_root / manifest["receipts"]["client"]["path"]
            )
            device_receipt = load(
                proof_root / manifest["receipts"]["device"]["path"]
            )
            require(
                manifest.get("sync_pause_observed_role_count") == 2
                and manifest.get("sync_pause_position_bytes")
                == client_receipt["sync_pause_position_bytes"]
                == device_receipt["sync_pause_position_bytes"]
                and manifest.get("sync_pause_minimum_stable_samples")
                == client_receipt["sync_pause_stable_samples"]
                == device_receipt["sync_pause_stable_samples"]
                and manifest.get("sync_pause_file_id")
                == client_receipt["sync_pause_file_id"]
                == device_receipt["sync_pause_file_id"],
                "manifest synchronization pause evidence disagrees with receipts",
            )
    if compact is not None:
        export = load(proof_root / "compact-export.json")
        require(export.get("schema") == COMPACT_SCHEMA, "compact export manifest schema mismatch")
        require(export.get("status") == "passed", "compact export did not pass")
        require(export.get("contains_secrets") is False, "compact export is not content-free")
        require(export.get("source_proof_id") == compact.get("source_proof_id"), "compact source proof mismatch")
        require(
            PAIR_NAME.fullmatch(str(export.get("source_proof_id", ""))) is not None,
            "compact source proof identity is invalid",
        )
        require(
            export.get("source_manifest_sha256")
            == compact.get("source_manifest_sha256"),
            "compact source manifest binding mismatch",
        )
        require(
            export.get("source_private_artifacts_omitted")
            == [
                "bootstrap-secret-key",
                "guest-disks",
                "injected-identities",
                "runtime-state",
            ],
            "compact omitted-private classification mismatch",
        )
        files = export.get("files")
        expected_files = {
            "pair-manifest.json",
            "client/direct-cloud-hypervisor-live-chain.json",
            "client/prelaunch/launch/cloud-hypervisor-launch.json",
            "client/live/workspace-export/guest-receipts/iotox/pair.json",
            "device/prelaunch/launch/cloud-hypervisor-launch.json",
        }
        if scenario in GUEST_RESTART_SCENARIOS:
            expected_files.update({
                "device/direct-cloud-hypervisor-live-chain.json",
                "device/live/cloud-hypervisor-launch.json",
                "device-restart/direct-cloud-hypervisor-live-chain.json",
                "device-restart/live/workspace-export/guest-receipts/iotox/pair.json",
            })
        else:
            expected_files.update({
                "device/direct-cloud-hypervisor-live-chain.json",
                "device/live/workspace-export/guest-receipts/iotox/pair.json",
            })
        if scenario in CONTENT_SCENARIOS:
            expected_files.add(
                "client/live/workspace-export/iotox-rendezvous/"
                "client.sync-complete"
            )
        if scenario in CONTENT_RESTART_SCENARIOS:
            expected_files.update({
                "client/live/workspace-export/iotox-rendezvous/"
                "client.sync-interruption-ready",
                "client/live/workspace-export/iotox-rendezvous/"
                "client.sync-crash-state",
            })
        if scenario == "sync-content-multi-source-loss":
            expected_files.update({
                "client/live/workspace-export/iotox-rendezvous/"
                "client.multi-source-loss-failed",
                "client/live/workspace-export/iotox-rendezvous/"
                "client.multi-source-loss-recovered",
                "device/live/workspace-export/iotox-rendezvous/"
                "device.multi-source-loss-ready",
                "device/live/workspace-export/iotox-rendezvous/"
                "device.multi-source-loss-stopped",
                "device/live/workspace-export/iotox-rendezvous/"
                "device.multi-source-loss-recovered",
            })
            if manifest.get(
                "multi_source_loss_durable_replica_cold_start", False
            ):
                expected_files.add(
                    "device/live/workspace-export/iotox-rendezvous/"
                    "device.multi-source-loss-replica-imported"
                )
        if scenario == "sync-content-multi-route-actual-tor-loss":
            expected_files.update({
                "client/live/workspace-export/iotox-rendezvous/"
                "client.multi-source-loss-failed",
                "client/live/workspace-export/iotox-rendezvous/"
                "client.multi-source-loss-recovered",
            })
        if scenario in {
            "sync-content-multi-route-actual-tor",
            "sync-content-multi-route-actual-tor-loss",
        }:
            expected_files.add(
                "client/live/workspace-export/iotox-rendezvous/"
                "client.content-multi-route"
            )
        if scenario == "sync-content-same-source-multi-route-actual-tor":
            expected_files.add(
                "client/live/workspace-export/iotox-rendezvous/"
                "client.content-same-source-multi-route"
            )
        if scenario in CONTENT_MULTI_SOURCE_SCENARIOS and route == "forced-tcp":
            expected_files.add("host-bootstrap-secondary/PUBLIC_ID.txt")
        if actual_i2p:
            expected_files.update({
                "client.tox-i2p.pcapng",
                "client.tox-i2p.dumpcap.log",
                "device.tox-i2p.pcapng",
                "device.tox-i2p.dumpcap.log",
                "tox-i2p-containment.json",
                "i2p-fronts/topology-final.json",
                "i2p-fronts/adapter.audit.jsonl",
                "i2p-fronts/forward-1.audit.jsonl",
                "i2p-fronts/forward-2.audit.jsonl",
                "i2p-fronts/forward-3.audit.jsonl",
            })
            if scenario == "i2p-service-restart":
                expected_files.update({
                    "i2p-fronts/forward-restart-1.audit.jsonl",
                    "i2p-fronts/forward-restart-2.audit.jsonl",
                    "i2p-fronts/forward-restart-3.audit.jsonl",
                })
            if scenario in {
                "sync-tree-route-private-actual-i2p-loss",
                "sync-file-range-actual-i2p-loss",
            }:
                expected_files.add("actual-i2p-fail-closed-loss.json")
        if scenario in RATOX_SCENARIOS:
            expected_files.update({
                "client/live/workspace-export/guest-receipts/iotox/ratox-controller-capture.tsv",
                "device/live/workspace-export/guest-receipts/iotox/ratox-host-events.txt",
                "device/live/workspace-export/guest-receipts/iotox/ratox-host-status.txt",
            })
            resource_files = {
                f"{role}/live/workspace-export/guest-receipts/iotox/ratox-resource-interval.tsv"
                for role in ROLES
            }
            present_resources = resource_files & set(files)
            require(
                len(present_resources) in {0, len(resource_files)},
                "compact Ratox resource intervals are only partially present",
            )
            expected_files.update(present_resources)
            status_files = {
                f"{role}/live/workspace-export/guest-receipts/iotox/ratox-agent-status.txt"
                for role in ROLES
            }
            present_statuses = status_files & set(files)
            require(
                len(present_statuses) in {0, len(status_files)},
                "compact Ratox agent statuses are only partially present",
            )
            expected_files.update(present_statuses)
        if scenario == "ratox-route-impairment":
            expected_files.update({
                "ratox-route-impairment.json",
                "client/live/workspace-export/guest-receipts/iotox/"
                "ratox-heartbeat-capture.tsv",
            })
        if scenario in {
            "ratox-route-loss",
            "ratox-cli-reconnect",
            "ratox-cli-reconnect-repeated",
            "ratox-route-actual-tor-loss",
            "ratox-route-actual-tor-adversary",
        }:
            expected_files.update({
                "ratox-route-loss.json",
                "client/live/workspace-export/guest-receipts/iotox/"
                "ratox-heartbeat-capture.tsv",
                "client/live/workspace-export/guest-receipts/iotox/"
                "ratox-route-loss-probe.json",
                "device/live/workspace-export/guest-receipts/iotox/"
                "ratox-host-loss-events.txt",
                "device/live/workspace-export/guest-receipts/iotox/"
                "ratox-host-loss-status.txt",
            })
        if scenario == "ratox-route-actual-tor-soak":
            expected_files.update({
                "actual-tor-ratox-churn.json",
                "client/live/workspace-export/guest-receipts/iotox/"
                "ratox-heartbeat-capture.tsv",
                "client/live/workspace-export/guest-receipts/iotox/"
                "ratox-circuit-churn-probe.json",
            })
            for role, ordinal in (("client", 20), ("device", 100)):
                for phase in ("before", "after"):
                    for status in ("stream", "circuit"):
                        expected_files.add(
                            f"tor-{role}-churn-{ordinal}-{phase}-{status}-status.txt"
                        )
        if scenario == "sync-tree-route-population":
            expected_files.update({
                "client/live/workspace-export/guest-receipts/iotox/"
                "sync-route-population-fixed-resource.tsv",
                "client/live/workspace-export/guest-receipts/iotox/"
                "sync-route-population-adaptive-resource.tsv",
            })
        if scenario in SYNC_CONCURRENT_CANCEL_SCENARIOS:
            expected_files.add(
                "client/live/workspace-export/guest-receipts/iotox/"
                "sync-route-concurrent-cancel-resource.tsv"
            )
        if scenario in {
            "sync-tree-route-population-loss",
            "sync-tree-route-loss-admission",
        }:
            expected_files.add(
                "client/live/workspace-export/guest-receipts/iotox/"
                "sync-route-population-loss-resource.tsv"
            )
        if scenario == "sync-tree-route-startup-admission":
            expected_files.add(
                "client/live/workspace-export/guest-receipts/iotox/"
                "sync-route-startup-admission-resource.tsv"
            )
        if scenario == "sync-tree-route-throughput":
            expected_files.update(
                "client/live/workspace-export/guest-receipts/iotox/"
                f"sync-route-throughput-{phase}-resource.tsv"
                for phase in (
                    "fixed-a",
                    "adaptive-a",
                    "adaptive-b",
                    "fixed-b",
                )
            )
        if scenario in CONTENT_LANE_SCIENCE_SCENARIOS:
            expected_files.add(
                "client/live/workspace-export/guest-receipts/iotox/"
                "content-lane-science.tsv"
            )
            expected_files.update(
                "client/live/workspace-export/guest-receipts/iotox/"
                f"content-lane-science-cap-{cap}-resource.tsv"
                for cap in (1, 2, 4, 8)
            )
        if scenario in {
            "sync-content-ratox-latency-science",
            "sync-content-ratox-cap-2-sla",
        }:
            expected_files.update({
                "client/live/workspace-export/guest-receipts/iotox/"
                "content-ratox-overlap-metadata.tsv",
                "client/live/workspace-export/guest-receipts/iotox/"
                "content-ratox-latency.tsv",
                "client/live/workspace-export/iotox-rendezvous/"
                "client.content-ratox-readiness",
                "client/live/workspace-export/guest-receipts/iotox/"
                "content-ratox-timeline.tsv",
            })
        if scenario == "sync-content-ratox-post-bulk-admission":
            expected_files.update({
                "client/live/workspace-export/guest-receipts/iotox/"
                "content-ratox-post-bulk-readiness.tsv",
                "client/live/workspace-export/guest-receipts/iotox/"
                "content-ratox-post-bulk-capture.tsv",
                "client/live/workspace-export/guest-receipts/iotox/"
                "content-ratox-post-bulk-admission.tsv",
            })
        if scenario in REPEATED_RANGE_LOSS_COUNTS:
            expected_files.update({
                "client/live/workspace-export/iotox-rendezvous/"
                "client.sync-range-loss-progress",
                "client/live/workspace-export/iotox-rendezvous/"
                "client.sync-range-postconditions",
            })
        if scenario == "sync-file-range-triple-route-loss":
            expected_files.update({
                "device/live/workspace-export/iotox-rendezvous/"
                "device.sync-range-live-status",
                "device/live/workspace-export/iotox-rendezvous/"
                "device.sync-range-live-routes",
            })
        if scenario == "sync-file-range-restart-resume":
            expected_files.update({
                "client/live/workspace-export/iotox-rendezvous/"
                "client.sync-range-restart-ready",
                "client/live/workspace-export/iotox-rendezvous/"
                "client.sync-range-crash-state",
                "client/live/workspace-export/iotox-rendezvous/"
                "client.sync-range-reconnect-ready",
                "client/live/workspace-export/iotox-rendezvous/"
                "client.sync-range-restart-reacquired",
                "device/live/workspace-export/iotox-rendezvous/"
                "device.sync-range-restart-armed",
                "device/live/workspace-export/iotox-rendezvous/"
                "device.sync-range-restart-offline",
                "device/live/workspace-export/iotox-rendezvous/"
                "device.sync-range-restart-recovered",
            })
        if scenario in RATOX_BULK_SCENARIOS:
            expected_files.add(
                "client/live/workspace-export/guest-receipts/iotox/ratox-bulk-observation.tsv"
            )
        if scenario in RATOX_STRIPE_SCENARIOS:
            expected_files.update({
                "client/live/workspace-export/guest-receipts/iotox/ratox-stripe-routes.tsv",
                "device/live/workspace-export/guest-receipts/iotox/ratox-stripe-routes.tsv",
            })
        if scenario == "packet-loss":
            expected_files.update({
                "client/live/workspace-export/guest-receipts/iotox/packet-loss-burst.tsv",
                "device/live/workspace-export/guest-receipts/iotox/packet-loss-burst.tsv",
            })
        if scenario == "proxy-restart":
            expected_files.update({
                "client.tox-tor.pcapng",
                "client.tox-tor.dumpcap.log",
                "device.tox-tor.pcapng",
                "device.tox-tor.dumpcap.log",
                "socks5-initial-audit.jsonl",
                "socks5-restart-audit.jsonl",
                "tox-tor-containment.json",
            })
        elif scenario == "sync-tree-route-private-mixed":
            expected_files.update({
                "client.tox-tor.pcapng",
                "client.tox-tor.dumpcap.log",
                "device.tox-tor.pcapng",
                "device.tox-tor.dumpcap.log",
                "socks5-initial-audit.jsonl",
                "mixed-route-containment.json",
            })
        elif scenario in {
            "sync-tree-route-private-actual-tor",
            "sync-tree-route-private-actual-tor-payload",
            "sync-tree-route-private-actual-tor-loss",
            "sync-content-route-private-actual-tor",
            "sync-content-same-source-multi-route-actual-tor",
            "sync-content-multi-route-actual-tor",
            "sync-content-multi-route-actual-tor-loss",
        }:
            expected_files.update({
                "client.tox-tor.pcapng",
                "client.tox-tor.dumpcap.log",
                "device.tox-tor.pcapng",
                "device.tox-tor.dumpcap.log",
                "actual-tor-mixed-route-containment.json",
            })
            if scenario == "sync-tree-route-private-actual-tor-loss":
                expected_files.update({
                    "actual-tor-process-loss.json",
                    "tor-client-pre-loss-control-events.txt",
                    "tor-client-pre-loss-bootstrap-status.txt",
                    "tor-client-pre-loss-circuit-status.txt",
                    "tor-client-recovered-control-events.txt",
                    "tor-client-recovered-bootstrap-status.txt",
                    "tor-client-recovered-circuit-status.txt",
                    "tor-device-continuous-control-events.txt",
                    "tor-device-continuous-bootstrap-status.txt",
                    "tor-device-continuous-circuit-status.txt",
                })
            else:
                expected_files.update({
                    "tor-client-control-events.txt",
                    "tor-client-bootstrap-status.txt",
                    "tor-client-circuit-status.txt",
                    "tor-device-control-events.txt",
                    "tor-device-bootstrap-status.txt",
                    "tor-device-circuit-status.txt",
                })
        elif scenario == "ratox-route-actual-tor-loss":
            expected_files.update({
                "client.tox-tor.pcapng",
                "client.tox-tor.dumpcap.log",
                "device.tox-tor.pcapng",
                "device.tox-tor.dumpcap.log",
                "actual-tor-route-containment.json",
                "actual-tor-process-loss.json",
                "tor-client-pre-loss-control-events.txt",
                "tor-client-pre-loss-bootstrap-status.txt",
                "tor-client-pre-loss-circuit-status.txt",
                "tor-client-recovered-control-events.txt",
                "tor-client-recovered-bootstrap-status.txt",
                "tor-client-recovered-circuit-status.txt",
                "tor-device-continuous-control-events.txt",
                "tor-device-continuous-bootstrap-status.txt",
                "tor-device-continuous-circuit-status.txt",
            })
        elif scenario == "ratox-route-actual-tor-soak":
            expected_files.update({
                "client.tox-tor.pcapng",
                "client.tox-tor.dumpcap.log",
                "device.tox-tor.pcapng",
                "device.tox-tor.dumpcap.log",
                "actual-tor-route-containment.json",
                "tor-client-control-events.txt",
                "tor-client-bootstrap-status.txt",
                "tor-client-circuit-status.txt",
                "tor-device-control-events.txt",
                "tor-device-bootstrap-status.txt",
                "tor-device-circuit-status.txt",
            })
        elif scenario == "ratox-route-actual-tor-adversary":
            expected_files.update({
                "client.tox-tor.pcapng",
                "client.tox-tor.dumpcap.log",
                "device.tox-tor.pcapng",
                "device.tox-tor.dumpcap.log",
                "actual-tor-route-containment.json",
                "actual-tor-adversarial-boundary.json",
                "actual-tor-client-adversary-audit.jsonl",
                "actual-tor-client-adversary.stdout",
                "actual-tor-client-adversary.stderr",
                "actual-tor-device-adversary-audit.jsonl",
                "actual-tor-device-adversary.stdout",
                "actual-tor-device-adversary.stderr",
                "tor-client-control-events.txt",
                "tor-client-bootstrap-status.txt",
                "tor-client-circuit-status.txt",
                "tor-device-control-events.txt",
                "tor-device-bootstrap-status.txt",
                "tor-device-circuit-status.txt",
            })
        elif scenario in {
            "ratox-route-impairment", "ratox-route-loss",
            "ratox-cli-reconnect",
        } \
                and route == "tox-tor":
            expected_files.update({
                "client.tox-tor.pcapng",
                "client.tox-tor.dumpcap.log",
                "device.tox-tor.pcapng",
                "device.tox-tor.dumpcap.log",
                "socks5-initial-audit.jsonl",
                "tox-tor-containment.json",
            })
        require(isinstance(files, dict), "compact export file inventory is absent")
        require(set(files) == expected_files, "compact export file inventory mismatch")
        observed_files = {
            str(path.relative_to(proof_root))
            for path in proof_root.rglob("*")
            if path.is_file()
        }
        require(
            not any(path.is_symlink() for path in proof_root.rglob("*")),
            "compact export contains a symbolic link",
        )
        require(
            observed_files == expected_files | {"compact-export.json"},
            "compact export contains an undeclared file",
        )
        for relative, expected_digest in files.items():
            path = (proof_root / relative).resolve()
            require(path.is_relative_to(proof_root), "compact export path escapes its root")
            require(path.is_file(), f"compact export file is absent: {relative}")
            require(expected_digest == digest(path), f"compact export digest mismatch: {relative}")
    require(
        observed_stripe_route_restarts == stripe_route_restart_count,
        "Ratox stripe restart receipt total does not match the manifest",
    )
    require(
        observed_stripe_injected_restarts == stripe_injected_restart_count,
        "Ratox injected stripe restart receipt total does not match the manifest",
    )
    return {
        "schema": "iotox.sandwurm-pair-verification.v0",
        "status": "passed",
        "route_mode": route,
        "scenario": scenario,
        "observed_connection": connection,
        "binary_sha256": next(iter(binary_digests)),
        "proof_root": str(proof_root),
        "compact_export": compact is not None,
        "receipts": verified_receipts,
    }


def actual_tor_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="iotox-actual-tor-verifier-") as raw:
        root = Path(raw)
        node = {
            "address": "8.8.8.8",
            "port": 443,
            "public_key": "B" * 64,
        }
        target = "8.8.8.8:443"
        role_evidence = []
        for index, role in enumerate(ROLES):
            source = "10.0.0.11" if role == "client" else "10.0.0.12"
            proxy = f"10.0.0.1:{ACTUAL_TOR_SOCKS_PORTS[role]}"
            stream_id = str(11 + index)
            circuit_id = str(21 + index)
            circuit_path = "$A~a,$B~b,$C~c"
            events_path = root / f"tor-{role}-control-events.txt"
            events_path.write_text(
                "\n".join(
                    (
                        f"650 STREAM {stream_id} NEW 0 {target} "
                        f"SOURCE_ADDR={source}:{41000 + index}",
                        f"650 CIRC {circuit_id} BUILT {circuit_path} PURPOSE=GENERAL",
                        f"650 STREAM {stream_id} SUCCEEDED {circuit_id} {target}",
                    )
                )
                + "\n",
                encoding="ascii",
            )
            bootstrap_path = root / f"tor-{role}-bootstrap-status.txt"
            bootstrap_path.write_text(
                'NOTICE BOOTSTRAP PROGRESS=100 TAG=done SUMMARY="Done"\n',
                encoding="ascii",
            )
            circuit_status_path = root / f"tor-{role}-circuit-status.txt"
            circuit_status_path.write_text(
                f"{circuit_id} BUILT {circuit_path} PURPOSE=GENERAL\n",
                encoding="ascii",
            )
            configuration = [
                "AvoidDiskWrites 1",
                "ClientOnly 1",
                "ClientUseIPv6 0",
                "CookieAuthentication 1",
                "CookieAuthFile <TOR_ROOT>/control.authcookie",
                "ControlSocket <TOR_ROOT>/control.sock",
                "DataDirectory <TOR_ROOT>/tor-data",
                "SafeSocks 0",
                f"SocksPolicy accept {source}",
                "SocksPolicy reject *",
                f"SocksPort {proxy}",
            ]
            role_evidence.append(
                {
                    "role": role,
                    "control_authenticated": True,
                    "source_address": source,
                    "socks_endpoint": proxy,
                    "stream_target": target,
                    "guest_source_stream_count": 1,
                    "successful_guest_stream_count": 1,
                    "stream_id_sha256": hashlib.sha256(
                        stream_id.encode("ascii")
                    ).hexdigest(),
                    "circuit_hop_count": 3,
                    "circuit_purpose": "GENERAL",
                    "circuit_path_sha256": hashlib.sha256(
                        circuit_path.encode("ascii")
                    ).hexdigest(),
                    "bootstrap_progress": 100,
                    "public_tcp_remote_count": 2,
                    "public_tcp_remote_set_sha256": "c" * 64,
                    "configuration": configuration,
                    "configuration_sha256": hashlib.sha256(
                        ("\n".join(configuration) + "\n").encode("ascii")
                    ).hexdigest(),
                    "process_pid": 100 + index,
                    "control_socket_inode": 200 + index,
                    "events_path": events_path.name,
                    "events_sha256": digest(events_path),
                    "bootstrap_status_path": bootstrap_path.name,
                    "bootstrap_status_sha256": digest(bootstrap_path),
                    "circuit_status_path": circuit_status_path.name,
                    "circuit_status_sha256": digest(circuit_status_path),
                }
            )
        manifest = {
            "actual_tor": True,
            "actual_tor_instance_count": 2,
            "actual_tor_node": node,
            "actual_tor_binary_path": "/nix/store/example-tor/bin/tor",
            "actual_tor_sha256": "a" * 64,
            "actual_tor_version": "Tor version 0.4.8.11.",
            "actual_tor_role_evidence": role_evidence,
        }
        verify_actual_tor_evidence(root, manifest, True)
        verify_actual_tor_evidence(root, {}, False)

        client_events = root / "tor-client-control-events.txt"
        client_events.write_text(
            client_events.read_text(encoding="ascii").replace(
                target, "1.1.1.1:443", 1
            ),
            encoding="ascii",
        )
        role_evidence[0]["events_sha256"] = digest(client_events)
        try:
            verify_actual_tor_evidence(root, manifest, True)
        except ValueError as error:
            require(
                "escaped its exact target" in str(error),
                "actual-Tor negative self-test failed for the wrong reason",
            )
        else:
            raise ValueError("verifier accepted an unexpected actual-Tor target")


def actual_i2p_fail_closed_loss_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="iotox-i2p-loss-verifier-") as raw:
        root = Path(raw)
        carrier = "A1" * 32
        carrier_sha256 = hashlib.sha256(carrier.encode("ascii")).hexdigest()
        evidence = {
            "schema": "iotox-actual-i2p-fail-closed-loss-v1",
            "role": "client",
            "original_job_id": 17,
            "replacement_job_id": 18,
            "position_bytes": 65_536,
            "stopped_carrier": carrier,
            "stopped_carrier_sha256": carrier_sha256,
            "carrier_losses": 1,
            "reassignments": 0,
            "blocked_jobs": 1,
            "recoveries": 1,
            "route_worker_restarts": 0,
            "old_job_cancelled": True,
            "replacement_same_carrier": True,
            "old_client_router_pid": 101,
            "new_client_router_pid": 202,
            "router_datadir_preserved": True,
            "adapter_listener_reachable_while_sam_down": True,
            "client_sam_listener_absent_during_fault": True,
            "adapter_generation_one_lost": True,
            "adapter_generation_two_ready": True,
            "fault_hold_ns": 3_000_000,
            "loss_observation_ns": 4_000_000,
            "router_recovery_ns": 5_000_000,
            "contains_secrets": False,
        }
        evidence_path = root / "actual-i2p-fail-closed-loss.json"
        evidence_path.write_text(
            json.dumps(evidence, sort_keys=True) + "\n", encoding="utf-8"
        )
        topology_root = root / "i2p-fronts"
        topology_root.mkdir()
        topology = {
            "client_router_fault": {
                "old_client_router_pid": 101,
                "new_client_router_pid": 202,
                "fault_hold_ns": 3_000_000,
                "router_datadir_preserved": True,
                "adapter_generation_one_lost": True,
                "adapter_generation_two_ready": True,
            }
        }
        (topology_root / "topology-final.json").write_text(
            json.dumps(topology, sort_keys=True) + "\n", encoding="utf-8"
        )
        manifest = {
            "actual_i2p_payload_carrier_sha256": carrier_sha256,
            "actual_i2p_fail_closed_loss": evidence,
            "actual_i2p_fail_closed_loss_path": (
                "actual-i2p-fail-closed-loss.json"
            ),
            "actual_i2p_fail_closed_loss_sha256": digest(evidence_path),
            "actual_i2p_topology_path": "i2p-fronts/topology-final.json",
        }
        verify_actual_i2p_fail_closed_loss(root, manifest, True)
        range_evidence = dict(evidence)
        range_evidence.update({
            "schema": "iotox-actual-i2p-fail-closed-loss-v2",
            "manifest_reused_locally": True,
            "replacement_committed_objects": 2,
            "replacement_requested_objects": 1,
        })
        evidence_path.write_text(
            json.dumps(range_evidence, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        range_manifest = dict(manifest)
        range_manifest.update({
            "actual_i2p_fail_closed_loss": range_evidence,
            "actual_i2p_fail_closed_loss_sha256": digest(evidence_path),
            "scenario": "sync-file-range-actual-i2p-loss",
            "sync_range_fetched_bytes": 1_048_576,
        })
        verify_actual_i2p_fail_closed_loss(root, range_manifest, True)
        range_evidence["replacement_requested_objects"] = 2
        range_manifest["actual_i2p_fail_closed_loss"] = range_evidence
        try:
            verify_actual_i2p_fail_closed_loss(root, range_manifest, True)
        except ValueError as error:
            require(
                "fail-closed loss summary" in str(error),
                "I2P manifest-reuse self-test failed for the wrong reason",
            )
        else:
            raise ValueError(
                "verifier accepted a replacement manifest network request"
            )
        range_evidence["replacement_requested_objects"] = 1
        range_manifest["sync_range_fetched_bytes"] = evidence["position_bytes"]
        try:
            verify_actual_i2p_fail_closed_loss(root, range_manifest, True)
        except ValueError as error:
            require(
                "fail-closed loss summary" in str(error),
                "I2P-range-loss bound self-test failed for the wrong reason",
            )
        else:
            raise ValueError("verifier accepted a completed I2P range as live loss")
        forged = dict(evidence)
        forged["reassignments"] = 1
        manifest["actual_i2p_fail_closed_loss"] = forged
        try:
            verify_actual_i2p_fail_closed_loss(root, manifest, True)
        except ValueError as error:
            require(
                "fail-closed loss summary" in str(error),
                "I2P-loss negative self-test failed for the wrong reason",
            )
        else:
            raise ValueError("verifier accepted native reassignment after I2P loss")


def self_test() -> None:
    require(
        "sync-bidirectional" in BIDIRECTIONAL_SYNC_SCENARIOS,
        "bidirectional synchronization scenario is not registered",
    )
    require(
        "sync-automation" in AUTOMATION_SYNC_SCENARIOS,
        "unattended synchronization scenario is not registered",
    )
    boundary_round_trips = [250_000] * CAP_2_SLA_MIN_OVERLAP
    boundary_queue_waits = [10_000] * CAP_2_SLA_MIN_OVERLAP
    require(
        cap_2_interactive_sla_passes(
            boundary_round_trips, boundary_queue_waits
        )
        and not cap_2_interactive_sla_passes(
            boundary_round_trips[:-1], boundary_queue_waits[:-1]
        )
        and not cap_2_interactive_sla_passes(
            [0] * 19 + [250_001] * 21, [0] * 40
        )
        and not cap_2_interactive_sla_passes(
            [0] * 37 + [500_001] * 3, [0] * 40
        )
        and not cap_2_interactive_sla_passes(
            [0] * 39 + [1_000_001], [0] * 40
        )
        and not cap_2_interactive_sla_passes(
            [0] * 100 + [1_500_001], [0] * 101
        )
        and not cap_2_interactive_sla_passes(
            [0] * 40, [0] * 37 + [10_001] * 3
        ),
        "cap-2 interactive SLA boundary self-test failed",
    )
    require(
        "sync-content-route-private-actual-tor" in CONTENT_SCENARIOS
        and "sync-content-route-private-actual-tor" in MULTI_ROUTE_SYNC_SCENARIOS
        and "sync-content-route-private-actual-tor" in SYNC_SCENARIOS,
        "actual-Tor content scenario classifiers disagree",
    )
    require(
        "sync-content-same-source-multi-route-actual-tor"
        in CONTENT_SCENARIOS
        and "sync-content-same-source-multi-route-actual-tor"
        in MULTI_ROUTE_SYNC_SCENARIOS
        and "sync-content-same-source-multi-route-actual-tor"
        in SYNC_SCENARIOS
        and "sync-content-same-source-multi-route-actual-tor"
        not in CONTENT_MULTI_SOURCE_SCENARIOS,
        "actual-Tor same-source path scenario classifiers disagree",
    )
    require(
        "sync-content-multi-route-actual-tor"
        in CONTENT_MULTI_SOURCE_SCENARIOS
        and "sync-content-multi-route-actual-tor"
        in MULTI_ROUTE_SYNC_SCENARIOS
        and "sync-content-multi-route-actual-tor" in SYNC_SCENARIOS,
        "actual-Tor multi-source scenario classifiers disagree",
    )
    require(
        "sync-content-multi-route-actual-tor-loss"
        in CONTENT_MULTI_SOURCE_SCENARIOS
        and "sync-content-multi-route-actual-tor-loss"
        in MULTI_ROUTE_SYNC_SCENARIOS
        and "sync-content-multi-route-actual-tor-loss" in SYNC_SCENARIOS,
        "actual-Tor multi-source loss classifiers disagree",
    )
    legacy_multi_source_fields = content_completion_fields(
        "sync-content-multi-source",
        False,
    )
    atomic_multi_source_fields = content_completion_fields(
        "sync-content-multi-source",
        True,
    )
    loss_fields = content_completion_fields(
        "sync-content-multi-source-loss",
        True,
    )
    route_loss_fields = content_completion_fields(
        "sync-content-multi-route-actual-tor-loss",
        True,
    )
    require(
        "content-atomic-pull" not in legacy_multi_source_fields
        and atomic_multi_source_fields
        == legacy_multi_source_fields[:12]
        + ["content-atomic-pull"]
        + legacy_multi_source_fields[12:]
        and loss_fields[: len(atomic_multi_source_fields)]
        == atomic_multi_source_fields
        and loss_fields[-1] == "content-loss-activation-fenced",
        "content completion format generations are ambiguous",
    )
    require(
        route_loss_fields[: len(loss_fields)] == loss_fields
        and route_loss_fields[-1] == "content-route-loss-secondary-epoch",
        "routed content-loss completion fields are ambiguous",
    )
    require(
        REPEATED_RANGE_LOSS_COUNTS
        == {
            "sync-file-range-repeated-route-loss": 2,
            "sync-file-range-triple-route-loss": 3,
        },
        "bounded repeated range-loss scenario counts changed",
    )
    require(
        actual_i2p_router_restart_expected("i2p-router-restart")
        and actual_i2p_router_restart_expected(
            "sync-tree-route-private-actual-i2p-loss"
        )
        and actual_i2p_router_restart_expected(
            "sync-file-range-actual-i2p-loss"
        )
        and not actual_i2p_router_restart_expected(
            "sync-file-range-actual-i2p"
        ),
        "actual-I2P router restart scenarios are incomplete",
    )
    actual_i2p_fail_closed_loss_self_test()
    actual_tor_self_test()
    version, revision = product_identity()
    route_resume = {
        "sync_tree_route_resume_observed": True,
        "sync_tree_route_loss_position_bytes": 131_072,
        "sync_tree_route_loss_retained_partials": 0,
        "sync_tree_route_loss_retained_attempts": 2,
        "sync_tree_route_loss_retained_bytes": 196_608,
        "sync_tree_route_loss_retention_fallbacks": 0,
        "sync_tree_route_loss_resumed_attempts": 2,
        "sync_tree_route_loss_resumed_bytes": 196_608,
    }
    verify_route_resume(route_resume, True, "self-test", 2)
    route_resume["sync_tree_route_loss_resumed_bytes"] -= 1
    try:
        verify_route_resume(route_resume, True, "self-test", 2)
    except ValueError as error:
        require(
            "route-prefix resume evidence is invalid" in str(error),
            "route-resume self-test failed for the wrong reason",
        )
    else:
        raise ValueError("verifier accepted mismatched resumed bytes")
    loss_before_cancel = {
        "sync_tree_route_loss_observed": True,
        "sync_tree_route_cancel_observed": True,
        "sync_tree_route_loss_position_bytes": 116_535,
        "sync_tree_route_loss_carrier_losses": 1,
        "sync_tree_route_loss_reassignments": 1,
        "sync_tree_route_loss_stale_terminals": 2,
        "sync_tree_route_loss_recoveries": 1,
        "sync_tree_route_cancel_adaptive_selections": 2,
        "sync_tree_route_cancel_reassignments_delta": 0,
        "sync_tree_route_cancel_carrier": "A" * 64,
        "sync_tree_route_loss_final_carrier": "A" * 64,
        "sync_tree_route_loss_stopped_carrier": "B" * 64,
    }
    verify_loss_before_cancel_order(loss_before_cancel, "self-test")
    loss_before_cancel["sync_tree_route_loss_final_carrier"] = "B" * 64
    try:
        verify_loss_before_cancel_order(loss_before_cancel, "self-test")
    except ValueError as error:
        require(
            "loss-before-cancel order is invalid" in str(error),
            "loss-before-cancel self-test failed for the wrong reason",
        )
    else:
        raise ValueError("verifier accepted a cancelled old carrier")
    cancel_before_loss = {
        "sync_tree_route_cancel_loss_observed": True,
        "sync_tree_route_loss_observed": True,
        "sync_tree_route_cancel_observed": True,
        "sync_tree_route_loss_position_bytes": 0,
        "sync_tree_route_loss_carrier_losses": 1,
        "sync_tree_route_loss_reassignments": 0,
        "sync_tree_route_loss_stale_terminals": 1,
        "sync_tree_route_loss_recoveries": 1,
        "sync_tree_route_cancel_adaptive_selections": 1,
        "sync_tree_route_cancel_reassignments_delta": 0,
        "sync_tree_route_cancel_carrier": "C" * 64,
        "sync_tree_route_loss_final_carrier": "C" * 64,
        "sync_tree_route_loss_stopped_carrier": "C" * 64,
    }
    verify_cancel_before_loss_order(cancel_before_loss, "self-test")
    cancel_before_loss["sync_tree_route_loss_reassignments"] = 1
    try:
        verify_cancel_before_loss_order(cancel_before_loss, "self-test")
    except ValueError as error:
        require(
            "cancel-before-loss order is invalid" in str(error),
            "cancel-before-loss self-test failed for the wrong reason",
        )
    else:
        raise ValueError("verifier accepted post-cancellation reassignment")
    cancel_loss_race = {
        "sync_tree_route_cancel_race_observed": True,
        "sync_tree_route_loss_observed": True,
        "sync_tree_route_cancel_observed": True,
        "sync_tree_route_loss_position_bytes": 98_304,
        "sync_tree_route_loss_carrier_losses": 1,
        "sync_tree_route_loss_reassignments": 0,
        "sync_tree_route_loss_stale_terminals": 0,
        "sync_tree_route_loss_recoveries": 1,
        "sync_tree_route_cancel_reassignments_delta": 0,
        "sync_tree_route_cancel_adaptive_selections": 1,
        "sync_tree_route_cancel_race_fault_delay_ms": 500,
        "sync_tree_route_cancel_race_cancel_delay_ms": 500,
        "sync_tree_route_cancel_race_cleanup_retries": 1,
        "sync_tree_route_cancel_race_outcome": "cancel-first",
        "sync_tree_route_cancel_carrier": "D" * 64,
        "sync_tree_route_loss_final_carrier": "D" * 64,
        "sync_tree_route_loss_stopped_carrier": "D" * 64,
    }
    verify_cancel_loss_race_order(cancel_loss_race, "self-test")
    loss_first_race = dict(cancel_loss_race)
    loss_first_race.update(
        {
            "sync_tree_route_loss_reassignments": 1,
            "sync_tree_route_cancel_reassignments_delta": 1,
            "sync_tree_route_cancel_adaptive_selections": 2,
            "sync_tree_route_cancel_race_fault_delay_ms": 250,
            "sync_tree_route_cancel_race_cancel_delay_ms": 1000,
            "sync_tree_route_cancel_race_cleanup_retries": 0,
            "sync_tree_route_cancel_race_outcome": "loss-first",
            "sync_tree_route_loss_final_carrier": "E" * 64,
        }
    )
    verify_cancel_loss_race_order(
        loss_first_race, "self-test", 250, 1000, "loss-first"
    )
    cancel_loss_race["sync_tree_route_loss_reassignments"] = 1
    try:
        verify_cancel_loss_race_order(cancel_loss_race, "self-test")
    except ValueError as error:
        require(
            "cancel/loss race order is invalid" in str(error),
            "cancel/loss race self-test failed for the wrong reason",
        )
    else:
        raise ValueError("verifier accepted an inconsistent race outcome")
    concurrent_cancel = {
        "sync_tree_route_concurrent_cancel_observed": True,
        "sync_tree_route_concurrent_cancel_jobs": 8,
        "sync_tree_route_concurrent_cancel_artifact_bytes": 262_211,
        "sync_tree_route_concurrent_cancel_requested": 4,
        "sync_tree_route_concurrent_cancel_completed": 4,
        "sync_tree_route_concurrent_cancel_survivors": 4,
        "sync_tree_route_concurrent_cancel_survivor_activations": 4,
        "sync_tree_route_concurrent_cancel_pattern": "01010101",
        "sync_tree_route_concurrent_cancel_route_zero": 2,
        "sync_tree_route_concurrent_cancel_route_one": 2,
        "sync_tree_route_concurrent_cancel_tail_ms": 150,
        "sync_tree_route_concurrent_cancel_work_before": 16,
        "sync_tree_route_concurrent_cancel_work_after": 0,
        "sync_tree_route_concurrent_cancel_reassignments_delta": 0,
        "sync_tree_route_concurrent_cancel_adaptive_selections": 8,
        "sync_tree_route_concurrent_cancel_resource_sha256": "a" * 64,
    }
    verify_route_concurrent_cancel_summary(
        concurrent_cancel, True, "self-test"
    )
    larger_concurrent_cancel = dict(concurrent_cancel)
    larger_concurrent_cancel[
        "sync_tree_route_concurrent_cancel_artifact_bytes"
    ] = 1_048_643
    verify_route_concurrent_cancel_summary(
        larger_concurrent_cancel,
        True,
        "self-test larger common-link cell",
        1_048_643,
    )
    verify_route_concurrent_cancel_summary({}, False, "self-test")
    fair_qdisc = {
        "schema": "iotox-common-link-fairness-v1",
        "tap": "vm-iotoxc",
        "root_kind": "htb",
        "root_handle": "1:",
        "class_kind": "htb",
        "class_handle": "1:1",
        "rate_bytes_per_second": 500_000,
        "ceil_bytes_per_second": 500_000,
        "leaf_kind": "fq_codel",
        "leaf_handle": "10:",
        "leaf_parent": "1:1",
        "leaf_limit_packets": 1000,
        "active_leaf_flow_count": 4,
        "fq_codel_bytes": 4096,
        "fq_codel_packets": 8,
        "fq_codel_drops": 1,
        "fq_codel_overlimits": 0,
        "fq_codel_requeues": 0,
        "htb_bytes": 4096,
        "htb_packets": 8,
        "htb_drops": 0,
        "htb_overlimits": 2,
        "htb_requeues": 0,
    }
    verify_common_link_fairness_qdisc(fair_qdisc, True, "self-test")
    verify_common_link_fairness_qdisc({}, False, "self-test absent")
    concurrent_cancel["sync_tree_route_concurrent_cancel_survivors"] = 3
    try:
        verify_route_concurrent_cancel_summary(
            concurrent_cancel, True, "self-test"
        )
    except ValueError as error:
        require(
            "concurrent route-cancellation evidence is invalid" in str(error),
            "concurrent cancellation self-test failed for the wrong reason",
        )
    else:
        raise ValueError(
            "verifier accepted incomplete concurrent cancellation survival"
        )
    population_loss = {
        "sync_tree_route_population_loss_observed": True,
        "sync_tree_route_population_loss_jobs": 8,
        "sync_tree_route_population_loss_artifact_bytes": 524_355,
        "sync_tree_route_population_loss_pattern": "00001111",
        "sync_tree_route_population_loss_affected_jobs": 4,
        "sync_tree_route_population_loss_carrier_losses": 1,
        "sync_tree_route_population_loss_reassignments": 4,
        "sync_tree_route_population_loss_stale_terminals": 4,
        "sync_tree_route_population_loss_recoveries": 1,
        "sync_tree_route_population_loss_fixed_selections": 12,
        "sync_tree_route_population_loss_activations": 8,
        "sync_tree_route_population_loss_work_before": 16,
        "sync_tree_route_population_loss_work_after": 0,
        "sync_tree_route_population_loss_fault_delay_ms": 750,
        "sync_tree_route_population_loss_fault_position_bytes": 131_072,
        "sync_tree_route_population_loss_duration_ms": 2_000,
        "sync_tree_route_population_loss_stopped_carrier": "A" * 64,
        "sync_tree_route_population_loss_resource_sha256": "b" * 64,
    }
    verify_route_population_loss_summary(population_loss, True, "self-test")
    verify_route_population_loss_summary({}, False, "self-test")
    loss_admission = dict(population_loss)
    loss_admission.update(
        {
            "sync_tree_route_population_loss_jobs": 4,
            "sync_tree_route_population_loss_pattern": "00",
            "sync_tree_route_population_loss_affected_jobs": 2,
            "sync_tree_route_population_loss_reassignments": 2,
            "sync_tree_route_population_loss_fixed_selections": 6,
            "sync_tree_route_population_loss_activations": 4,
            "sync_tree_route_population_loss_work_before": 4,
            "sync_tree_route_population_loss_fault_delay_ms": 1,
            "sync_tree_route_loss_admission_started_jobs": 2,
            "sync_tree_route_loss_admission_ready_bulk": 1,
            "sync_tree_route_loss_admission_surviving_carrier": "C" * 64,
        }
    )
    verify_route_population_loss_summary(
        loss_admission, True, "self-test", admission=True
    )
    loss_admission[
        "sync_tree_route_loss_admission_surviving_carrier"
    ] = "A" * 64
    try:
        verify_route_population_loss_summary(
            loss_admission, True, "self-test", admission=True
        )
    except ValueError as error:
        require(
            "route-population loss evidence is invalid" in str(error),
            "loss-admission self-test failed for the wrong reason",
        )
    else:
        raise ValueError(
            "verifier accepted admission on the stopped route"
        )
    startup_admission = {
        "sync_tree_route_startup_admission_observed": True,
        "sync_tree_route_startup_admission_jobs": 2,
        "sync_tree_route_startup_admission_artifact_bytes": 16_777_283,
        "sync_tree_route_startup_admission_delay_ms": 20_000,
        "sync_tree_route_startup_admission_restart_count": 1,
        "sync_tree_route_startup_admission_ready_bulk_before": 1,
        "sync_tree_route_startup_admission_ready_bulk_after": 2,
        "sync_tree_route_startup_admission_stable_samples": 10,
        "sync_tree_route_startup_admission_carrier": "D" * 64,
        "sync_tree_route_startup_admission_live_jobs_after_join": 2,
        "sync_tree_route_startup_admission_preserved_carriers": 2,
        "sync_tree_route_startup_admission_adaptive_selections": 2,
        "sync_tree_route_startup_admission_activations": 2,
        "sync_tree_route_startup_admission_work_before": 4,
        "sync_tree_route_startup_admission_work_after": 0,
        "sync_tree_route_startup_admission_duration_ms": 45_000,
        "sync_tree_route_startup_admission_resource_sha256": "e" * 64,
    }
    verify_route_startup_admission_summary(
        startup_admission, True, "self-test"
    )
    verify_route_startup_admission_summary({}, False, "self-test")
    startup_admission[
        "sync_tree_route_startup_admission_preserved_carriers"
    ] = 1
    try:
        verify_route_startup_admission_summary(
            startup_admission, True, "self-test"
        )
    except ValueError as error:
        require(
            "route-startup admission evidence is invalid" in str(error),
            "startup-admission self-test failed for the wrong reason",
        )
    else:
        raise ValueError(
            "verifier accepted migration during delayed-route admission"
        )
    throughput_policy_bytes = 4 * 16_777_283
    route_throughput = {
        "sync_tree_route_throughput_observed": True,
        "sync_tree_route_throughput_jobs_per_phase": 2,
        "sync_tree_route_throughput_phases": 4,
        "sync_tree_route_throughput_artifact_bytes": 16_777_283,
        "sync_tree_route_throughput_phase_order": (
            "fixed-a,adaptive-a,adaptive-b,fixed-b"
        ),
        "sync_tree_route_throughput_restart_count": 4,
        "sync_tree_route_throughput_restart_hold_ms": 5000,
        "sync_tree_route_throughput_fixed_patterns": "00,00",
        "sync_tree_route_throughput_adaptive_patterns": "01,01",
        "sync_tree_route_throughput_fixed_a_duration_ms": 100_000,
        "sync_tree_route_throughput_adaptive_a_duration_ms": 90_000,
        "sync_tree_route_throughput_adaptive_b_duration_ms": 91_000,
        "sync_tree_route_throughput_fixed_b_duration_ms": 101_000,
        "sync_tree_route_throughput_fixed_a_completion_skew_ms": 1_000,
        "sync_tree_route_throughput_adaptive_a_completion_skew_ms": 500,
        "sync_tree_route_throughput_adaptive_b_completion_skew_ms": 600,
        "sync_tree_route_throughput_fixed_b_completion_skew_ms": 1_100,
        "sync_tree_route_throughput_fixed_total_duration_ms": 201_000,
        "sync_tree_route_throughput_adaptive_total_duration_ms": 181_000,
        "sync_tree_route_throughput_fixed_artifact_bps": (
            throughput_policy_bytes * 1000 // 201_000
        ),
        "sync_tree_route_throughput_adaptive_artifact_bps": (
            throughput_policy_bytes * 1000 // 181_000
        ),
        "sync_tree_route_throughput_adaptive_speedup_ppm": (
            201_000 * 1_000_000 // 181_000
        ),
        "sync_tree_route_throughput_fixed_selections": 4,
        "sync_tree_route_throughput_adaptive_selections": 4,
        "sync_tree_route_throughput_reassignments": 0,
        "sync_tree_route_throughput_activations": 8,
        "sync_tree_route_throughput_peak_work": 4,
        "sync_tree_route_throughput_work_after": 0,
        "sync_tree_route_throughput_fixed_a_resource_sha256": "1" * 64,
        "sync_tree_route_throughput_adaptive_a_resource_sha256": "2" * 64,
        "sync_tree_route_throughput_adaptive_b_resource_sha256": "3" * 64,
        "sync_tree_route_throughput_fixed_b_resource_sha256": "4" * 64,
    }
    verify_route_throughput_summary(route_throughput, True, "self-test")
    verify_route_throughput_summary({}, False, "self-test")
    route_throughput[
        "sync_tree_route_throughput_adaptive_patterns"
    ] = "00,01"
    try:
        verify_route_throughput_summary(
            route_throughput, True, "self-test"
        )
    except ValueError as error:
        require(
            "route-throughput evidence is invalid" in str(error),
            "route-throughput self-test failed for the wrong reason",
        )
    else:
        raise ValueError(
            "verifier accepted a non-striped adaptive throughput phase"
        )
    population_loss["sync_tree_route_population_loss_reassignments"] = 3
    try:
        verify_route_population_loss_summary(
            population_loss, True, "self-test"
        )
    except ValueError as error:
        require(
            "route-population loss evidence is invalid" in str(error),
            "population-loss self-test failed for the wrong reason",
        )
    else:
        raise ValueError(
            "verifier accepted incomplete population-loss reassignment"
        )
    bulk_state = {
        "state-accounting": "active-or-paused",
        "present-before": "8",
        "active-before": "3",
        "paused-before": "5",
        "present-after": "8",
        "active-after": "1",
        "paused-after": "7",
    }
    verify_ratox_bulk_state_accounting(bulk_state, 8, 8)
    bulk_state["paused-after"] = "6"
    try:
        verify_ratox_bulk_state_accounting(bulk_state, 8, 8)
    except ValueError as error:
        require(
            "Ratox bulk state accounting is invalid" in str(error),
            "Ratox bulk state self-test failed for the wrong reason",
        )
    else:
        raise ValueError("verifier accepted incomplete Ratox bulk state")
    legacy_status = "\n".join(
        (
            "last-event=file-control",
            "transport-pending-events=0",
            "transport-maximum-pending-events=1024",
            "transport-required-event-backpressure-count=0",
            "transport-required-event-backpressure-total-us=0",
            "transport-required-event-backpressure-maximum-us=0",
        )
    ) + "\n"
    verify_ratox_agent_status(legacy_status, "self-test")
    paced_status = legacy_status + "\n".join(
        (
            "transport-file-pacing-paused-transfers=0",
            "transport-file-pacing-high-watermark=64",
            "transport-file-pacing-low-watermark=16",
            "transport-file-pacing-minimum-hold-us=5000",
            "transport-file-pacing-pause-count=3",
            "transport-file-pacing-resume-count=3",
            "transport-file-pacing-pause-failure-count=0",
            "transport-file-pacing-resume-failure-count=0",
            "transport-file-pacing-total-hold-us=18000",
            "transport-file-pacing-maximum-hold-us=7000",
        )
    ) + "\n"
    verify_ratox_agent_status(paced_status, "self-test")
    batched_status = paced_status + "\n".join(
        (
            "transport-file-pacing-resume-batch-limit=1",
            "transport-file-pacing-resume-batch-count=3",
            "transport-file-pacing-resume-batch-maximum=1",
        )
    ) + "\n"
    verify_ratox_agent_status(batched_status, "self-test")
    coordinated_status = (
        batched_status + "transport-file-pacing-external-pause-count=2\n"
    )
    verify_ratox_agent_status(coordinated_status, "self-test")
    try:
        verify_ratox_agent_status(
            coordinated_status.replace(
                "transport-file-pacing-pause-failure-count=0",
                "transport-file-pacing-pause-failure-count=1",
            ),
            "self-test",
        )
        raise ValueError("coordinated file-pacing failure passed")
    except ValueError as error:
        require(
            "coordinated file pacing recorded a control failure" in str(error),
            "coordinated file-pacing negative self-test failed for the wrong reason",
        )
    try:
        verify_ratox_agent_status(
            coordinated_status.replace(
                "last-event=file-control",
                "last-event=file-transfer-failed: late chunk",
            ),
            "self-test",
        )
        raise ValueError("coordinated terminal file failure passed")
    except ValueError as error:
        require(
            "ended on a file-transfer failure" in str(error),
            "coordinated terminal-failure self-test failed for the wrong reason",
        )
    carrier_status = coordinated_status + "\n".join(
        (
            "file-carrier-window-per-peer=1",
            "file-carrier-rotation-quantum-ms=20",
            "file-carrier-runnable-receives=0",
            "file-carrier-waiting-receives=0",
            "file-carrier-admission-count=8",
            "file-carrier-rotation-count=7",
            "file-carrier-pause-count=7",
            "file-carrier-resume-count=8",
            "file-carrier-control-failure-count=0",
            "file-carrier-total-wait-us=560000",
            "file-carrier-maximum-wait-us=140000",
        )
    ) + "\n"
    verify_ratox_agent_status(carrier_status, "self-test")
    try:
        verify_ratox_agent_status(
            carrier_status.replace(
                "file-carrier-maximum-wait-us=140000\n", ""
            ),
            "self-test",
        )
        raise ValueError("partial file-carrier status passed")
    except ValueError as error:
        require(
            "file-carrier evidence is incomplete" in str(error),
            "file-carrier negative self-test failed for the wrong reason",
        )
    try:
        verify_ratox_agent_status(
            batched_status.replace(
                "transport-file-pacing-resume-batch-maximum=1\n", ""
            ),
            "self-test",
        )
        raise ValueError("partial file-pacing batch status passed")
    except ValueError as error:
        require(
            "file-pacing batch evidence is incomplete" in str(error),
            "file-pacing batch negative self-test failed for the wrong reason",
        )
    try:
        verify_ratox_agent_status(
            paced_status.replace(
                "transport-file-pacing-maximum-hold-us=7000\n", ""
            ),
            "self-test",
        )
        raise ValueError("partial file-pacing status passed")
    except ValueError as error:
        require(
            "file-pacing evidence is incomplete" in str(error),
            "file-pacing negative self-test failed for the wrong reason",
        )
    with tempfile.TemporaryDirectory(prefix="iotox-packet-loss-report-") as directory:
        report = Path(directory) / "packet-loss-burst.tsv"
        rows = []
        for ordinal in range(1, PACKET_LOSS_PROBE_COUNT + 1):
            missed = ordinal % 16 == 0
            rows.append(
                "\t".join(
                    (
                        "burst-probe",
                        "ordinal",
                        str(ordinal),
                        "nonce",
                        str(10_000 + ordinal),
                        "rtt-us",
                        "miss" if missed else str(1_000 + ordinal),
                        "arrival-rank",
                        "miss" if missed else str(ordinal),
                        "copies",
                        "0" if missed else "1",
                        "send-error",
                        "ok",
                    )
                )
            )
        report.write_text("\n".join(rows) + "\n", encoding="utf-8")
        verify_packet_loss_report(report, 120, 8)
        report.write_text(
            report.read_text(encoding="utf-8").replace(
                "\tordinal\t1\t", "\tordinal\t2\t", 1
            ),
            encoding="utf-8",
        )
        try:
            verify_packet_loss_report(report, 120, 8)
        except ValueError as error:
            require(
                "duplicate partial-loss ordinal" in str(error),
                "partial-loss negative self-test failed for the wrong reason",
            )
        else:
            raise ValueError("partial-loss verifier accepted a duplicate ordinal")
    legacy_receipt = {
        "binary_sha256": next(iter(LEGACY_REPAIR_BINARY_SHA256))
    }
    require(
        is_legacy_repair_evidence(
            {"receipts": {"client": legacy_receipt, "device": legacy_receipt}}
        ),
        "legacy repair evidence classification changed",
    )
    require(
        not is_legacy_repair_evidence(
            {
                "receipts": {
                    "client": {"binary_sha256": "a" * 64},
                    "device": {"binary_sha256": "a" * 64},
                }
            }
        ),
        "current repair evidence was classified as legacy",
    )
    with tempfile.TemporaryDirectory(
        prefix="iotox-resource-verifier-"
    ) as directory:
        resource_path = Path(directory) / "resource.tsv"
        resource: dict[str, str] = {
            "schema": "iotox-process-resource-interval-v1",
            "role": "client",
            "pid": "1",
            "process-start-ticks": "10",
            "clock-ticks-per-second": "100",
            "page-size-bytes": "4096",
        }
        for phase in ("start", "end"):
            for key in RESOURCE_SAMPLE_KEYS:
                resource[f"{phase}-{key}"] = "1"
            resource[f"{phase}-process-start-ticks"] = "10"
            resource[f"{phase}-ratox-latency-mode-active"] = "0"
            resource[f"{phase}-ratox-active-service-interval-ms"] = "5"
            resource[
                f"{phase}-ratox-active-transport-iteration-interval-ms"
            ] = "5"
        for key in RESOURCE_DELTA_KEYS:
            resource[f"start-{key}"] = "1"
            resource[f"end-{key}"] = "2"
            resource[f"delta-{key}"] = "1"
        resource_path.write_text(
            "".join(
                f"{key}\t{resource[key]}\n" for key in sorted(resource)
            ),
            encoding="ascii",
        )
        verify_resource_interval(resource_path, "client")
        resource["start-ratox-latency-mode-active"] = "0"
        resource["end-ratox-latency-mode-active"] = "1"
        resource_path.write_text(
            "".join(
                f"{key}\t{resource[key]}\n" for key in sorted(resource)
            ),
            encoding="ascii",
        )
        verify_resource_interval(
            resource_path,
            "client",
            ratox_active_boundary=(0, 1),
        )
        try:
            verify_resource_interval(resource_path, "client")
        except ValueError as error:
            require(
                "active/idle cadence boundary" in str(error),
                "resource-boundary self-test failed for the wrong reason",
            )
        else:
            raise ValueError("verifier accepted the wrong Ratox boundary")
        resource["end-ratox-latency-mode-active"] = "0"
        resource["delta-user-cpu-ticks"] = "2"
        resource_path.write_text(
            "".join(
                f"{key}\t{resource[key]}\n" for key in sorted(resource)
            ),
            encoding="ascii",
        )
        try:
            verify_resource_interval(resource_path, "client")
        except ValueError as error:
            require(
                "delta is inconsistent" in str(error),
                "resource-delta self-test failed for the wrong reason",
            )
        else:
            raise ValueError("verifier accepted an inconsistent resource delta")
    with tempfile.TemporaryDirectory(prefix="iotox-pair-verifier-") as directory:
        root = Path(directory)
        role_entries = {}
        chain_entries = {}
        for role, (local_ip, peer_ip, tap) in {
            "client": ("10.0.0.11", "10.0.0.12", "vm-iotoxc"),
            "device": ("10.0.0.12", "10.0.0.11", "vm-iotoxd"),
        }.items():
            receipt = {
                "schema": "iotox.sandwurm-pair.v0", "status": "passed", "role": role,
                "route_mode": "direct-udp", "scenario": "baseline",
                "expected_connection": "udp", "observed_connection": "udp",
                "local_ipv4": local_ip, "peer_ipv4": peer_ip, "private_l2_ping": True,
                "tox_friendship": True, "session_confirmed": True, "bidirectional_text": True,
                "reusable_identity_copy": True, "controlled_host_bridge_bootstrap": True,
                "peer_key_sha256": "b" * 64, "bootstrap_key_sha256": "c" * 64,
                "source_revision": "0" * 40, "product_revision": revision,
                "version": f"IoTox {version} {revision}", "binary_sha256": "a" * 64,
                "package_variant": "pinned-source-linked", "c_toxcore_version": "0.2.23",
                "libsodium_version": "1.0.22", "argon2_version": "20190702",
                "virtualization": "kvm", "cgroup_type": "cgroup2fs",
                "network_class": "provider-egress", "contains_secrets": False,
                "initial_online_epoch": 1, "recovered_online_epoch": 1,
                "relay_interruption_observed": False,
                "relay_recovery_observed": False,
                "link_interruption_observed": False,
                "link_recovery_observed": False,
                "daemon_replacement_observed": False,
                "daemon_offline_observed": False,
                "daemon_identity_preserved": False,
                "fresh_session_after_daemon_restart": False,
                "daemon_restart_count": 0,
                "guest_restart_observed": False,
                "guest_offline_observed": False,
                "guest_identity_preserved": False,
                "fresh_session_after_guest_restart": False,
            }
            receipt_path = root / role / "live/workspace-export/guest-receipts/iotox/pair.json"
            receipt_path.parent.mkdir(parents=True)
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            role_entries[role] = {"path": str(receipt_path.relative_to(root)), "sha256": digest(receipt_path), "binary_sha256": "a" * 64, "peer_key_sha256": "b" * 64}
            chain = {"schema": "sandwurm.direct-cloud-hypervisor-live-chain.v0", "status": "guest-evidence-observed", "failure": None, "receipts": {"prelaunch_chain": {"status": "ready"}, "live_launch": {"status": "exited"}}, "guest_evidence": {"observed": True, "legacy_guest_receipts_complete": True}}
            chain_path = root / role / "direct-cloud-hypervisor-live-chain.json"
            chain_path.write_text(json.dumps(chain), encoding="utf-8")
            chain_entries[role] = {"path": str(chain_path.relative_to(root)), "sha256": digest(chain_path), "status": "guest-evidence-observed"}
            planned_path = root / role / "prelaunch/launch/cloud-hypervisor-launch.json"
            planned_path.parent.mkdir(parents=True)
            planned_path.write_text(json.dumps({"status": "planned", "network": {"class": "provider-egress", "mode": "prepared-host-tap-nat", "tap_interface": tap, "prepared_host_contract": {"bridge_interface": "sandwurm-vm"}}, "vmm": {"argv": ["cloud-hypervisor", "--net", f"tap={tap}"]}}), encoding="utf-8")
        manifest = {"schema": "iotox.sandwurm-pair-manifest.v0", "status": "passed", "route_mode": "direct-udp", "scenario": "baseline", "expected_connection": "udp", "simultaneous_vmm_chains_observed": True, "prepared_bridge": "sandwurm-vm", "bootstrap_fixture": "pinned-host-bridge-c-toxcore-0.2.23", "bootstrap_fixture_restart_count": 0, "bootstrap_fixture_key_preserved": True, "device_daemon_restart_count": 0, "link_interruption_count": 0, "device_guest_restart_count": 0, "identity_mode": "reused-immutable-private-baseline", "identity_baseline_unchanged": True, "proof_root_contains_private_guest_disks": True, "receipts_contain_secrets": False, "taps": [{"name": "vm-iotoxc", "master": "sandwurm-vm"}, {"name": "vm-iotoxd", "master": "sandwurm-vm"}], "receipts": role_entries, "chains": chain_entries}
        manifest_path = root / "pair-manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        verify_pair(root, "direct-udp")

        source_manifest_digest = digest(manifest_path)
        manifest["proof_root_contains_private_guest_disks"] = False
        manifest["compact_export"] = {
            "schema": COMPACT_SCHEMA,
            "source_proof_id": "pair.selftest",
            "source_manifest_sha256": source_manifest_digest,
            "source_proof_root_contained_private_guest_disks": True,
        }
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        compact_files = {
            str(path.relative_to(root)): digest(path)
            for path in root.rglob("*.json")
            if path != root / "compact-export.json"
        }
        (root / "compact-export.json").write_text(
            json.dumps({
                "schema": COMPACT_SCHEMA,
                "status": "passed",
                "contains_secrets": False,
                "source_proof_id": "pair.selftest",
                "source_manifest_sha256": source_manifest_digest,
                "source_private_artifacts_omitted": [
                    "bootstrap-secret-key",
                    "guest-disks",
                    "injected-identities",
                    "runtime-state",
                ],
                "files": compact_files,
            }),
            encoding="utf-8",
        )
        verify_pair(root, "direct-udp")
        compact_path = root / "compact-export.json"
        compact_record = load(compact_path)
        compact_record["files"]["pair-manifest.json"] = "f" * 64
        compact_path.write_text(json.dumps(compact_record), encoding="utf-8")
        try:
            verify_pair(root)
        except ValueError as error:
            require(
                "compact export digest mismatch" in str(error),
                "compact-digest self-test failed for the wrong reason",
            )
        else:
            raise ValueError("verifier accepted a forged compact export digest")
        manifest.pop("compact_export")
        manifest["proof_root_contains_private_guest_disks"] = True
        compact_path.unlink()

        manifest.update({
            "route_mode": "forced-tcp",
            "scenario": "relay-restart",
            "expected_connection": "tcp",
            "bootstrap_fixture_restart_count": 1,
        })
        for role in ROLES:
            receipt_path = root / manifest["receipts"][role]["path"]
            receipt = load(receipt_path)
            receipt.update({
                "route_mode": "forced-tcp",
                "scenario": "relay-restart",
                "expected_connection": "tcp",
                "observed_connection": "tcp",
                "initial_online_epoch": 1,
                "recovered_online_epoch": 2,
                "relay_interruption_observed": True,
                "relay_recovery_observed": True,
            })
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            manifest["receipts"][role]["sha256"] = digest(receipt_path)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        verify_pair(root, "forced-tcp", "relay-restart")

        manifest.update({
            "scenario": "link-interruption",
            "bootstrap_fixture_restart_count": 0,
            "link_interruption_count": 1,
        })
        for role in ROLES:
            receipt_path = root / manifest["receipts"][role]["path"]
            receipt = load(receipt_path)
            receipt.update({
                "scenario": "link-interruption",
                "relay_interruption_observed": False,
                "relay_recovery_observed": False,
                "link_interruption_observed": True,
                "link_recovery_observed": True,
                "initial_online_epoch": 1,
                "recovered_online_epoch": 2,
            })
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            manifest["receipts"][role]["sha256"] = digest(receipt_path)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        verify_pair(root, "forced-tcp", "link-interruption")

        manifest.update({
            "scenario": "guest-restart",
            "link_interruption_count": 0,
            "device_guest_restart_count": 1,
        })
        for role in ROLES:
            receipt_path = root / manifest["receipts"][role]["path"]
            receipt = load(receipt_path)
            receipt.update({
                "scenario": "guest-restart",
                "link_interruption_observed": False,
                "link_recovery_observed": False,
                "guest_restart_observed": True,
                "guest_offline_observed": role == "client",
                "guest_identity_preserved": True,
                "fresh_session_after_guest_restart": True,
                "initial_guest_boot_id_sha256": "d" * 64,
                "recovered_guest_boot_id_sha256": (
                    "d" * 64 if role == "client" else "e" * 64
                ),
                "initial_online_epoch": 1,
                "recovered_online_epoch": 2 if role == "client" else 1,
            })
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            manifest["receipts"][role]["sha256"] = digest(receipt_path)

        device_receipt = root / manifest["receipts"]["device"]["path"]
        successor_receipt = (
            root
            / "device-restart/live/workspace-export/guest-receipts/iotox/pair.json"
        )
        successor_receipt.parent.mkdir(parents=True)
        device_receipt.rename(successor_receipt)
        manifest["receipts"]["device"]["path"] = str(successor_receipt.relative_to(root))
        device_chain = root / manifest["chains"]["device"]["path"]
        successor_chain = root / "device-restart/direct-cloud-hypervisor-live-chain.json"
        successor_chain.parent.mkdir(parents=True, exist_ok=True)
        successor_chain_value = load(device_chain)
        successor_chain_value["receipts"]["prelaunch_chain"]["path"] = str(
            root / "device/prelaunch/direct-cloud-hypervisor-prelaunch-chain.json"
        )
        successor_chain.write_text(json.dumps(successor_chain_value), encoding="utf-8")
        manifest["chains"]["device"]["sha256"] = digest(successor_chain)
        manifest["chains"]["device"]["path"] = str(successor_chain.relative_to(root))
        initial_chain = {
            "schema": "sandwurm.direct-cloud-hypervisor-live-chain.v0",
            "status": "blocked",
            "failure": {"blockers": ["live:console-not-observed"]},
        }
        device_chain.write_text(json.dumps(initial_chain), encoding="utf-8")
        initial_launch_path = root / "device/live/cloud-hypervisor-launch.json"
        initial_launch_path.parent.mkdir(parents=True, exist_ok=True)
        initial_launch_path.write_text(json.dumps({
            "status": "blocked",
            "vmm": {
                "process_observed": True,
                "exit_observed": True,
                "exit_status": 1,
                "argv": [
                    f"path={root}/device/prelaunch/runtime-root/runtime-root/"
                    "sandwurm-direct-cloud.raw,readonly=off"
                ],
            },
        }), encoding="utf-8")
        manifest["initial_device_chain"] = {
            "path": str(device_chain.relative_to(root)),
            "sha256": digest(device_chain),
            "status": "bounded-reboot-exit",
        }
        manifest["initial_device_launch"] = {
            "path": str(initial_launch_path.relative_to(root)),
            "sha256": digest(initial_launch_path),
            "status": "bounded-reboot-exit",
        }
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        verify_pair(root, "forced-tcp", "guest-restart")

        manifest.update({
            "scenario": "sync-file-guest-restart",
            "sync_file_convergence": True,
            "sync_cancellation": False,
            "sync_generation": 1,
            "sync_artifact_sha256": "d" * 64,
            "sync_manifest_sha256": "e" * 64,
            "sync_head_record": "f" * 64,
            "sync_client_daemon_restart_count": 0,
            "sync_unclean_stop_count": 0,
            "sync_interrupted_staging_bytes": 0,
            "sync_restart_recovered_role_count": 2,
            "sync_disconnect_staging_bytes": 0,
            "sync_disconnect_recovered_role_count": 0,
            "sync_disconnect_minimum_stable_samples": 0,
            "sync_guest_restart_staging_bytes": 4096,
            "sync_guest_restart_recovered_role_count": 2,
            "sync_guest_restart_minimum_stable_samples": 50,
        })
        for role in ROLES:
            receipt_path = root / manifest["receipts"][role]["path"]
            receipt = load(receipt_path)
            receipt.update({
                "scenario": "sync-file-guest-restart",
                "sync_authority_observed": True,
                "sync_convergence_observed": True,
                "sync_activation_observed": True,
                "sync_restart_observed": True,
                "sync_peer_offline_observed": role == "client",
                "sync_restart_recovery_observed": True,
                "sync_restart_identity_preserved": True,
                "sync_attempt_recovery_observed": False,
                "sync_unclean_stop_observed": False,
                "sync_daemon_restart_count": 0,
                "sync_interrupted_staging_bytes": 0,
                "sync_cancellation_observed": False,
                "sync_cancelled_staging_bytes": 0,
                "sync_cancelled_receive_count": 0,
                "sync_cancelled_job_id": "",
                "sync_disconnect_staging_bytes": 0,
                "sync_disconnect_cleanup_observed": False,
                "sync_disconnect_retry_observed": False,
                "sync_disconnect_stable_samples": 0,
                "sync_guest_restart_staging_bytes": (
                    4096 if role == "client" else 0
                ),
                "sync_guest_restart_cleanup_observed": True,
                "sync_guest_restart_retry_observed": True,
                "sync_guest_restart_stable_samples": 50,
                "sync_pause_observed": False,
                "sync_resume_observed": False,
                "sync_pause_position_bytes": 0,
                "sync_pause_stable_samples": 0,
                "sync_pause_file_id": "",
                "sync_generation": 1,
                "sync_artifact_bytes": 8 * 1024 * 1024,
                "sync_manifest_bytes": 1234,
                "sync_artifact_sha256": "d" * 64,
                "sync_manifest_sha256": "e" * 64,
                "sync_head_record": "f" * 64,
            })
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            manifest["receipts"][role]["sha256"] = digest(receipt_path)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        verify_pair(root, "forced-tcp", "sync-file-guest-restart")

        client_path = root / manifest["receipts"]["client"]["path"]
        client_receipt = load(client_path)
        client_receipt["sync_guest_restart_retry_observed"] = False
        client_path.write_text(json.dumps(client_receipt), encoding="utf-8")
        manifest["receipts"]["client"]["sha256"] = digest(client_path)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        try:
            verify_pair(root)
        except ValueError as error:
            require(
                "client synchronization guest-restart evidence is incomplete"
                in str(error),
                "sync-guest-restart self-test failed for the wrong reason",
            )
        else:
            raise ValueError("verifier accepted missing guest-restart retry")

        for role in ROLES:
            receipt_path = root / manifest["receipts"][role]["path"]
            receipt = load(receipt_path)
            receipt.update({
                "sync_guest_restart_staging_bytes": 0,
                "sync_guest_restart_cleanup_observed": False,
                "sync_guest_restart_retry_observed": False,
                "sync_guest_restart_stable_samples": 0,
            })
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            manifest["receipts"][role]["sha256"] = digest(receipt_path)

        device_chain.write_bytes(successor_chain.read_bytes())
        successor_chain.unlink()
        successor_receipt.rename(device_receipt)
        manifest["receipts"]["device"]["path"] = str(device_receipt.relative_to(root))
        manifest["chains"]["device"]["path"] = str(device_chain.relative_to(root))
        manifest["chains"]["device"]["sha256"] = digest(device_chain)
        initial_launch_path.unlink()

        manifest.update({
            "scenario": "daemon-restart",
            "bootstrap_fixture_restart_count": 0,
            "device_daemon_restart_count": 1,
            "link_interruption_count": 0,
            "device_guest_restart_count": 0,
            "initial_device_chain": None,
            "initial_device_launch": None,
            "sync_file_convergence": False,
            "sync_cancellation": False,
        })
        for role in ROLES:
            receipt_path = root / manifest["receipts"][role]["path"]
            receipt = load(receipt_path)
            receipt.update({
                "scenario": "daemon-restart",
                "relay_interruption_observed": False,
                "relay_recovery_observed": False,
                "link_interruption_observed": False,
                "link_recovery_observed": False,
                "guest_restart_observed": False,
                "guest_offline_observed": False,
                "guest_identity_preserved": False,
                "fresh_session_after_guest_restart": False,
                "daemon_replacement_observed": True,
                "daemon_offline_observed": role == "client",
                "daemon_identity_preserved": True,
                "fresh_session_after_daemon_restart": True,
                "daemon_restart_count": 1 if role == "device" else 0,
                "sync_authority_observed": False,
                "sync_convergence_observed": False,
                "sync_activation_observed": False,
                "sync_restart_observed": False,
                "sync_peer_offline_observed": False,
                "sync_restart_recovery_observed": False,
                "sync_restart_identity_preserved": False,
                "sync_attempt_recovery_observed": False,
                "sync_unclean_stop_observed": False,
                "sync_daemon_restart_count": 0,
                "sync_interrupted_staging_bytes": 0,
                "sync_cancellation_observed": False,
                "sync_cancelled_staging_bytes": 0,
                "sync_cancelled_receive_count": 0,
                "sync_cancelled_job_id": "",
                "sync_disconnect_staging_bytes": 0,
                "sync_disconnect_cleanup_observed": False,
                "sync_disconnect_retry_observed": False,
                "sync_disconnect_stable_samples": 0,
                "sync_guest_restart_staging_bytes": 0,
                "sync_guest_restart_cleanup_observed": False,
                "sync_guest_restart_retry_observed": False,
                "sync_guest_restart_stable_samples": 0,
                "sync_pause_observed": False,
                "sync_resume_observed": False,
                "sync_pause_position_bytes": 0,
                "sync_pause_stable_samples": 0,
                "sync_pause_file_id": "",
                "sync_generation": 0,
                "sync_artifact_bytes": 0,
                "sync_manifest_bytes": 0,
                "sync_artifact_sha256": "",
                "sync_manifest_sha256": "",
                "sync_head_record": "",
                "initial_online_epoch": 1,
                "recovered_online_epoch": 2 if role == "client" else 1,
            })
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            manifest["receipts"][role]["sha256"] = digest(receipt_path)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        verify_pair(root, "forced-tcp", "daemon-restart")

        manifest.update({
            "scenario": "sync-file-restart",
            "device_daemon_restart_count": 0,
            "sync_file_convergence": True,
            "sync_generation": 1,
            "sync_artifact_sha256": "d" * 64,
            "sync_manifest_sha256": "e" * 64,
            "sync_head_record": "f" * 64,
            "sync_client_daemon_restart_count": 1,
            "sync_unclean_stop_count": 1,
            "sync_interrupted_staging_bytes": 4096,
            "sync_restart_recovered_role_count": 2,
            "sync_guest_restart_staging_bytes": 0,
            "sync_guest_restart_recovered_role_count": 0,
            "sync_guest_restart_minimum_stable_samples": 0,
        })
        for role in ROLES:
            receipt_path = root / manifest["receipts"][role]["path"]
            receipt = load(receipt_path)
            receipt.update({
                "scenario": "sync-file-restart",
                "daemon_replacement_observed": False,
                "daemon_offline_observed": False,
                "daemon_identity_preserved": False,
                "fresh_session_after_daemon_restart": False,
                "daemon_restart_count": 0,
                "sync_authority_observed": True,
                "sync_convergence_observed": True,
                "sync_activation_observed": True,
                "sync_restart_observed": True,
                "sync_peer_offline_observed": role == "device",
                "sync_restart_recovery_observed": True,
                "sync_restart_identity_preserved": True,
                "sync_attempt_recovery_observed": role == "client",
                "sync_unclean_stop_observed": role == "client",
                "sync_daemon_restart_count": 1 if role == "client" else 0,
                "sync_interrupted_staging_bytes": 4096 if role == "client" else 0,
                "sync_generation": 1,
                "sync_artifact_bytes": 8 * 1024 * 1024,
                "sync_manifest_bytes": 1234,
                "sync_artifact_sha256": "d" * 64,
                "sync_manifest_sha256": "e" * 64,
                "sync_head_record": "f" * 64,
                "initial_online_epoch": 1,
                "recovered_online_epoch": 2 if role == "device" else 1,
            })
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            manifest["receipts"][role]["sha256"] = digest(receipt_path)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        verify_pair(root, "forced-tcp", "sync-file-restart")

        client_path = root / manifest["receipts"]["client"]["path"]
        client_receipt = load(client_path)
        client_receipt["sync_interrupted_staging_bytes"] = 0
        client_path.write_text(json.dumps(client_receipt), encoding="utf-8")
        manifest["receipts"]["client"]["sha256"] = digest(client_path)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        try:
            verify_pair(root)
        except ValueError as error:
            require(
                "client synchronization restart evidence is incomplete"
                in str(error),
                "sync-restart self-test failed for the wrong reason",
            )
        else:
            raise ValueError("verifier accepted zero interrupted staging bytes")

        manifest.update({
            "scenario": "sync-file-cancel",
            "sync_file_convergence": False,
            "sync_cancellation": True,
            "sync_client_daemon_restart_count": 0,
            "sync_unclean_stop_count": 0,
            "sync_interrupted_staging_bytes": 0,
            "sync_restart_recovered_role_count": 0,
            "sync_cancelled_staging_bytes": 4096,
            "sync_cancelled_receive_count": 1,
        })
        for role in ROLES:
            receipt_path = root / manifest["receipts"][role]["path"]
            receipt = load(receipt_path)
            receipt.update({
                "scenario": "sync-file-cancel",
                "sync_convergence_observed": False,
                "sync_activation_observed": False,
                "sync_restart_observed": False,
                "sync_peer_offline_observed": False,
                "sync_restart_recovery_observed": False,
                "sync_restart_identity_preserved": False,
                "sync_attempt_recovery_observed": False,
                "sync_unclean_stop_observed": False,
                "sync_daemon_restart_count": 0,
                "sync_interrupted_staging_bytes": 0,
                "sync_cancellation_observed": True,
                "sync_cancelled_staging_bytes": 4096,
                "sync_cancelled_receive_count": 1,
                "sync_cancelled_job_id": "123456789",
                "recovered_online_epoch": 1,
            })
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            manifest["receipts"][role]["sha256"] = digest(receipt_path)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        verify_pair(root, "forced-tcp", "sync-file-cancel")

        client_receipt = load(client_path)
        client_receipt["sync_cancellation_observed"] = False
        client_path.write_text(json.dumps(client_receipt), encoding="utf-8")
        manifest["receipts"]["client"]["sha256"] = digest(client_path)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        try:
            verify_pair(root)
        except ValueError as error:
            require(
                "client synchronization boundary is incomplete" in str(error),
                "sync-cancellation self-test failed for the wrong reason",
            )
        else:
            raise ValueError("verifier accepted missing cancellation evidence")

        manifest.update({
            "scenario": "sync-file-disconnect",
            "link_interruption_count": 1,
            "sync_file_convergence": True,
            "sync_cancellation": False,
            "sync_client_daemon_restart_count": 0,
            "sync_unclean_stop_count": 0,
            "sync_interrupted_staging_bytes": 0,
            "sync_restart_recovered_role_count": 0,
            "sync_disconnect_staging_bytes": 4096,
            "sync_disconnect_recovered_role_count": 2,
            "sync_disconnect_minimum_stable_samples": 50,
            "sync_cancelled_staging_bytes": 0,
            "sync_cancelled_receive_count": 0,
        })
        for role in ROLES:
            receipt_path = root / manifest["receipts"][role]["path"]
            receipt = load(receipt_path)
            receipt.update({
                "scenario": "sync-file-disconnect",
                "initial_online_epoch": 1,
                "recovered_online_epoch": 2,
                "link_interruption_observed": True,
                "link_recovery_observed": True,
                "sync_authority_observed": True,
                "sync_convergence_observed": True,
                "sync_activation_observed": True,
                "sync_restart_observed": False,
                "sync_peer_offline_observed": True,
                "sync_restart_recovery_observed": False,
                "sync_restart_identity_preserved": False,
                "sync_attempt_recovery_observed": False,
                "sync_unclean_stop_observed": False,
                "sync_daemon_restart_count": 0,
                "sync_interrupted_staging_bytes": 0,
                "sync_cancellation_observed": False,
                "sync_cancelled_staging_bytes": 0,
                "sync_cancelled_receive_count": 0,
                "sync_cancelled_job_id": "",
                "sync_disconnect_staging_bytes": 4096 if role == "client" else 0,
                "sync_disconnect_cleanup_observed": True,
                "sync_disconnect_retry_observed": True,
                "sync_disconnect_stable_samples": 50,
            })
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            manifest["receipts"][role]["sha256"] = digest(receipt_path)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        verify_pair(root, "forced-tcp", "sync-file-disconnect")

        client_receipt = load(client_path)
        client_receipt["sync_disconnect_retry_observed"] = False
        client_path.write_text(json.dumps(client_receipt), encoding="utf-8")
        manifest["receipts"]["client"]["sha256"] = digest(client_path)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        try:
            verify_pair(root)
        except ValueError as error:
            require(
                "client synchronization disconnect evidence is incomplete"
                in str(error),
                "sync-disconnect self-test failed for the wrong reason",
            )
        else:
            raise ValueError("verifier accepted missing disconnect retry evidence")

        manifest.update({
            "scenario": "sync-file-pause",
            "link_interruption_count": 0,
            "sync_file_convergence": True,
            "sync_cancellation": False,
            "sync_client_daemon_restart_count": 0,
            "sync_unclean_stop_count": 0,
            "sync_interrupted_staging_bytes": 0,
            "sync_restart_recovered_role_count": 0,
            "sync_disconnect_staging_bytes": 0,
            "sync_disconnect_recovered_role_count": 0,
            "sync_disconnect_minimum_stable_samples": 0,
            "sync_cancelled_staging_bytes": 0,
            "sync_cancelled_receive_count": 0,
            "sync_pause_observed_role_count": 2,
            "sync_pause_position_bytes": 4096,
            "sync_pause_minimum_stable_samples": 20,
            "sync_pause_file_id": "a" * 64,
        })
        for role in ROLES:
            receipt_path = root / manifest["receipts"][role]["path"]
            receipt = load(receipt_path)
            receipt.update({
                "scenario": "sync-file-pause",
                "initial_online_epoch": 1,
                "recovered_online_epoch": 1,
                "link_interruption_observed": False,
                "link_recovery_observed": False,
                "sync_peer_offline_observed": False,
                "sync_disconnect_staging_bytes": 0,
                "sync_disconnect_cleanup_observed": False,
                "sync_disconnect_retry_observed": False,
                "sync_disconnect_stable_samples": 0,
                "sync_pause_observed": True,
                "sync_resume_observed": True,
                "sync_pause_position_bytes": 4096,
                "sync_pause_stable_samples": 20,
                "sync_pause_file_id": "a" * 64,
            })
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            manifest["receipts"][role]["sha256"] = digest(receipt_path)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        verify_pair(root, "forced-tcp", "sync-file-pause")

        client_receipt = load(client_path)
        client_receipt["sync_resume_observed"] = False
        client_path.write_text(json.dumps(client_receipt), encoding="utf-8")
        manifest["receipts"]["client"]["sha256"] = digest(client_path)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        try:
            verify_pair(root)
        except ValueError as error:
            require(
                "client synchronization pause/resume evidence is invalid"
                in str(error),
                "sync-pause self-test failed for the wrong reason",
            )
        else:
            raise ValueError("verifier accepted missing synchronization resume")

        manifest.update({
            "scenario": "daemon-restart",
            "device_daemon_restart_count": 1,
            "link_interruption_count": 0,
            "sync_file_convergence": False,
            "sync_generation": 0,
            "sync_artifact_sha256": "",
            "sync_manifest_sha256": "",
            "sync_head_record": "",
            "sync_client_daemon_restart_count": 0,
            "sync_unclean_stop_count": 0,
            "sync_interrupted_staging_bytes": 0,
            "sync_restart_recovered_role_count": 0,
            "sync_cancellation": False,
            "sync_cancelled_staging_bytes": 0,
            "sync_cancelled_receive_count": 0,
            "sync_disconnect_staging_bytes": 0,
            "sync_disconnect_recovered_role_count": 0,
            "sync_disconnect_minimum_stable_samples": 0,
            "sync_pause_observed_role_count": 0,
            "sync_pause_position_bytes": 0,
            "sync_pause_minimum_stable_samples": 0,
            "sync_pause_file_id": "",
        })
        for role in ROLES:
            receipt_path = root / manifest["receipts"][role]["path"]
            receipt = load(receipt_path)
            receipt.update({
                "scenario": "daemon-restart",
                "link_interruption_observed": False,
                "link_recovery_observed": False,
                "daemon_replacement_observed": True,
                "daemon_offline_observed": role == "client",
                "daemon_identity_preserved": True,
                "fresh_session_after_daemon_restart": True,
                "daemon_restart_count": 1 if role == "device" else 0,
                "sync_authority_observed": False,
                "sync_convergence_observed": False,
                "sync_activation_observed": False,
                "sync_restart_observed": False,
                "sync_peer_offline_observed": False,
                "sync_restart_recovery_observed": False,
                "sync_restart_identity_preserved": False,
                "sync_attempt_recovery_observed": False,
                "sync_unclean_stop_observed": False,
                "sync_daemon_restart_count": 0,
                "sync_interrupted_staging_bytes": 0,
                "sync_cancellation_observed": False,
                "sync_cancelled_staging_bytes": 0,
                "sync_cancelled_receive_count": 0,
                "sync_cancelled_job_id": "",
                "sync_disconnect_staging_bytes": 0,
                "sync_disconnect_cleanup_observed": False,
                "sync_disconnect_retry_observed": False,
                "sync_disconnect_stable_samples": 0,
                "sync_pause_observed": False,
                "sync_resume_observed": False,
                "sync_pause_position_bytes": 0,
                "sync_pause_stable_samples": 0,
                "sync_pause_file_id": "",
                "sync_generation": 0,
                "sync_artifact_bytes": 0,
                "sync_manifest_bytes": 0,
                "sync_artifact_sha256": "",
                "sync_manifest_sha256": "",
                "sync_head_record": "",
                "initial_online_epoch": 1,
                "recovered_online_epoch": 2 if role == "client" else 1,
            })
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            manifest["receipts"][role]["sha256"] = digest(receipt_path)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        client_receipt = load(client_path)
        client_receipt["recovered_online_epoch"] = 1
        client_path.write_text(json.dumps(client_receipt), encoding="utf-8")
        manifest["receipts"]["client"]["sha256"] = digest(client_path)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        try:
            verify_pair(root)
        except ValueError as error:
            require(
                "stable client online epoch did not advance" in str(error),
                "stale-epoch self-test failed for the wrong reason",
            )
        else:
            raise ValueError("verifier accepted a stale recovered online epoch")

        manifest["receipts"]["client"]["sha256"] = "f" * 64
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        try:
            verify_pair(root)
        except ValueError as error:
            require("receipt digest mismatch" in str(error), "negative self-test failed for the wrong reason")
        else:
            raise ValueError("verifier accepted a forged receipt digest")
    print("sandwurm-pair verifier self-test: PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("proof_root", nargs="?", type=Path)
    parser.add_argument("--route", choices=tuple(ROUTES))
    parser.add_argument(
        "--scenario",
        choices=(
            "baseline",
            "relay-restart",
            "proxy-restart",
            "i2p-router-restart",
            "i2p-service-restart",
            "daemon-restart",
            "link-interruption",
            "packet-loss",
            "guest-restart",
            "ratox-idle",
            "ratox-matrix-idle",
            "ratox-route-impairment",
            "ratox-route-loss",
            "ratox-cli-reconnect",
            "ratox-cli-reconnect-repeated",
            "ratox-route-actual-tor-loss",
            "ratox-route-actual-tor-soak",
            "ratox-route-actual-tor-adversary",
            *MUTABLE_SCENARIOS,
            *BIDIRECTIONAL_SYNC_SCENARIOS,
            *AUTOMATION_SYNC_SCENARIOS,
            *SYNC_SCENARIOS,
            *RATOX_BULK_SCENARIOS,
        ),
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.proof_root is None:
        parser.error("proof_root is required unless --self-test is used")
    print(
        json.dumps(
            verify_pair(args.proof_root, args.route, args.scenario),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
