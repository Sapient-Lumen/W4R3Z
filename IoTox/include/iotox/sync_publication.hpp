#pragma once

#include "iotox/security/identity.hpp"
#include "iotox/sync_head.hpp"
#include "iotox/sync_transaction.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <mutex>
#include <memory>
#include <optional>
#include <span>
#include <string_view>

namespace iotox::sync {

class SyncGuardedStateWitness;

inline constexpr std::size_t kSignedHeadBodyBytes = 232U;
inline constexpr std::size_t kSignedHeadBytes =
    kSignedHeadBodyBytes + security::kSignatureBytes;

using SignedHeadBody = std::array<std::uint8_t, kSignedHeadBodyBytes>;
using SignedHeadBytes = std::array<std::uint8_t, kSignedHeadBytes>;

struct SignedHead {
  std::string namespace_id;
  PrincipalId writer{};
  Engine engine{Engine::range_v1};
  std::uint64_t generation{0U};
  Digest parent{};
  Digest artifact{};
  Digest manifest{};
  std::uint64_t artifact_bytes{0U};
  std::uint64_t manifest_bytes{0U};
  security::Signature signature{};

  [[nodiscard]] bool operator==(const SignedHead &) const = default;
};

struct SignedHeadPublicationRequest {
  Digest artifact{};
  Digest manifest{};
  std::uint64_t artifact_bytes{0U};
  std::uint64_t manifest_bytes{0U};
};

struct SignedHeadPublicationResult {
  SignedHead head;
  Digest record{};
  bool genesis{false};
  bool duplicate{false};
};

[[nodiscard]] Result<SignedHeadBody>
encode_signed_head_body(const SignedHead &head);
[[nodiscard]] Result<SignedHeadBytes> encode_signed_head(
    const SignedHead &head);
[[nodiscard]] Result<SignedHead>
decode_signed_head(std::span<const std::uint8_t> bytes);
[[nodiscard]] Status verify_signed_head(const NamespacePolicy &policy,
                                        const SignedHead &head,
                                        const security::Sodium &sodium);
[[nodiscard]] Result<Digest>
signed_head_record_digest(const SignedHead &head,
                          const security::Sodium &sodium);
[[nodiscard]] Result<CandidateHead>
verified_candidate_head(const NamespacePolicy &policy, const SignedHead &head,
                        const security::Sodium &sodium);

// Creates generation one or an exact linked successor. The stable IoTox
// device identity is the sole signer; no toxsync-specific key is introduced.
[[nodiscard]] Result<SignedHead> create_signed_head(
    const NamespacePolicy &policy,
    const SignedHeadPublicationRequest &request,
    const std::optional<SignedHead> &previous,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium);

class SignedHeadStore {
public:
  explicit SignedHeadStore(
      std::filesystem::path root,
      std::shared_ptr<SyncGuardedStateWitness> witness = {});

  [[nodiscard]] Result<std::optional<SignedHead>>
  load(const NamespacePolicy &policy, const security::Sodium &sodium) const;
  [[nodiscard]] Result<std::optional<SignedHead>> load(
      const NamespacePolicy &policy, const security::Sodium &sodium,
      const SyncNamespaceTransaction &transaction) const;
  [[nodiscard]] Result<SignedHeadPublicationResult> publish(
      const NamespacePolicy &policy,
      const SignedHeadPublicationRequest &request,
      const security::DeviceIdentity &identity,
      const security::Sodium &sodium);
  [[nodiscard]] Result<SignedHeadPublicationResult> publish(
      const NamespacePolicy &policy,
      const SignedHeadPublicationRequest &request,
      const security::DeviceIdentity &identity,
      const security::Sodium &sodium,
      const SyncNamespaceTransaction &transaction);

private:
  [[nodiscard]] Result<std::optional<SignedHead>>
  load_unlocked(const NamespacePolicy &policy,
                const security::Sodium &sodium) const;
  [[nodiscard]] std::filesystem::path
  path_for(std::string_view namespace_id) const;

  std::filesystem::path root_;
  std::shared_ptr<SyncGuardedStateWitness> witness_;
  mutable std::mutex mutex_;
};

} // namespace iotox::sync
