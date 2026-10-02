#pragma once

#include "iotox/rollback_witness.hpp"
#include "iotox/security/identity.hpp"
#include "iotox/sync_rollback.hpp"

#include <cstdint>
#include <memory>
#include <mutex>
#include <optional>
#include <string_view>

namespace iotox::sync {

// The first per-namespace freshness slice covers exactly the four roots in
// SyncRollbackHead. Tree-v2 has a different frontier and is deliberately
// refused until that frontier receives its own protocol.
class SyncGuardedStateWitness {
public:
  struct Config {
    std::shared_ptr<rollback_witness::Backend> backend;
    rollback_witness::DomainId domain{};
    std::uint64_t witness_epoch{0U};
    bool allow_non_independent_for_testing{false};
  };

  SyncGuardedStateWitness(Config config, NamespacePolicy policy,
                          const security::DeviceIdentity &identity,
                          const security::Sodium &sodium);

  [[nodiscard]] Status reconcile(
      const NamespacePolicy &policy,
      const SyncNamespaceTransaction &transaction);
  [[nodiscard]] Status verify_read(
      const NamespacePolicy &policy,
      const SyncNamespaceTransaction &transaction);
  [[nodiscard]] Status transition(
      const NamespacePolicy &policy,
      const SyncReachabilityRoots &current,
      const SyncReachabilityRoots &next,
      const SyncNamespaceTransaction &transaction,
      const SyncRootCommit &commit);

  [[nodiscard]] std::string_view namespace_id() const noexcept {
    return policy_.id;
  }
  [[nodiscard]] std::optional<rollback_witness::Head>
  verified_head() const;

private:
  Config config_;
  NamespacePolicy policy_;
  const security::DeviceIdentity *identity_{nullptr};
  const security::Sodium *sodium_{nullptr};
  mutable std::mutex state_mutex_;
  std::optional<rollback_witness::Head> verified_head_;
};

[[nodiscard]] Result<rollback_witness::DomainId>
derive_sync_guarded_witness_domain(
    const rollback_witness::DomainId &base_domain,
    const security::SigningPublicKey &device,
    std::string_view namespace_id,
    const security::Sodium &sodium);

[[nodiscard]] Result<security::Digest> sync_guarded_state_digest(
    const NamespacePolicy &policy, const SyncRollbackHead &head,
    const security::Sodium &sodium);

// Explicit, quiescent enrollment. The service record starts at position one
// even when an existing authenticated four-root head is being anchored.
[[nodiscard]] Result<rollback_witness::Record>
sync_guarded_state_enrollment_record(
    const NamespacePolicy &policy,
    const rollback_witness::DomainId &base_domain,
    std::uint64_t witness_epoch,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction);

} // namespace iotox::sync
