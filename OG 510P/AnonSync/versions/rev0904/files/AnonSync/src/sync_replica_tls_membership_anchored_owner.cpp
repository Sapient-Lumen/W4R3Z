#include "sync_replica_tls_membership_anchored_owner.hpp"

#include "sha256_digest.hpp"
#include "sync_replica_tls_policy_sqlite_profile.hpp"

#include <cstddef>
#include <stdexcept>
#include <string>
#include <utility>

namespace anonsync {
namespace {

[[nodiscard]] std::string anchor_text(
    const SyncReplicaTlsMembershipAnchor& anchor) {
    return "generation " + std::to_string(anchor.state_generation) +
           " digest " + anchor.chain_digest;
}

class MembershipAuthoritySuperseded final : public std::runtime_error {
public:
    explicit MembershipAuthoritySuperseded(const std::string& message)
        : std::runtime_error(message) {}
};

}  // namespace

SyncReplicaTlsAnchoredMembershipAuthority::
    SyncReplicaTlsAnchoredMembershipAuthority(
        SyncReplicaTlsMembershipAuthority membership,
        SyncReplicaTlsMembershipAnchor durable_anchor,
        std::uint64_t durable_transition_sequence,
        std::string durable_transition_digest)
    : membership_(std::move(membership)),
      durable_anchor_(std::move(durable_anchor)),
      durable_transition_sequence_(durable_transition_sequence),
      durable_transition_digest_(std::move(durable_transition_digest)) {
    require_active_or_throw("anchored membership authority construction");
    validate_sync_replica_tls_membership_anchor_or_throw(
        durable_anchor_, "anchored membership durable anchor");
    if (durable_anchor_ != membership_.anchor()) {
        throw std::invalid_argument(
            "anchored membership durable anchor is not the exact membership authority cutpoint");
    }
    if (!is_lowercase_sha256_hex(durable_transition_digest_)) {
        throw std::invalid_argument(
            "anchored membership transition digest is not lowercase SHA-256");
    }
}

void SyncReplicaTlsAnchoredMembershipAuthority::require_active_or_throw(
    std::string_view label) const {
    if (!membership_.active()) {
        throw std::logic_error(
            std::string(label) + " anchored membership authority is inactive");
    }
}

const SyncReplicaTlsMembershipSnapshot&
SyncReplicaTlsAnchoredMembershipAuthority::snapshot() const {
    require_active_or_throw("anchored membership snapshot");
    return membership_.snapshot();
}

std::uint64_t
SyncReplicaTlsAnchoredMembershipAuthority::state_generation() const {
    require_active_or_throw("anchored membership generation");
    return membership_.state_generation();
}

const std::string&
SyncReplicaTlsAnchoredMembershipAuthority::previous_chain_digest() const {
    require_active_or_throw("anchored membership prior chain");
    return membership_.previous_chain_digest();
}

const std::string&
SyncReplicaTlsAnchoredMembershipAuthority::chain_digest() const {
    require_active_or_throw("anchored membership chain");
    return membership_.chain_digest();
}

SyncReplicaTlsMembershipAnchor
SyncReplicaTlsAnchoredMembershipAuthority::anchor() const {
    require_active_or_throw("anchored membership anchor");
    return membership_.anchor();
}

const SyncReplicaTlsMembershipAnchor&
SyncReplicaTlsAnchoredMembershipAuthority::durable_anchor() const {
    require_active_or_throw("anchored membership durable anchor");
    return durable_anchor_;
}

std::uint64_t
SyncReplicaTlsAnchoredMembershipAuthority::durable_transition_sequence() const {
    require_active_or_throw("anchored membership transition sequence");
    return durable_transition_sequence_;
}

const std::string&
SyncReplicaTlsAnchoredMembershipAuthority::durable_transition_digest() const {
    require_active_or_throw("anchored membership transition digest");
    return durable_transition_digest_;
}

SyncReplicaTlsMembershipAnchoredOwner::
    SyncReplicaTlsMembershipAnchoredOwner(
        SyncReplicaTlsMembershipSqliteOwner& membership_owner,
        SyncReplicaTlsMembershipAnchorSqliteOwner& anchor_owner,
        std::string label)
    : membership_owner_(membership_owner),
      anchor_owner_(anchor_owner),
      label_(std::move(label)) {
    if (label_.empty()) {
        throw std::invalid_argument(
            "sync replica TLS anchored membership owner label must not be empty");
    }
    if (membership_owner_.folder_id() != anchor_owner_.folder_id() ||
        membership_owner_.local_actor() != anchor_owner_.local_actor()) {
        throw std::invalid_argument(
            label_ +
            " membership and anchor owners do not describe the same identity");
    }
    require_distinct_sync_replica_tls_policy_sqlite_databases_or_throw(
        membership_owner_.database_filename(),
        anchor_owner_.database_filename(),
        label_ + " independent persistence preflight");

    // Construction validates the independent anchor against the complete
    // membership chain but deliberately does not mutate either store. Callers
    // choose an explicit reconciliation/current/publish operation before any
    // authority can escape.
    const SyncReplicaTlsMembershipAnchorSqliteSnapshot anchor_snapshot =
        anchor_owner_.snapshot_or_throw();
    (void)membership_owner_.snapshot_or_throw(
        anchor_snapshot.current_anchor);
}

bool SyncReplicaTlsMembershipAnchoredOwner::snapshot_contains_anchor(
    const SyncReplicaTlsMembershipSqliteSnapshot& snapshot,
    const SyncReplicaTlsMembershipAnchor& anchor) const {
    validate_sync_replica_tls_membership_anchor_or_throw(
        anchor, label_ + " chain-coverage target");
    if (snapshot.folder_id != membership_owner_.folder_id() ||
        snapshot.local_actor != membership_owner_.local_actor()) {
        throw std::runtime_error(
            label_ + " membership snapshot identity changed under its owner");
    }
    if (anchor.state_generation > snapshot.state_generation) {
        return false;
    }
    if (anchor.state_generation == 0U) {
        return anchor ==
               sync_replica_tls_membership_genesis_anchor_or_throw(
                   snapshot.folder_id, snapshot.local_actor,
                   label_ + " chain-coverage genesis");
    }

    const std::size_t index = static_cast<std::size_t>(
        anchor.state_generation - 1U);
    if (index >= snapshot.history.size()) {
        return false;
    }
    const SyncReplicaTlsMembershipHistoryRecord& record =
        snapshot.history[index];
    return record.state_generation == anchor.state_generation &&
           record.chain_digest == anchor.chain_digest;
}

SyncReplicaTlsMembershipAnchorCoverageResult
SyncReplicaTlsMembershipAnchoredOwner::ensure_anchor_covers_or_throw(
    const SyncReplicaTlsMembershipAnchor& target) {
    validate_sync_replica_tls_membership_anchor_or_throw(
        target, label_ + " requested coverage target");

    for (std::uint64_t attempt = 1U;
         attempt <= kSyncReplicaTlsMembershipAnchorReconciliationMaxAttempts;
         ++attempt) {
        const SyncReplicaTlsMembershipAnchorSqliteSnapshot anchor_snapshot =
            anchor_owner_.snapshot_or_throw();

        // The independently retained anchor is always supplied back to the
        // membership owner before a newer target is trusted. This catches a
        // whole-file rollback below the retained generation and a divergent
        // replacement through that generation.
        const SyncReplicaTlsMembershipSqliteSnapshot membership_snapshot =
            membership_owner_.snapshot_or_throw(
                anchor_snapshot.current_anchor);
        if (!snapshot_contains_anchor(membership_snapshot, target)) {
            throw std::runtime_error(
                label_ + " membership chain does not contain requested " +
                anchor_text(target));
        }
        if (!snapshot_contains_anchor(
                membership_snapshot, anchor_snapshot.current_anchor)) {
            // Normally unreachable because snapshot_or_throw(trusted_anchor)
            // made this proof already. Keep the coordinator invariant explicit
            // rather than relying on a callee's future implementation shape.
            throw std::runtime_error(
                label_ +
                " membership chain no longer contains its durable anchor");
        }

        if (anchor_snapshot.current_anchor.state_generation >=
            target.state_generation) {
            return {
                anchor_snapshot.current_anchor == target
                    ? SyncReplicaTlsMembershipAnchorCoverageDisposition::
                          AlreadyExact
                    : SyncReplicaTlsMembershipAnchorCoverageDisposition::
                          CoveredByNewer,
                target,
                anchor_snapshot.current_anchor,
                attempt};
        }

        const SyncReplicaTlsMembershipAnchorAdvanceResult advanced =
            anchor_owner_.advance_or_throw(
                anchor_snapshot.current_anchor, target);
        switch (advanced.disposition) {
            case SyncReplicaTlsMembershipAnchorAdvanceDisposition::Advanced:
            case SyncReplicaTlsMembershipAnchorAdvanceDisposition::
                AlreadyCurrent:
                if (advanced.durable_after != target) {
                    throw std::runtime_error(
                        label_ +
                        " anchor owner reported success at the wrong cutpoint");
                }
                return {
                    SyncReplicaTlsMembershipAnchorCoverageDisposition::Advanced,
                    target,
                    advanced.durable_after,
                    attempt};
            case SyncReplicaTlsMembershipAnchorAdvanceDisposition::
                StaleExpected:
                // Another exact owner advanced between read and CAS. Re-read
                // both stores and prove that the observed winner still lies on
                // this membership chain before accepting it as coverage.
                break;
        }
    }

    throw std::runtime_error(
        label_ +
        " membership anchor reconciliation exceeded its bounded contention budget");
}

SyncReplicaTlsMembershipAnchorCoverageResult
SyncReplicaTlsMembershipAnchoredOwner::reconcile_or_throw() {
    const SyncReplicaTlsMembershipAnchorSqliteSnapshot anchor_snapshot =
        anchor_owner_.snapshot_or_throw();
    const SyncReplicaTlsMembershipSqliteSnapshot membership_snapshot =
        membership_owner_.snapshot_or_throw(anchor_snapshot.current_anchor);
    return ensure_anchor_covers_or_throw(membership_snapshot.anchor());
}

SyncReplicaTlsAnchoredMembershipAuthority
SyncReplicaTlsMembershipAnchoredOwner::current_authority_or_throw() {
    for (std::uint64_t attempt = 1U;
         attempt <= kSyncReplicaTlsMembershipAnchorReconciliationMaxAttempts;
         ++attempt) {
        const SyncReplicaTlsMembershipAnchorSqliteSnapshot anchor_snapshot =
            anchor_owner_.snapshot_or_throw();
        SyncReplicaTlsMembershipSqliteSnapshot membership_snapshot =
            membership_owner_.snapshot_or_throw(
                anchor_snapshot.current_anchor);
        if (!membership_snapshot.current_authority.has_value()) {
            throw std::logic_error(
                label_ + " has no published membership authority");
        }

        try {
            // Return the authority only if it remains the exact current
            // membership and anchor cutpoint through final sealing. A newer
            // policy observed before capability emission causes a bounded
            // retry rather than authorizing from a known-stale snapshot.
            return seal_authority_or_throw(
                std::move(*membership_snapshot.current_authority));
        } catch (const MembershipAuthoritySuperseded&) {
            // Another exact publisher won before emission. Reconstruct current
            // policy instead of leaking the superseded authorization snapshot.
        }
    }
    throw std::runtime_error(
        label_ +
        " current anchored membership authority exceeded its bounded contention budget");
}

SyncReplicaTlsAnchoredMembershipAuthority
SyncReplicaTlsMembershipAnchoredOwner::publish_or_throw(
    const SyncReplicaTlsMembershipAnchor& expected_current,
    std::uint64_t policy_epoch,
    std::vector<SyncReplicaTlsMembershipEntry> entries) {
    validate_sync_replica_tls_membership_anchor_or_throw(
        expected_current, label_ + " expected membership anchor");

    const SyncReplicaTlsMembershipAnchorSqliteSnapshot anchor_snapshot =
        anchor_owner_.snapshot_or_throw();
    const SyncReplicaTlsMembershipSqliteSnapshot membership_snapshot =
        membership_owner_.snapshot_or_throw(anchor_snapshot.current_anchor);

    // Close any earlier post-membership/pre-anchor crash gap before permitting
    // a new append. This keeps each coordinator publication rooted in a
    // cutpoint independently retained before the next membership transaction.
    (void)ensure_anchor_covers_or_throw(membership_snapshot.anchor());
    if (membership_snapshot.anchor() != expected_current) {
        throw std::runtime_error(
            label_ + " expected-current membership anchor is stale");
    }

    SyncReplicaTlsMembershipAuthority authority =
        membership_owner_.publish_or_throw(
            expected_current, policy_epoch, std::move(entries));
    // The authority remains local and move-only until the second durable store
    // covers the exact committed membership cutpoint. Failure here intentionally
    // throws after membership commit; restart reconciliation is the recovery
    // path, and no unanchored authority escapes this call.
    return seal_authority_or_throw(std::move(authority));
}

SyncReplicaTlsAnchoredMembershipAuthority
SyncReplicaTlsMembershipAnchoredOwner::seal_authority_or_throw(
    SyncReplicaTlsMembershipAuthority membership) {
    if (!membership.active()) {
        throw std::invalid_argument(
            label_ + " cannot seal an inactive membership authority");
    }
    const SyncReplicaTlsMembershipAnchor target = membership.anchor();
    (void)ensure_anchor_covers_or_throw(target);

    const SyncReplicaTlsMembershipAnchorSqliteSnapshot anchor_snapshot =
        anchor_owner_.snapshot_or_throw();
    const SyncReplicaTlsMembershipSqliteSnapshot membership_snapshot =
        membership_owner_.snapshot_or_throw(anchor_snapshot.current_anchor);
    if (!snapshot_contains_anchor(membership_snapshot, target)) {
        throw std::runtime_error(
            label_ +
            " durable anchor did not retain the membership authority cutpoint");
    }
    if (anchor_snapshot.current_anchor != target ||
        membership_snapshot.anchor() != target) {
        throw MembershipAuthoritySuperseded(
            label_ +
            " membership authority was superseded before anchored emission");
    }

    return SyncReplicaTlsAnchoredMembershipAuthority(
        std::move(membership), anchor_snapshot.current_anchor,
        anchor_snapshot.transition_sequence,
        anchor_snapshot.current_transition_digest);
}

}  // namespace anonsync
