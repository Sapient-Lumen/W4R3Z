#pragma once

#include "anonsync_core.hpp"

#include <string>
#include <string_view>

namespace anonsync {

[[nodiscard]] std::string digest_sync_chunk_vector(
    const std::vector<SyncChunkRange>& chunks);

// These functions consume already-validated manifest values. Public callers
// continue to cross validate_sync_manifest_entry()/validate_sync_folder_manifest()
// in sync_domain before reaching this leaf. The leaf owns exact legacy digest
// bytes and streams nested aggregate evidence without constructing an
// unbounded concatenated material string.
[[nodiscard]] std::string digest_validated_sync_manifest_entry(
    const SyncManifestEntry& entry);
[[nodiscard]] std::string digest_validated_sync_manifest_entry_version(
    const SyncManifestEntry& entry);
[[nodiscard]] std::string digest_validated_sync_folder_manifest(
    const SyncFolderManifest& manifest);
[[nodiscard]] std::string digest_validated_sync_mutation_key(
    std::string_view operation,
    std::string_view manifest_entry_digest);

}  // namespace anonsync
