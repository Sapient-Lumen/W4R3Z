#pragma once

#include "iotox/sync_namespace.hpp"
#include "iotox/sync_transaction.hpp"

#include <cstddef>
#include <cstdint>
#include <filesystem>

namespace iotox::sync {

enum class SyncContentWorkspaceClass : std::uint8_t {
  publication = 1U,
  reconstruction = 2U,
};

// Allocates one exact mode-0700 same-filesystem local workspace beneath the
// content staging root. The namespace transaction excludes cleanup and other
// cooperating local mutations while the workspace is live.
[[nodiscard]] Result<std::filesystem::path>
create_sync_content_workspace(const NamespacePolicy &policy,
                              const SyncNamespaceTransaction &transaction,
                              SyncContentWorkspaceClass workspace_class);

// Removes one exact workspace after revalidating its class, name, ownership,
// mode, and filesystem. Absence is idempotent; no caller-selected tree is
// accepted.
[[nodiscard]] Status
remove_sync_content_workspace(const NamespacePolicy &policy,
                              const SyncNamespaceTransaction &transaction,
                              SyncContentWorkspaceClass workspace_class,
                              const std::filesystem::path &workspace);

// Startup recovery removes only exact local-<16 lowercase hex> directories
// for the requested class and refuses any foreign or unsafe entry.
[[nodiscard]] Result<std::size_t>
cleanup_sync_content_workspaces(const NamespacePolicy &policy,
                                const SyncNamespaceTransaction &transaction,
                                SyncContentWorkspaceClass workspace_class);

} // namespace iotox::sync
