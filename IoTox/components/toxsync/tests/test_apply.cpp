#include "test_harness.hpp"
#include "test_support.hpp"
#include "toxsync/apply.hpp"
#include "toxsync/index.hpp"
#include "toxsync/planner.hpp"
#include "toxsync/range_source.hpp"

#include <algorithm>
#include <stdexcept>

namespace {
class InterruptingSource final : public toxsync::RangeSource {
public:
    InterruptingSource(const std::filesystem::path& path, std::uint64_t allowance)
        : delegate_(path), allowance_(allowance) {}

    std::size_t read_at(std::uint64_t offset, std::span<std::byte> output) override {
        if (served_ >= allowance_) throw std::runtime_error("simulated transport interruption");
        const auto permitted = static_cast<std::size_t>(std::min<std::uint64_t>(output.size(), allowance_ - served_));
        const auto count = delegate_.read_at(offset, output.first(permitted));
        served_ += count;
        return count;
    }
private:
    toxsync::FileRangeSource delegate_;
    std::uint64_t allowance_{};
    std::uint64_t served_{};
};
}

TOXSYNC_TEST(apply_reconstructs_target_with_basis_and_ranges) {
    test::TempDir temp;
    constexpr std::size_t block = 512U;
    auto target = test::pattern(block * 8U, 81U);
    auto basis = target;
    std::fill(basis.begin() + static_cast<std::ptrdiff_t>(block * 3U),
              basis.begin() + static_cast<std::ptrdiff_t>(block * 5U), std::byte{0x42});
    test::write_file(temp.path() / "target", target);
    test::write_file(temp.path() / "basis", basis);
    const auto index = toxsync::Index::build_file(temp.path() / "target", block);
    const auto plan = toxsync::plan_file(index, temp.path() / "basis");
    toxsync::FileRangeSource source(temp.path() / "target");
    toxsync::ApplyOptions options;
    options.fsync_on_commit = false;
    const auto stats = toxsync::apply_file(index, plan, temp.path() / "basis", source,
                                           temp.path() / "output", options);
    REQUIRE(test::read_file(temp.path() / "output") == target);
    REQUIRE(stats.fetched_bytes == block * 2U);
    REQUIRE(stats.reused_bytes == block * 6U);
    REQUIRE(stats.output_digest == index.target_digest);
}

TOXSYNC_TEST(apply_resumes_from_completed_block_boundary) {
    test::TempDir temp;
    constexpr std::size_t block = 1024U;
    const auto target = test::pattern(block * 9U, 0xabcU);
    const std::vector<std::byte> empty;
    test::write_file(temp.path() / "target", target);
    test::write_file(temp.path() / "basis", empty);
    const auto index = toxsync::Index::build_file(temp.path() / "target", block);
    const auto plan = toxsync::plan_file(index, temp.path() / "basis");
    toxsync::ApplyOptions options;
    options.io_buffer_bytes = 333U;
    options.fsync_on_commit = false;

    InterruptingSource interrupted(temp.path() / "target", block * 3U + 177U);
    REQUIRE_THROWS(toxsync::apply_file(index, plan, temp.path() / "basis", interrupted,
                                       temp.path() / "output", options));
    const auto part = temp.path() / "output.toxsync.part";
    REQUIRE(std::filesystem::exists(part));
    REQUIRE(std::filesystem::file_size(part) >= block * 3U);

    toxsync::FileRangeSource healthy(temp.path() / "target");
    const auto stats = toxsync::apply_file(index, plan, temp.path() / "basis", healthy,
                                           temp.path() / "output", options);
    REQUIRE(stats.resumed_bytes == block * 3U);
    REQUIRE(stats.fetched_bytes == target.size() - block * 3U);
    REQUIRE(test::read_file(temp.path() / "output") == target);
    REQUIRE(!std::filesystem::exists(part));
}

TOXSYNC_TEST(apply_rejects_corrupt_source_and_removes_partial) {
    test::TempDir temp;
    constexpr std::size_t block = 512U;
    const auto target = test::pattern(block * 3U, 88U);
    auto corrupt = target;
    corrupt[700] ^= std::byte{0xff};
    const std::vector<std::byte> empty;
    test::write_file(temp.path() / "target", target);
    test::write_file(temp.path() / "corrupt", corrupt);
    test::write_file(temp.path() / "basis", empty);
    const auto index = toxsync::Index::build_file(temp.path() / "target", block);
    const auto plan = toxsync::plan_file(index, temp.path() / "basis");
    toxsync::FileRangeSource source(temp.path() / "corrupt");
    toxsync::ApplyOptions options;
    options.fsync_on_commit = false;
    REQUIRE_THROWS(toxsync::apply_file(index, plan, temp.path() / "basis", source,
                                       temp.path() / "output", options));
    REQUIRE(!std::filesystem::exists(temp.path() / "output"));
    REQUIRE(!std::filesystem::exists(temp.path() / "output.toxsync.part"));
}

TOXSYNC_TEST(verify_checks_size_and_sha256) {
    test::TempDir temp;
    const auto target = test::pattern(3333U, 1U);
    test::write_file(temp.path() / "target", target);
    const auto index = toxsync::Index::build_file(temp.path() / "target", 512U);
    REQUIRE(toxsync::verify_file(index, temp.path() / "target"));
    auto changed = target;
    changed.back() ^= std::byte{1};
    test::write_file(temp.path() / "changed", changed);
    REQUIRE(!toxsync::verify_file(index, temp.path() / "changed"));
}

