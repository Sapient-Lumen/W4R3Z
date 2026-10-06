#pragma once

#include <cstddef>
#include <cstdint>
#include <functional>
#include <memory>
#include <span>
#include <stdexcept>
#include <string>
#include <vector>

namespace bzip4 {

inline constexpr std::uint32_t min_block_size = 65U * 1024U;
inline constexpr std::uint32_t max_block_size = 511U * 1024U * 1024U;
inline constexpr std::size_t default_decoder_workspace_budget =
    static_cast<std::size_t>(512U) * 1024U * 1024U;

class CodecError final : public std::runtime_error {
public:
    CodecError(int code, std::string message);
    [[nodiscard]] int code() const noexcept { return code_; }

private:
    int code_;
};

struct FrameInfo {
    /** Declared BZ3v1 frame block-size upper bound. */
    std::uint32_t block_size{};
    /** Smallest legal bz3_state size satisfying all validated frame extents. */
    std::uint32_t decoder_block_size{};
    std::uint32_t block_count{};
    std::size_t original_size{};
    std::size_t encoded_block_bytes{};
    /** Per-lane decoder state plus scratch bytes at decoder_block_size. */
    std::size_t decoder_workspace_bytes{};
    std::size_t trailing_bytes{};
};

using FrameSink = std::function<void(std::span<const std::byte>)>;

/**
 * Fill an exact byte range from a stable random-access source.
 *
 * The callback must either fill the complete output span or throw. Offsets are
 * validated against the source size supplied to the range-backed frame API
 * before the callback is invoked. Source bytes must remain stable for the
 * duration of the enclosing codec call; filesystem callers should additionally
 * pin and revalidate source identity before publishing derived output.
 */
using RangeReader =
    std::function<void(std::uint64_t offset, std::span<std::byte> output)>;

/** A reusable low-level bzip3 state and scratch arena for one fixed block size. */
class Workspace final {
public:
    explicit Workspace(std::uint32_t block_size);
    ~Workspace();

    Workspace(Workspace&&) noexcept;
    Workspace& operator=(Workspace&&) noexcept;
    Workspace(const Workspace&) = delete;
    Workspace& operator=(const Workspace&) = delete;

    [[nodiscard]] std::uint32_t block_size() const noexcept;
    [[nodiscard]] std::size_t scratch_capacity() const noexcept;

    /**
     * Encode one block and return a view into workspace-owned storage.
     * The view is invalidated by the next operation on this workspace.
     */
    [[nodiscard]] std::span<const std::byte> encode_block_view(
        std::span<const std::byte> input);

    /** Read one block directly into workspace storage and encode it in place. */
    [[nodiscard]] std::span<const std::byte> encode_block_from(
        std::size_t input_size,
        std::uint64_t source_offset,
        const RangeReader& reader);

    /** Encode one block and return independently owned BZ3v1 payload bytes. */
    [[nodiscard]] std::vector<std::byte> encode_block(
        std::span<const std::byte> input);

    /**
     * Decode one BZ3v1 block payload and return a view into workspace-owned
     * storage. The decoded byte count must exactly match original_size.
     * The view is invalidated by the next operation on this workspace.
     */
    [[nodiscard]] std::span<const std::byte> decode_block_view(
        std::span<const std::byte> encoded,
        std::size_t original_size);

    /** Read one encoded payload directly into workspace storage and decode it. */
    [[nodiscard]] std::span<const std::byte> decode_block_from(
        std::size_t encoded_size,
        std::size_t original_size,
        std::uint64_t source_offset,
        const RangeReader& reader);

    /** Decode one BZ3v1 block payload into caller-owned storage. */
    void decode_block_into(
        std::span<const std::byte> encoded,
        std::span<std::byte> output);

    /** Decode one BZ3v1 block payload into an independently owned vector. */
    [[nodiscard]] std::vector<std::byte> decode_block(
        std::span<const std::byte> encoded,
        std::size_t original_size);

    /**
     * Emit a complete BZ3v1 frame in order without materializing the full frame.
     * Sink spans are valid only for the duration of each callback. A later codec
     * error or sink exception may leave the sink with a valid frame prefix.
     */
    [[nodiscard]] FrameInfo encode_frame_to(
        std::span<const std::byte> input,
        const FrameSink& sink);

    /**
     * Emit a complete frame from stable random-access input without
     * materializing the complete input or a separate caller-side block buffer.
     */
    [[nodiscard]] FrameInfo encode_frame_from(
        std::size_t input_size,
        const RangeReader& reader,
        const FrameSink& sink);

