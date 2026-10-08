#pragma once

#if !defined(_WIN32)

#include "resumable_sha256.hpp"
#include "sha256_digest.hpp"
#include "sync_posix_descriptor_snapshot.hpp"
#include "sync_replica_content_defined_chunker.hpp"

#include <cstddef>
#include <cstdint>
#include <string>
#include <string_view>
#include <type_traits>
#include <vector>

namespace anonsync {

inline constexpr std::string_view
    kSyncReplicaSourceManifestCheckpointBasename =
        ".anonsync-payload-source-manifest-checkpoint-v1";
inline constexpr std::uint64_t
    kSyncReplicaSourceManifestCheckpointMaximumChunks = 8192U;
inline constexpr std::uint64_t
    kSyncReplicaSourceManifestCheckpointMaximumCanonicalPathBytes = 4096U;

enum class SyncReplicaSourceManifestCheckpointDisposition : std::uint64_t {
    ActiveProjection = 1U,
    CompleteManifest = 2U,
};

inline constexpr std::size_t
    kSyncReplicaSourceManifestCheckpointDigestBytes = kSha256DigestBytes;

// Shared fixed-width digest storage. The durable codec has always carried
// chunk SHA-256 values as 32 binary bytes; retaining 64-character std::string
// objects here caused one heap allocation per chunk on every checkpoint parse,
// copy, and publication reproof. The same strict 32-byte value is now used by
// protocol, compact-cache, and checkpoint records, preventing three canonical
// text/binary codecs from drifting independently.
//
// This changes only the in-process representation. The checksum-framed on-disk
// format remains byte-for-byte compatible with rev1010.
struct SyncReplicaSourceManifestCheckpointChunk final {
    std::uint64_t size_bytes = 0U;
    Sha256DigestValue sha256;

    SyncReplicaSourceManifestCheckpointChunk() noexcept = default;
    SyncReplicaSourceManifestCheckpointChunk(
        std::uint64_t size_bytes_value,
        std::string_view sha256_hex);
    SyncReplicaSourceManifestCheckpointChunk(
        std::uint64_t size_bytes_value,
        Sha256DigestValue sha256_value) noexcept;

    [[nodiscard]] std::string sha256_hex() const;

    bool operator==(
        const SyncReplicaSourceManifestCheckpointChunk&) const = default;
};

static_assert(
    sizeof(SyncReplicaSourceManifestCheckpointChunk) == 40U,
    "checkpoint chunk storage must remain one contiguous 40-byte record");
static_assert(
    std::is_trivially_copyable_v<
        SyncReplicaSourceManifestCheckpointChunk>,
    "checkpoint chunks must not own hidden heap state");

// One bounded acceleration record for the source-side content-defined manifest
// of one exact retained file operation. It is not replica, payload, or transfer
// authority. Every use must reopen the digest-named payload and re-prove the
// exact private inode observation carried here. Active records retain the
// exact rolling chunker and both SHA-256 continuations at an arbitrary byte
// frontier, so restart does not discard as much as one maximum-sized chunk.
// Complete records retain at most 8,192 digest/extent pairs and avoid rehashing
// a multi-terabyte immutable source after restart.
struct SyncReplicaSourceManifestCheckpoint final {
    std::string store_identity_sha256;
    SyncPosixRegularFileSnapshotMetadata store_identity_metadata;
    std::uint64_t generation = 1U;

    std::string operation_id;
    std::string canonical_path;
    std::string content_sha256;
    std::uint64_t total_size_bytes = 0U;
    SyncPosixRegularFileSnapshotMetadata payload_metadata;
    SyncReplicaContentDefinedChunkingParameters parameters;

    SyncReplicaSourceManifestCheckpointDisposition disposition =
        SyncReplicaSourceManifestCheckpointDisposition::ActiveProjection;
    std::uint64_t next_offset_bytes = 0U;
    std::uint64_t completed_chunk_bytes = 0U;
    ResumableSha256Checkpoint whole_hash;
    ResumableSha256Checkpoint current_chunk_hash;
    SyncReplicaContentDefinedChunkerCheckpoint chunker;
    std::vector<SyncReplicaSourceManifestCheckpointChunk> chunks;
    // Required only for CompleteManifest. It binds the exact protocol manifest
    // projection; active records leave it empty.
    std::string manifest_digest;

    bool operator==(const SyncReplicaSourceManifestCheckpoint&) const =
        default;
};

[[nodiscard]] std::uint64_t
sync_replica_source_manifest_checkpoint_maximum_bytes(
    std::uint64_t maximum_chunk_count =
        kSyncReplicaSourceManifestCheckpointMaximumChunks) noexcept;

[[nodiscard]] std::string
serialize_sync_replica_source_manifest_checkpoint_or_throw(
    const SyncReplicaSourceManifestCheckpoint& checkpoint,
    std::uint64_t maximum_payload_bytes,
    std::uint64_t maximum_chunk_count =
        kSyncReplicaSourceManifestCheckpointMaximumChunks,
    std::string_view label = "source manifest checkpoint serialization");

[[nodiscard]] SyncReplicaSourceManifestCheckpoint
parse_sync_replica_source_manifest_checkpoint_or_throw(
    std::string_view bytes,
    std::uint64_t maximum_payload_bytes,
    std::uint64_t maximum_chunk_count =
        kSyncReplicaSourceManifestCheckpointMaximumChunks,
    std::string_view label = "source manifest checkpoint parsing");

}  // namespace anonsync

#endif
