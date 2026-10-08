#include "sync_replica_peer_service_status.hpp"
#include "sync_replica_historical_version_inventory_json.hpp"

#if !defined(_WIN32)

#include <iomanip>
#include <sstream>
#include <stdexcept>

#include <unistd.h>

namespace anonsync {
namespace {

[[nodiscard]] std::string json_quote(std::string_view value) {
    std::ostringstream output;
    output << '"';
    for (const unsigned char byte : value) {
        switch (byte) {
            case '"': output << "\\\""; break;
            case '\\': output << "\\\\"; break;
            case '\b': output << "\\b"; break;
            case '\f': output << "\\f"; break;
            case '\n': output << "\\n"; break;
            case '\r': output << "\\r"; break;
            case '\t': output << "\\t"; break;
            default:
                if (byte < 0x20U) {
                    output << "\\u00" << std::hex << std::setw(2)
                           << std::setfill('0')
                           << static_cast<unsigned int>(byte)
                           << std::dec << std::setfill(' ');
                } else {
                    output << static_cast<char>(byte);
                }
        }
    }
    output << '"';
    return output.str();
}

[[nodiscard]] const char* json_bool(bool value) noexcept {
    return value ? "true" : "false";
}

void append_optional_path(
    std::ostream& output,
    const std::optional<std::filesystem::path>& value) {
    if (!value.has_value()) {
        output << "null";
        return;
    }
    output << json_quote(value->generic_string());
}

void append_optional_int(
    std::ostream& output,
    const std::optional<int>& value) {
    if (value.has_value()) {
        output << *value;
    } else {
        output << "null";
    }
}

void append_optional_uint64(
    std::ostream& output,
    const std::optional<std::uint64_t>& value) {
    if (value.has_value()) {
        output << *value;
    } else {
        output << "null";
    }
}

void append_ingress_report(
    std::ostream& output,
    const std::optional<SyncReplicaStreamConnectReport>& report) {
    if (!report.has_value()) {
        output << "null";
        return;
    }
    output
        << "{\"route_kind\":"
        << json_quote(sync_replica_stream_route_kind_name(report->route_kind))
        << ",\"disposition\":"
        << json_quote(sync_replica_stream_connect_disposition_name(
               report->disposition))
        << ",\"terminal_stage\":"
        << json_quote(sync_replica_stream_route_stage_name(
               report->terminal_stage))
        << ",\"route_negotiated\":"
        << json_bool(report->route_negotiated)
        << ",\"control_session_created\":"
        << json_bool(report->control_session_created)
        << ",\"control_session_reused\":"
        << json_bool(report->control_session_reused)
        << ",\"control_session_stale_detected\":"
        << json_bool(report->control_session_stale_detected)
        << ",\"control_session_recovered\":"
        << json_bool(report->control_session_recovered)
        << ",\"numeric_connect_attempts\":"
        << report->numeric_connect_attempts
        << ",\"numeric_connect_error\":";
    append_optional_int(output, report->numeric_connect_error);
    output
        << ",\"route_bytes_written\":" << report->route_bytes_written
        << ",\"route_bytes_received\":" << report->route_bytes_received
        << ",\"sam_result\":";
    if (report->sam_result.has_value()) {
        output << json_quote(sync_replica_i2p_sam_result_name(
            *report->sam_result));
    } else {
        output << "null";
    }
    output << '}';
}

void append_ingress_event(
    std::ostream& output,
    const std::optional<SyncReplicaPeerServiceStepResult>& event) {
    if (!event.has_value()) {
        output << "null";
        return;
    }
    output
        << "{\"disposition\":"
        << json_quote(sync_replica_peer_service_step_disposition_name(
               event->disposition))
        << ",\"ingress_ready\":" << json_bool(event->ingress_ready)
        << ",\"consecutive_failures\":"
        << event->consecutive_ingress_failures
        << ",\"retry_delay_milliseconds\":"
        << event->ingress_retry_delay_milliseconds
        << ",\"diagnostic\":";
    if (event->ingress_error.has_value()) {
        output << json_quote(*event->ingress_error);
    } else {
        output << "null";
    }
    output << ",\"report\":";
    append_ingress_report(output, event->ingress_report);
    output << '}';
}

void append_folder_wake_snapshot(
    std::ostream& output,
    const SyncReplicaFolderWakeSnapshot& snapshot) {
    output
        << "{\"platform_supported\":"
        << json_bool(snapshot.platform_supported)
        << ",\"active\":" << json_bool(snapshot.active)
        << ",\"complete\":" << json_bool(snapshot.complete)
        << ",\"watch_count\":" << snapshot.watch_count
        << ",\"observations\":" << snapshot.observations
        << ",\"wake_observations\":" << snapshot.wake_observations
        << ",\"events_observed\":" << snapshot.events_observed
        << ",\"rebuilds\":" << snapshot.rebuilds
        << ",\"watch_add_failures\":"
        << snapshot.watch_add_failures
        << ",\"watch_limit_hits\":" << snapshot.watch_limit_hits
        << ",\"rebuild_entry_limit_hits\":"
        << snapshot.rebuild_entry_limit_hits
        << ",\"kernel_queue_overflows\":"
        << snapshot.kernel_queue_overflows
        << ",\"observation_budget_exhaustions\":"
        << snapshot.observation_budget_exhaustions
        << ",\"invalidations\":" << snapshot.invalidations
        << ",\"diagnostic\":";
    if (snapshot.diagnostic.has_value()) {
        output << json_quote(*snapshot.diagnostic);
    } else {
        output << "null";
    }
    output << '}';
}

void append_payload_scrub_status(
    std::ostream& output,
    const SyncReplicaFilePayloadStoreScrubStatus& status) {
    output
        << "{\"enabled\":" << json_bool(status.enabled)
        << ",\"max_bytes_per_attempt\":"
        << status.max_bytes_per_attempt
        << ",\"max_entries_per_attempt\":"
        << status.max_entries_per_attempt
        << ",\"last_report\":";
    if (!status.last_report.has_value()) {
        output << "null";
    } else {
        const auto& report = *status.last_report;
        output
            << "{\"disposition\":"
            << json_quote(
                   sync_replica_file_payload_store_scrub_disposition_name(
                       report.disposition))
            << ",\"age_milliseconds\":";
        append_optional_uint64(
            output, status.last_report_age_milliseconds);
        output
            << ",\"hashed_bytes\":" << report.hashed_bytes
            << ",\"touched_entries\":"
            << report.touched_entry_count
            << ",\"completed_entries\":"
            << report.completed_entry_count
            << ",\"completed_cycles\":"
            << report.completed_cycles
            << ",\"state_generation\":"
            << report.state_generation
            << ",\"active_content_sha256\":";
        if (report.active_content_sha256.empty()) {
            output << "null";
        } else {
            output << json_quote(report.active_content_sha256);
        }
        output
            << ",\"active_offset_bytes\":"
            << report.active_offset_bytes
            << ",\"state_rebuilt\":"
            << json_bool(report.state_rebuilt)
            << ",\"reverified_active_completed\":"
            << json_bool(report.reverified_active_completed)
            << ",\"reverified_failure_cleared\":"
            << json_bool(report.reverified_failure_cleared)
            << '}';
    }
    output << ",\"last_completed_cycle_age_milliseconds\":";
    append_optional_uint64(
        output, status.last_completed_cycle_age_milliseconds);
    output << '}';
}

void append_payload_terminal_verification_work(
    std::ostream& output,
    const std::optional<
        SyncReplicaFilePayloadStoreTerminalVerificationWork>& work) {
    if (!work.has_value()) {
        output << "null";
        return;
    }
    if (work->total_size_bytes == 0U ||
        work->verified_offset_bytes >= work->total_size_bytes) {
        throw std::logic_error(
            "payload terminal-verification work is not a pending extent");
    }
    const std::uint64_t remaining =
        work->total_size_bytes - work->verified_offset_bytes;
    output
        << "{\"content_sha256\":"
        << json_quote(work->content_sha256)
        << ",\"total_size_bytes\":" << work->total_size_bytes
        << ",\"verified_offset_bytes\":"
        << work->verified_offset_bytes
        << ",\"remaining_bytes\":" << remaining << '}';
}

void append_payload_terminal_verification_status(
    std::ostream& output,
    const SyncReplicaFilePayloadStoreTerminalVerificationStatus& status) {
    if (status.pending_verified_bytes > status.pending_total_bytes) {
        throw std::logic_error(
            "payload terminal-verification status exceeds its byte frontier");
    }
    if (!status.observation_known &&
        (status.pending_entry_count != 0U ||
         status.pending_total_bytes != 0U ||
         status.pending_verified_bytes != 0U || status.next_work.has_value())) {
        throw std::logic_error(
            "unknown payload terminal-verification status carries work");
    }
    const bool empty = status.pending_entry_count == 0U;
    if (status.observation_known &&
        (empty != !status.next_work.has_value() ||
         (empty && (status.pending_total_bytes != 0U ||
                    status.pending_verified_bytes != 0U)))) {
        throw std::logic_error(
            "payload terminal-verification status is internally inconsistent");
    }
    output
        << "{\"observation_known\":"
        << json_bool(status.observation_known)
        << ",\"pending_entry_count\":" << status.pending_entry_count
        << ",\"pending_total_bytes\":" << status.pending_total_bytes
        << ",\"pending_verified_bytes\":"
        << status.pending_verified_bytes
        << ",\"next_work\":";
    append_payload_terminal_verification_work(output, status.next_work);
    output << '}';
}

void append_payload_terminal_verification_step(
    std::ostream& output,
    const std::optional<
        SyncReplicaFilePayloadStoreTerminalVerificationStepResult>& step) {
    if (!step.has_value()) {
        output << "null";
        return;
    }
    output
        << "{\"disposition\":"
        << json_quote(
               sync_replica_file_payload_store_terminal_verification_step_disposition_name(
                   step->disposition))
        << ",\"work_before\":";
    append_payload_terminal_verification_work(output, step->work_before);
    output
        << ",\"verified_offset_after_bytes\":"
        << step->verified_offset_after_bytes
        << ",\"hashed_bytes\":" << step->hashed_bytes
        << ",\"terminal_verification_steps\":"
        << step->terminal_verification_steps << '}';
}

void append_source_manifest_projection_status(
    std::ostream& output,
    const SyncReplicaReconciliationSourceManifestProjectionStatus& status) {
    if (!status.pending) {
        if (!status.operation_id.empty() || !status.content_sha256.empty() ||
            status.total_size_bytes != 0U || status.next_offset_bytes != 0U ||
            status.completed_chunk_count != 0U) {
            throw std::logic_error(
                "idle source-manifest projection status carries work");
        }
        output << "{\"pending\":false,\"operation_id\":null,"
                  "\"content_sha256\":null,\"total_size_bytes\":0,"
                  "\"next_offset_bytes\":0,\"remaining_bytes\":0,"
                  "\"completed_chunk_count\":0}";
        return;
    }
    if (status.operation_id.empty() || status.content_sha256.empty() ||
        status.total_size_bytes == 0U ||
        status.next_offset_bytes >= status.total_size_bytes) {
        throw std::logic_error(
            "pending source-manifest projection status is invalid");
    }
    output
        << "{\"pending\":true,\"operation_id\":"
        << json_quote(status.operation_id)
        << ",\"content_sha256\":" << json_quote(status.content_sha256)
        << ",\"total_size_bytes\":" << status.total_size_bytes
        << ",\"next_offset_bytes\":" << status.next_offset_bytes
        << ",\"remaining_bytes\":"
        << (status.total_size_bytes - status.next_offset_bytes)
        << ",\"completed_chunk_count\":"
        << status.completed_chunk_count << '}';
}

void append_source_manifest_projection_step(
    std::ostream& output,
    const std::optional<
        SyncReplicaReconciliationSourceManifestProjectionStepResult>& step) {
    if (!step.has_value()) {
        output << "null";
        return;
    }
    output
        << "{\"disposition\":"
        << json_quote(
               sync_replica_reconciliation_source_manifest_projection_step_disposition_name(
                   step->disposition))
        << ",\"before\":";
    append_source_manifest_projection_status(output, step->before);
    output << ",\"after\":";
    append_source_manifest_projection_status(output, step->after);
    output
        << ",\"hashed_bytes\":" << step->hashed_bytes
        << ",\"newly_completed_chunk_count\":"
        << step->newly_completed_chunk_count
        << ",\"projection_restarted\":"
        << json_bool(step->projection_restarted) << '}';
}

void append_payload_integrity_status(
    std::ostream& output,
    const std::optional<SyncReplicaPeerServicePayloadIntegrityFault>& fault,
    const std::optional<SyncReplicaPeerServicePayloadIntegrityRecovery>&
        recovery) {
    output << "{\"state\":"
           << json_quote(fault.has_value() ? "faulted" : "healthy")
           << ",\"active_fault\":";
    if (!fault.has_value()) {
        output << "null";
    } else {
        output
            << "{\"expected_content_sha256\":"
            << json_quote(fault->expected_content_sha256)
            << ",\"observed_content_sha256\":"
            << json_quote(fault->observed_content_sha256)
            << ",\"failure_persisted\":"
            << json_bool(fault->failure_persisted)
            << ",\"detection_count\":"
            << fault->detection_count
            << ",\"observed_content_change_count\":"
            << fault->observed_content_change_count
            << ",\"active_age_milliseconds\":"
            << fault->active_age_milliseconds
            << ",\"last_detection_age_milliseconds\":"
            << fault->last_detection_age_milliseconds
            << ",\"retry_delay_milliseconds\":"
            << fault->retry_delay_milliseconds
            << '}';
    }
    output << ",\"most_recent_recovery\":";
    if (!recovery.has_value()) {
        output << "null}";
        return;
    }
    output
        << "{\"expected_content_sha256\":"
        << json_quote(recovery->expected_content_sha256)
        << ",\"observed_content_sha256\":"
        << json_quote(recovery->observed_content_sha256)
        << ",\"failure_persisted\":"
        << json_bool(recovery->failure_persisted)
        << ",\"detection_count\":"
        << recovery->detection_count
        << ",\"observed_content_change_count\":"
        << recovery->observed_content_change_count
        << ",\"fault_duration_milliseconds\":"
        << recovery->fault_duration_milliseconds
        << ",\"recovery_age_milliseconds\":"
        << recovery->recovery_age_milliseconds
        << "}}";
}

void append_payload_recheck_status(
    std::ostream& output,
    const SyncReplicaPeerServicePayloadRecheckStatus& status) {
    output
        << "{\"requested_generation\":"
        << status.requested_generation
        << ",\"started_generation\":"
        << status.started_generation
        << ",\"completed_generation\":"
        << status.completed_generation
        << ",\"pending\":" << json_bool(status.pending)
        << ",\"retry_delay_milliseconds\":"
        << status.retry_delay_milliseconds
        << ",\"last_hashed_entries\":"
        << status.last_hashed_entry_count
        << ",\"last_hashed_bytes\":"
        << status.last_hashed_bytes
        << ",\"last_snapshot_handoffs\":"
        << status.last_snapshot_handoff_count
        << ",\"last_convergence_snapshot_observations\":"
        << status.last_convergence_snapshot_observation_count
        << ",\"last_convergence_mutation_full_scans\":"
        << status.last_convergence_mutation_full_scan_count
        << ",\"last_completion_recovered_integrity_fault\":"
        << json_bool(
               status.last_completion_recovered_integrity_fault)
        << '}';
}

void append_payload_quarantine_result(
    std::ostream& output,
    const std::optional<SyncReplicaFilePayloadStoreQuarantineResult>& result) {
    if (!result.has_value()) {
        output << "null";
        return;
    }
    output
        << "{\"action\":"
        << json_quote(
               sync_replica_file_payload_store_quarantine_action_name(
                   result->action))
        << ",\"disposition\":"
        << json_quote(
               sync_replica_file_payload_store_quarantine_disposition_name(
                   result->disposition))
        << ",\"expected_content_sha256\":"
        << json_quote(result->expected_content_sha256)
        << ",\"requested_observed_content_sha256\":"
        << json_quote(result->requested_observed_content_sha256)
        << ",\"current_observed_content_sha256\":";
    if (result->current_observed_content_sha256.empty()) {
        output << "null";
    } else {
        output << json_quote(result->current_observed_content_sha256);
    }
    output << ",\"quarantine_basename\":";
    if (result->quarantine_basename.empty()) {
        output << "null";
    } else {
        output << json_quote(result->quarantine_basename);
    }
    output << ",\"size_bytes\":" << result->size_bytes << '}';
}

void append_payload_quarantine_inventory_status(
    std::ostream& output,
    const SyncReplicaFilePayloadStoreQuarantineInventoryStatus& inventory) {
    output
        << "{\"observation_known\":"
        << json_bool(inventory.observation_known)
        << ",\"last_observation_age_milliseconds\":";
    if (!inventory.last_observation_age_milliseconds.has_value()) {
        output << "null";
    } else {
        output << *inventory.last_observation_age_milliseconds;
    }
    output
        << ",\"entry_limit\":" << inventory.entry_limit
        << ",\"byte_limit\":" << inventory.byte_limit
        << ",\"entry_count\":" << inventory.entries.size()
        << ",\"total_bytes\":" << inventory.total_bytes
        << ",\"entries\":[";
    for (std::size_t index = 0U; index < inventory.entries.size(); ++index) {
        if (index != 0U) output << ',';
        const auto& entry = inventory.entries[index];
        output
            << "{\"expected_content_sha256\":"
            << json_quote(entry.expected_content_sha256)
            << ",\"observed_content_sha256\":"
            << json_quote(entry.observed_content_sha256)
            << ",\"size_bytes\":" << entry.size_bytes << '}';
    }
    output << "]}";
}

void append_payload_quarantine_status(
    std::ostream& output,
    const SyncReplicaPeerServicePayloadQuarantineStatus& status) {
    output
        << "{\"requested_generation\":"
        << status.requested_generation
        << ",\"started_generation\":"
        << status.started_generation
        << ",\"completed_generation\":"
        << status.completed_generation
        << ",\"pending\":" << json_bool(status.pending)
        << ",\"action\":";
    if (!status.action.has_value()) {
        output << "null";
    } else {
        output << json_quote(
            sync_replica_file_payload_store_quarantine_action_name(
                *status.action));
    }
    output << ",\"expected_content_sha256\":";
    if (status.expected_content_sha256.empty()) {
        output << "null";
    } else {
        output << json_quote(status.expected_content_sha256);
    }
    output << ",\"observed_content_sha256\":";
    if (status.observed_content_sha256.empty()) {
        output << "null";
    } else {
        output << json_quote(status.observed_content_sha256);
    }
    output
        << ",\"retry_delay_milliseconds\":"
        << status.retry_delay_milliseconds
        << ",\"last_result\":";
    append_payload_quarantine_result(output, status.last_result);
    output << ",\"inventory\":";
    append_payload_quarantine_inventory_status(output, status.inventory);
    output << '}';
}

void append_historical_version_query(
    std::ostream& output,
    const SyncReplicaHistoricalVersionQuery& query) {
    append_sync_replica_historical_version_query_json(output, query);
}

void append_retention_plan_query(
    std::ostream& output,
    const SyncReplicaRetentionPlanQuery& query) {
    append_sync_replica_retention_plan_query_json(output, query);
}

void append_historical_version_restore_request(
    std::ostream& output,
    const std::optional<SyncReplicaHistoricalVersionRestoreRequest>& request) {
    if (!request.has_value()) {
        output << "null";
        return;
    }
    output << "{\"operation_id\":" << json_quote(request->operation_id)
           << ",\"expected_current_operation_id\":";
    if (request->expected_current_operation_id.has_value()) {
        output << json_quote(*request->expected_current_operation_id);
    } else {
        output << "null";
    }
    output << '}';
}

void append_historical_version_inventory(
    std::ostream& output,
    const std::optional<SyncReplicaHistoricalVersionInventory>& inventory) {
    append_sync_replica_historical_version_inventory_json(output, inventory);
}

void append_retention_plan(
    std::ostream& output,
    const std::optional<SyncReplicaRetentionPlan>& plan) {
    append_sync_replica_retention_plan_json(output, plan);
}

void append_historical_version_restore(
    std::ostream& output,
    const std::optional<SyncReplicaHistoricalVersionRestoreResult>& restored) {
    if (!restored.has_value()) {
        output << "null";
        return;
    }
    output
        << "{\"disposition\":"
        << json_quote(
               sync_replica_historical_version_restore_disposition_name(
                   restored->disposition))
        << ",\"historical_operation_id\":"
        << json_quote(restored->historical_operation.operation_id)
        << ",\"replaced_visible_operation_id\":"
        << json_quote(restored->replaced_visible_operation.operation_id)
        << ",\"restored_operation_id\":"
        << json_quote(restored->restored_operation.operation_id)
        << ",\"canonical_path\":"
        << json_quote(restored->restored_operation.canonical_path)
        << ",\"size_bytes\":"
        << restored->restored_operation.size_bytes
        << ",\"content_sha256\":"
        << json_quote(restored->restored_operation.content_sha256)
        << ",\"catalog_operation_id\":"
        << json_quote(restored->restored_entry.operation_id) << '}';
}

void append_historical_version_pin_update(
    std::ostream& output,
    const std::optional<SyncReplicaSqliteHistoricalVersionPinResult>&
        update) {
    if (!update.has_value()) {
        output << "null";
        return;
    }
    output
        << "{\"disposition\":"
        << json_quote(
               sync_replica_sqlite_historical_version_pin_disposition_name(
                   update->disposition))
        << ",\"operation_id\":" << json_quote(update->operation_id)
        << ",\"state_generation\":" << update->state_generation
        << ",\"pin_count\":" << update->pin_count
        << ",\"pin_set_digest\":"
        << json_quote(update->pin_set_digest) << '}';
}

void append_historical_version_status(
    std::ostream& output,
    const SyncReplicaPeerServiceHistoricalVersionStatus& status) {
    output
        << "{\"requested_generation\":" << status.requested_generation
        << ",\"started_generation\":" << status.started_generation
        << ",\"completed_generation\":" << status.completed_generation
        << ",\"pending\":" << json_bool(status.pending)
        << ",\"action\":";
    if (status.action.has_value()) {
        output << json_quote(
            sync_replica_peer_service_historical_version_action_name(
                *status.action));
    } else {
        output << "null";
    }
    output << ",\"query\":";
    if (status.action.has_value() &&
        *status.action ==
            SyncReplicaPeerServiceHistoricalVersionAction::Inspect) {
        append_historical_version_query(output, status.query);
    } else {
        output << "null";
    }
    output << ",\"retention_plan_query\":";
    if (status.action.has_value() &&
        *status.action ==
            SyncReplicaPeerServiceHistoricalVersionAction::RetentionPlan) {
        append_retention_plan_query(output, status.retention_plan_query);
    } else {
        output << "null";
    }
    output << ",\"operation_id\":";
    const std::string_view operation_id =
        status.action.has_value() &&
                (*status.action ==
                     SyncReplicaPeerServiceHistoricalVersionAction::Pin ||
                 *status.action ==
                     SyncReplicaPeerServiceHistoricalVersionAction::Unpin)
            ? std::string_view(status.retention_operation_id)
            : std::string_view(status.restore_request.operation_id);
    if (operation_id.empty()) {
        output << "null";
    } else {
        output << json_quote(operation_id);
    }
    output << ",\"expected_current_operation_id\":";
    if (status.restore_request.expected_current_operation_id.has_value()) {
        output << json_quote(
            *status.restore_request.expected_current_operation_id);
    } else {
        output << "null";
    }
    output
        << ",\"retry_delay_milliseconds\":"
        << status.retry_delay_milliseconds
        << ",\"last_inventory\":";
    append_historical_version_inventory(output, status.last_inventory);
    output << ",\"last_retention_plan\":";
    append_retention_plan(output, status.last_retention_plan);
    output << ",\"last_restore\":";
    append_historical_version_restore(output, status.last_restore);
    output << ",\"last_pin_update\":";
    append_historical_version_pin_update(output, status.last_pin_update);
    output << ",\"last_failure_class\":";
    if (status.last_failure_class.has_value()) {
        output << json_quote(
            sync_replica_peer_service_historical_version_failure_class_name(
                *status.last_failure_class));
    } else {
        output << "null";
    }
    output << ",\"last_source_change_stage\":";
    if (status.last_source_change_stage.has_value()) {
        output << json_quote(
            sync_replica_historical_version_source_change_stage_name(
                *status.last_source_change_stage));
    } else {
        output << "null";
    }
    output << ",\"last_failure\":";
    if (status.last_failure.has_value()) {
        output << json_quote(*status.last_failure);
    } else {
        output << "null";
    }
    output << '}';
}

void validate_status_word_or_throw(
    std::string_view value,
    std::string_view label) {
    if (value.empty() || value.size() > 64U) {
        throw std::invalid_argument(
            std::string(label) + " must contain 1 to 64 bytes");
    }
    for (const unsigned char byte : value) {
        const bool accepted =
            (byte >= 'a' && byte <= 'z') ||
            (byte >= '0' && byte <= '9') || byte == '_';
        if (!accepted) {
            throw std::invalid_argument(
                std::string(label) +
                " must contain only lowercase ASCII, digits, or underscore");
        }
    }
}

}  // namespace

std::string render_sync_replica_folder_wake_status_json(
    const SyncReplicaFolderWakeSnapshot& snapshot) {
    std::ostringstream output;
    append_folder_wake_snapshot(output, snapshot);
    return output.str();
}

std::string
render_sync_replica_file_payload_store_terminal_verification_status_json(
    const SyncReplicaFilePayloadStoreTerminalVerificationStatus& status) {
    std::ostringstream output;
    append_payload_terminal_verification_status(output, status);
    return output.str();
}

std::string render_sync_replica_source_manifest_projection_status_json(
    const SyncReplicaReconciliationSourceManifestProjectionStatus& status) {
    std::ostringstream output;
    append_source_manifest_projection_status(output, status);
    return output.str();
}

std::string render_sync_replica_peer_service_payload_recheck_status_json(
    const SyncReplicaPeerServicePayloadRecheckStatus& status) {
    std::ostringstream output;
    append_payload_recheck_status(output, status);
    return output.str();
}

std::string render_sync_replica_peer_service_payload_quarantine_status_json(
    const SyncReplicaPeerServicePayloadQuarantineStatus& status) {
    std::ostringstream output;
    append_payload_quarantine_status(output, status);
    return output.str();
}

std::string
render_sync_replica_peer_service_historical_version_status_json(
    const SyncReplicaPeerServiceHistoricalVersionStatus& status) {
    std::ostringstream output;
    append_historical_version_status(output, status);
    return output.str();
}

std::string render_sync_replica_file_payload_store_quarantine_result_json(
    const SyncReplicaFilePayloadStoreQuarantineResult& result) {
    std::ostringstream output;
    append_payload_quarantine_result(output, result);
    return output.str();
}

void account_sync_replica_peer_service_step(
    SyncReplicaPeerServiceLoopSummary& summary,
    const SyncReplicaPeerServiceStepResult& step) {
    if (step.outbound.has_value()) {
        const auto& cycle = *step.outbound;
        if (sync_replica_sync_once_is_complete(cycle.disposition)) {
            ++summary.cycles_complete;
        } else if (sync_replica_sync_once_is_bounded_progress(
                       cycle.disposition)) {
            ++summary.cycles_partial_progress;
        } else {
            ++summary.cycles_failed;
        }
        if (sync_replica_sync_once_is_settled(cycle.disposition)) {
            ++summary.cycles_settled;
        }
        if (cycle.disposition ==
            SyncReplicaSyncOnceDisposition::CompleteChanged) {
            ++summary.cycles_changed;
        }
        if (cycle.disposition == SyncReplicaSyncOnceDisposition::
                CompleteWithUnresolvedPaths) {
            ++summary.cycles_with_unresolved_paths;
        }
        if (sync_replica_sync_once_made_durable_progress(cycle)) {
            ++summary.cycles_with_durable_progress;
        }
        summary.last_cycle = cycle;
    }
    if (step.disposition ==
        SyncReplicaPeerServiceStepDisposition::OutboundSessionIoFailed) {
        ++summary.cycles_failed;
    }

    if (step.inbound.has_value()) {
        const auto& inbound = *step.inbound;
        if (inbound.accepted) ++summary.accepted_sessions;
        if (inbound.handshake_complete) ++summary.completed_handshakes;
        if (inbound.disposition ==
                SyncReplicaPeerTlsServerDisposition::HandshakeDeadlineExpired ||
            inbound.disposition ==
                SyncReplicaPeerTlsServerDisposition::HandshakeRejected) {
            ++summary.rejected_handshakes;
        }
        if (inbound.disposition ==
            SyncReplicaPeerTlsServerDisposition::PeerUnauthorized) {
            ++summary.unauthorized_peers;
        }
        if (inbound.disposition ==
            SyncReplicaPeerTlsServerDisposition::ApplicationServed) {
            ++summary.applications_served;
        }
        if (inbound.application.has_value()) {
            switch (inbound.application->disposition) {
                case SyncReplicaPeerTlsServeDisposition::FileDelivery:
                    ++summary.file_delivery_sessions;
                    break;
                case SyncReplicaPeerTlsServeDisposition::Reconciliation:
                    ++summary.reconciliation_sessions;
                    break;
                case SyncReplicaPeerTlsServeDisposition::UnsupportedApplication:
                    ++summary.unsupported_application_sessions;
                    break;
                case SyncReplicaPeerTlsServeDisposition::PeerClosed:
                    ++summary.peer_closed_sessions;
                    break;
                case SyncReplicaPeerTlsServeDisposition::
                        FirstRequestDeadlineExpired:
                    ++summary.application_deadline_expirations;
                    break;
            }
        }
        summary.last_inbound = inbound;
    }
    switch (step.disposition) {
        case SyncReplicaPeerServiceStepDisposition::
                IngressPublicationConnected:
        case SyncReplicaPeerServiceStepDisposition::
                IngressPublicationUnavailable:
        case SyncReplicaPeerServiceStepDisposition::IngressPublicationLost:
            summary.last_ingress_event = step;
            break;
        case SyncReplicaPeerServiceStepDisposition::InitialRepairCompleted:
        case SyncReplicaPeerServiceStepDisposition::PeriodicRepairCompleted:
        case SyncReplicaPeerServiceStepDisposition::
                FilesystemWakeRepairCompleted:
        case SyncReplicaPeerServiceStepDisposition::OutboundCycleCompleted:
        case SyncReplicaPeerServiceStepDisposition::
                InboundAcceptWindowExpired:
        case SyncReplicaPeerServiceStepDisposition::InboundSessionObserved:
        case SyncReplicaPeerServiceStepDisposition::
                IngressPublicationBackoffPending:
        case SyncReplicaPeerServiceStepDisposition::
                PayloadIntegrityFaultObserved:
        case SyncReplicaPeerServiceStepDisposition::
                PayloadIntegrityReproofBackoffPending:
        case SyncReplicaPeerServiceStepDisposition::
                PayloadIntegrityReproofCompleted:
        case SyncReplicaPeerServiceStepDisposition::OutboundSessionIoFailed:
        case SyncReplicaPeerServiceStepDisposition::InboundSessionIoFailed:
        case SyncReplicaPeerServiceStepDisposition::
                PayloadStoreLeaseBusyDeferred:
        case SyncReplicaPeerServiceStepDisposition::
                OperatorPayloadRecheckCompleted:
        case SyncReplicaPeerServiceStepDisposition::
                OperatorPayloadQuarantineCompleted:
        case SyncReplicaPeerServiceStepDisposition::
                OperatorHistoricalVersionCompleted:
        case SyncReplicaPeerServiceStepDisposition::
                PayloadTerminalVerificationAdvanced:
        case SyncReplicaPeerServiceStepDisposition::
                SourceManifestProjectionAdvanced:
            break;
    }
    summary.last_step = step;
    // The completed inventory is already retained in the stable
    // historical_versions domain. Do not copy the same potentially large page
    // into generic last_step status as well; generation/action/failure fields
    // remain there as the event correlation surface.
    summary.last_step->historical_version_inventory.reset();
    summary.last_step->historical_version_retention_plan.reset();
}

std::string render_sync_replica_peer_service_status_json(
    const SyncReplicaPeerServiceOwner& owner,
    const SyncReplicaPeerServiceLoopSummary& summary,
    std::uint64_t generation,
    std::chrono::steady_clock::time_point service_started_at,
    std::string_view service_state,
    std::string_view activity,
    const std::optional<std::filesystem::path>& configuration_path,
    const std::optional<std::filesystem::path>& status_socket_path,
    std::optional<std::string_view> stop_reason) {
    validate_status_word_or_throw(service_state, "service state");
    validate_status_word_or_throw(activity, "service activity");
    if (stop_reason.has_value()) {
        validate_status_word_or_throw(*stop_reason, "service stop reason");
    }
    const auto now = std::chrono::steady_clock::now();
    const auto elapsed = now >= service_started_at
        ? std::chrono::duration_cast<std::chrono::milliseconds>(
              now - service_started_at)
        : std::chrono::milliseconds::zero();
    const auto& counters = owner.counters();
    const SyncReplicaFilePayloadStoreScrubStatus payload_scrub =
        owner.payload_scrub_status();
    const SyncReplicaFilePayloadStoreTerminalVerificationStatus
        payload_terminal_verification =
            owner.payload_terminal_verification_status();
    const SyncReplicaReconciliationSourceManifestProjectionStatus
        source_manifest_projection =
            owner.source_manifest_projection_status();
    const auto payload_integrity = owner.payload_integrity_fault();
    const auto payload_integrity_recovery =
        owner.most_recent_payload_integrity_recovery();
    const SyncReplicaPeerServicePayloadRecheckStatus payload_recheck =
        owner.payload_recheck_status();
    const SyncReplicaPeerServicePayloadQuarantineStatus payload_quarantine =
        owner.payload_quarantine_status();
    const SyncReplicaPeerServiceHistoricalVersionStatus historical_versions =
        owner.historical_version_status();

    std::ostringstream output;
    output
        << "{\"schema\":" << json_quote(kSyncReplicaPeerServiceStatusSchema)
        << ",\"service_state\":" << json_quote(service_state)
        << ",\"ready\":"
        << json_bool(service_state == "running" && owner.ready())
        << ",\"activity\":" << json_quote(activity)
        << ",\"generation\":" << generation
        << ",\"pid\":" << static_cast<unsigned long long>(::getpid())
        << ",\"uptime_milliseconds\":" << elapsed.count()
        << ",\"configuration_path\":";
    append_optional_path(output, configuration_path);
    output << ",\"status_socket\":";
    append_optional_path(output, status_socket_path);
    output
        << ",\"manifest_path\":"
        << json_quote(owner.deployment().manifest_path.generic_string())
        << ",\"deployment_id\":"
        << json_quote(owner.deployment().deployment_id)
        << ",\"folder_id\":" << json_quote(owner.deployment().folder_id)
        << ",\"local_device_id\":"
        << json_quote(owner.deployment().local_actor.device_id)
        << ",\"local_epoch\":" << owner.deployment().local_actor.epoch
        << ",\"remote_device_id\":"
        << json_quote(owner.expected_peer().actor.device_id)
        << ",\"remote_epoch\":" << owner.expected_peer().actor.epoch
        << ",\"transport\":"
        << json_quote(sync_replica_stream_route_kind_name(owner.route_kind()))
        << ",\"ingress_transport\":"
        << json_quote(sync_replica_peer_ingress_kind_name(owner.ingress_kind()))
        << ",\"ingress_ready\":" << json_bool(owner.ingress_ready())
        << ",\"numeric_listener_active\":"
        << json_bool(owner.has_numeric_listener())
        << ",\"bind_address\":";
    if (owner.has_numeric_listener()) {
        output << json_quote(owner.listen_endpoint().numeric_address);
    } else {
        output << "null";
    }
    output << ",\"listen_port\":";
    if (owner.has_numeric_listener()) {
        output << owner.listen_endpoint().port;
    } else {
        output << "null";
    }
    output
        << ",\"local_recovery_initiator\":"
        << json_bool(owner.local_is_recovery_initiator())
        << ",\"role\":"
        << json_quote(sync_replica_peer_service_role_name(owner.role()))
        << ",\"initial_repair_complete\":"
        << json_bool(owner.initial_repair_complete());

    output << ",\"filesystem_watch\":";
    append_folder_wake_snapshot(output, owner.folder_wake_snapshot());

    output << ",\"payload_scrub\":";
    append_payload_scrub_status(output, payload_scrub);
    output << ",\"payload_terminal_verification\":";
    append_payload_terminal_verification_status(
        output, payload_terminal_verification);
    output << ",\"source_manifest_projection\":";
    append_source_manifest_projection_status(
        output, source_manifest_projection);
    output << ",\"payload_integrity\":";
    append_payload_integrity_status(
        output, payload_integrity, payload_integrity_recovery);
    output << ",\"payload_recheck\":";
    append_payload_recheck_status(output, payload_recheck);
    output << ",\"payload_quarantine\":";
    append_payload_quarantine_status(output, payload_quarantine);
    output << ",\"historical_versions\":";
    append_historical_version_status(output, historical_versions);

    output << ",\"stop_reason\":";
    if (stop_reason.has_value()) {
        output << json_quote(*stop_reason);
    } else {
        output << "null";
    }

    output
        << ",\"counters\":{\"steps\":" << counters.steps
        << ",\"initial_repairs\":" << counters.initial_repairs
        << ",\"initial_repair_payload_snapshot_handoffs\":"
        << counters.initial_repair_payload_snapshot_handoffs
        << ",\"initial_repair_payload_snapshot_handoff_entries\":"
        << counters.initial_repair_payload_snapshot_handoff_entries
        << ",\"initial_repair_convergence_snapshot_observations\":"
        << counters.initial_repair_convergence_snapshot_observations
        << ",\"initial_repair_convergence_mutation_full_scans\":"
        << counters.initial_repair_convergence_mutation_full_scans
        << ",\"periodic_repairs\":" << counters.periodic_repairs
        << ",\"filesystem_wake_repairs\":"
        << counters.filesystem_wake_repairs
        << ",\"filesystem_wakes_consumed_by_outbound\":"
        << counters.filesystem_wakes_consumed_by_outbound
        << ",\"outbound_cycles\":" << counters.outbound_cycles
        << ",\"outbound_handoffs\":" << counters.outbound_handoffs
        << ",\"outbound_failures\":" << counters.outbound_failures
        << ",\"outbound_session_io_failures\":"
        << counters.outbound_session_io_failures
        << ",\"inbound_accept_windows_expired\":"
        << counters.inbound_accept_windows_expired
        << ",\"inbound_sessions\":" << counters.inbound_sessions
        << ",\"inbound_session_io_failures\":"
        << counters.inbound_session_io_failures
        << ",\"inbound_exact_peer_sessions\":"
        << counters.inbound_exact_peer_sessions
        << ",\"inbound_handoffs\":" << counters.inbound_handoffs
        << ",\"ingress_setup_attempts\":"
        << counters.ingress_setup_attempts
        << ",\"ingress_setup_successes\":"
        << counters.ingress_setup_successes
        << ",\"ingress_setup_failures\":"
        << counters.ingress_setup_failures
        << ",\"ingress_losses\":" << counters.ingress_losses
        << ",\"ingress_backoff_deferrals\":"
        << counters.ingress_backoff_deferrals
        << ",\"payload_integrity_faults_observed\":"
        << counters.payload_integrity_faults_observed
        << ",\"payload_integrity_reproof_attempts\":"
        << counters.payload_integrity_reproof_attempts
        << ",\"payload_integrity_reproof_recoveries\":"
        << counters.payload_integrity_reproof_recoveries
        << ",\"payload_integrity_reproof_snapshot_handoffs\":"
        << counters.payload_integrity_reproof_snapshot_handoffs
        << ",\"payload_integrity_reproof_convergence_snapshot_observations\":"
        << counters
               .payload_integrity_reproof_convergence_snapshot_observations
        << ",\"payload_integrity_reproof_convergence_mutation_full_scans\":"
        << counters
               .payload_integrity_reproof_convergence_mutation_full_scans
        << ",\"payload_integrity_backoff_deferrals\":"
        << counters.payload_integrity_backoff_deferrals
        << ",\"payload_store_lease_busy_deferrals\":"
        << counters.payload_store_lease_busy_deferrals
        << ",\"payload_store_lease_backoff_deferrals\":"
        << counters.payload_store_lease_backoff_deferrals
        << ",\"payload_authority_network_outcome_uncertain_steps\":"
        << counters.payload_authority_network_outcome_uncertain_steps
        << ",\"payload_terminal_verification_scheduler_steps\":"
        << counters.payload_terminal_verification_scheduler_steps
        << ",\"payload_terminal_verification_progress_steps\":"
        << counters.payload_terminal_verification_progress_steps
        << ",\"payload_terminal_verification_completions\":"
        << counters.payload_terminal_verification_completions
        << ",\"payload_terminal_verification_insertions\":"
        << counters.payload_terminal_verification_insertions
        << ",\"payload_terminal_verification_reconciliations\":"
        << counters.payload_terminal_verification_reconciliations
        << ",\"payload_terminal_verification_hashed_bytes\":"
        << counters.payload_terminal_verification_hashed_bytes
        << ",\"payload_terminal_verification_ordinary_turn_yields\":"
        << counters.payload_terminal_verification_ordinary_turn_yields
        << ",\"source_manifest_projection_scheduler_steps\":"
        << counters.source_manifest_projection_scheduler_steps
        << ",\"source_manifest_projection_progress_steps\":"
        << counters.source_manifest_projection_progress_steps
        << ",\"source_manifest_projection_completions\":"
        << counters.source_manifest_projection_completions
        << ",\"source_manifest_projection_payload_unavailable\":"
        << counters.source_manifest_projection_payload_unavailable
        << ",\"source_manifest_projection_restarts\":"
        << counters.source_manifest_projection_restarts
        << ",\"source_manifest_projection_hashed_bytes\":"
        << counters.source_manifest_projection_hashed_bytes
        << ",\"source_manifest_projection_ordinary_turn_yields\":"
        << counters.source_manifest_projection_ordinary_turn_yields
        << ",\"payload_recheck_requests_observed\":"
        << counters.payload_recheck_requests_observed
        << ",\"payload_recheck_requests_coalesced\":"
        << counters.payload_recheck_requests_coalesced
        << ",\"payload_recheck_attempts\":"
        << counters.payload_recheck_attempts
        << ",\"payload_recheck_completions\":"
        << counters.payload_recheck_completions
        << ",\"payload_recheck_integrity_recoveries\":"
        << counters.payload_recheck_integrity_recoveries
        << ",\"payload_recheck_snapshot_handoffs\":"
        << counters.payload_recheck_snapshot_handoffs
        << ",\"payload_recheck_convergence_snapshot_observations\":"
        << counters.payload_recheck_convergence_snapshot_observations
        << ",\"payload_recheck_convergence_mutation_full_scans\":"
        << counters.payload_recheck_convergence_mutation_full_scans
        << ",\"payload_quarantine_requests_observed\":"
        << counters.payload_quarantine_requests_observed
        << ",\"payload_quarantine_requests_coalesced\":"
        << counters.payload_quarantine_requests_coalesced
        << ",\"payload_quarantine_attempts\":"
        << counters.payload_quarantine_attempts
        << ",\"payload_quarantine_completions\":"
        << counters.payload_quarantine_completions
        << ",\"payload_quarantine_images_preserved\":"
        << counters.payload_quarantine_images_preserved
        << ",\"payload_quarantine_images_released\":"
        << counters.payload_quarantine_images_released
        << ",\"payload_quarantine_observed_content_changes\":"
        << counters.payload_quarantine_observed_content_changes
        << ",\"historical_version_requests_observed\":"
        << counters.historical_version_requests_observed
        << ",\"historical_version_requests_coalesced\":"
        << counters.historical_version_requests_coalesced
        << ",\"historical_version_attempts\":"
        << counters.historical_version_attempts
        << ",\"historical_version_completions\":"
        << counters.historical_version_completions
        << ",\"historical_version_inspections\":"
        << counters.historical_version_inspections
        << ",\"historical_version_retention_plans\":"
        << counters.historical_version_retention_plans
        << ",\"historical_version_restores\":"
        << counters.historical_version_restores
        << ",\"historical_version_pins\":"
        << counters.historical_version_pins
        << ",\"historical_version_unpins\":"
        << counters.historical_version_unpins
        << ",\"historical_version_failures\":"
        << counters.historical_version_failures
        << ",\"cycles_complete\":" << summary.cycles_complete
        << ",\"cycles_settled\":" << summary.cycles_settled
        << ",\"cycles_changed\":" << summary.cycles_changed
        << ",\"cycles_with_unresolved_paths\":"
        << summary.cycles_with_unresolved_paths
        << ",\"cycles_partial_progress\":"
        << summary.cycles_partial_progress
        << ",\"cycles_failed\":" << summary.cycles_failed
        << ",\"cycles_with_durable_progress\":"
        << summary.cycles_with_durable_progress
        << ",\"accepted_sessions\":" << summary.accepted_sessions
        << ",\"completed_handshakes\":" << summary.completed_handshakes
        << ",\"rejected_handshakes\":" << summary.rejected_handshakes
        << ",\"unauthorized_peers\":" << summary.unauthorized_peers
        << ",\"applications_served\":" << summary.applications_served
        << ",\"file_delivery_sessions\":"
        << summary.file_delivery_sessions
        << ",\"reconciliation_sessions\":"
        << summary.reconciliation_sessions << '}';

    output << ",\"last_ingress\":";
    append_ingress_event(output, summary.last_ingress_event);

    output << ",\"last_step\":";
    if (!summary.last_step.has_value()) {
        output << "null";
    } else {
        const auto& step = *summary.last_step;
        output
            << "{\"disposition\":"
            << json_quote(sync_replica_peer_service_step_disposition_name(
                   step.disposition))
            << ",\"role_before\":"
            << json_quote(sync_replica_peer_service_role_name(
                   step.role_before))
            << ",\"role_after\":"
            << json_quote(sync_replica_peer_service_role_name(step.role_after))
            << ",\"exact_peer_observed\":"
            << json_bool(step.exact_peer_observed)
            << ",\"network_turn_handed_off\":"
            << json_bool(step.network_turn_handed_off)
            << ",\"network_outcome_known\":"
            << json_bool(step.network_outcome_known)
            << ",\"payload_store_lease_conflict_observed\":"
            << json_bool(step.payload_store_lease_conflict_observed)
            << ",\"filesystem_wake_observed\":"
            << json_bool(step.filesystem_wake_observed)
            << ",\"filesystem_wake_overflow\":"
            << json_bool(step.filesystem_wake_overflow)
            << ",\"filesystem_watch_rebuilt\":"
            << json_bool(step.filesystem_watch_rebuilt)
            << ",\"filesystem_wake_event_count\":"
            << step.filesystem_wake_event_count
            << ",\"consecutive_outbound_failures\":"
            << step.consecutive_outbound_failures
            << ",\"retry_delay_milliseconds\":"
            << step.retry_delay_milliseconds
            << ",\"ingress_ready\":" << json_bool(step.ingress_ready)
            << ",\"consecutive_ingress_failures\":"
            << step.consecutive_ingress_failures
            << ",\"ingress_retry_delay_milliseconds\":"
            << step.ingress_retry_delay_milliseconds
            << ",\"payload_integrity_retry_delay_milliseconds\":"
            << step.payload_integrity_retry_delay_milliseconds
            << ",\"payload_store_lease_retry_delay_milliseconds\":"
            << step.payload_store_lease_retry_delay_milliseconds
            << ",\"payload_terminal_verification\":";
        append_payload_terminal_verification_step(
            output, step.payload_terminal_verification);
        output << ",\"source_manifest_projection\":";
        append_source_manifest_projection_step(
            output, step.source_manifest_projection);
        output
            << ",\"payload_recheck_generation\":"
            << step.payload_recheck_generation
            << ",\"payload_recheck_hashed_entries\":"
            << step.payload_recheck_hashed_entry_count
            << ",\"payload_recheck_hashed_bytes\":"
            << step.payload_recheck_hashed_bytes
            << ",\"payload_recheck_snapshot_handoffs\":"
            << step.payload_recheck_snapshot_handoff_count
            << ",\"payload_recheck_convergence_snapshot_observations\":"
            << step
                   .payload_recheck_convergence_snapshot_observation_count
            << ",\"payload_recheck_convergence_mutation_full_scans\":"
            << step
                   .payload_recheck_convergence_mutation_full_scan_count
            << ",\"payload_recheck_recovered_integrity_fault\":"
            << json_bool(
                   step.payload_recheck_recovered_integrity_fault)
            << ",\"payload_quarantine_generation\":"
            << step.payload_quarantine_generation
            << ",\"payload_quarantine_result\":";
        append_payload_quarantine_result(
            output, step.payload_quarantine_result);
        output
            << ",\"historical_version_generation\":"
            << step.historical_version_generation
            << ",\"historical_version_action\":";
        if (step.historical_version_action.has_value()) {
            output << json_quote(
                sync_replica_peer_service_historical_version_action_name(
                    *step.historical_version_action));
        } else {
            output << "null";
        }
        output << ",\"historical_version_restore_request\":";
        append_historical_version_restore_request(
            output, step.historical_version_restore_request);
        output << ",\"historical_version_retention_operation_id\":";
        if (step.historical_version_retention_operation_id.empty()) {
            output << "null";
        } else {
            output << json_quote(
                step.historical_version_retention_operation_id);
        }
        output << ",\"historical_version_inventory\":";
        append_historical_version_inventory(
            output, step.historical_version_inventory);
        output << ",\"historical_version_retention_plan\":";
        append_retention_plan(
            output, step.historical_version_retention_plan);
        output << ",\"historical_version_restore\":";
        append_historical_version_restore(
            output, step.historical_version_restore);
        output << ",\"historical_version_pin_update\":";
        append_historical_version_pin_update(
            output, step.historical_version_pin_update);
        output << ",\"historical_version_failure_class\":";
        if (step.historical_version_failure_class.has_value()) {
            output << json_quote(
                sync_replica_peer_service_historical_version_failure_class_name(
                    *step.historical_version_failure_class));
        } else {
            output << "null";
        }
        output << ",\"historical_version_source_change_stage\":";
        if (step.historical_version_source_change_stage.has_value()) {
            output << json_quote(
                sync_replica_historical_version_source_change_stage_name(
                    *step.historical_version_source_change_stage));
        } else {
            output << "null";
        }
        output << ",\"historical_version_failure\":";
        if (step.historical_version_failure.has_value()) {
            output << json_quote(*step.historical_version_failure);
        } else {
            output << "null";
        }
        output << ",\"session_io_error\":";
        if (step.session_io_error.has_value()) {
            output << json_quote(*step.session_io_error);
        } else {
            output << "null";
        }
        output << '}';
    }
    output << '}';
    return output.str();
}

}  // namespace anonsync

#endif
