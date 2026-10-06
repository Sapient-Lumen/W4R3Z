#include "bzip4/profile.hpp"

#include <array>
#include <stdexcept>
#include <string>

namespace bzip4 {
namespace {

constexpr std::array<CodecProfile, 3> profiles{{
    {
        "datacube-capsule-speed-v1",
        "latency-first profile for small Datacube source capsules",
        256U * 1024U,
        8U,
        profile_default_workspace_bytes,
    },
    {
        "cloudtainer-speed-v1",
        "general cloudtainer encode/decode throughput profile",
        1024U * 1024U,
        8U,
        profile_default_workspace_bytes,
    },
    {
        "cloudtainer-balanced-v1",
        "measured speed/size compromise for larger payloads",
        2U * 1024U * 1024U,
        8U,
        profile_default_workspace_bytes,
    },
}};

} // namespace

std::span<const CodecProfile> codec_profiles() noexcept {
    return profiles;
}

const CodecProfile& codec_profile(std::string_view id) {
    for (const CodecProfile& profile : profiles) {
        if (profile.id == id) return profile;
    }
    throw std::invalid_argument("unknown bzip4 codec profile: " + std::string(id));
}

std::uint32_t profile_effective_block_size(
    const CodecProfile& profile,
    std::size_t input_size) {
    return select_frame_block_size(profile.requested_block_size, input_size);
}

bool frame_is_compatible_with_profile(
    const FrameInfo& frame,
    const CodecProfile& profile) {
    return frame.block_size == profile_effective_block_size(profile, frame.original_size);
}

} // namespace bzip4
