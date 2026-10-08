#pragma once

#include "sync_replica_tls_membership_snapshot.hpp"
#include "sync_replica_tls_policy_sqlite_profile.hpp"
#include "sync_sqlite_handle_slot.hpp"

#include <cstdint>
#include <memory>
#include <optional>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

namespace anonsync {


inline constexpr std::uint64_t
    kSyncReplicaTlsMembershipMaxHistoryRecords = 65536U;
inline constexpr std::uint64_t
    kSyncReplicaTlsMembershipMaxRetainedEntryRows = 4194304U;

// Pure planning predicate for the owner's absolute append-only retention
// ceilings. A positive result is not publication authority: the owner repeats
// this check against the exact state reconstructed under BEGIN IMMEDIATE.
[[nodiscard]] constexpr bool
sync_replica_tls_membership_append_fits_hard_limits(
    std::uint64_t current_generation,
    std::uint64_t retained_entry_rows,
    std::uint64_t candidate_entry_rows) noexcept {
    return current_generation < kSyncReplicaTlsMembershipMaxHistoryRecords &&
           retained_entry_rows <=
               kSyncReplicaTlsMembershipMaxRetainedEntryRows &&
           candidate_entry_rows <= kSyncReplicaTlsMembershipMaxEntries &&
           candidate_entry_rows <=
               kSyncReplicaTlsMembershipMaxRetainedEntryRows -
                   retained_entry_rows;
}

// One externally retainable cutpoint in the append-only membership chain. The
// chain digest is meaningful only with its exact generation. Persisting this
// value outside the membership database lets a later owner detect whole-file
// rollback or a divergent replacement through that generation. This type is an
// anchor format, not an external durable-store implementation.
struct SyncReplicaTlsMembershipAnchor final {
    std::uint64_t state_generation = 0U;
    std::string chain_digest;

    bool operator==(const SyncReplicaTlsMembershipAnchor&) const = default;
};

// Canonical anchor-format and genesis helpers shared by the membership history
// owner, the independently persisted rollback anchor, and their coordinator.
// The digest is structural evidence, not a signature or authenticated counter.
void validate_sync_replica_tls_membership_anchor_or_throw(
    const SyncReplicaTlsMembershipAnchor& anchor,
    std::string_view label = "sync replica TLS membership anchor");

[[nodiscard]] SyncReplicaTlsMembershipAnchor
sync_replica_tls_membership_genesis_anchor_or_throw(
    std::string_view folder_id,
    const SyncReplicaActor& local_actor,
    std::string_view label =
        "sync replica TLS membership genesis anchor");

struct SyncReplicaTlsMembershipHistoryRecord final {
    std::uint64_t state_generation = 0U;
    std::uint64_t policy_epoch = 0U;
    std::uint64_t entry_count = 0U;
    std::string previous_chain_digest;
    std::string snapshot_digest;
    std::string chain_digest;

    bool operator==(const SyncReplicaTlsMembershipHistoryRecord&) const =
        default;
};

// Immutable single-use authority emitted only after one exact policy snapshot
// and its append-only chain record have committed. It is move-only; moves
// invalidate the source. The accepted TLS server takes this value by value so a
// freely constructed snapshot cannot cross the durable membership frontier and
// one issued capability cannot authorize multiple accepted sessions. The owner
// may emit multiple capabilities for the same committed cutpoint; this is not a
// one-session-per-generation nonce and does not make later policy rotation
// retroactively revoke a capability that was already issued.
class SyncReplicaTlsMembershipAuthority final {
public:
    SyncReplicaTlsMembershipAuthority(
        const SyncReplicaTlsMembershipAuthority&) = delete;
    SyncReplicaTlsMembershipAuthority& operator=(
        const SyncReplicaTlsMembershipAuthority&) = delete;
    SyncReplicaTlsMembershipAuthority(
        SyncReplicaTlsMembershipAuthority&&) noexcept = default;
    SyncReplicaTlsMembershipAuthority& operator=(
        SyncReplicaTlsMembershipAuthority&&) noexcept = default;
    ~SyncReplicaTlsMembershipAuthority() noexcept = default;

    [[nodiscard]] bool active() const noexcept {
        return static_cast<bool>(state_);
    }

    [[nodiscard]] const SyncReplicaTlsMembershipSnapshot& snapshot() const;
    [[nodiscard]] std::uint64_t state_generation() const;
    [[nodiscard]] const std::string& previous_chain_digest() const;
    [[nodiscard]] const std::string& chain_digest() const;
    [[nodiscard]] SyncReplicaTlsMembershipAnchor anchor() const;

private:
    struct State;

