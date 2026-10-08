#pragma once

#if !defined(_WIN32)

#include "sync_replica_deployment_binding.hpp"
#include "sync_replica_deployment_manifest.hpp"
#include "sync_replica_file_payload_store.hpp"
#include "sync_replica_folder_observer.hpp"
#include "sync_replica_historical_version_query.hpp"
#include "sync_replica_model.hpp"
#include "sync_replica_selective_sync_policy.hpp"
#include "sync_replica_sqlite_owner.hpp"
#include "sync_sqlite_handle_slot.hpp"

#include <cstdint>
#include <filesystem>
#include <memory>
#include <optional>
#include <string>
#include <string_view>
#include <vector>

namespace anonsync {

inline constexpr std::uint64_t kSyncReplicaFolderScanMaxCatalogEntries =
    1000000U;
inline constexpr std::uint64_t kSyncReplicaFolderScanMaxPayloadBytes =
    kSyncReplicaDeploymentManifestMaxPayloadBytes;

enum class SyncReplicaFolderCatalogOpenDisposition : std::uint8_t {
    ExistingOnly = 1,
    CreateIfMissing = 2,
};

struct SyncReplicaFolderScanLimits final {
    std::uint64_t max_catalog_entries = 100000U;
    std::uint64_t max_catalog_path_bytes = 64ULL * 1024ULL * 1024ULL;
    std::uint64_t max_payload_bytes = 4ULL * 1024ULL * 1024ULL;

    bool operator==(const SyncReplicaFolderScanLimits&) const = default;
};

void validate_sync_replica_folder_scan_limits_or_throw(
    const SyncReplicaFolderScanLimits& limits);

struct SyncReplicaFolderCatalogEntry final {
    std::string canonical_path;
    SyncReplicaValueKind kind = SyncReplicaValueKind::File;
    std::uint64_t size_bytes = 0U;
    std::string content_sha256;
    std::string operation_id;
    std::string source_snapshot_sha256;
    std::uint64_t last_seen_generation = 0U;

    bool operator==(const SyncReplicaFolderCatalogEntry&) const = default;
};

struct SyncReplicaFolderCatalogSnapshot final {
    std::string folder_id;
    std::string absolute_root_path;
    std::string root_attestation_digest;
    SyncReplicaFolderScanLimits limits;
    std::uint64_t state_generation = 0U;
    std::vector<SyncReplicaFolderCatalogEntry> entries;
    // The content digest retains the exact v5 catalog projection. The v6
    // catalog digest additionally binds the bounded selective-sync policy,
    // allowing a policy-only mutation without rehashing a million catalog rows.
    std::string content_catalog_digest;
    SyncReplicaSelectiveSyncPolicy selective_sync_policy;
    // Nonzero only while the first complete scan after this exact policy
    // generation is still withholding absence inference. This prevents a
    // newly materialized path from being tombstoned before remote rehydration.
    std::uint64_t selective_sync_absence_fence_generation = 0U;
    std::string catalog_digest;

    bool operator==(const SyncReplicaFolderCatalogSnapshot&) const = default;
};

// Bounded policy/cutpoint observation for operator inspection and replacement.
// Unlike SyncReplicaFolderCatalogSnapshot, this structure never materializes
// one object per catalog entry. It carries only persisted aggregate content
// identity plus the complete at-most-1,024-rule selection policy.
struct SyncReplicaFolderSelectiveSyncSnapshot final {
    std::string folder_id;
    std::string absolute_root_path;
    SyncReplicaFolderScanLimits limits;
    std::uint64_t state_generation = 0U;
    std::uint64_t catalog_entry_count = 0U;
    std::uint64_t catalog_path_bytes = 0U;
    std::string content_catalog_digest;
    SyncReplicaSelectiveSyncPolicy policy;
    std::uint64_t absence_inference_fence_generation = 0U;
    std::string catalog_digest;

    bool operator==(const SyncReplicaFolderSelectiveSyncSnapshot&) const =
        default;
};

// Offline exact-current-schema observations for one deployment-bound catalog
// image. They validate the persisted canonical root pathname and retained root
// attestation digest without opening the configured files root. The named form
// attests a descriptor-rooted operational read-only database; the detached form
// attests a sealed filename-free read-only image. Neither form initializes,
// migrates, scans, or mutates catalog state.
[[nodiscard]] SyncReplicaFolderCatalogSnapshot
inspect_sync_replica_folder_catalog_snapshot_read_only_without_root_access_or_throw(
    SyncSqliteDbHandleSlot& db,
    const SyncReplicaSqliteDeploymentBinding& catalog_binding,
    std::string folder_id,
    std::filesystem::path expected_root_path,
    std::string label =
        "sync replica folder-catalog offline SQLite inspection");

[[nodiscard]] SyncReplicaFolderCatalogSnapshot
inspect_sync_replica_folder_catalog_snapshot_in_attested_detached_read_only_image_without_root_access_or_throw(
    SyncSqliteDbHandleSlot& db,
    const SyncReplicaSqliteDeploymentBinding& catalog_binding,
    std::string folder_id,
    std::filesystem::path expected_root_path,
    std::string label =
        "sync replica detached folder-catalog offline SQLite inspection");


// Named-database selective-sync inspection and replacement for an offline
// deployment ceremony. Both paths attest the exact folder-catalog binding and
// persisted root pathname without opening the synchronized files root. The
// read-only form requires a genuinely read-only SQLite connection. The writer
// form requires an existing writable operational database and changes only the
// bounded policy plus scan/apply scheduling journals; catalog content authority
// and state_generation remain exact. A higher-level caller must hold the
// deployment singleton before invoking the writer form.
[[nodiscard]] SyncReplicaFolderSelectiveSyncSnapshot
inspect_sync_replica_folder_selective_sync_snapshot_read_only_without_root_access_or_throw(
    SyncSqliteDbHandleSlot& db,
    const SyncReplicaSqliteDeploymentBinding& catalog_binding,
    std::string folder_id,
    std::filesystem::path expected_root_path,
    std::string label =
        "sync replica selective-sync offline SQLite inspection");

[[nodiscard]] SyncReplicaFolderSelectiveSyncSnapshot
replace_sync_replica_folder_selective_sync_policy_without_root_access_or_throw(
    SyncSqliteDbHandleSlot& db,
    const SyncReplicaSqliteDeploymentBinding& catalog_binding,
    std::string folder_id,
    std::filesystem::path expected_root_path,
    SyncReplicaSelectiveSyncMode default_mode,
    std::vector<SyncReplicaSelectiveSyncRule> rules,
    std::string label =
        "sync replica selective-sync offline SQLite replacement");

// Exact durable continuation head for bounded folder work. The authenticated
// local scan fields authorize only rooted scan continuation and, after a full
// epoch, conservative absence adjudication. The historically named remote
// apply cursor is weaker scheduling state: it acknowledges the last completely
// classified post-scan path after every selected effect has committed. A
// cutpoint-bound sweep records how much of one stable catalog/replica projection
// has been acknowledged and whether any segment was unresolved. Rotating after
// both effects and safe deferrals prevents unavailable, conflicted, or
// already-settled prefixes from monopolizing every bounded pass. None of these
// fields is replicated folder content. Exposing them lets higher-level process
// cutpoints report real crash-surviving continuation progress instead of
// misclassifying it as a no-op.
struct SyncReplicaFolderScanProgressSnapshot final {
    std::uint64_t scan_epoch = 0U;
    std::string resume_after_path;
    std::uint64_t seen_path_count = 0U;
    std::uint64_t seen_path_bytes = 0U;
    std::string seen_chain_digest;
    std::string remote_apply_resume_after_path;
    std::string remote_inspection_sweep_basis_digest;
    std::string remote_inspection_sweep_started_after_path;
    std::uint64_t remote_inspection_sweep_seen_path_count = 0U;
    bool remote_inspection_sweep_had_unresolved_paths = false;

