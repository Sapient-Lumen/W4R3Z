#!/usr/bin/env python3
"""Corrupt and explicitly restore every live tree-v2 metadata record family."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import signal
import stat
import subprocess
import sys
import tempfile
import time


ROOT = Path(__file__).resolve().parent.parent
THREE_WRITER = ROOT / "tools/run-sync-three-writer.py"
RECOVERY = ROOT / "tools/run-sync-recovery-rehearsal.py"
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def load_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load helper: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def validate_private_record(path: Path) -> os.stat_result:
    metadata = path.lstat()
    require(stat.S_ISREG(metadata.st_mode), "metadata target is not regular")
    require(not path.is_symlink(), "metadata target is a symlink")
    require(metadata.st_uid == os.geteuid(), "metadata target has another owner")
    require(metadata.st_nlink == 1, "metadata target has multiple links")
    require(stat.S_IMODE(metadata.st_mode) == 0o600, "metadata target is not 0600")
    require(metadata.st_size > 0, "metadata target is empty")
    return metadata


def write_in_place_exact(path: Path, value: bytes) -> None:
    metadata = validate_private_record(path)
    require(metadata.st_size == len(value), "metadata restoration changed size")
    descriptor = os.open(path, os.O_RDWR | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        offset = 0
        while offset < len(value):
            count = os.pwrite(descriptor, value[offset:], offset)
            require(count > 0, "metadata restoration made no progress")
            offset += count
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    fsync_directory(path.parent)


def corrupt_in_place(path: Path) -> tuple[bytes, bytes]:
    metadata = validate_private_record(path)
    original = path.read_bytes()
    require(len(original) == metadata.st_size, "metadata target changed during read")
    corrupt = bytearray(original)
    corrupt[-1] ^= 0x01
    write_in_place_exact(path, corrupt)
    observed = path.read_bytes()
    require(observed == corrupt, "durable corruption reread changed")
    return original, bytes(corrupt)


def startup_refusal(
    node: object,
    state_root: Path,
    family: str,
    log_label: str | None = None,
) -> tuple[int, str]:
    control = node.runtime / "control.sock"
    try:
        control.unlink()
    except FileNotFoundError:
        pass
    log_path = state_root / f"startup-{log_label or family}.log"
    with log_path.open("xb") as output:
        os.chmod(output.fileno(), 0o600)
        process = subprocess.Popen(
            [*node.process_prefix, *node.args()],
            stdout=output,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        try:
            result = process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=10)
            raise RuntimeError(
                f"Agent remained live with corrupt {family} metadata"
            )
    require(
        result == 3,
        f"Agent refusal for corrupt {family} did not use startup exit 3: {result}",
    )
    detail = log_path.read_text(encoding="utf-8", errors="replace").lower()
    require(family.replace("-", " ") in detail, f"startup did not classify {family}")
    return result, sha256_file(log_path)


def controlled_stop(node: object) -> int:
    node.ensure_running()
    stopped = node.command("stop", timeout=10, check=False)
    require(stopped.returncode == 0, "Agent control stop was refused")
    require(node.process is not None, "Agent process disappeared before stop")
    result = node.process.wait(timeout=15)
    require(result == 0, f"Agent controlled stop exited {result}")
    node.process = None
    if node.log_handle is not None:
        node.log_handle.close()
        node.log_handle = None
    return result


def stopped_agent_task_count(pid: int, timeout: float = 10.0) -> int:
    deadline = time.monotonic() + timeout
    last_states: list[str] = []
    while time.monotonic() < deadline:
        task_root = Path(f"/proc/{pid}/task")
        try:
            states = []
            for task in task_root.iterdir():
                status_text = (task / "status").read_text(
                    encoding="ascii", errors="replace"
                )
                state_line = next(
                    line for line in status_text.splitlines()
                    if line.startswith("State:")
                )
                states.append(state_line.split()[1])
        except (OSError, StopIteration):
            states = []
        last_states = states
        if states and all(state in {"T", "t"} for state in states):
            return len(states)
        time.sleep(0.02)
    raise RuntimeError(
        "Agent tasks did not all stop before simultaneous corruption: "
        + ",".join(last_states)
    )


def suspend_agent_tasks(node: object) -> int:
    node.ensure_running()
    require(node.process is not None, "Agent process is absent")
    pid = node.process.pid
    require(os.getpgid(pid) == pid, "Agent does not own its process group")
    os.killpg(pid, signal.SIGSTOP)
    try:
        return stopped_agent_task_count(pid)
    except BaseException:
        os.killpg(pid, signal.SIGCONT)
        raise


def resume_agent_tasks(node: object) -> None:
    require(node.process is not None, "Agent process is absent")
    os.killpg(node.process.pid, signal.SIGCONT)
    node.ensure_running()


def write_receipt(path: Path, value: dict[str, object]) -> None:
    require(not path.exists() and not path.is_symlink(),
            "metadata corruption receipt already exists")
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    encoded = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    descriptor = os.open(
        temporary,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC,
        0o600,
    )
    try:
        offset = 0
        while offset < len(encoded):
            offset += os.write(descriptor, encoded[offset:])
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    try:
        os.link(temporary, path, follow_symlinks=False)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    temporary.unlink()
    fsync_directory(path.parent)


def self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="iotox-metadata-corruption-") as raw:
        root = Path(raw)
        root.chmod(0o700)
        record = root / "record"
        record.write_bytes(b"signed-metadata-record")
        record.chmod(0o600)
        original, corrupt = corrupt_in_place(record)
        require(original != corrupt and record.read_bytes() == corrupt,
                "self-test corruption failed")
        write_in_place_exact(record, original)
        require(record.read_bytes() == original, "self-test restoration failed")
    print("sync-metadata-corruption-rehearsal-self-test=pass")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--iotox", type=Path)
    parser.add_argument("--bootstrap", type=Path)
    parser.add_argument("--three-writer-helper", type=Path, default=THREE_WRITER)
    parser.add_argument("--recovery-helper", type=Path, default=RECOVERY)
    parser.add_argument("--state-root", type=Path)
    parser.add_argument("--evidence", type=Path)
    parser.add_argument("--namespace", default="metadata-corruption-notes")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    require(
        args.iotox is not None
        and args.bootstrap is not None
        and args.state_root is not None
        and args.evidence is not None,
        "runtime mode requires iotox, bootstrap, state-root, and evidence",
    )

    tw = load_module(args.three_writer_helper.resolve(), "iotox_tw_corruption")
    recovery = load_module(args.recovery_helper.resolve(), "iotox_recovery_corruption")
    recovery.tw = tw
    binary = args.iotox.resolve()
    bootstrap_binary = args.bootstrap.resolve()
    state_root = args.state_root.resolve()
    evidence = args.evidence.resolve()
    require(binary.is_file(), "IoTox binary is absent")
    require(bootstrap_binary.is_file(), "bootstrap binary is absent")
    require(not state_root.exists(), "corruption state root must start absent")
    require(not evidence.exists() and not evidence.is_symlink(),
            "corruption evidence must start absent")
    evidence_parent = evidence.parent
    evidence_parent_metadata = evidence_parent.lstat()
    require(
        stat.S_ISDIR(evidence_parent_metadata.st_mode)
        and not evidence_parent.is_symlink(),
        "corruption evidence parent is not a real directory",
    )
    require(
        evidence_parent_metadata.st_uid == os.geteuid()
        and stat.S_IMODE(evidence_parent_metadata.st_mode) == 0o700,
        "corruption evidence parent is not owner-private",
    )
    require(
        not state_root.is_relative_to(evidence_parent)
        and not evidence.is_relative_to(state_root),
        "corruption state and evidence roots overlap",
    )
    tw.private_directory(state_root)
    lock = (state_root / ".qualification.lock").open("a+b")
    os.chmod(lock.fileno(), 0o600)
    fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

    filesystem = subprocess.run(
        ["findmnt", "-n", "-o", "FSTYPE", "--target", str(state_root)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    ).stdout.strip()
    require(filesystem == "ext4", f"qualification root is not ext4: {filesystem}")

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
    nodes: list[object] = []
    started = time.monotonic()
    try:
        public_id = bootstrap_root / "PUBLIC_ID.txt"
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline and not (
            public_id.is_file() and public_id.stat().st_size == 64
        ):
            require(bootstrap_process.poll() is None, "bootstrap exited")
            time.sleep(0.05)
        bootstrap_key = public_id.read_text(encoding="ascii").strip()
        require(bool(tw.HEX64.fullmatch(bootstrap_key)), "bad bootstrap key")
        bootstrap = f"127.0.0.1:33445:{bootstrap_key}"

        nodes = [
            tw.Node(
                chr(97 + index),
                state_root / f"node-{index + 1}",
                phrase,
                binary,
                bootstrap,
            )
            for index, phrase in enumerate(tw.RECALL_PHRASES)
        ]
        for node in nodes:
            tw.private_directory(node.worktree)
        recovery.start_nodes(nodes)
        require(
            recovery.connect_full_mesh(nodes, args.namespace) == 6,
            "bad corruption share count",
        )
        recovery.seed_initial_tree(nodes[0], 4, 4096)
        expected = recovery.operator_tree_summary(nodes[0].worktree)
        tw.wait_for(
            "metadata corruption baseline convergence",
            nodes,
            lambda: all(
                tw.branch_count(node, args.namespace) == 3
                and not tw.conflict_files(node)
                and recovery.operator_tree_summary(node.worktree) == expected
                for node in nodes
            ),
            180,
        )
        recovery.repair_all(nodes, args.namespace)

        target = nodes[2]
        checkpoint = target.command(
            "sync-checkpoint", args.namespace, timeout=120
        ).stdout
        record_digest = tw.token_field(checkpoint, "record").lower()
        require(bool(HEX64.fullmatch(record_digest)), "checkpoint record is absent")
        target.command("sync-pin", args.namespace, record_digest, timeout=120)
        retention = target.command("sync-retention", args.namespace).stdout
        require(tw.unsigned_field(retention, "pins") == 1, "pin is absent")
        tw.wait_for(
            "checkpoint convergence before corruption",
            nodes,
            lambda: all(tw.branch_count(node, args.namespace) == 3 for node in nodes),
            180,
        )
        recovery.repair_all(nodes, args.namespace)

        # Stop both peers so no legitimate publication can race the exact
        # same-size corruption/restoration sequence on the selected node.
        for peer in nodes[:2]:
            peer.stop()
        baseline_identity = target.principal.lower()
        baseline_tree = recovery.operator_tree_summary(target.worktree)
        tree_root = target.policy_root / "data" / args.namespace / "tree-v2"
        pointer_path = tree_root / "branches" / f"{baseline_identity}.branch"
        pointer_bytes = pointer_path.read_bytes()
        require(
            len(pointer_bytes) >= 128 and pointer_bytes[:8] == b"IOTXTVB1",
            "current branch pointer is not canonical",
        )
        manifest_digest = pointer_bytes[96:128].hex()
        require(bool(HEX64.fullmatch(manifest_digest)), "manifest digest is invalid")
        families = (
            ("branch-pointer", pointer_path),
            ("manifest", tree_root / "manifests" / f"{manifest_digest}.manifest"),
            # TreeV2BranchStore loads the pointer, then its referenced
            # manifest, and only then derives and loads the immutable branch
            # record. Keep this receipt order equal to that actual cold-start
            # validation order.
            ("immutable-branch-record", tree_root / "records" / f"{record_digest}.branch"),
            ("workspace", tree_root / "workspace.state"),
            ("maintenance", tree_root / "maintenance.state"),
        )
        family_receipts: list[dict[str, object]] = []
        for family, path in families:
            original, corrupt = corrupt_in_place(path)
            live = target.command(
                "sync-repair", args.namespace, timeout=120, check=False
            )
            detail = (live.stderr or live.stdout).lower()
            require(
                live.returncode == 4 and "error=protocol-error" in detail,
                f"sync-repair did not return protocol-error exit 4 for {family}",
            )
            require(
                family.replace("-", " ") in detail,
                f"sync-repair did not classify corrupt {family}: {detail.strip()}",
            )
            require(path.read_bytes() == corrupt, f"sync-repair mutated {family}")

            controlled_shutdown_exit = controlled_stop(target)
            require(path.read_bytes() == corrupt, f"shutdown mutated {family}")
            startup_exit, startup_log_sha256 = startup_refusal(
                target, state_root, family
            )
            require(path.read_bytes() == corrupt, f"startup mutated {family}")

            write_in_place_exact(path, original)
            target.start()
            tw.wait_for(
                f"{family} exact restoration startup",
                [target],
                lambda: (target.runtime / "control.sock").is_socket()
                and target.command("status", check=False).returncode == 0,
                60,
            )
            restored_identity = tw.field(
                target.command("identity").stdout, "device-public-key"
            ).lower()
            require(restored_identity == baseline_identity,
                    f"identity changed after {family} restoration")
            repaired = target.command(
                "sync-repair", args.namespace, timeout=120
            ).stdout
            require(
                "metadata=verified" in repaired
                and "workspace=present" in repaired
                and "maintenance=present" in repaired
                and "verified=1" in repaired,
                f"{family} restoration did not verify",
            )
            require(path.read_bytes() == original,
                    f"restored {family} changed after verification")
            require(recovery.operator_tree_summary(target.worktree) == baseline_tree,
                    f"worktree changed across {family} corruption")
            family_receipts.append(
                {
                    "family": family,
                    "bytes": len(original),
                    "original_sha256": sha256_bytes(original),
                    "corrupt_sha256": sha256_bytes(corrupt),
                    "mutation": "last-byte-xor-01",
                    "live_repair_refused": True,
                    "live_repair_exit": 4,
                    "live_repair_error": "protocol-error",
                    "live_corrupt_bytes_retained": True,
                    "startup_refused": True,
                    "controlled_shutdown_exit": controlled_shutdown_exit,
                    "startup_exit": startup_exit,
                    "startup_log_sha256": startup_log_sha256,
                    "startup_family_classified": True,
                    "startup_corrupt_bytes_retained": True,
                    "exact_restoration_verified": True,
                    "restoration":
                        "exact-original-in-place-fsync-file-and-parent",
                }
            )

        # Corrupt all five signed roots together. Startup and repair report the
        # first invalid root in their frozen validation order; restoring that
        # one must expose the next root without changing any other bytes.
        simultaneous_records: list[dict[str, object]] = []
        simultaneous_originals: dict[str, bytes] = {}
        simultaneous_corrupt: dict[str, bytes] = {}
        stopped_task_count = suspend_agent_tasks(target)
        try:
            for family, path in families:
                original, corrupt = corrupt_in_place(path)
                simultaneous_originals[family] = original
                simultaneous_corrupt[family] = corrupt
                simultaneous_records.append(
                    {
                        "family": family,
                        "bytes": len(original),
                        "original_sha256": sha256_bytes(original),
                        "corrupt_sha256": sha256_bytes(corrupt),
                    }
                )
                prior = family_receipts[len(simultaneous_records) - 1]
                require(
                    len(original) == prior["bytes"]
                    and sha256_bytes(original) == prior["original_sha256"]
                    and sha256_bytes(corrupt) == prior["corrupt_sha256"],
                    f"{family} changed between sequential and simultaneous cells",
                )
            require(
                all(
                    path.read_bytes() == simultaneous_corrupt[family]
                    for family, path in families
                ),
                "simultaneous corrupt roots were not co-resident before resume",
            )
            require(target.process is not None, "Agent process is absent")
            require(
                stopped_agent_task_count(target.process.pid, timeout=1.0)
                == stopped_task_count,
                "Agent task set changed during simultaneous corruption",
            )
        finally:
            resume_agent_tasks(target)

        simultaneous_live = target.command(
            "sync-repair", args.namespace, timeout=120, check=False
        )
        simultaneous_live_detail = (
            simultaneous_live.stderr or simultaneous_live.stdout
        ).lower()
        require(
            simultaneous_live.returncode == 4
            and "error=protocol-error" in simultaneous_live_detail
            and "branch pointer" in simultaneous_live_detail,
            "simultaneous sync-repair did not refuse at the branch pointer",
        )
        require(
            all(
                path.read_bytes() == simultaneous_corrupt[family]
                for family, path in families
            ),
            "simultaneous sync-repair changed corrupt metadata",
        )

        simultaneous_controlled_shutdown_exit = controlled_stop(target)
        initial_startup_exit, initial_startup_log_sha256 = startup_refusal(
            target, state_root, families[0][0], "simultaneous-all"
        )
        require(
            all(
                path.read_bytes() == simultaneous_corrupt[family]
                for family, path in families
            ),
            "simultaneous cold startup changed corrupt metadata",
        )

        restoration_steps: list[dict[str, object]] = []
        for index, (family, path) in enumerate(families[:-1]):
            write_in_place_exact(path, simultaneous_originals[family])
            next_family = families[index + 1][0]
            startup_exit, startup_log_sha256 = startup_refusal(
                target,
                state_root,
                next_family,
                f"simultaneous-after-{family}",
            )
            require(
                all(
                    candidate.read_bytes()
                    == (
                        simultaneous_originals[candidate_family]
                        if candidate_index <= index
                        else simultaneous_corrupt[candidate_family]
                    )
                    for candidate_index, (candidate_family, candidate)
                    in enumerate(families)
                ),
                f"ordered restoration of {family} changed another root",
            )
            restoration_steps.append(
                {
                    "restored_family": family,
                    "next_refused_family": next_family,
                    "startup_exit": startup_exit,
                    "startup_log_sha256": startup_log_sha256,
                    "restored_prefix_retained": True,
                    "remaining_corrupt_bytes_retained": True,
                }
            )

        final_family, final_path = families[-1]
        write_in_place_exact(
            final_path, simultaneous_originals[final_family]
        )
        target.start()
        tw.wait_for(
            "simultaneous exact restoration startup",
            [target],
            lambda: (target.runtime / "control.sock").is_socket()
            and target.command("status", check=False).returncode == 0,
            60,
        )
        simultaneous_identity = tw.field(
            target.command("identity").stdout, "device-public-key"
        ).lower()
        simultaneous_repair = target.command(
            "sync-repair", args.namespace, timeout=120
        ).stdout
        require(
            "metadata=verified" in simultaneous_repair
            and "workspace=present" in simultaneous_repair
            and "maintenance=present" in simultaneous_repair
            and "verified=1" in simultaneous_repair,
            "simultaneous exact restoration did not verify",
        )
        require(
            all(
                path.read_bytes() == simultaneous_originals[family]
                for family, path in families
            ),
            "simultaneous exact restoration did not retain all originals",
        )
        require(
            simultaneous_identity == baseline_identity
            and recovery.operator_tree_summary(target.worktree) == baseline_tree,
            "simultaneous exact restoration changed identity or worktree",
        )
        simultaneous_receipt = {
            "family_count": len(simultaneous_records),
            "families": simultaneous_records,
            "mutation": "all-five-last-byte-xor-01-before-agent-resume",
            "mutation_fence": "agent-process-group-sigstop-all-tasks",
            "stopped_agent_tasks": stopped_task_count,
            "live_repair_refused": True,
            "live_repair_exit": 4,
            "live_repair_error": "protocol-error",
            "live_repair_family": families[0][0],
            "live_all_corrupt_bytes_retained": True,
            "initial_startup_refused": True,
            "controlled_shutdown_exit": simultaneous_controlled_shutdown_exit,
            "initial_startup_exit": initial_startup_exit,
            "initial_startup_family": families[0][0],
            "initial_startup_log_sha256": initial_startup_log_sha256,
            "initial_startup_all_corrupt_bytes_retained": True,
            "restoration_steps": restoration_steps,
            "final_restored_family": final_family,
            "final_startup_succeeded": True,
            "all_original_bytes_retained_after_recovery": True,
            "identity_preserved": True,
            "worktree_preserved": True,
            "exact_restoration_verified": True,
            "restoration":
                "ordered-exact-originals-in-place-fsync-file-and-parent",
        }

        for peer in nodes[:2]:
            peer.start()
        tw.wait_for(
            "all peers after metadata corruption campaign",
            nodes,
            lambda: all(
                (node.runtime / "control.sock").is_socket()
                and node.command("status", check=False).returncode == 0
                for node in nodes
            ),
            60,
        )
        tw.wait_for(
            "metadata corruption final convergence",
            nodes,
            lambda: all(
                tw.branch_count(node, args.namespace) == 3
                and not tw.conflict_files(node)
                and recovery.operator_tree_summary(node.worktree) == expected
                for node in nodes
            ),
            180,
        )
        recovery.repair_all(nodes, args.namespace)

        version = subprocess.run(
            [str(binary), "--version"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        ).stdout.strip()
        receipt = {
            "schema": "iotox.sync-metadata-corruption.v2",
            "status": "passed",
            "version": version,
            "binary_sha256": sha256_file(binary),
            "filesystem": filesystem,
            "network_class": "loopback-only-inside-networkless-vm",
            "node_count": 3,
            "directed_read_write_share_count": 6,
            "family_count": len(family_receipts),
            "families": family_receipts,
            "simultaneous": simultaneous_receipt,
            "identity_preserved": True,
            "final_branch_count": [tw.branch_count(node, args.namespace) for node in nodes],
            "final_files": expected["files"],
            "final_directories": expected["directories"],
            "final_bytes": expected["bytes"],
            "final_tree_sha256": expected["digest"],
            "final_repair_verified_nodes": 3,
            "elapsed_ms": int((time.monotonic() - started) * 1000),
            "automatic_signed_metadata_quarantine": False,
            "operator_supplied_exact_restoration": True,
            "power_cut": False,
            "dishonest_storage_assessed": False,
            "contains_secrets": False,
        }
        write_receipt(evidence, receipt)
        print(json.dumps(receipt, sort_keys=True), flush=True)
        return 0
    finally:
        for node in nodes:
            try:
                node.stop()
            except BaseException:
                pass
        if bootstrap_process.poll() is None:
            os.killpg(bootstrap_process.pid, signal.SIGTERM)
            try:
                bootstrap_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(bootstrap_process.pid, signal.SIGKILL)
                bootstrap_process.wait(timeout=5)
        bootstrap_log.close()
        lock.close()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, subprocess.SubprocessError) as error:
        print(f"sync metadata corruption rehearsal failed: {error}", file=sys.stderr)
        raise SystemExit(1)
