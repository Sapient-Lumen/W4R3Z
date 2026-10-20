#!/usr/bin/env python3
"""Run the same-host dishonest-storage matrix across ext4 and btrfs."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_STATE_ROOT = ROOT / ".sandwurm/lab/sync-dishonest-storage"
DEFAULT_EXPORT_ROOT = ROOT / ".sandwurm/exports/sync-dishonest-storage"
RUN_ID = re.compile(r"^run\.[A-Za-z0-9_]{8}$")
SCHEMA = "iotox.sync-dishonest-storage-matrix.v1"
FILESYSTEMS = ("ext4", "btrfs")
SCENARIOS = (
    "valid-old-rollback",
    "cross-family-rollback",
    "torn-record",
    "flakey-drop-writes",
)
FAMILIES = (
    "branch-pointer",
    "immutable-branch-record",
    "manifest",
    "workspace",
    "maintenance",
    "projection-marker",
)
FAMILY_PATHS = {
    "branch-pointer": Path("tree-v2/branches/current.branch.json"),
    "immutable-branch-record": Path("tree-v2/records/current.branch-record.json"),
    "manifest": Path("tree-v2/manifests/current.manifest.json"),
    "workspace": Path("tree-v2/workspaces/current.workspace.json"),
    "maintenance": Path("tree-v2/maintenance/current.maintenance.json"),
    "projection-marker": Path("tree-v2/projection/current.marker.json"),
}


class MatrixError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise MatrixError(message)


def run(argv: list[str], *, capture_output: bool = False, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, check=True, text=True, capture_output=capture_output, input=input_text)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def random_run_id() -> str:
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
    return "run." + "".join(secrets.choice(alphabet) for _ in range(8))


def validate_under(path: Path, parent: Path, label: str) -> Path:
    resolved = path.resolve()
    allowed = parent.resolve()
    require(resolved == allowed or resolved.is_relative_to(allowed), f"{label} must be under {parent}")
    require(not resolved.is_symlink(), f"{label} may not be a symlink")
    return resolved


def target_present(name: str) -> bool:
    result = subprocess.run(["sudo", "dmsetup", "targets"], check=False, text=True, capture_output=True)
    return result.returncode == 0 and any(line.split(maxsplit=1)[0] == name for line in result.stdout.splitlines())


def losetup(image: Path) -> str:
    result = run(["sudo", "losetup", "--find", "--show", str(image)], capture_output=True)
    device = result.stdout.strip()
    require(device.startswith("/dev/loop"), "losetup did not return a loop device")
    return device


def detach_loop(device: str | None) -> None:
    if device:
        subprocess.run(["sudo", "losetup", "-d", device], check=False)


def dm_exists(name: str) -> bool:
    result = subprocess.run(
        ["sudo", "dmsetup", "info", name],
        check=False,
        text=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def dm_remove(name: str | None, *, strict: bool = False) -> None:
    if name:
        result = subprocess.run(["sudo", "dmsetup", "remove", name], check=False)
        if result.returncode != 0:
            subprocess.run(["sudo", "dmsetup", "remove", "--deferred", name], check=False)
        for _ in range(50):
            if not dm_exists(name):
                return
            time.sleep(0.1)
        if strict:
            raise MatrixError(f"device-mapper node remained busy: {name}")


def mount(device: str, target: Path, options: str) -> None:
    run(["sudo", "mount", "-o", options, device, str(target)])


def umount(target: Path) -> None:
    run(["sudo", "umount", str(target)])


def cleanup_umount(target: Path) -> None:
    subprocess.run(["sudo", "umount", str(target)], check=False)


def block_sectors(device: str) -> int:
    return int(run(["sudo", "blockdev", "--getsz", device], capture_output=True).stdout.strip())


def dm_name(run_id: str, index: int, kind: str) -> str:
    safe = "".join(character.lower() if character.isalnum() else "_" for character in run_id.removeprefix("run."))
    return f"iotox_dst_{safe}_{index}_{kind}"


def create_snapshot(name: str, origin_device: str, cow_device: str) -> str:
    table = f"0 {block_sectors(origin_device)} snapshot {origin_device} {cow_device} P 8\n"
    run(["sudo", "dmsetup", "create", name], input_text=table)
    path = f"/dev/mapper/{name}"
    require(Path(path).exists(), "snapshot mapper device was not created")
    return path


def create_flakey_drop_writes(name: str, origin_device: str) -> str:
    table = f"0 {block_sectors(origin_device)} flakey {origin_device} 0 1 3600 1 drop_writes\n"
    run(["sudo", "dmsetup", "create", name], input_text=table)
    path = f"/dev/mapper/{name}"
    require(Path(path).exists(), "flakey mapper device was not created")
    time.sleep(1.2)
    return path


def fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def record_for(run_id: str, filesystem: str, scenario: str, family: str, generation: int) -> dict[str, Any]:
    payload = {
        "run_id": run_id,
        "filesystem": filesystem,
        "scenario": scenario,
        "family": family,
        "generation": generation,
        "payload_label": f"content-free-{family}-generation-{generation}",
    }
    return {
        "schema": "iotox.sync-dishonest-storage-record.v2",
        "family": family,
        "generation": generation,
        "parent_generation": None if generation == 1 else generation - 1,
        "payload_sha256": sha256_text(canonical_json(payload)),
    }


def atomic_write(path: Path, data: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        os.write(descriptor, data)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    os.replace(temporary, path)
    fsync_directory(path.parent)
    return sha256_bytes(data)


def write_family(root: Path, run_id: str, filesystem: str, scenario: str, family: str, generation: int) -> str:
    payload = json.dumps(record_for(run_id, filesystem, scenario, family, generation), indent=2, sort_keys=True).encode("utf-8") + b"\n"
    return atomic_write(root / FAMILY_PATHS[family], payload)


def write_generation(root: Path, run_id: str, filesystem: str, scenario: str, generation: int, families: tuple[str, ...] = FAMILIES) -> dict[str, str]:
    digests = {}
    for family in families:
        digests[family] = write_family(root, run_id, filesystem, scenario, family, generation)
    fsync_directory(root / "tree-v2")
    os.sync()
    return digests


def write_torn_family(root: Path, run_id: str, filesystem: str, scenario: str, family: str) -> str:
    payload = json.dumps(record_for(run_id, filesystem, scenario, family, 2), indent=2, sort_keys=True).encode("utf-8") + b"\n"
    torn = payload[: max(16, len(payload) // 2)]
    return atomic_write(root / FAMILY_PATHS[family], torn)


def observe_family(root: Path, family: str) -> dict[str, Any]:
    path = root / FAMILY_PATHS[family]
    if not path.exists():
        return {
            "family": family,
            "parse_status": "missing",
            "generation": None,
            "bytes_sha256": "0" * 64,
        }
    data = path.read_bytes()
    digest = sha256_bytes(data)
    try:
        record = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {
            "family": family,
            "parse_status": "invalid-json",
            "generation": None,
            "bytes_sha256": digest,
        }
    if not isinstance(record, dict) or record.get("family") != family or not isinstance(record.get("generation"), int):
        return {
            "family": family,
            "parse_status": "invalid-record",
            "generation": None,
            "bytes_sha256": digest,
        }
    return {
        "family": family,
        "parse_status": "valid",
        "generation": record["generation"],
        "bytes_sha256": digest,
    }


def observe_state(root: Path) -> dict[str, dict[str, Any]]:
    return {family: observe_family(root, family) for family in FAMILIES}


def state_digest(state: dict[str, dict[str, Any]]) -> str:
    return sha256_text(canonical_json(state))


def chown_mount(root: Path) -> None:
    run(["sudo", "chown", f"{os.getuid()}:{os.getgid()}", str(root)])


def make_image(path: Path, size_mib: int, filesystem: str) -> None:
    with path.open("wb") as handle:
        handle.truncate(size_mib * 1024 * 1024)
    path.chmod(0o600)
    if filesystem == "ext4":
        run(["mkfs.ext4", "-q", "-F", str(path)])
    elif filesystem == "btrfs":
        run(["mkfs.btrfs", "-q", "-f", str(path)])
    else:
        raise MatrixError(f"unsupported filesystem: {filesystem}")


def cold_options(filesystem: str) -> str:
    return "ro,nosuid,nodev,noatime,noload" if filesystem == "ext4" else "ro,nosuid,nodev,noatime"


def mount_options() -> str:
    return "rw,nosuid,nodev,noatime"


def mount_under(root: Path) -> bool:
    root = root.resolve()
    try:
        lines = Path("/proc/self/mountinfo").read_text(encoding="utf-8").splitlines()
    except OSError:
        return True
    for line in lines:
        fields = line.split()
        if len(fields) < 5:
            continue
        mountpoint = Path(fields[4].replace("\\040", " ")).resolve()
        if mountpoint == root or mountpoint.is_relative_to(root):
            return True
    return False


def remove_raw_root(raw_root: Path, state_root: Path) -> None:
    raw_root = raw_root.resolve()
    state_root = state_root.resolve()
    require(raw_root.parent == state_root, "raw root is not an immediate child")
    require(RUN_ID.fullmatch(raw_root.name) is not None, "raw root has bad name")
    require(raw_root.is_dir() and not raw_root.is_symlink(), "raw root is unsafe")
    require(not mount_under(raw_root), "raw root still contains a mount")
    shutil.rmtree(raw_root)


def git_revision() -> str:
    result = subprocess.run(["git", "-c", f"safe.directory={ROOT}", "-C", str(ROOT), "rev-parse", "HEAD"], check=False, text=True, capture_output=True)
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def load_verifier():
    verifier = ROOT / "tools/verify-sync-dishonest-storage-matrix.py"
    spec = importlib.util.spec_from_file_location("iotox_dishonest_storage_matrix_verify", verifier)
    require(spec is not None and spec.loader is not None, "unable to load matrix verifier")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def family_results(base: dict[str, dict[str, Any]], acknowledged: dict[str, dict[str, Any]], cold: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "family": family,
            "base_generation": base[family]["generation"],
            "acknowledged_generation": acknowledged[family]["generation"],
            "cold_generation": cold[family]["generation"],
            "base_parse_status": base[family]["parse_status"],
            "acknowledged_parse_status": acknowledged[family]["parse_status"],
            "cold_parse_status": cold[family]["parse_status"],
            "base_bytes_sha256": base[family]["bytes_sha256"],
            "acknowledged_bytes_sha256": acknowledged[family]["bytes_sha256"],
            "cold_bytes_sha256": cold[family]["bytes_sha256"],
        }
        for family in FAMILIES
    ]


def run_cell(
    *,
    run_id: str,
    raw_root: Path,
    cell_index: int,
    filesystem: str,
    scenario: str,
    origin_size_mib: int,
    cow_size_mib: int,
    keep_raw: bool,
) -> dict[str, Any]:
    cell_root = raw_root / f"cell-{cell_index:02d}-{filesystem}-{scenario}"
    cell_root.mkdir(mode=0o700)
    origin_image = cell_root / f"origin.{filesystem}.img"
    cow_image = cell_root / "snapshot-cow.bin"
    origin_mount = cell_root / "origin-mnt"
    fault_mount = cell_root / "fault-mnt"
    cold_mount = cell_root / "cold-mnt"
    for directory in (origin_mount, fault_mount, cold_mount):
        directory.mkdir(mode=0o700)
    origin_device: str | None = None
    cow_device: str | None = None
    dm_fault_name: str | None = None
    mounted_origin = False
    mounted_fault = False
    mounted_cold = False
    try:
        make_image(origin_image, origin_size_mib, filesystem)
        if scenario != "flakey-drop-writes":
            with cow_image.open("wb") as handle:
                handle.truncate(cow_size_mib * 1024 * 1024)
            cow_image.chmod(0o600)
        origin_device = losetup(origin_image)
        mount(origin_device, origin_mount, mount_options())
        mounted_origin = True
        chown_mount(origin_mount)
        write_generation(origin_mount, run_id, filesystem, scenario, 1)
        base_state = observe_state(origin_mount)
        if scenario == "cross-family-rollback":
            write_generation(origin_mount, run_id, filesystem, scenario, 2, ("immutable-branch-record", "manifest"))
        elif scenario == "torn-record":
            write_torn_family(origin_mount, run_id, filesystem, scenario, "manifest")
        umount(origin_mount)
        mounted_origin = False
        os.sync()
        time.sleep(2.0)

        if scenario == "flakey-drop-writes":
            dm_fault_name = dm_name(run_id, cell_index, "flakey")
            fault_device = create_flakey_drop_writes(dm_fault_name, origin_device)
            interposer = "device-mapper-flakey"
            storage_lie = "dm-flakey-drop-writes-after-acknowledged-fsync"
        else:
            cow_device = losetup(cow_image)
            dm_fault_name = dm_name(run_id, cell_index, "snap")
            fault_device = create_snapshot(dm_fault_name, origin_device, cow_device)
            interposer = "device-mapper-snapshot"
            storage_lie = {
                "valid-old-rollback": "snapshot-cow-discard-after-acknowledged-fsync",
                "cross-family-rollback": "snapshot-cow-discard-with-cross-family-prefix",
                "torn-record": "snapshot-cow-discard-with-torn-record-prefix",
            }[scenario]

        mount(fault_device, fault_mount, mount_options())
        mounted_fault = True
        chown_mount(fault_mount)
        write_generation(fault_mount, run_id, filesystem, scenario, 2)
        acknowledged_state = observe_state(fault_mount)
        require(all(item["parse_status"] == "valid" and item["generation"] == 2 for item in acknowledged_state.values()), "acknowledged state did not read as generation 2")
        umount(fault_mount)
        mounted_fault = False
        os.sync()
        time.sleep(1.0)
        dm_remove(dm_fault_name, strict=True)
        dm_fault_name = None

        mount(origin_device, cold_mount, cold_options(filesystem))
        mounted_cold = True
        cold_state = observe_state(cold_mount)
        umount(cold_mount)
        mounted_cold = False

        base_digest = state_digest(base_state)
        acknowledged_digest = state_digest(acknowledged_state)
        cold_digest = state_digest(cold_state)
        require(acknowledged_digest != base_digest, "acknowledged state did not change")
        require(cold_digest != acknowledged_digest, "cold state still equals acknowledged state")
        if scenario in {"valid-old-rollback", "flakey-drop-writes"}:
            require(all(item["parse_status"] == "valid" and item["generation"] == 1 for item in cold_state.values()), "cold state was not all valid generation 1")
        elif scenario == "cross-family-rollback":
            generations = {item["generation"] for item in cold_state.values() if item["parse_status"] == "valid"}
            require(generations == {1, 2}, "cold state was not mixed generation")
        elif scenario == "torn-record":
            require(cold_state["manifest"]["parse_status"] == "invalid-json", "cold manifest was not torn")

        return {
            "cell": cell_index,
            "filesystem": filesystem,
            "scenario": scenario,
            "block_interposer": interposer,
            "storage_lie": storage_lie,
            "claim_boundary": "same-host-dishonest-storage-matrix-drill",
            "acknowledged_generation_visible_before_cut": True,
            "rollback_detected": True,
            "mutation_refused": True,
            "contains_secrets": False,
            "raw_retained": keep_raw,
            "base_state_sha256": base_digest,
            "acknowledged_state_sha256": acknowledged_digest,
            "cold_state_sha256": cold_digest,
            "external_floor_state_sha256": acknowledged_digest,
            "family_results": family_results(base_state, acknowledged_state, cold_state),
        }
    finally:
        if mounted_cold:
            cleanup_umount(cold_mount)
        if mounted_fault:
            cleanup_umount(fault_mount)
        if mounted_origin:
            cleanup_umount(origin_mount)
        dm_remove(dm_fault_name)
        detach_loop(cow_device)
        detach_loop(origin_device)


def self_test() -> int:
    verifier = load_verifier()
    summary = verifier.verify_record(verifier.sample_receipt())
    require(summary["cell_count"] == 8, "matrix runner self-test verification failed")
    print("sync-dishonest-storage-matrix-runner-self-test=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-root", type=Path, default=DEFAULT_STATE_ROOT)
    parser.add_argument("--export-root", type=Path, default=DEFAULT_EXPORT_ROOT)
    parser.add_argument("--run-id")
    parser.add_argument("--origin-size-mib", type=int, default=256)
    parser.add_argument("--cow-size-mib", type=int, default=128)
    parser.add_argument("--filesystem", action="append", choices=FILESYSTEMS)
    parser.add_argument("--scenario", action="append", choices=SCENARIOS)
    parser.add_argument("--keep-raw", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()
    for tool in ("sudo", "dmsetup", "losetup", "mkfs.ext4", "mkfs.btrfs", "blockdev"):
        require(shutil.which(tool) is not None, f"{tool} is required")
    require(target_present("snapshot"), "device-mapper snapshot target is unavailable")
    require(target_present("flakey"), "device-mapper flakey target is unavailable")
    require(128 <= args.origin_size_mib <= 4096, "origin size must be 128..4096 MiB")
    require(64 <= args.cow_size_mib <= 4096, "COW size must be 64..4096 MiB")

    run_id = args.run_id or random_run_id()
    require(RUN_ID.fullmatch(run_id) is not None, "run id must look like run.XXXXXXXX")
    state_root = validate_under(args.state_root, ROOT / ".sandwurm/lab", "state root")
    export_root = validate_under(args.export_root, ROOT / ".sandwurm/exports", "export root")
    raw_root = state_root / run_id
    evidence_root = export_root / run_id
    require(not raw_root.exists(), "raw run root already exists")
    require(not evidence_root.exists(), "export run root already exists")
    state_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    export_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    raw_root.mkdir(mode=0o700)
    evidence_root.mkdir(mode=0o700)
    receipt_written = False
    try:
        filesystems = tuple(args.filesystem or FILESYSTEMS)
        scenarios = tuple(args.scenario or SCENARIOS)
        cells = []
        index = 0
        for filesystem in filesystems:
            for scenario in scenarios:
                cells.append(
                    run_cell(
                        run_id=run_id,
                        raw_root=raw_root,
                        cell_index=index,
                        filesystem=filesystem,
                        scenario=scenario,
                        origin_size_mib=args.origin_size_mib,
                        cow_size_mib=args.cow_size_mib,
                        keep_raw=args.keep_raw,
                    )
                )
                index += 1
        receipt = {
            "schema": SCHEMA,
            "status": "passed",
            "run_id": run_id,
            "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "tool": "tools/run-sync-dishonest-storage-matrix.py",
            "verifier": "tools/verify-sync-dishonest-storage-matrix.py",
            "git_revision": git_revision(),
            "contains_secrets": False,
            "filesystems": list(filesystems),
            "scenarios": list(scenarios),
            "cells": cells,
            "nonclaims": [
                "not-storage-media-certification",
                "not-independent-backup-custody",
                "not-precious-data-readiness",
                "not-full-production-agent-prefix-replay",
                "not-dm-log-writes-replay-log",
            ],
        }
        receipt_path = evidence_root / "matrix.json"
        receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        receipt_written = True
        verifier = load_verifier()
        verification = verifier.verify_record(receipt)
        verification_path = evidence_root / "matrix-verification.json"
        verification_path.write_text(json.dumps(verification, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        summary = {
            "schema": "iotox.sync-dishonest-storage-matrix-summary.v1",
            "status": "passed",
            "run_id": run_id,
            "receipt": str(receipt_path.relative_to(ROOT)),
            "receipt_sha256": sha256_file(receipt_path),
            "verification": str(verification_path.relative_to(ROOT)),
            "verification_sha256": sha256_file(verification_path),
            "cell_count": len(cells),
            "filesystems": list(filesystems),
            "scenarios": list(scenarios),
            "contains_secrets": False,
            "raw_retained": bool(args.keep_raw),
        }
        summary_path = evidence_root / "matrix-summary.json"
        summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
    finally:
        if receipt_written and not args.keep_raw and raw_root.exists():
            require(
                not mount_under(raw_root),
                "raw root still contains a mount after matrix cleanup",
            )
            remove_raw_root(raw_root, state_root)
        if not receipt_written and evidence_root.exists():
            shutil.rmtree(evidence_root)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (MatrixError, OSError, subprocess.SubprocessError, json.JSONDecodeError) as error:
        print(f"sync dishonest-storage matrix failed: {error}", file=sys.stderr)
        raise SystemExit(1)
