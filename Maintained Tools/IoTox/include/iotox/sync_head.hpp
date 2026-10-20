#pragma once

#include "iotox/security/identity.hpp"
#include "iotox/sync_namespace.hpp"
#include "iotox/sync_transaction.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <memory>
#include <optional>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace iotox::sync {

class SyncGuardedStateWitness;

using Digest = std::array<std::uint8_t, 32U>;

enum class HeadAcceptanceDecision : std::uint8_t {
  accept_genesis = 1U,
  accept_advance = 2U,
  duplicate = 3U,
  stale = 4U,
  fork = 5U,
  wrong_namespace = 6U,
  unauthorized_writer = 7U,
  parent_mismatch = 8U,
  generation_gap = 9U,
  engine_mismatch = 10U,
  resource_limit = 11U,
};

struct AcceptedHead {
  std::string namespace_id;
  PrincipalId writer{};
  Engine engine{Engine::range_v1};
  std::uint64_t generation{0U};
  Digest record{};
  Digest parent{};
  Digest artifact{};
  Digest manifest{};
  std::uint64_t artifact_bytes{0U};
  std::uint64_t manifest_bytes{0U};

  [[nodiscard]] bool operator==(const AcceptedHead &) const = default;
};

struct CandidateHead {
  std::string namespace_id;
  PrincipalId writer{};
  Engine engine{Engine::range_v1};
  std::uint64_t generation{0U};
  Digest record{};
  Digest parent{};
  Digest artifact{};
  Digest manifest{};
  std::uint64_t artifact_bytes{0U};
  std::uint64_t manifest_bytes{0U};
};

struct HeadAcceptancePolicy {
  std::uint64_t maximum_generation_jump{1024U};
};

struct HeadAcceptanceResult {
  HeadAcceptanceDecision decision{HeadAcceptanceDecision::resource_limit};
  std::uint64_t generation_delta{0U};

  [[nodiscard]] bool accepted() const noexcept;
};

[[nodiscard]] std::string_view
head_acceptance_decision_name(HeadAcceptanceDecision decision) noexcept;

[[nodiscard]] Status validate_accepted_head(const NamespacePolicy &policy,
                                            const AcceptedHead &head);
[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_accepted_head(const AcceptedHead &head);
[[nodiscard]] Result<AcceptedHead>
decode_accepted_head(std::span<const std::uint8_t> bytes);

[[nodiscard]] HeadAcceptanceResult
evaluate_candidate_head(const NamespacePolicy &policy,
                        const CandidateHead &candidate,
                        const std::optional<AcceptedHead> &current,
                        const HeadAcceptancePolicy &acceptance = {});

class AcceptedHeadStore {
public:
  explicit AcceptedHeadStore(
      std::filesystem::path root,
      std::shared_ptr<SyncGuardedStateWitness> witness = {});

  [[nodiscard]] Result<std::optional<AcceptedHead>>
  load(const NamespacePolicy &policy,
       const security::SigningPublicKey &expected_device,
       const security::Sodium &sodium) const;
  [[nodiscard]] Result<HeadAcceptanceResult>
  accept(const NamespacePolicy &policy, const CandidateHead &candidate,
         const security::DeviceIdentity &identity,
         const security::Sodium &sodium,
         const HeadAcceptancePolicy &acceptance = {});
  [[nodiscard]] Result<HeadAcceptanceResult>
  accept(const NamespacePolicy &policy, const CandidateHead &candidate,
         const security::DeviceIdentity &identity,
         const security::Sodium &sodium,
         const HeadAcceptancePolicy &acceptance,
         const SyncNamespaceTransaction &transaction);

private:
  [[nodiscard]] std::filesystem::path
  path_for(std::string_view namespace_id) const;

  std::filesystem::path root_;
  std::shared_ptr<SyncGuardedStateWitness> witness_;
};

} // namespace iotox::sync
