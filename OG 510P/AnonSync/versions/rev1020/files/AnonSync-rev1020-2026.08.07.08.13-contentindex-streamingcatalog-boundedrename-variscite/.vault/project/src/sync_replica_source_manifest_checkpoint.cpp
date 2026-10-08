#include "sync_replica_source_manifest_checkpoint.hpp"

#if !defined(_WIN32)

#include "sha256_digest.hpp"
#include "sync_manifest_validation.hpp"
#include "sync_posix_regular_file_snapshot_codec.hpp"

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>

namespace anonsync {
namespace {

constexpr std::string_view kMagic =
    "anonsync:sync-replica-source-manifest-checkpoint:v2\n";
constexpr std::uint64_t kEncodedU64Bytes = 8U;
constexpr std::uint64_t kDigestTextBytes = 64U;
constexpr std::uint64_t kDigestBinaryBytes = 32U;
constexpr std::uint64_t kShaCheckpointBytes =
    (8U * 4U) + 64U + 8U + 8U;
constexpr std::uint64_t kChunkBytes = kEncodedU64Bytes + kDigestBinaryBytes;
constexpr std::uint64_t kFixedBodyMaximumBytes =
    // identity digest + identity metadata + generation
    kDigestTextBytes + kSyncPosixRegularFileSnapshotMetadataEncodedBytes +
    kEncodedU64Bytes +
    // operation id + canonical path length and maximum path
    kDigestTextBytes + kEncodedU64Bytes +
    kSyncReplicaSourceManifestCheckpointMaximumCanonicalPathBytes +
    // content digest + total size + payload metadata
    kDigestTextBytes + kEncodedU64Bytes +
    kSyncPosixRegularFileSnapshotMetadataEncodedBytes +
    // four chunk parameters; disposition; next/completed byte frontiers;
    // rolling chunker gear/pending/completed/finished; chunk count
    (12U * kEncodedU64Bytes) +
    // resumable whole/current-chunk hashes + optional complete digest
    (2U * kShaCheckpointBytes) + kDigestTextBytes;

[[noreturn]] void invalid(
    std::string_view label,
    std::string_view reason) {
    throw std::invalid_argument(
        std::string(label) + " source manifest checkpoint " +
        std::string(reason));
}

void append_u64(std::string& output, std::uint64_t value) {
    for (unsigned shift = 56U;; shift -= 8U) {
        output.push_back(static_cast<char>((value >> shift) & 0xffU));
        if (shift == 0U) break;
    }
}

void append_u32(std::string& output, std::uint32_t value) {
    for (unsigned shift = 24U;; shift -= 8U) {
        output.push_back(static_cast<char>((value >> shift) & 0xffU));
        if (shift == 0U) break;
    }
}

class Cursor final {
public:
    Cursor(std::string_view bytes, std::string_view label)
        : bytes_(bytes), label_(label) {}

    [[nodiscard]] std::uint64_t take_u64(std::string_view field) {
        const std::string_view bytes = take(kEncodedU64Bytes, field);
        std::uint64_t value = 0U;
        for (const unsigned char byte : bytes) {
            value = (value << 8U) | static_cast<std::uint64_t>(byte);
        }
        return value;
    }

    [[nodiscard]] std::uint32_t take_u32(std::string_view field) {
        const std::string_view bytes = take(4U, field);
        std::uint32_t value = 0U;
        for (const unsigned char byte : bytes) {
            value = (value << 8U) | static_cast<std::uint32_t>(byte);
        }
        return value;
    }

    [[nodiscard]] std::string take_digest(std::string_view field) {
        const std::string_view value = take(kDigestTextBytes, field);
        if (!is_lowercase_sha256_hex(value)) {
            invalid(label_, std::string(field) + " digest is invalid");
        }
        return std::string(value);
    }

    [[nodiscard]] Sha256DigestValue
    take_binary_digest(std::string_view field) {
        const std::string_view bytes = take(kDigestBinaryBytes, field);
        std::array<
            std::uint8_t, kSyncReplicaSourceManifestCheckpointDigestBytes>
            output{};
        for (std::size_t index = 0U; index < output.size(); ++index) {
            output[index] = static_cast<std::uint8_t>(
                static_cast<unsigned char>(bytes[index]));
        }
        return Sha256DigestValue(output);
    }

    [[nodiscard]] std::string take_string(
        std::uint64_t maximum_bytes,
        std::string_view field) {
        const std::uint64_t length = take_u64(
            std::string(field) + " length");
        if (length > maximum_bytes ||
            length > static_cast<std::uint64_t>(
                (std::numeric_limits<std::size_t>::max)())) {
            invalid(label_, std::string(field) + " exceeds its byte frontier");
        }
        return std::string(take(static_cast<std::size_t>(length), field));
    }

