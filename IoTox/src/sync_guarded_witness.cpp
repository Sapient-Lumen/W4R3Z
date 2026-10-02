#include "iotox/sync_guarded_witness.hpp"

#include "iotox/security/random.hpp"

#include <algorithm>
#include <array>
#include <limits>
#include <string>
#include <vector>

namespace iotox::sync {
namespace {

constexpr std::string_view kDomainDerivation{
    "iotox-sync-guarded-witness-domain-v1"};
constexpr std::string_view kHeadDigestDomain{
    "iotox-sync-guarded-state-head-v1"};

void append_u32(std::vector<std::uint8_t> &output, std::uint32_t value) {
  output.push_back(static_cast<std::uint8_t>(value >> 24U));
  output.push_back(static_cast<std::uint8_t>(value >> 16U));
  output.push_back(static_cast<std::uint8_t>(value >> 8U));
  output.push_back(static_cast<std::uint8_t>(value));
}

void append_u64(std::vector<std::uint8_t> &output, std::uint64_t value) {
  for (std::size_t index = 0U; index < 8U; ++index) {
    output.push_back(static_cast<std::uint8_t>(
        value >> ((7U - index) * 8U)));
  }
}

void append_bytes(std::vector<std::uint8_t> &output,
                  std::span<const std::uint8_t> value) {
  output.insert(output.end(), value.begin(), value.end());
}

void append_string(std::vector<std::uint8_t> &output,
                   std::string_view value) {
  append_u32(output, static_cast<std::uint32_t>(value.size()));
  output.insert(output.end(), value.begin(), value.end());
}

[[nodiscard]] bool all_zero(
    std::span<const std::uint8_t> value) noexcept {
  return std::all_of(value.begin(), value.end(),
                     [](std::uint8_t byte) { return byte == 0U; });
}

[[nodiscard]] bool same_storage_identity(
    const NamespacePolicy &left, const NamespacePolicy &right) noexcept {
  return left.id == right.id && left.root == right.root &&
      left.engine == right.engine && left.quotas == right.quotas;
}

[[nodiscard]] Status validate_covered_policy(
    const NamespacePolicy &policy) {
  const Status valid = validate_namespace_policy(policy);
  if (!valid.ok()) return valid;
  if (policy.engine == Engine::tree_v2) {
    return Status{
        ErrorCode::unsupported,
        "tree-v2 frontier is not covered by the four-root sync witness"};
  }
  return Status::success();
}

[[nodiscard]] Status validate_config(
    const SyncGuardedStateWitness::Config &config,
    const NamespacePolicy &policy,
    const security::DeviceIdentity &identity) {
  const Status covered = validate_covered_policy(policy);
  if (!covered.ok()) return covered;
  rollback_witness::Record selector;
  selector.domain = config.domain;
  selector.device = identity.public_key();
  selector.witness_epoch = config.witness_epoch;
  selector.lane = rollback_witness::Lane::sync_guarded_state;
  if (!config.backend || !rollback_witness::validate(selector).ok()) {
    return Status{ErrorCode::invalid_argument,
                  "sync guarded-state witness configuration is invalid"};
  }
  if (!config.backend->independently_controlled() &&
      !config.allow_non_independent_for_testing) {
    return Status{
        ErrorCode::unsupported,
        "sync guarded-state witness shares the local failure domain"};
  }
  return Status::success();
}

[[nodiscard]] bool same_selector(
    const rollback_witness::Record &record,
    const SyncGuardedStateWitness::Config &config,
    const security::DeviceIdentity &identity) noexcept {
  return record.domain == config.domain &&
      security::constant_time_equal(record.device, identity.public_key()) &&
      record.witness_epoch == config.witness_epoch &&
      record.lane == rollback_witness::Lane::sync_guarded_state;
}

[[nodiscard]] Status resolve_cas(
    rollback_witness::Backend &backend,
    const rollback_witness::Record &expected,
    const rollback_witness::Record &desired,
    std::string_view label) {
  const Status exchanged = backend.compare_exchange(expected, desired);
  if (exchanged.ok()) return exchanged;
  auto observed = backend.query();
  if (observed && observed.value() == desired) return Status::success();
  return Status{exchanged.code(),
                std::string(label) + ": " + exchanged.message()};
}

[[nodiscard]] Result<SyncRollbackHead> current_local_head(
    const NamespacePolicy &policy,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) {
  auto roots = load_sync_rollback_roots(
      policy, identity.public_key(), sodium, transaction);
  if (!roots) return roots.status();
  return make_sync_rollback_head(
      policy, identity.public_key(), roots.value(), sodium);
}

[[nodiscard]] Result<rollback_witness::Head> semantic_head(
    const NamespacePolicy &policy, const SyncRollbackHead &head,
    std::uint64_t position, const security::Sodium &sodium) {
  auto digest = sync_guarded_state_digest(policy, head, sodium);
  if (!digest) return digest.status();
  return rollback_witness::Head{position, digest.value()};
}

} // namespace

Result<rollback_witness::DomainId> derive_sync_guarded_witness_domain(
    const rollback_witness::DomainId &base_domain,
    const security::SigningPublicKey &device,
    std::string_view namespace_id,
    const security::Sodium &sodium) {
  if (all_zero(base_domain) || all_zero(device) ||
      !valid_namespace_id(namespace_id)) {
    return Status{ErrorCode::invalid_argument,
                  "sync guarded witness domain inputs are invalid"};
  }
  std::vector<std::uint8_t> material;
  material.reserve(base_domain.size() + device.size() + 4U +
                   namespace_id.size());
  append_bytes(material, base_domain);
  append_bytes(material, device);
  append_string(material, namespace_id);
  auto digest = sodium.hash(kDomainDerivation, material);
  if (!digest) return digest.status();
  rollback_witness::DomainId result{};
  std::copy_n(digest.value().begin(), result.size(), result.begin());
  if (all_zero(result)) {
    return Status{ErrorCode::protocol_error,
                  "derived sync guarded witness domain is zero"};
  }
  return result;
}

Result<security::Digest> sync_guarded_state_digest(
    const NamespacePolicy &policy, const SyncRollbackHead &head,
    const security::Sodium &sodium) {
  const Status covered = validate_covered_policy(policy);
  if (!covered.ok()) return covered;
  if (policy.id.size() > std::numeric_limits<std::uint32_t>::max() ||
      policy.root.size() > std::numeric_limits<std::uint32_t>::max()) {
    return Status{ErrorCode::resource_exhausted,
                  "sync guarded storage identity is too large"};
  }
  std::vector<std::uint8_t> material;
  material.reserve(256U + policy.id.size() + policy.root.size());
  append_string(material, policy.id);
  append_string(material, policy.root);
  material.push_back(static_cast<std::uint8_t>(policy.engine));
  const std::array<std::uint64_t, 9U> quotas{{
      policy.quotas.maximum_artifact_bytes,
      policy.quotas.maximum_manifest_bytes,
      policy.quotas.maximum_store_bytes,
      policy.quotas.maximum_staging_bytes,
      policy.quotas.maximum_objects,
      policy.quotas.maximum_retained_revisions,
      policy.quotas.maximum_peers,
      policy.quotas.maximum_lanes,
      policy.quotas.maximum_outstanding_requests}};
  for (const std::uint64_t quota : quotas) append_u64(material, quota);
  const std::array<const SyncRollbackRoot *, 4U> roots{{
      &head.published, &head.accepted, &head.activated, &head.retained}};
  for (const SyncRollbackRoot *root : roots) {
    if ((root->counter == 0U) != all_zero(root->record)) {
      return Status{ErrorCode::protocol_error,
                    "sync guarded root is only partly initialized"};
    }
    append_u64(material, root->counter);
    append_bytes(material, root->record);
  }
  return sodium.hash(kHeadDigestDomain, material);
}

Result<rollback_witness::Record> sync_guarded_state_enrollment_record(
    const NamespacePolicy &policy,
    const rollback_witness::DomainId &base_domain,
    std::uint64_t witness_epoch,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) {
  const Status covered = validate_covered_policy(policy);
  if (!covered.ok()) return covered;
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok()) return held;
  auto local = current_local_head(policy, identity, sodium, transaction);
  if (!local) return local.status();
  SyncRollbackGuardStore guard_store(policy.root);
  auto guard = guard_store.load(policy, identity.public_key(), sodium);
  if (!guard) return guard.status();
  if ((!guard.value() && !local.value().empty()) ||
      (guard.value() &&
       (guard.value()->pending.has_value() ||
        guard.value()->committed != local.value()))) {
    return Status{ErrorCode::unavailable,
                  "sync guarded enrollment requires quiescent reconciled roots"};
  }
  auto domain = derive_sync_guarded_witness_domain(
      base_domain, identity.public_key(), policy.id, sodium);
  if (!domain) return domain.status();
  auto head = semantic_head(policy, local.value(), 1U, sodium);
  if (!head) return head.status();
  rollback_witness::Record record;
  record.domain = domain.value();
  record.device = identity.public_key();
  record.witness_epoch = witness_epoch;
  record.lane = rollback_witness::Lane::sync_guarded_state;
  record.committed = head.value();
  const Status valid = rollback_witness::validate(record);
  if (!valid.ok()) return valid;
  return record;
}

