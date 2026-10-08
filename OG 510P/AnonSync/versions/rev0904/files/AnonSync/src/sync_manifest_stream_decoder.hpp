#pragma once

#include "sync_manifest_validation.hpp"

#include <cstdint>
#include <string>
#include <string_view>

namespace anonsync {

// Borrowed scalar observations for one persisted or wire manifest entry. The
// decoder copies these bytes only after all declared row counts, path bytes,
// and base metadata bytes have been admitted by the supplied resource policy.
struct SyncManifestEntryStreamHeader final {
    std::string_view folder_id;
    std::string_view device_id;
    std::string_view path;
    SyncManifestEntryKind kind = SyncManifestEntryKind::File;
    std::uint64_t size_bytes = 0;
    std::string_view content_sha256;
    std::string_view conflict_set_id;
    std::uint64_t declared_chunk_count = 0;
    std::uint64_t declared_lineage_count = 0;
};

// A single-use incremental decoder for one manifest entry. The owner never
// publishes a partially reconstructed entry. Any malformed or over-budget
// event permanently fails the instance; finish() commits the complete value
// and exact usage evidence only after independent typed validation agrees with
// the incremental accounting.
class SyncManifestEntryStreamDecoder final {
public:
    SyncManifestEntryStreamDecoder() = default;
    ~SyncManifestEntryStreamDecoder() = default;

    SyncManifestEntryStreamDecoder(
        const SyncManifestEntryStreamDecoder&) = delete;
    SyncManifestEntryStreamDecoder& operator=(
        const SyncManifestEntryStreamDecoder&) = delete;
    SyncManifestEntryStreamDecoder(
        SyncManifestEntryStreamDecoder&&) = delete;
    SyncManifestEntryStreamDecoder& operator=(
        SyncManifestEntryStreamDecoder&&) = delete;

    [[nodiscard]] SyncValidationResult begin(
        const SyncManifestEntryStreamHeader& header,
        const SyncManifestResourceLimits& limits =
            sync_manifest_default_resource_limits());

    [[nodiscard]] SyncValidationResult append_chunk(
        std::uint64_t offset,
        std::uint64_t length,
        std::string_view sha256);

    [[nodiscard]] SyncValidationResult append_lineage(
        std::string_view device_id,
        std::uint64_t counter);

    [[nodiscard]] SyncValidationResult finish(
        SyncManifestEntry& out,
        SyncManifestResourceUsage* usage_out = nullptr);

    [[nodiscard]] bool active() const noexcept;
    [[nodiscard]] bool failed() const noexcept;
    [[nodiscard]] std::uint64_t chunks_accepted() const noexcept;
    [[nodiscard]] std::uint64_t lineage_entries_accepted() const noexcept;

private:
    enum class State : std::uint8_t {
        Empty,
        Active,
        Failed,
        Finished,
    };

    [[nodiscard]] SyncValidationResult state_failure(
        std::string_view operation) const;
    [[nodiscard]] SyncValidationResult fail(std::string reason);

    State state_ = State::Empty;
    SyncManifestResourceLimits limits_{};
    SyncManifestResourceBudget budget_{
        sync_manifest_default_resource_limits()};
    SyncManifestEntry candidate_{};
    std::uint64_t declared_chunk_count_ = 0;
    std::uint64_t declared_lineage_count_ = 0;
    std::uint64_t accepted_chunk_count_ = 0;
    std::uint64_t accepted_lineage_count_ = 0;
    std::uint64_t next_chunk_offset_ = 0;
    std::string failure_reason_;
};

}  // namespace anonsync
