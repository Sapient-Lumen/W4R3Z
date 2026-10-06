#include "bzip4/activation.hpp"

#include <algorithm>
#include <limits>

namespace bzip4 {
namespace {

[[nodiscard]] std::size_t floor_grain_cap(std::size_t work, std::size_t minimum) noexcept {
    if (minimum <= 1) {
        return work;
    }
    // A non-empty job always gets at least one lane; otherwise floor division
    // is the precise maximum number of lanes that can each receive the minimum.
    return std::max<std::size_t>(1, work / minimum);
}

} // namespace

ActivationPlan make_activation_plan(
    std::size_t block_count,
    std::size_t logical_bytes,
    const ActivationPolicy& policy) noexcept {
    ActivationPlan plan;
    plan.blocks = block_count;
    plan.logical_bytes = logical_bytes;
    if (block_count == 0) {
        return plan;
    }

    std::size_t retained_lanes = policy.retained_background_workers;
    if (policy.caller_participates && retained_lanes != std::numeric_limits<std::size_t>::max()) {
        ++retained_lanes;
    }
    if (retained_lanes == 0) {
        // A background-only profile with no retained worker has no executor.
        return plan;
    }
    std::size_t lanes = std::min(block_count, retained_lanes);
    if (policy.max_active_lanes != 0) {
        lanes = std::min(lanes, policy.max_active_lanes);
    }
    lanes = std::min(lanes, floor_grain_cap(block_count, policy.minimum_blocks_per_active_lane));
    lanes = std::min(lanes, floor_grain_cap(logical_bytes, policy.minimum_bytes_per_active_lane));
    lanes = std::max<std::size_t>(1, lanes);

    plan.active_lanes = lanes;
    plan.caller_participates = policy.caller_participates;
    const std::size_t caller_lane = policy.caller_participates ? 1U : 0U;
    plan.active_background_workers = lanes > caller_lane ? lanes - caller_lane : 0;
    plan.active_background_workers = std::min(
        plan.active_background_workers,
        policy.retained_background_workers);
    plan.workers_notified = policy.wake_mode == WakeMode::all_retained
        ? policy.retained_background_workers
        : plan.active_background_workers;
    return plan;
}

} // namespace bzip4
