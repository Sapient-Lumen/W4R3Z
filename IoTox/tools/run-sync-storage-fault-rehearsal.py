#!/usr/bin/env python3
"""Exercise bounded tree-v2 ENOSPC, read-only, and abrupt-exit recovery."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import stat
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parent.parent
THREE_WRITER = ROOT / "tools/run-sync-three-writer.py"
RECOVERY = ROOT / "tools/run-sync-recovery-rehearsal.py"


def load_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load helper: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def run_checked(arguments: list[str], *, timeout: int = 60) -> str:
    result = subprocess.run(
        arguments,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=timeout,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise RuntimeError(f"{' '.join(arguments)} failed: {detail}")
    return result.stdout


class LoopExt4:
    def __init__(self, image: Path, mountpoint: Path, size_mib: int) -> None:
        self.image = image
        self.mountpoint = mountpoint
        self.size_mib = size_mib
        self.mounted = False

    def create(self) -> None:
        self.image.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.mountpoint.mkdir(mode=0o700, parents=True, exist_ok=False)
        run_checked(["truncate", "-s", f"{self.size_mib}M", str(self.image)])
        run_checked(["mkfs.ext4", "-q", "-F", "-m", "0", str(self.image)])
        run_checked(
            [
                "mount",
                "-o",
                "loop,nosuid,nodev,noexec",
                str(self.image),
                str(self.mountpoint),
            ]
        )
        self.mounted = True
        os.chmod(self.mountpoint, 0o700)

    def remount(self, readonly: bool) -> None:
        mode = "ro" if readonly else "rw"
        run_checked(["mount", "-o", f"remount,{mode}", str(self.mountpoint)])

    def mount_existing(self) -> None:
        if self.image.is_symlink() or not self.image.is_file():
            raise RuntimeError(f"ext4 image is absent or unsafe: {self.image}")
        self.mountpoint.mkdir(mode=0o700, parents=True, exist_ok=True)
        if any(self.mountpoint.iterdir()):
            raise RuntimeError(
                f"existing ext4 mountpoint is not empty: {self.mountpoint}"
            )
        run_checked(
            [
                "mount",
                "-o",
                "loop,nosuid,nodev,noexec",
                str(self.image),
                str(self.mountpoint),
            ]
        )
        self.mounted = True
        os.chmod(self.mountpoint, 0o700)

    def unmount(self) -> None:
        if not self.mounted:
            return
        run_checked(["umount", str(self.mountpoint)])
        self.mounted = False


def fsync_path(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def write_exact(path: Path, content: bytes, mode: int = 0o600) -> None:
    descriptor = os.open(
        path,
        os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_CLOEXEC,
        mode,
    )
    try:
        view = memoryview(content)
        offset = 0
        while offset < len(view):
            offset += os.write(descriptor, view[offset:])
        os.fchmod(descriptor, mode)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    fsync_path(path.parent)


def durable_tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for candidate in sorted(root.rglob("*")):
        relative = candidate.relative_to(root)
        if relative.parts and relative.parts[0] in {"runtime"}:
            continue
        if relative == Path("agent.log"):
            continue
        metadata = candidate.lstat()
        encoded = relative.as_posix().encode("utf-8")
        digest.update(len(encoded).to_bytes(4, "big"))
        digest.update(encoded)
        digest.update(stat.S_IMODE(metadata.st_mode).to_bytes(2, "big"))
        if stat.S_ISDIR(metadata.st_mode):
            digest.update(b"d")
        elif stat.S_ISREG(metadata.st_mode):
            digest.update(b"f")
            digest.update(candidate.read_bytes())
        else:
            # Runtime sockets were excluded above. Durable state must remain
            # regular-file/directory-only for this offline comparison.
            raise RuntimeError(f"unexpected durable entry: {candidate}")
    return digest.hexdigest()


def fill_to_enospc(path: Path) -> int:
    descriptor = os.open(
        path,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC,
        0o600,
    )
    block = b"\xa5" * (1024 * 1024)
    total = 0
    exhausted = False
    try:
        while True:
            try:
                count = os.write(descriptor, block)
                if count <= 0:
                    raise RuntimeError("ENOSPC filler made no progress")
                total += count
            except OSError as error:
                if error.errno != 28:
                    raise
                exhausted = True
                break
        try:
            os.fsync(descriptor)
        except OSError as error:
            if error.errno != 28:
                raise
            exhausted = True
    finally:
        os.close(descriptor)
    if not exhausted:
        raise RuntimeError("loop filesystem did not report ENOSPC")
    return total


def abrupt_kill(node: object) -> int:
    return node.kill_abrupt()


def wait_exact(tw: object, recovery: object, nodes: list[object],
               namespace: str, expected: dict[str, object], label: str,
               timeout: int = 240) -> None:
    tw.wait_for(
        label,
        nodes,
        lambda: all(
            tw.automation_ready(node, namespace)
            and tw.branch_count(node, namespace) == 3
            and not tw.conflict_files(node)
            and recovery.operator_tree_summary(node.worktree) == expected
            for node in nodes
        ),
        timeout,
    )
    recovery.repair_all(nodes, namespace)


def readonly_start_attempt(node: object, volume: LoopExt4,
                           external_log: Path) -> tuple[int, str]:
    control = node.runtime / "control.sock"
    if control.exists() or control.is_socket():
        control.unlink()
    before = durable_tree_digest(node.root)
    volume.remount(True)
    with external_log.open("wb") as output:
        process = subprocess.Popen(
            node.args(),
            stdout=output,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        try:
            result = process.wait(timeout=20)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=10)
            raise RuntimeError("Agent unexpectedly remained live on read-only state")
    volume.remount(False)
    after = durable_tree_digest(node.root)
    if result == 0 or before != after:
        raise RuntimeError("read-only startup did not fail without durable mutation")
    detail = external_log.read_text(encoding="utf-8", errors="replace")
    return result, hashlib.sha256(detail.encode("utf-8")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iotox", type=Path, required=True)
    parser.add_argument("--bootstrap", type=Path, required=True)
    parser.add_argument("--three-writer-helper", type=Path, default=THREE_WRITER)
    parser.add_argument("--recovery-helper", type=Path, default=RECOVERY)
    parser.add_argument("--state-root", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--namespace", default="storage-fault-notes")
    parser.add_argument("--disk-mib", type=int, default=192)
    parser.add_argument("--exchange-bytes", type=int, default=32 * 1024 * 1024)
    args = parser.parse_args()

    if os.geteuid() != 0:
        raise RuntimeError("storage-fault rehearsal requires a disposable root VM")
    if not 128 <= args.disk_mib <= 1024:
        raise RuntimeError("disk-mib must be between 128 and 1024")
    if not 8 * 1024 * 1024 <= args.exchange_bytes <= 64 * 1024 * 1024:
        raise RuntimeError("exchange-bytes must be between 8 and 64 MiB")

    tw = load_module(args.three_writer_helper.resolve(), "iotox_three_writer_fault")
    recovery = load_module(args.recovery_helper.resolve(), "iotox_recovery_fault")
    recovery.tw = tw
    binary = args.iotox.resolve()
    bootstrap_binary = args.bootstrap.resolve()
    state_root = args.state_root.resolve()
    evidence = args.evidence.resolve()
    tw.require(binary.is_file(), "IoTox binary is absent")
    tw.require(bootstrap_binary.is_file(), "bootstrap binary is absent")
    tw.require(not state_root.exists(), "storage-fault root must start absent")
    tw.private_directory(state_root)
    tw.private_directory(evidence.parent)
    lock = (state_root / ".qualification.lock").open("a+b")
    os.chmod(lock.fileno(), 0o600)
    fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

    volumes = [
        LoopExt4(
            state_root / "disks" / f"node-{index + 1}.img",
            state_root / "mounts" / f"node-{index + 1}",
            args.disk_mib,
        )
        for index in range(3)
    ]
    nodes: list[object] = []
    bootstrap_process: subprocess.Popen[bytes] | None = None
    bootstrap_log = None
    started = time.monotonic()
    try:
        for volume in volumes:
            volume.create()
        bootstrap_root = state_root / "bootstrap"
        tw.private_directory(bootstrap_root)
        bootstrap_log = (bootstrap_root / "bootstrap.log").open("ab")
        bootstrap_process = subprocess.Popen(
            [str(bootstrap_binary), "--ipv4"],
            cwd=bootstrap_root,
            stdout=bootstrap_log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        public_id = bootstrap_root / "PUBLIC_ID.txt"
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline and not (
            public_id.is_file() and public_id.stat().st_size == 64
        ):
            tw.require(bootstrap_process.poll() is None, "bootstrap exited")
            time.sleep(0.05)
        bootstrap_key = public_id.read_text(encoding="ascii").strip()
        tw.require(bool(tw.HEX64.fullmatch(bootstrap_key)), "bad bootstrap key")
        bootstrap = f"127.0.0.1:33445:{bootstrap_key}"

        nodes = [
            tw.Node(
                chr(97 + index),
                volumes[index].mountpoint / "node",
                tw.RECALL_PHRASES[index],
                binary,
                bootstrap,
            )
            for index in range(3)
        ]
        for node in nodes:
            tw.private_directory(node.worktree)
        recovery.start_nodes(nodes)
        tw.require(
            recovery.connect_full_mesh(nodes, args.namespace) == 6,
            "bad storage-fault share count",
        )
        recovery.seed_initial_tree(nodes[0], 16, 4096)
        baseline = recovery.operator_tree_summary(nodes[0].worktree)
        wait_exact(tw, recovery, nodes, args.namespace, baseline,
                   "storage-fault baseline convergence")

        # Freeze one writer before an ordinary edit, consume every free block,
        # and let the live Agent encounter ENOSPC. The edit is already durable
        # in the worktree; after abrupt exit and space recovery it must publish
        # normally rather than yielding a corrupt semantic root.
        enospc_node = nodes[0]
        assert enospc_node.process is not None
        os.killpg(enospc_node.process.pid, signal.SIGSTOP)
        write_exact(enospc_node.worktree / "enospc.txt", b"durable before ENOSPC\n")
        filler = volumes[0].mountpoint / ".iotox-enospc-fill"
        filler_bytes = fill_to_enospc(filler)
        os.killpg(enospc_node.process.pid, signal.SIGCONT)
        fault_result = enospc_node.command(
            "sync-checkpoint", args.namespace, check=False, timeout=60
        )
        enospc_detail = fault_result.stdout + fault_result.stderr
        enospc_observed = (
            fault_result.returncode != 0
            and "No space left on device" in enospc_detail
        )
        if not enospc_observed:
            raise RuntimeError("live Agent did not expose the injected ENOSPC")
        enospc_exit = abrupt_kill(enospc_node)
        filler.unlink()
        fsync_path(volumes[0].mountpoint)
        enospc_node.start()
        after_enospc = recovery.operator_tree_summary(enospc_node.worktree)
        wait_exact(tw, recovery, nodes, args.namespace, after_enospc,
                   "post-ENOSPC convergence")

        # A stopped Agent must not silently start or alter state when its exact
        # ext4 state volume is read-only. Restore read-write access and require
        # the same identity/session surface to return.
        readonly_node = nodes[1]
        readonly_node.stop()
        readonly_exit, readonly_log_sha256 = readonly_start_attempt(
            readonly_node,
            volumes[1],
            state_root / "read-only-start.log",
        )
        readonly_node.start()
        tw.wait_for(
            "read-only recovery restart",
            nodes,
            lambda: readonly_node.command("status", check=False).returncode == 0,
            60,
        )
        wait_exact(tw, recovery, nodes, args.namespace, after_enospc,
                   "post-read-only convergence")

        # Create a wide remote successor while C is offline. On C's restart,
        # kill its process as soon as either the signed pending workspace or
        # invisible projection staging appears. Startup must join the exact
        # durable side and converge without accepting a third state.
        abrupt_node = nodes[2]
        abrupt_node.stop()
        payload_seed = hashlib.sha256(b"iotox-storage-fault-exchange-v1").digest()
        payload = (payload_seed * ((args.exchange_bytes + 31) // 32))[
            : args.exchange_bytes
        ]
        write_exact(nodes[0].worktree / "wide.bin", payload)
        wide = recovery.operator_tree_summary(nodes[0].worktree)
        tw.wait_for(
            "two-survivor wide edit convergence",
            nodes[:2],
            lambda: all(
                recovery.operator_tree_summary(node.worktree) == wide
                for node in nodes[:2]
            ),
            240,
        )
        abrupt_node.start()
        workspace_state = (
            abrupt_node.policy_root
            / "data"
            / args.namespace
            / "tree-v2"
            / "workspace.state"
        )
        stage_path = abrupt_node.root / f".worktree.iotox-{args.namespace}.stage"
        observed = ""
        deadline = time.monotonic() + 240
        while time.monotonic() < deadline:
            abrupt_node.ensure_running()
            if stage_path.exists():
                observed = "projection-stage"
                break
            try:
                header = workspace_state.read_bytes()[:10]
                if len(header) == 10 and header[:8] == b"IOTXTWS1" and header[9] == 1:
                    observed = "pending-workspace"
                    break
            except FileNotFoundError:
                pass
            time.sleep(0.001)
        if not observed:
            raise RuntimeError("abrupt exchange transition was not observed")
        abrupt_exit = abrupt_kill(abrupt_node)
        abrupt_node.start()
        wait_exact(tw, recovery, nodes, args.namespace, wide,
                   "post-abrupt-exchange convergence", 300)

        receipt = {
            "storage_fault_schema": "iotox.sync-storage-fault.v1",
            "storage_fault_rehearsal": True,
            "storage_fault_status": "passed",
            "storage_fault_node_count": 3,
            "storage_fault_filesystem": "ext4-loop",
            "storage_fault_disk_mib_per_node": args.disk_mib,
            "enospc_live_observed": enospc_observed,
            "enospc_filler_bytes": filler_bytes,
            "enospc_abrupt_exit": enospc_exit,
            "read_only_start_refused": True,
            "read_only_exit": readonly_exit,
            "read_only_log_sha256": readonly_log_sha256,
            "abrupt_exchange_observed": observed,
            "abrupt_exchange_bytes": args.exchange_bytes,
            "abrupt_exchange_exit": abrupt_exit,
            "storage_fault_final_files": wide["files"],
            "storage_fault_final_directories": wide["directories"],
            "storage_fault_final_bytes": wide["bytes"],
            "storage_fault_final_tree_sha256": wide["digest"],
            "storage_fault_repair_verified_nodes": 3,
            "storage_fault_elapsed_ms": int(
                (time.monotonic() - started) * 1000
            ),
            "storage_fault_contains_secrets": False,
            "storage_fault_power_cut": False,
            "storage_fault_dishonest_storage_assessed": False,
        }
        temporary = evidence.with_name(evidence.name + ".tmp")
        temporary.write_text(
            json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        os.chmod(temporary, 0o600)
        with temporary.open("rb") as source:
            os.fsync(source.fileno())
        temporary.replace(evidence)
        fsync_path(evidence.parent)
        print(json.dumps(receipt, sort_keys=True), flush=True)
        return 0
    except (OSError, RuntimeError, subprocess.SubprocessError,
            tw.QualificationError) as error:
        print(f"sync storage-fault rehearsal failed: {error}", file=sys.stderr)
        return 1
    finally:
        for node in nodes:
            try:
                node.stop()
            except Exception:
                pass
        if bootstrap_process is not None and bootstrap_process.poll() is None:
            os.killpg(bootstrap_process.pid, signal.SIGTERM)
            try:
                bootstrap_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(bootstrap_process.pid, signal.SIGKILL)
                bootstrap_process.wait(timeout=5)
        if bootstrap_log is not None:
            bootstrap_log.close()
        for volume in reversed(volumes):
            try:
                volume.unmount()
            except Exception as error:
                print(f"warning: unable to unmount {volume.mountpoint}: {error}",
                      file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
