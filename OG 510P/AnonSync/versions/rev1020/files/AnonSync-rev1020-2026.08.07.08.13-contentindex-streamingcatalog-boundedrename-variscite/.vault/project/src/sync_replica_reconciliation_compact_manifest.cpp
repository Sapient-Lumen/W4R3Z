#include "sync_replica_reconciliation_compact_manifest.hpp"

#include "sha256_digest.hpp"

#include <algorithm>
#include <limits>
#include <stdexcept>
#include <string>
#include <utility>

namespace anonsync {
namespace {

[[noreturn]] void invalid(
    std::string_view label,
    std::string_view reason) {
    throw std::invalid_argument(
        std::string(label) + " " + std::string(reason));
}


}  // namespace

SyncReplicaReconciliationCompactManifest
SyncReplicaReconciliationCompactManifest::from_manifest_or_throw(
    std::uint64_t total_size_bytes,
    const SyncReplicaReconciliationDeltaManifest& manifest,
    std::string_view label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "compact reconciliation manifest label must not be empty");
    }
    const SyncReplicaContentDefinedChunkingParameters canonical =
        sync_replica_reconciliation_content_defined_parameters_or_throw(
            total_size_bytes);
    if (manifest.parameters != canonical) {
        invalid(label, "uses noncanonical content-defined parameters");
    }
    if (manifest.chunks.empty() ||
        manifest.chunks.size() >
            kSyncReplicaReconciliationMaximumContentDefinedChunks) {
        invalid(label, "chunk count is outside its bounded frontier");
    }

    SyncReplicaReconciliationCompactManifest compact;
    compact.parameters_ = manifest.parameters;
    compact.total_size_bytes_ = total_size_bytes;
    compact.chunks_.reserve(manifest.chunks.size());

    std::uint64_t covered = 0U;
    for (std::size_t index = 0U; index < manifest.chunks.size(); ++index) {
        const SyncReplicaReconciliationDeltaChunk& chunk =
            manifest.chunks[index];
        if (chunk.size_bytes == 0U ||
            chunk.size_bytes > manifest.parameters.maximum_chunk_bytes ||
            (index + 1U != manifest.chunks.size() &&
             chunk.size_bytes < manifest.parameters.minimum_chunk_bytes)) {
            invalid(label, "contains an invalid chunk extent");
        }
        if (chunk.size_bytes > total_size_bytes - covered) {
            invalid(label, "chunk extents exceed the payload");
        }
        covered += chunk.size_bytes;
        compact.chunks_.push_back({covered, chunk.sha256});
    }
    if (covered != total_size_bytes) {
        invalid(label, "chunk extents do not cover the payload");
    }
    return compact;
}

std::uint64_t
SyncReplicaReconciliationCompactManifest::retained_chunk_capacity_bytes()
    const noexcept {
    static_assert(
        kSyncReplicaReconciliationMaximumContentDefinedChunks <=
        std::numeric_limits<std::uint64_t>::max() /
            sizeof(SyncReplicaReconciliationCompactManifestChunk));
    return static_cast<std::uint64_t>(chunks_.capacity()) *
           sizeof(SyncReplicaReconciliationCompactManifestChunk);
}

const SyncReplicaReconciliationCompactManifestChunk&
SyncReplicaReconciliationCompactManifest::chunk_or_throw(
    std::size_t chunk_index,
    std::string_view label) const {
    if (chunk_index >= chunks_.size()) {
        invalid(label, "index is outside the retained chunk frontier");
    }
    return chunks_[chunk_index];
}

std::size_t
SyncReplicaReconciliationCompactManifest::chunk_index_for_offset_or_throw(
    std::uint64_t offset_bytes,
    std::string_view label) const {
    if (offset_bytes >= total_size_bytes_) {
        invalid(label, "offset is outside the payload");
    }
    const auto found = std::upper_bound(
        chunks_.begin(), chunks_.end(), offset_bytes,
        [](std::uint64_t offset,
           const SyncReplicaReconciliationCompactManifestChunk& chunk) {
            return offset < chunk.end_offset_bytes;
        });
    if (found == chunks_.end()) {
        throw std::logic_error(
            std::string(label) +
            " compact chunk sequence ended before its payload");
    }
    return static_cast<std::size_t>(found - chunks_.begin());
}

std::uint64_t
SyncReplicaReconciliationCompactManifest::chunk_offset_bytes_or_throw(
    std::size_t chunk_index,
    std::string_view label) const {
    (void)chunk_or_throw(chunk_index, label);
    return chunk_index == 0U ? 0U : chunks_[chunk_index - 1U].end_offset_bytes;
}

std::uint64_t
SyncReplicaReconciliationCompactManifest::chunk_end_offset_bytes_or_throw(
    std::size_t chunk_index,
    std::string_view label) const {
    return chunk_or_throw(chunk_index, label).end_offset_bytes;
}

std::uint64_t
SyncReplicaReconciliationCompactManifest::chunk_size_bytes_or_throw(
    std::size_t chunk_index,
    std::string_view label) const {
    const std::uint64_t end =
        chunk_end_offset_bytes_or_throw(chunk_index, label);
    return end - chunk_offset_bytes_or_throw(chunk_index, label);
}

std::string
SyncReplicaReconciliationCompactManifest::chunk_sha256_hex_or_throw(
    std::size_t chunk_index,
    std::string_view label) const {
    return chunk_or_throw(chunk_index, label).sha256.lowercase_hex();
}

SyncReplicaReconciliationDeltaManifest
SyncReplicaReconciliationCompactManifest::materialize_or_throw(
    std::string_view label) const {
    if (label.empty()) {
        throw std::invalid_argument(
            "compact reconciliation manifest materialization label must not be empty");
    }
    if (chunks_.empty() || total_size_bytes_ == 0U) {
        throw std::logic_error(
            std::string(label) + " compact manifest is not initialized");
    }
    SyncReplicaReconciliationDeltaManifest manifest;
    manifest.parameters = parameters_;
    manifest.chunks.reserve(chunks_.size());
    std::uint64_t preceding = 0U;
    for (const auto& chunk : chunks_) {
        if (chunk.end_offset_bytes <= preceding) {
            throw std::logic_error(
                std::string(label) +
                " compact chunk sequence is not strictly increasing");
        }
        manifest.chunks.push_back({
            chunk.end_offset_bytes - preceding,
            chunk.sha256,
        });
        preceding = chunk.end_offset_bytes;
    }
    if (preceding != total_size_bytes_) {
        throw std::logic_error(
            std::string(label) +
            " compact chunk sequence does not cover its payload");
    }
    return manifest;
}

}  // namespace anonsync
