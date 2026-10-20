#!/usr/bin/env python3
"""Run a two-boot Sandwurm VMM-cut synchronization campaign."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile
import time


SHA256 = re.compile(r"^[0-9a-f]{64}$")
WORKSPACE_ARM_SCHEMA = "iotox.sync-power-cut-arm.v3"
OBJECT_ARM_SCHEMA = "iotox.sync-power-cut-arm.v4"
PUBLICATION_ARM_SCHEMA = "iotox.sync-power-cut-arm.v5"
POST_PUBLICATION_ARM_SCHEMA = "iotox.sync-power-cut-arm.v6"
WORKSPACE_CAMPAIGN_SCHEMA = "iotox.sync-power-cut-sandwurm.v3"
OBJECT_CAMPAIGN_SCHEMA = "iotox.sync-power-cut-sandwurm.v4"
PUBLICATION_CAMPAIGN_SCHEMA = "iotox.sync-power-cut-sandwurm.v5"
POST_PUBLICATION_CAMPAIGN_SCHEMA = "iotox.sync-power-cut-sandwurm.v6"
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


class ExactVmmNotReady(RuntimeError):
    """The task-owned VMM has not appeared in the supervised process tree yet."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path, maximum_bytes: int = 4 * 1024 * 1024) -> dict[str, object]:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError(f"required receipt is absent or unsafe: {path}")
    if path.stat().st_size > maximum_bytes:
        raise RuntimeError(f"receipt exceeds byte ceiling: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"receipt is not an object: {path}")
    return value


def write_json_atomic(path: Path, record: dict[str, object]) -> None:
    temporary = path.with_name(path.name + ".tmp")
    encoded = json.dumps(record, indent=2, sort_keys=True) + "\n"
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
        and SHA256.fullmatch(value["digest"]) is not None
    )


def object_cut(boundary: str) -> bool:
    return boundary in OBJECT_CUT_BOUNDARIES


def publication_cut(boundary: str) -> bool:
    return boundary in PUBLICATION_CUT_BOUNDARIES


def pre_publication_cut(boundary: str) -> bool:
    return boundary in PRE_PUBLICATION_CUT_BOUNDARIES


def post_publication_cut(boundary: str) -> bool:
    return boundary in POST_PUBLICATION_CUT_BOUNDARIES


def expected_transition(boundary: str) -> str:
    return {
        "pre-exchange-pending": "pending-workspace",
        "post-exchange-pending": "pending-workspace",
        "receive-staging-partial": "transport-receive-staging",
        "cas-install-temporary": "cas-install",
        "manifest-install-temporary": "manifest-install",
        "branch-record-install-temporary": "branch-record-install",
        "branch-pointer-update-temporary": "branch-pointer-update",
        "manifest-install-directory-fsync": "manifest-install-directory-fsync",
        "branch-record-install-directory-fsync": (
            "branch-record-install-directory-fsync"
        ),
        "branch-pointer-update-directory-fsync": (
            "branch-pointer-update-directory-fsync"
        ),
    }[boundary]


def expected_arm_schema(boundary: str) -> str:
    if post_publication_cut(boundary):
        return POST_PUBLICATION_ARM_SCHEMA
    if publication_cut(boundary):
        return PUBLICATION_ARM_SCHEMA
    return OBJECT_ARM_SCHEMA if object_cut(boundary) else WORKSPACE_ARM_SCHEMA


def publication_commitments_valid(value: object) -> bool:
    if not isinstance(value, dict) or set(value) != {
        "manifest",
        "branch_record",
        "branch_pointer",
    }:
        return False
    for name in ("manifest", "branch_record", "branch_pointer"):
        record = value.get(name)
        fields = {"name_sha256", "bytes", "sha256"}
        if name == "branch_pointer":
            fields |= {"prior_bytes", "prior_sha256"}
        if (
            not isinstance(record, dict)
            or set(record) != fields
            or SHA256.fullmatch(str(record.get("name_sha256", ""))) is None
            or not isinstance(record.get("bytes"), int)
            or not 0 < record["bytes"] <= 4 * 1024 * 1024
            or SHA256.fullmatch(str(record.get("sha256", ""))) is None
        ):
            return False
    pointer = value["branch_pointer"]
    record = value["branch_record"]
    return (
        isinstance(pointer.get("prior_bytes"), int)
        and 0 < pointer["prior_bytes"] <= 4 * 1024 * 1024
        and SHA256.fullmatch(str(pointer.get("prior_sha256", ""))) is not None
        and pointer["prior_sha256"] != pointer["sha256"]
        and record["bytes"] == pointer["bytes"]
        and record["sha256"] == pointer["sha256"]
    )


