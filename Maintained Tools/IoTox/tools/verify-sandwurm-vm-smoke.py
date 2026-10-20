#!/usr/bin/env python3
"""Verify one bounded IoTox Sandwurm boot receipt tree."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"JSON root is not an object: {path}")
    return value


def product_identity() -> tuple[str, str]:
    revision = (ROOT / "REVISION").read_text(encoding="utf-8").strip()
    header = (ROOT / "include/iotox/version.hpp").read_text(encoding="utf-8")
    match = re.search(r'kVersion = "([^"]+)"', header)
    if match is None:
        raise ValueError("IoTox version header has no kVersion")
    return match.group(1), revision


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def verify(proof_root: Path, role: str) -> dict:
    require(role in {"client", "device"}, "role must be client or device")
    proof_root = proof_root.resolve()
    chain = load(proof_root / "direct-cloud-hypervisor-live-chain.json")
    planned = load(proof_root / "prelaunch/launch/cloud-hypervisor-launch.json")
    live = load(proof_root / "live/cloud-hypervisor-launch.json")
    smoke = load(
        proof_root
        / "live/workspace-export/guest-receipts/iotox/vm-smoke.json"
    )

    require(
        chain.get("schema") == "sandwurm.direct-cloud-hypervisor-live-chain.v0",
        "unexpected Sandwurm live-chain schema",
    )
    require(
        chain.get("status") == "guest-evidence-observed",
        "guest evidence was not accepted",
    )
    require(chain.get("failure") is None, "live chain contains a failure")
    require(
        chain.get("receipts", {}).get("prelaunch_chain", {}).get("status")
        == "ready",
        "prelaunch was not ready",
    )
    require(
        chain.get("receipts", {}).get("live_launch", {}).get("status")
        == "exited",
        "VMM exit was not observed",
    )
    require(
        chain.get("guest_evidence", {}).get("observed") is True,
        "guest boundary was not observed",
    )
    require(
        chain.get("guest_evidence", {}).get("legacy_guest_receipts_complete")
        is True,
        "generic guest receipts are incomplete",
    )

    require(planned.get("status") == "planned", "launch receipt was not planned")
    require(
        planned.get("network", {}).get("class") == "none",
        "planned network class is not none",
    )
    require(
        planned.get("network", {}).get("mode") == "none",
        "planned network mode is not none",
    )
    argv = planned.get("vmm", {}).get("argv")
    require(isinstance(argv, list) and argv, "planned VMM argv is absent")
    require(
        not any(
            isinstance(arg, str)
            and (arg == "--net" or arg.startswith("--net="))
            for arg in argv
        ),
        "network-none launch contains a --net argument",
    )
    require(live.get("status") == "exited", "live launch did not exit")
    require(
        live.get("guest_boundary", {}).get("observed") is True,
        "live guest boundary is absent",
    )
    require(
        live.get("guest_boundary", {}).get("vm_substrate")
        == "cloud-hypervisor",
        "wrong VM substrate",
    )

    version, revision = product_identity()
    require(
        smoke.get("schema") == "iotox.sandwurm-vm-smoke.v0",
        "unexpected IoTox smoke schema",
    )
    require(smoke.get("status") == "passed", "IoTox guest smoke did not pass")
    require(smoke.get("role") == role, "IoTox guest role mismatch")
    require(
        smoke.get("product_revision") == revision,
        "IoTox product revision mismatch",
    )
    require(
        smoke.get("version") == f"IoTox {version} {revision}",
        "IoTox version output mismatch",
    )
    require(
        isinstance(smoke.get("source_revision"), str)
        and bool(smoke["source_revision"]),
        "source revision is absent",
    )
    require(
        re.fullmatch(
            r"[0-9a-f]{64}", str(smoke.get("binary_sha256", ""))
        )
        is not None,
        "binary digest is not SHA-256 hex",
    )
    require(smoke.get("virtualization") == "kvm", "guest did not observe KVM")
    require(smoke.get("cgroup_type") == "cgroup2fs", "guest did not observe cgroup v2")
    require(
        smoke.get("network_class") == "none",
        "IoTox receipt network class is not none",
    )
    require(
        smoke.get("package_variant") == "pinned-source-linked",
        "IoTox package is not the pinned source-linked variant",
    )
    require(
        smoke.get("contains_secrets") is False,
        "IoTox receipt is not marked content-free",
    )

    return {
        "schema": "iotox.sandwurm-vm-smoke-verification.v0",
        "status": "passed",
        "role": role,
        "proof_root": str(proof_root),
        "source_revision": smoke["source_revision"],
        "product_revision": revision,
        "version": smoke["version"],
        "binary_sha256": smoke["binary_sha256"],
        "vm_substrate": "cloud-hypervisor",
        "network_class": "none",
        "vmm_exit_observed": True,
    }


def self_test() -> None:
    version, revision = product_identity()
    with tempfile.TemporaryDirectory(prefix="iotox-sandwurm-verifier-") as directory:
        root = Path(directory)
        files = {
            "direct-cloud-hypervisor-live-chain.json": {
                "schema": "sandwurm.direct-cloud-hypervisor-live-chain.v0",
                "status": "guest-evidence-observed",
                "failure": None,
                "receipts": {
                    "prelaunch_chain": {"status": "ready"},
                    "live_launch": {"status": "exited"},
                },
                "guest_evidence": {
                    "observed": True,
                    "legacy_guest_receipts_complete": True,
                },
            },
            "prelaunch/launch/cloud-hypervisor-launch.json": {
                "status": "planned",
                "network": {"class": "none", "mode": "none"},
                "vmm": {"argv": ["cloud-hypervisor", "--cpus", "boot=2,max=2"]},
            },
            "live/cloud-hypervisor-launch.json": {
                "status": "exited",
                "guest_boundary": {
                    "observed": True,
                    "vm_substrate": "cloud-hypervisor",
                },
            },
            "live/workspace-export/guest-receipts/iotox/vm-smoke.json": {
                "schema": "iotox.sandwurm-vm-smoke.v0",
                "status": "passed",
                "role": "device",
                "source_revision": "0" * 40,
                "product_revision": revision,
                "version": f"IoTox {version} {revision}",
                "binary_sha256": "a" * 64,
                "virtualization": "kvm",
                "cgroup_type": "cgroup2fs",
                "network_class": "none",
                "package_variant": "pinned-source-linked",
                "contains_secrets": False,
            },
        }
        for relative, value in files.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(value), encoding="utf-8")
        verify(root, "device")
        files["prelaunch/launch/cloud-hypervisor-launch.json"]["vmm"]["argv"].append("--net")
        path = root / "prelaunch/launch/cloud-hypervisor-launch.json"
        path.write_text(
            json.dumps(
                files["prelaunch/launch/cloud-hypervisor-launch.json"]
            ),
            encoding="utf-8",
        )
        try:
            verify(root, "device")
        except ValueError as error:
            require("--net" in str(error), "negative self-test failed for the wrong reason")
        else:
            raise ValueError("verifier accepted a network-none launch containing --net")
    print("sandwurm-vm-smoke verifier self-test: PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("proof_root", nargs="?", type=Path)
    parser.add_argument("role", nargs="?", choices=("client", "device"))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.proof_root is None or args.role is None:
        parser.error("proof_root and role are required unless --self-test is used")
    print(json.dumps(verify(args.proof_root, args.role), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
