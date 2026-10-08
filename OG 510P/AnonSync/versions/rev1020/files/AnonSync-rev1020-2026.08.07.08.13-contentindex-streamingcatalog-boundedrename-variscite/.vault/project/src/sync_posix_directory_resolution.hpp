#pragma once

#if !defined(_WIN32)

#include <cstdint>
#include <filesystem>
#include <optional>
#include <string>
#include <string_view>

#include <sys/stat.h>

namespace anonsync {

// Exact live capability observed from the running POSIX environment.  The
// portable baseline compares st_dev/st_ino after component-wise no-follow
// opens.  Linux statx mount IDs detect same-device mount crossings after open;
// Linux openat2 additionally rejects mount crossings in kernel pathname
// resolution before the directory descriptor is returned.
enum class SyncPosixDirectoryResolutionCapability : std::uint8_t {
    DeviceIdentityOnly = 0,
    LinuxStatxMountId = 1,
    LinuxOpenat2NoXdev = 2,
    LinuxOpenat2NoXdevAndStatxMountId = 3,
};

[[nodiscard]] const char*
sync_posix_directory_resolution_capability_name(
    SyncPosixDirectoryResolutionCapability capability) noexcept;
[[nodiscard]] bool sync_posix_directory_resolution_uses_openat2_no_xdev(
    SyncPosixDirectoryResolutionCapability capability) noexcept;
[[nodiscard]] bool sync_posix_directory_resolution_uses_statx_mount_id(
    SyncPosixDirectoryResolutionCapability capability) noexcept;

// Pure probe-result classifiers keep unavailable-feature fallback separate
// from policy, programming, permission, and unexpected kernel failures.
enum class SyncPosixKernelProbeDisposition : std::uint8_t {
    Available = 0,
    ReportedUnavailable = 1,
    Fatal = 2,
};

[[nodiscard]] SyncPosixKernelProbeDisposition
sync_posix_classify_openat2_probe_result(
    long syscall_result,
    int error_number) noexcept;
[[nodiscard]] SyncPosixKernelProbeDisposition
sync_posix_classify_statx_mount_id_probe_result(
    long syscall_result,
    int error_number,
    bool mount_id_returned) noexcept;

struct SyncPosixMountIdentity final {
    bool available = false;
    // STATX_MNT_ID_UNIQUE is preferred when the running kernel reports it.
    // Unlike the older per-namespace mount ID, the unique form is not reused
    // for the lifetime of the system.
    bool unique = false;
    std::uint64_t value = 0;

