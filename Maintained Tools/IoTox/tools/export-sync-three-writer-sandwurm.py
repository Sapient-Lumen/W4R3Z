#!/usr/bin/env python3
"""Export the minimal independently verifiable three-writer VM proof."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
EXPORT_ROOT = ROOT / ".sandwurm" / "exports" / "three-writer"
SCHEMA = "iotox.sync-three-writer-sandwurm-compact-export.v1"
MAX_SOURCE_BYTES = 2 * 1024 * 1024
VM_SMOKE_RELATIVE = "live/workspace-export/guest-receipts/iotox/vm-smoke.json"
SYNC_RECEIPT_RELATIVE = "live/workspace-export/guest-receipts/iotox/sync-three-writer.json"
PASSED_EVIDENCE_PATHS = (
    "direct-cloud-hypervisor-live-chain.json",
    "prelaunch/launch/cloud-hypervisor-launch.json",
    "live/cloud-hypervisor-launch.json",
    VM_SMOKE_RELATIVE,
    SYNC_RECEIPT_RELATIVE,
)
REJECTED_EVIDENCE_PATHS = (
    "direct-cloud-hypervisor-live-chain.json",
    "prelaunch/launch/cloud-hypervisor-launch.json",
    "live/cloud-hypervisor-launch.json",
    SYNC_RECEIPT_RELATIVE,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as source:
        result = json.load(source)
    require(isinstance(result, dict), f"JSON root is not an object: {path}")
    return result


def sync_receipt_status(proof_root: Path) -> str:
    receipt = load_json(proof_root / SYNC_RECEIPT_RELATIVE)
    require(receipt.get("schema") == "iotox.sync-three-writer.v1", "bad sync receipt schema")
    status = receipt.get("status")
    require(status in ("passed", "rejected"), "unsupported sync receipt status")
    require(receipt.get("contains_secrets") is False, "sync receipt is not content-free")
    return str(status)


def evidence_paths_for_status(status: str) -> tuple[str, ...]:
    if status == "passed":
        return PASSED_EVIDENCE_PATHS
    if status == "rejected":
        return REJECTED_EVIDENCE_PATHS
    raise RuntimeError(f"unsupported sync receipt status: {status}")


def run_verifiers(proof_root: Path, status: str) -> None:
    if status == "passed":
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools" / "verify-sandwurm-vm-smoke.py"),
                str(proof_root),
                "device",
            ],
            check=True,
            stdout=subprocess.DEVNULL,
        )
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "verify-sync-three-writer-sandwurm.py"),
            str(proof_root),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
    )


def export(source: Path, destination: Path) -> dict:
    source = source.resolve()
    destination = destination.resolve()
    require(source.is_dir(), "proof root is not a directory")
    require(source != destination, "source and destination are identical")
    require(not destination.exists(), "destination already exists")
    require(
        source not in destination.parents and destination not in source.parents,
        "source and destination may not contain one another",
    )

    status = sync_receipt_status(source)
    evidence_paths = evidence_paths_for_status(status)
    files: list[dict] = []
    total_bytes = 0
    for relative in evidence_paths:
        path = source / relative
        require(path.is_file() and not path.is_symlink(), f"unsafe or absent evidence: {relative}")
        require(
            path.resolve(strict=True).is_relative_to(source),
            f"evidence escaped the proof root: {relative}",
        )
        size = path.stat().st_size
        require(size > 0, f"empty evidence: {relative}")
        total_bytes += size
        files.append({"path": relative, "bytes": size, "sha256": sha256(path)})
    require(total_bytes <= MAX_SOURCE_BYTES, "compact evidence exceeds the 2 MiB bound")
    run_verifiers(source, status)

    destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temporary = Path(
        tempfile.mkdtemp(prefix=f".{destination.name}.part-", dir=destination.parent)
    )
    try:
        temporary.chmod(0o700)
        for record in files:
            relative = record["path"]
            target = temporary / relative
            target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            target.write_bytes((source / relative).read_bytes())
            target.chmod(0o600)
            require(
                target.stat().st_size == record["bytes"]
                and sha256(target) == record["sha256"],
                f"evidence changed during export: {relative}",
            )
        manifest = {
            "schema": SCHEMA,
            "status": status,
            "source_proof_root": str(source),
            "file_count": len(files),
            "total_bytes": total_bytes,
            "files": files,
            "contains_secrets": False,
        }
        manifest_path = temporary / "compact-export.json"
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        manifest_path.chmod(0o600)
        run_verifiers(temporary, status)
        os.replace(temporary, destination)
        return {
            **manifest,
            "proof_root": str(destination),
            "manifest_sha256": sha256(destination / "compact-export.json"),
        }
    except BaseException:
        shutil.rmtree(temporary, ignore_errors=True)
        raise


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value) + "\n", encoding="utf-8")


def self_test() -> None:
    revision = (ROOT / "REVISION").read_text(encoding="utf-8").strip()
    version_header = (ROOT / "include" / "iotox" / "version.hpp").read_text(
        encoding="utf-8"
    )
    version = version_header.split('kVersion = "', 1)[1].split('"', 1)[0]
    with tempfile.TemporaryDirectory(prefix="iotox-three-writer-exporter-") as raw:
        base = Path(raw)
        source = base / "raw"
        output = base / "compact"
        write_json(
            source / PASSED_EVIDENCE_PATHS[0],
            {
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
        )
        write_json(
            source / PASSED_EVIDENCE_PATHS[1],
            {
                "status": "planned",
                "network": {"class": "none", "mode": "none"},
                "vmm": {"argv": ["cloud-hypervisor", "--cpus", "boot=2,max=2"]},
            },
        )
        write_json(
            source / PASSED_EVIDENCE_PATHS[2],
            {
                "status": "exited",
                "guest_boundary": {
                    "observed": True,
                    "vm_substrate": "cloud-hypervisor",
                },
            },
        )
        write_json(
            source / VM_SMOKE_RELATIVE,
            {
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
        )
        write_json(
            source / SYNC_RECEIPT_RELATIVE,
            {
                "schema": "iotox.sync-three-writer.v1",
                "status": "passed",
                "namespace_sha256": "31" * 32,
                "node_count": 3,
                "friendship_edge_count": 3,
                "directed_read_write_share_count": 6,
                "source_principals_per_node": 2,
                "branch_count_per_node": [3, 3, 3],
                "three_way_conflict_observed": True,
                "conflict_alternatives_per_node": [2, 2, 2],
                "explicit_resolution_observed": True,
                "resolved_sha256": "41" * 32,
                "automation_record_format": 2,
                "automation_record_bytes": 4808,
                "periodic_attempts_per_node": [2, 3, 4],
                "tox_key_sha256": ["01" * 32, "02" * 32, "03" * 32],
                "principal_sha256": ["11" * 32, "12" * 32, "13" * 32],
                "elapsed_ms": 1,
                "state_reused": False,
                "shadow_cycles": 0,
                "shadow_elapsed_ms": 0,
                "stalled_cycle_restarts": 0,
                "stalled_cycle_restart_events": [],
                "maintenance_lifecycle": False,
                "contains_secrets": False,
            },
        )
        result = export(source, output)
        require(result["file_count"] == len(PASSED_EVIDENCE_PATHS), "wrong compact file count")
        require(result["status"] == "passed", "passed compact status is wrong")
        require((output / "compact-export.json").is_file(), "manifest is absent")
        try:
            export(source, output)
        except RuntimeError as error:
            require("already exists" in str(error), "overwrite failed for wrong reason")
        else:
            raise RuntimeError("exporter overwrote an existing proof")

        rejected_source = base / "rejected-raw"
        rejected_output = base / "rejected-compact"
        write_json(
            rejected_source / REJECTED_EVIDENCE_PATHS[0],
            {
                "schema": "sandwurm.direct-cloud-hypervisor-live-chain.v0",
                "status": "launched-without-guest-evidence",
                "failure": {"blockers": ["guest-evidence-not-observed"]},
                "receipts": {"live_launch": {"status": "exited"}},
            },
        )
        write_json(
            rejected_source / REJECTED_EVIDENCE_PATHS[1],
            {
                "status": "planned",
                "network": {"class": "none", "mode": "none"},
                "vmm": {"argv": ["cloud-hypervisor", "--cpus", "boot=2,max=2"]},
            },
        )
        write_json(
            rejected_source / REJECTED_EVIDENCE_PATHS[2],
            {"status": "exited"},
        )
        failure = "timeout waiting for capacity population on all three writers"
        write_json(
            rejected_source / SYNC_RECEIPT_RELATIVE,
            {
                "schema": "iotox.sync-three-writer.v1",
                "status": "rejected",
                "failure": failure,
                "failure_sha256": hashlib.sha256(failure.encode("utf-8")).hexdigest(),
                "namespace_sha256": "31" * 32,
                "node_count": 3,
                "elapsed_ms": 1800001,
                "state_reused": False,
                "tree_lane_cap": 32,
                "tree_lane_process_cap": 32,
                "tree_lane_namespace_cap": 32,
                "capacity_campaign": True,
                "capacity_files": 3500,
                "capacity_file_bytes": 16384,
                "capacity_logical_bytes": 3500 * 16384,
                "partial_agent_high_water_kib": [1000, 1100, 1200],
                "partial_branch_count_per_node": [3, 3, 3],
                "partial_capacity_shape_per_node": [
                    {"files": 3500, "bytes": 3500 * 16384},
                    {"files": 132, "bytes": 132 * 16384},
                    {"files": 158, "bytes": 158 * 16384},
                ],
                "partial_conflict_alternatives_per_node": [0, 0, 0],
                "partial_tree_v2_store_shape_per_node": [
                    {
                        "branch_bytes": 984,
                        "branches": 3,
                        "incoming_bytes": 0,
                        "incoming_files": 0,
                        "manifest_bytes": 378524,
                        "manifests": 4,
                        "object_bytes": 57344016,
                        "objects": 3501,
                        "record_bytes": 1240,
                        "records": 4,
                    },
                    {
                        "branch_bytes": 768,
                        "branches": 3,
                        "incoming_bytes": 0,
                        "incoming_files": 0,
                        "manifest_bytes": 324,
                        "manifests": 3,
                        "object_bytes": 2146320,
                        "objects": 132,
                        "record_bytes": 768,
                        "records": 3,
                    },
                    {
                        "branch_bytes": 768,
                        "branches": 3,
                        "incoming_bytes": 0,
                        "incoming_files": 0,
                        "manifest_bytes": 324,
                        "manifests": 3,
                        "object_bytes": 2572304,
                        "objects": 158,
                        "record_bytes": 768,
                        "records": 3,
                    },
                ],
                "shadow_cycles": 0,
                "maintenance_lifecycle_requested": False,
                "stage_events": [
                    {"elapsed_ms": 0, "message": "starting private bootstrap and three agents"},
                    {"elapsed_ms": 2146, "message": "namespace maximum-lanes override applied: 32"},
                    {"elapsed_ms": 18315, "message": "three friendship edges confirmed"},
                    {"elapsed_ms": 22533, "message": "three signed branches converged"},
                ],
                "contains_secrets": False,
            },
        )
        rejected_result = export(rejected_source, rejected_output)
        require(
            rejected_result["file_count"] == len(REJECTED_EVIDENCE_PATHS),
            "wrong rejected compact file count",
        )
        require(rejected_result["status"] == "rejected", "rejected compact status is wrong")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("proof_root", nargs="?", type=Path)
    parser.add_argument("output", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        require(args.proof_root is None and args.output is None, "self-test accepts no paths")
        self_test()
        print("sync-three-writer Sandwurm exporter self-test: PASS")
        return 0
    require(args.proof_root is not None, "proof_root is required")
    destination = args.output or EXPORT_ROOT / args.proof_root.name
    print(json.dumps(export(args.proof_root, destination), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"three-writer evidence export refused: {error}", file=sys.stderr)
        raise SystemExit(1)
