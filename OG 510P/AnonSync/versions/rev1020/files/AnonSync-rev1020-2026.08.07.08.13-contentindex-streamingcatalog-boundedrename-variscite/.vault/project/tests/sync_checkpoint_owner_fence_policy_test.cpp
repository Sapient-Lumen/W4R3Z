#include "sync_checkpoint_owner_fence_policy.hpp"

#include <cstdint>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>

namespace {

using anonsync::SyncSessionCheckpointDaemonOwnerCapability;
using anonsync::sync_checkpoint_owner_fence_policy::AcquisitionRequest;
using anonsync::sync_checkpoint_owner_fence_policy::RecipientRequest;
using anonsync::sync_checkpoint_owner_fence_policy::StoredOwnerLockEvidence;
using anonsync::sync_checkpoint_owner_fence_policy::StoredOwnerModeEvidence;

std::string owner_id(char digest = 'a') {
    return "sync-resume-daemon-owner-lock:v1:" + std::string(64, digest);
}

StoredOwnerLockEvidence held_owner(std::uint64_t generation = 7,
                                   std::uint64_t acquired = 100,
                                   std::uint64_t expires = 200) {
    StoredOwnerLockEvidence out;
    out.present = true;
    out.session_id = "session-a";
    out.daemon_id = "daemon-a";
    out.worker_id = "worker-a";
    out.owner_lock_id = owner_id();
    out.owner_lock_epoch = generation;
    out.acquired_at_epoch = acquired;
    out.expires_at_epoch = expires;
    out.updated_at_epoch = acquired;
    out.lock_state = "held";
    out.owner_lock_id_is_canonical = true;
    return out;
}

StoredOwnerModeEvidence required_mode(std::uint64_t generation = 7,
                                      std::uint64_t updated = 100) {
    StoredOwnerModeEvidence out;
    out.present = true;
    out.session_id = "session-a";
    out.ownership_mode = "owner-required";
    out.latest_owner_lock_epoch = generation;
    out.mode_updated_at_epoch = updated;
    return out;
}

StoredOwnerModeEvidence disabled_mode(std::uint64_t generation = 7,
                                      std::uint64_t updated = 250) {
    auto out = required_mode(generation, updated);
    out.ownership_mode = "administratively-disabled";
    out.administrative_disable_evidence_id =
        "sync-checkpoint-owner-admin-disable:v1:" + std::string(64, 'd');
    return out;
}

SyncSessionCheckpointDaemonOwnerCapability capability_for(
    const StoredOwnerLockEvidence& stored) {
    SyncSessionCheckpointDaemonOwnerCapability capability;
    capability.session_id = stored.session_id;
    capability.daemon_id = stored.daemon_id;
    capability.worker_id = stored.worker_id;
    capability.owner_lock_id = stored.owner_lock_id;
    capability.owner_lock_epoch = stored.owner_lock_epoch;
    return capability;
}

void require(bool condition,
             const std::string& message,
             std::uint64_t& checks) {
    ++checks;
    if (!condition) throw std::runtime_error(message);
}

void test_capability_geometry(std::uint64_t& checks) {
    using namespace anonsync::sync_checkpoint_owner_fence_policy;
    SyncSessionCheckpointDaemonOwnerCapability empty;
    require(capability_is_empty(empty) && !capability_is_complete(empty),
            "empty capability classification failed", checks);

    auto complete = capability_for(held_owner());
    require(!capability_is_empty(complete) && capability_is_complete(complete),
            "complete capability classification failed", checks);

    complete.owner_lock_id.clear();
    require(!capability_is_empty(complete) && !capability_is_complete(complete),
            "partial capability was laundered as empty or complete", checks);
}

void test_monotonic_acquisition(std::uint64_t& checks) {
    using namespace anonsync::sync_checkpoint_owner_fence_policy;
    AcquisitionRequest request;
    request.session_id = "session-a";
    request.daemon_id = "daemon-a";
    request.worker_id = "worker-a";
    request.acquired_at_epoch = 100;
    request.owner_lock_seconds = 50;

    const auto first = plan_acquisition({}, {}, request);
    require(first.allowed && first.owner_lock_epoch == 1 &&
                first.expires_at_epoch == 150 && !first.reclaimed_expired,
            "first owner acquisition did not mint generation one", checks);

    StoredOwnerLockEvidence released = held_owner(1, 100, 150);
    released.lock_state = "released";
    released.released_at_epoch = 120;
    released.updated_at_epoch = 120;
    request.acquired_at_epoch = 121;
    const auto second = plan_acquisition(required_mode(1, 120), released, request);
    require(second.allowed && second.owner_lock_epoch == 2 &&
                !second.reclaimed_expired,
            "released owner takeover did not increment sticky generation", checks);

    request.acquired_at_epoch = 160;
    const auto after_reset =
        plan_acquisition(required_mode(2, 150), {}, request);
    require(after_reset.allowed && after_reset.owner_lock_epoch == 3,
            "owner-row absence after reset reused or lost sticky generation", checks);

    request.acquired_at_epoch = 260;
    const auto reactivated =
        plan_acquisition(disabled_mode(9, 250), {}, request);
    require(reactivated.allowed && reactivated.owner_lock_epoch == 10 &&
                reactivated.reactivated_administratively_disabled_mode,
            "administratively disabled mode did not reactivate with a new generation",
            checks);

    StoredOwnerLockEvidence expired = held_owner(41, 100, 150);
    request.acquired_at_epoch = 150;
    const auto takeover =
        plan_acquisition(required_mode(41, 100), expired, request);
    require(takeover.allowed && takeover.owner_lock_epoch == 42 &&
                takeover.reclaimed_expired,
            "expired owner takeover did not increment generation", checks);

    request.acquired_at_epoch = 149;
    const auto live = plan_acquisition(required_mode(41, 100), expired, request);
    require(!live.allowed && live.reason.find("still live") != std::string::npos,
            "live owner was overwritten", checks);

    request.acquired_at_epoch = 99;
    const auto regressed =
        plan_acquisition(required_mode(41, 100), expired, request);
    require(!regressed.allowed &&
                regressed.reason.find("regressed") != std::string::npos,
            "acquisition clock regression was accepted", checks);

    auto mismatched_mode = required_mode(40, 100);
    request.acquired_at_epoch = 150;
    const auto mismatched = plan_acquisition(mismatched_mode, expired, request);
    require(!mismatched.allowed &&
                mismatched.reason.find("does not match") != std::string::npos,
            "mode/owner generation disagreement was accepted", checks);

    StoredOwnerModeEvidence exhausted = required_mode(
        static_cast<std::uint64_t>(std::numeric_limits<std::int64_t>::max()),
        100);
    request.acquired_at_epoch = 150;
    const auto overflow = plan_acquisition(exhausted, {}, request);
    require(!overflow.allowed &&
                overflow.reason.find("exhausted") != std::string::npos,
            "owner generation overflow was accepted", checks);

    request.acquired_at_epoch = static_cast<std::uint64_t>(
        std::numeric_limits<std::int64_t>::max());
    request.owner_lock_seconds = 1;
    const auto timestamp_range = plan_acquisition({}, {}, request);
    require(!timestamp_range.allowed &&
                timestamp_range.reason.find("SQLite signed integer range") !=
                    std::string::npos,
            "owner lease exceeded SQLite durable integer range", checks);
}

void test_recipient_authority(std::uint64_t& checks) {
    using namespace anonsync::sync_checkpoint_owner_fence_policy;
    RecipientRequest request;
    request.session_id = "session-a";
    request.observed_at_epoch = 150;

    const auto unlocked = authorize_recipient({}, {}, request);
    require(unlocked.allowed && !unlocked.owner_capability_required,
            "capability-free mutation before ownership was rejected", checks);

    request.observed_at_epoch =
        static_cast<std::uint64_t>(std::numeric_limits<std::int64_t>::max()) + 1;
    const auto out_of_range_observation = authorize_recipient({}, {}, request);
    require(!out_of_range_observation.allowed &&
                out_of_range_observation.reason.find(
                    "SQLite signed integer range") != std::string::npos,
            "recipient accepted an observation outside SQLite durable integer range",
            checks);
    request.observed_at_epoch = 150;

    request.capability = capability_for(held_owner());
    const auto invented = authorize_recipient({}, {}, request);
    require(!invented.allowed,
            "invented capability without durable owner row was accepted", checks);

    const StoredOwnerLockEvidence held = held_owner();
    const StoredOwnerModeEvidence mode = required_mode();
    request.capability = {};
    const auto missing = authorize_recipient(mode, held, request);
    require(!missing.allowed && missing.owner_capability_required,
            "live owner did not require a capability", checks);

    request.capability = capability_for(held);
    const auto exact = authorize_recipient(mode, held, request);
    require(exact.allowed && exact.owner_capability_required,
            "exact live owner capability was rejected", checks);

    auto stale = request.capability;
    --stale.owner_lock_epoch;
    request.capability = stale;
    const auto stale_generation = authorize_recipient(mode, held, request);
    require(!stale_generation.allowed &&
                stale_generation.reason.find("does not match") !=
                    std::string::npos,
            "stale owner generation was accepted", checks);

    request.capability = capability_for(held);
    request.capability.daemon_id = "daemon-b";
    require(!authorize_recipient(mode, held, request).allowed,
            "wrong daemon identity was accepted", checks);
    request.capability = capability_for(held);
    request.capability.worker_id = "worker-b";
    require(!authorize_recipient(mode, held, request).allowed,
            "wrong worker identity was accepted", checks);
    request.capability = capability_for(held);
    request.capability.owner_lock_id = owner_id('b');
    require(!authorize_recipient(mode, held, request).allowed,
            "wrong owner lock id was accepted", checks);
    request.capability = capability_for(held);
    request.capability.session_id = "session-b";
    require(!authorize_recipient(mode, held, request).allowed,
            "cross-session owner capability was accepted", checks);

    request.capability = capability_for(held);
    request.observed_at_epoch = held.expires_at_epoch;
    const auto expired = authorize_recipient(mode, held, request);
    require(!expired.allowed && expired.reason.find("expired") != std::string::npos,
            "expired owner capability authorized a mutation", checks);

    StoredOwnerLockEvidence released = held;
    released.lock_state = "released";
    released.released_at_epoch = 160;
    released.updated_at_epoch = 160;
    request.observed_at_epoch = 161;
    request.capability = {};
    require(!authorize_recipient(required_mode(7, 160), released, request).allowed,
            "release erased sticky ownership", checks);
    require(!authorize_recipient({}, released, request).allowed,
            "legacy released owner row was laundered into unowned mode", checks);

    request.capability = capability_for(released);
    require(!authorize_recipient(required_mode(7, 160), released, request).allowed,
            "released capability authorized a mutation", checks);

    request.capability = {};
    require(!authorize_recipient(required_mode(7, 170), {}, request).allowed,
            "root-reset owner gap admitted an empty capability", checks);

    request.observed_at_epoch = 260;
    require(authorize_recipient(disabled_mode(), {}, request).allowed,
            "administratively disabled mode did not admit empty capability", checks);
    request.capability = capability_for(held);
    require(!authorize_recipient(disabled_mode(), {}, request).allowed,
            "administratively disabled mode accepted an owner capability", checks);
}

void test_hostile_durable_rows(std::uint64_t& checks) {
    using namespace anonsync::sync_checkpoint_owner_fence_policy;
    AcquisitionRequest acquisition{
        "session-a", "daemon-b", "worker-b", 250, 10};
    RecipientRequest recipient;
    recipient.session_id = "session-a";
    recipient.observed_at_epoch = 150;
    recipient.capability = capability_for(held_owner());

    StoredOwnerLockEvidence malformed = held_owner();
    malformed.owner_lock_id_is_canonical = false;
    require(!plan_acquisition(required_mode(), malformed, acquisition).allowed &&
                !authorize_recipient(required_mode(), malformed, recipient).allowed,
            "noncanonical owner id was accepted", checks);

    malformed = held_owner();
    malformed.lock_state = "held";
    malformed.released_at_epoch = 101;
    require(!plan_acquisition(required_mode(), malformed, acquisition).allowed &&
                !authorize_recipient(required_mode(), malformed, recipient).allowed,
            "held/released contradiction was accepted", checks);

    malformed = held_owner();
    malformed.expires_at_epoch = malformed.acquired_at_epoch;
    require(!plan_acquisition(required_mode(), malformed, acquisition).allowed &&
                !authorize_recipient(required_mode(), malformed, recipient).allowed,
            "zero-width owner lease was accepted", checks);

    malformed = held_owner();
    malformed.lock_state = "unknown";
    require(!plan_acquisition(required_mode(), malformed, acquisition).allowed &&
                !authorize_recipient(required_mode(), malformed, recipient).allowed,
            "unknown owner state was accepted", checks);

    malformed = held_owner();
    malformed.owner_lock_epoch = static_cast<std::uint64_t>(
        std::numeric_limits<std::int64_t>::max()) + 1;
    require(!plan_acquisition(required_mode(), malformed, acquisition).allowed &&
                !authorize_recipient(required_mode(), malformed, recipient).allowed,
            "out-of-range durable owner integer was accepted", checks);

    auto malformed_mode = required_mode();
    malformed_mode.administrative_disable_evidence_id = "forged";
    require(!plan_acquisition(malformed_mode, held_owner(), acquisition).allowed &&
                !authorize_recipient(malformed_mode, held_owner(), recipient).allowed,
            "owner-required mode accepted disable evidence", checks);

    malformed_mode = disabled_mode();
    malformed_mode.administrative_disable_evidence_id = "forged";
    require(!plan_acquisition(malformed_mode, {}, acquisition).allowed &&
                !authorize_recipient(malformed_mode, {}, recipient).allowed,
            "disabled mode accepted noncanonical administrative evidence", checks);

    require(!authorize_recipient(disabled_mode(), held_owner(), recipient).allowed,
            "disabled mode contradicted by held owner row was accepted", checks);

    recipient.capability = capability_for(held_owner());
    recipient.capability.owner_lock_id.clear();
    require(!authorize_recipient(required_mode(), held_owner(), recipient).allowed,
            "partial owner capability was accepted", checks);
}

}  // namespace

int main() {
    std::uint64_t checks = 0;
    try {
        test_capability_geometry(checks);
        test_monotonic_acquisition(checks);
        test_recipient_authority(checks);
        test_hostile_durable_rows(checks);
        std::cout << "sync checkpoint owner fence policy checks: "
                  << checks << "/" << checks << " passed\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sync checkpoint owner fence policy failed after "
                  << checks << " checks: " << error.what() << '\n';
        return 1;
    }
}
