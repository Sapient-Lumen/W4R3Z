 13572	        out.daemon_heartbeat_daemon_id = document.daemon_id;
 13573	        out.daemon_heartbeat_worker_id = document.worker_id;
 13574	        out.daemon_heartbeat_owner_lock_id =
 13575	            document.owner_lock.owner_lock_id;
 13576	        out.daemon_heartbeat_epoch = document.heartbeat_epoch;
 13577	        out.daemon_heartbeat_stale_after_seconds =
 13578	            document.stale_after_seconds;
 13579	        out.daemon_heartbeat_stale_at_epoch = document.stale_at_epoch;
 13580	        out.daemon_heartbeat_process_id = document.process_id;
 13581	        out.daemon_heartbeat_owner_lock_epoch =
 13582	            document.owner_lock.owner_lock_epoch;
 13583	
 13584	        out.daemon_heartbeat_session_matches =
 13585	            document.session_id == options.session_id;
 13586	        if (!out.daemon_heartbeat_session_matches) {
 13587	            sync_append_heartbeat_error(
 13588	                out.daemon_heartbeat_error,
 13589	                "heartbeat session_id does not match checkpoint query");
 13590	        }
 13591	        out.daemon_heartbeat_checkpoint_matches =
 13592	            sync_paths_match_lexically(document.checkpoint_path,
 13593	                                       options.sqlite_path);
 13594	        if (!out.daemon_heartbeat_checkpoint_matches) {
 13595	            sync_append_heartbeat_error(
 13596	                out.daemon_heartbeat_error,
 13597	                "heartbeat checkpoint_path does not match checkpoint query");
 13598	        }
 13599	
 13600	        const bool service_instance_matches =
 13601	            sync_daemon_heartbeat_service_instance_matches_document_or_throw(
 13602	                document);
 13603	        if (!service_instance_matches) {
 13604	            sync_append_heartbeat_error(
 13605	                out.daemon_heartbeat_error,
 13606	                "heartbeat service_instance_id is not bound to its session, daemon, worker, and restart epoch");
 13607	        }
 13608	
 13609	        if (document.owner_lock.required) {
 13610	            const bool durable_released =
 13611	                out.daemon_owner_lock_rows == 1 &&
 13612	                !out.daemon_owner_lock_held &&
 13613	                out.daemon_owner_lock_released_at_epoch != 0;
 13614	            out.daemon_heartbeat_owner_lock_matches =
 13615	                out.daemon_owner_lock_rows == 1 &&
 13616	                document.daemon_id == out.daemon_owner_lock_daemon_id &&
 13617	                document.worker_id == out.daemon_owner_lock_worker_id &&
 13618	                document.owner_lock.owner_lock_id ==
 13619	                    out.daemon_owner_lock_id &&
 13620	                document.owner_lock.owner_lock_epoch ==
 13621	                    out.daemon_owner_lock_epoch &&
 13622	                document.owner_lock.acquired_at_epoch ==
 13623	                    out.daemon_owner_lock_acquired_at_epoch &&
 13624	                document.owner_lock.expires_at_epoch ==
 13625	                    out.daemon_owner_lock_expires_at_epoch &&
 13626	                document.owner_lock.released == durable_released &&
 13627	                document.owner_lock.released_at_epoch ==
 13628	                    out.daemon_owner_lock_released_at_epoch;
 13629	        } else {
 13630	            out.daemon_heartbeat_owner_lock_matches =
 13631	                out.daemon_owner_lock_rows == 0;
 13632	        }
 13633	        if (!out.daemon_heartbeat_owner_lock_matches) {
 13634	            sync_append_heartbeat_error(
 13635	                out.daemon_heartbeat_error,
 13636	                "heartbeat is not bound to the exact durable owner generation");
 13637	        }
 13638	
 13639	        const bool identity_and_owner_match =
 13640	            out.daemon_heartbeat_session_matches &&
 13641	            out.daemon_heartbeat_checkpoint_matches &&
 13642	            service_instance_matches &&
 13643	            out.daemon_heartbeat_owner_lock_matches;
 13644	        out.daemon_heartbeat_stale =
 13645	            out.scheduler_clock_provided &&
 13646	            document.stale_at_epoch != 0 &&
 13647	            options.scheduler_now_epoch >= document.stale_at_epoch;
 13648	
 13649	        bool lifecycle_policy_ok = true;
 13650	        if (!document.final) {
 13651	            if (document.stale_after_seconds == 0 ||
 13652	                document.stale_at_epoch == 0) {
 13653	                lifecycle_policy_ok = false;
 13654	                sync_append_heartbeat_error(
 13655	                    out.daemon_heartbeat_error,
 13656	                    "non-final heartbeat has no stale horizon and blocks service re-entry");
 13657	            } else if (!out.scheduler_clock_provided) {
 13658	                lifecycle_policy_ok = false;
 13659	                sync_append_heartbeat_error(
 13660	                    out.daemon_heartbeat_error,
 13661	                    "scheduler clock is required to classify a non-final heartbeat");
 13662	            } else if (out.daemon_heartbeat_stale) {
 13663	                if (out.daemon_owner_lock_live) {
 13664	                    lifecycle_policy_ok = false;
 13665	                    sync_append_heartbeat_error(
 13666	                        out.daemon_heartbeat_error,
 13667	                        "heartbeat is stale while its durable owner generation is still live");
 13668	                }
 13669	            } else if (!out.daemon_owner_lock_live) {
 13670	                lifecycle_policy_ok = false;
 13671	                sync_append_heartbeat_error(
 13672	                    out.daemon_heartbeat_error,
 13673	                    "fresh non-final heartbeat blocks service re-entry until " +
 13674	                        u64_string(document.stale_at_epoch));
 13675	            }
 13676	        }
 13677	
 13678	        out.daemon_heartbeat_attention_required =