    bool operator==(
        const SyncReplicaFolderScanProgressSnapshot&) const = default;
};

enum class SyncReplicaFolderScanDisposition : std::uint8_t {
    Published = 1,
    AdoptedVisibleOperation = 2,
    CatalogNoOp = 3,
    CatalogRefreshed = 4,
};

struct SyncReplicaFolderScanResult final {
    SyncReplicaFolderScanDisposition disposition =
        SyncReplicaFolderScanDisposition::CatalogNoOp;
    SyncReplicaFolderCatalogEntry entry;
    std::optional<SyncReplicaOperation> published_operation;
    // Present only when one target-file observation atomically minted the
    // destination File and source Tombstone causal pair. published_operation is
    // the destination File for compatibility with existing single-path callers.
    std::optional<SyncReplicaIdentityPreservingRename>
        published_identity_preserving_rename;
    // Non-authoritative work accounting. True only when a direct single-path
    // commit re-opened one exact retained payload through the bounded targeted
    // lane and therefore skipped descriptor-based payload admission. The
    // targeted access and exact-inode payload capability remain live through
    // replica and catalog publication.
    bool targeted_payload_reuse = false;

    bool operator==(const SyncReplicaFolderScanResult&) const = default;
};

enum class SyncReplicaFolderApplyDisposition : std::uint8_t {
    Applied = 1,
    AdoptedExactTarget = 2,
    CatalogNoOp = 3,
};

struct SyncReplicaFolderApplyResult final {
    SyncReplicaFolderApplyDisposition disposition =
        SyncReplicaFolderApplyDisposition::CatalogNoOp;
    SyncReplicaFolderCatalogEntry entry;
    SyncReplicaOperation operation;

    bool operator==(const SyncReplicaFolderApplyResult&) const = default;
};

// One independently counted reachability class. File-operation counts are
// reference counts. Distinct content is exact (SHA-256, declared-size)
// identity. The same immutable content may appear in more than one class, so
// class distinct/present/missing totals deliberately overlap; retained_union
// deduplicates them across all retained file evidence.
struct SyncReplicaHistoricalVersionPayloadReachabilityClass final {
    std::uint64_t file_operation_count = 0U;
    std::uint64_t distinct_content_count = 0U;
    std::uint64_t present_content_count = 0U;
    std::uint64_t present_content_bytes = 0U;
    std::uint64_t missing_content_count = 0U;

    bool operator==(
        const SyncReplicaHistoricalVersionPayloadReachabilityClass&) const =
        default;
};

// Share-global diagnostic accounting over every retained file operation and
// the exact complete payload snapshot already paid for by exact history
// inspection. current_visible and superseded_active partition active file
// operations; inactive_evidence contains pending/quarantined file operations.
// Unreferenced means only "not named by any retained file operation at this
// bracketed cutpoint." It is not reclaimable authority: catalogs, in-flight
// transfers, pass snapshots, range/mutation pins, retention policy, grace,
// writer fencing, and a crash-safe collector are outside this object. Explicit
// user pins are measured as an overlapping root class, but no payload is deleted
// by history inspection.
struct SyncReplicaHistoricalVersionPayloadReachability final {
    std::uint64_t payload_entry_count = 0U;
    std::uint64_t payload_indexed_bytes = 0U;
    SyncReplicaHistoricalVersionPayloadReachabilityClass current_visible;
    SyncReplicaHistoricalVersionPayloadReachabilityClass superseded_active;
    SyncReplicaHistoricalVersionPayloadReachabilityClass inactive_evidence;
    // Overlapping local policy roots. Every pinned operation also belongs to
    // exactly one of the three retained evidence classes above; this class is
    // therefore diagnostic overlap and is not added to retained_union.
    SyncReplicaHistoricalVersionPayloadReachabilityClass explicit_pins;
    SyncReplicaHistoricalVersionPayloadReachabilityClass retained_union;
    std::uint64_t unreferenced_payload_count = 0U;
    std::uint64_t unreferenced_payload_bytes = 0U;

    bool operator==(
        const SyncReplicaHistoricalVersionPayloadReachability&) const =
        default;
};

// One immutable active file operation that is no longer a visible head at its
// path. Dotted counters are causal identities, not wall-clock timestamps. A
// candidate is immediately restorable only when its exact payload is present,
// the current path has one unambiguous visible head, and restoring would change
// the current materialized value. Every field is advisory inspection evidence;
// restore re-proves the complete replica, payload, catalog, and rooted path.
struct SyncReplicaHistoricalVersionEntry final {
    std::string operation_id;
    std::string canonical_path;
    std::uint64_t size_bytes = 0U;
    std::string content_sha256;
    SyncReplicaActor actor;
    std::uint64_t counter = 0U;
    std::uint64_t visible_head_count = 0U;
    std::string current_primary_operation_id;
    SyncReplicaValueKind current_primary_kind = SyncReplicaValueKind::File;
    // Null in causal-metadata-only inspection because that mode performs no
    // payload-store observation. A false exact value means the namespace was
    // observed and did not contain the exact digest/size pair.
    std::optional<bool> payload_present;
    std::optional<bool> restore_ready;
    bool pinned = false;

    bool operator==(const SyncReplicaHistoricalVersionEntry&) const = default;
};

struct SyncReplicaHistoricalVersionInventory final {
    SyncReplicaHistoricalVersionQuery query;
    std::uint64_t source_replica_state_generation = 0U;
    std::string source_operation_set_digest;
    // Present for exact inspection and absent in metadata-only mode. New exact
    // source tokens bind this digest because inactive retained evidence
    // participates in the reachability result.
    std::optional<std::string> source_evidence_set_digest;
    std::string source_historical_version_pin_set_digest;
    std::uint64_t historical_version_pin_count = 0U;
    std::string source_visible_state_digest;
    // Absent for causal-metadata-only inspection. Every payload-derived
    // field below is likewise null so zero cannot be mistaken for an exact
    // negative observation.
    std::optional<std::string> source_payload_snapshot_digest;
    std::optional<std::uint64_t> payload_scan_hashed_entry_count;
    std::optional<std::uint64_t> payload_scan_hashed_bytes;
    std::optional<std::uint64_t> payload_scan_reused_entry_count;
    std::optional<std::uint64_t> payload_scan_reused_bytes;
    std::optional<SyncReplicaHistoricalVersionPayloadReachability>
        retained_payload_reachability;
    // Total active superseded file operations in the selected path scope,
    // including the cursor and entries that precede it.
    std::uint64_t historical_file_operation_count = 0U;
    // Operations strictly after the exact cursor under the deterministic
    // inspection order. Equal to historical_file_operation_count when no
    // cursor was requested.
    std::uint64_t historical_file_operation_count_after_cursor = 0U;
    std::optional<std::uint64_t> payload_present_count;
    std::optional<std::uint64_t> restore_ready_count;
    // The owner records its causal entry-count frontier independently from the
    // service transport frontier. Either reason makes the page resumable
    // through next_start_after_operation_id, but only the service-owned byte
    // frontier is allowed to populate status_byte_limit.
    bool entry_limit_frontier_reached = false;
    std::optional<std::uint64_t> status_byte_limit;
    bool status_byte_frontier_reached = false;
    bool truncated = false;
    std::optional<std::string> next_start_after_operation_id;
    std::vector<SyncReplicaHistoricalVersionEntry> entries;

