#pragma once

#include "bzip4/activation.hpp"
#include "bzip4/codec.hpp"

#include <cstddef>
#include <cstdint>
#include <memory>
#include <span>

namespace bzip4 {

inline constexpr std::size_t default_parallel_workspace_budget =
    static_cast<std::size_t>(512U) * 1024U * 1024U;

/**
 * Policy for a retained, ordered frame encoder or decoder.
 *
 * retained_background_workers describes threads kept alive by the codec pool.
 * When caller_participates is true, the calling thread owns one additional
 * workspace and executes lane zero while also publishing completed blocks in
 * frame order. max_workspace_bytes charges every retained background workspace
 * plus the caller workspace before any worker thread is created. Range-backed
 * sources must support concurrent exact reads unless serialize_range_reads is
 * enabled.
 */
struct ParallelFramePolicy {
    ActivationPolicy activation{};
    std::size_t max_workspace_bytes{default_parallel_workspace_budget};
    bool serialize_range_reads{false};
};

/** Per-call evidence from the retained encoder. */
struct ParallelFrameStats {
    ActivationPlan activation{};
    std::size_t generation{};
    std::size_t retained_background_workers{};
    std::size_t retained_lanes{};
    std::size_t per_lane_workspace_bytes{};
    std::size_t retained_workspace_bytes{};
    std::size_t productive_lanes{};
    std::size_t batches{};
    std::size_t peak_blocks_in_flight{};
    std::size_t background_notifications{};
    std::size_t caller_blocks{};
    std::size_t background_blocks{};
    std::size_t inactive_worker_wakeups{};
};

/**
 * Reusable parallel BZ3v1 frame encoder with one fixed-size workspace per lane.
 *
 * Background threads and codec/BWT arenas survive across calls. Calls on one
 * encoder are serialized. For a call activating more than one lane, RangeReader
 * must support concurrent exact reads unless serialize_range_reads is enabled;
 * in either mode it must preserve stable bytes for the duration of the call.
 *
 * Each active lane encodes at most one block per bounded batch. The caller waits
 * for that batch, publishes its workspace-owned results in frame order, and only
 * then reuses the arenas for the next batch. Sink spans are borrowed only for the
 * callback duration. Reader and sink callbacks must not re-enter this encoder.
 * This removes payload copies while bounding in-flight results by active_lanes.
 * A codec, reader, or sink failure drains every notified worker and leaves the
 * encoder reusable for a later call.
 */
class ParallelFrameEncoder final {
public:
    ParallelFrameEncoder(
        std::uint32_t block_size,
        ParallelFramePolicy policy);
    ~ParallelFrameEncoder();

    ParallelFrameEncoder(const ParallelFrameEncoder&) = delete;
    ParallelFrameEncoder& operator=(const ParallelFrameEncoder&) = delete;
    ParallelFrameEncoder(ParallelFrameEncoder&&) = delete;
    ParallelFrameEncoder& operator=(ParallelFrameEncoder&&) = delete;

    [[nodiscard]] std::uint32_t block_size() const noexcept;
    [[nodiscard]] std::size_t retained_background_workers() const noexcept;
    [[nodiscard]] std::size_t retained_workspace_bytes() const noexcept;

    [[nodiscard]] FrameInfo encode_frame_to(
        std::span<const std::byte> input,
        const FrameSink& sink,
        ParallelFrameStats* stats = nullptr);

