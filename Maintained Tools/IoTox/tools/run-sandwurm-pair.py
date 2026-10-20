#!/usr/bin/env python3
"""Run one bounded, concurrent IoTox pair through Sandwurm."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import ipaddress
import json
import os
import re
import select
import shutil
import signal
import socket
import subprocess
import tempfile
import threading
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SANDWURM_ROOT = Path(
    os.environ.get("IOTOX_SANDWURM_ROOT", str(ROOT.parent / "sandwurm"))
).resolve()
STATE_ROOT = Path(
    os.environ.get("IOTOX_SANDWURM_STATE_DIR", ROOT / ".sandwurm/lab")
).resolve()
KEY_CACHE = Path(
    os.environ.get(
        "IOTOX_REAL_PEER_KEY_CACHE",
        ROOT / ".cache/real-peer-keys/c-toxcore-0.2.23",
    )
).resolve()
FOUR_ROUTE_KEY_CACHE = Path(
    os.environ.get(
        "IOTOX_FOUR_ROUTE_KEY_CACHE",
        ROOT / ".cache/four-route-lab/c-toxcore-0.2.23",
    )
).resolve()
HOST_BIN = Path("/run/current-system/sw/bin")
HOST_BRIDGE = "sandwurm-vm"
HOST_BRIDGE_ADDRESS = "10.0.0.1"
HOST_BRIDGE_PREFIX = 24
BOOTSTRAP_PORT = 33445
SOCKS5_PORT = 39050
I2P_SOCKS5_PORT = 39053
I2P_SERVER_SAM_PORT = 37656
I2P_CLIENT_SAM_PORT = 47656
ACTUAL_TOR_SOCKS_PORTS = {"client": 39051, "device": 39052}
ACTUAL_TOR_UPSTREAM_SOCKS_PORTS = {"client": 39151, "device": 39152}
TOR_APPLICATION_CIRCUIT_PURPOSES = {"GENERAL", "CONFLUX_LINKED"}
I2P_ROUTES = {"tox-i2p", "tox-i2p-construction"}
PACKET_LOSS_PERCENT = 5
PACKET_LOSS_PROBE_COUNT = 128
PACKET_LOSS_SEEDS = {
    "vm-iotoxc": 20_260_824,
    "vm-iotoxd": 20_260_825,
}
RATOX_IMPAIRMENT_SAMPLES = 120
RATOX_IMPAIRMENT_BASELINE_END = 20
RATOX_IMPAIRMENT_END = 100
RATOX_IMPAIRMENT_DELAY_MS = 75
RATOX_IMPAIRMENT_JITTER_MS = 15
RATOX_IMPAIRMENT_LOSS_PERCENT = 2
RATOX_IMPAIRMENT_SEEDS = {
    "vm-iotoxc": 20_260_827,
    "vm-iotoxd": 20_260_828,
}
RATOX_ROUTE_LOSS_SEEDS = {
    "vm-iotoxc": 20_260_829,
    "vm-iotoxd": 20_260_830,
}
RATOX_ACTUAL_TOR_SOAK_SAMPLES = 120
RATOX_ACTUAL_TOR_SOAK_INTERVAL_MS = 1000
RATOX_ACTUAL_TOR_SOAK_CHURNS = (("client", 20), ("device", 100))
SANDWURM_BIN = Path(
    os.environ.get("SANDWURM_BIN", HOST_BIN / "sandwurm")
).resolve()
RUNNER_RECEIPT = Path(
    "/var/lib/sandwurm-direct-cloud-hypervisor/runner-authority-declaration.json"
)
ADDRESS_PATTERN = re.compile(r"[0-9A-Fa-f]{76}\n?")
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
POST_SYNC_RATOX_SCENARIOS = {
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
    *RATOX_BULK_SCENARIOS,
    *POST_SYNC_RATOX_SCENARIOS,
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
    # treepack-v1 framing: 16-byte header + six 20-byte entry headers +
    # 56 path bytes + 4 MiB payload + 85 small-file bytes + 20-byte end.
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
CONTENT_MULTI_SOURCE_LOSS_SCENARIOS = {
    "sync-content-multi-route-actual-tor-loss",
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


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def expected_network(route: str) -> str:
    if route == "tox-tor":
        return "Tox/Tor"
    if route == "tox-i2p":
        return "Tox/I2P"
    if route == "tox-i2p-construction":
        return "Tox/I2P-construction"
    return "Tox/native"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def actual_tor_payload_summary(
    pair_root: Path, receipt_entries: dict[str, dict], enabled: bool
) -> dict:
    """Aggregate payload attribution from the indexed signed guest receipts."""
    if not enabled:
        return {
            "actual_tor_payload_observed_role_count": 0,
            "actual_tor_payload_carrier_sha256": "",
            "actual_tor_payload_reassignments": 0,
        }
    role_receipts = {
        role: load(pair_root / receipt_entries[role]["path"])
        for role in ("client", "device")
    }
    return {
        "actual_tor_payload_observed_role_count": sum(
            int(role_receipts[role].get("actual_tor_payload_observed", False))
            for role in ("client", "device")
        ),
        "actual_tor_payload_carrier_sha256": role_receipts["client"].get(
            "actual_tor_payload_carrier_sha256", ""
        ),
        "actual_tor_payload_reassignments": role_receipts["client"].get(
            "actual_tor_payload_reassignments", 0
        ),
    }


def actual_i2p_payload_summary(
    pair_root: Path, receipt_entries: dict[str, dict], enabled: bool
) -> dict:
    """Aggregate I2P payload attribution from the indexed signed guest receipts."""
    if not enabled:
        return {
            "actual_i2p_payload_observed_role_count": 0,
            "actual_i2p_payload_carrier_sha256": "",
            "actual_i2p_payload_reassignments": 0,
        }
    role_receipts = {
        role: load(pair_root / receipt_entries[role]["path"])
        for role in ("client", "device")
    }
    return {
        "actual_i2p_payload_observed_role_count": sum(
            int(role_receipts[role].get("actual_i2p_payload_observed", False))
            for role in ("client", "device")
        ),
        "actual_i2p_payload_carrier_sha256": role_receipts["client"].get(
            "actual_i2p_payload_carrier_sha256", ""
        ),
        "actual_i2p_payload_reassignments": role_receipts["client"].get(
            "actual_i2p_payload_reassignments", 0
        ),
    }


def select_tor_application_stream(
    succeeded: list[tuple[str, str]],
    current_circuits: dict[str, list[str]],
    event_circuits: dict[str, list[str]],
) -> tuple[str, str, list[str]] | None:
    for stream_id, circuit_id in reversed(succeeded):
        fields = current_circuits.get(circuit_id) or event_circuits.get(circuit_id)
        if (
            fields is None
            or len(fields) < 3
            or fields[1] not in {"BUILT", "CLOSED"}
        ):
            continue
        purposes = [
            field.split("=", 1)[1]
            for field in fields[3:]
            if field.startswith("PURPOSE=")
        ]
        if (
            len(purposes) == 1
            and purposes[0] in TOR_APPLICATION_CIRCUIT_PURPOSES
            and len(fields[2].split(",")) >= 3
        ):
            return stream_id, circuit_id, fields
    return None


def self_test() -> None:
    require(
        CONTENT_MULTI_SOURCE_LOSS_SCENARIOS
        == {
            "sync-content-multi-route-actual-tor-loss",
            "sync-content-multi-source-loss",
        },
        "multi-source content-loss scenario set changed",
    )
    require(
        REPEATED_RANGE_LOSS_COUNTS
        == {
            "sync-file-range-repeated-route-loss": 2,
            "sync-file-range-triple-route-loss": 3,
        },
        "bounded repeated range-loss scenario counts changed",
    )
    with tempfile.TemporaryDirectory(prefix="iotox-pair-runner-selftest-") as raw:
        root = Path(raw)
        entries = {}
        carrier = "a" * 64
        for role, observed in (("client", True), ("device", False)):
            path = root / role / "pair.json"
            path.parent.mkdir(parents=True)
            path.write_text(
                json.dumps(
                    {
                        "actual_tor_payload_observed": observed,
                        "actual_tor_payload_carrier_sha256": (
                            carrier if role == "client" else ""
                        ),
                        "actual_tor_payload_reassignments": 0,
                    }
                ),
                encoding="utf-8",
            )
            # The production index deliberately does not duplicate payload fields.
            entries[role] = {
                "path": str(path.relative_to(root)),
                "sha256": "b" * 64,
            }
        require(
            actual_tor_payload_summary(root, entries, True)
            == {
                "actual_tor_payload_observed_role_count": 1,
                "actual_tor_payload_carrier_sha256": carrier,
                "actual_tor_payload_reassignments": 0,
            },
            "actual-Tor payload receipt aggregation failed",
        )
        require(
            actual_tor_payload_summary(root, entries, False)
            == {
                "actual_tor_payload_observed_role_count": 0,
                "actual_tor_payload_carrier_sha256": "",
                "actual_tor_payload_reassignments": 0,
            },
            "disabled actual-Tor payload aggregation failed",
        )
        for role, observed in (("client", True), ("device", False)):
            path = root / entries[role]["path"]
            receipt = load(path)
            receipt.update(
                {
                    "actual_i2p_payload_observed": observed,
                    "actual_i2p_payload_carrier_sha256": (
                        carrier if role == "client" else ""
                    ),
                    "actual_i2p_payload_reassignments": 0,
                }
            )
            path.write_text(json.dumps(receipt), encoding="utf-8")
        require(
            actual_i2p_payload_summary(root, entries, True)
            == {
                "actual_i2p_payload_observed_role_count": 1,
                "actual_i2p_payload_carrier_sha256": carrier,
                "actual_i2p_payload_reassignments": 0,
            },
            "actual-I2P payload receipt aggregation failed",
        )
        selected = select_tor_application_stream(
            [("valid-stream", "7"), ("irrelevant-stream", "8")],
            {
                "7": [
                    "7",
                    "CLOSED",
                    "$A~a,$B~b,$C~c",
                    "PURPOSE=CONFLUX_LINKED",
                ],
                "8": [
                    "8",
                    "BUILT",
                    "$D~d,$E~e,$F~f",
                    "PURPOSE=HS_VANGUARDS",
                ],
            },
            {},
        )
        require(
            selected is not None and selected[:2] == ("valid-stream", "7"),
            "actual-Tor application stream selection accepted irrelevant circuit state",
        )
    print("sandwurm-pair runner self-test: PASS")


def sudo(*arguments: str, capture: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["sudo", "-n", *arguments],
        check=True,
        text=True,
        capture_output=capture,
    )


def deliver_guest_input(
    pair_root: Path, workspace: Path, role: str, name: str
) -> None:
    command_file = pair_root / f"{role}.{name}"
    command_file.write_text(f"{name}=1\n", encoding="ascii")
    sudo(
        "install",
        "-m",
        "0600",
        str(command_file),
        str(workspace / f"iotox-input/{name}"),
    )
    command_file.unlink()


def netem_observation(tap: str) -> dict:
    result = sudo(
        str(HOST_BIN / "tc"),
        "-j",
        "-s",
        "qdisc",
        "show",
        "dev",
        tap,
        capture=True,
    )
    qdiscs = json.loads(result.stdout)
    require(isinstance(qdiscs, list) and len(qdiscs) == 1, f"ambiguous qdisc on {tap}")
    qdisc = qdiscs[0]
    require(qdisc.get("kind") == "netem" and qdisc.get("root") is True, f"netem is absent on {tap}")
    counters = {}
    for key in ("bytes", "packets", "drops", "overlimits", "requeues", "backlog", "qlen"):
        value = qdisc.get(key)
        require(isinstance(value, int) and value >= 0, f"invalid {key} counter on {tap}")
        counters[key] = value
    return {
        "tap": tap,
        "kind": "netem",
        "loss_percent": PACKET_LOSS_PERCENT,
        "seed": PACKET_LOSS_SEEDS[tap],
        **counters,
    }


def common_link_fairness_observation(tap: str) -> dict:
    qdisc_result = sudo(
        str(HOST_BIN / "tc"),
        "-j",
        "-s",
        "qdisc",
        "show",
        "dev",
        tap,
        capture=True,
    )
    qdiscs = json.loads(qdisc_result.stdout)
    require(isinstance(qdiscs, list) and len(qdiscs) == 2,
            f"ambiguous common-link hierarchy on {tap}")
    by_kind = {qdisc.get("kind"): qdisc for qdisc in qdiscs}
    require(set(by_kind) == {"htb", "fq_codel"},
            f"common-link hierarchy is incomplete on {tap}")
    htb = by_kind["htb"]
    fair = by_kind["fq_codel"]
    require(
        htb.get("root") is True
        and htb.get("handle") == "1:"
        and htb.get("options", {}).get("default") == "0x1",
        f"common-link HTB root is invalid on {tap}",
    )
    require(
        fair.get("handle") == "10:"
        and fair.get("parent") == "1:1"
        and fair.get("options", {}).get("limit") == 1000,
        f"common-link fq_codel leaf is invalid on {tap}",
    )
    class_result = sudo(
        str(HOST_BIN / "tc"),
        "-j",
        "-s",
        "class",
        "show",
        "dev",
        tap,
        capture=True,
    )
    classes = json.loads(class_result.stdout)
    require(isinstance(classes, list),
            f"common-link classes are not a list on {tap}")
    link_classes = [
        entry
        for entry in classes
        if entry.get("class") == "htb" and entry.get("handle") == "1:1"
    ]
    leaf_flows = [
        entry
        for entry in classes
        if entry.get("class") == "fq_codel" and entry.get("parent") == "10:"
    ]
    require(len(link_classes) == 1,
            f"ambiguous common-link HTB class on {tap}")
    require(len(link_classes) + len(leaf_flows) == len(classes),
            f"unexpected common-link class kind on {tap}")
    link_class = link_classes[0]
    require(
        link_class.get("class") == "htb"
        and link_class.get("handle") == "1:1"
        and link_class.get("rate") == 500_000
        and link_class.get("ceil") == 500_000,
        f"common-link 4 Mbit/s class is invalid on {tap}",
    )
    leaf_counters = {}
    class_stats = link_class.get("stats", {})
    for key in ("bytes", "packets", "drops", "overlimits", "requeues"):
        leaf_value = fair.get(key)
        class_value = class_stats.get(key)
        require(isinstance(leaf_value, int) and leaf_value >= 0,
                f"invalid fq_codel {key} counter on {tap}")
        require(isinstance(class_value, int) and class_value >= 0,
                f"invalid HTB {key} counter on {tap}")
        leaf_counters[f"fq_codel_{key}"] = leaf_value
        leaf_counters[f"htb_{key}"] = class_value
    require(
        leaf_counters["fq_codel_bytes"] > 0
        and leaf_counters["fq_codel_packets"] > 0
        and leaf_counters["htb_bytes"] > 0
        and leaf_counters["htb_packets"] > 0,
        f"common-link hierarchy carried no traffic on {tap}",
    )
    return {
        "schema": "iotox-common-link-fairness-v1",
        "tap": tap,
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
        "active_leaf_flow_count": len(leaf_flows),
        **leaf_counters,
    }


def ratox_impairment_observation(tap: str) -> dict:
    result = sudo(
        str(HOST_BIN / "tc"),
        "-j",
        "-s",
        "qdisc",
        "show",
        "dev",
        tap,
        capture=True,
    )
    qdiscs = json.loads(result.stdout)
    require(isinstance(qdiscs, list) and len(qdiscs) == 1,
            f"ambiguous Ratox impairment qdisc on {tap}")
    qdisc = qdiscs[0]
    require(qdisc.get("kind") == "netem" and qdisc.get("root") is True,
            f"Ratox impairment netem is absent on {tap}")
    counters = {}
    for key in ("bytes", "packets", "drops", "overlimits", "requeues", "backlog", "qlen"):
        value = qdisc.get(key)
        require(isinstance(value, int) and value >= 0,
                f"invalid Ratox impairment {key} counter on {tap}")
        counters[key] = value
    return {
        "tap": tap,
        "kind": "netem",
        "delay_ms": RATOX_IMPAIRMENT_DELAY_MS,
        "jitter_ms": RATOX_IMPAIRMENT_JITTER_MS,
        "loss_percent": RATOX_IMPAIRMENT_LOSS_PERCENT,
        "seed": RATOX_IMPAIRMENT_SEEDS[tap],
        **counters,
    }


def ratox_route_loss_observation(tap: str, seed_offset: int = 0) -> dict:
    result = sudo(
        str(HOST_BIN / "tc"),
        "-j",
        "-s",
        "qdisc",
        "show",
        "dev",
        tap,
        capture=True,
    )
    qdiscs = json.loads(result.stdout)
    require(isinstance(qdiscs, list) and len(qdiscs) == 1,
            f"ambiguous Ratox route-loss qdisc on {tap}")
    qdisc = qdiscs[0]
    require(qdisc.get("kind") == "netem" and qdisc.get("root") is True,
            f"Ratox route-loss netem is absent on {tap}")
    counters = {}
    for key in ("bytes", "packets", "drops", "overlimits", "requeues", "backlog", "qlen"):
        value = qdisc.get(key)
        require(isinstance(value, int) and value >= 0,
                f"invalid Ratox route-loss {key} counter on {tap}")
        counters[key] = value
    return {
        "tap": tap,
        "kind": "netem",
        "loss_percent": 100,
        "seed": RATOX_ROUTE_LOSS_SEEDS[tap] + seed_offset,
        **counters,
    }


def ratox_progress_samples(path: Path) -> int:
    if not root_file_exists(path):
        return 0
    fields = {}
    for line in read_root_file(path).splitlines():
        parts = line.split("\t")
        require(len(parts) == 2 and parts[0] not in fields,
                "Ratox progress record is not canonical")
        fields[parts[0]] = parts[1]
    require(fields.get("schema") == "iotox-ratox-terminal-progress-v1",
            "Ratox progress schema drifted")
    completed = fields.get("samples-completed", "")
    require(completed.isdigit(), "Ratox progress count is not decimal")
    return int(completed)


def ensure_host_bridge() -> None:
    """Restore and prove the prepared bridge address before starting fixtures."""
    ip = str(HOST_BIN / "ip")
    sudo(ip, "link", "set", "dev", HOST_BRIDGE, "up")
    sudo(
        ip,
        "address",
        "replace",
        f"{HOST_BRIDGE_ADDRESS}/{HOST_BRIDGE_PREFIX}",
        "dev",
        HOST_BRIDGE,
    )
    result = sudo(
        ip,
        "-j",
        "-4",
        "address",
        "show",
        "dev",
        HOST_BRIDGE,
        capture=True,
    )
    links = json.loads(result.stdout)
    require(
        isinstance(links, list) and len(links) == 1,
        f"prepared host bridge is absent: {HOST_BRIDGE}",
    )
    addresses = links[0].get("addr_info", [])
    require(
        any(
            address.get("local") == HOST_BRIDGE_ADDRESS
            and address.get("prefixlen") == HOST_BRIDGE_PREFIX
            and address.get("scope") == "global"
            for address in addresses
        ),
        "prepared host bridge address was not restored exactly",
    )


def tcp_port_open(address: str, port: int) -> bool:
    try:
        with socket.create_connection((address, port), timeout=0.25):
            return True
    except OSError:
        return False


def socks5_connect_probe(
    proxy: tuple[str, int], target: tuple[str, int]
) -> None:
    """Require one numeric IPv4 SOCKS CONNECT without exchanging payload."""
    with socket.create_connection(proxy, timeout=15) as stream:
        stream.settimeout(15)
        stream.sendall(b"\x05\x01\x00")
        require(stream.recv(2) == b"\x05\x00", "SOCKS5 probe greeting failed")
        address = socket.inet_pton(socket.AF_INET, target[0])
        stream.sendall(
            b"\x05\x01\x00\x01" + address + target[1].to_bytes(2, "big")
        )
        header = b""
        while len(header) < 4:
            chunk = stream.recv(4 - len(header))
            require(bool(chunk), "SOCKS5 probe reply ended early")
            header += chunk
        require(
            header[:3] == b"\x05\x00\x00",
            f"SOCKS5 probe CONNECT failed with reply {header.hex()}",
        )
        address_bytes = {1: 4, 4: 16}.get(header[3])
        if header[3] == 3:
            length = stream.recv(1)
            require(len(length) == 1, "SOCKS5 probe domain reply ended early")
            address_bytes = length[0]
        require(address_bytes is not None, "SOCKS5 probe reply address type drifted")
        remaining = address_bytes + 2
        while remaining:
            chunk = stream.recv(remaining)
            require(bool(chunk), "SOCKS5 probe bound endpoint ended early")
            remaining -= len(chunk)


def require_bootstrap_ready(process: subprocess.Popen) -> None:
    wait_for(
        lambda: process.poll() is not None
        or tcp_port_open(HOST_BRIDGE_ADDRESS, BOOTSTRAP_PORT),
        10,
        "host bridge bootstrap TCP listener",
    )
    require(process.poll() is None, "host bridge bootstrap exited")
    require(
        tcp_port_open(HOST_BRIDGE_ADDRESS, BOOTSTRAP_PORT),
        "host bridge bootstrap TCP listener is unavailable",
    )


def start_socks5_forwarder(pair_root: Path, phase: str) -> subprocess.Popen:
    process = subprocess.Popen(
        [
            os.sys.executable,
            str(ROOT / "tools/run-socks5-forwarder.py"),
            "--listen",
            f"{HOST_BRIDGE_ADDRESS}:{SOCKS5_PORT}",
            "--allow-target",
            f"{HOST_BRIDGE_ADDRESS}:{BOOTSTRAP_PORT}",
            "--audit",
            str(pair_root / f"socks5-{phase}-audit.jsonl"),
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    require(process.stdout is not None, "SOCKS5 forwarder stdout is absent")
    ready = process.stdout.readline().strip()
    require(
        ready == f"ready={HOST_BRIDGE_ADDRESS}:{SOCKS5_PORT}",
        f"SOCKS5 forwarder did not bind the frozen endpoint: {ready}",
    )
    require(process.poll() is None, "SOCKS5 forwarder exited after readiness")
    return process


def realize_i2p_lab() -> tuple[Path, Path]:
    result = subprocess.run(
        [
            "nix",
            "build",
            "--no-link",
            "--print-out-paths",
            f"git+file:{ROOT}#iotox-i2pd-lab",
            f"git+file:{ROOT}#iotox-i2pd-source",
        ],
        check=True,
        text=True,
        capture_output=True,
        timeout=600,
    )
    paths = [Path(line) for line in result.stdout.splitlines() if line]
    binaries = [path / "bin/i2pd" for path in paths if (path / "bin/i2pd").is_file()]
    sources = [path for path in paths if (path / "libi2pd").is_dir()]
    require(len(binaries) == 1, "I2P router realization was ambiguous")
    require(len(sources) == 1, "I2P router source realization was ambiguous")
    return binaries[0], sources[0]


def start_i2p_fronts(pair_root: Path, nodes: list[dict[str, object]]) -> dict[str, object]:
    router_binary, router_source = realize_i2p_lab()
    socat = shutil.which("socat")
    require(socat is not None, "socat is required for exact I2P Tox egress shims")
    root = pair_root / "i2p-fronts"
    root.mkdir(mode=0o700)
    stderr = (pair_root / "i2p-fronts.stderr").open("w", encoding="utf-8")
    command = [
        os.sys.executable,
        str(ROOT / "tools/run-i2p-tox-fronts.py"),
        "--work-root",
        str(root),
        "--router-binary",
        str(router_binary),
        "--router-source",
        str(router_source),
        "--socat",
        socat,
        "--listen",
        f"{HOST_BRIDGE_ADDRESS}:{I2P_SOCKS5_PORT}",
        "--server-sam",
        f"127.0.0.1:{I2P_SERVER_SAM_PORT}",
        "--client-sam",
        f"127.0.0.1:{I2P_CLIENT_SAM_PORT}",
        "--startup-timeout",
        "840",
        "--command-timeout",
        "180",
    ]
    for node in nodes:
        command.extend(("--node", str(node["record"])))
    process = subprocess.Popen(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=stderr,
        start_new_session=True,
    )
    require(process.stdout is not None, "I2P topology stdout is unavailable")
    readable, _, _ = select.select([process.stdout], [], [], 900.0)
    require(bool(readable), "I2P topology did not report readiness")
    line = process.stdout.readline().strip()
    if not line.startswith("ready="):
        returncode = process.poll()
        detail = (
            f"I2P topology exited before readiness with status {returncode}; "
            f"inspect {pair_root / 'i2p-fronts.stderr'}"
            if returncode is not None
            else f"I2P topology readiness drifted: {line}"
        )
        raise RuntimeError(detail)
    ready = json.loads(line.removeprefix("ready="))
    require(
        isinstance(ready, dict)
        and ready.get("schema") == "iotox.i2p-tox-fronts.v1"
        and ready.get("status") == "ready"
        and ready.get("proxy_endpoint") == f"{HOST_BRIDGE_ADDRESS}:{I2P_SOCKS5_PORT}"
        and ready.get("nodes") == [node["record"] for node in nodes]
        and ready.get("front_count") == 3
        and process.poll() is None,
        "I2P topology ready record is invalid",
    )
    return {"process": process, "stderr": stderr, "root": root, "ready": ready}


def stop_i2p_fronts(instance: dict[str, object]) -> dict[str, object]:
    process = instance["process"]
    require(isinstance(process, subprocess.Popen), "I2P topology process is invalid")
    require(process.poll() is None, "I2P topology exited before bounded shutdown")
    os.killpg(process.pid, signal.SIGTERM)
    try:
        output, _ = process.communicate(timeout=30.0)
    except subprocess.TimeoutExpired as error:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait(timeout=5.0)
        raise RuntimeError("I2P topology did not stop cleanly") from error
    stderr = instance["stderr"]
    require(hasattr(stderr, "close"), "I2P topology stderr handle is invalid")
    stderr.close()
    (Path(instance["root"]).parent / "i2p-fronts.stdout").write_text(
        output, encoding="utf-8"
    )
    require(process.returncode == 0, "I2P topology failed during bounded shutdown")
    final = load(Path(instance["root"]) / "topology-final.json")
    require(
        final.get("schema") == "iotox.i2p-tox-fronts.v1"
        and final.get("status") == "passed"
        and final.get("front_count") == 3,
        "I2P topology final receipt is invalid",
    )
    return final


def stop_socks5_forwarder(
    process: subprocess.Popen, pair_root: Path, phase: str
) -> None:
    terminate({"socks5": process})
    output, errors = process.communicate(timeout=5)
    (pair_root / f"socks5-{phase}.stdout").write_text(output, encoding="utf-8")
    (pair_root / f"socks5-{phase}.stderr").write_text(errors, encoding="utf-8")
    require(process.returncode == 0, f"SOCKS5 {phase} forwarder failed: {errors}")


def parse_public_tox_node(text: str, route_label: str) -> dict[str, object]:
    fields = text.rsplit(":", 2)
    require(len(fields) == 3, f"{route_label} node must use IPv4:PORT:KEY")
    address = ipaddress.ip_address(fields[0])
    require(
        address.version == 4 and address.is_global,
        f"{route_label} node address must be public IPv4",
    )
    require(fields[1].isascii() and fields[1].isdecimal(), f"invalid {route_label} node port")
    port = int(fields[1])
    require(1 <= port <= 65535, f"{route_label} node port is out of range")
    public_key = fields[2].upper()
    require(
        re.fullmatch(r"[0-9A-F]{64}", public_key) is not None,
        f"{route_label} node key is not 64 hexadecimal characters",
    )
    return {
        "address": address.compressed,
        "port": port,
        "public_key": public_key,
        "record": f"{address.compressed}:{port}:{public_key}",
        "target": f"{address.compressed}:{port}",
    }


def parse_actual_tor_node(text: str) -> dict[str, object]:
    return parse_public_tox_node(text, "actual-Tor")


class TorStreamObserver:
    def __init__(self, root: Path):
        self.root = root
        self.control: socket.socket | None = None
        self.buffer = b""
        self.events: list[str] = []
        self.failure: str | None = None
        self.stopping = threading.Event()
        self.thread: threading.Thread | None = None

    def _readline(self) -> str:
        require(self.control is not None, "Tor observer control socket is absent")
        while b"\r\n" not in self.buffer:
            chunk = self.control.recv(65536)
            require(chunk, "Tor observer control socket closed")
            self.buffer += chunk
        raw, self.buffer = self.buffer.split(b"\r\n", 1)
        return raw.decode("ascii", errors="strict")

    def _command(self, command: str) -> None:
        require(self.control is not None, "Tor observer control socket is absent")
        self.control.sendall(command.encode("ascii") + b"\r\n")
        response = self._readline()
        require(response == "250 OK", f"Tor rejected {command}: {response}")

    def start(self) -> None:
        cookie = (self.root / "control.authcookie").read_bytes()
        require(len(cookie) == 32, "Tor observer cookie is not 32 bytes")
        control = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        control.settimeout(5)
        control.connect(str(self.root / "control.sock"))
        self.control = control
        self._command(f"AUTHENTICATE {cookie.hex()}")
        self._command("USEFEATURE EXTENDED_EVENTS")
        self._command("SETEVENTS STREAM CIRC")
        control.settimeout(0.5)
        self.thread = threading.Thread(
            target=self._observe,
            name=f"iotox-tor-observer-{self.root.name}",
            daemon=True,
        )
        self.thread.start()

    def _observe(self) -> None:
        try:
            while not self.stopping.is_set():
                try:
                    line = self._readline()
                except TimeoutError:
                    continue
                if line.startswith("650 "):
                    self.events.append(line)
        except (OSError, UnicodeError, RuntimeError) as error:
            if not self.stopping.is_set():
                self.failure = str(error)

    def stop(self) -> list[str]:
        self.stopping.set()
        if self.control is not None:
            try:
                self.control.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self.control.close()
        if self.thread is not None:
            self.thread.join(timeout=5)
            require(not self.thread.is_alive(), "Tor observer thread did not stop")
        require(self.failure is None, f"Tor observer failed: {self.failure}")
        return list(self.events)


def pair_tor_configuration(
    root: Path, role: str, adversarial_boundary: bool = False
) -> tuple[list[str], list[str]]:
    source = (
        "127.0.0.1"
        if adversarial_boundary
        else "10.0.0.11"
        if role == "client"
        else "10.0.0.12"
    )
    address = "127.0.0.1" if adversarial_boundary else HOST_BRIDGE_ADDRESS
    port = (
        ACTUAL_TOR_UPSTREAM_SOCKS_PORTS[role]
        if adversarial_boundary
        else ACTUAL_TOR_SOCKS_PORTS[role]
    )
    rendered = [
        "AvoidDiskWrites 1",
        "ClientOnly 1",
        "ClientUseIPv6 0",
        "CookieAuthentication 1",
        f"CookieAuthFile {root / 'control.authcookie'}",
        f"ControlSocket {root / 'control.sock'}",
        f"DataDirectory {root / 'tor-data'}",
        "SafeSocks 0",
        f"SocksPolicy accept {source}",
        "SocksPolicy reject *",
        f"SocksPort {address}:{port}",
    ]
    normalized = [line.replace(str(root), "<TOR_ROOT>") for line in rendered]
    return rendered, normalized


def start_pair_tor(
    pair_root: Path,
    role: str,
    phase: str = "continuous",
    adversarial_boundary: bool = False,
) -> dict[str, object]:
    root = pair_root / f"tor-{role}"
    root.mkdir(mode=0o700, exist_ok=True)
    (root / "tor-data").mkdir(mode=0o700, exist_ok=True)
    control_socket = root / "control.sock"
    require(
        not control_socket.exists(),
        f"{role} Tor control socket survived before {phase} start",
    )
    rendered, normalized = pair_tor_configuration(
        root, role, adversarial_boundary
    )
    torrc = root / "torrc"
    torrc.write_text("\n".join(rendered) + "\n", encoding="ascii")
    torrc.chmod(0o600)
    log_path = root / (
        "tor.log" if phase == "continuous" else f"tor-{phase}.log"
    )
    log = log_path.open("wb")
    tor_binary = (HOST_BIN / "tor").resolve(strict=True)
    tor_version = subprocess.run(
        [str(tor_binary), "--version"],
        check=True,
        text=True,
        capture_output=True,
        timeout=10,
    ).stdout.strip()
    process = subprocess.Popen(
        [str(tor_binary), "--defaults-torrc", "/dev/null", "-f", str(torrc)],
        cwd=root,
        stdout=log,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    socks_address = "127.0.0.1" if adversarial_boundary else HOST_BRIDGE_ADDRESS
    port = (
        ACTUAL_TOR_UPSTREAM_SOCKS_PORTS[role]
        if adversarial_boundary
        else ACTUAL_TOR_SOCKS_PORTS[role]
    )

    def ready() -> bool:
        if process.poll() is not None:
            return True
        try:
            tail = log_path.read_bytes()[-32768:]
        except FileNotFoundError:
            return False
        return (
            b"Bootstrapped 100% (done): Done" in tail
            and (root / "control.sock").is_socket()
            and (root / "control.authcookie").is_file()
            and tcp_port_open(socks_address, port)
        )

    try:
        wait_for(ready, 180, f"{role} Tor bootstrap")
        require(process.poll() is None, f"{role} Tor exited during bootstrap")
    except Exception as error:
        terminate({role: process})
        log.close()
        try:
            diagnostic = log_path.read_text(encoding="utf-8", errors="replace")[-4096:]
        except FileNotFoundError:
            diagnostic = ""
        raise RuntimeError(
            f"{role} Tor bootstrap failed: {error}: {diagnostic}"
        ) from error
    observer = TorStreamObserver(root)
    observer.start()
    return {
        "role": role,
        "phase": phase,
        "root": root,
        "process": process,
        "log": log,
        "observer": observer,
        "configuration": normalized,
        "configuration_sha256": hashlib.sha256(
            ("\n".join(normalized) + "\n").encode("ascii")
        ).hexdigest(),
        "socks_endpoint": f"{socks_address}:{port}",
        "expected_source_address": (
            "127.0.0.1"
            if adversarial_boundary
            else "10.0.0.11"
            if role == "client"
            else "10.0.0.12"
        ),
        "adversarial_boundary": adversarial_boundary,
        "tor_binary_path": str(tor_binary),
        "tor_sha256": sha256(tor_binary),
        "tor_version": tor_version,
    }


def start_actual_tor_adversary(
    pair_root: Path, role: str, node: dict[str, object]
) -> dict[str, object]:
    hold_path = pair_root / f"actual-tor-{role}.hold"
    audit_path = pair_root / f"actual-tor-{role}-adversary-audit.jsonl"
    stdout_path = pair_root / f"actual-tor-{role}-adversary.stdout"
    stderr_path = pair_root / f"actual-tor-{role}-adversary.stderr"
    process = subprocess.Popen(
        [
            os.sys.executable,
            str(ROOT / "tools/run-socks5-adversary.py"),
            "--listen",
            f"{HOST_BRIDGE_ADDRESS}:{ACTUAL_TOR_SOCKS_PORTS[role]}",
            "--allow-target",
            str(node["target"]),
            "--upstream-socks",
            f"127.0.0.1:{ACTUAL_TOR_UPSTREAM_SOCKS_PORTS[role]}",
            "--hold-file",
            str(hold_path),
            "--audit",
            str(audit_path),
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    require(process.stdout is not None, f"{role} adversary stdout is absent")
    ready = process.stdout.readline().strip()
    require(
        ready == f"ready={HOST_BRIDGE_ADDRESS}:{ACTUAL_TOR_SOCKS_PORTS[role]}",
        f"{role} adversary did not bind its frozen endpoint: {ready}",
    )
    require(process.poll() is None, f"{role} adversary exited after readiness")
    listeners = [
        record
        for record in process_inet_sockets(process.pid, "tcp")
        if record["local_address"] == HOST_BRIDGE_ADDRESS
        and record["local_port"] == ACTUAL_TOR_SOCKS_PORTS[role]
        and record["state"] == "0A"
    ]
    require(len(listeners) == 1, f"{role} adversary listener ownership is ambiguous")
    return {
        "role": role,
        "process": process,
        "process_pid": process.pid,
        "listener_inode": listeners[0]["inode"],
        "hold_path": hold_path,
        "audit_path": audit_path,
        "stdout_path": stdout_path,
        "stderr_path": stderr_path,
        "listen_endpoint": f"{HOST_BRIDGE_ADDRESS}:{ACTUAL_TOR_SOCKS_PORTS[role]}",
        "upstream_endpoint": f"127.0.0.1:{ACTUAL_TOR_UPSTREAM_SOCKS_PORTS[role]}",
    }


def stop_actual_tor_adversary(instance: dict[str, object]) -> None:
    process = instance["process"]
    require(isinstance(process, subprocess.Popen), "adversary process type drifted")
    terminate({str(instance["role"]): process})
    output, errors = process.communicate(timeout=5)
    Path(instance["stdout_path"]).write_text(output, encoding="utf-8")
    Path(instance["stderr_path"]).write_text(errors, encoding="utf-8")
    require(process.returncode == 0, f"adversary failed: {errors}")


def tor_getinfo(root: Path, key: str) -> str:
    cookie = (root / "control.authcookie").read_bytes()
    require(len(cookie) == 32, "Tor control cookie is not 32 bytes")
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as control:
        control.settimeout(5)
        control.connect(str(root / "control.sock"))
        stream = control.makefile("rwb", buffering=0)
        stream.write(f"AUTHENTICATE {cookie.hex()}\r\n".encode("ascii"))
        require(
            stream.readline().decode("ascii").rstrip("\r\n") == "250 OK",
            "Tor control authentication failed",
        )
        stream.write(f"GETINFO {key}\r\n".encode("ascii"))
        first = stream.readline().decode("ascii").rstrip("\r\n")
        require(
            first.startswith((f"250-{key}=", f"250+{key}=")),
            f"unexpected Tor GETINFO {key} response: {first}",
        )
        if first.startswith(f"250-{key}="):
            value = first.split("=", 1)[1]
            require(
                stream.readline().decode("ascii").rstrip("\r\n") == "250 OK",
                f"Tor GETINFO {key} omitted success",
            )
            return value
        lines: list[str] = []
        while True:
            line = stream.readline().decode("ascii").rstrip("\r\n")
            require(line != "", f"Tor GETINFO {key} ended early")
            if line == ".":
                break
            lines.append(line[1:] if line.startswith("..") else line)
        require(
            stream.readline().decode("ascii").rstrip("\r\n") == "250 OK",
            f"Tor GETINFO {key} omitted success",
        )
        return "\n".join(lines)


def tor_control_ok(root: Path, command: str) -> None:
    require(
        re.fullmatch(r"CLOSECIRCUIT [1-9][0-9]*", command) is not None,
        "Tor mutation command escaped the bounded circuit-close grammar",
    )
    cookie = (root / "control.authcookie").read_bytes()
    require(len(cookie) == 32, "Tor control cookie is not 32 bytes")
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as control:
        control.settimeout(5)
        control.connect(str(root / "control.sock"))
        stream = control.makefile("rwb", buffering=0)
        stream.write(f"AUTHENTICATE {cookie.hex()}\r\n".encode("ascii"))
        require(
            stream.readline().decode("ascii").rstrip("\r\n") == "250 OK",
            "Tor control authentication failed",
        )
        stream.write(command.encode("ascii") + b"\r\n")
        require(
            stream.readline().decode("ascii").rstrip("\r\n") == "250 OK",
            f"Tor rejected bounded mutation command {command}",
        )


def active_tor_guest_stream(
    instance: dict[str, object], node: dict[str, object]
) -> dict[str, object] | None:
    role = str(instance["role"])
    root = Path(instance["root"])
    observer = instance["observer"]
    require(isinstance(observer, TorStreamObserver), "Tor observer type drifted")
    expected_source = "10.0.0.11" if role == "client" else "10.0.0.12"
    expected_target = str(node["target"])
    source_streams: set[str] = set()
    for line in list(observer.events):
        fields = line.split()
        if len(fields) < 6 or fields[:2] != ["650", "STREAM"]:
            continue
        stream_id, state, _, target = fields[2:6]
        if state == "NEW":
            source_fields = [
                field.split("=", 1)[1]
                for field in fields[6:]
                if field.startswith("SOURCE_ADDR=")
            ]
            if len(source_fields) == 1:
                source_host, _, _ = source_fields[0].rpartition(":")
                if source_host == expected_source:
                    require(
                        target == expected_target,
                        f"{role} Tor churn observed an unexpected target {target}",
                    )
                    source_streams.add(stream_id)
    stream_status = tor_getinfo(root, "stream-status")
    circuit_status = tor_getinfo(root, "circuit-status")
    stream_states: list[tuple[str, str, str]] = []
    for line in stream_status.splitlines():
        fields = line.split()
        if len(fields) >= 4:
            stream_states.append((fields[0], fields[1], fields[2]))
            if fields[0] in source_streams:
                require(
                    fields[3] == expected_target,
                    f"{role} active Tor guest stream changed target",
                )
    circuits: dict[str, list[str]] = {}
    for line in circuit_status.splitlines():
        fields = line.split()
        if len(fields) >= 3 and fields[1] == "BUILT":
            circuits[fields[0]] = fields
    for stream_id, state, circuit_id in reversed(stream_states):
        if stream_id not in source_streams or state != "SUCCEEDED":
            continue
        circuit = circuits.get(circuit_id)
        if circuit is None or len(circuit) < 3 or circuit[1] != "BUILT":
            continue
        path = circuit[2]
        purposes = [
            field.split("=", 1)[1]
            for field in circuit[3:]
            if field.startswith("PURPOSE=")
        ]
        if not (
            len(purposes) == 1
            and purposes[0] in TOR_APPLICATION_CIRCUIT_PURPOSES
            and len(path.split(",")) >= 3
        ):
            continue
        return {
            "stream_id": stream_id,
            "circuit_id": circuit_id,
            "stream_id_sha256": hashlib.sha256(
                stream_id.encode("ascii")
            ).hexdigest(),
            "circuit_id_sha256": hashlib.sha256(
                circuit_id.encode("ascii")
            ).hexdigest(),
            "circuit_path_sha256": hashlib.sha256(
                path.encode("ascii")
            ).hexdigest(),
            "circuit_hop_count": len(path.split(",")),
            "circuit_purpose": purposes[0],
            "stream_status": stream_status,
            "circuit_status": circuit_status,
        }
    return None


def close_actual_tor_guest_circuit(
    instance: dict[str, object], node: dict[str, object], ordinal: int
) -> dict[str, object]:
    role = str(instance["role"])
    root = Path(instance["root"])
    process = instance["process"]
    observer = instance["observer"]
    require(isinstance(process, subprocess.Popen), "Tor process type drifted")
    require(isinstance(observer, TorStreamObserver), "Tor observer type drifted")
    before = active_tor_guest_stream(instance, node)
    require(before is not None, f"{role} Tor has no active guest stream before churn")
    process_pid = process.pid
    control_inode = (root / "control.sock").stat().st_ino
    started_ns = time.monotonic_ns()
    tor_control_ok(root, f"CLOSECIRCUIT {before['circuit_id']}")
    after: dict[str, object] | None = None
    requested_close = False

    def recovered() -> bool:
        nonlocal after, requested_close
        requested_close = any(
            (fields := line.split())[:4]
            == ["650", "CIRC", str(before["circuit_id"]), "CLOSED"]
            and "REASON=REQUESTED" in fields[4:]
            for line in list(observer.events)
        )
        candidate = active_tor_guest_stream(instance, node)
        if (
            requested_close
            and candidate is not None
            and candidate["circuit_id"] != before["circuit_id"]
        ):
            after = candidate
            return True
        return process.poll() is not None

    wait_for(recovered, 180, f"{role} Tor circuit churn recovery")
    require(process.poll() is None, f"{role} Tor exited during circuit churn")
    require(requested_close and after is not None, f"{role} Tor churn did not recover")
    completed_ns = time.monotonic_ns()
    require(
        process.pid == process_pid
        and (root / "control.sock").stat().st_ino == control_inode,
        f"{role} Tor process/control identity changed during circuit churn",
    )
    pair_root = root.parent
    for phase_name, phase in (("before", before), ("after", after)):
        for status_name in ("stream", "circuit"):
            status = str(phase[f"{status_name}_status"])
            status_path = (
                pair_root
                / f"tor-{role}-churn-{ordinal}-{phase_name}-{status_name}-status.txt"
            )
            status_path.write_text(status + "\n", encoding="ascii")
            phase[f"{status_name}_status_path"] = status_path.name
            phase[f"{status_name}_status_sha256"] = sha256(status_path)
    return {
        "role": role,
        "ordinal": ordinal,
        "command": "CLOSECIRCUIT",
        "close_reason": "REQUESTED",
        "stream_transition": (
            "stream-reattached"
            if after["stream_id"] == before["stream_id"]
            else "stream-reopened"
        ),
        "process_pid": process_pid,
        "control_socket_inode": control_inode,
        "started_ns": started_ns,
        "completed_ns": completed_ns,
        "recovery_ns": completed_ns - started_ns,
        "before": {
            key: before[key]
            for key in (
                "stream_id_sha256",
                "circuit_id_sha256",
                "circuit_path_sha256",
                "circuit_hop_count",
                "circuit_purpose",
                "stream_status_path",
                "stream_status_sha256",
                "circuit_status_path",
                "circuit_status_sha256",
            )
        },
        "after": {
            key: after[key]
            for key in (
                "stream_id_sha256",
                "circuit_id_sha256",
                "circuit_path_sha256",
                "circuit_hop_count",
                "circuit_purpose",
                "stream_status_path",
                "stream_status_sha256",
                "circuit_status_path",
                "circuit_status_sha256",
            )
        },
    }


def process_socket_inodes(pid: int) -> set[str]:
    output: set[str] = set()
    try:
        descriptors = list((Path("/proc") / str(pid) / "fd").iterdir())
    except FileNotFoundError:
        return output
    for descriptor in descriptors:
        try:
            target = os.readlink(descriptor)
        except (FileNotFoundError, PermissionError):
            continue
        if target.startswith("socket:[") and target.endswith("]"):
            output.add(target[8:-1])
    return output


def decode_proc_address(value: str, version: int) -> str:
    raw = bytes.fromhex(value)
    if version == 4:
        return str(ipaddress.IPv4Address(raw[::-1]))
    require(len(raw) == 16, "Linux IPv6 socket address has the wrong size")
    reordered = b"".join(
        raw[offset : offset + 4][::-1] for offset in range(0, 16, 4)
    )
    return str(ipaddress.IPv6Address(reordered))


def process_inet_sockets(pid: int, protocol: str) -> list[dict[str, object]]:
    inodes = process_socket_inodes(pid)
    records: list[dict[str, object]] = []
    for version, table in (
        (4, Path(f"/proc/net/{protocol}")),
        (6, Path(f"/proc/net/{protocol}6")),
    ):
        for line in table.read_text(encoding="ascii").splitlines()[1:]:
            fields = line.split()
            if len(fields) < 10 or fields[9] not in inodes:
                continue
            local_hex, local_port_hex = fields[1].rsplit(":", 1)
            remote_hex, remote_port_hex = fields[2].rsplit(":", 1)
            records.append(
                {
                    "inode": fields[9],
                    "local_address": decode_proc_address(local_hex, version),
                    "local_port": int(local_port_hex, 16),
                    "remote_address": decode_proc_address(remote_hex, version),
                    "remote_port": int(remote_port_hex, 16),
                    "state": fields[3],
                }
            )
    return records


def actual_tor_role_evidence(
    pair_root: Path,
    instance: dict[str, object],
    node: dict[str, object],
    phase: str | None = None,
) -> dict[str, object]:
    role = str(instance["role"])
    root = Path(instance["root"])
    process = instance["process"]
    observer = instance["observer"]
    require(isinstance(process, subprocess.Popen), "Tor process type drifted")
    require(isinstance(observer, TorStreamObserver), "Tor observer type drifted")
    require(process.poll() is None, f"{role} Tor exited before evidence capture")
    events = observer.stop()
    suffix = "" if phase is None else f"-{phase}"
    event_path = pair_root / f"tor-{role}{suffix}-control-events.txt"
    event_path.write_text("\n".join(events) + "\n", encoding="ascii")

    expected_source = str(instance["expected_source_address"])
    expected_target = str(node["target"])
    source_streams: dict[str, str] = {}
    succeeded: list[tuple[str, str]] = []
    circuit_events: dict[str, list[str]] = {}
    for line in events:
        fields = line.split()
        if len(fields) >= 5 and fields[:2] == ["650", "CIRC"]:
            if fields[3] in {"BUILT", "CLOSED"}:
                circuit_events[fields[2]] = fields[2:]
            continue
        if len(fields) < 6 or fields[:2] != ["650", "STREAM"]:
            continue
        stream_id, state, circuit_id, target = fields[2:6]
        if state == "NEW":
            source_fields = [
                field.split("=", 1)[1]
                for field in fields[6:]
                if field.startswith("SOURCE_ADDR=")
            ]
            if len(source_fields) != 1:
                continue
            source_host, _, _ = source_fields[0].rpartition(":")
            if source_host == expected_source:
                require(
                    target == expected_target,
                    f"{role} Tor observed an unexpected guest target {target}",
                )
                source_streams[stream_id] = target
        elif state == "SUCCEEDED" and stream_id in source_streams:
            require(target == expected_target, f"{role} Tor target changed in flight")
            succeeded.append((stream_id, circuit_id))

    require(source_streams, f"{role} Tor saw no SOCKS stream from its guest")
    require(succeeded, f"{role} Tor saw no successful guest SOCKS stream")
    bootstrap = tor_getinfo(root, "status/bootstrap-phase")
    require(
        "PROGRESS=100" in bootstrap and "TAG=done" in bootstrap,
        f"{role} Tor bootstrap is incomplete",
    )
    current_circuits = tor_getinfo(root, "circuit-status").splitlines()
    bootstrap_path = pair_root / f"tor-{role}{suffix}-bootstrap-status.txt"
    bootstrap_path.write_text(bootstrap + "\n", encoding="ascii")
    circuit_path = pair_root / f"tor-{role}{suffix}-circuit-status.txt"
    circuit_path.write_text(
        "\n".join(current_circuits) + "\n", encoding="ascii"
    )
    circuit_records = {
        fields[0]: fields
        for line in current_circuits
        if len(fields := line.split()) >= 3 and fields[1] == "BUILT"
    }
    selected = select_tor_application_stream(
        succeeded, circuit_records, circuit_events
    )
    require(selected is not None, f"{role} Tor stream has no built circuit evidence")
    stream_id, _, circuit = selected
    # GETINFO uses ID BUILT PATH. A raw event uses ID STATE PATH after dropping
    # 650/CIRC; a later CLOSED event can carry the final linked Conflux purpose
    # for a stream that originally succeeded while the circuit was unlinked.
    require(
        len(circuit) >= 3 and circuit[1] in {"BUILT", "CLOSED"},
        "Tor circuit shape drifted",
    )
    path = circuit[2]
    purpose = [
        field.split("=", 1)[1]
        for field in circuit[3:]
        if field.startswith("PURPOSE=")
    ]
    require(
        len(purpose) == 1 and purpose[0] in TOR_APPLICATION_CIRCUIT_PURPOSES,
        f"{role} Tor stream did not use an application circuit",
    )
    hop_count = len(path.split(","))
    require(hop_count >= 3, f"{role} Tor circuit has fewer than three hops")
    public_remotes = sorted(
        {
            f"{record['remote_address']}:{record['remote_port']}"
            for record in process_inet_sockets(process.pid, "tcp")
            if int(record["remote_port"]) != 0
            and ipaddress.ip_address(str(record["remote_address"])).is_global
        }
    )
    require(public_remotes, f"{role} Tor owns no public TCP socket")
    return {
        "role": role,
        **({"phase": phase} if phase is not None else {}),
        "control_authenticated": True,
        "source_address": expected_source,
        "socks_endpoint": instance["socks_endpoint"],
        "stream_target": expected_target,
        "guest_source_stream_count": len(source_streams),
        "successful_guest_stream_count": len(succeeded),
        "stream_id_sha256": hashlib.sha256(stream_id.encode("ascii")).hexdigest(),
        "circuit_hop_count": hop_count,
        "circuit_purpose": purpose[0],
        "circuit_path_sha256": hashlib.sha256(path.encode("ascii")).hexdigest(),
        "bootstrap_progress": 100,
        "public_tcp_remote_count": len(public_remotes),
        "public_tcp_remote_set_sha256": hashlib.sha256(
            ("\n".join(public_remotes) + "\n").encode("ascii")
        ).hexdigest(),
        "configuration": instance["configuration"],
        "configuration_sha256": instance["configuration_sha256"],
        "process_pid": process.pid,
        "control_socket_inode": (root / "control.sock").stat().st_ino,
        "events_path": event_path.name,
        "events_sha256": sha256(event_path),
        "bootstrap_status_path": bootstrap_path.name,
        "bootstrap_status_sha256": sha256(bootstrap_path),
        "circuit_status_path": circuit_path.name,
        "circuit_status_sha256": sha256(circuit_path),
    }


def start_tap_capture(
    tap: str, destination: Path
) -> tuple[subprocess.Popen, tuple[object, object]]:
    log = destination.with_suffix(".dumpcap.log").open("wb")
    output = destination.open("wb")
    process = subprocess.Popen(
        [
            "sudo",
            "-n",
            str(HOST_BIN / "dumpcap"),
            "-q",
            "-i",
            tap,
            "-f",
            "ip",
            "-w",
            "-",
        ],
        stdout=output,
        stderr=log,
        start_new_session=True,
    )
    wait_for(
        lambda: b"Capturing on" in destination.with_suffix(".dumpcap.log").read_bytes()
        or process.poll() is not None,
        10,
        f"{tap} packet capture",
    )
    require(process.poll() is None, f"{tap} packet capture exited during startup")
    return process, (log, output)


def summarize_tap_capture(
    capture: Path, role: str, proxy_port: int = SOCKS5_PORT
) -> dict:
    local = "10.0.0.11" if role == "client" else "10.0.0.12"
    peer = "10.0.0.12" if role == "client" else "10.0.0.11"
    result = subprocess.run(
        [
            str(HOST_BIN / "tshark"),
            "-r",
            str(capture),
            "-Y",
            "ip",
            "-T",
            "fields",
            "-E",
            "separator=/t",
            "-E",
            "occurrence=f",
            "-e",
            "ip.src",
            "-e",
            "ip.dst",
            "-e",
            "ip.proto",
            "-e",
            "tcp.dstport",
            "-e",
            "udp.dstport",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    rows = []
    for raw in result.stdout.splitlines():
        fields = raw.split("\t")
        fields.extend([""] * (5 - len(fields)))
        if fields[0] == local:
            rows.append(tuple(fields[1:5]))
    require(rows, f"{role} capture has no IPv4 egress")
    unexpected = [
        row
        for row in rows
        if row != (HOST_BRIDGE_ADDRESS, "6", str(proxy_port), "")
    ]
    require(not unexpected, f"{role} escaped strict SOCKS containment: {unexpected[:5]}")
    summary = {
        "role": role,
        "tap": "vm-iotoxc" if role == "client" else "vm-iotoxd",
        "path": capture.name,
        "capture_sha256": sha256(capture),
        "egress_ipv4_packets": len(rows),
        "allowed_destination": f"{HOST_BRIDGE_ADDRESS}:{proxy_port}",
        "only_proxy_destination": True,
        "tcp_only": True,
        "native_udp_packets": 0,
        "direct_bootstrap_packets": 0,
        "direct_peer_packets": 0,
        "peer_ipv4": peer,
    }
    return summary


def summarize_mixed_context_capture(
    capture: Path, role: str, proxy_port: int = SOCKS5_PORT
) -> dict:
    local = "10.0.0.11" if role == "client" else "10.0.0.12"
    peer = "10.0.0.12" if role == "client" else "10.0.0.11"
    result = subprocess.run(
        [
            str(HOST_BIN / "tshark"),
            "-r",
            str(capture),
            "-Y",
            "ip",
            "-T",
            "fields",
            "-E",
            "separator=/t",
            "-E",
            "occurrence=f",
            "-e",
            "ip.src",
            "-e",
            "ip.dst",
            "-e",
            "ip.proto",
            "-e",
            "tcp.dstport",
            "-e",
            "udp.dstport",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    rows = []
    for raw in result.stdout.splitlines():
        fields = raw.split("\t")
        fields.extend([""] * (5 - len(fields)))
        if fields[0] == local:
            rows.append(tuple(fields[1:5]))
    require(rows, f"{role} mixed-context capture has no IPv4 egress")
    # Native Tox is allowed to discover and use arbitrary UDP DHT endpoints.
    # The strict property for the mixed topology is that every TCP flow stays
    # on one of the explicitly configured host-local endpoints: the SOCKS
    # proxy for the Tor-designated worker or the pinned TCP relay.  ICMP is a
    # permitted consequence of the native UDP stack (including destination-
    # unreachable responses), but it can never satisfy either TCP count.
    proxy_packets = sum(
        row == (HOST_BRIDGE_ADDRESS, "6", str(proxy_port), "")
        for row in rows
    )
    native_tcp_relay_packets = sum(
        row == (HOST_BRIDGE_ADDRESS, "6", str(BOOTSTRAP_PORT), "")
        for row in rows
    )
    native_udp_packets = sum(row[1] == "17" for row in rows)
    native_icmp_packets = sum(row[1] == "1" for row in rows)
    unexpected = [
        row
        for row in rows
        if not (
            row[1] == "17"
            or row == (HOST_BRIDGE_ADDRESS, "6", str(proxy_port), "")
            or row == (HOST_BRIDGE_ADDRESS, "6", str(BOOTSTRAP_PORT), "")
            or row[1] == "1"
        )
    ]
    require(
        not unexpected,
        f"{role} mixed-context route escaped its declared egress classes: {unexpected[:5]}",
    )
    require(proxy_packets > 0, f"{role} emitted no strict-SOCKS worker packets")
    require(native_udp_packets > 0, f"{role} emitted no native-primary UDP packets")
    return {
        "role": role,
        "tap": "vm-iotoxc" if role == "client" else "vm-iotoxd",
        "path": capture.name,
        "capture_sha256": sha256(capture),
        "egress_ipv4_packets": len(rows),
        "proxy_packets": proxy_packets,
        "proxy_endpoint": f"{HOST_BRIDGE_ADDRESS}:{proxy_port}",
        "native_udp_packets": native_udp_packets,
        "native_tcp_relay_packets": native_tcp_relay_packets,
        "native_icmp_packets": native_icmp_packets,
        "mixed_native_and_proxy": True,
        "tcp_confined_to_configured_local_endpoints": True,
        "unexpected_context_packets": 0,
        "peer_ipv4": peer,
    }


def baseline_digest(current: Path) -> str:
    digest = hashlib.sha256()
    for relative in (
        "a/device.toxsave",
        "a/device.identity",
        "b/device.toxsave",
        "b/device.identity",
    ):
        path = current / relative
        require(path.is_file() and not path.is_symlink(), f"missing baseline: {path}")
        require(path.stat().st_mode & 0o777 == 0o600, f"unsafe baseline mode: {path}")
        digest.update(relative.encode("ascii"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
    return digest.hexdigest()


def stripe_baseline_digest(current: Path) -> str:
    digest = hashlib.sha256()
    for relative in (
        "a0.toxsave",
        "a1.toxsave",
        "a2.toxsave",
        "b0.toxsave",
        "b1.toxsave",
        "b2.toxsave",
    ):
        path = current / relative
        require(path.is_file() and not path.is_symlink(), f"missing stripe baseline: {path}")
        require(path.stat().st_mode & 0o777 == 0o600, f"unsafe stripe baseline mode: {path}")
        digest.update(relative.encode("ascii"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
    return digest.hexdigest()


def command_for(
    role: str,
    route: str,
    proof_root: Path,
    prelaunch_receipt: Path | None = None,
    guest_receipt_timeout: int = 480,
) -> list[str]:
    node = shutil.which("node")
    require(node is not None, "node is required by the Sandwurm receipt chain")
    host_path = f"{HOST_BIN}:{Path(node).parent}"
    tap = "vm-iotoxc" if role == "client" else "vm-iotoxd"
    config = f"iotox-sandwurm-{role}-{route}"
    environment = {
        "PATH": host_path,
        "SANDWURM_BIN": str(SANDWURM_BIN),
        "SW_DIRECT_CH_LIVE_CHAIN_PROOF_ROOT": str(proof_root),
        "SW_DIRECT_CH_LIVE_CHAIN_LAUNCH": "1",
        "SW_DIRECT_CH_LIVE_CHAIN_BUILD_ARTIFACTS": "1",
        "SW_DIRECT_CH_LIVE_CHAIN_MATERIALIZE_ROOT": "1",
        "SW_DIRECT_CH_LIVE_CHAIN_REALIZE_TOOLCHAIN": "1",
        "SW_DIRECT_CH_LIVE_CHAIN_TOOLCHAIN_FLAKE_REF": f"git+file:{SANDWURM_ROOT}",
        # A dirty git+file flake keeps the same rev-dirty identity while its
        # tracked contents change.  Nix's evaluation cache can therefore hand
        # a qualification run an older guest closure.  Pair proofs must always
        # evaluate the exact working-tree source that Sandwurm archives.
        "NIX_CONFIG": "eval-cache = false",
        "SW_DIRECT_CH_LIVE_CHAIN_NETWORK_MODE": "prepared-host-tap-nat",
        "SW_DIRECT_CH_LIVE_CHAIN_LAUNCH_MEMORY": "size=2G,shared=on",
        "SW_DIRECT_CH_LIVE_CHAIN_LAUNCH_VCPUS": "2",
        "SW_DIRECT_CH_LIVE_CHAIN_GUEST_RECEIPT_TIMEOUT_SECONDS": str(
            guest_receipt_timeout
        ),
        "SW_DIRECT_CH_PRELAUNCH_RUNNER_AUTHORITY_RECEIPT": str(RUNNER_RECEIPT),
        "SW_DIRECT_NIXOS_FLAKE_REF": f"git+file:{ROOT}",
        "SW_DIRECT_NIXOS_CONFIG": config,
        "SW_SMOKE_HOST_NET_TAP_INTERFACE": tap,
    }
    if prelaunch_receipt is not None:
        environment["SW_DIRECT_CH_LIVE_CHAIN_PRELAUNCH_RECEIPT"] = str(
            prelaunch_receipt
        )
    env_arguments = [f"{key}={value}" for key, value in environment.items()]
    probe = SANDWURM_ROOT / "tests/probe-direct-cloud-hypervisor-live-chain.sh"
    return ["sudo", "-n", "env", *env_arguments, str(HOST_BIN / "bash"), str(probe)]


def wait_for(predicate, timeout: float, description: str) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.1)
    raise RuntimeError(f"timeout waiting for {description}")


def read_root_file(path: Path) -> str:
    return sudo("cat", str(path), capture=True).stdout


def root_file_exists(path: Path) -> bool:
    result = subprocess.run(
        ["sudo", "-n", "test", "-s", str(path)],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def tap_observation(name: str) -> dict:
    result = sudo(str(HOST_BIN / "ip"), "-j", "link", "show", "dev", name, capture=True)
    values = json.loads(result.stdout)
    require(isinstance(values, list) and len(values) == 1, f"missing TAP {name}")
    value = values[0]
    return {
        "name": name,
        "master": value.get("master"),
        "operstate": value.get("operstate"),
    }


def tap_exists(name: str) -> bool:
    return subprocess.run(
        ["sudo", "-n", str(HOST_BIN / "ip"), "link", "show", "dev", name],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0


def terminate(processes: dict[str, subprocess.Popen]) -> None:
    # sudo can exit before a descendant which remains in the session's process
    # group (notably when a Nix build is interrupted).  Reap the whole group
    # based on the PGID we created, rather than trusting only the leader's state.
    groups = tuple(process.pid for process in processes.values())
    for group in groups:
        try:
            os.killpg(group, signal.SIGTERM)
        except ProcessLookupError:
            pass
        except PermissionError:
            subprocess.run(
                ["sudo", "-n", "kill", "-TERM", "--", f"-{group}"],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        # poll() reaps a terminated leader so an otherwise empty process
        # group is not mistaken for a live descendant group.
        for process in processes.values():
            process.poll()
        alive = []
        for group in groups:
            try:
                os.killpg(group, 0)
                alive.append(group)
            except ProcessLookupError:
                pass
            except PermissionError:
                alive.append(group)
        if not alive:
            break
        time.sleep(0.1)
    for group in groups:
        try:
            os.killpg(group, signal.SIGKILL)
        except ProcessLookupError:
            pass
        except PermissionError:
            subprocess.run(
                ["sudo", "-n", "kill", "-KILL", "--", f"-{group}"],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
    for process in processes.values():
        try:
            process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            pass


def kill_process_group(process: subprocess.Popen, label: str) -> int:
    require(process.poll() is None, f"{label} exited before injected SIGKILL")
    os.killpg(process.pid, signal.SIGKILL)
    try:
        returncode = process.wait(timeout=10)
    except subprocess.TimeoutExpired as error:
        raise RuntimeError(f"{label} survived injected SIGKILL") from error
    require(
        returncode == -signal.SIGKILL,
        f"{label} did not terminate by injected SIGKILL: {returncode}",
    )
    return returncode


def realize_bootstrap(package: str = "toxBootstrap") -> Path:
    result = subprocess.run(
        [
            "nix",
            "build",
            "--no-link",
            "--print-out-paths",
            f"git+file:{ROOT}#{package}",
        ],
        check=True,
        text=True,
        capture_output=True,
        timeout=300,
    )
    paths = [Path(line) for line in result.stdout.splitlines() if line]
    require(
        len(paths) == 1,
        f"bootstrap fixture realization was ambiguous: {package}",
    )
    binary = paths[0] / "bin/DHT_bootstrap"
    require(binary.is_file(), f"bootstrap fixture is absent: {package}: {binary}")
    return binary


def run_provider_rolling(route: str) -> Path:
    """Qualify one live 0.2.22/0.2.23 pair in two Sandwurm guests."""
    require(route in {"direct-udp", "forced-tcp"}, "invalid provider route")
    require(os.access("/dev/kvm", os.R_OK | os.W_OK), "/dev/kvm is unavailable")
    require(SANDWURM_BIN.is_file(), f"Sandwurm binary is absent: {SANDWURM_BIN}")
    sudo("true")
    ensure_host_bridge()

    pair_parent = STATE_ROOT / "pairs"
    pair_parent.mkdir(parents=True, exist_ok=True)
    pair_root = Path(tempfile.mkdtemp(prefix="pair.", dir=pair_parent)).resolve()
    os.chmod(pair_root, 0o700)
    role_roots = {role: pair_root / role for role in ("client", "device")}
    for path in role_roots.values():
        path.mkdir(mode=0o700)

    processes: dict[str, subprocess.Popen] = {}
    logs: dict[str, tuple] = {}
    fixture_process: subprocess.Popen | None = None
    fixture_log = None
    started_ns = time.monotonic_ns()
    try:
        bootstrap_binary = realize_bootstrap()
        bootstrap_dir = pair_root / "host-bootstrap"
        bootstrap_dir.mkdir(mode=0o700)
        fixture_log = (bootstrap_dir / "bootstrap.log").open("wb")
        fixture_process = subprocess.Popen(
            [str(bootstrap_binary), "--ipv4"],
            cwd=bootstrap_dir,
            stdout=fixture_log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        public_id = bootstrap_dir / "PUBLIC_ID.txt"
        wait_for(
            lambda: public_id.is_file() and public_id.stat().st_size == 64,
            10,
            "host bridge bootstrap public key",
        )
        require_bootstrap_ready(fixture_process)
        bootstrap_key = public_id.read_text(encoding="ascii")
        require(
            re.fullmatch(r"[0-9A-F]{64}", bootstrap_key) is not None,
            "invalid host bridge bootstrap public key",
        )
        os.chmod(public_id, 0o600)
        os.chmod(bootstrap_dir / "key", 0o600)

        for role, proof_root in role_roots.items():
            stdout = (pair_root / f"{role}.chain.stdout").open("wb")
            stderr = (pair_root / f"{role}.chain.stderr").open("wb")
            logs[role] = (stdout, stderr)
            processes[role] = subprocess.Popen(
                command_for(role, route, proof_root, guest_receipt_timeout=480),
                stdout=stdout,
                stderr=stderr,
                start_new_session=True,
            )

        workspace = {
            role: root / "live/workspace-export" for role, root in role_roots.items()
        }
        wait_for(
            lambda: all(path.is_dir() for path in workspace.values())
            or any(process.poll() is not None for process in processes.values()),
            900,
            "both provider-upgrade Sandwurm workspace exports",
        )
        require(
            all(path.is_dir() for path in workspace.values()),
            "a provider-upgrade chain exited before both workspace exports",
        )
        require(
            all(process.poll() is None for process in processes.values()),
            "a provider-upgrade VMM chain exited before rendezvous",
        )

        for role, path in workspace.items():
            input_dir = path / "iotox-input"
            sudo("install", "-d", "-m", "0700", str(input_dir))
            scenario_file = pair_root / f"{role}.scenario"
            scenario_file.write_text("provider-rolling\n", encoding="ascii")
            sudo(
                "install", "-m", "0600", str(scenario_file), str(input_dir / "scenario")
            )
            scenario_file.unlink()
            bootstrap_file = pair_root / f"{role}.bootstrap.public-key"
            bootstrap_file.write_text(bootstrap_key + "\n", encoding="ascii")
            sudo(
                "install",
                "-m",
                "0600",
                str(bootstrap_file),
                str(input_dir / "bootstrap.public-key"),
            )
            bootstrap_file.unlink()

        public_key_paths = {
            role: path / f"iotox-rendezvous/{role}.provider-public-key"
            for role, path in workspace.items()
        }
        wait_for(
            lambda: all(root_file_exists(path) for path in public_key_paths.values())
            or any(process.poll() is not None for process in processes.values()),
            180,
            "both old-provider public-key rendezvous records",
        )
        require(
            all(root_file_exists(path) for path in public_key_paths.values()),
            "a provider-upgrade guest failed before public-key rendezvous",
        )
        public_keys = {
            role: read_root_file(path).strip() for role, path in public_key_paths.items()
        }
        require(
            all(re.fullmatch(r"[0-9A-F]{64}", key) for key in public_keys.values()),
            "a provider-upgrade guest emitted an invalid public key",
        )
        require(
            public_keys["client"] != public_keys["device"],
            "provider-upgrade guests share one Tox identity",
        )
        taps = [tap_observation("vm-iotoxc"), tap_observation("vm-iotoxd")]
        require(
            all(tap["master"] == HOST_BRIDGE for tap in taps),
            "a provider-upgrade TAP escaped the prepared bridge",
        )

        for role, path in workspace.items():
            peer_role = "device" if role == "client" else "client"
            peer_file = pair_root / f"{role}.provider-peer-public-key"
            peer_file.write_text(public_keys[peer_role] + "\n", encoding="ascii")
            sudo(
                "install",
                "-m",
                "0600",
                str(peer_file),
                str(path / "iotox-input/provider-peer-public-key"),
            )
            peer_file.unlink()

        receipt_paths = {
            role: path / "guest-receipts/iotox/provider-rolling.json"
            for role, path in workspace.items()
        }
        failure_paths = {
            role: path / f"iotox-rendezvous/{role}.failure"
            for role, path in workspace.items()
        }
        wait_for(
            lambda: all(root_file_exists(path) for path in receipt_paths.values())
            or any(root_file_exists(path) for path in failure_paths.values())
            or any(process.poll() is not None for process in processes.values()),
            300,
            "both mixed-provider exchange receipts",
        )
        failures = {
            role: read_root_file(path).strip()
            for role, path in failure_paths.items()
            if root_file_exists(path)
        }
        require(
            all(root_file_exists(path) for path in receipt_paths.values()),
            f"a mixed-provider guest failed before emitting its receipt: {failures}",
        )

        for role, process in processes.items():
            try:
                result = process.wait(timeout=540)
            except subprocess.TimeoutExpired as error:
                raise RuntimeError(
                    f"{role} mixed-provider Sandwurm chain did not terminate"
                ) from error
            require(result == 0, f"{role} mixed-provider Sandwurm chain exited {result}")
        completed_ns = time.monotonic_ns()

        sudo("chown", "-R", f"{os.getuid()}:{os.getgid()}", str(pair_root))
        receipts = {}
        chains = {}
        launches = {}
        for role, root in role_roots.items():
            receipt_relative = (
                f"{role}/live/workspace-export/guest-receipts/iotox/"
                "provider-rolling.json"
            )
            chain_relative = f"{role}/direct-cloud-hypervisor-live-chain.json"
            launch_relative = f"{role}/prelaunch/launch/cloud-hypervisor-launch.json"
            receipt = load(pair_root / receipt_relative)
            expected_provider = "0.2.22" if role == "client" else "0.2.23"
            expected_connection = "udp" if route == "direct-udp" else "tcp"
            require(receipt.get("status") == "passed", f"{role} provider receipt failed")
            require(receipt.get("role") == role, f"{role} provider receipt role mismatch")
            require(receipt.get("route_mode") == route, f"{role} provider route mismatch")
            require(
                receipt.get("live_provider") == expected_provider,
                f"{role} live provider mismatch",
            )
            require(
                receipt.get("expected_connection") == expected_connection,
                f"{role} provider connection mismatch",
            )
            receipts[role] = {
                "path": receipt_relative,
                "sha256": sha256(pair_root / receipt_relative),
            }
            chains[role] = {
                "path": chain_relative,
                "sha256": sha256(pair_root / chain_relative),
            }
            launches[role] = {
                "path": launch_relative,
                "sha256": sha256(pair_root / launch_relative),
            }

        manifest = {
            "schema": "iotox.sandwurm-provider-rolling-manifest.v0",
            "status": "passed",
            "route_mode": route,
            "expected_connection": "udp" if route == "direct-udp" else "tcp",
            "old_provider": "0.2.22",
            "current_provider": "0.2.23",
            "client_live_provider": "0.2.22",
            "device_live_provider": "0.2.23",
            "savedata_created_by": "0.2.22",
            "simultaneous_vmm_chains_observed": True,
            "prepared_bridge": HOST_BRIDGE,
            "bootstrap_fixture": "pinned-host-bridge-c-toxcore-0.2.23",
            "rendezvous_monotonic_span_ns": completed_ns - started_ns,
            "taps": taps,
            "receipts": receipts,
            "chains": chains,
            "launches": launches,
            "proof_root_contains_private_guest_disks": True,
            "receipts_contain_secrets": False,
            "compact_export": None,
        }
        manifest_path = pair_root / "provider-rolling-manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        os.chmod(manifest_path, 0o600)
        subprocess.run(
            [
                os.sys.executable,
                str(ROOT / "tools/verify-sandwurm-provider-rolling.py"),
                str(pair_root),
                "--route",
                route,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        print(json.dumps({**manifest, "proof_root": str(pair_root)}, indent=2, sort_keys=True))
        return pair_root
    finally:
        if fixture_process is not None:
            terminate({"bootstrap": fixture_process})
        terminate(processes)
        for stdout, stderr in logs.values():
            stdout.close()
            stderr.close()
        if fixture_log is not None:
            fixture_log.close()


def run(
    route: str,
    scenario: str,
    tor_node_text: str | None = None,
    i2p_node_texts: list[str] | None = None,
) -> Path:
    require(
        route in {"direct-udp", "forced-tcp", "tox-tor", *I2P_ROUTES},
        "invalid pair route",
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
            "provider-rolling",
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
        "invalid pair scenario",
    )
    if scenario == "provider-rolling":
        require(route != "tox-tor", "provider-rolling does not support tox-tor")
        return run_provider_rolling(route)
    require(
        scenario != "relay-restart" or route == "forced-tcp",
        "relay-restart requires forced-tcp",
    )
    require(
        scenario != "proxy-restart" or route == "tox-tor",
        "proxy-restart requires tox-tor",
    )
    require(
        scenario not in BIDIRECTIONAL_SYNC_SCENARIOS or route == "direct-udp",
        "bidirectional sync qualification requires direct-udp",
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
        "tox-tor is qualified only for baseline, proxy-restart, and Ratox route gates",
    )
    require(
        route not in I2P_ROUTES
        or scenario in {"baseline", "i2p-router-restart", "i2p-service-restart"},
        "Tox/I2P supports only its baseline and recovery gates",
    )
    require(
        scenario != "i2p-router-restart" or route in I2P_ROUTES,
        "I2P router restart requires Tox/I2P",
    )
    require(
        scenario != "i2p-service-restart" or route in I2P_ROUTES,
        "I2P service restart requires Tox/I2P",
    )
    require(
        scenario not in RATOX_STRIPE_SCENARIOS or route == "forced-tcp",
        "Ratox striping requires forced-tcp",
    )
    require(
        scenario != "sync-content-multi-source-loss"
        or route == "direct-udp",
        "selected-source loss qualification requires direct-udp",
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
        "private mixed-context qualification requires a native UDP primary",
    )
    actual_tor_scenarios = {
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
    actual_tor = scenario in actual_tor_scenarios
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
    actual_i2p = route in I2P_ROUTES or actual_i2p_payload
    actual_tor_payload = scenario in {
        "sync-content-route-private-actual-tor",
        "sync-content-same-source-multi-route-actual-tor",
        "sync-content-multi-route-actual-tor",
        "sync-content-multi-route-actual-tor-loss",
        "sync-tree-route-private-actual-tor-payload",
    }
    actual_tor_loss = scenario == "sync-tree-route-private-actual-tor-loss"
    actual_tor_ratox_loss = scenario == "ratox-route-actual-tor-loss"
    actual_tor_ratox_soak = scenario == "ratox-route-actual-tor-soak"
    actual_tor_ratox_adversary = (
        scenario == "ratox-route-actual-tor-adversary"
    )
    actual_tor_process_fault = actual_tor_loss or actual_tor_ratox_loss
    require(
        not actual_tor or tor_node_text is not None,
        "actual-Tor qualification requires --tor-node IPv4:PORT:KEY",
    )
    tor_node = parse_actual_tor_node(tor_node_text) if actual_tor else None
    i2p_node_values = i2p_node_texts or []
    require(
        not actual_i2p or len(i2p_node_values) == 3,
        "Tox/I2P construction requires exactly three --i2p-node records",
    )
    require(
        actual_i2p or not i2p_node_values,
        "--i2p-node is valid only for an actual-I2P gate",
    )
    i2p_nodes = [
        parse_public_tox_node(value, "actual-I2P") for value in i2p_node_values
    ]
    require(
        not actual_i2p
        or (
            len({node["record"] for node in i2p_nodes}) == 3
            and len({node["public_key"] for node in i2p_nodes}) == 3
        ),
        "Tox/I2P construction node records and keys must be distinct",
    )
    require(
        not (
            actual_tor_ratox_loss
            or actual_tor_ratox_soak
            or actual_tor_ratox_adversary
        )
        or route == "tox-tor",
        "actual-Tor Ratox gate requires a Tox/Tor primary",
    )
    routed_socks5 = (
        route == "tox-tor" and not actual_tor
    ) or scenario == "sync-tree-route-private-mixed"
    routed_privacy = routed_socks5 or actual_tor or actual_i2p
    require(os.access("/dev/kvm", os.R_OK | os.W_OK), "/dev/kvm is unavailable")
    require(SANDWURM_BIN.is_file(), f"Sandwurm binary is absent: {SANDWURM_BIN}")
    sudo("true")
    ensure_host_bridge()

    current = KEY_CACHE / "current"
    require(current.is_dir() and not current.is_symlink(), "reusable key cache is absent")
    lock_path = KEY_CACHE / ".run.lock"
    lock_path.touch(mode=0o600, exist_ok=True)
    lock_handle = lock_path.open("r+")
    try:
        fcntl.flock(lock_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as error:
        raise RuntimeError("reusable test identities are already active") from error
    digest_before = baseline_digest(current)
    stripe_current: Path | None = None
    stripe_digest_before: str | None = None
    if scenario in RATOX_STRIPE_SCENARIOS or scenario in MULTI_ROUTE_SYNC_SCENARIOS:
        stripe_current = FOUR_ROUTE_KEY_CACHE / "current"
        require(
            stripe_current.is_dir() and not stripe_current.is_symlink(),
            "reusable four-route key cache is absent",
        )
        stripe_digest_before = stripe_baseline_digest(stripe_current)

    pair_parent = STATE_ROOT / "pairs"
    pair_parent.mkdir(parents=True, exist_ok=True)
    pair_root = Path(tempfile.mkdtemp(prefix="pair.", dir=pair_parent)).resolve()
    os.chmod(pair_root, 0o700)
    role_roots = {role: pair_root / role for role in ("client", "device")}
    for path in role_roots.values():
        path.mkdir(mode=0o700)

    processes: dict[str, subprocess.Popen] = {}
    logs = {}
    fixture_process: subprocess.Popen | None = None
    secondary_fixture_process: subprocess.Popen | None = None
    socks5_process: subprocess.Popen | None = None
    socks5_phase = "initial"
    socks5_restart_count = 0
    capture_processes: dict[str, subprocess.Popen] = {}
    capture_handles: dict[str, tuple[object, object]] = {}
    capture_summaries: list[dict] = []
    tor_instances: dict[str, dict[str, object]] = {}
    tor_adversaries: dict[str, dict[str, object]] = {}
    tor_role_evidence: list[dict[str, object]] = []
    tor_pre_loss_evidence: dict[str, object] | None = None
    actual_tor_process_loss: dict[str, object] = {}
    actual_tor_ratox_churn: dict[str, object] = {}
    actual_tor_adversarial_boundary: dict[str, object] = {}
    actual_i2p_fail_closed_loss: dict[str, object] = {}
    range_loss_primed = False
    i2p_instance: dict[str, object] | None = None
    i2p_topology_final: dict[str, object] = {}
    i2p_router_restart_count = 0
    i2p_front_restart_count = 0
    fixture_log = None
    secondary_fixture_log = None
    secondary_bootstrap_key = ""
    multi_source_loss_secondary_requests_before_stop = 0
    multi_source_loss_constructed_replica_head_reinjected = False
    multi_source_loss_durable_replica_cold_start = False
    fixture_restart_count = 0
    fixture_key_preserved = True
    device_daemon_restart_count = 0
    link_interruption_count = 0
    packet_loss_impairment_count = 0
    packet_loss_qdiscs: list[dict] = []
    common_link_fairness_qdisc: dict[str, object] = {}
    ratox_route_impairment: dict[str, object] = {}
    ratox_route_loss: dict[str, object] = {}
    ratox_cli_reconnect = scenario in {
        "ratox-cli-reconnect",
        "ratox-cli-reconnect-repeated",
    }
    ratox_cli_reconnect_repeated = scenario == "ratox-cli-reconnect-repeated"
    device_guest_restart_count = 0
    sync_client_daemon_restart_count = 0
    initial_device_chain_entry = None
    initial_device_launch_entry = None
    links_blocked = False
    sync_client_shaped = False
    matrix_bulk = (
        scenario in RATOX_MATRIX_SCENARIOS
        and scenario in RATOX_BULK_SCENARIOS
    )
    guest_receipt_timeout = (
        1920
        if actual_tor or actual_i2p
        else 1320
        if matrix_bulk
        or scenario in {
            "sync-tree-route-startup-order",
            "sync-tree-route-private-mixed",
        }
        else (
            2400
            if scenario == "sync-tree-route-throughput"
            else 1800
            if scenario in {
                "sync-content-lane-science",
                "sync-content-lane-science-reverse",
                "sync-content-ratox-latency-science",
                "sync-content-ratox-cap-2-sla",
                "sync-content-ratox-post-bulk-admission",
                "sync-tree-route-population",
                "sync-tree-route-population-loss",
                "sync-tree-route-loss-admission",
                "sync-tree-route-startup-admission",
                "sync-tree-route-concurrent-cancel",
                "sync-tree-route-common-link-fairness",
            }
            else 2100
            if scenario == "sync-file-range-triple-route-loss"
            else 1500
            if scenario in CONTENT_RESTART_SCENARIOS
            or scenario
            in {
                "sync-tree-route-balance",
                "sync-file-range-repeated-route-loss",
            }
            else (
                900
                if scenario
                in {
                    "ratox-route-loss",
                    "ratox-cli-reconnect",
                    "ratox-cli-reconnect-repeated",
                    "ratox-route-actual-tor-loss",
                    "ratox-route-actual-tor-adversary",
                }
                else 960
                if scenario
                in {
                    *CONTENT_MULTI_SOURCE_SCENARIOS,
                    "sync-file-guest-restart",
                    "update-service",
                }
                else 1200
                if scenario in BIDIRECTIONAL_SYNC_SCENARIOS
                else 480
            )
        )
    )
    started_ns = time.monotonic_ns()
    try:
        bootstrap_binary = realize_bootstrap()
        bootstrap_dir = pair_root / "host-bootstrap"
        bootstrap_dir.mkdir(mode=0o700)
        fixture_log = (bootstrap_dir / "bootstrap.log").open("wb")
        fixture_process = subprocess.Popen(
            [str(bootstrap_binary), "--ipv4"],
            cwd=bootstrap_dir,
            stdout=fixture_log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        public_id = bootstrap_dir / "PUBLIC_ID.txt"
        wait_for(
            lambda: public_id.is_file() and public_id.stat().st_size == 64,
            10,
            "host bridge bootstrap public key",
        )
        require_bootstrap_ready(fixture_process)
        bootstrap_key = public_id.read_text(encoding="ascii")
        require(
            re.fullmatch(r"[0-9A-F]{64}", bootstrap_key) is not None,
            "invalid host bridge bootstrap public key",
        )
        os.chmod(public_id, 0o600)
        os.chmod(bootstrap_dir / "key", 0o600)
        if route == "forced-tcp" and scenario in CONTENT_MULTI_SOURCE_SCENARIOS:
            secondary_bootstrap_binary = realize_bootstrap(
                "toxBootstrapSecondary"
            )
            secondary_bootstrap_dir = pair_root / "host-bootstrap-secondary"
            secondary_bootstrap_dir.mkdir(mode=0o700)
            secondary_fixture_log = (
                secondary_bootstrap_dir / "bootstrap.log"
            ).open("wb")
            secondary_fixture_process = subprocess.Popen(
                [str(secondary_bootstrap_binary), "--ipv4"],
                cwd=secondary_bootstrap_dir,
                stdout=secondary_fixture_log,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
            secondary_public_id = secondary_bootstrap_dir / "PUBLIC_ID.txt"
            wait_for(
                lambda: secondary_public_id.is_file()
                and secondary_public_id.stat().st_size == 64,
                10,
                "secondary host bridge bootstrap public key",
            )
            require_bootstrap_ready(secondary_fixture_process)
            secondary_bootstrap_key = secondary_public_id.read_text(
                encoding="ascii"
            )
            require(
                re.fullmatch(r"[0-9A-F]{64}", secondary_bootstrap_key)
                is not None,
                "invalid secondary host bridge bootstrap public key",
            )
            require(
                secondary_bootstrap_key != bootstrap_key,
                "host bridge bootstrap fixtures reused one identity",
            )
            os.chmod(secondary_public_id, 0o600)
            os.chmod(secondary_bootstrap_dir / "key", 0o600)
        if routed_socks5:
            socks5_process = start_socks5_forwarder(pair_root, socks5_phase)
        if actual_tor:
            for role in ("client", "device"):
                phase = (
                    "pre-loss"
                    if actual_tor_process_fault and role == "client"
                    else "continuous"
                )
                tor_instances[role] = start_pair_tor(
                    pair_root,
                    role,
                    phase,
                    adversarial_boundary=actual_tor_ratox_adversary,
                )
            if actual_tor_ratox_adversary:
                require(tor_node is not None, "actual-Tor node disappeared")
                tor_adversaries = {
                    role: start_actual_tor_adversary(pair_root, role, tor_node)
                    for role in ("client", "device")
                }
        if actual_i2p:
            i2p_instance = start_i2p_fronts(pair_root, i2p_nodes)

        for role, proof_root in role_roots.items():
            stdout = (pair_root / f"{role}.chain.stdout").open("wb")
            stderr = (pair_root / f"{role}.chain.stderr").open("wb")
            logs[role] = (stdout, stderr)
            processes[role] = subprocess.Popen(
                command_for(
                    role,
                    route,
                    proof_root,
                    guest_receipt_timeout=guest_receipt_timeout,
                ),
                stdout=stdout,
                stderr=stderr,
                start_new_session=True,
            )

        workspace = {
            role: root / "live/workspace-export" for role, root in role_roots.items()
        }
        wait_for(
            lambda: all(path.is_dir() for path in workspace.values())
            or any(process.poll() is not None for process in processes.values()),
            900,
            "both Sandwurm workspace exports",
        )
        require(
            all(path.is_dir() for path in workspace.values()),
            "a Sandwurm chain exited before both workspace exports",
        )
        require(
            all(process.poll() is None for process in processes.values()),
            "a VMM chain exited before identity injection",
        )

        if routed_privacy:
            wait_for(
                lambda: all(tap_exists(tap) for tap in ("vm-iotoxc", "vm-iotoxd"))
                or any(process.poll() is not None for process in processes.values()),
                900,
                "both routed-privacy TAP devices",
            )
            require(
                all(tap_exists(tap) for tap in ("vm-iotoxc", "vm-iotoxd")),
                "a routed-privacy chain exited before both TAPs appeared",
            )
            taps = [tap_observation("vm-iotoxc"), tap_observation("vm-iotoxd")]
            require(
                all(tap["master"] == HOST_BRIDGE for tap in taps),
                "a routed-privacy TAP escaped the prepared bridge",
            )
            for role, tap in (("client", "vm-iotoxc"), ("device", "vm-iotoxd")):
                capture_name = (
                    f"{role}.tox-i2p.pcapng"
                    if actual_i2p
                    else f"{role}.tox-tor.pcapng"
                )
                process, handles = start_tap_capture(
                    tap, pair_root / capture_name
                )
                capture_processes[role] = process
                capture_handles[role] = handles

        labels = {"client": "a", "device": "b"}
        for role, path in workspace.items():
            input_dir = path / "iotox-input"
            sudo("install", "-d", "-m", "0700", str(input_dir))
            scenario_file = pair_root / f"{role}.scenario"
            scenario_file.write_text(scenario + "\n", encoding="ascii")
            sudo(
                "install",
                "-m",
                "0600",
                str(scenario_file),
                str(input_dir / "scenario"),
            )
            scenario_file.unlink()
            for name in ("device.toxsave", "device.identity"):
                sudo(
                    "install",
                    "-m",
                    "0600",
                    str(current / labels[role] / name),
                    str(input_dir / name),
                )
            if scenario in RATOX_STRIPE_SCENARIOS or scenario in MULTI_ROUTE_SYNC_SCENARIOS:
                require(stripe_current is not None, "stripe key cache is absent")
                label = labels[role]
                lane_count = 3 if scenario in RATOX_STRIPE_SCENARIOS else 2
                for lane in range(1, lane_count + 1):
                    source = stripe_current / f"{label}{lane - 1}.toxsave"
                    sudo(
                        "install",
                        "-m",
                        "0600",
                        str(source),
                        str(input_dir / f"lane-{lane}.toxsave"),
                    )

        for path in workspace.values():
            temporary = pair_root / "bootstrap.public-key"
            temporary.write_text(bootstrap_key + "\n", encoding="ascii")
            sudo(
                "install",
                "-m",
                "0600",
                str(temporary),
                str(path / "iotox-input/bootstrap.public-key"),
            )
            temporary.unlink()

        if secondary_bootstrap_key:
            for path in workspace.values():
                temporary = pair_root / "secondary.bootstrap.public-key"
                temporary.write_text(
                    secondary_bootstrap_key + "\n", encoding="ascii"
                )
                sudo(
                    "install",
                    "-m",
                    "0600",
                    str(temporary),
                    str(
                        path
                        / "iotox-input/secondary.bootstrap.public-key"
                    ),
                )
                temporary.unlink()

        if actual_tor:
            require(tor_node is not None, "actual-Tor node disappeared")
            for role, path in workspace.items():
                proxy_file = pair_root / f"{role}.tor.proxy"
                proxy_file.write_text(
                    f"{HOST_BRIDGE_ADDRESS}:{ACTUAL_TOR_SOCKS_PORTS[role]}\n",
                    encoding="ascii",
                )
                sudo(
                    "install",
                    "-m",
                    "0600",
                    str(proxy_file),
                    str(path / "iotox-input/tor.proxy"),
                )
                proxy_file.unlink()
                node_file = pair_root / f"{role}.tor.node"
                node_file.write_text(str(tor_node["record"]) + "\n", encoding="ascii")
                sudo(
                    "install",
                    "-m",
                    "0600",
                    str(node_file),
                    str(path / "iotox-input/tor.node"),
                )
                node_file.unlink()

        if actual_i2p:
            require(i2p_instance is not None, "I2P topology disappeared")
            ready = i2p_instance["ready"]
            require(isinstance(ready, dict), "I2P topology ready record disappeared")
            node_lines = "\n".join(str(node["record"]) for node in i2p_nodes) + "\n"
            for role, path in workspace.items():
                proxy_file = pair_root / f"{role}.i2p.proxy"
                proxy_file.write_text(str(ready["proxy_endpoint"]) + "\n", encoding="ascii")
                sudo(
                    "install",
                    "-m",
                    "0600",
                    str(proxy_file),
                    str(path / "iotox-input/i2p.proxy"),
                )
                proxy_file.unlink()
                nodes_file = pair_root / f"{role}.i2p.nodes"
                nodes_file.write_text(node_lines, encoding="ascii")
                sudo(
                    "install",
                    "-m",
                    "0600",
                    str(nodes_file),
                    str(path / "iotox-input/i2p.nodes"),
                )
                nodes_file.unlink()

        if scenario in SIGNED_UPDATE_SCENARIOS:
            signer_path = (
                workspace["device"]
                / "iotox-rendezvous/device.update-release-signer"
            )
            signer_failures = {
                role: path / f"iotox-rendezvous/{role}.failure"
                for role, path in workspace.items()
            }
            wait_for(
                lambda: root_file_exists(signer_path)
                or any(
                    root_file_exists(path)
                    for path in signer_failures.values()
                )
                or any(process.poll() is not None for process in processes.values()),
                180,
                "device release-signer rendezvous",
            )
            require(
                root_file_exists(signer_path),
                "device did not publish a release signer: "
                + "; ".join(
                    f"{role}={read_root_file(path).strip()}"
                    for role, path in signer_failures.items()
                    if root_file_exists(path)
                ),
            )
            release_signer = read_root_file(signer_path).strip()
            require(
                re.fullmatch(r"[0-9A-F]{64}", release_signer) is not None,
                "device release signer is invalid",
            )
            temporary = pair_root / "update-release-signer.public"
            temporary.write_text(release_signer + "\n", encoding="ascii")
            sudo(
                "install",
                "-m",
                "0600",
                str(temporary),
                str(
                    workspace["client"]
                    / "iotox-input/update-release-signer.public"
                ),
            )
            temporary.unlink()

        multi_route_address_paths: dict[str, list[Path]] = {}
        multi_route_addresses: dict[str, list[str]] = {}
        if scenario in MULTI_ROUTE_SYNC_SCENARIOS:
            multi_route_address_paths = {
                role: [
                    path / f"iotox-rendezvous/{role}.lane-{lane}.address"
                    for lane in range(1, 3)
                ]
                for role, path in workspace.items()
            }
            wait_for(
                lambda: all(
                    root_file_exists(path)
                    for paths in multi_route_address_paths.values()
                    for path in paths
                ),
                240,
                "four offline auxiliary Tox route addresses",
            )
            require(
                all(process.poll() is None for process in processes.values()),
                "a VMM chain exited before auxiliary route rendezvous",
            )
            multi_route_addresses = {
                role: [read_root_file(path) for path in paths]
                for role, paths in multi_route_address_paths.items()
            }
            require(
                all(
                    ADDRESS_PATTERN.fullmatch(address)
                    for values in multi_route_addresses.values()
                    for address in values
                ),
                "invalid offline auxiliary Tox route address",
            )
            auxiliary_route_keys = [
                address[:64]
                for values in multi_route_addresses.values()
                for address in values
            ]
            require(
                len(set(auxiliary_route_keys)) == 4,
                "multi-route sync pair does not have four distinct auxiliary keys",
            )
            for role, path in workspace.items():
                remote_role = "device" if role == "client" else "client"
                for lane, address in enumerate(
                    multi_route_addresses[remote_role], start=1
                ):
                    temporary = pair_root / f"{role}.lane-{lane}.peer.address"
                    temporary.write_text(
                        address.rstrip("\n") + "\n", encoding="ascii"
                    )
                    sudo(
                        "install",
                        "-m",
                        "0600",
                        str(temporary),
                        str(path / f"iotox-input/lane-{lane}.peer.address"),
                    )
                    temporary.unlink()

        address_paths = {
            role: path / f"iotox-rendezvous/{role}.address"
            for role, path in workspace.items()
        }
        startup_failure_paths = {
            role: path / f"iotox-rendezvous/{role}.failure"
            for role, path in workspace.items()
        }
        wait_for(
            lambda: all(root_file_exists(path) for path in address_paths.values())
            or any(
                root_file_exists(path)
                for path in startup_failure_paths.values()
            )
            or any(process.poll() is not None for process in processes.values()),
            180,
            "both guest public-address rendezvous records",
        )
        require(
            all(root_file_exists(path) for path in address_paths.values()),
            "a guest failed before public-address rendezvous: "
            + "; ".join(
                f"{role}={read_root_file(path).strip()}"
                for role, path in startup_failure_paths.items()
                if root_file_exists(path)
            ),
        )
        require(all(process.poll() is None for process in processes.values()), "a VMM chain exited before rendezvous")
        stripe_address_paths: dict[str, list[Path]] = {}
        if scenario in RATOX_STRIPE_SCENARIOS:
            stripe_address_paths = {
                role: [
                    path / f"iotox-rendezvous/{role}.lane-{lane}.address"
                    for lane in range(1, 4)
                ]
                for role, path in workspace.items()
            }
            wait_for(
                lambda: all(
                    root_file_exists(path)
                    for paths in stripe_address_paths.values()
                    for path in paths
                ),
                240,
                "six auxiliary Tox route addresses",
            )
        principal_paths = {
            role: path / f"iotox-rendezvous/{role}.principal"
            for role, path in workspace.items()
        }
        wait_for(
            lambda: all(root_file_exists(path) for path in principal_paths.values()),
            180,
            "both guest stable-principal rendezvous records",
        )
        taps = [tap_observation("vm-iotoxc"), tap_observation("vm-iotoxd")]
        require(all(tap["master"] == "sandwurm-vm" for tap in taps), "a TAP is outside the prepared bridge")

        addresses = {role: read_root_file(path) for role, path in address_paths.items()}
        stripe_addresses = {
            role: [addresses[role]]
            + [read_root_file(path) for path in stripe_address_paths.get(role, [])]
            for role in ("client", "device")
        }
        principals = {
            role: read_root_file(path).strip()
            for role, path in principal_paths.items()
        }
        secondary_address = ""
        secondary_principal = ""
        if scenario in CONTENT_MULTI_SOURCE_SCENARIOS:
            secondary_address_path = (
                workspace["device"]
                / "iotox-rendezvous/device.secondary.address"
            )
            secondary_principal_path = (
                workspace["device"]
                / "iotox-rendezvous/device.secondary.principal"
            )
            wait_for(
                lambda: root_file_exists(secondary_address_path)
                and root_file_exists(secondary_principal_path),
                180,
                "secondary content source identity rendezvous",
            )
            secondary_address = read_root_file(secondary_address_path)
            secondary_principal = read_root_file(
                secondary_principal_path
            ).strip()
            require(
                ADDRESS_PATTERN.fullmatch(secondary_address) is not None
                and re.fullmatch(
                    r"[0-9A-Fa-f]{64}", secondary_principal
                )
                is not None,
                "secondary content source identity is invalid",
            )
        require(all(ADDRESS_PATTERN.fullmatch(value) for value in addresses.values()), "invalid guest Tox address")
        require(
            all(re.fullmatch(r"[0-9A-Fa-f]{64}", value) for value in principals.values()),
            "invalid guest stable principal",
        )
        require(addresses["client"][:64] != addresses["device"][:64], "guests share one Tox key")
        if scenario in CONTENT_MULTI_SOURCE_SCENARIOS:
            require(
                len(
                    {
                        addresses["client"][:64],
                        addresses["device"][:64],
                        secondary_address[:64],
                    }
                )
                == 3
                and len(
                    {
                        principals["client"].lower(),
                        principals["device"].lower(),
                        secondary_principal.lower(),
                    }
                )
                == 3,
                "multi-source content identities are not distinct",
            )
        if scenario in MULTI_ROUTE_SYNC_SCENARIOS:
            all_route_keys = [
                addresses[role][:64]
                for role in ("client", "device")
            ] + [
                address[:64]
                for values in multi_route_addresses.values()
                for address in values
            ]
            require(
                len(set(all_route_keys)) == 6,
                "multi-route sync pair does not have six distinct route keys",
            )
        if scenario in RATOX_STRIPE_SCENARIOS:
            require(
                all(
                    ADDRESS_PATTERN.fullmatch(address)
                    for values in stripe_addresses.values()
                    for address in values
                ),
                "invalid auxiliary Tox route address",
            )
            route_keys = [
                address[:64]
                for values in stripe_addresses.values()
                for address in values
            ]
            require(len(set(route_keys)) == 8, "striped pair does not have eight distinct route keys")
        for role, path in workspace.items():
            remote = addresses["device" if role == "client" else "client"]
            temporary = pair_root / f"{role}.peer.address"
            temporary.write_text(remote.rstrip("\n") + "\n", encoding="ascii")
            sudo("install", "-m", "0600", str(temporary), str(path / "iotox-input/peer.address"))
            temporary.unlink()
            if scenario in RATOX_STRIPE_SCENARIOS:
                remote_role = "device" if role == "client" else "client"
                for lane in range(1, 4):
                    temporary = pair_root / f"{role}.lane-{lane}.peer.address"
                    temporary.write_text(
                        stripe_addresses[remote_role][lane].rstrip("\n") + "\n",
                        encoding="ascii",
                    )
                    sudo(
                        "install",
                        "-m",
                        "0600",
                        str(temporary),
                        str(path / f"iotox-input/lane-{lane}.peer.address"),
                    )
                    temporary.unlink()
            if (
                scenario in RATOX_SCENARIOS
                or scenario in SYNC_SCENARIOS
                or scenario in MUTABLE_SCENARIOS
                or scenario in BIDIRECTIONAL_SYNC_SCENARIOS
                or scenario in AUTOMATION_SYNC_SCENARIOS
            ):
                remote_principal = principals[
                    "device" if role == "client" else "client"
                ]
                temporary = pair_root / f"{role}.peer.principal"
                temporary.write_text(remote_principal + "\n", encoding="ascii")
                sudo(
                    "install",
                    "-m",
                    "0600",
                    str(temporary),
                    str(path / "iotox-input/peer.principal"),
                )
                temporary.unlink()

        if scenario in CONTENT_MULTI_SOURCE_SCENARIOS:
            for name, value in (
                ("secondary.peer.address", secondary_address),
                ("secondary.peer.principal", secondary_principal),
            ):
                temporary = pair_root / f"client.{name}"
                temporary.write_text(value.rstrip("\n") + "\n", encoding="ascii")
                sudo(
                    "install",
                    "-m",
                    "0600",
                    str(temporary),
                    str(workspace["client"] / f"iotox-input/{name}"),
                )
                temporary.unlink()

        if scenario in BIDIRECTIONAL_SYNC_SCENARIOS:
            stopped_paths = {
                role: path
                / f"iotox-rendezvous/{role}.sync-bidirectional-stopped"
                for role, path in workspace.items()
            }
            failure_paths = {
                role: path / f"iotox-rendezvous/{role}.failure"
                for role, path in workspace.items()
            }
            try:
                wait_for(
                    lambda: all(
                        root_file_exists(path)
                        for path in stopped_paths.values()
                    )
                    or any(
                        root_file_exists(path)
                        for path in failure_paths.values()
                    )
                    or any(
                        process.poll() is not None
                        for process in processes.values()
                    ),
                    1000,
                    "both bidirectional sync daemons to stop",
                )
            except RuntimeError as error:
                progress = {}
                for role, path in workspace.items():
                    progress_path = (
                        path
                        / f"iotox-rendezvous/{role}.sync-bidirectional-progress"
                    )
                    progress[role] = (
                        read_root_file(progress_path).strip().replace("\n", ",")
                        if root_file_exists(progress_path)
                        else "no-progress-record"
                    )
                raise RuntimeError(f"{error}; progress: {progress}") from error
            require(
                all(root_file_exists(path) for path in stopped_paths.values()),
                "a guest failed before the bidirectional offline barrier: "
                + "; ".join(
                    f"{role}={read_root_file(path).strip()}"
                    for role, path in failure_paths.items()
                    if root_file_exists(path)
                ),
            )
            for role, path in workspace.items():
                deliver_guest_input(
                    pair_root,
                    path,
                    role,
                    "sync-bidirectional-restart",
                )

        if (
            scenario in RATOX_SCENARIOS
            and scenario not in POST_SYNC_RATOX_SCENARIOS
        ):
            if scenario in RATOX_STRIPE_SCENARIOS:
                stripe_ready_paths = {
                    role: path
                    / f"iotox-rendezvous/{role}.stripe-routes-ready"
                    for role, path in workspace.items()
                }
                try:
                    wait_for(
                        lambda: all(
                            root_file_exists(path)
                            for path in stripe_ready_paths.values()
                        ),
                        240,
                        "both guests' four authenticated Tox routes",
                    )
                except RuntimeError as error:
                    progress = {}
                    for role, path in workspace.items():
                        progress_path = (
                            path / f"iotox-rendezvous/{role}.stripe-progress"
                        )
                        progress[role] = (
                            read_root_file(progress_path).strip().replace("\n", ",")
                            if root_file_exists(progress_path)
                            else "no-confirmed-routes"
                        )
                    raise RuntimeError(
                        f"{error}; content-free convergence progress: {progress}"
                    ) from error
            ready_path = workspace["device"] / "iotox-rendezvous/device.ratox-ready"
            wait_for(
                lambda: root_file_exists(ready_path),
                240,
                "device Ratox authority/profile activation",
            )
            if scenario in RATOX_BULK_SCENARIOS:
                for role in ("client", "device"):
                    command_file = pair_root / f"{role}.ratox-bulk-start"
                    command_file.write_text("ratox-bulk-start=1\n", encoding="ascii")
                    sudo(
                        "install",
                        "-m",
                        "0600",
                        str(command_file),
                        str(workspace[role] / "iotox-input/ratox-bulk-start"),
                    )
                    command_file.unlink()
                bulk_active = (
                    workspace["client"]
                    / "iotox-rendezvous/client.ratox-bulk-active"
                )
                wait_for(
                    lambda: root_file_exists(bulk_active),
                    240,
                    "client Ratox bulk admission",
                )
                if scenario in RATOX_LIVE_LOSS_SCENARIOS:
                    command_file = pair_root / "device.stripe-live-fault"
                    command_file.write_text("stripe-live-fault=1\n", encoding="ascii")
                    sudo(
                        "install",
                        "-m",
                        "0600",
                        str(command_file),
                        str(
                            workspace["device"]
                            / "iotox-input/stripe-live-fault"
                        ),
                    )
                    command_file.unlink()
                    faulted_path = (
                        workspace["device"]
                        / "iotox-rendezvous/device.stripe-live-faulted"
                    )
                    wait_for(
                        lambda: root_file_exists(faulted_path),
                        120,
                        "device live auxiliary-route stop",
                    )
                    loss_observed_path = (
                        workspace["client"]
                        / "iotox-rendezvous/client.stripe-live-loss-observed"
                    )
                    wait_for(
                        lambda: root_file_exists(loss_observed_path),
                        240,
                        "client auxiliary-route offline and transfer purge",
                    )
            command_file = pair_root / "device.ratox-measure-start"
            command_file.write_text("ratox-measure-start=1\n", encoding="ascii")
            sudo(
                "install",
                "-m",
                "0600",
                str(command_file),
                str(
                    workspace["device"]
                    / "iotox-input/ratox-measure-start"
                ),
            )
            command_file.unlink()
            resource_started = (
                workspace["device"]
                / "iotox-rendezvous/device.ratox-resource-started"
            )
            wait_for(
                lambda: root_file_exists(resource_started),
                60,
                "device Ratox resource interval start",
            )
            command_file = pair_root / "client.ratox-start"
            command_file.write_text("ratox-start=1\n", encoding="ascii")
            sudo(
                "install",
                "-m",
                "0600",
                str(command_file),
                str(workspace["client"] / "iotox-input/ratox-start"),
            )
            command_file.unlink()
            captured_path = (
                workspace["client"]
                / "iotox-rendezvous/client.ratox-terminal-captured"
            )
            client_failure_path = (
                workspace["client"] / "iotox-rendezvous/client.failure"
            )
            if scenario == "ratox-route-impairment":
                progress_path = (
                    workspace["client"]
                    / "iotox-rendezvous/client.ratox-terminal-progress"
                )
                try:
                    wait_for(
                        lambda: ratox_progress_samples(progress_path)
                        >= RATOX_IMPAIRMENT_BASELINE_END
                        or root_file_exists(client_failure_path),
                        240,
                        "Ratox baseline phase",
                    )
                except RuntimeError as error:
                    readiness_path = (
                        workspace["client"]
                        / "iotox-rendezvous/client.ratox-controller-readiness"
                    )
                    readiness = (
                        read_root_file(readiness_path).strip().replace("\n", ",")
                        if root_file_exists(readiness_path)
                        else "not-published"
                    )
                    raise RuntimeError(
                        f"{error}; controller-readiness={readiness}"
                    ) from error
                require(
                    not root_file_exists(client_failure_path),
                    "client Ratox probe failed before impairment",
                )
                impairment_started_ns = time.monotonic_ns()
                links_blocked = True
                for tap in ("vm-iotoxc", "vm-iotoxd"):
                    sudo(
                        str(HOST_BIN / "tc"),
                        "qdisc",
                        "replace",
                        "dev",
                        tap,
                        "root",
                        "netem",
                        "limit",
                        "1000",
                        "delay",
                        f"{RATOX_IMPAIRMENT_DELAY_MS}ms",
                        f"{RATOX_IMPAIRMENT_JITTER_MS}ms",
                        "distribution",
                        "normal",
                        "loss",
                        "random",
                        f"{RATOX_IMPAIRMENT_LOSS_PERCENT}%",
                        "seed",
                        str(RATOX_IMPAIRMENT_SEEDS[tap]),
                    )
                deliver_guest_input(
                    pair_root,
                    workspace["client"],
                    "client",
                    f"ratox-release-after-{RATOX_IMPAIRMENT_BASELINE_END}",
                )
                wait_for(
                    lambda: ratox_progress_samples(progress_path)
                    >= RATOX_IMPAIRMENT_END
                    or root_file_exists(client_failure_path),
                    600,
                    "Ratox impaired phase",
                )
                require(
                    not root_file_exists(client_failure_path),
                    "client Ratox probe failed under impairment",
                )
                impairment_qdiscs = [
                    ratox_impairment_observation(tap)
                    for tap in ("vm-iotoxc", "vm-iotoxd")
                ]
                require(
                    all(
                        observation["packets"] > 0
                        and observation["drops"] > 0
                        for observation in impairment_qdiscs
                    ),
                    "Ratox impairment did not exercise delay/loss on both TAPs",
                )
                for tap in ("vm-iotoxc", "vm-iotoxd"):
                    sudo(str(HOST_BIN / "tc"), "qdisc", "del", "dev", tap, "root")
                links_blocked = False
                deliver_guest_input(
                    pair_root,
                    workspace["client"],
                    "client",
                    f"ratox-release-after-{RATOX_IMPAIRMENT_END}",
                )
                impairment_ended_ns = time.monotonic_ns()
                ratox_route_impairment = {
                    "schema": "iotox-ratox-route-impairment-v1",
                    "sample_count": RATOX_IMPAIRMENT_SAMPLES,
                    "baseline_end_ordinal": RATOX_IMPAIRMENT_BASELINE_END,
                    "impairment_end_ordinal": RATOX_IMPAIRMENT_END,
                    "recovery_sample_count": (
                        RATOX_IMPAIRMENT_SAMPLES - RATOX_IMPAIRMENT_END
                    ),
                    "delay_ms": RATOX_IMPAIRMENT_DELAY_MS,
                    "jitter_ms": RATOX_IMPAIRMENT_JITTER_MS,
                    "loss_percent": RATOX_IMPAIRMENT_LOSS_PERCENT,
                    "active_wall_ms": (
                        impairment_ended_ns - impairment_started_ns
                    ) // 1_000_000,
                    "qdiscs": impairment_qdiscs,
                }
                (pair_root / "ratox-route-impairment.json").write_text(
                    json.dumps(ratox_route_impairment, indent=2, sort_keys=True)
                    + "\n",
                    encoding="utf-8",
                )
            elif scenario == "ratox-route-actual-tor-soak":
                require(tor_node is not None, "actual-Tor node disappeared")
                progress_path = (
                    workspace["client"]
                    / "iotox-rendezvous/client.ratox-terminal-progress"
                )
                soak_started_ns = time.monotonic_ns()
                churns: list[dict[str, object]] = []
                for role, ordinal in RATOX_ACTUAL_TOR_SOAK_CHURNS:
                    wait_for(
                        lambda ordinal=ordinal: ratox_progress_samples(progress_path)
                        >= ordinal
                        or root_file_exists(client_failure_path),
                        300,
                        f"Ratox actual-Tor soak checkpoint {ordinal}",
                    )
                    require(
                        not root_file_exists(client_failure_path),
                        f"client Ratox probe failed before churn {ordinal}",
                    )
                    churns.append(
                        close_actual_tor_guest_circuit(
                            tor_instances[role], tor_node, ordinal
                        )
                    )
                    deliver_guest_input(
                        pair_root,
                        workspace["client"],
                        "client",
                        f"ratox-release-after-{ordinal}",
                    )
                actual_tor_ratox_churn = {
                    "schema": "iotox-actual-tor-ratox-churn-v3",
                    "sample_count": RATOX_ACTUAL_TOR_SOAK_SAMPLES,
                    "sample_interval_ms": RATOX_ACTUAL_TOR_SOAK_INTERVAL_MS,
                    "churn_ordinals": [
                        ordinal for _, ordinal in RATOX_ACTUAL_TOR_SOAK_CHURNS
                    ],
                    "churns": churns,
                    "iotox_daemon_restarts": 0,
                    "tor_process_restarts": 0,
                    "active_wall_ns": 0,
                    "started_ns": soak_started_ns,
                    "completed_ns": 0,
                }
            elif scenario in {
                "ratox-route-loss",
                "ratox-cli-reconnect",
                "ratox-cli-reconnect-repeated",
                "ratox-route-actual-tor-loss",
                "ratox-route-actual-tor-adversary",
            }:
                attached_path = (
                    workspace["client"]
                    / "iotox-rendezvous/client.ratox-route-loss-attached"
                )
                wait_for(
                    lambda: root_file_exists(attached_path)
                    or root_file_exists(client_failure_path),
                    240,
                    "Ratox route-loss initial attachment",
                )
                require(
                    not root_file_exists(client_failure_path),
                    "client Ratox probe failed before route loss",
                )
                loss_started_ns = time.monotonic_ns()
                if actual_tor_ratox_adversary:
                    require(tor_node is not None, "actual-Tor node disappeared")
                    client_tor = tor_instances["client"]
                    client_adversary = tor_adversaries["client"]
                    tor_process = client_tor["process"]
                    adversary_process = client_adversary["process"]
                    require(
                        isinstance(tor_process, subprocess.Popen)
                        and isinstance(adversary_process, subprocess.Popen),
                        "adversarial boundary process types drifted",
                    )
                    tor_pid = tor_process.pid
                    tor_control_inode = (
                        Path(client_tor["root"]) / "control.sock"
                    ).stat().st_ino
                    adversary_pid = adversary_process.pid
                    listener_inode = str(client_adversary["listener_inode"])
                    hold_path = Path(client_adversary["hold_path"])
                    require(not hold_path.exists(), "adversarial hold was pre-existing")
                    loss_started_ns = time.monotonic_ns()
                    hold_path.write_text("hold\n", encoding="ascii")
                    os.chmod(hold_path, 0o600)
                    wait_for(
                        lambda: any(
                            json.loads(line).get("event") == "relay-hold"
                            for line in Path(client_adversary["audit_path"])
                            .read_text(encoding="ascii")
                            .splitlines()
                        )
                        or adversary_process.poll() is not None,
                        10,
                        "client adversarial relay hold",
                    )
                    require(
                        adversary_process.poll() is None,
                        "client adversary exited during relay hold",
                    )
                    listener_reachable_during_hold = tcp_port_open(
                        HOST_BRIDGE_ADDRESS, ACTUAL_TOR_SOCKS_PORTS["client"]
                    )
                    socks5_connect_probe(
                        (HOST_BRIDGE_ADDRESS, ACTUAL_TOR_SOCKS_PORTS["client"]),
                        (str(tor_node["address"]), int(tor_node["port"])),
                    )
                    socks_connect_during_hold = True
                elif actual_tor_ratox_loss:
                    require(tor_node is not None, "actual-Tor node disappeared")
                    client_tor = tor_instances["client"]
                    tor_pre_loss_evidence = actual_tor_role_evidence(
                        pair_root, client_tor, tor_node, "pre-loss"
                    )
                    old_process = client_tor["process"]
                    require(
                        isinstance(old_process, subprocess.Popen),
                        "client Tor process type drifted",
                    )
                    old_pid = old_process.pid
                    loss_started_ns = time.monotonic_ns()
                    returncode = kill_process_group(old_process, "client Tor")
                    client_tor["log"].close()
                    old_control = Path(client_tor["root"]) / "control.sock"
                    old_control.unlink(missing_ok=True)
                else:
                    links_blocked = True
                    for tap in ("vm-iotoxc", "vm-iotoxd"):
                        sudo(
                            str(HOST_BIN / "tc"),
                            "qdisc",
                            "replace",
                            "dev",
                            tap,
                            "root",
                            "netem",
                            "limit",
                            "1000",
                            "loss",
                            "random",
                            "100%",
                            "seed",
                            str(RATOX_ROUTE_LOSS_SEEDS[tap]),
                        )
                deliver_guest_input(
                    pair_root,
                    workspace["client"],
                    "client",
                    "ratox-route-loss-active",
                )
                heartbeat_missed_path = (
                    workspace["client"]
                    / "iotox-rendezvous/client.ratox-route-loss-heartbeat-missed"
                )
                wait_for(
                    lambda: root_file_exists(heartbeat_missed_path)
                    or root_file_exists(client_failure_path),
                    30,
                    "Ratox heartbeat loss before carrier loss",
                )
                require(
                    not root_file_exists(client_failure_path),
                    "client Ratox probe failed at heartbeat loss",
                )
                heartbeat_missed_ns = time.monotonic_ns()
                offline_path = (
                    workspace["client"]
                    / "iotox-rendezvous/client.ratox-route-loss-offline"
                )
                wait_for(
                    lambda: root_file_exists(offline_path)
                    or root_file_exists(client_failure_path),
                    240,
                    "Ratox authoritative route loss",
                )
                require(
                    not root_file_exists(client_failure_path),
                    "client Ratox probe failed before authoritative offline",
                )
                controller_offline_ns = time.monotonic_ns()
                deliver_guest_input(
                    pair_root,
                    workspace["device"],
                    "device",
                    "ratox-loss-snapshot",
                )
                host_snapshot_path = (
                    workspace["device"]
                    / "iotox-rendezvous/device.ratox-loss-snapshot-ready"
                )
                wait_for(
                    lambda: root_file_exists(host_snapshot_path)
                    or root_file_exists(
                        workspace["device"] / "iotox-rendezvous/device.failure"
                    ),
                    60,
                    "detached Ratox host snapshot",
                )
                require(
                    root_file_exists(host_snapshot_path),
                    "device did not retain a detached Ratox host session",
                )
                loss_qdiscs = []
                if actual_tor_ratox_adversary:
                    hold_path = Path(tor_adversaries["client"]["hold_path"])
                    require(hold_path.is_file(), "adversarial hold disappeared early")
                    hold_path.unlink()
                    released_ns = time.monotonic_ns()
                    client_tor = tor_instances["client"]
                    client_adversary = tor_adversaries["client"]
                    require(
                        client_tor["process"].poll() is None
                        and client_tor["process"].pid == tor_pid
                        and (Path(client_tor["root"]) / "control.sock").stat().st_ino
                        == tor_control_inode,
                        "Tor identity changed across adversarial boundary hold",
                    )
                    require(
                        client_adversary["process"].poll() is None
                        and client_adversary["process"].pid == adversary_pid,
                        "interposer identity changed across its relay hold",
                    )
                    listeners = [
                        record
                        for record in process_inet_sockets(adversary_pid, "tcp")
                        if record["local_address"] == HOST_BRIDGE_ADDRESS
                        and record["local_port"]
                        == ACTUAL_TOR_SOCKS_PORTS["client"]
                        and record["state"] == "0A"
                    ]
                    require(
                        len(listeners) == 1
                        and listeners[0]["inode"] == listener_inode,
                        "interposer listener identity changed across its hold",
                    )
                    actual_tor_adversarial_boundary = {
                        "schema": "iotox-actual-tor-adversarial-boundary-v1",
                        "role": "client",
                        "fault_kind": "established-relay-byte-hold",
                        "hold_file_mode": "host-owned-presence",
                        "hold_started_ns": loss_started_ns,
                        "hold_released_ns": released_ns,
                        "hold_active_ns": released_ns - loss_started_ns,
                        "heartbeat_missed_after_hold_ns": (
                            heartbeat_missed_ns - loss_started_ns
                        ),
                        "controller_offline_after_hold_ns": (
                            controller_offline_ns - loss_started_ns
                        ),
                        "listener_reachable_during_hold": (
                            listener_reachable_during_hold
                        ),
                        "socks_connect_succeeded_during_hold": (
                            socks_connect_during_hold
                        ),
                        "tor_process_pid": tor_pid,
                        "tor_control_socket_inode": tor_control_inode,
                        "interposer_process_pid": adversary_pid,
                        "interposer_listener_inode": listener_inode,
                        "tor_process_restarts": 0,
                        "interposer_process_restarts": 0,
                        "iotox_daemon_restarts": 0,
                    }
                elif actual_tor_ratox_loss:
                    restart_started_ns = time.monotonic_ns()
                    recovered_client_tor = start_pair_tor(
                        pair_root, "client", "recovered"
                    )
                    require(
                        recovered_client_tor["tor_sha256"]
                        == client_tor["tor_sha256"]
                        and recovered_client_tor["tor_version"]
                        == client_tor["tor_version"],
                        "recovered client Tor binary identity changed",
                    )
                    tor_instances["client"] = recovered_client_tor
                    restart_completed_ns = time.monotonic_ns()
                    actual_tor_process_loss = {
                        "schema": "iotox-actual-tor-ratox-process-loss-v1",
                        "role": "client",
                        "signal": signal.SIGKILL,
                        "returncode": returncode,
                        "pre_loss_process_pid": old_pid,
                        "pre_loss_control_socket_inode": tor_pre_loss_evidence[
                            "control_socket_inode"
                        ],
                        "heartbeat_missed_after_loss_ns": (
                            heartbeat_missed_ns - loss_started_ns
                        ),
                        "controller_offline_after_loss_ns": (
                            controller_offline_ns - loss_started_ns
                        ),
                        "restart_bootstrap_ns": (
                            restart_completed_ns - restart_started_ns
                        ),
                        "iotox_daemon_restarts": 0,
                    }
                    loss_path = pair_root / "actual-tor-process-loss.json"
                    loss_path.write_text(
                        json.dumps(
                            actual_tor_process_loss, indent=2, sort_keys=True
                        )
                        + "\n",
                        encoding="utf-8",
                    )
                else:
                    loss_qdiscs = [
                        ratox_route_loss_observation(tap)
                        for tap in ("vm-iotoxc", "vm-iotoxd")
                    ]
                    require(
                        all(
                            observation["drops"] > 0
                            for observation in loss_qdiscs
                        ),
                        "Ratox total loss did not drop traffic on both TAPs",
                    )
                    for tap in ("vm-iotoxc", "vm-iotoxd"):
                        sudo(
                            str(HOST_BIN / "tc"),
                            "qdisc",
                            "del",
                            "dev",
                            tap,
                            "root",
                        )
                    links_blocked = False
                recovery_started_ns = time.monotonic_ns()
                deliver_guest_input(
                    pair_root,
                    workspace["client"],
                    "client",
                    "ratox-route-loss-recover",
                )
                repeated_interruption: dict[str, object] | None = None
                if ratox_cli_reconnect_repeated:
                    recovered_once_path = (
                        workspace["client"]
                        / "iotox-rendezvous/client.ratox-route-loss-recovered-1"
                    )
                    wait_for(
                        lambda: root_file_exists(recovered_once_path)
                        or root_file_exists(client_failure_path),
                        240,
                        "first production CLI Ratox recovery",
                    )
                    require(
                        not root_file_exists(client_failure_path),
                        "client Ratox probe failed before repeated route loss",
                    )
                    second_loss_started_ns = time.monotonic_ns()
                    links_blocked = True
                    for tap in ("vm-iotoxc", "vm-iotoxd"):
                        sudo(
                            str(HOST_BIN / "tc"),
                            "qdisc",
                            "replace",
                            "dev",
                            tap,
                            "root",
                            "netem",
                            "limit",
                            "1000",
                            "loss",
                            "random",
                            "100%",
                            "seed",
                            str(RATOX_ROUTE_LOSS_SEEDS[tap] + 1000),
                        )
                    deliver_guest_input(
                        pair_root,
                        workspace["client"],
                        "client",
                        "ratox-route-loss-active-2",
                    )
                    second_heartbeat_path = (
                        workspace["client"]
                        / "iotox-rendezvous/"
                        "client.ratox-route-loss-heartbeat-missed-2"
                    )
                    wait_for(
                        lambda: root_file_exists(second_heartbeat_path)
                        or root_file_exists(client_failure_path),
                        30,
                        "second Ratox heartbeat loss before carrier loss",
                    )
                    require(
                        not root_file_exists(client_failure_path),
                        "client Ratox probe failed at second heartbeat loss",
                    )
                    second_heartbeat_ns = time.monotonic_ns()
                    second_offline_path = (
                        workspace["client"]
                        / "iotox-rendezvous/client.ratox-route-loss-offline-2"
                    )
                    wait_for(
                        lambda: root_file_exists(second_offline_path)
                        or root_file_exists(client_failure_path),
                        240,
                        "second Ratox authoritative route loss",
                    )
                    require(
                        not root_file_exists(client_failure_path),
                        "client Ratox probe failed before second authoritative offline",
                    )
                    second_offline_ns = time.monotonic_ns()
                    second_qdiscs = [
                        ratox_route_loss_observation(tap, 1000)
                        for tap in ("vm-iotoxc", "vm-iotoxd")
                    ]
                    require(
                        all(
                            observation["drops"] > 0
                            for observation in second_qdiscs
                        ),
                        "second Ratox total loss did not drop traffic on both TAPs",
                    )
                    for tap in ("vm-iotoxc", "vm-iotoxd"):
                        sudo(
                            str(HOST_BIN / "tc"),
                            "qdisc",
                            "del",
                            "dev",
                            tap,
                            "root",
                        )
                    links_blocked = False
                    second_recovery_ns = time.monotonic_ns()
                    deliver_guest_input(
                        pair_root,
                        workspace["client"],
                        "client",
                        "ratox-route-loss-recover-2",
                    )
                    recovered_twice_path = (
                        workspace["client"]
                        / "iotox-rendezvous/client.ratox-route-loss-recovered-2"
                    )
                    wait_for(
                        lambda: root_file_exists(recovered_twice_path)
                        or root_file_exists(client_failure_path),
                        240,
                        "second production CLI Ratox recovery",
                    )
                    require(
                        not root_file_exists(client_failure_path),
                        "client Ratox probe failed during second recovery",
                    )
                    repeated_interruption = {
                        "ordinal": 2,
                        "heartbeat_missed_after_loss_ms": (
                            second_heartbeat_ns - second_loss_started_ns
                        )
                        // 1_000_000,
                        "controller_offline_after_loss_ms": (
                            second_offline_ns - second_loss_started_ns
                        )
                        // 1_000_000,
                        "active_wall_ms": (
                            second_recovery_ns - second_loss_started_ns
                        )
                        // 1_000_000,
                        "qdiscs": second_qdiscs,
                    }
                ratox_route_loss = {
                    "schema": (
                        "iotox-ratox-route-loss-v3"
                        if actual_tor_ratox_adversary
                        else "iotox-ratox-route-loss-v2"
                        if actual_tor_ratox_loss
                        else "iotox-ratox-route-loss-v5"
                        if ratox_cli_reconnect_repeated
                        else "iotox-ratox-route-loss-v4"
                        if ratox_cli_reconnect
                        else "iotox-ratox-route-loss-v1"
                    ),
                    **(
                        {"fault_kind": "actual-tor-established-byte-hold"}
                        if actual_tor_ratox_adversary
                        else {"fault_kind": "actual-tor-process-sigkill"}
                        if actual_tor_ratox_loss
                        else {
                            "fault_kind": "netem-total-loss",
                            "controller_kind": "production-cli-reconnect",
                        }
                        if ratox_cli_reconnect
                        else {"loss_percent": 100}
                    ),
                    "heartbeat_timeout_ms": (
                        3000 if ratox_cli_reconnect else 2000
                    ),
                    "heartbeat_missed_after_loss_ms": (
                        heartbeat_missed_ns - loss_started_ns
                    ) // 1_000_000,
                    "controller_offline_after_loss_ms": (
                        controller_offline_ns - loss_started_ns
                    ) // 1_000_000,
                    "active_wall_ms": (
                        recovery_started_ns - loss_started_ns
                    ) // 1_000_000,
                    "qdiscs": loss_qdiscs,
                    "detached_host_snapshot": True,
                }
                if repeated_interruption is not None:
                    ratox_route_loss["interruption_count"] = 2
                    ratox_route_loss["interruptions"] = [
                        {
                            "ordinal": 1,
                            "heartbeat_missed_after_loss_ms": (
                                heartbeat_missed_ns - loss_started_ns
                            )
                            // 1_000_000,
                            "controller_offline_after_loss_ms": (
                                controller_offline_ns - loss_started_ns
                            )
                            // 1_000_000,
                            "active_wall_ms": (
                                recovery_started_ns - loss_started_ns
                            )
                            // 1_000_000,
                            "qdiscs": loss_qdiscs,
                        },
                        repeated_interruption,
                    ]
                (pair_root / "ratox-route-loss.json").write_text(
                    json.dumps(ratox_route_loss, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
            wait_for(
                lambda: root_file_exists(captured_path)
                or root_file_exists(client_failure_path),
                900
                if matrix_bulk
                else 420
                if scenario
                in {
                    "ratox-route-loss",
                    "ratox-cli-reconnect",
                    "ratox-cli-reconnect-repeated",
                    "ratox-route-actual-tor-loss",
                    "ratox-route-actual-tor-adversary",
                }
                else 600
                if scenario == "ratox-route-actual-tor-soak"
                else 240,
                "client Ratox terminal capture or explicit failure",
            )
            if root_file_exists(client_failure_path):
                detail = read_root_file(client_failure_path).strip()
                probe_error_path = (
                    workspace["client"]
                    / "iotox-rendezvous/client.ratox-terminal-probe.stderr"
                )
                if root_file_exists(probe_error_path):
                    detail += "\nprobe-stderr=" + read_root_file(
                        probe_error_path
                    ).strip()
                raise RuntimeError(
                    "client Ratox terminal probe failed:\n" + detail
                )
            if actual_tor_ratox_soak:
                soak_completed_ns = time.monotonic_ns()
                actual_tor_ratox_churn["completed_ns"] = soak_completed_ns
                actual_tor_ratox_churn["active_wall_ns"] = (
                    soak_completed_ns - int(actual_tor_ratox_churn["started_ns"])
                )
                churn_lifecycle_relative = (
                    "client/live/workspace-export/guest-receipts/iotox/"
                    "ratox-circuit-churn-probe.json"
                )
                churn_lifecycle_path = pair_root / churn_lifecycle_relative
                churn_lifecycle_text = read_root_file(churn_lifecycle_path)
                churn_lifecycle = json.loads(churn_lifecycle_text)
                require(
                    isinstance(churn_lifecycle, dict)
                    and churn_lifecycle.get("schema")
                    == "iotox-ratox-circuit-churn-probe-v2"
                    and churn_lifecycle.get("status") == "passed"
                    and len(churn_lifecycle.get("transitions", [])) == 2,
                    "Ratox circuit-churn lifecycle is invalid",
                )
                actual_tor_ratox_churn["controller_lifecycle_path"] = (
                    churn_lifecycle_relative
                )
                actual_tor_ratox_churn["controller_lifecycle_sha256"] = (
                    hashlib.sha256(
                        churn_lifecycle_text.encode("utf-8")
                    ).hexdigest()
                )
                (pair_root / "actual-tor-ratox-churn.json").write_text(
                    json.dumps(
                        actual_tor_ratox_churn, indent=2, sort_keys=True
                    )
                    + "\n",
                    encoding="utf-8",
                )
            if scenario in RATOX_LIVE_LOSS_SCENARIOS:
                command_file = pair_root / "device.stripe-live-recover"
                command_file.write_text("stripe-live-recover=1\n", encoding="ascii")
                sudo(
                    "install",
                    "-m",
                    "0600",
                    str(command_file),
                    str(
                        workspace["device"]
                        / "iotox-input/stripe-live-recover"
                    ),
                )
                command_file.unlink()
                recovered_paths = {
                    role: path
                    / f"iotox-rendezvous/{role}.stripe-live-recovered"
                    for role, path in workspace.items()
                }
                wait_for(
                    lambda: all(
                        root_file_exists(path)
                        for path in recovered_paths.values()
                    ),
                    240,
                    "both guests' recovered auxiliary route",
                )
            complete_path = (
                workspace["client"] / "iotox-rendezvous/client.ratox-complete"
            )
            wait_for(
                lambda: root_file_exists(complete_path),
                240,
                "client Ratox bulk completion"
                if scenario in RATOX_BULK_SCENARIOS
                else "client Ratox completion",
            )
            command_file = pair_root / "device.ratox-finished"
            command_file.write_text("ratox-finished=1\n", encoding="ascii")
            sudo(
                "install",
                "-m",
                "0600",
                str(command_file),
                str(workspace["device"] / "iotox-input/ratox-finished"),
            )
            command_file.unlink()
            if scenario in RATOX_STRIPE_SCENARIOS:
                evidence_ready_paths = {
                    role: path
                    / f"iotox-rendezvous/{role}.stripe-evidence-ready"
                    for role, path in workspace.items()
                }
                wait_for(
                    lambda: all(
                        root_file_exists(path)
                        for path in evidence_ready_paths.values()
                    ),
                    120,
                    "both guests' live stripe-route evidence",
                )
                for role, path in workspace.items():
                    command_file = pair_root / f"{role}.stripe-evidence-release"
                    command_file.write_text(
                        "stripe-evidence-release=1\n", encoding="ascii"
                    )
                    sudo(
                        "install",
                        "-m",
                        "0600",
                        str(command_file),
                        str(path / "iotox-input/stripe-evidence-release"),
                    )
                    command_file.unlink()

        if scenario in SYNC_SCENARIOS:
            if scenario == "sync-tree-route-startup-order":
                def wait_for_startup_markers(
                    marker: str, timeout: float, label: str
                ) -> None:
                    paths = {
                        role: path / f"iotox-rendezvous/{role}.{marker}"
                        for role, path in workspace.items()
                    }
                    wait_for(
                        lambda: all(
                            root_file_exists(path) for path in paths.values()
                        )
                        or any(
                            process.poll() is not None
                            for process in processes.values()
                        ),
                        timeout,
                        label,
                    )
                    require(
                        all(root_file_exists(path) for path in paths.values()),
                        f"a guest exited before {label}",
                    )

                wait_for_startup_markers(
                    "startup-sync-restart-ready",
                    600,
                    "both guests' rolling sync-restart barrier",
                )
                deliver_guest_input(
                    pair_root,
                    workspace["client"],
                    "client",
                    "startup-sync-restart-release",
                )
                client_sync_restarted = (
                    workspace["client"]
                    / "iotox-rendezvous/client.startup-sync-restarted"
                )
                wait_for(
                    lambda: root_file_exists(client_sync_restarted)
                    or processes["client"].poll() is not None,
                    60,
                    "client rolling sync restart",
                )
                require(
                    root_file_exists(client_sync_restarted),
                    "client exited during rolling sync restart",
                )
                deliver_guest_input(
                    pair_root,
                    workspace["device"],
                    "device",
                    "startup-sync-restart-release",
                )
                device_sync_restarted = (
                    workspace["device"]
                    / "iotox-rendezvous/device.startup-sync-restarted"
                )
                wait_for(
                    lambda: root_file_exists(device_sync_restarted)
                    or processes["device"].poll() is not None,
                    60,
                    "device rolling sync restart",
                )
                require(
                    root_file_exists(device_sync_restarted),
                    "device exited during rolling sync restart",
                )

                wait_for_startup_markers(
                    "startup-phase-one-ready",
                    180,
                    "both guests' first route-readiness permutation",
                )
                deliver_guest_input(
                    pair_root,
                    workspace["client"],
                    "client",
                    "startup-phase-two-release",
                )
                client_phase_two = (
                    workspace["client"]
                    / "iotox-rendezvous/client.startup-phase-two-restarted"
                )
                wait_for(
                    lambda: root_file_exists(client_phase_two)
                    or processes["client"].poll() is not None,
                    60,
                    "client second readiness restart",
                )
                require(
                    root_file_exists(client_phase_two),
                    "client exited during second readiness restart",
                )
                deliver_guest_input(
                    pair_root,
                    workspace["device"],
                    "device",
                    "startup-phase-two-release",
                )
                device_phase_two = (
                    workspace["device"]
                    / "iotox-rendezvous/device.startup-phase-two-restarted"
                )
                wait_for(
                    lambda: root_file_exists(device_phase_two)
                    or processes["device"].poll() is not None,
                    60,
                    "device second readiness restart",
                )
                require(
                    root_file_exists(device_phase_two),
                    "device exited during second readiness restart",
                )
            authority_ready = {
                role: path
                / f"iotox-rendezvous/{role}.sync-authority-ready"
                for role, path in workspace.items()
            }
            authority_failures = {
                role: path / f"iotox-rendezvous/{role}.failure"
                for role, path in workspace.items()
            }
            authority_progress = {
                role: path
                / f"iotox-rendezvous/{role}.sync-authority-progress"
                for role, path in workspace.items()
            }
            authority_timeout = (
                900
                if scenario in CONTENT_MULTI_SOURCE_SCENARIOS
                else (
                    480
                    if route == "forced-tcp"
                    and scenario
                    in {
                        "sync-content",
                        "sync-content-same-source-lanes",
                        *CONTENT_RESTART_SCENARIOS,
                        "sync-content-lane-science",
                        "sync-content-lane-science-reverse",
                        "sync-content-ratox-latency-science",
                        "sync-content-ratox-cap-2-sla",
                        "sync-content-ratox-post-bulk-admission",
                        "update-service",
                    }
                    else 240
                )
            )
            wait_for(
                lambda: all(
                    root_file_exists(path) for path in authority_ready.values()
                )
                or any(
                    root_file_exists(path)
                    for path in authority_failures.values()
                )
                or any(process.poll() is not None for process in processes.values()),
                authority_timeout,
                "both guests' v3 synchronization authority or explicit failure",
            )
            authority_failure_detail = {
                role: read_root_file(path).strip()
                for role, path in authority_failures.items()
                if root_file_exists(path)
            }
            authority_progress_detail = {
                role: read_root_file(path).strip()
                for role, path in authority_progress.items()
                if root_file_exists(path)
            }
            require(
                all(root_file_exists(path) for path in authority_ready.values()),
                "a synchronization guest failed before v3 authority readiness: "
                f"failures={authority_failure_detail} "
                f"progress={authority_progress_detail}",
            )
            published_path = (
                workspace["device"]
                / "iotox-rendezvous/device.sync-published"
            )
            wait_for(
                lambda: root_file_exists(published_path),
                240,
                "device signed synchronization publication",
            )
            published = read_root_file(published_path)
            publication_pattern = (
                r"generation=1\n"
                r"head-record=[0-9a-f]{64}\n"
                r"artifact-sha256=[0-9a-f]{64}\n"
                r"manifest-sha256=[0-9a-f]{64}\n"
                rf"artifact-bytes={SYNC_SCENARIOS[scenario]}\n"
                r"manifest-bytes=[1-9][0-9]*\n"
            )
            if scenario in SYNC_TREE_SCENARIOS:
                tree_content_bytes = (
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
                    else 4_194_389
                )
                publication_pattern += (
                    r"tree-directories=3\n"
                    r"tree-files=3\n"
                    rf"tree-content-bytes={tree_content_bytes}\n"
                    r"tree-payload-sha256=[0-9a-f]{64}\n"
                )
            if scenario in CONTENT_SCENARIOS:
                publication_pattern += (
                    r"content-format=(flat|paged)\n"
                    r"content-chunks=[1-9][0-9]*\n"
                    r"content-pages=[0-9]+\n"
                    r"content-objects=[1-9][0-9]*\n"
                )
                if scenario in CONTENT_MULTI_SOURCE_SCENARIOS:
                    publication_pattern += (
                        r"content-primary-chunks=[1-9][0-9]*\n"
                        r"content-secondary-chunks=[1-9][0-9]*\n"
                        r"content-source-count=2\n"
                    )
            if scenario in SIGNED_UPDATE_SCENARIOS:
                publication_pattern += (
                    r"update-payload-sha256=[0-9a-f]{64}\n"
                    r"update-manifest-record=[0-9a-f]{64}\n"
                )
            require(
                re.fullmatch(publication_pattern, published) is not None,
                "device synchronization publication evidence is invalid",
            )
            if scenario in {
                "sync-file-restart",
                "sync-file-restart-resume",
                "sync-file-guest-restart",
                "sync-file-pause",
                "sync-file-cancel",
                "sync-file-disconnect",
                "sync-file-range-retry",
                "sync-file-range-route-loss",
                "sync-file-range-late-route-loss",
                "sync-file-range-repeated-route-loss",
                "sync-file-range-triple-route-loss",
                "sync-file-range-restart-resume",
                "sync-file-range-actual-i2p-loss",
                "sync-tree-route-loss",
                "sync-tree-route-loss-cancel",
                "sync-tree-route-cancel-loss",
                "sync-tree-route-cancel-race",
                "sync-tree-route-cancel-race-loss-first",
                "sync-tree-route-startup-order",
                "sync-tree-route-private-actual-tor-loss",
                "sync-tree-route-private-actual-i2p-loss",
                "sync-tree-route-balance",
                "sync-tree-route-population",
                "sync-tree-route-population-loss",
                "sync-tree-route-loss-admission",
                "sync-tree-route-startup-admission",
                "sync-tree-route-throughput",
                "sync-tree-route-concurrent-cancel",
                "sync-tree-route-common-link-fairness",
                "sync-tree-route-cancel",
                "sync-tree-destination-corrupt",
                "sync-tree-control-replay",
                "sync-content-same-source-lanes",
                *CONTENT_RESTART_SCENARIOS,
                "sync-content-lane-science",
                "sync-content-lane-science-reverse",
                "sync-content-ratox-latency-science",
                "sync-content-ratox-cap-2-sla",
                "sync-content-ratox-post-bulk-admission",
                "sync-content-multi-source-loss",
                "sync-content-multi-route-actual-tor-loss",
            }:
                if scenario == "sync-tree-route-common-link-fairness":
                    sudo(
                        str(HOST_BIN / "tc"), "qdisc", "replace", "dev",
                        "vm-iotoxc", "root", "handle", "1:", "htb",
                        "default", "1",
                    )
                    sudo(
                        str(HOST_BIN / "tc"), "class", "replace", "dev",
                        "vm-iotoxc", "parent", "1:", "classid", "1:1",
                        "htb", "rate", "4mbit", "ceil", "4mbit",
                    )
                    sudo(
                        str(HOST_BIN / "tc"), "qdisc", "replace", "dev",
                        "vm-iotoxc", "parent", "1:1", "handle", "10:",
                        "fq_codel", "limit", "1000",
                    )
                else:
                    sudo(
                        str(HOST_BIN / "tc"),
                        "qdisc",
                        "replace",
                        "dev",
                        "vm-iotoxc",
                        "root",
                        "netem",
                        "rate",
                        "4mbit",
                        "limit",
                        "1000",
                    )
                sync_client_shaped = True
            command_file = pair_root / "client.sync-start"
            command_file.write_text(published, encoding="ascii")
            sudo(
                "install",
                "-m",
                "0600",
                str(command_file),
                str(workspace["client"] / "iotox-input/sync-start"),
            )
            command_file.unlink()
            if scenario == "sync-content-multi-source-loss":
                require(
                    route == "direct-udp",
                    "selected-source loss is qualified only over direct UDP",
                )
                loss_ready_path = (
                    workspace["device"]
                    / "iotox-rendezvous/device.multi-source-loss-ready"
                )
                client_failure = (
                    workspace["client"] / "iotox-rendezvous/client.failure"
                )
                device_failure = (
                    workspace["device"] / "iotox-rendezvous/device.failure"
                )
                wait_for(
                    lambda: root_file_exists(loss_ready_path)
                    or root_file_exists(client_failure)
                    or root_file_exists(device_failure)
                    or any(
                        process.poll() is not None
                        for process in processes.values()
                    ),
                    300,
                    "secondary source to receive selected object work",
                )
                require(
                    root_file_exists(loss_ready_path),
                    "secondary source never received selected object work",
                )
                loss_ready = read_root_file(loss_ready_path)
                loss_ready_match = re.fullmatch(
                        r"schema=iotox-content-multi-source-loss-ready-v1\n"
                        r"secondary-object-requests=([1-9][0-9]*)\n",
                        loss_ready,
                    )
                require(
                    loss_ready_match is not None,
                    "secondary source loss checkpoint is malformed",
                )
                multi_source_loss_secondary_requests_before_stop = int(
                    loss_ready_match.group(1)
                )
                deliver_guest_input(
                    pair_root,
                    workspace["device"],
                    "device",
                    "multi-source-loss-inject",
                )
                loss_stopped_path = (
                    workspace["device"]
                    / "iotox-rendezvous/device.multi-source-loss-stopped"
                )
                loss_failed_path = (
                    workspace["client"]
                    / "iotox-rendezvous/client.multi-source-loss-failed"
                )
                wait_for(
                    lambda: (
                        root_file_exists(loss_stopped_path)
                        and root_file_exists(loss_failed_path)
                    )
                    or root_file_exists(client_failure)
                    or root_file_exists(device_failure)
                    or any(
                        process.poll() is not None
                        for process in processes.values()
                    ),
                    240,
                    "subscriber fail-closed cleanup after selected-source loss",
                )
                require(
                    root_file_exists(loss_stopped_path)
                    and root_file_exists(loss_failed_path),
                    "selected-source loss did not produce fenced failure",
                )
                loss_failed = read_root_file(loss_failed_path)
                require(
                    re.fullmatch(
                        r"schema=iotox-content-multi-source-loss-failed-v1\n"
                        r"job=[1-9][0-9]*\n"
                        r"committed-objects=[1-9][0-9]*\n"
                        r"fetched-bytes=[1-9][0-9]*\n"
                        r"staging-clean=1\n"
                        r"accepted-head=0\n"
                        r"activation=0\n",
                        loss_failed,
                    )
                    is not None,
                    "selected-source loss failure evidence is malformed",
                )
                deliver_guest_input(
                    pair_root,
                    workspace["device"],
                    "device",
                    "multi-source-loss-restart",
                )
                loss_recovered_paths = {
                    "client": workspace["client"]
                    / "iotox-rendezvous/client.multi-source-loss-recovered",
                    "device": workspace["device"]
                    / "iotox-rendezvous/device.multi-source-loss-recovered",
                }
                wait_for(
                    lambda: all(
                        root_file_exists(path)
                        for path in loss_recovered_paths.values()
                    )
                    or root_file_exists(client_failure)
                    or root_file_exists(device_failure)
                    or any(
                        process.poll() is not None
                        for process in processes.values()
                    ),
                    300,
                    "secondary source restart and explicit fresh pull",
                )
                require(
                    all(
                        root_file_exists(path)
                        for path in loss_recovered_paths.values()
                    ),
                    "selected-source restart did not admit a fresh pull",
                )
                client_recovered = read_root_file(loss_recovered_paths["client"])
                require(
                    re.fullmatch(r"replacement-job=[1-9][0-9]*\n", client_recovered)
                    is not None,
                    "selected-source client recovery checkpoint is malformed",
                )
                device_recovered = read_root_file(loss_recovered_paths["device"])
                legacy_recovery = (
                    "schema=iotox-content-multi-source-loss-recovered-v1\n"
                    "secondary-recovered=1\n"
                    "constructed-replica-head-reinjected=1\n"
                )
                durable_recovery = (
                    "schema=iotox-content-multi-source-loss-recovered-v1\n"
                    "secondary-recovered=1\n"
                    "durable-replica-head-cold-start=1\n"
                    "published-head-absent=1\n"
                    "replica-gc-consistent=1\n"
                )
                require(
                    device_recovered in {legacy_recovery, durable_recovery},
                    "selected-source replica recovery checkpoint is malformed",
                )
                multi_source_loss_constructed_replica_head_reinjected = (
                    device_recovered == legacy_recovery
                )
                multi_source_loss_durable_replica_cold_start = (
                    device_recovered == durable_recovery
                )
            elif scenario == "sync-content-multi-route-actual-tor-loss":
                failure_path = (
                    workspace["client"]
                    / "iotox-rendezvous/client.multi-source-loss-failed"
                )
                recovered_path = (
                    workspace["client"]
                    / "iotox-rendezvous/client.multi-source-loss-recovered"
                )
                client_failure = (
                    workspace["client"] / "iotox-rendezvous/client.failure"
                )
                device_failure = (
                    workspace["device"] / "iotox-rendezvous/device.failure"
                )
                wait_for(
                    lambda: (
                        root_file_exists(failure_path)
                        and root_file_exists(recovered_path)
                    )
                    or root_file_exists(client_failure)
                    or root_file_exists(device_failure)
                    or any(
                        process.poll() is not None
                        for process in processes.values()
                    ),
                    480,
                    "exact Tor content-worker failure and recovery",
                )
                require(
                    root_file_exists(failure_path)
                    and root_file_exists(recovered_path),
                    "exact Tor content-worker loss did not admit a fresh pull",
                )
                route_failure = read_root_file(failure_path)
                route_failure_match = re.fullmatch(
                    r"schema=iotox-content-multi-source-loss-failed-v1\n"
                    r"job=([1-9][0-9]*)\n"
                    r"committed-objects=([1-9][0-9]*)\n"
                    r"fetched-bytes=([1-9][0-9]*)\n"
                    r"staging-clean=1\n"
                    r"accepted-head=0\n"
                    r"activation=0\n"
                    r"route-loss=1\n"
                    r"route=([0-9A-F]{64})\n"
                    r"worker=([1-9][0-9]*)\n"
                    r"position-bytes=([1-9][0-9]*)\n"
                    r"carrier-losses=1\n"
                    r"reassignments=0\n",
                    route_failure,
                )
                require(
                    route_failure_match is not None
                    and int(route_failure_match.group(2)) > 0
                    and int(route_failure_match.group(3)) > 0
                    and int(route_failure_match.group(6)) >= 65_536,
                    "exact Tor content-worker failure evidence is malformed",
                )
                require(
                    re.fullmatch(
                        r"replacement-job=[1-9][0-9]*\n",
                        read_root_file(recovered_path),
                    )
                    is not None,
                    "exact Tor content-worker recovery checkpoint is malformed",
                )
            if actual_tor_loss:
                require(tor_node is not None, "actual-Tor node disappeared")
                loss_ready_path = (
                    workspace["client"]
                    / "iotox-rendezvous/client.actual-tor-loss-ready"
                )
                client_failure = (
                    workspace["client"] / "iotox-rendezvous/client.failure"
                )
                wait_for(
                    lambda: root_file_exists(loss_ready_path)
                    or root_file_exists(client_failure)
                    or processes["client"].poll() is not None,
                    300,
                    "positive sync progress on the actual-Tor carrier",
                )
                require(
                    root_file_exists(loss_ready_path),
                    "client did not bind positive progress to actual Tor",
                )
                loss_ready = read_root_file(loss_ready_path)
                ready_match = re.fullmatch(
                    r"schema=iotox-actual-tor-loss-ready-v1\n"
                    r"job=([1-9][0-9]*)\n"
                    r"position-bytes=([1-9][0-9]*)\n"
                    r"carrier=([0-9A-F]{64})\n"
                    r"carrier-worker=([1-9][0-9]*)\n",
                    loss_ready,
                )
                require(
                    ready_match is not None
                    and 0 < int(ready_match.group(2))
                    < SYNC_SCENARIOS[scenario],
                    "actual-Tor loss readiness evidence is invalid",
                )
                client_tor = tor_instances["client"]
                tor_pre_loss_evidence = actual_tor_role_evidence(
                    pair_root, client_tor, tor_node, "pre-loss"
                )
                old_process = client_tor["process"]
                require(
                    isinstance(old_process, subprocess.Popen),
                    "client Tor process type drifted",
                )
                fault_ns = time.monotonic_ns()
                old_pid = old_process.pid
                returncode = kill_process_group(old_process, "client Tor")
                client_tor["log"].close()
                old_control = Path(client_tor["root"]) / "control.sock"
                old_control.unlink(missing_ok=True)

                loss_observed_path = (
                    workspace["client"]
                    / "iotox-rendezvous/client.actual-tor-loss-observed"
                )
                wait_for(
                    lambda: root_file_exists(loss_observed_path)
                    or root_file_exists(client_failure)
                    or processes["client"].poll() is not None,
                    240,
                    "actual-Tor carrier loss and native reassignment",
                )
                require(
                    root_file_exists(loss_observed_path),
                    "client did not observe actual-Tor carrier loss",
                )
                loss_observed = read_root_file(loss_observed_path)
                observed_match = re.fullmatch(
                    r"schema=iotox-actual-tor-loss-observed-v1\n"
                    r"job=([1-9][0-9]*)\n"
                    r"position-bytes=([1-9][0-9]*)\n"
                    r"stopped-carrier=([0-9A-F]{64})\n"
                    r"replacement-carrier=([0-9A-F]{64})\n"
                    r"carrier-losses=1\n"
                    r"reassignments=1\n",
                    loss_observed,
                )
                require(
                    observed_match is not None
                    and observed_match.group(1) == ready_match.group(1)
                    and observed_match.group(2) == ready_match.group(2)
                    and observed_match.group(3) == ready_match.group(3)
                    and observed_match.group(4) != ready_match.group(3),
                    "actual-Tor reassignment evidence changed the fault target",
                )
                observed_ns = time.monotonic_ns()
                recovered_client_tor = start_pair_tor(
                    pair_root, "client", "recovered"
                )
                require(
                    recovered_client_tor["tor_sha256"]
                    == client_tor["tor_sha256"]
                    and recovered_client_tor["tor_version"]
                    == client_tor["tor_version"],
                    "recovered client Tor binary identity changed",
                )
                tor_instances["client"] = recovered_client_tor
                restarted_ns = time.monotonic_ns()
                deliver_guest_input(
                    pair_root,
                    workspace["client"],
                    "client",
                    "actual-tor-restarted",
                )
                actual_tor_process_loss = {
                    "schema": "iotox-actual-tor-process-loss-v1",
                    "role": "client",
                    "signal": signal.SIGKILL,
                    "returncode": returncode,
                    "pre_loss_process_pid": old_pid,
                    "pre_loss_control_socket_inode": tor_pre_loss_evidence[
                        "control_socket_inode"
                    ],
                    "job_id": int(ready_match.group(1)),
                    "position_bytes": int(ready_match.group(2)),
                    "stopped_carrier": ready_match.group(3),
                    "stopped_carrier_sha256": hashlib.sha256(
                        ready_match.group(3).encode("ascii")
                    ).hexdigest(),
                    "replacement_carrier": observed_match.group(4),
                    "carrier_losses": 1,
                    "reassignments": 1,
                    "route_worker_restarts": 0,
                    "loss_observation_ns": observed_ns - fault_ns,
                    "restart_bootstrap_ns": restarted_ns - observed_ns,
                }
                loss_path = pair_root / "actual-tor-process-loss.json"
                loss_path.write_text(
                    json.dumps(
                        actual_tor_process_loss, indent=2, sort_keys=True
                    )
                    + "\n",
                    encoding="utf-8",
                )
            if scenario == "sync-file-range-actual-i2p-loss":
                # The ordinary range orchestration follows validation of the
                # generation-1 completion below. This loss gate needs the
                # generation-2 range to be live before the host can wait for
                # its fault checkpoint. Relay the two immutable records now;
                # the common path still validates them and suppresses only
                # the duplicate deliveries.
                initial_complete_path = (
                    workspace["client"]
                    / "iotox-rendezvous/client.sync-complete"
                )
                client_failure = (
                    workspace["client"] / "iotox-rendezvous/client.failure"
                )
                wait_for(
                    lambda: root_file_exists(initial_complete_path)
                    or root_file_exists(client_failure)
                    or processes["client"].poll() is not None,
                    300,
                    "generation-1 basis convergence before range loss",
                )
                require(
                    root_file_exists(initial_complete_path),
                    "client did not converge the generation-1 range basis",
                )
                early_complete = read_root_file(initial_complete_path)
                command_file = pair_root / "device.sync-finished.early"
                command_file.write_text(early_complete, encoding="ascii")
                sudo(
                    "install",
                    "-m",
                    "0600",
                    str(command_file),
                    str(workspace["device"] / "iotox-input/sync-finished"),
                )
                command_file.unlink()

                range_published_path = (
                    workspace["device"]
                    / "iotox-rendezvous/device.sync-range-published"
                )
                device_failure = (
                    workspace["device"] / "iotox-rendezvous/device.failure"
                )
                wait_for(
                    lambda: root_file_exists(range_published_path)
                    or root_file_exists(device_failure)
                    or processes["device"].poll() is not None,
                    240,
                    "generation-2 publication before range loss",
                )
                require(
                    root_file_exists(range_published_path),
                    "device did not publish generation 2 before range loss",
                )
                early_range = read_root_file(range_published_path)
                command_file = pair_root / "client.sync-range-start.early"
                command_file.write_text(early_range, encoding="ascii")
                sudo(
                    "install",
                    "-m",
                    "0600",
                    str(command_file),
                    str(
                        workspace["client"]
                        / "iotox-input/sync-range-start"
                    ),
                )
                command_file.unlink()
                range_loss_primed = True
            if actual_i2p_loss:
                require(i2p_instance is not None, "I2P topology is absent")
                loss_ready_path = (
                    workspace["client"]
                    / "iotox-rendezvous/client.actual-i2p-loss-ready"
                )
                client_failure = (
                    workspace["client"] / "iotox-rendezvous/client.failure"
                )
                wait_for(
                    lambda: root_file_exists(loss_ready_path)
                    or root_file_exists(client_failure)
                    or processes["client"].poll() is not None,
                    360,
                    "positive sync progress on the signed actual-I2P carrier",
                )
                require(
                    root_file_exists(loss_ready_path),
                    "client did not bind positive progress to actual I2P",
                )
                ready_match = re.fullmatch(
                    r"schema=iotox-actual-i2p-loss-ready-v1\n"
                    r"job=([1-9][0-9]*)\n"
                    r"position-bytes=([1-9][0-9]*)\n"
                    r"carrier=([0-9A-F]{64})\n"
                    r"carrier-worker=([1-9][0-9]*)\n",
                    read_root_file(loss_ready_path),
                )
                require(
                    ready_match is not None
                    and 65_536 <= int(ready_match.group(2))
                    < SYNC_SCENARIOS[scenario],
                    "actual-I2P loss readiness evidence is invalid",
                )

                i2p_root = Path(i2p_instance["root"])
                fault_requested_ns = time.monotonic_ns()
                fault_request = i2p_root / "fault-client-router"
                fault_request.write_text(
                    "fault-client-router=1\n", encoding="ascii"
                )
                os.chmod(fault_request, 0o600)
                active_path = i2p_root / "fault-active.json"
                wait_for(
                    active_path.is_file,
                    60,
                    "I2P client-router sync fault activation",
                )
                i2p_loss_active = load(active_path)
                require(
                    i2p_loss_active.get("schema")
                    == "iotox.i2p-tox-fronts.v1"
                    and i2p_loss_active.get("status") == "fault-active"
                    and i2p_loss_active.get("kind")
                    == "client-router-process-restart"
                    and i2p_loss_active.get("adapter_listener_reachable")
                    is True
                    and i2p_loss_active.get(
                        "client_sam_listener_reachable"
                    )
                    is False
                    and i2p_loss_active.get("adapter_generation_one_lost")
                    is True
                    and i2p_loss_active.get("contains_secrets") is False
                    and tcp_port_open(
                        HOST_BRIDGE_ADDRESS, I2P_SOCKS5_PORT
                    ),
                    "I2P loss listener-positive/SAM-negative evidence is invalid",
                )

                loss_observed_path = (
                    workspace["client"]
                    / "iotox-rendezvous/client.actual-i2p-loss-observed"
                )
                wait_for(
                    lambda: root_file_exists(loss_observed_path)
                    or root_file_exists(client_failure)
                    or processes["client"].poll() is not None,
                    360,
                    "fail-closed actual-I2P carrier-loss observation",
                )
                require(
                    root_file_exists(loss_observed_path),
                    "client did not observe fail-closed actual-I2P loss",
                )
                observed_match = re.fullmatch(
                    r"schema=iotox-actual-i2p-loss-observed-v1\n"
                    r"job=([1-9][0-9]*)\n"
                    r"position-bytes=([1-9][0-9]*)\n"
                    r"stopped-carrier=([0-9A-F]{64})\n"
                    r"carrier-losses=1\n"
                    r"reassignments=0\n"
                    r"blocked-jobs=1\n",
                    read_root_file(loss_observed_path),
                )
                require(
                    observed_match is not None
                    and observed_match.group(1) == ready_match.group(1)
                    and observed_match.group(2) == ready_match.group(2)
                    and observed_match.group(3) == ready_match.group(3),
                    "actual-I2P fail-closed observation changed the fault target",
                )
                loss_observed_ns = time.monotonic_ns()

                recover_request = i2p_root / "recover-client-router"
                recover_request.write_text(
                    "recover-client-router=1\n", encoding="ascii"
                )
                os.chmod(recover_request, 0o600)
                router_recovered_path = i2p_root / "fault-recovered.json"
                wait_for(
                    router_recovered_path.is_file,
                    480,
                    "I2P client-router sync recovery",
                )
                i2p_loss_recovered = load(router_recovered_path)
                require(
                    i2p_loss_recovered.get("schema")
                    == "iotox.i2p-tox-fronts.v1"
                    and i2p_loss_recovered.get("status")
                    == "fault-recovered"
                    and i2p_loss_recovered.get("kind")
                    == "client-router-process-restart"
                    and i2p_loss_recovered.get("process_replaced") is True
                    and i2p_loss_recovered.get("router_datadir_preserved")
                    is True
                    and i2p_loss_recovered.get(
                        "adapter_listener_reachable_while_sam_down"
                    )
                    is True
                    and i2p_loss_recovered.get(
                        "client_sam_listener_absent_during_fault"
                    )
                    is True
                    and i2p_loss_recovered.get(
                        "adapter_generation_one_lost"
                    )
                    is True
                    and i2p_loss_recovered.get(
                        "adapter_generation_two_ready"
                    )
                    is True
                    and isinstance(
                        i2p_loss_recovered.get("fault_hold_ns"), int
                    )
                    and i2p_loss_recovered["fault_hold_ns"] > 0
                    and i2p_loss_recovered.get("contains_secrets") is False,
                    "I2P sync router recovery evidence is invalid",
                )
                router_recovered_ns = time.monotonic_ns()
                deliver_guest_input(
                    pair_root,
                    workspace["client"],
                    "client",
                    "actual-i2p-restarted",
                )
                guest_recovered_path = (
                    workspace["client"]
                    / "iotox-rendezvous/client.actual-i2p-loss-recovered"
                )
                wait_for(
                    lambda: root_file_exists(guest_recovered_path)
                    or root_file_exists(client_failure)
                    or processes["client"].poll() is not None,
                    900,
                    "explicit fresh pull through the recovered I2P member",
                )
                require(
                    root_file_exists(guest_recovered_path),
                    "client did not complete through the recovered I2P member",
                )
                range_loss = scenario == "sync-file-range-actual-i2p-loss"
                recovered_pattern = (
                    r"schema=iotox-actual-i2p-loss-recovered-v2\n"
                    r"original-job=([1-9][0-9]*)\n"
                    r"replacement-job=([1-9][0-9]*)\n"
                    r"carrier=([0-9A-F]{64})\n"
                    r"replacement-requested-objects=(1)\n"
                    r"replacement-committed-objects=(2)\n"
                    r"manifest-reused-locally=(1)\n"
                    r"recoveries=1\n"
                    r"worker-restarts=0\n"
                    r"old-job-cancelled=1\n"
                    r"same-carrier=1\n"
                    if range_loss
                    else (
                        r"schema=iotox-actual-i2p-loss-recovered-v1\n"
                        r"original-job=([1-9][0-9]*)\n"
                        r"replacement-job=([1-9][0-9]*)\n"
                        r"carrier=([0-9A-F]{64})\n"
                        r"recoveries=1\n"
                        r"worker-restarts=0\n"
                        r"old-job-cancelled=1\n"
                        r"same-carrier=1\n"
                    )
                )
                guest_recovered_match = re.fullmatch(
                    recovered_pattern, read_root_file(guest_recovered_path)
                )
                require(
                    guest_recovered_match is not None
                    and guest_recovered_match.group(1)
                    == ready_match.group(1)
                    and guest_recovered_match.group(2)
                    != ready_match.group(1)
                    and guest_recovered_match.group(3)
                    == ready_match.group(3),
                    "actual-I2P recovered pull changed the signed member",
                )
                actual_i2p_fail_closed_loss = {
                    "schema": (
                        "iotox-actual-i2p-fail-closed-loss-v2"
                        if range_loss
                        else "iotox-actual-i2p-fail-closed-loss-v1"
                    ),
                    "role": "client",
                    "original_job_id": int(ready_match.group(1)),
                    "replacement_job_id": int(
                        guest_recovered_match.group(2)
                    ),
                    "position_bytes": int(ready_match.group(2)),
                    "stopped_carrier": ready_match.group(3),
                    "stopped_carrier_sha256": hashlib.sha256(
                        ready_match.group(3).encode("ascii")
                    ).hexdigest(),
                    "carrier_losses": 1,
                    "reassignments": 0,
                    "blocked_jobs": 1,
                    "recoveries": 1,
                    "route_worker_restarts": 0,
                    "old_job_cancelled": True,
                    "replacement_same_carrier": True,
                    "old_client_router_pid": i2p_loss_active[
                        "old_client_router_pid"
                    ],
                    "new_client_router_pid": i2p_loss_recovered[
                        "new_client_router_pid"
                    ],
                    "router_datadir_preserved": True,
                    "adapter_listener_reachable_while_sam_down": True,
                    "client_sam_listener_absent_during_fault": True,
                    "adapter_generation_one_lost": True,
                    "adapter_generation_two_ready": True,
                    "fault_hold_ns": i2p_loss_recovered["fault_hold_ns"],
                    "loss_observation_ns": (
                        loss_observed_ns - fault_requested_ns
                    ),
                    "router_recovery_ns": (
                        router_recovered_ns - loss_observed_ns
                    ),
                    "contains_secrets": False,
                }
                if range_loss:
                    actual_i2p_fail_closed_loss.update(
                        {
                            "replacement_requested_objects": int(
                                guest_recovered_match.group(4)
                            ),
                            "replacement_committed_objects": int(
                                guest_recovered_match.group(5)
                            ),
                            "manifest_reused_locally": (
                                guest_recovered_match.group(6) == "1"
                            ),
                        }
                    )
                (pair_root / "actual-i2p-fail-closed-loss.json").write_text(
                    json.dumps(
                        actual_i2p_fail_closed_loss,
                        indent=2,
                        sort_keys=True,
                    )
                    + "\n",
                    encoding="utf-8",
                )
                i2p_router_restart_count = 1
            if scenario in SIGNED_UPDATE_SCENARIOS:
                client_stage_ready = (
                    workspace["client"]
                    / "iotox-rendezvous/client.update-stage-ready"
                )
                client_failure = (
                    workspace["client"] / "iotox-rendezvous/client.failure"
                )
                device_failure = (
                    workspace["device"] / "iotox-rendezvous/device.failure"
                )
                wait_for(
                    lambda: root_file_exists(client_stage_ready)
                    or root_file_exists(client_failure)
                    or root_file_exists(device_failure)
                    or any(
                        process.poll() is not None
                        for process in processes.values()
                    ),
                    300,
                    "subscriber accepted HEAD and remote-stage readiness",
                )
                require(
                    root_file_exists(client_stage_ready),
                    "subscriber did not reach remote update staging readiness",
                )
                stage_ready = read_root_file(client_stage_ready)
                expected_head = re.search(
                    r"^head-record=([0-9a-f]{64})$", stage_ready, re.MULTILINE
                )
                require(
                    expected_head is not None
                    and expected_head.group(1)
                    == re.search(
                        r"^head-record=([0-9a-f]{64})$",
                        published,
                        re.MULTILINE,
                    ).group(1),
                    "remote update staging readiness changed the accepted HEAD",
                )
                command_file = pair_root / "device.signed-update-stage-ready"
                command_file.write_text(stage_ready, encoding="ascii")
                sudo(
                    "install",
                    "-m",
                    "0600",
                    str(command_file),
                    str(
                        workspace["device"]
                        / "iotox-input/signed-update-stage-ready"
                    ),
                )
                command_file.unlink()
                device_stage_complete = (
                    workspace["device"]
                    / "iotox-rendezvous/device.update-stage-complete"
                )
                wait_for(
                    lambda: root_file_exists(device_stage_complete)
                    or root_file_exists(client_failure)
                    or root_file_exists(device_failure)
                    or any(
                        process.poll() is not None
                        for process in processes.values()
                    ),
                    300,
                    "publisher durable remote update.stage completion",
                )
                require(
                    root_file_exists(device_stage_complete),
                    "publisher did not receive successful remote update.stage evidence",
                )
                stage_complete = read_root_file(device_stage_complete)
                require(
                    re.search(r"^remote-stage=1$", stage_complete, re.MULTILINE)
                    is not None
                    and re.search(
                        r"^remote-stage-outcome=succeeded$",
                        stage_complete,
                        re.MULTILINE,
                    )
                    is not None,
                    "publisher remote update.stage evidence is not terminal success",
                )
                command_file = pair_root / "client.signed-update-stage-complete"
                command_file.write_text(stage_complete, encoding="ascii")
                sudo(
                    "install",
                    "-m",
                    "0600",
                    str(command_file),
                    str(
                        workspace["client"]
                        / "iotox-input/signed-update-stage-complete"
                    ),
                )
                command_file.unlink()
            if scenario == "sync-file-disconnect":
                interruption_ready = (
                    workspace["client"]
                    / "iotox-rendezvous/client.sync-interruption-ready"
                )
                wait_for(
                    lambda: root_file_exists(interruption_ready),
                    240,
                    "client partial synchronization staging",
                )
                command_file = pair_root / "device.sync-observe-disconnect"
                command_file.write_text(
                    "sync-observe-disconnect=1\n", encoding="ascii"
                )
                sudo(
                    "install",
                    "-m",
                    "0600",
                    str(command_file),
                    str(
                        workspace["device"]
                        / "iotox-input/sync-observe-disconnect"
                    ),
                )
                command_file.unlink()
                device_armed = (
                    workspace["device"]
                    / "iotox-rendezvous/device.sync-disconnect-armed"
                )
                wait_for(
                    lambda: root_file_exists(device_armed),
                    120,
                    "publisher synchronization link-loss arm",
                )
                command_file = pair_root / "client.sync-disconnect"
                command_file.write_text("sync-disconnect=1\n", encoding="ascii")
                sudo(
                    "install",
                    "-m",
                    "0600",
                    str(command_file),
                    str(workspace["client"] / "iotox-input/sync-disconnect"),
                )
                command_file.unlink()
                client_armed = (
                    workspace["client"]
                    / "iotox-rendezvous/client.sync-disconnect-armed"
                )
                wait_for(
                    lambda: root_file_exists(client_armed),
                    120,
                    "subscriber synchronization link-loss arm",
                )
                links_blocked = True
                sync_client_shaped = False
                for tap in ("vm-iotoxc", "vm-iotoxd"):
                    sudo(
                        str(HOST_BIN / "tc"),
                        "qdisc",
                        "replace",
                        "dev",
                        tap,
                        "root",
                        "netem",
                        "loss",
                        "100%",
                    )
                link_interruption_count = 1
                disconnect_offline = {
                    "client": workspace["client"]
                    / "iotox-rendezvous/client.sync-disconnect-offline",
                    "device": workspace["device"]
                    / "iotox-rendezvous/device.sync-disconnect-offline",
                }
                wait_for(
                    lambda: all(
                        root_file_exists(path)
                        for path in disconnect_offline.values()
                    ),
                    180,
                    "both synchronization peers to observe link loss",
                )
                for tap in ("vm-iotoxc", "vm-iotoxd"):
                    sudo(str(HOST_BIN / "tc"), "qdisc", "del", "dev", tap, "root")
                links_blocked = False
                disconnect_recovered = {
                    "client": workspace["client"]
                    / "iotox-rendezvous/client.sync-disconnect-recovered",
                    "device": workspace["device"]
                    / "iotox-rendezvous/device.sync-disconnect-recovered",
                }
                wait_for(
                    lambda: all(
                        root_file_exists(path)
                        for path in disconnect_recovered.values()
                    ),
                    240,
                    "both synchronization peers to recover a fresh epoch",
                )
            if scenario in {
                "sync-file-restart",
                "sync-file-restart-resume",
                *CONTENT_RESTART_SCENARIOS,
            }:
                interruption_ready = (
                    workspace["client"]
                    / "iotox-rendezvous/client.sync-interruption-ready"
                )
                restart_client_failure = (
                    workspace["client"] / "iotox-rendezvous/client.failure"
                )
                restart_progress = (
                    workspace["client"]
                    / "iotox-rendezvous/client.content-restart-progress"
                )
                wait_for(
                    lambda: root_file_exists(interruption_ready)
                    or root_file_exists(restart_client_failure)
                    or processes["client"].poll() is not None,
                    240,
                    "client partial synchronization staging",
                )
                require(
                    root_file_exists(interruption_ready),
                    "client failed before the restart boundary: "
                    + (
                        read_root_file(restart_client_failure).strip()
                        if root_file_exists(restart_client_failure)
                        else read_root_file(restart_progress).strip()
                        if root_file_exists(restart_progress)
                        else f"chain-exit={processes['client'].poll()}"
                    ),
                )
                if scenario in CONTENT_RESTART_SCENARIOS:
                    content_restart_cap = CONTENT_RESTART_SCENARIOS[scenario]
                    content_restart_partial_pattern = (
                        "2" if content_restart_cap == 2 else "[2-4]"
                    )
                    interruption = read_root_file(interruption_ready)
                    require(
                        re.fullmatch(
                            r"sync-interruption-ready=1\n"
                            r"staging-bytes=[1-9][0-9]*\n"
                            rf"content-restart-cap={content_restart_cap}\n"
                            rf"content-restart-live-lanes={content_restart_cap}\n"
                            rf"content-restart-staging-temporaries={content_restart_partial_pattern}\n"
                            r"content-restart-lane-set-sha256=[0-9a-f]{64}\n"
                            r"content-restart-first-job=[1-9][0-9]*\n",
                            interruption,
                        )
                        is not None,
                        "subscriber live content-lane restart boundary is invalid",
                    )
                command_file = pair_root / "device.sync-observe-restart"
                command_file.write_text("sync-observe-restart=1\n", encoding="ascii")
                sudo(
                    "install",
                    "-m",
                    "0600",
                    str(command_file),
                    str(workspace["device"] / "iotox-input/sync-observe-restart"),
                )
                command_file.unlink()
                restart_armed = (
                    workspace["device"]
                    / "iotox-rendezvous/device.sync-restart-armed"
                )
                wait_for(
                    lambda: root_file_exists(restart_armed),
                    120,
                    "publisher synchronization restart observation arm",
                )
                command_file = pair_root / "client.sync-restart"
                command_file.write_text("sync-restart=1\n", encoding="ascii")
                sudo(
                    "install",
                    "-m",
                    "0600",
                    str(command_file),
                    str(workspace["client"] / "iotox-input/sync-restart"),
                )
                command_file.unlink()
                stopped_path = (
                    workspace["client"]
                    / "iotox-rendezvous/client.sync-daemon-stopped"
                )
                crash_state_path = (
                    workspace["client"]
                    / "iotox-rendezvous/client.sync-crash-state"
                )
                offline_path = (
                    workspace["device"]
                    / "iotox-rendezvous/device.sync-offline-observed"
                )
                wait_for(
                    lambda: root_file_exists(crash_state_path)
                    and root_file_exists(offline_path),
                    180,
                    "subscriber crash state and publisher offline observation",
                )
                crash_state = read_root_file(crash_state_path)
                if scenario in CONTENT_RESTART_SCENARIOS:
                    content_restart_cap = CONTENT_RESTART_SCENARIOS[scenario]
                    partial_pattern = (
                        "2" if content_restart_cap == 2 else "[2-4]"
                    )
                    crash_pattern = (
                        r"schema=iotox-sync-content-crash-state-v1\n"
                        r"stop-status=137\n"
                        rf"transport-temporaries={partial_pattern}\n"
                        rf"content-restart-cap={content_restart_cap}\n"
                        rf"content-live-lanes={content_restart_cap}\n"
                        r"content-transport-bytes=[1-9][0-9]*\n"
                        r"content-canonical-partials=0\n"
                        r"content-committed-objects=[2-9][0-9]*\n"
                        r"content-committed-bytes=[1-9][0-9]*\n"
                        r"content-inventory-sha256=[0-9a-f]{64}\n"
                        r"attempt-journal-present=1\n"
                        r"accepted-head-present=0\n"
                        r"activation-present=0\n"
                    )
                elif scenario == "sync-file-restart-resume":
                    crash_pattern = (
                        r"schema=iotox-sync-crash-state-v2\n"
                        r"stop-status=137\n"
                        r"transport-temporaries=0\n"
                        r"canonical-partials=[12]\n"
                        r"canonical-bytes=[1-9][0-9]*\n"
                        r"attempt-journal-present=1\n"
                        r"accepted-head-present=0\n"
                        r"activation-present=0\n"
                    )
                else:
                    crash_pattern = (
                        r"schema=iotox-sync-crash-state-v1\n"
                        r"stop-status=137\n"
                        r"transport-temporaries=[12]\n"
                        r"attempt-journal-present=1\n"
                        r"accepted-head-present=0\n"
                        r"activation-present=0\n"
                    )
                require(
                    re.fullmatch(crash_pattern, crash_state) is not None,
                    "subscriber unclean synchronization state is invalid",
                )
                wait_for(
                    lambda: root_file_exists(stopped_path),
                    30,
                    "subscriber post-crash checkpoint",
                )
                sudo(
                    str(HOST_BIN / "tc"),
                    "qdisc",
                    "del",
                    "dev",
                    "vm-iotoxc",
                    "root",
                )
                sync_client_shaped = False
                command_file = pair_root / "client.sync-restart-continue"
                command_file.write_text(
                    "sync-restart-continue=1\n", encoding="ascii"
                )
                sudo(
                    "install",
                    "-m",
                    "0600",
                    str(command_file),
                    str(
                        workspace["client"]
                        / "iotox-input/sync-restart-continue"
                    ),
                )
                command_file.unlink()
                restarted_path = (
                    workspace["client"]
                    / "iotox-rendezvous/client.sync-daemon-restarted"
                )
                recovered_path = (
                    workspace["device"]
                    / "iotox-rendezvous/device.sync-recovered"
                )
                wait_for(
                    lambda: root_file_exists(restarted_path)
                    and root_file_exists(recovered_path),
                    240,
                    "subscriber restart and publisher session recovery",
                )
                # The subscriber's local authority view can become ready
                # before the publisher has processed the subscriber's proof,
                # especially over a TCP relay.  Release the fresh pull only
                # after both independently observed recovery markers exist.
                command_file = pair_root / "client.sync-restart-authority-ready"
                command_file.write_text(
                    "sync-restart-authority-ready=1\n", encoding="ascii"
                )
                sudo(
                    "install",
                    "-m",
                    "0600",
                    str(command_file),
                    str(
                        workspace["client"]
                        / "iotox-input/sync-restart-authority-ready"
                    ),
                )
                command_file.unlink()
                sync_client_daemon_restart_count = 1
            if scenario == "sync-file-guest-restart":
                interruption_ready = (
                    workspace["client"]
                    / "iotox-rendezvous/client.sync-interruption-ready"
                )
                wait_for(
                    lambda: root_file_exists(interruption_ready),
                    240,
                    "client partial synchronization staging",
                )
                command_file = pair_root / "device.sync-observe-guest-restart"
                command_file.write_text(
                    "sync-observe-guest-restart=1\n", encoding="ascii"
                )
                sudo(
                    "install",
                    "-m",
                    "0600",
                    str(command_file),
                    str(
                        workspace["device"]
                        / "iotox-input/sync-observe-guest-restart"
                    ),
                )
                command_file.unlink()
                armed_path = (
                    workspace["device"]
                    / "iotox-rendezvous/device.sync-guest-restart-armed"
                )
                offline_path = (
                    workspace["client"]
                    / "iotox-rendezvous/client.sync-guest-restart-offline"
                )
                wait_for(
                    lambda: root_file_exists(armed_path)
                    and root_file_exists(offline_path),
                    180,
                    "publisher guest shutdown and subscriber cleanup",
                )
                initial_device_process = processes["device"]
                try:
                    # Cloud Hypervisor attempts an in-process reboot first. The
                    # deliberately severed virtiofs transport has a bounded
                    # one-minute reconnect window before the VMM exits, so the
                    # host must allow that protocol timeout to finish.
                    initial_device_result = initial_device_process.wait(timeout=120)
                except subprocess.TimeoutExpired as error:
                    raise RuntimeError(
                        "initial device VMM chain did not terminate after sync reboot"
                    ) from error
                require(
                    initial_device_result in {0, 1},
                    "initial sync device VMM chain exited unexpectedly: "
                    f"{initial_device_result}",
                )
                initial_chain_path = (
                    role_roots["device"]
                    / "direct-cloud-hypervisor-live-chain.json"
                )
                initial_launch_path = (
                    role_roots["device"]
                    / "live/cloud-hypervisor-launch.json"
                )
                initial_chain = load(initial_chain_path)
                initial_launch = load(initial_launch_path)
                require(
                    initial_chain.get("status") == "blocked"
                    and initial_chain.get("failure", {}).get("blockers")
                    == ["live:console-not-observed"],
                    "initial sync device chain did not record the bounded reboot exit",
                )
                require(
                    initial_launch.get("status") == "blocked"
                    and initial_launch.get("vmm", {}).get("process_observed") is True
                    and initial_launch.get("vmm", {}).get("exit_observed") is True
                    and initial_launch.get("vmm", {}).get("exit_status") == 1,
                    "initial sync device VMM reboot exit evidence is invalid",
                )
                initial_device_chain_entry = {
                    "path": str(initial_chain_path.relative_to(pair_root)),
                    "sha256": sha256(initial_chain_path),
                    "status": "bounded-reboot-exit",
                }
                initial_device_launch_entry = {
                    "path": str(initial_launch_path.relative_to(pair_root)),
                    "sha256": sha256(initial_launch_path),
                    "status": "bounded-reboot-exit",
                }

                sudo(
                    str(HOST_BIN / "tc"),
                    "qdisc",
                    "del",
                    "dev",
                    "vm-iotoxc",
                    "root",
                )
                sync_client_shaped = False
                successor_root = pair_root / "device-restart"
                successor_root.mkdir(mode=0o700)
                successor_stdout = (
                    pair_root / "device-restart.chain.stdout"
                ).open("wb")
                successor_stderr = (
                    pair_root / "device-restart.chain.stderr"
                ).open("wb")
                logs["device-restart"] = (successor_stdout, successor_stderr)
                prelaunch_receipt = (
                    role_roots["device"]
                    / "prelaunch/direct-cloud-hypervisor-prelaunch-chain.json"
                )
                processes["device"] = subprocess.Popen(
                    command_for(
                        "device",
                        route,
                        successor_root,
                        prelaunch_receipt=prelaunch_receipt,
                        guest_receipt_timeout=guest_receipt_timeout,
                    ),
                    stdout=successor_stdout,
                    stderr=successor_stderr,
                    start_new_session=True,
                )
                role_roots["device"] = successor_root
                workspace["device"] = successor_root / "live/workspace-export"
                wait_for(
                    lambda: workspace["device"].is_dir(),
                    180,
                    "replacement synchronization device Sandwurm workspace",
                )
                device_recovered = (
                    workspace["device"]
                    / "iotox-rendezvous/device.sync-guest-recovered"
                )
                client_recovered = (
                    workspace["client"]
                    / "iotox-rendezvous/client.sync-guest-restart-recovered"
                )
                wait_for(
                    lambda: root_file_exists(device_recovered)
                    and root_file_exists(client_recovered)
                    or processes["client"].poll() is not None
                    or processes["device"].poll() is not None,
                    600,
                    "publisher guest reboot and subscriber fresh-epoch retry",
                )
                require(
                    root_file_exists(device_recovered)
                    and root_file_exists(client_recovered),
                    "a synchronization VMM chain exited before guest-restart recovery",
                )
                device_guest_restart_count = 1
            completed_path = (
                workspace["client"]
                / "iotox-rendezvous/client.sync-complete"
            )
            client_failure_path = (
                workspace["client"]
                / "iotox-rendezvous/client.failure"
            )
            post_retry_failure = (
                workspace["client"]
                / "iotox-rendezvous/client.sync-post-retry-failed"
            )
            balance_phase_path = (
                workspace["client"]
                / "iotox-rendezvous/client.sync-route-balance-phase"
            )

            def balance_phase_is_terminal() -> bool:
                if scenario != "sync-tree-route-balance" or not root_file_exists(
                    balance_phase_path
                ):
                    return False
                return re.search(
                    r"^phase=(?:fixed|adaptive)-(?:preflight-failed|terminal|timeout|carrier-invalid|policy-mismatch)",
                    read_root_file(balance_phase_path),
                    re.MULTILINE,
                ) is not None
            if scenario in CONTENT_LANE_SCIENCE_SCENARIOS:
                lane_science_ready_path = (
                    workspace["device"]
                    / "iotox-rendezvous/device.sync-content-lane-science-ready"
                )
                wait_for(
                    lambda: root_file_exists(lane_science_ready_path)
                    or root_file_exists(client_failure_path)
                    or root_file_exists(
                        workspace["device"] / "iotox-rendezvous/device.failure"
                    )
                    or any(
                        process.poll() is not None
                        for process in processes.values()
                    ),
                    300,
                    "publisher isolated content-lane publications",
                )
                require(
                    root_file_exists(lane_science_ready_path),
                    "publisher chain exited before content-lane publications",
                )
                lane_science_ready = read_root_file(lane_science_ready_path)
                require(
                    re.fullmatch(
                        r"schema=iotox-content-lane-science-publications-v1\n"
                        r"artifact-sha256=[0-9a-f]{64}\n"
                        r"artifact-bytes=8388608\n"
                        r"content-chunks=([1-9][0-9]*)\n"
                        r"content-objects=([1-9][0-9]*)\n"
                        r"cap-1-head-record=[0-9a-f]{64}\n"
                        r"cap-2-head-record=[0-9a-f]{64}\n"
                        r"cap-4-head-record=[0-9a-f]{64}\n"
                        r"cap-8-head-record=[0-9a-f]{64}\n",
                        lane_science_ready,
                    )
                    is not None,
                    "publisher content-lane publication evidence is malformed",
                )
                lane_science_relay = (
                    pair_root / "relay.device.sync-content-lane-science-ready"
                )
                lane_science_relay.write_text(
                    lane_science_ready, encoding="ascii"
                )
                sudo(
                    "install",
                    "-m",
                    "0600",
                    str(lane_science_relay),
                    str(
                        workspace["client"]
                        / "iotox-input/device.sync-content-lane-science-ready"
                    ),
                )
                lane_science_relay.unlink()
            elif scenario == "sync-tree-route-balance":
                balance_ready_path = (
                    workspace["device"]
                    / "iotox-rendezvous/device.sync-route-balance-ready"
                )
                wait_for(
                    lambda: root_file_exists(balance_ready_path)
                    or root_file_exists(client_failure_path)
                    or root_file_exists(
                        workspace["device"]
                        / "iotox-rendezvous/device.failure"
                    )
                    or any(
                        process.poll() is not None
                        for process in processes.values()
                    ),
                    300,
                    "publisher fixed/adaptive balance publications",
                )
                require(
                    root_file_exists(balance_ready_path),
                    "publisher chain exited before route-balance publications",
                )
                balance_relay = pair_root / "relay.device.sync-route-balance-ready"
                balance_relay.write_text(
                    read_root_file(balance_ready_path), encoding="ascii"
                )
                sudo(
                    "install",
                    "-m",
                    "0600",
                    str(balance_relay),
                    str(
                        workspace["client"]
                        / "iotox-input/device.sync-route-balance-ready"
                    ),
                )
                balance_relay.unlink()
            elif scenario in {
                "sync-tree-route-population",
                "sync-tree-route-population-loss",
                "sync-tree-route-loss-admission",
                "sync-tree-route-startup-admission",
                "sync-tree-route-throughput",
                "sync-tree-route-concurrent-cancel",
                "sync-tree-route-common-link-fairness",
            }:
                population_ready_path = (
                    workspace["device"]
                    / "iotox-rendezvous/device.sync-route-population-ready"
                )
                wait_for(
                    lambda: root_file_exists(population_ready_path)
                    or root_file_exists(client_failure_path)
                    or root_file_exists(
                        workspace["device"]
                        / "iotox-rendezvous/device.failure"
                    )
                    or any(
                        process.poll() is not None
                        for process in processes.values()
                    ),
                    600,
                    "publisher route-population publications",
                )
                require(
                    root_file_exists(population_ready_path),
                    "publisher chain exited before route-population publications",
                )
                population_relay = (
                    pair_root / "relay.device.sync-route-population-ready"
                )
                population_relay.write_text(
                    read_root_file(population_ready_path), encoding="ascii"
                )
                sudo(
                    "install",
                    "-m",
                    "0600",
                    str(population_relay),
                    str(
                        workspace["client"]
                        / "iotox-input/device.sync-route-population-ready"
                    ),
                )
                population_relay.unlink()
            sync_completion_timeout = (
                2100
                if scenario == "sync-tree-route-throughput"
                else 1200
                if scenario in CONTENT_LANE_SCIENCE_SCENARIOS
                else 1800
                if scenario in {
                    "sync-tree-route-population",
                    "sync-tree-route-population-loss",
                    "sync-tree-route-loss-admission",
                    "sync-tree-route-startup-admission",
                    "sync-tree-route-concurrent-cancel",
                    "sync-tree-route-common-link-fairness",
                }
                else 1500
                if scenario == "sync-tree-route-balance"
                else 600
                if scenario in REPEATED_RANGE_LOSS_COUNTS
                or scenario in CONTENT_RESTART_SCENARIOS
                else 300
            )
            sync_completion_terminal = lambda: (
                root_file_exists(completed_path)
                or root_file_exists(client_failure_path)
                or balance_phase_is_terminal()
                or any(
                    process.poll() is not None
                    for process in processes.values()
                )
                or (
                    scenario == "sync-file-disconnect"
                    and root_file_exists(post_retry_failure)
                )
            )
            if scenario in REPEATED_RANGE_LOSS_COUNTS:
                sync_completion_deadline = (
                    time.monotonic() + sync_completion_timeout
                )
                while not sync_completion_terminal():
                    if time.monotonic() >= sync_completion_deadline:
                        initial_live = {}
                        for role in ("client", "device"):
                            for surface in ("status", "routes"):
                                live_path = (
                                    workspace[role]
                                    / "iotox-rendezvous"
                                    / f"{role}.sync-initial-live-{surface}"
                                )
                                if root_file_exists(live_path):
                                    initial_live[f"{role}-{surface}"] = (
                                        read_root_file(live_path).strip()
                                    )
                        raise RuntimeError(
                            "timeout waiting for client convergence and "
                            "exact-token activation: "
                            f"initial-live={initial_live}"
                        )
                    time.sleep(0.05)
            else:
                wait_for(
                    sync_completion_terminal,
                    sync_completion_timeout,
                    "client convergence and exact-token activation",
                )
            require(
                not balance_phase_is_terminal(),
                "client route-balance phase failed: "
                + (
                    read_root_file(balance_phase_path).strip()
                    if root_file_exists(balance_phase_path)
                    else "missing diagnostic"
                ),
            )
            require(
                not root_file_exists(client_failure_path),
                "client synchronization guest failed: "
                + (
                    read_root_file(client_failure_path).strip()
                    if root_file_exists(client_failure_path)
                    else "missing diagnostic"
                ),
            )
            require(
                root_file_exists(completed_path),
                "fresh-epoch synchronization retry failed: "
                f"chain-exits={{"
                + ", ".join(
                    f"{role}={process.poll()}"
                    for role, process in processes.items()
                    if process.poll() is not None
                )
                + "}",
            )
            completed = read_root_file(completed_path)
            completion_publication = published.strip()
            if scenario in CONTENT_MULTI_SOURCE_SCENARIOS:
                completion_publication = completion_publication.replace(
                    "\ncontent-primary-chunks=",
                    "\ncontent-atomic-pull=1\ncontent-primary-chunks=",
                    1,
                )
            if scenario in SYNC_CANCELLATION_SCENARIOS:
                require(
                    completed.startswith(
                        "cancellation=1\nconvergence=0\nactivation=0\n"
                    )
                    and completion_publication in completed,
                    "client synchronization cancellation does not bind publication",
                )
            else:
                require(
                    completed.startswith("convergence=1\nactivation=1\n")
                    and completion_publication in completed,
                    "client synchronization completion does not bind publication",
                )
            if scenario in CONTENT_LANE_SCIENCE_SCENARIOS:
                lane_science_phase_order = (
                    "8,4,2,1"
                    if scenario == "sync-content-lane-science-reverse"
                    else "1,2,4,8"
                )
                lane_science_completion = re.search(
                    r"^content-lane-science=1\n"
                    rf"content-lane-science-phase-order={lane_science_phase_order}\n"
                    r"content-lane-science-restarts=0\n"
                    r"content-lane-science-activations=4\n"
                    r"content-lane-science-cap-1-duration-ms=([1-9][0-9]*)\n"
                    r"content-lane-science-cap-1-bps=([1-9][0-9]*)\n"
                    r"content-lane-science-cap-1-active=([1-9][0-9]*)\n"
                    r"content-lane-science-cap-2-duration-ms=([1-9][0-9]*)\n"
                    r"content-lane-science-cap-2-bps=([1-9][0-9]*)\n"
                    r"content-lane-science-cap-2-active=([1-9][0-9]*)\n"
                    r"content-lane-science-cap-4-duration-ms=([1-9][0-9]*)\n"
                    r"content-lane-science-cap-4-bps=([1-9][0-9]*)\n"
                    r"content-lane-science-cap-4-active=([1-9][0-9]*)\n"
                    r"content-lane-science-cap-8-duration-ms=([1-9][0-9]*)\n"
                    r"content-lane-science-cap-8-bps=([1-9][0-9]*)\n"
                    r"content-lane-science-cap-8-active=([1-9][0-9]*)\n"
                    r"content-lane-science-summary-sha256=([0-9a-f]{64})$",
                    completed,
                    re.MULTILINE,
                )
                require(
                    lane_science_completion is not None,
                    "client content-lane science completion is malformed",
                )
                assert lane_science_completion is not None
                for cap, duration_group, bps_group, active_group in (
                    (1, 1, 2, 3),
                    (2, 4, 5, 6),
                    (4, 7, 8, 9),
                    (8, 10, 11, 12),
                ):
                    duration = int(lane_science_completion.group(duration_group))
                    measured_bps = int(lane_science_completion.group(bps_group))
                    active = int(lane_science_completion.group(active_group))
                    require(
                        measured_bps == (8 * 1024 * 1024 * 1000) // duration,
                        "content-lane throughput does not bind measured duration",
                    )
                    require(
                        1 <= active <= cap,
                        "content-lane maximum exceeds its requested cap",
                    )
                if scenario == "sync-content-ratox-post-bulk-admission":
                    post_bulk = re.search(
                        r"^content-ratox-post-bulk=1\n"
                        r"content-ratox-post-bulk-cap=8\n"
                        r"content-ratox-post-bulk-samples=40\n"
                        r"content-ratox-post-bulk-origin-us=([1-9][0-9]*)\n"
                        r"content-ratox-post-bulk-origin-to-open-sent-us=([0-9]+)\n"
                        r"content-ratox-post-bulk-origin-to-opened-us=([1-9][0-9]*)\n"
                        r"content-ratox-post-bulk-open-round-trip-us=([1-9][0-9]*)\n"
                        r"content-ratox-post-bulk-online-epoch=([1-9][0-9]*)\n"
                        r"content-ratox-post-bulk-readiness-sha256=([0-9a-f]{64})\n"
                        r"content-ratox-post-bulk-capture-sha256=([0-9a-f]{64})\n"
                        r"content-ratox-post-bulk-admission-sha256=([0-9a-f]{64})$",
                        completed,
                        re.MULTILINE,
                    )
                    require(
                        post_bulk is not None
                        and int(post_bulk.group(2)) <= 1_000_000
                        and int(post_bulk.group(3)) <= 6_000_000
                        and int(post_bulk.group(4)) <= 5_000_000,
                        "fresh post-bulk Ratox admission is malformed or late",
                    )
            if scenario in SIGNED_UPDATE_SCENARIOS:
                update_restarts = 6 if scenario == "update-service" else 1
                update_pattern = (
                    r"^signed-update=1\n"
                    r"update-release-sequence=1\n"
                    r"update-startup-disposition=health-window-opened\n"
                    r"update-confirmed=1\n"
                    r"update-current-sha256=([0-9a-f]{64})\n"
                    rf"update-restarts={update_restarts}\n"
                    r"update-feature-advertised=1\n"
                    r"update-remote-stage=1\n"
                    r"update-remote-sender-epoch=[1-9][0-9]*\n"
                    r"update-remote-message-id=[1-9][0-9]*"
                )
                if scenario == "update-service":
                    update_pattern += (
                        r"\nupdate-service=1"
                        r"\nupdate-service-pre-ready-exit=1"
                        r"\nupdate-service-agent-death=1"
                        r"\nupdate-service-parent-death=1"
                        r"\nupdate-service-health-expiry=1"
                        r"\nupdate-service-ready=1"
                        r"\nupdate-service-confirmed-recovery=1"
                        r"\nupdate-service-rollback-count=3"
                        r"\nupdate-service-payload-kind=linux-service-v1"
                        r"\nupdate-service-image-sealed=1"
                    )
                update_pattern += r"$"
                update_completion = re.search(
                    update_pattern,
                    completed,
                    re.MULTILINE,
                )
                payload_match = re.search(
                    r"^update-payload-sha256=([0-9a-f]{64})$",
                    completed,
                    re.MULTILINE,
                )
                require(
                    update_completion is not None
                    and payload_match is not None
                    and update_completion.group(1) == payload_match.group(1),
                    "client signed-update lifecycle evidence is invalid",
                )
            if scenario in {
                "sync-tree-route-loss",
                "sync-tree-route-private-actual-tor-loss",
            }:
                route_resume_completion = re.search(
                    r"^route-loss=1\n"
                    r"route-loss-position-bytes=([1-9][0-9]*)\n"
                    r"route-retained-partials=0\n"
                    r"route-retained-attempts=([12])\n"
                    r"route-retained-bytes=([1-9][0-9]*)\n"
                    r"route-retention-fallbacks=0\n"
                    r"route-resumed-attempts=([12])\n"
                    r"route-resumed-bytes=([1-9][0-9]*)\n"
                    r"route-carrier-losses=1\n"
                    r"route-reassignments=1\n"
                    r"route-stale-terminals=[1-9][0-9]*\n"
                    r"route-recoveries=1\n"
                    r"route-final-carrier=([0-9A-F]{64})\n"
                    r"route-stopped-carrier=([0-9A-F]{64})$",
                    completed,
                    re.MULTILINE,
                )
                require(
                    route_resume_completion is not None
                    and route_resume_completion.group(2)
                    == route_resume_completion.group(4)
                    and route_resume_completion.group(3)
                    == route_resume_completion.group(5)
                    and int(route_resume_completion.group(3))
                    >= int(route_resume_completion.group(1))
                    and route_resume_completion.group(6)
                    != route_resume_completion.group(7),
                    "client route-loss completion evidence is invalid",
                )
            if scenario == "sync-tree-route-balance":
                balance_match = re.search(
                    r"^route-balance=1\n"
                    r"route-balance-artifact-bytes=8259\n"
                    r"route-balance-phase-order=adaptive-fixed\n"
                    r"route-balance-fixed-same-carrier=1\n"
                    r"route-balance-adaptive-distinct-carriers=1\n"
                    r"route-balance-fixed-carrier-a=([0-9A-F]{64})\n"
                    r"route-balance-fixed-carrier-b=([0-9A-F]{64})\n"
                    r"route-balance-adaptive-carrier-a=([0-9A-F]{64})\n"
                    r"route-balance-adaptive-carrier-b=([0-9A-F]{64})\n"
                    r"route-balance-fixed-selections=2\n"
                    r"route-balance-adaptive-selections=2\n"
                    r"route-balance-fixed-duration-ms=[1-9][0-9]*\n"
                    r"route-balance-adaptive-duration-ms=[1-9][0-9]*\n"
                    r"route-balance-activations=4\n"
                    r"route-balance-fixed-head-retries=(?:[0-9]|1[0-6])\n"
                    r"route-balance-adaptive-head-retries=(?:[0-9]|1[0-6])$",
                    completed,
                    re.MULTILINE,
                )
                require(
                    balance_match is not None
                    and balance_match.group(1) == balance_match.group(2)
                    and balance_match.group(3) != balance_match.group(4),
                    "client route-balance completion evidence is invalid",
                )
            if scenario == "sync-tree-route-population":
                require(
                    re.search(
                        r"^route-population=1\n"
                        r"route-population-jobs=8\n"
                        r"route-population-artifact-bytes=([1-9][0-9]*)\n"
                        r"route-population-fixed-pattern=00001111\n"
                        r"route-population-adaptive-pattern=01010101\n"
                        r"route-population-fixed-max-prefix-imbalance=4\n"
                        r"route-population-adaptive-max-prefix-imbalance=1\n"
                        r"route-population-fixed-progress-jobs=8\n"
                        r"route-population-adaptive-progress-jobs=8\n"
                        r"route-population-fixed-progress-observation-spread-ms=[0-9]+\n"
                        r"route-population-adaptive-progress-observation-spread-ms=[0-9]+\n"
                        r"route-population-fixed-duration-ms=[1-9][0-9]*\n"
                        r"route-population-adaptive-duration-ms=[1-9][0-9]*\n"
                        r"route-population-activations=16\n"
                        r"route-population-fixed-resource-sha256=[0-9a-f]{64}\n"
                        r"route-population-adaptive-resource-sha256=[0-9a-f]{64}$",
                        completed,
                        re.MULTILINE,
                    )
                    is not None,
                    "client route-population completion evidence is invalid",
                )
            if scenario == "sync-tree-route-population-loss":
                require(
                    re.search(
                        r"^route-population-loss=1\n"
                        r"route-population-loss-jobs=8\n"
                        r"route-population-loss-artifact-bytes=524355\n"
                        r"route-population-loss-pattern=00001111\n"
                        r"route-population-loss-affected-jobs=4\n"
                        r"route-population-loss-carrier-losses=1\n"
                        r"route-population-loss-reassignments=4\n"
                        r"route-population-loss-stale-terminals=[1-9][0-9]*\n"
                        r"route-population-loss-recoveries=1\n"
                        r"route-population-loss-fixed-selections=12\n"
                        r"route-population-loss-activations=8\n"
                        r"route-population-loss-work-before=16\n"
                        r"route-population-loss-work-after=0\n"
                        r"route-population-loss-fault-delay-ms=750\n"
                        r"route-population-loss-fault-position-bytes=[1-9][0-9]*\n"
                        r"route-population-loss-duration-ms=[1-9][0-9]*\n"
                        r"route-population-loss-stopped-carrier=[0-9A-F]{64}\n"
                        r"route-population-loss-resource-sha256=[0-9a-f]{64}\n"
                        r"route-loss-admission-started-jobs=0\n"
                        r"route-loss-admission-ready-bulk=0\n"
                        r"route-loss-admission-surviving-carrier=$",
                        completed,
                        re.MULTILINE,
                    )
                    is not None,
                    "client route-population loss completion evidence is invalid",
                )
            if scenario == "sync-tree-route-loss-admission":
                admission_match = re.search(
                    r"^route-population-loss=1\n"
                    r"route-population-loss-jobs=4\n"
                    r"route-population-loss-artifact-bytes=524355\n"
                    r"route-population-loss-pattern=00\n"
                    r"route-population-loss-affected-jobs=2\n"
                    r"route-population-loss-carrier-losses=1\n"
                    r"route-population-loss-reassignments=2\n"
                    r"route-population-loss-stale-terminals=[1-9][0-9]*\n"
                    r"route-population-loss-recoveries=1\n"
                    r"route-population-loss-fixed-selections=6\n"
                    r"route-population-loss-activations=4\n"
                    r"route-population-loss-work-before=4\n"
                    r"route-population-loss-work-after=0\n"
                    r"route-population-loss-fault-delay-ms=1\n"
                    r"route-population-loss-fault-position-bytes=[1-9][0-9]*\n"
                    r"route-population-loss-duration-ms=[1-9][0-9]*\n"
                    r"route-population-loss-stopped-carrier=([0-9A-F]{64})\n"
                    r"route-population-loss-resource-sha256=[0-9a-f]{64}\n"
                    r"route-loss-admission-started-jobs=2\n"
                    r"route-loss-admission-ready-bulk=1\n"
                    r"route-loss-admission-surviving-carrier=([0-9A-F]{64})$",
                    completed,
                    re.MULTILINE,
                )
                require(
                    admission_match is not None
                    and admission_match.group(1) != admission_match.group(2),
                    "client route-loss admission completion evidence is invalid",
                )
            if scenario == "sync-tree-route-startup-admission":
                require(
                    re.search(
                        r"^route-startup-admission=1\n"
                        r"route-startup-admission-jobs=2\n"
                        r"route-startup-admission-artifact-bytes=16777283\n"
                        r"route-startup-admission-delay-ms=20000\n"
                        r"route-startup-admission-restart-count=1\n"
                        r"route-startup-admission-ready-bulk-before=1\n"
                        r"route-startup-admission-ready-bulk-after=2\n"
                        r"route-startup-admission-stable-samples=(?:1[0-9]|[2-9][0-9]|[1-9][0-9]{2,})\n"
                        r"route-startup-admission-carrier=[0-9A-F]{64}\n"
                        r"route-startup-admission-live-jobs-after-join=2\n"
                        r"route-startup-admission-preserved-carriers=2\n"
                        r"route-startup-admission-adaptive-selections=2\n"
                        r"route-startup-admission-activations=2\n"
                        r"route-startup-admission-work-before=4\n"
                        r"route-startup-admission-work-after=0\n"
                        r"route-startup-admission-duration-ms=[1-9][0-9]*\n"
                        r"route-startup-admission-resource-sha256=[0-9a-f]{64}$",
                        completed,
                        re.MULTILINE,
                    )
                    is not None,
                    "client route-startup admission completion evidence is invalid",
                )
            if scenario == "sync-tree-route-throughput":
                require(
                    re.search(
                        r"^route-throughput=1\n"
                        r"route-throughput-jobs-per-phase=2\n"
                        r"route-throughput-phases=4\n"
                        r"route-throughput-artifact-bytes=16777283\n"
                        r"route-throughput-phase-order=fixed-a,adaptive-a,adaptive-b,fixed-b\n"
                        r"route-throughput-restart-hold-ms=5000\n"
                        r"route-throughput-fixed-patterns=00,00\n"
                        r"route-throughput-adaptive-patterns=01,01\n"
                        r"route-throughput-fixed-total-duration-ms=[1-9][0-9]*\n"
                        r"route-throughput-adaptive-total-duration-ms=[1-9][0-9]*\n"
                        r"route-throughput-fixed-artifact-bps=[1-9][0-9]*\n"
                        r"route-throughput-adaptive-artifact-bps=[1-9][0-9]*\n"
                        r"route-throughput-adaptive-speedup-ppm=[1-9][0-9]*\n"
                        r"route-throughput-activations=8$",
                        completed,
                        re.MULTILINE,
                    )
                    is not None,
                    "client route-throughput completion evidence is invalid",
                )
            if scenario in SYNC_CONCURRENT_CANCEL_SCENARIOS:
                require(
                    re.search(
                        r"^route-concurrent-cancel=1\n"
                        r"route-concurrent-cancel-jobs=8\n"
                        rf"route-concurrent-cancel-artifact-bytes="
                        rf"{SYNC_CONCURRENT_CANCEL_ARTIFACT_BYTES[scenario]}\n"
                        r"route-concurrent-cancel-requested=4\n"
                        r"route-concurrent-cancel-completed=4\n"
                        r"route-concurrent-cancel-survivors=4\n"
                        r"route-concurrent-cancel-survivor-activations=4\n"
                        r"route-concurrent-cancel-pattern=01010101\n"
                        r"route-concurrent-cancel-route-zero=2\n"
                        r"route-concurrent-cancel-route-one=2\n"
                        r"route-concurrent-cancel-tail-ms=(?:[0-9]|[1-9][0-9]{1,2}|[1-4][0-9]{3}|5000)\n"
                        r"route-concurrent-cancel-work-before=[1-9][0-9]*\n"
                        r"route-concurrent-cancel-work-after=0\n"
                        r"route-concurrent-cancel-reassignments-delta=0\n"
                        r"route-concurrent-cancel-adaptive-selections=8\n"
                        r"route-concurrent-cancel-resource-sha256=[0-9a-f]{64}$",
                        completed,
                        re.MULTILINE,
                    )
                    is not None,
                    "client concurrent-cancellation completion evidence is invalid",
                )
            if scenario == "sync-tree-route-cancel":
                require(
                    re.search(
                        r"^route-cancel=1\n"
                        r"route-cancel-carrier=[0-9A-F]{64}\n"
                        r"route-cancel-worker-id=[1-9][0-9]*\n"
                        r"route-cancel-tail-ms=(?:[0-9]|[1-9][0-9]{1,2}|[1-4][0-9]{3}|5000)\n"
                        r"route-cancel-work-before=[1-9][0-9]*\n"
                        r"route-cancel-work-after=0\n"
                        r"route-cancel-reassignments-delta=0\n"
                        r"route-cancel-adaptive-selections=1$",
                        completed,
                        re.MULTILINE,
                    )
                    is not None,
                    "client route-cancellation completion evidence is invalid",
                )
            if scenario == "sync-tree-route-loss-cancel":
                loss_cancel = re.search(
                    r"^route-cancel=1\n"
                    r"route-cancel-carrier=([0-9A-F]{64})\n"
                    r"route-cancel-worker-id=[1-9][0-9]*\n"
                    r"route-cancel-tail-ms=(?:[0-9]|[1-9][0-9]{1,2}|[1-4][0-9]{3}|5000)\n"
                    r"route-cancel-work-before=[1-9][0-9]*\n"
                    r"route-cancel-work-after=0\n"
                    r"route-cancel-reassignments-delta=0\n"
                    r"route-cancel-adaptive-selections=2\n"
                    r"route-loss-before-cancel=1\n"
                    r"route-loss-position-bytes=[1-9][0-9]*\n"
                    r"route-carrier-losses=1\n"
                    r"route-reassignments=1\n"
                    r"route-stale-terminals=[1-9][0-9]*\n"
                    r"route-recoveries=1\n"
                    r"route-final-carrier=([0-9A-F]{64})\n"
                    r"route-stopped-carrier=([0-9A-F]{64})$",
                    completed,
                    re.MULTILINE,
                )
                require(
                    loss_cancel is not None
                    and loss_cancel.group(1) == loss_cancel.group(2)
                    and loss_cancel.group(1) != loss_cancel.group(3),
                    "client loss-before-cancel completion evidence is invalid",
                )
            if scenario == "sync-tree-route-cancel-loss":
                cancel_loss = re.search(
                    r"^route-cancel=1\n"
                    r"route-cancel-carrier=([0-9A-F]{64})\n"
                    r"route-cancel-worker-id=[1-9][0-9]*\n"
                    r"route-cancel-tail-ms=(?:[0-9]|[1-9][0-9]{1,2}|[1-4][0-9]{3}|5000)\n"
                    r"route-cancel-work-before=[1-9][0-9]*\n"
                    r"route-cancel-work-after=0\n"
                    r"route-cancel-reassignments-delta=0\n"
                    r"route-cancel-adaptive-selections=1\n"
                    r"route-cancel-before-loss=1\n"
                    r"route-loss-position-bytes=0\n"
                    r"route-carrier-losses=1\n"
                    r"route-reassignments=0\n"
                    r"route-stale-terminals=[1-9][0-9]*\n"
                    r"route-recoveries=1\n"
                    r"route-final-carrier=([0-9A-F]{64})\n"
                    r"route-stopped-carrier=([0-9A-F]{64})$",
                    completed,
                    re.MULTILINE,
                )
                require(
                    cancel_loss is not None
                    and cancel_loss.group(1) == cancel_loss.group(2)
                    == cancel_loss.group(3),
                    "client cancel-before-loss completion evidence is invalid",
                )
            if scenario in SYNC_ROUTE_CANCEL_RACE_SCENARIOS:
                fault_delay, cancel_delay, required_outcome = (
                    SYNC_ROUTE_CANCEL_RACE_SCENARIOS[scenario]
                )
                cancel_race = re.search(
                    r"^route-cancel=1\n"
                    r"route-cancel-carrier=([0-9A-F]{64})\n"
                    r"route-cancel-worker-id=[1-9][0-9]*\n"
                    r"route-cancel-tail-ms=(?:[0-9]|[1-9][0-9]{1,2}|[1-4][0-9]{3}|5000)\n"
                    r"route-cancel-work-before=[1-9][0-9]*\n"
                    r"route-cancel-work-after=0\n"
                    r"route-cancel-reassignments-delta=([01])\n"
                    r"route-cancel-adaptive-selections=([12])\n"
                    r"route-cancel-loss-race=1\n"
                    r"route-cancel-loss-race-outcome=(cancel-first|loss-first)\n"
                    rf"route-cancel-loss-race-fault-delay-ms={fault_delay}\n"
                    rf"route-cancel-loss-race-cancel-delay-ms={cancel_delay}\n"
                    r"route-cancel-loss-race-cleanup-retries=([01])\n"
                    r"route-loss-position-bytes=[1-9][0-9]*\n"
                    r"route-carrier-losses=1\n"
                    r"route-reassignments=([01])\n"
                    r"route-stale-terminals=[0-9]+\n"
                    r"route-recoveries=1\n"
                    r"route-final-carrier=([0-9A-F]{64})\n"
                    r"route-stopped-carrier=([0-9A-F]{64})$",
                    completed,
                    re.MULTILINE,
                )
                require(
                    cancel_race is not None
                    and int(cancel_race.group(3))
                    == 1 + int(cancel_race.group(2))
                    and cancel_race.group(2) == cancel_race.group(6)
                    and cancel_race.group(1) == cancel_race.group(8)
                    and (
                        required_outcome is None
                        or cancel_race.group(4) == required_outcome
                    )
                    and (
                        cancel_race.group(4) == "cancel-first"
                        and cancel_race.group(2) == "0"
                        and cancel_race.group(7) == cancel_race.group(8)
                        or cancel_race.group(4) == "loss-first"
                        and cancel_race.group(2) == "1"
                        and cancel_race.group(7) != cancel_race.group(8)
                    ),
                    "client cancel/loss race completion evidence is invalid",
                )
            if not range_loss_primed:
                command_file = pair_root / "device.sync-finished"
                command_file.write_text(completed, encoding="ascii")
                sudo(
                    "install",
                    "-m",
                    "0600",
                    str(command_file),
                    str(workspace["device"] / "iotox-input/sync-finished"),
                )
                command_file.unlink()
            if scenario in {
                "sync-tree-adversity",
                "sync-tree-pressure",
                "sync-tree-quota",
                "sync-tree-object-quota",
                "sync-tree-read-only",
                "sync-tree-memory",
                "sync-tree-source-corrupt",
                "sync-tree-destination-corrupt",
                "sync-tree-control-replay",
            }:
                def relay_sync_marker(
                    source_role: str,
                    marker: str,
                    destination_role: str,
                    description: str,
                ) -> str:
                    source = (
                        workspace[source_role]
                        / f"iotox-rendezvous/{marker}"
                    )
                    failures = {
                        role: workspace[role]
                        / f"iotox-rendezvous/{role}.failure"
                        for role in ("client", "device")
                    }
                    wait_for(
                        lambda: root_file_exists(source)
                        or any(root_file_exists(path) for path in failures.values())
                        or any(process.poll() is not None for process in processes.values()),
                        300,
                        description,
                    )
                    for failed_role, failure_path in failures.items():
                        require(
                            not root_file_exists(failure_path),
                            f"{failed_role} synchronization guest failed: "
                            + (
                                read_root_file(failure_path).strip()
                                if root_file_exists(failure_path)
                                else "missing diagnostic"
                            ),
                        )
                    require(
                        root_file_exists(source),
                        f"{source_role} chain exited before {description}",
                    )
                    contents = read_root_file(source)
                    relay = pair_root / f"relay.{marker}"
                    relay.write_text(contents, encoding="ascii")
                    sudo(
                        "install",
                        "-m",
                        "0600",
                        str(relay),
                        str(
                            workspace[destination_role]
                            / f"iotox-input/{marker}"
                        ),
                    )
                    relay.unlink()
                    return contents

            if scenario == "sync-tree-adversity":
                relay_sync_marker(
                    "device",
                    "device.sync-adversity-generation-2a",
                    "client",
                    "publisher generation 2A publication",
                )
                relay_sync_marker(
                    "client",
                    "client.sync-adversity-generation-2a",
                    "device",
                    "subscriber generation 2A activation",
                )
                relay_sync_marker(
                    "device",
                    "device.sync-adversity-stale",
                    "client",
                    "publisher stale generation presentation",
                )
                relay_sync_marker(
                    "client",
                    "client.sync-adversity-stale",
                    "device",
                    "subscriber rollback refusal",
                )
                relay_sync_marker(
                    "device",
                    "device.sync-adversity-fork",
                    "client",
                    "publisher equal-generation fork presentation",
                )
                relay_sync_marker(
                    "client",
                    "client.sync-adversity-fork",
                    "device",
                    "subscriber fork refusal",
                )
                relay_sync_marker(
                    "device",
                    "device.sync-adversity-generation-3",
                    "client",
                    "publisher generation 3 publication",
                )
                relay_sync_marker(
                    "client",
                    "client.sync-adversity-finished",
                    "device",
                    "subscriber ENOSPC recovery",
                )
            if scenario == "sync-tree-pressure":
                relay_sync_marker(
                    "device",
                    "device.sync-pressure-ready",
                    "client",
                    "publisher pressure namespaces and held transaction lock",
                )
                relay_sync_marker(
                    "device",
                    "device.sync-pressure-saturated",
                    "client",
                    "publisher ordinary worker saturation",
                )
                relay_sync_marker(
                    "device",
                    "device.sync-pressure-refused",
                    "client",
                    "publisher ordinary work refusal and drain",
                )
                relay_sync_marker(
                    "client",
                    "client.sync-pressure-finished",
                    "device",
                    "subscriber exact retry and dual activation",
                )
            if scenario in SYNC_TREE_QUOTA_SCENARIOS:
                relay_sync_marker(
                    "device",
                    "device.sync-quota-candidate",
                    "client",
                    "publisher generation-2 quota candidate",
                )
                relay_sync_marker(
                    "client",
                    "client.sync-quota-finished",
                    "device",
                    "subscriber quota refusal and state preservation",
                )
            if scenario == "sync-tree-read-only":
                relay_sync_marker(
                    "device",
                    "device.sync-read-only-candidate",
                    "client",
                    "publisher generation-2 read-only candidate",
                )
                relay_sync_marker(
                    "client",
                    "client.sync-read-only-finished",
                    "device",
                    "subscriber read-only refusal and exact recovery",
                )
            if scenario == "sync-tree-memory":
                relay_sync_marker(
                    "device",
                    "device.sync-memory-candidate",
                    "client",
                    "publisher maximum-entry memory candidate",
                )
                relay_sync_marker(
                    "client",
                    "client.sync-memory-finished",
                    "device",
                    "subscriber maximum-entry memory observation",
                )
                relay_sync_marker(
                    "device",
                    "device.sync-memory-finished",
                    "client",
                    "publisher final memory observation",
                )
            if scenario == "sync-tree-source-corrupt":
                relay_sync_marker(
                    "device",
                    "device.sync-source-corrupt-candidate",
                    "client",
                    "publisher corrupt generation-2 source candidate",
                )
                relay_sync_marker(
                    "client",
                    "client.sync-source-corrupt-refused",
                    "device",
                    "subscriber source-corruption refusal",
                )
                relay_sync_marker(
                    "device",
                    "device.sync-source-corrupt-recovered",
                    "client",
                    "publisher source repair and exact republication",
                )
                relay_sync_marker(
                    "client",
                    "client.sync-source-corrupt-finished",
                    "device",
                    "subscriber exact retry and activation",
                )
            if scenario == "sync-tree-destination-corrupt":
                relay_sync_marker(
                    "device",
                    "device.sync-destination-corrupt-candidate",
                    "client",
                    "publisher generation-2 destination-corruption candidate",
                )
                relay_sync_marker(
                    "client",
                    "client.sync-destination-corrupt-failed",
                    "device",
                    "subscriber destination-corruption refusal",
                )
                relay_sync_marker(
                    "device",
                    "device.sync-destination-corrupt-retry-ready",
                    "client",
                    "publisher observation of destination-corruption failure",
                )
                relay_sync_marker(
                    "client",
                    "client.sync-destination-corrupt-finished",
                    "device",
                    "subscriber destination-corruption retry and activation",
                )
            if scenario == "sync-tree-control-replay":
                relay_sync_marker(
                    "device",
                    "device.sync-control-replay-candidate",
                    "client",
                    "publisher generation-2 control-replay candidate",
                )
                relay_sync_marker(
                    "client",
                    "client.sync-control-object-replays-sent",
                    "device",
                    "subscriber duplicate object requests",
                )
                relay_sync_marker(
                    "device",
                    "device.sync-control-object-replays-observed",
                    "client",
                    "publisher exact object-request replay observation",
                )
                relay_sync_marker(
                    "client",
                    "client.sync-control-head-replay-sent",
                    "device",
                    "subscriber duplicate HEAD request",
                )
                relay_sync_marker(
                    "device",
                    "device.sync-control-head-replay-observed",
                    "client",
                    "publisher exact HEAD-request replay observation",
                )
                relay_sync_marker(
                    "client",
                    "client.sync-control-conflict-sent",
                    "device",
                    "subscriber conflicting HEAD-request replay",
                )
                relay_sync_marker(
                    "device",
                    "device.sync-control-conflict-observed",
                    "client",
                    "publisher replay-conflict refusal",
                )
                relay_sync_marker(
                    "client",
                    "client.sync-control-replay-finished",
                    "device",
                    "subscriber replay-safe convergence and activation",
                )
            if scenario in SYNC_RANGE_SCENARIOS:
                range_published_path = (
                    workspace["device"]
                    / "iotox-rendezvous/device.sync-range-published"
                )
                range_publish_failed_path = (
                    workspace["device"]
                    / "iotox-rendezvous/device.sync-range-publish-failed"
                )
                wait_for(
                    lambda: root_file_exists(range_published_path)
                    or root_file_exists(range_publish_failed_path)
                    or any(
                        process.poll() is not None
                        for process in processes.values()
                    ),
                    240,
                    "device signed successor publication",
                )
                require(
                    not root_file_exists(range_publish_failed_path),
                    "device successor publication failed: "
                    + (
                        read_root_file(range_publish_failed_path).strip()
                        if root_file_exists(range_publish_failed_path)
                        else "missing diagnostic"
                    ),
                )
                require(
                    root_file_exists(range_published_path),
                    "device chain exited before successor publication",
                )
                range_published = read_root_file(range_published_path)
                require(
                    re.fullmatch(
                        r"generation=2\n"
                        r"head-record=[0-9a-f]{64}\n"
                        r"artifact-sha256=[0-9a-f]{64}\n"
                        r"manifest-sha256=[0-9a-f]{64}\n"
                        rf"artifact-bytes={SYNC_SCENARIOS[scenario]}\n"
                        r"manifest-bytes=[1-9][0-9]*\n",
                        range_published,
                    )
                    is not None,
                    "device successor publication evidence is invalid",
                )
                if scenario in {
                    "sync-file-range-late-route-loss",
                    "sync-file-range-repeated-route-loss",
                    "sync-file-range-triple-route-loss",
                    "sync-file-range-restart-resume",
                }:
                    # Keep the 4 MiB prerequisite fast, then make the selected
                    # point in the 1 MiB successor observable. Repeated loss
                    # additionally uses the protocol's bounded qualification
                    # hold while the first stopped identity recovers.
                    sudo(
                        str(HOST_BIN / "tc"),
                        "qdisc",
                        "replace",
                        "dev",
                        "vm-iotoxc",
                        "root",
                        "netem",
                        "rate",
                        "256kbit",
                        "limit",
                        "1000",
                    )
                if not range_loss_primed:
                    command_file = pair_root / "client.sync-range-start"
                    command_file.write_text(range_published, encoding="ascii")
                    sudo(
                        "install",
                        "-m",
                        "0600",
                        str(command_file),
                        str(
                            workspace["client"]
                            / "iotox-input/sync-range-start"
                        ),
                    )
                    command_file.unlink()
                if scenario == "sync-file-range-restart-resume":
                    range_restart_ready_path = (
                        workspace["client"]
                        / "iotox-rendezvous/client.sync-range-restart-ready"
                    )
                    wait_for(
                        lambda: root_file_exists(range_restart_ready_path)
                        or any(
                            process.poll() is not None
                            for process in processes.values()
                        ),
                        300,
                        "positive bounded-range prefix before daemon restart",
                    )
                    require(
                        root_file_exists(range_restart_ready_path),
                        "client exited before bounded-range restart readiness",
                    )
                    range_restart_ready = read_root_file(
                        range_restart_ready_path
                    )
                    ready_match = re.fullmatch(
                        r"schema=iotox-sync-range-restart-ready-v1\n"
                        r"job=([1-9][0-9]*)\n"
                        r"attempt=([1-9][0-9]*)\n"
                        r"message=([1-9][0-9]*)\n"
                        r"file-id=([0-9a-f]{64})\n"
                        r"position-bytes=([1-9][0-9]*)\n"
                        r"bundle-bytes=1048576\n",
                        range_restart_ready,
                    )
                    require(
                        ready_match is not None
                        and 262_144 <= int(ready_match.group(5)) < 1_048_576,
                        "bounded-range restart readiness is invalid",
                    )

                    command_file = pair_root / "device.sync-observe-range-restart"
                    command_file.write_text(
                        "sync-observe-range-restart=1\n", encoding="ascii"
                    )
                    sudo(
                        "install",
                        "-m",
                        "0600",
                        str(command_file),
                        str(
                            workspace["device"]
                            / "iotox-input/sync-observe-range-restart"
                        ),
                    )
                    command_file.unlink()
                    range_restart_armed = (
                        workspace["device"]
                        / "iotox-rendezvous/device.sync-range-restart-armed"
                    )
                    wait_for(
                        lambda: root_file_exists(range_restart_armed),
                        120,
                        "publisher range-restart observation arm",
                    )

                    command_file = pair_root / "client.sync-range-restart"
                    command_file.write_text(
                        "sync-range-restart=1\n", encoding="ascii"
                    )
                    sudo(
                        "install",
                        "-m",
                        "0600",
                        str(command_file),
                        str(
                            workspace["client"]
                            / "iotox-input/sync-range-restart"
                        ),
                    )
                    command_file.unlink()
                    range_crash_path = (
                        workspace["client"]
                        / "iotox-rendezvous/client.sync-range-crash-state"
                    )
                    range_offline_path = (
                        workspace["device"]
                        / "iotox-rendezvous/device.sync-range-restart-offline"
                    )
                    wait_for(
                        lambda: root_file_exists(range_crash_path)
                        and root_file_exists(range_offline_path),
                        180,
                        "range subscriber crash and publisher offline observation",
                    )
                    range_crash = read_root_file(range_crash_path)
                    crash_match = re.fullmatch(
                        r"schema=iotox-sync-range-crash-state-v1\n"
                        r"stop-status=137\n"
                        r"transport-temporaries=0\n"
                        r"canonical-partials=1\n"
                        r"interrupted-range-bytes=([1-9][0-9]*)\n"
                        r"range-bundle-bytes=1048576\n"
                        r"attempt-journal-present=1\n"
                        r"first-job=([1-9][0-9]*)\n"
                        r"first-attempt=([1-9][0-9]*)\n"
                        r"first-message=([1-9][0-9]*)\n"
                        r"first-file-id=([0-9a-f]{64})\n",
                        range_crash,
                    )
                    require(
                        crash_match is not None
                        and int(crash_match.group(1))
                        >= int(ready_match.group(5))
                        and int(crash_match.group(1)) < 1_048_576
                        and crash_match.group(2) == ready_match.group(1)
                        and crash_match.group(3) == ready_match.group(2)
                        and crash_match.group(4) == ready_match.group(3)
                        and crash_match.group(5) == ready_match.group(4),
                        "bounded-range crash state is not the armed prefix",
                    )

                    sudo(
                        str(HOST_BIN / "tc"),
                        "qdisc",
                        "replace",
                        "dev",
                        "vm-iotoxc",
                        "root",
                        "netem",
                        "rate",
                        "4mbit",
                        "limit",
                        "1000",
                    )
                    sync_client_shaped = True
                    command_file = pair_root / "client.sync-range-restart-continue"
                    command_file.write_text(
                        "sync-range-restart-continue=1\n", encoding="ascii"
                    )
                    sudo(
                        "install",
                        "-m",
                        "0600",
                        str(command_file),
                        str(
                            workspace["client"]
                            / "iotox-input/sync-range-restart-continue"
                        ),
                    )
                    command_file.unlink()
                    range_restarted_path = (
                        workspace["client"]
                        / "iotox-rendezvous/client.sync-range-daemon-restarted"
                    )
                    range_reconnect_ready_path = (
                        workspace["client"]
                        / "iotox-rendezvous/client.sync-range-reconnect-ready"
                    )
                    range_reacquired_path = (
                        workspace["client"]
                        / "iotox-rendezvous/client.sync-range-restart-reacquired"
                    )
                    range_recovered_path = (
                        workspace["device"]
                        / "iotox-rendezvous/device.sync-range-restart-recovered"
                    )
                    wait_for(
                        lambda: root_file_exists(range_reconnect_ready_path)
                        and root_file_exists(range_recovered_path),
                        300,
                        "two-sided authority after subscriber restart",
                    )
                    reconnect_ready = read_root_file(
                        range_reconnect_ready_path
                    )
                    require(
                        reconnect_ready
                        == "schema=iotox-sync-range-reconnect-ready-v1\n"
                        "address-preserved=1\n"
                        "session-confirmed=1\n"
                        "remote-authorized=1\n",
                        "subscriber reconnect readiness is invalid",
                    )
                    command_file = pair_root / "client.sync-range-repull"
                    command_file.write_text(
                        "sync-range-repull=1\n", encoding="ascii"
                    )
                    sudo(
                        "install",
                        "-m",
                        "0600",
                        str(command_file),
                        str(
                            workspace["client"]
                            / "iotox-input/sync-range-repull"
                        ),
                    )
                    command_file.unlink()
                    wait_for(
                        lambda: root_file_exists(range_restarted_path)
                        and root_file_exists(range_reacquired_path),
                        300,
                        "fresh authorized range pull after subscriber restart",
                    )
                    reacquired = read_root_file(range_reacquired_path)
                    reacquired_match = re.fullmatch(
                        r"schema=iotox-sync-range-restart-reacquired-v1\n"
                        r"first-job=([1-9][0-9]*)\n"
                        r"second-job=([1-9][0-9]*)\n"
                        r"first-attempt=([1-9][0-9]*)\n"
                        r"second-attempt=([1-9][0-9]*)\n"
                        r"first-message=([1-9][0-9]*)\n"
                        r"second-message=([1-9][0-9]*)\n"
                        r"first-file-id=([0-9a-f]{64})\n"
                        r"second-file-id=([0-9a-f]{64})\n"
                        r"interrupted-bytes=([1-9][0-9]*)\n"
                        r"retained-bytes=([1-9][0-9]*)\n"
                        r"resumed-bytes=([1-9][0-9]*)\n"
                        r"suffix-bytes=([1-9][0-9]*)\n"
                        r"observed-position=([1-9][0-9]*)\n",
                        reacquired,
                    )
                    require(
                        reacquired_match is not None
                        and reacquired_match.group(1) == crash_match.group(2)
                        and reacquired_match.group(3) == crash_match.group(3)
                        and reacquired_match.group(5) == crash_match.group(4)
                        and reacquired_match.group(7) == crash_match.group(5)
                        and reacquired_match.group(1)
                        != reacquired_match.group(2)
                        and reacquired_match.group(3)
                        != reacquired_match.group(4)
                        and reacquired_match.group(5)
                        != reacquired_match.group(6)
                        and reacquired_match.group(7)
                        != reacquired_match.group(8)
                        and int(reacquired_match.group(9))
                        == int(reacquired_match.group(10))
                        == int(reacquired_match.group(11))
                        == int(crash_match.group(1))
                        and int(reacquired_match.group(11))
                        + int(reacquired_match.group(12))
                        == 1_048_576
                        and int(reacquired_match.group(11))
                        <= int(reacquired_match.group(13))
                        < 1_048_576,
                        "fresh bounded-range restart claim is invalid",
                    )
                    sync_client_daemon_restart_count = 1
                range_completed_path = (
                    workspace["client"]
                    / "iotox-rendezvous/client.sync-range-complete"
                )
                range_failure_paths = {
                    role: path / f"iotox-rendezvous/{role}.failure"
                    for role, path in workspace.items()
                }
                range_postconditions_path = (
                    workspace["client"]
                    / "iotox-rendezvous/client.sync-range-postconditions"
                )
                range_progress_path = (
                    workspace["client"]
                    / "iotox-rendezvous/client.sync-range-loss-progress"
                )
                range_device_status_path = (
                    workspace["device"]
                    / "iotox-rendezvous/device.sync-range-live-status"
                )
                range_device_routes_path = (
                    workspace["device"]
                    / "iotox-rendezvous/device.sync-range-live-routes"
                )
                range_completion_timeout = (
                    1800
                    if scenario == "sync-file-range-triple-route-loss"
                    else 1200
                    if scenario == "sync-file-range-repeated-route-loss"
                    else 300
                )
                if scenario in REPEATED_RANGE_LOSS_COUNTS:
                    range_deadline = (
                        time.monotonic() + range_completion_timeout
                    )
                    while True:
                        if (
                            root_file_exists(range_completed_path)
                            or any(
                                root_file_exists(path)
                                for path in range_failure_paths.values()
                            )
                            or any(
                                process.poll() is not None
                                for process in processes.values()
                            )
                        ):
                            break
                        if time.monotonic() >= range_deadline:
                            raise RuntimeError(
                                "timeout waiting for client bounded-range "
                                "successor convergence or explicit failure"
                            )
                        time.sleep(0.05)
                else:
                    wait_for(
                        lambda: root_file_exists(range_completed_path)
                        or any(
                            root_file_exists(path)
                            for path in range_failure_paths.values()
                        )
                        or any(
                            process.poll() is not None
                            for process in processes.values()
                        ),
                        range_completion_timeout,
                        "client bounded-range successor convergence or explicit failure",
                    )
                range_failures = {
                    role: read_root_file(path).strip()
                    for role, path in range_failure_paths.items()
                    if root_file_exists(path)
                }
                range_postconditions = (
                    read_root_file(range_postconditions_path).strip()
                    if root_file_exists(range_postconditions_path)
                    else "absent"
                )
                range_progress = (
                    read_root_file(range_progress_path).strip()
                    if root_file_exists(range_progress_path)
                    else "absent"
                )
                range_device_status = (
                    read_root_file(range_device_status_path).strip()
                    if root_file_exists(range_device_status_path)
                    else "absent"
                )
                range_device_routes = (
                    read_root_file(range_device_routes_path).strip()
                    if root_file_exists(range_device_routes_path)
                    else "absent"
                )
                require(
                    root_file_exists(range_completed_path),
                    "client failed before bounded-range convergence: "
                    f"failures={range_failures} "
                    "chain-exits={"
                    + ", ".join(
                        f"{role}={process.poll()}"
                        for role, process in processes.items()
                        if process.poll() is not None
                    )
                    + "} "
                    f"progress={range_progress} "
                    f"postconditions={range_postconditions} "
                    f"device-status={range_device_status} "
                    f"device-routes={range_device_routes}",
                )
                range_completed = read_root_file(range_completed_path)
                expected_prefix = (
                    "range-convergence=1\nrange-activation=1\n"
                    + (
                        "range-transfer=0\nrange-fallback=1\n"
                        "corrupt-basis-preserved=1\n"
                        if scenario == "sync-file-corrupt-basis"
                        else "range-transfer=1\nrange-fallback=0\n"
                        "corrupt-basis-preserved=0\n"
                    )
                )
                require(
                    range_completed.startswith(expected_prefix)
                    and range_published.strip() in range_completed,
                    "client successor completion does not bind its range policy",
                )

                def range_counter(name: str) -> int:
                    match = re.search(
                        rf"^{re.escape(name)}=([0-9]+)$",
                        range_completed,
                        re.MULTILINE,
                    )
                    require(match is not None, f"missing {name} evidence")
                    return int(match.group(1))

                range_count = range_counter("range-count")
                range_reused = range_counter("range-reused-bytes")
                range_fetched = range_counter("range-fetched-bytes")
                if scenario == "sync-file-corrupt-basis":
                    require(
                        range_count == 0
                        and range_reused == 0
                        and range_fetched == 0,
                        "corrupt-basis fallback falsely claims range reuse",
                    )
                else:
                    require(
                        range_count > 0
                        and range_reused > 0
                        and 0 < range_fetched < SYNC_SCENARIOS[scenario]
                        and range_reused + range_fetched
                        == SYNC_SCENARIOS[scenario],
                        "bounded-range byte accounting is invalid",
                    )
                if scenario == "sync-file-range-retry":
                    range_retries = range_counter("range-retries")
                    range_retained = range_counter(
                        "range-retained-bytes"
                    )
                    range_resumed = range_counter(
                        "range-resumed-bytes"
                    )
                    range_discarded = range_counter(
                        "range-discarded-bytes"
                    )
                    range_retention_fallbacks = range_counter(
                        "range-retention-fallbacks"
                    )

                    def range_text(name: str) -> str:
                        match = re.search(
                            rf"^{re.escape(name)}=([^\n]+)$",
                            range_completed,
                            re.MULTILINE,
                        )
                        require(match is not None, f"missing {name} evidence")
                        return match.group(1)

                    first_file_id = range_text("range-first-file-id")
                    second_file_id = range_text("range-second-file-id")
                    require(
                        range_retries == 1
                        and 0 < range_retained == range_resumed
                        < range_fetched
                        and range_discarded == 0
                        and range_retention_fallbacks == 0
                        and re.fullmatch(r"[0-9a-f]{64}", first_file_id)
                        is not None
                        and re.fullmatch(r"[0-9a-f]{64}", second_file_id)
                        is not None
                        and first_file_id != second_file_id,
                        "bounded-range retry identity evidence is invalid",
                    )
                if scenario == "sync-file-range-restart-resume":
                    restart_interrupted = range_counter(
                        "range-restart-interrupted-bytes"
                    )
                    restart_retained = range_counter(
                        "range-restart-retained-bytes"
                    )
                    restart_resumed_attempts = range_counter(
                        "range-restart-resumed-attempts"
                    )
                    restart_resumed = range_counter(
                        "range-restart-resumed-bytes"
                    )
                    restart_suffix = range_counter(
                        "range-restart-suffix-bytes"
                    )

                    def restart_text(name: str) -> str:
                        match = re.search(
                            rf"^{re.escape(name)}=([^\n]+)$",
                            range_completed,
                            re.MULTILINE,
                        )
                        require(match is not None, f"missing {name} evidence")
                        return match.group(1)

                    restart_jobs = (
                        restart_text("range-restart-first-job"),
                        restart_text("range-restart-second-job"),
                    )
                    restart_attempts = (
                        restart_text("range-restart-first-attempt"),
                        restart_text("range-restart-second-attempt"),
                    )
                    restart_messages = (
                        restart_text("range-restart-first-message"),
                        restart_text("range-restart-second-message"),
                    )
                    restart_file_ids = (
                        restart_text("range-restart-first-file-id"),
                        restart_text("range-restart-second-file-id"),
                    )
                    require(
                        "range-restart-resume=1\n" in range_completed
                        and restart_resumed_attempts == 1
                        and 0
                        < restart_interrupted
                        == restart_retained
                        == restart_resumed
                        < range_fetched
                        and restart_resumed + restart_suffix == range_fetched
                        and all(value.isdigit() and int(value) > 0 for value in (
                            *restart_jobs,
                            *restart_attempts,
                            *restart_messages,
                        ))
                        and restart_jobs[0] != restart_jobs[1]
                        and restart_attempts[0] != restart_attempts[1]
                        and restart_messages[0] != restart_messages[1]
                        and all(
                            re.fullmatch(r"[0-9a-f]{64}", value) is not None
                            for value in restart_file_ids
                        )
                        and restart_file_ids[0] != restart_file_ids[1],
                        "bounded-range daemon-restart evidence is invalid",
                    )
                command_file = pair_root / "device.sync-range-finished"
                command_file.write_text(range_completed, encoding="ascii")
                sudo(
                    "install",
                    "-m",
                    "0600",
                    str(command_file),
                    str(workspace["device"] / "iotox-input/sync-range-finished"),
                )
                command_file.unlink()
            if scenario == "sync-file-disconnect":
                command_file = pair_root / "client.sync-disconnect-release"
                command_file.write_text(
                    "sync-disconnect-release=1\n", encoding="ascii"
                )
                sudo(
                    "install",
                    "-m",
                    "0600",
                    str(command_file),
                    str(
                        workspace["client"]
                        / "iotox-input/sync-disconnect-release"
                    ),
                )
                command_file.unlink()

        if scenario in POST_SYNC_RATOX_SCENARIOS:
            ready_path = (
                workspace["device"]
                / "iotox-rendezvous/device.ratox-ready"
            )
            device_failure_path = (
                workspace["device"] / "iotox-rendezvous/device.failure"
            )
            client_failure_path = (
                workspace["client"] / "iotox-rendezvous/client.failure"
            )
            post_sync_failure_paths = {
                "device": device_failure_path,
                "client": client_failure_path,
            }

            def require_post_sync_success(path: Path, operation: str) -> None:
                wait_for(
                    lambda: root_file_exists(path)
                    or any(
                        root_file_exists(failure_path)
                        for failure_path in post_sync_failure_paths.values()
                    ),
                    300,
                    operation + " or explicit guest failure",
                )
                failures = {
                    role: read_root_file(failure_path).strip()
                    for role, failure_path in post_sync_failure_paths.items()
                    if root_file_exists(failure_path)
                }
                require(
                    root_file_exists(path),
                    f"{operation} failed before completion: {failures}",
                )

            require_post_sync_success(
                ready_path,
                "post-reassignment protected Ratox authority/profile activation",
            )
            command_file = pair_root / "device.ratox-measure-start"
            command_file.write_text(
                "ratox-measure-start=1\n", encoding="ascii"
            )
            sudo(
                "install",
                "-m",
                "0600",
                str(command_file),
                str(
                    workspace["device"]
                    / "iotox-input/ratox-measure-start"
                ),
            )
            command_file.unlink()
            resource_started = (
                workspace["device"]
                / "iotox-rendezvous/device.ratox-resource-started"
            )
            require_post_sync_success(
                resource_started,
                "post-reassignment Ratox resource interval start",
            )
            command_file = pair_root / "client.ratox-start"
            command_file.write_text("ratox-start=1\n", encoding="ascii")
            sudo(
                "install",
                "-m",
                "0600",
                str(command_file),
                str(workspace["client"] / "iotox-input/ratox-start"),
            )
            command_file.unlink()
            captured_path = (
                workspace["client"]
                / "iotox-rendezvous/client.ratox-terminal-captured"
            )
            wait_for(
                lambda: root_file_exists(captured_path)
                or any(
                    root_file_exists(path)
                    for path in post_sync_failure_paths.values()
                ),
                240,
                "post-reassignment protected Ratox capture or explicit failure",
            )
            if not root_file_exists(captured_path):
                failures = {
                    role: read_root_file(path).strip()
                    for role, path in post_sync_failure_paths.items()
                    if root_file_exists(path)
                }
                probe_error_path = (
                    workspace["client"]
                    / "iotox-rendezvous/client.ratox-terminal-probe.stderr"
                )
                if root_file_exists(probe_error_path):
                    failures["probe-stderr"] = read_root_file(
                        probe_error_path
                    ).strip()
                raise RuntimeError(
                    "post-reassignment protected Ratox probe failed:\n"
                    + repr(failures)
                )
            complete_path = (
                workspace["client"]
                / "iotox-rendezvous/client.ratox-complete"
            )
            require_post_sync_success(
                complete_path,
                "post-reassignment protected Ratox completion",
            )
            command_file = pair_root / "device.ratox-finished"
            command_file.write_text("ratox-finished=1\n", encoding="ascii")
            sudo(
                "install",
                "-m",
                "0600",
                str(command_file),
                str(workspace["device"] / "iotox-input/ratox-finished"),
            )
            command_file.unlink()

        if scenario == "relay-restart":
            ready_paths = {
                role: path / f"iotox-rendezvous/{role}.fault-ready"
                for role, path in workspace.items()
            }
            wait_for(
                lambda: all(root_file_exists(path) for path in ready_paths.values()),
                180,
                "both guests to reach the pre-fault confirmed session",
            )
            require(fixture_process is not None, "bootstrap fixture is absent")
            terminate({"bootstrap": fixture_process})
            fixture_process = None

            offline_paths = {
                role: path / f"iotox-rendezvous/{role}.offline-observed"
                for role, path in workspace.items()
            }
            wait_for(
                lambda: all(root_file_exists(path) for path in offline_paths.values()),
                180,
                "both guests to observe relay loss",
            )
            fixture_process = subprocess.Popen(
                [str(bootstrap_binary), "--ipv4"],
                cwd=bootstrap_dir,
                stdout=fixture_log,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
            require_bootstrap_ready(fixture_process)
            fixture_restart_count = 1
            fixture_key_preserved = (
                public_id.read_text(encoding="ascii") == bootstrap_key
            )
            require(fixture_key_preserved, "bootstrap fixture key changed on restart")

        if scenario == "proxy-restart":
            ready_paths = {
                role: path / f"iotox-rendezvous/{role}.fault-ready"
                for role, path in workspace.items()
            }
            wait_for(
                lambda: all(root_file_exists(path) for path in ready_paths.values()),
                180,
                "both guests to reach the pre-proxy-fault confirmed session",
            )
            require(socks5_process is not None, "SOCKS5 forwarder is absent")
            stop_socks5_forwarder(socks5_process, pair_root, socks5_phase)
            socks5_process = None

            offline_paths = {
                role: path / f"iotox-rendezvous/{role}.offline-observed"
                for role, path in workspace.items()
            }
            wait_for(
                lambda: all(root_file_exists(path) for path in offline_paths.values()),
                240,
                "both guests to observe strict proxy loss",
            )
            socks5_phase = "restart"
            socks5_process = start_socks5_forwarder(pair_root, socks5_phase)
            socks5_restart_count = 1

        if scenario == "i2p-router-restart":
            ready_paths = {
                role: path / f"iotox-rendezvous/{role}.fault-ready"
                for role, path in workspace.items()
            }
            wait_for(
                lambda: all(root_file_exists(path) for path in ready_paths.values()),
                240,
                "both guests to reach the pre-I2P-router-fault confirmed session",
            )
            require(i2p_instance is not None, "I2P topology is absent")
            i2p_root = Path(i2p_instance["root"])
            fault_request = i2p_root / "fault-client-router"
            fault_request.write_text("fault-client-router=1\n", encoding="ascii")
            os.chmod(fault_request, 0o600)
            active_path = i2p_root / "fault-active.json"
            wait_for(
                active_path.is_file,
                60,
                "I2P client-router fault activation",
            )
            active = load(active_path)
            require(
                active.get("schema") == "iotox.i2p-tox-fronts.v1"
                and active.get("status") == "fault-active"
                and active.get("kind") == "client-router-process-restart"
                and active.get("adapter_listener_reachable") is True
                and active.get("client_sam_listener_reachable") is False
                and active.get("adapter_generation_one_lost") is True
                and active.get("contains_secrets") is False
                and tcp_port_open(HOST_BRIDGE_ADDRESS, I2P_SOCKS5_PORT),
                "I2P listener-positive/SAM-negative fault evidence is invalid",
            )
            offline_paths = {
                role: path / f"iotox-rendezvous/{role}.offline-observed"
                for role, path in workspace.items()
            }
            wait_for(
                lambda: all(root_file_exists(path) for path in offline_paths.values()),
                300,
                "both guests to observe I2P router loss",
            )
            recover_request = i2p_root / "recover-client-router"
            recover_request.write_text("recover-client-router=1\n", encoding="ascii")
            os.chmod(recover_request, 0o600)
            recovered_path = i2p_root / "fault-recovered.json"
            wait_for(
                recovered_path.is_file,
                480,
                "I2P client-router recovery",
            )
            recovered = load(recovered_path)
            require(
                recovered.get("schema") == "iotox.i2p-tox-fronts.v1"
                and recovered.get("status") == "fault-recovered"
                and recovered.get("kind") == "client-router-process-restart"
                and recovered.get("process_replaced") is True
                and recovered.get("router_datadir_preserved") is True
                and recovered.get("adapter_listener_reachable_while_sam_down")
                is True
                and recovered.get("client_sam_listener_absent_during_fault")
                is True
                and recovered.get("adapter_generation_one_lost") is True
                and recovered.get("adapter_generation_two_ready") is True
                and isinstance(recovered.get("fault_hold_ns"), int)
                and recovered["fault_hold_ns"] > 0
                and recovered.get("contains_secrets") is False,
                "I2P router recovery evidence is invalid",
            )
            text_received_paths = {
                role: path / f"iotox-rendezvous/{role}.fault-text-received"
                for role, path in workspace.items()
            }
            wait_for(
                lambda: all(
                    root_file_exists(path) for path in text_received_paths.values()
                ),
                600,
                "both guests to receive fresh post-I2P-recovery text",
            )
            for role, path in workspace.items():
                finish = pair_root / f"{role}.i2p-router-fault-finish"
                finish.write_text("i2p-router-fault-finish=1\n", encoding="ascii")
                sudo(
                    "install",
                    "-m",
                    "0600",
                    str(finish),
                    str(path / "iotox-input/i2p-router-fault-finish"),
                )
                finish.unlink()
            i2p_router_restart_count = 1

        if scenario == "i2p-service-restart":
            ready_paths = {
                role: path / f"iotox-rendezvous/{role}.fault-ready"
                for role, path in workspace.items()
            }
            wait_for(
                lambda: all(root_file_exists(path) for path in ready_paths.values()),
                240,
                "both guests to reach the pre-I2P-service-fault confirmed session",
            )
            require(i2p_instance is not None, "I2P topology is absent")
            i2p_root = Path(i2p_instance["root"])
            fault_request = i2p_root / "fault-server-fronts"
            fault_request.write_text("fault-server-fronts=1\n", encoding="ascii")
            os.chmod(fault_request, 0o600)
            active_path = i2p_root / "front-fault-active.json"
            wait_for(active_path.is_file, 60, "I2P server-front fault activation")
            active = load(active_path)
            require(
                active.get("schema") == "iotox.i2p-tox-fronts.v1"
                and active.get("status") == "fault-active"
                and active.get("kind") == "server-front-process-restart"
                and isinstance(active.get("old_server_front_pids"), list)
                and len(active["old_server_front_pids"]) == 3
                and len(set(active["old_server_front_pids"])) == 3
                and all(
                    isinstance(pid, int) and pid > 1
                    for pid in active["old_server_front_pids"]
                )
                and active.get("adapter_listener_reachable") is True
                and active.get("server_sam_listener_reachable") is True
                and active.get("client_sam_listener_reachable") is True
                and active.get("routers_preserved") is True
                and active.get("contains_secrets") is False
                and tcp_port_open(HOST_BRIDGE_ADDRESS, I2P_SOCKS5_PORT),
                "I2P front-negative/router-positive fault evidence is invalid",
            )
            offline_paths = {
                role: path / f"iotox-rendezvous/{role}.offline-observed"
                for role, path in workspace.items()
            }
            wait_for(
                lambda: all(root_file_exists(path) for path in offline_paths.values()),
                300,
                "both guests to observe I2P service-front loss",
            )
            recover_request = i2p_root / "recover-server-fronts"
            recover_request.write_text("recover-server-fronts=1\n", encoding="ascii")
            os.chmod(recover_request, 0o600)
            recovered_path = i2p_root / "front-fault-recovered.json"
            wait_for(recovered_path.is_file, 480, "I2P server-front recovery")
            recovered = load(recovered_path)
            require(
                recovered.get("schema") == "iotox.i2p-tox-fronts.v1"
                and recovered.get("status") == "fault-recovered"
                and recovered.get("kind") == "server-front-process-restart"
                and recovered.get("old_server_front_pids")
                == active["old_server_front_pids"]
                and isinstance(recovered.get("new_server_front_pids"), list)
                and len(recovered["new_server_front_pids"]) == 3
                and len(set(recovered["new_server_front_pids"])) == 3
                and set(recovered["new_server_front_pids"]).isdisjoint(
                    active["old_server_front_pids"]
                )
                and recovered.get("processes_replaced") is True
                and recovered.get("destination_keys_preserved") is True
                and recovered.get("adapter_listener_preserved") is True
                and recovered.get("server_sam_listener_preserved") is True
                and recovered.get("client_sam_listener_preserved") is True
                and recovered.get("routers_preserved") is True
                and isinstance(recovered.get("fault_started_ns"), int)
                and isinstance(recovered.get("fault_recovered_ns"), int)
                and recovered["fault_recovered_ns"] > recovered["fault_started_ns"]
                and recovered.get("fault_hold_ns")
                == recovered["fault_recovered_ns"] - recovered["fault_started_ns"]
                and recovered.get("contains_secrets") is False,
                "I2P service-front recovery evidence is invalid",
            )
            text_received_paths = {
                role: path / f"iotox-rendezvous/{role}.fault-text-received"
                for role, path in workspace.items()
            }
            wait_for(
                lambda: all(
                    root_file_exists(path) for path in text_received_paths.values()
                ),
                600,
                "both guests to receive fresh post-I2P-service-recovery text",
            )
            for role, path in workspace.items():
                finish = pair_root / f"{role}.i2p-service-fault-finish"
                finish.write_text("i2p-service-fault-finish=1\n", encoding="ascii")
                sudo(
                    "install",
                    "-m",
                    "0600",
                    str(finish),
                    str(path / "iotox-input/i2p-service-fault-finish"),
                )
                finish.unlink()
            i2p_front_restart_count = 1

        if scenario == "link-interruption":
            ready_paths = {
                role: path / f"iotox-rendezvous/{role}.fault-ready"
                for role, path in workspace.items()
            }
            wait_for(
                lambda: all(root_file_exists(path) for path in ready_paths.values()),
                180,
                "both guests to reach the pre-link-fault confirmed session",
            )
            links_blocked = True
            for tap in ("vm-iotoxc", "vm-iotoxd"):
                sudo(
                    str(HOST_BIN / "tc"),
                    "qdisc",
                    "replace",
                    "dev",
                    tap,
                    "root",
                    "netem",
                    "loss",
                    "100%",
                )
            link_interruption_count = 1
            offline_paths = {
                role: path / f"iotox-rendezvous/{role}.offline-observed"
                for role, path in workspace.items()
            }
            wait_for(
                lambda: all(root_file_exists(path) for path in offline_paths.values()),
                180,
                "both guests to observe TAP link interruption",
            )
            for tap in ("vm-iotoxc", "vm-iotoxd"):
                sudo(str(HOST_BIN / "tc"), "qdisc", "del", "dev", tap, "root")
            links_blocked = False

        if scenario == "packet-loss":
            ready_paths = {
                role: path / f"iotox-rendezvous/{role}.packet-loss-ready"
                for role, path in workspace.items()
            }
            wait_for(
                lambda: all(root_file_exists(path) for path in ready_paths.values()),
                180,
                "both guests to reach the confirmed pre-loss session",
            )
            links_blocked = True
            for tap in ("vm-iotoxc", "vm-iotoxd"):
                sudo(
                    str(HOST_BIN / "tc"),
                    "qdisc",
                    "replace",
                    "dev",
                    tap,
                    "root",
                    "netem",
                    "limit",
                    "1000",
                    "loss",
                    "random",
                    f"{PACKET_LOSS_PERCENT}%",
                    "seed",
                    str(PACKET_LOSS_SEEDS[tap]),
                )
            packet_loss_impairment_count = 1
            for role, root in workspace.items():
                command_file = pair_root / f"{role}.packet-loss-start"
                command_file.write_text("packet-loss-start=1\n", encoding="ascii")
                sudo(
                    "install",
                    "-m",
                    "0600",
                    str(command_file),
                    str(root / "iotox-input/packet-loss-start"),
                )
                command_file.unlink()
            complete_paths = {
                role: path / f"iotox-rendezvous/{role}.packet-loss-complete"
                for role, path in workspace.items()
            }
            wait_for(
                lambda: all(root_file_exists(path) for path in complete_paths.values()),
                180,
                "both guests to complete traffic under partial loss",
            )
            packet_loss_qdiscs = [
                netem_observation(tap) for tap in ("vm-iotoxc", "vm-iotoxd")
            ]
            require(
                all(observation["drops"] > 0 for observation in packet_loss_qdiscs),
                "seeded partial loss did not drop packets on both TAPs",
            )
            for tap in ("vm-iotoxc", "vm-iotoxd"):
                sudo(str(HOST_BIN / "tc"), "qdisc", "del", "dev", tap, "root")
            links_blocked = False
            for role, root in workspace.items():
                command_file = pair_root / f"{role}.packet-loss-release"
                command_file.write_text("packet-loss-release=1\n", encoding="ascii")
                sudo(
                    "install",
                    "-m",
                    "0600",
                    str(command_file),
                    str(root / "iotox-input/packet-loss-release"),
                )
                command_file.unlink()

        if scenario == "daemon-restart":
            ready_paths = {
                role: path / f"iotox-rendezvous/{role}.fault-ready"
                for role, path in workspace.items()
            }
            wait_for(
                lambda: all(root_file_exists(path) for path in ready_paths.values()),
                180,
                "both guests to reach the pre-replacement confirmed session",
            )
            command_file = pair_root / "device.stop-daemon"
            command_file.write_text("stop-daemon=1\n", encoding="ascii")
            sudo(
                "install",
                "-m",
                "0600",
                str(command_file),
                str(workspace["device"] / "iotox-input/stop-daemon"),
            )
            command_file.unlink()

            stopped_path = workspace["device"] / "iotox-rendezvous/device.daemon-stopped"
            offline_path = workspace["client"] / "iotox-rendezvous/client.offline-observed"
            wait_for(
                lambda: root_file_exists(stopped_path)
                and root_file_exists(offline_path),
                180,
                "device daemon stop and stable-client offline observation",
            )
            command_file = pair_root / "device.restart-daemon"
            command_file.write_text("restart-daemon=1\n", encoding="ascii")
            sudo(
                "install",
                "-m",
                "0600",
                str(command_file),
                str(workspace["device"] / "iotox-input/restart-daemon"),
            )
            command_file.unlink()
            device_daemon_restart_count = 1

        if scenario == "guest-restart":
            ready_paths = {
                role: path / f"iotox-rendezvous/{role}.fault-ready"
                for role, path in workspace.items()
            }
            wait_for(
                lambda: all(root_file_exists(path) for path in ready_paths.values()),
                180,
                "both guests to reach the pre-reboot confirmed session",
            )
            command_file = pair_root / "device.reboot-guest"
            command_file.write_text("reboot-guest=1\n", encoding="ascii")
            sudo(
                "install",
                "-m",
                "0600",
                str(command_file),
                str(workspace["device"] / "iotox-input/reboot-guest"),
            )
            command_file.unlink()
            stopping_path = workspace["device"] / "iotox-rendezvous/device.guest-stopping"
            offline_path = workspace["client"] / "iotox-rendezvous/client.offline-observed"
            recovered_path = workspace["device"] / "iotox-rendezvous/device.guest-recovered"
            wait_for(
                lambda: root_file_exists(stopping_path)
                and root_file_exists(offline_path),
                180,
                "device guest shutdown and stable-client offline observation",
            )
            initial_device_process = processes["device"]
            try:
                initial_device_result = initial_device_process.wait(timeout=60)
            except subprocess.TimeoutExpired as error:
                raise RuntimeError("initial device VMM chain did not terminate after reboot") from error
            require(
                initial_device_result in {0, 1},
                f"initial device VMM chain exited unexpectedly: {initial_device_result}",
            )
            initial_chain_path = role_roots["device"] / "direct-cloud-hypervisor-live-chain.json"
            initial_launch_path = role_roots["device"] / "live/cloud-hypervisor-launch.json"
            initial_chain = load(initial_chain_path)
            initial_launch = load(initial_launch_path)
            require(
                initial_chain.get("status") == "blocked"
                and initial_chain.get("failure", {}).get("blockers")
                == ["live:console-not-observed"],
                "initial device chain did not record the bounded reboot exit",
            )
            require(
                initial_launch.get("status") == "blocked"
                and initial_launch.get("vmm", {}).get("process_observed") is True
                and initial_launch.get("vmm", {}).get("exit_observed") is True
                and initial_launch.get("vmm", {}).get("exit_status") == 1,
                "initial device VMM reboot exit evidence is invalid",
            )
            initial_device_chain_entry = {
                "path": str(initial_chain_path.relative_to(pair_root)),
                "sha256": sha256(initial_chain_path),
                "status": "bounded-reboot-exit",
            }
            initial_device_launch_entry = {
                "path": str(initial_launch_path.relative_to(pair_root)),
                "sha256": sha256(initial_launch_path),
                "status": "bounded-reboot-exit",
            }

            successor_root = pair_root / "device-restart"
            successor_root.mkdir(mode=0o700)
            successor_stdout = (pair_root / "device-restart.chain.stdout").open("wb")
            successor_stderr = (pair_root / "device-restart.chain.stderr").open("wb")
            logs["device-restart"] = (successor_stdout, successor_stderr)
            prelaunch_receipt = (
                role_roots["device"]
                / "prelaunch/direct-cloud-hypervisor-prelaunch-chain.json"
            )
            processes["device"] = subprocess.Popen(
                command_for(
                    "device",
                    route,
                    successor_root,
                    prelaunch_receipt=prelaunch_receipt,
                    guest_receipt_timeout=guest_receipt_timeout,
                ),
                stdout=successor_stdout,
                stderr=successor_stderr,
                start_new_session=True,
            )
            role_roots["device"] = successor_root
            workspace["device"] = successor_root / "live/workspace-export"
            wait_for(
                lambda: workspace["device"].is_dir(),
                180,
                "replacement device Sandwurm workspace",
            )
            recovered_path = workspace["device"] / "iotox-rendezvous/device.guest-recovered"
            wait_for(
                lambda: root_file_exists(recovered_path),
                180,
                "device guest reboot and confirmed recovery",
            )
            device_guest_restart_count = 1

        if scenario == "sync-tree-route-common-link-fairness":
            capture_ready = (
                workspace["client"]
                / "iotox-rendezvous/client.common-link-capture-ready"
            )
            wait_for(
                lambda: root_file_exists(capture_ready)
                or processes["client"].poll() is not None,
                600,
                "client common-link fairness evidence boundary",
            )
            require(
                root_file_exists(capture_ready)
                and processes["client"].poll() is None,
                "client exited before common-link fairness evidence capture",
            )
            common_link_fairness_qdisc = common_link_fairness_observation(
                "vm-iotoxc"
            )
            deliver_guest_input(
                pair_root,
                workspace["client"],
                "client",
                "common-link-captured",
            )

        if scenario in BIDIRECTIONAL_SYNC_SCENARIOS:
            wait_for(
                lambda: all(
                    process.poll() is not None for process in processes.values()
                )
                or any(
                    root_file_exists(path) for path in failure_paths.values()
                ),
                1200,
                "both bidirectional sync guest chains",
            )
            require(
                not any(
                    root_file_exists(path) for path in failure_paths.values()
                ),
                "a bidirectional sync guest failed: "
                + "; ".join(
                    f"{role}={read_root_file(path).strip()}"
                    for role, path in failure_paths.items()
                    if root_file_exists(path)
                ),
            )

        guest_exit_timeout = (
            1200 if scenario in BIDIRECTIONAL_SYNC_SCENARIOS else 540
        )
        for role, process in processes.items():
            try:
                result = process.wait(timeout=guest_exit_timeout)
            except subprocess.TimeoutExpired as error:
                raise RuntimeError(f"{role} Sandwurm chain did not terminate") from error
            require(result == 0, f"{role} Sandwurm chain exited {result}")
        if socks5_process is not None:
            stop_socks5_forwarder(socks5_process, pair_root, socks5_phase)
            socks5_process = None
        if capture_processes:
            terminate(capture_processes)
            capture_processes.clear()
            for handles in capture_handles.values():
                for handle in handles:
                    handle.close()
            capture_handles.clear()
        if i2p_instance is not None:
            i2p_topology_final = stop_i2p_fronts(i2p_instance)
            i2p_instance = None
            require(
                i2p_topology_final.get("client_router_restart_count")
                == i2p_router_restart_count,
                "I2P topology restart count mismatch",
            )
            require(
                i2p_topology_final.get("server_front_restart_count", 0)
                == i2p_front_restart_count,
                "I2P topology front restart count mismatch",
            )
        if tor_adversaries:
            for role in ("client", "device"):
                stop_actual_tor_adversary(tor_adversaries[role])
        if actual_tor:
            require(tor_node is not None, "actual-Tor node disappeared")
            if actual_tor_process_fault:
                require(
                    tor_pre_loss_evidence is not None,
                    "pre-loss client Tor evidence is absent",
                )
                tor_role_evidence = [
                    tor_pre_loss_evidence,
                    actual_tor_role_evidence(
                        pair_root,
                        tor_instances["client"],
                        tor_node,
                        "recovered",
                    ),
                    actual_tor_role_evidence(
                        pair_root,
                        tor_instances["device"],
                        tor_node,
                        "continuous",
                    ),
                ]
            else:
                tor_role_evidence = [
                    actual_tor_role_evidence(
                        pair_root, tor_instances[role], tor_node
                    )
                    for role in ("client", "device")
                ]
            require(
                tor_instances["client"]["tor_binary_path"]
                == tor_instances["device"]["tor_binary_path"]
                and tor_instances["client"]["tor_sha256"]
                == tor_instances["device"]["tor_sha256"]
                and tor_instances["client"]["tor_version"]
                == tor_instances["device"]["tor_version"],
                "actual-Tor instances do not share one exact binary",
            )
            require(
                len({record["process_pid"] for record in tor_role_evidence})
                == (3 if actual_tor_process_fault else 2)
                and len(
                    {record["control_socket_inode"] for record in tor_role_evidence}
                )
                >= 2,
                "actual-Tor role instances are not process/control distinct",
            )
            if actual_tor_process_fault:
                require(
                    actual_tor_process_loss.get("pre_loss_process_pid")
                    == tor_role_evidence[0]["process_pid"]
                    and tor_role_evidence[1]["process_pid"]
                    != tor_role_evidence[0]["process_pid"],
                    "actual-Tor process loss is not bound to two client PIDs",
                )
                actual_tor_process_loss["recovered_process_pid"] = (
                    tor_role_evidence[1]["process_pid"]
                )
                actual_tor_process_loss["recovered_control_socket_inode"] = (
                    tor_role_evidence[1]["control_socket_inode"]
                )
                loss_path = pair_root / "actual-tor-process-loss.json"
                loss_path.write_text(
                    json.dumps(
                        actual_tor_process_loss, indent=2, sort_keys=True
                    )
                    + "\n",
                    encoding="utf-8",
                )
            if actual_tor_ratox_adversary:
                require(
                    bool(actual_tor_adversarial_boundary),
                    "adversarial boundary lifecycle evidence is absent",
                )
                boundary_roles: list[dict[str, object]] = []
                for role, role_evidence in zip(
                    ("client", "device"), tor_role_evidence
                ):
                    instance = tor_adversaries[role]
                    audit_path = Path(instance["audit_path"])
                    records = [
                        json.loads(line)
                        for line in audit_path.read_text(
                            encoding="ascii"
                        ).splitlines()
                    ]
                    admitted = [
                        record
                        for record in records
                        if record.get("event") == "socks5-connect"
                        and record.get("outcome") == "admitted"
                    ]
                    chains = [
                        record
                        for record in records
                        if record.get("event") == "socks5-chain"
                        and record.get("outcome") == "admitted-chain"
                    ]
                    holds = [
                        record
                        for record in records
                        if record.get("event") == "relay-hold"
                        and record.get("outcome") == "held"
                    ]
                    denied = [
                        record
                        for record in records
                        if str(record.get("outcome", "")).startswith("denied")
                    ]
                    expected_guest = (
                        "10.0.0.11:" if role == "client" else "10.0.0.12:"
                    )
                    guest_chains = [
                        record
                        for record in chains
                        if str(record.get("client_source", "")).startswith(
                            expected_guest
                        )
                    ]
                    event_lines = (
                        pair_root / str(role_evidence["events_path"])
                    ).read_text(encoding="ascii").splitlines()
                    upstream_sources = sorted(
                        str(record.get("upstream_source", ""))
                        for record in chains
                    )
                    require(
                        len(admitted) == len(chains)
                        and len(chains) >= (2 if role == "client" else 1)
                        and guest_chains
                        and not denied,
                        f"{role} adversarial chain audit is incomplete",
                    )
                    require(
                        all(
                            record.get("target") == str(tor_node["target"])
                            and record.get("upstream_destination")
                            == str(instance["upstream_endpoint"])
                            for record in chains
                        ),
                        f"{role} adversarial chain escaped its endpoints",
                    )
                    require(
                        all(
                            any(
                                f"SOURCE_ADDR={source}" in line
                                and f" {tor_node['target']} " in line
                                for line in event_lines
                            )
                            for source in upstream_sources
                        ),
                        f"{role} interposer chains are not bound to Tor events",
                    )
                    require(
                        len(holds) >= 1 if role == "client" else len(holds) == 0,
                        f"{role} adversarial hold count is invalid",
                    )
                    boundary_roles.append(
                        {
                            "role": role,
                            "listen_endpoint": instance["listen_endpoint"],
                            "upstream_endpoint": instance["upstream_endpoint"],
                            "process_pid": instance["process_pid"],
                            "listener_inode": instance["listener_inode"],
                            "audit_path": audit_path.name,
                            "audit_sha256": sha256(audit_path),
                            "admitted_count": len(admitted),
                            "chain_count": len(chains),
                            "guest_chain_count": len(guest_chains),
                            "hold_observation_count": len(holds),
                            "denied_count": len(denied),
                            "upstream_source_set_sha256": hashlib.sha256(
                                ("\n".join(upstream_sources) + "\n").encode(
                                    "ascii"
                                )
                            ).hexdigest(),
                            "tor_control_events_path": role_evidence[
                                "events_path"
                            ],
                            "exact_chain_to_tor_binding": True,
                        }
                    )
                actual_tor_adversarial_boundary["roles"] = boundary_roles
                actual_tor_adversarial_boundary["interposer_sha256"] = sha256(
                    ROOT / "tools/run-socks5-adversary.py"
                )
                boundary_path = pair_root / "actual-tor-adversarial-boundary.json"
                boundary_path.write_text(
                    json.dumps(
                        actual_tor_adversarial_boundary, indent=2, sort_keys=True
                    )
                    + "\n",
                    encoding="utf-8",
                )
            terminate(
                {
                    role: tor_instances[role]["process"]
                    for role in ("client", "device")
                }
            )
            for instance in tor_instances.values():
                instance["log"].close()
        completed_ns = time.monotonic_ns()

        sudo("chown", "-R", f"{os.getuid()}:{os.getgid()}", str(pair_root))
        for path in role_roots.values():
            os.chmod(path, 0o700)
        require(baseline_digest(current) == digest_before, "reusable key baseline changed")
        if scenario in RATOX_STRIPE_SCENARIOS or scenario in MULTI_ROUTE_SYNC_SCENARIOS:
            require(
                stripe_current is not None and stripe_digest_before is not None,
                "stripe baseline disappeared",
            )
            require(
                stripe_baseline_digest(stripe_current) == stripe_digest_before,
                "reusable stripe identity baseline changed",
            )

        expected_connection = "udp" if route == "direct-udp" else "tcp"
        socks5_audits = []
        socks5_admitted = 0
        socks5_denied = 0
        if actual_tor:
            capture_summaries = [
                (
                    summarize_tap_capture(
                        pair_root / f"{role}.tox-tor.pcapng",
                        role,
                        ACTUAL_TOR_SOCKS_PORTS[role],
                    )
                    if actual_tor_ratox_loss
                    or actual_tor_ratox_soak
                    or actual_tor_ratox_adversary
                    else summarize_mixed_context_capture(
                        pair_root / f"{role}.tox-tor.pcapng",
                        role,
                        ACTUAL_TOR_SOCKS_PORTS[role],
                    )
                )
                for role in ("client", "device")
            ]
            actual_tor_containment_name = (
                "actual-tor-route-containment.json"
                if actual_tor_ratox_loss
                or actual_tor_ratox_soak
                or actual_tor_ratox_adversary
                else "actual-tor-mixed-route-containment.json"
            )
            (pair_root / actual_tor_containment_name).write_text(
                json.dumps(capture_summaries, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        if routed_socks5:
            capture_summaries = [
                (
                    summarize_mixed_context_capture(
                        pair_root / f"{role}.tox-tor.pcapng", role
                    )
                    if scenario == "sync-tree-route-private-mixed"
                    else summarize_tap_capture(
                        pair_root / f"{role}.tox-tor.pcapng", role
                    )
                )
                for role in ("client", "device")
            ]
            containment_name = (
                "mixed-route-containment.json"
                if scenario == "sync-tree-route-private-mixed"
                else "tox-tor-containment.json"
            )
            (pair_root / containment_name).write_text(
                json.dumps(capture_summaries, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            phases = ["initial"] + (["restart"] if socks5_restart_count else [])
            for phase in phases:
                audit_path = pair_root / f"socks5-{phase}-audit.jsonl"
                records = [
                    json.loads(line)
                    for line in audit_path.read_text(encoding="ascii").splitlines()
                ]
                admitted = sum(record.get("outcome") == "admitted" for record in records)
                denied = len(records) - admitted
                require(admitted >= 2, f"SOCKS5 {phase} did not admit both guests")
                require(denied == 0, f"SOCKS5 {phase} observed a denied route attempt")
                require(
                    all(
                        record.get("target")
                        == f"{HOST_BRIDGE_ADDRESS}:{BOOTSTRAP_PORT}"
                        for record in records
                    ),
                    f"SOCKS5 {phase} observed an unexpected target",
                )
                socks5_admitted += admitted
                socks5_denied += denied
                socks5_audits.append(
                    {
                        "phase": phase,
                        "path": audit_path.name,
                        "sha256": sha256(audit_path),
                        "admitted": admitted,
                        "denied": denied,
                    }
                )
        if actual_i2p:
            capture_summaries = [
                (
                    summarize_mixed_context_capture(
                        pair_root / f"{role}.tox-i2p.pcapng",
                        role,
                        I2P_SOCKS5_PORT,
                    )
                    if actual_i2p_payload
                    else summarize_tap_capture(
                        pair_root / f"{role}.tox-i2p.pcapng",
                        role,
                        I2P_SOCKS5_PORT,
                    )
                )
                for role in ("client", "device")
            ]
            (pair_root / "tox-i2p-containment.json").write_text(
                json.dumps(capture_summaries, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        receipts = {}
        chains = {}
        for role, root in role_roots.items():
            receipt_path = root / "live/workspace-export/guest-receipts/iotox/pair.json"
            chain_path = root / "direct-cloud-hypervisor-live-chain.json"
            receipt = load(receipt_path)
            chain = load(chain_path)
            require(receipt.get("status") == "passed", f"{role} pair receipt failed")
            require(receipt.get("role") == role, f"{role} receipt role mismatch")
            require(receipt.get("route_mode") == route, f"{role} route mismatch")
            require(receipt.get("scenario") == scenario, f"{role} scenario mismatch")
            require(receipt.get("observed_connection") == expected_connection, f"{role} connection mismatch")
            require(
                receipt.get("network") == expected_network(route),
                f"{role} network projection mismatch",
            )
            require(
                receipt.get("private_l2_ping")
                is (route != "tox-tor" and route not in I2P_ROUTES),
                f"{role} private-L2 observation mismatch",
            )
            if scenario in BIDIRECTIONAL_SYNC_SCENARIOS:
                require(
                    receipt.get("sync_bidirectional_observed") is True
                    and receipt.get(
                        "sync_bidirectional_conflict_observed"
                    )
                    is True
                    and receipt.get(
                        "sync_bidirectional_resolution_observed"
                    )
                    is True
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
                    and receipt.get("sync_bidirectional_final_sha256", "")
                    == "",
                    f"{role} unexpectedly claims bidirectional sync",
                )
            require(
                not actual_i2p
                or receipt.get("i2p_node_records_sha256")
                == i2p_topology_final.get("node_records_sha256"),
                f"{role} I2P node-set commitment mismatch",
            )
            if scenario in mixed_context_scenarios:
                require(
                    receipt.get("private_route_mixed_context_observed") is True
                    and receipt.get("private_route_primary_network") == "Tox/native"
                    and receipt.get("private_route_auxiliary_network")
                    == (
                        "Tox/I2P-construction"
                        if actual_i2p_payload
                        else "Tox/Tor"
                    )
                    and re.fullmatch(
                        r"[0-9a-f]{64}",
                        receipt.get("private_route_auxiliary_key_sha256", ""),
                    )
                    is not None,
                    f"{role} private mixed-context evidence is invalid",
                )
            require(
                receipt.get("actual_tor_payload_observed", False)
                is (actual_tor_payload and role == "client")
                and (
                    re.fullmatch(
                        r"[0-9a-f]{64}",
                        receipt.get("actual_tor_payload_carrier_sha256", ""),
                    )
                    is not None
                    if actual_tor_payload and role == "client"
                    else receipt.get("actual_tor_payload_carrier_sha256", "")
                    == ""
                )
                and receipt.get("actual_tor_payload_reassignments", 0) == 0,
                f"{role} actual-Tor payload attribution is invalid",
            )
            if actual_tor_payload and role == "client":
                require(
                    receipt["actual_tor_payload_carrier_sha256"]
                    == receipt["private_route_auxiliary_key_sha256"],
                    "client actual-Tor payload carrier is not the Tor member",
                )
            require(
                receipt.get("actual_i2p_payload_observed", False)
                is (actual_i2p_payload and role == "client")
                and (
                    re.fullmatch(
                        r"[0-9a-f]{64}",
                        receipt.get("actual_i2p_payload_carrier_sha256", ""),
                    )
                    is not None
                    if actual_i2p_payload and role == "client"
                    else receipt.get("actual_i2p_payload_carrier_sha256", "")
                    == ""
                )
                and receipt.get("actual_i2p_payload_reassignments", 0) == 0,
                f"{role} actual-I2P payload attribution is invalid",
            )
            if actual_i2p_payload and role == "client":
                require(
                    receipt["actual_i2p_payload_carrier_sha256"]
                    == receipt["private_route_auxiliary_key_sha256"],
                    "client actual-I2P payload carrier is not the I2P member",
                )
            if actual_i2p_loss and role == "client":
                require(
                    receipt.get("actual_i2p_fail_closed_loss_observed")
                    is True
                    and receipt.get(
                        "actual_i2p_fail_closed_loss_position_bytes"
                    )
                    == actual_i2p_fail_closed_loss.get("position_bytes")
                    and receipt.get(
                        "actual_i2p_fail_closed_loss_carrier_sha256"
                    )
                    == receipt["private_route_auxiliary_key_sha256"]
                    == actual_i2p_fail_closed_loss.get(
                        "stopped_carrier_sha256"
                    )
                    and receipt.get(
                        "actual_i2p_fail_closed_loss_carrier_losses"
                    )
                    == 1
                    and receipt.get(
                        "actual_i2p_fail_closed_loss_reassignments"
                    )
                    == 0
                    and receipt.get(
                        "actual_i2p_fail_closed_loss_blocked_jobs"
                    )
                    == 1
                    and receipt.get(
                        "actual_i2p_fail_closed_loss_recoveries"
                    )
                    == 1
                    and receipt.get(
                        "actual_i2p_fail_closed_loss_worker_restarts"
                    )
                    == 0
                    and receipt.get(
                        "actual_i2p_fail_closed_loss_original_job_id"
                    )
                    == actual_i2p_fail_closed_loss.get("original_job_id")
                    and receipt.get(
                        "actual_i2p_fail_closed_loss_replacement_job_id"
                    )
                    == actual_i2p_fail_closed_loss.get(
                        "replacement_job_id"
                    )
                    and receipt.get(
                        "actual_i2p_fail_closed_loss_old_job_cancelled"
                    )
                    is True
                    and receipt.get(
                        "actual_i2p_fail_closed_loss_same_carrier"
                    )
                    is True,
                    "client fail-closed actual-I2P loss evidence is invalid",
                )
            else:
                require(
                    receipt.get(
                        "actual_i2p_fail_closed_loss_observed", False
                    )
                    is False
                    and receipt.get(
                        "actual_i2p_fail_closed_loss_position_bytes", 0
                    )
                    == 0
                    and receipt.get(
                        "actual_i2p_fail_closed_loss_carrier_sha256", ""
                    )
                    == ""
                    and receipt.get(
                        "actual_i2p_fail_closed_loss_carrier_losses", 0
                    )
                    == 0
                    and receipt.get(
                        "actual_i2p_fail_closed_loss_reassignments", 0
                    )
                    == 0
                    and receipt.get(
                        "actual_i2p_fail_closed_loss_blocked_jobs", 0
                    )
                    == 0
                    and receipt.get(
                        "actual_i2p_fail_closed_loss_recoveries", 0
                    )
                    == 0
                    and receipt.get(
                        "actual_i2p_fail_closed_loss_worker_restarts", 0
                    )
                    == 0
                    and receipt.get(
                        "actual_i2p_fail_closed_loss_original_job_id", 0
                    )
                    == 0
                    and receipt.get(
                        "actual_i2p_fail_closed_loss_replacement_job_id", 0
                    )
                    == 0
                    and receipt.get(
                        "actual_i2p_fail_closed_loss_old_job_cancelled",
                        False,
                    )
                    is False
                    and receipt.get(
                        "actual_i2p_fail_closed_loss_same_carrier", False
                    )
                    is False,
                    f"{role} unexpectedly claims fail-closed I2P loss",
                )
            if actual_tor_loss and role == "client":
                stopped_carrier = receipt.get(
                    "sync_tree_route_loss_stopped_carrier", ""
                )
                require(
                    receipt.get("sync_tree_route_loss_observed") is True
                    and receipt.get("sync_tree_route_loss_position_bytes")
                    == actual_tor_process_loss.get("position_bytes")
                    and stopped_carrier
                    == actual_tor_process_loss.get("stopped_carrier")
                    and receipt.get(
                        "sync_tree_route_loss_worker_restarts"
                    )
                    == actual_tor_process_loss.get(
                        "route_worker_restarts"
                    )
                    == 0
                    and hashlib.sha256(
                        str(stopped_carrier).encode("ascii")
                    ).hexdigest()
                    == receipt["private_route_auxiliary_key_sha256"]
                    == actual_tor_process_loss.get(
                        "stopped_carrier_sha256"
                    ),
                    "client route loss is not bound to the actual-Tor member",
                )
            pull_attempts = receipt.get("sync_initial_pull_attempts", 0)
            pull_failures = receipt.get("sync_initial_pull_failures", 0)
            pull_error_digest = receipt.get(
                "sync_initial_pull_first_error_sha256", ""
            )
            if role == "client" and scenario in SYNC_SCENARIOS:
                require(
                    isinstance(pull_attempts, int)
                    and pull_attempts >= 1
                    and isinstance(pull_failures, int)
                    and 0 <= pull_failures < pull_attempts
                    and pull_attempts == pull_failures + 1
                    and (
                        re.fullmatch(r"[0-9a-f]{64}", pull_error_digest)
                        is not None
                        if pull_failures > 0
                        else pull_error_digest == ""
                    ),
                    "client sync pull admission evidence is invalid",
                )
            else:
                require(
                    pull_attempts == 0
                    and pull_failures == 0
                    and pull_error_digest == "",
                    f"{role} unexpectedly claims sync pull admission",
                )
            if scenario == "relay-restart":
                initial_epoch = receipt.get("initial_online_epoch")
                recovered_epoch = receipt.get("recovered_online_epoch")
                require(
                    isinstance(initial_epoch, int) and initial_epoch > 0,
                    f"{role} initial online epoch is invalid",
                )
                require(
                    isinstance(recovered_epoch, int)
                    and recovered_epoch > initial_epoch,
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
            if scenario == "proxy-restart":
                require(
                    receipt.get("proxy_interruption_observed") is True,
                    f"{role} did not observe proxy interruption",
                )
                require(
                    receipt.get("proxy_recovery_observed") is True,
                    f"{role} did not observe proxy recovery",
                )
            if scenario == "i2p-router-restart":
                require(
                    isinstance(receipt.get("initial_online_epoch"), int)
                    and isinstance(receipt.get("recovered_online_epoch"), int)
                    and receipt["recovered_online_epoch"]
                    > receipt["initial_online_epoch"],
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
                    isinstance(receipt.get("initial_online_epoch"), int)
                    and isinstance(receipt.get("recovered_online_epoch"), int)
                    and receipt["recovered_online_epoch"]
                    > receipt["initial_online_epoch"],
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
                    f"{role} did not preserve the device identity",
                )
                require(
                    receipt.get("fresh_session_after_daemon_restart") is True,
                    f"{role} did not confirm a fresh replacement session",
                )
                expected_restarts = 1 if role == "device" else 0
                require(
                    receipt.get("daemon_restart_count") == expected_restarts,
                    f"{role} daemon restart count mismatch",
                )
                if role == "client":
                    require(
                        receipt.get("daemon_offline_observed") is True,
                        "stable client did not observe the daemon offline",
                    )
                    initial_epoch = receipt.get("initial_online_epoch")
                    recovered_epoch = receipt.get("recovered_online_epoch")
                    require(
                        isinstance(initial_epoch, int)
                        and isinstance(recovered_epoch, int)
                        and recovered_epoch > initial_epoch,
                        "stable client online epoch did not advance",
                    )
            if scenario in {"link-interruption", "sync-file-disconnect"}:
                initial_epoch = receipt.get("initial_online_epoch")
                recovered_epoch = receipt.get("recovered_online_epoch")
                require(
                    isinstance(initial_epoch, int)
                    and isinstance(recovered_epoch, int)
                    and recovered_epoch > initial_epoch,
                    f"{role} online epoch did not advance after link restoration",
                )
                require(
                    receipt.get("link_interruption_observed") is True,
                    f"{role} did not observe link interruption",
                )
                require(
                    receipt.get("link_recovery_observed") is True,
                    f"{role} did not observe link recovery",
                )
            if scenario == "packet-loss":
                require(
                    receipt.get("packet_loss_observed") is True
                    and receipt.get("packet_loss_epoch_stable") is True
                    and receipt.get("packet_loss_text_delivered") is True
                    and receipt.get("packet_loss_restored_text_delivered") is True,
                    f"{role} partial-loss continuity evidence is incomplete",
                )
                delivered = receipt.get("packet_loss_probe_delivered")
                missed = receipt.get("packet_loss_probe_missed")
                require(
                    receipt.get("packet_loss_probe_count") == PACKET_LOSS_PROBE_COUNT
                    and isinstance(delivered, int)
                    and delivered > 0
                    and isinstance(missed, int)
                    and missed >= 0
                    and delivered + missed == PACKET_LOSS_PROBE_COUNT
                    and receipt.get("packet_loss_probe_send_errors") == 0,
                    f"{role} partial-loss burst evidence is invalid",
                )
                require(
                    receipt.get("recovered_online_epoch")
                    == receipt.get("initial_online_epoch"),
                    f"{role} changed online epoch under partial loss",
                )
                require(
                    route != "direct-udp" or missed > 0,
                    f"{role} direct-UDP burst did not expose any lossy-carrier miss",
                )
            if scenario in {"guest-restart", "sync-file-guest-restart"}:
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
                    f"{role} did not confirm a fresh post-reboot session",
                )
                initial_boot = receipt.get("initial_guest_boot_id_sha256")
                recovered_boot = receipt.get("recovered_guest_boot_id_sha256")
                require(
                    isinstance(initial_boot, str)
                    and isinstance(recovered_boot, str)
                    and re.fullmatch(r"[0-9a-f]{64}", initial_boot) is not None
                    and re.fullmatch(r"[0-9a-f]{64}", recovered_boot) is not None,
                    f"{role} boot-ID digest is invalid",
                )
                if role == "device":
                    require(initial_boot != recovered_boot, "device boot ID did not change")
                else:
                    require(initial_boot == recovered_boot, "stable client boot ID changed")
                    require(
                        receipt.get("guest_offline_observed") is True,
                        "stable client did not observe guest offline",
                    )
                    require(
                        receipt.get("recovered_online_epoch", 0)
                        > receipt.get("initial_online_epoch", 0),
                        "stable client epoch did not advance after guest reboot",
                    )
            if scenario in MUTABLE_SCENARIOS:
                require(
                    receipt.get("mutable_authority_observed") is True
                    and receipt.get("mutable_outgoing_succeeded") is True
                    and receipt.get("mutable_incoming_succeeded") is True
                    and receipt.get("mutable_provider_converged") is True
                    and receipt.get("mutable_ownership_epoch") == 1,
                    f"{role} did not prove the mutable profile-state boundary",
                )
            if scenario in RATOX_SCENARIOS:
                require(
                    receipt.get("ratox_idle_observed") is True
                    and receipt.get("ratox_sample_count")
                    == ratox_sample_count(scenario),
                    f"{role} did not retain the Ratox capture boundary",
                )
                expected_bulk = RATOX_BULK_SCENARIOS.get(scenario, 0)
                require(
                    receipt.get("ratox_bulk_observed") is (expected_bulk != 0)
                    and receipt.get("ratox_bulk_stream_count") == expected_bulk
                    and receipt.get("ratox_bulk_payload_bytes")
                    == (1073741824 if expected_bulk else 0),
                    f"{role} did not retain the Ratox bulk boundary",
                )
                expected_routes = RATOX_STRIPE_SCENARIOS.get(scenario, 1)
                require(
                    receipt.get("ratox_stripe_route_count") == expected_routes,
                    f"{role} stripe route count mismatch",
                )
                route_restarts = receipt.get("ratox_stripe_route_restart_count")
                injected_restarts = receipt.get("ratox_stripe_injected_restart_count")
                require(
                    isinstance(route_restarts, int)
                    and 0 <= route_restarts <= 7
                    and isinstance(injected_restarts, int)
                    and 0 <= injected_restarts <= route_restarts,
                    f"{role} stripe restart counters are invalid",
                )
                expected_injected = int(
                    scenario == "ratox-stripe-recovery-32" and role == "device"
                )
                require(
                    injected_restarts == expected_injected,
                    f"{role} injected stripe restart count mismatch",
                )
                live_loss = scenario in RATOX_LIVE_LOSS_SCENARIOS
                require(
                    receipt.get("ratox_stripe_live_fault_injected")
                    is (live_loss and role == "device")
                    and receipt.get("ratox_stripe_live_offline_observed")
                    is (live_loss and role == "client")
                    and receipt.get("ratox_stripe_live_recovery_observed")
                    is live_loss
                    and receipt.get("ratox_stripe_live_affected_transfer_count")
                    == (8 if live_loss else 0)
                    and receipt.get("ratox_stripe_live_reassigned_transfer_count")
                    == 0,
                    f"{role} live stripe-loss boundary mismatch",
                )
                if expected_routes == 4:
                    stripe_path = receipt_path.parent / "ratox-stripe-routes.tsv"
                    require(stripe_path.is_file(), f"{role} stripe route evidence is absent")
                    stripe_lines = stripe_path.read_text(encoding="ascii").splitlines()
                    require(
                        stripe_lines[:2]
                        == ["schema\tiotox-ratox-stripe-routes-v1", "route-count\t4"],
                        f"{role} stripe route metadata is invalid",
                    )
                    route_rows = [line.split("\t") for line in stripe_lines[2:]]
                    require(len(route_rows) == 4, f"{role} stripe route rows are incomplete")
                    route_hashes = []
                    for lane, row in enumerate(route_rows):
                        require(
                            len(row) == 6
                            and row[:5] == [
                                "route",
                                str(lane),
                                "connection",
                                "tcp",
                                "peer-key-sha256",
                            ]
                            and re.fullmatch(r"[0-9a-f]{64}", row[5]) is not None,
                            f"{role} stripe route {lane} is invalid",
                        )
                        route_hashes.append(row[5])
                    require(len(set(route_hashes)) == 4, f"{role} stripe peer routes are not distinct")
                    require(
                        route_hashes[0] == receipt.get("peer_key_sha256"),
                        f"{role} protected Ratox route is not stripe route zero",
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
                        isinstance(receipt.get(field), str)
                        and re.fullmatch(r"[0-9a-f]{64}", receipt[field])
                        is not None,
                        f"{role} {field} is invalid",
                    )
                if scenario in CONTENT_MULTI_SOURCE_SCENARIOS:
                    require(
                        receipt.get("multi_source_count") == 2
                        and isinstance(
                            receipt.get("multi_source_availability_requests"),
                            int,
                        )
                        and receipt["multi_source_availability_requests"] >= 2
                        and receipt.get("multi_source_availability_results")
                        == receipt["multi_source_availability_requests"]
                        and re.fullmatch(
                            r"[0-9a-f]{64}",
                            str(
                                receipt.get(
                                    "multi_source_secondary_key_sha256", ""
                                )
                            ),
                        )
                        is not None
                        and re.fullmatch(
                            r"[0-9a-f]{64}",
                            str(
                                receipt.get(
                                    "multi_source_secondary_principal_sha256",
                                    "",
                                )
                            ),
                        )
                        is not None
                        and (
                            role != "device"
                            or (
                                receipt.get("multi_source_primary_objects", 0)
                                > 1
                                and receipt.get(
                                    "multi_source_secondary_objects", 0
                                )
                                > 0
                            )
                        ),
                        f"{role} multi-source content evidence is incomplete",
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
                            re.fullmatch(
                                r"[0-9a-f]{64}",
                                str(
                                    receipt.get(
                                        "multi_source_auxiliary_carriers_sha256",
                                        "",
                                    )
                                ),
                            )
                            is not None
                            if routed_multi_source and role == "client"
                            else receipt.get(
                                "multi_source_auxiliary_carriers_sha256", ""
                            )
                            == ""
                        ),
                        f"{role} routed multi-source carrier evidence is invalid",
                    )
                    native_loss = scenario == "sync-content-multi-source-loss"
                    route_loss = (
                        scenario
                        == "sync-content-multi-route-actual-tor-loss"
                    )
                    loss = native_loss or route_loss
                    require(
                        receipt.get("multi_source_loss_observed", False)
                        is loss
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
                            receipt.get("multi_source_loss_first_job_id", 0)
                            > 0
                            and receipt.get(
                                "multi_source_loss_replacement_job_id", 0
                            )
                            > 0
                            and receipt["multi_source_loss_first_job_id"]
                            != receipt[
                                "multi_source_loss_replacement_job_id"
                            ]
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
                                > receipt[
                                    "multi_source_loss_initial_epoch"
                                ]
                                if native_loss
                                else receipt.get(
                                    "multi_source_loss_recovered_epoch", 0
                                )
                                == receipt[
                                    "multi_source_loss_initial_epoch"
                                ]
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
                        f"{role} selected-source loss evidence is invalid",
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
                        f"{role} exact routed source-loss evidence is invalid",
                    )
                if scenario == "sync-content-same-source-lanes":
                    lane_digest = receipt.get(
                        "same_source_lane_set_sha256", ""
                    )
                    require(
                        receipt.get("same_source_lanes_observed", False)
                        is (role == "client")
                        and receipt.get("same_source_lane_cap", 0)
                        == (2 if role == "client" else 0)
                        and receipt.get("same_source_active_lanes", 0)
                        == (2 if role == "client" else 0)
                        and receipt.get("same_source_admitted_lanes", 0)
                        == (2 if role == "client" else 0)
                        and receipt.get(
                            "same_source_distinct_requests", 0
                        )
                        == (2 if role == "client" else 0)
                        and receipt.get("same_source_distinct_files", 0)
                        == (2 if role == "client" else 0)
                        and receipt.get("same_source_source_count", 0)
                        == (1 if role == "client" else 0)
                        and receipt.get(
                            "same_source_root_lane_count", 0
                        )
                        == 0
                        and (
                            re.fullmatch(r"[0-9a-f]{64}", lane_digest)
                            is not None
                            if role == "client"
                            else lane_digest == ""
                        ),
                        f"{role} same-source content-lane evidence is invalid",
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
                        and receipt.get(
                            "content_lane_science_artifact_bytes", 0
                        )
                        == (8 * 1024 * 1024 if science else 0)
                        and receipt.get("content_lane_science_chunks", 0)
                        >= (8 if science else 0)
                        and receipt.get("content_lane_science_objects", 0)
                        >= (10 if science else 0)
                        and receipt.get(
                            "content_lane_science_restart_count", 0
                        )
                        == 0
                        and receipt.get(
                            "content_lane_science_activation_count", 0
                        )
                        == (4 if science else 0),
                        f"{role} content-lane science boundary is invalid",
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
                        and receipt.get("content_ratox_post_bulk_origin_us", 0)
                        >= (1 if post_bulk else 0)
                        and receipt.get(
                            "content_ratox_post_bulk_origin_to_open_sent_us", 0
                        )
                        <= (1_000_000 if post_bulk else 0)
                        and receipt.get(
                            "content_ratox_post_bulk_origin_to_opened_us", 0
                        )
                        <= (6_000_000 if post_bulk else 0)
                        and receipt.get(
                            "content_ratox_post_bulk_open_round_trip_us", 0
                        )
                        <= (5_000_000 if post_bulk else 0)
                        and receipt.get("content_ratox_post_bulk_online_epoch", 0)
                        >= (1 if post_bulk else 0),
                        f"{role} post-bulk Ratox admission boundary is invalid",
                    )
                    for field in (
                        "readiness_sha256",
                        "capture_sha256",
                        "admission_sha256",
                    ):
                        value = receipt.get(f"content_ratox_post_bulk_{field}", "")
                        require(
                            (
                                re.fullmatch(r"[0-9a-f]{64}", value) is not None
                                if post_bulk
                                else value == ""
                            ),
                            f"{role} post-bulk Ratox {field} is invalid",
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
                            f"content_lane_science_cap_{cap}_resource_sha256",
                            "",
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
                                and re.fullmatch(
                                    r"[0-9a-f]{64}", resource_digest
                                )
                                is not None
                                if science
                                else duration == 0
                                and measured_bps == 0
                                and active == 0
                                and resource_digest == ""
                            ),
                            f"{role} cap-{cap} content-lane evidence is invalid",
                        )
                    summary_digest = receipt.get(
                        "content_lane_science_summary_sha256", ""
                    )
                    require(
                        (
                            re.fullmatch(r"[0-9a-f]{64}", summary_digest)
                            is not None
                            if science
                            else summary_digest == ""
                        ),
                        f"{role} content-lane summary commitment is invalid",
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
                    and isinstance(
                        receipt.get("signed_update_sender_epoch", 0), int
                    )
                    and (
                        receipt.get("signed_update_sender_epoch", 0) > 0
                        if signed_update
                        else receipt.get("signed_update_sender_epoch", 0) == 0
                    )
                    and isinstance(
                        receipt.get("signed_update_message_id", 0), int
                    )
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
                            isinstance(value, str)
                            and re.fullmatch(r"[0-9a-f]{64}", value)
                            is not None
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
                    receipt.get("sync_tree_observed", False)
                    is tree_scenario
                    and receipt.get("sync_tree_directories", 0)
                    == (3 if tree_scenario else 0)
                    and receipt.get("sync_tree_files", 0)
                    == (3 if tree_scenario else 0)
                    and receipt.get("sync_tree_content_bytes", 0)
                    == expected_tree_content_bytes
                    and (
                        re.fullmatch(
                            r"[0-9a-f]{64}",
                            str(receipt.get("sync_tree_payload_sha256", "")),
                        )
                        is not None
                        if tree_scenario
                        else receipt.get("sync_tree_payload_sha256", "") == ""
                    ),
                    f"{role} deterministic tree evidence is invalid",
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
                route_loss_scenario = scenario in SYNC_ROUTE_LOSS_SCENARIOS
                multi_route_sync_scenario = scenario in MULTI_ROUTE_SYNC_SCENARIOS
                require(
                    receipt.get("sync_tree_route_ready_bulk", 0)
                    == (2 if multi_route_sync_scenario else 0)
                    and receipt.get("sync_tree_route_loss_observed", False)
                    is (route_loss_scenario and role == "client"),
                    f"{role} synchronization route admission evidence is invalid",
                )
                require(
                    receipt.get(
                        "sync_tree_route_cancel_loss_observed", False
                    )
                    is (
                        scenario == "sync-tree-route-cancel-loss"
                        and role == "client"
                    ),
                    f"{role} cancellation-before-loss evidence is invalid",
                )
                race_observer = (
                    scenario in SYNC_ROUTE_CANCEL_RACE_SCENARIOS
                    and role == "client"
                )
                race_fault_delay, race_cancel_delay, required_race_outcome = (
                    SYNC_ROUTE_CANCEL_RACE_SCENARIOS.get(
                        scenario, (0, 0, None)
                    )
                )
                race_outcome = receipt.get(
                    "sync_tree_route_cancel_race_outcome", ""
                )
                require(
                    receipt.get(
                        "sync_tree_route_cancel_race_observed", False
                    )
                    is race_observer
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
                    and (
                        race_outcome in {"cancel-first", "loss-first"}
                        if scenario in SYNC_ROUTE_CANCEL_RACE_SCENARIOS
                        else race_outcome == ""
                    )
                    and (
                        required_race_outcome is None
                        or race_outcome == required_race_outcome
                    ),
                    f"{role} cancel/loss race evidence is invalid",
                )
                startup_order_scenario = (
                    scenario == "sync-tree-route-startup-order"
                )
                phase_one_first = receipt.get(
                    "sync_tree_route_startup_phase_one_first", ""
                )
                phase_two_first = receipt.get(
                    "sync_tree_route_startup_phase_two_first", ""
                )
                require(
                    receipt.get(
                        "sync_tree_route_startup_order_observed", False
                    )
                    is startup_order_scenario
                    and receipt.get("sync_tree_route_startup_delay_ms", 0)
                    == (20_000 if startup_order_scenario else 0)
                    and receipt.get(
                        "sync_tree_route_startup_restart_count", 0
                    )
                    == (1 if startup_order_scenario else 0)
                    and receipt.get(
                        "sync_tree_route_startup_phase_one_stable_samples", 0
                    )
                    == (10 if startup_order_scenario else 0)
                    and receipt.get(
                        "sync_tree_route_startup_phase_two_stable_samples", 0
                    )
                    == (10 if startup_order_scenario else 0)
                    and (
                        re.fullmatch(r"[0-9A-F]{64}", str(phase_one_first))
                        is not None
                        and re.fullmatch(
                            r"[0-9A-F]{64}", str(phase_two_first)
                        )
                        is not None
                        and phase_one_first != phase_two_first
                        and 0
                        < receipt.get(
                            "sync_tree_route_startup_phase_one_ms", 0
                        )
                        < 20_000
                        and 0
                        < receipt.get(
                            "sync_tree_route_startup_phase_two_ms", 0
                        )
                        < 20_000
                        if startup_order_scenario
                        else phase_one_first == ""
                        and phase_two_first == ""
                        and receipt.get(
                            "sync_tree_route_startup_phase_one_ms", 0
                        )
                        == 0
                        and receipt.get(
                            "sync_tree_route_startup_phase_two_ms", 0
                        )
                        == 0
                    ),
                    f"{role} route startup-order evidence is invalid",
                )
                if route_loss_scenario and role == "client":
                    final_carrier = receipt.get(
                        "sync_tree_route_loss_final_carrier", ""
                    )
                    stopped_carrier = receipt.get(
                        "sync_tree_route_loss_stopped_carrier", ""
                    )
                    cancel_before_loss = (
                        scenario == "sync-tree-route-cancel-loss"
                    )
                    cancel_loss_race = (
                        scenario in SYNC_ROUTE_CANCEL_RACE_SCENARIOS
                    )
                    repeated_range_loss_count = (
                        REPEATED_RANGE_LOSS_COUNTS.get(scenario, 0)
                    )
                    repeated_range_loss = repeated_range_loss_count != 0
                    expected_route_losses = repeated_range_loss_count or 1
                    route_reassignments = receipt.get(
                        "sync_tree_route_loss_reassignments"
                    )
                    position = receipt.get(
                        "sync_tree_route_loss_position_bytes"
                    )
                    require(
                        isinstance(position, int)
                        and (
                            position == 0
                            if cancel_before_loss
                            else 65_536
                            <= position
                            < SYNC_SCENARIOS[scenario]
                        )
                        and receipt.get(
                            "sync_tree_route_loss_carrier_losses"
                        )
                        == expected_route_losses
                        and (
                            route_reassignments in {0, 1}
                            if cancel_loss_race
                            else route_reassignments
                            == (
                                0
                                if cancel_before_loss
                                else expected_route_losses
                            )
                        )
                        and receipt.get(
                            "sync_tree_route_loss_stale_terminals", -1
                        )
                        >= (
                            0
                            if cancel_loss_race
                            else expected_route_losses
                        )
                        and receipt.get("sync_tree_route_loss_recoveries")
                        == expected_route_losses
                        and (
                            receipt.get(
                                "sync_tree_route_loss_worker_restarts"
                            )
                            == expected_route_losses
                            if repeated_range_loss
                            else True
                        )
                        and re.fullmatch(r"[0-9A-F]{64}", final_carrier)
                        is not None
                        and re.fullmatch(r"[0-9A-F]{64}", stopped_carrier)
                        is not None
                        and (
                            final_carrier == stopped_carrier
                            if repeated_range_loss_count == 2 or
                            cancel_before_loss or
                            cancel_loss_race and route_reassignments == 0
                            else final_carrier != stopped_carrier
                        ),
                        "client synchronization route-loss evidence is invalid",
                    )
                else:
                    require(
                        receipt.get("sync_tree_route_loss_position_bytes", 0)
                        == 0
                        and receipt.get(
                            "sync_tree_route_loss_carrier_losses", 0) == 0
                        and receipt.get(
                            "sync_tree_route_loss_reassignments", 0) == 0
                        and receipt.get(
                            "sync_tree_route_loss_stale_terminals", 0) == 0
                        and receipt.get(
                            "sync_tree_route_loss_recoveries", 0) == 0
                        and receipt.get(
                            "sync_tree_route_loss_final_carrier", "") == ""
                        and receipt.get(
                            "sync_tree_route_loss_stopped_carrier", "") == "",
                        f"{role} non-route-loss scenario claims route-loss evidence",
                    )
                route_resume_observer = role == "client" and scenario in {
                    "sync-tree-route-loss",
                    "sync-tree-route-private-actual-tor-loss",
                    "sync-file-range-route-loss",
                    "sync-file-range-late-route-loss",
                    "sync-file-range-repeated-route-loss",
                    "sync-file-range-triple-route-loss",
                }
                route_resume_bytes = receipt.get(
                    "sync_tree_route_loss_resumed_bytes", 0
                )
                require(
                    receipt.get("sync_tree_route_resume_observed", False)
                    is route_resume_observer
                    and (
                        receipt.get(
                            "sync_tree_route_loss_retained_partials", -1
                        )
                        == 0
                        and (
                            receipt.get(
                                "sync_tree_route_loss_retained_attempts", 0
                            )
                            == REPEATED_RANGE_LOSS_COUNTS[scenario]
                            if scenario in REPEATED_RANGE_LOSS_COUNTS
                            else 1
                            <= receipt.get(
                                "sync_tree_route_loss_retained_attempts", 0
                            )
                            <= 2
                        )
                        and receipt.get(
                            "sync_tree_route_loss_retained_bytes", 0
                        )
                        == route_resume_bytes
                        and receipt.get(
                            "sync_tree_route_loss_retention_fallbacks", -1
                        )
                        == 0
                        and receipt.get(
                            "sync_tree_route_loss_resumed_attempts", 0
                        )
                        == receipt.get(
                            "sync_tree_route_loss_retained_attempts", 0
                        )
                        and route_resume_bytes >= receipt.get(
                            "sync_tree_route_loss_position_bytes", 0
                        )
                        and route_resume_bytes > 0
                        if route_resume_observer
                        else receipt.get(
                            "sync_tree_route_loss_retained_partials", 0
                        )
                        == 0
                        and receipt.get(
                            "sync_tree_route_loss_retained_attempts", 0
                        )
                        == 0
                        and receipt.get(
                            "sync_tree_route_loss_retained_bytes", 0
                        )
                        == 0
                        and receipt.get(
                            "sync_tree_route_loss_retention_fallbacks", 0
                        )
                        == 0
                        and receipt.get(
                            "sync_tree_route_loss_resumed_attempts", 0
                        )
                        == 0
                        and route_resume_bytes == 0
                    ),
                    f"{role} route-prefix resume evidence is invalid",
                )
                route_balance_observer = (
                    scenario == "sync-tree-route-balance" and role == "client"
                )
                fixed_a = receipt.get(
                    "sync_tree_route_balance_fixed_carrier_a", ""
                )
                fixed_b = receipt.get(
                    "sync_tree_route_balance_fixed_carrier_b", ""
                )
                adaptive_a = receipt.get(
                    "sync_tree_route_balance_adaptive_carrier_a", ""
                )
                adaptive_b = receipt.get(
                    "sync_tree_route_balance_adaptive_carrier_b", ""
                )
                phase_order = receipt.get(
                    "sync_tree_route_balance_phase_order", ""
                )
                require(
                    receipt.get("sync_tree_route_balance_observed", False)
                    is route_balance_observer
                    and receipt.get(
                        "sync_tree_route_balance_fixed_same_carrier", False
                    )
                    is route_balance_observer
                    and receipt.get(
                        "sync_tree_route_balance_adaptive_distinct_carriers",
                        False,
                    )
                    is route_balance_observer
                    and (
                        re.fullmatch(r"[0-9A-F]{64}", fixed_a) is not None
                        and fixed_a == fixed_b
                        and re.fullmatch(r"[0-9A-F]{64}", adaptive_a)
                        is not None
                        and re.fullmatch(r"[0-9A-F]{64}", adaptive_b)
                        is not None
                        and adaptive_a != adaptive_b
                        and phase_order == "adaptive-fixed"
                        and receipt.get(
                            "sync_tree_route_balance_fixed_selections", 0
                        )
                        == 2
                        and receipt.get(
                            "sync_tree_route_balance_adaptive_selections", 0
                        )
                        == 2
                        and receipt.get(
                            "sync_tree_route_balance_fixed_duration_ms", 0
                        )
                        > 0
                        and receipt.get(
                            "sync_tree_route_balance_adaptive_duration_ms", 0
                        )
                        > 0
                        and receipt.get(
                            "sync_tree_route_balance_activations", 0
                        )
                        == 4
                        and receipt.get(
                            "sync_tree_route_balance_artifact_bytes", 0
                        )
                        == 8259
                        and receipt.get(
                            "sync_tree_route_balance_fixed_head_retries", 0
                        )
                        >= 0
                        and receipt.get(
                            "sync_tree_route_balance_fixed_head_retries", 0
                        )
                        <= 16
                        and receipt.get(
                            "sync_tree_route_balance_adaptive_head_retries", 0
                        )
                        >= 0
                        and receipt.get(
                            "sync_tree_route_balance_adaptive_head_retries", 0
                        )
                        <= 16
                        if route_balance_observer
                        else fixed_a == ""
                        and fixed_b == ""
                        and adaptive_a == ""
                        and adaptive_b == ""
                        and phase_order == ""
                        and receipt.get(
                            "sync_tree_route_balance_fixed_selections", 0
                        )
                        == 0
                        and receipt.get(
                            "sync_tree_route_balance_adaptive_selections", 0
                        )
                        == 0
                        and receipt.get(
                            "sync_tree_route_balance_fixed_duration_ms", 0
                        )
                        == 0
                        and receipt.get(
                            "sync_tree_route_balance_adaptive_duration_ms", 0
                        )
                        == 0
                        and receipt.get(
                            "sync_tree_route_balance_activations", 0
                        )
                        == 0
                        and receipt.get(
                            "sync_tree_route_balance_artifact_bytes", 0
                        )
                        == 0
                        and receipt.get(
                            "sync_tree_route_balance_fixed_head_retries", 0
                        )
                        == 0
                        and receipt.get(
                            "sync_tree_route_balance_adaptive_head_retries", 0
                        )
                        == 0
                    ),
                    f"{role} deterministic route-balance evidence is invalid",
                )
                route_population_observer = (
                    scenario == "sync-tree-route-population"
                    and role == "client"
                )
                population_fixed_resource = receipt.get(
                    "sync_tree_route_population_fixed_resource_sha256", ""
                )
                population_adaptive_resource = receipt.get(
                    "sync_tree_route_population_adaptive_resource_sha256", ""
                )
                require(
                    receipt.get(
                        "sync_tree_route_population_observed", False
                    )
                    is route_population_observer
                    and (
                        receipt.get("sync_tree_route_population_jobs") == 8
                        and 131_072
                        < receipt.get(
                            "sync_tree_route_population_artifact_bytes", 0
                        )
                        < 262_144
                        and receipt.get(
                            "sync_tree_route_population_fixed_pattern"
                        )
                        == "00001111"
                        and receipt.get(
                            "sync_tree_route_population_adaptive_pattern"
                        )
                        == "01010101"
                        and receipt.get(
                            "sync_tree_route_population_fixed_max_prefix_imbalance"
                        )
                        == 4
                        and receipt.get(
                            "sync_tree_route_population_adaptive_max_prefix_imbalance"
                        )
                        == 1
                        and receipt.get(
                            "sync_tree_route_population_fixed_progress_jobs"
                        )
                        == 8
                        and receipt.get(
                            "sync_tree_route_population_adaptive_progress_jobs"
                        )
                        == 8
                        and receipt.get(
                            "sync_tree_route_population_fixed_progress_observation_spread_ms",
                            -1,
                        )
                        >= 0
                        and receipt.get(
                            "sync_tree_route_population_adaptive_progress_observation_spread_ms",
                            -1,
                        )
                        >= 0
                        and receipt.get(
                            "sync_tree_route_population_fixed_duration_ms", 0
                        )
                        > 0
                        and receipt.get(
                            "sync_tree_route_population_adaptive_duration_ms",
                            0,
                        )
                        > 0
                        and receipt.get(
                            "sync_tree_route_population_activations"
                        )
                        == 16
                        and re.fullmatch(
                            r"[0-9a-f]{64}", population_fixed_resource
                        )
                        is not None
                        and re.fullmatch(
                            r"[0-9a-f]{64}", population_adaptive_resource
                        )
                        is not None
                        if route_population_observer
                        else receipt.get(
                            "sync_tree_route_population_jobs", 0
                        )
                        == 0
                        and receipt.get(
                            "sync_tree_route_population_artifact_bytes", 0
                        )
                        == 0
                        and receipt.get(
                            "sync_tree_route_population_fixed_pattern", ""
                        )
                        == ""
                        and receipt.get(
                            "sync_tree_route_population_adaptive_pattern", ""
                        )
                        == ""
                        and receipt.get(
                            "sync_tree_route_population_activations", 0
                        )
                        == 0
                        and population_fixed_resource == ""
                        and population_adaptive_resource == ""
                    ),
                    f"{role} route-population evidence is invalid",
                )
                population_loss_scenario = scenario in {
                    "sync-tree-route-population-loss",
                    "sync-tree-route-loss-admission",
                }
                population_loss_observer = (
                    population_loss_scenario and role == "client"
                )
                loss_admission_observer = (
                    scenario == "sync-tree-route-loss-admission"
                    and role == "client"
                )
                population_loss_resource = receipt.get(
                    "sync_tree_route_population_loss_resource_sha256", ""
                )
                population_loss_stopped = receipt.get(
                    "sync_tree_route_population_loss_stopped_carrier", ""
                )
                loss_admission_survivor = receipt.get(
                    "sync_tree_route_loss_admission_surviving_carrier", ""
                )
                if population_loss_observer:
                    expected_jobs = 4 if loss_admission_observer else 8
                    expected_pattern = (
                        "00" if loss_admission_observer else "00001111"
                    )
                    expected_affected = 2 if loss_admission_observer else 4
                    expected_selections = 6 if loss_admission_observer else 12
                    expected_work = 4 if loss_admission_observer else 16
                    expected_delay = 1 if loss_admission_observer else 750
                    population_loss_values = (
                        receipt.get("sync_tree_route_population_loss_jobs")
                        == expected_jobs
                        and receipt.get(
                            "sync_tree_route_population_loss_artifact_bytes"
                        )
                        == 524_355
                        and receipt.get(
                            "sync_tree_route_population_loss_pattern"
                        )
                        == expected_pattern
                        and receipt.get(
                            "sync_tree_route_population_loss_affected_jobs"
                        )
                        == expected_affected
                        and receipt.get(
                            "sync_tree_route_population_loss_carrier_losses"
                        )
                        == 1
                        and receipt.get(
                            "sync_tree_route_population_loss_reassignments"
                        )
                        == expected_affected
                        and receipt.get(
                            "sync_tree_route_population_loss_stale_terminals", 0
                        )
                        >= 1
                        and receipt.get(
                            "sync_tree_route_population_loss_recoveries"
                        )
                        == 1
                        and receipt.get(
                            "sync_tree_route_population_loss_fixed_selections"
                        )
                        == expected_selections
                        and receipt.get(
                            "sync_tree_route_population_loss_activations"
                        )
                        == expected_jobs
                        and receipt.get(
                            "sync_tree_route_population_loss_work_before"
                        )
                        == expected_work
                        and receipt.get(
                            "sync_tree_route_population_loss_work_after"
                        )
                        == 0
                        and receipt.get(
                            "sync_tree_route_population_loss_fault_delay_ms"
                        )
                        == expected_delay
                        and 65_536
                        <= receipt.get(
                            "sync_tree_route_population_loss_fault_position_bytes",
                            0,
                        )
                        < 524_355
                        and receipt.get(
                            "sync_tree_route_population_loss_duration_ms", 0
                        )
                        > 0
                        and re.fullmatch(
                            r"[0-9A-F]{64}", population_loss_stopped
                        )
                        is not None
                        and re.fullmatch(
                            r"[0-9a-f]{64}", population_loss_resource
                        )
                        is not None
                        and receipt.get(
                            "sync_tree_route_loss_admission_started_jobs", 0
                        )
                        == (2 if loss_admission_observer else 0)
                        and receipt.get(
                            "sync_tree_route_loss_admission_ready_bulk", 0
                        )
                        == (1 if loss_admission_observer else 0)
                        and (
                            re.fullmatch(
                                r"[0-9A-F]{64}", loss_admission_survivor
                            )
                            is not None
                            and loss_admission_survivor
                            != population_loss_stopped
                            if loss_admission_observer
                            else loss_admission_survivor == ""
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
                    population_loss_values = (
                        all(receipt.get(field, 0) == 0 for field in integer_fields)
                        and receipt.get(
                            "sync_tree_route_population_loss_pattern", ""
                        )
                        == ""
                        and population_loss_stopped == ""
                        and population_loss_resource == ""
                        and loss_admission_survivor == ""
                    )
                require(
                    receipt.get(
                        "sync_tree_route_population_loss_observed", False
                    )
                    is population_loss_observer
                    and population_loss_values,
                    f"{role} route-population loss evidence is invalid",
                )
                startup_admission_observer = (
                    scenario == "sync-tree-route-startup-admission"
                    and role == "client"
                )
                startup_admission_carrier = receipt.get(
                    "sync_tree_route_startup_admission_carrier", ""
                )
                startup_admission_resource = receipt.get(
                    "sync_tree_route_startup_admission_resource_sha256", ""
                )
                startup_admission_values = (
                    receipt.get("sync_tree_route_startup_admission_jobs") == 2
                    and receipt.get(
                        "sync_tree_route_startup_admission_artifact_bytes"
                    )
                    == 16_777_283
                    and receipt.get(
                        "sync_tree_route_startup_admission_delay_ms"
                    )
                    == 20_000
                    and receipt.get(
                        "sync_tree_route_startup_admission_restart_count"
                    )
                    == 1
                    and receipt.get(
                        "sync_tree_route_startup_admission_ready_bulk_before"
                    )
                    == 1
                    and receipt.get(
                        "sync_tree_route_startup_admission_ready_bulk_after"
                    )
                    == 2
                    and receipt.get(
                        "sync_tree_route_startup_admission_stable_samples", 0
                    )
                    >= 10
                    and re.fullmatch(
                        r"[0-9A-F]{64}", startup_admission_carrier
                    )
                    is not None
                    and receipt.get(
                        "sync_tree_route_startup_admission_live_jobs_after_join"
                    )
                    == 2
                    and receipt.get(
                        "sync_tree_route_startup_admission_preserved_carriers"
                    )
                    == 2
                    and receipt.get(
                        "sync_tree_route_startup_admission_adaptive_selections"
                    )
                    == 2
                    and receipt.get(
                        "sync_tree_route_startup_admission_activations"
                    )
                    == 2
                    and receipt.get(
                        "sync_tree_route_startup_admission_work_before"
                    )
                    == 4
                    and receipt.get(
                        "sync_tree_route_startup_admission_work_after"
                    )
                    == 0
                    and receipt.get(
                        "sync_tree_route_startup_admission_duration_ms", 0
                    )
                    > 0
                    and re.fullmatch(
                        r"[0-9a-f]{64}", startup_admission_resource
                    )
                    is not None
                    if startup_admission_observer
                    else all(
                        receipt.get(field, 0) == 0
                        for field in (
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
                    )
                    and startup_admission_carrier == ""
                    and startup_admission_resource == ""
                )
                require(
                    receipt.get(
                        "sync_tree_route_startup_admission_observed", False
                    )
                    is startup_admission_observer
                    and startup_admission_values,
                    f"{role} route-startup admission evidence is invalid",
                )
                throughput_observer = (
                    scenario == "sync-tree-route-throughput"
                    and role == "client"
                )
                throughput_durations = tuple(
                    receipt.get(field, 0)
                    for field in (
                        "sync_tree_route_throughput_fixed_a_duration_ms",
                        "sync_tree_route_throughput_adaptive_a_duration_ms",
                        "sync_tree_route_throughput_adaptive_b_duration_ms",
                        "sync_tree_route_throughput_fixed_b_duration_ms",
                    )
                )
                throughput_skews = tuple(
                    receipt.get(field, 0)
                    for field in (
                        "sync_tree_route_throughput_fixed_a_completion_skew_ms",
                        "sync_tree_route_throughput_adaptive_a_completion_skew_ms",
                        "sync_tree_route_throughput_adaptive_b_completion_skew_ms",
                        "sync_tree_route_throughput_fixed_b_completion_skew_ms",
                    )
                )
                throughput_resources = tuple(
                    receipt.get(field, "")
                    for field in (
                        "sync_tree_route_throughput_fixed_a_resource_sha256",
                        "sync_tree_route_throughput_adaptive_a_resource_sha256",
                        "sync_tree_route_throughput_adaptive_b_resource_sha256",
                        "sync_tree_route_throughput_fixed_b_resource_sha256",
                    )
                )
                throughput_fixed_total = receipt.get(
                    "sync_tree_route_throughput_fixed_total_duration_ms", 0
                )
                throughput_adaptive_total = receipt.get(
                    "sync_tree_route_throughput_adaptive_total_duration_ms", 0
                )
                throughput_bytes = 4 * 16_777_283
                if throughput_observer:
                    throughput_values = (
                        receipt.get(
                            "sync_tree_route_throughput_jobs_per_phase"
                        )
                        == 2
                        and receipt.get("sync_tree_route_throughput_phases")
                        == 4
                        and receipt.get(
                            "sync_tree_route_throughput_artifact_bytes"
                        )
                        == 16_777_283
                        and receipt.get(
                            "sync_tree_route_throughput_phase_order"
                        )
                        == "fixed-a,adaptive-a,adaptive-b,fixed-b"
                        and receipt.get(
                            "sync_tree_route_throughput_restart_count"
                        )
                        == 4
                        and receipt.get(
                            "sync_tree_route_throughput_restart_hold_ms"
                        )
                        == 5000
                        and receipt.get(
                            "sync_tree_route_throughput_fixed_patterns"
                        )
                        == "00,00"
                        and receipt.get(
                            "sync_tree_route_throughput_adaptive_patterns"
                        )
                        == "01,01"
                        and all(value > 0 for value in throughput_durations)
                        and all(
                            0 <= skew <= duration
                            for skew, duration in zip(
                                throughput_skews, throughput_durations
                            )
                        )
                        and throughput_fixed_total
                        == throughput_durations[0] + throughput_durations[3]
                        and throughput_adaptive_total
                        == throughput_durations[1] + throughput_durations[2]
                        and receipt.get(
                            "sync_tree_route_throughput_fixed_artifact_bps"
                        )
                        == throughput_bytes * 1000 // throughput_fixed_total
                        and receipt.get(
                            "sync_tree_route_throughput_adaptive_artifact_bps"
                        )
                        == throughput_bytes * 1000 // throughput_adaptive_total
                        and receipt.get(
                            "sync_tree_route_throughput_adaptive_speedup_ppm"
                        )
                        == throughput_fixed_total * 1_000_000
                        // throughput_adaptive_total
                        and receipt.get(
                            "sync_tree_route_throughput_fixed_selections"
                        )
                        == 4
                        and receipt.get(
                            "sync_tree_route_throughput_adaptive_selections"
                        )
                        == 4
                        and receipt.get(
                            "sync_tree_route_throughput_reassignments"
                        )
                        == 0
                        and receipt.get(
                            "sync_tree_route_throughput_activations"
                        )
                        == 8
                        and receipt.get(
                            "sync_tree_route_throughput_peak_work"
                        )
                        == 4
                        and receipt.get(
                            "sync_tree_route_throughput_work_after"
                        )
                        == 0
                        and all(
                            re.fullmatch(r"[0-9a-f]{64}", value) is not None
                            for value in throughput_resources
                        )
                    )
                else:
                    throughput_integer_fields = (
                        "sync_tree_route_throughput_jobs_per_phase",
                        "sync_tree_route_throughput_phases",
                        "sync_tree_route_throughput_artifact_bytes",
                        "sync_tree_route_throughput_restart_count",
                        "sync_tree_route_throughput_restart_hold_ms",
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
                    )
                    throughput_values = (
                        all(
                            receipt.get(field, 0) == 0
                            for field in throughput_integer_fields
                        )
                        and receipt.get(
                            "sync_tree_route_throughput_phase_order", ""
                        )
                        == ""
                        and receipt.get(
                            "sync_tree_route_throughput_fixed_patterns", ""
                        )
                        == ""
                        and receipt.get(
                            "sync_tree_route_throughput_adaptive_patterns", ""
                        )
                        == ""
                        and all(value == "" for value in throughput_resources)
                    )
                require(
                    receipt.get(
                        "sync_tree_route_throughput_observed", False
                    )
                    is throughput_observer
                    and throughput_values,
                    f"{role} route-throughput evidence is invalid",
                )
                concurrent_cancel_observer = (
                    scenario in SYNC_CONCURRENT_CANCEL_SCENARIOS
                    and role == "client"
                )
                concurrent_cancel_resource = receipt.get(
                    "sync_tree_route_concurrent_cancel_resource_sha256", ""
                )
                require(
                    receipt.get(
                        "sync_tree_route_concurrent_cancel_observed", False
                    )
                    is concurrent_cancel_observer
                    and (
                        receipt.get("sync_tree_route_concurrent_cancel_jobs")
                        == 8
                        and receipt.get(
                            "sync_tree_route_concurrent_cancel_artifact_bytes"
                        )
                        == SYNC_CONCURRENT_CANCEL_ARTIFACT_BYTES[scenario]
                        and receipt.get(
                            "sync_tree_route_concurrent_cancel_requested"
                        )
                        == 4
                        and receipt.get(
                            "sync_tree_route_concurrent_cancel_completed"
                        )
                        == 4
                        and receipt.get(
                            "sync_tree_route_concurrent_cancel_survivors"
                        )
                        == 4
                        and receipt.get(
                            "sync_tree_route_concurrent_cancel_survivor_activations"
                        )
                        == 4
                        and receipt.get(
                            "sync_tree_route_concurrent_cancel_pattern"
                        )
                        == "01010101"
                        and receipt.get(
                            "sync_tree_route_concurrent_cancel_route_zero"
                        )
                        == 2
                        and receipt.get(
                            "sync_tree_route_concurrent_cancel_route_one"
                        )
                        == 2
                        and isinstance(
                            receipt.get(
                                "sync_tree_route_concurrent_cancel_tail_ms"
                            ),
                            int,
                        )
                        and 0
                        <= receipt["sync_tree_route_concurrent_cancel_tail_ms"]
                        <= 5000
                        and receipt.get(
                            "sync_tree_route_concurrent_cancel_work_before", 0
                        )
                        > 0
                        and receipt.get(
                            "sync_tree_route_concurrent_cancel_work_after"
                        )
                        == 0
                        and receipt.get(
                            "sync_tree_route_concurrent_cancel_reassignments_delta"
                        )
                        == 0
                        and receipt.get(
                            "sync_tree_route_concurrent_cancel_adaptive_selections"
                        )
                        == 8
                        and re.fullmatch(
                            r"[0-9a-f]{64}", concurrent_cancel_resource
                        )
                        is not None
                        if concurrent_cancel_observer
                        else receipt.get(
                            "sync_tree_route_concurrent_cancel_jobs", 0
                        )
                        == 0
                        and receipt.get(
                            "sync_tree_route_concurrent_cancel_artifact_bytes",
                            0,
                        )
                        == 0
                        and receipt.get(
                            "sync_tree_route_concurrent_cancel_requested", 0
                        )
                        == 0
                        and receipt.get(
                            "sync_tree_route_concurrent_cancel_completed", 0
                        )
                        == 0
                        and receipt.get(
                            "sync_tree_route_concurrent_cancel_survivors", 0
                        )
                        == 0
                        and receipt.get(
                            "sync_tree_route_concurrent_cancel_survivor_activations",
                            0,
                        )
                        == 0
                        and receipt.get(
                            "sync_tree_route_concurrent_cancel_pattern", ""
                        )
                        == ""
                        and receipt.get(
                            "sync_tree_route_concurrent_cancel_route_zero", 0
                        )
                        == 0
                        and receipt.get(
                            "sync_tree_route_concurrent_cancel_route_one", 0
                        )
                        == 0
                        and receipt.get(
                            "sync_tree_route_concurrent_cancel_tail_ms", 0
                        )
                        == 0
                        and receipt.get(
                            "sync_tree_route_concurrent_cancel_work_before", 0
                        )
                        == 0
                        and receipt.get(
                            "sync_tree_route_concurrent_cancel_work_after", 0
                        )
                        == 0
                        and receipt.get(
                            "sync_tree_route_concurrent_cancel_reassignments_delta",
                            0,
                        )
                        == 0
                        and receipt.get(
                            "sync_tree_route_concurrent_cancel_adaptive_selections",
                            0,
                        )
                        == 0
                        and concurrent_cancel_resource == ""
                    ),
                    f"{role} concurrent route-cancellation evidence is invalid",
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
                route_cancel_carrier = receipt.get(
                    "sync_tree_route_cancel_carrier", ""
                )
                require(
                    receipt.get("sync_tree_route_cancel_observed", False)
                    is route_cancel_scenario
                    and (
                        re.fullmatch(r"[0-9A-F]{64}", route_cancel_carrier)
                        is not None
                        and isinstance(
                            receipt.get("sync_tree_route_cancel_worker_id"), int
                        )
                        and receipt["sync_tree_route_cancel_worker_id"] > 0
                        and isinstance(
                            receipt.get("sync_tree_route_cancel_tail_ms"), int
                        )
                        and 0 <= receipt["sync_tree_route_cancel_tail_ms"] <= 5000
                        and isinstance(
                            receipt.get("sync_tree_route_cancel_work_before"), int
                        )
                        and receipt["sync_tree_route_cancel_work_before"] > 0
                        and receipt.get("sync_tree_route_cancel_work_after") == 0
                        and receipt.get(
                            "sync_tree_route_cancel_reassignments_delta"
                        )
                        in ({0, 1} if route_cancel_race_scenario else {0})
                        and receipt.get(
                            "sync_tree_route_cancel_adaptive_selections"
                        )
                        == (
                            1 + receipt.get(
                                "sync_tree_route_cancel_reassignments_delta"
                            )
                            if route_cancel_race_scenario
                            else 2 if route_loss_cancel_scenario else 1
                        )
                        if route_cancel_scenario
                        else route_cancel_carrier == ""
                        and receipt.get("sync_tree_route_cancel_worker_id", 0) == 0
                        and receipt.get("sync_tree_route_cancel_tail_ms", 0) == 0
                        and receipt.get("sync_tree_route_cancel_work_before", 0)
                        == 0
                        and receipt.get("sync_tree_route_cancel_work_after", 0)
                        == 0
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
                    require(
                        receipt["sync_tree_route_cancel_carrier"]
                        == receipt["sync_tree_route_loss_final_carrier"]
                        and receipt["sync_tree_route_cancel_carrier"]
                        != receipt["sync_tree_route_loss_stopped_carrier"],
                        "client loss-before-cancel carrier order is invalid",
                    )
                if (
                    scenario == "sync-tree-route-cancel-loss"
                    and role == "client"
                ):
                    require(
                        receipt["sync_tree_route_cancel_carrier"]
                        == receipt["sync_tree_route_loss_final_carrier"]
                        == receipt["sync_tree_route_loss_stopped_carrier"]
                        and receipt["sync_tree_route_loss_position_bytes"] == 0
                        and receipt["sync_tree_route_loss_carrier_losses"] == 1
                        and receipt["sync_tree_route_loss_reassignments"] == 0
                        and receipt["sync_tree_route_loss_stale_terminals"] >= 1
                        and receipt["sync_tree_route_loss_recoveries"] == 1,
                        "client cancel-before-loss carrier order is invalid",
                    )
                if route_cancel_race_scenario and role == "client":
                    race_reassignments = receipt[
                        "sync_tree_route_loss_reassignments"
                    ]
                    require(
                        receipt["sync_tree_route_cancel_carrier"]
                        == receipt[
                            "sync_tree_route_loss_stopped_carrier"
                        ]
                        and race_reassignments
                        == receipt[
                            "sync_tree_route_cancel_reassignments_delta"
                        ]
                        and (
                            race_outcome == "cancel-first"
                            and race_reassignments == 0
                            and receipt[
                                "sync_tree_route_loss_final_carrier"
                            ]
                            == receipt[
                                "sync_tree_route_loss_stopped_carrier"
                            ]
                            or race_outcome == "loss-first"
                            and race_reassignments == 1
                            and receipt[
                                "sync_tree_route_loss_final_carrier"
                            ]
                            != receipt[
                                "sync_tree_route_loss_stopped_carrier"
                            ]
                        ),
                        "client cancel/loss race outcome is invalid",
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
                        re.fullmatch(r"[0-9a-f]{64}", str(pressure_a)) is not None
                        and re.fullmatch(r"[0-9a-f]{64}", str(pressure_b)) is not None
                        and pressure_a != pressure_b
                        if pressure_scenario
                        else pressure_a == "" and pressure_b == ""
                    ),
                    f"{role} deterministic tree worker-pressure evidence is invalid",
                )
                quota_scenario = scenario in SYNC_TREE_QUOTA_SCENARIOS
                object_quota_scenario = scenario == "sync-tree-object-quota"
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
                    and receipt.get("sync_tree_quota_kind", "")
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
                    and receipt.get("sync_tree_quota_maximum_objects", 0)
                    == (
                        6
                        if object_quota_scenario
                        else 32 if quota_scenario else 0
                    )
                    and receipt.get("sync_tree_quota_inventory_objects", 0)
                    == (
                        6
                        if object_quota_scenario
                        else 2 if quota_scenario else 0
                    )
                    and (
                        receipt["sync_tree_quota_inventory_bytes"]
                        < receipt["sync_tree_quota_store_bytes"]
                        and (
                            receipt["sync_tree_quota_inventory_objects"]
                            == receipt["sync_tree_quota_maximum_objects"]
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
                        and re.fullmatch(r"[0-9a-f]{64}", str(quota_head))
                        is not None
                        and re.fullmatch(r"[0-9a-f]{64}", str(quota_artifact))
                        is not None
                        and re.fullmatch(r"[0-9a-f]{64}", str(quota_manifest))
                        is not None
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
                        re.fullmatch(r"[0-9a-f]{64}", str(read_only_head))
                        is not None
                        and re.fullmatch(
                            r"[0-9a-f]{64}", str(read_only_artifact)
                        )
                        is not None
                        and re.fullmatch(
                            r"[0-9a-f]{64}", str(read_only_manifest)
                        )
                        is not None
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
                    receipt.get(
                        "sync_tree_memory_publisher_baseline_hwm_kib", 0
                    ),
                    receipt.get(
                        "sync_tree_memory_publisher_post_publish_hwm_kib", 0
                    ),
                    receipt.get("sync_tree_memory_publisher_peak_hwm_kib", 0),
                    receipt.get("sync_tree_memory_publisher_delta_hwm_kib", 0),
                    receipt.get(
                        "sync_tree_memory_subscriber_baseline_hwm_kib", 0
                    ),
                    receipt.get(
                        "sync_tree_memory_subscriber_post_pull_hwm_kib", 0
                    ),
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
                        and memory_values[11] == max(memory_values[5], memory_values[9])
                        and memory_values[12] == max(memory_values[6], memory_values[10])
                        and re.fullmatch(r"[0-9a-f]{64}", str(memory_head))
                        is not None
                        and re.fullmatch(r"[0-9a-f]{64}", str(memory_artifact))
                        is not None
                        and re.fullmatch(r"[0-9a-f]{64}", str(memory_manifest))
                        is not None
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
                        re.fullmatch(r"[0-9a-f]{64}", str(source_corrupt_head))
                        is not None
                        and re.fullmatch(
                            r"[0-9a-f]{64}", str(source_corrupt_artifact)
                        )
                        is not None
                        and re.fullmatch(
                            r"[0-9a-f]{64}", str(source_corrupt_manifest)
                        )
                        is not None
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
                        re.fullmatch(
                            r"[0-9a-f]{64}", str(destination_corrupt_head)
                        )
                        is not None
                        and re.fullmatch(
                            r"[0-9a-f]{64}", str(destination_corrupt_artifact)
                        )
                        is not None
                        and re.fullmatch(
                            r"[0-9a-f]{64}", str(destination_corrupt_manifest)
                        )
                        is not None
                        and re.fullmatch(
                            r"[0-9a-f]{64}", str(destination_corrupt_file_id)
                        )
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
                control_replay_scenario = (
                    scenario == "sync-tree-control-replay"
                )
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
                        re.fullmatch(r"[0-9a-f]{64}", str(control_replay_head))
                        is not None
                        and re.fullmatch(
                            r"[0-9a-f]{64}", str(control_replay_artifact)
                        )
                        is not None
                        and re.fullmatch(
                            r"[0-9a-f]{64}", str(control_replay_manifest)
                        )
                        is not None
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
                repair_scenario = scenario == "sync-file-repair"
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
                    is repair_scenario
                    and receipt.get("sync_gc_dry_candidates", 0)
                    == (1 if repair_scenario else 0)
                    and receipt.get("sync_gc_moved_objects", 0)
                    == (1 if repair_scenario else 0)
                    and receipt.get("sync_gc_durable_objects", 0)
                    == (1 if repair_scenario else 0)
                    and receipt.get("sync_gc_outside_sentinels", 0)
                    == (2 if repair_scenario else 0)
                    and receipt.get("sync_gc_purge_disabled", False)
                    is repair_scenario
                    and receipt.get("sync_gc_mount_refused", False)
                    is repair_scenario,
                    f"{role} synchronization repair evidence is invalid",
                )
                if scenario in SYNC_POSITIVE_RANGE_SCENARIOS:
                    retry_scenario = scenario == "sync-file-range-retry"
                    require(
                        receipt.get("sync_range_observed") is True
                        and receipt.get("sync_range_fallback_observed") is False
                        and receipt.get("sync_corrupt_basis_preserved") is False
                        and receipt.get("sync_range_retry_observed", False)
                        is retry_scenario
                        and isinstance(receipt.get("sync_range_count"), int)
                        and receipt["sync_range_count"] > 0
                        and isinstance(receipt.get("sync_range_reused_bytes"), int)
                        and receipt["sync_range_reused_bytes"] > 0
                        and isinstance(receipt.get("sync_range_fetched_bytes"), int)
                        and 0 < receipt["sync_range_fetched_bytes"]
                        < receipt["sync_artifact_bytes"]
                        and receipt["sync_range_reused_bytes"]
                        + receipt["sync_range_fetched_bytes"]
                        == receipt["sync_artifact_bytes"],
                        f"{role} bounded-range evidence is incomplete",
                    )
                    retry_position = receipt.get(
                        "sync_range_retry_position_bytes", 0
                    )
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
                    first_file_id = receipt.get(
                        "sync_range_retry_first_file_id", ""
                    )
                    second_file_id = receipt.get(
                        "sync_range_retry_second_file_id", ""
                    )
                    require(
                        (
                            isinstance(retry_position, int)
                            and 0 < retry_position
                            == retry_retained
                            == retry_resumed
                            < receipt["sync_range_fetched_bytes"]
                            and retry_discarded == 0
                            and retry_retention_fallbacks == 0
                            and isinstance(first_file_id, str)
                            and isinstance(second_file_id, str)
                            and re.fullmatch(r"[0-9a-f]{64}", first_file_id)
                            is not None
                            and re.fullmatch(r"[0-9a-f]{64}", second_file_id)
                            is not None
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
                        f"{role} bounded-range retry evidence is invalid",
                    )
                elif scenario == "sync-file-corrupt-basis":
                    require(
                        receipt.get("sync_range_observed") is False
                        and receipt.get("sync_range_fallback_observed") is True
                        and receipt.get("sync_corrupt_basis_preserved") is True
                        and receipt.get("sync_range_retry_observed") is False
                        and receipt.get("sync_range_retry_position_bytes") == 0
                        and receipt.get("sync_range_retry_retained_bytes") == 0
                        and receipt.get("sync_range_retry_resumed_bytes") == 0
                        and receipt.get("sync_range_retry_discarded_bytes") == 0
                        and receipt.get("sync_range_retry_retention_fallbacks") == 0
                        and receipt.get("sync_range_retry_first_file_id") == ""
                        and receipt.get("sync_range_retry_second_file_id") == ""
                        and receipt.get("sync_range_count") == 0
                        and receipt.get("sync_range_reused_bytes") == 0
                        and receipt.get("sync_range_fetched_bytes") == 0,
                        f"{role} corrupt-basis fallback evidence is incomplete",
                    )
                else:
                    require(
                        receipt.get("sync_range_observed", False) is False
                        and receipt.get("sync_range_fallback_observed", False) is False
                        and receipt.get("sync_corrupt_basis_preserved", False) is False
                        and receipt.get("sync_range_retry_observed", False) is False
                        and receipt.get("sync_range_retry_position_bytes", 0) == 0
                        and receipt.get("sync_range_retry_retained_bytes", 0) == 0
                        and receipt.get("sync_range_retry_resumed_bytes", 0) == 0
                        and receipt.get("sync_range_retry_discarded_bytes", 0) == 0
                        and receipt.get("sync_range_retry_retention_fallbacks", 0) == 0
                        and receipt.get("sync_range_retry_first_file_id", "") == ""
                        and receipt.get("sync_range_retry_second_file_id", "") == ""
                        and receipt.get("sync_range_count", 0) == 0
                        and receipt.get("sync_range_reused_bytes", 0) == 0
                        and receipt.get("sync_range_fetched_bytes", 0) == 0,
                        f"{role} non-range scenario claims range reuse",
                    )
                range_restart = scenario == "sync-file-range-restart-resume"
                range_restart_values = {
                    name: receipt.get(f"sync_range_restart_{name}", 0)
                    for name in (
                        "interrupted_bytes",
                        "retained_bytes",
                        "resumed_attempts",
                        "resumed_bytes",
                        "suffix_bytes",
                        "first_job_id",
                        "second_job_id",
                        "first_attempt_id",
                        "second_attempt_id",
                        "first_message_id",
                        "second_message_id",
                    )
                }
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
                            for value in range_restart_values.values()
                        )
                        and range_restart_values["resumed_attempts"] == 1
                        and 0
                        < range_restart_values["interrupted_bytes"]
                        == range_restart_values["retained_bytes"]
                        == range_restart_values["resumed_bytes"]
                        < receipt["sync_range_fetched_bytes"]
                        and range_restart_values["resumed_bytes"]
                        + range_restart_values["suffix_bytes"]
                        == receipt["sync_range_fetched_bytes"]
                        and all(
                            range_restart_values[name] > 0
                            for name in (
                                "first_job_id",
                                "second_job_id",
                                "first_attempt_id",
                                "second_attempt_id",
                                "first_message_id",
                                "second_message_id",
                            )
                        )
                        and range_restart_values["first_job_id"]
                        != range_restart_values["second_job_id"]
                        and range_restart_values["first_attempt_id"]
                        != range_restart_values["second_attempt_id"]
                        and range_restart_values["first_message_id"]
                        != range_restart_values["second_message_id"]
                        and all(
                            re.fullmatch(r"[0-9a-f]{64}", value) is not None
                            for value in range_restart_file_ids
                        )
                        and range_restart_file_ids[0]
                        != range_restart_file_ids[1]
                        if range_restart
                        else all(
                            value == 0
                            for value in range_restart_values.values()
                        )
                        and range_restart_file_ids == ("", "")
                    ),
                    f"{role} bounded-range restart evidence is invalid",
                )
                if scenario in {
                    "sync-file-restart",
                    "sync-file-restart-resume",
                    "sync-file-range-restart-resume",
                    *CONTENT_RESTART_SCENARIOS,
                }:
                    require(
                        receipt.get("sync_restart_observed") is True
                        and receipt.get("sync_restart_recovery_observed") is True
                        and receipt.get("sync_restart_identity_preserved") is True,
                        f"{role} synchronization restart boundary is incomplete",
                    )
                    restart_prefix_resume = (
                        scenario == "sync-file-restart-resume"
                    )
                    require(
                        receipt.get(
                            "sync_restart_prefix_resume_observed", False
                        )
                        is restart_prefix_resume
                        and isinstance(
                            receipt.get("sync_restart_resumed_attempts", 0),
                            int,
                        )
                        and isinstance(
                            receipt.get("sync_restart_resumed_bytes", 0), int
                        )
                        and (
                            1
                            <= receipt["sync_restart_resumed_attempts"]
                            <= 2
                            and 0
                            < receipt["sync_restart_resumed_bytes"]
                            < receipt["sync_artifact_bytes"]
                            + receipt["sync_manifest_bytes"]
                            if restart_prefix_resume
                            else receipt.get("sync_restart_resumed_attempts", 0)
                            == 0
                            and receipt.get("sync_restart_resumed_bytes", 0)
                            == 0
                        ),
                        f"{role} restart-prefix continuation evidence is invalid",
                    )
                    if role == "client":
                        require(
                            receipt.get("sync_daemon_restart_count") == 1
                            and receipt.get("sync_attempt_recovery_observed") is True
                            and receipt.get("sync_unclean_stop_observed") is True
                            and receipt.get("sync_peer_offline_observed") is False
                            and isinstance(
                                receipt.get("sync_interrupted_staging_bytes"), int
                            )
                            and 0
                            < receipt["sync_interrupted_staging_bytes"]
                            < receipt["sync_artifact_bytes"]
                            + receipt["sync_manifest_bytes"],
                            "client synchronization attempt was not durably recovered",
                        )
                        if restart_prefix_resume:
                            require(
                                receipt["sync_restart_resumed_bytes"]
                                == receipt["sync_interrupted_staging_bytes"],
                                "client restart did not resume the exact interrupted prefix",
                            )
                    else:
                        require(
                            receipt.get("sync_daemon_restart_count") == 0
                            and receipt.get("sync_attempt_recovery_observed") is False
                            and receipt.get("sync_unclean_stop_observed") is False
                            and receipt.get("sync_peer_offline_observed") is True
                            and receipt.get("sync_interrupted_staging_bytes") == 0
                            and receipt.get("recovered_online_epoch", 0)
                            > receipt.get("initial_online_epoch", 0),
                            "publisher did not observe the subscriber restart epoch",
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
                        total_chunks = receipt.get(
                            "content_restart_total_chunks", 0
                        )
                        total_objects = receipt.get(
                            "content_restart_total_objects", 0
                        )
                        require(
                            receipt.get("content_restart_observed", False)
                            is content_restart
                            and receipt.get("content_restart_cap", 0)
                            == (content_cap if content_restart else 0)
                            and receipt.get("content_restart_live_lanes", 0)
                            == (content_cap if content_restart else 0)
                            and (
                                re.fullmatch(
                                    r"[0-9a-f]{64}",
                                    str(
                                        receipt.get(
                                            "content_restart_live_lane_set_sha256",
                                            "",
                                        )
                                    ),
                                )
                                is not None
                                if content_restart
                                else receipt.get(
                                    "content_restart_live_lane_set_sha256", ""
                                )
                                == ""
                            )
                            and (
                                isinstance(
                                    receipt.get("content_restart_first_job_id"),
                                    int,
                                )
                                and isinstance(
                                    receipt.get("content_restart_second_job_id"),
                                    int,
                                )
                                and receipt["content_restart_first_job_id"] > 0
                                and receipt["content_restart_second_job_id"] > 0
                                and receipt["content_restart_first_job_id"]
                                != receipt["content_restart_second_job_id"]
                                and isinstance(total_chunks, int)
                                and total_chunks >= content_cap
                                and isinstance(total_objects, int)
                                and total_objects >= content_cap + 2
                                and isinstance(transport_files, int)
                                and 2 <= transport_files <= content_cap
                                and 0
                                < receipt.get(
                                    "content_restart_crash_transport_bytes", 0
                                )
                                < receipt["sync_artifact_bytes"]
                                and receipt.get(
                                    "content_restart_crash_canonical_partials"
                                )
                                == 0
                                and isinstance(crash_objects, int)
                                and 2 <= crash_objects < total_objects
                                and isinstance(recovered_objects, int)
                                and recovered_objects == crash_objects
                                and isinstance(crash_bytes, int)
                                and 0 < crash_bytes < receipt["sync_artifact_bytes"]
                                and isinstance(recovered_bytes, int)
                                and recovered_bytes == crash_bytes
                                and receipt.get(
                                    "content_restart_recovery_committed_delta"
                                )
                                == recovered_objects - crash_objects
                                and receipt[
                                    "content_restart_recovery_committed_delta"
                                ]
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
                                    re.fullmatch(r"[0-9a-f]{64}", str(value))
                                    is not None
                                    for value in (
                                        receipt.get(
                                            "content_restart_crash_inventory_sha256",
                                            "",
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
                                == receipt[
                                    "content_restart_recovered_inventory_sha256"
                                ]
                                if content_restart
                                else receipt.get(
                                    "content_restart_first_job_id", 0
                                )
                                == 0
                                and receipt.get(
                                    "content_restart_second_job_id", 0
                                )
                                == 0
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
                                    "content_restart_post_start_transport_files",
                                    0,
                                )
                                == 0
                                and receipt.get(
                                    "content_restart_post_start_canonical_partials",
                                    0,
                                )
                                == 0
                                and receipt.get(
                                    "content_restart_crash_inventory_sha256", ""
                                )
                                == ""
                                and receipt.get(
                                    "content_restart_recovered_inventory_sha256",
                                    "",
                                )
                                == ""
                            ),
                            f"{role} multi-lane content restart evidence is invalid",
                        )
                elif scenario == "sync-file-guest-restart":
                    interrupted_bytes = receipt.get(
                        "sync_guest_restart_staging_bytes"
                    )
                    require(
                        receipt.get("sync_restart_observed") is True
                        and receipt.get("sync_restart_recovery_observed") is True
                        and receipt.get("sync_restart_identity_preserved") is True
                        and receipt.get("sync_attempt_recovery_observed") is False
                        and receipt.get("sync_unclean_stop_observed") is False
                        and receipt.get("sync_daemon_restart_count") == 0
                        and receipt.get("sync_peer_offline_observed")
                        is (role == "client")
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
                            isinstance(interrupted_bytes, int)
                            and (
                                0
                                < interrupted_bytes
                                < receipt["sync_artifact_bytes"]
                                + receipt["sync_manifest_bytes"]
                                if role == "client"
                                else interrupted_bytes == 0
                            )
                        ),
                        f"{role} synchronization guest-restart boundary is incomplete",
                    )
                elif scenario == "sync-file-disconnect":
                    interrupted_bytes = receipt.get(
                        "sync_disconnect_staging_bytes"
                    )
                    require(
                        receipt.get("sync_restart_observed") is False
                        and receipt.get("sync_restart_recovery_observed") is False
                        and receipt.get("sync_restart_identity_preserved") is False
                        and receipt.get("sync_attempt_recovery_observed") is False
                        and receipt.get("sync_unclean_stop_observed") is False
                        and receipt.get("sync_daemon_restart_count") == 0
                        and receipt.get("sync_peer_offline_observed") is True
                        and receipt.get("sync_disconnect_cleanup_observed") is True
                        and receipt.get("sync_disconnect_retry_observed") is True
                        and receipt.get("sync_disconnect_stable_samples") == 50
                        and receipt.get("sync_guest_restart_staging_bytes", 0) == 0
                        and receipt.get(
                            "sync_guest_restart_cleanup_observed", False
                        )
                        is False
                        and receipt.get(
                            "sync_guest_restart_retry_observed", False
                        )
                        is False
                        and receipt.get("sync_guest_restart_stable_samples", 0) == 0
                        and receipt.get("recovered_online_epoch", 0)
                        > receipt.get("initial_online_epoch", 0)
                        and (
                            isinstance(interrupted_bytes, int)
                            and 0
                            < interrupted_bytes
                            < receipt["sync_artifact_bytes"]
                            + receipt["sync_manifest_bytes"]
                            if role == "client"
                            else interrupted_bytes == 0
                        ),
                        f"{role} synchronization disconnect boundary is incomplete",
                    )
                else:
                    require(
                        receipt.get("sync_restart_observed") is False
                        and receipt.get("sync_peer_offline_observed") is False
                        and receipt.get("sync_restart_recovery_observed") is False
                        and receipt.get("sync_restart_identity_preserved") is False
                        and receipt.get("sync_attempt_recovery_observed") is False
                        and receipt.get("sync_unclean_stop_observed") is False
                        and receipt.get("sync_daemon_restart_count") == 0
                        and receipt.get("sync_interrupted_staging_bytes") == 0,
                        f"{role} baseline synchronization claims a restart",
                    )
                    require(
                        receipt.get("sync_disconnect_staging_bytes", 0) == 0
                        and receipt.get("sync_disconnect_cleanup_observed", False)
                        is False
                        and receipt.get("sync_disconnect_retry_observed", False)
                        is False
                        and receipt.get("sync_disconnect_stable_samples", 0) == 0,
                        f"{role} non-disconnect sync scenario claims disconnect recovery",
                    )
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
                        f"{role} non-guest-restart sync scenario claims reboot recovery",
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
                        and isinstance(receipt.get("sync_pause_file_id"), str)
                        and re.fullmatch(
                            r"[0-9a-f]{64}", receipt["sync_pause_file_id"]
                        )
                        is not None
                        if pause
                        else pause_position == 0
                        and receipt.get("sync_pause_stable_samples", 0) == 0
                        and receipt.get("sync_pause_file_id", "") == ""
                    ),
                    f"{role} synchronization pause/resume boundary is invalid",
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
            require(chain.get("status") == "guest-evidence-observed", f"{role} guest evidence missing")
            receipts[role] = {
                "path": str(receipt_path.relative_to(pair_root)),
                "sha256": sha256(receipt_path),
                "binary_sha256": receipt["binary_sha256"],
                "peer_key_sha256": receipt["peer_key_sha256"],
            }
            chains[role] = {
                "path": str(chain_path.relative_to(pair_root)),
                "sha256": sha256(chain_path),
                "status": chain["status"],
            }
        require(
            receipts["client"]["binary_sha256"] == receipts["device"]["binary_sha256"],
            "guest binary digests differ",
        )
        if scenario in SYNC_SCENARIOS:
            client_sync = load(pair_root / receipts["client"]["path"])
            device_sync = load(pair_root / receipts["device"]["path"])
            for field in (
                "sync_generation",
                "sync_artifact_bytes",
                "sync_manifest_bytes",
                "sync_artifact_sha256",
                "sync_manifest_sha256",
                "sync_head_record",
            ):
                require(
                    client_sync[field] == device_sync[field],
                    f"synchronization receipts disagree on {field}",
                )
            if scenario in CONTENT_MULTI_SOURCE_SCENARIOS:
                for field in (
                    "multi_source_count",
                    "multi_source_atomic_pull_observed",
                    "multi_source_availability_requests",
                    "multi_source_availability_results",
                    "multi_source_secondary_key_sha256",
                    "multi_source_secondary_principal_sha256",
                ):
                    require(
                        client_sync[field] == device_sync[field],
                        f"multi-source receipts disagree on {field}",
                    )
                if scenario in CONTENT_MULTI_SOURCE_LOSS_SCENARIOS:
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
                            client_sync[field] == device_sync[field],
                            "selected-source loss receipts disagree on "
                            f"{field}",
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
                            client_sync[field] == device_sync[field],
                            "exact routed source-loss receipts disagree on "
                            f"{field}",
                        )
            if scenario in SIGNED_UPDATE_SCENARIOS:
                for field in (
                    "signed_update_observed",
                    "signed_update_release_sequence",
                    "signed_update_payload_sha256",
                    "signed_update_manifest_record",
                    "signed_update_startup_disposition",
                    "signed_update_confirmed",
                    "signed_update_current_sha256",
                    "signed_update_restart_count",
                    "signed_update_feature_advertised",
                    "signed_update_remote_stage_observed",
                    "signed_update_sender_epoch",
                    "signed_update_message_id",
                    "update_service_pre_ready_exit_observed",
                    "update_service_agent_death_observed",
                    "update_service_parent_death_observed",
                    "update_service_health_expiry_observed",
                    "update_service_ready_observed",
                    "update_service_confirmed_recovery_observed",
                    "update_service_rollback_count",
                    "update_service_payload_kind",
                    "update_service_image_sealed",
                ):
                    require(
                        client_sync[field] == device_sync[field],
                        f"signed-update receipts disagree on {field}",
                    )
            if scenario in SYNC_TREE_SCENARIOS:
                for field in (
                    "sync_tree_observed",
                    "sync_tree_directories",
                    "sync_tree_files",
                    "sync_tree_content_bytes",
                    "sync_tree_payload_sha256",
                ):
                    require(
                        client_sync[field] == device_sync[field],
                        f"synchronization tree receipts disagree on {field}",
                    )
                if scenario == "sync-tree-adversity":
                    for field in (
                        "sync_tree_rollback_refused",
                        "sync_tree_fork_refused",
                        "sync_tree_enospc_observed",
                        "sync_tree_enospc_retry_observed",
                        "sync_tree_enospc_reserved_bytes",
                        "sync_tree_enospc_failure_free_bytes",
                        "sync_tree_publisher_restart_count",
                    ):
                        require(
                            client_sync[field] == device_sync[field],
                            f"synchronization tree adversity receipts disagree on {field}",
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
                            client_sync[field] == device_sync[field],
                            f"synchronization tree worker-pressure receipts disagree on {field}",
                        )
                if scenario in SYNC_TREE_QUOTA_SCENARIOS:
                    for field in (
                        "sync_tree_quota_observed",
                        "sync_tree_quota_kind",
                        "sync_tree_quota_store_bytes",
                        "sync_tree_quota_inventory_bytes",
                        "sync_tree_quota_maximum_objects",
                        "sync_tree_quota_inventory_objects",
                        "sync_tree_quota_candidate_head_record",
                        "sync_tree_quota_candidate_artifact_sha256",
                        "sync_tree_quota_candidate_manifest_sha256",
                    ):
                        require(
                            client_sync[field] == device_sync[field],
                            f"synchronization tree quota receipts disagree on {field}",
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
                            client_sync[field] == device_sync[field],
                            f"synchronization tree read-only receipts disagree on {field}",
                        )
                if scenario == "sync-tree-memory":
                    for field in (
                        "sync_tree_memory_observed",
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
                    ):
                        require(
                            client_sync[field] == device_sync[field],
                            f"synchronization tree memory receipts disagree on {field}",
                        )
                if scenario == "sync-tree-source-corrupt":
                    for field in (
                        "sync_tree_source_corrupt_observed",
                        "sync_tree_source_corrupt_refused",
                        "sync_tree_source_corrupt_repaired",
                        "sync_tree_source_corrupt_retry_observed",
                        "sync_tree_source_corrupt_head_record",
                        "sync_tree_source_corrupt_artifact_sha256",
                        "sync_tree_source_corrupt_manifest_sha256",
                        "sync_tree_source_corrupt_artifact_bytes",
                        "sync_tree_source_corrupt_manifest_bytes",
                        "sync_tree_source_corrupt_quarantined_objects",
                        "sync_tree_source_corrupt_quarantined_bytes",
                    ):
                        require(
                            client_sync[field] == device_sync[field],
                            f"synchronization publisher-source corruption receipts disagree on {field}",
                        )
                if scenario == "sync-tree-destination-corrupt":
                    for field in (
                        "sync_tree_destination_corrupt_observed",
                        "sync_tree_destination_corrupt_rejected",
                        "sync_tree_destination_corrupt_retry_observed",
                        "sync_tree_destination_corrupt_head_record",
                        "sync_tree_destination_corrupt_artifact_sha256",
                        "sync_tree_destination_corrupt_manifest_sha256",
                        "sync_tree_destination_corrupt_artifact_bytes",
                        "sync_tree_destination_corrupt_manifest_bytes",
                        "sync_tree_destination_corrupt_file_id",
                        "sync_tree_destination_corrupt_position_bytes",
                        "sync_tree_destination_corrupt_committed_before_failure",
                        "sync_tree_destination_corrupt_retry_requested_objects",
                    ):
                        require(
                            client_sync[field] == device_sync[field],
                            f"synchronization subscriber-destination corruption receipts disagree on {field}",
                        )
                if scenario == "sync-tree-control-replay":
                    for field in (
                        "sync_tree_control_replay_observed",
                        "sync_tree_control_replay_exact_replay_observed",
                        "sync_tree_control_replay_reordered_result_observed",
                        "sync_tree_control_replay_conflict_refused",
                        "sync_tree_control_replay_activation_observed",
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
                    ):
                        require(
                            client_sync[field] == device_sync[field],
                            f"synchronization control replay receipts disagree on {field}",
                        )
            if scenario in SYNC_RANGE_SCENARIOS:
                for field in (
                    "sync_range_observed",
                    "sync_range_fallback_observed",
                    "sync_corrupt_basis_preserved",
                    "sync_range_retry_observed",
                    "sync_range_retry_position_bytes",
                    "sync_range_retry_retained_bytes",
                    "sync_range_retry_resumed_bytes",
                    "sync_range_retry_discarded_bytes",
                    "sync_range_retry_retention_fallbacks",
                    "sync_range_retry_first_file_id",
                    "sync_range_retry_second_file_id",
                    "sync_range_restart_resume_observed",
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
                    "sync_range_count",
                    "sync_range_reused_bytes",
                    "sync_range_fetched_bytes",
                ):
                    require(
                        client_sync[field] == device_sync[field],
                        f"synchronization range receipts disagree on {field}",
                    )
            if scenario == "sync-file-pause":
                for field in (
                    "sync_pause_position_bytes",
                    "sync_pause_stable_samples",
                    "sync_pause_file_id",
                ):
                    require(
                        client_sync[field] == device_sync[field],
                        f"synchronization pause receipts disagree on {field}",
                    )
            if scenario == "sync-file-repair":
                for field in (
                    "sync_repair_observed",
                    "sync_repair_recovery_observed",
                    "sync_repair_clean_retry_observed",
                    "sync_repair_quarantine_preserved",
                    "sync_repair_state_preserved",
                    "sync_repair_inspected_objects",
                    "sync_repair_quarantined_objects",
                    "sync_repair_quarantined_bytes",
                    "sync_gc_observed",
                    "sync_gc_dry_candidates",
                    "sync_gc_moved_objects",
                    "sync_gc_durable_objects",
                    "sync_gc_outside_sentinels",
                    "sync_gc_purge_disabled",
                    "sync_gc_mount_refused",
                ):
                    require(
                        client_sync[field] == device_sync[field],
                        f"synchronization repair receipts disagree on {field}",
                    )
        require(
            not any((path / "iotox-input/device.toxsave").exists() for path in workspace.values()),
            "raw injected savedata remained in a workspace export",
        )

        payload_summary = actual_tor_payload_summary(
            pair_root, receipts, actual_tor_payload
        )
        i2p_payload_summary = actual_i2p_payload_summary(
            pair_root, receipts, actual_i2p_payload
        )
        manifest = {
            "schema": "iotox.sandwurm-pair-manifest.v0",
            "status": "passed",
            "route_mode": route,
            "scenario": scenario,
            "expected_connection": expected_connection,
            "network": expected_network(route),
            "simultaneous_vmm_chains_observed": True,
            "rendezvous_monotonic_span_ns": completed_ns - started_ns,
            "prepared_bridge": "sandwurm-vm",
            "bootstrap_fixture": "pinned-host-bridge-c-toxcore-0.2.23",
            "bootstrap_fixture_restart_count": fixture_restart_count,
            "bootstrap_fixture_key_preserved": fixture_key_preserved,
            "socks5_proxy": (
                f"{HOST_BRIDGE_ADDRESS}:{SOCKS5_PORT}"
                if routed_socks5
                else None
            ),
            "socks5_allowed_target": (
                f"{HOST_BRIDGE_ADDRESS}:{BOOTSTRAP_PORT}"
                if routed_socks5
                else None
            ),
            "socks5_forwarder_sha256": (
                sha256(ROOT / "tools/run-socks5-forwarder.py")
                if routed_socks5
                else None
            ),
            "socks5_restart_count": socks5_restart_count,
            "socks5_admitted": socks5_admitted,
            "socks5_denied": socks5_denied,
            "socks5_audits": socks5_audits,
            "actual_tor": actual_tor,
            "actual_i2p": actual_i2p,
            "actual_i2p_topology_ready": (
                i2p_topology_final.get("status") == "passed" if actual_i2p else False
            ),
            "actual_i2p_topology_path": (
                "i2p-fronts/topology-final.json" if actual_i2p else None
            ),
            "actual_i2p_topology_sha256": (
                sha256(pair_root / "i2p-fronts/topology-final.json")
                if actual_i2p
                else None
            ),
            "actual_i2p_node_records_sha256": (
                i2p_topology_final.get("node_records_sha256", "")
                if actual_i2p
                else ""
            ),
            "actual_i2p_front_count": (
                i2p_topology_final.get("front_count", 0) if actual_i2p else 0
            ),
            "actual_i2p_router_restart_count": i2p_router_restart_count,
            "actual_i2p_front_restart_count": i2p_front_restart_count,
            "actual_i2p_fail_closed_loss": actual_i2p_fail_closed_loss,
            "actual_i2p_fail_closed_loss_path": (
                "actual-i2p-fail-closed-loss.json"
                if actual_i2p_loss
                else None
            ),
            "actual_i2p_fail_closed_loss_sha256": (
                sha256(pair_root / "actual-i2p-fail-closed-loss.json")
                if actual_i2p_loss
                else None
            ),
            "actual_tor_instance_count": len(tor_role_evidence),
            "actual_tor_node": (
                {
                    "address": tor_node["address"],
                    "port": tor_node["port"],
                    "public_key": tor_node["public_key"],
                }
                if tor_node is not None
                else None
            ),
            "actual_tor_binary_path": (
                tor_instances["client"]["tor_binary_path"]
                if actual_tor
                else None
            ),
            "actual_tor_sha256": (
                tor_instances["client"]["tor_sha256"] if actual_tor else None
            ),
            "actual_tor_version": (
                tor_instances["client"]["tor_version"] if actual_tor else None
            ),
            "actual_tor_role_evidence": tor_role_evidence,
            "actual_tor_process_loss": actual_tor_process_loss,
            "actual_tor_process_loss_path": (
                "actual-tor-process-loss.json"
                if actual_tor_process_fault
                else None
            ),
            "actual_tor_process_loss_sha256": (
                sha256(pair_root / "actual-tor-process-loss.json")
                if actual_tor_process_fault
                else None
            ),
            "actual_tor_ratox_churn": actual_tor_ratox_churn,
            "actual_tor_ratox_churn_path": (
                "actual-tor-ratox-churn.json"
                if actual_tor_ratox_soak
                else None
            ),
            "actual_tor_ratox_churn_sha256": (
                sha256(pair_root / "actual-tor-ratox-churn.json")
                if actual_tor_ratox_soak
                else None
            ),
            "actual_tor_adversarial_boundary": (
                actual_tor_adversarial_boundary
            ),
            "actual_tor_adversarial_boundary_path": (
                "actual-tor-adversarial-boundary.json"
                if actual_tor_ratox_adversary
                else None
            ),
            "actual_tor_adversarial_boundary_sha256": (
                sha256(pair_root / "actual-tor-adversarial-boundary.json")
                if actual_tor_ratox_adversary
                else None
            ),
            **payload_summary,
            **i2p_payload_summary,
            "sync_initial_pull_attempts": (
                client_sync["sync_initial_pull_attempts"]
                if scenario in SYNC_SCENARIOS
                else 0
            ),
            "sync_initial_pull_failures": (
                client_sync["sync_initial_pull_failures"]
                if scenario in SYNC_SCENARIOS
                else 0
            ),
            "sync_initial_pull_first_error_sha256": (
                client_sync["sync_initial_pull_first_error_sha256"]
                if scenario in SYNC_SCENARIOS
                else ""
            ),
            "route_packet_containment": capture_summaries,
            "private_route_mixed_context_role_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"]).get(
                            "private_route_mixed_context_observed"
                        )
                        is True
                    )
                    for role in ("client", "device")
                )
                if scenario in mixed_context_scenarios
                else 0
            ),
            "device_daemon_restart_count": device_daemon_restart_count,
            "link_interruption_count": link_interruption_count,
            "packet_loss_impairment_count": packet_loss_impairment_count,
            "packet_loss_percent": (
                PACKET_LOSS_PERCENT if scenario == "packet-loss" else 0
            ),
            "packet_loss_probe_count_per_role": (
                PACKET_LOSS_PROBE_COUNT if scenario == "packet-loss" else 0
            ),
            "packet_loss_qdiscs": packet_loss_qdiscs,
            "common_link_fairness_qdisc": common_link_fairness_qdisc,
            "ratox_route_impairment": ratox_route_impairment,
            "ratox_route_loss": ratox_route_loss,
            "device_guest_restart_count": device_guest_restart_count,
            "sync_client_daemon_restart_count": sync_client_daemon_restart_count,
            "mutable_profile_convergence": scenario in MUTABLE_SCENARIOS,
            "bidirectional_sync_convergence": (
                scenario in BIDIRECTIONAL_SYNC_SCENARIOS
            ),
            "bidirectional_sync_converged_role_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"])[
                            "sync_bidirectional_observed"
                        ]
                    )
                    for role in ("client", "device")
                )
                if scenario in BIDIRECTIONAL_SYNC_SCENARIOS
                else 0
            ),
            "automation_sync_convergence": (
                scenario in AUTOMATION_SYNC_SCENARIOS
            ),
            "automation_sync_converged_role_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"])[
                            "sync_automation_observed"
                        ]
                    )
                    for role in ("client", "device")
                )
                if scenario in AUTOMATION_SYNC_SCENARIOS
                else 0
            ),
            "mutable_authorized_role_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"])[
                            "mutable_authority_observed"
                        ]
                    )
                    for role in ("client", "device")
                )
                if scenario in MUTABLE_SCENARIOS
                else 0
            ),
            "mutable_converged_role_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"])[
                            "mutable_provider_converged"
                        ]
                    )
                    for role in ("client", "device")
                )
                if scenario in MUTABLE_SCENARIOS
                else 0
            ),
            "sync_unclean_stop_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"])[
                            "sync_unclean_stop_observed"
                        ]
                    )
                    for role in ("client", "device")
                )
                if scenario in SYNC_SCENARIOS
                else 0
            ),
            "sync_interrupted_staging_bytes": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_interrupted_staging_bytes"
                ]
                if scenario in SYNC_SCENARIOS
                else 0
            ),
            "sync_restart_prefix_resume_role_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"])[
                            "sync_restart_prefix_resume_observed"
                        ]
                    )
                    for role in ("client", "device")
                )
                if scenario == "sync-file-restart-resume"
                else 0
            ),
            "sync_restart_resumed_attempts": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_restart_resumed_attempts"
                ]
                if scenario == "sync-file-restart-resume"
                else 0
            ),
            "sync_restart_resumed_bytes": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_restart_resumed_bytes"
                ]
                if scenario == "sync-file-restart-resume"
                else 0
            ),
            "sync_range_restart_resume_role_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"])[
                            "sync_range_restart_resume_observed"
                        ]
                    )
                    for role in ("client", "device")
                )
                if scenario == "sync-file-range-restart-resume"
                else 0
            ),
            "sync_range_restart_interrupted_bytes": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_range_restart_interrupted_bytes"
                ]
                if scenario == "sync-file-range-restart-resume"
                else 0
            ),
            "sync_range_restart_retained_bytes": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_range_restart_retained_bytes"
                ]
                if scenario == "sync-file-range-restart-resume"
                else 0
            ),
            "sync_range_restart_resumed_attempts": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_range_restart_resumed_attempts"
                ]
                if scenario == "sync-file-range-restart-resume"
                else 0
            ),
            "sync_range_restart_resumed_bytes": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_range_restart_resumed_bytes"
                ]
                if scenario == "sync-file-range-restart-resume"
                else 0
            ),
            "sync_range_restart_suffix_bytes": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_range_restart_suffix_bytes"
                ]
                if scenario == "sync-file-range-restart-resume"
                else 0
            ),
            "sync_range_restart_first_job_id": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_range_restart_first_job_id"
                ]
                if scenario == "sync-file-range-restart-resume"
                else 0
            ),
            "sync_range_restart_second_job_id": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_range_restart_second_job_id"
                ]
                if scenario == "sync-file-range-restart-resume"
                else 0
            ),
            "sync_range_restart_first_attempt_id": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_range_restart_first_attempt_id"
                ]
                if scenario == "sync-file-range-restart-resume"
                else 0
            ),
            "sync_range_restart_second_attempt_id": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_range_restart_second_attempt_id"
                ]
                if scenario == "sync-file-range-restart-resume"
                else 0
            ),
            "sync_range_restart_first_message_id": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_range_restart_first_message_id"
                ]
                if scenario == "sync-file-range-restart-resume"
                else 0
            ),
            "sync_range_restart_second_message_id": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_range_restart_second_message_id"
                ]
                if scenario == "sync-file-range-restart-resume"
                else 0
            ),
            "sync_range_restart_first_file_id": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_range_restart_first_file_id"
                ]
                if scenario == "sync-file-range-restart-resume"
                else ""
            ),
            "sync_range_restart_second_file_id": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_range_restart_second_file_id"
                ]
                if scenario == "sync-file-range-restart-resume"
                else ""
            ),
            "sync_restart_recovered_role_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"])[
                            "sync_restart_recovery_observed"
                        ]
                    )
                    for role in ("client", "device")
                )
                if scenario in SYNC_SCENARIOS
                else 0
            ),
            "sync_disconnect_recovered_role_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"])[
                            "sync_disconnect_retry_observed"
                        ]
                    )
                    for role in ("client", "device")
                )
                if scenario == "sync-file-disconnect"
                else 0
            ),
            "sync_disconnect_staging_bytes": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_disconnect_staging_bytes"
                ]
                if scenario == "sync-file-disconnect"
                else 0
            ),
            "sync_disconnect_minimum_stable_samples": (
                min(
                    load(pair_root / receipts[role]["path"])[
                        "sync_disconnect_stable_samples"
                    ]
                    for role in ("client", "device")
                )
                if scenario == "sync-file-disconnect"
                else 0
            ),
            "sync_guest_restart_recovered_role_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"])[
                            "sync_guest_restart_retry_observed"
                        ]
                    )
                    for role in ("client", "device")
                )
                if scenario == "sync-file-guest-restart"
                else 0
            ),
            "sync_guest_restart_staging_bytes": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_guest_restart_staging_bytes"
                ]
                if scenario == "sync-file-guest-restart"
                else 0
            ),
            "sync_guest_restart_minimum_stable_samples": (
                min(
                    load(pair_root / receipts[role]["path"])[
                        "sync_guest_restart_stable_samples"
                    ]
                    for role in ("client", "device")
                )
                if scenario == "sync-file-guest-restart"
                else 0
            ),
            "sync_pause_observed_role_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"])[
                            "sync_pause_observed"
                        ]
                    )
                    for role in ("client", "device")
                )
                if scenario == "sync-file-pause"
                else 0
            ),
            "sync_pause_position_bytes": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_pause_position_bytes"
                ]
                if scenario == "sync-file-pause"
                else 0
            ),
            "sync_pause_minimum_stable_samples": (
                min(
                    load(pair_root / receipts[role]["path"])[
                        "sync_pause_stable_samples"
                    ]
                    for role in ("client", "device")
                )
                if scenario == "sync-file-pause"
                else 0
            ),
            "sync_pause_file_id": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_pause_file_id"
                ]
                if scenario == "sync-file-pause"
                else ""
            ),
            "sync_file_convergence": (
                scenario in SYNC_SCENARIOS
                and scenario not in SYNC_CANCELLATION_SCENARIOS
            ),
            "sync_repeated_route_loss_initial_rate_kbit": (
                256
                if scenario in REPEATED_RANGE_LOSS_COUNTS
                else 0
            ),
            "sync_range_route_loss_threshold_bytes": (
                983_040
                if scenario == "sync-file-range-late-route-loss"
                else 262_144
                if scenario in {
                    "sync-file-range-route-loss",
                    "sync-file-range-repeated-route-loss",
                    "sync-file-range-triple-route-loss",
                }
                else 0
            ),
            "sync_range_route_loss_rate_kbit": (
                256
                if scenario in {
                    "sync-file-range-late-route-loss",
                    "sync-file-range-repeated-route-loss",
                    "sync-file-range-triple-route-loss",
                }
                else 0
            ),
            "sync_qualification_deferred_frames": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_qualification_deferred_frames"
                ]
                if scenario in SYNC_SCENARIOS
                else 0
            ),
            "sync_qualification_deferred_frame_releases": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_qualification_deferred_frame_releases"
                ]
                if scenario in SYNC_SCENARIOS
                else 0
            ),
            "signed_update_observed_role_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"])[
                            "signed_update_observed"
                        ]
                    )
                    for role in ("client", "device")
                )
                if scenario in SIGNED_UPDATE_SCENARIOS
                else 0
            ),
            "signed_update_release_sequence": (
                load(pair_root / receipts["client"]["path"])[
                    "signed_update_release_sequence"
                ]
                if scenario in SIGNED_UPDATE_SCENARIOS
                else 0
            ),
            "signed_update_payload_sha256": (
                load(pair_root / receipts["client"]["path"])[
                    "signed_update_payload_sha256"
                ]
                if scenario in SIGNED_UPDATE_SCENARIOS
                else ""
            ),
            "signed_update_manifest_record": (
                load(pair_root / receipts["client"]["path"])[
                    "signed_update_manifest_record"
                ]
                if scenario in SIGNED_UPDATE_SCENARIOS
                else ""
            ),
            "signed_update_confirmed_role_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"])[
                            "signed_update_confirmed"
                        ]
                    )
                    for role in ("client", "device")
                )
                if scenario in SIGNED_UPDATE_SCENARIOS
                else 0
            ),
            "signed_update_restart_count": (
                load(pair_root / receipts["client"]["path"])[
                    "signed_update_restart_count"
                ]
                if scenario in SIGNED_UPDATE_SCENARIOS
                else 0
            ),
            "signed_update_feature_advertised_role_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"])[
                            "signed_update_feature_advertised"
                        ]
                    )
                    for role in ("client", "device")
                )
                if scenario in SIGNED_UPDATE_SCENARIOS
                else 0
            ),
            "signed_update_remote_stage_observed_role_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"])[
                            "signed_update_remote_stage_observed"
                        ]
                    )
                    for role in ("client", "device")
                )
                if scenario in SIGNED_UPDATE_SCENARIOS
                else 0
            ),
            "signed_update_sender_epoch": (
                load(pair_root / receipts["client"]["path"])[
                    "signed_update_sender_epoch"
                ]
                if scenario in SIGNED_UPDATE_SCENARIOS
                else 0
            ),
            "signed_update_message_id": (
                load(pair_root / receipts["client"]["path"])[
                    "signed_update_message_id"
                ]
                if scenario in SIGNED_UPDATE_SCENARIOS
                else 0
            ),
            "sync_cancellation": scenario in SYNC_CANCELLATION_SCENARIOS,
            "sync_cancelled_staging_bytes": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_cancelled_staging_bytes"
                ]
                if scenario in SYNC_CANCELLATION_SCENARIOS
                else 0
            ),
            "sync_cancelled_receive_count": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_cancelled_receive_count"
                ]
                if scenario in SYNC_CANCELLATION_SCENARIOS
                else 0
            ),
            "sync_generation": (
                load(pair_root / receipts["client"]["path"])["sync_generation"]
                if scenario in SYNC_SCENARIOS
                else 0
            ),
            "multi_source_count": (
                load(pair_root / receipts["client"]["path"])[
                    "multi_source_count"
                ]
                if scenario in CONTENT_MULTI_SOURCE_SCENARIOS
                else 0
            ),
            "multi_source_availability_requests": (
                load(pair_root / receipts["client"]["path"])[
                    "multi_source_availability_requests"
                ]
                if scenario in CONTENT_MULTI_SOURCE_SCENARIOS
                else 0
            ),
            "multi_source_availability_results": (
                load(pair_root / receipts["client"]["path"])[
                    "multi_source_availability_results"
                ]
                if scenario in CONTENT_MULTI_SOURCE_SCENARIOS
                else 0
            ),
            "multi_source_primary_objects": (
                load(pair_root / receipts["device"]["path"])[
                    "multi_source_primary_objects"
                ]
                if scenario in CONTENT_MULTI_SOURCE_SCENARIOS
                else 0
            ),
            "multi_source_secondary_objects": (
                load(pair_root / receipts["device"]["path"])[
                    "multi_source_secondary_objects"
                ]
                if scenario in CONTENT_MULTI_SOURCE_SCENARIOS
                else 0
            ),
            "multi_source_atomic_pull_role_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"])[
                            "multi_source_atomic_pull_observed"
                        ]
                    )
                    for role in ("client", "device")
                )
                if scenario in CONTENT_MULTI_SOURCE_SCENARIOS
                else 0
            ),
            "multi_source_auxiliary_carrier_count": (
                load(pair_root / receipts["client"]["path"])[
                    "multi_source_auxiliary_carrier_count"
                ]
                if scenario in {
                    "sync-content-multi-route-actual-tor",
                    "sync-content-multi-route-actual-tor-loss",
                }
                else 0
            ),
            "multi_source_auxiliary_carriers_sha256": (
                load(pair_root / receipts["client"]["path"])[
                    "multi_source_auxiliary_carriers_sha256"
                ]
                if scenario in {
                    "sync-content-multi-route-actual-tor",
                    "sync-content-multi-route-actual-tor-loss",
                }
                else ""
            ),
            "multi_source_secondary_key_sha256": (
                load(pair_root / receipts["client"]["path"])[
                    "multi_source_secondary_key_sha256"
                ]
                if scenario in CONTENT_MULTI_SOURCE_SCENARIOS
                else ""
            ),
            "multi_source_secondary_principal_sha256": (
                load(pair_root / receipts["client"]["path"])[
                    "multi_source_secondary_principal_sha256"
                ]
                if scenario in CONTENT_MULTI_SOURCE_SCENARIOS
                else ""
            ),
            "multi_source_tcp_relay_count": (
                2
                if scenario in CONTENT_MULTI_SOURCE_SCENARIOS
                and route == "forced-tcp"
                else 0
            ),
            "multi_source_secondary_bootstrap_key_sha256": (
                hashlib.sha256(
                    secondary_bootstrap_key.encode("ascii")
                ).hexdigest()
                if secondary_bootstrap_key
                else ""
            ),
            "multi_source_loss_observed_role_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"])[
                            "multi_source_loss_observed"
                        ]
                    )
                    for role in ("client", "device")
                )
                if scenario in CONTENT_MULTI_SOURCE_LOSS_SCENARIOS
                else 0
            ),
            "multi_source_loss_recovery_role_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"])[
                            "multi_source_loss_recovery_observed"
                        ]
                    )
                    for role in ("client", "device")
                )
                if scenario in CONTENT_MULTI_SOURCE_LOSS_SCENARIOS
                else 0
            ),
            "multi_source_loss_first_job_id": (
                load(pair_root / receipts["client"]["path"])[
                    "multi_source_loss_first_job_id"
                ]
                if scenario in CONTENT_MULTI_SOURCE_LOSS_SCENARIOS
                else 0
            ),
            "multi_source_loss_replacement_job_id": (
                load(pair_root / receipts["client"]["path"])[
                    "multi_source_loss_replacement_job_id"
                ]
                if scenario in CONTENT_MULTI_SOURCE_LOSS_SCENARIOS
                else 0
            ),
            "multi_source_loss_committed_objects": (
                load(pair_root / receipts["client"]["path"])[
                    "multi_source_loss_committed_objects"
                ]
                if scenario in CONTENT_MULTI_SOURCE_LOSS_SCENARIOS
                else 0
            ),
            "multi_source_loss_fetched_bytes": (
                load(pair_root / receipts["client"]["path"])[
                    "multi_source_loss_fetched_bytes"
                ]
                if scenario in CONTENT_MULTI_SOURCE_LOSS_SCENARIOS
                else 0
            ),
            "multi_source_loss_initial_epoch": (
                load(pair_root / receipts["client"]["path"])[
                    "multi_source_loss_initial_epoch"
                ]
                if scenario in CONTENT_MULTI_SOURCE_LOSS_SCENARIOS
                else 0
            ),
            "multi_source_loss_recovered_epoch": (
                load(pair_root / receipts["client"]["path"])[
                    "multi_source_loss_recovered_epoch"
                ]
                if scenario in CONTENT_MULTI_SOURCE_LOSS_SCENARIOS
                else 0
            ),
            "multi_source_loss_restart_count": (
                load(pair_root / receipts["client"]["path"])[
                    "multi_source_loss_restart_count"
                ]
                if scenario in CONTENT_MULTI_SOURCE_LOSS_SCENARIOS
                else 0
            ),
            "multi_source_loss_secondary_requests_before_stop": (
                multi_source_loss_secondary_requests_before_stop
                if scenario in CONTENT_MULTI_SOURCE_LOSS_SCENARIOS
                else 0
            ),
            "multi_source_loss_constructed_replica_head_reinjected": (
                multi_source_loss_constructed_replica_head_reinjected
                if scenario in CONTENT_MULTI_SOURCE_LOSS_SCENARIOS
                else False
            ),
            "multi_source_loss_durable_replica_cold_start": (
                multi_source_loss_durable_replica_cold_start
                if scenario in CONTENT_MULTI_SOURCE_LOSS_SCENARIOS
                else False
            ),
            "multi_source_loss_staging_clean_role_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"])[
                            "multi_source_loss_staging_clean"
                        ]
                    )
                    for role in ("client", "device")
                )
                if scenario in CONTENT_MULTI_SOURCE_LOSS_SCENARIOS
                else 0
            ),
            "multi_source_loss_head_fenced_role_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"])[
                            "multi_source_loss_head_fenced"
                        ]
                    )
                    for role in ("client", "device")
                )
                if scenario in CONTENT_MULTI_SOURCE_LOSS_SCENARIOS
                else 0
            ),
            "multi_source_loss_activation_fenced_role_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"])[
                            "multi_source_loss_activation_fenced"
                        ]
                    )
                    for role in ("client", "device")
                )
                if scenario in CONTENT_MULTI_SOURCE_LOSS_SCENARIOS
                else 0
            ),
            "multi_source_route_loss_observed_role_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"])[
                            "multi_source_route_loss_observed"
                        ]
                    )
                    for role in ("client", "device")
                )
                if scenario == "sync-content-multi-route-actual-tor-loss"
                else 0
            ),
            **(
                {
                    field: load(pair_root / receipts["client"]["path"])[field]
                    for field in (
                        "multi_source_route_loss_target",
                        "multi_source_route_loss_fault_worker",
                        "multi_source_route_loss_recovered_worker",
                        "multi_source_route_loss_position_bytes",
                        "multi_source_route_loss_carrier_losses",
                        "multi_source_route_loss_reassignments",
                        "multi_source_route_loss_recoveries",
                        "multi_source_route_loss_primary_epoch",
                        "multi_source_route_loss_secondary_epoch",
                    )
                }
                if scenario == "sync-content-multi-route-actual-tor-loss"
                else {
                    "multi_source_route_loss_target": "",
                    "multi_source_route_loss_fault_worker": 0,
                    "multi_source_route_loss_recovered_worker": 0,
                    "multi_source_route_loss_position_bytes": 0,
                    "multi_source_route_loss_carrier_losses": 0,
                    "multi_source_route_loss_reassignments": 0,
                    "multi_source_route_loss_recoveries": 0,
                    "multi_source_route_loss_primary_epoch": 0,
                    "multi_source_route_loss_secondary_epoch": 0,
                }
            ),
            "sync_tree_observed_role_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"])[
                            "sync_tree_observed"
                        ]
                    )
                    for role in ("client", "device")
                )
                if scenario in SYNC_TREE_SCENARIOS
                else 0
            ),
            "sync_tree_admission_observed_role_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"])[
                            "sync_tree_admission_observed"
                        ]
                    )
                    for role in ("client", "device")
                )
                if scenario == "sync-tree-admission"
                else 0
            ),
            "sync_tree_admission_receive_limit": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_admission_receive_limit"
                ]
                if scenario == "sync-tree-admission"
                else 0
            ),
            "sync_tree_admission_retry_count": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_admission_retry_count"
                ]
                if scenario == "sync-tree-admission"
                else 0
            ),
            "sync_tree_admission_admitted_offers": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_admission_admitted_offers"
                ]
                if scenario == "sync-tree-admission"
                else 0
            ),
            "sync_tree_admission_pending_offers": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_admission_pending_offers"
                ]
                if scenario == "sync-tree-admission"
                else 0
            ),
            "sync_tree_route_loss_observed": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_loss_observed"
                ]
                if scenario in SYNC_ROUTE_LOSS_SCENARIOS
                else False
            ),
            "sync_tree_route_loss_position_bytes": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_loss_position_bytes"
                ]
                if scenario in SYNC_ROUTE_LOSS_SCENARIOS
                else 0
            ),
            "sync_tree_route_resume_observed": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_resume_observed"
                ]
                if scenario
                in {
                    "sync-tree-route-loss",
                    "sync-tree-route-private-actual-tor-loss",
                    "sync-file-range-route-loss",
                    "sync-file-range-late-route-loss",
                    "sync-file-range-repeated-route-loss",
                    "sync-file-range-triple-route-loss",
                }
                else False
            ),
            "sync_tree_route_loss_retained_partials": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_loss_retained_partials"
                ]
                if scenario
                in {
                    "sync-tree-route-loss",
                    "sync-tree-route-private-actual-tor-loss",
                    "sync-file-range-route-loss",
                    "sync-file-range-late-route-loss",
                    "sync-file-range-repeated-route-loss",
                    "sync-file-range-triple-route-loss",
                }
                else 0
            ),
            "sync_tree_route_loss_retained_attempts": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_loss_retained_attempts"
                ]
                if scenario
                in {
                    "sync-tree-route-loss",
                    "sync-tree-route-private-actual-tor-loss",
                    "sync-file-range-route-loss",
                    "sync-file-range-late-route-loss",
                    "sync-file-range-repeated-route-loss",
                    "sync-file-range-triple-route-loss",
                }
                else 0
            ),
            "sync_tree_route_loss_retained_bytes": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_loss_retained_bytes"
                ]
                if scenario
                in {
                    "sync-tree-route-loss",
                    "sync-tree-route-private-actual-tor-loss",
                    "sync-file-range-route-loss",
                    "sync-file-range-late-route-loss",
                    "sync-file-range-repeated-route-loss",
                    "sync-file-range-triple-route-loss",
                }
                else 0
            ),
            "sync_tree_route_loss_retention_fallbacks": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_loss_retention_fallbacks"
                ]
                if scenario
                in {
                    "sync-tree-route-loss",
                    "sync-tree-route-private-actual-tor-loss",
                    "sync-file-range-route-loss",
                    "sync-file-range-late-route-loss",
                    "sync-file-range-repeated-route-loss",
                    "sync-file-range-triple-route-loss",
                }
                else 0
            ),
            "sync_tree_route_loss_resumed_attempts": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_loss_resumed_attempts"
                ]
                if scenario
                in {
                    "sync-tree-route-loss",
                    "sync-tree-route-private-actual-tor-loss",
                    "sync-file-range-route-loss",
                    "sync-file-range-late-route-loss",
                    "sync-file-range-repeated-route-loss",
                    "sync-file-range-triple-route-loss",
                }
                else 0
            ),
            "sync_tree_route_loss_resumed_bytes": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_loss_resumed_bytes"
                ]
                if scenario
                in {
                    "sync-tree-route-loss",
                    "sync-tree-route-private-actual-tor-loss",
                    "sync-file-range-route-loss",
                    "sync-file-range-late-route-loss",
                    "sync-file-range-repeated-route-loss",
                    "sync-file-range-triple-route-loss",
                }
                else 0
            ),
            "sync_tree_route_loss_carrier_losses": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_loss_carrier_losses"
                ]
                if scenario in SYNC_ROUTE_LOSS_SCENARIOS
                else 0
            ),
            "sync_tree_route_loss_reassignments": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_loss_reassignments"
                ]
                if scenario in SYNC_ROUTE_LOSS_SCENARIOS
                else 0
            ),
            "sync_tree_route_loss_stale_terminals": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_loss_stale_terminals"
                ]
                if scenario in SYNC_ROUTE_LOSS_SCENARIOS
                else 0
            ),
            "sync_tree_route_loss_recoveries": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_loss_recoveries"
                ]
                if scenario in SYNC_ROUTE_LOSS_SCENARIOS
                else 0
            ),
            "sync_tree_route_cancel_loss_observed": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_cancel_loss_observed"
                ]
                if scenario == "sync-tree-route-cancel-loss"
                else False
            ),
            "sync_tree_route_cancel_race_observed": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_cancel_race_observed"
                ]
                if scenario in SYNC_ROUTE_CANCEL_RACE_SCENARIOS
                else False
            ),
            "sync_tree_route_cancel_race_outcome": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_cancel_race_outcome"
                ]
                if scenario in SYNC_ROUTE_CANCEL_RACE_SCENARIOS
                else ""
            ),
            "sync_tree_route_cancel_race_fault_delay_ms": (
                SYNC_ROUTE_CANCEL_RACE_SCENARIOS.get(
                    scenario, (0, 0, None)
                )[0]
            ),
            "sync_tree_route_cancel_race_cancel_delay_ms": (
                SYNC_ROUTE_CANCEL_RACE_SCENARIOS.get(
                    scenario, (0, 0, None)
                )[1]
            ),
            "sync_tree_route_cancel_race_cleanup_retries": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_cancel_race_cleanup_retries"
                ]
                if scenario in SYNC_ROUTE_CANCEL_RACE_SCENARIOS
                else 0
            ),
            "sync_tree_route_ready_role_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"])[
                            "sync_tree_route_ready_bulk"
                        ] == 2
                    )
                    for role in ("client", "device")
                )
                if scenario in MULTI_ROUTE_SYNC_SCENARIOS
                else 0
            ),
            "signed_route_network_class_role_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"]).get(
                            "signed_route_network_classes_observed", False
                        )
                    )
                    for role in ("client", "device")
                )
                if scenario in MULTI_ROUTE_SYNC_SCENARIOS
                else 0
            ),
            "sync_tree_route_startup_order_observed_role_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"])[
                            "sync_tree_route_startup_order_observed"
                        ]
                    )
                    for role in ("client", "device")
                )
                if scenario == "sync-tree-route-startup-order"
                else 0
            ),
            "sync_tree_route_startup_delay_ms": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_startup_delay_ms"
                ]
                if scenario == "sync-tree-route-startup-order"
                else 0
            ),
            "sync_tree_route_startup_restart_count": (
                sum(
                    load(pair_root / receipts[role]["path"])[
                        "sync_tree_route_startup_restart_count"
                    ]
                    for role in ("client", "device")
                )
                if scenario == "sync-tree-route-startup-order"
                else 0
            ),
            "sync_tree_route_startup_minimum_stable_samples": (
                min(
                    load(pair_root / receipts[role]["path"])[field]
                    for role in ("client", "device")
                    for field in (
                        "sync_tree_route_startup_phase_one_stable_samples",
                        "sync_tree_route_startup_phase_two_stable_samples",
                    )
                )
                if scenario == "sync-tree-route-startup-order"
                else 0
            ),
            "sync_tree_route_startup_maximum_observation_ms": (
                max(
                    load(pair_root / receipts[role]["path"])[field]
                    for role in ("client", "device")
                    for field in (
                        "sync_tree_route_startup_phase_one_ms",
                        "sync_tree_route_startup_phase_two_ms",
                    )
                )
                if scenario == "sync-tree-route-startup-order"
                else 0
            ),
            "sync_tree_route_balance_observed": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_balance_observed"
                ]
                if scenario == "sync-tree-route-balance"
                else False
            ),
            "sync_tree_route_balance_fixed_same_carrier": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_balance_fixed_same_carrier"
                ]
                if scenario == "sync-tree-route-balance"
                else False
            ),
            "sync_tree_route_balance_adaptive_distinct_carriers": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_balance_adaptive_distinct_carriers"
                ]
                if scenario == "sync-tree-route-balance"
                else False
            ),
            "sync_tree_route_balance_fixed_carrier_a": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_balance_fixed_carrier_a"
                ]
                if scenario == "sync-tree-route-balance"
                else ""
            ),
            "sync_tree_route_balance_fixed_carrier_b": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_balance_fixed_carrier_b"
                ]
                if scenario == "sync-tree-route-balance"
                else ""
            ),
            "sync_tree_route_balance_adaptive_carrier_a": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_balance_adaptive_carrier_a"
                ]
                if scenario == "sync-tree-route-balance"
                else ""
            ),
            "sync_tree_route_balance_adaptive_carrier_b": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_balance_adaptive_carrier_b"
                ]
                if scenario == "sync-tree-route-balance"
                else ""
            ),
            "sync_tree_route_balance_fixed_selections": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_balance_fixed_selections"
                ]
                if scenario == "sync-tree-route-balance"
                else 0
            ),
            "sync_tree_route_balance_adaptive_selections": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_balance_adaptive_selections"
                ]
                if scenario == "sync-tree-route-balance"
                else 0
            ),
            "sync_tree_route_balance_fixed_duration_ms": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_balance_fixed_duration_ms"
                ]
                if scenario == "sync-tree-route-balance"
                else 0
            ),
            "sync_tree_route_balance_adaptive_duration_ms": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_balance_adaptive_duration_ms"
                ]
                if scenario == "sync-tree-route-balance"
                else 0
            ),
            "sync_tree_route_balance_activations": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_balance_activations"
                ]
                if scenario == "sync-tree-route-balance"
                else 0
            ),
            "sync_tree_route_balance_artifact_bytes": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_balance_artifact_bytes"
                ]
                if scenario == "sync-tree-route-balance"
                else 0
            ),
            "sync_tree_route_balance_fixed_head_retries": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_balance_fixed_head_retries"
                ]
                if scenario == "sync-tree-route-balance"
                else 0
            ),
            "sync_tree_route_balance_adaptive_head_retries": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_balance_adaptive_head_retries"
                ]
                if scenario == "sync-tree-route-balance"
                else 0
            ),
            "sync_tree_route_balance_phase_order": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_balance_phase_order"
                ]
                if scenario == "sync-tree-route-balance"
                else ""
            ),
            "sync_tree_route_population_observed": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_population_observed"
                ]
                if scenario == "sync-tree-route-population"
                else False
            ),
            "sync_tree_route_population_jobs": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_population_jobs"
                ]
                if scenario == "sync-tree-route-population"
                else 0
            ),
            "sync_tree_route_population_artifact_bytes": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_population_artifact_bytes"
                ]
                if scenario == "sync-tree-route-population"
                else 0
            ),
            "sync_tree_route_population_fixed_pattern": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_population_fixed_pattern"
                ]
                if scenario == "sync-tree-route-population"
                else ""
            ),
            "sync_tree_route_population_adaptive_pattern": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_population_adaptive_pattern"
                ]
                if scenario == "sync-tree-route-population"
                else ""
            ),
            "sync_tree_route_population_fixed_max_prefix_imbalance": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_population_fixed_max_prefix_imbalance"
                ]
                if scenario == "sync-tree-route-population"
                else 0
            ),
            "sync_tree_route_population_adaptive_max_prefix_imbalance": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_population_adaptive_max_prefix_imbalance"
                ]
                if scenario == "sync-tree-route-population"
                else 0
            ),
            "sync_tree_route_population_fixed_progress_jobs": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_population_fixed_progress_jobs"
                ]
                if scenario == "sync-tree-route-population"
                else 0
            ),
            "sync_tree_route_population_adaptive_progress_jobs": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_population_adaptive_progress_jobs"
                ]
                if scenario == "sync-tree-route-population"
                else 0
            ),
            "sync_tree_route_population_fixed_progress_observation_spread_ms": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_population_fixed_progress_observation_spread_ms"
                ]
                if scenario == "sync-tree-route-population"
                else 0
            ),
            "sync_tree_route_population_adaptive_progress_observation_spread_ms": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_population_adaptive_progress_observation_spread_ms"
                ]
                if scenario == "sync-tree-route-population"
                else 0
            ),
            "sync_tree_route_population_fixed_duration_ms": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_population_fixed_duration_ms"
                ]
                if scenario == "sync-tree-route-population"
                else 0
            ),
            "sync_tree_route_population_adaptive_duration_ms": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_population_adaptive_duration_ms"
                ]
                if scenario == "sync-tree-route-population"
                else 0
            ),
            "sync_tree_route_population_activations": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_population_activations"
                ]
                if scenario == "sync-tree-route-population"
                else 0
            ),
            "sync_tree_route_population_fixed_resource_sha256": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_population_fixed_resource_sha256"
                ]
                if scenario == "sync-tree-route-population"
                else ""
            ),
            "sync_tree_route_population_adaptive_resource_sha256": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_population_adaptive_resource_sha256"
                ]
                if scenario == "sync-tree-route-population"
                else ""
            ),
            "sync_tree_route_concurrent_cancel_observed_role_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"])[
                            "sync_tree_route_concurrent_cancel_observed"
                        ]
                    )
                    for role in ("client", "device")
                )
                if scenario in SYNC_CONCURRENT_CANCEL_SCENARIOS
                else 0
            ),
            **{
                field: (
                    load(pair_root / receipts["client"]["path"])[field]
                    if scenario in SYNC_CONCURRENT_CANCEL_SCENARIOS
                    else default
                )
                for field, default in {
                    "sync_tree_route_concurrent_cancel_jobs": 0,
                    "sync_tree_route_concurrent_cancel_artifact_bytes": 0,
                    "sync_tree_route_concurrent_cancel_requested": 0,
                    "sync_tree_route_concurrent_cancel_completed": 0,
                    "sync_tree_route_concurrent_cancel_survivors": 0,
                    "sync_tree_route_concurrent_cancel_survivor_activations": 0,
                    "sync_tree_route_concurrent_cancel_pattern": "",
                    "sync_tree_route_concurrent_cancel_route_zero": 0,
                    "sync_tree_route_concurrent_cancel_route_one": 0,
                    "sync_tree_route_concurrent_cancel_tail_ms": 0,
                    "sync_tree_route_concurrent_cancel_work_before": 0,
                    "sync_tree_route_concurrent_cancel_work_after": 0,
                    "sync_tree_route_concurrent_cancel_reassignments_delta": 0,
                    "sync_tree_route_concurrent_cancel_adaptive_selections": 0,
                    "sync_tree_route_concurrent_cancel_resource_sha256": "",
                }.items()
            },
            "sync_tree_route_population_loss_observed_role_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"])[
                            "sync_tree_route_population_loss_observed"
                        ]
                    )
                    for role in ("client", "device")
                )
                if scenario in {
                    "sync-tree-route-population-loss",
                    "sync-tree-route-loss-admission",
                }
                else 0
            ),
            **{
                field: (
                    load(pair_root / receipts["client"]["path"])[field]
                    if scenario in {
                        "sync-tree-route-population-loss",
                        "sync-tree-route-loss-admission",
                    }
                    else default
                )
                for field, default in {
                    "sync_tree_route_population_loss_jobs": 0,
                    "sync_tree_route_population_loss_artifact_bytes": 0,
                    "sync_tree_route_population_loss_pattern": "",
                    "sync_tree_route_population_loss_affected_jobs": 0,
                    "sync_tree_route_population_loss_carrier_losses": 0,
                    "sync_tree_route_population_loss_reassignments": 0,
                    "sync_tree_route_population_loss_stale_terminals": 0,
                    "sync_tree_route_population_loss_recoveries": 0,
                    "sync_tree_route_population_loss_fixed_selections": 0,
                    "sync_tree_route_population_loss_activations": 0,
                    "sync_tree_route_population_loss_work_before": 0,
                    "sync_tree_route_population_loss_work_after": 0,
                    "sync_tree_route_population_loss_fault_delay_ms": 0,
                    "sync_tree_route_population_loss_fault_position_bytes": 0,
                    "sync_tree_route_population_loss_duration_ms": 0,
                    "sync_tree_route_population_loss_stopped_carrier": "",
                    "sync_tree_route_population_loss_resource_sha256": "",
                    "sync_tree_route_loss_admission_started_jobs": 0,
                    "sync_tree_route_loss_admission_ready_bulk": 0,
                    "sync_tree_route_loss_admission_surviving_carrier": "",
                }.items()
            },
            "sync_tree_route_startup_admission_observed_role_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"])[
                            "sync_tree_route_startup_admission_observed"
                        ]
                    )
                    for role in ("client", "device")
                )
                if scenario == "sync-tree-route-startup-admission"
                else 0
            ),
            **{
                field: (
                    load(pair_root / receipts["client"]["path"])[field]
                    if scenario == "sync-tree-route-startup-admission"
                    else default
                )
                for field, default in {
                    "sync_tree_route_startup_admission_jobs": 0,
                    "sync_tree_route_startup_admission_artifact_bytes": 0,
                    "sync_tree_route_startup_admission_delay_ms": 0,
                    "sync_tree_route_startup_admission_restart_count": 0,
                    "sync_tree_route_startup_admission_ready_bulk_before": 0,
                    "sync_tree_route_startup_admission_ready_bulk_after": 0,
                    "sync_tree_route_startup_admission_stable_samples": 0,
                    "sync_tree_route_startup_admission_carrier": "",
                    "sync_tree_route_startup_admission_live_jobs_after_join": 0,
                    "sync_tree_route_startup_admission_preserved_carriers": 0,
                    "sync_tree_route_startup_admission_adaptive_selections": 0,
                    "sync_tree_route_startup_admission_activations": 0,
                    "sync_tree_route_startup_admission_work_before": 0,
                    "sync_tree_route_startup_admission_work_after": 0,
                    "sync_tree_route_startup_admission_duration_ms": 0,
                    "sync_tree_route_startup_admission_resource_sha256": "",
                }.items()
            },
            "sync_tree_route_throughput_observed_role_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"])[
                            "sync_tree_route_throughput_observed"
                        ]
                    )
                    for role in ("client", "device")
                )
                if scenario == "sync-tree-route-throughput"
                else 0
            ),
            **{
                field: (
                    load(pair_root / receipts["client"]["path"])[field]
                    if scenario == "sync-tree-route-throughput"
                    else default
                )
                for field, default in {
                    "sync_tree_route_throughput_jobs_per_phase": 0,
                    "sync_tree_route_throughput_phases": 0,
                    "sync_tree_route_throughput_artifact_bytes": 0,
                    "sync_tree_route_throughput_phase_order": "",
                    "sync_tree_route_throughput_restart_count": 0,
                    "sync_tree_route_throughput_restart_hold_ms": 0,
                    "sync_tree_route_throughput_fixed_patterns": "",
                    "sync_tree_route_throughput_adaptive_patterns": "",
                    "sync_tree_route_throughput_fixed_a_duration_ms": 0,
                    "sync_tree_route_throughput_adaptive_a_duration_ms": 0,
                    "sync_tree_route_throughput_adaptive_b_duration_ms": 0,
                    "sync_tree_route_throughput_fixed_b_duration_ms": 0,
                    "sync_tree_route_throughput_fixed_a_completion_skew_ms": 0,
                    "sync_tree_route_throughput_adaptive_a_completion_skew_ms": 0,
                    "sync_tree_route_throughput_adaptive_b_completion_skew_ms": 0,
                    "sync_tree_route_throughput_fixed_b_completion_skew_ms": 0,
                    "sync_tree_route_throughput_fixed_total_duration_ms": 0,
                    "sync_tree_route_throughput_adaptive_total_duration_ms": 0,
                    "sync_tree_route_throughput_fixed_artifact_bps": 0,
                    "sync_tree_route_throughput_adaptive_artifact_bps": 0,
                    "sync_tree_route_throughput_adaptive_speedup_ppm": 0,
                    "sync_tree_route_throughput_fixed_selections": 0,
                    "sync_tree_route_throughput_adaptive_selections": 0,
                    "sync_tree_route_throughput_reassignments": 0,
                    "sync_tree_route_throughput_activations": 0,
                    "sync_tree_route_throughput_peak_work": 0,
                    "sync_tree_route_throughput_work_after": 0,
                    "sync_tree_route_throughput_fixed_a_resource_sha256": "",
                    "sync_tree_route_throughput_adaptive_a_resource_sha256": "",
                    "sync_tree_route_throughput_adaptive_b_resource_sha256": "",
                    "sync_tree_route_throughput_fixed_b_resource_sha256": "",
                }.items()
            },
            "sync_tree_route_cancel_observed_role_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"])[
                            "sync_tree_route_cancel_observed"
                        ]
                    )
                    for role in ("client", "device")
                )
                if scenario in {
                    "sync-tree-route-cancel",
                    "sync-tree-route-loss-cancel",
                    "sync-tree-route-cancel-loss",
                    "sync-tree-route-cancel-race",
                    "sync-tree-route-cancel-race-loss-first",
                }
                else 0
            ),
            "sync_tree_route_cancel_carrier": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_cancel_carrier"
                ]
                if scenario in {
                    "sync-tree-route-cancel",
                    "sync-tree-route-loss-cancel",
                    "sync-tree-route-cancel-loss",
                    "sync-tree-route-cancel-race",
                    "sync-tree-route-cancel-race-loss-first",
                }
                else ""
            ),
            "sync_tree_route_cancel_worker_id": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_cancel_worker_id"
                ]
                if scenario in {
                    "sync-tree-route-cancel",
                    "sync-tree-route-loss-cancel",
                    "sync-tree-route-cancel-loss",
                    "sync-tree-route-cancel-race",
                    "sync-tree-route-cancel-race-loss-first",
                }
                else 0
            ),
            "sync_tree_route_cancel_tail_ms": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_cancel_tail_ms"
                ]
                if scenario in {
                    "sync-tree-route-cancel",
                    "sync-tree-route-loss-cancel",
                    "sync-tree-route-cancel-loss",
                    "sync-tree-route-cancel-race",
                    "sync-tree-route-cancel-race-loss-first",
                }
                else 0
            ),
            "sync_tree_route_cancel_work_before": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_cancel_work_before"
                ]
                if scenario in {
                    "sync-tree-route-cancel",
                    "sync-tree-route-loss-cancel",
                    "sync-tree-route-cancel-loss",
                    "sync-tree-route-cancel-race",
                    "sync-tree-route-cancel-race-loss-first",
                }
                else 0
            ),
            "sync_tree_route_cancel_work_after": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_cancel_work_after"
                ]
                if scenario in {
                    "sync-tree-route-cancel",
                    "sync-tree-route-loss-cancel",
                    "sync-tree-route-cancel-loss",
                    "sync-tree-route-cancel-race",
                    "sync-tree-route-cancel-race-loss-first",
                }
                else 0
            ),
            "sync_tree_route_cancel_reassignments_delta": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_cancel_reassignments_delta"
                ]
                if scenario in {
                    "sync-tree-route-cancel",
                    "sync-tree-route-loss-cancel",
                    "sync-tree-route-cancel-loss",
                    "sync-tree-route-cancel-race",
                    "sync-tree-route-cancel-race-loss-first",
                }
                else 0
            ),
            "sync_tree_route_cancel_adaptive_selections": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_route_cancel_adaptive_selections"
                ]
                if scenario in {
                    "sync-tree-route-cancel",
                    "sync-tree-route-loss-cancel",
                    "sync-tree-route-cancel-loss",
                    "sync-tree-route-cancel-race",
                    "sync-tree-route-cancel-race-loss-first",
                }
                else 0
            ),
            "sync_tree_directories": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_directories"
                ]
                if scenario in SYNC_TREE_SCENARIOS
                else 0
            ),
            "sync_tree_files": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_files"
                ]
                if scenario in SYNC_TREE_SCENARIOS
                else 0
            ),
            "sync_tree_content_bytes": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_content_bytes"
                ]
                if scenario in SYNC_TREE_SCENARIOS
                else 0
            ),
            "sync_tree_payload_sha256": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_payload_sha256"
                ]
                if scenario in SYNC_TREE_SCENARIOS
                else ""
            ),
            "sync_tree_rollback_refused_role_count": (
                sum(
                    int(load(pair_root / receipts[role]["path"])[
                        "sync_tree_rollback_refused"
                    ])
                    for role in ("client", "device")
                )
                if scenario == "sync-tree-adversity"
                else 0
            ),
            "sync_tree_fork_refused_role_count": (
                sum(
                    int(load(pair_root / receipts[role]["path"])[
                        "sync_tree_fork_refused"
                    ])
                    for role in ("client", "device")
                )
                if scenario == "sync-tree-adversity"
                else 0
            ),
            "sync_tree_enospc_observed_role_count": (
                sum(
                    int(load(pair_root / receipts[role]["path"])[
                        "sync_tree_enospc_observed"
                    ])
                    for role in ("client", "device")
                )
                if scenario == "sync-tree-adversity"
                else 0
            ),
            "sync_tree_enospc_retry_observed_role_count": (
                sum(
                    int(load(pair_root / receipts[role]["path"])[
                        "sync_tree_enospc_retry_observed"
                    ])
                    for role in ("client", "device")
                )
                if scenario == "sync-tree-adversity"
                else 0
            ),
            "sync_tree_enospc_reserved_bytes": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_enospc_reserved_bytes"
                ]
                if scenario == "sync-tree-adversity"
                else 0
            ),
            "sync_tree_enospc_failure_free_bytes": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_enospc_failure_free_bytes"
                ]
                if scenario == "sync-tree-adversity"
                else 0
            ),
            "sync_tree_publisher_restart_count": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_publisher_restart_count"
                ]
                if scenario == "sync-tree-adversity"
                else 0
            ),
            "sync_tree_queue_saturation_observed_role_count": (
                sum(
                    int(load(pair_root / receipts[role]["path"])[
                        "sync_tree_queue_saturation_observed"
                    ])
                    for role in ("client", "device")
                )
                if scenario == "sync-tree-pressure"
                else 0
            ),
            "sync_tree_queue_retry_observed_role_count": (
                sum(
                    int(load(pair_root / receipts[role]["path"])[
                        "sync_tree_queue_retry_observed"
                    ])
                    for role in ("client", "device")
                )
                if scenario == "sync-tree-pressure"
                else 0
            ),
            "sync_tree_worker_queue_bound": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_worker_queue_bound"
                ]
                if scenario == "sync-tree-pressure"
                else 0
            ),
            "sync_tree_worker_rejected_delta": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_worker_rejected_delta"
                ]
                if scenario == "sync-tree-pressure"
                else 0
            ),
            "sync_tree_pressure_a_head_record": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_pressure_a_head_record"
                ]
                if scenario == "sync-tree-pressure"
                else ""
            ),
            "sync_tree_pressure_b_head_record": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_pressure_b_head_record"
                ]
                if scenario == "sync-tree-pressure"
                else ""
            ),
            "sync_tree_quota_observed_role_count": (
                sum(
                    int(load(pair_root / receipts[role]["path"])[
                        "sync_tree_quota_observed"
                    ])
                    for role in ("client", "device")
                )
                if scenario in SYNC_TREE_QUOTA_SCENARIOS
                else 0
            ),
            "sync_tree_quota_kind": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_quota_kind"
                ]
                if scenario in SYNC_TREE_QUOTA_SCENARIOS
                else ""
            ),
            "sync_tree_quota_store_bytes": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_quota_store_bytes"
                ]
                if scenario in SYNC_TREE_QUOTA_SCENARIOS
                else 0
            ),
            "sync_tree_quota_inventory_bytes": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_quota_inventory_bytes"
                ]
                if scenario in SYNC_TREE_QUOTA_SCENARIOS
                else 0
            ),
            "sync_tree_quota_maximum_objects": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_quota_maximum_objects"
                ]
                if scenario in SYNC_TREE_QUOTA_SCENARIOS
                else 0
            ),
            "sync_tree_quota_inventory_objects": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_quota_inventory_objects"
                ]
                if scenario in SYNC_TREE_QUOTA_SCENARIOS
                else 0
            ),
            "sync_tree_quota_candidate_head_record": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_quota_candidate_head_record"
                ]
                if scenario in SYNC_TREE_QUOTA_SCENARIOS
                else ""
            ),
            "sync_tree_quota_candidate_artifact_sha256": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_quota_candidate_artifact_sha256"
                ]
                if scenario in SYNC_TREE_QUOTA_SCENARIOS
                else ""
            ),
            "sync_tree_quota_candidate_manifest_sha256": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_quota_candidate_manifest_sha256"
                ]
                if scenario in SYNC_TREE_QUOTA_SCENARIOS
                else ""
            ),
            "sync_tree_read_only_observed_role_count": (
                sum(
                    int(load(pair_root / receipts[role]["path"])[
                        "sync_tree_read_only_observed"
                    ])
                    for role in ("client", "device")
                )
                if scenario == "sync-tree-read-only"
                else 0
            ),
            "sync_tree_read_only_pull_refused_role_count": (
                sum(
                    int(load(pair_root / receipts[role]["path"])[
                        "sync_tree_read_only_pull_refused"
                    ])
                    for role in ("client", "device")
                )
                if scenario == "sync-tree-read-only"
                else 0
            ),
            "sync_tree_read_only_activation_refused_role_count": (
                sum(
                    int(load(pair_root / receipts[role]["path"])[
                        "sync_tree_read_only_activation_refused"
                    ])
                    for role in ("client", "device")
                )
                if scenario == "sync-tree-read-only"
                else 0
            ),
            "sync_tree_read_only_retry_observed_role_count": (
                sum(
                    int(load(pair_root / receipts[role]["path"])[
                        "sync_tree_read_only_retry_observed"
                    ])
                    for role in ("client", "device")
                )
                if scenario == "sync-tree-read-only"
                else 0
            ),
            "sync_tree_read_only_head_record": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_read_only_head_record"
                ]
                if scenario == "sync-tree-read-only"
                else ""
            ),
            "sync_tree_read_only_artifact_sha256": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_read_only_artifact_sha256"
                ]
                if scenario == "sync-tree-read-only"
                else ""
            ),
            "sync_tree_read_only_manifest_sha256": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_read_only_manifest_sha256"
                ]
                if scenario == "sync-tree-read-only"
                else ""
            ),
            "sync_tree_memory_observed_role_count": (
                sum(
                    int(load(pair_root / receipts[role]["path"])[
                        "sync_tree_memory_observed"
                    ])
                    for role in ("client", "device")
                )
                if scenario == "sync-tree-memory"
                else 0
            ),
            "sync_tree_memory_ceiling_kib": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_memory_ceiling_kib"
                ]
                if scenario == "sync-tree-memory"
                else 0
            ),
            "sync_tree_memory_entries": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_memory_entries"
                ]
                if scenario == "sync-tree-memory"
                else 0
            ),
            "sync_tree_memory_artifact_bytes": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_memory_artifact_bytes"
                ]
                if scenario == "sync-tree-memory"
                else 0
            ),
            "sync_tree_memory_head_record": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_memory_head_record"
                ]
                if scenario == "sync-tree-memory"
                else ""
            ),
            "sync_tree_memory_artifact_sha256": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_memory_artifact_sha256"
                ]
                if scenario == "sync-tree-memory"
                else ""
            ),
            "sync_tree_memory_manifest_sha256": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_memory_manifest_sha256"
                ]
                if scenario == "sync-tree-memory"
                else ""
            ),
            "sync_tree_memory_publisher_baseline_hwm_kib": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_memory_publisher_baseline_hwm_kib"
                ]
                if scenario == "sync-tree-memory"
                else 0
            ),
            "sync_tree_memory_publisher_post_publish_hwm_kib": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_memory_publisher_post_publish_hwm_kib"
                ]
                if scenario == "sync-tree-memory"
                else 0
            ),
            "sync_tree_memory_publisher_peak_hwm_kib": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_memory_publisher_peak_hwm_kib"
                ]
                if scenario == "sync-tree-memory"
                else 0
            ),
            "sync_tree_memory_publisher_delta_hwm_kib": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_memory_publisher_delta_hwm_kib"
                ]
                if scenario == "sync-tree-memory"
                else 0
            ),
            "sync_tree_memory_subscriber_baseline_hwm_kib": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_memory_subscriber_baseline_hwm_kib"
                ]
                if scenario == "sync-tree-memory"
                else 0
            ),
            "sync_tree_memory_subscriber_post_pull_hwm_kib": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_memory_subscriber_post_pull_hwm_kib"
                ]
                if scenario == "sync-tree-memory"
                else 0
            ),
            "sync_tree_memory_subscriber_peak_hwm_kib": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_memory_subscriber_peak_hwm_kib"
                ]
                if scenario == "sync-tree-memory"
                else 0
            ),
            "sync_tree_memory_subscriber_delta_hwm_kib": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_memory_subscriber_delta_hwm_kib"
                ]
                if scenario == "sync-tree-memory"
                else 0
            ),
            "sync_tree_memory_pair_peak_hwm_kib": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_memory_pair_peak_hwm_kib"
                ]
                if scenario == "sync-tree-memory"
                else 0
            ),
            "sync_tree_memory_pair_maximum_delta_hwm_kib": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_memory_pair_maximum_delta_hwm_kib"
                ]
                if scenario == "sync-tree-memory"
                else 0
            ),
            "sync_tree_source_corrupt_observed_role_count": (
                sum(
                    int(load(pair_root / receipts[role]["path"])[
                        "sync_tree_source_corrupt_observed"
                    ])
                    for role in ("client", "device")
                )
                if scenario == "sync-tree-source-corrupt"
                else 0
            ),
            "sync_tree_source_corrupt_refused_role_count": (
                sum(
                    int(load(pair_root / receipts[role]["path"])[
                        "sync_tree_source_corrupt_refused"
                    ])
                    for role in ("client", "device")
                )
                if scenario == "sync-tree-source-corrupt"
                else 0
            ),
            "sync_tree_source_corrupt_repaired_role_count": (
                sum(
                    int(load(pair_root / receipts[role]["path"])[
                        "sync_tree_source_corrupt_repaired"
                    ])
                    for role in ("client", "device")
                )
                if scenario == "sync-tree-source-corrupt"
                else 0
            ),
            "sync_tree_source_corrupt_retry_observed_role_count": (
                sum(
                    int(load(pair_root / receipts[role]["path"])[
                        "sync_tree_source_corrupt_retry_observed"
                    ])
                    for role in ("client", "device")
                )
                if scenario == "sync-tree-source-corrupt"
                else 0
            ),
            "sync_tree_source_corrupt_head_record": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_source_corrupt_head_record"
                ]
                if scenario == "sync-tree-source-corrupt"
                else ""
            ),
            "sync_tree_source_corrupt_artifact_sha256": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_source_corrupt_artifact_sha256"
                ]
                if scenario == "sync-tree-source-corrupt"
                else ""
            ),
            "sync_tree_source_corrupt_manifest_sha256": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_source_corrupt_manifest_sha256"
                ]
                if scenario == "sync-tree-source-corrupt"
                else ""
            ),
            "sync_tree_source_corrupt_artifact_bytes": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_source_corrupt_artifact_bytes"
                ]
                if scenario == "sync-tree-source-corrupt"
                else 0
            ),
            "sync_tree_source_corrupt_manifest_bytes": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_source_corrupt_manifest_bytes"
                ]
                if scenario == "sync-tree-source-corrupt"
                else 0
            ),
            "sync_tree_source_corrupt_quarantined_objects": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_source_corrupt_quarantined_objects"
                ]
                if scenario == "sync-tree-source-corrupt"
                else 0
            ),
            "sync_tree_source_corrupt_quarantined_bytes": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_source_corrupt_quarantined_bytes"
                ]
                if scenario == "sync-tree-source-corrupt"
                else 0
            ),
            "sync_tree_destination_corrupt_observed_role_count": (
                sum(
                    int(load(pair_root / receipts[role]["path"])[
                        "sync_tree_destination_corrupt_observed"
                    ])
                    for role in ("client", "device")
                )
                if scenario == "sync-tree-destination-corrupt"
                else 0
            ),
            "sync_tree_destination_corrupt_rejected_role_count": (
                sum(
                    int(load(pair_root / receipts[role]["path"])[
                        "sync_tree_destination_corrupt_rejected"
                    ])
                    for role in ("client", "device")
                )
                if scenario == "sync-tree-destination-corrupt"
                else 0
            ),
            "sync_tree_destination_corrupt_retry_observed_role_count": (
                sum(
                    int(load(pair_root / receipts[role]["path"])[
                        "sync_tree_destination_corrupt_retry_observed"
                    ])
                    for role in ("client", "device")
                )
                if scenario == "sync-tree-destination-corrupt"
                else 0
            ),
            "sync_tree_destination_corrupt_head_record": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_destination_corrupt_head_record"
                ]
                if scenario == "sync-tree-destination-corrupt"
                else ""
            ),
            "sync_tree_destination_corrupt_artifact_sha256": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_destination_corrupt_artifact_sha256"
                ]
                if scenario == "sync-tree-destination-corrupt"
                else ""
            ),
            "sync_tree_destination_corrupt_manifest_sha256": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_destination_corrupt_manifest_sha256"
                ]
                if scenario == "sync-tree-destination-corrupt"
                else ""
            ),
            "sync_tree_destination_corrupt_artifact_bytes": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_destination_corrupt_artifact_bytes"
                ]
                if scenario == "sync-tree-destination-corrupt"
                else 0
            ),
            "sync_tree_destination_corrupt_manifest_bytes": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_destination_corrupt_manifest_bytes"
                ]
                if scenario == "sync-tree-destination-corrupt"
                else 0
            ),
            "sync_tree_destination_corrupt_file_id": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_destination_corrupt_file_id"
                ]
                if scenario == "sync-tree-destination-corrupt"
                else ""
            ),
            "sync_tree_destination_corrupt_position_bytes": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_destination_corrupt_position_bytes"
                ]
                if scenario == "sync-tree-destination-corrupt"
                else 0
            ),
            "sync_tree_destination_corrupt_committed_before_failure": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_destination_corrupt_committed_before_failure"
                ]
                if scenario == "sync-tree-destination-corrupt"
                else 0
            ),
            "sync_tree_destination_corrupt_retry_requested_objects": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_destination_corrupt_retry_requested_objects"
                ]
                if scenario == "sync-tree-destination-corrupt"
                else 0
            ),
            "sync_tree_control_replay_observed_role_count": (
                sum(
                    int(load(pair_root / receipts[role]["path"])[
                        "sync_tree_control_replay_observed"
                    ])
                    for role in ("client", "device")
                )
                if scenario == "sync-tree-control-replay"
                else 0
            ),
            "sync_tree_control_replay_exact_replay_observed_role_count": (
                sum(
                    int(load(pair_root / receipts[role]["path"])[
                        "sync_tree_control_replay_exact_replay_observed"
                    ])
                    for role in ("client", "device")
                )
                if scenario == "sync-tree-control-replay"
                else 0
            ),
            "sync_tree_control_replay_reordered_result_observed_role_count": (
                sum(
                    int(load(pair_root / receipts[role]["path"])[
                        "sync_tree_control_replay_reordered_result_observed"
                    ])
                    for role in ("client", "device")
                )
                if scenario == "sync-tree-control-replay"
                else 0
            ),
            "sync_tree_control_replay_conflict_refused_role_count": (
                sum(
                    int(load(pair_root / receipts[role]["path"])[
                        "sync_tree_control_replay_conflict_refused"
                    ])
                    for role in ("client", "device")
                )
                if scenario == "sync-tree-control-replay"
                else 0
            ),
            "sync_tree_control_replay_activation_observed_role_count": (
                sum(
                    int(load(pair_root / receipts[role]["path"])[
                        "sync_tree_control_replay_activation_observed"
                    ])
                    for role in ("client", "device")
                )
                if scenario == "sync-tree-control-replay"
                else 0
            ),
            "sync_tree_control_replay_head_record": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_control_replay_head_record"
                ]
                if scenario == "sync-tree-control-replay"
                else ""
            ),
            "sync_tree_control_replay_artifact_sha256": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_control_replay_artifact_sha256"
                ]
                if scenario == "sync-tree-control-replay"
                else ""
            ),
            "sync_tree_control_replay_manifest_sha256": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_control_replay_manifest_sha256"
                ]
                if scenario == "sync-tree-control-replay"
                else ""
            ),
            "sync_tree_control_replay_admitted_before_replay": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_control_replay_admitted_before_replay"
                ]
                if scenario == "sync-tree-control-replay"
                else 0
            ),
            "sync_tree_control_replay_publisher_head_requests_delta": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_control_replay_publisher_head_requests_delta"
                ]
                if scenario == "sync-tree-control-replay"
                else 0
            ),
            "sync_tree_control_replay_publisher_object_requests_delta": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_control_replay_publisher_object_requests_delta"
                ]
                if scenario == "sync-tree-control-replay"
                else 0
            ),
            "sync_tree_control_replay_publisher_file_offers_delta": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_control_replay_publisher_file_offers_delta"
                ]
                if scenario == "sync-tree-control-replay"
                else 0
            ),
            "sync_tree_control_replay_publisher_replay_hits_delta": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_control_replay_publisher_replay_hits_delta"
                ]
                if scenario == "sync-tree-control-replay"
                else 0
            ),
            "sync_tree_control_replay_publisher_replay_conflicts_delta": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_control_replay_publisher_replay_conflicts_delta"
                ]
                if scenario == "sync-tree-control-replay"
                else 0
            ),
            "sync_tree_control_replay_subscriber_incoming_head_results_delta": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_control_replay_subscriber_incoming_head_results_delta"
                ]
                if scenario == "sync-tree-control-replay"
                else 0
            ),
            "sync_tree_control_replay_subscriber_incoming_object_results_delta": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_control_replay_subscriber_incoming_object_results_delta"
                ]
                if scenario == "sync-tree-control-replay"
                else 0
            ),
            "sync_tree_control_replay_subscriber_outgoing_object_requests_delta": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_tree_control_replay_subscriber_outgoing_object_requests_delta"
                ]
                if scenario == "sync-tree-control-replay"
                else 0
            ),
            "sync_range_observed_role_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"])[
                            "sync_range_observed"
                        ]
                    )
                    for role in ("client", "device")
                )
                if scenario in SYNC_POSITIVE_RANGE_SCENARIOS
                else 0
            ),
            "sync_range_fallback_observed_role_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"])[
                            "sync_range_fallback_observed"
                        ]
                    )
                    for role in ("client", "device")
                )
                if scenario == "sync-file-corrupt-basis"
                else 0
            ),
            "sync_corrupt_basis_preserved_role_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"])[
                            "sync_corrupt_basis_preserved"
                        ]
                    )
                    for role in ("client", "device")
                )
                if scenario == "sync-file-corrupt-basis"
                else 0
            ),
            "sync_range_retry_observed_role_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"])[
                            "sync_range_retry_observed"
                        ]
                    )
                    for role in ("client", "device")
                )
                if scenario == "sync-file-range-retry"
                else 0
            ),
            "sync_range_retry_position_bytes": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_range_retry_position_bytes"
                ]
                if scenario == "sync-file-range-retry"
                else 0
            ),
            "sync_range_retry_retained_bytes": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_range_retry_retained_bytes"
                ]
                if scenario == "sync-file-range-retry"
                else 0
            ),
            "sync_range_retry_resumed_bytes": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_range_retry_resumed_bytes"
                ]
                if scenario == "sync-file-range-retry"
                else 0
            ),
            "sync_range_retry_discarded_bytes": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_range_retry_discarded_bytes"
                ]
                if scenario == "sync-file-range-retry"
                else 0
            ),
            "sync_range_retry_retention_fallbacks": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_range_retry_retention_fallbacks"
                ]
                if scenario == "sync-file-range-retry"
                else 0
            ),
            "sync_range_retry_first_file_id": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_range_retry_first_file_id"
                ]
                if scenario == "sync-file-range-retry"
                else ""
            ),
            "sync_range_retry_second_file_id": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_range_retry_second_file_id"
                ]
                if scenario == "sync-file-range-retry"
                else ""
            ),
            "sync_range_count": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_range_count"
                ]
                if scenario in SYNC_RANGE_SCENARIOS
                else 0
            ),
            "sync_range_reused_bytes": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_range_reused_bytes"
                ]
                if scenario in SYNC_RANGE_SCENARIOS
                else 0
            ),
            "sync_range_fetched_bytes": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_range_fetched_bytes"
                ]
                if scenario in SYNC_RANGE_SCENARIOS
                else 0
            ),
            "sync_repair_observed_role_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"])[
                            "sync_repair_observed"
                        ]
                    )
                    for role in ("client", "device")
                )
                if scenario == "sync-file-repair"
                else 0
            ),
            "sync_repair_recovered_role_count": (
                sum(
                    int(
                        load(pair_root / receipts[role]["path"])[
                            "sync_repair_recovery_observed"
                        ]
                    )
                    for role in ("client", "device")
                )
                if scenario == "sync-file-repair"
                else 0
            ),
            "sync_repair_inspected_objects": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_repair_inspected_objects"
                ]
                if scenario == "sync-file-repair"
                else 0
            ),
            "sync_repair_quarantined_objects": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_repair_quarantined_objects"
                ]
                if scenario == "sync-file-repair"
                else 0
            ),
            "sync_repair_quarantined_bytes": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_repair_quarantined_bytes"
                ]
                if scenario == "sync-file-repair"
                else 0
            ),
            "sync_gc_observed_role_count": (
                sum(
                    int(load(pair_root / receipts[role]["path"])[
                        "sync_gc_observed"
                    ])
                    for role in ("client", "device")
                )
                if scenario == "sync-file-repair"
                else 0
            ),
            "sync_gc_dry_candidates": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_gc_dry_candidates"
                ]
                if scenario == "sync-file-repair"
                else 0
            ),
            "sync_gc_moved_objects": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_gc_moved_objects"
                ]
                if scenario == "sync-file-repair"
                else 0
            ),
            "sync_gc_durable_objects": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_gc_durable_objects"
                ]
                if scenario == "sync-file-repair"
                else 0
            ),
            "sync_gc_outside_sentinel_count": (
                sum(
                    load(pair_root / receipts[role]["path"])[
                        "sync_gc_outside_sentinels"
                    ]
                    for role in ("client", "device")
                )
                if scenario == "sync-file-repair"
                else 0
            ),
            "sync_gc_purge_disabled_role_count": (
                sum(
                    int(load(pair_root / receipts[role]["path"])[
                        "sync_gc_purge_disabled"
                    ])
                    for role in ("client", "device")
                )
                if scenario == "sync-file-repair"
                else 0
            ),
            "sync_gc_mount_refused_role_count": (
                sum(
                    int(load(pair_root / receipts[role]["path"])[
                        "sync_gc_mount_refused"
                    ])
                    for role in ("client", "device")
                )
                if scenario == "sync-file-repair"
                else 0
            ),
            "sync_artifact_sha256": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_artifact_sha256"
                ]
                if scenario in SYNC_SCENARIOS
                else ""
            ),
            "sync_manifest_sha256": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_manifest_sha256"
                ]
                if scenario in SYNC_SCENARIOS
                else ""
            ),
            "sync_head_record": (
                load(pair_root / receipts["client"]["path"])[
                    "sync_head_record"
                ]
                if scenario in SYNC_SCENARIOS
                else ""
            ),
            "ratox_bulk_stream_count": RATOX_BULK_SCENARIOS.get(scenario, 0),
            "ratox_sample_count": (
                ratox_sample_count(scenario) if scenario in RATOX_SCENARIOS else 0
            ),
            "ratox_resource_interval_role_count": (
                2 if scenario in RATOX_SCENARIOS else 0
            ),
            "ratox_stripe_route_count": RATOX_STRIPE_SCENARIOS.get(scenario, 1),
            "ratox_stripe_route_restart_count": sum(
                load(
                    pair_root / receipts[role]["path"]
                )["ratox_stripe_route_restart_count"]
                for role in ("client", "device")
            ),
            "ratox_stripe_injected_restart_count": sum(
                load(
                    pair_root / receipts[role]["path"]
                )["ratox_stripe_injected_restart_count"]
                for role in ("client", "device")
            ),
            "ratox_stripe_live_fault_count": sum(
                int(
                    load(pair_root / receipts[role]["path"])[
                        "ratox_stripe_live_fault_injected"
                    ]
                )
                for role in ("client", "device")
            ),
            "ratox_stripe_live_observer_count": sum(
                int(
                    load(pair_root / receipts[role]["path"])[
                        "ratox_stripe_live_offline_observed"
                    ]
                )
                for role in ("client", "device")
            ),
            "ratox_stripe_live_recovered_role_count": sum(
                int(
                    load(pair_root / receipts[role]["path"])[
                        "ratox_stripe_live_recovery_observed"
                    ]
                )
                for role in ("client", "device")
            ),
            "ratox_stripe_live_affected_transfer_count": max(
                load(pair_root / receipts[role]["path"])[
                    "ratox_stripe_live_affected_transfer_count"
                ]
                for role in ("client", "device")
            ),
            "ratox_stripe_live_reassigned_transfer_count": max(
                load(pair_root / receipts[role]["path"])[
                    "ratox_stripe_live_reassigned_transfer_count"
                ]
                for role in ("client", "device")
            ),
            "initial_device_chain": initial_device_chain_entry,
            "initial_device_launch": initial_device_launch_entry,
            "taps": taps,
            "identity_mode": "reused-immutable-private-baseline",
            "identity_baseline_unchanged": True,
            "proof_root_contains_private_guest_disks": True,
            "receipts_contain_secrets": False,
            "receipts": receipts,
            "chains": chains,
        }
        manifest_path = pair_root / "pair-manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        os.chmod(manifest_path, 0o600)
        print(json.dumps({**manifest, "proof_root": str(pair_root)}, indent=2, sort_keys=True))
        return pair_root
    finally:
        for instance in tor_adversaries.values():
            hold_path = Path(instance["hold_path"])
            hold_path.unlink(missing_ok=True)
            process = instance.get("process")
            if isinstance(process, subprocess.Popen) and process.poll() is None:
                terminate({str(instance["role"]): process})
                try:
                    output, errors = process.communicate(timeout=5)
                    Path(instance["stdout_path"]).write_text(
                        output, encoding="utf-8"
                    )
                    Path(instance["stderr_path"]).write_text(
                        errors, encoding="utf-8"
                    )
                except (OSError, subprocess.TimeoutExpired):
                    pass
        if sync_client_shaped:
            subprocess.run(
                [
                    "sudo",
                    "-n",
                    str(HOST_BIN / "tc"),
                    "qdisc",
                    "del",
                    "dev",
                    "vm-iotoxc",
                    "root",
                ],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        if links_blocked:
            for tap in ("vm-iotoxc", "vm-iotoxd"):
                subprocess.run(
                    [
                        "sudo",
                        "-n",
                        str(HOST_BIN / "tc"),
                        "qdisc",
                        "del",
                        "dev",
                        tap,
                        "root",
                    ],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
        terminate(processes)
        if socks5_process is not None:
            terminate({"socks5": socks5_process})
            try:
                output, errors = socks5_process.communicate(timeout=5)
                (pair_root / f"socks5-{socks5_phase}.stdout").write_text(
                    output, encoding="utf-8"
                )
                (pair_root / f"socks5-{socks5_phase}.stderr").write_text(
                    errors, encoding="utf-8"
                )
            except (OSError, subprocess.TimeoutExpired):
                pass
        if capture_processes:
            terminate(capture_processes)
        for handles in capture_handles.values():
            for handle in handles:
                handle.close()
        if i2p_instance is not None:
            process = i2p_instance.get("process")
            if isinstance(process, subprocess.Popen) and process.poll() is None:
                terminate({"i2p-fronts": process})
            stderr = i2p_instance.get("stderr")
            if hasattr(stderr, "close"):
                stderr.close()
        if tor_instances:
            for instance in tor_instances.values():
                observer = instance.get("observer")
                if isinstance(observer, TorStreamObserver):
                    try:
                        observer.stop()
                    except (OSError, RuntimeError):
                        pass
            terminate(
                {
                    role: instance["process"]
                    for role, instance in tor_instances.items()
                    if isinstance(instance.get("process"), subprocess.Popen)
                }
            )
            for instance in tor_instances.values():
                log = instance.get("log")
                if log is not None:
                    log.close()
        if fixture_process is not None:
            terminate({"bootstrap": fixture_process})
        if secondary_fixture_process is not None:
            terminate({"bootstrap-secondary": secondary_fixture_process})
        for stdout, stderr in logs.values():
            stdout.close()
            stderr.close()
        if fixture_log is not None:
            fixture_log.close()
        if secondary_fixture_log is not None:
            secondary_fixture_log.close()
        fcntl.flock(lock_handle, fcntl.LOCK_UN)
        lock_handle.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "route",
        nargs="?",
        choices=(
            "direct-udp",
            "forced-tcp",
            "tox-tor",
            "tox-i2p",
            "tox-i2p-construction",
        ),
    )
    parser.add_argument(
        "scenario",
        nargs="?",
        choices=(
            "baseline",
            "relay-restart",
            "proxy-restart",
            "i2p-router-restart",
            "i2p-service-restart",
            "daemon-restart",
            "link-interruption",
            "packet-loss",
            "provider-rolling",
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
        default="baseline",
    )
    parser.add_argument(
        "--tor-node",
        help="operator-supplied public IPv4:PORT:64_HEX_KEY for the actual-Tor scenario",
    )
    parser.add_argument(
        "--i2p-node",
        action="append",
        default=[],
        help="one explicit public IPv4:PORT:64_HEX_KEY for the three-front actual-I2P route",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.route is None:
        parser.error("route is required unless --self-test is used")
    try:
        run(args.route, args.scenario, args.tor_node, args.i2p_node)
    except Exception as error:
        print(f"sandwurm pair failed: {error}", file=os.sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
