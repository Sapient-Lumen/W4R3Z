#pragma once

#include "iotox/status.hpp"
#include "iotox/sync_head.hpp"

#include <cstdint>
#include <filesystem>

namespace iotox::sync {

struct SyncRangeManifestInfo {
  Digest artifact{};
  std::uint64_t artifact_bytes{0U};
  std::uint64_t manifest_bytes{0U};
  std::uint64_t blocks{0U};
  std::uint32_t block_bytes{0U};
};

// Builds the canonical toxsync range-v1 index for one immutable file. The
// caller owns OUTPUT and removes it after ordered local publication.
[[nodiscard]] Result<SyncRangeManifestInfo> build_sync_range_manifest(
    const NamespacePolicy &policy,
    const std::filesystem::path &artifact,
    const std::filesystem::path &output);

// Validates that MANIFEST is a canonical, bounded range-v1 index for the exact
// artifact identity and size already named by a verified signed HEAD. Callers
// additionally retain the ordinary strict object-shape/digest checks.
[[nodiscard]] Status verify_sync_range_manifest(
    const NamespacePolicy &policy,
    const std::filesystem::path &artifact,
    const std::filesystem::path &manifest,
    const Digest &expected_artifact,
    std::uint64_t expected_artifact_bytes,
    std::uint64_t expected_manifest_bytes);

} // namespace iotox::sync
