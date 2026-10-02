#include "iotox/sync_reachability.hpp"

#include "iotox/sync_guarded_witness.hpp"
#include "iotox/sync_rollback.hpp"

#include <algorithm>
#include <limits>

namespace iotox::sync {
namespace {

[[nodiscard]] bool all_zero(const Digest &value) noexcept {
  return std::all_of(value.begin(), value.end(),
                     [](std::uint8_t byte) { return byte == 0U; });
}

[[nodiscard]] bool object_less(const SyncObjectRecord &left,
                               const SyncObjectRecord &right) noexcept {
  if (left.kind != right.kind)
    return left.kind < right.kind;
  return left.identity < right.identity;
}

[[nodiscard]] bool same_object(const SyncObjectRecord &left,
                               const SyncObjectRecord &right) noexcept {
  return left.kind == right.kind && left.identity == right.identity;
}

[[nodiscard]] Status validate_object(const NamespacePolicy &policy,
                                     const SyncObjectRecord &object) {
  if ((object.kind != SyncObjectKind::artifact &&
       object.kind != SyncObjectKind::manifest) ||
      all_zero(object.identity) || object.bytes == 0U ||
      (object.kind == SyncObjectKind::artifact &&
       object.bytes > policy.quotas.maximum_artifact_bytes) ||
      (object.kind == SyncObjectKind::manifest &&
       object.bytes > policy.quotas.maximum_manifest_bytes)) {
    return Status{ErrorCode::invalid_argument,
                  "sync reachability object is invalid"};
  }
  return Status::success();
}

[[nodiscard]] Status add_root(const NamespacePolicy &policy,
                              std::vector<SyncRootedObject> &roots,
                              SyncObjectRecord object,
                              SyncRootSource source) {
  const Status valid = validate_object(policy, object);
  if (!valid.ok())
    return valid;
  auto existing = std::find_if(
      roots.begin(), roots.end(), [&](const SyncRootedObject &root) {
        return same_object(root.object, object);
      });
  if (existing != roots.end()) {
    if (existing->object.bytes != object.bytes) {
      return Status{ErrorCode::protocol_error,
                    "sync live roots disagree about object size"};
    }
    existing->source_mask |= static_cast<std::uint8_t>(source);
    return Status::success();
  }
  if (roots.size() >= policy.quotas.maximum_objects) {
    return Status{ErrorCode::resource_exhausted,
                  "sync live roots exceed the object-store quota"};
  }
  roots.push_back(
      SyncRootedObject{std::move(object), static_cast<std::uint8_t>(source)});
  return Status::success();
}

[[nodiscard]] Status add_head_roots(const NamespacePolicy &policy,
                                    std::vector<SyncRootedObject> &roots,
                                    const Digest &artifact,
                                    std::uint64_t artifact_bytes,
                                    const Digest &manifest,
                                    std::uint64_t manifest_bytes,
                                    SyncRootSource source) {
  Status added = add_root(
      policy, roots,
      SyncObjectRecord{SyncObjectKind::artifact, artifact, artifact_bytes},
      source);
  if (!added.ok())
    return added;
  return add_root(
      policy, roots,
      SyncObjectRecord{SyncObjectKind::manifest, manifest, manifest_bytes},
      source);
}

} // namespace

Result<SyncReachabilityPlan> plan_sync_reachability(
    const NamespacePolicy &policy,
    const security::SigningPublicKey &expected_device,
    const SyncReachabilityRoots &roots,
    std::vector<SyncObjectRecord> inventory,
    const security::Sodium &sodium) {
  const Status valid_policy = validate_namespace_policy(policy);
  if (!valid_policy.ok())
    return valid_policy;
  if (all_zero(expected_device)) {
    return Status{ErrorCode::invalid_argument,
                  "sync reachability expected device is zero"};
  }

  std::uint64_t inventory_bytes = 0U;
  if (inventory.size() > policy.quotas.maximum_objects) {
    return Status{ErrorCode::resource_exhausted,
                  "sync reachability inventory exceeds object quota"};
  }
  for (const SyncObjectRecord &object : inventory) {
    const Status valid = validate_object(policy, object);
    if (!valid.ok())
      return valid;
    if (inventory_bytes > std::numeric_limits<std::uint64_t>::max() -
                              object.bytes) {
      return Status{ErrorCode::resource_exhausted,
                    "sync reachability inventory byte count overflows"};
    }
    inventory_bytes += object.bytes;
  }
  if (inventory_bytes > policy.quotas.maximum_store_bytes) {
    return Status{ErrorCode::resource_exhausted,
                  "sync reachability inventory exceeds store quota"};
  }
  std::sort(inventory.begin(), inventory.end(), object_less);
  if (std::adjacent_find(inventory.begin(), inventory.end(), same_object) !=
      inventory.end()) {
    return Status{ErrorCode::protocol_error,
                  "sync reachability inventory duplicates an object"};
  }

  std::vector<SyncRootedObject> expected;
  if (roots.published.has_value()) {
    if (roots.published->writer != expected_device) {
      return Status{ErrorCode::protocol_error,
                    "published sync root is not signed by this device"};
    }
    const Status verified =
        verify_signed_head(policy, *roots.published, sodium);
    if (!verified.ok())
      return verified;
    const Status added = add_head_roots(
        policy, expected, roots.published->artifact,
        roots.published->artifact_bytes, roots.published->manifest,
        roots.published->manifest_bytes, SyncRootSource::published);
    if (!added.ok())
      return added;
  }
  if (roots.accepted.has_value()) {
    const Status valid = validate_accepted_head(policy, *roots.accepted);
    if (!valid.ok())
      return valid;
    const Status added = add_head_roots(
        policy, expected, roots.accepted->artifact,
        roots.accepted->artifact_bytes, roots.accepted->manifest,
        roots.accepted->manifest_bytes, SyncRootSource::accepted);
    if (!added.ok())
      return added;
  }
  if (roots.activated.has_value()) {
    auto canonical = encode_activated_revision(*roots.activated);
    if (!canonical.ok() || roots.activated->namespace_id != policy.id ||
        roots.activated->artifact_bytes >
            policy.quotas.maximum_artifact_bytes) {
      return Status{ErrorCode::protocol_error,
                    "activated sync root is invalid for namespace policy"};
    }
    const Status added = add_root(
        policy, expected,
        SyncObjectRecord{SyncObjectKind::artifact,
                         roots.activated->artifact,
                         roots.activated->artifact_bytes},
        SyncRootSource::activated);
    if (!added.ok())
      return added;
  }

  SyncReachabilityPlan plan;
  if (roots.retained.mutation == 0U) {
    if (roots.retained.namespace_id != policy.id ||
        !roots.retained.revisions.empty()) {
      return Status{ErrorCode::protocol_error,
                    "absent sync retention sentinel is invalid"};
    }
  } else {
    auto encoded = encode_retention_snapshot(roots.retained);
    if (!encoded.ok())
      return encoded.status();
    auto bounded = decode_retention_snapshot(
        encoded.value(), policy.quotas.maximum_retained_revisions);
    if (!bounded.ok() || bounded.value() != roots.retained ||
        roots.retained.namespace_id != policy.id) {
      return Status{ErrorCode::protocol_error,
                    "retained sync roots are invalid for namespace policy"};
    }
    const Status verified = verify_retention_snapshot(
        roots.retained, expected_device, sodium);
    if (!verified.ok())
      return verified;
    plan.retention_authenticated = true;
    for (const RetainedRevision &revision : roots.retained.revisions) {
      const Status added = add_head_roots(
          policy, expected, revision.artifact, revision.artifact_bytes,
          revision.manifest, revision.manifest_bytes,
          SyncRootSource::retained);
      if (!added.ok())
        return added;
    }
  }

  std::uint64_t expected_bytes = 0U;
  for (const SyncRootedObject &root : expected) {
    if (expected_bytes > std::numeric_limits<std::uint64_t>::max() -
                             root.object.bytes) {
      return Status{ErrorCode::resource_exhausted,
                    "sync live-root byte count overflows"};
    }
    expected_bytes += root.object.bytes;
  }
  if (expected_bytes > policy.quotas.maximum_store_bytes) {
    return Status{ErrorCode::resource_exhausted,
                  "sync live roots exceed the object-store byte quota"};
  }
  std::sort(expected.begin(), expected.end(),
            [](const SyncRootedObject &left,
               const SyncRootedObject &right) {
              return object_less(left.object, right.object);
            });
  for (const SyncRootedObject &root : expected) {
    auto found = std::lower_bound(inventory.begin(), inventory.end(),
                                  root.object, object_less);
    if (found == inventory.end() || !same_object(*found, root.object)) {
      plan.missing.push_back(root);
      continue;
    }
    if (found->bytes != root.object.bytes) {
      plan.mismatched.push_back(SyncObjectMismatch{root, found->bytes});
      continue;
    }
    plan.rooted.push_back(root);
    plan.rooted_bytes += root.object.bytes;
  }
  for (const SyncObjectRecord &object : inventory) {
    auto found = std::lower_bound(
        expected.begin(), expected.end(), object,
        [](const SyncRootedObject &root, const SyncObjectRecord &candidate) {
          return object_less(root.object, candidate);
        });
    if (found == expected.end() || !same_object(found->object, object)) {
      plan.unreferenced.push_back(object);
      plan.unreferenced_bytes += object.bytes;
    }
  }
  return plan;
}

Result<SyncReachabilityPlan> plan_sync_reachability_from_store(
    const NamespacePolicy &policy,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium,
    std::shared_ptr<SyncGuardedStateWitness> witness) {
  auto transaction = SyncNamespaceTransaction::acquire(policy);
  if (!transaction.ok())
    return transaction.status();

  auto inventory =
      inspect_sync_object_records(policy, transaction.value());
  if (!inventory.ok())
    return inventory.status();
  return plan_sync_reachability_in_transaction(
      policy, expected_device, std::move(inventory.value()), sodium,
      transaction.value(), std::move(witness));
}

Result<SyncReachabilityPlan> plan_sync_reachability_in_transaction(
    const NamespacePolicy &policy,
    const security::SigningPublicKey &expected_device,
    std::vector<SyncObjectRecord> inventory, const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction,
    std::shared_ptr<SyncGuardedStateWitness> witness) {
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok())
    return held;
  if (witness) {
    const Status verified = witness->verify_read(policy, transaction);
    if (!verified.ok()) return verified;
  }

  auto roots =
      load_sync_rollback_roots(policy, expected_device, sodium, transaction);
  if (!roots.ok())
    return roots.status();
  auto rollback_head =
      make_sync_rollback_head(policy, expected_device, roots.value(), sodium);
  if (!rollback_head.ok())
    return rollback_head.status();
  SyncRollbackGuardStore guard(policy.root);
  auto guarded = guard.check(policy, rollback_head.value(), expected_device,
                             sodium, transaction);
  if (!guarded.ok())
    return guarded.status();

  auto plan = plan_sync_reachability(policy, expected_device, roots.value(),
                                     std::move(inventory), sodium);
  if (!plan.ok())
    return plan.status();
  plan.value().transaction_stable = true;
  plan.value().rollback_guard_consistent = true;
  return plan;
}

} // namespace iotox::sync
