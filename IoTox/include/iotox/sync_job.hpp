#pragma once

#include "iotox/status.hpp"
#include "iotox/sync_head.hpp"
#include "iotox/sync_publication.hpp"
#include "iotox/sync_transaction.hpp"

#include <cstdint>
#include <filesystem>
#include <functional>
#include <memory>
#include <span>
#include <vector>

namespace iotox::sync {

class SyncGuardedStateWitness;

struct SyncInstallSeams {
  // Product integration supplies the final cryptographic file hasher. Tests may
  // inject a deterministic hasher without loading optional runtime libraries.
  std::function<Result<Digest>(const std::filesystem::path &path)> hash_file;
  std::function<bool()> cancel_requested;
  // Optional publication-only semantic binding between the exact source pair
  // and the already-computed immutable identities. The range-v1 product path
  // uses this before either object or the signed HEAD can commit.
  std::function<Status(const std::filesystem::path &artifact,
                       const std::filesystem::path &manifest,
                       const Digest &artifact_digest,
                       std::uint64_t artifact_bytes,
                       std::uint64_t manifest_bytes)>
      validate_revision_sources;
  std::function<Result<std::shared_ptr<SyncGuardedStateWitness>>(
      const NamespacePolicy &policy)>
      guarded_state_witness;
};

struct SyncInstallRequest {
  NamespacePolicy policy;
  CandidateHead candidate;
  std::filesystem::path source_path;
  HeadAcceptancePolicy acceptance{};
  std::uint64_t copy_chunk_bytes{64U * 1024U};
};

struct SyncInstallResult {
  HeadAcceptanceResult head{};
  std::filesystem::path object_path;
  std::uint64_t bytes{0U};
  bool installed{false};
  bool activated{false};
};

struct SyncPublishJobRequest {
  NamespacePolicy policy;
  std::filesystem::path artifact_source_path;
  std::filesystem::path manifest_source_path;
  std::uint64_t copy_chunk_bytes{64U * 1024U};
};

struct SyncPublishJobResult {
  SignedHeadPublicationResult publication;
  std::filesystem::path artifact_object_path;
  std::filesystem::path manifest_object_path;
  bool artifact_installed{false};
  bool manifest_installed{false};
};

struct SyncObjectInventory {
  std::uint64_t objects{0U};
  std::uint64_t bytes{0U};
  std::uint64_t artifacts{0U};
  std::uint64_t manifests{0U};
};

enum class SyncObjectKind : std::uint8_t {
  artifact = 1U,
  manifest = 2U,
};

struct SyncObjectRecord {
  SyncObjectKind kind{SyncObjectKind::artifact};
  Digest identity{};
  std::uint64_t bytes{0U};

  [[nodiscard]] bool operator==(const SyncObjectRecord &) const = default;
};

struct SyncObjectStoreRepairResult {
  std::uint64_t inspected_objects{0U};
  std::uint64_t inspected_bytes{0U};
  std::uint64_t verified_objects{0U};
  std::uint64_t quarantined_objects{0U};
  std::uint64_t quarantined_bytes{0U};
  std::vector<SyncObjectRecord> quarantined;
};

struct SyncStagedObjectCommitResult {
  SyncObjectRecord object;
  std::filesystem::path staging_path;
  std::filesystem::path object_path;
  bool installed{false};
};

struct SyncAttemptPartial {
  std::filesystem::path path;
  std::uint64_t bytes{0U};

