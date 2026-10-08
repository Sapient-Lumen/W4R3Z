#pragma once

#include "sync_replica_model.hpp"
#include "sync_replica_file_content_inventory.hpp"
#include "sync_replica_outbox_clock.hpp"
#include "sync_replica_outbox_lease.hpp"
#include "sync_sqlite_support.hpp"

#include <cstdint>
#include <memory>
#include <optional>
#include <span>
#include <string>
#include <vector>

namespace anonsync {

// Durable policy for one replica folder. Model limits govern immutable
// evidence; independent outbox limits govern lightweight destination intents;
// clock limits govern only lease/retry liveness observations. Canonical
// operation bytes remain stored once regardless of destination fanout.
struct SyncReplicaSqliteOwnerLimits final {
    SyncReplicaModelLimits model;
    std::uint64_t max_outbox_intents = 1000000ULL;
    std::uint64_t max_outbox_destination_bytes = 64ULL * 1024ULL * 1024ULL;
    std::uint64_t max_outbox_clock_uncertainty_ns =
        kSyncReplicaOutboxDefaultClockMaxUncertaintyNs;
    std::uint64_t max_outbox_clock_forward_step_seconds =
        kSyncReplicaOutboxDefaultClockMaxForwardStepSeconds;
    std::uint64_t max_outbox_clock_realtime_lag_seconds =
        kSyncReplicaOutboxDefaultClockMaxRealtimeLagSeconds;

    bool operator==(const SyncReplicaSqliteOwnerLimits&) const = default;
};

struct SyncReplicaSqliteOutboxIntent final {
    std::string destination_device_id;
    std::string operation_id;
    std::uint64_t enqueued_generation = 0;
    SyncReplicaOutboxLeaseState lease;
    bool operator==(const SyncReplicaSqliteOutboxIntent&) const = default;
};

struct SyncReplicaSqliteOutboxClaim final {
    SyncReplicaSqliteOutboxIntent intent;
    SyncReplicaOperation operation;
    bool operator==(const SyncReplicaSqliteOutboxClaim&) const = default;
};

enum class SyncReplicaSqliteOutboxReceiptResult {
    Applied,
    LeaseAlreadyCovered,
    IntentMissing,
    StaleClaim,
    ExpiredClaim,
};

enum class SyncReplicaSqliteOutboxDispatchGuardDisposition {
    Acquired,
    IntentMissing,
    StaleClaim,
    ExpiredClaim,
};

// Compact transaction-bound result for remote evidence admission. The state,
// generation, and cutpoint digest are captured from the same SQLite write
// transaction that decided admission, avoiding a post-commit snapshot race in
// delivery/receipt orchestration. CapacityBlocked is the only result without a
// retained evidence state.
struct SyncReplicaSqliteRemoteAdmissionResult final {
    SyncReplicaAdmission admission = SyncReplicaAdmission::CapacityBlocked;
    std::optional<SyncReplicaEvidenceState> evidence_state;
    std::uint64_t state_generation = 0;
    std::string cutpoint_digest;

    bool operator==(const SyncReplicaSqliteRemoteAdmissionResult&) const =
        default;
};

struct SyncReplicaSqliteSnapshot final {
    SyncReplicaDurableState durable;
    SyncReplicaSqliteOwnerLimits limits;
    std::uint64_t state_generation = 0;
    std::uint64_t policy_generation = 0;
    std::vector<SyncReplicaSqliteOutboxIntent> outbox;
    // Separate liveness authority. The exact accepted/rejected host observation,
    // identity bindings, cumulative drift anchor, quarantine, and recovery
    // generations are durable without being mislabeled as canonical evidence.
    SyncReplicaOutboxClockState outbox_clock_state;
    // Convenience projection of outbox_clock_state.high_water_epoch.
    std::uint64_t outbox_time_high_water_epoch = 0;
    std::string outbox_clock_digest;
    // Binds the exact local counter->operation authority map. This mapping
    // cannot be reconstructed from the evidence set after a local same-dot fork.
    std::string local_operation_digest;
    std::string operation_set_digest;
    std::string evidence_set_digest;
    std::string visible_state_digest;
    std::string outbox_digest;
    // Unkeyed structural seal over identity, policy generations, exact resource
    // counters, and projection/outbox digests. It detects torn or casual edits;
    // it is not a substitute for an authenticated local store.
    std::string cutpoint_digest;
    bool operator==(const SyncReplicaSqliteSnapshot&) const = default;
};

// Scope-bound causal cutpoint authority for an external immutable effect. The
// guard owns one BEGIN IMMEDIATE transaction after complete-state restore, so
// no competing SQLite writer can change evidence or projection until commit.
// It does not make SQLite and the filesystem one transaction; it gives a
// coordinator an exact, restart-safe cutpoint under which to perform and attest
// an idempotent external effect. Destruction rolls the unchanged,
// writer-serializing transaction back. The inherited transaction capability
// remains process/thread-affine.
class SyncReplicaSqliteProjectionGuard final {
public:
    ~SyncReplicaSqliteProjectionGuard() = default;
    SyncReplicaSqliteProjectionGuard(
        const SyncReplicaSqliteProjectionGuard&) = delete;
    SyncReplicaSqliteProjectionGuard& operator=(
        const SyncReplicaSqliteProjectionGuard&) = delete;
    SyncReplicaSqliteProjectionGuard(
        SyncReplicaSqliteProjectionGuard&&) = delete;
    SyncReplicaSqliteProjectionGuard& operator=(
        SyncReplicaSqliteProjectionGuard&&) = delete;