    explicit SyncReplicaTlsMembershipAuthority(
        std::shared_ptr<const State> state) noexcept
        : state_(std::move(state)) {}

    [[nodiscard]] const State& require_state_or_throw(
        std::string_view label) const;

    std::shared_ptr<const State> state_;

    friend class SyncReplicaTlsMembershipSqliteOwner;
};

struct SyncReplicaTlsMembershipSqliteSnapshot final {
    std::string folder_id;
    SyncReplicaActor local_actor;
    std::uint64_t state_generation = 0U;
    std::uint64_t current_policy_epoch = 0U;
    std::uint64_t current_entry_count = 0U;
    std::string current_snapshot_digest;
    std::string current_chain_digest;
    std::vector<SyncReplicaTlsMembershipHistoryRecord> history;
    std::optional<SyncReplicaTlsMembershipAuthority> current_authority;

    [[nodiscard]] SyncReplicaTlsMembershipAnchor anchor() const {
        return {state_generation, current_chain_digest};
    }

};

// Correctness-oracle owner for one folder/local-actor membership history.
// Every read and mutation restores and re-attests the complete append-only set.
// Publication is compare-and-swap against one exact current anchor, requires a
// strictly increasing caller policy epoch, writes the complete canonical
// snapshot in one BEGIN IMMEDIATE transaction, and returns authority only after
// commit. This is intentionally O(history + retained entries), not a scalable
// production index. The owner retains an exact serialized SQLite connection
// generation for its entire lifetime and re-attests that handle, generation,
// and main filename before and after durable operations; moving or refilling
// the caller's handle slot cannot silently retarget policy authority.
//
// The internal digest chain detects accidental corruption and, when paired with
// a trusted anchor retained outside this database, detects rollback or a fork
// through that anchor. It is not signed provenance and cannot by itself defeat
// a malicious local writer who can replace both the database and every external
// anchor available to the process.
class SyncReplicaTlsMembershipSqliteOwner final {
public:
    SyncReplicaTlsMembershipSqliteOwner(
        SyncSqliteDbHandleSlot& db,
        std::string folder_id,
        SyncReplicaActor local_actor,
        std::string label = "sync replica TLS membership SQLite owner");

    // Narrow bootstrap-image form. DetachedBootstrapImage permits schema and
    // genesis construction only on an anonymous writable SQLite connection;
    // the ordinary constructor remains durable named authority.
    SyncReplicaTlsMembershipSqliteOwner(
        SyncSqliteDbHandleSlot& db,
        std::string folder_id,
        SyncReplicaActor local_actor,
        SyncReplicaTlsPolicySqliteBackendDisposition backend_disposition,
        std::string label);

    SyncReplicaTlsMembershipSqliteOwner(
        const SyncReplicaTlsMembershipSqliteOwner&) = delete;
    SyncReplicaTlsMembershipSqliteOwner& operator=(
        const SyncReplicaTlsMembershipSqliteOwner&) = delete;
    SyncReplicaTlsMembershipSqliteOwner(
        SyncReplicaTlsMembershipSqliteOwner&&) = delete;
    SyncReplicaTlsMembershipSqliteOwner& operator=(
        SyncReplicaTlsMembershipSqliteOwner&&) = delete;

    [[nodiscard]] const std::string& folder_id() const noexcept {
        return folder_id_;
    }

    [[nodiscard]] const SyncReplicaActor& local_actor() const noexcept {
        return local_actor_;
    }

    [[nodiscard]] const std::string& database_filename() const noexcept {
        return database_.database_filename();
    }

    [[nodiscard]] SyncReplicaTlsMembershipSqliteSnapshot snapshot_or_throw(
        std::optional<SyncReplicaTlsMembershipAnchor> trusted_anchor =
            std::nullopt);

    [[nodiscard]] SyncReplicaTlsMembershipAuthority
    current_authority_or_throw(
        std::optional<SyncReplicaTlsMembershipAnchor> trusted_anchor =
            std::nullopt);

    [[nodiscard]] SyncReplicaTlsMembershipAuthority publish_or_throw(
        const SyncReplicaTlsMembershipAnchor& expected_current,
        std::uint64_t policy_epoch,
        std::vector<SyncReplicaTlsMembershipEntry> entries);

private:
    std::string folder_id_;
    SyncReplicaActor local_actor_;
    std::string label_;
    SyncReplicaTlsPolicySqliteBackendDisposition backend_disposition_ =
        SyncReplicaTlsPolicySqliteBackendDisposition::DurableNamed;
    SyncReplicaTlsPolicySqliteConnectionBinding database_;
};

}  // namespace anonsync
