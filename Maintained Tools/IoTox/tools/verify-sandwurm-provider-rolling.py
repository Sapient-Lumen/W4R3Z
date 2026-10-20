#!/usr/bin/env python3
"""Strictly verify the content-free mixed c-toxcore Sandwurm proof."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path


ROLES = ("client", "device")
ROUTES = {"direct-udp": "udp", "forced-tcp": "tcp"}
SHA256 = re.compile(r"[0-9a-f]{64}")
OLD_SOURCE_SHA256 = "276d447eb94e9d76e802cecc5ca7660c6c15128a83dfbe4353b678972aeb950a"
CURRENT_SOURCE_SHA256 = "b0349f4829d3d1699a77e199850f870f48d376e2baaf2c69d27b28571c498cfe"
MANIFEST_SCHEMA = "iotox.sandwurm-provider-rolling-manifest.v0"
RECEIPT_SCHEMA = "iotox.sandwurm-provider-rolling.v0"
COMPACT_SCHEMA = "iotox.sandwurm-provider-rolling-compact.v0"
MANIFEST_NAME = "provider-rolling-manifest.json"


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


def evidence_paths() -> tuple[str, ...]:
    values = [MANIFEST_NAME]
    for role in ROLES:
        values.extend(
            (
                f"{role}/direct-cloud-hypervisor-live-chain.json",
                f"{role}/prelaunch/launch/cloud-hypervisor-launch.json",
                f"{role}/live/workspace-export/guest-receipts/iotox/provider-rolling.json",
            )
        )
    return tuple(values)


def verify(proof_root: Path, expected_route: str | None = None) -> dict:
    proof_root = proof_root.resolve()
    manifest_path = proof_root / MANIFEST_NAME
    manifest = load(manifest_path)
    route = manifest.get("route_mode")
    require(route in ROUTES, "provider proof route is invalid")
    if expected_route is not None:
        require(route == expected_route, "provider proof route mismatch")
    connection = ROUTES[route]
    require(manifest.get("schema") == MANIFEST_SCHEMA, "provider manifest schema mismatch")
    require(manifest.get("status") == "passed", "provider manifest did not pass")
    require(manifest.get("expected_connection") == connection, "provider connection mismatch")
    require(manifest.get("old_provider") == "0.2.22", "old provider mismatch")
    require(manifest.get("current_provider") == "0.2.23", "current provider mismatch")
    require(manifest.get("client_live_provider") == "0.2.22", "client provider mismatch")
    require(manifest.get("device_live_provider") == "0.2.23", "device provider mismatch")
    require(manifest.get("savedata_created_by") == "0.2.22", "savedata origin mismatch")
    require(
        manifest.get("simultaneous_vmm_chains_observed") is True,
        "simultaneous VMM observation is absent",
    )
    require(manifest.get("prepared_bridge") == "sandwurm-vm", "prepared bridge mismatch")
    require(
        manifest.get("bootstrap_fixture") == "pinned-host-bridge-c-toxcore-0.2.23",
        "bootstrap fixture mismatch",
    )
    span = manifest.get("rendezvous_monotonic_span_ns")
    require(isinstance(span, int) and span > 0, "provider proof duration is invalid")
    require(manifest.get("receipts_contain_secrets") is False, "provider receipts claim secrets")

    taps = manifest.get("taps")
    require(isinstance(taps, list) and len(taps) == 2, "provider TAP inventory is invalid")
    require(
        {entry.get("name") for entry in taps if isinstance(entry, dict)}
        == {"vm-iotoxc", "vm-iotoxd"},
        "provider TAP names changed",
    )
    require(
        all(entry.get("master") == "sandwurm-vm" for entry in taps),
        "a provider TAP escaped the prepared bridge",
    )

    receipts = manifest.get("receipts")
    chains = manifest.get("chains")
    launches = manifest.get("launches")
    require(isinstance(receipts, dict) and set(receipts) == set(ROLES), "receipt inventory mismatch")
    require(isinstance(chains, dict) and set(chains) == set(ROLES), "chain inventory mismatch")
    require(isinstance(launches, dict) and set(launches) == set(ROLES), "launch inventory mismatch")
    old_binary_sha256 = None
    current_binary_sha256 = None

    for role in ROLES:
        expected_provider = "0.2.22" if role == "client" else "0.2.23"
        receipt_relative = (
            f"{role}/live/workspace-export/guest-receipts/iotox/provider-rolling.json"
        )
        chain_relative = f"{role}/direct-cloud-hypervisor-live-chain.json"
        launch_relative = f"{role}/prelaunch/launch/cloud-hypervisor-launch.json"
        for inventory, relative, label in (
            (receipts, receipt_relative, "receipt"),
            (chains, chain_relative, "chain"),
            (launches, launch_relative, "launch"),
        ):
            entry = inventory[role]
            require(isinstance(entry, dict), f"{role} {label} entry is invalid")
            require(entry.get("path") == relative, f"{role} {label} path mismatch")
            path = proof_root / relative
            require(path.is_file() and not path.is_symlink(), f"{role} {label} is absent")
            require(entry.get("sha256") == digest(path), f"{role} {label} digest mismatch")

        receipt = load(proof_root / receipt_relative)
        require(receipt.get("schema") == RECEIPT_SCHEMA, f"{role} receipt schema mismatch")
        require(receipt.get("status") == "passed", f"{role} receipt did not pass")
        require(receipt.get("role") == role, f"{role} receipt role mismatch")
        require(receipt.get("route_mode") == route, f"{role} receipt route mismatch")
        require(receipt.get("expected_connection") == connection, f"{role} route was not observed")
        require(receipt.get("live_provider") == expected_provider, f"{role} provider mismatch")
        require(receipt.get("savedata_created_by") == "0.2.22", f"{role} savedata origin mismatch")
        require(
            receipt.get("savedata_readable_by") == ["0.2.22", "0.2.23"],
            f"{role} cross-provider readability mismatch",
        )
        require(receipt.get("old_source_sha256") == OLD_SOURCE_SHA256, f"{role} old source mismatch")
        require(
            receipt.get("current_source_sha256") == CURRENT_SOURCE_SHA256,
            f"{role} current source mismatch",
        )
        require(receipt.get("virtualization") == "kvm", f"{role} was not a KVM guest")
        require(receipt.get("sent") is True and receipt.get("received") is True, f"{role} did not exchange")
        require(
            receipt.get("savedata_semantics_preserved") is True,
            f"{role} savedata semantics changed",
        )
        savedata_bytes = receipt.get("savedata_bytes")
        require(
            isinstance(savedata_bytes, int) and 1 <= savedata_bytes <= 16 * 1024 * 1024,
            f"{role} savedata size is invalid",
        )
        require(receipt.get("contains_secrets") is False, f"{role} receipt claims secrets")
        for field in ("old_binary_sha256", "current_binary_sha256"):
            require(SHA256.fullmatch(str(receipt.get(field, ""))) is not None, f"{role} {field} invalid")
        if old_binary_sha256 is None:
            old_binary_sha256 = receipt["old_binary_sha256"]
            current_binary_sha256 = receipt["current_binary_sha256"]
        require(receipt["old_binary_sha256"] == old_binary_sha256, "old fixture differs between guests")
        require(
            receipt["current_binary_sha256"] == current_binary_sha256,
            "current fixture differs between guests",
        )

        chain = load(proof_root / chain_relative)
        require(
            chain.get("schema") == "sandwurm.direct-cloud-hypervisor-live-chain.v0",
            f"{role} chain schema mismatch",
        )
        require(chain.get("status") == "guest-evidence-observed", f"{role} chain did not pass")
        requested = chain.get("requested")
        require(isinstance(requested, dict) and requested.get("live_launch") is True, f"{role} was not live")
        require(requested.get("launch_memory") == "size=2G,shared=on", f"{role} memory envelope changed")
        guest_evidence = chain.get("guest_evidence")
        require(
            isinstance(guest_evidence, dict) and guest_evidence.get("observed") is True,
            f"{role} guest evidence is absent",
        )

        launch = load(proof_root / launch_relative)
        require(launch.get("schema") == "sandwurm.cloud-hypervisor-launch.v0", f"{role} launch schema mismatch")
        require(launch.get("status") == "planned", f"{role} launch plan mismatch")
        vmm = launch.get("vmm")
        require(isinstance(vmm, dict) and isinstance(vmm.get("argv"), list), f"{role} VMM argv absent")
        argv = vmm["argv"]
        tap = "vm-iotoxc" if role == "client" else "vm-iotoxd"
        require(f"tap={tap}" in argv, f"{role} VMM TAP mismatch")
        require("size=2G,shared=on" in argv and "boot=2,max=2" in argv, f"{role} VMM envelope mismatch")

    compact = manifest.get("compact_export")
    if compact is None:
        require(
            manifest.get("proof_root_contains_private_guest_disks") is True,
            "raw provider proof lost its private-disk warning",
        )
    else:
        require(isinstance(compact, dict), "compact declaration is invalid")
        require(compact.get("schema") == COMPACT_SCHEMA, "compact declaration schema mismatch")
        require(
            manifest.get("proof_root_contains_private_guest_disks") is False,
            "compact provider proof claims private disks",
        )
        export = load(proof_root / "compact-export.json")
        require(export.get("schema") == COMPACT_SCHEMA, "compact export schema mismatch")
        require(export.get("status") == "passed", "compact export did not pass")
        require(export.get("contains_secrets") is False, "compact export claims secrets")
        require(export.get("source_proof_id") == compact.get("source_proof_id"), "compact proof id mismatch")
        require(
            export.get("source_manifest_sha256") == compact.get("source_manifest_sha256"),
            "compact source manifest mismatch",
        )
        files = export.get("files")
        require(isinstance(files, dict) and set(files) == set(evidence_paths()), "compact file inventory mismatch")
        observed = {
            str(path.relative_to(proof_root))
            for path in proof_root.rglob("*")
            if path.is_file()
        }
        require(observed == set(evidence_paths()) | {"compact-export.json"}, "compact export contains undeclared files")
        for relative, expected_digest in files.items():
            path = proof_root / relative
            require(path.is_file() and not path.is_symlink(), f"compact evidence absent: {relative}")
            require(digest(path) == expected_digest, f"compact evidence digest mismatch: {relative}")

    return {
        "schema": MANIFEST_SCHEMA,
        "status": "passed",
        "route_mode": route,
        "expected_connection": connection,
        "old_provider": "0.2.22",
        "current_provider": "0.2.23",
        "compact_export": compact is not None,
        "rendezvous_monotonic_span_ns": span,
    }


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="iotox-provider-rolling-verifier-") as directory:
        root = Path(directory) / "raw"
        root.mkdir()
        receipts = {}
        chains = {}
        launches = {}
        for role in ROLES:
            provider = "0.2.22" if role == "client" else "0.2.23"
            tap = "vm-iotoxc" if role == "client" else "vm-iotoxd"
            receipt_relative = (
                f"{role}/live/workspace-export/guest-receipts/iotox/provider-rolling.json"
            )
            chain_relative = f"{role}/direct-cloud-hypervisor-live-chain.json"
            launch_relative = f"{role}/prelaunch/launch/cloud-hypervisor-launch.json"
            write_json(
                root / receipt_relative,
                {
                    "schema": RECEIPT_SCHEMA,
                    "status": "passed",
                    "role": role,
                    "route_mode": "direct-udp",
                    "expected_connection": "udp",
                    "live_provider": provider,
                    "savedata_created_by": "0.2.22",
                    "savedata_readable_by": ["0.2.22", "0.2.23"],
                    "old_source_sha256": OLD_SOURCE_SHA256,
                    "current_source_sha256": CURRENT_SOURCE_SHA256,
                    "old_binary_sha256": "1" * 64,
                    "current_binary_sha256": "2" * 64,
                    "virtualization": "kvm",
                    "sent": True,
                    "received": True,
                    "savedata_semantics_preserved": True,
                    "savedata_bytes": 4096,
                    "contains_secrets": False,
                },
            )
            write_json(
                root / chain_relative,
                {
                    "schema": "sandwurm.direct-cloud-hypervisor-live-chain.v0",
                    "status": "guest-evidence-observed",
                    "requested": {
                        "live_launch": True,
                        "launch_memory": "size=2G,shared=on",
                    },
                    "guest_evidence": {"observed": True},
                },
            )
            write_json(
                root / launch_relative,
                {
                    "schema": "sandwurm.cloud-hypervisor-launch.v0",
                    "status": "planned",
                    "vmm": {
                        "argv": [
                            "cloud-hypervisor",
                            "--memory",
                            "size=2G,shared=on",
                            "--cpus",
                            "boot=2,max=2",
                            "--net",
                            f"tap={tap}",
                        ]
                    },
                },
            )
            receipts[role] = {
                "path": receipt_relative,
                "sha256": digest(root / receipt_relative),
            }
            chains[role] = {
                "path": chain_relative,
                "sha256": digest(root / chain_relative),
            }
            launches[role] = {
                "path": launch_relative,
                "sha256": digest(root / launch_relative),
            }
        manifest = {
            "schema": MANIFEST_SCHEMA,
            "status": "passed",
            "route_mode": "direct-udp",
            "expected_connection": "udp",
            "old_provider": "0.2.22",
            "current_provider": "0.2.23",
            "client_live_provider": "0.2.22",
            "device_live_provider": "0.2.23",
            "savedata_created_by": "0.2.22",
            "simultaneous_vmm_chains_observed": True,
            "prepared_bridge": "sandwurm-vm",
            "bootstrap_fixture": "pinned-host-bridge-c-toxcore-0.2.23",
            "rendezvous_monotonic_span_ns": 1,
            "taps": [
                {"name": "vm-iotoxc", "master": "sandwurm-vm", "operstate": "UNKNOWN"},
                {"name": "vm-iotoxd", "master": "sandwurm-vm", "operstate": "UNKNOWN"},
            ],
            "receipts": receipts,
            "chains": chains,
            "launches": launches,
            "proof_root_contains_private_guest_disks": True,
            "receipts_contain_secrets": False,
            "compact_export": None,
        }
        write_json(root / MANIFEST_NAME, manifest)
        verify(root, "direct-udp")

        client_receipt_path = root / receipts["client"]["path"]
        client_receipt = load(client_receipt_path)
        client_receipt["received"] = False
        write_json(client_receipt_path, client_receipt)
        try:
            verify(root, "direct-udp")
        except RuntimeError as error:
            require(
                "receipt digest mismatch" in str(error),
                "tamper negative failed for an unexpected reason",
            )
        else:
            raise RuntimeError("provider verifier accepted a tampered receipt")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("proof_root", nargs="?", type=Path)
    parser.add_argument("--route", choices=tuple(ROUTES))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        require(args.proof_root is None and args.route is None, "self-test takes no proof arguments")
        self_test()
        print("sandwurm-provider-rolling verifier self-test: PASS")
        return 0
    require(args.proof_root is not None, "proof root is required")
    print(json.dumps(verify(args.proof_root, args.route), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as error:
        print(f"provider rolling proof refused: {error}", file=sys.stderr)
        raise SystemExit(1)
