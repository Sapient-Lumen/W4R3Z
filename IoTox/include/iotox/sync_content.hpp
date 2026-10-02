#pragma once

#include "iotox/security/authority.hpp"
#include "iotox/security/authority_session.hpp"
#include "iotox/status.hpp"
#include "iotox/sync_content_wire.hpp"
#include "iotox/sync_head.hpp"
#include "iotox/sync_job.hpp"
#include "iotox/sync_namespace.hpp"
#include "iotox/sync_publication.hpp"

#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <functional>
#include <memory>
#include <optional>
#include <span>
#include <vector>

namespace iotox::sync {

using SyncContentSourceId = std::uint64_t;

enum class SyncContentPhase : std::uint8_t {
  unprepared = 1U,
  manifest_pages = 2U,
  artifact_chunks = 3U,
  complete = 4U,
};

enum class SyncContentFailure : std::uint8_t {
  retry_source = 1U,
  object_absent = 2U,
  permanent = 3U,
};

struct SyncContentConfig {
  std::size_t maximum_window_objects{4096U};
  std::size_t maximum_page_window_objects{256U};
  std::size_t workspace_budget_bytes{64U * 1024U * 1024U};
  std::size_t object_io_buffer_bytes{256U * 1024U};
  std::size_t manifest_buffer_bytes{64U * 1024U};
  bool verify_local_objects{true};
  bool fsync_on_commit{true};
};

struct SyncContentSource {
  SyncContentSourceId source_id{0U};
  Digest advertised_head_record{};
  security::PeerAuthoritySnapshot authority;
  std::uint16_t maximum_lanes{1U};
  std::uint64_t useful_bytes_per_second{0U};
  std::uint32_t recent_failures{0U};
  bool content_transfer_negotiated{false};
};

struct SyncContentAssignment {
  std::uint64_t request_id{0U};
  SyncContentSourceId source_id{0U};
  SyncContentObjectKind kind{SyncContentObjectKind::artifact_chunk};
  Digest object{};
  std::uint64_t object_bytes{0U};
  std::uint64_t logical_index{0U};
  std::filesystem::path staging_path;

  [[nodiscard]] bool operator==(const SyncContentAssignment &) const = default;
};

struct SyncContentSnapshot {
  SyncContentPhase phase{SyncContentPhase::unprepared};
  std::size_t sources{0U};
  std::size_t active_requests{0U};
  std::uint64_t assignments{0U};
  std::uint64_t request_failures{0U};
  std::uint64_t verification_failures{0U};
  std::uint64_t fenced_requests{0U};
  std::uint64_t page_objects_reused{0U};
  std::uint64_t page_objects_fetched{0U};
  std::uint64_t chunk_objects_reused{0U};
  std::uint64_t chunk_objects_fetched{0U};
  std::uint64_t chunk_bytes_reused{0U};
  std::uint64_t chunk_bytes_fetched{0U};
  std::size_t resident_bytes{0U};
  SyncContentObjectKind window_kind{SyncContentObjectKind::artifact_chunk};
  std::uint64_t window_first_object{0U};
  std::uint32_t window_object_count{0U};
};

struct SyncContentAvailabilityDescriptor {
  SyncContentObjectKind kind{SyncContentObjectKind::artifact_chunk};
  std::uint64_t first_object{0U};
  std::uint32_t object_count{0U};
  std::uint32_t available_objects{0U};
  std::vector<std::uint8_t> availability;
};

struct SyncContentStoredObject {
  Digest object{};
  std::uint64_t object_bytes{0U};

  [[nodiscard]] bool
  operator==(const SyncContentStoredObject &) const = default;
};

struct SyncContentStoreInventory {
  std::uint64_t objects{0U};
  std::uint64_t bytes{0U};
  std::vector<SyncContentStoredObject> records;
};

struct SyncCombinedStoreInventory {
  SyncObjectInventory flat;
  SyncContentStoreInventory content;
  std::uint64_t objects{0U};
  std::uint64_t bytes{0U};
};

struct SyncContentCommitConfig {
  std::size_t io_buffer_bytes{256U * 1024U};
  bool fsync_on_commit{true};
};

struct SyncContentCommitResult {
  std::filesystem::path object_path;
  std::uint64_t object_bytes{0U};
  std::uint64_t bytes_verified{0U};
  std::uint64_t bytes_copied{0U};
  bool installed{false};
  bool reused{false};
};

struct SyncContentReconstruction {
  Digest artifact{};
  std::uint64_t artifact_bytes{0U};
  std::uint64_t chunks_read{0U};
};

struct SyncContentObjectDescriptor {
  SyncContentObjectKind kind{SyncContentObjectKind::artifact_chunk};
  Digest object{};
  std::uint64_t object_bytes{0U};
  std::uint64_t logical_index{0U};
  std::filesystem::path path;

