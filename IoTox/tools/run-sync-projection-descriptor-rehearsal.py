#!/usr/bin/env python3
"""Qualify externally held projection descriptors at real rename boundaries.

Two independent three-writer cells stop the production Agent at an exact
ptrace-observed RENAME_EXCHANGE entry or exit.  A separate helper process owns
the writable descriptor.  The second cell also proves ext4's writable-FD
read-only-remount refusal and the retained stage's persistence across a
closed-descriptor RO/RW remount.
"""

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
STORAGE = ROOT / "tools/run-sync-storage-fault-rehearsal.py"
POWER_CUT = ROOT / "tools/run-sync-power-cut-rehearsal.py"
SCHEMA = "iotox.sync-projection-descriptor.v1"
VALUE_BYTES = 64
STRACE_DELAY = "5s"


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


def exact_value(label: str) -> bytes:
    encoded = (label + "\n").encode("ascii")
    require(len(encoded) <= VALUE_BYTES, "descriptor value label is too long")
    return encoded + b"." * (VALUE_BYTES - len(encoded))


def fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def write_exact(path: Path, value: bytes) -> None:
    descriptor = os.open(
        path,
        os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_CLOEXEC | os.O_NOFOLLOW,
        0o600,
    )
    try:
        offset = 0
        while offset < len(value):
            count = os.write(descriptor, value[offset:])
            require(count > 0, "exact write made no progress")
            offset += count
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    os.chmod(path, 0o600, follow_symlinks=False)
    fsync_directory(path.parent)


def copy_exact(source: Path, destination: Path) -> None:
    value = source.read_bytes()
    destination.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    destination.parent.chmod(0o700)
    write_exact(destination, value)


def exact_private_file(path: Path) -> os.stat_result:
    metadata = path.lstat()
    require(not path.is_symlink(), f"descriptor path is a symlink: {path}")
    require(stat.S_ISREG(metadata.st_mode), f"descriptor path is not regular: {path}")
    require(metadata.st_uid == os.geteuid(), f"descriptor path owner differs: {path}")
    require(metadata.st_nlink == 1, f"descriptor path has multiple links: {path}")
    require(stat.S_IMODE(metadata.st_mode) & 0o022 == 0,
            f"descriptor path is group/world writable: {path}")
    require(metadata.st_size == VALUE_BYTES,
            f"descriptor path has unexpected size: {path}")
    return metadata


def descriptor_snapshot(descriptor: int) -> dict[str, object]:
    metadata = os.fstat(descriptor)
    require(stat.S_ISREG(metadata.st_mode), "held descriptor is not regular")
    require(metadata.st_nlink == 1, "held descriptor has multiple links")
    require(metadata.st_size == VALUE_BYTES, "held descriptor size changed")
    value = os.pread(descriptor, VALUE_BYTES, 0)
    require(len(value) == VALUE_BYTES, "held descriptor short-read")
    return {
        "pid": os.getpid(),
        "fd": descriptor,
        "device": metadata.st_dev,
        "inode": metadata.st_ino,
        "bytes": metadata.st_size,
        "sha256": sha256_bytes(value),
    }


