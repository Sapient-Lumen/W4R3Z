#include "test_harness.hpp"
#include "test_support.hpp"

#include "toxsync/index_file.hpp"
#include "toxsync/range_source.hpp"
#include "toxsync/streaming.hpp"

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <span>
#include <stdexcept>
#include <vector>

namespace {

class MemorySource : public toxsync::RangeSource {
public:
    explicit MemorySource(std::span<const std::byte> bytes) : bytes_(bytes) {}

    std::size_t read_at(std::uint64_t offset, std::span<std::byte> output) override {
        ++read_calls;
        if (offset >= bytes_.size()) return 0U;
        const auto count = std::min<std::size_t>(output.size(), bytes_.size() -
            static_cast<std::size_t>(offset));
        std::memcpy(output.data(), bytes_.data() + static_cast<std::size_t>(offset), count);
        return count;
    }

    void read_many(std::span<toxsync::RangeRead> reads) override {
        ++batch_calls;
        max_batch = std::max(max_batch, reads.size());
        toxsync::RangeSource::read_many(reads);
    }

    std::uint64_t read_calls{};
    std::uint64_t batch_calls{};
    std::size_t max_batch{};

protected:
    std::span<const std::byte> bytes_;
};

class InterruptingSource final : public MemorySource {
public:
    InterruptingSource(std::span<const std::byte> bytes, std::uint64_t successful_batches)
        : MemorySource(bytes), successful_batches_(successful_batches) {}

    void read_many(std::span<toxsync::RangeRead> reads) override {
        if (accepted_batches_ >= successful_batches_) {
            throw std::runtime_error("simulated range transport interruption");
        }
        ++accepted_batches_;
        MemorySource::read_many(reads);
    }

private:
    std::uint64_t successful_batches_{};
    std::uint64_t accepted_batches_{};
};

void build_index(const std::filesystem::path& target,
                 const std::filesystem::path& index,
                 std::uint32_t block = 4096U) {
    toxsync::IndexFileBuildOptions options;
    options.block_size = block;
    options.fsync_on_commit = false;
    static_cast<void>(toxsync::build_index_file(target, index, options));
}

} // namespace

TOXSYNC_TEST(streaming_sync_reuses_aligned_blocks_with_constant_working_memory) {
    test::TempDir temp;
    constexpr std::size_t block = 4096U;
    const auto target = test::pattern(32U * 1024U * 1024U + 77U, 0x600600U);
    auto basis = target;
    for (std::size_t offset = block * 5U; offset < basis.size(); offset += block * 97U) {
        const auto end = std::min(basis.size(), offset + block);
        std::fill(basis.begin() + static_cast<std::ptrdiff_t>(offset),
                  basis.begin() + static_cast<std::ptrdiff_t>(end), std::byte{0x5a});
    }
    test::write_file(temp.path() / "target", target);
    test::write_file(temp.path() / "basis", basis);
    build_index(temp.path() / "target", temp.path() / "target.txi", block);

    MemorySource source(target);
    toxsync::StreamingSyncOptions options;
    options.io_buffer_bytes = 1024U * 1024U;
    options.fsync_on_commit = false;
    const auto stats = toxsync::sync_file_streaming(
        temp.path() / "target.txi", temp.path() / "basis", source,
        temp.path() / "output", options);

    REQUIRE(test::read_file(temp.path() / "output") == target);
    REQUIRE(stats.reused_bytes + stats.fetched_bytes == target.size());
    REQUIRE(stats.reused_bytes > stats.fetched_bytes);
    REQUIRE(stats.peak_working_bytes() < 2U * 1024U * 1024U);
    REQUIRE(stats.block_state_bytes == 32U);  // 256 batch blocks, one bit each.
    REQUIRE(stats.metadata.block_count > 8000U);
}

TOXSYNC_TEST(streaming_sync_uses_batched_discontiguous_source_ranges) {
    test::TempDir temp;
    constexpr std::size_t block = 4096U;
    const auto target = test::pattern(block * 32U, 0x9911U);
    auto basis = target;
    for (std::size_t i = 0; i < 32U; i += 2U) {
        basis[i * block] ^= std::byte{0xff};
    }
    test::write_file(temp.path() / "target", target);
    test::write_file(temp.path() / "basis", basis);
    build_index(temp.path() / "target", temp.path() / "target.txi", block);

    MemorySource source(target);
    toxsync::StreamingSyncOptions options;
    options.io_buffer_bytes = target.size();
    options.max_source_ranges_per_batch = 4U;
    options.fsync_on_commit = false;
    const auto stats = toxsync::sync_file_streaming(
        temp.path() / "target.txi", temp.path() / "basis", source,
        temp.path() / "output", options);
    REQUIRE(stats.source_ranges == 16U);
    REQUIRE(stats.source_batch_calls == 4U);
    REQUIRE(source.max_batch == 4U);
    REQUIRE(test::read_file(temp.path() / "output") == target);
}

