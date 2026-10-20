#pragma once

#include "iotox/status.hpp"
#include "iotox/sync_head.hpp"

#include <filesystem>

namespace iotox::sync {

// Computes the SHA-256 identity used by the preserved toxsync content store.
// The opened object must remain one stable regular file for the entire read;
// symlinks, replacements, truncation, growth, and metadata races fail closed.
[[nodiscard]] Result<Digest> hash_sync_file_sha256(const std::filesystem::path &path);

} // namespace iotox::sync
