#!/usr/bin/env python3
"""Lexical hygiene audit for owned outbox liveness time.

This inventories reviewed source ownership and ordering. It does not claim
semantic proof of host-clock quality, procfs behavior, or linearization.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED = (
    Path("CMakeLists.txt"),
    Path("src/sync_replica_outbox_clock.hpp"),
    Path("src/sync_replica_outbox_clock.cpp"),
    Path("src/sync_replica_outbox_clock_linux.cpp"),
    Path("src/sync_replica_outbox_clock_linux_internal.hpp"),
    Path("src/sync_system_epoch_identity.hpp"),
    Path("src/sync_system_epoch_identity.cpp"),
    Path("tests/sync_system_epoch_identity_test.cpp"),
    Path("src/sync_replica_sqlite_owner.hpp"),
    Path("src/sync_replica_sqlite_owner.cpp"),
    Path("tests/sync_replica_outbox_clock_test.cpp"),
    Path("src/anonsync_replica.cpp"),
    Path("tests/sync_replica_sqlite_owner_test.cpp"),
    Path("tests/sync_replica_delivery_service_test.cpp"),
    Path("tools/test_anonsync_replica_cli.py"),
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
                return text[start : index + 1]
    return ""


def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-sync-replica-outbox-clock-audit-v2",
        "scope": "lexical-hygiene-not-semantic-proof",
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
    header = text["src/sync_replica_outbox_clock.hpp"]
    source = text["src/sync_replica_outbox_clock.cpp"]
    linux = text["src/sync_replica_outbox_clock_linux.cpp"]
    linux_internal = text[
        "src/sync_replica_outbox_clock_linux_internal.hpp"
    ]
    epoch_header = text["src/sync_system_epoch_identity.hpp"]
    epoch_source = text["src/sync_system_epoch_identity.cpp"]
    epoch_runtime = text["tests/sync_system_epoch_identity_test.cpp"]
    owner_header = text["src/sync_replica_sqlite_owner.hpp"]
    owner = text["src/sync_replica_sqlite_owner.cpp"]
    runtime = text["tests/sync_replica_outbox_clock_test.cpp"]
    replica_cli = text["src/anonsync_replica.cpp"]
    owner_runtime = text["tests/sync_replica_sqlite_owner_test.cpp"]
    delivery_runtime = text["tests/sync_replica_delivery_service_test.cpp"]
    process_runtime = text["tools/test_anonsync_replica_cli.py"]
    verifier = text["tools/verify_release_package.py"]

    require(
        all(
            token in header
            for token in (
                "source_id",
                "boot_id",
                "time_namespace_id",
                "realtime_ns",
                "boottime_ns",
                "uncertainty_ns",
                "synchronization",
            )
        ),
        "observation_names_identity_quality_and_dual_clock_material",
        "wall time is never accepted without source, boot, namespace, monotonic, and uncertainty evidence",
    )
    require(
        all(
            token in header
            for token in (
                "max_uncertainty_ns",
                "max_forward_step_seconds",
                "max_realtime_lag_seconds",
                "HardMaxUncertainty",
                "HardMaxForwardStep",
                "HardMaxRealtimeLag",
            )
        ),
        "clock_policy_has_independent_durable_and_hard_bounds",
        "uncertainty, forward jumps, and wall-clock stalls fail closed under explicit ceilings",
    )
    require(
        all(
            token in header
            for token in (
                "SyncReplicaOutboxClockAnchor",
                "observation_generation",
                "recovery_generation",
                "accepted",
                "rejected",
                "LegacyUnbound",
                "Quarantined",
            )
        ),
        "state_retains_anchor_generations_and_both_sides_of_quarantine",
        "restart cannot forget what was trusted, what was rejected, or which recovery named the quarantine",
    )

    require(
        "SynchronizationUnknown = 11U" in header
        and "SyncReplicaOutboxClockAnomaly::SynchronizationUnknown" in source
        and "synchronization-unknown" in source,
        "unknown_and_unsynchronized_quality_have_distinct_durable_anomalies",
        "capability uncertainty is not mislabeled as proven clock-discipline failure",
    )

    validate_policy = function_body(
        source, "void validate_sync_replica_outbox_clock_policy_or_throw("
    )
    require(
        all(
            token in validate_policy
            for token in (
                "max_uncertainty_ns == 0U",
                "kSyncReplicaOutboxClockHardMaxUncertaintyNs",
                "max_forward_step_seconds == 0U",
                "kSyncReplicaOutboxClockHardMaxForwardStepSeconds",
                "max_realtime_lag_seconds == 0U",
                "kSyncReplicaOutboxClockHardMaxRealtimeLagSeconds",
            )
        ),
        "policy_validation_rejects_zero_and_overhard_limits",
        "configuration cannot disable or overflow any liveness tripwire",
    )
    validate_state = function_body(
        source, "void validate_sync_replica_outbox_clock_state_or_throw("
    )
    require(
        all(
            token in validate_state
            for token in (
                "recovery generation exceeds observation generation",
                "accepted observation is not synchronized",
                "accepted observation has no coherent drift anchor",
                "invalid uninitialized clock state",
                "invalid healthy clock state",
                "incomplete clock quarantine evidence",
                "invalid legacy-unbound quarantine",
                "quarantine discarded its rejected observation",
            )
        ),
        "state_validation_rejects_partial_or_laundered_clock_authority",
        "health, evidence, anchor, anomaly, and generations form one exact state machine",
    )
    validate_policy_state = function_body(
        source, "void validate_sync_replica_outbox_clock_state_against_policy_or_throw("
    )
    require(
        "accepted clock uncertainty exceeds durable policy" in validate_policy_state
        and "cumulative forward-step policy" in validate_policy_state
        and "cumulative realtime-lag policy" in validate_policy_state,
        "retained_state_is_reproved_against_durable_policy",
        "policy replacement and restore cannot reinterpret an already-accepted clock outside current limits",
    )

    observe = function_body(
        source, "observe_sync_replica_outbox_clock_or_throw("
    )
    require(
        ordered(
            observe,
            "AlreadyQuarantined",
            "synchronization",
            "max_uncertainty_ns",
            "source_id",
            "boot_id",
            "time_namespace_id",
            "boottime_ns < accepted.boottime_ns",
            "realtime_ns < accepted.realtime_ns",
            "cumulative_forward_step_exceeds_policy",
            "cumulative_realtime_lag_exceeds_policy",
            "usable_epoch < current.high_water_epoch",
        ),
        "observation_order_is_sticky_quality_identity_rollback_then_drift",
        "an anomalous sample cannot mint time, and ordinary observation cannot clear quarantine",
    )
    require(
        "*current.anchor" in observe
        and "if (!next.anchor) next.anchor = observation_anchor(observation)" in observe
        and "accepted.boottime_ns" not in function_body(
            source, "cumulative_forward_step_exceeds_policy("
        ),
        "drift_is_measured_from_recovery_anchor_not_only_previous_sample",
        "many individually-small wall-clock steps cannot launder an unbounded cumulative jump",
    )

    recover = function_body(
        source, "recover_sync_replica_outbox_clock_or_throw("
    )
    require(
        ordered(
            recover,
            "clock is not quarantined",
            "recovery generation does not name current quarantine",
            "recovery observation is unsynchronized",
            "recovery observation exceeds uncertainty policy",
            "recovery would move below durable high-water",
            "next.anchor = observation_anchor(observation)",
        ),
        "recovery_is_explicit_generation_fenced_and_forward_only",
        "operator recovery binds a fresh anchor without silently erasing the durable time floor",
    )

    encode = function_body(
        source, "encode_sync_replica_outbox_clock_state_canonical_or_throw("
    )
    decode = function_body(
        source, "decode_sync_replica_outbox_clock_state_canonical_or_throw("
    )
    require(
        "outbox-clock-state-v2" in source
        and "kSyncReplicaOutboxClockStateMaxCanonicalBytes" in encode
        and "anchor marker" in decode
        and "accepted marker" in decode
        and "rejected marker" in decode
        and "canonical clock state has trailing bytes" in source,
        "canonical_encoding_is_versioned_bounded_and_complete",
        "every authority-bearing optional field is framed and noncanonical bytes fail closed",
    )

    linux_class_start = linux.find(
        "class LinuxSyncReplicaOutboxClockSource final"
    )
    system = function_body(
        linux[linux_class_start:] if linux_class_start >= 0 else "",
        "SyncReplicaOutboxClockObservation observe_or_throw(",
    )
    require(
        "/proc/thread-self/ns/time" in linux
        and "/proc/self/ns/time" not in linux
        and system.count("read_time_namespace_or_throw") >= 2
        and system.count("boot_id") >= 2,
        "linux_identity_is_calling_thread_scoped_and_double_sampled",
        "setns on another thread cannot be mistaken for the clock-owning thread's namespace identity",
    )
    require(
        ordered(
            system,
            "CLOCK_BOOTTIME",
            "adjtimex",
            "CLOCK_REALTIME",
            "CLOCK_BOOTTIME",
            "namespace_after",
            "boot_after",
        )
        and "TIME_ERROR" in system
        and "STA_UNSYNC" in system
        and "STA_CLOCKERR" in system,
        "linux_sample_brackets_realtime_with_boottime_and_sync_quality",
        "sample span contributes uncertainty and kernel unsynchronized states are never labeled healthy",
    )
    require(
        '#include "sync_system_epoch_identity.hpp"' in linux
        and "observe_sync_system_boot_identity_or_throw" in linux
        and "O_NOFOLLOW" in epoch_source
        and "kMaximumBootIdentityBytes" in epoch_source
        and "sync_system_parse_boot_id_text_or_throw" in epoch_header
        and "repeated newline is not normalized into evidence" in epoch_runtime
        and "kernel_error_us * 1000ULL" in linux
        and "sample_span_ns" in linux,
        "linux_procfs_and_uncertainty_inputs_are_bounded",
        "the shared boot reader rejects symlink/framing substitution while clock uncertainty arithmetic remains checked",
    )
    require(
        all(
            token in linux_internal
            for token in (
                "feature-generation hint",
                "Bound",
                "AbsentBeforeMainlineFeature",
                "IdentityUnavailable",
                "FatalError",
                "ENOENT",
                "EACCES",
                "EPERM",
            )
        )
        and "kernel that supports time namespaces" not in linux,
        "kernel_version_is_a_hint_not_time_namespace_capability_proof",
        "only an observed calling-thread namespace handle can be labeled bound",
    )
    require(
        "timens-unavailable" in linux
        and "timens-pre-mainline-unavailable" in linux
        and "namespace_identity_is_bound" in system
        and ordered(
            system,
            "clock_source_id",
            "time_namespace_digest",
            "namespace_identity_is_bound",
            "SyncReplicaOutboxClockSynchronization::Unknown",
        ),
        "unbound_namespace_identity_becomes_unknown_durable_evidence",
        "missing or hidden identity remains observable but cannot mint synchronized liveness authority",
    )

    operator_class_start = linux.find(
        "class OperatorTrustedSyncReplicaOutboxClockSource final"
    )
    operator_clock = function_body(
        linux[operator_class_start:] if operator_class_start >= 0 else "",
        "SyncReplicaOutboxClockObservation observe_or_throw(",
    )
    require(
        all(
            token in header
            for token in (
                "SyncReplicaOperatorTrustedClockProfile",
                "authority_id",
                "claimed_uncertainty_ns",
                "operator assertions, not measurements",
                "must not select this profile implicitly",
                "make_operator_trusted_sync_replica_outbox_clock_source_or_throw",
            )
        )
        and ordered(
            operator_clock,
            "boot_id before sample",
            "namespace_before",
            "CLOCK_BOOTTIME",
            "CLOCK_REALTIME",
            "CLOCK_BOOTTIME",
            "namespace_after",
            "boot_id after sample",
            "claimed_uncertainty_ns",
            "SyncReplicaOutboxClockSynchronization::Synchronized",
        )
        and "--operator-clock-authority-id" in replica_cli
        and "--operator-clock-uncertainty-ns" in replica_cli
        and "make_operator_trusted_sync_replica_outbox_clock_source_or_throw"
        in replica_cli
        and "if (!has_authority) return {};" in replica_cli
        and "has_authority != has_uncertainty" in replica_cli
        and "test_operator_trusted_source_shape" in runtime,
        "operator_trusted_clock_is_explicit_bounded_and_runtime_pinned",
        "container clock trust is a named deployment assertion with bracketed sampling, hard uncertainty bounds, explicit CLI selection, and focused runtime coverage",
    )

    explicit_observe = function_body(
        owner, "SyncReplicaSqliteOwner::observe_outbox_clock_or_throw()"
    )
    require(
        "observe_outbox_clock_or_throw();" in owner_header
        and ordered(
            explicit_observe,
            "SyncSqliteTransactionMode::Immediate",
            "require_write_authority_or_throw",
            "load_state_or_throw",
            "clock_source_->observe_or_throw",
            "publish_outbox_clock_observation_or_throw",
            "attest_and_commit_clock_observation_or_throw",
        )
        and "accept_outbox_clock_observation_or_commit_quarantine_or_throw"
        not in explicit_observe,
        "explicit_clock_probe_publishes_exact_state_without_spending_dispatch_authority",
        "an operator probe samples under the writer lock, reuses the reviewed exact-CAS publication path, and returns quarantine instead of translating it into a work-path exception",
    )
    require(
        all(
            token in replica_cli
            for token in (
                '"clock-observe"',
                '"clock-recover"',
                "expected-observation-generation",
                "outbox_clock_observation_outcome_name",
                "append_outbox_clock_state_json_fields",
                "DatabaseOpenDisposition::ExistingOperational",
            )
        )
        and all(
            token in process_runtime
            for token in (
                "initial clock observation",
                "source-change quarantine",
                "generation-fenced clock recovery",
                "clock is not quarantined",
            )
        ),
        "product_cli_exposes_observe_quarantine_and_generation_fenced_recovery",
        "the shipped process can diagnose and explicitly recover a sticky clock quarantine, with the full healthy-to-quarantined-to-healthy sequence proven across process invocations",
    )

    claim_wrapper = function_body(
        owner, "SyncReplicaSqliteOwner::claim_next_outbox_or_throw("
    )
    delivery_claim_wrapper = function_body(
        owner, "SyncReplicaSqliteOwner::claim_next_outbox_for_delivery_or_throw("
    )
    claim = function_body(
        owner, "SyncReplicaSqliteOwner::claim_next_outbox_impl_or_throw("
    )
    settle = function_body(owner, "SyncReplicaSqliteOwner::settle_outbox_or_throw(")
    require(
        "std::uint64_t now_epoch" not in owner_header
        and "PreparedOutboxClockObservation" not in owner
        and "clock precondition remained contended" not in owner,
        "caller_time_and_stale_prelock_sampling_are_removed",
        "the owner, not its caller or an aged precondition loop, supplies liveness time",
    )
    require(
        "claim_next_outbox_impl_or_throw" in claim_wrapper
        and "claim_next_outbox_impl_or_throw" in delivery_claim_wrapper
        and ordered(
            claim,
            "random_claim_entropy_or_throw",
            "SyncSqliteTransaction transaction",
            "SyncSqliteTransactionMode::Immediate",
            "load_state_or_throw",
            "clock_source_->observe_or_throw",
            "accept_outbox_clock_observation_or_commit_quarantine_or_throw",
        ),
        "claim_samples_time_after_writer_lock_and_full_restore",
        "both public claim surfaces share one core whose expiry authority receives a real SQLite serialization point",
    )
    require(
        ordered(
            settle,
            "SyncSqliteTransactionMode::Immediate",
            "load_state_or_throw",
            "find_outbox_intent",
            "IntentMissing",
            "found->lease.claim_id != claim_id",
            "StaleClaim",
            "clock_source_->observe_or_throw",
            "sync_replica_outbox_claim_status_at_or_throw",
        ),
        "nonmatching_receipts_do_not_sample_or_ratchet_clock_state",
        "only an exact current receipt reaches the liveness decision",
    )

    require(
        all(
            token in runtime
            for token in (
                "cumulative_forward_step_tripwire",
                "individually-small steps must not launder",
                "split wall-clock stalls",
                "ordinary observation must not silently clear quarantine",
                "recovery must name the exact quarantine generation",
                "legacy high-water must migrate as explicit unbound quarantine",
                "retained cumulative drift must fit a replacement policy",
                "system clock smoke observation",
                "test_linux_time_namespace_probe_classification",
                "successful stat must be the only bound-identity proof",
                "unavailable capability must become durable quarantine evidence",
                "synchronization-unknown",
            )
        ),
        "pure_runtime_pins_cumulative_drift_quarantine_recovery_and_codec",
        "the deterministic state machine covers the adversarial boundaries introduced by schema v5",
    )
    require(
        all(
            token in owner_runtime
            for token in (
                "test_clock_sampling_is_inside_writer_transaction",
                "was sampled before SQLite writer authority",
                "competing_writer_was_blocked",
                "v2 migration must not relabel a caller epoch as trusted host time",
                "v3 migration must quarantine its caller-supplied legacy epoch",
                "TEMP-trigger clock mutation escaped staged re-attestation",
                "clock rollback was not durably isolated from receipt authority",
                "test_unknown_clock_capability_is_durably_quarantined",
                "restart forgot the synchronization-unknown quarantine cutpoint",
                "test_explicit_clock_observation_and_recovery_preserve_replica_authority",
                "explicit observation bypassed sticky clock quarantine",
                "stale recovery generation changed the durable cutpoint",
            )
        ),
        "owner_runtime_pins_linearization_migration_and_tamper_recovery",
        "the owner proves lock-local sampling, migration quarantine, and durable clock-tamper isolation",
    )
    require(
        all(
            token in delivery_runtime
            for token in (
                "test_ambiguous_receiver_commit_survives_restart_and_stale_receipt",
                "ambiguous retry rewrote receiver evidence instead of returning duplicate",
                "old ambiguous receipt settled the replacement attempt",
                "fresh duplicate receipt did not settle ambiguous delivery",
                "settled ambiguous receipt replay changed sender cutpoint",
            )
        ),
        "delivery_service_runtime_pins_ambiguous_commit_and_duplicate_recovery",
        "the service proves duplicate recovery and stale-receipt fencing across two independent SQLite cutpoints",
    )
    require(
        all(
            token in cmake
            for token in (
                "anonsync_sync_replica_outbox_clock",
                "src/sync_replica_outbox_clock.cpp",
                "src/sync_replica_outbox_clock_linux.cpp",
                "anonsync_sync_replica_outbox_clock_test",
                "tests/sync_replica_outbox_clock_test.cpp",
                "audit_sync_replica_outbox_clock.py",
            )
        ),
        "clock_library_runtime_and_structural_audit_are_registered",
        "the authority slice participates in normal, sanitizer, and source-audit lanes",
    )
    require(
        "revision_number >= 875" in verifier
        and "revision_number is not None and revision_number >= 897" in verifier
        and all(
            token in verifier
            for token in (
                "src/sync_replica_outbox_clock.hpp",
                "src/sync_replica_outbox_clock.cpp",
                "src/sync_replica_outbox_clock_linux.cpp",
                "src/sync_replica_outbox_clock_linux_internal.hpp",
                "tests/sync_replica_outbox_clock_test.cpp",
                "tools/audit_sync_replica_outbox_clock.py",
                "OWNED_OUTBOX_CLOCK_AUDIT_rev0874.md",
                "TIME_NAMESPACE_CAPABILITY_AUDIT_rev0875.md",
                "PRODUCT_CLOCK_RECOVERY_AND_DATABASE_TARGET_AUDIT_rev0897.md",
                "tools/audit_anonsync_replica_database_open_policy.py",
            )
        ),
        "release_verifier_requires_the_owned_clock_and_product_recovery_slice",
        "a sealed current archive cannot omit capability classification, runtime proof, product recovery, database targeting audit, or design records",
    )

    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
