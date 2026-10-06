#pragma once

#include "bzip4/codec.hpp"

#include <cstddef>
#include <cstdint>
#include <span>

namespace bzip4::detail {

inline constexpr std::size_t frame_header_size = 13;
inline constexpr std::size_t block_header_size = 8;

struct BlockDescriptor {
    std::uint32_t index{};
    std::size_t payload_offset{};
    std::size_t compressed_size{};
    std::size_t original_size{};
    std::size_t output_offset{};
};

struct FrameSource {
    std::size_t size{};
    const RangeReader& reader;
};

/** Convert a checked process-size offset to the public range-reader width. */
[[nodiscard]] std::uint64_t source_offset(std::size_t value);

/** Read one exact, already source-bounded range. */
void read_source(
    const FrameSource& source,
    std::size_t offset,
    std::span<std::byte> output);

/** Adapt an immutable span to the stable random-access reader contract. */
[[nodiscard]] RangeReader span_reader(std::span<const std::byte> input);

/**
 * Validate a complete BZ3v1 envelope with O(1) metadata retention.
 *
 * One 13-byte header and one at-most-25-byte descriptor/model probe are read
 * per block. No block-count-proportional descriptor vector is retained.
 */
[[nodiscard]] FrameInfo scan_frame_source(
    const FrameSource& source,
    std::size_t max_output_size,
    bool reject_trailing_bytes,
    std::size_t max_workspace_bytes);

/**
 * A second-pass, constant-metadata descriptor cursor.
 *
 * Each descriptor is reread and reconciled against the aggregate shape from a
 * prior scan. This catches changed sizes, offsets, totals, and trailing shape
 * before the descriptor is handed to a decoder batch.
 */
class FrameBlockCursor final {
public:
    FrameBlockCursor(const FrameSource& source, const FrameInfo& info) noexcept;

    [[nodiscard]] bool has_next() const noexcept;
    [[nodiscard]] BlockDescriptor next();
    void require_complete() const;

private:
    const FrameSource& source_;
    const FrameInfo& info_;
    std::size_t cursor_{frame_header_size};
    std::size_t output_offset_{};
    std::size_t encoded_total_{};
    std::uint32_t index_{};
};

} // namespace bzip4::detail
