#!/usr/bin/env python3
"""Lexical hygiene audit for rev1018 history-cold service construction.

Source spelling is not semantic proof. Compiler, sanitizer, runtime allocation,
history-read-fence, reconstruction, and package evidence remain load-bearing.
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
    Path("HISTORY_COLD_PEER_SERVICE_STARTUP_AUDIT_rev1018.md"),
    Path("REVISION_NOTES_rev1018.md"),
    Path("src/sync_replica_delivery_service.cpp"),
    Path("src/sync_replica_reconciliation_service.cpp"),
    Path("src/sync_replica_file_delivery_service.cpp"),
    Path("src/sync_replica_file_effect_sqlite_owner.hpp"),
    Path("src/sync_replica_file_effect_sqlite_owner.cpp"),
    Path("tests/sync_replica_reconciliation_source_frame_memory_test.cpp"),
    Path("tools/audit_sync_replica_service_startup.py"),
    Path("tools/audit_sync_file_payload_store.py"),
    Path("tools/verify_release_package.py"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def function_window(text: str, signature: str, next_signature: str) -> str:
    start = text.find(signature)
    if start < 0:
        return ""
    end = text.find(next_signature, start + len(signature))
    return text[start:] if end < 0 else text[start:end]


def normalized_prose(text: str) -> str:
    return " ".join(text.replace("**", "").replace("`", "").split())


def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [item.check_id for item in checks if not item.passed]
    report = {
        "format": "anonsync-peer-service-startup-audit-v1",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source spelling does not prove history-read absence, allocation "
            "counts, four-terabyte service behavior, RSS, sanitizer cleanliness, "
            "source reconstruction, or package identity"
        ),
        "root": str(root),
        "passed": not violations,
        "passed_checks": len(checks) - len(violations),
        "total_checks": len(checks),
        "checks": [asdict(item) for item in checks],
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
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    checks: list[Check] = []

    def require(condition: bool, check_id: str, detail: str) -> None:
        checks.append(Check(check_id, bool(condition), detail))

    missing = [path.as_posix() for path in REQUIRED if not (root / path).is_file()]
    require(not missing, "required_files_exist", f"missing={missing}")
    bootstrap_candidates = (
        root.parent.parent / "BOOTSTRAPROSE.md",
        root.parent / "BOOTSTRAPROSE.md",
    )
    bootstrap_path = next((path for path in bootstrap_candidates if path.is_file()), None)
    require(bootstrap_path is not None, "bootstrap_exists", "release-root runbook is visible")
    if missing or bootstrap_path is None:
        return emit(root, args.json, checks)

    text = {path.as_posix(): (root / path).read_text(encoding="utf-8") for path in REQUIRED}
    bootstrap = bootstrap_path.read_text(encoding="utf-8")
    cmake = text["CMakeLists.txt"]
    readme = text["README.md"]
    design = text["HISTORY_COLD_PEER_SERVICE_STARTUP_AUDIT_rev1018.md"]
    notes = text["REVISION_NOTES_rev1018.md"]
    delivery = text["src/sync_replica_delivery_service.cpp"]
    reconciliation = text["src/sync_replica_reconciliation_service.cpp"]
    file_delivery = text["src/sync_replica_file_delivery_service.cpp"]
    effect_h = text["src/sync_replica_file_effect_sqlite_owner.hpp"]
    effect_c = text["src/sync_replica_file_effect_sqlite_owner.cpp"]
    runtime = text["tests/sync_replica_reconciliation_source_frame_memory_test.cpp"]
    structural = text["tools/audit_sync_file_payload_store.py"]
    verifier = text["tools/verify_release_package.py"]

    delivery_ctor = function_window(
        delivery,
        "SyncReplicaDeliveryService::SyncReplicaDeliveryService(",
        "SyncReplicaSqliteSnapshot SyncReplicaDeliveryService::snapshot_or_throw(",
    )
    reconciliation_ctor = function_window(
        reconciliation,
        "SyncReplicaReconciliationService::SyncReplicaReconciliationService(",
        "void SyncReplicaReconciliationService::\nrequire_current_owner_identity_or_throw(",
    )
    file_delivery_ctor = function_window(
        file_delivery,
        "SyncReplicaFileDeliveryService::SyncReplicaFileDeliveryService(",
        "SyncReplicaFileEffectSqliteSnapshot\nSyncReplicaFileDeliveryService::effect_snapshot_or_throw(",
    )
    effect_meta = function_window(
        effect_c,
        "struct LoadedEffectMeta final",
        "void validate_effect_identity_cutpoint_or_throw(",
    )
    effect_identity = function_window(
        effect_c,
        "[[nodiscard]] SyncReplicaFileEffectSqliteIdentityCutpoint\nload_identity_cutpoint_or_throw(",
        "[[nodiscard]] LoadedState load_state_or_throw(",
    )
    effect_complete = function_window(
        effect_c,
        "[[nodiscard]] LoadedState load_state_or_throw(",
        "void bind_limits_or_throw(",
    )
    runtime_case = function_window(
        runtime,
        "void test_peer_service_startup_is_history_cold_for_four_tib_tree()",
        "}  // namespace",
    )

    require(
        "SyncReplicaSqliteIdentityCutpoint identity" in delivery_ctor
        and "owner_.identity_cutpoint_or_throw()" in delivery_ctor
        and "snapshot_or_throw()" not in delivery_ctor,
        "delivery_constructor_uses_bounded_identity_cutpoint",
        "evidence delivery does not reload retained replica history at construction",
    )
    require(
        "SyncReplicaSqliteIdentityCutpoint identity" in reconciliation_ctor
        and "owner_.identity_cutpoint_or_throw()" in reconciliation_ctor
        and "identity.limits.model" in reconciliation_ctor
        and "snapshot_or_throw()" not in reconciliation_ctor,
        "reconciliation_constructor_uses_bounded_identity_and_policy_cutpoint",
        "reconciliation obtains identity and durable model limits without a complete snapshot",
    )
    require(
        "SyncReplicaFileEffectSqliteIdentityCutpoint effect" in file_delivery_ctor
        and "identity_cutpoint_or_throw()" in file_delivery_ctor
        and "snapshot_or_throw()" not in file_delivery_ctor,
        "file_delivery_constructor_uses_bounded_effect_cutpoint",
        "file delivery does not reload retained file effects at construction",
    )
    require(
        "struct SyncReplicaFileEffectSqliteIdentityCutpoint final" in effect_h
        and "SyncReplicaFileEffectSqliteIdentityCutpoint\n    identity_cutpoint_or_throw();" in effect_h
        and "It never loads canonical operations or payloads" in effect_h,
        "effect_owner_declares_bounded_service_composition_cutpoint",
        "the header states the exact bounded authority and its history/payload nonclaim",
    )
    require(
        "struct LoadedEffectMeta final" in effect_meta
        and "SELECT schema_version,folder_id,root_path,root_authority_digest" in effect_meta
        and "sqlite_column_text_or_throw(\n        meta.stmt, 23" in effect_meta
        and "require_done_or_throw(meta.stmt" in effect_meta,
        "effect_metadata_has_one_exact_24_column_decoder",
        "bounded and complete paths share one fixed metadata codec",
    )
    require(
        "read_effect_meta_or_throw(db, label)" in effect_identity
        and "validate_effect_identity_cutpoint_or_throw" in effect_identity
        and "load_effect_rows_or_throw" not in effect_identity,
        "bounded_effect_cutpoint_is_history_cold",
        "the cutpoint re-attests metadata without decoding retained effect rows",
    )
    require(
        "read_effect_meta_or_throw(db, label)" in effect_complete
        and "load_effect_rows_or_throw(" in effect_complete
        and "derive_attestation_or_throw(" in effect_complete,
        "complete_effect_snapshot_preserves_full_authority",
        "the startup correction does not remove the complete cold reconstruction oracle",
    )
    require(
        "constexpr std::uint64_t kFiles = 64U" in runtime_case
        and "64ULL * 1024ULL * 1024ULL * 1024ULL" in runtime_case
        and "4ULL * 1024ULL * 1024ULL * 1024ULL * 1024ULL" in runtime_case
        and "static_assert(kFiles * kFileBytes == kLogicalTreeBytes)" in runtime_case,
        "runtime_fixture_binds_exact_logical_four_tib_shape",
        "64 logical files at 64 GiB each equal exactly 4 TiB",
    )
    require(
        'HistoryReadFence replica_fence{"sync_replica_operations"' in runtime_case
        and 'HistoryReadFence effect_fence{"sync_replica_file_effects"' in runtime_case
        and "replica_owner.snapshot_or_throw()" in runtime_case
        and "effect_owner.snapshot_or_throw()" in runtime_case
        and "replica_control_blocked" in runtime_case
        and "effect_control_blocked" in runtime_case,
        "runtime_has_complete_snapshot_negative_controls",
        "the live authorizer fences prove they would catch both historical scan paths",
    )
    require(
        "SyncReplicaDeliveryService evidence_service" in runtime_case
        and "SyncReplicaReconciliationService reconciliation_service" in runtime_case
        and "SyncReplicaFileDeliveryService file_service" in runtime_case
        and "attempted to read retained history" in runtime_case,
        "runtime_constructs_all_three_services_under_history_fences",
        "evidence, reconciliation, and file delivery remain history-cold together",
    )
    require(
        "arm_large_allocations(64U * 1024U)" in runtime_case
        and "startup_allocations.count == 0U" in runtime_case
        and "startup_allocations.bytes == 0U" in runtime_case
        and "allocated at least one 64 KiB history-shaped buffer" in runtime_case,
        "runtime_binds_zero_large_constructor_allocations",
        "all three constructors allocate no block at or above 64 KiB",
    )
    require(
        "anonsync_sync_replica_file_delivery_service" in cmake
        and "anonsync_sync_replica_service_startup_source_audit" in cmake
        and "tools/audit_sync_replica_service_startup.py" in cmake,
        "build_and_registry_bind_runtime_and_focused_audit",
        "the memory executable has the required service dependency and the audit is registered",
    )
    require(
        "HISTORY_COLD_PEER_SERVICE_STARTUP_AUDIT_rev1018.md" in verifier
        and "REVISION_NOTES_rev1018.md" in verifier
        and "audit_sync_replica_service_startup.py" in verifier
        and "rev1018_history_cold_startup" in structural,
        "release_and_structural_policy_bind_rev1018_surfaces",
        "the archive cannot omit the implementation, runtime proof, design, notes, or focused audit",
    )
    prose = normalized_prose("\n".join((design, notes, readme, bootstrap)))
    require(
        all(token in prose for token in (
            "O(history)", "4 TiB", "64 GiB", "64 KiB", "logical",
            "not a measured whole-process RSS", "multi-terabyte",
            "rename/move", "directories", "conflicts", "selective-sync",
            "ENOSPC", "Android", "Tor", "I2P",
        )),
        "benefit_and_nonclaims_are_explicit",
        "the bounded constructor win is not overstated as solved startup or product breadth",
    )
    require(
        "owners still perform one complete cold reconstruction" in design
        or "owners remain O(history)" in notes,
        "remaining_owner_history_cost_is_named",
        "the next measured bottleneck is not hidden by the service-level correction",
    )
    require(
        all(token not in (design + notes + readme + bootstrap) for token in (
            "VALIDATION_PENDING_REV1018",
            "ARCHIVE_PENDING_REV1018",
            "CODENAME_PENDING_REV1018",
        )),
        "final_validation_and_release_cutpoint_are_sealed",
        "the audit cannot pass before exact validation and archive facts replace every placeholder",
    )
    require(
        "lexical-hygiene-not-semantic-proof" in text["tools/audit_sync_replica_service_startup.py"]
        and "Source spelling is not semantic proof" in text["tools/audit_sync_replica_service_startup.py"],
        "focused_audit_disclaims_semantic_authority",
        "compiler, sanitizer, runtime, reconstruction, and package evidence remain load-bearing",
    )
    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
