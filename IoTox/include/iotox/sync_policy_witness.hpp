#pragma once

#include "iotox/security/sodium.hpp"
#include "iotox/status.hpp"
#include "iotox/sync_automation.hpp"
#include "iotox/sync_namespace.hpp"

#include <cstdint>
#include <filesystem>
#include <vector>

namespace iotox::sync {

// One strictly loaded, canonical snapshot of every owner-local policy that
// can grant namespace membership or schedule a filesystem effect.
struct SyncPolicyTree {
  std::vector<NamespacePolicy> namespaces;
  std::vector<SyncAutomationPolicy> automations;

  [[nodiscard]] bool operator==(const SyncPolicyTree &) const = default;
};

[[nodiscard]] Result<SyncPolicyTree> load_sync_policy_tree(
    const std::filesystem::path &policy_root,
    std::uint32_t expected_owner_uid,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium);

// Canonical, length-bound commitment over the exact namespace and signed
// automation records. Runtime data, content, and namespace rollback guards
// are deliberately separate witness lanes.
[[nodiscard]] Result<security::Digest> sync_policy_tree_digest(
    const SyncPolicyTree &tree, const security::Sodium &sodium);

}  // namespace iotox::sync