    bool operator==(const SyncReplicaHistoricalVersionInventory&) const =
        default;

    [[nodiscard]] SyncReplicaHistoricalVersionSourceCutpoint source_cutpoint()
        const {
        return {
            .inspection_mode = query.inspection_mode,
            .operation_set_digest = source_operation_set_digest,
            .evidence_set_digest = source_evidence_set_digest,
            .historical_version_pin_set_digest =
                source_historical_version_pin_set_digest,
            .payload_snapshot_digest = source_payload_snapshot_digest,
        };
    }
};

// Deletion-free physical payload classification at one exact causal/payload
// cutpoint. CurrentOrExplicitPin identifies current materialization or explicit
// owner policy. RetainedHistoryOrEvidence identifies only superseded-active or
// inactive causal evidence. UnreferencedByRetainedFileOperations means exactly
// that no retained File operation names the object at this cutpoint; it does
// not grant quota, grace-period, quarantine, or unlink authority.
enum class SyncReplicaRetentionPlanDisposition : std::uint8_t {
    CurrentOrExplicitPin = 1U,
    RetainedHistoryOrEvidence = 2U,
    UnreferencedByRetainedFileOperations = 3U,
};

// Historical result of one exact-inode exclusive payload-use lease probe made
// while the complete payload namespace remained beneath the store-global
// exclusive writer fence. NotApplicable is used for entries retained by a
// File-operation root. Available and Busy are point-in-time observations only:
// the dry-run planner releases both the inode probe and the global fence before
// returning, so neither value grants later quarantine or unlink authority.
enum class SyncReplicaRetentionPlanPayloadUseDisposition : std::uint8_t {
    NotApplicable = 1U,
    ExclusiveAvailableAtCutpoint = 2U,
    BusyAtCutpoint = 3U,
};

[[nodiscard]] constexpr std::string_view
sync_replica_retention_plan_payload_use_disposition_name(
    SyncReplicaRetentionPlanPayloadUseDisposition disposition) noexcept {
    switch (disposition) {
        case SyncReplicaRetentionPlanPayloadUseDisposition::NotApplicable:
            return "not_applicable";
        case SyncReplicaRetentionPlanPayloadUseDisposition::
                ExclusiveAvailableAtCutpoint:
            return "exclusive_available_at_cutpoint";
        case SyncReplicaRetentionPlanPayloadUseDisposition::BusyAtCutpoint:
            return "busy_at_cutpoint";
    }
    return "unknown";
}

[[nodiscard]] constexpr std::string_view
sync_replica_retention_plan_disposition_name(
    SyncReplicaRetentionPlanDisposition disposition) noexcept {
    switch (disposition) {
        case SyncReplicaRetentionPlanDisposition::CurrentOrExplicitPin:
            return "current_or_explicit_pin";
        case SyncReplicaRetentionPlanDisposition::RetainedHistoryOrEvidence:
            return "retained_history_or_evidence";
        case SyncReplicaRetentionPlanDisposition::
                UnreferencedByRetainedFileOperations:
            return "unreferenced_by_retained_file_operations";
    }
    return "unknown";
}

struct SyncReplicaRetentionPlanClass final {
    std::uint64_t payload_count = 0U;
    std::uint64_t payload_bytes = 0U;

    bool operator==(const SyncReplicaRetentionPlanClass&) const = default;
};

struct SyncReplicaRetentionPlanEntry final {
    std::string content_sha256;
    std::uint64_t size_bytes = 0U;
    bool current_visible = false;
    bool superseded_active = false;
    bool inactive_evidence = false;
    bool explicit_pin = false;
    // True only when a capability registered by any retained owner in this
    // process for the exact attested payload-store scope can still consume this
    // physical payload after the planner's own shared lease is released. This
    // is not a cross-process or durable root.
    bool same_process_store_live_capability = false;
    SyncReplicaRetentionPlanPayloadUseDisposition payload_use_disposition =
        SyncReplicaRetentionPlanPayloadUseDisposition::NotApplicable;
    SyncReplicaRetentionPlanDisposition disposition =
        SyncReplicaRetentionPlanDisposition::UnreferencedByRetainedFileOperations;

    bool operator==(const SyncReplicaRetentionPlanEntry&) const = default;
};

// One bounded page over the complete physical payload namespace. The source
// token is the existing exact v4 historical cutpoint, so pages cannot silently
// mix operation, inactive-evidence, pin-policy, or payload snapshots. The
// reachability aggregate includes missing referenced content, while entries
// enumerate only physical objects in digest order. The candidate-set digest is
// page-invariant and binds every exact physical object that lacks a retained
// File-operation root. The deletion-free mark digest additionally binds that
// candidate set to the exact operation/evidence/pin/payload source cutpoint.
// The payload cutpoint now includes an exact canonical witness for every
// admitted payload-store transient namespace obligation plus its physical and
// reserved capacity. This closes aggregate count/byte aliasing, but does not
// claim that opened senders, active service passes, or future collector restart
// obligations have all been modeled. The mark also binds an exact bounded
// census of capabilities issued by every retained owner in this process for
// the exact attested payload-store scope. It excludes the planner's own
// snapshot, brackets the projection, and roots either every current payload
// (snapshot/targeted-access/mutation authority) or one exact digest/size object
// (opened payload). Other processes, already-copied response bytes, and durable
// restart roots are deliberately outside this census. The CPU- and
// allocation-heavy causal projection is prepared before exclusion; the
// complete payload observation, exact physical/root merge, and bounded
// candidate probes are made while one store-global exclusive writer fence
// remains live. Every returned unreferenced candidate is additionally probed
// for an exact-inode exclusive payload-use lease before that fence is released.
// This excludes cooperating new namespace work during the physical cutpoint
// and detects already-open cooperating descriptors on the bounded returned
// page; it still does not bind future work after return.
// Neither digest is durable collection authority: this object remains
// explanatory dry-run evidence and deliberately has no reclaimable-authority
// bit.
struct SyncReplicaRetentionPlan final {
    SyncReplicaRetentionPlanQuery query;
    std::string source_replica_database_incarnation_sha256;
    std::uint64_t source_replica_database_recovery_epoch = 0U;
    std::uint64_t source_replica_state_generation = 0U;
    std::string source_operation_set_digest;
    std::string source_evidence_set_digest;
    std::string source_historical_version_pin_set_digest;
    std::uint64_t historical_version_pin_count = 0U;
    std::string source_visible_state_digest;
    std::string source_payload_snapshot_digest;
    std::string source_payload_transient_namespace_digest;
    std::uint64_t payload_transient_entry_count = 0U;
    std::uint64_t payload_transient_bytes = 0U;
    std::uint64_t payload_transient_reserved_bytes = 0U;
    std::uint64_t payload_scan_hashed_entry_count = 0U;
    std::uint64_t payload_scan_hashed_bytes = 0U;
    std::uint64_t payload_scan_reused_entry_count = 0U;
    std::uint64_t payload_scan_reused_bytes = 0U;
    std::string live_capability_process_store_scope_digest;
    std::string live_capability_process_store_scope_incarnation_digest;
    std::string live_capability_set_digest;
    std::uint64_t live_snapshot_count = 0U;
    std::uint64_t live_opened_payload_count = 0U;
    std::uint64_t live_targeted_access_count = 0U;
    std::uint64_t live_mutation_batch_count = 0U;
    std::uint64_t distinct_live_opened_payload_root_count = 0U;
    std::uint64_t distinct_live_opened_payload_root_bytes = 0U;
    bool live_capabilities_may_reopen_all_current_payloads = false;
    std::uint64_t live_capability_rooted_physical_payload_count = 0U;
    std::uint64_t live_capability_rooted_physical_payload_bytes = 0U;
    std::uint64_t unreferenced_live_capability_rooted_payload_count = 0U;
    std::uint64_t unreferenced_live_capability_rooted_payload_bytes = 0U;
    bool writer_fenced_observation = false;
    bool cooperating_new_namespace_activity_excluded_during_observation =
        false;
    // Number of entries in the logical query page while the writer fence was
    // held. The independent status-byte frontier may later expose only a
    // canonical prefix of those already-probed entries; the digest and counts
    // below continue to describe the complete logical page.
    std::uint64_t writer_fenced_candidate_page_entry_count = 0U;
    std::uint64_t returned_unreferenced_candidate_count = 0U;
    std::uint64_t returned_candidate_payload_use_exclusive_available_count =
        0U;
    std::uint64_t returned_candidate_payload_use_busy_count = 0U;
    std::string writer_fenced_candidate_page_digest;
    SyncReplicaHistoricalVersionPayloadReachability retained_payload_reachability;
    SyncReplicaRetentionPlanClass current_or_explicit_pin;
    SyncReplicaRetentionPlanClass retained_history_or_evidence;
    SyncReplicaRetentionPlanClass unreferenced_by_retained_file_operations;
    std::string unreferenced_candidate_set_digest;
    // Restart-stable candidate identity over durable replica roots, the exact
    // physical/transient payload snapshot, and the complete candidate set. It
    // deliberately excludes process-store incarnation and live-capability
    // generation; future mutation must re-prove current reader exclusion.
    std::string durable_candidate_witness_digest;
    std::string exact_deletion_free_mark_digest;
    std::uint64_t physical_payload_count_after_cursor = 0U;
    bool entry_limit_frontier_reached = false;
    std::optional<std::uint64_t> status_byte_limit;
    bool status_byte_frontier_reached = false;
    bool truncated = false;
    std::optional<std::string> next_start_after_content_sha256;
    std::vector<SyncReplicaRetentionPlanEntry> entries;

