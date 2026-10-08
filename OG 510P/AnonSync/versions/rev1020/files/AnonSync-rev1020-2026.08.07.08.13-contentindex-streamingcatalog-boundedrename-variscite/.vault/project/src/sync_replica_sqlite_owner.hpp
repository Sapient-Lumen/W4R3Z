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

struct SyncReplicaSqliteDeploymentBinding;

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

// Result of explicitly deriving courier work from already-published share
// evidence. Publication is share-global; destination intents are disposable
// delivery scheduling state. Repeating the same derivation while an exact
// intent is still present is a durable no-op rather than a uniqueness error.
struct SyncReplicaSqliteOutboxEnqueueResult final {
    std::uint64_t added_intent_count = 0;
    std::uint64_t already_present_intent_count = 0;
    std::uint64_t state_generation = 0;

    bool operator==(const SyncReplicaSqliteOutboxEnqueueResult&) const =
        default;
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

// Restart-safe boundary between local byte observation and durable evidence
// publication. prepare() derives the exact next canonical operation from one
// pinned replica cutpoint without mutating SQLite. A catalog may durably retain
// this value before commit(), then repeat the exact commit after a crash. The
// publication fence binds the exact path-head set, local minting authority,
// and durable policy. Remote evidence on another path, outbox leases, retries,
// clock samples, and destination reconciliation cannot starve local folder
// publication because they do not determine the canonical operation being
// minted.
struct SyncReplicaSqlitePreparedLocalFilePublication final {
    SyncReplicaOperation operation;
    std::vector<std::string> observed_visible_operation_ids;
    // Diagnostic generation observed by prepare(); commit authority comes from
    // expected_publication_cutpoint_digest, not unrelated outbox liveness.
    std::uint64_t observed_state_generation = 0;
    std::string expected_publication_cutpoint_digest;

    bool operator==(
        const SyncReplicaSqlitePreparedLocalFilePublication&) const = default;
};

enum class SyncReplicaSqlitePreparedPublicationDisposition {
    Published,
    AlreadyPublished,
    StaleCutpoint,
};

struct SyncReplicaSqlitePreparedPublicationResult final {
    SyncReplicaSqlitePreparedPublicationDisposition disposition =
        SyncReplicaSqlitePreparedPublicationDisposition::StaleCutpoint;
    std::uint64_t state_generation = 0;
    std::string cutpoint_digest;

    bool operator==(const SyncReplicaSqlitePreparedPublicationResult&) const =
        default;
};

// Atomic, wire-compatible local rename publication. The destination File and
// source Tombstone are minted consecutively inside one replica SQLite write
// transaction and advance the durable state generation once. The compact
// inferred identity is returned alongside the two newly minted operations so a
// folder catalog can bind both path effects without reconstructing history.
struct SyncReplicaSqliteLocalRenamePublicationResult final {
    SyncReplicaIdentityPreservingRename identity;
    SyncReplicaOperation destination_file_operation;
    SyncReplicaOperation source_tombstone_operation;
    std::uint64_t state_generation = 0U;
    std::string cutpoint_digest;

    bool operator==(
        const SyncReplicaSqliteLocalRenamePublicationResult&) const = default;
};

// Bounded share-global evidence page for peer reconciliation. This is not an
// outbox view: every retained operation is eligible regardless of which peers
// were known when it was published. Lexicographic operation-ID order is only a
// stable serialization cursor. It does not choose causal readiness, retry
// priority, or a conflict winner.
struct SyncReplicaSqliteEvidencePageLimits final {
    std::uint64_t max_operations = 256U;
    std::uint64_t max_canonical_bytes = 16ULL * 1024ULL * 1024ULL;

    bool operator==(const SyncReplicaSqliteEvidencePageLimits&) const = default;
};

void validate_sync_replica_sqlite_evidence_page_limits_or_throw(
    const SyncReplicaSqliteEvidencePageLimits& limits);

enum class SyncReplicaSqliteEvidencePageDisposition : std::uint8_t {
    Page = 1U,
    SourceChanged = 2U,
};

struct SyncReplicaSqliteEvidencePage final {
    SyncReplicaSqliteEvidencePageDisposition disposition =
        SyncReplicaSqliteEvidencePageDisposition::Page;
    std::uint64_t source_state_generation = 0U;
    std::uint64_t source_evidence_count = 0U;
    std::string source_evidence_set_digest;
    std::vector<SyncReplicaOperation> operations;
    std::uint64_t canonical_bytes = 0U;
    bool has_more = false;
    // Empty on the first empty page. Otherwise this is the exact last operation
    // ID returned, or the request cursor when no later operation exists.
    std::string next_after_operation_id;

