#!/usr/bin/env python3
"""Verify the content-free IoTox/Resilio shadow receipt and Sandwurm boundary."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path


HEX64 = re.compile(r"^[0-9a-f]{64}$")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as source:
        value = json.load(source)
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def verify_receipt(evidence: dict, minimum_seconds: int) -> dict:
    require(evidence.get("schema") == "iotox.sync-shadow.v1", "bad shadow schema")
    require(evidence.get("status") == "passed", "shadow campaign did not pass")
    require(evidence.get("incumbent") == "resilio-sync", "incumbent is not Resilio")
    floor = evidence.get("duration_floor_seconds")
    elapsed = evidence.get("elapsed_ms")
    require(
        isinstance(floor, int)
        and floor >= minimum_seconds
        and isinstance(elapsed, int)
        and elapsed >= floor * 1000,
        "wall-clock shadow floor is not satisfied",
    )
    cycles = evidence.get("cycles")
    interval = evidence.get("interval_seconds")
    require(
        isinstance(cycles, int)
        and cycles >= 9
        and isinstance(interval, int)
        and interval >= 5,
        "shadow cycle evidence is invalid",
    )
    require(
        evidence.get("node_count") == 2
        and evidence.get("manual_publish_pull_activate_commands") == 0,
        "shadow path was not an unattended two-node path",
    )
    require(
        isinstance(evidence.get("publisher_restarts"), int)
        and evidence["publisher_restarts"] >= 0
        and isinstance(evidence.get("replica_restarts"), int)
        and evidence["replica_restarts"] >= 0,
        "restart evidence is invalid",
    )
    require(
        isinstance(evidence.get("publisher_replay_evictions"), int)
        and evidence["publisher_replay_evictions"] > 0,
        "shadow did not cross the publisher exact-replay window",
    )
    require(
        isinstance(evidence.get("canonical_files"), int)
        and evidence["canonical_files"] > 0
        and isinstance(evidence.get("canonical_bytes"), int)
        and evidence["canonical_bytes"] >= 0,
        "canonical tree population is invalid",
    )
    for name in (
        "canonical_manifest_sha256",
        "resilio_binary_sha256",
        "resilio_version_output_sha256",
        "iotox_binary_sha256",
    ):
        require(HEX64.fullmatch(evidence.get(name, "")) is not None,
                f"{name} is invalid")
    require(evidence.get("contains_secrets") is False, "receipt contains secrets")
    return {
        "schema": "iotox.sync-shadow-verification.v1",
        "status": "passed",
        "duration_floor_seconds": floor,
        "elapsed_ms": elapsed,
        "cycles": cycles,
        "publisher_restarts": evidence["publisher_restarts"],
        "replica_restarts": evidence["replica_restarts"],
        "publisher_replay_evictions": evidence["publisher_replay_evictions"],
        "canonical_manifest_sha256": evidence["canonical_manifest_sha256"],
        "incumbent": "resilio-sync",
        "contains_secrets": False,
    }


def verify_sandwurm(proof_root: Path, minimum_seconds: int) -> dict:
    proof_root = proof_root.resolve()
    chain = load(proof_root / "direct-cloud-hypervisor-live-chain.json")
    launch = load(proof_root / "prelaunch/launch/cloud-hypervisor-launch.json")
    evidence = load(
        proof_root / "live/workspace-export/guest-receipts/iotox/sync-shadow.json"
    )
    require(
        chain.get("status") == "guest-evidence-observed"
        and chain.get("failure") is None,
        "Sandwurm did not accept the shadow guest boundary",
    )
    require(
        launch.get("network", {}).get("class") == "none"
        and launch.get("network", {}).get("mode") == "none",
        "shadow guest was not networkless",
    )
    argv = launch.get("vmm", {}).get("argv", [])
    require(
        not any(
            isinstance(argument, str)
            and (argument == "--net" or argument.startswith("--net="))
            for argument in argv
        ),
        "networkless shadow launch contains a VMM network device",
    )
    result = verify_receipt(evidence, minimum_seconds)
    result["proof_root"] = str(proof_root)
    result["network_class"] = "none"
    result["vm_substrate"] = "cloud-hypervisor"
    return result


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value) + "\n", encoding="utf-8")


def fixture_receipt() -> dict:
    return {
        "schema": "iotox.sync-shadow.v1",
        "status": "passed",
        "incumbent": "resilio-sync",
        "duration_floor_seconds": 7200,
        "elapsed_ms": 7_200_001,
        "cycles": 240,
        "interval_seconds": 30,
        "seed": 20260901,
        "publisher_restarts": 6,
        "replica_restarts": 6,
        "publisher_replay_evictions": 1024,
        "canonical_manifest_sha256": "11" * 32,
        "canonical_files": 24,
        "canonical_bytes": 65536,
        "resilio_binary_sha256": "22" * 32,
        "resilio_version_output_sha256": "33" * 32,
        "iotox_binary_sha256": "44" * 32,
        "node_count": 2,
        "manual_publish_pull_activate_commands": 0,
        "contains_secrets": False,
    }


def self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="iotox-shadow-verifier-") as raw:
        root = Path(raw)
        write_json(
            root / "direct-cloud-hypervisor-live-chain.json",
            {"status": "guest-evidence-observed", "failure": None},
        )
        write_json(
            root / "prelaunch/launch/cloud-hypervisor-launch.json",
            {"network": {"class": "none", "mode": "none"}, "vmm": {"argv": []}},
        )
        evidence_path = (
            root / "live/workspace-export/guest-receipts/iotox/sync-shadow.json"
        )
        evidence = fixture_receipt()
        write_json(evidence_path, evidence)
        require(verify_sandwurm(root, 7200)["status"] == "passed",
                "valid shadow fixture failed")
        evidence["elapsed_ms"] = 7_199_999
        write_json(evidence_path, evidence)
        try:
            verify_sandwurm(root, 7200)
        except ValueError:
            pass
        else:
            raise ValueError("short shadow fixture passed")
        evidence = fixture_receipt()
        evidence["cycles"] = 8
        write_json(evidence_path, evidence)
        try:
            verify_sandwurm(root, 7200)
        except ValueError:
            pass
        else:
            raise ValueError("pre-regression-boundary shadow fixture passed")
        evidence = fixture_receipt()
        evidence["publisher_replay_evictions"] = 0
        write_json(evidence_path, evidence)
        try:
            verify_sandwurm(root, 7200)
        except ValueError:
            pass
        else:
            raise ValueError("replay-window exhaustion regression fixture passed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("proof_root", type=Path, nargs="?")
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--minimum-seconds", type=int, default=7200)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    require(60 <= args.minimum_seconds <= 86400, "minimum duration is invalid")
    if args.self_test:
        self_test()
        print("sync-shadow Sandwurm verifier self-test: PASS")
        return 0
    require((args.proof_root is None) != (args.receipt is None),
            "provide exactly one proof root or --receipt")
    result = (
        verify_receipt(load(args.receipt.resolve()), args.minimum_seconds)
        if args.receipt is not None
        else verify_sandwurm(args.proof_root, args.minimum_seconds)
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
