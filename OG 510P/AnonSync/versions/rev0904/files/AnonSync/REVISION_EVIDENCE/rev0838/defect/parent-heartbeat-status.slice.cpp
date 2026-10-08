        out.daemon_heartbeat_path_exists = fs::exists(status);
        if (!out.daemon_heartbeat_path_exists) {
            sync_append_heartbeat_error(out.daemon_heartbeat_error, "heartbeat file is missing");
            return;
        }
        if (fs::is_symlink(status)) {
            sync_append_heartbeat_error(out.daemon_heartbeat_error, "heartbeat file must not be a symlink");
            return;
        }
        out.daemon_heartbeat_path_is_regular_file = fs::is_regular_file(status);
        if (!out.daemon_heartbeat_path_is_regular_file) {
            sync_append_heartbeat_error(out.daemon_heartbeat_error, "heartbeat path is not a regular file");
            return;
        }

        Json heartbeat = load_sync_daemon_heartbeat_json_or_throw(heartbeat_path);
        out.daemon_heartbeat_loaded = true;
        if (!heartbeat.is_object()) {
            sync_append_heartbeat_error(out.daemon_heartbeat_error, "heartbeat JSON root must be an object");
            return;
        }
        out.daemon_heartbeat_format = heartbeat.at("format").str();
        out.daemon_heartbeat_format_ok = out.daemon_heartbeat_format == "anonsync-sync-daemon-service-heartbeat-v1";
        if (!out.daemon_heartbeat_format_ok) {
            sync_append_heartbeat_error(out.daemon_heartbeat_error, "heartbeat format marker mismatch");
        }
        out.daemon_heartbeat_state = heartbeat.at("state").str();
        out.daemon_heartbeat_reason = heartbeat.at("reason").str();
        out.daemon_heartbeat_final = heartbeat.at("final").boolean(false);
        out.daemon_heartbeat_checkpoint_path = heartbeat.at("checkpoint_path").str();
        out.daemon_heartbeat_session_id = heartbeat.at("session_id").str();
        out.daemon_heartbeat_daemon_id = heartbeat.at("daemon_id").str();
        out.daemon_heartbeat_worker_id = heartbeat.at("worker_id").str();
        const Json& owner_lock = heartbeat.at("owner_lock");
        out.daemon_heartbeat_owner_lock_id = owner_lock.at("owner_lock_id").str();

        bool fields_ok = true;
        out.daemon_heartbeat_epoch = sync_json_nonnegative_u64_field_or_zero(heartbeat,
                                                                             "heartbeat_epoch",
                                                                             "heartbeat_epoch",
                                                                             fields_ok,
                                                                             out.daemon_heartbeat_error);
        out.daemon_heartbeat_stale_after_seconds = sync_json_nonnegative_u64_field_or_zero(heartbeat,
                                                                                           "stale_after_seconds",
                                                                                           "stale_after_seconds",
                                                                                           fields_ok,
                                                                                           out.daemon_heartbeat_error);
        out.daemon_heartbeat_stale_at_epoch = sync_json_nonnegative_u64_field_or_zero(heartbeat,
                                                                                      "stale_at_epoch",
                                                                                      "stale_at_epoch",
                                                                                      fields_ok,
                                                                                      out.daemon_heartbeat_error);
        out.daemon_heartbeat_process_id = sync_json_nonnegative_u64_field_or_zero(heartbeat,
                                                                                  "process_id",
                                                                                  "process_id",
                                                                                  fields_ok,
                                                                                  out.daemon_heartbeat_error);
        if (owner_lock.is_object()) {
            out.daemon_heartbeat_owner_lock_epoch = sync_json_nonnegative_u64_field_or_zero(owner_lock,
                                                                                           "owner_lock_epoch",
                                                                                           "owner_lock_epoch",
                                                                                           fields_ok,
                                                                                           out.daemon_heartbeat_error);
        } else {
            fields_ok = false;
            sync_append_heartbeat_error(out.daemon_heartbeat_error, "owner_lock object is missing");
        }

        out.daemon_heartbeat_session_matches = out.daemon_heartbeat_session_id == options.session_id;
        if (!out.daemon_heartbeat_session_matches) {
            sync_append_heartbeat_error(out.daemon_heartbeat_error, "heartbeat session_id does not match checkpoint query");
        }
        out.daemon_heartbeat_checkpoint_matches = sync_paths_match_lexically(out.daemon_heartbeat_checkpoint_path,
                                                                             options.sqlite_path);
        if (!out.daemon_heartbeat_checkpoint_matches) {
            sync_append_heartbeat_error(out.daemon_heartbeat_error, "heartbeat checkpoint_path does not match checkpoint query");
        }
        out.daemon_heartbeat_owner_lock_matches = !out.daemon_owner_lock_held ||
                                                  (out.daemon_heartbeat_owner_lock_id == out.daemon_owner_lock_id &&
                                                   out.daemon_heartbeat_daemon_id == out.daemon_owner_lock_daemon_id &&
                                                   out.daemon_heartbeat_worker_id == out.daemon_owner_lock_worker_id);
        if (!out.daemon_heartbeat_owner_lock_matches) {
            sync_append_heartbeat_error(out.daemon_heartbeat_error, "heartbeat owner lock does not match checkpoint owner lock");
        }
        out.daemon_heartbeat_stale = out.scheduler_clock_provided &&
                                     out.daemon_heartbeat_stale_at_epoch != 0 &&
                                     options.scheduler_now_epoch >= out.daemon_heartbeat_stale_at_epoch;
        if (out.daemon_heartbeat_stale) {
            sync_append_heartbeat_error(out.daemon_heartbeat_error, "heartbeat is stale at the supplied scheduler clock");
        }
        if (!fields_ok) {
            sync_append_heartbeat_error(out.daemon_heartbeat_error, "heartbeat numeric fields are incomplete");
        }
        out.daemon_heartbeat_attention_required = out.daemon_owner_lock_live &&
                                                  (!out.daemon_heartbeat_loaded ||
                                                   !out.daemon_heartbeat_format_ok ||
                                                   !out.daemon_heartbeat_session_matches ||
                                                   !out.daemon_heartbeat_checkpoint_matches ||
                                                   !out.daemon_heartbeat_owner_lock_matches ||
                                                   out.daemon_heartbeat_stale ||
                                                   !fields_ok);
    } catch (const std::exception& e) {
        sync_append_heartbeat_error(out.daemon_heartbeat_error, e.what());
        out.daemon_heartbeat_attention_required = out.daemon_owner_lock_live;
    }
}


SyncValidationResult load_sync_session_checkpoint_operator_status(const SyncSessionCheckpointOperatorStatusOptions& options,
                                                                  SyncSessionCheckpointOperatorStatusResult& out) {
    out = SyncSessionCheckpointOperatorStatusResult{};
