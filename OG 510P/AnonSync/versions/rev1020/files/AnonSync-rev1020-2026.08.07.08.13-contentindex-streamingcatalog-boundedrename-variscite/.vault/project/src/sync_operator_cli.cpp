#include "anonsync_core.hpp"
#include "anonsync_core_internal.hpp"
#include "sync_atomic_file_publication.hpp"
#include "sync_bounded_regular_file.hpp"

#include <cstdint>
#include <filesystem>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>

namespace anonsync {
namespace fs = std::filesystem;

namespace {

SyncValidationResult sync_operator_cli_ok_result() {
    return {true, ""};
}

fs::path sync_operator_cli_absolute_lexically_normal_path_or_throw(const std::string& raw_path, const std::string& label) {
    if (raw_path.empty()) throw std::invalid_argument(label + " is empty");
    std::error_code ec;
    fs::path absolute = fs::absolute(fs::path(raw_path), ec);
    if (ec) throw std::invalid_argument(label + " could not be resolved: " + ec.message());
    return absolute.lexically_normal();
}

class SyncOperatorRepairOwnerLeaseGuard final {
public:
    SyncOperatorRepairOwnerLeaseGuard() = default;
    SyncOperatorRepairOwnerLeaseGuard(
        const SyncOperatorRepairOwnerLeaseGuard&) = delete;
    SyncOperatorRepairOwnerLeaseGuard& operator=(
        const SyncOperatorRepairOwnerLeaseGuard&) = delete;
    SyncOperatorRepairOwnerLeaseGuard(
        SyncOperatorRepairOwnerLeaseGuard&&) = delete;
    SyncOperatorRepairOwnerLeaseGuard& operator=(
        SyncOperatorRepairOwnerLeaseGuard&&) = delete;

    ~SyncOperatorRepairOwnerLeaseGuard() {
        if (armed_) {
            (void)sync_internal_release_checkpoint_mutation_owner_lease(
                sqlite_path_, session_id_, capability_, release_at_epoch_);
        }
    }

    void arm(
        std::string sqlite_path,
        std::string session_id,
        SyncSessionCheckpointDaemonOwnerCapability capability,
        std::uint64_t release_at_epoch) {
        if (armed_) {
            throw std::logic_error(
                "sync operator repair owner lease guard was already armed");
        }
        sqlite_path_ = std::move(sqlite_path);
        session_id_ = std::move(session_id);
        capability_ = std::move(capability);
        release_at_epoch_ = release_at_epoch;
        armed_ = true;
    }

