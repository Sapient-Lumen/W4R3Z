#pragma once

#include "anonsync_core.hpp"
#include "sync_sqlite_support.hpp"

#include <cstdint>
#include <span>
#include <string>

namespace anonsync {

// Stable semantic accounting for one selected manifest row: offset, length,
// SHA-256 text, and the persisted ordinal used to prove ordering.
inline constexpr std::uint64_t
    kSyncManifestChunkSubsetEvidenceBytesPerRow = 88U;

struct SyncSqliteManifestChunkSubsetLimits final {
    std::uint64_t max_manifest_rows = 0;
    std::uint64_t max_required_rows = 0;
    std::uint64_t max_required_metadata_bytes = 0;
    std::uint64_t max_required_chunk_bytes = 0;
};

struct SyncSqliteManifestChunkSubsetEvidence final {
    std::uint64_t expected_manifest_rows = 0;
    std::uint64_t required_rows = 0;
    std::uint64_t required_metadata_bytes = 0;
    std::uint64_t required_chunk_bytes = 0;
    std::uint64_t first_manifest_chunk_index = 0;
    std::uint64_t last_manifest_chunk_index = 0;
};

[[nodiscard]] std::uint64_t
sync_manifest_chunk_subset_metadata_bytes_or_throw(
    std::uint64_t rows,
    const std::string& label);

// Exact-generation, bounded verifier for an already-selected source-manifest
// subset. The owner never materializes the complete persisted manifest. It
// validates the entire caller value and every budget before issuing its first
// data query, then point-probes only the selected offsets. Its statement is
// explicitly bound to main so a TEMP shadow cannot redirect durable evidence.
class SyncSqliteManifestChunkSubsetVerifier final {
public:
    explicit SyncSqliteManifestChunkSubsetVerifier(
        SyncSqliteDbHandleSlot& db,
        const std::string& label);
    ~SyncSqliteManifestChunkSubsetVerifier() = default;

    SyncSqliteManifestChunkSubsetVerifier(
        const SyncSqliteManifestChunkSubsetVerifier&) = delete;
    SyncSqliteManifestChunkSubsetVerifier& operator=(
        const SyncSqliteManifestChunkSubsetVerifier&) = delete;
    SyncSqliteManifestChunkSubsetVerifier(
        SyncSqliteManifestChunkSubsetVerifier&&) = delete;
    SyncSqliteManifestChunkSubsetVerifier& operator=(
        SyncSqliteManifestChunkSubsetVerifier&&) = delete;

    [[nodiscard]] SyncSqliteManifestChunkSubsetEvidence
    verify_source_chunks_or_throw(
        const std::string& session_id,
        const std::string& normalized_path,
        std::uint64_t file_size_bytes,
        std::uint64_t expected_manifest_rows,
        std::span<const SyncChunkRange> required_chunks,
        const SyncSqliteManifestChunkSubsetLimits& limits,
        const std::string& label);

    [[nodiscard]] std::uint64_t owner_generation() const noexcept;

private:
    SyncSqliteStmt chunk_probe_;
};

}  // namespace anonsync
