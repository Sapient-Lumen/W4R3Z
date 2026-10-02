#!/usr/bin/env python3
"""Strictly verify one content-free Sandwurm metadata-corruption proof."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tempfile


CHAIN = "direct-cloud-hypervisor-live-chain.json"
PRELAUNCH = "prelaunch/launch/cloud-hypervisor-launch.json"
LIVE = "live/cloud-hypervisor-launch.json"
VM_SMOKE = "live/workspace-export/guest-receipts/iotox/vm-smoke.json"
RECEIPT = "live/workspace-export/guest-receipts/iotox/sync-metadata-corruption.json"
COMPACT = "compact-export.json"
MAX_JSON_BYTES = 2 * 1024 * 1024
EVIDENCE = (CHAIN, PRELAUNCH, LIVE, VM_SMOKE, RECEIPT)
FAMILIES_V1 = (
    "branch-pointer",
    "immutable-branch-record",
    "manifest",
    "workspace",
    "maintenance",
)
FAMILIES_V2 = (
    "branch-pointer",
    "manifest",
    "immutable-branch-record",
    "workspace",
    "maintenance",
)
RECEIPT_V1 = "iotox.sync-metadata-corruption.v1"
RECEIPT_V2 = "iotox.sync-metadata-corruption.v2"
EXPECTED_IDENTITIES = {
    RECEIPT_V1: ("IoTox 0.50.0 rev0050", "rev0050"),
    RECEIPT_V2: ("IoTox 0.51.0 rev0051", "rev0051"),
}
FAMILIES_BY_RECEIPT = {
    RECEIPT_V1: FAMILIES_V1,
    RECEIPT_V2: FAMILIES_V2,
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def strict_object(pairs: list[tuple[str, object]]) -> dict:
    value: dict[str, object] = {}
    for key, item in pairs:
        require(key not in value, f"duplicate JSON key: {key}")
        value[key] = item
    return value


def load(root: Path, relative: str, maximum_bytes: int = MAX_JSON_BYTES) -> dict:
    path = root / relative
    require(path.resolve(strict=True).is_relative_to(root),
            f"receipt escapes proof root: {relative}")
    metadata = path.lstat()
    require(
        stat.S_ISREG(metadata.st_mode) and not path.is_symlink(),
        f"receipt is absent or unsafe: {relative}",
    )
    require(0 < metadata.st_size <= maximum_bytes,
            f"receipt size is invalid: {relative}")
    encoded = path.read_bytes()
    require(len(encoded) == metadata.st_size,
            f"receipt changed while reading: {relative}")
    value = json.loads(encoded.decode("utf-8"), object_pairs_hook=strict_object)
    require(isinstance(value, dict), f"JSON root is not an object: {relative}")
    return value


def is_sha256(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def validate_simultaneous(
    simultaneous: object,
    sequential: list[dict[str, object]],
    expected_families: tuple[str, ...],
) -> None:
    require(isinstance(simultaneous, dict), "simultaneous evidence is absent")
    require(
        set(simultaneous) == {
            "all_original_bytes_retained_after_recovery",
            "controlled_shutdown_exit",
            "exact_restoration_verified", "families", "family_count",
            "final_restored_family", "final_startup_succeeded",
            "identity_preserved", "initial_startup_all_corrupt_bytes_retained",
            "initial_startup_exit", "initial_startup_family",
            "initial_startup_log_sha256", "initial_startup_refused",
            "live_all_corrupt_bytes_retained", "live_repair_error",
            "live_repair_exit", "live_repair_family", "live_repair_refused",
            "mutation", "mutation_fence", "restoration", "restoration_steps",
            "stopped_agent_tasks",
            "worktree_preserved",
        },
        "simultaneous evidence field set is invalid",
    )
    records = simultaneous.get("families")
    require(
        type(simultaneous.get("family_count")) is int
        and simultaneous["family_count"] == len(expected_families)
        and isinstance(records, list)
        and [entry.get("family") for entry in records
             if isinstance(entry, dict)] == list(expected_families),
        "simultaneous family set is incomplete or unordered",
    )
    for expected, entry, prior in zip(
        expected_families, records, sequential, strict=True
    ):
        require(
            isinstance(entry, dict)
            and set(entry) == {
                "bytes", "corrupt_sha256", "family", "original_sha256"
            }
            and entry.get("family") == expected
            and type(entry.get("bytes")) is int
            and 1 <= entry["bytes"] <= 1024 * 1024
            and is_sha256(entry.get("original_sha256"))
            and is_sha256(entry.get("corrupt_sha256"))
            and entry["original_sha256"] != entry["corrupt_sha256"]
            and entry["bytes"] == prior["bytes"]
            and entry["original_sha256"] == prior["original_sha256"]
            and entry["corrupt_sha256"] == prior["corrupt_sha256"],
            f"simultaneous {expected} record is invalid",
        )
    require(
        simultaneous.get("mutation")
        == "all-five-last-byte-xor-01-before-agent-resume"
        and simultaneous.get("mutation_fence")
        == "agent-process-group-sigstop-all-tasks"
        and type(simultaneous.get("stopped_agent_tasks")) is int
        and 1 <= simultaneous["stopped_agent_tasks"] <= 4096
        and type(simultaneous.get("controlled_shutdown_exit")) is int
        and simultaneous["controlled_shutdown_exit"] == 0
        and simultaneous.get("live_repair_refused") is True
        and type(simultaneous.get("live_repair_exit")) is int
        and simultaneous["live_repair_exit"] == 4
        and simultaneous.get("live_repair_error") == "protocol-error"
        and simultaneous.get("live_repair_family") == expected_families[0]
        and simultaneous.get("live_all_corrupt_bytes_retained") is True
        and simultaneous.get("initial_startup_refused") is True
        and type(simultaneous.get("initial_startup_exit")) is int
        and simultaneous["initial_startup_exit"] == 3
        and simultaneous.get("initial_startup_family") == expected_families[0]
        and is_sha256(simultaneous.get("initial_startup_log_sha256"))
        and simultaneous.get("initial_startup_all_corrupt_bytes_retained")
        is True,
        "simultaneous initial refusal evidence is invalid",
    )
    steps = simultaneous.get("restoration_steps")
    require(
        isinstance(steps, list) and len(steps) == len(expected_families) - 1,
        "simultaneous restoration steps are incomplete",
    )
    for index, step in enumerate(steps):
        require(
            isinstance(step, dict)
            and set(step) == {
                "next_refused_family", "remaining_corrupt_bytes_retained",
                "restored_family", "restored_prefix_retained",
                "startup_exit", "startup_log_sha256",
            }
            and step.get("restored_family") == expected_families[index]
            and step.get("next_refused_family") == expected_families[index + 1]
            and type(step.get("startup_exit")) is int
            and step["startup_exit"] == 3
            and is_sha256(step.get("startup_log_sha256"))
            and step.get("restored_prefix_retained") is True
            and step.get("remaining_corrupt_bytes_retained") is True,
            f"simultaneous restoration step {index} is invalid",
        )
    require(
        simultaneous.get("final_restored_family") == expected_families[-1]
        and simultaneous.get("final_startup_succeeded") is True
        and simultaneous.get("all_original_bytes_retained_after_recovery")
        is True
        and simultaneous.get("identity_preserved") is True
        and simultaneous.get("worktree_preserved") is True
        and simultaneous.get("exact_restoration_verified") is True
        and simultaneous.get("restoration")
        == "ordered-exact-originals-in-place-fsync-file-and-parent",
        "simultaneous final restoration evidence is invalid",
    )


def require_networkless_launch(launch: dict) -> None:
    require(
        launch.get("schema") == "sandwurm.cloud-hypervisor-launch.v0"
        and isinstance(launch.get("network"), dict)
        and launch["network"].get("class") == "none"
        and launch["network"].get("mode") == "none",
        "metadata corruption qualification was not networkless",
    )
    vmm = launch.get("vmm")
    require(isinstance(vmm, dict), "metadata corruption VMM evidence is absent")
    argv = vmm.get("argv", [])
    require(
        isinstance(argv, list)
        and not any(
            isinstance(argument, str)
            and (argument == "--net" or argument.startswith("--net="))
            for argument in argv
        ),
        "networkless launch contains a VMM network device",
    )


def verify(proof_root: Path) -> dict:
    require(
        proof_root.is_dir() and not proof_root.is_symlink(),
        "proof root is absent or unsafe",
    )
    proof_root = proof_root.resolve(strict=True)
    chain = load(proof_root, CHAIN)
    prelaunch = load(proof_root, PRELAUNCH)
    live = load(proof_root, LIVE)
    vm = load(proof_root, VM_SMOKE, 256 * 1024)
    receipt = load(proof_root, RECEIPT, 256 * 1024)
    receipt_schema = receipt.get("schema")
    require(receipt_schema in EXPECTED_IDENTITIES,
            "metadata corruption receipt schema is unsupported")
    expected_version, expected_product_revision = EXPECTED_IDENTITIES[
        receipt_schema
    ]
    expected_families = FAMILIES_BY_RECEIPT[receipt_schema]
    compact_mode = (proof_root / COMPACT).exists() or (
        proof_root / COMPACT
    ).is_symlink()
    if compact_mode:
        require(
            set(chain) == {
                "contains_secrets", "guest_evidence_observed",
                "live_launch_status", "prelaunch_chain_status", "schema",
                "status",
            }
            and chain.get("schema")
            == "iotox.sync-metadata-corruption-chain-summary.v1"
            and chain.get("status") == "guest-evidence-observed"
            and chain.get("prelaunch_chain_status") == "ready"
            and chain.get("live_launch_status") == "exited"
            and chain.get("guest_evidence_observed") is True
            and chain.get("contains_secrets") is False,
            "compact Sandwurm chain summary is invalid",
        )
        require(
            set(prelaunch) == {
                "contains_secrets", "network_class", "network_device_present",
                "network_mode", "schema", "status",
            }
            and prelaunch.get("schema")
            == "iotox.sync-metadata-corruption-launch-summary.v1"
            and prelaunch.get("status") == "planned"
            and prelaunch.get("network_class") == "none"
            and prelaunch.get("network_mode") == "none"
            and prelaunch.get("network_device_present") is False
            and prelaunch.get("contains_secrets") is False,
            "compact prelaunch summary is invalid",
        )
        require(
            set(live) == {
                "contains_secrets", "exit_control_observed", "exit_observed",
                "exit_status", "guest_boundary_observed", "network_class",
                "network_device_present", "network_mode",
                "process_observed", "schema", "status", "vm_substrate",
            }
            and live.get("schema")
            == "iotox.sync-metadata-corruption-launch-summary.v1"
            and live.get("status") == "exited"
            and live.get("network_class") == "none"
            and live.get("network_mode") == "none"
            and live.get("network_device_present") is False
            and live.get("vm_substrate") == "cloud-hypervisor"
            and live.get("guest_boundary_observed") is True
            and live.get("process_observed") is True
            and live.get("exit_observed") is True
            and live.get("exit_status") == 0
            and live.get("exit_control_observed") is True
            and live.get("contains_secrets") is False,
            "compact live-launch summary is invalid",
        )
    else:
        require(
            set(chain) == {
                "failure", "guest_evidence", "logical_delegation",
                "m6_handoff_gate", "next_runtime_threshold", "nix_handoff",
                "observed_at", "proof_root", "provider_proof",
                "provider_work_summary", "receipts", "requested",
                "safe_default_no_launch", "schema", "self_build_handoff",
                "status", "toolchain",
            },
            "Sandwurm chain field set is invalid",
        )
        require(
            chain.get("schema")
            == "sandwurm.direct-cloud-hypervisor-live-chain.v0"
            and chain.get("status") == "guest-evidence-observed"
            and chain.get("failure") is None
            and chain.get("receipts", {})
            .get("prelaunch_chain", {})
            .get("status")
            == "ready"
            and chain.get("receipts", {}).get("live_launch", {}).get("status")
            == "exited"
            and chain.get("guest_evidence", {}).get("observed") is True,
            "Sandwurm chain did not retain successful guest evidence",
        )
        require(
            set(prelaunch) == {
                "ch_remote", "direct_nixos_artifact_realizer",
                "direct_nixos_runtime_root", "failure", "guest_boundary",
                "network", "nix_handoff", "observed_at", "receipts",
                "recursive_depth_projection", "runtime_inputs", "schema",
                "status", "task_id", "virtiofsd", "vmm",
                "workspace_handoff",
            }
            and prelaunch.get("status") == "planned"
            and prelaunch.get("failure") is None,
            "prelaunch receipt is invalid",
        )
        require(
            set(live) == {
                "ch_remote", "delegation_plan_host_inputs",
                "direct_nixos_artifact_realizer", "direct_nixos_runtime_root",
                "failure", "guest_boundary", "guest_filesystem_space",
                "guest_receipts", "network", "nix_handoff",
                "nix_handoff_developer_host_postcheck",
                "nix_handoff_host_inputs", "observed_at",
                "provider_bundle_host_inputs", "provider_proof",
                "provider_work_file_manifest", "provider_work_live_state",
                "provider_work_summary", "receipts",
                "recursive_depth_host_inputs", "recursive_depth_projection",
                "runtime_inputs", "schema", "self_build_host_inputs",
                "signed_cache_handoff", "signed_cache_host_inputs", "status",
                "task_id", "virtiofsd", "vmm", "workspace_handoff",
            },
            "live launch field set is invalid",
        )
        require_networkless_launch(prelaunch)
        require_networkless_launch(live)
        require(
            live.get("status") == "exited"
            and live.get("failure") is None
            and live.get("guest_boundary", {}).get("observed") is True
            and live.get("guest_boundary", {}).get("vm_substrate")
            == "cloud-hypervisor",
            "live VMM boundary is invalid",
        )
        require(
            live["vmm"].get("process_observed") is True
            and live["vmm"].get("exit_observed") is True
            and live["vmm"].get("exit_status") == 0
            and type(live["vmm"].get("pid")) is int
            and live["vmm"]["pid"] > 0
            and isinstance(live["vmm"].get("proc_starttime"), str)
            and live["vmm"]["proc_starttime"].isdigit()
            and isinstance(live.get("ch_remote"), dict)
            and live["ch_remote"].get("exit_control_observed") is True,
            "live VMM process lifecycle is invalid",
        )
    require(
        set(vm) == {
            "binary_sha256", "cgroup_type", "contains_secrets",
            "network_class", "package_variant", "product_revision", "role",
            "schema", "source_revision", "status", "version",
            "virtualization",
        },
        "VM evidence field set is invalid",
    )
    require(
        vm.get("schema") == "iotox.sandwurm-vm-smoke.v0"
        and vm.get("status") == "passed"
        and vm.get("role") == "device"
        and vm.get("virtualization") == "kvm"
        and vm.get("network_class") == "none"
        and vm.get("package_variant") == "pinned-source-linked"
        and vm.get("product_revision") == expected_product_revision
        and vm.get("version") == expected_version
        and vm.get("cgroup_type") == "cgroup2fs"
        and vm.get("contains_secrets") is False
        and re.fullmatch(r"[0-9a-f]{40}", vm.get("source_revision", ""))
        is not None
        and is_sha256(vm.get("binary_sha256")),
        "VM source/binary evidence is invalid",
    )
    receipt_fields = {
            "automatic_signed_metadata_quarantine", "binary_sha256",
            "contains_secrets", "directed_read_write_share_count",
            "dishonest_storage_assessed", "elapsed_ms", "families",
            "family_count", "filesystem", "final_branch_count",
            "final_bytes", "final_directories", "final_files",
            "final_repair_verified_nodes", "final_tree_sha256",
            "identity_preserved", "network_class", "node_count",
            "operator_supplied_exact_restoration", "power_cut", "schema",
            "status", "version",
    }
    if receipt_schema == RECEIPT_V2:
        receipt_fields.add("simultaneous")
    require(
        receipt_schema in {RECEIPT_V1, RECEIPT_V2}
        and set(receipt) == receipt_fields,
        "metadata corruption receipt field set is invalid",
    )
    require(
        receipt.get("status") == "passed"
        and receipt.get("version") == vm.get("version")
        and receipt.get("binary_sha256") == vm.get("binary_sha256")
        and receipt.get("filesystem") == "ext4"
        and receipt.get("network_class")
        == "loopback-only-inside-networkless-vm"
        and type(receipt.get("node_count")) is int
        and receipt["node_count"] == 3
        and type(receipt.get("directed_read_write_share_count")) is int
        and receipt["directed_read_write_share_count"] == 6,
        "metadata corruption substrate is invalid",
    )
    families = receipt.get("families")
    require(
        type(receipt.get("family_count")) is int
        and receipt["family_count"] == len(expected_families)
        and isinstance(families, list)
        and all(isinstance(entry, dict) for entry in families)
        and [entry.get("family") for entry in families]
        == list(expected_families),
        "metadata corruption family set is incomplete or unordered",
    )
    for expected, entry in zip(expected_families, families, strict=True):
        require(isinstance(entry, dict), f"{expected} receipt is not an object")
        family_fields = {
                "bytes", "corrupt_sha256", "exact_restoration_verified",
                "family", "live_corrupt_bytes_retained",
                "live_repair_error", "live_repair_exit",
                "live_repair_refused", "mutation", "original_sha256",
                "restoration", "startup_family_classified",
                "startup_corrupt_bytes_retained", "startup_exit",
                "startup_log_sha256", "startup_refused",
        }
        if receipt_schema == RECEIPT_V2:
            family_fields.add("controlled_shutdown_exit")
        require(
            set(entry) == family_fields
            and entry.get("family") == expected
            and type(entry.get("bytes")) is int
            and 1 <= entry["bytes"] <= 1024 * 1024
            and is_sha256(entry.get("original_sha256"))
            and is_sha256(entry.get("corrupt_sha256"))
            and entry["original_sha256"] != entry["corrupt_sha256"]
            and entry.get("mutation") == "last-byte-xor-01"
            and entry.get("live_repair_refused") is True
            and type(entry.get("live_repair_exit")) is int
            and entry["live_repair_exit"] == 4
            and entry.get("live_repair_error") == "protocol-error"
            and entry.get("live_corrupt_bytes_retained") is True
            and entry.get("startup_refused") is True
            and type(entry.get("startup_exit")) is int
            and entry["startup_exit"] == 3
            and is_sha256(entry.get("startup_log_sha256"))
            and entry.get("startup_family_classified") is True
            and entry.get("startup_corrupt_bytes_retained") is True
            and (
                receipt_schema == RECEIPT_V1
                or (
                    type(entry.get("controlled_shutdown_exit")) is int
                    and entry["controlled_shutdown_exit"] == 0
                )
            )
            and entry.get("exact_restoration_verified") is True
            and entry.get("restoration")
            == "exact-original-in-place-fsync-file-and-parent",
            f"{expected} corruption/restoration evidence is invalid",
        )
    if receipt_schema == RECEIPT_V2:
        validate_simultaneous(
            receipt.get("simultaneous"), families, expected_families
        )
    require(
        receipt.get("identity_preserved") is True
        and isinstance(receipt.get("final_branch_count"), list)
        and len(receipt["final_branch_count"]) == 3
        and all(type(value) is int for value in receipt["final_branch_count"])
        and receipt["final_branch_count"] == [3, 3, 3]
        and type(receipt.get("final_files")) is int
        and receipt["final_files"] == 5
        and type(receipt.get("final_directories")) is int
        and receipt.get("final_directories") == 1
        and type(receipt.get("final_bytes")) is int
        and receipt["final_bytes"] == 16411
        and is_sha256(receipt.get("final_tree_sha256"))
        and type(receipt.get("final_repair_verified_nodes")) is int
        and receipt["final_repair_verified_nodes"] == 3
        and type(receipt.get("elapsed_ms")) is int
        and receipt["elapsed_ms"] > 0,
        "metadata corruption completion evidence is invalid",
    )
    require(
        receipt.get("automatic_signed_metadata_quarantine") is False
        and receipt.get("operator_supplied_exact_restoration") is True
        and receipt.get("power_cut") is False
        and receipt.get("dishonest_storage_assessed") is False
        and receipt.get("contains_secrets") is False,
        "metadata corruption nonclaims are invalid",
    )
    compact_path = proof_root / COMPACT
    if compact_path.exists() or compact_path.is_symlink():
        compact = load(proof_root, COMPACT, 256 * 1024)
        require(
            set(compact) == {
                "contains_secrets", "file_count", "files", "schema",
                "source_proof_root_sha256", "status", "total_bytes",
            }
            and compact.get("schema")
            == "iotox.sync-metadata-corruption-sandwurm-compact-export.v1"
            and compact.get("status") == "passed"
            and compact.get("contains_secrets") is False
            and is_sha256(compact.get("source_proof_root_sha256"))
            and compact.get("file_count") == len(EVIDENCE)
            and isinstance(compact.get("total_bytes"), int)
            and 0 < compact["total_bytes"] <= MAX_JSON_BYTES
            and isinstance(compact.get("files"), list)
            and len(compact["files"]) == len(EVIDENCE),
            "compact metadata-corruption manifest is invalid",
        )
        records = compact["files"]
        require(
            [entry.get("path") for entry in records if isinstance(entry, dict)]
            == list(EVIDENCE),
            "compact metadata-corruption file order is invalid",
        )
        total_bytes = 0
        for entry in records:
            require(
                isinstance(entry, dict)
                and set(entry) == {"bytes", "path", "sha256"}
                and isinstance(entry.get("bytes"), int)
                and entry["bytes"] > 0
                and is_sha256(entry.get("sha256")),
                "compact metadata-corruption file record is invalid",
            )
            path = proof_root / entry["path"]
            require(
                path.resolve(strict=True).is_relative_to(proof_root)
                and path.is_file()
                and not path.is_symlink()
                and path.stat().st_size == entry["bytes"]
                and hashlib.sha256(path.read_bytes()).hexdigest()
                == entry["sha256"],
                "compact metadata-corruption digest mismatch",
            )
            total_bytes += entry["bytes"]
        require(total_bytes == compact["total_bytes"],
                "compact metadata-corruption byte total is invalid")
        expected_files = set(EVIDENCE) | {COMPACT}
        expected_directories = {
            str(parent)
            for relative in expected_files
            for parent in Path(relative).parents
            if str(parent) != "."
        }
        actual_files: set[str] = set()
        actual_directories: set[str] = set()
        for path in proof_root.rglob("*"):
            relative = str(path.relative_to(proof_root))
            require(not path.is_symlink(),
                    "compact metadata-corruption proof contains a symlink")
            if path.is_file():
                actual_files.add(relative)
            elif path.is_dir():
                actual_directories.add(relative)
            else:
                raise ValueError(
                    "compact metadata-corruption proof contains a special file"
                )
        require(actual_files == expected_files,
                "compact metadata-corruption proof has an unexpected file")
        require(
            actual_directories == expected_directories,
            "compact metadata-corruption proof has an unexpected directory",
        )
    return {
        "schema": "iotox.sync-metadata-corruption-sandwurm-verification.v1",
        "status": "passed",
        "proof_root": str(proof_root),
        "source_revision": vm["source_revision"],
        "binary_sha256": vm["binary_sha256"],
        "receipt_schema": receipt_schema,
        "simultaneous_receipt_verified": receipt_schema == RECEIPT_V2,
        "families": list(expected_families),
        "final_tree_sha256": receipt["final_tree_sha256"],
        "contains_secrets": False,
    }


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value) + "\n", encoding="utf-8")


def fixture(root: Path, receipt_schema: str = RECEIPT_V2) -> dict:
    require(receipt_schema in EXPECTED_IDENTITIES,
            "fixture receipt schema is unsupported")
    families = FAMILIES_BY_RECEIPT[receipt_schema]
    chain_fields = {
        "failure", "guest_evidence", "logical_delegation",
        "m6_handoff_gate", "next_runtime_threshold", "nix_handoff",
        "observed_at", "proof_root", "provider_proof",
        "provider_work_summary", "receipts", "requested",
        "safe_default_no_launch", "schema", "self_build_handoff",
        "status", "toolchain",
    }
    prelaunch_fields = {
        "ch_remote", "direct_nixos_artifact_realizer",
        "direct_nixos_runtime_root", "failure", "guest_boundary",
        "network", "nix_handoff", "observed_at", "receipts",
        "recursive_depth_projection", "runtime_inputs", "schema",
        "status", "task_id", "virtiofsd", "vmm", "workspace_handoff",
    }
    live_fields = {
        "ch_remote", "delegation_plan_host_inputs",
        "direct_nixos_artifact_realizer", "direct_nixos_runtime_root",
        "failure", "guest_boundary", "guest_filesystem_space",
        "guest_receipts", "network", "nix_handoff",
        "nix_handoff_developer_host_postcheck", "nix_handoff_host_inputs",
        "observed_at", "provider_bundle_host_inputs", "provider_proof",
        "provider_work_file_manifest", "provider_work_live_state",
        "provider_work_summary", "receipts", "recursive_depth_host_inputs",
        "recursive_depth_projection", "runtime_inputs",
        "self_build_host_inputs", "signed_cache_handoff",
        "signed_cache_host_inputs", "status", "task_id", "virtiofsd", "vmm",
        "workspace_handoff",
    }
    launch = {
        **{field: None for field in prelaunch_fields},
        "schema": "sandwurm.cloud-hypervisor-launch.v0",
        "status": "planned",
        "failure": None,
        "network": {"class": "none", "mode": "none"},
        "vmm": {"argv": ["cloud-hypervisor", "--cpus", "boot=2,max=2"]},
    }
    write(
        root / CHAIN,
        {
            **{field: None for field in chain_fields},
            "schema": "sandwurm.direct-cloud-hypervisor-live-chain.v0",
            "status": "guest-evidence-observed",
            "failure": None,
            "receipts": {
                "prelaunch_chain": {"status": "ready"},
                "live_launch": {"status": "exited"},
            },
            "guest_evidence": {"observed": True},
        },
    )
    write(root / PRELAUNCH, launch)
    write(
        root / LIVE,
        {
            **{field: None for field in live_fields},
            "schema": "sandwurm.cloud-hypervisor-launch.v0",
            "status": "exited",
            "failure": None,
            "network": {"class": "none", "mode": "none"},
            "vmm": {
                "argv": ["cloud-hypervisor", "--cpus", "boot=2,max=2"],
                "process_observed": True,
                "exit_observed": True,
                "exit_status": 0,
                "pid": 42,
                "proc_starttime": "1234",
            },
            "ch_remote": {"exit_control_observed": True},
            "guest_boundary": {
                "observed": True,
                "vm_substrate": "cloud-hypervisor",
            },
        },
    )
    version, product_revision = EXPECTED_IDENTITIES[receipt_schema]
    binary = "ab" * 32
    write(
        root / VM_SMOKE,
        {
            "schema": "iotox.sandwurm-vm-smoke.v0",
            "status": "passed",
            "role": "device",
            "source_revision": "12" * 20,
            "product_revision": product_revision,
            "version": version,
            "binary_sha256": binary,
            "virtualization": "kvm",
            "cgroup_type": "cgroup2fs",
            "network_class": "none",
            "package_variant": "pinned-source-linked",
            "contains_secrets": False,
        },
    )
    sequential = [
        {
            "family": family,
            "bytes": 256,
            "original_sha256": hashlib.sha256(f"old:{family}".encode()).hexdigest(),
            "corrupt_sha256": hashlib.sha256(f"new:{family}".encode()).hexdigest(),
            "mutation": "last-byte-xor-01",
            "live_repair_refused": True,
            "live_repair_exit": 4,
            "live_repair_error": "protocol-error",
            "live_corrupt_bytes_retained": True,
            "startup_refused": True,
            "startup_exit": 3,
            "startup_log_sha256": hashlib.sha256(family.encode()).hexdigest(),
            "startup_family_classified": True,
            "startup_corrupt_bytes_retained": True,
            "exact_restoration_verified": True,
            "restoration":
                "exact-original-in-place-fsync-file-and-parent",
        }
        for family in families
    ]
    if receipt_schema == RECEIPT_V2:
        for entry in sequential:
            entry["controlled_shutdown_exit"] = 0
    simultaneous = {
        "family_count": len(families),
        "families": [
            {
                "family": entry["family"],
                "bytes": entry["bytes"],
                "original_sha256": entry["original_sha256"],
                "corrupt_sha256": entry["corrupt_sha256"],
            }
            for entry in sequential
        ],
        "mutation": "all-five-last-byte-xor-01-before-agent-resume",
        "mutation_fence": "agent-process-group-sigstop-all-tasks",
        "stopped_agent_tasks": 4,
        "controlled_shutdown_exit": 0,
        "live_repair_refused": True,
        "live_repair_exit": 4,
        "live_repair_error": "protocol-error",
        "live_repair_family": families[0],
        "live_all_corrupt_bytes_retained": True,
        "initial_startup_refused": True,
        "initial_startup_exit": 3,
        "initial_startup_family": families[0],
        "initial_startup_log_sha256": hashlib.sha256(b"all").hexdigest(),
        "initial_startup_all_corrupt_bytes_retained": True,
        "restoration_steps": [
            {
                "restored_family": families[index],
                "next_refused_family": families[index + 1],
                "startup_exit": 3,
                "startup_log_sha256": hashlib.sha256(
                    f"step:{index}".encode()
                ).hexdigest(),
                "restored_prefix_retained": True,
                "remaining_corrupt_bytes_retained": True,
            }
            for index in range(len(families) - 1)
        ],
        "final_restored_family": families[-1],
        "final_startup_succeeded": True,
        "all_original_bytes_retained_after_recovery": True,
        "identity_preserved": True,
        "worktree_preserved": True,
        "exact_restoration_verified": True,
        "restoration":
            "ordered-exact-originals-in-place-fsync-file-and-parent",
    }
    receipt = {
        "schema": receipt_schema,
        "status": "passed",
        "version": version,
        "binary_sha256": binary,
        "filesystem": "ext4",
        "network_class": "loopback-only-inside-networkless-vm",
        "node_count": 3,
        "directed_read_write_share_count": 6,
        "family_count": 5,
        "families": sequential,
        "identity_preserved": True,
        "final_branch_count": [3, 3, 3],
        "final_files": 5,
        "final_directories": 1,
        "final_bytes": 16411,
        "final_tree_sha256": "cd" * 32,
        "final_repair_verified_nodes": 3,
        "elapsed_ms": 1000,
        "automatic_signed_metadata_quarantine": False,
        "operator_supplied_exact_restoration": True,
        "power_cut": False,
        "dishonest_storage_assessed": False,
        "contains_secrets": False,
    }
    if receipt_schema == RECEIPT_V2:
        receipt["simultaneous"] = simultaneous
    write(root / RECEIPT, receipt)
    return receipt


def self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="iotox-metadata-corruption-verify-") as raw:
        root = Path(raw)
        receipt = fixture(root)
        summary = verify(root)
        require(
            summary["status"] == "passed"
            and summary["receipt_schema"] == RECEIPT_V2
            and summary["simultaneous_receipt_verified"] is True,
            "valid v2 fixture failed",
        )
        receipt["automatic_signed_metadata_quarantine"] = True
        write(root / RECEIPT, receipt)
        try:
            verify(root)
        except ValueError:
            pass
        else:
            raise ValueError("automatic signed-metadata quarantine overclaim passed")
        receipt["automatic_signed_metadata_quarantine"] = False
        receipt["families"] = receipt["families"][:-1]
        write(root / RECEIPT, receipt)
        try:
            verify(root)
        except ValueError:
            pass
        else:
            raise ValueError("incomplete metadata family set passed")
        receipt = fixture(root)
        receipt["families"][2] = None
        write(root / RECEIPT, receipt)
        try:
            verify(root)
        except ValueError:
            pass
        else:
            raise ValueError("non-object metadata family passed")
        receipt = fixture(root)
        receipt["simultaneous"]["restoration_steps"][1][
            "next_refused_family"
        ] = FAMILIES_V2[-1]
        write(root / RECEIPT, receipt)
        try:
            verify(root)
        except ValueError:
            pass
        else:
            raise ValueError("misordered simultaneous restoration passed")
        receipt = fixture(root)
        receipt["family_count"] = float(len(FAMILIES_V2))
        write(root / RECEIPT, receipt)
        try:
            verify(root)
        except ValueError:
            pass
        else:
            raise ValueError("floating-point sequential family count passed")
        for field in (
            "node_count",
            "directed_read_write_share_count",
            "final_files",
            "final_bytes",
            "final_repair_verified_nodes",
        ):
            receipt = fixture(root)
            receipt[field] = float(receipt[field])
            write(root / RECEIPT, receipt)
            try:
                verify(root)
            except ValueError:
                pass
            else:
                raise ValueError(f"floating-point {field} passed")
        receipt = fixture(root)
        receipt["final_branch_count"][1] = 3.0
        write(root / RECEIPT, receipt)
        try:
            verify(root)
        except ValueError:
            pass
        else:
            raise ValueError("floating-point final branch count passed")
        receipt = fixture(root)
        receipt["simultaneous"]["family_count"] = float(len(FAMILIES_V2))
        write(root / RECEIPT, receipt)
        try:
            verify(root)
        except ValueError:
            pass
        else:
            raise ValueError("floating-point simultaneous family count passed")
        receipt = fixture(root)
        receipt["simultaneous"]["live_repair_exit"] = 4.0
        write(root / RECEIPT, receipt)
        try:
            verify(root)
        except ValueError:
            pass
        else:
            raise ValueError("floating-point simultaneous exit passed")
        receipt = fixture(root, RECEIPT_V1)
        write(root / RECEIPT, receipt)
        summary = verify(root)
        require(
            summary["status"] == "passed"
            and summary["receipt_schema"] == RECEIPT_V1
            and summary["simultaneous_receipt_verified"] is False,
            "accepted v1 proof compatibility failed",
        )
        receipt = fixture(root)
        receipt["unexpected"] = "secret"
        write(root / RECEIPT, receipt)
        try:
            verify(root)
        except ValueError:
            pass
        else:
            raise ValueError("unexpected receipt field passed")
    print("sync-metadata-corruption-sandwurm-verifier-self-test=pass")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("proof_root", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    require(args.proof_root is not None, "proof root is required")
    print(json.dumps(verify(args.proof_root), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
