#pragma once

#if !defined(_WIN32)

#include "sync_posix_descriptor_snapshot.hpp"

#include <cstdint>
#include <string>
#include <string_view>
#include <vector>

namespace anonsync {

// Private non-authoritative acceleration record colocated with the immutable
// digest namespace. The payload store validates this exact basename as internal
// metadata; it never appears in content inventory or capacity accounting.
inline constexpr std::string_view
    kSyncReplicaFilePayloadVerificationIndexBasename =
        ".anonsync-payload-verification-index-v1";

struct SyncReplicaFilePayloadVerificationIndexEntry final {
    std::string content_sha256;
    SyncPosixRegularFileSnapshotMetadata metadata;

    bool operator==(
        const SyncReplicaFilePayloadVerificationIndexEntry&) const = default;
};

// A durable verification index is a restart acceleration hint, not payload
// authority. It binds the exact immutable store-identity marker observation and
// exact per-payload metadata observations to records that were previously
// established by complete byte hashing. Consumers must still enumerate the
// namespace, re-prove every named file, and hash every missing or changed
// observation before returning a snapshot.
struct SyncReplicaFilePayloadVerificationIndex final {
    std::string store_identity_sha256;
    SyncPosixRegularFileSnapshotMetadata store_identity_metadata;
    std::uint64_t indexed_bytes = 0U;
    std::vector<SyncReplicaFilePayloadVerificationIndexEntry> entries;

    bool operator==(
        const SyncReplicaFilePayloadVerificationIndex&) const = default;
};

// Exact upper bound for the v1 binary encoding at max_entries. This lets the
// descriptor freezer reject oversized/crafted metadata before allocation.
[[nodiscard]] std::uint64_t
sync_replica_file_payload_verification_index_maximum_bytes_or_throw(
    std::uint64_t max_entries,
    std::string_view label);

// Canonical fixed-width big-endian encoding with a trailing SHA-256 checksum.
// The checksum detects torn/corrupt records; it is not a secret-key MAC and is
// deliberately not treated as protection from a noncooperating same-UID writer.
[[nodiscard]] std::string
serialize_sync_replica_file_payload_verification_index_or_throw(
    const SyncReplicaFilePayloadVerificationIndex& index,
    std::uint64_t max_entries,
    std::uint64_t max_indexed_bytes,
    std::string_view label);

// Strict inverse of the serializer. Malformed bytes throw invalid_argument so
// the payload owner can distinguish an unusable acceleration record from an I/O
// or authority failure and conservatively fall back to complete byte hashing.
[[nodiscard]] SyncReplicaFilePayloadVerificationIndex
parse_sync_replica_file_payload_verification_index_or_throw(
    std::string_view bytes,
    std::uint64_t max_entries,
    std::uint64_t max_indexed_bytes,
    std::string_view label);

}  // namespace anonsync

#endif
