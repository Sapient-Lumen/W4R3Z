#pragma once

#include <cstddef>
#include <cstdint>
#include <span>

namespace bzip4::detail {

enum class BlockEnvelopeIssue : std::uint8_t {
    none,
    invalid_declared_block_size,
    original_size_out_of_range,
    payload_too_short,
    payload_too_large,
    prefix_too_short,
    raw_length_mismatch,
    nonpositive_bwt_index,
    regular_empty_output,
    missing_model,
    unsupported_model,
    truncated_model_header,
    invalid_lzp_size,
    invalid_rle_size,
    bwt_index_out_of_range,
};

/**
 * Decoder extents accumulated from already validated block envelopes.
 *
 * block_extent is constrained directly by bz3_state::block_size (the decoded
 * original size). bound_extent is constrained by bz3_bound(block_size): the
 * encoded payload and any LZP/RLE/BWT intermediate stored in codec buffers.
 */
struct DecoderWorkspaceRequirements {
    std::size_t block_extent{};
    std::size_t bound_extent{};
};

/** Parsed, constant-metadata description of one valid BZ3v1 block payload. */
struct BlockEnvelope {
    bool raw{};
    std::uint8_t model{};
    std::int32_t bwt_index{-1};
    std::int32_t lzp_size{-1};
    std::int32_t rle_size{-1};
    std::int32_t size_before_bwt{};
    std::size_t header_size{};
    DecoderWorkspaceRequirements requirements{};
};

struct BlockEnvelopeValidation {
    int error_code{};
    BlockEnvelopeIssue issue{BlockEnvelopeIssue::none};
    BlockEnvelope envelope{};
};

/**
 * Validate and parse the constant-metadata portion of one BZ3 block payload.
 *
 * prefix may contain only the first min(payload_size, 17) bytes. The parsed
 * envelope is meaningful only when error_code is BZ3_OK. The same parser is
 * used by the low-level block decoder, every frame preflight, and encoder
 * metadata accounting so those boundaries cannot drift independently.
 */
[[nodiscard]] BlockEnvelopeValidation validate_block_envelope(
    std::size_t payload_size,
    std::span<const std::uint8_t> prefix,
    std::size_t original_size,
    std::uint32_t declared_block_size) noexcept;

/** Merge one successful envelope result into frame-wide decoder requirements. */
void merge_decoder_requirements(
    DecoderWorkspaceRequirements& aggregate,
    const BlockEnvelopeValidation& envelope) noexcept;

/**
 * Select the smallest legal bz3_state block size satisfying validated frame
 * requirements. Returns zero when the requirements cannot fit the declaration.
 */
[[nodiscard]] std::uint32_t select_decoder_block_size(
    const DecoderWorkspaceRequirements& requirements,
    std::uint32_t declared_block_size) noexcept;

[[nodiscard]] const char* block_envelope_issue_message(
    BlockEnvelopeIssue issue) noexcept;

} // namespace bzip4::detail
