#!/usr/bin/env python3
"""Verify the content-free three-writer receipt from one Sandwurm guest."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tempfile
from pathlib import Path


def load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as source:
        result = json.load(source)
    if not isinstance(result, dict):
        raise ValueError(f"JSON root is not an object: {path}")
    return result


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def is_sha256(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def require_int_list(value: object, length: int, field: str, *, minimum: int = 0) -> list[int]:
    require(
        isinstance(value, list)
        and len(value) == length
        and all(isinstance(item, int) and item >= minimum for item in value),
        f"{field} is invalid",
    )
    return value


def require_soak_projection_list(value: object, field: str) -> list[dict[str, object]]:
    require(
        isinstance(value, list) and len(value) == 3,
        f"{field} is invalid",
    )
    result: list[dict[str, object]] = []
    for item in value:
        require(isinstance(item, dict), f"{field} entry is invalid")
        normalized: dict[str, object] = {}
        for name in ("current", "toggle"):
            exists = item.get(f"{name}_exists")
            size = item.get(f"{name}_bytes")
            digest = item.get(f"{name}_sha256")
            require(isinstance(exists, bool), f"{field}.{name}_exists is invalid")
            require(
                isinstance(size, int) and size >= 0,
                f"{field}.{name}_bytes is invalid",
            )
            if exists:
                require(is_sha256(digest), f"{field}.{name}_sha256 is invalid")
            else:
                require(
                    size == 0 and digest == "",
                    f"{field}.{name} absence evidence is invalid",
                )
            normalized[f"{name}_exists"] = exists
            normalized[f"{name}_bytes"] = size
            normalized[f"{name}_sha256"] = digest
        result.append(normalized)
    return result


def require_soak_stalled_recovery_events(
    value: object, count: int, field: str
) -> list[dict[str, object]]:
    require(
        isinstance(value, list) and len(value) == count,
        f"{field} is invalid",
    )
    result: list[dict[str, object]] = []
    for event in value:
        require(isinstance(event, dict), f"{field} entry is invalid")
        cycle = event.get("cycle")
        writer = event.get("writer")
        targets = event.get("targets")
        channel_rows = event.get("wait_channels_by_node")
        require(
            isinstance(cycle, int)
            and 1 <= cycle <= 200000
            and writer in ("a", "b", "c")
            and isinstance(targets, list)
            and 1 <= len(targets) <= 3
            and len(set(targets)) == len(targets)
            and all(target in ("a", "b", "c") for target in targets)
            and isinstance(channel_rows, list)
            and len(channel_rows) == len(targets),
            f"{field} shape is invalid",
        )
        normalized_rows: list[dict[str, object]] = []
        for row in channel_rows:
            require(isinstance(row, dict), f"{field}.wait row is invalid")
            node = row.get("node")
            channels = row.get("wait_channels")
            require(
                node in targets
                and isinstance(channels, list)
                and bool(channels)
                and all(
                    isinstance(channel, str)
                    and re.fullmatch(r"[A-Za-z0-9_.-]{1,128}", channel)
                    for channel in channels
                ),
                f"{field}.wait_channels is invalid",
            )
            normalized_rows.append(
                {"node": node, "wait_channels": list(channels)}
            )
        result.append(
            {
                "cycle": cycle,
                "writer": writer,
                "targets": list(targets),
                "wait_channels_by_node": normalized_rows,
            }
        )
    return result


def require_soak_repair_policy(value: object, field: str) -> str:
    require(value in ("defer", "coincident"), f"{field} is invalid")
    return str(value)


def require_soak_stalled_restart_after_ms(value: object, field: str) -> int:
    require(
        isinstance(value, int) and 0 <= value <= 7 * 86400 * 1000,
        f"{field} is invalid",
    )
    return value


def require_soak_restart_settle_policy(value: object, field: str) -> str:
    require(value in ("none", "repair-before-edit"), f"{field} is invalid")
    return str(value)


def require_soak_final_boundary_restart_policy(value: object, field: str) -> str:
    require(value in ("allow", "skip-if-floor-satisfied"), f"{field} is invalid")
    return str(value)


def require_soak_restart_settle(
    record: dict,
    max_cycle: int,
    restart_count: int,
    prefix: str,
    *,
    completed: bool,
) -> tuple[str | None, int | None, list[int] | None]:
    policy = None
    if "soak_restart_settle_policy" in record:
        policy = require_soak_restart_settle_policy(
            record["soak_restart_settle_policy"],
            f"{prefix}.soak_restart_settle_policy",
        )
    fields_present = (
        "soak_restart_settle_passes" in record
        or "soak_restart_settle_cycles" in record
    )
    if not fields_present:
        return policy, None, None
    passes = record.get("soak_restart_settle_passes")
    cycles = record.get("soak_restart_settle_cycles")
    require(
        isinstance(passes, int) and 0 <= passes <= restart_count,
        f"{prefix}.soak_restart_settle_passes is invalid",
    )
    require(
        isinstance(cycles, list)
        and len(cycles) == passes
        and len(set(cycles)) == len(cycles)
        and all(
            isinstance(cycle, int)
            and 1 <= cycle <= max_cycle
            for cycle in cycles
        ),
        f"{prefix}.soak_restart_settle_cycles is invalid",
    )
    if policy == "none":
        require(passes == 0, f"{prefix}.soak_restart_settle_passes is nonzero")
    if policy == "repair-before-edit" and completed:
        require(
            passes == restart_count,
            f"{prefix}.soak_restart_settle_passes did not match restarts",
        )
    return policy, passes, cycles


def require_soak_final_boundary_restart_skips(
    record: dict,
    max_cycle: int,
    minimum_cycles: int,
    restart_every: int,
    prefix: str,
) -> tuple[str | None, int | None, list[int] | None]:
    policy = None
    if "soak_final_boundary_restart_policy" in record:
        policy = require_soak_final_boundary_restart_policy(
            record["soak_final_boundary_restart_policy"],
            f"{prefix}.soak_final_boundary_restart_policy",
        )
    fields_present = (
        "soak_restart_skipped_final_boundary" in record
        or "soak_restart_skipped_cycles" in record
    )
    if not fields_present:
        return policy, None, None
    count = record.get("soak_restart_skipped_final_boundary")
    cycles = record.get("soak_restart_skipped_cycles")
    require(
        isinstance(count, int) and 0 <= count <= 1,
        f"{prefix}.soak_restart_skipped_final_boundary is invalid",
    )
    require(
        isinstance(cycles, list)
        and len(cycles) == count
        and len(set(cycles)) == len(cycles)
        and all(
            isinstance(cycle, int)
            and 1 <= cycle <= max_cycle
            and cycle >= minimum_cycles
            and restart_every > 0
            and cycle % restart_every == 0
            for cycle in cycles
        ),
        f"{prefix}.soak_restart_skipped_cycles is invalid",
    )
    if policy == "allow":
        require(count == 0, f"{prefix}.soak_restart_skipped_final_boundary is nonzero")
    if count > 0:
        require(
            policy == "skip-if-floor-satisfied",
            f"{prefix}.soak_final_boundary_restart_policy did not permit skip",
        )
    return policy, count, cycles


def require_soak_repair_deferrals(
    record: dict,
    max_cycle: int,
    prefix: str,
) -> list[int]:
    count = record.get("soak_repair_deferrals")
    cycles = record.get("soak_repair_deferred_cycles")
    require(
        isinstance(count, int) and count >= 0,
        f"{prefix}.soak_repair_deferrals is invalid",
    )
    require(
        isinstance(cycles, list)
        and len(cycles) == count
        and len(set(cycles)) == len(cycles)
        and all(
            isinstance(cycle, int)
            and 1 <= cycle <= max_cycle
            for cycle in cycles
        ),
        f"{prefix}.soak_repair_deferred_cycles is invalid",
    )
    return cycles


RECONCILE_APPLY_FIELDS = (
    "branch_advances",
    "cas_inspected",
    "cas_inspected_bytes",
    "cas_installed",
    "cas_installed_bytes",
    "cas_reused",
    "local_events",
    "projection_bytes",
    "projection_conflict_files",
    "projection_conflict_tombstones",
    "projection_dirs",
    "projection_files",
    "projection_preserved_bytes",
    "projection_preserved_dirs",
    "projection_preserved_entries",
    "projection_preserved_files",
    "source_hashed",
    "source_inspected",
    "source_reused",
)


PARTIAL_TREE_V2_PULL_FIELDS = (
    "jobs",
    "awaiting_inventory",
    "awaiting_object",
    "complete",
    "failed",
    "cancelled",
    "manifest_file_objects",
    "selected_file_objects",
    "skipped_file_objects",
    "selected_paths",
    "skipped_paths",
    "sources",
    "availability_requests",
    "availability_results",
    "absent_results",
    "unavailable_results",
    "active_lanes",
    "staged_file_objects",
    "file_commit_batches",
    "largest_file_commit_batch",
    "cas_full_inventory_scans",
    "cas_inventory_objects_inspected",
    "requested_objects",
    "committed_objects",
    "reused_objects",
    "fetched_bytes",
    "accepted_branches",
    "conflicts",
    "lane_records",
    "lane_admitted",
    "lane_bytes",
    "source_records",
    "source_online",
    "source_requested",
    "source_offered",
    "source_absent",
    "source_unavailable",
    "source_committed",
    "source_fetched_bytes",
)


def require_reconcile_apply_list(value: object, field: str) -> list[dict[str, int]]:
    require(
        isinstance(value, list) and len(value) == 3,
        f"{field} is invalid",
    )
    result: list[dict[str, int]] = []
    for item in value:
        require(isinstance(item, dict), f"{field} entry is invalid")
        normalized: dict[str, int] = {}
        for key in RECONCILE_APPLY_FIELDS:
            number = item.get(key)
            require(
                isinstance(number, int) and number >= 0,
                f"{field}.{key} is invalid",
            )
            normalized[key] = number
        result.append(normalized)
    return result


def require_partial_tree_v2_pull_summary_list(
    value: object, field: str
) -> list[dict[str, int]]:
    require(
        isinstance(value, list) and len(value) == 3,
        f"{field} is invalid",
    )
    result: list[dict[str, int]] = []
    for item in value:
        require(isinstance(item, dict), f"{field} entry is invalid")
        normalized: dict[str, int] = {}
        for key in PARTIAL_TREE_V2_PULL_FIELDS:
            number = item.get(key)
            require(
                isinstance(number, int) and number >= 0,
                f"{field}.{key} is invalid",
            )
            normalized[key] = number
        require(
            normalized["active_lanes"] <= normalized["lane_records"],
            f"{field}.active_lanes exceeds lane_records",
        )
        require(
            normalized["lane_admitted"] <= normalized["lane_records"],
            f"{field}.lane_admitted exceeds lane_records",
        )
        require(
            normalized["source_online"] <= normalized["source_records"],
            f"{field}.source_online exceeds source_records",
        )
        result.append(normalized)
    return result


def require_networkless_launch(launch: dict) -> None:
    require(
        launch.get("network", {}).get("class") == "none"
        and launch.get("network", {}).get("mode") == "none",
        "three-writer qualification was not networkless",
    )
    argv = launch.get("vmm", {}).get("argv", [])
    require(
        not any(
            isinstance(argument, str)
            and (argument == "--net" or argument.startswith("--net="))
            for argument in argv
        ),
        "networkless launch contains a VMM network device",
    )


def require_sync_receipt_boundary(chain: dict) -> str:
    if chain.get("status") == "guest-evidence-observed" and chain.get("failure") is None:
        return "sandwurm-guest-evidence"

    failure = chain.get("failure")
    blockers = failure.get("blockers") if isinstance(failure, dict) else None
    receipts = chain.get("receipts")
    live_launch = receipts.get("live_launch") if isinstance(receipts, dict) else None
    guest_evidence = chain.get("guest_evidence")
    missing_legacy = (
        guest_evidence.get("missing_legacy_guest_receipts")
        if isinstance(guest_evidence, dict)
        else None
    )
    require(
        chain.get("status") == "launched-without-guest-evidence"
        and isinstance(blockers, list)
        and blockers == ["guest-evidence-not-observed"]
        and isinstance(live_launch, dict)
        and live_launch.get("status") == "exited"
        and (
            not isinstance(guest_evidence, dict)
            or (
                guest_evidence.get("observed") is False
                and (
                    missing_legacy is None
                    or "task-receipt.json" in missing_legacy
                )
            )
        ),
        "Sandwurm did not accept the guest boundary or a completed IoTox domain receipt",
    )
    return "iotox-domain-receipt"


def verify_rejected(proof_root: Path, chain: dict, launch: dict, evidence: dict) -> dict:
    del launch
    require(
        chain.get("status") in ("guest-evidence-observed", "launched-without-guest-evidence"),
        "Sandwurm did not launch the rejected guest",
    )
    live_launch = chain.get("receipts", {}).get("live_launch", {})
    require(
        isinstance(live_launch, dict) and live_launch.get("status") == "exited",
        "rejected guest did not exit through the VMM wrapper",
    )
    require(evidence.get("schema") == "iotox.sync-three-writer.v1", "bad schema")
    require(evidence.get("status") == "rejected", "receipt is not rejected")
    failure = evidence.get("failure")
    require(isinstance(failure, str) and 1 <= len(failure) <= 256, "failure is invalid")
    require(
        evidence.get("failure_sha256")
        == hashlib.sha256(failure.encode("utf-8")).hexdigest(),
        "failure digest does not bind the failure string",
    )
    require(evidence.get("contains_secrets") is False, "receipt is not content-free")
    require(evidence.get("node_count") == 3, "node count is not three")
    require(
        isinstance(evidence.get("state_reused"), bool),
        "state-reuse evidence is invalid",
    )
    require(
        is_sha256(evidence.get("namespace_sha256")),
        "namespace digest is invalid",
    )
    capacity_files = evidence.get("capacity_files")
    capacity_file_bytes = evidence.get("capacity_file_bytes")
    capacity_logical_bytes = evidence.get("capacity_logical_bytes")
    require(
        evidence.get("capacity_campaign") is True
        and isinstance(capacity_files, int)
        and 1 <= capacity_files <= 3500
        and isinstance(capacity_file_bytes, int)
        and 1 <= capacity_file_bytes <= 1024 * 1024
        and capacity_logical_bytes == capacity_files * capacity_file_bytes
        and capacity_logical_bytes <= 56 * 1024 * 1024,
        "capacity population is invalid",
    )
    require(
        isinstance(evidence.get("elapsed_ms"), int)
        and evidence["elapsed_ms"] > 0,
        "elapsed time is invalid",
    )
    tree_lane_cap = evidence.get("tree_lane_cap", 0)
    process_tree_lane_cap = evidence.get("tree_lane_process_cap", tree_lane_cap)
    namespace_tree_lane_cap = evidence.get("tree_lane_namespace_cap", tree_lane_cap)
    require(
        isinstance(tree_lane_cap, int)
        and 0 <= tree_lane_cap <= 64
        and isinstance(process_tree_lane_cap, int)
        and 0 <= process_tree_lane_cap <= 64
        and isinstance(namespace_tree_lane_cap, int)
        and 0 <= namespace_tree_lane_cap <= 64
        and tree_lane_cap == min(process_tree_lane_cap, namespace_tree_lane_cap),
        "tree lane cap split evidence is invalid",
    )
    branch_count = require_int_list(
        evidence.get("partial_branch_count_per_node"),
        3,
        "partial_branch_count_per_node",
    )
    conflict_alternatives = require_int_list(
        evidence.get("partial_conflict_alternatives_per_node"),
        3,
        "partial_conflict_alternatives_per_node",
    )
    high_water = require_int_list(
        evidence.get("partial_agent_high_water_kib"),
        3,
        "partial_agent_high_water_kib",
    )
    capacity_shape = evidence.get("partial_capacity_shape_per_node")
    require(
        isinstance(capacity_shape, list) and len(capacity_shape) == 3,
        "partial capacity shape is invalid",
    )
    for shape in capacity_shape:
        require(
            isinstance(shape, dict)
            and isinstance(shape.get("files"), int)
            and 0 <= shape["files"] <= capacity_files
            and isinstance(shape.get("bytes"), int)
            and shape["bytes"] == shape["files"] * capacity_file_bytes,
            "one partial capacity shape is invalid",
        )
    if failure.startswith("timeout waiting for capacity population on all three writers"):
        require(
            any(shape["files"] < capacity_files for shape in capacity_shape),
            "rejected capacity shape unexpectedly reached full projection",
        )
    store_shape = evidence.get("partial_tree_v2_store_shape_per_node")
    require(
        isinstance(store_shape, list) and len(store_shape) == 3,
        "partial tree-v2 store shape is invalid",
    )
    store_fields = (
        "branch_bytes",
        "branches",
        "incoming_bytes",
        "incoming_files",
        "manifest_bytes",
        "manifests",
        "object_bytes",
        "objects",
        "record_bytes",
        "records",
    )
    for shape in store_shape:
        require(
            isinstance(shape, dict)
            and all(isinstance(shape.get(field), int) and shape[field] >= 0 for field in store_fields),
            "one partial tree-v2 store shape is invalid",
        )
    pull_summary: list[dict[str, int]] = []
    if "partial_tree_v2_pull_summary_per_node" in evidence:
        pull_summary = require_partial_tree_v2_pull_summary_list(
            evidence.get("partial_tree_v2_pull_summary_per_node"),
            "partial_tree_v2_pull_summary_per_node",
        )
    soak_projection: list[dict[str, object]] = []
    if "partial_soak_projection_per_node" in evidence:
        soak_projection = require_soak_projection_list(
            evidence.get("partial_soak_projection_per_node"),
            "partial_soak_projection_per_node",
        )
    partial_soak_stalled_recoveries = 0
    partial_soak_stalled_restart_after_ms = (
        require_soak_stalled_restart_after_ms(
            evidence["soak_stalled_restart_after_ms"],
            "soak_stalled_restart_after_ms",
        )
        if "soak_stalled_restart_after_ms" in evidence
        else None
    )
    partial_soak_restart_settle_passes = 0
    stage_events = evidence.get("stage_events")
    require(
        isinstance(stage_events, list) and len(stage_events) >= 4,
        "stage history is invalid",
    )
    for event in stage_events:
        require(
            isinstance(event, dict)
            and isinstance(event.get("elapsed_ms"), int)
            and event["elapsed_ms"] >= 0
            and isinstance(event.get("message"), str)
            and 1 <= len(event["message"]) <= 256,
            "one stage event is invalid",
        )
    partial_soak = evidence.get("partial_soak_evidence")
    retained_branch_convergence = any(
        event.get("message") == "three signed branches converged"
        for event in stage_events
    )
    top_level_soak_cycles = evidence.get("soak_cycles", 0)
    partial_soak_cycles = (
        partial_soak.get("soak_cycles", 0)
        if isinstance(partial_soak, dict)
        else 0
    )
    partial_soak_minimum_cycles = (
        partial_soak.get("soak_minimum_cycles", 0)
        if isinstance(partial_soak, dict)
        else 0
    )
    completed_soak_rejection = (
        isinstance(partial_soak, dict)
        and partial_soak.get("soak_campaign") is True
        and partial_soak.get("soak_completed") is True
        and isinstance(top_level_soak_cycles, int)
        and isinstance(partial_soak_cycles, int)
        and isinstance(partial_soak_minimum_cycles, int)
        and max(top_level_soak_cycles, partial_soak_cycles)
        >= partial_soak_minimum_cycles
        and len(soak_projection) == 3
        and len({
            (
                projection.get("current_sha256"),
                projection.get("toggle_exists"),
                projection.get("toggle_sha256"),
            )
            for projection in soak_projection
        })
        == 1
        and conflict_alternatives == [0, 0, 0]
    )
    require(
        retained_branch_convergence
        or (
            isinstance(partial_soak, dict)
            and partial_soak.get("soak_campaign") is True
            and isinstance(top_level_soak_cycles, int)
            and isinstance(partial_soak_cycles, int)
            and max(top_level_soak_cycles, partial_soak_cycles) > 0
            and branch_count == [3, 3, 3]
        )
        or completed_soak_rejection,
        "rejected run lacks retained branch convergence or later soak evidence",
    )
    require(
        isinstance(evidence.get("shadow_cycles", 0), int)
        and evidence.get("shadow_cycles", 0) >= 0
        and isinstance(evidence.get("maintenance_lifecycle_requested", False), bool),
        "rejected follow-up flags are invalid",
    )
    if partial_soak is not None:
        require(isinstance(partial_soak, dict), "partial soak evidence is invalid")
        require(
            isinstance(partial_soak.get("soak_campaign"), bool)
            and isinstance(partial_soak.get("soak_completed", False), bool)
            and isinstance(partial_soak.get("soak_contains_secrets"), bool)
            and partial_soak.get("soak_contains_secrets") is False,
            "partial soak flags are invalid",
        )
        if partial_soak.get("soak_campaign"):
            for field in (
                "soak_requested_seconds",
                "soak_minimum_cycles",
                "soak_cycle_delay_ms",
                "soak_restart_every",
                "soak_repair_every",
                "soak_cycles",
                "soak_elapsed_ms",
                "soak_daemon_restarts",
                "soak_repair_passes",
                "soak_delete_cycles",
            ):
                value = partial_soak.get(field)
                require(
                    isinstance(value, int) and value >= 0,
                    f"partial {field} is invalid",
                )
            if "soak_restart_phase" in partial_soak:
                require(
                    partial_soak["soak_restart_phase"]
                    in ("none", "before-edit", "after-edit"),
                    "partial soak restart phase is invalid",
                )
            _, settle_passes, _ = require_soak_restart_settle(
                partial_soak,
                200000,
                partial_soak.get("soak_daemon_restarts", 0),
                "partial_soak_evidence",
                completed=False,
            )
            if settle_passes is not None:
                partial_soak_restart_settle_passes = settle_passes
            require_soak_final_boundary_restart_skips(
                partial_soak,
                200000,
                partial_soak.get("soak_minimum_cycles", 0),
                partial_soak.get("soak_restart_every", 0),
                "partial_soak_evidence",
            )
            if "soak_repair_restart_policy" in partial_soak:
                require_soak_repair_policy(
                    partial_soak["soak_repair_restart_policy"],
                    "partial_soak_evidence.soak_repair_restart_policy",
                )
            if "sync_repair_control_timeout_ms" in partial_soak:
                control_timeout = partial_soak["sync_repair_control_timeout_ms"]
                require(
                    isinstance(control_timeout, int)
                    and 5000 <= control_timeout <= 600000,
                    "partial sync-repair control timeout is invalid",
                )
            if "soak_stalled_restart_after_ms" in partial_soak:
                partial_soak_stalled_restart_after_ms = (
                    require_soak_stalled_restart_after_ms(
                        partial_soak["soak_stalled_restart_after_ms"],
                        "partial_soak_evidence.soak_stalled_restart_after_ms",
                    )
                )
            if "soak_repair_pending" in partial_soak:
                require(
                    isinstance(partial_soak["soak_repair_pending"], bool),
                    "partial soak repair pending flag is invalid",
                )
            if (
                "soak_repair_deferrals" in partial_soak
                or "soak_repair_deferred_cycles" in partial_soak
            ):
                require_soak_repair_deferrals(
                    partial_soak,
                    200000,
                    "partial_soak_evidence",
                )
            if partial_soak.get("soak_cycles", 0) > 0:
                require(
                    isinstance(partial_soak.get("soak_last_cycle_ms"), int)
                    and partial_soak["soak_last_cycle_ms"] >= 0
                    and re.fullmatch(
                        r"[0-9a-f]{64}",
                        partial_soak.get("soak_final_sha256", ""),
                    )
                    is not None,
                    "partial soak cycle evidence is invalid",
                )
            if "soak_agent_high_water_kib" in partial_soak:
                high_water = partial_soak["soak_agent_high_water_kib"]
                require(
                    isinstance(high_water, list)
                    and len(high_water) == 3
                    and all(
                        isinstance(value, int) and value > 0
                        for value in high_water
                    ),
                    "partial soak high-water evidence is invalid",
                )
            if "soak_restart_targets" in partial_soak:
                targets = partial_soak["soak_restart_targets"]
                require(
                    isinstance(targets, list)
                    and len(targets) == partial_soak.get("soak_daemon_restarts")
                    and all(target in ("a", "b", "c") for target in targets),
                    "partial soak restart-target evidence is invalid",
                )
            recovery_fields_present = (
                "soak_stalled_cycle_recoveries" in partial_soak
                or "soak_stalled_cycle_recovery_events" in partial_soak
            )
            if recovery_fields_present:
                recovery_count = partial_soak.get("soak_stalled_cycle_recoveries")
                require(
                    isinstance(recovery_count, int)
                    and 0 <= recovery_count <= partial_soak.get("soak_cycles", 0),
                    "partial soak stalled-recovery count is invalid",
                )
                require_soak_stalled_recovery_events(
                    partial_soak.get("soak_stalled_cycle_recovery_events"),
                    recovery_count,
                    "partial_soak_evidence.soak_stalled_cycle_recovery_events",
                )
                partial_soak_stalled_recoveries = recovery_count
    return {
        "schema": "iotox.sync-three-writer-sandwurm-verification.v1",
        "status": "rejected",
        "proof_root": str(proof_root),
        "failure_sha256": evidence["failure_sha256"],
        "node_count": 3,
        "branch_count_per_node": branch_count,
        "conflict_alternatives_per_node": conflict_alternatives,
        "partial_capacity_shape_per_node": capacity_shape,
        "partial_tree_v2_store_shape_per_node": store_shape,
        "partial_tree_v2_pull_summary_per_node": pull_summary,
        "partial_soak_projection_per_node": soak_projection,
        "partial_agent_high_water_kib": high_water,
        "shadow_cycles": evidence.get("shadow_cycles", 0),
        "partial_soak_cycles": (
            partial_soak.get("soak_cycles", 0)
            if isinstance(partial_soak, dict)
            else 0
        ),
        "partial_soak_stalled_restart_after_ms": partial_soak_stalled_restart_after_ms,
        "partial_soak_restart_settle_passes": partial_soak_restart_settle_passes,
        "partial_soak_stalled_cycle_recoveries": partial_soak_stalled_recoveries,
        "tree_lane_cap": tree_lane_cap,
        "tree_lane_process_cap": process_tree_lane_cap,
        "tree_lane_namespace_cap": namespace_tree_lane_cap,
        "capacity_campaign": True,
        "capacity_files": capacity_files,
        "capacity_logical_bytes": capacity_logical_bytes,
        "capacity_catchup_ms": 0,
        "elapsed_ms": evidence["elapsed_ms"],
        "network_class": "none",
        "vm_substrate": "cloud-hypervisor",
        "contains_secrets": False,
    }


def verify(proof_root: Path) -> dict:
    proof_root = proof_root.resolve()
    chain = load(proof_root / "direct-cloud-hypervisor-live-chain.json")
    launch = load(proof_root / "prelaunch/launch/cloud-hypervisor-launch.json")
    evidence = load(
        proof_root
        / "live/workspace-export/guest-receipts/iotox/sync-three-writer.json"
    )
    require_networkless_launch(launch)
    if evidence.get("status") == "rejected":
        return verify_rejected(proof_root, chain, launch, evidence)
    evidence_boundary = require_sync_receipt_boundary(chain)
    require(evidence.get("schema") == "iotox.sync-three-writer.v1", "bad schema")
    require(evidence.get("status") == "passed", "qualification did not pass")
    require(evidence.get("node_count") == 3, "node count is not three")
    require(evidence.get("friendship_edge_count") == 3, "friendship triangle is incomplete")
    require(
        evidence.get("directed_read_write_share_count") == 6,
        "six directional grants were not observed",
    )
    require(
        evidence.get("source_principals_per_node") == 2,
        "every node does not name both remote principals",
    )
    require(
        evidence.get("branch_count_per_node") == [3, 3, 3],
        "three branches did not reach every node",
    )
    require(
        evidence.get("conflict_alternatives_per_node") == [2, 2, 2]
        and evidence.get("three_way_conflict_observed") is True,
        "three-way conflict material is incomplete",
    )
    require(
        evidence.get("explicit_resolution_observed") is True,
        "explicit resolution did not converge",
    )
    require(
        evidence.get("automation_record_format") == 2
        and evidence.get("automation_record_bytes") == 4808,
        "automation-v2 record evidence is wrong",
    )
    attempts = evidence.get("periodic_attempts_per_node")
    require(
        isinstance(attempts, list)
        and len(attempts) == 3
        and all(isinstance(value, int) and value >= 2 for value in attempts),
        "each node did not schedule both peers",
    )
    for field in ("tox_key_sha256", "principal_sha256"):
        values = evidence.get(field)
        require(
            isinstance(values, list)
            and len(values) == 3
            and len(set(values)) == 3
            and all(re.fullmatch(r"[0-9a-f]{64}", value) for value in values),
            f"{field} does not prove three distinct identities",
        )
    require(
        re.fullmatch(r"[0-9a-f]{64}", evidence.get("resolved_sha256", ""))
        is not None,
        "resolved digest is invalid",
    )
    require(
        re.fullmatch(r"[0-9a-f]{64}", evidence.get("namespace_sha256", ""))
        is not None,
        "namespace digest is invalid",
    )
    require(
        isinstance(evidence.get("elapsed_ms"), int)
        and evidence["elapsed_ms"] > 0,
        "elapsed time is invalid",
    )
    require(
        isinstance(evidence.get("state_reused"), bool),
        "state-reuse evidence is invalid",
    )
    tree_lane_cap = evidence.get("tree_lane_cap", 0)
    require(
        isinstance(tree_lane_cap, int) and 0 <= tree_lane_cap <= 64,
        "tree lane cap evidence is invalid",
    )
    process_tree_lane_cap = evidence.get(
        "tree_lane_process_cap", tree_lane_cap
    )
    namespace_tree_lane_cap = evidence.get(
        "tree_lane_namespace_cap", tree_lane_cap
    )
    require(
        isinstance(process_tree_lane_cap, int)
        and 0 <= process_tree_lane_cap <= 64
        and isinstance(namespace_tree_lane_cap, int)
        and 0 <= namespace_tree_lane_cap <= 64
        and tree_lane_cap == min(process_tree_lane_cap, namespace_tree_lane_cap),
        "tree lane cap split evidence is invalid",
    )
    require(
        isinstance(evidence.get("shadow_cycles", 0), int)
        and evidence.get("shadow_cycles", 0) >= 0
        and isinstance(evidence.get("shadow_elapsed_ms", 0), int)
        and evidence.get("shadow_elapsed_ms", 0) >= 0,
        "shadow evidence is invalid",
    )
    restart_count = evidence.get("stalled_cycle_restarts")
    restart_events = evidence.get("stalled_cycle_restart_events")
    require(
        isinstance(restart_count, int)
        and 0 <= restart_count <= evidence.get("shadow_cycles", 0)
        and isinstance(restart_events, list)
        and len(restart_events) == restart_count,
        "stalled-cycle recovery evidence is invalid",
    )
    for event in restart_events:
        require(
            isinstance(event, dict)
            and isinstance(event.get("cycle"), int)
            and 1 <= event["cycle"] <= evidence.get("shadow_cycles", 0)
            and event.get("writer") in ("a", "b", "c")
            and isinstance(event.get("wait_channels"), list)
            and bool(event["wait_channels"])
            and all(
                isinstance(value, str)
                and re.fullmatch(r"[A-Za-z0-9_.-]{1,128}", value)
                for value in event["wait_channels"]
            ),
            "one stalled-cycle recovery event is invalid",
        )
    soak_campaign = evidence.get("soak_campaign", False)
    require(isinstance(soak_campaign, bool), "soak campaign flag is invalid")
    if soak_campaign:
        soak_requested_seconds = evidence.get("soak_requested_seconds")
        soak_minimum_cycles = evidence.get("soak_minimum_cycles")
        soak_cycles = evidence.get("soak_cycles")
        soak_elapsed_ms = evidence.get("soak_elapsed_ms")
        soak_high_water = evidence.get("soak_agent_high_water_kib")
        require(
            isinstance(soak_requested_seconds, int)
            and 0 <= soak_requested_seconds <= 7 * 86400
            and isinstance(soak_minimum_cycles, int)
            and 0 <= soak_minimum_cycles <= 200000
            and isinstance(soak_cycles, int)
            and soak_cycles >= max(1, soak_minimum_cycles)
            and isinstance(soak_elapsed_ms, int)
            and soak_elapsed_ms >= soak_requested_seconds * 1000,
            "soak duration/cycle evidence is invalid",
        )
        for field in (
            "soak_cycle_delay_ms",
            "soak_restart_every",
            "soak_repair_every",
            "soak_daemon_restarts",
            "soak_repair_passes",
            "soak_delete_cycles",
            "soak_cycle_ms_min",
            "soak_cycle_ms_median",
            "soak_cycle_ms_max",
        ):
            value = evidence.get(field)
            require(
                isinstance(value, int) and value >= 0,
                f"{field} is invalid",
            )
        if "soak_restart_phase" in evidence:
            require(
                evidence["soak_restart_phase"]
                in ("none", "before-edit", "after-edit"),
                "soak restart phase is invalid",
            )
        require_soak_restart_settle(
            evidence,
            soak_cycles,
            evidence["soak_daemon_restarts"],
            "soak evidence",
            completed=True,
        )
        require_soak_final_boundary_restart_skips(
            evidence,
            soak_cycles,
            soak_minimum_cycles,
            evidence["soak_restart_every"],
            "soak evidence",
        )
        if "soak_repair_restart_policy" in evidence:
            require_soak_repair_policy(
                evidence["soak_repair_restart_policy"],
                "soak_repair_restart_policy",
            )
        if "sync_repair_control_timeout_ms" in evidence:
            control_timeout = evidence["sync_repair_control_timeout_ms"]
            require(
                isinstance(control_timeout, int)
                and 5000 <= control_timeout <= 600000,
                "sync-repair control timeout is invalid",
            )
        if "soak_stalled_restart_after_ms" in evidence:
            require_soak_stalled_restart_after_ms(
                evidence["soak_stalled_restart_after_ms"],
                "soak_stalled_restart_after_ms",
            )
        if (
            "soak_repair_deferrals" in evidence
            or "soak_repair_deferred_cycles" in evidence
        ):
            deferred_cycles = require_soak_repair_deferrals(
                evidence, soak_cycles, "soak evidence"
            )
            if evidence.get("soak_repair_restart_policy") == "defer":
                require(
                    evidence["soak_repair_passes"] >= len(deferred_cycles),
                    "deferred soak repair was not drained before completion",
                )
        if "soak_repair_pending" in evidence:
            require(
                evidence["soak_repair_pending"] is False,
                "soak completed with repair still pending",
            )
        require(
            evidence["soak_cycle_ms_min"]
            <= evidence["soak_cycle_ms_median"]
            <= evidence["soak_cycle_ms_max"]
            and evidence["soak_daemon_restarts"] <= soak_cycles
            and evidence["soak_repair_passes"] <= soak_cycles
            and evidence["soak_delete_cycles"] <= soak_cycles
            and re.fullmatch(
                r"[0-9a-f]{64}", evidence.get("soak_final_sha256", "")
            )
            is not None
            and isinstance(soak_high_water, list)
            and len(soak_high_water) == 3
            and all(
                isinstance(value, int) and value > 0
                for value in soak_high_water
            )
            and evidence.get("soak_contains_secrets") is False,
            "soak completion evidence is invalid",
        )
        if "soak_restart_targets" in evidence:
            targets = evidence["soak_restart_targets"]
            require(
                isinstance(targets, list)
                and len(targets) == evidence["soak_daemon_restarts"]
                and all(target in ("a", "b", "c") for target in targets),
                "soak restart-target evidence is invalid",
            )
        if (
            "soak_stalled_cycle_recoveries" in evidence
            or "soak_stalled_cycle_recovery_events" in evidence
        ):
            recovery_count = evidence.get("soak_stalled_cycle_recoveries")
            require(
                isinstance(recovery_count, int)
                and 0 <= recovery_count <= soak_cycles,
                "soak stalled-recovery count is invalid",
            )
            require_soak_stalled_recovery_events(
                evidence.get("soak_stalled_cycle_recovery_events"),
                recovery_count,
                "soak_stalled_cycle_recovery_events",
            )
    capacity_campaign = evidence.get("capacity_campaign", False)
    require(isinstance(capacity_campaign, bool), "capacity flag is invalid")
    if capacity_campaign:
        capacity_files = evidence.get("capacity_files")
        capacity_file_bytes = evidence.get("capacity_file_bytes")
        capacity_logical_bytes = evidence.get("capacity_logical_bytes")
        require(
            isinstance(capacity_files, int)
            and 1 <= capacity_files <= 3500
            and isinstance(capacity_file_bytes, int)
            and 1 <= capacity_file_bytes <= 1024 * 1024
            and capacity_logical_bytes == capacity_files * capacity_file_bytes
            and capacity_logical_bytes <= 56 * 1024 * 1024,
            "capacity population is invalid",
        )
        require(
            re.fullmatch(r"[0-9a-f]{64}", evidence.get("capacity_digest", ""))
            is not None
            and isinstance(evidence.get("capacity_catchup_ms"), int)
            and evidence["capacity_catchup_ms"] > 0,
            "capacity convergence evidence is invalid",
        )
        for field in (
            "capacity_repair_ms_per_node",
            "capacity_agent_high_water_kib",
            "capacity_allocated_delta_bytes_per_node",
        ):
            values = evidence.get(field)
            require(
                isinstance(values, list)
                and len(values) == 3
                and all(isinstance(value, int) and value >= 0 for value in values),
                f"{field} is invalid",
            )
        require(
            all(
                value > 0
                for value in evidence["capacity_agent_high_water_kib"]
            )
            and all(
                value > 0
                for value in evidence["capacity_allocated_delta_bytes_per_node"]
            ),
            "capacity resource evidence is empty",
        )
        batch_fields = (
            "capacity_staged_file_objects_per_node",
            "capacity_file_commit_batches_per_node",
            "capacity_largest_file_commit_batch_per_node",
            "capacity_late_offers_cancelled_per_node",
            "capacity_retired_offer_ids_per_node",
            "capacity_retired_offer_evictions_per_node",
        )
        batch_present = [field in evidence for field in batch_fields]
        require(
            all(batch_present) or not any(batch_present),
            "capacity batch evidence is partial",
        )
        if all(batch_present):
            staged = require_int_list(
                evidence[batch_fields[0]], 3, batch_fields[0]
            )
            batches = require_int_list(
                evidence[batch_fields[1]], 3, batch_fields[1]
            )
            largest = require_int_list(
                evidence[batch_fields[2]], 3, batch_fields[2]
            )
            late = require_int_list(
                evidence[batch_fields[3]], 3, batch_fields[3]
            )
            retired = require_int_list(
                evidence[batch_fields[4]], 3, batch_fields[4]
            )
            evictions = require_int_list(
                evidence[batch_fields[5]], 3, batch_fields[5]
            )
            require(
                staged == [0, 0, 0]
                and all(value <= tree_lane_cap for value in largest)
                and all(
                    batch == 0 or largest_batch > 0
                    for batch, largest_batch in zip(batches, largest)
                )
                and all(
                    batch > 0 or largest_batch == 0
                    for batch, largest_batch in zip(batches, largest)
                ),
                "capacity batch evidence is incoherent",
            )
            require(
                retired == [0, 0, 0]
                and evictions == [0, 0, 0]
                and all(value >= 0 for value in late),
                "capacity late-offer retirement evidence is unsafe",
            )
        inventory_fields = (
            "capacity_cas_full_inventory_scans_per_node",
            "capacity_cas_inventory_objects_inspected_per_node",
        )
        inventory_present = [field in evidence for field in inventory_fields]
        require(
            all(inventory_present) or not any(inventory_present),
            "capacity CAS inventory evidence is partial",
        )
        if all(inventory_present):
            scans = require_int_list(
                evidence[inventory_fields[0]], 3, inventory_fields[0]
            )
            inspected = require_int_list(
                evidence[inventory_fields[1]], 3, inventory_fields[1]
            )
            require(
                scans[0] == 0
                and scans[1] >= 2
                and scans[2] >= 2
                and all(
                    scan_count <= 2 * batch_count
                    for scan_count, batch_count in zip(
                        scans[1:], batches[1:], strict=True
                    )
                )
                and all(
                    batch_count < 4 or scan_count < batch_count
                    for scan_count, batch_count in zip(
                        scans[1:], batches[1:], strict=True
                    )
                )
                and inspected[0] == 0
                and inspected[1] >= evidence["capacity_files"]
                and inspected[2] >= evidence["capacity_files"],
                "capacity CAS inventory scan fence is incoherent",
            )
        reconcile_apply = evidence.get("capacity_reconcile_apply_per_node")
        if reconcile_apply is not None:
            parsed_reconcile_apply = require_reconcile_apply_list(
                reconcile_apply, "capacity_reconcile_apply_per_node"
            )
            require(
                any(item["projection_files"] > 0 for item in parsed_reconcile_apply),
                "capacity reconcile apply evidence has no projected files",
            )
    if evidence.get("maintenance_lifecycle") is True:
        require(
            evidence.get("checkpoint_peer_copies") == 2
            and re.fullmatch(
                r"[0-9a-f]{64}", evidence.get("checkpoint_record_sha256", "")
            )
            is not None,
            "checkpoint propagation evidence is invalid",
        )
        candidates = evidence.get("gc_candidates")
        require(
            isinstance(candidates, int)
            and candidates > 0
            and evidence.get("gc_quarantined") == candidates
            and evidence.get("gc_restored") == candidates
            and evidence.get("pin_unpin_observed") is True,
            "recoverable GC evidence is invalid",
        )
        require(
            evidence.get("cutoff_survivors") == 2
            and evidence.get("post_cutoff_branch_count") == [2, 2]
            and evidence.get("post_cutoff_source_principals") == [1, 1]
            and evidence.get("retired_writer_reentry_refused") is True,
            "writer cutoff evidence is invalid",
        )
    recovery_rehearsal = evidence.get("recovery_rehearsal", False)
    require(isinstance(recovery_rehearsal, bool), "recovery rehearsal flag is invalid")
    if recovery_rehearsal:
        require(
            evidence.get("recovery_model")
            == "same-vm-independent-backup-not-assessed"
            and evidence.get("recovery_backup_independence") == "not-assessed"
            and evidence.get("recovery_restore_provenance") == "not-assessed",
            "recovery rehearsal overstates backup evidence",
        )
        require(
            isinstance(evidence.get("recovery_files"), int)
            and 1 <= evidence["recovery_files"] <= 4096
            and isinstance(evidence.get("recovery_directories"), int)
            and 0 <= evidence["recovery_directories"] <= 4096
            and isinstance(evidence.get("recovery_bytes"), int)
            and 0 < evidence["recovery_bytes"] <= 64 * 1024 * 1024
            and re.fullmatch(
                r"[0-9a-f]{64}", evidence.get("recovery_tree_sha256", "")
            )
            is not None,
            "recovery population evidence is invalid",
        )
        verifier_hashes = evidence.get("recovery_verifier_report_sha256")
        require(
            evidence.get("recovery_verifier_matches") == 4
            and isinstance(verifier_hashes, list)
            and len(verifier_hashes) == 4
            and len(set(verifier_hashes)) == 4
            and all(re.fullmatch(r"[0-9a-f]{64}", value) for value in verifier_hashes),
            "external restore verification evidence is invalid",
        )
        require(
            evidence.get("recovery_one_node_empty_replacement") is True
            and evidence.get("recovery_one_node_capability_revocations") == 2
            and evidence.get("recovery_one_node_writer_cutoffs") == 2
            and evidence.get("recovery_one_node_transport_peer_removals") == 2
            and evidence.get("recovery_one_node_post_cutoff_checkpoints") == 2
            and evidence.get("recovery_one_node_survivor_restarts") == 2
            and evidence.get("recovery_one_node_branch_count") == [3, 3, 3]
            and evidence.get("recovery_all_live_nodes_lost") is True
            and evidence.get("recovery_replacement_nodes") == 3
            and evidence.get("recovery_replacement_branch_count") == [3, 3, 3]
            and evidence.get("recovery_obsolete_principals_absent") is True
            and evidence.get("recovery_repair_verified_nodes") == 6,
            "node-loss/reseed evidence is incomplete",
        )
        obsolete = evidence.get("recovery_obsolete_principal_sha256")
        replacements = evidence.get("recovery_replacement_principal_sha256")
        require(
            isinstance(obsolete, list)
            and len(obsolete) == 4
            and len(set(obsolete)) == 4
            and isinstance(replacements, list)
            and len(replacements) == 3
            and len(set(replacements)) == 3
            and set(obsolete).isdisjoint(replacements)
            and all(
                re.fullmatch(r"[0-9a-f]{64}", value)
                for value in obsolete + replacements
            ),
            "replacement identity commitments are invalid",
        )
        require(
            isinstance(evidence.get("recovery_elapsed_ms"), int)
            and evidence["recovery_elapsed_ms"] > 0
            and evidence.get("recovery_contains_secrets") is False,
            "recovery completion evidence is invalid",
        )
        recovery_operator_provenance = evidence.get(
            "recovery_operator_provenance", "absent"
        )
        require(
            recovery_operator_provenance in ("absent", "present"),
            "recovery operator provenance flag is invalid",
        )
        if recovery_operator_provenance == "present":
            require(
                evidence.get("recovery_operator_provenance_bound") is True
                and evidence.get("recovery_restore_reports_with_provenance")
                == evidence.get("recovery_verifier_matches"),
                "recovery provenance was not bound into every verifier report",
            )
            for field in (
                "recovery_backup_system_sha256",
                "recovery_backup_generation_sha256",
                "recovery_backup_failure_domain_sha256",
                "recovery_restore_provenance_sha256",
            ):
                require(
                    re.fullmatch(r"[0-9a-f]{64}", evidence.get(field, ""))
                    is not None,
                    f"{field} is invalid",
                )
        root_devices = evidence.get("recovery_root_devices_differ")
        if root_devices is not None:
            require(
                isinstance(root_devices, list)
                and len(root_devices) == evidence.get(
                    "recovery_verifier_matches"
                )
                and all(value in (0, 1) for value in root_devices),
                "recovery root-device evidence is invalid",
            )
    storage_fault_rehearsal = evidence.get("storage_fault_rehearsal", False)
    require(
        isinstance(storage_fault_rehearsal, bool),
        "storage-fault rehearsal flag is invalid",
    )
    if storage_fault_rehearsal:
        require(
            evidence.get("storage_fault_schema")
            == "iotox.sync-storage-fault.v1"
            and evidence.get("storage_fault_status") == "passed"
            and evidence.get("storage_fault_node_count") == 3
            and evidence.get("storage_fault_filesystem") == "ext4-loop"
            and evidence.get("storage_fault_disk_mib_per_node") == 192,
            "storage-fault substrate evidence is invalid",
        )
        require(
            evidence.get("enospc_live_observed") is True
            and isinstance(evidence.get("enospc_filler_bytes"), int)
            and evidence["enospc_filler_bytes"] > 0
            and isinstance(evidence.get("enospc_abrupt_exit"), int)
            and evidence["enospc_abrupt_exit"] != 0
            and evidence.get("read_only_start_refused") is True
            and isinstance(evidence.get("read_only_exit"), int)
            and evidence["read_only_exit"] != 0
            and re.fullmatch(
                r"[0-9a-f]{64}", evidence.get("read_only_log_sha256", "")
            )
            is not None,
            "ENOSPC/read-only evidence is invalid",
        )
        require(
            evidence.get("abrupt_exchange_observed")
            in ("projection-stage", "pending-workspace")
            and evidence.get("abrupt_exchange_bytes") == 32 * 1024 * 1024
            and isinstance(evidence.get("abrupt_exchange_exit"), int)
            and evidence["abrupt_exchange_exit"] != 0,
            "abrupt exchange evidence is invalid",
        )
        require(
            evidence.get("storage_fault_final_files") == 19
            and evidence.get("storage_fault_final_directories") == 1
            and evidence.get("storage_fault_final_bytes") == 33620017
            and re.fullmatch(
                r"[0-9a-f]{64}",
                evidence.get("storage_fault_final_tree_sha256", ""),
            )
            is not None
            and evidence.get("storage_fault_repair_verified_nodes") == 3
            and isinstance(evidence.get("storage_fault_elapsed_ms"), int)
            and evidence["storage_fault_elapsed_ms"] > 0
            and evidence.get("storage_fault_contains_secrets") is False
            and evidence.get("storage_fault_power_cut") is False
            and evidence.get("storage_fault_dishonest_storage_assessed") is False,
            "storage-fault completion evidence is invalid",
        )
    require(evidence.get("contains_secrets") is False, "receipt is not content-free")
    return {
        "schema": "iotox.sync-three-writer-sandwurm-verification.v1",
        "status": "passed",
        "proof_root": str(proof_root),
        "evidence_boundary": evidence_boundary,
        "node_count": 3,
        "directed_read_write_share_count": 6,
        "branch_count_per_node": [3, 3, 3],
        "conflict_alternatives_per_node": [2, 2, 2],
        "shadow_cycles": evidence.get("shadow_cycles", 0),
        "soak_campaign": soak_campaign,
        "soak_cycles": evidence.get("soak_cycles", 0),
        "soak_elapsed_ms": evidence.get("soak_elapsed_ms", 0),
        "soak_restart_settle_passes": evidence.get(
            "soak_restart_settle_passes", 0
        ),
        "soak_stalled_restart_after_ms": evidence.get(
            "soak_stalled_restart_after_ms", 0
        ),
        "soak_stalled_cycle_recoveries": evidence.get(
            "soak_stalled_cycle_recoveries", 0
        ),
        "tree_lane_cap": tree_lane_cap,
        "tree_lane_process_cap": process_tree_lane_cap,
        "tree_lane_namespace_cap": namespace_tree_lane_cap,
        "stalled_cycle_restarts": restart_count,
        "capacity_campaign": capacity_campaign,
        "capacity_files": evidence.get("capacity_files", 0),
        "capacity_logical_bytes": evidence.get("capacity_logical_bytes", 0),
        "capacity_catchup_ms": evidence.get("capacity_catchup_ms", 0),
        "capacity_file_commit_batches_per_node": evidence.get(
            "capacity_file_commit_batches_per_node", [0, 0, 0]
        ),
        "capacity_largest_file_commit_batch_per_node": evidence.get(
            "capacity_largest_file_commit_batch_per_node", [0, 0, 0]
        ),
        "capacity_cas_full_inventory_scans_per_node": evidence.get(
            "capacity_cas_full_inventory_scans_per_node", [0, 0, 0]
        ),
        "capacity_cas_inventory_objects_inspected_per_node": evidence.get(
            "capacity_cas_inventory_objects_inspected_per_node", [0, 0, 0]
        ),
        "capacity_reconcile_apply_per_node": evidence.get(
            "capacity_reconcile_apply_per_node", []
        ),
        "capacity_late_offers_cancelled_per_node": evidence.get(
            "capacity_late_offers_cancelled_per_node", [0, 0, 0]
        ),
        "maintenance_lifecycle": evidence.get("maintenance_lifecycle", False),
        "recovery_rehearsal": recovery_rehearsal,
        "recovery_verifier_matches": evidence.get("recovery_verifier_matches", 0),
        "storage_fault_rehearsal": storage_fault_rehearsal,
        "enospc_live_observed": evidence.get("enospc_live_observed", False),
        "read_only_start_refused": evidence.get(
            "read_only_start_refused", False
        ),
        "abrupt_exchange_observed": evidence.get(
            "abrupt_exchange_observed", "not-run"
        ),
        "resolved_sha256": evidence["resolved_sha256"],
        "network_class": "none",
        "vm_substrate": "cloud-hypervisor",
        "contains_secrets": False,
    }


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value) + "\n", encoding="utf-8")


def self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="iotox-three-writer-verifier-") as raw:
        root = Path(raw)
        write_json(
            root / "direct-cloud-hypervisor-live-chain.json",
            {"status": "guest-evidence-observed", "failure": None},
        )
        write_json(
            root / "prelaunch/launch/cloud-hypervisor-launch.json",
            {"network": {"class": "none", "mode": "none"}, "vmm": {"argv": []}},
        )
        evidence_path = (
            root
            / "live/workspace-export/guest-receipts/iotox/sync-three-writer.json"
        )
        evidence = {
            "schema": "iotox.sync-three-writer.v1",
            "status": "passed",
            "namespace_sha256": "31" * 32,
            "node_count": 3,
            "friendship_edge_count": 3,
            "directed_read_write_share_count": 6,
            "source_principals_per_node": 2,
            "branch_count_per_node": [3, 3, 3],
            "conflict_alternatives_per_node": [2, 2, 2],
            "three_way_conflict_observed": True,
            "explicit_resolution_observed": True,
            "automation_record_format": 2,
            "automation_record_bytes": 4808,
            "periodic_attempts_per_node": [2, 3, 4],
            "tox_key_sha256": ["01" * 32, "02" * 32, "03" * 32],
            "principal_sha256": ["11" * 32, "12" * 32, "13" * 32],
            "resolved_sha256": "21" * 32,
            "elapsed_ms": 1,
            "state_reused": False,
            "tree_lane_cap": 4,
            "tree_lane_process_cap": 4,
            "tree_lane_namespace_cap": 4,
            "shadow_cycles": 0,
            "shadow_elapsed_ms": 0,
            "stalled_cycle_restarts": 0,
            "stalled_cycle_restart_events": [],
            "maintenance_lifecycle": False,
            "capacity_campaign": False,
            "contains_secrets": False,
        }
        write_json(evidence_path, evidence)
        require(verify(root)["status"] == "passed", "valid fixture failed")

        write_json(
            root / "direct-cloud-hypervisor-live-chain.json",
            {
                "status": "launched-without-guest-evidence",
                "failure": {"blockers": ["guest-evidence-not-observed"]},
                "receipts": {"live_launch": {"status": "exited"}},
                "guest_evidence": {
                    "observed": False,
                    "missing_legacy_guest_receipts": ["task-receipt.json"],
                },
            },
        )
        require(
            verify(root)["evidence_boundary"] == "iotox-domain-receipt",
            "valid IoTox-domain receipt fixture failed",
        )
        write_json(
            root / "direct-cloud-hypervisor-live-chain.json",
            {
                "status": "launched-without-guest-evidence",
                "failure": {"blockers": ["guest-evidence-not-observed"]},
                "receipts": {"live_launch": {"status": "running"}},
                "guest_evidence": {
                    "observed": False,
                    "missing_legacy_guest_receipts": ["task-receipt.json"],
                },
            },
        )
        try:
            verify(root)
        except ValueError:
            pass
        else:
            raise ValueError("running VMM domain receipt boundary passed")
        write_json(
            root / "direct-cloud-hypervisor-live-chain.json",
            {
                "status": "launched-without-guest-evidence",
                "failure": {"blockers": ["guest-evidence-not-observed"]},
                "receipts": {"live_launch": {"status": "exited"}},
                "guest_evidence": {
                    "observed": False,
                    "missing_legacy_guest_receipts": ["task-receipt.json"],
                },
            },
        )

        evidence.update(
            {
                "capacity_campaign": True,
                "capacity_files": 128,
                "capacity_file_bytes": 4096,
                "capacity_logical_bytes": 128 * 4096,
                "capacity_digest": "51" * 32,
                "capacity_catchup_ms": 100,
                "capacity_repair_ms_per_node": [10, 11, 12],
                "capacity_agent_high_water_kib": [1000, 1100, 1200],
                "capacity_allocated_delta_bytes_per_node": [4096, 4096, 4096],
                "capacity_staged_file_objects_per_node": [0, 0, 0],
                "capacity_file_commit_batches_per_node": [0, 8, 8],
                "capacity_largest_file_commit_batch_per_node": [0, 4, 4],
                "capacity_cas_full_inventory_scans_per_node": [0, 2, 2],
                "capacity_cas_inventory_objects_inspected_per_node": [
                    0,
                    129,
                    129,
                ],
                "capacity_reconcile_apply_per_node": [
                    {
                        "branch_advances": 0,
                        "cas_inspected": 0,
                        "cas_inspected_bytes": 0,
                        "cas_installed": 0,
                        "cas_installed_bytes": 0,
                        "cas_reused": 0,
                        "local_events": 0,
                        "projection_bytes": 0,
                        "projection_conflict_files": 0,
                        "projection_conflict_tombstones": 0,
                        "projection_dirs": 0,
                        "projection_files": 0,
                        "projection_preserved_bytes": 0,
                        "projection_preserved_dirs": 0,
                        "projection_preserved_entries": 0,
                        "projection_preserved_files": 0,
                        "source_hashed": 0,
                        "source_inspected": 0,
                        "source_reused": 0,
                    },
                    {
                        "branch_advances": 0,
                        "cas_inspected": 129,
                        "cas_inspected_bytes": 524288,
                        "cas_installed": 0,
                        "cas_installed_bytes": 0,
                        "cas_reused": 0,
                        "local_events": 0,
                        "projection_bytes": 524288,
                        "projection_conflict_files": 0,
                        "projection_conflict_tombstones": 0,
                        "projection_dirs": 1,
                        "projection_files": 128,
                        "projection_preserved_bytes": 0,
                        "projection_preserved_dirs": 0,
                        "projection_preserved_entries": 0,
                        "projection_preserved_files": 0,
                        "source_hashed": 0,
                        "source_inspected": 0,
                        "source_reused": 0,
                    },
                    {
                        "branch_advances": 0,
                        "cas_inspected": 129,
                        "cas_inspected_bytes": 524288,
                        "cas_installed": 0,
                        "cas_installed_bytes": 0,
                        "cas_reused": 0,
                        "local_events": 0,
                        "projection_bytes": 524288,
                        "projection_conflict_files": 0,
                        "projection_conflict_tombstones": 0,
                        "projection_dirs": 1,
                        "projection_files": 128,
                        "projection_preserved_bytes": 0,
                        "projection_preserved_dirs": 0,
                        "projection_preserved_entries": 0,
                        "projection_preserved_files": 0,
                        "source_hashed": 0,
                        "source_inspected": 0,
                        "source_reused": 0,
                    },
                ],
                "capacity_late_offers_cancelled_per_node": [0, 2, 3],
                "capacity_retired_offer_ids_per_node": [0, 0, 0],
                "capacity_retired_offer_evictions_per_node": [0, 0, 0],
            }
        )
        write_json(evidence_path, evidence)
        require(
            verify(root)["capacity_campaign"] is True,
            "valid capacity fixture failed",
        )

        evidence.update(
            {
                "soak_campaign": True,
                "soak_requested_seconds": 1,
                "soak_minimum_cycles": 3,
                "soak_cycle_delay_ms": 0,
                "soak_restart_every": 2,
                "soak_restart_phase": "before-edit",
                "soak_restart_settle_policy": "repair-before-edit",
                "soak_final_boundary_restart_policy": "allow",
                "soak_restart_settle_passes": 1,
                "soak_restart_settle_cycles": [2],
                "soak_restart_skipped_final_boundary": 0,
                "soak_restart_skipped_cycles": [],
                "soak_repair_every": 2,
                "soak_stalled_restart_after_ms": 120000,
                "soak_cycles": 3,
                "soak_elapsed_ms": 1000,
                "soak_daemon_restarts": 1,
                "soak_restart_targets": ["a"],
                "soak_stalled_cycle_recoveries": 1,
                "soak_stalled_cycle_recovery_events": [
                    {
                        "cycle": 2,
                        "writer": "b",
                        "targets": ["c"],
                        "wait_channels_by_node": [
                            {
                                "node": "c",
                                "wait_channels": ["ep_poll"],
                            },
                        ],
                    },
                ],
                "soak_repair_passes": 1,
                "soak_delete_cycles": 1,
                "soak_cycle_ms_min": 10,
                "soak_cycle_ms_median": 20,
                "soak_cycle_ms_max": 30,
                "soak_final_sha256": "55" * 32,
                "soak_agent_high_water_kib": [1000, 1100, 1200],
                "soak_contains_secrets": False,
            }
        )
        write_json(evidence_path, evidence)
        require(
            verify(root)["soak_cycles"] == 3,
            "valid soak fixture failed",
        )
        evidence["soak_cycles"] = 2
        write_json(evidence_path, evidence)
        try:
            verify(root)
        except ValueError:
            pass
        else:
            raise ValueError("under-counted soak evidence passed")
        evidence["soak_cycles"] = 3

        evidence.update(
            {
                "recovery_rehearsal": True,
                "recovery_model": "same-vm-independent-backup-not-assessed",
                "recovery_backup_independence": "not-assessed",
                "recovery_restore_provenance": "not-assessed",
                "recovery_files": 33,
                "recovery_directories": 1,
                "recovery_bytes": 131099,
                "recovery_tree_sha256": "61" * 32,
                "recovery_verifier_matches": 4,
                "recovery_verifier_report_sha256": [
                    "71" * 32,
                    "72" * 32,
                    "73" * 32,
                    "74" * 32,
                ],
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
                "recovery_obsolete_principal_sha256": [
                    "81" * 32,
                    "82" * 32,
                    "83" * 32,
                    "84" * 32,
                ],
                "recovery_replacement_principal_sha256": [
                    "91" * 32,
                    "92" * 32,
                    "93" * 32,
                ],
                "recovery_repair_verified_nodes": 6,
                "recovery_elapsed_ms": 1000,
                "recovery_contains_secrets": False,
                "recovery_operator_provenance": "present",
                "recovery_operator_provenance_bound": True,
                "recovery_restore_reports_with_provenance": 4,
                "recovery_backup_system_sha256": "a1" * 32,
                "recovery_backup_generation_sha256": "a2" * 32,
                "recovery_backup_failure_domain_sha256": "a3" * 32,
                "recovery_restore_provenance_sha256": "a4" * 32,
                "recovery_root_devices_differ": [0, 0, 0, 0],
            }
        )
        write_json(evidence_path, evidence)
        require(
            verify(root)["recovery_verifier_matches"] == 4,
            "valid recovery rehearsal fixture failed",
        )

        evidence["recovery_backup_independence"] = "proven"
        write_json(evidence_path, evidence)
        try:
            verify(root)
        except ValueError:
            pass
        else:
            raise ValueError("overstated recovery evidence passed")
        evidence["recovery_backup_independence"] = "not-assessed"

        evidence.update(
            {
                "storage_fault_schema": "iotox.sync-storage-fault.v1",
                "storage_fault_rehearsal": True,
                "storage_fault_status": "passed",
                "storage_fault_node_count": 3,
                "storage_fault_filesystem": "ext4-loop",
                "storage_fault_disk_mib_per_node": 192,
                "enospc_live_observed": True,
                "enospc_filler_bytes": 1024,
                "enospc_abrupt_exit": -9,
                "read_only_start_refused": True,
                "read_only_exit": 1,
                "read_only_log_sha256": "a1" * 32,
                "abrupt_exchange_observed": "pending-workspace",
                "abrupt_exchange_bytes": 32 * 1024 * 1024,
                "abrupt_exchange_exit": -9,
                "storage_fault_final_files": 19,
                "storage_fault_final_directories": 1,
                "storage_fault_final_bytes": 33620017,
                "storage_fault_final_tree_sha256": "a2" * 32,
                "storage_fault_repair_verified_nodes": 3,
                "storage_fault_elapsed_ms": 1000,
                "storage_fault_contains_secrets": False,
                "storage_fault_power_cut": False,
                "storage_fault_dishonest_storage_assessed": False,
            }
        )
        write_json(evidence_path, evidence)
        require(
            verify(root)["storage_fault_rehearsal"] is True,
            "valid storage-fault fixture failed",
        )
        evidence["storage_fault_power_cut"] = True
        write_json(evidence_path, evidence)
        try:
            verify(root)
        except ValueError:
            pass
        else:
            raise ValueError("overstated storage-fault evidence passed")
        evidence["storage_fault_power_cut"] = False

        evidence["periodic_attempts_per_node"] = [2, 0, 4]
        write_json(evidence_path, evidence)
        try:
            verify(root)
        except ValueError:
            pass
        else:
            raise ValueError("invalid peer scheduler evidence passed")

        failure = "timeout waiting for writable soak cycle 73"
        rejected_pull_summary = [
            {
                "jobs": 2,
                "awaiting_inventory": 0,
                "awaiting_object": 1,
                "complete": 1,
                "failed": 0,
                "cancelled": 0,
                "manifest_file_objects": 3501,
                "selected_file_objects": 3501,
                "skipped_file_objects": 0,
                "selected_paths": 3501,
                "skipped_paths": 0,
                "sources": 2,
                "availability_requests": 0,
                "availability_results": 0,
                "absent_results": 0,
                "unavailable_results": 0,
                "active_lanes": 8,
                "staged_file_objects": 0,
                "file_commit_batches": 24,
                "largest_file_commit_batch": 8,
                "cas_full_inventory_scans": 5,
                "cas_inventory_objects_inspected": 512,
                "requested_objects": 203,
                "committed_objects": 195,
                "reused_objects": 0,
                "fetched_bytes": 3178512,
                "accepted_branches": 3,
                "conflicts": 0,
                "lane_records": 8,
                "lane_admitted": 8,
                "lane_bytes": 131072,
                "source_records": 2,
                "source_online": 2,
                "source_requested": 203,
                "source_offered": 203,
                "source_absent": 0,
                "source_unavailable": 0,
                "source_committed": 195,
                "source_fetched_bytes": 3178512,
            },
            {
                "jobs": 1,
                "awaiting_inventory": 0,
                "awaiting_object": 1,
                "complete": 0,
                "failed": 0,
                "cancelled": 0,
                "manifest_file_objects": 3501,
                "selected_file_objects": 3501,
                "skipped_file_objects": 0,
                "selected_paths": 3501,
                "skipped_paths": 0,
                "sources": 1,
                "availability_requests": 0,
                "availability_results": 0,
                "absent_results": 0,
                "unavailable_results": 0,
                "active_lanes": 8,
                "staged_file_objects": 0,
                "file_commit_batches": 16,
                "largest_file_commit_batch": 8,
                "cas_full_inventory_scans": 4,
                "cas_inventory_objects_inspected": 300,
                "requested_objects": 203,
                "committed_objects": 195,
                "reused_objects": 0,
                "fetched_bytes": 3178512,
                "accepted_branches": 3,
                "conflicts": 0,
                "lane_records": 8,
                "lane_admitted": 8,
                "lane_bytes": 131072,
                "source_records": 1,
                "source_online": 1,
                "source_requested": 203,
                "source_offered": 203,
                "source_absent": 0,
                "source_unavailable": 0,
                "source_committed": 195,
                "source_fetched_bytes": 3178512,
            },
            {
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
            },
        ]
        write_json(
            root / "direct-cloud-hypervisor-live-chain.json",
            {
                "status": "launched-without-guest-evidence",
                "failure": {"blockers": ["guest-evidence-not-observed"]},
                "receipts": {"live_launch": {"status": "exited"}},
            },
        )
        rejected = {
            "schema": "iotox.sync-three-writer.v1",
            "status": "rejected",
            "failure": failure,
            "failure_sha256": hashlib.sha256(failure.encode("utf-8")).hexdigest(),
            "namespace_sha256": "31" * 32,
            "node_count": 3,
            "elapsed_ms": 1800001,
            "state_reused": False,
            "tree_lane_cap": 32,
            "tree_lane_process_cap": 32,
            "tree_lane_namespace_cap": 32,
            "capacity_campaign": True,
            "capacity_files": 3500,
            "capacity_file_bytes": 16384,
            "capacity_logical_bytes": 3500 * 16384,
            "partial_agent_high_water_kib": [1000, 1100, 1200],
            "partial_branch_count_per_node": [3, 3, 3],
            "partial_capacity_shape_per_node": [
                {"files": 3500, "bytes": 3500 * 16384},
                {"files": 3500, "bytes": 3500 * 16384},
                {"files": 3500, "bytes": 3500 * 16384},
            ],
            "partial_conflict_alternatives_per_node": [0, 0, 0],
            "partial_tree_v2_store_shape_per_node": [
                {
                    "branch_bytes": 984,
                    "branches": 3,
                    "incoming_bytes": 0,
                    "incoming_files": 0,
                    "manifest_bytes": 378524,
                    "manifests": 4,
                    "object_bytes": 57344016,
                    "objects": 3501,
                    "record_bytes": 1240,
                    "records": 4,
                },
                {
                    "branch_bytes": 768,
                    "branches": 3,
                    "incoming_bytes": 0,
                    "incoming_files": 0,
                    "manifest_bytes": 324,
                    "manifests": 3,
                    "object_bytes": 2146320,
                    "objects": 132,
                    "record_bytes": 768,
                    "records": 3,
                },
                {
                    "branch_bytes": 768,
                    "branches": 3,
                    "incoming_bytes": 0,
                    "incoming_files": 0,
                    "manifest_bytes": 324,
                    "manifests": 3,
                    "object_bytes": 2572304,
                    "objects": 158,
                    "record_bytes": 768,
                    "records": 3,
                },
            ],
            "partial_tree_v2_pull_summary_per_node": rejected_pull_summary,
            "partial_soak_projection_per_node": [
                {
                    "current_exists": True,
                    "current_bytes": 26,
                    "current_sha256": "71" * 32,
                    "toggle_exists": True,
                    "toggle_bytes": 15,
                    "toggle_sha256": "72" * 32,
                },
                {
                    "current_exists": True,
                    "current_bytes": 26,
                    "current_sha256": "71" * 32,
                    "toggle_exists": True,
                    "toggle_bytes": 15,
                    "toggle_sha256": "72" * 32,
                },
                {
                    "current_exists": True,
                    "current_bytes": 26,
                    "current_sha256": "73" * 32,
                    "toggle_exists": False,
                    "toggle_bytes": 0,
                    "toggle_sha256": "",
                },
            ],
            "shadow_cycles": 0,
            "maintenance_lifecycle_requested": False,
            "partial_soak_evidence": {
                "soak_campaign": True,
                "soak_completed": False,
                "soak_requested_seconds": 86400,
                "soak_minimum_cycles": 288,
                "soak_cycle_delay_ms": 5000,
                "soak_restart_every": 24,
                "soak_restart_phase": "after-edit",
                "soak_final_boundary_restart_policy": "allow",
                "soak_restart_skipped_final_boundary": 0,
                "soak_restart_skipped_cycles": [],
                "soak_repair_every": 12,
                "soak_stalled_restart_after_ms": 600000,
                "soak_cycles": 17,
                "soak_elapsed_ms": 5400000,
                "soak_daemon_restarts": 0,
                "soak_restart_targets": [],
                "soak_stalled_cycle_recoveries": 0,
                "soak_stalled_cycle_recovery_events": [],
                "soak_repair_passes": 1,
                "soak_delete_cycles": 8,
                "soak_last_cycle_ms": 2210,
                "soak_final_sha256": "77" * 32,
                "soak_agent_high_water_kib": [1000, 1100, 1200],
                "soak_contains_secrets": False,
            },
            "stage_events": [
                {"elapsed_ms": 0, "message": "starting private bootstrap and three agents"},
                {"elapsed_ms": 2146, "message": "namespace maximum-lanes override applied: 32"},
                {"elapsed_ms": 18315, "message": "three friendship edges confirmed"},
                {"elapsed_ms": 22533, "message": "three signed branches converged"},
            ],
            "contains_secrets": False,
        }
        write_json(evidence_path, rejected)
        rejected_result = verify(root)
        require(rejected_result["status"] == "rejected", "valid rejected fixture failed")
        require(
            rejected_result["partial_soak_cycles"] == 17,
            "partial soak evidence was not projected",
        )
        require(
            rejected_result["partial_soak_projection_per_node"][2][
                "toggle_exists"
            ]
            is False,
            "partial soak projection evidence was not projected",
        )

        rejected["stage_events"] = [
            {
                "elapsed_ms": 5400001,
                "message": "writable soak cycle 12 sync-repair scheduled completed",
            },
            {
                "elapsed_ms": 5600001,
                "message": "writable soak cycle 17 restarting node c before edit",
            },
            {
                "elapsed_ms": 5605001,
                "message": "writable soak cycle 17 restart-settle sync-repair started",
            },
            {
                "elapsed_ms": 5610001,
                "message": "writable soak cycle 17 restart-settle sync-repair completed",
            },
        ]
        write_json(evidence_path, rejected)
        require(
            verify(root)["partial_soak_cycles"] == 17,
            "valid late-soak rejected fixture failed without retained branch event",
        )
        rejected["stage_events"] = [
            {"elapsed_ms": 0, "message": "starting private bootstrap and three agents"},
            {"elapsed_ms": 2146, "message": "namespace maximum-lanes override applied: 32"},
            {"elapsed_ms": 18315, "message": "three friendship edges confirmed"},
            {"elapsed_ms": 22533, "message": "three signed branches converged"},
        ]

        rejected["failure"] = "timeout waiting for capacity population on all three writers"
        rejected["failure_sha256"] = hashlib.sha256(
            rejected["failure"].encode("utf-8")
        ).hexdigest()
        write_json(evidence_path, rejected)
        try:
            verify(root)
        except ValueError:
            pass
        else:
            raise ValueError("full-capacity capacity-time rejection passed")

        rejected["partial_capacity_shape_per_node"][2] = {
            "files": 158,
            "bytes": 158 * 16384,
        }
        write_json(evidence_path, rejected)
        require(
            verify(root)["status"] == "rejected",
            "capacity-time rejected fixture failed",
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("proof_root", type=Path, nargs="?")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        print("sync-three-writer Sandwurm verifier self-test: PASS")
        return 0
    if args.proof_root is None:
        parser.error("proof_root is required unless --self-test is used")
    print(json.dumps(verify(args.proof_root), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
