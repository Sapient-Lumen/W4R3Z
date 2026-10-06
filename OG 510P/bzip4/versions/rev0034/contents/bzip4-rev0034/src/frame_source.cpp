#include "frame_source.hpp"
#include "frame_envelope.hpp"

#include "bzip4/libbz3.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cstring>
#include <limits>
#include <stdexcept>

namespace bzip4::detail {
namespace {

constexpr std::size_t block_payload_minimum = 8;
constexpr std::size_t block_envelope_prefix_size = 17;
constexpr std::size_t block_probe_size = block_header_size + block_envelope_prefix_size;

[[nodiscard]] std::uint32_t read_u32_le(const std::byte* data) noexcept {
    return std::to_integer<std::uint32_t>(data[0]) |
           (std::to_integer<std::uint32_t>(data[1]) << 8U) |
           (std::to_integer<std::uint32_t>(data[2]) << 16U) |
           (std::to_integer<std::uint32_t>(data[3]) << 24U);
}

[[nodiscard]] std::int32_t read_i32_le(const std::byte* data) noexcept {
    return std::bit_cast<std::int32_t>(read_u32_le(data));
}

[[nodiscard]] std::size_t checked_add(std::size_t lhs, std::size_t rhs) {
    if (rhs > std::numeric_limits<std::size_t>::max() - lhs) {
        throw CodecError(BZ3_ERR_DATA_TOO_BIG, "frame-source size arithmetic overflow");
    }
    return lhs + rhs;
}

void validate_block_size(std::uint32_t block_size) {
    if (block_size < min_block_size || block_size > max_block_size) {
        throw CodecError(BZ3_ERR_INIT, "block size must be between 65 KiB and 511 MiB");
    }
}

[[nodiscard]] BlockDescriptor parse_block_descriptor(
    const FrameSource& source,
    std::uint32_t index,
    std::size_t cursor,
    std::size_t output_offset,
    std::uint32_t block_size,
    std::span<const std::byte> descriptor) {
    if (descriptor.size() < block_header_size) {
        throw std::logic_error("block descriptor parser received a short span");
    }
    const std::int32_t compressed_signed = read_i32_le(descriptor.data());
    const std::int32_t original_signed = read_i32_le(descriptor.data() + 4);
    if (compressed_signed < 0 || original_signed < 0) {
        throw CodecError(BZ3_ERR_MALFORMED_HEADER,
                         "negative block size in frame descriptor");
    }

    const std::size_t compressed = static_cast<std::size_t>(compressed_signed);
    const std::size_t original = static_cast<std::size_t>(original_signed);
    if (compressed > bz3_bound(block_size)) {
        throw CodecError(BZ3_ERR_MALFORMED_HEADER,
                         "compressed block exceeds the checked block bound");
    }
    if (original > block_size) {
        throw CodecError(BZ3_ERR_MALFORMED_HEADER,
                         "original block exceeds the declared frame block size");
    }

    const std::size_t payload_offset = checked_add(cursor, block_header_size);
    if (payload_offset > source.size || compressed > source.size - payload_offset) {
        throw CodecError(BZ3_ERR_TRUNCATED_DATA,
                         "compressed block extends past end of frame");
    }
    return {index, payload_offset, compressed, original, output_offset};
}

[[nodiscard]] BlockDescriptor read_block_descriptor(
    const FrameSource& source,
    std::uint32_t index,
    std::size_t cursor,
    std::size_t output_offset,
    std::uint32_t block_size) {
    if (cursor > source.size || source.size - cursor < block_header_size) {
        throw CodecError(BZ3_ERR_TRUNCATED_DATA, "truncated block descriptor");
    }
    std::array<std::byte, block_header_size> descriptor{};
    read_source(source, cursor, descriptor);
    return parse_block_descriptor(
        source, index, cursor, output_offset, block_size, descriptor);
}

} // namespace

std::uint64_t source_offset(std::size_t value) {
    if constexpr (sizeof(std::size_t) > sizeof(std::uint64_t)) {
        if (value > std::numeric_limits<std::uint64_t>::max()) {
            throw CodecError(BZ3_ERR_DATA_TOO_BIG,
                             "range source offset cannot be represented in uint64_t");
        }
    }
    return static_cast<std::uint64_t>(value);
}

void read_source(
    const FrameSource& source,
    std::size_t offset,
    std::span<std::byte> output) {
    if (offset > source.size || output.size() > source.size - offset) {
        throw CodecError(BZ3_ERR_TRUNCATED_DATA,
                         "requested byte range is outside the frame source");
    }
    if (!output.empty()) {
        source.reader(source_offset(offset), output);
    }
}

RangeReader span_reader(std::span<const std::byte> input) {
    return [input](std::uint64_t offset, std::span<std::byte> output) {
        const std::size_t position = static_cast<std::size_t>(offset);
        if (static_cast<std::uint64_t>(position) != offset || position > input.size() ||
            output.size() > input.size() - position) {
            throw std::out_of_range("memory frame source range is outside the input span");
        }
        if (!output.empty()) {
            std::memmove(output.data(), input.subspan(position, output.size()).data(), output.size());
        }
    };
}

FrameInfo scan_frame_source(
    const FrameSource& source,
    std::size_t max_output_size,
    bool reject_trailing_bytes,
    std::size_t max_workspace_bytes) {
    if (!source.reader) {
        throw std::invalid_argument("range reader must be callable");
    }
    if (source.size < frame_header_size) {
        throw CodecError(BZ3_ERR_MALFORMED_HEADER,
                         "frame is shorter than the 13-byte BZ3v1 header");
    }

    std::array<std::byte, frame_header_size> header{};
    read_source(source, 0, header);
    constexpr std::array<std::byte, 5> magic{
        std::byte{'B'}, std::byte{'Z'}, std::byte{'3'}, std::byte{'v'}, std::byte{'1'}};
    if (!std::equal(magic.begin(), magic.end(), header.begin())) {
        throw CodecError(BZ3_ERR_MALFORMED_HEADER, "frame magic is not BZ3v1");
    }

    FrameInfo info;
    info.block_size = read_u32_le(header.data() + 5);
    info.block_count = read_u32_le(header.data() + 9);
    validate_block_size(info.block_size);

    const std::size_t available_after_header = source.size - frame_header_size;
    constexpr std::size_t minimum_record_size = block_header_size + block_payload_minimum;
    if (info.block_count > available_after_header / minimum_record_size) {
        throw CodecError(BZ3_ERR_MALFORMED_HEADER, "block count cannot fit in the frame");
    }

    DecoderWorkspaceRequirements workspace_requirements;
    std::size_t cursor = frame_header_size;
    for (std::uint32_t index = 0; index < info.block_count; ++index) {
        if (cursor > source.size || source.size - cursor < block_header_size) {
            throw CodecError(BZ3_ERR_TRUNCATED_DATA, "truncated block descriptor");
        }

        std::array<std::byte, block_probe_size> probe{};
        const std::size_t probe_size = std::min(probe.size(), source.size - cursor);
        read_source(source, cursor, std::span<std::byte>(probe).first(probe_size));
        const BlockDescriptor block = parse_block_descriptor(
            source, index, cursor, info.original_size, info.block_size,
            std::span<const std::byte>(probe).first(block_header_size));
        const std::size_t prefix_size = std::min(
            block.compressed_size, block_envelope_prefix_size);
        if (probe_size - block_header_size < prefix_size) {
            throw std::logic_error("block probe did not cover the validated model prefix");
        }
        const auto prefix_bytes =
            std::span<const std::byte>(probe).subspan(block_header_size, prefix_size);
        const BlockEnvelopeValidation envelope = validate_block_envelope(
            block.compressed_size,
            {reinterpret_cast<const std::uint8_t*>(prefix_bytes.data()),
             prefix_bytes.size()},
            block.original_size, info.block_size);
        if (envelope.error_code != BZ3_OK) {
            throw CodecError(
                envelope.error_code,
                block_envelope_issue_message(envelope.issue));
        }
        merge_decoder_requirements(workspace_requirements, envelope);
        info.original_size = checked_add(info.original_size, block.original_size);
        if (info.original_size > max_output_size) {
            throw CodecError(BZ3_ERR_DATA_TOO_BIG,
                             "decoded frame exceeds the configured output budget");
        }
        info.encoded_block_bytes = checked_add(
            info.encoded_block_bytes, block.compressed_size);
        cursor = checked_add(block.payload_offset, block.compressed_size);
    }

    if (info.block_count != 0) {
        info.decoder_block_size = select_decoder_block_size(
            workspace_requirements, info.block_size);
        if (info.decoder_block_size == 0) {
            throw CodecError(
                BZ3_ERR_MALFORMED_HEADER,
                "validated block extents cannot fit the declared frame block size");
        }
        info.decoder_workspace_bytes = workspace_memory_bound(
            info.decoder_block_size);
        if (info.decoder_workspace_bytes > max_workspace_bytes) {
            throw CodecError(BZ3_ERR_DATA_TOO_BIG,
                             "decoder workspace exceeds the configured memory budget");
        }
    }

    info.trailing_bytes = source.size - cursor;
    if (reject_trailing_bytes && info.trailing_bytes != 0) {
        throw CodecError(BZ3_ERR_MALFORMED_HEADER,
                         "trailing bytes follow the final BZ3v1 block");
    }
    return info;
}

FrameBlockCursor::FrameBlockCursor(
    const FrameSource& source,
    const FrameInfo& info) noexcept
    : source_(source), info_(info) {}

bool FrameBlockCursor::has_next() const noexcept {
    return index_ < info_.block_count;
}

BlockDescriptor FrameBlockCursor::next() {
    if (!has_next()) {
        throw std::logic_error("frame block cursor advanced past the validated block count");
    }
    const BlockDescriptor block = read_block_descriptor(
        source_, index_, cursor_, output_offset_, info_.block_size);
    if (output_offset_ > info_.original_size ||
        encoded_total_ > info_.encoded_block_bytes ||
        block.original_size > info_.original_size - output_offset_ ||
        block.compressed_size > info_.encoded_block_bytes - encoded_total_) {
        throw CodecError(BZ3_ERR_MALFORMED_HEADER,
                         "range-backed frame descriptors changed after validation");
    }

    cursor_ = checked_add(block.payload_offset, block.compressed_size);
    output_offset_ = checked_add(output_offset_, block.original_size);
    encoded_total_ = checked_add(encoded_total_, block.compressed_size);
    ++index_;
    return block;
}

void FrameBlockCursor::require_complete() const {
    if (index_ != info_.block_count || output_offset_ != info_.original_size ||
        encoded_total_ != info_.encoded_block_bytes || cursor_ > source_.size ||
        source_.size - cursor_ != info_.trailing_bytes) {
        throw CodecError(BZ3_ERR_MALFORMED_HEADER,
                         "range-backed frame shape changed after validation");
    }
}

} // namespace bzip4::detail
