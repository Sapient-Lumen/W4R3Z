#include "sha256_digest.hpp"
#include "sync_replica_outbox_lease.hpp"

#include <cstdint>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>

namespace {

using anonsync::SyncReplicaOutboxLeaseState;

std::size_t checks = 0;

[[noreturn]] void fail(const std::string& message) {
    throw std::runtime_error(message);
}

void require(bool condition, const std::string& message) {
    ++checks;
    if (!condition) fail(message);
}

template <typename Callable>
void require_error(
    Callable&& callable,
    std::string_view expected,
    const std::string& message) {
    ++checks;
    try {
        std::forward<Callable>(callable)();
    } catch (const std::exception& error) {
        if (std::string_view(error.what()).find(expected) ==
            std::string_view::npos) {
            fail(message + " returned unexpected error: " + error.what());
        }
        return;
    }
    fail(message + " did not reject");
}

SyncReplicaOutboxLeaseState claim(
    const SyncReplicaOutboxLeaseState& current,
    std::uint64_t now,
    std::string worker,
    char entropy_byte) {
    return anonsync::claim_sync_replica_outbox_lease_or_throw(
        current,
        "folder-lease-policy",
        "device-lease-peer",
        anonsync::sha256_hex("operation"),
        7U,
        anonsync::sha256_hex("cutpoint"),
        std::move(worker),
        now,
        10U,
        std::string(32U, entropy_byte),
        "lease policy test");
}

void test_claim_expiry_reclaim_and_release() {
    SyncReplicaOutboxLeaseState state;
    anonsync::validate_sync_replica_outbox_lease_state_or_throw(
        state, "fresh state");
    require(anonsync::sync_replica_outbox_lease_is_claimable_at_or_throw(
                state, 100U, "fresh state"),
            "fresh intent was not claimable");

    const SyncReplicaOutboxLeaseState first =
        claim(state, 100U, "worker-a", 'a');
    require(first.dispatch_attempts == 1U &&
                first.worker_id == "worker-a" &&
                first.claimed_at_epoch == 100U &&
                first.lease_expires_at_epoch == 110U &&
                first.retry_not_before_epoch == 0U &&
                first.retry_released_at_epoch == 0U &&
                first.retry_release_provenance ==
                    anonsync::SyncReplicaOutboxRetryReleaseProvenance::None &&
                anonsync::is_lowercase_sha256_hex(first.claim_id),
            "first claim did not mint exact lease authority");
    require(!anonsync::sync_replica_outbox_lease_is_claimable_at_or_throw(
                first, 109U, "active first claim"),
            "unexpired claim was stealable");
    require(anonsync::sync_replica_outbox_lease_is_claimable_at_or_throw(
                first, 110U, "expired first claim"),
            "claim did not expire at its exact deadline");

    const SyncReplicaOutboxLeaseState second =
        claim(first, 110U, "worker-b", 'b');
    require(second.dispatch_attempts == 2U &&
                second.worker_id == "worker-b" &&
                second.claim_id != first.claim_id,
            "reclaim did not fence the previous receipt");
    require_error(
        [&] {
            (void)anonsync::release_sync_replica_outbox_lease_or_throw(
                second, first.claim_id, 115U, 5U, "stale release");
        },
        "stale",
        "old claim released a replacement attempt");

    const SyncReplicaOutboxLeaseState released =
        anonsync::release_sync_replica_outbox_lease_or_throw(
            second, second.claim_id, 115U, 15U, "current release");
    require(released.dispatch_attempts == 2U &&
                released.claim_id.empty() &&
                released.worker_id.empty() &&
                released.claimed_at_epoch == 0U &&
                released.lease_expires_at_epoch == 0U &&
                released.retry_not_before_epoch == 130U &&
                released.retry_released_at_epoch == 115U &&
                released.retry_release_provenance ==
                    anonsync::SyncReplicaOutboxRetryReleaseProvenance::Exact,
            "release did not retain exact retry-minting provenance");
    require(!anonsync::sync_replica_outbox_lease_is_claimable_at_or_throw(
                released, 129U, "backed off release") &&
                anonsync::sync_replica_outbox_lease_is_claimable_at_or_throw(
                    released, 130U, "ready release"),
            "retry-not-before boundary was not exact");

    const SyncReplicaOutboxLeaseState repeated =
        claim(state, 100U, "worker-a", 'a');
    require(repeated == first,
            "pure claim token construction is not deterministic for fixed entropy");
    const SyncReplicaOutboxLeaseState different_entropy =
        claim(state, 100U, "worker-a", 'z');
    require(different_entropy.claim_id != first.claim_id,
            "claim token did not bind CSPRNG entropy");
}

void test_renewal_and_expiry_revoke_receipt_authority() {
    const SyncReplicaOutboxLeaseState claimed =
        claim({}, 100U, "worker-heartbeat", 'h');
    require(
        anonsync::sync_replica_outbox_claim_status_at_or_throw(
            claimed, claimed.claim_id, 109U, "live receipt") ==
            anonsync::SyncReplicaOutboxClaimStatus::Current,
        "current receipt was not live before its exact deadline");
    require(
        anonsync::sync_replica_outbox_claim_status_at_or_throw(
            claimed, claimed.claim_id, 110U, "expired receipt") ==
            anonsync::SyncReplicaOutboxClaimStatus::Expired,
        "receipt remained authoritative at its expiry boundary");
    require(
        anonsync::sync_replica_outbox_claim_status_at_or_throw(
            claimed, anonsync::sha256_hex("different receipt"), 101U,
            "stale receipt") ==
            anonsync::SyncReplicaOutboxClaimStatus::Stale,
        "different receipt was not classified as stale");

    const SyncReplicaOutboxLeaseState renewed =
        anonsync::renew_sync_replica_outbox_lease_or_throw(
            claimed, claimed.claim_id, 105U, 10U, "heartbeat renewal");
    require(renewed.claim_id == claimed.claim_id &&
                renewed.worker_id == claimed.worker_id &&
                renewed.dispatch_attempts == claimed.dispatch_attempts &&
                renewed.claimed_at_epoch == claimed.claimed_at_epoch &&
                renewed.lease_expires_at_epoch == 115U,
            "heartbeat changed attempt identity or failed to extend the deadline");
    const SyncReplicaOutboxLeaseState already_covered =
        anonsync::renew_sync_replica_outbox_lease_or_throw(
            renewed, renewed.claim_id, 106U, 5U,
            "already-covered heartbeat");
    require(already_covered == renewed,
            "heartbeat shortened or rewrote an already-covered lease");

    require_error(
        [&] {
            (void)anonsync::renew_sync_replica_outbox_lease_or_throw(
                claimed, claimed.claim_id, 110U, 10U,
                "expired heartbeat");
        },
        "expired",
        "expired receipt renewed its former attempt");
    require_error(
        [&] {
            (void)anonsync::release_sync_replica_outbox_lease_or_throw(
                claimed, claimed.claim_id, 110U, 10U,
                "expired retry release");
        },
        "expired",
        "expired receipt installed retry policy");
    require_error(
        [&] {
            (void)anonsync::renew_sync_replica_outbox_lease_or_throw(
                claimed, claimed.claim_id, 109U,
                anonsync::kSyncReplicaOutboxMaxLeaseSeconds,
                "cumulative lifetime overflow");
        },
        "cumulative",
        "heartbeat exceeded the cumulative claim lifetime budget");
    const SyncReplicaOutboxLeaseState immediate =
        anonsync::release_sync_replica_outbox_lease_or_throw(
            claimed, claimed.claim_id, 105U, 0U,
            "immediate relative retry");
    require(immediate.retry_not_before_epoch == 105U &&
                immediate.retry_released_at_epoch == 105U &&
                immediate.retry_release_provenance ==
                    anonsync::SyncReplicaOutboxRetryReleaseProvenance::Exact,
            "zero relative retry did not retain its exact minting observation");
    require_error(
        [&] {
            (void)anonsync::release_sync_replica_outbox_lease_or_throw(
                claimed, claimed.claim_id, 105U,
                anonsync::kSyncReplicaOutboxMaxRetryDelaySeconds + 1U,
                "unbounded retry delay");
        },
        "fixed retry budget",
        "retry release accepted an unbounded liveness delay");
    require_error(
        [&] {
            (void)anonsync::sync_replica_outbox_claim_status_at_or_throw(
                claimed, claimed.claim_id, 99U, "clock rollback");
        },
        "predates",
        "current receipt accepted a clock observation before its claim");
}

void test_invalid_and_overflow_states_fail_closed() {
    SyncReplicaOutboxLeaseState partial;
    partial.claim_id = anonsync::sha256_hex("claim");
    require_error(
        [&] {
            anonsync::validate_sync_replica_outbox_lease_state_or_throw(
                partial, "partial state");
        },
        "partial",
        "partial claim metadata was accepted");

    SyncReplicaOutboxLeaseState zero_duration = claim(
        {}, 100U, "worker-a", 'd');
    zero_duration.lease_expires_at_epoch = zero_duration.claimed_at_epoch;
    require_error(
        [&] {
            anonsync::validate_sync_replica_outbox_lease_state_or_throw(
                zero_duration, "zero duration");
        },
        "invalid active",
        "persisted zero-duration lease was accepted as reachable state");

    SyncReplicaOutboxLeaseState overlong_lifetime = claim(
        {}, 100U, "worker-a", 'l');
    overlong_lifetime.lease_expires_at_epoch =
        overlong_lifetime.claimed_at_epoch +
        anonsync::kSyncReplicaOutboxMaxClaimLifetimeSeconds + 1U;
    require_error(
        [&] {
            anonsync::validate_sync_replica_outbox_lease_state_or_throw(
                overlong_lifetime, "overlong lifetime");
        },
        "cumulative claim lifetime",
        "persisted claim exceeded the cumulative lifetime policy");

    SyncReplicaOutboxLeaseState active_backoff = claim(
        {}, 100U, "worker-a", 'q');
    active_backoff.retry_not_before_epoch = 111U;
    require_error(
        [&] {
            anonsync::validate_sync_replica_outbox_lease_state_or_throw(
                active_backoff, "active backoff");
        },
        "invalid active",
        "active claim accepted a simultaneous retry backoff");

    SyncReplicaOutboxLeaseState never_dispatched;
    never_dispatched.retry_not_before_epoch = 1U;
    never_dispatched.retry_released_at_epoch = 1U;
    never_dispatched.retry_release_provenance =
        anonsync::SyncReplicaOutboxRetryReleaseProvenance::Exact;
    require_error(
        [&] {
            anonsync::validate_sync_replica_outbox_lease_state_or_throw(
                never_dispatched, "never dispatched");
        },
        "never been dispatched",
        "backoff was accepted without a prior attempt");

    SyncReplicaOutboxLeaseState unreachable_inactive;
    unreachable_inactive.dispatch_attempts = 1U;
    require_error(
        [&] {
            anonsync::validate_sync_replica_outbox_lease_state_or_throw(
                unreachable_inactive, "unreachable inactive");
        },
        "without active or retry authority",
        "dispatched history was accepted without a claim or retry fence");

    SyncReplicaOutboxLeaseState missing_provenance;
    missing_provenance.dispatch_attempts = 1U;
    missing_provenance.retry_not_before_epoch = 120U;
    require_error(
        [&] {
            anonsync::validate_sync_replica_outbox_lease_state_or_throw(
                missing_provenance, "missing retry provenance");
        },
        "without release provenance",
        "retry schedule without provenance was accepted");

    SyncReplicaOutboxLeaseState fabricated_legacy;
    fabricated_legacy.dispatch_attempts = 1U;
    fabricated_legacy.retry_not_before_epoch = 120U;
    fabricated_legacy.retry_released_at_epoch = 100U;
    fabricated_legacy.retry_release_provenance =
        anonsync::SyncReplicaOutboxRetryReleaseProvenance::LegacyUnproven;
    require_error(
        [&] {
            anonsync::validate_sync_replica_outbox_lease_state_or_throw(
                fabricated_legacy, "fabricated legacy provenance");
        },
        "fabricates",
        "legacy migration marker accepted a guessed release epoch");

    SyncReplicaOutboxLeaseState overlong_exact;
    overlong_exact.dispatch_attempts = 1U;
    overlong_exact.retry_released_at_epoch = 100U;
    overlong_exact.retry_not_before_epoch =
        100U + anonsync::kSyncReplicaOutboxMaxRetryDelaySeconds + 1U;
    overlong_exact.retry_release_provenance =
        anonsync::SyncReplicaOutboxRetryReleaseProvenance::Exact;
    require_error(
        [&] {
            anonsync::validate_sync_replica_outbox_lease_state_or_throw(
                overlong_exact, "overlong exact retry");
        },
        "fixed retry budget",
        "persisted exact retry exceeded the fixed delay budget");

    SyncReplicaOutboxLeaseState legacy_unproven;
    legacy_unproven.dispatch_attempts = 1U;
    legacy_unproven.retry_not_before_epoch = 120U;
    legacy_unproven.retry_release_provenance =
        anonsync::SyncReplicaOutboxRetryReleaseProvenance::LegacyUnproven;
    anonsync::validate_sync_replica_outbox_lease_state_or_throw(
        legacy_unproven, "honest legacy retry provenance");
    require(!anonsync::sync_replica_outbox_lease_is_claimable_at_or_throw(
                legacy_unproven, 119U, "legacy retry blocked") &&
                anonsync::sync_replica_outbox_lease_is_claimable_at_or_throw(
                    legacy_unproven, 120U, "legacy retry ready"),
            "legacy provenance did not preserve its exact retained deadline");

    SyncReplicaOutboxLeaseState exhausted =
        claim({}, 100U, "worker-a", 'e');
    exhausted.dispatch_attempts = std::numeric_limits<std::uint64_t>::max();
    require_error(
        [&] { (void)claim(exhausted, 110U, "worker-a", 'f'); },
        "exhausted",
        "dispatch counter overflow was not rejected");

    require_error(
        [&] {
            (void)anonsync::claim_sync_replica_outbox_lease_or_throw(
                {}, "folder-lease-policy", "device-lease-peer",
                anonsync::sha256_hex("operation"), 7U,
                anonsync::sha256_hex("cutpoint"), "worker-a", 100U, 10U,
                std::string(31U, 'x'), "short entropy");
        },
        "32 bytes",
        "short claim entropy was accepted");
    require_error(
        [&] {
            (void)anonsync::claim_sync_replica_outbox_lease_or_throw(
                {}, "folder-lease-policy", "device-lease-peer",
                anonsync::sha256_hex("operation"), 7U,
                anonsync::sha256_hex("cutpoint"), "INVALID WORKER", 100U,
                10U, std::string(32U, 'x'), "invalid worker");
        },
        "worker identity",
        "invalid worker identity was accepted");
    require_error(
        [&] {
            (void)anonsync::claim_sync_replica_outbox_lease_or_throw(
                {}, "folder-lease-policy", "device-lease-peer",
                anonsync::sha256_hex("operation"), 7U,
                anonsync::sha256_hex("cutpoint"), "worker-a",
                std::numeric_limits<std::uint64_t>::max() - 5U, 10U,
                std::string(32U, 'x'), "deadline overflow");
        },
        "overflows",
        "lease deadline overflow was accepted");
    require_error(
        [&] {
            const SyncReplicaOutboxLeaseState near_max =
                claim({}, std::numeric_limits<std::uint64_t>::max() - 20U,
                      "worker-overflow", 'o');
            (void)anonsync::release_sync_replica_outbox_lease_or_throw(
                near_max, near_max.claim_id,
                std::numeric_limits<std::uint64_t>::max() - 15U, 20U,
                "retry deadline overflow");
        },
        "overflows",
        "relative retry deadline overflow was accepted");
    require_error(
        [&] {
            (void)anonsync::sync_replica_outbox_lease_is_claimable_at_or_throw(
                {}, 0U, "zero now");
        },
        "positive",
        "zero claim clock was accepted");
}

}  // namespace

int main() {
    try {
        test_claim_expiry_reclaim_and_release();
        test_renewal_and_expiry_revoke_receipt_authority();
        test_invalid_and_overflow_states_fail_closed();
        std::cout << "sync replica outbox lease tests passed: "
                  << checks << " checks\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sync replica outbox lease tests failed after "
                  << checks << " checks: " << error.what() << '\n';
        return 1;
    }
}
