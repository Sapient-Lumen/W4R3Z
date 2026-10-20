#pragma once

#include "iotox/security/identity.hpp"
#include "iotox/sync_content.hpp"
#include "iotox/sync_publication.hpp"
#include "iotox/sync_transaction.hpp"

#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <functional>

namespace iotox::sync {

enum class SyncContentPublicationFormat : std::uint8_t {
  automatic = 1U,
  flat = 2U,
  paged = 3U,
};

struct SyncContentPublicationConfig {
  SyncContentPublicationFormat format{SyncContentPublicationFormat::automatic};
  std::uint32_t minimum_chunk_bytes{64U * 1024U};
  std::uint32_t average_chunk_bytes{256U * 1024U};
  std::uint32_t maximum_chunk_bytes{1024U * 1024U};
  std::uint32_t entries_per_page{1024U};
  std::size_t io_buffer_bytes{256U * 1024U};
  std::size_t manifest_buffer_bytes{64U * 1024U};
  std::size_t workspace_budget_bytes{64U * 1024U * 1024U};
  bool fsync_on_commit{true};
};

struct SyncContentPublicationSeams {
  std::function<bool()> cancel_requested;
};

struct SyncContentPublicationResult {
  SignedHeadPublicationResult publication;
  SyncContentPublicationFormat format{SyncContentPublicationFormat::flat};
  Digest artifact{};
  Digest manifest{};
  std::uint64_t artifact_bytes{0U};
  std::uint64_t manifest_bytes{0U};
  std::uint64_t chunks{0U};
  std::uint64_t pages{0U};
  std::uint64_t unique_objects{0U};
  std::uint64_t unique_object_bytes{0U};
  std::uint64_t objects_installed{0U};
  std::uint64_t objects_reused{0U};
  std::uint64_t bytes_copied{0U};
  std::size_t workspace_reserved_bytes{0U};
};

// Removes only exact abandoned local content-publication workspaces while the
// namespace transaction excludes a live publisher. It never scans or removes
// network-attempt staging.
[[nodiscard]] Result<std::size_t> cleanup_sync_content_publication_staging(
    const NamespacePolicy &policy, const SyncNamespaceTransaction &transaction);

// Builds a bounded flat or paged content fabric in private namespace staging,
// prospectively admits the complete unique object set against combined quota,
// imports every object through the verified content commit, and signs HEAD
// last. A failed build/import may leave immutable unreachable CAS objects but
// never publishes a HEAD naming an incomplete fabric.
[[nodiscard]] Result<SyncContentPublicationResult>
publish_local_content_revision(const NamespacePolicy &policy,
                               const std::filesystem::path &artifact_source,
                               const security::DeviceIdentity &identity,
                               const security::Sodium &sodium,
                               SignedHeadStore &head_store,
                               SyncContentPublicationConfig config = {},
                               SyncContentPublicationSeams seams = {});

} // namespace iotox::sync
