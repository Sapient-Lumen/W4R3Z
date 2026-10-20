#pragma once

#include "iotox/sync_activation.hpp"
#include "iotox/sync_job.hpp"
#include "iotox/sync_retention.hpp"

#include <cstdint>
#include <memory>
#include <optional>
#include <vector>

namespace iotox::sync {

class SyncGuardedStateWitness;

enum class SyncRootSource : std::uint8_t {
  published = 1U << 0U,
  accepted = 1U << 1U,
  activated = 1U << 2U,
  retained = 1U << 3U,
};

struct SyncRootedObject {
  SyncObjectRecord object;
  std::uint8_t source_mask{0U};

  [[nodiscard]] bool operator==(const SyncRootedObject &) const = default;
};

struct SyncObjectMismatch {
  SyncRootedObject expected;
  std::uint64_t observed_bytes{0U};

  [[nodiscard]] bool operator==(const SyncObjectMismatch &) const = default;
};

struct SyncReachabilityRoots {
  std::optional<SignedHead> published;
  std::optional<AcceptedHead> accepted;
  std::optional<ActivatedRevision> activated;
  RetentionSnapshot retained;
};

struct SyncReachabilityPlan {
  std::vector<SyncRootedObject> rooted;
  std::vector<SyncRootedObject> missing;
  std::vector<SyncObjectMismatch> mismatched;
  std::vector<SyncObjectRecord> unreferenced;
  std::uint64_t rooted_bytes{0U};
  std::uint64_t unreferenced_bytes{0U};
  bool retention_authenticated{false};
  bool transaction_stable{false};
  bool rollback_guard_consistent{false};

  [[nodiscard]] bool consistent() const noexcept {
    return missing.empty() && mismatched.empty();
  }
};

// Produces evidence only. Even a complete plan is not deletion authority: a
// complete matching guard-plus-root snapshot remains replayable.
[[nodiscard]] Result<SyncReachabilityPlan> plan_sync_reachability(
    const NamespacePolicy &policy,
    const security::SigningPublicKey &expected_device,
    const SyncReachabilityRoots &roots,
    std::vector<SyncObjectRecord> inventory,
    const security::Sodium &sodium);

// Acquires the namespace transaction once, loads every current persisted root,
// inventories the object store under that same token, and invokes the pure
// planner, and checks the signed rollback guard against that same root set.
// The result remains non-destructive for the rollback reason above.
[[nodiscard]] Result<SyncReachabilityPlan> plan_sync_reachability_from_store(
    const NamespacePolicy &policy,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium,
    std::shared_ptr<SyncGuardedStateWitness> witness = {});

// Reuses one already-held namespace transaction and one strict caller-captured
// inventory. This is the maintenance boundary used by descriptor-pinned GC:
// the caller owns filesystem identity checks while this function authenticates
// every persisted root and the monotonic rollback guard under the same lock.
[[nodiscard]] Result<SyncReachabilityPlan>
plan_sync_reachability_in_transaction(
    const NamespacePolicy &policy,
    const security::SigningPublicKey &expected_device,
    std::vector<SyncObjectRecord> inventory, const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction,
    std::shared_ptr<SyncGuardedStateWitness> witness = {});

} // namespace iotox::sync