  [[nodiscard]] bool
  operator==(const SyncContentObjectDescriptor &) const = default;
};

enum class SyncContentRootSource : std::uint8_t {
  published = 1U << 0U,
  accepted = 1U << 1U,
  activated = 1U << 2U,
  retained = 1U << 3U,
  replica = 1U << 4U,
};

struct SyncContentRootedObject {
  SyncContentStoredObject object;
  std::uint8_t source_mask{0U};

  [[nodiscard]] bool
  operator==(const SyncContentRootedObject &) const = default;
};

struct SyncContentObjectMismatch {
  SyncContentRootedObject expected;
  std::uint64_t observed_bytes{0U};

  [[nodiscard]] bool
  operator==(const SyncContentObjectMismatch &) const = default;
};

struct SyncContentReachabilityPlan {
  std::vector<SyncContentRootedObject> rooted;
  std::vector<SyncContentRootedObject> missing;
  std::vector<SyncContentObjectMismatch> mismatched;
  std::vector<SyncContentStoredObject> unreferenced;
  std::uint64_t rooted_bytes{0U};
  std::uint64_t unreferenced_bytes{0U};
  bool traversal_complete{false};
  bool transaction_stable{false};
  bool rollback_guard_consistent{false};

  [[nodiscard]] bool consistent() const noexcept {
    return traversal_complete && missing.empty() && mismatched.empty();
  }
};

struct SyncContentRepairResult {
  std::uint64_t inspected_objects{0U};
  std::uint64_t inspected_bytes{0U};
  std::uint64_t verified_objects{0U};
  std::uint64_t quarantined_objects{0U};
  std::uint64_t quarantined_bytes{0U};
  std::vector<SyncContentStoredObject> quarantined;
};

struct SyncContentMaintenanceSeams {
  std::function<bool()> cancel_requested;
  std::function<Status(std::size_t, const SyncContentStoredObject &)>
      before_move;
};

struct SyncContentGcOutcome {
  Status status;
  std::optional<SyncContentReachabilityPlan> plan;
  std::vector<SyncContentStoredObject> moved;
  std::uint64_t moved_bytes{0U};
  std::uint64_t durable_objects{0U};
  std::uint64_t durable_bytes{0U};
  bool quarantine_created{false};
  bool cancelled{false};