def validate_arm(record: dict[str, object], expected_boundary: str) -> None:
    required = {
        "schema",
        "status",
        "transition",
        "cut_boundary",
        "projection_orientation",
        "projection_stage_present",
        "workspace_phase_raw",
        "workspace_phase_encoding",
        "marker_sha256",
        "first_boot_id_sha256",
        "prior",
        "completed",
        "contains_secrets",
    }
    if object_cut(expected_boundary):
        required |= {
            "temporary_class",
            "temporary_bytes_at_arm",
            "temporary_mode_at_arm",
            "temporary_link_count_at_arm",
            "temporary_owner_match_at_arm",
            "expected_object_sha256",
            "expected_object_bytes",
            "final_object_present_at_arm",
            "agent_sigstop_at_arm",
        }
    if pre_publication_cut(expected_boundary):
        required |= {
            "temporary_class",
            "temporary_bytes_at_arm",
            "temporary_sha256_at_arm",
            "temporary_mode_at_arm",
            "temporary_link_count_at_arm",
            "temporary_owner_match_at_arm",
            "target_name_sha256",
            "publication_target_commitments",
            "destination_state_at_arm",
            "qualification_scheduler_fence",
            "traced_agent_at_arm",
            "agent_sigstop_at_arm",
        }
    if post_publication_cut(expected_boundary):
        required |= {
            "directory_class",
            "directory_name_sha256",
            "selected_final_bytes_at_arm",
            "selected_final_sha256_at_arm",
            "selected_temporary_absent_at_arm",
            "target_name_sha256",
            "publication_target_commitments",
            "destination_state_at_arm",
            "qualification_scheduler_fence",
            "traced_agent_at_arm",
            "agent_sigstop_at_arm",
        }
    if set(record) != required:
        raise RuntimeError("power-cut arm receipt has an unexpected shape")
    transition = expected_transition(expected_boundary)
    if (
        record.get("schema")
        != expected_arm_schema(expected_boundary)
        or record.get("status") != "armed"
        or record.get("transition") != transition
        or record.get("cut_boundary") != expected_boundary
        or record.get("projection_orientation")
        != (
            "pending" if expected_boundary == "post-exchange-pending" else "active"
        )
        or not isinstance(record.get("projection_stage_present"), bool)
        or record.get("workspace_phase_raw")
        != (
            1
            if object_cut(expected_boundary) or publication_cut(expected_boundary)
            else 2
        )
        or record.get("workspace_phase_encoding") != WORKSPACE_PHASE_ENCODING
        or SHA256.fullmatch(str(record.get("marker_sha256", ""))) is None
        or SHA256.fullmatch(str(record.get("first_boot_id_sha256", ""))) is None
        or not summary_valid(record.get("prior"))
        or not summary_valid(record.get("completed"))
        or record.get("prior") == record.get("completed")
        or record.get("contains_secrets") is not False
    ):
        raise RuntimeError("power-cut arm receipt is invalid")
    if object_cut(expected_boundary) and (
        record.get("temporary_class") != transition
        or not isinstance(record.get("temporary_bytes_at_arm"), int)
        or record["temporary_bytes_at_arm"] <= 0
        or not isinstance(record.get("expected_object_bytes"), int)
        or record["expected_object_bytes"] < 8 * 1024 * 1024
        or record["temporary_bytes_at_arm"] > record["expected_object_bytes"]
        or (
            expected_boundary == "receive-staging-partial"
            and record["temporary_bytes_at_arm"] >= record["expected_object_bytes"]
        )
        or record.get("temporary_mode_at_arm") != "0600"
        or record.get("temporary_link_count_at_arm") != 1
        or record.get("temporary_owner_match_at_arm") is not True
        or SHA256.fullmatch(str(record.get("expected_object_sha256", ""))) is None
        or record.get("final_object_present_at_arm") is not False
        or record.get("agent_sigstop_at_arm") is not True
    ):
        raise RuntimeError("power-cut object arm receipt is invalid")
    if pre_publication_cut(expected_boundary) and (
        record.get("temporary_class") != transition
        or not isinstance(record.get("temporary_bytes_at_arm"), int)
        or not 0 < record["temporary_bytes_at_arm"] <= 4 * 1024 * 1024
        or SHA256.fullmatch(str(record.get("temporary_sha256_at_arm", "")))
        is None
        or record.get("temporary_mode_at_arm") != "0600"
        or record.get("temporary_link_count_at_arm") != 1
        or record.get("temporary_owner_match_at_arm") is not True
        or SHA256.fullmatch(str(record.get("target_name_sha256", ""))) is None
        or not publication_commitments_valid(
            record.get("publication_target_commitments")
        )
        or record["publication_target_commitments"][
            {
                "manifest-install-temporary": "manifest",
                "branch-record-install-temporary": "branch_record",
                "branch-pointer-update-temporary": "branch_pointer",
            }[expected_boundary]
        ]["name_sha256"]
        != record["target_name_sha256"]
        or record["publication_target_commitments"][
            {
                "manifest-install-temporary": "manifest",
                "branch-record-install-temporary": "branch_record",
                "branch-pointer-update-temporary": "branch_pointer",
            }[expected_boundary]
        ]["bytes"]
        != record["temporary_bytes_at_arm"]
        or record["publication_target_commitments"][
            {
                "manifest-install-temporary": "manifest",
                "branch-record-install-temporary": "branch_record",
                "branch-pointer-update-temporary": "branch_pointer",
            }[expected_boundary]
        ]["sha256"]
        != record["temporary_sha256_at_arm"]
        or record.get("destination_state_at_arm")
        != (
            "prior"
            if expected_boundary == "branch-pointer-update-temporary"
            else "absent"
        )
        or record.get("qualification_scheduler_fence")
        != "strace-path-filtered-delay-enter+sigstop"
        or record.get("traced_agent_at_arm") is not True
        or record.get("agent_sigstop_at_arm") is not True
    ):
        raise RuntimeError("power-cut publication arm receipt is invalid")
    if post_publication_cut(expected_boundary):
        selected = {
            "manifest-install-directory-fsync": "manifest",
            "branch-record-install-directory-fsync": "branch_record",
            "branch-pointer-update-directory-fsync": "branch_pointer",
        }[expected_boundary]
        directory = {
            "manifest-install-directory-fsync": "manifests",
            "branch-record-install-directory-fsync": "records",
            "branch-pointer-update-directory-fsync": "branches",
        }[expected_boundary]
        commitments = record.get("publication_target_commitments")
        if (
            not publication_commitments_valid(commitments)
            or record.get("directory_class") != directory
            or record.get("directory_name_sha256")
            != hashlib.sha256(directory.encode("ascii")).hexdigest()
            or not isinstance(record.get("selected_final_bytes_at_arm"), int)
            or record["selected_final_bytes_at_arm"] <= 0
            or record["selected_final_bytes_at_arm"] > 4 * 1024 * 1024
            or SHA256.fullmatch(
                str(record.get("selected_final_sha256_at_arm", ""))
            )
            is None
            or record.get("selected_temporary_absent_at_arm") is not True
            or SHA256.fullmatch(str(record.get("target_name_sha256", ""))) is None
            or commitments[selected]["name_sha256"]
            != record["target_name_sha256"]
            or commitments[selected]["bytes"]
            != record["selected_final_bytes_at_arm"]
            or commitments[selected]["sha256"]
            != record["selected_final_sha256_at_arm"]
            or record.get("destination_state_at_arm")
            != (
                "successor"
                if expected_boundary == "branch-pointer-update-directory-fsync"
                else "exact"
            )
            or record.get("qualification_scheduler_fence")
            != "strace-path-filtered-fsync-delay-enter+sigstop"
            or record.get("traced_agent_at_arm") is not True
            or record.get("agent_sigstop_at_arm") is not True
        ):
            raise RuntimeError("power-cut post-rename arm receipt is invalid")


