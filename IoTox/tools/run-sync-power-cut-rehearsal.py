#!/usr/bin/env python3
"""Arm and recover one real Sandwurm VMM-cut tree-v2 transition.

The first boot establishes three ext4-backed writers, durably records the exact
prior and successor summaries, starts one offline follower, and emits an arm
receipt only after a correctly decoded pending-workspace or projection-stage
boundary appears.
It then waits for the host to kill the VMM.  The second boot mounts the same
images, admits only the exact prior or completed follower view, and requires
normal convergence plus repair.
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
import subprocess
import sys
import tempfile
import time


ROOT = Path(__file__).resolve().parent.parent
THREE_WRITER = ROOT / "tools/run-sync-three-writer.py"
RECOVERY = ROOT / "tools/run-sync-recovery-rehearsal.py"
STORAGE_FAULT = ROOT / "tools/run-sync-storage-fault-rehearsal.py"
WORKSPACE_MARKER_SCHEMA = "iotox.sync-power-cut-state.v3"
WORKSPACE_ARM_SCHEMA = "iotox.sync-power-cut-arm.v3"
WORKSPACE_RECEIPT_SCHEMA = "iotox.sync-power-cut.v3"
OBJECT_MARKER_SCHEMA = "iotox.sync-power-cut-state.v4"
OBJECT_ARM_SCHEMA = "iotox.sync-power-cut-arm.v4"
OBJECT_RECEIPT_SCHEMA = "iotox.sync-power-cut.v4"
PUBLICATION_MARKER_SCHEMA = "iotox.sync-power-cut-state.v5"
PUBLICATION_ARM_SCHEMA = "iotox.sync-power-cut-arm.v5"
PUBLICATION_RECEIPT_SCHEMA = "iotox.sync-power-cut.v5"
POST_PUBLICATION_MARKER_SCHEMA = "iotox.sync-power-cut-state.v6"
POST_PUBLICATION_ARM_SCHEMA = "iotox.sync-power-cut-arm.v6"
POST_PUBLICATION_RECEIPT_SCHEMA = "iotox.sync-power-cut.v6"
WORKSPACE_MAGIC = b"IOTXTWS1"
WORKSPACE_FORMAT = 1
WORKSPACE_STABLE = 1
WORKSPACE_PENDING_EXCHANGE = 2
WORKSPACE_PHASE_ENCODING = "stable=1,pending-exchange=2"
WORKSPACE_CUT_BOUNDARIES = {
    "pre-exchange-pending",
    "post-exchange-pending",
}
OBJECT_CUT_BOUNDARIES = {"receive-staging-partial", "cas-install-temporary"}
PRE_PUBLICATION_CUT_BOUNDARIES = {
    "manifest-install-temporary",
    "branch-record-install-temporary",
    "branch-pointer-update-temporary",
}
POST_PUBLICATION_CUT_BOUNDARIES = {
    "manifest-install-directory-fsync",
    "branch-record-install-directory-fsync",
    "branch-pointer-update-directory-fsync",
}
PUBLICATION_CUT_BOUNDARIES = (
    PRE_PUBLICATION_CUT_BOUNDARIES | POST_PUBLICATION_CUT_BOUNDARIES
)
CUT_BOUNDARIES = (
    WORKSPACE_CUT_BOUNDARIES
    | OBJECT_CUT_BOUNDARIES
    | PUBLICATION_CUT_BOUNDARIES
)
RECEIVE_STAGING = re.compile(r"^\.receive-[0-9a-f]{16}\.part$")
TRANSPORT_RECEIVE_STAGING = re.compile(
    r"^\.iotox-\.receive-[0-9a-f]{16}\.part\.part-[0-9A-Za-z]{6}$"
)
HEX_FANOUT = re.compile(r"^[0-9a-f]{2}$")
MANIFEST_NAME = re.compile(r"^[0-9a-f]{64}\.manifest$")
BRANCH_NAME = re.compile(r"^[0-9a-f]{64}\.branch$")
MAXIMUM_PUBLICATION_BYTES = 4 * 1024 * 1024
STRACE_DELAY = "2s"


def load_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load helper: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def boot_id_sha256() -> str:
    value = Path("/proc/sys/kernel/random/boot_id").read_text(
        encoding="ascii"
    ).strip()
    if not value:
        raise RuntimeError("kernel boot identity is empty")
    return hashlib.sha256(value.encode("ascii")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def write_json_durable(path: Path, record: dict[str, object]) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    path.parent.chmod(0o700)
    temporary = path.with_name(path.name + ".tmp")
    encoded = json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n"
    descriptor = os.open(
        temporary,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC,
        0o600,
    )
    try:
        view = memoryview(encoded.encode("utf-8"))
        offset = 0
        while offset < len(view):
            offset += os.write(descriptor, view[offset:])
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    os.replace(temporary, path)
    descriptor = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def read_json_regular(path: Path, maximum_bytes: int = 64 * 1024) -> dict[str, object]:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError(f"required record is absent or unsafe: {path}")
    if path.stat().st_size > maximum_bytes:
        raise RuntimeError(f"record exceeds its byte ceiling: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"record is not an object: {path}")
    return value


def summary_valid(value: object) -> bool:
    return (
        isinstance(value, dict)
        and set(value) == {"bytes", "digest", "directories", "files"}
        and isinstance(value.get("bytes"), int)
        and value["bytes"] >= 0
        and isinstance(value.get("directories"), int)
        and value["directories"] >= 0
        and isinstance(value.get("files"), int)
        and value["files"] >= 0
        and isinstance(value.get("digest"), str)
        and len(value["digest"]) == 64
        and all(character in "0123456789abcdef" for character in value["digest"])
    )


def object_cut(cut_boundary: str) -> bool:
    return cut_boundary in OBJECT_CUT_BOUNDARIES


def publication_cut(cut_boundary: str) -> bool:
    return cut_boundary in PUBLICATION_CUT_BOUNDARIES


def post_publication_cut(cut_boundary: str) -> bool:
    return cut_boundary in POST_PUBLICATION_CUT_BOUNDARIES


def publication_scheduler_fence(cut_boundary: str) -> str:
    return (
        "strace-path-filtered-fsync-delay-enter+sigstop"
        if post_publication_cut(cut_boundary)
        else "strace-path-filtered-delay-enter+sigstop"
    )


def marker_schema(cut_boundary: str) -> str:
    if post_publication_cut(cut_boundary):
        return POST_PUBLICATION_MARKER_SCHEMA
    if publication_cut(cut_boundary):
        return PUBLICATION_MARKER_SCHEMA
    return OBJECT_MARKER_SCHEMA if object_cut(cut_boundary) else WORKSPACE_MARKER_SCHEMA


def arm_schema(cut_boundary: str) -> str:
    if post_publication_cut(cut_boundary):
        return POST_PUBLICATION_ARM_SCHEMA
    if publication_cut(cut_boundary):
        return PUBLICATION_ARM_SCHEMA
    return OBJECT_ARM_SCHEMA if object_cut(cut_boundary) else WORKSPACE_ARM_SCHEMA


def receipt_schema(cut_boundary: str) -> str:
    if post_publication_cut(cut_boundary):
        return POST_PUBLICATION_RECEIPT_SCHEMA
    if publication_cut(cut_boundary):
        return PUBLICATION_RECEIPT_SCHEMA
    return OBJECT_RECEIPT_SCHEMA if object_cut(cut_boundary) else WORKSPACE_RECEIPT_SCHEMA


def classify_initial(
    observed: list[dict[str, object]],
    prior: dict[str, object],
    completed: dict[str, object],
) -> list[str]:
    if len(observed) != 3:
        raise RuntimeError("power-cut recovery requires exactly three initial views")
    classifications: list[str] = []
    for index, value in enumerate(observed):
        if value == completed:
            classifications.append("completed")
        elif index == 2 and value == prior:
            classifications.append("prior")
        else:
            raise RuntimeError(
                f"node {index + 1} exposed neither its permitted prior nor completed tree"
            )
    return classifications


def decode_workspace_state_header(header: bytes) -> tuple[str, int | None]:
    if (
        len(header) != 10
        or header[:8] != WORKSPACE_MAGIC
        or header[8] != WORKSPACE_FORMAT
    ):
        return "unrecognized", None
    phase = header[9]
    if phase == WORKSPACE_STABLE:
        return "stable", phase
    if phase == WORKSPACE_PENDING_EXCHANGE:
        return "pending", phase
    return "unrecognized", phase


def workspace_state_class(path: Path) -> tuple[str, int | None]:
    try:
        header = path.read_bytes()[:10]
    except FileNotFoundError:
        return "absent", None
    return decode_workspace_state_header(header)


def workspace_state_snapshot(path: Path) -> dict[str, object]:
    try:
        header = path.read_bytes()[:88]
    except FileNotFoundError:
        return {"state": "absent", "phase": None}
    state, phase = decode_workspace_state_header(header[:10])
    if state == "unrecognized" or len(header) != 88:
        return {"state": "unrecognized", "phase": phase}
    result: dict[str, object] = {"state": state, "phase": phase}
    result["active_manifest"] = header[24:56].hex()
    result["pending_manifest"] = header[56:88].hex()
    return result


def projection_orientation(
    marker: Path, namespace: str, snapshot: dict[str, object]
) -> str:
    try:
        if marker.is_symlink() or not marker.is_file() or marker.stat().st_size > 4096:
            return "unrecognized"
        fields: dict[str, str] = {}
        for line in marker.read_text(encoding="ascii").splitlines():
            key, separator, value = line.partition("=")
            if not separator:
                return "unrecognized"
            if key in {"namespace", "manifest"}:
                if key in fields:
                    return "unrecognized"
                fields[key] = value
    except (FileNotFoundError, OSError, UnicodeError):
        return "absent"
    manifest = fields.get("manifest", "")
    if (
        fields.get("namespace") != namespace
        or len(manifest) != 64
        or any(character not in "0123456789abcdef" for character in manifest)
    ):
        return "unrecognized"
    if manifest == snapshot.get("active_manifest"):
        return "active"
    if manifest == snapshot.get("pending_manifest"):
        return "pending"
    return "other"


def wait_workspace_transition(
    node: object, namespace: str, timeout: int, cut_boundary: str
) -> dict[str, object]:
    workspace_state = (
        node.policy_root / "data" / namespace / "tree-v2" / "workspace.state"
    )
    stage_path = node.root / f".worktree.iotox-{namespace}.stage"
    marker_path = node.worktree / ".iotox-conflicts" / ".iotox-projection"
    required_orientation = (
        "active" if cut_boundary == "pre-exchange-pending" else "pending"
    )
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        node.ensure_running()
        snapshot = workspace_state_snapshot(workspace_state)
        if snapshot.get("state") == "pending":
            active_manifest = snapshot.get("active_manifest")
            pending_manifest = snapshot.get("pending_manifest")
            if (
                not isinstance(active_manifest, str)
                or not isinstance(pending_manifest, str)
                or active_manifest == "00" * 32
                or pending_manifest == "00" * 32
                or active_manifest == pending_manifest
            ):
                time.sleep(0.001)
                continue
            orientation = projection_orientation(marker_path, namespace, snapshot)
            confirmed = workspace_state_snapshot(workspace_state)
            if snapshot == confirmed and orientation == required_orientation:
                return {
                    "transition": "pending-workspace",
                    "cut_boundary": cut_boundary,
                    "projection_orientation": orientation,
                    "projection_stage_present": stage_path.exists(),
                    "workspace_phase_raw": WORKSPACE_PENDING_EXCHANGE,
                }
            time.sleep(0.0001)
            continue
        time.sleep(0.001)
    raise RuntimeError(f"tree-v2 {cut_boundary} transition was not observed")


def expected_object_path(node: object, namespace: str, digest: str) -> Path:
    return (
        node.policy_root
        / "data"
        / namespace
        / "tree-v2"
        / "objects"
        / digest[:2]
        / digest[2:]
    )


def path_present(path: Path) -> bool:
    try:
        path.lstat()
        return True
    except FileNotFoundError:
        return False


def private_temporary(path: Path, maximum_bytes: int) -> os.stat_result | None:
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return None
    if (
        path.is_symlink()
        or not path.is_file()
        or metadata.st_uid != os.geteuid()
        or metadata.st_nlink != 1
        or metadata.st_mode & 0o777 != 0o600
        or metadata.st_size < 0
        or metadata.st_size > maximum_bytes
    ):
        raise RuntimeError(f"tree-v2 power-cut temporary is unsafe: {path}")
    return metadata


def wait_object_transition(
    node: object,
    namespace: str,
    timeout: int,
    cut_boundary: str,
    expected_digest: str,
    expected_bytes: int,
) -> dict[str, object]:
    tree = node.policy_root / "data" / namespace / "tree-v2"
    final_object = expected_object_path(node, namespace, expected_digest)
    workspace_state = tree / "workspace.state"
    marker_path = node.worktree / ".iotox-conflicts" / ".iotox-projection"
    deadline = time.monotonic() + timeout
    minimum_receive_bytes = min(8 * 1024 * 1024, expected_bytes // 4)
    while time.monotonic() < deadline:
        node.ensure_running()
        candidates: list[tuple[str, Path]] = []
        if cut_boundary == "receive-staging-partial":
            incoming = tree / "incoming"
            try:
                candidates = [
                    ("transport-receive-staging", path)
                    for path in incoming.iterdir()
                    if TRANSPORT_RECEIVE_STAGING.fullmatch(path.name)
                ]
            except FileNotFoundError:
                candidates = []
        else:
            candidates = [
                (
                    "cas-install",
                    final_object.parent / ".install.tmp",
                )
            ]
        for temporary_class, temporary in candidates:
            first = private_temporary(temporary, expected_bytes)
            if first is None:
                continue
            if cut_boundary == "receive-staging-partial" and not (
                minimum_receive_bytes <= first.st_size < expected_bytes
            ):
                continue
            if first.st_size <= 0 or path_present(final_object):
                continue
            snapshot = workspace_state_snapshot(workspace_state)
            orientation = projection_orientation(marker_path, namespace, snapshot)
            if snapshot.get("state") != "stable" or orientation != "active":
                continue
            second = private_temporary(temporary, expected_bytes)
            if (
                second is None
                or first.st_dev != second.st_dev
                or first.st_ino != second.st_ino
                or second.st_size <= 0
                or path_present(final_object)
            ):
                continue
            stop_agent_at_boundary(node)
            stopped = private_temporary(temporary, expected_bytes)
            stopped_snapshot = workspace_state_snapshot(workspace_state)
            stopped_orientation = projection_orientation(
                marker_path, namespace, stopped_snapshot
            )
            valid_stopped = (
                stopped is not None
                and stopped.st_dev == second.st_dev
                and stopped.st_ino == second.st_ino
                and stopped.st_size > 0
                and not path_present(final_object)
                and stopped_snapshot.get("state") == "stable"
                and stopped_orientation == "active"
                and (
                    cut_boundary != "receive-staging-partial"
                    or stopped.st_size < expected_bytes
                )
            )
            if not valid_stopped:
                assert node.process is not None
                os.killpg(node.process.pid, signal.SIGCONT)
                continue
            assert stopped is not None
            return {
                "transition": temporary_class,
                "cut_boundary": cut_boundary,
                "projection_orientation": stopped_orientation,
                "projection_stage_present": (
                    path_present(
                        node.root / f".worktree.iotox-{namespace}.stage"
                    )
                ),
                "workspace_phase_raw": WORKSPACE_STABLE,
                "temporary_class": temporary_class,
                "temporary_bytes_at_arm": stopped.st_size,
                "temporary_mode_at_arm": "0600",
                "temporary_link_count_at_arm": second.st_nlink,
                "temporary_owner_match_at_arm": second.st_uid == os.geteuid(),
                "expected_object_sha256": expected_digest,
                "expected_object_bytes": expected_bytes,
                "final_object_present_at_arm": False,
                "agent_sigstop_at_arm": True,
            }
        time.sleep(0.0001)
    raise RuntimeError(f"tree-v2 {cut_boundary} transition was not observed")


def process_state(pid: int) -> str:
    try:
        return next(
            line.partition(":")[2].strip()
            for line in Path(f"/proc/{pid}/status").read_text(
                encoding="ascii"
            ).splitlines()
            if line.startswith("State:")
        )
    except (FileNotFoundError, StopIteration):
        return ""


def process_group_members(group: int) -> set[int]:
    members: set[int] = set()
    for process in Path("/proc").iterdir():
        if not process.name.isdigit():
            continue
        pid = int(process.name)
        try:
            if os.getpgid(pid) == group:
                members.add(pid)
        except (ProcessLookupError, PermissionError):
            continue
    return members


def stop_agent_at_boundary(
    node: object, expected_trace_tid: int | None = None
) -> None:
    if node.process is None or node.process.poll() is not None:
        raise RuntimeError("tree-v2 follower exited before boundary stop")
    if expected_trace_tid is None:
        os.killpg(node.process.pid, signal.SIGSTOP)
    else:
        identity = traced_agent_identity(node, expected_trace_tid)
        if identity is None:
            raise RuntimeError("traced Agent identity vanished before boundary stop")
        agent_pid, _ = identity
        if os.getpgid(node.process.pid) != node.process.pid or process_group_members(
            node.process.pid
        ) != {node.process.pid, agent_pid}:
            raise RuntimeError("tracer/Agent process group is not exact")
        # Keep ptrace live while delivering SIGSTOP to the multithreaded Agent.
        # Stopping the whole group at once can stop strace before it propagates
        # the group-stop, leaving otherwise sleeping Agent threads runnable.
        os.kill(agent_pid, signal.SIGSTOP)
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            if traced_agent_identity(
                node, expected_trace_tid, require_stopped=True
            ) == (agent_pid, expected_trace_tid):
                break
            time.sleep(0.001)
        else:
            raise RuntimeError("traced Agent thread group did not stop")
        if process_group_members(node.process.pid) != {node.process.pid, agent_pid}:
            raise RuntimeError("tracer/Agent process group changed during boundary stop")
        os.kill(node.process.pid, signal.SIGSTOP)
    deadline = time.monotonic() + 2
    while time.monotonic() < deadline:
        state = process_state(node.process.pid)
        process_stopped = state.startswith("T ") or state.startswith("t ")
        traced_agent_stopped = (
            expected_trace_tid is None
            or traced_agent_identity(
                node, expected_trace_tid, require_stopped=True
            )
            == (agent_pid, expected_trace_tid)
        )
        group_exact = (
            expected_trace_tid is None
            or process_group_members(node.process.pid)
            == {node.process.pid, agent_pid}
        )
        if process_stopped and traced_agent_stopped and group_exact:
            return
        time.sleep(0.001)
    raise RuntimeError("tree-v2 follower did not enter SIGSTOP at the cut boundary")


def inspect_object_pipeline(
    node: object, namespace: str, expected_digest: str, expected_bytes: int
) -> dict[str, object]:
    tree = node.policy_root / "data" / namespace / "tree-v2"
    incoming_records: list[os.stat_result] = []
    incoming = tree / "incoming"
    if path_present(incoming):
        if incoming.is_symlink() or not incoming.is_dir():
            raise RuntimeError("tree-v2 recovered incoming path is unsafe")
        for path in incoming.iterdir():
            if not (
                RECEIVE_STAGING.fullmatch(path.name)
                or TRANSPORT_RECEIVE_STAGING.fullmatch(path.name)
            ):
                raise RuntimeError("tree-v2 recovered incoming entry is noncanonical")
            metadata = private_temporary(path, expected_bytes)
            if metadata is None:
                continue
            incoming_records.append(metadata)
    cas_records: list[os.stat_result] = []
    objects = tree / "objects"
    if path_present(objects):
        if objects.is_symlink() or not objects.is_dir():
            raise RuntimeError("tree-v2 recovered object path is unsafe")
        for fanout in objects.iterdir():
            if not HEX_FANOUT.fullmatch(fanout.name):
                raise RuntimeError("tree-v2 recovered CAS fanout is noncanonical")
            if fanout.is_symlink() or not fanout.is_dir():
                raise RuntimeError("tree-v2 recovered CAS fanout is unsafe")
            temporary = fanout / ".install.tmp"
            metadata = private_temporary(temporary, expected_bytes)
            if metadata is not None:
                cas_records.append(metadata)
    final_object = expected_object_path(node, namespace, expected_digest)
    if path_present(final_object):
        metadata = private_temporary(final_object, expected_bytes)
        if (
            metadata is None
            or metadata.st_size != expected_bytes
            or sha256_file(final_object) != expected_digest
        ):
            raise RuntimeError("tree-v2 digest-named object is partial or corrupt")
        final_state = "exact"
    else:
        final_state = "absent"
    return {
        "incoming_temporary_count": len(incoming_records),
        "incoming_temporary_bytes": sum(item.st_size for item in incoming_records),
        "cas_install_temporary_count": len(cas_records),
        "cas_install_temporary_bytes": sum(item.st_size for item in cas_records),
        "expected_object_state": final_state,
    }


def exact_private_file(path: Path, maximum_bytes: int) -> dict[str, object]:
    metadata = private_temporary(path, maximum_bytes)
    if metadata is None or metadata.st_size <= 0:
        raise RuntimeError(f"tree-v2 publication file is absent or empty: {path}")
    return {
        "bytes": metadata.st_size,
        "sha256": sha256_file(path),
    }


def publication_targets(
    nodes: list[object], namespace: str
) -> dict[str, dict[str, object]]:
    if len(nodes) != 3:
        raise RuntimeError("publication target discovery requires three nodes")
    trees = [
        node.policy_root / "data" / namespace / "tree-v2" for node in nodes
    ]
    survivor_branches: list[dict[str, dict[str, object]]] = []
    for tree in trees[:2]:
        entries: dict[str, dict[str, object]] = {}
        for path in (tree / "branches").iterdir():
            if BRANCH_NAME.fullmatch(path.name) is None:
                raise RuntimeError("survivor branch directory is noncanonical")
            entries[path.name] = exact_private_file(
                path, MAXIMUM_PUBLICATION_BYTES
            )
        survivor_branches.append(entries)
    if survivor_branches[0] != survivor_branches[1]:
        raise RuntimeError("survivors disagree on the publication frontier")

    follower_branches: dict[str, dict[str, object]] = {}
    for path in (trees[2] / "branches").iterdir():
        if BRANCH_NAME.fullmatch(path.name) is None:
            raise RuntimeError("follower branch directory is noncanonical")
        follower_branches[path.name] = exact_private_file(
            path, MAXIMUM_PUBLICATION_BYTES
        )
    if set(follower_branches) != set(survivor_branches[0]):
        raise RuntimeError("follower and survivors disagree on branch writers")
    changed = [
        name
        for name, expected in survivor_branches[0].items()
        if name in follower_branches and follower_branches[name] != expected
    ]
    if len(changed) != 1:
        raise RuntimeError(
            "publication campaign requires exactly one advanced writer pointer"
        )
    pointer_name = changed[0]
    pointer_path = trees[0] / "branches" / pointer_name
    pointer_bytes = pointer_path.read_bytes()
    if (
        len(pointer_bytes) < 256
        or pointer_bytes[:8] != b"IOTXTVB1"
        or pointer_bytes[32:64].hex() + ".branch" != pointer_name
    ):
        raise RuntimeError("publication target branch is malformed")
    manifest_name = pointer_bytes[96:128].hex() + ".manifest"
    if MANIFEST_NAME.fullmatch(manifest_name) is None:
        raise RuntimeError("publication target manifest name is malformed")
    manifest = exact_private_file(
        trees[0] / "manifests" / manifest_name, MAXIMUM_PUBLICATION_BYTES
    )
    if path_present(trees[2] / "manifests" / manifest_name):
        raise RuntimeError("follower already stores the publication manifest")

    record_matches: list[tuple[str, dict[str, object]]] = []
    pointer = survivor_branches[0][pointer_name]
    for path in (trees[0] / "records").iterdir():
        if BRANCH_NAME.fullmatch(path.name) is None:
            raise RuntimeError("survivor record directory is noncanonical")
        record = exact_private_file(path, MAXIMUM_PUBLICATION_BYTES)
        if record == pointer:
            record_matches.append((path.name, record))
    if len(record_matches) != 1:
        raise RuntimeError("publication target immutable record is ambiguous")
    record_name, record = record_matches[0]
    if path_present(trees[2] / "records" / record_name):
        raise RuntimeError("follower already stores the publication branch record")

    return {
        "manifest": {"name": manifest_name, **manifest},
        "branch_record": {"name": record_name, **record},
        "branch_pointer": {
            "name": pointer_name,
            **pointer,
            "prior_bytes": follower_branches[pointer_name]["bytes"],
            "prior_sha256": follower_branches[pointer_name]["sha256"],
        },
    }


def publication_target_valid(
    value: object, *, pointer: bool = False
) -> bool:
    required = {"name", "bytes", "sha256"}
    if pointer:
        required |= {"prior_bytes", "prior_sha256"}
    return (
        isinstance(value, dict)
        and set(value) == required
        and isinstance(value.get("name"), str)
        and (
            BRANCH_NAME.fullmatch(value["name"]) is not None
            if pointer
            else (
                MANIFEST_NAME.fullmatch(value["name"]) is not None
                or BRANCH_NAME.fullmatch(value["name"]) is not None
            )
        )
        and isinstance(value.get("bytes"), int)
        and 0 < value["bytes"] <= MAXIMUM_PUBLICATION_BYTES
        and isinstance(value.get("sha256"), str)
        and re.fullmatch(r"[0-9a-f]{64}", value["sha256"]) is not None
        and (
            not pointer
            or (
                isinstance(value.get("prior_bytes"), int)
                and 0 < value["prior_bytes"] <= MAXIMUM_PUBLICATION_BYTES
                and isinstance(value.get("prior_sha256"), str)
                and re.fullmatch(r"[0-9a-f]{64}", value["prior_sha256"])
                is not None
                and value["prior_sha256"] != value["sha256"]
            )
        )
    )


def validate_publication_targets(value: object) -> dict[str, dict[str, object]]:
    if (
        not isinstance(value, dict)
        or set(value) != {"manifest", "branch_record", "branch_pointer"}
        or not publication_target_valid(value.get("manifest"))
        or not publication_target_valid(value.get("branch_record"))
        or not publication_target_valid(value.get("branch_pointer"), pointer=True)
    ):
        raise RuntimeError("power-cut publication targets are malformed")
    manifest = value["manifest"]
    record = value["branch_record"]
    pointer = value["branch_pointer"]
    assert isinstance(manifest, dict)
    assert isinstance(record, dict)
    assert isinstance(pointer, dict)
    if not str(manifest["name"]).endswith(".manifest"):
        raise RuntimeError("publication manifest target has the wrong suffix")
    if not str(record["name"]).endswith(".branch"):
        raise RuntimeError("publication record target has the wrong suffix")
    if record["sha256"] != pointer["sha256"] or record["bytes"] != pointer["bytes"]:
        raise RuntimeError("publication record and pointer bytes disagree")
    return value


def publication_target_commitments(
    targets: dict[str, dict[str, object]],
) -> dict[str, dict[str, object]]:
    commitments: dict[str, dict[str, object]] = {}
    for name in ("manifest", "branch_record", "branch_pointer"):
        target = targets[name]
        commitment: dict[str, object] = {
            "name_sha256": hashlib.sha256(
                str(target["name"]).encode("ascii")
            ).hexdigest(),
            "bytes": target["bytes"],
            "sha256": target["sha256"],
        }
        if name == "branch_pointer":
            commitment.update(
                {
                    "prior_bytes": target["prior_bytes"],
                    "prior_sha256": target["prior_sha256"],
                }
            )
        commitments[name] = commitment
    return commitments


def publication_state(
    node: object,
    namespace: str,
    targets: dict[str, dict[str, object]],
) -> dict[str, object]:
    tree = node.policy_root / "data" / namespace / "tree-v2"
    locations = {
        "manifest": tree / "manifests" / str(targets["manifest"]["name"]),
        "branch_record": tree
        / "records"
        / str(targets["branch_record"]["name"]),
        "branch_pointer": tree
        / "branches"
        / str(targets["branch_pointer"]["name"]),
    }
    states: dict[str, str] = {}
    for name in ("manifest", "branch_record"):
        path = locations[name]
        if not path_present(path):
            states[name] = "absent"
            continue
        actual = exact_private_file(path, MAXIMUM_PUBLICATION_BYTES)
        if actual != {
            "bytes": targets[name]["bytes"],
            "sha256": targets[name]["sha256"],
        }:
            raise RuntimeError(f"publication {name} final is corrupt")
        states[name] = "exact"
    pointer_path = locations["branch_pointer"]
    actual_pointer = exact_private_file(pointer_path, MAXIMUM_PUBLICATION_BYTES)
    if actual_pointer == {
        "bytes": targets["branch_pointer"]["prior_bytes"],
        "sha256": targets["branch_pointer"]["prior_sha256"],
    }:
        states["branch_pointer"] = "prior"
    elif actual_pointer == {
        "bytes": targets["branch_pointer"]["bytes"],
        "sha256": targets["branch_pointer"]["sha256"],
    }:
        states["branch_pointer"] = "successor"
    else:
        raise RuntimeError("publication branch pointer is neither prior nor successor")

    temporary_records: dict[str, os.stat_result | None] = {
        "manifest": private_temporary(
            tree / "manifests" / ".install.tmp", MAXIMUM_PUBLICATION_BYTES
        ),
        "branch_record": private_temporary(
            tree / "records" / ".install.tmp", MAXIMUM_PUBLICATION_BYTES
        ),
        "branch_pointer": private_temporary(
            tree / "branches" / ".update.tmp", MAXIMUM_PUBLICATION_BYTES
        ),
    }
    for name, metadata in temporary_records.items():
        if metadata is not None and (
            metadata.st_size != targets[name]["bytes"]
            or sha256_file(
                {
                    "manifest": tree / "manifests" / ".install.tmp",
                    "branch_record": tree / "records" / ".install.tmp",
                    "branch_pointer": tree / "branches" / ".update.tmp",
                }[name]
            )
            != targets[name]["sha256"]
        ):
            raise RuntimeError(f"publication {name} temporary is not exact")
    return {
        "manifest_state": states["manifest"],
        "branch_record_state": states["branch_record"],
        "branch_pointer_state": states["branch_pointer"],
        "manifest_temporary_count": int(temporary_records["manifest"] is not None),
        "manifest_temporary_bytes": (
            0
            if temporary_records["manifest"] is None
            else temporary_records["manifest"].st_size
        ),
        "branch_record_temporary_count": int(
            temporary_records["branch_record"] is not None
        ),
        "branch_record_temporary_bytes": (
            0
            if temporary_records["branch_record"] is None
            else temporary_records["branch_record"].st_size
        ),
        "branch_pointer_temporary_count": int(
            temporary_records["branch_pointer"] is not None
        ),
        "branch_pointer_temporary_bytes": (
            0
            if temporary_records["branch_pointer"] is None
            else temporary_records["branch_pointer"].st_size
        ),
    }


def expected_publication_prefix(cut_boundary: str) -> dict[str, str]:
    if cut_boundary == "manifest-install-temporary":
        return {
            "manifest_state": "absent",
            "branch_record_state": "absent",
            "branch_pointer_state": "prior",
        }
    if cut_boundary == "branch-record-install-temporary":
        return {
            "manifest_state": "exact",
            "branch_record_state": "absent",
            "branch_pointer_state": "prior",
        }
    if cut_boundary == "branch-pointer-update-temporary":
        return {
            "manifest_state": "exact",
            "branch_record_state": "exact",
            "branch_pointer_state": "prior",
        }
    if cut_boundary == "manifest-install-directory-fsync":
        return {
            "manifest_state": "exact",
            "branch_record_state": "absent",
            "branch_pointer_state": "prior",
        }
    if cut_boundary == "branch-record-install-directory-fsync":
        return {
            "manifest_state": "exact",
            "branch_record_state": "exact",
            "branch_pointer_state": "prior",
        }
    if cut_boundary == "branch-pointer-update-directory-fsync":
        return {
            "manifest_state": "exact",
            "branch_record_state": "exact",
            "branch_pointer_state": "successor",
        }
    raise RuntimeError("unknown publication cut boundary")


def publication_recovery_prefix_valid(
    state: dict[str, object], cut_boundary: str
) -> bool:
    if not post_publication_cut(cut_boundary):
        expected = expected_publication_prefix(cut_boundary)
        return all(state.get(key) == value for key, value in expected.items())
    allowed = {
        "manifest-install-directory-fsync": {
            "manifest_state": {"absent", "exact"},
            "branch_record_state": {"absent"},
            "branch_pointer_state": {"prior"},
        },
        "branch-record-install-directory-fsync": {
            "manifest_state": {"exact"},
            "branch_record_state": {"absent", "exact"},
            "branch_pointer_state": {"prior"},
        },
        "branch-pointer-update-directory-fsync": {
            "manifest_state": {"exact"},
            "branch_record_state": {"exact"},
            "branch_pointer_state": {"prior", "successor"},
        },
    }[cut_boundary]
    return all(state.get(key) in values for key, values in allowed.items())


def publication_temporary_state_valid(
    state: dict[str, object],
    cut_boundary: str,
    targets: dict[str, dict[str, object]],
) -> bool:
    selected = {
        "manifest-install-temporary": "manifest",
        "branch-record-install-temporary": "branch_record",
        "branch-pointer-update-temporary": "branch_pointer",
        "manifest-install-directory-fsync": "manifest",
        "branch-record-install-directory-fsync": "branch_record",
        "branch-pointer-update-directory-fsync": "branch_pointer",
    }[cut_boundary]
    for name in ("manifest", "branch_record", "branch_pointer"):
        count = state.get(f"{name}_temporary_count")
        byte_count = state.get(f"{name}_temporary_bytes")
        if name == selected:
            if (count, byte_count) not in {
                (0, 0),
                (1, targets[name]["bytes"]),
            }:
                return False
        elif count != 0 or byte_count != 0:
            return False
    return True


def publication_selection(
    node: object, namespace: str, cut_boundary: str
) -> tuple[str, str, Path, Path, str]:
    tree = node.policy_root / "data" / namespace / "tree-v2"
    transition, target_name, parent_name, temporary_name = {
        "manifest-install-temporary": (
            "manifest-install",
            "manifest",
            "manifests",
            ".install.tmp",
        ),
        "branch-record-install-temporary": (
            "branch-record-install",
            "branch_record",
            "records",
            ".install.tmp",
        ),
        "branch-pointer-update-temporary": (
            "branch-pointer-update",
            "branch_pointer",
            "branches",
            ".update.tmp",
        ),
        "manifest-install-directory-fsync": (
            "manifest-install-directory-fsync",
            "manifest",
            "manifests",
            ".install.tmp",
        ),
        "branch-record-install-directory-fsync": (
            "branch-record-install-directory-fsync",
            "branch_record",
            "records",
            ".install.tmp",
        ),
        "branch-pointer-update-directory-fsync": (
            "branch-pointer-update-directory-fsync",
            "branch_pointer",
            "branches",
            ".update.tmp",
        ),
    }[cut_boundary]
    parent = tree / parent_name
    temporary = parent / temporary_name
    trace_path = parent if post_publication_cut(cut_boundary) else temporary
    return transition, target_name, temporary, trace_path, parent_name


def traced_agent_identity(
    node: object,
    expected_trace_tid: int | None = None,
    *,
    require_stopped: bool = False,
) -> tuple[int, int] | None:
    if node.process is None:
        return None
    matches: list[tuple[int, int]] = []
    for process in Path("/proc").iterdir():
        if not process.name.isdigit():
            continue
        try:
            fields: dict[str, str] = {}
            for line in (process / "status").read_text(
                encoding="ascii", errors="replace"
            ).splitlines():
                key, separator, value = line.partition(":")
                if separator and key in {"PPid", "TracerPid"}:
                    fields[key] = value.strip()
            command = (process / "cmdline").read_bytes().split(b"\0", 1)[0]
        except (FileNotFoundError, PermissionError, OSError):
            continue
        if (
            fields.get("PPid") == str(node.process.pid)
            and fields.get("TracerPid") == str(node.process.pid)
            and command
            and Path(os.fsdecode(command)).resolve() == node.binary.resolve()
        ):
            tasks: dict[int, str] = {}
            try:
                for task in (process / "task").iterdir():
                    if not task.name.isdigit():
                        continue
                    task_fields: dict[str, str] = {}
                    for line in (task / "status").read_text(
                        encoding="ascii", errors="replace"
                    ).splitlines():
                        key, separator, value = line.partition(":")
                        if separator and key in {"State", "TracerPid"}:
                            task_fields[key] = value.strip()
                    if task_fields.get("TracerPid") != str(node.process.pid):
                        tasks = {}
                        break
                    tasks[int(task.name)] = task_fields.get("State", "")
            except (FileNotFoundError, PermissionError, OSError, ValueError):
                continue
            tracing = [
                tid for tid, state in tasks.items() if state.startswith("t ")
            ]
            candidate = (
                tracing[0]
                if expected_trace_tid is None and len(tracing) == 1
                else expected_trace_tid
            )
            if (
                tasks
                and candidate is not None
                and candidate in tracing
                and (
                    not require_stopped
                    or all(
                        state.startswith("T ") or state.startswith("t ")
                        for state in tasks.values()
                    )
                )
            ):
                matches.append((int(process.name), candidate))
    return matches[0] if len(matches) == 1 else None


def traced_agent_thread(
    node: object,
    expected_trace_tid: int | None = None,
    *,
    require_stopped: bool = False,
) -> int | None:
    identity = traced_agent_identity(
        node, expected_trace_tid, require_stopped=require_stopped
    )
    return None if identity is None else identity[1]


def wait_publication_transition(
    node: object,
    namespace: str,
    timeout: int,
    cut_boundary: str,
    targets: dict[str, dict[str, object]],
) -> dict[str, object]:
    tree = node.policy_root / "data" / namespace / "tree-v2"
    transition, target_name, temporary, _trace_path, parent_name = publication_selection(
        node, namespace, cut_boundary
    )
    post_rename = post_publication_cut(cut_boundary)
    expected = targets[target_name]
    commitments = publication_target_commitments(targets)
    workspace_state = tree / "workspace.state"
    marker_path = node.worktree / ".iotox-conflicts" / ".iotox-projection"
    stage_path = node.root / f".worktree.iotox-{namespace}.stage"
    expected_prefix = expected_publication_prefix(cut_boundary)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        node.ensure_running()
        first = private_temporary(temporary, MAXIMUM_PUBLICATION_BYTES)
        if post_rename and first is not None:
            time.sleep(0.0001)
            continue
        if not post_rename and (
            first is None
            or first.st_size != expected["bytes"]
            or sha256_file(temporary) != expected["sha256"]
        ):
            time.sleep(0.0001)
            continue
        snapshot = workspace_state_snapshot(workspace_state)
        orientation = projection_orientation(marker_path, namespace, snapshot)
        state = publication_state(node, namespace, targets)
        trace_tid = traced_agent_thread(node)
        if (
            snapshot.get("state") != "stable"
            or orientation != "active"
            or path_present(stage_path)
            or any(state[key] != value for key, value in expected_prefix.items())
            or trace_tid is None
        ):
            time.sleep(0.0001)
            continue
        second = private_temporary(temporary, MAXIMUM_PUBLICATION_BYTES)
        if post_rename and second is not None:
            continue
        if not post_rename and (
            first is None
            or second is None
            or first.st_dev != second.st_dev
            or first.st_ino != second.st_ino
            or second.st_size != expected["bytes"]
            or sha256_file(temporary) != expected["sha256"]
        ):
            continue
        stop_agent_at_boundary(node, trace_tid)
        stopped = private_temporary(temporary, MAXIMUM_PUBLICATION_BYTES)
        stopped_snapshot = workspace_state_snapshot(workspace_state)
        stopped_orientation = projection_orientation(
            marker_path, namespace, stopped_snapshot
        )
        stopped_state = publication_state(node, namespace, targets)
        stopped_stage_present = path_present(stage_path)
        stopped_trace_tid = traced_agent_thread(
            node, trace_tid, require_stopped=True
        )
        failures: list[str] = []
        if post_rename and stopped is not None:
            failures.append("temporary-present")
        elif not post_rename and stopped is None:
            failures.append("temporary-absent")
        elif not post_rename:
            assert stopped is not None and second is not None
            if stopped.st_dev != second.st_dev or stopped.st_ino != second.st_ino:
                failures.append("temporary-identity")
            if stopped.st_size != expected["bytes"]:
                failures.append("temporary-bytes")
            if sha256_file(temporary) != expected["sha256"]:
                failures.append("temporary-digest")
        if stopped_snapshot.get("state") != "stable":
            failures.append("workspace-state")
        if stopped_orientation != "active":
            failures.append("projection-orientation")
        if stopped_stage_present:
            failures.append("projection-stage")
        for key, value in expected_prefix.items():
            if stopped_state[key] != value:
                failures.append(key.replace("_", "-"))
        if stopped_trace_tid != trace_tid:
            failures.append("traced-agent-group")
        if failures:
            raise RuntimeError(
                "publication boundary changed after scheduler stop: "
                + ",".join(failures)
            )
        common = {
            "transition": transition,
            "cut_boundary": cut_boundary,
            "projection_orientation": "active",
            "projection_stage_present": stopped_stage_present,
            "workspace_phase_raw": WORKSPACE_STABLE,
            "target_name_sha256": hashlib.sha256(
                str(expected["name"]).encode("ascii")
            ).hexdigest(),
            "publication_target_commitments": commitments,
            "destination_state_at_arm": expected_prefix[
                f"{target_name}_state"
            ],
            "qualification_scheduler_fence": publication_scheduler_fence(
                cut_boundary
            ),
            "traced_agent_at_arm": True,
            "agent_sigstop_at_arm": True,
        }
        if post_rename:
            common.update(
                {
                    "directory_class": parent_name,
                    "directory_name_sha256": hashlib.sha256(
                        parent_name.encode("ascii")
                    ).hexdigest(),
                    "selected_final_bytes_at_arm": int(expected["bytes"]),
                    "selected_final_sha256_at_arm": str(expected["sha256"]),
                    "selected_temporary_absent_at_arm": True,
                }
            )
        else:
            assert stopped is not None
            common.update(
                {
                    "temporary_class": transition,
                    "temporary_bytes_at_arm": stopped.st_size,
                    "temporary_sha256_at_arm": str(expected["sha256"]),
                    "temporary_mode_at_arm": "0600",
                    "temporary_link_count_at_arm": stopped.st_nlink,
                    "temporary_owner_match_at_arm": stopped.st_uid
                    == os.geteuid(),
                }
            )
        return common
    raise RuntimeError(f"tree-v2 {cut_boundary} transition was not observed")


def start_bootstrap(
    tw: object, binary: Path, root: Path
) -> tuple[subprocess.Popen[bytes], object, str]:
    tw.private_directory(root)
    log = (root / "bootstrap.log").open("ab")
    process = subprocess.Popen(
        [str(binary), "--ipv4"],
        cwd=root,
        stdout=log,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    public_id = root / "PUBLIC_ID.txt"
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline and not (
        public_id.is_file() and public_id.stat().st_size == 64
    ):
        tw.require(process.poll() is None, "bootstrap exited")
        time.sleep(0.05)
    key = public_id.read_text(encoding="ascii").strip()
    tw.require(bool(tw.HEX64.fullmatch(key)), "bootstrap key is invalid")
    return process, log, f"127.0.0.1:33445:{key}"


def stop_bootstrap(process: subprocess.Popen[bytes] | None, log: object | None) -> None:
    if process is not None and process.poll() is None:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=5)
    if log is not None:
        log.close()


def make_nodes(
    tw: object, binary: Path, bootstrap: str, volumes: list[object]
) -> list[object]:
    return [
        tw.Node(
            chr(97 + index),
            volumes[index].mountpoint / "node",
            tw.RECALL_PHRASES[index],
            binary,
            bootstrap,
        )
        for index in range(3)
    ]


def initialize(
    args: argparse.Namespace,
    tw: object,
    recovery: object,
    storage: object,
    state_root: Path,
    marker: Path,
) -> int:
    volumes = [
        storage.LoopExt4(
            state_root / "disks" / f"node-{index + 1}.img",
            state_root / "mounts" / f"node-{index + 1}",
            args.disk_mib,
        )
        for index in range(3)
    ]
    nodes: list[object] = []
    bootstrap_process = None
    bootstrap_log = None
    try:
        for volume in volumes:
            volume.create()
        bootstrap_process, bootstrap_log, bootstrap = start_bootstrap(
            tw, args.bootstrap.resolve(), state_root / "bootstrap"
        )
        nodes = make_nodes(tw, args.iotox.resolve(), bootstrap, volumes)
        for node in nodes:
            tw.private_directory(node.worktree)
        recovery.start_nodes(nodes)
        tw.require(
            recovery.connect_full_mesh(nodes, args.namespace) == 6,
            "bad power-cut share count",
        )
        recovery.seed_initial_tree(nodes[0], args.files, args.file_bytes)
        prior = recovery.operator_tree_summary(nodes[0].worktree)
        storage.wait_exact(
            tw,
            recovery,
            nodes,
            args.namespace,
            prior,
            "power-cut baseline convergence",
        )

        follower = nodes[2]
        follower.stop()
        seed = hashlib.sha256(b"iotox-vmm-power-cut-workspace-v1").digest()
        payload = (seed * ((args.exchange_bytes + 31) // 32))[: args.exchange_bytes]
        storage.write_exact(nodes[0].worktree / "power-cut-wide.bin", payload)
        expected_object_sha256 = hashlib.sha256(payload).hexdigest()
        completed = recovery.operator_tree_summary(nodes[0].worktree)
        storage.wait_exact(
            tw,
            recovery,
            nodes[:2],
            args.namespace,
            completed,
            "power-cut survivor convergence",
            args.timeout,
        )

        publication: dict[str, dict[str, object]] | None = None
        if publication_cut(args.cut_boundary):
            publication = publication_targets(nodes, args.namespace)

        first_boot = boot_id_sha256()
        marker_record: dict[str, object] = {
            "schema": marker_schema(args.cut_boundary),
            "phase": "recovery-required",
            "namespace": args.namespace,
            "disk_mib_per_node": args.disk_mib,
            "exchange_bytes": args.exchange_bytes,
            "cut_boundary": args.cut_boundary,
            "first_boot_id_sha256": first_boot,
            "prior": prior,
            "completed": completed,
            "tox_key_sha256": sorted(
                tw.sha256_text(node.tox_key.lower()) for node in nodes
            ),
            "principal_sha256": sorted(
                tw.sha256_text(node.principal.lower()) for node in nodes
            ),
            "contains_secrets": False,
        }
        if object_cut(args.cut_boundary):
            marker_record.update(
                {
                    "expected_object_sha256": expected_object_sha256,
                    "expected_object_bytes": len(payload),
                    "agent_sigstop_at_arm": True,
                }
            )
        if publication_cut(args.cut_boundary):
            assert publication is not None
            marker_record.update(
                {
                    "publication_targets": publication,
                    "qualification_scheduler_fence": publication_scheduler_fence(
                        args.cut_boundary
                    ),
                    "strace_delay": STRACE_DELAY,
                    "agent_sigstop_at_arm": True,
                }
            )
        write_json_durable(marker, marker_record)
        marker_sha256 = sha256_file(marker)

        if publication_cut(args.cut_boundary):
            if args.strace is None:
                raise RuntimeError("publication cut requires strace")
            _, _, _, trace_path, _ = publication_selection(
                follower, args.namespace, args.cut_boundary
            )
            follower.process_prefix = [
                str(args.strace.resolve()),
                "-f",
                "-qq",
                "-P",
                str(trace_path),
            ]
            if post_publication_cut(args.cut_boundary):
                follower.process_prefix.extend(
                    [
                        "--trace=fsync",
                        f"--inject=fsync:delay_enter={STRACE_DELAY}",
                    ]
                )
            else:
                follower.process_prefix.extend(
                    [
                        "--trace=rename,renameat2",
                        f"--inject=rename:delay_enter={STRACE_DELAY}",
                        f"--inject=renameat2:delay_enter={STRACE_DELAY}",
                    ]
                )
            follower.process_prefix.extend(
                ["-o", str(state_root / "publication-strace.log")]
            )
        follower.start()
        if publication_cut(args.cut_boundary):
            assert publication is not None
            observed = wait_publication_transition(
                follower,
                args.namespace,
                args.timeout,
                args.cut_boundary,
                publication,
            )
        elif object_cut(args.cut_boundary):
            observed = wait_object_transition(
                follower,
                args.namespace,
                args.timeout,
                args.cut_boundary,
                expected_object_sha256,
                len(payload),
            )
        else:
            observed = wait_workspace_transition(
                follower, args.namespace, args.timeout, args.cut_boundary
            )
        arm_record = {
            "schema": arm_schema(args.cut_boundary),
            "status": "armed",
            **observed,
            "workspace_phase_encoding": WORKSPACE_PHASE_ENCODING,
            "marker_sha256": marker_sha256,
            "first_boot_id_sha256": first_boot,
            "prior": prior,
            "completed": completed,
            "contains_secrets": False,
        }
        write_json_durable(args.arm_receipt.resolve(), arm_record)
        print(json.dumps(arm_record, sort_keys=True), flush=True)
        while True:
            time.sleep(3600)
    finally:
        for node in reversed(nodes):
            try:
                node.stop()
            except Exception:
                pass
        stop_bootstrap(bootstrap_process, bootstrap_log)
        for volume in reversed(volumes):
            try:
                volume.unmount()
            except Exception as error:
                print(f"warning: unable to unmount {volume.mountpoint}: {error}", file=sys.stderr)


def recover(
    args: argparse.Namespace,
    tw: object,
    recovery: object,
    storage: object,
    state_root: Path,
    marker: Path,
) -> int:
    marker_record = read_json_regular(marker)
    marker_sha256 = sha256_file(marker)
    required = {
        "schema",
        "phase",
        "namespace",
        "disk_mib_per_node",
        "exchange_bytes",
        "cut_boundary",
        "first_boot_id_sha256",
        "prior",
        "completed",
        "tox_key_sha256",
        "principal_sha256",
        "contains_secrets",
    }
    if object_cut(args.cut_boundary):
        required |= {
            "expected_object_sha256",
            "expected_object_bytes",
            "agent_sigstop_at_arm",
        }
    if publication_cut(args.cut_boundary):
        required |= {
            "publication_targets",
            "qualification_scheduler_fence",
            "strace_delay",
            "agent_sigstop_at_arm",
        }
    if (
        set(marker_record) != required
        or marker_record.get("schema") != marker_schema(args.cut_boundary)
    ):
        raise RuntimeError("power-cut durable marker is malformed")
    if (
        marker_record.get("phase") != "recovery-required"
        or marker_record.get("namespace") != args.namespace
        or marker_record.get("disk_mib_per_node") != args.disk_mib
        or marker_record.get("exchange_bytes") != args.exchange_bytes
        or marker_record.get("cut_boundary") != args.cut_boundary
        or marker_record.get("contains_secrets") is not False
        or not summary_valid(marker_record.get("prior"))
        or not summary_valid(marker_record.get("completed"))
    ):
        raise RuntimeError("power-cut durable marker contract is invalid")
    if object_cut(args.cut_boundary) and (
        not isinstance(marker_record.get("expected_object_sha256"), str)
        or len(str(marker_record["expected_object_sha256"])) != 64
        or any(
            character not in "0123456789abcdef"
            for character in str(marker_record["expected_object_sha256"])
        )
        or marker_record.get("expected_object_bytes") != args.exchange_bytes
        or marker_record.get("agent_sigstop_at_arm") is not True
    ):
        raise RuntimeError("power-cut object marker contract is invalid")
    publication: dict[str, dict[str, object]] | None = None
    if publication_cut(args.cut_boundary):
        publication = validate_publication_targets(
            marker_record.get("publication_targets")
        )
        if (
            marker_record.get("qualification_scheduler_fence")
            != publication_scheduler_fence(args.cut_boundary)
            or marker_record.get("strace_delay") != STRACE_DELAY
            or marker_record.get("agent_sigstop_at_arm") is not True
        ):
            raise RuntimeError("power-cut publication marker contract is invalid")
    prior = marker_record["prior"]
    completed = marker_record["completed"]
    assert isinstance(prior, dict) and isinstance(completed, dict)
    second_boot = boot_id_sha256()
    if second_boot == marker_record["first_boot_id_sha256"]:
        raise RuntimeError("power-cut recovery did not cross a VM boot boundary")

    volumes = [
        storage.LoopExt4(
            state_root / "disks" / f"node-{index + 1}.img",
            state_root / "mounts" / f"node-{index + 1}",
            args.disk_mib,
        )
        for index in range(3)
    ]
    nodes: list[object] = []
    bootstrap_process = None
    bootstrap_log = None
    started = time.monotonic()
    try:
        for volume in volumes:
            volume.mount_existing()
        bootstrap_process, bootstrap_log, bootstrap = start_bootstrap(
            tw,
            args.bootstrap.resolve(),
            state_root / "bootstrap-recovery" / second_boot[:16],
        )
        nodes = make_nodes(tw, args.iotox.resolve(), bootstrap, volumes)
        initial = [recovery.operator_tree_summary(node.worktree) for node in nodes]
        classifications = classify_initial(initial, prior, completed)
        if (
            object_cut(args.cut_boundary)
            or publication_cut(args.cut_boundary)
        ) and classifications[2] != "prior":
            raise RuntimeError(
                "pre-projection cut crossed a visible projection effect"
            )
        if (
            args.cut_boundary == "post-exchange-pending"
            and classifications[2] != "completed"
        ):
            raise RuntimeError(
                "post-exchange cut did not retain the completed follower projection"
            )
        follower = nodes[2]
        stage_before = (
            follower.root / f".worktree.iotox-{args.namespace}.stage"
        ).exists()
        workspace_path = (
            follower.policy_root
            / "data" / args.namespace / "tree-v2" / "workspace.state"
        )
        snapshot_before = workspace_state_snapshot(workspace_path)
        state_before = str(snapshot_before.get("state"))
        phase_before = snapshot_before.get("phase")
        if state_before not in {"pending", "stable"}:
            raise RuntimeError("power-cut workspace state is absent or unrecognized")
        orientation_before = projection_orientation(
            follower.worktree / ".iotox-conflicts" / ".iotox-projection",
            args.namespace,
            snapshot_before,
        )
        orientation_valid = (
            state_before == "stable" and orientation_before == "active"
        ) or (
            state_before == "pending"
            and orientation_before in {"active", "pending"}
            and (
                args.cut_boundary != "post-exchange-pending"
                or orientation_before == "pending"
            )
        )
        if not orientation_valid:
            raise RuntimeError(
                "power-cut projection marker does not match the recovered workspace"
            )

        pipeline_before: dict[str, object] | None = None
        if object_cut(args.cut_boundary):
            expected_digest = str(marker_record["expected_object_sha256"])
            expected_bytes = int(marker_record["expected_object_bytes"])
            pipeline_before = inspect_object_pipeline(
                follower, args.namespace, expected_digest, expected_bytes
            )
            if state_before != "stable" or orientation_before != "active":
                raise RuntimeError(
                    "object-pipeline cut changed the stable prior workspace"
                )
        publication_before: dict[str, object] | None = None
        if publication_cut(args.cut_boundary):
            assert publication is not None
            publication_before = publication_state(
                follower, args.namespace, publication
            )
            if (
                state_before != "stable"
                or orientation_before != "active"
                or not publication_recovery_prefix_valid(
                    publication_before, args.cut_boundary
                )
                or not publication_temporary_state_valid(
                    publication_before,
                    args.cut_boundary,
                    publication,
                )
            ):
                raise RuntimeError(
                    "publication cut crossed its selected metadata commit"
                )

        recovery.start_nodes(nodes)
        if sorted(
            tw.sha256_text(node.tox_key.lower()) for node in nodes
        ) != marker_record["tox_key_sha256"]:
            raise RuntimeError("Tox identity changed across the VM power cut")
        if sorted(
            tw.sha256_text(node.principal.lower()) for node in nodes
        ) != marker_record["principal_sha256"]:
            raise RuntimeError("stable principal changed across the VM power cut")
        storage.wait_exact(
            tw,
            recovery,
            nodes,
            args.namespace,
            completed,
            "post-power-cut convergence",
            args.timeout,
        )
        pipeline_after: dict[str, object] | None = None
        if object_cut(args.cut_boundary):
            pipeline_after = inspect_object_pipeline(
                follower,
                args.namespace,
                str(marker_record["expected_object_sha256"]),
                int(marker_record["expected_object_bytes"]),
            )
            if pipeline_after != {
                "incoming_temporary_count": 0,
                "incoming_temporary_bytes": 0,
                "cas_install_temporary_count": 0,
                "cas_install_temporary_bytes": 0,
                "expected_object_state": "exact",
            }:
                raise RuntimeError(
                    "object-pipeline recovery left staging or lacks the exact CAS object"
                )
        publication_after: dict[str, object] | None = None
        if publication_cut(args.cut_boundary):
            assert publication is not None
            publication_after = publication_state(
                follower, args.namespace, publication
            )
            if publication_after != {
                "manifest_state": "exact",
                "branch_record_state": "exact",
                "branch_pointer_state": "successor",
                "manifest_temporary_count": 0,
                "manifest_temporary_bytes": 0,
                "branch_record_temporary_count": 0,
                "branch_record_temporary_bytes": 0,
                "branch_pointer_temporary_count": 0,
                "branch_pointer_temporary_bytes": 0,
            }:
                raise RuntimeError(
                    "publication recovery left staging or lacks exact metadata"
                )
        receipt = {
            "schema": receipt_schema(args.cut_boundary),
            "status": "passed",
            "power_cut_recovery": True,
            "power_cut_model": "host-sigkill-cloud-hypervisor-preseeded-crash-image",
            "power_cut_transition": (
                "branch-publication"
                if publication_cut(args.cut_boundary)
                else (
                    "object-pipeline"
                    if object_cut(args.cut_boundary)
                    else "workspace-exchange"
                )
            ),
            "cut_boundary_requested": marker_record["cut_boundary"],
            "first_boot_id_sha256": marker_record["first_boot_id_sha256"],
            "recovery_boot_id_sha256": second_boot,
            "distinct_boot_observed": True,
            "initial_view_per_node": classifications,
            "initial_prior_or_completed_only": True,
            "follower_projection_stage_present_before_restart": stage_before,
            "follower_workspace_state_before_restart": state_before,
            "follower_workspace_phase_raw_before_restart": phase_before,
            "follower_projection_orientation_before_restart": orientation_before,
            "identity_preserved": True,
            "branch_count_per_node": [
                tw.branch_count(node, args.namespace) for node in nodes
            ],
            "repair_verified_nodes": 3,
            "final": completed,
            "elapsed_ms": int((time.monotonic() - started) * 1000),
            "contains_secrets": False,
            "dishonest_storage_assessed": False,
        }
        if object_cut(args.cut_boundary):
            receipt.update(
                {
                    "expected_object_sha256": marker_record[
                        "expected_object_sha256"
                    ],
                    "expected_object_bytes": marker_record[
                        "expected_object_bytes"
                    ],
                    "agent_sigstop_at_arm": True,
                    "object_pipeline_before_restart": pipeline_before,
                    "object_pipeline_after_recovery": pipeline_after,
                }
            )
        if publication_cut(args.cut_boundary):
            receipt.update(
                {
                    "marker_sha256": marker_sha256,
                    "publication_target_commitments": (
                        publication_target_commitments(publication)
                    ),
                    "agent_sigstop_at_arm": True,
                    "qualification_scheduler_fence": (
                        publication_scheduler_fence(args.cut_boundary)
                    ),
                    "publication_before_restart": publication_before,
                    "publication_after_recovery": publication_after,
                }
            )
        if receipt["branch_count_per_node"] != [3, 3, 3]:
            raise RuntimeError("power-cut recovery did not restore all branches")
        write_json_durable(args.evidence.resolve(), receipt)
        print(json.dumps(receipt, sort_keys=True), flush=True)
        return 0
    finally:
        for node in reversed(nodes):
            try:
                node.stop()
            except Exception:
                pass
        stop_bootstrap(bootstrap_process, bootstrap_log)
        for volume in reversed(volumes):
            try:
                volume.unmount()
            except Exception as error:
                print(f"warning: unable to unmount {volume.mountpoint}: {error}", file=sys.stderr)


def self_test() -> int:
    prior = {"bytes": 1, "digest": "11" * 32, "directories": 0, "files": 1}
    completed = {
        "bytes": 2,
        "digest": "22" * 32,
        "directories": 0,
        "files": 1,
    }
    if classify_initial([completed, completed, prior], prior, completed) != [
        "completed",
        "completed",
        "prior",
    ]:
        raise RuntimeError("prior recovery classification failed")
    if classify_initial([completed, completed, completed], prior, completed) != [
        "completed",
        "completed",
        "completed",
    ]:
        raise RuntimeError("completed recovery classification failed")
    try:
        classify_initial(
            [completed, completed, {**prior, "digest": "33" * 32}],
            prior,
            completed,
        )
    except RuntimeError:
        pass
    else:
        raise RuntimeError("hybrid recovery classification was accepted")
    stable = WORKSPACE_MAGIC + bytes([1, WORKSPACE_STABLE])
    pending = WORKSPACE_MAGIC + bytes([1, WORKSPACE_PENDING_EXCHANGE])
    if decode_workspace_state_header(stable) != ("stable", WORKSPACE_STABLE):
        raise RuntimeError("stable workspace phase was decoded incorrectly")
    if decode_workspace_state_header(pending) != (
        "pending",
        WORKSPACE_PENDING_EXCHANGE,
    ):
        raise RuntimeError("pending workspace phase was decoded incorrectly")
    if decode_workspace_state_header(WORKSPACE_MAGIC + b"\x01\x7f") != (
        "unrecognized",
        0x7F,
    ):
        raise RuntimeError("unknown workspace phase was accepted")
    if decode_workspace_state_header(WORKSPACE_MAGIC + b"\x02\x01") != (
        "unrecognized",
        None,
    ):
        raise RuntimeError("unknown workspace format was accepted")
    snapshot = {
        "state": "pending",
        "phase": WORKSPACE_PENDING_EXCHANGE,
        "active_manifest": "11" * 32,
        "pending_manifest": "22" * 32,
    }
    with tempfile.TemporaryDirectory(prefix="iotox-power-cut-phase-") as directory:
        marker = Path(directory) / ".iotox-projection"
        marker.write_text(
            "namespace=notes\nmanifest=" + "11" * 32 + "\nmetadata=owner-mode-v2\n"
            "includes=0\nexcludes=0\n",
            encoding="ascii",
        )
        if projection_orientation(marker, "notes", snapshot) != "active":
            raise RuntimeError("active projection marker was decoded incorrectly")
        marker.write_text(
            "namespace=notes\nmanifest=" + "22" * 32 + "\nmetadata=owner-mode-v2\n"
            "includes=0\nexcludes=0\n",
            encoding="ascii",
        )
        if projection_orientation(marker, "notes", snapshot) != "pending":
            raise RuntimeError("pending projection marker was decoded incorrectly")
    publication = {
        "manifest": {
            "name": "11" * 32 + ".manifest",
            "bytes": 1024,
            "sha256": "22" * 32,
        },
        "branch_record": {
            "name": "33" * 32 + ".branch",
            "bytes": 256,
            "sha256": "44" * 32,
        },
        "branch_pointer": {
            "name": "55" * 32 + ".branch",
            "bytes": 256,
            "sha256": "44" * 32,
            "prior_bytes": 256,
            "prior_sha256": "66" * 32,
        },
    }
    validate_publication_targets(publication)
    if not publication_temporary_state_valid(
        {
            "manifest_temporary_count": 1,
            "manifest_temporary_bytes": 1024,
            "branch_record_temporary_count": 0,
            "branch_record_temporary_bytes": 0,
            "branch_pointer_temporary_count": 0,
            "branch_pointer_temporary_bytes": 0,
        },
        "manifest-install-temporary",
        publication,
    ):
        raise RuntimeError("publication temporary prefix was rejected")
    if publication_temporary_state_valid(
        {
            "manifest_temporary_count": 0,
            "manifest_temporary_bytes": 0,
            "branch_record_temporary_count": 1,
            "branch_record_temporary_bytes": 256,
            "branch_pointer_temporary_count": 0,
            "branch_pointer_temporary_bytes": 0,
        },
        "manifest-install-temporary",
        publication,
    ):
        raise RuntimeError("unrelated publication temporary was accepted")
    if expected_publication_prefix("manifest-install-temporary") != {
        "manifest_state": "absent",
        "branch_record_state": "absent",
        "branch_pointer_state": "prior",
    }:
        raise RuntimeError("manifest publication prefix is incorrect")
    for boundary, live, recovered_old, recovered_new in (
        (
            "manifest-install-directory-fsync",
            ("exact", "absent", "prior"),
            ("absent", "absent", "prior"),
            ("exact", "absent", "prior"),
        ),
        (
            "branch-record-install-directory-fsync",
            ("exact", "exact", "prior"),
            ("exact", "absent", "prior"),
            ("exact", "exact", "prior"),
        ),
        (
            "branch-pointer-update-directory-fsync",
            ("exact", "exact", "successor"),
            ("exact", "exact", "prior"),
            ("exact", "exact", "successor"),
        ),
    ):
        keys = ("manifest_state", "branch_record_state", "branch_pointer_state")
        if tuple(expected_publication_prefix(boundary)[key] for key in keys) != live:
            raise RuntimeError(f"{boundary} live prefix is incorrect")
        for recovered in (recovered_old, recovered_new):
            if not publication_recovery_prefix_valid(
                dict(zip(keys, recovered, strict=True)), boundary
            ):
                raise RuntimeError(f"{boundary} recovery prefix was rejected")
        invalid = dict(zip(keys, recovered_old, strict=True))
        invalid["branch_pointer_state"] = "corrupt"
        if publication_recovery_prefix_valid(invalid, boundary):
            raise RuntimeError(f"{boundary} corrupt recovery prefix was accepted")
        if publication_scheduler_fence(boundary) != (
            "strace-path-filtered-fsync-delay-enter+sigstop"
        ):
            raise RuntimeError(f"{boundary} scheduler fence is incorrect")
    try:
        validate_publication_targets(
            {
                **publication,
                "branch_pointer": {
                    **publication["branch_pointer"],
                    "sha256": "77" * 32,
                },
            }
        )
    except RuntimeError:
        pass
    else:
        raise RuntimeError("mismatched publication record/pointer was accepted")
    print("sync-power-cut-rehearsal-self-test=pass")
    return 0


def main() -> int:
    if "--self-test" in sys.argv[1:]:
        return self_test()
    parser = argparse.ArgumentParser()
    parser.add_argument("--iotox", type=Path, required=True)
    parser.add_argument("--bootstrap", type=Path, required=True)
    parser.add_argument("--strace", type=Path)
    parser.add_argument("--three-writer-helper", type=Path, default=THREE_WRITER)
    parser.add_argument("--recovery-helper", type=Path, default=RECOVERY)
    parser.add_argument("--storage-fault-helper", type=Path, default=STORAGE_FAULT)
    parser.add_argument("--state-root", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--arm-receipt", type=Path, required=True)
    parser.add_argument("--namespace", default="power-cut-notes")
    parser.add_argument("--disk-mib", type=int, default=192)
    parser.add_argument("--files", type=int, default=16)
    parser.add_argument("--file-bytes", type=int, default=4096)
    parser.add_argument("--exchange-bytes", type=int, default=32 * 1024 * 1024)
    parser.add_argument(
        "--cut-boundary", choices=sorted(CUT_BOUNDARIES),
        default="pre-exchange-pending"
    )
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()

    if os.geteuid() != 0:
        raise RuntimeError("power-cut rehearsal requires a disposable root VM")
    if not 128 <= args.disk_mib <= 1024:
        raise RuntimeError("disk-mib must be between 128 and 1024")
    if not 1 <= args.files <= 512 or not 1 <= args.file_bytes <= 65536:
        raise RuntimeError("power-cut seed shape is invalid")
    if not 8 * 1024 * 1024 <= args.exchange_bytes <= 64 * 1024 * 1024:
        raise RuntimeError("exchange-bytes must be between 8 and 64 MiB")
    if not 30 <= args.timeout <= 1800:
        raise RuntimeError("timeout must be between 30 and 1800 seconds")
    if publication_cut(args.cut_boundary) and (
        args.strace is None
        or args.strace.is_symlink()
        or not args.strace.resolve().is_file()
    ):
        raise RuntimeError("publication cut requires a regular strace executable")

    tw = load_module(args.three_writer_helper.resolve(), "iotox_three_writer_power_cut")
    recovery = load_module(args.recovery_helper.resolve(), "iotox_recovery_power_cut")
    storage = load_module(args.storage_fault_helper.resolve(), "iotox_storage_power_cut")
    recovery.tw = tw
    binary = args.iotox.resolve()
    bootstrap = args.bootstrap.resolve()
    state_root = args.state_root.resolve()
    marker = state_root / "campaign.state"
    tw.require(binary.is_file(), "IoTox binary is absent")
    tw.require(bootstrap.is_file(), "bootstrap binary is absent")
    if not state_root.exists():
        tw.private_directory(state_root)
    else:
        tw.require(
            state_root.is_dir() and not state_root.is_symlink(),
            "power-cut state root is unsafe",
        )
        state_root.chmod(0o700)
    lock = (state_root / ".qualification.lock").open("a+b")
    os.chmod(lock.fileno(), 0o600)
    fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    try:
        if marker.exists():
            return recover(args, tw, recovery, storage, state_root, marker)
        if any(path.name != ".qualification.lock" for path in state_root.iterdir()):
            raise RuntimeError("unmarked power-cut state root is not empty")
        return initialize(args, tw, recovery, storage, state_root, marker)
    except (OSError, RuntimeError, subprocess.SubprocessError, tw.QualificationError) as error:
        print(f"sync power-cut rehearsal failed: {error}", file=sys.stderr)
        return 1
    finally:
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        lock.close()


if __name__ == "__main__":
    raise SystemExit(main())
