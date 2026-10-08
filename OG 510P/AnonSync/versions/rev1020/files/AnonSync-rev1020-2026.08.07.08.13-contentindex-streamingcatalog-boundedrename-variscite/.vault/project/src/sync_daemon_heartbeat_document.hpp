#pragma once

#include "sync_process_identity_observation.hpp"

#include <cstddef>
#include <cstdint>
#include <string>

namespace anonsync {

struct Json;

inline constexpr std::size_t kSyncDaemonHeartbeatMaximumJsonBytes =
    64U * 1024U;

struct SyncDaemonHeartbeatOwnerLockDocument final {
    bool required = false;
    bool acquired = false;
    bool released = false;
    bool reclaimed_expired = false;
    std::string owner_lock_id;
    std::uint64_t owner_lock_epoch = 0;
    std::uint64_t acquired_at_epoch = 0;
    std::uint64_t expires_at_epoch = 0;
    std::uint64_t released_at_epoch = 0;
};

// Typed authority-bearing subset of the external daemon heartbeat document.
// The remaining service_lifecycle, lease, and progress objects are explicitly
// observational. Decode validates their object shape but does not let their
// fields participate in lifecycle authority.
struct SyncDaemonHeartbeatDocument final {
    std::string format;
    std::string revision_id;
    std::string operation;
    std::string service_instance_id;
    std::uint64_t service_restart_epoch = 0;
    std::string state;
    bool final = false;
    std::string reason;
    std::uint64_t heartbeat_epoch = 0;
    std::uint64_t stale_after_seconds = 0;
    std::uint64_t stale_at_epoch = 0;
    std::uint64_t process_id = 0;
    bool process_identity_present = false;
    SyncProcessIdentityObservation process_identity;
    std::string checkpoint_path;
    std::string session_id;
    std::string daemon_id;
    std::string worker_id;
    SyncDaemonHeartbeatOwnerLockDocument owner_lock;
};

struct SyncDaemonHeartbeatServiceLifecycleObservation final {
    bool preflight_checked = false;
    bool preflight_passed = false;
    bool live_owner_blocked = false;
    bool heartbeat_checked = false;
    bool existing_heartbeat_loaded = false;
    bool existing_heartbeat_final = false;
    bool existing_heartbeat_fresh = false;
    bool existing_heartbeat_stale = false;
    bool reentry_from_stale_heartbeat = false;
    std::string preflight_reason;
};

struct SyncDaemonHeartbeatLeaseObservation final {
    std::string worker_lease_id;
    std::uint64_t final_worker_lease_epoch = 0;
    std::uint64_t next_worker_lease_epoch = 0;
    std::uint64_t next_scheduler_now_epoch = 0;
};

struct SyncDaemonHeartbeatProgressObservation final {
    std::uint64_t passes_attempted = 0;
    std::uint64_t passes_completed = 0;
    std::uint64_t mutating_passes = 0;
    std::uint64_t idle_passes = 0;
    bool startup_sidecar_recovery_attempted = false;
    bool startup_sidecar_recovery_completed = false;
    std::string checkpoint_schema_version;
    bool archived_checkpoint_migration_backfill_checked = false;
    bool archived_checkpoint_exact_startup_hydration_supported = false;
    bool archived_checkpoint_migration_backfill_required = false;
    bool archived_checkpoint_migration_backfill_blocked_missing_lineage = false;
    std::uint64_t archived_checkpoint_claimed_paths_blocked_by_missing_lineage = 0;
    std::uint64_t terminal_apply_workorders_checked = 0;
    std::uint64_t terminal_apply_workorders_inserted = 0;
    std::uint64_t terminal_apply_workorders_completed = 0;
    std::uint64_t terminal_apply_workorders_already_completed = 0;
    std::uint64_t terminal_apply_tombstone_workorders_completed = 0;
    std::uint64_t terminal_apply_tombstone_targets_removed = 0;
    std::uint64_t terminal_apply_tombstone_targets_already_absent = 0;
    std::uint64_t terminal_apply_conflict_tombstone_workorders_completed = 0;
    std::uint64_t terminal_apply_conflict_file_workorders_completed = 0;
    std::uint64_t terminal_apply_conflict_copies_preserved = 0;
    std::uint64_t terminal_apply_conflict_copies_reused = 0;
    std::uint64_t terminal_apply_conflict_remote_tombstones_applied = 0;
    std::uint64_t terminal_apply_conflict_remote_files_materialized = 0;
    std::uint64_t workorder_rows_claimed = 0;
    std::uint64_t workorder_rows_reclaimed = 0;
    std::uint64_t workorder_rows_completed = 0;
    std::uint64_t chunks_written = 0;
    std::uint64_t bytes_written = 0;
};

// One owning publication value freezes the exact authority and observation
// fields that will be serialized.  The codec validates and emits this same
// value; it does not retain access to the broad daemon option/result model.
struct SyncDaemonHeartbeatPublication final {
    SyncDaemonHeartbeatDocument document;
    SyncDaemonHeartbeatServiceLifecycleObservation service_lifecycle;
    SyncDaemonHeartbeatLeaseObservation lease;
    SyncDaemonHeartbeatProgressObservation progress;
};

// Pure lifecycle classification shared by daemon preflight and operator status.
// A healthy live daemon intentionally blocks a second start without requiring
// operator attention; a stale heartbeat authorizes re-entry only when durable
// owner authority is no longer live and the exact process incarnation is not.
struct SyncDaemonHeartbeatLifecycleEvaluation final {
    bool existing_fresh = false;
    bool existing_stale = false;
    bool service_start_allowed = false;
    bool operator_attention_required = false;
    bool reentry_from_stale_heartbeat = false;
    std::string reason;
};

// Decodes canonical v1 and v2 authority fields. V1 is retained only as legacy
// PID-only evidence; v2 requires a typed process-incarnation observation.
// Missing fields, wrong JSON types, non-exact integers, stale-horizon
// contradictions, malformed identities, and final/release contradictions throw
// before policy consumes the document.
SyncDaemonHeartbeatDocument decode_sync_daemon_heartbeat_document_or_throw(
    const Json& root);

SyncDaemonHeartbeatLifecycleEvaluation
evaluate_sync_daemon_heartbeat_lifecycle_or_throw(
    const SyncDaemonHeartbeatDocument& document,
    bool scheduler_clock_provided,
    std::uint64_t observed_at_epoch,
    bool durable_owner_live,
    SyncProcessIdentityMatchKind process_match_kind,
    const std::string& process_match_reason);

// Serializes one complete, already-frozen v2 publication.  The exact value
// validated here is the value emitted.  Locale-sensitive integer formatting and
// documents larger than the reader's bound are rejected before publication.
std::string encode_sync_daemon_heartbeat_document_or_throw(
    const SyncDaemonHeartbeatPublication& publication);

}  // namespace anonsync
