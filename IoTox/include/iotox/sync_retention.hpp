#pragma once

#include "iotox/security/identity.hpp"
#include "iotox/sync_head.hpp"
#include "iotox/sync_transaction.hpp"

#include <cstdint>
#include <filesystem>
#include <memory>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace iotox::sync {

class SyncGuardedStateWitness;

struct RetainedRevision {
  std::uint64_t generation{0U};
  Digest record{};
  Digest artifact{};
  Digest manifest{};
  std::uint64_t artifact_bytes{0U};
  std::uint64_t manifest_bytes{0U};

  [[nodiscard]] bool operator==(const RetainedRevision &) const = default;
};

struct RetentionSnapshot {
  std::string namespace_id;
  std::vector<RetainedRevision> revisions;
  security::SigningPublicKey signer{};
  std::uint64_t mutation{0U};
  Digest previous{};
  security::Signature signature{};

  [[nodiscard]] bool operator==(const RetentionSnapshot &) const = default;
};

enum class RetentionUpdate : std::uint8_t {
  inserted = 1U,
  duplicate = 2U,
};

[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_retention_snapshot(const RetentionSnapshot &snapshot);
[[nodiscard]] Result<RetentionSnapshot>
decode_retention_snapshot(std::span<const std::uint8_t> bytes,
                          std::uint64_t maximum_revisions);
[[nodiscard]] Status verify_retention_snapshot(
    const RetentionSnapshot &snapshot,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium);
[[nodiscard]] Result<Digest> retention_snapshot_record_digest(
    const RetentionSnapshot &snapshot, const security::Sodium &sodium);

class RetentionStore {
public:
  explicit RetentionStore(
      std::filesystem::path root,
      std::shared_ptr<SyncGuardedStateWitness> witness = {});

  [[nodiscard]] Result<RetentionSnapshot>
  load(const NamespacePolicy &policy,
       const security::SigningPublicKey &expected_device,
       const security::Sodium &sodium) const;
  [[nodiscard]] Result<RetentionUpdate>
  pin(const NamespacePolicy &policy, const AcceptedHead &head,
      const security::DeviceIdentity &identity,
      const security::Sodium &sodium);
  [[nodiscard]] Result<RetentionUpdate>
  pin(const NamespacePolicy &policy, const AcceptedHead &head,
      const security::DeviceIdentity &identity,
      const security::Sodium &sodium,
      const SyncNamespaceTransaction &transaction);
  [[nodiscard]] Result<bool> unpin(const NamespacePolicy &policy,
                                   const Digest &record,
                                   const security::DeviceIdentity &identity,
                                   const security::Sodium &sodium);
  [[nodiscard]] Result<bool> unpin(
      const NamespacePolicy &policy, const Digest &record,
      const security::DeviceIdentity &identity,
      const security::Sodium &sodium,
      const SyncNamespaceTransaction &transaction);

private:
  [[nodiscard]] std::filesystem::path
  path_for(std::string_view namespace_id) const;

  std::filesystem::path root_;
  std::shared_ptr<SyncGuardedStateWitness> witness_;
};

} // namespace iotox::sync
