#pragma once

#include "bzip4/codec.hpp"

#include <cstddef>
#include <cstdint>

namespace bzip4 {

/** Caller-participating parallel helpers retain at most 256 background lanes. */
inline constexpr std::size_t maximum_parallel_lanes = 257;

/**
 * Allocation-free resource plan for one caller-participating codec operation.
 *
 * Lane count is scheduling-only for BZ3v1: reducing selected_lanes does not
 * change encoded bytes. The plan therefore distinguishes the caller's cap,
 * the amount of useful block parallelism, and the amount that fits the explicit
 * codec-workspace budget. It does not charge thread stacks, allocator metadata,
 * page cache, input/output staging, or the embedding application's memory.
 */
struct ParallelResourcePlan {
    std::uint32_t workspace_block_size{};
    std::size_t block_count{};
    std::size_t logical_bytes{};
    std::size_t requested_lanes{};
    std::size_t work_limited_lanes{};
    std::size_t workspace_lane_capacity{};
    std::size_t selected_lanes{};
    std::size_t per_lane_workspace_bytes{};
    std::size_t strict_workspace_bytes{};
    std::size_t selected_workspace_bytes{};
    std::size_t max_workspace_bytes{};
    bool limited_by_work{};
    bool limited_by_workspace{};
    bool fits{};
};

/** Plan a known block population without allocating a codec state or thread. */
[[nodiscard]] ParallelResourcePlan plan_parallel_resources(
    std::size_t block_count,
    std::size_t logical_bytes,
    std::uint32_t workspace_block_size,
    std::size_t requested_lanes,
    std::size_t max_workspace_bytes);

struct CompressionResourcePlan {
    std::size_t input_bytes{};
    std::uint32_t requested_block_size{};
    std::uint32_t effective_block_size{};
    ParallelResourcePlan parallel;
};

/** Plan BZ3v1 frame compression, including input-sensitive block-size selection. */
[[nodiscard]] CompressionResourcePlan plan_parallel_compression(
    std::size_t input_size,
    std::uint32_t requested_block_size,
    std::size_t requested_lanes,
    std::size_t max_workspace_bytes);

/** Plan parallel decoding from a completely validated frame envelope. */
[[nodiscard]] ParallelResourcePlan plan_parallel_decompression(
    const FrameInfo& info,
    std::size_t requested_lanes,
    std::size_t max_workspace_bytes);

} // namespace bzip4
