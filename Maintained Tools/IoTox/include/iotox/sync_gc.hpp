#pragma once

#include "iotox/status.hpp"
#include "iotox/sync_reachability.hpp"
#include "iotox/sync_transaction.hpp"

#include <cstddef>
#include <cstdint>
#include <functional>
#include <memory>
#include <optional>
#include <vector>

namespace iotox::sync {

class SyncGuardedStateWitness;

// Filesystem identity frozen by the dry-run planner. Paths are deliberately
// absent: every name is reconstructed from the validated object identity.
struct SyncGcObjectIdentity {
  SyncObjectRecord object;
  std::uint64_t device{0U};
  std::uint64_t inode{0U};
  std::uint64_t owner{0U};
  std::uint64_t group{0U};
  std::uint64_t links{0U};
  std::uint32_t mode{0U};

  [[nodiscard]] bool operator==(const SyncGcObjectIdentity &) const = default;
};

struct SyncGcPlan {
  SyncReachabilityPlan reachability;
  std::vector<SyncGcObjectIdentity> inventory;
  std::vector<SyncGcObjectIdentity> candidates;
  std::uint64_t root_device{0U};
  std::uint64_t root_inode{0U};
  std::uint64_t objects_device{0U};
  std::uint64_t objects_inode{0U};
  bool objects_present{false};
  bool descriptor_pinned{false};
};

struct SyncGcSeams {
  std::function<bool()> cancel_requested;
  // Test-only adversarial boundary, invoked immediately before the candidate
  // is reopened and compared with its frozen identity.
  std::function<Status(std::size_t, const SyncGcObjectIdentity &)> before_move;
  // Defaults to fsync(2). A seam makes post-rename failure accounting
  // deterministic without weakening the production behavior.
  std::function<Status(int)> sync_directory;
};

struct SyncGcQuarantineOutcome {
  Status status;
  std::optional<SyncGcPlan> plan;
  std::vector<SyncObjectRecord> moved;
  std::uint64_t moved_bytes{0U};
  std::uint64_t durable_objects{0U};
  std::uint64_t durable_bytes{0U};
  bool quarantine_created{false};
  bool cancelled{false};

  [[nodiscard]] bool ok() const noexcept { return status.ok(); }
};

// Evidence only. Acquires the namespace transaction, authenticates all live
// roots and the rollback guard, and freezes a descriptor-relative inventory.
[[nodiscard]] Result<SyncGcPlan>
plan_sync_gc_quarantine(const NamespacePolicy &policy,
                        const security::SigningPublicKey &expected_device,
                        const security::Sodium &sodium,
                        std::shared_ptr<SyncGuardedStateWitness> witness = {});

// Recomputes the plan under one transaction and moves only exact unreferenced
// identities into root/gc-quarantine. There is no purge or unlink path. The
// outcome always preserves exact partial-move and durability accounting.
[[nodiscard]] SyncGcQuarantineOutcome quarantine_unreferenced_sync_objects(
    const NamespacePolicy &policy,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium, const SyncGcSeams &seams = {},
    std::shared_ptr<SyncGuardedStateWitness> witness = {});

} // namespace iotox::sync
