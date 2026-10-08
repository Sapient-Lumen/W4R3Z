#include "sync_system_epoch_identity.hpp"

#include <array>
#include <cerrno>
#include <cstddef>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>
#include <utility>

#if defined(__linux__)
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#endif

namespace anonsync {
namespace {

constexpr std::string_view kUnsupportedBootSource =
    "system-boot-identity-unsupported-v1";
constexpr std::string_view kLinuxProcBootSource =
    "linux-proc-boot-id-v1";
constexpr std::string_view kLinuxProcBootMissingSource =
    "linux-proc-boot-id-missing-v1";
constexpr std::string_view kLinuxProcBootPermissionSource =
    "linux-proc-boot-id-permission-denied-v1";
[[nodiscard]] bool ascii_lower_hex(char value) noexcept {
    return (value >= '0' && value <= '9') ||
           (value >= 'a' && value <= 'f');
}

#if defined(__linux__)

class OwnedDescriptor final {
public:
    explicit OwnedDescriptor(int descriptor = -1) noexcept
        : descriptor_(descriptor) {}
    ~OwnedDescriptor() { reset_noexcept(); }
    OwnedDescriptor(const OwnedDescriptor&) = delete;
    OwnedDescriptor& operator=(const OwnedDescriptor&) = delete;
    OwnedDescriptor(OwnedDescriptor&& other) noexcept
        : descriptor_(std::exchange(other.descriptor_, -1)) {}
    OwnedDescriptor& operator=(OwnedDescriptor&& other) noexcept {
        if (this != &other) {
            reset_noexcept();
            descriptor_ = std::exchange(other.descriptor_, -1);
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return descriptor_; }

    void close_or_throw(std::string_view label) {
        const int descriptor = std::exchange(descriptor_, -1);
        if (descriptor < 0) return;
        if (::close(descriptor) != 0) {
            const int error = errno;
            throw std::system_error(
                error, std::generic_category(), std::string(label));
        }
    }

private:
    void reset_noexcept() noexcept {
        if (descriptor_ < 0) return;
        const int saved = errno;
        (void)::close(descriptor_);
        errno = saved;
        descriptor_ = -1;
    }

    int descriptor_ = -1;
};

[[nodiscard]] SyncSystemBootIdentityObservation
observe_linux_boot_identity_or_throw(std::string_view label_view) {
    const std::string label(label_view);
    int descriptor;
    do {
        descriptor = ::open(
            "/proc/sys/kernel/random/boot_id",
            O_RDONLY | O_CLOEXEC | O_NOFOLLOW | O_NONBLOCK);
    } while (descriptor < 0 && errno == EINTR);
    const int open_error = descriptor < 0 ? errno : 0;
    switch (sync_system_classify_boot_identity_open_result(
        descriptor, open_error)) {
        case SyncSystemBootIdentityProbeDisposition::Missing:
            return {SyncSystemBootIdentityKind::LinuxProcBootIdMissing, {}};
        case SyncSystemBootIdentityProbeDisposition::PermissionDenied:
            return {
                SyncSystemBootIdentityKind::LinuxProcBootIdPermissionDenied,
                {}};
        case SyncSystemBootIdentityProbeDisposition::Fatal:
            throw std::system_error(
                open_error, std::generic_category(), label + " open");
        case SyncSystemBootIdentityProbeDisposition::Available:
            break;
    }

    OwnedDescriptor owned(descriptor);
    struct stat status {};
    if (::fstat(owned.get(), &status) != 0) {
        const int error = errno;
        throw std::system_error(
            error, std::generic_category(), label + " fstat");
    }
    if (!S_ISREG(status.st_mode)) {
        throw std::runtime_error(label + " source is not a regular file");
    }

    constexpr std::size_t kMaximumBootIdentityBytes = 64U;
    std::string bytes;
    bytes.reserve(kMaximumBootIdentityBytes);
    std::array<char, 64U> buffer{};
    for (;;) {
        ssize_t count;
        do {
            count = ::read(owned.get(), buffer.data(), buffer.size());
        } while (count < 0 && errno == EINTR);
        if (count < 0) {
            const int error = errno;
            throw std::system_error(
                error, std::generic_category(), label + " read");
        }
        if (count == 0) break;
        const auto amount = static_cast<std::size_t>(count);
        if (bytes.size() > kMaximumBootIdentityBytes - amount) {
            throw std::runtime_error(
                label + " exceeds its bounded observation size");
        }
        bytes.append(buffer.data(), amount);
    }
    owned.close_or_throw(label + " close");

    return {
        SyncSystemBootIdentityKind::LinuxProcBootId,
        sync_system_parse_boot_id_text_or_throw(bytes, label)};
}

#endif

}  // namespace

SyncSystemBootIdentityProbeDisposition
sync_system_classify_boot_identity_open_result(
    int open_result,
    int error_number) noexcept {
    if (open_result >= 0) {
        return SyncSystemBootIdentityProbeDisposition::Available;
    }
    if (error_number == ENOENT) {
        return SyncSystemBootIdentityProbeDisposition::Missing;
    }
    if (error_number == EACCES || error_number == EPERM) {
        return SyncSystemBootIdentityProbeDisposition::PermissionDenied;
    }
    return SyncSystemBootIdentityProbeDisposition::Fatal;
}

bool sync_system_boot_id_is_canonical(std::string_view value) noexcept {
    if (value.size() != 36U) return false;
    for (std::size_t index = 0U; index < value.size(); ++index) {
        const bool separator =
            index == 8U || index == 13U || index == 18U || index == 23U;
        if (separator) {
            if (value[index] != '-') return false;
        } else if (!ascii_lower_hex(value[index])) {
            return false;
        }
    }
    return true;
}

std::string sync_system_parse_boot_id_text_or_throw(
    std::string_view bytes,
    std::string_view label_view) {
    const std::string label(label_view);
    if (bytes.find('\0') != std::string_view::npos) {
        throw std::runtime_error(label + " contains a NUL byte");
    }

    std::string_view identifier = bytes;
    if (bytes.size() == 37U && bytes.back() == '\n') {
        identifier.remove_suffix(1U);
    } else if (bytes.size() == 38U &&
               bytes.substr(bytes.size() - 2U) == "\r\n") {
        identifier.remove_suffix(2U);
    } else if (bytes.size() != 36U) {
        throw std::runtime_error(label + " is not exactly one UUID line");
    }
    if (!sync_system_boot_id_is_canonical(identifier)) {
        throw std::runtime_error(
            label + " is not a canonical lowercase UUID");
    }
    return std::string(identifier);
}

const char* sync_system_boot_identity_kind_name(
    SyncSystemBootIdentityKind kind) noexcept {
    switch (kind) {
        case SyncSystemBootIdentityKind::Unsupported:
            return kUnsupportedBootSource.data();
        case SyncSystemBootIdentityKind::LinuxProcBootId:
            return kLinuxProcBootSource.data();
        case SyncSystemBootIdentityKind::LinuxProcBootIdMissing:
            return kLinuxProcBootMissingSource.data();
        case SyncSystemBootIdentityKind::LinuxProcBootIdPermissionDenied:
            return kLinuxProcBootPermissionSource.data();
    }
    return "unknown-system-boot-identity-source";
}

SyncSystemBootIdentityKind
sync_system_boot_identity_kind_from_name_or_throw(
    std::string_view name,
    std::string_view label_view) {
    if (name == kUnsupportedBootSource) {
        return SyncSystemBootIdentityKind::Unsupported;
    }
    if (name == kLinuxProcBootSource) {
        return SyncSystemBootIdentityKind::LinuxProcBootId;
    }
    if (name == kLinuxProcBootMissingSource) {
        return SyncSystemBootIdentityKind::LinuxProcBootIdMissing;
    }
    if (name == kLinuxProcBootPermissionSource) {
        return SyncSystemBootIdentityKind::LinuxProcBootIdPermissionDenied;
    }
    throw std::runtime_error(
        std::string(label_view) + " has an unknown boot identity source");
}

void validate_sync_system_boot_identity_observation_or_throw(
    const SyncSystemBootIdentityObservation& observation,
    std::string_view label_view) {
    const std::string label(label_view);
    if (observation.kind == SyncSystemBootIdentityKind::LinuxProcBootId) {
        if (!sync_system_boot_id_is_canonical(observation.boot_id)) {
            throw std::runtime_error(
                label + " boot ID is not a canonical lowercase UUID");
        }
        return;
    }
    if (!observation.boot_id.empty()) {
        throw std::runtime_error(
            label + " unavailable source carries boot identity residue");
    }
    switch (observation.kind) {
        case SyncSystemBootIdentityKind::Unsupported:
        case SyncSystemBootIdentityKind::LinuxProcBootIdMissing:
        case SyncSystemBootIdentityKind::LinuxProcBootIdPermissionDenied:
            return;
        case SyncSystemBootIdentityKind::LinuxProcBootId:
            break;
    }
    throw std::runtime_error(label + " boot identity kind is unknown");
}

SyncSystemBootIdentityObservation observe_sync_system_boot_identity_or_throw(
    std::string_view label) {
#if defined(__linux__)
    SyncSystemBootIdentityObservation observation =
        observe_linux_boot_identity_or_throw(label);
#else
    (void)label;
    SyncSystemBootIdentityObservation observation{
        SyncSystemBootIdentityKind::Unsupported, {}};
#endif
    validate_sync_system_boot_identity_observation_or_throw(
        observation, label);
    return observation;
}

}  // namespace anonsync