    bool operator==(const SyncReplicaRetentionPlan&) const = default;

    [[nodiscard]] SyncReplicaHistoricalVersionSourceCutpoint source_cutpoint()
        const {
        return {
            .inspection_mode = SyncReplicaHistoricalVersionInspectionMode::
                ExactPayloadAvailability,
            .operation_set_digest = source_operation_set_digest,
            .evidence_set_digest = source_evidence_set_digest,
            .historical_version_pin_set_digest =
                source_historical_version_pin_set_digest,
            .payload_snapshot_digest = source_payload_snapshot_digest,
        };
    }
};

// One explicit request to persist a deletion-free retention observation. The
// request binds both the exact v4 causal/payload cutpoint and its complete
// restart-stable candidate witness. The database incarnation distinguishes
// independent SQLite files with otherwise identical contents; the recovery
// epoch and source generation prevent stale same-incarnation evidence from
// crossing an explicit recovery or digest-level causal ABA. These values live
// inside SQLite and are therefore not external exact-image anti-rollback
// authority. The supplied wall-clock value is historical operator evidence
// only; a future collector must still re-prove trusted elapsed time.
struct SyncReplicaPayloadRetentionMarkRequest final {
    SyncReplicaHistoricalVersionSourceCutpoint expected_source_cutpoint;
    std::string expected_source_replica_database_incarnation_sha256;
    std::uint64_t expected_source_replica_database_recovery_epoch = 0U;
    std::uint64_t expected_source_replica_state_generation = 0U;
    std::string expected_durable_candidate_witness_digest;
    std::uint64_t marked_at_unix_seconds = 0U;
    SyncReplicaFilePayloadRetentionPolicy policy;

    bool operator==(
        const SyncReplicaPayloadRetentionMarkRequest&) const = default;
};

enum class SyncReplicaHistoricalVersionRestoreDisposition : std::uint8_t {
    Published = 1U,
    AdoptedVisibleOperation = 2U,
};

[[nodiscard]] constexpr std::string_view
sync_replica_historical_version_restore_disposition_name(
    SyncReplicaHistoricalVersionRestoreDisposition disposition) noexcept {
    switch (disposition) {
        case SyncReplicaHistoricalVersionRestoreDisposition::Published:
            return "published";
        case SyncReplicaHistoricalVersionRestoreDisposition::
            AdoptedVisibleOperation:
            return "adopted_visible_operation";
    }
    return "unknown";
}

struct SyncReplicaHistoricalVersionRestoreResult final {
    SyncReplicaHistoricalVersionRestoreDisposition disposition =
        SyncReplicaHistoricalVersionRestoreDisposition::Published;
    SyncReplicaOperation historical_operation;
    SyncReplicaOperation replaced_visible_operation;
    SyncReplicaFolderCatalogEntry restored_entry;
    SyncReplicaOperation restored_operation;

