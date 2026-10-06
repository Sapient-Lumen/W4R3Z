#pragma once

#include "bzip4/codec.hpp"

#include <cstddef>
#include <cstdint>
#include <span>
#include <string_view>

namespace bzip4 {

/**
 * A versioned, byte-defining block policy plus realization-local defaults.
 *
 * requested_block_size affects encoded bytes and is therefore part of the
 * stable profile contract. requested_lanes and default_workspace_bytes affect
 * scheduling only; fitting them downward cannot change BZ3v1 bytes.
 */
struct CodecProfile {
    std::string_view id;
    std::string_view purpose;
    std::uint32_t requested_block_size{};
    std::size_t requested_lanes{};
    std::size_t default_workspace_bytes{};
};

inline constexpr std::size_t profile_default_workspace_bytes =
    128U * 1024U * 1024U;

/** The complete immutable profile registry carried by this release. */
[[nodiscard]] std::span<const CodecProfile> codec_profiles() noexcept;

/** Resolve an exact profile identifier or throw std::invalid_argument. */
[[nodiscard]] const CodecProfile& codec_profile(std::string_view id);

/** Effective serialized block size for this profile and input length. */
[[nodiscard]] std::uint32_t profile_effective_block_size(
    const CodecProfile& profile,
    std::size_t input_size);

/**
 * Verify compatibility with this profile's serialized block law.
 *
 * Small inputs can make multiple profiles converge to the same effective block
 * size. The BZ3v1 frame therefore cannot prove the external profile identifier;
 * an embedder must bind that identifier in its own authenticated metadata.
 */
[[nodiscard]] bool frame_is_compatible_with_profile(
    const FrameInfo& frame,
    const CodecProfile& profile);

} // namespace bzip4
