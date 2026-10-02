#!/usr/bin/env python3
"""Strictly verify one Sandwurm projection-descriptor qualification proof."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import stat
import sys
import tempfile


CHAIN = "direct-cloud-hypervisor-live-chain.json"
PRELAUNCH = "prelaunch/launch/cloud-hypervisor-launch.json"
LIVE = "live/cloud-hypervisor-launch.json"
VM_SMOKE = "live/workspace-export/guest-receipts/iotox/vm-smoke.json"
RECEIPT = "live/workspace-export/guest-receipts/iotox/sync-projection-descriptor.json"
EVIDENCE = (CHAIN, PRELAUNCH, LIVE, VM_SMOKE, RECEIPT)
COMPACT = "compact-export.json"
SCHEMA = "iotox.sync-projection-descriptor.v1"
MAX_JSON_BYTES = 512 * 1024


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def strict_object(pairs: list[tuple[str, object]]) -> dict:
    value: dict[str, object] = {}
    for key, item in pairs:
        require(key not in value, f"duplicate JSON key: {key}")
        value[key] = item
    return value


def load(root: Path, relative: str) -> dict:
    path = root / relative
    require(path.resolve(strict=True).is_relative_to(root),
            f"evidence escapes proof root: {relative}")
    metadata = path.lstat()
    require(stat.S_ISREG(metadata.st_mode) and not path.is_symlink(),
            f"evidence is absent or unsafe: {relative}")
    require(0 < metadata.st_size <= MAX_JSON_BYTES,
            f"evidence size is invalid: {relative}")
    encoded = path.read_bytes()
    require(len(encoded) == metadata.st_size, f"evidence changed: {relative}")
    value = json.loads(encoded.decode("utf-8"), object_pairs_hook=strict_object)
    require(isinstance(value, dict), f"evidence root is not an object: {relative}")
    return value


def is_sha256(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def integral(value: object, minimum: int = 0, maximum: int = 2**63 - 1) -> bool:
    return type(value) is int and minimum <= value <= maximum


def validate_state(value: object, label: str) -> None:
    require(
        isinstance(value, dict)
        and set(value) == {
            "stage_orientation", "stage_present", "visible_orientation", "workspace"
        }
        and value.get("stage_present") is True
        and value.get("visible_orientation") == "pending"
        and value.get("stage_orientation") == "active",
        f"{label} projection state is invalid",
    )
    workspace = value.get("workspace")
    require(
        isinstance(workspace, dict)
        and set(workspace) == {"active_manifest", "pending_manifest", "phase", "state"}
        and workspace.get("state") == "pending"
        and workspace.get("phase") == 2
        and is_sha256(workspace.get("active_manifest"))
        and is_sha256(workspace.get("pending_manifest"))
        and workspace["active_manifest"] != workspace["pending_manifest"],
        f"{label} workspace state is invalid",
    )


COMMON_CELL_FIELDS = {
    "baseline_sha256", "boundary", "cell", "descriptor_stage_identity_equal",
    "elapsed_ms", "exchange_count", "external_helper_fd", "external_helper_pid",
    "first_mutation_sha256", "first_write_fsync", "flag", "held_bytes",
    "held_device", "held_inode", "path_binding", "phase", "repair_refusal",
    "raw_exchange_line_count", "retained_sha256", "retained_state",
    "split_exchange_observed", "strace_delay", "strace_injection", "syscall",
    "trace_sha256", "trace_tid",
}


SELECTED_FIELDS = COMMON_CELL_FIELDS | {
    "controlled_stop_exit", "final_converged_nodes", "final_repair_verified_nodes",
    "final_sha256", "salvage_reapplied", "salvage_sha256",
}


UNSELECTED_FIELDS = COMMON_CELL_FIELDS | {
    "busy_remount_classification", "busy_remount_exit_nonzero", "cold_start_control_socket_exposed",
    "cold_start_exit", "cold_start_log_sha256", "cold_start_refused",
    "cold_start_retained_sha256", "controlled_stop_exit",
    "descriptor_unchanged_after_busy_remount", "final_converged_nodes",
    "final_repair_verified_nodes", "final_sha256", "helper_closed_before_successful_remount",
    "identity_preserved", "read_only_remount_succeeded", "read_write_remount_succeeded",
    "salvage_reapplied_as", "salvage_sha256", "second_helper",
    "second_mutation_sha256", "stage_inode_preserved_across_remount",
}


def validate_cell(cell: object, selected: bool) -> None:
    name = "pre-exchange-selected" if selected else "post-exchange-unselected"
    phase = "entry" if selected else "exit"
    fields = SELECTED_FIELDS if selected else UNSELECTED_FIELDS
    require(isinstance(cell, dict) and set(cell) == fields,
            f"{name} field set is invalid")
    require(
        cell.get("cell") == name
        and cell.get("phase") == phase
        and cell.get("syscall") == "renameat2"
        and cell.get("flag") == "RENAME_EXCHANGE"
        and cell.get("path_binding") == "exact-visible-and-stage"
        and cell.get("strace_delay") == "5s"
        and cell.get("strace_injection")
        == f"--inject=renameat2:delay_{'enter' if selected else 'exit'}=5s"
        and cell.get("exchange_count") == 1
        and integral(cell.get("raw_exchange_line_count"), 1)
        and cell.get("raw_exchange_line_count") >= cell.get("exchange_count")
        and isinstance(cell.get("split_exchange_observed"), bool)
        and cell.get("descriptor_stage_identity_equal") is True
        and cell.get("first_write_fsync") is True
        and cell.get("held_bytes") == 64
        and all(integral(cell.get(key), 1) for key in (
            "elapsed_ms", "external_helper_pid", "external_helper_fd",
            "held_device", "held_inode", "trace_tid",
        ))
        and all(is_sha256(cell.get(key)) for key in (
            "baseline_sha256", "first_mutation_sha256", "retained_sha256",
            "trace_sha256",
        ))
        and cell["baseline_sha256"] != cell["first_mutation_sha256"]
        and cell["retained_sha256"] == cell["first_mutation_sha256"],
        f"{name} syscall/descriptor evidence is invalid",
    )
    boundary = cell.get("boundary")
    require(isinstance(boundary, dict), f"{name} boundary is absent")
    expected_orientations = ("active", "pending") if selected else ("pending", "active")
    require(
        set(boundary) == {
            "stage_orientation", "stage_present", "visible_orientation", "workspace"
        }
        and boundary.get("stage_present") is True
        and (boundary.get("visible_orientation"), boundary.get("stage_orientation"))
        == expected_orientations,
        f"{name} boundary orientation is invalid",
    )
    boundary_workspace = boundary.get("workspace")
    require(
        isinstance(boundary_workspace, dict)
        and boundary_workspace.get("state") == "pending"
        and boundary_workspace.get("phase") == 2
        and is_sha256(boundary_workspace.get("active_manifest"))
        and is_sha256(boundary_workspace.get("pending_manifest")),
        f"{name} boundary workspace is invalid",
    )
    validate_state(cell.get("retained_state"), name)
    refusal = cell.get("repair_refusal")
    classification = (
        "exchanged old projection changed" if selected
        else "preserved unselected projection changed"
    )
    require(
        isinstance(refusal, dict)
        and set(refusal) == {"classification", "error", "exit"}
        and refusal.get("exit") == 4
        and refusal.get("error") == "protocol-error"
        and refusal.get("classification") == classification,
        f"{name} refusal is invalid",
    )
    require(
        cell.get("controlled_stop_exit") == 0
        and cell.get("final_converged_nodes") == 3
        and cell.get("final_repair_verified_nodes") == 3
        and is_sha256(cell.get("salvage_sha256"))
        and is_sha256(cell.get("final_sha256")),
        f"{name} recovery evidence is invalid",
    )
    if selected:
        require(
            cell.get("salvage_reapplied") is True
            and cell["salvage_sha256"] == cell["first_mutation_sha256"]
            and cell["final_sha256"] == cell["first_mutation_sha256"],
            "selected salvage evidence is invalid",
        )
        return
    second = cell.get("second_helper")
    require(
        cell.get("busy_remount_exit_nonzero") is True
        and cell.get("busy_remount_classification") == "mount-point-busy"
        and cell.get("descriptor_unchanged_after_busy_remount") is True
        and cell.get("helper_closed_before_successful_remount") is True
        and cell.get("read_only_remount_succeeded") is True
        and cell.get("read_write_remount_succeeded") is True
        and cell.get("stage_inode_preserved_across_remount") is True
        and isinstance(second, dict)
        and set(second) == {"device", "fd", "inode", "pid"}
        and all(integral(second.get(key), 1) for key in second)
        and second.get("device") == cell.get("held_device")
        and second.get("inode") == cell.get("held_inode")
        and is_sha256(cell.get("second_mutation_sha256"))
        and cell["second_mutation_sha256"] != cell["first_mutation_sha256"]
        and cell.get("cold_start_refused") is True
        and cell.get("cold_start_exit") == 3
        and is_sha256(cell.get("cold_start_log_sha256"))
        and cell.get("cold_start_control_socket_exposed") is False
        and cell.get("identity_preserved") is True
        and cell.get("salvage_reapplied_as") == "recovered/held.bin"
        and cell.get("cold_start_retained_sha256") == cell["second_mutation_sha256"]
        and cell.get("salvage_sha256") == cell["second_mutation_sha256"]
        and cell.get("final_sha256") == cell["second_mutation_sha256"],
        "unselected remount/startup/salvage evidence is invalid",
    )


TOP_FIELDS = {
    "binary_sha256", "cell_count", "cells", "contains_secrets",
    "directed_read_write_share_count_per_cell", "elapsed_ms", "filesystem",
    "network_class", "node_count_per_cell", "product_test_seam", "ptrace_controller",
    "salvage_is_automatic_merge", "same_fd_across_ro_rw_remount",
    "same_fd_remount_nonclaim_reason", "schema", "status", "version",
    "virtualization_required",
}


def validate_receipt(receipt: dict) -> None:
    require(set(receipt) == TOP_FIELDS, "descriptor receipt field set is invalid")
    require(
        receipt.get("schema") == SCHEMA
        and receipt.get("status") == "passed"
        and receipt.get("version") == "IoTox 0.51.0 rev0051"
        and is_sha256(receipt.get("binary_sha256"))
        and receipt.get("network_class") == "loopback-only-inside-networkless-vm"
        and receipt.get("virtualization_required") == "kvm"
        and receipt.get("filesystem") == "ext4"
        and receipt.get("node_count_per_cell") == 3
        and receipt.get("directed_read_write_share_count_per_cell") == 6
        and receipt.get("cell_count") == 2
        and receipt.get("ptrace_controller") == "external-strace"
        and receipt.get("product_test_seam") is False
        and receipt.get("same_fd_across_ro_rw_remount") is False
        and receipt.get("same_fd_remount_nonclaim_reason")
        == "ext4-refuses-ro-remount-busy"
        and receipt.get("salvage_is_automatic_merge") is False
        and integral(receipt.get("elapsed_ms"), 1)
        and receipt.get("contains_secrets") is False,
        "descriptor receipt substrate/nonclaims are invalid",
    )
    cells = receipt.get("cells")
    require(isinstance(cells, list) and len(cells) == 2,
            "descriptor receipt does not have two cells")
    validate_cell(cells[0], True)
    validate_cell(cells[1], False)


def require_networkless_launch(launch: dict) -> None:
    if launch.get("schema") == "iotox.sync-projection-descriptor-launch-summary.v1":
        require(
            launch.get("status") in {"planned", "exited"}
            and launch.get("network_class") == "none"
            and launch.get("network_mode") == "none"
            and launch.get("network_device_present") is False,
            "compact launch summary is not networkless",
        )
        return
    network = launch.get("network")
    require(
        isinstance(network, dict)
        and network.get("class") == "none"
        and network.get("mode") == "none",
        "descriptor qualification was not networkless",
    )
    vmm = launch.get("vmm")
    require(isinstance(vmm, dict), "VMM launch evidence is absent")
    argv = vmm.get("argv", [])
    require(
        isinstance(argv, list)
        and not any(
            isinstance(argument, str)
            and (argument == "--net" or argument.startswith("--net="))
            for argument in argv
        ),
        "networkless launch contains a network device",
    )


def verify(proof_root: Path) -> dict:
    require(proof_root.is_dir() and not proof_root.is_symlink(),
            "proof root is absent or unsafe")
    root = proof_root.resolve(strict=True)
    chain = load(root, CHAIN)
    prelaunch = load(root, PRELAUNCH)
    live = load(root, LIVE)
    vm = load(root, VM_SMOKE)
    receipt = load(root, RECEIPT)
    if chain.get("schema") == "iotox.sync-projection-descriptor-chain-summary.v1":
        require(
            chain.get("status") == "guest-evidence-observed"
            and chain.get("prelaunch_chain_status") == "ready"
            and chain.get("live_launch_status") == "exited"
            and chain.get("guest_evidence_observed") is True
            and chain.get("contains_secrets") is False,
            "compact chain summary is invalid",
        )
    else:
        require(
            chain.get("schema") == "sandwurm.direct-cloud-hypervisor-live-chain.v0"
            and chain.get("status") == "guest-evidence-observed"
            and chain.get("failure") is None
            and chain.get("guest_evidence", {}).get("observed") is True,
            "Sandwurm chain did not retain successful guest evidence",
        )
    require_networkless_launch(prelaunch)
    require_networkless_launch(live)
    if live.get("schema") == "iotox.sync-projection-descriptor-launch-summary.v1":
        require(
            live.get("status") == "exited"
            and live.get("vm_substrate") == "cloud-hypervisor"
            and live.get("guest_boundary_observed") is True
            and live.get("process_observed") is True
            and live.get("exit_observed") is True
            and live.get("exit_status") == 0
            and live.get("exit_control_observed") is True,
            "compact live VMM lifecycle summary is invalid",
        )
    else:
        require(
            live.get("status") == "exited"
            and live.get("failure") is None
            and live.get("guest_boundary", {}).get("observed") is True
            and live.get("guest_boundary", {}).get("vm_substrate") == "cloud-hypervisor"
            and live.get("vmm", {}).get("process_observed") is True
            and live.get("vmm", {}).get("exit_observed") is True
            and live.get("vmm", {}).get("exit_status") == 0
            and live.get("ch_remote", {}).get("exit_control_observed") is True,
            "live VMM lifecycle is invalid",
        )
    require(
        vm.get("schema") == "iotox.sandwurm-vm-smoke.v0"
        and vm.get("status") == "passed"
        and vm.get("role") == "device"
        and vm.get("virtualization") == "kvm"
        and vm.get("network_class") == "none"
        and vm.get("package_variant") == "pinned-source-linked"
        and vm.get("product_revision") == "rev0051"
        and vm.get("version") == "IoTox 0.51.0 rev0051"
        and vm.get("cgroup_type") == "cgroup2fs"
        and vm.get("contains_secrets") is False
        and re.fullmatch(r"[0-9a-f]{40}", vm.get("source_revision", "")) is not None
        and is_sha256(vm.get("binary_sha256")),
        "VM source/binary evidence is invalid",
    )
    validate_receipt(receipt)
    require(receipt["version"] == vm["version"]
            and receipt["binary_sha256"] == vm["binary_sha256"],
            "receipt does not bind the VM product binary")
    compact_path = root / COMPACT
    if compact_path.exists() or compact_path.is_symlink():
        compact = load(root, COMPACT)
        require(
            set(compact) == {
                "contains_secrets", "file_count", "files", "schema",
                "source_proof_root_sha256", "status", "total_bytes",
            }
            and compact.get("schema")
            == "iotox.sync-projection-descriptor-sandwurm-compact-export.v1"
            and compact.get("status") == "passed"
            and compact.get("contains_secrets") is False
            and is_sha256(compact.get("source_proof_root_sha256"))
            and compact.get("file_count") == len(EVIDENCE)
            and integral(compact.get("total_bytes"), 1, MAX_JSON_BYTES * len(EVIDENCE))
            and isinstance(compact.get("files"), list)
            and len(compact["files"]) == len(EVIDENCE),
            "compact projection-descriptor manifest is invalid",
        )
        require(
            [entry.get("path") for entry in compact["files"] if isinstance(entry, dict)]
            == list(EVIDENCE),
            "compact projection-descriptor file order is invalid",
        )
        total = 0
        for entry in compact["files"]:
            require(
                isinstance(entry, dict)
                and set(entry) == {"bytes", "path", "sha256"}
                and integral(entry.get("bytes"), 1, MAX_JSON_BYTES)
                and is_sha256(entry.get("sha256")),
                "compact projection-descriptor file record is invalid",
            )
            path = root / entry["path"]
            require(
                path.resolve(strict=True).is_relative_to(root)
                and path.is_file()
                and not path.is_symlink()
                and path.stat().st_size == entry["bytes"]
                and hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"],
                "compact projection-descriptor digest mismatch",
            )
            total += entry["bytes"]
        require(total == compact["total_bytes"],
                "compact projection-descriptor byte total mismatch")
    return {
        "schema": "iotox.sync-projection-descriptor-verification.v1",
        "status": "passed",
        "source_revision": vm["source_revision"],
        "binary_sha256": vm["binary_sha256"],
        "cell_count": 2,
        "contains_secrets": False,
    }


def fixture_receipt() -> dict:
    digest = lambda label: hashlib.sha256(label.encode("ascii")).hexdigest()
    workspace = {
        "state": "pending", "phase": 2,
        "active_manifest": digest("active"), "pending_manifest": digest("pending"),
    }
    def base(name: str, phase: str) -> dict:
        selected = phase == "entry"
        first = digest(name + "-first")
        return {
            "cell": name, "phase": phase, "syscall": "renameat2",
            "flag": "RENAME_EXCHANGE", "path_binding": "exact-visible-and-stage",
            "strace_injection":
                f"--inject=renameat2:delay_{'enter' if selected else 'exit'}=5s",
            "strace_delay": "5s", "trace_tid": 7, "external_helper_pid": 8,
            "external_helper_fd": 3, "held_device": 11, "held_inode": 12,
            "held_bytes": 64, "baseline_sha256": digest(name + "-base"),
            "first_mutation_sha256": first, "retained_sha256": first,
            "descriptor_stage_identity_equal": True, "first_write_fsync": True,
            "boundary": {
                "workspace": copy.deepcopy(workspace), "stage_present": True,
                "visible_orientation": "active" if selected else "pending",
                "stage_orientation": "pending" if selected else "active",
            },
            "retained_state": {
                "workspace": copy.deepcopy(workspace), "stage_present": True,
                "visible_orientation": "pending", "stage_orientation": "active",
            },
            "repair_refusal": {
                "exit": 4, "error": "protocol-error",
                "classification": "exchanged old projection changed" if selected
                else "preserved unselected projection changed",
            },
            "exchange_count": 1, "trace_sha256": digest(name + "-trace"),
            "raw_exchange_line_count": 1,
            "split_exchange_observed": False,
            "controlled_stop_exit": 0, "salvage_sha256": first,
            "final_sha256": first, "final_converged_nodes": 3,
            "final_repair_verified_nodes": 3, "elapsed_ms": 100,
        }
    selected = base("pre-exchange-selected", "entry")
    selected["salvage_reapplied"] = True
    unselected = base("post-exchange-unselected", "exit")
    second = digest("second")
    unselected.update({
        "busy_remount_exit_nonzero": True,
        "busy_remount_classification": "mount-point-busy",
        "descriptor_unchanged_after_busy_remount": True,
        "helper_closed_before_successful_remount": True,
        "read_only_remount_succeeded": True, "read_write_remount_succeeded": True,
        "stage_inode_preserved_across_remount": True,
        "second_helper": {"pid": 9, "fd": 3, "device": 11, "inode": 12},
        "second_mutation_sha256": second, "cold_start_refused": True,
        "cold_start_exit": 3, "cold_start_log_sha256": digest("startup"),
        "cold_start_control_socket_exposed": False,
        "cold_start_retained_sha256": second, "identity_preserved": True,
        "salvage_sha256": second, "salvage_reapplied_as": "recovered/held.bin",
        "final_sha256": second,
    })
    return {
        "schema": SCHEMA, "status": "passed", "version": "IoTox 0.51.0 rev0051",
        "binary_sha256": digest("binary"),
        "network_class": "loopback-only-inside-networkless-vm",
        "virtualization_required": "kvm", "filesystem": "ext4",
        "node_count_per_cell": 3, "directed_read_write_share_count_per_cell": 6,
        "cell_count": 2, "cells": [selected, unselected],
        "ptrace_controller": "external-strace", "product_test_seam": False,
        "same_fd_across_ro_rw_remount": False,
        "same_fd_remount_nonclaim_reason": "ext4-refuses-ro-remount-busy",
        "salvage_is_automatic_merge": False, "elapsed_ms": 200,
        "contains_secrets": False,
    }


def self_test() -> None:
    receipt = fixture_receipt()
    validate_receipt(receipt)
    rejected = copy.deepcopy(receipt)
    rejected["cells"][1]["busy_remount_exit_nonzero"] = False
    try:
        validate_receipt(rejected)
    except ValueError:
        pass
    else:
        raise ValueError("verifier accepted a false busy-remount claim")
    rejected = copy.deepcopy(receipt)
    rejected["cells"][0]["phase"] = "exit"
    try:
        validate_receipt(rejected)
    except ValueError:
        pass
    else:
        raise ValueError("verifier accepted the wrong syscall phase")
    with tempfile.TemporaryDirectory(prefix="iotox-projection-verify-") as raw:
        root = Path(raw)
        fixture(root)
        summary = verify(root)
        require(summary["status"] == "passed", "raw fixture did not verify")
    print("sync-projection-descriptor-sandwurm-verifier-self-test=pass")


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")


def fixture(root: Path) -> dict:
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    receipt = fixture_receipt()
    vm = {
        "schema": "iotox.sandwurm-vm-smoke.v0",
        "status": "passed",
        "role": "device",
        "source_revision": "a" * 40,
        "product_revision": "rev0051",
        "version": receipt["version"],
        "binary_sha256": receipt["binary_sha256"],
        "virtualization": "kvm",
        "cgroup_type": "cgroup2fs",
        "network_class": "none",
        "package_variant": "pinned-source-linked",
        "contains_secrets": False,
    }
    launch_common = {
        "status": "exited",
        "failure": None,
        "network": {"class": "none", "mode": "none"},
        "vmm": {
            "argv": ["cloud-hypervisor", "--console", "file=/tmp/console.log"],
            "process_observed": True,
            "exit_observed": True,
            "exit_status": 0,
        },
        "guest_boundary": {
            "observed": True,
            "vm_substrate": "cloud-hypervisor",
        },
        "ch_remote": {"exit_control_observed": True},
    }
    prelaunch = copy.deepcopy(launch_common)
    prelaunch["status"] = "planned"
    live = copy.deepcopy(launch_common)
    chain = {
        "schema": "sandwurm.direct-cloud-hypervisor-live-chain.v0",
        "status": "guest-evidence-observed",
        "failure": None,
        "receipts": {
            "prelaunch_chain": {"status": "ready"},
            "live_launch": {"status": "exited"},
        },
        "guest_evidence": {"observed": True},
    }
    write(root / CHAIN, chain)
    write(root / PRELAUNCH, prelaunch)
    write(root / LIVE, live)
    write(root / VM_SMOKE, vm)
    write(root / RECEIPT, receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("proof_root", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    require(args.proof_root is not None, "proof root is required")
    print(json.dumps(verify(args.proof_root), sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, json.JSONDecodeError) as error:
        print(f"sync projection descriptor verification failed: {error}", file=sys.stderr)
        raise SystemExit(1)
