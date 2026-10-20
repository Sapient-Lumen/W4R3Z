#pragma once

#include "iotox/security/identity.hpp"
#include "iotox/status.hpp"
#include "iotox/sync_head.hpp"
#include "iotox/sync_namespace.hpp"

#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace iotox::sync {

inline constexpr std::uint8_t kTreeV2ManifestVersion = 1U;
inline constexpr std::uint8_t kTreeV2OwnerModeManifestVersion = 2U;
inline constexpr std::uint8_t kTreeV2BranchVersion = 1U;
inline constexpr std::uint8_t kTreeV2CheckpointBranchVersion = 2U;
inline constexpr std::size_t kTreeV2MaximumPathBytes = 4096U;
inline constexpr std::size_t kTreeV2MaximumValuesPerPath = 16U;
inline constexpr std::string_view kTreeV2ConflictRoot = ".iotox-conflicts";

enum class TreeV2EntryKind : std::uint8_t {
    directory = 1U,
    file = 2U,
    tombstone = 3U,
};

struct TreeV2Version {
    PrincipalId writer{};
    std::uint64_t generation{0U};

    [[nodiscard]] bool operator==(const TreeV2Version &) const = default;
};

// A manifest can retain more than one value for a path. Multiple values are
// unresolved concurrent edits, not duplicate paths and not an ordering error.
// One writer/generation may contribute at most one value to a path.
struct TreeV2Entry {
    std::string path;
    TreeV2EntryKind kind{TreeV2EntryKind::file};
    TreeV2Version origin;
    Digest content{};
    std::uint64_t content_bytes{0U};
    bool executable{false};
    // Zero retains the manifest-v1 executable-bit representation. Values 4
    // through 7 carry exact owner r/w/x permissions in manifest v2. Group,
    // other, special, directory, and tombstone mode bits are never carried.
    std::uint8_t owner_mode{0U};

    [[nodiscard]] bool operator==(const TreeV2Entry &other) const noexcept;
};

struct TreeV2Manifest {
    std::vector<TreeV2Entry> entries;

    [[nodiscard]] bool operator==(const TreeV2Manifest &) const = default;
};

// This is a signed vector-clock observation, not a merge-policy assertion.
// RECORD binds the exact observed branch HEAD at GENERATION.
struct TreeV2Observation {
    PrincipalId writer{};
    std::uint64_t generation{0U};
    Digest record{};

    [[nodiscard]] bool operator==(const TreeV2Observation &) const = default;
};

struct TreeV2BranchHead {
    std::string namespace_id;
    PrincipalId writer{};
    std::uint64_t generation{0U};
    Digest previous{};
    Digest manifest{};
    std::uint64_t manifest_bytes{0U};
    std::vector<TreeV2Observation> observations;
    // A checkpoint is a signed causal snapshot and graph traversal floor.
    // Every manifest value belongs to this writer at GENERATION, so no
    // unverifiable foreign provenance is inherited across the floor.
    bool checkpoint{false};
    security::Signature signature{};

    [[nodiscard]] bool operator==(const TreeV2BranchHead &) const = default;
};

struct TreeV2Snapshot {
    TreeV2BranchHead head;
    TreeV2Manifest manifest;

    [[nodiscard]] bool operator==(const TreeV2Snapshot &) const = default;
};

struct TreeV2Conflict {
    std::string path;
    std::vector<TreeV2Entry> candidates;

    [[nodiscard]] bool operator==(const TreeV2Conflict &) const = default;
};

struct TreeV2MergeResult {
    TreeV2Manifest manifest;
    std::vector<TreeV2Conflict> conflicts;
    std::uint64_t paths{0U};
    std::uint64_t live_files{0U};
    std::uint64_t live_directories{0U};
    std::uint64_t tombstoned_paths{0U};

    [[nodiscard]] bool operator==(const TreeV2MergeResult &) const = default;
};