    [[nodiscard]] FrameInfo encode_frame_from(
        std::size_t input_size,
        const RangeReader& reader,
        const FrameSink& sink,
        ParallelFrameStats* stats = nullptr);

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

/** Per-call evidence from the retained decoder. */
struct ParallelDecodeStats {
    ActivationPlan activation{};
    std::size_t generation{};
    std::size_t retained_background_workers{};
    std::size_t retained_lanes{};
    std::size_t per_lane_workspace_bytes{};
    std::size_t retained_workspace_bytes{};
    std::size_t productive_lanes{};
    std::size_t batches{};
    std::size_t peak_blocks_in_flight{};
    std::size_t background_notifications{};
    std::size_t caller_blocks{};
    std::size_t background_blocks{};
    std::size_t inactive_worker_wakeups{};
    std::size_t descriptor_reads{};
};

/**
 * Reusable parallel BZ3v1 frame decoder for one fixed declared frame block size.
 *
 * The two-argument constructor retains declaration-sized workspaces. The
 * three-argument constructor may retain a smaller legal workspace block size;
 * each frame is still completely scanned and is rejected before output when its
 * validated payload/output/intermediate extent exceeds that retained capacity.
 * One-shot helpers choose the smallest validated workspace automatically.
 *
 * The complete envelope is validated before the first decoded sink callback.
 * Block descriptors are then re-read through a constant-state cursor and only
 * one bounded active-lane batch is retained at a time. Decoded workspace views
 * are published in exact block order before their lanes are reused. Calls on
 * one decoder are serialized, and failures drain every notified worker so the
 * retained pool remains reusable.
 */
class ParallelFrameDecoder final {
public:
    ParallelFrameDecoder(
        std::uint32_t block_size,
        ParallelFramePolicy policy);
    ParallelFrameDecoder(
        std::uint32_t block_size,
        std::uint32_t decoder_block_size,
        ParallelFramePolicy policy);
    ~ParallelFrameDecoder();

    ParallelFrameDecoder(const ParallelFrameDecoder&) = delete;
    ParallelFrameDecoder& operator=(const ParallelFrameDecoder&) = delete;
    ParallelFrameDecoder(ParallelFrameDecoder&&) = delete;
    ParallelFrameDecoder& operator=(ParallelFrameDecoder&&) = delete;

    [[nodiscard]] std::uint32_t block_size() const noexcept;
    [[nodiscard]] std::uint32_t decoder_block_size() const noexcept;
    [[nodiscard]] std::size_t retained_background_workers() const noexcept;
    [[nodiscard]] std::size_t retained_workspace_bytes() const noexcept;

    [[nodiscard]] FrameInfo decode_frame_to(
        std::span<const std::byte> encoded,
        std::size_t max_output_size,
        const FrameSink& sink,
        bool reject_trailing_bytes = true,
        ParallelDecodeStats* stats = nullptr);

    [[nodiscard]] FrameInfo decode_frame_from(
        std::size_t encoded_size,
        const RangeReader& reader,
        std::size_t max_output_size,
        const FrameSink& sink,
        bool reject_trailing_bytes = true,
        ParallelDecodeStats* stats = nullptr);

private:
    class Impl;
    std::unique_ptr<Impl> impl_;

    friend FrameInfo decompress_frame_parallel_from(
        std::size_t encoded_size,
        const RangeReader& reader,
        std::size_t max_output_size,
        const FrameSink& sink,
        ParallelFramePolicy policy,
        bool reject_trailing_bytes,
        ParallelDecodeStats* stats);
};

/** One-shot retained-pool counterpart to decompress_frame_to(). */
[[nodiscard]] FrameInfo decompress_frame_parallel_to(
    std::span<const std::byte> encoded,
    std::size_t max_output_size,
    const FrameSink& sink,
    ParallelFramePolicy policy,
    bool reject_trailing_bytes = true,
    ParallelDecodeStats* stats = nullptr);

/** One-shot range-backed retained-pool counterpart to decompress_frame_from(). */
[[nodiscard]] FrameInfo decompress_frame_parallel_from(
    std::size_t encoded_size,
    const RangeReader& reader,
    std::size_t max_output_size,
    const FrameSink& sink,
    ParallelFramePolicy policy,
    bool reject_trailing_bytes = true,
    ParallelDecodeStats* stats = nullptr);

/** One-shot retained-pool convenience counterpart to compress_frame_to(). */
[[nodiscard]] FrameInfo compress_frame_parallel_to(
    std::span<const std::byte> input,
    std::uint32_t requested_block_size,
    const FrameSink& sink,
    ParallelFramePolicy policy,
    ParallelFrameStats* stats = nullptr);

/** One-shot range-backed retained-pool counterpart to compress_frame_from(). */
[[nodiscard]] FrameInfo compress_frame_parallel_from(
    std::size_t input_size,
    std::uint32_t requested_block_size,
    const RangeReader& reader,
    const FrameSink& sink,
    ParallelFramePolicy policy,
    ParallelFrameStats* stats = nullptr);

} // namespace bzip4
