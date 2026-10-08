#pragma once


#include <cstdint>
#include <string>
#include <string_view>

namespace anonsync {

inline constexpr std::uint64_t kSyncReplicaOutboxMaxLeaseSeconds =
    24U * 60U * 60U;
inline constexpr std::uint64_t kSyncReplicaOutboxMaxClaimLifetimeSeconds =
    24U * 60U * 60U;
inline constexpr std::uint64_t kSyncReplicaOutboxMaxRetryDelaySeconds =
    24U * 60U * 60U;

// Values are stored as durable protocol bytes in SQLite. Keep the numeric
// representation explicit so a compiler or refactor cannot silently rewrite
// existing rows.
enum class SyncReplicaOutboxRetryReleaseProvenance : std::uint8_t {
    None = 0U,
    Exact = 1U,
    LegacyUnproven = 2U,
};

// Durable dispatch state for one immutable (destination, operation) intent.
// The intent remains unsettled until the exact current claim is settled. An
// expired claim may be replaced, but its old receipt can never settle the new
// attempt. Expiry also revokes settlement, retry-release, and renewal authority
// from the still-stored receipt: a lease is not merely a hint that another
// worker may race it. Time can revoke authority but can never grant it; the
// exact current claim ID is always required before the deadline.
struct SyncReplicaOutboxLeaseState final {
    std::uint64_t dispatch_attempts = 0;
    std::string claim_id;
    std::string worker_id;
    std::uint64_t claimed_at_epoch = 0;
    std::uint64_t lease_expires_at_epoch = 0;
    std::uint64_t retry_not_before_epoch = 0;
    std::uint64_t retry_released_at_epoch = 0;
    // Exact retains the accepted owner-time observation that minted the retry
    // schedule. LegacyUnproven is migration evidence: an older schema retained
    // the deadline but discarded that observation. Migration must not guess it.
    SyncReplicaOutboxRetryReleaseProvenance retry_release_provenance =
        SyncReplicaOutboxRetryReleaseProvenance::None;

    bool operator==(const SyncReplicaOutboxLeaseState&) const = default;
};

enum class SyncReplicaOutboxClaimStatus {
    Current,
    Stale,
    Expired,
};

void validate_sync_replica_outbox_lease_state_or_throw(
    const SyncReplicaOutboxLeaseState& state,
    const std::string& label);

[[nodiscard]] bool sync_replica_outbox_lease_is_claimable_at_or_throw(
    const SyncReplicaOutboxLeaseState& state,
    std::uint64_t now_epoch,
    const std::string& label);

// Classifies one receipt against the exact stored attempt. The deadline is
// exclusive: at lease_expires_at_epoch the current receipt is expired. A stale
// receipt is reported as stale even when a newer attempt has a later clock.
[[nodiscard]] SyncReplicaOutboxClaimStatus
sync_replica_outbox_claim_status_at_or_throw(
    const SyncReplicaOutboxLeaseState& state,
    std::string_view expected_claim_id,
    std::uint64_t now_epoch,
    const std::string& label);

// Entropy must contain exactly 32 CSPRNG bytes. Keeping entropy injection at
// this pure boundary makes the state machine deterministic under test while the
// SQLite owner remains responsible for obtaining process-local CSPRNG output.
[[nodiscard]] SyncReplicaOutboxLeaseState
claim_sync_replica_outbox_lease_or_throw(
    const SyncReplicaOutboxLeaseState& current,
    std::string_view folder_id,
    std::string_view destination_device_id,
    std::string_view operation_id,
    std::uint64_t enqueued_generation,
    std::string_view current_cutpoint_digest,
    std::string worker_id,
    std::uint64_t now_epoch,
    std::uint64_t lease_seconds,
    std::string_view entropy,
    const std::string& label);

// Extends one still-current, still-live receipt without changing attempt
// identity. A heartbeat never shortens a lease and cannot extend one claim
// beyond the fixed cumulative lifetime budget measured from claimed_at_epoch.
// Returning an unchanged state means the existing deadline already covers the
// requested interval.
[[nodiscard]] SyncReplicaOutboxLeaseState
renew_sync_replica_outbox_lease_or_throw(
    const SyncReplicaOutboxLeaseState& current,
    std::string_view expected_claim_id,
    std::uint64_t now_epoch,
    std::uint64_t lease_seconds,
    const std::string& label);

[[nodiscard]] SyncReplicaOutboxLeaseState
release_sync_replica_outbox_lease_or_throw(
    const SyncReplicaOutboxLeaseState& current,
    std::string_view expected_claim_id,
    std::uint64_t now_epoch,
    std::uint64_t retry_delay_seconds,
    const std::string& label);

}  // namespace anonsync
