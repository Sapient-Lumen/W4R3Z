#pragma once

#if !defined(_WIN32)

#include "sync_posix_directory_resolution.hpp"
#include "sync_posix_mount_namespace_authority.hpp"
#include "sync_process_incarnation.hpp"
#include "sync_thread_incarnation.hpp"

#include <cstdint>
#include <filesystem>
#include <string>
#include <string_view>

namespace anonsync {

namespace sync_directory_authority_detail {
class SyncDirectoryAuthorityAccess;
}
namespace persistence {
class LocalJsonlReplayDirectoryAuthority;
}

// Frozen kernel-visible evidence for one owner-controlled directory capability.
// This is narrower than process-exclusive write access: another process with
// the same effective UID, a privileged process, mutable ancestor authority, or
// a mechanism outside the reported POSIX mode bits remains outside the proof.
struct SyncDirectoryAttestation final {
    std::uint64_t device = 0;
    std::uint64_t inode = 0;
    std::uint64_t owner_user_id = 0;
    std::uint64_t owner_group_id = 0;
    std::uint64_t effective_user_id = 0;
    std::uint64_t effective_group_id = 0;
    std::uint32_t permission_mode = 0;
    std::uint64_t filesystem_id = 0;
    std::uint64_t mount_flags = 0;
    std::uint64_t filesystem_name_maximum = 0;
    long path_name_maximum = -1;

    bool operator==(const SyncDirectoryAttestation&) const = default;
};

// Move-only, process-incarnation- and thread-incarnation-bound authority over
// one retained directory. Opening traverses every absolute path component
// without following symlinks, retains the terminal descriptor, and freezes
// identity, ownership, mode, and mount observations. Every later proof checks
// both the retained descriptor and the configured absolute path. Any failed
// reproof permanently revokes this object; restoring visible path or mode
// cannot resurrect authority after an unobserved interval. The calling
// thread's live mount-namespace identity, directory resolution capability, and,
// when available, Linux statx mount identity are frozen separately from the
// durable attestation digest: namespace and mount IDs are runtime-ephemeral
// evidence, not restart-stable identity.
class SyncDirectoryAuthority final {
public:
    SyncDirectoryAuthority() = default;
    ~SyncDirectoryAuthority();
    SyncDirectoryAuthority(const SyncDirectoryAuthority&) = delete;
    SyncDirectoryAuthority& operator=(const SyncDirectoryAuthority&) = delete;
    SyncDirectoryAuthority(SyncDirectoryAuthority&& other) noexcept;
    SyncDirectoryAuthority& operator=(SyncDirectoryAuthority&& other) noexcept;

    [[nodiscard]] static SyncDirectoryAuthority open_or_throw(
        const std::filesystem::path& absolute_directory,
        const std::string& label = "sync directory authority");

    [[nodiscard]] const std::filesystem::path& path() const noexcept;
    [[nodiscard]] const std::string& absolute_path() const noexcept;
    [[nodiscard]] const SyncDirectoryAttestation& attestation() const noexcept;
    [[nodiscard]] SyncPosixDirectoryResolutionCapability
    resolution_capability() const noexcept;
    [[nodiscard]] const SyncPosixMountNamespaceIdentity&
    mount_namespace_identity() const noexcept;

    void verify_or_throw(
        std::string_view label = "sync directory authority") const;

private:
    friend class sync_directory_authority_detail::
        SyncDirectoryAuthorityAccess;
    friend class persistence::LocalJsonlReplayDirectoryAuthority;

    void require_current_owner_noexcept() const noexcept;
    void require_current_owner_or_throw(std::string_view label) const;
    void transfer_from_noexcept(SyncDirectoryAuthority& other) noexcept;
    void clear_moved_from_noexcept() noexcept;

    [[nodiscard]] int descriptor_no_verify() const noexcept;
    [[nodiscard]] long name_maximum_no_verify() const noexcept;
    [[nodiscard]] SyncPosixDirectoryResolutionCapability
    resolution_capability_no_verify() const noexcept;
    [[nodiscard]] const SyncPosixMountIdentity&
    mount_identity_no_verify() const noexcept;

    SyncProcessIncarnation process_id_;
    SyncThreadIncarnation thread_id_;
    SyncPosixMountNamespaceAuthority mount_namespace_authority_;
    std::filesystem::path path_;
    std::string path_text_;
    int descriptor_ = -1;
    SyncDirectoryAttestation attestation_;
    SyncPosixDirectoryResolutionCapability resolution_capability_ =
        SyncPosixDirectoryResolutionCapability::DeviceIdentityOnly;
    SyncPosixMountIdentity mount_identity_;
    mutable bool revoked_ = false;
};

// Stable canonical digest of the frozen authority observations. Callers should
// bind the absolute path separately when path spelling is itself durable
// identity. This digest intentionally includes effective credentials and mount
// observations, so a restart under changed authority fails closed.
[[nodiscard]] std::string sync_directory_attestation_digest_or_throw(
    const SyncDirectoryAttestation& attestation);

}  // namespace anonsync

#endif
