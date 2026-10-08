#pragma once

#if !defined(_WIN32)

#include "sync_directory_authority.hpp"

#include <string>
#include <string_view>

namespace anonsync::sync_directory_authority_detail {

// Internal bridge for owners that must issue descriptor-relative syscalls
// against a fully re-proved SyncDirectoryAuthority. The duplicate owns a new
// descriptor number but intentionally refers to the authority's existing open
// file description: file offsets and status flags are shared. It is therefore
// suitable for openat/fstatat-style traversal, not for an independently
// positioned fdopendir/readdir observation.
class SyncDirectorySharedOpenDescriptionLease final {
public:
    SyncDirectorySharedOpenDescriptionLease() noexcept = default;
    ~SyncDirectorySharedOpenDescriptionLease() noexcept;

    SyncDirectorySharedOpenDescriptionLease(
        const SyncDirectorySharedOpenDescriptionLease&) = delete;
    SyncDirectorySharedOpenDescriptionLease& operator=(
        const SyncDirectorySharedOpenDescriptionLease&) = delete;
    SyncDirectorySharedOpenDescriptionLease(
        SyncDirectorySharedOpenDescriptionLease&& other) noexcept;
    SyncDirectorySharedOpenDescriptionLease& operator=(
        SyncDirectorySharedOpenDescriptionLease&& other) noexcept;

    [[nodiscard]] int descriptor() const noexcept { return descriptor_; }
    [[nodiscard]] int release_descriptor() noexcept;
    [[nodiscard]] SyncPosixDirectoryResolutionCapability
    resolution_capability() const noexcept {
        return resolution_capability_;
    }
    [[nodiscard]] const SyncPosixMountIdentity& mount_identity() const noexcept {
        return mount_identity_;
    }

private:
    friend class SyncDirectoryAuthorityAccess;

    SyncDirectorySharedOpenDescriptionLease(
        int descriptor,
        SyncPosixDirectoryResolutionCapability resolution_capability,
        SyncPosixMountIdentity mount_identity) noexcept;

    void reset_noexcept() noexcept;

    int descriptor_ = -1;
    SyncPosixDirectoryResolutionCapability resolution_capability_ =
        SyncPosixDirectoryResolutionCapability::DeviceIdentityOnly;
    SyncPosixMountIdentity mount_identity_;
};

class SyncDirectoryAuthorityAccess final {
public:
    // Cheap capability-owner proof for internal process-local state that must
    // never be touched from a foreign thread. Unlike verify_or_throw(), this
    // does not re-open or stat the filesystem path; callers must still perform
    // a complete authority proof before issuing descriptor-relative effects.
    static void require_current_owner_or_throw(
        const SyncDirectoryAuthority& authority,
        std::string_view label);

    [[nodiscard]] static SyncDirectorySharedOpenDescriptionLease
    duplicate_shared_open_description_or_throw(
        const SyncDirectoryAuthority& authority,
        const std::string& label);
};

}  // namespace anonsync::sync_directory_authority_detail

#endif
