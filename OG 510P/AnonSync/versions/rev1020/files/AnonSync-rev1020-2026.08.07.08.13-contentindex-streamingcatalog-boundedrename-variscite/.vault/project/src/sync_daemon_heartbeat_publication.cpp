#include "sync_daemon_heartbeat_publication.hpp"

#include "anonsync_core.hpp"

namespace anonsync {

SyncDaemonHeartbeatPublication
make_sync_daemon_heartbeat_publication_or_throw(
    const SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions& options,
    const SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult& result,
    const std::string& state,
    std::uint64_t heartbeat_epoch,
    std::uint64_t stale_at_epoch,
    bool final,
    const std::string& reason) {
    SyncDaemonHeartbeatPublication publication;
    SyncDaemonHeartbeatDocument& document = publication.document;
    document.format = "anonsync-sync-daemon-service-heartbeat-v2";
    document.revision_id = "rev0840";
    document.operation = "sync-daemon-service-heartbeat";
    document.service_instance_id = result.service_instance_id;
    document.service_restart_epoch = result.service_restart_epoch;
    document.state = state;
    document.final = final;
    document.reason = reason;
    document.heartbeat_epoch = heartbeat_epoch;
    document.stale_after_seconds = options.daemon_heartbeat_stale_after_seconds;
    document.stale_at_epoch = stale_at_epoch;
    document.process_id = result.daemon_heartbeat_process_id;
    document.process_identity_present = true;
    document.process_identity.format =
        result.daemon_heartbeat_process_identity_format;
    document.process_identity.process_id = result.daemon_heartbeat_process_id;
    document.process_identity.boot_id = result.daemon_heartbeat_process_boot_id;
    document.process_identity.start_token =
        result.daemon_heartbeat_process_start_token;
    document.checkpoint_path = options.sqlite_path;
    document.session_id = options.session_id;
    document.daemon_id = result.daemon_id;
    document.worker_id = result.worker_id;

    SyncDaemonHeartbeatOwnerLockDocument& owner = document.owner_lock;
    owner.required = result.daemon_owner_lock_required;
    owner.acquired = result.daemon_owner_lock_acquired;
    owner.released = result.daemon_owner_lock_released;
    owner.reclaimed_expired = result.daemon_owner_lock_reclaimed_expired;
    owner.owner_lock_id = result.daemon_owner_lock_id;
    owner.owner_lock_epoch = result.daemon_owner_lock_epoch;
    owner.acquired_at_epoch = result.daemon_owner_lock_acquired_at_epoch;
    owner.expires_at_epoch = result.daemon_owner_lock_expires_at_epoch;
    owner.released_at_epoch = result.daemon_owner_lock_released_at_epoch;

    SyncDaemonHeartbeatServiceLifecycleObservation& lifecycle =
        publication.service_lifecycle;
    lifecycle.preflight_checked = result.service_lifecycle_preflight_checked;
    lifecycle.preflight_passed = result.service_lifecycle_preflight_passed;
    lifecycle.live_owner_blocked = result.service_lifecycle_live_owner_blocked;
    lifecycle.heartbeat_checked = result.service_lifecycle_heartbeat_checked;
    lifecycle.existing_heartbeat_loaded =
        result.service_lifecycle_heartbeat_existing_loaded;
    lifecycle.existing_heartbeat_final =
        result.service_lifecycle_heartbeat_existing_final;
    lifecycle.existing_heartbeat_fresh =
        result.service_lifecycle_heartbeat_existing_fresh;
    lifecycle.existing_heartbeat_stale =
        result.service_lifecycle_heartbeat_existing_stale;
    lifecycle.reentry_from_stale_heartbeat =
        result.service_lifecycle_reentry_from_stale_heartbeat;
    lifecycle.preflight_reason = result.service_lifecycle_preflight_reason;

    SyncDaemonHeartbeatLeaseObservation& lease = publication.lease;
    lease.worker_lease_id = result.final_worker_lease_id;
    lease.final_worker_lease_epoch = result.final_worker_lease_epoch;
    lease.next_worker_lease_epoch = result.next_worker_lease_epoch;
    lease.next_scheduler_now_epoch = result.next_scheduler_now_epoch;

    SyncDaemonHeartbeatProgressObservation& progress = publication.progress;
    progress.passes_attempted = result.passes_attempted;
    progress.passes_completed = result.passes_completed;
    progress.mutating_passes = result.mutating_passes;
    progress.idle_passes = result.idle_passes;
    progress.startup_sidecar_recovery_attempted =
        result.startup_sidecar_recovery_attempted;
    progress.startup_sidecar_recovery_completed =
        result.startup_sidecar_recovery_completed;
    progress.checkpoint_schema_version =
        result.startup_sidecar_recovery_checkpoint_schema_version;
    progress.archived_checkpoint_migration_backfill_checked =
        result.startup_sidecar_recovery_archived_checkpoint_migration_backfill_checked;
    progress.archived_checkpoint_exact_startup_hydration_supported =
        result.startup_sidecar_recovery_archived_checkpoint_exact_startup_hydration_supported;
    progress.archived_checkpoint_migration_backfill_required =
        result.startup_sidecar_recovery_archived_checkpoint_migration_backfill_required;
    progress.archived_checkpoint_migration_backfill_blocked_missing_lineage =
        result.startup_sidecar_recovery_archived_checkpoint_migration_backfill_blocked_missing_lineage;
    progress.archived_checkpoint_claimed_paths_blocked_by_missing_lineage =
        result.startup_sidecar_recovery_archived_checkpoint_claimed_paths_blocked_by_missing_lineage;
    progress.terminal_apply_workorders_checked =
        result.terminal_apply_workorders_checked;
    progress.terminal_apply_workorders_inserted =
        result.terminal_apply_workorders_inserted;
    progress.terminal_apply_workorders_completed =
        result.terminal_apply_workorders_completed;
    progress.terminal_apply_workorders_already_completed =
        result.terminal_apply_workorders_already_completed;
    progress.terminal_apply_tombstone_workorders_completed =
        result.terminal_apply_tombstone_workorders_completed;
    progress.terminal_apply_tombstone_targets_removed =
        result.terminal_apply_tombstone_targets_removed;
    progress.terminal_apply_tombstone_targets_already_absent =
        result.terminal_apply_tombstone_targets_already_absent;
    progress.terminal_apply_conflict_tombstone_workorders_completed =
        result.terminal_apply_conflict_tombstone_workorders_completed;
    progress.terminal_apply_conflict_file_workorders_completed =
        result.terminal_apply_conflict_file_workorders_completed;
    progress.terminal_apply_conflict_copies_preserved =
        result.terminal_apply_conflict_copies_preserved;
    progress.terminal_apply_conflict_copies_reused =
        result.terminal_apply_conflict_copies_reused;
    progress.terminal_apply_conflict_remote_tombstones_applied =
        result.terminal_apply_conflict_remote_tombstones_applied;
    progress.terminal_apply_conflict_remote_files_materialized =
        result.terminal_apply_conflict_remote_files_materialized;
    progress.workorder_rows_claimed = result.workorder_rows_claimed;
    progress.workorder_rows_reclaimed = result.workorder_rows_reclaimed;
    progress.workorder_rows_completed = result.workorder_rows_completed;
    progress.chunks_written = result.chunks_written;
    progress.bytes_written = result.bytes_written;

    return publication;
}

}  // namespace anonsync
