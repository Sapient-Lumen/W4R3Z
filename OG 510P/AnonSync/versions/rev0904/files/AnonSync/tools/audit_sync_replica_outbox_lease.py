#!/usr/bin/env python3
"""Fail-closed structural audit for receipt-bound outbox lease authority."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED = (
    Path("CMakeLists.txt"),
    Path("src/sync_replica_outbox_lease.hpp"),
    Path("src/sync_replica_outbox_lease.cpp"),
    Path("tests/sync_replica_outbox_lease_test.cpp"),
    Path("src/sync_replica_sqlite_owner.cpp"),
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
        "format": "anonsync-sync-replica-outbox-lease-audit-v5",
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
    header = text["src/sync_replica_outbox_lease.hpp"]
    source = text["src/sync_replica_outbox_lease.cpp"]
    runtime = text["tests/sync_replica_outbox_lease_test.cpp"]
    owner = text["src/sync_replica_sqlite_owner.cpp"]
    verifier = text["tools/verify_release_package.py"]

    require(
        all(
            token in header
            for token in (
                "dispatch_attempts",
                "claim_id",
                "worker_id",
                "claimed_at_epoch",
                "lease_expires_at_epoch",
                "retry_not_before_epoch",
                "retry_released_at_epoch",
                "retry_release_provenance",
                "Exact = 1U",
                "LegacyUnproven = 2U",
            )
        ),
        "lease_state_names_every_durable_authority_field",
        "attempt identity, owner, lifetime, and retry provenance are explicit restart state",
    )
    require(
        "Expiry also revokes settlement" in header
        and "Time can revoke authority but can never grant it" in header
        and "exact current claim ID is always required before the deadline" in header,
        "contract_makes_expiry_a_one_way_authority_boundary",
        "settlement, renewal, and retry release all require the exact live receipt",
    )
    require(
        "RAND_bytes" not in source
        and "random_device" not in source
        and "Entropy must contain exactly 32 CSPRNG bytes" in header,
        "pure_policy_injects_entropy",
        "deterministic policy code does not hide operating-system randomness",
    )

    validate = function_body(
        source, "void validate_sync_replica_outbox_lease_state_or_throw("
    )
    require(
        all(
            token in validate
            for token in (
                "has_claim != has_worker",
                "has_claim != has_claimed_at",
                "has_claim != has_deadline",
                "partial lease authority",
                "state.lease_expires_at_epoch <= state.claimed_at_epoch",
                "kSyncReplicaOutboxMaxClaimLifetimeSeconds",
                "cumulative claim lifetime budget",
            )
        ),
        "active_claim_is_all_or_none_positive_and_lifetime_bounded",
        "restart rejects partial, zero-duration, and indefinitely renewable authority",
    )
    require(
        all(
            token in validate
            for token in (
                "backs off an intent that has never been dispatched",
                "retry authority without release provenance",
                "fabricates an exact legacy retry release epoch",
                "invalid exact retry release provenance",
                "exact retry delay exceeds the fixed retry budget",
                "unsupported retry release provenance",
            )
        ),
        "retry_state_requires_reachable_bounded_provenance",
        "current rows prove the release observation while migration gaps stay explicitly unproven",
    )
    require(
        "has dispatched history without active or retry authority" in validate,
        "dispatch_history_cannot_float_without_current_or_retry_authority",
        "an unreachable persisted attempt is rejected instead of becoming immediately claimable",
    )

    claimable = function_body(
        source, "bool sync_replica_outbox_lease_is_claimable_at_or_throw("
    )
    require(
        ordered(
            claimable,
            "validate_sync_replica_outbox_lease_state_or_throw",
            "now_epoch == 0U",
            "state.retry_not_before_epoch > now_epoch",
            "state.claim_id.empty() || state.lease_expires_at_epoch <= now_epoch",
        ),
        "claimability_has_exact_retry_and_expiry_boundaries",
        "ready-at and expiry-at instants are inclusive while epoch zero is invalid",
    )

    claim = function_body(source, "claim_sync_replica_outbox_lease_or_throw(")
    require(
        all(
            token in claim
            for token in (
                "sync_id_is_valid(folder_id)",
                "sync_id_is_valid(destination_device_id)",
                "is_lowercase_sha256_hex(operation_id)",
                "enqueued_generation == 0U",
                "is_lowercase_sha256_hex(current_cutpoint_digest)",
                "sync_id_is_valid(worker_id)",
                "entropy.size() != kClaimEntropyBytes",
                "numeric_limits<std::uint64_t>::max()",
            )
        ),
        "claim_validates_identity_entropy_and_counter_before_mint",
        "malformed scope, short entropy, or exhausted attempt counters fail closed",
    )
    require(
        ordered(
            claim,
            "sync_replica_outbox_lease_is_claimable_at_or_throw",
            "next.dispatch_attempts = current.dispatch_attempts + 1U",
            "next.worker_id = std::move(worker_id)",
            "next.claimed_at_epoch = now_epoch",
            "lease_deadline_or_throw",
            "anonsync-sync-replica-outbox-claim-v2",
            "next.claim_id = digest.finish_hex()",
            "validate_sync_replica_outbox_lease_state_or_throw(next",
        ),
        "claim_transition_is_deterministic_validated_and_digest_bound",
        "the receipt is scoped to one exact intent, prior state, worker, deadline, and entropy input",
    )
    require(
        all(
            token in claim
            for token in (
                "folder_id",
                "destination_device_id",
                "operation_id",
                "enqueued_generation",
                "current_cutpoint_digest",
                "current.dispatch_attempts",
                "current.retry_not_before_epoch",
                "current.retry_released_at_epoch",
                "current.retry_release_provenance",
                "next.worker_id",
                "next.claimed_at_epoch",
                "next.lease_expires_at_epoch",
                "entropy",
            )
        ),
        "claim_digest_covers_scope_prior_authority_schedule_and_entropy",
        "a receipt cannot be replayed across destination, cutpoint, attempt, or schedule",
    )

    status = function_body(
        source, "sync_replica_outbox_claim_status_at_or_throw("
    )
    require(
        ordered(
            status,
            "validate_sync_replica_outbox_lease_state_or_throw",
            "state.claim_id.empty() || state.claim_id != expected_claim_id",
            "SyncReplicaOutboxClaimStatus::Stale",
            "now_epoch < state.claimed_at_epoch",
            "now_epoch >= state.lease_expires_at_epoch",
            "SyncReplicaOutboxClaimStatus::Expired",
            "SyncReplicaOutboxClaimStatus::Current",
        ),
        "receipt_status_is_stale_first_and_deadline_exclusive",
        "a different receipt is stale; the matching receipt expires exactly at its deadline",
    )

    renew = function_body(source, "renew_sync_replica_outbox_lease_or_throw(")
    require(
        ordered(
            renew,
            "sync_replica_outbox_claim_status_at_or_throw",
            "expected claim is stale",
            "expected claim is expired",
            "lease_deadline_or_throw",
            "proposed_deadline <= current.lease_expires_at_epoch",
            "kSyncReplicaOutboxMaxClaimLifetimeSeconds",
            "next.lease_expires_at_epoch = proposed_deadline",
        ),
        "renewal_is_live_receipt_fenced_nonshortening_and_cumulative_bounded",
        "heartbeats cannot revive expiry, rotate identity, or extend one attempt indefinitely",
    )
    release = function_body(source, "release_sync_replica_outbox_lease_or_throw(")
    require(
        ordered(
            release,
            "sync_replica_outbox_claim_status_at_or_throw",
            "expected claim is stale",
            "expected claim is expired",
            "retry_delay_seconds > kSyncReplicaOutboxMaxRetryDelaySeconds",
            "numeric_limits<std::uint64_t>::max() - now_epoch",
            "next.retry_not_before_epoch = now_epoch + retry_delay_seconds",
            "next.retry_released_at_epoch = now_epoch",
            "SyncReplicaOutboxRetryReleaseProvenance::Exact",
        ),
        "release_is_live_receipt_fenced_bounded_and_exactly_provenanced",
        "a stale or expired sender cannot install delay over current work",
    )

    require(
        all(
            token in runtime
            for token in (
                "claim did not expire at its exact deadline",
                "expired receipt renewed its former attempt",
                "expired receipt installed retry policy",
                "heartbeat exceeded the cumulative claim lifetime budget",
                "retry release accepted an unbounded liveness delay",
                "old claim released a replacement attempt",
                "retry-not-before boundary was not exact",
                "pure claim token construction is not deterministic",
                "claim token did not bind CSPRNG entropy",
                "dispatch counter overflow was not rejected",
                "short claim entropy was accepted",
                "lease deadline overflow was accepted",
                "dispatched history was accepted without a claim or retry fence",
                "legacy migration marker accepted a guessed release epoch",
            )
        ),
        "runtime_pins_expiry_renewal_release_provenance_and_overflow",
        "adversarial tests cover the complete pure receipt state machine",
    )

    owner_claim_wrapper = function_body(
        owner, "SyncReplicaSqliteOwner::claim_next_outbox_or_throw("
    )
    owner_delivery_claim_wrapper = function_body(
        owner, "SyncReplicaSqliteOwner::claim_next_outbox_for_delivery_or_throw("
    )
    owner_claim = function_body(
        owner, "SyncReplicaSqliteOwner::claim_next_outbox_impl_or_throw("
    )
    require(
        "RAND_bytes" in owner
        and "claim_next_outbox_impl_or_throw" in owner_claim_wrapper
        and "claim_next_outbox_impl_or_throw" in owner_delivery_claim_wrapper
        and ordered(
            owner_claim,
            "random_claim_entropy_or_throw",
            "SyncSqliteTransaction transaction",
            "SyncSqliteTransactionMode::Immediate",
            "claim_sync_replica_outbox_lease_or_throw",
        ),
        "owner_acquires_checked_csprng_entropy_before_writer_authority",
        "both public claim surfaces share one core where randomness stays outside SQLite's writer slot",
    )
    require(
        all(
            token in owner
            for token in (
                "SyncReplicaSqliteOwner::renew_outbox_lease_or_throw",
                "SyncReplicaSqliteOutboxReceiptResult::LeaseAlreadyCovered",
                "SyncReplicaSqliteOutboxReceiptResult::ExpiredClaim",
                "publish_outbox_lease_update_or_throw",
            )
        ),
        "owner_integrates_fenced_heartbeat_and_shared_publication",
        "claim, renewal, and release converge on one exact re-attested lease update path",
    )
    require(
        all(
            token in cmake
            for token in (
                "anonsync_sync_replica_outbox_lease",
                "src/sync_replica_outbox_lease.cpp",
                "anonsync_sync_replica_outbox_lease_test",
                "tests/sync_replica_outbox_lease_test.cpp",
                "audit_sync_replica_outbox_lease.py",
            )
        ),
        "lease_library_runtime_and_audit_are_registered",
        "the pure authority layer participates in normal, sanitizer, and source-audit lanes",
    )
    require(
        "revision_number >= 874" in verifier
        and all(
            token in verifier
            for token in (
                "src/sync_replica_outbox_lease.hpp",
                "src/sync_replica_outbox_lease.cpp",
                "tests/sync_replica_outbox_lease_test.cpp",
                "tools/audit_sync_replica_outbox_lease.py",
                "OWNED_OUTBOX_CLOCK_AUDIT_rev0874.md",
            )
        ),
        "release_verifier_requires_receipt_policy_and_rev0874_design_record",
        "a sealed archive cannot omit the lease state machine, runtime, structural audit, or authority analysis",
    )

    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
