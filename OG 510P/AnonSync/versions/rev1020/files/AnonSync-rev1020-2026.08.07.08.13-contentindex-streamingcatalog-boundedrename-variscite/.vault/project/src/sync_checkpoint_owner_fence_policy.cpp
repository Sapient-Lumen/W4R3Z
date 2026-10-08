#include "sync_checkpoint_owner_fence_policy.hpp"

#include <algorithm>
#include <limits>
#include <string_view>
#include <utility>

namespace anonsync::sync_checkpoint_owner_fence_policy {
namespace {

constexpr std::uint64_t kMaxDurableSqliteInteger =
    static_cast<std::uint64_t>(std::numeric_limits<std::int64_t>::max());
constexpr std::string_view kOwnerRequiredMode = "owner-required";
constexpr std::string_view kAdministrativelyDisabledMode =
    "administratively-disabled";

bool ascii_lower_alnum(char c) noexcept {
    return (c >= 'a' && c <= 'z') || (c >= '0' && c <= '9');
}

bool portable_sync_id(std::string_view value) noexcept {
    if (value.empty() || value.size() > 128) return false;
    if (!ascii_lower_alnum(value.front()) ||
        !ascii_lower_alnum(value.back())) {
        return false;
    }
    return std::all_of(value.begin(), value.end(), [](char c) {
        return ascii_lower_alnum(c) || c == '.' || c == '_' || c == '-';
    });
}

bool lowercase_sha256(std::string_view value) noexcept {
    return value.size() == 64 &&
           std::all_of(value.begin(), value.end(), [](char c) {
               return (c >= '0' && c <= '9') ||
                      (c >= 'a' && c <= 'f');
           });
}

bool owner_lock_id_shape(std::string_view value) noexcept {
    constexpr std::string_view prefix =
        "sync-resume-daemon-owner-lock:v1:";
    return value.starts_with(prefix) &&
           lowercase_sha256(value.substr(prefix.size()));
}

bool administrative_disable_evidence_id_shape(
    std::string_view value) noexcept {
    constexpr std::string_view prefix =
        "sync-checkpoint-owner-admin-disable:v1:";
    return value.starts_with(prefix) &&
           lowercase_sha256(value.substr(prefix.size()));
}

std::string validate_stored_evidence(
    const StoredOwnerLockEvidence& stored) {
    if (!stored.present) return {};
    if (!portable_sync_id(stored.session_id) ||
        !portable_sync_id(stored.daemon_id) ||
        !portable_sync_id(stored.worker_id)) {
        return "stored owner row contains a non-portable identity";
    }
    if (stored.owner_lock_epoch == 0) {
        return "stored owner generation is zero";
    }
    if (stored.owner_lock_epoch > kMaxDurableSqliteInteger ||
        stored.acquired_at_epoch > kMaxDurableSqliteInteger ||
        stored.expires_at_epoch > kMaxDurableSqliteInteger ||
        stored.released_at_epoch > kMaxDurableSqliteInteger ||
        stored.updated_at_epoch > kMaxDurableSqliteInteger) {
        return "stored owner row exceeds SQLite signed integer range";
    }
    if (!owner_lock_id_shape(stored.owner_lock_id)) {
        return "stored owner lock id has the wrong namespace or digest shape";
    }
    if (!stored.owner_lock_id_is_canonical) {
        return "stored owner lock id does not bind its row identities and generation";
    }
    if (stored.acquired_at_epoch == 0 ||
        stored.expires_at_epoch <= stored.acquired_at_epoch) {
        return "stored owner lease geometry is malformed";
    }
    if (stored.updated_at_epoch < stored.acquired_at_epoch) {
        return "stored owner update time predates acquisition";
    }
    if (stored.lock_state == "held") {
        if (stored.released_at_epoch != 0) {
            return "stored held owner row also carries release evidence";
        }
        return {};
    }
    if (stored.lock_state == "released") {
        if (stored.released_at_epoch < stored.acquired_at_epoch ||
            stored.updated_at_epoch < stored.released_at_epoch) {
            return "stored released owner row has malformed release geometry";
        }
        return {};
    }
    return "stored owner row has an unsupported lock state";
}

std::string validate_mode_evidence(const StoredOwnerModeEvidence& mode) {
    if (!mode.present) return {};
    if (!portable_sync_id(mode.session_id)) {
        return "stored owner mode row contains a non-portable session identity";
    }
    if (mode.latest_owner_lock_epoch == 0) {
        return "stored owner mode latest generation is zero";
    }
    if (mode.latest_owner_lock_epoch > kMaxDurableSqliteInteger ||
        mode.mode_updated_at_epoch == 0 ||
        mode.mode_updated_at_epoch > kMaxDurableSqliteInteger) {
        return "stored owner mode row exceeds SQLite signed integer range";
    }
    if (mode.ownership_mode == kOwnerRequiredMode) {
        if (!mode.administrative_disable_evidence_id.empty()) {
            return "owner-required mode carries administrative-disable evidence";
        }
        return {};
    }
    if (mode.ownership_mode == kAdministrativelyDisabledMode) {
        if (!administrative_disable_evidence_id_shape(
                mode.administrative_disable_evidence_id)) {
            return "administratively-disabled mode lacks canonical disable evidence";
        }
        return {};
    }
    return "stored owner mode row has an unsupported ownership mode";
}

std::string validate_combined_evidence(
    const StoredOwnerModeEvidence& mode,
    const StoredOwnerLockEvidence& stored) {
    if (const std::string error = validate_mode_evidence(mode); !error.empty()) {
        return error;
    }
    if (const std::string error = validate_stored_evidence(stored);
        !error.empty()) {
        return error;
    }
    if (!mode.present || !stored.present) return {};
    if (mode.session_id != stored.session_id) {
        return "owner mode and owner row belong to different sessions";
    }
    if (mode.latest_owner_lock_epoch != stored.owner_lock_epoch) {
        return "owner mode latest generation does not match the durable owner row";
    }
    if (mode.ownership_mode == kAdministrativelyDisabledMode &&
        stored.lock_state == "held") {
        return "administratively-disabled mode contradicts a held owner row";
    }
    return {};
}

RecipientDecision recipient_failure(std::string reason,
                                    bool required = false) {
    RecipientDecision out;
    out.reason = std::move(reason);
    out.owner_capability_required = required;
    return out;
}

}  // namespace

bool capability_is_empty(
    const SyncSessionCheckpointDaemonOwnerCapability& capability) noexcept {
    return capability.session_id.empty() && capability.daemon_id.empty() &&
           capability.worker_id.empty() && capability.owner_lock_id.empty() &&
           capability.owner_lock_epoch == 0;
}

bool capability_is_complete(
    const SyncSessionCheckpointDaemonOwnerCapability& capability) noexcept {
    return !capability.session_id.empty() && !capability.daemon_id.empty() &&
           !capability.worker_id.empty() && !capability.owner_lock_id.empty() &&
           capability.owner_lock_epoch != 0;
}

AcquisitionDecision plan_acquisition(
    const StoredOwnerModeEvidence& mode,
    const StoredOwnerLockEvidence& stored,
    const AcquisitionRequest& request) {
    AcquisitionDecision out;
    if (!portable_sync_id(request.session_id) ||
        !portable_sync_id(request.daemon_id) ||
        !portable_sync_id(request.worker_id)) {
        out.reason = "acquisition identities are not lowercase portable sync ids";
        return out;
    }
    if (request.acquired_at_epoch == 0) {
        out.reason = "acquisition time is zero";
        return out;
    }
    if (request.owner_lock_seconds == 0) {
        out.reason = "owner lease duration is zero";
        return out;
    }
    if (request.acquired_at_epoch > kMaxDurableSqliteInteger ||
        request.owner_lock_seconds > kMaxDurableSqliteInteger ||
        request.owner_lock_seconds >
            kMaxDurableSqliteInteger - request.acquired_at_epoch) {
        out.reason = "owner lease expiration exceeds SQLite signed integer range";
        return out;
    }
    out.expires_at_epoch =
        request.acquired_at_epoch + request.owner_lock_seconds;

    if (const std::string error = validate_combined_evidence(mode, stored);
        !error.empty()) {
        out.reason = error;
        return out;
    }
    if (mode.present && mode.session_id != request.session_id) {
        out.reason = "stored owner mode row belongs to another session";
        return out;
    }
    if (stored.present && stored.session_id != request.session_id) {
        out.reason = "stored owner row belongs to another session";
        return out;
    }
    if (mode.present &&
        request.acquired_at_epoch < mode.mode_updated_at_epoch) {
        out.reason = "acquisition clock regressed behind durable owner mode evidence";
        return out;
    }
    if (stored.present &&
        (request.acquired_at_epoch < stored.acquired_at_epoch ||
         (stored.lock_state == "released" &&
          request.acquired_at_epoch < stored.released_at_epoch))) {
        out.reason = "acquisition clock regressed behind durable owner evidence";
        return out;
    }
    if (stored.present && stored.lock_state == "held" &&
        request.acquired_at_epoch < stored.expires_at_epoch) {
        out.reason = "owner lock is still live";
        return out;
    }

    std::uint64_t latest_generation = 0;
    if (mode.present) {
        latest_generation = mode.latest_owner_lock_epoch;
    } else if (stored.present) {
        // Deterministic legacy migration: the pre-sticky owner row is already
        // proof that the session crossed the ownership boundary.
        latest_generation = stored.owner_lock_epoch;
    }
    if (latest_generation == kMaxDurableSqliteInteger) {
        out.reason = "owner generation is exhausted";
        return out;
    }

    out.allowed = true;
    out.owner_lock_epoch = latest_generation + 1;
    out.reclaimed_expired = stored.present && stored.lock_state == "held" &&
                            request.acquired_at_epoch >=
                                stored.expires_at_epoch;
    out.reactivated_administratively_disabled_mode =
        mode.present && mode.ownership_mode == kAdministrativelyDisabledMode;
    return out;
}

RecipientDecision authorize_recipient(
    const StoredOwnerModeEvidence& mode,
    const StoredOwnerLockEvidence& stored,
    const RecipientRequest& request) {
    if (!portable_sync_id(request.session_id)) {
        return recipient_failure(
            "recipient session id is not a lowercase portable sync id");
    }
    if (request.observed_at_epoch == 0) {
        return recipient_failure("recipient observation time is zero");
    }
    if (request.observed_at_epoch > kMaxDurableSqliteInteger) {
        return recipient_failure(
            "recipient observation time exceeds SQLite signed integer range");
    }
    if (!capability_is_empty(request.capability) &&
        !capability_is_complete(request.capability)) {
        return recipient_failure(
            "presented owner capability is only partially populated", true);
    }

    if (const std::string error = validate_combined_evidence(mode, stored);
        !error.empty()) {
        return recipient_failure(error, mode.present || stored.present);
    }
    if (mode.present && mode.session_id != request.session_id) {
        return recipient_failure(
            "durable owner mode row belongs to another session", true);
    }
    if (stored.present && stored.session_id != request.session_id) {
        return recipient_failure(
            "durable owner row belongs to another session", true);
    }
    if (mode.present && request.observed_at_epoch < mode.mode_updated_at_epoch) {
        return recipient_failure(
            "recipient clock regressed behind owner mode evidence", true);
    }

    if (mode.present &&
        mode.ownership_mode == kAdministrativelyDisabledMode) {
        if (!capability_is_empty(request.capability)) {
            return recipient_failure(
                "owner capability was presented after administrative disable");
        }
        return {true, "", false};
    }

    if (!stored.present) {
        if (mode.present) {
            return recipient_failure(
                "sticky owner mode has no live durable generation; acquire a successor before mutation",
                true);
        }
        if (!capability_is_empty(request.capability)) {
            return recipient_failure(
                "owner capability was presented but no durable owner row exists");
        }
        return {true, "", false};
    }

    // A legacy owner row without a mode row is still sticky: durable evidence
    // that ownership once existed must not be laundered into unowned mutation.
    if (stored.lock_state == "released") {
        if (!capability_is_empty(request.capability)) {
            return recipient_failure(
                "released owner generation cannot authorize a mutation", true);
        }
        return recipient_failure(
            "sticky owner mode remains required after release; acquire a successor before mutation",
            true);
    }

    if (request.observed_at_epoch < stored.acquired_at_epoch) {
        return recipient_failure(
            "recipient clock regressed behind owner acquisition", true);
    }
    if (request.observed_at_epoch >= stored.expires_at_epoch) {
        return recipient_failure(
            "durable owner generation is expired and must be replaced before mutation",
            true);
    }
    if (!capability_is_complete(request.capability)) {
        return recipient_failure(
            "live durable owner row requires its exact capability", true);
    }
    if (request.capability.session_id != request.session_id ||
        request.capability.session_id != stored.session_id) {
        return recipient_failure(
            "presented owner capability session does not match the recipient",
            true);
    }
    if (request.capability.daemon_id != stored.daemon_id ||
        request.capability.worker_id != stored.worker_id ||
        request.capability.owner_lock_id != stored.owner_lock_id ||
        request.capability.owner_lock_epoch != stored.owner_lock_epoch) {
        return recipient_failure(
            "presented owner capability does not match the live durable generation",
            true);
    }
    if (!portable_sync_id(request.capability.daemon_id) ||
        !portable_sync_id(request.capability.worker_id) ||
        !owner_lock_id_shape(request.capability.owner_lock_id)) {
        return recipient_failure(
            "presented owner capability is not canonical portable evidence",
            true);
    }
    return {true, "", true};
}

}  // namespace anonsync::sync_checkpoint_owner_fence_policy