def process_parent(pid: int) -> int | None:
    try:
        for line in Path(f"/proc/{pid}/status").read_text(
            encoding="ascii", errors="replace"
        ).splitlines():
            if line.startswith("PPid:"):
                return int(line.split()[1])
    except (FileNotFoundError, PermissionError, ValueError):
        return None
    return None


def descendants(root_pid: int) -> set[int]:
    parents: dict[int, int] = {}
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        pid = int(entry.name)
        parent = process_parent(pid)
        if parent is not None:
            parents[pid] = parent
    selected = {root_pid}
    changed = True
    while changed:
        changed = False
        for pid, parent in parents.items():
            if parent in selected and pid not in selected:
                selected.add(pid)
                changed = True
    selected.remove(root_pid)
    return selected


def process_cmdline(pid: int) -> list[str]:
    try:
        content = Path(f"/proc/{pid}/cmdline").read_bytes()
    except (FileNotFoundError, PermissionError):
        return []
    return [
        part.decode("utf-8", errors="surrogateescape")
        for part in content.split(b"\0")
        if part
    ]


def process_starttime(pid: int) -> str:
    text = Path(f"/proc/{pid}/stat").read_text(encoding="ascii")
    close = text.rfind(")")
    if close < 0:
        raise RuntimeError("VMM process stat is malformed")
    fields = text[close + 2 :].split()
    if len(fields) <= 19 or not fields[19].isdigit():
        raise RuntimeError("VMM process start time is unavailable")
    return fields[19]


def find_exact_vmm(chain_pid: int, runtime_root: Path) -> tuple[int, str, str]:
    candidates: list[tuple[int, list[str]]] = []
    expected_disk = f"path={runtime_root},readonly=off"
    for pid in descendants(chain_pid):
        arguments = process_cmdline(pid)
        if not arguments or Path(arguments[0]).name != "cloud-hypervisor":
            continue
        if expected_disk not in arguments:
            continue
        candidates.append((pid, arguments))
    if not candidates:
        raise ExactVmmNotReady("exact task-owned Cloud Hypervisor has not appeared")
    if len(candidates) != 1:
        raise RuntimeError(
            f"expected one exact task-owned Cloud Hypervisor process, found {len(candidates)}"
        )
    pid, arguments = candidates[0]
    starttime = process_starttime(pid)
    command_sha256 = hashlib.sha256(
        b"\0".join(
            argument.encode("utf-8", errors="surrogateescape")
            for argument in arguments
        )
    ).hexdigest()
    return pid, starttime, command_sha256


