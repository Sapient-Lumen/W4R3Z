#include "sync_replica_file_payload_store.hpp"

#if !defined(_WIN32)

#include "sha256_digest.hpp"
#include "sync_atomic_file_publication.hpp"
#include "sync_directory_authority.hpp"
#include "sync_directory_authority_internal.hpp"
#include "sync_manifest_validation.hpp"
#include "sync_posix_descriptor_snapshot.hpp"
#include "sync_posix_directory_resolution.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <dirent.h>
#include <exception>
#include <fcntl.h>
#include <limits>
#include <memory>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>
#include <utility>
#include <vector>

#include <sys/file.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

namespace anonsync {
namespace {

namespace fs = std::filesystem;

constexpr std::string_view kSnapshotDigestDomain =
    "anonsync:sync-replica-file-payload-store-snapshot:v3";
constexpr std::string_view kStandaloneStoreIdentityBasenameV2 =
    ".anonsync-payload-store-identity-v2";
constexpr std::string_view kProductStoreIdentityBasenameV3 =
    ".anonsync-payload-store-identity-v3";
constexpr std::string_view kLegacyStoreIdentityBasenameV1 =
    ".anonsync-payload-store-identity-v1";
constexpr std::string_view kStandaloneStoreIdentityDomainV2 =
    "anonsync:sync-replica-file-payload-store-identity:v2";
constexpr std::string_view kProductStoreIdentityDomainV3 =
    "anonsync:sync-replica-file-payload-store-identity:v3";
constexpr std::string_view kStoreLeaseProtocol =
    "anonsync:sync-replica-file-payload-store-flock-lease:v1";
constexpr std::uint64_t kMaximumPersistentInteger =
    static_cast<std::uint64_t>(std::numeric_limits<std::int64_t>::max());

class OwnedFd final {
public:
    explicit OwnedFd(int descriptor = -1) noexcept
        : descriptor_(descriptor) {}
    ~OwnedFd() { reset(); }
    OwnedFd(const OwnedFd&) = delete;
    OwnedFd& operator=(const OwnedFd&) = delete;
    OwnedFd(OwnedFd&& other) noexcept
        : descriptor_(other.release()) {}
    OwnedFd& operator=(OwnedFd&& other) noexcept {
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

class OwnedDirectoryStream final {
public:
    explicit OwnedDirectoryStream(DIR* stream = nullptr) noexcept
        : stream_(stream) {}
    ~OwnedDirectoryStream() {
        if (stream_ != nullptr) (void)::closedir(stream_);
    }
    OwnedDirectoryStream(const OwnedDirectoryStream&) = delete;
    OwnedDirectoryStream& operator=(const OwnedDirectoryStream&) = delete;

    [[nodiscard]] DIR* get() const noexcept { return stream_; }

private:
    DIR* stream_ = nullptr;
};

struct PayloadIndexEntry final {
    std::string content_sha256;
    std::uint64_t size_bytes = 0U;
};

struct ScannedPayloadIndex final {
    std::vector<PayloadIndexEntry> entries;
    std::uint64_t indexed_bytes = 0U;
    std::uint64_t transient_entry_count = 0U;
    std::uint64_t transient_bytes = 0U;
    bool identity_present = false;
};

class StoreLease final {
public:
    StoreLease(
        OwnedFd root_descriptor,
        OwnedFd identity_descriptor,
        struct stat identity_status,
        SyncDirectoryAttestation root_attestation,
        std::string identity_basename,
        std::string expected_identity,
        SyncReplicaFilePayloadStoreLeaseMode mode) noexcept
        : root_descriptor_(std::move(root_descriptor)),
          identity_descriptor_(std::move(identity_descriptor)),
          identity_status_(identity_status),
          root_attestation_(root_attestation),
          identity_basename_(std::move(identity_basename)),
          expected_identity_(std::move(expected_identity)),
          mode_(mode) {}
    StoreLease(const StoreLease&) = delete;
    StoreLease& operator=(const StoreLease&) = delete;
    StoreLease(StoreLease&&) noexcept = default;
    StoreLease& operator=(StoreLease&&) noexcept = default;
    ~StoreLease() noexcept = default;

    void verify_or_throw(
        const SyncDirectoryAuthority& root_authority,
        const std::string& label) const;

    [[nodiscard]] SyncReplicaFilePayloadStoreLeaseMode mode() const noexcept {
        return mode_;
    }

private:
    // flock(2) locks are released with the final close of the independently
    // opened identity file description. Retaining the exact root descriptor,
    // identity inode, and bytes lets every protected scan re-prove that the
    // pathname still names the locked anchor rather than an identical
    // replacement inode. Both descriptors remain CLOEXEC through the shared
    // resolvers.
    OwnedFd root_descriptor_;
    OwnedFd identity_descriptor_;
    struct stat identity_status_ {};
    SyncDirectoryAttestation root_attestation_;
    std::string identity_basename_;
    std::string expected_identity_;
    SyncReplicaFilePayloadStoreLeaseMode mode_ =
        SyncReplicaFilePayloadStoreLeaseMode::SharedObservation;
};

struct VerifiedStoreIdentityFile final {
    OwnedFd descriptor;
    struct stat status {};
};

[[nodiscard]] std::string error_text(int error_number) {
    return std::error_code(error_number, std::generic_category()).message();
}

[[nodiscard]] std::uint64_t size_to_u64_or_throw(
    std::size_t value,
    const std::string& label) {
    if constexpr (sizeof(std::size_t) > sizeof(std::uint64_t)) {
        if (value > std::numeric_limits<std::uint64_t>::max()) {
            throw std::overflow_error(label + " size exceeds uint64 range");
        }
    }
    return static_cast<std::uint64_t>(value);
}

[[nodiscard]] std::span<const unsigned char> byte_span(
    const std::string& bytes) noexcept {
    return {reinterpret_cast<const unsigned char*>(bytes.data()), bytes.size()};
}

[[nodiscard]] std::string standalone_store_identity_payload(
    std::string_view folder_id) {
    std::string payload;
    payload.reserve(
        kStandaloneStoreIdentityDomainV2.size() + folder_id.size() +
        kStoreLeaseProtocol.size() + 3U);
    payload.append(kStandaloneStoreIdentityDomainV2);
    payload.push_back('\n');
    payload.append(folder_id);
    payload.push_back('\n');
    payload.append(kStoreLeaseProtocol);
    payload.push_back('\n');
    return payload;
}

void append_u64(Sha256DigestBuilder& digest, std::uint64_t value) {
    std::array<char, 8U> bytes{};
    for (std::size_t index = bytes.size(); index != 0U; --index) {
        bytes[index - 1U] = static_cast<char>(value & 0xffU);
        value >>= 8U;
    }
    digest.update(std::string_view(bytes.data(), bytes.size()));
}

void append_string(Sha256DigestBuilder& digest, std::string_view value) {
    if (value.size() > std::numeric_limits<std::uint64_t>::max()) {
        throw std::overflow_error(
            "durable payload store digest field exceeds uint64 range");
    }
    append_u64(digest, static_cast<std::uint64_t>(value.size()));
    digest.update(value);
}

void append_framed_marker_field(
    std::string& output,
    std::string_view value) {
    output.append(std::to_string(value.size()));
    output.push_back(':');
    output.append(value);
}

[[nodiscard]] std::string product_store_identity_payload_or_throw(
    const SyncReplicaDeploymentIdentity& identity,
    const std::string& label) {
    validate_sync_replica_deployment_identity_or_throw(identity, label);
    std::string payload;
    payload.reserve(
        kProductStoreIdentityDomainV3.size() +
        identity.deployment_id.size() + identity.manifest_digest.size() +
        identity.manifest_path.generic_string().size() +
        identity.folder_id.size() + identity.local_actor.device_id.size() +
        kStoreLeaseProtocol.size() + 192U);
    payload.append(kProductStoreIdentityDomainV3);
    payload.push_back('\n');
    append_framed_marker_field(payload, identity.deployment_id);
    append_framed_marker_field(payload, identity.manifest_digest);
    append_framed_marker_field(
        payload, identity.manifest_path.generic_string());
    append_framed_marker_field(payload, identity.folder_id);
    append_framed_marker_field(payload, identity.local_actor.device_id);
    append_framed_marker_field(
        payload, std::to_string(identity.local_actor.epoch));
    append_framed_marker_field(payload, kStoreLeaseProtocol);
    return payload;
}

[[nodiscard]] bool same_identity(
    const struct stat& left,
    const struct stat& right) noexcept {
    return left.st_dev == right.st_dev && left.st_ino == right.st_ino;
}

[[nodiscard]] bool same_timespec(
    const timespec& left,
    const timespec& right) noexcept {
    return left.tv_sec == right.tv_sec && left.tv_nsec == right.tv_nsec;
}

[[nodiscard]] bool same_directory_observation(
    const struct stat& left,
    const struct stat& right) noexcept {
    const bool common =
        same_identity(left, right) && left.st_mode == right.st_mode &&
        left.st_nlink == right.st_nlink && left.st_uid == right.st_uid &&
        left.st_gid == right.st_gid && left.st_size == right.st_size;
#if defined(__APPLE__)
    return common && same_timespec(left.st_mtimespec, right.st_mtimespec) &&
           same_timespec(left.st_ctimespec, right.st_ctimespec);
#elif defined(__linux__) || defined(__FreeBSD__) || defined(__NetBSD__) || \
    defined(__OpenBSD__)
    return common && same_timespec(left.st_mtim, right.st_mtim) &&
           same_timespec(left.st_ctim, right.st_ctim);
#else
    return common && left.st_mtime == right.st_mtime &&
           left.st_ctime == right.st_ctime;
#endif
}

void fsync_or_throw(int descriptor, const std::string& label) {
    int result;
    do {
        result = ::fsync(descriptor);
    } while (result != 0 && errno == EINTR);
    if (result != 0) {
        const int error = errno;
        throw std::runtime_error(label + " synchronization failed: " +
                                 error_text(error));
    }
}

void require_private_regular_file_or_throw(
    const struct stat& status,
    const SyncDirectoryAttestation& root_attestation,
    const std::string& label) {
    if (!S_ISREG(status.st_mode)) {
        throw std::runtime_error(label + " is not a regular file");
    }
    if (status.st_nlink != 1) {
        throw std::runtime_error(label + " is not a single-link file");
    }
    if (static_cast<std::uint64_t>(status.st_dev) !=
        root_attestation.device) {
        throw std::runtime_error(label + " is not on the retained root device");
    }
    if (static_cast<std::uint64_t>(status.st_uid) !=
        root_attestation.effective_user_id) {
        throw std::runtime_error(label + " is not owned by the effective user");
    }
    if ((status.st_mode & 07777U) != (S_IRUSR | S_IWUSR)) {
        throw std::runtime_error(label + " does not have exact mode 0600");
    }
    if (status.st_size < 0) {
        throw std::runtime_error(label + " has a negative size");
    }
}

void verify_named_regular_file_or_throw(
    int directory_descriptor,
    std::string_view basename,
    const struct stat& expected,
    const SyncDirectoryAttestation& root_attestation,
    const std::string& label) {
    const std::string name(basename);
    struct stat observed{};
    int result;
    do {
        result = ::fstatat(directory_descriptor, name.c_str(), &observed,
                           AT_SYMLINK_NOFOLLOW);
    } while (result != 0 && errno == EINTR);
    if (result != 0) {
        const int error = errno;
        throw std::runtime_error(label + " final namespace inspection failed: " +
                                 error_text(error));
    }
    require_private_regular_file_or_throw(
        observed, root_attestation, label + " final namespace entry");
    if (!same_identity(expected, observed) ||
        expected.st_size != observed.st_size ||
        expected.st_mode != observed.st_mode ||
        expected.st_nlink != observed.st_nlink ||
        expected.st_uid != observed.st_uid) {
        throw std::runtime_error(
            label + " namespace entry changed during validation");
    }
}

[[nodiscard]] SyncPosixOpenedRegularFile open_store_file_or_throw(
    int directory_descriptor,
    std::string_view basename,
    const fs::path& root_path,
    SyncPosixDirectoryResolutionCapability capability,
    const SyncPosixMountIdentity& mount_identity,
    const std::string& label) {
    return sync_posix_open_regular_file_component_or_throw(
        directory_descriptor, basename, root_path / std::string(basename),
        SyncPosixDirectoryMountPolicy::RequireRetainedRootMount,
        capability, mount_identity, label);
}

[[nodiscard]] SyncDirectoryAuthority
reopen_matching_root_authority_or_throw(
    const SyncDirectoryAuthority& retained,
    const std::string& label) {
    retained.verify_or_throw(label + " retained root pre-open proof");
    SyncDirectoryAuthority reopened = SyncDirectoryAuthority::open_or_throw(
        retained.path(), label + " reopened root");
    retained.verify_or_throw(label + " retained root post-open proof");
    const std::string retained_digest =
        sync_directory_attestation_digest_or_throw(retained.attestation());
    const std::string reopened_digest =
        sync_directory_attestation_digest_or_throw(reopened.attestation());
    if (reopened.path() != retained.path() ||
        reopened_digest != retained_digest ||
        reopened.resolution_capability() != retained.resolution_capability() ||
        reopened.mount_namespace_identity() !=
            retained.mount_namespace_identity()) {
        throw std::runtime_error(
            label + " reopened root does not match retained store authority");
    }
    return reopened;
}

void verify_open_store_identity_or_throw(
    int directory_descriptor,
    int identity_descriptor,
    const struct stat& opened_status,
    const SyncDirectoryAttestation& root_attestation,
    std::string_view identity_basename,
    std::string_view expected_identity,
    const std::string& label) {
    require_private_regular_file_or_throw(
        opened_status, root_attestation, label);
    if (static_cast<std::uint64_t>(opened_status.st_size) !=
        expected_identity.size()) {
        throw std::runtime_error(label + " does not bind this folder");
    }
    FrozenSyncPosixRegularFileSnapshot frozen =
        FrozenSyncPosixRegularFileSnapshot::freeze_borrowed_descriptor_or_throw(
            identity_descriptor, expected_identity.size(),
            SyncPosixDescriptorLinkPolicy::exactly_one, label);
    if (frozen.bytes() != expected_identity) {
        throw std::runtime_error(label + " does not bind this folder");
    }
    fsync_or_throw(identity_descriptor, label);
    verify_named_regular_file_or_throw(
        directory_descriptor, identity_basename, opened_status,
        root_attestation, label);
}

[[nodiscard]] VerifiedStoreIdentityFile
open_verified_store_identity_or_throw(
    int directory_descriptor,
    const fs::path& root_path,
    SyncPosixDirectoryResolutionCapability capability,
    const SyncPosixMountIdentity& mount_identity,
    const SyncDirectoryAttestation& root_attestation,
    std::string_view identity_basename,
    std::string_view expected_identity,
    const std::string& label) {
    SyncPosixOpenedRegularFile opened = open_store_file_or_throw(
        directory_descriptor, identity_basename, root_path, capability,
        mount_identity, label);
    VerifiedStoreIdentityFile identity{
        OwnedFd(opened.descriptor), opened.status};
    verify_open_store_identity_or_throw(
        directory_descriptor, identity.descriptor.get(), identity.status,
        root_attestation, identity_basename, expected_identity, label);
    return identity;
}

void StoreLease::verify_or_throw(
    const SyncDirectoryAuthority& root_authority,
    const std::string& label) const {
    if (root_descriptor_.get() < 0 || identity_descriptor_.get() < 0) {
        throw std::logic_error(label + " payload-store lease is inactive");
    }
    root_authority.verify_or_throw(label + " retained root pre-proof");
    if (root_authority.attestation() != root_attestation_) {
        throw std::runtime_error(
            label + " payload-store lease root attestation changed");
    }
    verify_open_store_identity_or_throw(
        root_descriptor_.get(), identity_descriptor_.get(), identity_status_,
        root_attestation_, identity_basename_, expected_identity_,
        label + " locked identity");
    root_authority.verify_or_throw(label + " retained root post-proof");
}

[[nodiscard]] bool flock_conflict_error(int error_number) noexcept {
    return error_number == EWOULDBLOCK || error_number == EAGAIN;
}

[[nodiscard]] const char* store_lease_mode_name(
    SyncReplicaFilePayloadStoreLeaseMode mode) noexcept {
    switch (mode) {
        case SyncReplicaFilePayloadStoreLeaseMode::SharedObservation:
            return "shared observation";
        case SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation:
            return "exclusive mutation";
    }
    return "unknown";
}

void acquire_flock_nonblocking_or_throw(
    int descriptor,
    int operation,
    SyncReplicaFilePayloadStoreLeaseMode mode,
    const std::string& label) {
    int result;
    do {
        result = ::flock(descriptor, operation | LOCK_NB);
    } while (result != 0 && errno == EINTR);
    if (result == 0) return;
    const int error = errno;
    if (flock_conflict_error(error)) {
        throw SyncReplicaFilePayloadStoreLeaseBusyError(
            mode,
            label + " payload-store " + store_lease_mode_name(mode) +
                " lease is busy");
    }
    throw std::runtime_error(
        label + " payload-store " + store_lease_mode_name(mode) +
        " lease acquisition failed: " + error_text(error));
}

[[nodiscard]] StoreLease acquire_store_lease_or_throw(
    const SyncDirectoryAuthority& root_authority,
    std::string_view identity_basename,
    std::string_view expected_identity,
    SyncReplicaFilePayloadStoreLeaseMode mode,
    const std::string& label) {
    using Access = sync_directory_authority_detail::
        SyncDirectoryAuthorityAccess;
    root_authority.verify_or_throw(label + " root pre-lease proof");
    auto root_lease =
        Access::duplicate_shared_open_description_or_throw(
            root_authority, label + " root");
    OwnedFd root_descriptor(root_lease.release_descriptor());
    const SyncDirectoryAttestation& root_attestation =
        root_authority.attestation();

    VerifiedStoreIdentityFile identity =
        open_verified_store_identity_or_throw(
            root_descriptor.get(), root_authority.path(),
            root_lease.resolution_capability(), root_lease.mount_identity(),
            root_attestation, identity_basename, expected_identity,
            label + " identity lock anchor");
    const int requested =
        mode == SyncReplicaFilePayloadStoreLeaseMode::SharedObservation
            ? LOCK_SH
            : LOCK_EX;
    acquire_flock_nonblocking_or_throw(
        identity.descriptor.get(), requested, mode, label);

    // A successful advisory lock is not promoted to authority until a second,
    // independently opened file description proves that the opposite lock is
    // rejected. This catches platforms/filesystems that collapse locks to
    // process ownership or otherwise fail to provide the required exclusion.
    VerifiedStoreIdentityFile conflict_probe =
        open_verified_store_identity_or_throw(
            root_descriptor.get(), root_authority.path(),
            root_lease.resolution_capability(), root_lease.mount_identity(),
            root_attestation, identity_basename, expected_identity,
            label + " independent lease conflict probe");
    const int conflicting =
        mode == SyncReplicaFilePayloadStoreLeaseMode::SharedObservation
            ? LOCK_EX
            : LOCK_SH;
    int probe_result;
    do {
        probe_result = ::flock(
            conflict_probe.descriptor.get(), conflicting | LOCK_NB);
    } while (probe_result != 0 && errno == EINTR);
    if (probe_result == 0) {
        (void)::flock(conflict_probe.descriptor.get(), LOCK_UN);
        throw std::runtime_error(
            label +
            " payload-store lease exclusion self-proof unexpectedly succeeded");
    }
    const int probe_error = errno;
    if (!flock_conflict_error(probe_error)) {
        throw std::runtime_error(
            label + " payload-store lease exclusion self-proof failed: " +
            error_text(probe_error));
    }

    StoreLease lease(
        std::move(root_descriptor), std::move(identity.descriptor),
        identity.status, root_attestation, std::string(identity_basename),
        std::string(expected_identity), mode);
    lease.verify_or_throw(
        root_authority, label + " identity lock anchor after exclusion proof");
    return lease;
}

[[nodiscard]] std::string snapshot_digest_or_throw(
    std::string_view folder_id,
    std::string_view root_path,
    std::string_view root_attestation_digest,
    std::string_view identity_basename,
    std::string_view expected_identity,
    const SyncReplicaFilePayloadStoreLimits& limits,
    std::uint64_t transient_entry_count,
    std::uint64_t transient_bytes,
    std::uint64_t indexed_bytes,
    const std::vector<PayloadIndexEntry>& entries) {
    Sha256DigestBuilder digest;
    append_string(digest, kSnapshotDigestDomain);
    append_string(digest, kStoreLeaseProtocol);
    append_string(digest, folder_id);
    append_string(digest, root_path);
    append_string(digest, root_attestation_digest);
    append_string(digest, identity_basename);
    append_string(digest, sha256_hex(std::string(expected_identity)));
    append_u64(digest, limits.max_entries);
    append_u64(digest, limits.max_payload_bytes);
    append_u64(digest, limits.max_indexed_bytes);
    append_u64(digest, limits.max_transient_entries);
    append_u64(digest, limits.max_transient_bytes);
    append_u64(digest, static_cast<std::uint64_t>(entries.size()));
    append_u64(digest, indexed_bytes);
    append_u64(digest, transient_entry_count);
    append_u64(digest, transient_bytes);
    for (const PayloadIndexEntry& entry : entries) {
        append_string(digest, entry.content_sha256);
        append_u64(digest, entry.size_bytes);
    }
    return digest.finish_hex();
}

// Raw namespace traversal. The only intentionally unleased caller is clean
// identity bootstrap before a stable lock anchor exists. Every ordinary
// observation and mutation must enter through scan_store_under_lease_or_throw.
[[nodiscard]] ScannedPayloadIndex scan_store_namespace_or_throw(
    const SyncDirectoryAuthority& root_authority,
    const SyncReplicaFilePayloadStoreLimits& limits,
    std::string_view identity_basename,
    std::string_view expected_identity,
    bool identity_required,
    const std::string& label) {
    using Access = sync_directory_authority_detail::
        SyncDirectoryAuthorityAccess;
    // dup/fcntl descriptors share one open-file-description directory offset.
    // fdopendir/readdir on a duplicate would therefore mutate the retained
    // authority's cursor and make a later scan begin at end-of-directory.
    // Reopen and attest an independent root before duplicating it into DIR.
    SyncDirectoryAuthority scan_authority =
        reopen_matching_root_authority_or_throw(
            root_authority, label + " independent cursor");
    auto descriptor_lease =
        Access::duplicate_shared_open_description_or_throw(
            scan_authority, label + " scan");
    OwnedFd root_descriptor(descriptor_lease.release_descriptor());

    struct stat directory_before{};
    if (::fstat(root_descriptor.get(), &directory_before) != 0) {
        const int error = errno;
        throw std::runtime_error(label + " initial root fstat failed: " +
                                 error_text(error));
    }
    if (!S_ISDIR(directory_before.st_mode)) {
        throw std::runtime_error(label + " retained root is not a directory");
    }

    DIR* raw_stream = ::fdopendir(root_descriptor.get());
    if (raw_stream == nullptr) {
        const int error = errno;
        throw std::runtime_error(label + " directory stream open failed: " +
                                 error_text(error));
    }
    (void)root_descriptor.release();
    OwnedDirectoryStream stream(raw_stream);
    const int directory_descriptor = ::dirfd(stream.get());
    if (directory_descriptor < 0) {
        const int error = errno;
        throw std::runtime_error(label + " directory stream descriptor failed: " +
                                 error_text(error));
    }

    ScannedPayloadIndex out;
    out.entries.reserve(static_cast<std::size_t>(limits.max_entries));
    const SyncDirectoryAttestation& root_attestation =
        scan_authority.attestation();

    for (;;) {
        errno = 0;
        dirent* entry = ::readdir(stream.get());
        if (entry == nullptr) {
            if (errno != 0) {
                const int error = errno;
                throw std::runtime_error(label + " directory scan failed: " +
                                         error_text(error));
            }
            break;
        }
        const std::string_view basename(entry->d_name);
        if (basename == "." || basename == "..") continue;

        if (basename == kLegacyStoreIdentityBasenameV1) {
            throw std::runtime_error(
                label +
                " refuses legacy payload-store identity generation v1; "
                "offline migration is required before lease-protected use");
        }
        const bool current_identity_name =
            basename == kStandaloneStoreIdentityBasenameV2 ||
            basename == kProductStoreIdentityBasenameV3;
        if (current_identity_name && basename != identity_basename) {
            throw std::runtime_error(
                label +
                " refuses an incompatible payload-store identity generation: " +
                std::string(basename));
        }

        if (basename == identity_basename) {
            if (out.identity_present) {
                throw std::runtime_error(
                    label + " observed duplicate payload-store identity authority");
            }
            (void)open_verified_store_identity_or_throw(
                directory_descriptor, scan_authority.path(),
                descriptor_lease.resolution_capability(),
                descriptor_lease.mount_identity(),
                root_attestation, identity_basename, expected_identity,
                label + " identity marker");
            out.identity_present = true;
            continue;
        }

        if (is_lowercase_sha256_hex(basename)) {
            if (out.entries.size() >= limits.max_entries) {
                throw std::length_error(
                    label + " payload entry count exceeds configured budget");
            }
            SyncPosixOpenedRegularFile opened = open_store_file_or_throw(
                directory_descriptor, basename, scan_authority.path(),
                descriptor_lease.resolution_capability(),
                descriptor_lease.mount_identity(),
                label + " payload " + std::string(basename));
            OwnedFd file(opened.descriptor);
            require_private_regular_file_or_throw(
                opened.status, root_attestation,
                label + " payload " + std::string(basename));
            const std::uint64_t size_bytes =
                static_cast<std::uint64_t>(opened.status.st_size);
            if (size_bytes > limits.max_payload_bytes) {
                throw std::length_error(
                    label + " payload exceeds configured byte budget: " +
                    std::string(basename));
            }
            if (out.indexed_bytes > limits.max_indexed_bytes ||
                size_bytes > limits.max_indexed_bytes - out.indexed_bytes) {
                throw std::length_error(
                    label + " aggregate payload bytes exceed configured budget");
            }

            FrozenSyncPosixRegularFileSnapshot frozen =
                FrozenSyncPosixRegularFileSnapshot::
                    freeze_borrowed_descriptor_or_throw(
                        file.get(), limits.max_payload_bytes,
                        SyncPosixDescriptorLinkPolicy::exactly_one,
                        label + " payload " + std::string(basename));
            if (frozen.bytes().size() != size_bytes) {
                throw std::runtime_error(
                    label + " payload size changed during validation: " +
                    std::string(basename));
            }
            if (sha256_hex(frozen.bytes()) != basename) {
                throw std::runtime_error(
                    label + " payload bytes do not match digest basename: " +
                    std::string(basename));
            }
            fsync_or_throw(
                file.get(), label + " payload " + std::string(basename));
            verify_named_regular_file_or_throw(
                directory_descriptor, basename, opened.status,
                root_attestation,
                label + " payload " + std::string(basename));
            out.entries.push_back(
                PayloadIndexEntry{std::string(basename), size_bytes});
            out.indexed_bytes += size_bytes;
            continue;
        }

        if (sync_atomic_file_publication_temp_basename_is_exact(basename)) {
            if (out.transient_entry_count >= limits.max_transient_entries) {
                throw std::length_error(
                    label + " publication residue count exceeds configured budget");
            }
            SyncPosixOpenedRegularFile opened = open_store_file_or_throw(
                directory_descriptor, basename, scan_authority.path(),
                descriptor_lease.resolution_capability(),
                descriptor_lease.mount_identity(),
                label + " publication residue " + std::string(basename));
            OwnedFd file(opened.descriptor);
            require_private_regular_file_or_throw(
                opened.status, root_attestation,
                label + " publication residue " + std::string(basename));
            const std::uint64_t residue_bytes =
                static_cast<std::uint64_t>(opened.status.st_size);
            if (out.transient_bytes > limits.max_transient_bytes ||
                residue_bytes >
                    limits.max_transient_bytes - out.transient_bytes) {
                throw std::length_error(
                    label +
                    " publication residue bytes exceed configured budget");
            }
            verify_named_regular_file_or_throw(
                directory_descriptor, basename, opened.status,
                root_attestation,
                label + " publication residue " + std::string(basename));
            ++out.transient_entry_count;
            out.transient_bytes += residue_bytes;
            continue;
        }

        throw std::runtime_error(
            label + " refuses unexpected payload-root entry: " +
            std::string(basename));
    }

    std::sort(
        out.entries.begin(), out.entries.end(),
        [](const PayloadIndexEntry& left, const PayloadIndexEntry& right) {
            return left.content_sha256 < right.content_sha256;
        });
    if (std::adjacent_find(
            out.entries.begin(), out.entries.end(),
            [](const PayloadIndexEntry& left, const PayloadIndexEntry& right) {
                return left.content_sha256 == right.content_sha256;
            }) != out.entries.end()) {
        throw std::runtime_error(
            label + " observed duplicate digest namespace authority");
    }
    if (identity_required && !out.identity_present) {
        throw std::runtime_error(
            label + " payload-store identity marker is absent");
    }

    fsync_or_throw(directory_descriptor, label + " root directory");
    struct stat directory_after{};
    if (::fstat(directory_descriptor, &directory_after) != 0) {
        const int error = errno;
        throw std::runtime_error(label + " final root fstat failed: " +
                                 error_text(error));
    }
    if (!same_directory_observation(directory_before, directory_after)) {
        throw std::runtime_error(
            label + " payload root changed while its index was scanned");
    }
    scan_authority.verify_or_throw(label + " final scan root authority");
    root_authority.verify_or_throw(label + " final retained root authority");
    return out;
}

[[nodiscard]] ScannedPayloadIndex scan_store_under_lease_or_throw(
    const SyncDirectoryAuthority& root_authority,
    const SyncReplicaFilePayloadStoreLimits& limits,
    std::string_view identity_basename,
    std::string_view expected_identity,
    const StoreLease& lease,
    SyncReplicaFilePayloadStoreLeaseMode required_mode,
    const std::string& label) {
    if (lease.mode() != required_mode) {
        throw std::logic_error(
            label + " payload-store scan received the wrong lease mode");
    }
    lease.verify_or_throw(root_authority, label + " pre-scan lease proof");
    ScannedPayloadIndex out = scan_store_namespace_or_throw(
        root_authority, limits, identity_basename, expected_identity,
        true, label);
    // The directory scan validates the marker it enumerated. This separate
    // proof binds that name back to the exact inode carrying our still-live
    // lock, closing an identical-marker replacement/split-lock frontier.
    lease.verify_or_throw(root_authority, label + " final lease proof");
    return out;
}

void ensure_store_identity_or_throw(
    const SyncDirectoryAuthority& root_authority,
    const SyncReplicaFilePayloadStoreLimits& limits,
    std::string_view identity_basename,
    std::string_view expected_identity,
    SyncReplicaFilePayloadStoreOpenDisposition disposition,
    bool allow_existing_payload_adoption,
    const std::string& label) {
    const std::string expected(expected_identity);
    auto reconcile = [&]() {
        return reconcile_sync_immutable_file_create_new_under_directory_or_throw(
            root_authority, fs::path(identity_basename),
            byte_span(expected), label + " identity reconciliation");
    };

    SyncImmutableFileReconciliationOutcome outcome = reconcile();
    if (outcome ==
        SyncImmutableFileReconciliationOutcome::ExactAndDirectorySynced) {
        return;
    }
    if (outcome ==
        SyncImmutableFileReconciliationOutcome::ConflictingEntry) {
        throw std::runtime_error(
            label + " identity marker conflicts with the requested folder");
    }
    if (disposition ==
        SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly) {
        throw std::runtime_error(
            label +
            " payload-store identity marker is absent and requires explicit "
            "bootstrap");
    }

    // Bootstrap is mutation-free until the complete pre-existing namespace is
    // validated. This permits adoption of exact digest-named payloads while an
    // unknown, malformed, linked, or over-budget entry cannot gain a marker
    // merely by invoking the constructor or snapshot API.
    const ScannedPayloadIndex bootstrap = scan_store_namespace_or_throw(
        root_authority, limits, identity_basename, expected, false,
        label + " identity bootstrap preflight");
    if (!allow_existing_payload_adoption &&
        (!bootstrap.entries.empty() ||
         bootstrap.transient_entry_count != 0U ||
         bootstrap.transient_bytes != 0U)) {
        throw std::runtime_error(
            label +
            " product-bound bootstrap refuses adoption of pre-existing "
            "payload-root entries");
    }
    if (bootstrap.identity_present) {
        outcome = reconcile();
        if (outcome ==
            SyncImmutableFileReconciliationOutcome::ExactAndDirectorySynced) {
            return;
        }
        throw std::runtime_error(
            label + " identity marker changed during bootstrap");
    }

    try {
        write_sync_file_atomically_create_new_under_directory_or_throw(
            root_authority, fs::path(identity_basename),
            byte_span(expected), label + " identity publication");
    } catch (...) {
        const std::exception_ptr original = std::current_exception();
        outcome = reconcile();
        if (outcome ==
            SyncImmutableFileReconciliationOutcome::ExactAndDirectorySynced) {
            return;
        }
        if (outcome ==
            SyncImmutableFileReconciliationOutcome::ConflictingEntry) {
            throw std::runtime_error(
                label +
                " identity publication raced with a conflicting folder binding");
        }
        std::rethrow_exception(original);
    }

    outcome = reconcile();
    if (outcome !=
        SyncImmutableFileReconciliationOutcome::ExactAndDirectorySynced) {
        throw std::runtime_error(
            label + " identity publication did not become durable and exact");
    }
}

[[nodiscard]] const PayloadIndexEntry* find_entry(
    const std::vector<PayloadIndexEntry>& entries,
    std::string_view digest) noexcept {
    const auto found = std::lower_bound(
        entries.begin(), entries.end(), digest,
        [](const PayloadIndexEntry& entry, std::string_view value) {
            return entry.content_sha256 < value;
        });
    if (found == entries.end() || found->content_sha256 != digest) {
        return nullptr;
    }
    return &*found;
}

}  // namespace

struct SyncReplicaFilePayloadStoreSnapshot::State final {
    std::string folder_id;
    fs::path root_path;
    SyncDirectoryAuthority root_authority;
    SyncReplicaFilePayloadStoreLimits limits;
    std::vector<PayloadIndexEntry> entries;
    SyncReplicaFileContentInventory content_inventory;
    std::uint64_t indexed_bytes = 0U;
    std::uint64_t transient_entry_count = 0U;
    std::uint64_t transient_bytes = 0U;
    std::string root_attestation_digest;
    std::string snapshot_digest;
};

struct SyncReplicaFilePayloadStore::State final {
    std::string folder_id;
    fs::path root_path;
    SyncReplicaFilePayloadStoreOpenDisposition disposition =
        SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly;
    SyncReplicaFilePayloadStoreLimits limits;
    std::string label;
    std::string identity_basename;
    std::string expected_identity;
    bool allow_existing_payload_adoption = true;
    SyncDirectoryAuthority root_authority;
    std::string root_attestation_digest;
};

void validate_sync_replica_file_payload_store_limits_or_throw(
    const SyncReplicaFilePayloadStoreLimits& limits) {
    if (limits.max_entries == 0U ||
        limits.max_entries > kSyncReplicaFilePayloadStoreMaxEntries) {
        throw std::invalid_argument(
            "sync replica file payload store entry limit is invalid");
    }
    if (limits.max_payload_bytes == 0U ||
        limits.max_indexed_bytes == 0U ||
        limits.max_payload_bytes > limits.max_indexed_bytes ||
        limits.max_indexed_bytes > kMaximumPersistentInteger) {
        throw std::invalid_argument(
            "sync replica file payload store byte limits are invalid");
    }
    if (limits.max_payload_bytes >
        std::numeric_limits<std::size_t>::max()) {
        throw std::invalid_argument(
            "sync replica file payload store payload limit exceeds addressable memory");
    }
    if (limits.max_transient_entries == 0U ||
        limits.max_transient_entries >
            kSyncReplicaFilePayloadStoreMaxTransientEntries) {
        throw std::invalid_argument(
            "sync replica file payload store transient-entry limit is invalid");
    }
    if (limits.max_transient_bytes == 0U ||
        limits.max_transient_bytes > kMaximumPersistentInteger) {
        throw std::invalid_argument(
            "sync replica file payload store transient-byte limit is invalid");
    }
}

SyncReplicaFilePayloadStoreSnapshot::SyncReplicaFilePayloadStoreSnapshot(
    std::unique_ptr<State> state) noexcept
    : state_(std::move(state)) {}

SyncReplicaFilePayloadStoreSnapshot::SyncReplicaFilePayloadStoreSnapshot(
    SyncReplicaFilePayloadStoreSnapshot&&) noexcept = default;

SyncReplicaFilePayloadStoreSnapshot&
SyncReplicaFilePayloadStoreSnapshot::operator=(
    SyncReplicaFilePayloadStoreSnapshot&&) noexcept = default;

SyncReplicaFilePayloadStoreSnapshot::~SyncReplicaFilePayloadStoreSnapshot()
    noexcept = default;

const SyncReplicaFilePayloadStoreSnapshot::State&
SyncReplicaFilePayloadStoreSnapshot::require_state_or_throw(
    std::string_view label) const {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica durable payload snapshot operation label must not be empty");
    }
    if (!state_) {
        throw std::logic_error(
            std::string(label) + " durable payload snapshot is inactive");
    }
    return *state_;
}

const std::string& SyncReplicaFilePayloadStoreSnapshot::folder_id() const {
    return require_state_or_throw(
               "sync replica durable payload snapshot folder")
        .folder_id;
}

const fs::path& SyncReplicaFilePayloadStoreSnapshot::root_path() const {
    return require_state_or_throw(
               "sync replica durable payload snapshot root path")
        .root_path;
}

std::uint64_t SyncReplicaFilePayloadStoreSnapshot::entry_count() const {
    const State& state = require_state_or_throw(
        "sync replica durable payload snapshot entry count");
    return static_cast<std::uint64_t>(state.entries.size());
}

std::uint64_t SyncReplicaFilePayloadStoreSnapshot::indexed_bytes() const {
    return require_state_or_throw(
               "sync replica durable payload snapshot indexed bytes")
        .indexed_bytes;
}

std::uint64_t
SyncReplicaFilePayloadStoreSnapshot::transient_entry_count() const {
    return require_state_or_throw(
               "sync replica durable payload snapshot transient entry count")
        .transient_entry_count;
}

std::uint64_t SyncReplicaFilePayloadStoreSnapshot::transient_bytes() const {
    return require_state_or_throw(
               "sync replica durable payload snapshot transient bytes")
        .transient_bytes;
}

const std::string&
SyncReplicaFilePayloadStoreSnapshot::root_attestation_digest() const {
    return require_state_or_throw(
               "sync replica durable payload snapshot root attestation digest")
        .root_attestation_digest;
}

const std::string&
SyncReplicaFilePayloadStoreSnapshot::snapshot_digest() const {
    return require_state_or_throw(
               "sync replica durable payload snapshot digest")
        .snapshot_digest;
}

const SyncReplicaFilePayloadStoreLimits&
SyncReplicaFilePayloadStoreSnapshot::limits() const {
    return require_state_or_throw(
               "sync replica durable payload snapshot limits")
        .limits;
}

SyncReplicaFileContentInventory
SyncReplicaFilePayloadStoreSnapshot::content_inventory() const {
    return require_state_or_throw(
               "sync replica durable payload snapshot content inventory")
        .content_inventory;
}

std::optional<std::uint64_t>
SyncReplicaFilePayloadStoreSnapshot::payload_size_or_none(
    std::string_view content_sha256) const {
    const State& state = require_state_or_throw(
        "sync replica durable payload snapshot size lookup");
    if (!is_lowercase_sha256_hex(content_sha256)) {
        throw std::invalid_argument(
            "sync replica durable payload snapshot size lookup digest is invalid");
    }
    const PayloadIndexEntry* entry = find_entry(state.entries, content_sha256);
    if (entry == nullptr) return std::nullopt;
    return entry->size_bytes;
}

std::string
SyncReplicaFilePayloadStoreSnapshot::copy_payload_for_operation_or_throw(
    const SyncReplicaOperation& operation,
    std::string_view label_view) const {
    const State& state = require_state_or_throw(label_view);
    const std::string label(label_view);
    if (operation.kind != SyncReplicaValueKind::File) {
        throw std::invalid_argument(label + " requires a file operation");
    }
    if (!is_lowercase_sha256_hex(operation.content_sha256)) {
        throw std::invalid_argument(
            label + " operation content digest is invalid");
    }
    if (operation.size_bytes > state.limits.max_payload_bytes) {
        throw std::length_error(
            label + " operation exceeds the durable payload budget");
    }
    const PayloadIndexEntry* indexed =
        find_entry(state.entries, operation.content_sha256);
    if (indexed == nullptr) {
        throw std::runtime_error(
            label + " has no indexed payload for the claimed operation");
    }
    if (indexed->size_bytes != operation.size_bytes) {
        throw std::logic_error(
            label + " indexed payload size disagrees with the claimed operation");
    }

    using Access = sync_directory_authority_detail::
        SyncDirectoryAuthorityAccess;
    state.root_authority.verify_or_throw(label + " root preflight");
    auto descriptor_lease =
        Access::duplicate_shared_open_description_or_throw(
            state.root_authority, label + " selected payload");
    OwnedFd root_descriptor(descriptor_lease.release_descriptor());
    SyncPosixOpenedRegularFile opened = open_store_file_or_throw(
        root_descriptor.get(), operation.content_sha256, state.root_path,
        descriptor_lease.resolution_capability(),
        descriptor_lease.mount_identity(),
        label + " selected payload");
    OwnedFd file(opened.descriptor);
    require_private_regular_file_or_throw(
        opened.status, state.root_authority.attestation(),
        label + " selected payload");
    if (static_cast<std::uint64_t>(opened.status.st_size) !=
        operation.size_bytes) {
        throw std::runtime_error(
            label + " selected payload size changed after indexing");
    }
    FrozenSyncPosixRegularFileSnapshot frozen =
        FrozenSyncPosixRegularFileSnapshot::freeze_borrowed_descriptor_or_throw(
            file.get(), state.limits.max_payload_bytes,
            SyncPosixDescriptorLinkPolicy::exactly_one,
            label + " selected payload");
    if (frozen.bytes().size() != operation.size_bytes ||
        sha256_hex(frozen.bytes()) != operation.content_sha256) {
        throw std::runtime_error(
            label + " selected payload bytes changed after indexing");
    }
    verify_named_regular_file_or_throw(
        root_descriptor.get(), operation.content_sha256, opened.status,
        state.root_authority.attestation(), label + " selected payload");
    state.root_authority.verify_or_throw(label + " final root proof");
    return std::move(frozen).take_bytes();
}

void SyncReplicaFilePayloadStoreSnapshot::require_folder_or_throw(
    std::string_view folder_id,
    std::string_view label) const {
    const State& state = require_state_or_throw(label);
    if (!sync_id_is_valid(folder_id)) {
        throw std::invalid_argument(
            std::string(label) + " service folder_id is invalid");
    }
    if (state.folder_id != folder_id) {
        throw std::invalid_argument(
            std::string(label) +
            " durable payload snapshot does not match service folder identity");
    }
}

void SyncReplicaFilePayloadStoreSnapshot::preflight_or_throw(
    std::string_view label) const {
    const State& state = require_state_or_throw(label);
    state.root_authority.verify_or_throw(
        std::string(label) + " root authority");
}

SyncReplicaFilePayloadStore::SyncReplicaFilePayloadStore(
    std::string folder_id,
    fs::path absolute_root_directory,
    SyncReplicaFilePayloadStoreOpenDisposition disposition,
    SyncReplicaFilePayloadStoreLimits limits,
    std::string label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica file payload store label must not be empty");
    }
    if (!sync_id_is_valid(folder_id)) {
        throw std::invalid_argument(
            label + " folder_id is not a lowercase portable sync id");
    }
    switch (disposition) {
        case SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly:
        case SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing:
            break;
        default:
            throw std::invalid_argument(
                label + " payload-store open disposition is invalid");
    }
    validate_sync_replica_file_payload_store_limits_or_throw(limits);

