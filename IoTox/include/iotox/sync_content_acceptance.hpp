#pragma once

#include "iotox/security/identity.hpp"
#include "iotox/sync_content.hpp"

#include <cstddef>
#include <functional>
#include <memory>

namespace iotox::sync {

class SyncGuardedStateWitness;

struct SyncContentAcceptanceConfig {
  std::size_t io_buffer_bytes{256U * 1024U};
  bool fsync_on_commit{true};
};

struct SyncContentAcceptanceSeams {
  std::function<bool()> cancel_requested;
  std::shared_ptr<SyncGuardedStateWitness> guarded_state_witness;
};

struct SyncContentAcceptanceResult {
  HeadAcceptanceResult acceptance;
  SyncContentReconstruction reconstruction;
  SyncContentCommitResult artifact_commit;
  bool reconstructed{false};
};

[[nodiscard]] Result<std::size_t> cleanup_sync_content_reconstruction_staging(
    const NamespacePolicy &policy, const SyncNamespaceTransaction &transaction);

// Reconstructs a complete coordinator into private staging, commits the whole
// verified artifact into CAS, rechecks the root manifest, and accepts the
// signed HEAD last. Existing exact artifact CAS permits an idempotent retry
// without reconstructing again. This does not activate the revision.
[[nodiscard]] Result<SyncContentAcceptanceResult>
reconstruct_and_accept_sync_content_revision(
    const NamespacePolicy &policy, const SignedHead &head,
    SyncContentCoordinator &coordinator,
    const security::DeviceIdentity &identity, const security::Sodium &sodium,
    SyncContentAcceptanceConfig config = {},
    SyncContentAcceptanceSeams seams = {});

} // namespace iotox::sync
