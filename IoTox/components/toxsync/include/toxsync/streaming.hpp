#pragma once

#include "toxsync/index_file.hpp"
#include "toxsync/range_source.hpp"

#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <memory>
#include <vector>

namespace toxsync {

struct StreamingSyncOptions {
    std::size_t io_buffer_bytes{1024U * 1024U};
    std::size_t max_source_ranges_per_batch{256U};
    bool resume{true};
    bool fsync_on_commit{true};
    bool advise_sequential_io{true};
    IndexLimits limits{};
};

// A session arena that can be retained across many artifacts or namespaces.
// The data, index-record, and one-bit block-state arrays are allocated with
// overwrite semantics and are not zero-filled on growth. Range descriptors
// retain capacity but are cleared before every batch.
class StreamingWorkspace final {
public:
    StreamingWorkspace() = default;
    ~StreamingWorkspace() = default;
    StreamingWorkspace(StreamingWorkspace&&) noexcept = default;
    StreamingWorkspace& operator=(StreamingWorkspace&&) noexcept = default;
    StreamingWorkspace(const StreamingWorkspace&) = delete;
    StreamingWorkspace& operator=(const StreamingWorkspace&) = delete;

    [[nodiscard]] std::size_t resident_bytes() const noexcept {
        return data_capacity_ + record_capacity_ + state_capacity_ +
               ranges_.capacity() * sizeof(RangeRead);
    }
    void release() noexcept {
        data_.reset();
        records_.reset();
        state_.reset();
        data_capacity_ = 0U;
        record_capacity_ = 0U;
        state_capacity_ = 0U;
        std::vector<RangeRead>().swap(ranges_);
    }

private:
    friend struct StreamingWorkspaceAccess;
    std::unique_ptr<std::byte[]> data_{};
    std::unique_ptr<std::byte[]> records_{};
    std::unique_ptr<std::uint8_t[]> state_{};
    std::vector<RangeRead> ranges_{};
    std::size_t data_capacity_{};
    std::size_t record_capacity_{};
    std::size_t state_capacity_{};
};

struct StreamingSyncStats {
    IndexFileMetadata metadata{};
    std::uint64_t resumed_bytes{};
    std::uint64_t discarded_resume_bytes{};
    std::uint64_t reused_bytes{};
    std::uint64_t fetched_bytes{};
    std::uint64_t matched_blocks{};
    std::uint64_t missing_blocks{};
    std::uint64_t basis_read_calls{};
    std::uint64_t partial_read_calls{};
    std::uint64_t index_read_calls{};
    std::uint64_t source_batch_calls{};
    std::uint64_t source_ranges{};
    std::uint64_t output_write_calls{};
    std::uint64_t sync_calls{};
    std::size_t data_buffer_bytes{};
    std::size_t index_buffer_bytes{};
    std::size_t block_state_bytes{};
    std::size_t range_descriptor_bytes{};
    std::size_t workspace_reserved_bytes{};
    std::uint32_t workspace_growth_events{};
    Digest256 output_digest{};

    [[nodiscard]] std::size_t peak_working_bytes() const noexcept {
        return data_buffer_bytes + index_buffer_bytes + block_state_bytes +
               range_descriptor_bytes;
    }
};

// Memory-bounded v1 path. It intentionally checks reuse only at the expected
// target offset; callers that need shifted-block discovery can retain the
// legacy Index + plan_file exhaustive rolling path.
[[nodiscard]] StreamingSyncStats sync_file_streaming(
    const std::filesystem::path& index_path,
    const std::filesystem::path& basis,
    RangeSource& source,
    const std::filesystem::path& output,
    const StreamingSyncOptions& options = {});

[[nodiscard]] StreamingSyncStats sync_file_streaming(
    const std::filesystem::path& index_path,
    const std::filesystem::path& basis,
    RangeSource& source,
    const std::filesystem::path& output,
    StreamingWorkspace& workspace,
    const StreamingSyncOptions& options = {});

} // namespace toxsync