    [[nodiscard]] bool active() const noexcept;
    [[nodiscard]] const SyncReplicaSqliteSnapshot& snapshot() const noexcept {
        return snapshot_;
    }
    void commit_or_throw();

private:
    SyncReplicaSqliteProjectionGuard(
        std::unique_ptr<SyncSqliteTransaction> transaction,
        SyncReplicaSqliteSnapshot snapshot,
        std::string label);

    std::unique_ptr<SyncSqliteTransaction> transaction_;
    SyncReplicaSqliteSnapshot snapshot_;
    std::string label_;

    friend class SyncReplicaSqliteOwner;
};

// Scope-bound sender claim authority for bounded request construction. The
// guard owns one BEGIN IMMEDIATE transaction after complete-state restore and
// a fresh owned-clock observation. While it is live, no competing SQLite writer
// can release, renew, settle, replace, or otherwise supersede the exact claim
// exposed by claim(). Destruction rolls back any staged clock observation.
//
// This is deliberately not a general network-I/O transaction: callers must
// finish every bounded payload lookup/copy before acquiring it and must never
// invoke caller code while it is live. It may cover bounded local request
// validation/encoding, or a separately reviewed transport
// primitive may retain it through one fixed-size first-prefix write only after
// nonblocking TLS read/write readiness is re-proved. It must never cover the
// payload body. Destruction before that cutpoint rolls back; completion freezes
// which exact claim owned the first stream progress without pretending the peer
// received, admitted, or durably effected the frame.
class SyncReplicaSqliteOutboxDispatchGuard final {
public:
    ~SyncReplicaSqliteOutboxDispatchGuard() = default;
    SyncReplicaSqliteOutboxDispatchGuard(
        const SyncReplicaSqliteOutboxDispatchGuard&) = delete;
    SyncReplicaSqliteOutboxDispatchGuard& operator=(
        const SyncReplicaSqliteOutboxDispatchGuard&) = delete;
    SyncReplicaSqliteOutboxDispatchGuard(
        SyncReplicaSqliteOutboxDispatchGuard&&) = delete;
    SyncReplicaSqliteOutboxDispatchGuard& operator=(
        SyncReplicaSqliteOutboxDispatchGuard&&) = delete;

    [[nodiscard]] bool active() const noexcept;
    [[nodiscard]] const SyncReplicaSqliteOutboxClaim& claim() const noexcept {
        return claim_;
    }
    [[nodiscard]] std::uint64_t observed_epoch() const noexcept {
        return observed_epoch_;
    }
    void commit_or_throw();

private:
    SyncReplicaSqliteOutboxDispatchGuard(
        std::unique_ptr<SyncSqliteTransaction> transaction,
        SyncReplicaSqliteOutboxClaim claim,
        std::uint64_t observed_epoch,
        std::string label);

    std::unique_ptr<SyncSqliteTransaction> transaction_;
    SyncReplicaSqliteOutboxClaim claim_;
    std::uint64_t observed_epoch_ = 0;
    std::string label_;

