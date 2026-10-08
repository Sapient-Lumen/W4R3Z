#pragma once

#include "sync_replica_tls_membership_anchor_sqlite_owner.hpp"
#include "sync_replica_tls_membership_sqlite_owner.hpp"

#include <cstdint>
#include <string>
#include <vector>

namespace anonsync {

inline constexpr std::uint64_t
    kSyncReplicaTlsMembershipAnchorReconciliationMaxAttempts = 64U;

enum class SyncReplicaTlsMembershipAnchorCoverageDisposition : std::uint8_t {
    AlreadyExact = 1,
    Advanced = 2,
    CoveredByNewer = 3,
};

struct SyncReplicaTlsMembershipAnchorCoverageResult final {
    SyncReplicaTlsMembershipAnchorCoverageDisposition disposition =
        SyncReplicaTlsMembershipAnchorCoverageDisposition::AlreadyExact;
    SyncReplicaTlsMembershipAnchor target;
    SyncReplicaTlsMembershipAnchor durable_anchor;
    std::uint64_t attempts = 0U;
};


// Type-level proof that one membership capability was held private until an
// independently persisted anchor store covered its exact chain cutpoint. The
// raw membership authority is not implicitly convertible, so accepted-session
// code cannot accidentally bypass the coordinator by calling the history owner
// directly. The retained anchor-store digest is structural crash/rollback
// evidence, not a signature or hardware monotonic-counter attestation.
class SyncReplicaTlsAnchoredMembershipAuthority final {
public:
    SyncReplicaTlsAnchoredMembershipAuthority(
        const SyncReplicaTlsAnchoredMembershipAuthority&) = delete;
    SyncReplicaTlsAnchoredMembershipAuthority& operator=(
        const SyncReplicaTlsAnchoredMembershipAuthority&) = delete;
    SyncReplicaTlsAnchoredMembershipAuthority(
        SyncReplicaTlsAnchoredMembershipAuthority&&) noexcept = default;
    SyncReplicaTlsAnchoredMembershipAuthority& operator=(
        SyncReplicaTlsAnchoredMembershipAuthority&&) noexcept = default;
    ~SyncReplicaTlsAnchoredMembershipAuthority() noexcept = default;

    [[nodiscard]] bool active() const noexcept {
        return membership_.active();
    }

    [[nodiscard]] const SyncReplicaTlsMembershipSnapshot& snapshot() const;
    [[nodiscard]] std::uint64_t state_generation() const;
    [[nodiscard]] const std::string& previous_chain_digest() const;
    [[nodiscard]] const std::string& chain_digest() const;
    [[nodiscard]] SyncReplicaTlsMembershipAnchor anchor() const;

    [[nodiscard]] const SyncReplicaTlsMembershipAnchor&
    durable_anchor() const;
    [[nodiscard]] std::uint64_t durable_transition_sequence() const;
    [[nodiscard]] const std::string& durable_transition_digest() const;

private:
    SyncReplicaTlsAnchoredMembershipAuthority(
        SyncReplicaTlsMembershipAuthority membership,
        SyncReplicaTlsMembershipAnchor durable_anchor,
        std::uint64_t durable_transition_sequence,
        std::string durable_transition_digest);

    void require_active_or_throw(std::string_view label) const;

    SyncReplicaTlsMembershipAuthority membership_;
    SyncReplicaTlsMembershipAnchor durable_anchor_;
    std::uint64_t durable_transition_sequence_ = 0U;
    std::string durable_transition_digest_;

    friend class SyncReplicaTlsMembershipAnchoredOwner;
};

// Coordinates the append-only membership database with an independently
// persisted monotonic anchor database. Membership commits first; the returned
// accepted-session authority remains private until the anchor store covers that
// exact chain cutpoint. A crash or storage failure in the gap can leave a valid
// membership generation ahead of the anchor, but restart reconciliation closes
// that gap before any authority is emitted.
//
// The two SQLite transactions are deliberately not described as atomic. This
// owner makes their order and recovery semantics executable; it cannot detect a
// malicious replacement of both stores, authenticate unsigned policy updates,
// or retroactively revoke authority already issued under an older generation.
class SyncReplicaTlsMembershipAnchoredOwner final {
public:
    SyncReplicaTlsMembershipAnchoredOwner(
        SyncReplicaTlsMembershipSqliteOwner& membership_owner,
        SyncReplicaTlsMembershipAnchorSqliteOwner& anchor_owner,
        std::string label = "sync replica TLS anchored membership owner");

    SyncReplicaTlsMembershipAnchoredOwner(
        const SyncReplicaTlsMembershipAnchoredOwner&) = delete;
    SyncReplicaTlsMembershipAnchoredOwner& operator=(
        const SyncReplicaTlsMembershipAnchoredOwner&) = delete;
    SyncReplicaTlsMembershipAnchoredOwner(
        SyncReplicaTlsMembershipAnchoredOwner&&) = delete;
    SyncReplicaTlsMembershipAnchoredOwner& operator=(
        SyncReplicaTlsMembershipAnchoredOwner&&) = delete;

    // Advances a lagging anchor directly to the current valid membership
    // cutpoint. No membership authority is returned by reconciliation alone.
    [[nodiscard]] SyncReplicaTlsMembershipAnchorCoverageResult
    reconcile_or_throw();

    // Returns a move-only authority from one membership snapshot only after the
    // independent anchor store covers that snapshot's exact chain cutpoint.
    [[nodiscard]] SyncReplicaTlsAnchoredMembershipAuthority
    current_authority_or_throw();

    // Reconciles any prior crash gap, performs exact membership CAS, commits the
    // membership history first, and then makes the independent anchor cover the
    // committed cutpoint. If anchoring fails, no authority escapes; a later
    // reconcile/current call can recover the committed generation.
    [[nodiscard]] SyncReplicaTlsAnchoredMembershipAuthority publish_or_throw(
        const SyncReplicaTlsMembershipAnchor& expected_current,
        std::uint64_t policy_epoch,
        std::vector<SyncReplicaTlsMembershipEntry> entries);

private:
    [[nodiscard]] SyncReplicaTlsMembershipAnchorCoverageResult
    ensure_anchor_covers_or_throw(
        const SyncReplicaTlsMembershipAnchor& target);

    [[nodiscard]] bool snapshot_contains_anchor(
        const SyncReplicaTlsMembershipSqliteSnapshot& snapshot,
        const SyncReplicaTlsMembershipAnchor& anchor) const;

    [[nodiscard]] SyncReplicaTlsAnchoredMembershipAuthority
    seal_authority_or_throw(SyncReplicaTlsMembershipAuthority membership);

    SyncReplicaTlsMembershipSqliteOwner& membership_owner_;
    SyncReplicaTlsMembershipAnchorSqliteOwner& anchor_owner_;
    std::string label_;
};

}  // namespace anonsync