    bool operator==(const SyncReplicaSqliteEvidencePage&) const = default;
};

// Bounded current-visible primary-file page used only as an acceleration
// candidate source. The page walks the durable visible-path projection in
// canonical path order and never reconstructs retained history. Tombstone
// primaries consume the path and byte frontier but are omitted from
// file_operations, so a long deletion prefix cannot starve continuation.
inline constexpr std::uint64_t
    kSyncReplicaSqliteVisibleFileCandidateMaximumPaths = 64U;
inline constexpr std::uint64_t
    kSyncReplicaSqliteVisibleFileCandidateMaximumCanonicalBytes =
        4ULL * 1024ULL * 1024ULL;

struct SyncReplicaSqliteVisibleFileCandidatePageLimits final {
    std::uint64_t max_visible_paths =
        kSyncReplicaSqliteVisibleFileCandidateMaximumPaths;
    std::uint64_t max_canonical_bytes =
        kSyncReplicaSqliteVisibleFileCandidateMaximumCanonicalBytes;

    bool operator==(
        const SyncReplicaSqliteVisibleFileCandidatePageLimits&) const = default;
};

void validate_sync_replica_sqlite_visible_file_candidate_page_limits_or_throw(
    const SyncReplicaSqliteVisibleFileCandidatePageLimits& limits);

enum class SyncReplicaSqliteVisibleFileCandidatePageDisposition : std::uint8_t {
    Page = 1U,
    SourceChanged = 2U,
};

struct SyncReplicaSqliteVisibleFileCandidatePage final {
    SyncReplicaSqliteVisibleFileCandidatePageDisposition disposition =
        SyncReplicaSqliteVisibleFileCandidatePageDisposition::Page;
    std::uint64_t source_state_generation = 0U;
    std::uint64_t source_visible_path_count = 0U;
    std::string source_visible_state_digest;
    std::vector<SyncReplicaOperation> file_operations;
    std::uint64_t scanned_visible_paths = 0U;
    std::uint64_t canonical_bytes = 0U;
    bool has_more = false;
    // Empty on the first empty page. Otherwise this is the exact last visible
    // canonical path consumed, or the request cursor when no later path exists.
    std::string next_after_canonical_path;

    bool operator==(
        const SyncReplicaSqliteVisibleFileCandidatePage&) const = default;
};

// One local storage-policy root over immutable retained share evidence. A pin
// names an exact File operation, not a path or mutable payload pathname. It is
// durable local authority for future retention decisions, but it does not by
// itself authorize deletion, restoration, network propagation, or garbage
// collection. Repeating an exact transition is a durable no-op.
enum class SyncReplicaSqliteHistoricalVersionPinDisposition : std::uint8_t {
    Pinned = 1U,
    AlreadyPinned = 2U,
    Unpinned = 3U,
    AlreadyUnpinned = 4U,
};

[[nodiscard]] constexpr std::string_view
sync_replica_sqlite_historical_version_pin_disposition_name(
    SyncReplicaSqliteHistoricalVersionPinDisposition disposition) noexcept {
    switch (disposition) {
        case SyncReplicaSqliteHistoricalVersionPinDisposition::Pinned:
            return "pinned";
        case SyncReplicaSqliteHistoricalVersionPinDisposition::AlreadyPinned:
            return "already_pinned";
        case SyncReplicaSqliteHistoricalVersionPinDisposition::Unpinned:
            return "unpinned";
        case SyncReplicaSqliteHistoricalVersionPinDisposition::
                AlreadyUnpinned:
            return "already_unpinned";
    }
    return "unknown";
}

struct SyncReplicaSqliteHistoricalVersionPinResult final {
    SyncReplicaSqliteHistoricalVersionPinDisposition disposition =
        SyncReplicaSqliteHistoricalVersionPinDisposition::AlreadyUnpinned;
    std::string operation_id;
    std::uint64_t state_generation = 0U;
    std::uint64_t pin_count = 0U;
    std::string pin_set_digest;

