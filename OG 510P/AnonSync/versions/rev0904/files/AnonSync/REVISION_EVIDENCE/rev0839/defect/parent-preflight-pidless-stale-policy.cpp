 11342	        }
 11343	
 11344	        out.service_lifecycle_existing_heartbeat_state = document.state;
 11345	        out.service_lifecycle_existing_heartbeat_daemon_id =
 11346	            document.daemon_id;
 11347	        out.service_lifecycle_heartbeat_existing_final = document.final;
 11348	        out.service_lifecycle_existing_heartbeat_epoch =
 11349	            document.heartbeat_epoch;
 11350	        out.service_lifecycle_existing_heartbeat_stale_at_epoch =
 11351	            document.stale_at_epoch;
 11352	        out.service_lifecycle_existing_heartbeat_owner_lock_id =
 11353	            document.owner_lock.owner_lock_id;
 11354	
 11355	        if (document.final) {
 11356	            out.service_lifecycle_preflight_passed = true;
 11357	            out.service_lifecycle_preflight_reason =
 11358	                "prior heartbeat is final evidence bound to a retired owner generation";
 11359	            return ok_result();
 11360	        }
 11361	        if (document.stale_after_seconds == 0 ||
 11362	            document.stale_at_epoch == 0) {
 11363	            out.service_lifecycle_heartbeat_existing_fresh = true;
 11364	            return fail_result(
 11365	                "sync daemon service lifecycle preflight refused non-final heartbeat without a stale horizon");
 11366	        }
 11367	        if (observed_at_epoch < document.stale_at_epoch) {
 11368	            out.service_lifecycle_heartbeat_existing_fresh = true;
 11369	            return fail_result(
 11370	                "sync daemon service lifecycle preflight refused fresh non-final heartbeat from daemon " +
 11371	                document.daemon_id + " until " +
 11372	                u64_string(document.stale_at_epoch));
 11373	        }
 11374	        out.service_lifecycle_heartbeat_existing_stale = true;
 11375	        out.service_lifecycle_reentry_from_stale_heartbeat = true;
 11376	        out.service_lifecycle_preflight_passed = true;
 11377	        out.service_lifecycle_preflight_reason =
 11378	            "stale non-final heartbeat bound to the expired owner generation permits service re-entry";
 11379	        return ok_result();
 11380	    } catch (const std::exception& e) {
 11381	        return fail_result(
 11382	            std::string("sync daemon service lifecycle preflight failed: ") +
