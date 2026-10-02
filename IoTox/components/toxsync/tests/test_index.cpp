#include "test_harness.hpp"
#include "test_support.hpp"
#include "toxsync/index.hpp"

TOXSYNC_TEST(index_build_encode_decode_round_trip) {
    test::TempDir temp;
    const auto bytes = test::pattern(4096U * 3U + 37U, 101U);
    const auto target = temp.path() / "target.bin";
    test::write_file(target, bytes);
    const auto index = toxsync::Index::build_file(target, 4096U);
    REQUIRE(index.target_size == bytes.size());
    REQUIRE(index.blocks.size() == 4U);
    REQUIRE(index.blocks.back().length == 37U);
    REQUIRE(index.target_digest == toxsync::sha256(bytes));
    const auto decoded = toxsync::Index::decode(index.encode());
    REQUIRE(decoded.block_size == index.block_size);
    REQUIRE(decoded.target_size == index.target_size);
    REQUIRE(decoded.target_digest == index.target_digest);
    REQUIRE(decoded.blocks == index.blocks);
}

TOXSYNC_TEST(index_file_round_trip) {
    test::TempDir temp;
    const auto target = temp.path() / "target.bin";
    const auto index_path = temp.path() / "target.txi";
    test::write_file(target, test::pattern(25000U, 9U));
    const auto original = toxsync::Index::build_file(target, 1024U);
    original.write_file(index_path);
    const auto loaded = toxsync::Index::read_file(index_path);
    REQUIRE(loaded.encode() == original.encode());
}

TOXSYNC_TEST(index_rejects_corruption_and_limits) {
    test::TempDir temp;
    const auto target = temp.path() / "target.bin";
    test::write_file(target, test::pattern(4096U, 5U));
    auto bytes = toxsync::Index::build_file(target, 512U).encode();
    bytes[0] ^= std::byte{1};
    REQUIRE_THROWS(toxsync::Index::decode(bytes));

    const auto valid = toxsync::Index::build_file(target, 512U).encode();
    toxsync::IndexLimits limits;
    limits.max_blocks = 1U;
    REQUIRE_THROWS(toxsync::Index::decode(valid, limits));
}

TOXSYNC_TEST(empty_target_has_valid_empty_index) {
    test::TempDir temp;
    const auto target = temp.path() / "empty";
    test::write_file(target, {});
    const auto index = toxsync::Index::build_file(target, 4096U);
    REQUIRE(index.blocks.empty());
    REQUIRE(index.target_size == 0U);
    REQUIRE(toxsync::Index::decode(index.encode()).blocks.empty());
}

TOXSYNC_TEST(index_bulk_and_minimum_buffer_builds_are_identical) {
    test::TempDir temp;
    const auto target = temp.path() / "target.bin";
    test::write_file(target, test::pattern(1024U * 1024U + 73U, 0x9911U));
    toxsync::IndexBuildOptions small;
    small.block_size = 4096U;
    small.io_buffer_bytes = 1U;
    toxsync::IndexBuildOptions bulk;
    bulk.block_size = 4096U;
    bulk.io_buffer_bytes = 1024U * 1024U;
    REQUIRE(toxsync::Index::build_file(target, small).encode() ==
            toxsync::Index::build_file(target, bulk).encode());
}

TOXSYNC_TEST(index_rejects_zero_io_buffer) {
    test::TempDir temp;
    const auto target = temp.path() / "target.bin";
    test::write_file(target, test::pattern(1024U, 5U));
    toxsync::IndexBuildOptions options;
    options.io_buffer_bytes = 0U;
    REQUIRE_THROWS(toxsync::Index::build_file(target, options));
}

TOXSYNC_TEST(index_build_enforces_limits_before_large_allocation) {
    test::TempDir temp;
    const auto target = temp.path() / "target.bin";
    test::write_file(target, test::pattern(4096U, 0x1188U));

    toxsync::IndexBuildOptions options;
    options.block_size = options.limits.max_block_size + 1U;
    REQUIRE_THROWS(toxsync::Index::build_file(target, options));

    options.block_size = 512U;
    options.io_buffer_bytes = 0U;
    REQUIRE_THROWS(toxsync::Index::build_file(target, options));

    options.io_buffer_bytes = 4096U;
    options.limits.max_blocks = 1U;
    REQUIRE_THROWS(toxsync::Index::build_file(target, options));
}

TOXSYNC_TEST(index_small_io_buffer_preserves_format) {
    test::TempDir temp;
    const auto target = temp.path() / "target.bin";
    test::write_file(target, test::pattern(8192U + 37U, 0x8899U));
    toxsync::IndexBuildOptions lean;
    lean.block_size = 512U;
    lean.io_buffer_bytes = 513U;
    const auto small = toxsync::Index::build_file(target, lean);
    const auto regular = toxsync::Index::build_file(target, 512U);
    REQUIRE(small.encode() == regular.encode());
}