    friend class SyncReplicaSqliteOwner;
};

struct SyncReplicaSqliteOutboxDispatchGuardResult final {
    SyncReplicaSqliteOutboxDispatchGuardDisposition disposition =
        SyncReplicaSqliteOutboxDispatchGuardDisposition::IntentMissing;
    std::unique_ptr<SyncReplicaSqliteOutboxDispatchGuard> guard;
};

// SQLite-backed correctness slice for one folder and local actor epoch.
//
// The database is the owner: every public operation opens one typed transaction,
// restores canonical evidence and every redundant projection, applies the pure
// model, then independently reloads the complete staged cutpoint before COMMIT.
// Lease/retry time comes only from the injected owned clock source. Authoritative
// samples are taken after BEGIN IMMEDIATE and complete restore, establishing a
// real serialization point rather than allowing a pre-lock sample to age while
// SQLite waits for the writer slot. All durable SQL names are bound to main and
// exact sqlite_schema text is protocol state.
//
// This is intentionally an O(history) reference owner and assurance scaffold,
// not a production scaling claim. A later incremental production projector must
// preserve these authority and re-attestation boundaries.
class SyncReplicaSqliteOwner final {
public:
    SyncReplicaSqliteOwner(
        SyncSqliteDbHandleSlot& db,
        std::string folder_id,
        SyncReplicaActor local_actor,
        SyncReplicaSqliteOwnerLimits initial_limits = {},
        std::string label = "sync replica SQLite owner",
        std::unique_ptr<SyncReplicaOutboxClockSource> clock_source = {});

    SyncReplicaSqliteOwner(const SyncReplicaSqliteOwner&) = delete;
    SyncReplicaSqliteOwner& operator=(const SyncReplicaSqliteOwner&) = delete;
    SyncReplicaSqliteOwner(SyncReplicaSqliteOwner&&) = delete;
    SyncReplicaSqliteOwner& operator=(SyncReplicaSqliteOwner&&) = delete;

    [[nodiscard]] SyncReplicaSqliteSnapshot snapshot_or_throw();
    [[nodiscard]] SyncReplicaOperation create_local_file_or_throw(
        std::string canonical_path,
        std::uint64_t size_bytes,
        std::string content_sha256,
        std::span<const std::string> destination_device_ids = {});
    [[nodiscard]] SyncReplicaOperation create_local_tombstone_or_throw(
        std::string canonical_path,
        std::span<const std::string> destination_device_ids = {});
    // Duplicate and CapacityBlocked are durable no-ops. The persisted
    // retention policy, not caller defaults, remains authoritative after restart.
    [[nodiscard]] SyncReplicaAdmission accept_remote_or_throw(
        const SyncReplicaOperation& operation);

    // Same admission authority, with a compact exact cutpoint captured inside
    // the deciding transaction. This is the composition surface for protocols
    // that must emit a receipt without racing a second owner snapshot.
    [[nodiscard]] SyncReplicaSqliteRemoteAdmissionResult
    accept_remote_with_cutpoint_or_throw(
        const SyncReplicaOperation& operation);

    // Acquires an unchanged projection guard backed by BEGIN IMMEDIATE only when
    // complete current cutpoint exactly matches the transaction-bound evidence
    // receipt and the named File operation is the sole visible active primary.
    // A null result means the cutpoint advanced or projection is not currently
    // unambiguous; no durable row is changed. While a non-null guard is live, a
    // coordinator may perform one bounded idempotent filesystem effect without
    // a competing causal writer invalidating the authorizing projection.
    [[nodiscard]] std::unique_ptr<SyncReplicaSqliteProjectionGuard>
    guard_unambiguous_file_primary_at_cutpoint_or_throw(
        const SyncReplicaOperation& operation,
        std::uint64_t expected_state_generation,
        const std::string& expected_cutpoint_digest);

    // Claims the first ready intent in canonical order, optionally for one
    // destination. Entropy is acquired before the writer lock; host time is
    // sampled only after writer authority and full restore. Each attempt receives
    // a fresh cutpoint- and CSPRNG-bound claim ID.
    [[nodiscard]] std::optional<SyncReplicaSqliteOutboxClaim>
    claim_next_outbox_or_throw(
        std::string worker_id,
        std::uint64_t lease_seconds,
        std::optional<std::string> destination_device_id = std::nullopt,
        std::optional<SyncReplicaValueKind> operation_kind = std::nullopt);

