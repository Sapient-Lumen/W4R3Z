#include "sync_directory_authority_internal.hpp"

#include "sha256_digest.hpp"

#if !defined(_WIN32)

#include <array>
#include <cerrno>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <fcntl.h>
#include <stdexcept>
#include <string>
#include <utility>

#include <sys/stat.h>
#include <sys/statvfs.h>
#include <sys/types.h>
#include <unistd.h>

namespace anonsync {

namespace sync_directory_authority_detail {

SyncDirectorySharedOpenDescriptionLease::
    SyncDirectorySharedOpenDescriptionLease(
        int descriptor,
        SyncPosixDirectoryResolutionCapability resolution_capability,
        SyncPosixMountIdentity mount_identity) noexcept
    : descriptor_(descriptor),
      resolution_capability_(resolution_capability),
      mount_identity_(mount_identity) {}

SyncDirectorySharedOpenDescriptionLease::
    ~SyncDirectorySharedOpenDescriptionLease() noexcept {
    reset_noexcept();
}

SyncDirectorySharedOpenDescriptionLease::
    SyncDirectorySharedOpenDescriptionLease(
        SyncDirectorySharedOpenDescriptionLease&& other) noexcept
    : descriptor_(other.release_descriptor()),
      resolution_capability_(other.resolution_capability_),
      mount_identity_(other.mount_identity_) {}

SyncDirectorySharedOpenDescriptionLease&
SyncDirectorySharedOpenDescriptionLease::operator=(
    SyncDirectorySharedOpenDescriptionLease&& other) noexcept {
    if (this != &other) {
        reset_noexcept();
        descriptor_ = other.release_descriptor();
        resolution_capability_ = other.resolution_capability_;
        mount_identity_ = other.mount_identity_;
    }
    return *this;
}

int SyncDirectorySharedOpenDescriptionLease::release_descriptor() noexcept {
    const int out = descriptor_;
    descriptor_ = -1;
    return out;
}

void SyncDirectorySharedOpenDescriptionLease::reset_noexcept() noexcept {
    if (descriptor_ >= 0) (void)::close(descriptor_);
    descriptor_ = -1;
}

void SyncDirectoryAuthorityAccess::require_current_owner_or_throw(
    const SyncDirectoryAuthority& authority,
    std::string_view label) {
    authority.require_current_owner_or_throw(label);
}

SyncDirectorySharedOpenDescriptionLease
SyncDirectoryAuthorityAccess::duplicate_shared_open_description_or_throw(
    const SyncDirectoryAuthority& authority,
    const std::string& label) {
    authority.verify_or_throw(
        label + " root authority before descriptor duplication");
    const int source = authority.descriptor_no_verify();
    if (source < 0) {
        throw std::logic_error(
            label + " root authority descriptor is absent");
    }

#ifdef F_DUPFD_CLOEXEC
    int duplicate;
    do {
        duplicate = ::fcntl(source, F_DUPFD_CLOEXEC, 0);
    } while (duplicate < 0 && errno == EINTR);
#else
    int duplicate;
    do {
        duplicate = ::dup(source);
    } while (duplicate < 0 && errno == EINTR);
#endif
    if (duplicate < 0) {
        const int error = errno;
        throw std::runtime_error(
            label + " root authority descriptor duplication failed: " +
            std::strerror(error));
    }

    SyncDirectorySharedOpenDescriptionLease lease(
        duplicate, authority.resolution_capability_no_verify(),
        authority.mount_identity_no_verify());
#ifndef F_DUPFD_CLOEXEC
    const int old_flags = ::fcntl(lease.descriptor(), F_GETFD);
    if (old_flags < 0 ||
        ::fcntl(lease.descriptor(), F_SETFD, old_flags | FD_CLOEXEC) != 0) {
        const int error = errno;
        throw std::runtime_error(
            label + " duplicated root close-on-exec setup failed: " +
            std::strerror(error));
    }
#endif
    authority.verify_or_throw(
        label + " root authority after descriptor duplication");
    return lease;
}

}  // namespace sync_directory_authority_detail

namespace {

namespace fs = std::filesystem;

class ScopedFd final {
public:
    ScopedFd() noexcept = default;
    explicit ScopedFd(int descriptor) noexcept : descriptor_(descriptor) {}
    ~ScopedFd() { reset(); }
    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;
    ScopedFd(ScopedFd&& other) noexcept : descriptor_(other.release()) {}
    ScopedFd& operator=(ScopedFd&& other) noexcept {
        if (this != &other) reset(other.release());
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return descriptor_; }
    [[nodiscard]] int release() noexcept {
        const int out = descriptor_;
        descriptor_ = -1;
        return out;
    }
    void reset(int descriptor = -1) noexcept {
        if (descriptor_ >= 0) (void)::close(descriptor_);
        descriptor_ = descriptor;
    }

private:
    int descriptor_ = -1;
};

[[noreturn]] void throw_errno(const std::string& label,
                              const std::string& operation,
                              const fs::path& path,
                              int error_number = errno) {
    throw std::runtime_error(label + " " + operation + " failed for " +
                             path.generic_string() + ": " +
                             std::strerror(error_number));
}

[[nodiscard]] std::uint64_t unsigned_value(unsigned long long value) noexcept {
    return static_cast<std::uint64_t>(value);
}

[[nodiscard]] std::uint64_t device_value(
    const struct stat& status) noexcept {
    return unsigned_value(static_cast<unsigned long long>(status.st_dev));
}

[[nodiscard]] std::uint64_t inode_value(
    const struct stat& status) noexcept {
    return unsigned_value(static_cast<unsigned long long>(status.st_ino));
}

[[nodiscard]] std::uint64_t uid_value(uid_t value) noexcept {
    return unsigned_value(static_cast<unsigned long long>(value));
}

[[nodiscard]] std::uint64_t gid_value(gid_t value) noexcept {
    return unsigned_value(static_cast<unsigned long long>(value));
}

struct TraversedDirectory final {
    ScopedFd descriptor;
    struct stat identity {};
};

[[nodiscard]] TraversedDirectory traverse_directory_or_throw(
    const fs::path& absolute_directory,
    const std::string& label) {
    if (!absolute_directory.is_absolute()) {
        throw std::logic_error(
            label + " traversal requires an absolute directory");
    }

    SyncPosixOpenedDirectory root =
        sync_posix_open_filesystem_root_directory_or_throw(label);
    ScopedFd current(root.descriptor);
    struct stat current_status = root.status;

    fs::path walked = "/";
    for (const fs::path& component_path : absolute_directory.relative_path()) {
        const std::string component = component_path.string();
        if (component.empty() || component == ".") continue;
        walked /= component_path;

        SyncPosixOpenedDirectory opened =
            sync_posix_open_directory_component_or_throw(
                current.get(), component, walked,
                SyncPosixDirectoryComponentRole::AbsoluteParent,
                SyncPosixDirectoryMountPolicy::AllowMountCrossing,
                SyncPosixDirectoryResolutionCapability::DeviceIdentityOnly,
                {}, label);
        ScopedFd next(opened.descriptor);
        current = std::move(next);
        current_status = opened.status;
    }

    TraversedDirectory out;
    out.descriptor = std::move(current);
    out.identity = current_status;
    return out;
}

[[nodiscard]] long query_name_maximum_or_throw(int descriptor,
                                                const std::string& label,
                                                const fs::path& path) {
    errno = 0;
    const long value = ::fpathconf(descriptor, _PC_NAME_MAX);
    if (value < 0 && errno != 0) {
        throw_errno(label, "NAME_MAX query", path);
    }
    return value;
}

[[nodiscard]] SyncDirectoryAttestation capture_attestation_or_throw(
    int descriptor,
    const struct stat& status,
    const std::string& label,
    const fs::path& path) {
    struct statvfs filesystem {};
    if (::fstatvfs(descriptor, &filesystem) != 0) {
        throw_errno(label, "filesystem attestation", path);
    }

    SyncDirectoryAttestation out;
    out.device = device_value(status);
    out.inode = inode_value(status);
    out.owner_user_id = uid_value(status.st_uid);
    out.owner_group_id = gid_value(status.st_gid);
    out.effective_user_id = uid_value(::geteuid());
    out.effective_group_id = gid_value(::getegid());
    out.permission_mode = static_cast<std::uint32_t>(status.st_mode & 07777U);
    out.filesystem_id =
        unsigned_value(static_cast<unsigned long long>(filesystem.f_fsid));
    out.mount_flags =
        unsigned_value(static_cast<unsigned long long>(filesystem.f_flag));
    out.filesystem_name_maximum = unsigned_value(
        static_cast<unsigned long long>(filesystem.f_namemax));
    out.path_name_maximum =
        query_name_maximum_or_throw(descriptor, label, path);
    return out;
}

void require_owner_controlled_mutation_surface_or_throw(
    const SyncDirectoryAttestation& attestation,
    const std::string& label,
    const fs::path& path) {
    if (attestation.owner_user_id != attestation.effective_user_id) {
        throw std::runtime_error(
            label + " owner does not match the effective user for " +
            path.generic_string());
    }
    const auto mode = static_cast<mode_t>(attestation.permission_mode);
    if ((mode & (S_IRUSR | S_IWUSR | S_IXUSR)) !=
        (S_IRUSR | S_IWUSR | S_IXUSR)) {
        throw std::runtime_error(
            label + " owner read/write/search permission is required for " +
            path.generic_string());
    }
    if ((mode & (S_IWGRP | S_IWOTH)) != 0) {
        throw std::runtime_error(
            label + " refuses a group/other-writable directory: " +
            path.generic_string());
    }
#ifdef ST_RDONLY
    if ((attestation.mount_flags & static_cast<std::uint64_t>(ST_RDONLY)) != 0) {
        throw std::runtime_error(label + " refuses a read-only mount: " +
                                 path.generic_string());
    }
#endif
}

[[nodiscard]] bool same_attestation(
    const SyncDirectoryAttestation& left,
    const SyncDirectoryAttestation& right) noexcept {
    return left.device == right.device && left.inode == right.inode &&
           left.owner_user_id == right.owner_user_id &&
           left.owner_group_id == right.owner_group_id &&
           left.effective_user_id == right.effective_user_id &&
           left.effective_group_id == right.effective_group_id &&
           left.permission_mode == right.permission_mode &&
           left.filesystem_id == right.filesystem_id &&
           left.mount_flags == right.mount_flags &&
           left.filesystem_name_maximum == right.filesystem_name_maximum &&
           left.path_name_maximum == right.path_name_maximum;
}

}  // namespace

SyncDirectoryAuthority::~SyncDirectoryAuthority() {
    require_current_owner_noexcept();
    if (descriptor_ >= 0) (void)::close(descriptor_);
}

SyncDirectoryAuthority::SyncDirectoryAuthority(
    SyncDirectoryAuthority&& other) noexcept {
    other.require_current_owner_noexcept();
    transfer_from_noexcept(other);
}

SyncDirectoryAuthority&
SyncDirectoryAuthority::operator=(
    SyncDirectoryAuthority&& other) noexcept {
    require_current_owner_noexcept();
    other.require_current_owner_noexcept();
    if (this == &other) return *this;
    if (descriptor_ >= 0) (void)::close(descriptor_);
    transfer_from_noexcept(other);
    return *this;
}

SyncDirectoryAuthority
SyncDirectoryAuthority::open_or_throw(
    const fs::path& raw_absolute_directory,
    const std::string& label) {
    if (raw_absolute_directory.empty() ||
        !raw_absolute_directory.is_absolute()) {
        throw std::runtime_error(label + " path must be absolute");
    }
    for (const fs::path& component : raw_absolute_directory) {
        if (component == "..") {
            throw std::runtime_error(
                label + " path must not contain a parent traversal component");
        }
    }
    const fs::path absolute_directory =
        raw_absolute_directory.lexically_normal();
    if (!absolute_directory.is_absolute()) {
        throw std::runtime_error(label + " normalized path must be absolute");
    }

    SyncDirectoryAuthority out;
    out.process_id_ = current_sync_process_incarnation_noexcept();
    out.thread_id_ = current_sync_thread_incarnation_noexcept();
    // Bind the authority to the calling thread's mount namespace before any
    // pathname traversal. A later setns()/unshare() must not let a descriptor
    // captured in one namespace authorize traversal in another.
    out.mount_namespace_authority_ =
        SyncPosixMountNamespaceAuthority::capture_or_throw(
            label + " mount namespace");
    out.path_ = absolute_directory;
    out.path_text_ = absolute_directory.generic_string();

    TraversedDirectory traversed =
        traverse_directory_or_throw(absolute_directory, label);
    out.descriptor_ = traversed.descriptor.release();
    out.attestation_ = capture_attestation_or_throw(
        out.descriptor_, traversed.identity, label, out.path_);
    require_owner_controlled_mutation_surface_or_throw(
        out.attestation_, label, out.path_);
    out.resolution_capability_ =
        sync_posix_probe_directory_resolution_capability_or_throw(
            out.descriptor_, label + " resolution capability");
    out.mount_identity_ = sync_posix_capture_mount_identity_or_throw(
        out.descriptor_, out.resolution_capability_,
        label + " retained mount identity");
    out.verify_or_throw(label + " initial proof");
    return out;
}

void SyncDirectoryAuthority::require_current_owner_noexcept()
    const noexcept {
    if (process_id_.valid() &&
        !sync_process_incarnation_is_current(process_id_)) {
        fail_stop_on_sync_process_capability_violation_noexcept();
    }
    if (thread_id_.valid() &&
        !sync_thread_incarnation_is_current(thread_id_)) {
        fail_stop_on_sync_thread_capability_violation_noexcept();
    }
}

void SyncDirectoryAuthority::require_current_owner_or_throw(
    std::string_view label) const {
    if (!process_id_.valid()) {
        throw std::logic_error(std::string(label) +
                               " directory authority is not initialized");
    }
    require_sync_process_incarnation_or_fail_stop(process_id_, label);
    require_sync_thread_incarnation_or_throw(thread_id_, label);
}

void SyncDirectoryAuthority::transfer_from_noexcept(
    SyncDirectoryAuthority& other) noexcept {
    process_id_ = other.process_id_;
    thread_id_ = other.thread_id_;
    mount_namespace_authority_ =
        std::move(other.mount_namespace_authority_);
    path_ = std::move(other.path_);
    path_text_ = std::move(other.path_text_);
    descriptor_ = other.descriptor_;
    attestation_ = other.attestation_;
    resolution_capability_ = other.resolution_capability_;
    mount_identity_ = other.mount_identity_;
    revoked_ = other.revoked_;
    other.clear_moved_from_noexcept();
}

void SyncDirectoryAuthority::clear_moved_from_noexcept() noexcept {
    process_id_ = {};
    thread_id_ = {};
    mount_namespace_authority_ = {};
    path_.clear();
    path_text_.clear();
    descriptor_ = -1;
    attestation_ = {};
    resolution_capability_ =
        SyncPosixDirectoryResolutionCapability::DeviceIdentityOnly;
    mount_identity_ = {};
    revoked_ = false;
}

const fs::path& SyncDirectoryAuthority::path() const noexcept {
    require_current_owner_noexcept();
    return path_;
}

const std::string& SyncDirectoryAuthority::absolute_path() const
    noexcept {
    require_current_owner_noexcept();
    return path_text_;
}

const SyncDirectoryAttestation&
SyncDirectoryAuthority::attestation() const noexcept {
    require_current_owner_noexcept();
    return attestation_;
}

SyncPosixDirectoryResolutionCapability
SyncDirectoryAuthority::resolution_capability() const noexcept {
    require_current_owner_noexcept();
    return resolution_capability_;
}

const SyncPosixMountNamespaceIdentity&
SyncDirectoryAuthority::mount_namespace_identity() const noexcept {
    require_current_owner_noexcept();
    return mount_namespace_authority_.identity();
}

void SyncDirectoryAuthority::verify_or_throw(
    std::string_view label_view) const {
    const std::string label(label_view);
    require_current_owner_or_throw(label);
    if (revoked_) {
        throw std::runtime_error(label + " directory authority is revoked");
    }

    try {
        // Descendant resolution can change after setns()/unshare() even while
        // the retained root descriptor and inode remain exact. Reprove the
        // calling thread's namespace first and revoke this object on mismatch.
        mount_namespace_authority_.verify_or_throw(
            label + " mount namespace");
        if (descriptor_ < 0) {
            throw std::logic_error(label + " retained descriptor is absent");
        }

        struct stat retained_status {};
        if (::fstat(descriptor_, &retained_status) != 0) {
            throw_errno(label, "retained directory fstat", path_);
        }
        if (!S_ISDIR(retained_status.st_mode)) {
            throw std::runtime_error(
                label + " retained object is not a directory");
        }
        const SyncDirectoryAttestation retained =
            capture_attestation_or_throw(
                descriptor_, retained_status, label + " retained", path_);
        require_owner_controlled_mutation_surface_or_throw(
            retained, label + " retained", path_);
        if (!same_attestation(attestation_, retained)) {
            throw std::runtime_error(
                label + " retained directory attestation changed");
        }
        sync_posix_verify_directory_resolution_capability_or_throw(
            descriptor_, resolution_capability_,
            label + " retained resolution capability");
        const SyncPosixMountIdentity retained_mount =
            sync_posix_capture_mount_identity_or_throw(
                descriptor_, resolution_capability_,
                label + " retained mount identity");
        if (retained_mount != mount_identity_) {
            throw std::runtime_error(
                label + " retained directory mount identity changed");
        }

        const TraversedDirectory current =
            traverse_directory_or_throw(path_, label + " path");
        const SyncDirectoryAttestation reached =
            capture_attestation_or_throw(current.descriptor.get(),
                                         current.identity,
                                         label + " path",
                                         path_);
        require_owner_controlled_mutation_surface_or_throw(
            reached, label + " path", path_);
        const SyncPosixMountIdentity reached_mount =
            sync_posix_capture_mount_identity_or_throw(
                current.descriptor.get(), resolution_capability_,
                label + " path mount identity");
        if (reached_mount != mount_identity_) {
            throw std::runtime_error(
                label + " path crossed or changed mount identity: " +
                path_.generic_string());
        }
        if (!same_attestation(attestation_, reached)) {
            if (attestation_.device != reached.device ||
                attestation_.inode != reached.inode) {
                throw std::runtime_error(
                    label +
                    " path no longer names the retained directory: " +
                    path_.generic_string());
            }
            throw std::runtime_error(
                label + " path directory attestation changed");
        }
    } catch (...) {
        revoked_ = true;
        throw;
    }
}

int SyncDirectoryAuthority::descriptor_no_verify() const noexcept {
    require_current_owner_noexcept();
    return descriptor_;
}

long SyncDirectoryAuthority::name_maximum_no_verify() const
    noexcept {
    require_current_owner_noexcept();
    return attestation_.path_name_maximum;
}

SyncPosixDirectoryResolutionCapability
SyncDirectoryAuthority::resolution_capability_no_verify() const noexcept {
    require_current_owner_noexcept();
    return resolution_capability_;
}

const SyncPosixMountIdentity&
SyncDirectoryAuthority::mount_identity_no_verify() const noexcept {
    require_current_owner_noexcept();
    return mount_identity_;
}


std::string sync_directory_attestation_digest_or_throw(
    const SyncDirectoryAttestation& attestation) {
    auto big_endian_u64 = [](std::uint64_t value) {
        std::array<char, 8U> bytes{};
        for (std::size_t index = bytes.size(); index != 0U; --index) {
            bytes[index - 1U] = static_cast<char>(value & 0xffU);
            value >>= 8U;
        }
        return bytes;
    };
    auto append_u64 = [&big_endian_u64](Sha256DigestBuilder& digest,
                                        std::uint64_t value) {
        const auto bytes = big_endian_u64(value);
        digest.update(std::string_view(bytes.data(), bytes.size()));
    };

    Sha256DigestBuilder digest;
    digest.update("anonsync-sync-directory-attestation-v1");
    append_u64(digest, attestation.device);
    append_u64(digest, attestation.inode);
    append_u64(digest, attestation.owner_user_id);
    append_u64(digest, attestation.owner_group_id);
    append_u64(digest, attestation.effective_user_id);
    append_u64(digest, attestation.effective_group_id);
    append_u64(digest, attestation.permission_mode);
    append_u64(digest, attestation.filesystem_id);
    append_u64(digest, attestation.mount_flags);
    append_u64(digest, attestation.filesystem_name_maximum);
    append_u64(digest,
               static_cast<std::uint64_t>(attestation.path_name_maximum));
    return digest.finish_hex();
}

}  // namespace anonsync

#endif