SyncGuardedStateWitness::SyncGuardedStateWitness(
    Config config, NamespacePolicy policy,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium)
    : config_(std::move(config)), policy_(std::move(policy)),
      identity_(&identity), sodium_(&sodium) {}

std::optional<rollback_witness::Head>
SyncGuardedStateWitness::verified_head() const {
  std::scoped_lock lock(state_mutex_);
  return verified_head_;
}

Status SyncGuardedStateWitness::reconcile(
    const NamespacePolicy &policy,
    const SyncNamespaceTransaction &transaction) {
  {
    std::scoped_lock lock(state_mutex_);
    verified_head_.reset();
  }
  const Status configured = validate_config(config_, policy_, *identity_);
  if (!configured.ok()) return configured;
  if (!same_storage_identity(policy_, policy)) {
    return Status{ErrorCode::protocol_error,
                  "sync guarded witness storage identity changed"};
  }
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok()) return held;
  auto local = current_local_head(policy, *identity_, *sodium_, transaction);
  if (!local) return local.status();
  SyncRollbackGuardStore guard_store(policy.root);
  auto guard = guard_store.load(policy, identity_->public_key(), *sodium_);
  if (!guard) return guard.status();
  auto external = config_.backend->query();
  if (!external) {
    return Status{external.status().code(),
                  "unable to query sync guarded-state witness: " +
                      external.status().message()};
  }
  if (!rollback_witness::validate(external.value()).ok() ||
      !same_selector(external.value(), config_, *identity_) ||
      external.value().committed.position == 0U) {
    return Status{ErrorCode::protocol_error,
                  "sync guarded-state witness returned another or invalid lane"};
  }

  const auto digest_at = [&](const SyncRollbackHead &head,
                             std::uint64_t position) {
    return semantic_head(policy, head, position, *sodium_);
  };
  if (!guard.value()) {
    if (!local.value().empty() || external.value().pending) {
      return Status{ErrorCode::protocol_error,
                    "sync guarded witness found state without its local guard"};
    }
    auto head = digest_at(local.value(), external.value().committed.position);
    if (!head || head.value() != external.value().committed) {
      return Status{ErrorCode::protocol_error,
                    "empty sync roots are not the externally committed head"};
    }
    std::scoped_lock lock(state_mutex_);
    verified_head_ = external.value().committed;
    return Status::success();
  }

  SyncRollbackGuard local_guard = *guard.value();
  if (!local_guard.pending) {
    if (local_guard.committed != local.value()) {
      return Status{ErrorCode::protocol_error,
                    "sync roots diverge from their committed local guard"};
    }
    auto head = digest_at(local.value(), external.value().pending
                                             ? external.value().pending->position
                                             : external.value().committed.position);
    if (!head) return head.status();
    if (external.value().pending) {
      if (head.value() != *external.value().pending) {
        return Status{ErrorCode::protocol_error,
                      "local committed roots do not join the pending witness"};
      }
      auto committed = rollback_witness::finish(external.value());
      if (!committed) return committed.status();
      const Status finished = resolve_cas(
          *config_.backend, external.value(), committed.value(),
          "unable to finish recovered sync guarded-state witness");
      if (!finished.ok()) return finished;
      external = committed.value();
    } else if (head.value() != external.value().committed) {
      return Status{ErrorCode::protocol_error,
                    "local sync roots are not the externally committed head"};
    }
    std::scoped_lock lock(state_mutex_);
    verified_head_ = external.value().committed;
    return Status::success();
  }

  const SyncRollbackHead old = local_guard.committed;
  const SyncRollbackHead next = *local_guard.pending;
  auto old_head = digest_at(old, external.value().committed.position);
  const std::uint64_t next_position = external.value().pending
      ? external.value().pending->position
      : external.value().committed.position ==
                std::numeric_limits<std::uint64_t>::max()
            ? 0U
            : external.value().committed.position + 1U;
  if (next_position == 0U) {
    return Status{ErrorCode::resource_exhausted,
                  "sync guarded-state witness position is exhausted"};
  }
  auto next_head = digest_at(next, next_position);
  if (!old_head || !next_head) {
    return !old_head ? old_head.status() : next_head.status();
  }
  if (local.value() == old) {
    if (external.value().pending ||
        external.value().committed != old_head.value()) {
      return Status{ErrorCode::protocol_error,
                    "uncommitted sync root has an impossible external advance"};
    }
    auto cleared = guard_store.reconcile(
        policy, local.value(), *identity_, *sodium_, transaction);
    if (!cleared) return cleared.status();
    std::scoped_lock lock(state_mutex_);
    verified_head_ = external.value().committed;
    return Status::success();
  }
  if (local.value() != next) {
    return Status{ErrorCode::protocol_error,
                  "sync root is neither side of its guarded transition"};
  }

  if (external.value().pending) {
    if (external.value().committed.digest != old_head.value().digest ||
        *external.value().pending != next_head.value()) {
      return Status{ErrorCode::protocol_error,
                    "pending sync witness does not join the guarded root transition"};
    }
  } else {
    if (external.value().committed != old_head.value()) {
      return Status{ErrorCode::protocol_error,
                    "landed sync root cannot advance from external state"};
    }
    rollback_witness::TransactionNonce nonce{};
    const Status random = security::fill_random(nonce);
    if (!random.ok()) return random;
    auto pending = rollback_witness::begin(
        external.value(), next_head.value(), nonce);
    if (!pending) return pending.status();
    const Status begun = resolve_cas(
        *config_.backend, external.value(), pending.value(),
        "unable to recover landed sync root into its witness");
    if (!begun.ok()) return begun;
    external = pending.value();
  }
  const Status local_finished = guard_store.finish(
      policy, next, *identity_, *sodium_, transaction);
  if (!local_finished.ok()) return local_finished;
  auto committed = rollback_witness::finish(external.value());
  if (!committed) return committed.status();
  const Status remote_finished = resolve_cas(
      *config_.backend, external.value(), committed.value(),
      "unable to finish recovered sync root witness");
  if (!remote_finished.ok()) return remote_finished;
  std::scoped_lock lock(state_mutex_);
  verified_head_ = committed.value().committed;
  return Status::success();
}

