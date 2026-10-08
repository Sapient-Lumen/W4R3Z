#pragma once

#include "sync_replica_tls_membership_sqlite_owner.hpp"
#include "sync_replica_tls_policy_sqlite_profile.hpp"
#include "sync_sqlite_handle_slot.hpp"

#include <cstdint>
#include <string>
#include <string_view>
#include <vector>

namespace anonsync {

inline constexpr std::uint64_t
    kSyncReplicaTlsMembershipAnchorMaxTransitions = 65536U;

struct SyncReplicaTlsMembershipAnchorTransition final {
    std::uint64_t transition_sequence = 0U;
    SyncReplicaTlsMembershipAnchor previous_anchor;
    SyncReplicaTlsMembershipAnchor current_anchor;
    std::string previous_transition_digest;
    std::string transition_digest;

    bool operator==(
        const SyncReplicaTlsMembershipAnchorTransition&) const = default;
};

struct SyncReplicaTlsMembershipAnchorSqliteSnapshot final {
    std::string folder_id;
    SyncReplicaActor local_actor;
    std::uint64_t transition_sequence = 0U;
    SyncReplicaTlsMembershipAnchor current_anchor;
    std::string current_transition_digest;
    std::vector<SyncReplicaTlsMembershipAnchorTransition> history;
};

enum class SyncReplicaTlsMembershipAnchorAdvanceDisposition : std::uint8_t {
    Advanced = 1,
    AlreadyCurrent = 2,
    StaleExpected = 3,
};

struct SyncReplicaTlsMembershipAnchorAdvanceResult final {
    SyncReplicaTlsMembershipAnchorAdvanceDisposition disposition =
        SyncReplicaTlsMembershipAnchorAdvanceDisposition::StaleExpected;
    SyncReplicaTlsMembershipAnchor observed_before;
    SyncReplicaTlsMembershipAnchor durable_after;
    std::uint64_t transition_sequence = 0U;
    std::string transition_digest;
};

// Independently persisted monotonic checkpoint for one membership chain. The
// store starts at the canonical generation-zero anchor and records every
// successful advance in an append-only digest chain. Advance is exact-CAS and
// idempotent for the same target, and it may jump across multiple membership
// generations during crash recovery. The owner retains and re-attests the
// exact serialized SQLite connection generation for its lifetime, so a moved
// or refilled caller handle slot cannot silently retarget the checkpoint.
//
// This owner is useful only when its database is retained in a trust/storage
// domain independent from the membership database. It does not make SQLite a
// hardware monotonic counter, does not sign anchors, and cannot detect an
// attacker who rolls back or replaces both stores together.
class SyncReplicaTlsMembershipAnchorSqliteOwner final {
public:
    SyncReplicaTlsMembershipAnchorSqliteOwner(
        SyncSqliteDbHandleSlot& db,
        std::string folder_id,
        SyncReplicaActor local_actor,
        std::string label =
            "sync replica TLS membership anchor SQLite owner");

    SyncReplicaTlsMembershipAnchorSqliteOwner(
        SyncSqliteDbHandleSlot& db,
        std::string folder_id,
        SyncReplicaActor local_actor,
        SyncReplicaTlsPolicySqliteBackendDisposition backend_disposition,
        std::string label);

    SyncReplicaTlsMembershipAnchorSqliteOwner(
        const SyncReplicaTlsMembershipAnchorSqliteOwner&) = delete;
    SyncReplicaTlsMembershipAnchorSqliteOwner& operator=(
        const SyncReplicaTlsMembershipAnchorSqliteOwner&) = delete;
    SyncReplicaTlsMembershipAnchorSqliteOwner(
        SyncReplicaTlsMembershipAnchorSqliteOwner&&) = delete;
    SyncReplicaTlsMembershipAnchorSqliteOwner& operator=(
        SyncReplicaTlsMembershipAnchorSqliteOwner&&) = delete;

    [[nodiscard]] const std::string& folder_id() const noexcept {
        return folder_id_;
    }

    [[nodiscard]] const SyncReplicaActor& local_actor() const noexcept {
        return local_actor_;
    }

    [[nodiscard]] const std::string& database_filename() const noexcept {
        return database_.database_filename();
    }

    [[nodiscard]] SyncReplicaTlsMembershipAnchorSqliteSnapshot
    snapshot_or_throw();

    // Attempts one strict monotonic transition. If the durable store already
    // equals `next`, returns AlreadyCurrent so an ambiguous commit can be
    // retried exactly. If it equals neither `expected_current` nor `next`,
    // returns StaleExpected without mutation; callers must re-read and reprove
    // chain coverage rather than treating a newer generation as equivalent.
    [[nodiscard]] SyncReplicaTlsMembershipAnchorAdvanceResult
    advance_or_throw(
        const SyncReplicaTlsMembershipAnchor& expected_current,
        const SyncReplicaTlsMembershipAnchor& next);

private:
    std::string folder_id_;
    SyncReplicaActor local_actor_;
    std::string label_;
    SyncReplicaTlsPolicySqliteBackendDisposition backend_disposition_ =
        SyncReplicaTlsPolicySqliteBackendDisposition::DurableNamed;
    SyncReplicaTlsPolicySqliteConnectionBinding database_;
};

}  // namespace anonsync
