#include "anonsync_core.hpp"
#include "sync_daemon_heartbeat_publication.hpp"

#include <cstdint>
#include <iostream>
#include <string>

namespace {

using anonsync::SyncDaemonHeartbeatPublication;
using anonsync::SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions;
using anonsync::SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult;
using anonsync::encode_sync_daemon_heartbeat_document_or_throw;
using anonsync::make_sync_daemon_heartbeat_publication_or_throw;

struct TestState final {
    std::uint64_t passed = 0;
    std::uint64_t failed = 0;

    void require(bool condition, const std::string& label) {
        if (condition) {
            ++passed;
        } else {
            ++failed;
            std::cerr << "FAIL: " << label << "\n";
        }
    }
};

void test_complete_snapshot_mapping(TestState& test) {
    SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions options;
    options.sqlite_path = "/tmp/anonsync-publication.db";
    options.session_id = "session-publication";
    options.daemon_heartbeat_stale_after_seconds = 23;

    SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult result;
    result.service_instance_id =
        "sync-daemon-service-instance:v1:" + std::string(64, 'a');
    result.service_restart_epoch = 71;
    result.daemon_heartbeat_process_id = 4242;
    result.daemon_heartbeat_process_identity_format =
        "linux-proc-starttime-v1";
    result.daemon_heartbeat_process_boot_id =
        "01234567-89ab-cdef-0123-456789abcdef";
    result.daemon_heartbeat_process_start_token = "987654";
    result.daemon_id = "daemon-publication";
    result.worker_id = "worker-publication";

    result.daemon_owner_lock_required = true;
    result.daemon_owner_lock_acquired = true;
    result.daemon_owner_lock_released = false;
    result.daemon_owner_lock_reclaimed_expired = true;
    result.daemon_owner_lock_id =
        "sync-resume-daemon-owner-lock:v1:" + std::string(64, 'b');
    result.daemon_owner_lock_epoch = 73;
    result.daemon_owner_lock_acquired_at_epoch = 90;
    result.daemon_owner_lock_expires_at_epoch = 140;
    result.daemon_owner_lock_released_at_epoch = 0;

    result.service_lifecycle_preflight_checked = true;
    result.service_lifecycle_preflight_passed = true;
    result.service_lifecycle_live_owner_blocked = false;
    result.service_lifecycle_heartbeat_checked = true;
    result.service_lifecycle_heartbeat_existing_loaded = true;
    result.service_lifecycle_heartbeat_existing_final = false;
    result.service_lifecycle_heartbeat_existing_fresh = false;
    result.service_lifecycle_heartbeat_existing_stale = true;
    result.service_lifecycle_reentry_from_stale_heartbeat = true;
    result.service_lifecycle_preflight_reason = "stale owner retired";

    result.final_worker_lease_id = "lease-publication";
    result.final_worker_lease_epoch = 101;
    result.next_worker_lease_epoch = 102;
    result.next_scheduler_now_epoch = 103;

    result.passes_attempted = 11;
    result.passes_completed = 12;
    result.mutating_passes = 13;
    result.idle_passes = 14;
    result.startup_sidecar_recovery_attempted = true;
    result.startup_sidecar_recovery_completed = true;
    result.startup_sidecar_recovery_checkpoint_schema_version = "v19";
    result.startup_sidecar_recovery_archived_checkpoint_migration_backfill_checked =
        true;
    result.startup_sidecar_recovery_archived_checkpoint_exact_startup_hydration_supported =
        true;
    result.startup_sidecar_recovery_archived_checkpoint_migration_backfill_required =
        true;
    result.startup_sidecar_recovery_archived_checkpoint_migration_backfill_blocked_missing_lineage =
        true;
    result.startup_sidecar_recovery_archived_checkpoint_claimed_paths_blocked_by_missing_lineage =
        15;
    result.terminal_apply_workorders_checked = 16;
    result.terminal_apply_workorders_inserted = 17;
    result.terminal_apply_workorders_completed = 18;
    result.terminal_apply_workorders_already_completed = 19;
    result.terminal_apply_tombstone_workorders_completed = 20;
    result.terminal_apply_tombstone_targets_removed = 21;
    result.terminal_apply_tombstone_targets_already_absent = 22;
    result.terminal_apply_conflict_tombstone_workorders_completed = 23;
    result.terminal_apply_conflict_file_workorders_completed = 24;
    result.terminal_apply_conflict_copies_preserved = 25;
    result.terminal_apply_conflict_copies_reused = 26;
    result.terminal_apply_conflict_remote_tombstones_applied = 27;
    result.terminal_apply_conflict_remote_files_materialized = 28;
    result.workorder_rows_claimed = 29;
    result.workorder_rows_reclaimed = 30;
    result.workorder_rows_completed = 31;
    result.chunks_written = 32;
    result.bytes_written = 33000;

    const SyncDaemonHeartbeatPublication publication =
        make_sync_daemon_heartbeat_publication_or_throw(
            options,
            result,
            "scheduler-pass-completed",
            110,
            133,
            false,
            "publication snapshot");

    const auto& document = publication.document;
    test.require(
        document.format == "anonsync-sync-daemon-service-heartbeat-v2" &&
            document.revision_id == "rev0840" &&
            document.operation == "sync-daemon-service-heartbeat" &&
            document.service_instance_id == result.service_instance_id &&
            document.service_restart_epoch == 71 &&
            document.state == "scheduler-pass-completed" && !document.final &&
            document.reason == "publication snapshot" &&
            document.heartbeat_epoch == 110 &&
            document.stale_after_seconds == 23 &&
            document.stale_at_epoch == 133,
        "adapter freezes current document markers and transition fields");
    test.require(
        document.process_id == 4242 && document.process_identity_present &&
            document.process_identity.format == "linux-proc-starttime-v1" &&
            document.process_identity.process_id == 4242 &&
            document.process_identity.boot_id ==
                "01234567-89ab-cdef-0123-456789abcdef" &&
            document.process_identity.start_token == "987654" &&
            document.checkpoint_path == "/tmp/anonsync-publication.db" &&
            document.session_id == "session-publication" &&
            document.daemon_id == "daemon-publication" &&
            document.worker_id == "worker-publication",
        "adapter freezes exact process and daemon identity evidence");
    test.require(
        document.owner_lock.required && document.owner_lock.acquired &&
            !document.owner_lock.released &&
            document.owner_lock.reclaimed_expired &&
            document.owner_lock.owner_lock_id == result.daemon_owner_lock_id &&
            document.owner_lock.owner_lock_epoch == 73 &&
            document.owner_lock.acquired_at_epoch == 90 &&
            document.owner_lock.expires_at_epoch == 140 &&
            document.owner_lock.released_at_epoch == 0,
        "adapter freezes the complete owner-generation capability");

    const auto& lifecycle = publication.service_lifecycle;
    test.require(
        lifecycle.preflight_checked && lifecycle.preflight_passed &&
            !lifecycle.live_owner_blocked && lifecycle.heartbeat_checked &&
            lifecycle.existing_heartbeat_loaded &&
            !lifecycle.existing_heartbeat_final &&
            !lifecycle.existing_heartbeat_fresh &&
            lifecycle.existing_heartbeat_stale &&
            lifecycle.reentry_from_stale_heartbeat &&
            lifecycle.preflight_reason == "stale owner retired",
        "adapter freezes the complete lifecycle observation");

    const auto& lease = publication.lease;
    test.require(lease.worker_lease_id == "lease-publication" &&
                     lease.final_worker_lease_epoch == 101 &&
                     lease.next_worker_lease_epoch == 102 &&
                     lease.next_scheduler_now_epoch == 103,
                 "adapter freezes the complete lease observation");

    const auto& progress = publication.progress;
    test.require(
        progress.passes_attempted == 11 && progress.passes_completed == 12 &&
            progress.mutating_passes == 13 && progress.idle_passes == 14 &&
            progress.startup_sidecar_recovery_attempted &&
            progress.startup_sidecar_recovery_completed &&
            progress.checkpoint_schema_version == "v19" &&
            progress.archived_checkpoint_migration_backfill_checked &&
            progress.archived_checkpoint_exact_startup_hydration_supported &&
            progress.archived_checkpoint_migration_backfill_required &&
            progress.archived_checkpoint_migration_backfill_blocked_missing_lineage &&
            progress.archived_checkpoint_claimed_paths_blocked_by_missing_lineage ==
                15 &&
            progress.terminal_apply_workorders_checked == 16 &&
            progress.terminal_apply_workorders_inserted == 17 &&
            progress.terminal_apply_workorders_completed == 18 &&
            progress.terminal_apply_workorders_already_completed == 19 &&
            progress.terminal_apply_tombstone_workorders_completed == 20 &&
            progress.terminal_apply_tombstone_targets_removed == 21 &&
            progress.terminal_apply_tombstone_targets_already_absent == 22 &&
            progress.terminal_apply_conflict_tombstone_workorders_completed ==
                23 &&
            progress.terminal_apply_conflict_file_workorders_completed == 24 &&
            progress.terminal_apply_conflict_copies_preserved == 25 &&
            progress.terminal_apply_conflict_copies_reused == 26 &&
            progress.terminal_apply_conflict_remote_tombstones_applied == 27 &&
            progress.terminal_apply_conflict_remote_files_materialized == 28 &&
            progress.workorder_rows_claimed == 29 &&
            progress.workorder_rows_reclaimed == 30 &&
            progress.workorder_rows_completed == 31 &&
            progress.chunks_written == 32 && progress.bytes_written == 33000,
        "adapter freezes every serialized progress observation");

    options.sqlite_path = "/tmp/mutated.db";
    result.daemon_owner_lock_id = "mutated";
    result.bytes_written = 999;
    test.require(document.checkpoint_path == "/tmp/anonsync-publication.db" &&
                     document.owner_lock.owner_lock_id != "mutated" &&
                     progress.bytes_written == 33000,
                 "publication owns its snapshot instead of retaining broad model references");

    const std::string encoded =
        encode_sync_daemon_heartbeat_document_or_throw(publication);
    test.require(encoded.find("\"revision_id\": \"rev0840\"") !=
                         std::string::npos &&
                     encoded.find("\"bytes_written\": 33000") !=
                         std::string::npos &&
                     encoded.find("\"reentry_from_stale_heartbeat\": true") !=
                         std::string::npos,
                 "frozen adapter output is accepted unchanged by the codec");
}

}  // namespace

int main() {
    try {
        TestState test;
        test_complete_snapshot_mapping(test);
        std::cout << "sync daemon heartbeat publication tests passed: "
                  << test.passed << "/" << (test.passed + test.failed) << "\n";
        return test.failed == 0 ? 0 : 1;
    } catch (const std::exception& error) {
        std::cerr << "FATAL: " << error.what() << "\n";
        return 2;
    }
}