Status SyncGuardedStateWitness::verify_read(
    const NamespacePolicy &policy,
    const SyncNamespaceTransaction &transaction) {
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok()) return held;
  auto local = current_local_head(policy, *identity_, *sodium_, transaction);
  if (!local) return local.status();
  SyncRollbackGuardStore guard_store(policy.root);
  auto guard = guard_store.load(policy, identity_->public_key(), *sodium_);
  if (!guard) return guard.status();
  const bool stable = (!guard.value() && local.value().empty()) ||
      (guard.value() && !guard.value()->pending &&
       guard.value()->committed == local.value());
  if (!stable) {
    return reconcile(policy, transaction);
  }
  std::optional<rollback_witness::Head> verified;
  {
    std::scoped_lock lock(state_mutex_);
    verified = verified_head_;
  }
  if (!verified) return reconcile(policy, transaction);
  auto local_head = semantic_head(
      policy, local.value(), verified->position, *sodium_);
  if (!local_head || local_head.value() != *verified) {
    return Status{ErrorCode::protocol_error,
                  "sync guarded read found an uncommitted local head"};
  }
  return Status::success();
}

Status SyncGuardedStateWitness::transition(
    const NamespacePolicy &policy,
    const SyncReachabilityRoots &current,
    const SyncReachabilityRoots &next,
    const SyncNamespaceTransaction &transaction,
    const SyncRootCommit &commit) {
  if (!commit) {
    return Status{ErrorCode::invalid_argument,
                  "witnessed sync transition requires one root commit"};
  }
  const Status reconciled = reconcile(policy, transaction);
  if (!reconciled.ok()) return reconciled;
  auto current_root = make_sync_rollback_head(
      policy, identity_->public_key(), current, *sodium_);
  auto next_root = make_sync_rollback_head(
      policy, identity_->public_key(), next, *sodium_);
  if (!current_root || !next_root) {
    return !current_root ? current_root.status() : next_root.status();
  }
  if (current_root.value() == next_root.value()) {
    return Status{ErrorCode::invalid_argument,
                  "witnessed sync transition does not change the root head"};
  }
  auto external = config_.backend->query();
  if (!external) return external.status();
  if (!same_selector(external.value(), config_, *identity_) ||
      external.value().pending ||
      external.value().committed.position ==
          std::numeric_limits<std::uint64_t>::max()) {
    return Status{ErrorCode::protocol_error,
                  "sync guarded-state witness is not ready to advance"};
  }
  auto current_head = semantic_head(
      policy, current_root.value(), external.value().committed.position,
      *sodium_);
  auto next_head = semantic_head(
      policy, next_root.value(), external.value().committed.position + 1U,
      *sodium_);
  if (!current_head || !next_head ||
      current_head.value() != external.value().committed) {
    return Status{ErrorCode::protocol_error,
                  "caller sync roots are not the verified witness head"};
  }
  {
    std::scoped_lock lock(state_mutex_);
    verified_head_.reset();
  }
  SyncRollbackGuardStore guard_store(policy.root);
  const Status begun = guard_store.begin(
      policy, current_root.value(), next_root.value(), *identity_, *sodium_,
      transaction);
  if (!begun.ok()) return begun;
  const Status stored = commit();
  if (!stored.ok()) return stored;
  rollback_witness::TransactionNonce nonce{};
  const Status random = security::fill_random(nonce);
  if (!random.ok()) return random;
  auto pending = rollback_witness::begin(
      external.value(), next_head.value(), nonce);
  if (!pending) return pending.status();
  const Status remote_begun = resolve_cas(
      *config_.backend, external.value(), pending.value(),
      "unable to begin sync guarded-state witness transition");
  if (!remote_begun.ok()) return remote_begun;
  const Status local_finished = guard_store.finish(
      policy, next_root.value(), *identity_, *sodium_, transaction);
  if (!local_finished.ok()) return local_finished;
  auto committed = rollback_witness::finish(pending.value());
  if (!committed) return committed.status();
  const Status remote_finished = resolve_cas(
      *config_.backend, pending.value(), committed.value(),
      "local sync root advanced but witness commit is unresolved");
  if (!remote_finished.ok()) return remote_finished;
  std::scoped_lock lock(state_mutex_);
  verified_head_ = committed.value().committed;
  return Status::success();
}

} // namespace iotox::sync
