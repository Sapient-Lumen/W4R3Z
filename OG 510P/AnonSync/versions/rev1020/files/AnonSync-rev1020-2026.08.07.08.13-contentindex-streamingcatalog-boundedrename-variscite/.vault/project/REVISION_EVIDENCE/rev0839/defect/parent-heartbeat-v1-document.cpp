   400	
   401	    SyncDaemonHeartbeatDocument document;
   402	    document.format = require_string_field(root, "format", "sync daemon heartbeat");
   403	    document.revision_id =
   404	        require_string_field(root, "revision_id", "sync daemon heartbeat");
   405	    document.operation =
   406	        require_string_field(root, "operation", "sync daemon heartbeat");
   407	    document.service_instance_id = require_string_field(
   408	        root, "service_instance_id", "sync daemon heartbeat");
   409	    document.service_restart_epoch = require_u64_field(
   410	        root, "service_restart_epoch", "sync daemon heartbeat");
   411	    document.state = require_string_field(root, "state", "sync daemon heartbeat");
   412	    document.final = require_bool_field(root, "final", "sync daemon heartbeat");
   413	    document.reason = require_string_field(root, "reason", "sync daemon heartbeat");
   414	    document.heartbeat_epoch = require_u64_field(
   415	        root, "heartbeat_epoch", "sync daemon heartbeat");
   416	    document.stale_after_seconds = require_u64_field(
   417	        root, "stale_after_seconds", "sync daemon heartbeat");
   418	    document.stale_at_epoch = require_u64_field(
   419	        root, "stale_at_epoch", "sync daemon heartbeat");
   420	    document.process_id =
   421	        require_u64_field(root, "process_id", "sync daemon heartbeat");
   422	    document.checkpoint_path = require_string_field(
   423	        root, "checkpoint_path", "sync daemon heartbeat");
   424	    document.session_id =
   425	        require_string_field(root, "session_id", "sync daemon heartbeat");
   426	    document.daemon_id =
   427	        require_string_field(root, "daemon_id", "sync daemon heartbeat");
   428	    document.worker_id =
   429	        require_string_field(root, "worker_id", "sync daemon heartbeat");
   430	
   431	    document.owner_lock.required = require_bool_field(
   432	        owner_lock, "required", "sync daemon heartbeat owner_lock");
   433	    document.owner_lock.acquired = require_bool_field(
   434	        owner_lock, "acquired", "sync daemon heartbeat owner_lock");
   435	    document.owner_lock.released = require_bool_field(
   436	        owner_lock, "released", "sync daemon heartbeat owner_lock");
   437	    document.owner_lock.reclaimed_expired = require_bool_field(
   438	        owner_lock, "reclaimed_expired", "sync daemon heartbeat owner_lock");
   439	    document.owner_lock.owner_lock_id = require_string_field(
   440	        owner_lock,
   441	        "owner_lock_id",
   442	        "sync daemon heartbeat owner_lock",
   443	        !document.owner_lock.required);
   444	    document.owner_lock.owner_lock_epoch = require_u64_field(
   445	        owner_lock, "owner_lock_epoch", "sync daemon heartbeat owner_lock");
   446	    document.owner_lock.acquired_at_epoch = require_u64_field(
   447	        owner_lock, "acquired_at_epoch", "sync daemon heartbeat owner_lock");
   448	    document.owner_lock.expires_at_epoch = require_u64_field(
   449	        owner_lock, "expires_at_epoch", "sync daemon heartbeat owner_lock");
   450	    document.owner_lock.released_at_epoch = require_u64_field(
   451	        owner_lock, "released_at_epoch", "sync daemon heartbeat owner_lock");
   452	
   453	    validate_sync_daemon_heartbeat_document_or_throw(document);
   454	    return document;
   455	}
   456	
   457	std::string encode_sync_daemon_heartbeat_document_or_throw(
   458	    const SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions& options,
   459	    const SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult& result,
   460	    const std::string& state,
   461	    std::uint64_t heartbeat_epoch,
   462	    std::uint64_t stale_at_epoch,
   463	    bool final,
   464	    const std::string& reason) {
   465	    SyncDaemonHeartbeatDocument document;
   466	    document.format = std::string(kFormat);
   467	    document.revision_id = "rev0741";
   468	    document.operation = std::string(kOperation);
   469	    document.service_instance_id = result.service_instance_id;
   470	    document.service_restart_epoch = result.service_restart_epoch;
   471	    document.state = state;
   472	    document.final = final;
   473	    document.reason = reason;
   474	    document.heartbeat_epoch = heartbeat_epoch;
   475	    document.stale_after_seconds = options.daemon_heartbeat_stale_after_seconds;
   476	    document.stale_at_epoch = stale_at_epoch;
   477	    document.process_id = result.daemon_heartbeat_process_id;
   478	    document.checkpoint_path = options.sqlite_path;
   479	    document.session_id = options.session_id;
   480	    document.daemon_id = result.daemon_id;
   481	    document.worker_id = result.worker_id;
   482	    document.owner_lock.required = result.daemon_owner_lock_required;
   483	    document.owner_lock.acquired = result.daemon_owner_lock_acquired;
   484	    document.owner_lock.released = result.daemon_owner_lock_released;
   485	    document.owner_lock.reclaimed_expired =
   486	        result.daemon_owner_lock_reclaimed_expired;
   487	    document.owner_lock.owner_lock_id = result.daemon_owner_lock_id;
   488	    document.owner_lock.owner_lock_epoch = result.daemon_owner_lock_epoch;
   489	    document.owner_lock.acquired_at_epoch =
   490	        result.daemon_owner_lock_acquired_at_epoch;
   491	    document.owner_lock.expires_at_epoch =
   492	        result.daemon_owner_lock_expires_at_epoch;
   493	    document.owner_lock.released_at_epoch =
   494	        result.daemon_owner_lock_released_at_epoch;
   495	    validate_sync_daemon_heartbeat_document_or_throw(document);
   496	    validate_observational_numbers_or_throw(result);
   497	
   498	    std::ostringstream out;
   499	    out << "{\n"
   500	        << "  \"format\": \"anonsync-sync-daemon-service-heartbeat-v1\",\n"
   501	        << "  \"revision_id\": \"rev0741\",\n"
   502	        << "  \"operation\": \"sync-daemon-service-heartbeat\",\n"
   503	        << "  \"service_instance_id\": \""
   504	        << escape_json(result.service_instance_id) << "\",\n"
   505	        << "  \"service_restart_epoch\": " << result.service_restart_epoch
   506	        << ",\n"
   507	        << "  \"state\": \"" << escape_json(state) << "\",\n"
   508	        << "  \"final\": " << bool_json(final) << ",\n"
   509	        << "  \"reason\": \"" << escape_json(reason) << "\",\n"
   510	        << "  \"heartbeat_epoch\": " << heartbeat_epoch << ",\n"
   511	        << "  \"stale_after_seconds\": "
   512	        << options.daemon_heartbeat_stale_after_seconds << ",\n"
   513	        << "  \"stale_at_epoch\": " << stale_at_epoch << ",\n"
   514	        << "  \"process_id\": " << result.daemon_heartbeat_process_id
   515	        << ",\n"
   516	        << "  \"checkpoint_path\": \"" << escape_json(options.sqlite_path)
   517	        << "\",\n"
   518	        << "  \"session_id\": \"" << escape_json(options.session_id)
   519	        << "\",\n"
   520	        << "  \"daemon_id\": \"" << escape_json(result.daemon_id)
   521	        << "\",\n"
   522	        << "  \"worker_id\": \"" << escape_json(result.worker_id)
   523	        << "\",\n"
   524	        << "  \"service_lifecycle\": {\n"
   525	        << "    \"preflight_checked\": "
