#include "sync_posix_directory_resolution.hpp"

#if !defined(_WIN32)

#include <cerrno>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <stdexcept>
#include <string>
#include <system_error>
#include <utility>

#include <fcntl.h>
#include <unistd.h>

#if defined(__linux__)
#include <sys/syscall.h>
#if __has_include(<linux/openat2.h>)
#include <linux/openat2.h>
#define ANONSYNC_HAVE_LINUX_OPENAT2_UAPI 1
#endif
#if __has_include(<linux/stat.h>)
#include <linux/stat.h>
#define ANONSYNC_HAVE_LINUX_STATX_UAPI 1
#endif
#endif

namespace anonsync {
namespace {

namespace fs = std::filesystem;

class ScopedFd final {
public:
    explicit ScopedFd(int descriptor = -1) noexcept
        : descriptor_(descriptor) {}
    ~ScopedFd() { reset(); }
    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;
    ScopedFd(ScopedFd&& other) noexcept
        : descriptor_(other.release()) {}
    ScopedFd& operator=(ScopedFd&& other) noexcept {
        if (this != &other) reset(other.release());
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return descriptor_; }
    [[nodiscard]] int release() noexcept {
        return std::exchange(descriptor_, -1);
    }

private:
    void reset(int descriptor = -1) noexcept {
        if (descriptor_ >= 0) (void)::close(descriptor_);
        descriptor_ = descriptor;
    }