    [[nodiscard]] SyncPosixRegularFileSnapshotMetadata take_metadata(
        std::string_view field) {
        return parse_sync_posix_regular_file_snapshot_metadata_binary_or_throw(
            take(kSyncPosixRegularFileSnapshotMetadataEncodedBytes, field),
            std::string(label_) + " " + std::string(field));
    }

    [[nodiscard]] ResumableSha256Checkpoint take_sha_checkpoint() {
        ResumableSha256Checkpoint checkpoint;
        for (std::uint32_t& word : checkpoint.hash_words) {
            word = take_u32("SHA-256 hash word");
        }
        const std::string_view block =
            take(checkpoint.buffered_block.size(), "SHA-256 buffered block");
        std::copy(
            block.begin(), block.end(), checkpoint.buffered_block.begin());
        checkpoint.total_bytes = take_u64("SHA-256 total bytes");
        const std::uint64_t buffered = take_u64("SHA-256 buffered bytes");
        if (buffered > (std::numeric_limits<std::uint32_t>::max)()) {
            invalid(label_, "contains an out-of-range SHA-256 buffered count");
        }
        checkpoint.buffered_bytes = static_cast<std::uint32_t>(buffered);
        return checkpoint;
    }

    [[nodiscard]] bool exhausted() const noexcept {
        return position_ == bytes_.size();
    }

private:
    [[nodiscard]] std::string_view take(
        std::size_t count,
        std::string_view field) {
        if (count > bytes_.size() - position_) {
            invalid(label_, std::string(field) + " is truncated");
        }
        const std::string_view out = bytes_.substr(position_, count);
        position_ += count;
        return out;
    }