    auto state = std::make_unique<State>();
    state->folder_id = std::move(folder_id);
    state->disposition = disposition;
    state->limits = limits;
    state->label = std::move(label);
    state->identity_basename =
        std::string(kStandaloneStoreIdentityBasenameV2);
    state->expected_identity =
        standalone_store_identity_payload(state->folder_id);
    state->allow_existing_payload_adoption = true;
    state->root_authority = SyncDirectoryAuthority::open_or_throw(
        absolute_root_directory, state->label + " root");
    state->root_path = state->root_authority.path();
    state->root_attestation_digest =
        sync_directory_attestation_digest_or_throw(
            state->root_authority.attestation());
    state_ = std::move(state);
}

SyncReplicaFilePayloadStore::SyncReplicaFilePayloadStore(
    SyncReplicaDeploymentIdentity deployment_identity,
    fs::path absolute_root_directory,
    SyncReplicaFilePayloadStoreOpenDisposition disposition,
    SyncReplicaFilePayloadStoreLimits limits,
    std::string label)
    : SyncReplicaFilePayloadStore(
          deployment_identity.folder_id, std::move(absolute_root_directory),
          disposition, limits, std::move(label)) {
    validate_sync_replica_deployment_identity_or_throw(
        deployment_identity, state_->label + " deployment identity");
    state_->identity_basename = std::string(kProductStoreIdentityBasenameV3);
    state_->expected_identity = product_store_identity_payload_or_throw(
        deployment_identity, state_->label + " deployment identity");
    state_->allow_existing_payload_adoption = false;
}

SyncReplicaFilePayloadStore::~SyncReplicaFilePayloadStore() noexcept = default;

const std::string& SyncReplicaFilePayloadStore::folder_id() const {
    if (!state_) throw std::logic_error("file payload store is inactive");
    return state_->folder_id;
}

const fs::path& SyncReplicaFilePayloadStore::root_path() const {
    if (!state_) throw std::logic_error("file payload store is inactive");
    return state_->root_path;
}

const SyncReplicaFilePayloadStoreLimits&
SyncReplicaFilePayloadStore::limits() const {
    if (!state_) throw std::logic_error("file payload store is inactive");
    return state_->limits;
}

SyncReplicaFilePayloadStoreSnapshot
SyncReplicaFilePayloadStore::snapshot_or_throw() const {
    if (!state_) throw std::logic_error("file payload store is inactive");
    State& store = *state_;
    store.root_authority.verify_or_throw(
        store.label + " snapshot source preflight");
    ensure_store_identity_or_throw(
        store.root_authority, store.limits, store.identity_basename,
        store.expected_identity, store.disposition,
        store.allow_existing_payload_adoption, store.label);
    const std::string& expected_identity = store.expected_identity;
    SyncDirectoryAuthority snapshot_root =
        reopen_matching_root_authority_or_throw(
            store.root_authority, store.label + " snapshot");

    StoreLease observation_lease = acquire_store_lease_or_throw(
        snapshot_root, store.identity_basename, expected_identity,
        SyncReplicaFilePayloadStoreLeaseMode::SharedObservation,
        store.label + " snapshot");

    ScannedPayloadIndex scanned = scan_store_under_lease_or_throw(
        snapshot_root, store.limits, store.identity_basename,
        expected_identity, observation_lease,
        SyncReplicaFilePayloadStoreLeaseMode::SharedObservation,
        store.label + " snapshot");
    auto snapshot = std::make_unique<SyncReplicaFilePayloadStoreSnapshot::State>();
    snapshot->folder_id = store.folder_id;
    snapshot->root_path = store.root_path;
    snapshot->root_authority = std::move(snapshot_root);
    snapshot->limits = store.limits;
    snapshot->entries = std::move(scanned.entries);
    snapshot->indexed_bytes = scanned.indexed_bytes;
    snapshot->transient_entry_count = scanned.transient_entry_count;
    snapshot->transient_bytes = scanned.transient_bytes;
    snapshot->root_attestation_digest = store.root_attestation_digest;

    std::vector<std::string> digests;
    digests.reserve(snapshot->entries.size());
    for (const PayloadIndexEntry& entry : snapshot->entries) {
        digests.push_back(entry.content_sha256);
    }
    snapshot->content_inventory = SyncReplicaFileContentInventory(
        snapshot->folder_id, std::move(digests),
        store.label + " snapshot content inventory");
    snapshot->snapshot_digest = snapshot_digest_or_throw(
        snapshot->folder_id, snapshot->root_path.generic_string(),
        snapshot->root_attestation_digest, store.identity_basename,
        expected_identity, snapshot->limits,
        snapshot->transient_entry_count, snapshot->transient_bytes,
        snapshot->indexed_bytes, snapshot->entries);
    // Keep the shared observation lease live through every allocation and
    // derived-index construction. The final proof prevents an identical-bytes
    // replacement marker from turning a completed scan into authority bound to
    // a different lock inode before the snapshot is returned.
    observation_lease.verify_or_throw(
        snapshot->root_authority,
        store.label + " snapshot final lease cutpoint");
    return SyncReplicaFilePayloadStoreSnapshot(std::move(snapshot));
}

SyncReplicaFilePayloadStorePutResult
SyncReplicaFilePayloadStore::put_payload_or_throw(std::string payload) {
    if (!state_) throw std::logic_error("file payload store is inactive");
    State& store = *state_;
    const std::uint64_t size_bytes =
        size_to_u64_or_throw(payload.size(), store.label + " payload");
    if (size_bytes > store.limits.max_payload_bytes) {
        throw std::length_error(
            store.label + " payload exceeds configured byte budget");
    }
    const std::string digest = sha256_hex(payload);
    store.root_authority.verify_or_throw(
        store.label + " payload publication source preflight");
    ensure_store_identity_or_throw(
        store.root_authority, store.limits, store.identity_basename,
        store.expected_identity, store.disposition,
        store.allow_existing_payload_adoption, store.label);
    const std::string& expected_identity = store.expected_identity;
    StoreLease mutation_lease = acquire_store_lease_or_throw(
        store.root_authority, store.identity_basename, expected_identity,
        SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation,
        store.label + " payload publication");
    const ScannedPayloadIndex before = scan_store_under_lease_or_throw(
        store.root_authority, store.limits, store.identity_basename,
        expected_identity, mutation_lease,
        SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation,
        store.label + " payload publication preflight");
    const PayloadIndexEntry* existing = find_entry(before.entries, digest);
    if (existing != nullptr) {
        mutation_lease.verify_or_throw(
            store.root_authority,
            store.label + " existing payload pre-reconciliation lease cutpoint");
        const SyncImmutableFileReconciliationOutcome reconciliation =
            reconcile_sync_immutable_file_create_new_under_directory_or_throw(
                store.root_authority, fs::path(digest), byte_span(payload),
                store.label + " existing payload reconciliation");
        if (reconciliation !=
            SyncImmutableFileReconciliationOutcome::ExactAndDirectorySynced) {
            throw std::runtime_error(
                store.label +
                " digest-named payload conflicts with the exact supplied bytes");
        }
        mutation_lease.verify_or_throw(
            store.root_authority,
            store.label + " existing payload final lease cutpoint");
        return SyncReplicaFilePayloadStorePutResult{
            SyncReplicaFilePayloadStorePutDisposition::AlreadyPresent,
            digest, size_bytes};
    }
    if (before.entries.size() >= store.limits.max_entries) {
        throw std::length_error(
            store.label + " payload entry count is at configured capacity");
    }
    if (before.indexed_bytes > store.limits.max_indexed_bytes ||
        size_bytes >
            store.limits.max_indexed_bytes - before.indexed_bytes) {
        throw std::length_error(
            store.label + " aggregate payload bytes exceed configured budget");
    }
    if (before.transient_entry_count >=
        store.limits.max_transient_entries) {
        throw std::length_error(
            store.label + " publication residue count is at configured capacity");
    }
    if (before.transient_bytes > store.limits.max_transient_bytes ||
        size_bytes >
            store.limits.max_transient_bytes - before.transient_bytes) {
        throw std::length_error(
            store.label +
            " publication residue bytes cannot admit one bounded writer");
    }

    mutation_lease.verify_or_throw(
        store.root_authority,
        store.label + " payload pre-publication lease cutpoint");
    try {
        write_sync_file_atomically_create_new_under_directory_or_throw(
            store.root_authority, fs::path(digest), byte_span(payload),
            store.label + " payload publication");
        mutation_lease.verify_or_throw(
            store.root_authority,
            store.label + " payload publication final lease cutpoint");
        return SyncReplicaFilePayloadStorePutResult{
            SyncReplicaFilePayloadStorePutDisposition::Inserted,
            digest, size_bytes};
    } catch (...) {
        const std::exception_ptr original = std::current_exception();
        // Reconciliation is authoritative only while the exact lock anchor is
        // still named by the retained root. If that witness changed, propagate
        // the lease failure rather than interpreting bytes under a split lock.
        mutation_lease.verify_or_throw(
            store.root_authority,
            store.label + " failed publication pre-reconciliation lease cutpoint");
        const SyncImmutableFileReconciliationOutcome reconciliation =
            reconcile_sync_immutable_file_create_new_under_directory_or_throw(
                store.root_authority, fs::path(digest), byte_span(payload),
                store.label + " failed publication reconciliation");
        if (reconciliation ==
            SyncImmutableFileReconciliationOutcome::ExactAndDirectorySynced) {
            mutation_lease.verify_or_throw(
                store.root_authority,
                store.label + " reconciled publication final lease cutpoint");
            return SyncReplicaFilePayloadStorePutResult{
                SyncReplicaFilePayloadStorePutDisposition::AlreadyPresent,
                digest, size_bytes};
        }
        if (reconciliation ==
            SyncImmutableFileReconciliationOutcome::ConflictingEntry) {
            mutation_lease.verify_or_throw(
                store.root_authority,
                store.label + " conflicting publication final lease cutpoint");
            throw std::runtime_error(
                store.label +
                " digest-named destination contains conflicting immutable bytes");
        }
        mutation_lease.verify_or_throw(
            store.root_authority,
            store.label + " absent publication final lease cutpoint");
        std::rethrow_exception(original);
    }
}

}  // namespace anonsync

#endif
