#include "test_harness.hpp"
#include "toxsync/lane_budget.hpp"

#include <limits>

using namespace toxsync;

TOXSYNC_TEST(lane_budget_uses_runtime_resources_without_magic_ceiling) {
    LaneResourceBudget budget;
    budget.requested_lanes = 4096U;
    budget.peer_advertised_lanes = 8192U;
    budget.transport_slots = 6000U;
    budget.global_inflight_slots = 5000U;
    budget.descriptor_slots = 4500U;
    budget.command_queue_slots = 4300U;
    budget.memory_budget_bytes = 2U * 1024U * 1024U * 1024U;
    budget.reserved_memory_bytes = 64U * 1024U * 1024U;
    budget.bytes_per_lane = 256U * 1024U;
    const auto decision = derive_lane_budget(budget);
    REQUIRE(decision.usable());
    REQUIRE(decision.lanes == 4096U);
    REQUIRE(decision.limiting_reason == LaneLimitReason::requested);
    REQUIRE(decision.memory_lanes > decision.lanes);
}

TOXSYNC_TEST(lane_budget_reports_memory_and_resource_exhaustion) {
    LaneResourceBudget budget;
    budget.requested_lanes = 100U;
    budget.memory_budget_bytes = 9U * 1024U * 1024U;
    budget.reserved_memory_bytes = 1U * 1024U * 1024U;
    budget.bytes_per_lane = 1U * 1024U * 1024U;
    auto decision = derive_lane_budget(budget);
    REQUIRE(decision.lanes == 8U);
    REQUIRE(decision.limiting_reason == LaneLimitReason::memory_budget);

    budget.reserved_memory_bytes = budget.memory_budget_bytes;
    decision = derive_lane_budget(budget);
    REQUIRE(!decision.usable());
    REQUIRE(decision.limiting_reason == LaneLimitReason::resource_unavailable);
}

TOXSYNC_TEST(lane_tuner_scales_past_thirty_two_and_backs_off) {
    LaneTuner tuner(256U);
    REQUIRE(tuner.current_lanes() == 1U);
    std::size_t lanes = 1U;
    std::uint64_t rate = 1'000'000U;
    while (lanes <= 32U) {
        const auto next = tuner.observe({
            .lanes = lanes,
            .useful_bytes = rate,
            .elapsed_microseconds = 1'000'000U,
        });
        REQUIRE(next >= lanes);
        rate = rate + rate / 5U;
        lanes = next;
    }
    REQUIRE(lanes > 32U);
    const auto backed_off = tuner.observe({
        .lanes = lanes,
        .useful_bytes = rate,
        .elapsed_microseconds = 1'000'000U,
        .stalled_microseconds = 300'000U,
        .retries = 1U,
    });
    REQUIRE(backed_off >= 1U);
    REQUIRE(backed_off < lanes);
}

TOXSYNC_TEST(lane_tuner_tracks_a_shrinking_and_growing_runtime_budget) {
    LaneTuner tuner(64U);
    REQUIRE(tuner.observe({1U, 1'000'000U, 1'000'000U, 0U, 0U}) == 2U);
    REQUIRE(tuner.observe({2U, 1'300'000U, 1'000'000U, 0U, 0U}) == 3U);
    tuner.set_budget(1U);
    REQUIRE(tuner.current_lanes() == 1U);
    tuner.set_budget(128U);
    REQUIRE(tuner.current_lanes() == 1U);
    REQUIRE(tuner.snapshot().budget_lanes == 128U);
    tuner.reset();
    REQUIRE(tuner.current_lanes() == 1U);
}

TOXSYNC_TEST(lane_tuner_has_an_allocation_free_explicit_failure_backoff) {
    LaneTuner tuner(64U);
    REQUIRE(tuner.current_lanes() == 1U);
    REQUIRE(tuner.observe(LaneObservation{
        .lanes = 1U,
        .useful_bytes = 1U << 20U,
        .elapsed_microseconds = 100000U,
    }) == 2U);
    REQUIRE(tuner.observe(LaneObservation{
        .lanes = 2U,
        .useful_bytes = 3U << 20U,
        .elapsed_microseconds = 100000U,
    }) == 3U);
    REQUIRE(tuner.backoff() == 1U);
    const auto backed_off = tuner.snapshot();
    REQUIRE(backed_off.active_lanes == 1U);
    REQUIRE(!backed_off.probing_enabled);
    tuner.set_budget(64U);
    REQUIRE(tuner.snapshot().probing_enabled);
}
