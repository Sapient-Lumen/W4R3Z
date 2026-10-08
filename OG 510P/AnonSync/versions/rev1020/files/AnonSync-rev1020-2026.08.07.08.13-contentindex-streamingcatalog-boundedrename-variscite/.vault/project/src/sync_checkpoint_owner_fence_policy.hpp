#pragma once

#include "anonsync_sync_checkpoint_owner_fence.hpp"

#include <cstdint>
#include <string>

namespace anonsync::sync_checkpoint_owner_fence_policy {

struct StoredOwnerLockEvidence final {
    bool present = false;
    std::string session_id;
    std::string daemon_id;
    std::string worker_id;
    std::string owner_lock_id;
    std::uint64_t owner_lock_epoch = 0;
    std::uint64_t acquired_at_epoch = 0;
    std::uint64_t expires_at_epoch = 0;
    std::uint64_t released_at_epoch = 0;
    std::uint64_t updated_at_epoch = 0;
    std::string lock_state;
    bool owner_lock_id_is_canonical = false;
};

// Sticky ownership lives outside the checkpoint root's foreign-key cascade.
// A mode row means that this session has crossed the ownership boundary at
// least once.  `owner-required` remains in force across release and root reset;
// `administratively-disabled` is a separately evidenced escape hatch whose
// production transition is intentionally not exposed by this policy module.
struct StoredOwnerModeEvidence final {
    bool present = false;
    std::string session_id;
    std::string ownership_mode;
    std::uint64_t latest_owner_lock_epoch = 0;
    std::uint64_t mode_updated_at_epoch = 0;
    std::string administrative_disable_evidence_id;
};

struct AcquisitionRequest final {
    std::string session_id;
    std::string daemon_id;
    std::string worker_id;
    std::uint64_t acquired_at_epoch = 0;
    std::uint64_t owner_lock_seconds = 0;
};

struct AcquisitionDecision final {
    bool allowed = false;
    std::string reason;
    std::uint64_t owner_lock_epoch = 0;
    std::uint64_t expires_at_epoch = 0;
    bool reclaimed_expired = false;
    bool reactivated_administratively_disabled_mode = false;
};

struct RecipientRequest final {
    std::string session_id;
    std::uint64_t observed_at_epoch = 0;
    SyncSessionCheckpointDaemonOwnerCapability capability;
};

struct RecipientDecision final {
    bool allowed = false;
    std::string reason;
    bool owner_capability_required = false;
};

[[nodiscard]] bool capability_is_empty(
    const SyncSessionCheckpointDaemonOwnerCapability& capability) noexcept;

[[nodiscard]] bool capability_is_complete(
    const SyncSessionCheckpointDaemonOwnerCapability& capability) noexcept;

[[nodiscard]] AcquisitionDecision plan_acquisition(
    const StoredOwnerModeEvidence& mode,
    const StoredOwnerLockEvidence& stored,
    const AcquisitionRequest& request);

[[nodiscard]] RecipientDecision authorize_recipient(
    const StoredOwnerModeEvidence& mode,
    const StoredOwnerLockEvidence& stored,
    const RecipientRequest& request);

}  // namespace anonsync::sync_checkpoint_owner_fence_policy