    SyncValidationResult release_now() {
        if (!armed_) {
            return {false,
                    "sync operator repair owner lease guard is not armed"};
        }
        SyncValidationResult released =
            sync_internal_release_checkpoint_mutation_owner_lease(
                sqlite_path_, session_id_, capability_, release_at_epoch_);
        if (released.ok) armed_ = false;
        return released;
    }

private:
    std::string sqlite_path_;
    std::string session_id_;
    SyncSessionCheckpointDaemonOwnerCapability capability_;
    std::uint64_t release_at_epoch_ = 0;
    bool armed_ = false;
};

}  // namespace

std::string sync_cli_json_bool(bool value) {
    return value ? "true" : "false";
}

void append_sync_checkpoint_peer_transport_ingress_status_json(std::ostringstream& out,
                                                               const SyncSessionCheckpointOperatorStatusResult& status) {
    out << "    \"peer_transport_ingress_table_present\": " << sync_cli_json_bool(status.peer_transport_ingress_table_present) << ",\n"
        << "    \"peer_transport_ingress_total_rows\": " << status.peer_transport_ingress_total_rows << ",\n"
        << "    \"peer_transport_ingress_open_rows\": " << status.peer_transport_ingress_open_rows << ",\n"
        << "    \"peer_transport_ingress_open_bytes\": " << status.peer_transport_ingress_open_bytes << ",\n"
        << "    \"peer_transport_ingress_queued_rows\": " << status.peer_transport_ingress_queued_rows << ",\n"
        << "    \"peer_transport_ingress_queued_bytes\": " << status.peer_transport_ingress_queued_bytes << ",\n"
        << "    \"peer_transport_ingress_claimed_rows\": " << status.peer_transport_ingress_claimed_rows << ",\n"
        << "    \"peer_transport_ingress_claimed_bytes\": " << status.peer_transport_ingress_claimed_bytes << ",\n"
        << "    \"peer_transport_ingress_completed_rows\": " << status.peer_transport_ingress_completed_rows << ",\n"
        << "    \"peer_transport_ingress_completed_bytes\": " << status.peer_transport_ingress_completed_bytes << ",\n"
        << "    \"peer_transport_ingress_failed_rows\": " << status.peer_transport_ingress_failed_rows << ",\n"
        << "    \"peer_transport_ingress_failed_bytes\": " << status.peer_transport_ingress_failed_bytes << ",\n"
        << "    \"peer_transport_ingress_abandoned_rows\": " << status.peer_transport_ingress_abandoned_rows << ",\n"
        << "    \"peer_transport_ingress_abandoned_bytes\": " << status.peer_transport_ingress_abandoned_bytes << ",\n"
        << "    \"peer_transport_ingress_retention_event_table_present\": " << sync_cli_json_bool(status.peer_transport_ingress_retention_event_table_present) << ",\n"
        << "    \"peer_transport_ingress_retention_event_rows\": " << status.peer_transport_ingress_retention_event_rows << ",\n"
        << "    \"peer_transport_ingress_retention_drained_rows\": " << status.peer_transport_ingress_retention_drained_rows << ",\n"
        << "    \"peer_transport_ingress_retention_drained_bytes\": " << status.peer_transport_ingress_retention_drained_bytes << ",\n"
        << "    \"peer_transport_ingress_terminal_retention_candidate_rows\": " << status.peer_transport_ingress_terminal_retention_candidate_rows << ",\n"
        << "    \"peer_transport_ingress_terminal_retention_candidate_bytes\": " << status.peer_transport_ingress_terminal_retention_candidate_bytes << ",\n"
        << "    \"peer_transport_authority_denial_table_present\": " << sync_cli_json_bool(status.peer_transport_authority_denial_table_present) << ",\n"
        << "    \"peer_transport_authority_denied_rows\": " << status.peer_transport_authority_denied_rows << ",\n"
        << "    \"peer_transport_authority_denied_bytes\": " << status.peer_transport_authority_denied_bytes << ",\n"
        << "    \"peer_transport_authority_superseded_expired_denied_rows\": " << status.peer_transport_authority_superseded_expired_denied_rows << ",\n"
        << "    \"peer_transport_authority_superseded_expired_denied_bytes\": " << status.peer_transport_authority_superseded_expired_denied_bytes << ",\n"
        << "    \"peer_transport_authority_supersession_table_present\": " << sync_cli_json_bool(status.peer_transport_authority_supersession_table_present) << ",\n"
        << "    \"peer_transport_authority_supersession_rows\": " << status.peer_transport_authority_supersession_rows << ",\n"
        << "    \"peer_transport_authority_denial_retention_candidate_rows\": " << status.peer_transport_authority_denial_retention_candidate_rows << ",\n"
        << "    \"peer_transport_authority_denial_retention_candidate_bytes\": " << status.peer_transport_authority_denial_retention_candidate_bytes << ",\n"
        << "    \"peer_transport_ingress_retry_ready_rows\": " << status.peer_transport_ingress_retry_ready_rows << ",\n"
        << "    \"peer_transport_ingress_retry_waiting_rows\": " << status.peer_transport_ingress_retry_waiting_rows << ",\n"
        << "    \"peer_transport_ingress_live_claim_rows\": " << status.peer_transport_ingress_live_claim_rows << ",\n"
        << "    \"peer_transport_ingress_expired_claim_rows\": " << status.peer_transport_ingress_expired_claim_rows << ",\n"
        << "    \"peer_transport_ingress_total_attempts\": " << status.peer_transport_ingress_total_attempts << ",\n"
        << "    \"peer_transport_ingress_next_action\": \"" << json_escape(status.peer_transport_ingress_next_action) << "\",\n";
}

std::uint64_t sync_cli_u64_or_throw(long long value, const std::string& label) {
    if (value < 0) throw std::runtime_error(label + " must be nonnegative");
    return static_cast<std::uint64_t>(value);
}

std::uint64_t sync_cli_positive_u64_or_throw(long long value, const std::string& label) {
    if (value <= 0) throw std::runtime_error(label + " must be positive");
    return static_cast<std::uint64_t>(value);
}


bool sync_cli_lower_alnum(char c) {
    return (c >= 'a' && c <= 'z') || (c >= '0' && c <= '9');
}

void sync_cli_portable_id_or_throw(const std::string& value, const std::string& label) {
    if (value.empty() || value.size() > 128 || !sync_cli_lower_alnum(value.front()) || !sync_cli_lower_alnum(value.back())) {
        throw std::runtime_error(label + " must be lowercase portable sync id");
    }
    for (char raw_c : value) {
        const unsigned char raw = static_cast<unsigned char>(raw_c);
        const char c = static_cast<char>(raw);
        if (sync_cli_lower_alnum(c) || c == '.' || c == '_' || c == '-') continue;
        throw std::runtime_error(label + " must be lowercase portable sync id");
    }
}

void append_sync_peer_sqlite_write_contention_json(
    std::ostringstream& out,
    const SyncPeerTransportSqliteWriteContentionResult& contention,
    const std::string& indent) {
    out << indent << "\"sqlite_write_contention\": {\n"
        << indent << "  \"configured_busy_timeout_ms\": " << contention.configured_busy_timeout_ms << ",\n"
        << indent << "  \"busy_handler_installed\": " << sync_cli_json_bool(contention.busy_handler_installed) << ",\n"
        << indent << "  \"contention_observed\": " << sync_cli_json_bool(contention.contention_observed) << ",\n"
        << indent << "  \"sqlite_busy\": " << sync_cli_json_bool(contention.sqlite_busy) << ",\n"
        << indent << "  \"sqlite_locked\": " << sync_cli_json_bool(contention.sqlite_locked) << ",\n"
        << indent << "  \"busy_timeout_exhausted\": " << sync_cli_json_bool(contention.busy_timeout_exhausted) << ",\n"
        << indent << "  \"busy_handler_invocations\": " << contention.busy_handler_invocations << ",\n"
        << indent << "  \"busy_sleep_ms\": " << contention.busy_sleep_ms << ",\n"
        << indent << "  \"write_lock_attempts\": " << contention.write_lock_attempts << ",\n"
        << indent << "  \"write_locks_acquired\": " << contention.write_locks_acquired << ",\n"
        << indent << "  \"write_lock_wait_elapsed_ms\": " << contention.write_lock_wait_elapsed_ms << ",\n"
        << indent << "  \"primary_result_code\": " << contention.primary_result_code << ",\n"
        << indent << "  \"extended_result_code\": " << contention.extended_result_code << ",\n"
        << indent << "  \"result_code_name\": \"" << json_escape(contention.result_code_name) << "\",\n"
        << indent << "  \"failure_operation\": \"" << json_escape(contention.failure_operation) << "\",\n"
        << indent << "  \"sqlite_runtime_version\": \"" << json_escape(contention.sqlite_runtime_version) << "\",\n"
        << indent << "  \"sqlite_runtime_source_id\": \"" << json_escape(contention.sqlite_runtime_source_id) << "\",\n"
        << indent << "  \"sqlite_journal_mode\": \"" << json_escape(contention.sqlite_journal_mode) << "\",\n"
        << indent << "  \"sqlite_durability_profile_checked\": " << sync_cli_json_bool(contention.sqlite_durability_profile_checked) << ",\n"
        << indent << "  \"sqlite_runtime_bundled\": " << sync_cli_json_bool(contention.sqlite_runtime_bundled) << ",\n"
        << indent << "  \"sqlite_wal_reset_fix_known\": " << sync_cli_json_bool(contention.sqlite_wal_reset_fix_known) << ",\n"
        << indent << "  \"sqlite_rollback_journal_fallback_active\": " << sync_cli_json_bool(contention.sqlite_rollback_journal_fallback_active) << "\n"
        << indent << "}";
}

std::string sync_peer_ingress_retention_report_json(const SyncValidationResult& run,
                                                    const SyncPeerTransportIngressRetentionOptions& options,
                                                    const SyncPeerTransportIngressRetentionResult& result) {
    std::ostringstream out;
    out << "{\n"
        << "  \"format\": \"anonsync-sync-peer-ingress-retention-operator-report-v2\",\n"
        << "  \"revision_id\": \"rev0765\",\n"
        << "  \"operation\": \"sync-peer-ingress-retention\",\n"
        << "  \"ok\": " << sync_cli_json_bool(run.ok) << ",\n"
        << "  \"reason\": \"" << json_escape(run.reason) << "\",\n"
        << "  \"input\": {\n"
        << "    \"checkpoint_path\": \"" << json_escape(options.sqlite_path) << "\",\n"
        << "    \"session_id\": \"" << json_escape(options.session_id) << "\",\n"
        << "    \"operator_id\": \"" << json_escape(options.operator_id) << "\",\n"
        << "    \"retention_now_epoch\": " << options.retention_now_epoch << ",\n"
        << "    \"completed_older_than_epoch\": " << options.completed_older_than_epoch << ",\n"
        << "    \"abandoned_older_than_epoch\": " << options.abandoned_older_than_epoch << ",\n"
        << "    \"authority_denial_older_than_epoch\": " << options.authority_denial_older_than_epoch << ",\n"
        << "    \"max_completed_rows\": " << options.max_completed_rows << ",\n"
        << "    \"max_abandoned_rows\": " << options.max_abandoned_rows << ",\n"
        << "    \"max_authority_denial_rows\": " << options.max_authority_denial_rows << ",\n"
        << "    \"max_frame_bytes\": " << options.max_frame_bytes << ",\n"
        << "    \"max_chunk_count\": " << options.max_chunk_count << ",\n"
        << "    \"max_metadata_field_bytes\": " << options.max_metadata_field_bytes << ",\n"
        << "    \"dry_run\": " << sync_cli_json_bool(options.dry_run) << ",\n"
        << "    \"sqlite_busy_timeout_ms\": " << options.sqlite_busy_timeout_ms << ",\n"
        << "    \"operator_reason\": \"" << json_escape(options.reason) << "\"\n"
        << "  },\n"
        << "  \"result\": {\n"
        << "    \"retention_schema_loaded\": " << sync_cli_json_bool(result.retention_schema_loaded) << ",\n"
        << "    \"retention_completed\": " << sync_cli_json_bool(result.retention_completed) << ",\n"
        << "    \"retention_noop\": " << sync_cli_json_bool(result.retention_noop) << ",\n"
        << "    \"completed_eligible_rows\": " << result.completed_eligible_rows << ",\n"
        << "    \"completed_eligible_bytes\": " << result.completed_eligible_bytes << ",\n"
        << "    \"abandoned_eligible_rows\": " << result.abandoned_eligible_rows << ",\n"
        << "    \"abandoned_eligible_bytes\": " << result.abandoned_eligible_bytes << ",\n"
        << "    \"authority_denial_eligible_rows\": " << result.authority_denial_eligible_rows << ",\n"
        << "    \"authority_denial_eligible_bytes\": " << result.authority_denial_eligible_bytes << ",\n"
        << "    \"ingress_rows_drained\": " << result.ingress_rows_drained << ",\n"
        << "    \"ingress_bytes_drained\": " << result.ingress_bytes_drained << ",\n"
        << "    \"completed_rows_drained\": " << result.completed_rows_drained << ",\n"
        << "    \"completed_bytes_drained\": " << result.completed_bytes_drained << ",\n"
        << "    \"abandoned_rows_drained\": " << result.abandoned_rows_drained << ",\n"
        << "    \"abandoned_bytes_drained\": " << result.abandoned_bytes_drained << ",\n"
        << "    \"authority_denial_rows_drained\": " << result.authority_denial_rows_drained << ",\n"
        << "    \"authority_denial_bytes_drained\": " << result.authority_denial_bytes_drained << ",\n"
        << "    \"audit_events_written\": " << result.audit_events_written << ",\n";
    append_sync_peer_sqlite_write_contention_json(out, result.sqlite_write_contention, "    ");
    out << "\n  }\n"
        << "}\n";
    return out.str();
}

std::string sync_peer_authority_supersession_report_json(const SyncValidationResult& run,
                                                         const SyncPeerTransportAuthoritySupersessionRecordOptions& options,
                                                         const std::string& operator_id,
                                                         const SyncPeerTransportAuthoritySupersessionRecordResult& result,
                                                         const SyncPeerTransportIngressStatusResult& status) {
    std::ostringstream out;
    out << "{\n"
        << "  \"format\": \"anonsync-sync-peer-authority-supersession-operator-report-v2\",\n"
        << "  \"revision_id\": \"rev0765\",\n"
        << "  \"operation\": \"sync-peer-authority-supersession-record\",\n"
        << "  \"ok\": " << sync_cli_json_bool(run.ok) << ",\n"
        << "  \"reason\": \"" << json_escape(run.reason) << "\",\n"
        << "  \"input\": {\n"
        << "    \"checkpoint_path\": \"" << json_escape(options.sqlite_path) << "\",\n"
        << "    \"session_id\": \"" << json_escape(options.session_id) << "\",\n"
        << "    \"operator_id\": \"" << json_escape(operator_id) << "\",\n"
        << "    \"peer_id\": \"" << json_escape(options.peer_id) << "\",\n"
        << "    \"peer_session_id\": \"" << json_escape(options.peer_session_id) << "\",\n"
        << "    \"transport_instance_id\": \"" << json_escape(options.transport_instance_id) << "\",\n"
        << "    \"old_transport_key_id\": \"" << json_escape(options.old_transport_key_id) << "\",\n"
        << "    \"replacement_transport_key_id\": \"" << json_escape(options.replacement_transport_key_id) << "\",\n"
        << "    \"overlap_valid_from_epoch\": " << options.overlap_valid_from_epoch << ",\n"
        << "    \"overlap_valid_until_epoch\": " << options.overlap_valid_until_epoch << ",\n"
        << "    \"updated_at_epoch\": " << options.updated_at_epoch << ",\n"
        << "    \"sqlite_busy_timeout_ms\": " << options.sqlite_busy_timeout_ms << ",\n"
        << "    \"operator_reason\": \"" << json_escape(options.reason) << "\"\n"
        << "  },\n"
        << "  \"result\": {\n"
        << "    \"record_inserted\": " << sync_cli_json_bool(result.record_inserted) << ",\n"
        << "    \"record_updated\": " << sync_cli_json_bool(result.record_updated) << ",\n"
        << "    \"authority_supersession_table_present\": " << sync_cli_json_bool(status.authority_supersession_table_present) << ",\n"
        << "    \"authority_supersession_rows_after\": " << status.authority_supersession_rows << ",\n";
    append_sync_peer_sqlite_write_contention_json(out, result.sqlite_write_contention, "    ");
    out << "\n  }\n"
        << "}\n";
    return out.str();
}

std::string sync_checkpoint_operator_status_report_json(const SyncValidationResult& run,
                                                        const SyncSessionCheckpointOperatorStatusOptions& options,
                                                        const SyncSessionCheckpointOperatorStatusResult& status) {
    std::ostringstream out;
    out << "{\n"
        << "  \"format\": \"anonsync-sync-checkpoint-operator-status-report-v1\",\n"
        << "  \"revision_id\": \"rev0741\",\n"
        << "  \"operation\": \"sync-checkpoint-operator-status\",\n"
        << "  \"ok\": " << sync_cli_json_bool(run.ok) << ",\n"
        << "  \"reason\": \"" << json_escape(run.reason) << "\",\n"
        << "  \"input\": {\n"
        << "    \"checkpoint_path\": \"" << json_escape(options.sqlite_path) << "\",\n"
        << "    \"session_id\": \"" << json_escape(options.session_id) << "\",\n"
        << "    \"scheduler_now_epoch\": " << options.scheduler_now_epoch << ",\n"
        << "    \"daemon_heartbeat_path\": \"" << json_escape(options.daemon_heartbeat_path) << "\"\n"
        << "  },\n"
        << "  \"status\": {\n"
        << "    \"status_loaded\": " << sync_cli_json_bool(status.status_loaded) << ",\n"
        << "    \"query_only_enabled\": " << sync_cli_json_bool(status.query_only_enabled) << ",\n"
        << "    \"scheduler_clock_provided\": " << sync_cli_json_bool(status.scheduler_clock_provided) << ",\n"
        << "    \"schema_version\": \"" << json_escape(status.schema_version) << "\",\n"
        << "    \"schema_version_supported\": " << sync_cli_json_bool(status.schema_version_supported) << ",\n"
        << "    \"operator_attention_required\": " << sync_cli_json_bool(status.operator_attention_required) << ",\n"
        << "    \"safe_to_schedule\": " << sync_cli_json_bool(status.safe_to_schedule) << ",\n"
        << "    \"suggested_next_action\": \"" << json_escape(status.suggested_next_action) << "\",\n"
        << "    \"sidecar_review_events\": " << status.sidecar_review_events << ",\n"
        << "    \"pending_sidecar_review_events\": " << status.pending_sidecar_review_events << ",\n"
        << "    \"sidecar_review_repair_reset_events\": " << status.sidecar_review_repair_reset_events << ",\n"
        << "    \"repair_reset_workorder_rows_reset\": " << status.repair_reset_workorder_rows_reset << ",\n"
        << "    \"quarantined_workorder_rows\": " << status.quarantined_workorder_rows << ",\n"
        << "    \"abandoned_workorder_rows\": " << status.abandoned_workorder_rows << ",\n"
        << "    \"claimed_workorder_rows\": " << status.claimed_workorder_rows << ",\n"
        << "    \"completed_workorder_rows\": " << status.completed_workorder_rows << ",\n"
        << "    \"terminal_apply_tombstone_intent_rows\": " << status.terminal_apply_tombstone_intent_rows << ",\n"
        << "    \"pending_terminal_apply_tombstone_intent_rows\": " << status.pending_terminal_apply_tombstone_intent_rows << ",\n"
        << "    \"terminal_apply_conflict_tombstone_intent_rows\": " << status.terminal_apply_conflict_tombstone_intent_rows << ",\n"
        << "    \"pending_terminal_apply_conflict_tombstone_intent_rows\": " << status.pending_terminal_apply_conflict_tombstone_intent_rows << ",\n"
        << "    \"terminal_apply_conflict_file_intent_rows\": " << status.terminal_apply_conflict_file_intent_rows << ",\n"
        << "    \"pending_terminal_apply_conflict_file_intent_rows\": " << status.pending_terminal_apply_conflict_file_intent_rows << ",\n"
        << "    \"terminal_apply_workorder_rows\": " << status.terminal_apply_workorder_rows << ",\n"
        << "    \"pending_terminal_apply_workorder_rows\": " << status.pending_terminal_apply_workorder_rows << ",\n"
        << "    \"completed_terminal_apply_workorder_rows\": " << status.completed_terminal_apply_workorder_rows << ",\n"
        << "    \"tombstone_terminal_apply_workorder_rows\": " << status.tombstone_terminal_apply_workorder_rows << ",\n"
        << "    \"tombstone_terminal_apply_completed_rows\": " << status.tombstone_terminal_apply_completed_rows << ",\n"
        << "    \"tombstone_terminal_apply_targets_removed\": " << status.tombstone_terminal_apply_targets_removed << ",\n"
        << "    \"tombstone_terminal_apply_targets_already_absent\": " << status.tombstone_terminal_apply_targets_already_absent << ",\n"
        << "    \"conflict_terminal_apply_workorder_rows\": " << status.conflict_terminal_apply_workorder_rows << ",\n"
        << "    \"conflict_terminal_apply_completed_rows\": " << status.conflict_terminal_apply_completed_rows << ",\n"
        << "    \"conflict_terminal_apply_targets_removed\": " << status.conflict_terminal_apply_targets_removed << ",\n"
        << "    \"conflict_file_terminal_apply_workorder_rows\": " << status.conflict_file_terminal_apply_workorder_rows << ",\n"
        << "    \"conflict_file_terminal_apply_completed_rows\": " << status.conflict_file_terminal_apply_completed_rows << ",\n"
        << "    \"conflict_file_terminal_apply_targets_materialized\": " << status.conflict_file_terminal_apply_targets_materialized << ",\n";
    append_sync_checkpoint_peer_transport_ingress_status_json(out, status);
    out << "    \"live_claimed_workorder_rows\": " << status.live_claimed_workorder_rows << ",\n"
        << "    \"expired_claimed_workorder_rows\": " << status.expired_claimed_workorder_rows << ",\n"
        << "    \"retryable_expired_workorder_rows\": " << status.retryable_expired_workorder_rows << ",\n"
        << "    \"cooling_down_expired_workorder_rows\": " << status.cooling_down_expired_workorder_rows << ",\n"
        << "    \"daemon_lease_events\": " << status.daemon_lease_events << ",\n"
        << "    \"live_daemon_lease_events\": " << status.live_daemon_lease_events << ",\n"
        << "    \"expired_daemon_lease_events\": " << status.expired_daemon_lease_events << ",\n"
        << "    \"latest_daemon_id\": \"" << json_escape(status.latest_daemon_id) << "\",\n"
        << "    \"latest_daemon_worker_id\": \"" << json_escape(status.latest_daemon_worker_id) << "\",\n"
        << "    \"latest_daemon_worker_lease_epoch\": " << status.latest_daemon_worker_lease_epoch << ",\n"
        << "    \"latest_daemon_lease_live\": " << sync_cli_json_bool(status.latest_daemon_lease_live) << ",\n"
        << "    \"daemon_owner_lock_rows\": " << status.daemon_owner_lock_rows << ",\n"
        << "    \"daemon_owner_lock_held\": " << sync_cli_json_bool(status.daemon_owner_lock_held) << ",\n"
        << "    \"daemon_owner_lock_live\": " << sync_cli_json_bool(status.daemon_owner_lock_live) << ",\n"
        << "    \"daemon_owner_lock_daemon_id\": \"" << json_escape(status.daemon_owner_lock_daemon_id) << "\",\n"
        << "    \"daemon_owner_lock_worker_id\": \"" << json_escape(status.daemon_owner_lock_worker_id) << "\",\n"
        << "    \"daemon_owner_lock_id\": \"" << json_escape(status.daemon_owner_lock_id) << "\",\n"
        << "    \"daemon_owner_lock_epoch\": " << status.daemon_owner_lock_epoch << ",\n"
        << "    \"daemon_owner_lock_acquired_at_epoch\": " << status.daemon_owner_lock_acquired_at_epoch << ",\n"
        << "    \"daemon_owner_lock_expires_at_epoch\": " << status.daemon_owner_lock_expires_at_epoch << ",\n"
        << "    \"daemon_owner_lock_released_at_epoch\": " << status.daemon_owner_lock_released_at_epoch << ",\n"
        << "    \"daemon_heartbeat_requested\": " << sync_cli_json_bool(status.daemon_heartbeat_requested) << ",\n"
        << "    \"daemon_heartbeat_path_exists\": " << sync_cli_json_bool(status.daemon_heartbeat_path_exists) << ",\n"
        << "    \"daemon_heartbeat_path_is_regular_file\": " << sync_cli_json_bool(status.daemon_heartbeat_path_is_regular_file) << ",\n"
        << "    \"daemon_heartbeat_loaded\": " << sync_cli_json_bool(status.daemon_heartbeat_loaded) << ",\n"
        << "    \"daemon_heartbeat_format_ok\": " << sync_cli_json_bool(status.daemon_heartbeat_format_ok) << ",\n"
        << "    \"daemon_heartbeat_session_matches\": " << sync_cli_json_bool(status.daemon_heartbeat_session_matches) << ",\n"
        << "    \"daemon_heartbeat_checkpoint_matches\": " << sync_cli_json_bool(status.daemon_heartbeat_checkpoint_matches) << ",\n"
        << "    \"daemon_heartbeat_owner_lock_matches\": " << sync_cli_json_bool(status.daemon_heartbeat_owner_lock_matches) << ",\n"
        << "    \"daemon_heartbeat_process_identity_present\": " << sync_cli_json_bool(status.daemon_heartbeat_process_identity_present) << ",\n"
        << "    \"daemon_heartbeat_process_identity_checked\": " << sync_cli_json_bool(status.daemon_heartbeat_process_identity_checked) << ",\n"
        << "    \"daemon_heartbeat_process_identity_verification_available\": " << sync_cli_json_bool(status.daemon_heartbeat_process_identity_verification_available) << ",\n"
        << "    \"daemon_heartbeat_process_live\": " << sync_cli_json_bool(status.daemon_heartbeat_process_live) << ",\n"
        << "    \"daemon_heartbeat_process_identity_matches\": " << sync_cli_json_bool(status.daemon_heartbeat_process_identity_matches) << ",\n"
        << "    \"daemon_heartbeat_stale\": " << sync_cli_json_bool(status.daemon_heartbeat_stale) << ",\n"
        << "    \"daemon_heartbeat_attention_required\": " << sync_cli_json_bool(status.daemon_heartbeat_attention_required) << ",\n"
        << "    \"daemon_heartbeat_final\": " << sync_cli_json_bool(status.daemon_heartbeat_final) << ",\n"
        << "    \"daemon_heartbeat_path\": \"" << json_escape(status.daemon_heartbeat_path) << "\",\n"
        << "    \"daemon_heartbeat_error\": \"" << json_escape(status.daemon_heartbeat_error) << "\",\n"
        << "    \"daemon_heartbeat_format\": \"" << json_escape(status.daemon_heartbeat_format) << "\",\n"
        << "    \"daemon_heartbeat_state\": \"" << json_escape(status.daemon_heartbeat_state) << "\",\n"
        << "    \"daemon_heartbeat_reason\": \"" << json_escape(status.daemon_heartbeat_reason) << "\",\n"
        << "    \"daemon_heartbeat_checkpoint_path\": \"" << json_escape(status.daemon_heartbeat_checkpoint_path) << "\",\n"
        << "    \"daemon_heartbeat_session_id\": \"" << json_escape(status.daemon_heartbeat_session_id) << "\",\n"
        << "    \"daemon_heartbeat_daemon_id\": \"" << json_escape(status.daemon_heartbeat_daemon_id) << "\",\n"
        << "    \"daemon_heartbeat_worker_id\": \"" << json_escape(status.daemon_heartbeat_worker_id) << "\",\n"
        << "    \"daemon_heartbeat_owner_lock_id\": \"" << json_escape(status.daemon_heartbeat_owner_lock_id) << "\",\n"
        << "    \"daemon_heartbeat_process_identity_format\": \"" << json_escape(status.daemon_heartbeat_process_identity_format) << "\",\n"
        << "    \"daemon_heartbeat_process_boot_id\": \"" << json_escape(status.daemon_heartbeat_process_boot_id) << "\",\n"
        << "    \"daemon_heartbeat_process_start_token\": \"" << json_escape(status.daemon_heartbeat_process_start_token) << "\",\n"
        << "    \"daemon_heartbeat_process_identity_match_kind\": \"" << json_escape(status.daemon_heartbeat_process_identity_match_kind) << "\",\n"
        << "    \"daemon_heartbeat_epoch\": " << status.daemon_heartbeat_epoch << ",\n"
        << "    \"daemon_heartbeat_stale_after_seconds\": " << status.daemon_heartbeat_stale_after_seconds << ",\n"
        << "    \"daemon_heartbeat_stale_at_epoch\": " << status.daemon_heartbeat_stale_at_epoch << ",\n"
        << "    \"daemon_heartbeat_process_id\": " << status.daemon_heartbeat_process_id << ",\n"
        << "    \"daemon_heartbeat_owner_lock_epoch\": " << status.daemon_heartbeat_owner_lock_epoch << "\n"
        << "  }\n"
        << "}\n";
    return out.str();
}

std::string sync_checkpoint_sidecar_repair_reset_report_json(const SyncValidationResult& run,
                                                             const SyncSessionCheckpointBoundPeerSidecarReviewEventRepairResetOptions& options,
                                                             const SyncSessionCheckpointBoundPeerSidecarReviewEventRepairResetResult& result) {
    std::ostringstream out;
    out << "{\n"
        << "  \"format\": \"anonsync-sync-checkpoint-sidecar-repair-reset-report-v1\",\n"
        << "  \"revision_id\": \"rev0741\",\n"
        << "  \"operation\": \"sync-checkpoint-sidecar-repair-reset\",\n"
        << "  \"ok\": " << sync_cli_json_bool(run.ok) << ",\n"
        << "  \"reason\": \"" << json_escape(run.reason) << "\",\n"
        << "  \"input\": {\n"
        << "    \"checkpoint_path\": \"" << json_escape(options.sqlite_path) << "\",\n"
        << "    \"session_id\": \"" << json_escape(options.session_id) << "\",\n"
        << "    \"staging_root_path\": \"" << json_escape(options.staging_root_path) << "\",\n"
        << "    \"path\": \"" << json_escape(options.path.value) << "\",\n"
        << "    \"review_event_idempotency_key\": \"" << json_escape(options.review_event_idempotency_key) << "\",\n"
        << "    \"decision_operator_id\": \"" << json_escape(options.decision_operator_id) << "\",\n"
        << "    \"repair_at_epoch\": " << options.repair_at_epoch << "\n"
        << "  },\n"
        << "  \"repair_reset\": {\n"
        << "    \"review_event_found\": " << sync_cli_json_bool(result.review_event_found) << ",\n"
        << "    \"transaction_committed\": " << sync_cli_json_bool(result.transaction_committed) << ",\n"
        << "    \"repair_reset_event_written\": " << sync_cli_json_bool(result.repair_reset_event_written) << ",\n"
        << "    \"repair_reset_event_already_present\": " << sync_cli_json_bool(result.repair_reset_event_already_present) << ",\n"
        << "    \"review_category\": \"" << json_escape(result.review_category) << "\",\n"
        << "    \"repair_worker_id\": \"" << json_escape(result.repair_worker_id) << "\",\n"
        << "    \"repair_worker_lease_id\": \"" << json_escape(result.repair_worker_lease_id) << "\",\n"
        << "    \"sidecar_disposition\": \"" << json_escape(result.sidecar_disposition) << "\",\n"
        << "    \"staged_bytes_disposition\": \"" << json_escape(result.staged_bytes_disposition) << "\",\n"
        << "    \"staged_file_checked\": " << sync_cli_json_bool(result.staged_file_checked) << ",\n"
        << "    \"staged_file_left_in_place\": " << sync_cli_json_bool(result.staged_file_left_in_place) << ",\n"
        << "    \"workorder_rows_matched\": " << result.workorder_rows_matched << ",\n"
        << "    \"workorder_rows_reset\": " << result.workorder_rows_reset << ",\n"
        << "    \"workorder_rows_already_reset\": " << result.workorder_rows_already_reset << ",\n"
        << "    \"claimed_rows_reset\": " << result.claimed_rows_reset << ",\n"
        << "    \"quarantined_rows_reset\": " << result.quarantined_rows_reset << ",\n"
        << "    \"receipt_paths_considered\": " << result.receipt_paths_considered << ",\n"
        << "    \"receipts_removed\": " << result.receipts_removed << ",\n"
        << "    \"receipts_already_missing\": " << result.receipts_already_missing << ",\n"
        << "    \"retry_at_epoch\": " << result.retry_at_epoch << "\n"
        << "  }\n"
        << "}\n";
    return out.str();
}

std::string sync_checkpoint_daemon_run_report_json(const SyncValidationResult& run,
                                                   const SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions& options,
                                                   const SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult& result) {
    std::ostringstream out;
    out << "{\n"
        << "  \"format\": \"anonsync-sync-checkpoint-daemon-run-report-v1\",\n"
        << "  \"revision_id\": \"rev0741\",\n"
        << "  \"operation\": \"sync-checkpoint-daemon-run\",\n"
        << "  \"ok\": " << sync_cli_json_bool(run.ok) << ",\n"
        << "  \"reason\": \"" << json_escape(run.reason) << "\",\n"
        << "  \"input\": {\n"
        << "    \"checkpoint_path\": \"" << json_escape(options.sqlite_path) << "\",\n"
        << "    \"session_id\": \"" << json_escape(options.session_id) << "\",\n"
        << "    \"source_root_path\": \"" << json_escape(options.source_root_path) << "\",\n"
        << "    \"destination_root_path\": \"" << json_escape(options.destination_root_path) << "\",\n"
        << "    \"staging_root_path\": \"" << json_escape(options.staging_root_path) << "\",\n"
        << "    \"worker_id\": \"" << json_escape(options.worker_id) << "\",\n"
        << "    \"daemon_id\": \"" << json_escape(options.daemon_id) << "\",\n"
        << "    \"initial_worker_lease_epoch\": " << options.initial_worker_lease_epoch << ",\n"
        << "    \"initial_scheduler_now_epoch\": " << options.initial_scheduler_now_epoch << ",\n"
        << "    \"max_loop_passes\": " << options.max_loop_passes << ",\n"
        << "    \"max_scheduler_actions_per_pass\": " << options.max_scheduler_actions_per_pass << ",\n"
        << "    \"require_daemon_owner_lock\": " << sync_cli_json_bool(options.require_daemon_owner_lock) << ",\n"
        << "    \"daemon_heartbeat_path\": \"" << json_escape(options.daemon_heartbeat_path) << "\",\n"
        << "    \"daemon_heartbeat_stale_after_seconds\": " << options.daemon_heartbeat_stale_after_seconds << "\n"
        << "  },\n"
        << "  \"daemon_loop\": {\n"
        << "    \"daemon_loop_completed\": " << sync_cli_json_bool(result.daemon_loop_completed) << ",\n"
        << "    \"daemon_id\": \"" << json_escape(result.daemon_id) << "\",\n"
        << "    \"worker_id\": \"" << json_escape(result.worker_id) << "\",\n"
        << "    \"worker_lease_id\": \"" << json_escape(result.worker_lease_id) << "\",\n"
        << "    \"service_instance_id\": \"" << json_escape(result.service_instance_id) << "\",\n"
        << "    \"service_restart_epoch\": " << result.service_restart_epoch << ",\n"
        << "    \"service_lifecycle_preflight_checked\": " << sync_cli_json_bool(result.service_lifecycle_preflight_checked) << ",\n"
        << "    \"service_lifecycle_preflight_passed\": " << sync_cli_json_bool(result.service_lifecycle_preflight_passed) << ",\n"
        << "    \"service_lifecycle_live_owner_blocked\": " << sync_cli_json_bool(result.service_lifecycle_live_owner_blocked) << ",\n"
        << "    \"service_lifecycle_heartbeat_checked\": " << sync_cli_json_bool(result.service_lifecycle_heartbeat_checked) << ",\n"
        << "    \"service_lifecycle_heartbeat_existing_loaded\": " << sync_cli_json_bool(result.service_lifecycle_heartbeat_existing_loaded) << ",\n"
        << "    \"service_lifecycle_heartbeat_existing_final\": " << sync_cli_json_bool(result.service_lifecycle_heartbeat_existing_final) << ",\n"
        << "    \"service_lifecycle_heartbeat_existing_fresh\": " << sync_cli_json_bool(result.service_lifecycle_heartbeat_existing_fresh) << ",\n"
        << "    \"service_lifecycle_heartbeat_existing_stale\": " << sync_cli_json_bool(result.service_lifecycle_heartbeat_existing_stale) << ",\n"
        << "    \"service_lifecycle_reentry_from_stale_heartbeat\": " << sync_cli_json_bool(result.service_lifecycle_reentry_from_stale_heartbeat) << ",\n"
        << "    \"service_lifecycle_existing_heartbeat_process_identity_checked\": " << sync_cli_json_bool(result.service_lifecycle_existing_heartbeat_process_identity_checked) << ",\n"
        << "    \"service_lifecycle_existing_heartbeat_process_live\": " << sync_cli_json_bool(result.service_lifecycle_existing_heartbeat_process_live) << ",\n"
        << "    \"service_lifecycle_existing_heartbeat_process_identity_matches\": " << sync_cli_json_bool(result.service_lifecycle_existing_heartbeat_process_identity_matches) << ",\n"
        << "    \"service_lifecycle_existing_heartbeat_process_identity_match_kind\": \"" << json_escape(result.service_lifecycle_existing_heartbeat_process_identity_match_kind) << "\",\n"
        << "    \"service_lifecycle_preflight_reason\": \"" << json_escape(result.service_lifecycle_preflight_reason) << "\",\n"
        << "    \"service_lifecycle_existing_heartbeat_state\": \"" << json_escape(result.service_lifecycle_existing_heartbeat_state) << "\",\n"
        << "    \"service_lifecycle_existing_heartbeat_daemon_id\": \"" << json_escape(result.service_lifecycle_existing_heartbeat_daemon_id) << "\",\n"
        << "    \"service_lifecycle_existing_heartbeat_owner_lock_id\": \"" << json_escape(result.service_lifecycle_existing_heartbeat_owner_lock_id) << "\",\n"
        << "    \"service_lifecycle_existing_heartbeat_epoch\": " << result.service_lifecycle_existing_heartbeat_epoch << ",\n"
        << "    \"service_lifecycle_existing_heartbeat_stale_at_epoch\": " << result.service_lifecycle_existing_heartbeat_stale_at_epoch << ",\n"
        << "    \"final_worker_lease_epoch\": " << result.final_worker_lease_epoch << ",\n"
        << "    \"next_worker_lease_epoch\": " << result.next_worker_lease_epoch << ",\n"
        << "    \"next_scheduler_now_epoch\": " << result.next_scheduler_now_epoch << ",\n"
        << "    \"daemon_owner_lock_acquired\": " << sync_cli_json_bool(result.daemon_owner_lock_acquired) << ",\n"
        << "    \"daemon_owner_lock_released\": " << sync_cli_json_bool(result.daemon_owner_lock_released) << ",\n"
        << "    \"daemon_owner_lock_reclaimed_expired\": " << sync_cli_json_bool(result.daemon_owner_lock_reclaimed_expired) << ",\n"
        << "    \"daemon_owner_lock_id\": \"" << json_escape(result.daemon_owner_lock_id) << "\",\n"
        << "    \"daemon_owner_lock_epoch\": " << result.daemon_owner_lock_epoch << ",\n"
        << "    \"daemon_owner_lock_acquired_at_epoch\": " << result.daemon_owner_lock_acquired_at_epoch << ",\n"
        << "    \"daemon_owner_lock_expires_at_epoch\": " << result.daemon_owner_lock_expires_at_epoch << ",\n"
        << "    \"daemon_owner_lock_released_at_epoch\": " << result.daemon_owner_lock_released_at_epoch << ",\n"
        << "    \"daemon_heartbeat_requested\": " << sync_cli_json_bool(result.daemon_heartbeat_requested) << ",\n"
        << "    \"daemon_heartbeat_written\": " << sync_cli_json_bool(result.daemon_heartbeat_written) << ",\n"
        << "    \"daemon_heartbeat_final\": " << sync_cli_json_bool(result.daemon_heartbeat_final) << ",\n"
        << "    \"daemon_heartbeat_writes\": " << result.daemon_heartbeat_writes << ",\n"
        << "    \"daemon_heartbeat_path\": \"" << json_escape(result.daemon_heartbeat_path) << "\",\n"
        << "    \"daemon_heartbeat_state\": \"" << json_escape(result.daemon_heartbeat_state) << "\",\n"
        << "    \"daemon_heartbeat_epoch\": " << result.daemon_heartbeat_epoch << ",\n"
        << "    \"daemon_heartbeat_stale_at_epoch\": " << result.daemon_heartbeat_stale_at_epoch << ",\n"
        << "    \"daemon_heartbeat_process_id\": " << result.daemon_heartbeat_process_id << ",\n"
        << "    \"daemon_heartbeat_process_identity_format\": \"" << json_escape(result.daemon_heartbeat_process_identity_format) << "\",\n"
        << "    \"daemon_heartbeat_process_boot_id\": \"" << json_escape(result.daemon_heartbeat_process_boot_id) << "\",\n"
        << "    \"daemon_heartbeat_process_start_token\": \"" << json_escape(result.daemon_heartbeat_process_start_token) << "\",\n"
        << "    \"startup_sidecar_recovery_attempted\": " << sync_cli_json_bool(result.startup_sidecar_recovery_attempted) << ",\n"
        << "    \"startup_sidecar_recovery_completed\": " << sync_cli_json_bool(result.startup_sidecar_recovery_completed) << ",\n"
        << "    \"startup_sidecar_recovery_blocked_scheduling\": " << sync_cli_json_bool(result.startup_sidecar_recovery_blocked_scheduling) << ",\n"
        << "    \"startup_sidecar_recovery_checkpoint_schema_version\": \"" << json_escape(result.startup_sidecar_recovery_checkpoint_schema_version) << "\",\n"
        << "    \"startup_sidecar_recovery_checkpoint_schema_supported\": " << sync_cli_json_bool(result.startup_sidecar_recovery_checkpoint_schema_supported) << ",\n"
        << "    \"startup_sidecar_recovery_checkpoint_schema_has_manifest_chunks\": " << sync_cli_json_bool(result.startup_sidecar_recovery_checkpoint_schema_has_manifest_chunks) << ",\n"
        << "    \"startup_sidecar_recovery_checkpoint_schema_has_manifest_lineage\": " << sync_cli_json_bool(result.startup_sidecar_recovery_checkpoint_schema_has_manifest_lineage) << ",\n"
        << "    \"startup_sidecar_recovery_archived_checkpoint_migration_backfill_checked\": " << sync_cli_json_bool(result.startup_sidecar_recovery_archived_checkpoint_migration_backfill_checked) << ",\n"
        << "    \"startup_sidecar_recovery_archived_checkpoint_exact_startup_hydration_supported\": " << sync_cli_json_bool(result.startup_sidecar_recovery_archived_checkpoint_exact_startup_hydration_supported) << ",\n"
        << "    \"startup_sidecar_recovery_archived_checkpoint_migration_backfill_required\": " << sync_cli_json_bool(result.startup_sidecar_recovery_archived_checkpoint_migration_backfill_required) << ",\n"
        << "    \"startup_sidecar_recovery_archived_checkpoint_migration_backfill_blocked_missing_lineage\": " << sync_cli_json_bool(result.startup_sidecar_recovery_archived_checkpoint_migration_backfill_blocked_missing_lineage) << ",\n"
        << "    \"startup_sidecar_recovery_archived_checkpoint_claimed_paths_blocked_by_missing_lineage\": " << result.startup_sidecar_recovery_archived_checkpoint_claimed_paths_blocked_by_missing_lineage << ",\n"
        << "    \"startup_sidecar_recovery_archived_checkpoint_migration_backfill_reason\": \"" << json_escape(result.startup_sidecar_recovery_archived_checkpoint_migration_backfill_reason) << "\",\n"
        << "    \"passes_attempted\": " << result.passes_attempted << ",\n"
        << "    \"passes_completed\": " << result.passes_completed << ",\n"
        << "    \"mutating_passes\": " << result.mutating_passes << ",\n"
        << "    \"idle_passes\": " << result.idle_passes << ",\n"
        << "    \"terminal_apply_workorders_checked\": " << result.terminal_apply_workorders_checked << ",\n"
        << "    \"terminal_apply_workorders_inserted\": " << result.terminal_apply_workorders_inserted << ",\n"
        << "    \"terminal_apply_workorders_completed\": " << result.terminal_apply_workorders_completed << ",\n"
        << "    \"terminal_apply_workorders_already_completed\": " << result.terminal_apply_workorders_already_completed << ",\n"
        << "    \"terminal_apply_tombstone_workorders_completed\": " << result.terminal_apply_tombstone_workorders_completed << ",\n"
        << "    \"terminal_apply_tombstone_targets_removed\": " << result.terminal_apply_tombstone_targets_removed << ",\n"
        << "    \"terminal_apply_tombstone_targets_already_absent\": " << result.terminal_apply_tombstone_targets_already_absent << ",\n"
        << "    \"terminal_apply_conflict_tombstone_workorders_completed\": " << result.terminal_apply_conflict_tombstone_workorders_completed << ",\n"
        << "    \"terminal_apply_conflict_file_workorders_completed\": " << result.terminal_apply_conflict_file_workorders_completed << ",\n"
        << "    \"terminal_apply_conflict_copies_preserved\": " << result.terminal_apply_conflict_copies_preserved << ",\n"
        << "    \"terminal_apply_conflict_copies_reused\": " << result.terminal_apply_conflict_copies_reused << ",\n"
        << "    \"terminal_apply_conflict_remote_tombstones_applied\": " << result.terminal_apply_conflict_remote_tombstones_applied << ",\n"
        << "    \"terminal_apply_conflict_remote_files_materialized\": " << result.terminal_apply_conflict_remote_files_materialized << ",\n"
        << "    \"daemon_lease_events_written\": " << result.daemon_lease_events_written << ",\n"
        << "    \"daemon_lease_events_already_present\": " << result.daemon_lease_events_already_present << ",\n"
        << "    \"terminal_review_actions_observed\": " << result.terminal_review_actions_observed << ",\n"
        << "    \"mutations_blocked_by_terminal_review\": " << sync_cli_json_bool(result.mutations_blocked_by_terminal_review) << ",\n"
        << "    \"mutating_action_groups_blocked_by_terminal_review\": " << result.mutating_action_groups_blocked_by_terminal_review << ",\n"
        << "    \"mutating_actions_blocked_by_terminal_review\": " << result.mutating_actions_blocked_by_terminal_review << ",\n"
        << "    \"scheduler_actions_returned\": " << result.scheduler_actions_returned << ",\n"
        << "    \"scheduler_actions_deferred_by_limit\": " << result.scheduler_actions_deferred_by_limit << ",\n"
        << "    \"workorder_rows_claimed\": " << result.workorder_rows_claimed << ",\n"
        << "    \"workorder_rows_reclaimed\": " << result.workorder_rows_reclaimed << ",\n"
        << "    \"workorder_rows_quarantined\": " << result.workorder_rows_quarantined << ",\n"
        << "    \"workorder_rows_completed\": " << result.workorder_rows_completed << ",\n"
        << "    \"chunks_written\": " << result.chunks_written << ",\n"
        << "    \"receipts_reused\": " << result.receipts_reused << ",\n"
        << "    \"receipt_rows_upserted\": " << result.receipt_rows_upserted << ",\n"
        << "    \"bytes_written\": " << result.bytes_written << "\n"
        << "  }\n"
        << "}\n";
    return out.str();
}

int run_sync_checkpoint_operator_status_report_command(const std::string& checkpoint_path,
                                                        const std::string& session_id,
                                                        long long scheduler_now_epoch,
                                                        const std::string& report_path,
                                                        const std::string& daemon_heartbeat_path) {
    try {
        if (checkpoint_path.empty() || session_id.empty() || report_path.empty()) {
            std::cerr << "sync operator status requires --sync-checkpoint, --sync-session-id, and --sync-operator-status-report\n";
            return 64;
        }
        SyncSessionCheckpointOperatorStatusOptions options;
        options.sqlite_path = checkpoint_path;
        options.session_id = session_id;
        options.scheduler_now_epoch = sync_cli_u64_or_throw(scheduler_now_epoch, "sync operator status scheduler_now_epoch");
        options.daemon_heartbeat_path = daemon_heartbeat_path;
        SyncSessionCheckpointOperatorStatusResult status;
        SyncValidationResult run = load_sync_session_checkpoint_operator_status(options, status);
        write_sync_cli_report_json_or_throw(report_path, sync_checkpoint_operator_status_report_json(run, options, status), "sync checkpoint operator status report");
        if (!run.ok) {
            std::cerr << run.reason << "\n";
            return 1;
        }
        std::cout << "sync checkpoint operator status wrote " << report_path << " suggested_next_action=" << status.suggested_next_action << "\n";
        return 0;
    } catch (const std::exception& e) {
        std::cerr << e.what() << "\n";
        return 1;
    }
}

int run_sync_peer_ingress_retention_command(const std::string& checkpoint_path,
                                            const std::string& session_id,
                                            const std::string& operator_id,
                                            const std::string& reason,
                                            long long retention_now_epoch,
                                            long long completed_older_than_epoch,
                                            long long abandoned_older_than_epoch,
                                            long long authority_denial_older_than_epoch,
                                            long long max_completed_rows,
                                            long long max_abandoned_rows,
                                            long long max_authority_denial_rows,
                                            bool dry_run,
                                            const std::string& report_path,
                                            long long sqlite_busy_timeout_ms,
                                            long long max_frame_bytes,
                                            long long max_chunk_count,
                                            long long max_metadata_field_bytes) {
    try {
        if (checkpoint_path.empty() || session_id.empty() || operator_id.empty() || reason.empty() || report_path.empty()) {
            std::cerr << "sync peer ingress retention requires --sync-checkpoint, --sync-session-id, --sync-operator-id, --sync-retention-reason, --sync-retention-now-epoch, at least one cutoff, and --sync-peer-ingress-retention-report\n";
            return 64;
        }
        SyncPeerTransportIngressRetentionOptions options;
        options.sqlite_path = checkpoint_path;
        options.session_id = session_id;
        options.operator_id = operator_id;
        options.reason = reason;
        options.retention_now_epoch = sync_cli_positive_u64_or_throw(retention_now_epoch, "sync peer ingress retention retention_now_epoch");
        options.completed_older_than_epoch = sync_cli_u64_or_throw(completed_older_than_epoch, "sync peer ingress retention completed_older_than_epoch");
        options.abandoned_older_than_epoch = sync_cli_u64_or_throw(abandoned_older_than_epoch, "sync peer ingress retention abandoned_older_than_epoch");
        options.authority_denial_older_than_epoch = sync_cli_u64_or_throw(authority_denial_older_than_epoch, "sync peer ingress retention authority_denial_older_than_epoch");
        options.max_completed_rows = sync_cli_u64_or_throw(max_completed_rows, "sync peer ingress retention max_completed_rows");
        options.max_abandoned_rows = sync_cli_u64_or_throw(max_abandoned_rows, "sync peer ingress retention max_abandoned_rows");
        options.max_authority_denial_rows = sync_cli_u64_or_throw(max_authority_denial_rows, "sync peer ingress retention max_authority_denial_rows");
        options.max_frame_bytes = sync_cli_positive_u64_or_throw(max_frame_bytes, "sync peer ingress retention max_frame_bytes");
        options.max_chunk_count = sync_cli_positive_u64_or_throw(max_chunk_count, "sync peer ingress retention max_chunk_count");
        options.max_metadata_field_bytes = sync_cli_positive_u64_or_throw(max_metadata_field_bytes, "sync peer ingress retention max_metadata_field_bytes");
        options.dry_run = dry_run;
        options.sqlite_busy_timeout_ms = sync_cli_u64_or_throw(sqlite_busy_timeout_ms,
                                                               "sync peer ingress retention sqlite_busy_timeout_ms");
        SyncPeerTransportIngressRetentionResult result;
        SyncValidationResult run = drain_sync_peer_transport_ingress_retention(options, result);
        write_sync_cli_report_json_or_throw(report_path,
                                            sync_peer_ingress_retention_report_json(run, options, result),
                                            "sync peer ingress retention report");
        if (!run.ok) {
            std::cerr << run.reason << "\n";
            return 1;
        }
        std::cout << "sync peer ingress retention wrote " << report_path
                  << " dry_run=" << sync_cli_json_bool(result.dry_run)
                  << " drained_rows=" << (result.ingress_rows_drained + result.authority_denial_rows_drained)
                  << " audit_events=" << result.audit_events_written << "\n";
        return 0;
    } catch (const std::exception& e) {
        std::cerr << e.what() << "\n";
        return 1;
    }
}

int run_sync_peer_authority_supersession_command(const std::string& checkpoint_path,
                                                 const std::string& session_id,
                                                 const std::string& operator_id,
                                                 const std::string& peer_id,
                                                 const std::string& peer_session_id,
                                                 const std::string& transport_instance_id,
                                                 const std::string& old_transport_key_id,
                                                 const std::string& replacement_transport_key_id,
                                                 long long overlap_valid_from_epoch,
                                                 long long overlap_valid_until_epoch,
                                                 long long updated_at_epoch,
                                                 const std::string& reason,
                                                 const std::string& report_path,
                                                 long long sqlite_busy_timeout_ms) {
    try {
        if (checkpoint_path.empty() || session_id.empty() || operator_id.empty() || peer_id.empty() ||
            peer_session_id.empty() || transport_instance_id.empty() || old_transport_key_id.empty() ||
            replacement_transport_key_id.empty() || reason.empty() || report_path.empty()) {
            std::cerr << "sync peer authority supersession requires --sync-checkpoint, --sync-session-id, --sync-operator-id, --sync-peer-id, --sync-peer-session-id, --sync-transport-instance-id, --sync-old-transport-key-id, --sync-replacement-transport-key-id, --sync-supersession-overlap-from-epoch, --sync-supersession-overlap-until-epoch, --sync-operator-now-epoch, --sync-supersession-reason, and --sync-peer-authority-supersession-report\n";
            return 64;
        }
        sync_cli_portable_id_or_throw(operator_id, "sync peer authority supersession operator_id");
        SyncPeerTransportAuthoritySupersessionRecordOptions options;
        options.sqlite_path = checkpoint_path;
        options.session_id = session_id;
        options.peer_id = peer_id;
        options.peer_session_id = peer_session_id;
        options.transport_instance_id = transport_instance_id;
        options.old_transport_key_id = old_transport_key_id;
        options.replacement_transport_key_id = replacement_transport_key_id;
        options.overlap_valid_from_epoch = sync_cli_positive_u64_or_throw(overlap_valid_from_epoch, "sync peer authority supersession overlap_valid_from_epoch");
        options.overlap_valid_until_epoch = sync_cli_positive_u64_or_throw(overlap_valid_until_epoch, "sync peer authority supersession overlap_valid_until_epoch");
        options.updated_at_epoch = sync_cli_positive_u64_or_throw(updated_at_epoch, "sync peer authority supersession updated_at_epoch");
        options.reason = "operator=" + operator_id + "; " + reason;
        options.sqlite_busy_timeout_ms = sync_cli_u64_or_throw(sqlite_busy_timeout_ms,
                                                               "sync peer authority supersession sqlite_busy_timeout_ms");
        SyncPeerTransportAuthoritySupersessionRecordResult result;
        SyncValidationResult run = record_sync_peer_transport_authority_supersession(options, result);
        SyncPeerTransportIngressStatusResult status;
        if (run.ok) {
            SyncPeerTransportIngressStatusOptions status_options;
            status_options.sqlite_path = checkpoint_path;
            status_options.session_id = session_id;
            status_options.status_now_epoch = options.updated_at_epoch;
            SyncValidationResult status_run = load_sync_peer_transport_ingress_status(status_options, status);
            if (!status_run.ok) run = status_run;
        }
        write_sync_cli_report_json_or_throw(report_path,
                                            sync_peer_authority_supersession_report_json(run, options, operator_id, result, status),
                                            "sync peer authority supersession report");
        if (!run.ok) {
            std::cerr << run.reason << "\n";
            return 1;
        }
        std::cout << "sync peer authority supersession wrote " << report_path
                  << " inserted=" << sync_cli_json_bool(result.record_inserted)
                  << " updated=" << sync_cli_json_bool(result.record_updated)
                  << " supersession_rows=" << status.authority_supersession_rows << "\n";
        return 0;
    } catch (const std::exception& e) {
        std::cerr << e.what() << "\n";
        return 1;
    }
}

int run_sync_checkpoint_sidecar_repair_reset_command(const std::string& checkpoint_path,
                                                     const std::string& session_id,
                                                     const std::string& staging_root_path,
                                                     const std::string& sync_path,
                                                     const std::string& review_event_idempotency_key,
                                                     const std::string& decision_operator_id,
                                                     const std::string& decision_reason,
                                                     long long repair_at_epoch,
                                                     const std::string& repair_worker_id,
                                                     long long repair_worker_lease_epoch,
                                                     long long repair_worker_lease_seconds,
                                                     long long workorder_retry_backoff_seconds,
                                                     const std::string& report_path) {
    try {
        if (checkpoint_path.empty() || session_id.empty() || staging_root_path.empty() || sync_path.empty() ||
            review_event_idempotency_key.empty() || decision_operator_id.empty() || repair_worker_id.empty() || report_path.empty()) {
            std::cerr << "sync sidecar repair reset requires --sync-checkpoint, --sync-session-id, --sync-staging-root, --sync-path, --sync-review-event-key, --sync-operator-id, --sync-repair-at-epoch, --sync-repair-worker-id, and --sync-sidecar-repair-reset-report\n";
            return 64;
        }
        NormalizedSyncPath normalized_path;
        SyncValidationResult normalized = normalize_sync_relative_path(sync_path, normalized_path);
        if (!normalized.ok) {
            std::cerr << normalized.reason << "\n";
            return 64;
        }
        SyncSessionCheckpointBoundPeerSidecarReviewEventRepairResetOptions options;
        options.sqlite_path = checkpoint_path;
        options.session_id = session_id;
        options.staging_root_path = staging_root_path;
        options.path = normalized_path;
        options.review_event_idempotency_key = review_event_idempotency_key;
        options.decision_operator_id = decision_operator_id;
        options.decision_reason = decision_reason.empty() ? "sidecar-review-repaired-reset-by-operator-cli" : decision_reason;
        options.repair_at_epoch = sync_cli_positive_u64_or_throw(repair_at_epoch, "sync sidecar repair reset repair_at_epoch");
        options.repair_worker_id = repair_worker_id;
        options.repair_worker_lease_epoch = sync_cli_positive_u64_or_throw(repair_worker_lease_epoch, "sync sidecar repair reset repair_worker_lease_epoch");
        options.repair_worker_lease_seconds = sync_cli_positive_u64_or_throw(repair_worker_lease_seconds, "sync sidecar repair reset repair_worker_lease_seconds");
        options.workorder_retry_backoff_seconds = sync_cli_u64_or_throw(workorder_retry_backoff_seconds, "sync sidecar repair reset workorder_retry_backoff_seconds");
        SyncSessionCheckpointBoundPeerSidecarReviewEventRepairResetResult result;
        SyncInternalCheckpointMutationOwnerLease owner_lease;
        SyncValidationResult run =
            sync_internal_acquire_checkpoint_mutation_owner_lease(
                options.sqlite_path,
                options.session_id,
                "sync-operator-repair-cli",
                options.repair_worker_id,
                options.repair_at_epoch,
                60,
                owner_lease);
        SyncOperatorRepairOwnerLeaseGuard owner_guard;
        if (run.ok) {
            options.daemon_owner_capability = owner_lease.capability;
            owner_guard.arm(options.sqlite_path,
                            options.session_id,
                            owner_lease.capability,
                            options.repair_at_epoch);
            try {
                run = repair_reset_sync_session_checkpoint_bound_peer_sidecar_review_event(
                    options, result);
            } catch (const std::exception& e) {
                run = {
                    false,
                    std::string(
                        "sync sidecar repair reset threw after owner acquisition: ") +
                        e.what()};
            }
            const SyncValidationResult release_run = owner_guard.release_now();
            if (!release_run.ok) {
                if (run.ok) run = release_run;
                else run.reason += "; " + release_run.reason;
            }
        }
        write_sync_cli_report_json_or_throw(report_path, sync_checkpoint_sidecar_repair_reset_report_json(run, options, result), "sync checkpoint sidecar repair reset report");
        if (!run.ok) {
            std::cerr << run.reason << "\n";
            return 1;
        }
        std::cout << "sync sidecar repair reset wrote " << report_path << " reset_rows=" << result.workorder_rows_reset << " already_present=" << sync_cli_json_bool(result.repair_reset_event_already_present) << "\n";
        return 0;
    } catch (const std::exception& e) {
        std::cerr << e.what() << "\n";
        return 1;
    }
}

int run_sync_checkpoint_daemon_run_command(const std::string& checkpoint_path,
                                           const std::string& session_id,
                                           const std::string& source_root_path,
                                           const std::string& destination_root_path,
                                           const std::string& staging_root_path,
                                           const std::string& expected_folder_id,
                                           const std::string& expected_source_device_id,
                                           const std::string& expected_destination_device_id,
                                           const std::string& expected_peer_id,
                                           const std::string& peer_id,
                                           const std::string& peer_session_id,
                                           const std::string& worker_id,
                                           const std::string& daemon_id,
                                           long long initial_worker_lease_epoch,
                                           long long initial_scheduler_now_epoch,
                                           long long worker_lease_seconds,
                                           long long loop_tick_seconds,
                                           long long max_loop_passes,
                                           long long max_scheduler_actions_per_pass,
                                           long long workorder_retry_backoff_seconds,
                                           bool recover_bound_peer_sidecars_before_scheduling,
                                           bool require_daemon_owner_lock,
                                           const std::string& report_path,
                                           const std::string& daemon_heartbeat_path,
                                           long long daemon_heartbeat_stale_after_seconds) {
    try {
        if (checkpoint_path.empty() || session_id.empty() || source_root_path.empty() || destination_root_path.empty() ||
            staging_root_path.empty() || expected_folder_id.empty() || expected_source_device_id.empty() ||
            expected_destination_device_id.empty() || expected_peer_id.empty() || worker_id.empty() ||
            initial_scheduler_now_epoch <= 0 || report_path.empty()) {
            std::cerr << "sync daemon run requires --sync-checkpoint, --sync-session-id, --sync-source-root, --sync-destination-root, --sync-staging-root, --sync-expected-folder-id, --sync-expected-source-device-id, --sync-expected-destination-device-id, --sync-expected-peer-id, --sync-worker-id, --sync-daemon-now-epoch, and --sync-daemon-report\n";
            return 64;
        }
        SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions options;
        options.sqlite_path = checkpoint_path;
        options.session_id = session_id;
        options.source_root_path = source_root_path;
        options.destination_root_path = destination_root_path;
        options.staging_root_path = staging_root_path;
        options.expected_folder_id = expected_folder_id;
        options.expected_source_device_id = expected_source_device_id;
        options.expected_destination_device_id = expected_destination_device_id;
        options.expected_peer_id = expected_peer_id;
        options.peer_id = peer_id;
        options.peer_session_id = peer_session_id;
        options.worker_id = worker_id;
        options.daemon_id = daemon_id;
        options.initial_worker_lease_epoch = sync_cli_positive_u64_or_throw(initial_worker_lease_epoch, "sync daemon run initial_worker_lease_epoch");
        options.initial_scheduler_now_epoch = sync_cli_positive_u64_or_throw(initial_scheduler_now_epoch, "sync daemon run initial_scheduler_now_epoch");
        options.worker_lease_seconds = sync_cli_positive_u64_or_throw(worker_lease_seconds, "sync daemon run worker_lease_seconds");
        options.loop_tick_seconds = sync_cli_positive_u64_or_throw(loop_tick_seconds, "sync daemon run loop_tick_seconds");
        options.max_loop_passes = sync_cli_positive_u64_or_throw(max_loop_passes, "sync daemon run max_loop_passes");
        options.max_scheduler_actions_per_pass = sync_cli_u64_or_throw(max_scheduler_actions_per_pass, "sync daemon run max_scheduler_actions_per_pass");
        options.workorder_retry_backoff_seconds = sync_cli_u64_or_throw(workorder_retry_backoff_seconds, "sync daemon run workorder_retry_backoff_seconds");
        options.recover_bound_peer_sidecars_before_scheduling = recover_bound_peer_sidecars_before_scheduling;
        options.require_daemon_owner_lock = require_daemon_owner_lock;
        options.daemon_heartbeat_path = daemon_heartbeat_path;
        options.daemon_heartbeat_stale_after_seconds = sync_cli_u64_or_throw(daemon_heartbeat_stale_after_seconds, "sync daemon run daemon_heartbeat_stale_after_seconds");
        SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult result;
        SyncValidationResult run = run_sync_session_checkpoint_resume_transfer_workorder_daemon_loop(options, result);
        write_sync_cli_report_json_or_throw(report_path, sync_checkpoint_daemon_run_report_json(run, options, result), "sync checkpoint daemon run report");
        if (!run.ok) {
            std::cerr << run.reason << "\n";
            return 1;
        }
        std::cout << "sync daemon run wrote " << report_path << " passes=" << result.passes_completed << " completed=" << sync_cli_json_bool(result.daemon_loop_completed) << "\n";
        return 0;
    } catch (const std::exception& e) {
        std::cerr << e.what() << "\n";
        return 1;
    }
}




struct SyncOperatorRecoveryWorkflowConfig {
    std::string config_path;
    SyncSessionCheckpointOperatorStatusOptions status_options;
    bool repair_enabled = false;
    SyncSessionCheckpointBoundPeerSidecarReviewEventRepairResetOptions repair_options;
    std::string repair_owner_daemon_id = "sync-operator-repair";
    std::uint64_t repair_owner_lock_seconds = 60;
    bool daemon_enabled = false;
    SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions daemon_options;
};

Json load_sync_operator_recovery_workflow_config_json_or_throw(const std::string& config_path) {
    constexpr std::uint64_t kMaxWorkflowConfigJsonBytes = 128 * 1024;
    const fs::path path = sync_operator_cli_absolute_lexically_normal_path_or_throw(config_path,
                                                                  "sync operator recovery workflow config path");
    return parse_json_text(read_sync_bounded_regular_file_no_symlink_or_throw(path,
                                                                         kMaxWorkflowConfigJsonBytes,
                                                                         "sync operator recovery workflow config"));
}

const Json& sync_workflow_object_field_or_throw(const Json& obj,
                                                const std::string& field,
                                                const std::string& label) {
    const Json& value = obj.at(field);
    if (!value.is_object()) throw std::runtime_error(label + " must contain object field " + field);
    return value;
}

std::string sync_workflow_string_field_or_throw(const Json& obj,
                                                const std::string& field,
                                                const std::string& label) {
    const Json& value = obj.at(field);
    if (!value.is_string() || value.s.empty()) throw std::runtime_error(label + " must contain nonempty string field " + field);
    return value.s;
}

std::string sync_workflow_optional_string_field(const Json& obj,
                                                const std::string& field,
                                                const std::string& fallback = "") {
    const Json& value = obj.at(field);
    return value.is_string() ? value.s : fallback;
}

bool sync_workflow_bool_field(const Json& obj,
                              const std::string& field,
                              bool fallback = false) {
    const Json& value = obj.at(field);
    return value.is_bool() ? value.b : fallback;
}

std::uint64_t sync_workflow_required_positive_u64_field(const Json& obj,
                                                        const std::string& field,
                                                        const std::string& label) {
    const Json& value = obj.at(field);
    if (!value.is_number()) throw std::runtime_error(label + " must contain numeric field " + field);
    const long long parsed = value.integer(-1);
    if (parsed <= 0) throw std::runtime_error(label + " field " + field + " must be positive");
    return static_cast<std::uint64_t>(parsed);
}

std::uint64_t sync_workflow_optional_u64_field(const Json& obj,
                                               const std::string& field,
                                               std::uint64_t fallback,
                                               const std::string& label) {
    const Json& value = obj.at(field);
    if (value.is_null()) return fallback;
    if (!value.is_number()) throw std::runtime_error(label + " field " + field + " must be numeric when present");
    const long long parsed = value.integer(-1);
    if (parsed < 0) throw std::runtime_error(label + " field " + field + " must be nonnegative");
    return static_cast<std::uint64_t>(parsed);
}

std::string sync_workflow_absolute_lexically_normal_string_or_throw(const std::string& raw_path,
                                                                    const std::string& label) {
    return sync_operator_cli_absolute_lexically_normal_path_or_throw(raw_path, label).string();
}

void enforce_sync_operator_workflow_root_consistency_or_throw(const SyncOperatorRecoveryWorkflowConfig& parsed) {
    if (!parsed.repair_enabled || !parsed.daemon_enabled) return;
    const std::string repair_staging_root = sync_workflow_absolute_lexically_normal_string_or_throw(
        parsed.repair_options.staging_root_path,
        "sync operator recovery workflow repair staging_root_path");
    const std::string daemon_staging_root = sync_workflow_absolute_lexically_normal_string_or_throw(
        parsed.daemon_options.staging_root_path,
        "sync operator recovery workflow daemon staging_root_path");
    if (repair_staging_root != daemon_staging_root) {
        throw std::runtime_error("sync operator recovery workflow repair and daemon staging roots must match when both steps are enabled");
    }
}

SyncOperatorRecoveryWorkflowConfig parse_sync_operator_recovery_workflow_config(const std::string& config_path) {
    if (config_path.empty()) throw std::runtime_error("sync operator recovery workflow config path is required");
    Json config = load_sync_operator_recovery_workflow_config_json_or_throw(config_path);
    if (!config.is_object()) throw std::runtime_error("sync operator recovery workflow config must be a JSON object");
    const std::string format = sync_workflow_string_field_or_throw(config, "format", "sync operator recovery workflow config");
    if (format != "anonsync-sync-operator-recovery-workflow-v1") {
        throw std::runtime_error("sync operator recovery workflow config has unsupported format");
    }

    SyncOperatorRecoveryWorkflowConfig parsed;
    parsed.config_path = sync_operator_cli_absolute_lexically_normal_path_or_throw(config_path,
                                                                 "sync operator recovery workflow config path").string();
    parsed.status_options.sqlite_path = sync_workflow_string_field_or_throw(config, "checkpoint_path", "sync operator recovery workflow config");
    parsed.status_options.session_id = sync_workflow_string_field_or_throw(config, "session_id", "sync operator recovery workflow config");
    parsed.status_options.scheduler_now_epoch = sync_workflow_required_positive_u64_field(config,
                                                                                          "operator_now_epoch",
                                                                                          "sync operator recovery workflow config");
    parsed.status_options.daemon_heartbeat_path = sync_workflow_optional_string_field(config, "daemon_heartbeat_path");

    const Json& repair = config.at("repair");
    if (repair.is_object()) {
        parsed.repair_enabled = sync_workflow_bool_field(repair, "enabled", false);
        if (parsed.repair_enabled) {
            parsed.repair_options.sqlite_path = parsed.status_options.sqlite_path;
            parsed.repair_options.session_id = parsed.status_options.session_id;
            parsed.repair_options.staging_root_path = sync_workflow_string_field_or_throw(repair, "staging_root_path", "sync operator recovery workflow repair");
            NormalizedSyncPath normalized_path;
            SyncValidationResult normalized = normalize_sync_relative_path(sync_workflow_string_field_or_throw(repair, "path", "sync operator recovery workflow repair"),
                                                                          normalized_path);
            if (!normalized.ok) throw std::runtime_error(normalized.reason);
            parsed.repair_options.path = normalized_path;
            parsed.repair_options.review_event_idempotency_key = sync_workflow_string_field_or_throw(repair, "review_event_idempotency_key", "sync operator recovery workflow repair");
            parsed.repair_options.decision_operator_id = sync_workflow_string_field_or_throw(repair, "operator_id", "sync operator recovery workflow repair");
            parsed.repair_options.decision_reason = sync_workflow_optional_string_field(repair,
                                                                                        "decision_reason",
                                                                                        "sidecar-review-repaired-reset-by-operator-workflow");
            parsed.repair_options.repair_at_epoch = sync_workflow_required_positive_u64_field(repair,
                                                                                              "repair_at_epoch",
                                                                                              "sync operator recovery workflow repair");
            parsed.repair_options.repair_worker_id = sync_workflow_string_field_or_throw(repair, "repair_worker_id", "sync operator recovery workflow repair");
            parsed.repair_owner_daemon_id = sync_workflow_optional_string_field(
                repair, "owner_daemon_id", "sync-operator-repair");
            if (!sync_internal_valid_sync_id(parsed.repair_owner_daemon_id)) {
                throw std::runtime_error(
                    "sync operator recovery workflow repair owner_daemon_id must be a lowercase portable sync id");
            }
            parsed.repair_owner_lock_seconds = sync_workflow_optional_u64_field(
                repair,
                "owner_lock_seconds",
                60,
                "sync operator recovery workflow repair");
            if (parsed.repair_owner_lock_seconds == 0) {
                throw std::runtime_error(
                    "sync operator recovery workflow repair owner_lock_seconds must be positive");
            }
            parsed.repair_options.repair_worker_lease_epoch = sync_workflow_optional_u64_field(repair,
                                                                                               "repair_worker_lease_epoch",
                                                                                               1,
                                                                                               "sync operator recovery workflow repair");
            if (parsed.repair_options.repair_worker_lease_epoch == 0) throw std::runtime_error("sync operator recovery workflow repair_worker_lease_epoch must be positive");
            parsed.repair_options.repair_worker_lease_seconds = sync_workflow_optional_u64_field(repair,
                                                                                                 "repair_worker_lease_seconds",
                                                                                                 1,
                                                                                                 "sync operator recovery workflow repair");
            if (parsed.repair_options.repair_worker_lease_seconds == 0) throw std::runtime_error("sync operator recovery workflow repair_worker_lease_seconds must be positive");
            parsed.repair_options.workorder_retry_backoff_seconds = sync_workflow_optional_u64_field(repair,
                                                                                                     "workorder_retry_backoff_seconds",
                                                                                                     0,
                                                                                                     "sync operator recovery workflow repair");
        }
    } else if (!repair.is_null()) {
        throw std::runtime_error("sync operator recovery workflow repair must be an object when present");
    }

    const Json& daemon = config.at("daemon");
    if (daemon.is_object()) {
        parsed.daemon_enabled = sync_workflow_bool_field(daemon, "enabled", false);
        if (parsed.daemon_enabled) {
            parsed.daemon_options.sqlite_path = parsed.status_options.sqlite_path;
            parsed.daemon_options.session_id = parsed.status_options.session_id;
            parsed.daemon_options.source_root_path = sync_workflow_string_field_or_throw(daemon, "source_root_path", "sync operator recovery workflow daemon");
            parsed.daemon_options.destination_root_path = sync_workflow_string_field_or_throw(daemon, "destination_root_path", "sync operator recovery workflow daemon");
            parsed.daemon_options.staging_root_path = sync_workflow_string_field_or_throw(daemon, "staging_root_path", "sync operator recovery workflow daemon");
            parsed.daemon_options.expected_folder_id = sync_workflow_string_field_or_throw(daemon, "expected_folder_id", "sync operator recovery workflow daemon");
            parsed.daemon_options.expected_source_device_id = sync_workflow_string_field_or_throw(daemon, "expected_source_device_id", "sync operator recovery workflow daemon");
            parsed.daemon_options.expected_destination_device_id = sync_workflow_string_field_or_throw(daemon, "expected_destination_device_id", "sync operator recovery workflow daemon");
            parsed.daemon_options.expected_peer_id = sync_workflow_string_field_or_throw(daemon, "expected_peer_id", "sync operator recovery workflow daemon");
            parsed.daemon_options.peer_id = sync_workflow_optional_string_field(daemon, "peer_id");
            parsed.daemon_options.peer_session_id = sync_workflow_optional_string_field(daemon, "peer_session_id");
            parsed.daemon_options.worker_id = sync_workflow_string_field_or_throw(daemon, "worker_id", "sync operator recovery workflow daemon");
            parsed.daemon_options.daemon_id = sync_workflow_optional_string_field(daemon, "daemon_id");
            parsed.daemon_options.initial_worker_lease_epoch = sync_workflow_optional_u64_field(daemon,
                                                                                                "initial_worker_lease_epoch",
                                                                                                1,
                                                                                                "sync operator recovery workflow daemon");
            if (parsed.daemon_options.initial_worker_lease_epoch == 0) throw std::runtime_error("sync operator recovery workflow daemon initial_worker_lease_epoch must be positive");
            parsed.daemon_options.initial_scheduler_now_epoch = sync_workflow_optional_u64_field(daemon,
                                                                                                 "daemon_now_epoch",
                                                                                                 parsed.status_options.scheduler_now_epoch,
                                                                                                 "sync operator recovery workflow daemon");
            if (parsed.daemon_options.initial_scheduler_now_epoch == 0) throw std::runtime_error("sync operator recovery workflow daemon daemon_now_epoch must be positive");
            parsed.daemon_options.worker_lease_seconds = sync_workflow_optional_u64_field(daemon,
                                                                                         "worker_lease_seconds",
                                                                                         60,
                                                                                         "sync operator recovery workflow daemon");
            if (parsed.daemon_options.worker_lease_seconds == 0) throw std::runtime_error("sync operator recovery workflow daemon worker_lease_seconds must be positive");
            parsed.daemon_options.loop_tick_seconds = sync_workflow_optional_u64_field(daemon,
                                                                                       "loop_tick_seconds",
                                                                                       1,
                                                                                       "sync operator recovery workflow daemon");
            if (parsed.daemon_options.loop_tick_seconds == 0) throw std::runtime_error("sync operator recovery workflow daemon loop_tick_seconds must be positive");
            parsed.daemon_options.max_loop_passes = sync_workflow_optional_u64_field(daemon,
                                                                                    "max_loop_passes",
                                                                                    1,
                                                                                    "sync operator recovery workflow daemon");
            if (parsed.daemon_options.max_loop_passes == 0) throw std::runtime_error("sync operator recovery workflow daemon max_loop_passes must be positive");
            parsed.daemon_options.max_scheduler_actions_per_pass = sync_workflow_optional_u64_field(daemon,
                                                                                                    "max_scheduler_actions_per_pass",
                                                                                                    0,
                                                                                                    "sync operator recovery workflow daemon");
            parsed.daemon_options.workorder_retry_backoff_seconds = sync_workflow_optional_u64_field(daemon,
                                                                                                     "workorder_retry_backoff_seconds",
                                                                                                     0,
                                                                                                     "sync operator recovery workflow daemon");
            parsed.daemon_options.recover_bound_peer_sidecars_before_scheduling = sync_workflow_bool_field(daemon,
                                                                                                           "recover_bound_peer_sidecars_before_scheduling",
                                                                                                           false);
            parsed.daemon_options.require_daemon_owner_lock = sync_workflow_bool_field(daemon,
                                                                                       "require_daemon_owner_lock",
                                                                                       true);
            parsed.daemon_options.daemon_heartbeat_path = sync_workflow_optional_string_field(daemon,
                                                                                              "heartbeat_path",
                                                                                              parsed.status_options.daemon_heartbeat_path);
            parsed.daemon_options.daemon_heartbeat_stale_after_seconds = sync_workflow_optional_u64_field(daemon,
                                                                                                          "heartbeat_stale_after_seconds",
                                                                                                          0,
                                                                                                          "sync operator recovery workflow daemon");
        }
    } else if (!daemon.is_null()) {
        throw std::runtime_error("sync operator recovery workflow daemon must be an object when present");
    }
    enforce_sync_operator_workflow_root_consistency_or_throw(parsed);
    return parsed;
}

bool sync_operator_recovery_workflow_status_allows_daemon_run(const SyncSessionCheckpointOperatorStatusResult& status) {
    if (!status.status_loaded) return false;
    if (status.operator_attention_required || status.daemon_heartbeat_attention_required || status.daemon_owner_lock_live) return false;
    return status.safe_to_schedule ||
           status.suggested_next_action == "run-daemon-reclaim-retry" ||
           status.suggested_next_action == "wait-live-lease-or-run-owner";
}

SyncSessionCheckpointOperatorStatusOptions sync_operator_recovery_workflow_status_options_at_epoch(
    const SyncOperatorRecoveryWorkflowConfig& config,
    std::uint64_t scheduler_now_epoch) {
    SyncSessionCheckpointOperatorStatusOptions options = config.status_options;
    options.scheduler_now_epoch = scheduler_now_epoch;
    return options;
}

std::string sync_operator_recovery_workflow_report_json(const SyncOperatorRecoveryWorkflowConfig& config,
                                                        const SyncValidationResult& initial_status_run,
                                                        const SyncSessionCheckpointOperatorStatusResult& initial_status,
                                                        const std::string& initial_status_report,
                                                        bool repair_requested,
                                                        bool repair_attempted,
                                                        const std::string& repair_skip_reason,
                                                        const SyncValidationResult& repair_run,
                                                        const SyncSessionCheckpointBoundPeerSidecarReviewEventRepairResetOptions& repair_options,
                                                        const SyncSessionCheckpointBoundPeerSidecarReviewEventRepairResetResult& repair_result,
                                                        const std::string& repair_report,
                                                        bool repair_owner_acquire_attempted,
                                                        const SyncValidationResult& repair_owner_acquire_run,
                                                        const SyncInternalCheckpointMutationOwnerLease& repair_owner_lease,
                                                        bool repair_owner_release_attempted,
                                                        const SyncValidationResult& repair_owner_release_run,
                                                        const SyncValidationResult& after_repair_status_run,
                                                        const SyncSessionCheckpointOperatorStatusResult& after_repair_status,
                                                        const std::string& after_repair_status_report,
                                                        const SyncValidationResult& pre_daemon_status_run,
                                                        const SyncSessionCheckpointOperatorStatusResult& pre_daemon_status,
                                                        const std::string& pre_daemon_status_report,
                                                        bool daemon_requested,
                                                        bool daemon_attempted,
                                                        const std::string& daemon_skip_reason,
                                                        const SyncValidationResult& daemon_run,
                                                        const SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions& daemon_options,
                                                        const SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult& daemon_result,
                                                        const std::string& daemon_report,
                                                        const SyncValidationResult& final_status_run,
                                                        const SyncSessionCheckpointOperatorStatusResult& final_status,
                                                        const std::string& final_status_report) {
    const bool pre_daemon_status_required = daemon_requested && initial_status_run.ok && (!repair_attempted || repair_run.ok);
    const bool ok = initial_status_run.ok &&
                    (!repair_attempted || repair_run.ok) &&
                    after_repair_status_run.ok &&
                    (!pre_daemon_status_required || pre_daemon_status_run.ok) &&
                    (!daemon_attempted || daemon_run.ok) &&
                    final_status_run.ok;
    std::string reason;
    if (!initial_status_run.ok) reason = initial_status_run.reason;
    else if (repair_attempted && !repair_run.ok) reason = repair_run.reason;
    else if (!after_repair_status_run.ok) reason = after_repair_status_run.reason;
    else if (pre_daemon_status_required && !pre_daemon_status_run.ok) reason = pre_daemon_status_run.reason;
    else if (daemon_attempted && !daemon_run.ok) reason = daemon_run.reason;
    else if (!final_status_run.ok) reason = final_status_run.reason;

    auto report_or_null = [](const std::string& report) -> std::string {
        return report.empty() ? "null" : report;
    };

    std::ostringstream out;
    out << "{\n"
        << "  \"format\": \"anonsync-sync-operator-recovery-workflow-report-v1\",\n"
        << "  \"revision_id\": \"rev0741\",\n"
        << "  \"operation\": \"sync-operator-recovery-workflow\",\n"
        << "  \"ok\": " << sync_cli_json_bool(ok) << ",\n"
        << "  \"reason\": \"" << json_escape(reason) << "\",\n"
        << "  \"input\": {\n"
        << "    \"config_path\": \"" << json_escape(config.config_path) << "\",\n"
        << "    \"checkpoint_path\": \"" << json_escape(config.status_options.sqlite_path) << "\",\n"
        << "    \"session_id\": \"" << json_escape(config.status_options.session_id) << "\",\n"
        << "    \"operator_now_epoch\": " << config.status_options.scheduler_now_epoch << ",\n"
        << "    \"daemon_heartbeat_path\": \"" << json_escape(config.status_options.daemon_heartbeat_path) << "\"\n"
        << "  },\n"
        << "  \"workflow\": {\n"
        << "    \"initial_status_loaded\": " << sync_cli_json_bool(initial_status.status_loaded) << ",\n"
        << "    \"initial_suggested_next_action\": \"" << json_escape(initial_status.suggested_next_action) << "\",\n"
        << "    \"repair_requested\": " << sync_cli_json_bool(repair_requested) << ",\n"
        << "    \"repair_attempted\": " << sync_cli_json_bool(repair_attempted) << ",\n"
        << "    \"repair_skip_reason\": \"" << json_escape(repair_skip_reason) << "\",\n"
        << "    \"pre_daemon_status_loaded\": " << sync_cli_json_bool(pre_daemon_status.status_loaded) << ",\n"
        << "    \"pre_daemon_suggested_next_action\": \"" << json_escape(pre_daemon_status.suggested_next_action) << "\",\n"
        << "    \"daemon_requested\": " << sync_cli_json_bool(daemon_requested) << ",\n"
        << "    \"daemon_attempted\": " << sync_cli_json_bool(daemon_attempted) << ",\n"
        << "    \"daemon_skip_reason\": \"" << json_escape(daemon_skip_reason) << "\",\n"
        << "    \"final_status_loaded\": " << sync_cli_json_bool(final_status.status_loaded) << ",\n"
        << "    \"final_suggested_next_action\": \"" << json_escape(final_status.suggested_next_action) << "\"\n"
        << "  },\n"
        << "  \"repair_owner_lock\": {\n"
        << "    \"acquire_attempted\": " << sync_cli_json_bool(repair_owner_acquire_attempted) << ",\n"
        << "    \"acquired\": " << sync_cli_json_bool(repair_owner_lease.acquired) << ",\n"
        << "    \"reclaimed_expired\": " << sync_cli_json_bool(repair_owner_lease.reclaimed_expired) << ",\n"
        << "    \"release_attempted\": " << sync_cli_json_bool(repair_owner_release_attempted) << ",\n"
        << "    \"released\": " << sync_cli_json_bool(repair_owner_release_attempted && repair_owner_release_run.ok) << ",\n"
        << "    \"daemon_id\": \"" << json_escape(repair_owner_lease.capability.daemon_id) << "\",\n"
        << "    \"worker_id\": \"" << json_escape(repair_owner_lease.capability.worker_id) << "\",\n"
        << "    \"owner_lock_id\": \"" << json_escape(repair_owner_lease.capability.owner_lock_id) << "\",\n"
        << "    \"owner_lock_epoch\": " << repair_owner_lease.capability.owner_lock_epoch << ",\n"
        << "    \"acquired_at_epoch\": " << repair_owner_lease.acquired_at_epoch << ",\n"
        << "    \"expires_at_epoch\": " << repair_owner_lease.expires_at_epoch << ",\n"
        << "    \"acquire_reason\": \"" << json_escape(repair_owner_acquire_run.reason) << "\",\n"
        << "    \"release_reason\": \"" << json_escape(repair_owner_release_run.reason) << "\"\n"
        << "  },\n"
        << "  \"initial_status_report\": " << report_or_null(initial_status_report) << ",\n"
        << "  \"repair_reset_report\": " << report_or_null(repair_report) << ",\n"
        << "  \"after_repair_status_report\": " << report_or_null(after_repair_status_report) << ",\n"
        << "  \"pre_daemon_status_report\": " << report_or_null(pre_daemon_status_report) << ",\n"
        << "  \"daemon_run_report\": " << report_or_null(daemon_report) << ",\n"
        << "  \"final_status_report\": " << report_or_null(final_status_report) << "\n"
        << "}\n";
    (void)repair_options;
    (void)repair_result;
    (void)after_repair_status;
    (void)daemon_options;
    (void)daemon_result;
    return out.str();
}

int run_sync_checkpoint_operator_recovery_workflow_command(const std::string& workflow_config_path,
                                                           const std::string& workflow_report_path) {
    try {
        if (workflow_config_path.empty() || workflow_report_path.empty()) {
            std::cerr << "sync operator recovery workflow requires --sync-operator-recovery-workflow-config and --sync-operator-recovery-workflow-report\n";
            return 64;
        }
        SyncOperatorRecoveryWorkflowConfig config = parse_sync_operator_recovery_workflow_config(workflow_config_path);

        SyncSessionCheckpointOperatorStatusResult initial_status;
        SyncValidationResult initial_status_run = load_sync_session_checkpoint_operator_status(config.status_options,
                                                                                               initial_status);
        const std::string initial_status_report = sync_checkpoint_operator_status_report_json(initial_status_run,
                                                                                              config.status_options,
                                                                                              initial_status);

        bool repair_attempted = false;
        std::string repair_skip_reason;
        SyncValidationResult repair_run = sync_operator_cli_ok_result();
        SyncSessionCheckpointBoundPeerSidecarReviewEventRepairResetResult repair_result;
        std::string repair_report;
        bool repair_owner_acquire_attempted = false;
        SyncValidationResult repair_owner_acquire_run =
            sync_operator_cli_ok_result();
        SyncInternalCheckpointMutationOwnerLease repair_owner_lease;
        bool repair_owner_release_attempted = false;
        SyncValidationResult repair_owner_release_run =
            sync_operator_cli_ok_result();
        SyncOperatorRepairOwnerLeaseGuard repair_owner_guard;
        if (config.repair_enabled) {
            if (initial_status_run.ok && initial_status.pending_sidecar_review_events != 0 && initial_status.suggested_next_action == "review-sidecar-events") {
                repair_attempted = true;
                repair_owner_acquire_attempted = true;
                repair_owner_acquire_run =
                    sync_internal_acquire_checkpoint_mutation_owner_lease(
                        config.repair_options.sqlite_path,
                        config.repair_options.session_id,
                        config.repair_owner_daemon_id,
                        config.repair_options.repair_worker_id,
                        config.repair_options.repair_at_epoch,
                        config.repair_owner_lock_seconds,
                        repair_owner_lease);
                if (!repair_owner_acquire_run.ok) {
                    repair_run = repair_owner_acquire_run;
                } else {
                    config.repair_options.daemon_owner_capability =
                        repair_owner_lease.capability;
                    repair_owner_guard.arm(
                        config.repair_options.sqlite_path,
                        config.repair_options.session_id,
                        repair_owner_lease.capability,
                        config.repair_options.repair_at_epoch);
                    try {
                        repair_run =
                            repair_reset_sync_session_checkpoint_bound_peer_sidecar_review_event(
                                config.repair_options, repair_result);
                    } catch (const std::exception& e) {
                        repair_run = {
                            false,
                            std::string(
                                "sync operator recovery workflow repair threw after owner acquisition: ") +
                                e.what()};
                    }
                    repair_owner_release_attempted = true;
                    repair_owner_release_run = repair_owner_guard.release_now();
                    if (!repair_owner_release_run.ok) {
                        if (repair_run.ok) {
                            repair_run = repair_owner_release_run;
                        } else {
                            repair_run.reason += "; " +
                                                 repair_owner_release_run.reason;
                        }
                    }
                }
                repair_report = sync_checkpoint_sidecar_repair_reset_report_json(repair_run,
                                                                                 config.repair_options,
                                                                                 repair_result);
            } else {
                repair_skip_reason = "initial status did not require sidecar review repair";
            }
        } else {
            repair_skip_reason = "repair disabled by workflow config";
        }

        SyncSessionCheckpointOperatorStatusResult after_repair_status;
        SyncValidationResult after_repair_status_run = initial_status_run;
        std::string after_repair_status_report;
        if (initial_status_run.ok) {
            after_repair_status_run = load_sync_session_checkpoint_operator_status(config.status_options,
                                                                                   after_repair_status);
            after_repair_status_report = sync_checkpoint_operator_status_report_json(after_repair_status_run,
                                                                                     config.status_options,
                                                                                     after_repair_status);
        }

        SyncSessionCheckpointOperatorStatusResult pre_daemon_status;
        SyncValidationResult pre_daemon_status_run = sync_operator_cli_ok_result();
        std::string pre_daemon_status_report;
        if (config.daemon_enabled && initial_status_run.ok && (!repair_attempted || repair_run.ok)) {
            const SyncSessionCheckpointOperatorStatusOptions pre_daemon_status_options =
                sync_operator_recovery_workflow_status_options_at_epoch(config, config.daemon_options.initial_scheduler_now_epoch);
            pre_daemon_status_run = load_sync_session_checkpoint_operator_status(pre_daemon_status_options,
                                                                                 pre_daemon_status);
            pre_daemon_status_report = sync_checkpoint_operator_status_report_json(pre_daemon_status_run,
                                                                                   pre_daemon_status_options,
                                                                                   pre_daemon_status);
        }

        bool daemon_attempted = false;
        std::string daemon_skip_reason;
        SyncValidationResult daemon_run = sync_operator_cli_ok_result();
        SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult daemon_result;
        std::string daemon_report;
        if (config.daemon_enabled) {
            if (repair_attempted && !repair_run.ok) {
                daemon_skip_reason = "repair failed before daemon run";
            } else if (!pre_daemon_status_run.ok) {
                daemon_skip_reason = "daemon-time status preflight failed";
            } else if (sync_operator_recovery_workflow_status_allows_daemon_run(pre_daemon_status)) {
                daemon_attempted = true;
                daemon_run = run_sync_session_checkpoint_resume_transfer_workorder_daemon_loop(config.daemon_options,
                                                                                              daemon_result);
                daemon_report = sync_checkpoint_daemon_run_report_json(daemon_run,
                                                                       config.daemon_options,
                                                                       daemon_result);
            } else {
                daemon_skip_reason = "daemon-time status did not permit owner-fenced daemon run";
            }
        } else {
            daemon_skip_reason = "daemon disabled by workflow config";
        }

        SyncSessionCheckpointOperatorStatusOptions final_status_options = config.status_options;
        if (daemon_attempted && daemon_run.ok && daemon_result.next_scheduler_now_epoch != 0) {
            final_status_options = sync_operator_recovery_workflow_status_options_at_epoch(config, daemon_result.next_scheduler_now_epoch);
        }
        SyncSessionCheckpointOperatorStatusResult final_status;
        SyncValidationResult final_status_run = initial_status_run;
        std::string final_status_report;
        if (initial_status_run.ok) {
            final_status_run = load_sync_session_checkpoint_operator_status(final_status_options,
                                                                            final_status);
            final_status_report = sync_checkpoint_operator_status_report_json(final_status_run,
                                                                              final_status_options,
                                                                              final_status);
        }

        const std::string report = sync_operator_recovery_workflow_report_json(config,
                                                                               initial_status_run,
                                                                               initial_status,
                                                                               initial_status_report,
                                                                               config.repair_enabled,
                                                                               repair_attempted,
                                                                               repair_skip_reason,
                                                                               repair_run,
                                                                               config.repair_options,
                                                                               repair_result,
                                                                               repair_report,
                                                                               repair_owner_acquire_attempted,
                                                                               repair_owner_acquire_run,
                                                                               repair_owner_lease,
                                                                               repair_owner_release_attempted,
                                                                               repair_owner_release_run,
                                                                               after_repair_status_run,
                                                                               after_repair_status,
                                                                               after_repair_status_report,
                                                                               pre_daemon_status_run,
                                                                               pre_daemon_status,
                                                                               pre_daemon_status_report,
                                                                               config.daemon_enabled,
                                                                               daemon_attempted,
                                                                               daemon_skip_reason,
                                                                               daemon_run,
                                                                               config.daemon_options,
                                                                               daemon_result,
                                                                               daemon_report,
                                                                               final_status_run,
                                                                               final_status,
                                                                               final_status_report);
        write_sync_cli_report_json_or_throw(workflow_report_path, report, "sync operator recovery workflow report");

        const bool pre_daemon_status_required = config.daemon_enabled && initial_status_run.ok && (!repair_attempted || repair_run.ok);
        const bool ok = initial_status_run.ok &&
                        (!repair_attempted || repair_run.ok) &&
                        after_repair_status_run.ok &&
                        (!pre_daemon_status_required || pre_daemon_status_run.ok) &&
                        (!daemon_attempted || daemon_run.ok) &&
                        final_status_run.ok;
        if (!ok) {
            std::cerr << "sync operator recovery workflow failed\n";
            return 1;
        }
        std::cout << "sync operator recovery workflow wrote " << workflow_report_path
                  << " repair_attempted=" << sync_cli_json_bool(repair_attempted)
                  << " daemon_attempted=" << sync_cli_json_bool(daemon_attempted)
                  << " final_next_action=" << final_status.suggested_next_action << "\n";
        return 0;
    } catch (const std::exception& e) {
        std::cerr << e.what() << "\n";
        return 1;
    }
}


}  // namespace anonsync