    bool operator==(const SyncReplicaHistoricalVersionRestoreResult&) const =
        default;
};

inline constexpr std::uint64_t
    kSyncReplicaFolderDefaultMaximumRemoteApplyOperations = 4096U;
inline constexpr std::uint64_t
    kSyncReplicaFolderDefaultMaximumRemoteInspectionPaths = 4096U;

// The post-scan remote planner validates the complete visible projection before
// publishing any selected cyclic segment, but effect work is cooperatively
// segmented. A count frontier covers tombstones and zero-byte files, while the
// aggregate byte frontier independently covers regular-file materialization.
// This value is diagnostic scheduling state only; it is not replica or catalog
// authority.
enum class SyncReplicaFolderRemoteApplyStopReason : std::uint8_t {
    NotStarted = 0,
    EndOfProjection = 1,
    AggregateFileByteFrontier = 2,
    OperationCountFrontier = 3,
    InspectionPathFrontier = 4,
    AuthorityCutpointChanged = 5,
};

[[nodiscard]] constexpr std::string_view
sync_replica_folder_remote_apply_stop_reason_name(
    SyncReplicaFolderRemoteApplyStopReason reason) noexcept {
    switch (reason) {
        case SyncReplicaFolderRemoteApplyStopReason::NotStarted:
            return "not_started";
        case SyncReplicaFolderRemoteApplyStopReason::EndOfProjection:
            return "end_of_projection";
        case SyncReplicaFolderRemoteApplyStopReason::
            AggregateFileByteFrontier:
            return "aggregate_file_byte_frontier";
        case SyncReplicaFolderRemoteApplyStopReason::OperationCountFrontier:
            return "operation_count_frontier";
        case SyncReplicaFolderRemoteApplyStopReason::InspectionPathFrontier:
            return "inspection_path_frontier";
        case SyncReplicaFolderRemoteApplyStopReason::AuthorityCutpointChanged:
            return "authority_cutpoint_changed";
    }
    return "unknown";
}

// One deliberately bounded synchronous folder pass. These limits govern the
// namespace walk and exact local file extents streamed during this invocation.
// The same per-file and aggregate byte ceilings independently bound remote files
// selected for materialization. Only successful completion of one durable
// scan epoch authorizes classification of cataloged file paths omitted from its
// authenticated journal as absent; no watcher hint, segment prefix, nominal
// completion of a changed namespace, or failed traversal authorizes deletion.
struct SyncReplicaFolderConvergencePassLimits final {
    // Namespace-work capacity and durable file capacity are intentionally
    // distinct. Directories and ignored objects spend maximum_entries but do
    // not consume catalog rows or payload identities. Regular files spend both.
    std::uint64_t maximum_entries =
        kSyncReplicaFolderObservationDefaultMaximumEntries;
    std::uint64_t maximum_regular_files =
        kSyncReplicaFolderObservationDefaultMaximumRegularFiles;
    std::uint64_t maximum_file_bytes = 4ULL * 1024ULL * 1024ULL;
    std::uint64_t maximum_total_file_bytes = 256ULL * 1024ULL * 1024ULL;
    std::uint64_t maximum_relative_path_bytes = 4096U;
    std::uint64_t maximum_directory_depth = 64U;
    std::uint64_t maximum_remote_paths = 100000U;
    // Bounds rooted local-path classification and payload-readiness lookups in
    // the cyclic remote projection. Complete in-memory projection admission is
    // still performed before any effect. Paths safely skipped in this segment
    // advance the durable scheduling cursor only after all selected effects
    // commit, so a large unavailable/conflicted/no-op prefix cannot be reopened
    // on every pass.
    std::uint64_t maximum_remote_inspection_paths =
        kSyncReplicaFolderDefaultMaximumRemoteInspectionPaths;
    // Bounds successful calls into remote file/tombstone apply owners across one
    // pass. Local traversal only proves exact predecessor eligibility or records
    // a conflict; every materialization is selected later by the cyclic planner.
    // This frontier is therefore independent of the local scan segment size.
    // Unlike maximum_remote_paths, it is a scheduling boundary, not admission.
    std::uint64_t maximum_remote_apply_operations =
        kSyncReplicaFolderDefaultMaximumRemoteApplyOperations;
    // Bounds the number of local regular paths whose independently committed
    // effects can be staged for one authenticated scan-journal publication.
    // The byte frontier still applies independently. Keeping this scheduling
    // field internal avoids exposing an unmeasured product knob while ensuring
    // zero-byte trees cannot create a 100,000-row pass transaction by default.
    std::uint64_t maximum_local_scan_segment_regular_files =
        kSyncReplicaFolderTraversalDefaultMaximumRegularFiles;
    // One cooperative exclusive payload-store lease is segmented before it can
    // cover more than this many source puts or this much measured exact byte
    // work. Work counts cold bytes hashed by batch construction/recovery, bytes
    // prepared while the lease was already live, and bytes presented to puts.
    // Construction learns cold-scan cost only after acquiring the lease, so one
    // cold scan plus one selected file may exceed this scheduling frontier; no
    // additional path is then admitted to that batch. A single larger file is
    // likewise admissible because the per-file and whole-pass ceilings remain
    // authoritative.
    std::uint64_t maximum_payload_batch_puts = 256U;
    std::uint64_t maximum_payload_batch_work_bytes =
        256ULL * 1024ULL * 1024ULL;

