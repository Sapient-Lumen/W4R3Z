#!/usr/bin/env python3
"""Run a same-host block-level dishonest-storage drill for sync state.

The drill creates an ext4 origin image containing generation 1 of three
IoTox-shaped tree-v2 state families.  It then mounts a device-mapper snapshot,
writes generation 2 with file and directory fsyncs, confirms generation 2 is
visible, and discards the snapshot COW to simulate storage that acknowledged
the write but later returned the older valid backing state.

The pass condition is deliberately narrow: a content-free external witness
floor remembers generation 2, observes the cold generation 1 rollback, and
refuses mutation.  This is a first dishonest-storage substrate gate, not a
claim about real hardware honesty.
"""

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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_STATE_ROOT = ROOT / ".sandwurm/lab/sync-dishonest-storage"
DEFAULT_EXPORT_ROOT = ROOT / ".sandwurm/exports/sync-dishonest-storage"
RUN_ID = re.compile(r"^run\.[A-Za-z0-9_]{8}$")
FAMILIES = ("branch-pointer", "workspace", "maintenance")
FAMILY_PATHS = {
    "branch-pointer": Path("tree-v2/branches/current.branch.json"),
    "workspace": Path("tree-v2/workspaces/current.workspace.json"),
    "maintenance": Path("tree-v2/maintenance/current.maintenance.json"),
}
SCHEMA = "iotox.sync-dishonest-storage-drill.v1"


class DrillError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise DrillError(message)


def run(
    argv: list[str],
    *,
    capture_output: bool = False,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        check=True,
        text=True,
        capture_output=capture_output,
        input=input_text,
    )


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


def validate_state_root(path: Path) -> Path:
    resolved = path.resolve()
    allowed = (ROOT / ".sandwurm/lab").resolve()
    require(
        resolved == allowed or resolved.is_relative_to(allowed),
        "state root must be under .sandwurm/lab",
    )
    require(not resolved.is_symlink(), "state root may not be a symlink")
    return resolved


def validate_export_root(path: Path) -> Path:
    resolved = path.resolve()
    allowed = (ROOT / ".sandwurm/exports").resolve()
    require(
        resolved == allowed or resolved.is_relative_to(allowed),
        "export root must be under .sandwurm/exports",
    )
    require(not resolved.is_symlink(), "export root may not be a symlink")
    return resolved


def mount(device: str, target: Path, options: str) -> None:
    run(["sudo", "mount", "-o", options, device, str(target)])


def umount(target: Path) -> None:
    run(["sudo", "umount", str(target)])


def cleanup_umount(target: Path) -> None:
    subprocess.run(["sudo", "umount", str(target)], check=False)


def losetup(image: Path) -> str:
    result = run(
        ["sudo", "losetup", "--find", "--show", str(image)],
        capture_output=True,
    )
    device = result.stdout.strip()
    require(device.startswith("/dev/loop"), "losetup did not return a loop device")
    return device


def detach_loop(device: str | None) -> None:
    if device:
        subprocess.run(["sudo", "losetup", "-d", device], check=False)


def dm_remove(name: str | None) -> None:
    if name:
        subprocess.run(["sudo", "dmsetup", "remove", name], check=False)


def dm_snapshot_name(run_id: str) -> str:
    safe = "".join(
        character.lower() if character.isalnum() else "_"
        for character in run_id.removeprefix("run.")
    )
    return f"iotox_dishonest_{safe}"


def create_dm_snapshot(name: str, origin_device: str, cow_device: str) -> str:
    sectors = int(
        run(
            ["sudo", "blockdev", "--getsz", origin_device],
            capture_output=True,
        ).stdout.strip()
    )
    require(sectors > 0, "origin device has no sectors")
    table = f"0 {sectors} snapshot {origin_device} {cow_device} P 8\n"
    run(["sudo", "dmsetup", "create", name], input_text=table)
    path = f"/dev/mapper/{name}"
    require(Path(path).exists(), "snapshot mapper device was not created")
    return path


def target_present(name: str) -> bool:
    result = subprocess.run(
        ["sudo", "dmsetup", "targets"],
        check=False,
        text=True,
        capture_output=True,
    )
    return result.returncode == 0 and any(
        line.split(maxsplit=1)[0] == name for line in result.stdout.splitlines()
    )


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