    bool operator==(
        const SyncReplicaSqliteHistoricalVersionPinResult&) const = default;
};

struct SyncReplicaSqliteSnapshot final {
    SyncReplicaDurableState durable;
    SyncReplicaSqliteOwnerLimits limits;
    // Randomly minted once for a new database or exact pre-v7 migration.
    // Distinguishes independent SQLite files that otherwise contain identical
    // causal state. Because it is stored in the database, it is not by itself
    // an external exact-image rollback detector.
    std::string database_incarnation_sha256;
    // Monotonic within the retained database image. An explicit recovery
    // transition advances this value and the state generation together so
    // stale same-incarnation retention evidence cannot cross that boundary.
    std::uint64_t database_recovery_epoch = 0U;
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
    std::uint64_t visible_path_count = 0U;
    std::string visible_state_digest;
    std::string outbox_digest;
    // Canonical operation-ID order. Every ID names one retained immutable File
    // operation. The count/digest are redundant exact authority checked during
    // every restore and bound into the owner cutpoint.
    std::vector<std::string> historical_version_pins;
    std::uint64_t historical_version_pin_count = 0U;
    std::string historical_version_pin_set_digest;
    // Unkeyed structural seal over identity, policy generations, exact resource
    // counters, and projection/outbox digests. It detects torn or casual edits;
    // it is not a substitute for an authenticated local store.
    std::string cutpoint_digest;
    bool operator==(const SyncReplicaSqliteSnapshot&) const = default;
};

// One fixed-size, transactionally pinned observation of the durable owner
// identity and configured resource limits. This is the bounded counterpart to
// snapshot_or_throw() for per-turn reconciliation checks that must detect a
// replaced database or changed owner without reconstructing retained history.
// It deliberately does not claim a fresh proof of aggregate operation,
// evidence, visible, outbox, clock, or retention-pin contents.
struct SyncReplicaSqliteIdentityCutpoint final {
    std::string folder_id;
    SyncReplicaActor local_actor;
    SyncReplicaSqliteOwnerLimits limits;
    std::string database_incarnation_sha256;
    std::uint64_t database_recovery_epoch = 0U;

    bool operator==(const SyncReplicaSqliteIdentityCutpoint&) const = default;
};

// One transactionally pinned, path-local replica observation. This is the
// bounded counterpart to snapshot_or_throw() for a coordinator that needs to
// re-prove one exact sole-visible value and, optionally, one retained evidence
// operation while filesystem work is in progress. It deliberately does not
// claim a fresh proof of unrelated operations, aggregate digests, outbox rows,
// or the complete visible projection; ordinary full snapshots remain the
// authority for those global facts.
struct SyncReplicaSqliteTargetedPathCutpoint final {
    std::optional<SyncReplicaOperation> sole_visible_operation;
    // True means at least two visible rows were observed. The bounded reader
    // materializes only the first two exact active operations so a caller may
    // adopt an already-visible displayed candidate without restoring retained
    // history. It never treats that bounded prefix as a complete conflict set.
    bool conflicted = false;
    std::vector<SyncReplicaOperation> bounded_conflict_visible_operations;
    // When the requested retained identity is already owned by the sole or
    // bounded-conflict view, these selectors avoid another exact row read and
    // another potentially large operation-envelope copy. Otherwise the
    // separately requested retained row, if present, is owned below.
    bool requested_retained_operation_is_sole_visible = false;
    std::optional<std::size_t>
        requested_retained_operation_bounded_conflict_index;
    std::optional<SyncReplicaOperation> distinct_retained_operation;

    [[nodiscard]] const SyncReplicaOperation*
    requested_retained_operation_or_none() const noexcept {
        if (requested_retained_operation_is_sole_visible) {
            return sole_visible_operation.has_value()
                ? &*sole_visible_operation
                : nullptr;
        }
        if (requested_retained_operation_bounded_conflict_index.has_value()) {
            const std::size_t index =
                *requested_retained_operation_bounded_conflict_index;
            return index < bounded_conflict_visible_operations.size()
                ? &bounded_conflict_visible_operations[index]
                : nullptr;
        }
        return distinct_retained_operation.has_value()
            ? &*distinct_retained_operation
            : nullptr;
    }

