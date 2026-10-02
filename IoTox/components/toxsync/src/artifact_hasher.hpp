#pragma once

#include "toxsync/hash.hpp"

#include <span>

namespace toxsync::detail {

class ArtifactSha256 final {
public:
    ArtifactSha256();
    ~ArtifactSha256();
    ArtifactSha256(ArtifactSha256&&) noexcept;
    ArtifactSha256& operator=(ArtifactSha256&&) noexcept;
    ArtifactSha256(const ArtifactSha256&) = delete;
    ArtifactSha256& operator=(const ArtifactSha256&) = delete;

    void update(std::span<const std::byte> bytes);
    [[nodiscard]] Digest256 finish();

private:
#if defined(TOXSYNC_HAVE_OPENSSL)
    void* context_{};
#else
    Sha256 portable_{};
#endif
    Digest256 digest_{};
    bool finished_{};
};

} // namespace toxsync::detail
