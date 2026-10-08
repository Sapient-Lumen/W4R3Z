#!/usr/bin/env python3
"""Fail-closed structural audit for capacity-is-not-validity semantics."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED = (
    Path("CMakeLists.txt"),
    Path("src/sync_replica_model.hpp"),
    Path("src/sync_replica_model.cpp"),
    Path("src/sync_replica_network_simulator.hpp"),
    Path("src/sync_replica_network_simulator.cpp"),
    Path("tests/sync_replica_capacity_backpressure_test.cpp"),
    Path("tools/audit_sync_replica_capacity_backpressure.py"),
    Path("tools/verify_release_package.py"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def ordered(text: str, *tokens: str) -> bool:
    cursor = -1
    for token in tokens:
        cursor = text.find(token, cursor + 1)
        if cursor < 0:
            return False
    return True


def function_body(text: str, signature: str) -> str:
    start = text.find(signature)
    if start < 0:
        return ""
    brace = text.find("{", start)
    if brace < 0:
        return ""
    depth = 0
    for index in range(brace, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    return ""


def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-sync-replica-capacity-backpressure-audit-v1",
        "root": str(root),
        "passed": not violations,
        "passed_checks": len(checks) - len(violations),
        "total_checks": len(checks),
        "checks": [asdict(check) for check in checks],
        "violations": violations,
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if output is None:
        sys.stdout.write(rendered)
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    return 0 if not violations else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()

    checks: list[Check] = []

    def require(condition: bool, check_id: str, detail: str) -> None:
        checks.append(Check(check_id, bool(condition), detail))

    missing = [path.as_posix() for path in REQUIRED if not (root / path).is_file()]
    require(not missing, "required_files_exist", f"missing={missing}")
    if missing:
        return emit(root, args.json, checks)

    text = {
        path.as_posix(): (root / path).read_text(encoding="utf-8")
        for path in REQUIRED
    }
    cmake = text["CMakeLists.txt"]
    model_header = text["src/sync_replica_model.hpp"]
    model = text["src/sync_replica_model.cpp"]
    network_header = text["src/sync_replica_network_simulator.hpp"]
    network = text["src/sync_replica_network_simulator.cpp"]
    runtime = text["tests/sync_replica_capacity_backpressure_test.cpp"]
    verifier = text["tools/verify_release_package.py"]

    require(
        "CapacityBlocked" in model_header
        and "enum class SyncReplicaRemoteReadiness" in model_header,
        "capacity_is_explicit_in_result_algebra",
        "valid local resource pressure is distinct from insertion, duplicate, and quarantine",
    )
    require(
        all(token in model_header for token in (
            "struct SyncReplicaResourceBudget final",
            "std::uint64_t retained",
            "std::uint64_t incoming",
            "std::uint64_t limit",
            "incoming > limit - retained",
            "struct SyncReplicaRemoteAdmissionPreflight final",
        )),
        "preflight_exposes_exact_overflow_safe_resource_state",
        "operation, canonical-byte, context, and predecessor charges use fixed-width values",
    )
    require(
        "preflight_remote_admission_or_throw" in model_header
        and "const SyncReplicaOperation& operation) const" in model_header,
        "preflight_is_public_and_nonmutating",
        "transport can classify retryable pressure before cloning destination state",
    )

    preflight = function_body(
        model, "SyncReplicaModel::preflight_remote_admission_or_throw(")
    require(
        ordered(
            preflight,
            "const auto duplicate",
            "SyncReplicaRemoteReadiness::Duplicate",
            "validate_sync_replica_operation_and_measure_or_throw",
            "operation.folder_id != folder_id_",
            "retained_charge_or_throw",
            "remote_preflight_is_capacity_blocked",
            "SyncReplicaRemoteReadiness::CapacityBlocked",
        ),
        "validity_precedes_capacity_classification",
        "malformed/cross-folder evidence cannot be mislabeled as local backpressure",
    )
    duplicate_prefix = preflight.split(
        "validate_sync_replica_operation_and_measure_or_throw", 1
    )[0]
    require(
        duplicate_prefix.count("0U") >= 4
        and "SyncReplicaRemoteReadiness::Duplicate" in duplicate_prefix,
        "exact_duplicate_reports_zero_incoming_charge_before_rehash",
        "already-owned immutable evidence consumes no additional retained budget",
    )

    accept = function_body(
        model, "SyncReplicaAdmission SyncReplicaModel::accept_remote_or_throw(")
    require(
        ordered(
            accept,
            "preflight_remote_admission_or_throw",
            "return SyncReplicaAdmission::Duplicate",
            "return SyncReplicaAdmission::CapacityBlocked",
            "accept_remote_admissible_after_preflight_or_throw",
        )
        and "evidence_by_id_.emplace" not in accept,
        "capacity_and_duplicate_return_before_mutating_commit",
        "only an admissible preflight reaches the staged evidence owner",
    )

    commit = function_body(
        model,
        "SyncReplicaModel::accept_remote_admissible_after_preflight_or_throw(",
    )
    require(
        all(token in commit for token in (
            "preflight.operations != SyncReplicaResourceBudget",
            "preflight.canonical_bytes.retained != retained_canonical_bytes_",
            "preflight.context_entries.retained != retained_context_entries_",
            "preflight.predecessor_ids.retained != retained_predecessor_ids_",
            "evidence_by_id_.contains(operation.operation_id)",
        )),
        "preflight_consumption_rejects_stale_owner_state",
        "a copied model may consume only a plan matching all live counters and limits",
    )
    require(
        ordered(
            commit,
            "evidence_by_id_.emplace",
            "project_sync_replica_evidence_or_throw",
            "retained_canonical_bytes_ =",
        )
        and "catch (...)" in commit
        and "evidence_by_id_.erase(inserted.first);" in commit,
        "admissible_commit_is_atomic_and_rollback_safe",
        "projection/allocation failure cannot publish partial evidence or counters",
    )
    require(
        "friend class SyncReplicaNetworkSimulator" in model_header
        and "accept_remote_admissible_after_preflight_or_throw" in model_header,
        "friend_boundary_avoids_double_validation",
        "the deterministic harness alone can consume a validated plan on an exact model copy",
    )

    deliver = function_body(
        network, "SyncReplicaNetworkSimulator::deliver_message_or_throw(")
    require(
        ordered(
            deliver,
            "preflight_remote_admission_or_throw",
            "SyncReplicaRemoteReadiness::Duplicate",
            "erase_message_noexcept(found)",
            "SyncReplicaRemoteReadiness::CapacityBlocked",
            "SyncReplicaModel candidate",
            "accept_remote_admissible_after_preflight_or_throw",
            "candidate.durable_state()",
        ),
        "network_preflights_before_whole_graph_clone",
        "duplicates retire and capacity retries remain queued before candidate/durable allocation",
    )
    pre_clone = deliver.split("SyncReplicaModel candidate", 1)[0]
    require(
        "candidate.durable_state" not in pre_clone
        and "accept_remote_or_throw" not in deliver,
        "admissible_delivery_validates_once",
        "the post-copy path consumes the original validated plan instead of rehashing twice",
    )
    require(
        "direction_is_partitioned_noexcept" in network_header
        and "erase_partition_direction_noexcept" in network_header
        and "struct DirectionView final" in network_header
        and "using is_transparent = void" in network_header
        and "DirectionView{source_device_id, destination_device_id}" in network
        and "std::set<DirectionKey, DirectionLess>" in network_header,
        "partition_queries_do_not_construct_owned_pair_keys",
        "transparent logarithmic lookup avoids both temporary strings and a linear partition scan",
    )

    drain = function_body(
        network, "SyncReplicaNetworkSimulator::drain_deliverable_or_throw(")
    require(
        all(token in drain for token in (
            "std::set<std::uint64_t> capacity_blocked_message_ids",
            "capacity_blocked_message_ids.contains",
            "result.value() == SyncReplicaAdmission::CapacityBlocked",
            "capacity_blocked_message_ids.insert",
            "continue;",
        )),
        "drain_skips_each_capacity_block_once_per_pass",
        "retryable pressure cannot spin to max_deliveries or hide a later duplicate/admissible message",
    )

    require(
        all(token in runtime for token in (
            "full capacity masked malformed evidence as backpressure",
            "the same valid envelope did not succeed after local capacity expansion",
            "AllocationArm arm(1U)",
            "duplicate_allocation_attempts == 0U",
            "SyncReplicaAdmission::CapacityBlocked",
            "pending_message_semantic_bytes",
            "SyncReplicaDeliveryOrder::OldestFirst",
            "SyncReplicaDeliveryOrder::NewestFirst",
        )),
        "runtime_proof_covers_validity_retry_zero_allocation_and_fair_drain",
        "the executable tests both result semantics and transport ownership behavior",
    )
    require(
        runtime.count("network_baseline") >= 4
        and "!model.evidence_state(blocked.operation_id).has_value()" in runtime,
        "runtime_proof_attests_no_quarantine_or_durable_mutation",
        "capacity blocking leaves both model and network durable owners unchanged",
    )

    target = "anonsync_sync_replica_capacity_backpressure_test"
    require(
        cmake.count(target) >= 5
        and f"add_test(NAME {target}" in cmake,
        "runtime_test_is_built_registered_and_sanitized",
        "the focused proof participates in ordinary and ASan/UBSan lanes",
    )
    require(
        "anonsync_sync_replica_capacity_backpressure_source_audit" in cmake
        and "audit_sync_replica_capacity_backpressure.py" in cmake
        and "${Python3_EXECUTABLE} -B -S" in cmake,
        "source_audit_is_hermetically_registered",
        "CTest runs this script without site imports or bytecode products",
    )
    require(
        "revision_number >= 868" in verifier
        and "tests/sync_replica_capacity_backpressure_test.cpp" in verifier
        and "tools/audit_sync_replica_capacity_backpressure.py" in verifier,
        "release_verifier_requires_rev0868_boundary",
        "future archives cannot omit the implementation or structural proof",
    )

    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