    std::string_view bytes_;
    std::string_view label_;
    std::size_t position_ = 0U;
};

void append_sha_checkpoint(
    std::string& output,
    const ResumableSha256Checkpoint& checkpoint) {
    for (const std::uint32_t word : checkpoint.hash_words) {
        append_u32(output, word);
    }
    output.append(
        reinterpret_cast<const char*>(checkpoint.buffered_block.data()),
        checkpoint.buffered_block.size());
    append_u64(output, checkpoint.total_bytes);
    append_u64(output, checkpoint.buffered_bytes);
}

void validate_limits_or_throw(
    std::uint64_t maximum_payload_bytes,
    std::uint64_t maximum_chunk_count,
    std::string_view label) {
    if (maximum_payload_bytes == 0U) {
        invalid(label, "payload byte frontier is zero");
    }
    if (maximum_chunk_count == 0U ||
        maximum_chunk_count >
            kSyncReplicaSourceManifestCheckpointMaximumChunks) {
        invalid(label, "chunk-count frontier is outside the supported range");
    }
}

void validate_checkpoint_or_throw(
    const SyncReplicaSourceManifestCheckpoint& checkpoint,
    std::uint64_t maximum_payload_bytes,
    std::uint64_t maximum_chunk_count,
    std::string_view label) {
    validate_limits_or_throw(
        maximum_payload_bytes, maximum_chunk_count, label);
    if (!is_lowercase_sha256_hex(checkpoint.store_identity_sha256)) {
        invalid(label, "store-identity digest is invalid");
    }
    validate_sync_posix_private_single_link_regular_file_snapshot_metadata_or_throw(
        checkpoint.store_identity_metadata, std::nullopt,
        std::string(label) + " store identity");
    if (checkpoint.generation == 0U) {
        invalid(label, "generation is zero");
    }
    if (!is_lowercase_sha256_hex(checkpoint.operation_id)) {
        invalid(label, "operation digest is invalid");
    }
    if (checkpoint.canonical_path.empty() ||
        checkpoint.canonical_path.size() >
            kSyncReplicaSourceManifestCheckpointMaximumCanonicalPathBytes) {
        invalid(label, "canonical path exceeds its byte frontier");
    }
    const SyncValidationResult path =
        validate_sync_relative_path(checkpoint.canonical_path);
    if (!path.ok) {
        invalid(label, "canonical path is invalid: " + path.reason);
    }
    if (!is_lowercase_sha256_hex(checkpoint.content_sha256)) {
        invalid(label, "content digest is invalid");
    }
    if (checkpoint.total_size_bytes == 0U ||
        checkpoint.total_size_bytes > maximum_payload_bytes) {
        invalid(label, "payload extent is outside the configured frontier");
    }
    validate_sync_posix_private_single_link_regular_file_snapshot_metadata_or_throw(
        checkpoint.payload_metadata, maximum_payload_bytes,
        std::string(label) + " payload");
    if (checkpoint.payload_metadata.size_bytes !=
        checkpoint.total_size_bytes) {
        invalid(label, "payload metadata does not match the exact extent");
    }
    validate_sync_replica_content_defined_chunking_parameters_or_throw(
        checkpoint.parameters, std::string(label) + " parameters");
    if (checkpoint.parameters.maximum_chunk_count != maximum_chunk_count) {
        invalid(label, "chunk-count parameter does not match the durable frontier");
    }
    if (checkpoint.chunks.size() > maximum_chunk_count) {
        invalid(label, "chunk vector is outside the durable frontier");
    }
    validate_resumable_sha256_checkpoint_or_throw(
        checkpoint.whole_hash, std::string(label) + " whole hash");
    validate_resumable_sha256_checkpoint_or_throw(
        checkpoint.current_chunk_hash,
        std::string(label) + " current chunk hash");
    validate_sync_replica_content_defined_chunker_checkpoint_or_throw(
        checkpoint.parameters, checkpoint.chunker,
        std::string(label) + " rolling chunker");
    if (checkpoint.whole_hash.total_bytes !=
        checkpoint.next_offset_bytes) {
        invalid(label, "whole-hash continuation is not at the byte frontier");
    }
    if (checkpoint.current_chunk_hash.total_bytes !=
        checkpoint.chunker.pending_chunk_bytes) {
        invalid(label, "current-chunk hash does not match rolling extent");
    }
    if (checkpoint.chunker.completed_chunk_count !=
        checkpoint.chunks.size()) {
        invalid(label, "rolling chunk count does not match retained chunks");
    }

    std::uint64_t chunk_bytes = 0U;
    for (std::size_t index = 0U; index < checkpoint.chunks.size(); ++index) {
        const auto& chunk = checkpoint.chunks[index];
        const bool final_complete_chunk =
            checkpoint.disposition ==
                SyncReplicaSourceManifestCheckpointDisposition::CompleteManifest &&
            index + 1U == checkpoint.chunks.size();
        if (chunk.size_bytes == 0U ||
            chunk.size_bytes > checkpoint.parameters.maximum_chunk_bytes ||
            (!final_complete_chunk &&
             chunk.size_bytes < checkpoint.parameters.minimum_chunk_bytes)) {
            invalid(label, "contains a noncanonical chunk extent");
        }
        if (chunk_bytes > checkpoint.total_size_bytes ||
            chunk.size_bytes > checkpoint.total_size_bytes - chunk_bytes) {
            invalid(label, "chunk extents overflow the payload");
        }
        chunk_bytes += chunk.size_bytes;
    }
    if (chunk_bytes != checkpoint.completed_chunk_bytes) {
        invalid(label, "chunk extents do not match the completed frontier");
    }
    if (checkpoint.completed_chunk_bytes > checkpoint.next_offset_bytes ||
        checkpoint.chunker.pending_chunk_bytes >
            checkpoint.next_offset_bytes - checkpoint.completed_chunk_bytes ||
        checkpoint.completed_chunk_bytes +
                checkpoint.chunker.pending_chunk_bytes !=
            checkpoint.next_offset_bytes) {
        invalid(label, "completed and rolling extents do not reach the byte frontier");
    }

    switch (checkpoint.disposition) {
        case SyncReplicaSourceManifestCheckpointDisposition::
                ActiveProjection:
            if (checkpoint.next_offset_bytes == 0U ||
                checkpoint.next_offset_bytes >= checkpoint.total_size_bytes ||
                checkpoint.chunker.finished) {
                invalid(label, "active record is not a nonterminal byte frontier");
            }
            if (!checkpoint.manifest_digest.empty()) {
                invalid(label, "active record carries a complete-manifest digest");
            }
            if (checkpoint.chunks.size() == maximum_chunk_count &&
                checkpoint.chunker.pending_chunk_bytes == 0U) {
                invalid(label, "active record exhausted its chunk-count frontier");
            }
            break;
        case SyncReplicaSourceManifestCheckpointDisposition::CompleteManifest: {
            if (checkpoint.next_offset_bytes != checkpoint.total_size_bytes ||
                checkpoint.completed_chunk_bytes != checkpoint.total_size_bytes ||
                !checkpoint.chunker.finished ||
                checkpoint.chunker.pending_chunk_bytes != 0U ||
                checkpoint.chunks.empty()) {
                invalid(label, "complete record does not cover the payload");
            }
            if (checkpoint.current_chunk_hash !=
                ResumableSha256{}.checkpoint()) {
                invalid(label, "complete record retains a noninitial chunk hash");
            }
            if (!is_lowercase_sha256_hex(checkpoint.manifest_digest)) {
                invalid(label, "complete-manifest digest is invalid");
            }
            ResumableSha256 whole(checkpoint.whole_hash,
                                  std::string(label) + " terminal whole hash");
            if (whole.finish_hex() != checkpoint.content_sha256) {
                invalid(label, "complete record whole digest does not match content");
            }
            break;
        }
        default:
            invalid(label, "contains an unknown disposition");
    }
}

}  // namespace

SyncReplicaSourceManifestCheckpointChunk::
SyncReplicaSourceManifestCheckpointChunk(
    std::uint64_t size_bytes_value,
    std::string_view sha256_hex_value)
    : size_bytes(size_bytes_value),
      sha256(sha256_hex_value) {}

SyncReplicaSourceManifestCheckpointChunk::
SyncReplicaSourceManifestCheckpointChunk(
    std::uint64_t size_bytes_value,
    Sha256DigestValue sha256_value) noexcept
    : size_bytes(size_bytes_value),
      sha256(std::move(sha256_value)) {}

std::string SyncReplicaSourceManifestCheckpointChunk::sha256_hex() const {
    return sha256.lowercase_hex();
}

std::uint64_t sync_replica_source_manifest_checkpoint_maximum_bytes(
    std::uint64_t maximum_chunk_count) noexcept {
    if (maximum_chunk_count >
        kSyncReplicaSourceManifestCheckpointMaximumChunks) {
        return 0U;
    }
    return static_cast<std::uint64_t>(kMagic.size()) +
        kFixedBodyMaximumBytes + maximum_chunk_count * kChunkBytes +
        kDigestTextBytes;
}

std::string serialize_sync_replica_source_manifest_checkpoint_or_throw(
    const SyncReplicaSourceManifestCheckpoint& checkpoint,
    std::uint64_t maximum_payload_bytes,
    std::uint64_t maximum_chunk_count,
    std::string_view label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "source manifest checkpoint serialization label must not be empty");
    }
    validate_checkpoint_or_throw(
        checkpoint, maximum_payload_bytes, maximum_chunk_count, label);

    std::string output;
    output.reserve(static_cast<std::size_t>(
        sync_replica_source_manifest_checkpoint_maximum_bytes(
            maximum_chunk_count)));
    output.append(kMagic);
    output.append(checkpoint.store_identity_sha256);
    append_sync_posix_regular_file_snapshot_metadata_binary(
        output, checkpoint.store_identity_metadata);
    append_u64(output, checkpoint.generation);
    output.append(checkpoint.operation_id);
    append_u64(output, checkpoint.canonical_path.size());
    output.append(checkpoint.canonical_path);
    output.append(checkpoint.content_sha256);
    append_u64(output, checkpoint.total_size_bytes);
    append_sync_posix_regular_file_snapshot_metadata_binary(
        output, checkpoint.payload_metadata);
    append_u64(output, checkpoint.parameters.minimum_chunk_bytes);
    append_u64(output, checkpoint.parameters.average_chunk_bytes);
    append_u64(output, checkpoint.parameters.maximum_chunk_bytes);
    append_u64(output, checkpoint.parameters.maximum_chunk_count);
    append_u64(output, static_cast<std::uint64_t>(checkpoint.disposition));
    append_u64(output, checkpoint.next_offset_bytes);
    append_u64(output, checkpoint.completed_chunk_bytes);
    append_sha_checkpoint(output, checkpoint.whole_hash);
    append_sha_checkpoint(output, checkpoint.current_chunk_hash);
    append_u64(output, checkpoint.chunker.gear_hash);
    append_u64(output, checkpoint.chunker.pending_chunk_bytes);
    append_u64(output, checkpoint.chunker.completed_chunk_count);
    append_u64(output, checkpoint.chunker.finished ? 1U : 0U);
    append_u64(output, checkpoint.chunks.size());
    for (const auto& chunk : checkpoint.chunks) {
        append_u64(output, chunk.size_bytes);
        chunk.sha256.append_binary_to(output);
    }
    if (checkpoint.disposition ==
        SyncReplicaSourceManifestCheckpointDisposition::CompleteManifest) {
        output.append(checkpoint.manifest_digest);
    }
    output.append(sha256_hex(output));
    const std::uint64_t maximum_bytes =
        sync_replica_source_manifest_checkpoint_maximum_bytes(
            maximum_chunk_count);
    if (output.size() > maximum_bytes) {
        throw std::logic_error(
            std::string(label) + " encoded extent exceeded its maximum");
    }
    return output;
}

