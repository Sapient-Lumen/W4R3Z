#pragma once

#include "iotox/security/identity.hpp"
#include "iotox/sync_publication.hpp"
#include "iotox/sync_transaction.hpp"

#include <cstdint>
#include <filesystem>
#include <optional>
#include <span>
#include <string_view>
#include <vector>

namespace iotox::sync {

// A replica is an owner-admitted availability cache for an exact foreign-
// writer signed HEAD. It is deliberately neither local publication nor
// accepted/activated revision authority.
struct ReplicaHead {
  security::SigningPublicKey custodian{};
  SignedHead head;
  security::Signature signature{};

  [[nodiscard]] bool operator==(const ReplicaHead &) const = default;
};

enum class ReplicaHeadImportDecision : std::uint8_t {
  imported = 1U,
  advanced = 2U,
  duplicate = 3U,
};

struct ReplicaHeadImportResult {
  ReplicaHeadImportDecision decision{ReplicaHeadImportDecision::imported};
  Digest record{};
};

[[nodiscard]] std::string_view
replica_head_import_decision_name(ReplicaHeadImportDecision decision) noexcept;
[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_replica_head(const ReplicaHead &replica);
[[nodiscard]] Result<ReplicaHead>
decode_replica_head(std::span<const std::uint8_t> bytes);
[[nodiscard]] Status
verify_replica_head(const NamespacePolicy &policy, const ReplicaHead &replica,
                    const security::SigningPublicKey &expected_device,
                    const security::Sodium &sodium);

class ReplicaHeadStore final {
public:
  explicit ReplicaHeadStore(std::filesystem::path root);

  [[nodiscard]] Result<std::optional<SignedHead>>
  load(const NamespacePolicy &policy,
       const security::SigningPublicKey &expected_device,
       const security::Sodium &sodium) const;
  [[nodiscard]] Result<ReplicaHeadImportResult>
  import_head(const NamespacePolicy &policy, const SignedHead &head,
              const security::DeviceIdentity &identity,
              const security::Sodium &sodium);
  [[nodiscard]] Result<ReplicaHeadImportResult>
  import_head(const NamespacePolicy &policy, const SignedHead &head,
              const security::DeviceIdentity &identity,
              const security::Sodium &sodium,
              const SyncNamespaceTransaction &transaction);

private:
  [[nodiscard]] std::filesystem::path
  path_for(std::string_view namespace_id) const;

  std::filesystem::path root_;
};

} // namespace iotox::sync
