#pragma once

#include "iotox/rollback_witness.hpp"
#include "iotox/security/identity.hpp"
#include "iotox/sync_multiwriter_maintenance.hpp"
#include "iotox/sync_multiwriter_workspace.hpp"

#include <functional>
#include <memory>
#include <mutex>
#include <optional>
#include <string_view>
#include <vector>

namespace iotox::sync {

// The mutable semantic roots of one tree-v2 namespace. Immutable branch
// records, manifests, and file objects are transitively named by these roots;
// their availability is deliberately not a freshness claim.
struct TreeV2FreshnessState {
  std::vector<TreeV2Observation> frontier;
  TreeV2MaintenanceState maintenance;
  std::optional<TreeV2WorkspaceState> workspace;

  [[nodiscard]] bool operator==(const TreeV2FreshnessState &) const = default;
};

using TreeV2StateTransform =
    std::function<Result<TreeV2FreshnessState>(const TreeV2FreshnessState &)>;
using TreeV2StateCommit = std::function<Status()>;

class TreeV2StateWitness final {
public:
  struct Config {
    std::shared_ptr<rollback_witness::Backend> backend;
    rollback_witness::DomainId domain{};
    std::uint64_t witness_epoch{0U};
    bool allow_non_independent_for_testing{false};
  };

  TreeV2StateWitness(Config config, NamespacePolicy policy,
                     const security::DeviceIdentity &identity,
                     const security::Sodium &sodium);

  [[nodiscard]] Status reconcile(const NamespacePolicy &policy,
                                 const SyncNamespaceTransaction &transaction);
  [[nodiscard]] Status verify_read(const NamespacePolicy &policy,
                                   const SyncNamespaceTransaction &transaction);
  [[nodiscard]] Status transition(const NamespacePolicy &policy,
                                  const SyncNamespaceTransaction &transaction,
                                  const TreeV2StateTransform &transform,
                                  const TreeV2StateCommit &commit);

  [[nodiscard]] std::string_view namespace_id() const noexcept {
    return policy_.id;
  }

private:
  Config config_;
  NamespacePolicy policy_;
  const security::DeviceIdentity *identity_{nullptr};
  const security::Sodium *sodium_{nullptr};
  mutable std::mutex state_mutex_;
  std::optional<rollback_witness::Head> verified_head_;
};

[[nodiscard]] Result<rollback_witness::DomainId>
derive_tree_v2_witness_domain(const rollback_witness::DomainId &base_domain,
                              const security::SigningPublicKey &device,
                              std::string_view namespace_id,
                              const security::Sodium &sodium);

[[nodiscard]] Result<TreeV2FreshnessState>
load_tree_v2_freshness_state(const NamespacePolicy &policy,
                             const security::SigningPublicKey &expected_device,
                             const security::Sodium &sodium,
                             const SyncNamespaceTransaction &transaction);

[[nodiscard]] Result<security::Digest>
tree_v2_freshness_digest(const NamespacePolicy &policy,
                         const TreeV2FreshnessState &state,
                         const security::Sodium &sodium);

[[nodiscard]] Result<rollback_witness::Record> tree_v2_state_enrollment_record(
    const NamespacePolicy &policy,
    const rollback_witness::DomainId &base_domain, std::uint64_t witness_epoch,
    const security::DeviceIdentity &identity, const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction);

} // namespace iotox::sync
