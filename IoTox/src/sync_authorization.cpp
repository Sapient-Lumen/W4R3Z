#include "iotox/sync_authorization.hpp"

#include <algorithm>

namespace iotox::sync {
namespace {

std::uint64_t required_capability(SyncOperation operation) noexcept {
  switch (operation) {
  case SyncOperation::administer:
    return static_cast<std::uint64_t>(security::Capability::sync_admin);
  case SyncOperation::publish:
    return static_cast<std::uint64_t>(security::Capability::sync_publish);
  case SyncOperation::subscribe:
    return static_cast<std::uint64_t>(security::Capability::sync_subscribe);
  case SyncOperation::activate:
    return static_cast<std::uint64_t>(security::Capability::sync_activate);
  }
  return 0U;
}

bool exact_v3_head(const security::AuthoritySnapshot &current,
                   const security::PeerAuthoritySnapshot &peer) noexcept {
  return current.initialized &&
         current.format == security::AuthorityLedgerFormat::v3 &&
         peer.connected && peer.feature_negotiated &&
         peer.authority_v2_negotiated && peer.authority_v3_negotiated &&
         peer.verifier_state == security::AuthorityVerifierState::authorized &&
         peer.remote_authorized &&
         peer.local_authority_format == current.format &&
         peer.local_authority_epoch == current.ownership_epoch &&
         peer.local_authority_sequence == current.sequence &&
         security::constant_time_equal(peer.local_authority_tail_digest,
                                       current.tail_digest);
}

bool contains(const std::vector<PrincipalId> &principals,
              const PrincipalId &principal) {
  return std::binary_search(principals.begin(), principals.end(), principal);
}

} // namespace

std::string_view sync_operation_name(SyncOperation operation) noexcept {
  switch (operation) {
  case SyncOperation::administer:
    return "administer";
  case SyncOperation::publish:
    return "publish";
  case SyncOperation::subscribe:
    return "subscribe";
  case SyncOperation::activate:
    return "activate";
  }
  return "unknown";
}

std::string_view sync_authorization_decision_name(
    SyncAuthorizationDecision decision) noexcept {
  switch (decision) {
  case SyncAuthorizationDecision::authorized:
    return "authorized";
  case SyncAuthorizationDecision::invalid_policy:
    return "invalid-policy";
  case SyncAuthorizationDecision::authority_v3_required:
    return "authority-v3-required";
  case SyncAuthorizationDecision::exact_head_proof_required:
    return "exact-head-proof-required";
  case SyncAuthorizationDecision::capability_missing:
    return "capability-missing";
  case SyncAuthorizationDecision::writer_not_allowed:
    return "writer-not-allowed";
  case SyncAuthorizationDecision::subscriber_not_allowed:
    return "subscriber-not-allowed";
  case SyncAuthorizationDecision::activation_disabled:
    return "activation-disabled";
  case SyncAuthorizationDecision::invalid_operation:
    return "invalid-operation";
  }
  return "unknown";
}

std::string_view sync_content_source_decision_name(
    SyncContentSourceDecision decision) noexcept {
  switch (decision) {
  case SyncContentSourceDecision::authorized:
    return "authorized";
  case SyncContentSourceDecision::invalid_policy:
    return "invalid-policy";
  case SyncContentSourceDecision::content_v2_required:
    return "content-v2-required";
  case SyncContentSourceDecision::invalid_expected_head:
    return "invalid-expected-head";
  case SyncContentSourceDecision::authority_v3_required:
    return "authority-v3-required";
  case SyncContentSourceDecision::exact_head_proof_required:
    return "exact-head-proof-required";
  case SyncContentSourceDecision::capability_missing:
    return "capability-missing";
  case SyncContentSourceDecision::source_not_allowed:
    return "source-not-allowed";
  case SyncContentSourceDecision::head_mismatch:
    return "head-mismatch";
  }
  return "unknown";
}

SyncAuthorizationResult evaluate_sync_authorization(
    SyncOperation operation, const NamespacePolicy &policy,
    const security::AuthoritySnapshot &current_authority,
    const security::PeerAuthoritySnapshot &peer_authority) {
  const std::uint64_t capability = required_capability(operation);
  if (capability == 0U) {
    return {SyncAuthorizationDecision::invalid_operation, 0U};
  }
  if (!validate_namespace_policy(policy).ok()) {
    return {SyncAuthorizationDecision::invalid_policy, capability};
  }
  if (!current_authority.initialized ||
      current_authority.format != security::AuthorityLedgerFormat::v3) {
    return {SyncAuthorizationDecision::authority_v3_required, capability};
  }
  if (!exact_v3_head(current_authority, peer_authority)) {
    return {SyncAuthorizationDecision::exact_head_proof_required, capability};
  }
  if ((peer_authority.remote_capabilities & capability) != capability) {
    return {SyncAuthorizationDecision::capability_missing, capability};
  }
  if (operation == SyncOperation::publish &&
      !contains(policy.writers, peer_authority.remote_principal)) {
    return {SyncAuthorizationDecision::writer_not_allowed, capability};
  }
  if ((operation == SyncOperation::subscribe ||
       operation == SyncOperation::activate) &&
      !contains(policy.subscribers, peer_authority.remote_principal)) {
    return {SyncAuthorizationDecision::subscriber_not_allowed, capability};
  }
  if (operation == SyncOperation::activate &&
      policy.activation != ActivationMode::manual) {
    return {SyncAuthorizationDecision::activation_disabled, capability};
  }
  return {SyncAuthorizationDecision::authorized, capability};
}

SyncContentSourceAuthorizationResult evaluate_sync_content_source(
    const NamespacePolicy &policy, const AcceptedHead &expected_head,
    const Digest &advertised_head_record,
    const security::AuthoritySnapshot &current_authority,
    const security::PeerAuthoritySnapshot &peer_authority) {
  const SyncAuthorizationResult publication = evaluate_sync_authorization(
      SyncOperation::publish, policy, current_authority, peer_authority);
  const auto result = [&](SyncContentSourceDecision decision) {
    return SyncContentSourceAuthorizationResult{
        decision, publication.required_capability};
  };
  switch (publication.decision) {
  case SyncAuthorizationDecision::authorized:
    break;
  case SyncAuthorizationDecision::invalid_policy:
    return result(SyncContentSourceDecision::invalid_policy);
  case SyncAuthorizationDecision::authority_v3_required:
    return result(SyncContentSourceDecision::authority_v3_required);
  case SyncAuthorizationDecision::exact_head_proof_required:
    return result(SyncContentSourceDecision::exact_head_proof_required);
  case SyncAuthorizationDecision::capability_missing:
    return result(SyncContentSourceDecision::capability_missing);
  case SyncAuthorizationDecision::writer_not_allowed:
    return result(SyncContentSourceDecision::source_not_allowed);
  case SyncAuthorizationDecision::subscriber_not_allowed:
  case SyncAuthorizationDecision::activation_disabled:
  case SyncAuthorizationDecision::invalid_operation:
    return result(SyncContentSourceDecision::invalid_policy);
  }
  if (policy.engine != Engine::content_v2) {
    return result(SyncContentSourceDecision::content_v2_required);
  }
  if (!validate_accepted_head(policy, expected_head).ok()) {
    return result(SyncContentSourceDecision::invalid_expected_head);
  }
  if (!security::constant_time_equal(expected_head.record,
                                     advertised_head_record)) {
    return result(SyncContentSourceDecision::head_mismatch);
  }
  return result(SyncContentSourceDecision::authorized);
}

} // namespace iotox::sync
