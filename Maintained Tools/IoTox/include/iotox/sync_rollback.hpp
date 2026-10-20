#pragma once

#include "iotox/security/identity.hpp"
#include "iotox/sync_reachability.hpp"
#include "iotox/sync_transaction.hpp"

#include <cstdint>
#include <filesystem>
#include <functional>
#include <optional>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace iotox::sync {

class SyncGuardedStateWitness;

struct SyncRollbackRoot {
  std::uint64_t counter{0U};
  Digest record{};

  [[nodiscard]] bool operator==(const SyncRollbackRoot &) const = default;
  [[nodiscard]] bool present() const noexcept { return counter != 0U; }
};

struct SyncRollbackHead {
  SyncRollbackRoot published;
  SyncRollbackRoot accepted;
  SyncRollbackRoot activated;
  SyncRollbackRoot retained;

  [[nodiscard]] bool operator==(const SyncRollbackHead &) const = default;
  [[nodiscard]] bool empty() const noexcept;
};

struct SyncRollbackGuard {
  std::string namespace_id;
  security::SigningPublicKey signer{};
  SyncRollbackHead committed;
  std::optional<SyncRollbackHead> pending;
  security::Signature signature{};

  [[nodiscard]] bool operator==(const SyncRollbackGuard &) const = default;
};

enum class SyncRollbackReconcile : std::uint8_t {
  absent_empty = 1U,
  committed = 2U,
  recovered_before_state_commit = 3U,
  recovered_after_state_commit = 4U,
};

[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_sync_rollback_guard(const SyncRollbackGuard &guard);
[[nodiscard]] Result<SyncRollbackGuard>
decode_sync_rollback_guard(std::span<const std::uint8_t> bytes);
[[nodiscard]] Status verify_sync_rollback_guard(
    const NamespacePolicy &policy, const SyncRollbackGuard &guard,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium);
[[nodiscard]] Result<SyncRollbackHead> make_sync_rollback_head(
    const NamespacePolicy &policy,
    const security::SigningPublicKey &expected_device,
    const SyncReachabilityRoots &roots, const security::Sodium &sodium);
[[nodiscard]] Result<SyncReachabilityRoots> load_sync_rollback_roots(
    const NamespacePolicy &policy,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction);
[[nodiscard]] Status reconcile_sync_rollback_roots(
    const NamespacePolicy &policy,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction);

using SyncRootCommit = std::function<Status()>;

// The caller supplies authenticated current roots, an exact successor, and
// one atomic root-file commit. The guard is reconciled, moved to pending,
// followed by the commit, and then finalized while the transaction is held.
[[nodiscard]] Status guarded_sync_root_transition(
    const NamespacePolicy &policy, const SyncReachabilityRoots &current,
    const SyncReachabilityRoots &next,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction,
    const SyncRootCommit &commit,
    SyncGuardedStateWitness *witness = nullptr);

class SyncRollbackGuardStore {
public:
  explicit SyncRollbackGuardStore(std::filesystem::path root);

  [[nodiscard]] Result<std::optional<SyncRollbackGuard>> load(
      const NamespacePolicy &policy,
      const security::SigningPublicKey &expected_device,
      const security::Sodium &sodium) const;
  [[nodiscard]] Result<SyncRollbackReconcile> check(
      const NamespacePolicy &policy, const SyncRollbackHead &current,
      const security::SigningPublicKey &expected_device,
      const security::Sodium &sodium,
      const SyncNamespaceTransaction &transaction) const;
  [[nodiscard]] Result<SyncRollbackReconcile> reconcile(
      const NamespacePolicy &policy, const SyncRollbackHead &current,
      const security::DeviceIdentity &identity,
      const security::Sodium &sodium,
      const SyncNamespaceTransaction &transaction);
  [[nodiscard]] Status begin(
      const NamespacePolicy &policy, const SyncRollbackHead &current,
      const SyncRollbackHead &next,
      const security::DeviceIdentity &identity,
      const security::Sodium &sodium,
      const SyncNamespaceTransaction &transaction);
  [[nodiscard]] Status finish(
      const NamespacePolicy &policy, const SyncRollbackHead &current,
      const security::DeviceIdentity &identity,
      const security::Sodium &sodium,
      const SyncNamespaceTransaction &transaction);

private:
  [[nodiscard]] std::filesystem::path
  path_for(std::string_view namespace_id) const;

  std::filesystem::path root_;
};

} // namespace iotox::sync
