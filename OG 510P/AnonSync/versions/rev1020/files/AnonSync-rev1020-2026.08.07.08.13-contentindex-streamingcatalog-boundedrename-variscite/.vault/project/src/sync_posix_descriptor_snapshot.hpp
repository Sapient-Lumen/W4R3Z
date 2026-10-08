#pragma once

#if !defined(_WIN32)

#include <cstdint>
#include <string>
#include <utility>

#include <sys/stat.h>

namespace anonsync {

enum class SyncPosixDescriptorLinkPolicy : unsigned char {
    stable_named_object,
    exactly_one,
};

// Exact final descriptor metadata retained with one frozen byte observation.
// The snapshot compares these fields before and after pread(2), and callers
// may later compare a no-follow pathname observation against the same record.
// This lets a folder observer prove that a name still designates the object it
// hashed instead of reacquiring metadata through a second, unrelated pathname
// lookup.
struct SyncPosixRegularFileSnapshotMetadata final {
    std::uint64_t device = 0;
    std::uint64_t inode = 0;
    std::uint64_t size_bytes = 0;
    std::uint64_t link_count = 0;
    std::uint64_t owner_user_id = 0;
    std::uint64_t owner_group_id = 0;
    std::uint32_t mode = 0;
    std::int64_t modification_seconds = 0;
    std::uint32_t modification_nanoseconds = 0;
    std::int64_t status_change_seconds = 0;
    std::uint32_t status_change_nanoseconds = 0;

    bool operator==(const SyncPosixRegularFileSnapshotMetadata&) const =
        default;
};

// Converts one caller-supplied status observation into the canonical complete
// regular-file metadata record. This is a pure conversion boundary: it grants
// no pathname or descriptor authority, and callers remain responsible for the
// syscall/capability that produced status.
[[nodiscard]] SyncPosixRegularFileSnapshotMetadata
sync_posix_regular_file_snapshot_metadata_from_status_or_throw(
    const struct stat& status,
    SyncPosixDescriptorLinkPolicy link_policy,
    const std::string& label);

// Captures the same validated metadata record used by a frozen byte snapshot
// without consuming or closing the borrowed descriptor. This is the shared
// re-attestation boundary for scanners that retain an opened file across a
// publication transaction.
[[nodiscard]] SyncPosixRegularFileSnapshotMetadata
observe_sync_posix_regular_file_descriptor_or_throw(
    int descriptor,
    SyncPosixDescriptorLinkPolicy link_policy,
    const std::string& label);

// Pure status comparison shared by descriptor owners and pathname reproofs.
// Callers remain responsible for obtaining status from the exact capability
// they need to bind; this function grants no pathname authority by itself.
[[nodiscard]] bool sync_posix_regular_file_snapshot_metadata_matches_status(
    const SyncPosixRegularFileSnapshotMetadata& metadata,
    const struct stat& status) noexcept;

// One exact streaming digest observation. Unlike FrozenSyncPosixRegularFileSnapshot,
// this owner never retains the file bytes in memory. It hashes the descriptor with
// pread(2), compares the complete metadata record before and after the stream, and
// returns the same metadata identity that callers can later bind to a pathname or
// use as the source proof for descriptor-to-descriptor publication.
struct SyncPosixRegularFileDigestObservation final {
    SyncPosixRegularFileSnapshotMetadata metadata;
    std::string content_sha256;

    bool operator==(const SyncPosixRegularFileDigestObservation&) const =
        default;
};

[[nodiscard]] SyncPosixRegularFileDigestObservation
hash_sync_posix_regular_file_descriptor_or_throw(
    int descriptor,
    std::uint64_t maximum_bytes,
    SyncPosixDescriptorLinkPolicy link_policy,
    const std::string& label);

// Freezes one exact observation of a caller-owned POSIX descriptor. The
// descriptor remains borrowed: this owner never closes it and uses pread(2),
// so the caller's shared file offset is not consumed or rewritten.
class FrozenSyncPosixRegularFileSnapshot final {
public:
    [[nodiscard]] static FrozenSyncPosixRegularFileSnapshot
    freeze_borrowed_descriptor_or_throw(
        int descriptor,
        std::uint64_t maximum_bytes,
        SyncPosixDescriptorLinkPolicy link_policy,
        const std::string& label);

    [[nodiscard]] const std::string& bytes() const noexcept { return bytes_; }
    [[nodiscard]] std::string take_bytes() && { return std::move(bytes_); }
    [[nodiscard]] const SyncPosixRegularFileSnapshotMetadata& metadata()
        const noexcept {
        return metadata_;
    }

    // Pure no-follow re-attestation helper. It performs no syscall and never
    // grants authority by itself; callers supply a status record obtained from
    // the exact parent/name they need to bind after the byte read.
    [[nodiscard]] bool matches_status(const struct stat& status) const noexcept;

private:
    FrozenSyncPosixRegularFileSnapshot(
        std::string bytes,
        SyncPosixRegularFileSnapshotMetadata metadata)
        : bytes_(std::move(bytes)), metadata_(metadata) {}

    std::string bytes_;
    SyncPosixRegularFileSnapshotMetadata metadata_;
};

}  // namespace anonsync

#endif