def runtime_root_from_receipt(receipt: Path, epoch_root: Path) -> Path:
    record = read_json(receipt)
    value = record.get("runtime_root_image")
    if not isinstance(value, str):
        raise RuntimeError("first runtime-root receipt lacks its image")
    candidate = Path(value)
    if candidate.is_symlink() or not candidate.is_file():
        raise RuntimeError("first runtime root image is absent or unsafe")
    runtime_root = candidate.resolve()
    try:
        runtime_root.relative_to(epoch_root)
    except ValueError as error:
        raise RuntimeError("first runtime root escaped its proof root") from error
    return runtime_root


def wait_first_vmm(
    process: subprocess.Popen[bytes],
    runtime_receipt: Path,
    epoch_root: Path,
    timeout: int,
) -> tuple[Path, int, str, str]:
    deadline = time.monotonic() + timeout
    last_transient_error = "runtime-root receipt has not appeared"
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(
                f"first Sandwurm epoch exited {process.returncode} before VMM launch"
            )
        if runtime_receipt.is_file():
            runtime_root = runtime_root_from_receipt(runtime_receipt, epoch_root)
            try:
                pid, starttime, command_sha256 = find_exact_vmm(
                    process.pid, runtime_root
                )
                return runtime_root, pid, starttime, command_sha256
            except ExactVmmNotReady as error:
                # Sandwurm writes the runtime receipt before starting the VMM. A
                # validated receipt with no matching child is therefore a normal,
                # bounded prelaunch state rather than an arm failure.
                last_transient_error = str(error)
        time.sleep(0.1)
    raise RuntimeError(
        "first Sandwurm epoch did not launch its exact VMM before the "
        f"prelaunch timeout ({last_transient_error})"
    )


def base_environment(args: argparse.Namespace, proof_root: Path) -> dict[str, str]:
    environment = os.environ.copy()
    environment.update(
        {
            "PATH": args.host_path,
            "SANDWURM_BIN": str(args.sandwurm_bin),
            "SW_DIRECT_CH_LIVE_CHAIN_PROOF_ROOT": str(proof_root),
            "SW_DIRECT_CH_LIVE_CHAIN_LAUNCH": "1",
            "SW_DIRECT_CH_LIVE_CHAIN_BUILD_ARTIFACTS": "1",
            "SW_DIRECT_CH_LIVE_CHAIN_MATERIALIZE_ROOT": "1",
            "SW_DIRECT_CH_LIVE_CHAIN_REALIZE_TOOLCHAIN": "1",
            "SW_DIRECT_CH_LIVE_CHAIN_TOOLCHAIN_FLAKE_REF": f"path:{args.sandwurm_root}",
            "SW_DIRECT_CH_LIVE_CHAIN_NETWORK_MODE": "none",
            "SW_DIRECT_CH_LIVE_CHAIN_LAUNCH_MEMORY": "size=2G,shared=on",
            "SW_DIRECT_CH_LIVE_CHAIN_LAUNCH_VCPUS": "2",
            "SW_DIRECT_CH_LIVE_CHAIN_GUEST_RECEIPT_TIMEOUT_SECONDS": str(
                args.timeout
            ),
            "SW_DIRECT_CH_PRELAUNCH_RUNNER_AUTHORITY_RECEIPT": "/var/lib/sandwurm-direct-cloud-hypervisor/runner-authority-declaration.json",
            "SW_DIRECT_NIXOS_FLAKE_REF": f"git+file:{args.repo_root}",
            "SW_DIRECT_NIXOS_CONFIG": args.config,
        }
    )
    return environment


def launch_first_epoch(
    args: argparse.Namespace, epoch_root: Path
) -> tuple[subprocess.Popen[bytes], object, object]:
    stdout = (epoch_root.parent / "epoch-1-chain.stdout").open("wb")
    stderr = (epoch_root.parent / "epoch-1-chain.stderr").open("wb")
    process = subprocess.Popen(
        [str(args.host_bash), str(args.live_chain_probe)],
        cwd=args.sandwurm_root,
        env=base_environment(args, epoch_root),
        stdout=stdout,
        stderr=stderr,
        start_new_session=True,
    )
    return process, stdout, stderr


def run_second_epoch(args: argparse.Namespace, epoch_root: Path, crash_image: Path) -> int:
    environment = base_environment(args, epoch_root)
    environment["SW_DIRECT_NIXOS_ROOT_IMAGE_PRESEEDED"] = "1"
    environment["SW_DIRECT_NIXOS_PRESEEDED_ROOT_IMAGE"] = str(crash_image)
    with (epoch_root.parent / "epoch-2-chain.stdout").open("wb") as stdout, (
        epoch_root.parent / "epoch-2-chain.stderr"
    ).open("wb") as stderr:
        result = subprocess.run(
            [str(args.host_bash), str(args.live_chain_probe)],
            cwd=args.sandwurm_root,
            env=environment,
            stdout=stdout,
            stderr=stderr,
            timeout=args.prelaunch_timeout + args.timeout + 300,
            check=False,
        )
    return result.returncode


