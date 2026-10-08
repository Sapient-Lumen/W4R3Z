#pragma once

#include "anonsync_core.hpp"

#include <cstdint>
#include <cstddef>
#include <string_view>

namespace anonsync {

inline constexpr std::uint64_t kSyncManifestIdMaxBytes = 128;
inline constexpr std::uint64_t kSyncManifestRelativePathMaxBytes = 4096;
inline constexpr std::uint64_t kSyncManifestSha256TextBytes = 64;
inline constexpr std::uint64_t kSyncManifestKindTextMaxBytes = 9;

// A typed manifest has already consumed caller memory before it reaches this
// boundary. These limits nevertheless bound every production traversal,
// nested digest, diff, and filesystem plan that follows validation. The
// two-phase validator rejects vector cardinality and aggregate byte budgets
// before inspecting nested element contents.
struct SyncManifestResourceLimits final {
    std::uint64_t max_entries = 100000;
    std::uint64_t max_chunks_per_entry = 262144;
    std::uint64_t max_lineage_entries_per_entry = 4096;
    std::uint64_t max_total_chunks = 1000000;
    std::uint64_t max_total_lineage_entries = 500000;
    std::uint64_t max_total_path_bytes = 64ULL * 1024ULL * 1024ULL;
    std::uint64_t max_total_metadata_bytes = 256ULL * 1024ULL * 1024ULL;
};

struct SyncManifestResourceUsage final {
    std::uint64_t entries = 0;
    std::uint64_t chunks = 0;
    std::uint64_t lineage_entries = 0;
    std::uint64_t path_bytes = 0;
    // String bytes plus fixed-width semantic scalar bytes. This is not an
    // estimate of allocator overhead or serialized JSON size; it is a stable,
    // implementation-independent budget for the typed manifest value.
    std::uint64_t metadata_bytes = 0;
};

// A one-way admission token shared by typed validation and incremental
// decoders. Counts and byte lengths are admitted before the caller traverses or
// copies the corresponding values. Failed admission may leave this token
// consumed; callers must discard it and never publish its partial usage.
class SyncManifestResourceBudget final {
public:
    explicit SyncManifestResourceBudget(
        SyncManifestResourceLimits limits) noexcept;

    SyncManifestResourceBudget(const SyncManifestResourceBudget&) = default;
    SyncManifestResourceBudget& operator=(
        const SyncManifestResourceBudget&) = default;

    [[nodiscard]] SyncValidationResult admit_entry_count(
        std::uint64_t count);

    [[nodiscard]] SyncValidationResult admit_entry_shape(
        std::uint64_t chunk_count,
        std::uint64_t lineage_count,
        std::size_t path_bytes);

    [[nodiscard]] SyncValidationResult admit_metadata_bytes(
        std::size_t bytes);

    [[nodiscard]] const SyncManifestResourceUsage& usage() const noexcept {
        return usage_;
    }

private:
    SyncManifestResourceLimits limits_{};
    SyncManifestResourceUsage usage_{};
    bool entry_count_admitted_ = false;
};

[[nodiscard]] constexpr SyncManifestResourceLimits
sync_manifest_default_resource_limits() noexcept {
    return {};
}

[[nodiscard]] bool sync_id_is_valid(std::string_view value) noexcept;

[[nodiscard]] SyncValidationResult
validate_sync_relative_path(std::string_view raw_path);

// Applies one receiver-local filename-component byte ceiling after the shared
// portable path grammar has succeeded. This is deliberately separate from the
// canonical 4096-byte wire/model limit: filesystems expose NAME_MAX-like local
// effect constraints that must not be promoted into globally canonical path
// identity. The maximum is measured in encoded pathname bytes, not Unicode
// scalar values or display characters.
[[nodiscard]] SyncValidationResult
validate_sync_relative_path_component_byte_limit(
    std::string_view raw_path,
    std::uint64_t maximum_component_bytes);

[[nodiscard]] SyncValidationResult
validate_sync_manifest_entry_with_limits(
    const SyncManifestEntry& entry,
    const SyncManifestResourceLimits& limits,
    SyncManifestResourceUsage* usage_out = nullptr);

[[nodiscard]] SyncValidationResult
validate_sync_folder_manifest_with_limits(
    const SyncFolderManifest& manifest,
    const SyncManifestResourceLimits& limits,
    SyncManifestResourceUsage* usage_out = nullptr);

}  // namespace anonsync