    bool operator==(
        const SyncReplicaSqliteTargetedPathCutpoint&) const = default;
};

// One transactionally pinned content lookup over the startup-attested visible
// value projection. The query returns at most two exact active file operations:
// a sole match is owned below, while `ambiguous` means two or more current
// visible files carry the same immutable payload identity. This is bounded
// acceleration, not complete replica authority; snapshot_or_throw() remains the
// cold verifier for the whole projection.
struct SyncReplicaSqliteVisibleFileContentCutpoint final {
    std::optional<SyncReplicaOperation> sole_visible_file_operation;
    bool ambiguous = false;

    bool operator==(
        const SyncReplicaSqliteVisibleFileContentCutpoint&) const = default;
};

struct SyncReplicaSqliteDatabaseRecoveryEpochResult final {
    std::string database_incarnation_sha256;
    std::uint64_t previous_database_recovery_epoch = 0U;
    std::uint64_t database_recovery_epoch = 0U;
    std::uint64_t state_generation = 0U;
    std::string cutpoint_digest;

    bool operator==(
        const SyncReplicaSqliteDatabaseRecoveryEpochResult&) const = default;
};

// Exact-current-schema observation for a connection already constrained to
// read-only/query-only authority. Unlike SyncReplicaSqliteOwner construction,
// this surface never initializes or migrates schema and never acquires a
// writer transaction. It exists for side-effect-free forensic inspection.
[[nodiscard]] SyncReplicaSqliteSnapshot
inspect_sync_replica_sqlite_snapshot_read_only_or_throw(
    SyncSqliteDbHandleSlot& db,
    std::string folder_id,
    SyncReplicaActor local_actor,
    std::string label = "sync replica read-only SQLite inspection");

// Exact-current-schema observation for one sealed, filename-free,
// behaviorally read-only deserialized image. SQLite intentionally reports an
// in-memory SQLITE_DESERIALIZE_READONLY database as writable through
// sqlite3_db_readonly(); this composition instead proves write denial, the
// exact deployment binding, and the complete replica snapshot inside one
// deferred transaction. Named forensic database inspection must continue to
// use inspect_sync_replica_sqlite_snapshot_read_only_or_throw() above.
[[nodiscard]] SyncReplicaSqliteSnapshot
inspect_sync_replica_sqlite_snapshot_in_attested_detached_read_only_image_or_throw(
    SyncSqliteDbHandleSlot& db,
    const SyncReplicaSqliteDeploymentBinding& binding,
    std::string folder_id,
    SyncReplicaActor local_actor,
    std::string label =
        "sync replica detached read-only SQLite inspection");

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

    // Re-attests the exact trigger-free schema, foreign-key mode, typed metadata
    // row, durable folder/local actor, database incarnation/recovery epoch, and
    // configured limits without decoding any retained operation or projection
    // row. Constructor-time complete reconstruction remains the cold authority;
    // this cutpoint is for bounded per-turn identity and compatibility reproof.
    [[nodiscard]] SyncReplicaSqliteIdentityCutpoint
    identity_cutpoint_or_throw();

    // Reads the current metadata row, at most two visible rows for one exact
    // canonical path, and zero or one separately requested retained operation
    // inside one deferred SQLite snapshot. A sole visible operation is returned
    // only after its canonical bytes, identity, redundant charges, active
    // evidence state, path, primary flag, and preservation flag all agree. Two
    // or more visible rows conservatively produce no sole value without
    // materializing the complete conflict set.
    [[nodiscard]] SyncReplicaSqliteTargetedPathCutpoint
    targeted_path_cutpoint_or_throw(
        std::string canonical_path,
        std::optional<std::string> retained_operation_id = std::nullopt);

    // Reads at most two exact current visible file rows for one immutable
    // (size,digest) identity through the normalized schema-v9 projection. Every
    // returned row is cross-checked against its canonical operation bytes and
    // active evidence state inside the same deferred SQLite snapshot.
    [[nodiscard]] SyncReplicaSqliteVisibleFileContentCutpoint
    visible_file_content_cutpoint_or_throw(
        std::uint64_t size_bytes,
        std::string content_sha256);

