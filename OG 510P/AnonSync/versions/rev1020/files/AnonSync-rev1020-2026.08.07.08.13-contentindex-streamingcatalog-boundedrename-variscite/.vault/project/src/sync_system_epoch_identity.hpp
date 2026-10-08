#pragma once

#include <cstdint>
#include <string>
#include <string_view>

namespace anonsync {

// Exact observation source used to distinguish one running-kernel epoch. This
// is evidence, not a secret and not authority by itself. Linux may hide the
// procfs source; that absence is preserved as a typed observation rather than
// being confused with a boot UUID or inferred from a kernel version.
enum class SyncSystemBootIdentityKind : std::uint8_t {
    Unsupported = 0,
    LinuxProcBootId = 1,
    LinuxProcBootIdMissing = 2,
    LinuxProcBootIdPermissionDenied = 3,
};

struct SyncSystemBootIdentityObservation final {
    SyncSystemBootIdentityKind kind =
        SyncSystemBootIdentityKind::Unsupported;
    std::string boot_id;

    bool operator==(const SyncSystemBootIdentityObservation&) const = default;
};

enum class SyncSystemBootIdentityProbeDisposition : std::uint8_t {
    Available = 0,
    Missing = 1,
    PermissionDenied = 2,
    Fatal = 3,
};

[[nodiscard]] SyncSystemBootIdentityProbeDisposition
sync_system_classify_boot_identity_open_result(
    int open_result,
    int error_number) noexcept;

[[nodiscard]] bool sync_system_boot_id_is_canonical(
    std::string_view value) noexcept;
// Accept exactly one canonical lowercase UUID, optionally followed by one LF
// or one CRLF. No whitespace trimming or repeated terminators are permitted.
[[nodiscard]] std::string sync_system_parse_boot_id_text_or_throw(
    std::string_view bytes,
    std::string_view label = "system boot identity");
[[nodiscard]] const char* sync_system_boot_identity_kind_name(
    SyncSystemBootIdentityKind kind) noexcept;
[[nodiscard]] SyncSystemBootIdentityKind
sync_system_boot_identity_kind_from_name_or_throw(
    std::string_view name,
    std::string_view label);
void validate_sync_system_boot_identity_observation_or_throw(
    const SyncSystemBootIdentityObservation& observation,
    std::string_view label = "system boot identity");

// Linux reads /proc/sys/kernel/random/boot_id with O_NOFOLLOW, a fixed byte
// cap, exact one-line framing, and lowercase UUID validation. ENOENT and
// EACCES/EPERM become explicit unavailable observations; unexpected open,
// read, close, framing, or content failures throw. Other systems return an
// explicit Unsupported observation.
[[nodiscard]] SyncSystemBootIdentityObservation
observe_sync_system_boot_identity_or_throw(
    std::string_view label = "system boot identity");

}  // namespace anonsync
