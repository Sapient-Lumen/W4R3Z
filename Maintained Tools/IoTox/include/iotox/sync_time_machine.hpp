#pragma once

#include "iotox/security/identity.hpp"
#include "iotox/status.hpp"
#include "iotox/sync_multiwriter.hpp"
#include "iotox/sync_multiwriter_reconcile.hpp"
#include "iotox/sync_transaction.hpp"

#include <cstdint>
#include <filesystem>
#include <memory>
#include <optional>
#include <string>
#include <string_view>
#include <vector>

namespace iotox::sync {

class TreeV2StateWitness;

enum class TreeV2DiffKind : std::uint8_t {
    added = 1U,
    removed = 2U,
    modified = 3U,
};

struct TreeV2Revision {
    Digest record{};
    PrincipalId writer{};
    std::uint64_t generation{0U};
    Digest previous{};
    Digest manifest{};
    std::uint64_t paths{0U};
    std::uint64_t files{0U};
    std::uint64_t conflicts{0U};
    bool checkpoint{false};
    bool current{false};
    bool pinned{false};

    [[nodiscard]] bool operator==(const TreeV2Revision &) const = default;
};

struct TreeV2DiffEntry {
    std::string path;
    TreeV2DiffKind kind{TreeV2DiffKind::modified};
    std::uint64_t from_candidates{0U};
    std::uint64_t to_candidates{0U};
    bool projected_content_changed{false};

    [[nodiscard]] bool operator==(const TreeV2DiffEntry &) const = default;
};

struct TreeV2Diff {
    Digest from_record{};
    Digest to_record{};
    Digest from_manifest{};
    Digest to_manifest{};
    std::vector<TreeV2DiffEntry> entries;
    std::uint64_t added{0U};
    std::uint64_t removed{0U};
    std::uint64_t modified{0U};
    std::uint64_t projected_content_changes{0U};
    std::uint64_t from_conflicts{0U};
    std::uint64_t to_conflicts{0U};
};

struct TreeV2RestorePlan {
    Digest id{};
    Digest target_record{};
    Digest target_manifest{};
    Digest current_manifest{};
    std::uint64_t workspace_generation{0U};
    std::uint64_t next_local_generation{0U};
    std::uint64_t frontier_writers{0U};
    std::uint64_t namespace_writers{0U};
    std::uint64_t pins{0U};
    std::uint64_t cutoffs{0U};
    std::uint64_t target_paths{0U};
    std::uint64_t target_files{0U};
    std::uint64_t target_conflicts{0U};
    std::uint64_t current_conflicts{0U};
    std::uint64_t changed_paths{0U};
    std::uint64_t required_objects{0U};
    std::uint64_t required_bytes{0U};
    std::uint64_t missing_objects{0U};
    std::uint64_t missing_bytes{0U};
    bool target_pinned{false};
    bool workspace_current{false};
    bool worktree_clean{false};
    bool already_current{false};
    bool ready{false};
};

struct TreeV2RestoreForwardResult {
    TreeV2RestorePlan plan;
    TreeV2BranchStoreResult publication;
    TreeV2ReconcileResult reconciliation;
};

[[nodiscard]] std::string_view
tree_v2_diff_kind_name(TreeV2DiffKind kind) noexcept;

// Inventories every live retained immutable record. Ordering is canonical by
// writer, descending writer generation, then record. It is not a wall-clock
// history and it deliberately excludes quarantined objects.
[[nodiscard]] Result<std::vector<TreeV2Revision>> list_tree_v2_history(
    const NamespacePolicy &policy,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction);

// Compares exact candidate sets, including causal provenance. The projected
// content bit separately tells callers whether the ordinary visible value
// changed.
[[nodiscard]] Result<TreeV2Diff> diff_tree_v2_records(
    const NamespacePolicy &policy, const Digest &from_record,
    const Digest &to_record, const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction);

[[nodiscard]] Result<std::vector<TreeV2Conflict>> tree_v2_conflicts(
    const NamespacePolicy &policy, const std::optional<Digest> &record,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction);

// The plan is an optimistic-concurrency token over policy, authenticated
// maintenance state, current frontier, signed workspace generation, target,
// and the clean worktree projection. Planning performs no mutation.
[[nodiscard]] Result<TreeV2RestorePlan> plan_tree_v2_restore_forward(
    const NamespacePolicy &policy, const Digest &target_record,
    const std::filesystem::path &worktree,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction,
    std::shared_ptr<TreeV2StateWitness> witness = {});

// Re-derives and constant-time checks EXPECTED_PLAN, then authors the selected
// historical projection as one new local generation against the exact current
// frontier. It never changes a branch pointer to TARGET_RECORD.
[[nodiscard]] Result<TreeV2RestoreForwardResult> restore_tree_v2_forward(
    const NamespacePolicy &policy, const Digest &target_record,
    const Digest &expected_plan, const std::filesystem::path &worktree,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction,
    std::shared_ptr<TreeV2StateWitness> witness = {});

} // namespace iotox::sync
