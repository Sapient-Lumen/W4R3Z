#pragma once

#include "bzip4/libbz3.h"

#include <cstddef>
#include <cstdint>
#include <span>

namespace bzip4::detail {

/**
 * Borrowed result from the translated low-level block core.
 *
 * The pointer aliases either the caller buffer or storage owned by bz3_state and
 * remains valid only until the next operation on that state. A negative size
 * reports the same failure already stored in bz3_last_error(state).
 *
 * These entry points are intentionally internal. The public C API retains its
 * historical in-place contract by copying a successful borrowed result back to
 * the caller buffer when necessary.
 */
struct Bz3BlockView {
    std::uint8_t* data{};
    std::int32_t size{-1};
};

[[nodiscard]] Bz3BlockView bz3_encode_block_view(
    bz3_state* state,
    std::uint8_t* buffer,
    std::int32_t size) noexcept;

[[nodiscard]] Bz3BlockView bz3_decode_block_view(
    bz3_state* state,
    std::uint8_t* buffer,
    std::size_t buffer_size,
    std::int32_t compressed_size,
    std::int32_t original_size) noexcept;

struct Bz3EntropyDecodeStats {
    std::int32_t input_bytes_read{};
    std::int32_t output_symbols{};
    bool truncated{};
};

/** Last arithmetic-decoder progress for deterministic truncation-work tests. */
[[nodiscard]] Bz3EntropyDecodeStats bz3_entropy_decode_stats(
    const bz3_state* state) noexcept;

/** Internal exact-consumption LZP decoder used by the block core and tests. */
[[nodiscard]] int bz3_decode_lzp_exact(
    std::span<const std::uint8_t> input,
    std::span<std::uint8_t> output,
    std::span<std::int32_t> dictionary,
    std::uint32_t* crc) noexcept;

/** Internal exact-consumption modified-RLE decoder used by the block core and tests. */
[[nodiscard]] int bz3_decode_mrle_exact(
    std::span<const std::uint8_t> input,
    std::span<std::uint8_t> output,
    std::uint32_t* crc) noexcept;

} // namespace bzip4::detail
