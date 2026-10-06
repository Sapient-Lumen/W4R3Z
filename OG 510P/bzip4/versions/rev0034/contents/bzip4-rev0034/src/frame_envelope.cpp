#include "frame_envelope.hpp"

#include "bzip4/codec.hpp"
#include "bzip4/libbz3.h"

#include <algorithm>
#include <bit>
#include <limits>

namespace bzip4::detail {
namespace {

constexpr std::size_t fixed_header_size = 8;
constexpr std::uint8_t supported_model_bits = 0x06U;

[[nodiscard]] std::uint32_t read_u32_le(const std::uint8_t* data) noexcept {
    return static_cast<std::uint32_t>(data[0]) |
           (static_cast<std::uint32_t>(data[1]) << 8U) |
           (static_cast<std::uint32_t>(data[2]) << 16U) |
           (static_cast<std::uint32_t>(data[3]) << 24U);
}

[[nodiscard]] std::int32_t read_i32_le(const std::uint8_t* data) noexcept {
    return std::bit_cast<std::int32_t>(read_u32_le(data));
}

[[nodiscard]] BlockEnvelopeValidation failure(
    int error_code,
    BlockEnvelopeIssue issue) noexcept {
    return {error_code, issue, {}};
}

[[nodiscard]] bool legal_declared_block_size(std::uint32_t block_size) noexcept {
    return block_size >= min_block_size && block_size <= max_block_size;
}

} // namespace

BlockEnvelopeValidation validate_block_envelope(
    std::size_t payload_size,
    std::span<const std::uint8_t> prefix,
    std::size_t original_size,
    std::uint32_t declared_block_size) noexcept {
    if (!legal_declared_block_size(declared_block_size)) {
        return failure(BZ3_ERR_INIT,
                       BlockEnvelopeIssue::invalid_declared_block_size);
    }
    if (original_size > declared_block_size) {
        return failure(BZ3_ERR_MALFORMED_HEADER,
                       BlockEnvelopeIssue::original_size_out_of_range);
    }
    if (payload_size < fixed_header_size) {
        return failure(BZ3_ERR_MALFORMED_HEADER,
                       BlockEnvelopeIssue::payload_too_short);
    }
    const std::size_t transform_bound = bz3_bound(declared_block_size);
    if (payload_size > transform_bound) {
        return failure(BZ3_ERR_MALFORMED_HEADER,
                       BlockEnvelopeIssue::payload_too_large);
    }
    if (prefix.size() < fixed_header_size) {
        return failure(BZ3_ERR_TRUNCATED_DATA,
                       BlockEnvelopeIssue::prefix_too_short);
    }

    BlockEnvelope envelope;
    envelope.bwt_index = read_i32_le(prefix.data() + 4);
    envelope.requirements = {original_size, payload_size};
    if (envelope.bwt_index == -1) {
        const std::size_t literal_size = payload_size - fixed_header_size;
        if (literal_size > 64 || literal_size != original_size) {
            return failure(BZ3_ERR_MALFORMED_HEADER,
                           BlockEnvelopeIssue::raw_length_mismatch);
        }
        envelope.raw = true;
        envelope.header_size = fixed_header_size;
        envelope.size_before_bwt = static_cast<std::int32_t>(original_size);
        return {BZ3_OK, BlockEnvelopeIssue::none, envelope};
    }
    if (envelope.bwt_index <= 0) {
        return failure(BZ3_ERR_MALFORMED_HEADER,
                       BlockEnvelopeIssue::nonpositive_bwt_index);
    }
    if (original_size == 0) {
        return failure(BZ3_ERR_MALFORMED_HEADER,
                       BlockEnvelopeIssue::regular_empty_output);
    }
    if (payload_size < 9) {
        return failure(BZ3_ERR_MALFORMED_HEADER,
                       BlockEnvelopeIssue::missing_model);
    }
    if (prefix.size() < 9) {
        return failure(BZ3_ERR_TRUNCATED_DATA,
                       BlockEnvelopeIssue::prefix_too_short);
    }

    envelope.model = prefix[8];
    if ((envelope.model & static_cast<std::uint8_t>(~supported_model_bits)) != 0U) {
        return failure(BZ3_ERR_MALFORMED_HEADER,
                       BlockEnvelopeIssue::unsupported_model);
    }

    envelope.header_size = 9;
    if ((envelope.model & 0x02U) != 0U) envelope.header_size += 4;
    if ((envelope.model & 0x04U) != 0U) envelope.header_size += 4;
    if (payload_size < envelope.header_size + 4) {
        return failure(BZ3_ERR_TRUNCATED_DATA,
                       BlockEnvelopeIssue::truncated_model_header);
    }
    if (prefix.size() < envelope.header_size) {
        return failure(BZ3_ERR_TRUNCATED_DATA,
                       BlockEnvelopeIssue::prefix_too_short);
    }

    std::size_t field_offset = 9;
    if ((envelope.model & 0x02U) != 0U) {
        envelope.lzp_size = read_i32_le(prefix.data() + field_offset);
        if (envelope.lzp_size < 4 ||
            static_cast<std::size_t>(envelope.lzp_size) > transform_bound) {
            return failure(BZ3_ERR_MALFORMED_HEADER,
                           BlockEnvelopeIssue::invalid_lzp_size);
        }
        envelope.requirements.bound_extent = std::max(
            envelope.requirements.bound_extent,
            static_cast<std::size_t>(envelope.lzp_size));
        field_offset += 4;
    }
    if ((envelope.model & 0x04U) != 0U) {
        envelope.rle_size = read_i32_le(prefix.data() + field_offset);
        if (envelope.rle_size < 32 ||
            static_cast<std::size_t>(envelope.rle_size) > transform_bound) {
            return failure(BZ3_ERR_MALFORMED_HEADER,
                           BlockEnvelopeIssue::invalid_rle_size);
        }
        envelope.requirements.bound_extent = std::max(
            envelope.requirements.bound_extent,
            static_cast<std::size_t>(envelope.rle_size));
    }

    if ((envelope.model & 0x02U) != 0U) {
        envelope.size_before_bwt = envelope.lzp_size;
    } else if ((envelope.model & 0x04U) != 0U) {
        envelope.size_before_bwt = envelope.rle_size;
    } else {
        envelope.size_before_bwt = static_cast<std::int32_t>(original_size);
    }
    if (envelope.size_before_bwt <= 0 ||
        envelope.bwt_index > envelope.size_before_bwt) {
        return failure(BZ3_ERR_MALFORMED_HEADER,
                       BlockEnvelopeIssue::bwt_index_out_of_range);
    }

    return {BZ3_OK, BlockEnvelopeIssue::none, envelope};
}

void merge_decoder_requirements(
    DecoderWorkspaceRequirements& aggregate,
    const BlockEnvelopeValidation& validation) noexcept {
    if (validation.error_code != BZ3_OK) return;
    aggregate.block_extent = std::max(
        aggregate.block_extent,
        validation.envelope.requirements.block_extent);
    aggregate.bound_extent = std::max(
        aggregate.bound_extent,
        validation.envelope.requirements.bound_extent);
}

std::uint32_t select_decoder_block_size(
    const DecoderWorkspaceRequirements& requirements,
    std::uint32_t declared_block_size) noexcept {
    if (!legal_declared_block_size(declared_block_size) ||
        requirements.block_extent > declared_block_size ||
        requirements.bound_extent > bz3_bound(declared_block_size)) {
        return 0;
    }

    std::size_t lower = std::max<std::size_t>(
        min_block_size, requirements.block_extent);
    if (lower > declared_block_size ||
        lower > std::numeric_limits<std::uint32_t>::max()) {
        return 0;
    }

    std::uint32_t first = static_cast<std::uint32_t>(lower);
    std::uint32_t last = declared_block_size;
    while (first < last) {
        const std::uint32_t middle = first + (last - first) / 2U;
        if (bz3_bound(middle) >= requirements.bound_extent) {
            last = middle;
        } else {
            first = middle + 1U;
        }
    }
    return bz3_bound(first) >= requirements.bound_extent ? first : 0;
}

const char* block_envelope_issue_message(BlockEnvelopeIssue issue) noexcept {
    switch (issue) {
    case BlockEnvelopeIssue::none:
        return "no block-envelope error";
    case BlockEnvelopeIssue::invalid_declared_block_size:
        return "declared BZ3 block size is outside the legal range";
    case BlockEnvelopeIssue::original_size_out_of_range:
        return "original block size exceeds the declared frame block size";
    case BlockEnvelopeIssue::payload_too_short:
        return "BZ3 block payload is shorter than its fixed header";
    case BlockEnvelopeIssue::payload_too_large:
        return "BZ3 block payload exceeds the declared block bound";
    case BlockEnvelopeIssue::prefix_too_short:
        return "block envelope prefix is shorter than the required model metadata";
    case BlockEnvelopeIssue::raw_length_mismatch:
        return "raw BZ3 block length disagrees with its frame descriptor";
    case BlockEnvelopeIssue::nonpositive_bwt_index:
        return "regular BZ3 block has a nonpositive BWT primary index";
    case BlockEnvelopeIssue::regular_empty_output:
        return "regular BZ3 block cannot describe empty output";
    case BlockEnvelopeIssue::missing_model:
        return "regular BZ3 block lacks its model byte";
    case BlockEnvelopeIssue::unsupported_model:
        return "BZ3 block uses unsupported model bits";
    case BlockEnvelopeIssue::truncated_model_header:
        return "regular BZ3 block has a truncated model header or entropy payload";
    case BlockEnvelopeIssue::invalid_lzp_size:
        return "invalid LZP intermediate size";
    case BlockEnvelopeIssue::invalid_rle_size:
        return "invalid RLE intermediate size";
    case BlockEnvelopeIssue::bwt_index_out_of_range:
        return "BWT primary index exceeds the transformed block size";
    }
    return "unknown block-envelope error";
}

} // namespace bzip4::detail
