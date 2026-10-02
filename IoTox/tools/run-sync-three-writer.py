#!/usr/bin/env python3
"""Qualify one full-mesh, three-writer IoTox namespace.

The default state root is persistent so ordinary development runs reuse the
same device and Tox keys.  ``--fresh-state`` is the explicit from-scratch gate.
Only content-free evidence leaves the state root.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import time
from dataclasses import dataclass, field as dataclass_field
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_STATE_ROOT = ROOT / ".cache/sync-three-writer/state"
DEFAULT_EVIDENCE_ROOT = ROOT / ".sandwurm/three-writer"
RECALL_PHRASES = (
    "abacus abdomen abdominal abide abiding ability ablaze able",
    "abnormal abrasion abrasive abreast abridge abroad abruptly absence",
    "absentee absently absinthe absolute absolve abstain abstract absurd",
)
HEX64 = re.compile(r"^[0-9A-Fa-f]{64}$")
HEX76 = re.compile(r"^[0-9A-Fa-f]{76}$")


class QualificationError(RuntimeError):
    pass


class InterruptedRun(QualificationError):
    pass


def interrupt_handler(signum: int, _frame: object) -> None:
    try:
        name = signal.Signals(signum).name
    except ValueError:
        name = str(signum)
    raise InterruptedRun(f"interrupted by {name}")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise QualificationError(message)


def field(text: str, name: str) -> str:
    prefix = f"{name}="
    for line in text.splitlines():
        if line.startswith(prefix):
            return line[len(prefix) :]
    return ""


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def private_directory(path: Path) -> None:
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    path.chmod(0o700)


def progress(started: float, message: str) -> None:
    elapsed = time.monotonic() - started
    print(f"stage elapsed={elapsed:.1f}s {message}", flush=True)


def subprocess_timeout_for_control_timeout(control_timeout_ms: int) -> int:
    return max(120, (control_timeout_ms + 999) // 1000 + 30)


def effective_soak_restart_settle_policy(args: argparse.Namespace) -> str:
    if args.soak_restart_every == 0:
        return "none"
    return args.soak_restart_settle_policy


def should_skip_soak_final_boundary_restart(
    *,
    policy: str,
    soak_seconds: float,
    soak_minimum_cycles: int,
    soak_restart_every: int,
    cycle: int,
    completed_cycles: int,
    now: float,
    deadline: float,
    repair_deferred: bool,
) -> bool:
    if policy != "skip-if-floor-satisfied":
        return False
    if repair_deferred:
        return False
    if soak_seconds <= 0.0 or soak_minimum_cycles <= 0:
        return False
    if soak_restart_every <= 0 or cycle % soak_restart_every != 0:
        return False
    if completed_cycles + 1 < soak_minimum_cycles:
        return False
    return now >= deadline


@dataclass
class Node:
    name: str
    root: Path
    phrase: str
    binary: Path
    bootstrap: str
    run_args: list[str] = dataclass_field(default_factory=list)
    process_prefix: list[str] = dataclass_field(default_factory=list)
    process: subprocess.Popen[bytes] | None = None
    log_handle: object | None = None
    address: str = ""
    tox_key: str = ""
    principal: str = ""

    @property
    def runtime(self) -> Path:
        return self.root / "runtime"

    @property
    def worktree(self) -> Path:
        return self.root / "worktree"

    @property
    def policy_root(self) -> Path:
        return self.root / "sync-policy"

    def args(self) -> list[str]:
        return [
            str(self.binary),
            "run",
            "--runtime",
            str(self.runtime),
            "--state",
            str(self.root / "device.toxsave"),
            "--identity",
            str(self.root / "device.identity"),
            "--authority-ledger",
            str(self.root / "authority.ledger"),
            "--command-store",
            str(self.root / "commands.store"),
            "--no-default-bootstrap",
            "--no-default-relays",
            "--bootstrap",
            self.bootstrap,
            "--bootstrap-retry-ms",
            "500",
            "--enable-sync",
            "--sync-policy-root",
            str(self.policy_root),
            *self.run_args,
        ]

    def start(self) -> None:
        private_directory(self.root)
        private_directory(self.worktree)
        private_directory(self.policy_root)
        control = self.runtime / "control.sock"
        if control.exists() or control.is_socket():
            control.unlink()
        self.log_handle = (self.root / "agent.log").open("ab")
        self.process = subprocess.Popen(
            [*self.process_prefix, *self.args()],
            stdout=self.log_handle,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )

    def ensure_running(self) -> None:
        require(self.process is not None, f"{self.name} was not started")
        result = self.process.poll()
        if result is not None:
            tail = (self.root / "agent.log").read_text(
                encoding="utf-8", errors="replace"
            )[-4000:]
            raise QualificationError(
                f"{self.name} exited {result}; log tail follows:\n{tail}"
            )

    def command(
        self,
        *arguments: str,
        input_text: str | None = None,
        timeout: int = 30,
        control_timeout_ms: int | None = None,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        self.ensure_running()
        command = [str(self.binary), "--runtime", str(self.runtime)]
        if control_timeout_ms is not None:
            command.extend(["--timeout-ms", str(control_timeout_ms)])
        command.extend(arguments)
        result = subprocess.run(
            command,
            input=input_text,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
        if check and result.returncode != 0:
            detail = (result.stderr or result.stdout).strip()
            raise QualificationError(
                f"{self.name} {' '.join(arguments)} failed: {detail}"
            )
        return result

    def sync_repair(
        self,
        namespace: str,
        *,
        control_timeout_ms: int,
        timeout: int | None = None,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        return self.command(
            "sync-repair",
            namespace,
            timeout=(
                timeout
                if timeout is not None
                else subprocess_timeout_for_control_timeout(control_timeout_ms)
            ),
            control_timeout_ms=control_timeout_ms,
            check=check,
        )

    def stop(self) -> None:
        if self.process is None:
            return
        if self.process.poll() is None:
            try:
                self.command("stop", timeout=5, check=False)
            except subprocess.TimeoutExpired:
                pass
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(self.process.pid, signal.SIGTERM)
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(self.process.pid, signal.SIGKILL)
                    self.process.wait(timeout=5)
        self.process = None
        if self.log_handle is not None:
            self.log_handle.close()
            self.log_handle = None

    def kill_abrupt(self) -> int:
        """Kill the Agent process group without a control-plane shutdown."""
        self.ensure_running()
        assert self.process is not None
        pid = self.process.pid
        os.killpg(pid, signal.SIGKILL)
        result = self.process.wait(timeout=10)
        self.process = None
        if self.log_handle is not None:
            self.log_handle.close()
            self.log_handle = None
        return result


def process_wait_channels(node: Node) -> list[str]:
    if node.process is None or node.process.poll() is not None:
        return ["not-running"]
    task_root = Path(f"/proc/{node.process.pid}/task")
    channels: set[str] = set()
    try:
        for task in task_root.iterdir():
            try:
                channel = (task / "wchan").read_text(
                    encoding="ascii", errors="replace"
                ).strip()
            except OSError:
                continue
            if channel:
                channels.add(channel)
    except OSError:
        return ["unavailable"]
    return sorted(channels) or ["unavailable"]


def wait_for(
    description: str,
    nodes: list[Node],
    predicate: Callable[[], bool],
    timeout: float,
) -> None:
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        for node in nodes:
            node.ensure_running()
        try:
            if predicate():
                return
        except (OSError, subprocess.SubprocessError, QualificationError) as error:
            last_error = error
        time.sleep(0.1)
    suffix = f": {last_error}" if last_error is not None else ""
    raise QualificationError(f"timeout waiting for {description}{suffix}")


def initialize_authority(node: Node) -> None:
    snapshot = node.command("authority").stdout
    initialized = field(snapshot, "initialized") == "1"
    ledger_format = field(snapshot, "ledger-format").removeprefix("v")
    changed = False
    if not initialized:
        node.command(
            "authority-bootstrap-recall-stdin", input_text=node.phrase + "\n"
        )
        ledger_format = "1"
        changed = True
    if ledger_format == "1":
        node.command(
            "authority-migrate-v2-recall-stdin", input_text=node.phrase + "\n"
        )
        ledger_format = "2"
        changed = True
    if ledger_format == "2":
        node.command(
            "authority-migrate-v3-recall-stdin",
            "all",
            input_text=node.phrase + "\n",
        )
        ledger_format = "3"
        changed = True
    require(ledger_format == "3", f"{node.name} authority is not v3")
    if changed:
        owner = field(
            node.command(
                "recall-owner-public-key-stdin", input_text=node.phrase + "\n"
            ).stdout,
            "owner-public-key",
        )
        require(bool(HEX64.fullmatch(owner)), f"{node.name} owner is invalid")
        node.command(
            "authority-grant-recall-stdin",
            owner,
            "owner",
            "all-v3",
            input_text=node.phrase + "\n",
        )


def discover_identity(node: Node) -> None:
    node.address = node.command("address").stdout.strip()
    node.principal = field(node.command("identity").stdout, "device-public-key")
    require(bool(HEX76.fullmatch(node.address)), f"{node.name} Tox address is invalid")
    require(bool(HEX64.fullmatch(node.principal)), f"{node.name} principal is invalid")
    node.tox_key = node.address[:64]


def peer_present(node: Node, peer_key: str) -> bool:
    return peer_key.lower() in node.command("peers").stdout.lower()


def connect_pair(left: Node, right: Node, nodes: list[Node]) -> None:
    if not peer_present(left, right.tox_key):
        left.command(
            "transport-peer-request",
            right.address,
            "IoTox three-writer qualification",
        )
    if not peer_present(right, left.tox_key):
        wait_for(
            f"{left.name} friend request at {right.name}",
            nodes,
            lambda: left.tox_key.lower()
            in right.command("requests", check=False).stdout.lower(),
            60,
        )
        right.command("request-accept", left.tox_key)

    for node, peer in ((left, right), (right, left)):
        wait_for(
            f"confirmed {node.name} to {peer.name} session",
            nodes,
            lambda node=node, peer=peer: "state=confirmed"
            in node.command("session", peer.tox_key, check=False).stdout,
            120,
        )


def ensure_namespace(node: Node, namespace: str) -> None:
    result = node.command(
        "sync-create",
        namespace,
        str(node.worktree),
        "read-write",
        "1",
        check=False,
    )
    if result.returncode != 0:
        status = node.command("sync-automation").stdout
        require(
            f"namespace={namespace} " in status
            and "source-path-hex=" in status,
            f"{node.name} could not create or reuse {namespace}: "
            f"{(result.stderr or result.stdout).strip()}",
        )


def fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def set_namespace_lane_quota(node: Node, namespace: str, maximum_lanes: int) -> None:
    record = node.policy_root / "namespaces" / f"{namespace}.namespace"
    require(record.is_file(), f"{node.name} namespace record is absent")
    text = record.read_text(encoding="utf-8")
    require(
        f"id={namespace}\n" in text and "engine=tree-v2\n" in text,
        f"{node.name} namespace record is not the expected tree-v2 namespace",
    )
    outstanding = re.search(r"^maximum-outstanding-requests=([0-9]+)$", text, re.M)
    require(
        outstanding is not None and int(outstanding.group(1)) >= maximum_lanes,
        f"{node.name} namespace outstanding-request quota is below lane override",
    )
    text, replacements = re.subn(
        r"^maximum-lanes=[0-9]+$",
        f"maximum-lanes={maximum_lanes}",
        text,
        count=1,
        flags=re.M,
    )
    require(replacements == 1, f"{node.name} namespace lane quota is absent")
    temporary = record.with_name(f".{record.name}.lane-quota-{os.getpid()}.tmp")
    descriptor = os.open(
        temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC, 0o600
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as output:
            output.write(text)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, record)
        fsync_directory(record.parent)
    except BaseException:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
        raise
    lint = subprocess.run(
        [str(node.binary), "sync-namespace-lint", str(record)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    require(
        lint.returncode == 0,
        f"{node.name} namespace lane override did not lint: "
        f"{(lint.stderr or lint.stdout).strip()}",
    )


def start_nodes_after_policy_edit(nodes: list[Node]) -> None:
    for node in nodes:
        node.start()
    wait_for(
        "all local control sockets after namespace policy edit",
        nodes,
        lambda: all(
            (node.runtime / "control.sock").is_socket()
            and node.command("status", check=False).returncode == 0
            for node in nodes
        ),
        60,
    )


def share(node: Node, peer: Node, namespace: str, nodes: list[Node]) -> None:
    last = ""

    def attempt() -> bool:
        nonlocal last
        result = node.command(
            "sync-share",
            namespace,
            peer.tox_key,
            "read-write",
            input_text=node.phrase + "\n",
            timeout=60,
            check=False,
        )
        last = (result.stderr or result.stdout).strip()
        if result.returncode != 0 or "access=read-write" not in result.stdout:
            # A preceding edge can legitimately start a pull before the next
            # additive policy mutation.  Leave the Agent's event loop enough
            # time to finish that transfer instead of hammering its local
            # control socket at the generic 10 Hz predicate cadence.
            time.sleep(0.9)
            raise QualificationError(last or "sync-share returned no result")
        return True

    wait_for(
        f"{node.name} read-write share to {peer.name}", nodes, attempt, 180
    )
    require(not last or "error:" not in last.lower(), last)


def automation_ready(node: Node, namespace: str) -> bool:
    output = node.command("sync-automation", check=False).stdout
    return (
        f"namespace={namespace} mode=bidirectional" in output
        and "record-format=2" in output
        and "source-principals=2" in output
        and "source-principal-0=" in output
        and "source-principal-1=" in output
    )


def branch_count(node: Node, namespace: str) -> int:
    # This is a liveness predicate, not the integrity gate.  Polling the
    # authenticated sync-repair command at 10 Hz monopolized the first node's
    # local control/event loop and could itself prevent Tox progress.  Count
    # only canonical durable frontier names here; the campaign still invokes
    # sync-repair explicitly after capacity convergence.
    branches = (
        node.policy_root
        / "data"
        / namespace
        / "tree-v2"
        / "branches"
    )
    try:
        return sum(
            1
            for path in branches.iterdir()
            if path.is_file()
            and not path.is_symlink()
            and path.suffix == ".branch"
            and HEX64.fullmatch(path.stem)
        )
    except FileNotFoundError:
        return 0


def conflict_files(node: Node) -> list[Path]:
    root = node.worktree / ".iotox-conflicts" / "by-origin"
    if not root.is_dir():
        return []
    return sorted(path for path in root.rglob("*") if path.is_file())


def tree_allocated_bytes(root: Path) -> int:
    total = root.lstat().st_blocks * 512
    for path in root.rglob("*"):
        try:
            total += path.lstat().st_blocks * 512
        except FileNotFoundError:
            # Agent journals and staging files can disappear between rglob()
            # and lstat().  This is an operational high-water measurement, not
            # an authenticated inventory; omit only that vanished inode.
            continue
    return total


def process_high_water_kib(node: Node) -> int:
    node.ensure_running()
    assert node.process is not None
    status = Path(f"/proc/{node.process.pid}/status").read_text(
        encoding="ascii", errors="strict"
    )
    match = re.search(r"^VmHWM:\s+([0-9]+)\s+kB$", status, re.MULTILINE)
    require(match is not None, f"{node.name} process high-water RSS is absent")
    return int(match.group(1))


def tree_file_batch_summary(node: Node, namespace: str) -> dict[str, int]:
    """Return content-free high water across retained tree pull records."""
    output = node.command("sync-status", check=False).stdout
    header = output.splitlines()[0] if output else ""
    def field(line: str, name: str) -> int:
        match = re.search(rf"(?:^| ){re.escape(name)}=([0-9]+)(?: |$)", line)
        return int(match.group(1)) if match is not None else 0

    reconcile_fields = {
        "local_events": "reconcile-local-events",
        "branch_advances": "reconcile-branch-advances",
        "source_inspected": "reconcile-source-inspected",
        "source_hashed": "reconcile-source-hashed",
        "source_reused": "reconcile-source-reused",
        "cas_inspected": "reconcile-cas-inspected",
        "cas_inspected_bytes": "reconcile-cas-inspected-bytes",
        "cas_installed": "reconcile-cas-installed",
        "cas_installed_bytes": "reconcile-cas-installed-bytes",
        "cas_reused": "reconcile-cas-reused",
        "projection_dirs": "reconcile-projection-dirs",
        "projection_files": "reconcile-projection-files",
        "projection_bytes": "reconcile-projection-bytes",
        "projection_conflict_files": "reconcile-projection-conflict-files",
        "projection_conflict_tombstones": (
            "reconcile-projection-conflict-tombstones"
        ),
        "projection_preserved_entries": (
            "reconcile-projection-preserved-entries"
        ),
        "projection_preserved_dirs": "reconcile-projection-preserved-dirs",
        "projection_preserved_files": "reconcile-projection-preserved-files",
        "projection_preserved_bytes": "reconcile-projection-preserved-bytes",
    }
    reconcile = dict.fromkeys(reconcile_fields.keys(), 0)
    staged = 0
    for line in output.splitlines():
        if not line.startswith("tree-job=") or f" namespace={namespace} " not in line:
            continue
        staged = max(staged, field(line, "staged-file-objects"))
        for key, status_field in reconcile_fields.items():
            reconcile[key] += field(line, status_field)
    return {
        "staged": staged,
        "batches": field(header, "tree-file-commit-batches"),
        "largest": field(header, "tree-largest-file-commit-batch"),
        "inventory_scans": field(header, "tree-cas-full-inventory-scans"),
        "inventory_objects_inspected": field(
            header, "tree-cas-inventory-objects-inspected"
        ),
        "late": field(header, "tree-late-offers-cancelled"),
        "retired": field(header, "tree-retired-offer-ids"),
        "evictions": field(header, "tree-retired-offer-evictions"),
        "reconcile": reconcile,
    }


def partial_tree_v2_pull_summary(node: Node, namespace: str) -> dict[str, int]:
    """Return content-free retained/active tree-v2 pull state for rejection."""
    zero_fields = {
        "jobs": 0,
        "awaiting_inventory": 0,
        "awaiting_object": 0,
        "complete": 0,
        "failed": 0,
        "cancelled": 0,
        "manifest_file_objects": 0,
        "selected_file_objects": 0,
        "skipped_file_objects": 0,
        "selected_paths": 0,
        "skipped_paths": 0,
        "sources": 0,
        "availability_requests": 0,
        "availability_results": 0,
        "absent_results": 0,
        "unavailable_results": 0,
        "active_lanes": 0,
        "staged_file_objects": 0,
        "file_commit_batches": 0,
        "largest_file_commit_batch": 0,
        "cas_full_inventory_scans": 0,
        "cas_inventory_objects_inspected": 0,
        "requested_objects": 0,
        "committed_objects": 0,
        "reused_objects": 0,
        "fetched_bytes": 0,
        "accepted_branches": 0,
        "conflicts": 0,
        "lane_records": 0,
        "lane_admitted": 0,
        "lane_bytes": 0,
        "source_records": 0,
        "source_online": 0,
        "source_requested": 0,
        "source_offered": 0,
        "source_absent": 0,
        "source_unavailable": 0,
        "source_committed": 0,
        "source_fetched_bytes": 0,
    }
    try:
        output = node.command("sync-status", timeout=5, check=False).stdout
    except (OSError, subprocess.SubprocessError, QualificationError):
        return dict(zero_fields)

    def field(line: str, name: str) -> int:
        match = re.search(rf"(?:^| ){re.escape(name)}=([0-9]+)(?: |$)", line)
        return int(match.group(1)) if match is not None else 0

    def text_field(line: str, name: str) -> str:
        match = re.search(rf"(?:^| ){re.escape(name)}=([^ ]+)(?: |$)", line)
        return match.group(1) if match is not None else ""

    summary = dict(zero_fields)
    job_ids: set[int] = set()
    job_fields = {
        "manifest_file_objects": "manifest-file-objects",
        "selected_file_objects": "selected-file-objects",
        "skipped_file_objects": "skipped-file-objects",
        "selected_paths": "selected-paths",
        "skipped_paths": "skipped-paths",
        "sources": "sources",
        "availability_requests": "availability-requests",
        "availability_results": "availability-results",
        "absent_results": "absent-results",
        "unavailable_results": "unavailable-results",
        "active_lanes": "active-lanes",
        "staged_file_objects": "staged-file-objects",
        "file_commit_batches": "file-commit-batches",
        "cas_full_inventory_scans": "cas-full-inventory-scans",
        "cas_inventory_objects_inspected": "cas-inventory-objects-inspected",
        "requested_objects": "requested",
        "committed_objects": "committed",
        "reused_objects": "reused",
        "fetched_bytes": "fetched-bytes",
        "accepted_branches": "accepted-branches",
        "conflicts": "conflicts",
    }
    state_fields = {
        "awaiting-inventory": "awaiting_inventory",
        "awaiting-object": "awaiting_object",
        "complete": "complete",
        "failed": "failed",
        "cancelled": "cancelled",
    }
    for line in output.splitlines():
        if not line.startswith("tree-job=") or f" namespace={namespace} " not in line:
            continue
        job_id = field(line, "tree-job")
        if job_id == 0:
            continue
        job_ids.add(job_id)
        summary["jobs"] += 1
        state = state_fields.get(text_field(line, "state"))
        if state is not None:
            summary[state] += 1
        for key, status_field in job_fields.items():
            value = field(line, status_field)
            if key == "largest_file_commit_batch":
                summary[key] = max(summary[key], value)
            else:
                summary[key] += value

    for line in output.splitlines():
        if line.startswith("tree-lane-job="):
            job_id = field(line, "tree-lane-job")
            if job_id not in job_ids:
                continue
            summary["lane_records"] += 1
            summary["lane_admitted"] += field(line, "admitted")
            summary["lane_bytes"] += field(line, "bytes")
        elif line.startswith("tree-source-job="):
            job_id = field(line, "tree-source-job")
            if job_id not in job_ids:
                continue
            summary["source_records"] += 1
            summary["source_online"] += field(line, "online")
            summary["source_requested"] += field(line, "requested")
            summary["source_offered"] += field(line, "offered")
            summary["source_absent"] += field(line, "absent")
            summary["source_unavailable"] += field(line, "unavailable")
            summary["source_committed"] += field(line, "committed")
            summary["source_fetched_bytes"] += field(line, "fetched-bytes")
    return summary


def write_capacity_tree(root: Path, file_count: int, file_bytes: int) -> None:
    capacity = root / "capacity"
    private_directory(capacity)
    for index in range(file_count):
        seed = hashlib.sha256(
            f"iotox-three-writer-capacity-v1:{index}".encode("ascii")
        ).digest()
        repeats = (file_bytes + len(seed) - 1) // len(seed)
        payload = (seed * repeats)[:file_bytes]
        path = capacity / f"object-{index:04d}.bin"
        path.write_bytes(payload)
        # The three-writer qualification namespace intentionally retains the
        # historical executable-v1 metadata model.  Its stable file modes are
        # 0600 and 0700; owner-mode-v2 is qualified separately.
        path.chmod((0o600, 0o700)[index % 2])


def capacity_tree_summary(root: Path) -> dict[str, object]:
    capacity = root / "capacity"
    if not capacity.is_dir() or capacity.is_symlink():
        return {"files": 0, "bytes": 0, "digest": ""}
    digest = hashlib.sha256()
    files = sorted(path for path in capacity.rglob("*") if path.is_file())
    total_bytes = 0
    for path in files:
        require(not path.is_symlink(), "capacity tree contains a symlink")
        relative = path.relative_to(capacity).as_posix().encode("utf-8")
        content = path.read_bytes()
        mode = path.stat().st_mode & 0o700
        digest.update(len(relative).to_bytes(4, "big"))
        digest.update(relative)
        digest.update(mode.to_bytes(2, "big"))
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
        total_bytes += len(content)
    return {
        "files": len(files),
        "bytes": total_bytes,
        "digest": digest.hexdigest(),
    }


def capacity_tree_shape(root: Path) -> dict[str, int]:
    capacity = root / "capacity"
    if not capacity.is_dir() or capacity.is_symlink():
        return {"files": 0, "bytes": 0}
    files = [path for path in capacity.rglob("*") if path.is_file()]
    total_bytes = 0
    for path in files:
        require(not path.is_symlink(), "capacity tree contains a symlink")
        total_bytes += path.stat().st_size
    return {"files": len(files), "bytes": total_bytes}


def capacity_tree_matches(root: Path, expected: dict[str, object]) -> bool:
    shape = capacity_tree_shape(root)
    if shape["files"] != expected["files"] or shape["bytes"] != expected["bytes"]:
        return False
    return capacity_tree_summary(root) == expected


def regular_tree_shape(root: Path) -> dict[str, int]:
    if not root.is_dir() or root.is_symlink():
        return {"files": 0, "bytes": 0}
    files = 0
    total_bytes = 0
    for path in root.rglob("*"):
        if path.is_symlink() or not path.is_file():
            continue
        files += 1
        total_bytes += path.stat().st_size
    return {"files": files, "bytes": total_bytes}


def tree_v2_store_shape(node: Node, namespace: str) -> dict[str, int]:
    tree = node.policy_root / "data" / namespace / "tree-v2"
    objects = regular_tree_shape(tree / "objects")
    manifests = regular_tree_shape(tree / "manifests")
    records = regular_tree_shape(tree / "records")
    branches = regular_tree_shape(tree / "branches")
    incoming = regular_tree_shape(tree / "incoming")
    return {
        "objects": objects["files"],
        "object_bytes": objects["bytes"],
        "manifests": manifests["files"],
        "manifest_bytes": manifests["bytes"],
        "records": records["files"],
        "record_bytes": records["bytes"],
        "branches": branches["files"],
        "branch_bytes": branches["bytes"],
        "incoming_files": incoming["files"],
        "incoming_bytes": incoming["bytes"],
    }


def regular_file_summary(path: Path) -> dict[str, object]:
    try:
        if not path.is_file() or path.is_symlink():
            return {"exists": False, "bytes": 0, "sha256": ""}
        return {
            "exists": True,
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
    except OSError:
        return {"exists": False, "bytes": 0, "sha256": ""}


def partial_soak_projection_shape(node: Node) -> dict[str, object]:
    current = regular_file_summary(node.worktree / "soak" / "current.txt")
    toggle = regular_file_summary(node.worktree / "soak" / "toggle.txt")
    return {
        "current_exists": current["exists"],
        "current_bytes": current["bytes"],
        "current_sha256": current["sha256"],
        "toggle_exists": toggle["exists"],
        "toggle_bytes": toggle["bytes"],
        "toggle_sha256": toggle["sha256"],
    }


def wait_reconfirmed_full_mesh(nodes: list[Node], description: str) -> None:
    for left_index, right_index in ((0, 1), (0, 2), (1, 2)):
        for node, peer in (
            (nodes[left_index], nodes[right_index]),
            (nodes[right_index], nodes[left_index]),
        ):
            wait_for(
                f"{description}: {node.name} to {peer.name}",
                nodes,
                lambda node=node, peer=peer: "state=confirmed"
                in node.command("session", peer.tox_key, check=False).stdout,
                120,
            )


def write_private_text(path: Path, value: str) -> None:
    private_directory(path.parent)
    path.write_text(value, encoding="utf-8")
    path.chmod(0o600)


def read_text_if_file(path: Path) -> str | None:
    try:
        if path.is_file() and not path.is_symlink():
            return path.read_text(encoding="utf-8")
    except OSError:
        return None
    return None


def run_writable_soak(
    nodes: list[Node],
    namespace: str,
    args: argparse.Namespace,
    started: float,
    soak_progress: dict[str, object],
    note: Callable[[str], None],
) -> dict[str, object]:
    if args.soak_seconds == 0.0 and args.soak_minimum_cycles == 0:
        soak_progress.clear()
        soak_progress.update({"soak_campaign": False})
        return {"soak_campaign": False}

    soak_started = time.monotonic()
    deadline = soak_started + args.soak_seconds
    cycle_ms: list[int] = []
    cycles = 0
    delete_cycles = 0
    repair_passes = 0
    daemon_restarts = 0
    restart_index = 0
    restart_targets: list[str] = []
    restart_settle_policy = effective_soak_restart_settle_policy(args)
    restart_settle_passes = 0
    restart_settle_cycles: list[int] = []
    restart_skipped_final_boundary = 0
    restart_skipped_cycles: list[int] = []
    repair_deferred_cycles: list[int] = []
    repair_deferred = False
    stalled_cycle_recoveries: list[dict[str, object]] = []
    last_digest = ""
    log_each_cycle = (
        args.soak_minimum_cycles <= 1000 or args.soak_cycle_delay >= 60.0
    )
    soak_progress.clear()
    soak_progress.update(
        {
            "soak_campaign": True,
            "soak_completed": False,
            "soak_requested_seconds": int(args.soak_seconds),
            "soak_minimum_cycles": args.soak_minimum_cycles,
            "soak_cycle_delay_ms": int(args.soak_cycle_delay * 1000),
            "soak_restart_every": args.soak_restart_every,
            "soak_restart_phase": (
                "before-edit" if args.soak_restart_every > 0 else "none"
            ),
            "soak_restart_settle_policy": restart_settle_policy,
            "soak_final_boundary_restart_policy": (
                args.soak_final_boundary_restart_policy
            ),
            "soak_repair_every": args.soak_repair_every,
            "soak_repair_restart_policy": args.soak_repair_restart_policy,
            "sync_repair_control_timeout_ms": args.sync_repair_control_timeout_ms,
            "soak_stalled_restart_after_ms": int(
                args.soak_stalled_restart_after * 1000
            ),
            "soak_cycles": 0,
            "soak_elapsed_ms": 0,
            "soak_daemon_restarts": 0,
            "soak_restart_targets": [],
            "soak_restart_settle_passes": 0,
            "soak_restart_settle_cycles": [],
            "soak_restart_skipped_final_boundary": 0,
            "soak_restart_skipped_cycles": [],
            "soak_stalled_cycle_recoveries": 0,
            "soak_stalled_cycle_recovery_events": [],
            "soak_repair_passes": 0,
            "soak_repair_deferrals": 0,
            "soak_repair_deferred_cycles": [],
            "soak_repair_pending": False,
            "soak_delete_cycles": 0,
            "soak_contains_secrets": False,
        }
    )

    note(
        f"writable soak started seconds={args.soak_seconds:.3f} "
        f"minimum-cycles={args.soak_minimum_cycles} "
        f"cycle-delay={args.soak_cycle_delay:.3f} "
        f"timeout={args.timeout} "
        f"stalled-restart-after={args.soak_stalled_restart_after:.3f} "
        f"restart-settle-policy={restart_settle_policy} "
        f"final-boundary-restart-policy="
        f"{args.soak_final_boundary_restart_policy} "
        f"repair-policy={args.soak_repair_restart_policy} "
        f"repair-control-timeout-ms={args.sync_repair_control_timeout_ms} "
        f"cycle-log={'each' if log_each_cycle else 'sparse'}",
    )
    while (
        time.monotonic() < deadline
        or cycles < args.soak_minimum_cycles
        or repair_deferred
    ):
        cycle_started = time.monotonic()
        cycle = cycles + 1
        writer = nodes[cycles % len(nodes)]
        restarted_this_cycle = False
        scheduled_restart = (
            args.soak_restart_every > 0 and cycle % args.soak_restart_every == 0
        )
        if should_skip_soak_final_boundary_restart(
            policy=args.soak_final_boundary_restart_policy,
            soak_seconds=args.soak_seconds,
            soak_minimum_cycles=args.soak_minimum_cycles,
            soak_restart_every=args.soak_restart_every,
            cycle=cycle,
            completed_cycles=cycles,
            now=time.monotonic(),
            deadline=deadline,
            repair_deferred=repair_deferred,
        ):
            restart_skipped_final_boundary += 1
            restart_skipped_cycles.append(cycle)
            note(
                f"writable soak cycle {cycle} scheduled restart skipped at "
                "final boundary after satisfying wall-clock floor"
            )
            soak_progress["soak_restart_skipped_final_boundary"] = (
                restart_skipped_final_boundary
            )
            soak_progress["soak_restart_skipped_cycles"] = list(
                restart_skipped_cycles
            )
        elif scheduled_restart:
            restarted = nodes[restart_index % len(nodes)]
            restart_index += 1
            restart_targets.append(restarted.name)
            restarted_this_cycle = True
            note(
                f"writable soak cycle {cycle} restarting node "
                f"{restarted.name} before edit"
            )
            restarted.stop()
            restarted.start()
            wait_for(
                f"soak restarted node {restarted.name} control socket",
                nodes,
                lambda restarted=restarted: (
                    restarted.runtime / "control.sock"
                ).is_socket()
                and restarted.command("status", check=False).returncode == 0,
                60,
            )
            wait_reconfirmed_full_mesh(nodes, "soak post-restart session")
            daemon_restarts += 1
            soak_progress["soak_daemon_restarts"] = daemon_restarts
            soak_progress["soak_restart_targets"] = list(restart_targets)
            if restart_settle_policy == "repair-before-edit":
                note(
                    f"writable soak cycle {cycle} restart-settle sync-repair "
                    "started"
                )
                for node in nodes:
                    node.sync_repair(
                        namespace,
                        control_timeout_ms=args.sync_repair_control_timeout_ms,
                    )
                restart_settle_passes += 1
                restart_settle_cycles.append(cycle)
                note(
                    f"writable soak cycle {cycle} restart-settle sync-repair "
                    "completed"
                )
            soak_progress["soak_restart_settle_passes"] = restart_settle_passes
            soak_progress["soak_restart_settle_cycles"] = list(
                restart_settle_cycles
            )
            soak_progress["soak_restart_skipped_final_boundary"] = (
                restart_skipped_final_boundary
            )
            soak_progress["soak_restart_skipped_cycles"] = list(
                restart_skipped_cycles
            )

        current_value = f"soak cycle {cycle} from node {writer.name}\n"
        marker_value = f"soak marker {cycle}\n"
        write_private_text(writer.worktree / "soak" / "current.txt",
                           current_value)
        marker = writer.worktree / "soak" / "toggle.txt"
        marker_present = cycle % 2 == 1
        if marker_present:
            write_private_text(marker, marker_value)
        else:
            try:
                marker.unlink()
                delete_cycles += 1
            except FileNotFoundError:
                pass
        note(
            f"writable soak cycle {cycle} edit written writer={writer.name} "
            f"marker={'present' if marker_present else 'absent'}"
        )

        def node_soak_converged(node: Node) -> bool:
            current = node.worktree / "soak" / "current.txt"
            if read_text_if_file(current) != current_value:
                return False
            node_marker = node.worktree / "soak" / "toggle.txt"
            if marker_present:
                if read_text_if_file(node_marker) != marker_value:
                    return False
            elif node_marker.exists():
                return False
            return not conflict_files(node) and branch_count(node, namespace) == 3

        def soak_converged() -> bool:
            return all(node_soak_converged(node) for node in nodes)

        def lagging_soak_nodes() -> list[Node]:
            lagging = []
            for node in nodes:
                try:
                    if not node_soak_converged(node):
                        lagging.append(node)
                except (OSError, subprocess.SubprocessError, QualificationError):
                    lagging.append(node)
            return lagging

        try:
            wait_for(
                f"writable soak cycle {cycle}",
                nodes,
                soak_converged,
                (
                    args.soak_stalled_restart_after
                    if args.soak_stalled_restart_after > 0.0
                    else args.timeout
                ),
            )
        except QualificationError:
            if args.soak_stalled_restart_after == 0.0:
                raise
            targets = lagging_soak_nodes()
            if not targets:
                targets = [writer]
            target_names = [node.name for node in targets]
            event = {
                "cycle": cycle,
                "writer": writer.name,
                "targets": target_names,
                "wait_channels_by_node": [
                    {
                        "node": node.name,
                        "wait_channels": process_wait_channels(node),
                    }
                    for node in targets
                ],
            }
            note(
                f"writable soak cycle {cycle} stalled; restarting "
                f"targets={','.join(target_names)}"
            )
            for target in targets:
                target.stop()
                target.start()
                wait_for(
                    f"soak stalled-recovery node {target.name} control socket",
                    nodes,
                    lambda target=target: (
                        target.runtime / "control.sock"
                    ).is_socket()
                    and target.command("status", check=False).returncode == 0,
                    60,
                )
            wait_reconfirmed_full_mesh(nodes, "soak stalled-recovery session")
            for node in nodes:
                node.sync_repair(
                    namespace,
                    control_timeout_ms=args.sync_repair_control_timeout_ms,
                    check=False,
                )
            repair_passes += 1
            stalled_cycle_recoveries.append(event)
            soak_progress.update(
                {
                "soak_repair_passes": repair_passes,
                "soak_repair_pending": repair_deferred,
                "soak_stalled_cycle_recoveries": len(
                    stalled_cycle_recoveries
                ),
                    "soak_stalled_cycle_recovery_events": list(
                        stalled_cycle_recoveries
                    ),
                }
            )
            wait_for(
                f"writable soak cycle {cycle} after stalled recovery",
                nodes,
                soak_converged,
                args.timeout,
            )

        repair_due = (
            args.soak_repair_every > 0 and cycle % args.soak_repair_every == 0
        )
        if (
            repair_due
            and restarted_this_cycle
            and args.soak_repair_restart_policy == "defer"
        ):
            repair_deferred = True
            repair_deferred_cycles.append(cycle)
            note(
                f"writable soak cycle {cycle} sync-repair deferred after "
                "scheduled restart"
            )
        elif repair_due or (repair_deferred and not restarted_this_cycle):
            reason = (
                "deferred"
                if repair_deferred and not repair_due
                else "scheduled"
            )
            note(f"writable soak cycle {cycle} sync-repair {reason} started")
            for node in nodes:
                node.sync_repair(
                    namespace,
                    control_timeout_ms=args.sync_repair_control_timeout_ms,
                )
            repair_passes += 1
            repair_deferred = False
            note(f"writable soak cycle {cycle} sync-repair {reason} completed")

        last_digest = sha256_text(
            current_value + ("present:" + marker_value if marker_present else "absent")
        )
        cycle_ms.append(int((time.monotonic() - cycle_started) * 1000))
        cycles += 1
        soak_progress.update(
            {
                "soak_cycles": cycles,
                "soak_elapsed_ms": int(
                    (time.monotonic() - soak_started) * 1000
                ),
                "soak_daemon_restarts": daemon_restarts,
                "soak_restart_targets": list(restart_targets),
                "soak_restart_settle_passes": restart_settle_passes,
                "soak_restart_settle_cycles": list(restart_settle_cycles),
                "soak_restart_skipped_final_boundary": (
                    restart_skipped_final_boundary
                ),
                "soak_restart_skipped_cycles": list(restart_skipped_cycles),
                "soak_stalled_cycle_recoveries": len(stalled_cycle_recoveries),
                "soak_stalled_cycle_recovery_events": list(
                    stalled_cycle_recoveries
                ),
                "soak_repair_passes": repair_passes,
                "soak_repair_deferrals": len(repair_deferred_cycles),
                "soak_repair_deferred_cycles": list(repair_deferred_cycles),
                "soak_repair_pending": repair_deferred,
                "soak_delete_cycles": delete_cycles,
                "soak_last_cycle_ms": cycle_ms[-1],
                "soak_final_sha256": last_digest,
            }
        )
        if log_each_cycle or cycles == 1 or cycles % 10 == 0:
            note(f"writable soak cycle {cycles} converged")
        if (
            args.soak_cycle_delay > 0.0
            and (
                time.monotonic() < deadline
                or cycles < args.soak_minimum_cycles
                or repair_deferred
            )
        ):
            time.sleep(args.soak_cycle_delay)

    soak_elapsed_ms = int((time.monotonic() - soak_started) * 1000)
    ordered = sorted(cycle_ms)
    complete = {
        "soak_campaign": True,
        "soak_completed": True,
        "soak_requested_seconds": int(args.soak_seconds),
        "soak_minimum_cycles": args.soak_minimum_cycles,
        "soak_cycle_delay_ms": int(args.soak_cycle_delay * 1000),
        "soak_restart_every": args.soak_restart_every,
        "soak_restart_phase": (
            "before-edit" if args.soak_restart_every > 0 else "none"
        ),
        "soak_restart_settle_policy": restart_settle_policy,
        "soak_final_boundary_restart_policy": (
            args.soak_final_boundary_restart_policy
        ),
        "soak_repair_every": args.soak_repair_every,
        "soak_repair_restart_policy": args.soak_repair_restart_policy,
        "sync_repair_control_timeout_ms": args.sync_repair_control_timeout_ms,
        "soak_stalled_restart_after_ms": int(
            args.soak_stalled_restart_after * 1000
        ),
        "soak_cycles": cycles,
        "soak_elapsed_ms": soak_elapsed_ms,
        "soak_daemon_restarts": daemon_restarts,
        "soak_restart_targets": restart_targets,
        "soak_restart_settle_passes": restart_settle_passes,
        "soak_restart_settle_cycles": restart_settle_cycles,
        "soak_restart_skipped_final_boundary": restart_skipped_final_boundary,
        "soak_restart_skipped_cycles": restart_skipped_cycles,
        "soak_stalled_cycle_recoveries": len(stalled_cycle_recoveries),
        "soak_stalled_cycle_recovery_events": stalled_cycle_recoveries,
        "soak_repair_passes": repair_passes,
        "soak_repair_deferrals": len(repair_deferred_cycles),
        "soak_repair_deferred_cycles": repair_deferred_cycles,
        "soak_repair_pending": repair_deferred,
        "soak_delete_cycles": delete_cycles,
        "soak_cycle_ms_min": ordered[0],
        "soak_cycle_ms_median": ordered[len(ordered) // 2],
        "soak_cycle_ms_max": ordered[-1],
        "soak_final_sha256": last_digest,
        "soak_agent_high_water_kib": [
            process_high_water_kib(node) for node in nodes
        ],
        "soak_contains_secrets": False,
    }
    soak_progress.update(complete)
    return complete


def safe_int(producer: Callable[[], int]) -> int:
    try:
        return producer()
    except (OSError, subprocess.SubprocessError, QualificationError):
        return 0


def safe_value(producer: Callable[[], object], fallback: object) -> object:
    try:
        return producer()
    except (OSError, subprocess.SubprocessError, QualificationError):
        return fallback


def write_json_atomic(path: Path, record: dict[str, object]) -> None:
    private_directory(path.parent)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.chmod(0o600)
    temporary.replace(path)


def write_rejected_evidence(
    evidence: Path,
    started: float,
    args: argparse.Namespace,
    nodes: list[Node],
    stage_events: list[dict[str, object]],
    state_preexisting: bool,
    soak_progress: dict[str, object],
    error: BaseException,
) -> None:
    failure = str(error)
    record = {
        "schema": "iotox.sync-three-writer.v1",
        "status": "rejected",
        "failure": failure[:512],
        "failure_sha256": sha256_text(failure),
        "namespace_sha256": sha256_text(args.namespace),
        "node_count": len(nodes),
        "tree_lane_cap": min(
            args.max_sync_tree_lanes, args.namespace_maximum_lanes
        ),
        "tree_lane_process_cap": args.max_sync_tree_lanes,
        "tree_lane_namespace_cap": args.namespace_maximum_lanes,
        "capacity_campaign": args.capacity_files > 0,
        "capacity_files": args.capacity_files,
        "capacity_file_bytes": args.capacity_file_bytes,
        "capacity_logical_bytes": args.capacity_files * args.capacity_file_bytes,
        "shadow_cycles": args.shadow_cycles,
        "soak_campaign": args.soak_seconds > 0.0
        or args.soak_minimum_cycles > 0,
        "soak_requested_seconds": int(args.soak_seconds),
        "soak_minimum_cycles": args.soak_minimum_cycles,
        "soak_cycle_delay_ms": int(args.soak_cycle_delay * 1000),
        "soak_restart_every": args.soak_restart_every,
        "soak_restart_phase": (
            "before-edit" if args.soak_restart_every > 0 else "none"
        ),
        "soak_final_boundary_restart_policy": (
            args.soak_final_boundary_restart_policy
        ),
        "soak_repair_every": args.soak_repair_every,
        "soak_repair_restart_policy": args.soak_repair_restart_policy,
        "sync_repair_control_timeout_ms": args.sync_repair_control_timeout_ms,
        "soak_stalled_restart_after_ms": int(
            args.soak_stalled_restart_after * 1000
        ),
        "maintenance_lifecycle_requested": bool(args.maintenance_lifecycle),
        "elapsed_ms": int((time.monotonic() - started) * 1000),
        "state_reused": state_preexisting,
        "stage_events": stage_events[-64:],
        "partial_capacity_shape_per_node": [
            safe_value(
                lambda node=node: capacity_tree_shape(node.worktree),
                {"files": 0, "bytes": 0},
            )
            for node in nodes
        ],
        "partial_tree_v2_store_shape_per_node": [
            safe_value(
                lambda node=node: tree_v2_store_shape(node, args.namespace),
                {
                    "objects": 0,
                    "object_bytes": 0,
                    "manifests": 0,
                    "manifest_bytes": 0,
                    "records": 0,
                    "record_bytes": 0,
                    "branches": 0,
                    "branch_bytes": 0,
                    "incoming_files": 0,
                    "incoming_bytes": 0,
                },
            )
            for node in nodes
        ],
        "partial_tree_v2_pull_summary_per_node": [
            partial_tree_v2_pull_summary(node, args.namespace) for node in nodes
        ],
        "partial_soak_projection_per_node": [
            safe_value(
                lambda node=node: partial_soak_projection_shape(node),
                {
                    "current_exists": False,
                    "current_bytes": 0,
                    "current_sha256": "",
                    "toggle_exists": False,
                    "toggle_bytes": 0,
                    "toggle_sha256": "",
                },
            )
            for node in nodes
        ],
        "partial_branch_count_per_node": [
            safe_int(lambda node=node: branch_count(node, args.namespace))
            for node in nodes
        ],
        "partial_conflict_alternatives_per_node": [
            safe_int(lambda node=node: len(conflict_files(node))) for node in nodes
        ],
        "partial_agent_high_water_kib": [
            safe_int(lambda node=node: process_high_water_kib(node)) for node in nodes
        ],
        "contains_secrets": False,
    }
    if soak_progress:
        record["partial_soak_evidence"] = dict(soak_progress)
        for key in (
            "soak_cycles",
            "soak_elapsed_ms",
            "soak_daemon_restarts",
            "soak_restart_targets",
            "soak_restart_phase",
            "soak_restart_settle_policy",
            "soak_restart_settle_passes",
            "soak_restart_settle_cycles",
            "soak_final_boundary_restart_policy",
            "soak_restart_skipped_final_boundary",
            "soak_restart_skipped_cycles",
            "soak_repair_restart_policy",
            "sync_repair_control_timeout_ms",
            "soak_stalled_restart_after_ms",
            "soak_stalled_cycle_recoveries",
            "soak_stalled_cycle_recovery_events",
            "soak_repair_passes",
            "soak_repair_deferrals",
            "soak_repair_deferred_cycles",
            "soak_repair_pending",
            "soak_delete_cycles",
            "soak_last_cycle_ms",
            "soak_final_sha256",
        ):
            if key in soak_progress:
                record[key] = soak_progress[key]
    write_json_atomic(evidence, record)


def token_field(text: str, name: str) -> str:
    match = re.search(
        rf"(?:^|[ \n]){re.escape(name)}=([^ \n]+)(?:[ \n]|$)", text
    )
    return match.group(1) if match else ""


def unsigned_field(text: str, name: str) -> int:
    value = token_field(text, name)
    require(value.isdigit(), f"{name} is absent or not unsigned")
    return int(value)


def checkpoint_record_present(node: Node, namespace: str) -> bool:
    records = node.policy_root / "data" / namespace / "tree-v2" / "records"
    if not records.is_dir():
        return False
    for record in records.glob("*.branch"):
        try:
            with record.open("rb") as source:
                header = source.read(9)
        except OSError:
            continue
        if len(header) == 9 and header[8] == 2:
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iotox", type=Path, required=True)
    parser.add_argument("--bootstrap", type=Path, required=True)
    parser.add_argument("--state-root", type=Path, default=DEFAULT_STATE_ROOT)
    parser.add_argument("--evidence", type=Path)
    parser.add_argument("--fresh-state", action="store_true")
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--namespace", default="field-notes")
    parser.add_argument("--shadow-cycles", type=int, default=0)
    parser.add_argument("--capacity-files", type=int, default=0)
    parser.add_argument("--capacity-file-bytes", type=int, default=0)
    parser.add_argument("--maintenance-lifecycle", action="store_true")
    parser.add_argument("--stalled-cycle-restart-after", type=float, default=0.0)
    parser.add_argument("--max-sync-tree-lanes", type=int, default=4)
    parser.add_argument("--namespace-maximum-lanes", type=int, default=4)
    parser.add_argument("--soak-seconds", type=float, default=0.0)
    parser.add_argument("--soak-minimum-cycles", type=int, default=0)
    parser.add_argument("--soak-cycle-delay", type=float, default=0.0)
    parser.add_argument("--soak-restart-every", type=int, default=0)
    parser.add_argument("--soak-repair-every", type=int, default=0)
    parser.add_argument(
        "--soak-repair-restart-policy",
        choices=("defer", "coincident"),
        default="defer",
        help=(
            "whether a periodic soak repair that lands on a scheduled restart "
            "cycle is deferred to the next non-restart cycle or run coincidently"
        ),
    )
    parser.add_argument(
        "--soak-restart-settle-policy",
        choices=("none", "repair-before-edit"),
        default="repair-before-edit",
        help=(
            "post-restart sync readiness policy before the cycle edit; "
            "repair-before-edit runs one bounded sync-repair pass across all "
            "nodes after sessions reconfirm"
        ),
    )
    parser.add_argument(
        "--soak-final-boundary-restart-policy",
        choices=("allow", "skip-if-floor-satisfied"),
        default="allow",
        help=(
            "whether a scheduled restart on the final required cycle may be "
            "skipped after the wall-clock soak floor is already satisfied"
        ),
    )
    parser.add_argument(
        "--sync-repair-control-timeout-ms",
        type=int,
        default=120000,
        help="IoTox local-control deadline for sync-repair maintenance commands",
    )
    parser.add_argument("--soak-stalled-restart-after", type=float, default=0.0)
    args = parser.parse_args()
    require(0 <= args.shadow_cycles <= 10000, "shadow cycle count is invalid")
    require(0 <= args.capacity_files <= 3500, "capacity file count is invalid")
    require(
        (args.capacity_files == 0 and args.capacity_file_bytes == 0)
        or (
            args.capacity_files > 0
            and 1 <= args.capacity_file_bytes <= 1024 * 1024
            and args.capacity_files * args.capacity_file_bytes
            <= 56 * 1024 * 1024
        ),
        "capacity population must be disabled or fit the bounded tree profile",
    )
    require(
        args.stalled_cycle_restart_after == 0.0
        or 5.0 <= args.stalled_cycle_restart_after <= args.timeout,
        "stalled-cycle restart threshold is invalid",
    )
    require(1 <= args.max_sync_tree_lanes <= 64, "tree lane cap is invalid")
    require(
        1 <= args.namespace_maximum_lanes <= 64,
        "namespace tree lane quota is invalid",
    )
    require(0.0 <= args.soak_seconds <= 7.0 * 86400.0,
            "soak duration is invalid")
    if args.soak_seconds > 0.0 and args.soak_minimum_cycles == 0:
        args.soak_minimum_cycles = 1
    require(0 <= args.soak_minimum_cycles <= 200000,
            "soak minimum cycle count is invalid")
    require(0.0 <= args.soak_cycle_delay <= 3600.0,
            "soak cycle delay is invalid")
    require(0 <= args.soak_restart_every <= 200000,
            "soak restart interval is invalid")
    require(0 <= args.soak_repair_every <= 200000,
            "soak repair interval is invalid")
    require(
        5000 <= args.sync_repair_control_timeout_ms <= 600000,
        "sync-repair control timeout is invalid",
    )
    require(
        not (
            args.soak_repair_restart_policy == "defer"
            and args.soak_restart_every == 1
            and args.soak_repair_every > 0
        ),
        "deferred repair would never run when every soak cycle restarts",
    )
    require(
        args.soak_stalled_restart_after == 0.0
        or 5.0 <= args.soak_stalled_restart_after <= args.timeout,
        "soak stalled-cycle restart threshold is invalid",
    )

    binary = args.iotox.resolve()
    bootstrap_binary = args.bootstrap.resolve()
    require(binary.is_file(), "IoTox binary is absent")
    require(bootstrap_binary.is_file(), "Tox bootstrap binary is absent")
    state_root = args.state_root.resolve()
    state_preexisting = state_root.exists() and any(state_root.iterdir())
    require(
        args.namespace_maximum_lanes == 4 or not state_preexisting,
        "namespace lane quota override requires a fresh or empty state root",
    )
    if args.fresh_state:
        require(
            not state_preexisting,
            "--fresh-state requires an absent or empty state root",
        )
    private_directory(state_root)
    state_lock = (state_root / ".qualification.lock").open("a+b")
    os.chmod(state_lock.fileno(), 0o600)
    try:
        fcntl.flock(state_lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        state_lock.close()
        print(
            f"three-writer qualification failed: state root is already in use: "
            f"{state_root}",
            file=sys.stderr,
        )
        return 1
    evidence = (
        args.evidence.resolve()
        if args.evidence is not None
        else DEFAULT_EVIDENCE_ROOT
        / f"run.{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}.json"
    )
    private_directory(evidence.parent)
    previous_sigint = signal.getsignal(signal.SIGINT)
    previous_sigterm = signal.getsignal(signal.SIGTERM)
    signal.signal(signal.SIGINT, interrupt_handler)
    signal.signal(signal.SIGTERM, interrupt_handler)

    bootstrap_process = None
    bootstrap_log = None
    nodes: list[Node] = []
    started = time.monotonic()
    stage_events: list[dict[str, object]] = []
    soak_progress: dict[str, object] = {}

    def note(message: str) -> None:
        stage_events.append(
            {
                "elapsed_ms": int((time.monotonic() - started) * 1000),
                "message": message,
            }
        )
        progress(started, message)

    try:
        bootstrap_root = state_root / "bootstrap"
        private_directory(bootstrap_root)
        bootstrap_log = (bootstrap_root / "bootstrap.log").open("ab")
        bootstrap_process = subprocess.Popen(
            [str(bootstrap_binary), "--ipv4"],
            cwd=bootstrap_root,
            stdout=bootstrap_log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        note("starting private bootstrap and three agents")
        public_id = bootstrap_root / "PUBLIC_ID.txt"
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline and not (
            public_id.is_file() and public_id.stat().st_size == 64
        ):
            require(
                bootstrap_process.poll() is None,
                "private Tox bootstrap exited during startup",
            )
            time.sleep(0.05)
        bootstrap_key = public_id.read_text(encoding="ascii").strip()
        require(bool(HEX64.fullmatch(bootstrap_key)), "bootstrap key is invalid")
        bootstrap_record = f"127.0.0.1:33445:{bootstrap_key}"

        nodes = [
            Node(chr(ord("a") + index), state_root / f"node-{index + 1}", phrase,
                 binary, bootstrap_record,
                 ["--max-sync-tree-lanes", str(args.max_sync_tree_lanes)])
            for index, phrase in enumerate(RECALL_PHRASES)
        ]
        for node in nodes:
            private_directory(node.worktree)
            baseline = node.worktree / "note.txt"
            baseline.write_text("common baseline\n", encoding="utf-8")
            baseline.chmod(0o600)
            node.start()
        wait_for(
            "all local control sockets",
            nodes,
            lambda: all(
                (node.runtime / "control.sock").is_socket()
                and node.command("status", check=False).returncode == 0
                for node in nodes
            ),
            60,
        )
        note("local control sockets ready")
        for node in nodes:
            discover_identity(node)
            initialize_authority(node)
        require(
            len({node.tox_key.lower() for node in nodes}) == 3,
            "Tox identities are not distinct",
        )
        require(
            len({node.principal.lower() for node in nodes}) == 3,
            "stable principals are not distinct",
        )
        note("distinct identities and authority ledgers ready")

        for node in nodes:
            ensure_namespace(node, args.namespace)
        if args.namespace_maximum_lanes != 4:
            for node in nodes:
                node.stop()
            for node in nodes:
                set_namespace_lane_quota(
                    node, args.namespace, args.namespace_maximum_lanes
                )
            start_nodes_after_policy_edit(nodes)
            for node in nodes:
                discover_identity(node)
            require(
                len({node.tox_key.lower() for node in nodes}) == 3,
                "Tox identities changed or are not distinct after lane override",
            )
            require(
                len({node.principal.lower() for node in nodes}) == 3,
                "stable principals changed or are not distinct after lane override",
            )
            note(
                f"namespace maximum-lanes override applied: "
                f"{args.namespace_maximum_lanes}"
            )
        for left_index, right_index in ((0, 1), (0, 2), (1, 2)):
            connect_pair(nodes[left_index], nodes[right_index], nodes)
        note("three friendship edges confirmed")
        directed_shares = 0
        for node in nodes:
            for peer in nodes:
                if peer is node:
                    continue
                share(node, peer, args.namespace, nodes)
                directed_shares += 1
                note(f"share {directed_shares}/6 {node.name}->{peer.name} committed")
        require(directed_shares == 6, "full-mesh share count is not six")

        wait_for(
            "two-peer automation on all nodes",
            nodes,
            lambda: all(automation_ready(node, args.namespace) for node in nodes),
            120,
        )
        wait_for(
            "three signed branches on all nodes",
            nodes,
            lambda: all(branch_count(node, args.namespace) == 3 for node in nodes),
            args.timeout,
        )
        note("three signed branches converged")

        capacity_evidence: dict[str, object] = {"capacity_campaign": False}
        if args.capacity_files > 0:
            disk_before = [tree_allocated_bytes(node.root) for node in nodes]
            capacity_started = time.monotonic()
            write_capacity_tree(
                nodes[0].worktree,
                args.capacity_files,
                args.capacity_file_bytes,
            )
            expected_capacity = capacity_tree_summary(nodes[0].worktree)
            require(
                expected_capacity["files"] == args.capacity_files
                and expected_capacity["bytes"]
                == args.capacity_files * args.capacity_file_bytes,
                "capacity source population is incomplete",
            )

            def capacity_converged() -> bool:
                expected_shape = {
                    "files": expected_capacity["files"],
                    "bytes": expected_capacity["bytes"],
                }
                if not all(
                    capacity_tree_shape(node.worktree) == expected_shape
                    and not conflict_files(node)
                    for node in nodes
                ):
                    return False
                return all(
                    capacity_tree_matches(node.worktree, expected_capacity)
                    for node in nodes
                )

            wait_for(
                "capacity population on all three writers",
                nodes,
                capacity_converged,
                args.timeout,
            )
            catchup_ms = int((time.monotonic() - capacity_started) * 1000)
            batch_summaries = [
                tree_file_batch_summary(node, args.namespace) for node in nodes
            ]
            repair_ms = []
            for node in nodes:
                repair_started = time.monotonic()
                node.sync_repair(
                    args.namespace,
                    control_timeout_ms=args.sync_repair_control_timeout_ms,
                )
                repair_ms.append(int((time.monotonic() - repair_started) * 1000))
            disk_after = [tree_allocated_bytes(node.root) for node in nodes]
            disk_delta = [
                after - before
                for before, after in zip(disk_before, disk_after, strict=True)
            ]
            require(
                all(value >= 0 for value in disk_delta),
                "capacity disk allocation moved backwards",
            )
            capacity_evidence = {
                "capacity_campaign": True,
                "capacity_files": args.capacity_files,
                "capacity_file_bytes": args.capacity_file_bytes,
                "capacity_logical_bytes": expected_capacity["bytes"],
                "capacity_digest": expected_capacity["digest"],
                "capacity_catchup_ms": catchup_ms,
                "capacity_repair_ms_per_node": repair_ms,
                "capacity_agent_high_water_kib": [
                    process_high_water_kib(node) for node in nodes
                ],
                "capacity_allocated_delta_bytes_per_node": disk_delta,
                "capacity_staged_file_objects_per_node": [
                    summary["staged"] for summary in batch_summaries
                ],
                "capacity_file_commit_batches_per_node": [
                    summary["batches"] for summary in batch_summaries
                ],
                "capacity_largest_file_commit_batch_per_node": [
                    summary["largest"] for summary in batch_summaries
                ],
                "capacity_cas_full_inventory_scans_per_node": [
                    summary["inventory_scans"] for summary in batch_summaries
                ],
                "capacity_cas_inventory_objects_inspected_per_node": [
                    summary["inventory_objects_inspected"]
                    for summary in batch_summaries
                ],
                "capacity_late_offers_cancelled_per_node": [
                    summary["late"] for summary in batch_summaries
                ],
                "capacity_retired_offer_ids_per_node": [
                    summary["retired"] for summary in batch_summaries
                ],
                "capacity_retired_offer_evictions_per_node": [
                    summary["evictions"] for summary in batch_summaries
                ],
                "capacity_reconcile_apply_per_node": [
                    summary["reconcile"] for summary in batch_summaries
                ],
            }
            note("capacity population converged and repaired")

        # Freeze all daemons before changing the same path.  No writer can
        # observe another edit until every branch has independently advanced.
        for node in nodes:
            node.stop()
        offline_values = {
            node.name: f"offline edit from node {node.name}\n" for node in nodes
        }
        for node in nodes:
            path = node.worktree / "note.txt"
            path.write_text(offline_values[node.name], encoding="utf-8")
            path.chmod(0o600)
            node.start()
        wait_for(
            "restarted control sockets",
            nodes,
            lambda: all(
                (node.runtime / "control.sock").is_socket()
                and node.command("status", check=False).returncode == 0
                for node in nodes
            ),
            60,
        )
        for left_index, right_index in ((0, 1), (0, 2), (1, 2)):
            for node, peer in (
                (nodes[left_index], nodes[right_index]),
                (nodes[right_index], nodes[left_index]),
            ):
                wait_for(
                    f"reconfirmed {node.name} to {peer.name} session",
                    nodes,
                    lambda node=node, peer=peer: "state=confirmed"
                    in node.command("session", peer.tox_key, check=False).stdout,
                    120,
                )

        expected_writer = min(nodes, key=lambda node: node.principal.lower())
        expected_projection = offline_values[expected_writer.name]

        def conflict_converged(node: Node) -> bool:
            note = node.worktree / "note.txt"
            return (
                note.is_file()
                and note.read_text(encoding="utf-8") == expected_projection
                and len(conflict_files(node)) == 2
                and branch_count(node, args.namespace) == 3
            )

        wait_for(
            "three-way conflict convergence",
            nodes,
            lambda: all(conflict_converged(node) for node in nodes),
            args.timeout,
        )
        conflict_counts = [len(conflict_files(node)) for node in nodes]
        note("offline three-way conflict converged")

        resolution = "resolved after observing all three branches\n"
        resolved_path = nodes[0].worktree / "note.txt"
        resolved_path.write_text(resolution, encoding="utf-8")
        resolved_path.chmod(0o600)

        def resolution_converged(node: Node) -> bool:
            note = node.worktree / "note.txt"
            return (
                note.is_file()
                and note.read_text(encoding="utf-8") == resolution
                and not conflict_files(node)
                and branch_count(node, args.namespace) == 3
            )

        wait_for(
            "explicit three-writer resolution",
            nodes,
            lambda: all(resolution_converged(node) for node in nodes),
            args.timeout,
        )
        resolved_digests = [sha256_file(node.worktree / "note.txt") for node in nodes]
        require(len(set(resolved_digests)) == 1, "resolved worktrees disagree")
        note("explicit conflict resolution converged")

        shadow_started = time.monotonic()
        stalled_cycle_restarts: list[dict[str, object]] = []
        for cycle in range(args.shadow_cycles):
            writer = nodes[cycle % len(nodes)]
            shadow_value = f"shadow cycle {cycle + 1} from node {writer.name}\n"
            shadow_path = writer.worktree / "shadow.txt"
            shadow_path.write_text(shadow_value, encoding="utf-8")
            shadow_path.chmod(0o600)
            def shadow_converged(shadow_value: str = shadow_value) -> bool:
                return all(
                    (node.worktree / "shadow.txt").is_file()
                    and (node.worktree / "shadow.txt").read_text(
                        encoding="utf-8"
                    )
                    == shadow_value
                    and not conflict_files(node)
                    for node in nodes
                )

            try:
                wait_for(
                    f"shadow cycle {cycle + 1}",
                    nodes,
                    shadow_converged,
                    args.stalled_cycle_restart_after
                    if args.stalled_cycle_restart_after > 0.0
                    else args.timeout,
                )
            except QualificationError:
                if args.stalled_cycle_restart_after == 0.0:
                    raise
                channels = process_wait_channels(writer)
                progress(
                    started,
                    f"shadow cycle {cycle + 1} stalled; restarting writer "
                    f"{writer.name} wait-channels={','.join(channels)}",
                )
                writer.stop()
                writer.start()
                wait_for(
                    f"writer {writer.name} recovery control socket",
                    nodes,
                    lambda: (writer.runtime / "control.sock").is_socket()
                    and writer.command("status", check=False).returncode == 0,
                    60,
                )
                for peer in nodes:
                    if peer is writer:
                        continue
                    wait_for(
                        f"reconfirmed {writer.name} to {peer.name} after "
                        "stalled-cycle restart",
                        nodes,
                        lambda peer=peer: "state=confirmed"
                        in writer.command(
                            "session", peer.tox_key, check=False
                        ).stdout,
                        120,
                    )
                wait_for(
                    f"shadow cycle {cycle + 1} after writer restart",
                    nodes,
                    shadow_converged,
                    args.timeout,
                )
                stalled_cycle_restarts.append(
                    {
                        "cycle": cycle + 1,
                        "writer": writer.name,
                        "wait_channels": channels,
                    }
                )
            note(f"shadow cycle {cycle + 1} converged")
        shadow_elapsed_ms = int((time.monotonic() - shadow_started) * 1000)
        soak_evidence = run_writable_soak(
            nodes, args.namespace, args, started, soak_progress, note
        )
        if soak_evidence.get("soak_campaign") is True:
            note(
                f"writable soak completed cycles={soak_evidence['soak_cycles']} "
                f"elapsed-ms={soak_evidence['soak_elapsed_ms']}"
            )

        maintenance_control_timeout_ms = args.sync_repair_control_timeout_ms
        maintenance_timeout = subprocess_timeout_for_control_timeout(
            maintenance_control_timeout_ms
        )
        maintenance_evidence: dict[str, object] = {
            "maintenance_lifecycle": False,
            "maintenance_control_timeout_ms": maintenance_control_timeout_ms,
        }
        if args.maintenance_lifecycle:
            checkpoint = nodes[0].command(
                "sync-checkpoint",
                args.namespace,
                timeout=maintenance_timeout,
                control_timeout_ms=maintenance_control_timeout_ms,
            ).stdout
            checkpoint_record = token_field(checkpoint, "record")
            require(
                bool(HEX64.fullmatch(checkpoint_record)),
                "checkpoint record identity is absent",
            )
            nodes[0].command(
                "sync-pin",
                args.namespace,
                checkpoint_record,
                timeout=maintenance_timeout,
                control_timeout_ms=maintenance_control_timeout_ms,
            )
            retention = nodes[0].command(
                "sync-retention",
                args.namespace,
                timeout=maintenance_timeout,
                control_timeout_ms=maintenance_control_timeout_ms,
            ).stdout
            require(
                unsigned_field(retention, "pins") == 1,
                "checkpoint pin did not become durable",
            )
            nodes[0].command(
                "sync-unpin",
                args.namespace,
                checkpoint_record,
                timeout=maintenance_timeout,
                control_timeout_ms=maintenance_control_timeout_ms,
            )

            dry_run = nodes[0].command(
                "sync-gc",
                args.namespace,
                "dry-run",
                timeout=maintenance_timeout,
                control_timeout_ms=maintenance_control_timeout_ms,
            ).stdout
            gc_candidates = unsigned_field(dry_run, "candidates")
            require(gc_candidates > 0, "checkpoint exposed no reclaimable history")
            quarantined = nodes[0].command(
                "sync-gc",
                args.namespace,
                "quarantine",
                timeout=maintenance_timeout,
                control_timeout_ms=maintenance_control_timeout_ms,
            ).stdout
            gc_moved = unsigned_field(quarantined, "moved")
            require(
                gc_moved == gc_candidates,
                "quarantine did not move the complete GC plan",
            )
            restored = nodes[0].command(
                "sync-restore",
                args.namespace,
                timeout=maintenance_timeout,
                control_timeout_ms=maintenance_control_timeout_ms,
            ).stdout
            gc_restored = unsigned_field(restored, "restored")
            require(gc_restored == gc_moved, "quarantine restore was incomplete")

            wait_for(
                "checkpoint record at both remote nodes",
                nodes,
                lambda: all(
                    checkpoint_record_present(node, args.namespace)
                    for node in nodes[1:]
                ),
                args.timeout,
            )

            # Writer retirement is owner-local policy.  The two surviving
            # owners each freeze the exact third branch before the retired
            # daemon is allowed to return.
            nodes[2].stop()
            cutoff_outputs = [
                node.command(
                    "sync-writer-cutoff",
                    args.namespace,
                    nodes[2].principal,
                    timeout=maintenance_timeout,
                    control_timeout_ms=maintenance_control_timeout_ms,
                ).stdout
                for node in nodes[:2]
            ]
            require(
                all("terminal=1" in output for output in cutoff_outputs),
                "one survivor did not commit the writer cutoff",
            )
            wait_for(
                "retired writer absent from both survivor frontiers",
                nodes[:2],
                lambda: all(
                    branch_count(node, args.namespace) == 2
                    for node in nodes[:2]
                ),
                args.timeout,
            )
            survivor_automations = [
                node.command(
                    "sync-automation",
                    timeout=maintenance_timeout,
                    control_timeout_ms=maintenance_control_timeout_ms,
                ).stdout
                for node in nodes[:2]
            ]
            require(
                all(
                    f"namespace={args.namespace} mode=bidirectional" in output
                    and "source-principals=1" in output
                    for output in survivor_automations
                ),
                "retired writer remains in survivor automation",
            )
            cutoff_states = [
                node.command(
                    "sync-retention",
                    args.namespace,
                    timeout=maintenance_timeout,
                    control_timeout_ms=maintenance_control_timeout_ms,
                ).stdout
                for node in nodes[:2]
            ]
            require(
                all(unsigned_field(output, "cutoffs") == 1 for output in cutoff_states),
                "terminal cutoff state is not durable on both survivors",
            )

            rogue = nodes[2].worktree / "retired-writer.txt"
            rogue.write_text("must not re-enter survivor state\n", encoding="utf-8")
            rogue.chmod(0o600)
            nodes[2].start()
            wait_for(
                "retired daemon control restart",
                nodes,
                lambda: (nodes[2].runtime / "control.sock").is_socket()
                and nodes[2].command("status", check=False).returncode == 0,
                60,
            )
            time.sleep(5)
            require(
                all(
                    branch_count(node, args.namespace) == 2
                    and not (node.worktree / "retired-writer.txt").exists()
                    for node in nodes[:2]
                ),
                "retired writer re-entered a survivor frontier",
            )
            maintenance_evidence = {
                "maintenance_lifecycle": True,
                "maintenance_control_timeout_ms": maintenance_control_timeout_ms,
                "checkpoint_peer_copies": 2,
                "checkpoint_record_sha256": sha256_text(checkpoint_record),
                "gc_candidates": gc_candidates,
                "gc_quarantined": gc_moved,
                "gc_restored": gc_restored,
                "pin_unpin_observed": True,
                "cutoff_survivors": 2,
                "post_cutoff_branch_count": [2, 2],
                "post_cutoff_source_principals": [1, 1],
                "retired_writer_reentry_refused": True,
            }
            note("maintenance lifecycle and writer cutoff converged")
        automation_records = [
            node.policy_root / "automation" / f"{args.namespace}.automation"
            for node in nodes
        ]
        require(
            all(path.stat().st_size == 4808 for path in automation_records),
            "a node did not migrate to the fixed automation-v2 record",
        )
        automation_outputs = [
            node.command(
                "sync-automation",
                timeout=maintenance_timeout,
                control_timeout_ms=maintenance_control_timeout_ms,
            ).stdout
            for node in nodes
        ]
        periodic_attempts = []
        for output in automation_outputs:
            match = re.search(r"periodic-attempts=([0-9]+)", output)
            require(match is not None, "automation attempt evidence is absent")
            periodic_attempts.append(int(match.group(1)))
        require(
            all(value >= 2 for value in periodic_attempts),
            "one node did not schedule both remote writers",
        )

        evidence_record = {
            "schema": "iotox.sync-three-writer.v1",
            "status": "passed",
            "namespace_sha256": sha256_text(args.namespace),
            "node_count": 3,
            "friendship_edge_count": 3,
            "directed_read_write_share_count": directed_shares,
            "source_principals_per_node": 2,
            "branch_count_per_node": [3, 3, 3],
            "three_way_conflict_observed": True,
            "conflict_alternatives_per_node": conflict_counts,
            "explicit_resolution_observed": True,
            "resolved_sha256": resolved_digests[0],
            "automation_record_format": 2,
            "automation_record_bytes": 4808,
            "periodic_attempts_per_node": periodic_attempts,
            "tree_lane_cap": min(
                args.max_sync_tree_lanes, args.namespace_maximum_lanes
            ),
            "tree_lane_process_cap": args.max_sync_tree_lanes,
            "tree_lane_namespace_cap": args.namespace_maximum_lanes,
            "shadow_cycles": args.shadow_cycles,
            "shadow_elapsed_ms": shadow_elapsed_ms,
            "stalled_cycle_restarts": len(stalled_cycle_restarts),
            "stalled_cycle_restart_events": stalled_cycle_restarts,
            "tox_key_sha256": [sha256_text(node.tox_key) for node in nodes],
            "principal_sha256": [sha256_text(node.principal) for node in nodes],
            "elapsed_ms": int((time.monotonic() - started) * 1000),
            "state_reused": state_preexisting,
            "contains_secrets": False,
            **capacity_evidence,
            **soak_evidence,
            **maintenance_evidence,
        }
        temporary = evidence.with_suffix(evidence.suffix + ".tmp")
        temporary.write_text(
            json.dumps(evidence_record, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary.chmod(0o600)
        temporary.replace(evidence)
        print(f"proof={evidence}")
        print(json.dumps(evidence_record, sort_keys=True))
        return 0
    except (QualificationError, OSError, subprocess.SubprocessError) as error:
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        try:
            write_rejected_evidence(
                evidence,
                started,
                args,
                nodes,
                stage_events,
                state_preexisting,
                soak_progress,
                error,
            )
            print(f"rejected-proof={evidence}")
        except (OSError, subprocess.SubprocessError, QualificationError) as write_error:
            print(
                f"three-writer rejected evidence failed: {write_error}",
                file=sys.stderr,
            )
        print(f"three-writer qualification failed: {error}", file=sys.stderr)
        return 1
    finally:
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        for node in reversed(nodes):
            try:
                node.stop()
            except (OSError, subprocess.SubprocessError, QualificationError):
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
        fcntl.flock(state_lock.fileno(), fcntl.LOCK_UN)
        state_lock.close()
        signal.signal(signal.SIGINT, previous_sigint)
        signal.signal(signal.SIGTERM, previous_sigterm)


if __name__ == "__main__":
    raise SystemExit(main())