[[nodiscard]] std::string_view
tree_v2_entry_kind_name(TreeV2EntryKind kind) noexcept;
[[nodiscard]] bool valid_tree_v2_path(std::string_view path) noexcept;
[[nodiscard]] Status validate_tree_v2_manifest(const NamespacePolicy &policy,
                                               const TreeV2Manifest &manifest);
[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_tree_v2_manifest(const NamespacePolicy &policy,
                        const TreeV2Manifest &manifest);
[[nodiscard]] Result<TreeV2Manifest>
decode_tree_v2_manifest(const NamespacePolicy &policy,
                        std::span<const std::uint8_t> bytes);
[[nodiscard]] Result<Digest>
tree_v2_manifest_digest(const NamespacePolicy &policy,
                        const TreeV2Manifest &manifest,
                        const security::Sodium &sodium);

[[nodiscard]] Status validate_tree_v2_branch_head(const NamespacePolicy &policy,
                                                  const TreeV2BranchHead &head);
[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_tree_v2_branch_body(const NamespacePolicy &policy,
                           const TreeV2BranchHead &head);
[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_tree_v2_branch_head(const NamespacePolicy &policy,
                           const TreeV2BranchHead &head);
[[nodiscard]] Result<TreeV2BranchHead>
decode_tree_v2_branch_head(const NamespacePolicy &policy,
                           std::span<const std::uint8_t> bytes);
[[nodiscard]] Status verify_tree_v2_branch_head(const NamespacePolicy &policy,
                                                const TreeV2BranchHead &head,
                                                const security::Sodium &sodium);
[[nodiscard]] Result<Digest>
tree_v2_branch_record_digest(const NamespacePolicy &policy,
                             const TreeV2BranchHead &head,
                             const security::Sodium &sodium);

// PREVIOUS is this writer's exact current branch. OBSERVATIONS is the
// complete other-writer frontier known at creation. The function installs the
// exact predecessor observation, sorts the frontier, and refuses duplicates.
[[nodiscard]] Result<TreeV2BranchHead> create_tree_v2_branch_head(
    const NamespacePolicy &policy, const TreeV2Manifest &manifest,
    const std::optional<TreeV2BranchHead> &previous,
    std::span<const TreeV2Observation> observations,
    const security::DeviceIdentity &identity, const security::Sodium &sodium);

// Creates an explicit graph floor from a complete conflict-free frontier.
// Unresolved conflicts are refused rather than projected away.
[[nodiscard]] Result<TreeV2Snapshot> create_tree_v2_checkpoint(
    const NamespacePolicy &policy,
    std::span<const TreeV2Snapshot> frontier,
    const security::DeviceIdentity &identity, const security::Sodium &sodium);

[[nodiscard]] Status verify_tree_v2_snapshot(const NamespacePolicy &policy,
                                             const TreeV2Snapshot &snapshot,
                                             const security::Sodium &sodium);
[[nodiscard]] bool tree_v2_head_observes(const TreeV2BranchHead &head,
                                         const TreeV2Version &version) noexcept;

// Merges one exact branch frontier. A value disappears only when a branch
// cryptographically observes its origin and omits it while retaining another
// value for that path. Concurrent values remain side by side. Equivalent
// payloads coalesce deterministically without creating a conflict.
[[nodiscard]] Result<TreeV2MergeResult>
merge_tree_v2_snapshots(const NamespacePolicy &policy,
                        std::span<const TreeV2Snapshot> snapshots,
                        const security::Sodium &sodium);

// Reconstructs deterministic projection/conflict counters from an already
// validated merged manifest. It does not perform causality or dominance.
[[nodiscard]] Result<TreeV2MergeResult>
summarize_tree_v2_manifest(const NamespacePolicy &policy,
                           const TreeV2Manifest &manifest);

// Selects the deterministic ordinary projection value for one path. Every
// unselected concurrent value still belongs in provenance-bearing conflict
// material. Live values beat a concurrent tombstone; directories beat files
// so descendants cannot be silently hidden by a file/directory conflict.
[[nodiscard]] Result<TreeV2Entry>
select_tree_v2_projection_entry(std::span<const TreeV2Entry> candidates);

} // namespace iotox::sync