    /** Build a complete BZ3v1 frame with correct exact-multiple block splitting. */
    [[nodiscard]] std::vector<std::byte> encode_frame(std::span<const std::byte> input);

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

/** Select the effective BZ3v1 block size used by the safe frame APIs. */
[[nodiscard]] std::uint32_t select_frame_block_size(
    std::uint32_t requested_block_size,
    std::size_t input_size);

/**
 * Return the checked per-lane codec-state plus scratch-memory requirement for
 * one workspace at block_size. Parallel callers use this before retaining a
 * pool so memory policy is enforced before any worker thread is started.
 */
[[nodiscard]] std::size_t workspace_memory_bound(std::uint32_t block_size);

/**
 * Return a checked worst-case frame capacity for a fixed block size.
 * Unlike upstream bz3_bound(input_size), this includes every per-block frame
 * header and every per-block expansion allowance.
 */
[[nodiscard]] std::size_t frame_bound(std::size_t input_size, std::uint32_t block_size);

/**
 * Emit a frame using an input-sensitive effective block size while fixing
 * upstream's exact-multiple split defect. The checked frame shape is known
 * before the first sink call, but a later codec or sink failure may leave a
 * prefix in the sink. Use atomic staging when publishing to a filesystem name.
 */
[[nodiscard]] FrameInfo compress_frame_to(
    std::span<const std::byte> input,
    std::uint32_t requested_block_size,
    const FrameSink& sink);

/** Range-backed counterpart to compress_frame_to(). */
[[nodiscard]] FrameInfo compress_frame_from(
    std::size_t input_size,
    std::uint32_t requested_block_size,
    const RangeReader& reader,
    const FrameSink& sink);

/** Encode the same safe frame into an independently owned vector. */
[[nodiscard]] std::vector<std::byte> compress_frame(
    std::span<const std::byte> input,
    std::uint32_t requested_block_size = 16U * 1024U * 1024U);

/** Decode a complete frame with checked arithmetic, output, and workspace budgets. */
[[nodiscard]] std::vector<std::byte> decompress_frame(
    std::span<const std::byte> encoded,
    std::size_t max_output_size,
    bool reject_trailing_bytes = true,
    std::size_t max_workspace_bytes = default_decoder_workspace_budget);

/**
 * Decode a complete frame block-by-block into a sink without materializing the
 * full output. The entire frame envelope is validated before the first sink
 * call. Each sink span aliases workspace storage and is valid only for the
 * duration of that call; the sink must copy or synchronously consume it. A
 * later compressed-block error or sink exception may leave the sink with a
 * valid decoded prefix, so callers requiring atomic publication should write
 * to a temporary destination and commit only after this function returns.
 */
[[nodiscard]] FrameInfo decompress_frame_to(
    std::span<const std::byte> encoded,
    std::size_t max_output_size,
    const FrameSink& sink,
    bool reject_trailing_bytes = true,
    std::size_t max_workspace_bytes = default_decoder_workspace_budget);

/**
 * Range-backed counterpart to decompress_frame_to(). The complete frame
 * envelope is validated with fixed-size reads before the first decoded
 * callback; payloads are then loaded one block at a time into workspace.
 */
[[nodiscard]] FrameInfo decompress_frame_from(
    std::size_t encoded_size,
    const RangeReader& reader,
    std::size_t max_output_size,
    const FrameSink& sink,
    bool reject_trailing_bytes = true,
    std::size_t max_workspace_bytes = default_decoder_workspace_budget);

/** Parse and validate the frame envelope and resource budgets without decoding. */
[[nodiscard]] FrameInfo inspect_frame(
    std::span<const std::byte> encoded,
    std::size_t max_output_size,
    bool reject_trailing_bytes = true,
    std::size_t max_workspace_bytes = default_decoder_workspace_budget);

/** Parse a range-backed frame using only fixed-size envelope reads. */
[[nodiscard]] FrameInfo inspect_frame_from(
    std::size_t encoded_size,
    const RangeReader& reader,
    std::size_t max_output_size,
    bool reject_trailing_bytes = true,
    std::size_t max_workspace_bytes = default_decoder_workspace_budget);

/** Isolated upstream high-level framing witness retained for compatibility tests.
 * It intentionally preserves upstream 1.5.3's exact-multiple final-block
 * defect. The public bz3_compress C entry point and all normal bzip4 encoders
 * use corrected remaining-byte splitting. */
[[nodiscard]] std::vector<std::byte> compress_frame_upstream_exact(
    std::span<const std::byte> input,
    std::uint32_t requested_block_size);

[[nodiscard]] const char* translated_codec_version() noexcept;

} // namespace bzip4
