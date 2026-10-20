#!/usr/bin/env python3
"""Run a same-host loopback sync recovery custody prerequisite drill.

The helper creates two temporary ext4 loopback filesystems, places a selected
"backup generation" on one of them, remounts that filesystem read-only, restores
the generation onto the other filesystem, and invokes the retained recovery
drill wrapper with provenance and different-device requirements enabled.

The retained receipt is content-free. The loop images are temporary and are
removed by default after unmount/detach. This is deliberately not an
independent-backup proof: both loop images are backed by this host unless an
operator supplies genuinely independent media outside this helper.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import shutil
import stat
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_STATE_ROOT = ROOT / ".sandwurm/lab/sync-recovery-custody-loopback"
DEFAULT_EXPORT_ROOT = ROOT / ".sandwurm/exports/sync-recovery-custody"
RUN_ID = re.compile(r"^run\.[A-Za-z0-9_]{8}$")


class DrillError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise DrillError(message)


def run(
    argv: list[str],
    *,
    capture_output: bool = False,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        check=True,
        text=True,
        capture_output=capture_output,
    )


def sha256_file(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


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


def populate_backup(root: Path, run_id: str) -> None:
    require(root.is_dir() and not root.is_symlink(), "backup root is unsafe")
    (root / "docs").mkdir(mode=0o700)
    (root / "bin").mkdir(mode=0o700)
    (root / "empty-dir").mkdir(mode=0o700)
    (root / "README.txt").write_text(
        f"IoTox local loopback recovery custody drill {run_id}\n",
        encoding="utf-8",
    )
    (root / "docs/config.txt").write_text(
        "stable config\nline two\n",
        encoding="utf-8",
    )
    (root / "bin/blob.bin").write_bytes(
        bytes((index * 17 + 3) % 256 for index in range(32768))
    )
    for path in (
        root,
        root / "docs",
        root / "bin",
        root / "empty-dir",
        root / "bin/blob.bin",
    ):
        path.chmod(0o700)
    for path in (root / "README.txt", root / "docs/config.txt"):
        path.chmod(0o600)


def copy_regular_tree(source: Path, destination: Path) -> None:
    require(source.is_dir() and not source.is_symlink(), "source tree is unsafe")
    require(not destination.exists(), "destination tree already exists")
    destination.mkdir(mode=0o700)
    for item in sorted(source.rglob("*")):
        relative = item.relative_to(source)
        metadata = item.lstat()
        target = destination / relative
        require(not stat.S_ISLNK(metadata.st_mode), "source tree contains a symlink")
        if stat.S_ISDIR(metadata.st_mode):
            target.mkdir(mode=stat.S_IMODE(metadata.st_mode) & 0o700)
        elif stat.S_ISREG(metadata.st_mode):
            target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            shutil.copyfile(item, target, follow_symlinks=False)
            target.chmod(stat.S_IMODE(metadata.st_mode) & 0o700)
        else:
            raise DrillError("source tree contains a special file")


def remove_raw_root(raw_root: Path, state_root: Path) -> None:
    raw_root = raw_root.resolve()
    state_root = state_root.resolve()
    require(raw_root.parent == state_root, "raw root is not an immediate child")
    require(RUN_ID.fullmatch(raw_root.name) is not None, "raw root has bad name")
    require(raw_root.is_dir() and not raw_root.is_symlink(), "raw root is unsafe")
    require(not mount_under(raw_root), "raw root still contains a mount")
    shutil.rmtree(raw_root)


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


def load_receipt(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as source:
        record = json.load(source)
    require(isinstance(record, dict), "receipt root is not an object")
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iotox", type=Path, default=ROOT / "build/iotox")
    parser.add_argument("--state-root", type=Path, default=DEFAULT_STATE_ROOT)
    parser.add_argument("--export-root", type=Path, default=DEFAULT_EXPORT_ROOT)
    parser.add_argument("--run-id")
    parser.add_argument("--size-mib", type=int, default=64)
    parser.add_argument("--keep-raw", action="store_true")
    args = parser.parse_args()

    run_id = args.run_id or random_run_id()
    require(RUN_ID.fullmatch(run_id) is not None, "run id must look like run.XXXXXXXX")
    require(32 <= args.size_mib <= 1024, "loop image size must be 32..1024 MiB")
    iotox = args.iotox.resolve()
    require(iotox.is_file() and os.access(iotox, os.X_OK), "IoTox binary is absent")
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

    backup_image = raw_root / "backup.ext4"
    restore_image = raw_root / "restore.ext4"
    backup_mount = raw_root / "backup-mnt"
    restore_mount = raw_root / "restore-mnt"
    backup_mount.mkdir(mode=0o700)
    restore_mount.mkdir(mode=0o700)
    backup_device: str | None = None
    restore_device: str | None = None
    backup_mounted = False
    restore_mounted = False
    receipt = evidence_root / "retained-recovery-drill.json"

    try:
        for image in (backup_image, restore_image):
            with image.open("wb") as handle:
                handle.truncate(args.size_mib * 1024 * 1024)
            run(["mkfs.ext4", "-q", "-F", str(image)])
            image.chmod(0o600)
        backup_device = losetup(backup_image)
        restore_device = losetup(restore_image)

        mount(backup_device, backup_mount, "rw,nosuid,nodev")
        backup_mounted = True
        mount(restore_device, restore_mount, "rw,nosuid,nodev")
        restore_mounted = True
        run(
            [
                "sudo",
                "chown",
                f"{os.getuid()}:{os.getgid()}",
                str(backup_mount),
                str(restore_mount),
            ]
        )

        backup_root = backup_mount / "selected-generation"
        restored_root = restore_mount / "restored-generation"
        backup_root.mkdir(mode=0o700)
        populate_backup(backup_root, run_id)
        os.sync()

        umount(backup_mount)
        backup_mounted = False
        mount(backup_device, backup_mount, "ro,nosuid,nodev")
        backup_mounted = True

        copy_regular_tree(backup_root, restored_root)
        os.sync()

        drill = ROOT / "tools/run-sync-retained-recovery-drill.py"
        result = subprocess.run(
            [
                sys.executable,
                str(drill),
                "--iotox",
                str(iotox),
                "--evidence",
                str(receipt),
                "--backup-system",
                "iotox-local-loopback-ext4",
                "--backup-generation",
                run_id,
                "--backup-failure-domain",
                "same-host-read-only-loopback-ext4",
                "--restore-provenance",
                f"manual-copy-from-read-only-loopback:{run_id}",
                "--require-operator-provenance",
                "--require-different-device",
                str(backup_root),
                str(restored_root),
            ],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120,
        )
        (evidence_root / "retained-recovery-drill.stdout").write_text(
            result.stdout,
            encoding="utf-8",
        )
        (evidence_root / "retained-recovery-drill.stderr").write_text(
            result.stderr,
            encoding="utf-8",
        )
        require(result.returncode == 0, "retained recovery drill rejected")
        record = load_receipt(receipt)
        summary = {
            "schema": "iotox.sync-loopback-custody-drill.v1",
            "status": record.get("status"),
            "run_id": run_id,
            "receipt": str(receipt),
            "receipt_sha256": sha256_file(receipt),
            "decision": record.get("decision"),
            "root_devices_differ": record.get("root_devices_differ"),
            "operator_provenance_bound": record.get("operator_provenance_bound"),
            "operator_requirement_satisfied": record.get(
                "operator_requirement_satisfied"
            ),
            "device_requirement_satisfied": record.get(
                "device_requirement_satisfied"
            ),
            "local_requirements_satisfied": record.get(
                "local_requirements_satisfied"
            ),
            "backup_entries": record.get("backup_entries"),
            "backup_files": record.get("backup_files"),
            "backup_bytes": record.get("backup_bytes"),
            "backup_manifest": record.get("backup_manifest"),
            "restored_manifest": record.get("restored_manifest"),
            "report_sha256": record.get("report_sha256"),
            "iotox_binary_sha256": record.get("iotox_binary_sha256"),
            "backup_independence": record.get("backup_independence"),
            "restore_provenance_assessment": record.get(
                "restore_provenance_assessment"
            ),
            "contains_secrets": record.get("contains_secrets"),
            "raw_retained": bool(args.keep_raw),
            "claim_boundary": "same-host-loopback-different-device-prerequisite",
        }
        (evidence_root / "summary.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(summary, indent=2, sort_keys=True))
    finally:
        if backup_mounted:
            cleanup_umount(backup_mount)
        if restore_mounted:
            cleanup_umount(restore_mount)
        detach_loop(backup_device)
        detach_loop(restore_device)
        if not args.keep_raw and raw_root.exists():
            remove_raw_root(raw_root, state_root)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (DrillError, OSError, subprocess.SubprocessError) as error:
        print(f"sync loopback custody drill failed: {error}", file=sys.stderr)
        raise SystemExit(1)