  [[nodiscard]] bool ok() const noexcept { return status.ok(); }
};

// The first content-v2 store convention is deliberately distinct from the
// whole-object v1 directory. Its digest fanout is owned by toxsync; Agent-side
// quota/reachability integration remains a prerequisite before advertisement.
[[nodiscard]] std::filesystem::path
sync_content_store_root(const NamespacePolicy &policy);
[[nodiscard]] std::filesystem::path
sync_content_staging_root(const NamespacePolicy &policy);
[[nodiscard]] std::filesystem::path
sync_content_object_path(const NamespacePolicy &policy, const Digest &object);

// Creates or validates the owner-private CAS root under one namespace
// transaction. Digest fanout directories remain beneath this 0700 boundary.
[[nodiscard]] Status
prepare_sync_content_store(const NamespacePolicy &policy,
                           const SyncNamespaceTransaction &transaction);
[[nodiscard]] Status
prepare_sync_content_staging(const NamespacePolicy &policy,
                             const SyncNamespaceTransaction &transaction);

// Strict physical inventory. The optional verification pass rehashes every
// object against its 64-hex fanout identity. The combined view counts both
// legacy flat objects and CAS objects against the one namespace quota.
[[nodiscard]] Result<SyncContentStoreInventory>
inspect_sync_content_store(const NamespacePolicy &policy,
                           bool verify_objects = false);
[[nodiscard]] Result<SyncContentStoreInventory>
inspect_sync_content_store(const NamespacePolicy &policy,
                           const SyncNamespaceTransaction &transaction,
                           bool verify_objects = false);
[[nodiscard]] Result<SyncCombinedStoreInventory>
inspect_sync_combined_store(const NamespacePolicy &policy,
                            bool verify_content_objects = false);

// Authenticates every persisted revision root and rollback guard under one
// namespace transaction, then walks each root/page/chunk manifest graph. An
// incomplete root or page prevents unreferenced classification, so GC cannot
// turn missing metadata into deletion authority.
[[nodiscard]] Result<SyncContentReachabilityPlan>
plan_sync_content_reachability_from_store(
    const NamespacePolicy &policy,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium,
    std::shared_ptr<SyncGuardedStateWitness> witness = {});

// Explicit corruption repair. Every strict CAS object is rehashed; only a
// digest/name mismatch is moved to owner-private quarantine. Unsafe shapes and
// unexpected entries remain terminal failures.
[[nodiscard]] Result<SyncContentRepairResult>
repair_sync_content_store(const NamespacePolicy &policy,
                          const SyncContentMaintenanceSeams &seams = {});

// Replans authenticated reachability while holding the transaction and moves
// only exact unreferenced identities to quarantine. There is intentionally no
// purge or unlink mode.
[[nodiscard]] SyncContentGcOutcome quarantine_unreferenced_sync_content(
    const NamespacePolicy &policy,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium,
    const SyncContentMaintenanceSeams &seams = {},
    std::shared_ptr<SyncGuardedStateWitness> witness = {});
[[nodiscard]] Result<SyncCombinedStoreInventory>
inspect_sync_combined_store(const NamespacePolicy &policy,
                            const SyncNamespaceTransaction &transaction,
                            bool verify_content_objects = false);

// Publishes one exact private content staging file through a verified copy.
// The transaction serializes prospective flat-plus-CAS quota accounting and
// the source is consumed only after immutable publication succeeds.
[[nodiscard]] Result<SyncContentCommitResult>
commit_sync_content_staging(const NamespacePolicy &policy, const Digest &object,
                            std::uint64_t object_bytes,
                            const std::filesystem::path &staging_path,
                            const SyncNamespaceTransaction &transaction,
                            SyncContentCommitConfig config = {});

// Resolves one logical page/chunk from the locally verified manifest named by
// HEAD, revalidates its exact CAS object, and returns no caller-selected path.
[[nodiscard]] Result<SyncContentObjectDescriptor>
resolve_sync_content_object(const NamespacePolicy &policy,
                            const SignedHead &head, SyncContentObjectKind kind,
                            std::uint64_t logical_index);

[[nodiscard]] Result<SyncContentAvailabilityDescriptor>
resolve_sync_content_availability(const NamespacePolicy &policy,
                                  const SignedHead &head,
                                  SyncContentObjectKind kind,
                                  std::uint64_t first_object,
                                  std::uint32_t object_count);

// Revalidates the immutable whole artifact and root manifest named by an
// accepted content-v2 HEAD, including the manifest's embedded artifact
// identity. This is the engine-specific semantic gate used immediately before
// a manual activation pointer is advanced.
[[nodiscard]] Status
verify_sync_content_revision(const NamespacePolicy &policy,
                             const AcceptedHead &head,
                             const std::filesystem::path &artifact,
                             const std::filesystem::path &root_manifest);

// Transport-neutral content-v2 coordinator. One already verified AcceptedHead
// remains frozen for the lifetime of the coordinator. Every candidate source
// is separately admitted against current exact-v3 authority and the identical
// signed-HEAD record digest. The coordinator assigns only immutable objects;
// callers still own FileIds, transport cancellation, durable attempt records,
// accepted-HEAD-last persistence, and activation.
class SyncContentCoordinator final {
public:
  SyncContentCoordinator(NamespacePolicy policy, AcceptedHead expected_head,
                         std::filesystem::path manifest_path,
                         std::filesystem::path content_store_root,
                         std::filesystem::path staging_root,
                         SyncContentConfig config = {});
  ~SyncContentCoordinator();
  SyncContentCoordinator(SyncContentCoordinator &&) noexcept;
  SyncContentCoordinator &operator=(SyncContentCoordinator &&) noexcept;
  SyncContentCoordinator(const SyncContentCoordinator &) = delete;
  SyncContentCoordinator &operator=(const SyncContentCoordinator &) = delete;

  [[nodiscard]] Status prepare();
  [[nodiscard]] Status
  upsert_complete_source(const SyncContentSource &source,
                         const security::AuthoritySnapshot &current_authority);
  [[nodiscard]] Status
  upsert_source_window(const SyncContentSource &source,
                       const security::AuthoritySnapshot &current_authority,
                       SyncContentObjectKind kind, std::uint64_t first_object,
                       std::uint32_t object_count,
                       std::span<const std::uint8_t> availability);
  // Returns every transport assignment fenced by disappearance. Callers must
  // cancel/retire those exact FileIds before removing staging in a live Agent.
  [[nodiscard]] Result<std::vector<SyncContentAssignment>>
  remove_source(SyncContentSourceId source_id);

  [[nodiscard]] Result<std::optional<SyncContentAssignment>>
  next(std::uint64_t request_id);
  [[nodiscard]] std::optional<SyncContentAssignment>
  assignment(std::uint64_t request_id) const;
  [[nodiscard]] Status
  commit(std::uint64_t request_id,
         const std::filesystem::path &completed_staging_path = {});
  [[nodiscard]] Status fail(std::uint64_t request_id,
                            SyncContentFailure failure);
  [[nodiscard]] Result<bool> advance_window();
  [[nodiscard]] bool complete() const;
  [[nodiscard]] Result<SyncContentReconstruction>
  reconstruct(const std::filesystem::path &output_path);
  [[nodiscard]] SyncContentSnapshot snapshot() const;

private:
  class Impl;
  std::unique_ptr<Impl> impl_;
};

[[nodiscard]] std::string_view
sync_content_phase_name(SyncContentPhase phase) noexcept;

} // namespace iotox::sync