def remove_empty_or_partial_export(evidence_root: Path, export_root: Path) -> None:
    evidence_root = evidence_root.resolve()
    export_root = export_root.resolve()
    if not evidence_root.exists():
        return
    require(evidence_root.parent == export_root, "export root is not an immediate child")
    require(RUN_ID.fullmatch(evidence_root.name) is not None, "export root has bad name")
    require(evidence_root.is_dir() and not evidence_root.is_symlink(), "export root is unsafe")
    shutil.rmtree(evidence_root)


def fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def atomic_write_json(path: Path, record: dict[str, object]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    payload = json.dumps(record, indent=2, sort_keys=True) + "\n"
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    descriptor = os.open(temporary, flags, 0o600)
    try:
        os.write(descriptor, payload.encode("utf-8"))
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    os.replace(temporary, path)
    fsync_directory(path.parent)
    return sha256_text(canonical_json(record))


def generation_record(run_id: str, family: str, generation: int) -> dict[str, object]:
    parent = None if generation == 1 else generation - 1
    payload = {
        "run_id": run_id,
        "family": family,
        "generation": generation,
        "payload_label": f"content-free-{family}-generation-{generation}",
    }
    return {
        "schema": "iotox.sync-dishonest-storage-record.v1",
        "family": family,
        "generation": generation,
        "parent_generation": parent,
        "payload_sha256": sha256_text(canonical_json(payload)),
    }


def write_generation(root: Path, run_id: str, generation: int) -> dict[str, str]:
    record_digests: dict[str, str] = {}
    for family in FAMILIES:
        record = generation_record(run_id, family, generation)
        record_digests[family] = atomic_write_json(root / FAMILY_PATHS[family], record)
    fsync_directory(root / "tree-v2")
    os.sync()
    return record_digests


def read_generation(root: Path) -> dict[str, dict[str, object]]:
    state: dict[str, dict[str, object]] = {}
    for family in FAMILIES:
        path = root / FAMILY_PATHS[family]
        with path.open("r", encoding="utf-8") as source:
            record = json.load(source)
        require(isinstance(record, dict), f"{family} record is not an object")
        require(record.get("family") == family, f"{family} record has wrong family")
        generation = record.get("generation")
        require(isinstance(generation, int), f"{family} generation is invalid")
        state[family] = record
    return state


def state_generation(state: dict[str, dict[str, object]]) -> int:
    generations = {record["generation"] for record in state.values()}
    require(len(generations) == 1, "state families have mixed generations")
    value = generations.pop()
    require(isinstance(value, int), "generation is invalid")
    return value


def state_digest(state: dict[str, dict[str, object]]) -> str:
    return sha256_text(canonical_json(state))


def record_digest(record: dict[str, object]) -> str:
    return sha256_text(canonical_json(record))


def git_revision() -> str:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={ROOT}", "-C", str(ROOT), "rev-parse", "HEAD"],
        check=False,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def load_verifier():
    verifier = ROOT / "tools/verify-sync-dishonest-storage-drill.py"
    spec = importlib.util.spec_from_file_location("iotox_dishonest_storage_verify", verifier)
    require(spec is not None and spec.loader is not None, "unable to load verifier")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sample_receipt_for_self_test() -> dict[str, object]:
    verifier = load_verifier()
    return verifier.sample_receipt()


def self_test() -> int:
    verifier = load_verifier()
    summary = verifier.verify_record(sample_receipt_for_self_test())
    require(summary["status"] == "passed", "runner self-test verification failed")
    print("sync-dishonest-storage-drill-runner-self-test=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-root", type=Path, default=DEFAULT_STATE_ROOT)
    parser.add_argument("--export-root", type=Path, default=DEFAULT_EXPORT_ROOT)
    parser.add_argument("--run-id")
    parser.add_argument("--origin-size-mib", type=int, default=96)
    parser.add_argument("--cow-size-mib", type=int, default=64)
    parser.add_argument("--keep-raw", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()
    require(shutil.which("sudo") is not None, "sudo is required")
    require(shutil.which("dmsetup") is not None, "dmsetup is required")
    require(shutil.which("losetup") is not None, "losetup is required")
    require(shutil.which("mkfs.ext4") is not None, "mkfs.ext4 is required")
    require(shutil.which("blockdev") is not None, "blockdev is required")
    require(target_present("snapshot"), "device-mapper snapshot target is unavailable")
    require(64 <= args.origin_size_mib <= 2048, "origin size must be 64..2048 MiB")
    require(32 <= args.cow_size_mib <= 2048, "COW size must be 32..2048 MiB")

    run_id = args.run_id or random_run_id()
    require(RUN_ID.fullmatch(run_id) is not None, "run id must look like run.XXXXXXXX")
    state_root = validate_state_root(args.state_root)
    export_root = validate_export_root(args.export_root)
    raw_root = state_root / run_id
    evidence_root = export_root / run_id
    require(not raw_root.exists(), "raw run root already exists")
    require(not evidence_root.exists(), "export run root already exists")
    state_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    export_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    raw_root.mkdir(mode=0o700)
    evidence_root.mkdir(mode=0o700)

    origin_image = raw_root / "origin.ext4"
    cow_image = raw_root / "snapshot-cow.bin"
    origin_mount = raw_root / "origin-mnt"
    snapshot_mount = raw_root / "snapshot-mnt"
    cold_mount = raw_root / "cold-mnt"
    for directory in (origin_mount, snapshot_mount, cold_mount):
        directory.mkdir(mode=0o700)

    origin_device: str | None = None
    cow_device: str | None = None
    snapshot_name: str | None = None
    snapshot_device: str | None = None
    origin_mounted = False
    snapshot_mounted = False
    cold_mounted = False
    receipt_written = False

    try:
        with origin_image.open("wb") as handle:
            handle.truncate(args.origin_size_mib * 1024 * 1024)
        with cow_image.open("wb") as handle:
            handle.truncate(args.cow_size_mib * 1024 * 1024)
        origin_image.chmod(0o600)
        cow_image.chmod(0o600)
        run(["mkfs.ext4", "-q", "-F", str(origin_image)])

        origin_device = losetup(origin_image)
        cow_device = losetup(cow_image)

        mount(origin_device, origin_mount, "rw,nosuid,nodev,noatime")
        origin_mounted = True
        run(["sudo", "chown", f"{os.getuid()}:{os.getgid()}", str(origin_mount)])
        base_record_digests = write_generation(origin_mount, run_id, 1)
        base_state = read_generation(origin_mount)
        base_generation = state_generation(base_state)
        base_digest = state_digest(base_state)
        require(base_generation == 1, "base generation write failed")
        umount(origin_mount)
        origin_mounted = False

        snapshot_name = dm_snapshot_name(run_id)
        snapshot_device = create_dm_snapshot(snapshot_name, origin_device, cow_device)
        mount(snapshot_device, snapshot_mount, "rw,nosuid,nodev,noatime")
        snapshot_mounted = True
        acknowledged_record_digests = write_generation(snapshot_mount, run_id, 2)
        acknowledged_state = read_generation(snapshot_mount)
        acknowledged_generation = state_generation(acknowledged_state)
        acknowledged_digest = state_digest(acknowledged_state)
        require(acknowledged_generation == 2, "acknowledged generation write failed")
        require(base_digest != acknowledged_digest, "acknowledged state did not change")
        umount(snapshot_mount)
        snapshot_mounted = False
        dm_remove(snapshot_name)
        snapshot_name = None

        mount(origin_device, cold_mount, "ro,nosuid,nodev,noatime,noload")
        cold_mounted = True
        cold_state = read_generation(cold_mount)
        cold_generation = state_generation(cold_state)
        cold_digest = state_digest(cold_state)
        require(cold_generation == 1, "cold origin did not return the older state")
        require(cold_digest == base_digest, "cold state is not the base state")
        require(cold_digest != acknowledged_digest, "cold state still has acknowledged write")
        umount(cold_mount)
        cold_mounted = False

        family_results = []
        for family in FAMILIES:
            base_record_digest = record_digest(base_state[family])
            acknowledged_record_digest = record_digest(acknowledged_state[family])
            cold_record_digest = record_digest(cold_state[family])
            require(base_record_digest == base_record_digests[family], f"{family} base digest mismatch")
            require(
                acknowledged_record_digest == acknowledged_record_digests[family],
                f"{family} acknowledged digest mismatch",
            )
            require(cold_record_digest == base_record_digest, f"{family} cold digest mismatch")
            family_results.append(
                {
                    "family": family,
                    "base_generation": 1,
                    "acknowledged_generation": 2,
                    "cold_generation": 1,
                    "external_floor_generation": 2,
                    "base_record_sha256": base_record_digest,
                    "acknowledged_record_sha256": acknowledged_record_digest,
                    "cold_record_sha256": cold_record_digest,
                    "rollback_detected": True,
                    "mutation_refused": True,
                }
            )

        receipt = {
            "schema": SCHEMA,
            "status": "passed",
            "run_id": run_id,
            "created_at_utc": datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat(),
            "tool": "tools/run-sync-dishonest-storage-drill.py",
            "verifier": "tools/verify-sync-dishonest-storage-drill.py",
            "git_revision": git_revision(),
            "block_interposer": "device-mapper-snapshot",
            "filesystem": "ext4",
            "storage_lie": "snapshot-cow-discard-after-acknowledged-fsync",
            "claim_boundary": "same-host-dm-snapshot-valid-old-rollback-drill",
            "dm_snapshot_target_present": True,
            "acknowledged_generation_visible_before_cut": True,
            "cold_valid_old_returned": True,
            "rollback_detected": True,
            "mutation_refused": True,
            "refusal_reason": "valid-old-rollback-below-external-witness-floor",
            "contains_secrets": False,
            "raw_retained": bool(args.keep_raw),
            "generations": {
                "base": base_generation,
                "acknowledged": acknowledged_generation,
                "cold": cold_generation,
                "external_floor": acknowledged_generation,
            },
            "state_digests": {
                "base": base_digest,
                "acknowledged": acknowledged_digest,
                "cold": cold_digest,
                "external_floor": acknowledged_digest,
            },
            "family_results": family_results,
            "fsyncs": {
                "generation_1_file_and_directory": True,
                "generation_2_file_and_directory": True,
                "os_sync_after_acknowledged_write": True,
            },
            "devices": {
                "origin_loop_sha256": sha256_text(origin_device),
                "cow_loop_sha256": sha256_text(cow_device),
                "snapshot_dm_name_sha256": sha256_text(snapshot_device or ""),
                "origin_size_bytes": args.origin_size_mib * 1024 * 1024,
                "cow_size_bytes": args.cow_size_mib * 1024 * 1024,
            },
            "nonclaims": [
                "not-storage-media-certification",
                "not-full-dishonest-storage-matrix",
                "not-physical-power-loss-evidence",
                "not-independent-backup-custody",
                "not-precious-data-readiness",
            ],
        }

        receipt_path = evidence_root / "receipt.json"
        receipt_path.write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        receipt_written = True
        verifier = load_verifier()
        verification = verifier.verify_record(receipt)
        (evidence_root / "verification.json").write_text(
            json.dumps(verification, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        summary = {
            "schema": "iotox.sync-dishonest-storage-drill-summary.v1",
            "status": "passed",
            "run_id": run_id,
            "receipt": str(receipt_path.relative_to(ROOT)),
            "receipt_sha256": sha256_file(receipt_path),
            "verification": str((evidence_root / "verification.json").relative_to(ROOT)),
            "verification_sha256": sha256_file(evidence_root / "verification.json"),
            "claim_boundary": receipt["claim_boundary"],
            "block_interposer": receipt["block_interposer"],
            "storage_lie": receipt["storage_lie"],
            "families": list(FAMILIES),
            "base_generation": base_generation,
            "acknowledged_generation": acknowledged_generation,
            "cold_generation": cold_generation,
            "rollback_detected": True,
            "mutation_refused": True,
            "contains_secrets": False,
            "raw_retained": bool(args.keep_raw),
        }
        (evidence_root / "summary.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(summary, indent=2, sort_keys=True))
    finally:
        if cold_mounted:
            cleanup_umount(cold_mount)
        if snapshot_mounted:
            cleanup_umount(snapshot_mount)
        if origin_mounted:
            cleanup_umount(origin_mount)
        dm_remove(snapshot_name)
        detach_loop(cow_device)
        detach_loop(origin_device)
        if not args.keep_raw and raw_root.exists():
            remove_raw_root(raw_root, state_root)
        if not receipt_written and evidence_root.exists():
            remove_empty_or_partial_export(evidence_root, export_root)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (DrillError, OSError, subprocess.SubprocessError, json.JSONDecodeError) as error:
        print(f"sync dishonest-storage drill failed: {error}", file=sys.stderr)
        raise SystemExit(1)