    // Same claim transition, but first proves that the selected canonical
    // operation is encodable under the caller's complete delivery wire model.
    // A file-only caller may also preflight the operation's committed payload
    // size and provide a canonical immutable inventory of content identities it
    // can supply. Operations absent from an engaged inventory are not claim
    // candidates and consume no attempt authority. An incompatible first-ready
    // matching operation throws before lease mutation, so local configuration
    // cannot create a durable, repeatedly unsendable claim/expiry loop.
    [[nodiscard]] std::optional<SyncReplicaSqliteOutboxClaim>
    claim_next_outbox_for_delivery_or_throw(
        std::string worker_id,
        std::uint64_t lease_seconds,
        const SyncReplicaModelLimits& delivery_operation_limits,
        std::optional<std::string> destination_device_id = std::nullopt,
        std::optional<SyncReplicaValueKind> operation_kind = std::nullopt,
        std::optional<std::uint64_t> max_file_payload_bytes = std::nullopt,
        std::optional<SyncReplicaFileContentInventory>
            available_file_content = std::nullopt);

    // Re-attests one previously minted claim after bounded immutable payload
    // lookup/copy. Missing and stale identities do not sample or ratchet time.
    // A matching expired claim commits the accepted clock observation that
    // proves revocation. Acquired returns a writer-serializing guard carrying
    // the current exact row (including a valid intervening renewal) and retained
    // canonical operation. No unbounded frame body may be exposed before guard
    // commit; only a separately reviewed fixed-size prefix primitive may cross
    // that frontier while this writer capability remains live.
    [[nodiscard]] SyncReplicaSqliteOutboxDispatchGuardResult
    guard_outbox_claim_for_dispatch_or_throw(
        const SyncReplicaSqliteOutboxClaim& expected_claim);

    // Retires one exact unsettled intent only while claim_id names its current
    // unexpired attempt. Missing/stale identities do not sample or ratchet time;
    // a matching expired receipt durably publishes revocation before returning.
    [[nodiscard]] SyncReplicaSqliteOutboxReceiptResult settle_outbox_or_throw(
        const std::string& destination_device_id,
        const std::string& operation_id,
        const std::string& claim_id);

    // Extends one exact live attempt. It cannot change receipt identity, revive
    // expiry, shorten a deadline, or exceed the cumulative lifetime budget.
    // LeaseAlreadyCovered may publish only a newer owned clock observation.
    [[nodiscard]] SyncReplicaSqliteOutboxReceiptResult renew_outbox_lease_or_throw(
        const std::string& destination_device_id,
        const std::string& operation_id,
        const std::string& claim_id,
        std::uint64_t lease_seconds);

    // Releases one exact live attempt and derives a bounded absolute retry
    // deadline from the same owned observation that authorized the transition.
    [[nodiscard]] SyncReplicaSqliteOutboxReceiptResult
    release_outbox_for_retry_or_throw(
        const std::string& destination_device_id,
        const std::string& operation_id,
        const std::string& claim_id,
        std::uint64_t retry_delay_seconds);

    // Samples and publishes only the owned clock cutpoint. This spends no
    // dispatch authority and returns quarantine as exact state instead of
    // translating it into an exception, making it suitable for an explicit
    // supervisor/operator health probe.
    [[nodiscard]] SyncReplicaOutboxClockObservationResult
    observe_outbox_clock_or_throw();

    // Quarantine is sticky. Recovery is explicit, generation-fenced, and binds
    // the current source/boot/thread-time-namespace observation as a fresh drift
    // anchor without moving below the durable high-water epoch.
    [[nodiscard]] SyncReplicaOutboxClockState recover_outbox_clock_or_throw(
        std::uint64_t expected_observation_generation);

    // Policy replacement succeeds only when all retained evidence, outbox state,
    // and accepted clock evidence fit the replacement limits atomically.
    void replace_limits_or_throw(
        const SyncReplicaSqliteOwnerLimits& replacement);

private:
    [[nodiscard]] std::optional<SyncReplicaSqliteOutboxClaim>
    claim_next_outbox_impl_or_throw(
        std::string worker_id,
        std::uint64_t lease_seconds,
        std::optional<std::string> destination_device_id,
        std::optional<SyncReplicaValueKind> operation_kind,
        const SyncReplicaModelLimits* delivery_operation_limits,
        std::optional<std::uint64_t> max_file_payload_bytes,
        std::optional<SyncReplicaFileContentInventory>
            available_file_content);

    SyncSqliteDbHandleSlot& db_;
    std::string folder_id_;
    SyncReplicaActor local_actor_;
    std::string label_;
    std::unique_ptr<SyncReplicaOutboxClockSource> clock_source_;
};

}  // namespace anonsync
