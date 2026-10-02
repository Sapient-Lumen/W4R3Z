#include "test_harness.hpp"
#include "test_support.hpp"
#include "toxsync/index.hpp"
#include "toxsync/planner.hpp"

#include <algorithm>

TOXSYNC_TEST(planner_finds_shifted_blocks_and_only_requests_new_block) {
    test::TempDir temp;
    constexpr std::size_t block = 512U;
    const auto a = test::pattern(block, 1U);
    const auto b = test::pattern(block, 2U);
    const auto c = test::pattern(block, 3U);
    const auto d = test::pattern(block, 4U);
    const auto fresh = test::pattern(block, 99U);

    std::vector<std::byte> target;
    for (const auto* part : {&a, &b, &fresh, &c, &d}) target.insert(target.end(), part->begin(), part->end());
    std::vector<std::byte> basis(37U, std::byte{0x55});
    for (const auto* part : {&a, &b, &c, &d}) basis.insert(basis.end(), part->begin(), part->end());

    const auto target_path = temp.path() / "target";
    const auto basis_path = temp.path() / "basis";
    test::write_file(target_path, target);
    test::write_file(basis_path, basis);
    const auto index = toxsync::Index::build_file(target_path, block);
    const auto plan = toxsync::plan_file(index, basis_path);
    REQUIRE(plan.stats.matched_blocks == 4U);
    REQUIRE(plan.stats.reused_bytes == block * 4U);
    REQUIRE(plan.stats.missing_bytes == block);
    REQUIRE(plan.missing_ranges.size() == 1U);
    REQUIRE((plan.missing_ranges[0] == toxsync::MissingRange{block * 2U, block}));
    REQUIRE(plan.basis_offsets[0] == 37U);
    REQUIRE(plan.basis_offsets[1] == 37U + block);
    REQUIRE(plan.basis_offsets[3] == 37U + block * 2U);
    REQUIRE(plan.basis_offsets[4] == 37U + block * 3U);
}

TOXSYNC_TEST(planner_reuses_duplicate_target_blocks_from_one_basis_copy) {
    test::TempDir temp;
    constexpr std::size_t block = 256U;
    const auto repeated = test::pattern(block, 333U);
    std::vector<std::byte> target;
    target.insert(target.end(), repeated.begin(), repeated.end());
    target.insert(target.end(), repeated.begin(), repeated.end());
    target.insert(target.end(), repeated.begin(), repeated.end());
    test::write_file(temp.path() / "target", target);
    test::write_file(temp.path() / "basis", repeated);
    const auto plan = toxsync::plan_file(toxsync::Index::build_file(temp.path() / "target", block),
                                         temp.path() / "basis");
    REQUIRE(plan.stats.matched_blocks == 3U);
    REQUIRE(plan.stats.missing_bytes == 0U);
    REQUIRE(std::all_of(plan.basis_offsets.begin(), plan.basis_offsets.end(), [](auto offset) { return offset == 0U; }));
}

TOXSYNC_TEST(planner_handles_partial_tail_block) {
    test::TempDir temp;
    constexpr std::size_t block = 512U;
    const auto target = test::pattern(block * 2U + 71U, 123U);
    std::vector<std::byte> basis(19U, std::byte{0x77});
    basis.insert(basis.end(), target.begin(), target.end());
    test::write_file(temp.path() / "target", target);
    test::write_file(temp.path() / "basis", basis);
    const auto plan = toxsync::plan_file(toxsync::Index::build_file(temp.path() / "target", block),
                                         temp.path() / "basis");
    REQUIRE(plan.stats.missing_bytes == 0U);
    REQUIRE(plan.stats.matched_blocks == 3U);
}

TOXSYNC_TEST(planner_coalesces_adjacent_missing_blocks) {
    test::TempDir temp;
    constexpr std::size_t block = 256U;
    const auto target = test::pattern(block * 5U, 11U);
    const std::vector<std::byte> empty;
    test::write_file(temp.path() / "target", target);
    test::write_file(temp.path() / "basis", empty);
    const auto plan = toxsync::plan_file(toxsync::Index::build_file(temp.path() / "target", block),
                                         temp.path() / "basis");
    REQUIRE(plan.missing_ranges.size() == 1U);
    REQUIRE(plan.missing_ranges[0].offset == 0U);
    REQUIRE(plan.missing_ranges[0].length == target.size());
}

TOXSYNC_TEST(planner_adaptive_fast_path_avoids_rolling_for_small_in_place_change) {
    test::TempDir temp;
    constexpr std::size_t block = 512U;
    auto target = test::pattern(block * 20U, 0x1234U);
    auto basis = target;
    std::fill(basis.begin() + static_cast<std::ptrdiff_t>(block * 7U),
              basis.begin() + static_cast<std::ptrdiff_t>(block * 8U), std::byte{0x91});
    test::write_file(temp.path() / "target", target);
    test::write_file(temp.path() / "basis", basis);
    const auto index = toxsync::Index::build_file(temp.path() / "target", block);
    const auto plan = toxsync::plan_file(index, temp.path() / "basis");
    REQUIRE(plan.stats.aligned_blocks_checked == 20U);
    REQUIRE(plan.stats.aligned_blocks_matched == 19U);
    REQUIRE(plan.stats.rolling_passes == 0U);
    REQUIRE(plan.stats.missing_bytes == block);
}

