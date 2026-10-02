#pragma once

#include "iotox/security/authority.hpp"
#include "iotox/security/authority_session.hpp"
#include "iotox/sync_head.hpp"
#include "iotox/sync_namespace.hpp"

#include <cstdint>
#include <string_view>

namespace iotox::sync {

enum class SyncOperation : std::uint8_t {
  administer = 1U,
  publish = 2U,
  subscribe = 3U,
  activate = 4U,
};

enum class SyncAuthorizationDecision : std::uint8_t {
  authorized = 1U,
  invalid_policy = 2U,
  authority_v3_required = 3U,
  exact_head_proof_required = 4U,
  capability_missing = 5U,
  writer_not_allowed = 6U,
  subscriber_not_allowed = 7U,
  activation_disabled = 8U,
  invalid_operation = 9U,
};

struct SyncAuthorizationResult {
  SyncAuthorizationDecision decision{
      SyncAuthorizationDecision::invalid_operation};
  std::uint64_t required_capability{0U};

  [[nodiscard]] bool authorized() const noexcept {
    return decision == SyncAuthorizationDecision::authorized;
  }
};

// A content-v2 source is not a second HEAD authority. The caller first
// verifies and freezes one signed HEAD, then may select another exact-v3-
// proven writer principal that advertises that same record digest. Complete
// object bytes remain independently digest-verified.
enum class SyncContentSourceDecision : std::uint8_t {
  authorized = 1U,
  invalid_policy = 2U,
  content_v2_required = 3U,
  invalid_expected_head = 4U,
  authority_v3_required = 5U,
  exact_head_proof_required = 6U,
  capability_missing = 7U,
  source_not_allowed = 8U,
  head_mismatch = 9U,
};

struct SyncContentSourceAuthorizationResult {
  SyncContentSourceDecision decision{
      SyncContentSourceDecision::invalid_policy};
  std::uint64_t required_capability{0U};

  [[nodiscard]] bool authorized() const noexcept {
    return decision == SyncContentSourceDecision::authorized;
  }
};

[[nodiscard]] std::string_view
sync_operation_name(SyncOperation operation) noexcept;
[[nodiscard]] std::string_view sync_authorization_decision_name(
    SyncAuthorizationDecision decision) noexcept;
[[nodiscard]] std::string_view sync_content_source_decision_name(
    SyncContentSourceDecision decision) noexcept;

// Pure admission gate for future sync service entrances. The authority proof
// must name the exact current local v3 head; capability and namespace
// membership are independent mandatory checks. Callers must evaluate this
// immediately before admitting an effect and serialize admission with any
// authority or namespace-policy replacement they expose concurrently.
[[nodiscard]] SyncAuthorizationResult evaluate_sync_authorization(
    SyncOperation operation, const NamespacePolicy &policy,
    const security::AuthoritySnapshot &current_authority,
    const security::PeerAuthoritySnapshot &peer_authority);

// EXPECTED_HEAD must already be signature-verified and frozen by the caller.
// ADVERTISED_HEAD_RECORD is the digest of the candidate source's separately
// verified signed HEAD. This allocates no wire format and grants no HEAD
// transition or activation right.
[[nodiscard]] SyncContentSourceAuthorizationResult
evaluate_sync_content_source(
    const NamespacePolicy &policy, const AcceptedHead &expected_head,
    const Digest &advertised_head_record,
    const security::AuthoritySnapshot &current_authority,
    const security::PeerAuthoritySnapshot &peer_authority);

} // namespace iotox::sync
