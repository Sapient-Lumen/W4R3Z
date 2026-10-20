#!/usr/bin/env python3
"""Export a minimal independently replayable metadata-corruption proof."""

from __future__ import annotations

import argparse
import ctypes
import errno
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parent.parent
EXPORT_ROOT = ROOT / ".sandwurm/exports/sync-metadata-corruption"
SCHEMA = "iotox.sync-metadata-corruption-sandwurm-compact-export.v1"
MAX_SOURCE_BYTES = 2 * 1024 * 1024
EVIDENCE = (
    "direct-cloud-hypervisor-live-chain.json",
    "prelaunch/launch/cloud-hypervisor-launch.json",
    "live/cloud-hypervisor-launch.json",
    "live/workspace-export/guest-receipts/iotox/vm-smoke.json",
    "live/workspace-export/guest-receipts/iotox/sync-metadata-corruption.json",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def run_verifier(root: Path) -> None:
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools/verify-sync-metadata-corruption-sandwurm.py"),
            str(root),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
    )


def canonical_json(value: dict[str, object]) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def network_device_present(value: dict[str, object]) -> bool:
    vmm = value.get("vmm")
    require(isinstance(vmm, dict), "launch VMM evidence is absent")
    argv = vmm.get("argv")
    require(
        isinstance(argv, list) and all(isinstance(item, str) for item in argv),
        "launch VMM argv is invalid",
    )
    return any(item == "--net" or item.startswith("--net=") for item in argv)


def compact_payloads(source: Path) -> dict[str, bytes]:
    chain = json.loads((source / EVIDENCE[0]).read_text(encoding="utf-8"))
    prelaunch = json.loads((source / EVIDENCE[1]).read_text(encoding="utf-8"))
    live = json.loads((source / EVIDENCE[2]).read_text(encoding="utf-8"))
    chain_summary = {
        "schema": "iotox.sync-metadata-corruption-chain-summary.v1",
        "status": chain["status"],
        "prelaunch_chain_status":
            chain["receipts"]["prelaunch_chain"]["status"],
        "live_launch_status": chain["receipts"]["live_launch"]["status"],
        "guest_evidence_observed": chain["guest_evidence"]["observed"],
        "contains_secrets": False,
    }
    prelaunch_summary = {
        "schema": "iotox.sync-metadata-corruption-launch-summary.v1",
        "status": prelaunch["status"],
        "network_class": prelaunch["network"]["class"],
        "network_mode": prelaunch["network"]["mode"],
        "network_device_present": network_device_present(prelaunch),
        "contains_secrets": False,
    }
    live_summary = {
        "schema": "iotox.sync-metadata-corruption-launch-summary.v1",
        "status": live["status"],
        "network_class": live["network"]["class"],
        "network_mode": live["network"]["mode"],
        "network_device_present": network_device_present(live),
        "vm_substrate": live["guest_boundary"]["vm_substrate"],
        "guest_boundary_observed": live["guest_boundary"]["observed"],
        "process_observed": live["vmm"]["process_observed"],
        "exit_observed": live["vmm"]["exit_observed"],
        "exit_status": live["vmm"]["exit_status"],
        "exit_control_observed": live["ch_remote"]["exit_control_observed"],
        "contains_secrets": False,
    }
    return {
        EVIDENCE[0]: canonical_json(chain_summary),
        EVIDENCE[1]: canonical_json(prelaunch_summary),
        EVIDENCE[2]: canonical_json(live_summary),
        EVIDENCE[3]: (source / EVIDENCE[3]).read_bytes(),
        EVIDENCE[4]: (source / EVIDENCE[4]).read_bytes(),
    }


def write_durable_private(path: Path, value: bytes) -> None:
    descriptor = os.open(
        path,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW,
        0o600,
    )
    try:
        offset = 0
        while offset < len(value):
            count = os.write(descriptor, value[offset:])
            require(count > 0, "compact evidence write made no progress")
            offset += count
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def rename_noreplace(source: Path, destination: Path) -> None:
    libc = ctypes.CDLL(None, use_errno=True)
    renameat2 = getattr(libc, "renameat2", None)
    require(renameat2 is not None, "renameat2 is unavailable")
    renameat2.argtypes = [
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_uint,
    ]
    renameat2.restype = ctypes.c_int
    if renameat2(
        -100, os.fsencode(source), -100, os.fsencode(destination), 1
    ) != 0:
        error = ctypes.get_errno()
        if error == errno.EEXIST:
            raise FileExistsError(error, "destination already exists", destination)
        raise OSError(error, os.strerror(error), destination)