  [[nodiscard]] bool operator==(const SyncAttemptPartial &) const = default;
};

// Returns the sole digest-derived immutable-store path for an object record.
// Callers must still hold the namespace transaction while trusting its shape
// or contents.
[[nodiscard]] std::filesystem::path
sync_object_path(const NamespacePolicy &policy,
                 const SyncObjectRecord &object);

// Creates only the strict private namespace directories and returns the sole
// no-clobber destination owned by this attempt. FileTransferManager may use
// this path as its receive destination; callers cannot nominate another path.
[[nodiscard]] Result<std::filesystem::path> prepare_sync_attempt_staging(
    const NamespacePolicy &policy, std::uint64_t attempt_id,
    const SyncObjectRecord &object,
    const SyncNamespaceTransaction &transaction);

// Creates the exact empty private staging inode used by a resumable upper
// protocol receive. Unlike prepare_sync_attempt_staging(), this has a durable
// filesystem effect and fsyncs both inode and containing directory.
[[nodiscard]] Result<SyncAttemptPartial> create_sync_attempt_partial(
    const NamespacePolicy &policy, std::uint64_t attempt_id,
    const SyncObjectRecord &object,
    const SyncNamespaceTransaction &transaction);

[[nodiscard]] Result<SyncAttemptPartial> inspect_sync_attempt_partial(
    const NamespacePolicy &policy, std::uint64_t attempt_id,
    const SyncObjectRecord &object,
    const SyncNamespaceTransaction &transaction);

// Atomically transfers one strict incomplete partial from a fenced attempt to
// a fresh attempt in the same namespace. Linux RENAME_NOREPLACE prevents
// substitution; exact retries accept only the already-moved expected shape.
[[nodiscard]] Result<SyncAttemptPartial> handoff_sync_attempt_partial(
    const NamespacePolicy &policy, std::uint64_t prior_attempt_id,
    std::uint64_t next_attempt_id, const SyncObjectRecord &object,
    const SyncNamespaceTransaction &transaction);

// Startup-only reconciliation for canonical attempt paths whose ID is proven
// burned by the signed journal high-water but is not in its active set.
[[nodiscard]] Status cleanup_inactive_sync_attempt_partials(
    const NamespacePolicy &policy, std::uint64_t high_attempt_id,
    std::span<const std::uint64_t> active_attempt_ids,
    const SyncNamespaceTransaction &transaction);

// Revalidates and hashes the completed private staging file, commits it to the
// digest-named object store under the namespace transaction, then removes the
// attempt path. Signed HEAD acceptance and activation remain separate.
[[nodiscard]] Result<SyncStagedObjectCommitResult> commit_sync_attempt_staging(
    const NamespacePolicy &policy, std::uint64_t attempt_id,
    const SyncObjectRecord &object,
    const SyncNamespaceTransaction &transaction,
    const SyncInstallSeams &seams,
    std::uint64_t copy_chunk_bytes = 64U * 1024U);

// Idempotently removes only the exact private regular file derived from this
// attempt. An unexpected file shape fails closed and is never deleted.
[[nodiscard]] Status discard_sync_attempt_staging(
    const NamespacePolicy &policy, std::uint64_t attempt_id,
    const SyncNamespaceTransaction &transaction);

// Revalidates one digest-named final object against strict store shape, exact
// size, and content digest. Absence is reported as ErrorCode::not_found.
[[nodiscard]] Status verify_sync_object(
    const NamespacePolicy &policy, const SyncObjectRecord &object,
    const SyncNamespaceTransaction &transaction,
    const SyncInstallSeams &seams);

// Stages one already-authorized local artifact into the namespace object store
// and commits the accepted HEAD last. This function never changes activation
// state; convergence and activation remain separate authority boundaries.
[[nodiscard]] Result<SyncInstallResult>
install_local_artifact(const SyncInstallRequest &request,
                       const security::DeviceIdentity &identity,
                       const security::Sodium &sodium,
                       const SyncInstallSeams &seams);

// Verifies and commits both immutable inputs before advancing the stable-device
// signed publisher HEAD. Cancellation or any object failure leaves the HEAD
// unchanged; successfully committed unreferenced objects are safe to reuse.
[[nodiscard]] Result<SyncPublishJobResult> publish_local_revision(
    const SyncPublishJobRequest &request,
    const security::DeviceIdentity &identity, const security::Sodium &sodium,
    SignedHeadStore &store, const SyncInstallSeams &seams);

// Strictly inventories the flat digest-named object directory and refuses
// malformed entries or a store already beyond its configured byte/object cap.
[[nodiscard]] Result<SyncObjectInventory>
inspect_sync_object_store(const NamespacePolicy &policy);
[[nodiscard]] Result<SyncObjectInventory>
inspect_sync_object_store(const NamespacePolicy &policy,
                          const SyncNamespaceTransaction &transaction);

// Returns one canonical kind/identity-sorted record per strict inventory
// entry. Paths are intentionally not retained as authority-bearing state.
[[nodiscard]] Result<std::vector<SyncObjectRecord>>
inspect_sync_object_records(const NamespacePolicy &policy);
[[nodiscard]] Result<std::vector<SyncObjectRecord>>
inspect_sync_object_records(const NamespacePolicy &policy,
                            const SyncNamespaceTransaction &transaction);

// Verifies every strict digest-named final object and quarantines only objects
// whose bytes do not match their filename identity. Unsafe shapes and
// unexpected names remain terminal errors, not deletion candidates.
[[nodiscard]] Result<SyncObjectStoreRepairResult>
repair_sync_object_store(const NamespacePolicy &policy,
                         const SyncInstallSeams &seams);
[[nodiscard]] Result<SyncObjectStoreRepairResult>
repair_sync_object_store(const NamespacePolicy &policy,
                         const SyncNamespaceTransaction &transaction,
                         const SyncInstallSeams &seams);

} // namespace iotox::sync
