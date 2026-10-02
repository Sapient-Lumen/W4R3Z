#include "test_harness.hpp"

#include "iotox/sync_authorization.hpp"

#include <cstdint>

namespace {

using iotox::security::AuthorityLedgerFormat;
using iotox::security::AuthoritySnapshot;
using iotox::security::AuthorityVerifierState;
using iotox::security::Capability;
using iotox::security::PeerAuthoritySnapshot;
using iotox::sync::AcceptedHead;
using iotox::sync::ActivationMode;
using iotox::sync::Engine;
using iotox::sync::NamespacePolicy;
using iotox::sync::PrincipalId;
using iotox::sync::SyncAuthorizationDecision;
using iotox::sync::SyncContentSourceDecision;
using iotox::sync::SyncOperation;

PrincipalId principal(std::uint8_t value) {
  PrincipalId result{};
  result[0U] = value;
  return result;
}

NamespacePolicy policy() {
  NamespacePolicy result;
  result.id = "field-notes";
  result.root = "/var/lib/iotox/sync/field-notes";
  result.activation = ActivationMode::manual;
  result.writers = {principal(1U)};
  result.subscribers = {principal(2U)};
  return result;
}

AcceptedHead head(const NamespacePolicy &configured) {
  AcceptedHead result;
  result.namespace_id = configured.id;
  result.writer = principal(1U);
  result.engine = configured.engine;
  result.generation = 7U;
  result.record[0U] = 31U;
  result.artifact[0U] = 32U;
  result.manifest[0U] = 33U;
  result.artifact_bytes = 4096U;
  result.manifest_bytes = 512U;
  return result;
}

AuthoritySnapshot authority() {
  AuthoritySnapshot result;
  result.initialized = true;
  result.format = AuthorityLedgerFormat::v3;
  result.ownership_epoch = 7U;
  result.sequence = 19U;
  result.tail_digest[0U] = 42U;
  return result;
}

PeerAuthoritySnapshot peer(const AuthoritySnapshot &current,
                           PrincipalId remote,
                           std::uint64_t capabilities) {
  PeerAuthoritySnapshot result;
  result.connected = true;
  result.feature_negotiated = true;
  result.authority_v2_negotiated = true;
  result.authority_v3_negotiated = true;
  result.verifier_state = AuthorityVerifierState::authorized;
  result.remote_authorized = true;
  result.remote_principal = remote;
  result.remote_capabilities = capabilities;
  result.local_authority_format = current.format;
  result.local_authority_epoch = current.ownership_epoch;
  result.local_authority_sequence = current.sequence;
  result.local_authority_tail_digest = current.tail_digest;
  return result;
}

std::uint64_t bit(Capability capability) {
  return static_cast<std::uint64_t>(capability);
}

} // namespace

IOTOX_TEST("sync authorization maps every operation to one independent capability") {
  const AuthoritySnapshot current = authority();
  const NamespacePolicy configured = policy();

  auto admin = iotox::sync::evaluate_sync_authorization(
      SyncOperation::administer, configured, current,
      peer(current, principal(9U), bit(Capability::sync_admin)));
  IOTOX_CHECK(admin.authorized());
  IOTOX_CHECK(admin.required_capability == bit(Capability::sync_admin));

  auto publish = iotox::sync::evaluate_sync_authorization(
      SyncOperation::publish, configured, current,
      peer(current, principal(1U), bit(Capability::sync_publish)));
  IOTOX_CHECK(publish.authorized());
  IOTOX_CHECK(publish.required_capability == bit(Capability::sync_publish));

  auto subscribe = iotox::sync::evaluate_sync_authorization(
      SyncOperation::subscribe, configured, current,
      peer(current, principal(2U), bit(Capability::sync_subscribe)));
  IOTOX_CHECK(subscribe.authorized());
  IOTOX_CHECK(subscribe.required_capability == bit(Capability::sync_subscribe));

  auto activate = iotox::sync::evaluate_sync_authorization(
      SyncOperation::activate, configured, current,
      peer(current, principal(2U), bit(Capability::sync_activate)));
  IOTOX_CHECK(activate.authorized());
  IOTOX_CHECK(activate.required_capability == bit(Capability::sync_activate));
}

