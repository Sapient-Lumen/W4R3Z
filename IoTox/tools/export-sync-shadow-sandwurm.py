#!/usr/bin/env python3
"""Export the minimal independently verifiable IoTox/Resilio VM proof."""

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
EXPORT_ROOT = ROOT / ".sandwurm" / "exports" / "sync-shadow"
SCHEMA = "iotox.sync-shadow-sandwurm-compact-export.v1"
MAX_SOURCE_BYTES = 2 * 1024 * 1024
EVIDENCE_PATHS = (
    "direct-cloud-hypervisor-live-chain.json",
    "prelaunch/launch/cloud-hypervisor-launch.json",
    "live/cloud-hypervisor-launch.json",
    "live/workspace-export/guest-receipts/iotox/vm-smoke.json",
    "live/workspace-export/guest-receipts/iotox/sync-shadow.json",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            checksum.update(block)
    return checksum.hexdigest()


def verify(proof_root: Path) -> None:
    subprocess.run(
        [sys.executable, str(ROOT / "tools/verify-sandwurm-vm-smoke.py"),
         str(proof_root), "device"],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    subprocess.run(
        [sys.executable,
         str(ROOT / "tools/verify-sync-shadow-sandwurm.py"),
         str(proof_root)],
        check=True,
        stdout=subprocess.DEVNULL,
    )


def export(source: Path, destination: Path) -> dict:
    source = source.resolve()
    destination = destination.resolve()
    require(source.is_dir() and not source.is_symlink(),
            "proof root is not a safe directory")
    require(not destination.exists(), "destination already exists")
    require(source != destination, "source and destination are identical")
    require(source not in destination.parents and destination not in source.parents,
            "source and destination may not contain one another")
    files = []
    total_bytes = 0
    for relative in EVIDENCE_PATHS:
        path = source / relative
        require(path.is_file() and not path.is_symlink(),
                f"unsafe or absent evidence: {relative}")
        require(path.resolve(strict=True).is_relative_to(source),
                f"evidence escaped its proof root: {relative}")
        size = path.stat().st_size
        require(size > 0, f"empty evidence: {relative}")
        total_bytes += size
        files.append({"path": relative, "bytes": size, "sha256": sha256(path)})
    require(total_bytes <= MAX_SOURCE_BYTES,
            "compact evidence exceeds the 2 MiB bound")
    verify(source)

    destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temporary = Path(tempfile.mkdtemp(
        prefix=f".{destination.name}.part-", dir=destination.parent))
    try:
        temporary.chmod(0o700)
        for record in files:
            relative = record["path"]
            target = temporary / relative
            target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            shutil.copyfile(source / relative, target)
            target.chmod(0o600)
            require(
                target.stat().st_size == record["bytes"]
                and sha256(target) == record["sha256"],
                f"evidence changed during export: {relative}",
            )
        manifest = {
            "schema": SCHEMA,
            "status": "passed",
            "source_proof_root": str(source),
            "file_count": len(files),
            "total_bytes": total_bytes,
            "files": files,
            "source_private_artifacts_omitted": [
                "guest-disk", "runtime-state", "tox-keys", "resilio-secrets",
                "directory-content",
            ],
            "contains_secrets": False,
        }
        manifest_path = temporary / "compact-export.json"
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        manifest_path.chmod(0o600)
        verify(temporary)
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
    header = (ROOT / "include/iotox/version.hpp").read_text(encoding="utf-8")
    version = header.split('kVersion = "', 1)[1].split('"', 1)[0]
    with tempfile.TemporaryDirectory(prefix="iotox-shadow-exporter-") as raw:
        base = Path(raw)
        source = base / "raw"
        output = base / "compact"
        write_json(
            source / EVIDENCE_PATHS[0],
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
            source / EVIDENCE_PATHS[1],
            {
                "status": "planned",
                "network": {"class": "none", "mode": "none"},
                "vmm": {"argv": ["cloud-hypervisor", "--cpus", "boot=2,max=2"]},
            },
        )
        write_json(
            source / EVIDENCE_PATHS[2],
            {
                "status": "exited",
                "guest_boundary": {
                    "observed": True,
                    "vm_substrate": "cloud-hypervisor",
                },
            },
        )
        write_json(
            source / EVIDENCE_PATHS[3],
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
            source / EVIDENCE_PATHS[4],
            {
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
                "canonical_manifest_sha256": "1" * 64,
                "canonical_files": 24,
                "canonical_bytes": 65536,
                "resilio_binary_sha256": "2" * 64,
                "resilio_version_output_sha256": "3" * 64,
                "iotox_binary_sha256": "4" * 64,
                "node_count": 2,
                "manual_publish_pull_activate_commands": 0,
                "contains_secrets": False,
            },
        )
        result = export(source, output)
        require(result["file_count"] == 5, "wrong compact file count")
        require((output / "compact-export.json").is_file(), "manifest is absent")
        try:
            export(source, output)
        except RuntimeError as error:
            require("already exists" in str(error),
                    "overwrite failed for wrong reason")
        else:
            raise RuntimeError("exporter overwrote an existing proof")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("proof_root", nargs="?", type=Path)
    parser.add_argument("output", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        require(args.proof_root is None and args.output is None,
                "self-test accepts no paths")
        self_test()
        print("sync-shadow Sandwurm exporter self-test: PASS")
        return 0
    require(args.proof_root is not None, "proof_root is required")
    destination = args.output or EXPORT_ROOT / args.proof_root.name
    print(json.dumps(export(args.proof_root, destination), indent=2,
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"sync-shadow evidence export refused: {error}", file=sys.stderr)
        raise SystemExit(1)
