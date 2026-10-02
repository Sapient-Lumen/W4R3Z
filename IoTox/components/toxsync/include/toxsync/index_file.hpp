#pragma once

#include "toxsync/hash.hpp"
#include "toxsync/index.hpp"

#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <memory>

namespace toxsync {

struct AutoBlockSizeOptions {
    std::uint64_t metadata_budget_bytes{64ULL * 1024ULL * 1024ULL};
    std::uint32_t min_block_size{4096U};
    std::uint32_t max_block_size{16U * 1024U * 1024U};
    bool power_of_two{true};
};

struct IndexFileMetadata {
    std::uint32_t block_size{};
    std::uint64_t target_size{};
    std::uint64_t block_count{};
    Digest256 target_digest{};

    [[nodiscard]] std::uint64_t encoded_size() const noexcept;
};

struct IndexFileBuildOptions {
    // Zero selects the smallest block size that satisfies auto_block's
    // metadata budget. A nonzero value preserves byte compatibility with the
    // original in-memory v1 index builder.
    std::uint32_t block_size{};
    std::size_t io_buffer_bytes{1024U * 1024U};
    std::size_t record_buffer_bytes{64U * 1024U};
    bool fsync_on_commit{true};
    bool advise_sequential_io{true};
    bool discard_input_cache{false};
    AutoBlockSizeOptions auto_block{};
    IndexLimits limits{};
};

// Reusable, overwrite-only storage for repeated index builds. Buffers grow
// geometrically only when a later job needs more space; ordinary reuse makes
// zero heap-growth calls on the index hot path.
class IndexBuildWorkspace final {
public:
    IndexBuildWorkspace() = default;
    ~IndexBuildWorkspace() = default;
    IndexBuildWorkspace(IndexBuildWorkspace&&) noexcept = default;
    IndexBuildWorkspace& operator=(IndexBuildWorkspace&&) noexcept = default;
    IndexBuildWorkspace(const IndexBuildWorkspace&) = delete;
    IndexBuildWorkspace& operator=(const IndexBuildWorkspace&) = delete;

    [[nodiscard]] std::size_t resident_bytes() const noexcept {
        return data_capacity_ + record_capacity_;
    }
    void release() noexcept {
        data_.reset();
        records_.reset();
        data_capacity_ = 0U;
        record_capacity_ = 0U;
    }

private:
    friend struct IndexWorkspaceAccess;
    std::unique_ptr<std::byte[]> data_{};
    std::unique_ptr<std::byte[]> records_{};
    std::size_t data_capacity_{};
    std::size_t record_capacity_{};
};

struct IndexFileBuildStats {
    IndexFileMetadata metadata{};
    std::uint64_t target_read_calls{};
    std::uint64_t index_write_calls{};
    std::size_t data_buffer_bytes{};
    std::size_t record_buffer_bytes{};
    std::size_t workspace_reserved_bytes{};
    std::uint32_t workspace_growth_events{};

    [[nodiscard]] std::size_t peak_working_bytes() const noexcept {
        return data_buffer_bytes + record_buffer_bytes;
    }
};

[[nodiscard]] std::uint64_t index_metadata_bytes(std::uint64_t target_size,
                                                 std::uint32_t block_size);

[[nodiscard]] std::uint32_t choose_block_size(
    std::uint64_t target_size,
    const AutoBlockSizeOptions& options = {});

// Reads and validates only the fixed header and encoded length. It does not
// allocate a BlockRecord per target block.
[[nodiscard]] IndexFileMetadata inspect_index_file(
    const std::filesystem::path& index_path,
    const IndexLimits& limits = {});

// Writes a byte-compatible toxsync index directly to disk. Peak heap is
// bounded by the two configured buffers rather than target block count.
[[nodiscard]] IndexFileBuildStats build_index_file(
    const std::filesystem::path& target,
    const std::filesystem::path& index_path,
    const IndexFileBuildOptions& options = {});

[[nodiscard]] IndexFileBuildStats build_index_file(
    const std::filesystem::path& target,
    const std::filesystem::path& index_path,
    IndexBuildWorkspace& workspace,
    const IndexFileBuildOptions& options = {});

[[nodiscard]] bool verify_indexed_file(
    const std::filesystem::path& index_path,
    const std::filesystem::path& artifact,
    const IndexLimits& limits = {});

} // namespace toxsync
