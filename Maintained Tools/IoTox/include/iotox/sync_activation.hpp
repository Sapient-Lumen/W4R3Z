#pragma once

#include "iotox/status.hpp"
#include "iotox/sync_head.hpp"
#include "iotox/sync_transaction.hpp"

#include <cstdint>
#include <filesystem>
#include <functional>
#include <memory>
#include <optional>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace iotox::sync {

class SyncGuardedStateWitness;

enum class ActivationDecision : std::uint8_t {
  activated = 1U,
  duplicate = 2U,
  disabled = 3U,
  no_accepted_head = 4U,
  accepted_head_mismatch = 5U,
  stale = 6U,
  fork = 7U,
  object_missing = 8U,
  object_size_mismatch = 9U,
  object_digest_mismatch = 10U,
  manifest_missing = 11U,
  manifest_size_mismatch = 12U,
  manifest_digest_mismatch = 13U,
};

struct ActivatedRevision {
  std::string namespace_id;
  std::uint64_t generation{0U};
  Digest record{};
  Digest artifact{};
  std::uint64_t artifact_bytes{0U};

  [[nodiscard]] bool operator==(const ActivatedRevision &) const = default;
};

struct SyncActivationSeams {
  std::function<Result<Digest>(const std::filesystem::path &path)> hash_file;
  // Optional engine-specific immutable path resolution. Defaults preserve the
  // range-v1/treepack-v1 flat object layout. Resolvers run under the namespace
  // transaction and cannot alter the accepted identities.
  std::function<Result<std::filesystem::path>(
      const NamespacePolicy &policy, const AcceptedHead &accepted)>
      resolve_artifact_path;
  std::function<Result<std::filesystem::path>(
      const NamespacePolicy &policy, const AcceptedHead &accepted)>
      resolve_manifest_path;
  // Called only after both immutable objects have passed exact shape, size,
  // and digest checks while the namespace transaction remains held.
  std::function<Status(const NamespacePolicy &policy,
                       const AcceptedHead &accepted,
                       const std::filesystem::path &artifact,
                       const std::filesystem::path &manifest)>
      validate_revision;
  // Optional derived projection invoked only after the signed activation
  // state is durable, while the same namespace transaction remains held.
  // It is also invoked on exact duplicate retries so an interrupted local
  // projection can be reconciled without changing signed state.
  std::function<Status(const NamespacePolicy &policy,
                       const ActivatedRevision &revision,
                       const std::filesystem::path &artifact,
                       const SyncNamespaceTransaction &transaction)>
      project_revision;
  std::shared_ptr<SyncGuardedStateWitness> guarded_state_witness;
};

struct SyncActivationRequest {
  NamespacePolicy policy;
  // This optimistic-concurrency token prevents an operator command prepared
  // for one accepted HEAD from activating a newer record by accident.
  Digest expected_record{};
};

struct SyncActivationResult {
  ActivationDecision decision{ActivationDecision::disabled};
  std::optional<ActivatedRevision> revision;
  std::filesystem::path object_path;

  [[nodiscard]] bool active() const noexcept;
};

[[nodiscard]] std::string_view
activation_decision_name(ActivationDecision decision) noexcept;
[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_activated_revision(const ActivatedRevision &revision);
[[nodiscard]] Result<ActivatedRevision>
decode_activated_revision(std::span<const std::uint8_t> bytes);

class ActivatedRevisionStore {
public:
  explicit ActivatedRevisionStore(
      std::filesystem::path root,
      std::shared_ptr<SyncGuardedStateWitness> witness = {});

  [[nodiscard]] Result<std::optional<ActivatedRevision>>
  load(const NamespacePolicy &policy,
       const security::SigningPublicKey &expected_device,
       const security::Sodium &sodium) const;
  [[nodiscard]] Status store(const NamespacePolicy &policy,
                             const ActivatedRevision &revision,
                             const security::DeviceIdentity &identity,
                             const security::Sodium &sodium);
  [[nodiscard]] Status store(
      const NamespacePolicy &policy, const ActivatedRevision &revision,
      const security::DeviceIdentity &identity,
      const security::Sodium &sodium,
      const SyncNamespaceTransaction &transaction);

private:
  [[nodiscard]] std::filesystem::path
  path_for(std::string_view namespace_id) const;

  std::filesystem::path root_;
  std::shared_ptr<SyncGuardedStateWitness> witness_;
};

// Activates only the exact currently accepted HEAD. The immutable object and
// its manifest are rechecked immediately before the activation pointer is
// atomically replaced. The operation acquires the transaction shared with
// accepted-HEAD updates and signs the activation pointer before replacement.
[[nodiscard]] Result<SyncActivationResult>
activate_staged_artifact(const SyncActivationRequest &request,
                         const security::DeviceIdentity &identity,
                         const security::Sodium &sodium,
                         const SyncActivationSeams &seams);

} // namespace iotox::sync