    bool operator==(const SyncReplicaFolderConvergencePassLimits&) const =
        default;
};

// Canonical default composition for one committed deployment. A pass that
// admits one configured file must also admit at least that file in its
// aggregate budget; otherwise raising the deployment ceiling silently creates
// an unusable configuration. Callers may still lower either bound explicitly.
[[nodiscard]] SyncReplicaFolderConvergencePassLimits
sync_replica_folder_convergence_pass_limits_for_payload_ceiling_or_throw(
    std::uint64_t maximum_payload_bytes,
    std::string_view label =
        "sync replica folder convergence deployment limits");

// Bootstrap-only initializer for one complete filename-free folder-catalog
// SQLite image. It proves the selected deployment, root, replica actor, and
// payload store before adding the exact catalog schema. The caller must seal
// and publish the image create-new, then reopen it through the named
// ExistingOnly constructor below. No filesystem database path is created here.
void initialize_sync_replica_folder_catalog_in_detached_image_or_throw(
    SyncSqliteDbHandleSlot& catalog_db,
    SyncReplicaSqliteDeploymentBinding catalog_binding,
    std::filesystem::path absolute_root_directory,
    SyncReplicaSqliteOwner& replica_owner,
    SyncReplicaFilePayloadStore& payload_store,
    SyncReplicaFolderScanLimits limits = {},
    std::string label =
        "sync replica detached folder catalog bootstrap");

struct SyncReplicaFolderConvergencePassReport final {
    SyncReplicaFolderTraversalSummary traversal;
    // Durable fair-scan state. A bounded pass may advance one deterministic
    // prefix and leave the cursor for a later process incarnation. Deletion
    // authority is available only when completed_local_scan_epoch is true. At
    // completion, a cataloged file omitted from the authenticated seen journal
    // but found present forces a conservative epoch restart. A path changed or
    // deleted after it was already seen is deferred to the next epoch; journal
    // membership never proves that its current namespace binding still exists.
    std::uint64_t local_scan_epoch = 0U;
    bool completed_local_scan_epoch = false;
    bool restarted_local_scan_epoch = false;
    std::uint64_t local_scan_seen_path_count = 0U;
    std::string local_scan_resume_after_path;
    // The current invocation's local traversal outcome. This explains whether
    // a retained cursor is waiting on classified-byte work or path-effect work,
    // while EndOfNamespace distinguishes a complete traversal from either
    // cooperative scheduling frontier. It is diagnostic, not durable authority.
    SyncReplicaFolderTraversalStopReason local_scan_stop_reason =
        SyncReplicaFolderTraversalStopReason::NotStarted;
    // Exact diagnostics copied from the traversal segment that produced this
    // pass. They expose the bounded sorted-component implementation without a
    // second directory walk or inferred memory claim.
    std::uint64_t local_directory_enumeration_pass_count = 0U;
    std::uint64_t local_peak_buffered_directory_component_batch_count = 0U;
    std::uint64_t
        local_peak_simultaneously_buffered_directory_component_count = 0U;
    // True only when the pass proved an unchanged working tree, catalog,
    // replica cutpoint, and locally retained payload inventory using one
    // bounded read-only observation of each authority. The ordinary
    // path-local mutation owners remain the fallback for every changed,
    // incomplete, or ambiguous case.
    bool used_idle_fast_path = false;
    // Complete payload-root observations performed by this convergence pass
    // are distinct from an exact snapshot consumed from its retaining process
    // owner. Rev0957 uses the latter after integrity recovery so the complete
    // current-byte reproof is not immediately followed by another namespace
    // enumeration. The handoff is accepted only from the exact same store
    // handle and remains subject to all snapshot epoch/path reproofs.
    std::uint64_t payload_snapshot_handoff_count = 0U;
    std::uint64_t payload_snapshot_handoff_entry_count = 0U;
    std::uint64_t payload_snapshot_observation_count = 0U;
    std::uint64_t payload_snapshot_observed_entry_count = 0U;
    std::uint64_t exact_local_file_bytes = 0U;
    std::uint64_t exact_remote_file_bytes = 0U;
    // Diagnostic-only proof of the local payload publication shape. A
    // fallback traversal may release and reacquire the batch around remote
    // materialization, so these counters are pass totals rather than one
    // assumed batch. They never participate in replica or catalog authority.
    std::uint64_t payload_mutation_batch_count = 0U;
    std::uint64_t payload_mutation_full_scan_count = 0U;
    std::uint64_t payload_mutation_scan_hashed_entry_count = 0U;
    std::uint64_t payload_mutation_scan_hashed_bytes = 0U;
    std::uint64_t payload_mutation_scan_reused_entry_count = 0U;
    std::uint64_t payload_mutation_scan_reused_bytes = 0U;
    std::uint64_t payload_mutation_scan_process_reused_entry_count = 0U;
    std::uint64_t payload_mutation_scan_process_reused_bytes = 0U;
    std::uint64_t payload_mutation_scan_durable_reused_entry_count = 0U;
    std::uint64_t payload_mutation_scan_durable_reused_bytes = 0U;
    std::uint64_t payload_mutation_put_count = 0U;
    std::uint64_t payload_mutation_source_bytes = 0U;
    // Measured exact file bytes hashed, read, or copied while an exclusive
    // payload mutation lease was live. Namespace enumeration and metadata work
    // are reported only indirectly by full-scan/reuse counts. Diagnostic only.
    std::uint64_t payload_mutation_work_bytes = 0U;
    std::uint64_t payload_mutation_peak_batch_put_count = 0U;
    std::uint64_t payload_mutation_peak_batch_work_bytes = 0U;
    std::uint64_t payload_mutation_inserted_count = 0U;
    std::uint64_t payload_mutation_already_present_count = 0U;
    std::uint64_t local_published_count = 0U;
    // One logical exact-content identity continuation. Each count corresponds
    // to two ordinary wire-compatible operations committed atomically in the
    // replica database: destination File, then source Tombstone.
    std::uint64_t local_identity_preserving_rename_count = 0U;
    std::uint64_t local_adopted_visible_count = 0U;
    std::uint64_t local_catalog_no_op_count = 0U;
    std::uint64_t local_catalog_refreshed_count = 0U;
    std::uint64_t remote_applied_count = 0U;
    std::uint64_t remote_adopted_exact_count = 0U;
    std::uint64_t remote_catalog_no_op_count = 0U;
    // Count of completed calls into a remote apply owner. The three disposition
    // counters above partition this value. A complete pass-scoped payload
    // snapshot is reused when local admission already needed one; its observation
    // count is therefore zero or one and entry_count records that exact frozen
    // inventory. A remote-only pass instead creates at most one targeted access
    // cutpoint, then performs lease-proved target-name probes while inspecting
    // paths and opens only selected present payloads.
    // probe_count includes exact absence; selection_count counts completed
    // descriptor-backed apply owners, and selected_bytes records their admitted
    // operation extents rather than claiming bytes were read. The atomic
    // publisher computes SHA-256 exactly once if publication consumes a selected
    // descriptor; an already-exact destination consumes none. None of these
    // counters claims a complete payload-root namespace or capacity attestation.
    // Missing payloads are deferred without blocking later ready paths.
    //
    // deferred_remote_apply_candidate_count counts the first otherwise eligible
    // post-scan candidate left for a later pass after an effect frontier. Remote
    // inspected/acknowledged/deferred counts expose the independent path-work
    // frontier: inspected includes the candidate that discovered an effect
    // frontier, while acknowledged excludes it because the durable cursor may
    // advance only across completed work. The cursor fields retain their public
    // rev0951 names for compatibility but now expose that stronger scheduling
    // acknowledgement. Wrapped is true when the cyclic walk crossed canonical
    // namespace end. These are diagnostics, not replicated evidence or
    // authority.
    std::uint64_t remote_apply_operation_count = 0U;
    std::uint64_t remote_payload_snapshot_observation_count = 0U;
    std::uint64_t remote_payload_snapshot_entry_count = 0U;
    std::uint64_t remote_targeted_payload_access_count = 0U;
    std::uint64_t remote_targeted_payload_probe_count = 0U;
    std::uint64_t remote_targeted_payload_selection_count = 0U;
    std::uint64_t remote_targeted_payload_selected_bytes = 0U;
    // File operations resolved to MetadataOnly are fully admitted causal
    // evidence but request no successor payload and publish no successor rooted
    // file. A previously materialized exact catalog predecessor is removed only
    // after the current rooted bytes, retained catalog mapping, causal target,
    // selection policy, and private predecessor payload are all re-proved. An
    // untracked, locally changed, conflicted, or payload-unavailable file is
    // preserved and makes the remote sweep unresolved instead of being silently
    // hidden or deleted. This is local dematerialization, never a replicated
    // tombstone. Excluded cataloged files remain omitted from local absence
    // inference, so a policy change cannot manufacture a deletion.
    std::uint64_t remote_metadata_only_file_count = 0U;
    std::uint64_t remote_metadata_only_already_absent_file_count = 0U;
    // Exact one-path catalog observations performed while re-proving
    // metadata-only effects. Each observation reads one PRIMARY KEY row plus
    // the bounded catalog/selection metadata inside one read transaction; it
    // never materializes the complete catalog. Diagnostic only.
    std::uint64_t remote_targeted_catalog_path_cutpoint_count = 0U;
    // Exact path-local replica observations performed while re-proving
    // metadata-only effects. Each observation reads the bounded metadata row,
    // at most two visible rows for the canonical path, and zero or one distinct
    // retained operation. It never restores the complete causal model.
    // Diagnostic only.
    std::uint64_t remote_targeted_replica_path_cutpoint_count = 0U;
    std::uint64_t remote_metadata_only_dematerialization_attempt_count = 0U;
    std::uint64_t remote_metadata_only_dematerialized_file_count = 0U;
    std::uint64_t remote_metadata_only_dematerialized_bytes = 0U;
    std::uint64_t remote_metadata_only_dematerialization_blocked_file_count =
        0U;
    std::uint64_t
        remote_metadata_only_dematerialization_payload_unavailable_count = 0U;
    std::uint64_t local_metadata_only_absence_suppressed_count = 0U;
    // A changed policy opens one durable complete-scan fence. During that
    // epoch, materialized catalog predecessors absent from the rooted walk are
    // left for remote rehydration rather than converted into local tombstones.
    std::uint64_t local_selection_change_absence_suppressed_count = 0U;
    std::uint64_t deferred_remote_payload_candidate_count = 0U;
    // Count of present catalog predecessors not already hashed by this
    // invocation's local traversal and then revalidated from fresh rooted
    // descriptor metadata before becoming eligible. Catalog metadata only
    // nominates work: the apply owner still reopens and hashes the exact bytes.
    std::uint64_t remote_apply_revalidated_catalog_predecessor_count = 0U;
    std::uint64_t deferred_remote_apply_candidate_count = 0U;
    std::uint64_t remote_inspected_path_count = 0U;
    std::uint64_t remote_acknowledged_path_count = 0U;
    std::uint64_t deferred_remote_inspection_path_count = 0U;
    // A bounded inspection segment can contribute to one durable sweep only
    // while both the catalog digest and replica visible-state digest remain
    // identical to its persisted basis. The count includes earlier committed
    // segments of that exact basis. The persisted origin lets the owner rederive
    // the exact expected cursor from projection order plus count before trusting
    // continuation. Completion means every sole-visible path in the admitted
    // projection was acknowledged once; the unresolved flag folds in safe
    // deferrals observed by any segment of the completed sweep.
    std::string remote_inspection_sweep_started_after_path;
    std::uint64_t remote_inspection_sweep_seen_path_count = 0U;
    bool completed_remote_inspection_sweep = false;
    bool remote_inspection_sweep_had_unresolved_paths = false;
    // True only when the terminal catalog digest and replica visible-state
    // digest were re-proved while a replica BEGIN IMMEDIATE guard excluded
    // causal writers and the catalog owner atomically checked its exact
    // progress/cutpoint head. These two digests name that terminal cross-owner
    // observation. A sync-once composition must compare them and the report's
    // remote_apply_resume_after_path with its final durable cutpoint before
    // calling the cycle settled; completion of an older sweep is not settlement
    // of a newer projection or scheduling cursor head.
    bool remote_inspection_terminal_cutpoint_reproved = false;
    std::string remote_inspection_terminal_catalog_digest;
    std::string remote_inspection_terminal_visible_state_digest;
    std::string remote_apply_started_after_path;
    std::string remote_apply_resume_after_path;
    bool remote_apply_wrapped_projection = false;
    SyncReplicaFolderRemoteApplyStopReason remote_apply_stop_reason =
        SyncReplicaFolderRemoteApplyStopReason::NotStarted;
    std::uint64_t skipped_conflicted_remote_path_count = 0U;
    std::uint64_t skipped_tombstone_remote_path_count = 0U;
    // A locally absent exact catalog predecessor is a possible uncommitted
    // local deletion. Remote materialization must not silently restore that
    // predecessor until an authoritative local scan either publishes absence
    // or observes the path again. This fence remains necessary after nominal
    // epoch completion because a path seen in an earlier segment can disappear
    // before the final segment. A distinct remote successor is not deferred.
    std::uint64_t deferred_unadjudicated_local_absence_remote_file_count = 0U;

