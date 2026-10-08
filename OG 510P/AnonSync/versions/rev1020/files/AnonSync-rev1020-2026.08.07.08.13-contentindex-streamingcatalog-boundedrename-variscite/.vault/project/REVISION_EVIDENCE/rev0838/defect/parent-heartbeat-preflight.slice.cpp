    return static_cast<std::uint64_t>(::getpid());
#endif
}

std::string sync_bool_json(bool value) {
    return value ? "true" : "false";
}

Json load_sync_daemon_heartbeat_json_or_throw(const fs::path& heartbeat_path) {
    constexpr std::uint64_t kMaxHeartbeatJsonBytes = 64 * 1024;
    return parse_json_text(read_sync_bounded_regular_file_no_symlink_or_throw(heartbeat_path,
                                                                         kMaxHeartbeatJsonBytes,
                                                                         "sync daemon service heartbeat"));
}

std::string sync_daemon_heartbeat_json(const SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions& options,
                                       const SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult& result,
                                       const std::string& state,
                                       std::uint64_t heartbeat_epoch,
                                       std::uint64_t stale_at_epoch,
                                       bool final,
                                       const std::string& reason) {
    std::ostringstream out;
    out << "{\n"
        << "  \"format\": \"anonsync-sync-daemon-service-heartbeat-v1\",\n"
        << "  \"revision_id\": \"rev0741\",\n"
        << "  \"operation\": \"sync-daemon-service-heartbeat\",\n"
        << "  \"service_instance_id\": \"" << json_escape(result.service_instance_id) << "\",\n"
        << "  \"service_restart_epoch\": " << result.service_restart_epoch << ",\n"
        << "  \"state\": \"" << json_escape(state) << "\",\n"
        << "  \"final\": " << sync_bool_json(final) << ",\n"
        << "  \"reason\": \"" << json_escape(reason) << "\",\n"
        << "  \"heartbeat_epoch\": " << heartbeat_epoch << ",\n"
        << "  \"stale_after_seconds\": " << options.daemon_heartbeat_stale_after_seconds << ",\n"
        << "  \"stale_at_epoch\": " << stale_at_epoch << ",\n"
        << "  \"process_id\": " << result.daemon_heartbeat_process_id << ",\n"
        << "  \"checkpoint_path\": \"" << json_escape(options.sqlite_path) << "\",\n"
        << "  \"session_id\": \"" << json_escape(options.session_id) << "\",\n"
        << "  \"daemon_id\": \"" << json_escape(result.daemon_id) << "\",\n"
        << "  \"worker_id\": \"" << json_escape(result.worker_id) << "\",\n"
        << "  \"service_lifecycle\": {\n"
        << "    \"preflight_checked\": " << sync_bool_json(result.service_lifecycle_preflight_checked) << ",\n"
        << "    \"preflight_passed\": " << sync_bool_json(result.service_lifecycle_preflight_passed) << ",\n"
        << "    \"live_owner_blocked\": " << sync_bool_json(result.service_lifecycle_live_owner_blocked) << ",\n"
        << "    \"heartbeat_checked\": " << sync_bool_json(result.service_lifecycle_heartbeat_checked) << ",\n"
        << "    \"existing_heartbeat_loaded\": " << sync_bool_json(result.service_lifecycle_heartbeat_existing_loaded) << ",\n"
        << "    \"existing_heartbeat_final\": " << sync_bool_json(result.service_lifecycle_heartbeat_existing_final) << ",\n"
        << "    \"existing_heartbeat_fresh\": " << sync_bool_json(result.service_lifecycle_heartbeat_existing_fresh) << ",\n"
        << "    \"existing_heartbeat_stale\": " << sync_bool_json(result.service_lifecycle_heartbeat_existing_stale) << ",\n"
        << "    \"reentry_from_stale_heartbeat\": " << sync_bool_json(result.service_lifecycle_reentry_from_stale_heartbeat) << ",\n"
        << "    \"preflight_reason\": \"" << json_escape(result.service_lifecycle_preflight_reason) << "\"\n"
        << "  },\n"
        << "  \"owner_lock\": {\n"
        << "    \"required\": " << sync_bool_json(result.daemon_owner_lock_required) << ",\n"
        << "    \"acquired\": " << sync_bool_json(result.daemon_owner_lock_acquired) << ",\n"
        << "    \"released\": " << sync_bool_json(result.daemon_owner_lock_released) << ",\n"
        << "    \"reclaimed_expired\": " << sync_bool_json(result.daemon_owner_lock_reclaimed_expired) << ",\n"
        << "    \"owner_lock_id\": \"" << json_escape(result.daemon_owner_lock_id) << "\",\n"
        << "    \"owner_lock_epoch\": " << result.daemon_owner_lock_epoch << ",\n"
        << "    \"acquired_at_epoch\": " << result.daemon_owner_lock_acquired_at_epoch << ",\n"
        << "    \"expires_at_epoch\": " << result.daemon_owner_lock_expires_at_epoch << ",\n"
        << "    \"released_at_epoch\": " << result.daemon_owner_lock_released_at_epoch << "\n"
        << "  },\n"
        << "  \"lease\": {\n"
        << "    \"worker_lease_id\": \"" << json_escape(result.final_worker_lease_id) << "\",\n"
        << "    \"final_worker_lease_epoch\": " << result.final_worker_lease_epoch << ",\n"
        << "    \"next_worker_lease_epoch\": " << result.next_worker_lease_epoch << ",\n"
        << "    \"next_scheduler_now_epoch\": " << result.next_scheduler_now_epoch << "\n"
        << "  },\n"
        << "  \"progress\": {\n"
        << "    \"passes_attempted\": " << result.passes_attempted << ",\n"
        << "    \"passes_completed\": " << result.passes_completed << ",\n"
        << "    \"mutating_passes\": " << result.mutating_passes << ",\n"
        << "    \"idle_passes\": " << result.idle_passes << ",\n"
        << "    \"startup_sidecar_recovery_attempted\": " << sync_bool_json(result.startup_sidecar_recovery_attempted) << ",\n"
        << "    \"startup_sidecar_recovery_completed\": " << sync_bool_json(result.startup_sidecar_recovery_completed) << ",\n"
        << "    \"checkpoint_schema_version\": \"" << json_escape(result.startup_sidecar_recovery_checkpoint_schema_version) << "\",\n"
        << "    \"archived_checkpoint_migration_backfill_checked\": " << sync_bool_json(result.startup_sidecar_recovery_archived_checkpoint_migration_backfill_checked) << ",\n"
        << "    \"archived_checkpoint_exact_startup_hydration_supported\": " << sync_bool_json(result.startup_sidecar_recovery_archived_checkpoint_exact_startup_hydration_supported) << ",\n"
        << "    \"archived_checkpoint_migration_backfill_required\": " << sync_bool_json(result.startup_sidecar_recovery_archived_checkpoint_migration_backfill_required) << ",\n"
        << "    \"archived_checkpoint_migration_backfill_blocked_missing_lineage\": " << sync_bool_json(result.startup_sidecar_recovery_archived_checkpoint_migration_backfill_blocked_missing_lineage) << ",\n"
        << "    \"archived_checkpoint_claimed_paths_blocked_by_missing_lineage\": " << result.startup_sidecar_recovery_archived_checkpoint_claimed_paths_blocked_by_missing_lineage << ",\n"
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
        << "    \"workorder_rows_claimed\": " << result.workorder_rows_claimed << ",\n"
        << "    \"workorder_rows_reclaimed\": " << result.workorder_rows_reclaimed << ",\n"
        << "    \"workorder_rows_completed\": " << result.workorder_rows_completed << ",\n"
        << "    \"chunks_written\": " << result.chunks_written << ",\n"
        << "    \"bytes_written\": " << result.bytes_written << "\n"
        << "  }\n"
        << "}\n";
    return out.str();
}