IOTOX_TEST("sync authorization rejects v1 v2 and uninitialized authority") {
  NamespacePolicy configured = policy();
  AuthoritySnapshot current = authority();
  PeerAuthoritySnapshot proven =
      peer(current, principal(1U), bit(Capability::sync_publish));

  current.format = AuthorityLedgerFormat::v2;
  auto denied = iotox::sync::evaluate_sync_authorization(
      SyncOperation::publish, configured, current, proven);
  IOTOX_CHECK(denied.decision ==
              SyncAuthorizationDecision::authority_v3_required);

  current = authority();
  current.initialized = false;
  denied = iotox::sync::evaluate_sync_authorization(
      SyncOperation::publish, configured, current, proven);
  IOTOX_CHECK(denied.decision ==
              SyncAuthorizationDecision::authority_v3_required);
}

IOTOX_TEST("sync authorization requires a negotiated exact-head proof") {
  const AuthoritySnapshot current = authority();
  const NamespacePolicy configured = policy();
  PeerAuthoritySnapshot proven =
      peer(current, principal(1U), bit(Capability::sync_publish));

  proven.local_authority_sequence += 1U;
  auto denied = iotox::sync::evaluate_sync_authorization(
      SyncOperation::publish, configured, current, proven);
  IOTOX_CHECK(denied.decision ==
              SyncAuthorizationDecision::exact_head_proof_required);

  proven = peer(current, principal(1U), bit(Capability::sync_publish));
  proven.authority_v3_negotiated = false;
  denied = iotox::sync::evaluate_sync_authorization(
      SyncOperation::publish, configured, current, proven);
  IOTOX_CHECK(denied.decision ==
              SyncAuthorizationDecision::exact_head_proof_required);

  proven = peer(current, principal(1U), bit(Capability::sync_publish));
  proven.remote_authorized = false;
  denied = iotox::sync::evaluate_sync_authorization(
      SyncOperation::publish, configured, current, proven);
  IOTOX_CHECK(denied.decision ==
              SyncAuthorizationDecision::exact_head_proof_required);
}

IOTOX_TEST("sync authorization never substitutes one sync capability for another") {
  const AuthoritySnapshot current = authority();
  const NamespacePolicy configured = policy();
  const auto wrong = peer(current, principal(2U),
                          bit(Capability::sync_subscribe));
  const auto denied = iotox::sync::evaluate_sync_authorization(
      SyncOperation::activate, configured, current, wrong);
  IOTOX_CHECK(denied.decision ==
              SyncAuthorizationDecision::capability_missing);
  IOTOX_CHECK(denied.required_capability == bit(Capability::sync_activate));
}

IOTOX_TEST("sync publication requires the proven principal in the writer set") {
  const AuthoritySnapshot current = authority();
  const NamespacePolicy configured = policy();
  const auto denied = iotox::sync::evaluate_sync_authorization(
      SyncOperation::publish, configured, current,
      peer(current, principal(2U), bit(Capability::sync_publish)));
  IOTOX_CHECK(denied.decision ==
              SyncAuthorizationDecision::writer_not_allowed);
}

IOTOX_TEST("sync convergence and activation require subscriber membership") {
  const AuthoritySnapshot current = authority();
  const NamespacePolicy configured = policy();
  auto denied = iotox::sync::evaluate_sync_authorization(
      SyncOperation::subscribe, configured, current,
      peer(current, principal(1U), bit(Capability::sync_subscribe)));
  IOTOX_CHECK(denied.decision ==
              SyncAuthorizationDecision::subscriber_not_allowed);

  denied = iotox::sync::evaluate_sync_authorization(
      SyncOperation::activate, configured, current,
      peer(current, principal(1U), bit(Capability::sync_activate)));
  IOTOX_CHECK(denied.decision ==
              SyncAuthorizationDecision::subscriber_not_allowed);
}

IOTOX_TEST("sync activation requires manual host policy after authority") {
  const AuthoritySnapshot current = authority();
  NamespacePolicy configured = policy();
  configured.activation = ActivationMode::disabled;
  const auto denied = iotox::sync::evaluate_sync_authorization(
      SyncOperation::activate, configured, current,
      peer(current, principal(2U), bit(Capability::sync_activate)));
  IOTOX_CHECK(denied.decision ==
              SyncAuthorizationDecision::activation_disabled);
}