    // Explicitly invalidates stale same-incarnation evidence after an operator
    // has restored, repaired, or otherwise re-authorized this exact database.
    // The transition is generation- and cutpoint-fenced, preserves all causal,
    // outbox, clock, and pin state, and advances the recovery epoch plus the
    // ordinary state generation atomically. It cannot independently discover
    // restoration of an older exact whole-database image; an external anchor or
    // a post-restore call using freshly trusted expectations is still required.
    [[nodiscard]] SyncReplicaSqliteDatabaseRecoveryEpochResult
    advance_database_recovery_epoch_or_throw(
        std::string expected_database_incarnation_sha256,
        std::uint64_t expected_database_recovery_epoch,
        std::string expected_cutpoint_digest);

    // Returns one exact page from the retained share-global evidence set. A
    // non-empty cursor must be paired with the evidence-set digest obtained from
    // the preceding page. The digest may also be supplied with an empty cursor
    // to pin and re-read the first page, including continuation of a payload for
    // the first operation. If the source evidence changed, SourceChanged is
    // returned with the new digest and no records; callers restart at the empty
    // cursor. The cursor must name an exact retained operation in that digest,
    // preventing an accidental fabricated cursor from skipping a prefix.
    [[nodiscard]] SyncReplicaSqliteEvidencePage evidence_page_or_throw(
        std::optional<std::string> after_operation_id = std::nullopt,
        std::optional<std::string> expected_source_evidence_set_digest =
            std::nullopt,
        SyncReplicaSqliteEvidencePageLimits limits = {});


    // Returns one bounded page of exact current-visible primary File values in
    // canonical path order. A continuation cursor must be paired with the
    // visible-state digest from the preceding page and must still name an exact
    // visible path in that digest. SourceChanged is returned before operation
    // rows are decoded. This is acceleration evidence only: it grants no
    // publication, payload-presence, retention, or conflict-resolution
    // authority.
    [[nodiscard]] SyncReplicaSqliteVisibleFileCandidatePage
    visible_file_candidate_page_or_throw(
        std::optional<std::string> after_canonical_path = std::nullopt,
        std::optional<std::string> expected_source_visible_state_digest =
            std::nullopt,
        SyncReplicaSqliteVisibleFileCandidatePageLimits limits = {});

    // Adds or removes one explicit local retention root. Pinning requires an
    // exact retained File operation. Unpinning an absent canonical ID is
    // idempotent so an operator can safely repeat a request after restart.
    // Neither transition touches payload bytes or changes causal evidence.
    [[nodiscard]] SyncReplicaSqliteHistoricalVersionPinResult
    pin_historical_version_or_throw(std::string operation_id);
    [[nodiscard]] SyncReplicaSqliteHistoricalVersionPinResult
    unpin_historical_version_or_throw(std::string operation_id);

    // Share-global publication surfaces. These mint immutable share evidence
    // without naming current peers or creating delivery intents. A later
    // reconciler may derive destination work from grants and peer knowledge.
    // The unguarded file form is for callers that already serialize observation
    // and publication. A scanner must use the exact observed-head form so a
    // concurrent remote admission cannot turn stale bytes into a successor.
    [[nodiscard]] SyncReplicaOperation publish_local_file_or_throw(
        std::string canonical_path,
        std::uint64_t size_bytes,
        std::string content_sha256);
    [[nodiscard]] SyncReplicaOperation
    publish_local_file_from_observed_heads_or_throw(
        std::string canonical_path,
        std::span<const std::string> observed_visible_operation_ids,
        std::uint64_t size_bytes,
        std::string content_sha256);

    // Two-step catalog composition. Preparation is a transaction-pinned read
    // and has no durable side effect. Commit either publishes that exact
    // operation, proves it was already published by this local actor/counter,
    // or reports changed local-mint, policy, or target-path authority without
    // mutating the store. Unrelated remote paths and delivery liveness do not
    // invalidate a prepared local file.
    [[nodiscard]] SyncReplicaSqlitePreparedLocalFilePublication
    prepare_local_file_from_observed_heads_or_throw(
        std::string canonical_path,
        std::span<const std::string> observed_visible_operation_ids,
        std::uint64_t size_bytes,
        std::string content_sha256);
    [[nodiscard]] SyncReplicaSqlitePreparedPublicationResult
    commit_prepared_local_file_or_throw(
        const SyncReplicaSqlitePreparedLocalFilePublication& prepared);
    [[nodiscard]] SyncReplicaOperation
    resolve_published_local_file_conflict_or_throw(
        std::string canonical_path,
        std::span<const std::string> expected_visible_operation_ids,
        std::uint64_t size_bytes,
        std::string content_sha256);
    [[nodiscard]] SyncReplicaOperation publish_local_tombstone_or_throw(
        std::string canonical_path);
    [[nodiscard]] SyncReplicaOperation
    publish_local_tombstone_from_observed_heads_or_throw(
        std::string canonical_path,
        std::span<const std::string> observed_visible_operation_ids);