def receipt_paths(proof_root: Path) -> dict[str, Path]:
    return {
        "arm": proof_root / "epoch-1/live/workspace-export/power-cut/armed.json",
        "epoch_1_chain": proof_root / "epoch-1/direct-cloud-hypervisor-live-chain.json",
        "epoch_1_launch": proof_root / "epoch-1/live/cloud-hypervisor-launch.json",
        "epoch_1_runtime_root": proof_root / "epoch-1/prelaunch/runtime-root/direct-nixos-runtime-root.json",
        "recovery": proof_root / "epoch-2/live/workspace-export/guest-receipts/iotox/sync-power-cut.json",
        "vm_smoke": proof_root / "epoch-2/live/workspace-export/guest-receipts/iotox/vm-smoke.json",
        "epoch_2_chain": proof_root / "epoch-2/direct-cloud-hypervisor-live-chain.json",
        "epoch_2_launch": proof_root / "epoch-2/live/cloud-hypervisor-launch.json",
        "epoch_2_runtime_root": proof_root / "epoch-2/prelaunch/runtime-root/direct-nixos-runtime-root.json",
    }


def self_test() -> int:
    summary = {"bytes": 1, "digest": "11" * 32, "directories": 0, "files": 1}
    successor = {**summary, "bytes": 2, "digest": "22" * 32}
    valid = {
        "schema": WORKSPACE_ARM_SCHEMA,
        "status": "armed",
        "transition": "pending-workspace",
        "cut_boundary": "pre-exchange-pending",
        "projection_orientation": "active",
        "projection_stage_present": False,
        "workspace_phase_raw": 2,
        "workspace_phase_encoding": WORKSPACE_PHASE_ENCODING,
        "marker_sha256": "33" * 32,
        "first_boot_id_sha256": "44" * 32,
        "prior": summary,
        "completed": successor,
        "contains_secrets": False,
    }
    validate_arm(valid, "pre-exchange-pending")
    post = {
        **valid,
        "cut_boundary": "post-exchange-pending",
        "projection_orientation": "pending",
    }
    validate_arm(post, "post-exchange-pending")
    try:
        validate_arm(
            {**post, "projection_orientation": "active"},
            "post-exchange-pending",
        )
    except RuntimeError:
        pass
    else:
        raise RuntimeError("pre-exchange projection armed the post-exchange gate")
    try:
        validate_arm({**valid, "contains_secrets": True}, "pre-exchange-pending")
    except RuntimeError:
        pass
    else:
        raise RuntimeError("secret-bearing arm receipt was accepted")
    try:
        validate_arm({**valid, "workspace_phase_raw": 1}, "pre-exchange-pending")
    except RuntimeError:
        pass
    else:
        raise RuntimeError("stable workspace phase was accepted as a cut arm")
    object_valid = {
        **valid,
        "schema": OBJECT_ARM_SCHEMA,
        "transition": "transport-receive-staging",
        "cut_boundary": "receive-staging-partial",
        "workspace_phase_raw": 1,
        "temporary_class": "transport-receive-staging",
        "temporary_bytes_at_arm": 8 * 1024 * 1024,
        "temporary_mode_at_arm": "0600",
        "temporary_link_count_at_arm": 1,
        "temporary_owner_match_at_arm": True,
        "expected_object_sha256": "55" * 32,
        "expected_object_bytes": 32 * 1024 * 1024,
        "final_object_present_at_arm": False,
        "agent_sigstop_at_arm": True,
    }
    validate_arm(object_valid, "receive-staging-partial")
    cas_valid = {
        **object_valid,
        "transition": "cas-install",
        "cut_boundary": "cas-install-temporary",
        "temporary_class": "cas-install",
        "temporary_bytes_at_arm": 32 * 1024 * 1024,
    }
    validate_arm(cas_valid, "cas-install-temporary")
    publication_valid = {
        **valid,
        "schema": PUBLICATION_ARM_SCHEMA,
        "transition": "manifest-install",
        "cut_boundary": "manifest-install-temporary",
        "workspace_phase_raw": 1,
        "temporary_class": "manifest-install",
        "temporary_bytes_at_arm": 1024,
        "temporary_sha256_at_arm": "88" * 32,
        "temporary_mode_at_arm": "0600",
        "temporary_link_count_at_arm": 1,
        "temporary_owner_match_at_arm": True,
        "target_name_sha256": "99" * 32,
        "publication_target_commitments": {
            "manifest": {
                "name_sha256": "99" * 32,
                "bytes": 1024,
                "sha256": "88" * 32,
            },
            "branch_record": {
                "name_sha256": "aa" * 32,
                "bytes": 1024,
                "sha256": "bb" * 32,
            },
            "branch_pointer": {
                "name_sha256": "cc" * 32,
                "bytes": 1024,
                "sha256": "bb" * 32,
                "prior_bytes": 1024,
                "prior_sha256": "dd" * 32,
            },
        },
        "destination_state_at_arm": "absent",
        "qualification_scheduler_fence": (
            "strace-path-filtered-delay-enter+sigstop"
        ),
        "traced_agent_at_arm": True,
        "agent_sigstop_at_arm": True,
    }
    validate_arm(publication_valid, "manifest-install-temporary")
    validate_arm(
        {
            **publication_valid,
            "transition": "branch-record-install",
            "cut_boundary": "branch-record-install-temporary",
            "temporary_class": "branch-record-install",
            "temporary_sha256_at_arm": "bb" * 32,
            "target_name_sha256": "aa" * 32,
        },
        "branch-record-install-temporary",
    )
    validate_arm(
        {
            **publication_valid,
            "transition": "branch-pointer-update",
            "cut_boundary": "branch-pointer-update-temporary",
            "temporary_class": "branch-pointer-update",
            "temporary_sha256_at_arm": "bb" * 32,
            "target_name_sha256": "cc" * 32,
            "destination_state_at_arm": "prior",
        },
        "branch-pointer-update-temporary",
    )
    post_publication_valid = {
        **valid,
        "schema": POST_PUBLICATION_ARM_SCHEMA,
        "transition": "manifest-install-directory-fsync",
        "cut_boundary": "manifest-install-directory-fsync",
        "workspace_phase_raw": 1,
        "directory_class": "manifests",
        "directory_name_sha256": hashlib.sha256(b"manifests").hexdigest(),
        "selected_final_bytes_at_arm": 1024,
        "selected_final_sha256_at_arm": "88" * 32,
        "selected_temporary_absent_at_arm": True,
        "target_name_sha256": "99" * 32,
        "publication_target_commitments": publication_valid[
            "publication_target_commitments"
        ],
        "destination_state_at_arm": "exact",
        "qualification_scheduler_fence": (
            "strace-path-filtered-fsync-delay-enter+sigstop"
        ),
        "traced_agent_at_arm": True,
        "agent_sigstop_at_arm": True,
    }
    validate_arm(post_publication_valid, "manifest-install-directory-fsync")
    validate_arm(
        {
            **post_publication_valid,
            "transition": "branch-record-install-directory-fsync",
            "cut_boundary": "branch-record-install-directory-fsync",
            "directory_class": "records",
            "directory_name_sha256": hashlib.sha256(b"records").hexdigest(),
            "selected_final_sha256_at_arm": "bb" * 32,
            "target_name_sha256": "aa" * 32,
        },
        "branch-record-install-directory-fsync",
    )
    validate_arm(
        {
            **post_publication_valid,
            "transition": "branch-pointer-update-directory-fsync",
            "cut_boundary": "branch-pointer-update-directory-fsync",
            "directory_class": "branches",
            "directory_name_sha256": hashlib.sha256(b"branches").hexdigest(),
            "selected_final_sha256_at_arm": "bb" * 32,
            "target_name_sha256": "cc" * 32,
            "destination_state_at_arm": "successor",
        },
        "branch-pointer-update-directory-fsync",
    )
    try:
        validate_arm(
            {**object_valid, "final_object_present_at_arm": True},
            "receive-staging-partial",
        )
    except RuntimeError:
        pass
    else:
        raise RuntimeError("digest-named object present at arm was accepted")
    with tempfile.TemporaryDirectory(prefix="iotox-vmm-receipt-selftest.") as name:
        root = Path(name)
        epoch = root / "epoch-1"
        epoch.mkdir()
        runtime_root = epoch / "runtime.raw"
        runtime_root.write_bytes(b"runtime")
        receipt = epoch / "runtime-root.json"
        receipt.write_text(
            json.dumps({"runtime_root_image": str(runtime_root)}) + "\n",
            encoding="utf-8",
        )
        if runtime_root_from_receipt(receipt, epoch) != runtime_root.resolve():
            raise RuntimeError("safe runtime-root receipt did not resolve exactly")

        linked = epoch / "linked.raw"
        linked.symlink_to(runtime_root.name)
        receipt.write_text(
            json.dumps({"runtime_root_image": str(linked)}) + "\n",
            encoding="utf-8",
        )
        try:
            runtime_root_from_receipt(receipt, epoch)
        except RuntimeError:
            pass
        else:
            raise RuntimeError("symlink runtime root was accepted")

        escaped = root / "escaped.raw"
        escaped.write_bytes(b"escaped")
        receipt.write_text(
            json.dumps({"runtime_root_image": str(escaped)}) + "\n",
            encoding="utf-8",
        )
        try:
            runtime_root_from_receipt(receipt, epoch)
        except RuntimeError:
            pass
        else:
            raise RuntimeError("escaped runtime root was accepted")
    print("sync-power-cut-sandwurm-runner-self-test=pass")
    return 0


