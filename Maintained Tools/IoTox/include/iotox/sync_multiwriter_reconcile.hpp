#pragma once

#include "iotox/security/identity.hpp"
#include "iotox/status.hpp"
#include "iotox/sync_multiwriter_store.hpp"
#include "iotox/sync_multiwriter_workspace.hpp"
#include "iotox/sync_multiwriter_worktree.hpp"

#include <cstdint>
#include <filesystem>
#include <memory>

namespace iotox::sync {

class TreeV2StateWitness;

struct TreeV2ReconcileResult {
    TreeV2BranchStoreDecision publication{TreeV2BranchStoreDecision::duplicate};
    std::uint64_t local_events{0U};
    std::uint64_t source_inspected_entries{0U};
    std::uint64_t source_hashed_file_digests{0U};
    std::uint64_t source_reused_file_digests{0U};
    std::uint64_t cas_inspected_objects{0U};
    std::uint64_t cas_inspected_bytes{0U};
    std::uint64_t cas_installed_objects{0U};
    std::uint64_t cas_installed_bytes{0U};
    std::uint64_t cas_reused_objects{0U};
    std::uint64_t projection_directories{0U};
    std::uint64_t projection_files{0U};
    std::uint64_t projection_bytes{0U};
    std::uint64_t projection_conflict_files{0U};
    std::uint64_t projection_conflict_tombstones{0U};
    std::uint64_t projection_preserved_unselected_entries{0U};
    std::uint64_t projection_preserved_unselected_directories{0U};
    std::uint64_t projection_preserved_unselected_files{0U};
    std::uint64_t projection_preserved_unselected_bytes{0U};
    std::uint64_t branch_advances{0U};
    std::uint64_t frontier_writers{0U};
    std::uint64_t conflicts{0U};
    std::uint64_t files{0U};
    std::uint64_t tombstoned_paths{0U};
    bool local_changed{false};
    bool workspace_initialized{false};
    bool workspace_exchanged{false};
    bool recovered_pending_exchange{false};

    [[nodiscard]] bool
    operator==(const TreeV2ReconcileResult &) const = default;
};

struct TreeV2CheckpointResult {
    TreeV2ReconcileResult before;
    TreeV2ReconcileResult after;
    TreeV2BranchStoreResult checkpoint;

    [[nodiscard]] bool operator==(const TreeV2CheckpointResult &) const =
        default;
};

// One bounded local reconciliation cycle. The signed workspace frontier—not
// newly received daemon knowledge—defines the causal past of filesystem edits.
// CAS commits precede the local branch; a signed pending workspace checkpoint
// precedes any whole-directory exchange.
[[nodiscard]] Result<TreeV2ReconcileResult> reconcile_tree_v2_workspace(
    const NamespacePolicy &policy, const std::filesystem::path &worktree,
    const security::DeviceIdentity &identity, const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction,
    std::shared_ptr<TreeV2StateWitness> witness = {},
    TreeV2SourceDigestCache *source_digest_cache = nullptr);

// Reconciles local edits, refuses unresolved conflicts, commits one explicit
// v2 graph floor, then advances the signed workspace marker to that floor.
// Re-entry repairs a crash after the branch commit but before the marker.
[[nodiscard]] Result<TreeV2CheckpointResult> checkpoint_tree_v2_workspace(
    const NamespacePolicy &policy, const std::filesystem::path &worktree,
    const security::DeviceIdentity &identity, const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction,
    std::shared_ptr<TreeV2StateWitness> witness = {});

} // namespace iotox::sync
