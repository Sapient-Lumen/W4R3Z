#!/usr/bin/env python3
"""Lexical hygiene audit for rev0889 file-effect accounting and migration.

This inventory checks reviewed type shape, source ordering, runtime fixture
presence, build registration, documentation, and release retention. It cannot
prove allocator behavior, C++ move elision, SQLite isolation/durability, digest
strength, crash safety, fairness, membership security, network privacy, or
package integrity.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

REQUIRED = (
    Path("CMakeLists.txt"),
    Path("README.md"),
    Path("src/sync_replica_file_effect_sqlite_owner.hpp"),
    Path("src/sync_replica_file_effect_sqlite_owner.cpp"),
    Path("src/sync_replica_file_delivery_service.hpp"),
    Path("src/sync_replica_file_delivery_service.cpp"),
    Path("tests/sync_replica_file_effect_sqlite_owner_test.cpp"),
    Path("tests/sync_replica_file_delivery_service_test.cpp"),
    Path("tools/audit_sync_file_effect_capacity_accounting.py"),
    Path("tools/verify_release_package.py"),
    Path("FILE_EFFECT_CAPACITY_ACCOUNTING_AUDIT_rev0889.md"),
    Path("FILE_EFFECT_DEVICE_ISOLATION_MIGRATION_AUDIT_rev0889.md"),
    Path("RECEIVER_STAGING_FAIRNESS_AUDIT_rev0889.md"),
    Path("REVISION_NOTES_rev0889.md"),
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


def function_body(text: str, signature: str, start_at: int = 0) -> str:
    start = text.find(signature, start_at)
    if start < 0:
        return ""
    brace = text.find("{", start + len(signature))
    if brace < 0:
        return ""
    depth = 0
    for index in range(brace, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    return ""


def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-file-effect-capacity-accounting-audit-v2",
        "scope": "lexical-hygiene-not-semantic-proof",
        "root": str(root),
        "passed": not violations,
        "passed_checks": len(checks) - len(violations),
        "total_checks": len(checks),
        "checks": [asdict(check) for check in checks],
        "violations": violations,
        "scope_nonclaim": (
            "source vocabulary/order cannot prove allocator behavior, C++ move "
            "elision, SQLite isolation or durability, digest strength, crash "
            "safety, fair scheduling, membership security, network privacy, or "
            "package integrity"
        ),
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
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
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
    readme = text["README.md"]
    owner_h = text["src/sync_replica_file_effect_sqlite_owner.hpp"]
    owner_cpp = text["src/sync_replica_file_effect_sqlite_owner.cpp"]
    service_h = text["src/sync_replica_file_delivery_service.hpp"]
    service_cpp = text["src/sync_replica_file_delivery_service.cpp"]
    owner_test = text["tests/sync_replica_file_effect_sqlite_owner_test.cpp"]
    service_test = text["tests/sync_replica_file_delivery_service_test.cpp"]
    verifier = text["tools/verify_release_package.py"]
    design = text["FILE_EFFECT_CAPACITY_ACCOUNTING_AUDIT_rev0889.md"]
    migration_design = text[
        "FILE_EFFECT_DEVICE_ISOLATION_MIGRATION_AUDIT_rev0889.md"
    ]
    fairness = text["RECEIVER_STAGING_FAIRNESS_AUDIT_rev0889.md"]
    notes = text["REVISION_NOTES_rev0889.md"]
    self_text = text["tools/audit_sync_file_effect_capacity_accounting.py"]

    require(
        cmake.count("anonsync_sync_file_effect_capacity_accounting_source_audit")
        >= 2
        and "tools/audit_sync_file_effect_capacity_accounting.py" in cmake,
        "capacity_accounting_audit_is_registered",
        "ordinary CTest retains the limited source inventory",
    )

    require(
        all(
            token in owner_h
            for token in (
                "max_effects_per_device",
                "max_retained_payload_bytes_per_device",
                "enum class SyncReplicaFileEffectCapacityConstraint",
                "FolderEffectCount",
                "FolderRetainedPayloadBytes",
                "DeviceEffectCount",
                "DeviceRetainedPayloadBytes",
                "struct SyncReplicaFileEffectActorUsage final",
                "struct SyncReplicaFileEffectDeviceUsage final",
                "does not claim that device_id is a human",
                "std::string device_usage_digest",
            )
        ),
        "public_contract_separates_folder_device_and_actor_epoch",
        "the API names exact local boundaries without inventing a membership principal",
    )

    require(
        all(
            token in owner_cpp
            for token in (
                "constexpr std::uint64_t kSchemaVersion = 3U",
                "constexpr std::uint64_t kLegacySchemaVersion = 2U",
                "CHECK(schema_version=2)",
                "CHECK(schema_version=3)",
                "device_count INTEGER NOT NULL",
                "device_usage_digest TEXT NOT NULL",
                "constexpr std::array<SchemaDefinition, 3U> kLegacySchema",
                "constexpr std::array<SchemaDefinition, 3U> kSchema",
            )
        ),
        "exact_v2_and_v3_schema_contracts_are_explicit",
        "migration accepts only the reviewed predecessor and current schema shapes",
    )

    derive_content = function_body(
        owner_cpp, "derive_content_attestation_or_throw("
    )
    require(
        ordered(
            derive_content,
            "std::map<SyncReplicaActor, SyncReplicaFileEffectActorUsage>",
            "operation.dot.actor",
            "actor retained payload bytes",
            "std::map<std::string, SyncReplicaFileEffectDeviceUsage>",
            "usage.actor.device_id",
            "device actor epochs",
            "out.actor_usage.push_back(std::move(usage))",
            "out.device_usage.push_back(std::move(usage))",
            "anonsync-replica-file-effect-device-usage-v1",
            "out.device_usage_digest = usage_digest.finish_hex()",
        ),
        "usage_is_rederived_from_complete_effect_closure",
        "actor epochs remain distinct while the device partition receives a deterministic witness",
    )

    derive_v3 = function_body(owner_cpp, "derive_attestation_or_throw(")
    require(
        ordered(
            derive_v3,
            "anonsync-replica-file-effect-cutpoint-v3",
            "digest_legacy_policy(cutpoint, limits)",
            "limits.max_effects_per_device",
            "limits.max_retained_payload_bytes_per_device",
            "out.device_usage.size()",
            "out.effect_set_digest",
            "out.device_usage_digest",
            "out.cutpoint_digest = cutpoint.finish_hex()",
        ),
        "v3_cutpoint_binds_policy_effects_and_device_partition",
        "device limits and derived usage cannot drift outside the durable cutpoint",
    )

    apply_projection = function_body(owner_cpp, "void apply_derived_snapshot(")
    require(
        ordered(
            apply_projection,
            "std::move(derived.actor_usage)",
            "std::move(derived.device_usage)",
            "std::move(derived.device_usage_digest)",
            "SnapshotProjection::PublicSnapshot",
            "push_back(std::move(stored.record))",
        )
        and "push_back(stored.record)" not in apply_projection,
        "public_projection_is_explicit_and_move_owned",
        "internal authority loads do not manufacture an unobserved O(history) record view",
    )

    load = function_body(owner_cpp, "load_state_or_throw(")
    require(
        ordered(
            load,
            "stored_device_count",
            "stored_device_usage_digest",
            "derive_attestation_or_throw(",
            "derived.device_usage.size()",
            "derived.device_usage_digest != stored_device_usage_digest",
            "durable cutpoint attestation mismatch",
            "apply_derived_snapshot(loaded, std::move(derived), projection)",
        ),
        "v3_load_recomputes_before_exposing_projection",
        "persisted device witnesses are checked projections rather than admission counters",
    )

    constructor = function_body(
        owner_cpp, "SyncReplicaFileEffectSqliteOwner::SyncReplicaFileEffectSqliteOwner("
    )
    require(
        ordered(
            constructor,
            "schema_matches(observed, kLegacySchema)",
            "validate_device_limits_or_throw(",
            "load_legacy_state_or_throw(",
            "migrated_limits.max_effects_per_device",
            "migrated_limits.max_retained_payload_bytes_per_device",
            "DROP TABLE main.sync_replica_file_effect_meta",
            "create v3 metadata",
            "insert_meta_or_throw(",
            "verify_schema_or_throw(db_, kSchema",
            "load_state_or_throw(",
            "v2-to-v3 migration changed retained effect authority",
            "transaction.commit()",
        ),
        "migration_rechecks_v2_then_replaces_metadata_atomically",
        "legacy rows and policy are restored before DDL and v3 is reloaded before commit",
    )

    stage = function_body(
        owner_cpp,
        "SyncReplicaFileEffectSqliteOwner::stage_with_diagnostics_or_throw(",
    )
    require(
        ordered(
            stage,
            "destination_path_is_blocked",
            "find_effect(loaded.stored",
            "payload_view_from_span(payload_bytes)",
            "SyncReplicaResourceBudget effect_budget",
            "SyncReplicaResourceBudget payload_budget",
            "SyncReplicaResourceBudget device_effect_budget",
            "SyncReplicaResourceBudget device_payload_budget",
            "effect_budget.would_exceed()",
            "payload_budget.would_exceed()",
            "device_effect_budget.would_exceed()",
            "device_payload_budget.would_exceed()",
            "SyncReplicaFileEffectCapacityBlock block",
            "transaction.commit()",
            "StoredEffect inserted",
            "encode_sync_replica_operation_canonical_or_throw(",
            "payload_from_span(payload_bytes)",
            "loaded.stored.insert(found, std::move(inserted))",
        ),
        "duplicate_and_all_capacity_decisions_precede_new_row_copy",
        "folder precedence is stable and blocked/duplicate requests do not construct a retained row",
    )

    receive = function_body(
        service_cpp, "SyncReplicaFileDeliveryService::receive_request_or_throw("
    )
    require(
        ordered(
            receive,
            "stage_with_diagnostics_or_throw(",
            "inbound.request = std::move(request)",
            "inbound.capacity_block = std::move(stage.capacity_block)",
            "EffectCapacityBlocked",
            "make_receipt_or_throw(",
        )
        and "inbound.request = request;" not in receive
        and "std::optional<SyncReplicaFileEffectCapacityBlock> capacity_block"
        in service_h
        and "receipt remains a bounded generic classification" in service_h,
        "service_keeps_capacity_detail_local_and_moves_payload_request",
        "device detail cannot become peer timing/evidence authority and no payload-bearing copy follows stage",
    )

    require(
        all(
            token in owner_test
            for token in (
                "test_device_isolation_schema_migration_and_restart",
                "test_v2_migration_fail_closed_and_rolls_back_ddl",
                "downgrade_effect_meta_to_v2_or_throw",
                "legacy_cutpoint_digest",
                "DeviceEffectCount",
                "DeviceRetainedPayloadBytes",
                "independent device admission",
                "did not roll back legacy DDL atomically",
                "device-usage metadata tamper was not rejected",
            )
        ),
        "runtime_owner_matrix_covers_migration_isolation_rollback_and_tamper",
        "compiled tests, rather than lexical shape, own the schema and quota claims",
    )

    require(
        all(
            token in service_test
            for token in (
                "anonsync-file-delivery-device-capacity",
                "older actor epoch",
                "DeviceEffectCount",
                "device-local detail escaped into downstream evidence or effect authority",
                "generic wire receipt did not classify device isolation as nonterminal",
                "device-capacity receipt did not release the exact attempt",
            )
        ),
        "runtime_service_proves_actor_epoch_isolation_and_generic_wire_receipt",
        "the receiver-local boundary is exercised through sender retry release",
    )

    require(
        "FILE_EFFECT_CAPACITY_ACCOUNTING_AUDIT_rev0889.md" in verifier
        and "FILE_EFFECT_DEVICE_ISOLATION_MIGRATION_AUDIT_rev0889.md" in verifier
        and "tools/audit_sync_file_effect_capacity_accounting.py" in verifier,
        "release_verifier_requires_device_isolation_surface",
        "the implementation, tests, audit, and design record cannot be omitted",
    )

    require(
        all(
            token in readme
            for token in (
                "Exact schema v3",
                "FILE_EFFECT_DEVICE_ISOLATION_MIGRATION_AUDIT_rev0889.md",
                "stable membership principal, total disk quota",
            )
        )
        and "Device-isolated capacity, exact migration" in notes
        and "completed narrow slice in rev0889" in fairness,
        "documentation_states_completed_slice_and_remaining_lifecycle_gap",
        "device hard limits are not mislabeled as fair scheduling or reclamation",
    )

    require(
        "cannot prove C++ allocation behavior" in design
        and "custom-VFS crash campaign" in migration_design
        and "cannot prove allocator behavior" in self_text
        and "does not claim fair resource allocation" in design,
        "audit_surfaces_preserve_semantic_nonclaims",
        "lexical inventory and focused fault injection are not presented as universal proof",
    )

    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