    bool operator==(const SyncReplicaFolderConvergencePassReport&) const =
        default;
};

// Move-only stable observation prepared before any payload-store or replica
// mutation. It retains the exact opened file descriptor and streaming digest,
// without retaining the file bytes. Commit rejects an in-place mutation and
// re-traverses the configured root to prove that the same pathname still names
// the observed object.
class SyncReplicaPreparedRegularFile final {
public:
    SyncReplicaPreparedRegularFile() noexcept = default;
    ~SyncReplicaPreparedRegularFile() noexcept;
    SyncReplicaPreparedRegularFile(
        const SyncReplicaPreparedRegularFile&) = delete;
    SyncReplicaPreparedRegularFile& operator=(
        const SyncReplicaPreparedRegularFile&) = delete;
    SyncReplicaPreparedRegularFile(
        SyncReplicaPreparedRegularFile&&) noexcept;
    SyncReplicaPreparedRegularFile& operator=(
        SyncReplicaPreparedRegularFile&&) noexcept;

    [[nodiscard]] bool active() const noexcept;
    [[nodiscard]] const std::string& canonical_path() const;
    [[nodiscard]] std::uint64_t size_bytes() const;
    [[nodiscard]] const std::string& content_sha256() const;
    [[nodiscard]] const std::vector<std::string>&
    observed_visible_operation_ids() const;

private:
    struct State;

    explicit SyncReplicaPreparedRegularFile(
        std::unique_ptr<State> state) noexcept;
    [[nodiscard]] State& require_state_or_throw(std::string_view label);
    [[nodiscard]] const State& require_state_or_throw(
        std::string_view label) const;

    std::unique_ptr<State> state_;

    friend class SyncReplicaFolderScanOwner;
};

// First production-facing folder bridge: one configured Linux root, regular
// files plus durable file tombstones, and an indexed local catalog. Local file
// scanning re-proves exact bytes and publishes against observed replica heads.
// A complete successful traversal may also publish disappearance of an exact
// cataloged file; incomplete walks and unsupported substitutions never may.
// Remote apply accepts one exact sole-visible file or tombstone, fences all
// effects beneath the retained root, and records the exact materialized value
// so the next scan does not echo it. Changed local state, populated-target
// ambiguity, and unresolved replica heads fail closed. Directories remain
// structural rather than replicated values. No peer outbox is created here.
class SyncReplicaFolderScanOwner final {
public:
    SyncReplicaFolderScanOwner(
        SyncSqliteDbHandleSlot& catalog_db,
        std::string folder_id,
        std::filesystem::path absolute_root_directory,
        SyncReplicaSqliteOwner& replica_owner,
        SyncReplicaFilePayloadStore& payload_store,
        SyncReplicaFolderScanLimits limits = {},
        std::string label = "sync replica folder scan owner");

    // Product-bound form. The exact folder-catalog deployment binding is
    // attested on every catalog load. ExistingOnly is the operational default:
    // it can never turn a mistyped path into a new authority store. Explicit
    // bootstrap may select CreateIfMissing on a fresh dedicated database.
    SyncReplicaFolderScanOwner(
        SyncSqliteDbHandleSlot& catalog_db,
        SyncReplicaSqliteDeploymentBinding catalog_binding,
        std::filesystem::path absolute_root_directory,
        SyncReplicaSqliteOwner& replica_owner,
        SyncReplicaFilePayloadStore& payload_store,
        SyncReplicaFolderCatalogOpenDisposition disposition,
        SyncReplicaFolderScanLimits limits = {},
        std::string label =
            "sync replica product-bound folder scan owner");
    ~SyncReplicaFolderScanOwner() noexcept;

    SyncReplicaFolderScanOwner(const SyncReplicaFolderScanOwner&) = delete;
    SyncReplicaFolderScanOwner& operator=(
        const SyncReplicaFolderScanOwner&) = delete;
    SyncReplicaFolderScanOwner(SyncReplicaFolderScanOwner&&) = delete;
    SyncReplicaFolderScanOwner& operator=(
        SyncReplicaFolderScanOwner&&) = delete;

    [[nodiscard]] SyncReplicaFolderCatalogSnapshot snapshot_or_throw();
    [[nodiscard]] const std::string& folder_id() const;
    [[nodiscard]] SyncReplicaSelectiveSyncPolicy
    selective_sync_policy_snapshot_or_throw();
    [[nodiscard]] SyncReplicaSelectiveSyncPolicy
    replace_selective_sync_policy_or_throw(
        SyncReplicaSelectiveSyncMode default_mode,
        std::vector<SyncReplicaSelectiveSyncRule> rules);
    [[nodiscard]] SyncReplicaFolderScanProgressSnapshot
    scan_progress_snapshot_or_throw();

    [[nodiscard]] SyncReplicaPreparedRegularFile
    prepare_regular_file_or_throw(std::string canonical_path);

    // Same exact observation boundary with a narrower per-call byte ceiling.
    // The whole-folder pass uses this to ensure aggregate limits are checked
    // before payload admission or replica/catalog mutation.
    [[nodiscard]] SyncReplicaPreparedRegularFile
    prepare_regular_file_bounded_or_throw(
        std::string canonical_path,
        std::uint64_t maximum_bytes);

    [[nodiscard]] SyncReplicaFolderScanResult
    commit_prepared_regular_file_or_throw(
        SyncReplicaPreparedRegularFile prepared);

    [[nodiscard]] SyncReplicaFolderScanResult scan_regular_file_or_throw(
        std::string canonical_path);

    [[nodiscard]] SyncReplicaFolderApplyResult
    apply_visible_regular_file_or_throw(std::string operation_id);