    bool operator==(const SyncPosixMountIdentity&) const = default;
};

// Allocation-free observation of one existing path component relative to a
// retained directory descriptor. This is intentionally separate from the
// open helpers below: owners such as SQLite VFS callbacks may already hold
// POSIX record locks on the named inode, and opening then closing another
// descriptor for that inode can release process-associated locks. Linux
// statx supplies mount identity without creating a file descriptor.
enum class SyncPosixRelativeMountDisposition : std::uint8_t {
    RetainedMount = 0,
    Absent = 1,
    DifferentMount = 2,
    ProbeFailed = 3,
};

struct SyncPosixRelativeMountObservation final {
    SyncPosixRelativeMountDisposition disposition =
        SyncPosixRelativeMountDisposition::ProbeFailed;
    int error_number = 0;
};

// component must be one NUL-terminated relative pathname component. The
// observer never follows a final symbolic link, never allocates, and never
// opens the component. It returns ProbeFailed when statx mount identity was
// not part of the frozen capability, when the retained identity is absent, or
// when the previously proven kernel observation no longer succeeds.
[[nodiscard]] SyncPosixRelativeMountObservation
sync_posix_observe_relative_mount_noexcept(
    int parent_descriptor,
    const char* component,
    SyncPosixDirectoryResolutionCapability capability,
    const SyncPosixMountIdentity& retained_mount) noexcept;

enum class SyncPosixDirectoryMountPolicy : std::uint8_t {
    AllowMountCrossing = 0,
    RequireRetainedRootMount = 1,
};

enum class SyncPosixDirectoryComponentRole : std::uint8_t {
    AbsoluteParent = 0,
    RootedDescendant = 1,
};

// The caller owns descriptor on success and must close it.  The helper closes
// every intermediate descriptor on all exceptional paths.
struct SyncPosixOpenedDirectory final {
    int descriptor = -1;
    struct stat status {};
};

// The caller owns descriptor on success and must close it. The component is
// inspected without following links, opened with nonblocking regular-file
// flags, re-attested by descriptor identity, and (when available) fenced to
// the retained root mount.
struct SyncPosixOpenedRegularFile final {
    int descriptor = -1;
    struct stat status {};
};

[[nodiscard]] SyncPosixDirectoryResolutionCapability
sync_posix_probe_directory_resolution_capability_or_throw(
    int directory_descriptor,
    std::string_view label);

void sync_posix_verify_directory_resolution_capability_or_throw(
    int directory_descriptor,
    SyncPosixDirectoryResolutionCapability expected,
    std::string_view label);

[[nodiscard]] SyncPosixMountIdentity
sync_posix_capture_mount_identity_or_throw(
    int directory_descriptor,
    SyncPosixDirectoryResolutionCapability capability,
    std::string_view label);

[[nodiscard]] SyncPosixOpenedDirectory
sync_posix_open_filesystem_root_directory_or_throw(
    std::string_view label);

// Returns nullopt only when the named component is absent at a bounded
// no-follow inspection/open cutpoint. Symlinks, non-directories, mount
// crossings, permission failures, and identity races remain errors. This is
// the read-side primitive for safely distinguishing an absent descendant path
// from an unsafe one without weakening the required-open API below.
[[nodiscard]] std::optional<SyncPosixOpenedDirectory>
sync_posix_open_optional_directory_component_or_throw(
    int parent_descriptor,
    std::string_view component,
    const std::filesystem::path& display_path,
    SyncPosixDirectoryComponentRole role,
    SyncPosixDirectoryMountPolicy mount_policy,
    SyncPosixDirectoryResolutionCapability capability,
    const SyncPosixMountIdentity& retained_root_mount,
    std::string_view label);

[[nodiscard]] SyncPosixOpenedDirectory
sync_posix_open_directory_component_or_throw(
    int parent_descriptor,
    std::string_view component,
    const std::filesystem::path& display_path,
    SyncPosixDirectoryComponentRole role,
    SyncPosixDirectoryMountPolicy mount_policy,
    SyncPosixDirectoryResolutionCapability capability,
    const SyncPosixMountIdentity& retained_root_mount,
    std::string_view label);

// Returns nullopt only when the named component is absent at a bounded
// no-follow inspection/open cutpoint. Symlinks, non-regular files, mount
// crossings, permission failures, and identity races remain errors. This is
// the regular-file counterpart to the optional directory primitive above; the
// required-open API remains the default for callers that already own presence
// authority.
[[nodiscard]] std::optional<SyncPosixOpenedRegularFile>
sync_posix_open_optional_regular_file_component_or_throw(
    int parent_descriptor,
    std::string_view component,
    const std::filesystem::path& display_path,
    SyncPosixDirectoryMountPolicy mount_policy,
    SyncPosixDirectoryResolutionCapability capability,
    const SyncPosixMountIdentity& retained_root_mount,
    std::string_view label);

[[nodiscard]] SyncPosixOpenedRegularFile
sync_posix_open_regular_file_component_or_throw(
    int parent_descriptor,
    std::string_view component,
    const std::filesystem::path& display_path,
    SyncPosixDirectoryMountPolicy mount_policy,
    SyncPosixDirectoryResolutionCapability capability,
    const SyncPosixMountIdentity& retained_root_mount,
    std::string_view label);

}  // namespace anonsync

#endif
