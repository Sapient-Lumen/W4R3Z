#pragma once

#include "iotox/status.hpp"
#include "iotox/sync_activation.hpp"
#include "iotox/sync_namespace.hpp"
#include "iotox/sync_transaction.hpp"

#include <cstdint>
#include <filesystem>
#include <functional>
#include <string_view>

namespace iotox::sync {

inline constexpr std::uint64_t kMaximumTreepackEntries = 4096U;
inline constexpr std::uint32_t kMaximumTreepackPathBytes = 4096U;

struct SyncTreepackStats {
  std::uint64_t directories{0U};
  std::uint64_t files{0U};
  std::uint64_t content_bytes{0U};
  std::uint64_t artifact_bytes{0U};

  [[nodiscard]] bool operator==(const SyncTreepackStats &) const = default;
};

struct SyncTreeActivationResult {
  SyncTreepackStats tree{};
  bool materialized{false};
  bool already_current{false};
  std::uint64_t recovered_staging_trees{0U};
  std::uint64_t recovered_pointer_temporaries{0U};
  std::uint64_t pruned_revision_trees{0U};

  [[nodiscard]] bool operator==(const SyncTreeActivationResult &) const =
      default;
};

// Named boundaries are reached only after the described local projection
// effect. They are an injected crash/failure seam for deterministic and
// separate-process qualification; normal product construction leaves the
// callback empty.
enum class SyncTreeProjectionPoint : std::uint8_t {
  unpacked = 1U,
  frozen = 2U,
  revision_committed = 3U,
  revision_synced = 4U,
  pointer_prepared = 5U,
  pointer_committed = 6U,
  pointer_synced = 7U,
  stale_projections_pruned = 8U,
};

struct SyncTreeProjectionSeams {
  std::function<Status(SyncTreeProjectionPoint point)> after_step;
};

[[nodiscard]] std::string_view
sync_tree_projection_point_name(SyncTreeProjectionPoint point) noexcept;

// Packs one owner-controlled directory into the canonical toxsync treepack-v1
// form. The complete artifact, entry population, individual file, path, and
// in-memory sort population are bounded by the namespace policy and fixed
// product ceilings. OUTPUT must be a pre-reserved private regular file.
[[nodiscard]] Result<SyncTreepackStats> build_sync_treepack(
    const NamespacePolicy &policy, const std::filesystem::path &source,
    const std::filesystem::path &output);

// Materializes one already verified and signed active treepack under
// POLICY.root/materialized-trees/revisions and atomically switches the local
// `current` symlink. The signed activation pointer is authoritative and must
// be committed before this derived projection is invoked. Exact retry verifies
// an existing revision byte-for-byte by deterministic repacking.
[[nodiscard]] Result<SyncTreeActivationResult> materialize_sync_treepack(
    const NamespacePolicy &policy, const ActivatedRevision &revision,
    const std::filesystem::path &artifact,
    const SyncNamespaceTransaction &transaction,
    const SyncTreeProjectionSeams &seams = {});

} // namespace iotox::sync
