#!/usr/bin/env python3
"""Run one long IoTox one-writer mirror beside a Resilio read-only mirror.

All mutable state stays below ``--state-root``.  The emitted receipt contains
only counts, timings, and commitments; Resilio secrets and IoTox keys never
leave that private root.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import random
import re
import signal
import socket
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


RECALL_PHRASES = (
    "abacus abdomen abdominal abide abiding ability ablaze able",
    "abnormal abrasion abrasive abreast abridge abroad abruptly absence",
)
HEX64 = re.compile(r"^[0-9A-Fa-f]{64}$")
HEX76 = re.compile(r"^[0-9A-Fa-f]{76}$")
RESILIO_SECRET = re.compile(r"^[A-Z2-7]{33}$")
IGNORED_TOP_LEVEL = {".sync", ".SyncArchive"}
SAFE_AUTOMATION_FIELDS = {
    "enabled", "policies", "active", "namespace", "mode", "activation",
    "record-format", "generation", "interval-ms", "source-principals",
    "periodic-busy", "activation-busy", "periodic-attempts",
    "periodic-successes", "periodic-failures", "activation-attempts",
    "activation-successes", "activation-failures", "last-periodic-error",
    "last-activation-error",
}


class QualificationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise QualificationError(message)


def private_directory(path: Path) -> None:
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    path.chmod(0o700)


def field(text: str, name: str) -> str:
    prefix = f"{name}="
    for line in text.splitlines():
        if line.startswith(prefix):
            return line[len(prefix) :]
    return ""


def integer_token(text: str, name: str) -> int:
    prefix = f"{name}="
    for token in text.split():
        if token.startswith(prefix):
            value = token[len(prefix) :]
            require(value.isdecimal(), f"{name} is not an unsigned counter")
            return int(value)
    raise QualificationError(f"{name} is absent from status")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def safe_automation_status(text: str) -> str:
    lines: list[str] = []
    for line in text.splitlines():
        fields = [
            field
            for field in line.split()
            if field.partition("=")[0] in SAFE_AUTOMATION_FIELDS
        ]
        if fields:
            lines.append(" ".join(fields))
    return "\n".join(lines)


def canonical_manifest(root: Path) -> tuple[str, int, int]:
    require(root.is_dir() and not root.is_symlink(), f"manifest root is unsafe: {root}")
    rows: list[str] = []
    files = 0
    total_bytes = 0
    for path in sorted(root.rglob("*"), key=lambda value: value.relative_to(root).as_posix()):
        relative_path = path.relative_to(root)
        if relative_path.parts and relative_path.parts[0] in IGNORED_TOP_LEVEL:
            continue
        relative = relative_path.as_posix()
        require(not path.is_symlink(), f"shadow tree contains a symlink: {relative}")
        if path.is_dir():
            rows.append(f"d\t{relative}\n")
            continue
        require(path.is_file(), f"shadow tree contains a special entry: {relative}")
        size = path.stat().st_size
        rows.append(f"f\t{relative}\t{size}\t{sha256_file(path)}\n")
        files += 1
        total_bytes += size
    encoded = "".join(rows).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest(), files, total_bytes


def wait_for(
    description: str,
    processes: Callable[[], None],
    predicate: Callable[[], bool],
    timeout: float,
    diagnostics: Callable[[], str] | None = None,
) -> None:
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        processes()
        try:
            if predicate():
                return
        except (OSError, QualificationError, subprocess.SubprocessError) as error:
            last_error = error
        time.sleep(0.2)
    details: list[str] = []
    if last_error is not None:
        details.append(str(last_error))
    if diagnostics is not None:
        try:
            diagnostic_text = diagnostics().strip()
            if diagnostic_text:
                details.append(diagnostic_text)
        except (OSError, QualificationError, subprocess.SubprocessError) as error:
            details.append(f"diagnostics unavailable: {error}")
    suffix = ": " + " | ".join(details) if details else ""
    raise QualificationError(f"timeout waiting for {description}{suffix}")


@dataclass
class Node:
    name: str
    root: Path
    phrase: str
    binary: Path
    bootstrap: str
    process: subprocess.Popen[bytes] | None = None
    log_handle: object | None = None
    address: str = ""
    tox_key: str = ""
    principal: str = ""

    @property
    def runtime(self) -> Path:
        return self.root / "runtime"

    @property
    def policy_root(self) -> Path:
        return self.root / "sync-policy"

    def start(self) -> None:
        private_directory(self.root)
        private_directory(self.policy_root)
        control = self.runtime / "control.sock"
        control.unlink(missing_ok=True)
        self.log_handle = (self.root / "agent.log").open("ab")
        self.process = subprocess.Popen(
            [
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
            ],
            stdout=self.log_handle,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )

    def ensure_running(self) -> None:
        require(self.process is not None, f"{self.name} was not started")
        result = self.process.poll()
        if result is None:
            return
        tail = (self.root / "agent.log").read_text(
            encoding="utf-8", errors="replace"
        )[-4000:]
        raise QualificationError(f"{self.name} exited {result}; log tail:\n{tail}")

    def command(
        self,
        *arguments: str,
        input_text: str | None = None,
        timeout: int = 60,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        self.ensure_running()
        result = subprocess.run(
            [str(self.binary), "--runtime", str(self.runtime), *arguments],
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


def initialize_authority(node: Node) -> None:
    snapshot = node.command("authority").stdout
    initialized = field(snapshot, "initialized") == "1"
    ledger_format = field(snapshot, "ledger-format").removeprefix("v")
    if not initialized:
        node.command("authority-bootstrap-recall-stdin", input_text=node.phrase + "\n")
        ledger_format = "1"
    if ledger_format == "1":
        node.command("authority-migrate-v2-recall-stdin", input_text=node.phrase + "\n")
        ledger_format = "2"
    if ledger_format == "2":
        node.command(
            "authority-migrate-v3-recall-stdin", "all", input_text=node.phrase + "\n"
        )
        ledger_format = "3"
    require(ledger_format == "3", f"{node.name} authority is not v3")
    owner = field(
        node.command("recall-owner-public-key-stdin", input_text=node.phrase + "\n").stdout,
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


def connect_pair(left: Node, right: Node, nodes: list[Node]) -> None:
    if right.tox_key.lower() not in left.command("peers").stdout.lower():
        left.command("transport-peer-request", right.address, "IoTox shadow qualification")

    def accept_request() -> bool:
        requests = right.command("requests", check=False).stdout.lower()
        if left.tox_key.lower() not in requests:
            return False
        right.command("request-accept", left.tox_key)
        return True

    if left.tox_key.lower() not in right.command("peers").stdout.lower():
        wait_for("shadow friendship request", lambda: ensure_nodes(nodes), accept_request, 60)
    for node, peer in ((left, right), (right, left)):
        wait_for(
            f"confirmed {node.name} session",
            lambda: ensure_nodes(nodes),
            lambda node=node, peer=peer: "state=confirmed"
            in node.command("session", peer.tox_key, check=False).stdout,
            120,
        )


def ensure_nodes(nodes: list[Node]) -> None:
    for node in nodes:
        node.ensure_running()


def wait_authorized(node: Node, peer: Node, nodes: list[Node]) -> None:
    wait_for(
        f"authorized {node.name} session",
        lambda: ensure_nodes(nodes),
        lambda: "remote-authorized=1"
        in node.command("authority-session", peer.tox_key, check=False).stdout,
        120,
    )


def free_loopback_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


@dataclass
class ResilioPair:
    binary: Path
    root: Path
    source: Path
    replica: Path
    processes: list[subprocess.Popen[bytes]]
    logs: list[object]
    version_sha256: str

    @classmethod
    def start(cls, binary: Path, root: Path, source: Path, replica: Path) -> "ResilioPair":
        private_directory(root)
        private_directory(source)
        private_directory(replica)
        admin = root / "admin"
        private_directory(admin)
        generated = subprocess.run(
            [str(binary), "--generate-secret", "2"],
            cwd=admin,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=30,
            check=False,
        )
        read_write = next(
            (line.strip() for line in generated.stdout.splitlines()
             if RESILIO_SECRET.fullmatch(line.strip())),
            "",
        )
        require(generated.returncode == 0 and bool(read_write),
                "Resilio did not generate one v2 read-write secret")
        read_only_result = subprocess.run(
            [str(binary), "--get-ro-secret", read_write],
            cwd=admin,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=30,
            check=False,
        )
        read_only = next(
            (line.strip() for line in read_only_result.stdout.splitlines()
             if RESILIO_SECRET.fullmatch(line.strip())),
            "",
        )
        require(read_only_result.returncode == 0 and bool(read_only),
                "Resilio did not derive one read-only secret")
        ports = (free_loopback_port(), free_loopback_port())
        require(ports[0] != ports[1], "Resilio loopback ports collided")
        processes: list[subprocess.Popen[bytes]] = []
        logs: list[object] = []
        for index, (directory, secret) in enumerate(
            ((source, read_write), (replica, read_only))
        ):
            instance = root / f"node-{index + 1}"
            storage = instance / "storage"
            private_directory(storage)
            config = {
                "device_name": f"iotox-shadow-{index + 1}",
                "listening_port": ports[index],
                "storage_path": str(storage),
                "pid_file": str(instance / "rslsync.pid"),
                "use_upnp": False,
                "send_statistics": False,
                "download_limit": 0,
                "upload_limit": 0,
                "shared_folders": [
                    {
                        "secret": secret,
                        "dir": str(directory),
                        "use_relay_server": False,
                        "use_tracker": False,
                        "search_lan": False,
                        "use_sync_trash": True,
                        "overwrite_changes": index == 1,
                        "selective_sync": False,
                        "known_hosts": [f"127.0.0.1:{ports[1 - index]}"],
                    }
                ],
            }
            config_path = instance / "config.json"
            config_path.write_text(json.dumps(config, sort_keys=True) + "\n", encoding="utf-8")
            config_path.chmod(0o600)
            log_handle = (instance / "process.log").open("ab")
            process = subprocess.Popen(
                [str(binary), "--nodaemon", "--config", str(config_path)],
                cwd=instance,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
            processes.append(process)
            logs.append(log_handle)
        version = subprocess.run(
            [str(binary), "--help"],
            cwd=admin,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=30,
            check=False,
        ).stdout
        return cls(
            binary,
            root,
            source,
            replica,
            processes,
            logs,
            hashlib.sha256(version).hexdigest(),
        )

    def ensure_running(self) -> None:
        for index, process in enumerate(self.processes):
            if process.poll() is not None:
                raise QualificationError(
                    f"Resilio shadow node {index + 1} exited {process.returncode}"
                )

    def stop(self) -> None:
        for process in self.processes:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
        for process in self.processes:
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=5)
        for handle in self.logs:
            handle.close()
        self.processes.clear()
        self.logs.clear()


def write_private(path: Path, content: bytes) -> None:
    private_directory(path.parent)
    path.write_bytes(content)
    path.chmod(0o600)


def apply_mutation(root: Path, cycle: int, payload: bytes) -> None:
    slot = cycle % 16
    action = cycle % 6
    if action == 0:
        write_private(root / "notes" / "state.txt", payload.hex().encode("ascii") + b"\n")
    elif action == 1:
        write_private(root / "sets" / f"slot-{slot:02d}.bin", payload)
    elif action == 2:
        write_private(root / "empty" / f"slot-{slot:02d}", b"")
    elif action == 3:
        target = root / "sets" / f"slot-{(slot + 7) % 16:02d}.bin"
        target.unlink(missing_ok=True)
    elif action == 4:
        write_private(root / "reports" / "space name.txt", payload[:257] + b"\n")
    else:
        write_private(root / "rotating" / f"value-{slot:02d}.txt", payload[:1024])


def self_test() -> None:
    import tempfile

    with tempfile.TemporaryDirectory(prefix="iotox-shadow-self-test-") as temporary:
        left = Path(temporary) / "left"
        right = Path(temporary) / "right"
        private_directory(left)
        private_directory(right)
        rng = random.Random(20260901)
        for cycle in range(24):
            payload = rng.randbytes(4096 + cycle)
            apply_mutation(left, cycle, payload)
            apply_mutation(right, cycle, payload)
        require(canonical_manifest(left) == canonical_manifest(right),
                "canonical shadow self-test diverged")
        private_directory(right / ".sync")
        write_private(right / ".sync" / "ignored", b"provider state")
        require(canonical_manifest(left) == canonical_manifest(right),
                "provider-state exclusion is not canonical")
        redacted = safe_automation_status(
            "namespace=notes mode=publish source-path-hex=2f736563726574 "
            "source-principal=" + "ab" * 32 + " periodic-attempts=9\n"
        )
        require("source-path" not in redacted and "source-principal" not in redacted,
                "automation diagnostics retained owner-private identity")
        require("periodic-attempts=9" in redacted,
                "automation diagnostics dropped the useful counter")
    print("sync-shadow self-test: PASS")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iotox", type=Path)
    parser.add_argument("--bootstrap", type=Path)
    parser.add_argument("--rslsync", type=Path)
    parser.add_argument("--state-root", type=Path)
    parser.add_argument("--evidence", type=Path)
    parser.add_argument("--duration-seconds", type=int, default=7200)
    parser.add_argument("--interval-seconds", type=int, default=30)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--seed", type=int, default=20260901)
    parser.add_argument("--restart-every-cycles", type=int, default=20)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()
    if args.self_test:
        self_test()
        return 0
    for value, label in (
        (args.iotox, "--iotox"),
        (args.bootstrap, "--bootstrap"),
        (args.rslsync, "--rslsync"),
        (args.state_root, "--state-root"),
        (args.evidence, "--evidence"),
    ):
        require(value is not None, f"{label} is required")
    require(60 <= args.duration_seconds <= 86400, "shadow duration is outside 60..86400")
    require(5 <= args.interval_seconds <= 3600, "shadow interval is outside 5..3600")
    require(30 <= args.timeout <= 1800, "shadow timeout is outside 30..1800")
    require(0 <= args.restart_every_cycles <= 10000, "restart cadence is invalid")
    iotox = args.iotox.resolve()
    bootstrap_binary = args.bootstrap.resolve()
    rslsync = args.rslsync.resolve()
    state_root = args.state_root.resolve()
    evidence = args.evidence.resolve()
    require(iotox.is_file() and bootstrap_binary.is_file() and rslsync.is_file(),
            "one or more qualification binaries are absent")
    private_directory(state_root)
    private_directory(evidence.parent)
    lock = (state_root / ".qualification.lock").open("a+b")
    os.chmod(lock.fileno(), 0o600)
    try:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as error:
        raise QualificationError("sync shadow state is already active") from error

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
    nodes: list[Node] = []
    resilio: ResilioPair | None = None
    started = time.monotonic()
    try:
        public_id = bootstrap_root / "PUBLIC_ID.txt"
        wait_for(
            "private bootstrap",
            lambda: require(bootstrap_process.poll() is None, "bootstrap exited"),
            lambda: public_id.is_file() and public_id.stat().st_size == 64,
            20,
        )
        bootstrap_key = public_id.read_text(encoding="ascii").strip()
        require(bool(HEX64.fullmatch(bootstrap_key)), "bootstrap key is invalid")
        bootstrap_record = f"127.0.0.1:33445:{bootstrap_key}"
        nodes = [
            Node("publisher", state_root / "publisher", RECALL_PHRASES[0],
                 iotox, bootstrap_record),
            Node("replica", state_root / "replica", RECALL_PHRASES[1],
                 iotox, bootstrap_record),
        ]
        source = state_root / "iotox-source"
        replica = state_root / "iotox-replica"
        resilio_source = state_root / "resilio-source"
        resilio_replica = state_root / "resilio-replica"
        for path in (source, replica, resilio_source, resilio_replica):
            private_directory(path)
        baseline = b"IoTox/Resilio shadow baseline\n"
        write_private(source / "notes" / "state.txt", baseline)
        write_private(resilio_source / "notes" / "state.txt", baseline)
        for node in nodes:
            node.start()
        wait_for(
            "IoTox local controls",
            lambda: ensure_nodes(nodes),
            lambda: all(
                (node.runtime / "control.sock").is_socket()
                and node.command("status", check=False).returncode == 0
                for node in nodes
            ),
            60,
        )
        for node in nodes:
            initialize_authority(node)
            discover_identity(node)
        connect_pair(nodes[0], nodes[1], nodes)
        namespace = "resilio-shadow"
        created = nodes[0].command(
            "sync-create", namespace, str(source), "1"
        ).stdout
        require("engine=treepack-v1" in created, "publisher namespace was not treepack-v1")
        shared = nodes[0].command(
            "sync-share", namespace, nodes[1].tox_key, "read-only",
            input_text=nodes[0].phrase + "\n",
        ).stdout
        require("access=read-only" in shared and "membership=added" in shared,
                "publisher read-only share did not commit")

        template = subprocess.run(
            [str(iotox), "sync-namespace-template-tree", namespace,
             str(replica), nodes[0].principal, nodes[1].principal],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
            check=False,
        )
        require(template.returncode == 0, f"replica policy template failed: {template.stderr}")
        policy_path = nodes[1].root / f"{namespace}.namespace"
        policy_path.write_text(template.stdout, encoding="ascii")
        policy_path.chmod(0o600)
        installed = nodes[1].command("sync-namespace-install", str(policy_path)).stdout
        require("decision=installed" in installed, "replica namespace installation failed")
        nodes[1].command(
            "authority-grant-recall-stdin", nodes[0].principal, "service",
            "sync.publish", input_text=nodes[1].phrase + "\n",
        )
        wait_authorized(nodes[0], nodes[1], nodes)
        wait_authorized(nodes[1], nodes[0], nodes)
        followed = nodes[1].command(
            "sync-follow", nodes[0].tox_key, namespace, "verified", "1"
        ).stdout
        require("mode=follow" in followed and "activation=verified" in followed,
                "replica follow policy did not commit")

        resilio = ResilioPair.start(
            rslsync, state_root / "resilio-state", resilio_source, resilio_replica
        )
        current = replica / "materialized-trees" / "current"

        def iotox_projection_manifest() -> tuple[str, int, int]:
            if not current.is_symlink():
                raise QualificationError("IoTox activation pointer is absent")
            resolved = current.resolve(strict=True)
            revisions = (replica / "materialized-trees" / "revisions").resolve()
            require(resolved.parent == revisions and resolved.is_dir(),
                    "IoTox activation pointer escaped its revision root")
            return canonical_manifest(resolved)

        def ensure_all() -> None:
            ensure_nodes(nodes)
            require(bootstrap_process.poll() is None, "bootstrap exited")
            require(resilio is not None, "Resilio pair is absent")
            resilio.ensure_running()

        def mirrors_equal() -> bool:
            source_manifest = canonical_manifest(source)
            return (
                canonical_manifest(resilio_source) == source_manifest
                and iotox_projection_manifest() == source_manifest
                and canonical_manifest(resilio_replica) == source_manifest
            )

        def convergence_diagnostics() -> str:
            views: dict[str, object] = {}
            for name, root in (
                ("iotox-source", source),
                ("resilio-source", resilio_source),
                ("resilio-replica", resilio_replica),
            ):
                try:
                    digest, files, content_bytes = canonical_manifest(root)
                    views[name] = {
                        "sha256": digest,
                        "files": files,
                        "bytes": content_bytes,
                    }
                except (OSError, QualificationError) as error:
                    views[name] = {"error": str(error)}
            try:
                digest, files, content_bytes = iotox_projection_manifest()
                views["iotox-replica"] = {
                    "sha256": digest,
                    "files": files,
                    "bytes": content_bytes,
                }
            except (OSError, QualificationError) as error:
                views["iotox-replica"] = {"error": str(error)}
            automation: dict[str, object] = {}
            for node in nodes:
                result = node.command("sync-automation", check=False)
                automation[node.name] = {
                    "returncode": result.returncode,
                    "status": safe_automation_status(result.stdout),
                }
            return "shadow-state=" + json.dumps(
                {"views": views, "automation": automation}, sort_keys=True
            )

        wait_for(
            "initial dual-mirror convergence", ensure_all, mirrors_equal,
            args.timeout, convergence_diagnostics,
        )
        rng = random.Random(args.seed)
        shadow_started = time.monotonic()
        cycles = 0
        publisher_restarts = 0
        replica_restarts = 0
        while time.monotonic() - shadow_started < args.duration_seconds:
            cycle_started = time.monotonic()
            payload = rng.randbytes(4096 + rng.randrange(0, 12 * 1024))
            apply_mutation(source, cycles, payload)
            apply_mutation(resilio_source, cycles, payload)
            wait_for(
                f"shadow cycle {cycles + 1}", ensure_all, mirrors_equal,
                args.timeout, convergence_diagnostics,
            )
            cycles += 1
            if args.restart_every_cycles > 0 and cycles % args.restart_every_cycles == 0:
                target = nodes[(cycles // args.restart_every_cycles + 1) % 2]
                target.stop()
                target.start()
                if target is nodes[0]:
                    publisher_restarts += 1
                else:
                    replica_restarts += 1
                wait_for(
                    f"{target.name} restart control",
                    ensure_all,
                    lambda: (target.runtime / "control.sock").is_socket()
                    and target.command("status", check=False).returncode == 0,
                    60,
                )
                wait_for(
                    f"{target.name} restart convergence", ensure_all, mirrors_equal,
                    args.timeout, convergence_diagnostics,
                )
            remaining = args.interval_seconds - (time.monotonic() - cycle_started)
            duration_remaining = args.duration_seconds - (
                time.monotonic() - shadow_started
            )
            if remaining > 0 and duration_remaining > 0:
                time.sleep(min(remaining, duration_remaining, 60.0))
            print(
                f"shadow-cycle={cycles} elapsed-seconds="
                f"{time.monotonic() - shadow_started:.1f}",
                flush=True,
            )

        wait_for(
            "final dual-mirror convergence", ensure_all, mirrors_equal,
            args.timeout, convergence_diagnostics,
        )
        nodes[1].command("sync-repair", namespace, timeout=120)
        publisher_replay_evictions = 0

        def observed_replay_eviction() -> bool:
            nonlocal publisher_replay_evictions
            publisher_replay_evictions = integer_token(
                nodes[0].command("sync-status").stdout, "replay-evictions"
            )
            return publisher_replay_evictions > 0

        wait_for(
            "publisher exact-replay window turnover",
            ensure_all,
            observed_replay_eviction,
            30,
        )
        final_digest, final_files, final_bytes = canonical_manifest(source)
        elapsed_ms = int((time.monotonic() - shadow_started) * 1000)
        require(elapsed_ms >= args.duration_seconds * 1000,
                "shadow campaign ended before its wall-clock floor")
        receipt = {
            "schema": "iotox.sync-shadow.v1",
            "status": "passed",
            "incumbent": "resilio-sync",
            "duration_floor_seconds": args.duration_seconds,
            "elapsed_ms": elapsed_ms,
            "cycles": cycles,
            "interval_seconds": args.interval_seconds,
            "seed": args.seed,
            "publisher_restarts": publisher_restarts,
            "replica_restarts": replica_restarts,
            "publisher_replay_evictions": publisher_replay_evictions,
            "canonical_manifest_sha256": final_digest,
            "canonical_files": final_files,
            "canonical_bytes": final_bytes,
            "resilio_binary_sha256": sha256_file(rslsync),
            "resilio_version_output_sha256": resilio.version_sha256,
            "iotox_binary_sha256": sha256_file(iotox),
            "node_count": 2,
            "manual_publish_pull_activate_commands": 0,
            "contains_secrets": False,
        }
        temporary = evidence.with_suffix(evidence.suffix + ".tmp")
        temporary.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n",
                             encoding="utf-8")
        temporary.chmod(0o600)
        temporary.replace(evidence)
        print(f"proof={evidence}")
        print(json.dumps(receipt, sort_keys=True))
        return 0
    except (QualificationError, OSError, subprocess.SubprocessError) as error:
        print(f"sync shadow qualification failed: {error}", file=sys.stderr)
        return 1
    finally:
        if resilio is not None:
            try:
                resilio.stop()
            except (OSError, subprocess.SubprocessError):
                pass
        for node in reversed(nodes):
            try:
                node.stop()
            except (OSError, subprocess.SubprocessError, QualificationError):
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
    except QualificationError as error:
        print(f"sync shadow qualification failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
