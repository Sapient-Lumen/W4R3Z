#include "bzip4/resource_plan.hpp"

#include "bzip4/libbz3.h"

#include <algorithm>
#include <limits>
#include <stdexcept>

namespace bzip4 {
namespace {

[[nodiscard]] std::size_t checked_mul(std::size_t left, std::size_t right) {
    if (left != 0 && right > std::numeric_limits<std::size_t>::max() / left) {
        throw CodecError(BZ3_ERR_DATA_TOO_BIG, "resource-plan workspace arithmetic overflow");
    }
    return left * right;
}

void validate_requested_lanes(std::size_t requested_lanes) {
    if (requested_lanes == 0) {
        throw std::invalid_argument("requested lane count must be at least one");
    }
    if (requested_lanes > maximum_parallel_lanes) {
        throw std::invalid_argument("requested lane count exceeds the hard safety limit");
    }
}

} // namespace

ParallelResourcePlan plan_parallel_resources(
    std::size_t block_count,
    std::size_t logical_bytes,
    std::uint32_t workspace_block_size,
    std::size_t requested_lanes,
    std::size_t max_workspace_bytes) {
    validate_requested_lanes(requested_lanes);

    ParallelResourcePlan plan;
    plan.workspace_block_size = workspace_block_size;
    plan.block_count = block_count;
    plan.logical_bytes = logical_bytes;
    plan.requested_lanes = requested_lanes;
    plan.max_workspace_bytes = max_workspace_bytes;

    if (block_count == 0) {
        // Empty BZ3v1 frames require no block codec state. Keep the caller's
        // requested cap visible while reporting literal zero allocation.
        plan.limited_by_work = true;
        plan.fits = true;
        return plan;
    }

    plan.per_lane_workspace_bytes = workspace_memory_bound(workspace_block_size);
    plan.work_limited_lanes = std::min(requested_lanes, block_count);
    plan.strict_workspace_bytes = checked_mul(
        plan.work_limited_lanes, plan.per_lane_workspace_bytes);
    plan.workspace_lane_capacity = max_workspace_bytes / plan.per_lane_workspace_bytes;
    plan.selected_lanes = std::min(
        plan.work_limited_lanes, plan.workspace_lane_capacity);
    plan.selected_workspace_bytes = checked_mul(
        plan.selected_lanes, plan.per_lane_workspace_bytes);
    plan.limited_by_work = plan.work_limited_lanes < requested_lanes;
    plan.limited_by_workspace = plan.selected_lanes < plan.work_limited_lanes;
    plan.fits = plan.selected_lanes != 0;
    return plan;
}

CompressionResourcePlan plan_parallel_compression(
    std::size_t input_size,
    std::uint32_t requested_block_size,
    std::size_t requested_lanes,
    std::size_t max_workspace_bytes) {
    CompressionResourcePlan plan;
    plan.input_bytes = input_size;
    plan.requested_block_size = requested_block_size;
    plan.effective_block_size = select_frame_block_size(
        requested_block_size, input_size);

    // This also checks frame-count representability and all bound arithmetic.
    (void)frame_bound(input_size, plan.effective_block_size);
    const std::size_t block_count = input_size == 0
        ? 0 : 1 + (input_size - 1) / plan.effective_block_size;
    plan.parallel = plan_parallel_resources(
        block_count,
        input_size,
        plan.effective_block_size,
        requested_lanes,
        max_workspace_bytes);
    return plan;
}

ParallelResourcePlan plan_parallel_decompression(
    const FrameInfo& info,
    std::size_t requested_lanes,
    std::size_t max_workspace_bytes) {
    if (info.block_count == 0) {
        return plan_parallel_resources(
            0, info.original_size, info.decoder_block_size,
            requested_lanes, max_workspace_bytes);
    }
    if (info.decoder_block_size < min_block_size ||
        info.decoder_block_size > info.block_size) {
        throw std::invalid_argument(
            "frame info has an invalid contracted decoder block size");
    }
    const std::size_t expected = workspace_memory_bound(info.decoder_block_size);
    if (info.decoder_workspace_bytes != 0 &&
        info.decoder_workspace_bytes != expected) {
        throw std::invalid_argument(
            "frame info decoder workspace accounting is inconsistent");
    }
    return plan_parallel_resources(
        info.block_count,
        info.original_size,
        info.decoder_block_size,
        requested_lanes,
        max_workspace_bytes);
}

} // namespace bzip4