std::uint64_t sync_daemon_heartbeat_required_u64_or_throw(const Json& object,
                                                          const std::string& key,
                                                          const std::string& label) {
    const Json& field = object.at(key);
    if (!field.is_number()) {
        throw std::runtime_error(label + " is missing or not numeric");
    }
    const long long value = field.integer(-1);
    if (value < 0) {
        throw std::runtime_error(label + " must be nonnegative");
    }
    return static_cast<std::uint64_t>(value);
}

bool sync_daemon_heartbeat_paths_match_lexically(const std::string& left, const std::string& right) {
    if (left.empty() || right.empty()) return false;
    try {
        return absolute_lexically_normal_path_or_throw(left, "left sync daemon heartbeat preflight checkpoint path").string() ==
               absolute_lexically_normal_path_or_throw(right, "right sync daemon heartbeat preflight checkpoint path").string();
    } catch (...) {
        return left == right;
    }
}

SyncValidationResult check_sync_daemon_service_lifecycle_preflight(const SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions& options,
                                                                   SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult& out,
                                                                   std::uint64_t observed_at_epoch) {
    out.service_lifecycle_preflight_checked = true;
    if (options.daemon_heartbeat_path.empty()) {
        out.service_lifecycle_preflight_passed = true;
        if (out.service_lifecycle_preflight_reason.empty()) {
            out.service_lifecycle_preflight_reason = "no heartbeat path configured";
        }
        return ok_result();
    }
    out.service_lifecycle_heartbeat_checked = true;
    try {
        const fs::path heartbeat_path = absolute_lexically_normal_path_or_throw(options.daemon_heartbeat_path,
                                                                                "sync daemon service lifecycle preflight heartbeat path");
        std::error_code ec;
        const fs::file_status status = fs::symlink_status(heartbeat_path, ec);
        if (ec) {
            if (ec == std::make_error_code(std::errc::no_such_file_or_directory)) {
                out.service_lifecycle_preflight_passed = true;
                out.service_lifecycle_preflight_reason = "no prior heartbeat file exists";
                return ok_result();
            }
            return fail_result("sync daemon service lifecycle preflight could not inspect heartbeat path: " + ec.message());
        }
        if (!fs::exists(status)) {
            out.service_lifecycle_preflight_passed = true;
            out.service_lifecycle_preflight_reason = "no prior heartbeat file exists";
            return ok_result();
        }
        if (fs::is_symlink(status)) {
            return fail_result("sync daemon service lifecycle preflight refused symlink heartbeat path");
        }
        if (!fs::is_regular_file(status)) {
            return fail_result("sync daemon service lifecycle preflight refused non-regular heartbeat path");
        }

        Json heartbeat = load_sync_daemon_heartbeat_json_or_throw(heartbeat_path);
        out.service_lifecycle_heartbeat_existing_loaded = true;
        if (!heartbeat.is_object()) {
            return fail_result("sync daemon service lifecycle preflight refused heartbeat JSON with non-object root");
        }
        if (heartbeat.at("format").str() != "anonsync-sync-daemon-service-heartbeat-v1") {
            return fail_result("sync daemon service lifecycle preflight refused heartbeat format mismatch");
        }
        const std::string checkpoint_path = heartbeat.at("checkpoint_path").str();
        const std::string session_id = heartbeat.at("session_id").str();
        if (!sync_daemon_heartbeat_paths_match_lexically(checkpoint_path, options.sqlite_path) || session_id != options.session_id) {
            return fail_result("sync daemon service lifecycle preflight refused heartbeat for a different checkpoint or session");
        }

        out.service_lifecycle_existing_heartbeat_state = heartbeat.at("state").str();
        out.service_lifecycle_existing_heartbeat_daemon_id = heartbeat.at("daemon_id").str();
        out.service_lifecycle_heartbeat_existing_final = heartbeat.at("final").boolean(false);
        out.service_lifecycle_existing_heartbeat_epoch = sync_daemon_heartbeat_required_u64_or_throw(heartbeat,
                                                                                                     "heartbeat_epoch",
                                                                                                     "heartbeat_epoch");
        const std::uint64_t stale_after_seconds = sync_daemon_heartbeat_required_u64_or_throw(heartbeat,
                                                                                              "stale_after_seconds",
                                                                                              "stale_after_seconds");
        out.service_lifecycle_existing_heartbeat_stale_at_epoch = sync_daemon_heartbeat_required_u64_or_throw(heartbeat,
                                                                                                              "stale_at_epoch",
                                                                                                              "stale_at_epoch");
        const Json& owner_lock = heartbeat.at("owner_lock");
        if (!owner_lock.is_object()) {
            return fail_result("sync daemon service lifecycle preflight refused heartbeat without owner_lock object");
        }
        out.service_lifecycle_existing_heartbeat_owner_lock_id = owner_lock.at("owner_lock_id").str();

        if (out.service_lifecycle_heartbeat_existing_final) {
            out.service_lifecycle_preflight_passed = true;
            out.service_lifecycle_preflight_reason = "prior heartbeat is final observational evidence";
            return ok_result();
        }
        if (stale_after_seconds == 0 || out.service_lifecycle_existing_heartbeat_stale_at_epoch == 0) {
            out.service_lifecycle_heartbeat_existing_fresh = true;
            return fail_result("sync daemon service lifecycle preflight refused non-final heartbeat without a stale horizon");
        }
        if (observed_at_epoch < out.service_lifecycle_existing_heartbeat_stale_at_epoch) {
            out.service_lifecycle_heartbeat_existing_fresh = true;
            return fail_result("sync daemon service lifecycle preflight refused fresh non-final heartbeat from daemon " +
                               out.service_lifecycle_existing_heartbeat_daemon_id + " until " +
                               u64_string(out.service_lifecycle_existing_heartbeat_stale_at_epoch));
        }
        out.service_lifecycle_heartbeat_existing_stale = true;
        out.service_lifecycle_reentry_from_stale_heartbeat = true;
        out.service_lifecycle_preflight_passed = true;
        out.service_lifecycle_preflight_reason = "stale non-final heartbeat permits service re-entry after owner-lock check";
        return ok_result();
    } catch (const std::exception& e) {
        return fail_result(std::string("sync daemon service lifecycle preflight failed: ") + e.what());
    }
}


std::string sync_terminal_tombstone_apply_idempotency_key_or_throw(const std::string& session_id,
                                                                  const NormalizedSyncPath& path,
                                                                  const std::string& apply_intent_key,
                                                                  const std::string& local_entry_digest,
                                                                  const std::string& local_version_digest,
                                                                  const std::string& remote_entry_digest,
                                                                  const std::string& remote_version_digest,
