#!/usr/bin/env python3
"""Fail-closed source audit for frozen daemon-heartbeat publication ownership."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED = (
    Path("CMakeLists.txt"),
    Path("include/anonsync_core_internal.hpp"),
    Path("include/anonsync_json_value.hpp"),
    Path("src/sync_daemon_heartbeat_document.hpp"),
    Path("src/sync_daemon_heartbeat_document.cpp"),
    Path("src/sync_daemon_heartbeat_publication.hpp"),
    Path("src/sync_daemon_heartbeat_publication.cpp"),
    Path("src/sync_domain.cpp"),
    Path("src/sync_domain_selftests.cpp"),
    Path("tests/sync_daemon_heartbeat_document_test.cpp"),
    Path("tests/sync_daemon_heartbeat_publication_test.cpp"),
    Path("tools/audit_sync_daemon_heartbeat_document.py"),
)

SERIALIZED_RESULT_FIELDS = (
    "service_instance_id",
    "service_restart_epoch",
    "daemon_heartbeat_process_id",
    "daemon_heartbeat_process_identity_format",
    "daemon_heartbeat_process_boot_id",
    "daemon_heartbeat_process_start_token",
    "daemon_id",
    "worker_id",
    "daemon_owner_lock_required",
    "daemon_owner_lock_acquired",
    "daemon_owner_lock_released",
    "daemon_owner_lock_reclaimed_expired",
    "daemon_owner_lock_id",
    "daemon_owner_lock_epoch",
    "daemon_owner_lock_acquired_at_epoch",
    "daemon_owner_lock_expires_at_epoch",
    "daemon_owner_lock_released_at_epoch",
    "service_lifecycle_preflight_checked",
    "service_lifecycle_preflight_passed",
    "service_lifecycle_live_owner_blocked",
    "service_lifecycle_heartbeat_checked",
    "service_lifecycle_heartbeat_existing_loaded",
    "service_lifecycle_heartbeat_existing_final",
    "service_lifecycle_heartbeat_existing_fresh",
    "service_lifecycle_heartbeat_existing_stale",
    "service_lifecycle_reentry_from_stale_heartbeat",
    "service_lifecycle_preflight_reason",
    "final_worker_lease_id",
    "final_worker_lease_epoch",
    "next_worker_lease_epoch",
    "next_scheduler_now_epoch",
    "passes_attempted",
    "passes_completed",
    "mutating_passes",
    "idle_passes",
    "startup_sidecar_recovery_attempted",
    "startup_sidecar_recovery_completed",
    "startup_sidecar_recovery_checkpoint_schema_version",
    "startup_sidecar_recovery_archived_checkpoint_migration_backfill_checked",
    "startup_sidecar_recovery_archived_checkpoint_exact_startup_hydration_supported",
    "startup_sidecar_recovery_archived_checkpoint_migration_backfill_required",
    "startup_sidecar_recovery_archived_checkpoint_migration_backfill_blocked_missing_lineage",
    "startup_sidecar_recovery_archived_checkpoint_claimed_paths_blocked_by_missing_lineage",
    "terminal_apply_workorders_checked",
    "terminal_apply_workorders_inserted",
    "terminal_apply_workorders_completed",
    "terminal_apply_workorders_already_completed",
    "terminal_apply_tombstone_workorders_completed",
    "terminal_apply_tombstone_targets_removed",
    "terminal_apply_tombstone_targets_already_absent",
    "terminal_apply_conflict_tombstone_workorders_completed",
    "terminal_apply_conflict_file_workorders_completed",
    "terminal_apply_conflict_copies_preserved",
    "terminal_apply_conflict_copies_reused",
    "terminal_apply_conflict_remote_tombstones_applied",
    "terminal_apply_conflict_remote_files_materialized",
    "workorder_rows_claimed",
    "workorder_rows_reclaimed",
    "workorder_rows_completed",
    "chunks_written",
    "bytes_written",
)

SERIALIZED_OPTION_FIELDS = (
    "sqlite_path",
    "session_id",
    "daemon_heartbeat_stale_after_seconds",
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def block_between(text: str, begin: str, end: str) -> str:
    start = text.find(begin)
    stop = text.find(end, start + len(begin)) if start >= 0 else -1
    return text[start:stop] if start >= 0 and stop > start else ""


def struct_block(text: str, name: str) -> str:
    start = text.find(f"struct {name}")
    if start < 0:
        return ""
    stop = text.find("\n};", start)
    return text[start : stop + 3] if stop >= 0 else ""


def emit(root: Path, output: Path | None, checks: list[Check], metrics: dict) -> int:
    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-sync-daemon-heartbeat-publication-audit-v2",
        "root": str(root),
        "passed": not violations,
        "passed_checks": len(checks) - len(violations),
        "total_checks": len(checks),
        "checks": [asdict(check) for check in checks],
        "metrics": metrics,
        "violations": violations,
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0 if not violations else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="AnonSync source root",
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
        return emit(root, args.json, checks, {})

    texts = {
        path: (root / path).read_text(encoding="utf-8") for path in REQUIRED
    }
    cmake = texts[Path("CMakeLists.txt")]
    internal = texts[Path("include/anonsync_core_internal.hpp")]
    json_value = texts[Path("include/anonsync_json_value.hpp")]
    header = texts[Path("src/sync_daemon_heartbeat_document.hpp")]
    source = texts[Path("src/sync_daemon_heartbeat_document.cpp")]
    adapter_header = texts[Path("src/sync_daemon_heartbeat_publication.hpp")]
    adapter = texts[Path("src/sync_daemon_heartbeat_publication.cpp")]
    domain = texts[Path("src/sync_domain.cpp")]
    selftests = texts[Path("src/sync_domain_selftests.cpp")]
    focused = texts[Path("tests/sync_daemon_heartbeat_document_test.cpp")]
    adapter_test = texts[Path("tests/sync_daemon_heartbeat_publication_test.cpp")]

    publication_block = struct_block(header, "SyncDaemonHeartbeatPublication final")
    json_block = struct_block(json_value, "Json final")

    require(
        "struct SyncDaemonHeartbeatDocument final" in header
        and "struct SyncDaemonHeartbeatOwnerLockDocument final" in header
        and "struct SyncDaemonHeartbeatPublication final" in header,
        "typed_publication_surface",
        "authority, owner generation, and frozen publication are explicit types",
    )
    require(
        all(token in publication_block for token in (
            "SyncDaemonHeartbeatDocument document;",
            "SyncDaemonHeartbeatServiceLifecycleObservation service_lifecycle;",
            "SyncDaemonHeartbeatLeaseObservation lease;",
            "SyncDaemonHeartbeatProgressObservation progress;",
        ))
        and "*" not in publication_block
        and "&" not in publication_block,
        "owning_publication_value",
        "publication owns values and retains no pointers or references into the broad result",
    )
    require(
        "kSyncDaemonHeartbeatMaximumJsonBytes" in header
        and "64U * 1024U" in header,
        "shared_document_byte_bound",
        "reader and publisher share one named 64 KiB protocol bound",
    )
    require(
        "anonsync_core" not in header
        and "openssl" not in header.lower()
        and "sqlite" not in header.lower(),
        "codec_header_dependency_direction",
        "focused schema header is independent of runtime, crypto, and SQLite umbrellas",
    )

    require(
        "struct Json final" in json_value
        and "std::map<std::string, Json> o;" in json_block
        and "JSON number is not an exact interoperable signed integer" in json_block,
        "dependency_light_json_owner",
        "the parser value has one small reusable header owner",
    )
    require(
        '#include "anonsync_json_value.hpp"' in internal
        and "struct Json" not in internal,
        "runtime_consumes_json_leaf",
        "runtime umbrella imports rather than redeclares the JSON value",
    )
    json_includes = re.findall(r'^#include\s+[<"]([^>"]+)[>"]',
                               json_value,
                               flags=re.MULTILINE)
    require(
        all(not any(token in include.lower() for token in (
            "anonsync_core",
            "openssl",
            "sqlite",
            "filesystem",
        )) for include in json_includes),
        "json_leaf_has_no_heavy_backedge",
        f"includes={json_includes}",
    )
    require(
        '#include "anonsync_json_value.hpp"' in source
        and '#include "anonsync_core_internal.hpp"' not in source
        and '#include "anonsync_core.hpp"' not in source,
        "codec_uses_json_leaf_only",
        "codec implementation no longer inherits the internal runtime umbrella",
    )
    require(
        '#include "anonsync_json_value.hpp"' in focused
        and "anonsync_core_internal.hpp" not in focused
        and "anonsync_core.hpp" not in focused,
        "focused_corpus_uses_json_leaf_only",
        "codec corpus compiles against the small schema surface",
    )

    require(
        source.count(
            "SyncDaemonHeartbeatDocument decode_sync_daemon_heartbeat_document_or_throw("
        ) == 1
        and source.count(
            "std::string encode_sync_daemon_heartbeat_document_or_throw("
        ) == 1,
        "single_codec_definition",
        "decode and encode entry points each have exactly one implementation",
    )
    require(
        "const SyncDaemonHeartbeatPublication& publication" in source
        and "const SyncDaemonHeartbeatDocument& document = publication.document;" in source
        and "validate_sync_daemon_heartbeat_document_or_throw(document);" in source
        and "validate_observational_numbers_or_throw(publication);" in source,
        "validate_exact_frozen_value",
        "validation and emission consume the same owning publication snapshot",
    )
    require(
        "SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions" not in source
        and "SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult" not in source
        and "result." not in source
        and "options." not in source,
        "broad_model_absent_from_codec",
        "codec cannot reread or reinterpret the mutable orchestration model",
    )
    require(
        "out.imbue(std::locale::classic());" in source
        and '#include <locale>' in source,
        "locale_independent_json_numbers",
        "JSON integer spelling is pinned to the classic locale before emission",
    )
    require(
        "payload.size() > kSyncDaemonHeartbeatMaximumJsonBytes" in source
        and "serialized document exceeds the reader byte bound" in source,
        "publisher_enforces_reader_bound",
        "encoder rejects any document that the bounded reader cannot admit",
    )
    require(
        "stale_at_epoch !=" in source
        and "heartbeat_epoch + document.stale_after_seconds" in source
        and "stale horizon exceeds exact JSON range" in source,
        "stale_horizon_recomputed",
        "stale authority is derived with exact-range fencing",
    )
    require(
        "cannot be final while its owner generation remains unreleased" in source
        and "final epoch does not equal owner release epoch" in source,
        "release_bound_finality",
        "finality requires the exact owner retirement transition",
    )
    require(
        "lockless document contains owner authority residue" in source,
        "lockless_residue_rejected",
        "disabled owner policy cannot carry latent owner fields",
    )
    require(
        "kMaximumExactJsonInteger" in source
        and "exceeds the exact interoperable JSON integer range" in source,
        "exact_json_integer_fence",
        "serialized authority and observations stay lossless in JSON",
    )

    require(
        "make_sync_daemon_heartbeat_publication_or_throw" in adapter_header
        and "SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions;" in adapter_header
        and "SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult;" in adapter_header
        and '#include "anonsync_core.hpp"' not in adapter_header,
        "narrow_adapter_header",
        "adapter header forward-declares the broad model and exposes one conversion",
    )
    require(
        adapter.count("make_sync_daemon_heartbeat_publication_or_throw(") == 1
        and "SyncDaemonHeartbeatPublication publication;" in adapter
        and "return publication;" in adapter,
        "single_owning_adapter_definition",
        "one compiled owner snapshots the broad model by value",
    )
    missing_result_mappings = [
        field for field in SERIALIZED_RESULT_FIELDS
        if f"result.{field}" not in adapter
    ]
    expected_result_counts = {
        field: (2 if field == "daemon_heartbeat_process_id" else 1)
        for field in SERIALIZED_RESULT_FIELDS
    }
    duplicate_result_mappings = [
        field for field, expected in expected_result_counts.items()
        if len(re.findall(rf"result\.{re.escape(field)}\b", adapter)) != expected
    ]
    require(
        not missing_result_mappings and not duplicate_result_mappings,
        "complete_unique_result_mapping",
        f"missing={missing_result_mappings}, nonunique={duplicate_result_mappings}",
    )
    missing_option_mappings = [
        field for field in SERIALIZED_OPTION_FIELDS
        if f"options.{field}" not in adapter
    ]
    duplicate_option_mappings = [
        field for field in SERIALIZED_OPTION_FIELDS
        if len(re.findall(rf"options\.{re.escape(field)}\b", adapter)) != 1
    ]
    require(
        not missing_option_mappings and not duplicate_option_mappings,
        "complete_unique_option_mapping",
        f"missing={missing_option_mappings}, nonunique={duplicate_option_mappings}",
    )
    require(
        'document.revision_id = "rev0840";' in adapter
        and 'document.format = "anonsync-sync-daemon-service-heartbeat-v2";' in adapter
        and 'document.operation = "sync-daemon-service-heartbeat";' in adapter,
        "current_markers_owned_by_adapter",
        "new publications carry the exact current format, revision, and operation",
    )

    require(
        '#include "sync_daemon_heartbeat_publication.hpp"' in domain
        and "make_sync_daemon_heartbeat_publication_or_throw(" in domain,
        "domain_consumes_publication_adapter",
        "domain freezes a publication before handing bytes to the codec",
    )
    writer_block = block_between(
        domain,
        "void write_sync_daemon_heartbeat_if_requested_or_throw",
        "SyncValidationResult run_sync_session_checkpoint_resume_transfer_workorder_daemon_loop",
    )
    require(
        "const SyncDaemonHeartbeatPublication publication" in writer_block
        and "make_sync_daemon_heartbeat_publication_or_throw(" in writer_block
        and "encode_sync_daemon_heartbeat_document_or_throw(publication)" in writer_block,
        "writer_freeze_then_encode_choreography",
        "writer constructs one frozen value and encodes that exact value",
    )
    reader_block = block_between(
        domain,
        "Json load_sync_daemon_heartbeat_json_or_throw",
        "bool sync_daemon_heartbeat_paths_match_lexically",
    )
    require(
        "kSyncDaemonHeartbeatMaximumJsonBytes" in reader_block
        and "kMaxHeartbeatJsonBytes" not in reader_block,
        "reader_uses_shared_bound",
        "runtime reader cannot drift from the encoder's publication ceiling",
    )
    require(
        "sync_daemon_heartbeat_json(" not in domain
        and "sync_daemon_heartbeat_required_u64_or_throw" not in domain
        and "sync_json_nonnegative_u64_field_or_zero" not in domain,
        "legacy_embedded_codec_removed",
        "permissive embedded codec helpers remain absent",
    )
    require(
        domain.count("decode_sync_daemon_heartbeat_document_or_throw(") >= 2,
        "shared_decode_policy",
        "daemon preflight and operator status consume the same decoder",
    )
    require(
        "not bound to the exact durable owner generation" in domain
        and "document.owner_lock.acquired_at_epoch ==" in domain
        and "document.owner_lock.expires_at_epoch ==" in domain,
        "exact_durable_generation_binding",
        "identity, epoch, acquisition, expiry, and release evidence are compared",
    )
    require(
        "sync_daemon_heartbeat_service_instance_matches_document_or_throw" in domain
        and domain.count(
            "sync_daemon_heartbeat_service_instance_matches_document_or_throw("
        ) >= 3
        and "checkpoint_resume_transfer_daemon_service_instance_id_or_throw(" in domain,
        "service_instance_material_binding",
        "service identity is recomputed from session, daemon, worker, and restart epoch",
    )
    require(
        "completed-owner-lock-retained" in domain
        and "failed-owner-lock-retained" in domain
        and "failed-exception-owner-lock-retained" in domain
        and "owner_generation_retired" in domain,
        "retained_owner_not_final",
        "release failures publish non-final retained-owner states",
    )

    require(
        "struct SyncDaemonHeartbeatLifecycleEvaluation final" in header
        and "evaluate_sync_daemon_heartbeat_lifecycle_or_throw" in header
        and source.count("evaluate_sync_daemon_heartbeat_lifecycle_or_throw(") == 1,
        "typed_lifecycle_policy_owner",
        "freshness, owner, and process-incarnation evidence have one pure policy owner",
    )
    require(
        domain.count("evaluate_sync_daemon_heartbeat_lifecycle_or_throw(") >= 2,
        "preflight_status_share_lifecycle_policy",
        "daemon preflight and operator status consume the same lifecycle decision",
    )
    require(
        "fresh non-final heartbeat blocks service re-entry until" in source
        and "heartbeat is stale while its durable owner generation is still live" in source
        and "heartbeat is stale while its exact process incarnation remains live" in source,
        "status_freshness_fail_closed",
        "shared policy exposes clock, durable-owner, and live-process blockers",
    )

    invariant_block = block_between(
        cmake,
        "foreach(ANONSYNC_INVARIANT_OWNED_SOURCE",
        "add_library(anonsync_core_lib",
    )
    core_link_block = block_between(
        cmake,
        "target_link_libraries(anonsync_core_lib",
        "if(ANONSYNC_USE_BUNDLED_SQLITE)",
    )
    focused_guard_block = block_between(
        cmake,
        "foreach(ANONSYNC_FOCUSED_BOUNDARY_TARGET",
        "if(TARGET anonsync_sync_bounded_regular_file_syscall_test)",
    )
    sanitizer_compile_block = block_between(
        cmake,
        "set(ANONSYNC_SANITIZER_COMPILE_TARGETS",
        "# Keep the multi-megabyte reviewed amalgamation",
    )
    sanitizer_link_block = block_between(
        cmake,
        "foreach(tgt\n      anonsync_core",
        "if(TARGET anonsync_sync_bounded_regular_file_syscall_test)",
    )
    require(
        "set(ANONSYNC_SYNC_DAEMON_HEARTBEAT_DOCUMENT_SOURCE" in cmake
        and "add_library(anonsync_sync_daemon_heartbeat_document STATIC" in cmake
        and "set(ANONSYNC_SYNC_DAEMON_HEARTBEAT_PUBLICATION_SOURCE" in cmake
        and "add_library(anonsync_sync_daemon_heartbeat_publication STATIC" in cmake,
        "focused_library_targets",
        "codec and broad-model adapter have separate compiled owners",
    )
    require(
        "ANONSYNC_SYNC_DAEMON_HEARTBEAT_DOCUMENT_SOURCE" in invariant_block
        and "ANONSYNC_SYNC_DAEMON_HEARTBEAT_PUBLICATION_SOURCE" in invariant_block,
        "sources_outside_core_translation_units",
        "configure guard prevents either owner being reabsorbed into the domain target",
    )
    require(
        "anonsync_sync_daemon_heartbeat_document" in core_link_block
        and "anonsync_sync_daemon_heartbeat_publication" in core_link_block,
        "one_way_runtime_dependency",
        "core consumes both focused owners",
    )
    require(
        all(target in focused_guard_block for target in (
            "anonsync_sync_daemon_heartbeat_document",
            "anonsync_sync_daemon_heartbeat_document_test",
            "anonsync_sync_daemon_heartbeat_publication",
            "anonsync_sync_daemon_heartbeat_publication_test",
        )),
        "no_focused_core_backedge",
        "configure guard forbids codec, adapter, and corpora linking back to core",
    )
    require(
        "target_link_libraries(anonsync_sync_daemon_heartbeat_document_test PRIVATE\n  anonsync_sync_daemon_heartbeat_document)" in cmake
        and "target_link_libraries(anonsync_sync_daemon_heartbeat_publication_test PRIVATE\n  anonsync_sync_daemon_heartbeat_publication)" in cmake,
        "focused_corpus_targets",
        "each corpus links only its focused owner",
    )
    require(
        "add_test(NAME anonsync_sync_daemon_heartbeat_document_test" in cmake
        and "add_test(NAME anonsync_sync_daemon_heartbeat_publication_test" in cmake,
        "focused_corpora_registered",
        "CTest gates both codec and mapping contracts",
    )
    require(
        "anonsync_sync_daemon_heartbeat_document" in sanitizer_compile_block
        and "anonsync_sync_daemon_heartbeat_publication" in sanitizer_compile_block
        and "anonsync_sync_daemon_heartbeat_document_test" in sanitizer_compile_block
        and "anonsync_sync_daemon_heartbeat_publication_test" in sanitizer_compile_block
        and "anonsync_sync_daemon_heartbeat_document_test" in sanitizer_link_block
        and "anonsync_sync_daemon_heartbeat_publication_test" in sanitizer_link_block,
        "sanitizer_compile_link_parity",
        "new leaf objects and executable corpora remain instrumented together",
    )

    require(
        "publisher cannot emit a document its bounded reader rejects" in focused
        and "JSON integer spelling is independent of the process-global locale" in focused
        and "publication codec cannot mint legacy PID-only evidence" in focused,
        "locale_size_and_downgrade_corpus",
        "codec corpus proves the two reproduced defects and fail-closed format minting",
    )
    require(
        "publication owns its snapshot instead of retaining broad model references" in adapter_test
        and "adapter freezes every serialized progress observation" in adapter_test
        and "frozen adapter output is accepted unchanged by the codec" in adapter_test,
        "adapter_snapshot_corpus",
        "mapping corpus covers ownership, complete observations, and codec handoff",
    )
    require(
        "clock staleness cannot supersede live durable owner authority" in focused
        and "clock staleness cannot impersonate exact process death" in focused
        and "stale plus expired owner plus absent or recycled process permits re-entry" in focused
        and "legacy non-final PID-only evidence fails closed" in focused,
        "lifecycle_decision_table_corpus",
        "focused policy tests cover owner, process, clock, legacy, and finality combinations",
    )
    require(
        "mirrors fresh-heartbeat preflight even after the durable owner generation expires" in selftests
        and "recomputes stale-horizon arithmetic before any owner or scheduler mutation" in selftests
        and "refuses a canonical but different owner generation before takeover" in selftests
        and "recomputes service-instance identity before takeover" in selftests
        and "same service-instance identity blocker as daemon preflight" in selftests,
        "integration_policy_coverage",
        "domain corpus proves arithmetic, owner, service identity, and status parity",
    )

    metrics = {
        "json_value_header_lines": len(json_value.splitlines()),
        "document_header_lines": len(header.splitlines()),
        "document_source_lines": len(source.splitlines()),
        "publication_header_lines": len(adapter_header.splitlines()),
        "publication_source_lines": len(adapter.splitlines()),
        "document_test_lines": len(focused.splitlines()),
        "publication_test_lines": len(adapter_test.splitlines()),
        "domain_lines": len(domain.splitlines()),
        "serialized_result_fields": len(SERIALIZED_RESULT_FIELDS),
        "serialized_option_fields": len(SERIALIZED_OPTION_FIELDS),
        "domain_decoder_calls": domain.count(
            "decode_sync_daemon_heartbeat_document_or_throw("
        ),
        "domain_encoder_calls": domain.count(
            "encode_sync_daemon_heartbeat_document_or_throw("
        ),
        "domain_publication_adapter_calls": domain.count(
            "make_sync_daemon_heartbeat_publication_or_throw("
        ),
        "domain_lifecycle_policy_calls": domain.count(
            "evaluate_sync_daemon_heartbeat_lifecycle_or_throw("
        ),
        "broad_model_tokens_in_codec": sum(
            source.count(symbol)
            for symbol in (
                "SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions",
                "SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult",
                "result.",
                "options.",
            )
        ),
    }
    return emit(root, args.json, checks, metrics)


if __name__ == "__main__":
    raise SystemExit(main())