SyncReplicaSourceManifestCheckpoint
parse_sync_replica_source_manifest_checkpoint_or_throw(
    std::string_view bytes,
    std::uint64_t maximum_payload_bytes,
    std::uint64_t maximum_chunk_count,
    std::string_view label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "source manifest checkpoint parse label must not be empty");
    }
    validate_limits_or_throw(
        maximum_payload_bytes, maximum_chunk_count, label);
    const std::uint64_t maximum_bytes =
        sync_replica_source_manifest_checkpoint_maximum_bytes(
            maximum_chunk_count);
    if (bytes.size() > maximum_bytes ||
        bytes.size() < kMagic.size() + kDigestTextBytes) {
        invalid(label, "encoded extent is outside its fixed frontier");
    }
    if (!bytes.starts_with(kMagic)) {
        invalid(label, "magic/version is invalid");
    }
    const std::size_t framed_size = bytes.size() - kDigestTextBytes;
    const std::string_view expected_checksum = bytes.substr(framed_size);
    if (!is_lowercase_sha256_hex(expected_checksum) ||
        sha256_hex(std::string(bytes.substr(0U, framed_size))) !=
            expected_checksum) {
        invalid(label, "checksum is invalid");
    }

    Cursor cursor(
        bytes.substr(kMagic.size(), framed_size - kMagic.size()), label);
    SyncReplicaSourceManifestCheckpoint checkpoint;
    checkpoint.store_identity_sha256 = cursor.take_digest("store-identity");
    checkpoint.store_identity_metadata = cursor.take_metadata("store identity");
    checkpoint.generation = cursor.take_u64("generation");
    checkpoint.operation_id = cursor.take_digest("operation");
    checkpoint.canonical_path = cursor.take_string(
        kSyncReplicaSourceManifestCheckpointMaximumCanonicalPathBytes,
        "canonical path");
    checkpoint.content_sha256 = cursor.take_digest("content");
    checkpoint.total_size_bytes = cursor.take_u64("total size");
    checkpoint.payload_metadata = cursor.take_metadata("payload metadata");
    checkpoint.parameters.minimum_chunk_bytes = cursor.take_u64("minimum chunk");
    checkpoint.parameters.average_chunk_bytes = cursor.take_u64("average chunk");
    checkpoint.parameters.maximum_chunk_bytes = cursor.take_u64("maximum chunk");
    checkpoint.parameters.maximum_chunk_count = cursor.take_u64("maximum chunks");
    checkpoint.disposition =
        static_cast<SyncReplicaSourceManifestCheckpointDisposition>(
            cursor.take_u64("disposition"));
    checkpoint.next_offset_bytes = cursor.take_u64("next offset");
    checkpoint.completed_chunk_bytes = cursor.take_u64("completed bytes");
    checkpoint.whole_hash = cursor.take_sha_checkpoint();
    checkpoint.current_chunk_hash = cursor.take_sha_checkpoint();
    checkpoint.chunker.gear_hash = cursor.take_u64("rolling gear hash");
    checkpoint.chunker.pending_chunk_bytes =
        cursor.take_u64("rolling pending bytes");
    checkpoint.chunker.completed_chunk_count =
        cursor.take_u64("rolling completed chunks");
    const std::uint64_t finished = cursor.take_u64("rolling finished flag");
    if (finished > 1U) {
        invalid(label, "rolling finished flag is not canonical");
    }
    checkpoint.chunker.finished = finished != 0U;
    const std::uint64_t chunk_count = cursor.take_u64("chunk count");
    if (chunk_count > maximum_chunk_count ||
        chunk_count > static_cast<std::uint64_t>(
            (std::numeric_limits<std::size_t>::max)())) {
        invalid(label, "chunk count exceeds its durable frontier");
    }
    checkpoint.chunks.reserve(static_cast<std::size_t>(chunk_count));
    for (std::uint64_t index = 0U; index < chunk_count; ++index) {
        SyncReplicaSourceManifestCheckpointChunk chunk;
        chunk.size_bytes = cursor.take_u64("chunk size");
        chunk.sha256 = cursor.take_binary_digest("chunk");
        checkpoint.chunks.push_back(chunk);
    }
    if (checkpoint.disposition ==
        SyncReplicaSourceManifestCheckpointDisposition::CompleteManifest) {
        checkpoint.manifest_digest = cursor.take_digest("manifest");
    }
    if (!cursor.exhausted()) {
        invalid(label, "contains trailing body bytes");
    }
    validate_checkpoint_or_throw(
        checkpoint, maximum_payload_bytes, maximum_chunk_count, label);
    return checkpoint;
}

}  // namespace anonsync

#endif
