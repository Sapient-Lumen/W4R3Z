#pragma once

#include "sync_replica_reconciliation_protocol.hpp"

#include <cstddef>
#include <cstdint>
#include <string>
#include <string_view>
#include <type_traits>
#include <vector>

namespace anonsync {

// One cache-only chunk record. The cumulative exclusive end offset replaces
// both the ordinary manifest's per-chunk size and the separate chunk-offset
// vector retained before rev1012. The same fixed record is now also the
// non-owning direct-frame source, so cache-cold publication can serialize it
// without first allocating a second complete manifest vector.
using SyncReplicaReconciliationCompactManifestChunk =
    SyncReplicaReconciliationCumulativeDeltaChunk;

static_assert(
    sizeof(SyncReplicaReconciliationCompactManifestChunk) == 40U,
    "compact reconciliation manifest chunks must remain 40-byte records");
static_assert(
    std::is_trivially_copyable_v<
        SyncReplicaReconciliationCompactManifestChunk>,
    "compact reconciliation manifest chunks must not own hidden heap state");

// Process-local exact source-manifest cache. It preserves the complete bounded
// content-defined sequence in one contiguous fixed-width vector. This is not a
// new wire format or durable authority. The shipping direct-frame path borrows
// this exact sequence only until canonical generation-9 framing finishes;
// compatibility and test callers may still request an owning materialization.
class SyncReplicaReconciliationCompactManifest final {
public:
    [[nodiscard]] static SyncReplicaReconciliationCompactManifest
    from_manifest_or_throw(
        std::uint64_t total_size_bytes,
        const SyncReplicaReconciliationDeltaManifest& manifest,
        std::string_view label = "compact reconciliation manifest");

    [[nodiscard]] const SyncReplicaContentDefinedChunkingParameters&
    parameters() const noexcept {
        return parameters_;
    }

    [[nodiscard]] std::uint64_t total_size_bytes() const noexcept {
        return total_size_bytes_;
    }

    [[nodiscard]] std::size_t chunk_count() const noexcept {
        return chunks_.size();
    }

    [[nodiscard]] std::uint64_t retained_chunk_capacity_bytes() const noexcept;

    // Borrows the exact retained cumulative sequence for one direct response
    // frame. The view becomes invalid when this manifest is destroyed or
    // mutated; callers must finish framing before either can occur.
    [[nodiscard]] SyncReplicaReconciliationBorrowedDeltaManifest
    borrow_for_direct_frame() const noexcept {
        return {parameters_, total_size_bytes_, chunks_};
    }

    [[nodiscard]] std::size_t chunk_index_for_offset_or_throw(
        std::uint64_t offset_bytes,
        std::string_view label = "compact reconciliation manifest lookup")
        const;

    [[nodiscard]] std::uint64_t chunk_offset_bytes_or_throw(
        std::size_t chunk_index,
        std::string_view label = "compact reconciliation manifest chunk")
        const;

    [[nodiscard]] std::uint64_t chunk_end_offset_bytes_or_throw(
        std::size_t chunk_index,
        std::string_view label = "compact reconciliation manifest chunk")
        const;

    [[nodiscard]] std::uint64_t chunk_size_bytes_or_throw(
        std::size_t chunk_index,
        std::string_view label = "compact reconciliation manifest chunk")
        const;

    [[nodiscard]] std::string chunk_sha256_hex_or_throw(
        std::size_t chunk_index,
        std::string_view label = "compact reconciliation manifest chunk")
        const;

    [[nodiscard]] SyncReplicaReconciliationDeltaManifest materialize_or_throw(
        std::string_view label = "compact reconciliation manifest materialization")
        const;

    bool operator==(
        const SyncReplicaReconciliationCompactManifest&) const = default;

private:
    [[nodiscard]] const SyncReplicaReconciliationCompactManifestChunk&
    chunk_or_throw(std::size_t chunk_index, std::string_view label) const;

    SyncReplicaContentDefinedChunkingParameters parameters_;
    std::uint64_t total_size_bytes_ = 0U;
    std::vector<SyncReplicaReconciliationCompactManifestChunk> chunks_;
};

}  // namespace anonsync