TOXSYNC_TEST(streaming_sync_resumes_from_last_complete_batch_after_transport_failure) {
    test::TempDir temp;
    constexpr std::size_t block = 4096U;
    const auto target = test::pattern(block * 12U, 0x7777U);
    test::write_file(temp.path() / "target", target);
    test::write_file(temp.path() / "basis", {});
    build_index(temp.path() / "target", temp.path() / "target.txi", block);

    toxsync::StreamingSyncOptions options;
    options.io_buffer_bytes = block * 4U;
    options.fsync_on_commit = false;
    InterruptingSource interrupted(target, 1U);
    REQUIRE_THROWS(toxsync::sync_file_streaming(
        temp.path() / "target.txi", temp.path() / "basis", interrupted,
        temp.path() / "output", options));
    REQUIRE(std::filesystem::file_size(temp.path() / "output.toxsync.part") == block * 4U);

    MemorySource source(target);
    const auto stats = toxsync::sync_file_streaming(
        temp.path() / "target.txi", temp.path() / "basis", source,
        temp.path() / "output", options);
    REQUIRE(stats.resumed_bytes == block * 4U);
    REQUIRE(test::read_file(temp.path() / "output") == target);
}

TOXSYNC_TEST(streaming_sync_discards_corrupt_resume_prefix) {
    test::TempDir temp;
    constexpr std::size_t block = 4096U;
    const auto target = test::pattern(block * 5U, 0x123456U);
    auto corrupt = std::vector<std::byte>(target.begin(), target.begin() +
        static_cast<std::ptrdiff_t>(block * 2U));
    corrupt[10] ^= std::byte{1};
    test::write_file(temp.path() / "target", target);
    test::write_file(temp.path() / "basis", {});
    test::write_file(temp.path() / "output.toxsync.part", corrupt);
    build_index(temp.path() / "target", temp.path() / "target.txi", block);

    MemorySource source(target);
    toxsync::StreamingSyncOptions options;
    options.io_buffer_bytes = block * 2U;
    options.fsync_on_commit = false;
    const auto stats = toxsync::sync_file_streaming(
        temp.path() / "target.txi", temp.path() / "basis", source,
        temp.path() / "output", options);
    REQUIRE(stats.resumed_bytes == 0U);
    REQUIRE(stats.discarded_resume_bytes == block * 2U);
    REQUIRE(test::read_file(temp.path() / "output") == target);
}

TOXSYNC_TEST(streaming_sync_rejects_corrupt_source_block) {
    test::TempDir temp;
    constexpr std::size_t block = 4096U;
    const auto target = test::pattern(block * 3U, 0x7007U);
    auto corrupt = target;
    corrupt[block + 9U] ^= std::byte{0xff};
    test::write_file(temp.path() / "target", target);
    test::write_file(temp.path() / "basis", {});
    build_index(temp.path() / "target", temp.path() / "target.txi", block);

    MemorySource source(corrupt);
    toxsync::StreamingSyncOptions options;
    options.io_buffer_bytes = block * 3U;
    options.fsync_on_commit = false;
    REQUIRE_THROWS(toxsync::sync_file_streaming(
        temp.path() / "target.txi", temp.path() / "basis", source,
        temp.path() / "output", options));
    REQUIRE(!std::filesystem::exists(temp.path() / "output"));
    REQUIRE(std::filesystem::file_size(temp.path() / "output.toxsync.part") == 0U);
}

TOXSYNC_TEST(streaming_sync_accepts_missing_basis_as_empty) {
    test::TempDir temp;
    const auto target = test::pattern(98765U, 0xabcdU);
    test::write_file(temp.path() / "target", target);
    build_index(temp.path() / "target", temp.path() / "target.txi");
    MemorySource source(target);
    toxsync::StreamingSyncOptions options;
    options.fsync_on_commit = false;
    const auto stats = toxsync::sync_file_streaming(
        temp.path() / "target.txi", temp.path() / "does-not-exist", source,
        temp.path() / "output", options);
    REQUIRE(stats.reused_bytes == 0U);
    REQUIRE(stats.fetched_bytes == target.size());
    REQUIRE(test::read_file(temp.path() / "output") == target);
}

TOXSYNC_TEST(reusable_streaming_workspace_stops_growing_after_warmup) {
    test::TempDir temp;
    constexpr std::size_t block = 4096U;
    const auto first = test::pattern(block * 257U + 31U, 0x7011U);
    const auto second = test::pattern(first.size(), 0x7012U);
    test::write_file(temp.path() / "first", first);
    test::write_file(temp.path() / "second", second);
    test::write_file(temp.path() / "basis", {});
    build_index(temp.path() / "first", temp.path() / "first.txi", block);
    build_index(temp.path() / "second", temp.path() / "second.txi", block);

    toxsync::StreamingSyncOptions options;
    options.io_buffer_bytes = block * 32U;
    options.max_source_ranges_per_batch = 8U;
    options.fsync_on_commit = false;
    toxsync::StreamingWorkspace workspace;

    MemorySource first_source(first);
    const auto cold = toxsync::sync_file_streaming(
        temp.path() / "first.txi", temp.path() / "basis", first_source,
        temp.path() / "first.out", workspace, options);
    const auto retained = workspace.resident_bytes();

    MemorySource second_source(second);
    const auto warm = toxsync::sync_file_streaming(
        temp.path() / "second.txi", temp.path() / "basis", second_source,
        temp.path() / "second.out", workspace, options);

    REQUIRE(cold.workspace_growth_events == 4U);
    REQUIRE(cold.workspace_reserved_bytes == retained);
    REQUIRE(warm.workspace_growth_events == 0U);
    REQUIRE(warm.workspace_reserved_bytes == retained);
    REQUIRE(test::read_file(temp.path() / "first.out") == first);
    REQUIRE(test::read_file(temp.path() / "second.out") == second);

    workspace.release();
    REQUIRE(workspace.resident_bytes() == 0U);
}
