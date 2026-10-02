#!/usr/bin/env python3
"""Export the exact content-free, independently verifiable pair evidence set."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PAIR_ROOT = (ROOT / ".sandwurm/lab/pairs").resolve()
EXPORT_ROOT = (ROOT / ".sandwurm/exports/pairs").resolve()
SCHEMA = "iotox.sandwurm-pair-compact-export.v0"
ROLES = ("client", "device")
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
    "ratox-bulk-1",
    "ratox-bulk-8",
    "ratox-bulk-16",
    "ratox-bulk-32",
    "ratox-bulk-64",
    "ratox-matrix-bulk-1",
    "ratox-matrix-bulk-8",
    "ratox-matrix-bulk-16",
    "ratox-matrix-bulk-32",
    "ratox-matrix-bulk-64",
    "ratox-stripe-32",
    "ratox-stripe-40",
    "ratox-stripe-48",
    "ratox-stripe-56",
    "ratox-stripe-64",
    "ratox-stripe-recovery-32",
    "ratox-stripe-live-loss-32",
    "ratox-stripe-protected-live-loss-24",
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
RATOX_STRIPE_SCENARIOS = {
    "ratox-stripe-32",
    "ratox-stripe-40",
    "ratox-stripe-48",
    "ratox-stripe-56",
    "ratox-stripe-64",
    "ratox-stripe-recovery-32",
    "ratox-stripe-live-loss-32",
    "ratox-stripe-protected-live-loss-24",
}
SYNC_SCENARIOS = {
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
    "sync-file",
    "sync-content",
    "sync-content-same-source-lanes",
    "sync-content-restart-cap-2",
    "sync-content-restart-cap-4",
    "sync-content-lane-science",
    "sync-content-lane-science-reverse",
    "sync-content-ratox-latency-science",
    "sync-content-ratox-cap-2-sla",
    "sync-content-ratox-post-bulk-admission",
    "sync-content-route-private-actual-tor",
    "sync-content-same-source-multi-route-actual-tor",
    "sync-content-multi-route-actual-tor",
    "sync-content-multi-route-actual-tor-loss",
    "sync-content-multi-source",
    "sync-content-multi-source-loss",
    "sync-file-range-restart-resume",
    "signed-update",
    "update-service",
    "sync-file-range",
    "sync-file-range-actual-i2p",
    "sync-file-range-actual-i2p-loss",
    "sync-file-corrupt-basis",
    "sync-file-range-retry",
    "sync-file-range-route-loss",
    "sync-file-range-late-route-loss",
    "sync-file-range-repeated-route-loss",
    "sync-file-range-triple-route-loss",
    "sync-file-repair",
    "sync-file-restart",
    "sync-file-restart-resume",
    "sync-file-guest-restart",
    "sync-file-pause",
    "sync-file-cancel",
    "sync-file-disconnect",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            value.update(chunk)
    return value.hexdigest()


def load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def evidence_paths(scenario: str, source: Path) -> tuple[str, ...]:
    values = [
        "pair-manifest.json",
        "client/direct-cloud-hypervisor-live-chain.json",
        "client/prelaunch/launch/cloud-hypervisor-launch.json",
        "client/live/workspace-export/guest-receipts/iotox/pair.json",
        "device/prelaunch/launch/cloud-hypervisor-launch.json",
    ]
    if scenario in {"guest-restart", "sync-file-guest-restart"}:
        values.extend((
            "device/direct-cloud-hypervisor-live-chain.json",
            "device/live/cloud-hypervisor-launch.json",
            "device-restart/direct-cloud-hypervisor-live-chain.json",
            "device-restart/live/workspace-export/guest-receipts/iotox/pair.json",
        ))
    else:
        values.extend((
            "device/direct-cloud-hypervisor-live-chain.json",
            "device/live/workspace-export/guest-receipts/iotox/pair.json",
        ))
    if scenario in {
        "sync-content",
        "sync-content-same-source-lanes",
        "sync-content-restart-cap-2",
        "sync-content-restart-cap-4",
        "sync-content-lane-science",
        "sync-content-lane-science-reverse",
        "sync-content-ratox-latency-science",
        "sync-content-ratox-cap-2-sla",
        "sync-content-ratox-post-bulk-admission",
        "sync-content-route-private-actual-tor",
        "sync-content-same-source-multi-route-actual-tor",
        "sync-content-multi-route-actual-tor",
        "sync-content-multi-route-actual-tor-loss",
        "sync-content-multi-source",
        "sync-content-multi-source-loss",
    }:
        values.append(
            "client/live/workspace-export/iotox-rendezvous/"
            "client.sync-complete"
        )
    if scenario in {
        "sync-content-restart-cap-2",
        "sync-content-restart-cap-4",
    }:
        values.extend(
            (
                "client/live/workspace-export/iotox-rendezvous/"
                "client.sync-interruption-ready",
                "client/live/workspace-export/iotox-rendezvous/"
                "client.sync-crash-state",
            )
        )
    if scenario in {
        "sync-content-lane-science",
        "sync-content-lane-science-reverse",
        "sync-content-ratox-latency-science",
        "sync-content-ratox-cap-2-sla",
        "sync-content-ratox-post-bulk-admission",
    }:
        values.append(
            "client/live/workspace-export/guest-receipts/iotox/"
            "content-lane-science.tsv"
        )
        values.extend(
            "client/live/workspace-export/guest-receipts/iotox/"
            f"content-lane-science-cap-{cap}-resource.tsv"
            for cap in (1, 2, 4, 8)
        )
    if scenario in {
        "sync-content-ratox-latency-science",
        "sync-content-ratox-cap-2-sla",
    }:
        values.extend(
            (
                "client/live/workspace-export/guest-receipts/iotox/"
                "content-ratox-overlap-metadata.tsv",
                "client/live/workspace-export/guest-receipts/iotox/"
                "content-ratox-latency.tsv",
                "client/live/workspace-export/iotox-rendezvous/"
                "client.content-ratox-readiness",
                "client/live/workspace-export/guest-receipts/iotox/"
                "content-ratox-timeline.tsv",
            )
        )
    if scenario == "sync-content-ratox-post-bulk-admission":
        values.extend(
            (
                "client/live/workspace-export/guest-receipts/iotox/"
                "content-ratox-post-bulk-readiness.tsv",
                "client/live/workspace-export/guest-receipts/iotox/"
                "content-ratox-post-bulk-capture.tsv",
                "client/live/workspace-export/guest-receipts/iotox/"
                "content-ratox-post-bulk-admission.tsv",
            )
        )
    secondary_bootstrap_public_id = (
        source / "host-bootstrap-secondary/PUBLIC_ID.txt"
    )
    if (
        scenario
        in {
            "sync-content-multi-route-actual-tor",
            "sync-content-multi-route-actual-tor-loss",
            "sync-content-multi-source",
            "sync-content-multi-source-loss",
        }
        and secondary_bootstrap_public_id.is_file()
    ):
        require(
            not secondary_bootstrap_public_id.is_symlink(),
            "secondary bootstrap public identity is a symbolic link",
        )
        values.append("host-bootstrap-secondary/PUBLIC_ID.txt")
    if scenario in RATOX_SCENARIOS:
        values.extend((
            "client/live/workspace-export/guest-receipts/iotox/ratox-controller-capture.tsv",
            "device/live/workspace-export/guest-receipts/iotox/ratox-host-events.txt",
            "device/live/workspace-export/guest-receipts/iotox/ratox-host-status.txt",
        ))
        resource_paths = tuple(
            f"{role}/live/workspace-export/guest-receipts/iotox/ratox-resource-interval.tsv"
            for role in ("client", "device")
        )
        present = tuple(path for path in resource_paths if (source / path).is_file())
        require(
            len(present) in {0, len(resource_paths)},
            "Ratox resource intervals are only partially present",
        )
        values.extend(present)
        status_paths = tuple(
            f"{role}/live/workspace-export/guest-receipts/iotox/ratox-agent-status.txt"
            for role in ("client", "device")
        )
        present = tuple(path for path in status_paths if (source / path).is_file())
        require(
            len(present) in {0, len(status_paths)},
            "Ratox agent statuses are only partially present",
        )
        values.extend(present)
    if scenario == "ratox-route-impairment":
        values.extend((
            "ratox-route-impairment.json",
            "client/live/workspace-export/guest-receipts/iotox/"
            "ratox-heartbeat-capture.tsv",
        ))
    if scenario in {
        "ratox-route-loss",
        "ratox-cli-reconnect",
        "ratox-cli-reconnect-repeated",
        "ratox-route-actual-tor-loss",
        "ratox-route-actual-tor-adversary",
    }:
        values.extend((
            "ratox-route-loss.json",
            "client/live/workspace-export/guest-receipts/iotox/"
            "ratox-heartbeat-capture.tsv",
            "client/live/workspace-export/guest-receipts/iotox/"
            "ratox-route-loss-probe.json",
            "device/live/workspace-export/guest-receipts/iotox/"
            "ratox-host-loss-events.txt",
            "device/live/workspace-export/guest-receipts/iotox/"
            "ratox-host-loss-status.txt",
        ))
    if scenario == "ratox-route-actual-tor-soak":
        values.extend((
            "actual-tor-ratox-churn.json",
            "client/live/workspace-export/guest-receipts/iotox/"
            "ratox-heartbeat-capture.tsv",
            "client/live/workspace-export/guest-receipts/iotox/"
            "ratox-circuit-churn-probe.json",
        ))
        for role, ordinal in (("client", 20), ("device", 100)):
            for phase in ("before", "after"):
                for status in ("stream", "circuit"):
                    values.append(
                        f"tor-{role}-churn-{ordinal}-{phase}-{status}-status.txt"
                    )
    if scenario == "sync-tree-route-population":
        values.extend((
            "client/live/workspace-export/guest-receipts/iotox/"
            "sync-route-population-fixed-resource.tsv",
            "client/live/workspace-export/guest-receipts/iotox/"
            "sync-route-population-adaptive-resource.tsv",
        ))
    if scenario in {
        "sync-tree-route-concurrent-cancel",
        "sync-tree-route-common-link-fairness",
    }:
        values.append(
            "client/live/workspace-export/guest-receipts/iotox/"
            "sync-route-concurrent-cancel-resource.tsv"
        )
    if scenario in {
        "sync-tree-route-population-loss",
        "sync-tree-route-loss-admission",
    }:
        values.append(
            "client/live/workspace-export/guest-receipts/iotox/"
            "sync-route-population-loss-resource.tsv"
        )
    if scenario == "sync-tree-route-startup-admission":
        values.append(
            "client/live/workspace-export/guest-receipts/iotox/"
            "sync-route-startup-admission-resource.tsv"
        )
    if scenario == "sync-tree-route-throughput":
        values.extend(
            "client/live/workspace-export/guest-receipts/iotox/"
            f"sync-route-throughput-{phase}-resource.tsv"
            for phase in (
                "fixed-a",
                "adaptive-a",
                "adaptive-b",
                "fixed-b",
            )
        )
    if scenario in {
        "sync-file-range-repeated-route-loss",
        "sync-file-range-triple-route-loss",
    }:
        values.extend((
            "client/live/workspace-export/iotox-rendezvous/"
            "client.sync-range-loss-progress",
            "client/live/workspace-export/iotox-rendezvous/"
            "client.sync-range-postconditions",
        ))
    if scenario == "sync-file-range-triple-route-loss":
        values.extend((
            "device/live/workspace-export/iotox-rendezvous/"
            "device.sync-range-live-status",
            "device/live/workspace-export/iotox-rendezvous/"
            "device.sync-range-live-routes",
        ))
    if scenario == "sync-content-multi-source-loss":
        values.extend((
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
        ))
        replica_imported = (
            source
            / "device/live/workspace-export/iotox-rendezvous/"
            "device.multi-source-loss-replica-imported"
        )
        if replica_imported.is_file():
            require(
                not replica_imported.is_symlink(),
                "durable replica import checkpoint is a symbolic link",
            )
            values.append(
                "device/live/workspace-export/iotox-rendezvous/"
                "device.multi-source-loss-replica-imported"
            )
    if scenario == "sync-content-multi-route-actual-tor-loss":
        values.extend((
            "client/live/workspace-export/iotox-rendezvous/"
            "client.multi-source-loss-failed",
            "client/live/workspace-export/iotox-rendezvous/"
            "client.multi-source-loss-recovered",
        ))
    if scenario in {
        "sync-content-multi-route-actual-tor",
        "sync-content-multi-route-actual-tor-loss",
    }:
        values.append(
            "client/live/workspace-export/iotox-rendezvous/"
            "client.content-multi-route"
        )
    if scenario == "sync-content-same-source-multi-route-actual-tor":
        values.append(
            "client/live/workspace-export/iotox-rendezvous/"
            "client.content-same-source-multi-route"
        )
    if scenario == "sync-file-range-restart-resume":
        values.extend((
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
        ))
    if scenario in RATOX_BULK_SCENARIOS:
        values.append(
            "client/live/workspace-export/guest-receipts/iotox/ratox-bulk-observation.tsv"
        )
    if scenario in RATOX_STRIPE_SCENARIOS:
        values.extend((
            "client/live/workspace-export/guest-receipts/iotox/ratox-stripe-routes.tsv",
            "device/live/workspace-export/guest-receipts/iotox/ratox-stripe-routes.tsv",
        ))
    if scenario == "packet-loss":
        values.extend((
            "client/live/workspace-export/guest-receipts/iotox/packet-loss-burst.tsv",
            "device/live/workspace-export/guest-receipts/iotox/packet-loss-burst.tsv",
        ))
    if scenario == "proxy-restart":
        values.extend((
            "client.tox-tor.pcapng",
            "client.tox-tor.dumpcap.log",
            "device.tox-tor.pcapng",
            "device.tox-tor.dumpcap.log",
            "socks5-initial-audit.jsonl",
            "socks5-restart-audit.jsonl",
            "tox-tor-containment.json",
        ))
    elif scenario == "sync-tree-route-private-mixed":
        values.extend((
            "client.tox-tor.pcapng",
            "client.tox-tor.dumpcap.log",
            "device.tox-tor.pcapng",
            "device.tox-tor.dumpcap.log",
            "socks5-initial-audit.jsonl",
            "mixed-route-containment.json",
        ))
    elif scenario in {
        "sync-tree-route-private-actual-tor",
        "sync-tree-route-private-actual-tor-payload",
        "sync-tree-route-private-actual-tor-loss",
        "sync-content-route-private-actual-tor",
        "sync-content-same-source-multi-route-actual-tor",
        "sync-content-multi-route-actual-tor",
        "sync-content-multi-route-actual-tor-loss",
    }:
        values.extend((
            "client.tox-tor.pcapng",
            "client.tox-tor.dumpcap.log",
            "device.tox-tor.pcapng",
            "device.tox-tor.dumpcap.log",
            "actual-tor-mixed-route-containment.json",
        ))
        if scenario == "sync-tree-route-private-actual-tor-loss":
            values.extend((
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
            ))
        else:
            values.extend((
                "tor-client-control-events.txt",
                "tor-client-bootstrap-status.txt",
                "tor-client-circuit-status.txt",
                "tor-device-control-events.txt",
                "tor-device-bootstrap-status.txt",
                "tor-device-circuit-status.txt",
            ))
    elif scenario == "ratox-route-actual-tor-loss":
        values.extend((
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
        ))
    elif scenario == "ratox-route-actual-tor-soak":
        values.extend((
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
        ))
    elif scenario == "ratox-route-actual-tor-adversary":
        values.extend((
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
        ))
    elif scenario in {
        "ratox-route-impairment",
        "ratox-route-loss",
        "ratox-cli-reconnect",
    } and (
        source / "tox-tor-containment.json"
    ).is_file():
        values.extend((
            "client.tox-tor.pcapng",
            "client.tox-tor.dumpcap.log",
            "device.tox-tor.pcapng",
            "device.tox-tor.dumpcap.log",
            "socks5-initial-audit.jsonl",
            "tox-tor-containment.json",
        ))
    if (source / "tox-i2p-containment.json").is_file():
        values.extend((
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
        ))
        if scenario == "i2p-service-restart":
            values.extend((
                "i2p-fronts/forward-restart-1.audit.jsonl",
                "i2p-fronts/forward-restart-2.audit.jsonl",
                "i2p-fronts/forward-restart-3.audit.jsonl",
            ))
        if scenario in {
            "sync-tree-route-private-actual-i2p-loss",
            "sync-file-range-actual-i2p-loss",
        }:
            values.append("actual-i2p-fail-closed-loss.json")
    return tuple(values)


def verify_with_repository(path: Path, route: str, scenario: str) -> None:
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools/verify-sandwurm-pair.py"),
            str(path),
            "--route",
            route,
            "--scenario",
            scenario,
        ],
        check=True,
        stdout=subprocess.DEVNULL,
    )


def export(source: Path, destination: Path) -> dict:
    source = source.resolve()
    destination = destination.resolve()
    require(source.parent == PAIR_ROOT, "source is not an immediate pair proof root")
    require(PAIR_NAME.fullmatch(source.name) is not None, "source proof name is invalid")
    require(source.is_dir() and not source.is_symlink(), "source proof root is absent or unsafe")
    require(destination.parent == EXPORT_ROOT, "destination escaped the compact export root")
    require(PAIR_NAME.fullmatch(destination.name) is not None, "destination name is invalid")
    require(not destination.exists(), "compact export destination already exists")

    source_manifest_path = source / "pair-manifest.json"
    manifest = load(source_manifest_path)
    require(
        manifest.get("proof_root_contains_private_guest_disks") is True,
        "source is not an uncompacted private pair proof",
    )
    require(manifest.get("compact_export") is None, "source already claims compact form")
    route = manifest.get("route_mode")
    scenario = manifest.get("scenario", "baseline")
    require(
        route
        in {
            "direct-udp",
            "forced-tcp",
            "tox-tor",
            "tox-i2p",
            "tox-i2p-construction",
        },
        "source route is invalid",
    )
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
        "source scenario is invalid",
    )
    verify_with_repository(source, route, scenario)

    source_manifest_sha256 = digest(source_manifest_path)
    EXPORT_ROOT.mkdir(parents=True, exist_ok=True, mode=0o700)
    temporary = Path(tempfile.mkdtemp(prefix=f".{source.name}.", dir=EXPORT_ROOT))
    os.chmod(temporary, 0o700)
    try:
        paths = evidence_paths(scenario, source)
        for relative in paths[1:]:
            source_path = (source / relative).resolve()
            require(source_path.is_relative_to(source), f"source evidence escaped: {relative}")
            require(source_path.is_file() and not source_path.is_symlink(), f"source evidence is absent: {relative}")
            destination_path = temporary / relative
            destination_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            shutil.copyfile(source_path, destination_path)
            os.chmod(destination_path, 0o600)

        compact_declaration = {
            "schema": SCHEMA,
            "source_proof_id": source.name,
            "source_manifest_sha256": source_manifest_sha256,
            "source_proof_root_contained_private_guest_disks": True,
        }
        manifest["proof_root_contains_private_guest_disks"] = False
        manifest["compact_export"] = compact_declaration
        compact_manifest_path = temporary / "pair-manifest.json"
        compact_manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.chmod(compact_manifest_path, 0o600)

        files = {
            relative: digest(temporary / relative)
            for relative in paths
        }
        export_manifest = {
            "schema": SCHEMA,
            "status": "passed",
            "contains_secrets": False,
            "source_proof_id": source.name,
            "source_manifest_sha256": source_manifest_sha256,
            "source_private_artifacts_omitted": [
                "bootstrap-secret-key",
                "guest-disks",
                "injected-identities",
                "runtime-state",
            ],
            "files": files,
        }
        export_manifest_path = temporary / "compact-export.json"
        export_manifest_path.write_text(
            json.dumps(export_manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.chmod(export_manifest_path, 0o600)

        verify_with_repository(temporary, route, scenario)
        temporary.rename(destination)
        temporary = Path()
        result = {
            "schema": SCHEMA,
            "status": "passed",
            "source_proof_id": source.name,
            "destination": str(destination),
            "route_mode": route,
            "scenario": scenario,
            "allocated_bytes": int(
                subprocess.run(
                    ["du", "-s", "--block-size=1", "--", str(destination)],
                    check=True,
                    text=True,
                    capture_output=True,
                ).stdout.split(maxsplit=1)[0]
            ),
        }
        return result
    finally:
        if temporary != Path() and temporary.exists():
            shutil.rmtree(temporary)


def self_test() -> None:
    require(
        "sync-bidirectional" in BIDIRECTIONAL_SYNC_SCENARIOS,
        "bidirectional synchronization export scenario is not registered",
    )
    require(
        "sync-automation" in AUTOMATION_SYNC_SCENARIOS,
        "unattended synchronization export scenario is not registered",
    )
    with tempfile.TemporaryDirectory(prefix="iotox-pair-export-test-") as directory:
        source = Path(directory)
        (source / "tox-i2p-containment.json").touch()
        i2p_paths = set(
            evidence_paths("sync-tree-route-private-actual-i2p-payload", source)
        )
        require("client.tox-i2p.pcapng" in i2p_paths, "actual-I2P client capture omitted")
        require("device.tox-i2p.pcapng" in i2p_paths, "actual-I2P device capture omitted")
        require("i2p-fronts/topology-final.json" in i2p_paths, "actual-I2P topology omitted")
        require(
            "i2p-fronts/adapter.audit.jsonl" in i2p_paths,
            "actual-I2P adapter audit omitted",
        )
        require("client.tox-tor.pcapng" not in i2p_paths, "actual-I2P selected Tor evidence")
        require(
            "actual-tor-mixed-route-containment.json" not in i2p_paths,
            "actual-I2P selected Tor containment",
        )
        loss_paths = set(
            evidence_paths("sync-tree-route-private-actual-i2p-loss", source)
        )
        require(
            "actual-i2p-fail-closed-loss.json" in loss_paths,
            "actual-I2P fail-closed loss record omitted",
        )

        repeated_loss_paths = set(
            evidence_paths("sync-file-range-repeated-route-loss", source)
        )
        require(
            "client/live/workspace-export/iotox-rendezvous/"
            "client.sync-range-loss-progress" in repeated_loss_paths,
            "repeated range-loss progress checkpoint omitted",
        )
        require(
            "client/live/workspace-export/iotox-rendezvous/"
            "client.sync-range-postconditions" in repeated_loss_paths,
            "repeated range-loss postconditions omitted",
        )
        triple_loss_paths = set(
            evidence_paths("sync-file-range-triple-route-loss", source)
        )
        require(
            repeated_loss_paths < triple_loss_paths
            and "device/live/workspace-export/iotox-rendezvous/"
            "device.sync-range-live-status" in triple_loss_paths
            and "device/live/workspace-export/iotox-rendezvous/"
            "device.sync-range-live-routes" in triple_loss_paths,
            "triple range-loss compact evidence omits its watchdog records",
        )
        content_paths = set(evidence_paths("sync-content", source))
        require(
            "client/live/workspace-export/iotox-rendezvous/"
            "client.sync-complete" in content_paths,
            "content-v2 compact evidence omits its exact completion record",
        )
        routed_content_paths = set(
            evidence_paths("sync-content-route-private-actual-tor", source)
        )
        require(
            content_paths < routed_content_paths
            and "actual-tor-mixed-route-containment.json" in routed_content_paths
            and "client.tox-tor.pcapng" in routed_content_paths
            and "device.tox-tor.pcapng" in routed_content_paths,
            "actual-Tor content compact evidence omits completion or carrier proof",
        )
        routed_multi_content_paths = set(
            evidence_paths("sync-content-multi-route-actual-tor", source)
        )
        require(
            routed_content_paths <= routed_multi_content_paths,
            "actual-Tor multi-source compact evidence regressed its carrier proof",
        )
        same_source_multi_route_paths = set(
            evidence_paths(
                "sync-content-same-source-multi-route-actual-tor", source
            )
        )
        require(
            routed_content_paths < same_source_multi_route_paths
            and "client/live/workspace-export/iotox-rendezvous/"
            "client.content-same-source-multi-route"
            in same_source_multi_route_paths,
            "actual-Tor same-source multi-route evidence omits its path proof",
        )
        routed_multi_loss_paths = set(
            evidence_paths(
                "sync-content-multi-route-actual-tor-loss", source
            )
        )
        require(
            routed_multi_content_paths < routed_multi_loss_paths
            and "client/live/workspace-export/iotox-rendezvous/"
            "client.multi-source-loss-failed" in routed_multi_loss_paths
            and "client/live/workspace-export/iotox-rendezvous/"
            "client.multi-source-loss-recovered" in routed_multi_loss_paths,
            "actual-Tor multi-source loss compact evidence omits checkpoints",
        )
        source_loss_paths = set(
            evidence_paths("sync-content-multi-source-loss", source)
        )
        require(
            {
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
            }
            < source_loss_paths,
            "selected-source loss compact evidence omits exact checkpoints",
        )

        (source / "tox-i2p-containment.json").unlink()
        tor_paths = set(
            evidence_paths("sync-tree-route-private-actual-tor-payload", source)
        )
        require("client.tox-tor.pcapng" in tor_paths, "actual-Tor client capture omitted")
        require("device.tox-tor.pcapng" in tor_paths, "actual-Tor device capture omitted")
        require("client.tox-i2p.pcapng" not in tor_paths, "actual-Tor selected I2P evidence")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("proof_root", nargs="?", type=Path)
    parser.add_argument("output", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        require(args.proof_root is None and args.output is None, "self-test accepts no paths")
        self_test()
        print("sandwurm-pair exporter self-test: PASS")
        return 0
    require(args.proof_root is not None, "proof_root is required")
    output = args.output or EXPORT_ROOT / args.proof_root.name
    print(json.dumps(export(args.proof_root, output), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"pair evidence export refused: {error}", file=sys.stderr)
        raise SystemExit(1)
