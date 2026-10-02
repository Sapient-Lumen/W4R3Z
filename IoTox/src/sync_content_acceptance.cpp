#include "iotox/sync_content_acceptance.hpp"

#include "iotox/sync_content_workspace.hpp"

#include <algorithm>
#include <filesystem>
#include <optional>
#include <sys/stat.h>
#include <utility>

namespace iotox::sync {
namespace {

class WorkspaceRemoval final {
public:
  WorkspaceRemoval(const NamespacePolicy &policy,
                   const SyncNamespaceTransaction &transaction,
                   std::filesystem::path path)
      : policy_(&policy), transaction_(&transaction), path_(std::move(path)) {}
  ~WorkspaceRemoval() {
    if (!path_.empty()) {
      static_cast<void>(remove_sync_content_workspace(
          *policy_, *transaction_, SyncContentWorkspaceClass::reconstruction,
          path_));
    }
  }
  WorkspaceRemoval(const WorkspaceRemoval &) = delete;
  WorkspaceRemoval &operator=(const WorkspaceRemoval &) = delete;

private:
  const NamespacePolicy *policy_{nullptr};
  const SyncNamespaceTransaction *transaction_{nullptr};
  std::filesystem::path path_;
};

bool cancelled(const SyncContentAcceptanceSeams &seams) {
  return seams.cancel_requested && seams.cancel_requested();
}

std::optional<SyncContentStoredObject>
find_object(const SyncContentStoreInventory &inventory, const Digest &object) {
  const auto found = std::lower_bound(
      inventory.records.begin(), inventory.records.end(), object,
      [](const SyncContentStoredObject &record, const Digest &candidate) {
        return record.object < candidate;
      });
  return found != inventory.records.end() && found->object == object
             ? std::optional<SyncContentStoredObject>{*found}
             : std::nullopt;
}

} // namespace

Result<std::size_t> cleanup_sync_content_reconstruction_staging(
    const NamespacePolicy &policy,
    const SyncNamespaceTransaction &transaction) {
  return cleanup_sync_content_workspaces(
      policy, transaction, SyncContentWorkspaceClass::reconstruction);
}

Result<SyncContentAcceptanceResult>
reconstruct_and_accept_sync_content_revision(
    const NamespacePolicy &policy, const SignedHead &head,
    SyncContentCoordinator &coordinator,
    const security::DeviceIdentity &identity, const security::Sodium &sodium,
    SyncContentAcceptanceConfig config, SyncContentAcceptanceSeams seams) {
  const Status valid_policy = validate_namespace_policy(policy);
  if (!valid_policy.ok())
    return valid_policy;
  if (policy.engine != Engine::content_v2 || config.io_buffer_bytes == 0U ||
      config.io_buffer_bytes > policy.quotas.maximum_staging_bytes ||
      head.artifact_bytes > policy.quotas.maximum_staging_bytes) {
    return Status{ErrorCode::invalid_argument,
                  "content acceptance configuration is invalid"};
  }
  auto candidate = verified_candidate_head(policy, head, sodium);
  if (!candidate)
    return candidate.status();
  if (cancelled(seams)) {
    return Status{ErrorCode::unavailable,
                  "content acceptance cancelled before reconstruction"};
  }

  auto transaction = SyncNamespaceTransaction::acquire(policy);
  if (!transaction)
    return transaction.status();
  const Status store_prepared =
      prepare_sync_content_store(policy, transaction.value());
  if (!store_prepared.ok())
    return store_prepared;
  const Status staging_prepared =
      prepare_sync_content_staging(policy, transaction.value());
  if (!staging_prepared.ok())
    return staging_prepared;
  auto cleaned =
      cleanup_sync_content_reconstruction_staging(policy, transaction.value());
  if (!cleaned)
    return cleaned.status();

  auto root = resolve_sync_content_object(
      policy, head, SyncContentObjectKind::root_manifest, 0U);
  if (!root)
    return root.status();
  auto inventory =
      inspect_sync_content_store(policy, transaction.value(), true);
  if (!inventory)
    return inventory.status();
  const auto present = find_object(inventory.value(), head.artifact);
  if (present && present->object_bytes != head.artifact_bytes) {
    return Status{ErrorCode::protocol_error,
                  "content whole artifact CAS size conflicts with HEAD"};
  }

  SyncContentAcceptanceResult result;
  result.reconstruction.artifact = head.artifact;
  result.reconstruction.artifact_bytes = head.artifact_bytes;
  result.artifact_commit.object_path =
      sync_content_object_path(policy, head.artifact);
  result.artifact_commit.object_bytes = head.artifact_bytes;
  if (present) {
    result.artifact_commit.reused = true;
    result.artifact_commit.bytes_verified = head.artifact_bytes;
  } else {
    auto workspace = create_sync_content_workspace(
        policy, transaction.value(), SyncContentWorkspaceClass::reconstruction);
    if (!workspace)
      return workspace.status();
    WorkspaceRemoval remove_workspace(policy, transaction.value(),
                                      workspace.value());
    const std::filesystem::path output = workspace.value() / "artifact.part";
    auto reconstructed = coordinator.reconstruct(output);
    if (!reconstructed)
      return reconstructed.status();
    if (reconstructed.value().artifact != head.artifact ||
        reconstructed.value().artifact_bytes != head.artifact_bytes) {
      return Status{ErrorCode::protocol_error,
                    "content reconstruction conflicts with signed HEAD"};
    }
    if (::chmod(output.c_str(), static_cast<mode_t>(0600)) != 0) {
      return Status{ErrorCode::io_error,
                    "unable to secure reconstructed content artifact"};
    }
    if (cancelled(seams)) {
      return Status{ErrorCode::unavailable,
                    "content acceptance cancelled before artifact commit"};
    }
    SyncContentCommitConfig commit;
    commit.io_buffer_bytes = config.io_buffer_bytes;
    commit.fsync_on_commit = config.fsync_on_commit;
    auto committed =
        commit_sync_content_staging(policy, head.artifact, head.artifact_bytes,
                                    output, transaction.value(), commit);
    if (!committed)
      return committed.status();
    result.reconstruction = reconstructed.value();
    result.artifact_commit = committed.value();
    result.reconstructed = true;
  }

  if (cancelled(seams)) {
    return Status{ErrorCode::unavailable,
                  "content acceptance cancelled before signed HEAD"};
  }
  AcceptedHeadStore accepted(policy.root, seams.guarded_state_witness);
  auto acceptance = accepted.accept(policy, candidate.value(), identity, sodium,
                                    {}, transaction.value());
  if (!acceptance)
    return acceptance.status();
  if (!acceptance.value().accepted() &&
      acceptance.value().decision != HeadAcceptanceDecision::duplicate) {
    return Status{ErrorCode::protocol_error,
                  "content signed HEAD was refused after reconstruction"};
  }
  result.acceptance = acceptance.value();
  return result;
}

} // namespace iotox::sync