def fd_helper(path: Path) -> int:
    descriptor = os.open(path, os.O_RDWR | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        print(json.dumps({"status": "ready", **descriptor_snapshot(descriptor)}),
              flush=True)
        for line in sys.stdin:
            request = json.loads(line)
            require(isinstance(request, dict), "helper request is not an object")
            operation = request.get("operation")
            if operation == "inspect":
                response = descriptor_snapshot(descriptor)
            elif operation == "write":
                encoded = request.get("value_hex")
                require(isinstance(encoded, str), "helper write value is absent")
                value = bytes.fromhex(encoded)
                require(len(value) == VALUE_BYTES,
                        "helper write must preserve the file size")
                offset = 0
                while offset < len(value):
                    count = os.pwrite(descriptor, value[offset:], offset)
                    require(count > 0, "held-descriptor write made no progress")
                    offset += count
                os.fsync(descriptor)
                response = descriptor_snapshot(descriptor)
                response["write_fsync"] = True
            elif operation == "close":
                print(json.dumps({"status": "closing"}), flush=True)
                return 0
            else:
                raise RuntimeError("unknown helper operation")
            print(json.dumps({"status": "ok", **response}), flush=True)
        raise RuntimeError("helper control pipe closed without close request")
    finally:
        os.close(descriptor)


class HeldWriter:
    def __init__(self, path: Path) -> None:
        self.process = subprocess.Popen(
            [sys.executable, str(Path(__file__).resolve()), "--fd-helper", str(path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            start_new_session=True,
        )
        self.closed = False
        ready = self._read()
        require(ready.get("status") == "ready", "descriptor helper did not start")
        self.initial = ready

    def _read(self) -> dict[str, object]:
        require(self.process.stdout is not None, "helper stdout is absent")
        line = self.process.stdout.readline()
        if not line:
            detail = ""
            if self.process.stderr is not None:
                detail = self.process.stderr.read()
            raise RuntimeError(f"descriptor helper exited early: {detail.strip()}")
        value = json.loads(line)
        require(isinstance(value, dict), "helper response is not an object")
        return value

    def request(self, operation: str, value: bytes | None = None) -> dict[str, object]:
        require(not self.closed, "descriptor helper is closed")
        require(self.process.stdin is not None, "helper stdin is absent")
        request: dict[str, object] = {"operation": operation}
        if value is not None:
            request["value_hex"] = value.hex()
        self.process.stdin.write(json.dumps(request) + "\n")
        self.process.stdin.flush()
        response = self._read()
        require(response.get("status") == "ok", "descriptor helper refused request")
        return response

    def inspect(self) -> dict[str, object]:
        return self.request("inspect")

    def write(self, value: bytes) -> dict[str, object]:
        return self.request("write", value)

    def close(self) -> None:
        if self.closed:
            return
        try:
            require(self.process.stdin is not None, "helper stdin is absent")
            self.process.stdin.write('{"operation":"close"}\n')
            self.process.stdin.flush()
            response = self._read()
            require(response.get("status") == "closing", "helper close was refused")
            result = self.process.wait(timeout=5)
            require(result == 0, f"descriptor helper exited {result}")
        finally:
            if self.process.poll() is None:
                os.killpg(self.process.pid, signal.SIGKILL)
                self.process.wait(timeout=5)
            self.closed = True


def same_identity(snapshot: dict[str, object], metadata: os.stat_result) -> bool:
    return (
        snapshot.get("device") == metadata.st_dev
        and snapshot.get("inode") == metadata.st_ino
        and snapshot.get("bytes") == metadata.st_size
    )


def write_receipt(path: Path, value: dict[str, object]) -> None:
    require(not path.exists() and not path.is_symlink(), "receipt already exists")
    encoded = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    descriptor = os.open(
        temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC, 0o600
    )
    try:
        offset = 0
        while offset < len(encoded):
            offset += os.write(descriptor, encoded[offset:])
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    os.link(temporary, path, follow_symlinks=False)
    temporary.unlink()
    fsync_directory(path.parent)


def controlled_stop(node: object) -> int:
    node.ensure_running()
    result = node.command("stop", timeout=15, check=False)
    require(result.returncode == 0, "Agent controlled stop was refused")
    require(node.process is not None, "Agent wrapper vanished before stop")
    exit_code = node.process.wait(timeout=20)
    require(exit_code == 0, f"Agent wrapper controlled stop exited {exit_code}")
    node.process = None
    if node.log_handle is not None:
        node.log_handle.close()
        node.log_handle = None
    return exit_code


def startup_refusal(node: object, log_path: Path) -> tuple[int, str]:
    control = node.runtime / "control.sock"
    try:
        control.unlink()
    except FileNotFoundError:
        pass
    with log_path.open("xb") as output:
        os.chmod(output.fileno(), 0o600)
        process = subprocess.Popen(
            node.args(), stdout=output, stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        try:
            exit_code = process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=5)
            raise RuntimeError("Agent remained live with ambiguous projection")
    detail = log_path.read_text(encoding="utf-8", errors="replace").lower()
    require(exit_code == 3, f"ambiguous startup exited {exit_code}, not 3")
    require("preserved for operator recovery" in detail,
            "ambiguous startup did not emit the preservation classification")
    require(not control.exists(), "ambiguous startup exposed a control socket")
    return exit_code, sha256_file(log_path)


def start_nodes(nodes: list[object], tw: object) -> None:
    for node in nodes:
        node.start()
    tw.wait_for(
        "projection descriptor control sockets", nodes,
        lambda: all(
            (node.runtime / "control.sock").is_socket()
            and node.command("status", check=False).returncode == 0
            for node in nodes
        ), 60,
    )
    for node in nodes:
        tw.discover_identity(node)
        tw.initialize_authority(node)


def connect_cell(nodes: list[object], namespace: str, unselected: bool,
                 tw: object) -> int:
    for node in nodes:
        arguments = [
            "sync-create", namespace, str(node.worktree), "read-write", "1",
        ]
        if unselected:
            arguments.extend(["owner-mode-v2", "exclude=local"])
        created = node.command(*arguments, timeout=60, check=False)
        require(created.returncode == 0,
                f"{node.name} namespace creation failed: "
                f"{(created.stderr or created.stdout).strip()}")
    for left, right in ((0, 1), (0, 2), (1, 2)):
        tw.connect_pair(nodes[left], nodes[right], nodes)
    shares = 0
    for node in nodes:
        for peer in nodes:
            if node is peer:
                continue
            tw.share(node, peer, namespace, nodes)
            shares += 1
    tw.wait_for(
        "projection descriptor automation", nodes,
        lambda: all(tw.automation_ready(node, namespace) for node in nodes), 180,
    )
    tw.wait_for(
        "projection descriptor branches", nodes,
        lambda: all(tw.branch_count(node, namespace) == 3 for node in nodes), 180,
    )
    return shares


def resume_traced_agent(node: object) -> None:
    require(node.process is not None, "traced Agent wrapper is absent")
    os.killpg(node.process.pid, signal.SIGCONT)
    node.ensure_running()


def projection_state(node: object, namespace: str, power: object) -> dict[str, object]:
    tree = node.policy_root / "data" / namespace / "tree-v2"
    workspace_path = tree / "workspace.state"
    stage = node.root / f".worktree.iotox-{namespace}.stage"
    snapshot = power.workspace_state_snapshot(workspace_path)
    return {
        "workspace": snapshot,
        "stage_present": power.path_present(stage),
        "visible_orientation": power.projection_orientation(
            node.worktree / ".iotox-conflicts" / ".iotox-projection",
            namespace, snapshot,
        ),
        "stage_orientation": power.projection_orientation(
            stage / ".iotox-conflicts" / ".iotox-projection",
            namespace, snapshot,
        ),
    }


def wait_exchange_boundary(node: object, namespace: str, phase: str,
                           timeout: int, power: object) -> tuple[int, dict[str, object]]:
    expected = (
        ("active", "pending") if phase == "entry" else ("pending", "active")
    )
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        node.ensure_running()
        trace_tid = power.traced_agent_thread(node)
        state = projection_state(node, namespace, power)
        workspace = state["workspace"]
        if (
            trace_tid is not None
            and workspace.get("state") == "pending"
            and state["stage_present"] is True
            and (state["visible_orientation"], state["stage_orientation"]) == expected
        ):
            try:
                power.stop_agent_at_boundary(node, trace_tid)
            except RuntimeError as exc:
                if "traced Agent identity vanished before boundary stop" in str(exc):
                    time.sleep(0.001)
                    continue
                raise
            stopped = projection_state(node, namespace, power)
            require(stopped == state, "projection state changed while stopping boundary")
            require(
                power.traced_agent_thread(node, trace_tid, require_stopped=True)
                == trace_tid,
                "exact traced worker was not retained at boundary",
            )
            return trace_tid, stopped
        time.sleep(0.0005)
    raise RuntimeError(f"renameat2 {phase} boundary was not observed")


def trace_pid(line: str) -> str:
    match = re.match(r"\[pid\s+(\d+)\]\s+", line)
    if match:
        return match.group(1)
    return ""


def validate_trace(trace: Path, worktree: Path, stage: Path) -> dict[str, object]:
    deadline = time.monotonic() + 5
    text = ""
    raw_lines: list[str] = []
    while time.monotonic() < deadline:
        try:
            text = trace.read_text(encoding="utf-8", errors="replace")
        except FileNotFoundError:
            text = ""
        raw_lines = [
            line for line in text.splitlines()
            if (
                ("renameat2(" in line and "RENAME_EXCHANGE" in line)
                or "<... renameat2 resumed>" in line
            )
        ]
        if raw_lines:
            break
        time.sleep(0.02)

    unfinished: dict[str, str] = {}
    successes: list[str] = []
    split_successes: list[str] = []
    for line in raw_lines:
        if "renameat2(" in line and "RENAME_EXCHANGE" in line:
            exact_paths = f'"{worktree}"' in line and f'"{stage}"' in line
            if not exact_paths:
                continue
            if re.search(r"RENAME_EXCHANGE\)\s+=\s+0(?:\s|$)", line) is not None:
                successes.append(line)
            elif "<unfinished ...>" in line:
                unfinished[trace_pid(line)] = line
            continue
        if "<... renameat2 resumed>" in line:
            prior = unfinished.get(trace_pid(line))
            if prior is not None and re.search(r"\)\s+=\s+0(?:\s|$)", line) is not None:
                split_successes.append(f"{prior} {line}")

    exact_successes = successes + split_successes
    require(
        len(exact_successes) == 1,
        "trace does not contain exactly one successful exact exchange: "
        f"raw_count={len(raw_lines)} success_count={len(exact_successes)} "
        f"sample={raw_lines[:4]!r}",
    )
    return {
        "exchange_count": 1,
        "raw_exchange_line_count": len(raw_lines),
        "split_exchange_observed": bool(split_successes),
        "trace_sha256": sha256_file(trace),
    }


def repair_refusal(node: object, namespace: str, classification: str) -> dict[str, object]:
    result = node.command("sync-repair", namespace, timeout=120, check=False)
    detail = (result.stderr or result.stdout).lower()
    require(result.returncode == 4 and "error=protocol-error" in detail,
            "ambiguous sync-repair did not return protocol-error exit 4: "
            f"exit={result.returncode} detail={detail.strip()!r}")
    require(classification in detail and "preserved for operator recovery" in detail,
            "ambiguous sync-repair used the wrong preservation classification: "
            f"expected={classification!r} detail={detail.strip()!r}")
    return {"exit": 4, "error": "protocol-error", "classification": classification}


def create_cell_nodes(cell_root: Path, binary: Path, bootstrap: str,
                      storage: object, tw: object, disk_mib: int
                      ) -> tuple[list[object], list[object]]:
    images = cell_root / "images"
    mounts = cell_root / "mounts"
    tw.private_directory(images)
    tw.private_directory(mounts)
    volumes = []
    nodes = []
    for index, phrase in enumerate(tw.RECALL_PHRASES):
        volume = storage.LoopExt4(
            images / f"node-{index + 1}.ext4",
            mounts / f"node-{index + 1}", disk_mib,
        )
        volume.create()
        volumes.append(volume)
        nodes.append(tw.Node(chr(97 + index), volume.mountpoint, phrase,
                             binary, bootstrap))
    return nodes, volumes


def run_cell(cell_name: str, *, binary: Path, bootstrap: str, state_root: Path,
             namespace: str, strace: Path, timeout: int, disk_mib: int,
             tw: object, recovery: object, storage: object, power: object
             ) -> dict[str, object]:
    unselected = cell_name == "post-exchange-unselected"
    phase = "exit" if unselected else "entry"
    cell_root = state_root / cell_name
    tw.private_directory(cell_root)
    nodes: list[object] = []
    volumes: list[object] = []
    helper: HeldWriter | None = None
    second_helper: HeldWriter | None = None
    started = time.monotonic()
    try:
        nodes, volumes = create_cell_nodes(
            cell_root, binary, bootstrap, storage, tw, disk_mib
        )
        start_nodes(nodes, tw)
        require(connect_cell(nodes, namespace, unselected, tw) == 6,
                "cell did not create six directed read-write shares")

        baseline = exact_value(f"{cell_name}:baseline")
        first_mutation = exact_value(f"{cell_name}:held-write-1")
        second_mutation = exact_value(f"{cell_name}:held-write-2")
        trigger_before = exact_value(f"{cell_name}:trigger-before")
        trigger_after = exact_value(f"{cell_name}:trigger-after")
        write_exact(nodes[0].worktree / "trigger.bin", trigger_before)
        if not unselected:
            write_exact(nodes[0].worktree / "held.bin", baseline)

        tw.wait_for(
            f"{cell_name} baseline convergence", nodes,
            lambda: all(
                (node.worktree / "trigger.bin").is_file()
                and (node.worktree / "trigger.bin").read_bytes() == trigger_before
                and (unselected or (
                    (node.worktree / "held.bin").is_file()
                    and (node.worktree / "held.bin").read_bytes() == baseline
                ))
                for node in nodes
            ), timeout,
        )
        target = nodes[2]
        held_relative = Path("local/held.bin") if unselected else Path("held.bin")
        held_visible = target.worktree / held_relative
        if unselected:
            held_visible.parent.mkdir(mode=0o700, parents=True, exist_ok=False)
            write_exact(held_visible, baseline)
        recovery.repair_all(nodes, namespace)
        identities = [node.principal.lower() for node in nodes]
        helper = HeldWriter(held_visible)
        require(same_identity(helper.initial, exact_private_file(held_visible)),
                "external helper did not bind the visible held inode")

        target.stop()
        write_exact(nodes[0].worktree / "trigger.bin", trigger_after)
        tw.wait_for(
            f"{cell_name} remote successor", nodes[:2],
            lambda: all(
                (node.worktree / "trigger.bin").read_bytes() == trigger_after
                and tw.branch_count(node, namespace) == 3
                for node in nodes[:2]
            ), timeout,
        )

        stage = target.root / f".worktree.iotox-{namespace}.stage"
        trace = cell_root / "renameat2.strace"
        injection = (
            f"--inject=renameat2:delay_{'exit' if unselected else 'enter'}="
            f"{STRACE_DELAY}"
        )
        target.process_prefix = [
            str(strace), "-f", "-qq", "-s", "4096",
            "-P", str(target.worktree), "-P", str(stage),
            "--trace=renameat2", injection, "-o", str(trace),
        ]
        target.start()
        trace_tid, boundary = wait_exchange_boundary(
            target, namespace, phase, timeout, power
        )
        held_at_boundary = target.worktree / held_relative if phase == "entry" \
            else stage / held_relative
        require(same_identity(helper.inspect(), exact_private_file(held_at_boundary)),
                "held descriptor lost its inode at the exchange boundary")
        first_snapshot = helper.write(first_mutation)
        require(first_snapshot.get("write_fsync") is True,
                "first helper write was not fsynced")
        require(held_at_boundary.read_bytes() == first_mutation,
                "first descriptor bytes are not visible at the bound inode")
        resume_traced_agent(target)

        tw.wait_for(
            f"{cell_name} retained ambiguity", nodes,
            lambda: (
                stage.is_dir()
                and (stage / held_relative).is_file()
                and (stage / held_relative).read_bytes() == first_mutation
                and (target.worktree / "trigger.bin").read_bytes() == trigger_after
            ), timeout,
        )
        require(same_identity(helper.inspect(), exact_private_file(stage / held_relative)),
                "held descriptor does not name the retained stage inode")
        classification = (
            "preserved unselected projection changed"
            if unselected else "exchanged old projection changed"
        )
        refusal = repair_refusal(target, namespace, classification)
        retained_state = projection_state(target, namespace, power)
        require(
            retained_state["workspace"].get("state") == "pending"
            and retained_state["visible_orientation"] == "pending"
            and retained_state["stage_orientation"] == "active",
            "retained ambiguity lost its pending workspace or markers",
        )
        trace_record = validate_trace(trace, target.worktree, stage)

        common: dict[str, object] = {
            "cell": cell_name,
            "phase": phase,
            "syscall": "renameat2",
            "flag": "RENAME_EXCHANGE",
            "path_binding": "exact-visible-and-stage",
            "strace_injection": injection,
            "strace_delay": STRACE_DELAY,
            "trace_tid": trace_tid,
            "external_helper_pid": helper.initial["pid"],
            "external_helper_fd": helper.initial["fd"],
            "held_device": helper.initial["device"],
            "held_inode": helper.initial["inode"],
            "held_bytes": VALUE_BYTES,
            "baseline_sha256": sha256_bytes(baseline),
            "first_mutation_sha256": sha256_bytes(first_mutation),
            "retained_sha256": sha256_file(stage / held_relative),
            "descriptor_stage_identity_equal": True,
            "first_write_fsync": True,
            "boundary": boundary,
            "retained_state": retained_state,
            "repair_refusal": refusal,
            **trace_record,
        }

        if not unselected:
            salvage = cell_root / "operator-recovery" / "held.bin"
            copy_exact(stage / held_relative, salvage)
            controlled_stop(target)
            helper.close()
            helper = None
            write_exact(stage / held_relative, baseline)
            write_exact(target.worktree / held_relative, first_mutation)
            target.process_prefix = []
            target.start()
            tw.wait_for(
                "selected ambiguity recovery", nodes,
                lambda: (target.runtime / "control.sock").is_socket()
                and target.command("status", check=False).returncode == 0
                and not stage.exists(), 60,
            )
            tw.wait_for(
                "selected salvage convergence", nodes,
                lambda: all(
                    (node.worktree / "held.bin").read_bytes() == first_mutation
                    and (node.worktree / "trigger.bin").read_bytes() == trigger_after
                    for node in nodes
                ), timeout,
            )
            recovery.repair_all(nodes, namespace)
            common.update({
                "controlled_stop_exit": 0,
                "salvage_sha256": sha256_file(salvage),
                "salvage_reapplied": True,
                "final_sha256": sha256_file(nodes[0].worktree / "held.bin"),
                "final_converged_nodes": 3,
                "final_repair_verified_nodes": 3,
            })
        else:
            controlled_stop(target)
            busy = subprocess.run(
                ["mount", "-o", "remount,ro", str(volumes[2].mountpoint)],
                text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                check=False,
            )
            busy_detail = (busy.stderr or busy.stdout).lower()
            require(busy.returncode != 0 and "busy" in busy_detail,
                    "ext4 did not refuse RO remount with writable descriptor")
            require(same_identity(helper.inspect(), exact_private_file(stage / held_relative)),
                    "busy remount attempt changed descriptor identity")
            require((stage / held_relative).read_bytes() == first_mutation,
                    "busy remount attempt changed retained bytes")
            helper.close()
            helper = None

            before_remount = exact_private_file(stage / held_relative)
            volumes[2].remount(True)
            require((stage / held_relative).read_bytes() == first_mutation,
                    "read-only remount changed retained bytes")
            volumes[2].remount(False)
            after_remount = exact_private_file(stage / held_relative)
            require(
                before_remount.st_dev == after_remount.st_dev
                and before_remount.st_ino == after_remount.st_ino,
                "RO/RW remount changed retained stage inode",
            )
            second_helper = HeldWriter(stage / held_relative)
            require(same_identity(second_helper.initial, after_remount),
                    "second helper did not reopen the retained inode")
            second_snapshot = second_helper.write(second_mutation)
            require(second_snapshot.get("write_fsync") is True,
                    "second helper write was not fsynced")
            second_helper_record = {
                "pid": second_helper.initial["pid"],
                "fd": second_helper.initial["fd"],
                "device": second_helper.initial["device"],
                "inode": second_helper.initial["inode"],
            }
            second_helper.close()
            second_helper = None
            require((stage / held_relative).read_bytes() == second_mutation,
                    "second descriptor bytes were not retained")

            target.process_prefix = []
            startup_exit, startup_log_sha256 = startup_refusal(
                target, cell_root / "ambiguous-startup.log"
            )
            require((stage / held_relative).read_bytes() == second_mutation,
                    "cold-start refusal changed retained bytes")
            require([node.principal.lower() for node in nodes] == identities,
                    "identity changed before salvage")

            salvage = cell_root / "operator-recovery" / "held.bin"
            copy_exact(stage / held_relative, salvage)
            write_exact(stage / held_relative, baseline)
            target.start()
            tw.wait_for(
                "unselected ambiguity recovery", nodes,
                lambda: (target.runtime / "control.sock").is_socket()
                and target.command("status", check=False).returncode == 0
                and not stage.exists(), 60,
            )
            published = target.worktree / "recovered" / "held.bin"
            copy_exact(salvage, published)
            tw.wait_for(
                "explicit salvage publication", nodes,
                lambda: all(
                    (node.worktree / "recovered" / "held.bin").is_file()
                    and (node.worktree / "recovered" / "held.bin").read_bytes()
                    == second_mutation
                    and (node.worktree / "trigger.bin").read_bytes() == trigger_after
                    for node in nodes
                ), timeout,
            )
            recovery.repair_all(nodes, namespace)
            common.update({
                "controlled_stop_exit": 0,
                "busy_remount_exit_nonzero": True,
                "busy_remount_classification": "mount-point-busy",
                "descriptor_unchanged_after_busy_remount": True,
                "helper_closed_before_successful_remount": True,
                "read_only_remount_succeeded": True,
                "read_write_remount_succeeded": True,
                "stage_inode_preserved_across_remount": True,
                "second_helper": second_helper_record,
                "second_mutation_sha256": sha256_bytes(second_mutation),
                "cold_start_refused": True,
                "cold_start_exit": startup_exit,
                "cold_start_log_sha256": startup_log_sha256,
                "cold_start_control_socket_exposed": False,
                "cold_start_retained_sha256": sha256_file(salvage),
                "identity_preserved": True,
                "salvage_sha256": sha256_file(salvage),
                "salvage_reapplied_as": "recovered/held.bin",
                "final_sha256": sha256_file(published),
                "final_converged_nodes": 3,
                "final_repair_verified_nodes": 3,
            })
        common["elapsed_ms"] = int((time.monotonic() - started) * 1000)
        return common
    finally:
        if second_helper is not None:
            try:
                second_helper.close()
            except BaseException:
                pass
        if helper is not None:
            try:
                helper.close()
            except BaseException:
                pass
        for node in nodes:
            try:
                node.stop()
            except BaseException:
                pass
        for volume in reversed(volumes):
            try:
                volume.unmount()
            except BaseException:
                pass


def self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="iotox-projection-descriptor-") as raw:
        root = Path(raw)
        root.chmod(0o700)
        held = root / "held.bin"
        baseline = exact_value("self-test-baseline")
        mutated = exact_value("self-test-mutated")
        write_exact(held, baseline)
        helper = HeldWriter(held)
        try:
            initial = exact_private_file(held)
            require(same_identity(helper.initial, initial), "self-test inode mismatch")
            written = helper.write(mutated)
            require(written.get("sha256") == sha256_bytes(mutated),
                    "self-test helper digest mismatch")
            require(held.read_bytes() == mutated, "self-test write mismatch")
        finally:
            helper.close()
        worktree = root / "worktree.bin"
        stage = root / "stage.bin"
        full = root / "full.strace"
        split = root / "split.strace"
        full.write_text(
            f'renameat2(AT_FDCWD, "{worktree}", AT_FDCWD, "{stage}", '
            "RENAME_EXCHANGE) = 0\n",
            encoding="utf-8",
        )
        split.write_text(
            f'[pid 123] renameat2(AT_FDCWD, "{worktree}", AT_FDCWD, "{stage}", '
            "RENAME_EXCHANGE <unfinished ...>\n"
            "[pid 123] <... renameat2 resumed>) = 0\n",
            encoding="utf-8",
        )
        require(validate_trace(full, worktree, stage)["exchange_count"] == 1,
                "self-test full trace exchange mismatch")
        split_record = validate_trace(split, worktree, stage)
        require(split_record["exchange_count"] == 1,
                "self-test split trace exchange mismatch")
        require(split_record["split_exchange_observed"] is True,
                "self-test split trace flag mismatch")
    print("sync-projection-descriptor-rehearsal-self-test=pass")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--fd-helper", type=Path)
    parser.add_argument("--iotox", type=Path)
    parser.add_argument("--bootstrap", type=Path)
    parser.add_argument("--strace", type=Path)
    parser.add_argument("--three-writer-helper", type=Path, default=THREE_WRITER)
    parser.add_argument("--recovery-helper", type=Path, default=RECOVERY)
    parser.add_argument("--storage-helper", type=Path, default=STORAGE)
    parser.add_argument("--power-cut-helper", type=Path, default=POWER_CUT)
    parser.add_argument("--state-root", type=Path)
    parser.add_argument("--evidence", type=Path)
    parser.add_argument("--namespace", default="descriptor-notes")
    parser.add_argument("--disk-mib", type=int, default=128)
    parser.add_argument("--timeout", type=int, default=240)
    args = parser.parse_args()
    if args.fd_helper is not None:
        return fd_helper(args.fd_helper.resolve())
    if args.self_test:
        self_test()
        return 0
    require(
        args.iotox is not None and args.bootstrap is not None
        and args.strace is not None and args.state_root is not None
        and args.evidence is not None,
        "runtime mode requires iotox, bootstrap, strace, state-root, and evidence",
    )
    require(64 <= args.disk_mib <= 1024, "per-node disk size is outside its bound")
    require(60 <= args.timeout <= 1800, "timeout is outside its bound")

    tw = load_module(args.three_writer_helper.resolve(), "iotox_tw_descriptor")
    recovery = load_module(args.recovery_helper.resolve(), "iotox_recovery_descriptor")
    storage = load_module(args.storage_helper.resolve(), "iotox_storage_descriptor")
    power = load_module(args.power_cut_helper.resolve(), "iotox_power_descriptor")
    recovery.tw = tw
    binary = args.iotox.resolve()
    bootstrap_binary = args.bootstrap.resolve()
    strace = args.strace.resolve()
    state_root = args.state_root.resolve()
    evidence = args.evidence.resolve()
    require(binary.is_file(), "IoTox binary is absent")
    require(bootstrap_binary.is_file(), "bootstrap binary is absent")
    require(strace.is_file(), "strace is absent")
    require(not state_root.exists(), "descriptor state root must start absent")
    require(not evidence.exists() and not evidence.is_symlink(),
            "descriptor evidence must start absent")
    tw.private_directory(state_root)
    tw.private_directory(evidence.parent)
    lock = (state_root / ".qualification.lock").open("a+b")
    os.chmod(lock.fileno(), 0o600)
    fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

    bootstrap_root = state_root / "bootstrap"
    tw.private_directory(bootstrap_root)
    bootstrap_log = (bootstrap_root / "bootstrap.log").open("ab")
    bootstrap_process = subprocess.Popen(
        [str(bootstrap_binary), "--ipv4"], cwd=bootstrap_root,
        stdout=bootstrap_log, stderr=subprocess.STDOUT, start_new_session=True,
    )
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
        require(bool(tw.HEX64.fullmatch(bootstrap_key)), "bootstrap key is invalid")
        bootstrap = f"127.0.0.1:33445:{bootstrap_key}"

        cells = []
        for name in ("pre-exchange-selected", "post-exchange-unselected"):
            print(f"projection-descriptor stage={name} begin", flush=True)
            cells.append(run_cell(
                name, binary=binary, bootstrap=bootstrap,
                state_root=state_root, namespace=args.namespace,
                strace=strace, timeout=args.timeout, disk_mib=args.disk_mib,
                tw=tw, recovery=recovery, storage=storage, power=power,
            ))
            print(f"projection-descriptor stage={name} passed", flush=True)

        version = subprocess.run(
            [str(binary), "--version"], text=True, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, check=True,
        ).stdout.strip()
        receipt = {
            "schema": SCHEMA,
            "status": "passed",
            "version": version,
            "binary_sha256": sha256_file(binary),
            "network_class": "loopback-only-inside-networkless-vm",
            "virtualization_required": "kvm",
            "filesystem": "ext4",
            "node_count_per_cell": 3,
            "directed_read_write_share_count_per_cell": 6,
            "cell_count": 2,
            "cells": cells,
            "ptrace_controller": "external-strace",
            "product_test_seam": False,
            "same_fd_across_ro_rw_remount": False,
            "same_fd_remount_nonclaim_reason": "ext4-refuses-ro-remount-busy",
            "salvage_is_automatic_merge": False,
            "elapsed_ms": int((time.monotonic() - started) * 1000),
            "contains_secrets": False,
        }
        write_receipt(evidence, receipt)
        print(json.dumps(receipt, sort_keys=True), flush=True)
        return 0
    finally:
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
    except (RuntimeError, OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"sync projection descriptor rehearsal failed: {error}", file=sys.stderr)
        raise SystemExit(1)