TOXSYNC_TEST(planner_adaptive_falls_back_to_rolling_for_shifted_basis) {
    test::TempDir temp;
    constexpr std::size_t block = 512U;
    const auto target = test::pattern(block * 8U, 0x7711U);
    std::vector<std::byte> basis(37U, std::byte{0x6a});
    basis.insert(basis.end(), target.begin(), target.end());
    test::write_file(temp.path() / "target", target);
    test::write_file(temp.path() / "basis", basis);
    toxsync::PlannerOptions options;
    options.aligned_buffer_bytes = block * 2U;
    options.rolling_buffer_bytes = 193U;
    const auto plan = toxsync::plan_file(toxsync::Index::build_file(temp.path() / "target", block),
                                         temp.path() / "basis", options);
    REQUIRE(plan.stats.aligned_probe_aborted_early);
    REQUIRE(plan.stats.aligned_blocks_checked < 8U);
    REQUIRE(plan.stats.rolling_passes >= 1U);
    REQUIRE(plan.stats.missing_bytes == 0U);
    REQUIRE(plan.stats.matched_blocks == 8U);
    REQUIRE(plan.basis_offsets.front() == 37U);
}

TOXSYNC_TEST(planner_aligned_only_trades_reuse_for_minimum_cpu) {
    test::TempDir temp;
    constexpr std::size_t block = 256U;
    const auto target = test::pattern(block * 4U, 0x5151U);
    std::vector<std::byte> basis(11U, std::byte{0x44});
    basis.insert(basis.end(), target.begin(), target.end());
    test::write_file(temp.path() / "target", target);
    test::write_file(temp.path() / "basis", basis);
    toxsync::PlannerOptions options;
    options.search_mode = toxsync::PlannerSearchMode::aligned_only;
    const auto plan = toxsync::plan_file(toxsync::Index::build_file(temp.path() / "target", block),
                                         temp.path() / "basis", options);
    REQUIRE(plan.stats.rolling_passes == 0U);
    REQUIRE(plan.stats.missing_bytes == target.size());
}

TOXSYNC_TEST(planner_rejects_invalid_adaptive_threshold) {
    test::TempDir temp;
    test::write_file(temp.path() / "target", test::pattern(1024U, 9U));
    test::write_file(temp.path() / "basis", test::pattern(1024U, 9U));
    toxsync::PlannerOptions options;
    options.adaptive_min_aligned_reuse_percent = 101U;
    REQUIRE_THROWS(toxsync::plan_file(toxsync::Index::build_file(temp.path() / "target", 256U),
                                      temp.path() / "basis", options));
}

TOXSYNC_TEST(planner_exhaustive_mode_uses_bounded_rolling_buffer) {
    test::TempDir temp;
    constexpr std::size_t block = 512U;
    const auto target = test::pattern(block * 7U + 39U, 0x9191U);
    std::vector<std::byte> basis(23U, std::byte{0x61});
    basis.insert(basis.end(), target.begin(), target.end());
    test::write_file(temp.path() / "target", target);
    test::write_file(temp.path() / "basis", basis);

    toxsync::PlannerOptions options;
    options.search_mode = toxsync::PlannerSearchMode::exhaustive_rolling;
    options.aligned_buffer_bytes = 17U;
    options.rolling_buffer_bytes = 67U;
    const auto plan = toxsync::plan_file(toxsync::Index::build_file(temp.path() / "target", block),
                                         temp.path() / "basis", options);
    REQUIRE(plan.stats.aligned_blocks_checked == 0U);
    REQUIRE(plan.stats.rolling_passes >= 1U);
    REQUIRE(plan.stats.missing_bytes == 0U);
    REQUIRE(plan.stats.temporary_bytes_peak < 4096U);
}

TOXSYNC_TEST(planner_rejects_zero_work_buffers) {
    test::TempDir temp;
    test::write_file(temp.path() / "target", test::pattern(2048U, 0x3131U));
    test::write_file(temp.path() / "basis", test::pattern(2048U, 0x3131U));
    const auto index = toxsync::Index::build_file(temp.path() / "target", 256U);

    toxsync::PlannerOptions options;
    options.aligned_buffer_bytes = 0U;
    REQUIRE_THROWS(toxsync::plan_file(index, temp.path() / "basis", options));
    options.aligned_buffer_bytes = 1024U;
    options.rolling_buffer_bytes = 0U;
    REQUIRE_THROWS(toxsync::plan_file(index, temp.path() / "basis", options));
}
