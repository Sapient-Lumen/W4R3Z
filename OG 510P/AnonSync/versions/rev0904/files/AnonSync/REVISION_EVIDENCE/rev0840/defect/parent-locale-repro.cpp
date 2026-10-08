#include "anonsync_core_internal.hpp"
#include "sync_daemon_heartbeat_document.hpp"
#include <iostream>
#include <locale>
#include <string>

struct Grouping final : std::numpunct<char> {
    char do_thousands_sep() const override { return '_'; }
    std::string do_grouping() const override { return "\3"; }
};

int main() {
    anonsync::SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions options;
    options.sqlite_path = "/tmp/anonsync-checkpoint.db";
    options.session_id = "session-alpha";
    options.daemon_heartbeat_stale_after_seconds = 20;
    anonsync::SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult result;
    result.service_instance_id = "sync-daemon-service-instance:v1:" + std::string(64, 'c');
    result.service_restart_epoch = 7000;
    result.daemon_heartbeat_process_id = 41000;
    result.daemon_heartbeat_process_identity_format = "linux-proc-starttime-v1";
    result.daemon_heartbeat_process_boot_id = "01234567-89ab-cdef-0123-456789abcdef";
    result.daemon_heartbeat_process_start_token = "987654";
    result.daemon_id = "daemon-alpha";
    result.worker_id = "worker-alpha";
    result.daemon_owner_lock_required = true;
    result.daemon_owner_lock_acquired = true;
    result.daemon_owner_lock_id = "sync-resume-daemon-owner-lock:v1:" + std::string(64, 'd');
    result.daemon_owner_lock_epoch = 3000;
    result.daemon_owner_lock_acquired_at_epoch = 90000;
    result.daemon_owner_lock_expires_at_epoch = 130000;
    std::locale::global(std::locale(std::locale::classic(), new Grouping));
    std::cout << anonsync::encode_sync_daemon_heartbeat_document_or_throw(
        options, result, "scheduler-pass-started", 100000, 100020, false, "locale repro");
}
