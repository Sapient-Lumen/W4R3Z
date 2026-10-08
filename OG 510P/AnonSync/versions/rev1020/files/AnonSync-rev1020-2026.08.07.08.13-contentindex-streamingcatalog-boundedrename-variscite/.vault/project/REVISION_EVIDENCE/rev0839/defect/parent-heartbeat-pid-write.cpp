 12700	    out.daemon_heartbeat_state = state;
 12701	    out.daemon_heartbeat_epoch = heartbeat_epoch;
 12702	    out.daemon_heartbeat_final = final;
 12703	    out.daemon_heartbeat_stale_after_seconds = options.daemon_heartbeat_stale_after_seconds;
 12704	    if (options.daemon_heartbeat_stale_after_seconds != 0) {
 12705	        if (heartbeat_epoch > std::numeric_limits<std::uint64_t>::max() - options.daemon_heartbeat_stale_after_seconds) {
 12706	            throw std::runtime_error("sync daemon service heartbeat stale epoch would overflow");
 12707	        }
 12708	        out.daemon_heartbeat_stale_at_epoch = heartbeat_epoch + options.daemon_heartbeat_stale_after_seconds;
 12709	    } else {
 12710	        out.daemon_heartbeat_stale_at_epoch = 0;
 12711	    }
 12712	    if (out.daemon_heartbeat_process_id == 0) {
 12713	        out.daemon_heartbeat_process_id = sync_current_process_id_or_zero();
 12714	    }
 12715	    const std::string payload =
 12716	        encode_sync_daemon_heartbeat_document_or_throw(
 12717	            options,
 12718	            out,
 12719	            state,
 12720	            heartbeat_epoch,
 12721	            out.daemon_heartbeat_stale_at_epoch,
 12722	            final,
 12723	            reason);
 12724	    write_sync_json_file_atomically_no_symlink_or_throw(heartbeat_path,