    [[nodiscard]] SyncReplicaFolderApplyResult
    apply_visible_tombstone_or_throw(std::string operation_id);

    // Explicit, potentially expensive operator inspection. It performs one
    // complete rooted payload-store snapshot, restores the complete causal
    // model, and returns a bounded deterministic projection of superseded file
    // operations. It mutates no replica/catalog/file state and makes no
    // retention promise; unavailable payloads remain visible as non-restorable
    // evidence.
    [[nodiscard]] SyncReplicaHistoricalVersionInventory
    inspect_historical_versions_or_throw(
        std::uint64_t maximum_entries =
            kSyncReplicaHistoricalVersionDefaultMaximumEntries);

    // Path-scoped and cursor-paginated inspection. The cursor is one exact
    // currently active superseded file operation; it is not durable paging
    // authority across replica changes. The returned source digests let an
    // operator detect that each page came from a different current cutpoint.
    [[nodiscard]] SyncReplicaHistoricalVersionInventory
    inspect_historical_versions_or_throw(
        SyncReplicaHistoricalVersionQuery query);

    // Exact, deletion-free physical payload planning. The page is ordered by
    // digest and bound to the same operation/evidence/pin/payload cutpoint as
    // exact historical inspection. It explains roots and missing references,
    // but does not select a grace period, quota, quarantine, or unlink action.
    [[nodiscard]] SyncReplicaRetentionPlan
    plan_payload_retention_or_throw(
        SyncReplicaRetentionPlanQuery query = {});

    // Persists one checksum-framed policy record while the exact complete
    // payload snapshot used to recompute the caller's durable candidate witness
    // still retains the store-global writer fence. Publication performs no
    // second payload scan, payload rename, quarantine, or unlink. A final
    // replica reproof makes concurrent source drift a typed failure; any record
    // already committed at that cutpoint is permanently stale by generation.
    [[nodiscard]] SyncReplicaFilePayloadRetentionMarkPublication
    mark_payload_retention_or_throw(
        SyncReplicaPayloadRetentionMarkRequest request);

    // Mutates only the replica owner's exact local retention-root set. No
    // payload bytes, catalog rows, rooted paths, or causal evidence are changed.
    [[nodiscard]] SyncReplicaSqliteHistoricalVersionPinResult
    pin_historical_version_or_throw(std::string operation_id);
    [[nodiscard]] SyncReplicaSqliteHistoricalVersionPinResult
    unpin_historical_version_or_throw(std::string operation_id);

    // Restores one exact non-visible active file operation by copying its
    // retained immutable payload through the ordinary rooted atomic publisher,
    // then minting a new local causal successor through the existing scanner.
    // A bound request additionally requires the path's sole visible operation
    // to be the exact current head the operator inspected; stale intent fails
    // before catalog, rooted-path, or payload-store work. It never reactivates
    // the historical operation and never bypasses current conflict, catalog,
    // path, payload, or actor-authority checks.
    [[nodiscard]] SyncReplicaHistoricalVersionRestoreResult
    restore_historical_version_or_throw(
        SyncReplicaHistoricalVersionRestoreRequest request);

    // Compatibility entry point for the rev0966 owner API and local-socket
    // frame. New product callers should pass an expected current operation.
    [[nodiscard]] SyncReplicaHistoricalVersionRestoreResult
    restore_historical_version_or_throw(std::string operation_id);

    // Processes local regular files one at a time, then cyclically selects
    // sole-visible remote files or tombstones. A present cataloged local base is
    // replaced by a causal remote successor only when this invocation observed
    // its exact predecessor bytes; otherwise local publication remains the only
    // allowed action. The first unsafe path or infrastructure failure stops the
    // pass. Earlier per-path progress is durable and restart-idempotent.
    [[nodiscard]] SyncReplicaFolderConvergencePassReport
    run_convergence_pass_or_throw(
        const SyncReplicaFolderConvergencePassLimits& limits = {});

    // Consumes one complete snapshot issued by the exact payload-store handle
    // retained by this owner. This is the same convergence algorithm, not a
    // weaker recovery path: catalog/replica cutpoints, rooted file observations,
    // payload descriptor reproof, and terminal settlement remain unchanged.
    // The sole optimization is that a caller which just completed an
    // authoritative payload reproof need not enumerate the store a second time.
    [[nodiscard]] SyncReplicaFolderConvergencePassReport
    run_convergence_pass_with_payload_snapshot_or_throw(
        SyncReplicaFilePayloadStoreSnapshot payload_snapshot,
        const SyncReplicaFolderConvergencePassLimits& limits = {});

private:
    struct State;

    [[nodiscard]] SyncReplicaRetentionPlan
    plan_payload_retention_impl_or_throw(
        SyncReplicaRetentionPlanQuery query,
        const SyncReplicaPayloadRetentionMarkRequest* mark_request,
        SyncReplicaFilePayloadRetentionMarkPublication* mark_publication);

    [[nodiscard]] SyncReplicaFolderConvergencePassReport
    run_convergence_pass_impl_or_throw(
        const SyncReplicaFolderConvergencePassLimits& limits,
        std::optional<SyncReplicaFilePayloadStoreSnapshot> payload_snapshot);

    [[nodiscard]] SyncReplicaPreparedRegularFile
    prepare_regular_file_bounded_for_policy_or_throw(
        std::string canonical_path,
        std::uint64_t maximum_bytes,
        const SyncReplicaSelectiveSyncPolicy& selective_sync_policy);

    [[nodiscard]] SyncReplicaFolderScanResult
    commit_prepared_regular_file_with_payload_batch_or_throw(
        SyncReplicaPreparedRegularFile prepared,
        SyncReplicaFilePayloadStoreMutationBatch* payload_batch,
        const SyncReplicaFilePayloadStoreSnapshot*
            retained_payload_snapshot);

    [[nodiscard]] SyncReplicaFolderScanResult
    commit_complete_scan_absence_or_throw(std::string canonical_path);

    [[nodiscard]] SyncReplicaFolderApplyResult
    apply_visible_regular_file_with_payload_snapshot_or_throw(
        std::string operation_id,
        const SyncReplicaFilePayloadStoreSnapshot*
            retained_payload_snapshot);

    [[nodiscard]] std::optional<SyncReplicaFolderApplyResult>
    try_apply_visible_regular_file_with_targeted_payload_or_throw(
        std::string operation_id,
        SyncReplicaFilePayloadStoreTargetedAccess& targeted_payload_access);

    [[nodiscard]] std::optional<SyncReplicaFolderApplyResult>
    apply_visible_regular_file_with_payload_strategy_or_throw(
        std::string operation_id,
        const SyncReplicaFilePayloadStoreSnapshot*
            retained_payload_snapshot,
        SyncReplicaFilePayloadStoreTargetedAccess*
            targeted_payload_access);

    void initialize_or_throw(
        SyncSqliteDbHandleSlot& catalog_db,
        std::string folder_id,
        std::filesystem::path absolute_root_directory,
        SyncReplicaSqliteOwner& replica_owner,
        SyncReplicaFilePayloadStore& payload_store,
        SyncReplicaFolderScanLimits limits,
        std::string label,
        std::optional<SyncReplicaSqliteDeploymentBinding> catalog_binding,
        SyncReplicaFolderCatalogOpenDisposition disposition);

    std::unique_ptr<State> state_;
};

}  // namespace anonsync

#endif