def export(source: Path, destination: Path) -> dict[str, object]:
    require(not source.is_symlink(), "proof root is a symlink")
    source = source.resolve()
    destination = destination.resolve()
    require(source.is_dir(), "proof root is not a directory")
    require(
        not destination.exists() and not destination.is_symlink(),
        "destination already exists",
    )
    require(source != destination, "source and destination are identical")
    require(
        source not in destination.parents and destination not in source.parents,
        "source and destination may not contain one another",
    )
    run_verifier(source)
    payloads = compact_payloads(source)
    records: list[dict[str, object]] = []
    total_bytes = 0
    for relative in EVIDENCE:
        path = source / relative
        require(path.is_file() and not path.is_symlink(), f"unsafe evidence: {relative}")
        require(path.resolve(strict=True).is_relative_to(source),
                f"evidence escaped proof root: {relative}")
        value = payloads[relative]
        size = len(value)
        require(size > 0, f"empty compact evidence: {relative}")
        total_bytes += size
        records.append(
            {
                "path": relative,
                "bytes": size,
                "sha256": hashlib.sha256(value).hexdigest(),
            }
        )
    require(total_bytes <= MAX_SOURCE_BYTES, "compact evidence exceeds 2 MiB")

    destination.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    temporary = Path(
        tempfile.mkdtemp(prefix=f".{destination.name}.part-", dir=destination.parent)
    )
    try:
        temporary.chmod(0o700)
        for record in records:
            relative = str(record["path"])
            target = temporary / relative
            target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            write_durable_private(target, payloads[relative])
            require(
                target.stat().st_size == record["bytes"]
                and sha256(target) == record["sha256"],
                f"evidence changed during export: {relative}",
            )
        manifest = {
            "schema": SCHEMA,
            "status": "passed",
            "source_proof_root_sha256":
                hashlib.sha256(str(source).encode("utf-8")).hexdigest(),
            "file_count": len(records),
            "total_bytes": total_bytes,
            "files": records,
            "contains_secrets": False,
        }
        manifest_path = temporary / "compact-export.json"
        write_durable_private(manifest_path, canonical_json(manifest))
        directories = {temporary}
        for relative in EVIDENCE:
            current = (temporary / relative).parent
            while current != temporary:
                directories.add(current)
                current = current.parent
        for directory in sorted(
            directories, key=lambda value: len(value.parts), reverse=True
        ):
            fsync_directory(directory)
        run_verifier(temporary)
        rename_noreplace(temporary, destination)
        fsync_directory(destination.parent)
        return {
            **manifest,
            "proof_root": str(destination),
            "manifest_sha256": sha256(destination / "compact-export.json"),
        }
    except BaseException:
        shutil.rmtree(temporary, ignore_errors=True)
        raise


def load_verifier() -> object:
    path = ROOT / "tools/verify-sync-metadata-corruption-sandwurm.py"
    spec = importlib.util.spec_from_file_location("iotox_metadata_verify", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load metadata corruption verifier")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def self_test() -> None:
    verifier = load_verifier()
    with tempfile.TemporaryDirectory(prefix="iotox-metadata-export-") as raw:
        root = Path(raw)
        source = root / "source"
        destination = root / "compact"
        verifier.fixture(source)
        live_path = source / EVIDENCE[2]
        live = json.loads(live_path.read_text(encoding="utf-8"))
        live["vmm"]["secret"] = "sentinel-private-value"
        live_path.write_text(json.dumps(live) + "\n", encoding="utf-8")
        result = export(source, destination)
        require(result["file_count"] == len(EVIDENCE), "export omitted evidence")
        require(verifier.verify(destination)["status"] == "passed",
                "compact proof did not replay")
        require(
            b"sentinel-private-value"
            not in (destination / EVIDENCE[2]).read_bytes(),
            "compact launch summary retained an unknown nested field",
        )
        source_v1 = root / "source-v1"
        destination_v1 = root / "compact-v1"
        verifier.fixture(source_v1, verifier.RECEIPT_V1)
        export(source_v1, destination_v1)
        v1_summary = verifier.verify(destination_v1)
        require(
            v1_summary["status"] == "passed"
            and v1_summary["receipt_schema"] == verifier.RECEIPT_V1
            and v1_summary["simultaneous_receipt_verified"] is False,
            "accepted v1 raw-to-compact replay failed",
        )
        receipt = destination / EVIDENCE[-1]
        value = json.loads(receipt.read_text(encoding="utf-8"))
        value["power_cut"] = True
        receipt.write_text(json.dumps(value) + "\n", encoding="utf-8")
        try:
            verifier.verify(destination)
        except ValueError:
            pass
        else:
            raise RuntimeError("tampered compact proof passed")
    print("sync-metadata-corruption-sandwurm-exporter-self-test=pass")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("proof_root", nargs="?", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    require(args.proof_root is not None, "proof root is required")
    destination = args.output or (EXPORT_ROOT / args.proof_root.resolve().name)
    print(json.dumps(export(args.proof_root, destination), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, subprocess.SubprocessError) as error:
        print(f"metadata corruption export failed: {error}", file=sys.stderr)
        raise SystemExit(1)
