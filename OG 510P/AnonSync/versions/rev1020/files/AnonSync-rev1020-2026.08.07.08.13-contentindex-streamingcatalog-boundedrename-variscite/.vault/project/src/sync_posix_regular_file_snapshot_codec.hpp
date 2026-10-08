#pragma once

#if !defined(_WIN32)

#include "sync_posix_descriptor_snapshot.hpp"

#include <cstdint>
#include <optional>
#include <string>
#include <string_view>

namespace anonsync {

// Canonical fixed-width projection shared by every durable record that binds a
// POSIX regular-file observation. Keeping the eleven fields and their big-endian
// layout in one leaf prevents the restart verification index and rotating scrub
// cursor from silently assigning different meanings to the same stat snapshot.
inline constexpr std::uint64_t
    kSyncPosixRegularFileSnapshotMetadataEncodedBytes = 11U * 8U;

void append_sync_posix_regular_file_snapshot_metadata_binary(
    std::string& output,
    const SyncPosixRegularFileSnapshotMetadata& metadata);

[[nodiscard]] SyncPosixRegularFileSnapshotMetadata
parse_sync_posix_regular_file_snapshot_metadata_binary_or_throw(
    std::string_view exact_bytes,
    std::string_view label);

// Durable payload metadata is stricter than the generic descriptor snapshot:
// it must name one private regular inode with exact mode 0600 and one link. An
// optional extent ceiling applies to payload entries, while identity-marker
// observations remain unbounded by the content ceiling.
void validate_sync_posix_private_single_link_regular_file_snapshot_metadata_or_throw(
    const SyncPosixRegularFileSnapshotMetadata& metadata,
    std::optional<std::uint64_t> maximum_size_bytes,
    std::string_view label);

}  // namespace anonsync

#endif