IOTOX_TEST("sync authorization rejects invalid policy and operation deterministically") {
  const AuthoritySnapshot current = authority();
  NamespacePolicy configured = policy();
  configured.writers.clear();
  auto denied = iotox::sync::evaluate_sync_authorization(
      SyncOperation::publish, configured, current,
      peer(current, principal(1U), bit(Capability::sync_publish)));
  IOTOX_CHECK(denied.decision == SyncAuthorizationDecision::invalid_policy);

  configured = policy();
  denied = iotox::sync::evaluate_sync_authorization(
      static_cast<SyncOperation>(255U), configured, current,
      peer(current, principal(1U), bit(Capability::sync_publish)));
  IOTOX_CHECK(denied.decision ==
              SyncAuthorizationDecision::invalid_operation);
  IOTOX_CHECK(!denied.authorized());
  IOTOX_CHECK(iotox::sync::sync_operation_name(SyncOperation::activate) ==
              "activate");
  IOTOX_CHECK(iotox::sync::sync_operation_name(
                  static_cast<SyncOperation>(255U)) == "unknown");
  IOTOX_CHECK(iotox::sync::sync_authorization_decision_name(
                  SyncAuthorizationDecision::exact_head_proof_required) ==
              "exact-head-proof-required");
  IOTOX_CHECK(iotox::sync::sync_authorization_decision_name(
                  static_cast<SyncAuthorizationDecision>(255U)) == "unknown");
}

IOTOX_TEST("content source selection separates exact head authority from immutable bytes") {
  const AuthoritySnapshot current = authority();
  NamespacePolicy configured = policy();
  configured.engine = Engine::content_v2;
  configured.writers.push_back(principal(3U));
  const AcceptedHead expected = head(configured);

  const auto selected = iotox::sync::evaluate_sync_content_source(
      configured, expected, expected.record, current,
      peer(current, principal(3U), bit(Capability::sync_publish)));
  IOTOX_CHECK(selected.authorized());
  IOTOX_CHECK(selected.required_capability == bit(Capability::sync_publish));
  IOTOX_CHECK(expected.writer != principal(3U));

  auto wrong_head = expected.record;
  wrong_head[0U] ^= 1U;
  const auto mismatch = iotox::sync::evaluate_sync_content_source(
      configured, expected, wrong_head, current,
      peer(current, principal(3U), bit(Capability::sync_publish)));
  IOTOX_CHECK(mismatch.decision == SyncContentSourceDecision::head_mismatch);
}

IOTOX_TEST("content source selection fails closed on authority membership and engine") {
  const AuthoritySnapshot current = authority();
  NamespacePolicy configured = policy();
  configured.engine = Engine::content_v2;
  const AcceptedHead expected = head(configured);

  auto denied = iotox::sync::evaluate_sync_content_source(
      configured, expected, expected.record, current,
      peer(current, principal(9U), bit(Capability::sync_publish)));
  IOTOX_CHECK(denied.decision == SyncContentSourceDecision::source_not_allowed);

  denied = iotox::sync::evaluate_sync_content_source(
      configured, expected, expected.record, current,
      peer(current, principal(1U), bit(Capability::sync_subscribe)));
  IOTOX_CHECK(denied.decision == SyncContentSourceDecision::capability_missing);

  configured.engine = Engine::range_v1;
  AcceptedHead range_head = head(configured);
  denied = iotox::sync::evaluate_sync_content_source(
      configured, range_head, range_head.record, current,
      peer(current, principal(1U), bit(Capability::sync_publish)));
  IOTOX_CHECK(denied.decision == SyncContentSourceDecision::content_v2_required);

  configured.engine = Engine::content_v2;
  AcceptedHead invalid = head(configured);
  invalid.artifact = {};
  denied = iotox::sync::evaluate_sync_content_source(
      configured, invalid, invalid.record, current,
      peer(current, principal(1U), bit(Capability::sync_publish)));
  IOTOX_CHECK(denied.decision ==
              SyncContentSourceDecision::invalid_expected_head);

  IOTOX_CHECK(iotox::sync::sync_content_source_decision_name(
                  SyncContentSourceDecision::source_not_allowed) ==
              "source-not-allowed");
  IOTOX_CHECK(iotox::sync::sync_content_source_decision_name(
                  static_cast<SyncContentSourceDecision>(255U)) == "unknown");
}
