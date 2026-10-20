#!/usr/bin/env python3
"""Exercise bounded one-node and all-live-node tree-v2 recovery.

This is a same-VM ceremony gate.  The backup and restored views are deliberately
outside every node root, but their administrative/storage independence is not
and cannot be inferred here.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import importlib.util
import json
import os
import shutil
import signal
import stat
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
THREE_WRITER = ROOT / "tools" / "run-sync-three-writer.py"
tw = None


def load_three_writer(path: Path) -> object:
    spec = importlib.util.spec_from_file_location("iotox_three_writer", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load the three-writer qualification helpers")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def copy_operator_tree(source: Path, destination: Path) -> None:
    tw.require(source.is_dir() and not source.is_symlink(), "source tree is unsafe")
    if destination.exists():
        tw.require(
            destination.is_dir() and not destination.is_symlink(),
            "operator-tree destination is unsafe",
        )
        tw.require(
            not any(
                child.name != ".iotox-conflicts"
                for child in destination.iterdir()
            )
            and not any(
                candidate.is_file()
                for candidate in (
                    destination / ".iotox-conflicts" / "by-origin"
                ).rglob("*")
            ),
            "operator-tree destination is not empty",
        )
    else:
        tw.private_directory(destination)
    for candidate in sorted(source.rglob("*")):
        relative = candidate.relative_to(source)
        if relative.parts and relative.parts[0] == ".iotox-conflicts":
            continue
        metadata = candidate.lstat()
        target = destination / relative
        tw.require(not stat.S_ISLNK(metadata.st_mode), "operator tree contains a link")
        if stat.S_ISDIR(metadata.st_mode):
            tw.private_directory(target)
            os.chmod(target, stat.S_IMODE(metadata.st_mode) & 0o700)
        elif stat.S_ISREG(metadata.st_mode):
            tw.private_directory(target.parent)
            shutil.copyfile(candidate, target, follow_symlinks=False)
            os.chmod(target, stat.S_IMODE(metadata.st_mode) & 0o700)
        else:
            raise tw.QualificationError("operator tree contains a special file")


def operator_tree_summary(root: Path) -> dict[str, object]:
    digest = hashlib.sha256()
    files = 0
    directories = 0
    total_bytes = 0
    for candidate in sorted(root.rglob("*")):
        relative = candidate.relative_to(root)
        if relative.parts and relative.parts[0] == ".iotox-conflicts":
            continue
        metadata = candidate.lstat()
        tw.require(not stat.S_ISLNK(metadata.st_mode), "operator tree contains a link")
        encoded = relative.as_posix().encode("utf-8")
        digest.update(len(encoded).to_bytes(4, "big"))
        digest.update(encoded)
        digest.update((stat.S_IMODE(metadata.st_mode) & 0o700).to_bytes(2, "big"))
        if stat.S_ISDIR(metadata.st_mode):
            digest.update(b"d")
            directories += 1
        elif stat.S_ISREG(metadata.st_mode):
            content = candidate.read_bytes()
            digest.update(b"f")
            digest.update(len(content).to_bytes(8, "big"))
            digest.update(content)
            files += 1
            total_bytes += len(content)
        else:
            raise tw.QualificationError("operator tree contains a special file")
    return {
        "digest": digest.hexdigest(),
        "files": files,
        "directories": directories,
        "bytes": total_bytes,
    }


def report_field(text: str, name: str) -> str:
    prefix = f"{name}="
    for line in text.splitlines():
        if line.startswith(prefix):
            return line[len(prefix) :]
    return ""


def hex_text(text: str) -> str:
    return text.encode("utf-8").hex().upper()


def provenance_tokens(args: argparse.Namespace) -> list[str]:
    labels = (
        args.backup_system,
        args.backup_generation,
        args.backup_failure_domain,
        args.restore_provenance,
    )
    present = [label is not None for label in labels]
    tw.require(
        not any(present) or all(present),
        "backup provenance labels must be supplied all-or-none",
    )
    if not all(present):
        return []
    return [
        f"backup-system={args.backup_system}",
        f"backup-generation={args.backup_generation}",
        f"backup-failure-domain={args.backup_failure_domain}",
        f"restore-provenance={args.restore_provenance}",
    ]


def verify_restore(
    binary: Path,
    backup: Path,
    restored: Path,
    operator_provenance: list[str],
) -> dict[str, object]:
    command = [
        str(binary),
        "sync-recovery-verify",
        str(backup),
        str(restored),
        str(64 * 1024 * 1024),
        "4096",
        *operator_provenance,
    ]
    result = subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=120,
    )
    detail = result.stderr or result.stdout
    tw.require(result.returncode == 0, f"restore verifier refused: {detail.strip()}")
    tw.require(
        result.stdout.startswith("iotox-sync-recovery-verify-v1\ndecision=match\n")
        and "iotox-live-state-read=0\n" in result.stdout
        and "backup-independence=not-assessed\n" in result.stdout
        and "restore-provenance=not-assessed\n" in result.stdout,
        "restore verifier did not emit its strict match/nonclaim contract",
    )
    if operator_provenance:
        for token in operator_provenance:
            key, value = token.split("=", 1)
            tw.require(
                f"{key}-hex={hex_text(value)}\n" in result.stdout,
                "restore verifier did not bind one provenance label",
            )
        tw.require(
            "operator-provenance=present\n" in result.stdout,
            "restore verifier did not record present provenance",
        )
    else:
        tw.require(
            "operator-provenance=absent\n" in result.stdout,
            "restore verifier did not record absent provenance",
        )
    root_devices_differ = report_field(result.stdout, "root-devices-differ")
    tw.require(
        root_devices_differ in ("0", "1"),
        "restore verifier did not emit root-device evidence",
    )
    return {
        "sha256": hashlib.sha256(result.stdout.encode("utf-8")).hexdigest(),
        "root_devices_differ": int(root_devices_differ),
        "operator_provenance": "present" if operator_provenance else "absent",
    }


def branch_principals(node: object, namespace: str) -> set[str]:
    root = node.policy_root / "data" / namespace / "tree-v2" / "branches"
    try:
        return {
            path.stem.lower()
            for path in root.iterdir()
            if path.is_file()
            and not path.is_symlink()
            and path.suffix == ".branch"
            and tw.HEX64.fullmatch(path.stem)
        }
    except FileNotFoundError:
        return set()


def current_checkpoint_count(
    node: object, namespace: str, minimum_generation: int = 0
) -> int:
    # This is only a low-impact liveness observation. Calling authenticated
    # sync-history at 10 Hz can monopolize the local control loop and prevent
    # the very Tox exchange being observed. Final sync-repair remains the
    # integrity gate after convergence.
    root = node.policy_root / "data" / namespace / "tree-v2" / "branches"
    try:
        count = 0
        for path in root.iterdir():
            if (
                not path.is_file()
                or path.is_symlink()
                or path.suffix != ".branch"
                or not tw.HEX64.fullmatch(path.stem)
            ):
                continue
            with path.open("rb") as handle:
                header = handle.read(24)
            if (
                header[:8] == b"IOTXTVB1"
                and header[8:9] == b"\x02"
                and int.from_bytes(header[16:24], "big") >= minimum_generation
            ):
                count += 1
        return count
    except FileNotFoundError:
        return 0


def start_nodes(nodes: list[object]) -> None:
    for node in nodes:
        node.start()
    tw.wait_for(
        "recovery-node control sockets",
        nodes,
        lambda: all(
            (node.runtime / "control.sock").is_socket()
            and node.command("status", check=False).returncode == 0
            for node in nodes
        ),
        60,
    )
    for node in nodes:
        tw.discover_identity(node)
        tw.initialize_authority(node)


def connect_full_mesh(nodes: list[object], namespace: str) -> int:
    for left, right in ((0, 1), (0, 2), (1, 2)):
        tw.connect_pair(nodes[left], nodes[right], nodes)
    for node in nodes:
        tw.ensure_namespace(node, namespace)
    shares = 0
    for node in nodes:
        for peer in nodes:
            if node is peer:
                continue
            tw.share(node, peer, namespace, nodes)
            shares += 1
    tw.wait_for(
        "recovery full-mesh automation",
        nodes,
        lambda: all(tw.automation_ready(node, namespace) for node in nodes),
        180,
    )
    tw.wait_for(
        "recovery full-mesh branches",
        nodes,
        lambda: all(tw.branch_count(node, namespace) == 3 for node in nodes),
        180,
    )
    return shares


def destroy_node(node: object, state_root: Path) -> None:
    node.stop()
    root = node.root.resolve()
    tw.require(root.parent == state_root, "refusing to remove a non-child node root")
    tw.require(
        root.name.startswith(("node-", "replacement-")),
        "refusing to remove an unrecognized node root",
    )
    shutil.rmtree(root)
    tw.require(not root.exists(), "synthetic node root survived removal")


def seed_initial_tree(node: object, files: int, file_bytes: int) -> None:
    tw.private_directory(node.worktree)
    note = node.worktree / "note.txt"
    note.write_text("selected backup generation\n", encoding="utf-8")
    note.chmod(0o600)
    payload_root = node.worktree / "payload"
    tw.private_directory(payload_root)
    for index in range(files):
        seed = hashlib.sha256(f"iotox-recovery-v1:{index}".encode("ascii")).digest()
        content = (seed * ((file_bytes + 31) // 32))[:file_bytes]
        path = payload_root / f"file-{index:04d}.bin"
        path.write_bytes(content)
        path.chmod(0o600 if index % 2 == 0 else 0o700)


def repair_all(nodes: list[object], namespace: str) -> None:
    for node in nodes:
        output = node.command("sync-repair", namespace, timeout=120).stdout
        tw.require(" verified=1" in f" {output}", "one replacement failed repair")


def main() -> int:
    global tw
    parser = argparse.ArgumentParser()
    parser.add_argument("--iotox", type=Path, required=True)
    parser.add_argument("--bootstrap", type=Path, required=True)
    parser.add_argument("--three-writer-helper", type=Path, default=THREE_WRITER)
    parser.add_argument("--state-root", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--namespace", default="recovered-notes")
    parser.add_argument("--files", type=int, default=32)
    parser.add_argument("--file-bytes", type=int, default=4096)
    parser.add_argument("--backup-system")
    parser.add_argument("--backup-generation")
    parser.add_argument("--backup-failure-domain")
    parser.add_argument("--restore-provenance")
    args = parser.parse_args()
    helper = args.three_writer_helper.resolve()
    if not helper.is_file():
        raise RuntimeError("three-writer qualification helper is absent")
    tw = load_three_writer(helper)
    tw.require(1 <= args.files <= 512, "recovery file count is invalid")
    tw.require(1 <= args.file_bytes <= 65536, "recovery file size is invalid")
    recovery_provenance = provenance_tokens(args)

    binary = args.iotox.resolve()
    bootstrap_binary = args.bootstrap.resolve()
    state_root = args.state_root.resolve()
    evidence = args.evidence.resolve()
    tw.require(binary.is_file(), "IoTox binary is absent")
    tw.require(bootstrap_binary.is_file(), "bootstrap binary is absent")
    tw.require(not state_root.exists(), "recovery state root must start absent")
    tw.private_directory(state_root)
    tw.private_directory(evidence.parent)
    lock = (state_root / ".qualification.lock").open("a+b")
    os.chmod(lock.fileno(), 0o600)
    fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

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

    def stage(message: str) -> None:
        elapsed = time.monotonic() - started
        print(f"sync-recovery stage elapsed={elapsed:.1f}s {message}", flush=True)

    try:
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
            tw.Node(chr(97 + index), state_root / f"node-{index + 1}", phrase,
                    binary, bootstrap)
            for index, phrase in enumerate(tw.RECALL_PHRASES)
        ]
        for node in nodes:
            tw.private_directory(node.worktree)
        start_nodes(nodes)
        tw.require(connect_full_mesh(nodes, args.namespace) == 6, "bad share count")
        # Establish all six policy edges while the namespace is empty.  If the
        # seed is present first, the earliest edge can start a pull and the
        # Agent correctly fences the next membership mutation until it drains.
        seed_initial_tree(nodes[0], args.files, args.file_bytes)
        stage("initial full mesh established and recovery dataset seeded")
        expected = operator_tree_summary(nodes[0].worktree)
        tw.wait_for(
            "initial recovery dataset convergence",
            nodes,
            lambda: all(
                not tw.conflict_files(node)
                and operator_tree_summary(node.worktree) == expected
                for node in nodes
            ),
            180,
        )
        repair_all(nodes, args.namespace)
        stage("initial recovery dataset converged and verified")

        recovery_root = state_root / "operator-recovery"
        tw.private_directory(recovery_root)
        backup = recovery_root / "selected-backup-generation"
        restored = recovery_root / "external-restore"
        copy_operator_tree(nodes[0].worktree, backup)
        copy_operator_tree(backup, restored)
        verifier_reports = [
            verify_restore(binary, backup, restored, recovery_provenance)
        ]
        stage("ordinary backup and strict restore view verified")

        old_principals = {node.principal.lower() for node in nodes}
        old_c = nodes[2]
        # Retire the old relationship while it is still online and quiescent.
        # Once an unretired writer is offline, exact publisher replay state can
        # correctly fence membership mutation because it cannot prove drain.
        for survivor in nodes[:2]:
            survivor.command(
                "sync-writer-cutoff", args.namespace, old_c.principal,
                timeout=120,
            )
            survivor.command(
                "authority-revoke-recall-stdin", old_c.principal,
                input_text=survivor.phrase + "\n",
            )
            survivor.command("transport-peer-remove", old_c.tox_key)
        tw.wait_for(
            "old writer retirement on both survivors",
            nodes,
            lambda: all(
                tw.branch_count(node, args.namespace) == 2
                and "source-principals=1" in node.command(
                    "sync-automation", check=False
                ).stdout
                for node in nodes[:2]
            ),
            180,
        )
        destroy_node(old_c, state_root)
        # Exercise persistence and the real authority-session recovery path at
        # the quiescent retirement boundary. This restart is not a replay-cache
        # shortcut: additive sharing now retires only its namespace's cached
        # replies while holding the Agent authority/effect fence.
        for survivor in nodes[:2]:
            survivor.stop()
        for survivor in nodes[:2]:
            survivor.start()
        tw.wait_for(
            "survivor quiescence restart",
            nodes[:2],
            lambda: all(
                (node.runtime / "control.sock").is_socket()
                and node.command("status", check=False).returncode == 0
                for node in nodes[:2]
            ),
            60,
        )
        for survivor, peer in ((nodes[0], nodes[1]), (nodes[1], nodes[0])):
            tw.wait_for(
                "survivor session after quiescence restart",
                nodes[:2],
                lambda survivor=survivor, peer=peer: "state=confirmed"
                in survivor.command("session", peer.tox_key, check=False).stdout,
                120,
            )
        # The cutoff operation creates one checkpoint on each survivor. First
        # exchange those exact successors: accepting a later graph floor may
        # never skip the other writer's intervening generation.
        tw.wait_for(
            "cutoff checkpoint exchange",
            nodes[:2],
            lambda: all(
                current_checkpoint_count(node, args.namespace, 2) == 2
                for node in nodes[:2]
            ),
            180,
        )
        # A cutoff prevents the obsolete writer from advancing, but its
        # checkpoint still cites the terminal history. Fresh replacements do
        # not inherit that obsolete principal roster. Create and exchange a
        # second graph floor whose observations contain only the survivors.
        for survivor in nodes[:2]:
            checkpoint = survivor.command(
                "sync-checkpoint", args.namespace, timeout=120
            ).stdout
            tw.require(
                "checkpoint=1" in checkpoint and "graph-floor=1" in checkpoint,
                "survivor did not create a post-cutoff graph floor",
            )
        tw.wait_for(
            "post-cutoff graph-floor exchange",
            nodes[:2],
            lambda: all(
                current_checkpoint_count(node, args.namespace, 3) == 2
                for node in nodes[:2]
            ),
            180,
        )
        replacement = tw.Node(
            "c", state_root / "replacement-one-node", old_c.phrase,
            binary, bootstrap,
        )
        tw.private_directory(replacement.worktree)
        replacement.start()
        active = [nodes[0], nodes[1], replacement]
        # Publish the live cleanup set before any fallible admission step.
        # Otherwise a refused share can leave the newly started replacement
        # outside the finally block's process inventory.
        nodes = active
        tw.wait_for(
            "single replacement control socket",
            active,
            lambda: (replacement.runtime / "control.sock").is_socket()
            and replacement.command("status", check=False).returncode == 0,
            60,
        )
        tw.discover_identity(replacement)
        tw.initialize_authority(replacement)
        tw.require(
            replacement.principal.lower() not in old_principals
            and replacement.tox_key.lower() != old_c.tox_key.lower(),
            "one-node replacement reused an obsolete identity",
        )
        tw.connect_pair(active[0], replacement, active)
        tw.connect_pair(active[1], replacement, active)
        tw.ensure_namespace(replacement, args.namespace)
        for survivor in active[:2]:
            tw.share(survivor, replacement, args.namespace, active)
            tw.share(replacement, survivor, args.namespace, active)
        tw.wait_for(
            "one-node replacement reseed",
            nodes,
            lambda: all(
                tw.automation_ready(node, args.namespace)
                and tw.branch_count(node, args.namespace) == 3
                and not tw.conflict_files(node)
                and operator_tree_summary(node.worktree) == expected
                for node in nodes
            ),
            240,
        )
        repair_all(nodes, args.namespace)
        stage("one-node empty replacement converged and repaired")
        live_principals = {node.principal.lower() for node in nodes}
        tw.require(
            all(branch_principals(node, args.namespace) == live_principals for node in nodes),
            "one-node replacement frontier retained an obsolete writer",
        )

        obsolete_principals = old_principals | live_principals
        for node in list(nodes):
            destroy_node(node, state_root)
        nodes = [
            tw.Node(chr(97 + index), state_root / f"replacement-all-{index + 1}",
                    phrase, binary, bootstrap)
            for index, phrase in enumerate(tw.RECALL_PHRASES)
        ]
        for node in nodes:
            tw.private_directory(node.worktree)
        start_nodes(nodes)
        tw.require(connect_full_mesh(nodes, args.namespace) == 6, "bad replacement share count")
        # The selected backup is ordinary operator data.  Install it only
        # after the fresh identities have a quiescent six-edge policy graph,
        # then let normal publication reseed every replacement.
        copy_operator_tree(restored, nodes[0].worktree)
        stage("fresh three-node mesh established and selected backup installed")
        replacement_principals = {node.principal.lower() for node in nodes}
        tw.require(
            replacement_principals.isdisjoint(obsolete_principals),
            "all-node replacement reused an obsolete principal",
        )
        tw.wait_for(
            "all-node backup reseed",
            nodes,
            lambda: all(
                not tw.conflict_files(node)
                and operator_tree_summary(node.worktree) == expected
                for node in nodes
            ),
            240,
        )
        repair_all(nodes, args.namespace)
        stage("all-live-node replacement converged and repaired")
        tw.require(
            all(
                branch_principals(node, args.namespace) == replacement_principals
                for node in nodes
            ),
            "replacement frontier contains an obsolete principal",
        )
        for index, node in enumerate(nodes, start=1):
            view = recovery_root / f"replacement-{index}-verified-view"
            copy_operator_tree(node.worktree, view)
            verifier_reports.append(
                verify_restore(binary, backup, view, recovery_provenance)
            )

        verifier_hashes = [
            str(report["sha256"]) for report in verifier_reports
        ]
        operator_provenance = (
            "present" if recovery_provenance else "absent"
        )
        receipt = {
            "recovery_rehearsal": True,
            "recovery_model": "same-vm-independent-backup-not-assessed",
            "recovery_backup_independence": "not-assessed",
            "recovery_restore_provenance": "not-assessed",
            "recovery_operator_provenance": operator_provenance,
            "recovery_operator_provenance_bound": bool(recovery_provenance),
            "recovery_restore_reports_with_provenance": (
                len(verifier_reports) if recovery_provenance else 0
            ),
            "recovery_root_devices_differ": [
                int(report["root_devices_differ"])
                for report in verifier_reports
            ],
            "recovery_files": expected["files"],
            "recovery_directories": expected["directories"],
            "recovery_bytes": expected["bytes"],
            "recovery_tree_sha256": expected["digest"],
            "recovery_verifier_matches": len(verifier_hashes),
            "recovery_verifier_report_sha256": verifier_hashes,
            "recovery_one_node_empty_replacement": True,
            "recovery_one_node_capability_revocations": 2,
            "recovery_one_node_writer_cutoffs": 2,
            "recovery_one_node_transport_peer_removals": 2,
            "recovery_one_node_post_cutoff_checkpoints": 2,
            "recovery_one_node_survivor_restarts": 2,
            "recovery_one_node_branch_count": [3, 3, 3],
            "recovery_all_live_nodes_lost": True,
            "recovery_replacement_nodes": 3,
            "recovery_replacement_branch_count": [3, 3, 3],
            "recovery_obsolete_principals_absent": True,
            "recovery_obsolete_principal_sha256": sorted(
                tw.sha256_text(value) for value in obsolete_principals
            ),
            "recovery_replacement_principal_sha256": sorted(
                tw.sha256_text(value) for value in replacement_principals
            ),
            "recovery_repair_verified_nodes": 6,
            "recovery_elapsed_ms": int((time.monotonic() - started) * 1000),
            "recovery_contains_secrets": False,
        }
        if recovery_provenance:
            receipt.update(
                {
                    "recovery_backup_system_sha256": tw.sha256_text(
                        args.backup_system
                    ),
                    "recovery_backup_generation_sha256": tw.sha256_text(
                        args.backup_generation
                    ),
                    "recovery_backup_failure_domain_sha256": tw.sha256_text(
                        args.backup_failure_domain
                    ),
                    "recovery_restore_provenance_sha256": tw.sha256_text(
                        args.restore_provenance
                    ),
                }
            )
        temporary = evidence.with_suffix(evidence.suffix + ".tmp")
        temporary.write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary.chmod(0o600)
        temporary.replace(evidence)
        print(json.dumps(receipt, sort_keys=True))
        return 0
    except (OSError, subprocess.SubprocessError, tw.QualificationError) as error:
        print(f"sync recovery rehearsal failed: {error}", file=sys.stderr)
        return 1
    finally:
        for node in reversed(nodes):
            try:
                node.stop()
            except (OSError, subprocess.SubprocessError, tw.QualificationError):
                pass
        if bootstrap_process.poll() is None:
            os.killpg(bootstrap_process.pid, signal.SIGTERM)
            try:
                bootstrap_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(bootstrap_process.pid, signal.SIGKILL)
                bootstrap_process.wait(timeout=5)
        bootstrap_log.close()
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        lock.close()


if __name__ == "__main__":
    raise SystemExit(main())