def main() -> int:
    if "--self-test" in sys.argv[1:]:
        return self_test()
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--sandwurm-root", type=Path, required=True)
    parser.add_argument("--sandwurm-bin", type=Path, required=True)
    parser.add_argument("--host-bash", type=Path, required=True)
    parser.add_argument("--host-path", required=True)
    parser.add_argument("--state-root", type=Path, required=True)
    parser.add_argument("--verifier", type=Path, required=True)
    parser.add_argument("--config", default="iotox-sandwurm-sync-power-cut")
    parser.add_argument(
        "--cut-boundary", choices=sorted(CUT_BOUNDARIES),
        default="pre-exchange-pending"
    )
    parser.add_argument(
        "--prelaunch-timeout",
        type=int,
        default=3600,
        help="seconds allowed for realization, materialization, and exact VMM launch",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=1200,
        help="seconds allowed for the guest to arm after exact VMM launch",
    )
    args = parser.parse_args()
    if not 300 <= args.timeout <= 3600:
        raise RuntimeError("timeout must be between 300 and 3600 seconds")
    if not 300 <= args.prelaunch_timeout <= 7200:
        raise RuntimeError("prelaunch timeout must be between 300 and 7200 seconds")
    args.repo_root = args.repo_root.resolve()
    args.sandwurm_root = args.sandwurm_root.resolve()
    args.sandwurm_bin = args.sandwurm_bin.resolve()
    args.host_bash = args.host_bash.resolve()
    args.live_chain_probe = (
        args.sandwurm_root / "tests/probe-direct-cloud-hypervisor-live-chain.sh"
    )
    args.verifier = args.verifier.resolve()
    for required in (
        args.sandwurm_bin,
        args.host_bash,
        args.live_chain_probe,
        args.verifier,
    ):
        if not required.is_file():
            raise RuntimeError(f"required power-cut input is absent: {required}")
    args.state_root.mkdir(mode=0o700, parents=True, exist_ok=True)
    proof_root = Path(tempfile.mkdtemp(prefix="run.", dir=args.state_root)).resolve()
    proof_root.chmod(0o700)
    print(f"proof-root={proof_root}", flush=True)
    epoch_1 = proof_root / "epoch-1"
    epoch_2 = proof_root / "epoch-2"
    epoch_1.mkdir(mode=0o700)
    epoch_2.mkdir(mode=0o700)
    paths = receipt_paths(proof_root)
    started = time.monotonic()
    first_process, first_stdout, first_stderr = launch_first_epoch(args, epoch_1)
    first_rc: int | None = None
    vmm_pid = 0
    vmm_starttime = ""
    vmm_command_sha256 = ""
    crash_image: Path | None = None
    try:
        crash_image, vmm_pid, vmm_starttime, vmm_command_sha256 = wait_first_vmm(
            first_process,
            paths["epoch_1_runtime_root"],
            epoch_1,
            args.prelaunch_timeout,
        )
        deadline = time.monotonic() + args.timeout
        while time.monotonic() < deadline:
            if paths["arm"].is_file():
                arm = read_json(paths["arm"])
                validate_arm(arm, args.cut_boundary)
                break
            if first_process.poll() is not None:
                raise RuntimeError(
                    f"first Sandwurm epoch exited {first_process.returncode} before arming"
                )
            time.sleep(0.1)
        else:
            raise RuntimeError("first Sandwurm epoch did not arm before timeout")

        current_pid, current_starttime, current_command_sha256 = find_exact_vmm(
            first_process.pid, crash_image
        )
        if (
            current_pid != vmm_pid
            or current_starttime != vmm_starttime
            or current_command_sha256 != vmm_command_sha256
        ):
            raise RuntimeError("exact VMM identity changed between launch and arm")
        os.kill(vmm_pid, signal.SIGKILL)
        first_rc = first_process.wait(timeout=120)
    finally:
        if first_process.poll() is None:
            os.killpg(first_process.pid, signal.SIGTERM)
            try:
                first_process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                os.killpg(first_process.pid, signal.SIGKILL)
                first_process.wait(timeout=30)
        if first_rc is None:
            first_rc = first_process.returncode
        first_stdout.close()
        first_stderr.close()

    if not paths["epoch_1_chain"].is_file():
        raise RuntimeError("first Sandwurm epoch did not retain its chain receipt")
    if crash_image is None:
        raise RuntimeError("first runtime root was not retained")
    second_rc = run_second_epoch(args, epoch_2, crash_image)
    if second_rc != 0:
        raise RuntimeError(f"second Sandwurm epoch exited {second_rc}")
    for name, path in paths.items():
        if not path.is_file():
            raise RuntimeError(f"power-cut receipt is missing after recovery: {name}")

    arm = read_json(paths["arm"])
    recovery = read_json(paths["recovery"])
    vm_smoke = read_json(paths["vm_smoke"])
    second_runtime = read_json(paths["epoch_2_runtime_root"])
    files = {
        str(path.relative_to(proof_root)): {
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in paths.values()
    }
    is_object_cut = object_cut(args.cut_boundary)
    is_publication_cut = publication_cut(args.cut_boundary)
    is_post_publication_cut = post_publication_cut(args.cut_boundary)
    campaign = {
        "schema": (
            POST_PUBLICATION_CAMPAIGN_SCHEMA
            if is_post_publication_cut
            else (
                PUBLICATION_CAMPAIGN_SCHEMA
                if is_publication_cut
                else (
                    OBJECT_CAMPAIGN_SCHEMA
                    if is_object_cut
                    else WORKSPACE_CAMPAIGN_SCHEMA
                )
            )
        ),
        "status": "passed",
        "vm_substrate": "cloud-hypervisor",
        "power_cut_signal": "SIGKILL",
        "power_cut_target": "cloud-hypervisor",
        "power_cut_observed": True,
        "first_epoch_runner_exit": first_rc,
        "first_vmm_pid": vmm_pid,
        "first_vmm_proc_starttime": vmm_starttime,
        "first_vmm_command_sha256": vmm_command_sha256,
        "transition_observed": arm["transition"],
        "cut_boundary_observed": arm["cut_boundary"],
        "projection_orientation_observed": arm["projection_orientation"],
        "projection_stage_present_at_arm": arm["projection_stage_present"],
        "workspace_phase_raw_observed": arm["workspace_phase_raw"],
        "workspace_phase_encoding": arm["workspace_phase_encoding"],
        "first_boot_id_sha256": arm["first_boot_id_sha256"],
        "recovery_boot_id_sha256": recovery.get("recovery_boot_id_sha256"),
        "distinct_boot_observed": recovery.get("distinct_boot_observed"),
        "crash_image_reused_as_preseed": (
            second_runtime.get("source_root_image") == str(crash_image)
        ),
        "recovery_root_copy_method": second_runtime.get("copy_method"),
        "source_revision": vm_smoke.get("source_revision"),
        "product_revision": vm_smoke.get("product_revision"),
        "version": vm_smoke.get("version"),
        "binary_sha256": vm_smoke.get("binary_sha256"),
        "elapsed_ms": int((time.monotonic() - started) * 1000),
        "files": files,
        "contains_secrets": False,
        "dishonest_storage_assessed": False,
    }
    if is_object_cut:
        campaign.update(
            {
                "temporary_class_observed": arm["temporary_class"],
                "temporary_bytes_at_arm": arm["temporary_bytes_at_arm"],
                "temporary_mode_at_arm": arm["temporary_mode_at_arm"],
                "temporary_link_count_at_arm": arm[
                    "temporary_link_count_at_arm"
                ],
                "temporary_owner_match_at_arm": arm[
                    "temporary_owner_match_at_arm"
                ],
                "expected_object_sha256": arm["expected_object_sha256"],
                "expected_object_bytes": arm["expected_object_bytes"],
                "final_object_present_at_arm": arm[
                    "final_object_present_at_arm"
                ],
                "agent_sigstop_at_arm": arm["agent_sigstop_at_arm"],
            }
        )
    if is_publication_cut and not is_post_publication_cut:
        campaign.update(
            {
                "marker_sha256": arm["marker_sha256"],
                "temporary_class_observed": arm["temporary_class"],
                "temporary_bytes_at_arm": arm["temporary_bytes_at_arm"],
                "temporary_sha256_at_arm": arm[
                    "temporary_sha256_at_arm"
                ],
                "temporary_mode_at_arm": arm["temporary_mode_at_arm"],
                "temporary_link_count_at_arm": arm[
                    "temporary_link_count_at_arm"
                ],
                "temporary_owner_match_at_arm": arm[
                    "temporary_owner_match_at_arm"
                ],
                "target_name_sha256": arm["target_name_sha256"],
                "publication_target_commitments": arm[
                    "publication_target_commitments"
                ],
                "destination_state_at_arm": arm[
                    "destination_state_at_arm"
                ],
                "qualification_scheduler_fence": arm[
                    "qualification_scheduler_fence"
                ],
                "traced_agent_at_arm": arm["traced_agent_at_arm"],
                "agent_sigstop_at_arm": arm["agent_sigstop_at_arm"],
            }
        )
    if is_post_publication_cut:
        campaign.update(
            {
                "marker_sha256": arm["marker_sha256"],
                "directory_class_observed": arm["directory_class"],
                "directory_name_sha256": arm["directory_name_sha256"],
                "selected_final_bytes_at_arm": arm[
                    "selected_final_bytes_at_arm"
                ],
                "selected_final_sha256_at_arm": arm[
                    "selected_final_sha256_at_arm"
                ],
                "selected_temporary_absent_at_arm": arm[
                    "selected_temporary_absent_at_arm"
                ],
                "target_name_sha256": arm["target_name_sha256"],
                "publication_target_commitments": arm[
                    "publication_target_commitments"
                ],
                "destination_state_at_arm": arm["destination_state_at_arm"],
                "qualification_scheduler_fence": arm[
                    "qualification_scheduler_fence"
                ],
                "traced_agent_at_arm": arm["traced_agent_at_arm"],
                "agent_sigstop_at_arm": arm["agent_sigstop_at_arm"],
            }
        )
    write_json_atomic(proof_root / "campaign.json", campaign)
    result = subprocess.run(
        [sys.executable, str(args.verifier), str(proof_root)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"power-cut verifier rejected campaign: {(result.stderr or result.stdout).strip()}"
        )
    print(result.stdout, end="", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"sync power-cut Sandwurm campaign failed: {error}", file=sys.stderr)
        raise SystemExit(1)