    // Publishes one exact-content path identity continuation without changing
    // the operation codec. The source must currently expose exactly one File
    // head matching the supplied content; the destination must be absent. The
    // destination File and source Tombstone commit atomically in this database.
    // Unrelated evidence may advance the global frontier, but any source or
    // destination path-head change rejects the composition before durable effect.
    [[nodiscard]] SyncReplicaSqliteLocalRenamePublicationResult
    publish_local_identity_preserving_rename_from_observed_heads_or_throw(
        std::string source_canonical_path,
        std::span<const std::string> observed_source_visible_operation_ids,
        std::string destination_canonical_path,
        std::span<const std::string> observed_destination_visible_operation_ids,
        std::uint64_t size_bytes,
        std::string content_sha256);

    // Courier compatibility surfaces. These preserve the existing atomic
    // "publish plus selected destination intents" composition used by the
    // manually driven CLI. Product folder publication should use the explicit
    // destination-free methods above.
    [[nodiscard]] SyncReplicaOperation create_local_file_or_throw(
        std::string canonical_path,
        std::uint64_t size_bytes,
        std::string content_sha256,
        std::span<const std::string> destination_device_ids);
    [[nodiscard]] SyncReplicaOperation
    create_local_file_from_observed_heads_or_throw(
        std::string canonical_path,
        std::span<const std::string> observed_visible_operation_ids,
        std::uint64_t size_bytes,
        std::string content_sha256,
        std::span<const std::string> destination_device_ids = {});
    [[nodiscard]] SyncReplicaOperation
    resolve_local_file_conflict_or_throw(
        std::string canonical_path,
        std::span<const std::string> expected_visible_operation_ids,
        std::uint64_t size_bytes,
        std::string content_sha256,
        std::span<const std::string> destination_device_ids = {});
    [[nodiscard]] SyncReplicaOperation create_local_tombstone_or_throw(
        std::string canonical_path,
        std::span<const std::string> destination_device_ids);

    // Adds disposable delivery intents for one already-retained active
    // operation. This admits both local and remote active evidence so a future
    // reconciliation owner can relay dependencies and current heads. Exact
    // existing destination/operation pairs are counted as already present and
    // do not advance the durable generation. Settled pairs may be re-enqueued;
    // duplicate delivery remains receiver-idempotent.
    [[nodiscard]] SyncReplicaSqliteOutboxEnqueueResult
    enqueue_operation_for_destinations_or_throw(
        const std::string& operation_id,
        std::span<const std::string> destination_device_ids);

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

    // Acquires an unchanged visible-projection guard backed by BEGIN IMMEDIATE
    // only when the complete current projection digest exactly matches the
    // caller's previously attested value. Unlike the operation-specific guard
    // below, this surface also covers empty projections and tombstones. It is
    // intended for a coordinator that must publish scheduling evidence in a
    // second durable owner without allowing a causal writer to move the
    // authorizing projection between final reproof and that publication.
    // A null result means the visible projection advanced; no durable row is
    // changed. Unrelated outbox/clock changes are deliberately tolerated when
    // they leave visible_state_digest unchanged.
    [[nodiscard]] std::unique_ptr<SyncReplicaSqliteProjectionGuard>
    guard_visible_state_at_digest_or_throw(
        const std::string& expected_visible_state_digest);

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
    enum class LocalPublicationPurpose {
        Ordinary,
        ConflictResolution,
    };

    [[nodiscard]] SyncReplicaOperation create_local_publication_or_throw(
        std::string canonical_path,
        SyncReplicaValueKind kind,
        std::uint64_t size_bytes,
        std::string content_sha256,
        std::optional<std::vector<std::string>>
            expected_visible_operation_ids,
        LocalPublicationPurpose purpose,
        std::span<const std::string> destination_device_ids);

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
