#!/usr/bin/env python3
"""Verify one content-free two-boot Sandwurm synchronization power-cut proof."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile


SHA256 = re.compile(r"^[0-9a-f]{64}$")
SOURCE_REVISION = re.compile(r"^(?:[0-9a-f]{40,64}|uncommitted)$")
EXPECTED_FILES = {
    "epoch-1/live/workspace-export/power-cut/armed.json",
    "epoch-1/direct-cloud-hypervisor-live-chain.json",
    "epoch-1/live/cloud-hypervisor-launch.json",
    "epoch-1/prelaunch/runtime-root/direct-nixos-runtime-root.json",
    "epoch-2/live/workspace-export/guest-receipts/iotox/sync-power-cut.json",
    "epoch-2/live/workspace-export/guest-receipts/iotox/vm-smoke.json",
    "epoch-2/direct-cloud-hypervisor-live-chain.json",
    "epoch-2/live/cloud-hypervisor-launch.json",
    "epoch-2/prelaunch/runtime-root/direct-nixos-runtime-root.json",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def load(root: Path, relative: str, maximum_bytes: int = 4 * 1024 * 1024) -> dict:
    path = root / relative
    require(path.resolve().is_relative_to(root), f"receipt escapes proof root: {relative}")
    require(path.is_file() and not path.is_symlink(), f"receipt is absent or unsafe: {relative}")
    require(path.stat().st_size <= maximum_bytes, f"receipt is oversized: {relative}")
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"receipt is not an object: {relative}")
    return value


def is_sha256(value: object) -> bool:
    return isinstance(value, str) and SHA256.fullmatch(value) is not None


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
        and is_sha256(value.get("digest"))
    )


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
            or not is_sha256(record.get("name_sha256"))
            or not isinstance(record.get("bytes"), int)
            or not 0 < record["bytes"] <= 4 * 1024 * 1024
            or not is_sha256(record.get("sha256"))
        ):
            return False
    pointer = value["branch_pointer"]
    record = value["branch_record"]
    return (
        isinstance(pointer.get("prior_bytes"), int)
        and 0 < pointer["prior_bytes"] <= 4 * 1024 * 1024
        and is_sha256(pointer.get("prior_sha256"))
        and pointer["prior_sha256"] != pointer["sha256"]
        and record["bytes"] == pointer["bytes"]
        and record["sha256"] == pointer["sha256"]
    )


def networkless_launch(launch: dict, *, cut: bool) -> None:
    require(
        launch.get("schema") == "sandwurm.cloud-hypervisor-launch.v0"
        and launch.get("status") == "exited",
        "Sandwurm launch receipt is not terminal",
    )
    network = launch.get("network")
    require(
        isinstance(network, dict)
        and network.get("class") == "none"
        and network.get("mode") == "none",
        "power-cut VM was not networkless",
    )
    vmm = launch.get("vmm")
    require(
        isinstance(vmm, dict)
        and vmm.get("process_observed") is True
        and vmm.get("exit_observed") is True
        and isinstance(vmm.get("pid"), int)
        and vmm["pid"] > 0
        and isinstance(vmm.get("proc_starttime"), str)
        and vmm["proc_starttime"].isdigit()
        and isinstance(vmm.get("argv"), list)
        and all(isinstance(argument, str) for argument in vmm["argv"]),
        "power-cut VMM process evidence is invalid",
    )
    require(
        not any(
            argument == "--net" or argument.startswith("--net=")
            for argument in vmm["argv"]
        ),
        "networkless power-cut launch contains a network device",
    )
    control = launch.get("ch_remote")
    require(isinstance(control, dict), "VMM control evidence is absent")
    if cut:
        require(
            isinstance(vmm.get("exit_status"), int)
            and vmm["exit_status"] != 0
            and control.get("exit_control_observed") is False,
            "first VMM exited cooperatively instead of through the power cut",
        )
    else:
        require(
            vmm.get("exit_status") == 0
            and control.get("exit_control_observed") is True,
            "recovery VMM did not exit through normal Sandwurm control",
        )


def verify(root: Path) -> dict[str, object]:
    root = root.resolve()
    campaign = load(root, "campaign.json", 256 * 1024)
    campaign_schema = campaign.get("schema")
    require(
        campaign_schema
        in {
            "iotox.sync-power-cut-sandwurm.v2",
            "iotox.sync-power-cut-sandwurm.v3",
            "iotox.sync-power-cut-sandwurm.v4",
            "iotox.sync-power-cut-sandwurm.v5",
            "iotox.sync-power-cut-sandwurm.v6",
        },
        "power-cut campaign schema is unsupported",
    )
    proof_version = int(str(campaign_schema).rsplit("v", 1)[1])
    require(
        campaign.get("status") == "passed"
        and campaign.get("vm_substrate") == "cloud-hypervisor"
        and campaign.get("power_cut_signal") == "SIGKILL"
        and campaign.get("power_cut_target") == "cloud-hypervisor"
        and campaign.get("power_cut_observed") is True
        and isinstance(campaign.get("first_epoch_runner_exit"), int)
        and isinstance(campaign.get("first_vmm_pid"), int)
        and campaign["first_vmm_pid"] > 0
        and isinstance(campaign.get("first_vmm_proc_starttime"), str)
        and campaign["first_vmm_proc_starttime"].isdigit()
        and is_sha256(campaign.get("first_vmm_command_sha256"))
        and campaign.get("transition_observed")
        in {
            "pending-workspace",
            "projection-stage",
            "transport-receive-staging",
            "cas-install",
            "manifest-install",
            "branch-record-install",
            "branch-pointer-update",
            "manifest-install-directory-fsync",
            "branch-record-install-directory-fsync",
            "branch-pointer-update-directory-fsync",
        }
        and campaign.get("workspace_phase_raw_observed") in {1, 2}
        and campaign.get("workspace_phase_encoding")
        == "stable=1,pending-exchange=2"
        and is_sha256(campaign.get("first_boot_id_sha256"))
        and is_sha256(campaign.get("recovery_boot_id_sha256"))
        and campaign["first_boot_id_sha256"]
        != campaign["recovery_boot_id_sha256"]
        and campaign.get("distinct_boot_observed") is True
        and campaign.get("crash_image_reused_as_preseed") is True
        and campaign.get("recovery_root_copy_method")
        in {"cp-reflink-always-sparse-auto", "cp-plain-sparse"}
        and SOURCE_REVISION.fullmatch(str(campaign.get("source_revision", "")))
        is not None
        and re.fullmatch(r"rev[0-9]{4,}", str(campaign.get("product_revision", "")))
        is not None
        and isinstance(campaign.get("version"), str)
        and campaign["product_revision"] in campaign["version"]
        and is_sha256(campaign.get("binary_sha256"))
        and isinstance(campaign.get("elapsed_ms"), int)
        and campaign["elapsed_ms"] > 0
        and campaign.get("contains_secrets") is False
        and campaign.get("dishonest_storage_assessed") is False,
        "power-cut campaign receipt is invalid",
    )
    if proof_version == 3:
        boundary = campaign.get("cut_boundary_observed")
        require(
            boundary in {"pre-exchange-pending", "post-exchange-pending"}
            and campaign.get("transition_observed") == "pending-workspace"
            and campaign.get("projection_orientation_observed")
            == ("active" if boundary == "pre-exchange-pending" else "pending")
            and isinstance(campaign.get("projection_stage_present_at_arm"), bool),
            "power-cut v3 boundary observation is invalid",
        )
    elif proof_version == 4:
        boundary = campaign.get("cut_boundary_observed")
        transition = (
            "transport-receive-staging"
            if boundary == "receive-staging-partial"
            else "cas-install"
        )
        require(
            boundary in {"receive-staging-partial", "cas-install-temporary"}
            and campaign.get("transition_observed") == transition
            and campaign.get("projection_orientation_observed") == "active"
            and campaign.get("projection_stage_present_at_arm") is False
            and campaign.get("workspace_phase_raw_observed") == 1
            and campaign.get("temporary_class_observed") == transition
            and isinstance(campaign.get("temporary_bytes_at_arm"), int)
            and campaign["temporary_bytes_at_arm"] > 0
            and isinstance(campaign.get("expected_object_bytes"), int)
            and campaign["expected_object_bytes"] >= 8 * 1024 * 1024
            and campaign["temporary_bytes_at_arm"]
            <= campaign["expected_object_bytes"]
            and (
                boundary != "receive-staging-partial"
                or campaign["temporary_bytes_at_arm"]
                < campaign["expected_object_bytes"]
            )
            and campaign.get("temporary_mode_at_arm") == "0600"
            and campaign.get("temporary_link_count_at_arm") == 1
            and campaign.get("temporary_owner_match_at_arm") is True
            and is_sha256(campaign.get("expected_object_sha256"))
            and campaign.get("final_object_present_at_arm") is False
            and campaign.get("agent_sigstop_at_arm") is True,
            "power-cut v4 object boundary observation is invalid",
        )
    elif proof_version == 5:
        boundary = campaign.get("cut_boundary_observed")
        transitions = {
            "manifest-install-temporary": "manifest-install",
            "branch-record-install-temporary": "branch-record-install",
            "branch-pointer-update-temporary": "branch-pointer-update",
        }
        transition = transitions.get(boundary)
        require(
            transition is not None
            and campaign.get("transition_observed") == transition
            and campaign.get("projection_orientation_observed") == "active"
            and campaign.get("projection_stage_present_at_arm") is False
            and campaign.get("workspace_phase_raw_observed") == 1
            and campaign.get("temporary_class_observed") == transition
            and isinstance(campaign.get("temporary_bytes_at_arm"), int)
            and 0 < campaign["temporary_bytes_at_arm"] <= 4 * 1024 * 1024
            and is_sha256(campaign.get("temporary_sha256_at_arm"))
            and campaign.get("temporary_mode_at_arm") == "0600"
            and campaign.get("temporary_link_count_at_arm") == 1
            and campaign.get("temporary_owner_match_at_arm") is True
            and is_sha256(campaign.get("target_name_sha256"))
            and campaign.get("destination_state_at_arm")
            == (
                "prior"
                if boundary == "branch-pointer-update-temporary"
                else "absent"
            )
            and campaign.get("qualification_scheduler_fence")
            == "strace-path-filtered-delay-enter+sigstop"
            and campaign.get("traced_agent_at_arm") is True
            and campaign.get("agent_sigstop_at_arm") is True,
            "power-cut v5 publication boundary observation is invalid",
        )
        require(
            is_sha256(campaign.get("marker_sha256")),
            "power-cut v5 marker commitment is invalid",
        )
        commitments = campaign.get("publication_target_commitments")
        selected = {
            "manifest-install-temporary": "manifest",
            "branch-record-install-temporary": "branch_record",
            "branch-pointer-update-temporary": "branch_pointer",
        }[boundary]
        require(
            publication_commitments_valid(commitments)
            and commitments[selected]["name_sha256"]
            == campaign["target_name_sha256"]
            and commitments[selected]["bytes"]
            == campaign["temporary_bytes_at_arm"]
            and commitments[selected]["sha256"]
            == campaign["temporary_sha256_at_arm"],
            "power-cut v5 publication target commitments are invalid",
        )
    elif proof_version == 6:
        boundary = campaign.get("cut_boundary_observed")
        transitions = {
            "manifest-install-directory-fsync": "manifest-install-directory-fsync",
            "branch-record-install-directory-fsync": (
                "branch-record-install-directory-fsync"
            ),
            "branch-pointer-update-directory-fsync": (
                "branch-pointer-update-directory-fsync"
            ),
        }
        selected = {
            "manifest-install-directory-fsync": "manifest",
            "branch-record-install-directory-fsync": "branch_record",
            "branch-pointer-update-directory-fsync": "branch_pointer",
        }.get(boundary)
        directory = {
            "manifest-install-directory-fsync": "manifests",
            "branch-record-install-directory-fsync": "records",
            "branch-pointer-update-directory-fsync": "branches",
        }.get(boundary)
        commitments = campaign.get("publication_target_commitments")
        require(
            selected is not None
            and directory is not None
            and campaign.get("transition_observed") == transitions[boundary]
            and campaign.get("projection_orientation_observed") == "active"
            and campaign.get("projection_stage_present_at_arm") is False
            and campaign.get("workspace_phase_raw_observed") == 1
            and campaign.get("directory_class_observed") == directory
            and campaign.get("directory_name_sha256")
            == hashlib.sha256(directory.encode("ascii")).hexdigest()
            and isinstance(campaign.get("selected_final_bytes_at_arm"), int)
            and 0 < campaign["selected_final_bytes_at_arm"] <= 4 * 1024 * 1024
            and is_sha256(campaign.get("selected_final_sha256_at_arm"))
            and campaign.get("selected_temporary_absent_at_arm") is True
            and is_sha256(campaign.get("target_name_sha256"))
            and campaign.get("destination_state_at_arm")
            == (
                "successor"
                if boundary == "branch-pointer-update-directory-fsync"
                else "exact"
            )
            and campaign.get("qualification_scheduler_fence")
            == "strace-path-filtered-fsync-delay-enter+sigstop"
            and campaign.get("traced_agent_at_arm") is True
            and campaign.get("agent_sigstop_at_arm") is True
            and is_sha256(campaign.get("marker_sha256"))
            and publication_commitments_valid(commitments)
            and commitments[selected]["name_sha256"]
            == campaign["target_name_sha256"]
            and commitments[selected]["bytes"]
            == campaign["selected_final_bytes_at_arm"]
            and commitments[selected]["sha256"]
            == campaign["selected_final_sha256_at_arm"],
            "power-cut v6 post-rename boundary observation is invalid",
        )

    files = campaign.get("files")
    require(
        isinstance(files, dict) and set(files) == EXPECTED_FILES,
        "power-cut campaign file set is invalid",
    )
    for relative, evidence in files.items():
        require(
            isinstance(evidence, dict)
            and set(evidence) == {"bytes", "sha256"}
            and isinstance(evidence.get("bytes"), int)
            and 0 < evidence["bytes"] <= 4 * 1024 * 1024
            and is_sha256(evidence.get("sha256")),
            f"power-cut file evidence is invalid: {relative}",
        )
        path = root / relative
        require(
            path.is_file()
            and not path.is_symlink()
            and path.stat().st_size == evidence["bytes"]
            and sha256_file(path) == evidence["sha256"],
            f"power-cut file digest mismatch: {relative}",
        )

    arm = load(root, "epoch-1/live/workspace-export/power-cut/armed.json")
    arm_fields = {
        "schema",
        "status",
        "transition",
        "workspace_phase_raw",
        "workspace_phase_encoding",
        "marker_sha256",
        "first_boot_id_sha256",
        "prior",
        "completed",
        "contains_secrets",
    }
    if proof_version >= 3:
        arm_fields |= {
            "cut_boundary",
            "projection_orientation",
            "projection_stage_present",
        }
    if proof_version == 4:
        arm_fields |= {
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
    if proof_version == 5:
        arm_fields |= {
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
    if proof_version == 6:
        arm_fields |= {
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
    require(
        set(arm) == arm_fields
        and arm.get("schema") == f"iotox.sync-power-cut-arm.v{proof_version}"
        and arm.get("status") == "armed"
        and arm.get("transition") == campaign["transition_observed"]
        and arm.get("workspace_phase_raw")
        == campaign["workspace_phase_raw_observed"]
        and arm.get("workspace_phase_encoding")
        == campaign["workspace_phase_encoding"]
        and is_sha256(arm.get("marker_sha256"))
        and arm.get("first_boot_id_sha256") == campaign["first_boot_id_sha256"]
        and summary_valid(arm.get("prior"))
        and summary_valid(arm.get("completed"))
        and arm["prior"] != arm["completed"]
        and arm.get("contains_secrets") is False,
        "power-cut arm receipt is invalid",
    )
    if proof_version >= 3:
        require(
            arm.get("cut_boundary") == campaign["cut_boundary_observed"]
            and arm.get("projection_orientation")
            == campaign["projection_orientation_observed"]
            and arm.get("projection_stage_present")
            == campaign["projection_stage_present_at_arm"],
            "power-cut arm boundary does not match its campaign",
        )
    if proof_version == 4:
        require(
            arm.get("temporary_class") == campaign["temporary_class_observed"]
            and arm.get("temporary_bytes_at_arm")
            == campaign["temporary_bytes_at_arm"]
            and arm.get("temporary_mode_at_arm")
            == campaign["temporary_mode_at_arm"]
            and arm.get("temporary_link_count_at_arm")
            == campaign["temporary_link_count_at_arm"]
            and arm.get("temporary_owner_match_at_arm")
            == campaign["temporary_owner_match_at_arm"]
            and arm.get("expected_object_sha256")
            == campaign["expected_object_sha256"]
            and arm.get("expected_object_bytes")
            == campaign["expected_object_bytes"]
            and arm.get("final_object_present_at_arm") is False
            and arm.get("agent_sigstop_at_arm") is True,
            "power-cut v4 arm object observation does not match its campaign",
        )
    if proof_version == 5:
        require(
            arm.get("marker_sha256") == campaign["marker_sha256"]
            and arm.get("temporary_class") == campaign["temporary_class_observed"]
            and arm.get("temporary_bytes_at_arm")
            == campaign["temporary_bytes_at_arm"]
            and arm.get("temporary_sha256_at_arm")
            == campaign["temporary_sha256_at_arm"]
            and arm.get("temporary_mode_at_arm")
            == campaign["temporary_mode_at_arm"]
            and arm.get("temporary_link_count_at_arm")
            == campaign["temporary_link_count_at_arm"]
            and arm.get("temporary_owner_match_at_arm")
            == campaign["temporary_owner_match_at_arm"]
            and arm.get("target_name_sha256")
            == campaign["target_name_sha256"]
            and arm.get("publication_target_commitments")
            == campaign["publication_target_commitments"]
            and arm.get("destination_state_at_arm")
            == campaign["destination_state_at_arm"]
            and arm.get("qualification_scheduler_fence")
            == campaign["qualification_scheduler_fence"]
            and arm.get("traced_agent_at_arm") is True
            and arm.get("agent_sigstop_at_arm") is True,
            "power-cut v5 arm publication observation does not match its campaign",
        )
    if proof_version == 6:
        require(
            arm.get("marker_sha256") == campaign["marker_sha256"]
            and arm.get("directory_class")
            == campaign["directory_class_observed"]
            and arm.get("directory_name_sha256")
            == campaign["directory_name_sha256"]
            and arm.get("selected_final_bytes_at_arm")
            == campaign["selected_final_bytes_at_arm"]
            and arm.get("selected_final_sha256_at_arm")
            == campaign["selected_final_sha256_at_arm"]
            and arm.get("selected_temporary_absent_at_arm") is True
            and arm.get("target_name_sha256")
            == campaign["target_name_sha256"]
            and arm.get("publication_target_commitments")
            == campaign["publication_target_commitments"]
            and arm.get("destination_state_at_arm")
            == campaign["destination_state_at_arm"]
            and arm.get("qualification_scheduler_fence")
            == campaign["qualification_scheduler_fence"]
            and arm.get("traced_agent_at_arm") is True
            and arm.get("agent_sigstop_at_arm") is True,
            "power-cut v6 arm post-rename observation does not match its campaign",
        )

    recovery = load(
        root,
        "epoch-2/live/workspace-export/guest-receipts/iotox/sync-power-cut.json",
    )
    initial = recovery.get("initial_view_per_node")
    require(
        recovery.get("schema") == f"iotox.sync-power-cut.v{proof_version}"
        and recovery.get("status") == "passed"
        and recovery.get("power_cut_recovery") is True
        and recovery.get("power_cut_model")
        == "host-sigkill-cloud-hypervisor-preseeded-crash-image"
        and recovery.get("power_cut_transition")
        == (
            "branch-publication"
            if proof_version in {5, 6}
            else ("object-pipeline" if proof_version == 4 else "workspace-exchange")
        )
        and recovery.get("first_boot_id_sha256")
        == campaign["first_boot_id_sha256"]
        and recovery.get("recovery_boot_id_sha256")
        == campaign["recovery_boot_id_sha256"]
        and recovery.get("distinct_boot_observed") is True
        and initial
        in (["completed", "completed", "prior"], ["completed", "completed", "completed"])
        and recovery.get("initial_prior_or_completed_only") is True
        and isinstance(
            recovery.get("follower_projection_stage_present_before_restart"), bool
        )
        and recovery.get("follower_workspace_state_before_restart")
        in {"absent", "pending", "stable"}
        and (
            (
                recovery.get("follower_workspace_state_before_restart") == "absent"
                and recovery.get("follower_workspace_phase_raw_before_restart")
                is None
            )
            or (
                recovery.get("follower_workspace_state_before_restart") == "stable"
                and recovery.get("follower_workspace_phase_raw_before_restart") == 1
            )
            or (
                recovery.get("follower_workspace_state_before_restart") == "pending"
                and recovery.get("follower_workspace_phase_raw_before_restart") == 2
            )
        )
        and recovery.get("identity_preserved") is True
        and recovery.get("branch_count_per_node") == [3, 3, 3]
        and recovery.get("repair_verified_nodes") == 3
        and recovery.get("final") == arm["completed"]
        and isinstance(recovery.get("elapsed_ms"), int)
        and recovery["elapsed_ms"] > 0
        and recovery.get("contains_secrets") is False
        and recovery.get("dishonest_storage_assessed") is False,
        "power-cut recovery receipt is invalid",
    )
    if proof_version == 3:
        recovery_orientation = recovery.get(
            "follower_projection_orientation_before_restart"
        )
        boundary = campaign["cut_boundary_observed"]
        recovery_state = recovery.get("follower_workspace_state_before_restart")
        require(
            recovery.get("cut_boundary_requested")
            == boundary
            and recovery_state in {"pending", "stable"}
            and (
                (recovery_state == "stable" and recovery_orientation == "active")
                or (
                    recovery_state == "pending"
                    and recovery_orientation in {"active", "pending"}
                    and (
                        boundary != "post-exchange-pending"
                        or recovery_orientation == "pending"
                    )
                )
            )
            and (
                boundary != "post-exchange-pending"
                or initial == ["completed", "completed", "completed"]
            ),
            "power-cut v3 recovery boundary is invalid",
        )
    elif proof_version == 4:
        before = recovery.get("object_pipeline_before_restart")
        after = recovery.get("object_pipeline_after_recovery")
        pipeline_fields = {
            "incoming_temporary_count",
            "incoming_temporary_bytes",
            "cas_install_temporary_count",
            "cas_install_temporary_bytes",
            "expected_object_state",
        }
        require(
            recovery.get("cut_boundary_requested")
            == campaign["cut_boundary_observed"]
            and initial == ["completed", "completed", "prior"]
            and recovery.get("follower_workspace_state_before_restart") == "stable"
            and recovery.get("follower_workspace_phase_raw_before_restart") == 1
            and recovery.get("follower_projection_orientation_before_restart")
            == "active"
            and recovery.get("follower_projection_stage_present_before_restart")
            is False
            and recovery.get("expected_object_sha256")
            == campaign["expected_object_sha256"]
            and recovery.get("expected_object_bytes")
            == campaign["expected_object_bytes"]
            and recovery.get("agent_sigstop_at_arm") is True
            and isinstance(before, dict)
            and set(before) == pipeline_fields
            and isinstance(before.get("incoming_temporary_count"), int)
            and 0 <= before["incoming_temporary_count"] <= 4
            and isinstance(before.get("incoming_temporary_bytes"), int)
            and 0 <= before["incoming_temporary_bytes"]
            <= 4 * campaign["expected_object_bytes"]
            and isinstance(before.get("cas_install_temporary_count"), int)
            and 0 <= before["cas_install_temporary_count"] <= 1
            and isinstance(before.get("cas_install_temporary_bytes"), int)
            and 0 <= before["cas_install_temporary_bytes"]
            <= campaign["expected_object_bytes"]
            and before.get("expected_object_state") in {"absent", "exact"}
            and after
            == {
                "incoming_temporary_count": 0,
                "incoming_temporary_bytes": 0,
                "cas_install_temporary_count": 0,
                "cas_install_temporary_bytes": 0,
                "expected_object_state": "exact",
            },
            "power-cut v4 recovery boundary is invalid",
        )
    elif proof_version == 5:
        before = recovery.get("publication_before_restart")
        after = recovery.get("publication_after_recovery")
        publication_fields = {
            "manifest_state",
            "branch_record_state",
            "branch_pointer_state",
            "manifest_temporary_count",
            "manifest_temporary_bytes",
            "branch_record_temporary_count",
            "branch_record_temporary_bytes",
            "branch_pointer_temporary_count",
            "branch_pointer_temporary_bytes",
        }
        expected_prefix = {
            "manifest-install-temporary": ("absent", "absent", "prior"),
            "branch-record-install-temporary": ("exact", "absent", "prior"),
            "branch-pointer-update-temporary": ("exact", "exact", "prior"),
        }[campaign["cut_boundary_observed"]]
        selected_temporary = {
            "manifest-install-temporary": "manifest",
            "branch-record-install-temporary": "branch_record",
            "branch-pointer-update-temporary": "branch_pointer",
        }[campaign["cut_boundary_observed"]]
        temporary_state_valid = isinstance(before, dict)
        if temporary_state_valid:
            for name in ("manifest", "branch_record", "branch_pointer"):
                count = before.get(f"{name}_temporary_count")
                byte_count = before.get(f"{name}_temporary_bytes")
                if name == selected_temporary:
                    temporary_state_valid = temporary_state_valid and (
                        (count == 0 and byte_count == 0)
                        or (
                            count == 1
                            and byte_count == campaign["temporary_bytes_at_arm"]
                        )
                    )
                else:
                    temporary_state_valid = (
                        temporary_state_valid and count == 0 and byte_count == 0
                    )
        require(
            recovery.get("cut_boundary_requested")
            == campaign["cut_boundary_observed"]
            and recovery.get("marker_sha256") == campaign["marker_sha256"]
            and recovery.get("publication_target_commitments")
            == campaign["publication_target_commitments"]
            and initial == ["completed", "completed", "prior"]
            and recovery.get("follower_workspace_state_before_restart") == "stable"
            and recovery.get("follower_workspace_phase_raw_before_restart") == 1
            and recovery.get("follower_projection_orientation_before_restart")
            == "active"
            and recovery.get("follower_projection_stage_present_before_restart")
            is False
            and recovery.get("agent_sigstop_at_arm") is True
            and recovery.get("qualification_scheduler_fence")
            == "strace-path-filtered-delay-enter+sigstop"
            and isinstance(before, dict)
            and set(before) == publication_fields
            and before.get("manifest_state") == expected_prefix[0]
            and before.get("branch_record_state") == expected_prefix[1]
            and before.get("branch_pointer_state") == expected_prefix[2]
            and temporary_state_valid
            and after
            == {
                "manifest_state": "exact",
                "branch_record_state": "exact",
                "branch_pointer_state": "successor",
                "manifest_temporary_count": 0,
                "manifest_temporary_bytes": 0,
                "branch_record_temporary_count": 0,
                "branch_record_temporary_bytes": 0,
                "branch_pointer_temporary_count": 0,
                "branch_pointer_temporary_bytes": 0,
            },
            "power-cut v5 recovery boundary is invalid",
        )
    elif proof_version == 6:
        before = recovery.get("publication_before_restart")
        after = recovery.get("publication_after_recovery")
        publication_fields = {
            "manifest_state",
            "branch_record_state",
            "branch_pointer_state",
            "manifest_temporary_count",
            "manifest_temporary_bytes",
            "branch_record_temporary_count",
            "branch_record_temporary_bytes",
            "branch_pointer_temporary_count",
            "branch_pointer_temporary_bytes",
        }
        boundary = campaign["cut_boundary_observed"]
        selected_temporary = {
            "manifest-install-directory-fsync": "manifest",
            "branch-record-install-directory-fsync": "branch_record",
            "branch-pointer-update-directory-fsync": "branch_pointer",
        }[boundary]
        allowed_prefix = {
            "manifest-install-directory-fsync": (
                {"absent", "exact"},
                {"absent"},
                {"prior"},
            ),
            "branch-record-install-directory-fsync": (
                {"exact"},
                {"absent", "exact"},
                {"prior"},
            ),
            "branch-pointer-update-directory-fsync": (
                {"exact"},
                {"exact"},
                {"prior", "successor"},
            ),
        }[boundary]
        temporary_state_valid = isinstance(before, dict)
        if temporary_state_valid:
            for name in ("manifest", "branch_record", "branch_pointer"):
                count = before.get(f"{name}_temporary_count")
                byte_count = before.get(f"{name}_temporary_bytes")
                if name == selected_temporary:
                    temporary_state_valid = temporary_state_valid and (
                        (count == 0 and byte_count == 0)
                        or (
                            count == 1
                            and byte_count
                            == campaign["selected_final_bytes_at_arm"]
                        )
                    )
                else:
                    temporary_state_valid = (
                        temporary_state_valid and count == 0 and byte_count == 0
                    )
        require(
            recovery.get("cut_boundary_requested") == boundary
            and recovery.get("marker_sha256") == campaign["marker_sha256"]
            and recovery.get("publication_target_commitments")
            == campaign["publication_target_commitments"]
            and initial == ["completed", "completed", "prior"]
            and recovery.get("follower_workspace_state_before_restart") == "stable"
            and recovery.get("follower_workspace_phase_raw_before_restart") == 1
            and recovery.get("follower_projection_orientation_before_restart")
            == "active"
            and recovery.get("follower_projection_stage_present_before_restart")
            is False
            and recovery.get("agent_sigstop_at_arm") is True
            and recovery.get("qualification_scheduler_fence")
            == "strace-path-filtered-fsync-delay-enter+sigstop"
            and isinstance(before, dict)
            and set(before) == publication_fields
            and before.get("manifest_state") in allowed_prefix[0]
            and before.get("branch_record_state") in allowed_prefix[1]
            and before.get("branch_pointer_state") in allowed_prefix[2]
            and temporary_state_valid
            and after
            == {
                "manifest_state": "exact",
                "branch_record_state": "exact",
                "branch_pointer_state": "successor",
                "manifest_temporary_count": 0,
                "manifest_temporary_bytes": 0,
                "branch_record_temporary_count": 0,
                "branch_record_temporary_bytes": 0,
                "branch_pointer_temporary_count": 0,
                "branch_pointer_temporary_bytes": 0,
            },
            "power-cut v6 post-rename recovery boundary is invalid",
        )

    vm_smoke = load(
        root, "epoch-2/live/workspace-export/guest-receipts/iotox/vm-smoke.json"
    )
    require(
        vm_smoke.get("schema") == "iotox.sandwurm-vm-smoke.v0"
        and vm_smoke.get("status") == "passed"
        and vm_smoke.get("role") == "device"
        and vm_smoke.get("source_revision") == campaign["source_revision"]
        and vm_smoke.get("product_revision") == campaign["product_revision"]
        and vm_smoke.get("version") == campaign["version"]
        and vm_smoke.get("binary_sha256") == campaign["binary_sha256"]
        and vm_smoke.get("virtualization") == "kvm"
        and vm_smoke.get("cgroup_type") == "cgroup2fs"
        and vm_smoke.get("network_class") == "none"
        and vm_smoke.get("contains_secrets") is False,
        "power-cut VM identity receipt is invalid",
    )

    first_chain = load(root, "epoch-1/direct-cloud-hypervisor-live-chain.json")
    second_chain = load(root, "epoch-2/direct-cloud-hypervisor-live-chain.json")
    require(
        first_chain.get("schema") == "sandwurm.direct-cloud-hypervisor-live-chain.v0"
        and first_chain.get("receipts", {}).get("live_launch", {}).get("status")
        == "exited",
        "first Sandwurm chain did not retain a terminal launch",
    )
    require(
        second_chain.get("schema") == "sandwurm.direct-cloud-hypervisor-live-chain.v0"
        and second_chain.get("status") == "guest-evidence-observed"
        and second_chain.get("guest_evidence", {}).get("observed") is True
        and second_chain.get("receipts", {}).get("live_launch", {}).get("status")
        == "exited",
        "recovery Sandwurm chain did not observe guest evidence",
    )

    first_launch = load(root, "epoch-1/live/cloud-hypervisor-launch.json")
    second_launch = load(root, "epoch-2/live/cloud-hypervisor-launch.json")
    networkless_launch(first_launch, cut=True)
    networkless_launch(second_launch, cut=False)
    first_vmm = first_launch["vmm"]
    command_sha256 = hashlib.sha256(
        b"\0".join(argument.encode("utf-8") for argument in first_vmm["argv"])
    ).hexdigest()
    require(
        first_vmm["pid"] == campaign["first_vmm_pid"]
        and first_vmm["proc_starttime"] == campaign["first_vmm_proc_starttime"]
        and command_sha256 == campaign["first_vmm_command_sha256"],
        "host cut identity does not match the first VMM receipt",
    )

    first_runtime = load(
        root, "epoch-1/prelaunch/runtime-root/direct-nixos-runtime-root.json"
    )
    second_runtime = load(
        root, "epoch-2/prelaunch/runtime-root/direct-nixos-runtime-root.json"
    )
    require(
        first_runtime.get("status") == "ready"
        and first_runtime.get("task_owned") is True
        and isinstance(first_runtime.get("runtime_root_image"), str)
        and second_runtime.get("status") == "ready"
        and second_runtime.get("task_owned") is True
        and second_runtime.get("source_root_image")
        == first_runtime["runtime_root_image"]
        and second_runtime.get("copy_method") == campaign["recovery_root_copy_method"],
        "crash-image preseed lineage is invalid",
    )

    compact_path = root / "compact-export.json"
    if compact_path.exists():
        compact = load(root, "compact-export.json", 256 * 1024)
        manifest_files = compact.get("files")
        require(
            compact.get("schema")
            == f"iotox.sync-power-cut-sandwurm-compact.v{proof_version}"
            and compact.get("status") == "passed"
            and compact.get("contains_secrets") is False
            and isinstance(manifest_files, list)
            and len(manifest_files) == len(EXPECTED_FILES) + 1,
            "power-cut compact manifest is invalid",
        )
        expected_manifest_paths = EXPECTED_FILES | {"campaign.json"}
        require(
            {entry.get("path") for entry in manifest_files if isinstance(entry, dict)}
            == expected_manifest_paths,
            "power-cut compact manifest file set is invalid",
        )
        for entry in manifest_files:
            require(
                isinstance(entry, dict)
                and set(entry) == {"bytes", "path", "sha256"}
                and isinstance(entry.get("bytes"), int)
                and entry["bytes"] > 0
                and is_sha256(entry.get("sha256")),
                "power-cut compact manifest entry is invalid",
            )
            path = root / entry["path"]
            require(
                path.is_file()
                and not path.is_symlink()
                and path.stat().st_size == entry["bytes"]
                and sha256_file(path) == entry["sha256"],
                "power-cut compact manifest digest mismatch",
            )

    return {
        "schema": f"iotox.sync-power-cut-sandwurm-verification.v{proof_version}",
        "status": "passed",
        "vm_substrate": "cloud-hypervisor",
        "power_cut_signal": "SIGKILL",
        "transition_observed": campaign["transition_observed"],
        **(
            {"cut_boundary_observed": campaign["cut_boundary_observed"]}
            if proof_version >= 3
            else {}
        ),
        "initial_view_per_node": initial,
        "branch_count_per_node": recovery["branch_count_per_node"],
        "repair_verified_nodes": recovery["repair_verified_nodes"],
        "distinct_boot_observed": True,
        "crash_image_reused_as_preseed": True,
        "source_revision": campaign["source_revision"],
        "product_revision": campaign["product_revision"],
        "binary_sha256": campaign["binary_sha256"],
        "contains_secrets": False,
        "dishonest_storage_assessed": False,
    }


def write_fixture(
    root: Path, version: int = 3, boundary: str = "pre-exchange-pending"
) -> None:
    if version not in {2, 3, 4, 5, 6}:
        raise ValueError("fixture proof version is unsupported")
    workspace_boundaries = {"pre-exchange-pending", "post-exchange-pending"}
    object_boundaries = {"receive-staging-partial", "cas-install-temporary"}
    publication_boundaries = {
        "manifest-install-temporary",
        "branch-record-install-temporary",
        "branch-pointer-update-temporary",
    }
    post_publication_boundaries = {
        "manifest-install-directory-fsync",
        "branch-record-install-directory-fsync",
        "branch-pointer-update-directory-fsync",
    }
    valid_boundaries = (
        post_publication_boundaries
        if version == 6
        else (
            publication_boundaries
            if version == 5
            else (object_boundaries if version == 4 else workspace_boundaries)
        )
    )
    if boundary not in valid_boundaries:
        raise ValueError("fixture cut boundary is unsupported")
    if version == 2 and boundary != "pre-exchange-pending":
        raise ValueError("v2 fixture does not carry an exact cut boundary")
    root.mkdir(parents=True)
    prior = {"bytes": 1, "digest": "11" * 32, "directories": 0, "files": 1}
    completed = {
        "bytes": 2,
        "digest": "22" * 32,
        "directories": 0,
        "files": 1,
    }
    arm = {
        "schema": f"iotox.sync-power-cut-arm.v{version}",
        "status": "armed",
        "transition": "pending-workspace",
        "workspace_phase_raw": 2,
        "workspace_phase_encoding": "stable=1,pending-exchange=2",
        "marker_sha256": "33" * 32,
        "first_boot_id_sha256": "44" * 32,
        "prior": prior,
        "completed": completed,
        "contains_secrets": False,
    }
    if version >= 3:
        arm.update(
            {
                "cut_boundary": boundary,
                "projection_orientation": (
                    "pending" if boundary == "post-exchange-pending" else "active"
                ),
                "projection_stage_present": False,
            }
        )
    if version == 4:
        transition = (
            "transport-receive-staging"
            if boundary == "receive-staging-partial"
            else "cas-install"
        )
        arm.update(
            {
                "transition": transition,
                "workspace_phase_raw": 1,
                "projection_orientation": "active",
                "temporary_class": transition,
                "temporary_bytes_at_arm": 8 * 1024 * 1024,
                "temporary_mode_at_arm": "0600",
                "temporary_link_count_at_arm": 1,
                "temporary_owner_match_at_arm": True,
                "expected_object_sha256": "88" * 32,
                "expected_object_bytes": 32 * 1024 * 1024,
                "final_object_present_at_arm": False,
                "agent_sigstop_at_arm": True,
            }
        )
    if version == 5:
        transition = {
            "manifest-install-temporary": "manifest-install",
            "branch-record-install-temporary": "branch-record-install",
            "branch-pointer-update-temporary": "branch-pointer-update",
        }[boundary]
        arm.update(
            {
                "transition": transition,
                "workspace_phase_raw": 1,
                "projection_orientation": "active",
                "temporary_class": transition,
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
                        "name_sha256": "99" * 32,
                        "bytes": 1024,
                        "sha256": "88" * 32,
                    },
                    "branch_pointer": {
                        "name_sha256": "99" * 32,
                        "bytes": 1024,
                        "sha256": "88" * 32,
                        "prior_bytes": 1024,
                        "prior_sha256": "77" * 32,
                    },
                },
                "destination_state_at_arm": (
                    "prior"
                    if boundary == "branch-pointer-update-temporary"
                    else "absent"
                ),
                "qualification_scheduler_fence": (
                    "strace-path-filtered-delay-enter+sigstop"
                ),
                "traced_agent_at_arm": True,
                "agent_sigstop_at_arm": True,
            }
        )
    if version == 6:
        selected = {
            "manifest-install-directory-fsync": "manifest",
            "branch-record-install-directory-fsync": "branch_record",
            "branch-pointer-update-directory-fsync": "branch_pointer",
        }[boundary]
        directory = {
            "manifest-install-directory-fsync": "manifests",
            "branch-record-install-directory-fsync": "records",
            "branch-pointer-update-directory-fsync": "branches",
        }[boundary]
        transition = boundary
        commitments = {
            "manifest": {
                "name_sha256": "99" * 32,
                "bytes": 1024,
                "sha256": "88" * 32,
            },
            "branch_record": {
                "name_sha256": "99" * 32,
                "bytes": 1024,
                "sha256": "88" * 32,
            },
            "branch_pointer": {
                "name_sha256": "99" * 32,
                "bytes": 1024,
                "sha256": "88" * 32,
                "prior_bytes": 1024,
                "prior_sha256": "77" * 32,
            },
        }
        arm.update(
            {
                "transition": transition,
                "workspace_phase_raw": 1,
                "projection_orientation": "active",
                "directory_class": directory,
                "directory_name_sha256": hashlib.sha256(
                    directory.encode("ascii")
                ).hexdigest(),
                "selected_final_bytes_at_arm": commitments[selected]["bytes"],
                "selected_final_sha256_at_arm": commitments[selected]["sha256"],
                "selected_temporary_absent_at_arm": True,
                "target_name_sha256": commitments[selected]["name_sha256"],
                "publication_target_commitments": commitments,
                "destination_state_at_arm": (
                    "successor"
                    if boundary == "branch-pointer-update-directory-fsync"
                    else "exact"
                ),
                "qualification_scheduler_fence": (
                    "strace-path-filtered-fsync-delay-enter+sigstop"
                ),
                "traced_agent_at_arm": True,
                "agent_sigstop_at_arm": True,
            }
        )
    recovery = {
        "schema": f"iotox.sync-power-cut.v{version}",
        "status": "passed",
        "power_cut_recovery": True,
        "power_cut_model": "host-sigkill-cloud-hypervisor-preseeded-crash-image",
        "power_cut_transition": "workspace-exchange",
        "first_boot_id_sha256": "44" * 32,
        "recovery_boot_id_sha256": "55" * 32,
        "distinct_boot_observed": True,
        "initial_view_per_node": [
            "completed",
            "completed",
            "completed" if boundary == "post-exchange-pending" else "prior",
        ],
        "initial_prior_or_completed_only": True,
        "follower_projection_stage_present_before_restart": False,
        "follower_workspace_state_before_restart": "pending",
        "follower_workspace_phase_raw_before_restart": 2,
        "identity_preserved": True,
        "branch_count_per_node": [3, 3, 3],
        "repair_verified_nodes": 3,
        "final": completed,
        "elapsed_ms": 1,
        "contains_secrets": False,
        "dishonest_storage_assessed": False,
    }
    if version >= 3:
        recovery.update(
            {
                "cut_boundary_requested": boundary,
                "follower_projection_orientation_before_restart": (
                    "pending" if boundary == "post-exchange-pending" else "active"
                ),
            }
        )
    if version == 4:
        recovery.update(
            {
                "power_cut_transition": "object-pipeline",
                "initial_view_per_node": ["completed", "completed", "prior"],
                "follower_workspace_state_before_restart": "stable",
                "follower_workspace_phase_raw_before_restart": 1,
                "follower_projection_orientation_before_restart": "active",
                "expected_object_sha256": "88" * 32,
                "expected_object_bytes": 32 * 1024 * 1024,
                "agent_sigstop_at_arm": True,
                "object_pipeline_before_restart": {
                    "incoming_temporary_count": 1,
                    "incoming_temporary_bytes": 8 * 1024 * 1024,
                    "cas_install_temporary_count": 0,
                    "cas_install_temporary_bytes": 0,
                    "expected_object_state": "absent",
                },
                "object_pipeline_after_recovery": {
                    "incoming_temporary_count": 0,
                    "incoming_temporary_bytes": 0,
                    "cas_install_temporary_count": 0,
                    "cas_install_temporary_bytes": 0,
                    "expected_object_state": "exact",
                },
            }
        )
    if version == 5:
        prefix = {
            "manifest-install-temporary": ("absent", "absent", "prior"),
            "branch-record-install-temporary": ("exact", "absent", "prior"),
            "branch-pointer-update-temporary": ("exact", "exact", "prior"),
        }[boundary]
        recovery.update(
            {
                "power_cut_transition": "branch-publication",
                "marker_sha256": "33" * 32,
                "publication_target_commitments": arm[
                    "publication_target_commitments"
                ],
                "initial_view_per_node": ["completed", "completed", "prior"],
                "follower_workspace_state_before_restart": "stable",
                "follower_workspace_phase_raw_before_restart": 1,
                "follower_projection_orientation_before_restart": "active",
                "agent_sigstop_at_arm": True,
                "qualification_scheduler_fence": (
                    "strace-path-filtered-delay-enter+sigstop"
                ),
                "publication_before_restart": {
                    "manifest_state": prefix[0],
                    "branch_record_state": prefix[1],
                    "branch_pointer_state": prefix[2],
                    "manifest_temporary_count": 1
                    if boundary == "manifest-install-temporary"
                    else 0,
                    "manifest_temporary_bytes": 1024
                    if boundary == "manifest-install-temporary"
                    else 0,
                    "branch_record_temporary_count": 1
                    if boundary == "branch-record-install-temporary"
                    else 0,
                    "branch_record_temporary_bytes": 1024
                    if boundary == "branch-record-install-temporary"
                    else 0,
                    "branch_pointer_temporary_count": 1
                    if boundary == "branch-pointer-update-temporary"
                    else 0,
                    "branch_pointer_temporary_bytes": 1024
                    if boundary == "branch-pointer-update-temporary"
                    else 0,
                },
                "publication_after_recovery": {
                    "manifest_state": "exact",
                    "branch_record_state": "exact",
                    "branch_pointer_state": "successor",
                    "manifest_temporary_count": 0,
                    "manifest_temporary_bytes": 0,
                    "branch_record_temporary_count": 0,
                    "branch_record_temporary_bytes": 0,
                    "branch_pointer_temporary_count": 0,
                    "branch_pointer_temporary_bytes": 0,
                },
            }
        )
    if version == 6:
        prefix = {
            "manifest-install-directory-fsync": ("absent", "absent", "prior"),
            "branch-record-install-directory-fsync": ("exact", "absent", "prior"),
            "branch-pointer-update-directory-fsync": ("exact", "exact", "prior"),
        }[boundary]
        selected = {
            "manifest-install-directory-fsync": "manifest",
            "branch-record-install-directory-fsync": "branch_record",
            "branch-pointer-update-directory-fsync": "branch_pointer",
        }[boundary]
        recovery.update(
            {
                "power_cut_transition": "branch-publication",
                "marker_sha256": "33" * 32,
                "publication_target_commitments": arm[
                    "publication_target_commitments"
                ],
                "initial_view_per_node": ["completed", "completed", "prior"],
                "follower_workspace_state_before_restart": "stable",
                "follower_workspace_phase_raw_before_restart": 1,
                "follower_projection_orientation_before_restart": "active",
                "agent_sigstop_at_arm": True,
                "qualification_scheduler_fence": (
                    "strace-path-filtered-fsync-delay-enter+sigstop"
                ),
                "publication_before_restart": {
                    "manifest_state": prefix[0],
                    "branch_record_state": prefix[1],
                    "branch_pointer_state": prefix[2],
                    "manifest_temporary_count": 1 if selected == "manifest" else 0,
                    "manifest_temporary_bytes": 1024 if selected == "manifest" else 0,
                    "branch_record_temporary_count": (
                        1 if selected == "branch_record" else 0
                    ),
                    "branch_record_temporary_bytes": (
                        1024 if selected == "branch_record" else 0
                    ),
                    "branch_pointer_temporary_count": (
                        1 if selected == "branch_pointer" else 0
                    ),
                    "branch_pointer_temporary_bytes": (
                        1024 if selected == "branch_pointer" else 0
                    ),
                },
                "publication_after_recovery": {
                    "manifest_state": "exact",
                    "branch_record_state": "exact",
                    "branch_pointer_state": "successor",
                    "manifest_temporary_count": 0,
                    "manifest_temporary_bytes": 0,
                    "branch_record_temporary_count": 0,
                    "branch_record_temporary_bytes": 0,
                    "branch_pointer_temporary_count": 0,
                    "branch_pointer_temporary_bytes": 0,
                },
            }
        )
    vm = {
        "schema": "iotox.sandwurm-vm-smoke.v0",
        "status": "passed",
        "role": "device",
        "source_revision": "66" * 20,
        "product_revision": "rev0048",
        "version": "IoTox 0.48.0 rev0048",
        "binary_sha256": "77" * 32,
        "virtualization": "kvm",
        "cgroup_type": "cgroup2fs",
        "network_class": "none",
        "contains_secrets": False,
    }
    chain_1 = {
        "schema": "sandwurm.direct-cloud-hypervisor-live-chain.v0",
        "status": "launched-without-guest-evidence",
        "receipts": {"live_launch": {"status": "exited"}},
    }
    chain_2 = {
        "schema": "sandwurm.direct-cloud-hypervisor-live-chain.v0",
        "status": "guest-evidence-observed",
        "guest_evidence": {"observed": True},
        "receipts": {"live_launch": {"status": "exited"}},
    }
    argv = [
        "/nix/store/example/bin/cloud-hypervisor",
        "--disk",
        "path=/proof/root.raw,readonly=off",
    ]
    launch_1 = {
        "schema": "sandwurm.cloud-hypervisor-launch.v0",
        "status": "exited",
        "network": {"class": "none", "mode": "none"},
        "vmm": {
            "process_observed": True,
            "exit_observed": True,
            "exit_status": 137,
            "pid": 123,
            "proc_starttime": "456",
            "argv": argv,
        },
        "ch_remote": {"exit_control_observed": False},
    }
    launch_2 = {
        **launch_1,
        "vmm": {**launch_1["vmm"], "pid": 124, "exit_status": 0},
        "ch_remote": {"exit_control_observed": True},
    }
    first_runtime = {
        "status": "ready",
        "task_owned": True,
        "runtime_root_image": "/proof/root.raw",
        "source_root_image": "/nix/store/base.raw",
        "copy_method": "cp-reflink-always-sparse-auto",
    }
    second_runtime = {
        "status": "ready",
        "task_owned": True,
        "runtime_root_image": "/proof/root-2.raw",
        "source_root_image": "/proof/root.raw",
        "copy_method": "cp-reflink-always-sparse-auto",
    }
    documents = {
        "epoch-1/live/workspace-export/power-cut/armed.json": arm,
        "epoch-1/direct-cloud-hypervisor-live-chain.json": chain_1,
        "epoch-1/live/cloud-hypervisor-launch.json": launch_1,
        "epoch-1/prelaunch/runtime-root/direct-nixos-runtime-root.json": first_runtime,
        "epoch-2/live/workspace-export/guest-receipts/iotox/sync-power-cut.json": recovery,
        "epoch-2/live/workspace-export/guest-receipts/iotox/vm-smoke.json": vm,
        "epoch-2/direct-cloud-hypervisor-live-chain.json": chain_2,
        "epoch-2/live/cloud-hypervisor-launch.json": launch_2,
        "epoch-2/prelaunch/runtime-root/direct-nixos-runtime-root.json": second_runtime,
    }
    for relative, document in documents.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(document, sort_keys=True) + "\n", encoding="utf-8"
        )
    files = {
        relative: {
            "bytes": (root / relative).stat().st_size,
            "sha256": sha256_file(root / relative),
        }
        for relative in documents
    }
    command_sha256 = hashlib.sha256(
        b"\0".join(argument.encode("utf-8") for argument in argv)
    ).hexdigest()
    campaign = {
        "schema": f"iotox.sync-power-cut-sandwurm.v{version}",
        "status": "passed",
        "vm_substrate": "cloud-hypervisor",
        "power_cut_signal": "SIGKILL",
        "power_cut_target": "cloud-hypervisor",
        "power_cut_observed": True,
        "first_epoch_runner_exit": 0,
        "first_vmm_pid": 123,
        "first_vmm_proc_starttime": "456",
        "first_vmm_command_sha256": command_sha256,
        "transition_observed": "pending-workspace",
        "workspace_phase_raw_observed": 2,
        "workspace_phase_encoding": "stable=1,pending-exchange=2",
        "first_boot_id_sha256": "44" * 32,
        "recovery_boot_id_sha256": "55" * 32,
        "distinct_boot_observed": True,
        "crash_image_reused_as_preseed": True,
        "recovery_root_copy_method": "cp-reflink-always-sparse-auto",
        "source_revision": "66" * 20,
        "product_revision": "rev0048",
        "version": "IoTox 0.48.0 rev0048",
        "binary_sha256": "77" * 32,
        "elapsed_ms": 2,
        "files": files,
        "contains_secrets": False,
        "dishonest_storage_assessed": False,
    }
    if version >= 3:
        campaign.update(
            {
                "cut_boundary_observed": boundary,
                "projection_orientation_observed": (
                    "active" if boundary == "pre-exchange-pending" else "pending"
                ),
                "projection_stage_present_at_arm": False,
            }
        )
    if version == 4:
        campaign.update(
            {
                "transition_observed": arm["transition"],
                "workspace_phase_raw_observed": 1,
                "projection_orientation_observed": "active",
                "temporary_class_observed": arm["temporary_class"],
                "temporary_bytes_at_arm": arm["temporary_bytes_at_arm"],
                "temporary_mode_at_arm": "0600",
                "temporary_link_count_at_arm": 1,
                "temporary_owner_match_at_arm": True,
                "expected_object_sha256": "88" * 32,
                "expected_object_bytes": 32 * 1024 * 1024,
                "final_object_present_at_arm": False,
                "agent_sigstop_at_arm": True,
            }
        )
    if version == 5:
        campaign.update(
            {
                "marker_sha256": arm["marker_sha256"],
                "publication_target_commitments": arm[
                    "publication_target_commitments"
                ],
                "transition_observed": arm["transition"],
                "workspace_phase_raw_observed": 1,
                "projection_orientation_observed": "active",
                "temporary_class_observed": arm["temporary_class"],
                "temporary_bytes_at_arm": arm["temporary_bytes_at_arm"],
                "temporary_sha256_at_arm": arm["temporary_sha256_at_arm"],
                "temporary_mode_at_arm": "0600",
                "temporary_link_count_at_arm": 1,
                "temporary_owner_match_at_arm": True,
                "target_name_sha256": arm["target_name_sha256"],
                "destination_state_at_arm": arm["destination_state_at_arm"],
                "qualification_scheduler_fence": (
                    "strace-path-filtered-delay-enter+sigstop"
                ),
                "traced_agent_at_arm": True,
                "agent_sigstop_at_arm": True,
            }
        )
    if version == 6:
        campaign.update(
            {
                "marker_sha256": arm["marker_sha256"],
                "publication_target_commitments": arm[
                    "publication_target_commitments"
                ],
                "transition_observed": arm["transition"],
                "workspace_phase_raw_observed": 1,
                "projection_orientation_observed": "active",
                "directory_class_observed": arm["directory_class"],
                "directory_name_sha256": arm["directory_name_sha256"],
                "selected_final_bytes_at_arm": arm[
                    "selected_final_bytes_at_arm"
                ],
                "selected_final_sha256_at_arm": arm[
                    "selected_final_sha256_at_arm"
                ],
                "selected_temporary_absent_at_arm": True,
                "target_name_sha256": arm["target_name_sha256"],
                "destination_state_at_arm": arm["destination_state_at_arm"],
                "qualification_scheduler_fence": (
                    "strace-path-filtered-fsync-delay-enter+sigstop"
                ),
                "traced_agent_at_arm": True,
                "agent_sigstop_at_arm": True,
            }
        )
    (root / "campaign.json").write_text(
        json.dumps(campaign, sort_keys=True) + "\n", encoding="utf-8"
    )


def self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="iotox-power-cut-verifier-") as directory:
        root = Path(directory) / "proof"
        write_fixture(root)
        verify(root)
        legacy = Path(directory) / "proof-v2"
        write_fixture(legacy, version=2)
        verify(legacy)
        post_exchange = Path(directory) / "proof-v3-post-exchange"
        write_fixture(
            post_exchange, version=3, boundary="post-exchange-pending"
        )
        verify(post_exchange)
        receive_staging = Path(directory) / "proof-v4-receive-staging"
        write_fixture(
            receive_staging, version=4, boundary="receive-staging-partial"
        )
        verify(receive_staging)
        cas_install = Path(directory) / "proof-v4-cas-install"
        write_fixture(
            cas_install, version=4, boundary="cas-install-temporary"
        )
        cas_arm_path = (
            cas_install
            / "epoch-1/live/workspace-export/power-cut/armed.json"
        )
        cas_arm = json.loads(cas_arm_path.read_text(encoding="utf-8"))
        cas_arm["temporary_bytes_at_arm"] = 32 * 1024 * 1024
        cas_arm_path.write_text(json.dumps(cas_arm) + "\n", encoding="utf-8")
        cas_campaign_path = cas_install / "campaign.json"
        cas_campaign = json.loads(cas_campaign_path.read_text(encoding="utf-8"))
        cas_campaign["temporary_bytes_at_arm"] = 32 * 1024 * 1024
        cas_relative = str(cas_arm_path.relative_to(cas_install))
        cas_campaign["files"][cas_relative] = {
            "bytes": cas_arm_path.stat().st_size,
            "sha256": sha256_file(cas_arm_path),
        }
        cas_campaign_path.write_text(
            json.dumps(cas_campaign) + "\n", encoding="utf-8"
        )
        verify(cas_install)
        for boundary in (
            "manifest-install-temporary",
            "branch-record-install-temporary",
            "branch-pointer-update-temporary",
        ):
            publication = Path(directory) / f"proof-v5-{boundary}"
            write_fixture(publication, version=5, boundary=boundary)
            verify(publication)
        for boundary in (
            "manifest-install-directory-fsync",
            "branch-record-install-directory-fsync",
            "branch-pointer-update-directory-fsync",
        ):
            publication = Path(directory) / f"proof-v6-old-{boundary}"
            write_fixture(publication, version=6, boundary=boundary)
            verify(publication)

            recovered = Path(directory) / f"proof-v6-new-{boundary}"
            write_fixture(recovered, version=6, boundary=boundary)
            recovery_path = (
                recovered
                / "epoch-2/live/workspace-export/guest-receipts/iotox/"
                "sync-power-cut.json"
            )
            recovery = json.loads(recovery_path.read_text(encoding="utf-8"))
            before = recovery["publication_before_restart"]
            selected = {
                "manifest-install-directory-fsync": "manifest",
                "branch-record-install-directory-fsync": "branch_record",
                "branch-pointer-update-directory-fsync": "branch_pointer",
            }[boundary]
            before[f"{selected}_state"] = (
                "successor" if selected == "branch_pointer" else "exact"
            )
            before[f"{selected}_temporary_count"] = 0
            before[f"{selected}_temporary_bytes"] = 0
            recovery_path.write_text(
                json.dumps(recovery, sort_keys=True) + "\n", encoding="utf-8"
            )
            campaign_path = recovered / "campaign.json"
            campaign = json.loads(campaign_path.read_text(encoding="utf-8"))
            relative = str(recovery_path.relative_to(recovered))
            campaign["files"][relative] = {
                "bytes": recovery_path.stat().st_size,
                "sha256": sha256_file(recovery_path),
            }
            campaign_path.write_text(
                json.dumps(campaign, sort_keys=True) + "\n", encoding="utf-8"
            )
            verify(recovered)
        publication_absent = Path(directory) / "proof-v5-temporary-absent"
        write_fixture(
            publication_absent,
            version=5,
            boundary="manifest-install-temporary",
        )
        publication_recovery_path = (
            publication_absent
            / "epoch-2/live/workspace-export/guest-receipts/iotox/sync-power-cut.json"
        )
        publication_recovery = json.loads(
            publication_recovery_path.read_text(encoding="utf-8")
        )
        publication_recovery["publication_before_restart"].update(
            {
                "manifest_temporary_count": 0,
                "manifest_temporary_bytes": 0,
            }
        )
        publication_recovery_path.write_text(
            json.dumps(publication_recovery) + "\n", encoding="utf-8"
        )
        publication_campaign_path = publication_absent / "campaign.json"
        publication_campaign = json.loads(
            publication_campaign_path.read_text(encoding="utf-8")
        )
        publication_relative = str(
            publication_recovery_path.relative_to(publication_absent)
        )
        publication_campaign["files"][publication_relative] = {
            "bytes": publication_recovery_path.stat().st_size,
            "sha256": sha256_file(publication_recovery_path),
        }
        publication_campaign_path.write_text(
            json.dumps(publication_campaign) + "\n", encoding="utf-8"
        )
        verify(publication_absent)
        recovery_path = (
            root
            / "epoch-2/live/workspace-export/guest-receipts/iotox/sync-power-cut.json"
        )
        recovery = json.loads(recovery_path.read_text(encoding="utf-8"))
        recovery["initial_view_per_node"] = ["completed", "completed", "hybrid"]
        recovery_path.write_text(json.dumps(recovery) + "\n", encoding="utf-8")
        campaign_path = root / "campaign.json"
        campaign = json.loads(campaign_path.read_text(encoding="utf-8"))
        relative = str(recovery_path.relative_to(root))
        campaign["files"][relative] = {
            "bytes": recovery_path.stat().st_size,
            "sha256": sha256_file(recovery_path),
        }
        campaign_path.write_text(json.dumps(campaign) + "\n", encoding="utf-8")
        try:
            verify(root)
        except ValueError:
            pass
        else:
            raise ValueError("tampered power-cut recovery receipt passed")
    print("sync-power-cut-sandwurm-verifier-self-test=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("proof_root", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if args.proof_root is None:
        parser.error("proof_root is required")
    print(json.dumps(verify(args.proof_root), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"sync power-cut verification failed: {error}", file=sys.stderr)
        raise SystemExit(1)
