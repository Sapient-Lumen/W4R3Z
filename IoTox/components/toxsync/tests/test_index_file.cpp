#include "test_harness.hpp"
#include "test_support.hpp"

#include "toxsync/index.hpp"
#include "toxsync/index_file.hpp"

#include <cstddef>
#include <cstdint>
#include <filesystem>

TOXSYNC_TEST(auto_block_size_keeps_sixteen_tib_index_below_sixty_four_mib) {
    constexpr std::uint64_t target = 16ULL * 1024ULL * 1024ULL * 1024ULL * 1024ULL;
    const auto block = toxsync::choose_block_size(target);
    REQUIRE(block == 8U * 1024U * 1024U);
    REQUIRE(toxsync::index_metadata_bytes(target, block) <= 64ULL * 1024ULL * 1024ULL);
}

TOXSYNC_TEST(auto_block_size_chooses_small_blocks_when_budget_allows) {
    toxsync::AutoBlockSizeOptions options;
    options.metadata_budget_bytes = 64U * 1024U * 1024U;
    const auto block = toxsync::choose_block_size(256U * 1024U * 1024U, options);
    REQUIRE(block == 4096U);
}

TOXSYNC_TEST(streamed_index_is_byte_compatible_with_legacy_v1_encoder) {
    test::TempDir temp;
    const auto target = test::pattern(1024U * 1024U + 333U, 0x6006U);
    test::write_file(temp.path() / "target", target);

    const auto legacy = toxsync::Index::build_file(temp.path() / "target", 4096U);
    legacy.write_file(temp.path() / "legacy.txi");

    toxsync::IndexFileBuildOptions options;
    options.block_size = 4096U;
    options.io_buffer_bytes = 64U * 1024U;
    options.record_buffer_bytes = 1024U;
    options.fsync_on_commit = false;
    const auto stats = toxsync::build_index_file(
        temp.path() / "target", temp.path() / "streamed.txi", options);

    REQUIRE(test::read_file(temp.path() / "legacy.txi") ==
            test::read_file(temp.path() / "streamed.txi"));
    REQUIRE(stats.metadata.block_count == legacy.blocks.size());
    REQUIRE(stats.peak_working_bytes() == stats.data_buffer_bytes + stats.record_buffer_bytes);
}

TOXSYNC_TEST(inspect_reads_metadata_without_decoding_block_vector) {
    test::TempDir temp;
    const auto target = test::pattern(2U * 1024U * 1024U + 17U, 0x1234U);
    test::write_file(temp.path() / "target", target);
    toxsync::IndexFileBuildOptions options;
    options.block_size = 4096U;
    options.fsync_on_commit = false;
    const auto built = toxsync::build_index_file(
        temp.path() / "target", temp.path() / "target.txi", options);
    const auto metadata = toxsync::inspect_index_file(temp.path() / "target.txi");
    REQUIRE(metadata.block_size == built.metadata.block_size);
    REQUIRE(metadata.block_count == built.metadata.block_count);
    REQUIRE(metadata.target_size == target.size());
    REQUIRE(metadata.target_digest == built.metadata.target_digest);
    REQUIRE(metadata.encoded_size() == std::filesystem::file_size(temp.path() / "target.txi"));
}

TOXSYNC_TEST(streamed_index_handles_empty_target) {
    test::TempDir temp;
    test::write_file(temp.path() / "empty", {});
    toxsync::IndexFileBuildOptions options;
    options.fsync_on_commit = false;
    const auto built = toxsync::build_index_file(
        temp.path() / "empty", temp.path() / "empty.txi", options);
    REQUIRE(built.metadata.target_size == 0U);
    REQUIRE(built.metadata.block_count == 0U);
    REQUIRE(built.metadata.encoded_size() == toxsync::Index::kHeaderBytes);
    REQUIRE(toxsync::verify_indexed_file(temp.path() / "empty.txi", temp.path() / "empty"));
}

TOXSYNC_TEST(inspect_rejects_truncated_index) {
    test::TempDir temp;
    const auto bytes = test::pattern(31U, 7U);
    test::write_file(temp.path() / "bad.txi", bytes);
    REQUIRE_THROWS(toxsync::inspect_index_file(temp.path() / "bad.txi"));
}

TOXSYNC_TEST(reusable_index_workspace_stops_growing_after_warmup) {
    test::TempDir temp;
    const auto first = test::pattern(3U * 1024U * 1024U + 17U, 0x7001U);
    const auto second = test::pattern(first.size(), 0x7002U);
    test::write_file(temp.path() / "first", first);
    test::write_file(temp.path() / "second", second);

    toxsync::IndexFileBuildOptions options;
    options.block_size = 4096U;
    options.io_buffer_bytes = 256U * 1024U;
    options.record_buffer_bytes = 16U * 1024U;
    options.fsync_on_commit = false;
    toxsync::IndexBuildWorkspace workspace;

    const auto cold = toxsync::build_index_file(
        temp.path() / "first", temp.path() / "first.txi", workspace, options);
    const auto retained = workspace.resident_bytes();
    const auto warm = toxsync::build_index_file(
        temp.path() / "second", temp.path() / "second.txi", workspace, options);

    REQUIRE(cold.workspace_growth_events == 2U);
    REQUIRE(cold.workspace_reserved_bytes == retained);
    REQUIRE(warm.workspace_growth_events == 0U);
    REQUIRE(warm.workspace_reserved_bytes == retained);
    REQUIRE(toxsync::verify_indexed_file(temp.path() / "first.txi", temp.path() / "first"));
    REQUIRE(toxsync::verify_indexed_file(temp.path() / "second.txi", temp.path() / "second"));

    workspace.release();
    REQUIRE(workspace.resident_bytes() == 0U);
}
