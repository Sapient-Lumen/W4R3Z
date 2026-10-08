#pragma once

#include <cstdint>
#include <string>

namespace anonsync {

// A serializable observation of one operating-system process incarnation.
// Unlike SyncProcessIncarnation, this is not process-local capability authority:
// it may cross a document boundary and can be forged by a writer.  Its purpose
// is to distinguish PID reuse and reboot from the same observed process life.
struct SyncProcessIdentityObservation final {
    std::string format;
    std::uint64_t process_id = 0;
    std::string boot_id;
    std::string start_token;

    friend bool operator==(const SyncProcessIdentityObservation&,
                           const SyncProcessIdentityObservation&) = default;
};

enum class SyncProcessIdentityMatchKind {
    Match,
    NotRunning,
    Mismatch,
    Unsupported,
    Indeterminate,
    Invalid,
};

struct SyncProcessIdentityMatch final {
    SyncProcessIdentityMatchKind kind = SyncProcessIdentityMatchKind::Invalid;
    bool verification_available = false;
    bool process_live = false;
    bool exact_match = false;
    std::string reason;
};

// Validates canonical interchange geometry.  This proves only that the fields
// form one supported observation, not that the named process is live.
void validate_sync_process_identity_observation_or_throw(
    const SyncProcessIdentityObservation& observation);

// Captures the current process using the strongest implemented local primitive:
// Linux boot UUID + /proc starttime, or Windows process creation FILETIME.
// Other platforms return an explicit unavailable observation rather than a PID
// masquerading as incarnation evidence.
[[nodiscard]] SyncProcessIdentityObservation
current_sync_process_identity_observation_or_throw();

// Re-observes the claimed local PID and classifies the relationship.  No result
// authorizes checkpoint mutation; Match is still only liveness evidence.
[[nodiscard]] SyncProcessIdentityMatch
check_sync_process_identity_observation_noexcept(
    const SyncProcessIdentityObservation& expected) noexcept;

[[nodiscard]] const char* sync_process_identity_match_kind_name(
    SyncProcessIdentityMatchKind kind) noexcept;

}  // namespace anonsync