    int descriptor_ = -1;
};

[[nodiscard]] std::string error_text(int error_number) {
    return std::error_code(error_number, std::generic_category()).message();
}

[[nodiscard]] bool same_identity(const struct stat& left,
                                 const struct stat& right) noexcept {
    return left.st_dev == right.st_dev && left.st_ino == right.st_ino;
}

[[nodiscard]] int directory_open_flags() noexcept {
    int flags = O_RDONLY;
#ifdef O_DIRECTORY
    flags |= O_DIRECTORY;
#endif
#ifdef O_CLOEXEC
    flags |= O_CLOEXEC;
#endif
#ifdef O_NOFOLLOW
    flags |= O_NOFOLLOW;
#endif
    return flags;
}

[[nodiscard]] int regular_file_open_flags() noexcept {
    int flags = O_RDONLY | O_NONBLOCK;
#ifdef O_CLOEXEC
    flags |= O_CLOEXEC;
#endif
#ifdef O_NOFOLLOW
    flags |= O_NOFOLLOW;
#endif
#ifdef O_NOCTTY
    flags |= O_NOCTTY;
#endif
    return flags;
}

void set_close_on_exec_or_throw(int descriptor,
                                std::string_view label,
                                const fs::path& display_path) {
#ifndef O_CLOEXEC
    const int old_flags = ::fcntl(descriptor, F_GETFD);
    if (old_flags < 0 ||
        ::fcntl(descriptor, F_SETFD, old_flags | FD_CLOEXEC) != 0) {
        const int error = errno;
        throw std::runtime_error(
            std::string(label) + " close-on-exec setup failed for " +
            display_path.generic_string() + ": " + error_text(error));
    }
#else
    (void)descriptor;
    (void)label;
    (void)display_path;
#endif
}

struct ProbeObservation final {
    SyncPosixKernelProbeDisposition disposition =
        SyncPosixKernelProbeDisposition::ReportedUnavailable;
    int error_number = 0;
};

#if defined(__linux__) && defined(ANONSYNC_HAVE_LINUX_STATX_UAPI) && \
    defined(STATX_MNT_ID)
[[nodiscard]] constexpr unsigned int requested_mount_identity_mask() noexcept {
#if defined(STATX_MNT_ID_UNIQUE)
    return STATX_MNT_ID | STATX_MNT_ID_UNIQUE;
#else
    return STATX_MNT_ID;
#endif
}

[[nodiscard]] bool statx_mount_identity_returned(
    const struct statx& status) noexcept {
#if defined(STATX_MNT_ID_UNIQUE)
    return (status.stx_mask &
            static_cast<unsigned int>(STATX_MNT_ID |
                                      STATX_MNT_ID_UNIQUE)) != 0U;
#else
    return (status.stx_mask & STATX_MNT_ID) != 0U;
#endif
}

[[nodiscard]] bool statx_unique_mount_identity_returned(
    const struct statx& status) noexcept {
#if defined(STATX_MNT_ID_UNIQUE)
    return (status.stx_mask & STATX_MNT_ID_UNIQUE) != 0U;
#else
    (void)status;
    return false;
#endif
}
#endif

[[nodiscard]] ProbeObservation probe_openat2_no_xdev(
    int directory_descriptor) noexcept {
#if defined(__linux__) && defined(ANONSYNC_HAVE_LINUX_OPENAT2_UAPI) && \
    defined(SYS_openat2) && defined(RESOLVE_BENEATH) && \
    defined(RESOLVE_NO_MAGICLINKS) && defined(RESOLVE_NO_SYMLINKS) && \
    defined(RESOLVE_NO_XDEV)
    struct open_how how {};
    how.flags = static_cast<std::uint64_t>(directory_open_flags());
    how.resolve = static_cast<std::uint64_t>(
        RESOLVE_BENEATH | RESOLVE_NO_MAGICLINKS | RESOLVE_NO_SYMLINKS |
        RESOLVE_NO_XDEV);

    long result;
    do {
        result = ::syscall(SYS_openat2, directory_descriptor, ".", &how,
                           sizeof(how));
    } while (result < 0 && errno == EINTR);
    const int error = result < 0 ? errno : 0;
    const SyncPosixKernelProbeDisposition disposition =
        sync_posix_classify_openat2_probe_result(result, error);
    if (result >= 0) (void)::close(static_cast<int>(result));
    return ProbeObservation{disposition, error};
#else
    (void)directory_descriptor;
    return ProbeObservation{
        SyncPosixKernelProbeDisposition::ReportedUnavailable, ENOSYS};
#endif
}

[[nodiscard]] ProbeObservation probe_statx_mount_id(
    int directory_descriptor) noexcept {
#if defined(__linux__) && defined(ANONSYNC_HAVE_LINUX_STATX_UAPI) && \
    defined(SYS_statx) && defined(AT_EMPTY_PATH) && defined(STATX_MNT_ID)
    struct statx status {};
    long result;
    do {
        result = ::syscall(SYS_statx, directory_descriptor, "",
                           AT_EMPTY_PATH | AT_SYMLINK_NOFOLLOW,
                           requested_mount_identity_mask(), &status);
    } while (result < 0 && errno == EINTR);
    const int error = result < 0 ? errno : 0;
    const bool returned =
        result == 0 && statx_mount_identity_returned(status);
    return ProbeObservation{
        sync_posix_classify_statx_mount_id_probe_result(
            result, error, returned),
        error};
#else
    (void)directory_descriptor;
    return ProbeObservation{
        SyncPosixKernelProbeDisposition::ReportedUnavailable, ENOSYS};
#endif
}

[[nodiscard]] SyncPosixDirectoryResolutionCapability combine_capabilities(
    bool openat2_available,
    bool statx_mount_id_available) noexcept {
    if (openat2_available && statx_mount_id_available) {
        return SyncPosixDirectoryResolutionCapability::
            LinuxOpenat2NoXdevAndStatxMountId;
    }
    if (openat2_available) {
        return SyncPosixDirectoryResolutionCapability::LinuxOpenat2NoXdev;
    }
    if (statx_mount_id_available) {
        return SyncPosixDirectoryResolutionCapability::LinuxStatxMountId;
    }
    return SyncPosixDirectoryResolutionCapability::DeviceIdentityOnly;
}

[[nodiscard]] const char* component_noun(
    SyncPosixDirectoryComponentRole role) noexcept {
    return role == SyncPosixDirectoryComponentRole::AbsoluteParent
               ? "parent component"
               : "component";
}

[[noreturn]] void throw_component_inspection_error(
    std::string_view label,
    SyncPosixDirectoryComponentRole role,
    const fs::path& display_path,
    int error_number) {
    throw std::runtime_error(
        std::string(label) + " " + component_noun(role) +
        " inspection failed for " + display_path.generic_string() + ": " +
        error_text(error_number));
}

[[noreturn]] void throw_component_symlink_error(
    std::string_view label,
    SyncPosixDirectoryComponentRole role,
    const fs::path& display_path) {
    if (role == SyncPosixDirectoryComponentRole::AbsoluteParent) {
        throw std::runtime_error(
            std::string(label) + " refuses symbolic-link parent component: " +
            display_path.generic_string());
    }
    throw std::runtime_error(
        std::string(label) + " component must not be a symlink: " +
        display_path.generic_string());
}

[[noreturn]] void throw_component_not_directory_error(
    std::string_view label,
    SyncPosixDirectoryComponentRole role,
    const fs::path& display_path) {
    throw std::runtime_error(
        std::string(label) + " " + component_noun(role) +
        " is not a directory: " + display_path.generic_string());
}

[[noreturn]] void throw_component_open_error(
    std::string_view label,
    SyncPosixDirectoryComponentRole role,
    const fs::path& display_path,
    int error_number) {
    throw std::runtime_error(
        std::string(label) + " " + component_noun(role) +
        " open failed for " + display_path.generic_string() + ": " +
        error_text(error_number));
}

[[noreturn]] void throw_component_fstat_error(
    std::string_view label,
    SyncPosixDirectoryComponentRole role,
    const fs::path& display_path,
    int error_number) {
    throw std::runtime_error(
        std::string(label) + " " + component_noun(role) +
        " fstat failed for " + display_path.generic_string() + ": " +
        error_text(error_number));
}

[[noreturn]] void throw_component_changed_error(
    std::string_view label,
    SyncPosixDirectoryComponentRole role,
    const fs::path& display_path) {
    if (role == SyncPosixDirectoryComponentRole::AbsoluteParent) {
        throw std::runtime_error(
            std::string(label) +
            " parent component changed during traversal: " +
            display_path.generic_string());
    }
    throw std::runtime_error(
        std::string(label) + " component changed identity while opening: " +
        display_path.generic_string());
}

[[nodiscard]] int open_component_with_policy_and_flags(
    int parent_descriptor,
    const std::string& component,
    int open_flags,
    SyncPosixDirectoryMountPolicy mount_policy,
    SyncPosixDirectoryResolutionCapability capability,
    int& error_number) noexcept {
    error_number = 0;
#if defined(__linux__) && defined(ANONSYNC_HAVE_LINUX_OPENAT2_UAPI) && \
    defined(SYS_openat2) && defined(RESOLVE_BENEATH) && \
    defined(RESOLVE_NO_MAGICLINKS) && defined(RESOLVE_NO_SYMLINKS) && \
    defined(RESOLVE_NO_XDEV)
    if (mount_policy ==
            SyncPosixDirectoryMountPolicy::RequireRetainedRootMount &&
        sync_posix_directory_resolution_uses_openat2_no_xdev(capability)) {
        struct open_how how {};
        how.flags = static_cast<std::uint64_t>(open_flags);
        how.resolve = static_cast<std::uint64_t>(
            RESOLVE_BENEATH | RESOLVE_NO_MAGICLINKS |
            RESOLVE_NO_SYMLINKS | RESOLVE_NO_XDEV);
        constexpr std::size_t kMaximumRaceRetries = 8U;
        std::size_t race_retries = 0U;
        for (;;) {
            const long result = ::syscall(
                SYS_openat2, parent_descriptor, component.c_str(), &how,
                sizeof(how));
            if (result >= 0) return static_cast<int>(result);
            error_number = errno;
            if (error_number == EINTR) continue;
            if (error_number == EAGAIN &&
                race_retries < kMaximumRaceRetries) {
                ++race_retries;
                continue;
            }
            return -1;
        }
    }
#else
    (void)capability;
#endif

    int descriptor;
    do {
        descriptor = ::openat(parent_descriptor, component.c_str(),
                              open_flags);
    } while (descriptor < 0 && errno == EINTR);
    if (descriptor < 0) error_number = errno;
    return descriptor;
}

[[nodiscard]] int open_directory_component_with_policy(
    int parent_descriptor,
    const std::string& component,
    SyncPosixDirectoryMountPolicy mount_policy,
    SyncPosixDirectoryResolutionCapability capability,
    int& error_number) noexcept {
    return open_component_with_policy_and_flags(
        parent_descriptor, component, directory_open_flags(), mount_policy,
        capability, error_number);
}

[[nodiscard]] int open_regular_file_component_with_policy(
    int parent_descriptor,
    const std::string& component,
    SyncPosixDirectoryMountPolicy mount_policy,
    SyncPosixDirectoryResolutionCapability capability,
    int& error_number) noexcept {
    return open_component_with_policy_and_flags(
        parent_descriptor, component, regular_file_open_flags(), mount_policy,
        capability, error_number);
}

}  // namespace

const char* sync_posix_directory_resolution_capability_name(
    SyncPosixDirectoryResolutionCapability capability) noexcept {
    switch (capability) {
        case SyncPosixDirectoryResolutionCapability::DeviceIdentityOnly:
            return "portable-device-identity-v1";
        case SyncPosixDirectoryResolutionCapability::LinuxStatxMountId:
            return "linux-statx-mount-id-v1";
        case SyncPosixDirectoryResolutionCapability::LinuxOpenat2NoXdev:
            return "linux-openat2-no-xdev-v1";
        case SyncPosixDirectoryResolutionCapability::
            LinuxOpenat2NoXdevAndStatxMountId:
            return "linux-openat2-no-xdev-statx-mount-id-v1";
    }
    return "unknown-directory-resolution-capability";
}

bool sync_posix_directory_resolution_uses_openat2_no_xdev(
    SyncPosixDirectoryResolutionCapability capability) noexcept {
    return capability ==
               SyncPosixDirectoryResolutionCapability::LinuxOpenat2NoXdev ||
           capability == SyncPosixDirectoryResolutionCapability::
                             LinuxOpenat2NoXdevAndStatxMountId;
}

bool sync_posix_directory_resolution_uses_statx_mount_id(
    SyncPosixDirectoryResolutionCapability capability) noexcept {
    return capability ==
               SyncPosixDirectoryResolutionCapability::LinuxStatxMountId ||
           capability == SyncPosixDirectoryResolutionCapability::
                             LinuxOpenat2NoXdevAndStatxMountId;
}

SyncPosixKernelProbeDisposition
sync_posix_classify_openat2_probe_result(
    long syscall_result,
    int error_number) noexcept {
    if (syscall_result >= 0) {
        return SyncPosixKernelProbeDisposition::Available;
    }
    if (error_number == ENOSYS) {
        return SyncPosixKernelProbeDisposition::ReportedUnavailable;
    }
    return SyncPosixKernelProbeDisposition::Fatal;
}

SyncPosixKernelProbeDisposition
sync_posix_classify_statx_mount_id_probe_result(
    long syscall_result,
    int error_number,
    bool mount_id_returned) noexcept {
    if (syscall_result == 0) {
        return mount_id_returned
                   ? SyncPosixKernelProbeDisposition::Available
                   : SyncPosixKernelProbeDisposition::ReportedUnavailable;
    }
    if (syscall_result < 0 && error_number == ENOSYS) {
        return SyncPosixKernelProbeDisposition::ReportedUnavailable;
    }
    return SyncPosixKernelProbeDisposition::Fatal;
}

SyncPosixDirectoryResolutionCapability
sync_posix_probe_directory_resolution_capability_or_throw(
    int directory_descriptor,
    std::string_view label_view) {
    const std::string label(label_view);
    if (directory_descriptor < 0) {
        throw std::logic_error(label + " probe descriptor is absent");
    }

    const ProbeObservation openat2 =
        probe_openat2_no_xdev(directory_descriptor);
    if (openat2.disposition == SyncPosixKernelProbeDisposition::Fatal) {
        throw std::runtime_error(
            label + " openat2 no-cross-mount probe failed: " +
            error_text(openat2.error_number));
    }
    const ProbeObservation statx = probe_statx_mount_id(directory_descriptor);
    if (statx.disposition == SyncPosixKernelProbeDisposition::Fatal) {
        throw std::runtime_error(
            label + " statx mount-id probe failed: " +
            error_text(statx.error_number));
    }

    return combine_capabilities(
        openat2.disposition == SyncPosixKernelProbeDisposition::Available,
        statx.disposition == SyncPosixKernelProbeDisposition::Available);
}

void sync_posix_verify_directory_resolution_capability_or_throw(
    int directory_descriptor,
    SyncPosixDirectoryResolutionCapability expected,
    std::string_view label_view) {
    const std::string label(label_view);
    const SyncPosixDirectoryResolutionCapability observed =
        sync_posix_probe_directory_resolution_capability_or_throw(
            directory_descriptor, label + " observation");
    if (observed != expected) {
        throw std::runtime_error(
            label + " changed from " +
            sync_posix_directory_resolution_capability_name(expected) +
            " to " +
            sync_posix_directory_resolution_capability_name(observed));
    }
}

SyncPosixMountIdentity sync_posix_capture_mount_identity_or_throw(
    int directory_descriptor,
    SyncPosixDirectoryResolutionCapability capability,
    std::string_view label_view) {
    if (!sync_posix_directory_resolution_uses_statx_mount_id(capability)) {
        return {};
    }
    const std::string label(label_view);
#if defined(__linux__) && defined(ANONSYNC_HAVE_LINUX_STATX_UAPI) && \
    defined(SYS_statx) && defined(AT_EMPTY_PATH) && defined(STATX_MNT_ID)
    struct statx status {};
    long result;
    do {
        result = ::syscall(SYS_statx, directory_descriptor, "",
                           AT_EMPTY_PATH | AT_SYMLINK_NOFOLLOW,
                           requested_mount_identity_mask(), &status);
    } while (result < 0 && errno == EINTR);
    const int error = result < 0 ? errno : 0;
    const bool returned =
        result == 0 && statx_mount_identity_returned(status);
    if (sync_posix_classify_statx_mount_id_probe_result(
            result, error, returned) !=
        SyncPosixKernelProbeDisposition::Available) {
        throw std::runtime_error(
            label + " previously proven statx mount-id observation failed" +
            (error == 0 ? std::string() : ": " + error_text(error)));
    }
    return SyncPosixMountIdentity{
        true, statx_unique_mount_identity_returned(status),
        static_cast<std::uint64_t>(status.stx_mnt_id)};
#else
    (void)directory_descriptor;
    throw std::runtime_error(
        label + " previously proven statx mount-id support is not compiled");
#endif
}

SyncPosixRelativeMountObservation
sync_posix_observe_relative_mount_noexcept(
    int parent_descriptor,
    const char* component,
    SyncPosixDirectoryResolutionCapability capability,
    const SyncPosixMountIdentity& retained_mount) noexcept {
    using Disposition = SyncPosixRelativeMountDisposition;
    if (parent_descriptor < 0 || component == nullptr || *component == '\0' ||
        std::strcmp(component, ".") == 0 ||
        std::strcmp(component, "..") == 0 ||
        std::strchr(component, '/') != nullptr) {
        return {Disposition::ProbeFailed, EINVAL};
    }
    if (!sync_posix_directory_resolution_uses_statx_mount_id(capability) ||
        !retained_mount.available) {
        return {Disposition::ProbeFailed, EOPNOTSUPP};
    }

#if defined(__linux__) && defined(ANONSYNC_HAVE_LINUX_STATX_UAPI) && \
    defined(SYS_statx) && defined(STATX_MNT_ID)
    struct statx status {};
    long result;
    do {
        result = ::syscall(SYS_statx, parent_descriptor, component,
                           AT_SYMLINK_NOFOLLOW,
                           requested_mount_identity_mask(), &status);
    } while (result < 0 && errno == EINTR);
    if (result < 0) {
        const int error = errno;
        return {error == ENOENT ? Disposition::Absent
                                : Disposition::ProbeFailed,
                error};
    }
    if (!statx_mount_identity_returned(status)) {
        return {Disposition::ProbeFailed, EOPNOTSUPP};
    }

    const SyncPosixMountIdentity observed{
        true, statx_unique_mount_identity_returned(status),
        static_cast<std::uint64_t>(status.stx_mnt_id)};
    if (observed.unique != retained_mount.unique) {
        // The same frozen capability requested the same mask. A change in the
        // identity kind is capability drift, not evidence that two mount IDs
        // are safely comparable.
        return {Disposition::ProbeFailed, EPROTO};
    }
    return {observed.value == retained_mount.value
                ? Disposition::RetainedMount
                : Disposition::DifferentMount,
            0};
#else
    (void)parent_descriptor;
    (void)component;
    return {Disposition::ProbeFailed, ENOSYS};
#endif
}

SyncPosixOpenedDirectory sync_posix_open_filesystem_root_directory_or_throw(
    std::string_view label_view) {
    const std::string label(label_view);
    int descriptor;
    do {
        descriptor = ::open("/", directory_open_flags());
    } while (descriptor < 0 && errno == EINTR);
    if (descriptor < 0) {
        const int error = errno;
        throw std::runtime_error(label + " root directory open failed for /: " +
                                 error_text(error));
    }
    ScopedFd owned(descriptor);
    set_close_on_exec_or_throw(owned.get(), label, "/");
    struct stat status {};
    if (::fstat(owned.get(), &status) != 0) {
        const int error = errno;
        throw std::runtime_error(label + " root directory fstat failed for /: " +
                                 error_text(error));
    }
    if (!S_ISDIR(status.st_mode)) {
        throw std::runtime_error(label + " root path is not a directory");
    }
    return SyncPosixOpenedDirectory{owned.release(), status};
}

namespace {

enum class MissingDirectoryComponentPolicy : std::uint8_t {
    Throw = 0,
    ReturnAbsent = 1,
};

[[nodiscard]] std::optional<SyncPosixOpenedDirectory>
open_directory_component_with_missing_policy_or_throw(
    int parent_descriptor,
    std::string_view component_view,
    const fs::path& display_path,
    SyncPosixDirectoryComponentRole role,
    SyncPosixDirectoryMountPolicy mount_policy,
    SyncPosixDirectoryResolutionCapability capability,
    const SyncPosixMountIdentity& retained_root_mount,
    std::string_view label_view,
    MissingDirectoryComponentPolicy missing_policy) {
    const std::string label(label_view);
    const std::string component(component_view);
    if (parent_descriptor < 0) {
        throw std::logic_error(label + " parent descriptor is absent");
    }
    if (component.empty() || component == "." || component == ".." ||
        component.find('/') != std::string::npos ||
        component.find('\0') != std::string::npos) {
        throw std::runtime_error(label + " contains an unsafe path component");
    }

    struct stat before {};
    int inspect_result;
    do {
        inspect_result = ::fstatat(parent_descriptor, component.c_str(),
                                   &before, AT_SYMLINK_NOFOLLOW);
    } while (inspect_result != 0 && errno == EINTR);
    if (inspect_result != 0) {
        const int error = errno;
        if (error == ENOENT &&
            missing_policy ==
                MissingDirectoryComponentPolicy::ReturnAbsent) {
            return std::nullopt;
        }
        throw_component_inspection_error(label, role, display_path, error);
    }
    if (S_ISLNK(before.st_mode)) {
        throw_component_symlink_error(label, role, display_path);
    }
    if (!S_ISDIR(before.st_mode)) {
        throw_component_not_directory_error(label, role, display_path);
    }

    int open_error = 0;
    const int descriptor = open_directory_component_with_policy(
        parent_descriptor, component, mount_policy, capability, open_error);
    if (descriptor < 0) {
        if (open_error == ENOENT &&
            missing_policy ==
                MissingDirectoryComponentPolicy::ReturnAbsent) {
            return std::nullopt;
        }
        if (mount_policy ==
                SyncPosixDirectoryMountPolicy::RequireRetainedRootMount &&
            sync_posix_directory_resolution_uses_openat2_no_xdev(capability) &&
            open_error == EXDEV) {
            throw std::runtime_error(
                label + " component crosses the retained root mount: " +
                display_path.generic_string());
        }
        if (open_error == ELOOP) {
            throw_component_symlink_error(label, role, display_path);
        }
        throw_component_open_error(
            label, role, display_path, open_error);
    }
    ScopedFd owned(descriptor);
    set_close_on_exec_or_throw(owned.get(), label, display_path);

    struct stat after {};
    if (::fstat(owned.get(), &after) != 0) {
        throw_component_fstat_error(label, role, display_path, errno);
    }
    if (!S_ISDIR(after.st_mode) || !same_identity(before, after)) {
        throw_component_changed_error(label, role, display_path);
    }

    if (mount_policy ==
            SyncPosixDirectoryMountPolicy::RequireRetainedRootMount &&
        sync_posix_directory_resolution_uses_statx_mount_id(capability)) {
        if (!retained_root_mount.available) {
            throw std::logic_error(
                label + " retained root mount identity is absent");
        }
        const SyncPosixMountIdentity opened_mount =
            sync_posix_capture_mount_identity_or_throw(
                owned.get(), capability,
                label + " opened component mount identity");
        if (opened_mount != retained_root_mount) {
            throw std::runtime_error(
                label + " component crosses the retained root mount: " +
                display_path.generic_string());
        }
    }

    return SyncPosixOpenedDirectory{owned.release(), after};
}

}  // namespace

std::optional<SyncPosixOpenedDirectory>
sync_posix_open_optional_directory_component_or_throw(
    int parent_descriptor,
    std::string_view component,
    const fs::path& display_path,
    SyncPosixDirectoryComponentRole role,
    SyncPosixDirectoryMountPolicy mount_policy,
    SyncPosixDirectoryResolutionCapability capability,
    const SyncPosixMountIdentity& retained_root_mount,
    std::string_view label) {
    return open_directory_component_with_missing_policy_or_throw(
        parent_descriptor, component, display_path, role, mount_policy,
        capability, retained_root_mount, label,
        MissingDirectoryComponentPolicy::ReturnAbsent);
}

SyncPosixOpenedDirectory sync_posix_open_directory_component_or_throw(
    int parent_descriptor,
    std::string_view component,
    const fs::path& display_path,
    SyncPosixDirectoryComponentRole role,
    SyncPosixDirectoryMountPolicy mount_policy,
    SyncPosixDirectoryResolutionCapability capability,
    const SyncPosixMountIdentity& retained_root_mount,
    std::string_view label) {
    std::optional<SyncPosixOpenedDirectory> opened =
        open_directory_component_with_missing_policy_or_throw(
            parent_descriptor, component, display_path, role, mount_policy,
            capability, retained_root_mount, label,
            MissingDirectoryComponentPolicy::Throw);
    if (!opened.has_value()) {
        throw std::logic_error(
            std::string(label) + " required component was reported absent");
    }
    return std::move(*opened);
}

namespace {

enum class MissingRegularFileComponentPolicy : std::uint8_t {
    Throw = 0,
    ReturnAbsent = 1,
};

[[nodiscard]] std::optional<SyncPosixOpenedRegularFile>
open_regular_file_component_with_missing_policy_or_throw(
    int parent_descriptor,
    std::string_view component_view,
    const fs::path& display_path,
    SyncPosixDirectoryMountPolicy mount_policy,
    SyncPosixDirectoryResolutionCapability capability,
    const SyncPosixMountIdentity& retained_root_mount,
    std::string_view label_view,
    MissingRegularFileComponentPolicy missing_policy) {
    const std::string label(label_view);
    const std::string component(component_view);
    if (parent_descriptor < 0) {
        throw std::logic_error(label + " parent descriptor is absent");
    }
    if (component.empty() || component == "." || component == ".." ||
        component.find('/') != std::string::npos ||
        component.find('\0') != std::string::npos) {
        throw std::runtime_error(label + " contains an unsafe file component");
    }
#if !defined(O_NOFOLLOW)
    throw std::runtime_error(
        label + " requires O_NOFOLLOW regular-file authority");
#else
    struct stat before {};
    int inspect_result;
    do {
        inspect_result = ::fstatat(parent_descriptor, component.c_str(),
                                   &before, AT_SYMLINK_NOFOLLOW);
    } while (inspect_result != 0 && errno == EINTR);
    if (inspect_result != 0) {
        const int error = errno;
        if (error == ENOENT &&
            missing_policy ==
                MissingRegularFileComponentPolicy::ReturnAbsent) {
            return std::nullopt;
        }
        throw std::runtime_error(
            label + " regular-file inspection failed for " +
            display_path.generic_string() + ": " + error_text(error));
    }
    if (S_ISLNK(before.st_mode)) {
        throw std::runtime_error(
            label + " regular-file component must not be a symlink: " +
            display_path.generic_string());
    }
    if (!S_ISREG(before.st_mode)) {
        throw std::runtime_error(
            label + " component is not a regular file: " +
            display_path.generic_string());
    }

    int open_error = 0;
    const int descriptor = open_regular_file_component_with_policy(
        parent_descriptor, component, mount_policy, capability, open_error);
    if (descriptor < 0) {
        if (open_error == ENOENT &&
            missing_policy ==
                MissingRegularFileComponentPolicy::ReturnAbsent) {
            return std::nullopt;
        }
        if (mount_policy ==
                SyncPosixDirectoryMountPolicy::RequireRetainedRootMount &&
            sync_posix_directory_resolution_uses_openat2_no_xdev(capability) &&
            open_error == EXDEV) {
            throw std::runtime_error(
                label + " regular-file component crosses the retained root mount: " +
                display_path.generic_string());
        }
        if (open_error == ELOOP) {
            throw std::runtime_error(
                label + " regular-file component became a symlink: " +
                display_path.generic_string());
        }
        throw std::runtime_error(
            label + " regular-file open failed for " +
            display_path.generic_string() + ": " + error_text(open_error));
    }
    ScopedFd owned(descriptor);
    set_close_on_exec_or_throw(owned.get(), label, display_path);

    const int status_flags = ::fcntl(owned.get(), F_GETFL);
    if (status_flags < 0 || (status_flags & O_NONBLOCK) == 0) {
        const int error = status_flags < 0 ? errno : EINVAL;
        throw std::runtime_error(
            label + " regular-file nonblocking flag proof failed for " +
            display_path.generic_string() + ": " + error_text(error));
    }

    struct stat after {};
    if (::fstat(owned.get(), &after) != 0) {
        const int error = errno;
        throw std::runtime_error(
            label + " regular-file fstat failed for " +
            display_path.generic_string() + ": " + error_text(error));
    }
    if (!S_ISREG(after.st_mode) || !same_identity(before, after)) {
        throw std::runtime_error(
            label + " regular-file component changed identity while opening: " +
            display_path.generic_string());
    }

    if (mount_policy ==
            SyncPosixDirectoryMountPolicy::RequireRetainedRootMount &&
        sync_posix_directory_resolution_uses_statx_mount_id(capability)) {
        if (!retained_root_mount.available) {
            throw std::logic_error(
                label + " retained root mount identity is absent");
        }
        const SyncPosixMountIdentity opened_mount =
            sync_posix_capture_mount_identity_or_throw(
                owned.get(), capability,
                label + " opened regular-file mount identity");
        if (opened_mount != retained_root_mount) {
            throw std::runtime_error(
                label + " regular-file component crosses the retained root mount: " +
                display_path.generic_string());
        }
    }

    return SyncPosixOpenedRegularFile{owned.release(), after};
#endif
}

}  // namespace

std::optional<SyncPosixOpenedRegularFile>
sync_posix_open_optional_regular_file_component_or_throw(
    int parent_descriptor,
    std::string_view component,
    const fs::path& display_path,
    SyncPosixDirectoryMountPolicy mount_policy,
    SyncPosixDirectoryResolutionCapability capability,
    const SyncPosixMountIdentity& retained_root_mount,
    std::string_view label) {
    return open_regular_file_component_with_missing_policy_or_throw(
        parent_descriptor, component, display_path, mount_policy, capability,
        retained_root_mount, label,
        MissingRegularFileComponentPolicy::ReturnAbsent);
}

SyncPosixOpenedRegularFile
sync_posix_open_regular_file_component_or_throw(
    int parent_descriptor,
    std::string_view component,
    const fs::path& display_path,
    SyncPosixDirectoryMountPolicy mount_policy,
    SyncPosixDirectoryResolutionCapability capability,
    const SyncPosixMountIdentity& retained_root_mount,
    std::string_view label) {
    std::optional<SyncPosixOpenedRegularFile> opened =
        open_regular_file_component_with_missing_policy_or_throw(
            parent_descriptor, component, display_path, mount_policy,
            capability, retained_root_mount, label,
            MissingRegularFileComponentPolicy::Throw);
    if (!opened.has_value()) {
        throw std::logic_error(
            std::string(label) + " required regular file was reported absent");
    }
    return std::move(*opened);
}

}  // namespace anonsync

#endif
