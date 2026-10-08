# 10 — Plugin Surface + Telemetry (v0.19)

## Plugin philosophy
- Kernel invariants are stable.
- Everything else is configurable or pluggable.
- MetaLLM proposes config/plugin diffs; applied between runs with rollback.

## Telemetry events (minimal set)
- `cap.probe_started(agent)`
- `cap.probe_finished(agent, supports, parsed?, t_ms)`
- `cursor_tick`
- `view_rendered(agent, counts_by_section, bytes_est)`
- `agent_output_received(agent, bytes, truncated?)`
- `bcc.ctrl_seen(agent, t_ms, parsed?)`
- `bcc.ctrl_healed(agent, success?)`
- `bcc.repair_asked(agent, success?)`
- `ws.object_added(type, id)`
- `ws.object_updated(type, id)`
- `ws.compaction_performed(sum_id, evicted_count)`
- `lease.grant/revoke/expire(scope, owner)`
- `patch.selected(patch_id)`
- `verifier.run(name, status, duration_ms)`
- `ce.admit/certify(ce_id, status)`

## Configuration diffs
- versioned config file(s)
- rollbackable snapshots
- changes applied between “runs” or at explicit safe points
- `req.created(req_id, from, to, type)`
- `req.closed(req_id, status)`
- `verifier.queued(name, cost)`
- `verifier.cache_hit(name, key)`
