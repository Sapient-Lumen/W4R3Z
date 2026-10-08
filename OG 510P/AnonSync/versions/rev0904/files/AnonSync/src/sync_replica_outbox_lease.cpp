#include "sync_replica_outbox_lease.hpp"

#include "sha256_digest.hpp"
#include "sync_manifest_validation.hpp"

#include <limits>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>

namespace anonsync {
namespace {

constexpr std::size_t kClaimEntropyBytes = 32U;

[[nodiscard]] std::string u64_be(std::uint64_t value) {
    std::string out(8, '\0');
    for (std::size_t index = 0; index < 8U; ++index) {
        out[7U - index] = static_cast<char>(value & 0xffU);
        value >>= 8U;
    }
    return out;
}

void append_framed(Sha256DigestBuilder& digest, std::string_view bytes) {
    if (std::cmp_greater(
            bytes.size(), std::numeric_limits<std::uint64_t>::max())) {
        throw std::overflow_error(
            "sync replica outbox claim frame length overflows uint64_t");
    }
    digest.update(u64_be(static_cast<std::uint64_t>(bytes.size())));
    digest.update(bytes);
}

[[nodiscard]] std::uint64_t lease_deadline_or_throw(
    std::uint64_t now_epoch,
    std::uint64_t lease_seconds,
    const std::string& label) {
    if (now_epoch == 0U) {
        throw std::invalid_argument(label + " now_epoch must be positive");
    }
    if (lease_seconds == 0U ||
        lease_seconds > kSyncReplicaOutboxMaxLeaseSeconds) {
        throw std::invalid_argument(
            label + " lease_seconds must be in the range 1..86400");
    }
    if (lease_seconds >
        std::numeric_limits<std::uint64_t>::max() - now_epoch) {
        throw std::overflow_error(label + " lease deadline overflows uint64_t");
    }
    return now_epoch + lease_seconds;
}

}  // namespace

void validate_sync_replica_outbox_lease_state_or_throw(
    const SyncReplicaOutboxLeaseState& state,
    const std::string& label) {
    const bool has_claim = !state.claim_id.empty();
    const bool has_worker = !state.worker_id.empty();
    const bool has_claimed_at = state.claimed_at_epoch != 0U;
    const bool has_deadline = state.lease_expires_at_epoch != 0U;

    if (has_claim != has_worker || has_claim != has_claimed_at ||
        has_claim != has_deadline) {
        throw std::runtime_error(label + " has partial lease authority");
    }
    if (has_claim) {
        if (state.dispatch_attempts == 0U ||
            !is_lowercase_sha256_hex(state.claim_id) ||
            !sync_id_is_valid(state.worker_id) ||
            state.lease_expires_at_epoch <= state.claimed_at_epoch ||
            state.retry_not_before_epoch != 0U ||
            state.retry_released_at_epoch != 0U ||
            state.retry_release_provenance !=
                SyncReplicaOutboxRetryReleaseProvenance::None) {
            throw std::runtime_error(label + " has invalid active lease authority");
        }
        if (state.lease_expires_at_epoch - state.claimed_at_epoch >
            kSyncReplicaOutboxMaxClaimLifetimeSeconds) {
            throw std::runtime_error(
                label + " exceeds the cumulative claim lifetime budget");
        }
    } else if (state.dispatch_attempts == 0U) {
        if (state.retry_not_before_epoch != 0U ||
            state.retry_released_at_epoch != 0U ||
            state.retry_release_provenance !=
                SyncReplicaOutboxRetryReleaseProvenance::None) {
            throw std::runtime_error(
                label + " backs off an intent that has never been dispatched");
        }
    } else {
        if (state.retry_not_before_epoch == 0U) {
            throw std::runtime_error(
                label + " has dispatched history without active or retry authority");
        }
        if (state.retry_release_provenance ==
            SyncReplicaOutboxRetryReleaseProvenance::None) {
            throw std::runtime_error(
                label + " has retry authority without release provenance");
        }
        if (state.retry_release_provenance ==
            SyncReplicaOutboxRetryReleaseProvenance::LegacyUnproven) {
            if (state.retry_released_at_epoch != 0U) {
                throw std::runtime_error(
                    label + " fabricates an exact legacy retry release epoch");
            }
        } else if (state.retry_release_provenance ==
                   SyncReplicaOutboxRetryReleaseProvenance::Exact) {
            if (state.retry_released_at_epoch == 0U ||
                state.retry_not_before_epoch < state.retry_released_at_epoch) {
                throw std::runtime_error(
                    label + " has invalid exact retry release provenance");
            }
            if (state.retry_not_before_epoch - state.retry_released_at_epoch >
                kSyncReplicaOutboxMaxRetryDelaySeconds) {
                throw std::runtime_error(
                    label + " exact retry delay exceeds the fixed retry budget");
            }
        } else {
            throw std::runtime_error(
                label + " has unsupported retry release provenance");
        }
    }
}

bool sync_replica_outbox_lease_is_claimable_at_or_throw(
    const SyncReplicaOutboxLeaseState& state,
    std::uint64_t now_epoch,
    const std::string& label) {
    validate_sync_replica_outbox_lease_state_or_throw(state, label);
    if (now_epoch == 0U) {
        throw std::invalid_argument(label + " now_epoch must be positive");
    }
    if (state.retry_not_before_epoch > now_epoch) return false;
    return state.claim_id.empty() || state.lease_expires_at_epoch <= now_epoch;
}

SyncReplicaOutboxClaimStatus sync_replica_outbox_claim_status_at_or_throw(
    const SyncReplicaOutboxLeaseState& state,
    std::string_view expected_claim_id,
    std::uint64_t now_epoch,
    const std::string& label) {
    validate_sync_replica_outbox_lease_state_or_throw(state, label);
    if (!is_lowercase_sha256_hex(expected_claim_id)) {
        throw std::invalid_argument(label + " expected claim id is invalid");
    }
    if (now_epoch == 0U) {
        throw std::invalid_argument(label + " now_epoch must be positive");
    }
    if (state.claim_id.empty() || state.claim_id != expected_claim_id) {
        return SyncReplicaOutboxClaimStatus::Stale;
    }
    if (now_epoch < state.claimed_at_epoch) {
        throw std::invalid_argument(
            label + " now_epoch predates the current claim");
    }
    if (now_epoch >= state.lease_expires_at_epoch) {
        return SyncReplicaOutboxClaimStatus::Expired;
    }
    return SyncReplicaOutboxClaimStatus::Current;
}

SyncReplicaOutboxLeaseState claim_sync_replica_outbox_lease_or_throw(
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
    const std::string& label) {
    validate_sync_replica_outbox_lease_state_or_throw(current, label);
    if (!sync_id_is_valid(folder_id) ||
        !sync_id_is_valid(destination_device_id) ||
        !is_lowercase_sha256_hex(operation_id) ||
        enqueued_generation == 0U ||
        !is_lowercase_sha256_hex(current_cutpoint_digest)) {
        throw std::invalid_argument(label + " claim identity is invalid");
    }
    if (!sync_id_is_valid(worker_id)) {
        throw std::invalid_argument(label + " worker identity is invalid");
    }
    if (entropy.size() != kClaimEntropyBytes) {
        throw std::invalid_argument(label + " claim entropy is not exactly 32 bytes");
    }
    if (!sync_replica_outbox_lease_is_claimable_at_or_throw(
            current, now_epoch, label)) {
        throw std::runtime_error(label + " intent is not claimable at now_epoch");
    }
    if (current.dispatch_attempts ==
        std::numeric_limits<std::uint64_t>::max()) {
        throw std::overflow_error(label + " dispatch attempt counter is exhausted");
    }

    SyncReplicaOutboxLeaseState next;
    next.dispatch_attempts = current.dispatch_attempts + 1U;
    next.worker_id = std::move(worker_id);
    next.claimed_at_epoch = now_epoch;
    next.lease_expires_at_epoch = lease_deadline_or_throw(
        now_epoch, lease_seconds, label);
    next.retry_not_before_epoch = 0U;
    next.retry_released_at_epoch = 0U;
    next.retry_release_provenance =
        SyncReplicaOutboxRetryReleaseProvenance::None;

    Sha256DigestBuilder digest;
    digest.update("anonsync-sync-replica-outbox-claim-v2");
    append_framed(digest, folder_id);
    append_framed(digest, destination_device_id);
    append_framed(digest, operation_id);
    digest.update(u64_be(enqueued_generation));
    append_framed(digest, current_cutpoint_digest);
    digest.update(u64_be(current.dispatch_attempts));
    append_framed(digest, current.claim_id);
    digest.update(u64_be(current.retry_not_before_epoch));
    digest.update(u64_be(current.retry_released_at_epoch));
    digest.update(u64_be(static_cast<std::uint64_t>(
        current.retry_release_provenance)));
    append_framed(digest, next.worker_id);
    digest.update(u64_be(next.dispatch_attempts));
    digest.update(u64_be(next.claimed_at_epoch));
    digest.update(u64_be(next.lease_expires_at_epoch));
    append_framed(digest, entropy);
    next.claim_id = digest.finish_hex();

    validate_sync_replica_outbox_lease_state_or_throw(next, label);
    return next;
}

SyncReplicaOutboxLeaseState renew_sync_replica_outbox_lease_or_throw(
    const SyncReplicaOutboxLeaseState& current,
    std::string_view expected_claim_id,
    std::uint64_t now_epoch,
    std::uint64_t lease_seconds,
    const std::string& label) {
    const SyncReplicaOutboxClaimStatus status =
        sync_replica_outbox_claim_status_at_or_throw(
            current, expected_claim_id, now_epoch, label);
    if (status == SyncReplicaOutboxClaimStatus::Stale) {
        throw std::runtime_error(label + " expected claim is stale");
    }
    if (status == SyncReplicaOutboxClaimStatus::Expired) {
        throw std::runtime_error(label + " expected claim is expired");
    }

    const std::uint64_t proposed_deadline = lease_deadline_or_throw(
        now_epoch, lease_seconds, label);
    if (proposed_deadline <= current.lease_expires_at_epoch) {
        return current;
    }
    if (proposed_deadline - current.claimed_at_epoch >
        kSyncReplicaOutboxMaxClaimLifetimeSeconds) {
        throw std::invalid_argument(
            label + " renewal exceeds the cumulative claim lifetime budget");
    }

    SyncReplicaOutboxLeaseState next = current;
    next.lease_expires_at_epoch = proposed_deadline;
    validate_sync_replica_outbox_lease_state_or_throw(next, label);
    return next;
}

SyncReplicaOutboxLeaseState release_sync_replica_outbox_lease_or_throw(
    const SyncReplicaOutboxLeaseState& current,
    std::string_view expected_claim_id,
    std::uint64_t now_epoch,
    std::uint64_t retry_delay_seconds,
    const std::string& label) {
    const SyncReplicaOutboxClaimStatus status =
        sync_replica_outbox_claim_status_at_or_throw(
            current, expected_claim_id, now_epoch, label);
    if (status == SyncReplicaOutboxClaimStatus::Stale) {
        throw std::runtime_error(label + " expected claim is stale");
    }
    if (status == SyncReplicaOutboxClaimStatus::Expired) {
        throw std::runtime_error(label + " expected claim is expired");
    }
    if (retry_delay_seconds > kSyncReplicaOutboxMaxRetryDelaySeconds) {
        throw std::invalid_argument(
            label + " retry delay exceeds the fixed retry budget");
    }
    if (retry_delay_seconds >
        std::numeric_limits<std::uint64_t>::max() - now_epoch) {
        throw std::overflow_error(
            label + " retry deadline overflows uint64_t");
    }

    SyncReplicaOutboxLeaseState next;
    next.dispatch_attempts = current.dispatch_attempts;
    next.retry_not_before_epoch = now_epoch + retry_delay_seconds;
    next.retry_released_at_epoch = now_epoch;
    next.retry_release_provenance =
        SyncReplicaOutboxRetryReleaseProvenance::Exact;
    validate_sync_replica_outbox_lease_state_or_throw(next, label);
    return next;
}

}  // namespace anonsync
