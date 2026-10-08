#pragma once

#include <cstdint>
#include <string>
#include <string_view>
#include <vector>

namespace anonsync {

// Selective synchronization is intentionally a bounded prefix policy rather
// than one durable row per path. A multi-terabyte namespace may contain millions
// of files, while a human selection normally names a comparatively small set of
// directory/file prefixes. The complete canonical policy fits in one bounded
// reconciliation request and one folder-catalog authority record.
inline constexpr std::uint64_t kSyncReplicaSelectiveSyncMaximumRules = 1024U;
inline constexpr std::uint64_t kSyncReplicaSelectiveSyncMaximumRulePathBytes =
    48ULL * 1024ULL;

// Materialize means retain operation metadata, obtain exact payload bytes, and
// publish the visible value beneath the rooted folder. MetadataOnly means retain
// causal metadata but neither request nor publish file payload bytes. Tombstones
// remain metadata and are always eligible for ordinary absence convergence.
enum class SyncReplicaSelectiveSyncMode : std::uint8_t {
    Materialize = 1U,
    MetadataOnly = 2U,
};

[[nodiscard]] constexpr std::string_view sync_replica_selective_sync_mode_name(
    SyncReplicaSelectiveSyncMode mode) noexcept {
    switch (mode) {
        case SyncReplicaSelectiveSyncMode::Materialize:
            return "materialize";
        case SyncReplicaSelectiveSyncMode::MetadataOnly:
            return "metadata_only";
    }
    return "unknown";
}

[[nodiscard]] SyncReplicaSelectiveSyncMode
sync_replica_selective_sync_mode_from_name_or_throw(std::string_view name);

struct SyncReplicaSelectiveSyncRule final {
    std::string canonical_path;
    SyncReplicaSelectiveSyncMode mode =
        SyncReplicaSelectiveSyncMode::Materialize;

    bool operator==(const SyncReplicaSelectiveSyncRule&) const = default;
};

struct SyncReplicaSelectiveSyncPolicy final {
    std::uint64_t generation = 1U;
    SyncReplicaSelectiveSyncMode default_mode =
        SyncReplicaSelectiveSyncMode::Materialize;
    // Strict canonical-path order, unique by path.
    std::vector<SyncReplicaSelectiveSyncRule> rules;
    std::uint64_t rule_path_bytes = 0U;
    std::string policy_digest;

    bool operator==(const SyncReplicaSelectiveSyncPolicy&) const = default;
};

// Builds and validates one canonical policy. Input rules may be unsorted, but
// duplicate paths are rejected rather than silently resolving contradictory
// operator intent. Generation is durable local policy history and must be
// positive. The resulting digest commits to generation, default, and every rule.
[[nodiscard]] SyncReplicaSelectiveSyncPolicy
make_sync_replica_selective_sync_policy_or_throw(
    SyncReplicaSelectiveSyncMode default_mode,
    std::vector<SyncReplicaSelectiveSyncRule> rules,
    std::uint64_t generation = 1U);

[[nodiscard]] SyncReplicaSelectiveSyncPolicy
sync_replica_default_selective_sync_policy();

void validate_sync_replica_selective_sync_policy_or_throw(
    const SyncReplicaSelectiveSyncPolicy& policy,
    std::string_view label = "sync replica selective-sync policy");

// Semantic equality intentionally ignores durable generation and digest. It is
// used to make an operator replay idempotent instead of advancing state for an
// unchanged selection.
[[nodiscard]] bool sync_replica_selective_sync_policy_semantically_equal(
    const SyncReplicaSelectiveSyncPolicy& left,
    const SyncReplicaSelectiveSyncPolicy& right) noexcept;

// True exactly when at least one canonical path is MetadataOnly under before
// and Materialize under after. Longest-prefix policy semantics change only at
// the default region or a rule path from either policy, so this bounded check
// never enumerates the catalog or synchronized tree.
[[nodiscard]] bool
sync_replica_selective_sync_policy_materializes_new_paths(
    const SyncReplicaSelectiveSyncPolicy& before,
    const SyncReplicaSelectiveSyncPolicy& after);

// Longest matching canonical component prefix wins; the default applies when
// no rule names the path or any ancestor. Both functions allocate no memory.
[[nodiscard]] SyncReplicaSelectiveSyncMode
sync_replica_selective_sync_mode_for_path(
    const SyncReplicaSelectiveSyncPolicy& policy,
    std::string_view canonical_path);

[[nodiscard]] bool sync_replica_selective_sync_path_is_materialized(
    const SyncReplicaSelectiveSyncPolicy& policy,
    std::string_view canonical_path);

// True when walking this directory can discover at least one materialized file.
// Empty canonical_directory names the configured root. A metadata-only subtree
// with no deeper materialize rule may be pruned without enumerating its children.
// The lookup allocates no memory.
[[nodiscard]] bool
sync_replica_selective_sync_directory_may_contain_materialized_path(
    const SyncReplicaSelectiveSyncPolicy& policy,
    std::string_view canonical_directory);

}  // namespace anonsync
