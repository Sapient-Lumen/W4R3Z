#!/usr/bin/env python3
"""Run a same-host dm-log-writes prefix replay gate for sync state."""

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
DEFAULT_STATE_ROOT = ROOT / ".sandwurm/lab/sync-log-writes-prefix"
DEFAULT_EXPORT_ROOT = ROOT / ".sandwurm/exports/sync-log-writes-prefix"
RUN_ID = re.compile(r"^run\.[A-Za-z0-9_]{8}$")
SCHEMA = "iotox.sync-log-writes-prefix-replay.v1"
FILESYSTEMS = ("ext4", "btrfs")
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
MARKS = {
    "generation-1-stable": "valid old branch/workspace floor after directory fsync",
    "manifest-record-prefix": "manifest and immutable branch-record installed before mutable branch pointer",
    "generation-2-stable": "complete branch pointer/workspace/projection generation after directory fsync",
}


class PrefixReplayError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PrefixReplayError(message)


def run(argv: list[str], *, capture_output: bool = False, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, check=True, text=True, capture_output=capture_output, input=input_text)


def run_combined(argv: list[str], *, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
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
            raise PrefixReplayError(f"device-mapper node remained busy: {name}")


def block_sectors(device: str) -> int:
    return int(run(["sudo", "blockdev", "--getsz", device], capture_output=True).stdout.strip())


def dm_name(run_id: str, index: int, kind: str) -> str:
    safe = "".join(character.lower() if character.isalnum() else "_" for character in run_id.removeprefix("run."))
    return f"iotox_lw_{safe}_{index}_{kind}"


def create_log_writes(name: str, origin_device: str, log_device: str) -> str:
    table = f"0 {block_sectors(origin_device)} log-writes {origin_device} {log_device}\n"
    run(["sudo", "dmsetup", "create", name], input_text=table)
    path = f"/dev/mapper/{name}"
    require(Path(path).exists(), "log-writes mapper device was not created")
    return path


def mark_log_writes(name: str, mark: str) -> None:
    require(mark in MARKS or mark == "mkfs", f"unsupported mark: {mark}")
    run(["sudo", "dmsetup", "message", name, "0", "mark", mark])


def mount(device: str, target: Path, options: str) -> None:
    run(["sudo", "mount", "-o", options, device, str(target)])


def umount(target: Path) -> None:
    run(["sudo", "umount", str(target)])


def cleanup_umount(target: Path) -> None:
    subprocess.run(["sudo", "umount", str(target)], check=False)


def fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def record_for(run_id: str, filesystem: str, family: str, generation: int) -> dict[str, Any]:
    payload = {
        "run_id": run_id,
        "filesystem": filesystem,
        "scenario": "dm-log-writes-prefix-replay",
        "family": family,
        "generation": generation,
        "payload_label": f"content-free-{family}-generation-{generation}",
    }
    return {
        "schema": "iotox.sync-dishonest-storage-record.v3",
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


def write_family(root: Path, run_id: str, filesystem: str, family: str, generation: int) -> str:
    payload = json.dumps(record_for(run_id, filesystem, family, generation), indent=2, sort_keys=True).encode("utf-8") + b"\n"
    return atomic_write(root / FAMILY_PATHS[family], payload)


def write_generation(root: Path, run_id: str, filesystem: str, generation: int, families: tuple[str, ...] = FAMILIES) -> dict[str, str]:
    digests = {}
    for family in families:
        digests[family] = write_family(root, run_id, filesystem, family, generation)
    fsync_directory(root / "tree-v2")
    os.sync()
    return digests


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


def family_results(acknowledged: dict[str, dict[str, Any]], replayed: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "family": family,
            "acknowledged_generation": acknowledged[family]["generation"],
            "replayed_generation": replayed[family]["generation"],
            "acknowledged_parse_status": acknowledged[family]["parse_status"],
            "replayed_parse_status": replayed[family]["parse_status"],
            "acknowledged_bytes_sha256": acknowledged[family]["bytes_sha256"],
            "replayed_bytes_sha256": replayed[family]["bytes_sha256"],
        }
        for family in FAMILIES
    ]


def chown_mount(root: Path) -> None:
    run(["sudo", "chown", f"{os.getuid()}:{os.getgid()}", str(root)])


def make_sparse(path: Path, size_mib: int) -> None:
    with path.open("wb") as handle:
        handle.truncate(size_mib * 1024 * 1024)
    path.chmod(0o600)


def mkfs(device: str, filesystem: str) -> None:
    if filesystem == "ext4":
        run(["sudo", "mkfs.ext4", "-q", "-F", device])
    elif filesystem == "btrfs":
        run(["sudo", "mkfs.btrfs", "-q", "-f", device])
    else:
        raise PrefixReplayError(f"unsupported filesystem: {filesystem}")


def mount_options(filesystem: str, readonly: bool = False) -> str:
    if filesystem == "ext4":
        return "ro,nosuid,nodev,noatime,noload" if readonly else "rw,nosuid,nodev,noatime"
    if filesystem == "btrfs":
        return "ro,nosuid,nodev,noatime" if readonly else "rw,nosuid,nodev,noatime"
    raise PrefixReplayError(f"unsupported filesystem: {filesystem}")


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


def find_replay_log(explicit: Path | None = None) -> Path:
    candidates: list[Path] = []
    if explicit is not None:
        candidates.append(explicit)
    which = shutil.which("replay-log")
    if which:
        candidates.append(Path(which))
    store = Path("/nix/store")
    if store.is_dir():
        candidates.extend(sorted(store.glob("*-xfstests-*/lib/xfstests/src/log-writes/replay-log")))
    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate.resolve()
    raise PrefixReplayError("replay-log is required; try `nix shell nixpkgs#xfstests` or pass --replay-log")


def replay_find_entry(replay_tool: Path, log_device: str, mark: str) -> tuple[int, str, str]:
    result = run_combined(["sudo", str(replay_tool), "--log", log_device, "--find", "--end-mark", mark])
    output = result.stdout.strip()
    match = re.search(r"(\d+)@", output)
    require(match is not None, f"unable to parse replay mark entry for {mark}: {output!r}")
    return int(match.group(1)), output, sha256_text(output)


def replay_to_mark(replay_tool: Path, log_device: str, replay_device: str, mark: str) -> None:
    run_combined(["sudo", str(replay_tool), "--log", log_device, "--replay", replay_device, "--end-mark", mark])
    os.sync()


def replay_prefix(
    *,
    replay_tool: Path,
    log_device: str,
    cell_root: Path,
    filesystem: str,
    mark: str,
    expected_state: dict[str, dict[str, Any]],
    acknowledged_state: dict[str, dict[str, Any]],
    origin_size_mib: int,
    index: int,
) -> dict[str, Any]:
    replay_image = cell_root / f"replay-{mark}.{filesystem}.img"
    replay_mount = cell_root / f"replay-{index:02d}-{mark}-mnt"
    replay_mount.mkdir(mode=0o700)
    replay_device: str | None = None
    mounted = False
    try:
        make_sparse(replay_image, origin_size_mib)
        replay_device = losetup(replay_image)
        mark_entry, find_output, find_output_sha256 = replay_find_entry(replay_tool, log_device, mark)
        replay_to_mark(replay_tool, log_device, replay_device, mark)
        mount(replay_device, replay_mount, mount_options(filesystem, readonly=True))
        mounted = True
        replayed_state = observe_state(replay_mount)
        umount(replay_mount)
        mounted = False
        replayed_digest = state_digest(replayed_state)
        expected_digest = state_digest(expected_state)
        acknowledged_digest = state_digest(acknowledged_state)
        require(replayed_digest == expected_digest, f"{filesystem}/{mark} replayed unexpected state")
        complete_current = mark == "generation-2-stable"
        if complete_current:
            require(replayed_digest == acknowledged_digest, f"{filesystem}/{mark} did not replay acknowledged current")
        else:
            require(replayed_digest != acknowledged_digest, f"{filesystem}/{mark} unexpectedly replayed acknowledged current")
        return {
            "mark": mark,
            "production_boundary": MARKS[mark],
            "mark_entry": mark_entry,
            "find_output_sha256": find_output_sha256,
            "replayed_state_sha256": replayed_digest,
            "expected_state_sha256": expected_digest,
            "external_floor_state_sha256": acknowledged_digest,
            "replayed_equals_expected_prefix": True,
            "rollback_detected_against_ack_floor": not complete_current,
            "mutation_refused": not complete_current,
            "accepted_current": complete_current,
            "contains_secrets": False,
            "family_results": family_results(acknowledged_state, replayed_state),
        }
    finally:
        if mounted:
            cleanup_umount(replay_mount)
        detach_loop(replay_device)


def run_cell(
    *,
    run_id: str,
    raw_root: Path,
    cell_index: int,
    filesystem: str,
    origin_size_mib: int,
    log_size_mib: int,
    replay_tool: Path,
    keep_raw: bool,
) -> dict[str, Any]:
    cell_root = raw_root / f"cell-{cell_index:02d}-{filesystem}-log-writes-prefix"
    cell_root.mkdir(mode=0o700)
    origin_image = cell_root / f"origin.{filesystem}.img"
    log_image = cell_root / "log-writes.bin"
    live_mount = cell_root / "live-mnt"
    live_mount.mkdir(mode=0o700)
    origin_device: str | None = None
    log_device: str | None = None
    dm_live_name: str | None = None
    mounted_live = False
    try:
        make_sparse(origin_image, origin_size_mib)
        make_sparse(log_image, log_size_mib)
        origin_device = losetup(origin_image)
        log_device = losetup(log_image)
        dm_live_name = dm_name(run_id, cell_index, "log")
        live_device = create_log_writes(dm_live_name, origin_device, log_device)
        mkfs(live_device, filesystem)
        mark_log_writes(dm_live_name, "mkfs")
        mount(live_device, live_mount, mount_options(filesystem))
        mounted_live = True
        chown_mount(live_mount)
        write_generation(live_mount, run_id, filesystem, 1)
        base_state = observe_state(live_mount)
        require(all(item["parse_status"] == "valid" and item["generation"] == 1 for item in base_state.values()), "base state did not read as generation 1")
        mark_log_writes(dm_live_name, "generation-1-stable")
        write_generation(live_mount, run_id, filesystem, 2, ("immutable-branch-record", "manifest"))
        manifest_prefix_state = observe_state(live_mount)
        require(
            manifest_prefix_state["immutable-branch-record"]["generation"] == 2
            and manifest_prefix_state["manifest"]["generation"] == 2,
            "manifest prefix did not advance manifest/record",
        )
        require(
            all(manifest_prefix_state[family]["generation"] == 1 for family in ("branch-pointer", "workspace", "maintenance", "projection-marker")),
            "manifest prefix advanced mutable families",
        )
        mark_log_writes(dm_live_name, "manifest-record-prefix")
        write_generation(live_mount, run_id, filesystem, 2)
        acknowledged_state = observe_state(live_mount)
        require(all(item["parse_status"] == "valid" and item["generation"] == 2 for item in acknowledged_state.values()), "acknowledged state did not read as generation 2")
        mark_log_writes(dm_live_name, "generation-2-stable")
        umount(live_mount)
        mounted_live = False
        os.sync()
        time.sleep(1.0)
        dm_remove(dm_live_name, strict=True)
        dm_live_name = None
        detach_loop(origin_device)
        origin_device = None

        prefix_results = []
        expected = {
            "generation-1-stable": base_state,
            "manifest-record-prefix": manifest_prefix_state,
            "generation-2-stable": acknowledged_state,
        }
        for prefix_index, mark in enumerate(MARKS):
            prefix_results.append(
                replay_prefix(
                    replay_tool=replay_tool,
                    log_device=log_device,
                    cell_root=cell_root,
                    filesystem=filesystem,
                    mark=mark,
                    expected_state=expected[mark],
                    acknowledged_state=acknowledged_state,
                    origin_size_mib=origin_size_mib,
                    index=prefix_index,
                )
            )

        return {
            "cell": cell_index,
            "filesystem": filesystem,
            "block_interposer": "device-mapper-log-writes",
            "claim_boundary": "same-host-dm-log-writes-prefix-replay-substrate",
            "replay_tool": str(replay_tool),
            "replay_tool_sha256": sha256_file(replay_tool),
            "origin_size_mib": origin_size_mib,
            "log_size_mib": log_size_mib,
            "contains_secrets": False,
            "raw_retained": keep_raw,
            "base_state_sha256": state_digest(base_state),
            "acknowledged_state_sha256": state_digest(acknowledged_state),
            "prefix_results": prefix_results,
        }
    finally:
        if mounted_live:
            cleanup_umount(live_mount)
        dm_remove(dm_live_name)
        detach_loop(origin_device)
        detach_loop(log_device)


def git_revision() -> str:
    result = subprocess.run(["git", "-c", f"safe.directory={ROOT}", "-C", str(ROOT), "rev-parse", "HEAD"], check=False, text=True, capture_output=True)
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def load_verifier():
    verifier = ROOT / "tools/verify-sync-log-writes-prefix-replay.py"
    spec = importlib.util.spec_from_file_location("iotox_log_writes_prefix_verify", verifier)
    require(spec is not None and spec.loader is not None, "unable to load prefix replay verifier")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def self_test() -> int:
    verifier = load_verifier()
    summary = verifier.verify_record(verifier.sample_receipt())
    require(summary["cell_count"] == 2, "prefix replay runner self-test verification failed")
    print("sync-log-writes-prefix-replay-runner-self-test=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-root", type=Path, default=DEFAULT_STATE_ROOT)
    parser.add_argument("--export-root", type=Path, default=DEFAULT_EXPORT_ROOT)
    parser.add_argument("--run-id")
    parser.add_argument("--origin-size-mib", type=int, default=256)
    parser.add_argument("--log-size-mib", type=int, default=512)
    parser.add_argument("--filesystem", action="append", choices=FILESYSTEMS)
    parser.add_argument("--replay-log", type=Path)
    parser.add_argument("--keep-raw", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()
    for tool in ("sudo", "dmsetup", "losetup", "mkfs.ext4", "mkfs.btrfs", "blockdev"):
        require(shutil.which(tool) is not None, f"{tool} is required")
    require(target_present("log-writes"), "device-mapper log-writes target is unavailable")
    require(128 <= args.origin_size_mib <= 4096, "origin size must be 128..4096 MiB")
    require(128 <= args.log_size_mib <= 8192, "log size must be 128..8192 MiB")
    replay_tool = find_replay_log(args.replay_log)

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
        cells = []
        for index, filesystem in enumerate(filesystems):
            cells.append(
                run_cell(
                    run_id=run_id,
                    raw_root=raw_root,
                    cell_index=index,
                    filesystem=filesystem,
                    origin_size_mib=args.origin_size_mib,
                    log_size_mib=args.log_size_mib,
                    replay_tool=replay_tool,
                    keep_raw=args.keep_raw,
                )
            )
        receipt = {
            "schema": SCHEMA,
            "status": "passed",
            "run_id": run_id,
            "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "tool": "tools/run-sync-log-writes-prefix-replay.py",
            "verifier": "tools/verify-sync-log-writes-prefix-replay.py",
            "git_revision": git_revision(),
            "contains_secrets": False,
            "filesystems": list(filesystems),
            "cells": cells,
            "nonclaims": [
                "not-live-agent-production-prefix-replay",
                "not-storage-media-certification",
                "not-independent-backup-custody",
                "not-precious-data-readiness",
                "not-physical-power-removal",
                "not-backup",
            ],
        }
        receipt_path = evidence_root / "prefix-replay.json"
        receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        receipt_written = True
        verifier = load_verifier()
        verification = verifier.verify_record(receipt)
        verification_path = evidence_root / "prefix-replay-verification.json"
        verification_path.write_text(json.dumps(verification, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        summary = {
            "schema": "iotox.sync-log-writes-prefix-replay-summary.v1",
            "status": "passed",
            "run_id": run_id,
            "receipt": str(receipt_path.relative_to(ROOT)),
            "receipt_sha256": sha256_file(receipt_path),
            "verification": str(verification_path.relative_to(ROOT)),
            "verification_sha256": sha256_file(verification_path),
            "cell_count": len(cells),
            "filesystems": list(filesystems),
            "marks": list(MARKS),
            "contains_secrets": False,
            "raw_retained": bool(args.keep_raw),
            "replay_tool": str(replay_tool),
            "replay_tool_sha256": sha256_file(replay_tool),
        }
        summary_path = evidence_root / "prefix-replay-summary.json"
        summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    finally:
        if not args.keep_raw and raw_root.exists():
            remove_raw_root(raw_root, state_root)
        if not receipt_written and evidence_root.exists():
            shutil.rmtree(evidence_root)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (PrefixReplayError, subprocess.CalledProcessError, OSError, json.JSONDecodeError) as error:
        print(f"sync log-writes prefix replay failed: {error}", file=sys.stderr)
        raise SystemExit(1)