TOXSYNC_TEST(verified_receiver_can_seed_the_same_immutable_target) {
    test::TempDir temp;
    constexpr std::size_t block = 1024U;
    const auto target = test::pattern(block * 12U + 317U, 0x515151U);
    auto basis_b = target;
    auto basis_c = target;
    std::fill(basis_b.begin() + static_cast<std::ptrdiff_t>(block * 2U),
              basis_b.begin() + static_cast<std::ptrdiff_t>(block * 5U), std::byte{0x22});
    std::fill(basis_c.begin() + static_cast<std::ptrdiff_t>(block * 7U),
              basis_c.begin() + static_cast<std::ptrdiff_t>(block * 11U), std::byte{0x77});

    test::write_file(temp.path() / "publisher", target);
    test::write_file(temp.path() / "basis-b", basis_b);
    test::write_file(temp.path() / "basis-c", basis_c);
    const auto index = toxsync::Index::build_file(temp.path() / "publisher", block);

    toxsync::ApplyOptions options;
    options.fsync_on_commit = false;

    const auto plan_b = toxsync::plan_file(index, temp.path() / "basis-b");
    toxsync::FileRangeSource publisher(temp.path() / "publisher");
    const auto result_b = toxsync::apply_file(index, plan_b, temp.path() / "basis-b", publisher,
                                              temp.path() / "peer-b", options);
    REQUIRE(result_b.output_digest == index.target_digest);
    REQUIRE(toxsync::verify_file(index, temp.path() / "peer-b"));

    const auto plan_c = toxsync::plan_file(index, temp.path() / "basis-c");
    toxsync::FileRangeSource peer_b(temp.path() / "peer-b");
    const auto result_c = toxsync::apply_file(index, plan_c, temp.path() / "basis-c", peer_b,
                                              temp.path() / "peer-c", options);
    REQUIRE(result_c.output_digest == index.target_digest);
    REQUIRE(test::read_file(temp.path() / "peer-c") == target);
}

TOXSYNC_TEST(apply_batches_output_and_source_reads_to_configured_buffer) {
    test::TempDir temp;
    constexpr std::size_t block = 1024U;
    const auto target = test::pattern(block * 17U, 0xabc123U);
    test::write_file(temp.path() / "target", target);
    test::write_file(temp.path() / "basis", {});
    const auto index = toxsync::Index::build_file(temp.path() / "target", block);
    toxsync::PlannerOptions planner_options;
    planner_options.search_mode = toxsync::PlannerSearchMode::aligned_only;
    const auto plan = toxsync::plan_file(index, temp.path() / "basis", planner_options);
    toxsync::FileRangeSource source(temp.path() / "target");
    toxsync::ApplyOptions options;
    options.io_buffer_bytes = block * 4U;
    options.fsync_on_commit = false;
    const auto stats = toxsync::apply_file(index, plan, temp.path() / "basis", source,
                                           temp.path() / "output", options);
    REQUIRE(stats.output_write_calls == 5U);
    REQUIRE(stats.source_read_calls == 5U);
    REQUIRE(stats.source_runs == 5U);
    REQUIRE(stats.buffer_bytes == block * 4U);
    REQUIRE(test::read_file(temp.path() / "output") == target);
}

TOXSYNC_TEST(apply_batches_reads_and_writes_with_fixed_memory) {
    test::TempDir temp;
    constexpr std::size_t block = 1024U;
    const auto target = test::pattern(block * 16U, 0x4444U);
    test::write_file(temp.path() / "target", target);
    test::write_file(temp.path() / "basis", {});
    const auto index = toxsync::Index::build_file(temp.path() / "target", block);
    const auto plan = toxsync::plan_file(index, temp.path() / "basis");
    toxsync::FileRangeSource source(temp.path() / "target");
    toxsync::ApplyOptions options;
    options.io_buffer_bytes = block * 4U;
    options.fsync_on_commit = false;
    const auto stats = toxsync::apply_file(index, plan, temp.path() / "basis", source,
                                           temp.path() / "output", options);
    REQUIRE(stats.buffer_bytes == block * 4U);
    REQUIRE(stats.source_runs == 4U);
    REQUIRE(stats.source_read_calls == 4U);
    REQUIRE(stats.output_write_calls == 4U);
    REQUIRE(stats.fetched_bytes == target.size());
    REQUIRE(test::read_file(temp.path() / "output") == target);
}

TOXSYNC_TEST(apply_rounds_tiny_buffer_up_to_one_block) {
    test::TempDir temp;
    constexpr std::size_t block = 2048U;
    const auto target = test::pattern(block * 3U + 91U, 0x8888U);
    test::write_file(temp.path() / "target", target);
    test::write_file(temp.path() / "basis", {});
    const auto index = toxsync::Index::build_file(temp.path() / "target", block);
    const auto plan = toxsync::plan_file(index, temp.path() / "basis");
    toxsync::FileRangeSource source(temp.path() / "target");
    toxsync::ApplyOptions options;
    options.io_buffer_bytes = 17U;
    options.fsync_on_commit = false;
    const auto stats = toxsync::apply_file(index, plan, temp.path() / "basis", source,
                                           temp.path() / "output", options);
    REQUIRE(stats.buffer_bytes == block);
    REQUIRE(stats.output_write_calls == 4U);
    REQUIRE(test::read_file(temp.path() / "output") == target);
}
