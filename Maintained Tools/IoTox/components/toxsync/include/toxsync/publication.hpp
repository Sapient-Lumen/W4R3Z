#pragma once

#include "toxsync/content_store.hpp"
#include "toxsync/head.hpp"
#include "toxsync/treepack.hpp"

#include <cstdint>
#include <filesystem>
#include <optional>

namespace toxsync {

struct DirectoryPublicationOptions {
    TreePackLimits treepack_limits{};
    PagedContentStoreOptions content_options{};
    bool retain_treepack{false};
    bool retain_root_manifest{false};
    bool fsync_head_on_commit{true};
};

struct DirectoryPublicationRequest {
    std::filesystem::path source_root;
    std::filesystem::path work_root;
    std::filesystem::path store_root;
    std::filesystem::path head_output;
    Digest256 namespace_id{};
    std::uint64_t generation{};
    std::optional<MutableHead> previous;
    Ed25519PrivateKey private_key{};
    bool snapshot{};
};

struct DirectoryPublicationStats {
    MutableHead head{};
    TreePackStats treepack{};
    PagedContentStoreBuildStats content{};
    std::filesystem::path retained_treepack;
    std::filesystem::path retained_root_manifest;
    std::size_t workspace_reserved_bytes{};
};

// Executes the publisher transaction locally: deterministic treepack, paged
// content-addressed storage, linked signed HEAD, then atomic raw-HEAD
// publication. The signed HEAD is not exposed until all named immutable store
// objects have been committed successfully.
[[nodiscard]] DirectoryPublicationStats publish_directory_revision(
    const DirectoryPublicationRequest& request,
    const DirectoryPublicationOptions& options = {});

[[nodiscard]] DirectoryPublicationStats publish_directory_revision(
    const DirectoryPublicationRequest& request,
    ContentStoreWorkspace& workspace,
    const DirectoryPublicationOptions& options = {});

struct TreeActivationOptions {
    TreePackLimits treepack_limits{};
    bool fsync_on_commit{true};
    // A fixed activation receipt allows a restart after the immutable revision
    // rename but before (or just after) the current-symlink switch to finish
    // idempotently. An unrelated pre-existing revision is still rejected.
    bool resume_committed_revision{true};
};

struct TreeActivationStats {
    TreePackStats treepack{};
    std::filesystem::path revision_path;
    std::filesystem::path current_link;
    std::filesystem::path previous_target;
    bool resumed_existing_revision{};
    bool already_active{};
};

// Unpacks into a private sibling staging directory, renames the complete
// revision into an immutable versioned location, and atomically replaces the
// `current` symlink. This is the directory-side counterpart to atomic artifact
// publication. Existing revision names are never trusted or overwritten.
[[nodiscard]] TreeActivationStats activate_treepack_revision(
    const std::filesystem::path& treepack_artifact,
    const std::filesystem::path& activation_root,
    const Digest256& namespace_id,
    std::uint64_t generation,
    const Digest256& head_record,
    const TreeActivationOptions& options = {});

} // namespace toxsync
